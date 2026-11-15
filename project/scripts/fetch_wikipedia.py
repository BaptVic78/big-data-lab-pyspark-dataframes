"""Fetch human-written Wikipedia text for Spark-selected IMDb entities.

The host only retrieves text. Ranking, normalization and joins run in Spark.
Wikipedia search results are accepted only after Wikidata P345 matches the
requested IMDb ID exactly. Each cache record includes source and revision
URLs. Existing results are reused; interrupted runs can be resumed.
"""
import argparse
import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = ("ECE-Group04-IMDb/1.0 "
              "(https://github.com/BaptVic78/big-data-lab-pyspark-dataframes)")
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"


class Client:
    def __init__(self, interval=1.0, retries=4):
        self.interval = interval
        self.retries = retries
        self.last_request = 0.0

    def get(self, endpoint, params):
        params = dict(params, format="json", formatversion=2, maxlag=5)
        url = endpoint + "?" + urllib.parse.urlencode(params)
        for attempt in range(self.retries + 1):
            delay = self.interval - (time.monotonic() - self.last_request)
            if delay > 0:
                time.sleep(delay)
            request = urllib.request.Request(url, headers={
                "User-Agent": USER_AGENT, "Accept": "application/json"})
            self.last_request = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    data = json.load(response)
                if "error" in data:
                    error = data["error"]
                    if error.get("code") in {"maxlag", "ratelimited", "readonly"}:
                        raise urllib.error.HTTPError(
                            url, 503, error.get("info", "API unavailable"), {}, None)
                    raise ValueError("MediaWiki API: " + str(error))
                return data
            except urllib.error.HTTPError as error:
                if error.code not in {429, 500, 502, 503, 504} or attempt == self.retries:
                    raise
                retry_after = error.headers.get("Retry-After", "")
                delay = retry_delay(retry_after, attempt)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                if attempt == self.retries:
                    raise
                delay = 2 ** attempt
            time.sleep(delay)
        raise RuntimeError("request retry limit exceeded")


def retry_delay(value, attempt):
    try:
        wait = float(value)
    except ValueError:
        try:
            wait = (parsedate_to_datetime(value)
                    - datetime.now(timezone.utc)).total_seconds()
        except (TypeError, ValueError, OverflowError):
            wait = 0
    return max(2 ** attempt, wait)


def has_imdb_id(entity, imdb_id):
    return any(
        claim.get("rank") != "deprecated"
        and claim.get("mainsnak", {}).get("datavalue", {}).get("value") == imdb_id
        for claim in entity.get("claims", {}).get("P345", [])
    )


def plot_text(extract):
    # Preserve raw prose. Whitespace cleanup belongs to the Spark finalize step.
    headings = list(re.finditer(r"(?m)^==\s*([^=\n]+?)\s*==\s*$", extract))
    for index, heading in enumerate(headings):
        if heading.group(1).strip().lower() in {"plot", "synopsis", "plot summary"}:
            end = headings[index + 1].start() if index + 1 < len(headings) else len(extract)
            return extract[heading.end():end], heading.group(1).strip()
    return "", ""


