// Playwright-smoketest voor Jaartallen (29 juli, v19.42): de standalone Jaartallen-oefening in de
// Speeltuin (typ het jaartal voluit in het Spaans) is op Stefans verzoek ("de jaartallen is beetje
// dubbel misschien gewoon terug laten komen in woordjes en zinnen ... meer is ook vaak minder")
// opgeruimd. De 15 jaartal-zinnen bestaan nu gewoon als normale SENTENCES-items (tag:"jaartallen"),
// gekoppeld aan les a2-2, en lopen mee in de gewone Vertalen-rotatie via de spaced-repetition-flow.
// Deze test bewijst in een echte browser (i.p.v. de node-only checks in test.js) dat: (1) de oude
// tegel/functies volledig weg zijn, en (2) een jaartal-zin gewoon door checkSentence() heen werkt
// zoals elke andere zin (score/competenties blijven geldig).
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

  await page.fill('input[placeholder="Name"]', 'PwJaartal' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // de standalone oefening en zijn functies/data bestaan niet meer
  await page.click('#nav button[data-tab="speeltuin"]');
  await page.waitForTimeout(300);
  ok(await page.locator('#ftGt').count() === 0, 'de Jaartallen-tegel staat niet meer in de Speeltuin');
  const weg = await page.evaluate(() => ({
    jaarInWoorden: typeof jaarInWoorden === 'undefined',
    JAARTALLEN: typeof JAARTALLEN === 'undefined',
    checkJaartal: typeof checkJaartal === 'undefined',
    pickJaartal: typeof pickJaartal === 'undefined'
  }));
  ok(weg.jaarInWoorden && weg.JAARTALLEN && weg.checkJaartal && weg.pickJaartal, 'jaarInWoorden/JAARTALLEN/checkJaartal/pickJaartal bestaan niet meer (' + JSON.stringify(weg) + ')');

  // de 15 jaartal-zinnen bestaan als gewone SENTENCES en zitten in a2-2, en werken gewoon via
  // checkSentence() zoals elke andere zin (rechtstreekse sIdx-manipulatie, zelfde patroon als
  // test.js en pw-leerkpi.js, want dit hoeft niet via het lesje-vrijspeel-pad te lopen)
  const info = await page.evaluate(() => {
    const zinnen = SENTENCES.filter(s => s.tag === 'jaartallen');
    const a2_2 = TRACKS.a2.lessons.find(l => l.id === 'a2-2');
    return {
      aantal: zinnen.length,
      inLes: !!a2_2 && zinnen.every(s => a2_2.sents.indexOf(s.id) !== -1),
      eersteId: zinnen[0] && zinnen[0].id,
      eersteEs: zinnen[0] && zinnen[0].es
    };
  });
  // Minstens de 15 zinnen uit de v19.42-migratie; de nachtrun mag er drillzinnen bij hangen
  // (v20.8: s142), dus een exacte telling zou elke contentgroei als valse regressie aanmerken.
  ok(info.aantal >= 15, 'er zijn minstens 15 jaartal-zinnen als gewone SENTENCES (' + info.aantal + ')');
  ok(info.inLes, 'alle jaartal-zinnen zitten in les a2-2s sents-array');

  await page.evaluate(() => show('vertalen'));
  await page.waitForTimeout(300);
  const resultaat = await page.evaluate((id) => {
    const s = SENTENCES.find(x => x.id === id);
    sIdx = s;
    document.getElementById('sInput').value = s.es;
    checkSentence();
    return { done: !!S.done[s.id], comp: !!(S.comp && S.comp.schrijven && S.comp.schrijven[s.id]) };
  }, info.eersteId);
  ok(resultaat.done, 'een jaartal-zin (' + info.eersteId + ': "' + info.eersteEs + '") werkt gewoon door checkSentence() heen, net als elke andere zin');
  ok(resultaat.comp, 'checkSentence() markeert S.comp.schrijven voor een jaartal-zin, zoals voor elke andere zin');
  const schrijvenNa = await page.evaluate(() => berekenCompetenties().schrijven.pct);
  ok(schrijvenNa >= 0, 'berekenCompetenties() blijft geldig na een jaartal-zin (' + schrijvenNa + '%)');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
