// Playwright-smoketest voor het Familie-klassement (29 juli, v19.38): stond eerst als losse tegel in de
// Speeltuin (v19.37), maar Stefan gaf terecht aan dat een klassement niet bij "extra spelletjes" hoort.
// Nu een vast kaartje op de Profielpagina, tussen je eigen gegevens/competenties en de (handmatige-code)
// Groepen-sectie - want dit scorebord vergt geen code (automatisch op naam) en is dus lager-frictie.
// De sandbox heeft geen netwerktoegang tot Render, dus /api/familia geeft hier altijd null terug -
// deze test verifieert de UI-kant: kaartje bestaat op Profiel, staat op de juiste plek, en de nette
// "server niet bereikbaar"-fallback verschijnt zonder JS-fouten (dezelfde api()-fallback als Duel/Groepen).
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

  await page.fill('input[placeholder="Name"]', 'PwFamilie' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(500);

  // de Speeltuin toont géén Familie-tegel meer (verplaatst)
  await page.click('#nav button[data-tab="speeltuin"]');
  await page.waitForTimeout(300);
  ok(await page.locator('#ftFam').count() === 0, 'de Speeltuin toont geen losse Familie-tegel meer (verplaatst naar Profiel)');

  // Profiel-tabblad openen (nav:false, via de gebruikersnaamknop)
  await page.click('#userName');
  await page.waitForTimeout(300);
  ok(await page.locator('#familieCard').count() === 1, 'de Profielpagina heeft een eigen Familie-kaartje');
  const familieTekst = await page.locator('#familieCard').innerText();
  const titelLabel = await page.evaluate(() => ct('Familie-klassement', 'Family leaderboard'));
  ok(familieTekst.indexOf(titelLabel) !== -1, 'het Familie-kaartje toont de juiste titel (' + titelLabel + ')');

  // volgorde op de Profielpagina: eigen gegevens -> familie (geen code nodig) -> groepen (wel code nodig)
  const volgordeOk = await page.evaluate(() => {
    const kaarten = Array.from(document.querySelectorAll('#tab-perfil .card'));
    const iPerfil = kaarten.findIndex((k) => k.id === 'perfilCard');
    const iFamilie = kaarten.findIndex((k) => k.id === 'familieCard');
    const iGroep = kaarten.findIndex((k) => k.id === 'groepCard');
    return iPerfil < iFamilie && iFamilie < iGroep;
  });
  ok(volgordeOk, 'volgorde op Profiel klopt: eigen gegevens, dan Familie (automatisch), dan Groepen (code nodig)');

  // sandbox heeft geen netwerktoegang tot Render, dus dit valt netjes terug op de bestaande foutmelding
  ok(await page.locator('#famStatus').count() === 1, 'het Familie-kaartje toont een statusregel');
  await page.waitForTimeout(600);
  const statusTekst = await page.locator('#famStatus').innerText();
  ok(statusTekst.length > 0, 'de statusregel toont een nette fallback-tekst i.p.v. leeg te blijven hangen (' + statusTekst + ')');

  // bestaande Profiel-functionaliteit (mail opslaan, competentie-kaart, groepen) staat er nog gewoon naast
  ok(await page.locator('#perfilMail').count() === 1, 'het bestaande mail-veld staat er nog naast het nieuwe Familie-kaartje');
  ok(await page.locator('#groepCard').innerText().then((t) => t.length > 0), 'de Groepen-sectie werkt nog gewoon naast het nieuwe Familie-kaartje');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
