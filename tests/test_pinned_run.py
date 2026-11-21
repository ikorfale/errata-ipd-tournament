"""CI replays a declaration that pins interpreter and RNG stream (tests/pinned_run). The matrix runs 3.12, which
the declaration does not name, so the refusal is shown on GitHub's machine, not only on the one that wrote it.
Expected: any interpreter outside CPython 3.14 exits 4 before the replay starts; a 3.14.x (any patch level, since
2026-11-19 the RNG pin decides within one minor version) either replays every number or is refused by the RNG pin."""
import os, platform, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))

def test_pinned_declaration_refuses_other_interpreters():
    p = subprocess.run([sys.executable, os.path.join(H, "pinned_run", "check_pinned_run.py")],
                       capture_output=True, text=True, cwd=os.path.join(H, ".."))
    out = p.stdout; print(out, p.stderr)
    here = f"{platform.python_implementation()} {platform.python_version()}"
    if not here.startswith("CPython 3.14."):
        assert "INTERPRETER DIFFERS" in out and "result: exit 4" in out, out
        assert "REPLAY" not in out and "identical" not in out, out   # refused before any replay
    else:
        assert ("result: pass" in out and "identical" in out) or \
               ("RNG STREAM DIFFERS" in out and "result: exit 4" in out), out
        if "result: pass" in out:
            # The committed table carries its pass kind in the header; this runner's own table must equal it
            # byte for byte, so 'pass: strict' in ranks.txt is reproduced only by a strict run (fieldnotes-ai, 21 Nov).
            mine = out[out.index("# ranking of the run"):]
            mine = mine[:mine.index("written:")] if "written:" in mine else mine
            committed = open(os.path.join(H, "pinned_run", "ranks.txt")).read()
            assert mine == committed, "ranks.txt differs from this runner's table:\n" + mine
