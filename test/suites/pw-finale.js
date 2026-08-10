// Playwright-test voor de finale-ceremonie in v19.73.
// Stefan: "als je hem alles soort tapasjes hebt gegeven dan komt er een hele ceremonie net alsof
// je mario bros of zelda hebt uitgespeeld."
//
// Wat hier vastligt is niet de animatie maar de drie eigenschappen die een eindscherm tot een
// eindscherm maken:
//   1. het komt precies één keer, bij de laatste tapa, en niet bij de zeventiende
//   2. het onderbreekt alles en je moet er zelf uit klikken
//   3. het laat iets achter dat blijft staan: een plaquette met de datum, en de ceremonie is
//      daarna terug te kijken. Een viering die niets achterlaat is een schermbeveiliger.
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
  await page.goto(BASIS);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(BASIS);
  await page.waitForTimeout(600);

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwFinale' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // --- 1. Bij de op één na laatste tapa gebeurt er nog niets ---
  const bijna = await page.evaluate(() => {
    window.chispaSlaapt = function () { return false; };
    S.tapas = 200;
    S.tapaMenu = [];
    S.tapaFinale = null;
    for (let i = 0; i < TAPAS.length - 1; i++) tapaGeven();
    const w = document.getElementById('finaleWrap');
    return { menu: S.tapaMenu.length, n: TAPAS.length, klaar: tapaAllemaal(),
             scherm: !!(w && !w.classList.contains('hidden')), datum: S.tapaFinale };
  });
  ok(bijna.menu === bijna.n - 1, 'zeventien van de achttien tapas geproefd (' + bijna.menu + '/' + bijna.n + ')');
  ok(!bijna.klaar, 'de verzameling is nog niet compleet');
  ok(!bijna.scherm, 'en dus is er nog geen ceremonie: bijna is niet af');
  ok(!bijna.datum, 'er staat ook nog geen datum vast');

  // --- 2. De laatste tapa opent het eindscherm, precies één keer ---
  const laatste = await page.evaluate(() => {
    const r = tapaGeven();
    const w = document.getElementById('finaleWrap');
    return {
      finale: r && r.finale,
      zichtbaar: !!(w && w.getClientRects().length > 0),
      datum: S.tapaFinale,
      vandaag: today(),
      tapas: w ? w.querySelectorAll('.finaletapa').length : 0,
      dier: w ? w.querySelectorAll('svg').length : 0,
      knop: !!document.getElementById('btnFinaleSluit'),
      tekst: w ? w.innerText : ''
    };
  });
  ok(laatste.finale === true, 'tapaGeven() meldt de finale terug aan wie hem aanriep');
  ok(laatste.zichtbaar, 'het eindscherm staat er, schermvullend en over alles heen');
  ok(laatste.datum === laatste.vandaag, 'de dag waarop je het afmaakte wordt vastgelegd (' + laatste.datum + ')');
  ok(laatste.tapas === bijna.n, 'alle achttien tapas komen nog één keer voorbij (' + laatste.tapas + ')');
  ok(laatste.dier >= 1, 'en Chispa staat er zelf bij, want zij heeft ze opgegeten');
  ok(/Gran Men/i.test(laatste.tekst), 'het scherm heeft een naam: El Gran Menú');
  ok(laatste.knop, 'er is één knop om eruit te komen; je klikt hem zelf weg');

  // een eindscherm dat je per ongeluk oproept is geen eindscherm meer
  const nogmaals = await page.evaluate(() => {
    document.getElementById('btnFinaleSluit').click();
    S.tapas = 5;
    const r = tapaGeven();
    const w = document.getElementById('finaleWrap');
    return { finale: r && r.finale, zichtbaar: !!(w && w.getClientRects().length > 0), nieuw: r && r.nieuw };
  });
  ok(nogmaals.finale === false, 'een tapa geven na de finale opent hem niet opnieuw');
  ok(!nogmaals.zichtbaar, 'het scherm blijft dicht');
  ok(nogmaals.nieuw === false, 'en die tapa is geen ontdekking meer maar gewoon een smaak');

  // --- 3. Wat er blijft staan: de plaquette in de vitrine ---
  await page.evaluate(() => show('chispa'));
  await page.waitForTimeout(500);
  const plaq = await page.evaluate(() => {
    const p = document.getElementById('tapaPlaquette');
    return {
      erIs: !!p,
      inVitrine: !!(p && p.closest('#petCard')),   // v23.33: de plaquette staat bij Chispa zelf
      tekst: p ? p.innerText : '',
      datum: p ? p.innerText.indexOf(S.tapaFinale) !== -1 : false,
      knop: !!document.getElementById('btnFinaleTerug')
    };
  });
  ok(plaq.erIs && plaq.inVitrine, 'de plaquette staat bij Chispa, waar de verzameling staat');
  ok(/Gran Men/i.test(plaq.tekst), 'met dezelfde naam als de ceremonie');
  ok(plaq.datum, 'en de datum waarop je het afmaakte staat erop');
  /* v23.33, op Stefans verzoek: de knop "Kijk de ceremonie terug" is weg. De plaquette blijft, want
     die is het bewijs; de herhaling was iets anders. Een ceremonie die je op afroep kunt herhalen is
     na de tweede keer geen ceremonie meer, en de datum erop doet het werk. */
  ok(!plaq.knop, 'en er zit geen knop meer bij om de ceremonie te herhalen');

  // --- 4. De stand blijft staan, ook zonder herhaling ---
  const weg = await page.evaluate(() => {
    const w = document.getElementById('finaleWrap');
    return { dicht: !(w && w.getClientRects().length > 0),
             chispa: !document.getElementById('tab-chispa').classList.contains('hidden'),
             datum: S.tapaFinale,
             chips: document.querySelectorAll('#petCard .tapachip.gehad').length };
  });
  ok(weg.dicht, 'de ceremonie staat niet opnieuw open');
  ok(weg.chispa, 'je staat op Chispa\'s pagina');
  ok(weg.datum === laatste.datum, 'de oorspronkelijke datum blijft staan, niet die van vandaag');
  ok(weg.chips === bijna.n, 'en de verzameling staat vol (' + weg.chips + ')');

  // --- 5. Het scherm spreekt de taal van het profiel ---
  const taal = await page.evaluate(() => {
    tapaFinaleTonen();
    const w = document.getElementById('finaleWrap');
    return { lang: profLang(), tekst: w.innerText };
  });
  if (taal.lang === 'en') {
    ok(!/geproefd|Compleet op|Terug naar/.test(taal.tekst), 'geen Nederlandse resten in het eindscherm van een Engels profiel');
  } else {
    ok(/geproefd|Compleet op/.test(taal.tekst), 'het eindscherm staat in het Nederlands');
  }
  await page.evaluate(() => { const b = document.getElementById('btnFinaleSluit'); if (b) b.click(); });
  await page.waitForTimeout(300);

  // --- 6. Geen JS-fouten in eigen code ---
  const eigen = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(eigen.length === 0, 'geen JS-fouten tijdens de hele test (' + eigen.length + ' gevonden)');
  if (eigen.length) eigen.slice(0, 4).forEach((e) => console.log('   ', e));

  await browser.close();
  if (fails === 0) console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
  else { console.log('\n' + fails + ' TESTS GEFAALD'); process.exit(1); }
})();
