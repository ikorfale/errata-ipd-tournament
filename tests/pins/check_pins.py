"""Readable pins: a declaration's file_sha256/entry_sha256 lines must match its commit and cover everything.
Run from anywhere: python3 tests/pins/check_pins.py  (exit 0 = all four cases behave)."""
import os, subprocess, sys, contextlib, io
H = os.path.dirname(os.path.abspath(__file__)); TOP = os.path.abspath(os.path.join(H, "..", ".."))
sys.path.insert(0, os.path.join(TOP, "erratum")); import table_guard as g
files, entries = g.pins_at("HEAD", TOP)
good = "criterion: mean\n" + "".join(f"file_sha256: {k} {v}\n" for k, v in files.items()) \
       + "".join(f"entry_sha256: {k} {v}\n" for k, v in entries.items())
def verdict(text):
    try:
        with contextlib.redirect_stdout(io.StringIO()) as o: r = g.check_pins(text, "HEAD", TOP)
        return "ok", r
    except SystemExit as e: return f"exit {e.code}", o.getvalue().strip()
first = next(iter(entries)); h = entries[first]
cases = [("all pins, true", good, "ok"),
         ("one entry edited", good.replace(h, ("0" if h[0] != "0" else "1") + h[1:]), "exit 4"),
         ("one entry left out", "".join(l + "\n" for l in good.splitlines() if not l.startswith(f"entry_sha256: {first} ")), "exit 4"),
         ("no pins at all", "criterion: mean\n", "ok")]
def verdict_py(text):
    try:
        with contextlib.redirect_stdout(io.StringIO()) as o: r = g.check_interpreter(text)
        return "ok", r
    except SystemExit as e: return f"exit {e.code}", o.getvalue().strip()
py_cases = [("interpreter pinned, same", f"python: {g.interpreter()}\n", "ok"),
            ("interpreter pinned, other", "python: CPython 2.7\n", "exit 4"),
            ("interpreter pinned major.minor only", f"python: {g.interpreter(False)}\n", "ok"),
            ("interpreter pinned, other patch level, no rng pin", "python: " + g.interpreter().rsplit(".", 1)[0] + ".999\n", "exit 4"),
            ("interpreter pinned, other patch level, rng pin", "python: " + g.interpreter().rsplit(".", 1)[0] + ".999\n"
             + "rng_sha256: " + g.rng_fingerprint() + "\n", "ok"),
            ("interpreter pinned, other minor, rng pin", "python: CPython 3.1.4\n" + "rng_sha256: " + g.rng_fingerprint() + "\n", "exit 4"),
            ("interpreter not pinned", "criterion: mean\n", "ok")]
def verdict_rng(text):
    try:
        with contextlib.redirect_stdout(io.StringIO()) as o: r = g.check_rng(text)
        return "ok", r
    except SystemExit as e: return f"exit {e.code}", o.getvalue().strip()
fp = g.rng_fingerprint()
rng_cases = [("rng stream pinned, same", f"rng_sha256: {fp}\n", "ok"),
             ("rng stream pinned, other", "rng_sha256: " + ("0" if fp[0] != "0" else "1") + fp[1:] + "\n", "exit 4"),
             ("rng stream not pinned", "criterion: mean\n", "ok")]
import re as _re
calls = set(_re.findall(r"\brng\.(\w+)\(", open(os.path.join(TOP, "ipd.py")).read()))
extra = calls - g.REPLAY_RNG_CALLS
print(f"{'PASS' if not extra and calls else 'FAIL'}  replay RNG calls {sorted(calls)} all fingerprinted: {not extra}")
fail = 1 if extra or not calls else 0
for name, text, want in rng_cases:
    got, msg = verdict_rng(text); fail += got != want
    print(f"{'PASS' if got == want else 'FAIL'}  {name}: {got}  {msg[:110]}")
for name, text, want in cases:
    got, msg = verdict(text); fail += got != want
    print(f"{'PASS' if got == want else 'FAIL'}  {name}: {got}  {msg[:110]}")
for name, text, want in py_cases:
    got, msg = verdict_py(text); fail += got != want
    print(f"{'PASS' if got == want else 'FAIL'}  {name}: {got}  {msg[:110]}")
sys.exit(1 if fail else 0)
