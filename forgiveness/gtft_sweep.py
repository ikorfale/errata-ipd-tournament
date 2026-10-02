"""How much forgiveness pays under noise? Exact 200-round expectations, generous TFT(g) vs the house field.
Strategies are finite-state machines with a probability of *intending* C in each state; each played move
is then flipped with probability `noise`. GTFT(g): cooperate after the opponent's C; after a D, cooperate with prob g."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from ml_bench import BASE, repair

def det(s):  # deterministic BASE machine -> stochastic form
    start, states = s
    return (start, [(1.0 - m, c, d) for m, c, d in states])

def gtft(g):
    return (0, [(1.0, 0, 1), (g, 0, 1)])

PAY = np.array([[3., 0.], [5., 1.]])  # row: my move (0=C,1=D), col: theirs

def expect(a, b, noise=0.05, rounds=200):
    sa, aa = a; sb, bb = b
    na, nb = len(aa), len(bb)
    T = np.zeros((na * nb, na * nb)); R = np.zeros(na * nb); CC = np.zeros(na * nb)
    for i, (pa, ca, da) in enumerate(aa):
        qa = pa * (1 - noise) + (1 - pa) * noise  # prob played move is C
        for j, (pb, cb, db) in enumerate(bb):
            qb = pb * (1 - noise) + (1 - pb) * noise
            row = i * nb + j
            for va, wa in [(0, qa), (1, 1 - qa)]:
                for vb, wb in [(0, qb), (1, 1 - qb)]:
                    w = wa * wb
                    T[row, (ca if vb == 0 else da) * nb + (cb if va == 0 else db)] += w
                    R[row] += w * PAY[va, vb]; CC[row] += w * (va == vb == 0)
    assert np.allclose(T.sum(1), 1)
    x = np.zeros(na * nb); x[sa * nb + sb] = 1
    s = c = 0.
    for _ in range(rounds):
        s += x @ R; c += x @ CC; x = x @ T
    return s / rounds, c / rounds

HOUSE = {n: det(s) for n, s in BASE.items()}
HOUSE['repair-1'] = det(repair(1))

def main():
    # checks: g=0 is TFT, g=1 is ALLC, against the existing deterministic bench
    from ml_bench import expectation
    for e in [0, .05]:
        for n, s in BASE.items():
            assert np.isclose(expect(gtft(0), HOUSE[n], e)[0], expectation(BASE['tft'], s, e)[0])
            assert np.isclose(expect(gtft(1), HOUSE[n], e)[0], expectation(BASE['allc'], s, e)[0])
    gs = np.round(np.linspace(0, 1, 41), 3)
    out = {'method': 'exact Markov expectation, 200 rounds, payoffs T5 R3 P1 S0, independent move flips', 'g': gs.tolist(), 'noise': {}}
    for e in [0.0, 0.01, 0.05, 0.10]:
        rows = []
        for g in gs:
            G = gtft(g)
            self_s, self_cc = expect(G, G, e)
            alld_gets = expect(HOUSE['alld'], G, e)[0]
            vs_alld = expect(G, HOUSE['alld'], e)[0]
            house = float(np.mean([expect(G, t, e)[0] for t in HOUSE.values()]))
            rows.append(dict(g=float(g), self=self_s, self_cc=self_cc, alld_vs_it=alld_gets, it_vs_alld=vs_alld,
                             house_mean=house, alld_invades=alld_gets - self_s))
        out['noise'][str(e)] = rows
        bh = max(rows, key=lambda r: r['house_mean'])
        safe = [r['g'] for r in rows if r['alld_invades'] < 0]
        print(f"noise {e}: best g in house field {bh['g']} ({bh['house_mean']:.4f}; tft {rows[0]['house_mean']:.4f});"
              f" self-play g=0 {rows[0]['self']:.3f} g=1/3~{rows[13]['self']:.3f} (g={rows[13]['g']});"
              f" ALLD cannot invade for g <= {max(safe) if safe else None}")
    Path(__file__).with_name('gtft_sweep.json').write_text(json.dumps(out, indent=1))

if __name__ == '__main__':
    main()
