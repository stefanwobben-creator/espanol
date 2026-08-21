// pw-liedvandaag.js (20 aug, v23.148) — komt het liedje vanzelf, en laat het iets achter?
//
// WAAROM DIT ER IS
//
// Stefan: "musica mag blijven maar dan moet er automatisch een liedje van de dag of om de x dagen
// komen. En de leeroutput moet ook hoger."
//
// Wat een lied opleverde was nul, op het moment na. Veertien liedjes met samen 92 uitgelegde
// uitdrukkingen ("te bloqueé · ik blokkeerde je · indefinido van bloquear, mét de -qué spellingregel
// die je kent van practiqué"), en geen van die 92 kwam ooit terug. Ze waren alleen opzoekbaar.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET KOMT VANZELF, MAAR NIET ELKE DAG. Eens per drie actieve dagen is het inputblok een lied.
//      Een lied is twee keer een stukje hoofdstuk; elke dag zou de andere twee draden verdringen.
//   2. HET IS ÉÉN LIED, OVERAL HETZELFDE. De Música-pagina en het inputblok vragen dezelfde functie.
//      Twee plekken die "het liedje van vandaag" zeggen en een ander lied bedoelen is een tweede
//      waarheid, en dat is de fout waar deze app het meeste last van heeft gehad.
//   3. EN HET IS NIET ELKE KLIK EEN ANDER. Vast per dag, anders betekent de naam niets.
//   4. HET LAAT IETS ACHTER. Klaar met de quiz betekent: de uitdrukkingen staan bij je woorden, en
//      je ziet ze terug. Dit is de leeropbrengst waar het Stefan om ging.
//   5. EN JE KOMT ER WEER UIT. Ook uit het luisterblok, want dat was sinds v23.140 stuk: Escuchar
//      keek nog naar stap "produceren" terwijl de stap "input" heet.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door het lied elke dag te geven: dan klopt punt 1 half en verdringt
// het de rest. Daarom staat er tegenover "op dag 3 wel" een "op dag 4 niet", uit dezelfde functie.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwLd' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    S.musKlaar = {};

    // ---- 1. het komt vanzelf, maar niet elke dag ----
    uit.omDe = MUS_OM_DE;
    const beurten = [];
    for (let d = 1; d <= 9; d++) { S.dagen = { count: d }; beurten.push(musDagBeurt() ? d : null); }
    uit.beurten = beurten.filter(Boolean);

    // ---- 3. en het is niet elke klik een ander ----
    S.dagen = { count: MUS_OM_DE * 2 };
    uit.driekeer = [musVanDag().id, musVanDag().id, musVanDag().id];
    uit.lied = musVanDag().titel;
    uit.oogstN = musVanDag().oogst.length;

    // ---- 2. het is één lied, overal hetzelfde ----
    uit.keuze = lesFlowInputKeuze();
    dagPlanVerval();
    const blok = dagPlan().blokken.filter(function (b) { return b.stap === 'input'; })[0];
    uit.blok = blok ? { naam: blok.naam, wat: blok.wat, min: blok.min } : null;
    show('musica', true); renderSongs();
    const pagina = document.getElementById('songList').textContent.replace(/\s+/g, ' ');
    uit.paginaKop = /liedje van vandaag/i.test(pagina);
    uit.paginaLied = pagina.indexOf(musVanDag().titel) !== -1;

    // ---- 4. het laat iets achter ----
    const sg = musVanDag();
    uit.voor = musOogstOpen(sg).length;
    const woordenVoor = Object.keys(S.srs || {}).length;
    uit.geoogst = musOogstBij(sg);
    uit.na = musOogstOpen(sg).length;
    uit.woordenErbij = Object.keys(S.srs || {}).length - woordenVoor;
    // en het zijn echte kaartjes: ze staan in WORDS, met een doosje en een datum
    const doel = musOogstDoel(sg.oogst[0]);
    uit.inWoorden = WORDS.some(function (w) { return w.id === doel.id; });
    uit.kaart = S.srs[doel.id] ? { box: S.srs[doel.id].box, due: !!S.srs[doel.id].due } : null;
    uit.paar = doel ? { es: doel.es, nl: doel.nl } : null;
    // twee keer oogsten levert niet twee keer dezelfde kaartjes op
    uit.tweedeKeer = musOogstBij(sg);
    uit.gedaan = musGedaan(sg);

    // ---- 5. en je komt er weer uit ----
    lesFlowStart();
    lesFlow.stap = 'toetsjes'; lesFlow.quizzesTeDoen = [];
    lesFlowVolgendeKern();
    uit.stapNaInput = lesFlow.stap;
    uit.vaardigheid = lesFlow.vaardigheid;
    uit.gekozenSpel = lesFlow.gekozenSpel;
    uit.banner = lesFlowStapNaam();
    lesFlowVolgende();
    uit.naLied = lesFlow ? lesFlow.stap : 'klaar';

    S.musKlaar = {};
    dagPlanVerval();
    return uit;
  });

  console.log('\n-- 1. het komt vanzelf, maar niet elke dag --');
  console.log('   dagen met een lied, van dag 1 t/m 9: ' + r.beurten.join(', '));
  ok(r.beurten.length >= 2, 'het lied komt meerdere keren langs (' + r.beurten.length + 'x in 9 dagen)');
  ok(r.beurten.length <= 4, 'het controlegeval: en niet elke dag, anders verdringt het de rest');
  ok(r.beurten.indexOf(1) === -1, 'op dag een niet, net als het dagplan');
  ok(r.beurten.every(function (d) { return d % r.omDe === 0; }), 'precies eens per ' + r.omDe + ' actieve dagen');

  console.log('\n-- 3. en het is niet elke klik een ander --');
  ok(r.driekeer[0] === r.driekeer[1] && r.driekeer[1] === r.driekeer[2],
    'drie keer vragen geeft hetzelfde lied (' + r.lied + ')');

  console.log('\n-- 2. het is één lied, overal hetzelfde --');
  ok(r.keuze === 'musica', 'het inputblok kiest het lied (nu: ' + r.keuze + ')');
  ok(r.blok && r.blok.naam === 'Liedje', 'het plan noemt het blok "Liedje" (nu: ' + (r.blok || {}).naam + ')');
  ok(r.blok && r.blok.wat === r.lied, 'en zet de titel erbij (nu: ' + (r.blok || {}).wat + ')');
  ok(r.blok && r.blok.min >= 1, 'met minuten (nu: ' + (r.blok || {}).min + ')');
  ok(r.paginaKop, 'de Música-pagina heeft een kop "het liedje van vandaag"');
  ok(r.paginaLied, 'en dat is hetzelfde lied als het inputblok kiest');

  console.log('\n-- 4. het laat iets achter --');
  console.log('   "' + (r.paar || {}).es + '" · ' + (r.paar || {}).nl);
  ok(r.voor === r.oogstN, 'vooraf staat er nog niets van dit lied bij je woorden (' + r.voor + ' van ' + r.oogstN + ')');
  ok(r.geoogst === r.oogstN, 'na de quiz staan alle ' + r.oogstN + ' uitdrukkingen erbij (nu: ' + r.geoogst + ')');
  ok(r.woordenErbij === r.oogstN, 'en dat zijn echt evenveel nieuwe kaartjes (' + r.woordenErbij + ')');
  ok(r.inWoorden, 'ze staan in de woordenpoel, dus de kaartjes kunnen ze ophalen');
  ok(r.kaart && r.kaart.box === 0 && r.kaart.due, 'met een doosje en een datum, dus ze komen terug');
  ok(r.na === 0, 'er staat daarna niets meer open');
  ok(r.tweedeKeer === 0, 'het controlegeval: nog een keer oogsten levert geen dubbele kaartjes');
  ok(r.gedaan, 'en het lied telt als gedaan, dus morgen komt er een ander');

  console.log('\n-- 5. en je komt er weer uit --');
  ok(r.stapNaInput === 'input', 'na het toetsje komt het inputblok (nu: ' + r.stapNaInput + ')');
  ok(r.vaardigheid === 'musica', 'met het lied als vaardigheid (nu: ' + r.vaardigheid + ')');
  ok(r.gekozenSpel === 'musica', 'en het lied staat echt open (nu: ' + r.gekozenSpel + ')');
  ok(r.banner === 'Liedje', 'de banner noemt het bij naam (nu: "' + r.banner + '")');
  ok(r.naLied === 'produceren', 'en daarna ga je door naar het schrijven (nu: ' + r.naLied + ')');

  // Escuchar kende de stap "input" niet: dat was de doodlopende weg uit v23.140
  const audi = await page.evaluate(() => {
    lesFlow = { stap: 'input', vaardigheid: 'luisteren', gekozenSpel: 'audi', quizzesTeDoen: [], vaardigheidRij: [] };
    audMenu = true;
    funView = 'audi'; audStop(); audNieuw();
    show('speeltuin', true); renderFun();
    const el = document.getElementById('funCard');
    return { plank: /plank|escuchar/i.test(el.textContent) && !audSc, heeftScene: !!audSc };
  });
  ok(audi.heeftScene, 'in het luisterblok krijg je de scene en niet het menu');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
