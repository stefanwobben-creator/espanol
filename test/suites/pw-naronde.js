// Playwright-test voor "En nu?" en de kortere uitleg in de dagles (7 aug, v21.7).
// Stefan: "ik mis nog af en toe een grammaticale toets of vraag en als ik klaar ben krijg ik geen
// suggesties van doe ook dit" en "moeten die [grammaticalessen] nog kleiner?"
// De suggesties bestonden wel, maar alleen aan het eind van de begeleide dagles. Wie de app opent en
// zelf een ronde doet eindigde in het niets, en dat is precies het moment waarop je doorgaat of
// afhaakt. Nu staat er na elke ronde één voorstel, en wordt geteld of erop geklikt wordt: een
// suggestie die niemand gebruikt is geen suggestie maar een drempel voor de afsluitknop.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error' && !/Failed to load resource/.test(msg.text())) errors.push('console.error: ' + msg.text()); });

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
  await page.fill('input[placeholder="Name"]', 'PwNaRonde' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. na een afgeronde ronde staat er één voorstel ----
  await page.evaluate(() => {
    S.speelAlles = true; lesFlow = null;
    S.rvDrill = 1; // v21.8: het eindscherm van de drill, want daar hangt het voorstel aan
    show('speeltuin'); funView = 'conj';
    conjugadorNieuweRonde();
    conjRonde.n = conjRonde.lengte; conjRonde.goed = conjRonde.lengte;
    renderFun();
  });
  await page.waitForTimeout(400);
  ok(await page.locator('.naronde').count() === 1, 'na een Conjugador-ronde staat er een "En nu?"-blok');
  ok(await page.locator('#btnNaRonde').count() === 1, 'met precies één knop, geen keuzemenu');
  const kop = await page.locator('.naronde .kicker').innerText();
  ok(/En nu|And now/i.test(kop), 'het blok heet "En nu?" ("' + kop + '")');

  // ---- 2. het wordt geteld: gezien en geklikt apart ----
  const voor = await page.evaluate(() => ({ gezien: S.voorstelGezien || 0, klik: S.voorstelKlik || 0 }));
  ok(voor.gezien > 0, 'er wordt geteld hoe vaak het voorstel getoond is (' + voor.gezien + ')');
  await page.click('#btnNaRonde');
  await page.waitForTimeout(500);
  const na = await page.evaluate(() => ({ klik: S.voorstelKlik || 0 }));
  ok(na.klik === voor.klik + 1, 'en hoe vaak erop geklikt is (' + na.klik + ')');

  // ---- 3. het voorstel brengt je ergens heen ----
  const verplaatst = await page.evaluate(() => ({
    fun: funView,
    tab: Array.from(document.querySelectorAll('section[id^="tab-"]')).filter((s) => !s.classList.contains('hidden')).map((s) => s.id)
  }));
  ok(verplaatst.tab.length > 0, 'je staat na de tik ergens (' + verplaatst.tab.join(',') + ')');

  // ---- 4. ook na een luisterscene ----
  await page.evaluate(() => {
    lesFlow = null;
    show('speeltuin'); funView = 'audi'; audStop(); audNieuw();
    // rechtstreeks naar het eindscherm: de vragen zelf zijn al gedekt door pw-audicion.js
    audStap = audSc.vragen.length; audGoed = audSc.vragen.length; audGehoord = 1;
    audAfronden();
    renderFunAudicion();
  });
  await page.waitForTimeout(400);
  ok(await page.locator('.naronde').count() === 1, 'ook na een Escuchar-scene staat er een voorstel');

  // ---- 5. in de dagles juist niet: die heeft zijn eigen afsluiting ----
  const inFlow = await page.evaluate(() => {
    lesFlow = { stap: 'produceren', gekozenSpel: 'conj', quizzesTeDoen: [] };
    const h = naRondeHtml();
    lesFlow = null;
    return h;
  });
  ok(inFlow === '', 'binnen de dagles komt het voorstel er niet bij (twee afsluitingen is te veel)');

  // ---- 6. de uitleg is korter in de dagles, en compleet in de leesmodus ----
  const lengtes = await page.evaluate(() => {
    const id = GRAMWIZ[0].id;
    show('spiekbrief');
    lesFlow = null;
    gwStart(id);
    const los = document.getElementById('cheat').innerHTML;
    lesFlow = { stap: 'grammatica' };
    gwStart(id);
    const kort = document.getElementById('cheat').innerHTML;
    lesFlow = null;
    return {
      losLen: (los.match(/<p>/g) || []).length,
      kortZichtbaar: (kort.split('<details')[0].match(/<p>/g) || []).length,
      kortHeeftMeer: /Meer uitleg|More explanation/.test(kort),
      losHeeftDiep: /gwdiep/.test(los)
    };
  });
  ok(lengtes.kortZichtbaar <= lengtes.losLen, 'in de dagles staat er minder in beeld (' + lengtes.kortZichtbaar + ' van ' + lengtes.losLen + ' alinea\'s)');
  ok(lengtes.kortHeeftMeer === true, 'de rest zit achter een "Meer uitleg"-knop');
  ok(lengtes.losHeeftDiep === true, 'in de leesmodus blijft de verdieping gewoon staan');

  // ---- 7. elke conceptles begint met een vraag over de regel zelf ----
  // (bestond al: gcBouw zet begrip vooraan; hier vastgelegd zodat het zo blijft)
  const begrip = await page.evaluate(() => {
    const o = gcOnderwerp('concept-' + GC_CONCEPTEN[0].id);
    const eerste = o.stappen[0].vragen[0];
    return { heeft: !!eerste, vraag: eerste && (eerste.v || eerste.vEn || '') };
  });
  ok(begrip.heeft === true, 'elke conceptles opent met een vraag over de regel zelf ("' + String(begrip.vraag).slice(0, 50) + '")');

  // ---- 8. El Corrector opent zonder te crashen ----
  // v21.7: corrRegelVolgorde() riep shuffleArr() aan, een functie die niet bestaat. Het spel gooide
  // dus een ReferenceError en opende helemaal niet. Gevonden doordat het nieuwe voorstel erheen wees.
  const corr = await page.evaluate(() => {
    try {
      lesFlow = null; S.speelAlles = true;
      show('speeltuin'); funView = 'corr'; corrOpg = null; corrRonde = null;
      renderFun();
      return { ok: true, kaart: !!document.querySelector('#funCard h2') };
    } catch (e) { return { ok: false, fout: String(e.message).slice(0, 90) }; }
  });
  ok(corr.ok === true, 'El Corrector opent zonder fout (' + (corr.fout || '') + ')');
  ok(corr.kaart === true, 'en er staat echt een opgave op het scherm');
  const geschudBestaat = await page.evaluate(() => typeof shuffleArr === 'undefined' && typeof geschud === 'function');
  ok(geschudBestaat === true, 'shuffleArr bestaat niet meer, geschud wel');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  // ---- v23.52: een voorstel wijst nooit naar een gesloten deur, en staat in beeld ----
  // Stefan, telefoontest 11 aug: "als je alles hebt doorlopen, loopt het dood." Het klaar-scherm had
  // wél voorstellen, maar het eerste was El Corrector (doet mee vanaf 8 vrijgespeelde zinnen, een
  // vreemde heeft er 5) en het tweede Escuchar (vanaf 20 woorden, hij had er 3). De poort van v23.43
  // verbergt die tegels, maar deze voorstellen riepen speelNaar() rechtstreeks aan.
  console.log('\n-- v23.52: het voorstel kan ook echt --');
  // De regel testen en niet de toestand: in dit profiel staan die spellen misschien gewoon open.
  // Daarom zetten we de poort zelf even dicht en kijken of de voorstellen dat respecteren.
  const dag1 = await page.evaluate(() => {
    const echt = speelKlaar;
    const uit = {};
    uit.metPoortOpen = lesFlowVoorstellen().map(v => v.kop);
    // eerst: hoe reageert het als corr en audi dicht staan?
    window.speelKlaar = function (v) { return (v === 'corr' || v === 'audi') ? false : echt(v); };
    S.lesFlowSpel = {}; S.gram = {};
    uit.metPoortDicht = lesFlowVoorstellen().map(v => v.kop);
    uit.corrDue = corrDueHaalbaar().length;
    window.speelKlaar = echt;
    return uit;
  });
  console.log('  poort open  ::', dag1.metPoortOpen.join(' · ') || '(niets)');
  console.log('  poort dicht ::', dag1.metPoortDicht.join(' · ') || '(niets)', '· regels op herhaling ::', dag1.corrDue);
  ok(dag1.metPoortDicht.indexOf('El Corrector') === -1,
    'staat El Corrector dicht, dan wordt hij niet voorgesteld (ook al staan er ' + dag1.corrDue + ' regels op herhaling)');
  ok(!dag1.metPoortDicht.some(k => /Escuchar/.test(k)),
    'staat Escuchar dicht, dan wordt hij niet voorgesteld');
  ok(dag1.metPoortDicht.length > 0,
    'er blijft wél iets over om voor te stellen (' + dag1.metPoortDicht.join(', ') + ')');
  ok(await page.evaluate(() => dagSpelKeuze().every(x => speelKlaar(x.v))),
    'en het spel dat wordt voorgesteld voldoet aan zijn eigen eis');

  console.log('\n-- v23.52: het antwoord op "en nu?" staat binnen het scherm --');
  const plek = await page.evaluate(() => {
    S.lesFlow = {}; S.lesFlowEerste = null;   // dag 1: dan is de kaart het langst
    lesFlowKlaar();
    /* v23.58: "En nu?" is geen eigen kaart meer maar een blok bínnen de vieringskaart, boven de
       knoppenrij. Twee kaarten waren twee randen, twee koppen en twee marges, en precies die
       pixels waren nodig om zowel het voorstel als "Klaar voor vandaag" boven de vouw te houden. */
    const kickers = Array.prototype.map.call(document.querySelectorAll('#lessonList .kicker'), k => ({
      tekst: (k.innerText || '').trim(), top: Math.round(k.getBoundingClientRect().top)
    }));
    const knoppen = Array.prototype.map.call(document.querySelectorAll('[data-voorstel]'),
      b => Math.round(b.getBoundingClientRect().top));
    return {
      kickers: kickers, knoppen: knoppen, hoogte: window.innerHeight,
      kaarten: document.querySelectorAll('#lessonList .card').length,
      primair: ((document.querySelector('#lessonList .card button.primary') || {}).innerText || '').trim()
    };
  });
  console.log('  koppen ::', plek.kickers.map(k => k.tekst + '@' + k.top).join(' · '), '· venster', plek.hoogte);
  const enNu = plek.kickers.filter(k => /EN NU|WHAT NOW/i.test(k.tekst))[0];
  ok(!!enNu, 'het blok "En nu?" staat er');
  ok(plek.kaarten === 1, 'en het staat in dezelfde kaart als de viering, niet in een tweede (' + plek.kaarten + ')');
  ok(enNu && enNu.top < plek.hoogte,
    'het begint binnen het scherm (' + (enNu ? enNu.top : '?') + ' van ' + plek.hoogte + ' px)');
  ok(plek.knoppen.length > 0 && plek.knoppen[0] < plek.hoogte,
    'en de eerste voorstelknop ook (' + (plek.knoppen[0] === undefined ? '?' : plek.knoppen[0]) + ')');
  /* v23.58: de primaire knop is het voorstel en niet "Klaar voor vandaag". Zolang de stopknop de
     enige rode knop was, tikte iedereen die, en dan is er geen vervolg. */
  ok(!/Klaar voor vandaag|Done for today/.test(plek.primair),
    'de primaire knop wijst niet naar de uitgang (' + plek.primair + ')');
  ok(plek.knoppen.length >= 1, 'er staat minstens één knop in (' + plek.knoppen.length + ')');

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
