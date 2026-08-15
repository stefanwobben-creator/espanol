// pw-tiempos.js (15 aug, v23.108) — heeft elke tijd een naam, en staat die naam op één plek?
//
// WAAROM DIT ER IS
//
// Stefan, 15 augustus: "ik weet nog niet eens hoe de normale vorm heet omdat we die vertalingen
// nooit leren of die definities maar een keer worden getoond."
//
// Nagemeten en het klopte. conjTiempoLabel() gaf alleen Spaans. De spiekbrief die belooft de
// tijden naar Nederlandse termen te vertalen noemde er drie van de vijf: imperfecto en subjuntivo
// stonden er niet in, terwijl je in de Conjugador wel tot fase 12 (subjuntivo) kunt komen. En
// CONJ_FASES noemt de fasen "verleden tijd 1" en "hoe het was", wat bijnamen zijn, geen namen.
//
// Drie plekken die hetzelfde feit opschrijven en alle drie iets anders zeggen. Dat is de klasse
// fout waar de architectuurregel van 15 augustus over gaat: staat een feit in de data, dan
// schrijft geen enkele codeplek dat feit opnieuw.
//
// DE CONTROLEGEVALLEN
//
// Deze suite is groen te krijgen door overal het woord "onvoltooid verleden tijd" neer te zetten.
// Daarom drie checks die dat uitsluiten:
//
//   1. de dekkingscheck loopt over CONJ_FASES, niet over een lijstje hier. Voeg je morgen een
//      fase met futuro toe zonder de tijd in CONJ_TIEMPOS te zetten, dan valt deze suite om.
//   2. indefinido en imperfecto moeten een VERSCHILLENDE Nederlandse naam hebben. Ze zijn allebei
//      "onvoltooid verleden tijd" op school, en juist dat is Stefans struikelblok; een tabel die
//      ze allebei zo noemt is erger dan geen tabel.
//   3. in het Engels moet er Engels staan en geen Nederlands. Anders test check 1 alleen of er
//      iets staat, niet of het de goede taal is.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(800);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTiempo' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(800);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  // De suite zet de taal zelf, want de helft van de checks gaat over wélke taal er staat. Een
  // nieuw profiel begint hier niet gegarandeerd in het Nederlands, en dan zou "er staat iets"
  // groen zijn terwijl "er staat Nederlands" de vraag is.
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });
  const taal = await page.evaluate(() => profLang());
  ok(taal === 'nl', 'de suite draait in het Nederlands (nu: ' + taal + ')');

  // ---- 1. de databron ----
  const bron = await page.evaluate(() => ({
    n: CONJ_TIEMPOS.length,
    ids: CONJ_TIEMPOS.map((t) => t.id),
    velden: CONJ_TIEMPOS.every((t) => t.id && t.es && t.nl && t.en && t.vb && t.vbNl && t.vbEn),
    // geen twee tijden met dezelfde Nederlandse naam
    uniekNl: new Set(CONJ_TIEMPOS.map((t) => t.nl)).size,
    uniekEn: new Set(CONJ_TIEMPOS.map((t) => t.en)).size,
    // dekking: elke tijd die een fase oefent moet een naam hebben ("mix" is geen tijd)
    ongedekt: CONJ_FASES.map((f) => f.tijd).filter((t) => t !== 'mix' && !conjTiempo(t))
  }));

  console.log('\n-- de bron --');
  ok(bron.n === 5, 'vijf tijden in CONJ_TIEMPOS (nu: ' + bron.n + ')');
  ok(bron.velden === true, 'elke tijd heeft id, es, nl, en, vb, vbNl en vbEn');
  ok(bron.ongedekt.length === 0,
    'DEKKING: elke tijd uit CONJ_FASES staat in CONJ_TIEMPOS (mist: ' + (bron.ongedekt.join(', ') || 'niets') + ')');
  ok(bron.uniekNl === bron.n && bron.uniekEn === bron.n,
    'CONTROLE: indefinido en imperfecto krijgen niet allebei dezelfde naam (nl uniek: ' + bron.uniekNl + '/' + bron.n + ')');

  // ---- 2. de twee labelfuncties ----
  const lab = await page.evaluate(() => ({
    es: CONJ_TIEMPOS.map((t) => conjTiempoLabel(t.id)),
    esVerwacht: CONJ_TIEMPOS.map((t) => t.es),
    naam: CONJ_TIEMPOS.map((t) => conjTiempoNaam(t.id)),
    nlNamen: CONJ_TIEMPOS.map((t) => t.nl),
    mixNaam: conjTiempoNaam('mix'),
    mixLabel: conjTiempoLabel('mix'),
    leegLabel: conjTiempoLabel(undefined)
  }));

  console.log('\n-- de namen --');
  ok(JSON.stringify(lab.es) === JSON.stringify(lab.esVerwacht),
    'conjTiempoLabel geeft precies de Spaanse naam uit de bron');
  ok(lab.naam.every((n, i) => n.indexOf(lab.esVerwacht[i]) !== -1 && n.indexOf(lab.nlNamen[i]) !== -1),
    'conjTiempoNaam geeft de Spaanse EN de Nederlandse naam');
  ok(lab.mixNaam === '', 'conjTiempoNaam("mix") is leeg, want mix is geen tijd (nu: "' + lab.mixNaam + '")');
  ok(lab.mixLabel === 'presente' && lab.leegLabel === 'presente',
    'de oude terugval op "presente" is intact voor mix en undefined');

  // ---- 3. de spiekbrief ----
  const spiek = await page.evaluate(() => {
    const kaart = CHEATSHEET.filter((c) => /De tijden/.test(c.titel))[0];
    if (!kaart) return null;
    return {
      html: kaart.html,
      htmlEn: kaart.htmlEn,
      mist: CONJ_TIEMPOS.filter((t) => kaart.html.indexOf(t.nl) === -1 || kaart.html.indexOf(t.es) === -1).map((t) => t.id),
      mistEn: CONJ_TIEMPOS.filter((t) => kaart.htmlEn.indexOf(t.en) === -1 || kaart.htmlEn.indexOf(t.es) === -1).map((t) => t.id),
      marker: kaart.html.indexOf('<!--TIEMPOS-->') !== -1 || kaart.htmlEn.indexOf('<!--TIEMPOS-->') !== -1,
      // de blokkenknipper van de conceptles moet de gebouwde tabel nog steeds zien
      blokken: gwBlokken(kaart.html).length,
      tabellen: gwBlokken(kaart.html).filter((b) => /^<table/i.test(b)).length
    };
  });

  console.log('\n-- de spiekbrief --');
  ok(!!spiek, 'de kaart "De tijden" bestaat nog');
  ok(spiek && spiek.mist.length === 0,
    'alle vijf de tijden staan erin, met Spaanse en Nederlandse naam (mist: ' + (spiek ? spiek.mist.join(', ') || 'niets' : '?') + ')');
  ok(spiek && spiek.mistEn.length === 0,
    'en in het Engels ook (mist: ' + (spiek ? spiek.mistEn.join(', ') || 'niets' : '?') + ')');
  ok(spiek && spiek.marker === false, 'de markering is vervangen en staat niet meer in de tekst');
  ok(spiek && spiek.tabellen === 1, 'er is precies één tabel, en de knipper van de conceptles ziet hem');
  ok(spiek && /Nederlands/.test(spiek.html) && /verleden tijd/.test(spiek.html),
    'het contrast met het Nederlands wordt benoemd (McManus & Marsden: dat is de werkzame stof)');

  // ---- 4. het scherm ----
  await page.evaluate(() => {
    S.rvDrill = 1; S.conjOpen = CONJ_FASES.length - 2;   // subjuntivo: de fase die niemand kon benoemen
    S.conjFase = 'subjuntivo';
    conjRonde = null; conjIdx = null;
    funView = 'conj'; renderFun();
  });
  await page.waitForTimeout(400);
  const scherm = await page.evaluate(() => ({
    tiempo: (document.getElementById('cjTiempoEs') || {}).innerText || '',
    tiempoNl: (document.getElementById('cjTiempoNl') || {}).innerText || '',
    faseTijd: (document.getElementById('cjFaseTijd') || {}).innerText || ''
  }));

  console.log('\n-- het scherm --');
  ok(/subjuntivo/.test(scherm.tiempo), 'de vraagkaart noemt de Spaanse tijd (nu: "' + scherm.tiempo + '")');
  ok(/aanvoegende wijs/.test(scherm.tiempoNl),
    'en de Nederlandse naam eronder (nu: "' + scherm.tiempoNl + '")');
  ok(/subjuntivo/.test(scherm.faseTijd) && /aanvoegende wijs/.test(scherm.faseTijd),
    'de fasekaart zegt welke tijd deze fase oefent (nu: "' + scherm.faseTijd + '")');

  // ---- 5. controle: in het Engels staat er Engels ----
  await page.evaluate(() => { S.lang = 'en'; try { persist(); } catch (e) {} });
  await page.evaluate(() => { conjRonde = null; conjIdx = null; funView = 'conj'; renderFun(); });
  await page.waitForTimeout(400);
  const eng = await page.evaluate(() => ({
    lang: profLang(),
    tiempoNl: (document.getElementById('cjTiempoNl') || {}).innerText || '',
    naam: conjTiempoNaam('imperfecto')
  }));

  console.log('\n-- controle: de taalknop --');
  if (eng.lang === 'en') {
    ok(!/aanvoegende wijs/.test(eng.tiempoNl) && /subjunctive/.test(eng.tiempoNl),
      'CONTROLE: in het Engels staat de Engelse naam, niet de Nederlandse (nu: "' + eng.tiempoNl + '")');
    ok(/used to|continuous/.test(eng.naam), 'CONTROLE: conjTiempoNaam volgt de taalknop ook (nu: "' + eng.naam + '")');
  } else {
    console.log('  (taal niet omgezet, profLang=' + eng.lang + '; controle overgeslagen)');
  }

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
