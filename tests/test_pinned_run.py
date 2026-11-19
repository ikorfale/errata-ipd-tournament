"""CI replays a declaration that pins interpreter and RNG stream (tests/pinned_run). The matrix runs 3.12, which
the declaration does not name, so the refusal is shown on GitHub's machine, not only on the one that wrote it.
Expected: any interpreter other than the pinned CPython 3.14.4 exits 4 before the replay starts; the pinned one
either replays every number or, if its random module draws differently, is refused by the RNG pin."""
import os, platform, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))

def test_pinned_declaration_refuses_other_interpreters():
    p = subprocess.run([sys.executable, os.path.join(H, "pinned_run", "check_pinned_run.py")],
                       capture_output=True, text=True, cwd=os.path.join(H, ".."))
    out = p.stdout; print(out, p.stderr)
    here = f"{platform.python_implementation()} {platform.python_version()}"
    if here != "CPython 3.14.4":
        assert "INTERPRETER DIFFERS" in out and "result: exit 4" in out, out
        assert "REPLAY" not in out and "identical" not in out, out   # refused before any replay
    else:
        assert ("result: pass" in out and "identical" in out) or \
               ("RNG STREAM DIFFERS" in out and "result: exit 4" in out), out
