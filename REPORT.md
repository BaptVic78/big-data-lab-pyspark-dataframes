# IMDb Project Report – Group 04

<!--
  Rule reminder: AI tools are NOT allowed for the explanations, reasoning and
  methodology in this file. Result tables may be copied from project/output/.
  Every "Methodological Explanation" must be written by a group member.
-->

## 1. Data preparation

### 1.1 Null / missing / empty values per column

Source: `project/output/1_1_null_profile`. `missing_token_N` counts IMDb's `\N` placeholder; `empty` counts empty or whitespace-only strings.

| table | column | total_rows | null | missing_token_N | empty | total_missing | pct_missing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| name_basics | birthYear | 15818137 | 0 | 15132142 | 0 | 15132142 | 95.66 |
| name_basics | deathYear | 15818137 | 0 | 15552559 | 0 | 15552559 | 98.32 |
| name_basics | knownForTitles | 15818137 | 0 | 1917637 | 0 | 1917637 | 12.12 |
| name_basics | nconst | 15818137 | 0 | 0 | 0 | 0 | 0.0 |
| name_basics | primaryName | 15818137 | 0 | 403 | 0 | 403 | 0.0 |
| name_basics | primaryProfession | 15818137 | 0 | 3220949 | 0 | 3220949 | 20.36 |
| title_akas | attributes | 60445719 | 0 | 60128411 | 0 | 60128411 | 99.48 |
| title_akas | isOriginalTitle | 60445719 | 0 | 0 | 0 | 0 | 0.0 |
| title_akas | language | 60445719 | 0 | 19671304 | 0 | 19671304 | 32.54 |
| title_akas | ordering | 60445719 | 0 | 0 | 0 | 0 | 0.0 |
| title_akas | region | 60445719 | 0 | 13005267 | 0 | 13005267 | 21.52 |
| title_akas | title | 60445719 | 0 | 0 | 0 | 0 | 0.0 |
| title_akas | titleId | 60445719 | 0 | 0 | 0 | 0 | 0.0 |
| title_akas | types | 60445719 | 0 | 40400487 | 0 | 40400487 | 66.84 |
| title_basics | endYear | 12965577 | 0 | 12801064 | 0 | 12801064 | 98.73 |
| title_basics | genres | 12965577 | 0 | 548263 | 0 | 548263 | 4.23 |
| title_basics | isAdult | 12965577 | 0 | 0 | 0 | 0 | 0.0 |
| title_basics | originalTitle | 12965577 | 0 | 0 | 0 | 0 | 0.0 |
| title_basics | primaryTitle | 12965577 | 0 | 0 | 0 | 0 | 0.0 |
| title_basics | runtimeMinutes | 12965577 | 0 | 8051768 | 0 | 8051768 | 62.1 |
| title_basics | startYear | 12965577 | 0 | 1487435 | 0 | 1487435 | 11.47 |
| title_basics | tconst | 12965577 | 0 | 0 | 0 | 0 | 0.0 |
| title_basics | titleType | 12965577 | 0 | 0 | 0 | 0 | 0.0 |
| title_crew | directors | 12963794 | 0 | 5793504 | 0 | 5793504 | 44.69 |
| title_crew | tconst | 12963794 | 0 | 0 | 0 | 0 | 0.0 |
| title_crew | writers | 12963794 | 0 | 6434529 | 0 | 6434529 | 49.63 |
| title_episode | episodeNumber | 10036861 | 0 | 2126414 | 0 | 2126414 | 21.19 |
| title_episode | parentTconst | 10036861 | 0 | 0 | 0 | 0 | 0.0 |
| title_episode | seasonNumber | 10036861 | 0 | 2126414 | 0 | 2126414 | 21.19 |
| title_episode | tconst | 10036861 | 0 | 0 | 0 | 0 | 0.0 |
| title_principals | category | 102774786 | 0 | 0 | 0 | 0 | 0.0 |
| title_principals | characters | 102774786 | 0 | 52701519 | 0 | 52701519 | 51.28 |
| title_principals | job | 102774786 | 0 | 82894365 | 0 | 82894365 | 80.66 |
| title_principals | nconst | 102774786 | 0 | 0 | 0 | 0 | 0.0 |
| title_principals | ordering | 102774786 | 0 | 0 | 0 | 0 | 0.0 |
| title_principals | tconst | 102774786 | 0 | 0 | 0 | 0 | 0.0 |
| title_ratings | averageRating | 1732558 | 0 | 0 | 0 | 0 | 0.0 |
| title_ratings | numVotes | 1732558 | 0 | 0 | 0 | 0 | 0.0 |
| title_ratings | tconst | 1732558 | 0 | 0 | 0 | 0 | 0.0 |

