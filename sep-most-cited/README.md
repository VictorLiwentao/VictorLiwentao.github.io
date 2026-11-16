# The philosophers and works the Stanford Encyclopedia of Philosophy cites most (2026)

An update and extension of Eric Schwitzgebel and Jordan Jackson's 2024 counts, rebuilt from all 1,872 entries of the
[Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/) as of 16 November 2026.

`index.html` is the whole site: one self-contained page with the data embedded. It has:

- a **co-citation map** of the 446 most-cited philosophers born since 1900 (who is cited by the same entries),
- a **profile** for each philosopher (`#p-name` links): life dates, field mix, most-cited works, who they are cited alongside, and every citing entry,
- **generations and gender**: birth years and gender from Wikidata,
- **field leaders**, the **279 most-cited works**, and **changes since 2024**.

## Data

- `data/philosophers.csv`: 446 philosophers born 1900+ cited in 30+ entries, plus 49 earlier authors (rank_all_eras), with birth/death years, Wikidata gender and ID, main field, most-cited work and 2024 comparison.
- `data/works.csv`: 279 works first published 1900+ cited in 16+ entries.
- `data/entry_fields.json`: the field assigned to each SEP entry.
- `data/page_data.json`: everything the page uses.
- `data/schwitzgebel_*_2024.*`: the 2024 lists used for comparison. `data/wikidata_overrides.json`: hand-checked Wikidata matches.

## Method (short version)

A work or author scores one point per SEP main entry whose bibliography cites it, however many times.

**Works.** Same first author and titles beginning with the same words (ignoring punctuation, capitals, a leading article);
editions, reprints, near-identical spellings and multi-volume works merged; translations not merged; editor citations
excluded; first published 1900 or later (so Sidgwick's *Methods of Ethics*, 1874, is left out, unlike 2024).

**Philosophers.** First, second and last authors count, plus editors named before the date. Name variants merged; people
sharing a surname and initial split by first name, middle initial and cited titles. Three name keys that mix several people
(J. Allen, M. Martin, S. Smith) are left out. Main ranking: born 1900 or later.

**Fields and map.** Entries clustered (k-means on TF-IDF citation profiles), clusters named by hand and grouped into eight
fields. The map is a UMAP projection of each philosopher's citing entries (idf-weighted, cosine).

**Lives and gender.** From Wikidata, matched by name with candidates scored on description and on birth year vs. first
publication; uncertain matches checked by hand. Birth year known for 419 and gender for 434 of the 446.

Spot checks against a raw-text search put most counts within one to three entries.

## Re-running

```
python3 scripts/fetch.py slugs.txt raw              # slugs from plato.stanford.edu/contents.html
python3 scripts/parse.py raw records.jsonl
python3 scripts/works.py && python3 scripts/finalize_works.py 16
python3 scripts/authors.py && python3 scripts/finalize_authors.py
python3 scripts/build_data.py                       # works data + entry titles (page_data.json)
python3 scripts/fields.py 22 && python3 scripts/fields_final.py
python3 scripts/wikidata.py && python3 scripts/wd_match.py overrides
python3 scripts/profiles.py && python3 scripts/build_v2.py
```
Then substitute `page_data_v2.json` into `scripts/template.html` at `__DATA__` to rebuild `index.html`.

Original analyses: [The 253 most-cited works in the SEP](https://schwitzsplinters.blogspot.com/2025/03/the-253-most-cited-works-in-stanford.html)
and [The most-cited contemporary authors in the SEP](https://schwitzsplinters.blogspot.com/2024/08/the-378-most-cited-contemporary-authors.html).
Biographical data from [Wikidata](https://www.wikidata.org/) (CC0). Not affiliated with the SEP.
