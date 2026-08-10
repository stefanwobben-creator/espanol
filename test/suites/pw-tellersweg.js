// Playwright-test voor v19.64: de schuldtellers zijn weg.
//
// Waarom dit een eigen testbestand verdient: een due-teller is het soort ding dat vanzelf
// terugkomt. Hij is makkelijk te bouwen, ziet er behulpzaam uit, en elke leerapp heeft er een. Maar
// hij telt op terwijl je wég bent. Wie na drie weken terugkomt wordt begroet met "83 woordjes te
// doen", en dat is geen informatie maar een rekening. Stefan noemde precies dit als reden om ooit
// te stoppen: "dat ik merk dat het niet vol te houden is, het niet leuk is, te lastig".
//
// Wat hier vastligt:
//   - de badge bovenin bestaat niet meer, in geen enkele toestand van de app
//   - de ritmekaart toont geen "N herhalingen open" en geen "N grammatica-herhalingen open"
//   - het chipje "herhalingen bij" verschijnt alleen als je bíj bent (schouderklopje, geen saldo)
//   - het toetsjesmenu heeft geen "Nog niet gedaan" en geen aantal achter "Tijd voor herhaling"
//   - en, net zo belangrijk: de SRS zelf rekent gewoon door. Verstoppen is niet hetzelfde als
//     afschaffen; de planning moet blijven kloppen, anders is dit geen ontwerpkeuze maar dataverlies.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => {
    if (msg.type() !== 'error') return;
    const t = msg.text();
    if (/Failed to load resource|ERR_TUNNEL|ERR_NAME_NOT_RESOLVED|ERR_INTERNET_DISCONNECTED/.test(t)) return;
    errors.push('console.error: ' + t);
  });

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

  // --- 1. al op het profielkeuzescherm, dus vóór er een profiel is, staat er geen badge ---
  ok(await page.locator('#dueBadge').count() === 0, 'geen #dueBadge op het profielkeuzescherm');

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwTellers' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(600);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // --- 2. de kop van de app ---
  ok(await page.locator('#dueBadge').count() === 0, 'en ook niet zodra je binnen bent');
  const kop = await page.locator('header').innerText();
  ok(!/te doen|to review|fällig|réviser/i.test(kop), 'de koptekst bevat geen te-doen-getal ("' + kop.replace(/\n/g, ' ') + '")');
  // de profielnaam mag natuurlijk cijfers bevatten; het gaat om alles daarbuiten
  const kopRest = await page.evaluate(() => {
    const h = document.querySelector('header').cloneNode(true);
    const naam = h.querySelector('#userName');
    if (naam) naam.remove();
    return h.innerText;
  });
  ok(!/\d/.test(kopRest), 'er staat sowieso geen getal in de kop, los van je naam ("' + kopRest.replace(/\n/g, ' ') + '")');
  ok(await page.locator('#miniPet').count() === 1, 'Chispa staat er nog wel');

  // --- 3. updateBadge() blijft bestaan en mag overal aangeroepen worden zonder te knallen ---
  const badgeFn = await page.evaluate(() => {
    let fout = '';
    try { updateBadge(); updateBadge(); } catch (e) { fout = e.message; }
    return { type: typeof updateBadge, fout: fout, aanroepen: (document.documentElement.innerHTML.match(/updateBadge\(\)/g) || []).length };
  });
  ok(badgeFn.type === 'function', 'updateBadge() bestaat nog als seam voor de dagsessie');
  ok(badgeFn.fout === '', 'en knalt niet nu het element weg is ("' + badgeFn.fout + '")');

  // --- 4. de SRS-boekhouding loopt onder water gewoon door ---
  const srs = await page.evaluate(() => {
    const t = today();
    // bouw een flinke achterstand op: dertig woorden die al lang open staan
    const ids = WORDS.slice(0, 30).map(function (w) { return w.id; });
    ids.forEach(function (id) { S.srs[id] = { box: 2, due: addDays(t, -20), n: 3, f: 0 }; });
    const n = dueCount();
    let over = 0;
    WORDS.forEach(function (w) { const st = S.srs[w.id]; if (st && st.due <= t) over++; });
    return { due: n, over: over, isFn: typeof dueCount === 'function' };
  });
  ok(srs.isFn && srs.due >= 30, 'dueCount() rekent nog gewoon door (' + srs.due + ' open)');
  ok(srs.over >= 30, 'en de woorden staan echt open in S.srs (' + srs.over + ')');

  // --- 5. maar met die achterstand van dertig toont de ritmekaart geen enkel getal daarover ---
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(500);
  // v20.1: de chipjes staan er alleen nog als ze iets zeggen, dus met een vers profiel dat vandaag
  // nog niets deed kan de hele rij ontbreken. Waar het hier om gaat blijft hetzelfde: nergens een
  // saldo van wat je open hebt staan.
  const ritme = await page.evaluate(() => {
    const el = document.querySelector('.ritme');
    return el ? el.innerText : '';
  });
  ok(!/herhalingen open|reviews open/i.test(ritme), 'geen "N herhalingen open" op de ritmekaart ("' + ritme.replace(/\n/g, ' | ') + '")');
  ok(!/herhaling(en)? bij|reviews done/i.test(ritme), 'en met een achterstand ook geen vinkje dat je bij bent');
  ok(!/grammatica-herhaling|grammar review/i.test(ritme), 'geen "N grammatica-herhalingen open"');
  ok(!/🔁/.test(ritme), 'geen herhaal-icoon met een saldo erachter');
  /* v23.31: het dagdoel-chipje op de leskaart is weg. Niet omdat een saldo terugkwam (daar gaat
     deze suite over en dat blijft zo), maar omdat dezelfde stand bovenin al in de strook staat en
     twee weergaven van een getal de fout is die dit scherm aan het opruimen was. Wat hier vanaf nu
     vastligt is precies dat: de stand staat er, en op een plek. */
  const metDoel = await page.evaluate(() => {
    S.xp[today()] = (S.xp[today()] || 0) + 5;
    show('lessen');
    const el = document.querySelector('.ritme');
    return { ritme: el ? el.innerText : '',
             kop: (document.getElementById('goalTxt') || {}).innerText || '' };
  });
  ok(/\d+\/\d+/.test(metDoel.kop),
    'zodra je vandaag punten hebt staat je stand bovenin ("' + metDoel.kop + '")');
  ok(!/dagdoel|daily goal/i.test(metDoel.ritme),
    'en niet ook nog eens als chipje op de leskaart ("' + metDoel.ritme.replace(/\n/g, ' | ') + '")');

  // --- 6. ben je wél bij, dan verschijnt het schouderklopje ---
  const bij = await page.evaluate(() => {
    const t = today();
    WORDS.forEach(function (w) { if (S.srs[w.id]) S.srs[w.id].due = addDays(t, 3); });
    show('lessen');
    return document.querySelector('.ritme').innerText;
  });
  await page.waitForTimeout(300);
  ok(/herhaling(en)? bij|reviews done/i.test(bij), 'wie bij is krijgt "herhalingen bij" te zien ("' + bij.replace(/\n/g, ' | ') + '")');
  ok(!/\bopen\b/i.test(bij), 'en nergens het woord "open"');

  // --- 7. het toetsjesmenu ---
  const toets = await page.evaluate(() => {
    // zet een grammaticatoetsje op "moet herhaald worden" en laat de rest onaangeraakt
    const t = today();
    if (typeof QUIZZES !== 'undefined' && QUIZZES.length) {
      S.quizSrs[QUIZZES[0].id] = { box: 1, due: addDays(t, -5) };
      if (QUIZZES[1]) S.quizSrs[QUIZZES[1].id] = { box: 1, due: addDays(t, -5) };
    }
    scopeLesson = null;
    show('toetsjes');
    return true;
  });
  ok(toets, 'het toetsjesscherm is te openen');
  await page.waitForTimeout(500);
  const qTekst = await page.locator('#tab-toetsjes').innerText();
  ok(!/Nog niet gedaan|Not done yet/i.test(qTekst), 'het kopje "Nog niet gedaan" is weg');
  ok(/Nieuw voor jou|New for you/i.test(qTekst), 'en vervangen door "Nieuw voor jou"');
  const herhaalKop = (qTekst.split('\n').filter(function (r) { return /Tijd voor herhaling|Time to review/i.test(r); })[0] || '');
  ok(herhaalKop !== '', 'de herhaalsectie staat er ("' + herhaalKop + '")');
  ok(!/\d/.test(herhaalKop), 'maar zonder aantal erachter ("' + herhaalKop + '")');

  // --- 8. geen enkel scherm in de dagelijkse route toont nog een openstaand saldo ---
  const schermen = ['lessen', 'toetsjes', 'perfil', 'speeltuin'];
  for (const s of schermen) {
    await page.evaluate((naam) => { scopeLesson = null; show(naam); }, s);
    await page.waitForTimeout(350);
    const tekst = await page.evaluate((naam) => {
      const el = document.getElementById('tab-' + naam);
      return el ? el.innerText : '';
    }, s);
    ok(!/herhalingen open|reviews open|woordjes te doen|words to review/i.test(tekst), 'geen openstaand saldo op "' + s + '"');
  }

  // --- 9. de CSS-haak is ook weg, zodat terugzetten niet één regel HTML is ---
  const stijl = await page.evaluate(() => {
    const uit = [];
    for (const sheet of document.styleSheets) {
      let regels;
      try { regels = sheet.cssRules; } catch (e) { continue; }
      for (const r of regels) if (r.selectorText && /(^|,|\s)\.badge(\s|,|$|:)/.test(r.selectorText)) uit.push(r.selectorText);
    }
    return uit;
  });
  ok(stijl.length === 0, 'de .badge-stijl is opgeruimd (' + stijl.join(', ') + ')');

  ok(errors.length === 0, 'geen JS-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  if (fails) { console.log('\n' + fails + ' TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
