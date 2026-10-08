#!/usr/bin/env python3
"""How people played errata.page/play: first move, defection in the middle vs the last five rounds,
and cooperation right after the house's (actual, post-noise) defection. Reads the anonymous game files here."""
import glob, json
EXCLUDED = {'fb7828b448cf9b66'}   # my own replay overwrote the agent's game, see EXCLUDED.md
for via in ('api', 'browser'):
    gs = [json.load(open(f)) for f in sorted(glob.glob(f'games_{via}_*'))]
    gs = [g for g in gs if g.get('game') not in EXCLUDED and g.get('arm', 'shown') == 'shown']   # known-length games only (hidden arm: see ../endgame)
    mid = end = forg = fn = first = 0
    for g in gs:
        I, T = g['intended'], g['theirs']
        assert len(I) == len(T) == 50
        first += I[0] == 'C'
        mid += I[5:45].count('D'); end += I[45:].count('D')
        for i in range(49):
            if T[i] == 'D':
                fn += 1; forg += I[i + 1] == 'C'
    n = len(gs)
    print(f"{via}: {n} games, days {sorted({g['day'] for g in gs})}")
    print(f"  opened with C: {first}/{n}")
    print(f"  intended D, rounds 6-45: {mid}/{40*n} = {mid/(40*n):.2f}; last 5 rounds: {end}/{5*n} = {end/(5*n):.2f}")
    print(f"  C right after a house D: {forg}/{fn} = {forg/fn:.2f}")
    print(f"  player ahead of the house: {sum(g['score']['you'] > g['score']['them'] for g in gs)}/{n}, "
          f"mean per round {sum(g['score']['you'] for g in gs)/(50*n):.2f}")
