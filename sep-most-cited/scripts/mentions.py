"""Count SEP entries that mention each philosopher born before 1900 (disambiguated), plus links."""
import json, re, html, collections, sys
sys.path.insert(0, 'scripts')
from common import fold

L = json.load(open('longcanon_raw.json', encoding='utf-8'))
F = json.load(open('entry_fields.json'))
slugs = [l.strip() for l in open('slugs.txt') if l.strip()]
LABEL_FIX = {'Q15975': 'Montesquieu', 'Q463553': 'J. M. E. McTaggart', 'Q528802': 'Henry More', 'Q134661': 'George Boole', 'Q2332520': 'Damaris Masham'}
LABEL_REN = {'Alexandros of Aphrodisias': 'Alexander of Aphrodisias', 'Ammonius Hermiae': 'Ammonius', 'Ibn Taymiyyah': 'Ibn Taymiyya',
             'Jean-Antoine-Nicolas de Caritat de Condorcet': 'Marquis de Condorcet', 'Gangesha Upadhyaya': 'Gaṅgeśa', 'Avempace': 'Ibn Bājja'}
for x in L:
    if not x['label']:
        x['label'] = LABEL_FIX.get(x['q'], x['all_slugs'][0])
    x['label'] = LABEL_REN.get(x['label'], x['label'])

# folded main text of every entry (cached)
import os, pickle
if os.path.exists('ent_text.pkl'):
    T = pickle.load(open('ent_text.pkl', 'rb'))
else:
    T = {}
    for s in slugs:
        h = open(f'raw/{s}.html', encoding='utf-8', errors='ignore').read()
        i = h.find('id="preamble"'); i = i if i >= 0 else h.find('id="main-text"')
        j = h.find('id="bibliography"', i)
        seg = h[i:j if j > 0 else len(h)]
        T[s] = re.sub(r'\s+', ' ', fold(html.unescape(re.sub(r'<[^>]+>', ' ', seg)))).replace('’', "'")
    pickle.dump(T, open('ent_text.pkl', 'wb'))

STOP = set('''In For On As But And The While Unlike Like According Both See Cf Following After Before Since Although Though Thus Hence So Then
When If Yet Indeed Even Also Here There This That These Those Such Where Whereas Against Contra With Without From To By Of At Is Was Were
Not Nor Or Unlike Neither Either Only Just Much Many Most More Some Later Early Earlier Young Old Book Part Chapter Section Vol Volume
Letter Letters Works Essay Treatise Critique Ethics Notes Note Introduction Preface Appendix Lecture Lectures Moreover However Similarly
Therefore Accordingly Again Unlike Apart Despite Among Between Within Through Throughout Upon Toward Towards Under Over Into Onto
I II III IV V VI VII VIII IX X Sect Ch Bk Pt Fr Frag Prop Def Ax Cor Schol Ep Dial'''.split())
FIRSTNAMES = set('Peter Henry John Giles William Hugh Robert Richard Thomas James Gregory Nicholas Bernard Walter Godfrey Adam Roger Albert Paul Simon Alexander Matthew Francis Duns'.split())

