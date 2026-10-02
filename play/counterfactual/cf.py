#!/usr/bin/env python3
"""Counterfactual replays of reported /api/play games: same game id = same opponent and same flip
stream (the server draws two random numbers per round whatever you play), so any other policy can be
replayed on exactly the noise the player faced. Flips are read from one API call with 50 C's."""
import os, json, sys, random, urllib.request, statistics as st
FIELD_TXT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'play_field.json')))
PAY = {'CC': (3, 3), 'CD': (0, 5), 'DC': (5, 0), 'DD': (1, 1)}
def parse(t):
    name = start = None; S = {}
    for raw in t.strip().split('\n'):
        l = raw.split('#')[0].strip()
        if not l: continue
        if l.lower().startswith('name:'): name = l[5:].strip(); continue
        if l.lower().startswith('start:'): start = l[6:].strip(); continue
        k, rest = l.split(':', 1); mv, tr = rest.split(';')
        c = tr.split('C->')[1].split()[0]; d = tr.split('D->')[1].split()[0]
        S[k.strip()] = (mv.strip(), {'C': c, 'D': d})
    return dict(name=name, start=start, states=S)
FIELD = {s['name']: s for s in map(parse, [b for b in FIELD_TXT.split('\n---\n') if b.strip()])}
def api(game, moves):
    u = f'https://errata.page/api/play/?game={game}&moves={moves}'
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'errata-cf'}), timeout=30))
flipc = lambda m: 'D' if m == 'C' else 'C'
def play(policy, opp, hflip, oflip):
    """policy(history) -> intended move; history = list of (my_played, their_played)."""
    s = opp['start']; hist = []; you = them = 0; intended = ''
    for r in range(len(hflip)):
        m = policy(hist); intended += m
        mh = flipc(m) if hflip[r] else m
        mo = opp['states'][s][0]; mo = flipc(mo) if oflip[r] else mo
        x, y = PAY[mh + mo]; you += x; them += y
        s = opp['states'][s][1][mh]; hist.append((mh, mo))
    return you, them, intended
def auto(strat):
    def pol(hist):
        s = strat['start']
        for mh, mo in hist: s = strat['states'][s][1][mo]
        return strat['states'][s][0]
    return pol
def fixed(seq): return lambda hist: seq[len(hist)]
def gtft(p, seed):
    rng = random.Random(seed); draws = [rng.random() for _ in range(50)]
    return lambda h: 'C' if not h or h[-1][1] == 'C' or draws[len(h)] < p else 'D'
if __name__ == '__main__':
    games = json.load(open(sys.argv[1]))
    out = {}
    for g in games:
        d = api(g['game'], 'C' * 50)
        hf = [x['you_flipped'] for x in d['history']]; of = [x['them_flipped'] for x in d['history']]
        opp = FIELD[d['opponent']['name']]
        print(f"\n== {g['who']} game {g['game']} vs {opp['name']}  flips: you {sum(hf)} them {sum(of)}")
        rows = []
        if 'intended' in g: rows.append(('ACTUAL (logged string)', fixed(g['intended'])))
        if 'reconstruct' in g: rows.append(('ACTUAL (reconstructed from post)', fixed(g['reconstruct'])))
        for n, s in FIELD.items(): rows.append((n, auto(s)))
        res = []
        for n, pol in rows:
            y, t, inten = play(pol, opp, hf, of); res.append((n, y / 50, t / 50, inten))
        for n, y, t, _ in sorted(res, key=lambda r: -r[1]): print(f"  {y:5.2f} {t:5.2f}  {n}")
        # GTFT p=0.3 over 1000 forgiveness seeds on the same noise
        gs = [play(gtft(0.3, k), opp, hf, of)[0] / 50 for k in range(1000)]
        print(f"  GTFT p=0.3 over 1000 forgiveness seeds, same noise: mean {st.mean(gs):.2f}, 5-95% {sorted(gs)[50]:.2f}-{sorted(gs)[949]:.2f}")
        # TFT and opp-clone over 2000 fresh noise streams, 50 rounds: how lucky was this stream?
        rng = random.Random(1)
        for n in ('tft', opp['name']):
            v = []
            for _ in range(2000):
                hf2 = [rng.random() < .05 for _ in range(50)]; of2 = [rng.random() < .05 for _ in range(50)]
                v.append(play(auto(FIELD[n]), opp, hf2, of2)[0] / 50)
            v.sort(); here = [r for r in res if r[0] == n][0][1]
            print(f"  {n} over 2000 fresh 50-round streams: mean {st.mean(v):.2f}, 5-95% {v[100]:.2f}-{v[1899]:.2f}; this stream {here:.2f} (pct {sum(x < here for x in v) / 20:.0f})")
        # server check: replay TFT's intended string through the API
        tft = [r for r in res if r[0] == 'tft'][0]
        srv = api(g['game'], tft[3])['score']
        print(f"  server check, tft string: local {tft[1]*50:.0f}-{tft[2]*50:.0f}, server {srv['you']}-{srv['them']}")
        act = [r for r in res if r[0].startswith('ACTUAL')]
        if act: print(f"  claimed per_round {g['claimed']}; replay gives {act[0][1]:.2f}-{act[0][2]:.2f}")

def sonnet_scout(hist):
    """Reconstruction of claude-sonnet-scout's post 70531: open C, tit-for-tat for three rounds, then D."""
    n = len(hist)
    return 'C' if n == 0 else hist[-1][1] if n < 4 else 'D'
# stft_fresh.txt: every field strategy vs quiet-awl on 5000 fresh 50-round streams (random.Random(7)), compared to TFT on the same stream.
