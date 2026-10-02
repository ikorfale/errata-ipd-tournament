"""Why does a repair-1 that always dies out move starts from grim's basin to TFT's? (errata, 2026-10-02, plan #17)
Same seed/starts as paired.py (20% share). For starts whose winner flips grim -> tft, follow the first 50
generations and split the fitness gap tft - grim into the part earned against repair-1 and the rest."""
import sys, numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from basins import matrix, run, R
n8, M8 = matrix(os.path.join(R, 'field', 'house.txt')); n9, M9 = matrix(os.path.join(R, 'field', 'house_repair1.txt'))
N, GENS, s = 2000, 20000, 0.2
rng = np.random.default_rng(20261002); P8 = rng.dirichlet(np.ones(8), N)
w8 = run(M8, P8, GENS).argmax(1)
P9 = np.hstack([P8 * (1 - s), np.full((N, 1), s)]); w9 = run(M9, P9, GENS).argmax(1)
T, G, R = n9.index('tft'), n9.index('grim'), 8
print('payoff per round, row vs column (200 rounds, 5% noise):')
print('%-12s' % '' + ''.join('%11s' % c for c in n9))
for i in range(9): print('%-12s' % n9[i] + ''.join('%11.3f' % M9[i, j] for j in range(9)))
print('tft minus grim, against each opponent:', {n9[j]: round(M9[T, j] - M9[G, j], 3) for j in range(9)})
flip = np.where((w8 == G) & (w9 == T))[0]; stay = np.where((w8 == G) & (w9 == G))[0]
print(f'grim->tft flips: {len(flip)}, grim stays grim: {len(stay)}')
def follow(idx, gens=50):
    P = P9[idx].copy(); gap_r = np.zeros(len(idx)); gap_o = np.zeros(len(idx)); share = []
    for g in range(gens):
        d = M9[T] - M9[G]                       # tft - grim payoff against each opponent
        gap_r += P[:, R] * d[R]; gap_o += P[:, :R] @ d[:R]; share.append(P[:, R].mean())
        F = P @ M9.T; P = P * F / (P * F).sum(1, keepdims=True)
    return gap_r / gens, gap_o / gens, np.array(share), P
for name, idx in (('flip', flip), ('stay', stay)):
    gr, go, sh, P = follow(idx)
    print(f'{name}: mean tft-grim fitness gap over gens 0-49: from repair-1 {gr.mean():+.4f}, from everyone else {go.mean():+.4f}; '
          f'repair-1 share gen 0/10/49: {sh[0]:.3f}/{sh[10]:.3f}/{sh[49]:.3f}; tft/grim share at gen 50: {P[:, T].mean():.3f}/{P[:, G].mean():.3f}')
# counterfactual: same starts, repair-1's row/column copied from tft (a newcomer that plays like tft)
for label, j in (('a second tft', T), ('a second grim', G)):
    M = M9.copy(); M[R, :] = M9[j, :]; M[:, R] = M9[:, j]; M[R, R] = M9[j, j]
    w = run(M, P9, GENS); wn = w.argmax(1); wn = np.where(wn == R, j, wn)
    print(f'newcomer = {label} at 20%: grim->tft flips {int(((w8 == G) & (wn == T)).sum())}, tft->grim {int(((w8 == T) & (wn == G)).sum())}')
P0 = P9[flip]; print('flipped starts: mean initial share tft %.3f grim %.3f (all grim-basin starts: tft %.3f grim %.3f)' % (
    P0[:, T].mean(), P0[:, G].mean(), P9[w8 == G][:, T].mean(), P9[w8 == G][:, G].mean()))
