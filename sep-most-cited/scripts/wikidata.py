"""Match ranked authors to Wikidata people via exact label/alias SPARQL lookups."""
import json, re, time, sys, os, collections, urllib.parse, urllib.request
sys.path.insert(0, 'scripts')
from common import fold

UA = 'SEP-citation-study/1.0 (research; https://github.com/VictorLiwentao)'
R = json.load(open('authors_final.json', encoding='utf-8'))
AC = {a['pid']: a for a in json.load(open('author_counts.json', encoding='utf-8'))}
people = R['contemporary'] + R['pre1900']

def variants(p):
    s, _, g = p['name'].partition(', ')
    out = set()
    def add(given, sur):
        given = given.strip(); sur = sur.strip()
        if not sur: return
        full = f'{given} {sur}'.strip()
        out.add(full)
        # initials spaced / unspaced
        out.add(re.sub(r'\.\s+(?=[A-Z]\.)', '.', full))
        toks = given.split()
        if toks:
            # first name only
            if len(toks[0]) > 2 and not toks[0].endswith('.'):
                out.add(f'{toks[0]} {sur}')
            # drop middle initials
            keep = [t for t in toks if not re.fullmatch(r'[A-Z]\.', t)]
            if keep and keep != toks:
                out.add(' '.join(keep + [sur]))
    add(g, s)
    a = AC.get(p['pid'])
    if a:
        for sur, giv, c in a['names'][:6]:
            if giv and len(giv) < 40 and len(sur) < 40:
                gv = re.sub(r'\b([A-Z])(?=\s|$)', r'\1.', giv)
                add(gv, sur)
    if not g:
        out.add(s)
    return sorted(v for v in out if len(v) > 3)

def sparql(q):
    url = 'https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': q, 'format': 'json'})
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/sparql-results+json'})
            return json.load(urllib.request.urlopen(req, timeout=70))['results']['bindings']
        except Exception as e:
            print('retry', attempt, e, flush=True); time.sleep(float(os.environ.get('SLEEP', 4)))
    return None

Q = '''SELECT ?name ?item ?label ?desc ?birth ?death ?gender ?article WHERE {
 VALUES ?name { %s }
 ?item rdfs:label|skos:altLabel ?name .
 ?item wdt:P31 wd:Q5 .
 OPTIONAL { ?item rdfs:label ?label FILTER(lang(?label)="en") }
 OPTIONAL { ?item schema:description ?desc FILTER(lang(?desc)="en") }
 OPTIONAL { ?item wdt:P569 ?birth }
 OPTIONAL { ?item wdt:P570 ?death }
 OPTIONAL { ?item wdt:P21 ?g . ?g rdfs:label ?gender FILTER(lang(?gender)="en") }
 OPTIONAL { ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> }
 }'''

name_to_people = collections.defaultdict(set)
for i, p in enumerate(people):
    for v in variants(p):
        name_to_people[v].add(i)
names = sorted(name_to_people)
print('people', len(people), 'name variants', len(names), flush=True)

import os
cands = collections.defaultdict(dict)  # person idx -> qid -> info
B = int(os.environ.get('B', 40))
LIMIT = int(os.environ.get('LIMIT', 10**9))
cache = {}
if os.path.exists('wd_names.jsonl'):
    for line in open('wd_names.jsonl'):
        x = json.loads(line); cache[x['n']] = x['rows']
cf = open('wd_names.jsonl', 'a')
todo = [n for n in names if n not in cache]
if os.environ.get('PRIORITY'):
    # only people with no candidate yet; their two most likely name forms
    have = set()
    for n, rows in cache.items():
        if rows:
            have |= name_to_people.get(n, set())
    todo = []
    for i, p in enumerate(people):
        if i in have:
            continue
        s_, _, g_ = p['name'].partition(', ')
        prim = [f"{g_} {s_}".strip()]
        toks = [t for t in g_.split() if not re.fullmatch(r'[A-Z]\.', t)]
        if toks and toks != g_.split():
            prim.append(' '.join(toks + [s_]))
        for v in variants(p)[:6]:
            if len(prim) < 3 and v not in prim:
                prim.append(v)
        todo += [v for v in prim if v not in cache and v not in todo]
print('todo', len(todo), flush=True)
for k in range(0, min(len(todo), LIMIT), B):
    chunk = todo[k:k + B]
    t0 = time.time()
    got = sparql(Q % ' '.join('"%s"@en' % n.replace('"', '') for n in chunk))
    if got is None:
        print('failed batch', k, flush=True); continue
    by = collections.defaultdict(list)
    for r in got: by[r['name']['value']].append(r)
    for n in chunk:
        cache[n] = by.get(n, []); cf.write(json.dumps({'n': n, 'rows': cache[n]}) + '\n')
    cf.flush()
    print(k, len(got), round(time.time() - t0, 1), 's', flush=True)
    time.sleep(float(os.environ.get('SLEEP', 1)))
for n in names:
    rows = cache.get(n, [])
    for r in rows:
        n = r['name']['value']; qid = r['item']['value'].rsplit('/', 1)[1]
        info = {'qid': qid, 'label': r.get('label', {}).get('value'), 'desc': r.get('desc', {}).get('value', ''),
                'birth': r.get('birth', {}).get('value', '')[:5], 'death': r.get('death', {}).get('value', '')[:5],
                'gender': r.get('gender', {}).get('value'), 'article': r.get('article', {}).get('value'),
                'occs': r.get('occs', {}).get('value', '')}
        for i in name_to_people[n]:
            prev = cands[i].get(qid)
            if prev:
                # keep the earliest birth if multiple values
                if info['birth'] and (not prev['birth'] or info['birth'] < prev['birth']):
                    prev['birth'] = info['birth']
                if info['death'] and not prev['death']:
                    prev['death'] = info['death']
            else:
                cands[i][qid] = info

json.dump({'people': people, 'cands': {str(i): c for i, c in cands.items()}}, open('wd_raw.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('people with candidates', len(cands))
