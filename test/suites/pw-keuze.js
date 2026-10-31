// pw-keuze.js (31 okt, v23.256) — mag je zelf kiezen, en blijft de echte poort dicht?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan: "ik zit bijna al op a2 niveau dus ik moet het nu hebben over werkwoorden, verleden tijd
// enzo (...) nu heb ik gevoel dat ik vastloop en hier doorheen moet breken."
//
// Nagerekend: GC_ORDE telt 31 onderwerpen, GC_VENSTER staat op 3, en indefimperf staat op plek 30.
// Nieuwe onderwerpen gaan strikt op volgorde open, dus dat onderwerp is dit jaar niet te bereiken.
// De echte voorwaarden staan los in GC_VOOR, en dat zijn er vijf; 26 van de 31 onderwerpen hebben
// er geen. Het venster is dus geen pedagogiek maar een rem (v23.234), en een rem mag je loslaten.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. KIEZEN WERKT. Een onderwerp dat alleen op een plek in het venster wacht, gaat open zodra je
//      het kiest, en het komt vooraan in de focus. Zonder dat tweede is de knop een loze knop: het
//      onderwerp staat dan wel open, maar gcFocus() vult op volgorde en plek 30 komt nooit.
//   2. KIEZEN VERBRUIKT GEEN VENSTERPLEK. Anders duwt jouw keuze stilletjes een ander onderwerp
//      dicht, en dan is het geen keuze maar een ruil die je niet gevraagd hebt.
//   3. DE ECHTE POORT BLIJFT DICHT. Een onvervulde voorwaarde uit GC_VOOR wijkt niet, en de
//      vormladder (gcRouteOpen, v23.248) ook niet. Dat is de fout die v23.248 repareerde: de keuze
//      tussen twee verleden tijden oefenen terwijl je de vormen nog niet hebt gehad. Zelf kiezen
//      mag die reparatie niet ongedaan maken.
//   4. TWEE ONDERHANDEN BLIJFT TWEE ONDERHANDEN (GC_FOCUS_N, v23.234).
//   5. DE KAART TELT KLOPPEND. De vier getallen boven de route tellen samen op tot alle onderwerpen.
//   6. DE KNOP STAAT ER OOK ECHT. Niet alleen in de functie maar in het scherm, en alleen bij de
//      onderwerpen die op het venster wachten.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwKz' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- de uitgangstoestand: wat staat er op slot, en waarom ----
  console.log('\n-- 0. de uitgangstoestand --');
  const start = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
    const soort = {};
    GC_ORDE.forEach((id) => { soort[id] = gcSlotSoort(id); });
    const tel = { '': 0, venster: 0, voorwaarde: 0, vormen: 0 };
    Object.keys(soort).forEach((id) => { tel[soort[id]] = (tel[soort[id]] || 0) + 1; });
    return {
      n: GC_ORDE.length, venster: GC_VENSTER, soort: soort, tel: tel,
      indefimperf: soort.indefimperf || '(bestaat niet)',
      eersteVenster: GC_ORDE.filter((id) => soort[id] === 'venster')[0] || null,
      eersteVoorwaarde: GC_ORDE.filter((id) => soort[id] === 'voorwaarde')[0] || null,
      eersteVormen: GC_ORDE.filter((id) => soort[id] === 'vormen')[0] || null
    };
  });
  console.log('  ' + start.n + ' onderwerpen · open ' + start.tel[''] + ' · venster ' + start.tel.venster +
              ' · voorwaarde ' + start.tel.voorwaarde + ' · vormen ' + start.tel.vormen);
  ok(start.tel[''] === start.venster,
     'met een schone lei staan er precies GC_VENSTER onderwerpen open: ' + start.tel[''] + ' van ' + start.venster);
  ok(start.indefimperf !== '', 'indefimperf staat op slot bij een nieuwe leerling (soort: ' + start.indefimperf + ')');
  ok(!!start.eersteVenster, 'er is minstens één onderwerp dat alleen op een plek wacht: ' + start.eersteVenster);

  // ---- 1 en 2. kiezen werkt, en kost geen ander onderwerp zijn plek ----
  console.log('\n-- 1 en 2. kiezen opent, en verbruikt geen vensterplek --');
  const na = await page.evaluate((id) => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
    const voor = GC_ORDE.filter((x) => gcConceptOpen(x));
    gcKiesOnderwerp(id);
    const naLijst = GC_ORDE.filter((x) => gcConceptOpen(x));
    return {
      open: gcConceptOpen(id),
      voor: voor, na: naLijst,
      kwijt: voor.filter((x) => naLijst.indexOf(x) === -1),
      focus: gcFocus(), focusMax: GC_FOCUS_N,
      bewaard: (S.gcKeuze || []).slice()
    };
  }, start.eersteVenster);
  ok(na.open, start.eersteVenster + ' staat open na gcKiesOnderwerp()');
  ok(na.bewaard.indexOf(start.eersteVenster) !== -1, 'de keuze wordt bewaard in S.gcKeuze');
  ok(na.kwijt.length === 0, 'geen enkel onderwerp dat eerst open stond is dicht gegaan (kwijt: ' + (na.kwijt.join(', ') || 'niets') + ')');
  ok(na.na.length === na.voor.length + 1, 'er staat precies één onderwerp meer open: ' + na.voor.length + ' → ' + na.na.length);
  ok(na.focus[0] === start.eersteVenster, 'het gekozen onderwerp staat vooraan in de focus (' + na.focus.join(', ') + ')');
  ok(na.focus.length <= na.focusMax, 'en de focus blijft hoogstens ' + na.focusMax + ' onderwerpen breed');

  // ---- 3. de echte poort blijft dicht ----
  console.log('\n-- 3. een echte voorwaarde wijkt niet --');
  if (start.eersteVoorwaarde) {
    const w = await page.evaluate((id) => {
      S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
      const kiesbaar = gcKiesbaar(id);
      gcKiesOnderwerp(id);
      return { kiesbaar: kiesbaar, open: gcConceptOpen(id), bewaard: (S.gcKeuze || []).slice(), reden: gcSlotReden(id) };
    }, start.eersteVoorwaarde);
    ok(!w.kiesbaar, start.eersteVoorwaarde + ' is niet kiesbaar, want er is een onvervulde voorwaarde');
    ok(!w.open, 'en gcKiesOnderwerp() krijgt hem niet open');
    ok(w.bewaard.length === 0, 'er wordt ook niets bewaard voor een onderwerp dat niet mag');
    ok(/eerst/.test(w.reden), 'de reden noemt de voorwaarde: "' + w.reden + '"');
  } else {
    console.log('  (geen onderwerp met een onvervulde voorwaarde bij een schone lei; overgeslagen)');
  }

  console.log('\n-- 3b. de vormladder wijkt ook niet (v23.248 blijft gerepareerd) --');
  if (start.eersteVormen) {
    const v = await page.evaluate((id) => {
      S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
      gcKiesOnderwerp(id);
      return { kiesbaar: gcKiesbaar(id), open: gcConceptOpen(id) };
    }, start.eersteVormen);
    ok(!v.kiesbaar, start.eersteVormen + ' is niet kiesbaar zolang de vormladder dicht staat');
    ok(!v.open, 'en gcKiesOnderwerp() krijgt hem niet open');
  } else {
    console.log('  (geen onderwerp met een dichte vormladder bij een schone lei; overgeslagen)');
  }

  // ---- 4. zelfs alles kiezen opent niet meer dan mag ----
  console.log('\n-- 4. alles tegelijk kiezen opent alleen wat mag --');
  const alles = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
    GC_ORDE.forEach((id) => gcKiesOnderwerp(id));
    const open = GC_ORDE.filter((x) => gcConceptOpen(x));
    const dicht = GC_ORDE.filter((x) => !gcConceptOpen(x));
    return { open: open.length, dicht: dicht, soorten: dicht.map((id) => gcSlotSoort(id)) };
  });
  ok(alles.dicht.length > 0, 'er blijven onderwerpen dicht, ook als je alles probeert te kiezen: ' + alles.dicht.join(', '));
  ok(alles.soorten.every((s) => s === 'voorwaarde' || s === 'vormen'),
     'en dat zijn alleen echte poorten, geen venster (' + alles.soorten.join(', ') + ')');

  // ---- 5. de kaart telt kloppend ----
  console.log('\n-- 5. de vier getallen boven de route --');
  const stand = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
    const leeg = gcStand();
    const alle = gcGeordend().map((c) => c.id);
    S.gram[gramSleutel(alle[0], 0)] = { box: 5, due: addDays(today(), 55), goed: 12, fout: 0, bd: today() };
    S.gram[gramSleutel(alle[1], 0)] = { box: 3, due: addDays(today(), 8), goed: 7, fout: 1, bd: today() };
    S.gram[gramSleutel(alle[2], 0)] = { box: 1, due: today(), goed: 2, fout: 1, bd: today() };
    const vol = gcStand();
    return { leeg: leeg, vol: vol, n: GC_ORDE.length, html: gcStandHtml() };
  });
  const somLeeg = stand.leeg.vast + stand.leeg.onderhoud + stand.leeg.bezig + stand.leeg.open;
  const somVol = stand.vol.vast + stand.vol.onderhoud + stand.vol.bezig + stand.vol.open;
  ok(somLeeg === stand.n, 'bij een schone lei tellen de vier getallen op tot ' + stand.n + ' (nu ' + somLeeg + ')');
  ok(stand.leeg.open === stand.n, 'en staan ze allemaal op "nog te gaan"');
  ok(somVol === stand.n, 'na drie onderwerpen tellen ze nog steeds op tot ' + stand.n + ' (nu ' + somVol + ')');
  ok(stand.vol.vast === 1 && stand.vol.onderhoud === 1 && stand.vol.bezig === 1,
     'doos 5 telt als beheerst, doos 3 als onderhoud, doos 1 als bezig (' +
     stand.vol.vast + '/' + stand.vol.onderhoud + '/' + stand.vol.bezig + ')');
  ok(/nog te gaan/.test(stand.html), 'de kaart noemt de vier groepen bij naam');

  // ---- 6. de knop staat in het scherm ----
  console.log('\n-- 6. de knop staat er ook echt --');
  await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = []; S.gcAlles = true;
    try { persist(); } catch (e) {}
    show('spiekbrief');
    try { renderCheat(); } catch (e) {}
  });
  await page.waitForTimeout(400);
  const knoppen = await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll('[data-gckies]'));
    return {
      n: el.length,
      ids: el.map((d) => d.getAttribute('data-gckies')),
      soorten: el.map((d) => gcSlotSoort(d.getAttribute('data-gckies'))),
      sloten: Array.from(document.querySelectorAll('.gcroute')).length
    };
  });
  ok(knoppen.sloten > 0, 'de hele route staat op het scherm (' + knoppen.sloten + ' rijen)');
  ok(knoppen.n > 0, 'er staat minstens één "Nu doen"-knop (' + knoppen.n + ')');
  ok(knoppen.soorten.every((s) => s === 'venster'),
     'en alleen bij onderwerpen die op een plek wachten (' + knoppen.soorten.join(', ') + ')');

  // en hij doet ook iets als je erop drukt
  const gekozen = knoppen.ids[0];
  await page.locator('[data-gckies="' + gekozen + '"]').scrollIntoViewIfNeeded();
  await page.click('[data-gckies="' + gekozen + '"]');
  await page.waitForTimeout(400);
  const naKlik = await page.evaluate((id) => ({
    open: gcConceptOpen(id), focus: gcFocus(), bewaard: (S.gcKeuze || []).slice()
  }), gekozen);
  ok(naKlik.open, 'na een echte klik op de knop staat ' + gekozen + ' open');
  ok(naKlik.focus[0] === gekozen, 'en staat hij vooraan in de focus');

  ok(errs.length === 0, 'geen pagina-fouten: ' + (errs.slice(0, 3).join(' | ') || 'geen'));

  await browser.close();
  console.log(fout ? '\n' + fout + ' GEFAALD' : '\nalles goed');
  process.exit(fout ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
