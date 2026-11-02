// pw-weekles.js (2 nov, v23.266) — de les van de week: drie voorstellen, vier fasen.
//
// WAAROM DEZE SUITE ER IS
//
// Stefan: "kunnen we ook een keer per week een bestaand of nieuw grammatica concept, echt meer een
// volledige les introduceren?" En op de vraag wie kiest: "maandagochtend zelf kiezen uit drie
// voorstellen."
//
// Wat er was, was een microles van drie stappen en vijf vragen, en elke stap vroeg meteen om de
// vorm. De stap die eraan ontbrak staat in VanPatten en Cadierno (1993): wie een vorm eerst alleen
// hoeft te LEZEN en te begrijpen, produceert hem daarna net zo goed als wie meteen gaat produceren,
// en begrijpt hem veel beter.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DRIE VOORSTELLEN, EN ZE VERSCHILLEN. Drie keer het zwakste onderwerp aanbieden is geen keuze.
//   2. DE WEEK IS EEN WEEK. De sleutel is de maandag van deze week, en wat je maandag koos staat er
//      zondag nog; de maandag erna staat er een nieuwe keuze.
//   3. FASE 1 TELT NIET MEE VOOR JE DOOSJES. Het is lezen en oordelen met twee opties, dus vijftig
//      procent gokken. Zou dat meetellen, dan koop je er een doos mee.
//   4. FASE 1 IS GEEN INVULVRAAG. Geen gat in de zin: de vorm staat er al in, goed of fout.
//   5. FASE 3 TELT WEL MEE, EN DOOR ELKAAR. Vragen over dit onderwerp vermengd met onderwerpen die
//      je al kent, elk met hun eigen onderwerp eraan (dezelfde afspraak als de oefensessie).
//   6. EEN GEKOZEN ONDERWERP DAT OP SLOT STOND, GAAT OPEN. Anders kies je een les die daarna niet
//      te doen is.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwWl' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1. de drie voorstellen ----
  console.log('\n-- 1. drie voorstellen, en ze verschillen --');
  const voor = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = []; S.weekles = null;
    // een onderwerp met verse missers, zodat er iets te kiezen valt uit alle drie de hoeken
    const alle = gcGeordend().filter(function (c) { return gcConceptOpen(c.id); });
    const mis = alle[1] || alle[0];
    S.gram[gramSleutel(mis.id, 0)] = { box: 0, due: today(), goed: 1, fout: 3, laatst: today(), bd: '' };
    const v = weekVoorstellen();
    return { v: v, n: WEEK_KEUZES, uniek: new Set(v).size, mis: mis.id,
             soorten: v.map(function (cid) { return gcConceptOpen(cid) ? 'open' : gcSlotSoort(cid); }) };
  });
  console.log('   ' + voor.v.join(' · ') + '   (' + voor.soorten.join(', ') + ')');
  ok(voor.v.length === voor.n, 'er staan ' + voor.n + ' voorstellen (' + voor.v.length + ')');
  ok(voor.uniek === voor.v.length, 'en ze zijn alle drie verschillend');
  ok(voor.v.indexOf(voor.mis) !== -1, 'het onderwerp met verse missers staat erbij (' + voor.mis + ')');
  ok(voor.soorten.some(function (s) { return s === 'venster'; }) || voor.soorten.every(function (s) { return s === 'open'; }),
    'en er is ruimte voor iets nieuws van de route (' + voor.soorten.join(', ') + ')');

  // ---- 2. de week is een week ----
  console.log('\n-- 2. de week loopt van maandag tot maandag --');
  const week = await page.evaluate(() => {
    const echt = window.today;
    function opDag(d) { window.today = function () { return d; }; return weekMaandag(); }
    const ma = opDag('2026-11-02');   // maandag
    const zo = opDag('2026-11-08');   // zondag erna
    const vo = opDag('2026-11-09');   // maandag erop
    // en de keuze blijft binnen de week staan
    window.today = function () { return '2026-11-02'; };
    S.weekles = null;
    weekKies(gcGeordend()[0].id);
    const gekozen = weekStand().cid;
    window.today = function () { return '2026-11-08'; };
    const zondagNog = weekStand().cid;
    window.today = function () { return '2026-11-09'; };
    const nieuweWeek = weekStand().cid;
    window.today = echt;
    return { ma: ma, zo: zo, vo: vo, gekozen: gekozen, zondagNog: zondagNog, nieuweWeek: nieuweWeek };
  });
  ok(week.ma === '2026-11-02' && week.zo === '2026-11-02',
    'maandag en de zondag erna horen bij dezelfde week (' + week.ma + ' / ' + week.zo + ')');
  ok(week.vo === '2026-11-09', 'en de maandag erop is een nieuwe week (' + week.vo + ')');
  ok(week.zondagNog === week.gekozen, 'wat je maandag koos staat er zondag nog (' + week.zondagNog + ')');
  ok(week.nieuweWeek === null, 'en de week erna staat de keuze weer open');

  // ---- 3 en 4. de vier fasen ----
  console.log('\n-- 3. de vier fasen --');
  const les = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = []; S.weekles = null;
    // twee onderwerpen die je al kent, zodat fase 3 iets heeft om doorheen te mengen
    const alle = gcGeordend().filter(function (c) { return gcConceptOpen(c.id); });
    const doel = alle[0];
    alle.slice(1, 3).forEach(function (c) {
      S.gram[gramSleutel(c.id, 0)] = { box: 3, due: addDays(today(), 8), goed: 9, fout: 1, laatst: '', bd: '' };
    });
    const o = gcVernieuw(weekId(doel.id));
    if (!o) return { fout: 'geen les gebouwd' };
    const f1 = o.stappen[0], f3 = o.stappen[o.stappen.length - 1];
    return {
      doel: doel.id, stappen: o.stappen.length, concept: o.concept, week: !!o.week,
      koppen: o.stappen.map(function (s) { return s.kop; }),
      f1n: (f1.vragen || []).length,
      f1cids: (f1.vragen || []).filter(function (q) { return q.cid; }).length,
      f1gaten: (f1.vragen || []).filter(function (q) { return String(q.v).indexOf('___') !== -1; }).length,
      f1opties: (f1.vragen || []).map(function (q) { return q.o.length; }),
      f1goed: (f1.vragen || []).filter(function (q) { return q.g === 0; }).length,
      f3n: (f3.vragen || []).length,
      f3cids: new Set((f3.vragen || []).map(function (q) { return q.cid; })).size,
      f3zonder: (f3.vragen || []).filter(function (q) { return !q.cid; }).length,
      f3volgorde: (f3.vragen || []).map(function (q) { return q.cid === doel.id ? 'x' : 'o'; }).join('')
    };
  });
  ok(!les.fout, 'de les wordt gebouwd' + (les.fout ? ': ' + les.fout : ''));
  console.log('   ' + (les.koppen || []).join(' | '));
  ok(les.stappen === 3, 'drie stappen in de wizard, de vierde fase is een overstap (' + les.stappen + ')');
  ok(les.week === true, 'en hij is als weekles herkenbaar');

  console.log('\n-- 3a. fase 1: lezen en oordelen, en het telt niet mee --');
  ok(les.f1n >= 3, 'er staan ' + les.f1n + ' zinnen in fase 1');
  ok(les.f1cids === 0, 'geen enkele draagt een onderwerp, dus gramAntwoord schrijft niets weg');
  ok(les.f1gaten === 0, 'en er staat geen gat meer in de zin: de vorm is al ingevuld');
  ok(les.f1opties.every(function (n) { return n === 2; }), 'twee opties: klopt of klopt niet');
  ok(les.f1goed > 0 && les.f1goed < les.f1n,
    'en niet alles klopt (' + les.f1goed + ' van de ' + les.f1n + ' zinnen zijn goed)');

  console.log('\n-- 3b. fase 3: door elkaar, en het telt wel mee --');
  ok(les.f3n >= 6, 'er staan ' + les.f3n + ' vragen in fase 3');
  ok(les.f3zonder === 0, 'elke vraag draagt zijn eigen onderwerp');
  ok(les.f3cids >= 2, 'en ze gaan over meer dan één onderwerp (' + les.f3cids + ')');
  ok(/o/.test(les.f3volgorde || ''), 'met de bekende onderwerpen ertussen: ' + les.f3volgorde);
  ok(!/^x+$/.test(les.f3volgorde || ''), 'dus niet eerst alles van het nieuwe onderwerp en dan de rest');
  ok(les.concept === null, 'de les zelf hangt niet aan één concept, want fase 3 is gemengd');

  // ---- 5. het antwoord landt op het goede doosje ----
  console.log('\n-- 4. een antwoord in fase 3 landt op zijn eigen doosje --');
  const schrijft = await page.evaluate(() => {
    S.gram = {}; S.weekles = null;
    const doel = gcGeordend().filter(function (c) { return gcConceptOpen(c.id); })[0];
    const o = gcVernieuw(weekId(doel.id));
    const f1 = o.stappen[0], f3 = o.stappen[o.stappen.length - 1];
    gramAntwoord(o, f1, f1.vragen[0], f1.vragen[0].g);     // fase 1: hoort niets te doen
    const naFase1 = Object.keys(S.gram).length;
    const q = f3.vragen[0];
    gramAntwoord(o, f3, q, q.g);                            // fase 3: hoort wel te landen
    return { naFase1: naFase1, naFase3: Object.keys(S.gram).length, cid: q.cid,
             goed: (gramLees(q.cid).goed || 0) };
  });
  ok(schrijft.naFase1 === 0, 'na een antwoord in fase 1 staat er nog niets in je doosjes (' + schrijft.naFase1 + ')');
  ok(schrijft.naFase3 > 0 && schrijft.goed >= 1,
    'na een antwoord in fase 3 wel, en bij het goede onderwerp (' + schrijft.cid + ')');

  // ---- 6. een gekozen onderwerp dat op slot stond, gaat open ----
  console.log('\n-- 5. kiezen opent het onderwerp --');
  const opent = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = []; S.weekles = null;
    let dicht = null;
    gcGeordend().forEach(function (c) { if (!dicht && gcKiesbaar(c.id)) dicht = c.id; });
    if (!dicht) return { over: true };
    const voor = gcConceptOpen(dicht);
    weekKies(dicht);
    return { over: false, id: dicht, voor: voor, na: gcConceptOpen(dicht), bewaard: (S.gcKeuze || []).slice() };
  });
  if (opent.over) {
    console.log('   (geen onderwerp achter het venster; overgeslagen)');
  } else {
    ok(opent.voor === false, opent.id + ' stond achter het venster');
    ok(opent.na === true, 'en staat open zodra je hem als les van de week kiest');
    ok(opent.bewaard.indexOf(opent.id) !== -1, 'de keuze is ook op de route bewaard');
  }

  // ---- 7. en de kaart staat op het scherm ----
  console.log('\n-- 6. de kaart op de grammaticatab --');
  await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = []; S.weekles = null;
    try { persist(); } catch (e) {}
    show('spiekbrief');
    try { renderCheat(); } catch (e) {}
  });
  await page.waitForTimeout(400);
  const kaart = await page.evaluate(() => ({
    keuzes: document.querySelectorAll('[data-weekkies]').length,
    start: document.querySelectorAll('[data-weekstart]').length,
    tekst: (document.getElementById('cheat') || {}).textContent || ''
  }));
  ok(kaart.keuzes === 3, 'er staan drie voorstellen op het scherm (' + kaart.keuzes + ')');
  ok(kaart.start === 0, 'en nog geen startknop, want je hebt nog niet gekozen');
  ok(/les van de week/i.test(kaart.tekst), 'met een kop die zegt wat het is');

  const gekozen = await page.evaluate(() => document.querySelector('[data-weekkies]').getAttribute('data-weekkies'));
  await page.locator('[data-weekkies="' + gekozen + '"]').scrollIntoViewIfNeeded();
  await page.click('[data-weekkies="' + gekozen + '"]');
  await page.waitForTimeout(400);
  const naKlik = await page.evaluate(() => ({
    cid: weekStand().cid,
    keuzes: document.querySelectorAll('[data-weekkies]').length,
    start: document.querySelectorAll('[data-weekstart]').length,
    anders: !!document.getElementById('weekAnders')
  }));
  ok(naKlik.cid === gekozen, 'een klik kiest het onderwerp (' + naKlik.cid + ')');
  ok(naKlik.keuzes === 0 && naKlik.start === 1, 'de drie voorstellen maken plaats voor één startknop');
  ok(naKlik.anders, 'en je kunt alsnog iets anders kiezen');

  await page.click('[data-weekstart]');
  await page.waitForTimeout(600);
  const gestart = await page.evaluate(() => ({ id: gwSess ? gwSess.id : null, stap: gwSess ? gwSess.stap : -1 }));
  ok(gestart.id === 'week-' + gekozen, 'en de startknop opent de les (' + gestart.id + ')');
  ok(gestart.stap === 0, 'bij fase 1');

  ok(errs.length === 0, 'geen pagina-fouten: ' + (errs.slice(0, 3).join(' | ') || 'geen'));

  await browser.close();
  console.log(fout ? '\n' + fout + ' GEFAALD' : '\nalles goed');
  process.exit(fout ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
