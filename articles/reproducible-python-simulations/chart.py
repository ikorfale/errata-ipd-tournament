"""Chart of hashseed.json: which strategy random.Random(42).choice(list(set)) picked in 40 fresh processes."""
import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d = json.load(open("hashseed.json"))["hash seed not set"]["choice(list(set))"]
items = sorted(d.items(), key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(12, 6.3), dpi=100)
y = range(len(items))
ax.barh(list(y), [v for _, v in items], color="#257de0", height=0.62)
ax.set_yticks(list(y), [k for k, _ in items], fontsize=13, color="#191919")
for i, (_, v) in enumerate(items): ax.text(v + 0.15, i, str(v), va="center", fontsize=12, color="#191919")
ax.set_xlabel("processes (of 40) that picked this strategy", fontsize=12, color="#666666")
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#cccccc"); ax.tick_params(colors="#666666", length=0)
ax.xaxis.grid(True, color="#eeeeee"); ax.set_axisbelow(True)
fig.suptitle("Same seed, 40 runs, 8 different answers", x=0.06, ha="left", fontsize=20, color="#191919", y=0.97)
ax.set_title("random.Random(42).choice(list(a_set_of_strings)) on CPython 3.14.4, PYTHONHASHSEED unset.\n"
             "With choice(sorted(...)) or PYTHONHASHSEED=0, all 40 runs picked 'allc'.",
             loc="left", fontsize=12.5, color="#666666", pad=14)
fig.text(0.06, 0.02, "errata.page · script: hashseed_probe.py, chart.py", fontsize=10, color="#666666")
plt.tight_layout(rect=(0.02, 0.04, 1, 0.93)); plt.savefig("python-hash-seed-random-choice.png")
