// pw-leesdekking.js (7 nov, v23.272) — is wat er te lezen staat ook te lezen?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan vroeg om nieuwe lees- en luisterstof "passend bij mijn niveau". Dat is een meetbare
// eigenschap, en hij werd nooit gemeten: de 43 hoofdstukken en 21 scenes die er staan zijn
// geschreven zonder dat iets natelde of ze te volgen waren.
//
// Hu en Nation (2000), en Laufer: om een tekst zonder woordenboek te volgen moet je ongeveer 98
// procent van de lopende woorden kennen; met hulp (en deze app heeft hulp: je tikt een woord aan)
// kom je weg met 95. Onder de 90 is het geen lezen meer maar ontcijferen.
//
// EN OMDAT IK HET ZELF FOUT HEB GEMETEN, STAAT HET NU IN DE POORT
//
// Een week lang stond er in drie projectnotities dat de dekking 68 tot 74 procent was. Dat klopte
// niet: de meting keek alleen naar WORDS (437 kaarten) en vergat B_WORDS, K_WORDS en C_WORDS
// (samen ruim tweeduizend), en rekende geen enkele werkwoordsvorm mee. Een getal dat nergens in de
// poort staat, kan een week lang verkeerd zijn zonder dat iemand het ziet. Vandaar deze suite.
//
// WAT HIJ BEWAAKT
//
//   1. GEEN ENKEL HOOFDSTUK ONDER DE 90. Dat is de ondergrens van lezen.
//   2. ELKE REEKS GEMIDDELD BOVEN DE 95, en het hele boek boven de 97.
//   3. DE LUISTERSCENES BOVEN DE 95.
//   4. DE BEGROTING IS COMPLEET. Het controlegeval bij 1 tot en met 3: die percentages zijn zo
//      hoog te krijgen door de begroting op te blazen. Dus wordt ook geteld dat alle vijf de
//      woordenbakken meedoen, en dat de app ze bij het laden ook echt samenvoegt.
//   5. DE LEESWOORDEN KOMEN LANGS. Een bak die aan geen les hangt en niet in allowedWordIds staat,
//      ligt er wel maar wordt nooit geoefend (dezelfde val als v19.84 en v23.15).
const path = require('path');
const { chromium } = require('playwright');
const L = require(path.join(__dirname, '..', '..', 'tools', 'leesdekking.js'));

const U = 'http://localhost:8321/espanol-stefan.html';

