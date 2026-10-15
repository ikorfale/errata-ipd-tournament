"""Leave rule evolving with the strategy. World and guesses: PREREG-coevo.md (committed before this file ran).
Usage: python3 leave_coevo.py [noise seed] -> one run; with no arguments runs 20 seeds per noise, writes leave_coevo.out/json."""
import sys, json
import numpy as np
from leave_sim import K, NAMES, MOVE, NEXT, START, PAY, N, TICKS, GENS, MUT, BREAK
RULES = ['never', 'after2', 'after1']; LVAL = np.array([10**9, 2, 1])
T = K * len(RULES)                                   # type = strategy * 3 + rule

def run(noise, seed, fixed=None):
    """fixed=rule index: control, everyone carries that rule and mutation never changes it (should match leave_seeds.out)."""
    rng = np.random.default_rng(seed)
    typ = np.repeat(np.arange(T), N // T) if fixed is None else np.repeat(np.arange(K) * 3 + fixed, N // K)
    hist = [np.bincount(typ, minlength=T) / N]
    for g in range(GENS):
        strat, L = typ // 3, LVAL[typ % 3]
        partner = np.full(N, -1); state = START[strat].copy(); cd = np.zeros(N, dtype=np.int16)
        pay = np.zeros(N); waiting = np.ones(N, dtype=bool); splits = 0
        for t in range(TICKS):
            ip = np.nonzero(partner >= 0)[0]
            justleft = np.zeros(N, dtype=bool)
            if ip.size:
                act = np.zeros(N, dtype=np.int8)
                act[ip] = MOVE[strat[ip], state[ip]] ^ (rng.random(ip.size) < noise)
                other = act[partner[ip]]
                pay[ip] += PAY[act[ip], other]
                state[ip] = NEXT[strat[ip], state[ip], other]
                cd[ip] = np.where(other == 1, cd[ip] + 1, 0)
                leave = np.zeros(N, dtype=bool); leave[ip] = cd[ip] >= L[ip]
                lo = ip[ip < partner[ip]]
                end = leave[lo] | leave[partner[lo]] | (rng.random(lo.size) < BREAK)
                a = lo[end]; b = partner[a]; splits += int((leave[lo] | leave[partner[lo]]).sum())
                partner[a] = -1; partner[b] = -1; justleft[a] = True; justleft[b] = True
            pool = np.nonzero(waiting)[0]; rng.shuffle(pool)
            if pool.size % 2: pool = pool[:-1]
            a, b = pool[0::2], pool[1::2]
            partner[a] = b; partner[b] = a
            state[a] = START[strat[a]]; state[b] = START[strat[b]]; cd[a] = 0; cd[b] = 0
            waiting = partner < 0                    # same effective rule as leave_sim.py: everyone unpartnered waits
        fit = pay / TICKS
        typ = rng.choice(typ, size=N, p=fit / fit.sum())
        mut = np.nonzero(rng.random(N) < MUT)[0]
        for i in mut:
            s, r = divmod(int(typ[i]), 3)
            if fixed is not None or rng.random() < 0.5: s = int(rng.integers(K))
            else: r = int(rng.integers(3))
            typ[i] = s * 3 + r
        hist.append(np.bincount(typ, minlength=T) / N)
    return np.array(hist), fit.mean(), splits

if __name__ == '__main__':
    if len(sys.argv) > 1:
        h, f, sp = run(float(sys.argv[1]), int(sys.argv[2])); last = h[-1].reshape(K, 3)
        print(f'payoff {f:.2f}, splits by rule last gen {sp}; rules ' + ', '.join(f'{r} {x:.2f}' for r, x in zip(RULES, last.sum(0)))
              + '; ' + ', '.join(f'{n} {x:.2f}' for n, x in zip(NAMES, last.sum(1))))
        sys.exit()
    G, D = NAMES.index('grim'), [NAMES.index(n) for n in ('alld', 'stft', 'alternator')]
    out = {}
    with open('leave_coevo.out', 'w') as fo:
        for noise in (0.01, 0.05):
            R = [run(noise, s) for s in range(201, 221)]
            last = np.array([h[-1].reshape(K, 3) for h, _, _ in R])          # seeds x strat x rule
            rules, strats = last.sum(1), last.sum(2)
            pay = np.array([f for _, f, _ in R])
            top = np.bincount(rules.argmax(1), minlength=3)
            out[str(noise)] = {'history': [h.round(4).tolist() for h, _, _ in R], 'payoff_last': pay.round(4).tolist()}
            line = (f'noise {noise}: payoff/tick {pay.mean():.2f} (sd {pay.std():.2f}); rule shares ' + ', '.join(f'{r} {x:.3f}' for r, x in zip(RULES, rules.mean(0)))
                    + '; rule top counts ' + ', '.join(f'{r} {c}/20' for r, c in zip(RULES, top))
                    + f'; grim share mean {strats[:, G].mean():.3f}; defectors combined mean {strats[:, D].sum(1).mean():.3f}; '
                    + 'strategy shares ' + ', '.join(f'{n} {x:.2f}' for n, x in zip(NAMES, strats.mean(0)))
                    + '; grim by rule ' + ', '.join(f'{r} {x:.3f}' for r, x in zip(RULES, last[:, G].mean(0))))
            print(line, file=fo, flush=True); print(line, flush=True)
    json.dump({'names': NAMES, 'rules': RULES, 'runs': out}, open('leave_coevo.json', 'w'))
