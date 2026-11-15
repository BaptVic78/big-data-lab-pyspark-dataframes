"""Small boundary checks: python /home/jovyan/jobs/test_exploration_part2.py."""
import importlib

from common import get_spark

queries = importlib.import_module("21_exploration_part2")


def check_series(spark):
    episodes = [(f"e{s}_{e}", "series", s, e)
                for s in range(1, 4) for e in range(1, 11)]
    frame = spark.createDataFrame(episodes, ["tconst", "parentTconst",
                                            "seasonNumber", "episodeNumber"])
    basics = spark.createDataFrame([("series", "Example", "tvSeries")],
                                  ["tconst", "primaryTitle", "titleType"])
    ratings = spark.createDataFrame(
        [(t, 9.0 if s == 1 and e == 1 else 2.0 if s == 3 and e == 1 else 7.0)
         for t, _, s, e in episodes], ["tconst", "averageRating"])
    assert queries.series_extremes(frame, basics, ratings).count() == 1
    incomplete = frame.filter("tconst != 'e2_10'")
    assert queries.series_extremes(incomplete, basics, ratings).count() == 0
    # A known season must not disappear because its episode numbers are missing.
    missing_number = spark.createDataFrame(
        [("e4_unknown", "series", 4, None)], frame.schema)
    assert queries.series_extremes(
        frame.unionByName(missing_number), basics, ratings).count() == 0
    # Episodes with a known season still count when episodeNumber is unknown.
    unknown_numbers = frame.selectExpr(
        "tconst", "parentTconst", "seasonNumber", "cast(null as bigint) as episodeNumber")
    assert queries.series_extremes(unknown_numbers, basics, ratings).count() == 1


def check_languages(spark):
    cast = spark.createDataFrame([("person", f"m{i}") for i in range(3)],
                                ["nconst", "tconst"])
    ratings = spark.createDataFrame([(f"m{i}", 7.0, 1000) for i in range(3)],
                                   ["tconst", "averageRating", "numVotes"])
    akas = spark.createDataFrame([
        ("m0", "en", True), ("m0", "en", True),
        ("m1", "fr", True), ("m2", "de", True), ("m2", "es", False),
    ], ["titleId", "language", "isOriginalTitle"])
    names = spark.createDataFrame([("person", "Example")], ["nconst", "primaryName"])
    actors, _, coverage = queries.multilingual_success(cast, ratings, akas,
                                                      names, 7, 1000)
    actor = actors.first()
    assert actor.language_count == 3 and actor.successful_movies == 3
    assert coverage.first().movies_with_original_title_language == 3
    assert queries.multilingual_success(cast, ratings, akas, names, 7, 1001)[0].count() == 0


def check_careers_and_roles(spark):
    cast = spark.createDataFrame(
        [("person", f"m{i}", 1980 + i if i < 14 else 2000) for i in range(15)],
        ["nconst", "tconst", "startYear"])
    ratings = spark.createDataFrame(
        [(f"m{i}", 9.0 if i == 0 else 6.0, 1000) for i in range(15)],
        ["tconst", "averageRating", "numVotes"])
    names = spark.createDataFrame([("person", "Example")], ["nconst", "primaryName"])
    assert queries.early_career_peaks(cast, ratings, names, 1 / 3).count() == 1
    assert queries.early_career_peaks(cast.filter("tconst != 'm1'"), ratings,
                                     names, 1 / 3).count() == 0
    tied = ratings.selectExpr("tconst", "9.0 as averageRating", "numVotes")
    assert queries.early_career_peaks(cast, tied, names, 1 / 3).count() == 0
    movies = spark.createDataFrame([("m0", "A", 1980), ("m1", "B", 1981)],
                                  ["tconst", "primaryTitle", "startYear"])
    principals = spark.createDataFrame([
        ("m0", "person", "actor"), ("m0", "person", "director"),
        ("m1", "person", "actor"),
    ], ["tconst", "nconst", "category"])
    crew = spark.createDataFrame([("m0", ["person"], ["other"])],
                                ["tconst", "directors", "writers"])
    summary, details = queries.role_performance(principals, crew, movies, ratings, names)
    row = summary.first()
    assert row.multi_role_movies == 1 and row.single_role_movies == 1
    assert row.multi_minus_single_rating == 3.0
    assert details.first().project_role_count == 2


if __name__ == "__main__":
    session = get_spark("exploration-part2-boundaries")
    try:
        check_series(session)
        check_languages(session)
        check_careers_and_roles(session)
        print("all exploration part 2 checks passed")
    finally:
        session.stop()
