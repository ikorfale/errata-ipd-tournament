#!/usr/bin/env python3
"""Per-seed spread of the co-evolution result (added 29.10 after the IPD-final erratum: a mean over seeds of an
absorbing outcome needs its spread). Final after1 - after2 share per seed, bootstrap 95% CI over seeds (10000 draws)."""
import json, random, statistics as st
d = json.load(open('leave_coevo.json')); rnd = random.Random(20261029)
for nz, run in d['runs'].items():
    fin = [h[-1] for h in run['history']]  # type index = strategy*3 + rule (never, after2, after1)
    diff = [sum(f[s * 3 + 2] - f[s * 3 + 1] for s in range(8)) for f in fin]
    boot = sorted(st.mean(rnd.choices(diff, k=len(diff))) for _ in range(10000))
    print('noise %s: after1 - after2, final share: mean %+.3f, median %+.3f, sd %.3f, after1 ahead in %d/20, '
          'bootstrap 95%% CI [%+.3f, %+.3f]' % (nz, st.mean(diff), st.median(diff), st.stdev(diff),
          sum(x > 0 for x in diff), boot[250], boot[9749]))
