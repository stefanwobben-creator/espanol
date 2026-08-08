// Playwright-test voor de mijlpalen (8 aug, v22.4). Dit is de bouwsteen onder de muur: wat je kunt
// wordt opgeschreven met een datum, zodat er straks iets te tonen valt. Stefan, over de wall: "en
// dingen als gefeliciteerd je zit al op 100 woorden bijv."
// Wat hier bewaakt wordt: de inhaalronde viert niets (anders vier je vandaag acht oude mijlpalen
// tegelijk), een nieuwe grens krijgt de datum van vandaag, een grens die je al had blijft op zijn
// oorspronkelijke datum staan, en persist() doet het vanzelf zodat niemand het kan vergeten.
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
  await page.fill('input[placeholder="Name"]', 'PwMj' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);

  const eerste = await page.evaluate(() => {
    S.mijlpalen = null;
    S.srs = {};
    for (let i = 0; i < 120; i++) S.srs['w' + i] = { box: 1 };
    const nieuw = mijlpaalCheck();
    return { n: nieuw.length, honderd: S.mijlpalen['woorden-100'], vijf: S.mijlpalen['woorden-25'],
             tweehonderd: S.mijlpalen['woorden-200'] };
  });
  ok(eerste.n === 0, 'de inhaalronde viert niets');
  ok(eerste.honderd === 'oud', 'wat je al had krijgt "oud" in plaats van de datum van vandaag');
  ok(eerste.vijf === 'oud', 'dat geldt voor elke grens die je al voorbij was');
  ok(eerste.tweehonderd === undefined, 'een grens die je nog niet haalde staat er niet in');

  const tweede = await page.evaluate(() => {
    for (let i = 120; i < 210; i++) S.srs['w' + i] = { box: 1 };
    const nieuw = mijlpaalCheck();
    return { ids: nieuw.map((x) => x.id).join(','), stempel: S.mijlpalen['woorden-200'], vandaag: today() };
  });
  ok(tweede.ids === 'woorden-200', 'de nieuwe grens komt erbij, en alleen die: ' + tweede.ids);
  ok(tweede.stempel === tweede.vandaag, 'met de datum van vandaag');

  const nogEens = await page.evaluate(() => {
    S.mijlpalen['woorden-200'] = '2020-01-01';
    const nieuw = mijlpaalCheck();
    return { n: nieuw.length, stempel: S.mijlpalen['woorden-200'] };
  });
  ok(nogEens.n === 0, 'een grens die je al had levert niets nieuws op');
  ok(nogEens.stempel === '2020-01-01', 'en de oorspronkelijke datum blijft staan');

  const rest = await page.evaluate(() => {
    S.lessons = S.lessons || {};
    S.lessons['a2-1'] = { done: true };
    S.bailes = ['salsa'];
    S.boek = S.boek || {};
    S.boek['h1'] = { done: true };
    return mijlpaalCheck().map((x) => x.id).join(',');
  });
  ok(rest.indexOf('les-a2-1') >= 0, 'een afgeronde les is een mijlpaal: ' + rest);
  ok(rest.indexOf('baile-salsa') >= 0, 'een geleerde dans ook');
  ok(rest.indexOf('boek-h1') >= 0, 'een uitgelezen hoofdstuk ook');

  const vanzelf = await page.evaluate(() => {
    delete S.mijlpalen['baile-salsa'];
    persist();
    return !!S.mijlpalen['baile-salsa'];
  });
  ok(vanzelf, 'persist() legt ze vast, dus geen enkele plek in de app hoeft eraan te denken');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
