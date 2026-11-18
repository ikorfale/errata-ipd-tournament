"""CI replays the declared run on GitHub's runner, not only on the machine that wrote it.
Expected: the honest run passes; one changed number, an edited runner and a mismatched
interpreter pin are all refused (exit 4)."""
import os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))

def run(path):
    p = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=os.path.join(H, ".."))
    print(p.stdout, p.stderr)
    return p.stdout

def test_one_run_replays_here():
    out = run(os.path.join(H, "one_run", "check_one_run.py"))
    lines = dict(l.split(":", 1) for l in out.splitlines() if ":" in l)
    assert "('pass'" in lines["honest run"], out
    # DECLARED.txt predates the pins: the pass must say it rests on no interpreter or rng pin
    assert "interpreter not pinned" in lines["honest run"] and "RNG stream not pinned" in lines["honest run"], out
    assert "exit 4" in lines["one number changed"] and "REPLAY MISMATCH" in out, out
    assert "exit 4" in out.splitlines()[-1], out

def test_interpreter_and_rng_pins():
    out = run(os.path.join(H, "pins", "check_pins.py"))
    assert "FAIL" not in out and out.count("PASS") >= 4, out
