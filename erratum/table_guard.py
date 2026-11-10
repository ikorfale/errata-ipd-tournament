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

    python3 table_guard.py dump.json f0.0001     # the floored evolution table
    python3 table_guard.py dump.json rr          # round-robin points per round
"""
import json, statistics as st, sys

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
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    d = json.load(open(sys.argv[1]))
    key = sys.argv[2]
    names = d["names"]
    cols = [[s[key][i] for s in d["seeds"]] for i in range(len(names))]
    bad, rows = guard(names, cols, key)
    if bad:
        print("\nREFUSED: a mean would misrepresent these entries; print median and per-seed ranks instead:")
        for r, n, f in bad:
            print(f"  place {r} {n}: {f}")
        sys.exit(1)
    conf = order_conflicts(rows)
    if conf:
        print("\nBOTH REQUIRED: mean and median order these pairs differently; print both columns and name the declared criterion:")
        for a, b, ma, mb, da, db in conf:
            print(f"  {a} over {b} by mean ({ma:.5f} > {mb:.5f}), under by median ({da:.5f} < {db:.5f})")
        sys.exit(3)
    print("\nOK: every ranked mean is larger than its spread, its median is not zero, and mean and median give the same order.")

if __name__ == "__main__":
    main()
