"""Chart for the co-evolving leave rule: share of each leave rule by generation, 20 seeds per noise level (leave_coevo.json)."""
import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = json.load(open('leave_coevo.json')); R = d['rules']; K = len(d['names'])
COL = {'never': '#2a78d6', 'after2': '#eb6834', 'after1': '#1baf7a'}
SHORT = {'never': 'never', 'after2': '2 Ds', 'after1': 'any D'}
LAB = {'never': 'never leave', 'after2': 'leave after 2 Ds in a row', 'after1': 'leave after any D'}
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True, facecolor='#fcfcfb')
for ax, nz in zip(axs, ('0.01', '0.05')):
    H = np.array(d['runs'][nz]['history']).reshape(20, -1, K, 3).sum(2)   # seed x gen x rule
    g = np.arange(H.shape[1])
    for j, r in enumerate(R):
        for s in range(H.shape[0]): ax.plot(g, H[s, :, j], color=COL[r], lw=0.6, alpha=0.18)
        m = H[:, :, j].mean(0); ax.plot(g, m, color=COL[r], lw=2.2, label=LAB[r])
        ax.text(g[-1] + 1.5, m[-1], f'{SHORT[r]} {m[-1]:.0%}', va='center', fontsize=9.5, color='#333')
    ax.set_title(f'{float(nz):.0%} noise', loc='left', fontsize=12, color='#222')
    ax.set_xlim(0, 60); ax.set_ylim(0, 1); ax.set_xlabel('generation', color='#555')
    ax.set_facecolor('#fcfcfb'); ax.grid(axis='y', color='#e6e6e3', lw=0.8)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'): ax.spines[sp].set_color('#bbb')
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.tick_params(colors='#555')
axs[0].set_ylabel('share of population carrying the rule', color='#555')
axs[0].legend(loc='upper left', frameon=False, fontsize=9.5)
fig.suptitle('Which leave rule evolves? Thick line: mean of 20 seeds; thin lines: each seed', x=0.01, ha='left', fontsize=12.5, color='#222')
fig.tight_layout(rect=(0, 0, 0.95, 1)); fig.subplots_adjust(wspace=0.22)
fig.savefig('leave_coevo.png', dpi=130); print('ok', {nz: [round(float(x), 3) for x in np.array(d['runs'][nz]['history']).reshape(20, -1, K, 3).sum(2)[:, -1].mean(0)] for nz in ('0.01', '0.05')})
