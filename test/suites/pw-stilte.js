// pw-stilte.js (20 aug, v23.146) — zwijgt Chispa tijdens je les, en vergeet het logboek zijn spoken?
//
// WAAROM DIT ER IS
//
// Stefan: "chispa die altijd iets leuks zegt kan weg. nou heel veel dingen kunnen weg."
//
// Dit draait iets terug dat er op zijn eigen verzoek in kwam (v19.49: "zou chispa ook in de
// interface terug komen bijv na de onboarding bij je eerste les?"). Wat er toen bij kwam was een
// hele kaart boven élk scherm van de dagles, met vier zinnen die over twaalf plekken en
// zesentwintig dagen rouleerden. Een aanmoediging die altijd komt is meubilair.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. GEEN CHISPA IN JE LES. Geen kop, geen tekstballon, geen kaart boven je oefening.
//   2. MAAR WEL WAAR JE BENT. Wat ervoor terugkomt is de balk plus "stap 3/5 · Toetsje". Zonder dit
//      is het geen opruimen maar weglaten.
//   3. EN WEL DAARBUITEN. Op het dagscherm vóór je begint staat ze er nog. Zonder deze helft is
//      punt 1 een leegte. Sinds 22 aug, v23.169 met een grens erin: haar begroeting staat op dag 1
//      (daar stelt ze zich voor), en vanaf dag 2 alleen nog haar kop als knop. Stefan: "we zouden
//      Chispa zuiniger inzetten." Deze suite meet daarom allebei de dagen, want een opruiming die
//      haar ook op dag 1 weglaat haalt de introductie weg, en dat is niet zuiniger maar stiller.
//   4. DE FOSSIELEN ZIJN WEG. Fouten op dictado, husselen, klemtoon en jaartal verdwijnen bij het
//      laden. Die oefeningen bestaan niet meer.
//   5. EN DE LEVENDE BLIJVEN. Dit is het controlegeval: een opruiming die alles weggooit klopt ook
//      met punt 4.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwSt' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    S.dagen = { count: 5 };
    dagPlanVerval();

    // ---- 1 en 2. de strook in plaats van de banner ----
    lesFlowStart();
    lesFlow.stap = dagPlan().stappen[2] || 'toetsjes';
    const d = document.createElement('div');
    /* v23.155: de strook is uit de schermen naar het lesframe bovenaan verhuisd, dus
       lesFlowBannerHtml() geeft niets meer terug zolang die les loopt. lesStrookHtml() bouwt hem. */
    d.innerHTML = lesStrookHtml();
    uit.chispaKnop = !!d.querySelector('#btnLesFlowChispa');
    uit.tekstballon = !!d.querySelector('.lfsay');
    uit.kaart = !!d.querySelector('.card');
    uit.strook = !!d.querySelector('.lesstrook');
    uit.balk = d.querySelectorAll('.dagbalk i').length;
    uit.stapregel = (d.querySelector('.lesstap') || {}).textContent || '';
    uit.weg = ['LESFLOW_CHISPA', 'lesFlowChispaFrase', 'lesFlowChispaKlik', 'lesFlowWireBanner']
      .filter(function (n) { return typeof window[n] !== 'undefined'; });
    lesFlow = null;

    // ---- 3. en wel daarbuiten ----
    /* 22 aug, v23.169: dit blok mat op dag 5 dat haar begroeting op de dagkaart stond. Sinds deze
       versie staat die zin er alleen op dag 1. Stefan, na 32 dagen: "we zouden Chispa zuiniger
       inzetten." Dat is dezelfde beweging als waar deze suite over gaat, dus het is hier geen
       verlies maar een aanscherping: op dag 1 stelt die zin haar voor en dat is werk, op dag 32 is
       het dezelfde spreuk voor de dertigste keer en zegt hij alleen nog dat er een diertje bestaat.
       Ze verdwijnt niet: haar kop staat er elke dag als knop, en na je les krijgt ze haar tapa.
       Daarom nu twee metingen, dag 1 en dag 32, en de knop hoort er op allebei te staan. */
    const opDagscherm = function (dagen) {
      S.dagen = { count: dagen };
      show('lessen'); renderLessons();
      const el = document.getElementById('tab-lessen');
      return { knop: !!el.querySelector('#btnRitmeChispa'), groet: !!el.querySelector('.lfsay') };
    };
    const dag1 = opDagscherm(1);
    const dag32 = opDagscherm(32);
    S.dagen = { count: 5 };
    uit.opDagscherm = dag1.knop;
    uit.groetOpDagscherm = dag1.groet;
    uit.knopLaat = dag32.knop;
    uit.groetLaat = dag32.groet;

    // ---- 4 en 5. het foutenlogboek ----
    S.errors = {
      'woord:b1': { id: 'b1', type: 'woord', count: 3 },
      'zin:bs1': { id: 'bs1', type: 'zin', count: 1 },
      'quiz:bq-getallen#0': { id: 'bq-getallen#0', type: 'quiz', count: 1 },
      'conj:hablar-yo-presente': { id: 'x', type: 'conj', count: 1 },
      'dictado:d3': { id: 'd3', type: 'dictado', count: 66 },
      'husselen:h1': { id: 'h1', type: 'husselen', count: 10 },
      'klemtoon:k1': { id: 'k1', type: 'klemtoon', count: 4 },
      'jaartal:j1': { id: 'j1', type: 'jaartal', count: 1 }
    };
    uit.voor = Object.keys(S.errors).length;
    uit.weggegooid = foutenOpschonen(S);
    uit.na = Object.keys(S.errors).sort();
    uit.soorten = FOUT_SOORTEN.slice();
    // en elke soort die de app nog aanmaakt hoort in de lijst te staan, anders gooit hij zich leeg
    uit.levendGemist = ['woord', 'zin', 'quiz', 'gramwiz', 'conj', 'verbo', 'concept', 'corrector', 'escucha']
      .filter(function (t) { return FOUT_SOORTEN.indexOf(t) === -1; });
    return uit;
  });

  console.log('\n-- 1. geen Chispa in je les --');
  ok(r.chispaKnop === false, 'haar kop staat niet meer boven je oefening');
  ok(r.tekstballon === false, 'en er is geen tekstballon met een zin per stap');
  ok(r.kaart === false, 'het is ook geen kaart meer, alleen een strook');
  ok(r.weg.length === 0, 'de zinnen en hun machinerie bestaan niet meer (' + (r.weg.join(',') || 'niets over') + ')');

  console.log('\n-- 2. maar wel waar je bent --');
  console.log('   "' + r.stapregel + '" · ' + r.balk + ' staafjes');
  ok(r.strook, 'er staat een strook');
  ok(r.balk >= 2, 'met de balk erin (' + r.balk + ')');
  ok(/stap \d+\/\d+ · .+/.test(r.stapregel), 'en één regel die zegt waar je bent');

  console.log('\n-- 3. en wel daarbuiten --');
  ok(r.opDagscherm, 'op het dagscherm staat ze er nog, vóór je begint');
  ok(r.groetOpDagscherm, 'op dag 1 met haar begroeting erbij, want daar stelt ze zich voor');
  ok(r.knopLaat, 'en op dag 32 staat haar kop er nog steeds');
  ok(r.groetLaat === false, 'maar de begroeting niet meer: die had je toen al dertig keer gelezen');

  console.log('\n-- 4. de fossielen zijn weg --');
  ok(r.weggegooid === 4, 'vier soorten die niet meer bestaan gaan eruit (' + r.weggegooid + ')');
  ok(r.na.indexOf('dictado:d3') === -1, 'dictado is weg (verwijderd in v21.4)');
  ok(!r.na.some(function (k) { return /^(husselen|klemtoon|jaartal):/.test(k); }), 'husselen, klemtoon en jaartal ook');

  console.log('\n-- 5. het controlegeval: en de levende blijven --');
  console.log('   ' + r.na.join(' · '));
  ok(r.na.length === r.voor - 4, 'de rest staat er nog (' + r.na.length + ' van ' + r.voor + ')');
  ok(r.na.indexOf('woord:b1') !== -1 && r.na.indexOf('conj:hablar-yo-presente') !== -1,
    'ook de soorten met een dubbele punt of streepje in hun id');
  ok(r.levendGemist.length === 0, 'elke soort die de app nog aanmaakt staat in de lijst (' + (r.levendGemist.join(',') || 'alle') + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
