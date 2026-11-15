# Open question

Do recurring director–actor pairs receive better ratings than each person's
movies with other partners?

The job uses feature films released in 1980–2025 with at least 1,000 votes.
It joins titles, ratings, acting principals, director crew arrays and names.
Actor and actress credits are combined. Credits are deduplicated per person
and film; actor/director self-pairs are excluded. Co-directed films count
once for each credited director.

A recurring pair needs at least three qualifying films together. Each
person also needs at least three qualifying films outside that pair. A
shared film is removed from both outside-pair baselines. All means give
each film equal weight. The job exports the two rating differences, a flag
for pairs strictly above both baselines, and the shared films as evidence.
Differences are rounded to ten decimal places before testing improvement,
so floating-point noise cannot turn a rating tie into a positive result.
The aggregate summary gives each eligible pair equal weight, so the same
film or person may contribute to several pairs. This is a descriptive
comparison; genre, release year, selection and repeated observations can
affect it, and a higher mean does not establish a causal collaboration effect.

Thresholds can be changed with `--min-votes`, `--min-shared`,
`--min-baseline` and `--last-year`. The parameter export records the run's
settings and the number of eligible rated feature films. CSV outputs are
complete; Markdown previews contain at most fifty rows.

```bash
docker compose exec spark python /home/jovyan/jobs/50_open_question.py
docker compose exec spark python /home/jovyan/jobs/test_open_question.py
```
