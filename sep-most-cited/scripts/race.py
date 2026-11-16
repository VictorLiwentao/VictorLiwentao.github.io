"""Cumulative citing entries per philosopher by year of the cited work's publication (1900-2026)."""
import json, sys, io, contextlib, importlib.util, collections
sys.path.insert(0, 'scripts')
spec = importlib.util.spec_from_file_location('authors', 'scripts/authors.py')
with contextlib.redirect_stdout(io.StringIO()):
    au = importlib.util.module_from_spec(spec); spec.loader.exec_module(au)
recs = au.recs
D = json.load(open('page_data_v2.json', encoding='utf-8'))
P = D['P']; nC = D['nC']
R = json.load(open('authors_final.json', encoding='utf-8'))
pids = [p['pid'] for p in R['contemporary'] + R['pre1900']]
assert len(pids) == len(P)
idx = {pid: i for i, pid in enumerate(pids)}
# eligible: everyone born 1850 or later (contemporaries + early analytic generation)
elig = {i for i, p in enumerate(P) if (p['b'] or 0) >= 1850 or (not p['p'])}
Y0, Y1 = 1900, 2026
first = collections.defaultdict(dict)   # person -> entry -> first year a cited work of theirs appears
for (ri, ns, s, g), pid in zip(au.occ, au.final_pid):
    i = idx.get(pid)
    if i is None or i not in elig:
        continue
    ys = [y for y in (recs[ri].get('years') or []) if Y0 <= y <= Y1]
    if not ys:
        continue
    y = min(ys)
    e = recs[ri]['entry']
    if e not in first[i] or y < first[i][e]:
        first[i][e] = y
series = {}
for i, ents in first.items():
    c = collections.Counter(ents.values())
    run, arr = 0, []
    for y in range(Y0, Y1 + 1):
        run += c.get(y, 0); arr.append(run)
    series[i] = arr
# keep anyone who is ever in the top 14
keep = set()
for k in range(Y1 - Y0 + 1):
    top = sorted(series, key=lambda i: -series[i][k])[:14]
    keep |= {i for i in top if series[i][k] > 0}
race = [{'i': i, 'c': series[i]} for i in sorted(keep, key=lambda i: -series[i][-1])]
# leader by year and key works by year
leaders = []
for k in range(Y1 - Y0 + 1):
    li = max(series, key=lambda i: series[i][k])
    if not leaders or leaders[-1][1] != li:
        leaders.append((Y0 + k, li))
works = {}
for w in D['W']:
    y = int(str(w['y'])[:4])
    if Y0 <= y <= Y1 and (y not in works or w['n'] > works[y]['n']):
        works[y] = {'t': w['t'], 'a': w['a'].split(' & ')[0], 'n': w['n']}
json.dump({'y0': Y0, 'y1': Y1, 'R': race, 'K': {str(k): v for k, v in sorted(works.items())}}, open('race.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('people in race', len(race))
print('leaders:', [(y, P[i]['a']) for y, i in leaders])
for y in (1920, 1940, 1960, 1980, 2000, 2026):
    k = y - Y0
    print(y, [(P[i]['a'], series[i][k]) for i in sorted(series, key=lambda i: -series[i][k])[:6]])
