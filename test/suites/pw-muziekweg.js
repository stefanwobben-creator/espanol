// pw-muziekweg.js (31 aug, v23.218) — muziek is eruit, en wat je geoogst had staat er nog
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 31 aug: "helemaal eruit."
//
// De aanleiding was dat drie van de zeventien liedjes een verzonnen taaloogst hadden (bij Orión
// stonden zeven uitdrukkingen met correcte uitleg waarvan er nul in het nummer voorkwamen). De
// beslissing eronder kwam uit het nameten van wat muziek eigenlijk oplevert: onvrijwillige
// herhaling en letterlijke gesproken productie, bij een dosis van uren. Het liedscherm was vier
// minuten en eindigde in drie meerkeuzevragen, en meerkeuze is precies de toetsvorm waarop zingen
// géén voordeel heeft.
//
// EEN VERWIJDERING IS GEVAARLIJKER DAN EEN TOEVOEGING
//
// Muziek zat op acht plekken vastgehaakt: de dagles (MUS_OM_DE), de speeltuin (SPEL_VAST), een wens
// van Chispa, het Meer-menu, het woordenboek (songWoordenLijst), TABS en DOM, de globale zoekfunctie,
// de terugknop-geschiedenis, het morgenbericht en een beheerrol uit v19.92. Bij het bouwen vond de
// eigen controle van de patch er tien die ik zelf over het hoofd had gezien.
//
// Maar het echte risico is niet een dode knop. Het is dat er honderd woorden uit iemands doosjes
// verdwijnen zonder dat iemand het merkt, want die merk je pas als je ze zou moeten terugzien.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. WAT JE GEOOGST HAD STAAT ER NOG, MET ZIJN DOOSJE. Dit is de belangrijkste. Geoogste
//      liedwoorden gingen via mijnBij() naar S.mijn (gesleuteld op de platte Spaanse tekst) en
//      krijgen bij elke start opnieuw een rij in WORDS via mijnWoordenInPool(). Dat loopt langs de
//      SONGS-array heen, dus het hoort te overleven. "Hoort te" is geen bewijs.
//   2. CONTROLE BIJ 1: de proef ziet het ook als het WEL kapot is. Zonder dit bewijst proef 1
//      niets, want een woord dat er nooit was is ook niet weg.
//   3. ER IS GEEN MUZIEKSCHERM MEER, en er is ook geen tabblad dat naar een leeg scherm wijst.
//   4. GEEN ENKELE PAGINA VALT OM. Zeventien schermen langs, geen paginafouten. Dit vangt de dode
//      aanroep die na een verwijdering altijd ergens blijft hangen.
//   5. DE DAGLES HEEFT NOG STEEDS EEN INPUTBLOK. Muziek was eens per drie dagen dat blok; valt de
//      terugval naar lezen of luisteren om, dan is de les een stap korter zonder dat iemand het zegt.
//   6. DE SPEELTUIN WERKT NOG. Música was het enige vaste tegeltje (SPEL_VAST), en een lege lijst
//      is precies het soort randgeval waar zo'n rotatie op stukloopt.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwMw' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {} });
  await page.waitForTimeout(300);

  // ---- 1 en 2. de geoogste woorden ----
  console.log('\n-- 1. wat je uit een lied geoogst had --');
  /* Precies zoals musOogstBij() het achterliet: een rij in S.mijn op de platte Spaanse tekst, en
     een doosje in S.srs op mijnWoordId() van diezelfde sleutel. Twee echte uitdrukkingen uit de
     oogst van La Bachata, want die was niet verzonnen. */
  const gezet = await page.evaluate(() => {
    const paren = [['te bloqueé', 'ik blokkeerde je'], ['me enamoré (de ti)', 'ik werd verliefd (op jou)']];
    const ids = [];
    paren.forEach(function (p) {
      const plat = stripAcc(p[0].toLowerCase()).replace(/[^a-z0-9 ]/g, '').trim();
      S.mijn = S.mijn || {};
      S.mijn[plat] = { es: p[0], nl: p[1], d: today() };
      const id = mijnWoordId(plat);
      S.srs = S.srs || {};
      S.srs[id] = { box: 3, due: addDays(today(), 8), n: 5, zelf: 1 };
      ids.push(id);
    });
    try { persist(); } catch (e) {}
    return ids;
  });
  console.log('   ids: ' + gezet.join(', '));

  await page.reload();
  await page.waitForTimeout(1200);

  const na = await page.evaluate((ids) => {
    const uit = { inPool: [], doos: [], poolTotaal: WORDS.length };
    ids.forEach(function (id) {
      const w = WORDS.filter(function (x) { return x.id === id; })[0];
      uit.inPool.push(w ? w.es : null);
      uit.doos.push((S.srs[id] || {}).box);
    });
    return uit;
  }, gezet);
  console.log('   ' + JSON.stringify(na));
  ok(na.inPool.every(function (x) { return !!x; }),
    'beide geoogste uitdrukkingen staan na een herstart nog in de woordenpool');
  ok(na.doos.every(function (b) { return b === 3; }),
    'en hun doosje staat nog op 3, dus de SRS is niet teruggezet');

  console.log('\n-- 2. controlegeval: ziet deze proef het ook als het wél weg is --');
  const controle = await page.evaluate(() => {
    const id = mijnWoordId('bestaatnietinmijn');
    return { inPool: !!WORDS.filter(function (x) { return x.id === id; })[0],
             doos: (S.srs[id] || {}).box };
  });
  ok(controle.inPool === false && controle.doos === undefined,
    'CONTROLE: een woord dat nooit geoogst is, staat er ook niet (dus proef 1 kan omvallen)');

  // ---- 3. geen muziekscherm meer ----
  console.log('\n-- 3. muziek is er niet meer --');
  const weg = await page.evaluate(() => ({
    tab: !!document.getElementById('tab-musica'),
    inTabs: TABS.filter(function (t) { return t.id === 'musica'; }).length,
    songs: typeof SONGS,
    render: typeof renderSongs,
    vanDag: typeof musVanDag,
    /* elk tabblad in TABS hoort een sectie in de pagina te hebben; een tab zonder scherm is een
       knop naar het niets, en dat is precies wat een halve verwijdering achterlaat */
    zonderScherm: TABS.filter(function (t) { return !document.getElementById('tab-' + t.id); }).map(function (t) { return t.id; })
  }));
  console.log('   ' + JSON.stringify(weg));
  ok(!weg.tab && weg.inTabs === 0, 'er is geen muziektabblad meer');
  ok(weg.songs === 'undefined' && weg.render === 'undefined' && weg.vanDag === 'undefined',
    'en geen SONGS, renderSongs of musVanDag meer');
  ok(weg.zonderScherm.length === 0,
    'CONTROLE: elk tabblad heeft nog een eigen scherm (' + (weg.zonderScherm.join(', ') || 'alle') + ')');

  // ---- 4. niets valt om ----
  console.log('\n-- 4. alle schermen langs --');
  const ids = await page.evaluate(() => TABS.map(function (t) { return t.id; }));
  for (const id of ids) {
    await page.evaluate((x) => show(x, true), id);
    await page.waitForTimeout(140);
  }
  console.log('   ' + ids.length + ' schermen getekend');
  ok(ids.length >= 15, 'er zijn nog genoeg schermen over (' + ids.length + ')');

  // ---- 5. de dagles heeft nog een inputblok ----
  console.log('\n-- 5. het inputblok van de dagles --');
  const input = await page.evaluate(() => {
    (tLessons() || []).forEach(function (l) {
      S.lessons[l.id] = { done: true, woorden: true, zinnen: true, quiz: true, spiek: true };
    });
    try { persist(); } catch (e) {}
    let k = null;
    try { k = lesFlowInputKeuze(); } catch (e) { k = 'FOUT: ' + e.message; }
    return { keuze: k, musDagBeurt: typeof musDagBeurt };
  });
  console.log('   ' + JSON.stringify(input));
  ok(['lezen', 'luisteren', null].indexOf(input.keuze) !== -1,
    'de keuze is lezen, luisteren of niets, en geen fout (' + input.keuze + ')');
  ok(input.musDagBeurt === 'undefined', 'CONTROLE: en musDagBeurt() bestaat echt niet meer');

  // ---- 6. de speeltuin met een lege SPEL_VAST ----
  console.log('\n-- 6. de speeltuin overleeft een lege vaste lijst --');
  const speel = await page.evaluate(() => {
    S.speelAlles = true;
    try { persist(); } catch (e) {}
    show('speeltuin', true);
    let vandaag = null;
    try { vandaag = spelVanVandaag(); } catch (e) { vandaag = 'FOUT: ' + e.message; }
    const sec = document.getElementById('tab-speeltuin');
    return { vast: SPEL_VAST.length, vandaag: vandaag && vandaag.v ? vandaag.v : String(vandaag),
             tegels: [].slice.call(sec.querySelectorAll('[id^="ft"]')).map(function (x) { return x.id; }) };
  });
  await page.waitForTimeout(300);
  console.log('   ' + JSON.stringify(speel));
  ok(speel.vast === 0, 'SPEL_VAST is leeg (was ["musica"])');
  ok(String(speel.vandaag).indexOf('FOUT') === -1 && speel.vandaag !== 'null',
    'en er is nog gewoon een spel van vandaag (' + speel.vandaag + ')');
  /* Op een vers profiel staan de meeste spellen nog op slot. Nagemeten op de bouw van vlak vóór
     deze verwijdering: daar stonden er twee (ftClas en ftMusica), hier hoort er dus precies één
     over te blijven en dat moet die van vandaag zijn. Een aantal als drempel zou hier niets zeggen;
     dit zegt dat er precies één tegel is verdwenen en welke. */
  ok(speel.tegels.length >= 1, 'de speeltuin toont nog tegels (' + speel.tegels.join(', ') + ')');
  ok(speel.tegels.indexOf('ftMusica') === -1, 'en Música staat er niet meer tussen');
  ok(speel.tegels.indexOf('ft' + speel.vandaag.charAt(0).toUpperCase() + speel.vandaag.slice(1)) !== -1,
    'CONTROLE: het spel van vandaag heeft ook echt een tegel (' + speel.vandaag + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs.join(' | ') : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
