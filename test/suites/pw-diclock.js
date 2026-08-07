// Playwright-smoketest voor het woordenboek-slot op Chispa-boek-woorden (29 juli, v19.43): Stefans tweede
// bevestigde keuze (via AskUserQuestion) op zijn feedback dat het woordenboek verder uitgebreid kan worden
// - "Lock ze tot je dat hoofdstuk leest" voor Chispa-boek-woorden (w235-w299/b187-b251, tag boek-N), net
// als het boek zelf al doet via boekOntgrendeld(). Test in een echte browser (i.p.v. alleen de node-only
// checks in test.js) dat een nog-vergrendeld boekwoord niet vindbaar is, en na ontgrendeling wél.
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

  await page.fill('input[placeholder="Name"]', 'PwDicLock' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // vers profiel, dus doneLessonCount() is 0 - hoofdstuk 13 (drempel 10, de hoogste) is dus zeker nog niet
  // ontgrendeld. Zoek een woord met tag boek-13 en bewijs dat het onvindbaar is.
  const boek13 = await page.evaluate(() => {
    const w = WORDS.find(x => x.tag === 'boek-13');
    return w ? { id: w.id, es: w.es } : null;
  });
  ok(!!boek13, 'er bestaat minstens 1 woord met tag boek-13 (voorwaarde voor deze test)');

  if (boek13) {
    // v21.6: de kop opent nu het globale zoekveld; het woordenboek zit daar een tik achter.
  await page.evaluate(() => dicModal());
    await page.waitForTimeout(200);
    await page.fill('#dicZoek', boek13.es);
    await page.waitForTimeout(200);
    const rijenVergrendeld = await page.locator('.dicrow[data-dic]').count();
    ok(rijenVergrendeld === 0, 'zoeken op een nog-vergrendeld boek-13-woord ("' + boek13.es + '") levert geen rij op in het woordenboek');

    // hoofdstuk 13 kunstmatig ontgrendelen (zelfde patroon als pw-dicgroup.js/test.js: genoeg fake
    // voltooide lessen zodat doneLessonCount() >= de hoogste drempel, 10)
    await page.evaluate(() => { for (let i = 0; i < 12; i++) { S.lessons['__test_boekunlock_' + i] = { done: true }; } });
    await page.fill('#dicZoek', '');
    await page.waitForTimeout(100);
    await page.fill('#dicZoek', boek13.es);
    await page.waitForTimeout(200);
    const rijenOntgrendeld = await page.locator('.dicrow[data-dic]').count();
    ok(rijenOntgrendeld === 1, 'hetzelfde boek-13-woord verschijnt wél zodra hoofdstuk 13 ontgrendeld is');
  }

  // sanity check: een gewoon (niet-boek-)woord blijft gewoon altijd vindbaar
  await page.fill('#dicZoek', '');
  await page.waitForTimeout(100);
  await page.fill('#dicZoek', 'hola');
  await page.waitForTimeout(200);
  const rijenHola = await page.locator('.dicrow[data-dic]').count();
  ok(rijenHola >= 1, 'een gewoon woord ("hola") blijft altijd gewoon vindbaar in het woordenboek');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
