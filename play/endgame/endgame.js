// Exact counterfactuals for the last five rounds of each browser /play game (zenith-claude's test, board 79212).
// Same seed -> same opponent and the same flip stream (two draws per round whatever is played), so only the
// swapped intentions in rounds 46-50 change the payoff. Run: node endgame/endgame.js gamelog
const fs = require('fs'), path = require('path');
const HERE = __dirname;
const IPD = require(path.join(HERE, '../engine.js'));
const FIELD = IPD.load(require(path.join(HERE, '../counterfactual/play_field.json')));
const ROUNDS = 50, NOISE = 0.05, W0 = 45;               // window = rounds 46..50 (index 45..49)
const flip = m => (m === 'C' ? 'D' : 'C');

function setup(seed) {
  const rng = IPD.mulberry32(seed), opp = FIELD[Math.floor(rng.random() * FIELD.length)];
  const draws = []; for (let r = 0; r < ROUNDS; r++) draws.push([rng.random() < NOISE, rng.random() < NOISE]);
  return { opp, draws };
}
// policy(r, hist) -> intended move; hist = [[myPlayed, theirPlayed], ...]
function run(opp, draws, policy) {
  let s = opp.start; const hist = [], pts = [];
  for (let r = 0; r < ROUNDS; r++) {
    let mh = policy(r, hist), ms = opp.states[s][0];
    if (draws[r][0]) mh = flip(mh);
    if (draws[r][1]) ms = flip(ms);
    const pay = { CC: 3, CD: 0, DC: 5, DD: 1 }[mh + ms];
    pts.push(pay); s = opp.states[s][1][mh]; hist.push([mh, ms]);
  }
  return { pts, played: hist.map(h => h[0]).join(''), theirs: hist.map(h => h[1]).join('') };
}
const sum = a => a.reduce((x, y) => x + y, 0);
// mulberry32 for the fitted-rule draws, so the expected value is reproducible
function mean(f, n) { let t = 0; for (let k = 0; k < n; k++) t += f(IPD.mulberry32(1000 + k)); return t / n; }

const dir = process.argv[2];
const games = fs.readdirSync(dir).filter(f => f.includes('browser')).map(f => JSON.parse(fs.readFileSync(path.join(dir, f))));
const byRound = Array.from({ length: 5 }, () => 0);
console.log('seed        opponent                                  check  win46-50  vs-copy  vs-fitted  vs-allC  P(C|C) P(C|D) last5');
for (const g of games) {
  const { opp, draws } = setup(g.seed);
  const actual = run(opp, draws, r => g.intended[r]);
  const ok = actual.played === g.played && actual.theirs === g.theirs && sum(actual.pts) === g.score.you;
  // the player's own mid-game reply rule, rounds 6-45, to the house's last PLAYED move
  let cc = 0, nc = 0, cd = 0, nd = 0;
  for (let r = 5; r < W0; r++) { const prev = actual.theirs[r - 1]; const c = g.intended[r] === 'C';
    if (prev === 'C') { nc++; cc += c; } else { nd++; cd += c; } }
  const pC = nc ? cc / nc : 1, pD = nd ? cd / nd : (nc ? cc / nc : 1);
  const win = res => sum(res.pts.slice(W0));
  const A = win(actual);
  const copy = win(run(opp, draws, (r, h) => r < W0 ? g.intended[r] : h[r - 1][1]));
  const allc = win(run(opp, draws, r => r < W0 ? g.intended[r] : 'C'));
  const fitted = mean(rng => win(run(opp, draws, (r, h) => r < W0 ? g.intended[r] :
                         (rng.random() < (h[r - 1][1] === 'C' ? pC : pD) ? 'C' : 'D'))), 2000);
  for (let k = 0; k < 5; k++) byRound[k] += g.intended[W0 + k] === 'D';
  console.log(String(g.seed).padEnd(11), opp.name.padEnd(41), ok ? 'ok   ' : 'FAIL ', String(A).padStart(6),
    String(A - copy).padStart(9), (A - fitted).toFixed(2).padStart(10), String(A - allc).padStart(8),
    pC.toFixed(2).padStart(7), pD.toFixed(2).padStart(6), ' ' + g.intended.slice(W0));
}
console.log('\nintended D by round 46..50 (of ' + games.length + '):', byRound.join(' '));
