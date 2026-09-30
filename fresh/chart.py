#!/usr/bin/env python3
"""Share of fields won (round-robin 1st) by each agent entry, per regime; numbers from results/fresh_*.txt."""
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, numpy as np
reg = ['Reshuffled real roster\n(2000 fields)', 'Random 1-3 state\nautomata (1000)', 'Random 4-8 state\nautomata (1000)']
data = {'quiet-awl (winner)': [1553/2000, 91/1000, 68/1000], 'cross-cut': [760/2000, 159/1000, 262/1000], 'knock-twice': [408/2000, 191/1000, 581/1000]}
col = ['#c0392b', '#7f8c8d', '#2c3e50']
fig, ax = plt.subplots(figsize=(8, 4.2)); x = np.arange(3); w = 0.26
for k, (n, v) in enumerate(data.items()):
    b = ax.bar(x + (k - 1) * w, v, w, label=n, color=col[k])
    for r, val in zip(b, v): ax.text(r.get_x() + w / 2, val + 0.01, '%d%%' % round(val * 100), ha='center', fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(reg); ax.set_ylabel('share of fields where it places 1st'); ax.set_ylim(0, 0.9)
ax.set_title('Does the tournament winner still win on a field it never saw?\n(each entry alone in the field, exact expected payoffs, 5% noise)', fontsize=10)
ax.spines[['top', 'right']].set_visible(False); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig('assets/fresh_fields.png', dpi=140)
