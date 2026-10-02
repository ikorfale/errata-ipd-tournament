import json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
inv = json.load(open('gtft_invaders.json')); sw = json.load(open('gtft_sweep.json'))
cols = {'0.0': '#86b6ef', '0.01': '#3987e5', '0.05': '#1c5cab'}
fig, ax = plt.subplots(figsize=(8, 4.6))
for e, rows in inv.items():
    ax.plot([r[0] for r in rows], [r[1] for r in rows], color=cols[e], lw=2, label=f'best less-generous mutant, noise {float(e):.0%}')
r5 = [r for r in sw['noise']['0.05'] if 0.2 <= r['g'] <= 0.5]
ax.plot([r['g'] for r in r5], [r['alld_invades'] for r in r5], color='#888', lw=2, ls=':', label='always-defect only, noise 5%')
ax.axhline(0, color='#333', lw=1); ax.axvline(1/3, color='#888', lw=1, ls='--')
ax.text(1/3 + .005, .12, 'g = 1/3\n(Nowak & Sigmund 1992)', fontsize=9, color='#555')
ax.set_ylim(-0.6, 0.18)
ax.set_xlabel('forgiveness g of the resident generous tit-for-tat'); ax.set_ylabel('invader payoff minus resident payoff')
ax.set_title('Above 1/3 the occasional cheat invades, long before always-defect can', loc='left', fontsize=11)
ax.grid(color='#eee'); [ax.spines[s].set_visible(False) for s in ('top', 'right')]
ax.legend(frameon=False, fontsize=9, loc='lower left')
fig.tight_layout(); fig.savefig('gtft_invaders.png', dpi=110)
