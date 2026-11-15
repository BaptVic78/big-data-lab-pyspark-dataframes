"""Exploration 2.1–2.4 using the clean IMDb tables.

Run all queries, or select question numbers, for example::

    docker compose exec spark python /home/jovyan/jobs/20_exploration_part1.py 2.1 2.4

Popularity is the sum of numVotes, with each film contributing to each of
its genres. Runtime outliers have abs(population z-score) > 2 by default.
Questions 2.2–2.4 include all movie titles, including short-runtime movies.
Unrated films are excluded from rating averages and popularity aggregates.
"""
import argparse
import time

from pyspark.sql import Window
from pyspark.sql import functions as F

from common import feature_films, get_spark, read_table, save_result


def runtime_outliers(films, threshold):
    """One row per feature film/genre exceeding the chosen z-score."""
    by_genre = films.select(
        "tconst", "primaryTitle", "startYear", "runtimeMinutes",
        F.explode("genres").alias("genre"),
    ).filter(F.col("genre").isNotNull() & (F.col("genre") != ""))
    stats = by_genre.groupBy("genre").agg(
        F.count("*").alias("genre_films"),
        F.avg("runtimeMinutes").alias("genre_mean_minutes"),
        F.stddev_pop("runtimeMinutes").alias("genre_stddev_minutes"),
    )
    return (
        by_genre.join(stats, "genre")
        .filter(F.col("genre_stddev_minutes") > 0)
        .withColumn("difference_minutes",
                    F.col("runtimeMinutes") - F.col("genre_mean_minutes"))
        .withColumn("z_score",
                    F.col("difference_minutes") / F.col("genre_stddev_minutes"))
        .filter(F.abs("z_score") > threshold)
        .withColumn("z_score_threshold", F.lit(threshold))
        .orderBy("genre", F.desc(F.abs("z_score")), "tconst")
    )


def genre_popularity(movies, ratings):
    """Rank genres within each year by total votes, then genre name."""
    film_genres = (
        movies.filter(F.col("startYear").between(1980, 2025))
        .join(ratings, "tconst")
        .select(F.col("startYear").alias("year"), "numVotes", "averageRating",
                F.explode("genres").alias("genre"))
        .filter(F.col("genre").isNotNull() & (F.col("genre") != ""))
    )
    stats = film_genres.groupBy("year", "genre").agg(
        F.count("*").alias("rated_films"),
        F.sum("numVotes").alias("total_votes"),
        F.avg("averageRating").alias("mean_rating"),
        F.sum(F.col("averageRating") * F.col("numVotes"))
        .alias("rating_vote_sum"),
    ).withColumn("vote_weighted_rating",
                 F.col("rating_vote_sum") / F.col("total_votes"))
    rank = Window.partitionBy("year").orderBy(F.desc("total_votes"), "genre")
    return stats.withColumn("genre_rank", F.row_number().over(rank))


def compare_genres(ranked):
    """Compare top-three vs remaining genre assignments within each year.

    Multi-genre films contribute once per genre, including across groups.
    Shares therefore use genre-assigned votes and film counts.
    """
    grouped = (
        ranked.withColumn("genre_group", F.when(F.col("genre_rank") <= 3,
                                                "top_three").otherwise("rest"))
        .groupBy("year", "genre_group")
        .agg(F.count("*").alias("genres"),
             F.sum("rated_films").alias("rated_film_genre_assignments"),
             F.sum("total_votes").alias("genre_assigned_votes"),
             F.sum("rating_vote_sum").alias("rating_vote_sum"))
    )
    year = Window.partitionBy("year")
    return (
        grouped.withColumn("vote_share_pct", 100 * F.col("genre_assigned_votes")
                           / F.sum("genre_assigned_votes").over(year))
        .withColumn("film_assignment_share_pct",
                    100 * F.col("rated_film_genre_assignments")
                    / F.sum("rated_film_genre_assignments").over(year))
        .withColumn("votes_per_genre",
                    F.col("genre_assigned_votes") / F.col("genres"))
        .withColumn("vote_weighted_rating",
                    F.col("rating_vote_sum") / F.col("genre_assigned_votes"))
        .drop("rating_vote_sum")
        .orderBy("year", F.desc("genre_group"))
    )


def qualifying_directors(movies, ratings, crew, names):
    """Exactly one rated movie >=8, at least two others averaging <=6.

    Each director/movie pair is counted once. Unknown ratings are excluded
    from both the other-film count and its average.
    """
    credits = (
        crew.select("tconst", F.explode("directors").alias("nconst"))
        .dropDuplicates(["tconst", "nconst"])
        .join(movies.select("tconst", "primaryTitle", "startYear"), "tconst")
        .join(ratings.select("tconst", "averageRating"), "tconst")
    )
    high = F.col("averageRating") >= 8.0
    totals = credits.groupBy("nconst").agg(
        F.sum(high.cast("int")).alias("high_rated_movies"),
        F.sum((~high).cast("int")).alias("other_rated_movies"),
        F.avg(F.when(~high, F.col("averageRating"))).alias("other_mean_rating"),
        F.max(F.when(high, F.col("tconst"))).alias("high_movie_id"),
        F.max(F.when(high, F.col("primaryTitle"))).alias("high_movie_title"),
        F.max(F.when(high, F.col("startYear"))).alias("high_movie_year"),
        F.max(F.when(high, F.col("averageRating"))).alias("high_movie_rating"),
    )
    return (
        totals.filter((F.col("high_rated_movies") == 1)
                      & (F.col("other_rated_movies") >= 2)
                      & (F.col("other_mean_rating") <= 6.0))
        .join(names.select("nconst", "primaryName"), "nconst", "left")
        .orderBy("other_mean_rating", "primaryName", "nconst")
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("questions", nargs="*", choices=["2.1", "2.2", "2.3", "2.4"])
    parser.add_argument("--runtime-z-score", type=float, default=2.0)
    args = parser.parse_args()
    if not 0 < args.runtime_z_score < float("inf"):
        parser.error("--runtime-z-score must be finite and positive")
    selected = set(args.questions or ["2.1", "2.2", "2.3", "2.4"])
    spark = get_spark("imdb-exploration-part1")
    start = time.monotonic()
    ranked = None
    try:
        movies = read_table(spark, "title_basics").filter(F.col("titleType") == "movie")
        ratings = read_table(spark, "title_ratings")
        if "2.1" in selected:
            save_result(runtime_outliers(feature_films(spark), args.runtime_z_score),
                        "2_1_runtime_outliers")
            print("2.1 complete", flush=True)
        if selected & {"2.2", "2.3"}:
            ranked = genre_popularity(movies, ratings).cache()
            if "2.2" in selected:
                save_result(ranked.filter(F.col("genre_rank") <= 3)
                            .drop("rating_vote_sum").orderBy("year", "genre_rank"),
                            "2_2_top_genres")
                print("2.2 complete", flush=True)
            if "2.3" in selected:
                save_result(compare_genres(ranked), "2_3_genre_comparison")
                print("2.3 complete", flush=True)
        if "2.4" in selected:
            save_result(qualifying_directors(
                movies, ratings, read_table(spark, "title_crew"),
                read_table(spark, "name_basics")), "2_4_directors")
            print("2.4 complete", flush=True)
        print(f"completed in {time.monotonic() - start:.0f}s", flush=True)
    finally:
        if ranked is not None:
            ranked.unpersist()
        spark.stop()


if __name__ == "__main__":
    main()
