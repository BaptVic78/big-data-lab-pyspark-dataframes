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

<!-- AI-assisted working draft. The course requires the final explanations and methodology to be written personally without AI. Review and replace this prose before submission. -->

These results use the local clean IMDb data. The tables below show all years for the genre questions and selected examples for the larger results. Ratings are out of 10.

### 2.1 Movies with a runtime notably different from their genre average

A feature film is a movie longer than 40 minutes. A film is unusual here when its duration is more than two standard deviations away from the average of its genre. A film can appear in several genres.

The query returned **14,601 film/genre pairs**, covering **10,611 different films**. The table shows the largest absolute deviation in five selected genres.

| Film | Year | Genre | Minutes | Genre average | Z-score |
| --- | --- | --- | --- | --- | --- |
| h36: | 2017 | Action | 2160 | 101.2 | 61.00 |
| London EC1 | 2015 | Comedy | 5460 | 93.1 | 187.08 |
| Hunger! | 2015 | Drama | 6000 | 96.1 | 159.38 |
| 24 Hour Psycho | 1993 | Horror | 1440 | 88.6 | 60.63 |
| Funusion | 2016 | Sci-Fi | 1440 | 91.2 | 44.34 |

Some durations are extremely long. These records need care when interpreting the result. The preparation step kept durations up to one week, so these large values still affect the genre average and standard deviation.

Full output in `project/output/2_1_runtime_outliers`.

### 2.2 Top three genres per year (1980–2025)

Popularity is measured by the total number of IMDb votes on rated movies released in each year. These are the votes in the dataset at download time, rather than votes collected only during the release year. Each movie contributes its votes to every listed genre. Equal totals are ordered by genre name.

| Year | First genre (votes) | Second genre (votes) | Third genre (votes) |
| --- | --- | --- | --- |
| 1980 | Drama (3,169,854) | Adventure (2,484,046) | Horror (2,075,877) |
| 1981 | Adventure (2,252,476) | Drama (1,715,724) | Horror (1,277,939) |
| 1982 | Drama (3,078,847) | Sci-Fi (2,460,442) | Action (1,876,156) |
| 1983 | Drama (2,928,737) | Action (2,027,094) | Adventure (1,986,092) |
| 1984 | Action (3,671,883) | Drama (3,031,248) | Adventure (2,934,263) |
| 1985 | Comedy (4,572,084) | Adventure (3,414,163) | Drama (3,083,881) |
| 1986 | Drama (4,007,820) | Adventure (2,968,190) | Comedy (2,789,958) |
| 1987 | Drama (4,144,004) | Comedy (3,691,770) | Action (2,364,221) |
| 1988 | Drama (4,473,262) | Comedy (3,993,103) | Action (2,719,783) |
| 1989 | Comedy (5,019,532) | Drama (3,970,324) | Adventure (2,946,106) |
| 1990 | Drama (6,332,597) | Comedy (4,023,103) | Crime (3,592,542) |
| 1991 | Drama (5,596,163) | Crime (3,679,019) | Comedy (3,199,913) |
| 1992 | Drama (6,106,649) | Comedy (4,079,332) | Crime (3,613,791) |
| 1993 | Drama (9,012,484) | Comedy (4,507,640) | Crime (3,050,272) |
| 1994 | Drama (15,759,420) | Crime (6,511,377) | Comedy (5,684,586) |
| 1995 | Drama (12,538,990) | Crime (7,773,151) | Comedy (6,088,830) |
| 1996 | Drama (7,873,198) | Comedy (4,795,391) | Crime (4,449,239) |
| 1997 | Drama (12,645,714) | Action (6,774,834) | Comedy (5,612,854) |
| 1998 | Drama (11,800,157) | Comedy (9,874,531) | Crime (6,223,826) |
| 1999 | Drama (15,541,874) | Comedy (8,233,020) | Crime (7,190,261) |
| 2000 | Drama (13,037,225) | Comedy (8,347,108) | Adventure (6,997,046) |
| 2001 | Drama (14,756,674) | Comedy (9,526,610) | Adventure (9,261,621) |
| 2002 | Drama (17,081,024) | Adventure (8,700,310) | Action (8,405,142) |
| 2003 | Drama (13,274,270) | Action (11,722,350) | Comedy (10,774,182) |
| 2004 | Drama (16,494,754) | Action (11,532,824) | Comedy (10,961,866) |
| 2005 | Drama (13,709,258) | Comedy (10,211,440) | Action (9,070,666) |
| 2006 | Drama (20,911,052) | Comedy (11,793,629) | Thriller (8,672,816) |
| 2007 | Drama (18,557,236) | Comedy (11,733,485) | Action (9,004,528) |
| 2008 | Drama (17,595,233) | Action (13,419,561) | Comedy (11,341,471) |
| 2009 | Drama (17,612,963) | Comedy (13,480,999) | Action (12,126,154) |
| 2010 | Drama (17,577,170) | Action (13,345,627) | Adventure (13,189,055) |
| 2011 | Drama (20,769,808) | Action (17,162,784) | Comedy (13,997,192) |
| 2012 | Drama (20,135,136) | Action (14,907,246) | Comedy (12,523,735) |
| 2013 | Drama (22,005,476) | Action (17,199,545) | Comedy (14,971,794) |
| 2014 | Drama (24,538,160) | Action (20,953,891) | Adventure (17,753,805) |
| 2015 | Drama (20,513,226) | Action (15,574,153) | Adventure (14,173,242) |
| 2016 | Drama (20,909,486) | Action (17,223,407) | Adventure (12,373,219) |
| 2017 | Drama (20,828,838) | Action (16,723,873) | Comedy (11,316,585) |
| 2018 | Drama (17,432,900) | Action (15,092,453) | Adventure (13,359,177) |
| 2019 | Drama (22,050,482) | Action (12,376,332) | Comedy (12,280,769) |
| 2020 | Drama (10,491,432) | Comedy (6,522,967) | Action (6,137,659) |
| 2021 | Drama (14,417,065) | Action (12,890,131) | Adventure (10,201,318) |
| 2022 | Drama (16,000,756) | Action (13,369,554) | Comedy (10,222,181) |
| 2023 | Drama (14,798,977) | Action (10,600,229) | Comedy (9,795,757) |
| 2024 | Drama (11,697,311) | Action (8,672,259) | Comedy (7,114,308) |
| 2025 | Drama (8,687,310) | Action (7,714,781) | Comedy (5,930,476) |

