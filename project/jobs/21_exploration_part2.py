"""Exploration 2.5–2.8 on clean IMDb tables.

Usage: python /home/jovyan/jobs/21_exploration_part2.py [2.5 2.6 2.7 2.8]
Successful movies have rating >=7 and >=1000 votes by default. IMDb akas
languages describe title variants; original-title language is used as an
explicit proxy for film language, with unknown languages excluded.
"""
import argparse
import time
from datetime import datetime, timezone

from pyspark.sql import functions as F

from common import get_spark, read_table, save_result


def series_extremes(episodes, basics, ratings):
    """Every numbered season needs >=10 episodes, including unrated ones.

    Season zero (specials) is excluded. At least three numbered seasons
    are required. Rating ties qualify if a best episode exists in seasons
    1–2 and a worst episode exists in the last numbered season.
    """
    # Season membership is known even when the episode number is missing.
    # Filtering episodeNumber here could hide an entire last season.
    numbered = episodes.filter(F.col("seasonNumber") >= 1)
    seasons = numbered.groupBy("parentTconst", "seasonNumber").agg(
        F.countDistinct("tconst").alias("episodes_in_season"))
    eligible = seasons.groupBy("parentTconst").agg(
        F.count("*").alias("numbered_seasons"),
        F.min("episodes_in_season").alias("smallest_season"),
        F.max("seasonNumber").alias("last_season"),
    ).filter((F.col("numbered_seasons") >= 3) & (F.col("smallest_season") >= 10))
    rated = numbered.join(eligible, "parentTconst").join(ratings, "tconst")
    extrema = rated.groupBy("parentTconst").agg(
        F.min("averageRating").alias("worst_rating"),
        F.max("averageRating").alias("best_rating"),
        F.count("*").alias("rated_episodes"),
    )
    candidates = rated.join(extrema, "parentTconst")
    best = candidates.filter((F.col("averageRating") == F.col("best_rating"))
                             & F.col("seasonNumber").isin(1, 2)).groupBy(
                                 "parentTconst").agg(
        F.min("tconst").alias("best_early_episode"))
    worst = candidates.filter((F.col("averageRating") == F.col("worst_rating"))
                              & (F.col("seasonNumber") == F.col("last_season")))
    worst = worst.groupBy("parentTconst").agg(
        F.min("tconst").alias("worst_last_episode"))
    series = basics.filter(F.col("titleType").isin("tvSeries", "tvMiniSeries"))
    return (
        eligible.join(extrema, "parentTconst").join(best, "parentTconst")
        .join(worst, "parentTconst")
        .join(series.select(F.col("tconst").alias("parentTconst"),
                            "primaryTitle"), "parentTconst")
        .orderBy(F.desc("numbered_seasons"), "parentTconst")
    )


def actor_movies(principals, movies):
    return (
        principals.filter(F.col("category").isin("actor", "actress"))
        .select("nconst", "tconst").dropDuplicates()
        .join(movies.select("tconst", "primaryTitle", "startYear"), "tconst")
    )


def multilingual_success(cast, ratings, akas, names, min_rating, min_votes):
    """Original-title language metadata is a proxy, not spoken-language data.

    Repeated regional variants count once per film/language. Actors need
    distinct successful movies across languages, not one multilingual title.
    Evidence and coverage are returned alongside actor-level results.
    """
    successful = ratings.filter((F.col("averageRating") >= min_rating)
                                & (F.col("numVotes") >= min_votes))
    languages = (
        akas.filter(F.col("isOriginalTitle") & F.col("language").isNotNull()
                    & (F.trim("language") != "") & (F.col("language") != "und"))
        .select(F.col("titleId").alias("tconst"), "language").distinct()
    )
    success_cast = cast.join(successful, "tconst")
    evidence = success_cast.join(languages, "tconst")
    actors = evidence.groupBy("nconst").agg(
        F.countDistinct("language").alias("language_count"),
        F.countDistinct("tconst").alias("successful_movies"),
        F.concat_ws(",", F.sort_array(F.collect_set("language"))).alias("languages"),
    ).filter((F.col("language_count") >= 2) & (F.col("successful_movies") >= 2))
    actors = actors.join(names.select("nconst", "primaryName"), "nconst", "left")
    coverage = success_cast.select("tconst").distinct().join(
        languages.select("tconst").distinct().withColumn("has_language", F.lit(1)),
        "tconst", "left").agg(
            F.count("*").alias("successful_cast_movies"),
            F.count("has_language").alias("movies_with_original_title_language"))
    return actors.orderBy(F.desc("language_count"), "nconst"), evidence, coverage


