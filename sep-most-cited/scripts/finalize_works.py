"""Apply manual fixes to work clusters, rank, and compare with Schwitzgebel 2024."""
import json, re, collections, sys
sys.path.insert(0, 'scripts')
from common import norm_surname, norm_title_tokens, fold

recs = [json.loads(l) for l in open('records.jsonl', encoding='utf-8')]
W = json.load(open('work_clusters.json', encoding='utf-8'))
THRESH = int(sys.argv[1]) if len(sys.argv) > 1 else 16

# rebuild record index per cluster (works.py stores entries only); recompute via key+canon
# simpler: re-run clustering membership by importing works module state
import importlib.util
spec = importlib.util.spec_from_file_location('works', 'scripts/works.py')
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    works = importlib.util.module_from_spec(spec); spec.loader.exec_module(works)
clusters = works.clusters

EXCLUDE_KEYS = {('descartes|r', 'philosophical writings of descartes'), ('godel|k', 'collected works')}
# split rules: (key, canon) -> list of (label_title, year_lo, year_hi)
SPLITS = {
    ('rawls|j', 'justice as fairness'): [('Justice as Fairness: A Restatement', 1990, 2100),
                                        ('Justice as Fairness: Political not Metaphysical', 1984, 1986),
                                        ('Justice as Fairness', 1950, 1983)],
    ('fodor|j', 'special sciences'): [('Special Sciences (or: The Disunity of Science as a Working Hypothesis)', 1960, 1990),
                                     ('Special Sciences: Still Autonomous after All These Years', 1991, 2100)],
}

def min_year(r):
    y = r.get('years') or []
    return min(y) if y else None

def summarize(key, idxs, forced_title=None):
    entries = sorted({recs[i]['entry'] for i in idxs})
    yrs = collections.Counter(min_year(recs[i]) for i in idxs if min_year(recs[i]))
    tot = sum(yrs.values())
    disp_year = None
    for y in sorted(yrs):
        if yrs[y] / tot >= 0.15:
            disp_year = y; break
    names = collections.Counter((recs[i]['authors'][0][0].strip(), recs[i]['authors'][0][1].strip()) for i in idxs)
    # choose display name: most common surname spelling, longest given name seen >=2 times
    sur = collections.Counter(n[0] for n in names.elements()).most_common(1)[0][0]
    givens = [(g, c) for (s, g), c in names.items() if g]
    good = [g for g, c in givens if c >= 2] or [g for g, c in givens]
    given = max(good, key=lambda g: (len(g.replace('.', '').replace(' ', '')) > 2, len(g))) if good else ''
    given = re.sub(r'(?<=[A-Z])(?=\s|$)', '.', given).strip()
    co = collections.Counter()
    nco = 0
    for i in idxs:
        au = recs[i]['authors']
        if len(au) > 1:
            nco += 1
            co[tuple((s, g) for s, g in au[1:3])] += 1
    coauth = None
    if nco / len(idxs) >= 0.5 and co:
        best = co.most_common(1)[0][0]
        coauth = [f"{g} {s}".strip() for s, g in best]
    titles = collections.Counter(recs[i]['title'].strip(' ,.;:“”‘’"\'') for i in idxs)
    title = forced_title or titles.most_common(1)[0][0]
    if title and title[0].islower():
        title = title[0].upper() + title[1:]
    return {'key': key, 'author_surname': sur, 'author_given': given, 'coauthors': coauth,
            'year': disp_year, 'title': title, 'n': len(entries), 'entries': entries,
            'n_lines': len(idxs)}

final = []
for cl in clusters:
    key, canon = cl['key'], ' '.join(cl['canon'])
    if len({recs[i]['entry'] for i in cl['idxs']}) < THRESH - 4:
        continue
    if (key, canon) in EXCLUDE_KEYS:
        continue
    if (key, canon) in SPLITS:
        rules = SPLITS[(key, canon)]
        groups = collections.defaultdict(list)
        for i in cl['idxs']:
            y = min_year(recs[i])
            lab = None
            for t, lo, hi in rules:
                if y and lo <= y <= hi:
                    lab = t; break
            if lab is None:
                lab = rules[0][0]
            groups[lab].append(i)
        for t, idxs in groups.items():
            final.append(summarize(key, idxs, forced_title=t))
        continue
    final.append(summarize(key, cl['idxs']))

# year rule: first published 1900 or later
excluded_pre1900 = [w for w in final if (w['year'] or 0) < 1900]
final = [w for w in final if (w['year'] or 0) >= 1900]
final.sort(key=lambda w: (-w['n'], w['author_surname'], w['title']))

# ---- compare with 2024 list
old = []
for line in open('ref/works2024.txt', encoding='utf-8'):
    m = re.match(r'\s*(\d+)\.\s*\((\d+)\)\s*(.+)', line)
    if not m: continue
    rank, cnt, rest = int(m.group(1)), int(m.group(2)), m.group(3)
    sm = re.match(r"([^,]+),\s*(.*?)(\d{4}).*?[,\.]\s*(.+)$", rest)
    if not sm: continue
    old.append({'rank': rank, 'n': cnt, 'surname': sm.group(1).strip(), 'title': sm.group(4).strip(), 'raw': rest})

def toks(title):
    t = [x for x in norm_title_tokens(title) if x != ':']
    return [x.rstrip('s') for x in t]

def match_old(w):
    s4 = norm_surname(w['author_surname'])[:4]
    mt = toks(w['title'])
    best = None
    for o in old:
        if norm_surname(o['surname'])[:4] != s4:
            continue
        ot = toks(o['title'])
        k = min(2, len(ot), len(mt))
        if k and ot[:k] == mt[:k]:
            if id(o) not in matched and (best is None or abs(o['n'] - w['n']) < abs(best['n'] - w['n'])):
                best = o
    return best

matched = set()
for w in final:
    o = match_old(w)
    if o and id(o) not in matched:
        w['n2024'] = o['n']; w['rank2024'] = o['rank']; matched.add(id(o))
        o['_m'] = True

# ranks with ties
rank = 0; prev = None
for i, w in enumerate(final):
    if w['n'] != prev:
        rank = i + 1; prev = w['n']
    w['rank'] = rank

top = [w for w in final if w['n'] >= THRESH]
dropped = [w for w in final if w['n'] < THRESH and 'n2024' in w]
json.dump(dropped, open('works_dropped.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(top, open('works_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(excluded_pre1900[:0] + sorted([w for w in excluded_pre1900 if w['n'] >= THRESH], key=lambda w: -w['n']),
          open('works_pre1900.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('works >= %d:' % THRESH, len(top))
print('\nOld-list works not matched (2024 count):')
for o in old:
    if not o.get('_m'):
        print('  ', o['n'], o['raw'][:90])
