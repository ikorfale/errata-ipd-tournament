"""Does replaying on the same flip stream (same game id) really remove the luck term? SD of the
difference between two strategies against the same opponent: independent flips vs shared flips."""
import numpy as np, sys
sys.argv = ['x']; exec(open('sd_check.py').read().split('for a, b in')[0])
def game_f(a, b, fa, fb, gr, n=50):
    ha, hb, s = [], [], 0
    for t in range(n):
        x, y = a(ha, hb, gr), b(hb, ha, gr)
        if fa[t]: x = 1 - x
        if fb[t]: y = 1 - y
        ha.append(x); hb.append(y); s += PAY[(x, y)]
    return s / n
rs = np.random.default_rng(5)
for A, B, O in [('TFT','GTFT10','Pavlov'),('TFT','Pavlov','TFT'),('GTFT10','TFT','TFT'),('TFT','ALLD','Pavlov')]:
    ind, sh = [], []
    for _ in range(3000):
        f = [rs.random(50) < .05 for _ in range(4)]
        ind.append(game_f(S[A], S[O], f[0], f[1], rs) - game_f(S[B], S[O], f[2], f[3], rs))
        sh.append(game_f(S[A], S[O], f[0], f[1], rs) - game_f(S[B], S[O], f[0], f[1], rs))
    ind, sh = np.array(ind), np.array(sh)
    print(f'{A} minus {B} vs {O}: mean {ind.mean():+.3f}/{sh.mean():+.3f}  SD independent {ind.std(ddof=1):.3f}  shared flips {sh.std(ddof=1):.3f}')
