"""How stable is the round-robin order across the 20 official seeds? Reads dump.json (written by
check.py): per-seed round-robin means, prints each entry's rank range over seeds and the seeds whose
full order equals the official (mean) order. Asked by a correspondent on 9 Nov 2026."""
import json, statistics as st
d = json.load(open('dump.json')); names = d['names']; n = len(names)
rr = [s['rr'] for s in d['seeds']]
ranks = []
for v in rr:
    order = sorted(range(n), key=lambda i: -v[i]); r = [0] * n
    for p, i in enumerate(order): r[i] = p + 1
    ranks.append(r)
mean = [st.mean(v[i] for v in rr) for i in range(n)]
official = sorted(range(n), key=lambda i: -mean[i])
print('%-46s %7s %6s  %-6s %s' % ('name', 'mean_rr', 'sd', 'ranks', 'seeds at official place'))
for i in official:
    rs = [r[i] for r in ranks]; off = official.index(i) + 1
    print('%-46s %.4f %.4f  %d..%d  %d/%d' % (names[i], mean[i], st.stdev(v[i] for v in rr), min(rs), max(rs), sum(x == off for x in rs), len(rr)))
same = sum(1 for r in ranks if sorted(range(n), key=lambda i: r[i]) == official)
print('seeds whose full round-robin order equals the official mean order: %d / %d' % (same, len(rr)))
for a, b in zip(official, official[1:]):
    fl = sum(1 for v in rr if v[b] > v[a])
    if fl: print('  %s < %s in %d/%d seeds' % (names[a], names[b], fl, len(rr)))
