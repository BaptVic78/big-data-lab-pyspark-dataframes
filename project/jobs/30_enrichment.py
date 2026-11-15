"""Prepare IMDb targets, then join cached Wikipedia text with Spark.

Run `prepare`, the host-side fetch_wikipedia.py, then `finalize`.
Every genre/year keeps its own ten highest-rated feature films. A film
belonging to several genres is fetched once but retained in each ranking.
"""
import argparse
from pyspark.sql import Window, functions as F, types as T

from common import (DATA_DIR, feature_films, get_spark,
                    read_table, save_result)

TARGET_DIR = DATA_DIR / "enrichment" / "targets"
CACHE_DIR = DATA_DIR / "enrichment" / "wikipedia"
CACHE_SCHEMA = T.StructType([
    T.StructField(c, T.StringType()) for c in [
        "entity_id", "kind", "label", "status", "note", "text",
        "source_url", "revision_url", "wikidata_url", "fetched_at",
        "license_url", "section", "revision_id"]
])


def top_films(films, ratings, top_n=10, min_votes=1):
    candidates = (
        films.filter(F.col("startYear").between(1980, 2025))
        .join(ratings.filter(F.col("numVotes") >= min_votes), "tconst")
        .select("tconst", "primaryTitle", "originalTitle", "startYear",
                "averageRating", "numVotes", F.explode("genres").alias("genre"))
        .filter(F.col("genre").isNotNull() & (F.trim("genre") != ""))
        .dropDuplicates(["tconst", "genre"])
    )
    ranking = Window.partitionBy("genre", "startYear").orderBy(
        F.desc("averageRating"), F.desc("numVotes"), "tconst")
    return candidates.withColumn("genre_year_rank", F.row_number().over(ranking)) \
        .filter(F.col("genre_year_rank") <= top_n)


def principal_candidates(selected, principals, names, candidate_count=10):
    # One person per film, even when credited in more than one role.
    people = (
        principals.join(selected.select("tconst").distinct(), "tconst", "left_semi")
        .groupBy("tconst", "nconst")
        .agg(F.min("ordering").alias("ordering"))
        .join(names.select("nconst", "primaryName"), "nconst")
    )
    order = Window.partitionBy("tconst").orderBy(F.col("ordering").asc_nulls_last(),
                                                "nconst")
    return people.withColumn("principal_rank", F.row_number().over(order)) \
        .filter(F.col("principal_rank") <= candidate_count)


def requests_for(selected, people):
    films = selected.select(
        F.col("tconst").alias("entity_id"), F.lit("film").alias("kind"),
        F.col("primaryTitle").alias("label"),
        F.col("startYear").cast("string").alias("year")).distinct()
    persons = people.select(
        F.col("nconst").alias("entity_id"), F.lit("person").alias("kind"),
        F.col("primaryName").alias("label"), F.lit("").alias("year")).distinct()
    return films.unionByName(persons).orderBy("kind", "entity_id")


def prepare(spark, args):
    selected = top_films(feature_films(spark), read_table(spark, "title_ratings"),
                         args.top_n, args.min_votes).cache()
    try:
        people = principal_candidates(selected, read_table(spark, "title_principals"),
                                      read_table(spark, "name_basics"),
                                      args.principal_candidates).cache()
        try:
            selected.write.mode("overwrite").parquet(str(TARGET_DIR / "films"))
            people.write.mode("overwrite").parquet(str(TARGET_DIR / "principals"))
            save_result(requests_for(selected, people), "3_requests")
            save_result(selected.orderBy("startYear", "genre", "genre_year_rank"),
                        "3_selected_films")
            parameters = spark.createDataFrame(
                [(args.top_n, args.min_votes, args.principal_candidates)],
                ["top_n_per_genre_year", "min_votes", "principal_candidates"])
            parameters.write.mode("overwrite").parquet(str(TARGET_DIR / "parameters"))
            save_result(parameters, "3_parameters")
        finally:
            people.unpersist()
    finally:
        selected.unpersist()


