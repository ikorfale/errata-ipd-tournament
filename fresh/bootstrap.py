#!/usr/bin/env python3
"""Comparable composition: opponents resampled with replacement from the real field (minus the tested entry),
12 opponents, 2000 fields; the tested entry alone. Round-robin rank of the tested entry."""
import sys, random, copy, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fresh'); import ipd, fresh_fields as f
F = ipd.load('field/final.txt'); by = {s['name']: s for s in F}
T = ['nous-hermes-vasily/quiet-awl', 'xboss-xoxomo/cross-cut', 'fable-ledger/knock-twice', 'stft', 'alternator']
rng = random.Random(20260930); N = 2000; cache = {}; out = {t: [] for t in T}
for k in range(N):
    picks = [rng.randrange(len(F)) for _ in range(12)]
    for t in T:
        pool = [s for s in F if s['name'] != t]
        opp = []
        for j, p in enumerate(picks):
            s = pool[p % len(pool)]; c = dict(s); c['name'] = s['name'] + '#%d' % j; opp.append(c)
        field = [by[t]] + opp
        # cache by base names
        n = len(field); M = np.zeros((n, n))
        for i in range(n):
            for jj in range(i, n):
                a, b = field[i]['name'].split('#')[0], field[jj]['name'].split('#')[0]
                if (a, b) not in cache: cache[(a, b)] = f.exact(by[a], by[b])
                x, y = cache[(a, b)]; M[i, jj] = x; M[jj, i] = y if i != jj else (x + y) / 2
        rr = M.mean(1); out[t].append(1 + int((rr[1:] > rr[0]).sum()))
print('bootstrap of the real field, 12 opponents with replacement, tested alone, %d fields' % N)
for t, v in out.items():
    v = np.array(v); print('  %-30s median %4.1f  1st %4d  top3 %4d' % (t, np.median(v), (v == 1).sum(), (v <= 3).sum()))
