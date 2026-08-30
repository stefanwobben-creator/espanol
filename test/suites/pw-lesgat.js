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
// WAT HIJ DOET, EN WAAROM DE TELLER NU EEN VERBOD IS
//
// De suite legde eerst het huidige aantal vast en werd rood zodra het GROTER werd, zodat elke ronde
// het getal kon verlagen: 12 → 9 na v23.193, en 9 → 0 na v23.194. Vanaf nu staat hij op nul, en
// daarmee is het geen teller meer maar een regel: een toetsvraag over stof die nergens wordt
// uitgelegd komt er niet meer in. Wie een spiekkaart toetst, schrijft de les erbij.
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

/* Stand op 24 augustus, ná de zes lessen en twee aanhechtingen van v23.194: nul. Dit getal hoort
   niet meer omhoog te gaan. Gaat het toch omhoog, dan is er een toets bij gekomen zonder les. */
const GATEN_MAX = 0;

/* de acht lessen van v23.193 en v23.194, met de spiekkaart die ze horen te dekken */
const NIEUW = [
  { id: 'imperativo',    kaarten: [20, 25] },
  { id: 'cortesia',      kaarten: [12] },
  { id: 'tijdmarkers',   kaarten: [6] },
  { id: 'posesivo',      kaarten: [9] },
  { id: 'exclamacion',   kaarten: [17] },
  { id: 'gustarfamilie', kaarten: [18, 23] },
  { id: 'seimpersonal',  kaarten: [21] },
  { id: 'cantidad',      kaarten: [22] }
];

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

  // ---- 2. de acht nieuwe lessen ----
  console.log('\n-- 2. de acht lessen van v23.193 en v23.194 --');
  const les = await page.evaluate((ids) => {
    const tk = gwTrackKey();
    return ids.map(function (id) {
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
  }, NIEUW.map(function (n) { return n.id; }));
  les.forEach(function (l, li) {
    ok(l.bestaat, l.id + ' bestaat als concept' + (l.bestaat ? ' ("' + l.naam + '")' : ''));
    if (!l.bestaat) return;
    const wil = NIEUW[li].kaarten;
    ok(wil.every(function (k) { return l.kaarten.indexOf(k) >= 0; }),
      '  en hangt aan spiekkaart ' + JSON.stringify(wil) + ' (heeft ' + JSON.stringify(l.kaarten) + ')');
    ok(l.inOrde, '  en staat in de leervolgorde op plek ' + l.rang + ' (999 = nooit aan de beurt)');
    ok(l.hulp, '  en heeft een ezelsbrug en een "waar het misgaat"');
    ok(l.stappen >= 2, '  en bouwt ' + l.stappen + ' stappen');
  });

  // ---- 3 en 4. de vragen ----
  console.log('\n-- 3 en 4. de vragen die ze maken --');
  const kwaliteit = await page.evaluate((ids) => {
    const uit = {};
    ids.forEach(function (id) {
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
                      .map(function (q) { return q.v; }).slice(0, 3),
        /* een vraag die met een kleine letter begint verraadt een ingevuld woord dat vooraan
           terechtkwam ("durante el verano viví..."). Het gat zelf telt niet mee: daar staat ___. */
        kleineLetter: alle.filter(function (q) {
          const t = String(q.v).replace(/<[^>]+>/g, '').replace(/^\s+/, '');
          return /^[a-záéíóúñü]/.test(t);
        }).map(function (q) { return q.v; }).slice(0, 3)
      };
    });
    return uit;
  }, NIEUW.map(function (n) { return n.id; }));
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
    ok(k.kleineLetter.length === 0,
      'CONTROLE: ' + id + ' — geen vraag begint met een kleine letter (' + (k.kleineLetter[0] || 'geen') + ')');
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
      /* v23.208: hier stond `if (krijgt < kan)`, en dat is twee ruistrekkingen op exacte gelijkheid
         vergelijken. `kan` is een schatting uit 300 willekeurige trekkingen per patroon en `krijgt`
         is een tweede willekeurige greep uit dezelfde ruimte; die twee lopen af en toe één uit
         elkaar zonder dat er iets stuk is. Op 30 augustus viel de poort daarop om
         (pedirpreguntar: 17 mogelijk, 16 bereikbaar) en was hij daarna drie keer op rij groen.
         Een poort die op ruis dichtvalt kan een goede nacht afkeuren.
         De marge is met opzet klein: het defect waarvoor deze proef is gebouwd was 580 van de 1416,
         een verlies van 59 procent, en dat haalt deze drempel met een factor twintig. */
      if (krijgt < kan - 1 && krijgt < kan * 0.9) uit.push(c.id + ': ' + kan + ' mogelijk, ' + krijgt + ' bereikbaar');
    });
    return { mogelijk: mogelijk, bereikbaar: bereikbaar, mis: uit };
  });
  console.log('   ' + bereik.bereikbaar + ' van de ' + bereik.mogelijk + ' vragen zijn te krijgen');
  ok(bereik.mis.length === 0,
    'elk concept levert alles wat zijn patronen kunnen maken (' + (bereik.mis.slice(0, 3).join(' · ') || 'geen verlies') + ')');
  ok(bereik.mogelijk > 1000, 'CONTROLE: en er is genoeg om over te tellen (' + bereik.mogelijk + ')');
  /* en over alles heen wél een strakke eis, want per concept één item speling mag optellen tot iets
     wat je niet meer wilt. Het defect van toen zat op 41 procent van dit getal. */
  ok(bereik.bereikbaar >= bereik.mogelijk * 0.98,
    'en over alle concepten heen komt er minstens 98 procent uit (' +
      Math.round(1000 * bereik.bereikbaar / bereik.mogelijk) / 10 + '%)');

  // ---- 6. de twee aanhechtingen leggen ook echt uit ----
  console.log('\n-- 6. de aangehechte kaarten worden uitgelegd, niet alleen geclaimd --');
  /* Kaart 4 en 28 zijn woordenlijsten, geen onderwerpen. Ze zijn in v23.194 aan een bestaande les
     gehangen in plaats van er een aparte les voor te verzinnen. Dat mag alleen als die les de
     woorden ook echt behandelt: anders praat de aanhechting proef 1 naar nul zonder dat Stefan er
     iets van leert, en dat is precies het boekhouden waar de review tegen was. */
  const hecht = await page.evaluate(() => {
    const eis = {
      perfindef:   { kaart: 4,  woorden: ['ya', 'todavía no', 'alguna vez', 'últimamente', 'hace dos años', 'aquel día'] },
      indefimperf: { kaart: 28, woorden: ['un día', 'una vez', 'mientras', 'de repente', 'al final'] }
    };
    const tk = gwTrackKey();
    const uit = {};
    Object.keys(eis).forEach(function (id) {
      const c = gcConcept(id);
      const tekst = c ? String(c.uitleg).replace(/<[^>]+>/g, ' ').toLowerCase() : '';
      uit[id] = {
        bestaat: !!c,
        claimt: c ? ((c.spiek || {})[tk] || []).indexOf(eis[id].kaart) >= 0 : false,
        mist: eis[id].woorden.filter(function (w) { return tekst.indexOf(w.toLowerCase()) < 0; }),
        // de matcher moet kunnen falen, anders bewijst "niets mist" niets
        nep: tekst.indexOf('zzquux') < 0
      };
    });
    return uit;
  });
  Object.keys(hecht).forEach(function (id) {
    const h = hecht[id];
    ok(h.bestaat && h.claimt, id + ' claimt de aangehechte kaart');
    ok(h.mist.length === 0, id + ' legt de woorden van die kaart ook echt uit (mist: ' + (h.mist.join(', ') || 'niets') + ')');
    ok(h.nep, 'CONTROLE: ' + id + ' — de zoekmethode vindt een woord dat er niet staat niet');
  });

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
