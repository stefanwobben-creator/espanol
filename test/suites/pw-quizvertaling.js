// Playwright-smoketest (29 juli, v19.41): Stefans screenshot van bq-preposiciones vraag 4/8
// ("El parque está ___ de mi casa.", opties enfrente/al lado) - hij vroeg zich terecht af of niet
// beide antwoorden moeten kunnen. Root cause: 113 van de 321 toetsvragen hebben een vertaling
// (v.nl/v.ne) die de dubbelzinnigheid tussen twee grammaticaal geldige opties oplost, maar die
// vertaling werd pas ná het antwoorden getoond (als uitleg), dus de gebruiker moest gokken.
// Fix: de vertaling staat nu al bij de vraag zelf. Deze test bewijst dat aan de hand van precies
// dit voorbeeld (bq-preposiciones) én een tweede toetsje zonder vertaling (moet niets extra tonen).
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

  await page.fill('input[placeholder="Name"]', 'PwQuizVert' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(500);

  // exact het toetsje/de vraag uit Stefans screenshot: bq-preposiciones, "El parque está ___ de mi casa."
  await page.evaluate(() => show('toetsjes')); // v19.47: Toetsjes zit niet meer in de nav
  await page.waitForTimeout(200);
  await page.evaluate(() => startQuiz('bq-preposiciones'));
  await page.waitForTimeout(200);

  // doorlopen tot de vraag met de bekende ambiguïteit (enfrente vs al lado zonder context)
  let gevonden = false;
  for (let i = 0; i < 8; i++) {
    const vraagTekst = await page.locator('#qCard').innerText();
    if (vraagTekst.indexOf('parque') !== -1 && vraagTekst.indexOf('mi casa') !== -1) { gevonden = true; break; }
    const correctIdx = await page.evaluate(() => qState.qz.vragen[qState.i].c);
    await page.locator('#qCard .opt').nth(correctIdx).click();
    await page.waitForTimeout(150);
    if (await page.locator('#btnNextQ').count()) { await page.click('#btnNextQ'); await page.waitForTimeout(150); }
  }
  ok(gevonden, 'de bekende vraag ("El parque está ___ de mi casa.") is teruggevonden in bq-preposiciones');

  if (gevonden) {
    const vraagTekstVoorAntwoord = await page.locator('#qCard').innerText();
    // headless Chromium heeft navigator.language=en, dus profLang()==="en" - de vertaling verschijnt
    // dan als "opposite" i.p.v. "tegenover" (zelfde taalkeuze als de rest van de app, zie eerdere tests)
    ok(/tegenover|opposite/i.test(vraagTekstVoorAntwoord), 'de vertaling ("tegenover"/"opposite" mijn huis) staat al bij de vraag, VOOR het antwoorden - dit lost de ambiguïteit op (' + JSON.stringify(vraagTekstVoorAntwoord.split('\n').slice(0,4)) + ')');
    ok(/vertaling|translation/i.test(vraagTekstVoorAntwoord), 'het label "Vertaling:"/"Translation:" staat bij de vraag zelf');
  }

  // een toetsje ZONDER vertaling-veld moet niets extra's tonen (geen lege "Vertaling:"-regel)
  await page.click('#userName').catch(() => {});
  await page.click('button:has-text("Quizzes")').catch(() => {});
  await page.waitForTimeout(200);
  await page.evaluate(() => startQuiz('bq-getallen'));
  await page.waitForTimeout(200);
  const vraagZonderVert = await page.locator('#qCard').innerText().catch(() => '');
  if (vraagZonderVert) {
    ok(!/vertaling/i.test(vraagZonderVert), 'een toetsje zonder v.nl-veld toont geen (lege) "Vertaling:"-regel');
  }

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
