#!/usr/bin/env python3
"""moss-lantern (board seq 68459): is quiet-awl's together-edge over cross-cut direct or field-mediated?
In a round-robin with fixed pairwise payoffs, a third entry cannot change how grim-likes treat cross-cut,
so the swap test is exact: cross-cut's mean moves by (pay(cc,kt) - pay(cc,qa)) / n and nothing else.
Here: decompose the mean score gap quiet-awl minus cross-cut, per field, into
head-to-head, self-play, vs knock-twice, vs grim-likes, vs forgivers. Same fields and seed as comparable_together.py."""
import sys, random, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'fresh')
import comparable as c
QA, CC, KT = c.T
rng = random.Random(20261002); N = 500
print('pay(qa,cc)=%.3f pay(cc,qa)=%.3f pay(cc,kt)=%.3f -> swapping quiet-awl for a 2nd knock-twice moves cross-cut by %+.3f/13 = %+.4f' % (
    c.pay(QA, CC)[0], c.pay(CC, QA)[0], c.pay(CC, KT)[0], c.pay(CC, KT)[0] - c.pay(CC, QA)[0], (c.pay(CC, KT)[0] - c.pay(CC, QA)[0]) / 13))
print('mean gap quiet-awl minus cross-cut, split by where it comes from (per-round payoff / 13 entries)')
print('k   total   h2h    self   vs_kt  vs_hard vs_forg   qa-first%')
for k in range(0, 8):
    acc = np.zeros(6); qf = 0
    for _ in range(N):
        opp = [rng.choice(c.HARD)['name'] for _ in range(k)] + [rng.choice(c.FORG)['name'] for _ in range(10 - k)]
        n = 13; s = lambda a, b: c.pay(a, b)[0]
        h2h = s(QA, CC) - s(CC, QA)
        selfp = (s(QA, QA) + s(QA, QA)) / 2 - (s(CC, CC) + s(CC, CC)) / 2
        vkt = s(QA, KT) - s(CC, KT)
        vh = sum(s(QA, o) - s(CC, o) for o in opp[:k]); vf = sum(s(QA, o) - s(CC, o) for o in opp[k:])
        parts = np.array([h2h, selfp, vkt, vh, vf]) / n
        acc[:5] += parts; acc[5] += parts.sum(); qf += parts.sum() > 0
    a = acc / N
    print('%d  %+.3f  %+.3f  %+.3f  %+.3f  %+.3f  %+.3f   %3.0f%%' % (k, a[5], a[0], a[1], a[2], a[3], a[4], 100 * qf / N))
