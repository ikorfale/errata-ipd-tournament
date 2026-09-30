#!/usr/bin/env python3
"""Regimes for the fresh-field check. Each tested entry is evaluated ALONE in the same fresh field
(so the three agent entries do not score off each other), 1000 fields per regime, round-robin rank."""
import sys, random, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fresh'); import ipd, fresh_fields as f
F = ipd.load('field/final.txt'); by = {s['name']: s for s in F}
house = [s for s in F if '/' not in s['name']]
T = ['nous-hermes-vasily/quiet-awl', 'xboss-xoxomo/cross-cut', 'fable-ledger/knock-twice', 'tft', 'stft', 'pavlov', 'grim']
REG = {'small (1-3 states)': (1, 3), 'large (4-8 states)': (4, 8)}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
cache = {}
for rname, (lo, hi) in REG.items():
    rng = random.Random(20260930); out = {t: [] for t in T}
    for k in range(N):
        opp = rng.sample(house, 4) + [f.rand_fsm(rng, rng.randint(lo, hi), 'r%s_%d_%d' % (lo, k, j)) for j in range(10)]
        for t in T:
            field = [by[t]] + [o for o in opp if o['name'] != t]
            rank, rr = f.rr_ranks(field, cache); out[t].append(rank[t])
    print('regime: 4 house + 10 random %s, each tested entry alone, %d fields' % (rname, N))
    for t, v in out.items():
        v = np.array(v); print('  %-30s median %4.1f  1st %4d  top3 %4d  field size ~%d' % (t, np.median(v), (v == 1).sum(), (v <= 3).sum(), 15))
