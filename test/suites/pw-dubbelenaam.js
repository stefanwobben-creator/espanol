// pw-dubbelenaam.js (26 aug, v23.198) — geen twee functies met dezelfde naam
//
// Geen browsertest, en dat is de bedoeling: dit is een statische controle en die hoort niet op een
// Chromium te wachten. Hij staat hier omdat de poort alles draait wat pw-*.js heet, en deze regel
// hoort in de poort.
//
// De regel zelf en de uitleg waarom hij bestaat staan in tools/dubbelenaam.js. Kort: bij het bouwen
// van de dagmeting schreef ik een tweede `function dagenSinds`, JavaScript hees hem, de laatste won,
// en mijn functie verdween zonder één foutmelding. Dezelfde botsing als de Door-knop van v23.197 en
// als de globale `ws` van v23.162. Drie keer dezelfde vorm is een ontbrekende controle.
//
// Eén plek rekent, twee plekken roepen aan: het gereedschap voor de hand, de poort voor elke ronde.
const { execFileSync } = require('child_process');
const path = require('path');

const TOOL = path.resolve(__dirname, '..', '..', 'tools', 'dubbelenaam.js');

try {
  const uit = execFileSync(process.execPath, [TOOL], { encoding: 'utf8' });
  process.stdout.write(uit);
  console.log('\nalles goed');
} catch (e) {
  if (e.stdout) process.stdout.write(e.stdout);
  if (e.stderr) process.stderr.write(e.stderr);
  console.log('\n1 fout');
  process.exit(1);
}
