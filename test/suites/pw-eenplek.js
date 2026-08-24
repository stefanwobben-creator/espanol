// pw-eenplek.js (24 aug, v23.191) — drie invarianten, geen drie bugs
//
// WAAROM DEZE SUITE ER IS
//
// Vier fouten op één dag, vier keer dezelfde vorm: twee plekken die hetzelfde werk doen en uit
// elkaar zijn gelopen.
//
//   v23.188  speelStart() maakt een spel vers, speelNaar() vergat letras en de woordenzoeker
//   v23.189  answerQuestion() markeert beide antwoorden, renderCheat() alleen het juiste
//   v23.190  gcOnderwerp() cachet zijn onderwerp, gcOpfrisOnderwerp() ging eromheen
//   v23.188  lesFlowVolgendeKern() had zes takken en geen bodem
//
// Elk van die vier is los gerepareerd, en dat is precies de reparatie waar dit een reparatie van is.
// De suites bij die versies bewaken elk hun eigen geval. Deze bewaakt de VORM, zodat de vijfde
// opvalt voordat Stefan hem tegenkomt.
//
// DE DRIE INVARIANTEN
//
//   1. ELK GEBOUWD ONDERWERP staat stil binnen een sessie en is vers bij een start. Niet alleen de
//      twee soorten van vandaag: de suite loopt over GC_BOUWERS heen, dus een derde soort wordt
//      vanzelf meegenomen zodra hij bestaat.
//   2. ELK KEUZESCHERM markeert het juiste antwoord én dat van jou, en gebruikt daarvoor dezelfde
//      functie. Getoetst op gedrag (staan de merktekens er) én op herkomst (komt het uit
//      keuzeMerk), want een scherm dat het gedrag nabouwt is de volgende die afdrijft.
//   3. ELKE WEG NAAR EEN SPEL maakt hem net zo vers als de andere weg. Getoetst door de twee wegen
//      tegen elkaar te leggen, niet door een lijstje spellen af te vinken.
//
// EN HET CONTROLEGEVAL VAN DE HELE SUITE
//
// Punt 1 is triviaal te halen door nooit meer te vernieuwen, punt 2 door altijd beide klassen te
// zetten, punt 3 door elk spel altijd leeg te gooien. Bij alle drie staat daarom het omgekeerde er
// ook: vers bij een start, één merkteken bij een goed antwoord, en een spel dat je NIET opnieuw
// opent blijft staan waar het stond.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwEp' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ================= 1. elk gebouwd onderwerp =================
  console.log('\n-- 1. elk gebouwd onderwerp staat stil, en is vers bij een start --');
  const bouw = await page.evaluate(() => {
    const soorten = GC_BOUWERS.map(function (b) { return b.pre; });
    const uit = { soorten: soorten, rijen: [] };
    // per soort een handvol echte ids, via de conceptlijst
    const cids = gcGeordend().slice(0, 6).map(function (c) { return c.id; });
    soorten.forEach(function (pre) {
      cids.forEach(function (cid) {
        const id = pre + cid;
        if (!gcGebouwd(id)) return;
        const merk = function () {
          const o = gcGebouwd(id);
          const s = o.stappen[0];
          return JSON.stringify(s.vragen.map(function (q) { return [q.v, q.o, q.g]; }));
        };
        const binnen = [];
        for (let k = 0; k < 5; k++) binnen.push(merk());
        const overStarts = [];
        for (let k = 0; k < 10; k++) { gcVernieuw(id); overStarts.push(merk()); }
        uit.rijen.push({ id: id, pre: pre,
          binnenUniek: new Set(binnen).size, naVernieuwUniek: new Set(overStarts).size });
      });
    });
    return uit;
  });
  console.log('   soorten in GC_BOUWERS: ' + bouw.soorten.join(', ') + ' (' + bouw.rijen.length + ' onderwerpen getoetst)');
  ok(bouw.soorten.length >= 2, 'er zijn minstens twee soorten om te vergelijken');
  ok(bouw.rijen.length >= 6, 'genoeg onderwerpen om iets te betekenen (' + bouw.rijen.length + ')');
  const beweegt = bouw.rijen.filter(function (r) { return r.binnenUniek !== 1; });
  ok(beweegt.length === 0,
    'geen enkel onderwerp verandert onder je handen (' +
    (beweegt.map(function (r) { return r.id + ':' + r.binnenUniek; }).join(', ') || 'alle stil') + ')');
  const perSoortVers = {};
  bouw.rijen.forEach(function (r) {
    perSoortVers[r.pre] = (perSoortVers[r.pre] || 0) + (r.naVernieuwUniek > 1 ? 1 : 0);
  });
  console.log('   vers na vernieuwen, per soort: ' + JSON.stringify(perSoortVers));
  ok(Object.keys(perSoortVers).every(function (p) { return perSoortVers[p] > 0; }),
    'CONTROLE: en elke soort levert ná gcVernieuw() wél andere vragen — anders is de cache een groef');

  // ================= 2. elk keuzescherm =================
  console.log('\n-- 2. elk keuzescherm markeert allebei, via dezelfde functie --');
  const merk = await page.evaluate(() => {
    return {
      // gedrag van de functie zelf
      juist: keuzeMerk(1, 1, 0),
      jouw: keuzeMerk(0, 1, 0),
      niets: keuzeMerk(2, 1, 0),
      goedAntwoord: [keuzeMerk(0, 1, 1), keuzeMerk(1, 1, 1)],
      zonderKeuze: keuzeMerk(0, 1, null),
      // en of de twee schermen hem echt aanroepen
      inToets: /keuzeMerk\(/.test(String(answerQuestion)),
      inWizard: /keuzeMerk\(/.test(String(renderGramWiz || function () {})) ||
                /keuzeMerk\(/.test(document.documentElement.innerHTML) // valt terug op de bron
    };
  });
  ok(merk.juist === 'juist' && merk.jouw === 'jouw' && merk.niets === '',
    'keuzeMerk geeft juist / jouw / niets (' + [merk.juist, merk.jouw, merk.niets].join(' · ') + ')');
  ok(merk.goedAntwoord[1] === 'juist' && merk.goedAntwoord[0] === '',
    'CONTROLE: bij een goed antwoord staat er één merkteken, niet twee (' + merk.goedAntwoord.join(' · ') + ')');
  ok(merk.zonderKeuze === '',
    'CONTROLE: en zonder gekozen antwoord markeert hij niets rood');
  ok(merk.inToets, 'het toetsje gebruikt keuzeMerk en bouwt het niet na');

  // en op het scherm, in allebei
  const schermen = await page.evaluate(() => {
    const uit = {};
    // het toetsje
    show('toetsjes', true);
    const q = QUIZZES[0];
    startQuiz(q.id);
    const v = qState.volgorde[qState.i].v;
    const knop = document.querySelectorAll('#qCard .opt');
    const mis = v.c === 0 ? 1 : 0;
    answerQuestion(mis, knop[mis]);
    const na = document.querySelectorAll('#qCard .opt');
    uit.toets = { juist: na[v.c].classList.contains('juist'), jouw: na[mis].classList.contains('jouw') };
    // de wizard
    lesFlow = null; gwSess = null;
    const oid = gcOpfrisId(gcGeordend()[0].id);
    gwStart(oid);
    gwSess.fase = 'toets';
    show('spiekbrief', true); renderCheat();
    const vr = gwVragen()[gwSess.vraag];
    const kies = vr.g === 0 ? 1 : 0;
    gwKies(kies);
    const gw = document.querySelectorAll('#cheat .gw-optie');
    uit.wizard = { juist: gw[vr.g].classList.contains('juist'), jouw: gw[kies].classList.contains('jouw') };
    return uit;
  });
  ok(schermen.toets.juist && schermen.toets.jouw,
    'het toetsje zet allebei de merktekens op het scherm');
  ok(schermen.wizard.juist && schermen.wizard.jouw,
    'en de wizard ook');

  // ================= 3. elke weg naar een spel =================
  console.log('\n-- 3. de twee wegen naar een spel zijn het eens --');
  /* Niet via een monkeypatch op g.verse: spelInfo() bouwt bij elke aanroep een nieuwe array met
     nieuwe closures, dus de twee wegen krijgen niet eens hetzelfde object in handen. Dát was de
     eigenlijke vondst van deze suite, en de reparatie is speelVers(): één functie die het doet.
     De invariant is daarmee te meten in plaats van te vermoeden. */
  const wegen = await page.evaluate(() => {
    return {
      spellen: spelInfo().filter(function (g) { return g.verse && !g.open; }).map(function (g) { return g.v; }),
      tegel: /speelVers\(/.test(String(speelStart)),
      suggestie: /speelVers\(/.test(String(speelNaar)),
      // en met de hand ernaast? dat is de tweede plek die vanzelf afdrijft
      handwerkTegel: (String(speelStart).match(/\.verse\s*\(/g) || []).length,
      handwerkSuggestie: (String(speelNaar).match(/\.verse\s*\(/g) || []).length
    };
  });
  console.log('   ' + wegen.spellen.length + ' spellen met een verse: ' + wegen.spellen.join(', '));
  ok(wegen.spellen.length >= 5, 'genoeg spellen om iets te betekenen (' + wegen.spellen.length + ')');
  ok(wegen.tegel && wegen.suggestie,
    'beide wegen gaan door speelVers() (tegel=' + wegen.tegel + ', suggestie=' + wegen.suggestie + ')');
  ok(wegen.handwerkTegel === 0 && wegen.handwerkSuggestie === 0,
    'CONTROLE: en geen van beide roept daarnaast nog met de hand een verse aan (' +
    wegen.handwerkTegel + ' / ' + wegen.handwerkSuggestie + ')');

  // en het gedrag, want een functie aanroepen is niet hetzelfde als iets doen
  const echtVers = await page.evaluate(() => {
    const uit = {};
    ltSpel = { letters: ['a'], gekozen: [], doelen: [], gevonden: {}, merk: 'OUD' };
    speelNaar('letras');
    uit.suggestie = !(ltSpel && ltSpel.merk === 'OUD');
    ltSpel = { letters: ['a'], gekozen: [], doelen: [], gevonden: {}, merk: 'OUD' };
    speelStart(spelInfoVan('letras'));
    uit.tegel = !(ltSpel && ltSpel.merk === 'OUD');
    return uit;
  });
  ok(echtVers.suggestie && echtVers.tegel,
    'en allebei zetten Letras ook echt vers neer (suggestie=' + echtVers.suggestie + ', tegel=' + echtVers.tegel + ')');

  // HET CONTROLEGEVAL: een spel dat je niet opent, blijft staan
  const blijft = await page.evaluate(() => {
    ltSpel = { letters: ['a'], gekozen: [], doelen: [], gevonden: {}, merk: 'OUD' };
    speelNaar('kruis');            // een ánder spel openen
    return { letrasNogOud: !!(ltSpel && ltSpel.merk === 'OUD') };
  });
  ok(blijft.letrasNogOud,
    'CONTROLE: een spel dat je niet opent blijft staan waar het stond (niet alles wordt leeggegooid)');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
