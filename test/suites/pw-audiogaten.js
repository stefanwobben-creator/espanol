// pw-audiogaten.js (13 aug, v23.75) — bewaakt of de opnames de zinnen nog bijhouden.
//
// Deze suite start geen browser. Hij heet toch pw-, want de poort pakt alleen bestanden op die zo
// heten (zie test/poort.js regel 65) en er is bewust precies één weg naar live. Wat hij doet is
// tellen: welke zin-ids staan in index.html, en welke daarvan hebben een mp3.
//
// WAAROM DIT ER IS
//
// Stefan, 13 aug: "is het mogelijk om een lijst te krijgen van wat concreet is toegevoegd? bijv
// nieuwe audiolessen? dat staat volgens mij stil."
//
// Het stond stil, en niemand kon dat zien. audio/dictado/ bleef sinds 30 juli op 201 bestanden
// staan terwijl SENTENCES doorgroeide van 132 naar 178. Vijftig zinnen zonder opname, 20% van het
// corpus, en de app zei er niets over: zinSpreek() had een lege catch. Er was dus geen enkele
// meter die "de audio loopt achter" kon laten zien, en de eerste die het merkte was iemand die de
// map ging tellen.
//
// WAAROM DE DREMPEL NIET NUL IS
//
// De verleiding is om te eisen dat elke zin een opname heeft. Dat kan niet, en niet omdat het te
// streng is maar omdat de volgorde het onmogelijk maakt: de avondrun genereert zinnen, laat de
// poort erover oordelen, en spreekt pás daarna in. Op het moment dat deze suite draait heeft de
// verse zin per definitie nog geen mp3. Een drempel van nul zou dus elke nacht dichtslaan en er
// zou nooit meer iets gepubliceerd worden.
//
// Wat deze suite wél moet vangen is de toestand van vandaag: niet "vannacht loopt er een handvol
// achter" maar "er wordt al weken niets meer ingesproken". Vandaar 60. Een normale nacht levert
// drie tot zes zinnen, dus 60 is ruim twee weken stilte voordat de poort dichtgaat. Dat is laat
// genoeg om nooit een gewone nacht te blokkeren, en vroeg genoeg om het te zien voordat het weer
// een vijfde van de app is.
//
// Onder de drempel staat er een waarschuwing in het log. Dat is geen decoratie: dat is het getal
// dat er anderhalve maand niet was.
const fs = require('fs');
const path = require('path');

const WORTEL = path.resolve(__dirname, '..', '..');
const HTML = path.join(WORTEL, 'index.html');
const DREMPEL = Number(process.env.AUDIO_DREMPEL || 60);

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

const html = fs.readFileSync(HTML, 'utf8');

// SENTENCES staat als JSON-literal in de bron ("id":"s1"), B_SENTENCES met kale sleutels (id:"bs1").
// Twee patronen dus, en dat is geen slordigheid van deze suite maar van de brondata; wie ze ooit
// gelijktrekt mag hier één regel weghalen.
function ids(re) {
  const uit = new Set();
  let m;
  while ((m = re.exec(html))) uit.add(m[1]);
  return [...uit];
}
const zinnen = ids(/"id":"(s\d+)"/g).concat(ids(/id:"(bs\d+)"/g));

function bestanden(map) {
  try { return new Set(fs.readdirSync(path.join(WORTEL, 'audio', map)).map((f) => f.replace(/\.mp3$/, ''))); }
  catch (e) { return new Set(); }
}
const opnames = bestanden('dictado');

const missen = zinnen.filter((id) => !opnames.has(id));
const wezen = [...opnames].filter((id) => zinnen.indexOf(id) === -1);

console.log('\n-- dictado: elke oefenzin een stem --');
console.log('  zinnen in index.html :: ' + zinnen.length);
console.log('  mp3s in audio/dictado :: ' + opnames.size);
console.log('  zonder opname         :: ' + missen.length + (missen.length ? ' (' + missen.slice(0, 12).join(' ') + (missen.length > 12 ? ' …' : '') + ')' : ''));

ok(zinnen.length > 0, 'de zinnen zijn überhaupt uit index.html te lezen');
ok(missen.length <= DREMPEL,
  'de achterstand is ' + missen.length + ', dat is binnen de drempel van ' + DREMPEL);
