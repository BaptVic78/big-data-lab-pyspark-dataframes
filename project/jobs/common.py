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
    """Create (or reuse) a local SparkSession sized for a laptop.

    Memory budget inside the 6 GB container: 3 GB heap + at most 1.5 GB of
    direct (off-heap) buffers + JVM/Python overhead.

    Parquet reads go through Java NIO, which allocates a temporary direct
    buffer as large as each read (~128 MB) and, by default, keeps it cached
    per thread forever. With many threads these cached buffers filled the
    container ("Cannot allocate memory"), so caching is limited to 256 KB
    buffers and parallelism is capped. Values can be overridden with
    environment variables.
    """
    cores = os.environ.get("SPARK_LOCAL_CORES", "4")
    builder = (
        SparkSession.builder.appName(app_name)
        .master(f"local[{cores}]")
        .config("spark.driver.memory",
                os.environ.get("SPARK_DRIVER_MEMORY", "3g"))
        .config("spark.driver.extraJavaOptions",
                "-XX:MaxDirectMemorySize="
                + os.environ.get("SPARK_MAX_DIRECT_MEMORY", "1536m")
                + " -Djdk.nio.maxCachedBufferSize=262144")
        .config("spark.sql.shuffle.partitions", "128")
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


FEATURE_MIN_RUNTIME = 40  # minutes, Academy / AFI / BFI definition


def feature_films(spark):
    """Feature-length films: titleType 'movie' running over 40 minutes."""
    from pyspark.sql import functions as F

    return read_table(spark, "title_basics").filter(
        (F.col("titleType") == "movie")
        & (F.col("runtimeMinutes") > FEATURE_MIN_RUNTIME)
    )


def to_markdown(df, limit=50):
    """Return the first ``limit`` rows of ``df`` as a Markdown table."""
    rows = df.limit(limit).collect()
    header = "| " + " | ".join(df.columns) + " |"
    sep = "| " + " | ".join("---" for _ in df.columns) + " |"
    body = [
        "| " + " | ".join("" if v is None else str(v) for v in row) + " |"
        for row in rows
    ]
    return "\n".join([header, sep] + body)


def save_result(df, name, limit=None):
    """Save a result table as one CSV file under output/<name>/.

    Results are small, so coalescing to a single file keeps them easy to
    paste into REPORT.md.
    """
    if limit is not None:
        df = df.limit(limit)
    (df.coalesce(1).write.mode("overwrite")
       .option("header", "true").csv(str(OUTPUT_DIR / name)))
    # Markdown preview (first 50 rows) ready to paste into REPORT.md.
    saved = df.sparkSession.read.option("header", "true").csv(
        str(OUTPUT_DIR / name))
    (OUTPUT_DIR / f"{name}.md").write_text(to_markdown(saved) + "\n",
                                           encoding="utf-8")
