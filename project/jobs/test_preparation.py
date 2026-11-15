"""Regression checks for 10_preparation.py, using real IMDb records.

Run (needs the parquet layer; the clean-layer checks run when it exists):
    docker compose exec spark python /home/jovyan/jobs/test_preparation.py
"""
import importlib

from pyspark.sql import functions as F

from common import CLEAN_DIR, get_spark, read_table

prep = importlib.import_module("10_preparation")

# Real multi-value records: (titleId, ordering) -> expected arrays.
AKAS_CASES = {
    ("tt0007189", 12): {"types": None,
                        "attributes": ["reissue title", "recut version"]},
    ("tt0008133", 9): {"types": None,
                       "attributes": ["8mm release title", "short version"]},
    ("tt0022698", 34): {"types": ["imdbDisplay", "tv"], "attributes": None},
}
GENRES_CASE = ("tt0000003", ["Animation", "Comedy", "Romance"])


def check_typed_akas(typed):
    """The typing step splits akas lists on the STX character."""
    akas = typed["title_akas"]
    for (title_id, ordering), expected in AKAS_CASES.items():
        row = (akas.filter((F.col("titleId") == title_id)
                           & (F.col("ordering") == ordering))
               .select("types", "attributes").first())
        assert row is not None, f"{title_id}/{ordering} not found"
        for col, value in expected.items():
            assert row[col] == value, (
                f"{title_id}/{ordering} {col}: {row[col]!r} != {value!r}")
    print("ok  typed akas: types/attributes split on \\x02")


def check_typed_genres(typed):
    """Comma-separated lists are unaffected by the akas separator."""
    tconst, expected = GENRES_CASE
    row = (typed["title_basics"].filter(F.col("tconst") == tconst)
           .select("genres").first())
    assert row["genres"] == expected, f"{tconst} genres: {row['genres']!r}"
    print("ok  typed genres: comma split")


def check_clean_akas(spark):
    """No element of the clean akas lists still holds a separator."""
    if not (CLEAN_DIR / "title_akas").exists():
        print("skip clean akas: run 10_preparation.py clean first")
        return
    akas = read_table(spark, "title_akas")
    for col in ("types", "attributes"):
        bad = (akas.select(F.explode(col).alias("v"))
               .filter(F.col("v").contains(prep.AKAS_SEP)).count())
        assert bad == 0, f"clean title_akas.{col}: {bad} unsplit values"
    title_id, ordering = "tt0007189", 12
    row = (akas.filter((F.col("titleId") == title_id)
                       & (F.col("ordering") == ordering))
           .select("attributes").first())
    assert row["attributes"] == ["reissue title", "recut version"], row
    print("ok  clean akas: no unsplit values")


def main():
    spark = get_spark("imdb-preparation-tests")
    typed, _ = prep.typed_tables(spark)
    check_typed_akas(typed)
    check_typed_genres(typed)
    check_clean_akas(spark)
    print("all preparation checks passed")
    spark.stop()


if __name__ == "__main__":
    main()
