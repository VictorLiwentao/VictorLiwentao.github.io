#!/usr/bin/env python3
"""Build killbench/index.html from scripts/template.html and data/killbench.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((root / "data" / "killbench.json").read_text(encoding="utf-8"))
tpl = (root / "scripts" / "template.html").read_text(encoding="utf-8")
assert "/*__DATA__*/" in tpl
out = tpl.replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
(root / "index.html").write_text(out, encoding="utf-8")
print("wrote", root / "index.html", len(out), "bytes")
