"""Convert the raw IMDb TSV files to Parquet (the ``parquet`` layer).

Every column is kept as a string and values are not altered: ``\\N`` and
empty strings are preserved so the data-preparation job can measure them.
Typing and cleaning happen later, in the preparation job.

Run:
    docker compose exec spark python /home/jovyan/jobs/00_ingest.py
"""
import sys

from common import PARQUET_DIR, RAW_DIR, TABLES, get_spark


def ingest_table(spark, name, file_name):
    """Read one TSV file as strings and write it as Parquet."""
    df = (
        spark.read.option("header", "true")
        .option("sep", "\t")
        # IMDb does not quote fields; titles may contain a raw '"'.
        .option("quote", "")
        # Keep "\N" and "" as they are instead of turning them into null.
        .option("nullValue", "\u0001__never__\u0001")
        .option("emptyValue", "")
        .option("inferSchema", "false")
        .csv(str(RAW_DIR / file_name))
    )
    df.write.mode("overwrite").parquet(str(PARQUET_DIR / name))
    written = spark.read.parquet(str(PARQUET_DIR / name))
    print(f"{name:18s} {written.count():>12,d} rows  {len(df.columns)} cols")


def main(selected):
    spark = get_spark("imdb-ingest")
    for name, file_name in TABLES.items():
        if selected and name not in selected:
            continue
        ingest_table(spark, name, file_name)
    spark.stop()


if __name__ == "__main__":
    main(sys.argv[1:])