def early_career_peaks(cast, ratings, names, early_fraction):
    """At least 15 released movies and 20 years between first/last release.

    Early means the first fraction of that observed calendar-year span.
    The highest rated early movie must strictly exceed every later movie.
    Career eligibility uses all dated credits; peak comparisons use rated
    films and require at least one rated film in each period.
    """
    current_year = datetime.now(timezone.utc).year
    dated = cast.filter(F.col("startYear").isNotNull()
                        & (F.col("startYear") <= current_year))
    careers = dated.groupBy("nconst").agg(
        F.countDistinct("tconst").alias("career_movies"),
        F.min("startYear").alias("first_year"),
        F.max("startYear").alias("last_year"),
    ).withColumn("career_years", F.col("last_year") - F.col("first_year"))
    careers = careers.filter((F.col("career_movies") >= 15)
                              & (F.col("career_years") >= 20)).withColumn(
        "early_cutoff_year", F.col("first_year") + early_fraction * F.col("career_years"))
    credits = dated.join(careers, "nconst").join(ratings, "tconst")
    early = F.col("startYear") <= F.col("early_cutoff_year")
    peaks = credits.groupBy("nconst").agg(
        F.sum(early.cast("int")).alias("early_rated_movies"),
        F.sum((~early).cast("int")).alias("later_rated_movies"),
        F.max(F.when(early, F.col("averageRating"))).alias("early_best_rating"),
        F.max(F.when(~early, F.col("averageRating"))).alias("later_best_rating"),
        F.avg(F.when(early, F.col("averageRating"))).alias("early_mean_rating"),
        F.avg(F.when(~early, F.col("averageRating"))).alias("later_mean_rating"),
    ).filter((F.col("early_rated_movies") > 0) & (F.col("later_rated_movies") > 0)
              & (F.col("early_best_rating") > F.col("later_best_rating")))
    return (
        careers.join(peaks, "nconst")
        .join(names.select("nconst", "primaryName"), "nconst", "left")
        .withColumn("early_fraction", F.lit(early_fraction))
        .orderBy(F.desc("career_years"), "nconst")
    )


