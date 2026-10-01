#!/usr/bin/env python3
"""Same families as comparable.py, but the three agent entries share each field: 3 entries + 10 opponents,
k of them grim-likes. Who places highest among the three, and is quiet-awl 1st overall?"""
import sys, random, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fresh')
import comparable as c
rng = random.Random(20261002); N = 500
print('sanity (row player payoff): tf1t-alld %.3f  grim1-allc %.3f  wsls-wsls %.3f  tf1t-tf1t %.3f  punish12-tf1t %.3f' % (
    c.pay('tf1t', 'alld_')[0], c.pay('grim1', 'allc_')[0], c.pay('wsls', 'wsls')[0], c.pay('tf1t', 'tf1t')[0], c.pay('punish12', 'tf1t')[0]))
print('fields of 13 = 3 entries + 10 opponents, k grim-likes; %d fields per k; %% of fields each entry is best of the three | %% 1st overall' % N)
for k in range(0, 8):
    best = {t: 0 for t in c.T}; first = {t: 0 for t in c.T}
    for _ in range(N):
        fl = c.T + [rng.choice(c.HARD)['name'] for _ in range(k)] + [rng.choice(c.FORG)['name'] for _ in range(10 - k)]
        n = len(fl); M = np.zeros((n, n))
        for i in range(n):
            for j in range(i, n):
                x, y = c.pay(fl[i], fl[j]); M[i, j] = x; M[j, i] = y if i != j else (x + y) / 2
        rr = M.mean(1); best[c.T[int(np.argmax(rr[:3]))]] += 1
        for i, t in enumerate(c.T): first[t] += rr[i] >= rr.max() - 1e-12
    print('k=%d  ' % k + '  '.join('%s %3.0f%%|%3.0f%%' % (t.split('/')[1], 100 * best[t] / N, 100 * first[t] / N) for t in c.T))
