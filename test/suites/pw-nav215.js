// Playwright-test voor de nieuwe navigatie (7 aug, v21.5). Stefan: "lessen, dat zijn de oefeningen,
// die zitten nu ook onder speeltuin" en "speeltuin maar daar spelletjes van". Allebei raak: Vertalen,
// zijn belangrijkste oefening, zat verstopt achter het hamburgermenu, en Escuchar, El Corrector en de
// Conjugador stonden tussen Memory en het kruiswoord. De balk heeft nu vijf plekken en de regel
// eronder is in een zin te zeggen: onder Oefenen telt het mee voor je niveau, onder Spelen niet.
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
  await page.fill('input[placeholder="Name"]', 'PwNav' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. vijf plekken, in deze volgorde ----
  const balk = await page.evaluate(() => Array.from(document.querySelectorAll('#nav button')).map(b => b.getAttribute('data-tab')));
  ok(balk.length === 5, 'de balk heeft vijf plekken (' + balk.length + ')');
  ok(balk.join(',') === 'lessen,woorden,oefenen,speeltuin,__meer', 'volgorde: vandaag, woorden, oefenen, spelen, meer (' + balk.join(',') + ')');

  // ---- 2. Oefenen bevat de oefeningen, Spelen alleen spelletjes ----
  await page.evaluate(() => { S.speelAlles = true; show('oefenen'); });
  await page.waitForTimeout(300);
  const oef = await page.evaluate(() => Array.from(document.querySelectorAll('#oefenCard [data-oef]')).map(r => r.getAttribute('data-oef')));
  ['vertalen', 'audi', 'lezen', 'corr', 'conj', 'spiekbrief'].forEach(function (id) {
    ok(oef.indexOf(id) !== -1, 'Oefenen bevat ' + id);
  });

  await page.evaluate(() => { funView = null; show('speeltuin'); });
  await page.waitForTimeout(300);
  const spel = await page.evaluate(() => Array.from(document.querySelectorAll('#funCard .lesson')).map(r => r.id).filter(Boolean));
  ok(spel.indexOf('ftAudi') === -1 && spel.indexOf('ftCorr') === -1 && spel.indexOf('ftConj') === -1,
     'de Speeltuin heeft geen oefeningen meer (' + spel.join(',') + ')');
  ok(spel.indexOf('ftMem') !== -1 || spel.indexOf('ftWs') !== -1, 'maar de spelletjes staan er nog wel');

  // ---- 3. Meer is korter geworden ----
  const meer = await page.evaluate(() => meerItems().map(m => m.id));
  ok(meer.indexOf('vertalen') === -1, 'Vertalen zit niet meer achter het hamburgermenu');
  ok(meer.indexOf('lezen') === -1 && meer.indexOf('spiekbrief') === -1, 'lezen en grammatica ook niet meer');
  ok(meer.indexOf('perfil') !== -1 && meer.indexOf('cursus') !== -1, 'profiel en cursus zitten er nog wel');

  // ---- 4. de balk licht Oefenen op, ook bij een oefening die in de speeltuinkaart woont ----
  await page.evaluate(() => { show('oefenen'); });
  await page.waitForTimeout(200);
  await page.click('#oefenCard [data-oef="audi"]');
  await page.waitForTimeout(400);
  const nu = await page.evaluate(() => ({
    actief: Array.from(document.querySelectorAll('#nav button.active')).map(b => b.getAttribute('data-tab')),
    fun: funView,
    kaart: !!document.querySelector('#funCard h2')
  }));
  ok(nu.fun === 'audi', 'je zit in Escuchar (' + nu.fun + ')');
  ok(nu.actief.join(',') === 'oefenen', 'de balk licht Oefenen op, niet Spelen (' + nu.actief.join(',') + ')');
  ok(nu.kaart === true, 'en de oefening staat echt op het scherm');

  // via Vertalen, dat een eigen tabblad is, moet dat net zo goed werken
  await page.evaluate(() => { show('vertalen'); });
  await page.waitForTimeout(300);
  const bijVertalen = await page.evaluate(() => Array.from(document.querySelectorAll('#nav button.active')).map(b => b.getAttribute('data-tab')));
  ok(bijVertalen.join(',') === 'oefenen', 'ook bij Vertalen licht Oefenen op (' + bijVertalen.join(',') + ')');

  // en bij een echt spelletje licht Spelen op
  await page.evaluate(() => { funView = 'mem'; show('speeltuin'); });
  await page.waitForTimeout(300);
  const bijSpel = await page.evaluate(() => Array.from(document.querySelectorAll('#nav button.active')).map(b => b.getAttribute('data-tab')));
  ok(bijSpel.join(',') === 'speeltuin', 'bij een spelletje licht Spelen op (' + bijSpel.join(',') + ')');

  // ---- 5. de Spelen-knop brengt je naar de lijst, niet naar het spel waar je in zat ----
  await page.click('#nav button[data-tab="speeltuin"]');
  await page.waitForTimeout(300);
  const terug = await page.evaluate(() => ({ fun: funView, kop: (document.querySelector('#funCard h2') || {}).textContent }));
  ok(!terug.fun, 'de Spelen-knop zet je terug op de lijst (' + terug.fun + ')');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
