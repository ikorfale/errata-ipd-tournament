"""Own exact expectation bench; no tournament entry and no downloaded code execution."""
import json
from pathlib import Path
import numpy as np

# Each tuple is (intended move: C=0/D=1, next after C, next after D).
BASE = {
    'allc': (0, [(0, 0, 0)]),
    'alld': (0, [(1, 0, 0)]),
    'tft': (0, [(0, 0, 1), (1, 0, 1)]),
    'stft': (1, [(0, 0, 1), (1, 0, 1)]),
    'grim': (0, [(0, 0, 1), (1, 1, 1)]),
    'pavlov': (0, [(0, 0, 1), (1, 1, 0)]),
    'tf2t': (0, [(0, 0, 1), (0, 0, 2), (1, 0, 2)]),
    'alternator': (0, [(0, 1, 1), (1, 0, 0)]),
}

def repair(punishments):
    # Ignore one D, punish after two; after a bounded D spell try C once.
    assert 1 <= punishments <= 5
    states = [(0, 0, 1), (0, 0, 2)]
    states += [(1, 0, k + 1) for k in range(2, 2 + punishments)]
    states += [(0, 0, 2)]
    return (0, states)

def expectation(a, b, noise=0.05, rounds=200):
    sa, aa = a; sb, bb = b
    na, nb = len(aa), len(bb)
    transition = np.zeros((na * nb, na * nb))
    reward = np.zeros(na * nb)
    cooperation = np.zeros(na * nb)
    pay = np.array([[3., 0.], [5., 1.]])
    for i, (ma, ca, da) in enumerate(aa):
        for j, (mb, cb, db) in enumerate(bb):
            row = i * nb + j
            for fa, pa in [(0, 1 - noise), (1, noise)]:
                for fb, pb in [(0, 1 - noise), (1, noise)]:
                    va, vb = ma ^ fa, mb ^ fb
                    probability = pa * pb
                    target_a = ca if vb == 0 else da
                    target_b = cb if va == 0 else db
                    transition[row, target_a * nb + target_b] += probability
                    reward[row] += probability * pay[va, vb]
                    cooperation[row] += probability * (va == vb == 0)
    assert np.allclose(transition.sum(axis=1), 1)
    distribution = np.zeros(na * nb); distribution[sa * nb + sb] = 1
    score = cc = 0.
    for _ in range(rounds):
        score += distribution @ reward
        cc += distribution @ cooperation
        distribution = distribution @ transition
    assert np.isclose(distribution.sum(), 1)
    return float(score / rounds), float(cc / rounds)

def main():
    # Closed-form boundaries catch move, payoff, and noise wiring errors.
    assert np.isclose(expectation(BASE['allc'], BASE['allc'], 0)[0], 3)
    assert np.isclose(expectation(BASE['alld'], BASE['allc'], 0)[0], 5)
    assert np.isclose(expectation(BASE['alld'], BASE['alld'], 0)[0], 1)
    assert np.isclose(expectation(BASE['allc'], BASE['allc'])[0], 2.9475)
    assert np.isclose(expectation(BASE['tft'], BASE['tft'], 0)[1], 1)
    # In the exact eight-strategy house field, compare the published rounded RR baseline.
    means = {n: float(np.mean([expectation(s, t)[0] for t in BASE.values()])) for n, s in BASE.items()}
    assert np.isclose(means['alternator'], 2.258, atol=.001)
    assert np.isclose(means['tft'], 2.198, atol=.001)
    cases = {}
    for name, strategy in [('tft', BASE['tft']), ('tf2t', BASE['tf2t'])] + [(f'repair-{n}', repair(n)) for n in range(1, 6)]:
        cases[name] = {
            'states': len(strategy[1]),
            'house_opponents_mean': float(np.mean([expectation(strategy, t)[0] for t in BASE.values()])),
            'self_score': expectation(strategy, strategy)[0],
            'self_CC_fraction': expectation(strategy, strategy)[1],
            'against_alld': expectation(strategy, BASE['alld'])[0],
            'noise_self_CC': {str(e): expectation(strategy, strategy, e)[1] for e in [0, .01, .05, .10, .20]},
        }
    data = {'method': 'Exact finite-horizon joint-state Markov expectation, float64; 200 rounds; independent flips 0.05; house opponents only. Own strategy does not enter the opponent field.', 'checks': 'All stated boundary and baseline checks passed.', 'house_RR': means, 'cases': cases}
    Path(__file__).with_name('forgiveness-bench.json').write_text(json.dumps(data, indent=2))
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()
