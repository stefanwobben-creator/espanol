#!/usr/bin/env node
// avondrun-herkansing.js (28 aug) — mag deze mislukking nog een keer?
//
// WAAROM DIT ER IS
//
// De avondrun stond vijf nachten op rij rood met "De avondrun heeft niets gepubliceerd (geklapt)".
// "geklapt" komt uit avondrun.sh en betekent één ding: curriculum.js eindigde met een andere code
// dan nul. En dáár zat de fout:
//
//     CODE=0
//     node tools/curriculum.js $VLAGGEN || CODE=$?
//     if [ "$CODE" -ne 0 ]; then ... echo "wat=geklapt" ... exit "$CODE"; fi
//
// Het script heet "hoogstens twee pogingen" en heeft een lus die daarvoor bestaat, maar een
// klapper springt er bij poging één meteen uit. De herkansing dekte dus alleen het geval "de poort
// keurde de tekst af" en niet het geval "de run viel om". Sinds v23.178 is dat tweede geval juist
// het gewone geval geworden, want toen kreeg curriculum.js exitcode 1 voor "beloofd en niets
// geleverd". De herkansing was er, en precies de meest voorkomende mislukking liep eromheen.
//
// WAAROM DIT EEN APART BESTAND IS EN GEEN REGEL SHELL
//
// Niet elke klapper verdient een herkansing. Twaalf minuten opnieuw draaien om weer te horen dat
// er geen taalmodel bereikbaar is, kost een nacht en levert niets. Dat onderscheid is een regel met
// gevallen, en een regel met gevallen hoort een proef te hebben. In shell krijgt hij die niet.
//
// GEBRUIK
//   node tools/avondrun-herkansing.js <exitcode> [pad-naar-hartslag]
//     exit 0  → probeer het nog een keer
//     exit 1  → stoppen, dit lost zich niet op door opnieuw te vragen
//   node tools/avondrun-herkansing.js --zelftest
const fs = require('fs');
const path = require('path');

/* Wat er níét opnieuw geprobeerd hoeft te worden. Deze redenen komen letterlijk uit
   HART.staat.reden in curriculum.js; ze staan hier als patroon zodat een kleine herformulering daar
   deze lijst niet stil laat verlopen — een patroon dat nergens meer op past is zichtbaar in de
   zelftest hieronder, een gemiste string niet. */
const ZINLOOS = [
  { patroon: /geen taalmodel bereikbaar/i, waarom: 'er is geen model om het nog eens aan te vragen' },
  { patroon: /ladder onbereikbaar/i,       waarom: 'de ladder is onbereikbaar, dus een tweede worp komt er niet' },
  { patroon: /ADMIN_KEY/i,                 waarom: 'de sleutel ontbreekt, en die komt niet vanzelf terug' }
];

function herkansing(code, hart) {
  if (!code) return { nog: false, waarom: 'de run eindigde goed' };
  const reden = (hart && hart.reden) || '';
  for (const z of ZINLOOS) {
    if (z.patroon.test(reden)) return { nog: false, waarom: z.waarom, reden };
  }
  return { nog: true, waarom: 'een klapper is een mislukte worp, en daar is de tweede poging voor', reden };
}

function leesHart(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (e) { return null; }
}

// ---------------------------------------------------------------- zelftest
function zelftest() {
  let mis = 0;
  const proef = (goed, wat) => { console.log((goed ? '  ok   ' : '  FOUT ') + wat); if (!goed) mis++; };

  proef(herkansing(0, null).nog === false, 'code 0 is geen mislukking, dus geen herkansing');

  /* het geval van de laatste vijf nachten: curriculum.js eindigt met 1 omdat er niets geleverd is.
     Dat is precies waar de tweede poging voor bedoeld was. */
  proef(herkansing(1, { reden: 'beloofd en niet geleverd: de kale zinnen' }).nog === true,
    'beloofd en niet geleverd verdient een tweede worp');
  proef(herkansing(1, { reden: 'het besluit vroeg om 5 stuk(ken) werk en er is niets van weggeschreven' }).nog === true,
    'en de oude formulering daarvan ook');
  proef(herkansing(1, { reden: 'de run klapte: oud is not defined' }).nog === true,
    'een programmeerfout ook: die kan aan één ongelukkig pad liggen');
  proef(herkansing(1, null).nog === true,
    'en een klapper zonder hartslag ook, want dan weet je juist niets');

  /* de controlegevallen: altijd ja is net zo fout als altijd nee. */
  proef(herkansing(1, { reden: 'geen taalmodel bereikbaar' }).nog === false,
    'CONTROLE: geen taalmodel is zinloos om nog eens te vragen');
  proef(herkansing(1, { reden: 'ladder onbereikbaar: 503' }).nog === false,
    'CONTROLE: een onbereikbare ladder ook');

  /* en elk patroon moet nog ergens op passen. Een lijst die stil verloopt omdat de tekst aan de
     andere kant is veranderd, is precies hoe deze bug vijf nachten kon duren. */
  const dekking = ZINLOOS.map(z => ({
    p: String(z.patroon),
    raakt: [
      'geen taalmodel bereikbaar', 'ladder onbereikbaar: 503', 'ADMIN_KEY-secret ontbreekt'
    ].some(r => z.patroon.test(r))
  }));
  proef(dekking.every(d => d.raakt),
    'CONTROLE: elk patroon past nog op een echte reden (' +
    dekking.filter(d => !d.raakt).map(d => d.p).join(', ') + ')');

  return mis;
}

// ---------------------------------------------------------------- ingang
const arg = process.argv[2];
if (arg === '--zelftest') {
  const mis = zelftest();
  console.log(mis ? `\n${mis} fout` : '\nherkansing: alles goed');
  process.exit(mis ? 1 : 0);
}

const code = Number(arg || 0);
const hartPad = process.argv[3] || path.resolve(__dirname, 'avondrun-hart.json');
const uit = herkansing(code, leesHart(hartPad));
console.log(uit.nog
  ? `nog een poging: ${uit.waarom}`
  : `stoppen: ${uit.waarom}${uit.reden ? ' (' + uit.reden + ')' : ''}`);
process.exit(uit.nog ? 0 : 1);
