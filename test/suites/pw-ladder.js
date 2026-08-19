// pw-ladder.js (19 aug, v23.132) — houdt de herhaalladder op met groeien?
//
// WAAROM DIT ER IS
//
// De ladder was [0,1,3,7,14,30]. De bovenste doos was 30 dagen en tegelijk de doos waar een woord
// voorgoed in bleef zitten. Elk bewezen woord kwam dus twaalf keer per jaar terug, voor altijd:
// zo'n tien herhalingen per dag bij 313 woorden, ruim zestig bij de 1907 die er met een
// niveauprofiel in zitten. De leesmotor die hierna komt gooit er per gelezen tekst nog woorden bij.
// Zolang de bovenste doos 30 dagen is, groeit de dagelijkse last dus lineair mee met alles wat je
// erbij leert, en straft de app je voor doorleren.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE LADDER LOOPT DOOR. De bovenste doos is een halfjaar-plus, niet een maand, en de reeks
//      stijgt overal.
//   2. "BEWEZEN VAST" SCHUIFT NIET MEE. Dit is de valkuil van deze ronde. stevigDrempel() zit
//      onder de voortgangsbalk, de poort, de niveaupeiling en de Laatste stap. Verlengt iemand de
//      ladder en laat hij stevig meelopen, dan gaat de balk van elke bestaande gebruiker naar nul
//      op de dag van de update. De suite eist dat stevig op doos 5 blijft staan.
//   3. JE KOMT ER OOK ECHT. Een bewezen woord klimt van 5 naar 6, 7 en 8 met 60, 120 en 240 dagen
//      ertussen, en blijft daarna staan.
//   4. MAAR NIET OP JE EIGEN WOORD. Zonder de check van v20.0 blijf je op doos 4 steken. Anders is
//      de langere ladder een sluiproute langs het enige bewijs dat de app heeft.
//   5. DE VERSNELLING SPRINGT NIET OVER DE LAATSTE STAP. Twee dozen tegelijk mag, maar niet over
//      doos 4 heen, want dan bestaat de check niet meer.
//   6. EN DE TELLING BEWEEGT MEE. Woorden in de nieuwe dozen moeten in de doosjesverdeling en in
//      "bewezen vast" blijven meetellen, en elk doosje hoort een label te hebben. Een ladder
//      verlengen en de telling vergeten laat de balk juist dalen zodra je goed wordt.
//
// HET CONTROLEGEVAL
//
// Deze suite is triviaal groen te krijgen door van elke doos 240 dagen te maken: dan klimt alles en
// wordt er nooit meer iets herhaald. Daarom staat er een meting in die MOET dalen: een fout
// antwoord hoort een woord terug te zetten op doos 0, vandaag. Zakt die mee, dan is niet de app
// stuk maar deze meting.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

