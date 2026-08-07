// Playwright-smoketest voor het samenvoegen van dubbele woordenboek-rijen (27 juli): Stefan zag
// "antiguo / antigua" 4x na elkaar in het woordenboek. Nu 1 rij per Spaanse tekst, met alle unieke
// vertalingen eronder als je 'm openklapt.
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

  await page.fill('input[placeholder="Name"]', 'PwDicGroup' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // sinds v19.43 zit de "oeroud"-betekenis van "antiguo / antigua" op boek-11 (tag boek-11, drempel 6
  // voltooide lessen) en is die op slot tot dat hoofdstuk ontgrendeld is (zie WOORDENBOEK-SLOT hieronder
  // en pw-diclock.js) - voor déze test (dubbele-rijen-samenvoeging) is dat niet waar het om gaat, dus
  // hoofdstuk 11 hier kunstmatig ontgrendelen zodat de oorspronkelijke test-intentie overeind blijft
  await page.evaluate(() => { for (let i = 0; i < 8; i++) { S.lessons['__test_boekunlock_' + i] = { done: true }; } });

  // v21.6: de kop opent nu het globale zoekveld; het woordenboek zit daar een tik achter.
  await page.evaluate(() => dicModal());
  await page.waitForTimeout(200);
  await page.fill('#dicZoek', 'antiguo');
  await page.waitForTimeout(200);

  // Sinds v19.53 is ook elke zoekstaart-treffer een aanklikbare rij met een eigen sleutel (freq:<woord>),
  // dus scopen we hier expliciet op de WORDS-gebaseerde rijen: die hebben geen freq:-prefix.
  const LES = '.dicrow[data-dic]:not([data-dic^="freq:"])';
  const rijen = await page.locator(LES).count();
  ok(rijen === 1, 'zoeken op "antiguo" toont nog maar 1 leswoord-rij (was 4 losse rijen voor hetzelfde woord)');

  await page.click(LES + ' .dichead');
  await page.waitForTimeout(150);
  const detailText = await page.locator(LES).innerText();
  ok(detailText.indexOf('oud, van vroeger') !== -1, 'opengeklapt toont de eerste betekenis (les9: "oud, van vroeger")');
  ok(detailText.indexOf('oeroud') !== -1, 'opengeklapt toont ook de andere betekenis (boek-11: "oud, oeroud")');
  const oeroudCount = (detailText.match(/oeroud/g) || []).length;
  ok(oeroudCount === 1, '"oeroud" (dubbel in zowel A2- als A0-woordpool, identieke vertaling) staat maar 1x, niet 2x');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
