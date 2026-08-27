// pw-versiegelijk.js (27 aug, v23.199) — versie.txt en APP_VERSIE zeggen hetzelfde
//
// Geen browsertest, net als pw-dubbelenaam: een statische controle hoort niet op een Chromium te
// wachten. Hij staat hier omdat de poort alles draait wat pw-*.js heet.
//
// De regel en de aanleiding staan in tools/versiegelijk.js. Kort: bij het herstellen van de keten
// v23.197 → v23.198 liep versie.txt op v23.198 terwijl APP_VERSIE op v23.197 bleef staan, en niets
// merkte het. Het nummer onderaan de app zou dan iets anders zeggen dan wat er draait.
const { execFileSync } = require('child_process');
const path = require('path');

const TOOL = path.resolve(__dirname, '..', '..', 'tools', 'versiegelijk.js');

try {
  process.stdout.write(execFileSync(process.execPath, [TOOL], { encoding: 'utf8' }));
  console.log('\nalles goed');
} catch (e) {
  if (e.stdout) process.stdout.write(e.stdout);
  if (e.stderr) process.stderr.write(e.stderr);
  console.log('\n1 fout');
  process.exit(1);
}
