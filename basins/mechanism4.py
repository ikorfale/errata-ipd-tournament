"""Puzzle from mechanism.py: a second grim at 20% flips 356 starts grim->tft. (errata, 2026-10-02)
1) Recount with the clone merged into grim (sum of columns), so a split grim cannot lose the argmax.
2) Hypothesis: extra grim kills pavlov (grim's prey) early, then grim starves. Follow flipped starts.
3) Knock-out: same extra grim, but pavlov earns against grim what TFT earns against grim (pavlov no longer collapses faster)."""
import sys, numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from basins import matrix, run, R
n8, M8 = matrix(os.path.join(R, 'field', 'house.txt'))
N, GENS, s = 2000, 20000, 0.2
rng = np.random.default_rng(20261002); P8 = rng.dirichlet(np.ones(8), N)
G, T, V, A = n8.index('grim'), n8.index('tft'), n8.index('pavlov'), n8.index('alternator')
w8 = run(M8, P8, GENS).argmax(1)
def extra_grim(M, P0):
    Q = P0 * (1 - s); Q[:, G] += s; return Q          # a clone of grim is the same as more grim
Q = extra_grim(M8, P8); wq = run(M8, Q, GENS).argmax(1)
print(f'1) extra grim merged: grim->tft {int(((w8 == G) & (wq == T)).sum())}, tft->grim {int(((w8 == T) & (wq == G)).sum())}, '
      f'end states with extra grim: ' + str({n8[i]: int((wq == i).sum()) for i in set(wq.tolist())}))
flip = (w8 == G) & (wq == T); print('   flipped starts:', int(flip.sum()))
a, b, done = P8[flip], Q[flip], 0
print('   gen   without extra grim: pavlov grim tft alternator | with: pavlov grim tft alternator | grim fitness - tft fitness (without | with)')
for g in (0, 5, 10, 25, 50, 100, 200):
    a = run(M8, a, g - done); b = run(M8, b, g - done); done = g
    fa = a @ M8.T; fb = b @ M8.T
    print(f'   {g:3d}   ' + ' '.join(f'{a[:, i].mean():.3f}' for i in (V, G, T, A)) + '  |  ' + ' '.join(f'{b[:, i].mean():.3f}' for i in (V, G, T, A))
          + f'  |  {(fa[:, G] - fa[:, T]).mean():+.3f} {(fb[:, G] - fb[:, T]).mean():+.3f}')
M = M8.copy(); M[V, G] = M8[T, G]; M[G, V] = M8[G, T]   # pavlov vs grim behaves like tft vs grim, both directions
wk0 = run(M, P8, GENS).argmax(1); wk = run(M, extra_grim(M, P8), GENS).argmax(1)
print(f'3) knock-out (pavlov-grim pair played like tft-grim): extra grim flips grim->tft {int(((wk0 == G) & (wk == T)).sum())}, tft->grim {int(((wk0 == T) & (wk == G)).sum())}')
print(f'   payoffs: pavlov vs grim {M8[V, G]:.3f}, grim vs pavlov {M8[G, V]:.3f}, tft vs grim {M8[T, G]:.3f}, grim vs tft {M8[G, T]:.3f}')
