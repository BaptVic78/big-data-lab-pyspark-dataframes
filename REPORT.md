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

### 4.2 Late-arriving data

### Methodological Explanation

## 5. Open question

### 5.1 Question and motivation

### 5.2 Results

### 5.3 Key takeaways

### Methodological Explanation
