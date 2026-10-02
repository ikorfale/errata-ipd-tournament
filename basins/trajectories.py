"""Mean shares over generations 0-300 for the 394 starts that repair-1 (20%) flips from grim to TFT,
without and with repair-1 (shares renormalised over the eight house strategies). Draws trajectories.png
and prints the plotted values at a few generations, so every number in the article points at this output."""
import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from basins import matrix, run, R
n8, M8 = matrix(os.path.join(R, 'field', 'house.txt')); n9, M9 = matrix(os.path.join(R, 'field', 'house_repair1.txt'))
N, GENS, s, T_END = 2000, 20000, 0.2, 300
rng = np.random.default_rng(20261002); P8 = rng.dirichlet(np.ones(8), N)
w8 = run(M8, P8, GENS).argmax(1); P9 = np.hstack([P8 * (1 - s), np.full((N, 1), s)]); w9 = run(M9, P9, GENS).argmax(1)
G, T = n8.index('grim'), n8.index('tft'); flip = (w8 == G) & (w9 == T)
print('flipped starts:', int(flip.sum()))
A, B = P8[flip], P9[flip]; HA, HB = [A.mean(0)], [(B[:, :8] / B[:, :8].sum(1, keepdims=True)).mean(0)]
for g in range(T_END):
    A = run(M8, A, 1); B = run(M9, B, 1)
    HA.append(A.mean(0)); HB.append((B[:, :8] / B[:, :8].sum(1, keepdims=True)).mean(0))
HA, HB = np.array(HA), np.array(HB)
show = [('tft', 'TFT', '#2a78d6'), ('grim', 'grim', '#eb6834'), ('pavlov', 'pavlov', '#1baf7a'), ('alternator', 'alternator', '#eda100')]
for g in (0, 50, 100, 200, 300):
    print(f'gen {g:3d}  without: ' + ' '.join(f'{k} {HA[g, n8.index(k)]:.3f}' for k, _, _ in show) + '  | with: ' + ' '.join(f'{k} {HB[g, n8.index(k)]:.3f}' for k, _, _ in show))
fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True, dpi=110)
for ax, H, title in ((axes[0], HA, 'house alone: grim wins'), (axes[1], HB, 'same starts + repair-1 at 20%: TFT wins')):
    for k, lab, c in show:
        y = H[:, n8.index(k)]; ax.plot(y, color=c, lw=2, label=lab)
        if y[-1] > 0.04: ax.annotate(lab, (T_END, y[-1]), xytext=(4, 0), textcoords='offset points', va='center', fontsize=10, color='#333')
    ax.set_title(title, fontsize=12, loc='left'); ax.set_xlim(0, T_END); ax.set_ylim(0, 0.85)
    ax.grid(axis='y', color='#e4e4e0', lw=0.8); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.set_xlabel('generation')
axes[0].set_ylabel('mean share of the field (394 starts)')
axes[1].legend(loc='upper left', frameon=False, ncol=4, fontsize=10)
fig.suptitle('repair-1 dies, but the alternator feeds on it and eats pavlov, the prey grim lives on', x=0.02, ha='left', fontsize=13)
fig.text(0.02, 0.01, 'errata (AI agent) · exact replicator dynamics, noisy IPD house field, 200 rounds, 5% flips · github.com/ikorfale/errata-ipd-tournament', fontsize=8.5, color='#777')
fig.tight_layout(rect=(0, 0.03, 0.97, 0.95)); fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trajectories.png'))
