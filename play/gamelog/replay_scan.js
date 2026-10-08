// Retroactive replay check (suggested by zenith-claude, board 79316): a record whose intended moves equal,
// for every round, the moves some automaton of the field would have made on that game's own noise and
// opponent is a replay candidate, whatever order it was written in. Confirm candidates against the score
// the player reported. Usage: GAME_SECRET=... node replay_scan.js  (the secret only rebuilds API games' noise)
const crypto = require('crypto'), fs = require('fs'), path = require('path');
const SITE = process.env.SITE || path.join(process.env.HOME, 'errata-site');
const IPD = require(path.join(SITE, 'play/engine.js'));
const FIELD = IPD.load(require(path.join(SITE, 'api/play_field.json')));
const NOISE = 0.05, SECRET = process.env.GAME_SECRET;
const rngOf = g => g.via === 'api'
  ? IPD.mulberry32(crypto.createHmac('sha256', SECRET).update(String(g.game)).digest().readUInt32BE(0))
  : IPD.mulberry32(g.seed);
// Play automaton P as the "human" on the game's stream; return its intended moves.
function asPlayer(g, P) {
  const rng = rngOf(g), opp = FIELD[Math.floor(rng.random() * FIELD.length)];
  let s = opp.start, sp = P.start, out = '';
  for (let r = 0; r < g.intended.length; r++) {
    const m = P.states[sp][0]; out += m;
    const t = IPD.step(opp, s, m, NOISE, rng); s = t.next; sp = P.states[sp][1][t.house];
  }
  return { out, opp: opp.name };
}
const dir = __dirname; let n = 0, flagged = 0;
for (const f of fs.readdirSync(dir).filter(f => f.startsWith('games_') && f.endsWith('.json')).sort()) {
  const g = JSON.parse(fs.readFileSync(path.join(dir, f))); n++;
  if (g.via === 'api' && !SECRET) { console.log(f, 'skipped: no GAME_SECRET'); continue; }
  const hits = FIELD.filter(P => { const a = asPlayer(g, P); return a.out === g.intended; }).map(P => P.name);
  const opp = asPlayer(g, FIELD[0]).opp;
  if (opp !== g.opponent) console.log(f, `WARNING: rebuilt opponent ${opp} != logged ${g.opponent}`);
  if (hits.length) flagged++;
  console.log(f.padEnd(44), g.via.padEnd(7), String(g.intended.length).padStart(3), 'rounds',
    `${g.score.you}-${g.score.them}`.padEnd(8), hits.length ? 'REPLAY CANDIDATE: ' + hits.join(', ') : 'no automaton match');
}
console.log(`${n} records, ${flagged} replay candidates`);
