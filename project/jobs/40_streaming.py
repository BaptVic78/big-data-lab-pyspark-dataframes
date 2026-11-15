"""Streaming: Wikipedia edits -> Kafka -> Spark Structured Streaming.

Reads the Kafka topic filled by ``scripts/wikipedia_producer.py`` and keeps
only the edits of Wikipedia pages that match an IMDb title or person of the
clean layer. Matching is a stream-static join on a normalised page title.

Run (the producer must be running on the host)::

    docker compose exec spark python /home/jovyan/jobs/40_streaming.py \
        --minutes 25

Outputs:
  * ``output/4_matched_edits_stream/``  Parquet, one row per matched edit
  * ``output/4_matched_edits``          CSV + Markdown, matches per entity
  * ``output/4_edits_per_window``       CSV + Markdown, matches per window
"""
import argparse
import shutil

from pyspark.sql import functions as F
from pyspark.sql.types import (BooleanType, LongType, StringType, StructField,
                               StructType)

from common import OUTPUT_DIR, DATA_DIR, get_spark, read_table, save_result

KAFKA_SERVER = "kafka:19092"  # address of the broker inside the compose network
TOPIC = "wikipedia-edits"
CHECKPOINT_DIR = DATA_DIR / "checkpoints" / "40_streaming"
STREAM_OUT = OUTPUT_DIR / "4_matched_edits_stream"

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

    One row per (key, entity_type): ``key`` is the normalised name,
    ``imdb_id`` the most-voted entity carrying that name.
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

    # Several entities can share a name: keep the most voted one so that an
    # edit is never duplicated by the join.
    return (
        titles.unionByName(people)
        .filter(F.length("key") > 2)
        .groupBy("key", "entity_type")
        .agg(F.max_by("imdb_id", "votes").alias("imdb_id"),
             F.max_by("label", "votes").alias("label"),
             F.max("votes").alias("votes"))
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

    # 2. Matches per 5-minute window. The watermark tells Spark how long to
    #    keep a window open for late events: an edit arriving more than
    #    10 minutes behind the newest event time is dropped, and a window is
    #    final once the watermark passes its end.
    per_window = (
        matched.withWatermark("event_time", WATERMARK)
        .groupBy(F.window("event_time", WINDOW), "entity_type")
        .agg(F.count("*").alias("edits"),
             F.approx_count_distinct("imdb_id").alias("entities"))
        .select(F.col("window.start").alias("window_start"),
                F.col("window.end").alias("window_end"),
                "entity_type", "edits", "entities")
    )
    to_console = (
        per_window.writeStream.outputMode("update").format("console")
        .option("truncate", "false")
        .option("checkpointLocation", str(CHECKPOINT_DIR / "windows"))
        .trigger(processingTime="30 seconds")
        .queryName("edits_per_window")
        .start()
    )

    print(f"streaming for {args.minutes} minutes...", flush=True)
    spark.streams.awaitAnyTermination(timeout=int(args.minutes * 60))
    for query in (to_parquet, to_console):
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
    save_result(
        result.groupBy(F.window("event_time", WINDOW).alias("w"),
                       "entity_type")
        .agg(F.count("*").alias("edits"))
        .select(F.col("w.start").alias("window_start"), "entity_type",
                "edits")
        .orderBy("window_start", "entity_type"),
        "4_edits_per_window")


if __name__ == "__main__":
    main()
