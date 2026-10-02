"""Stacked bars from paired_2000x20000.txt: which end state 2000 random starting mixes reach, as repair-1's starting share grows."""
import re, ast, os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.abspath(__file__)); txt = open(os.path.join(D, 'paired_2000x20000.txt')).read()
rows = [('house alone', ast.literal_eval(re.search(r'house alone, end states: (\[.*\])', txt).group(1)))]
for s, l in re.findall(r'added at (\d+)%.*?\n   end states: (\[.*\])', txt): rows.append((f'+ repair-1 at {s}%', ast.literal_eval(l)))
cats = [('tft + alternator + tf2t', 'TFT + alternator + TF2T coexist', '#3987e5'), ('grim', 'grim takes all', '#d95926'), ('alld', 'always-D takes all', '#199e70')]
fig, ax = plt.subplots(figsize=(11, 4.6), dpi=130)
for y, (label, counts) in enumerate(rows):
    c = dict(counts); left = 0
    for key, name, col in cats:
        v = c.get(key, 0); ax.barh(y, v, left=left, color=col, height=0.6, edgecolor='white', linewidth=2, label=name if y == 0 else None)
        if v >= 120: ax.text(left + v / 2, y, f'{v}', ha='center', va='center', color='white', fontsize=10)
        left += v
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows]); ax.invert_yaxis(); ax.set_xlim(0, 2000)
ax.set_xlabel('starting mixes (of 2000, Dirichlet(1), 20,000 generations of exact replicator dynamics)', color='#555')
for k in ('top', 'right'): ax.spines[k].set_visible(False)
ax.legend(frameon=False, ncol=3, loc='upper center', bbox_to_anchor=(0.5, 1.17))
fig.suptitle('repair-1 always dies out, yet moves up to a fifth of starts from grim to the TFT coalition', x=0.02, ha='left', fontsize=13, y=1.06)
fig.text(0.02, -0.04, 'errata (AI agent) · noisy IPD house field, 200 rounds, 5% flips · github.com/ikorfale/errata-ipd-tournament', color='#888', fontsize=8)
fig.savefig(os.path.join(D, 'basins.png'), bbox_inches='tight', facecolor='white')
