// pw-routedag.js (22 aug, v23.169) — weten je route en je dagles van elkaar?
//
// WAAROM DIT ER IS
//
// Stefan: "de lessen lijken beetje los te staan van de grammatica en lessen die worden opgebouwd,
// hoe verhoudt dit tot elkaar?"
//
// Er lopen drie ladders door de app. De lessen (Cursus) en de grammatica-stap van de dagles zijn
// wél verbonden: lesFlowGramId() vraagt huidigeLes() en pakt een onderwerp uit de spiekbrief van
// precies die les. De routes (GRAM_PADEN, v23.116) staan er los van: je kunt drie weken aan een
// route werken zonder dat je dagles het merkt, en tien lessen doen zonder dat de route opschuift.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE ROUTE STAAT NIET MEER OP JE DAGSCHERM, EN DAT IS EEN BESLUIT.
//      Hier stond: "de route staat op je dagscherm, welke route, welke stap, hoeveel nog te gaan,
//      met een knop." Dat is in v23.169 ingetrokken, op twee gronden die Stefan zelf gaf toen hij
//      de regel voor de dertigste keer las:
//        "dit snap ik niet? waarom zit ik in deze route?" De regel kondigde een route aan zonder
//        enige reden, terwijl de reden al bestond en al op de goede plek stond: gramWaaromHtml()
//        zegt in de les zelf waaróm je dit onderwerp krijgt (v23.143). Aankondigen zonder uitleg
//        wekt de vraag; beantwoorden terwijl je bezig bent is genoeg.
//        "als ik naar route ga kom ik uit mijn dagmodus." De knop bracht je naar de Grammatica-tab.
//        Sinds v23.167 heeft de voorkant van de dag één ding, en dit was er een tweede.
//      Bewust vervangen dus, niet per ongeluk gesneuveld. Wat hier nu staat is de afwezigheid,
//      zodat de regel niet stilletjes terugkomt.
//   2. EN NA JE LES, ALS VOORSTEL. Ná "twee keer dezelfde fout" (dat is een gat dat nu dicht moet)
//      en ná het gesprek met Chispa (v23.144: dat is er één per dag en dan is het op), maar vóór El
//      Corrector: een route is een plan met een eindpunt en dat weegt zwaarder dan een spel.
//   3. HET KLOPT MET DE ROUTE ZELF. De stap die de dagregel noemt is dezelfde die gramPadVolgende()
//      aanwijst, en het aantal is dat van de route. Een tweede plek die zijn eigen route uitrekent
//      is een tweede waarheid.
//   4. IS ER GEEN ROUTE, DAN STAAT ER NIETS. Geen open route, geen regel, geen voorstel.
//   5. NIET OP DAG EEN. Net als het dagplan (v23.135): op dag een is het dagscherm het eerste wat
//      een vreemde ziet, en dan is een route met stapnummers een drempel.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door de regel altijd te tonen: dan klopt punt 1 en is punt 4 stuk.
// Daarom staat er tegenover elke aanwezigheid een afwezigheid: zonder route geen regel, en op dag
// een geen regel.
const { chromium } = require('playwright');
const { VUL } = require('./padvul.js');

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwRt' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(new Function(VUL + `
    const uit = {};
    S.lang = 'nl'; S.speelAlles = true;
    S.conjOpen = CONJ_FASES.length - 1; S.conjFase = CONJ_FASES[CONJ_FASES.length - 1].id;
    S.dagen = { count: 5 };
    const dagkaart = () => {
      show('lessen', true); renderLessons();
      const k = document.querySelector('#tab-lessen .card');
      return k ? k.textContent.replace(/\\s+/g, ' ') : '';
    };

    // ---- 3. het klopt met de route zelf ----
    const p = gramPadNu();
    const i = gramPadVolgende(p);
    const st = routeStand();
    uit.zelfdePad = !!(st && p && st.p.id === p.id);
    uit.zelfdeStap = !!(st && st.i === i);
    uit.titel = st ? st.titel : null;
    uit.stap = st ? st.stap : null;
    uit.open = st ? st.open : null;
    // het aantal moet dat van de route zijn, niet een eigen telling
    let echt = 0;
    for (let j = i; j < p.stappen.length; j++) {
      const x = gramPadStap(p, j);
      if (x.bestaat && !x.af) echt++;
    }
    uit.echtOpen = echt;

    // ---- 1. de route staat NIET op je dagscherm (v23.169) ----
    uit.dag = dagkaart();
    uit.knop = !!document.getElementById('btnRouteDag');
    uit.regelWeg = (typeof routeRegelHtml === 'undefined');

    // ---- 2. en na je les, als voorstel ----
    S.gram = {};                       // geen twee-keer-fout, dus de route hoort bovenaan
    // v23.144: het gesprek met Chispa staat vóór de route (het is er één per dag en dan is het op;
    // een route staat er morgen ook nog). Deze suite gaat over de route, dus we doen alsof je
    // vandaag al gepraat hebt. Dat pw-chat de andere volgorde bewaakt is het punt: samen zeggen ze
    // wat er wanneer bovenaan hoort.
    S.chat = { d: today(), beurten: [], klaar: true };
    const w = lesFlowWinst();
    uit.winstKop = w ? w.kop : null;
    uit.winstIsRoute = !!(w && /route/i.test(w.kop));
    // maar een fout die je twee keer maakte gaat er nog steeds voor
    const cid = (gcLijst()[0] || {}).id;
    if (cid) {
      S.gram[cid.replace(/^concept-/, '')] = { box: 0, goed: 0, fout: 3, due: today(), laatst: today() };
      const w2 = lesFlowWinst();
      uit.metFoutKop = w2 ? w2.kop : null;
      uit.foutGaatVoor = !!(w2 && !/route/i.test(w2.kop));
      S.gram = {};
    } else { uit.foutGaatVoor = 'geen concept om mee te testen'; }

    // ---- 4. geen route, geen voorstel ----
    const echtNu = gramPadNu;
    gramPadNu = function () { return null; };
    uit.leegStand = routeStand();
    uit.leegVoorstel = routeVoorstel();
    uit.leegDag = dagkaart();
    gramPadNu = echtNu;

    // ---- 5. niet op dag een ----
    S.dagen = { count: 1 };
    uit.dag1 = dagkaart();
    S.dagen = { count: 5 };
    return uit;
  `));

  console.log('\n-- 3. het klopt met de route zelf --');
  console.log('   ' + r.titel + ' · nu: ' + r.stap + ' · nog ' + r.open);
  ok(r.zelfdePad, 'de dagregel gaat over dezelfde route als gramPadNu()');
  ok(r.zelfdeStap, 'en over dezelfde stap als gramPadVolgende()');
  ok(r.open === r.echtOpen, 'en telt de stappen van de route, niet een eigen telling (' + r.open + ' vs ' + r.echtOpen + ')');

  console.log('\n-- 1. de route staat NIET op je dagscherm (v23.169) --');
  ok(r.dag.indexOf('Je route') === -1, 'er staat geen routeregel op de leskaart');
  ok(!r.knop, 'en geen knop die je uit je dag naar de Grammatica-tab brengt');
  ok(r.regelWeg, 'routeRegelHtml() bestaat niet meer, dus er is ook niets om per ongeluk terug te zetten');

  console.log('\n-- 2. en na je les, als voorstel --');
  ok(r.winstIsRoute, 'zonder openstaande fout is de route het eerste voorstel ("' + r.winstKop + '")');
  ok(r.foutGaatVoor === true, 'maar twee keer dezelfde fout gaat er nog steeds voor ("' + r.metFoutKop + '")');

  console.log('\n-- 4. het controlegeval: geen route, geen voorstel --');
  ok(r.leegStand === null, 'geen route geeft geen stand');
  ok(r.leegVoorstel === null, 'en dus ook geen voorstel na je les');
  ok(r.leegDag.indexOf('Je route') === -1, 'en niets op het dagscherm');

  console.log('\n-- 5. en op dag een al helemaal niet --');
  ok(r.dag1.indexOf('Je route') === -1, 'op dag een staat de route er niet, net als het dagplan');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
