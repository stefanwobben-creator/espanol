// v23.9: Rueda, het letterwiel van Letras met het raster van Crucigrama eromheen.
//
// Stefan: "ja of maak hem maar en dan speel ik hem en dan kijk ik of het aanvulling is of vervanging."
// Vandaar dat hij naast Letras staat: vergelijken kan pas als je ze allebei kunt spelen.
//
// De drie verschillen met Letras zijn waar de vergelijking over gaat, en dus wat hier bewaakt wordt:
// er is een raster met betekenissen (dus je produceert uit betekenis, niet uit letterpuzzelen), wat je
// vindt telt mee in je rotatie, en je puzzel blijft staan als je halverwege stopt.
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
  await page.fill('input[placeholder="Name"]', 'PwRu' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. het spel staat er, naast Letras en niet in plaats van ----
  const menu = await page.evaluate(() => {
    // genoeg woorden zodat beide spellen mogen verschijnen (zie SPEEL_EIS)
    WORDS.slice(0, 40).forEach((w) => { S.srs[w.id] = { box: 2, due: today(), n: 2 }; });
    funView = null;
    show('speeltuin', true); renderFun();
    return {
      letras: !!document.getElementById('ftLetras'),
      rueda: !!document.getElementById('ftRueda'),
      inDagspellen: DAGSPELLEN.some((g) => g.v === 'rueda'),
      eis: !!SPEEL_EIS.rueda
    };
  });
  await page.waitForTimeout(200);
  ok(menu.letras && menu.rueda, 'Letras en Rueda staan allebei in de speeltuin, zodat je ze kunt vergelijken');
  ok(menu.inDagspellen, 'Rueda kan ook als dagspel langskomen');
  ok(menu.eis, 'en hij heeft een materiaal-eis, dus hij verschijnt pas als hij iets kan tonen');

  // ---- 2. het raster: je ziet wat je zoekt ----
  const raster = await page.evaluate(() => {
    delete S.rueda; ruedaSpel = null;
    funView = 'rueda'; renderFun();
    const kaart = document.getElementById('funCard');
    const rijen = Array.from(kaart.querySelectorAll('.ruRij'));
    return {
      doelen: ruedaSpel.doelen.length,
      rijen: rijen.length,
      hints: rijen.filter((r) => (r.querySelector('.ruHint') || {}).textContent).length,
      vakjesKlopt: rijen.every((r, i) => r.querySelectorAll('.ruVak').length === ltPlat(ruedaSpel.doelen[i].es).length),
      lettersZichtbaar: rijen.some((r) => (r.querySelector('.ruVak') || {}).textContent),
      wiel: kaart.querySelectorAll('[data-rul]').length
    };
  });
  ok(raster.rijen === raster.doelen && raster.doelen >= 5, 'elk doelwoord heeft een rij: ' + raster.rijen);
  ok(raster.hints === raster.rijen, 'en elke rij toont de betekenis, want daar produceer je uit');
  ok(raster.vakjesKlopt, 'het aantal vakjes klopt met de lengte van het woord');
  ok(raster.lettersZichtbaar === false, 'maar de letters staan er nog niet in: je krijgt het antwoord niet cadeau');
  ok(raster.wiel >= 6, 'onderin staat het wiel met de letters: ' + raster.wiel);

  // ---- 3. een woord invullen vult het raster en telt mee in je rotatie ----
  const raak = await page.evaluate(() => {
    // een doelwoord kiezen dat een leswoord is, want alleen die kan de app volgen
    let doel = null, id = null;
    for (const d of ruedaSpel.doelen) {
      const p = ltPlat(d.es), i = ruedaIdVoor(p);
      if (i) { doel = d; id = i; break; }
    }
    if (!doel) return { geen: true };
    const plat = ltPlat(doel.es);
    S.srs[id] = { box: 1, due: today(), n: 1 };
    const voorBox = S.srs[id].box;
    // het woord letter voor letter uit het wiel tikken
    plat.split('').forEach((L) => {
      for (let i = 0; i < ruedaSpel.letters.length; i++) {
        if (ruedaSpel.letters[i] === L && ruedaSpel.gekozen.indexOf(i) === -1) { ruedaTik(i); return; }
      }
    });
    const rij = Array.from(document.querySelectorAll('#funCard .ruRij')).filter((r) => r.classList.contains('af'));
    return {
      geen: false, plat: plat,
      gevonden: !!ruedaSpel.gevonden[plat],
      afRijen: rij.length,
      letterInVak: rij.length ? (rij[0].querySelector('.ruVak.af') || {}).textContent : '',
      boxOmhoog: S.srs[id].box > voorBox,
      uitSpel: S.srs[id].sp === 1,
      bewaard: (S.rueda.gevonden || []).indexOf(plat) !== -1
    };
  });
  if (raak.geen) {
    console.log('PASS geen leswoord in deze puzzel, niets te toetsen');
  } else {
    ok(raak.gevonden === true, 'het woord uit het wiel tikken vult het in: ' + raak.plat);
    ok(raak.afRijen >= 1 && !!raak.letterInVak, 'en de letters verschijnen in de vakjes');
    ok(raak.boxOmhoog === true, 'een gevonden leswoord schuift een doosje op, net als bij de andere spellen');
    ok(raak.uitSpel === true, 'gemarkeerd als uit een spel, zodat "werkt de app" en "werkt spelen" apart leesbaar blijven');
    ok(raak.bewaard === true, 'en het staat meteen bewaard');
  }

  // ---- 4. halverwege stoppen mag: morgen ligt hij er nog ----
  await page.reload();
  await page.waitForTimeout(700);
  const terug = await page.evaluate(() => {
    const bewaard = S.rueda;
    funView = 'rueda'; show('speeltuin', true); renderFun();
    return {
      basisGelijk: ruedaSpel && ruedaSpel.basis === bewaard.basis,
      gevonden: ruedaSpel ? Object.keys(ruedaSpel.gevonden).length : -1,
      wasGevonden: (bewaard.gevonden || []).length,
      afRijen: document.querySelectorAll('#funCard .ruRij.af').length
    };
  });
  await page.waitForTimeout(200);
  ok(terug.basisGelijk === true, 'na herladen krijg je dezelfde puzzel terug, geen nieuwe');
  ok(terug.gevonden === terug.wasGevonden, 'met wat je al had gevonden er nog in: ' + terug.gevonden);
  ok(terug.afRijen === terug.wasGevonden, 'en dat is ook op het scherm te zien');

  // ---- 5. geen klok, geen levens, geen verliesconditie ----
  const rustig = await page.evaluate(() => {
    const bron = renderFunRueda.toString() + ruedaTik.toString() + ruedaCheck.toString();
    return {
      timer: /setInterval|setTimeout/.test(bron),
      levens: /levens|lives|gameOver|verloren/.test(bron),
      tekst: document.getElementById('funCard').innerText
    };
  });
  ok(rustig.timer === false, 'er zit geen enkele klok in het spel');
  ok(rustig.levens === false, 'en geen levens of verliesconditie');
  ok(/(Geen klok|No clock)/.test(rustig.tekst), 'dat staat er ook gewoon: "geen klok"');

  // ---- 6. een nieuwe puzzel mag, en gooit de oude echt weg ----
  const nieuw = await page.evaluate(() => {
    const oud = ruedaSpel.basis;
    let anders = false;
    for (let i = 0; i < 8 && !anders; i++) { ruedaNieuw(); anders = ruedaSpel.basis !== oud; }
    renderFunRueda();
    return { anders: anders, leeg: Object.keys(ruedaSpel.gevonden).length, opgeslagen: S.rueda.basis === ruedaSpel.basis };
  });
  ok(nieuw.anders === true, 'de knop Nieuwe puzzel geeft een andere basis');
  ok(nieuw.leeg === 0 && nieuw.opgeslagen === true, 'schoon begin, en meteen bewaard');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
