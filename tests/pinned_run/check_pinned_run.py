"""A declaration that carries both pins: tests/pinned_run/DECLARED.txt, written with --pin on CPython 3.14.4,
pushed to GitHub before its drand round; run.json is the run that round seeded, committed after it.
Replays it on whatever interpreter runs this script: the interpreter and RNG checks come first, and only an
interpreter that matches both pins reaches the replay. python3 tests/pinned_run/check_pinned_run.py
After a pass it prints the ranking table of the run with the pass kind in its header, and with --write stores
it as ranks.txt: the kind travels with the table, and CI compares its own table to the committed one byte for
byte, so a 'pass: strict' header can only be reproduced by a strict run (asked by fieldnotes-ai, 21 Nov 2026)."""
import contextlib, io, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "erratum"))
import table_guard as g
INPUTS_COMMIT = "8d3d9e1b29c09f4c02fb74a7f385a479c9da16de"   # run.json committed 19 Nov 2026 06:58Z (fieldnotes-ai, 26 Nov)
D, RUN, RANKS = os.path.join(H, "DECLARED.txt"), os.path.join(H, "run.json"), os.path.join(H, "ranks.txt")
t = open(D).read(); n = int(re.search(r"^beacon_round:\s*(\d+)", t, re.M).group(1))
print("pinned:          ", re.search(r"^python:\s*(.+?)\s*$", t, re.M).group(1),
      "| rng", re.search(r"^rng_sha256:\s*(\w+)", t, re.M).group(1)[:12])
print("this interpreter:", g.interpreter(), "| rng", g.rng_fingerprint()[:12])

def ranks_table():
    """The round-robin ranking of run.json (mean over seeds), headed by the declaration and the pass kind."""
    run = json.load(open(RUN))
    cols = [[s["rr"][i] for s in run["seeds"]] for i in range(len(run["names"]))]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        g.guard(run["names"], cols, "rr")
    inputs = __import__("hashlib").sha256(open(D, "rb").read() + open(RUN, "rb").read()).hexdigest()
    head = [f"# ranking of the run seeded by drand round {n} (tests/pinned_run/run.json, column rr)",
            "# source: https://github.com/ikorfale/errata-ipd-tournament, tag pinned-run-34089373",
            f"# inputs_commit: {INPUTS_COMMIT} = the first commit holding both input files byte for byte as hashed"
            " below; resolve it directly, no tag needed (a later table can name an earlier commit, never its own)",
            f"# inputs_sha256: {inputs} = sha256(DECLARED.txt bytes + run.json bytes) in tests/pinned_run/; any"
            " clone whose two files hash to this generated this table",
            f"# pass: {g.PASS_KIND}",
            "# declared: " + "; ".join(l.strip() for l in t.splitlines() if l.strip()),
            "# a 'pass: strict' line here was reproduced byte for byte by the interpreter named in it; any other kind"
            " of pass would print its own kind and fail the comparison in tests/test_pinned_run.py"]
    return "\n".join(head) + "\n" + buf.getvalue()

try:
    r = g.check_interpreter(t) + g.check_rng(t) + g.one_run(n, D, RUN)
    print("result: pass" + r)
    print("pass:", g.PASS_KIND)
    table = ranks_table()
    print(table, end="")
    if "--write" in sys.argv:
        open(RANKS, "w").write(table); print(f"written: {RANKS}")
except SystemExit as e:
    print(f"result: exit {e.code}")
