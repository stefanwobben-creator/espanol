// Playwright-test voor v20.5 - de leermachine.
//
// Stefan, 6 augustus, drie klachten in een adem:
//   "ik merk dat ik nu meer de toetsjes automatisch invul omdat ik geleerd heb wat een goede
//    antwoord is (dat is ook zo bij babbel) ipv dat echt het grammaticale concept wordt getest"
//   "drie woordjes is denk ik weinig toch? moet altijd en deel herhaling inzitten maar ook iedere
//    dag nieuwe woordjes"
//   "als je klaar bent met je minimale ja dan wil je een suggestie of meer suggesties waarom een
//    bepaald spel of oefening goed voor je is en alle fouten die maak moeten weer terug, mijn
//    leermachine is"
//
// Deze suite bewaakt de vier antwoorden daarop, in de volgorde waarin ze gebouwd zijn:
//   1. een concept heeft een geheugen (S.gram), gevoed door El Corrector, de toetsjes en de les zelf
//   2. de grammatica van de dag wordt gekozen door je eigen fout, niet door een vaste lijst
//   3. de voorbeelden worden per start gegenereerd, dus het antwoord onthouden kan niet meer
//   4. de les stopt na de toets; wat daarna komt is een voorstel met een reden, en stoppen kan altijd
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);

  await page.fill('input[placeholder="Name"]', 'PwLeer' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(400);

  /* ---------------- 1. het geheugen ---------------- */
  const geheugen = await page.evaluate(() => {
    return { erin: !!S.gram, leeg: Object.keys(S.gram || {}).length === 0, aantal: GC_CONCEPTEN.length };
  });
  ok(geheugen.erin === true, 'S.gram bestaat na een verse start');
  ok(geheugen.leeg === true, 'en hij begint leeg: niets wordt voor je ingevuld');
  ok(geheugen.aantal >= 9, 'er zijn minstens negen concepten (' + geheugen.aantal + ')');

  // El Corrector is de bron die Stefan zelf aanwees ("ik maakte deze fout, neem je dat nu mee?")
  const corr = await page.evaluate(() => {
    S.gram = {};
    corrSrsBij('muymucho', false);
    const st = S.gram.muymucho || {};
    return { fout: st.fout, box: st.box, due: st.due, morgen: addDays(today(), 1) };
  });
  ok(corr.fout === 1, 'een fout in El Corrector komt aan bij het concept muy/mucho');
  ok(corr.box === 0, 'en zet het doosje terug naar nul');
  ok(corr.due === corr.morgen, 'de fout komt morgen terug, niet over een week (' + corr.due + ')');

  // de toetsjes zijn de tweede bron: die kenden hun eigen concept niet
  const quiz = await page.evaluate(() => {
    S.gram = {};
    const qz = QUIZZES.filter((q) => gcConceptenVoorQuiz(q).length)[0];
    if (!qz) return { gevonden: false };
    const cids = gcConceptenVoorQuiz(qz);
    quizSrsBij(qz, 1);
    return { gevonden: true, cids: cids, box: (S.gram[cids[0]] || {}).box };
  });
  ok(quiz.gevonden === true, 'minstens een toetsje is aan een concept te koppelen');
  ok(quiz.box === 1, 'een gehaald toetsje schuift het concept een doosje op');

  // en goed blijven antwoorden schuift hem verder weg, precies volgens GRAM_BOX
  const dozen = await page.evaluate(() => {
    S.gram = {};
    gramBij('serestar', true); gramBij('serestar', true); gramBij('serestar', true);
    const st = S.gram.serestar;
    return { box: st.box, due: st.due, verwacht: addDays(today(), GRAM_BOX[3]) };
  });
  ok(dozen.box === 3, 'drie keer goed is doosje drie');
  ok(dozen.due === dozen.verwacht, 'en dan komt hij pas over ' + 'GRAM_BOX[3]' + ' dagen terug');

  /* ---------------- 2. de keuze volgt je fout ---------------- */
  const keuze = await page.evaluate(() => {
    S.gram = {};
    lesFlow = { stap: null, quizzesTeDoen: [] };
    const zonder = lesFlowGramId();
    corrSrsBij('muymucho', false);
    const met = lesFlowGramId();
    return { zonder: zonder, met: met };
  });
  ok(keuze.met === 'concept-muymucho', 'na die fout gaat de grammatica van vandaag over muy/mucho (' + keuze.met + ')');
  ok(keuze.zonder !== keuze.met, 'zonder fout had hij iets anders gekozen (' + keuze.zonder + ')');

  /* ---------------- 3. de voorbeelden worden gemaakt, niet opgeslagen ---------------- */
  const vers = await page.evaluate(() => {
    const a = gcVernieuw('concept-muymucho').stappen[0].vragen.map((q) => q.v).join('|');
    const b = gcVernieuw('concept-muymucho').stappen[0].vragen.map((q) => q.v).join('|');
    const les = gcOnderwerp('concept-muymucho');
    const vr = les.stappen[0].vragen;
    const stil = gcOnderwerp('concept-muymucho').stappen[0].vragen[1].v === vr[1].v;
    return {
      anders: a !== b,
      aantal: vr.length,
      begripEerst: vr[0].v === gcConcept('muymucho').begrip.v,
      uniek: vr.slice(1).map((q) => q.v).filter((v, i, arr) => arr.indexOf(v) === i).length,
      stil: stil,
      concept: les.concept,
      stappen: les.stappen.length
    };
  });
  ok(vers.anders === true, 'twee keer starten geeft twee keer andere voorbeelden');
  ok(vers.stil === true, 'maar binnen een sessie staat de vraag stil: hij verandert niet onder je handen');
  ok(vers.aantal === 1 + GC_VOORBEELDEN_VERWACHT(), 'een microles is een begripsvraag plus vier voorbeelden (' + vers.aantal + ')');
  ok(vers.begripEerst === true, 'en de eerste vraag gaat over de regel zelf, niet over een zin');
  ok(vers.uniek === vers.aantal - 1, 'de vier voorbeelden zijn onderling verschillend');
  ok(vers.concept === 'muymucho', 'de les weet bij welk concept hij hoort, dus de fout komt terug bij de bron');
  ok(vers.stappen === 1, 'het is een microles: een stap, geen wizard van zes');

  // de derde voeder: fout in de microles zelf
  const inLes = await page.evaluate(() => {
    S.gram = {};
    gwStart('concept-serestar');
    const q = gwOnderwerp(gwSess.id).stappen[0].vragen[0];
    const mis = q.g === 0 ? 1 : 0;
    gwKies(mis);
    const st = S.gram.serestar || {};
    gwSluit();
    return { fout: st.fout, due: st.due, morgen: addDays(today(), 1) };
  });
  ok(inLes.fout === 1, 'een fout in de microles zelf komt ook bij het concept aan');
  ok(inLes.due === inLes.morgen, 'en zet hem net zo goed op morgen');

  /* ---------------- 4. de dagportie ---------------- */
  const portie = await page.evaluate(() => {
    S.doelMin = 10;
    const basis = { nieuw: dagPortieNieuw(), herhaal: dagPortieHerhaal(), cap: dagPortieCap(), vloer: dagPortieVloer() };
    // veel fout: de regelaar mag knijpen, maar niet door de vloer
    S.tempo = null;
    const knijp = (function () {
      const echt = leerKpi;
      leerKpi = function () { return { recent: { pog: 100, pct: 40 } }; };
      const t = tempoVandaag();
      leerKpi = echt;
      return t;
    })();
    // en herstelmodus houdt nieuwe woorden overeind
    S.tempo = null;
    const herstel = (function () {
      const echt = herstelModus;
      herstelModus = function () { return true; };
      const t = tempoVandaag();
      herstelModus = echt;
      return t;
    })();
    S.tempo = null;
    return { basis: basis, knijp: knijp.n, herstel: herstel.n };
  });
  ok(portie.basis.nieuw >= 5, 'bij tien minuten zijn er minstens vijf nieuwe woorden per dag (' + portie.basis.nieuw + ')');
  ok(portie.basis.herhaal >= portie.basis.nieuw, 'en er zit altijd meer herhaling in dan nieuw (' + portie.basis.herhaal + ')');
  ok(portie.basis.cap === portie.basis.nieuw + portie.basis.herhaal, 'de dagportie is precies de som van die twee potten');
  ok(portie.knijp >= portie.basis.vloer, 'bij veel fouten knijpt de regelaar tot de vloer, niet eronder (' + portie.knijp + ')');
  ok(portie.herstel >= 3, 'zelfs in herstelmodus krijg je elke dag nieuwe woorden (' + portie.herstel + ')');

  /* ---------------- 5. de flow stopt na de toets ---------------- */
  const stopt = await page.evaluate(() => {
    S.xp = {}; S.dag = {}; S.ritme = { wanneer: 'stil' }; S.lesFlow = {};
    lesFlow = { stap: 'toetsjes', quizzesTeDoen: [], gekozenSpel: null, vertalenTeGaan: 0 };
    lesFlowVolgende();
    const feest = document.getElementById('feestWrap');
    if (feest && feest.remove) feest.remove();
    return {
      flowWeg: lesFlow === null,
      tekst: document.getElementById('lessonList').innerText
    };
  });
  ok(stopt.flowWeg === true, 'na de toets is de les klaar: geen verplicht dictado-blok meer');
  // let op de /i: de kicker staat in CSS op text-transform, dus innerText leest hem in kapitalen
  ok(/les afgerond|session complete/i.test(stopt.tekst), 'en je krijgt meteen het afgerond-scherm');

  /* ---------------- 6. de voorstellen, met een reden ---------------- */
  const voorstel = await page.evaluate(() => {
    S.gram = {}; S.xp = {}; S.dag = {}; S.ritme = { wanneer: 'stil' }; S.lesFlow = {};
    corrSrsBij('muymucho', false);
    lesFlow = { stap: 'produceren' };
    lesFlowKlaar();
    const feest = document.getElementById('feestWrap');
    if (feest && feest.remove) feest.remove();
    const knoppen = document.querySelectorAll('#lessonList [data-voorstel]');
    const kaarten = [].slice.call(knoppen).map((b) => b.closest('.card').innerText);
    return {
      aantal: knoppen.length,
      kaarten: kaarten,
      eerste: kaarten[0] || '',
      primair: (document.querySelector('#lessonList .card .row button.primary') || {}).textContent || ''
    };
  });
  ok(voorstel.aantal >= 1 && voorstel.aantal <= 2, 'na de les staan er hoogstens twee voorstellen (' + voorstel.aantal + ')');
  ok(/mucho/i.test(voorstel.eerste), 'het eerste voorstel is de fout van net, niet een willekeurig spel');
  ok(/de mist in|wrong/i.test(voorstel.eerste), 'en er staat bij waarom juist dit voorstel (Stefan: "waarom een bepaald spel goed voor je is")');
  ok(voorstel.kaarten.some((k) => /leuk|fun/i.test(k)), 'daarnaast staat er iets wat gewoon leuk is');
  ok(/Klaar voor vandaag|Done for today/.test(voorstel.primair), 'en stoppen blijft de hoofdknop, ook met voorstellen erbij');

  // het voorstel doet ook echt wat het belooft
  const gedrukt = await page.evaluate(() => {
    document.querySelector('#lessonList [data-voorstel]').click();
    return { id: gwSess ? gwSess.id : null };
  });
  ok(gedrukt.id === 'concept-muymucho', 'op het voorstel drukken opent die microles (' + gedrukt.id + ')');

  // en de opt-in op het productieblok bestaat nog, want de oefening zelf was niet het probleem
  const extra = await page.evaluate(() => {
    gwSluit();
    S.lesFlowSpel = {};
    lesFlowExtra('luisteren');
    return { stap: lesFlow.stap, extra: !!lesFlow.extra, v: lesFlow.vaardigheid };
  });
  ok(extra.stap === 'produceren' && extra.extra === true, 'lesFlowExtra() zet het productieblok aan als keuze');
  ok(extra.v === 'luisteren', 'met precies de vaardigheid die je gekozen hebt');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();

function GC_VOORBEELDEN_VERWACHT() { return 4; }
