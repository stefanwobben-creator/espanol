const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });
  let fails = 0;
  function ok(cond, name) { if (cond) console.log('PASS', name); else { fails++; console.log('FAIL', name); } }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  // v19.48: nieuwe bezoekers krijgen eerst de leer-eerst-proeverij; die slaan we hier over
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"]', 'PwLes7' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  await page.evaluate(() => show('spiekbrief'));
  await page.waitForTimeout(300);
  // sinds de A2-content-EN-vertaalronde (26 juli) toont de spiekbrief de Engelse titel (het
  // testprofiel staat op EN) i.p.v. de NL-fallback van eerder.
  const grammText = await page.locator('#cheat').innerText();
  ok(grammText.indexOf('El imperativo (tú): recipes and instructions') !== -1, 'Grammatica-tab toont de imperativo-titel');
  ok(grammText.indexOf("Se impersonal: how something 'gets done'") !== -1, 'Grammatica-tab toont se impersonal-titel');
  ok(grammText.indexOf('Quantities: un poco de') !== -1, 'Grammatica-tab toont hoeveelheden-titel');

  await page.evaluate(() => show('toetsjes')); // v19.47: Toetsjes zit niet meer in de nav
  await page.waitForTimeout(200);
  await page.evaluate(() => startQuiz('q-imperativo'));
  await page.waitForTimeout(200);
  ok(await page.locator('#qCard .opt').count() === 2, 'q-imperativo: eerste vraag toont 2 opties');
  for (let i = 0; i < 8; i++) {
    const correctIdx = await page.evaluate(() => qState.qz.vragen[qState.i].c);
    await page.locator('#qCard .opt').nth(correctIdx).click();
    await page.waitForTimeout(80);
    await page.click('#btnNextQ');
    await page.waitForTimeout(80);
  }
  ok((await page.locator('#qCard').innerText()).indexOf('8 / 8') !== -1, 'q-imperativo: eindscore 8/8');

  await page.evaluate(() => { closeQuiz(); startQuiz('q-seimpersonal'); });
  await page.waitForTimeout(200);
  for (let i = 0; i < 8; i++) {
    const correctIdx = await page.evaluate(() => qState.qz.vragen[qState.i].c);
    await page.locator('#qCard .opt').nth(correctIdx).click();
    await page.waitForTimeout(80);
    await page.click('#btnNextQ');
    await page.waitForTimeout(80);
  }
  ok((await page.locator('#qCard').innerText()).indexOf('8 / 8') !== -1, 'q-seimpersonal: eindscore 8/8');

  const hasNewWord = await page.evaluate(() => WORDS.some((w) => w.id === 'w191' && w.es === 'la sartén'));
  ok(hasNewWord, 'nieuw woord w191 (la sartén) zit in de globale WORDS-lijst');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
