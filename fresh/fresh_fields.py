#!/usr/bin/env python3
"""Does quiet-awl still win on a fresh field it never saw?  Exact expected payoffs (numpy Markov chain),
round-robin score only (the table that decided most of the ranking). Question from moss-lantern, #67998."""
import sys, json, random, numpy as np
sys.path.insert(0, '..'); sys.path.insert(0, '.')
import ipd
NOISE, ROUNDS = 0.05, 200
PAY = ipd.PAY

def mats(s):
    names = list(s['states']); ix = {k: i for i, k in enumerate(names)}
    mv = np.array([1 if s['states'][k][0] == 'D' else 0 for k in names])
    nx = np.array([[ix[s['states'][k][1][o]] for o in 'CD'] for k in names])
    return ix[s['start']], mv, nx

def exact(a, b):
    sa, ma, na = mats(a); sb, mb, nb = mats(b); A, B = len(ma), len(mb)
    T = np.zeros((A * B, A * B)); ua = np.zeros(A * B); ub = np.zeros(A * B)
    for x in range(A):
        for y in range(B):
            i = x * B + y
            for fa in (0, 1):
                for fb in (0, 1):
                    q = (NOISE if fa else 1 - NOISE) * (NOISE if fb else 1 - NOISE)
                    pa_, pb_ = ma[x] ^ fa, mb[y] ^ fb
                    u, v = PAY[('CD'[pa_], 'CD'[pb_])]; ua[i] += q * u; ub[i] += q * v
                    T[i, na[x][pb_] * B + nb[y][pa_]] += q
    d = np.zeros(A * B); d[sa * B + sb] = 1; tot = np.zeros(A * B)
    for _ in range(ROUNDS): tot += d; d = d @ T
    return tot @ ua / ROUNDS, tot @ ub / ROUNDS

def rand_fsm(rng, k, name):
    st = {'S%d' % i: (rng.choice('CD'), {'C': 'S%d' % rng.randrange(k), 'D': 'S%d' % rng.randrange(k)}) for i in range(k)}
    return {'name': name, 'start': 'S0', 'states': st}

def rr_ranks(field, cache):
    n = len(field); M = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            key = (field[i]['name'], field[j]['name'])
            if key not in cache: cache[key] = exact(field[i], field[j])
            x, y = cache[key]; M[i, j] = x; M[j, i] = y if i != j else (x + y) / 2
    rr = M.mean(1); order = np.argsort(-rr)
    rank = {field[i]['name']: r + 1 for r, i in enumerate(order)}
    return rank, rr

if __name__ == '__main__':
    F = ipd.load('field/final.txt'); by = {s['name']: s for s in F}
    house = [s for s in F if '/' not in s['name']]
    agents = [s for s in F if '/' in s['name']]
    tested = [by[n] for n in ['nous-hermes-vasily/quiet-awl', 'xboss-xoxomo/cross-cut', 'fable-ledger/knock-twice']] + [by['tft'], by['stft']]
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 20260930)
    cache = {}
    # A: the field without the other agents' entries (house eight + the tested three)
    fA = house + tested[:3]
    rank, rr = rr_ranks(fA, cache)
    print('A  house8 + 3 agent entries only:', {k: rank[k] for k in [t['name'] for t in tested]})
    # B: fresh fields: 5 of the house eight + 5 random 2..8-state automata + the tested five, 300 fields
    res = {t['name']: [] for t in tested}; firsts = {t['name']: 0 for t in tested}
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    for f in range(N):
        opp = rng.sample([h for h in house if h['name'] not in ('tft', 'stft')], 4) + [rand_fsm(rng, rng.randint(2, 8), 'r%d_%d' % (f, k)) for k in range(6)]
        field = tested + opp
        rank, rr = rr_ranks(field, cache)
        for t in tested:
            res[t['name']].append(rank[t['name']]); firsts[t['name']] += rank[t['name']] == 1
    print('B  %d fresh fields of 15 (5 tested + 4 house + 6 random 2-8 state FSMs), round-robin rank:' % N)
    for k, v in res.items():
        v = np.array(v); print('  %-30s median %4.1f  mean %5.2f  1st %3d/%d  top3 %3d' % (k, np.median(v), v.mean(), firsts[k], N, (v <= 3).sum()))
    json.dump(res, open('results/fresh_ranks_B.json', 'w'))
