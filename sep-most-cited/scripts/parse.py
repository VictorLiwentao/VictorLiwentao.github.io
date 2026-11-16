"""Extract bibliography records from SEP entry HTML files.

Output: records.jsonl, one line per bibliography item:
  entry, raw_auth, authors [[surname, given], ...], editor (bool),
  years [int...], forthcoming (bool), title, text
"""
import html, json, os, re, sys
from bs4 import BeautifulSoup, NavigableString, Tag

RAW = sys.argv[1]
OUT = sys.argv[2]

END_MARKERS = ['id="other-internet-resources"', '<h2 id="Oth"', 'name="Oth"',
               'id="related-entries"', '<h2 id="Rel"', 'name="Rel"', 'id="article-copyright"']

def bib_segment(h):
    i = h.find('id="bibliography"')
    if i < 0:
        return None
    j = min([k for k in (h.find(m, i) for m in END_MARKERS) if k > 0] or [len(h)])
    seg = h[i:j]
    # drop the academic tools block, which is sometimes nested in the bibliography
    seg = re.sub(r'<div id="academic-tools">.*?</blockquote>\s*</div>', '', seg, flags=re.S)
    return '<div ' + seg

YEAR_RE = re.compile(r'(?<![\d/])(1[0-9]\d\d|20[0-3]\d)(?:\s*[a-z](?![a-z]))?(?!\d)')
FORTH_RE = re.compile(r'\b(forthcoming|in press|unpublished|n\.\s?d\.|manuscript|to appear)\b', re.I)
DASH_RE = re.compile(r'^\s*(?:[‐-―−\-_=~]\s*){2,}')

def item_html_list(seg):
    soup = BeautifulSoup(seg, 'lxml')
    items = []
    for tag in soup.find_all(['li', 'dd', 'p', 'td']):
        # skip containers that themselves contain list items (avoid double counting)
        if tag.name in ('p', 'td', 'dd') and tag.find_parent('li'):
            continue
        if tag.name == 'p' and tag.find_parent(['dd', 'td']):
            continue
        if tag.name == 'li' and tag.find('li'):
            # nested list: take only the li's own leading text
            for sub in tag.find_all(['ul', 'ol']):
                sub.extract()
        if tag.name == 'p' and 'bibnote' in (tag.get('class') or []):
            continue
        # remove annotation sub-paragraphs inside items
        for note in tag.find_all('p', class_='bibnote'):
            note.extract()
        items.append(tag)
    return items

def clean_text(s):
    s = html.unescape(s)
    s = s.replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()

def first_title(tag_html_after):
    """Given the html after the year, return the first quoted or italic title."""
    t = tag_html_after
    q = re.search(r'(?:&ldquo;|“|")(.+?)(?:&rdquo;|”|")', t, re.S)
    e = re.search(r'<(em|i)>(.+?)</\1>', t, re.S)
    cands = []
    if q: cands.append((q.start(), q.group(1)))
    if e: cands.append((e.start(), e.group(2)))
    if cands:
        pos, raw = min(cands)
        # only accept if near the start (title should come right after year)
        prefix = clean_text(re.sub(r'<[^>]+>', '', t[:pos]))
        if len(prefix) <= 25:
            return clean_text(re.sub(r'<[^>]+>', '', raw))
    txt = clean_text(re.sub(r'<[^>]+>', '', t))
    txt = re.sub(r'^[\s\.,:;\)\]]+', '', txt)
    m = re.match(r'(.{3,200}?)(?:\.\s|,\s(?:in|In)\s|$)', txt)
    return m.group(1) if m else txt[:150]

GIVEN_TOKEN = re.compile(r"^(?:[A-ZÀ-Þ][a-zß-ÿ'\-]*\.?|[A-Z]{1,3}|[A-Za-z]\.(?:-?[A-Za-z]\.?){0,3}|[A-Z]\.?-[A-Z]\.?|Jr\.?|Sr\.?|II|III|de|van|von|der|den|la|le|da|du|del|di|St\.)$")
def given_word(w):
    w2 = w.strip('.')
    if GIVEN_TOKEN.match(w):
        return True
    if not w2:
        return False
    parts = w2.split('-')
    return all(p and p[0].isupper() and all(ch.isalpha() or ch in "'’." for ch in p) for p in parts)

PARTICLES = {'van', 'von', 'de', 'der', 'den', 'du', 'da', 'di', 'del', 'della', 'la', 'le', 'ter', 'ten', 'al', 'el', 'bin', 'ibn', 'dos', 'das', 'st.', "d'"}

def split_people(a):
    """Split an author string into [(surname, given)] list."""
    a = a.strip().strip(',;:. ')
    a = re.sub(r'\bet\.? al\.?', '', a)
    a = re.sub(r',?\s*(?:Jr|Sr)\.?(?=,|$|\s)', '', a)
    parts = re.split(r'\s*(?:,\s*)?(?:\band\b|&|\bund\b|\bet\b|;)\s*', a)
    people = []
    for pi, part in enumerate(parts):
        part = part.strip().strip(',. ')
        if not part:
            continue
        pieces = [p.strip() for p in part.split(',') if p.strip()]
        k = 0
        while k < len(pieces):
            p = pieces[k]
            words = p.split()
            nxt = pieces[k + 1] if k + 1 < len(pieces) else None
            def is_given(s):
                ws = s.split()
                return bool(ws) and all(given_word(w) for w in ws) and len(ws) <= 5
            if nxt is not None and is_given(nxt) and (len(words) == 1 or words[0].lower() in PARTICLES or (len(words) <= 3 and not is_given(p))):
                people.append((p, nxt)); k += 2; continue
            if len(words) >= 2 and len(words[0]) > 2 and not re.fullmatch(r'[A-Z]\.?', words[0]) and all(re.fullmatch(r"(?:[A-Z]\.?-?){1,4}", w) for w in words[1:]):
                # "Surname G." / "Surname J.L." without a comma
                people.append((words[0], ' '.join(words[1:]))); k += 1; continue
            if len(words) >= 2:
                # natural order: Given ... Surname (with particles)
                idx = len(words) - 1
                while idx - 1 > 0 and words[idx - 1].lower() in PARTICLES:
                    idx -= 1
                people.append((' '.join(words[idx:]), ' '.join(words[:idx]))); k += 1; continue
            people.append((p, '')); k += 1
    return people

