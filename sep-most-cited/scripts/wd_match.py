"""Pick the best Wikidata candidate for each person; flag uncertain matches."""
import json, re, sys, collections
D = json.load(open('wd_raw.json', encoding='utf-8'))
AC = {a['pid']: a for a in json.load(open('author_counts.json', encoding='utf-8'))}
OVR = json.load(open('wd_overrides.json')) if len(sys.argv) > 1 else {}
people = D['people']; cands = D['cands']

STRONG = r'philosoph|logician|ethicist|metaphysician|epistemolog'
MID = r'mathematician|economist|psycholog|linguist|physicist|computer scientist|political (theorist|scientist)|cognitive|game theor|statistician|decision theor'
WEAK = r'scholar|historian|classicist|philologist|sinolog|indolog|buddholog|theolog|jurist|legal|lawyer|sociolog|biolog|anthropolog|scientist|academic|professor|writer|author|essayist|critic|orientalist|islamicist|arabist|translator|educator|feminist|activist|musicolog|semiotic'
BAD = r'footballer|actor|actress|singer|musician|politician|painter|basketball|cricketer|rugby|athlete|racing|baseball|soccer|golfer|boxer|guitarist|rapper|swimmer|businessman|hockey|wrestler|model|bishop|priest|footballer'

def score(c, p):
    a = AC.get(p['pid'], {})
    d = (c.get('desc') or '').lower()
    s = 0
    if re.search(STRONG, d): s += 6
    elif re.search(MID, d): s += 3
    elif re.search(WEAK, d): s += 2
    if re.search(BAD, d): s -= 6
    if c.get('article'): s += 1
    b = c.get('birth')
    ref = a.get('year_p10') or a.get('year_min')
    if b and b.lstrip('-').isdigit() and ref:
        by = int(b)
        gap = ref - by
        s += 4 if 18 <= gap <= 95 else -6
    elif not b:
        s -= 1
    return s

res = {}
flag = []
for i, p in enumerate(people):
    cs = list((cands.get(str(i)) or {}).values())
    if p['pid'] in OVR:
        q = OVR[p['pid']]
        if q is None:
            res[p['pid']] = None; continue
        pick = next((c for c in cs if c['qid'] == q), {'qid': q, 'manual': True})
        res[p['pid']] = pick; continue
    if not cs:
        res[p['pid']] = None; flag.append((p['n'], p['name'], 'NO CANDIDATES', [])); continue
    sc = sorted(((score(c, p), c) for c in cs), key=lambda t: -t[0])
    best, c = sc[0]
    res[p['pid']] = c if best >= 3 else None
    close = len(sc) > 1 and sc[1][0] >= best - 1
    if best < 7 or close:
        flag.append((p['n'], p['name'], f'best={best}', [(s, x['qid'], x.get('label'), x.get('desc', '')[:60], x.get('birth')) for s, x in sc[:3]]))
json.dump(res, open('wd_matched.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('matched', sum(1 for v in res.values() if v), 'of', len(res), '; flagged', len(flag))
for f in sorted(flag, key=lambda t: -t[0]):
    print(f[0], f[1], f[2]); [print('     ', x) for x in f[3]]
