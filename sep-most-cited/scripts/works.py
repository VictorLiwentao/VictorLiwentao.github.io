"""Cluster bibliography records into works and count citing entries."""
import json, collections, sys, re
sys.path.insert(0, 'scripts')
from common import norm_surname, initial, norm_title_tokens

recs = [json.loads(l) for l in open('records.jsonl', encoding='utf-8')]

# person key = surname + first initial; resolve blank initials to dominant initial
by_sur = collections.defaultdict(collections.Counter)
for r in recs:
    for s, g in r.get('authors') or []:
        ns = norm_surname(s)
        if ns:
            by_sur[ns][initial(g)] += 1

def pkey(s, g):
    ns = norm_surname(s)
    if not ns:
        return None
    i = initial(g)
    if not i:
        c = by_sur[ns]
        tot = sum(v for k, v in c.items() if k)
        if tot:
            k, v = max(((k, v) for k, v in c.items() if k), key=lambda x: x[1])
            if v / tot >= 0.8:
                i = k
    return ns + '|' + i

# group records by first author key
groups = collections.defaultdict(list)
for idx, r in enumerate(recs):
    au = r.get('authors') or []
    if not au or r.get('editor'):
        continue
    k = norm_surname(au[0][0])
    if not k:
        continue
    toks = norm_title_tokens(r.get('title'))
    if not toks:
        continue
    groups[k].append((toks, idx))

SEP = ':'

def is_prefix(c, t):
    if len(c) > len(t) or t[:len(c)] != c:
        return False
    if len(c) == len(t):
        return True
    nwords = sum(1 for w in c if w != SEP)
    # multi-word prefix merges; single-word prefix only if followed by a subtitle separator
    return nwords >= 2 or t[len(c)] == SEP

clusters = []  # list of dict(key, canon, members)
SPLITS = []
for k, items in groups.items():
    # unique titles with frequency
    tcount = collections.Counter(tuple(t) for t, _ in items)
    titles = sorted(tcount, key=lambda t: (len(t), -tcount[t]))
    canon_of = {}
    canons = []
    for t in titles:
        # candidate canonicals that are prefixes; choose the longest such (most specific)
        best = None
        for c in canons:
            if is_prefix(list(c), list(t)):
                if best is None or len(c) > len(best):
                    best = c
        if best is None:
            canons.append(t); canon_of[t] = t
        else:
            canon_of[t] = canon_of[best]
    # fuzzy-merge near-identical canonical titles (e.g. "what we owe each other" / "what we owe to each other")
    import difflib
    croot = {c: c for c in canons}
    order = sorted(canons, key=lambda c: -sum(tcount[t] for t in titles if canon_of[t] == c))
    for i, c in enumerate(order):
        sc = ' '.join(w for w in c if w != SEP)
        for d in order[:i]:
            if croot[d] != d:
                continue
            sd = ' '.join(w for w in d if w != SEP)
            if c[0] == d[0] and min(len(sc), len(sd)) >= 12 and difflib.SequenceMatcher(None, sc, sd).ratio() >= 0.9:
                croot[c] = d; break
    for t in titles:
        canon_of[t] = croot[canon_of[t]]
    members = collections.defaultdict(list)
    for t, idx in items:
        members[canon_of[tuple(t)]].append(idx)
    for c, idxs in members.items():
        ini = collections.Counter(initial(recs[i]['authors'][0][1]) for i in idxs)
        nb = {x: v for x, v in ini.items() if x}
        tot = sum(nb.values())
        if tot and max(nb.values()) / tot < 0.85 and len(idxs) >= 8:
            # split by initial; blanks go to the dominant initial
            dom = max(nb, key=nb.get)
            parts = collections.defaultdict(list)
            for i in idxs:
                x = initial(recs[i]['authors'][0][1]) or dom
                parts[x].append(i)
            SPLITS.append((k, ' '.join(c), {x: len(v) for x, v in parts.items()}))
            for x, v in parts.items():
                clusters.append({'key': k + '|' + x, 'canon': c, 'idxs': v})
        else:
            dom = max(nb, key=nb.get) if nb else ''
            clusters.append({'key': k + '|' + dom, 'canon': c, 'idxs': idxs})

out = []
for cl in clusters:
    entries = {recs[i]['entry'] for i in cl['idxs']}
    if len(entries) < 8:
        continue
    yrs = collections.Counter()
    for i in cl['idxs']:
        y = recs[i].get('years') or []
        if y:
            yrs[min(y)] += 1
    names = collections.Counter()
    for i in cl['idxs']:
        s, g = recs[i]['authors'][0]
        names[(s.strip(), g.strip())] += 1
    co = collections.Counter()
    for i in cl['idxs']:
        au = recs[i]['authors']
        if len(au) > 1:
            co[' and '.join(f"{g} {s}".strip() for s, g in au[1:])] += 1
    titles = collections.Counter(recs[i]['title'].strip(' ,.;:') for i in cl['idxs'])
    out.append({
        'key': cl['key'], 'canon': ' '.join(cl['canon']), 'n_entries': len(entries),
        'n_cites': len(cl['idxs']), 'year_mode': yrs.most_common(1)[0][0] if yrs else None,
        'year_min': min(yrs) if yrs else None, 'years': yrs.most_common(5),
        'name': names.most_common(3), 'coauthors': co.most_common(2),
        'title': titles.most_common(4), 'entries': sorted(entries),
    })
out.sort(key=lambda x: -x['n_entries'])
json.dump(out, open('work_clusters.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('clusters with >=8 entries:', len(out))
for sp in SPLITS:
    if sum(sp[2].values())>=25: print('SPLIT', sp)
for w in out[:60]:
    print(w['n_entries'], w['key'], w['year_mode'], w['title'][0][0][:60], '|', w['name'][0])
