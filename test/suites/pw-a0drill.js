// Playwright-test voor het A0-machineblok (7 aug, v21.1). Stefans nachtbot meldde het drie nachten
// op rij: "content-lib/EXTRA_CONTENT beheert alleen het A2-pad; de A0-track heeft geen machine-blok"
// en "basis: 9 fouten · 0 oefenzinnen". Ilona is een echte gebruiker, dus liep zij als enige op een
// pad waar haar fouten nergens terugkwamen. pasExtraContentToe() liep alleen over TRACKS.a2.lessons.
// Deze test bewijst dat (1) de A0-lessen nu wel extra content krijgen, (2) de drie drillzinnen op
// haar eigen clusters bestaan en aan een les hangen die ze meteen open heeft, en (3) ze kort genoeg
// zijn om onder het dictado-plafond van een beginner te vallen (v21.0).
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
  await page.fill('input[placeholder="Name"]', 'PwA0' + Date.now());
  await page.click('button:has-text("A0")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. de drie drillzinnen bestaan en drillen haar eigen clusters ----
  const zinnen = await page.evaluate(() => {
    const bij = {};
    B_SENTENCES.forEach(function (z) { bij[z.id] = z; });
    return {
      bs70: bij.bs70 || null,
      bs71: bij.bs71 || null,
      bs72: bij.bs72 || null,
      aantal: B_SENTENCES.length
    };
  });
  ok(zinnen.bs70 && /se llama/.test(zinnen.bs70.es), 'bs70 drilt me llamo / se llama (' + (zinnen.bs70 && zinnen.bs70.es) + ')');
  ok(zinnen.bs71 && /viuda/.test(zinnen.bs71.es), 'bs71 drilt viudo/viuda (' + (zinnen.bs71 && zinnen.bs71.es) + ')');
  ok(zinnen.bs72 && /extranjero/.test(zinnen.bs72.es), 'bs72 drilt extranjero (' + (zinnen.bs72 && zinnen.bs72.es) + ')');
  ['bs70', 'bs71', 'bs72'].forEach(function (id) {
    const z = zinnen[id];
    ok(!!(z && z.nl && z.en && z.uitleg && z.ue && z.alt && z.alt.length),
       id + ' heeft nl, en, uitleg, ue en alt-varianten');
  });

  // ---- 2. ze hangen aan A0-lessen, en dat kon hiervoor helemaal niet ----
  const lessen = await page.evaluate(() => {
    const bij = {};
    TRACKS.beginner.lessons.forEach(function (l) { bij[l.id] = l.sents.slice(); });
    return {
      a0_0: bij['a0-0'] || [],
      a0_1: bij['a0-1'] || [],
      extraKeys: Object.keys(EXTRA_CONTENT.lessen)
    };
  });
  ok(lessen.a0_0.indexOf('bs70') !== -1, 'bs70 hangt aan les a0-0 (' + JSON.stringify(lessen.a0_0) + ')');
  ok(lessen.a0_1.indexOf('bs71') !== -1 && lessen.a0_1.indexOf('bs72') !== -1, 'bs71 en bs72 hangen aan les a0-1');
  ok(lessen.extraKeys.indexOf('a0-0') !== -1, 'EXTRA_CONTENT kent nu ook A0-lessen');

  // het A2-pad mag er niet door beschadigd zijn
  const a2 = await page.evaluate(() => {
    const bij = {};
    TRACKS.a2.lessons.forEach(function (l) { bij[l.id] = l.sents.slice(); });
    return { a2_2: bij['a2-2'] || [], a2_5: bij['a2-5'] || [], aantal: TRACKS.a2.lessons.length };
  });
  ok(a2.a2_2.indexOf('s142') !== -1 && a2.a2_2.indexOf('s143') !== -1, 'de A2-drillzinnen van de nachtbot staan er nog');
  ok(a2.a2_5.indexOf('s144') !== -1, 'ook s144 staat er nog');

  // geen dubbelen: pasExtraContentToe mag niet twee keer hetzelfde aanhangen
  const dubbel = await page.evaluate(() => {
    const uit = [];
    TRACKS.a2.lessons.concat(TRACKS.beginner.lessons).forEach(function (l) {
      const gezien = {};
      l.sents.forEach(function (id) { if (gezien[id]) uit.push(l.id + ':' + id); gezien[id] = 1; });
    });
    return uit;
  });
  ok(dubbel.length === 0, 'geen enkele les heeft een dubbele zin (' + JSON.stringify(dubbel.slice(0, 3)) + ')');

  // ---- 3. kort genoeg voor een beginner: onder het dictado-plafond van v21.0 ----
  const zwaarte = await page.evaluate(() => {
    S.dicGetypt = 0;
    const bij = {};
    B_SENTENCES.forEach(function (z) { bij[z.id] = z; });
    return {
      plafond: dicPlafond(),
      w70: dicZwaarte(bij.bs70), w71: dicZwaarte(bij.bs71), w72: dicZwaarte(bij.bs72)
    };
  });
  ok(zwaarte.w70 <= zwaarte.plafond, 'bs70 past onder het beginnersplafond (' + zwaarte.w70 + ' <= ' + zwaarte.plafond + ')');
  ok(zwaarte.w71 <= zwaarte.plafond, 'bs71 past onder het beginnersplafond (' + zwaarte.w71 + ')');
  ok(zwaarte.w72 <= zwaarte.plafond, 'bs72 past onder het beginnersplafond (' + zwaarte.w72 + ')');

  // ---- 4. en ze doen het echt in de app: als gewone zin door checkSentence heen ----
  const werkt = await page.evaluate(() => {
    const z = B_SENTENCES.filter(function (x) { return x.id === 'bs71'; })[0];
    const goeden = [norm(z.es)].concat((z.alt || []).map(norm));
    return goeden.indexOf(norm('Mi abuela es viuda.')) !== -1;
  });
  ok(werkt === true, 'bs71 keurt het juiste antwoord goed via de normale antwoordcontrole');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
