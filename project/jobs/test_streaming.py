"""Checks for the matching logic of 40_streaming.py, without Kafka.

Run (needs the clean layer):
    docker compose exec spark python /home/jovyan/jobs/test_streaming.py
"""
import importlib
import json

from common import get_spark

streaming = importlib.import_module("40_streaming")


def check_normalize(spark):
    rows = spark.createDataFrame(
        [("Inception (film)",), ("tom_hanks",), ("The  Matrix",),
         ("Heat (1995 film)",), ("Alien (film) (1979)",)], ["t"])
    out = [r.k for r in rows.select(streaming.normalize(streaming.F.col("t"))
                                    .alias("k")).collect()]
    assert out == ["inception", "tom hanks", "the matrix", "heat",
                   "alien (film)"], out
    print("ok  normalize: suffix removed, lower case, underscores")


def check_parse_and_match(spark):
    events = [
        {"id": 1, "type": "edit", "title": "Inception", "user": "a",
         "bot": False, "timestamp": 1700000000},
        {"id": 2, "type": "edit", "title": "Leonardo DiCaprio", "user": "b",
         "bot": True, "timestamp": 1700000060},
        {"id": 3, "type": "edit", "title": "Some unrelated page",
         "user": "c", "bot": False, "timestamp": 1700000120},
        {"id": 4, "type": "edit", "title": "Broken event", "user": "d",
         "bot": False, "timestamp": None},
    ]
    raw = spark.createDataFrame(
        [(json.dumps(e).encode("utf-8"),) for e in events], ["value"])
    entities = streaming.build_entities(spark, min_votes=500000)
    matched = streaming.match_edits(streaming.parse_edits(raw), entities)
    got = {r.id: (r.entity_type, r.imdb_id)
           for r in matched.collect()}
    assert got == {1: ("title", "tt1375666"), 2: ("person", "nm0000138")}, got
    print("ok  parse + match: Inception and DiCaprio kept, rest dropped")


if __name__ == "__main__":
    spark = get_spark("test_streaming")
    check_normalize(spark)
    check_parse_and_match(spark)
    print("all streaming checks passed")
