// pw-morgen.js (20 aug, v23.151) — weet je wat er morgen komt?
//
// WAAROM DIT ER IS
//
// Stefan: "wat is het beste en leukste?" — over de vraag of de roosters (liedje elke 3 dagen, praten
// om de dag, lezen/luisteren om en om) zichzelf moeten inroosteren, of dat hij de week vooruit wil
// zien.
//
// Geen van beide. Een weekoverzicht kán niet kloppen: alle drie de roosters lopen op dagenTotaal(),
// en die telt jouw actieve dagen en niet de kalender. Sla je een dag over, dan schuift alles op. Een
// kalendergrid moet dus gokken wanneer je komt, of het rooster aan de kalender vastspijkeren, en dat
// tweede laat je een liedje missen door een dag vrij te nemen. Dat is de straf die in v19.64 is
// weggehaald.
//
// Dus: één zin over morgen, op het scherm waar die vraag opkomt (v23.67).
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET STAAT ER, EN HET KLOPT MET HET ROOSTER. Wat de zin over morgen zegt is wat het rooster
//      morgen ook echt geeft. Een tweede plek die zijn eigen rooster uitrekent is een tweede
//      waarheid.
//   2. MET NAAM. "Je zingt mee met Brujería" en niet "er is een liedje". De naam is de helft van het
//      vooruitkijken.
//   3. OP EEN GEWONE DAG STAAT ER NIETS EXTRA. Een regel die elke dag hetzelfde zegt is geen bericht
//      meer. Dit is het controlegeval.
//   4. EN TWEE DINGEN OP ÉÉN DAG WORDT ÉÉN ZIN. Niet twee regels onder elkaar.
//   5. DE DAGSLEUTEL KAN OOK EEN ANDERE DAG ZIJN. dayHash() rekende altijd met vandaag; zonder die
//      splitsing is "welk lied is het morgen" niet te beantwoorden, en zou deze zin gokken.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door altijd iets te beloven: dan klopt punt 1 half en is punt 3
// stuk. Daarom staat er tegenover elke belofte een dag waarop er niets hoort te staan.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwMo' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl'; S.musKlaar = {}; S.chat = null;
    S.vert = { trede: 3, reeks: 0 };

    // ---- 5. de dagsleutel kan ook een andere dag zijn ----
    uit.zelfdeAlsVandaag = dagHashVoor(today(), 'musica') === dayHash('musica');
    uit.andersDanMorgen = dagHashVoor(addDays(today(), 1), 'musica') !== dayHash('musica');

    // ---- 1 en 2. het klopt met het rooster, en met naam ----
    // morgen is dag N+1; zet de teller zo dat morgen een liedjesdag is
    S.dagen = { count: MUS_OM_DE - 1 };            // morgen = MUS_OM_DE -> liedje
    const morgenLied = musVanDag(addDays(today(), 1));
    uit.liedTitel = morgenLied ? morgenLied.titel : null;
    uit.liedZin = morgenZin();
    // en dat is echt het lied dat het rooster morgen geeft: zet de teller op morgen en vraag het
    S.dagen = { count: MUS_OM_DE };
    uit.echtBeurt = musDagBeurt();

    // ---- 3. op een gewone dag staat er niets extra ----
    // een dag die geen liedjesdag is en geen praatdag: even, en niet deelbaar door MUS_OM_DE
    let gewoon = null;
    for (let d = 3; d < 40 && gewoon === null; d++) {
      const morgen = d + 1;
      if ((morgen % MUS_OM_DE) !== 0 && (morgen % 2) === 0) gewoon = d;
    }
    S.dagen = { count: gewoon };
    uit.gewoonDag = gewoon;
    uit.gewoonExtra = morgenBijzonder().length;
    uit.gewoonZin = morgenZin();

    // ---- 4. twee dingen op één dag wordt één zin ----
    let beide = null;
    for (let d = 3; d < 60 && beide === null; d++) {
      const morgen = d + 1;
      if ((morgen % MUS_OM_DE) === 0 && (morgen % 2) === 1) beide = d;
    }
    S.dagen = { count: beide };
    uit.beideDag = beide;
    uit.beideN = morgenBijzonder().length;
    uit.beideZin = morgenZin();

    // ---- de rem: op trede 1 belooft hij geen gesprek ----
    S.vert = { trede: 1, reeks: 0 };
    uit.tredeEenN = morgenBijzonder().filter(function (x) { return /Chispa/.test(x); }).length;
    S.vert = { trede: 3, reeks: 0 };

    // ---- en op dag 1 belooft hij niets ----
    S.dagen = { count: 0 };
    uit.dag0 = morgenBijzonder().length;

    S.dagen = { count: 5 };
    return uit;
  });

  console.log('\n-- 5. de dagsleutel kan ook een andere dag zijn --');
  ok(r.zelfdeAlsVandaag, 'dayHash() is dagHashVoor() met vandaag erin');
  ok(r.andersDanMorgen, 'en morgen geeft een andere sleutel, anders viel er niets vooruit te kijken');

  console.log('\n-- 1 en 2. het klopt met het rooster, en met naam --');
  console.log('   ' + r.liedZin);
  ok(r.echtBeurt, 'morgen is echt een liedjesdag volgens het rooster zelf');
  ok(/zingt mee/.test(r.liedZin), 'de zin zegt dat je gaat zingen');
  ok(r.liedTitel && r.liedZin.indexOf(r.liedTitel) !== -1, 'met de naam van het lied erbij (' + r.liedTitel + ')');

  console.log('\n-- 3. het controlegeval: op een gewone dag staat er niets extra --');
  console.log('   ' + r.gewoonZin);
  ok(r.gewoonExtra === 0, 'na dag ' + r.gewoonDag + ' komt er niets bijzonders (' + r.gewoonExtra + ')');
  ok(!/zingt mee|Chispa/.test(r.gewoonZin), 'en de zin belooft dus ook niets');
  ok(r.gewoonZin.length > 10, 'maar er staat nog steeds een regel over morgen');

  console.log('\n-- 4. twee dingen op één dag wordt één zin --');
  console.log('   ' + r.beideZin);
  ok(r.beideN === 2, 'na dag ' + r.beideDag + ' komen er twee dingen (' + r.beideN + ')');
  ok(/zingt mee/.test(r.beideZin) && /Chispa/.test(r.beideZin), 'allebei staan ze erin');
  ok((r.beideZin.match(/\. En /g) || []).length === 1, 'in één zin, niet twee keer "En"');

  console.log('\n-- de remmen --');
  ok(r.tredeEenN === 0, 'op trede 1 van de zinnenladder belooft hij geen gesprek');
  ok(r.dag0 === 0, 'en op dag een belooft hij helemaal niets');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
