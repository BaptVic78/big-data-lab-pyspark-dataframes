"""Shared helpers for every Spark job of the project.

All jobs run inside the ``imdb_spark`` container, for example::

    docker compose exec spark python /home/jovyan/jobs/00_ingest.py
"""
import os
from pathlib import Path

from pyspark.sql import SparkSession

DATA_DIR = Path(os.environ.get("IMDB_DATA_DIR", "/home/jovyan/data"))
OUTPUT_DIR = Path(os.environ.get("IMDB_OUTPUT_DIR", "/home/jovyan/output"))

RAW_DIR = DATA_DIR / "raw"          # original .tsv.gz files
PARQUET_DIR = DATA_DIR / "parquet"  # typed copy of the raw tables
CLEAN_DIR = DATA_DIR / "clean"      # tables after data preparation

KAFKA_PACKAGE = "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"

# IMDb table name -> raw file name
TABLES = {
    "name_basics": "name.basics.tsv.gz",
    "title_akas": "title.akas.tsv.gz",
    "title_basics": "title.basics.tsv.gz",
    "title_crew": "title.crew.tsv.gz",
    "title_episode": "title.episode.tsv.gz",
    "title_principals": "title.principals.tsv.gz",
    "title_ratings": "title.ratings.tsv.gz",
}


def get_spark(app_name, kafka=False):
    """Create (or reuse) a local SparkSession sized for a laptop."""
    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory",
                os.environ.get("SPARK_DRIVER_MEMORY", "4g"))
        .config("spark.sql.shuffle.partitions", "64")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.session.timeZone", "UTC")
    )
    if kafka:
        builder = builder.config("spark.jars.packages", KAFKA_PACKAGE)
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def read_table(spark, name, layer="clean"):
    """Read one IMDb table from the ``parquet`` or ``clean`` layer."""
    base = CLEAN_DIR if layer == "clean" else PARQUET_DIR
    return spark.read.parquet(str(base / name))


def save_result(df, name, limit=None):
    """Save a result table as one CSV file under output/<name>/.

    Results are small, so coalescing to a single file keeps them easy to
    paste into REPORT.md.
    """
    if limit is not None:
        df = df.limit(limit)
    (df.coalesce(1).write.mode("overwrite")
       .option("header", "true").csv(str(OUTPUT_DIR / name)))
