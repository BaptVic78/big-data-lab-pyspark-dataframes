"""Checks for the matching logic of 40_streaming.py, without Kafka.

Run (needs the clean layer):
    docker compose exec spark python /home/jovyan/jobs/test_streaming.py
"""
import importlib
import json
import shutil
import tempfile
from pathlib import Path

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


ENTITY_COLUMNS = ["key", "entity_type", "imdb_id", "label", "votes"]


def check_one_entity_per_key(spark):
    """A name shared by a title and a person matches an edit only once."""
    candidates = spark.createDataFrame([
        # cross-type collision: the title wins even with fewer votes
        ("doug", "title", "tt0101084", "Doug", 100),
        ("doug", "person", "nm16578308", "Doug", 5000),
        # same type: most votes wins
        ("heat", "title", "tt0113277", "Heat", 700000),
        ("heat", "title", "tt2404463", "The Heat", 180000),
        # full tie: smallest IMDb id wins
        ("twins", "person", "nm0000002", "Twins", 10),
        ("twins", "person", "nm0000001", "Twins", 10),
    ], ENTITY_COLUMNS)
    entities = streaming.one_per_key(candidates)
    picked = {r.key: r.imdb_id for r in entities.collect()}
    assert picked == {"doug": "tt0101084", "heat": "tt0113277",
                      "twins": "nm0000001"}, picked

    raw = spark.createDataFrame(
        [(json.dumps({"id": 7, "type": "edit", "title": "Doug",
                      "timestamp": 1700000000}).encode("utf-8"),)],
        ["value"])
    rows = streaming.match_edits(streaming.parse_edits(raw),
                                 entities).collect()
    assert len(rows) == 1, f"one edit gave {len(rows)} rows"
    assert (rows[0].entity_type, rows[0].imdb_id) == ("title", "tt0101084")
    print("ok  one entity per key: cross-type collision gives one row")


def check_late_event_dropped(spark):
    """An old event sent after the watermark moved on is not counted.

    Runs the real window query on a file stream, one file per micro-batch:
      1. an edit at T
      2. an edit at T + 30 min   -> watermark becomes T + 20 min
      3. an edit at T + 1 min    -> its window [T, T+5) is already closed
    """
    t0 = 1700000100  # 2023-11-14 22:15:00 UTC, start of a 5-minute window
    batches = [
        {"id": 1, "type": "edit", "title": "Doug", "timestamp": t0},
        {"id": 2, "type": "edit", "title": "Doug", "timestamp": t0 + 1800},
        {"id": 3, "type": "edit", "title": "Doug", "timestamp": t0 + 60},
    ]
    entities = spark.createDataFrame(
        [("doug", "title", "tt0101084", "Doug", 100)], ENTITY_COLUMNS)

    tmp = Path(tempfile.mkdtemp(prefix="test_streaming_"))
    source, updates = tmp / "in", tmp / "updates"
    source.mkdir()
    try:
        raw = (spark.readStream.option("maxFilesPerTrigger", 1)
               .text(str(source)))
        matched = streaming.match_edits(streaming.parse_edits(raw), entities)
        query = (
            streaming.window_counts(matched).writeStream.outputMode("update")
            .foreachBatch(streaming.window_update_writer(updates, show=False))
            .option("checkpointLocation", str(tmp / "checkpoint"))
            .start()
        )
        for i, event in enumerate(batches):
            (source / f"{i}.json").write_text(json.dumps(event) + "\n",
                                              encoding="utf-8")
            query.processAllAvailable()
        query.stop()

        all_matched = streaming.match_edits(
            streaming.parse_edits(spark.read.text(str(source))), entities)
        report = streaming.window_report(
            streaming.final_window_counts(spark, updates), all_matched)
        got = [(r.window_start.strftime("%H:%M"), r.edits_streaming,
                r.edits_all, r.late_not_counted) for r in report.collect()]
        assert got == [("22:15", 1, 2, 1), ("22:45", 1, 1, 0)], got
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("ok  watermark: late edit kept in storage, not in the "
          "streaming count")


if __name__ == "__main__":
    spark = get_spark("test_streaming")
    check_normalize(spark)
    check_one_entity_per_key(spark)
    check_late_event_dropped(spark)
    check_parse_and_match(spark)
    print("all streaming checks passed")
