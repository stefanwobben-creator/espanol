// pw-praatblok.js (20 aug, v23.150) — kom je nu wel bij het gesprek?
//
// WAAROM DIT ER IS
//
// Stefan, drie keer: "ik kan ook nog niet chatten met chispa."
//
// Het gesprek bestond al sinds v23.144, app en server allebei. Het stond alleen als vierde kaart op
// de Chispa-pagina, en die zit achter Meer. Drie tikken diep, onder de groei- en vitrinekaart.
//
// Dit is dus geen bouwronde maar een verhuizing, en het is de derde keer dezelfde diagnose: lezen
// vóór v23.140, Música vóór v23.148, en nu dit. Wat niet in de dagles staat, bestaat niet.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET IS EEN BLOK IN JE LES. Na het inputblok kom je in het gesprek, niet in het schrijfblok.
//   2. EN HET STAAT VOORAF IN JE PLAN. Met naam en minuten, net als de rest (v23.135).
//   3. OM DE DAG, NIET ELKE DAG. Vertalen en praten doen iets anders en vervangen elkaar niet.
//   4. NIET VANAF DAG ÉÉN. Pas vanaf trede 2 van de zinnenladder. Vrij praten terwijl je nog geen
//      zin kunt maken is geen oefening maar een muur.
//   5. EN JE STAAT NOOIT STIL. Ligt de AI plat, dan is er een knop naar het schrijfblok. Halverwege
//      je les stilstaan is precies waar v20.5 op is teruggedraaid.
//   6. ÉÉN PLEK DIE HET OPENT. Er waren twee takken die allebei het schrijfblok openden; dan krijgt
//      er straks eentje het gesprek niet mee.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door het gesprek altijd te geven: dan klopt punt 1 en zijn 3 en 4
// stuk. Daarom staat tegenover elke "wel" een "niet": niet op een even dag, niet op trede 1, niet
// twee keer op dezelfde dag.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwPb' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    S.chat = null;
    S.vert = { trede: 3, reeks: 0 };          // een eind op weg met de zinnen
    S.dagen = { count: 5 };                   // oneven: praatdag

    // ---- 3 en 4. om de dag, en niet vanaf dag één ----
    const dagen = [];
    for (let d = 1; d <= 8; d++) { S.dagen = { count: d }; if (praatBeurt()) dagen.push(d); }
    uit.praatDagen = dagen;
    S.dagen = { count: 5 };
    uit.opTrede3 = praatBeurt();
    S.vert = { trede: 1, reeks: 0 };
    uit.opTrede1 = praatBeurt();
    uit.tredeMin = PRAAT_TREDE_MIN;
    S.vert = { trede: 3, reeks: 0 };
    // en niet twee keer op dezelfde dag
    S.chat = { d: today(), beurten: [], klaar: true };
    uit.naGesprek = praatBeurt();
    S.chat = null;

    // ---- 2. het staat vooraf in je plan ----
    dagPlanVerval();
    const p = dagPlan();
    const blok = p.blokken.filter(function (b) { return b.stap === 'produceren'; })[0];
    uit.blok = blok ? { naam: blok.naam, wat: blok.wat, min: blok.min, draad: blok.draad } : null;
    show('lessen', true); renderLessons();
    const kaart = document.querySelector('#tab-lessen .card');
    uit.dagscherm = kaart ? kaart.textContent.replace(/\s+/g, ' ') : '';

    // ---- 1. het is een blok in je les ----
    lesFlowStart();
    lesFlow.stap = 'input';
    lesFlow.vaardigheid = 'lezen';
    lesFlowVolgendeKern();
    uit.naInput = { stap: lesFlow.stap, v: lesFlow.vaardigheid, spel: lesFlow.gekozenSpel };
    uit.banner = lesFlowStapNaam();
    uit.chatScherm = document.getElementById('chatWrap').textContent.replace(/\s+/g, ' ');
    uit.chatOpener = chatStand().beurten.length;

    // ---- 5. en je staat nooit stil ----
    renderChat();
    uit.knopZinnen = !!document.getElementById('chatNaarZinnen');
    uit.knopHulp = !!document.getElementById('chatHulp');
    document.getElementById('chatNaarZinnen').click();
    uit.naUitwijk = { stap: lesFlow.stap, v: lesFlow.vaardigheid, spel: lesFlow.gekozenSpel,
                      zinnen: lesFlow.vertalenTeGaan };

    // ---- controlegeval: op een even dag gewoon schrijven ----
    S.chat = null;
    S.dagen = { count: 6 };
    dagPlanVerval();
    const p2 = dagPlan();
    const b2 = p2.blokken.filter(function (b) { return b.stap === 'produceren'; })[0];
    uit.evenBlok = b2 ? b2.naam : null;
    lesFlow = null; lesFlowStart();
    lesFlow.stap = 'input'; lesFlow.vaardigheid = 'lezen';
    lesFlowVolgendeKern();
    uit.evenNaInput = { v: lesFlow.vaardigheid, spel: lesFlow.gekozenSpel };

    // ---- 6. één plek die het opent ----
    uit.eenPlek = typeof lesFlowNaarProduceren === 'function';

    S.chat = null; S.dagen = { count: 5 };
    dagPlanVerval();
    return uit;
  });

  console.log('\n-- 3 en 4. om de dag, en niet vanaf dag één --');
  console.log('   praatdagen van 1 t/m 8: ' + r.praatDagen.join(', '));
  ok(r.praatDagen.length >= 3, 'het gesprek komt meerdere keren langs (' + r.praatDagen.length + 'x in 8 dagen)');
  ok(r.praatDagen.length <= 4, 'het controlegeval: en niet elke dag');
  ok(r.praatDagen.indexOf(1) === -1, 'op dag een niet');
  ok(r.opTrede3, 'op trede 3 van de zinnenladder mag het');
  ok(!r.opTrede1, 'het controlegeval: op trede 1 nog niet (drempel: ' + r.tredeMin + ')');
  ok(!r.naGesprek, 'en niet twee keer op dezelfde dag');

  console.log('\n-- 2. het staat vooraf in je plan --');
  console.log('   ' + JSON.stringify(r.blok));
  ok(r.blok && /Chispa/.test(r.blok.naam), 'het blok heet naar het gesprek (nu: ' + (r.blok || {}).naam + ')');
  ok(r.blok && /\d/.test(r.blok.wat), 'met het aantal beurten erbij (nu: ' + (r.blok || {}).wat + ')');
  ok(r.blok && r.blok.min >= 1, 'en minuten (nu: ' + (r.blok || {}).min + ')');
  ok(r.blok && /zelf maken|output/.test(r.blok.draad), 'het telt als zelf iets maken, net als schrijven');
  ok(r.dagscherm.indexOf(r.blok ? r.blok.naam : 'zzz') !== -1, 'en het staat op Vandaag voordat je begint');

  console.log('\n-- 1. het is een blok in je les --');
  ok(r.naInput.stap === 'produceren', 'na het inputblok kom je in het productieblok');
  ok(r.naInput.v === 'praten', 'en dat is praten (nu: ' + r.naInput.v + ')');
  ok(r.naInput.spel === 'chat', 'het gesprek staat echt open (nu: ' + r.naInput.spel + ')');
  ok(r.banner === 'Praten', 'de banner noemt het bij naam (nu: "' + r.banner + '")');
  ok(r.chatOpener >= 1, 'Chispa is al begonnen, zonder dat er een model aan te pas kwam');
  ok(/Chispa/.test(r.chatScherm), 'en het scherm is echt het gesprek');

  console.log('\n-- 5. en je staat nooit stil --');
  ok(r.knopZinnen, 'er staat een knop naar het schrijfblok');
  ok(r.knopHulp, 'en "hoe zeg ik...?" voor als je vastloopt');
  ok(r.naUitwijk.v === 'schrijven', 'die knop brengt je bij het schrijven (nu: ' + r.naUitwijk.v + ')');
  ok(r.naUitwijk.zinnen >= 1, 'met zinnen om te maken (nu: ' + r.naUitwijk.zinnen + ')');
  ok(r.naUitwijk.stap === 'produceren', 'en je slaat het blok dus niet over');

  console.log('\n-- het controlegeval: op een even dag gewoon schrijven --');
  ok(r.evenBlok && /Schrijven|Writing/.test(r.evenBlok), 'het plan zegt schrijven (nu: ' + r.evenBlok + ')');
  ok(r.evenNaInput.v === 'schrijven', 'en de les gaat naar het schrijven (nu: ' + r.evenNaInput.v + ')');
  ok(r.evenNaInput.spel === 'vertalen', 'met de zinnen (nu: ' + r.evenNaInput.spel + ')');

  console.log('\n-- 6. één plek die het opent --');
  ok(r.eenPlek, 'lesFlowNaarProduceren() bestaat, dus er is één tak en geen twee');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
