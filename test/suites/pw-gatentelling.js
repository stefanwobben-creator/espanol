// pw-gatentelling.js (3 sep, v23.231) — kun je de vraag beantwoorden met één keuze?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 3 sep, met een schermafbeelding van q-relatar-extra2: "deze oefeningen blijf ik gek vinden
// want ik moet twee antwoorden intypen, maar kan er maar een kiezen."
//
//     Cuando ___ a la estación, el tren ya ___ .
//     [ llegué ]  [ llegaba ]  [ había salido ]  [ salió ]
//
// Twee gaten, vier losse vormen. Hij koos llegué en kreeg rood, terwijl llegué het juiste antwoord
// is voor het eerste gat. De vraag is niet moeilijk, hij is onbeantwoordbaar.
//
// Gemeten over alle 467 vragen: 31 hebben twee of meer gaten, 17 daarvan waren in orde (het antwoord
// vult ze allemaal: "era, vivía"), en 14 niet. Alle veertien in de toetsen over indefinido en
// imperfecto.
//
// EN DAAROM IS DIT MEER DAN EEN SCHOONHEIDSFOUT
//
// De nachtrun van 3 sep concludeerde uit "7 van de 8 fout op q-relatar-extra2" dat indefinido tegen
// imperfecto Stefans zwakste onderdeel is, en zette dat in zijn doosjes. Van die acht vragen waren
// er zes onbeantwoordbaar. Dat is geen meting van Stefan maar van de toets, en een verkeerde
// diagnose is erger dan geen.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. GEEN ENKELE VRAAG IN DE APP HEEFT MEER GATEN DAN ZIJN ANTWOORD VULT. Over alle toetsen van
//      allebei de sporen, want een A0-vraag is net zo goed onbeantwoordbaar.
//   2. DE AFLEIDERS HEBBEN EVENVEEL DELEN ALS HET ANTWOORD. Anders verraadt de vorm het antwoord:
//      één optie met een komma tussen vier zonder komma is te raden zonder Spaans te kennen.
//   3. HET CONTROLEGEVAL. Een gebouwde vraag met twee gaten en een antwoord van één deel wordt door
//      dezelfde telling wél afgekeurd. Zonder dit bewijst proef 1 niets: een teller die altijd nul
//      zegt haalt hem ook.
//   4. DE VRAAG UIT DE SCHERMAFBEELDING STAAT ER, EN IS NU TE BEANTWOORDEN. Bij naam, want dit is de
//      vraag waar het om begon.
//   5. HET AANTAL MEERGATS-VRAGEN IS NIET NUL. Anders zou proef 1 groen staan omdat er niets te
//      meten valt.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwGt' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);

  /* De telling staat in de browser en niet hier, zodat proef 1 en proef 3 met exact dezelfde
     rekenregel meten. Twee tellers die hetzelfde horen te doen lopen vroeg of laat uit elkaar. */
  const uitslag = await page.evaluate(() => {
    function gaten(q) { return (String(q || '').match(/_{2,}/g) || []).length; }
    function delen(o) { return String(o || '').split(/\s*[·,]\s*/).filter(function (x) { return x.trim(); }).length; }
    function keur(qz, v, j) {
      const n = gaten(v.q);
      const opts = v.opts || [];
      const c = v.c;
      if (!(typeof c === 'number' && c >= 0 && c < opts.length)) {
        return { fout: qz.id + ' v' + j + ': geen geldig antwoord' };
      }
      if (n < 2) return { meer: false };
      const d = delen(opts[c]);
      if (d < n) return { fout: qz.id + ' v' + j + ': ' + n + ' gaten, antwoord "' + opts[c] + '" vult er ' + d };
      for (let k = 0; k < opts.length; k++) {
        if (delen(opts[k]) !== d) {
          return { fout: qz.id + ' v' + j + ': afleider "' + opts[k] + '" heeft ' + delen(opts[k]) + ' delen en het antwoord ' + d };
        }
      }
      return { meer: true };
    }
    const fouten = [], meergats = [];
    let vragen = 0;
    [['a2', typeof QUIZZES !== 'undefined' ? QUIZZES : []],
     ['a0', typeof B_QUIZZES !== 'undefined' ? B_QUIZZES : []]].forEach(function (paar) {
      (paar[1] || []).forEach(function (qz) {
        (qz.vragen || []).forEach(function (v, i) {
          vragen++;
          const r = keur(qz, v, i + 1);
          if (r.fout) fouten.push(paar[0] + ' · ' + r.fout);
          if (r.meer) meergats.push(qz.id + ' v' + (i + 1));
        });
      });
    });

    // het gebouwde controlegeval: dezelfde telling op een vraag die wél kapot is
    const kapot = keur({ id: 'proef-kapot' },
      { q: 'Cuando ___ a la estación, el tren ya ___ .', opts: ['llegué', 'llegaba', 'había salido', 'salió'], c: 2 }, 1);
    const scheef = keur({ id: 'proef-scheef' },
      { q: 'Cuando ___ , el tren ya ___ .', opts: ['llegué, salió', 'llegaba', 'a, b', 'c, d'], c: 0 }, 1);

    // en de vraag uit de schermafbeelding, bij naam
    let deVraag = null;
    (typeof QUIZZES !== 'undefined' ? QUIZZES : []).forEach(function (qz) {
      (qz.vragen || []).forEach(function (v) {
        if (/Cuando ___ a la estaci/.test(v.q || '')) deVraag = { id: qz.id, q: v.q, opts: v.opts, c: v.c, u: v.u };
      });
    });

    return { vragen: vragen, fouten: fouten, meergats: meergats,
             kapot: kapot, scheef: scheef, deVraag: deVraag };
  });

  console.log('\n-- 1 en 2. geen enkele vraag vraagt meer dan hij aanbiedt --');
  console.log('   ' + uitslag.vragen + ' vragen nagelopen, ' + uitslag.meergats.length + ' met twee of meer gaten');
  if (uitslag.fouten.length) uitslag.fouten.slice(0, 12).forEach(function (f) { console.log('   ! ' + f); });
  ok(uitslag.fouten.length === 0,
    'elke vraag is met één keuze te beantwoorden (' + uitslag.fouten.length + ' problemen)');
  ok(uitslag.vragen >= 400, 'en er is echt overal gekeken (' + uitslag.vragen + ' vragen)');

  console.log('\n-- 5. er valt iets te meten --');
  console.log('   ' + uitslag.meergats.slice(0, 8).join(', ') + (uitslag.meergats.length > 8 ? ', ...' : ''));
  ok(uitslag.meergats.length >= 25,
    'er zijn genoeg meergats-vragen om van een regel te spreken (' + uitslag.meergats.length + ')');

  console.log('\n-- 3. het gebouwde controlegeval --');
  console.log('   twee gaten, antwoord van één deel : ' + (uitslag.kapot.fout || 'GOEDGEKEURD'));
  console.log('   afleider met een ander aantal delen: ' + (uitslag.scheef.fout || 'GOEDGEKEURD'));
  ok(!!uitslag.kapot.fout,
    'CONTROLE: precies de vraag uit Stefans schermafbeelding wordt door deze telling afgekeurd');
  ok(!!uitslag.scheef.fout,
    'CONTROLE: en een afleider die korter is dan het antwoord ook, want die vorm verraadt het antwoord');

  console.log('\n-- 4. de vraag waar het om begon --');
  const v = uitslag.deVraag;
  console.log('   ' + (v ? v.id + ': ' + v.q : 'NIET GEVONDEN'));
  console.log('   ' + (v ? JSON.stringify(v.opts) + ' c=' + v.c : ''));
  ok(!!v, 'de vraag staat er nog (weghalen is geen repareren)');
  ok(!!v && v.opts[v.c] === 'llegué, había salido',
    'en het juiste antwoord vult allebei de gaten (' + (v ? v.opts[v.c] : '-') + ')');
  ok(!!v && v.opts.every(function (o) { return /,/.test(o); }),
    'alle vier de keuzes zijn een paar, dus de komma verraadt niets');
  ok(!!v && /había salido/i.test(v.u || ''),
    'en de uitleg gaat over het antwoord dat er staat');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
