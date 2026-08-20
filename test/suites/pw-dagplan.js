// pw-dagplan.js (19 aug, v23.135) — zie je vooraf wat je les is?
//
// WAAROM DIT ER IS
//
// Op Vandaag stond één regel: "18 woordjes (5 nieuw) · daarna kort: grammatica, een toetsje en
// oefenen · ongeveer 9 min". Drie kwart van de les in zeven woorden, zonder aantallen en zonder
// verdeling. En die minuten werden gerekend als portie.totaal + toetsvragenPerDag() + 8, waarbij
// die 8 een hardgecodeerde handvol beurten was voor grammatica plus oefenen samen.
//
// Eronder zat iets ergers: de stappen van de dagles bestonden nergens als lijst. Vier plekken
// schreven onafhankelijk van elkaar op dat het er vier waren. Is er geen toetsje meer over, dan doe
// je drie stappen terwijl het scherm "stap 3/4" zegt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET PLAN STAAT ER, VOORDAT JE BEGINT. Per blok een naam, wat erin zit en hoeveel minuten.
//   2. EN HET LIEGT NIET. De aantallen komen uit dezelfde functies die de les draaien: dagPortie,
//      toetsvragenPerDag, SCHRIJF_PER_LES. Een plan dat zijn eigen getallen verzint is erger dan
//      geen plan, want je gelooft het.
//   3. GEEN TOETSJE = GEEN TOETSBLOK. Dit is het geval waar de oude "/4" op stukliep. Het plan
//      krimpt mee en het stapnummer telt mee.
//   4. HET PLAN WAAR JE JA OP ZEI REIST MEE. Komt er halverwege je les een toetsje op herhaling te
//      staan, dan blijft "van 4" staan waar het stond. Anders verandert de belofte terwijl je hem
//      aan het nakomen bent.
//   5. DE MINUTEN ZEGGEN WAAR ZE VANDAAN KOMEN. Zonder meting "geschat", met meting "gerekend met
//      jouw tempo". Dat is de erfenis van v23.17: een getal mag hier alleen staan met zijn herkomst
//      erbij.
//   6. HERVATTEN TELT WAT ER OVER IS. "Nog ongeveer 6 min" is het antwoord op de vraag die je dan
//      stelt; "ongeveer 11 min" is dat niet.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door overal nul te tonen: dan klopt "de som van de blokken" en is
// het scherm leeg. Daarom staat er tegenover elke som een ondergrens: er moeten blokken zijn, de
// tijd moet boven nul liggen, en het aantal kaartjes moet echt dat van de portie zijn.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwPlan' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    // v23.135: het plan staat er vanaf dag twee. Op dag een is het dagscherm het eerste wat een
    // vreemde ziet, en dan is een rooster met elf getallen een drempel in plaats van hulp; zie
    // pw-verbouw ("het dagscherm is geen dashboard") en pw-dag1. Deze suite gaat over de dagen
    // daarna, dus we zetten de teller op vijf.
    S.dagen = { count: 5 };
    const tekst = () => {
      show('lessen', true); renderLessons();
      const k = document.querySelector('#tab-lessen .card');
      return k ? k.textContent.replace(/\s+/g, ' ') : '';
    };

    // ---- 1 en 2. het plan staat er en het liegt niet ----
    dagPlanVerval();
    const p = dagPlan();
    uit.blokken = p.blokken.map(function (b) { return { stap: b.stap, naam: b.naam, wat: b.wat, min: b.min, sec: b.sec }; });
    uit.min = p.min;
    uit.sec = p.sec;
    uit.somMin = p.blokken.reduce(function (a, b) { return a + b.min; }, 0);
    uit.portieTotaal = dagPortie().totaal;
    uit.toetsvragen = toetsvragenPerDag();
    uit.schrijfPer = SCHRIJF_PER_LES;
    uit.scherm = tekst();
    uit.totaal = lesFlowStapTotaal();

    // ---- 3. geen toetsje = geen toetsblok ----
    const echteQuizId = lesFlowQuizId;
    lesFlowQuizId = function () { return null; };
    dagPlanVerval();
    const zonder = dagPlan();
    uit.zonderToets = zonder.stappen.slice();
    // Zonder lopende les hoort het totaal het plan van vandaag te volgen. Met een lopende les niet:
    // dan telt het plan waar je ja op zei, en dat is precies wat sectie 4 meet.
    const bewaardeFlow = lesFlow;
    lesFlow = null;
    uit.zonderTotaal = lesFlowStapTotaal();
    lesFlow = bewaardeFlow;
    uit.zonderScherm = tekst();
    lesFlowQuizId = echteQuizId;
    dagPlanVerval();

    // ---- 4. het plan waar je ja op zei reist mee ----
    lesFlowStart();
    uit.inLesTotaal = lesFlowStapTotaal();
    uit.inLesStappen = (lesFlow.stappen || []).slice();
    uit.inLesNum = lesFlowStapNum();
    // het plan van vandaag krimpt onder je handen; de les hoort dat niet te merken
    lesFlowQuizId = function () { return null; };
    dagPlanVerval();
    uit.naKrimpTotaal = lesFlowStapTotaal();
    uit.naKrimpBanner = lesFlowBannerHtml().replace(/\s+/g, ' ');
    // en na bewaren + hervatten nog steeds
    lesFlowBewaar();
    uit.bewaardeStappen = (S.lesFlowNu.stappen || []).slice();
    uit.bewaardTotaal = lesFlowStapTotaal(S.lesFlowNu);
    lesFlowQuizId = echteQuizId;
    dagPlanVerval();

    // ---- 5. de minuten zeggen waar ze vandaan komen ----
    uit.zonderMeting = /geschat/.test(tekst());
    S.dagStats = S.dagStats || {};
    S.dagStats[today()] = { sec: 1200, pogingen: 60, fouten: 5 };   // 20 sec per beurt, gemeten
    dagPlanVerval();
    uit.secPerBeurt = dagSecPerBeurt();
    uit.metMeting = /jouw tempo/.test(tekst());
    const gemeten = dagPlan();
    uit.gemetenMin = gemeten.min;

    // ---- 6. hervatten telt wat er over is ----
    S.lesFlowNu = { d: today(), stap: 'toetsjes', stappen: gemeten.stappen.slice(),
                    quizzesTeDoen: [], gramId: null, vaardigheidRij: [] };
    S.newIntro = S.newIntro || {}; S.newIntro[today()] = 3;   // zodat hervatten mag
    const hv = tekst();
    uit.hervatScherm = hv;
    uit.hervatNog = /Nog ongeveer/.test(hv);
    uit.hervatVink = (hv.match(/✓/g) || []).length;
    // v23.140: het totaal is niet meer vast vier (het inputblok kwam erbij). De bewering gaat over
    // "de stapregel telt uit het bewaarde plan", dus we vergelijken met het bewaarde plan zelf.
    uit.hervatVan = new RegExp('stap 3 van ' + gemeten.stappen.length).test(hv);
    return uit;
  });

  console.log('\n-- 1. het plan staat er, voordat je begint --');
  console.log('   ' + r.blokken.map(function (b) { return b.naam + ' ' + b.wat + ' ' + b.min + 'm'; }).join(' | '));
  ok(r.blokken.length >= 3, 'er staan minstens drie blokken in het plan (nu: ' + r.blokken.length + ')');
  ok(r.sec > 0, 'en er staat een tijd boven nul');
  r.blokken.forEach(function (b) {
    ok(!!b.naam && !!b.wat && b.min >= 1, 'blok "' + b.stap + '" heeft naam, inhoud en minuten');
    ok(r.scherm.indexOf(b.naam) !== -1, 'blok "' + b.naam + '" staat ook echt op het dagscherm');
  });
  ok(/min/.test(r.scherm), 'met minuten erbij');

  console.log('\n-- 2. en het liegt niet --');
  const bWoord = r.blokken.filter(function (b) { return b.stap === 'woorden'; })[0];
  const bToets = r.blokken.filter(function (b) { return b.stap === 'toetsjes'; })[0];
  const bSchr = r.blokken.filter(function (b) { return b.stap === 'produceren'; })[0];
  if (bWoord) ok(bWoord.wat.indexOf(String(r.portieTotaal)) === 0, 'het aantal kaartjes is dat van de dagportie (' + r.portieTotaal + ', op de kaart: ' + bWoord.wat + ')');
  if (bToets) ok(bToets.wat.indexOf(String(r.toetsvragen)) === 0, 'het aantal toetsvragen is toetsvragenPerDag() (' + r.toetsvragen + ')');
  if (bSchr) ok(bSchr.wat.indexOf(String(r.schrijfPer)) === 0, 'het aantal zinnen is SCHRIJF_PER_LES (' + r.schrijfPer + ')');

  console.log('\n-- 3. geen toetsje = geen toetsblok --');
  ok(r.zonderToets.indexOf('toetsjes') === -1, 'het toetsblok verdwijnt uit het plan');
  ok(r.zonderTotaal === r.totaal - 1, 'en het totaal telt mee (' + r.totaal + ' -> ' + r.zonderTotaal + ')');
  ok(r.zonderScherm.indexOf('Toetsje') === -1, 'het staat dan ook niet meer op het scherm');

  console.log('\n-- 4. het plan waar je ja op zei reist mee --');
  ok(r.inLesStappen.length === r.totaal, 'de les neemt het plan mee bij de start (nu: ' + r.inLesStappen.length + ')');
  ok(r.naKrimpTotaal === r.totaal, 'krimpt het plan van vandaag, dan blijft de lopende les even lang (nu: ' + r.naKrimpTotaal + ')');
  ok(new RegExp('/' + r.totaal + ' ').test(r.naKrimpBanner) || r.naKrimpBanner.indexOf('/' + r.totaal) !== -1,
    'en de banner zegt nog steeds /' + r.totaal);
  ok(r.bewaardTotaal === r.totaal, 'na bewaren ook (nu: ' + r.bewaardTotaal + ')');

  console.log('\n-- 5. de minuten zeggen waar ze vandaan komen --');
  ok(r.zonderMeting, 'zonder meting staat er "geschat"');
  ok(r.secPerBeurt === 20, 'met meting rekent hij met jouw seconden per beurt (nu: ' + r.secPerBeurt + ')');
  ok(r.metMeting, 'en dan staat er "gerekend met jouw tempo"');

  console.log('\n-- 6. hervatten telt wat er over is --');
  ok(r.hervatNog, 'de kop zegt hoeveel er nog te gaan is');
  ok(r.hervatVink === 2, 'de twee blokken die je gehad hebt staan afgevinkt (nu: ' + r.hervatVink + ')');
  ok(r.hervatVan, 'en de stapregel telt uit het bewaarde plan');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
