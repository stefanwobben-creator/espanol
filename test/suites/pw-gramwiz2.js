// Playwright-smoketest voor v19.45: de drie nieuwe wizard-onderwerpen (ser vs. estar, por vs. para,
// subjuntivo). Stefan antwoordde "allemaal" op de vraag welk onderwerp hem het meest frustreert, dus
// alle drie zijn gebouwd op dezelfde herbruikbare GRAMWIZ-component. Deze test loopt ser vs. estar
// helemaal door in een echte browser en checkt daarnaast dat de andere twee openen en dat de
// subjuntivo-doorsteek naar de Conjugador werkt.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  // v19.48: nieuwe bezoekers krijgen eerst de leer-eerst-proeverij; die slaan we hier over
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);

  await page.fill('input[placeholder="Name"]', 'PwGramWiz2' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  /* v23.53: de grammatica heeft sinds deze versie een volgorde (GC_ORDE) en die volgorde is een
     poort: op dag 1 staan er drie onderwerpen open en twintig dicht. Deze suite gaat niet over de
     poort maar over de handgeschreven wizards zelf, dus is dit profiel een gevorderde: alles al een keer goed gedaan.
     De poort zelf staat in pw-gramorde.js. */
  await page.evaluate(() => {
    GC_ORDE.forEach((id) => gramBij(id, true));
    try { persist(); } catch (e) {}
  });

  await page.evaluate(() => show('spiekbrief'));
  await page.waitForTimeout(250);

  // ---------- alle drie de nieuwe kaartjes staan er ----------
  for (const id of ['serestar', 'porpara', 'subjuntivo']) {
    ok(await page.locator('#cheat [data-gwstart="' + id + '"]').count() === 1, 'kaartje voor ' + id + ' staat op de Grammatica-tab');
  }

  // ---------- ser vs. estar helemaal doorlopen ----------
  await page.click('#cheat [data-gwstart="serestar"]');
  await page.waitForTimeout(250);
  ok(await page.locator('.gwuitleg').count() === 1, 'ser vs. estar opent in de uitlegfase');
  ok(await page.locator('details.gwdiep').count() === 1, 'de diepgang zit ook hier achter de uitklapper');
  ok(await page.locator('.gw-stapknop').count() === 4, 'de stap-navigatie toont vier stappen');

  const stappen = await page.evaluate(() => gwOnderwerp('serestar').stappen.length);
  let totaalGoed = 0;
  for (let s = 0; s < stappen; s++) {
    await page.click('#gwNaarToets');
    await page.waitForTimeout(200);
    const aantal = await page.evaluate((si) => gwOnderwerp('serestar').stappen[si].vragen.length, s);
    for (let q = 0; q < aantal; q++) {
      const juist = await page.evaluate(() => {
        const o = gwOnderwerp(gwSess.id);
        return o.stappen[gwSess.stap].vragen[gwSess.vraag].g;
      });
      await page.click('.gw-optie[data-gwo="' + juist + '"]');
      await page.waitForTimeout(120);
      totaalGoed++;
      await page.click('#gwVolgende');
      await page.waitForTimeout(120);
    }
    if (s < stappen - 1) {
      await page.click('#gwVolgendeStap');
      await page.waitForTimeout(200);
    }
  }
  ok(totaalGoed === 24, 'alle 24 vragen van ser vs. estar zijn beantwoord (' + totaalGoed + ')');
  ok(await page.evaluate(() => S.gramwiz.serestar.klaar === true), 'ser vs. estar staat op afgerond');
  await page.click('#gwVolgendeStap');
  await page.waitForTimeout(250);
  ok(await page.evaluate(() => gwSess.fase) === 'klaar', 'ser vs. estar eindigt op het slotscherm');
  ok(await page.locator('#gwNaarDrill').count() === 0, 'ser vs. estar heeft geen drill-doorsteek (er is geen Conjugador-tijd voor)');

  // ---------- por vs. para opent ----------
  await page.click('#gwSluit');
  await page.waitForTimeout(250);
  await page.click('#cheat [data-gwstart="porpara"]');
  await page.waitForTimeout(250);
  ok(await page.evaluate(() => gwSess && gwSess.id === 'porpara'), 'por vs. para opent');
  const ppTekst = await page.evaluate(() => document.getElementById('cheat').innerText);
  ok(ppTekst.indexOf('para') !== -1 && ppTekst.indexOf('por') !== -1, 'de uitleg van por vs. para wordt gerenderd');

  // ---------- subjuntivo: openen en doorsteken naar de Conjugador ----------
  await page.click('#gwSluit');
  await page.waitForTimeout(250);
  await page.click('#cheat [data-gwstart="subjuntivo"]');
  await page.waitForTimeout(250);
  ok(await page.evaluate(() => gwSess && gwSess.id === 'subjuntivo'), 'de subjuntivo opent');
  ok(await page.locator('.gw-stapknop').count() === 4, 'de subjuntivo heeft vier stappen');

  // laatste stap forceren zodat het slotscherm met de drill-knop verschijnt
  await page.evaluate(() => { S.gramwiz.subjuntivo = { stap: 3, klaar: false }; gwStart('subjuntivo', 3); });
  await page.waitForTimeout(200);
  await page.click('#gwNaarToets');
  await page.waitForTimeout(200);
  const laatste = await page.evaluate(() => gwOnderwerp('subjuntivo').stappen[3].vragen.length);
  for (let q = 0; q < laatste; q++) {
    const juist = await page.evaluate(() => {
      const o = gwOnderwerp(gwSess.id);
      return o.stappen[gwSess.stap].vragen[gwSess.vraag].g;
    });
    await page.click('.gw-optie[data-gwo="' + juist + '"]');
    await page.waitForTimeout(120);
    await page.click('#gwVolgende');
    await page.waitForTimeout(120);
  }
  // na de laatste vraag van de laatste stap staat het stap-afgerond-scherm klaar; één klik verder
  // komt het slotscherm met de drill-knop
  ok(await page.locator('#gwVolgendeStap').count() === 1, 'na de laatste vraag volgt het stap-afgerond-scherm');
  ok(await page.evaluate(() => S.gramwiz.subjuntivo.klaar === true), 'de subjuntivo staat op afgerond');
  await page.click('#gwVolgendeStap');
  await page.waitForTimeout(250);
  ok(await page.locator('#gwNaarDrill').count() === 1, 'het slotscherm van de subjuntivo biedt de doorsteek naar de Conjugador');
  await page.click('#gwNaarDrill');
  await page.waitForTimeout(400);
  ok(await page.evaluate(() => S.conjTiempo) === 'subjuntivo', 'die knop zet de Conjugador meteen op subjuntivo');
  // v19.68: de tijd is een fase geworden. De wizard zet die fase open én selecteert hem, want een
  // knop die subjuntivo belooft en je op het presente laat landen is een loze belofte.
  const chip = await page.evaluate(() => conjFaseNu().id);
  ok(chip === 'subjuntivo', 'de Conjugador staat op de subjuntivo-fase (' + chip + ')');
  ok(await page.evaluate(() => S.conjOpen >= conjFaseIdx('subjuntivo')), 'en die fase is ontgrendeld, want de app stuurde je er zelf heen');
  const opgave = await page.evaluate(() => ({ t: conjIdx.t, inf: conjIdx.verb.inf, p: conjIdx.p }));
  ok(opgave.t === 'subjuntivo', 'de getrokken opgave is een subjuntivo-opgave (' + opgave.inf + ')');
  const uitTabel = await page.evaluate(() => VERBOS_SUBJ[conjIdx.verb.inf][conjIdx.p]);
  ok(!!uitTabel, 'die opgave heeft een vorm in VERBOS_SUBJ (' + uitTabel + ')');

  const echte = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(echte.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + echte.length + ' gevonden, ' + (errors.length - echte.length) + ' netwerkruis genegeerd)');
  if (echte.length) console.log(echte.join('\n'));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' FAILURES');
  process.exit(fails === 0 ? 0 : 1);
})();
