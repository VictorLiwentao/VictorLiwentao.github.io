import re, unicodedata

def fold(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.replace('ß', 'ss').replace('ø', 'o').replace('Ø', 'O').replace('ł', 'l').replace('Ł', 'L').replace('æ', 'ae').replace('œ', 'oe')
    return s

def norm_surname(s):
    s = fold(s).lower()
    s = re.sub(r"[^a-z\- ']", '', s)
    s = s.replace("'", '').replace('-', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s.replace(' ', '')

def initial(given):
    g = fold(given or '').strip()
    m = re.search(r'[A-Za-z]', g)
    return m.group(0).lower() if m else ''

ARTICLES = {'a', 'an', 'the'}

def norm_title_tokens(t):
    t = fold(t or '').lower()
    t = t.replace('&', ' and ')
    t = re.sub(r"[‘’'`]", '', t)
    t = re.sub(r'[:–—;]', ' : ', t)
    t = re.sub(r'[\.\?\!]\s', ' : ', t + ' ')
    t = re.sub(r'[^a-z0-9: ]', ' ', t)
    toks = t.split()
    # strip leading separators and articles
    while toks and toks[0] == ':':
        toks.pop(0)
    if toks and toks[0] in ARTICLES:
        toks.pop(0)
    # collapse consecutive separators, drop trailing separators
    out = []
    for w in toks:
        if w == ':' and (not out or out[-1] == ':'):
            continue
        out.append(w)
    while out and out[-1] == ':':
        out.pop()
    return out
