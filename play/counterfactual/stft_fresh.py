"""Every field strategy vs quiet-awl on 5000 fresh 50-round noise streams, compared to TFT on the same stream.
Output: stft_fresh.txt."""
from cf import *
import random, statistics as st
opp = FIELD['nous-hermes-vasily/quiet-awl']; rng = random.Random(7)
streams = [([rng.random() < .05 for _ in range(50)], [rng.random() < .05 for _ in range(50)]) for _ in range(5000)]
res = {n: [play(auto(FIELD[n]), opp, a, b)[0] / 50 for a, b in streams] for n in FIELD}
tft = res['tft']
for n, v in sorted(res.items(), key=lambda kv: -st.mean(kv[1]))[:5]:
    d = [x - y for x, y in zip(v, tft)]
    print(f"{n:45s} mean {st.mean(v):.3f}  minus TFT on same stream: mean {st.mean(d):+.3f}, wins {sum(x > 0 for x in d) / len(d):.0%}")
print('5000 fresh 50-round streams vs quiet-awl, seed 7')
