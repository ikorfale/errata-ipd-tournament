#!/usr/bin/env python3
"""moss-lantern #68122: a fresh field of *comparable composition*. Opponents come from two hand-written families
the entries never saw by name: forgivers and grim-likes. Each tested entry plays alone against 12 opponents;
k of them grim-likes (k = 0..8), the rest forgivers, drawn with replacement. Exact payoffs, 5% noise,
200 rounds, round-robin rank. The real field had about 4 hard opponents in 12 (alld, grim, stft, alternator)."""
import sys, random, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fresh'); import ipd, fresh_fields as f

def fsm(name, start, st): return {'name': name, 'start': start, 'states': st}
def tfnt(n, sus=False):   # tit-for-n-tats: defect after n consecutive D, back on the first C
    st = {'c%d' % k: ('C', {'C': 'c0', 'D': 'c%d' % (k + 1) if k + 1 < n else 'd'}) for k in range(n)}
    st['d'] = ('D', {'C': 'c0', 'D': 'd'}); return fsm(('s' if sus else '') + 'tf%dt' % n, 'd' if sus else 'c0', st)
def punish(p):            # after any D, defect p rounds whatever happens, then forgive
    st = {'c': ('C', {'C': 'c', 'D': 'p1'})}
    for i in range(1, p + 1): nx = 'p%d' % (i + 1) if i < p else 'c'; st['p%d' % i] = ('D', {'C': nx, 'D': nx})
    return fsm('punish%d' % p, 'c', st)
def grim(m):              # defect forever after m total D
    st = {'c%d' % k: ('C', {'C': 'c%d' % k, 'D': 'c%d' % (k + 1) if k + 1 < m else 'g'}) for k in range(m)}
    st['g'] = ('D', {'C': 'g', 'D': 'g'}); return fsm('grim%d' % m, 'c0', st)
allc = fsm('allc_', 'c', {'c': ('C', {'C': 'c', 'D': 'c'})}); alld = fsm('alld_', 'd', {'d': ('D', {'C': 'd', 'D': 'd'})})
wsls = fsm('wsls', 'C', {'C': ('C', {'C': 'C', 'D': 'D'}), 'D': ('D', {'C': 'D', 'D': 'C'})})
FORG = [allc, tfnt(1), tfnt(2), tfnt(3), punish(1), punish(2), wsls]
HARD = [grim(1), grim(2), grim(3), alld, punish(5), punish(12), tfnt(1, sus=True)]
F = ipd.load('field/final.txt'); by = {s['name']: s for s in F}
T = ['nous-hermes-vasily/quiet-awl', 'xboss-xoxomo/cross-cut', 'fable-ledger/knock-twice']
P = {s['name']: s for s in FORG + HARD}; P.update({t: by[t] for t in T})
cache = {}
def pay(a, b):
    if (a, b) not in cache: cache[(a, b)] = f.exact(P[a], P[b])
    return cache[(a, b)]
if __name__ == '__main__':
    rng = random.Random(20261001); N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    print('fields of 13: tested entry alone + 12 opponents, k grim-likes; %d fields per k; share of fields where the entry is 1st (median rank)' % N)
    print('k   ' + ''.join('%-22s' % t.split('/')[1] for t in T))
    for k in range(0, 9):
        first = {t: 0 for t in T}; ranks = {t: [] for t in T}
        for _ in range(N):
            opp = [rng.choice(HARD)['name'] for _ in range(k)] + [rng.choice(FORG)['name'] for _ in range(12 - k)]
            for t in T:
                fl = [t] + opp; n = len(fl); M = np.zeros((n, n))
                for i in range(n):
                    for j in range(i, n):
                        x, y = pay(fl[i], fl[j]); M[i, j] = x; M[j, i] = y if i != j else (x + y) / 2
                rr = M.mean(1); r = 1 + int((rr[1:] > rr[0] + 1e-12).sum()); ranks[t].append(r); first[t] += r == 1
        print('%d   ' % k + ''.join('%-22s' % ('%3.0f%% (med %g)' % (100 * first[t] / N, np.median(ranks[t]))) for t in T))
