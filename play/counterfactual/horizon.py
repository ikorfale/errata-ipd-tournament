"""Does the opening matter more in short games? STFT, quiet-awl's clone and TFT vs quiet-awl, per-round score by
game length, 3000 fresh noise streams per length (random.Random(11)), all three strategies on the same stream."""
from cf import *
import random, statistics as st
opp = FIELD['nous-hermes-vasily/quiet-awl']; rng = random.Random(11)
for L in (10, 20, 50, 100, 200, 500):
    S = [([rng.random() < .05 for _ in range(L)], [rng.random() < .05 for _ in range(L)]) for _ in range(3000)]
    m = {n: [play(auto(FIELD[n]), opp, a, b)[0] / L for a, b in S] for n in ('tft', 'stft', opp['name'])}
    d = [x - y for x, y in zip(m['stft'], m['tft'])]
    print(f"rounds {L:3d}: tft {st.mean(m['tft']):.3f}  stft {st.mean(m['stft']):.3f}  clone {st.mean(m[opp['name']]):.3f}  stft-tft {st.mean(d):+.3f} (ahead {sum(x > 0 for x in d) / len(d):.0%})")
