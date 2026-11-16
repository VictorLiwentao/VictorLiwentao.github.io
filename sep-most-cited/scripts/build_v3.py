"""Merge v2 page data with the pre-1900 'long canon' and the race-over-time data."""
import json, re, collections, statistics, sys, csv
import numpy as np
sys.path.insert(0, 'scripts')
from common import fold

D = json.load(open('page_data_v2.json', encoding='utf-8'))
RACE = json.load(open('race.json', encoding='utf-8'))
L = [x for x in json.load(open('longcanon.json', encoding='utf-8')) if len(x['ment']) >= 5]
for x in L:
    x['all_slugs'] = sorted(x['all_slugs'], key=lambda t: (len(t), t))   # main article first
F = json.load(open('entry_fields.json'))
MAC, FINE = D['MAC'], D['FINE']
eidx = {e[0]: i for i, e in enumerate(D['E'])}

DISPLAY = {'Moshe ben Maimon': 'Maimonides', 'Benedictus de Spinoza': 'Baruch Spinoza', 'Augustine of Hippo': 'Augustine',
           'Anthony Ashley-Cooper, 3rd Earl of Shaftesbury': 'Shaftesbury', 'Margaret Cavendish, Duchess of Newcastle-upon-Tyne': 'Margaret Cavendish',
           'William David Ross': 'W. D. Ross', 'Luitzen Egbertus Jan Brouwer': 'L. E. J. Brouwer', 'Friedrich Wilhelm Joseph Schelling': 'F. W. J. Schelling',
           'Clarence Irving Lewis': 'C. I. Lewis', 'Farabi': 'al-Fārābī', 'Zhuang Zhou': 'Zhuangzi', 'Henry Habberley Price': 'H. H. Price',
           'Thomas Hill Green': 'T. H. Green', 'Gottfried Wilhelm Leibniz': 'G. W. Leibniz', 'Georg Wilhelm Friedrich Hegel': 'G. W. F. Hegel',
           'Pseudo-Dionysius the Areopagite': 'Pseudo-Dionysius', 'Simplicius of Cilicia': 'Simplicius', 'Harold Arthur Prichard': 'H. A. Prichard',
           'Johannes Scotus Eriugena': 'John Scottus Eriugena', 'Sophie de Condorcet': 'Sophie de Grouchy', 'Kitarō Nishida': 'Nishida Kitarō',
           'Marquis de Condorcet': 'Nicolas de Condorcet', 'Tetsuro Watsuji': 'Watsuji Tetsurō'}
DESC_FIX = {'Kumārila Bhaṭṭa': 'Indian Mīmāṃsā philosopher', 'Sophie de Condorcet': 'French philosopher and translator',
            'Anthony Ashley-Cooper, 3rd Earl of Shaftesbury': 'English philosopher and politician', 'Étienne Bonnot de Condillac': 'French philosopher',
            'Heinrich Scholz': 'German logician and theologian', 'Ludwik Fleck': 'Polish physician and philosopher of science',
            'Ernst Mach': 'Austrian physicist and philosopher', 'James Ward': 'English psychologist and philosopher',
            'Leo Strauss': 'German-American political philosopher', 'Radulphus Brito': 'Medieval philosopher and grammarian'}
LIFE_FIX = {'Galen': (129, 216)}
TRAD_FIX = {'Leo Strauss': 0, 'Gershom Scholem': 0}
GENDER_FIX = {'Q188569': 'male'}   # William Godwin: Wikidata currently says female

def tradition(x):
    if x['label'] in TRAD_FIX: return TRAD_FIX[x['label']]
    own = x['all_slugs'][0] if x['all_slugs'] else None
    f = F.get(own, {}).get('fine', '') if own else ''
    d = (x.get('desc') or '')
    if f == 'Chinese philosophy' or re.search(r'\bChinese\b', d): return 1
    if f == 'Indian & Buddhist philosophy' or re.search(r'\bIndian\b|Buddhis|Hindu|Tibetan', d): return 2
    if f == 'Arabic, Islamic & Jewish philosophy' or re.search(r'Persian|Arab|Islamic|Muslim|Andalus', d): return 3
    if f == 'Japanese philosophy' or re.search(r'Japanese|Korean', d): return 4
    return 0
TRAD = ['Western', 'Chinese', 'Indian & Buddhist', 'Arabic, Islamic & Jewish', 'Japanese & Korean']

