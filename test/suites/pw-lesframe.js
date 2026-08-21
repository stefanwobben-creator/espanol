// pw-lesframe.js (21 aug, v23.155) — heeft je dagles een eigen scherm?
//
// WAAROM DIT ER IS
//
// Stefan, na een echte doorloop: "de flow voelt nog steeds gebroken. Dat doet duolingo echt veel
// beter. (...) Ik weet niet echt wanneer wat gebeurt of waar ik wat kan vinden."
//
// De dagles rende door vijf tabbladen: Woordjes, de Grammatica-tab, Cursus, Lezen/Speeltuin/Música
// en Vertalen. Vijf soorten kop, vijf soorten knoppen, vijf manieren terug. De lesstrook stond
// vijftien keer in de code, elke keer met een eigen inFlow-controle, en op sommige schermen
// helemaal niet. En onderaan bleef de tabbalk staan: vijf knoppen die je uitnodigen om weg te gaan
// terwijl je iets aan het afmaken bent.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE STROOK STAAT ER, BUITEN DE SCHERMEN. Eén element, altijd op dezelfde plek, ongeacht welk
//      blok er draait.
//   2. EN HIJ REIST MEE. Bij elk blok noemt hij hetzelfde stapnummer als de les zelf. Een tweede
//      plek die zijn eigen stap uitrekent is een tweede waarheid.
//   3. HIJ STAAT ER MAAR ÉÉN KEER. De vijftien in-scherm-stroken cijferen zichzelf weg zolang het
//      frame er is. Twee stroken boven elkaar is erger dan geen.
//   4. DE TABBALK IS WEG TIJDENS JE LES. Dit is de grootste verandering en het makkelijkst te
//      breken.
//   5. EN ER IS ÉÉN MANIER TERUG. "pauzeer je les", en je komt terug waar je was.
//   6. NA JE LES IS ALLES WEER NORMAAL. Dit is het controlegeval: een frame dat blijft plakken is
//      erger dan geen frame, want dan is je hele app in les-modus.
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
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwLf' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl'; S.dagen = { count: 5 };

    // ---- 6a. vóór je les: geen frame, wél een tabbalk ----
    lesFlow = null; lesFrameSync();
    uit.vooraf = {
      leeg: document.getElementById('lesFrame').classList.contains('leeg'),
      klasse: document.body.classList.contains('in-les'),
      nav: getComputedStyle(document.getElementById('nav')).display
    };

    // ---- 1, 2, 3, 4. tijdens je les ----
    lesFlowStart();
    const gezien = [];
    for (let i = 0; i < 6; i++) {
      lesFrameSync();
      if (!lesFlow) break;
      const fr = document.getElementById('lesFrame');
      gezien.push({
        stap: lesFlow.stap,
        num: lesFlowStapNum(),
        tot: lesFlowStapTotaal(),
        naam: lesFlowStapNaam(),
        frameTekst: fr.textContent.replace(/\s+/g, ' ').trim(),
        // de strook staat buiten alle tabbladen: geen enkele section mag hem bevatten
        binnenTab: !!document.querySelector('section [id="lesFrame"]'),
        // en de in-scherm-stroken leveren niets meer
        inSchermStroken: document.querySelectorAll('.wrap > section .lesstrook').length,
        banner: lesFlowBannerHtml(),
        nav: getComputedStyle(document.getElementById('nav')).display,
        klasse: document.body.classList.contains('in-les'),
        pauzeKnop: !!document.getElementById('btnLesPauze')
      });
      // door naar het volgende blok
      lesFlow.quizzesTeDoen = [];
      lesFlow.vertalenTeGaan = 0;
      lesFlowVolgendeKern();
    }
    uit.gezien = gezien;

    // ---- 5. één manier terug ----
    lesFlowStart();
    /* Pauzeren op stap 1 met nog niets gedaan is geen hervatten maar opnieuw beginnen, en
       lesFlowHervatKan() zegt dat ook terecht. Dus eerst een blok verder. */
    lesFlow.quizzesTeDoen = [];
    lesFlowVolgendeKern();
    lesFrameSync();
    uit.voorPauze = lesFlow.stap;
    lesFramePauze();
    uit.naPauze = {
      flow: lesFlow,
      bewaard: !!(S.lesFlowNu && S.lesFlowNu.d === today()),
      hervat: (function () { try { return lesFlowHervatKan(); } catch (e) { return false; } })(),
      leeg: document.getElementById('lesFrame').classList.contains('leeg'),
      klasse: document.body.classList.contains('in-les'),
      nav: getComputedStyle(document.getElementById('nav')).display
    };

    // ---- 6b. het controlegeval: na je les is alles weer normaal ----
    lesFlow = null; lesFrameSync();
    uit.achteraf = {
      leeg: document.getElementById('lesFrame').classList.contains('leeg'),
      klasse: document.body.classList.contains('in-les'),
      nav: getComputedStyle(document.getElementById('nav')).display,
      frameTekst: document.getElementById('lesFrame').textContent.trim()
    };
    return uit;
  });

  console.log('\n-- 1 t/m 4. tijdens je les --');
  r.gezien.forEach(function (g) {
    console.log('   ' + g.stap + ': "' + g.frameTekst + '"');
  });
  ok(r.gezien.length >= 3, 'de les heeft meerdere blokken doorlopen (' + r.gezien.length + ')');
  r.gezien.forEach(function (g) {
    ok(!g.binnenTab, 'blok "' + g.stap + '": de strook staat buiten de tabbladen');
    ok(g.frameTekst.indexOf('stap ' + g.num + '/' + g.tot) !== -1,
      'blok "' + g.stap + '": de strook noemt stap ' + g.num + '/' + g.tot);
    ok(g.frameTekst.indexOf(g.naam) !== -1, 'blok "' + g.stap + '": met de naam van het blok (' + g.naam + ')');
    ok(g.banner === '', 'blok "' + g.stap + '": de in-scherm-strook cijfert zichzelf weg');
    ok(g.nav === 'none', 'blok "' + g.stap + '": de tabbalk is weg');
    ok(g.klasse, 'blok "' + g.stap + '": de body staat in les-modus');
    ok(g.pauzeKnop, 'blok "' + g.stap + '": en er staat één manier om te pauzeren');
  });

  console.log('\n-- 5. één manier terug --');
  ok(r.naPauze.flow === null, 'pauzeren stopt de lopende les');
  ok(r.naPauze.bewaard, 'maar bewaart hem, dus je raakt niets kwijt');
  ok(r.naPauze.hervat, 'en je kunt hem hervatten waar je was');
  ok(r.naPauze.nav !== 'none', 'de tabbalk komt meteen terug');
  ok(!r.naPauze.klasse, 'en de les-modus is uit');

  console.log('\n-- 6. het controlegeval: ervoor en erna is alles normaal --');
  ok(r.vooraf.leeg, 'vóór je les staat het frame er niet');
  ok(!r.vooraf.klasse, 'en de body staat niet in les-modus');
  ok(r.vooraf.nav !== 'none', 'en de tabbalk staat er gewoon');
  ok(r.achteraf.leeg && r.achteraf.frameTekst === '', 'na je les is het frame leeg');
  ok(!r.achteraf.klasse, 'de les-modus is uit');
  ok(r.achteraf.nav !== 'none', 'en de tabbalk is terug');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
