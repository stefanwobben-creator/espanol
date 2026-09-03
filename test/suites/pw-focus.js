// pw-focus.js (3 sep, v23.234) — dwingt de app af wat het advies was?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan kreeg vier aanbevelingen en antwoordde: "1 en 2 dwing dit meer af. 3 ok. 4 ok."
//
//   advies 1  lees de kaart van de tijden één keer, om de woorden te hebben
//   advies 2  doe minder tegelijk: kies twee onderwerpen en laat de rest liggen
//
// Allebei stonden ze in een chatbericht, en een advies in een chatbericht is geen app-gedrag.
//
// Gemeten in zijn logboek: 25 onderwerpen, 16 op doos 0, 1 of 2, en NUL op doos 3 of 4. Overal een
// beetje, nergens iets af.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. EEN ONGELEZEN TIJD WORDT NIET GEDRILD. Het vormenblok toont eerst de uitleg van zijn eigen
//      tijd. Gebouwd: S.tijdGelezen leeg, dan de les starten.
//   2. EN DAARNA NOOIT MEER. Dit is de grens tussen afdwingen en zeuren: een poort die elke dag
//      terugkomt klik je weg zonder te lezen. Controlegeval bij 1, want "altijd de poort" haalt
//      proef 1 ook.
//   3. OPENKLAPPEN OP DE KAART TELT OOK. De handeling is wat telt, niet de plek.
//   4. DE FOCUS HOUDT ER TWEE VAST, ook als er zestien openstaan. Gebouwd: zestien aangeraakte
//      onderwerpen op doos 0.
//   5. DE FOCUS BLIJFT STAAN. Twee keer vragen geeft hetzelfde antwoord, ook als er ondertussen
//      iets anders zwakker is geworden. Zonder dit draai je rondjes met een kleiner getal.
//   6. EN HIJ WISSELT ZODRA ER IETS AF IS. Doos 3 en het onderwerp verlaat de focus, en het
//      volgende uit de leervolgorde schuift erin. Dit is de proef dat het slot niet kan klemmen.
//   7. DE REGEL STAAT OP HET SCHERM, met wat er moet gebeuren voordat er iets bij komt.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwFo' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {} });
  await page.waitForTimeout(400);

  // ---- 1, 2 en 3. de poort voor het vormenblok ----
  console.log('\n-- 1 t/m 3. een ongelezen tijd wordt niet gedrild --');
  const poort = await page.evaluate(() => {
    function open(rij) {
      funView = 'les';
      lesSpel = null;
      lesStart(rij);
      renderFunLes();
      const el = document.getElementById('funCard');
      const tekst = (el.innerText || '').replace(/\s+/g, ' ');
      return { poort: !!document.getElementById('btnTijdBegrepen'),
               tekst: tekst.slice(0, 90),
               // de oefening zelf herken je aan de stapteller in de kicker
               oefening: !!document.getElementById('lesKicker') };
    }
    const rij = lesRijIds().filter(function (t) { const r = lesRij(t); return r && tijdVan(r.t); })[0];
    const t = lesRij(rij).t;

    S.tijdGelezen = {};
    const eerste = open(rij);
    // "begrepen" indrukken, en dan hoort de oefening er te staan
    if (document.getElementById('btnTijdBegrepen')) document.getElementById('btnTijdBegrepen').click();
    const naKlik = { poort: !!document.getElementById('btnTijdBegrepen'),
                     oefening: !!document.getElementById('lesKicker'),
                     gelezen: !!(S.tijdGelezen || {})[t] };
    const tweede = open(rij);

    // en de kaart: openklappen telt ook
    S.tijdGelezen = {};
    tijdenOpenNu = true; renderCheat();
    const d = document.querySelector('#cheat [data-tijd="' + t + '"]');
    let viaKaart = null;
    if (d) { d.open = true; d.dispatchEvent(new Event('toggle')); viaKaart = !!(S.tijdGelezen || {})[t]; }
    tijdenOpenNu = false;
    const naKaart = open(rij);
    return { t: t, rij: rij, eerste: eerste, naKlik: naKlik, tweede: tweede,
             viaKaart: viaKaart, naKaart: naKaart };
  });
  console.log('   rij "' + poort.rij + '" (tijd ' + poort.t + ')');
  console.log('   eerste keer: "' + poort.eerste.tekst + '"');
  ok(poort.eerste.poort && !poort.eerste.oefening,
    'de eerste keer staat de uitleg er, en de oefening nog niet');
  ok(poort.naKlik.gelezen && !poort.naKlik.poort && poort.naKlik.oefening,
    'na "begrepen" staat de oefening er, en de tijd is als gelezen genoteerd');
  ok(!poort.tweede.poort && poort.tweede.oefening,
    'CONTROLE: de tweede keer is de poort weg, want elke dag opnieuw is zeuren en geen poort');
  ok(poort.viaKaart === true, 'openklappen op de kaart telt ook als gelezen');
  ok(!poort.naKaart.poort,
    'en dan word je in je les niet nog een keer tegengehouden (de handeling telt, niet de plek)');

  // ---- 4 t/m 6. de focus ----
  console.log('\n-- 4 t/m 6. hoogstens twee onderhanden --');
  const focus = await page.evaluate(() => {
    // zestien aangeraakte onderwerpen op doos 0: precies Stefans gemeten toestand
    S.gram = {}; S.gramFocus = null;
    const alle = gcGeordend().map(function (c) { return c.id; });
    alle.slice(0, 16).forEach(function (id) {
      S.gram[id] = { box: 0, due: today(), goed: 5, fout: 5, laatst: addDays(today(), -10) };
    });
    const open = Object.keys(gcOpenSet()).length;
    const een = gcFocus();
    const twee = gcFocus();
    const vandaag = gcVandaagLijst().map(function (c) { return c.id; });

    // nu maakt hij er eentje af: doos 3
    S.gram[een[0]].box = 3;
    S.gram[een[0]].due = addDays(today(), 8);
    const naAf = gcFocus();

    // en het scherm
    show('spiekbrief', true); renderCheat();
    const regel = document.getElementById('gcFocus');
    return { open: open, een: een, twee: twee, vandaag: vandaag, naAf: naAf,
             n: GC_FOCUS_N, klaar: GC_FOCUS_KLAAR,
             regel: regel ? (regel.innerText || '').replace(/\s+/g, ' ') : null };
  });
  console.log('   ' + focus.open + ' onderwerpen open, focus: ' + focus.een.join(' + '));
  console.log('   vandaag: ' + focus.vandaag.join(' + '));
  console.log('   na eentje op doos ' + focus.klaar + ': ' + focus.naAf.join(' + '));
  ok(focus.open >= 16, 'CONTROLE: er staan er echt zestien open, dus er valt iets te beperken (' + focus.open + ')');
  ok(focus.een.length === focus.n, 'de focus houdt er ' + focus.n + ' vast (' + focus.een.join(', ') + ')');
  ok(focus.vandaag.length <= focus.n,
    'en de dagkeuze komt daar niet bovenuit (' + focus.vandaag.length + ')');
  ok(focus.vandaag.every(function (id) { return focus.een.indexOf(id) !== -1; }),
    'wat je vandaag krijgt komt uit de focus en nergens anders vandaan');
  ok(focus.een.join(',') === focus.twee.join(','),
    'twee keer vragen geeft hetzelfde antwoord: de focus wordt bewaard, niet elke keer opnieuw gekozen');
  ok(focus.naAf.indexOf(focus.een[0]) === -1,
    'zodra een onderwerp op doos ' + focus.klaar + ' staat verlaat het de focus (' + focus.een[0] + ' is weg)');
  ok(focus.naAf.length === focus.n && focus.naAf.indexOf(focus.een[1]) !== -1,
    'en er schuift er precies eentje voor in de plaats, dus het slot kan niet klemmen (' + focus.naAf.join(', ') + ')');

  console.log('\n-- 7. de regel staat op het scherm --');
  console.log('   "' + (focus.regel || 'NIET GEVONDEN') + '"');
  ok(!!focus.regel, 'er staat een regel op de Grammatica-tab die zegt waaraan je werkt');
  ok(!!focus.regel && /doos 3/.test(focus.regel),
    'en wat er moet gebeuren voordat er iets bij komt');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