### 1.2 Top five columns by percentage of nulls

Source: `project/output/1_2_top5_null_columns`.

| table | column | total_rows | null | missing_token_N | empty | total_missing | pct_missing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| title_akas | attributes | 60445719 | 0 | 60128411 | 0 | 60128411 | 99.48 |
| title_basics | endYear | 12965577 | 0 | 12801064 | 0 | 12801064 | 98.73 |
| name_basics | deathYear | 15818137 | 0 | 15552559 | 0 | 15552559 | 98.32 |
| name_basics | birthYear | 15818137 | 0 | 15132142 | 0 | 15132142 | 95.66 |
| title_principals | job | 102774786 | 0 | 82894365 | 0 | 82894365 | 80.66 |

### 1.3 Other data quality issues

Source: `project/output/1_3_quality_issues`.

| table | issue | rows_affected | handling |
| --- | --- | --- | --- |
| title_basics | duplicate tconst | 0 | keep first row |
| title_basics | runtimeMinutes <= 0 | 4 | set to null |
| title_basics | runtimeMinutes > 10080 (1 week) | 19 | set to null |
| title_basics | startYear after 2026 (unreleased) | 6280 | kept |
| title_basics | endYear before startYear | 0 | endYear set to null |
| title_basics | startYear before 1874 (first film) | 0 | startYear set to null |
| name_basics | duplicate nconst | 0 | keep first row |
| name_basics | died before they were born | 28 | birthYear and deathYear set to null |
| name_basics | birthYear after 2026 | 0 | birthYear set to null |
| name_basics | deathYear after 2026 | 0 | deathYear set to null |
| name_basics | lifespan over 120 years | 2 | birthYear and deathYear set to null |
| name_basics | alive and older than 120 years | 2796 | kept |
| name_basics | knownForTitles id not in title_basics | 94 | id removed from the array |
| title_ratings | rating outside 1-10 or numVotes <= 0 | 0 | row removed |
| title_ratings | tconst not in title_basics | 0 | row removed |
| title_episode | tconst not in title_basics | 0 | row removed |
| title_episode | parentTconst not in title_basics | 6 | row removed |
| title_episode | parent is not a tvSeries / tvMiniSeries | 0 | kept |
| title_episode | missing season or episode number | 2126414 | kept |
| title_akas | titleId not in title_basics | 11 | row removed |
| title_crew | tconst not in title_basics | 10 | row removed |
| title_crew | directors id not in name_basics | 443 | id removed from the array |
| title_crew | writers id not in name_basics | 1163 | id removed from the array |
| title_principals | tconst not in title_basics | 0 | row removed |
| title_principals | nconst not in name_basics | 7476 | row removed |
| title_principals | person born after the title's release | 3099 | row removed (archive footage kept) |
| title_principals | person died 2+ years before the title's release | 257472 | kept |

### 1.4 Handling strategy

Row counts before and after cleaning (source: `project/output/1_4_row_counts`).

