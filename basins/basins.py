"""Replicator basins for the noisy-IPD house field, with and without margin-lantern's repair-1.
Exact payoff matrices from exact_ipd.py (200 rounds, 5% independent flips). Discrete replicator dynamics
(same update as ipd.replicator) vectorised over many Dirichlet(1) starting mixes. Seed 20261002."""
import os, sys, json, numpy as np
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); sys.path.insert(0, R); import ipd, exact_ipd
def matrix(path):
    S = ipd.load(path); n = len(S); M = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            x, y = exact_ipd.exact(S[i], S[j]); M[i, j] = x; M[j, i] = y if i != j else (x + y) / 2
    return [s['name'] for s in S], M
def run(M, P, gens):
    for _ in range(gens):
        F = P @ M.T; P = P * F / (P * F).sum(1, keepdims=True)
    return P
if __name__ == '__main__':
    N, GENS = int(sys.argv[1]), int(sys.argv[2])
    rng = np.random.default_rng(20261002)
    out = {}
    for tag, path in [('house', os.path.join(R, 'field', 'house.txt')), ('house+repair1', os.path.join(R, 'field', 'house_repair1.txt'))]:
        names, M = matrix(path); n = len(names)
        U = np.full((1, n), 1 / n)
        for g in (1000, GENS):
            u = run(M, U, g)[0]; print(tag, 'uniform start, gens', g, {names[i]: round(float(u[i]), 4) for i in np.argsort(-u)[:4]})
        P0 = rng.dirichlet(np.ones(n), N); P = run(M, P0, GENS)
        win = P.argmax(1); top = P.max(1)
        counts = {names[i]: int((win == i).sum()) for i in range(n) if (win == i).any()}
        print(tag, f'{N} random starts, gens {GENS}: winner counts', counts, f'| winner share median {np.median(top):.3f}, <0.99 in {(top < 0.99).mean()*100:.1f}%')
        out[tag] = dict(names=names, M=M.tolist(), P0=P0.tolist(), win=win.tolist(), top=top.tolist())
    json.dump(out, open(os.path.join(R, 'basins', 'basins.json'), 'w'))
