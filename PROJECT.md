# ECE Big Data Processing – IMDb Project (Group 04)

## Contributors

| Name           | GitHub username | Email           |
| -------------- | --------------- | --------------- |
| Nils GIRAUD    | nilsgrd         | TODO@edu.ece.fr |
| Axel ALACACHE  | axou947         | axel.alacache@edu.ece.fr |
| Victor ROULEAU | BaptVic78       | victor.rouleau@edu.ece.fr |

All project code lives in the [`project/`](project/) directory. Results and
methodology are in [`REPORT.md`](REPORT.md).

## Repository layout

```text
project/
├── compose.yaml          # Kafka + Spark/Jupyter containers
├── requirements.txt      # host-side Python deps (Kafka producer, scraper)
├── scripts/              # code that runs on the host (download, producer, scraping)
├── jobs/                 # PySpark jobs, run inside the Spark container
├── notebooks/            # optional Jupyter exploration (mounted at /home/jovyan/work)
├── data/                 # (git-ignored) raw, parquet and clean layers
└── output/               # (git-ignored) CSV results produced by the jobs
```

## Requirements

- Docker Desktop with **at least 7 GB of memory** allocated to Docker
  (Settings → Resources). The Spark container is capped at 6 GB and Spark
  runs 4 parallel tasks with a 3 GB heap and 1.5 GB of off-heap memory. These
  are set in `project/compose.yaml` (`SPARK_LOCAL_CORES`,
  `SPARK_DRIVER_MEMORY`, `SPARK_MAX_DIRECT_MEMORY`). If a job fails with
  `Cannot allocate memory` or `OutOfMemoryError`, lower `SPARK_LOCAL_CORES`
  and run `docker compose up -d` to apply the change.
- Python 3.10+ on the host (the pinned `requests==2.34.2` requires
  Python >= 3.10).
- About 10 GB of free disk space.

## Setup from scratch

All commands are run from the `project/` directory.

