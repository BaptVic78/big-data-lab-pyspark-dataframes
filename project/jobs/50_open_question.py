"""Do recurring director/actor pairs rate better than their other films?

Compare the same director and actor against their own films outside the
pair. Results are descriptive associations, not estimates of causality.
"""
import argparse
import time

from pyspark.sql import functions as F

from common import feature_films, get_spark, read_table, save_result


def rated_movies(films, ratings, min_votes, last_year):
    return (
        films.filter(F.col("startYear").between(1980, last_year))
        .join(ratings.filter(F.col("numVotes") >= min_votes), "tconst")
        .select("tconst", "primaryTitle", "startYear", "averageRating",
                "numVotes")
    )


def credits(movies, principals, crew):
    actors = (
        principals.filter(F.col("category").isin("actor", "actress"))
        .select("tconst", F.col("nconst").alias("actor_id"))
        .filter(F.col("actor_id").isNotNull()).dropDuplicates()
        .join(movies, "tconst")
    )
    directors = (
        crew.select("tconst", F.explode("directors").alias("director_id"))
        .filter(F.col("director_id").isNotNull()).dropDuplicates()
        .join(movies, "tconst")
    )
    return actors, directors


def pair_comparison(movies, principals, crew, names, min_shared=3,
                    min_baseline=3):
    actors, directors = credits(movies, principals, crew)
    shared = (
        actors.join(directors.select("tconst", "director_id"), "tconst")
        .filter(F.col("actor_id") != F.col("director_id"))
    )
    pairs = shared.groupBy("director_id", "actor_id").agg(
        F.count("*").alias("shared_movies"),
        F.sum("averageRating").alias("shared_rating_sum"),
        F.avg("averageRating").alias("shared_mean_rating"),
        F.sum("numVotes").alias("shared_votes"),
        F.min("startYear").alias("first_shared_year"),
        F.max("startYear").alias("last_shared_year"),
    ).filter(F.col("shared_movies") >= min_shared)
    director_totals = directors.groupBy("director_id").agg(
        F.count("*").alias("director_movies"),
        F.sum("averageRating").alias("director_rating_sum"))
    actor_totals = actors.groupBy("actor_id").agg(
        F.count("*").alias("actor_movies"),
        F.sum("averageRating").alias("actor_rating_sum"))
    compared = (
        pairs.join(director_totals, "director_id")
        .join(actor_totals, "actor_id")
        .withColumn("director_other_movies",
                    F.col("director_movies") - F.col("shared_movies"))
        .withColumn("actor_other_movies",
                    F.col("actor_movies") - F.col("shared_movies"))
        .filter((F.col("director_other_movies") >= min_baseline)
                & (F.col("actor_other_movies") >= min_baseline))
        .withColumn("director_other_mean_rating",
                    (F.col("director_rating_sum") - F.col("shared_rating_sum"))
                    / F.col("director_other_movies"))
        .withColumn("actor_other_mean_rating",
                    (F.col("actor_rating_sum") - F.col("shared_rating_sum"))
                    / F.col("actor_other_movies"))
        # IMDb scores have one decimal place. Remove arithmetic noise before
        # testing strict improvements over the two outside-pair baselines.
        .withColumn("vs_director_others", F.round(F.col("shared_mean_rating")
                    - F.col("director_other_mean_rating"), 10))
        .withColumn("vs_actor_others", F.round(F.col("shared_mean_rating")
                    - F.col("actor_other_mean_rating"), 10))
        .withColumn("above_both_baselines",
                    (F.col("vs_director_others") > 0)
                    & (F.col("vs_actor_others") > 0))
        .drop("shared_rating_sum", "director_rating_sum", "actor_rating_sum")
    )
    director_names = names.select(
        F.col("nconst").alias("director_id"),
        F.col("primaryName").alias("director_name"))
    actor_names = names.select(
        F.col("nconst").alias("actor_id"),
        F.col("primaryName").alias("actor_name"))
    compared = (compared.join(director_names, "director_id", "left")
                .join(actor_names, "actor_id", "left"))
    details = shared.join(compared.select("director_id", "actor_id"),
                          ["director_id", "actor_id"], "left_semi")
    return compared, details


def summarize(pairs):
    return pairs.agg(
        F.count("*").alias("eligible_pairs"),
        F.coalesce(F.sum(F.col("above_both_baselines").cast("int")),
                   F.lit(0)).alias("pairs_above_both"),
        (100 * F.avg(F.col("above_both_baselines").cast("double")))
        .alias("pct_above_both"),
        F.avg("vs_director_others").alias("mean_vs_director_others"),
        F.avg("vs_actor_others").alias("mean_vs_actor_others"),
        F.percentile_approx("vs_director_others", 0.5, 10000)
        .alias("median_vs_director_others"),
        F.percentile_approx("vs_actor_others", 0.5, 10000)
        .alias("median_vs_actor_others"),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-votes", type=int, default=1000)
    parser.add_argument("--min-shared", type=int, default=3)
    parser.add_argument("--min-baseline", type=int, default=3)
    parser.add_argument("--last-year", type=int, default=2025)
    args = parser.parse_args()
    if min(args.min_votes, args.min_shared, args.min_baseline) < 1:
        parser.error("vote and film-count thresholds must be positive")
    if not 1980 <= args.last_year <= 2025:
        parser.error("--last-year must be between 1980 and 2025")
    spark = get_spark("imdb-open-question")
    started = time.monotonic()
    pairs = movies = None
    try:
        movies = rated_movies(feature_films(spark),
                              read_table(spark, "title_ratings"),
                              args.min_votes, args.last_year).cache()
        pairs, details = pair_comparison(
            movies, read_table(spark, "title_principals"),
            read_table(spark, "title_crew"),
            read_table(spark, "name_basics"), args.min_shared,
            args.min_baseline)
        pairs = pairs.cache()
        save_result(pairs.orderBy(F.desc("shared_movies"), "director_id",
                                  "actor_id"), "5_pair_comparison")
        save_result(summarize(pairs), "5_pair_summary")
        save_result(details.orderBy("director_id", "actor_id", "startYear",
                                    "tconst"), "5_shared_movies")
        parameters = spark.createDataFrame(
            [(1980, args.last_year, args.min_votes, args.min_shared,
              args.min_baseline, movies.count())],
            ["first_year", "last_year", "min_votes", "min_shared",
             "min_baseline", "eligible_rated_feature_films"])
        save_result(parameters, "5_parameters")
        print(f"completed in {time.monotonic() - started:.0f}s", flush=True)
    finally:
        if pairs is not None:
            pairs.unpersist()
        if movies is not None:
            movies.unpersist()
        spark.stop()


if __name__ == "__main__":
    main()
