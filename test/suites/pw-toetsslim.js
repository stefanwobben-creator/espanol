// Playwright-smoketest voor de twee vervolgfixes op de toetsjes-SRS (26 juli, na "Ja maak ook de
// ontbrekende 13 toetsjes"): 1) foutgewogen vraagvolgorde bij een herkansing, 2) bootstrap van
// quizSrs bij lesvoltooiing zodat een nog-nooit-gespeeld toetsje toch meteen in de dagelijkse
// Toetsjes-cyclus terechtkomt.
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

  await page.fill('input[placeholder="Name"]', 'PwToetsSlim' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  let skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // --- Foutgewogen volgorde: eerste vraag bewust fout, dan herkansen en checken dat 'm vooraan staat ---
  await page.evaluate(() => show('toetsjes')); // v19.47: Toetsjes zit niet meer in de nav
  await page.waitForTimeout(200);
  await page.evaluate(() => startQuiz('q-hoeveelheden'));
  await page.waitForTimeout(200);

  const eersteVraagTekst = await page.evaluate(() => qState.volgorde[0].v.q);
  const foutIdx = await page.evaluate(() => { const v = qState.volgorde[0].v; return v.c === 0 ? 1 : 0; });
  await page.locator('#qCard .opt').nth(foutIdx).click();
  await page.waitForTimeout(80);
  await page.click('#btnNextQ');
  await page.waitForTimeout(80);
  for (let i = 0; i < 7; i++) {
    const correctIdx = await page.evaluate(() => qState.volgorde[qState.i].v.c);
    await page.locator('#qCard .opt').nth(correctIdx).click();
    await page.waitForTimeout(80);
    await page.click('#btnNextQ');
    await page.waitForTimeout(80);
  }
  const score1 = await page.locator('#qCard').innerText();
  ok(score1.indexOf('7 / 8') !== -1, 'q-hoeveelheden: eerste speelbeurt scoort 7/8 (1 bewuste fout op vraag 1)');

  await page.click('#btnRetry');
  await page.waitForTimeout(200);
  const herkansingEersteTekst = await page.evaluate(() => qState.volgorde[0].v.q);
  ok(herkansingEersteTekst === eersteVraagTekst, 'bij de herkansing staat de eerder foutgegane vraag weer vooraan (foutgewogen volgorde werkt via de echte UI)');

  for (let i = 0; i < 8; i++) {
    const correctIdx = await page.evaluate(() => qState.volgorde[qState.i].v.c);
    await page.locator('#qCard .opt').nth(correctIdx).click();
    await page.waitForTimeout(80);
    await page.click('#btnNextQ');
    await page.waitForTimeout(80);
  }

  // --- Bootstrap: les a2-7 kunstmatig voltooien, checken dat q-hoeveelheden in de cyclus komt ---
  // v19.49 (Stefan: "ik moet er nu nog 12 ofzo doen, dat motiveert niet ... maar niet achterstallige
  // dingen"): aanmelden gebeurt nog steeds automatisch, maar niet alles meer op vandaag. quizSpreid()
  // zorgt dat er nooit meer dan één toetsje staat te wachten; de rest druppelt binnen. Deze test
  // controleert daarom niet langer "meteen due", maar "aangemeld én ingepland binnen de cyclus".
  const bootstrapCheck = await page.evaluate(() => {
    delete S.quizSrs['q-hoeveelheden'];
    const les = tLessons().find(function(l){ return l.id === 'a2-7'; });
    const stLes = S.lessons[les.id] || {}; stLes.spiek = true; stLes.done = false; S.lessons[les.id] = stLes;
    les.words.forEach(function(id){ S.srs[id] = S.srs[id] || {box:1, due:addDays(today(),5)}; });
    les.sents.forEach(function(id){ S.done[id] = true; });
    les.quizzes.forEach(function(id){ var q = QUIZZES.find(function(x){ return x.id===id; }); S.quiz[id] = q.vragen.length; });
    checkLessonComplete();
    var st = S.quizSrs['q-hoeveelheden'];
    return {
      done: !!(S.lessons['a2-7'] && S.lessons['a2-7'].done),
      hasSrs: !!st,
      due: st ? st.due : null,
      grens: addDays(today(), 30),
      aantalDue: quizDueList().length
    };
  });
  ok(bootstrapCheck.done, 'les a2-7 wordt (kunstmatig opgezet) als voltooid gemarkeerd');
  ok(bootstrapCheck.hasSrs, 'bootstrap: q-hoeveelheden krijgt automatisch een quizSrs-startpunt bij lesvoltooiing');
  ok(bootstrapCheck.due !== null && bootstrapCheck.due <= bootstrapCheck.grens,
    'bootstrap: hij is ingepland binnen de herhaalcyclus i.p.v. genegeerd (' + bootstrapCheck.due + ')');
  ok(bootstrapCheck.aantalDue <= 1,
    'v19.49: er staat nooit meer dan één toetsje op je te wachten, geen achterstand (' + bootstrapCheck.aantalDue + ')');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
