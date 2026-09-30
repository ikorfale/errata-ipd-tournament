# Where do my house automata rank in Axelrod-Python noisy tournaments (Glynatsi, Knight, Harper; zenodo 10246247, subset_noise)?
import csv, collections, statistics as st
MINE = {"Cooperator":"allc","Defector":"alld","Tit For Tat":"tft","Suspicious Tit For Tat":"stft","Grudger":"grim",
        "Win-Stay Lose-Shift":"pavlov","Tit For 2 Tats":"tf2t","Alternator":"alternator"}
R = collections.defaultdict(list); names=collections.Counter(); noises=[]; tours=set()
for row in csv.DictReader(open("subset_noise.csv")):
    names[row["Name"]]+=1; tours.add(row["seed"]+"|"+row["noise"]+"|"+row["size"])
    nz=float(row["noise"])
    if row["Name"] in MINE: R[(row["Name"], "near5" if 0.03<=nz<=0.07 else "all")].append(float(row["Normalized_Rank"]))
    if row["Name"]=="Cooperator": noises.append(nz)
print("rows tournaments", sum(names.values()), len(tours), "distinct strategies", len(names))
print("noise range", min(noises), max(noises), "tournaments with noise 0.03-0.07:", sum(0.03<=x<=0.07 for x in noises))
for n,m in MINE.items():
    a=R[(n,"all")]+R[(n,"near5")]; b=R[(n,"near5")]
    if not a: print(m, n, "ABSENT"); continue
    print(f"{m:10s} {n:24s} all: n={len(a):4d} median_norm_rank={st.median(a):.3f} | noise 3-7%: n={len(b):3d} median={st.median(b) if b else float('nan'):.3f}")
print("similar names:", [k for k in names if any(w in k for w in ("Grudger","Stay","Tit For","Pavlov","Generous"))][:40])
