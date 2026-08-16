// pw-gestold.js (16 aug, v23.117) — kun je "gestold" halen op de dag zelf?
//
// WAAROM DIT ER IS
//
// Stefan gebruikte het woord "gestold", en dat is scherper dan "gehaald". Kim & Webb (2022, 98
// effectgroottes, N = 3.411) vonden dat korte intervallen even goed scoren op de DIRECTE toets en
// slechter op de UITGESTELDE. Een app die vandaag afvinkt kan dat verschil niet zien.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE WACHTTIJD IS ECHT. Alles groen op dag 0 mag "gestold" niet opleveren, hoe je het ook
//      probeert. Dit is de hele reden dat deze ronde bestaat.
//   2. DE DATUM SCHUIFT NIET MEE. Nog een ronde doen mag de wachttijd niet opnieuw laten beginnen,
//      anders kun je het stollen eindeloos vooruitschuiven zonder het te merken.
//   3. DE HERTOETS TREKT UIT ALLE WERKWOORDEN, niet uit de fasepool. Gemeten: in het indefinido
//      volgen 13 van de 33 de regel en 20 niet. Een hertoets die alleen de fasepool pakt, meet de
//      makkelijke werkwoorden en maakt "gestold" opnieuw een leugen.
//   4. EN HIJ IS TE HALEN. Een toets die niemand haalt is net zo nutteloos als een die iedereen
//      haalt.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwGes' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  await page.evaluate(() => {
    S.lang = 'nl'; S.speelAlles = true;
    S.conjOpen = CONJ_FASES.length - 1; S.conjFase = CONJ_FASES[CONJ_FASES.length - 1].id;
    try { persist(); } catch (e) {}
  });

  // alles gehaald, vandaag
  const allesGroen = `S.brok = {
    'indefimperf.betekenis': {beste: 12, rondes: 1, laatst: today()},
    'les.imperfecto': {stapMax: 4}, 'les.indefinido': {stapMax: 4},
    'vorm.tijd': {beste: 12, rondes: 1, laatst: today()}
  };`;

  // ---- 1. DE KERN: op de dag zelf kun je niet stollen ----
  const dag0 = await page.evaluate(new Function(allesGroen + `
    const p = GRAM_PADEN[0];
    padGehaaldStempel(p);
    funView = 'pad'; renderFun();
    const i = p.stappen.findIndex((s) => s.soort === 'hertoets');
    return {
      gehaald: padGehaald(p),
      stempel: brokLees(padId(p)).gehaald,
      magHertoets: padMagHertoets(p),
      opSlot: gramPadOpSlot(p, i),
      klaar: gramPadKlaar(p),
      wacht: (document.getElementById('padWacht') || {}).innerText || '',
      teGaan: padDagenTeGaan(p),
      klaarMelding: (document.getElementById('padKlaar') || {}).innerText || '',
      knop: document.querySelectorAll('#btnPadVerder').length
    };
  `));

  console.log('\n-- DE KERN: dag 0, alles groen --');
  ok(dag0.gehaald === true, 'alle stappen zijn gehaald');
  ok(dag0.stempel === (await page.evaluate(() => today())), 'en er staat een datum bij');
  ok(dag0.magHertoets === false,
    'CONTROLE: de hertoets mag NIET op de dag zelf (magHertoets: ' + dag0.magHertoets + ')');
  ok(dag0.opSlot === true, 'CONTROLE: en hij staat op slot in het pad');
  ok(dag0.klaar === false, 'CONTROLE: het pad heet dus niet klaar, ook al is alles groen');
  ok(dag0.teGaan === 3 && /3 dagen/.test(dag0.wacht),
    'het scherm zegt hoeveel dagen nog ("' + dag0.wacht.replace(/\s+/g, ' ') + '")');
  ok(/woorden|lezen|luisteren/.test(await page.evaluate(() => document.getElementById('funCard').innerText)),
    'en het zegt wat je die dagen wél doet');

  // ---- 2. de datum schuift niet mee ----
  const schuift = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    const eerst = brokLees(padId(p)).gehaald;
    // doe alsof je gisteren gehaald had, en haal daarna nog een ronde
    S.brok[padId(p)].gehaald = addDays(today(), -2);
    const gezet = brokLees(padId(p)).gehaald;
    S.brok['vorm.tijd'] = {beste: 12, rondes: 5, laatst: today()};
    padGehaaldStempel(p);
    return { eerst, gezet, na: brokLees(padId(p)).gehaald, teGaan: padDagenTeGaan(p) };
  });

  console.log('\n-- de datum schuift niet mee --');
  ok(schuift.na === schuift.gezet,
    'CONTROLE: nog een ronde doen verzet de datum niet (' + schuift.gezet + ' → ' + schuift.na + ')');
  ok(schuift.teGaan === 1, 'en de resterende dagen tellen mee af (nu: ' + schuift.teGaan + ')');

  // ---- 3. na de wachttijd gaat hij open ----
  const dag3 = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    S.brok[padId(p)].gehaald = addDays(today(), -HERTOETS_WACHT);
    funView = 'pad'; renderFun();
    const i = p.stappen.findIndex((s) => s.soort === 'hertoets');
    return {
      mag: padMagHertoets(p), opSlot: gramPadOpSlot(p, i),
      volgende: gramPadVolgende(p),
      knop: (document.getElementById('btnPadVerder') || {}).innerText || '',
      wacht: document.querySelectorAll('#padWacht').length
    };
  });

  console.log('\n-- na drie dagen --');
  ok(dag3.mag === true && dag3.opSlot === false, 'de hertoets gaat open');
  ok(/Gestold/.test(dag3.knop), 'en de knop wijst ernaar ("' + dag3.knop + '")');
  ok(dag3.wacht === 0, 'de wachtmelding is weg');

  // ---- 4. de opgaven: alle werkwoorden, niet de fasepool ----
  const opgaven = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    // fasepool klein maken: sta helemaal onderaan de Conjugador-ladder
    S.conjOpen = 0; S.conjFase = CONJ_FASES[0].id;
    const faseNu = conjVerbPool('indefinido').length;
    const alle = conjAlleVerbs('indefinido').length;
    let uitFase = 0, buitenFase = 0, soorten = {};
    for (let r = 0; r < 30; r++) {
      hertoetsBouw(p).forEach((q) => {
        soorten[q.soort] = (soorten[q.soort] || 0) + 1;
        if (q.soort !== 'vorm') return;
        if (conjVerbPool(q.t).some((v) => v.inf === q.v.inf)) uitFase++; else buitenFase++;
      });
    }
    return {
      faseNu, alle, uitFase, buitenFase, soorten,
      // en geen werkwoord dat de tijd niet kent (dan zou conjVorm terugvallen op het presente)
      fout: (function () {
        let n = 0;
        for (let r = 0; r < 20; r++) hertoetsBouw(p).forEach((q) => { if (q.soort === 'vorm' && !conjHeeftTijd(q.v, q.t)) n++; });
        return n;
      })(),
      lengte: hertoetsBouw(p).length
    };
  });

  console.log('\n-- de opgaven --');
  ok(opgaven.lengte === 10, 'tien opgaven (nu: ' + opgaven.lengte + ')');
  ok(opgaven.soorten.betekenis > 0 && opgaven.soorten.vorm > 0,
    'gemengd: de regel én de vorm (' + JSON.stringify(opgaven.soorten) + ')');
  ok(opgaven.alle > opgaven.faseNu,
    'CONTROLE: de fasepool is kleiner dan alle werkwoorden (' + opgaven.faseNu + ' tegenover ' + opgaven.alle + ')');
  ok(opgaven.buitenFase > 0,
    'DE REGEL: de hertoets pakt ook werkwoorden buiten je Conjugador-fase (' + opgaven.buitenFase +
    ' van de ' + (opgaven.uitFase + opgaven.buitenFase) + ')');
  ok(opgaven.fout === 0,
    'CONTROLE: nooit een werkwoord dat de tijd niet kent, want dan zou het antwoord uit de verkeerde tijd komen (' + opgaven.fout + ')');

  // ---- 5. de toets is te halen én te zakken ----
  const spelen = await page.evaluate(() => {
    function ronde(alleGoed) {
      const p = GRAM_PADEN[0];
      hertoetsStart(p);
      for (let i = 0; i < hertoetsSpel.rij.length; i++) {
        const q = hertoetsSpel.rij[hertoetsSpel.i];
        const goed = q.soort === 'betekenis' ? q.z.s : conjVorm(q.v, q.p, q.t);
        hertoetsAntwoord(alleGoed ? goed : 'zzzz');
        hertoetsVolgende();
      }
      return hertoetsSpel.goed;
    }
    S.brok[padId(GRAM_PADEN[0])].gestold = null;
    const fout = ronde(false);
    const naFout = !!brokLees(padId(GRAM_PADEN[0])).gestold;
    const goed = ronde(true);
    const naGoed = brokLees(padId(GRAM_PADEN[0])).gestold;
    funView = 'pad'; renderFun();
    return { fout, naFout, goed, naGoed, klaar: gramPadKlaar(GRAM_PADEN[0]),
             melding: (document.getElementById('padKlaar') || {}).innerText || '' };
  });

  console.log('\n-- halen en zakken --');
  ok(spelen.fout === 0 && spelen.naFout === false,
    'CONTROLE: alles fout geeft 0/10 en géén gestold');
  ok(spelen.goed === 10, 'alles goed geeft 10/10 (nu: ' + spelen.goed + ')');
  ok(!!spelen.naGoed, 'en dan wordt gestold gezet, met een datum (' + spelen.naGoed + ')');
  ok(spelen.klaar === true && /Gestold/.test(spelen.melding),
    'pas dan heet het pad klaar ("' + spelen.melding + '")');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
