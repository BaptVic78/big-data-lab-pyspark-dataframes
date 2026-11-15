# Enrichment

Run the three enrichment steps in the `PROJECT.md` table in order, from `project/`.
The prepare step selects the ten highest-rated feature films per genre and
year from 1980 through 2025. Ties use total IMDb votes, then IMDb ID.
All rated films are eligible by default (`--min-votes 1`); use a higher
threshold explicitly if desired. A film may belong to several rankings.
Its text is fetched only once. Up to ten distinct principals per film are
selected by IMDb credit ordering, leaving alternatives if a biography is
unavailable. Increase `--principal-candidates` to consider more people.

The host fetcher uses the English Wikipedia Action API and verifies each
candidate against its exact IMDb ID in Wikidata property P345. Film text
comes from a Plot, Synopsis or Plot summary section; biographies come from
the introduction of the person's page. Text is retrieved from the source,
not generated. Normalization and joins run in Spark. Each retrieved record
keeps its source URL, revision URL, Wikidata URL, timestamp and license URL.
Source revisions provide attribution to the Wikipedia page history.

Requests are sequential, at least one second apart, with a descriptive
User-Agent, `maxlag`, retries and backoff for temporary failures. JSON files
are cached by IMDb ID and replaced atomically. Rerunning the fetcher reuses
the cache. `--limit 20` bounds a trial run; `--retry-missing` retries missing
matches or sections. Temporary request errors are retried on the next run.
Full collection can take many hours and is separate from Spark processing.

The finalize step exports synopses, up to three successful biographies per
film, every principal's source status, and film-level coverage. A film is
complete only when its synopsis and at least three biographies are available.
Missing pages, missing plot sections, unverified matches and pending fetches
remain explicit. Run finalize again after each fetch batch. A partial
collection must not be presented as complete enrichment. Outputs and source
text stay in the ignored `data/` and `output/` directories.

Checks:

```bash
python scripts/test_fetch_wikipedia.py
docker compose exec spark python /home/jovyan/jobs/test_enrichment.py
```

API references: [MediaWiki etiquette](https://www.mediawiki.org/wiki/API:Etiquette),
[text extraction](https://www.mediawiki.org/wiki/Extension:TextExtracts),
and [Wikidata IMDb identifiers](https://www.wikidata.org/wiki/Property:P345).
