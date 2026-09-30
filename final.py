#!/usr/bin/env python3
"""final.py <field.txt> <salt file> — the official result as the rules in the thread fix it (#62158):
seeds from sha256(field bytes + salt), three tables, places, overall = sum of places.
Table 1: round-robin mean. Table 2: final share with no floor, literal (the dust is a real ordering).
Table 3: final share with floor 1e-4; equal values share the mean of their places.
Equal overall rank sums share a place. ipd.py's own __main__ runs without the salt: do not use it for the result."""
import hashlib, sys
from ipd import official

path, salt = sys.argv[1], open(sys.argv[2]).read().strip()
names, rr, ev, base = official(path, salt=salt)
n = len(names)

def places(vals):
    """1 = best; equal values share the mean of their places."""
    order = sorted(range(n), key=lambda i: -vals[i]); pl = [0.0] * n; k = 0
    while k < n:
        m = k
        while m + 1 < n and vals[order[m + 1]] == vals[order[k]]: m += 1
        for t in range(k, m + 1): pl[order[t]] = (k + m) / 2 + 1
        k = m + 1
    return pl

t1 = places([x[0] for x in rr]); t2 = places([x[0] for x in ev[0.0]]); t3 = places([x[0] for x in ev[1e-4]])
tot = [t1[i] + t2[i] + t3[i] for i in range(n)]; ov = places([-x for x in tot])
print('field sha256 %s; salt sha256 %s' % (hashlib.sha256(open(path, 'rb').read()).hexdigest(),
                                           hashlib.sha256(salt.encode()).hexdigest()))
print('entries %d; seeds = %x + 0..19; noise 0.05, 200 rounds, 100 reps per pair' % (n, base))
print('%-5s %-48s %8s %6s %5s %-12s %5s %-12s %5s %5s' % ('place', 'name', 'rr', 'rr_sd', 'p1', 'share_f0', 'p2', 'share_f1e-4', 'p3', 'sum'))
for i in sorted(range(n), key=lambda i: (ov[i], names[i])):
    print('%-5g %-48s %8.4f %6.4f %5g %-12.4g %5g %-12.4g %5g %5g' % (
        ov[i], names[i], rr[i][0], rr[i][1], t1[i], ev[0.0][i][0], t2[i], ev[1e-4][i][0], t3[i], tot[i]))
