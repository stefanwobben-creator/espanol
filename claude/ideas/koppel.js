/* Zet de herschreven vragen uit vragen.js in scenes.js, zodat scenes.js de enige bron blijft die de
   patchgenerator leest. */
const fs = require('fs');
const V = require('./vragen.js');
const q = JSON.stringify;
let s = fs.readFileSync('scenes.js', 'utf8');
Object.keys(V).forEach(function (id) {
  const start = s.indexOf('{ id:"' + id + '"');
  if (start < 0) throw new Error('scene niet gevonden: ' + id);
  const vi = s.indexOf('vragen:[', start);
  if (vi < 0) throw new Error('vragen niet gevonden: ' + id);
  // het eind van de vragen-array: de bijbehorende ]
  let diepte = 0, eind = -1;
  for (let i = s.indexOf('[', vi); i < s.length; i++) {
    if (s[i] === '[') diepte++;
    else if (s[i] === ']') { diepte--; if (diepte === 0) { eind = i; break; } }
  }
  if (eind < 0) throw new Error('eind niet gevonden: ' + id);
  const nieuw = 'vragen:[\n' + V[id].map(function (v) {
    return '    {q:' + q(v.q) + ', qEn:' + q(v.qEn) + ',\n' +
      '     opts:[' + v.opts.map(q).join(',') + '],\n' +
      '     optsEn:[' + v.optsEn.map(q).join(',') + '], c:' + v.c + ',\n' +
      '     waarom:' + q(v.waarom) + ',\n' +
      '     waaromEn:' + q(v.waaromEn) + '}';
  }).join(',\n') + '\n  ]';
  s = s.slice(0, vi) + nieuw + s.slice(eind + 1);
});
fs.writeFileSync('scenes.js', s);
const S = require('./scenes.js');
console.log(S.length + ' scenes, vragen per scene: ' + S.map(function (x) { return x.vragen.length; }).join(' '));
S.forEach(function (sc) {
  sc.vragen.forEach(function (v, i) {
    if (v.opts.length !== 4 || v.optsEn.length !== 4) throw new Error(sc.id + ' q' + i);
  });
});
console.log('vier opties overal, scenes.js laadt');
