#!/usr/bin/env python3
"""Refuse a places table whose means hide a bimodal column.

Lesson of the 29 Oct erratum: stft's floored share was 0 in 16 of 20 seeds and
one seed carried 97% of the mean that placed it 2nd. A printed spread would have
shown it (sd 4x the mean, lower bound below zero); a median would have shown it
faster. This guard runs on per-seed columns and exits 1 when a ranked entry's
mean is smaller than its sd across seeds, or its median is 0 while its mean is
not. Use it before any table built from seeds goes out.

Second check (10 Nov, a reader's question): an entry that wins big in a third of
seeds and loses narrowly in the rest can pass both tests above (mean 0.17, sd
0.095, median 0.10) while mean and median rank it differently from its
neighbours. Which number is right depends on what the tournament rewards, so
the guard does not choose: when the order by mean and the order by median
disagree for any pair, it exits 3 and asks for both columns plus a sentence
naming the declared criterion.

Third check (11 Nov, the same reader): "both columns plus the declared
criterion" is only honest if the criterion was declared before the results
existed. With --declared FILE the guard reads `criterion: mean` or
`criterion: median` from FILE and asks git when FILE and the results file were
first committed. It exits 4 if either is uncommitted or the declaration is not
strictly older than the results; otherwise, on a mean/median conflict, it ranks
by the declared column and exits 0. Git commit times can be forged by whoever
owns the repo, so this catches choosing after the fact by habit, not by intent;
a public push (or a post) before the run is the stronger receipt.
Fourth check (12 Nov, same reader): commit order alone passes a results file
produced earlier and committed later, or a reordered branch. The declaration's
commit must now be an ancestor of the results' commit, and if the results carry
per-seed `ran_at` (unix time, written by the runner as each seed starts), the
declaration must be committed before the first seed ran. ran_at is written by
the same hand, so it stops the honest mistake, not a forger.

    python3 table_guard.py dump.json f0.0001     # the floored evolution table
    python3 table_guard.py dump.json rr          # round-robin points per round
    python3 table_guard.py dump.json rr --declared CRITERION.txt
"""
import json, os, re, statistics as st, subprocess, sys

def first_commit_time(path):
    """Unix time of the first commit that added path, or None if it is not committed."""
    d = os.path.dirname(os.path.abspath(path))
    r = subprocess.run(["git", "-C", d, "log", "--diff-filter=A", "--follow", "--format=%ct", "--",
                        os.path.abspath(path)], capture_output=True, text=True)
    lines = r.stdout.split()
    return int(lines[-1]) if r.returncode == 0 and lines else None

def first_commit(path):
    d = os.path.dirname(os.path.abspath(path))
    r = subprocess.run(["git", "-C", d, "log", "--diff-filter=A", "--follow", "--format=%H", "--",
                        os.path.abspath(path)], capture_output=True, text=True)
    lines = r.stdout.split()
    return lines[-1] if r.returncode == 0 and lines else None

def is_ancestor(a, b, path):
    d = os.path.dirname(os.path.abspath(path))
    return subprocess.run(["git", "-C", d, "merge-base", "--is-ancestor", a, b]).returncode == 0

def read_declared(dfile, results):
    m = re.search(r"^criterion:\s*(mean|median)\s*$", open(dfile).read(), re.M)
    if not m:
        print(f"DECLARATION INVALID: {dfile} has no line 'criterion: mean' or 'criterion: median'"); sys.exit(4)
    td, tr = first_commit_time(dfile), first_commit_time(results)
    if td is None or tr is None:
        print(f"DECLARATION UNPROVEN: {'declaration' if td is None else 'results file'} is not committed; "
              "commit the criterion before the run, then the results"); sys.exit(4)
    if td >= tr:
        print(f"DECLARATION TOO LATE: criterion first committed at {td}, results at {tr}; "
              "a criterion chosen after the results exist cannot settle the order"); sys.exit(4)
    if not is_ancestor(first_commit(dfile), first_commit(results), results):
        print("DECLARATION OFF-HISTORY: the criterion's commit is not an ancestor of the results' commit "
              "(reordered or on another branch)"); sys.exit(4)
    ran = [s["ran_at"] for s in json.load(open(results)).get("seeds", []) if "ran_at" in s]
    if ran and td >= min(ran):
        print(f"DECLARATION AFTER THE RUN: criterion committed at {td}, first seed ran at {min(ran)}; "
              "results produced earlier and committed later do not count"); sys.exit(4)
    note = f", {min(ran) - td} s before the first seed ran" if ran else "; no ran_at in results, commit order only"
    print(f"declared criterion: {m.group(1)} (committed {tr - td} s before the results{note})")
    return m.group(1)

def guard(names, cols, label):
    bad = []
    rows = []
    for n, v in zip(names, cols):
        m, sd, med = st.mean(v), st.pstdev(v), st.median(v)
        nz = sum(1 for x in v if x > 0)
        rows.append((m, sd, med, nz, n))
    rows.sort(reverse=True)
    print(f"{label}: {len(cols[0])} seeds, rank by mean")
    print(f"{'rk':>2} {'entry':34} {'mean':>9} {'sd':>9} {'median':>9} {'seeds>0':>7}  flag")
    for r, (m, sd, med, nz, n) in enumerate(rows, 1):
        flag = ""
        if m > 0 and sd > m:
            flag = "sd>mean"
        if m > 0 and med == 0:
            flag = (flag + " " if flag else "") + "median=0"
        if flag:
            bad.append((r, n, flag))
        print(f"{r:>2} {n:34} {m:9.5f} {sd:9.5f} {med:9.5f} {nz:7d}  {flag}")
    return bad, rows

def order_conflicts(rows):
    """Pairs ranked one way by mean and the other way by median (ties in median ignored)."""
    out = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]          # a above b by mean
            if a[2] < b[2]:
                out.append((a[4], b[4], a[0], b[0], a[2], b[2]))
    return out

def main():
    args = sys.argv[1:]
    declared = None
    if "--declared" in args:
        i = args.index("--declared")
        dfile = args[i + 1]
        del args[i:i + 2]
        declared = read_declared(dfile, args[0])
    if len(args) < 2:
        print(__doc__); sys.exit(2)
    d = json.load(open(args[0]))
    key = args[1]
    names = d["names"]
    cols = [[s[key][i] for s in d["seeds"]] for i in range(len(names))]
    bad, rows = guard(names, cols, key)
    if bad:
        print("\nREFUSED: a mean would misrepresent these entries; print median and per-seed ranks instead:")
        for r, n, f in bad:
            print(f"  place {r} {n}: {f}")
        sys.exit(1)
    conf = order_conflicts(rows)
    if conf and declared:
        print(f"\nmean and median disagree on {len(conf)} pair(s); ranking by the declared {declared}:")
        idx = 0 if declared == "mean" else 2
        for r, row in enumerate(sorted(rows, key=lambda x: -x[idx]), 1):
            print(f"  {r:>2} {row[4]:34} {row[idx]:.5f}")
        print("Print both columns anyway; the declaration says which one decides.")
        sys.exit(0)
    if conf:
        print("\nBOTH REQUIRED: mean and median order these pairs differently; print both columns and name the declared criterion:")
        for a, b, ma, mb, da, db in conf:
            print(f"  {a} over {b} by mean ({ma:.5f} > {mb:.5f}), under by median ({da:.5f} < {db:.5f})")
        sys.exit(3)
    print("\nOK: every ranked mean is larger than its spread, its median is not zero, and mean and median give the same order.")

if __name__ == "__main__":
    main()
