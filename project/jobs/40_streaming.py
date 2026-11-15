"""Streaming: Wikipedia edits -> Kafka -> Spark Structured Streaming.

Reads the Kafka topic filled by ``scripts/wikipedia_producer.py`` and keeps
only the edits of Wikipedia pages that match an IMDb title or person of the
clean layer. Matching is a stream-static join on a normalised page title.

Run (the producer must be running on the host)::

    docker compose exec spark python /home/jovyan/jobs/40_streaming.py \
        --minutes 25

Outputs:
  * ``output/4_matched_edits_stream/``  Parquet, one row per matched edit
  * ``output/4_window_updates_stream/`` Parquet, every update emitted by the
                                        watermarked window query
  * ``output/4_matched_edits``          CSV + Markdown, edits per entity
  * ``output/4_edits_per_window``       CSV + Markdown, per window: the
                                        watermarked streaming count, the count
                                        over all stored edits, and the gap
"""
import argparse
import shutil

from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql.types import (BooleanType, LongType, StringType, StructField,
                               StructType)

from common import OUTPUT_DIR, DATA_DIR, get_spark, read_table, save_result

KAFKA_SERVER = "kafka:19092"  # address of the broker inside the compose network
TOPIC = "wikipedia-edits"
CHECKPOINT_DIR = DATA_DIR / "checkpoints" / "40_streaming"
STREAM_OUT = OUTPUT_DIR / "4_matched_edits_stream"
WINDOW_OUT = OUTPUT_DIR / "4_window_updates_stream"

# Only well-known titles and people are matched, otherwise the broadcast
# table would hold millions of rows and common words would match anything.
MIN_VOTES = 10000
TITLE_TYPES = ["movie", "tvSeries", "tvMiniSeries"]

WATERMARK = "10 minutes"  # how late an event may arrive and still be counted
WINDOW = "5 minutes"

EDIT_SCHEMA = StructType([
    StructField("id", LongType()),
    StructField("type", StringType()),
    StructField("title", StringType()),
    StructField("user", StringType()),
    StructField("bot", BooleanType()),
    StructField("minor", BooleanType()),
    StructField("comment", StringType()),
    StructField("timestamp", LongType()),  # epoch seconds
    StructField("length_old", LongType()),
    StructField("length_new", LongType()),
])


def normalize(col):
    """Match key of a title: no '(film)'-style suffix, lower case, one space.

    'Inception (film)' and 'inception' both become 'inception'.
    """
    no_suffix = F.regexp_replace(col, r"\s*\([^)]*\)\s*$", "")
    return F.trim(F.regexp_replace(F.lower(no_suffix), r"[\s_]+", " "))


def build_entities(spark, min_votes=MIN_VOTES):
    """IMDb titles and people that edits are matched against.

    One row per ``key`` (the normalised name), see ``one_per_key``.
    """
    basics = read_table(spark, "title_basics")
    ratings = read_table(spark, "title_ratings")
    popular = (
        basics.filter(F.col("titleType").isin(TITLE_TYPES))
        .join(ratings.filter(F.col("numVotes") >= min_votes), "tconst")
        .select("tconst", "primaryTitle", F.col("numVotes").alias("votes"))
        .cache()
    )

    titles = popular.select(
        normalize(F.col("primaryTitle")).alias("key"),
        F.lit("title").alias("entity_type"),
        F.col("tconst").alias("imdb_id"),
        F.col("primaryTitle").alias("label"),
        "votes",
    )

    # People are the ones "known for" a popular title; their weight is the
    # votes of their best-known popular title.
    people = (
        read_table(spark, "name_basics")
        .select("nconst", "primaryName",
                F.explode("knownForTitles").alias("tconst"))
        .join(F.broadcast(popular.select("tconst", "votes")), "tconst")
        .groupBy("nconst", "primaryName")
        .agg(F.max("votes").alias("votes"))
        .select(
            normalize(F.col("primaryName")).alias("key"),
            F.lit("person").alias("entity_type"),
            F.col("nconst").alias("imdb_id"),
            F.col("primaryName").alias("label"),
            "votes",
        )
    )

    return one_per_key(
        titles.unionByName(people).filter(F.length("key") > 2))


def one_per_key(candidates):
    """Keep exactly one entity per key, so an edit matches at most once.

    Several entities can share a name, within a type (remakes) or across
    types (the series "Doug" and a person named Doug). Deterministic order:
      1. a title wins over a person: a title's votes are its own, while a
         person only borrows the votes of the title they are known for;
      2. then the most votes;
      3. then the smallest IMDb id.
    """
    best_first = Window.partitionBy("key").orderBy(
        F.when(F.col("entity_type") == "title", 0).otherwise(1),
        F.desc("votes"),
        F.asc("imdb_id"),
    )
    return (
        candidates.withColumn("rank", F.row_number().over(best_first))
        .filter(F.col("rank") == 1)
        .drop("rank")
    )


def parse_edits(raw):
    """Kafka records (binary value) -> typed edits with an event time."""
    return (
        raw.select(F.from_json(F.col("value").cast("string"),
                               EDIT_SCHEMA).alias("e"))
        .select("e.*")
        .filter(F.col("title").isNotNull() & F.col("timestamp").isNotNull())
        .withColumn("event_time", F.timestamp_seconds("timestamp"))
        .withColumn("key", normalize(F.col("title")))
    )


def match_edits(edits, entities):
    """Keep only the edits whose page title matches an IMDb entity."""
    return edits.join(F.broadcast(entities), "key", "inner").select(
        "event_time", "id", "title", "entity_type", "imdb_id", "label",
        "user", "bot", "comment", "length_old", "length_new",
    )


