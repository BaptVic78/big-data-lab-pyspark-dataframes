"""Data preparation: null profiling, quality checks and the ``clean`` layer.

Steps (run all by default, or pass one of them as argument):

    profile  % of null / missing (``\\N``) / empty values per column
             -> output/1_1_null_profile, output/1_2_top5_null_columns
    clean    type every table, detect quality issues, apply the handling
             rules and write data/clean/<table>
             -> output/1_3_quality_issues

Run:
    docker compose exec spark python /home/jovyan/jobs/10_preparation.py
    docker compose exec spark python /home/jovyan/jobs/10_preparation.py profile
"""
import sys
import time

from pyspark.sql import functions as F
from pyspark.sql import types as T

from common import (CLEAN_DIR, TABLES, get_spark, read_table, save_result,
                    to_markdown)

NULL_TOKEN = "\\N"           # how IMDb writes a missing value
CURRENT_YEAR = 2026
MAX_RUNTIME = 60 * 24 * 7    # a week; anything longer is an encoding error


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def missing(c):
    """True when a raw string column holds no real value."""
    col = F.col(c)
    return col.isNull() | (col == NULL_TOKEN) | (F.trim(col) == "")


def as_string(c):
    """Raw string with every missing value turned into a real null."""
    return F.when(missing(c), None).otherwise(F.col(c)).alias(c)


def as_int(c):
    """Integer value, null when missing or not a number."""
    return F.expr(f"try_cast(nullif(nullif(trim({c}), ''), '\\\\N') AS INT)") \
        .alias(c)


def as_double(c):
    return F.expr(
        f"try_cast(nullif(nullif(trim({c}), ''), '\\\\N') AS DOUBLE)").alias(c)


def as_bool(c):
    """IMDb booleans are written 0 / 1."""
    return (F.when(F.col(c) == "1", True)
            .when(F.col(c) == "0", False)
            .otherwise(None).alias(c))


def as_array(c):
    """Comma-separated list -> array<string>; null when missing."""
    return (F.when(missing(c), None)
            .otherwise(F.split(F.col(c), ",")).alias(c))


class IssueLog:
    """Collects (table, issue, rows affected, handling) for the report."""

    def __init__(self):
        self.rows = []

    def add(self, table, issue, count, handling):
        print(f"  [{table}] {issue}: {count:,d} -> {handling}")
        self.rows.append((table, issue, int(count), handling))

    def to_df(self, spark):
        schema = T.StructType([
            T.StructField("table", T.StringType()),
            T.StructField("issue", T.StringType()),
            T.StructField("rows_affected", T.LongType()),
            T.StructField("handling", T.StringType()),
        ])
        return spark.createDataFrame(self.rows, schema)


def write_clean(df, name):
    df.write.mode("overwrite").parquet(str(CLEAN_DIR / name))


def count_dupes(df, key):
    """Number of rows beyond the first one for each key."""
    total = df.count()
    distinct = df.select(*key).distinct().count()
    return total - distinct


# --------------------------------------------------------------------------
# Step 1 - null profile
# --------------------------------------------------------------------------
def profile(spark):
    """Null / missing / empty counts for every column of every table."""
    results = []
    for name in TABLES:
        df = read_table(spark, name, layer="parquet")
        aggs = [F.count(F.lit(1)).alias("__rows")]
        for c in df.columns:
            aggs += [
                F.sum(F.col(c).isNull().cast("int")).alias(f"{c}__null"),
                F.sum((F.col(c) == NULL_TOKEN).cast("int"))
                .alias(f"{c}__token"),
                F.sum((F.trim(F.col(c)) == "").cast("int"))
                .alias(f"{c}__empty"),
            ]
        row = df.agg(*aggs).first()
        total = row["__rows"]
        for c in df.columns:
            n_null = row[f"{c}__null"] or 0
            n_token = row[f"{c}__token"] or 0
            n_empty = row[f"{c}__empty"] or 0
            n_all = n_null + n_token + n_empty
            results.append((name, c, total, n_null, n_token, n_empty, n_all,
                            round(100.0 * n_all / total, 2)))
        print(f"profiled {name}")

    cols = ["table", "column", "total_rows", "null", "missing_token_N",
            "empty", "total_missing", "pct_missing"]
    prof = spark.createDataFrame(results, cols).orderBy("table", "column")
    save_result(prof, "1_1_null_profile")
    top5 = prof.orderBy(F.desc("pct_missing"), "table", "column").limit(5)
    save_result(top5, "1_2_top5_null_columns")
    print(to_markdown(top5))