| table | rows_raw | rows_clean | rows_removed |
| --- | --- | --- | --- |
| name_basics | 15818137 | 15818137 | 0 |
| title_akas | 60445719 | 60445708 | 11 |
| title_basics | 12965577 | 12965577 | 0 |
| title_crew | 12963794 | 12963784 | 10 |
| title_episode | 10036861 | 10036855 | 6 |
| title_principals | 102774786 | 102764211 | 10575 |
| title_ratings | 1732558 | 1732558 | 0 |

### Methodological Explanation

**Profiling.** The raw TSV files are first copied to Parquet with every
column kept as a string, so that nothing is lost or silently converted before
we measure it. On this copy we count, for every column of the seven tables,
three kinds of missing value: real nulls, IMDb's `\N` placeholder, and empty
or whitespace-only strings. In practice everything missing is written as
`\N`. The five columns with the most missing values are optional by nature
(attributes of an alternative title, end year of a series, death and birth
year of a person, job of a principal), so a high percentage there describes
the data and is not an error.

**Typing.** Missing values of all three kinds become real nulls. Numbers are
converted with `try_cast`, which gives null instead of failing on a value
that is not a number. Booleans written 0 or 1 become true or false. Lists
become arrays: genres, professions, directors, writers and known-for titles
are separated by commas, while `types` and `attributes` in `title_akas` are
separated by the control character `\x02`, which was found by inspecting
real multi-value records during the review.

**Handling rules.** We applied three rules, chosen to lose as little data as
possible.

- A value that cannot be true is set to null and the row is kept: a runtime
  of zero or of more than one week, a death year before the birth year, a
  lifespan over 120 years, an end year before the start year. The rest of
  the row is still usable.
- A row whose foreign key points to a missing parent is removed from the
  child table (for example a principal whose person is not in
  `name_basics`), and a missing id inside an array is removed from the
  array. Every join on the clean layer then finds its parent.
- A value that is unusual but possible is kept: titles announced for a
  future year, people with a birth year and no death year who would be over
  120, episodes without a season number, and people who died two or more
  years before a title's release.

A principal born after the release of the title is also removed, except for
archive credits. The effect on volume is small: 10,602 rows removed out of
about 217 million, of which 10,575 are in `title_principals`.

**Alternatives and trade-offs.** Dropping every row with an impossible value
would have been simpler but would remove titles and people that are valid
apart from one field. Keeping orphan rows would preserve every raw row but
would force each later job to handle missing parents. The thresholds (one
week of runtime, 120 years, 1874 as the first film) are deliberately wide:
they catch encoding errors without removing real extreme cases.

**Running at full scale.** The job runs on the full dataset on a laptop, in
a 6 GB container. The first version failed on a teammate's machine with
`Cannot allocate memory`: Parquet reads allocate large off-heap buffers that
Java caches per thread. We limited the cached buffer size, capped off-heap
memory at 1.5 GB, set the heap to 3 GB and used 4 parallel tasks instead of
all cores. The full run then takes about 31 minutes.

## 2. Data exploration

### 2.1 Movies with a runtime notably different from their genre average

### 2.2 Top three genres per year (1980–2025)

### 2.3 Top three genres compared to the other genres

### 2.4 Directors with exactly one movie rated ≥ 8.0 and others averaging ≤ 6.0

### 2.5 TV series: worst episode in the last season, best in the first two

### 2.6 Actors successful in multiple languages

### 2.7 Long careers that peaked early

### 2.8 Multi-talented professionals

### Methodological Explanation

## 3. Data enrichment

### 3.1 Selection and collection coverage

The target selection and enrichment pipeline ran on the full clean IMDb
dataset. The Wikipedia collection is **incomplete**: only **1 of 8,214
selected films** currently has both a synopsis and three principal biographies.
The other films must not be treated as successfully enriched.

Sources: `project/output/3_selected_films`, `3_requests`,
`3_coverage` and `3_coverage_summary`, generated on 15 November 2026.