def parse_item(tag):
    h = str(tag)
    h = re.sub(r'^<(li|dd|p|td)[^>]*>', '', h)
    h = re.sub(r'<a name="[^"]*"\s*>\s*</a>', '', h)
    h = re.sub(r'<a [^>]*>\s*</a>', '', h)
    text = clean_text(re.sub(r'<[^>]+>', ' ', h))
    if len(text) < 8:
        return None
    # locate the first year (or forthcoming) in the plain text
    ym = YEAR_RE.search(text)
    fm = FORTH_RE.search(text)
    cut = None
    if ym and (not fm or ym.start() < fm.start()):
        cut = ym.start()
    elif fm:
        cut = fm.start()
    if cut is None:
        return {'text': text[:300], 'raw_auth': None}
    auth = text[:cut]
    # author part shouldn't contain a title
    auth_clean = re.sub(r'[\(\[]\s*$', '', auth).strip()
    editor = bool(re.search(r'\(?\b(eds?|editors?|Hrsg|Hg|dir)\b\.?\)?', auth_clean, re.I))
    trans_only = bool(re.search(r'\((?:trans|tr)\.?\)', auth_clean, re.I))
    auth_clean = re.sub(r'\(?\b(eds?|editors?|Hrsg|Hg|dir|trans|tr|comp|compiler)\b\.?\)?', '', auth_clean, flags=re.I)
    auth_clean = re.sub(r'[\(\[][^\)\]]*[\)\]]', '', auth_clean)  # bracketed sigla
    auth_clean = auth_clean.strip().strip(',.:;([ ')
    # years field: from cut up to the start of the title (approx first 30 chars)
    yfield = text[cut:cut + 40]
    ystop = re.search(r'[\.,:]\s*(?=[A-Z“"‘\'])|\)\s*[\.,]?\s', yfield)
    yfield2 = yfield[:ystop.end()] if ystop else yfield[:20]
    years = [int(y) for y in re.findall(r'(?<!\d)(1[0-9]\d\d|20[0-3]\d)(?!\d)', yfield2)]
    # handle ranges like 1910-1913 counted via findall above
    forth = bool(FORTH_RE.match(text[cut:cut + 20]))
    # title: work in html after the year field
    # find position in html corresponding to the year field: search the year string
    ystr = ym.group(0) if (ym and cut == ym.start()) else (fm.group(0) if fm else '')
    hpos = h.find(ystr) if ystr else -1
    after = h[hpos + len(ystr):] if hpos >= 0 else h
    # skip trailing year-field characters (e.g. "/1787", " [2001]", ").")
    after = re.sub(r'^\s*(?:[a-z](?![a-z]))?\s*(?:[\[\(/–—-]\s*(?:&ndash;|&mdash;)?\s*[\dA-Za-z\.\s,/]*?[\]\)]?)*\s*[\.,:;\)]*\s*', '', after)
    title = first_title(after)
    return {'raw_auth': auth_clean, 'editor': editor, 'trans_only': trans_only,
            'years': years, 'forthcoming': forth, 'title': title, 'text': text[:300]}

def main():
    out = open(OUT, 'w', encoding='utf-8')
    files = sorted(f for f in os.listdir(RAW) if f.endswith('.html'))
    n_items = 0
    for f in files:
        entry = f[:-5]
        h = open(os.path.join(RAW, f), encoding='utf-8', errors='ignore').read()
        seg = bib_segment(h)
        if not seg:
            continue
        prev_auth = None
        for tag in item_html_list(seg):
            rec = parse_item(tag)
            if rec is None:
                continue
            ra = rec.get('raw_auth')
            if ra is not None:
                m = DASH_RE.match(ra)
                if m or ra == '':
                    if ra == '' and not DASH_RE.match(rec['text']):
                        # no author before the year: skip (e.g. title-first primary lit)
                        rec['authors'] = []
                    else:
                        rest = ra[m.end():].strip(' ,') if m else ''
                        if prev_auth:
                            if rest:
                                ra = prev_auth.split(' and ')[0].split(' & ')[0] + ' and ' + rest.lstrip('and ').lstrip('& ')
                            else:
                                ra = prev_auth
                        rec['raw_auth'] = ra
                if ra and not DASH_RE.match(ra) and len(ra) < 250 and not re.match(r'^[“"\'<\[]', ra):
                    rec['authors'] = split_people(ra)
                    prev_auth = ra
                else:
                    rec.setdefault('authors', [])
            else:
                rec['authors'] = []
            rec['entry'] = entry
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            n_items += 1
    print('items', n_items)

if __name__ == '__main__':
    main()
