"""Which g resist invasion by ANY less cooperative reactive mutant (p' <= 1, q' <= g)? Grid of mutants; exact 200-round expectations."""
import json, numpy as np
from gtft_sweep import expect
def react(p, q): return (0, [(p, 0, 1), (q, 0, 1)])
grid = np.round(np.linspace(0, 1, 21), 3)
res = {}
for e in [0.0, 0.01, 0.05]:
    rows = []
    for g in np.round(np.arange(0.2, 0.52, 0.02), 3):
        G = react(1, g); base = expect(G, G, e)[0]
        best = max(((expect(react(p, q), G, e)[0] - base, p, q) for p in grid for q in grid if q <= g + 1e-9 and (p, q) != (1, g)))
        rows.append((float(g), best[0], float(best[1]), float(best[2])))
    res[str(e)] = rows
    stable = [r[0] for r in rows if r[1] <= 1e-9]
    print(f"noise {e}: largest stable g on grid = {max(stable) if stable else None}")
    for r in rows: print(f"   g={r[0]:.2f} best mutant gain {r[1]:+.4f} at p'={r[2]} q'={r[3]}")
json.dump(res, open('gtft_invaders.json', 'w'), indent=1)
