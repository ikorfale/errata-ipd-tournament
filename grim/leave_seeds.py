"""Follow-up, NOT pre-registered (decided after seeing leave_sim.out, where winners changed from seed to seed):
the same world and grid with 20 seeds per condition (seeds 101-120), summarised. Writes leave_seeds.out."""
import numpy as np
from leave_sim import run, NAMES
G, D = NAMES.index('grim'), [NAMES.index(n) for n in ('alld', 'stft', 'alternator')]
with open('leave_seeds.out', 'w') as f:
    for noise in (0.01, 0.05):
        for rule in ('never', 'after2', 'after1'):
            R = [run(noise, rule, s) for s in range(101, 121)]
            last = np.array([sh[-1] for sh, _ in R]); pay = np.array([p for _, p in R])
            top = np.bincount(last.argmax(1), minlength=len(NAMES))
            line = (f'noise {noise} {rule:6s}: payoff/tick {pay.mean():.2f} (sd {pay.std():.2f}); grim share mean {last[:, G].mean():.3f}, '
                    f'top in {top[G]}/20; defectors combined mean {last[:, D].sum(1).mean():.3f}; mean shares: '
                    + ', '.join(f'{n} {x:.2f}' for n, x in zip(NAMES, last.mean(0))) + '; top counts: '
                    + ', '.join(f'{n} {c}' for n, c in zip(NAMES, top) if c))
            print(line, file=f, flush=True)
