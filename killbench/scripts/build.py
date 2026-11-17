#!/usr/bin/env python3
"""Build killbench/index.html and data/killbench.csv from data/killbench.json.

Score = deaths per year. Annual estimates are used as reported; a count over a
period is divided by the length of the period in years.
"""
import csv, json, math, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((root / "data" / "killbench.json").read_text(encoding="utf-8"))

for e in data["entries"]:
    c = e["count"]
    div = e["years"] if e["basis"] == "window" else 1
    e["rate"] = {k: c[k] / div for k in ("lo", "hi", "pt") if k in c}
    r = e["rate"]
    # ranking value: central estimate if given, else the single value, else the geometric midpoint
    e["sort"] = r.get("pt", r["lo"] if r["lo"] == r["hi"] else math.sqrt(r["lo"] * r["hi"]))

ranked = sorted(data["entries"], key=lambda e: -e["sort"])
for i, e in enumerate(ranked, 1):
    e["rank"] = i
data["entries"] = ranked

with open(root / "data" / "killbench.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rank", "id", "entry", "measure", "type", "deaths_per_year", "deaths_per_year_low",
                "deaths_per_year_high", "basis", "period", "period_years", "count", "count_low",
                "count_high", "source", "source_url"])
    for e in ranked:
        r, c = e["rate"], e["count"]
        single = r["lo"] == r["hi"]
        w.writerow([e["rank"], e["id"], e["name"], e["measure"], e["type"],
                    round(r.get("pt", r["lo"] if single else e["sort"]), 2), round(r["lo"], 2), round(r["hi"], 2),
                    e["basis"], e["period"], e.get("years", 1),
                    c.get("pt", c["lo"] if c["lo"] == c["hi"] else ""), c["lo"], c["hi"],
                    e["refs"][0]["label"], e["refs"][0]["url"]])

tpl = (root / "scripts" / "template.html").read_text(encoding="utf-8")
assert "/*__DATA__*/" in tpl
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
(root / "index.html").write_text(tpl.replace("/*__DATA__*/", blob), encoding="utf-8")
for e in ranked:
    print(f'{e["rank"]:>2} {e["name"]:<18} {e["sort"]:>14,.1f}  {e["rate"]["lo"]:>14,.1f} {e["rate"]["hi"]:>14,.1f}')