if (missen.length && missen.length <= DREMPEL) {
  console.log('  ! ' + missen.length + ' zinnen wachten nog op een opname. Dat mag, zolang de avondrun ze inhaalt.');
  console.log('    Nakijken: node tools/avondrun-audio.js --droog');
}

// Weesbestanden zijn geen storing maar wel een signaal: een zin is hernoemd of verwijderd en de
// opname bleef staan. Ze kosten alleen ruimte, dus dit is een melding en geen fout.
if (wezen.length) console.log('  ! ' + wezen.length + ' opnames horen bij geen enkele zin meer: ' + wezen.slice(0, 8).join(' '));

console.log('\n-- de luisterscenes hebben hun regels --');
const scenes = [];
{
  // AUDICIONES is te groot om te parsen met een regex over het hele bestand; we pakken alleen de
  // scene-ids en tellen per scene hoeveel regels er zijn. lineas staat als array van objecten met
  // een v (stem a of b), dus we tellen de v-sleutels binnen het blok van die scene.
  const blok = html.slice(html.indexOf('var AUDICIONES = ['));
  const einde = blok.indexOf('\n];');
  const tekst = einde > 0 ? blok.slice(0, einde) : blok;
  const re = /\{id:"(e\d+)"/g;
  let m;
  const posities = [];
  while ((m = re.exec(tekst))) posities.push({ id: m[1], van: m.index });
  posities.forEach((p, i) => {
    const stuk = tekst.slice(p.van, i + 1 < posities.length ? posities[i + 1].van : tekst.length);
    scenes.push({ id: p.id, regels: (stuk.match(/\bv:"[ab]"/g) || []).length });
  });
}
const dialoogA = bestanden('dialogo-a');
const dialoogB = bestanden('dialogo-b');
let scenesMis = 0;
scenes.forEach((sc) => {
  let mis = 0;
  for (let n = 1; n <= sc.regels; n++) {
    if (!dialoogA.has(sc.id + '-' + n) && !dialoogB.has(sc.id + '-' + n)) mis++;
  }
  if (mis) { scenesMis++; console.log('  ! ' + sc.id + ': ' + mis + ' van ' + sc.regels + ' regels zonder opname'); }
});
console.log('  scenes :: ' + scenes.length + ' · regels :: ' + scenes.reduce((n, s) => n + s.regels, 0) +
  ' · opnames :: ' + (dialoogA.size + dialoogB.size));
ok(scenes.length > 0, 'de luisterscenes zijn uit index.html te lezen');
/* Hier stond eerst `scenesMis === 0`, en dat was precies de fout waartegen de kop van dit bestand
   waarschuwt. v23.79 zette er negen scenes bij en de poort ging rood, terwijl de audiostap ná de
   poort draait: die negen kónden op dat moment nog geen opname hebben. Een suite die nieuwe content
   tegenhoudt tot er audio bij is, houdt ook de audio tegen, want die komt uit dezelfde run.

   Dus dezelfde regel als hierboven bij dictado: onder de drempel een waarschuwing, erboven rood.
   Twaalf, want een grote contentdrop is negen tot tien scenes en een dode pijplijn laat ze allemaal
   staan. */
const SCENE_DREMPEL = Number(process.env.SCENE_DREMPEL || 12);
ok(scenesMis <= SCENE_DREMPEL,
  scenesMis + ' scenes wachten op een opname, drempel is ' + SCENE_DREMPEL);
if (scenesMis) console.log('  ! ' + scenesMis + ' van de ' + scenes.length +
  ' scenes wachten nog op een opname. De avondrun spreekt ze in zodra ELEVENLABS_API_KEY er staat.');

console.log('\n-- de app zwijgt niet als een bestand ontbreekt --');
// v23.75. Een lege catch is niet te onderscheiden van een kapotte knop; deze twee terugvallen zijn
// de enige reden dat een gat hoorbaar is in plaats van onzichtbaar.
const kaal = html.replace(/\/\*[\s\S]*?\*\//g, '');
ok(/zinAudioEl = null;\s*spreekTTS\(zin\.es/.test(kaal),
  'zinSpreek() valt terug op de browserstem');
ok(/boekAudioEl = null;\s*spreekTTS\(/.test(kaal),
  'boekSpreek() valt terug op de browserstem');
ok(!/if\(p && p\.catch\) p\.catch\(function\(\)\{\}\);/.test(kaal),
  'er staat nergens meer een lege catch op een audio-play');

if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
console.log('\nalles goed');
