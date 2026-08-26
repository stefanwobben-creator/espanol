// pw-dagmeting.js (26 aug, v23.198) — de voorspelling meet je dagen, niet je maandagen
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 26 aug: "als je dagelijks meet en je ziet iemand komt dagelijks heb je sneller goede data
// om een voorspelling te doen dan iemand die af en toe komt toch?"
//
// De voorspelling rekende op weekmetingen en zweeg onder de drie. Stefan kwam 36 dagen op rij en had
// er twee; iemand die twee keer per maand komt had er na dezelfde drie weken evenveel. Het ritme
// volgde de kalender in plaats van de gebruiker.
//
// Sinds v23.198 komt er één punt per dag bij (S.dagMeting) en komt het tempo uit een
// kleinste-kwadratenlijn in plaats van uit een gemiddelde van twee verschillen.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE HELLING KLOPT. Een reeks van precies +3 per dag geeft een weektempo van 21. Dit is de
//      proef die er het meest toe doet: een voorspeller die de verkeerde helling meet is erger dan
//      een die zwijgt, want hij ziet er hetzelfde uit als een die het weet.
//   2. EN HIJ BELOOFT NIETS BIJ EEN VLAKKE REEKS. Het controlegeval bij 1: een teller die altijd
//      maar iets teruggeeft haalt proef 1 met de goede testdata en liegt bij de rest.
//   3. DE BAND WORDT SMALLER BIJ MEER PUNTEN. Dat is de hele reden om dagelijks te meten. Zonder
//      deze proef is het een aanname en geen eigenschap.
//   4. EÉN PUNT PER DAG. Twee keer openen op dezelfde dag schrijft geen tweede punt.
//   5. DE WEEKMETINGEN GAAN MEE ALS STARTPUNT, op hun eigen datum. Exact, geen reconstructie.
//   6. EN HIJ ZWIJGT ALS ER TE WEINIG LIGT, of als alle punten uit een paar dagen komen. Vijf
//      metingen uit drie dagen zeggen iets over drie dagen en niets over een tempo.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDm' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 1 en 2. de helling ----
  console.log('\n-- 1 en 2. meet de lijn wat erin zit? --');
  const hel = await page.evaluate(() => {
    /* een reeks neerzetten met een bekende helling, en dan kijken wat eruit komt. De datums lopen
       terug vanaf vandaag zodat de reeks er precies zo uitziet als een echte. */
    function zet(dagen, fn) {
      S.dagMeting = {};
      for (let i = dagen - 1; i >= 0; i--) {
        S.dagMeting[addDays(today(), -i)] = { dekw: { A1: fn(dagen - 1 - i), A2: fn(dagen - 1 - i) } };
      }
    }
    const uit = {};
    zet(14, (d) => 100 + 3 * d);          // precies +3 per dag
    uit.stijgend = tempoDagMeting('A2');
    zet(14, () => 100);                    // vlak
    uit.vlak = tempoDagMeting('A2');
    zet(14, (d) => 100 + 3 * d + (d % 3 === 0 ? 2 : d % 3 === 1 ? -2 : 0));  // hobbelig rond +3
    uit.hobbelig = tempoDagMeting('A2');
    return uit;
  });
  console.log('   stijgend: ' + JSON.stringify(hel.stijgend));
  console.log('   vlak    : ' + JSON.stringify(hel.vlak));
  console.log('   hobbelig: ' + JSON.stringify(hel.hobbelig));
  ok(hel.stijgend && Math.abs(hel.stijgend.gem - 21) < 0.001,
    '+3 per dag wordt 21 per week (' + (hel.stijgend ? hel.stijgend.gem.toFixed(3) : 'niets') + ')');
  ok(hel.stijgend && hel.stijgend.marge < 0.001,
    'en een perfecte lijn heeft geen marge (' + (hel.stijgend ? hel.stijgend.marge.toFixed(4) : '-') + ')');
  ok(hel.vlak && Math.abs(hel.vlak.gem) < 0.001,
    'CONTROLE: een vlakke reeks geeft tempo nul en belooft dus niets (' + (hel.vlak ? hel.vlak.gem.toFixed(3) : 'niets') + ')');
  ok(hel.hobbelig && Math.abs(hel.hobbelig.gem - 21) < 3 && hel.hobbelig.marge > 0,
    'hobbelige data rond +3 geeft nog steeds ~21, mét een marge (' +
    (hel.hobbelig ? hel.hobbelig.gem.toFixed(2) + ' ± ' + hel.hobbelig.marge.toFixed(2) : 'niets') + ')');

  // ---- 3. meer punten, smallere band ----
  console.log('\n-- 3. de band wordt smaller naarmate je vaker komt --');
  const band = await page.evaluate(() => {
    function reeks(dagen) {
      S.dagMeting = {};
      for (let i = dagen - 1; i >= 0; i--) {
        const d = dagen - 1 - i;
        S.dagMeting[addDays(today(), -i)] = { dekw: { A2: 100 + 3 * d + (d % 2 ? 2 : -2) } };
      }
      const m = tempoDagMeting('A2');
      return m ? { punten: m.punten, gem: +m.gem.toFixed(2), marge: +m.marge.toFixed(2) } : null;
    }
    return [8, 14, 30, 60].map(reeks);
  });
  band.forEach(function (b) { if (b) console.log('   ' + b.punten + ' punten: ' + b.gem + ' ± ' + b.marge); });
  const echt = band.filter(Boolean);
  ok(echt.length === 4, 'alle vier de reeksen leveren een tempo (' + echt.length + ')');
  ok(echt.every(function (b, i) { return i === 0 || b.marge < echt[i - 1].marge; }),
    'en de marge krimpt bij elke stap (' + echt.map(function (b) { return b.marge; }).join(' → ') + ')');
  ok(echt.every(function (b) { return Math.abs(b.gem - 21) < 2; }),
    'CONTROLE: terwijl de helling zelf blijft staan waar hij hoort (' + echt.map(function (b) { return b.gem; }).join(', ') + ')');

  // ---- 4 en 5. het schrijven ----
  console.log('\n-- 4 en 5. één punt per dag, en de weekmetingen gaan mee --');
  const schrijf = await page.evaluate(() => {
    S.dagMeting = {};
    S.meting = {};
    // twee echte weekmetingen, zoals ze in een bestaand profiel staan
    S.meting['2026-W33'] = { d: addDays(today(), -16), dek: { A2: 90 }, dekw: { A2: 120 } };
    S.meting['2026-W34'] = { d: addDays(today(), -9), dek: { A2: 95 }, dekw: { A2: 141 } };
    dagMetingSchrijf();
    const na1 = Object.keys(S.dagMeting).sort();
    const waardeNu = S.dagMeting[today()] && S.dagMeting[today()].dekw.A2;
    dagMetingSchrijf();                       // tweede opening dezelfde dag
    const na2 = Object.keys(S.dagMeting).sort();
    return {
      dagen: na1, nogSteeds: na2,
      uitWeek: na1.filter(function (d) { return S.dagMeting[d].uitWeek; }),
      vandaagIsEcht: !(S.dagMeting[today()] || {}).uitWeek,
      week33: (S.dagMeting[addDays(today(), -16)] || {}).dekw,
      waardeNu: waardeNu
    };
  });
  console.log('   ' + JSON.stringify(schrijf));
  ok(schrijf.dagen.length === 3, 'twee weekmetingen plus vandaag geeft drie punten (' + schrijf.dagen.length + ')');
  ok(schrijf.dagen.length === schrijf.nogSteeds.length,
    'CONTROLE: en twee keer openen op dezelfde dag schrijft er geen vierde bij (' + schrijf.nogSteeds.length + ')');
  ok(schrijf.uitWeek.length === 2 && schrijf.vandaagIsEcht,
    'de twee weekpunten staan gemerkt als afkomstig uit de week, de dagmeting van vandaag niet');
  ok(schrijf.week33 && schrijf.week33.A2 === 120,
    'en ze dragen hun eigen waarde, niet die van vandaag (' + JSON.stringify(schrijf.week33) + ')');

  // ---- 6. wanneer hij zwijgt ----
  console.log('\n-- 6. en wanneer hij zwijgt --');
  const stil = await page.evaluate(() => {
    function zetReeks(punten, spreiding) {
      S.dagMeting = {};
      for (let i = 0; i < punten; i++) {
        const d = Math.round(i * spreiding / Math.max(1, punten - 1));
        S.dagMeting[addDays(today(), -(spreiding - d))] = { dekw: { A2: 100 + 3 * d } };
      }
      return { tempo: tempoDagMeting('A2'), stand: tempoStand('A2') };
    }
    return {
      teWeinig: zetReeks(4, 20),        // 4 punten over 20 dagen: te weinig bewijs
      teKort: zetReeks(8, 3),           // 8 punten over 3 dagen: te weinig spreiding
      goed: zetReeks(8, 20)
    };
  });
  console.log('   te weinig punten: ' + (stil.teWeinig.tempo ? 'SPREEKT' : 'zwijgt') + ', zin: ' + JSON.stringify(stil.teWeinig.stand));
  console.log('   te kort bereik  : ' + (stil.teKort.tempo ? 'SPREEKT' : 'zwijgt') + ', zin: ' + JSON.stringify(stil.teKort.stand));
  /* let op de getallen in die twee regels: bij een spreiding van drie dagen vallen meerdere punten
     op dezelfde datum, dus er blijven er vier over. Dat is precies het geval dat deze proef moet
     vangen (veel beurten, weinig dagen) en niet een fout in de opzet. */
  console.log('   genoeg          : ' + (stil.goed.tempo ? 'spreekt' : 'ZWIJGT'));
  ok(!stil.teWeinig.tempo, 'vier punten is te weinig bewijs, dus geen tempo');
  ok(!stil.teKort.tempo && stil.teKort.stand.span < 7,
    'CONTROLE: en punten uit ' + stil.teKort.stand.span + ' dagen ook niet, want dat is geen tempo maar een week');
  ok(!!stil.goed.tempo, 'en acht punten over twintig dagen spreekt wel');
  ok(stil.goed.stand.genoeg === true && stil.teKort.stand.genoeg === false,
    'de wachtzin en de meter gebruiken dezelfde drempel');

  // ---- 7. en het hangt echt aan de voorspelling op het scherm ----
  console.log('\n-- 7. de voorspelling zelf --');
  const eind = await page.evaluate(() => {
    S.dagMeting = {};
    for (let i = 29; i >= 0; i--) S.dagMeting[addDays(today(), -i)] = { dekw: { A2: 100 + 3 * (29 - i) } };
    const v = voorspelWaar('A2', 4);
    const b = voortgangBand('A2');
    const m = tempoMeting('A2');
    return { v: v, b: b, bron: m && m.bron };
  });
  console.log('   ' + JSON.stringify(eind));
  ok(eind.bron === 'dag', 'tempoMeting() gebruikt de dagreeks en niet de weekreeks');
  ok(eind.v && eind.v.nu === 187 && eind.v.laag === 271 && eind.v.hoog === 271,
    'nu 187, en over 4 weken 271 bij een strak tempo van 21 per week (' +
    (eind.v ? eind.v.nu + ' → ' + eind.v.laag + '-' + eind.v.hoog : 'niets') + ')');
  ok(eind.b && eind.b.onder > 0, 'en de band "hoe lang nog" komt er ook uit (' + (eind.b ? eind.b.onder + '-' + eind.b.boven + ' weken' : 'niets') + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
