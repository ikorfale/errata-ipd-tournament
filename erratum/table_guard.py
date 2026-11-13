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
Fifth check (12 Nov): clocks I do not hold. If the declaration also says
`beacon_round: N` (a future drand quicknet round), the run must be seeded from
that round's randomness (check.py --beacon N), the declaration must be pushed
to main on GitHub before the round is published (GitHub's activity API is the
clock), and it must never have been edited. Seeds that did not exist before the
round cannot have run before it; one never-edited file on one ref leaves no
second criterion to pick from. Tested in tests/beacon/check_clocks.py.
Sixth check (13 Nov, same reader): one round must yield one run. With a
beacon round, the runner and its inputs (FROZEN below) must be byte-identical
between the declaration's commit and the results' commit, and the guard
re-runs the declaration's own code from that round (~15 s) and requires every
number to match. Seeds are sha256(round randomness) + k, k = 0..19, with noise,
reps and field fixed in that code, so reruns cannot differ and editing the
code to get a second draw is refused. Tested in tests/one_run/check_one_run.py.

    python3 table_guard.py dump.json f0.0001     # the floored evolution table
    python3 table_guard.py dump.json rr          # round-robin points per round
    python3 table_guard.py dump.json rr --declared CRITERION.txt
    python3 table_guard.py --pin    # file_sha256/entry_sha256 lines to paste into a declaration

Seventh check (13 Nov, same reader): the entries, readably. The commit already
pins every entry byte; a declaration may also carry file_sha256 and
entry_sha256 lines (printed by --pin). If it has any, they must match the
declaration's own commit and cover every frozen file and every entry, so a
reader can check one strategy with sha256sum, without git.
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

def external_clocks(rnd, dfile, results):
    """Exit 4 unless the run was seeded by drand round rnd and the declaration was pushed before it."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import beacon
    d = os.path.dirname(os.path.abspath(dfile))
    edits = subprocess.run(["git", "-C", d, "log", "--format=%H", "--", os.path.abspath(dfile)],
                           capture_output=True, text=True).stdout.split()
    if len(edits) != 1:
        print(f"DECLARATION EDITED: {dfile} has {len(edits)} commits; only a never-edited declaration counts"); sys.exit(4)
    R = json.load(open(results))
    if R.get("beacon_round") != rnd or int(R.get("base", "0"), 16) != beacon.seed_base(rnd):
        print(f"BEACON MISMATCH: results were not seeded from drand round {rnd}"); sys.exit(4)
    repo = os.environ.get("GUARD_REPO", "ikorfale/errata-ipd-tournament")
    tp = beacon.first_push_time(repo, first_commit(dfile), os.path.dirname(os.path.abspath(dfile)))
    tb = beacon.round_time(rnd)
    if tp is None or tp >= tb:
        print(f"BEACON TOO EARLY: declaration {'never pushed to ' + repo if tp is None else 'pushed at ' + str(tp)}, "
              f"round {rnd} published at {tb}; the criterion must be public before the randomness exists"); sys.exit(4)
    return f"; external: pushed to GitHub {tb - tp} s before drand round {rnd}, which seeded the run"

FROZEN = ["ipd.py", "exact_ipd.py", "erratum/check.py", "erratum/beacon.py", "erratum/salt.txt", "field"]

def runner_changed(a, b, gitdir):
    """Files of FROZEN that differ between commits a and b (empty list = same runner, same inputs)."""
    r = subprocess.run(["git", "-C", gitdir, "diff", "--name-only", a, b, "--"] + FROZEN,
                       capture_output=True, text=True, cwd=gitdir)
    return r.stdout.split()

def pins_at(commit, gitdir):
    """sha256 of every frozen file, and of every entry of the field, as stored in commit."""
    import hashlib
    names = subprocess.run(["git", "-C", gitdir, "ls-tree", "-r", "--name-only", commit, "--"] + FROZEN,
                           capture_output=True, text=True, check=True).stdout.split()
    files, entries = {}, {}
    for n in names:
        b = subprocess.run(["git", "-C", gitdir, "show", f"{commit}:{n}"], capture_output=True, check=True).stdout
        files[n] = hashlib.sha256(b).hexdigest()
        if n == "field/final.txt":
            for blk in re.split(r"^---$", b.decode(), flags=re.M):   # entry = text between '---' lines,
                blk = blk.strip("\n")                                  # surrounding newlines removed
                m = re.search(r"^name:\s*(\S+)", blk, re.M)
                if m: entries[m.group(1)] = hashlib.sha256(blk.encode()).hexdigest()
    return files, entries

def check_pins(text, commit, gitdir):
    """Readable pins in the declaration ('file_sha256: path hex', 'entry_sha256: name hex') must match
    the declaration's own commit and cover every frozen file and every entry; '' if it has none."""
    fp = dict(re.findall(r"^file_sha256:\s*(\S+)\s+([0-9a-f]{64})\s*$", text, re.M))
    ep = dict(re.findall(r"^entry_sha256:\s*(\S+)\s+([0-9a-f]{64})\s*$", text, re.M))
    if not fp and not ep:
        return "; no readable pins (the commit pins the field; run --pin to print them)"
    files, entries = pins_at(commit, gitdir)
    for kind, got, want in (("file", fp, files), ("entry", ep, entries)):
        missing = sorted(set(want) - set(got)); extra = sorted(set(got) - set(want))
        bad = sorted(k for k in set(got) & set(want) if got[k] != want[k])
        if missing or extra or bad:
            print(f"PIN MISMATCH ({kind}): missing {missing[:5]}, unknown {extra[:5]}, wrong hash {bad[:5]}; "
                  "the declaration does not describe the field it was committed with"); sys.exit(4)
    return f"; {len(fp)} file and {len(ep)} entry hashes in the declaration match its commit"

