"""Per-person profile data: field mix, top works, co-cited neighbours, 2D co-citation map."""
import json, sys, io, contextlib, importlib.util, collections, re
import numpy as np
sys.path.insert(0, 'scripts')
from common import norm_surname

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    with contextlib.redirect_stdout(io.StringIO()):
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

au = load('authors', 'scripts/authors.py')
wk = load('works', 'scripts/works.py')
recs = au.recs
R = json.load(open('authors_final.json', encoding='utf-8'))
F = json.load(open('entry_fields.json'))
people = R['contemporary'] + R['pre1900']
pids = [p['pid'] for p in people]
pidx = {p: i for i, p in enumerate(pids)}

# first-author pid per record
first_pid = {}
for (i, ns, s, g), pid in zip(au.occ, au.final_pid):
    if i in first_pid:
        continue
    a0 = recs[i]['authors'][0]
    if norm_surname(a0[0]) == ns or (ns == 'maynardsmith'):
        first_pid[i] = pid
    else:
        first_pid[i] = None

def disp_year(idxs):
    yrs = collections.Counter(min(recs[i]['years']) for i in idxs if recs[i].get('years'))
    tot = sum(yrs.values())
    for y in sorted(yrs):
        if yrs[y] / tot >= 0.15:
            return y
    return None

def clean(t):
    t = re.sub(r'\s+', ' ', t.strip().rstrip(',.;: '))
    if t.count('‘') > t.count('’'): t += '’'
    if t.count('“') > t.count('”'): t += '”'
    return t[:1].upper() + t[1:]

works_by = collections.defaultdict(list)
for cl in wk.clusters:
    byp = collections.defaultdict(list)
    for i in cl['idxs']:
        p = first_pid.get(i)
        if p in pidx:
            byp[p].append(i)
    for p, idxs in byp.items():
        ents = {recs[i]['entry'] for i in idxs}
        if len(ents) >= 3:
            title = collections.Counter(clean(recs[i]['title']) for i in idxs).most_common(1)[0][0]
            works_by[p].append({'t': title, 'y': disp_year(idxs), 'n': len(ents)})

# person x entry matrix
ents = sorted(F)
eidx = {e: j for j, e in enumerate(ents)}
M = np.zeros((len(people), len(ents)), dtype=np.float32)
for i, p in enumerate(people):
    for e in p['entries']:
        if e in eidx:
            M[i, eidx[e]] = 1
# idf weighting of entries (entries citing many listed people count less)
df = M.sum(0) + 1
W = M * np.log(len(people) / df)
Wn = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-9)
S = Wn @ Wn.T
np.fill_diagonal(S, 0)

MAC = ['Ethics', 'Social & political', 'Metaphysics & epistemology', 'Mind & language', 'Logic & mathematics',
       'Science', 'History & traditions', 'Aesthetics']
out = []
for i, p in enumerate(people):
    mac = collections.Counter(F[e]['macro'] for e in p['entries'] if e in F)
    fine = collections.Counter(F[e]['fine'] for e in p['entries'] if e in F)
    nb = [int(j) for j in np.argsort(-S[i])[:8] if S[i, j] > 0]
    tw = sorted(works_by.get(p['pid'], []), key=lambda w: -w['n'])[:5]
    out.append({'pid': p['pid'], 'mac': [mac.get(m, 0) for m in MAC], 'fine': fine.most_common(5), 'nb': nb[:6], 'works': tw})

# 2D map of contemporary authors (UMAP on the idf-weighted citation profiles)
import umap
nC = len(R['contemporary'])
emb = umap.UMAP(n_neighbors=12, min_dist=0.35, spread=1.2, metric='cosine', random_state=7).fit_transform(Wn[:nC])
emb = (emb - emb.min(0)) / (emb.max(0) - emb.min(0))
for i in range(nC):
    out[i]['xy'] = [round(float(emb[i, 0]), 4), round(float(emb[i, 1]), 4)]
json.dump({'MAC': MAC, 'people': out}, open('profiles.json', 'w', encoding='utf-8'), ensure_ascii=False)
# report
for i in [0, 1, 2, 3, 8, 13]:
    p = people[i]; o = out[i]
    print(p['name'], dict(zip(MAC, o['mac'])), [people[j]['name'] for j in o['nb']], o['works'][:3])
