import json, re, collections, sys
sys.path.insert(0, 'scripts')
from common import norm_surname, initial, fold

A = json.load(open('author_counts.json', encoding='utf-8'))
W = json.load(open('work_clusters.json', encoding='utf-8'))
THRESH = 30

# born before 1900 (Schwitzgebel's author list covers authors born 1900 or later)
PRE1900 = set('''russell|b|bertrand kant|i hume|d mill|j carnap|r locke|j frege|g wittgenstein|l moore|g|george
descartes|r james|w broad|c hobbes|t leibniz|g husserl|e ross|w sidgwick|h heidegger|m marx|k whitehead|a
reichenbach|h peirce|c hilbert|d hegel|g dewey|j reid|t bentham|j smith|a|adam einstein|a cassirer|e lewis|c
duhem|p darwin|c brentano|f nietzsche|f weyl|h berkeley|g aquinas|t rousseau|j|jean-jacques keynes|j schilpp|p
schopenhauer|a wolfson|h poincare|h bradley|f aristotle| meinong|a schlick|m lukasiewicz|j bernays|p hayek|f
price|h|hh spinoza|b plato| augustine| zermelo|e brouwer|l mach|e helmholtz|h boole|g dedekind|r cantor|g
peano|g wundt|w bolzano|b fichte|j schelling|f herder|j hamann|j jacobi|f mendelssohn|m wolff|c baumgarten|a
smith|a hutcheson|f shaftesbury| butler|j|joseph price|r malebranche|n arnauld|a gassendi|p pascal|b bacon|f
newton|i boyle|r galileo| condillac|e diderot|d voltaire| montesquieu| condorcet| wollstonecraft|m
kierkegaard|s feuerbach|l engels|f comte|a tocqueville|a green|t bosanquet|b mctaggart|j royce|j santayana|g
bergson|h freud|s weber|m durkheim|e mead|g simmel|g dilthey|w windelband|w rickert|h cohen|h natorp|p
scheler|m collingwood|r neurath|o kelsen|h prichard|h stout|g alexander|s cook|j skolem|t lesniewski|s
tarde|g sorel|g mill|j|john mill|j|james weber|m|max'''.split())
PRE1900 -= {'smith|a', 'weber|m', 'alexander|s'}
# not philosophers' persons but parse artifacts to drop
DROP = {'press|c', 'press|n', 'press|p', 'anonymous|', 'et|'}
ANCIENT_MEDIEVAL = {'aristotle|', 'plato|', 'aquinas|t', 'augustine|', 'avicenna|', 'averroes|', 'ockham|w', 'scotus|j'}

DISPLAY = {
    'lewis|d': 'Lewis, David K.', 'quine|w': 'Quine, W. V. O.', 'kripke|s': 'Kripke, Saul A.',
    'chalmers|d': 'Chalmers, David J.', 'searle|j': 'Searle, John R.', 'fodor|j': 'Fodor, Jerry A.',
    'stalnaker|r': 'Stalnaker, Robert C.', 'strawson|p': 'Strawson, P. F.', 'armstrong|d': 'Armstrong, David M.',
    'scanlon|t': 'Scanlon, T. M.', 'smith|m|maynard': 'Maynard Smith, John', 'kim|j': 'Kim, Jaegwon',
    'geach|p': 'Geach, Peter T.', 'mackie|j': 'Mackie, J. L.', 'anscombe|g': 'Anscombe, G. E. M.',
    'dretske|f': 'Dretske, Fred I.', 'tarski|a': 'Tarski, Alfred', 'zalta|e': 'Zalta, Edward N.',
    'hintikka|j': 'Hintikka, Jaakko', 'ayer|a': 'Ayer, A. J.', 'lowe|e': 'Lowe, E. J.', 'hart|h': 'Hart, H. L. A.',
    'smart|j': 'Smart, J. J. C.', 'grice|h|paul': 'Grice, H. Paul', 'cohen|g': 'Cohen, G. A.',
    'velleman|j': 'Velleman, J. David', 'paul|l': 'Paul, L. A.', 'beall|j': 'Beall, Jc', 'long|a': 'Long, A. A.',
    'hacker|p': 'Hacker, P. M. S.', 'kamm|f': 'Kamm, F. M.', 'mellor|d': 'Mellor, D. H.',
    'cooper|j': 'Cooper, John M.', 'burnyeat|m': 'Burnyeat, Myles', 'varzi|a': 'Varzi, Achille C.',
    'cresswell|m': 'Cresswell, M. J.', 'ashworth|e': 'Ashworth, E. J.', 'wolfson|h': 'Wolfson, Harry A.',
    'simmons|a': 'Simmons, A. John', 'wallace|r': 'Wallace, R. Jay', 'prior|a': 'Prior, Arthur N.',
    'hare|r': 'Hare, R. M.', 'ross|w': 'Ross, W. D.', 'moore|g|george': 'Moore, G. E.', 'broad|c': 'Broad, C. D.',
    'lewis|c': 'Lewis, C. I.', 'whitehead|a': 'Whitehead, Alfred North', 'mill|j': 'Mill, John Stuart',
    'van fraassen': 'van Fraassen, Bas C.', 'russell|b|bertrand': 'Russell, Bertrand', 'price|h|hh': 'Price, H. H.',
    'schilpp|p': 'Schilpp, Paul Arthur', 'sedley|d': 'Sedley, David',
}

