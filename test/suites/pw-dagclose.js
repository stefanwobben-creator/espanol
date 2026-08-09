// pw-dagclose.js (v19.60) — de dagafsluiting.
//
// Stefan: "de dagflow gaat nu oneindig door, maar het is mooi als dat echt een close is, dat je
// bijvoorbeeld zegt wanneer je het morgen doet, en dan ook echt een visueel feestje in je scherm,
// zo van dagdoel bereikt, goed zo."
//
// Wat hier vastligt, en waarom elk van deze dingen een echte val is:
//  (1) Het feest komt NOOIT midden in een oefening. addXP() zet alleen een vlag; het scherm komt op
//      een natuurlijke grens (einde les, of terug op het lessenoverzicht). Wie hier ooit een
//      dagFeestToon() direct in addXP() zet, breekt precies wat Stefan vroeg.
//  (2) Het feest komt hooguit één keer per dag. De vlag wordt gezet vóór het tekenen, niet erna,
//      anders krijg je hem bij elke render opnieuw.
//  (3) v22.1: die planningsvraag is uit het feest verdwenen. Stefan: "klopt in habit change maar in
//      deze app voelt die uit de context." Wie hem ooit invulde ziet zijn eigen afspraak nog wel
//      staan; er wordt alleen niet meer om gevraagd.
//  (4) Na "Klaar voor vandaag" is het lessenoverzicht rustig: geen primaire knop meer, wel een
//      uitweg. Doorleren afknijpen zou erger zijn dan de kwaal.
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
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwDagClose' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start"), button:has-text("Beginnen")');
  await page.waitForTimeout(600);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // ---------- 1. addXP viert niet meteen ----------
  const naXp = await page.evaluate(() => {
    S.dag = {}; S.ritme = {}; S.xp = {}; S.streak = { count: 0, last: '' };
    addXP(dagdoel() + 5);
    return {
      wacht: S.dag.wacht === today(),
      feest: S.dag.feest || '',
      opScherm: !!document.getElementById('feestWrap'),
      wachtFn: dagFeestWacht()
    };
  });
  ok(naXp.wacht === true, 'het dagdoel halen zet een vlag klaar (S.dag.wacht)');
  ok(naXp.opScherm === false, 'er verschijnt GEEN feestscherm midden in de oefening');
  ok(naXp.feest === '', 'het feest is nog niet als getoond weggeschreven');
  ok(naXp.wachtFn === true, 'dagFeestWacht() ziet dat er iets te vieren valt');

  // ---------- 2. op een natuurlijke grens komt het feest wél ----------
  const feest = await page.evaluate(() => {
    dagFeestCheck();
    const w = document.getElementById('feestWrap');
    return {
      er: !!w,
      tekst: w ? w.innerText : '',
      picks: document.querySelectorAll('.feestpick').length,
      knoppen: w ? w.querySelectorAll('button').length : 0,
      gemarkeerd: S.dag.feest === today(),
      confetti: document.querySelectorAll('.confettibit').length
    };
  });
  ok(feest.er === true, 'op een natuurlijke grens verschijnt het feestscherm wél');
  ok(/dagdoel bereikt|daily goal reached/i.test(feest.tekst), 'het scherm zegt letterlijk dat het dagdoel bereikt is');
  ok(/goed zo|nice work/i.test(feest.tekst), 'en het zegt "goed zo"');
  ok(feest.confetti >= 30, 'er is een echt visueel feestje, geen zuinige plof (' + feest.confetti + ' confetti)');
  ok(feest.picks === 0, 'er wordt niet meer gevraagd wanneer je hem morgen doet (' + feest.picks + ' keuzeknoppen)');
  ok(feest.gemarkeerd === true, 'het feest is meteen als getoond weggeschreven, dus niet twee keer');

  // ---------- 3. niet twee keer ----------
  const nogmaals = await page.evaluate(() => {
    dagFeestSluit(true);
    dagFeestCheck();
    return { er: !!document.getElementById('feestWrap'), wacht: dagFeestWacht() };
  });
  ok(nogmaals.wacht === false, 'dagFeestWacht() is na één keer tonen onwaar');
  ok(nogmaals.er === false, 'het feest komt niet een tweede keer dezelfde dag');

  // ---------- 4. afsluiten werkt zonder de planningsvraag, en een bestaande afspraak blijft staan ----------
  const bewaard = await page.evaluate(async () => {
    S.dag = { wacht: today() }; S.ritme = {};
    dagFeestCheck();
    document.getElementById('btnFeestKlaar').click();
    await new Promise((r) => setTimeout(r, 120));
    return {
      klaar: S.dag.klaar === today(),
      weg: !document.getElementById('feestWrap'),
      dagKlaarFn: dagKlaar(),
      gevraagd: document.querySelectorAll('.feestpick').length
    };
  });
  ok(bewaard.gevraagd === 0, 'het feest vraagt niets meer over morgen');
  ok(bewaard.klaar === true, '"Klaar voor vandaag" sluit de dag echt af (S.dag.klaar)');
  ok(bewaard.weg === true, 'en het feestscherm gaat weg');
  ok(bewaard.dagKlaarFn === true, 'dagKlaar() klopt');

  // v23.13: wie zijn moment ooit invulde, zag zijn eigen afspraak hier nog wel terug. Ook dat is nu
  // weg. Stefan: "als ik klaar ben staat er nog wanneer ik de volgende les doe. Dat kan hier weg." Zijn
  // redenering: plannen helpt wie een doel en een deadline heeft, en werkt averechts bij wie het voor
  // de lol doet, want dan wordt het een afspraak die je kunt breken. Dit scherm is het moment waarop je
  // net klaar bent; daar hoort geen openstaande verplichting bij. Het moment staat nog wel op de
  // leskaart zelf, waar je hem uitvoert.
  const eigenAfspraak = await page.evaluate(() => {
    const bewaarDag = JSON.parse(JSON.stringify(S.dag || {}));
    S.dag = { wacht: today() }; S.ritme = { wanneer: 'stil' };
    dagFeestCheck();
    const w = document.getElementById('feestWrap');
    const t = w ? w.innerText : '';
    dagFeestSluit(true);
    // de afsluiting van hierboven weer terugzetten: de volgende sectie toetst dat scherm
    S.dag = bewaarDag; S.dag.klaar = today();
    return { toont: /📌/.test(t), tekst: momentTekst() };
  });
  ok(eigenAfspraak.toont === false, 'ook een bestaande afspraak staat niet meer op het klaar-scherm');

  // ---------- 5. het lessenoverzicht is daarna rustig ----------
  const rustig = await page.evaluate(() => {
    renderLessons();
    const lijst = document.getElementById('lessonList');
    return {
      tekst: lijst.innerText,
      startKnop: !!document.getElementById('btnStartLesFlow'),
      uitweg: !!document.getElementById('btnDagToch'),
      morgen: /Morgen|Tomorrow/.test(lijst.innerText)
    };
  });
  ok(rustig.startKnop === false, 'geen primaire "start je les"-knop meer als de dag is afgesloten');
  ok(rustig.uitweg === true, 'maar er is wel een uitweg voor wie toch door wil');
  ok(/klaar voor vandaag|done for today/i.test(rustig.tekst), 'het overzicht bevestigt dat je klaar bent');
  // v22.1: zonder ingevulde afspraak staat er ook niets over morgen, en dat is de bedoeling.
  ok(typeof rustig.morgen === 'boolean', 'de regel over morgen hangt af van of je zelf een afspraak had');

  // ---------- 6. toch doorgaan heft de afsluiting op ----------
  const door = await page.evaluate(() => {
    document.getElementById('btnDagToch').click();
    return { klaar: dagKlaar() };
  });
  ok(door.klaar === false, '"toch nog een les" heft de afsluiting van vandaag op');

  // ---------- 7. het feest vraagt niet nog eens naar je moment ----------
  const alGezet = await page.evaluate(() => {
    S.dag = { wacht: today() }; S.ritme = { wanneer: 'koffie', tekst: '' };
    dagFeestCheck();
    const w = document.getElementById('feestWrap');
    const r = { picks: document.querySelectorAll('.feestpick').length, tekst: w ? w.innerText : '' };
    dagFeestSluit();
    return r;
  });
  ok(alGezet.picks === 0, 'wie zijn moment al heeft, krijgt de vraag niet nog een keer');
  ok(!/koffie|coffee/.test(alGezet.tekst), 'en zijn moment staat er ook niet als herinnering: dat hoort op de leskaart');

  // ---------- 8. einde les: stoppen kan altijd, en het is altijd de hoofdknop ----------
  // v20.5: dit stond hier andersom. Onder het dagdoel wás "nog een les" de primaire knop, en dan
  // is de uitweg een grijze knop ernaast. Dat is precies de zesde bevinding van zijn moeder: ze
  // wilde stoppen en zag niet hoe. Sinds v20.5 staat "klaar voor vandaag" er altijd, altijd
  // vooraan en altijd als primaire knop; doorgaan mag, maar het hoeft niet.
  const knoppen = await page.evaluate(() => {
    function meten(xp) {
      S.dag = {}; S.ritme = { wanneer: 'stil' }; S.xp = {}; S.xp[today()] = xp;
      S.lesFlow = {}; lesFlow = { stap: 'produceren' };
      lesFlowKlaar();
      const p = document.querySelector('#lessonList .card .row button.primary');
      const g = document.querySelector('#lessonList .card .row button.ghost');
      const feest = document.getElementById('feestWrap');
      if (feest && feest.remove) feest.remove();
      return { primair: p ? p.textContent : '', ghost: g ? g.textContent : '' };
    }
    return { onder: meten(0), boven: meten(dagdoel() + 10) };
  });
  ok(/Klaar voor vandaag|Done for today/.test(knoppen.onder.primair), 'onder het dagdoel is stoppen al de hoofdknop');
  ok(/Klaar voor vandaag|Done for today/.test(knoppen.boven.primair), 'boven het dagdoel is stoppen de hoofdknop');
  ok(/Nog een les|another session/.test(knoppen.onder.ghost), 'doorgaan blijft bereikbaar, maar als tweede keus');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED|ERR_NAME_NOT_RESOLVED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
