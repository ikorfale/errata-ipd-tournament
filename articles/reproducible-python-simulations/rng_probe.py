"""Run under one interpreter; prints JSON: per random-module call, sha256 of 2000 draws from fixed seeds.
python3 rng_probe.py > probe-<version>.json"""
import hashlib, json, platform, random, sys
def dig(f):
    try:
        out = []
        for s in (0, 1, 2**40 + 7, 12345678901234567890):
            r = random.Random(s); out.append(repr(f(r)))
        return hashlib.sha256("\n".join(out).encode()).hexdigest()[:16]
    except Exception as e:
        return "error: " + type(e).__name__
N = 500
calls = {
    "random()": lambda r: [r.random() for _ in range(N)],
    "getrandbits(64)": lambda r: [r.getrandbits(64) for _ in range(N)],
    "randrange(10)": lambda r: [r.randrange(10) for _ in range(N)],
    "randint(1,6)": lambda r: [r.randint(1, 6) for _ in range(N)],
    "choice(list)": lambda r: [r.choice("abcdefghij") for _ in range(N)],
    "shuffle(32)": lambda r: [r.shuffle(x) or x for x in [list(range(32)) for _ in range(50)]],
    "sample(range(100),5)": lambda r: [r.sample(range(100), 5) for _ in range(100)],
    "choices(k=10)": lambda r: [r.choices("abc", weights=[1, 2, 3], k=10) for _ in range(50)],
    "uniform(0,1)": lambda r: [r.uniform(0, 1) for _ in range(N)],
    "gauss(0,1)": lambda r: [r.gauss(0, 1) for _ in range(N)],
    "normalvariate(0,1)": lambda r: [r.normalvariate(0, 1) for _ in range(N)],
    "expovariate(1)": lambda r: [r.expovariate(1) for _ in range(N)],
    "binomialvariate(20,.3)": lambda r: [r.binomialvariate(20, 0.3) for _ in range(N)],
    "seed('text')": lambda r: (r.seed("errata"), [r.random() for _ in range(20)])[1],
    "seed(b'bytes')": lambda r: (r.seed(b"errata"), [r.random() for _ in range(20)])[1],
    "seed(3.5)": lambda r: (r.seed(3.5), [r.random() for _ in range(20)])[1],
    "seed((1,2))": lambda r: (r.seed((1, 2)), [r.random() for _ in range(20)])[1],
}
print(json.dumps({"python": platform.python_version(), "calls": {k: dig(f) for k, f in calls.items()}}))
