#!/usr/bin/env python3
"""Exact expected scores for the noisy IPD: no sampling. Reads the same field file as ipd.py.
A pair of automata is a Markov chain over (state_a, state_b); each round both intended moves
are flipped independently with probability NOISE, and both players see the flipped moves."""
import sys, ipd

NOISE, ROUNDS = 0.05, 200
FLIP = {'C': 'D', 'D': 'C'}

def exact(a, b):
    dist = {(a['start'], b['start']): 1.0}; pa = pb = 0.0
    for _ in range(ROUNDS):
        nd = {}
        for (x, y), p in dist.items():
            for fa in (0, 1):
                for fb in (0, 1):
                    q = p * (NOISE if fa else 1 - NOISE) * (NOISE if fb else 1 - NOISE)
                    ma, mb = a['states'][x][0], b['states'][y][0]
                    if fa: ma = FLIP[ma]
                    if fb: mb = FLIP[mb]
                    u, v = ipd.PAY[(ma, mb)]; pa += q * u; pb += q * v
                    k = (a['states'][x][1][mb], b['states'][y][1][ma])
                    nd[k] = nd.get(k, 0.0) + q
        dist = nd
    return pa / ROUNDS, pb / ROUNDS

if __name__ == '__main__':
    S = ipd.load(sys.argv[1]); n = len(S); names = [s['name'] for s in S]
    M = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            x, y = exact(S[i], S[j]); M[i][j] = x; M[j][i] = y if i != j else (x + y) / 2
    rr = [sum(r) / n for r in M]
    print('round-robin, exact:')
    for i in sorted(range(n), key=lambda i: -rr[i]): print('  %-24s %.4f' % (names[i], rr[i]))
    for fl in (0.0, 1e-4):
        p = ipd.replicator(M, floor=fl)[-1]
        print('evolution, exact matrix, floor %g:' % fl)
        for i in sorted(range(n), key=lambda i: -p[i]): print('  %-24s %.4g' % (names[i], p[i]))
