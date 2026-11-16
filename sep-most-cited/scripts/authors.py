"""Count, for each author, the number of SEP main entries citing them
(first, second or last author, or editor named before the date)."""
import json, re, collections, sys
sys.path.insert(0, 'scripts')
from common import norm_surname, initial, fold, norm_title_tokens

recs = [json.loads(l) for l in open('records.jsonl', encoding='utf-8')]

NICK = {'terry': 'terence', 'ernie': 'ernest', 'fred': 'frederick', 'ted': 'theodore', 'bill': 'william',
        'bob': 'robert', 'rob': 'robert', 'jim': 'james', 'tim': 'timothy', 'tom': 'thomas', 'dick': 'richard',
        'mike': 'michael', 'chris': 'christopher', 'dan': 'daniel', 'dave': 'david', 'steve': 'stephen',
        'steven': 'stephen', 'jerrold': 'jerry', 'nick': 'nicholas', 'ken': 'kenneth', 'matt': 'matthew',
        'greg': 'gregory', 'josh': 'joshua', 'andy': 'andrew', 'tony': 'anthony', 'sandy': 'sandra',
        'liz': 'elizabeth', 'beth': 'elizabeth', 'pat': 'patricia', 'jon': 'jonathan', 'joe': 'joseph',
        'sam': 'samuel', 'alex': 'alexander', 'ben': 'benjamin', 'phil': 'philip', 'phillip': 'philip',
        'fredrick': 'frederick', 'frederic': 'frederick', 'rudolph': 'rudolf', 'hilary': 'hilary', 'jaakko': 'jaakko',
        'sally': 'sally', 'kit': 'kit', 'ned': 'ned', 'jc': 'jc'}

def first_full(given):
    """First given-name token that is a full name (not an initial)."""
    toks = [t for t in re.split(r'[\s\.]+', fold(given or '')) if t.strip("-'")]
    toks = [t for t in toks if t.lower() not in ('de', 'van', 'von', 'der', 'la', 'le', 'da', 'du', 'st')]
    if not toks:
        return None
    t = toks[0].strip("-'").lower()
    if len(t) >= 2 and t.replace('-', '').isalpha() and not re.fullmatch(r'[a-z]-[a-z]', t):
        return NICK.get(t, t)
    return None

BAD_AUTH = re.compile(r'University|Press|Verlag|Editions|\u00c9ditions|Publishers|Publishing|Clarendon|Routledge|Blackwell|Springer|Oxford:|Cambridge:|:|\d')

def remap(s, g, ns):
    if ns == 'appiah': return s, 'Kwame Anthony', ns
    if ns == 'grice': return s, 'H. Paul', ns
    if ns == 'velleman': return s, 'J. David', ns
    if ns == 'mellor' and re.match(r'^(D|H)', g or ''): return s, 'D. H.', ns
    if ns == 'maynardsmith' or (ns == 'smith' and 'Maynard' in (g or '')): return 'Maynard Smith', 'John', 'maynardsmith'
    if ns == 'smith' and (g or '').strip() in ('J. Maynard', 'J.Maynard'): return 'Maynard Smith', 'John', 'maynardsmith'
    return s, g, ns

# occurrences: (rec_idx, surname, given)
occ = []
for i, r in enumerate(recs):
    au = r.get('authors') or []
    if not au or r.get('trans_only'):
        continue
    if BAD_AUTH.search(r.get('raw_auth') or ''):
        continue
    pos = [0]
    if len(au) >= 2: pos.append(1)
    if len(au) >= 3: pos.append(len(au) - 1)
    for p in pos:
        s, g = au[p]
        ns = norm_surname(s)
        s, g, ns = remap(s, g, ns)
        if not ns or len(ns) < 2 or len(s) > 40:
            continue
        occ.append((i, ns, s.strip(), g.strip()))

# per surname+initial, count full first names
full_by_key = collections.defaultdict(collections.Counter)
for i, ns, s, g in occ:
    k = ns + '|' + initial(g)
    f = first_full(g)
    if f:
        full_by_key[k][f] += 1
        if initial(g) != f[0]:
            pass

import difflib

