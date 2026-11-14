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
            ("interpreter not pinned", "criterion: mean\n", "ok")]
fail = 0
for name, text, want in cases:
    got, msg = verdict(text); fail += got != want
    print(f"{'PASS' if got == want else 'FAIL'}  {name}: {got}  {msg[:110]}")
for name, text, want in py_cases:
    got, msg = verdict_py(text); fail += got != want
    print(f"{'PASS' if got == want else 'FAIL'}  {name}: {got}  {msg[:110]}")
sys.exit(1 if fail else 0)