def fetch_one(row, client):
    record = dict(entity_id=row["entity_id"], kind=row["kind"],
                  label=row["label"], status="no_verified_match", note="",
                  text=None, source_url=None, revision_url=None,
                  wikidata_url=None, section=None, revision_id=None,
                  license_url=LICENSE_URL,
                  fetched_at=datetime.now(timezone.utc).isoformat())
    label = row["label"].replace('"', ' ')
    query = f'"{label}"'
    if row["kind"] == "film":
        query += f' {row.get("year", "")} film'
    results = client.get(WIKIPEDIA_API, {
        "action": "query", "list": "search", "srsearch": query,
        "srnamespace": 0, "srlimit": 5,
    }).get("query", {}).get("search", [])
    if not results:
        record["note"] = "No English Wikipedia search result."
        return record
    pages = client.get(WIKIPEDIA_API, {
        "action": "query", "prop": "pageprops", "redirects": 1,
        "pageids": "|".join(str(r["pageid"]) for r in results),
    }).get("query", {}).get("pages", [])
    candidates = {p.get("pageprops", {}).get("wikibase_item"): p
                  for p in pages if "disambiguation" not in p.get("pageprops", {})
                  and p.get("pageprops", {}).get("wikibase_item")}
    if not candidates:
        record["note"] = "Search results have no usable Wikidata identifier."
        return record
    entities = client.get(WIKIDATA_API, {
        "action": "wbgetentities", "ids": "|".join(candidates), "props": "claims",
    }).get("entities", {})
    matches = [(qid, candidates[qid]) for qid, entity in entities.items()
               if qid in candidates and has_imdb_id(entity, row["entity_id"])]
    if len(matches) != 1:
        record["note"] = "No unique search result with the exact Wikidata IMDb ID."
        return record
    qid, match = matches[0]
    pages = client.get(WIKIPEDIA_API, {
        "action": "query", "pageids": match["pageid"],
        "prop": "extracts|info|revisions", "inprop": "url", "explaintext": 1,
        "rvprop": "ids", "rvlimit": 1,
    }).get("query", {}).get("pages", [])
    page = next((p for p in pages if p.get("pageid") == match["pageid"]), {})
    extract = page.get("extract", "")
    revisions = page.get("revisions", [])
    revision = revisions[0].get("revid") if revisions else None
    record.update(source_url=page.get("fullurl"),
                  revision_url=(f"https://en.wikipedia.org/w/index.php?oldid={revision}"
                                if revision else None),
                  revision_id=str(revision) if revision else None,
                  wikidata_url="https://www.wikidata.org/wiki/" + qid)
    if row["kind"] == "film":
        text, section = plot_text(extract)
        record.update(text=text or None, section=section or None,
                      status="ok" if text.strip() else "missing_plot",
                      note=("" if text.strip()
                            else "Verified page has no plot or synopsis section."))
    else:
        intro = re.split(r"(?m)^==", extract, maxsplit=1)[0]
        record.update(text=intro or None, section="introduction",
                      status="ok" if intro.strip() else "missing_biography",
                      note="" if intro.strip() else "Verified page has no biography introduction.")
    if record["status"] == "ok" and (not record["source_url"] or not revision):
        record.update(status="missing_source", note="No source URL or revision ID returned.")
    return record


def request_rows(path):
    files = [path] if path.is_file() else sorted(path.glob("part-*.csv"))
    if not files:
        raise ValueError(f"No request CSV found at {path}; run the Spark prepare step.")
    seen = set()
    for file in files:
        with file.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                entity_id = row.get("entity_id", "")
                if not re.fullmatch(r"(?:tt|nm)\d+", entity_id):
                    raise ValueError("Invalid IMDb identifier in request CSV")
                if row.get("kind") not in {"film", "person"}:
                    raise ValueError("Invalid entity kind")
                if entity_id not in seen:
                    seen.add(entity_id)
                    yield row


def write_record(path, record):
    partial = path.with_suffix(".json.part")
    partial.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8")
    partial.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=Path, default=ROOT / "output" / "3_requests")
    parser.add_argument("--cache", type=Path,
                        default=ROOT / "data" / "enrichment" / "wikipedia")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--limit", type=int, help="maximum new entities for this run")
    parser.add_argument("--retry-missing", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.interval < float("inf"):
        parser.error("--interval must be finite and at least one second")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    args.cache.mkdir(parents=True, exist_ok=True)
    client = Client(args.interval)
    fetched = skipped = 0
    for row in request_rows(args.requests):
        path = args.cache / (row["entity_id"] + ".json")
        if path.exists():
            old = json.loads(path.read_text(encoding="utf-8"))
            if old.get("status") == "ok" or (
                old.get("status") != "request_error" and not args.retry_missing
            ):
                skipped += 1
                continue
        try:
            record = fetch_one(row, client)
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            record = dict(entity_id=row["entity_id"], kind=row["kind"],
                          label=row["label"], status="request_error", note=str(error),
                          fetched_at=datetime.now(timezone.utc).isoformat())
        write_record(path, record)
        fetched += 1
        print(f'{row["entity_id"]}: {record["status"]}', flush=True)
        if args.limit is not None and fetched >= args.limit:
            break
    print(f"finished: {fetched} fetched, {skipped} cached", flush=True)


if __name__ == "__main__":
    main()