# manual identity rules: (key, regex on given name, optional title regex) -> person suffix
MANUAL = [
    ('taylor|c', r'^C\.?\s*C', None, 'ccw'),
    ('lewis|c', r'^C\.?\s*S\b|^C\.S|^Clive', None, 'cs'),
    ('singer|p', r'^P(eter)?\.?\s*N', None, 'pn'),
    ('hilbert|d', r'^D(avid)?\.?\s*R', None, 'dr'),
    ('goodman|n', r'^N(icolas)?\.?\s*D', None, 'nd'),
    ('price|h', r'^H\.?\s*H|^Henry', None, 'hh'),
    ('lloyd|g', r'^G\.?\s*E|^Geoffrey', None, 'ger'),
    ('bell|j', r'^J(ohn)?\.?\s*S\b|^J\.S', None, 'js'),
    ('bell|j', r'^J(ohn)?\.?\s*L\b|^J\.L', None, 'jl'),
    ('smith|n', r'^N(icholas)?\.?\s*J', None, 'njj'),
    ('smith|n', r'^N(icholas)?\.?\s*D', None, 'nd'),
    ('martin|m', r'G\.?\s*F|^M\.?\s*G', None, 'mgf'),
    ('taylor|r', r'^R(ichard)?\.?\s*C', None, 'rc'),
    ('allen|j', r'^J(ames)?\.?\s*F', None, 'jf'),
    ('moore|g', r'^G(regory)?\.?\s*H|^Gregory', None, 'gh'),
    ('austin|j', r'.*', r'jurisprudence|province|lectures on', 'jurist'),
    ('kitcher|p', r'^Patricia', None, 'patricia'),
    ('kaplan|d', r'^D(avid)?\.?\s*M', None, 'dm'),
    ('griffiths|p', r'^P(aul)?\.?\s*J', None, 'pj'),
    ('craig|w', r'^(?!.*\bL(ane)?\b)', None, 'logician'),
    ('miller|d', r'.*', r'verisimilitude|popper|critical rationalism|out of error|propensit|false theor|paradox of information', 'popperian'),
    ('miller|d', r'^(D\.?|Dale.*)$', r'rule consequentialism|reflective equilibr|john stuart mill|moral education|\bmill\b', 'dale'),
    ('scott|d', r'^(D\.?|Dominic.*)$', r'plato|aristotl|recollection|anamnesis|socrat|levels of argument|thrasymach|well being|posthumous|listening to reason', 'dominic'),
]

def manual_pid(k, g, title):
    for mk, greg, treg, suf in MANUAL:
        if mk == k and re.search(greg, g or '') and (treg is None or re.search(treg, fold(title or ''), re.I)):
            return k + '|' + suf
    return None

# fuzzy-merge variant spellings of full first names within a key
alias = {}
for k, c in full_by_key.items():
    names = [n for n, _ in c.most_common()]
    for i, n in enumerate(names):
        for m in names[:i]:
            if alias.get(m, m) != m:
                continue
            if difflib.SequenceMatcher(None, n, m).ratio() >= 0.8 and n[:2] == m[:2]:
                alias[(k, n)] = m; break
merged_full = collections.defaultdict(collections.Counter)
for k, c in full_by_key.items():
    for n, v in c.items():
        merged_full[k][alias.get((k, n), n)] += v

def canon_full(k):
    c = merged_full.get(k)
    if not c:
        return None, False
    tot = sum(c.values())
    (f1, n1), *rest = c.most_common()
    amb = bool(rest) and rest[0][1] >= 3 and rest[0][1] / tot >= 0.02
    return f1, amb

def ffull(k, g):
    f = first_full(g)
    return alias.get((k, f), f) if f else None

def initials_after_first(g):
    toks = [t for t in re.split(r'[\s\.]+', fold(g or '')) if t]
    return [t[0].lower() for t in toks[1:] if t[0].isalpha()]

