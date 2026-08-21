// pw-vertladder.js (20 aug, v23.136) — luistert de lengte van de zinnen naar jou?
//
// WAAROM DIT ER IS
//
// Stefan, 20 aug: "nu zijn de zinnen soms te lang en dat is te moeilijk voor me."
//
// Er wás een lengteregeling, sinds v21.4, en dat maakt het interessanter dan een omissie:
//
//     function dicPlafond(){ return Math.min(30, 6 + getyptN() * 0.5); }
//
// Het plafond hing aan hoeveel zinnen je ooit had getypt. Na twintig staat het op 16, na
// achtenveertig op 30, en de zwaarste zin in de bak is een 19. Vanaf een stuk of vijftig getypte
// zinnen was het plafond dus uit. Het mat hoe lang je bezig was, niet hoe het ging: het ging maar
// één kant op, het ging vanzelf, en het ging nooit terug.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE LADDER BESTAAT EN HEEFT VOORRAAD. Zes treden, oplopende grenzen, en op elke trede staan
//      er genoeg zinnen om een les mee te vullen. Een trede zonder zinnen is geen trede.
//   2. HIJ KLIMT OP DRIE GOED. Niet op tellen, niet op tijd: op drie goede eerste pogingen op rij.
//   3. EN HIJ ZAKT OOK. Dit is het punt waarop de oude regeling faalde. Twee fout op rij en je
//      krijgt kortere zinnen.
//   4. ALLEEN DE EERSTE POGING TELT. Anders klim je door te blijven proberen in plaats van door
//      het te kunnen.
//   5. DE ZINNEN DIE JE KRIJGT ZIJN OOK ECHT KORTER. In de pool staan is niet hetzelfde als
//      aangeboden worden: pickSentence moet het plafond ook echt gebruiken.
//   6. DE KOP ZEGT DE TREDE. Er stond "niveau 2", en 183 van de 231 zinnen staan op 2.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door de trede altijd op 1 te laten staan: dan zijn de zinnen
// altijd kort en klopt punt 5. Daarom staat er tegenover elke daling een stijging, en wordt op de
// hoogste trede gemeten dat de zware zinnen er dan wél bij zitten.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwLad' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    S.speelAlles = true;

    // ---- 1. de ladder bestaat en heeft voorraad ----
    uit.tredes = VERT_TREDES.slice();
    uit.stijgt = VERT_TREDES.every((v, i) => i === 0 || v > VERT_TREDES[i - 1]);
    uit.voorraad = VERT_TREDES.map(function (g) {
      return SENTENCES.filter(function (x) { return dicZwaarte(x) <= g; }).length;
    });
    uit.oudWeg = typeof dicPlafond === 'undefined';

    // ---- 2 en 3. klimmen en zakken ----
    S.vert = { trede: 3, reeks: 0 };
    const klim = [];
    for (let i = 0; i < 3; i++) klim.push(vertBij(true).na);
    uit.klim = klim;                                   // 3,3,4
    S.vert = { trede: 3, reeks: 0 };
    const zak = [];
    for (let i = 0; i < 2; i++) zak.push(vertBij(false).na);
    uit.zak = zak;                                     // 3,2
    // de bodem en het plafond van de ladder zelf
    S.vert = { trede: 1, reeks: -5 };
    uit.bodem = vertBij(false).na;
    S.vert = { trede: VERT_TREDES.length, reeks: 5 };
    uit.top = vertBij(true).na;
    // een goed antwoord na twee fouten is een stap vooruit, geen schone lei
    S.vert = { trede: 3, reeks: -1 };
    vertBij(true);
    uit.naFoutReeks = S.vert.reeks;                    // 1

    // ---- 5. de zinnen die je krijgt zijn ook echt korter ----
    function trek(trede, n) {
      S.vert = { trede: trede, reeks: 0 };
      const uitk = [];
      for (let i = 0; i < n; i++) uitk.push(dicZwaarte(pickSentence()));
      return uitk;
    }
    const laag = trek(1, 40), hoog = trek(6, 40);
    uit.laagMax = Math.max.apply(null, laag);
    uit.hoogMax = Math.max.apply(null, hoog);
    /* Het gemiddelde niet uit veertig trekkingen: pickSentence() kiest willekeurig, en dan valt
       het gemiddelde van trede 6 er af en toe onder dat van trede 1. Deze suite ging daardoor
       willekeurig rood en dat is erger dan geen suite. De vijver zelf is wél deterministisch, en
       dat is ook waar de bewering over gaat: op een hogere trede mogen er zwaardere zinnen in. */
    function vijver(trede) {
      S.vert = { trede: trede, reeks: 0 };
      const p = vertPlafond();
      const z = allowedSentIds().map(function (id) {
        return dicZwaarte(SENTENCES.filter(function (x) { return x.id === id; })[0]);
      }).filter(function (w) { return w <= p; });
      return z.reduce(function (a, b) { return a + b; }, 0) / (z.length || 1);
    }
    uit.laagGem = vijver(1);
    uit.hoogGem = vijver(VERT_TREDES.length);
    uit.plafond1 = (function () { S.vert = { trede: 1, reeks: 0 }; return vertPlafond(); })();
    uit.plafond6 = (function () { S.vert = { trede: 6, reeks: 0 }; return vertPlafond(); })();

    // ---- 4 en 6. alleen de eerste poging telt, en de kop zegt de trede ----
    S.vert = { trede: 3, reeks: 0 };
    show('vertalen', true);
    renderSentence(true);
    const inp = document.getElementById('sInput');
    const zin = sIdx;
    uit.kop = (document.querySelector('#sCard .kicker') || {}).textContent || '';
    // eerste poging: fout
    if (inp) { inp.value = 'zzz onzin zzz'; checkSentence(); }
    const naEerste = S.vert.reeks;
    // tweede poging op dezelfde zin: mag niets meer doen
    renderSentence(false);
    const inp2 = document.getElementById('sInput');
    if (inp2) { inp2.value = zin.es; checkSentence(); }
    uit.naEerste = naEerste;
    uit.naTweede = S.vert.reeks;
    // een verse zin telt wel weer
    renderSentence(true);
    const inp3 = document.getElementById('sInput');
    if (inp3) { inp3.value = sIdx.es; checkSentence(); }
    uit.naVerse = S.vert.reeks;
    return uit;
  });

  console.log('\n-- 1. de ladder bestaat en heeft voorraad --');
  console.log('   grenzen ' + JSON.stringify(r.tredes) + ' · beschikbaar ' + JSON.stringify(r.voorraad));
  ok(r.tredes.length === 6, 'zes treden (nu: ' + r.tredes.length + ')');
  ok(r.stijgt, 'elke trede laat langere zinnen toe dan de vorige');
  ok(r.voorraad[0] >= 40, 'op trede 1 staan genoeg zinnen om een les mee te vullen (nu: ' + r.voorraad[0] + ')');
  ok(r.voorraad.every(function (n, i) { return i === 0 || n > r.voorraad[i - 1]; }),
    'elke trede voegt zinnen toe in plaats van ze te verplaatsen');
  ok(r.oudWeg, 'het oude dicPlafond() is weg');

  console.log('\n-- 2. hij klimt op drie goed --');
  ok(JSON.stringify(r.klim) === '[3,3,4]', 'pas de derde goede beurt levert een trede op (nu: ' + JSON.stringify(r.klim) + ')');
  ok(r.top === 6, 'op de hoogste trede blijft hij staan (nu: ' + r.top + ')');

  console.log('\n-- 3. en hij zakt ook --');
  ok(JSON.stringify(r.zak) === '[3,2]', 'twee foute beurten op rij kosten een trede (nu: ' + JSON.stringify(r.zak) + ')');
  ok(r.bodem === 1, 'op trede 1 kan hij niet verder zakken (nu: ' + r.bodem + ')');
  ok(r.naFoutReeks === 1, 'een goed antwoord na een foute reeks begint op 1, niet op 0 (nu: ' + r.naFoutReeks + ')');

  console.log('\n-- 4. alleen de eerste poging telt --');
  ok(r.naEerste === -1, 'de eerste poging telt (reeks nu: ' + r.naEerste + ')');
  ok(r.naTweede === r.naEerste, 'de tweede poging op dezelfde zin telt niet (reeks nu: ' + r.naTweede + ')');
  ok(r.naVerse !== r.naEerste, 'een verse zin telt wel weer (reeks nu: ' + r.naVerse + ')');

  console.log('\n-- 5. de zinnen die je krijgt zijn ook echt korter --');
  console.log('   trede 1: max ' + r.laagMax + ', gem ' + r.laagGem.toFixed(1) +
    '  |  trede 6: max ' + r.hoogMax + ', gem ' + r.hoogGem.toFixed(1));
  ok(r.laagMax <= r.plafond1, 'op trede 1 komt er niets zwaarder dan ' + r.plafond1 + ' langs (nu: ' + r.laagMax + ')');
  ok(r.hoogMax > r.plafond1, 'op trede 6 komen de zware zinnen er wél bij (nu: ' + r.hoogMax + ')');
  ok(r.hoogGem > r.laagGem, 'en de vijver waaruit hij trekt is er gemiddeld zwaarder');

  console.log('\n-- 6. de kop zegt de trede --');
  console.log('   ' + r.kop);
  ok(/trede 3\/6/.test(r.kop), 'de kop noemt de trede en het totaal');
  ok(!/niveau/.test(r.kop), 'en niet meer "niveau", dat getal stond bij 183 van de 231 zinnen op 2');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
