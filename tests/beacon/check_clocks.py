"""External-clock checks of table_guard against the real pushed tests/beacon/DECLARED.txt.
Run after its drand round is published: python3 tests/beacon/check_clocks.py"""
import json, os, re, sys, tempfile, contextlib, io
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "erratum"))
import beacon, table_guard as g
D = os.path.join(H, "DECLARED.txt"); n = int(re.search(r"beacon_round:\s*(\d+)", open(D).read()).group(1))

def case(rnd, base):
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"beacon_round": rnd, "base": "%x" % base, "seeds": []}, f); f.close()
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out): r = g.external_clocks(rnd, D, f.name)
        return "pass", r
    except SystemExit as e:
        return f"exit {e.code}", out.getvalue().strip()

print("honest:       ", case(n, beacon.seed_base(n)))
print("wrong seeds:  ", case(n, beacon.seed_base(n) ^ 1))
print("round before push:", case(n - 200, beacon.seed_base(n - 200)))
