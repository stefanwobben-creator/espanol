// Playwright-test voor Escuchar (7 aug, v21.2). Stefan: "luisteren is nog wat anders maar misschien
// moet dat meer gaan over begrip dan de zin nabouwen." Dat klopte, en het was erger dan een gemis:
// dictado schreef compMark("luisteren") weg terwijl je een Spaanse zin foutloos kunt overtikken
// zonder te weten wat er staat. Deze test bewaakt drie dingen: de meting (luisteren komt nu uit
// Escuchar, dictado telt als schrijven), de kwaliteit van de vragen (niet raadbaar zonder audio),
// en het gedrag als de opname er nog niet is.
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
  await page.fill('input[placeholder="Name"]', 'PwEsc' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. de content is compleet en consistent ----
  const vorm = await page.evaluate(() => {
    const fouten = [];
    AUDICIONES.forEach(function (sc) {
      if (!sc.lineas || sc.lineas.length < 3) fouten.push(sc.id + ': te weinig regels');
      if (!sc.vragen || sc.vragen.length < 2) fouten.push(sc.id + ': te weinig vragen');
      sc.lineas.forEach(function (l, i) {
        if (l.v !== 'a' && l.v !== 'b') fouten.push(sc.id + '-' + (i + 1) + ': onbekende spreker');
        if (!l.es) fouten.push(sc.id + '-' + (i + 1) + ': lege regel');
      });
      sc.vragen.forEach(function (v, qi) {
        if (v.opts.length !== 4 || v.optsEn.length !== 4) fouten.push(sc.id + ' q' + qi + ': niet vier opties');
        if (!(v.c >= 0 && v.c < 4)) fouten.push(sc.id + ' q' + qi + ': c wijst nergens heen');
        if (!v.q || !v.qEn || !v.waarom || !v.waaromEn) fouten.push(sc.id + ' q' + qi + ': vertaling of uitleg mist');
        if (new Set(v.opts).size !== 4) fouten.push(sc.id + ' q' + qi + ': dubbele optie');
      });
    });
    return { aantal: AUDICIONES.length, fouten: fouten, themas: AUDICIONES.map(function (s) { return s.tema; }) };
  });
  ok(vorm.aantal >= 6, 'er zijn minstens zes scenes (' + vorm.aantal + ')');
  ok(vorm.fouten.length === 0, 'elke scene is compleet: ' + JSON.stringify(vorm.fouten.slice(0, 3)));
  ok(vorm.themas.indexOf('cultura') !== -1, 'er zit cultuur tussen, niet alleen winkel en restaurant');

  // ---- 2. het juiste antwoord verraadt zichzelf niet door lengte ----
  // Een meerkeuzevraag over audio is verraderlijk makkelijk te raden: het juiste antwoord is vaak
  // langer en specifieker dan de afleiders. Dan meet je algemene ontwikkeling en geen Spaans.
  const scheef = await page.evaluate(() => {
    const uit = [];
    AUDICIONES.forEach(function (sc) {
      sc.vragen.forEach(function (v, qi) {
        ['opts', 'optsEn'].forEach(function (k) {
          const lens = v[k].map(function (o) { return o.length; });
          const eigen = lens[v.c];
          const rest = lens.filter(function (_, i) { return i !== v.c; });
          const langsteRest = Math.max.apply(null, rest);
          if (eigen - langsteRest > 5) uit.push(sc.id + ' q' + qi + ' ' + k);
        });
      });
    });
    return uit;
  });
  ok(scheef.length === 0, 'geen enkel juist antwoord is opvallend langer dan zijn afleiders: ' + JSON.stringify(scheef));

  // ---- 3. de meting klopt: luisteren komt uit Escuchar, dictado is schrijven ----
  const meting = await page.evaluate(() => {
    const c = berekenCompetenties();
    return { bron: c.luisteren.bron, noemer: c.luisteren.noemer, escenas: AUDICIONES.length };
  });
  ok(meting.bron.indexOf('Escuchar') !== -1, 'luistervaardigheid komt uit Escuchar (' + JSON.stringify(meting.bron) + ')');
  ok(meting.noemer === meting.escenas, 'de noemer is het aantal scenes, niet het aantal zinnen (' + meting.noemer + ')');
  const bron = await page.content();
  ok(!/compMark\("luisteren", s\.id\)/.test(bron), 'dictado schrijft geen luisteren meer weg');

  // ---- 4. het scherm: geen transcript voor je geantwoord hebt ----
  await page.evaluate(() => {
    S.speelAlles = true;
    show('speeltuin'); funView = 'audi'; audSc = null; audStop(); renderFun();
  });
  await page.waitForTimeout(400);
  ok(await page.locator('#btnAudSpeel').count() === 1, 'er staat een afspeelknop');
  ok(await page.locator('.audOpt').count() === 4, 'de eerste vraag staat met vier opties op het scherm');
  const verborgen = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.aud-tekst')).every(function (e) { return e.textContent.indexOf('·') === 0; });
  });
  ok(verborgen === true, 'het transcript is nog verborgen: dit is geen leesoefening met geluid');

  // ---- 5. alles goed beantwoorden: transcript aan, luisterbewijs weg als er audio was ----
  const uitslag = await page.evaluate(() => {
    audGeenAudio = false; audGehoord = 2;
    const sc = audSc;
    while (audStap < sc.vragen.length) {
      const v = sc.vragen[audStap];
      audAntwoord(v.c, null);
      audStap++;
    }
    audAfronden();
    return {
      goed: audGoed, van: sc.vragen.length,
      done: !!(S.audDone || {})[sc.id],
      luisteren: !!((S.comp.luisteren || {})[sc.id]),
      herhaald: (S.audLuister || {})[sc.id]
    };
  });
  ok(uitslag.goed === uitslag.van, 'alle vragen goed');
  ok(uitslag.done === true, 'de scene staat als afgerond');
  ok(uitslag.luisteren === true, 'de scene telt als luisterbewijs');
  ok(uitslag.herhaald === 2, 'het aantal keer luisteren is bewaard (' + uitslag.herhaald + ')');

  await page.evaluate(() => { renderFunAudicion(); });
  await page.waitForTimeout(200);
  const zichtbaar = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.aud-tekst')).some(function (e) { return /[a-zA-ZáéíóúñÁ]/.test(e.textContent); });
  });
  ok(zichtbaar === true, 'na afloop staat het transcript er wel');

  // ---- 6. zonder opname: wel oefenen, geen luisterbewijs ----
  const zonder = await page.evaluate(() => {
    audStop(); audNieuw();
    audGeenAudio = true;
    const sc = audSc;
    while (audStap < sc.vragen.length) { audAntwoord(sc.vragen[audStap].c, null); audStap++; }
    audAfronden();
    return { done: !!(S.audDone || {})[sc.id], luisteren: !!((S.comp.luisteren || {})[sc.id]) };
  });
  ok(zonder.done === true, 'zonder opname kun je de scene wel afronden');
  ok(zonder.luisteren === false, 'maar dan telt hij niet als luisterbewijs: je las hem');

  // ---- 7. scenes op niveau ----
  const niveau = await page.evaluate(() => {
    S.audDone = {};
    const plafond = audPlafond();
    const pool = audLijst();
    return { plafond: plafond, pool: pool.length, alle: AUDICIONES.length,
             zwaarste: Math.max.apply(null, AUDICIONES.map(audZwaarte)) };
  });
  ok(niveau.pool >= 2, 'een beginner krijgt minstens twee scenes aangeboden (' + niveau.pool + ')');
  ok(niveau.pool <= niveau.alle, 'en nooit meer dan er zijn');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
