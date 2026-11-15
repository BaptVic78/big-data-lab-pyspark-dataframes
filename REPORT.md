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

<!-- TODO (Axel): write this section yourself, without AI. -->

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

### Methodological Explanation

## 4. Streaming data processing

### 4.1 Results and metrics

<!-- TODO (Axel): add your own description and comments, without AI. -->

Run of 15 November 2026, 18:12–18:37 UTC (25 minutes), commands in
`PROJECT.md`. All times below are UTC.

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

<!-- TODO (Axel): add your own description and comments, without AI. -->

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

<!-- TODO (Axel): write this section yourself, without AI. -->

## 5. Open question

### 5.1 Question and motivation

### 5.2 Results

### 5.3 Key takeaways

### Methodological Explanation
