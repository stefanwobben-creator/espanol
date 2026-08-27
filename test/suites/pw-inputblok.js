// pw-inputblok.js (20 aug, v23.140) — staat lezen of luisteren ín je les?
//
// WAAROM DIT ER IS
//
// Nation's vier draden (2007): een taalcursus verdeelt zijn tijd ongeveer gelijk over input (lezen,
// luisteren), output (zelf iets maken), taalgerichte studie (woorden, grammatica) en vloeiendheid.
//
// De dagles van Vamos was woordjes, grammatica, toetsje, drie zinnen schrijven: ongeveer 90 procent
// taalgerichte studie. Input stond erachter als opt-in, ná het punt waarop je klaar was, en in
// Stefans logboek van 26 dagen staat "escucha" drie keer.
//
// HET RISICO, MET NAAM
//
// Dit is dezelfde ingreep die v20.5 heeft teruggedraaid ("ik merk dat ik afhaak als dit in de
// verplichte lijst is"). Toen ging het om vijf tot tien zinnen dictado ná het eindpunt; nu om één
// kort stukje vóór het schrijven. Maar het blijft de ingreep waar hij op afhaakte, en daarom
// bewaakt deze suite juist de remmen.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET BLOK ZIT IN DE LES. v23.200: na het toetsje komt eerst het SCHRIJVEN en dan pas lezen of
//      luisteren. Dat is een omkering van v23.140 en geen reparatie: gemeten over Stefans 38 dagen
//      werden de inputblokken 29 keer bereikt en de productieblokken 8 keer, terwijl productie
//      vrijwel dagelijks wordt aangeboden. Het korte blok stond achter het lange te wachten.
//   2. EN IN HET PLAN, VOORAF. Wie op Vandaag kijkt ziet het staan voordat hij begint. Een blok dat
//      halverwege opduikt is precies de verrassing waar je op afhaakt.
//   3. DE APP KIEST. Even dagen lezen, oneven luisteren. Zelf kiezen betekent nooit luisteren.
//   4. IS ER NIETS, DAN IS ER NIETS. Geen open hoofdstuk en geen audio: het blok staat niet in het
//      plan, en de les is gewoon vier stappen. Het plan mag niets beloven wat er niet is.
//   5. JE KOMT ER OOK WEER UIT. Klaar met het hoofdstuk of het gesprek betekent door naar het
//      schrijven, niet stranden in het boekenmenu.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door het blok altijd over te slaan: dan klopt punt 4 en is er niets
// veranderd. Daarom staat punt 1 ertegenover, en wordt gemeten dat de stap er met een normale
// profielstand wél is.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwIn' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    S.dagen = { count: 5 };                       // het plan staat er vanaf dag twee (v23.135)
    S.lesFlow = S.lesFlow || {};

    // ---- 3. de app kiest, en er is altijd iets ----
    uit.keuze = lesFlowInputKeuze();
    uit.audi = typeof audLijst === 'function' ? audLijst().length : -1;
    uit.boek = !!lesFlowBoekHoofdstuk();

    // ---- 2. het blok staat in het plan, vooraf ----
    dagPlanVerval();
    const p = dagPlan();
    uit.stappen = p.stappen.slice();
    const blok = p.blokken.filter(function (b) { return b.stap === 'input'; })[0];
    uit.blok = blok ? { naam: blok.naam, wat: blok.wat, min: blok.min, v: blok.vaardigheid } : null;
    show('lessen', true); renderLessons();
    const kaart = document.querySelector('#tab-lessen .card');
    uit.scherm = kaart ? kaart.textContent.replace(/\s+/g, ' ') : '';

    /* ---- 1. het blok zit in de les ----
       v23.200: na het toetsje komt het schrijven, en het inputblok staat daar weer achter. */
    lesFlowStart();
    lesFlow.stap = 'toetsjes';
    lesFlow.quizzesTeDoen = [];
    lesFlowVolgendeKern();
    uit.naToets = lesFlow ? lesFlow.stap : null;
    uit.naToetsV = lesFlow ? lesFlow.vaardigheid : null;
    uit.zinnen = lesFlow ? lesFlow.vertalenTeGaan : null;

    // ---- 5. en daarna komt het inputblok ----
    lesFlowVolgendeKern();
    uit.naInput = lesFlow ? lesFlow.stap : null;
    uit.naInputV = lesFlow ? lesFlow.vaardigheid : null;
    uit.naam = lesFlowStapNaam();
    uit.num = lesFlowStapNum();
    uit.tot = lesFlowStapTotaal();
    /* v23.200: de vaardigheid wordt genoteerd bij het VERLATEN van het inputblok, en sinds deze
       versie is dat het einde van de les in plaats van de overgang naar het schrijven. Dus nog één
       stap verder voordat we kijken. */
    lesFlowVolgendeKern();
    uit.gedaan = S.lesFlowSpel ? Object.keys(S.lesFlowSpel) : [];

    // ---- 4. is er niets, dan is er niets ----
    const echtBoek = lesFlowBoekHoofdstuk, echtLijst = audLijst;
    lesFlowBoekHoofdstuk = function () { return null; };
    audLijst = function () { return []; };
    uit.leegKeuze = lesFlowInputKeuze();
    dagPlanVerval();
    uit.leegStappen = dagPlan().stappen.slice();
    lesFlow = null;
    lesFlowStart();
    lesFlow.stap = 'toetsjes'; lesFlow.quizzesTeDoen = [];
    lesFlowVolgendeKern();
    uit.leegNaToets = lesFlow ? lesFlow.stap : null;
    lesFlowBoekHoofdstuk = echtBoek; audLijst = echtLijst;
    dagPlanVerval();
    return uit;
  });

  console.log('\n-- 3. de app kiest --');
  console.log('   keuze: ' + r.keuze + ' · audio open: ' + r.audi + ' · hoofdstuk open: ' + r.boek);
  ok(r.keuze === 'lezen' || r.keuze === 'luisteren', 'er is een keuze, en die is lezen of luisteren');

  console.log('\n-- 2. het blok staat in het plan, vooraf --');
  ok(r.stappen.indexOf('input') !== -1, 'het plan kent de stap (nu: ' + JSON.stringify(r.stappen) + ')');
  ok(r.stappen.indexOf('input') > r.stappen.indexOf('toetsjes'), 'en hij staat na het toetsje');
  ok(r.stappen.indexOf('input') > r.stappen.indexOf('produceren'),
     'en ná het schrijven (v23.200: het korte blok wacht niet meer op het lange)');
  ok(r.blok && r.blok.min >= 1, 'met minuten erbij (nu: ' + (r.blok || {}).min + ')');
  ok(r.scherm.indexOf(r.blok ? r.blok.naam : 'zzz') !== -1, 'en het staat op Vandaag voordat je begint');

  console.log('\n-- 1. het blok zit in de les --');
  ok(r.naToets === 'produceren', 'na het toetsje komt het schrijven (nu: ' + r.naToets + ')');
  ok(r.naToetsV === 'schrijven', 'en dat is echt schrijven (nu: ' + r.naToetsV + ')');
  ok(r.zinnen >= 1, 'met zinnen om te maken (nu: ' + r.zinnen + ')');

  console.log('\n-- 5. en daarna het inputblok --');
  ok(r.naInput === 'input', 'daarna komt lezen of luisteren (nu: ' + r.naInput + ')');
  ok(r.naInputV === r.keuze, 'met de vaardigheid van vandaag (nu: ' + r.naInputV + ')');
  ok(/Lezen|Luisteren/.test(r.naam), 'de banner noemt het bij naam (nu: "' + r.naam + '")');
  ok(r.num === r.tot, 'en het is nu de laatste stap (nu: ' + r.num + ' van ' + r.tot + ')');
  ok(r.gedaan.indexOf(r.keuze) !== -1, 'de vaardigheid is als gedaan genoteerd, dus morgen komt de andere');

  console.log('\n-- 4. het controlegeval: is er niets, dan is er niets --');
  ok(r.leegKeuze === null, 'geen boek en geen audio geeft geen keuze (nu: ' + r.leegKeuze + ')');
  ok(r.leegStappen.indexOf('input') === -1, 'dan staat het blok niet in het plan');
  ok(r.leegNaToets === 'produceren', 'en gaat de les gewoon door naar het schrijven (nu: ' + r.leegNaToets + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
