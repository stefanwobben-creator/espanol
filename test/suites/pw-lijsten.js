// pw-lijsten.js (13 aug, v23.85) — staat er in elke lijst wat erin hoort?
//
// Geen browser, net als pw-audiogaten.js: dit leest index.html en telt. De naam begint met pw-
// omdat test/poort.js alleen zo genoemde bestanden oppakt.
//
// WAAROM DIT ER IS
//
// v23.82 zette zes oefenzinnen in de app met dit anker:
//
//     "\n];\n\nvar B_SENTENCES = ["
//
// Dat anker kwam precies één keer voor, dus rep() gaf geen kik. Maar de array die vlak vóór
// B_SENTENCES eindigt is B_WORDS en niet SENTENCES. De zes zinnen stonden dus als woordkaarten in
// de A0-woordenlijst: "No los peles, la piel se va con la batidora." als los te leren woordje.
//
// De poort bleef 70/70 groen. Geen enkele suite kijkt naar wat er in een lijst staat, alleen naar
// wat de schermen ermee doen, en een woordkaart met een lange zin erop rendert prima. Het enige dat
// het verried was een terloops getal in content-lib: "178 zinnen" terwijl er 184 in het bestand
// stonden.
//
// De les is niet "beter opletten" maar: een anker dat één keer voorkomt is nog geen anker op de
// goede plek. En dat is te meten, want de lijsten hebben een vorm. Een woord is kort en heeft geen
// lvl; een zin is lang en heeft alt en uitleg. Wie zich vergist in de array, ziet het hier.
const fs = require('fs');
const path = require('path');

const WORTEL = path.resolve(__dirname, '..', '..');
const html = fs.readFileSync(path.join(WORTEL, 'index.html'), 'utf8');

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

function arr(naam) {
  const i = html.indexOf('var ' + naam + ' = [');
  if (i < 0) return null;
  let s = html.indexOf('[', i), d = 0, j = s;
  for (; j < html.length; j++) {
    const c = html[j];
    if (c === '[') d++;
    else if (c === ']') { d--; if (!d) break; }
  }
  try { return eval(html.slice(s, j + 1)); } catch (e) { return null; }
}

console.log('\n-- de woordenlijsten bevatten woorden --');
// 30 tekens is ruim: het langste echte item is "el diente de ajo" en "a fuego lento". Een oefenzin
// zit ver over de veertig. De grens ligt op 45 zodat een lange uitdrukking er nooit op struikelt.
['WORDS', 'B_WORDS', 'K_WORDS', 'C_WORDS'].forEach((naam) => {
  const a = arr(naam);
  if (!a) { fout++; console.log('  ✗ ' + naam + ' is niet te lezen'); return; }
  const langst = a.reduce((m, w) => Math.max(m, String(w.es || '').length), 0);
  const zinvormig = a.filter((w) => w.alt !== undefined || w.lvl !== undefined || w.uitleg !== undefined);
  console.log('  ' + naam.padEnd(9) + a.length + ' items · langste es: ' + langst);
  ok(langst <= 45, naam + ': geen item met een es langer dan 45 tekens (nu ' + langst + ')');
  ok(zinvormig.length === 0,
    naam + ': geen item met alt/lvl/uitleg erin, dat zijn zinvelden (' +
      zinvormig.map((w) => w.id).slice(0, 4).join(' ') + ')');
});

console.log('\n-- de zinnenlijsten bevatten zinnen --');
['SENTENCES', 'B_SENTENCES'].forEach((naam) => {
  const a = arr(naam);
  if (!a) { fout++; console.log('  ✗ ' + naam + ' is niet te lezen'); return; }
  const zonderAlt = a.filter((s) => !Array.isArray(s.alt) || !s.alt.length);
  const voorvoegsel = naam === 'SENTENCES' ? /^s\d+$/ : /^bs\d+$/;
  const raarId = a.filter((s) => !voorvoegsel.test(String(s.id || '')));
  console.log('  ' + naam.padEnd(11) + a.length + ' zinnen');
  ok(zonderAlt.length === 0, naam + ': elke zin heeft alt (' + zonderAlt.map((s) => s.id).slice(0, 4).join(' ') + ')');
  ok(raarId.length === 0, naam + ': elk id past bij de lijst (' + raarId.map((s) => s.id).slice(0, 4).join(' ') + ')');
});

console.log('\n-- geen id staat in twee lijsten --');
const alle = {};
const dubbel = [];
['WORDS', 'B_WORDS', 'K_WORDS', 'C_WORDS', 'SENTENCES', 'B_SENTENCES'].forEach((naam) => {
  (arr(naam) || []).forEach((x) => {
    const id = String(x.id || '');
    if (!id) return;
    if (alle[id] && alle[id] !== naam) dubbel.push(id + ' in ' + alle[id] + ' én ' + naam);
    alle[id] = naam;
  });
});
ok(dubbel.length === 0, 'elk id hoort bij één lijst (' + dubbel.slice(0, 4).join(', ') + ')');

if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
console.log('\nalles goed');
