"""quiet-awl has two regions: B-world {B, S543, S619} reachable only from its start S731 when the partner opens D,
and A-world {A, S324, S41, S830}, which has no exit. Fraction of games still in B-world after n rounds, and
noiseless per-round scores."""
from cf import *
import random
opp = FIELD['nous-hermes-vasily/quiet-awl']; BW = {'B', 'S543', 'S619'}
def track(strat, L, rng, noise=.05):
    s, sh = opp['start'], strat['start']; inB = []
    for r in range(L):
        mh = strat['states'][sh][0]; mo = opp['states'][s][0]
        if rng.random() < noise: mh = flipc(mh)
        if rng.random() < noise: mo = flipc(mo)
        s, sh = opp['states'][s][1][mh], strat['states'][sh][1][mo]; inB.append(s in BW)
    return inB
for n in ('stft', 'tft', 'alld', opp['name']):
    a, b, c = play(auto(FIELD[n]), opp, [False] * 200, [False] * 200)
    rng = random.Random(3); runs = [track(FIELD[n], 500, rng) for _ in range(2000)]
    frac = {k: sum(r[k - 1] for r in runs) / len(runs) for k in (2, 10, 50, 200, 500)}
    print(f"{n:30s} noiseless {a/200:.2f}-{b/200:.2f}  still in B-world after round " + '  '.join(f"{k}: {v:.0%}" for k, v in frac.items()))