def fmt_given(g):
    g = g.strip()
    g = re.sub(r'\b([A-Z])(?=\s|$)', r'\1.', g)          # "David K" -> "David K."
    g = re.sub(r'\b([A-Z])\.(?=[A-Z])', r'\1. ', g)      # "W.V.O." -> "W. V. O."
    g = re.sub(r'\b([A-Z])(?=[A-Z]\b)', r'\1. ', g)
    return re.sub(r'\s+', ' ', g).strip()

def is_full(g):
    t = [x for x in re.split(r'[\s\.]+', g) if x]
    return bool(t) and len(t[0]) >= 2 and t[0].replace('-', '').isalpha() and not t[0].isupper()

def display_name(a):
    if a['pid'] in DISPLAY:
        return DISPLAY[a['pid']]
    base = '|'.join(a['pid'].split('|')[:2])
    if base in DISPLAY and a['pid'].count('|') == 2 and a['n'] >= 30:
        return DISPLAY[base]
    names = collections.Counter()
    sur = collections.Counter()
    for s, g, c in a['names']:
        sur[s] += c
        names[g] += c
    s = sur.most_common(1)[0][0]
    if s and s[0].islower() and not s.startswith(('van ', 'von ', 'de ', 'van', 'hooks')):
        s = s[0].upper() + s[1:]
    full = [(g, c) for g, c in names.items() if is_full(g)]
    if full:
        g, c = max(full, key=lambda x: x[1])
        longer = [(h, d) for h, d in full if h != g and h.startswith(g) and d >= 0.25 * c]
        if longer:
            g = max(longer, key=lambda x: x[1])[0]
    else:
        g = names.most_common(1)[0][0]
    return f"{s}, {fmt_given(g)}".strip(', ')

# most-cited work per author (first-author clusters) — map from surname|initial
best_work = {}
for w in W:
    k = w['key']
    if (w['year_mode'] or 0) < 1900 and not k.startswith(('kant', 'hume')):
        pass
    if k not in best_work or w['n_entries'] > best_work[k]['n_entries']:
        best_work[k] = w

# Schwitzgebel 2024
old = []
for line in open('ref/authors2024.tsv', encoding='utf-8'):
    r, n, c = line.rstrip('\n').split('\t')
    s, _, g = n.partition(',')
    old.append({'rank': int(r), 'name': n, 'n': int(c), 'key': norm_surname(s) + '|' + initial(g.strip()),
                'first': (re.split(r'[\s\.]+', fold(g.strip()).lower()) or [''])[0]})

def match_old(a):
    base = '|'.join(a['pid'].split('|')[:2])
    cands = [o for o in old if o['key'] == base]
    if len(cands) > 1:
        fn = a['pid'].split('|')[2] if a['pid'].count('|') >= 2 else None
        c2 = [o for o in cands if fn and o['first'] == fn]
        cands = c2 or cands
    return cands[0] if len(cands) == 1 else None

out = []
for a in A:
    if a['pid'] in DROP or a['pid'] in ANCIENT_MEDIEVAL:
        continue
    if a['n'] < 20:
        continue
    base = '|'.join(a['pid'].split('|')[:2])
    rec = {'pid': a['pid'], 'name': display_name(a), 'n': a['n'], 'pre1900': a['pid'] in PRE1900 or (a['pid'].count('|') == 1 and base in PRE1900),
           'entries': a['entries']}
    bw = best_work.get(base)
    if bw:
        rec['top_work'] = {'title': bw['title'][0][0], 'year': bw['year_mode'], 'n': bw['n_entries']}
    o = match_old(a)
    if o:
        rec['n2024'] = o['n']; rec['rank2024'] = o['rank']
    out.append(rec)

def ranks(lst):
    prev = None
    for i, x in enumerate(lst):
        if x['n'] != prev:
            r = i + 1; prev = x['n']
        x['rank'] = r

contemp = [x for x in out if not x['pre1900']]
contemp.sort(key=lambda x: (-x['n'], x['name']))
ranks(contemp)
allera = sorted(out, key=lambda x: (-x['n'], x['name']))
for x in allera:
    x['rank_all'] = None
prev = None
for i, x in enumerate(allera):
    if x['n'] != prev:
        r = i + 1; prev = x['n']
    x['rank_all'] = r

res = {'contemporary': [x for x in contemp if x['n'] >= THRESH],
       'pre1900': [x for x in allera if x['pre1900'] and x['n'] >= THRESH]}
json.dump(res, open('authors_final.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('contemporary >=30:', len(res['contemporary']), ' pre-1900 >=30:', len(res['pre1900']))
miss = [o for o in old if not any(x.get('rank2024') == o['rank'] and x.get('n2024') == o['n'] for x in contemp)]
print('2024 authors not matched:', len(miss))
for o in miss[:40]:
    print('  ', o['rank'], o['name'], o['n'])
for x in res['contemporary'][:30]:
    print(x['rank'], x['n'], x.get('n2024'), x['name'], '|', (x.get('top_work') or {}).get('title', '')[:40])
