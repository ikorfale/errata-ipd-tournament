import json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
d = json.load(open('gtft_sweep.json'))
cols = {'0.0': '#86b6ef', '0.01': '#3987e5', '0.05': '#1c5cab', '0.1': '#104281'}
panels = [('self', 'Among forgivers (self-play)'), ('house_mean', 'Against the house field (9 strategies)'),
          ('alld_invades', 'Does a defector invade? (ALLD gain over natives)')]
fig, axs = plt.subplots(1, 3, figsize=(14, 4.6))
for ax, (k, title) in zip(axs, panels):
    for e, rows in d['noise'].items():
        g = [r['g'] for r in rows]; y = [r[k] for r in rows]
        ax.plot(g, y, color=cols[e], lw=2, label=f'noise {float(e):.0%}')
        if k == 'house_mean':
            b = max(rows, key=lambda r: r[k]); ax.plot(b['g'], b[k], 'o', ms=8, color=cols[e], mec='white', mew=2)
    ax.axvline(1/3, color='#888', lw=1, ls='--')
    ax.text(1/3 + .02, ax.get_ylim()[0] + .03 * (ax.get_ylim()[1] - ax.get_ylim()[0]), 'g = 1/3', color='#555', fontsize=9)
    if k == 'alld_invades': ax.axhline(0, color='#333', lw=1)
    ax.set_title(title, fontsize=11, loc='left'); ax.set_xlabel('forgiveness g (chance to cooperate after a defection)')
    ax.grid(color='#eee'); [ax.spines[s].set_visible(False) for s in ('top', 'right')]
axs[0].set_ylabel('mean payoff per round')
axs[2].set_ylabel('ALLD payoff minus native payoff')
axs[0].legend(frameon=False, fontsize=9)
fig.suptitle('Generous tit-for-tat: how much forgiveness pays (exact 200-round expectations, T5 R3 P1 S0)', fontsize=12, x=.01, ha='left')
fig.tight_layout(); fig.savefig('gtft_forgiveness.png', dpi=110)
