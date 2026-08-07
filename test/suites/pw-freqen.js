// Playwright-smoketest voor FREQ_EN 1001-2866 (26 juli): de top-2866 frequentiewoorden hadden tot
// nu toe alleen voor de eerste 1000 een Engelse gloss; nu volledig aangevuld. Dit script checkt via
// de echte woordenboek-zoekfunctie (niet alleen via page.evaluate) dat een woord ver voorbij de oude
// top-1000-grens nu ook echt een Engelse gloss toont voor een EN-profiel.
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

  await page.fill('input[placeholder="Name"]', 'PwFreqEn' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  const dataCheck = await page.evaluate(() => ({
    freqLen: FREQ.length,
    freqEnKeys: Object.keys(FREQ_EN).length,
    missing: FREQ.filter(function(p){ return !FREQ_EN[p[0]]; }).length
  }));
  ok(dataCheck.freqLen === 4219, 'FREQ heeft na de v19.52-uitbreiding 4219 woorden');
  ok(dataCheck.freqEnKeys === 4219, 'FREQ_EN heeft 4219 entries en loopt dus parallel');
  ok(dataCheck.missing === 0, 'geen enkel FREQ-woord mist een FREQ_EN-gloss');

  // woordenboek openen en zoeken op een woord ver voorbij de oude top-1000-grens (rang 2501)
  // v21.6: de kop opent nu het globale zoekveld; het woordenboek zit daar een tik achter.
  await page.evaluate(() => dicModal());
  await page.waitForTimeout(200);
  await page.fill('#dicZoek', 'salgamos');
  await page.waitForTimeout(200);
  const dicText = await page.locator('#dicCard').innerText();
  ok(dicText.indexOf("let's go out") !== -1, 'woordenboek-zoekresultaat toont de Engelse gloss voor "salgamos" (rang 2501, voorbij de oude top-1000-grens)');
  ok(dicText.indexOf('laten we uitgaan') === -1, 'woordenboek-zoekresultaat valt NIET meer terug op de Nederlandse gloss voor dit EN-profiel');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
