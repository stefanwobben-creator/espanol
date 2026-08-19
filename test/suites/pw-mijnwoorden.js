// pw-mijnwoorden.js (19 aug, v23.133) — komt terug wat je tijdens het lezen opzoekt?
//
// WAAROM DIT ER IS
//
// Sinds v23.21 kun je elk woord in een hoofdstuk aantikken en krijg je de betekenis. Dat tikken
// werd geteld ook, in S.leesZoek, met de belofte "eerst een paar hoofdstukken meten, dan pas iets
// beweren". Gezocht waar S.leesZoek gelezen wordt: nergens. Twee plekken in het hele bestand,
// allebei de schrijfkant. Elk woord dat Stefan ooit opzocht is geteld en op de grond gevallen.
//
// Daarmee was de leescyclus half: je leest, je struikelt, je tikt, je krijgt de betekenis, en
// morgen struikel je over hetzelfde woord. Lezen is de sterkste motor die er is voor woordenschat,
// maar alleen als wat je opzoekt ergens terechtkomt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE KNOP DOET IETS ECHTS. Een woord uit de frequentielijst (3.682 woorden die de app wél kon
//      uitleggen en niet kon leren) belandt in S.mijn, in WORDS en in de SRS op doos 0.
//   2. EN HET KOMT OOK ECHT LANGS. In de pool staan is niet hetzelfde als aan de beurt komen:
//      allowedWordIds en dagPortie moeten het woord kennen. Zonder deze twee is de knop een
//      knop die "toegevoegd" zegt en niets doet.
//   3. GEEN DUBBELEN. mijnWoordenInPool() draait bij elke start en bij elke toevoeging. Vult hij
//      WORDS twee keer, dan groeit de pool bij elke sessie en klopt geen enkele teller meer.
//   4. NIET OVERAL EEN KNOP. Bij een naam valt er niets te leren, en bij een uitdrukking zou je
//      juist de verkeerde eenheid leren: de uitleg zegt dat "dejan" los niets betekent.
//   5. DE TELLER VAN v23.21 WORDT GELEZEN. Een eerder opgezocht woord hoort in de regel "hier
//      zocht je eerder op" te staan, en de knop eronder hoort ze allemaal toe te voegen.
//   6. DE DEKKING IS EERLIJK EN BEWEEGT. Het getal telt kaartjes in je stapel, niet wat je "kent",
//      en het gaat omhoog van een woord toevoegen.
//   7. EN HET HOOFDSTUK WORDT EEN KEER ONTLEED. De dekking en de opzoeklijst willen allebei van elk
//      woord weten waar het heen zou gaan, en leesBetekenis() is duur. Zonder cache kostte een
//      hoofdstuk openen 455 ms hier en dus ruim een seconde op een telefoon. Geteld in plaats van
//      geklokt: een tweede vraag over hetzelfde hoofdstuk hoort NUL nieuwe ontledingen te kosten,
//      en een ander hoofdstuk hoort ze wel te doen. Een klok zou hier alleen maar flakken.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door élk woord in de pool te gooien: dan klopt punt 1 en 2 en is
// de app stuk. Daarom staat er tegenover elke toevoeging een meting die NIET mag bewegen: de
// pool groeit met precies één rij per toegevoegd woord, en een woord waar geen knop bij hoort komt
// er ook niet in.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwMijn' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    const h = BOOK[0];
    show('lezen', true);
    bState = { h: h, fase: 'lectura', i: 0, score: 0 };
    renderBoekLectura();

    // Een woord uit dit hoofdstuk dat de app wél kan uitleggen maar dat nergens als leerbaar woord
    // bestaat: precies het gat dat deze ronde dicht. Afgeleid uit de tekst, niet met de hand
    // opgeschreven, want een hardgecodeerd woord verandert stilletjes van soort als de lijst groeit.
    const kandidaat = (function () {
      const spans = [].slice.call(document.querySelectorAll('.lw'));
      for (let i = 0; i < spans.length; i++) {
        const w = spans[i].getAttribute('data-lw');
        const b = leesBetekenis(w);
        const d = mijnDoel(b);
        if (d && d.eigen && !mijnHeeft(d)) return { span: spans[i], w: w, b: b, d: d };
      }
      return null;
    })();
    uit.gevonden = !!kandidaat;
    if (!kandidaat) return uit;

    uit.woord = kandidaat.w;
    const poolVoor = WORDS.length;

    // ---- 1. de knop staat er en doet iets echts ----
    leesToon(kandidaat.w, kandidaat.span);
    uit.knopEr = !!document.getElementById('btnLeesMijn');
    leesMijnKlik();
    const id = kandidaat.d.id;
    uit.id = id;
    uit.inMijn = !!(S.mijn && S.mijn[kandidaat.d.plat]);
    uit.inWords = WORDS.some(function (w) { return w.id === id; });
    uit.srsBox = S.srs[id] && S.srs[id].box;
    uit.srsDue = S.srs[id] && S.srs[id].due === today();
    uit.knopWeg = !document.getElementById('btnLeesMijn');

    // ---- 2. en het komt ook echt langs ----
    uit.toegestaan = allowedWordIds().indexOf(id) !== -1;
    uit.inPortie = (function () {
      try {
        const p = dagPortie();
        return (p.herhaal || []).concat(p.nieuw || []).some(function (w) { return w.id === id; });
      } catch (e) { return 'FOUT: ' + e.message; }
    })();

    // ---- 3. HET CONTROLEGEVAL: precies een rij erbij, ook na tien keer aanvullen ----
    for (let i = 0; i < 10; i++) mijnWoordenInPool();
    uit.poolGroei = WORDS.length - poolVoor;

    // ---- 4. niet overal een knop ----
    uit.naamDoel = mijnDoel(leesBetekenis('Chispa'));      // staat in geen enkele lijst
    uit.uitdrukkingKnop = (function () {
      // een uitdrukking herkennen we aan de vlag die leesBetekenis zelf zet
      const spans = [].slice.call(document.querySelectorAll('.lw'));
      for (let i = 0; i < spans.length; i++) {
        const b = leesBetekenis(spans[i].getAttribute('data-lw'));
        if (b && b.uitdrukking) {
          leesToon(spans[i].getAttribute('data-lw'), spans[i]);
          return { gezien: true, knop: !!document.getElementById('btnLeesMijn') };
        }
      }
      return { gezien: false, knop: false };
    })();
    uit.alHeeftKnop = (function () {
      // een woord dat al in je stapel ligt: melding in plaats van knop
      leesToon(kandidaat.w, kandidaat.span);
      return { knop: !!document.getElementById('btnLeesMijn'),
               tekst: document.getElementById('leesUitleg').textContent };
    })();

    // ---- 5. de teller van v23.21 wordt gelezen ----
    S.leesZoek = S.leesZoek || {};
    const spans2 = [].slice.call(document.querySelectorAll('.lw'));
    let gezet = 0;
    for (let i = 0; i < spans2.length && gezet < 3; i++) {
      const w = spans2[i].getAttribute('data-lw');
      const d = mijnDoel(leesBetekenis(w));
      if (d && !mijnHeeft(d)) { S.leesZoek[leesPlat(w)] = 4; gezet++; }
    }
    uit.gezet = gezet;
    uit.opgezocht = leesOpgezocht(h).length;
    renderBoekLectura();
    uit.regelEr = /zocht je eerder op/.test(document.getElementById('lezenCard').textContent);
    uit.allesKnop = !!document.getElementById('btnLeesAlles');

    // ---- 6. de dekking beweegt ----
    const dekVoor = leesDekking(h);
    leesAllesKlik();
    uit.naAlles = leesOpgezocht(h).length;
    // doos 0 telt nog niet mee in de dekking (die telt wat je oefent, box >= 1), dus zetten we er
    // een echte beurt op: dan hoort het getal omhoog te gaan en niet eerder.
    const verse = leesOpgezocht(h);
    S.srs[Object.keys(S.mijn)[0] ? mijnWoordId(Object.keys(S.mijn)[0]) : id].box = 1;
    const dekNa = leesDekking(h);
    uit.dekVoor = dekVoor.bekend;
    uit.dekNa = dekNa.bekend;
    uit.dekN = dekVoor.n;
    uit.dekTekst = document.getElementById('leesDek') && document.getElementById('leesDek').textContent;

    // ---- 7. een keer ontleden, niet drie keer ----
    const echt = leesBetekenis;
    let tel = 0;
    leesBetekenis = function () { tel++; return echt.apply(null, arguments); };
    leesDekking(h); leesOpgezocht(h); leesDekking(h);
    uit.tweedeKeer = tel;
    // HET CONTROLEGEVAL: een ander hoofdstuk moet wel gewoon ontleed worden, anders meet dit niets
    tel = 0;
    leesDekking(BOOK[1]);
    uit.anderHfd = tel;
    leesBetekenis = echt;
    return uit;
  });

  console.log('\n-- 1. de knop doet iets echts --');
  ok(r.gevonden, 'er staat een woord in hoofdstuk 1 dat de app kan uitleggen maar niet kon leren');
  if (r.gevonden) {
    console.log('   proefwoord: ' + r.woord + ' -> ' + r.id);
    ok(r.knopEr, 'er staat een knop onder de betekenis');
    ok(r.inMijn, 'na de tik staat het woord in S.mijn');
    ok(r.inWords, 'en in de woordenpool');
    ok(r.srsBox === 0, 'met een SRS-rij op doos 0 (nu: ' + r.srsBox + ')');
    ok(r.srsDue, 'en vandaag als vervaldatum, dus morgen komt hij langs');
    ok(r.knopWeg, 'de knop maakt daarna plaats voor de bevestiging');

    console.log('\n-- 2. en het komt ook echt langs --');
    ok(r.toegestaan, 'het woord staat in de toegestane verzameling');
    ok(r.inPortie === true, 'en in de dagportie (nu: ' + r.inPortie + ')');

    console.log('\n-- 3. het controlegeval: geen dubbelen --');
    ok(r.poolGroei === 1, 'tien keer aanvullen geeft precies een rij erbij (nu: ' + r.poolGroei + ')');

    console.log('\n-- 4. niet overal een knop --');
    ok(r.naamDoel === null, 'een naam levert niets op om te leren');
    if (r.uitdrukkingKnop.gezien) ok(!r.uitdrukkingKnop.knop, 'een uitdrukking krijgt geen knop voor het losse woord');
    else console.log('  (geen uitdrukking in dit hoofdstuk, overgeslagen)');
    ok(!r.alHeeftKnop.knop, 'een woord dat al in je stapel ligt krijgt geen knop meer');
    ok(/staat in je woorden/.test(r.alHeeftKnop.tekst), 'maar wel de melding dat het er al staat');

    console.log('\n-- 5. de teller van v23.21 wordt eindelijk gelezen --');
    ok(r.opgezocht >= r.gezet, 'eerder opgezochte woorden komen terug (nu: ' + r.opgezocht + ' van ' + r.gezet + ')');
    ok(r.regelEr, 'de regel "hier zocht je eerder op" staat op het scherm');
    ok(r.allesKnop, 'met een knop om ze in een keer toe te voegen');
    ok(r.naAlles === 0, 'na die knop staat er niets meer open (nu: ' + r.naAlles + ')');

    console.log('\n-- 6. de dekking is eerlijk en beweegt --');
    console.log('   ' + r.dekTekst);
    ok(r.dekNa > r.dekVoor, 'een woord dat je echt oefent telt mee (' + r.dekVoor + ' -> ' + r.dekNa + ')');
    ok(r.dekNa < r.dekN, 'en het getal is geen honderd procent: het telt kaartjes, geen aannames');

    console.log('\n-- 7. een keer ontleden, niet drie keer --');
    ok(r.tweedeKeer === 0, 'drie vragen over hetzelfde hoofdstuk kosten geen enkele nieuwe ontleding (nu: ' + r.tweedeKeer + ')');
    ok(r.anderHfd > 50, 'maar een ander hoofdstuk wordt wel echt ontleed (nu: ' + r.anderHfd + ')');
  }

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
