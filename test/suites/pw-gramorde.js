// pw-gramorde.js (12 aug, v23.53) — de grammatica heeft een volgorde, en die volgorde is een poort.
//
// Stefan, telefoontest 11 aug: "de grammatica cual of que is veel te moeilijk. Je moet met de
// makkelijkste als begonnen, dat is denk ik el of la" en "wat fout is dat ik alles kan doen, dus
// dingen die nog ver boven mijn niveau liggen".
//
// GC_ORDE is een oordeel: welk grammaticaonderwerp makkelijk is, is didactiek en geen meetwaarde.
// Deze suite toetst dat oordeel dus niet. Wat hij wel toetst is de vórm ervan, en die is wel
// machinaal te controleren:
//
//   1. elk concept staat precies een keer in de volgorde, en de volgorde bevat niets anders
//   2. elke voorwaarde bestaat en staat eerder in de rij (dus: geen kringetjes, geen dode wachters)
//   3. op dag 1 staat er iets open, en niet alles
//   4. wie een onderwerp afmaakt, krijgt er een bij; wie een voorwaarde afmaakt, opent zijn opvolger
//   5. de drie plekken die vroeger zelf iets kozen (dagles, tab, Clasificador) volgen dezelfde poort
//
// Punt 1 en 2 zijn de reden dat deze suite bestaat: als iemand later een concept toevoegt en
// vergeet het in GC_ORDE te zetten, valt het stilzwijgend buiten de app. Dan hoort de poort rood
// te gaan en niet de gebruiker het onderwerp nooit meer te zien.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await b.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(500);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Orde' + Date.now());
  await page.click('button[data-lvl="A0"]');
  await page.click('#btnNewProf');
  await page.waitForFunction(() => !!activeProfile(), { timeout: 8000 });
  await page.waitForTimeout(1200);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- de volgorde dekt precies de concepten --');
  const vorm = await page.evaluate(() => {
    const ids = GC_CONCEPTEN.map(c => c.id);
    return {
      n: GC_ORDE.length, nConcept: ids.length,
      mist: ids.filter(i => GC_ORDE.indexOf(i) === -1),
      onbekend: GC_ORDE.filter(i => ids.indexOf(i) === -1),
      dubbel: GC_ORDE.filter((x, i) => GC_ORDE.indexOf(x) !== i)
    };
  });
  console.log('  ' + vorm.nConcept + ' concepten, ' + vorm.n + ' in de volgorde');
  ok(vorm.mist.length === 0, 'geen concept ontbreekt in GC_ORDE (mist: ' + (vorm.mist.join(',') || '-') + ')');
  ok(vorm.onbekend.length === 0, 'GC_ORDE noemt geen id dat niet bestaat (' + (vorm.onbekend.join(',') || '-') + ')');
  ok(vorm.dubbel.length === 0, 'geen id staat twee keer in de volgorde (' + (vorm.dubbel.join(',') || '-') + ')');

  console.log('\n-- elke voorwaarde bestaat en staat eerder --');
  // Een voorwaarde die later in de rij staat is een kringetje in vermomming: het onderwerp wacht op
  // iets dat pas na hem open kan gaan, en gaat dus nooit open.
  const voor = await page.evaluate(() => {
    const ids = GC_CONCEPTEN.map(c => c.id);
    const wiz = (typeof GRAMWIZ !== 'undefined' ? GRAMWIZ : []).map(o => o.id);
    const slecht = [];
    Object.keys(GC_VOOR).forEach(k => {
      if (ids.indexOf(k) === -1 && wiz.indexOf(k) === -1) slecht.push(k + ': bestaat niet als concept of wizard');
      (GC_VOOR[k] || []).forEach(v => {
        if (GC_ORDE.indexOf(v) === -1) { slecht.push(k + ' -> ' + v + ': voorwaarde bestaat niet'); return; }
        if (k === v) { slecht.push(k + ': is zijn eigen voorwaarde'); return; }
        // een wizard staat niet in GC_ORDE; voor die geldt alleen dat de voorwaarde bestaat
        if (GC_ORDE.indexOf(k) !== -1 && GC_ORDE.indexOf(v) >= GC_ORDE.indexOf(k))
          slecht.push(k + ' -> ' + v + ': voorwaarde staat later in de rij');
      });
      if ((GC_VOOR[k] || []).length > 2) slecht.push(k + ': meer dan twee voorwaarden');
    });
    return slecht;
  });
  ok(voor.length === 0, 'GC_VOOR is consistent' + (voor.length ? ' — ' + voor.join(' · ') : ''));

  console.log('\n-- dag 1: iets staat open, niet alles --');
  const d1 = await page.evaluate(() => ({
    open: Object.keys(gcOpenSet()),
    dicht: gcDichtAantal(),
    lijst: gcLijst().length,
    vandaag: gcVandaagLijst().map(c => c.id),
    gramId: lesFlowGramId(),
    cl: clConcepten().map(c => c.id),
    wiz: GRAMWIZ.filter(o => gcConceptOpen(o.id)).map(o => o.id),
    eerste: GC_ORDE[0]
  }));
  console.log('  open ::', d1.open.join(',') + ' · dicht :: ' + d1.dicht + ' · dagles :: ' + d1.gramId);
  ok(d1.open.length > 0, 'er staat op dag 1 minstens een onderwerp open');
  ok(d1.dicht > 0, 'er staat op dag 1 ook iets dicht (was: alle 23 open)');
  ok(d1.open.length <= 3, 'hoogstens GC_VENSTER onderwerpen tegelijk nieuw (' + d1.open.length + ')');
  ok(d1.open.indexOf(d1.eerste) !== -1, 'het eerste onderwerp uit de volgorde staat open');
  ok(d1.lijst === d1.open.length, 'de Grammatica-tab toont precies wat open staat');

  console.log('\n-- de drie kiezers volgen dezelfde poort --');
  ok(d1.vandaag.every(id => d1.open.indexOf(id) !== -1),
    'wat vandaag telt staat open (' + d1.vandaag.join(',') + ')');
  ok(d1.cl.every(id => d1.open.indexOf(id) !== -1),
    "Chispa's Clasificador speelt alleen met open onderwerpen (" + d1.cl.join(',') + ')');
  ok(/^concept-/.test(d1.gramId || '') && d1.open.indexOf(String(d1.gramId).replace(/^concept-/, '')) !== -1,
    'de grammatica-stap van de dagles staat open (' + d1.gramId + ')');
  ok(d1.wiz.length < 5 && d1.wiz.indexOf('subjuntivo') === -1,
    'de diepe lessen volgen de poort: subjuntivo staat dicht (open: ' + d1.wiz.join(',') + ')');

  console.log('\n-- de volgorde is echt de volgorde --');
  // Elk gesloten onderwerp staat achter elk open onderwerp dat nog nooit is aangeraakt. Dit is
  // de eigenschap die "makkelijk eerst" betekent, zonder dat de suite een oordeel velt over welk
  // onderwerp makkelijk is.
  const gesorteerd = await page.evaluate(() => {
    const open = gcOpenSet();
    let laatsteOpen = -1, eersteDicht = 999;
    GC_ORDE.forEach((id, i) => {
      if (open[id]) laatsteOpen = Math.max(laatsteOpen, i);
      else eersteDicht = Math.min(eersteDicht, i);
    });
    // een onderwerp dat op zijn voorganger wacht mag overgeslagen worden, dus laatsteOpen mag
    // hoger zijn dan eersteDicht; wat niet mag is dat de open onderwerpen achteraan de rij staan
    return { laatsteOpen: laatsteOpen, eersteDicht: eersteDicht, venster: GC_VENSTER };
  });
  ok(gesorteerd.laatsteOpen < gesorteerd.venster + 3,
    'de open onderwerpen staan vooraan in de rij (laatste op ' + gesorteerd.laatsteOpen + ')');

  console.log('\n-- wie iets afmaakt, krijgt er iets bij --');
  const na = await page.evaluate(() => {
    const eerste = GC_ORDE[0];
    gramBij(eerste, true);
    try { persist(); } catch (e) {}
    const open = gcOpenSet();
    return {
      eerste: eerste, open: Object.keys(open), dicht: gcDichtAantal(),
      volgende: gcVolgendeOpen(),
      kinderen: Object.keys(GC_VOOR).filter(k => (GC_VOOR[k] || []).indexOf(eerste) !== -1)
        .map(k => ({ id: k, vrij: gcVoorOk(k), open: !!open[k] }))
    };
  });
  console.log('  na ' + na.eerste + ' goed :: ' + na.open.join(','));
  ok(na.open.indexOf(na.eerste) !== -1, 'het afgemaakte onderwerp blijft open (fouten moeten terug kunnen komen)');
  // Vrijkomen is niet hetzelfde als meteen verschijnen: het venster blijft drie breed, dus wie
  // op genero wachtte staat nu in de rij en niet allemaal tegelijk op het scherm. Precies dat
  // onderscheid staat hier, want anders zou de poort bij elke afronding openklappen.
  ok(na.kinderen.every(k => k.vrij),
    'de onderwerpen die op ' + na.eerste + ' wachtten hebben geen blokkade meer (' +
      na.kinderen.map(k => k.id).join(',') + ')');
  ok(na.kinderen.some(k => k.open),
    'en minstens een ervan staat nu ook echt op het scherm (' +
      na.kinderen.filter(k => k.open).map(k => k.id).join(',') + ')');
  ok(na.open.length > d1.open.length, 'er staat meer open dan voorheen (' + d1.open.length + ' → ' + na.open.length + ')');
  ok(na.dicht < d1.dicht, 'er staat minder dicht dan voorheen (' + d1.dicht + ' → ' + na.dicht + ')');

  console.log('\n-- een fout onderwerp blijft bereikbaar, ook buiten het venster --');
  const foutTerug = await page.evaluate(() => {
    const ver = GC_ORDE[GC_ORDE.length - 1];   // het moeilijkste, ver buiten het venster
    gramBij(ver, false);
    try { persist(); } catch (e) {}
    return { ver: ver, open: !!gcOpenSet()[ver], vandaag: gcVandaagLijst().map(c => c.id) };
  });
  ok(foutTerug.open, 'wat je ooit aanraakte blijft open, ook al staat het achteraan (' + foutTerug.ver + ')');
  ok(foutTerug.vandaag.indexOf(foutTerug.ver) !== -1,
    'en het komt vandaag terug (' + foutTerug.vandaag.join(',') + ')');

  console.log('\n-- de tab zegt hoeveel er nog komt --');
  await page.evaluate(() => { show('spiekbrief'); });
  await page.waitForTimeout(500);
  const tekst = await page.evaluate(() => document.body.innerText);
  ok(/komen later|unlock as you get further/.test(tekst),
    'onder de lijst staat hoeveel onderwerpen er nog komen');

  ok(errs.length === 0, 'geen scriptfouten' + (errs.length ? ' :: ' + errs[0] : ''));

  await b.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