# --------------------------------------------------------------------------
# Step 2 - typing, quality checks and cleaning
# --------------------------------------------------------------------------
def typed_tables(spark):
    """Cast every raw table to the types of the clean-layer contract."""
    raw = {n: read_table(spark, n, layer="parquet") for n in TABLES}
    return {
        "title_basics": raw["title_basics"].select(
            as_string("tconst"), as_string("titleType"),
            as_string("primaryTitle"), as_string("originalTitle"),
            as_bool("isAdult"), as_int("startYear"), as_int("endYear"),
            as_int("runtimeMinutes"), as_array("genres")),
        "title_ratings": raw["title_ratings"].select(
            as_string("tconst"), as_double("averageRating"),
            as_int("numVotes")),
        "title_principals": raw["title_principals"].select(
            as_string("tconst"), as_int("ordering"), as_string("nconst"),
            as_string("category"), as_string("job"),
            as_string("characters")),
        "title_crew": raw["title_crew"].select(
            as_string("tconst"), as_array("directors"),
            as_array("writers")),
        "title_episode": raw["title_episode"].select(
            as_string("tconst"), as_string("parentTconst"),
            as_int("seasonNumber"), as_int("episodeNumber")),
        "name_basics": raw["name_basics"].select(
            as_string("nconst"), as_string("primaryName"),
            as_int("birthYear"), as_int("deathYear"),
            as_array("primaryProfession"), as_array("knownForTitles")),
        "title_akas": raw["title_akas"].select(
            as_string("titleId"), as_int("ordering"), as_string("title"),
            as_string("region"), as_string("language"), as_array("types"),
            as_array("attributes"), as_bool("isOriginalTitle")),
    }, raw


def invalid_casts(raw_df, typed_df, columns, log, table):
    """Values present in the raw table that could not be cast."""
    for c in columns:
        n = (raw_df.select(F.col(c).alias("raw"))
             .withColumn("typed", F.expr(
                 f"try_cast(nullif(nullif(trim(raw), ''), '\\\\N') AS DOUBLE)"))
             .filter(~missing("raw") & F.col("typed").isNull())
             .count())
        if n:
            log.add(table, f"non-numeric value in {c}", n, "set to null")


def filter_id_array(df, key, array_col, ref_ids):
    """Remove ids of ``array_col`` that do not exist in ``ref_ids``.

    Returns the cleaned frame and the number of ids removed. An array whose
    ids are all orphans becomes null.

    Only the (few) rows that contain an orphan id are regrouped, which
    keeps the memory footprint small: regrouping every row with
    collect_list ran out of heap on a 4 GB driver.
    """
    orphan_pairs = (df.select(key, F.explode(array_col).alias("id"))
                    .join(ref_ids, "id", "left_anti"))
    orphans_per_row = (orphan_pairs.groupBy(key)
                       .agg(F.collect_set("id").alias("_orphans")))
    orphans = orphan_pairs.count()
    cleaned_col = F.array_except(F.col(array_col), F.col("_orphans"))
    cleaned = (df.join(orphans_per_row, key, "left")
               .withColumn(array_col, F.when(
                   F.col("_orphans").isNull(), F.col(array_col))
                   .when(F.size(cleaned_col) > 0, cleaned_col))
               .select(*df.columns))
    return cleaned, orphans


