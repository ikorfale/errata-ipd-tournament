"""Same seed, same code, 40 fresh processes: does random.choice over a set of strings give one answer?
Without PYTHONHASHSEED each process hashes strings differently, so set order (and the pick) changes."""
import collections, json, os, subprocess, sys
code = "import random; r=random.Random(42); s={'tft','grim','pavlov','allc','alld','tf2t','stft','alternator'}; print(r.choice(list(s)), r.choice(sorted(s)))"
res = {}
for label, env in (("hash seed not set", {k: v for k, v in os.environ.items() if k != "PYTHONHASHSEED"}),
                   ("PYTHONHASHSEED=0", {**os.environ, "PYTHONHASHSEED": "0"})):
    outs = [subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True).stdout.split() for _ in range(40)]
    res[label] = {"choice(list(set))": dict(collections.Counter(o[0] for o in outs)),
                  "choice(sorted(set))": dict(collections.Counter(o[1] for o in outs))}
print(json.dumps(res, indent=1))
json.dump(res, open("hashseed.json", "w"), indent=1)
