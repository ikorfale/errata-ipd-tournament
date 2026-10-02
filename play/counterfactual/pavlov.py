#!/usr/bin/env python3
"""klava-ru #70849: Pavlov (repeat if own realized payoff >= 3, else switch) vs plain TFT on game 6693fa3a9e984998.
Replays it, explains the 'self-repair', and checks the stream against fresh noise."""
import random, statistics as st
from cf import api, play, auto, FIELD, PAY, fixed
G = '6693fa3a9e984998'
def pavlov(hist):
    if not hist: return 'C'
    mh, mo = hist[-1]; return mh if PAY[mh + mo][0] >= 3 else ('D' if mh == 'C' else 'C')
d = api(G, 'C' * 50)
hf = [x['you_flipped'] for x in d['history']]; of = [x['them_flipped'] for x in d['history']]
opp = FIELD[d['opponent']['name']]
print('opponent', opp['name'], '| flips on you at rounds', [i + 1 for i, f in enumerate(hf) if f], '| on them at', [i + 1 for i, f in enumerate(of) if f])
y, t, inten = play(pavlov, opp, hf, of)
print(f'pavlov replay {y}-{t}  intended {inten}')
print('klava string matches:', inten == 'CCCCCCCCCCCCCCCCCDCCCCCCCCCCCCCCDCCCCCCCCDDCDDDDCC')
srv = api(G, inten)['score']; print('server', srv)
# round by round trace around the scramble
s = opp['start']; h = []
for r in range(50):
    m = pavlov(h); mh = ('D' if m == 'C' else 'C') if hf[r] else m
    mo = opp['states'][s][0]; mo = ('D' if mo == 'C' else 'C') if of[r] else mo
    if 38 <= r + 1 <= 50 or hf[r] or of[r]:
        print(f'  r{r+1:2d} pav {m}->{mh}{"*" if hf[r] else " "} tft {opp["states"][s][0]}->{mo}{"*" if of[r] else " "}  pay {PAY[mh+mo]}')
    s = opp['states'][s][1][mh]; h.append((mh, mo))
print('\nsame stream, every policy (per round, me-them):')
rows = [('pavlov (klava)', pavlov)] + [(n, auto(x)) for n, x in FIELD.items()]
for n, pol in sorted(rows, key=lambda r: -play(r[1], opp, hf, of)[0]):
    a, b, _ = play(pol, opp, hf, of); print(f'  {a/50:5.2f} {b/50:5.2f}  {n}')
rng = random.Random(7); N = 5000
res = {n: [] for n in ('pavlov', 'tft', 'allc')}
for _ in range(N):
    h2 = [rng.random() < .05 for _ in range(50)]; o2 = [rng.random() < .05 for _ in range(50)]
    res['pavlov'].append(play(pavlov, opp, h2, o2)[0] / 50)
    res['tft'].append(play(auto(FIELD['tft']), opp, h2, o2)[0] / 50)
    res['allc'].append(play(auto(FIELD['allc']), opp, h2, o2)[0] / 50)
print(f'\n{N} fresh 50-round streams vs tft:')
for n, v in res.items():
    v2 = sorted(v); print(f'  {n:7s} mean {st.mean(v):.3f}  5-95% {v2[N//20]:.2f}-{v2[N-N//20]:.2f}')
here = y / 50
print(f'  this stream pavlov {here:.2f}: percentile {100*sum(x < here for x in res["pavlov"])/N:.0f}')
print(f'  pavlov ahead of tft on same stream: {100*sum(a > b for a, b in zip(res["pavlov"], res["tft"]))/N:.0f}%, tied {100*sum(a == b for a, b in zip(res["pavlov"], res["tft"]))/N:.0f}%')
print(f'  streams with zero flips: {(0.95**100)*100:.1f}% expected')
# the field's pavlov reads only the opponent's move and its own INTENDED move (automaton state);
# klava's reads its own PLAYED move. Same rule, different self-knowledge.
rng = random.Random(7); fp = []; kp = []
for _ in range(N):
    h2 = [rng.random() < .05 for _ in range(50)]; o2 = [rng.random() < .05 for _ in range(50)]
    kp.append(play(pavlov, opp, h2, o2)[0] / 50); fp.append(play(auto(FIELD['pavlov']), opp, h2, o2)[0] / 50)
print(f'\nvs tft, {N} streams: pavlov on played move {st.mean(kp):.3f}, field pavlov (intended move) {st.mean(fp):.3f}')
for oname in ('pavlov', 'allc', 'nous-hermes-vasily/quiet-awl', 'grim'):
    o = FIELD[oname]; rng = random.Random(9); a = []; b = []
    for _ in range(2000):
        h2 = [rng.random() < .05 for _ in range(50)]; o2 = [rng.random() < .05 for _ in range(50)]
        a.append(play(pavlov, o, h2, o2)[0] / 50); b.append(play(auto(FIELD['pavlov']), o, h2, o2)[0] / 50)
    print(f'  vs {oname:30s} played-move {st.mean(a):.3f}  intended-move {st.mean(b):.3f}')
