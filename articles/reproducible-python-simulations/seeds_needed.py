"""How many seeds does the pinned IPD run need before its ranking stops moving?
For k = 1..20, draw 2000 random subsets of k of the 20 seeds, rank entries by mean rr score,
and count how often the full 20-seed order (all 13 places) and the top 3 come out the same."""
import json, random, sys
import numpy as np
run = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "run.json"))
names = run["names"]; X = np.array([s["rr"] for s in run["seeds"]])   # seeds x entries
full = list(np.argsort(-X.mean(0)))
rng = random.Random(20261128); out = []
for k in range(1, X.shape[0] + 1):
    same_all = same_top3 = 0; T = 2000
    for _ in range(T):
        idx = rng.sample(range(X.shape[0]), k); o = list(np.argsort(-X[idx].mean(0)))
        same_all += o == full; same_top3 += o[:3] == full[:3]
    out.append({"k": k, "same_order": same_all / T, "same_top3": same_top3 / T})
m = X.mean(0); sd = X.std(0, ddof=1); gaps = -np.diff(np.sort(m)[::-1])
print("entries", len(names), "seeds", X.shape[0])
print("smallest gap between neighbours", round(float(gaps.min()), 5), "between ranks", int(gaps.argmin()) + 1, "and", int(gaps.argmin()) + 2)
print("median per-seed sd", round(float(np.median(sd)), 5))
for r in out: print(r)
json.dump({"rows": out, "min_gap": float(gaps.min()), "median_sd": float(np.median(sd))}, open("seeds_needed.json", "w"), indent=1)
