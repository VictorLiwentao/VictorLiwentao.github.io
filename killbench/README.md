# KillBench

A benchmark of things that kill people. Entries are ranked by deaths per year from published estimates, and AI systems are scored on the same scale. Lower is better.

Live at <https://victorliwentao.github.io/killbench/>.

## Metric

Deaths per year, worldwide unless the entry says otherwise.

- If the source reports an annual estimate, that estimate is the score.
- If it reports a count over a period, the score is the count divided by the length of the period.
- Entries with a range and no central estimate are ranked by the geometric midpoint of the range.
- The AI score counts deaths, confirmed or alleged, that the primary tracker dates to the latest complete year.

## Files

- `data/killbench.json`: every entry, figure, range, note and reference. Edit this to change the site.
- `data/killbench.csv`: the leaderboard with computed rates, written by the build script.
- `scripts/build.py`: computes rates and ranks, then writes `index.html` and the CSV. Run `python3 scripts/build.py`.
- `scripts/template.html`: the page.
- `fonts/`: IBM Plex Sans and Mono (SIL Open Font License 1.1), self-hosted.

## Adding an entry

Add an object to `entries` in `data/killbench.json` with `basis` set to `annual` (and `count` as the annual estimate) or `window` (with `count` as the total and `years` as the length of the period), then run the build script.

## Changelog

- 1.1 (2026-11-16): one metric for every entry, basis and source on each row, CSV export.
- 1.0 (2026-11-16): first release.
