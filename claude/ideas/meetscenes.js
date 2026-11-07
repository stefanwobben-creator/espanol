const path = require('path');
const L = require(path.join(__dirname, '..', '..', 'tools', 'leesdekking.js'));
const P = require('./pak.js');
const S = require('./scenes.js');
const bron = L.leesBronnen();
bron.words = bron.words.concat(P.kaarten);
bron.verbos = bron.verbos.concat(P.verbos);
const budget = L.begroting(bron);
let tb = 0, tg = 0; const alle = {};
S.forEach(function (sc) {
  const t = sc.lineas.map(function (r) { return r.es; }).join(' ');
  const d = L.dekking(t, budget);
  tb += d.bekend; tg += d.geteld;
  console.log(sc.id + ' ' + sc.tema.padEnd(13) + d.pct.toFixed(1) + '%  ' +
    d.onbekend.map(function (x) { return x.w; }).join(' '));
  d.onbekend.forEach(function (x) { alle[x.w] = (alle[x.w] || 0) + x.n; });
});
console.log('\nzes scenes samen: ' + (100 * tb / tg).toFixed(1) + '% van ' + tg + ' woorden');
console.log('rest: ' + Object.keys(alle).join(', '));
