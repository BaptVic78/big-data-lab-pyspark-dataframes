"""Download the IMDb non-commercial datasets into project/data/raw.

Usage (from the project directory):
    python scripts/download_imdb.py

Files that already exist with the same size as on the server are skipped,
so the script can be safely re-run.
"""
import sys
import urllib.request
from pathlib import Path

BASE_URL = "https://datasets.imdbws.com/"
FILES = [
    "name.basics.tsv.gz",
    "title.akas.tsv.gz",
    "title.basics.tsv.gz",
    "title.crew.tsv.gz",
    "title.episode.tsv.gz",
    "title.principals.tsv.gz",
    "title.ratings.tsv.gz",
]
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def remote_size(url):
    """Return the Content-Length of a remote file, or None."""
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request) as response:
        length = response.headers.get("Content-Length")
    return int(length) if length else None


def download(name):
    """Download one dataset file unless an identical copy is present."""
    url = BASE_URL + name
    target = RAW_DIR / name
    size = remote_size(url)
    if target.exists() and size is not None and target.stat().st_size == size:
        print(f"[skip] {name} already downloaded")
        return
    print(f"[get ] {name} ({(size or 0) / 1e6:.0f} MB)")
    partial = target.with_suffix(target.suffix + ".part")
    urllib.request.urlretrieve(url, partial)
    partial.replace(target)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        download(name)
    print("Done:", RAW_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
