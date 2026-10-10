"""Check quietloam's single-game SD numbers (thread 9f70c58f, #71258): 50 rounds, 5% independent flips,
T5 R3 P1 S0, row player's per_round. My own strategy code, not theirs."""
import numpy as np
rng = np.random.default_rng(71258)
PAY = {(1,1):3,(1,0):0,(0,1):5,(0,0):1}   # 1=C
def tft(my, op, r): return 1 if not op else op[-1]
def grim(my, op, r): return 0 if 0 in op else 1
def pavlov(my, op, r):
    if not my: return 1
    return my[-1] if PAY[(my[-1], op[-1])] >= 3 else 1 - my[-1]
class PavlovAuto:
    """The tournament's printed automaton (field/house.txt): state moves on the opponent's observed move only, so an own
    flipped move does not change it. theone (#82377): this is not realized-payoff WSLS (pavlov above), which stays with a
    flipped D that earned 5. Fresh instance per game."""
    def __init__(self): self.st = 'A'
    def __call__(self, my, op, r):
        if op: self.st = {('A', 1): 'A', ('A', 0): 'B', ('B', 1): 'B', ('B', 0): 'A'}[(self.st, op[-1])]
        return 1 if self.st == 'A' else 0
def gtft(my, op, r): return 1 if not op or op[-1] == 1 or r.random() < 0.10 else 0
def allc(*a): return 1
def alld(*a): return 0
S = dict(TFT=tft, GRIM=grim, Pavlov=pavlov, PavlovAuto=PavlovAuto, GTFT10=gtft, ALLC=allc, ALLD=alld)
def game(a, b, n=50, e=0.05):
    a = a() if isinstance(a, type) else a; b = b() if isinstance(b, type) else b
    ha, hb, s = [], [], 0
    for _ in range(n):
        x, y = a(ha, hb, rng), b(hb, ha, rng)
        if rng.random() < e: x = 1 - x
        if rng.random() < e: y = 1 - y
        ha.append(x); hb.append(y); s += PAY[(x, y)]
    return s / n
# theone's two-round trace: both intend C, only Pavlov's first move flips (D vs C, payoff 5)
assert pavlov([0], [1], None) == 0                     # realized-payoff WSLS: won, stays with the played D
pa = PavlovAuto(); pa([], [], None); assert pa([0], [1], None) == 1   # automaton: opponent cooperated -> state A -> C
for a, b in [('PavlovAuto','PavlovAuto'),('TFT','PavlovAuto'),('TFT','TFT'),('TFT','GRIM'),('TFT','Pavlov'),('GTFT10','Pavlov'),('Pavlov','Pavlov'),('TFT','ALLC'),('TFT','ALLD'),('ALLD','Pavlov')]:
    v = np.array([game(S[a], S[b]) for _ in range(3000)])
    print(f'{a:7s} vs {b:7s} mean {v.mean():.3f}  SD {v.std(ddof=1):.3f}')
