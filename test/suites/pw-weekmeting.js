// v23.4: de weekmeting legt ook pogingen en fouten vast.
// Zonder deze twee velden kan niemand later narekenen bij welk foutpercentage Stefan de meeste
// woorden per week vast krijgt. De 85%-regel geeft dat antwoord niet (die is afgeleid voor
// gradient-descent-algoritmes en claimt niets over woordenschat), dus moet het uit eigen data komen.
// Wat hier vastligt: zeven dagen tellen mee en de achtste niet, en de meting blijft eenmalig per week.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  let fails = 0;
  const ok = (c, n) => { console.log(c ? 'PASS' : 'FAIL', n); if (!c) fails++; };

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload(); await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"]', 'PwWm' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);

  const m = await page.evaluate(() => {
    const t = today();
    S.meting = {}; S.dagStats = {};
    S.dagStats[t] = { pogingen: 100, fouten: 21 };
    S.dagStats[addDays(t, -3)] = { pogingen: 50, fouten: 9 };
    S.dagStats[addDays(t, -9)] = { pogingen: 999, fouten: 999 };   // buiten het venster
    snapshotSchrijf();
    const w = Object.keys(S.meting)[0];
    return S.meting[w];
  });
  ok(m && m.pog === 150, 'pogingen van zeven dagen opgeteld (' + (m && m.pog) + ')');
  ok(m && m.fout === 30, 'en de fouten van diezelfde dagen (' + (m && m.fout) + ')');
  ok(m && m.pog < 999, 'een dag van negen dagen terug telt niet mee');
  ok(m && typeof m.stevig === 'number', 'het aantal stevige woorden staat er nog steeds bij');

  const nog = await page.evaluate(() => {
    const w = Object.keys(S.meting)[0];
    S.dagStats[today()] = { pogingen: 1, fouten: 1 };
    snapshotSchrijf();
    return S.meting[w].pog;
  });
  ok(nog === 150, 'een tweede keer schrijven in dezelfde week verandert niets');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 2).join(' | '));
  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
