// pw-tweekeuze.js (30 aug, v23.212) — een goed antwoord uit twee knoppen is nog geen doosje
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 30 aug: "grammatica maken en zinnen maken gaat nog niet zo goed."
//
// Gemeten: de 31 concepten van de leermachine maken 153 zinpatronen, waarvan er 101 precies twee
// keuzes geven. Dat is geen slordigheid maar de definitie van het onderwerp: het Nederlands heeft
// één woord waar het Spaans er twee heeft (por/para, es/está, el/la, a of niets). Er is dus ook
// geen derde antwoord om erbij te zetten.
//
// Wat er wél mis was zit niet in de vraag maar in wat de app met het antwoord deed. gramBij()
// verhoogde het doosje bij elk goed antwoord van de dag, of dat nu uit twee knoppen kwam of uit je
// toetsenbord. Gesimuleerd over 90 dagen: een leerling die het onderwerp NIET kent eindigde in 65%
// van de lopen in doosje 3 of hoger, en dat betekent 8 tot 55 dagen rust op iets wat hij niet kan.
//
// DE REGEL DIE DEZE SUITE BEWAAKT
//
//   1. UIT TWEE KNOPPEN IS EEN HALF BEWIJS. Eén goed antwoord laat het doosje staan en zet de
//      herhaling op morgen.
//   2. TWEE HALVE BEWIJZEN OP TWEE DAGEN ZIJN SAMEN EEN DOOSJE. Anders zou de regel geen rem zijn
//      maar een muur.
//   3. CONTROLEGEVAL: drie of meer knoppen, en alles wat je typt, telt gewoon vol. Zonder dit
//      verschil bewijst proef 1 niets: overal remmen haalt hem ook.
//   4. FOUT BLIJFT FOUT. Een half bewijs beschermt niets; het doosje gaat gewoon naar nul.
//   5. EN HET HALVE BEWIJS VERVALT ALS JE HET LATER OP DE DAG ALSNOG MIST. Dezelfde redenering als
//      de dagrem van v23.170: het oordeel van vandaag mag niet omhoog na een fout van vandaag.
//   6. DE WACHTRIJ ZIET HET HALVE BEWIJS ALS SLUITING VAN VANDAAG. Zonder dit blijft een concept
//      met doosje 0 en een fout de hele dag vooraan staan terwijl de dagrem elk verder antwoord
//      toch weggooit: een slot dat op zichzelf dichtklapt.
//   7. EN DE MICROLES KOMT NIET TWEE DAGEN ACHTER ELKAAR op een onderwerp dat je gisteren goed had.
//   8. HET AANTAL KEUZES KOMT UIT DE VRAAG en wordt nergens tweede keer opgeschreven.
//   9. EN ER ZIJN ER ECHT ZOVEEL. Zonder dit getal is de hele ronde een aanname.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);

  /* Elke proef begint bij nul, en "een andere dag" is hier gewoon st.bd terugzetten: dat is precies
     wat de dagrem leest, en morgen afwachten is geen proef. */
  const schoon = () => page.evaluate(() => { S.gram = {}; });
  const dagVerder = (cid) => page.evaluate((c) => { S.gram[c].bd = '2000-01-01'; }, cid);

  // ---- 9. het getal waar de ronde op staat ----
  console.log('\n-- 9. hoeveel patronen geven twee keuzes --');
  const telling = await page.evaluate(() => {
    var totaal = 0, twee = 0;
    GC_CONCEPTEN.forEach(function (c) {
      (c.patronen || []).forEach(function (fn) {
        var maten = {};
        for (var k = 0; k < 25; k++) {
          var q = null; try { q = fn(); } catch (e) {}
          if (q && q.o) maten[q.o.length] = 1;
        }
        totaal++;
        if (maten[2]) twee++;
      });
    });
    return { totaal: totaal, twee: twee, concepten: GC_CONCEPTEN.length };
  });
  console.log('   ' + telling.concepten + ' concepten, ' + telling.totaal + ' patronen, ' +
              telling.twee + ' met twee keuzes');
  ok(telling.twee >= 90, 'de tweekeuzevraag is de hoofdvorm en geen randgeval (' + telling.twee +
     ' van ' + telling.totaal + ')');

  // ---- 8. het aantal keuzes komt uit de vraag ----
  console.log('\n-- 8. de vraag draagt het feit zelf --');
  const doorgeef = await page.evaluate(() => {
    const bron = String(gramAntwoord);
    return { uitVraag: bron.indexOf('q.o) ? q.o.length') !== -1,
             hardgecodeerd: /gramBij\([^)]*,\s*2\s*\)/.test(bron) };
  });
  ok(doorgeef.uitVraag, 'gramAntwoord() leest het aantal knoppen uit de vraag');
  ok(!doorgeef.hardgecodeerd, 'CONTROLE: en schrijft nergens zelf een getal op');

  // ---- 1. uit twee knoppen is een half bewijs ----
  console.log('\n-- 1. één goed antwoord uit twee knoppen --');
  await schoon();
  const half = await page.evaluate(() => {
    gramBij('proef', true, 2);
    const st = S.gram.proef;
    return { box: st.box || 0, half: st.half || 0, due: st.due, morgen: addDays(today(), 1) };
  });
  console.log('   ' + JSON.stringify(half));
  ok(half.box === 0, 'het doosje blijft staan (' + half.box + ')');
  ok(half.half === 1, 'maar het halve bewijs is genoteerd');
  ok(half.due === half.morgen, 'en je ziet het morgen terug, niet over een week (' + half.due + ')');

  // ---- 2. twee halve bewijzen zijn samen een doosje ----
  console.log('\n-- 2. het tweede bewijs, een dag later --');
  await dagVerder('proef');
  const heel = await page.evaluate(() => {
    gramBij('proef', true, 2);
    const st = S.gram.proef;
    return { box: st.box || 0, half: st.half || 0, due: st.due, verwacht: addDays(today(), GRAM_BOX[1]) };
  });
  console.log('   ' + JSON.stringify(heel));
  ok(heel.box === 1, 'nu gaat het doosje wel omhoog (' + heel.box + ')');
  ok(heel.half === 0, 'en de teller staat weer op nul, klaar voor het volgende doosje');
  ok(heel.due === heel.verwacht, 'met de rust die bij doosje 1 hoort (' + heel.due + ')');

  // ---- de hele ladder, want twee stappen zijn nog geen ladder ----
  console.log('\n-- 2b. en zo verder, tot bovenaan --');
  await schoon();
  const ladder = await page.evaluate(() => {
    const uit = [];
    for (let d = 0; d < 12; d++) {
      gramBij('ladder', true, 2);
      uit.push((S.gram.ladder.box || 0) + (S.gram.ladder.half ? '+' : ''));
      S.gram.ladder.bd = '2000-01-0' + (d % 9 + 1);
    }
    return uit;
  });
  console.log('   ' + ladder.join(' → '));
  ok(ladder[11] === '5', 'twaalf goede dagen uit twee knoppen brengen je tot bovenin (' + ladder[11] + ')');
  ok(ladder.filter(function (x) { return x.indexOf('+') !== -1; }).length >= 5,
    'CONTROLE: en er zat elke keer een halve stap tussen, dus dit is echt de nieuwe regel');

  // ---- 3. het controlegeval ----
  console.log('\n-- 3. drie knoppen, en getypt, tellen vol --');
  await schoon();
  const vol = await page.evaluate(() => {
    gramBij('drie', true, 3);
    gramBij('vier', true, 4);
    gramBij('getypt', true);
    gramBij('nul', true, 0);
    return { drie: S.gram.drie.box, vier: S.gram.vier.box,
             getypt: S.gram.getypt.box, nul: S.gram.nul.box };
  });
  console.log('   ' + JSON.stringify(vol));
  ok(vol.drie === 1 && vol.vier === 1,
    'CONTROLE: drie of vier keuzes zetten het doosje meteen op 1 (' + vol.drie + ', ' + vol.vier + ')');
  ok(vol.getypt === 1 && vol.nul === 1,
    'CONTROLE: en een getypt antwoord ook, want daar valt niets te gokken (' + vol.getypt + ')');

  // ---- 4. fout blijft fout ----
  console.log('\n-- 4. een half bewijs beschermt niets --');
  await schoon();
  const mis = await page.evaluate(() => {
    gramBij('mis', true, 2);
    S.gram.mis.bd = '2000-01-01';
    gramBij('mis', false, 2);
    const st = S.gram.mis;
    return { box: st.box || 0, half: st.half || 0, due: st.due, morgen: addDays(today(), 1) };
  });
  console.log('   ' + JSON.stringify(mis));
  ok(mis.box === 0 && mis.half === 0, 'fout zet het doosje op nul en wist het halve bewijs');
  ok(mis.due === mis.morgen, 'en je ziet het morgen terug');

  // ---- 5. later op de dag alsnog mis ----
  console.log('\n-- 5. het halve bewijs vervalt bij een fout van dezelfde dag --');
  await schoon();
  const zelfdeDag = await page.evaluate(() => {
    gramBij('dag', true, 2);
    const na1 = S.gram.dag.half || 0;
    gramBij('dag', false, 2);
    return { na1: na1, half: S.gram.dag.half || 0, box: S.gram.dag.box || 0 };
  });
  console.log('   ' + JSON.stringify(zelfdeDag));
  ok(zelfdeDag.na1 === 1, 'CONTROLE: er lág een half bewijs');
  ok(zelfdeDag.half === 0, 'en na een fout van vandaag is het weg');
  ok(zelfdeDag.box === 0, 'terwijl het doosje van vandaag niet stiekem omhoog gaat (dagrem v23.170)');

  // ---- 6. de wachtrij ----
  console.log('\n-- 6. de wachtrij ziet het halve bewijs als sluiting van vandaag --');
  const rij = await page.evaluate(() => {
    const cid = GC_CONCEPTEN.filter(function (c) { try { return gcConceptOpen(c.id); } catch (e) { return false; } })[0].id;
    S.gram = {};
    gramBij(cid, false, 2);
    const voor = gramWachtrij().map(function (x) { return x.c.id; }).indexOf(cid);
    /* De fout is van gisteren, het goede antwoord van vandaag. Op dezelfde dag zou de dagrem van
       v23.170 het goede antwoord sowieso negeren, en dat is al zo sinds die ronde. */
    S.gram[cid].bd = '2000-01-01';
    gramBij(cid, true, 2);
    const na = gramWachtrij().map(function (x) { return x.c.id; }).indexOf(cid);
    return { cid: cid, voor: voor, na: na, box: S.gram[cid].box || 0, half: S.gram[cid].half || 0 };
  });
  console.log('   ' + JSON.stringify(rij));
  ok(rij.voor === 0, 'CONTROLE: na een fout staat het onderwerp vooraan (plek ' + rij.voor + ')');
  ok(rij.box === 0 && rij.half === 1, 'CONTROLE: en na het goede antwoord staat het doosje nog op nul');
  ok(rij.na === -1, 'toch is het uit de wachtrij van vandaag (plek ' + rij.na + ')');

  // ---- 7. niet twee dagen achter elkaar de hele microles ----
  console.log('\n-- 7. de hele microles komt niet twee keer op hetzelfde --');
  const microles = await page.evaluate(() => {
    const cid = GC_CONCEPTEN.filter(function (c) { try { return gcConceptOpen(c.id); } catch (e) { return false; } })[0].id;
    S.gram = {};
    gramBij(cid, false, 2); S.gram[cid].bd = '2000-01-01';
    gramBij(cid, false, 2);
    const tweeFout = lesFlowGramLijst().slice();
    S.gram[cid].bd = '2000-01-02';
    gramBij(cid, true, 2);
    S.gram[cid].due = today();
    const naGoed = lesFlowGramLijst().slice();
    return { cid: cid, tweeFout: tweeFout, naGoed: naGoed };
  });
  console.log('   twee keer mis : ' + microles.tweeFout.join(', '));
  console.log('   daarna goed   : ' + microles.naGoed.join(', '));
  const kaal = (x) => String(x || '').replace(/^(opfris|concept)-/, '');
  ok(microles.tweeFout.filter((x) => kaal(x) === microles.cid && x.indexOf('opfris-') === 0).length === 0,
    'CONTROLE: na twee fouten is er geen opfrisvraag maar de hele microles');
  ok(microles.naGoed.filter((x) => kaal(x) === microles.cid && x.indexOf('opfris-') === 0).length === 1,
    'na een goed antwoord is het weer een opfrisvraag, ook al staat het doosje nog op nul');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
