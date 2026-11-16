"""Assemble compact page data + CSV exports."""
import json, re, csv, html, collections, sys
sys.path.insert(0, 'scripts')
from common import norm_surname, initial, fold

W = json.load(open('works_final.json', encoding='utf-8'))
D = json.load(open('works_dropped.json', encoding='utf-8'))
PRE = json.load(open('works_pre1900.json', encoding='utf-8'))
R = json.load(open('authors_final.json', encoding='utf-8'))
ALL_A = json.load(open('author_counts.json', encoding='utf-8'))
import importlib.util, io, contextlib
spec = importlib.util.spec_from_file_location('fa', 'scripts/finalize_authors.py')
with contextlib.redirect_stdout(io.StringIO()):
    fa = importlib.util.module_from_spec(spec); spec.loader.exec_module(fa)

# entry titles from the SEP table of contents
toc = open('contents.html', encoding='utf-8').read()
titles = collections.defaultdict(collections.Counter)
for m in re.finditer(r'<a href="entries/([^/"]+)/">(.*?)</a>', toc, re.S):
    t = html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
    t = re.sub(r'\s+', ' ', t)
    if t:
        titles[m.group(1)][t] += 1
slugs = sorted(l.strip() for l in open('slugs.txt') if l.strip())
etitle = {}
for s_ in slugs:
    h = open(f'raw/{s_}.html', encoding='utf-8', errors='ignore').read()
    m = re.search(r'<h1>(.*?)</h1>', h, re.S)
    t = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
    etitle[s_] = re.sub(r'\s+', ' ', t) or (titles[s_].most_common(1)[0][0] if titles[s_] else s_)
eidx = {s: i for i, s in enumerate(slugs)}

# author display names for works
by_base = collections.defaultdict(list)
for a in ALL_A:
    if a['n'] >= 15:
        by_base['|'.join(a['pid'].split('|')[:2])].append(a)

def first_full(g):
    t = [x for x in re.split(r'[\s\.]+', fold(g or '')) if x]
    return t[0].lower() if t and len(t[0]) >= 2 else None

def work_author(w):
    base = norm_surname(w['author_surname']) + '|' + initial(w['author_given'])
    cands = by_base.get(base, [])
    if len(cands) > 1:
        ff = first_full(w['author_given'])
        c2 = [a for a in cands if ff and a['pid'].endswith('|' + ff)]
        cands = c2 or sorted(cands, key=lambda a: -a['n'])[:1]
    if cands:
        return fa.display_name(cands[0])
    return f"{w['author_surname']}, {fa.fmt_given(w['author_given'])}".strip(', ')

def clean_title(t):
    t = t.strip().rstrip(',.;: ')
    t = re.sub(r'\s+([,:;\.\?])', r'\1', t)
    t = re.sub(r'\s+', ' ', t)
    if t.count('‘') > t.count('’'):
        t += '’'
    if t.count('“') > t.count('”'):
        t += '”'
    return t[0].upper() + t[1:] if t else t

TITLE_FIX = {
    'Psychosemantics: The Problem of Meaning in the Philosophy of Mind': 'Psychosemantics',
}
YEAR_FIX = {('Whitehead', 'Principia Mathematica'): '1910–13', ('Husserl', 'Logische Untersuchungen'): '1900–01'}

works = []
for w in W:
    t = clean_title(w['title'])
    co = w.get('coauthors')
    a = work_author(w)
    if co:
        a += ' & ' + ', '.join(co)
    y = YEAR_FIX.get((w['author_surname'], t), w['year'])
    works.append({'r': w['rank'], 'n': w['n'], 'o': w.get('n2024'), 'or': w.get('rank2024'), 'a': a,
                  'y': y, 't': TITLE_FIX.get(t, t), 'e': [eidx[e] for e in w['entries']]})

def pack_author(x, rank_key):
    return {'r': x[rank_key], 'n': x['n'], 'o': x.get('n2024'), 'or': x.get('rank2024'), 'a': x['name'],
            'p': 1 if x['pre1900'] else 0,
            'w': clean_title(x['top_work']['title']) if x.get('top_work') else None,
            'e': [eidx[e] for e in x['entries'] if e in eidx]}

contemp = [pack_author(x, 'rank') for x in R['contemporary']]
pre = [pack_author(x, 'rank_all') for x in R['pre1900']]
# all-era ranks for contemporary authors too
allp = sorted(contemp + pre, key=lambda x: -x['n'])
prev = None
for i, x in enumerate(allp):
    if x['n'] != prev:
        rr = i + 1; prev = x['n']
    x['ra'] = rr

dropped = [{'n': w['n'], 'o': w['n2024'], 'a': work_author(w), 'y': w['year'], 't': 'Real Time / Real Time II' if clean_title(w['title']) == 'Real Time II' else clean_title(w['title'])} for w in D]
dropped.append({'n': 8, 'o': 16, 'a': 'Frege, Gottlob', 'y': 1918, 't': 'The Thought: A Logical Inquiry (German original “Der Gedanke” counted separately: 13)'})
sidg = [x for x in PRE if x['author_surname'] == 'Sidgwick']
total_lines = sum(1 for _ in open('records.jsonl'))
data = {'meta': {'date': '2026-11-16', 'entries': len(slugs), 'lines': total_lines,
                 'n_works': len(works), 'n_auth': len(contemp), 'sidgwick': sidg[0]['n'] if sidg else None},
        'E': [[s, etitle[s]] for s in slugs], 'W': works, 'A': contemp, 'P': pre, 'X': dropped}
json.dump(data, open('page_data.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

with open('out_works.csv', 'w', newline='', encoding='utf-8') as f:
    c = csv.writer(f)
    c.writerow(['rank', 'citing_entries', 'author', 'year', 'title', 'entries_2024', 'rank_2024'])
    for w in works:
        c.writerow([w['r'], w['n'], w['a'], w['y'], w['t'], w['o'] or '', w['or'] or ''])
with open('out_philosophers.csv', 'w', newline='', encoding='utf-8') as f:
    c = csv.writer(f)
    c.writerow(['rank_born_1900_plus', 'rank_all_eras', 'citing_entries', 'name', 'born_before_1900', 'most_cited_work', 'entries_2024', 'rank_2024'])
    for x in sorted(contemp + pre, key=lambda x: x['ra']):
        c.writerow([x['r'] if not x['p'] else '', x['ra'], x['n'], x['a'], 'yes' if x['p'] else '', x['w'] or '', x['o'] or '', x['or'] or ''])
import os
print('page_data.json', os.path.getsize('page_data.json'), 'bytes;', len(works), 'works;', len(contemp), 'contemp;', len(pre), 'pre1900')
for w in works[:12]: print(w['r'], w['n'], w['o'], w['a'], w['y'], w['t'])
for x in contemp[:12]: print(x['r'], x['n'], x['o'], x['a'], '|', x['w'])