def clean_cache(raw):
    # Fetching preserves source text; all text normalization happens here.
    return raw.withColumn("text", F.trim(F.regexp_replace("text", r"\s+", " "))) \
        .withColumn("status", F.when(
            (F.col("status") == "ok")
            & ((F.length("text") == 0) | F.col("text").isNull()
               | F.col("source_url").isNull()
               | F.col("revision_url").isNull()), "invalid_source")
                    .otherwise(F.col("status")))


def enrich(selected, people, raw, required_biographies=3):
    cached = clean_cache(raw)
    film_text = cached.filter(F.col("kind") == "film").drop("kind", "label")
    film_text = film_text.withColumnRenamed("entity_id", "tconst")
    film_rows = selected.join(film_text, "tconst", "left") \
        .withColumn("status", F.coalesce("status", F.lit("not_fetched")))
    bios = cached.filter(F.col("kind") == "person").drop("kind", "label")
    bios = bios.withColumnRenamed("entity_id", "nconst")
    person_rows = people.join(bios, "nconst", "left") \
        .withColumn("status", F.coalesce("status", F.lit("not_fetched")))
    usable = person_rows.filter(F.col("status") == "ok")
    order = Window.partitionBy("tconst").orderBy("principal_rank", "nconst")
    biographies = usable.withColumn("biography_rank", F.row_number().over(order)) \
        .filter(F.col("biography_rank") <= required_biographies)
    counts = biographies.groupBy("tconst").agg(
        F.countDistinct("nconst").alias("available_biographies"))
    coverage = (
        film_rows.select("tconst", "primaryTitle", "status", "section").distinct()
        .withColumnRenamed("status", "synopsis_status")
        .join(counts, "tconst", "left").na.fill(0, ["available_biographies"])
        .withColumn("required_biographies", F.lit(required_biographies))
        .withColumn("complete", (F.col("synopsis_status") == "ok")
                    & (F.col("available_biographies") >= required_biographies))
        .withColumn("note", F.when(F.col("complete"), F.lit("complete"))
                    .otherwise(F.lit("Missing synopsis or biographies; see source statuses.")))
    )
    return film_rows, biographies, person_rows, coverage


def finalize(spark, args):
    selected = spark.read.parquet(str(TARGET_DIR / "films"))
    people = spark.read.parquet(str(TARGET_DIR / "principals"))
    if CACHE_DIR.exists() and any(CACHE_DIR.glob("*.json")):
        raw = (spark.read.schema(CACHE_SCHEMA)
               .option("pathGlobFilter", "*.json").json(str(CACHE_DIR)))
    else:
        raw = spark.createDataFrame([], CACHE_SCHEMA)
    # The cache contains one file per IMDb entity; reject conflicting input.
    if raw.groupBy("entity_id").count().filter("count > 1").limit(1).count():
        raise ValueError("Duplicate IMDb entities in Wikipedia cache")
    films, bios, attempts, coverage = enrich(selected, people, raw,
                                            args.biographies_per_film)
    save_result(films.orderBy("startYear", "genre", "genre_year_rank"),
                "3_film_synopses")
    save_result(bios.orderBy("tconst", "biography_rank"), "3_principal_biographies")
    save_result(attempts.orderBy("tconst", "principal_rank"), "3_principal_sources")
    save_result(coverage.orderBy("tconst"), "3_coverage")
    save_result(coverage.agg(
        F.count("*").alias("selected_distinct_films"),
        F.coalesce(F.sum(F.col("complete").cast("int")), F.lit(0))
        .alias("complete_films"),
        F.sum("available_biographies").alias("available_film_biographies")),
        "3_coverage_summary")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=["prepare", "finalize"])
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--min-votes", type=int, default=1)
    parser.add_argument("--principal-candidates", type=int, default=10)
    parser.add_argument("--biographies-per-film", type=int, default=3)
    args = parser.parse_args()
    if min(args.top_n, args.min_votes) < 1:
        parser.error("top-n and min-votes must be positive")
    if args.biographies_per_film < 3:
        parser.error("at least three biographies per film are required")
    if args.principal_candidates < args.biographies_per_film:
        parser.error("principal-candidates must cover biographies-per-film")
    spark = get_spark("imdb-enrichment-" + args.step)
    try:
        {"prepare": prepare, "finalize": finalize}[args.step](spark, args)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
