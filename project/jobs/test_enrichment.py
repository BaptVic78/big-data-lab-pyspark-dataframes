"""Enrichment checks on small DataFrames, without network access."""
import importlib

from common import get_spark
from pyspark.sql import functions as F

q = importlib.import_module("30_enrichment")


def check_enrichment(spark):
    films = spark.createDataFrame([
        ("a", "A", "A", 1980, ["Drama", "Comedy"]),
        ("b", "B", "B", 1980, ["Drama"]),
        ("c", "C", "C", 1979, ["Drama"]),
        ("d", "D", "D", 2025, ["Drama"]),
        ("e", "E", "E", 2026, ["Drama"])],
        "tconst string, primaryTitle string, originalTitle string, "
        "startYear int, genres array<string>")
    ratings = spark.createDataFrame([
        ("a", 8.0, 100), ("b", 8.0, 200), ("c", 9.0, 100),
        ("d", 7.0, 100), ("e", 9.0, 100)],
        "tconst string, averageRating double, numVotes int")
    selected = q.top_films(films, ratings, 1)
    assert {(r.tconst, r.genre) for r in selected.collect()} == {
        ("a", "Comedy"), ("b", "Drama"), ("d", "Drama")}
    principals = spark.createDataFrame(
        [("a", f"nm{i}", i) for i in range(1, 5)] + [("a", "nm1", 5)],
        "tconst string, nconst string, ordering int")
    names = spark.createDataFrame([(f"nm{i}", f"Person {i}") for i in range(1, 5)],
                                  "nconst string, primaryName string")
    people = q.principal_candidates(selected, principals, names, 4)
    assert people.count() == 4
    assert q.requests_for(selected, people).count() == 7
    records = [dict(entity_id=e, kind=k, text=" Source\n text ", status="ok",
                    source_url="https://en.wikipedia.org/wiki/Example",
                    revision_url="https://en.wikipedia.org/w/index.php?oldid=1",
                    section="Plot" if k == "film" else "introduction")
               for e, k in [("a", "film"), ("nm1", "person"),
                            ("nm2", "person"), ("nm3", "person")]]
    raw = spark.createDataFrame(records, q.CACHE_SCHEMA)
    enriched, bios, attempts, coverage = q.enrich(selected, people, raw)
    assert bios.count() == 3 and attempts.count() == 4
    assert bios.first().text == "Source text"
    assert coverage.filter("complete").count() == 1
    missing = coverage.filter("tconst = 'b'").first()
    assert missing.synopsis_status == "not_fetched" and missing.available_biographies == 0
    assert enriched.filter("tconst = 'd'").first().status == "not_fetched"
    incomplete = raw.filter("entity_id != 'nm3'")
    assert q.enrich(selected, people, incomplete)[3].filter("complete").count() == 0
    bad_source = raw.withColumn("revision_url", F.lit(None).cast("string"))
    assert q.enrich(selected, people, bad_source)[3].filter("complete").count() == 0
    empty = spark.createDataFrame([], q.CACHE_SCHEMA)
    assert q.enrich(selected, people, empty)[3].filter("complete").count() == 0
    print("ok ranking, year limits, duplicate credits, source lineage and incomplete coverage")


if __name__ == "__main__":
    spark = get_spark("test-enrichment")
    spark.conf.set("spark.sql.shuffle.partitions", "4")
    try:
        check_enrichment(spark)
        print("all enrichment checks passed")
    finally:
        spark.stop()