def same_numbers(x, y, path="", tol=1e-9):
    """First place where two result trees differ, ignoring ran_at; None if they agree."""
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k == "ran_at": continue
            if k not in x or k not in y: return f"{path}/{k} missing on one side"
            d = same_numbers(x[k], y[k], f"{path}/{k}", tol)
            if d: return d
        return None
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y): return f"{path} length {len(x)} vs {len(y)}"
        for i, (a, b) in enumerate(zip(x, y)):
            d = same_numbers(a, b, f"{path}[{i}]", tol)
            if d: return d
        return None
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return None if abs(x - y) <= tol * max(1.0, abs(x), abs(y)) else f"{path} {x} vs {y}"
    return None if x == y else f"{path} {x!r} vs {y!r}"

def one_run(rnd, dfile, results):
    """Exit 4 unless these results are the only run round rnd allows: the runner and its inputs are
    byte-identical between the declaration's commit and the results' commit, and re-running the
    declaration's own code from round rnd reproduces every number (seeds are sha256(randomness)+k)."""
    import shutil, tempfile
    gd = os.path.dirname(os.path.abspath(dfile)); dc, rc = first_commit(dfile), first_commit(results) or "HEAD"
    top = subprocess.run(["git", "-C", gd, "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    ch = runner_changed(dc, rc, top)
    if ch:
        print(f"RUNNER CHANGED: {', '.join(ch)} differ between the declaration and the results; "
              "a run from edited code is a second draw from the same round"); sys.exit(4)
    tmp = tempfile.mkdtemp(prefix="replay-")
    try:
        a = subprocess.run(["git", "-C", top, "archive", dc], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", tmp], input=a.stdout, check=True)
        out = os.path.join(tmp, "erratum", "dump.json")
        if os.path.exists(out): os.remove(out)
        subprocess.run([sys.executable, os.path.join(tmp, "erratum", "check.py"), "--beacon", str(rnd)],
                       cwd=tmp, capture_output=True, check=True)
        diff = same_numbers(json.load(open(out)), json.load(open(results)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if diff:
        print(f"REPLAY MISMATCH at {diff}: the declaration's code seeded from round {rnd} gives other numbers; "
              "these results are not the one run this round allows"); sys.exit(4)
    return f"; replayed from the declaration's commit: identical (one round, one run)"

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
    b = re.search(r"^beacon_round:\s*(\d+)\s*$", open(dfile).read(), re.M)
    if b:
        note += external_clocks(int(b.group(1)), dfile, results)
        note += one_run(int(b.group(1)), dfile, results)
    else:
        note += "; local clocks only (add 'beacon_round: N' for external ones)"
    top = subprocess.run(["git", "-C", os.path.dirname(os.path.abspath(dfile)), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    note += check_pins(open(dfile).read(), first_commit(dfile), top)
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
    if args[:1] == ["--pin"]:   # print readable pins for a new declaration, from HEAD
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
        files, entries = pins_at("HEAD", top)
        for k, v in sorted(files.items()): print(f"file_sha256: {k} {v}")
        for k, v in sorted(entries.items()): print(f"entry_sha256: {k} {v}")
        return
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