# middle initials seen for each full-name person
mids = collections.defaultdict(collections.Counter)
person_titles = collections.defaultdict(set)
entry_people = collections.defaultdict(lambda: collections.defaultdict(set))
for i, ns, s, g in occ:
    k = ns + '|' + initial(g)
    f = ffull(k, g)
    if f and not manual_pid(k, g, recs[i].get('title')):
        for x in initials_after_first(g)[:1]:
            mids[(k, f)][x] += 1
        person_titles[(k, f)].add(' '.join(norm_title_tokens(recs[i].get('title'))[:4]))
        entry_people[recs[i]['entry']][k].add(f)

pid_of_occ = []
unresolved = collections.Counter()
for i, ns, s, g in occ:
    ini = initial(g)
    k = ns + '|' + ini
    mp = manual_pid(k, g, recs[i].get('title'))
    if mp:
        pid_of_occ.append(mp); continue
    f = ffull(k, g)
    f1, amb = canon_full(k)
    if not amb:
        pid_of_occ.append(k); continue
    if f:
        pid_of_occ.append(k + '|' + f); continue
    cands = merged_full[k]
    pid = None
    # 1. middle-initial signature
    sig = initials_after_first(g)
    if sig:
        hits = {ff: mids[(k, ff)][sig[0]] for ff in cands if mids[(k, ff)][sig[0]] >= 1}
        if hits:
            best = max(hits, key=hits.get)
            if hits[best] / sum(hits.values()) >= 0.8:
                pid = k + '|' + best
    # 1b. goes by a middle name (e.g. "J. Adam"): own identity when no full-name match
    if pid is None:
        toks = [t for t in re.split(r'[\s\.]+', fold(g or '')) if t]
        if len(toks) >= 2 and len(toks[1]) >= 2 and toks[1].isalpha():
            pid = k + '|~' + toks[1].lower()
    # 2. same-entry evidence
    if pid is None:
        seen = entry_people[recs[i]['entry']].get(k, set())
        if len(seen) == 1:
            pid = k + '|' + next(iter(seen))
    # 3. title evidence
    if pid is None:
        t = ' '.join(norm_title_tokens(recs[i].get('title'))[:4])
        hits = [ff for ff in cands if t and t in person_titles[(k, ff)]]
        if len(hits) == 1:
            pid = k + '|' + hits[0]
    # 4. dominance
    if pid is None:
        tot = sum(cands.values())
        if cands[f1] / tot >= 0.7:
            pid = k + '|' + f1
        else:
            unresolved[k] += 1
    pid_of_occ.append(pid)

# blank-initial ids: merge into dominant initial for the surname when dominant >= 80%
sur_ini = collections.defaultdict(collections.Counter)
for (i, ns, s, g), pid in zip(occ, pid_of_occ):
    if pid and initial(g):
        sur_ini[ns][pid] += 1
final_pid = []
for (i, ns, s, g), pid in zip(occ, pid_of_occ):
    if pid and not initial(g):
        c = sur_ini.get(ns)
        if c:
            top, n = c.most_common(1)[0]
            if n / sum(c.values()) >= 0.8:
                pid = top
    final_pid.append(pid)

people = collections.defaultdict(lambda: {'entries': set(), 'names': collections.Counter(), 'lines': 0, 'years': collections.Counter()})
for (i, ns, s, g), pid in zip(occ, final_pid):
    if not pid:
        continue
    P = people[pid]
    P['entries'].add(recs[i]['entry'])
    P['names'][(s, g)] += 1
    P['lines'] += 1
    y = recs[i].get('years') or []
    if y:
        P['years'][min(y)] += 1

out = []
for pid, P in people.items():
    n = len(P['entries'])
    if n < 15:
        continue
    yrs = P['years']
    out.append({'pid': pid, 'n': n, 'lines': P['lines'],
                'names': [[a, b, c] for (a, b), c in P['names'].most_common(6)],
                'year_min': min(yrs) if yrs else None,
                'year_p10': sorted(yrs.elements())[len(list(yrs.elements())) // 10] if yrs else None,
                'entries': sorted(P['entries'])})
out.sort(key=lambda x: -x['n'])
json.dump(out, open('author_counts.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('authors with >=15 entries:', len(out))
print('unresolved ambiguous initial-only occurrences (top):', unresolved.most_common(15))
for a in out[:80]:
    print(a['n'], a['pid'], a['names'][0][:2], a['year_p10'])
