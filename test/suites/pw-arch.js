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
  // v22.10: hier stond comp.luisteren:{a:1} als willekeurige vulwaarde. Sinds de opruiming geldt daar
  // een regel (alleen echte luisterscenes), dus de vulwaarde moet er ook een zijn. De vraag die deze
  // test stelt verandert niet: blijft staan wat er stond. Zie pw-cijferbugs.js voor de opruiming zelf.
  const behoud = await page.evaluate(() => {
    const echt = AUDICIONES[0].id;
    const s = normaliseerState({ txp: 1234, srs: { w1: { box: 4 } }, comp: { luisteren: { [echt]: 1 } }, dir: 'nl-es' });
    return { txp: s.txp, box: s.srs.w1.box, luist: s.comp.luisteren[echt], schrijf: !!s.comp.schrijven, dir: s.dir };
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
    /* v23.246: deze proef schreef de sorteerregel zelf nog een keer op en vergeleek dicSortKey()
       daarmee. Dat is precies de regel die dit bestand elders bewaakt: staat een feit in de data,
       dan schrijft geen enkele codeplek dat feit opnieuw. Toen woordEerste() kwam ("el / la cantante"
       is niet het woord "el"), veranderde de app en bleef de kopie hier achter: de proef ging af
       terwijl er niets mis was met wat hij zou moeten bewaken.

       Wat hij zou moeten bewaken staat in zijn eigen kop: gecachet, maar met dezelfde uitkomst. Dus
       twee keer meten met de cache ertussen leeggegooid, en die twee moeten gelijk zijn. Wat de
       sleutel inhoudelijk hoort te zijn, staat in pw-woordkern.js. */
    const vers = {};
    dicSortCache = {};
    WORDS.forEach(function (w) { vers[w.id] = dicSortKey(w); });
    const gevuld = Object.keys(dicSortCache).length;
    const afwijkend = WORDS.filter(function (w) { return dicSortKey(w) !== vers[w.id]; });
    return { cache: typeof dicSortCache === 'object', gevuld: gevuld,
             afw: afwijkend.length, n: WORDS.length,
             voorbeeld: (afwijkend[0] || {}).es || null };
  });
  ok(sortKey.cache, 'er is een dicSortCache');
  ok(sortKey.gevuld > 0, 'CONTROLE: en hij wordt ook echt gevuld (' + sortKey.gevuld + ' sleutels)');
  ok(sortKey.afw === 0,
    'de gecachte sorteersleutel is voor alle ' + sortKey.n + ' woorden gelijk aan de verse berekening' +
      (sortKey.voorbeeld ? ' (wijkt af: ' + sortKey.voorbeeld + ')' : ''));

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
  /* v23.247: hier stond `keyboard.type('agua', {delay: 15})` met een vaste 300 ms erachter, en de
     eis "hoogstens twee renders". Dat is een belofte over de klok van de MACHINE en niet over de
     app: de ontdendering wacht 80 ms stilte af, en draait de poort vier browsers tegelijk, dan
     liggen die vier aanslagen in werkelijkheid verder uit elkaar dan 80 ms. De app doet dan precies
     wat ze belooft en de proef gaat toch rood. Zo viel hij op 6 september om, op 3 renders, terwijl
     er niets aan de hand was.

     Nu wordt het geval GEBOUWD in plaats van gehoopt: vier input-gebeurtenissen in één synchrone
     taak. Die kan geen enkele belasting uit elkaar trekken, dus de timer wordt vier keer opnieuw
     gezet en er hoort er precies één te overleven. Daarna het controlegeval, want "precies één"
     zou ook waar zijn als de teller helemaal niet meer telt. */
  await page.evaluate(() => {
    window.__dicN = 0;
    const el = document.getElementById('dicZoek');
    ['a', 'ag', 'agu', 'agua'].forEach(function (v) {
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
    });
  });
  await page.waitForFunction(() => window.__dicN >= 1, null, { timeout: 8000, polling: 20 }).catch(function () {});
  const n = await page.evaluate(() => window.__dicN);
  ok(n === 1, 'vier aanslagen zonder stilte ertussen kosten één render, niet vier (' + n + ')');

  const n2 = await page.evaluate(() => new Promise((klaar) => {
    /* een vijfde aanslag, deze keer met stilte eromheen. De render heeft het veld vervangen, dus
       hem opnieuw opzoeken. */
    const el = document.getElementById('dicZoek');
    el.value = 'aguac';
    el.dispatchEvent(new Event('input', { bubbles: true }));
    const begin = Date.now();
    const kijk = setInterval(() => {
      if (window.__dicN >= 2 || Date.now() - begin > 5000) { clearInterval(kijk); klaar(window.__dicN); }
    }, 20);
  }));
  ok(n2 === 2, 'CONTROLE: mét stilte ertussen komt er wél een render bij, dus de teller telt (' + n2 + ')');

  /* terug naar "agua", want de twee controles hieronder gaan daarover */
  await page.evaluate(() => new Promise((klaar) => {
    const el = document.getElementById('dicZoek');
    el.value = 'agua';
    el.dispatchEvent(new Event('input', { bubbles: true }));
    const n0 = window.__dicN;
    const begin = Date.now();
    const kijk = setInterval(() => {
      if (window.__dicN > n0 || Date.now() - begin > 5000) { clearInterval(kijk); klaar(); }
    }, 20);
  }));
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
  /* v23.247: hier stond ook een vaste 250 ms. Wat deze proef wil weten is of de ontdendering
     ooit LOSLAAT, niet of de machine binnen een kwart seconde klaar is; wachten tot het er staat
     meet het eerste en niet het tweede. */
  const kwam = await page.waitForFunction(
    () => (document.getElementById('dicCard') || {}).innerText &&
          document.getElementById('dicCard').innerText.toLowerCase().indexOf('hola') !== -1,
    null, { timeout: 8000, polling: 50 }).then(() => true).catch(() => false);
  ok(kwam, 'na een gewone fill komt het resultaat er, zonder dat er nog een tik nodig is');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