def role_performance(principals, crew, movies, ratings, names):
    """Actor, writer and director roles across movies and on each project.

    Crew arrays complement principal credits, which omit some writers and
    directors. Actor/actress are one role. Every person/film/role is unique.
    Ratings compare the same person's single-role and multiple-role films.
    """
    principal_roles = principals.filter(
        F.col("category").isin("actor", "actress", "writer", "director"))
    principal_roles = principal_roles.select(
        "tconst", "nconst", F.when(F.col("category").isin("actor", "actress"),
                                   "actor").otherwise(F.col("category")).alias("role"))
    directors = crew.select("tconst", F.explode("directors").alias("nconst"))
    writers = crew.select("tconst", F.explode("writers").alias("nconst"))
    roles = (
        principal_roles.unionByName(directors.withColumn("role", F.lit("director")))
        .unionByName(writers.withColumn("role", F.lit("writer")))
        .filter(F.col("nconst").isNotNull()).dropDuplicates()
        .join(movies.select("tconst"), "tconst", "left_semi")
    )
    talented = roles.groupBy("nconst").agg(
        F.countDistinct("role").alias("career_role_count"),
        F.concat_ws(",", F.sort_array(F.collect_set("role"))).alias("career_roles"),
    ).filter(F.col("career_role_count") >= 2)
    projects = roles.groupBy("nconst", "tconst").agg(
        F.count("*").alias("project_role_count"),
        F.concat_ws(",", F.sort_array(F.collect_set("role"))).alias("project_roles"),
    ).join(talented, "nconst").join(ratings, "tconst", "left")
    multi = F.col("project_role_count") >= 2
    summary = projects.groupBy("nconst", "career_role_count", "career_roles").agg(
        F.sum(multi.cast("int")).alias("multi_role_movies"),
        F.sum((~multi).cast("int")).alias("single_role_movies"),
        F.count(F.when(multi, F.col("averageRating"))).alias("multi_role_rated_movies"),
        F.count(F.when(~multi, F.col("averageRating"))).alias("single_role_rated_movies"),
        F.avg(F.when(multi, F.col("averageRating"))).alias("multi_role_mean_rating"),
        F.avg(F.when(~multi, F.col("averageRating"))).alias("single_role_mean_rating"),
    ).withColumn("multi_minus_single_rating", F.col("multi_role_mean_rating")
                 - F.col("single_role_mean_rating"))
    summary = summary.join(names.select("nconst", "primaryName"), "nconst", "left")
    details = projects.join(movies.select("tconst", "primaryTitle", "startYear"),
                            "tconst").filter(multi)
    return summary.orderBy(F.desc("multi_role_movies"), "nconst"), details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("questions", nargs="*", choices=["2.5", "2.6", "2.7", "2.8"])
    parser.add_argument("--success-rating", type=float, default=7.0)
    parser.add_argument("--success-votes", type=int, default=1000)
    parser.add_argument("--early-fraction", type=float, default=1 / 3)
    args = parser.parse_args()
    if not 0 < args.early_fraction < 1:
        parser.error("--early-fraction must be between 0 and 1")
    if not 1 <= args.success_rating <= 10 or args.success_votes < 1:
        parser.error("success rating must be 1–10 and votes must be positive")
    selected = set(args.questions or ["2.5", "2.6", "2.7", "2.8"])
    spark = get_spark("imdb-exploration-part2")
    started = time.monotonic()
    try:
        basics = read_table(spark, "title_basics")
        movies = basics.filter(F.col("titleType") == "movie")
        ratings = read_table(spark, "title_ratings")
        names = read_table(spark, "name_basics")
        principals = read_table(spark, "title_principals")
        cast = actor_movies(principals, movies)
        if "2.5" in selected:
            save_result(series_extremes(read_table(spark, "title_episode"), basics,
                                       ratings), "2_5_series_extremes")
            print("2.5 complete", flush=True)
        if "2.6" in selected:
            actors, evidence, coverage = multilingual_success(
                cast, ratings, read_table(spark, "title_akas"), names,
                args.success_rating, args.success_votes)
            save_result(actors, "2_6_multilingual_actors")
            save_result(actors.filter(F.col("language_count") >= 3),
                        "2_6_three_languages")
            save_result(evidence, "2_6_language_evidence")
            save_result(coverage, "2_6_language_coverage")
            print("2.6 complete", flush=True)
        if "2.7" in selected:
            save_result(early_career_peaks(cast, ratings, names, args.early_fraction),
                        "2_7_early_career_peaks")
            print("2.7 complete", flush=True)
        if "2.8" in selected:
            summary, details = role_performance(principals, read_table(spark, "title_crew"),
                                                movies, ratings, names)
            save_result(summary, "2_8_role_comparison")
            save_result(details, "2_8_multi_role_projects")
            print("2.8 complete", flush=True)
        print(f"completed in {time.monotonic() - started:.0f}s", flush=True)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
