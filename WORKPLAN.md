# Work plan – Group 04

**Deadline: Sunday 15 November 2026, 23:59 (Paris time).** No extension is
possible any more, and each late day costs 1 point.

Each person writes the code for their own tasks and opens their own pull
requests from their own GitHub account. Each person also writes the
`REPORT.md` sections for their own tasks **themselves, without AI**.

## Who does what

| Person | Tasks (one branch and PR each) | Reviewed by |
| ------ | ------------------------------ | ----------- |
| Axel | Project init ✅, Data preparation, Streaming | Victor |
| Victor | Exploration questions 1–8 | Nils |
| Nils | Enrichment, Open question | Axel |

PR #1 (project init) was reviewed and approved by Victor before this plan
was agreed.

### Branches

| Owner | Task | Branch | `REPORT.md` section | Reviewer |
| ----- | ---- | ------ | ------------------- | -------- |
| Axel (axou947) | Project init ✅ (PR #1) | `feat/project-init` | – | Victor (done) |
| Axel (axou947) | Data preparation | `feat/data-preparation` | 1 | Victor |
| Axel (axou947) | Streaming | `feat/streaming` | 4 | Victor |
| Victor (BaptVic78) | Exploration, questions 2.1–2.4 | `feat/exploration-part-1` | 2.1–2.4 | Nils |
| Victor (BaptVic78) | Exploration, questions 2.5–2.8 | `feat/exploration-part-2` | 2.5–2.8 | Nils |
| Nils (nilsgrd) | Enrichment (Wikipedia scraping) | `feat/enrichment` | 3 | Axel |
| Nils (nilsgrd) | Open question | `feat/open-question` | 5 | Axel |
| Axel (axou947) | Submission email to `joe@adaltas.com` | – | – | – |

Each section's **Methodological Explanation** is written by the owner of that
section. Victor writes the shared Methodological Explanation for section 2.

### What each task covers

- **Data preparation (Axel):** % of null/missing/empty values for every column
  of every table, the top 5 columns by % of nulls, other quality issues
  (death before birth, orphan foreign keys, impossible values), and the
  cleaning that writes the `clean` layer.
- **Exploration part 1 (Victor):**
  - 2.1 feature-length movies whose runtime is far from their genre average
  - 2.2 top 3 genres per year, 1980–2025
  - 2.3 how those top 3 genres compare to the other genres
  - 2.4 directors with exactly one movie rated ≥ 8.0 and their other movies averaging ≤ 6.0
- **Exploration part 2 (Victor):**
  - 2.5 TV series with the worst episode in the last season and the best one in seasons 1–2
  - 2.6 actors successful in 2+ and 3+ languages
  - 2.7 careers of 20+ years and 15+ movies that peaked early
  - 2.8 multi-talented professionals, and how they perform when holding several roles on one film
- **Enrichment (Nils):** synopsis for the top 10 films per genre and year
  (1980–2025), plus a biography for at least 3 principals of each film.
  Data comes from Wikipedia or another human-written open source. Respect
  rate limits, add a source-URL lineage field to every record, and write a
  note when a page is missing. Fetching can run outside Spark, but all
  cleaning and joins must be done in Spark and must work on the full dataset
  without code changes.
- **Streaming (Axel):** Wikipedia edit events go through Kafka into Spark
  Structured Streaming, which keeps only edits that match our IMDb titles or
  people. The filter must capture several events within 15–30 minutes. Late
  data is handled with watermarks.
- **Open question (Nils):** our own non-trivial question that needs
  multi-table joins. Ideas:
  1. Do recurring director–actor duos (3+ films together) get better ratings
     than each of them gets with other partners? (IMDb data only)
  2. The age gap between actors and actresses at release, by decade from
     1950 to 2025, and its link with ratings. (IMDb data only)
  3. The "Oscar effect": do a director's ratings and number of votes change
     after an Oscar win? (needs Wikidata, CC0)

## Order and dependencies

```text
PR #1 setup ──► data preparation ──► exploration 1 & 2
                       │          ├─► enrichment (Spark part)
                       │          └─► open question
                       └─────────────► streaming (matches IMDb titles/names)
```

You **don't need to wait** for data preparation to merge before writing
code. Write your jobs against the `clean` layer format below, and test them
once the preparation PR is merged. Nils can start the Wikipedia fetching
script right away.

## Suggested timeline (Paris time)

| Time | Milestone |
| ---- | --------- |
| 15:00 | PR #1 merged |
| 17:30 | Data preparation merged, `clean` layer available to everyone |
| 20:00 | Exploration part 1, enrichment PR opened |
| 21:00 | Streaming PR opened |
| 22:00 | Exploration part 2, open question PR opened |
| 22:00–23:15 | Reviews, fixes, `REPORT.md` write-ups |
| 23:30 | Everything merged on `main`, submission email sent |

## Shared conventions

### Git

- Branch from an up-to-date `main`:
  `git switch main && git pull && git switch -c feat/<task>`.
- Never commit directly to `main`. Every change goes through a pull request,
  and the reviewer approves it before merging.
- Commit with **your own** GitHub-linked email. To check it, run
  `git config user.email`. GitHub's "noreply" address works:
  `<id>+<username>@users.noreply.github.com`.
- Keep pull requests small, one task per PR. The PR description says what
  changed and how to test it.
- When you review, actually run the code and leave real comments. The quality
  of PR discussions is graded.

### Code

- Spark jobs go in `project/jobs/`, numbered by step:
  - `10_preparation.py`
  - `20_exploration_part1.py`
  - `21_exploration_part2.py`
  - `30_enrichment.py`
  - `40_streaming.py`
  - `50_open_question.py`
- Host-side scripts (Kafka producer, Wikipedia fetching) go in
  `project/scripts/`.
- Use the helpers in `project/jobs/common.py`: `get_spark()`,
  `read_table()`, `save_result()`.
- Save every result shown in `REPORT.md` with
  `save_result(df, "<section>_<name>")`. It is written to `project/output/`.
- Add a row for your step to the "Running the project" table in
  `PROJECT.md`, with the exact command.
- Python style: PEP 8.

### Documentation

- `PROJECT.md` → **Use of AI / LLM tools**: if you used an AI tool for your
  code, add a line naming the tool and the tasks it helped with.
- `REPORT.md`: result tables can be copied from `project/output/`. The
  explanations, methodology, alternatives and trade-offs must be written by
  you, with no AI.

## Format of the `clean` layer

The data-preparation job writes one Parquet table per IMDb table to
`data/clean/<table>`. Read them with `read_table(spark, "<table>")`.

- Every `\N` or empty value becomes a real `null`.
- Comma-separated lists become arrays.
- Rows whose foreign key points to a missing parent row are removed from the
  child tables.
- Impossible values (for example a death year before the birth year) are
  set to `null`.

The preparation PR documents each rule in detail.

| Table | Columns (type) |
| ----- | -------------- |
| `title_basics` | `tconst`, `titleType`, `primaryTitle`, `originalTitle` (string), `isAdult` (boolean), `startYear`, `endYear`, `runtimeMinutes` (int), `genres` (array&lt;string&gt;) |
| `title_ratings` | `tconst` (string), `averageRating` (double), `numVotes` (int) |
| `title_principals` | `tconst` (string), `ordering` (int), `nconst`, `category`, `job`, `characters` (string) |
| `title_crew` | `tconst` (string), `directors`, `writers` (array&lt;string&gt;) |
| `title_episode` | `tconst`, `parentTconst` (string), `seasonNumber`, `episodeNumber` (int) |
| `name_basics` | `nconst`, `primaryName` (string), `birthYear`, `deathYear` (int), `primaryProfession`, `knownForTitles` (array&lt;string&gt;) |
| `title_akas` | `titleId`, `title`, `region`, `language` (string), `ordering` (int), `types`, `attributes` (array&lt;string&gt;), `isOriginalTitle` (boolean) |

**Feature-length film:** `titleType == "movie"` and `runtimeMinutes > 40`,
following the definition used by the Academy, the AFI and the BFI. The
preparation PR adds a `feature_films(spark)` helper to `common.py` so that
everyone uses the same definition.
