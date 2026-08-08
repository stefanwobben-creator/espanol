// Playwright-test voor de mijlpalen (v22.4) en de dagoogst (v22.6). Dit is de bouwsteen onder de muur: wat je kunt
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

  // ---- v22.6: de dagoogst ----
  const ijk = await page.evaluate(() => {
    S.oogst = {}; S.oogstSnap = null;
    S.srs = {}; S.done = {};
    for (let i = 0; i < 40; i++) S.srs['w' + i] = { box: 1 };
    const eerste = oogstBij();
    return { eerste: eerste, oogst: JSON.stringify(S.oogst), snap: S.oogstSnap.w };
  });
  ok(ijk.eerste === null, 'de eerste ronde zet alleen een ijkpunt en boekt niets');
  ok(ijk.oogst === '{}', 'wat je ooit leerde telt niet als oogst van vandaag');
  ok(ijk.snap === 40, 'het ijkpunt staat op wat je nu hebt');

  const oogst = await page.evaluate(() => {
    for (let i = 40; i < 45; i++) S.srs['w' + i] = { box: 1 };
    for (let i = 0; i < 3; i++) S.done['s' + i] = true;
    oogstBij();
    return S.oogst[today()];
  });
  ok(oogst && oogst.w === 5, 'vijf nieuwe woorden geboekt op vandaag: ' + JSON.stringify(oogst));
  ok(oogst && oogst.z === 3, 'en drie zinnen');

  const nogmaals = await page.evaluate(() => {
    const geen = oogstBij();
    S.srs['w99'] = { box: 1 };
    oogstBij();
    return { geen: geen, w: S.oogst[today()].w };
  });
  ok(nogmaals.geen === null, 'zonder verandering wordt er niets bijgeboekt');
  ok(nogmaals.w === 6, 'en een woord erbij telt er precies een bij op');

  const opruimen = await page.evaluate(() => {
    for (let d = 1; d <= 12; d++) S.oogst['2026-01-' + String(d).padStart(2, '0')] = { w: 1, z: 0 };
    S.oogstSnap.dag = '1999-01-01';
    oogstBij();
    return Object.keys(S.oogst).length;
  });
  ok(opruimen <= 7, 'oude dagen worden opgeruimd, hoogstens zeven blijven staan: ' + opruimen);

  const viaPersist = await page.evaluate(() => {
    const voor = (S.oogst[today()] || { w: 0 }).w;
    S.srs['wpersist'] = { box: 1 };
    persist();
    return (S.oogst[today()] || { w: 0 }).w - voor;
  });
  ok(viaPersist === 1, 'persist() boekt de oogst vanzelf');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