SPECIAL = {
 'The Buddha': [r'\bBuddha\b'], 'Margaret Cavendish, Duchess of Newcastle-upon-Tyne': [r'\bMargaret Cavendish\b', 'SUR:Cavendish'],
 'Anthony Ashley-Cooper, 3rd Earl of Shaftesbury': [r'\bShaftesbury\b'], 'Sextus Empiricus': ['SUR:Sextus'],
 'Elisabeth of the Palatinate': [r'\bElisabeth of (?:the Palatinate|Bohemia)\b', r'\bPrincess Elisabeth\b'],
 'William David Ross': [r'\bW\. ?D\. Ross\b', r'\b(?:Sir )?David Ross\b', r'\bWilliam David Ross\b', 'SUR:Ross'], 'C. D. Broad': [r'\bC\. ?D\. Broad\b', r'\bCharlie Dunbar Broad\b', 'SUR:Broad'],
 'Zeno of Elea': [r'\bZeno of Elea\b'], 'Zeno of Citium': [r'\bZeno of Citium\b'],
 'Thomas Aquinas': [r'\bAquinas\b', r'\bThomas Aquinas\b'], 'William of Ockham': [r'\bOckham\b'], 'Augustine of Hippo': [r'\bAugustine\b'],
 'Anselm of Canterbury': [r'\bAnselm\b'], 'Avicenna': [r'\bAvicenna\b', r'\bIbn Sina\b'], 'Averroes': [r'\bAverroes\b', r'\bIbn Rushd\b'],
 'Moshe ben Maimon': [r'\bMaimonides\b', r'\bMoses ben Maimon\b', r'\bMoshe ben Maimon\b'], 'Salomon Maimon': [r'\bSalomon Maimon\b', r'\bMaimon\b'],
 'John Duns Scotus': [r'\bScotus\b'], 'Francis Bacon': [r'\bFrancis Bacon\b', 'SUR:Bacon'], 'Roger Bacon': [r'\bRoger Bacon\b'],
 'Henry More': [r'\bHenry More\b'], 'Thomas More': [r'\bThomas More\b'], 'John Stuart Mill': [r'\bJ\. ?S\. Mill\b', r'\bJohn Stuart Mill\b', 'SUR:Mill'],
 'James Mill': [r'\bJames Mill\b'], 'Harriet Taylor Mill': [r'\bHarriet Taylor\b'], 'Benjamin Peirce': [r'\bBenjamin Peirce\b'],
 'Charles Sanders Peirce': [r'\bC\. ?S\. Peirce\b', r'\bCharles (?:Sanders )?Peirce\b', 'SUR:Peirce'], 'John Locke': [r'\bJohn Locke\b', 'SUR:Locke'],
 'Alain LeRoy Locke': [r'\bAlain (?:LeRoy )?Locke\b'], 'Clarence Irving Lewis': [r'\bC\. ?I\. Lewis\b', r'\bClarence Irving Lewis\b'],
 'Hermann Cohen': [r'\bHermann Cohen\b'], 'Anna J. Cooper': [r'\bAnna (?:Julia |J\. )?Cooper\b'], 'Nicolai Hartmann': [r'\bNicolai Hartmann\b'],
 'Wilhelm von Humboldt': [r'\bWilhelm von Humboldt\b'], 'Alexander von Humboldt': [r'\bAlexander von Humboldt\b'],
 'Friedrich Albert Lange': [r'\bF\. ?A\. Lange\b', r'\bFriedrich Albert Lange\b'], 'Henry Habberley Price': [r'\bH\. ?H\. Price\b'],
 'Richard Price': [r'\bRichard Price\b'], 'Friedrich Schlegel': [r'\bFriedrich (?:von )?Schlegel\b'],
 'August Wilhelm von Schlegel': [r'\bA\. ?W\. (?:von )?Schlegel\b', r'\bAugust Wilhelm (?:von )?Schlegel\b'], 'D. C. Williams': [r'\bD\. ?C\. Williams\b', r'\bDonald Cary Williams\b'],
 'John Cook Wilson': [r'\bCook Wilson\b'], 'Christian Wolff': [r'\bChristian Wolff\b', 'SUR:Wolff'], 'Chauncey Wright': [r'\bChauncey Wright\b'],
 'John Anderson': [r'\bJohn Anderson\b'], 'John Austin': [r'\bJohn Austin\b'], 'Fakhr al-Din al-Razi': [r'\bFakhr al-Din\b'],
 'Abu Bakr al-Razi': [r'\bAbu Bakr al-Razi\b', r'\bRhazes\b'], 'Kumārila Bhaṭṭa': [r'\bKumarila\b'], 'Jayarāśi Bhaṭṭa': [r'\bJayarasi\b'],
 'Socrates': [r'\bSocrates\b'], 'Plato': [r'\bPlato\b'], 'Aristotle': [r'\bAristotle\b'], 'William James': [r'\bWilliam James\b', r"\bJames's (?:Principles|Pragmatism|Varieties|radical)"],
 'Adam Smith': [r'\bAdam Smith\b'], 'Joseph Butler': [r'\bJoseph Butler\b', r'\bBishop Butler\b', 'SUR:Butler'], 'Thomas Reid': [r'\bThomas Reid\b', 'SUR:Reid'],
 'T. H. Green': [r'\bT\. ?H\. Green\b', r'\bThomas Hill Green\b'], 'Thomas Hill Green': [r'\bT\. ?H\. Green\b', r'\bThomas Hill Green\b'],
 'George Herbert Mead': [r'\bG\. ?H\. Mead\b', r'\bGeorge Herbert Mead\b'], 'Samuel Alexander': [r'\bSamuel Alexander\b'],
 'Emily Elizabeth Constance Jones': [r'\bConstance Jones\b', r'\bE\. ?E\. ?C\. Jones\b'], 'Max Weber': [r'\bMax Weber\b', 'SUR:Weber'],
 'Samuel Clarke': [r'\bSamuel Clarke\b', 'SUR:Clarke'], 'Anthony Collins': [r'\bAnthony Collins\b'], 'Adam Ferguson': [r'\bAdam Ferguson\b'],
 'Jonathan Edwards': [r'\bJonathan Edwards\b'], 'Dugald Stewart': [r'\bDugald Stewart\b'], 'John Dewey': [r'\bJohn Dewey\b', 'SUR:Dewey'],
 'Isaac Newton': [r'\bNewton\b'], 'Galileo Galilei': [r'\bGalileo\b'], 'Albert the Great': [r'\bAlbert the Great\b', r'\bAlbertus Magnus\b'],
 'Nicholas of Cusa': [r'\bNicholas of Cusa\b', r'\bCusanus\b'], 'Marsilius of Inghen': [r'\bMarsilius of Inghen\b'], 'Marsilius of Padua': [r'\bMarsilius of Padua\b'],
 'Peter Abelard': [r'\bAbelard\b'], 'Desiderius Erasmus': [r'\bErasmus\b'], 'Pseudo-Dionysius the Areopagite': [r'\bDionysius\b'],
 'Paul-Henri Thiry d\'Holbach': [r'\bHolbach\b'], 'Gottfried Wilhelm Leibniz': [r'\bLeibniz\b'], 'Georg Wilhelm Friedrich Hegel': [r'\bHegel\b'],
 'Benedictus de Spinoza': [r'\bSpinoza\b'], 'Baruch Spinoza': [r'\bSpinoza\b'], 'René Descartes': [r'\bDescartes\b'], 'Confucius': [r'\bConfucius\b', r'\bKongzi\b'],
 'Mencius': [r'\bMencius\b', r'\bMengzi\b'], 'Laozi': [r'\bLaozi\b', r'\bLao Tzu\b'], 'Zhuang Zhou': [r'\bZhuangzi\b', r'\bZhuang Zhou\b'], 'Mozi': [r'\bMozi\b'],
 'Xunzi': [r'\bXunzi\b'], 'Han Fei': [r'\bHan Fei\b'], 'Zhu Xi': [r'\bZhu Xi\b'], 'Wang Yangming': [r'\bWang Yangming\b'],
 'Montesquieu': [r'\bMontesquieu\b'], 'Voltaire': [r'\bVoltaire\b'], 'Damaris Masham': [r'\bMasham\b'], 'George Boole': [r'\bBoole\b'],
 'J. M. E. McTaggart': [r'\bMcTaggart\b'], 'Alfred North Whitehead': [r'\bWhitehead\b'], 'Bertrand Russell': [r'\bBertrand Russell\b', 'SUR:Russell'],
 'G. E. Moore': [r'\bG\. ?E\. Moore\b', 'SUR:Moore'], 'Gottlob Frege': [r'\bFrege\b'], 'Ludwig Wittgenstein': [r'\bWittgenstein\b'],
}
SPECIAL.update({'Sophie de Condorcet': [r'\bSophie de Grouchy\b', r'\bSophie de Condorcet\b', r'\bGrouchy\b'],
                'Marquis de Condorcet': [r'\bNicolas de Condorcet\b', r'\bMarquis de Condorcet\b', 'SUR:Condorcet'],
                'Ibn Bājja': [r'\bIbn Ba[^a-z]?jja\b', r'\bAvempace\b'], 'Gaṅgeśa': [r'\bGangesa\b']})
