// Noisy iterated prisoner's dilemma engine, a line-by-line port of ../ipd.py (parse, match).
// Runs in the browser (window.IPD) and in node (module.exports). Strategies are data, never code.
(function (root) {
  const PAY = { CC: [3, 3], CD: [0, 5], DC: [5, 0], DD: [1, 1] };
  const MAXSTATES = 8;
  const flip = m => (m === 'C' ? 'D' : 'C');

  function parse(text) {
    let name = null, start = null; const states = {};
    for (const raw of text.trim().split('\n')) {
      const line = raw.split('#')[0].trim();
      if (!line) continue;
      if (line.toLowerCase().startsWith('name:')) { name = line.slice(5).trim(); continue; }
      if (line.toLowerCase().startsWith('start:')) { start = line.slice(6).trim(); continue; }
      const m = line.match(/^(\w+)\s*:\s*([CD])\s*;\s*C\s*->\s*(\w+)\s+D\s*->\s*(\w+)$/);
      if (!m) throw new Error('bad line: ' + raw);
      states[m[1]] = [m[2], { C: m[3], D: m[4] }];
    }
    if (!name || !(start in states)) throw new Error('need name: and a start: that is a state');
    if (Object.keys(states).length > MAXSTATES) throw new Error('more than ' + MAXSTATES + ' states');
    for (const s in states) for (const v of Object.values(states[s][1]))
      if (!(v in states)) throw new Error('state ' + s + ' points to missing ' + v);
    return { name, start, states };
  }

  function load(text) { return text.split('\n---\n').filter(b => b.trim()).map(parse); }

  // mulberry32: a tiny 32-bit PRNG with an exact Python twin (tests/rng32.py), so both engines
  // can be fed the same random stream and compared to the last point.
  function mulberry32(seed) {
    let a = seed >>> 0;
    return { random() {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    } };
  }

  function match(a, b, rounds, noise, rng) {
    let sa = a.start, sb = b.start, pa = 0, pb = 0;
    for (let r = 0; r < rounds; r++) {
      let ma = a.states[sa][0], mb = b.states[sb][0];
      if (rng.random() < noise) ma = flip(ma);
      if (rng.random() < noise) mb = flip(mb);
      const [x, y] = PAY[ma + mb]; pa += x; pb += y;
      sa = a.states[sa][1][mb]; sb = b.states[sb][1][ma];
    }
    return [pa / rounds, pb / rounds];
  }

  // One step of a live game: the human's intended move against a strategy in state s.
  // Returns both played moves (after noise), payoffs and the strategy's next state.
  function step(strat, s, humanMove, noise, rng) {
    let mh = humanMove, ms = strat.states[s][0];
    const hFlip = rng.random() < noise, sFlip = rng.random() < noise;
    if (hFlip) mh = flip(mh);
    if (sFlip) ms = flip(ms);
    const [x, y] = PAY[mh + ms];
    return { human: mh, house: ms, humanFlipped: hFlip, houseFlipped: sFlip, humanPts: x, housePts: y,
             next: strat.states[s][1][mh] };
  }

  const api = { PAY, parse, load, match, step, mulberry32 };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.IPD = api;
})(this);
