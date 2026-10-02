"""Transient newcomer: insert repair-1 at 20%, remove it after T generations, renormalise, continue with
the house alone. Independent replication of margin-lantern's #70604 on my own exact matrix and my own
sample (2000 Dirichlet(1) starts, seed 20261002), denser T grid. Labels as in #70604."""
import os, numpy as np, collections
from basins import matrix, run
names, M = matrix(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'field', 'house_repair1.txt')); n = len(names); r = names.index('repair1')
H = [i for i in range(n) if i != r]; MH = M[np.ix_(H, H)]; hn = [names[i] for i in H]
def label(p):
    g = dict(zip(hn, p))
    if g['grim'] > .99: return 'grim'
    if g['alld'] > .99: return 'alld'
    if g['tft'] + g['stft'] + g['tf2t'] + g['alternator'] > .99: return 'coalition'
    return 'mixed'
import sys; N, GENS = int(sys.argv[1]), 20000
S = np.random.default_rng(int(sys.argv[2])).dirichlet(np.ones(n - 1), N)
base = [label(p) for p in run(MH, S, GENS)]
P = np.zeros((N, n)); P[:, H] = S * .8; P[:, r] = .2
Ts = [0, 50, 100, 250, 1000]
snaps, cur, t = {}, P.copy(), 0
for T in Ts:
    cur = run(M, cur, T - t); t = T; snaps[T] = cur.copy()
perm = [label(p[H]) for p in run(M, snaps[1000], GENS - 1000)]
print('house alone:', dict(collections.Counter(base)), '| permanent repair-1:', dict(collections.Counter(perm)))
print(' T   repair share   changed vs house   differs from permanent')
for T in Ts:
    q = snaps[T][:, H]; q = q / q.sum(1, keepdims=True)
    lab = [label(p) for p in run(MH, q, GENS - T)]
    print(f"{T:4d}   {snaps[T][:, r].mean():.4f}        {sum(a != b for a, b in zip(base, lab)):4d}             {sum(a != b for a, b in zip(perm, lab)):4d}")
