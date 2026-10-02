"""Knock-out tests for the mechanism (same starts as paired.py, newcomer at 20%):
(a) the newcomer is a second tf2t; (b) repair-1, but alternator earns against it only what tft does (3.023 instead of 3.738);
(c) repair-1, but grim earns against pavlov only what tft does (removes grim's prey advantage)."""
import sys, numpy as np
sys.path.insert(0, '/home/board/work/lab/ipd/basins'); from basins import matrix, run
n8, M8 = matrix('/home/board/work/lab/ipd/house.txt'); n9, M9 = matrix('/home/board/work/lab/ipd/house_repair1.txt')
N, GENS, s = 2000, 20000, 0.2
rng = np.random.default_rng(20261002); P8 = rng.dirichlet(np.ones(8), N)
P9 = np.hstack([P8 * (1 - s), np.full((N, 1), s)])
G, T, F2, AL, PV, R = (n9.index(x) for x in ('grim', 'tft', 'tf2t', 'alternator', 'pavlov', 'repair1'))
def flips(M8x, M9x, merge=None):
    a = run(M8x, P8, GENS).argmax(1); b = run(M9x, P9, GENS).argmax(1)
    if merge is not None: b = np.where(b == R, merge, b)
    return int(((a == G) & (b == T)).sum()), int(((a == T) & (b == G)).sum())
print('repair-1 as is: grim->tft %d, tft->grim %d' % flips(M8, M9))
M = M9.copy(); M[R, :] = M9[F2, :]; M[:, R] = M9[:, F2]; M[R, R] = M9[F2, F2]
print('(a) newcomer = second tf2t: grim->tft %d, tft->grim %d' % flips(M8, M, F2))
M = M9.copy(); M[AL, R] = M9[T, R]
print('(b) alternator gets only %.3f vs repair-1: grim->tft %d, tft->grim %d' % ((M9[T, R],) + flips(M8, M)))
M = M9.copy(); M[G, PV] = M9[T, PV]; Mh = M8.copy(); Mh[G, PV] = M8[T, PV]
print('(c) grim earns vs pavlov only what tft does, in both fields: grim->tft %d, tft->grim %d' % flips(Mh, M))
