"""Does the never-forgiving strategy die out under noise? A claim on Moltbook (relayzero, post 07cb3fc8): always-defect
wins early then starves; grim can't recover from noise, forgiving variants stay solvent. Tested on the 8 house
strategies with exact expected scores (exact_ipd.py, no sampling: an earlier Monte Carlo run of this flipped winners
between seeds), 200 rounds, replicator dynamics from equal shares, a share under 0.001 goes extinct.
Usage: python3 grim_survives.py   (from this folder)"""
import sys; sys.path.insert(0, '..')
import ipd, exact_ipd
S = ipd.load('../field/house.txt') if __import__('os').path.exists('../field/house.txt') else ipd.load('../house.txt')
names = [s['name'] for s in S]; ix = {n: i for i, n in enumerate(names)}
for noise in (0.0, 0.01, 0.05, 0.10):
    exact_ipd.NOISE = noise
    M = [[exact_ipd.exact(a, b)[0] for b in S] for a in S]
    H = ipd.replicator(M, gens=2000, floor=0.001)
    pk = max(range(1, len(H)), key=lambda t: H[t][ix['alld']])
    print(f'noise {noise:.2f}: self-play per round grim {M[ix["grim"]][ix["grim"]]:.2f}, tft {M[ix["tft"]][ix["tft"]]:.2f}, '
          f'pavlov {M[ix["pavlov"]][ix["pavlov"]]:.2f}; grim vs pavlov {M[ix["grim"]][ix["pavlov"]]:.2f}, '
          f'grim vs tf2t {M[ix["grim"]][ix["tf2t"]]:.2f}, grim vs allc {M[ix["grim"]][ix["allc"]]:.2f}')
    print(f'  round-robin mean: ' + ', '.join(f'{n} {sum(M[ix[n]]) / len(S):.2f}' for n in sorted(names, key=lambda n: -sum(M[ix[n]]))))
    print(f'  alld share: gen 0 {H[0][ix["alld"]]:.3f}, highest later {H[pk][ix["alld"]]:.3f} (gen {pk}), extinct by gen '
          f'{next((t for t, h in enumerate(H) if h[ix["alld"]] == 0), None)}')
    for t in (50, 200, 2000):
        print(f'  gen {t}: ' + ', '.join(f'{n} {H[t][i]:.2f}' for i, n in enumerate(names) if H[t][i] > 0))

# How close did grim come to extinction? Its lowest share, and the outcome when the floor is raised to 0.01.
print()
for noise in (0.01, 0.05):
    exact_ipd.NOISE = noise
    M = [[exact_ipd.exact(a, b)[0] for b in S] for a in S]
    H = ipd.replicator(M, gens=2000, floor=0.001)
    lo = min(range(len(H)), key=lambda t: H[t][ix['grim']])
    H2 = ipd.replicator(M, gens=2000, floor=0.01)
    print(f'noise {noise:.2f}: grim lowest share {H[lo][ix["grim"]]:.4f} at gen {lo}; with floor 0.01, gen 2000: '
          + ', '.join(f'{n} {H2[-1][i]:.2f}' for i, n in enumerate(names) if H2[-1][i] > 0))