| Measure | Result |
| --- | ---: |
| Release years | 1980–2025 |
| Genre/year groups with eligible films | 1,074 |
| Film/genre/year selections | 10,199 |
| Distinct selected films | 8,214 |
| Distinct principal candidates | 58,439 |
| Unique film and person retrieval requests | 66,653 |
| Films with a synopsis and three biographies | 1 |
| Films still incomplete | 8,213 |
| Available film/biography links, capped at three per film | 30 |

A film can appear in several genres, so 10,199 selections do not represent
10,199 different films. A biography can also be reused for a person credited
on several films: the 30 links are not 30 different people.

### 3.2 Verified example

*The Shawshank Redemption* (`tt0111161`, 1994) has a verified plot section
and biographies for its first three selected principals. The source pages
were matched to the exact IMDb identifiers through Wikidata. The links below
identify the retrieved Wikipedia revisions.

| Record | IMDb ID | Source revision |
| --- | --- | --- |
| Film synopsis | tt0111161 | [The Shawshank Redemption](https://en.wikipedia.org/w/index.php?oldid=1385870872) |
| Tim Robbins | nm0000209 | [Biography](https://en.wikipedia.org/w/index.php?oldid=1384219365) |
| Morgan Freeman | nm0000151 | [Biography](https://en.wikipedia.org/w/index.php?oldid=1384898723) |
| Bob Gunton | nm0348409 | [Biography](https://en.wikipedia.org/w/index.php?oldid=1362769678) |

The retrieved text, source URLs, revision URLs, collection timestamps and
license URLs are stored in `project/data/enrichment/wikipedia/` and exported
through `project/output/3_film_synopses` and `3_principal_biographies`.
The cache and full exports are generated locally and are not committed.

### 3.3 Remaining work

The full request list still needs to be collected. Pending requests are
labelled `not_fetched`; they are not evidence that a Wikipedia page is absent.
The pipeline separately records unverified matches, missing plot sections
and request errors. It can resume from its cache, then regenerate coverage
without repeating successful requests. The current example validates the
complete retrieval/join workflow but does not establish full coverage.

### Methodological Explanation

`30_enrichment.py prepare` selects feature films (`titleType = movie`,
runtime greater than 40 minutes) released between 1980 and 2025 with an IMDb
rating and at least one vote. Within each genre/year group, films are ordered
by rating, then number of votes, then IMDb ID. Up to ten films are retained.
There is no additional popularity floor, so a highly rated film with few
votes can be selected. These ratings and vote counts describe the downloaded
snapshot, not their values at the time of release.

Principal credits are deduplicated per film/person and ordered by their IMDb
credit ordering. Up to ten candidates per film provide alternatives when a
biography is unavailable. This uses principal credits rather than a complete
cast list. The final export retains the first three successful biographies.

The host fetcher retrieves English Wikipedia prose only after an exact
Wikidata P345/IMDb match. A film's Plot, Synopsis or Plot summary section is
used for its synopsis; a person's page introduction is used for a biography.
An unrelated search result or a film introduction without a plot section is
not accepted as a successful synopsis. Requests are sequential, at least one
second apart, with a descriptive User-Agent, `maxlag`, retries and backoff.
Each entity has an atomic JSON cache record with its source lineage.

Text normalization and joins are performed in Spark during `finalize`.
Coverage is counted once per distinct selected film. Completion requires a
successful synopsis and at least three distinct principal biographies.
Missing text is kept separate from successful retrievals. English Wikipedia
coverage and exact identifier availability limit what can be collected.

## 4. Streaming data processing

### 4.1 Results and metrics

The filter kept 75 of about 2,190 edits (3.4 %) and matched 53 different
IMDb titles and people, with 15 to 20 matches in every full five-minute
window. It therefore captures several events well within the required 15 to
30 minutes. Titles account for about two thirds of the matches. Most
entities are edited once; the most edited one, *Titanic*, received four
edits.

**Run metrics** (source: producer and job logs, `project/output/4_matched_edits`).

| Metric | Value |
| --- | --- |
| Stream duration | 25 minutes |
| Wikimedia `recentchange` events read by the producer | about 60,000 |
| Edits sent to Kafka (English Wikipedia articles) | about 2,190 |
| IMDb entities in the match table | 82,674 |
| Matched edits | 75 |
| Matched edits on titles | 48 |
| Matched edits on people | 27 |
| Distinct IMDb entities matched | 53 (31 titles, 22 people) |
| Share of Kafka edits that matched | about 3.4 % |
| Matched edits per full 5-minute window | 15 to 20 |

**Pipeline parameters** (source: `project/scripts/wikipedia_producer.py`, `project/jobs/40_streaming.py`).

| Parameter | Value |
| --- | --- |
| Source | Wikimedia EventStreams, `recentchange` (Server-Sent Events) |
| Producer filter | wiki `enwiki`, type `edit` or `new`, namespace 0 (articles) |
| Kafka topic | `wikipedia-edits`, key = page title, value = JSON |
| IMDb titles matched | `movie`, `tvSeries`, `tvMiniSeries` with at least 10,000 votes |
| IMDb people matched | actors, actresses and directors credited on one of those titles |
| Match key | page title without its trailing parenthesis, lower case |
| Name shared by several entities | one entity kept: title before person, then most votes, then smallest id |
| Join | stream-static inner join, entity table broadcast |
| Event time | `timestamp` field of the edit |
| Watermark | 10 minutes |
| Window | 5 minutes, tumbling |
| Trigger | every 30 seconds |
| Sinks | matched edits to Parquet (append); window counts stored at every update |

**Matched edits per IMDb entity** (source: `project/output/4_matched_edits`).

| entity_type | label | imdb_id | edits | first_edit | last_edit |
| --- | --- | --- | --- | --- | --- |
| title | Titanic | tt0120338 | 4 | 18:27:57 | 18:35:15 |
| person | Bhagyashri Borse | nm15134235 | 3 | 18:32:55 | 18:35:12 |
| title | D.P. | tt13024974 | 3 | 18:21:52 | 18:32:13 |
| title | Diego Maradona | tt5433114 | 3 | 18:29:11 | 18:32:38 |
| person | Quinn Shephard | nm0791723 | 3 | 18:22:47 | 18:26:30 |
| title | Ramayana | tt27988879 | 3 | 18:30:40 | 18:32:25 |
| title | After | tt4126476 | 2 | 18:21:21 | 18:25:10 |
| title | After Hours | tt0088680 | 2 | 18:25:45 | 18:27:23 |
| title | Crystal Lake | tt23148340 | 2 | 18:18:47 | 18:20:30 |
| title | Fashion | tt0964516 | 2 | 18:23:28 | 18:24:43 |
| title | Hamlet | tt0116477 | 2 | 18:15:26 | 18:24:38 |
| title | House of Guinness | tt13542714 | 2 | 18:28:22 | 18:29:40 |
| title | Madagascar | tt0351283 | 2 | 18:34:58 | 18:35:33 |
| title | Running Scared | tt0404390 | 2 | 18:33:48 | 18:34:03 |
| person | Sam Heughan | nm1537825 | 2 | 18:25:48 | 18:26:54 |
| person | Adrian Maben | nm0531066 | 1 | 18:16:05 | 18:16:05 |
| title | Alone in the Dark | tt0369226 | 1 | 18:32:34 | 18:32:34 |
| title | Bee Movie | tt0389790 | 1 | 18:19:47 | 18:19:47 |
| person | Billy Joel | nm0005055 | 1 | 18:21:21 | 18:21:21 |
| person | Binu Pappu | nm8527632 | 1 | 18:13:49 | 18:13:49 |
| person | Bruce Bennett | nm0071636 | 1 | 18:34:51 | 18:34:51 |
| title | Burning | tt7282468 | 1 | 18:12:17 | 18:12:17 |
| title | Fantastic Beasts: The Secrets of Dumbledore | tt4123432 | 1 | 18:18:29 | 18:18:29 |
| title | Four Lions | tt1341167 | 1 | 18:18:08 | 18:18:08 |
| person | Gerald McRaney | nm0574468 | 1 | 18:19:16 | 18:19:16 |
| title | Good Boy | tt35521922 | 1 | 18:33:17 | 18:33:17 |
| title | GoodFellas | tt0099685 | 1 | 18:27:56 | 18:27:56 |
| person | Haruka Tomatsu | nm2955927 | 1 | 18:25:54 | 18:25:54 |
| title | Heartland | tt1094229 | 1 | 18:22:28 | 18:22:28 |
| title | I Can't Think Straight | tt0830570 | 1 | 18:19:57 | 18:19:57 |
| person | Indrans | nm1428724 | 1 | 18:17:34 | 18:17:34 |
| person | Jeff Bennett | nm0071818 | 1 | 18:15:05 | 18:15:05 |
| title | Joji | tt13206926 | 1 | 18:15:03 | 18:15:03 |
| person | Kate Mara | nm0544718 | 1 | 18:23:24 | 18:23:24 |
| person | Michael Jordan | nm0003044 | 1 | 18:22:15 | 18:22:15 |
| person | Michel Hazanavicius | nm0371890 | 1 | 18:19:20 | 18:19:20 |
| person | Moushumi Chatterjee | nm0154139 | 1 | 18:32:13 | 18:32:13 |
| title | Parasite | tt6751668 | 1 | 18:18:52 | 18:18:52 |
| person | Robert Kerman | nm0449404 | 1 | 18:34:45 | 18:34:45 |
| person | Rooney Mara | nm1913734 | 1 | 18:22:09 | 18:22:09 |
| person | Sam Riley | nm0727165 | 1 | 18:21:49 | 18:21:49 |
| person | Taika Waititi | nm0169806 | 1 | 18:26:32 | 18:26:32 |
| title | The Cat in the Hat | tt0312528 | 1 | 18:15:29 | 18:15:29 |
| title | The Dark Tower | tt1648190 | 1 | 18:34:13 | 18:34:13 |
| title | The Fool | tt3560686 | 1 | 18:27:13 | 18:27:13 |
| title | The Lives of Others | tt0405094 | 1 | 18:31:41 | 18:31:41 |
| title | The Shawshank Redemption | tt0111161 | 1 | 18:28:07 | 18:28:07 |
| title | The Ten Commandments | tt0049833 | 1 | 18:19:36 | 18:19:36 |
| title | The Town | tt0840361 | 1 | 18:35:59 | 18:35:59 |
| person | Toby Jones | nm0429363 | 1 | 18:34:08 | 18:34:08 |
| person | Tom O'Brien | nm0639856 | 1 | 18:26:53 | 18:26:53 |
| title | Turbo | tt1860353 | 1 | 18:29:10 | 18:29:10 |
| person | Yumi Hara | nm3782945 | 1 | 18:25:43 | 18:25:43 |

### 4.2 Late-arriving data

Late data is handled with a 10-minute watermark on the edit's own timestamp.
Spark keeps a five-minute window open until the newest event time it has
seen is more than 10 minutes past the end of that window; an edit arriving
after that is not added to the count. During the live run no edit arrived
that late, so the streaming counts equal the counts over all stored edits.
The controlled test below shows the other case: an edit sent 29 minutes
late is stored, but it is not counted in its window.

**Counts per window** (source: `project/output/4_edits_per_window`).
`edits_streaming` is the last count emitted by the watermarked window query,
`edits_all` counts every matched edit stored in Parquet (written before the
watermark), and `late_not_counted` is the difference.

| window_start | window_end | entity_type | edits_streaming | edits_all | late_not_counted |
| --- | --- | --- | --- | --- | --- |
| 18:10:00 | 18:15:00 | person | 1 | 1 | 0 |
| 18:10:00 | 18:15:00 | title | 1 | 1 | 0 |
| 18:15:00 | 18:20:00 | person | 5 | 5 | 0 |
| 18:15:00 | 18:20:00 | title | 10 | 10 | 0 |
| 18:20:00 | 18:25:00 | person | 7 | 7 | 0 |
| 18:20:00 | 18:25:00 | title | 8 | 8 | 0 |
| 18:25:00 | 18:30:00 | person | 7 | 7 | 0 |
| 18:25:00 | 18:30:00 | title | 13 | 13 | 0 |
| 18:30:00 | 18:35:00 | person | 6 | 6 | 0 |
| 18:30:00 | 18:35:00 | title | 13 | 13 | 0 |
| 18:35:00 | 18:40:00 | person | 1 | 1 | 0 |
| 18:35:00 | 18:40:00 | title | 3 | 3 | 0 |

Total over the run: 75 edits counted by the stream, 75 stored, 0 late edits
not counted.

**Controlled late event** (source: `check_late_event_dropped` in
`project/jobs/test_streaming.py`). Three edits of the same page are sent in
three micro-batches: at T, at T + 30 min, then at T + 1 min.

| window | edits_streaming | edits_all | late_not_counted |
| --- | --- | --- | --- |
| T to T + 5 min | 1 | 2 | 1 |
| T + 30 to T + 35 min | 1 | 1 | 0 |

### Methodological Explanation

**Pipeline.** A producer on the host reads the public Wikimedia
`recentchange` stream and forwards the edits of English Wikipedia articles
to a Kafka topic. Filtering there removes about 96 % of the events before
Kafka, since other wikis and non-article pages cannot match an IMDb name. A
Spark Structured Streaming job reads the topic, parses the JSON with a fixed
schema and joins each edit with a table of IMDb entities.

**Matching.** An edit carries a page title and no IMDb identifier, so we
match on the name: the page title without its final parenthesis, in lower
case, against IMDb titles with at least 10,000 votes and the actors,
actresses and directors credited on them. When several entities share a
name we keep one (a title before a person, then the most votes), so one
edit gives at most one match. The IMDb table does not change during the
run, so a stream-static join with a broadcast table is enough and the join
itself needs no state.

**Alternatives and trade-offs.**

- Matching through Wikidata, which stores the IMDb id of a page, would be
  exact. It needs one more dataset or one API call per edit, which we could
  not fit in the time available. Name matching is simple but produces false
  positives: the pages "Fashion" or "Madagascar" match films of that name.
- The 10,000-vote threshold trades recall for precision and for memory. Our
  first version matched every person "known for" a popular title, about
  1.3 million entities. It matched more edits, many of them wrong, and a
  later run failed with an out-of-memory error after about nine minutes.
  The table now has 82,674 rows.
- A longer watermark would accept later edits but keep window state in
  memory for longer. Ten minutes is a margin we chose, not a measured
  value; in our run nothing arrived that late.
- Counting each edit once required a review fix: a name shared by a title
  and a person first produced two rows for one edit.

**Limits.** The window counts are final only once the watermark has passed
the window, so the last window of a run is partial. Stopping the job cancels
the micro-batch in progress. Each run starts from a clean checkpoint.

## 5. Open question

### 5.1 Question and motivation

**Do recurring director–actor pairs receive higher IMDb ratings than each
person receives on films outside that pair?** Comparing a pair with each
member's own other films gives two personal reference points instead of
comparing only with the overall movie average.

### 5.2 Results

In the selected sample, **1,257 of 2,470 eligible pairs (50.89%)** have a
strictly higher mean rating than both reference groups. This is a small
majority, not a general rule that repeated collaborations perform better.

Sources: `project/output/5_parameters`, `5_pair_summary`,
`5_pair_comparison` and `5_shared_movies`. The corrected full-data run on
15 November 2026 completed in 136 seconds on Spark 4.2.0.

| Sample or eligibility rule | Value |
| --- | ---: |
| Release years | 1980–2025 |
| Minimum IMDb votes per film | 1,000 |
| Eligible rated feature films | 40,061 |
| Minimum shared films per pair | 3 |
| Minimum outside-pair films for each person | 3 |
| Eligible director–actor pairs | 2,470 |
| Pair/film evidence rows | 9,273 |

Each film has equal weight within a pair's or person's mean. Each pair has
equal weight in the following summary. Differences are rating points on the
IMDb 1–10 scale, not percentage changes.

| Shared-film mean minus outside-pair mean | Mean across pairs | Median across pairs |
| --- | ---: | ---: |
| Director's other films | +0.196 | +0.197 |
| Actor's other films | +0.265 | +0.292 |

The three categories below are mutually exclusive. A tie does not count as
an improvement.

| Pair's mean rating is strictly higher than | Pairs | Share |
| --- | ---: | ---: |
| Both personal reference groups | 1,257 | 50.89% |
| Exactly one personal reference group | 738 | 29.88% |
| Neither personal reference group | 475 | 19.23% |
| Total | 2,470 | 100.00% |

The five eligible pairs with the most shared films illustrate the different
outcomes. These counts concern qualifying films in this sample, not complete
career collaboration counts. Ties in frequency use director and actor IDs.

| Director | Actor | Shared films | Shared mean | Difference vs director's others | Difference vs actor's others |
| --- | --- | ---: | ---: | ---: | ---: |
| Kartal Tibet | Kemal Sunal | 23 | 6.791 | +1.948 | -0.109 |
| Johnnie To | Suet Lam | 20 | 6.775 | +0.116 | +0.923 |
| David Dhawan | Govinda | 16 | 6.000 | +0.982 | +0.376 |
| Kunihiko Yuyama | Ikue Otani | 16 | 5.975 | +0.008 | -0.825 |
| Priyadarshan | Mohanlal | 15 | 7.513 | +0.822 | +0.612 |

### 5.3 Key takeaways

The average differences are positive against both personal reference groups,
but 1,213 pairs do not exceed both. A pair can improve on the director's other
films while remaining below the actor's other films, as the first example
shows. The two comparisons therefore answer different parts of the question.

These results describe an association. Successful films may encourage people
to work together again, and genre, release year, franchises or other factors
may affect both collaboration and ratings. None of those effects is isolated
here. The vote threshold also excludes less widely rated films, while acting
credits cover IMDb principals rather than every cast member. Repeated people
and films make pairs overlap, so the observations are not independent.

### Methodological Explanation

`50_open_question.py` joins feature-film titles, ratings, acting principals,
director crew arrays and names. Eligible films run over 40 minutes, were
released in 1980–2025 and have at least 1,000 votes in the downloaded snapshot.
Unrated films and films below the vote threshold are excluded from both
shared-film and outside-pair calculations.

Actor and actress categories are combined. Each actor/film and director/film
credit is counted once, including repeated IDs in crew arrays. Co-directed
films contribute to each credited director; actor/director self-pairs are
excluded. A pair needs at least three shared qualifying films, and each member
needs at least three other qualifying films in the same population.

For each pair, all shared films are removed from both personal reference
groups. Absence of a matching principal credit is interpreted within these
tables, not as proof that a person never appeared in the full cast. The two
differences are `shared mean - director's outside-pair mean` and
`shared mean - actor's outside-pair mean`. Differences are rounded to ten
decimal places before testing whether both are positive. This removes
floating-point noise that otherwise incorrectly classified three rating ties
as improvements in the initial run.

The aggregate means and medians describe pair-level differences. They do not
pool all films into one shared-film score, and the 9,273 evidence rows are
pair/film observations rather than 9,273 distinct films. Regression checks
cover duplicate credits, self-pairs, year/vote boundaries, insufficient
reference groups, fractional-rating ties and empty outputs. Independent CSV
checks reconcile pair counts, rating differences and shared-film evidence.
