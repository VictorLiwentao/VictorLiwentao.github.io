"""Assign each SEP entry a fine field and a macro field from the citation clusters."""
import json, numpy as np, collections
d = json.load(open('entry_clusters.json'))
E = d['entries']; L = np.array(d['labels']); Z = np.array(d['Z']); T = d['titles']
s = json.load(open('sub15.json'))

FINE = {0: 'Ethics', 1: 'Political philosophy & applied ethics', 2: 'Logic & philosophy of mathematics', 3: 'Epistemology',
        4: 'Metaphysics', 5: 'Philosophy of biology', 6: 'Aesthetics', 7: 'Early modern philosophy', 8: 'Ancient philosophy',
        9: 'Philosophy of mind & cognitive science', 10: 'Chinese philosophy', 11: 'Kant & German philosophy',
        12: 'Arabic, Islamic & Jewish philosophy', 13: 'Philosophy of religion', 14: 'Philosophy of physics',
        16: 'Philosophy of science & formal epistemology', 17: 'Indian & Buddhist philosophy', 18: 'Philosophy of language',
        19: 'Medieval philosophy', 20: 'Late ancient philosophy', 21: 'Renaissance philosophy',
        151: 'Continental philosophy & pragmatism', 152: 'Feminist philosophy', 153: 'Japanese philosophy',
        154: 'Philosophy of race, Africana & Latin American philosophy'}
MACRO = {0: 'Ethics', 1: 'Social & political', 152: 'Social & political', 154: 'Social & political',
         3: 'Metaphysics & epistemology', 4: 'Metaphysics & epistemology', 13: 'Metaphysics & epistemology',
         9: 'Mind & language', 18: 'Mind & language', 2: 'Logic & mathematics',
         5: 'Science', 14: 'Science', 16: 'Science', 6: 'Aesthetics'}
for k in (7, 8, 10, 11, 12, 17, 19, 20, 21, 151, 153):
    MACRO[k] = 'History & traditions'

fine = L.copy()
for i, sl in zip(s['idx'], s['sub']):
    fine[i] = 150 + sl
# reassign the mixed sub-cluster 150 to the nearest clean cluster centroid
cent = {k: Z[fine == k].mean(0) for k in FINE}
for i in np.where(fine == 150)[0]:
    fine[i] = max(cent, key=lambda k: float(Z[i] @ cent[k]) / np.linalg.norm(cent[k]))
out = {e: {'fine': FINE[int(f)], 'macro': MACRO[int(f)]} for e, f in zip(E, fine)}
json.dump(out, open('entry_fields.json', 'w'), indent=0)
c = collections.Counter(v['macro'] for v in out.values())
print(c)
moved = [T[E[i]] + ' -> ' + FINE[int(fine[i])] for i in s['idx'] if L[i] == 15 and int(fine[i]) < 150][:40]
print('\n'.join(moved))
