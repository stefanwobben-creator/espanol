#!/usr/bin/env node
// versiegelijk.js (27 aug, v23.199) — versie.txt en APP_VERSIE zeggen hetzelfde
//
// WAAROM DIT ER IS
//
// Bij het herstellen van de keten v23.197 → v23.198 (twee ronden die ik zelf had laten verwezen door
// tussendoor naar origin/main terug te zetten) liep versie.txt op v23.198 terwijl APP_VERSIE in
// index.html op v23.197 bleef staan. Git had de ene regel wel meegenomen en de andere niet, en
// niets merkte het op.
//
// Dat getal staat onderaan elk scherm van de app en het is het enige waaraan Stefan kan zien welke
// versie hij draait. Twee bronnen voor één getal is dezelfde vorm als alle botsingen van deze week
// (de Door-knop, de functienaam, de vier beloftes in één som): zolang niemand ze naast elkaar legt,
// kunnen ze uit elkaar lopen zonder één foutmelding.
//
// WAT HIJ DOET
//
// Leest versie.txt en de toekenning van APP_VERSIE in index.html, en wordt rood als ze verschillen.
// Statisch, dus hij kost geen browser en hij hangt in de poort.
const fs = require('fs');
const path = require('path');

const WORTEL = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(WORTEL, 'index.html'), 'utf8');
const txt = fs.readFileSync(path.join(WORTEL, 'versie.txt'), 'utf8').trim();

const m = /var APP_VERSIE = "([^"]+)"/.exec(app);
if (!m) {
  console.log('APP_VERSIE staat niet in index.html; daar hangt het versienummer onderaan elk scherm aan.');
  process.exit(1);
}
const inApp = m[1];

console.log('versie.txt   : ' + txt);
console.log('APP_VERSIE   : ' + inApp);

if (txt !== inApp) {
  console.log('\nDEZE TWEE HOREN GELIJK TE ZIJN.');
  console.log('Het nummer onderaan de app komt uit APP_VERSIE; versie.txt is wat de nachtrun en de');
  console.log('patchscripts lezen. Lopen ze uiteen, dan zegt de app iets anders dan wat er draait.');
  process.exit(1);
}

/* het controlegeval: deze vergelijking moet een verschil kunnen zien. Zonder dit is "ze zijn gelijk"
   ook waar als de regex nergens op past en beide kanten leeg blijven. */
if (!/^v\d+\.\d+/.test(txt)) {
  console.log('\nCONTROLE MISLUKT: het gelezen nummer ziet er niet uit als een versie (' + txt + ').');
  process.exit(1);
}

console.log('gelijk, en het gelezen nummer ziet eruit als een versie');
