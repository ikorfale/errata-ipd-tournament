// Prints every house pairing's match scores for seeds 1..20 with the JS engine (mulberry32 stream).
const fs = require('fs'), path = require('path'), IPD = require('../play/engine.js');
const S = IPD.load(fs.readFileSync(path.join(__dirname, '..', 'field', process.argv[2] || 'house.txt'), 'utf8'));
const out = [];
for (let seed = 1; seed <= 20; seed++) {
  const rng = IPD.mulberry32(seed);
  for (let i = 0; i < S.length; i++) for (let j = i; j < S.length; j++) {
    const [x, y] = IPD.match(S[i], S[j], 200, 0.05, rng);
    out.push([seed, S[i].name, S[j].name, x, y]);
  }
}
console.log(JSON.stringify(out));
