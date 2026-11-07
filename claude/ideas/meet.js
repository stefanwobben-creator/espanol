const path = require('path');
const L = require(path.join(__dirname, '..', '..', 'tools', 'leesdekking.js'));
const T = require('./teksten.js');
const P = require('./pak.js');
const bron = L.leesBronnen();
bron.words = bron.words.concat(P.kaarten);
bron.verbos = bron.verbos.concat(P.verbos);
const budget = L.begroting(bron);
let tb = 0, tg = 0; const alle = {};
Object.keys(T).forEach(function (id) {
  const d = L.dekking(T[id], budget);
  tb += d.bekend; tg += d.geteld;
  const w = T[id].split(/\s+/).length;
  console.log(id.padEnd(9) + w + 'w  ' + d.pct.toFixed(1) + '%  (' + d.namen + ' namen)  ' +
    d.onbekend.map(function (x) { return x.w + (x.n > 1 ? '*' + x.n : ''); }).join(' '));
  d.onbekend.forEach(function (x) { alle[x.w] = (alle[x.w] || 0) + x.n; });
});
console.log('\nTOTAAL ' + (100 * tb / tg).toFixed(1) + '% van ' + tg + ' woorden');
console.log('rest: ' + Object.keys(alle).sort(function (a, b) { return alle[b] - alle[a]; })
  .map(function (w) { return w + (alle[w] > 1 ? '*' + alle[w] : ''); }).join(', '));
