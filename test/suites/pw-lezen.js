// Playwright-smoketest voor de nieuwe Lezen-tab (Chispa-boek in de app, 26 juli): 1) hoofdstuk 1
// is meteen ontgrendeld (drempel 0) en te lezen, 2) begripsvragen beantwoorden geeft tapas/XP net
// als toetsjes, 3) na afronden staan de hoofdstuk-woorden automatisch in de Woordjes-wachtrij,
// 4) een nog vergrendeld hoofdstuk toont de voortgangsdrempel i.p.v. een leesknop.
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

  await page.fill('input[placeholder="Name"]', 'PwLezen' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  let skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  await page.evaluate(() => show('lezen')); // locale-onafhankelijk (nav-taal kan EN/NL/... zijn)
  await page.waitForTimeout(200);

  /* v23.26: het Lezen-scherm begint nu op de boekenplank. Eerst kijken of die klopt, dan Chispa
     openen; de rest van deze suite gaat over de hoofdstukkenlijst en die zit een tik verder. */
  const plank = await page.evaluate(() => {
    const el = document.getElementById('lezenMenu');
    return {
      tekst: (el.innerText || '').replace(/\s+/g, ' '),
      boeken: el.querySelectorAll('button[data-reeks]').length,
      geenHoofdstukken: el.querySelectorAll('button[data-boek]').length
    };
  });
  ok(plank.boeken >= 2, 'de boekenplank toont allebei de boeken (' + plank.boeken + ')');
  ok(plank.geenHoofdstukken === 0, 'en nog geen hoofdstukken: die zitten een tik verder');
  ok(/0%|\d+%/.test(plank.tekst), 'met een percentage erbij hoe ver je in dat boek bent');
  await page.evaluate(() => { document.querySelector('button[data-reeks="chispa"]').click(); });
  await page.waitForTimeout(150);
  ok(await page.locator('#btnPlankTerug').count() === 1, 'in een boek staat een weg terug naar de plank');

  const eersteKaart = await page.evaluate(() => ({
    ontgrendeld1: boekOntgrendeld(BOOK[0]),
    ontgrendeld4: boekOntgrendeld(BOOK[3]),
    doneCount: doneLessonCount()
  }));
  ok(eersteKaart.ontgrendeld1 === true, 'hoofdstuk 1 (drempel 0) is meteen ontgrendeld voor een nieuw profiel');
  ok(eersteKaart.ontgrendeld4 === (eersteKaart.doneCount >= 3), 'hoofdstuk 4 (drempel 3) volgt de eigen-track-lesvoortgang');

  if (!eersteKaart.ontgrendeld4) {
    const menuTekst = await page.locator('#lezenMenu').innerText();
    // locale-onafhankelijk: de "x/drempel"-teller staat er sowieso, ongeacht taal
    ok(menuTekst.indexOf(eersteKaart.doneCount + '/3') !== -1, 'een vergrendeld hoofdstuk toont de voortgangsdrempel (x/3) i.p.v. een leesknop');
    ok(await page.locator('button[data-boek="boek-4"]').count() === 0, 'een vergrendeld hoofdstuk toont geen leesknop');
  }

  // hoofdstuk 1 openen en lezen
  await page.evaluate(() => startBoek(BOOK[0].id));
  await page.waitForTimeout(150);
  const leesTekst = await page.locator('#lezenCard').innerText();
  ok(leesTekst.indexOf('El huevo que no sabía') !== -1, 'de titel van hoofdstuk 1 staat in de leesweergave');
  ok(leesTekst.indexOf('La Costa') !== -1, 'het deel (La Costa) staat in de leesweergave');

  // audio: nog geen voorgegenereerd bestand aanwezig in deze testomgeving, dus dit moet zonder
  // JS-fouten terugvallen op browser-TTS (dictadoSpreekTTS) — zie boekSpreek()
  ok(await page.locator('#btnBoekLuister').count() === 1, 'de leesweergave toont een "Luisteren"-knop');
  await page.click('#btnBoekLuister');
  await page.waitForTimeout(300);
  await page.evaluate(() => boekStop());

  const tapasVoorLezen = await page.evaluate(() => S.tapas || 0);
  const xpVoorLezen = await page.evaluate(() => S.txp || 0);

  await page.click('#btnBoekVragen');
  await page.waitForTimeout(150);

  const nVragen = await page.evaluate(() => BOOK[0].vragen.length);
  for (let i = 0; i < nVragen; i++) {
    const correctIdx = await page.evaluate(() => bState.h.vragen[bState.i].c);
    await page.locator('#lezenCard .opt').nth(correctIdx).click();
    await page.waitForTimeout(80);
    await page.click('#btnBoekNext');
    await page.waitForTimeout(80);
  }

  const reflectieTekst = await page.locator('#lezenCard').innerText();
  ok(await page.locator('#boekReflectieInput').count() === 1, 'na de laatste vraag verschijnt de (vrijblijvende) reflectiestap met een tekstveld');
  ok(reflectieTekst.indexOf(nVragen + ' / ' + nVragen) !== -1, 'de foutloze score wordt getoond vóór de reflectiestap');

  await page.fill('#boekReflectieInput', 'Sí, tengo una canción propia.');
  await page.click('#btnBoekKlaar');
  await page.waitForTimeout(200);

  const naAfloop = await page.evaluate(() => ({
    boekDone: S.boek['boek-1'] && S.boek['boek-1'].done,
    boekScore: S.boek['boek-1'] && S.boek['boek-1'].score,
    boekReflectie: S.boek['boek-1'] && S.boek['boek-1'].reflectie,
    tapas: S.tapas || 0,
    txp: S.txp || 0,
    woordenInQueue: boekWoorden(BOOK[0]).every(function(id){ return allowedWordIds().indexOf(id) !== -1; })
  }));
  ok(naAfloop.boekDone === true, 'hoofdstuk 1 staat na afronden als voltooid gemarkeerd');
  ok(naAfloop.boekScore === nVragen, 'de foutloze score is opgeslagen');
  ok(naAfloop.boekReflectie === 'Sí, tengo una canción propia.', 'de ingevulde reflectie is opgeslagen');
  ok(naAfloop.tapas - tapasVoorLezen === 5, 'eerste keer + foutloos levert 5 tapas op (3 voor het hoofdstuk, 2 voor foutloos), zichtbaar via de echte UI');
  ok(naAfloop.txp - xpVoorLezen === nVragen * 2, 'elke correcte begripsvraag levert 2 XP op, zichtbaar via de echte UI');
  ok(naAfloop.woordenInQueue === true, 'de woordenlijst van hoofdstuk 1 staat na afronden automatisch in de Woordjes-wachtrij (allowedWordIds)');

  // terug naar het menu: hoofdstuk 1 toont nu een vinkje, en de knop wordt "ghost" (herhaal-stijl) i.p.v. "primary"
  await page.waitForTimeout(150);
  const menuNaAfloop = await page.locator('#lezenMenu').innerText();
  ok(menuNaAfloop.indexOf('✓') !== -1, 'het Lezen-menu toont een vinkje bij een voltooid hoofdstuk');
  const knopKlasse = await page.evaluate(() => document.querySelector('button[data-boek="boek-1"]').className);
  ok(knopKlasse.indexOf('ghost') !== -1, 'een voltooid hoofdstuk krijgt de "nog eens"-knopstijl (ghost) i.p.v. de primaire "Lezen"-knop');

  /* De weg terug moet ook echt terug gaan, en niet alleen bestaan. Een knop die niets doet is
     erger dan geen knop, want je hebt hem al aangetikt voordat je het merkt. */
  await page.evaluate(() => { document.getElementById('btnPlankTerug').click(); });
  await page.waitForTimeout(150);
  ok(await page.evaluate(() => document.querySelectorAll('#lezenMenu button[data-reeks]').length) >= 2,
     'de weg terug brengt je op de plank, met de boeken er weer op');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
