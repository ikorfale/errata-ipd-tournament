"""Noisy IPD with the option to leave a partner. World and guesses: PREREG-leave.md (committed before this file ran).
Usage: python3 leave_sim.py [noise] [rule] [seed]  -> one run; with no arguments runs the pre-registered grid
and writes leave_sim.json."""
import sys, json, os
import numpy as np
sys.path.insert(0, '..')
import ipd

S = ipd.load('../house.txt' if os.path.exists('../house.txt') else '../field/house.txt')
NAMES = [s['name'] for s in S]; K = len(S)
NST = max(len(s['states']) for s in S)
MOVE = np.zeros((K, NST), dtype=np.int8); NEXT = np.zeros((K, NST, 2), dtype=np.int16); START = np.zeros(K, dtype=np.int16)
for k, s in enumerate(S):
    idx = {n: i for i, n in enumerate(s['states'])}
    START[k] = idx[s['start']]
    for n, (mv, t) in s['states'].items():
        MOVE[k, idx[n]] = mv == 'D'; NEXT[k, idx[n], 0] = idx[t['C']]; NEXT[k, idx[n], 1] = idx[t['D']]
PAY = np.array([[3, 0], [5, 1]])            # PAY[my move][their move], 0 = C, 1 = D
N, PER, TICKS, GENS, MUT, BREAK = 240, 30, 600, 60, 0.01, 1 / 200
LEAVE = {'never': 10**9, 'after2': 2, 'after1': 1}

def run(noise, rule, seed):
    rng = np.random.default_rng(seed); L = LEAVE[rule]
    strat = np.repeat(np.arange(K), PER)
    shares = [np.bincount(strat, minlength=K) / N]
    for g in range(GENS):
        partner = np.full(N, -1); state = START[strat].copy(); cd = np.zeros(N, dtype=np.int16)
        pay = np.zeros(N); waiting = np.ones(N, dtype=bool)          # everyone starts unpartnered: sits out tick 0
        for t in range(TICKS):
            p = partner >= 0; ip = np.nonzero(p)[0]
            if ip.size:
                m = MOVE[strat[ip], state[ip]].astype(np.int8)
                flip = rng.random(ip.size) < noise
                act = np.zeros(N, dtype=np.int8); act[ip] = m ^ flip
                other = act[partner[ip]]
                pay[ip] += PAY[act[ip], other]
                state[ip] = NEXT[strat[ip], state[ip], other]
                cd[ip] = np.where(other == 1, cd[ip] + 1, 0)
                leave = np.zeros(N, dtype=bool); leave[ip] = cd[ip] >= L
                lo = ip[ip < partner[ip]]                               # one draw per pair
                end = leave[lo] | leave[partner[lo]] | (rng.random(lo.size) < BREAK)
                a = lo[end]; b = partner[a]
                partner[a] = -1; partner[b] = -1
                justleft = np.zeros(N, dtype=bool); justleft[a] = True; justleft[b] = True
            else:
                justleft = np.zeros(N, dtype=bool)
            # those who sat out this tick get a new random partner; those who just left sit out the next tick
            pool = np.nonzero(waiting)[0]; rng.shuffle(pool)
            if pool.size % 2: pool = pool[:-1]
            a, b = pool[0::2], pool[1::2]
            partner[a] = b; partner[b] = a
            state[a] = START[strat[a]]; state[b] = START[strat[b]]; cd[a] = 0; cd[b] = 0
            waiting = (partner < 0) & ~np.isin(np.arange(N), pool) | justleft
            waiting &= partner < 0
            waiting |= (partner < 0)
        fit = pay / TICKS
        prob = fit / fit.sum() if fit.sum() > 0 else np.full(N, 1 / N)
        strat = rng.choice(strat, size=N, p=prob)
        mut = rng.random(N) < MUT; strat[mut] = rng.integers(0, K, mut.sum())
        shares.append(np.bincount(strat, minlength=K) / N)
    return np.array(shares), fit.mean()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        sh, f = run(float(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
        print(f'mean payoff per tick last gen {f:.2f}; gen {GENS}: ' + ', '.join(f'{n} {x:.2f}' for n, x in zip(NAMES, sh[-1])))
    else:
        out = {}
        for noise in (0.01, 0.05):
            for rule in ('never', 'after2', 'after1'):
                for seed in (1, 2, 3):
                    sh, f = run(noise, rule, seed)
                    out[f'{noise}/{rule}/{seed}'] = {'shares': sh.round(4).tolist(), 'payoff_last': round(float(f), 4)}
                    top = NAMES[int(sh[-1].argmax())]
                    print(f'noise {noise} {rule:6s} seed {seed}: payoff/tick {f:.2f}; top {top} {sh[-1].max():.2f}; '
                          + ', '.join(f'{n} {x:.2f}' for n, x in zip(NAMES, sh[-1]) if x >= 0.05), flush=True)
        json.dump({'names': NAMES, 'runs': out}, open('leave_sim.json', 'w'))
