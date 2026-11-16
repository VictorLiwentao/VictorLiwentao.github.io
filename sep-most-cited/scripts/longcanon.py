"""Philosophers with their own SEP entry: count entries that link to / mention them."""
import json, re, html, collections, sys, os
sys.path.insert(0, 'scripts')
from common import fold

r = json.load(open('wd_sep_people.json'))
slugs = [l.strip() for l in open('slugs.txt') if l.strip()]
sset = set(slugs)
toc = open('contents.html', encoding='utf-8').read()

def year(v):
    if not v: return None
    m = re.match(r'(-?)(\d+)-', v)
    if not m: return None
    return -int(m.group(2)) if m.group(1) else int(m.group(2))

people = {}
for x in r:
    g = lambda k: x.get(k, {}).get('value')
    q = g('item').split('/')[-1]
    p = people.setdefault(q, {'q': q, 'label': g('label'), 'desc': g('desc') or '', 'birth': None, 'death': None,
                               'gender': g('gender'), 'wp': g('article'), 'slugs': set()})
    if g('sep') in sset:
        p['slugs'].add(g('sep'))
    b, d = year(g('birth')), year(g('death'))
    if b is not None and (p['birth'] is None or b < p['birth']): p['birth'] = b
    if d is not None and (p['death'] is None or d > p['death']): p['death'] = d
# people with an SEP entry that Wikidata does not link to the SEP (matched by name from the table of contents)
for o in json.load(open('toc_people.json', encoding='utf-8')):
    if o.get('q') and o['q'] not in people:
        people[o['q']] = {'q': o['q'], 'label': o['label'], 'desc': o.get('desc') or '', 'birth': o['birth'], 'death': o['death'],
                          'gender': o.get('gender'), 'wp': o.get('wp'), 'slugs': set(o['slugs'])}
people = {q: p for q, p in people.items() if p['slugs']}

# sub-entries from the table of contents: "Surname, Given: topic" -> person whose main entry is "Surname, Given"
toc_text = collections.defaultdict(set)
for m in re.finditer(r'<a href="entries/([^/"]+)/">(.*?)</a>', toc, re.S):
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))).strip()
    toc_text[m.group(1)].add(t)
main_name = {}
for q, p in people.items():
    for s in p['slugs']:
        for t in toc_text.get(s, ()):
            if ':' not in t and t[:1].isupper():
                main_name[t] = q
owner = {}
for q, p in people.items():
    for s in p['slugs']:
        owner[s] = q
for s, ts in toc_text.items():
    if s in owner: continue
    for t in ts:
        if ':' in t:
            head = t.split(':')[0].strip()
            if head in main_name:
                owner[s] = main_name[head]
# nested sub-entries in the table of contents belong to the person in the head
HEADS = json.load(open('toc_heads.json', encoding='utf-8'))
PERSON_HEAD = re.compile(r"^[A-ZÀ-Ýa-zß’'\-\.\s\[\]]+, [A-ZÀ-Ý]")
for hd in HEADS:
    qs = {owner[s] for s in hd['slugs'] if s in owner}
    if len(qs) != 1: continue
    q = next(iter(qs))
    if (hd['main'] and owner.get(hd['main'][0]) == q) or (PERSON_HEAD.match(hd['head']) and hd['head'][:1].isupper()):
        for s in hd['slugs']:
            owner.setdefault(s, q)
for q, p in people.items():
    p['all_slugs'] = sorted(s for s, o in owner.items() if o == q)
    p['heads'] = [hd['head'] for hd in HEADS if set(hd['slugs']) & set(p['all_slugs'])]
# birth/death from the entry's own opening line when Wikidata has none
import pickle
TT = pickle.load(open('ent_text.pkl', 'rb'))
DATE = re.compile(r'\((?:[^()]{0,40}?)\b(?:c\.|ca\.|b\.|born|fl\.)?\s*(\d{1,4})\s*(?:–|-|—)\s*(?:c\.\s*|d\.\s*)?(\d{1,4})\s*(BCE|BC|B\.C\.E\.|B\.C\.)?')
FL = re.compile(r'\(\s*(?:fl\.|flourished|active)\s*(?:c\.\s*)?(\d{3,4})')
for q, p in people.items():
    if p['birth'] is None:
        for s in p['all_slugs'][:3]:
            t = TT.get(s, '')[:600]
            m = DATE.search(t)
            if m:
                b, d = int(m.group(1)), int(m.group(2))
                if m.group(3): b, d = 1 - b, 1 - d
                if b <= d: p['birth'], p['death'], p['date_src'] = b, d, 'sep'; break
            m = FL.search(t)
            if m:
                p['birth'], p['date_src'] = int(m.group(1)) - 30, 'sep-fl'; break

# links and text per entry
LINK = re.compile(r'href="(?:\.\./|/entries/|https?://plato\.stanford\.edu/entries/)([a-z0-9][a-z0-9\-]*)/?(?:index\.html)?(?:#[^"]*)?"', re.I)
def main_text(h):
    i = h.find('id="preamble"'); i = i if i >= 0 else h.find('id="main-text"')
    j = h.find('id="bibliography"', i)
    seg = h[i:j if j > 0 else len(h)]
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', seg)))
def content(h):
    i = h.find('id="preamble"'); i = i if i >= 0 else h.find('id="aueditable"')
    j = h.find('id="article-copyright"'); j = j if j > 0 else len(h)
    return h[max(i, 0):j]