// Hoeveel woorden er met een niveauprofiel in de pool zitten. Gemeten op 19 aug (313 basis, 1907
// met profiel). Staat hier als getal omdat de last-som anders afhangt van welk profiel de test
// toevallig aanmaakt, en dan meet hij de testopzet in plaats van de ladder.
const POOL = 1907;
const OUDE_TOP = 30;

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  await page.goto(U);
  await page.waitForTimeout(1500);

  const r = await page.evaluate((arg) => {
    const uit = {};
    S.xp = S.xp || {}; S.newIntro = S.newIntro || {}; S.srs = S.srs || {};

    // ---- 1. de vorm van de ladder ----
    uit.ladder = INTERVALS.slice();
    uit.stijgt = INTERVALS.every((v, i) => i === 0 || v > INTERVALS[i - 1]);
    uit.top = INTERVALS[INTERVALS.length - 1];
    uit.stevig = stevigDrempel();
    uit.stevigInterval = INTERVALS[stevigDrempel()];
    uit.zelf = zelfDrempel();

    // ---- 2. de last, gerekend met de ladder van de app zelf ----
    // Een woord op doos b levert 1/INTERVALS[b] herhaling per dag op. Alles bovenaan is dus
    // POOL / bovenste interval.
    uit.lastNieuw = arg.POOL / INTERVALS[INTERVALS.length - 1];
    uit.lastOud = arg.POOL / arg.OUDE_TOP;

    // ---- 3. een bewezen woord klimt door ----
    const w1 = WORDS[0];
    S.srs[w1.id] = { box: stevigDrempel(), due: today(), k: 1, n: 9, f: 3 };  // f: geen versnelling
    const trap = [];
    for (let i = 0; i < 5; i++) {
      S.srs[w1.id].bd = '2000-01-01';                     // de dagrem opzij, zie pw-srsrem
      avtSrsBij(w1, true, true);
      trap.push({ box: S.srs[w1.id].box, dagen: INTERVALS[S.srs[w1.id].box] });
    }
    uit.trap = trap;
    uit.blijftStaan = S.srs[w1.id].box === INTERVALS.length - 1;
    uit.dueVer = S.srs[w1.id].due === addDays(today(), INTERVALS[INTERVALS.length - 1]);

    // ---- 4. zonder check kom je niet voorbij de Laatste stap ----
    const w2 = WORDS[1];
    S.srs[w2.id] = { box: 3, due: today(), n: 9, f: 3 };  // geen k
    const zonder = [];
    for (let i = 0; i < 4; i++) {
      S.srs[w2.id].bd = '2000-01-01';
      avtSrsBij(w2, true, false);                          // aanklikken, geen bewijs
      zonder.push(S.srs[w2.id].box);
    }
    uit.zonderCheck = zonder;
    uit.zonderCheckK = !!S.srs[w2.id].k;
    uit.checkVraagt = wCheckNodig(S.srs[w2.id]);

    // ---- 5. de stapgrootte ----
    function stap(vlag) {
      const w = WORDS[5];
      S.srs[w.id] = Object.assign({ box: 2, due: today(), k: 1, n: 5 }, vlag);
      const voor = S.srs[w.id].box;
      avtSrsBij(w, true, true);
      return S.srs[w.id].box - voor;
    }
    uit.stapSchoon = stap({});               // nooit fout, genoeg beurten: twee
    uit.stapNaFout = stap({ f: 1 });         // ooit fout: een
    uit.stapJong = stap({ n: 1 });           // te weinig beurten: een
    uit.stapOnderaan = (function () {
      const w = WORDS[6];
      S.srs[w.id] = { box: 0, due: today(), k: 1, n: 5 };
      avtSrsBij(w, true, true);
      return S.srs[w.id].box;                // onderaan geen versnelling
    })();

    // ---- 6. de versnelling springt niet over de Laatste stap ----
    const w3 = WORDS[7];
    S.srs[w3.id] = { box: 3, due: today(), n: 9 };         // schoon, maar geen k
    avtSrsBij(w3, true, false);
    uit.sprongBox = S.srs[w3.id].box;
    uit.sprongCheck = wCheckNodig(S.srs[w3.id]);

    // ---- 7. HET CONTROLEGEVAL: fout gaat nog steeds terug naar nul ----
    const w4 = WORDS[8];
    S.srs[w4.id] = { box: INTERVALS.length - 1, due: addDays(today(), 240), k: 1, n: 9 };
    avtSrsBij(w4, false, true);
    uit.foutBox = S.srs[w4.id].box;
    uit.foutDue = S.srs[w4.id].due === today();

    // ---- 8. de telling beweegt mee ----
    S.srs = {};
    const hoog = WORDS.slice(0, 12);
    hoog.forEach(function (w, i) {
      S.srs[w.id] = { box: INTERVALS.length - 1 - (i % 3), due: today(), k: 1, n: 9 };
    });
    const c = voortgangCijfers();
    uit.dozenLengte = c.dozen.length;
    uit.dozenSom = c.dozen.reduce(function (a, b) { return a + b; }, 0);
    uit.gewichtTop = krachtGewicht(INTERVALS.length - 1);
    uit.gewichtStevig = krachtGewicht(stevigDrempel());
    uit.stevigTelt = voortgangTellers().stevig;
    uit.tabel = krachtTabelHtml();
    uit.legenda = vgLegendaUitlegHtml(10);
    return uit;
  }, { POOL, OUDE_TOP });

  console.log('\n-- 1. de ladder loopt door --');
  console.log('   ' + JSON.stringify(r.ladder));
  ok(r.stijgt, 'elke doos wacht langer dan de vorige');
  ok(r.top >= 200, 'de bovenste doos is een halfjaar-plus (nu: ' + r.top + ' dagen)');

  console.log('\n-- 2. de last stopt met groeien --');
  console.log('   ' + POOL + ' bewezen woorden: ' + r.lastOud.toFixed(1) + ' per dag met de oude ladder, ' +
    r.lastNieuw.toFixed(1) + ' met deze');
  ok(r.lastNieuw <= r.lastOud / 4, 'vier keer minder herhalingen aan wat je al kunt');
  ok(r.lastNieuw < 10, 'onder de tien herhalingen per dag voor de hele pool (nu: ' + r.lastNieuw.toFixed(1) + ')');

  console.log('\n-- 3. "bewezen vast" is niet meegeschoven --');
  // De valkuil van deze ronde: stevigDrempel() zit onder de balk, de poort, de peiling en de
  // Laatste stap. Schuift hij mee, dan gaat elke bestaande gebruiker op de dag van de update naar nul.
  ok(r.stevig === 5, 'stevig staat nog op doos 5 (nu: ' + r.stevig + ')');
  ok(r.stevigInterval === 30, 'en dat is nog steeds de maanddoos (nu: ' + r.stevigInterval + ' dagen)');
  ok(r.zelf === 4, 'de Laatste stap zit op de doos eronder (nu: ' + r.zelf + ')');
  ok(r.stevig < r.ladder.length - 1, 'er liggen wachtdozen boven stevig');

  console.log('\n-- 4. een bewezen woord klimt door --');
  const dagen = r.trap.map(function (x) { return x.dagen; });
  console.log('   ' + JSON.stringify(dagen));
  ok(dagen[0] === 60 && dagen[1] === 120 && dagen[2] === 240, 'na de maand volgen 60, 120 en 240 dagen');
  ok(r.blijftStaan, 'daarboven blijft hij staan, hij valt niet uit de ladder');
  ok(r.dueVer, 'en de volgende herhaling staat ook echt 240 dagen vooruit');

  console.log('\n-- 5. maar niet op je eigen woord --');
  ok(r.zonderCheck.every(function (b) { return b <= 4; }),
    'zonder de check kom je niet voorbij doos 4 (nu: ' + JSON.stringify(r.zonderCheck) + ')');
  ok(r.zonderCheckK === false, 'aanklikken zet st.k nog steeds niet');
  ok(r.checkVraagt === true, 'en de Laatste stap wordt daar gevraagd');

  console.log('\n-- 6. de stapgrootte beweegt mee met het woord --');
  ok(r.stapSchoon === 2, 'nooit fout, genoeg beurten, voorbij doos 2: twee dozen (nu: ' + r.stapSchoon + ')');
  ok(r.stapNaFout === 1, 'ooit fout: een doos (nu: ' + r.stapNaFout + ')');
  ok(r.stapJong === 1, 'te weinig beurten: een doos (nu: ' + r.stapJong + ')');
  ok(r.stapOnderaan === 1, 'onderaan de ladder geen versnelling (nu: doos ' + r.stapOnderaan + ')');
  ok(r.sprongBox === 4, 'de sprong stopt op de Laatste stap (nu: doos ' + r.sprongBox + ')');
  ok(r.sprongCheck === true, 'en die stap wordt daar dus ook echt gevraagd');

  console.log('\n-- 7. het controlegeval: naar beneden werkt nog --');
  ok(r.foutBox === 0, 'een fout antwoord zet ook het bovenste woord terug op doos 0 (nu: ' + r.foutBox + ')');
  ok(r.foutDue, 'en vandaag nog een keer');

  console.log('\n-- 8. de telling beweegt mee --');
  ok(r.dozenLengte === r.ladder.length,
    'de doosjesverdeling is even lang als de ladder (nu: ' + r.dozenLengte + ' van ' + r.ladder.length + ')');
  ok(r.dozenSom === 12, 'alle twaalf woorden zitten in een doosje, geen enkele valt eruit (nu: ' + r.dozenSom + ')');
  ok(r.gewichtTop === 1, 'de bovenste doos telt voor honderd procent mee (nu: ' + r.gewichtTop + ')');
  ok(r.gewichtStevig === 1, 'en de maanddoos nog steeds ook (nu: ' + r.gewichtStevig + ')');
  ok(r.stevigTelt === 12, 'woorden boven stevig tellen nog steeds als bewezen vast (nu: ' + r.stevigTelt + ')');
  ok(r.tabel.indexOf('undefined') === -1, 'elk doosje in de tabel heeft een label');
  ok(/8 maanden|8 months/.test(r.tabel), 'de bovenste doos staat met naam in de tabel');
  ok(/5 keer goed|right 5 times/.test(r.legenda),
    'de uitleg van bewezen vast zegt nog steeds vijf keer, niet acht');
  ok(/25 dagen|25 days/.test(r.legenda), 'en nog steeds 25 dagen');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
