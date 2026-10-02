"""Follow-up to mechanism.py: for the grim->tft flips, run each start with and without repair-1 (20%)
and compare the other strategies' shares (renormalised without repair-1) at gens 10, 25, 50, 100, 200."""
import sys, numpy as np
sys.path.insert(0, '/home/board/work/lab/ipd/basins'); from basins import matrix, run
n8, M8 = matrix('/home/board/work/lab/ipd/house.txt'); n9, M9 = matrix('/home/board/work/lab/ipd/house_repair1.txt')
N, GENS, s = 2000, 20000, 0.2
rng = np.random.default_rng(20261002); P8 = rng.dirichlet(np.ones(8), N)
w8 = run(M8, P8, GENS).argmax(1); P9 = np.hstack([P8 * (1 - s), np.full((N, 1), s)]); w9 = run(M9, P9, GENS).argmax(1)
G, T = n8.index('grim'), n8.index('tft'); flip = (w8 == G) & (w9 == T)
A, B, done = P8[flip], P9[flip], 0
for g in (10, 25, 50, 100, 200):
    A = run(M8, A, g - done); B = run(M9, B, g - done); done = g
    Bn = B[:, :8] / B[:, :8].sum(1, keepdims=True)
    print(f'gen {g:3d}  repair-1 {B[:, 8].mean():.3f} | ' + '  '.join(f'{n8[i]} {A[:, i].mean():.3f}->{Bn[:, i].mean():.3f}' for i in range(8)))
