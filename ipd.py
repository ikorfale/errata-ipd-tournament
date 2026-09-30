#!/usr/bin/env python3
"""Noisy iterated prisoner's dilemma tournament for finite-state strategies.

Strategy text (one block per strategy):
    name: pavlov
    start: A
    A: C ; C->A D->B
    B: D ; C->B D->A
A state plays its move, then moves on by the opponent's move as *observed* (after noise).
At most 8 states. No code is executed: strategies are data.
"""
import re, sys, json, random, itertools

PAY = {('C','C'):(3,3), ('C','D'):(0,5), ('D','C'):(5,0), ('D','D'):(1,1)}
MAXSTATES = 8

def parse(text):
    name, start, states = None, None, {}
    for raw in text.strip().splitlines():
        line = raw.split('#')[0].strip()
        if not line: continue
        if line.lower().startswith('name:'): name = line[5:].strip(); continue
        if line.lower().startswith('start:'): start = line[6:].strip(); continue
        m = re.fullmatch(r'(\w+)\s*:\s*([CD])\s*;\s*C\s*->\s*(\w+)\s+D\s*->\s*(\w+)', line)
        if not m: raise ValueError('bad line: %r' % raw)
        s, mv, nc, nd = m.groups()
        states[s] = (mv, {'C': nc, 'D': nd})
    if not name or start not in states: raise ValueError('need name: and a start: that is a state')
    if len(states) > MAXSTATES: raise ValueError('more than %d states' % MAXSTATES)
    for s, (_, t) in states.items():
        for v in t.values():
            if v not in states: raise ValueError('state %s points to missing %s' % (s, v))
    return {'name': name, 'start': start, 'states': states}

def match(a, b, rounds, noise, rng):
    sa, sb = a['start'], b['start']; pa = pb = 0
    for _ in range(rounds):
        ma, mb = a['states'][sa][0], b['states'][sb][0]
        if rng.random() < noise: ma = 'D' if ma == 'C' else 'C'
        if rng.random() < noise: mb = 'D' if mb == 'C' else 'C'
        x, y = PAY[(ma, mb)]; pa += x; pb += y
        sa = a['states'][sa][1][mb]; sb = b['states'][sb][1][ma]
    return pa / rounds, pb / rounds

def tournament(strats, rounds=200, noise=0.05, reps=50, seed=1):
    rng = random.Random(seed); n = len(strats)
    M = [[0.0]*n for _ in range(n)]  # M[i][j] = mean per-round score of i against j
    for i, j in itertools.combinations_with_replacement(range(n), 2):
        si = sj = 0.0
        for _ in range(reps):
            x, y = match(strats[i], strats[j], rounds, noise, rng); si += x; sj += y
        M[i][j] = si / reps
        M[j][i] = sj / reps if i != j else (si + sj) / (2 * reps)
    return M

def replicator(M, gens=1000, floor=0.0):
    """Discrete replicator dynamics from equal shares. A share that falls below
    `floor` is set to 0 (extinct) and the rest renormalised; floor=0 keeps everyone."""
    n = len(M); p = [1.0/n]*n; hist = [p[:]]
    for _ in range(gens):
        f = [sum(M[i][j]*p[j] for j in range(n)) for i in range(n)]
        avg = sum(f[i]*p[i] for i in range(n))
        p = [p[i]*f[i]/avg for i in range(n)]
        if floor:
            p = [x if x >= floor else 0.0 for x in p]; t = sum(p); p = [x/t for x in p]
        hist.append(p[:])
    return hist

def seed_of(path, salt=''):
    """The seed is fixed by the entries plus a salt committed before the deadline:
    sha256 of the file's bytes followed by the salt (ASCII hex, revealed with the results)."""
    import hashlib
    return int(hashlib.sha256(open(path, 'rb').read() + salt.encode()).hexdigest()[:16], 16)

def load(path):
    return [parse(b) for b in open(path).read().split('\n---\n') if b.strip()]

def official(path, noise=0.05, seeds=20, reps=100, salt=''):
    """The scoring the tournament uses: `seeds` independent tournaments whose seeds come
    from the entries file; each table reports mean and standard deviation across seeds."""
    import statistics as st
    S = load(path); base = seed_of(path, salt); names = [s['name'] for s in S]; n = len(S)
    rr = [[] for _ in S]; ev = {0.0: [[] for _ in S], 1e-4: [[] for _ in S]}
    for k in range(seeds):
        M = tournament(S, noise=noise, reps=reps, seed=base + k)
        for i in range(n): rr[i].append(sum(M[i]) / n)
        for fl in ev:
            h = replicator(M, floor=fl)
            for i in range(n): ev[fl][i].append(h[-1][i])
    ms = lambda xs: (st.mean(xs), st.stdev(xs) if len(xs) > 1 else 0.0)
    return names, [ms(x) for x in rr], {fl: [ms(x) for x in v] for fl, v in ev.items()}, base

if __name__ == '__main__':
    path = sys.argv[1]
    names, rr, ev, base = official(path)
    print('entries: %d; seeds sha256(file)[:16]+0..19 = %x+k; noise 0.05, 200 rounds, 100 reps per pair' % (len(names), base))
    print('round-robin, mean points per round over 20 seeds (sd):')
    for i in sorted(range(len(names)), key=lambda i: -rr[i][0]): print('  %-16s %.3f (%.3f)' % (names[i], *rr[i]))
    for fl, v in ev.items():
        print('evolution, mean final share after 1000 generations over 20 seeds (sd), extinction floor %g:' % fl)
        for i in sorted(range(len(names)), key=lambda i: -v[i][0]): print('  %-16s %.3f (%.3f)' % (names[i], *v[i]))
