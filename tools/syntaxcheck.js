// De hele app is één html-bestand met precies één inline scriptblok. Een kapotte haak daarin maakt
// het scherm wit zonder dat er een testsuite aan te pas hoeft te komen, en dat wil je binnen tien
// seconden weten in plaats van na twee minuten browsertests. Vandaar deze stap vóór de poort.
//
//   node tools/syntaxcheck.js index.html
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const bestand = process.argv[2] || 'index.html';
const s = fs.readFileSync(bestand, 'utf8');
const blokken = s.match(/<script>([\s\S]*?)<\/script>/g) || [];

if (blokken.length !== 1) {
  console.error('verwacht precies één inline scriptblok, gevonden: ' + blokken.length);
  console.error('Klopt dat, pas dan deze controle aan. Zo niet: er is er per ongeluk een bijgekomen.');
  process.exit(1);
}

const js = blokken[0].replace(/^<script>/, '').replace(/<\/script>$/, '');
const tmp = path.join(os.tmpdir(), 'vamos-syntax-' + process.pid + '.js');
fs.writeFileSync(tmp, js);
try {
  execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' });
  console.log('syntax ok :: ' + bestand + ', ' + js.length.toLocaleString('nl-NL') + ' tekens javascript');
} catch (e) {
  // node meldt het regelnummer binnen het losse bestand; tel de regels vóór het scriptblok erbij op
  // zodat het nummer verwijst naar de plek in index.html waar je moet kijken.
  const voor = s.slice(0, s.indexOf('<script>')).split('\n').length - 1;
  const patroon = new RegExp(tmp.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ':(\\d+)', 'g');
  console.error((e.stderr || Buffer.from('')).toString().replace(patroon,
    (m, r) => bestand + ':' + (Number(r) + voor)));
  process.exit(1);
} finally {
  try { fs.unlinkSync(tmp); } catch (e) {}
}