HEADOK = {'Anselm', 'Hildegard', 'Simplicius', 'Heloise', 'Philoponus', 'Ammonius', 'Damascius', 'Olympiodorus'}
ASIAN = re.compile(r'Chinese|Japanese|Korean|Indian|Buddhist|Hindu|Tibetan', re.I)

def patterns(x):
    lab = x['label']
    if lab in SPECIAL:
        return SPECIAL[lab]
    flab = fold(lab).replace('’', "'")
    toks = flab.split()
    if len(toks) == 1:
        return ['SUR:' + flab]
    if ASIAN.search(x.get('desc') or ''):
        return [r'\b' + re.escape(flab) + r'\b'] + ([r'\b' + re.escape(toks[0]) + r'\b'] if len(toks) == 2 and ASIAN.search(x.get('desc') or '') and 'Indian' in (x.get('desc') or '') else [])
    if ' of ' in flab or ' the ' in flab:
        head = toks[0]
        return [r'\b' + re.escape(flab) + r'\b'] + (['SUR:' + head] if head in HEADOK else [])
    if toks[0].lower() in ('al-', 'ibn'):
        return [r'\b' + re.escape(flab) + r'\b']
    sur = toks[-1]
    if sur.startswith(("d'", 'al-')):
        sur = sur.split("'", 1)[-1].split('-', 1)[-1]
    return [r'\b' + re.escape(flab) + r'\b(?!\s+[A-Z][a-z])', 'SUR:' + sur]

