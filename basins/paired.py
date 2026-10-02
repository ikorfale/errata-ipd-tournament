"""Paired test: same 8-strategy starting mix, with and without repair-1 added at share s (rest scaled by 1-s).
Counts how often the winner changes, and what the end states look like. Seed 20261002."""
import os, sys, collections, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from basins import matrix, run, R
N, GENS = int(sys.argv[1]), int(sys.argv[2])
n8, M8 = matrix(os.path.join(R, 'field', 'house.txt')); n9, M9 = matrix(os.path.join(R, 'field', 'house_repair1.txt'))
assert n9[:8] == n8 and np.allclose(M9[:8, :8], M8)
rng = np.random.default_rng(20261002); P8 = rng.dirichlet(np.ones(8), N)
E8 = run(M8, P8, GENS); w8 = E8.argmax(1)
def end_state(E, names): return ' + '.join(f'{names[i]}' for i in np.argsort(-E) if E[i] > 0.01)
print(f'{N} starts, {GENS} generations')
print('house alone, end states:', collections.Counter(end_state(e, n8) for e in E8).most_common(6))
for s in (0.01, 0.05, 0.2):
    P9 = np.hstack([P8 * (1 - s), np.full((N, 1), s)]); E9 = run(M9, P9, GENS); w9 = E9.argmax(1)
    flips = collections.Counter((n8[a], n9[b]) for a, b in zip(w8, w9) if n8[a] != n9[b])
    print(f'repair-1 added at {s:.0%}: winner changes in {sum(flips.values())}/{N} ({100*sum(flips.values())/N:.1f}%): {dict(flips.most_common(5))}; repair-1 final share max {E9[:, 8].max():.2e}')
    print('   end states:', collections.Counter(end_state(e, n9) for e in E9).most_common(5))
