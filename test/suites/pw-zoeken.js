// Playwright-test voor het globale zoekveld (7 aug, v21.6). Stefan: "zou woordenboek misschien een
// globale functie moeten zijn? in de header direct een zoekbalk en dan smart search?" De aanleiding
// was dat hij zelf niet wist dat dat boekicoontje in de kop het woordenboek was, en hij heeft het
// gebouwd. Precies zijn moeders bevinding: knoppen waarvan je het doel niet weet.
// Bewaakt hier: het veld zoekt in beide talen en over alle soorten inhoud, de rangschikking is hard
// en voorspelbaar (exact, dan begint-met, dan bevat), woorden staan altijd bovenaan, en er zit geen
// netwerkaanroep in de weg (dus geen AI, dus instant en offline).
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  const verzoeken = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error' && !/Failed to load resource/.test(msg.text())) errors.push('console.error: ' + msg.text()); });
  page.on('request', (r) => { if (/\/api\//.test(r.url())) verzoeken.push(r.url()); });

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
  await page.fill('input[placeholder="Name"]', 'PwZoek' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);


  /* v23.209: de zoekpil woont in de kop, en op een taakscherm is die kop weg. Dat is geen
     ongelukje: de app zegt bij elk woordkaartje "probeer het antwoord eerst zelf te bedenken", en
     een zoekknop naast die zin is een uitweg uit precies de poging die het werk doet. Buiten een
     oefening is opzoeken juist wel de bedoeling, en daar staat de pil dus gewoon.

     De app opent bij binnenkomst zelf je dagles, dus die pauzeren we hier eerst. Wat deze suite
     bewaakt verandert daar niet door: er is één zoekingang, hij heet iets, en hij opent het
     woordenboek. */
  await page.evaluate(() => { try { if(document.getElementById('btnLesPauze')) lesFramePauze(); } catch(e){} });
  await page.waitForTimeout(400);

  // ---- 1. de kop toont een zoekveld, geen raadsel ----
  ok(await page.locator('#dicFab.zoekpil').count() === 1, 'in de kop staat een zoekpil, geen los boekicoontje');
  const pilTekst = await page.locator('#dicFab').innerText();
  ok(/Zoek|Search/i.test(pilTekst), 'er staat een woord op dat zegt wat hij doet ("' + pilTekst.replace(/\n/g, ' ') + '")');

  // v23.6: de pil opende een eigen zoekvenster naast het woordenboek. Stefan, met een schermafbeelding
  // van dat venster: "deze hele weergave wil ik niet", en met een schermafbeelding van het woordenboek:
  // "ik wil alleen deze". Er is er nu nog één, en de pil opent hem.
  await page.click('#dicFab');
  await page.waitForTimeout(300);
  ok(await page.locator('#dicZoek').count() === 1, 'de pil opent het woordenboek met een invoerveld');
  ok(await page.locator('#dicZoek').evaluate((e) => document.activeElement === e), 'het veld heeft meteen de cursor');
  ok(await page.locator('#zoekVeld').count() === 0, 'en er is geen tweede zoekscherm meer');
  ok(await page.evaluate(() => typeof zoekOpen === 'undefined'), 'de code van dat venster is echt weg, niet alleen onbereikbaar');

  // ---- 2. beide talen, accentloos, en de rangschikking ----
  const talen = await page.evaluate(() => {
    function ids(q) { return zoekResultaten(q).map((g) => ({ soort: g.soort, eerste: g.rijen[0] && g.rijen[0].es })); }
    return { nl: ids('weduwe'), es: ids('viuda'), acc: ids('cafe'), kort: zoekResultaten('a').length };
  });
  ok(talen.nl.length > 0, 'zoeken op het Nederlandse woord geeft resultaat');
  ok(talen.es.length > 0, 'zoeken op het Spaanse woord ook');
  ok(talen.acc.length > 0, 'accenten mogen weggelaten worden (cafe vindt café)');
  ok(talen.kort === 0, 'bij een enkele letter zoekt hij nog niet');

  const rang = await page.evaluate(() => {
    const g = zoekResultaten('casa').filter((x) => x.soort === 'woord')[0];
    return g ? g.rijen.slice(0, 3).map((r) => r.es) : [];
  });
  ok(rang.length > 0 && /^casa$/i.test(rang[0].replace(/^(el|la|los|las|un|una)\s+/i, '').split(/[\/(]/)[0].trim()),
     'de exacte treffer staat bovenaan, ook met lidwoord ervoor (' + rang.join(' | ') + ')');

  // ---- 3. woorden altijd eerst, ook als iets anders beter scoort ----
  const volgorde = await page.evaluate(() => zoekResultaten('el').map((g) => g.soort));
  ok(volgorde[0] === 'woord' || volgorde.length === 0, 'woorden staan bovenaan (' + volgorde.join(',') + ')');

  // ---- 4. het zoekt echt over alle soorten ----
  const soorten = await page.evaluate(() => {
    const gevonden = {};
    ['casa', 'ser', 'estar', 'chispa', 'winkel', 'restaurante', 'bachata', 'por'].forEach(function (q) {
      zoekResultaten(q).forEach(function (g) { gevonden[g.soort] = true; });
    });
    return Object.keys(gevonden).sort();
  });
  ['woord', 'zin', 'concept'].forEach(function (k) {
    ok(soorten.indexOf(k) !== -1, 'zoekt ook in ' + k + ' (' + soorten.join(',') + ')');
  });

  // ---- 5. het scherm: woorden eerst en meteen leesbaar, de rest onder een vouw ----
  await page.fill('#dicZoek', 'casa');
  await page.waitForTimeout(400);
  const scherm = await page.evaluate(() => {
    const kaart = document.getElementById('dicCard');
    const vouw = kaart.querySelector('details');
    const perKop = [];
    if (vouw) {
      let n = 0;
      Array.from(vouw.children).forEach(function (el) {
        if (el.classList.contains('dicletter')) { if (n) perKop.push(n); n = 0; }
        else if (el.classList.contains('dicrow')) n++;
      });
      if (n) perKop.push(n);
    }
    return {
      woordrijen: kaart.querySelectorAll('.dicrow[data-dic]').length,
      vouwErIn: !!vouw,
      vouwDicht: vouw ? !vouw.open : null,
      perKop: perKop,
      andersVoorWoord: (function () {
        const rijen = Array.from(kaart.querySelectorAll('.dicrow'));
        const eersteAnder = rijen.findIndex(function (r) { return r.hasAttribute('data-oz'); });
        const eersteWoord = rijen.findIndex(function (r) { return r.hasAttribute('data-dic'); });
        return eersteAnder !== -1 && eersteWoord !== -1 && eersteAnder < eersteWoord;
      })()
    };
  });
  ok(scherm.woordrijen > 0, 'de woorden staan er als gewone rijen met hun betekenis: ' + scherm.woordrijen);
  ok(scherm.vouwErIn === true, 'zinnen, grammatica en verhalen zijn niet verdwenen, ze staan onder een vouw');
  ok(scherm.vouwDicht === true, 'die vouw staat dicht, want je zocht een woord');
  ok(scherm.andersVoorWoord === false, 'en niets van dat alles staat boven de woorden');
  ok(scherm.perKop.every(function (n) { return n <= 4; }), 'hoogstens vier per soort in de vouw (' + scherm.perKop.join(',') + ')');

  // ---- 5b. geen dubbele regels ----
  // SENTENCES krijgt bij het wisselen van track B_SENTENCES erbij geplakt, en bij de woorden bestaat
  // dezelfde overlap. Zonder ontdubbelen stond "la casa" twee keer in de uitslag.
  const dubbel = await page.evaluate(() => {
    const uit = [];
    ['casa', 'estar', 'padre', 'agua'].forEach(function (q) {
      zoekResultaten(q).forEach(function (g) {
        const gezien = {};
        g.rijen.forEach(function (r) {
          const k = r.es + '|' + r.nl;
          if (gezien[k]) uit.push(q + ' :: ' + k);
          gezien[k] = 1;
        });
      });
    });
    return uit;
  });
  ok(dubbel.length === 0, 'geen enkele regel staat er dubbel in (' + dubbel.slice(0, 3).join(' / ') + ')');
  const uniek = await page.evaluate(() => {
    const ids = {};
    let dub = 0;
    zoekIndex().forEach(function (it) { const k = it.soort + ':' + it.id; if (ids[k]) dub++; ids[k] = 1; });
    return { totaal: zoekIndex().length, dub: dub };
  });
  ok(uniek.dub === 0, 'de index zelf bevat geen dubbele ids (' + uniek.totaal + ' regels)');

  // ---- 6. een woord meenemen zet het in je rotatie, zonder je niveau op te tillen ----
  const mee = await page.evaluate(() => {
    const g = zoekResultaten('casa').filter((x) => x.soort === 'woord')[0];
    const id = g.rijen[0].id;
    delete S.srs[id];
    const voorSchrijven = Object.keys(S.comp.schrijven || {}).length;
    zoekNeemMee(id);
    return {
      inRotatie: !!S.srs[id],
      box: S.srs[id] && S.srs[id].box,
      zelf: S.srs[id] && S.srs[id].zelf,
      schrijvenErbij: Object.keys(S.comp.schrijven || {}).length - voorSchrijven
    };
  });
  ok(mee.inRotatie === true, 'een opgezocht woord komt in je woordjes terecht');
  ok(mee.box === 0, 'in doosje nul, dus hij komt vandaag nog terug');
  ok(mee.zelf === 1, 'gemarkeerd als zelf opgezocht, zodat je later kunt zien wat mensen missen');
  ok(mee.schrijvenErbij === 0, 'opzoeken telt niet mee voor je niveau');

  // ---- 7. geen netwerk: instant en offline ----
  // De app synchroniseert op de achtergrond met Render; dat staat los van zoeken. We tellen alleen
  // wat er tijdens het zoeken zelf gebeurt.
  const voorZoek = verzoeken.length;
  await page.fill('#dicZoek', 'estar');
  await page.waitForTimeout(400);
  await page.fill('#dicZoek', 'winkel');
  await page.waitForTimeout(400);
  ok(verzoeken.length === voorZoek, 'zoeken zelf doet geen enkele api-aanroep (' + verzoeken.slice(voorZoek).join(',') + ')');

  // ---- 8. een treffer brengt je er ook echt heen ----
  await page.evaluate(() => {
    const g = zoekResultaten('ser').filter((x) => x.soort === 'concept')[0];
    if (g) zoekGaNaar('concept', g.rijen[0].id);
  });
  await page.waitForTimeout(400);
  const naar = await page.evaluate(() => ({
    tab: !document.getElementById('tab-spiekbrief').classList.contains('hidden'),
    dicht: document.getElementById('dicWrap').classList.contains('hidden')
  }));
  ok(naar.tab === true, 'een grammaticatreffer opent de grammaticapagina');
  ok(naar.dicht === true, 'en het woordenboek gaat dicht');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
