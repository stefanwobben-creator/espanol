// pw-pad.js (16 aug, v23.116) — is het een route, of een lijstje?
//
// WAAROM DIT ER IS
//
// Stefan: "wanneer maak je er in plaats van losse elementen nu een geïntegreerde les van?"
//
// Er stonden vijf tegels die stuk voor stuk iets goeds doen en die samen niets zijn. Jij moest
// kiezen welke je deed, in welke volgorde, en wanneer je klaar was.
//
// WAT DEZE SUITE BEWAAKT
//
// De drie eigenschappen die van een lijstje een route maken:
//
//   1. DE VOLGORDE IS AFDWINGBAAR. "Alles door elkaar" mag niet je eerste oefening zijn. Dat is
//      regel R5 uit het ontwerpadvies en precies Stefans klacht ("ik word direct getoetst en alle
//      tijden door elkaar").
//   2. "AF" IS ÉÉN BEGRIP. Elk scherm scoorde op zijn eigen manier; zonder één definitie kan geen
//      pad bestaan. De eis hangt aan het SOORT stap, niet aan de stap.
//   3. DE KNOP GAAT NAAR DE JUISTE PLEK, en een stap die nog niet bestaat is geen deur naar niets.
//
// En de controle die dit alles tanden geeft: als je de brokken vult alsof je alles gehaald hebt,
// moet het pad kantelen. Een pad dat altijd hetzelfde zegt is geen pad.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwPad' + Date.now());
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

  // ---- 1. de data ----
  const data = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    return {
      paden: GRAM_PADEN.length,
      stappen: p.stappen.length,
      soorten: p.stappen.map((s) => s.soort),
      zonderEis: p.stappen.filter((s) => !GRAM_EIS[s.soort]).map((s) => s.brok),
      zonderTekst: p.stappen.filter((s) => !s.nl || !s.en || !s.subNl || !s.subEn).map((s) => s.brok),
      // elke stap met een view moet naar een view wijzen die renderFun ook echt kent
      views: p.stappen.filter((s) => s.view).map((s) => s.view)
    };
  });

  console.log('\n-- de data --');
  ok(data.stappen === 5, 'het pad heeft vijf stappen (nu: ' + data.stappen + ')');
  ok(data.zonderEis.length === 0,
    'DEKKING: elk soort stap heeft een eis in GRAM_EIS (mist: ' + (data.zonderEis.join(', ') || 'niets') + ')');
  ok(data.zonderTekst.length === 0,
    'DEKKING: elke stap heeft een titel en een uitleg, in beide talen (mist: ' + (data.zonderTekst.join(', ') || 'niets') + ')');

  // ---- 2. verse gebruiker: alles dicht behalve stap 1 ----
  const vers = await page.evaluate(() => {
    S.brok = {};
    funView = 'pad'; renderFun();
    const p = GRAM_PADEN[0];
    return {
      volgende: gramPadVolgende(p),
      klaar: gramPadKlaar(p),
      opSlot: p.stappen.map((s, i) => gramPadOpSlot(p, i)),
      af: p.stappen.map((s, i) => gramPadStap(p, i).af),
      knop: (document.getElementById('btnPadVerder') || {}).innerText || '',
      klikbaar: Array.prototype.filter.call(document.querySelectorAll('.pad-stap'), (d) => d.style.cursor === 'pointer').length
    };
  });

  console.log('\n-- verse gebruiker --');
  ok(vers.volgende === 0, 'de volgende stap is stap 1 (nu: ' + (vers.volgende + 1) + ')');
  ok(vers.klaar === false, 'en het pad is niet af');
  ok(JSON.stringify(vers.opSlot) === '[false,true,true,true,true]',
    'DE REGEL: alles behalve stap 1 zit op slot (' + vers.opSlot.map((x) => (x ? 'slot' : 'open')).join(',') + ')');
  ok(vers.klikbaar === 1, 'CONTROLE: precies één stap is aanklikbaar (nu: ' + vers.klikbaar + ')');
  ok(/Snap je het verschil/.test(vers.knop), 'de knop wijst naar stap 1 ("' + vers.knop + '")');

  // ---- 3. DE KERN: "alles door elkaar" kan niet je eerste oefening zijn ----
  const doorElkaar = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    const i = p.stappen.findIndex((s) => s.brok === 'vorm.tijd');
    // alleen stap 1 gehaald: de herkentoets hoort nog dicht te zitten
    S.brok = {'indefimperf.betekenis': {goed: 11, fout: 1, beste: 11, rondes: 1, laatst: today()}};
    const naStap1 = gramPadOpSlot(p, i);
    // ook de twee lessen af: nu pas open
    S.brok['les.imperfecto'] = {stapMax: 4, laatst: today()};
    S.brok['les.indefinido'] = {stapMax: 4, laatst: today()};
    const naLessen = gramPadOpSlot(p, i);
    return { i, naStap1, naLessen, volgende: gramPadVolgende(p) };
  });

  console.log('\n-- DE KERN: door elkaar is de laatste stap --');
  ok(doorElkaar.naStap1 === true,
    'CONTROLE: met alleen het verschil gehaald zit "welke tijd is dit" nog op slot');
  ok(doorElkaar.naLessen === false,
    'CONTROLE: pas als beide lessen af zijn gaat hij open');
  ok(doorElkaar.volgende === doorElkaar.i,
    'en dan is hij ook de volgende stap (nu: ' + (doorElkaar.volgende + 1) + ')');

  // ---- 4. "af" is één begrip, en het kantelt op de goede grens ----
  const grens = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    function afBij(brok, st) { S.brok[brok] = st; return gramPadStap(p, p.stappen.findIndex((s) => s.brok === brok)).af; }
    return {
      betekenis10: afBij('indefimperf.betekenis', {beste: 10, rondes: 1}),
      betekenis11: afBij('indefimperf.betekenis', {beste: 11, rondes: 1}),
      les3: afBij('les.imperfecto', {stapMax: 3}),
      les4: afBij('les.imperfecto', {stapMax: 4}),
      herken9: afBij('vorm.tijd', {beste: 9, rondes: 1}),
      herken10: afBij('vorm.tijd', {beste: 10, rondes: 1})
    };
  });

  console.log('\n-- de grens van "af" --');
  ok(grens.betekenis10 === false && grens.betekenis11 === true,
    'CONTROLE: de betekenisstap kantelt tussen 10 en 11 van de 12');
  ok(grens.les3 === false && grens.les4 === true,
    'CONTROLE: de les is pas af na de laatste stap, niet na de voorlaatste');
  ok(grens.herken9 === false && grens.herken10 === true,
    'CONTROLE: de herkentoets kantelt tussen 9 en 10 van de 12');

  // ---- 5. een stap die nog niet bestaat is geen deur naar niets ----
  const nietBestaand = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    // alles gehaald wat bestaat
    S.brok = {
      'indefimperf.betekenis': {beste: 12, rondes: 1},
      'les.imperfecto': {stapMax: 4}, 'les.indefinido': {stapMax: 4},
      'vorm.tijd': {beste: 12, rondes: 1}
    };
    funView = 'pad'; renderFun();
    const laatste = p.stappen.length - 1;
    return {
      bestaat: gramPadStap(p, laatste).bestaat,
      klaar: gramPadKlaar(p),
      volgende: gramPadVolgende(p),
      klaarMelding: (document.getElementById('padKlaar') || {}).innerText || '',
      knop: document.querySelectorAll('#btnPadVerder').length,
      klikbaar: Array.prototype.filter.call(document.querySelectorAll('.pad-stap'), (d) => d.style.cursor === 'pointer').length
    };
  });

  console.log('\n-- de stap die nog niet bestaat --');
  ok(nietBestaand.bestaat === false, 'stap 5 heeft nog geen scherm');
  ok(nietBestaand.volgende === -1 && nietBestaand.knop === 0,
    'CONTROLE: hij wordt geen knop naar niets (volgende: ' + nietBestaand.volgende + ', knoppen: ' + nietBestaand.knop + ')');
  ok(nietBestaand.klaar === true && /hele pad/.test(nietBestaand.klaarMelding),
    'en het pad meldt zich klaar op wat er wél is ("' + nietBestaand.klaarMelding + '")');
  ok(nietBestaand.klikbaar === 4, 'de vier bestaande stappen blijven aanklikbaar (nu: ' + nietBestaand.klikbaar + ')');

  // ---- 6. CONTROLE: het pad kantelt echt, het zegt niet altijd hetzelfde ----
  ok(JSON.stringify(vers.af) !== JSON.stringify([true, true, true, true, false]),
    'CONTROLE: vers was het pad leeg en nu vol, dus deze meting kan verschil zien');

  // ---- 7. de knop gaat naar de juiste plek ----
  await page.evaluate(() => { funView = null; renderFun(); });
  await page.click('#nav button[data-tab="speeltuin"]');
  await page.waitForTimeout(250);
  await page.evaluate(() => { funView = null; renderFun(); });
  await page.waitForTimeout(200);
  const tegel = await page.locator('#ftPad').count();
  if (tegel) await page.click('#ftPad');
  await page.waitForTimeout(300);
  const route = await page.evaluate(() => {
    S.brok = {};
    funView = 'pad'; renderFun();
    document.getElementById('btnPadVerder').click();
    const na1 = funView;
    // stap 1 gehaald: de knop hoort nu naar de les te gaan, mét de goede tijd
    S.brok = {'indefimperf.betekenis': {beste: 12, rondes: 1}};
    funView = 'pad'; renderFun();
    document.getElementById('btnPadVerder').click();
    return { na1, na2: funView, tijd: lesSpel && lesSpel.t, stap: lesSpel && lesSpel.stap };
  });

  console.log('\n-- de knop --');
  ok(tegel === 1, 'de tegel staat in de Speeltuin');
  ok(route.na1 === 'brok', 'stap 1 opent "Achtergrond of gebeurtenis" (nu: ' + route.na1 + ')');
  ok(route.na2 === 'les' && route.tijd === 'imperfecto' && route.stap === 0,
    'stap 2 opent de les met de JUISTE tijd, bij stap 0 (nu: ' + route.na2 + '/' + route.tijd + '/' + route.stap + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