def clean_desc(d):
    d = d or ''
    d = re.sub(r'\s*\([^)]*\d[^)]*(\)|$)', '', d)
    d = re.sub(r'\s*\((ca|fl|c|died)\b[^)]*(\)|$)', '', d)
    d = re.sub(r'\s*\(\*[^)]*(\)|$)', '', d)
    d = re.sub(r',?\s*born \d{4}$|\s*\d{3,4}\s*[–-]\s*\d{0,4}$', '', d)
    d = d.strip(' ,;')
    if len(d) > 90:
        d = d[:90].rsplit(' ', 1)[0].rstrip(' ,;') + '…'
    return d

def slugify(t):
    return re.sub(r'[^a-z0-9]+', '-', fold(t).lower()).strip('-')

used = {p['id'] for p in D['P']}
q2p = {p['q']: i for i, p in enumerate(D['P']) if p.get('q')}
H = []
for x in L:
    name = DISPLAY.get(x['label'], x['label'])
    sid = slugify(name)
    pi = q2p.get(x['q'])
    if pi is not None:
        sid = D['P'][pi]['id']           # same profile id as the bibliography list
    else:
        while sid in used:
            sid += '-h'
    used.add(sid)
    ents = [eidx[e] for e in x['ment'] if e in eidx]
    mac = collections.Counter(F[e]['macro'] for e in x['ment'] if e in F)
    fine = collections.Counter(F[e]['fine'] for e in x['ment'] if e in F)
    b, dd = LIFE_FIX.get(x['label'], (x['birth'], x['death']))
    H.append({'id': sid, 'a': name, 'b': b, 'd': dd, 'g': {'female': 'f', 'male': 'm'}.get(GENDER_FIX.get(x['q'], x['gender']), ''),
              'wd': DESC_FIX.get(x['label']) or clean_desc(x.get('desc')), 'q': x['q'], 'wp': x.get('wp'), 'own': x['all_slugs'][:6], 'oe': [eidx[o] for o in x['all_slugs'][:8] if o in eidx],
              'm': len(x['ment']), 'l': len(x['links']), 'tr': tradition(x), 'pi': pi,
              'mac': [mac.get(m, 0) for m in MAC], 'fine': [[FINE.index(f), c] for f, c in fine.most_common(4)], 'e': ents})
H.sort(key=lambda h: (-h['m'], h['a']))
prev = None
for k, h in enumerate(H):
    if h['m'] != prev:
        rr = k + 1; prev = h['m']
    h['r'] = rr
# neighbours: mentioned by the same entries (idf-weighted cosine)
M = np.zeros((len(H), len(D['E'])), dtype=np.float32)
for i, h in enumerate(H):
    M[i, h['e']] = 1
df = M.sum(0) + 1
W = M * np.log(len(H) / df)
W /= (np.linalg.norm(W, axis=1, keepdims=True) + 1e-9)
S = W @ W.T
np.fill_diagonal(S, 0)
for i, h in enumerate(H):
    h['nb'] = [int(j) for j in np.argsort(-S[i])[:6]]
# link bibliography-list people (born before 1900) to their long-canon profile
for i, p in enumerate(D['P']):
    if p['p']:
        hit = next((k for k, h in enumerate(H) if h['pi'] == i), None)
        p['h'] = hit
D['H'] = H
D['TRAD'] = TRAD
D['RACE'] = RACE
json.dump(D, open('page_data_v3.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
import os
print('bytes', os.path.getsize('page_data_v3.json'), 'long canon', len(H), 'linked pre-1900 bib people', sum(1 for p in D['P'] if p['p'] and p.get('h') is not None))
for h in H[:12]:
    print(h['r'], h['m'], h['l'], h['a'], h['b'], TRAD[h['tr']], [H[j]['a'] for j in h['nb'][:4]])
print('traditions', collections.Counter(TRAD[h['tr']] for h in H))
with open('out_before1900.csv', 'w', newline='', encoding='utf-8') as f:
    c = csv.writer(f)
    c.writerow(['rank', 'entries_mentioning', 'entries_linking', 'name', 'born', 'died', 'tradition', 'gender_wikidata', 'sep_entry', 'wikidata'])
    hy = lambda y: '' if y is None else (y if y > 0 else y - 1)   # negative = BCE (no year 0)
    for h in H:
        c.writerow([h['r'], h['m'], h['l'], h['a'], hy(h['b']), hy(h['d']), TRAD[h['tr']], {'f': 'female', 'm': 'male'}.get(h['g'], ''),
                    'https://plato.stanford.edu/entries/%s/' % h['own'][0] if h['own'] else '', h['q']])
