// Playwright-smoketest voor de architectuur-ingrepen van v19.56.
// Stefan, 30 juli: "ik denk dat je ook eens moet kijken naar de hele architectuur van deze app is
// dit snel, slim opgebouwt of is een refactor nodig."
// Geen refactor, wel drie gemeten ingrepen. Dit bestand legt ze vast zodat ze niet terugsluipen:
//  (1) normaliseerState(): één plek die een binnengekomen state compleet maakt, gebruikt door
//      boot(), serverPull() én het sync-code-inlogscherm. Vroeger vulde boot() 24 sleutels aan en
//      serverPull() maar 7, waardoor een state van een ander apparaat de app kon laten omvallen.
//  (2) checkVersie(): haalt versie.txt op (7 bytes) in plaats van de hele pagina (458 kB gezipt),
//      bij elke start én elke tien minuten.
//  (3) renderDic(): dicSortKey wordt gecachet en het zoekveld rendert gedebounced.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  const verzoeken = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });
  page.on('request', (r) => verzoeken.push(r.url()));

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

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwArch' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(600);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(300);

  // --- 1. normaliseerState bestaat en vult alles aan ---
  const norm = await page.evaluate(() => {
    const leeg = normaliseerState({});
    const d = defaultState();
    const mistDefault = Object.keys(d).filter(function (k) { return leeg[k] === undefined; });
    // de sleutels die boot() vroeger apart aanvulde en serverPull() vergat
    const verwacht = ['xp', 'streak', 'dagen', 'txp', 'tapas', 'tapaP', 'fed', 'owned', 'wear', 'lessons',
                      'quizSrs', 'boek', 'comp', 'dagStats', 'lesFlow', 'lesFlowSpel', 'modusKeuze',
                      'gramwiz', 'rincon', 'zorg', 'jerga',
                      'srs', 'errors', 'done', 'quiz', 'dir', 'newIntro'];
    const mist = verwacht.filter(function (k) { return leeg[k] === undefined || leeg[k] === null; });
    return {
      isFn: typeof normaliseerState === 'function',
      mist: mist, mistDefault: mistDefault,
      comp: !!(leeg.comp && leeg.comp.luisteren && leeg.comp.schrijven),
      jerga: Array.isArray(leeg.jerga.gezien),
      streak: leeg.streak && typeof leeg.streak.count === 'number',
      dagen: leeg.dagen && typeof leeg.dagen.count === 'number',
      nul: (function () { const n = normaliseerState(null); return !!(n && n.srs && n.comp.luisteren); })(),
      rommel: (function () { const n = normaliseerState('kapot'); return !!(n && n.srs); })()
    };
  });
  ok(norm.isFn, 'normaliseerState() bestaat als losse functie');
  ok(norm.mist.length === 0, 'een lege state krijgt alle 26 sleutels (mist: ' + norm.mist.join(', ') + ')');
  ok(norm.mistDefault.length === 0, 'alles uit defaultState() zit erin (mist: ' + norm.mistDefault.join(', ') + ')');
  ok(norm.comp, 'S.comp.luisteren en S.comp.schrijven worden allebei aangemaakt');
  ok(norm.jerga, 'S.jerga.gezien is een array');
  ok(norm.streak, 'S.streak heeft een count');
  ok(norm.dagen, 'S.dagen heeft een count (v19.63: het getal dat alleen kan oplopen)');
  ok(norm.nul, 'normaliseerState(null) geeft een bruikbare state terug i.p.v. te knallen');
  ok(norm.rommel, 'ook bij totale rommel als invoer');

  // --- 2. Bestaande waarden blijven staan ---
  const behoud = await page.evaluate(() => {
    const s = normaliseerState({ txp: 1234, srs: { w1: { box: 4 } }, comp: { luisteren: { a: 1 } }, dir: 'nl-es' });
    return { txp: s.txp, box: s.srs.w1.box, luist: s.comp.luisteren.a, schrijf: !!s.comp.schrijven, dir: s.dir };
  });
  ok(behoud.txp === 1234 && behoud.box === 4 && behoud.luist === 1, 'bestaande waarden worden niet overschreven');
  ok(behoud.schrijf, 'maar een half ingevulde S.comp wordt wel compleet gemaakt');
  ok(behoud.dir === 'nl-es', 'een afwijkende dir blijft staan');

  // --- 3. De bug die dit oploste: een pull-achtige state zonder comp/srs laat de app niet omvallen ---
  const overleef = await page.evaluate(() => {
    const bewaar = S;
    let fout = '';
    try {
      // precies wat serverPull() vroeger deed: alleen die zeven sleutels aanvullen
      S = { txp: 50, xp: {}, streak: { count: 0, last: '' }, tapaP: 0, fed: '', owned: {}, wear: {}, lessons: {} };
      S = normaliseerState(S);
      berekenCompetenties();
      updateBadge();
      show('lessen');
      show('perfil');
    } catch (e) { fout = e.message; }
    S = bewaar;
    show('lessen');
    return fout;
  });
  ok(overleef === '', 'berekenCompetenties() + de profielpagina overleven een state die van de server komt ("' + overleef + '")');

  // --- 4. serverPull en het inlogscherm gebruiken diezelfde functie ---
  const bron = await page.evaluate(() => ({
    pull: String(serverPull),
    losseRegels: (String(serverPull).match(/S\.[a-zA-Z]+ = S\.[a-zA-Z]+ *\|\|/g) || []).length
  }));
  ok(bron.pull.indexOf('normaliseerState') !== -1, 'serverPull() roept normaliseerState() aan');
  ok(bron.losseRegels === 0, 'en heeft geen eigen losse aanvul-regels meer (' + bron.losseRegels + ' gevonden)');

  // --- 5. checkVersie haalt versie.txt op, niet de hele pagina ---
  const vcheck = verzoeken.filter((u) => /vcheck=/.test(u));
  const vtxt = verzoeken.filter((u) => /versie\.txt/.test(u));
  ok(vcheck.length === 0, 'de oude hele-pagina-hercheck (?vcheck=) wordt niet meer gedaan (' + vcheck.length + ')');
  ok(vtxt.length >= 1, 'in plaats daarvan wordt versie.txt opgehaald (' + vtxt.length + ')');

  // --- 6. dicSortKey: gecachet, maar met dezelfde uitkomst ---
  await page.evaluate(() => show('woorden'));
  await page.waitForTimeout(300);
  const sortKey = await page.evaluate(() => {
    function ruw(w) {
      const art = { el: 1, la: 1, los: 1, las: 1, un: 1, una: 1 };
      const d = w.es.toLowerCase().split('/')[0].trim().split(' ');
      while (d.length > 1 && art[d[0]]) d.shift();
      return stripAcc(d.join(' '));
    }
    const afwijkend = WORDS.filter(function (w) { return dicSortKey(w) !== ruw(w); });
    const tweede = WORDS.filter(function (w) { return dicSortKey(w) !== ruw(w); }); // nu uit de cache
    return { cache: typeof dicSortCache === 'object', afw: afwijkend.length, afw2: tweede.length, n: WORDS.length };
  });
  ok(sortKey.cache, 'er is een dicSortCache');
  ok(sortKey.afw === 0 && sortKey.afw2 === 0, 'de gecachte sorteersleutel is voor alle ' + sortKey.n + ' woorden identiek aan de berekening');

  // --- 7. Het woordenboek zoekt nog steeds, en rendert gedebounced ---
  // het woordenboek zit achter de zwevende knop, niet achter een tab (zie ook pw-diclock.js)
  // v21.6: de kop opent nu het globale zoekveld; het woordenboek zit daar een tik achter.
  await page.evaluate(() => dicModal());
  await page.waitForTimeout(400);
  const teller = await page.evaluate(() => {
    window.__dicN = 0;
    const orig = window.renderDic;
    window.__dicOrig = orig;
    window.renderDic = function () { window.__dicN++; return orig.apply(null, arguments); };
    return typeof window.renderDic === 'function';
  });
  ok(teller, 'renderDic is te tellen');
  const veld = page.locator('#dicZoek');
  ok(await veld.count() === 1, 'het zoekveld staat er');
  await veld.click();
  await page.keyboard.type('agua', { delay: 15 });
  await page.waitForTimeout(300);
  const n = await page.evaluate(() => window.__dicN);
  ok(n <= 2, 'vier snelle aanslagen kosten hoogstens twee renders i.p.v. vier (' + n + ')');
  const treffers = await page.evaluate(() => {
    const el = document.getElementById('dicCard');
    return { tekst: el.innerText.toLowerCase().indexOf('agua') !== -1, waarde: (document.getElementById('dicZoek') || {}).value };
  });
  ok(treffers.tekst, 'en het zoeken werkt nog gewoon');
  ok(treffers.waarde === 'agua', 'de tekst in het zoekveld blijft heel ("' + treffers.waarde + '")');
  await page.evaluate(() => { if (window.__dicOrig) window.renderDic = window.__dicOrig; });

  // --- 8. Een trage typer krijgt gewoon elke keer een render ---
  await page.fill('#dicZoek', '');
  await page.waitForTimeout(200);
  await page.fill('#dicZoek', 'hola');
  await page.waitForTimeout(250);
  ok((await page.locator('#dicCard').innerText()).toLowerCase().indexOf('hola') !== -1, 'na een gewone fill staat het resultaat er binnen 250 ms');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
