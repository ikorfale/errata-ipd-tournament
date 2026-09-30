"""Chart of final.py output: round-robin score with seed spread, and places in the three tables.
Usage: python3 results_chart.py final.out out.png"""
import sys, re
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
src, out = sys.argv[1], sys.argv[2]
rows = []
for line in open(src):
    m = re.match(r"^(\d+)\s+(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\S+\s+([\d.]+)\s+\S+\s+([\d.]+)\s+([\d.]+)\s*$", line)
    if m:
        place, name, rr, sd, p1, p2, p3, s = m.groups()
        rows.append((int(place), name.split("/")[-1], float(rr), float(sd), float(p1), float(p2), float(p3)))
INK, PAPER, RED, GREY = "#1a1a1a", "#f6f1e7", "#b3261e", "#8a8378"
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 0.45 * len(rows) + 1.6), gridspec_kw={"width_ratios": [3, 2]}, facecolor=PAPER)
names = [f"{r[0]}. {r[1]}" for r in rows][::-1]
y = range(len(rows))
rr = [r[2] for r in rows][::-1]; sd = [r[3] for r in rows][::-1]
a.set_facecolor(PAPER)
a.barh(y, rr, xerr=sd, color=[RED if r[0] == 1 else GREY for r in rows][::-1], ecolor=INK, height=0.6)
a.set_yticks(list(y)); a.set_yticklabels(names, color=INK)
a.set_xlim(min(rr) - 0.1, max(rr) + 0.05)
a.set_xlabel("round-robin payoff per round (mean of 20 seeds, bar = seed sd)", color=INK)
a.spines[["top", "right"]].set_visible(False)
b.set_facecolor(PAPER)
for j, col in enumerate((4, 5, 6)):
    for i, r in enumerate(rows[::-1]):
        b.scatter(j, i, s=520, color=RED if r[col] == 1 else "white", edgecolor=INK, zorder=2)
        b.text(j, i, f"{r[col]:g}", ha="center", va="center", fontsize=8, color="white" if r[col] == 1 else INK, zorder=3)
b.set_xticks([0, 1, 2]); b.set_xticklabels(["round robin", "evolution\n(no floor)", "evolution\n(floor 1e-4)"], color=INK)
b.set_yticks([]); b.set_xlim(-0.6, 2.6); b.set_ylim(-0.6, len(rows) - 0.4)
for s in b.spines.values(): s.set_visible(False)
b.set_title("place in each table (ties share the mean place)", color=INK, fontsize=10)
fig.suptitle("Noisy prisoner's dilemma tournament: 5% noise, 200 rounds, 100 matches per pair", color=INK)
fig.tight_layout(); fig.savefig(out, dpi=150, facecolor=PAPER)
print("wrote", out, len(rows), "rows")
