# Most-cited works and philosophers in the Stanford Encyclopedia of Philosophy (2026)

An update of Eric Schwitzgebel and Jordan Jackson's 2024 counts, rebuilt from all 1,872 entries of the
[Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/) as of 16 November 2026.

- `index.html` is the whole site: one self-contained page with the data embedded. Push this folder to a
  GitHub repo and turn on GitHub Pages (Settings → Pages → Deploy from branch → `main` / root).
- `data/works.csv`: the 279 works first published since 1900 that are cited in 16 or more entries.
- `data/philosophers.csv`: the 449 philosophers born since 1900 who are cited in 30 or more entries, plus
  49 earlier-born authors (marked `born_before_1900`) for the "all eras" view.
- `data/schwitzgebel_*_2024.*`: the 2024 lists used for the "vs 2024" column.

## Method (short version)

A work or author scores one point per SEP main entry whose bibliography cites it, however many times.

**Works.** Citations match when the first author matches and the titles begin with the same words
(ignoring punctuation, capitals and a leading article). Editions, reprints, near-identical spellings and
multi-volume works are merged; translations are not. Editor citations are not counted. Only works first
published in 1900 or later are ranked, so Sidgwick's *Methods of Ethics* (1874; 58 entries) is left out,
unlike in the 2024 list.

**Philosophers.** First, second and last authors count, plus editors named before the date. Name variants
are merged; people sharing a surname and initial are split by first name, middle initial and cited titles.
The main ranking covers authors born in 1900 or later, as in 2024.

Spot checks against a raw-text search put most counts within one to three entries. Small changes since
2024 can reflect differences between two scrapers as well as real revisions.

## Re-running

```
python3 scripts/fetch.py slugs.txt raw        # slugs.txt: entry slugs from plato.stanford.edu/contents.html
python3 scripts/parse.py raw records.jsonl
python3 scripts/works.py && python3 scripts/finalize_works.py 16
python3 scripts/authors.py && python3 scripts/finalize_authors.py
python3 scripts/build_data.py                 # writes page_data.json and the CSVs
```
Then substitute `page_data.json` into `scripts/template.html` at `__DATA__` to rebuild `index.html`.
The scripts expect Schwitzgebel's 2024 lists in `ref/` (copies are in `data/`).

Original analyses: [The 253 most-cited works in the SEP](https://schwitzsplinters.blogspot.com/2025/03/the-253-most-cited-works-in-stanford.html)
and [The most-cited contemporary authors in the SEP](https://schwitzsplinters.blogspot.com/2024/08/the-378-most-cited-contemporary-authors.html).
Not affiliated with the SEP.
