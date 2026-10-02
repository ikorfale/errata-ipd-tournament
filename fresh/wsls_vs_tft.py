"""huddora's question (#68432): does WSLS (pavlov) separate from TFT under 5% noise? Exact per-pair payoffs
in the official 13-entry field: pavlov minus tft against each opponent."""
import sys; sys.path.insert(0, ".")
import ipd, exact_ipd as E
F = ipd.load('field/final.txt'); by = {s['name']: s for s in F}
rows = []
for s in F:
    p = E.exact(by['pavlov'], s)[0]; t = E.exact(by['tft'], s)[0]
    rows.append((p - t, s['name'], p, t))
for d, n, p, t in sorted(rows):
    print(f'{n:48s} pavlov {p:.3f}  tft {t:.3f}  diff {d:+.3f}')
print('mean diff over field', round(sum(r[0] for r in rows) / len(rows), 3))
