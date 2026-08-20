// pw-gramaf.js (20 aug, v23.143) — maak je een grammatica-onderwerp af, en zie je waarom je het krijgt?
//
// WAAROM DIT ER IS
//
// Stefan: "De grammatica [lijkt] beetje random of niet een heel toetsje maar een deel van de
// grammatica les, dat lijkt raar."
//
// Een conceptles is een stapel van drie tot vijf stappen (v23.107). In je dagles krijg je er één, en
// dat is met opzet. Wat niet met opzet was: lesFlowGramId() koos via gramVersKandidaat(), en die
// filtert op gramAangeraakt(). Eén stap gedaan = aangeraakt = nooit meer het onderwerp van de dag.
// Dus elke dag stap 1 van iets nieuws, nooit stap 2. Je verzamelde beginnetjes.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. AFMAKEN GAAT VOOR BEGINNEN. Is er een onderwerp waarvan stap 1 af is en de rest niet, dan is
//      dat het onderwerp van vandaag, ook al liggen er nog tien nieuwe klaar.
//   2. MAAR AFGERONDE ONDERWERPEN HOUDEN JE NIET VAST. Klaar is klaar: dan komt er weer iets nieuws.
//      Dit is de rem op uithongering, en zonder deze helft is punt 1 een val.
//   3. EN TWEE KEER MIS GAAT NOG STEEDS VOOR ALLES. Een gat dat nu dicht moet is dringender dan een
//      onderwerp afmaken.
//   4. DE LES ZEGT WAAROM JE DIT KRIJGT. Vier redenen, elk afgeleid uit dezelfde toestand waarop
//      gekozen wordt, dus er kan geen tweede waarheid ontstaan.
//   5. EN ALLEEN IN DE DAGLES. Koos je het zelf op de Grammatica-tab, dan is de vraag niet aan de orde.
//   6. HET PLAN ZEGT HOE VER JE BENT. "El of la · stap 2 van 4" in plaats van "1 onderwerp".
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door altijd het onafgemaakte onderwerp te kiezen: dan klopt punt 1
// en is punt 2 stuk (je krijgt nooit meer iets nieuws). Daarom staat er tegenover: zet het onderwerp
// op klaar en de keuze hoort te verspringen.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwGa' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    S.dagen = { count: 5 };
    S.gram = {}; S.gramwiz = {};
    dagPlanVerval();

    // waar zou de les zonder ingreep heen gaan?
    uit.vers = lesFlowGramId();

    // ---- 1. afmaken gaat voor beginnen ----
    // pak een ánder open onderwerp, doe alsof je er één stap van deed, en kijk of de les daarheen gaat
    const open = gcGeordend().filter(function (c) { return gcConceptOpen(c.id); });
    uit.nOpen = open.length;
    const anders = open.filter(function (c) { return 'concept-' + c.id !== uit.vers; })[0];
    uit.anders = anders ? anders.id : null;
    if (anders) {
      const o = gcOnderwerp('concept-' + anders.id);
      uit.andersStappen = o.stappen.length;
      S.gramwiz['concept-' + anders.id] = { stap: 1, klaar: false, rondes: 1 };
      // ook aangeraakt in de gramLees-boekhouding, want zo ziet een echt half onderwerp eruit
      gramBij(anders.id, true);
      uit.naOnaf = lesFlowGramId();
      uit.onafKandidaat = (gcOnafKandidaat(huidigeLes()) || {}).id || null;

      // ---- 4 en 6. de reden, en het plan ----
      uit.redenOnaf = gramWaaromHtml('concept-' + anders.id);
      uit.watOnaf = dagGramWat(['concept-' + anders.id]);
      uit.watTwee = dagGramWat(['opfris-x', 'concept-' + anders.id]);

      // ---- 2. klaar is klaar: het controlegeval ----
      S.gramwiz['concept-' + anders.id] = { stap: o.stappen.length, klaar: true, rondes: 4 };
      uit.naKlaar = lesFlowGramId();
      uit.klaarKandidaat = (gcOnafKandidaat(huidigeLes()) || {}).id || null;
      S.gramwiz = {}; S.gram = {};
    }

    // ---- 3. twee keer mis gaat voor ----
    const cid = (gcLijst()[0] || {}).id;
    uit.cid = cid || null;
    if (cid) {
      const kaal = cid.replace(/^concept-/, '');
      if (anders) S.gramwiz['concept-' + anders.id] = { stap: 1, klaar: false, rondes: 1 };
      S.gram[kaal] = { box: 0, goed: 0, fout: 3, due: today(), laatst: today() };
      uit.naFout = lesFlowGramId();
      uit.redenFout = gramWaaromHtml('concept-' + kaal);
      S.gram = {}; S.gramwiz = {};
    }

    // ---- 4. de andere twee redenen ----
    uit.redenOpfris = gramWaaromHtml('opfris-iets');
    uit.redenRest = gramWaaromHtml(uit.vers);

    // ---- 5. alleen in de dagles ----
    lesFlowStart();
    lesFlow.stap = 'grammatica';
    lesFlow.gramId = uit.vers;
    gwStart(uit.vers);
    const inles = document.createElement('div');
    inles.innerHTML = renderGramWiz();
    uit.inLesReden = inles.textContent.indexOf(uit.redenRest.replace(/<[^>]*>/g, '')) !== -1;
    lesFlow = null;
    const los = document.createElement('div');
    los.innerHTML = renderGramWiz();
    uit.losReden = los.textContent.indexOf(uit.redenRest.replace(/<[^>]*>/g, '')) !== -1;
    gwSess = null;
    return uit;
  });

  console.log('\n-- 1. afmaken gaat voor beginnen --');
  console.log('   vers: ' + r.vers + ' · half af: concept-' + r.anders + ' (' + r.andersStappen + ' stappen)');
  ok(r.nOpen >= 2, 'er staan minstens twee onderwerpen open (' + r.nOpen + ')');
  ok(r.onafKandidaat === r.anders, 'gcOnafKandidaat() vindt het halve onderwerp (' + r.onafKandidaat + ')');
  ok(r.naOnaf === 'concept-' + r.anders, 'en de dagles kiest het, niet iets nieuws (nu: ' + r.naOnaf + ')');

  console.log('\n-- 2. het controlegeval: klaar is klaar --');
  ok(r.klaarKandidaat === null, 'een afgerond onderwerp telt niet meer als onaf');
  ok(r.naKlaar !== 'concept-' + r.anders, 'en de dagles gaat weer naar iets anders (nu: ' + r.naKlaar + ')');

  console.log('\n-- 3. twee keer mis gaat nog steeds voor --');
  ok(r.naFout === r.cid, 'de fout wint van het onafgemaakte onderwerp (nu: ' + r.naFout + ')');

  console.log('\n-- 4. de les zegt waarom je dit krijgt --');
  console.log('   onaf:   ' + r.redenOnaf);
  console.log('   fout:   ' + r.redenFout);
  console.log('   opfris: ' + r.redenOpfris);
  console.log('   rest:   ' + r.redenRest);
  ok(/gebleven/.test(r.redenOnaf), 'half af: "hier was je gebleven"');
  ok(/3 keer mis/.test(r.redenFout), 'twee keer mis: het aantal staat erbij');
  ok(/terug om even op te frissen/.test(r.redenOpfris), 'opfrisser: die zegt dat hij terugkwam');
  ok(r.redenRest.length > 10, 'en anders staat er ook iets ("' + r.redenRest + '")');

  console.log('\n-- 5. en alleen in de dagles --');
  ok(r.inLesReden, 'in de dagles staat de reden op het scherm');
  ok(r.losReden === false, 'buiten de dagles niet: dan koos je het zelf');

  console.log('\n-- 6. het plan zegt hoe ver je bent --');
  console.log('   ' + r.watOnaf + '  |  ' + r.watTwee);
  ok(/stap 2 van /.test(r.watOnaf), 'het blok noemt het onderwerp en de stap (nu: "' + r.watOnaf + '")');
  ok(/^opfrisser \+ /.test(r.watTwee), 'en met een opfrisser erbij staat die er ook (nu: "' + r.watTwee + '")');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
