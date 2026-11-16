"""Cluster SEP entries by the authors they cite; write entry->cluster for labelling."""
import json, sys, io, contextlib, importlib.util, collections
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans
from scipy import sparse

sys.path.insert(0, 'scripts')
spec = importlib.util.spec_from_file_location('authors', 'scripts/authors.py')
with contextlib.redirect_stdout(io.StringIO()):
    au = importlib.util.module_from_spec(spec); spec.loader.exec_module(au)

entry_p = collections.defaultdict(set)
for (i, ns, s, g), pid in zip(au.occ, au.final_pid):
    if pid:
        entry_p[au.recs[i]['entry']].add(pid)
pc = collections.Counter(p for ps in entry_p.values() for p in ps)
vocab = {p: j for j, p in enumerate(sorted(p for p, c in pc.items() if c >= 3))}
entries = sorted(entry_p)
rows, cols = [], []
for r, e in enumerate(entries):
    for p in entry_p[e]:
        if p in vocab:
            rows.append(r); cols.append(vocab[p])
X = sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(entries), len(vocab)))
X = TfidfTransformer(sublinear_tf=True).fit_transform(X)
Z = normalize(TruncatedSVD(120, random_state=0).fit_transform(X))
K = int(sys.argv[1]) if len(sys.argv) > 1 else 22
km = KMeans(K, n_init=20, random_state=0).fit(Z)
lab = km.labels_
titles = {}
import re, html
for e in entries:
    h = open(f'raw/{e}.html', encoding='utf-8', errors='ignore').read()
    m = re.search(r'<h1>(.*?)</h1>', h, re.S)
    titles[e] = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else e
names = {}
for a in json.load(open('author_counts.json', encoding='utf-8')):
    names[a['pid']] = a['names'][0][0]
for k in range(K):
    members = [entries[i] for i in range(len(entries)) if lab[i] == k]
    # most characteristic authors: share within cluster vs overall
    cc = collections.Counter(p for e in members for p in entry_p[e])
    top = sorted(cc, key=lambda p: -(cc[p] / len(members)) * np.log(len(entries) / pc[p]))[:8]
    print(f'\n## {k} ({len(members)}):', ', '.join(names.get(p, p.split("|")[0]) for p in top))
    print('   ', '; '.join(titles[e] for e in members[:28]))
json.dump({'entries': entries, 'labels': lab.tolist(), 'Z': Z.tolist(), 'titles': titles}, open('entry_clusters.json', 'w'))
