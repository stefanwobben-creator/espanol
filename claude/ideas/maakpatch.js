/* Bouwt claude/patch-v23.273.py uit teksten.js, meta.js, pak.js en scenes.js. De data staat los van
   de patch omdat de meting op de data draait en niet op de patch. */
const fs = require('fs');
const T = require('./teksten.js'), M = require('./meta.js'), P = require('./pak.js'), S = require('./scenes.js');
const q = JSON.stringify;

/* ---- de woordkaarten, doorgenummerd vanaf l98 ---- */
let n = 97;
const kaarten = P.kaarten.map(function (k) {
  n++;
  const d = [' {id:"l' + n + '"', 'es:' + q(k.es), 'nl:' + q(k.nl), 'en:' + q(k.en), 'tag:' + q(k.tag)];
  if (k.meer) d.push('meer:' + q(k.meer));
  return d.join(',') + '}';
}).join(',\n');

const verbos = P.verbos.map(function (v) {
  return ' {inf:' + q(v.inf) + ',nl:' + q(v.nl) + ',en:' + q(v.en) +
    ',presente:[' + v.presente.map(q).join(', ') + ']}';
}).join(',\n');

/* ---- de tien hoofdstukken ---- */
const hoofdstukken = Object.keys(T).map(function (id, i) {
  const m = M[id];
  const alineas = T[id].split('\n\n').filter(function (p) { return p.trim(); });
  const tekst = alineas.map(function (p, j) {
    return '   ' + q(p + (j < alineas.length - 1 ? '\n\n' : ''));
  }).join('+\n');
  const vragen = m.vragen.map(function (v) {
    return '   {q:' + q(v.q) + ', opts:[' + v.opts.map(q).join(',') + '], c:' + v.c + '}';
  }).join(',\n');
  const vert = m.vert.map(function (r) { return '   ' + q(r); }).join(',\n');
  return ' {id:' + q(id) + ', num:' + (i + 1) + ', deel:"Diez ideas", titel:' + q(m.titel) + ', drempel:0,\n' +
    '  tekst:\n' + tekst + ',\n' +
    '  vragen:[\n' + vragen + '\n  ],\n' +
    '  reflectie:' + q(m.reflectie) + ',\n' +
    '  vert:[\n' + vert + '\n  ]}';
}).join(',\n');

/* ---- de zes luisterscenes ---- */
const scenes = S.map(function (sc) {
  const lineas = sc.lineas.map(function (l) { return '   {v:' + q(l.v) + ', es:' + q(l.es) + '}'; }).join(',\n');
  const vragen = sc.vragen.map(function (v) {
    return '   {q:' + q(v.q) + ', qEn:' + q(v.qEn) + ',\n' +
      '    opts:[' + v.opts.map(q).join(',') + '],\n' +
      '    optsEn:[' + v.optsEn.map(q).join(',') + '], c:' + v.c + ',\n' +
      '    waarom:' + q(v.waarom) + ',\n' +
      '    waaromEn:' + q(v.waaromEn) + '}';
  }).join(',\n');
  return ' {id:' + q(sc.id) + ', nivel:' + q(sc.nivel) + ', tema:' + q(sc.tema) + ',\n' +
    '  titel:' + q(sc.titel) + ', titelEn:' + q(sc.titelEn) + ',\n' +
    '  lineas:[\n' + lineas + '\n  ],\n' +
    '  vragen:[\n' + vragen + '\n  ]}';
}).join(',\n');

fs.writeFileSync('blokken.json', JSON.stringify({ kaarten, verbos, hoofdstukken, scenes }, null, 1));
console.log('blokken geschreven: ' + P.kaarten.length + ' kaarten, ' + P.verbos.length + ' werkwoorden, ' +
  Object.keys(T).length + ' hoofdstukken, ' + S.length + ' scenes');
