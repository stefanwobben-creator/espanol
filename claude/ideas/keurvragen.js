/* Dezelfde twee regels die pw-audicion.js stelt, maar hier, zodat ze niet pas in de poort afgaan. */
const V = require('./vragen.js');
let fout = 0;
Object.keys(V).forEach(function (id) {
  V[id].forEach(function (v, qi) {
    const naam = id + ' q' + qi;
    if (v.opts.length !== 4 || v.optsEn.length !== 4) { console.log('✗ ' + naam + ': niet vier opties'); fout++; }
    if (new Set(v.opts).size !== 4 || new Set(v.optsEn).size !== 4) { console.log('✗ ' + naam + ': dubbele optie'); fout++; }
    if (!(v.c >= 0 && v.c < 4)) { console.log('✗ ' + naam + ': c wijst nergens heen'); fout++; }
    ['opts', 'optsEn'].forEach(function (k) {
      const lens = v[k].map(function (o) { return o.length; });
      const eigen = lens[v.c];
      const rest = lens.filter(function (_, i) { return i !== v.c; });
      const over = eigen - Math.max.apply(null, rest);
      if (over > 5) { console.log('✗ ' + naam + ' ' + k + ': juiste antwoord ' + over + ' tekens te lang (' + v[k][v.c] + ')'); fout++; }
    });
    if (!v.q || !v.qEn || !v.waarom || !v.waaromEn) { console.log('✗ ' + naam + ': vertaling of uitleg mist'); fout++; }
  });
});
const plekken = {};
Object.keys(V).forEach(function (id) { V[id].forEach(function (v) { plekken[v.c] = (plekken[v.c] || 0) + 1; }); });
console.log('\njuiste antwoord staat op plek: ' + JSON.stringify(plekken));
console.log(fout ? fout + ' GEFAALD' : 'achttien vragen, beide regels gehaald');
process.exit(fout ? 1 : 0);
