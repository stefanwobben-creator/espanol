// pw-zwak.js (1 sep, v23.226) — wijst de kaart iets aan waar voor jou wat te halen valt?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, bij een schermafbeelding van "Even spelen" met drie tegels: "deze suggesties moeten we
// even kijken of je er eentje toont of iets wat zwakke punt is waar ik nog wat meer kan oefenen."
//
// Er stonden drie spellen, gekozen met dayHash("spel"). Een rotatie op de datum, zonder verband met
// wat je die week fout deed, en zonder een woord over waarom juist die drie.
//
// DE VAL DIE DEZE SUITE VOORAL MOET AFVANGEN
//
// S.errors bewaart alles, en over de hele historie wint "woord" altijd: in Stefans logboek 334
// tegen 130 zinnen, 40 conj en 22 corrector. Dat is blootstelling en geen zwakte. Een teller waarin
// het vaakst geoefende onderdeel per definitie wint, meet de oefening en niet de leerling. Vandaar
// het venster van zeven dagen, en vandaar proef 3: oude fouten mogen niet meetellen.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ÉÉN REGEL, NIET DRIE. En de knop naar alle spelletjes blijft, want de suggestie is een
//      voorstel en geen route.
//   2. HET ZWAKKE PUNT BEPAALT WELKE. Verse conj-fouten leveren de Conjugador op, verse
//      zin-fouten El Corrector. Allebei gebouwd: er worden echte regels in S.errors gezet.
//   3. OUDE FOUTEN TELLEN NIET MEE. Het controlegeval van de val hierboven: honderd fouten van
//      vorige maand horen niets aan te wijzen.
//   4. GEEN FOUTEN, GEEN REDEN. Dan staat er gewoon een spel, en de kop heet weer "Even spelen".
//      Een verzonnen reden is erger dan geen reden.
//   5. DE REDEN STAAT ERBIJ, MET HET GETAL. Zonder getal is het geen diagnose maar een mening.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwZw' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);

  /* Genoeg materiaal, anders vallen de spellen af op hun eigen eis en meet proef 2 de poort in
     plaats van de keuze. S.speelAlles is precies daarvoor: speelKlaar() geeft dan overal true. */
  await page.evaluate(() => {
    S.lang = 'nl';
    S.speelAlles = 1;
    S.lesFlow = S.lesFlow || {}; S.lesFlow[today()] = true;
    try { persist(); } catch (e) {}
  });

  // een dag naspelen: zet fouten van een bepaalde soort neer en teken de kaart opnieuw
  async function metFouten(rijen) {
    return page.evaluate((r) => {
      S.errors = {};
      r.forEach(function (x, i) {
        for (var j = 0; j < x.n; j++) {
          S.errors[x.type + ':proef' + i + '-' + j] =
            { id: 'proef' + i + '-' + j, type: x.type, tag: '', count: 1, laatst: '', dag: x.dag };
        }
      });
      show('lessen', true); renderLessons();
      const kaart = document.getElementById('speelKaart');
      let zwak = null;
      try { zwak = dagZwakPunt(); } catch (e) { zwak = { fout: e.message }; }
      return {
        zwak: zwak,
        rijen: kaart ? kaart.querySelectorAll('[data-speel]').length : -1,
        alle: !!document.getElementById('btnAlleSpellen'),
        kop: kaart ? (kaart.querySelector('.kicker') || {}).textContent || '' : '',
        tekst: kaart ? (kaart.textContent || '').replace(/\s+/g, ' ') : ''
      };
    }, rijen);
  }

  const vandaag = await page.evaluate(() => today());
  const oud = await page.evaluate(() => addDays(today(), -30));

  // ---- 1 en 2. één regel, en het zwakke punt bepaalt welke ----
  console.log('\n-- 1 en 2. één regel, gekozen uit je fouten van deze week --');
  const conj = await metFouten([{ type: 'conj', n: 12, dag: vandaag }, { type: 'woord', n: 3, dag: vandaag }]);
  console.log('   ' + JSON.stringify(conj.zwak) + ' · "' + conj.tekst.slice(0, 90) + '"');
  ok(conj.rijen === 1, 'er staat precies één regel op de kaart (' + conj.rijen + ')');
  ok(conj.alle, 'en de knop naar alle spelletjes staat er nog, want dit is een voorstel');
  ok(conj.zwak && conj.zwak.v === 'conj', 'twaalf conj-fouten wijzen naar de Conjugador (' + (conj.zwak || {}).v + ')');
  ok(conj.zwak && conj.zwak.n === 12, 'met het getal erbij (' + (conj.zwak || {}).n + ')');

  const zin = await metFouten([{ type: 'zin', n: 9, dag: vandaag }, { type: 'conj', n: 2, dag: vandaag }]);
  console.log('   ' + JSON.stringify(zin.zwak));
  ok(zin.zwak && zin.zwak.v === 'corr', 'negen zin-fouten wijzen naar El Corrector (' + (zin.zwak || {}).v + ')');
  /* De tegenmeting: als beide gevallen hetzelfde opleverden, zou proef 2 groen staan omdat de kaart
     altijd hetzelfde toont, en niet omdat hij kiest. */
  ok(conj.zwak.v !== zin.zwak.v, 'CONTROLE: en die twee gevallen leveren echt iets anders op');

  // ---- 3. oude fouten tellen niet mee ----
  console.log('\n-- 3. oude fouten tellen niet mee --');
  const versOud = await metFouten([{ type: 'conj', n: 100, dag: oud }]);
  console.log('   honderd conj-fouten van 30 dagen terug: ' + JSON.stringify(versOud.zwak));
  ok(!versOud.zwak, 'honderd fouten van vorige maand wijzen niets aan');
  ok(versOud.rijen === 1, 'en er staat gewoon een spel (' + versOud.rijen + ' regel)');

  // ---- 4. geen fouten, geen reden ----
  console.log('\n-- 4. geen fouten, geen reden --');
  const leeg = await metFouten([]);
  console.log('   kop: "' + leeg.kop.trim() + '"');
  ok(!leeg.zwak, 'zonder fouten is er geen zwak punt');
  ok(/spelen/i.test(leeg.kop), 'en dan heet de kaart weer "Even spelen" (' + leeg.kop.trim() + ')');
  ok(!/deze week ging het/i.test(leeg.tekst), 'er staat geen verzonnen reden bij');
  ok(leeg.rijen === 1, 'maar er staat wel iets (' + leeg.rijen + ' regel)');

  // ---- 5. de reden staat op het scherm, met het getal ----
  console.log('\n-- 5. de reden staat er, met het getal --');
  console.log('   "' + conj.tekst.slice(0, 110) + '"');
  ok(/oefenen/i.test(conj.kop), 'bij een zwak punt heet de kaart "Even oefenen" (' + conj.kop.trim() + ')');
  ok(/deze week ging het 12 keer mis/i.test(conj.tekst), 'en de reden staat erbij, met het getal');
  ok(/werkwoordsvormen/i.test(conj.tekst), 'in woorden en niet in een code');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
