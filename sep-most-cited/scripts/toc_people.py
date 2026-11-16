"""Person entries from the SEP table of contents, so the long canon is not limited to people Wikidata links to the SEP.
Heads like 'Descartes, René' (with nested sub-entries) and single names like 'Dai Zhen' are matched to Wikidata by name."""
import json, re, html, pickle, time, requests, collections
from bs4 import BeautifulSoup
slugs = set(l.strip() for l in open('slugs.txt') if l.strip())
T = pickle.load(open('ent_text.pkl', 'rb'))
soup = BeautifulSoup(open('contents.html', encoding='utf-8').read(), 'lxml')

def own_links(li):
    out = []
    for a in li.find_all('a', recursive=False):
        m = re.match(r'entries/([^/]+)/', a.get('href', ''))
        if m and a.find('strong') and m.group(1) in slugs: out.append(m.group(1))
    return out
heads = []
for li in soup.find_all('li'):
    if li.find_parent('li'): continue
    a = li.find('a', recursive=False)
    raw = a.get_text() if a is not None and a.find('strong') and li.contents and (li.contents[0] is a or str(li.contents[0]).strip() == '') else (li.find(string=True, recursive=False) or '')
    head = re.split(r'\s+(?:—|&mdash;)\s*', re.sub(r'\s+', ' ', raw).strip())[0].strip()
    subs = []
    for ul in li.find_all('ul', recursive=False):
        for sli in ul.find_all('li', recursive=False):
            subs += own_links(sli)
    heads.append({'head': head, 'main': own_links(li)[:1], 'slugs': own_links(li)[:1] + subs})

json.dump(heads, open('toc_heads.json', 'w', encoding='utf-8'), ensure_ascii=False)

def to_name(h):
    h = re.sub(r'\s*\[[^\]]*\]', '', h).strip()
    if h.startswith('Aristotle,'): return 'Aristotle'
    if ',' in h:
        sur, given = h.split(',', 1)
        given = given.strip()
        suf = ''
        if re.search(r',\s*(Jr\.|Sr\.)$', given):
            given, suf = re.split(r',\s*', given, 1)[0], ' ' + re.search(r'(Jr\.|Sr\.)$', given).group(1)
        return f'{given} {sur.strip()}{suf}'
    return h
COMMA = re.compile(r"^[A-ZÀ-Ýa-zß’'\-\.\s\[\]]+, [A-ZÀ-Ý]")
NONPERSON = re.compile(r'Philosophy|Theorem|paradox|argument|School|ism\b|ists?\b|Thesis|Dynasty|Enlightenment|Africana|Latinx|Abhidharma|Ikhwān|Darwinism|Cyrenaics|Byzantine|Dialectical', re.I)
cands = []
for h in heads:
    if not h['slugs'] or not h['head'][:1].isupper(): continue
    if COMMA.match(h['head']) or (',' not in h['head'] and not NONPERSON.search(h['head']) and len(h['head'].split()) <= 6):
        cands.append({'head': h['head'], 'name': to_name(h['head']), 'slugs': h['slugs']})
# merge duplicate names (Aristotle general + special topics)
byname = {}
for c in cands:
    o = byname.setdefault(c['name'], {'head': c['head'], 'name': c['name'], 'slugs': []})
    o['slugs'] += [s for s in c['slugs'] if s not in o['slugs']]
cands = list(byname.values())

DATE = re.compile(r'\((?:[^()]{0,40}?)\b(?:c\.|ca\.|b\.|born|fl\.)?\s*(\d{1,4})\s*(?:–|-|—)\s*(?:c\.\s*|d\.\s*)?(\d{1,4})\s*(BCE|BC|B\.C\.E\.|B\.C\.)?')
def pre_dates(c):
    for s in c['slugs'][:3]:
        t = T.get(s, '')[:600]
        m = DATE.search(t)
        if m:
            b, d = int(m.group(1)), int(m.group(2))
            if m.group(3): b, d = 1 - b, 1 - d
            if d < 100 and b > 100: d = int(str(b)[:-len(str(d))] + str(d))   # 1962–65
            return b, d
    return None, None