def window_counts(matched):
    """Matched edits per 5-minute window, with a watermark for late data.

    The watermark tells Spark how long to keep a window open: an edit whose
    window ended before (newest event time seen - 10 minutes) is dropped,
    and the state of that window is freed.
    """
    return (
        matched.withWatermark("event_time", WATERMARK)
        .groupBy(F.window("event_time", WINDOW), "entity_type")
        .agg(F.count("*").alias("edits"),
             F.approx_count_distinct("imdb_id").alias("entities"))
        .select(F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"),
                "entity_type", "edits", "entities")
    )


def window_update_writer(path, show=True):
    """foreachBatch function storing every update of the window query.

    In update mode each micro-batch emits the windows whose count changed.
    They are appended with their batch id, so the final streaming counts can
    be read back exactly as the stateful query computed them.
    """
    def write(batch_df, batch_id):
        batch_df.persist()
        if show and not batch_df.isEmpty():
            batch_df.orderBy("window_start", "entity_type").show(
                truncate=False)
        (batch_df.withColumn("batch_id", F.lit(batch_id))
         .write.mode("append").parquet(str(path)))
        batch_df.unpersist()
    return write


def final_window_counts(spark, path):
    """Last emitted count of each window: the watermarked streaming result."""
    return (
        spark.read.parquet(str(path))
        .groupBy("window_start", "window_end", "entity_type")
        .agg(F.max_by("edits", "batch_id").alias("edits_streaming"))
    )


def window_report(final_counts, matched_edits):
    """Compare the watermarked counts with a batch count of all stored edits.

    ``edits_all`` counts every matched edit of the Parquet sink, which sits
    before the watermark and therefore also holds the late edits.
    ``late_not_counted`` is the difference: edits that arrived too late for
    the streaming count of their window.
    """
    all_edits = (
        matched_edits.groupBy(F.window("event_time", WINDOW).alias("w"),
                              "entity_type")
        .agg(F.count("*").alias("edits_all"))
        .select(F.col("w.start").alias("window_start"),
                F.col("w.end").alias("window_end"), "entity_type",
                "edits_all")
    )
    return (
        final_counts.join(all_edits,
                          ["window_start", "window_end", "entity_type"],
                          "full_outer")
        .na.fill(0, ["edits_streaming", "edits_all"])
        .withColumn("late_not_counted",
                    F.col("edits_all") - F.col("edits_streaming"))
        .orderBy("window_start", "entity_type")
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--minutes", type=float, default=25,
                        help="how long the stream runs (default: 25)")
    parser.add_argument("--min-votes", type=int, default=MIN_VOTES)
    parser.add_argument("--from-beginning", action="store_true",
                        help="read the topic from its first offset instead "
                             "of only the new events")
    args = parser.parse_args()

    spark = get_spark("40_streaming", kafka=True)
    # Start from a clean slate: a stale checkpoint would resume old offsets.
    shutil.rmtree(CHECKPOINT_DIR, ignore_errors=True)
    shutil.rmtree(STREAM_OUT, ignore_errors=True)
    shutil.rmtree(WINDOW_OUT, ignore_errors=True)

    entities = build_entities(spark, args.min_votes).cache()
    print(f"matching against {entities.count()} IMDb titles and people",
          flush=True)

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_SERVER)
        .option("subscribe", TOPIC)
        .option("startingOffsets",
                "earliest" if args.from_beginning else "latest")
        .option("failOnDataLoss", "false")
        .load()
    )
    edits = parse_edits(raw)
    matched = match_edits(edits, entities)

    # 1. Every matched edit, appended to Parquet.
    to_parquet = (
        matched.writeStream.outputMode("append").format("parquet")
        .option("path", str(STREAM_OUT))
        .option("checkpointLocation", str(CHECKPOINT_DIR / "events"))
        .trigger(processingTime="30 seconds")
        .queryName("matched_edits")
        .start()
    )

    # 2. Watermarked counts per 5-minute window. Every update is printed
    #    and stored, so the exported counts are the ones of this query.
    to_windows = (
        window_counts(matched).writeStream.outputMode("update")
        .foreachBatch(window_update_writer(WINDOW_OUT))
        .option("checkpointLocation", str(CHECKPOINT_DIR / "windows"))
        .trigger(processingTime="30 seconds")
        .queryName("edits_per_window")
        .start()
    )

    print(f"streaming for {args.minutes} minutes...", flush=True)
    spark.streams.awaitAnyTermination(timeout=int(args.minutes * 60))
    for query in (to_parquet, to_windows):
        query.stop()

    # Results of the run, ready for REPORT.md.
    result = spark.read.parquet(str(STREAM_OUT))
    total = result.count()
    print(f"{total} matched edits", flush=True)
    if total == 0:
        print("no match: run longer, lower --min-votes, or check that the "
              "producer was running")
        return
    save_result(
        result.groupBy("entity_type", "label", "imdb_id")
        .agg(F.count("*").alias("edits"),
             F.min("event_time").alias("first_edit"),
             F.max("event_time").alias("last_edit"))
        .orderBy(F.desc("edits"), "label"),
        "4_matched_edits")
    # The two queries stop independently, so the last (partial) window can
    # differ by one micro-batch between the two counts.
    save_result(
        window_report(final_window_counts(spark, WINDOW_OUT), result),
        "4_edits_per_window")


if __name__ == "__main__":
    main()
