"""Two clocks I do not hold, for table_guard --declared.

1. drand quicknet (League of Entropy): round N is published at genesis + (N-1)*3 s and its
   randomness cannot be known earlier. A declaration names a future round (`beacon_round: N`);
   check.py --beacon N seeds the run from that round's randomness, so no seed can have run
   before the round existed, and the criterion cannot be ground against outcomes.
2. GitHub's repository activity API: the server's time of the first push whose head contains
   the declaration's commit. The declaration must be public before round N is published.
"""
import hashlib, json, subprocess, urllib.request

CHAIN = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"  # quicknet
GENESIS, PERIOD = 1692803367, 3

def round_time(n):
    return GENESIS + (n - 1) * PERIOD

def round_at(t):
    """First round published at or after unix time t."""
    return max(1, -(-(t - GENESIS) // PERIOD) + 1)

def randomness(n):
    with urllib.request.urlopen(f"https://api.drand.sh/{CHAIN}/public/{n}", timeout=20) as r:
        return json.load(r)["randomness"]

def seed_base(n):
    return int(hashlib.sha256(bytes.fromhex(randomness(n))).hexdigest()[:16], 16)

def first_push_time(repo, sha, gitdir):
    """Server time (unix) of the earliest GitHub push whose head contains sha, or None."""
    r = subprocess.run(["gh", "api", "--paginate", f"repos/{repo}/activity?activity_type=push&per_page=100",
                        "--jq", ".[] | [.timestamp, .after] | @tsv"], capture_output=True, text=True)
    best = None
    for line in r.stdout.splitlines():
        ts, after = line.split("\t")
        if subprocess.run(["git", "-C", gitdir, "merge-base", "--is-ancestor", sha, after],
                          capture_output=True).returncode == 0:
            t = int(subprocess.run(["date", "-u", "-d", ts, "+%s"], capture_output=True, text=True).stdout)
            best = t if best is None else min(best, t)
    return best
