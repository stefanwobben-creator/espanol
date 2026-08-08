// Playwright-test voor Letras (7 aug, v22.1). Stefan: "die snelheid game is leuk maar nog wel te
// intensief. ik bedoel iets nog meer casual zoals woordzoeker, iets wat speels en ontspannend is."
// Dit is het tegenovergestelde van Clasificador: geen klok, geen levens, geen game over. Zeven
// letters, een lijstje open plekken met de Nederlandse betekenis erbij, en je stopt wanneer je wilt.
// Wat hier bewaakt wordt: elke puzzel is oplosbaar (elk doelwoord past echt in de letters), er zit
// geen tijdmechaniek in, en het is productieve recall en geen gokwerk.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error' && !/Failed to load resource/.test(msg.text())) errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"]', 'PwLt' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. het woordenboek komt uit eigen materiaal ----
  const wb = await page.evaluate(() => {
    const w = ltWoordenboek();
    const k = Object.keys(w);
    return {
      n: k.length,
      metSpatie: k.filter((x) => /\s/.test(w[x].es)).length,
      metNtilde: k.filter((x) => /ñ/i.test(w[x].es)).length,
      teKort: k.filter((x) => x.length < 3).length,
      voorbeeld: w[k[0]]
    };
  });
  ok(wb.n >= 800, 'het woordenboek is groot genoeg voor variatie (' + wb.n + ' woorden)');

  // ---- 1b. de horizon: alleen de meestgebruikte woorden, en hij groeit mee ----
  // v22.2: "reo" (de gedaagde) kwam uit de frequentielijst, die op ondertitels is gebaseerd en dus
  // vol rechtbanktaal zit. Nu doet alleen de kop van die lijst mee, plus alles wat de app zelf leert.
  const horizon = await page.evaluate(() => {
    const uit = {};
    S.srs = {};
    uit.leeg = ltHorizon();
    for (let i = 0; i < 50; i++) S.srs['x' + i] = { box: 3, due: today() };
    uit.na50 = ltHorizon();
    for (let i = 0; i < 40; i++) S.srs['z' + i] = { box: 1, due: today() };   // doosje 1 telt niet mee
    uit.naZwak = ltHorizon();
    uit.basis = LT_BASIS; uit.perStap = LT_PER_STAP; uit.freq = FREQ.length;
    S.srs = {};
    return uit;
  });
  ok(horizon.leeg === horizon.basis, 'een nieuwe speler begint bij de ' + horizon.basis + ' meestgebruikte woorden');
  ok(horizon.na50 === horizon.basis + 2 * horizon.perStap, 'vijftig vaste woorden schuiven de horizon twee stappen op (' + horizon.na50 + ')');
  ok(horizon.naZwak === horizon.na50, 'woorden in doosje 1 tellen niet mee: het gaat om wat je aantoonbaar kent');
  ok(horizon.basis < horizon.freq, 'er valt dus echt iets af aan het begin (' + horizon.basis + ' van ' + horizon.freq + ')');

  const rechtbank = await page.evaluate(() => {
    S.srs = {};
    const w = ltWoordenboek();
    return { reo: !!w['reo'], carajo: !!w['carajo'], casa: !!w['casa'], agua: !!w['agua'] };
  });
  ok(rechtbank.reo === false, 'rechtbanktaal als "reo" doet niet meer mee op het startniveau');
  ok(rechtbank.casa === true && rechtbank.agua === true, 'gewone woorden als casa en agua wel');

  const groeit = await page.evaluate(() => {
    S.srs = {};
    const klein = Object.keys(ltWoordenboek()).length;
    for (let i = 0; i < 400; i++) S.srs['g' + i] = { box: 3, due: today() };
    const groot = Object.keys(ltWoordenboek()).length;
    S.srs = {};
    return { klein: klein, groot: groot };
  });
  ok(groeit.groot > groeit.klein, 'wie meer woorden vast heeft, speelt met een grotere lijst (' + groeit.klein + ' naar ' + groeit.groot + ')');
  ok(wb.metSpatie === 0, 'geen uitdrukkingen met spaties');
  ok(wb.metNtilde === 0, 'geen woorden met ñ (die verdwijnt bij het platslaan)');
  ok(wb.teKort === 0, 'niets korter dan drie letters');
  ok(!!wb.voorbeeld.nl, 'elk woord heeft een Nederlandse betekenis');

  // ---- 2. elke puzzel is echt oplosbaar ----
  const deals = await page.evaluate(() => {
    const uit = [];
    for (let k = 0; k < 20; k++) {
      const d = ltDeel();
      if (!d) { uit.push(null); continue; }
      const bsig = ltSig(d.basis);
      const passen = d.doelen.every((x) => ltPast(ltSig(x.es), bsig));
      uit.push({ n: d.doelen.length, letters: d.letters.length, passen: passen, basis: d.basis });
    }
    return uit;
  });
  ok(deals.every(Boolean), 'er komt altijd een puzzel uit');
  ok(deals.every((d) => d.passen), 'elk doelwoord past echt in de gegeven letters');
  ok(deals.every((d) => d.n >= 5), 'elke puzzel heeft minstens vijf woorden (min ' + Math.min.apply(null, deals.map((d) => d.n)) + ')');
  ok(deals.every((d) => d.letters === 6 || d.letters === 7), 'zes of zeven letters (' + Array.from(new Set(deals.map((d) => d.letters))).join(',') + ')');

  // ---- 3. geen klok, geen levens ----
  const bron = await page.content();
  const motor = bron.slice(bron.indexOf('LETRAS (v22.1)'), bron.indexOf('function renderFunClasificador'));
  ok(!/setInterval|setTimeout/.test(motor), 'er zit geen enkele timer in het spel');
  // op de mechaniek toetsen, niet op de woorden: de toelichting bovenin noemt "geen levens" juist wel
  ok(!/\.levens|levens--|klaar\s*=\s*true/.test(motor), 'en geen levensteller of eindtoestand');
  const geenTijd = await page.evaluate(() => ltSpel === null || (!('tijd' in ltSpel) && !('levens' in ltSpel)));
  ok(geenTijd === true, 'de speltoestand kent geen tijd en geen levens');

  // ---- 4. een woord vinden vult de regel, een verkeerde reeks doet niets ----
  await page.evaluate(() => { S.speelAlles = true; lesFlow = null; show('speeltuin'); funView = 'letras'; ltSpel = null; renderFun(); });
  await page.waitForTimeout(300);
  ok(await page.locator('.lt-letter').count() >= 6, 'de letters staan op het scherm');
  ok(await page.locator('.lt-rij').count() >= 5, 'en de open plekken met hun betekenis');
  const verborgen = await page.evaluate(() => Array.from(document.querySelectorAll('.lt-rij:not(.gev) .lt-es')).every((e) => /^·+$/.test(e.textContent)));
  ok(verborgen === true, 'een woord dat je nog niet vond staat als puntjes, niet als tekst');

  const vinden = await page.evaluate(() => {
    const doel = ltSpel.doelen[0];
    const plat = ltPlat(doel.es);
    const voorXp = S.xp[today()] || 0;
    // de letters van dat woord aantikken, in volgorde
    ltSpel.gekozen = [];
    plat.split('').forEach((L) => {
      for (let i = 0; i < ltSpel.letters.length; i++) {
        if (ltSpel.letters[i] === L && ltSpel.gekozen.indexOf(i) === -1) { ltSpel.gekozen.push(i); break; }
      }
    });
    ltCheck();
    return { gevonden: !!ltSpel.gevonden[plat], gekozenLeeg: ltSpel.gekozen.length === 0,
             xpErbij: (S.xp[today()] || 0) - voorXp, woord: doel.es };
  });
  ok(vinden.gevonden === true, 'het juiste woord wordt herkend (' + vinden.woord + ')');
  ok(vinden.gekozenLeeg === true, 'en de invoer wordt weer leeggemaakt');
  ok(vinden.xpErbij === 1, 'een gevonden woord levert 1 taco op');

  const onzin = await page.evaluate(() => {
    const voor = Object.keys(ltSpel.gevonden).length;
    ltSpel.gekozen = [0, 1, 2];
    ltCheck();
    return Object.keys(ltSpel.gevonden).length - voor;
  });
  ok(onzin === 0 || onzin === 1, 'een willekeurige reeks vult hoogstens een woord dat er echt in zit');

  // ---- 5. alles gevonden geeft een afsluiting, geen mislukking ----
  const af = await page.evaluate(() => {
    ltNieuw();
    ltSpel.doelen.forEach((d) => { ltSpel.gevonden[ltPlat(d.es)] = 1; });
    renderFunLetras();
    return { rondes: S.ltRondes || 0, knop: !!document.getElementById('btnLtNieuw') };
  });
  ok(af.knop === true, 'er staat een knop voor een nieuwe puzzel');
  await page.waitForTimeout(200);
  ok(await page.locator('.feedback.ok').count() >= 1, 'en een vriendelijke afsluiting');

  // ---- 6. de "wanneer doe je hem morgen"-vraag is weg ----
  const moment = await page.evaluate(() => {
    S.ritme = {};
    return { kaart: samenKaartNu(false).indexOf('momentKaart') !== -1 };
  });
  ok(moment.kaart === false, 'de planningsvraag komt niet meer als kaart terug (v22.1)');
  const feest = await page.evaluate(() => {
    S.ritme = {};
    const h = typeof feestKaart === 'function' ? feestKaart() : (typeof dagFeestHtml === 'function' ? dagFeestHtml() : '');
    return { heeftVraag: /Wanneer doe je hem morgen|When will you do it tomorrow/.test(h), leeg: h === '' };
  });
  ok(feest.leeg === true || feest.heeftVraag === false, 'het feestscherm vraagt niet meer wanneer je hem morgen doet');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
