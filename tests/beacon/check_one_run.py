"""One round, one run: table_guard.one_run against tests/beacon/run.json, the run seeded by
DECLARED.txt's drand round from the declaration's own code. python3 tests/beacon/check_one_run.py"""
import json, os, re, sys, tempfile, contextlib, io
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "erratum"))
import table_guard as g
D = os.path.join(H, "DECLARED.txt"); n = int(re.search(r"beacon_round:\s*(\d+)", open(D).read()).group(1))
RUN = os.path.join(H, "run.json")

def case(path):
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out): r = g.one_run(n, D, path)
        return "pass", r
    except SystemExit as e:
        return f"exit {e.code}", out.getvalue().strip()[:160]

print("honest run:        ", case(RUN))
d = json.load(open(RUN)); d["seeds"][7]["rr"][3] += 0.01   # a kept second draw differs somewhere
f = os.path.join(H, "..", "..", "erratum", "_tampered.json"); json.dump(d, open(f, "w"))
try: print("one number changed:", case(f))      # uncommitted file: first_commit is None -> diff vs HEAD
finally: os.remove(f)
print("runner edited a200529..7d0b4dd:", g.runner_changed("a200529", "7d0b4dd", os.path.join(H, "..", "..")))
