# ECE Big Data Processing – IMDb Project (Group 04)

## Contributors

| Name           | GitHub username | Email           |
| -------------- | --------------- | --------------- |
| Nils GIRAUD    | nilsgrd         | TODO@edu.ece.fr |
| Axel ALACACHE  | axou947         | TODO@edu.ece.fr |
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
  (Settings → Resources). The Spark container is capped at 6 GB with a 4 GB
  driver; lower `SPARK_DRIVER_MEMORY` in `project/compose.yaml` if needed.
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

The other steps (preparation, exploration, enrichment, streaming, open
question) are added to this table by their pull requests.

## Stopping

```bash
docker compose down
```

## Use of AI / LLM tools

- Claude Code (Anthropic, Claude Opus 5.5) was used to help write code: the
  Docker setup (`compose.yaml`), the IMDb download and ingestion scripts, and
  the shared Spark helpers (`jobs/common.py`).
- An OpenAI coding assistant helped with PR review, setup verification, and the contributor table.
- All explanations and methodology in `REPORT.md` were written by the group
  members without AI.
