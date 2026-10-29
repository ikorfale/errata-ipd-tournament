#!/usr/bin/env python3
"""Re-check of alex-730's claims on the IPD final (29.10): per-seed final shares (floor 1e-4 and 0),
and replicator trajectory under the exact matrix."""
import sys, json, statistics as st
R = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))); sys.path.insert(0, R)
import ipd, exact_ipd
path = R + '/field/final.txt'; salt = open(R + '/erratum/salt.txt').read().strip()
S = ipd.load(path); names = [s['name'] for s in S]; n = len(S); base = ipd.seed_of(path, salt)
out = {'names': names, 'base': '%x' % base, 'seeds': []}
for k in range(20):
    M = ipd.tournament(S, noise=0.05, reps=100, seed=base + k)
    row = {'k': k, 'rr': [sum(r) / n for r in M]}
    for fl in (0.0, 1e-4):
        h = ipd.replicator(M, floor=fl)
        row['f%g' % fl] = h[-1]; row['traj%g' % fl] = [h[g] for g in (200, 400, 600, 1000)]
    out['seeds'].append(row); print('seed', k, flush=True)
E = [[0.0] * n for _ in range(n)]
for i in range(n):
    for j in range(i, n):
        x, y = exact_ipd.exact(S[i], S[j]); E[i][j] = x; E[j][i] = y if i != j else (x + y) / 2
out['exact'] = E
for fl in (0.0, 1e-4):
    h = ipd.replicator(E, floor=fl); out['exact_traj%g' % fl] = {g: h[g] for g in (0, 200, 400, 600, 800, 1000)}
json.dump(out, open(R + '/erratum/dump.json', 'w'))
print('done')
