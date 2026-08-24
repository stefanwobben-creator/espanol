// pw-lesgat.js (24 aug, v23.193) — wordt uitgelegd wat er getoetst wordt?
//
// WAAROM DEZE SUITE ER IS
//
// De review "De grammatica als geheel" telde dat er twee curricula zijn die elkaar nauwelijks raken:
// het onderwijs komt uit 23 concepten, het toetsen hangt aan 30 spiekkaarten, en op 24 augustus
// gingen 98 van de 281 toetsvragen (35%) over stof die nergens werd uitgelegd. Twaalf kaarten
// hadden wél een toets en géén les.
//
// Dat gat kon zo groot worden omdat niets het narekende. Deze suite rekent het na.
//
// WAT HIJ DOET, EN WAAROM HET EEN TELLER IS EN GEEN VERBOD
//
// Er staan nog elf gaten open; dertien lessen schrijven is geen ronde. De suite legt daarom het
// huidige aantal vast en wordt rood zodra het GROTER wordt. Zo kan er geen gat bij komen zonder dat
// iemand het ziet, en elke les die erbij komt verlaagt het getal. Wie er twee schrijft, zet de
// grens twee lager; dat is één regel en het is de bedoeling.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET AANTAL ONVERKLAARDE KAARTEN LOOPT NIET OP. Dit is de eigenlijke regel.
//   2. DE TWEE NIEUWE LESSEN STAAN ER, hangen aan de kaarten waar ze bij horen, en staan in de
//      leervolgorde. Een concept buiten GC_ORDE krijgt rang 999 en komt nooit aan de beurt.
//   3. ELKE LES KAN GENOEG VRAGEN MAKEN. Het controlegeval bij 2: een les toevoegen is triviaal, een
//      les die na vijf vragen leeg is meet daarna of je vijf items onthoudt.
//   4. EN DE VRAGEN DEUGEN. Elke gegenereerde vraag heeft een juist antwoord dat tussen de opties
//      staat, geen dubbele opties, en een uitleg. Dat is het controlegeval bij 3: veel vragen maken
//      is makkelijk als ze niet hoeven te kloppen.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

/* Stand op 24 augustus, ná de twee lessen van v23.193: er waren twaalf kaarten met een toets en
   zonder les, en de imperativo (20, 25) en de beleefdheidsvormen (12) zijn eraf. */
