// pw-dag1.js (11 aug, v23.43) — dag 1 van een vreemde.
//
// De aanleiding staat in claude/lancering.md, punt 1: "Dag 1 van een vreemde is te vol. De
// machinerie staat er al (SPEEL_EIS, lessonUnlocked), ze staan alleen ruim afgesteld."
//
// Bij het nameten bleek het erger dan ruim afgesteld: de machinerie stond helemaal uit.
// speelOoitInit() geeft iedereen met iets in S.srs al zijn spellen cadeau (de coulanceregel van
// v19.92: wie al oefende raakt door een update niets kwijt), en het proefscherm zet drie woorden
// in S.srs voordat er een profiel bestaat. Elke vreemde viel dus onder de coulance. Op dag 1 met
// drie geleerde woorden opende Clasificador op indefinido-of-imperfecto en kaatste Crucigrama
// terug met "Leer eerst wat meer woordjes".
//
// Deze suite bewaakt niet de teksten maar de belofte eronder, en die is in een zin te zeggen:
// een tegel staat er alleen als het spel er ook echt uit kan komen. Dat is machinaal te
// controleren, want elk spel heeft zijn eigen ondergrens in zijn eigen bouwer staan, en die
// ondergrens is wat de eis hoort te zijn.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

// De proef echt doorlopen, niet overslaan. Juist het overslaan verbergt de bug: zonder proef
// blijft S.srs leeg en valt niemand onder de coulanceregel.
async function verseBezoeker(page, niveau) {
  await page.goto(U);
  await page.waitForTimeout(700);
  for (let i = 0; i < 3; i++) {
    await page.locator('#proefBox button:visible').first().click();
    await page.waitForTimeout(700);
  }
  // v23.44: na de drie vaste woorden biedt de helling aan om door te gaan naar dertig. Deze suite
  // gaat juist over de vreemde die dat niet doet en met drie woorden op zijn dagscherm belandt, dus
  // hier slaan we hem over. De helling zelf staat in pw-helling.js.
  // Wachten op het scherm en niet op de klok: renderProef tekent pas 850 ms na het laatste antwoord,
  // en een vaste pauze die daar net onder zit maakt van deze suite een dobbelsteen.
  await page.waitForSelector('#lnkHelNee, #btnProefDoor', { timeout: 5000 });
  const nee = page.locator('#lnkHelNee');
  if (await nee.count()) { await nee.click(); await page.waitForTimeout(400); }
  await page.locator('#btnProefDoor').click();
  await page.waitForTimeout(600);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Dag1' + Date.now());
  await page.click('button[data-lvl="' + niveau + '"]');
  await page.click('#btnNewProf');
  await page.waitForTimeout(1400);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
  await page.waitForTimeout(200);
}

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await b.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));

  await verseBezoeker(page, 'A0');

  console.log('\n-- de proef zet de poort niet open --');
  const start = await page.evaluate(() => ({
    woorden: Object.keys(S.srs || {}).length,
    ooit: S.speelOoit,
    alles: !!S.speelAlles,
    klaar: Object.keys(SPEEL_EIS).filter(k => speelKlaar(k))
  }));
  console.log('  woorden ::', start.woorden, '· open ::', start.klaar.join(',') || '(geen)');
  ok(start.woorden === 3, 'de drie proefwoorden zijn verzilverd in het verse profiel');
  ok(start.ooit && Object.keys(start.ooit).length === 0,
    'een vers profiel begint met een lege S.speelOoit, dus de coulanceregel raakt hem niet');
  ok(start.klaar.length === 0,
    'met drie woorden staat geen enkel spel met een eis open (was: alle acht)');

  console.log('\n-- geen knop die niets kan --');
  // De harde ondergrens die elk spel zelf hanteert. Dit is het punt van de hele suite: de eis
  // hoort hetzelfde getal te zijn als waarop de bouwer afslaat, anders belooft de tegel iets
  // wat het spel niet waarmaakt.
  const kanEcht = async () => page.evaluate(() => {
    const r = {};
    try { r.ws = wsWoordPool().length >= 4; } catch (e) { r.ws = false; }
    try { r.mem = memPool().length >= 4; } catch (e) { r.mem = false; }
    try {
      let g = 0;
      for (let t = 0; t < 5; t++) { if (kruisBouw()) g++; }
      r.kruis = g >= 4;
    } catch (e) { r.kruis = false; }
    return r;
  });

  const echt0 = await kanEcht();
  ok(echt0.ws === false && echt0.kruis === false && echt0.mem === false,
    'met drie woorden kan geen van de drie bouwers ook echt iets bouwen');

  console.log('\n-- de dagknoppen bieden alleen speelbare spellen aan --');
  const dag0 = await page.evaluate(() => dagSpelKeuze().map(x => x.v));
  console.log('  dagspellen ::', dag0.join(',') || '(geen)');
  ok(dag0.every((v, i) => dag0.indexOf(v) === i),
    'geen enkel spel staat twee keer op het dagbord');
  ok(await page.evaluate(() => dagSpelKeuze().every(x => speelKlaar(x.v))),
    'elk aangeboden dagspel voldoet aan zijn eigen eis');
  ok(dag0.indexOf('clas') === -1 && dag0.indexOf('kruis') === -1 && dag0.indexOf('corr') === -1,
    'Clasificador, Crucigrama en El Corrector staan niet op het dagbord van dag 1');

  console.log('\n-- na de eerste les komt Memory erbij, en geen van de andere --');
  await page.evaluate(() => {
    allowedWordIds().slice(0, 8).forEach(id => { if (!S.srs[id]) S.srs[id] = { box: 1, due: '2020-01-01', n: 1 }; });
    try { persist(); } catch (e) {}
  });
  const na8 = await page.evaluate(() => ({
    woorden: Object.keys(S.srs).length,
    klaar: Object.keys(SPEEL_EIS).filter(k => speelKlaar(k)),
    dag: dagSpelKeuze().map(x => x.v)
  }));
  const echt8 = await kanEcht();
  console.log('  woorden ::', na8.woorden, '· open ::', na8.klaar.join(',') || '(geen)', '· dag ::', na8.dag.join(','));
  ok(na8.klaar.indexOf('mem') !== -1 && echt8.mem === true,
    'Memory staat open en memPool() haalt zijn eigen ondergrens van 4');
  ok(na8.klaar.indexOf('kruis') === -1,
    'Crucigrama staat nog dicht: de eerste A0-woorden zijn uitdrukkingen en passen niet in een raster');
  ok(na8.dag.every((v, i) => na8.dag.indexOf(v) === i),
    'ook met een korte lijst speelbare spellen staat er niets dubbel op het dagbord');
  ok(na8.dag.indexOf('mem') !== -1,
    'het spel dat wel kan, staat er ook (dit ging mis toen de stap van 2 in zichzelf terugviel)');

  console.log('\n-- de tegel verschijnt precies wanneer de bouwer slaagt --');
  await page.evaluate(() => {
    allowedWordIds().slice(0, 16).forEach(id => { if (!S.srs[id]) S.srs[id] = { box: 1, due: '2020-01-01', n: 1 }; });
    try { persist(); } catch (e) {}
  });
  const na16 = await page.evaluate(() => Object.keys(SPEEL_EIS).filter(k => speelKlaar(k)));
  const echt16 = await kanEcht();
  console.log('  open ::', na16.join(','));
  ok(na16.indexOf('kruis') !== -1 && echt16.kruis === true,
    'Crucigrama staat open zodra kruisBouw() werkelijk slaagt');
  ok(na16.indexOf('ws') !== -1 && echt16.ws === true,
    'de Woordenzoeker staat open zodra zijn vijver groot genoeg is');
  ok(na16.indexOf('clas') === -1,
    'Clasificador blijft dicht: 25 woorden is een niveaudrempel en die haal je hier nog niet');

  console.log('\n-- het slot legt uit waarop het wacht, in de eenheid die het telt --');
  await page.evaluate(() => {
    Object.keys(S.srs).slice(3).forEach(id => delete S.srs[id]);
    try { persist(); } catch (e) {}
    funView = null; show('speeltuin');
  });
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'shot-dag1-speeltuin.png' });
  const tekst = await page.evaluate(() => document.getElementById('funCard').innerText);
  ok(/Crucigrama\s*\n\s*doet mee vanaf 4 woorden die in een raster passen · nu 3/.test(tekst),
    'het kruiswoord telt rasterwoorden en niet geleerde woorden');
  ok(/Memory[^\n]*\n\s*doet mee vanaf 4 geleerde woordjes · nu 3/.test(tekst),
    'Memory telt geleerde woorden, want dat is wat memPool() telt');
  ok(!/vanaf 12 /.test(tekst), 'de oude eis van 12 staat nergens meer');

  console.log('\n-- niemand die al bezig was raakt iets kwijt --');
  const oud = await page.evaluate(() => {
    S.speelOoit = null; S.speelAlles = false; S.txp = 400;
    S.srs = {}; WORDS.slice(0, 3).forEach(w => { S.srs[w.id] = { n: 1, d: 0 }; });
    speelOoitInit();
    return Object.keys(SPEEL_EIS).filter(k => speelKlaar(k)).length;
  });
  ok(oud === Object.keys(await page.evaluate(() => SPEEL_EIS)).length,
    'een bestaande speler houdt al zijn spellen (de coulanceregel van v19.92 blijft staan)');

  console.log('\n-- nieuwsgierigheid blijft onbeperkt --');
  const alles = await page.evaluate(() => {
    S.speelOoit = {}; S.speelAlles = true; S.txp = 0;
    S.srs = {}; WORDS.slice(0, 1).forEach(w => { S.srs[w.id] = { n: 1, d: 0 }; });
    return Object.keys(SPEEL_EIS).filter(k => speelKlaar(k)).length;
  });
  ok(alles === Object.keys(await page.evaluate(() => SPEEL_EIS)).length,
    '"laat ze toch allemaal zien" opent nog steeds alles');

  console.log('\n-- schone console --');
  ok(errs.length === 0, 'geen javascript-fouten onderweg' + (errs.length ? ' :: ' + errs.join(' | ') : ''));

  await b.close();
  console.log(fout === 0 ? '\nPOORT OPEN' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
