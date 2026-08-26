#!/usr/bin/env node
// dubbelenaam.js (26 aug, v23.198) — geen twee functies met dezelfde naam
//
// WAAROM DIT ER IS
//
// Bij het bouwen van de dagmeting schreef ik een `function dagenSinds(a, b)`. Die naam was al bezet:
// twaalfduizend regels verderop staat `function dagenSinds(d)`, met één argument en een andere
// betekenis. JavaScript vindt dat geen fout. Function-declaraties worden gehesen en de laatste wint,
// dus mijn functie verdween stilletijk en elke aanroep kreeg de andere. De voorspelling gaf overal
// nul terug en er stond geen enkele foutmelding op het scherm.
//
// Dat is dezelfde botsing als de Door-knop van v23.197 (vier schermen, één id, de eerste in de
// pagina wint), nu in de namen in plaats van in de id's. En het is het derde geval in twee dagen:
// v23.162 was `ws`, de wachtrij van de woordenzoeker, die de voorspeller sloopte omdat een lokale
// variabele niet gedeclareerd was en de globale pakte.
//
// Drie keer dezelfde vorm is geen toeval maar een ontbrekende controle. Dit is die controle.
//
// WAT HIJ DOET
//
// Hij leest index.html, haalt de functie-declaraties op het hoogste niveau eruit, en wordt rood
// zodra een naam er twee keer staat. Dat is een statische controle, dus hij kost geen browser en
// hij draait in de poort mee.
//
// WAT HIJ NIET DOET
//
// Methoden in objecten, functies in functies en toewijzingen (var x = function(){}) blijven buiten
// beschouwing: die hebben een eigen scope of een eigen naamruimte, en meetellen zou ruis geven waar
// geen probleem zit. De regel gaat over de globale naamruimte, want daar zat de fout.
const fs = require('fs');
const path = require('path');

const APP = path.resolve(__dirname, '..', 'index.html');
const src = fs.readFileSync(APP, 'utf8');

// alleen declaraties die aan het begin van een regel staan: dat is in dit bestand precies het
// hoogste niveau, want alles wat genest is staat ingesprongen.
const gevonden = {};
const re = /^function\s+([A-Za-z_$][\w$]*)\s*\(/gm;
let m;
while ((m = re.exec(src)) !== null) {
  const naam = m[1];
  const regel = src.slice(0, m.index).split('\n').length;
  (gevonden[naam] = gevonden[naam] || []).push(regel);
}

const namen = Object.keys(gevonden);
const dubbel = namen.filter((n) => gevonden[n].length > 1);

console.log(namen.length + ' functies op het hoogste niveau in index.html');

if (dubbel.length) {
  console.log('\nDEZE NAMEN STAAN ER MEER DAN EEN KEER:\n');
  dubbel.forEach((n) => {
    console.log('  ' + n + '  op regel ' + gevonden[n].join(' en '));
  });
  console.log('\nJavaScript hijst function-declaraties, dus de laatste wint en de eerste verdwijnt');
  console.log('zonder foutmelding. Hernoem er een.');
  process.exit(1);
}

/* het controlegeval: deze meting moet een dubbele naam kunnen vinden. Zonder dit is "geen dubbele
   namen" ook waar als de regex nergens op past, en dan bewaakt dit bestand niets. */
const proef = 'function aap(){}\nfunction noot(){}\nfunction aap(x){}\n';
const pre = {};
let p;
const re2 = /^function\s+([A-Za-z_$][\w$]*)\s*\(/gm;
while ((p = re2.exec(proef)) !== null) (pre[p[1]] = pre[p[1]] || []).push(1);
if (!Object.keys(pre).some((k) => pre[k].length > 1)) {
  console.log('\nCONTROLE MISLUKT: de meting vindt een dubbele naam niet eens in een voorbeeld waar hij in staat.');
  process.exit(1);
}

console.log('geen enkele naam staat er twee keer (en de controle vindt er wel een als je er een neerzet)');