const GATEN_MAX = 9;

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(800);

  // ---- 1. het gat ----
  console.log('\n-- 1. kaarten met een toets en zonder les --');
  const gat = await page.evaluate(() => {
    const tk = gwTrackKey();
    const metLes = {};
    gcGeordend().forEach(function (c) { ((c.spiek || {})[tk] || []).forEach(function (i) { metLes[i] = 1; }); });
    GRAMWIZ.forEach(function (o) { ((o.spiek || {})[tk] || []).forEach(function (i) { metLes[i] = 1; }); });
    const zonder = {}, vragen = {};
    QUIZZES.forEach(function (q) {
      (q.spiek || []).forEach(function (i) {
        if (metLes[i]) return;
        zonder[i] = 1;
        vragen[i] = (vragen[i] || 0) + (q.vragen || []).length;
      });
    });
    const lijst = Object.keys(zonder).map(Number).sort(function (a, b) { return a - b; });
    return {
      spoor: tk,
      kaarten: lijst.map(function (i) { return i + ' "' + String(CHEATSHEET[i].titel).slice(0, 34) + '" (' + vragen[i] + ' vragen)'; }),
      n: lijst.length,
      vragenTotaal: lijst.reduce(function (a, i) { return a + vragen[i]; }, 0),
      alleVragen: QUIZZES.reduce(function (a, q) { return a + (q.vragen || []).length; }, 0)
    };
  });
  gat.kaarten.forEach(function (k) { console.log('   ' + k); });
  console.log('   ' + gat.n + ' kaarten, ' + gat.vragenTotaal + ' van de ' + gat.alleVragen + ' vragen (' +
    Math.round(100 * gat.vragenTotaal / gat.alleVragen) + '%)');
  ok(gat.n <= GATEN_MAX,
    'het aantal onverklaarde kaarten loopt niet op (' + gat.n + ' van maximaal ' + GATEN_MAX + ')');
  if (gat.n < GATEN_MAX) {
    console.log('   ↓ er is een gat gedicht: zet GATEN_MAX in deze suite op ' + gat.n);
  }

  // ---- 2. de twee nieuwe lessen ----
  console.log('\n-- 2. de twee lessen van v23.193 --');
  const les = await page.evaluate(() => {
    const tk = gwTrackKey();
    return ['imperativo', 'cortesia'].map(function (id) {
      const c = gcConcept(id);
      if (!c) return { id: id, bestaat: false };
      return {
        id: id, bestaat: true, naam: String(c.naam),
        kaarten: (c.spiek || {})[tk] || [],
        rang: gcRang(id),
        inOrde: gcRang(id) < 900,
        hulp: !!gcHulp(id),
        stappen: (gcGebouwd('concept-' + id) || { stappen: [] }).stappen.length,
        capaciteit: (function () { try { return gcMaakVragen(c, 99).length; } catch (e) { return 0; } })()
      };
    });
  });
  les.forEach(function (l) {
    ok(l.bestaat, l.id + ' bestaat als concept' + (l.bestaat ? ' ("' + l.naam + '")' : ''));
    if (!l.bestaat) return;
    ok(l.kaarten.length > 0, '  en hangt aan spiekkaart ' + JSON.stringify(l.kaarten));
    ok(l.inOrde, '  en staat in de leervolgorde op plek ' + l.rang + ' (999 = nooit aan de beurt)');
    ok(l.hulp, '  en heeft een ezelsbrug en een "waar het misgaat"');
    ok(l.stappen >= 2, '  en bouwt ' + l.stappen + ' stappen');
  });

  // ---- 3 en 4. de vragen ----
  console.log('\n-- 3 en 4. de vragen die ze maken --');
  const kwaliteit = await page.evaluate(() => {
    const uit = {};
    ['imperativo', 'cortesia'].forEach(function (id) {
      const c = gcConcept(id);
      if (!c) { uit[id] = null; return; }
      const alle = [];
      for (let k = 0; k < 40; k++) {
        try { gcMaakVragen(c, 5).forEach(function (q) { alle.push(q); }); } catch (e) {}
      }
      uit[id] = {
        capaciteit: (function () { try { return gcMaakVragen(c, 99).length; } catch (e) { return 0; } })(),
        gemaakt: alle.length,
        zonderJuist: alle.filter(function (q) { return !q.o || q.g == null || q.o[q.g] === undefined; }).length,
        dubbeleOpties: alle.filter(function (q) { return new Set(q.o).size !== q.o.length; })
                           .map(function (q) { return q.v + ' :: ' + q.o.join(' | '); }).slice(0, 3),
        zonderUitleg: alle.filter(function (q) { return !q.w; }).length,
        leegVeld: alle.filter(function (q) { return /undefined|\[object/.test(q.v + q.o.join('') + q.w); })
                      .map(function (q) { return q.v; }).slice(0, 3)
      };
    });
    return uit;
  });
  Object.keys(kwaliteit).forEach(function (id) {
    const k = kwaliteit[id];
    if (!k) return;
    console.log('   ' + id + ': ' + k.capaciteit + ' verschillende vragen, ' + k.gemaakt + ' getrokken');
    ok(k.capaciteit >= 8,
      id + ' kan minstens acht verschillende vragen maken (' + k.capaciteit + ') — anders is hij na één ronde leeg');
    ok(k.zonderJuist === 0, 'CONTROLE: ' + id + ' — elk juist antwoord staat tussen de opties (' + k.zonderJuist + ' mis)');
    ok(k.dubbeleOpties.length === 0,
      'CONTROLE: ' + id + ' — geen vraag met twee keer dezelfde optie (' + (k.dubbeleOpties[0] || 'geen') + ')');
    ok(k.zonderUitleg === 0, 'CONTROLE: ' + id + ' — elke vraag zegt waarom (' + k.zonderUitleg + ' zonder)');
    ok(k.leegVeld.length === 0, 'CONTROLE: ' + id + ' — nergens undefined op het scherm (' + (k.leegVeld[0] || 'geen') + ')');
  });

  // ---- 5. en alles wat een concept kan maken, is ook te krijgen ----
  console.log('\n-- 5. bereikbaarheid: haalt de generator eruit wat erin zit? --');
  /* Gevonden doordat cortesia op precies acht vragen bleef steken terwijl zijn patronen er
     zeventien kunnen maken. gcMaakVragen() draaide zijn rotatie alleen door bij een treffer, dus een
     patroon met een vaste vraag blokkeerde alles erachter. Gemeten vóór de reparatie: 1416 vragen
     mogelijk, 580 bereikbaar. Deze proef is de reden dat dat niet terugkomt. */
  const bereik = await page.evaluate(() => {
    const uit = [];
    let mogelijk = 0, bereikbaar = 0;
    gcGeordend().forEach(function (c) {
      const g = {};
      c.patronen.forEach(function (fn) {
        for (let k = 0; k < 300; k++) { try { const q = fn(); if (q) g[q.v] = 1; } catch (e) {} }
      });
      const kan = Object.keys(g).length;
      let krijgt = 0;
      try { krijgt = gcMaakVragen(c, kan).length; } catch (e) {}
      mogelijk += kan; bereikbaar += Math.min(krijgt, kan);
      if (krijgt < kan) uit.push(c.id + ': ' + kan + ' mogelijk, ' + krijgt + ' bereikbaar');
    });
    return { mogelijk: mogelijk, bereikbaar: bereikbaar, mis: uit };
  });
  console.log('   ' + bereik.bereikbaar + ' van de ' + bereik.mogelijk + ' vragen zijn te krijgen');
  ok(bereik.mis.length === 0,
    'elk concept levert alles wat zijn patronen kunnen maken (' + (bereik.mis.slice(0, 3).join(' · ') || 'geen verlies') + ')');
  ok(bereik.mogelijk > 1000, 'CONTROLE: en er is genoeg om over te tellen (' + bereik.mogelijk + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
