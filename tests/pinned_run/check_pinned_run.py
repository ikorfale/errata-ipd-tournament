"""A declaration that carries both pins: tests/pinned_run/DECLARED.txt, written with --pin on CPython 3.14.4,
pushed to GitHub before its drand round; run.json is the run that round seeded, committed after it.
Replays it on whatever interpreter runs this script: the interpreter and RNG checks come first, and only an
interpreter that matches both pins reaches the replay. python3 tests/pinned_run/check_pinned_run.py"""
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "erratum"))
import table_guard as g
D, RUN = os.path.join(H, "DECLARED.txt"), os.path.join(H, "run.json")
t = open(D).read(); n = int(re.search(r"^beacon_round:\s*(\d+)", t, re.M).group(1))
print("pinned:          ", re.search(r"^python:\s*(.+?)\s*$", t, re.M).group(1),
      "| rng", re.search(r"^rng_sha256:\s*(\w+)", t, re.M).group(1)[:12])
print("this interpreter:", g.interpreter(), "| rng", g.rng_fingerprint()[:12])
try:
    r = g.check_interpreter(t) + g.check_rng(t) + g.one_run(n, D, RUN)
    print("result: pass" + r)
    print("pass:", g.PASS_KIND)
except SystemExit as e:
    print(f"result: exit {e.code}")