First-place counts over the 46 years are Drama 42, Comedy 2, Adventure 1, Action 1.

Full output in `project/output/2_2_top_genres`.

### 2.3 Top three genres compared to the other genres

The table compares the three leading genres with all remaining genres in the same year. The vote shares use genre-assigned votes. A vote can appear more than once because a movie can have several genres. The ratings are weighted by the number of votes.

| Year | Top 3 vote share (%) | Other vote share (%) | Top 3 rating | Other rating |
| --- | --- | --- | --- | --- |
| 1980 | 44.34 | 55.66 | 7.73 | 7.50 |
| 1981 | 46.47 | 53.53 | 7.24 | 6.85 |
| 1982 | 43.72 | 56.28 | 7.56 | 7.15 |
| 1983 | 45.85 | 54.15 | 7.43 | 7.11 |
| 1984 | 44.14 | 55.86 | 7.35 | 7.18 |
| 1985 | 51.53 | 48.47 | 7.39 | 7.02 |
| 1986 | 46.21 | 53.79 | 7.20 | 7.05 |
| 1987 | 42.63 | 57.37 | 7.09 | 7.06 |
| 1988 | 45.05 | 54.95 | 7.13 | 7.10 |
| 1989 | 49.44 | 50.56 | 7.22 | 6.78 |
| 1990 | 45.58 | 54.42 | 7.30 | 7.07 |
| 1991 | 44.16 | 55.84 | 7.36 | 7.49 |
| 1992 | 46.30 | 53.70 | 7.23 | 7.00 |
| 1993 | 44.76 | 55.24 | 7.31 | 7.39 |
| 1994 | 58.25 | 41.75 | 7.87 | 7.32 |
| 1995 | 48.96 | 51.04 | 7.59 | 7.28 |
| 1996 | 44.90 | 55.10 | 6.98 | 6.78 |
| 1997 | 44.07 | 55.93 | 7.09 | 7.13 |
| 1998 | 51.48 | 48.52 | 7.40 | 6.80 |
| 1999 | 43.64 | 56.36 | 7.53 | 7.32 |
| 2000 | 44.97 | 55.03 | 7.21 | 6.98 |
| 2001 | 42.38 | 57.62 | 7.36 | 7.16 |
| 2002 | 42.41 | 57.59 | 7.22 | 7.04 |
| 2003 | 45.50 | 54.50 | 7.11 | 7.22 |
| 2004 | 41.33 | 58.67 | 7.02 | 7.11 |
| 2005 | 40.38 | 59.62 | 6.79 | 6.87 |
| 2006 | 42.70 | 57.30 | 7.12 | 6.95 |
| 2007 | 38.33 | 61.67 | 6.96 | 6.91 |
| 2008 | 40.38 | 59.62 | 6.75 | 7.10 |
| 2009 | 41.33 | 58.67 | 6.98 | 6.88 |
| 2010 | 39.98 | 60.02 | 6.97 | 7.02 |
| 2011 | 46.09 | 53.91 | 6.84 | 6.75 |
| 2012 | 42.74 | 57.26 | 6.90 | 6.96 |
| 2013 | 41.53 | 58.47 | 6.84 | 6.95 |
| 2014 | 47.02 | 52.98 | 7.09 | 6.96 |
| 2015 | 46.61 | 53.39 | 6.98 | 6.77 |
| 2016 | 44.08 | 55.92 | 6.89 | 6.90 |
| 2017 | 45.04 | 54.96 | 6.93 | 6.80 |
| 2018 | 44.30 | 55.70 | 6.94 | 6.74 |
| 2019 | 43.63 | 56.37 | 7.00 | 6.85 |
| 2020 | 44.71 | 55.29 | 6.42 | 6.41 |
| 2021 | 46.42 | 53.58 | 6.78 | 6.54 |
| 2022 | 46.38 | 53.62 | 6.75 | 6.56 |
| 2023 | 44.94 | 55.06 | 6.67 | 6.66 |
| 2024 | 42.80 | 57.20 | 6.57 | 6.52 |
| 2025 | 39.30 | 60.70 | 6.51 | 6.46 |