ent_links, ent_text = {}, {}
for s in slugs:
    h = open(f'raw/{s}.html', encoding='utf-8', errors='ignore').read()
    ent_links[s] = {m.group(1).lower() for m in LINK.finditer(content(h))} - {s}
    ent_text[s] = main_text(h)

# name patterns for mentions
AMBIG = {'Mill': r'\b(?:J\.\s?S\.\s?Mill|John Stuart Mill|Mill(?:’|\')s|Mill)\b', 'James': r'\bWilliam James\b|\bJames(?:’|\')s? (?:Principles|Pragmatism|Varieties|Will to Believe)',
         'Smith': r'\bAdam Smith\b', 'Bacon': None, 'More': None, 'Butler': r'\bJoseph Butler\b|\bBishop Butler\b', 'Price': r'\bRichard Price\b',
         'Green': r'\bT\.\s?H\.\s?Green\b|\bThomas Hill Green\b', 'Reid': r'\bThomas Reid\b|\bReid\b', 'Wolff': r'\bChristian Wolff\b|\bWolff\b',
         'Cohen': r'\bHermann Cohen\b', 'Mead': r'\bGeorge Herbert Mead\b|\bG\.\s?H\.\s?Mead\b', 'Stewart': r'\bDugald Stewart\b',
         'Edwards': r'\bJonathan Edwards\b', 'Clarke': r'\bSamuel Clarke\b', 'Collins': r'\bAnthony Collins\b', 'Ferguson': r'\bAdam Ferguson\b',
         'Taylor': r'\bHarriet Taylor\b', 'Lewis': None, 'Russell': None, 'Moore': None, 'Mach': r'\bErnst Mach\b|\bMach(?:’|\')s\b|\bMach\b(?! number)'}
def pattern(p):
    lab = p['label'] or ''
    toks = lab.split()
    sur = toks[-1] if toks else lab
    # names like "Thomas Aquinas", "William of Ockham", "Ibn Sina", "al-Farabi"
    if ' of ' in lab or lab.startswith(('Ibn ', 'al-', 'Al-')) or len(toks) == 1:
        sur = lab
    special = {'Thomas Aquinas': r'\bAquinas\b', 'William of Ockham': r'\bOckham\b', 'Augustine of Hippo': r'\bAugustine\b',
               'Anselm of Canterbury': r'\bAnselm\b', 'Avicenna': r'\bAvicenna\b|\bIbn S[iī]n[aā]\b', 'Averroes': r'\bAverroes\b|\bIbn Rushd\b',
               'Al-Farabi': r'\bal-F[aā]r[aā]b[iī]\b|\bAlfarabi\b', 'Baruch Spinoza': r'\bSpinoza\b', 'René Descartes': r'\bDescartes\b',
               'Gottfried Wilhelm Leibniz': r'\bLeibniz\b', 'Georg Wilhelm Friedrich Hegel': r'\bHegel\b', 'Plato': r'\bPlato\b',
               'Aristotle': r'\bAristotle\b', 'Confucius': r'\bConfucius\b', 'John Duns Scotus': r'\bScotus\b',
               'Francis Bacon': r'\bFrancis Bacon\b', 'Roger Bacon': r'\bRoger Bacon\b', 'Thomas More': r'\bThomas More\b', 'Henry More': r'\bHenry More\b',
               'Bertrand Russell': r'\bRussell\b', 'G. E. Moore': r'\bG\.\s?E\.\s?Moore\b|\bMoore(?:’|\')s\b|\bMoore\b',
               'C. I. Lewis': r'\bC\.\s?I\.\s?Lewis\b', 'Clarence Irving Lewis': r'\bC\.\s?I\.\s?Lewis\b'}
    if lab in special:
        return special[lab]
    if sur in AMBIG:
        return AMBIG[sur]
    return r'\b' + re.escape(sur) + r'\b'

out = []
for q, p in people.items():
    own = set(p['all_slugs'])
    links = {e for e, ls in ent_links.items() if e not in own and ls & own}
    pat = pattern(p)
    ment = set()
    if pat:
        rx = re.compile(pat)
        ment = {e for e, t in ent_text.items() if e not in own and rx.search(t)}
    out.append({**{k: v for k, v in p.items() if k != 'slugs'}, 'links': sorted(links), 'ment': sorted(ment), 'pat': pat})
out.sort(key=lambda x: -len(x['ment']))
json.dump(out, open('longcanon_raw.json', 'w', encoding='utf-8'), ensure_ascii=False)
pre = [x for x in out if x['birth'] is not None and x['birth'] < 1900]
print('people', len(out), 'born<1900', len(pre), 'no birth', sum(1 for x in out if x['birth'] is None))
for x in pre[:60]:
    print(f"{len(x['ment']):4} ment {len(x['links']):4} links  {x['label']} ({x['birth']}) subs={len(x['all_slugs'])}")
print('no birth:', [x['label'] for x in out if x['birth'] is None])
