"""World check for leave_coevo.py: with the rule fixed for everyone it should reproduce leave_seeds.out (other seeds)."""
import numpy as np
from leave_coevo import run, RULES, K, NAMES
G = NAMES.index('grim')
with open('coevo_control.out', 'w') as f:
    for noise in (0.01, 0.05):
        for r in range(3):
            R = [run(noise, s, fixed=r) for s in range(301, 311)]
            last = np.array([h[-1].reshape(K, 3).sum(1) for h, _, _ in R]); pay = np.array([p for _, p, _ in R])
            line = f'noise {noise} fixed {RULES[r]:6s}: payoff/tick {pay.mean():.2f}; grim {last[:, G].mean():.3f}'
            print(line, file=f, flush=True); print(line, flush=True)
