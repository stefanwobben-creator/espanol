// pw-drill.js (1 sep, v23.225) — is één vraag genoeg bewijs, en komt er iets als het misgaat?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 1 sep: "wat bij de grammatica toetsjes soms wat raar is dat ik maar een vraag krijg, dat
// voelt beetje raar. en ik kreeg een toets met de verschillende tijden voor de werkwoorden, maar die
// was te moeilijk, dus daar zou je nu verwachten dat er een extra los komt."
//
// Het getal eronder: de opfrisser was één vraag met drie knoppen, en een goed antwoord daarop zette
// het doosje een hele stap verder. Van doos 2 naar doos 3 is van drie dagen naar acht. Eén keer
// raden is 33 procent. Dat is dezelfde fout als v23.212, alleen op de as "aantal vragen" in plaats
// van "aantal knoppen".
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE OPFRISSER HEEFT MEER DAN ÉÉN VRAAG, en de drill er meer dan de opfrisser. De getallen
//      komen uit de app (GC_OPFRIS_VRAGEN, GC_DRILL_VRAGEN), niet uit deze suite: een proef die
//      zijn eigen aanname meebrengt kan hem niet weerspreken.
//   2. EEN DRILL BESTAAT, IS VERS, EN WORDT NIET OMGELEID. gwStart() stuurt een afgerond concept
//      door naar de opfrisser; een drill-id mag daar niet in vallen, anders krijg je precies het
//      ene vraagje waar dit over ging.
//   3. DE KNOP STAAT ER ALS ER IETS MISGING, EN NIET ALS ALLES GOED WAS. Dat tweede is het
//      controlegeval en het wordt GEBOUWD: dezelfde stap wordt twee keer nagespeeld, één keer met
//      een fout antwoord en één keer zonder.
//   4. EEN DRILL KAN JE DOOSJE NIET OMHOOG DUWEN. Dat wordt nergens apart afgedwongen en dat is de
//      hele elegantie: gramBij() ziet dat er vandaag een misser was. Vijf goede antwoorden erna
//      veranderen daar niets aan. Oefening, geen herkansing.
//   5. EN DE VRAGEN ZIJN ECHT VERS. Twee keer starten geeft niet twee keer dezelfde vijf vragen,
//      want dan is drillen antwoorden onthouden.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDr' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1. de maten ----
  console.log('\n-- 1. hoeveel vragen --');
  const maten = await page.evaluate(() => {
    const cid = (gcGeordend()[0] || {}).id;
    const opfris = gcVernieuw(gcOpfrisId(cid));
    const drill = gcVernieuw(gcDrillId(cid));
    return {
      cid: cid,
      opfrisConst: GC_OPFRIS_VRAGEN, drillConst: GC_DRILL_VRAGEN,
      opfrisStappen: opfris ? opfris.stappen.length : -1,
      opfris: opfris ? opfris.stappen[0].vragen.length : -1,
      drillStappen: drill ? drill.stappen.length : -1,
      drill: drill ? drill.stappen[0].vragen.length : -1,
      drillConcept: drill ? drill.concept : null,
      drillTitel: drill ? drill.titel : ''
    };
  });
  console.log('   ' + maten.cid + ': opfrisser ' + maten.opfris + ', drill ' + maten.drill);
  ok(maten.opfrisConst >= 2, 'een opfrisser is meer dan één vraag (' + maten.opfrisConst + ')');
  ok(maten.opfris === maten.opfrisConst, 'en de gebouwde opfrisser heeft er ook zoveel');
  ok(maten.opfrisStappen === 1, 'nog steeds één stap: een opfrisser is geen tweede microles');
  ok(maten.drill === maten.drillConst && maten.drillConst > maten.opfrisConst,
    'de drill heeft er meer dan de opfrisser (' + maten.drill + ' tegen ' + maten.opfris + ')');
  ok(maten.drillStappen === 1, 'ook één stap, want het is oefenen en geen les');
  ok(maten.drillConcept === maten.cid, 'en hij hangt aan hetzelfde concept (' + maten.drillConcept + ')');

  // ---- 2. de omleiding ----
  console.log('\n-- 2. een drill wordt niet omgeleid naar de opfrisser --');
  const omleiding = await page.evaluate(() => {
    const cid = (gcGeordend()[0] || {}).id;
    // het concept op "afgerond" zetten: dat is precies de toestand waarin gwStart omleidt
    S.gramwiz = S.gramwiz || {};
    S.gramwiz['concept-' + cid] = { stap: 99, klaar: true, rondes: 3 };
    gwStart('concept-' + cid);
    const naConcept = gwSess ? gwSess.id : null;
    gwStart(gcDrillId(cid), 0);
    const naDrill = gwSess ? gwSess.id : null;
    const n = gwSess ? gwOnderwerp(gwSess.id).stappen[gwSess.stap].vragen.length : -1;
    gwSluit();
    return { naConcept: naConcept, naDrill: naDrill, vragen: n, cid: cid };
  });
  console.log('   ' + JSON.stringify(omleiding));
  ok(/^opfris-/.test(omleiding.naConcept || ''),
    'CONTROLE: een afgerond concept wordt wél omgeleid naar de opfrisser (' + omleiding.naConcept + ')');
  ok(/^drill-/.test(omleiding.naDrill || ''), 'maar een drill blijft een drill (' + omleiding.naDrill + ')');
  ok(omleiding.vragen === maten.drillConst, 'en houdt zijn eigen aantal vragen (' + omleiding.vragen + ')');

  // ---- 3. de knop, met een gebouwd controlegeval ----
  console.log('\n-- 3. de knop staat er als er iets misging --');
  const knop = await page.evaluate(() => {
    const cid = (gcGeordend()[0] || {}).id;
    function speel(allesGoed) {
      gwStart('concept-' + cid, 0);
      const o = gwOnderwerp(gwSess.id);
      const stap = o.stappen[gwSess.stap];
      if (gwSess.fase === 'uitleg') { gwSess.fase = 'toets'; }
      // de stap in het geheugen naspelen: alle vragen beantwoorden, eventueel eentje mis
      const n = stap.vragen.length;
      gwSess.goed = allesGoed ? n : n - 1;
      gwSess.fout = allesGoed ? 0 : 1;
      gwSess.fase = 'stapklaar';
      renderCheat();
      const el = document.getElementById('cheatView') || document.body;
      return { knop: !!document.getElementById('gwDrill'),
               tekst: (el.innerText || '').replace(/\s+/g, ' ').slice(0, 120) };
    }
    const mis = speel(false);
    const perfect = speel(true);
    gwSluit();
    return { mis: mis, perfect: perfect };
  });
  console.log('   met misser: ' + JSON.stringify(knop.mis.knop) + ' · perfect: ' + JSON.stringify(knop.perfect.knop));
  ok(knop.mis.knop, 'na een stap met een misser staat de knop er');
  ok(!knop.perfect.knop, 'CONTROLE: na een perfecte stap staat hij er niet');

  // ---- 4. een drill promoveert niet ----
  console.log('\n-- 4. wat een drill met je doosje doet --');
  const doos = await page.evaluate(() => {
    function dag(vanaf, rij) {
      S.gram = S.gram || {};
      S.gram.proef = { box: vanaf, due: '', goed: 0, fout: 0, laatst: '', bd: '' };
      rij.forEach(function (g) { gramBij('proef', g, 3); });
      return { box: S.gram.proef.box, due: S.gram.proef.due };
    }
    const drillNaMisser = dag(3, [false, true, true, true, true, true]);
    const schoon = dag(3, [true, true, true, true, true]);
    return { drillNaMisser: drillNaMisser, schoon: schoon, morgen: addDays(today(), 1) };
  });
  console.log('   na een misser + vijf goed: doos ' + doos.drillNaMisser.box +
    ' · een schone dag: doos ' + doos.schoon.box);
  ok(doos.drillNaMisser.box === 0, 'vijf goede antwoorden in een drill duwen het doosje niet omhoog');
  ok(doos.drillNaMisser.due === doos.morgen, 'het onderwerp komt gewoon morgen terug');
  ok(doos.schoon.box === 4, 'CONTROLE: zonder die misser klimt dezelfde reeks wél (' + doos.schoon.box + ')');

  // ---- 5. verse vragen ----
  console.log('\n-- 5. twee keer drillen is niet twee keer dezelfde vragen --');
  const vers = await page.evaluate(() => {
    const cid = (gcGeordend()[0] || {}).id;
    function trek() {
      const o = gcVernieuw(gcDrillId(cid));
      return o.stappen[0].vragen.map(function (q) { return q.v || q.vraag || JSON.stringify(q); }).join('|');
    }
    const a = trek(), b = trek(), c = trek();
    return { gelijk: (a === b && b === c), a: a.slice(0, 60) };
  });
  ok(!vers.gelijk, 'drie trekkingen leveren niet drie keer precies hetzelfde op');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
