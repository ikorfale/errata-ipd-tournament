#!/usr/bin/env python3
"""Alternative place tables for the IPD final (erratum 29.10, after alex-730): (a) every column from the
exact Markov matrix; (b) sampled, but each evolution column summarised by its median over the 20 seeds."""
import json, statistics as st
d = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'dump.json'))); N = d['names']; n = len(N)
def places(vals):
    order = sorted(range(n), key=lambda i: -vals[i]); pl = [0.0] * n; k = 0
    while k < n:
        m = k
        while m + 1 < n and vals[order[m + 1]] == vals[order[k]]: m += 1
        for t in range(k, m + 1): pl[order[t]] = (k + m) / 2 + 1
        k = m + 1
    return pl
def table(title, rr, e0, e4):
    t1, t2, t3 = places(rr), places(e0), places(e4); tot = [a + b + c for a, b, c in zip(t1, t2, t3)]
    ov = places([-x for x in tot]); print(title)
    print('%-5s %-48s %5s %5s %5s %6s' % ('place', 'name', 'p_rr', 'p_e0', 'p_e4', 'sum'))
    for i in sorted(range(n), key=lambda i: (ov[i], N[i])): print('%-5g %-48s %5g %5g %5g %6g' % (ov[i], N[i], t1[i], t2[i], t3[i], tot[i]))
    print()
E = d['exact']; rrE = [sum(r) / n for r in E]
table('(a) exact matrix: rr, final share floor 0, floor 1e-4 (generation 1000)', rrE, d['exact_traj0']['1000'], d['exact_traj0.0001']['1000'])
S = d['seeds']; rr = [st.mean(s['rr'][j] for s in S) for j in range(n)]
table('(b) sampled, evolution columns as median over 20 seeds', rr, [st.median(s['f0'][j] for s in S) for j in range(n)],
      [st.median(s['f0.0001'][j] for s in S) for j in range(n)])
table('(c) official rule reproduced: sampled, means over 20 seeds', rr, [st.mean(s['f0'][j] for s in S) for j in range(n)],
      [st.mean(s['f0.0001'][j] for s in S) for j in range(n)])
