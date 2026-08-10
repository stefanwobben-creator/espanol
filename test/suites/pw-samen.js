// Playwright-smoketest voor "Nodig een vriend uit" (v19.57) + het samen-blok van v19.58.
// Stefan, 30 juli: "qua marktintroductie denk ik dat het 'nodig een vriend uit, samen leren is
// leuker en effectiever' veel prominenter in de flow mag."
// Wat hier vastligt:
//  (1) uitnodigen is één tik: is er nog geen groep, dan maakt de app er zelf een aan.
//  (2) de knop staat op de plekken in de flow waar hij hoort (Lessen, na een les, Speeltuin,
//      Groepen), en niet op dag één.
//  (3) hij verdwijnt zodra je gedeeld hebt of zodra er iemand naast je zit.
//  (4) een ?groep=- of ?duel=-link wordt herkend en het aanmeldscherm zegt waaróm je hier bent.
//  (5) een duel zonder tegenstander heeft een deelknop met een echte link.
// v19.58 erbij:
//  (6) HOOGSTENS ÉÉN VRAAG TEGELIJK. samenKaartNu() is het enige punt dat kiest welke kaart er
//      onder de lessen en na een les staat, in de volgorde moment -> weekbericht -> uitnodiging ->
//      maatje. Dit is de regel die het makkelijkst stilletjes sneuvelt als er ooit een kaart
//      bijkomt, dus hij staat hier expliciet in.
//  (7) het 📌-moment (implementatie-intentie) komt na je eerste afgeronde les, gaat vóór de
//      uitnodiging, en staat daarna elke dag terug te lezen op het lessenoverzicht.
//  (8) de maatje-vraag komt pas als de uitnodiging is uitgewerkt, en nooit tegelijk.
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

  // --- 1. Het aanmeldscherm begroet iemand die via een uitnodigingslink binnenkomt ---
  await page.goto(BASIS + '?groep=abc123');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(BASIS + '?groep=abc123');
  await page.waitForTimeout(600);
  const banner = await page.evaluate(() => {
    const el = document.getElementById('uitnodigBanner');
    return { er: !!el, zichtbaar: el ? !el.classList.contains('hidden') : false, tekst: el ? el.textContent : '', pending: window.pendingGroep };
  });
  ok(banner.er, 'het aanmeldscherm heeft een uitnodigingsbanner');
  ok(banner.zichtbaar, 'die zichtbaar is als je via ?groep= binnenkomt');
  // let op: headless chromium hier draait op navigator.language=en, dus beide talen toestaan
  ok(/uitgenodigd|invited/i.test(banner.tekst), 'en die zegt dat je bent uitgenodigd ("' + banner.tekst.slice(0, 40) + '...")');
  ok(banner.pending === 'abc123', 'de groepscode uit de link is onthouden (' + banner.pending + ')');
  const adres = await page.evaluate(() => location.search);
  ok(adres === '', 'de code is uit de adresbalk gehaald ("' + adres + '")');

  // --- 2. Zonder link geen banner ---
  await page.goto(BASIS + '?duel=zz9');
  await page.waitForTimeout(600);
  const duelBanner = await page.evaluate(() => {
    const el = document.getElementById('uitnodigBanner');
    return { zichtbaar: el && !el.classList.contains('hidden'), tekst: el ? el.textContent : '', pending: window.pendingDuel };
  });
  ok(duelBanner.zichtbaar && /duel/i.test(duelBanner.tekst), 'een ?duel=-link geeft de duel-begroeting');
  ok(duelBanner.pending === 'zz9', 'en de duel-code wordt onthouden');

  await page.goto(BASIS);
  await page.waitForTimeout(500);
  const geenBanner = await page.evaluate(() => {
    const el = document.getElementById('uitnodigBanner');
    return el ? el.classList.contains('hidden') : false;
  });
  ok(geenBanner, 'zonder link staat de banner verstopt');

  // profiel aanmaken
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwSamen' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(600);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // --- 3. Dag één gaat over Spaans, niet over vrienden ---
  const dagEen = await page.evaluate(() => {
    S.lesFlow = {};
    S.samen = {};
    S.ritme = {};
    S.maatje = {};
    renderLessons();
    return {
      kaart: !!document.getElementById('uitnodigKaart'),
      moment: uitnodigMoment(2),
      momentKaart: !!document.getElementById('momentKaart'),
      maatje: !!document.getElementById('maatjeKaart'),
      sessies: samenSessies()
    };
  });
  ok(dagEen.sessies === 0, 'verse gebruiker heeft nul afgeronde sessies');
  ok(!dagEen.moment && !dagEen.kaart, 'en krijgt dus nog geen uitnodigingskaart op het lessenoverzicht');
  ok(!dagEen.momentKaart && !dagEen.maatje, 'en ook geen moment- of maatjekaart: dag één gaat over Spaans');

  // --- 3b. v22.1: de momentkaart is opgeheven ---
  // Stefan: "de wanneer doe je de les is leuk en klopt in habit change maar in deze app voelt die
  // uit de context." Een implementatie-intentie werkt als hij bij een besluit hoort dat je net
  // genomen hebt, niet als losse planningsvraag na een oefening. Wat hier telt is dat zijn plek in
  // de rij nu doorschuift naar de uitnodiging, en niet leeg blijft.
  const naEen = await page.evaluate(() => {
    S.lesFlow = { '2026-07-29': true };
    S.samen = {};
    S.ritme = {};
    S.maatje = {};
    renderLessons();
    return {
      moment: !!document.getElementById('momentKaart'),
      knoppen: document.querySelectorAll('.momentpick').length,
      kaartHtml: samenKaartNu(false)
    };
  });
  ok(naEen.moment === false, 'de momentkaart staat er niet meer');
  ok(naEen.knoppen === 0, 'en er staan geen keuzemomenten meer op het scherm');
  ok(naEen.kaartHtml.indexOf('momentKaart') === -1, 'samenKaartNu() biedt hem ook niet meer aan');

  // --- 4. Vanaf de tweede sessie staat de uitnodiging er, direct onder de dagkaart ---
  const naTwee = await page.evaluate(() => {
    S.lesFlow = { '2026-07-28': true, '2026-07-29': true };
    S.ritme = { wanneer: 'stil' }; // moment is al gezet, dus die kaart claimt de plek niet meer
    S.maatje = {};
    renderLessons();
    const kaart = document.getElementById('uitnodigKaart');
    const lijst = document.getElementById('lessonList');
    const kinderen = lijst ? Array.prototype.slice.call(lijst.children) : [];
    return {
      kaart: !!kaart,
      knop: !!document.getElementById('btnUitnodig'),
      positie: kaart ? kinderen.indexOf(kaart) : -1,
      tekst: kaart ? kaart.innerText : '',
      moment: !!document.getElementById('momentKaart'),
      maatje: !!document.getElementById('maatjeKaart')
    };
  });
  ok(naTwee.kaart && naTwee.knop, 'na twee sessies staat de uitnodigingskaart op het lessenoverzicht');
  ok(naTwee.positie === 1, 'en wel als tweede kaart, direct onder de dagkaart (positie ' + naTwee.positie + ')');
  ok(/nooit elkaars fouten|never each other's mistakes/i.test(naTwee.tekst), 'de kaart vertelt wat je vriend wel en niet ziet');
  ok(!naTwee.moment && !naTwee.maatje, 'en staat er alléén: geen tweede kaart eronder');

  // --- 5. Hij verdwijnt zodra je gedeeld hebt, en zodra er iemand naast je zit ---
  const stil = await page.evaluate(() => {
    S.samen = { gedeeld: '2026-07-29' };
    renderLessons();
    const na = !!document.getElementById('uitnodigKaart');
    S.samen = { gezien: '2026-07-29' };
    renderLessons();
    const metVriend = !!document.getElementById('uitnodigKaart');
    S.samen = {};
    return { na: na, metVriend: metVriend };
  });
  ok(!stil.na, 'wie al gedeeld heeft, wordt niet nog eens gevraagd');
  ok(!stil.metVriend, 'en wie al iemand naast zich heeft ook niet');

  // --- 6. Eén tik: geen groep? dan maakt de app er zelf een aan ---
  const eenTik = await page.evaluate(async () => {
    const gebeld = [];
    const echteApi = window.api;
    window.api = function (pad, methode, body) {
      gebeld.push({ pad: pad, body: body });
      if (pad === '/api/groep/nieuw') return Promise.resolve({ ok: true, groep: { gcode: 'gtest99', naam: body.naam } });
      return Promise.resolve({ ok: true });
    };
    const gedeeld = [];
    navigator.share = function (d) { gedeeld.push(d); return Promise.resolve(); };
    S.groepen = [];
    S.samen = {};
    S.tapas = 10;
    S.lesFlow = { a: true, b: true };
    renderLessons();
    document.getElementById('btnUitnodig').click();
    await new Promise(function (r) { setTimeout(r, 400); });
    window.api = echteApi;
    return {
      nieuw: gebeld.filter(function (g) { return g.pad === '/api/groep/nieuw'; }).length,
      naam: (gebeld.filter(function (g) { return g.pad === '/api/groep/nieuw'; })[0] || { body: {} }).body.naam,
      groepen: (S.groepen || []).length,
      gedeeld: gedeeld.length,
      url: gedeeld[0] ? gedeeld[0].url : '',
      tekst: gedeeld[0] ? gedeeld[0].text : '',
      tapas: S.tapas,
      gemarkeerd: !!S.samen.gedeeld
    };
  });
  ok(eenTik.nieuw === 1, 'één tik maakt precies één groep aan (' + eenTik.nieuw + ')');
  ok(/PwSamen/.test(eenTik.naam || ''), 'met je eigen naam erin ("' + eenTik.naam + '")');
  ok(eenTik.groepen === 1, 'en die groep wordt lokaal bewaard');
  ok(eenTik.gedeeld === 1, 'daarna gaat het deelvenster van het toestel open');
  ok(/\?groep=gtest99$/.test(eenTik.url), 'met de uitnodigingslink erin ("' + eenTik.url + '")');
  ok(/PwSamen/.test(eenTik.tekst) && !/\?groep=/.test(eenTik.tekst), 'de tekst noemt je naam en herhaalt de link niet');
  // v19.58: de beloning is omgedraaid. Betalen voor het versturen beloont de handeling die je
  // niet wilt (linkjes rondstrooien); betalen voor de aankomst beloont wat je wél wilt.
  ok(eenTik.tapas === 10, 'het versturen zelf levert géén tapas op (' + eenTik.tapas + ')');
  ok(eenTik.gemarkeerd, 'maar het wordt wel onthouden, zodat de vraag stopt');

  // --- 7. De beloning komt pas als er iemand aankomt, en precies één keer ---
  const aangekomen = await page.evaluate(async () => {
    const was = S.tapas;
    samenAangekomen([{ naam: 'PwVriendin' }, { naam: 'Iemand anders' }]);
    const na = S.tapas;
    samenAangekomen([{ naam: 'PwVriendin' }, { naam: 'Iemand anders' }]);
    return { was: was, na: na, nogEens: S.tapas, gezien: !!S.samen.gezien, beloond: !!S.samen.beloond };
  });
  ok(aangekomen.na === aangekomen.was + 5, 'er komt iemand aan: +5 tapas (' + aangekomen.was + ' -> ' + aangekomen.na + ')');
  ok(aangekomen.nogEens === aangekomen.na, 'en een tweede keer kijken levert niets extra op');
  ok(aangekomen.gezien && aangekomen.beloond, 'de aankomst wordt vastgelegd');

  // --- 7b. Wie zelf nooit uitnodigde, krijgt die tapas niet ---
  const zonderUitnodiging = await page.evaluate(() => {
    S.samen = {};
    const was = S.tapas;
    samenAangekomen([{ naam: 'PwVriendin' }, { naam: 'Iemand anders' }]);
    return { was: was, nu: S.tapas, gezien: !!S.samen.gezien };
  });
  ok(zonderUitnodiging.nu === zonderUitnodiging.was, 'zonder eigen uitnodiging geen aankomstbonus');
  ok(zonderUitnodiging.gezien, 'maar er zit wel iemand naast je, dus de vraag stopt');

  // --- 7c. Nog een keer delen kan gewoon, zonder tweede beloning ---
  const nogEens = await page.evaluate(async () => {
    const gedeeld = [];
    navigator.share = function (d) { gedeeld.push(d); return Promise.resolve(); };
    S.samen = { gedeeld: '2026-07-01', tikken: 1 };
    const was = S.tapas;
    uitnodigNu('test');
    await new Promise(function (r) { setTimeout(r, 300); });
    return { was: was, nu: S.tapas, gedeeld: gedeeld.length, tikken: S.samen.tikken };
  });
  ok(nogEens.gedeeld === 1, 'nog een keer delen kan gewoon');
  ok(nogEens.nu === nogEens.was, 'maar levert geen tapas op (' + nogEens.was + ' -> ' + nogEens.nu + ')');
  ok(nogEens.tikken === 2, 'de tikken worden geteld, zodat de app na twee keer ophoudt (' + nogEens.tikken + ')');

  // --- 7d. Na twee uitnodigingen houdt de app erover op ---
  const opIsOp = await page.evaluate(() => {
    S.samen = { gedeeld: '2026-01-01', tikken: 2 };
    S.lesFlow = { a: true, b: true };
    renderLessons();
    return { moment: uitnodigMoment(2), kaart: !!document.getElementById('uitnodigKaart') };
  });
  ok(!opIsOp.moment && !opIsOp.kaart, 'na twee uitnodigingen wordt er niet meer om gevraagd');

  // --- 8. De knop staat ook in de Speeltuin en bij Groepen ---
  const speeltuin = await page.evaluate(() => { show('speeltuin'); return !!document.getElementById('btnUitnodig'); });
  ok(speeltuin, 'de Speeltuin heeft een uitnodigknop in plaats van een verwijzing naar je naam bovenaan');
  const groepen = await page.evaluate(() => {
    show('perfil');
    return { knop: !!document.getElementById('btnUitnodig'), kaart: !!document.getElementById('grNaam') };
  });
  ok(groepen.knop, 'het groepenoverzicht ook, bovenaan');
  ok(groepen.kaart, 'en het handmatig starten van een groep blijft gewoon bestaan');

  // --- 9. Een duel zonder tegenstander is deelbaar als link ---
  const duel = await page.evaluate(() => {
    return {
      link: duelLink({ id: 'd7x' }),
      isFn: typeof duelDeel === 'function'
    };
  });
  ok(duel.link === 'https://vamos.stefanwobben.nl/?duel=d7x', 'duelLink() maakt een echte uitnodigingslink ("' + duel.link + '")');
  ok(duel.isFn, 'en duelDeel() bestaat om hem te versturen');

  // --- 10. Zonder navigator.share valt hij terug op het klembord ---
  const klembord = await page.evaluate(async () => {
    const gekopieerd = [];
    navigator.share = undefined;
    const echteKlem = navigator.clipboard;
    try {
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: { writeText: function (t) { gekopieerd.push(t); return Promise.resolve(); } }
      });
    } catch (e) { return { fout: e.message }; }
    uitnodigNu('test');
    await new Promise(function (r) { setTimeout(r, 300); });
    try { Object.defineProperty(navigator, 'clipboard', { configurable: true, value: echteKlem }); } catch (e) {}
    return { n: gekopieerd.length, tekst: gekopieerd[0] || '' };
  });
  ok(klembord.n === 1, 'zonder deelvenster gaat de uitnodiging naar het klembord');
  ok(/\?groep=/.test(klembord.tekst), 'en dan staat de link wél in de tekst ("' + String(klembord.tekst).slice(-30) + '")');

  // --- 11. De volgorde van samenKaartNu(), rechtstreeks (v19.58) ---
  // Dit is de regel die het makkelijkst sneuvelt als er ooit een kaart bijkomt: moment gaat voor
  // alles, dan het wekelijkse maatje-bericht, dan de uitnodiging, en de maatje-vraag is de laatste.
  const volgorde = await page.evaluate(() => {
    function welke() {
      const h = samenKaartNu(true);
      const m = h.match(/id='([a-zA-Z]+Kaart)'/);
      return m ? m[1] : (h ? 'onbekend' : 'geen');
    }
    const uit = {};
    maatjeStap = 0;
    momentOpen = false;

    // alles tegelijk waar: moment wint
    S.lesFlow = { a: 1, b: 1, c: 1, d: 1, e: 1 };
    S.samen = {};
    S.ritme = {};
    S.maatje = {};
    uit.alles = welke();

    // moment gezet -> uitnodiging
    S.ritme = { wanneer: 'stil' };
    uit.naMoment = welke();

    // uitnodiging op -> maatje-vraag
    S.samen = { gedeeld: '2026-01-01', tikken: 2 };
    uit.naUitnodiging = welke();

    // maatje gekoppeld -> geen werving meer; wel het weekbericht, maar alleen zo/ma
    S.maatje = { mcode: 'mtest01', naam: 'Kim' };
    uit.metMaatje = welke();
    uit.stuurMoment = maatjeStuurMoment();

    // zelf op "wijzigen" getikt gaat boven alles
    momentOpen = true;
    uit.gewijzigd = welke();
    momentOpen = false;

    // en alles afgehandeld = geen kaart
    S.maatje = { mcode: 'mtest01', naam: 'Kim', gestuurd: '2099-01-01' };
    uit.leeg = welke();

    S.maatje = {};
    S.samen = {};
    return uit;
  });
  // v22.1: de momentkaart is opgeheven, dus de uitnodiging staat nu vooraan in de rij.
  ok(volgorde.alles === 'uitnodigKaart', 'de uitnodiging gaat nu voor (' + volgorde.alles + ')');
  ok(volgorde.naMoment === 'uitnodigKaart', 'daarna pas de uitnodiging (' + volgorde.naMoment + ')');
  ok(volgorde.naUitnodiging === 'maatjeKaart', 'en als die op is, de maatje-vraag (' + volgorde.naUitnodiging + ')');
  /* v23.31: het weekbericht staat niet meer op Vandaag; het komt terug als rapport dat je een
     keer per week krijgt en kunt delen. Met een maatje staat er dus geen kaart meer, ook niet op
     zondag. Deze test hing tot nu toe aan de dag waarop hij toevallig draaide (op zondag verwachtte
     hij een kaart, doordeweeks niet); dat is nu weg en dat is winst op zich. */
  ok(volgorde.metMaatje === 'geen',
    'met een maatje staat er op Vandaag geen kaart meer, ook niet op zondag (' + volgorde.metMaatje + ')');
  ok(volgorde.gewijzigd !== 'momentKaart', 'ook met momentOpen komt de opgeheven momentkaart niet terug (' + volgorde.gewijzigd + ')');
  ok(volgorde.leeg === 'geen', 'en is alles afgehandeld, dan staat er niets (' + volgorde.leeg + ')');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