The three leading genres receive between 38.33% and 58.25% of genre-assigned votes. Their weighted rating is higher in 35 of the 46 years. A high vote total and a high rating measure different things.

Full output in `project/output/2_3_genre_comparison`.

### 2.4 Directors with exactly one movie rated ≥ 8.0 and others averaging ≤ 6.0

The query counts each director/movie pair once. It requires exactly one rated movie at 8.0 or above and at least two other rated movies with an average of 6.0 or below. Movies without a rating are excluded. There is no minimum vote threshold.

**1,572 directors** meet these conditions. These are the first five results, ordered by the average rating of the other movies.

| Director | High-rated film | Rating | Other rated films | Other average |
| --- | --- | --- | --- | --- |
| Salim Baba | Peppatty | 8.50 | 2 | 2.40 |
| Rajesh Amanakara | Punarjani | 8.10 | 2 | 2.45 |
| David Palmieri | Twelve | 8.20 | 10 | 2.52 |
| Noah Luke | Python of Jungle | 8.30 | 6 | 2.63 |
| Forrest Casper | Jason Thunder: Double Feature | 9.00 | 2 | 2.75 |

Some ratings may come from few votes. This list follows the requested rating conditions, but it does not measure how reliable each rating is.

Full output in `project/output/2_4_directors`.

### 2.5 TV series: worst episode in the last season, best in the first two

A series needs at least three numbered seasons. Every included season must have at least ten episodes with known positive season and episode numbers. Specials are excluded. Best and worst mean the highest and lowest available episode ratings. When ratings are tied, one matching episode in the required season is enough.

**552 series** qualify. These are the first five, ordered by the number of seasons.

| Series | Seasons | Smallest season | Rated episodes | Best rating | Worst rating |
| --- | --- | --- | --- | --- | --- |
| Papiny dochki | 20 | 20 | 259 | 8.50 | 4.60 |
| Roadkill | 13 | 11 | 9 | 9.50 | 6.80 |
| Two and a Half Men | 12 | 15 | 261 | 8.70 | 3.60 |
| Murphy Brown | 11 | 13 | 260 | 8.10 | 5.90 |
| Evening Urgant | 11 | 36 | 5 | 9.40 | 7.20 |

The season size includes unrated episodes, while the best and worst checks only use rated episodes. A series with very few rated episodes has weaker evidence, even if it has many episodes.

Full output in `project/output/2_5_series_extremes`.

### 2.6 Actors successful in multiple languages

Success is defined as a movie rating of at least 7.0 and at least 1,000 votes. The query prepares separate actor lists for at least two languages and at least three languages, with at least two distinct successful movies.