for c in cands:
    c['pb'], c['pd'] = pre_dates(c)

wd = json.load(open('wd_sep_people.json'))
wd_slugs = {x['sep']['value'] for x in wd}
todo = [c for c in cands if not (set(c['slugs']) & wd_slugs) and not (c['pb'] is not None and c['pb'] >= 1900)]
print(len(heads), 'heads', len(cands), 'person-like', len(todo), 'to look up')

UA = {'User-Agent': 'sep-most-cited/1.0 (https://victorliwentao.github.io/sep-most-cited/)', 'Accept': 'application/sparql-results+json'}
def lookup(names):
    vals = ' '.join('"%s"' % n.replace('"', '') for n in names)
    q = """SELECT ?name ?item ?itemLabel ?itemDescription ?gender ?birth ?death ?article WHERE {
      VALUES ?name { %s }
      SERVICE wikibase:mwapi { bd:serviceParam wikibase:endpoint "www.wikidata.org"; wikibase:api "EntitySearch"; mwapi:search ?name; mwapi:language "en".
        ?item wikibase:apiOutputItem mwapi:item. ?num wikibase:apiOrdinal true. }
      FILTER(?num < 3)
      ?item wdt:P31 wd:Q5 .
      OPTIONAL { ?item wdt:P21 ?g . ?g rdfs:label ?gender . FILTER(lang(?gender)='en') }
      OPTIONAL { ?item wdt:P569 ?birth } OPTIONAL { ?item wdt:P570 ?death }
      OPTIONAL { ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }""" % vals
    for attempt in range(4):
        r = requests.post('https://query.wikidata.org/sparql', data={'query': q, 'format': 'json'}, headers=UA, timeout=300)
        if r.status_code == 200: return r.json()['results']['bindings']
        print('status', r.status_code); time.sleep(70)
    return []
cache = json.load(open('toc_wd_cache.json')) if __import__('os').path.exists('toc_wd_cache.json') else {}
need = [c['name'] for c in todo if c['name'] not in cache]
for i in range(0, len(need), 150):
    batch = need[i:i + 150]
    rows = lookup(batch)
    for n in batch: cache[n] = []
    for r in rows:
        cache[r['name']['value']].append({k: v['value'] for k, v in r.items()})
    json.dump(cache, open('toc_wd_cache.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('batch', i, len(rows)); time.sleep(65 if i + 150 < len(need) else 0)

def yr(v):
    if not v: return None
    m = re.match(r'(-?)(\d+)-', v)
    return (-int(m.group(2)) if m.group(1) else int(m.group(2))) if m else None
from common import fold
out = []
for c in todo:
    hits = cache.get(c['name'], [])
    full = fold(c['name']).lower()
    sur = full.split()[-1]
    by = collections.OrderedDict()
    for h in hits:
        by.setdefault(h['item'], []).append(h)
    best = None
    for rank in (0, 1):
        for item, hs in by.items():
            lab = fold(hs[0].get('itemLabel', '')).lower()
            births = [yr(h.get('birth')) for h in hs if h.get('birth')]
            b = min([x for x in births if x is not None], default=None)
            if b is None or b >= 1900: continue
            if rank == 0 and lab == full: best = (item, hs, b); break
            if rank == 1 and sur in lab and (c['pb'] is None or abs(b - c['pb']) <= 12): best = (item, hs, b); break
        if best: break
    rec = {'name': c['name'], 'head': c['head'], 'slugs': c['slugs'], 'pb': c['pb'], 'pd': c['pd']}
    if best:
        item, hs, b = best
        ds = [yr(h.get('death')) for h in hs if h.get('death')]
        rec.update({'q': item.split('/')[-1], 'label': hs[0].get('itemLabel'), 'desc': hs[0].get('itemDescription', ''),
                    'gender': hs[0].get('gender'), 'wp': hs[0].get('article'), 'birth': b, 'death': max([d for d in ds if d is not None], default=None)})
    out.append(rec)
json.dump(out, open('toc_people.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('matched', sum(1 for o in out if o.get('q')), 'of', len(out))
