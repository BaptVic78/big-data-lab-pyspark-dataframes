"""Boundary checks without the IMDb dataset or network access."""
import importlib
from common import get_spark

q = importlib.import_module("50_open_question")


def check_pairs(spark):
    movies = spark.createDataFrame([
        (f"m{i}", f"Movie {i}", 2000, 8.0 if i < 3 else 6.0, 1000)
        for i in range(9)],
        "tconst string, primaryTitle string, startYear int, "
        "averageRating double, numVotes int")
    principals = spark.createDataFrame(
        [(f"m{i}", "a", "actress") for i in [0, 1, 2, 6, 7, 8]]
        + [("m0", "a", "actor"), ("m0", "d", "actor")],
        "tconst string, nconst string, category string")
    crew = spark.createDataFrame(
        [(f"m{i}", ["d", "d"]) for i in range(6)],
        "tconst string, directors array<string>")
    names = spark.createDataFrame([("a", "Actor"), ("d", "Director")],
                                  "nconst string, primaryName string")
    pairs, details = q.pair_comparison(movies, principals, crew, names)
    rows = pairs.collect()
    assert len(rows) == 1, rows
    r = rows[0]
    assert r.director_id == "d" and r.actor_id == "a"
    assert r.shared_movies == r.director_other_movies == r.actor_other_movies == 3
    assert r.shared_mean_rating == 8.0
    assert r.director_other_mean_rating == r.actor_other_mean_rating == 6.0
    assert r.vs_director_others == r.vs_actor_others == 2.0
    assert r.above_both_baselines and details.count() == 3
    assert q.pair_comparison(movies, principals, crew, names, 4)[0].count() == 0
    assert q.pair_comparison(movies, principals, crew, names, 3, 4)[0].count() == 0
    tied = movies.withColumn("averageRating", q.F.lit(6.0))
    tied_pairs, _ = q.pair_comparison(tied, principals, crew, names)
    assert not tied_pairs.first().above_both_baselines
    # Different baseline sizes must not turn a fractional-rating tie positive.
    fractional = movies.withColumn("averageRating", q.F.lit(6.3))
    extra = spark.createDataFrame(
        [("m9", "Extra director film", 2000, 6.3, 1000),
         ("m10", "Extra actor film", 2000, 6.3, 1000)], movies.schema)
    more_principals = principals.unionByName(spark.createDataFrame(
        [("m10", "a", "actor")], principals.schema))
    more_crew = crew.unionByName(spark.createDataFrame(
        [("m9", ["d"])], crew.schema))
    fractional_pairs, _ = q.pair_comparison(
        fractional.unionByName(extra), more_principals, more_crew, names)
    fractional_pair = fractional_pairs.first()
    assert fractional_pair.vs_director_others == 0
    assert fractional_pair.vs_actor_others == 0
    assert not fractional_pair.above_both_baselines
    summary = q.summarize(pairs).first()
    assert summary.eligible_pairs == 1 and summary.pct_above_both == 100
    empty = q.summarize(pairs.filter("false")).first()
    assert empty.eligible_pairs == empty.pairs_above_both == 0
    assert empty.pct_above_both is None
    print("ok pairs: deduplication, self-credits, baselines, ties and empty results")


def check_selection(spark):
    films = spark.createDataFrame(
        [("old", "Old", 1979), ("first", "First", 1980),
         ("last", "Last", 2025), ("future", "Future", 2026),
         ("few", "Few votes", 2000), ("none", "Unrated", 2000)],
        "tconst string, primaryTitle string, startYear int")
    ratings = spark.createDataFrame(
        [(n, 8.0, 1000 if n != "few" else 999)
         for n in ["old", "first", "last", "future", "few"]],
        "tconst string, averageRating double, numVotes int")
    selected = q.rated_movies(films, ratings, 1000, 2025)
    assert {r.tconst for r in selected.collect()} == {"first", "last"}
    print("ok selection: year boundaries, vote threshold and unrated exclusion")


if __name__ == "__main__":
    spark = get_spark("test-open-question")
    spark.conf.set("spark.sql.shuffle.partitions", "4")
    try:
        check_selection(spark)
        check_pairs(spark)
        print("all open question checks passed")
    finally:
        spark.stop()
