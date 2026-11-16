"""Assemble data for the people-first site (v2)."""
import json, re, html, collections, csv, statistics, sys
sys.path.insert(0, 'scripts')
from common import fold, norm_surname, initial

R = json.load(open('authors_final.json', encoding='utf-8'))
PF = json.load(open('profiles.json', encoding='utf-8'))
WD = json.load(open('wd_matched.json', encoding='utf-8'))
F = json.load(open('entry_fields.json'))
old = json.load(open('page_data.json', encoding='utf-8'))   # v1 data: works, dropped, entry titles
MAC = PF['MAC']
FINE = sorted({v['fine'] for v in F.values()})
slugs = [e[0] for e in old['E']]
etitle = {e[0]: e[1] for e in old['E']}
eidx = {s: i for i, s in enumerate(slugs)}

people = R['contemporary'] + R['pre1900']
assert len(people) == len(PF['people'])

def natural(name):
    s, _, g = name.partition(', ')
    return f'{g} {s}'.strip() if g else s

def slugify(t):
    t = fold(t).lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')

def yr(s):
    try:
        return int(str(s).rstrip('-'))
    except Exception:
        return None

GMAP = {'female': 'f', 'male': 'm', 'non-binary': 'x'}
seen = set()
P = []
for i, (p, pr) in enumerate(zip(people, PF['people'])):
    w = WD.get(p['pid']) or {}
    nm = natural(p['name'])
    sl = slugify(nm)
    while sl in seen:
        sl += '-2'
    seen.add(sl)
    fine = [[FINE.index(f), c] for f, c in pr['fine'][:4]]
    rec = {'id': sl, 'a': nm, 'sort': p['name'], 'n': p['n'], 'p': 1 if p['pre1900'] else 0,
           'r': p.get('rank'), 'ra': None, 'o': p.get('n2024'), 'or': p.get('rank2024'),
           'b': yr(w.get('birth')), 'd': yr(w.get('death')), 'g': GMAP.get(w.get('gender'), ''),
           'wd': re.sub(r'\s*\((?:born |b\. |c\. )?\d{4}[^)]*\)|,?\s*\(?born \d{4}\)?|\s*\(?\d{4}\s*[\u2013-]\s*\d{0,4}\)?$', '', (w.get('desc') or '')).strip(' ,;')[:90], 'q': w.get('qid'), 'wp': w.get('article'),
           'mac': pr['mac'], 'fine': fine, 'nb': pr['nb'],
           'w': [{'t': x['t'], 'y': x['y'], 'n': x['n']} for x in pr['works']],
           'e': [eidx[e] for e in p['entries'] if e in eidx]}
    if 'xy' in pr:
        rec['xy'] = pr['xy']
    P.append(rec)
# all-era ranks
order = sorted(range(len(P)), key=lambda i: -P[i]['n'])
prev = None
for k, i in enumerate(order):
    if P[i]['n'] != prev:
        rr = k + 1; prev = P[i]['n']
    P[i]['ra'] = rr

# region labels for the map: median position of people whose top fine field is F
nC = len(R['contemporary'])
SHORT = {'Political philosophy & applied ethics': 'Political philosophy', 'Logic & philosophy of mathematics': 'Logic & mathematics',
         'Philosophy of mind & cognitive science': 'Mind & cognitive science', 'Philosophy of science & formal epistemology': 'Philosophy of science',
         'Philosophy of language': 'Language', 'Philosophy of physics': 'Physics', 'Philosophy of biology': 'Biology',
         'Philosophy of religion': 'Religion', 'Kant & German philosophy': 'Kant & German philosophy',
         'Continental philosophy & pragmatism': 'Continental & pragmatism', 'Arabic, Islamic & Jewish philosophy': 'Arabic & Jewish philosophy',
         'Philosophy of race, Africana & Latin American philosophy': 'Race & Africana', 'Late ancient philosophy': 'Late antiquity'}
groups = collections.defaultdict(list)
for i in range(nC):
    top = max(P[i]['fine'], key=lambda t: t[1])[0] if P[i]['fine'] else None
    if top is not None:
        groups[FINE[top]].append(P[i]['xy'])
REG = []
for f, pts in groups.items():
    if len(pts) >= 6:
        xs = sorted(x for x, y in pts); ys = sorted(y for x, y in pts)
        REG.append({'t': SHORT.get(f, f), 'x': round(statistics.median(xs), 4), 'y': round(statistics.median(ys), 4), 'n': len(pts)})

# works: link to people
by_base = collections.defaultdict(list)
for i, p in enumerate(people):
    by_base['|'.join(p['pid'].split('|')[:2])].append(i)
W = []
for w in old['W']:
    a = w['a'].split(' & ')[0]
    s, _, g = a.partition(', ')
    base = norm_surname(s) + '|' + initial(g)
    cands = by_base.get(base, [])
    if len(cands) > 1:
        c2 = [i for i in cands if people[i]['name'] == a]
        cands = c2 or sorted(cands, key=lambda i: -people[i]['n'])[:1]
    ww = dict(w)
    ww['a'] = ' & '.join(natural(x) if ', ' in x else x for x in w['a'].split(' & '))
    ww['pi'] = cands[0] if cands else None
    W.append(ww)
X = [dict(x, a=natural(x['a'])) for x in old['X']]
E = [[s, etitle[s], MAC.index(F[s]['macro']) if s in F else -1, FINE.index(F[s]['fine']) if s in F else -1] for s in slugs]
meta = dict(old['meta'])
meta['n_auth'] = nC
data = {'meta': meta, 'MAC': MAC, 'FINE': FINE, 'E': E, 'P': P, 'nC': nC, 'REG': REG, 'W': W, 'X': X}
json.dump(data, open('page_data_v2.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
import os
print('bytes', os.path.getsize('page_data_v2.json'), 'people', len(P), 'contemp', nC, 'regions', [(r['t'], r['n']) for r in REG])

# CSV export (people)
with open('out_philosophers.csv', 'w', newline='', encoding='utf-8') as f:
    c = csv.writer(f)
    c.writerow(['rank_born_1900_plus', 'rank_all_eras', 'citing_entries', 'name', 'born', 'died', 'gender_wikidata', 'main_field', 'most_cited_work', 'entries_2024', 'rank_2024', 'wikidata'])
    for p in sorted(P, key=lambda x: x['ra']):
        mf = MAC[max(range(8), key=lambda k: p['mac'][k])]
        c.writerow([p['r'] if not p['p'] else '', p['ra'], p['n'], p['a'], p['b'] or '', p['d'] or '', {'f': 'female', 'm': 'male', 'x': 'non-binary'}.get(p['g'], ''),
                    mf, p['w'][0]['t'] if p['w'] else '', p['o'] or '', p['or'] or '', p['q'] or ''])
