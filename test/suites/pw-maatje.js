// Playwright-smoketest voor "iemand die meekijkt" (het maatje, v19.58).
//
// Waarom dit een eigen testbestand heeft: dit is het enige onderdeel van de app waarbij iets van
// de gebruiker naar buiten gaat naar een persoon zonder account. Twee dingen mogen daar nooit
// stilletjes veranderen:
//   (1) de link naar het maatje is NIET de sync-code. De sync-code geeft via /api/state/:code de
//       hele staat terug (antwoorden, fouten, e-mail). Het maatje krijgt een eigen mcode die maar
//       één ding kan: vijf getallen ophalen.
//   (2) het maatje ziet alleen wat er al gebeurd is, nooit wat je van plan bent. Harkin e.a.
//       (Psychological Bulletin 2016) vindt effect bij het rapporteren van gedane dingen;
//       aangekondigde voornemens werken eerder averechts. Het 📌-moment hoort dus niet in dit
//       bericht, en die afwezigheid wordt hier getest.
// Verder: de kaart bestaat uit twee stappen (vragen, dan pas naam invullen), Groepen is de plek
// waar je hem altijd terugvindt en als enige kunt loskoppelen.
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

  const BASIS = 'http://localhost:8321/espanol-stefan.html';
  const KIJK = 'http://localhost:8321/maatje.html';

  // De server zit hier niet in; we onderscheppen /api/maatje/:mcode en geven precies terug wat
  // server/index.js teruggeeft, zodat de pagina op het echte antwoordformaat wordt getest.
  const ANTWOORD = {
    ok: true,
    leerling: 'Stefan',
    maatje: 'Kim',
    streak: 6,
    woorden: 412,
    week: { start: '2026-07-27', dagen: 4, lessen: 5, dagelijks: [true, true, 'iets', true, false, true, false] },
    vorige: { start: '2026-07-20', dagen: 3, lessen: 3, dagelijks: [true, true, true, false, false, false, false] }
  };
  await page.route('**/api/maatje/**', (route) => {
    const url = route.request().url();
    if (/mweg999/.test(url)) return route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ ok: false, error: 'Onbekende link' }) });
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ANTWOORD) });
  });

  // ================= DEEL A: de pagina die het maatje ziet =================

  await page.goto(KIJK + '?m=mtest01');
  await page.waitForTimeout(600);
  const kijk = await page.evaluate(() => ({
    tekst: document.body.innerText,
    bollen: document.querySelectorAll('.bol').length,
    vol: document.querySelectorAll('.bol.vol').length,
    iets: document.querySelectorAll('.bol.iets').length,
    stats: document.querySelectorAll('.stat').length,
    laden: !!document.getElementById('laden'),
    svg: document.querySelectorAll('svg').length,
    opslag: (() => { try { return Object.keys(localStorage).length; } catch (e) { return -1; } })(),
    knoppen: document.querySelectorAll('button, input, textarea, select').length,
    links: Array.prototype.slice.call(document.querySelectorAll('a')).map((a) => a.getAttribute('href'))
  }));
  ok(!kijk.laden, 'de pagina laadt de gegevens en blijft niet op "even ophalen" staan');
  ok(/Stefan/.test(kijk.tekst), 'de naam van de leerling staat erop');
  ok(/4\/7/.test(kijk.tekst), 'het aantal dagen van deze week staat erop');
  ok(kijk.bollen === 7 && kijk.vol === 4 && kijk.iets === 1,
    'zeven dagbollen, vier vol en één half (' + kijk.bollen + '/' + kijk.vol + '/' + kijk.iets + ')');
  ok(kijk.stats === 4 && /6/.test(kijk.tekst) && /412/.test(kijk.tekst), 'streak, lessen, woorden en vorige week staan er');
  ok(/3/.test(kijk.tekst) && /vorige week|last week/i.test(kijk.tekst), 'en de vergelijking met vorige week');
  ok(kijk.svg >= 1, 'Chispa staat erop, zodat het bij de app hoort');

  // Dit zijn de twee beloftes uit de app, hier hard gemaakt.
  ok(!/📌|moment|van plan|plans to|intends/i.test(kijk.tekst),
    'er staat NIETS over voornemens: alleen wat er al gebeurd is');
  // Let op bij het lezen: de woorden "fouten" en "antwoorden" stáán wel op de pagina, in de belofte
  // onderaan. Waar het om gaat is dat er geen enkel gegeven staat dat daarop lijkt.
  ok(/geen fouten|no mistakes/i.test(kijk.tekst), 'de pagina zegt zelf wat het maatje níét ziet');
  ok(!/@/.test(kijk.tekst) && !/\b(hola|gato|casa|el |la )\b/i.test(kijk.tekst),
    'en er staat geen e-mailadres of los Spaans woord op: alleen getallen');
  ok(kijk.knoppen === 0, 'het maatje kan niets terugsturen: geen enkele knop of invoerveld (' + kijk.knoppen + ')');
  ok(kijk.opslag === 0, 'de pagina bewaart niets op het toestel van het maatje (' + kijk.opslag + ')');
  ok(kijk.links.length === 1 && /vamos\.stefanwobben\.nl/.test(kijk.links[0]),
    'één uitgang: de app zelf ("' + kijk.links[0] + '")');
  ok(!/oordeel|helaas|jammer|unfortunately|sadly/i.test(kijk.tekst), 'de toon is nergens veroordelend');

  // minder dan vorige week -> nog steeds vriendelijk
  const zachter = await page.evaluate(() => ({
    minder: vergelijk({ dagen: 1, lessen: 1 }, { dagen: 5, lessen: 5 }),
    gelijk: vergelijk({ dagen: 3, lessen: 3 }, { dagen: 3, lessen: 3 }),
    zonder: vergelijk({ dagen: 2, lessen: 2 }, null)
  }));
  ok(/busy|druk/i.test(zachter.minder), 'een mindere week krijgt begrip, geen tik ("' + zachter.minder + '")');
  ok(zachter.gelijk.length > 0 && zachter.zonder === '', 'gelijk blijven telt als iets; zonder vorige week geen zin');

  // foutpaden
  await page.goto(KIJK);
  await page.waitForTimeout(300);
  const zonderCode = await page.evaluate(() => document.body.innerText);
  ok(/niet compleet|incomplete/i.test(zonderCode), 'een link zonder code geeft een nette melding');

  await page.goto(KIJK + '?m=mweg999');
  await page.waitForTimeout(500);
  const weg = await page.evaluate(() => document.body.innerText);
  ok(/bestaat niet|doesn't exist|Onbekende link/i.test(weg), 'een ingetrokken link ook ("' + weg.slice(0, 40).replace(/\n/g, ' ') + '")');

  // ================= DEEL B: de kant van de leerling =================

  await page.goto(BASIS);
  await page.waitForTimeout(400);
  // de proefles overslaan; die heeft een eigen test en staat hier in de weg
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(BASIS);
  await page.waitForTimeout(600);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwMaatje' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(600);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // --- 1. Niet te vroeg: pas na vier sessies, en pas als de uitnodiging is uitgewerkt ---
  const timing = await page.evaluate(() => {
    S.ritme = { wanneer: 'stil' };
    S.maatje = {};
    const uit = {};
    S.samen = { gedeeld: '2026-01-01', tikken: 2 }; // uitnodiging uitgewerkt
    S.lesFlow = { a: 1, b: 1, c: 1 };
    uit.naDrie = maatjeMoment();
    S.lesFlow = { a: 1, b: 1, c: 1, d: 1 };
    uit.naVier = maatjeMoment();
    S.samen = {}; // uitnodiging leeft nog
    uit.metUitnodiging = maatjeMoment();
    S.samen = { gedeeld: '2026-01-01', tikken: 2 };
    // 12 aug: was '2026-07-29', en de drempel in de app is 21 dagen. Op 12 augustus is dat 14 dagen
    // (goed), op 19 augustus 21 en dan valt deze test om zonder dat er iets is veranderd. Zelfde
    // tijdbom als in pw-samen, die vannacht wél afging. Nu relatief.
    S.maatje = { niet: addDays(today(), -1), overgeslagen: 1 };
    uit.netAfgewezen = maatjeMoment();
    S.maatje = { overgeslagen: 2 };
    uit.tweeKeerWeg = maatjeMoment();
    S.maatje = {};
    return uit;
  });
  ok(!timing.naDrie && timing.naVier, 'de vraag komt na vier sessies, niet eerder');
  ok(!timing.metUitnodiging, 'en niet zolang de uitnodiging nog loopt: één ding tegelijk');
  ok(!timing.netAfgewezen, 'wie net nee zei, wordt drie weken met rust gelaten');
  ok(!timing.tweeKeerWeg, 'en na twee keer wegklikken stopt de app ermee');

  // --- 2. Stap 1: de vraag. Stap 2: pas dan een naam en een voorbeeld ---
  const stappen = await page.evaluate(async () => {
    maatjeStap = 0;
    /* 22 aug, v23.167: het dagscherm heeft een voorkant en een achterkant. Vóór je les staat er
       alleen je les; de maatjeskaart hangt aan samenKaartNu() en die komt pas achter "les af"
       vandaan. Vandaar dat de vierde sessie hieronder die van vandaag is: het blijven vier
       sessies, dus de vraag van maatjeMoment() verandert niet, alleen het moment waarop de kaart
       in beeld staat. */
    S.lesFlow = { a: 1, b: 1, c: 1 };
    S.lesFlow[today()] = 1;
    S.srs = { hola: 1, gato: 1, casa: 1 };
    renderLessons();
    const kaart = document.getElementById('maatjeKaart');
    const eerst = {
      kaart: !!kaart,
      tekst: kaart ? kaart.innerText : '',
      veld: !!document.getElementById('maatjeNaam')
    };
    document.getElementById('btnMaatjeJa').click();
    await new Promise((r) => setTimeout(r, 200));
    const k2 = document.getElementById('maatjeKaart');
    return {
      eerst: eerst,
      tekst: k2 ? k2.innerText : '',
      veld: !!document.getElementById('maatjeNaam'),
      terug: !!document.getElementById('btnMaatjeTerug'),
      stuur: !!document.getElementById('btnMaatjeStuur'),
      voorbeeld: k2 ? !!k2.querySelector('.uitleg') : false
    };
  });
  ok(stappen.eerst.kaart && !stappen.eerst.veld, 'de kaart begint met de vraag, niet met een formulier');
  ok(/👀/.test(stappen.eerst.tekst), 'en gaat over meekijken, niet over meedoen');
  ok(stappen.veld && stappen.stuur && stappen.terug, 'pas na "ja" komt het naamveld, met een weg-terug');
  ok(stappen.voorbeeld, 'met een voorbeeld van wat hij te zien krijgt');
  ok(/3/.test(stappen.tekst), 'en daarin staan je eigen cijfers, niet verzonnen cijfers');
  ok(!/📌/.test(stappen.tekst), 'het 📌-moment staat er nadrukkelijk niet in');

  // --- 3. Versturen: eigen mcode, eigen pagina, nooit de sync-code ---
  const sturen = await page.evaluate(async () => {
    const gebeld = [];
    const echteApi = window.api;
    window.api = function (pad, methode, body) {
      gebeld.push({ pad: pad, body: body });
      if (pad === '/api/maatje/nieuw') return Promise.resolve({ ok: true, maatje: { mcode: 'mabc123', naam: body.naam } });
      return Promise.resolve({ ok: true });
    };
    const gedeeld = [];
    navigator.share = function (d) { gedeeld.push(d); return Promise.resolve(); };
    document.getElementById('maatjeNaam').value = 'Kim';
    document.getElementById('btnMaatjeStuur').click();
    await new Promise((r) => setTimeout(r, 500));
    window.api = echteApi;
    return {
      pad: (gebeld[0] || {}).pad,
      body: (gebeld[0] || {}).body,
      sync: mijnSyncCode(),
      opgeslagen: JSON.parse(JSON.stringify(S.maatje || {})),
      gedeeld: gedeeld.length,
      url: gedeeld[0] ? gedeeld[0].url : '',
      tekst: gedeeld[0] ? gedeeld[0].text : ''
    };
  });
  ok(sturen.pad === '/api/maatje/nieuw', 'versturen maakt een maatje aan op de server');
  ok(sturen.body && sturen.body.naam === 'Kim' && sturen.body.code === sturen.sync,
    'met de naam en je eigen sync-code als afzender');
  ok(sturen.opgeslagen.mcode === 'mabc123' && sturen.opgeslagen.naam === 'Kim', 'de mcode wordt lokaal bewaard');
  ok(sturen.gedeeld === 1 && /maatje\.html\?m=mabc123$/.test(sturen.url),
    'en de link wijst naar de aparte kijkpagina ("' + sturen.url + '")');
  ok(sturen.sync && sturen.url.indexOf(sturen.sync) === -1,
    'de sync-code zit NIET in de link (dat zou de hele staat weggeven)');
  ok(!/\?m=/.test(sturen.tekst), 'en de link wordt niet ook nog eens in de tekst herhaald');

  // --- 4. Het weekbericht: alleen zondag/maandag, één keer per week, en te dempen ---
  const week = await page.evaluate(() => {
    const uit = {};
    // maatjeDeel() heeft hierboven al "deze week verstuurd" gezet; dat eerst opruimen
    delete S.maatje.gestuurd;
    delete S.maatje.stilWeek;
    const echteDag = Date.prototype.getDay;
    Date.prototype.getDay = function () { return 0; }; // zondag
    uit.zondag = maatjeStuurMoment();
    Date.prototype.getDay = function () { return 3; }; // woensdag
    uit.woensdag = maatjeStuurMoment();
    Date.prototype.getDay = function () { return 0; };
    S.maatje.stilWeek = weekIdNu();
    uit.gedempt = maatjeStuurMoment();
    delete S.maatje.stilWeek;
    S.maatje.gestuurd = weekIdNu();
    uit.alGestuurd = maatjeStuurMoment();
    delete S.maatje.gestuurd;
    const h = maatjeStuurKaart();
    Date.prototype.getDay = echteDag;
    uit.kaart = h;
    return uit;
  });
  ok(week.zondag && !week.woensdag, 'het weekbericht wordt op zondag gevraagd, niet doordeweeks');
  ok(!week.gedempt, 'wie deze week niet wil, wordt deze week niet gevraagd');
  ok(!week.alGestuurd, 'en wie al gestuurd heeft ook niet');
  ok(/id='maatjeKaart'/.test(week.kaart) && /btnMaatjeStil/.test(week.kaart),
    'de weekkaart heeft een "niet deze week"-knop');

  // --- 5. Groepen: hier vind je hem altijd terug, en hier kun je hem loskoppelen ---
  const groepen = await page.evaluate(() => {
    show('perfil');
    return {
      slot: !!document.getElementById('maatjeSlot'),
      week: !!document.getElementById('btnMaatjeWeek'),
      weg: !!document.getElementById('btnMaatjeWeg'),
      vraag: !!document.getElementById('btnMaatjeVraag'),
      tekst: document.body.innerText
    };
  });
  ok(groepen.slot && groepen.week && groepen.weg, 'met een maatje staan er in Groepen twee knoppen: sturen en loskoppelen');
  ok(!groepen.vraag, 'en niet ook nog de wervingsvraag');
  ok(/Kim/.test(groepen.tekst), 'de naam van je maatje staat erbij');

  const losgekoppeld = await page.evaluate(async () => {
    const gebeld = [];
    const echteApi = window.api;
    window.api = function (pad, methode, body) { gebeld.push(pad); return Promise.resolve({ ok: true }); };
    const echteConfirm = window.confirm;
    window.confirm = function () { return true; };
    document.getElementById('btnMaatjeWeg').click();
    await new Promise((r) => setTimeout(r, 400));
    window.api = echteApi;
    window.confirm = echteConfirm;
    return {
      pad: gebeld[0],
      leeg: !(S.maatje && S.maatje.mcode),
      vraag: !!document.getElementById('btnMaatjeVraag'),
      week: !!document.getElementById('btnMaatjeWeek')
    };
  });
  ok(losgekoppeld.pad === '/api/maatje/weg', 'loskoppelen trekt de link ook op de server in');
  ok(losgekoppeld.leeg, 'en lokaal is het maatje weg');
  ok(losgekoppeld.vraag && !losgekoppeld.week, 'het scherm slaat meteen om naar "iemand vragen"');

  // --- 6. Vanuit Groepen zelf vragen slaat de vraagstap over ---
  const zelfVragen = await page.evaluate(async () => {
    document.getElementById('btnMaatjeVraag').click();
    await new Promise((r) => setTimeout(r, 200));
    return {
      veld: !!document.getElementById('maatjeNaam'),
      inSlot: !!(document.getElementById('maatjeSlot') || { children: [] }).children.length
    };
  });
  ok(zelfVragen.veld, 'wie er zelf om vraagt, krijgt meteen het naamveld');
  ok(zelfVragen.inSlot, 'en de kaart verschijnt op zijn eigen plek in Groepen');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