def clean(spark):
    log = IssueLog()
    t, raw = typed_tables(spark)

    # ---- titles --------------------------------------------------------
    print("title_basics")
    basics = t["title_basics"]
    invalid_casts(raw["title_basics"], basics,
                  ["startYear", "endYear", "runtimeMinutes"], log,
                  "title_basics")
    log.add("title_basics", "duplicate tconst",
            count_dupes(basics, ["tconst"]), "keep first row")
    basics = basics.dropDuplicates(["tconst"])

    n = basics.filter(F.col("runtimeMinutes") <= 0).count()
    log.add("title_basics", "runtimeMinutes <= 0", n, "set to null")
    n = basics.filter(F.col("runtimeMinutes") > MAX_RUNTIME).count()
    log.add("title_basics", f"runtimeMinutes > {MAX_RUNTIME} (1 week)", n,
            "set to null")
    n = basics.filter(F.col("startYear") > CURRENT_YEAR).count()
    log.add("title_basics", f"startYear after {CURRENT_YEAR} (unreleased)",
            n, "kept")
    n = basics.filter(F.col("endYear") < F.col("startYear")).count()
    log.add("title_basics", "endYear before startYear", n,
            "endYear set to null")
    n = basics.filter(F.col("startYear") < 1874).count()
    log.add("title_basics", "startYear before 1874 (first film)", n,
            "startYear set to null")

    basics = (basics
              .withColumn("runtimeMinutes", F.when(
                  (F.col("runtimeMinutes") > 0)
                  & (F.col("runtimeMinutes") <= MAX_RUNTIME),
                  F.col("runtimeMinutes")))
              .withColumn("startYear", F.when(
                  F.col("startYear") >= 1874, F.col("startYear")))
              .withColumn("endYear", F.when(
                  F.col("startYear").isNull()
                  | (F.col("endYear") >= F.col("startYear")),
                  F.col("endYear"))))
    write_clean(basics, "title_basics")
    basics = read_table(spark, "title_basics")
    title_ids = basics.select(F.col("tconst").alias("id"))

    # ---- people --------------------------------------------------------
    print("name_basics")
    names = t["name_basics"]
    invalid_casts(raw["name_basics"], names, ["birthYear", "deathYear"],
                  log, "name_basics")
    log.add("name_basics", "duplicate nconst",
            count_dupes(names, ["nconst"]), "keep first row")
    names = names.dropDuplicates(["nconst"])

    n = names.filter(F.col("deathYear") < F.col("birthYear")).count()
    log.add("name_basics", "died before they were born", n,
            "birthYear and deathYear set to null")
    n = names.filter(F.col("birthYear") > CURRENT_YEAR).count()
    log.add("name_basics", f"birthYear after {CURRENT_YEAR}", n,
            "birthYear set to null")
    n = names.filter(F.col("deathYear") > CURRENT_YEAR).count()
    log.add("name_basics", f"deathYear after {CURRENT_YEAR}", n,
            "deathYear set to null")
    n = names.filter((F.col("deathYear") - F.col("birthYear")) > 120).count()
    log.add("name_basics", "lifespan over 120 years", n,
            "birthYear and deathYear set to null")
    n = names.filter(F.col("deathYear").isNull()
                     & (F.col("birthYear") < CURRENT_YEAR - 120)).count()
    log.add("name_basics", "alive and older than 120 years", n,
            "kept")

    bad_dates = ((F.col("deathYear") < F.col("birthYear"))
                 | ((F.col("deathYear") - F.col("birthYear")) > 120))
    names = (names
             .withColumn("_bad", F.coalesce(bad_dates, F.lit(False)))
             .withColumn("birthYear", F.when(
                 ~F.col("_bad") & (F.col("birthYear") <= CURRENT_YEAR),
                 F.col("birthYear")))
             .withColumn("deathYear", F.when(
                 ~F.col("_bad") & (F.col("deathYear") <= CURRENT_YEAR),
                 F.col("deathYear")))
             .drop("_bad"))
    names, n = filter_id_array(names, "nconst", "knownForTitles", title_ids)
    log.add("name_basics", "knownForTitles id not in title_basics", n,
            "id removed from the array")
    write_clean(names, "name_basics")
    names = read_table(spark, "name_basics")
    name_ids = names.select(F.col("nconst").alias("id"))

    # ---- ratings -------------------------------------------------------
    print("title_ratings")
    ratings = t["title_ratings"].dropDuplicates(["tconst"])
    n = ratings.filter(~F.col("averageRating").between(1, 10)
                       | (F.col("numVotes") <= 0)).count()
    log.add("title_ratings", "rating outside 1-10 or numVotes <= 0", n,
            "row removed")
    ratings = ratings.filter(F.col("averageRating").between(1, 10)
                             & (F.col("numVotes") > 0))
    n = ratings.join(basics, "tconst", "left_anti").count()
    log.add("title_ratings", "tconst not in title_basics", n, "row removed")
    write_clean(ratings.join(basics.select("tconst"), "tconst", "left_semi"),
                "title_ratings")

    # ---- episodes ------------------------------------------------------
    print("title_episode")
    episodes = t["title_episode"].dropDuplicates(["tconst"])
    n = episodes.join(basics, "tconst", "left_anti").count()
    log.add("title_episode", "tconst not in title_basics", n, "row removed")
    parents = basics.select(F.col("tconst").alias("parentTconst"),
                            F.col("titleType").alias("parentType"))
    n = episodes.join(parents, "parentTconst", "left_anti").count()
    log.add("title_episode", "parentTconst not in title_basics", n,
            "row removed")
    n = (episodes.join(parents, "parentTconst")
         .filter(~F.col("parentType").isin("tvSeries", "tvMiniSeries"))
         .count())
    log.add("title_episode", "parent is not a tvSeries / tvMiniSeries", n,
            "kept")
    n = episodes.filter(F.col("seasonNumber").isNull()
                        | F.col("episodeNumber").isNull()).count()
    log.add("title_episode", "missing season or episode number", n,
            "kept")
    write_clean(episodes
                .join(basics.select("tconst"), "tconst", "left_semi")
                .join(parents.select("parentTconst"), "parentTconst",
                      "left_semi")
                .select("tconst", "parentTconst", "seasonNumber",
                        "episodeNumber"),
                "title_episode")

    # ---- akas ----------------------------------------------------------
    print("title_akas")
    akas = t["title_akas"].dropDuplicates(["titleId", "ordering"])
    n = akas.join(title_ids.withColumnRenamed("id", "titleId"), "titleId",
                  "left_anti").count()
    log.add("title_akas", "titleId not in title_basics", n, "row removed")
    write_clean(akas.join(title_ids.withColumnRenamed("id", "titleId"),
                          "titleId", "left_semi"), "title_akas")

    # ---- crew ----------------------------------------------------------
    print("title_crew")
    crew = t["title_crew"].dropDuplicates(["tconst"])
    n = crew.join(basics, "tconst", "left_anti").count()
    log.add("title_crew", "tconst not in title_basics", n, "row removed")
    crew = crew.join(basics.select("tconst"), "tconst", "left_semi")
    for col_name in ("directors", "writers"):
        crew, n = filter_id_array(crew, "tconst", col_name, name_ids)
        log.add("title_crew", f"{col_name} id not in name_basics", n,
                "id removed from the array")
    write_clean(crew, "title_crew")

    # ---- principals ----------------------------------------------------
    print("title_principals")
    principals = t["title_principals"].dropDuplicates(["tconst", "ordering"])
    n = principals.join(basics.select("tconst"), "tconst",
                        "left_anti").count()
    log.add("title_principals", "tconst not in title_basics", n,
            "row removed")
    n = principals.join(names.select("nconst"), "nconst",
                        "left_anti").count()
    log.add("title_principals", "nconst not in name_basics", n,
            "row removed")

    linked = (principals
              .join(basics.select("tconst", "startYear"), "tconst")
              .join(names.select("nconst", "birthYear", "deathYear"),
                    "nconst"))
    archive = F.col("category").isin("archive_footage", "archive_sound")
    born_after = F.col("birthYear") > F.col("startYear")
    died_before = (F.col("deathYear") < F.col("startYear") - 1) & ~archive
    n = linked.filter(born_after & ~archive).count()
    log.add("title_principals", "person born after the title's release", n,
            "row removed (archive footage kept)")
    n = linked.filter(died_before).count()
    log.add("title_principals",
            "person died 2+ years before the title's release", n,
            "kept")
    write_clean(linked
                .filter(~F.coalesce(born_after & ~archive, F.lit(False)))
                .select("tconst", "ordering", "nconst", "category", "job",
                        "characters"),
                "title_principals")

    issues = log.to_df(spark)
    save_result(issues, "1_3_quality_issues")
    print(to_markdown(issues, limit=100))


def summary(spark):
    """Row counts before / after cleaning."""
    rows = []
    for name in TABLES:
        before = read_table(spark, name, layer="parquet").count()
        after = read_table(spark, name).count()
        rows.append((name, before, after, before - after))
    df = spark.createDataFrame(
        rows, ["table", "rows_raw", "rows_clean", "rows_removed"])
    save_result(df, "1_4_row_counts")
    print(to_markdown(df))


def main(steps):
    spark = get_spark("imdb-preparation")
    steps = steps or ["profile", "clean", "summary"]
    for step in steps:
        start = time.time()
        print(f"=== {step} ===")
        {"profile": profile, "clean": clean, "summary": summary}[step](spark)
        print(f"=== {step} done in {time.time() - start:.0f}s ===")
    spark.stop()


if __name__ == "__main__":
    main(sys.argv[1:])
