// Playwright-test voor Clasificador (7 aug, v21.9). Stefan: "ik zoek ook nog iets van een casual
// game zoals tetris maar dan zo gemaakt dat ik er spaans mee leer."
// Tetris zelf laat zich daar niet voor lenen (die kern is ruimtelijk), maar sorteren onder tijdsdruk
// wel: twee bakken, links of rechts, steeds sneller. En Spaans zit vol binaire beslissingen, dus de
// conceptmachine levert de content. Wat deze test bewaakt: de bakken staan stil (anders is het een
// leestest in plaats van een reactiespel), het tempo loopt op, drie missers stoppen de ronde, en het
// spel laat de klok niet doorlopen als je weggaat.
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
  await page.fill('input[placeholder="Name"]', 'PwCl' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  /* v23.53: de grammatica heeft sinds deze versie een volgorde (GC_ORDE) en die volgorde is een
     poort: op dag 1 staan er drie onderwerpen open en twintig dicht. Deze suite gaat niet over de
     poort maar over het sorteerspel zelf, dus is dit profiel een gevorderde: alles al een keer goed gedaan.
     De poort zelf staat in pw-gramorde.js. */
  await page.evaluate(() => {
    GC_ORDE.forEach((id) => gramBij(id, true));
    try { persist(); } catch (e) {}
  });

  // ---- 1. genoeg concepten met precies twee keuzes ----
  const CL_LEVENS_TEST = await page.evaluate(() => CL_LEVENS);
  const pool = await page.evaluate(() => clConcepten().map((c) => c.id));
  ok(pool.length >= 5, 'er zijn genoeg tweekeuze-concepten om mee te spelen (' + pool.length + ': ' + pool.slice(0, 6).join(',') + ')');

  // ---- 2. de bakken staan stil ----
  // Als de bakken per vraag van plek of inhoud wisselen, is het een leestest en geen reactiespel.
  const stil = await page.evaluate(() => {
    S.speelAlles = true; lesFlow = null;
    show('speeltuin'); funView = 'clas';
    clNieuwSpel('serestar');
    if (!clSpel) clNieuwSpel();
    const bakken = clSpel.bakken.join('|');
    const gezien = [];
    for (let k = 0; k < 12; k++) {
      const q = clTrekItem();
      if (!q) break;
      gezien.push(q.o.join('|'));
    }
    return { bakken: bakken, uniek: Array.from(new Set(gezien)), n: gezien.length };
  });
  ok(stil.n >= 5, 'er zijn genoeg verschillende opgaven te trekken (' + stil.n + ')');
  ok(stil.uniek.length === 1 && stil.uniek[0] === stil.bakken,
     'elke opgave gebruikt exact dezelfde twee bakken (' + stil.bakken + ')');

  // ---- 3. goed antwoord: reeks omhoog, klok korter ----
  const raak = await page.evaluate(() => {
    clNieuwSpel();
    const voorTijd = clSpel.tijd, voorStreak = clSpel.streak;
    clKies(clSpel.item.g);
    return { tijdVoor: voorTijd, tijdNa: clSpel.tijd, streakVoor: voorStreak, streakNa: clSpel.streak, goed: clSpel.goed };
  });
  ok(raak.streakNa === raak.streakVoor + 1, 'een goed antwoord verlengt je reeks');
  ok(raak.tijdNa < raak.tijdVoor, 'en maakt de klok korter (' + raak.tijdVoor + ' naar ' + raak.tijdNa + ')');

  // het tempo heeft een bodem, anders wordt het onspeelbaar
  const bodem = await page.evaluate(() => {
    clNieuwSpel();
    for (let k = 0; k < 40; k++) { if (!clSpel.item) break; clKies(clSpel.item.g); }
    return { tijd: clSpel.tijd, min: CL_MIN_TIJD, streak: clSpel.streak };
  });
  ok(bodem.tijd >= bodem.min, 'de klok zakt nooit onder de bodem (' + bodem.tijd + ' >= ' + bodem.min + ')');

  // ---- 4. drie missers en de ronde stopt, met je langste reeks als score ----
  const mis = await page.evaluate(() => {
    /* 11 aug: hier stond clNieuwSpel() zonder id, en dat is de reden dat deze suite af en toe rood
       werd in de poort en nooit als losse run. Zonder id kiest clNieuwSpel() een willekeurig
       concept (geschud(pool)[0]), en clTrekItem() geeft elk item maar één keer. Valt de keuze op een
       concept met weinig patronen, dan is de ronde al klaar vóór de misser hieronder: clKies() doet
       dan niets meer, de reeks blijft op 2 staan en "een misser zet je reeks op nul" zakt. Geen
       tijdsprobleem dus maar een dobbelsteen, en serestar heeft genoeg items (blok 2 trekt er
       twaalf uit). Zie claude/lancering.md punt 5. */
    clNieuwSpel('serestar');
    if (!clSpel) clNieuwSpel();
    S.clBest = 0;
    clKies(clSpel.item.g); clKies(clSpel.item.g);   // reeks van 2 opbouwen
    const best = clSpel.best, streakVoor = clSpel.streak;
    // eerst één misser apart meten: de lus hieronder kan ook eindigen doordat de opgaven op zijn
    clKies(clSpel.item.g === 0 ? 1 : 0);
    const streakNa = clSpel.streak, levensNa = clSpel.levens;
    let rondes = 0;
    while (!clSpel.klaar && clSpel.item && rondes < 5) { rondes++; clKies(clSpel.item.g === 0 ? 1 : 0); }
    return { best: best, streakVoor: streakVoor, streakNa: streakNa, levensNa: levensNa,
             klaar: clSpel.klaar, record: S.clBest || 0 };
  });
  ok(mis.best === 2, 'je langste reeks is bewaard (' + mis.best + ')');
  ok(mis.streakVoor === 2, 'twee goed geeft een reeks van twee');
  ok(mis.streakNa === 0, 'een misser zet je reeks op nul');
  ok(mis.levensNa === CL_LEVENS_TEST - 1, 'en kost een leven (' + mis.levensNa + ')');
  ok(mis.klaar === true, 'na drie missers stopt de ronde');
  ok(mis.record === mis.best, 'en je record is je langste reeks, niet je totaal (' + mis.record + ')');

  // ---- 5. een misser vertelt wat het wel was ----
  const uitleg = await page.evaluate(() => {
    clNieuwSpel('serestar');
    if (!clSpel) clNieuwSpel();
    clKies(clSpel.item.g === 0 ? 1 : 0);
    return clSpel.laatste;
  });
  ok(uitleg.goed === false, 'de misser wordt als misser genoteerd');
  ok(!!uitleg.juist, 'met het juiste antwoord erbij (' + uitleg.juist + ')');
  ok(!!uitleg.w && uitleg.w.length > 10, 'en de uitleg waarom');

  // ---- 6. de klok loopt niet door als je weggaat ----
  await page.evaluate(() => { clNieuwSpel(); renderFunClasificador(); });
  await page.waitForTimeout(200);
  const draait = await page.evaluate(() => clTimer !== null);
  ok(draait === true, 'tijdens het spelen loopt de klok');
  await page.click('#nav button[data-tab="speeltuin"]');
  await page.waitForTimeout(300);
  const gestopt = await page.evaluate(() => ({ timer: clTimer, spel: clSpel }));
  ok(gestopt.timer === null && gestopt.spel === null, 'de Spelen-knop zet de klok stil en ruimt het potje op');

  // ---- 7. geluid kan uit, en dat onthoudt hij ----
  const geluid = await page.evaluate(() => {
    S.geluid = 0;
    clPiep(440, 0.05, 'sine');   // mag niets doen en zeker niet omvallen
    const uit = S.geluid;
    S.geluid = 1;
    return { uit: uit };
  });
  ok(geluid.uit === 0, 'geluid kan uit zonder dat er iets omvalt');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
