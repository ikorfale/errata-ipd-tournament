"""A tag can be moved after the fact; a commit id cannot (fieldnotes-ai, 25 Nov 2026). ranks.txt names the tag
pinned-run-34089373 and an inputs_sha256, but cannot name the commit it lives in. This later commit can: the tag
pointed at TAG_COMMIT when it was pushed, and CI fails if it ever resolves elsewhere, or if the two input files in
the tagged tree no longer hash to the inputs_sha256 printed in the committed table."""
import hashlib, os, re, subprocess
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(H, "..")
TAG = "pinned-run-34089373"
TAG_COMMIT = "09407d3ac0cefcab0936ada28b525be8c4d51ee0"   # what the tag resolved to on 24 Nov 2026

def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True).stdout

def test_tag_still_points_at_the_commit_that_generated_the_table():
    assert git("rev-parse", TAG + "^{commit}").decode().strip() == TAG_COMMIT, f"{TAG} was moved"
    tagged = git("show", f"{TAG_COMMIT}:tests/pinned_run/DECLARED.txt") + \
             git("show", f"{TAG_COMMIT}:tests/pinned_run/run.json")
    printed = re.search(r"^# inputs_sha256: (\w{64})", open(os.path.join(H, "pinned_run", "ranks.txt")).read(), re.M)
    assert hashlib.sha256(tagged).hexdigest() == printed.group(1), "tagged inputs do not hash to the header"
