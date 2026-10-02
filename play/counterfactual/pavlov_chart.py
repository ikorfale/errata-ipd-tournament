#!/usr/bin/env python3
"""Chart for #70850: per-round score against TFT over 5000 fresh 50-round noisy streams (seed 7, as pavlov.py)."""
import os, random, statistics as st
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from cf import play, auto, FIELD, PAY
def pavlov(hist):
    if not hist: return 'C'
    mh, mo = hist[-1]; return mh if PAY[mh + mo][0] >= 3 else ('D' if mh == 'C' else 'C')
opp = FIELD['tft']; rng = random.Random(7); N = 5000
res = {'Pavlov (reads its played move)': [], 'TFT': [], 'Always cooperate': []}
pols = [pavlov, auto(FIELD['tft']), auto(FIELD['allc'])]
for _ in range(N):
    h = [rng.random() < .05 for _ in range(50)]; o = [rng.random() < .05 for _ in range(50)]
    for (k, v), p in zip(res.items(), pols): v.append(play(p, opp, h, o)[0] / 50)
cols = ['#2a78d6', '#eb6834', '#1baf7a']; ink, ink2 = '#0b0b0b', '#52514e'
fig, axs = plt.subplots(3, 1, figsize=(10, 6.2), sharex=True, facecolor='#fcfcfb')
bins = [x / 50 for x in range(40, 160, 3)]
for ax, (k, v), c in zip(axs, res.items(), cols):
    ax.set_facecolor('#fcfcfb'); ax.hist(v, bins=bins, color=c, edgecolor='#fcfcfb', linewidth=2)
    m = st.mean(v); ax.axvline(m, color=ink, lw=1.2)
    ax.text(0.01, 0.82, f'{k}', transform=ax.transAxes, color=ink, fontsize=12, weight='bold')
    ax.text(0.01, 0.64, f'mean {m:.2f}', transform=ax.transAxes, color=ink2, fontsize=11)
    ax.axvline(2.80, color=ink2, lw=1.2, ls='--')
    for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
    ax.set_yticks([]); ax.tick_params(colors=ink2)
axs[0].text(2.81, axs[0].get_ylim()[1] * 0.85, "klava-ru's game: 2.80\n(95th percentile for Pavlov)", color=ink2, fontsize=10, va='top')
axs[-1].set_xlabel('points per round against TFT, one 50-round game with 5% noise per move (5000 games each)', color=ink2)
fig.suptitle('Pavlov against TFT: a lucky 2.80, an average 2.36', x=0.01, ha='left', color=ink, fontsize=15, weight='bold')
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pavlov_vs_tft.png'), dpi=120, facecolor='#fcfcfb')
print({k: round(st.mean(v), 3) for k, v in res.items()})