IMDb language codes describe title variants. The language of a translated title does not prove the language spoken in the movie. The query therefore checks the language on variants marked as original titles.

| Coverage check | Movies |
| --- | --- |
| Successful movies with actor/actress credits | 12,831 |
| With usable language on an original-title variant | 0 |

Both actor lists are empty because the source has no usable language evidence under this rule. **Question 2.6 remains unanswered.** This does not show that multilingual actors are absent. Spoken-language data from an additional source is needed.

Outputs are in `project/output/2_6_multilingual_actors`, `project/output/2_6_three_languages`, `project/output/2_6_language_evidence`, `project/output/2_6_language_coverage`.

### 2.7 Long careers that peaked early

The query requires at least 15 dated movie credits and a gap of at least 20 years between the first and last release. Future releases are excluded. Early career means the first third of this observed year range. The highest early rating must be strictly above the highest later rating, with a rated movie in both periods.

**10,810 actors and actresses** match. The first five results below have the longest observed release spans.

| Person | First–last release | Movies | Best early rating | Best later rating |
| --- | --- | --- | --- | --- |
| Wilhelm Bendow | 1914–2023 | 55 | 7.70 | 6.20 |
| Donald Calthrop | 1916–2024 | 46 | 8.20 | 7.20 |
| Gustav von Wangenheim | 1916–2024 | 17 | 7.80 | 6.80 |
| Nils Asther | 1916–2022 | 70 | 7.50 | 7.20 |
| Wallace Beery | 1913–2018 | 125 | 7.50 | 6.20 |

Some spans are over 100 years. The output measures release dates of credited titles, which can include much later releases. It should not be read as the actual number of years a person worked. Also, an early highest-rated movie does not mean that the average early rating is higher.

Full output in `project/output/2_7_early_career_peaks`.

### 2.8 Multi-talented professionals

This query uses three roles, actor, director and writer. Actor and actress are grouped as one role. A person is multi-talented when they have at least two roles across their movie credits. For each person, the query compares rated movies with one role against rated movies with several roles on the same project.

The output contains **242,965 professionals** and **444,992 person/movie records with several roles**. Of the 59,637 people with rated movies in both groups, 30,289 have a higher average for multiple-role movies, 28,584 have a lower average and 764 have equal averages after rounding both averages to two decimals.

These selected examples show both positive and negative differences. Film counts in this table include only rated films.

| Person | Single-role films | Single-role average | Multiple-role films | Multiple-role average | Difference |
| --- | --- | --- | --- | --- | --- |
| Woody Allen | 11 | 5.94 | 54 | 6.89 | 0.95 |
| Clint Eastwood | 43 | 6.84 | 26 | 6.89 | 0.04 |
| Sylvester Stallone | 41 | 5.52 | 25 | 6.32 | 0.80 |
| Jesús Franco | 48 | 5.03 | 159 | 4.85 | -0.18 |
| Eckhart Schmidt | 8 | 6.54 | 22 | 5.69 | -0.85 |

The difference is the multiple-role average minus the single-role average. This comparison does not show that adding roles causes a better or worse film.

Full output in `project/output/2_8_role_comparison`. Project-level records are in `project/output/2_8_multi_role_projects`.

### Methodological Explanation

The jobs read the clean Parquet tables with Spark. Title and person IDs are used for joins. Director arrays are expanded, and repeated credits are removed before counting films or roles. Spark lets the jobs join the large tables without loading the whole dataset into Python.

The same definitions are used throughout each query. Genres share a movie's full vote count. Director averages and career peaks use rated movies. Role comparisons use ordinary film-rating averages, with the number of rated films shown. Votes measure audience interest, while ratings measure the score given by voters. The two-standard-deviation rule gives a simple runtime threshold, but very long films can move that threshold. Using one third of the release span adapts the early period to different career lengths.

Other choices would give different results. Runtime differences could use quartiles instead of a z-score. Genres could be ranked by film count instead of votes. Success could use another rating or vote threshold. Early career could mean a fixed number of years instead of one third of the observed span.

The main limits are missing film-language data, uneven rating coverage and long release spans in historical credits. These points matter when reading the tables. The complete CSV outputs keep the IDs and supporting values for further checks.

The full first job completed in 82 seconds and the second in 914 seconds. Focused checks covered rating thresholds, tied genre totals, zero runtime variance, incomplete seasons, language variants, career boundaries and duplicate roles.

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