COMMONFIRST = set('David Elias John Peter Paul James Thomas William Henry Richard Robert Simon Albert Adam Mary Anne Jane'.split())
def head_pats(x):
    out = []
    for h in x.get('heads', []):
        alts = [a.strip() for b in re.findall(r'\[(?:=\s*)?([^\]]+)\]', h) for a in b.split(',')]
        base = re.sub(r'\s*\[[^\]]*\]', '', h).strip()
        if base.startswith('Aristotle,'): base = 'Aristotle'
        if ',' in base:
            sur, given = [t.strip() for t in base.split(',', 1)]
            given = re.sub(r',?\s*(Jr\.|Sr\.)$', '', given)
            names = [f'{given} {sur}']
        else:
            names = [base]
        for n in names + alts:
            if not n or n[0].islower() or n in ('Cardinal', 'Saint', 'St.'): continue
            f = fold(n).replace('’', "'").replace('‘', "'")
            toks = f.split()
            if len(toks) >= 2:
                rx = r'\b' + r'\s+'.join(re.escape(t).replace("'", "[‘'ʿ’]?") for t in toks) + r'\b(?!\s+[A-Z][a-z])'
                out.append(rx)
            elif len(f) >= 5 and f not in COMMONFIRST and n in alts + ([base] if ',' not in base else []):
                out.append('SUR:' + f)
    return out

# surnames cited in each entry's bibliography with their first initials (to spot namesakes)
sys.path.insert(0, 'scripts')
from common import norm_surname, initial as ini
BIB = collections.defaultdict(set)
for line in open('records.jsonl', encoding='utf-8'):
    rr = json.loads(line)
    for sname, gname in (rr.get('authors') or [])[:3]:
        BIB[rr['entry']].add((norm_surname(sname), ini(gname)))
WORDLIKE = {'Broad', 'More', 'Price', 'Green', 'Long', 'Young', 'Bell', 'Hope', 'Wise', 'Smart', 'Law', 'Fox', 'Hall', 'Hart', 'Field',
            'Wood', 'Read', 'Mill', 'King', 'Brown', 'White', 'Black', 'Grant', 'Strong', 'Good', 'Rich', 'Bacon', 'Butler', 'Mead'}
YEAR_AFTER = re.compile(r"^(?:'s)?\s*[\(,]?\s*(?:19|20)\d\d")

def matches(text, pats, given, death, entry=None, myini=''):
    cutoff = (death or 1890) + 10
    for p in pats:
        if p.startswith('SUR:'):
            sur = p[4:]
            if myini and any(sn == norm_surname(sur) and i2 and i2 != myini for sn, i2 in BIB.get(entry, ())):
                continue  # this entry cites a namesake: require the full name
            for m in re.finditer(r'\b' + re.escape(sur) + r'\b', text):
                pre = text[max(0, m.start() - 30):m.start()].split()
                prev = pre[-1].strip('(,;:"\'') if pre else ''
                if sur in WORDLIKE and (not pre or pre[-1][-1:] in '.?!:'):
                    continue  # sentence-initial ordinary word
                nxt = text[m.end():m.end() + 25]
                if prev and prev[0].isupper() and prev not in STOP and prev not in given and not prev.endswith('.'):
                    continue  # another person's first name, e.g. "Alain Locke"
                if re.match(r"^\s+(?:[A-Z][a-z]+|[A-Z]\.)", nxt) and not re.match(r"^\s+(?:I|II|III|IV|V|VI|VII|VIII|IX|X)\b", nxt):
                    continue  # used as a first name, e.g. "James Mill"
                ym = YEAR_AFTER.match(nxt)
                if ym and int(re.search(r'(?:19|20)\d\d', ym.group(0)).group(0)) > cutoff:
                    continue  # author-date citation of a later namesake
                return True
        elif re.search(p, text):
            return True
    return False

out = []
for x in L:
    if x['birth'] is None or x['birth'] >= 1900:
        continue
    pats = patterns(x)
    if x['label'] not in SPECIAL:
        pats = pats + [p for p in head_pats(x) if p not in pats]
    given = set(fold(x['label']).split()[:-1])
    lt = fold(x['label']).split()
    myini = lt[0][0].lower() if len(lt) > 1 and lt[0][0].isalpha() else ''
    own = set(x['all_slugs'])
    def key(p):
        if p.startswith('SUR:'): return p[4:]
        q = re.sub(r'\(\?[^)]*\)', ' ', p); q = re.sub(r'\[[^\]]*\]', ' ', q); q = re.sub(r'\\[a-zA-Z]', ' ', q)
        w = re.findall(r'[A-Za-z]{3,}', q)
        return max(w, key=len) if w else ''
    keys = [key(p) for p in pats]
    ment = sorted(e for e, t in T.items() if e not in own and any(k in t for k in keys) and matches(t, pats, given, x.get('death'), e, myini))
    out.append({**x, 'ment': ment, 'pats': pats})
out.sort(key=lambda r: -len(r['ment']))
json.dump(out, open('longcanon.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(out))
for r in out[:110]:
    print(f"{len(r['ment']):4} {len(r['links']):4}  {r['label']} ({r['birth']})  {r['pats'][:2]}")
