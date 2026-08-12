// De hele app is één html-bestand met een handvol inline scriptblokken. Een kapotte haak daarin maakt
// het scherm wit zonder dat er een testsuite aan te pas hoeft te komen, en dat wil je binnen tien
// seconden weten in plaats van na twee minuten browsertests. Vandaar deze stap vóór de poort.
//
//   node tools/syntaxcheck.js index.html
//
// v23.55: hier stond "precies één blok", en dat klopte tot v23.53. Sindsdien zijn het er drie: de
// sluiter van het laadscherm (v23.54), het vroege proefscherm (v23.55) en het grote script. Elk blok
// wordt nu apart gecontroleerd, en dat is niet alleen nodig maar ook beter: bij een fout hoor je in
// welk blok hij zit en op welke regel van index.html.
//
// De ondergrens blijft wel staan. Zakt het aantal blokken onder de twee, dan is er iets weggevallen
// dat er hoort te zijn, en dat is precies zo'n fout die je pas in productie merkt.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const bestand = process.argv[2] || 'index.html';
const s = fs.readFileSync(bestand, 'utf8');

const blokken = [];
const re = /<script>([\s\S]*?)<\/script>/g;
let m;
while ((m = re.exec(s)) !== null) {
  blokken.push({ js: m[1], regel: s.slice(0, m.index).split('\n').length });
}

if (blokken.length < 2) {
  console.error('verwacht minstens twee inline scriptblokken, gevonden: ' + blokken.length);
  console.error('Het laadscherm (v23.54) en het vroege proefscherm (v23.55) horen er allebei te zijn.');
  console.error('Klopt het dat er nu minder zijn, pas dan deze controle aan. Zo niet: er is er een weggevallen.');
  process.exit(1);
}

let stuk = 0;
blokken.forEach((b, i) => {
  const tmp = path.join(os.tmpdir(), 'vamos-syntax-' + process.pid + '-' + i + '.js');
  fs.writeFileSync(tmp, b.js);
  try {
    execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' });
    console.log('  blok ' + (i + 1) + ' (regel ' + b.regel + ') :: ok, ' +
      b.js.length.toLocaleString('nl-NL') + ' tekens');
  } catch (e) {
    stuk++;
    // node meldt het regelnummer binnen het losse bestand; tel de regels vóór dit blok erbij op
    // zodat het nummer verwijst naar de plek in index.html waar je moet kijken.
    const patroon = new RegExp(tmp.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ':(\\d+)', 'g');
    console.error('  blok ' + (i + 1) + ' (regel ' + b.regel + ') :: STUK');
    console.error((e.stderr || Buffer.from('')).toString().replace(patroon,
      (mm, r) => bestand + ':' + (Number(r) + b.regel - 1)));
  } finally {
    try { fs.unlinkSync(tmp); } catch (e) {}
  }
});

if (stuk) process.exit(1);
const totaal = blokken.reduce((a, b) => a + b.js.length, 0);
console.log('syntax ok :: ' + bestand + ', ' + blokken.length + ' blokken, ' +
  totaal.toLocaleString('nl-NL') + ' tekens javascript');
