"""Evolution chart for the tournament: small multiples, one panel per official seed
(evolution is bimodal across seeds, so a single seed misleads: on the house field seed 0
is a tft win while grim takes 17 of 20). Top five by mean final share get a categorical
hue in fixed order; everyone else is a thin gray line. One SVG per extinction floor, and a
text summary for the board, which shows only text.
usage: python3 evo_svg.py entries.txt out.svg [salt] [reps]"""
import sys
from ipd import load, seed_of, tournament, replicator

HUES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4']
GRAY, INK, MUTED, SURF = '#b5b4ab', '#1a1a19', '#6b6a63', '#fcfcfb'

def run(path, salt='', reps=100, seeds=20, floor=0.0):
    """Same seeds as official(): sha256(file+salt)[:16] + k."""
    S = load(path); names = [s['name'] for s in S]; base = seed_of(path, salt)
    return names, [replicator(tournament(S, reps=reps, seed=base + k), floor=floor) for k in range(seeds)]

def svg(names, hists, out, floor):
    cols, pw, ph, gx, gy, pad, top = 5, 160, 90, 18, 34, 40, 64
    rows = (len(hists) + cols - 1) // cols
    W = 2 * pad + cols * pw + (cols - 1) * gx; H = top + rows * (ph + gy) + 40
    final = [sum(h[-1][i] for h in hists) / len(hists) for i in range(len(names))]
    order = sorted(range(len(names)), key=lambda i: -final[i])
    color = {i: HUES[k] for k, i in enumerate(order[:5])}
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">' % (W, H),
         '<rect width="100%%" height="100%%" fill="%s"/>' % SURF,
         '<text x="%d" y="24" font-size="16" fill="%s">Population share over 1000 generations, one panel per official seed</text>' % (pad, INK),
         '<text x="%d" y="44" font-size="12" fill="%s">replicator dynamics from equal shares; %s; y axis 0 to 100%%</text>'
         % (pad, MUTED, 'no extinction floor' if not floor else 'extinct below %g' % floor)]
    for k, h in enumerate(hists):
        x0 = pad + (k % cols) * (pw + gx); y0 = top + (k // cols) * (ph + gy); G = len(h) - 1
        X = lambda g: x0 + pw * g / G
        Y = lambda p: y0 + ph * (1 - p)
        w = max(range(len(names)), key=lambda i: h[-1][i])
        o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#e4e3dc"/>' % (x0, y0, pw, ph))
        o.append('<text x="%d" y="%d" font-size="11" fill="%s">seed %d: %s %.0f%%</text>' % (x0, y0 + ph + 14, MUTED, k, names[w], 100 * h[-1][w]))
        for i in sorted(range(len(names)), key=lambda i: i in color):
            pts = ' '.join('%.1f,%.1f' % (X(g), Y(h[g][i])) for g in range(0, G + 1, 10))
            o.append('<polyline fill="none" stroke="%s" stroke-width="%s" points="%s"><title>%s: final %.1f%%</title></polyline>'
                     % (color.get(i, GRAY), 2 if i in color else 1, pts, names[i], 100 * h[-1][i]))
    lx = pad
    for i in order[:5]:
        o.append('<rect x="%d" y="%d" width="14" height="4" rx="2" fill="%s"/>' % (lx, H - 22, color[i]))
        o.append('<text x="%d" y="%d" font-size="12" fill="%s">%s</text>' % (lx + 20, H - 17, INK, names[i]))
        lx += 30 + 8 * len(names[i])
    o.append('<rect x="%d" y="%d" width="14" height="2" fill="%s"/><text x="%d" y="%d" font-size="12" fill="%s">others</text>'
             % (lx, H - 21, GRAY, lx + 20, H - 17, INK))
    o.append('</svg>')
    open(out, 'w').write('\n'.join(o))

def summary(names, hists):
    """Text for the board: who ends on top in how many seeds, with the winning share."""
    from collections import Counter
    wins = Counter(); shares = {}
    for h in hists:
        w = max(range(len(names)), key=lambda i: h[-1][i]); wins[w] += 1
        shares.setdefault(w, []).append(h[-1][w])
    for w, c in wins.most_common():
        print('  %-16s on top in %2d of %d seeds, final share %.0f..%.0f%%' % (names[w], c, len(hists), 100 * min(shares[w]), 100 * max(shares[w])))

if __name__ == '__main__':
    path, out = sys.argv[1], sys.argv[2]
    salt = sys.argv[3] if len(sys.argv) > 3 else ''
    reps = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    for fl in (0.0, 1e-4):
        names, hists = run(path, salt, reps, floor=fl)
        o = out.replace('.svg', '.floor%g.svg' % fl); svg(names, hists, o, fl)
        print('floor %g -> %s' % (fl, o)); summary(names, hists)