// De grenzen staan net onder de gemeten stand van 7 november (97,9 / 99,2 / 96,0 / 97,8 en 96,8).
// Ze zijn een ratel en geen streefcijfer: ze mogen omhoog als de stand omhoog gaat.
const VLOER_HOOFDSTUK = 90;
const VLOER_REEKS = 95;
const VLOER_BOEK = 97;
const VLOER_LUISTER = 95;
const VLOER_BEGROTING = 30000;

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  // ---- 1 tot en met 4: de meting, puur in node ----
  const bron = L.leesBronnen();
  const budget = L.begroting(bron);

  console.log('\n-- 1. de begroting --');
  console.log('   ' + budget.size + ' woordvormen, ' + bron.words.length + ' kaarten, ' +
    bron.verbos.length + ' werkwoorden');
  ok(budget.size >= VLOER_BEGROTING,
    'de begroting telt ' + budget.size + ' vormen (ondergrens ' + VLOER_BEGROTING + ')');
  ok(bron.words.length > 2000,
    'en alle woordenbakken doen mee: ' + bron.words.length + ' kaarten (WORDS alleen zijn er ruim vierhonderd)');

  console.log('\n-- 2. het leesboek --');
  const perReeks = {};
  let totB = 0, totG = 0;
  const laag = [];
  (bron.book || []).forEach(function (h) {
    const d = L.dekking(h.tekst || '', budget);
    const r = String(h.id || '').split('-')[0];
    if (!perReeks[r]) perReeks[r] = { n: 0, b: 0, g: 0 };
    perReeks[r].n++; perReeks[r].b += d.bekend; perReeks[r].g += d.geteld;
    totB += d.bekend; totG += d.geteld;
    if (d.pct < VLOER_HOOFDSTUK) laag.push(h.id + ' ' + d.pct.toFixed(1) + '%');
  });
  Object.keys(perReeks).forEach(function (r) {
    const p = 100 * perReeks[r].b / perReeks[r].g;
    console.log('   ' + r.padEnd(6) + perReeks[r].n + ' hoofdstukken · ' + p.toFixed(1) + '%');
    ok(p >= VLOER_REEKS, '  ' + r + ' zit boven de ' + VLOER_REEKS + ' procent (' + p.toFixed(1) + ')');
  });
  ok(laag.length === 0, 'geen enkel hoofdstuk onder de ' + VLOER_HOOFDSTUK + ' procent (' + (laag.join(', ') || 'geen') + ')');
  const boek = 100 * totB / totG;
  ok(boek >= VLOER_BOEK, 'het hele boek zit boven de ' + VLOER_BOEK + ' procent (' + boek.toFixed(1) + ')');

  console.log('\n-- 3. de luisterscenes --');
  let aB = 0, aG = 0, aN = 0;
  (bron.audiciones || []).forEach(function (sc) {
    const t = (sc.regels || sc.lineas || []).map(function (r) { return r.es || r.texto || r; }).join(' ');
    const d = L.dekking(t, budget);
    aN++; aB += d.bekend; aG += d.geteld;
  });
  const luister = aG ? 100 * aB / aG : 0;
  console.log('   ' + aN + ' scenes · ' + luister.toFixed(1) + '%');
  ok(luister >= VLOER_LUISTER, 'de luisterscenes zitten boven de ' + VLOER_LUISTER + ' procent (' + luister.toFixed(1) + ')');

  // het controlegeval: met een lege begroting hoort alles te zakken. Zonder deze proef is elke
  // bewering hierboven ook waar als dekking() per ongeluk altijd honderd procent teruggeeft.
  const leeg = L.dekking('El califa vive en la mezquita grande.', new Set());
  ok(leeg.pct === 0, 'CONTROLE: met een lege begroting is de dekking nul (' + leeg.pct + ')');

  // ---- 5. en de leeswoorden komen in de app ook echt langs ----
  console.log('\n-- 4. de leeswoorden in de app --');
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', function (e) { errs.push(e.message); });
  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwLd' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);

  const app = await page.evaluate(() => {
    const ids = (typeof L_WORDS !== 'undefined') ? L_WORDS.map(function (w) { return w.id; }) : [];
    const inWords = WORDS.filter(function (w) { return /^l\d+$/.test(w.id); }).length;
    let toegestaan = 0;
    try {
      const set = {};
      allowedWordIds().forEach(function (i) { set[i] = 1; });
      toegestaan = ids.filter(function (i) { return set[i]; }).length;
    } catch (e) { toegestaan = -1; }
    const verb = (typeof L_VERBOS !== 'undefined') ? L_VERBOS.length : 0;
    return { n: ids.length, inWords: inWords, toegestaan: toegestaan,
             verbos: VERBOS.length, nieuwVerbos: verb,
             speelbaar: (function () {
               try { return Object.keys(rvIndex().perVerb).length; } catch (e) { return -1; }
             })() };
  });
  console.log('   ' + app.n + ' leeswoorden · ' + app.verbos + ' werkwoorden · ' +
    app.speelbaar + ' speelbaar in Rompecabezas');
  ok(app.n > 50, 'de leeswoorden staan in de app (' + app.n + ')');
  ok(app.inWords === app.n, 'en ze zitten bij het laden in WORDS (' + app.inWords + ' van ' + app.n + ')');
  ok(app.toegestaan === app.n,
    'en in allowedWordIds, anders komen ze nooit langs (' + app.toegestaan + ' van ' + app.n + ')');
  ok(app.verbos >= 60, 'VERBOS is gegroeid naar ' + app.verbos + ' werkwoorden');
  ok(app.speelbaar >= 50, 'en Rompecabezas kan er ' + app.speelbaar + ' van gebruiken');

  ok(errs.length === 0, 'geen pagina-fouten: ' + (errs.slice(0, 3).join(' | ') || 'geen'));

  await browser.close();
  console.log(fout ? '\n' + fout + ' GEFAALD' : '\nalles goed');
  process.exit(fout ? 1 : 0);
})().catch(function (e) { console.error(e); process.exit(1); });