1. Create the host virtual environment and install dependencies.

    ```bash
    cd project
    python -m venv .venv
    # Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. Download the IMDb non-commercial datasets (~2 GB) into `data/raw/`.

    ```bash
    python scripts/download_imdb.py
    ```

3. Start the containers.

    ```bash
    docker compose up -d
    ```

    Jupyter is then available through the link printed by
    `docker logs imdb_spark` (port 8888) and the Spark UI on port 4040 while
    a job runs.

4. Convert the raw TSV files to Parquet (one-time, ~10–15 minutes: gzip files
   cannot be split, so each file is read by a single core).

    ```bash
    docker compose exec spark python /home/jovyan/jobs/00_ingest.py
    ```

> **Windows / Git Bash:** Git Bash rewrites paths such as `/home/jovyan/...`.
> Use PowerShell, or prefix the command with `MSYS_NO_PATHCONV=1`.

## Running the project

Each step reads the output of the previous ones, so run them in order.

| Step | Command | Output |
| ---- | ------- | ------ |
| Ingest | `docker compose exec spark python /home/jovyan/jobs/00_ingest.py` | `data/parquet/` |
| Data preparation (~30 min) | `docker compose exec spark python /home/jovyan/jobs/10_preparation.py` | `data/clean/`, `output/1_*` |
| [Open question](project/OPEN_QUESTION.md) | `docker compose exec spark python /home/jovyan/jobs/50_open_question.py` | `output/5_*` |
| Streaming (25 min) | see "Streaming" below | `output/4_*` |
| Exploration 2.1–2.4 | `docker compose exec spark python /home/jovyan/jobs/20_exploration_part1.py` | `output/2_1_*` through `output/2_4_*` |
| Exploration 2.5–2.8 | `docker compose exec spark python /home/jovyan/jobs/21_exploration_part2.py` | `output/2_5_*` through `output/2_8_*` |
| [Enrichment targets](project/ENRICHMENT.md) | `docker compose exec spark python /home/jovyan/jobs/30_enrichment.py prepare` | `data/enrichment/targets/`, `output/3_requests/` |
| Enrichment fetch (host) | `python scripts/fetch_wikipedia.py` | `data/enrichment/wikipedia/` |
| Enrichment joins | `docker compose exec spark python /home/jovyan/jobs/30_enrichment.py finalize` | `output/3_*` |

The exploration job accepts question numbers to rerun selected queries, for
example `python /home/jovyan/jobs/20_exploration_part1.py 2.2 2.3` inside the
Spark container. Question 2.1 uses feature films and an absolute population
z-score greater than 2 (`--runtime-z-score` to change it). Questions 2.2 and
2.3 rank genres by total IMDb votes over rated movies released in 1980–2025.
Each movie contributes to every listed genre, so the comparison reports
genre-assigned vote and film shares. Ties in votes are resolved by genre name.
Question 2.4 requires exactly one movie rated at least 8 and at least two
other rated movies averaging at most 6. Unrated movies do not enter these
counts or averages. CSV outputs contain every result; Markdown previews
contain the first 50 rows.

The second exploration job accepts selected question numbers and optional
`--success-rating` (default 7), `--success-votes` (default 1000), and
`--early-fraction` (default one third).

- 2.5 requires at least three numbered seasons, each with at least ten
  episodes with a known positive season number, even when the episode
  number is missing. Specials are excluded. Rating extrema use rated
  episodes; ties qualify if a best episode occurs in seasons 1–2 and a
  worst episode in the last season.
- 2.6 uses non-missing language codes from original-title variants in
  `title_akas` as a film-language proxy. IMDb title-language metadata does
  not establish the spoken language of a film. Coverage counts and
  film/actor/language evidence are exported alongside the 2+ and 3+
  language actor lists. Success requires both configured thresholds.
- 2.7 requires at least fifteen dated movie credits spanning twenty years.
  Early career is the first third of the observed calendar-year span.
  The best early rating must strictly exceed the best later rating; both
  periods need a rated movie. Future releases are excluded.
- 2.8 combines principal credits and crew arrays for actor, writer and
  director roles. It compares each multi-talented person's mean rated-film
  score for single-role and multiple-role projects. Unrated films remain
  in the film counts and are excluded from rating means. The export also
  lists multiple-role projects individually.

Outputs include full CSV tables and Markdown previews of up to fifty rows.
Run the focused boundary checks with
`docker compose exec spark python /home/jovyan/jobs/test_exploration_part2.py`.
The current local dataset has no usable original-title language for the
successful cast movies. Empty 2.6 actor lists indicate missing language
evidence; additional spoken-language metadata is needed to answer that
question conclusively.

A single preparation step can be re-run on its own by passing `profile`,
`clean` or `summary` as an argument (`clean` must run before `summary`).

Regression checks for the preparation step (real multi-value IMDb records):

```bash
docker compose exec spark python /home/jovyan/jobs/test_preparation.py
```

### Streaming

Needs the clean layer and the running containers. Two processes run at the
same time, so use two terminals, both from `project/`:

```bash
# Terminal 1 (host): forward Wikipedia edits to Kafka for 27 minutes
python scripts/wikipedia_producer.py --minutes 27

# Terminal 2: Spark Structured Streaming job, stops itself after 25 minutes
docker compose exec spark python /home/jovyan/jobs/40_streaming.py --minutes 25
```

The producer reads the public Wikimedia `recentchange` stream, keeps edits to
English Wikipedia articles and writes them to the Kafka topic
`wikipedia-edits`. The job matches the normalised page title (suffix such as
"(film)" removed, lower case) against IMDb titles with at least 10,000 votes
(`--min-votes` to change it) and the actors, actresses and directors credited
on them, using a stream-static join. A
10-minute watermark bounds how late an event may arrive and still be counted
in its 5-minute window. Start the job right after the producer: it reads only
new events unless `--from-beginning` is given. Checks without Kafka:

```bash
docker compose exec spark python /home/jovyan/jobs/test_streaming.py
```

The other steps (exploration, enrichment, open
question) are added to this table by their pull requests.

## Stopping

```bash
docker compose down
```

## Use of AI / LLM tools

- Claude Code (Anthropic, Claude Opus 5.5) was used to help write code: the
  Docker setup (`compose.yaml`), the IMDb download and ingestion scripts, and
  the shared Spark helpers (`jobs/common.py`), and the data-preparation job
  (`jobs/10_preparation.py`) and its checks (`jobs/test_preparation.py`),
  and the streaming pipeline (`scripts/wikipedia_producer.py`,
  `jobs/40_streaming.py`, `jobs/test_streaming.py`).
- An OpenAI coding assistant helped with PR review, setup verification, the
  contributor table, and implementation and validation of exploration
  questions 2.1–2.8 (`jobs/20_exploration_part1.py` and
  `jobs/21_exploration_part2.py`).
- All explanations and methodology in `REPORT.md` were written by the group
  members without AI.
