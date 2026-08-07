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

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
