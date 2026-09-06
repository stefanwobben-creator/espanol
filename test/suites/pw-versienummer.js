// pw-versienummer.js (6 sep, v23.247) - één nummer, één boom
//
// Geen browsertest, net als pw-versiegelijk en pw-dubbelenaam: statische controles horen niet op een
// Chromium te wachten. Ze staan hier omdat de poort alles draait wat pw-*.js heet.
//
// WAAROM DEZE SUITE ER IS
//
// tools/versiegelijk.js bewaakt: één boom, één nummer (versie.txt en APP_VERSIE zeggen hetzelfde).
// Op 6 september bleek de andere kant onbewaakt. De avondrun ging voor het eerst zelfstandig live
// en publiceerde v23.245; mijn eigen ronde stond met datzelfde nummer open. Twee verschillende
// bomen, allebei v23.245, en geen enkele melding. Het patchscript zei zelfs opgewekt "versie.txt:
// stond al op v23.245", want zijn ene regel kon "ik heb dit al gedaan" niet onderscheiden van
// "iemand heeft mijn nummer ingenomen".
//
// Drie stukken houden dat nu tegen, en alle drie hebben ze een zelftest die deze suite draait:
//
//   claude/patchhulp.py    kiest het nummer bij het TOEPASSEN: het geplande nummer is een bodem,
//                          nooit een belofte, en de bump hangt aan het merkteken van de ronde en
//                          niet aan het nummer.
//   tools/versiehoger.js   vergelijkt bij het AFLEVEREN met wat er op origin/main leeft.
//   tools/leveren.sh       is de plek waar die controle draait, zodat hij niet over te slaan is.
//
// Elk van die drie bouwt in zijn zelftest de botsing van 6 september NA en eist dat hij rood wordt.
// Zonder die controlegevallen zou "alles groen" ook waar zijn als ze nooit rood kunnen worden.
const { execFileSync } = require('child_process');
const path = require('path');

const WORTEL = path.resolve(__dirname, '..', '..');

const stukken = [
  ['claude/patchhulp.py  (welk nummer krijgt de ronde)', 'python3', [path.join(WORTEL, 'claude', 'patchhulp.py'), '--zelftest']],
  ['tools/versiehoger.js (is dat nummer nog vrij)', process.execPath, [path.join(WORTEL, 'tools', 'versiehoger.js'), '--zelftest']],
  ['tools/leveren.sh     (en dat wordt ook echt gevraagd)', 'sh', [path.join(WORTEL, 'tools', 'leveren.sh'), '--zelftest']]
];

let fout = 0;
stukken.forEach(([naam, cmd, args]) => {
  console.log('\n== ' + naam + ' ==');
  try {
    process.stdout.write(execFileSync(cmd, args, { encoding: 'utf8', cwd: WORTEL }));
  } catch (e) {
    fout++;
    if (e.stdout) process.stdout.write(e.stdout);
    if (e.stderr) process.stderr.write(String(e.stderr));
    console.log('  -> deze zelftest ging ROOD');
  }
});

if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
console.log('\nalles goed');
