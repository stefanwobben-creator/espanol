// Playwright-smoketest voor v19.55: jargon-uitleg als herbruikbaar component + de start-les-kaart
// zonder knop.
// Stefan, 30 juli:
//  (1) "Het is een speelse instructie, geen actie of keuzemoment. Laat de kaart staan als banner van
//      stap 1, zonder knop."
//  (3) "Bouw het als één herbruikbaar component gevoed door een term->definitie-map, niet hardcoded
//      per term. Tikken moet werken, niet alleen hover. Een term zonder definitie wordt zichtbaar
//      gemarkeerd als 'nog geen uitleg' in plaats van stilzwijgend niets te doen. De uitleg is in
//      gewone taal, zonder jargon in de uitleg, met waar mogelijk een Spaans voorbeeld."
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

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwJargon' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(300);

  // --- 1. De map is de bron, niet de code ---
  const map = await page.evaluate(() => {
    const verwacht = ['infinitief', 'gerundio', 'participio', 'indicativo', 'subjuntivo', 'imperativo',
                      'pretérito indefinido', 'pretérito imperfecto', 'reflexief werkwoord'];
    const mist = verwacht.filter(function (t) { return !JARGON[t]; });
    const zonderVb = [];
    const zonderEn = [];
    const jargonInUitleg = [];
    // geen jargon binnen de uitleg van jargon: een definitie mag geen andere vakterm bevatten
    const termen = Object.keys(JARGON);
    Object.keys(JARGON).forEach(function (k) {
      const d = JARGON[k];
      if (!d.vb) zonderVb.push(k);
      if (!d.en) zonderEn.push(k);
      termen.forEach(function (t) {
        if (t !== k && new RegExp('(^|[^a-z])' + t + '([^a-z]|$)', 'i').test(d.nl)) jargonInUitleg.push(k + ' bevat ' + t);
      });
    });
    return { n: termen.length, mist: mist, zonderVb: zonderVb, zonderEn: zonderEn,
             jargonInUitleg: jargonInUitleg, zonder: JARGON_ZONDER.slice(0),
             termen: jargonTermen().length };
  });
  ok(map.mist.length === 0, 'alle negen termen van Stefan staan in de map (mist: ' + map.mist.join(', ') + ')');
  ok(map.zonderVb.length === 0, 'elke definitie heeft een Spaans voorbeeld (zonder: ' + map.zonderVb.join(', ') + ')');
  ok(map.zonderEn.length === 0, 'elke definitie heeft ook een Engelse variant (zonder: ' + map.zonderEn.join(', ') + ')');
  ok(map.jargonInUitleg.length === 0, 'geen jargon binnen de uitleg van jargon (' + map.jargonInUitleg.slice(0, 3).join(' | ') + ')');
  ok(map.zonder.length > 0, 'er is een lijst met termen die de app wél gebruikt maar nog geen uitleg hebben (' + map.zonder.join(', ') + ')');
  ok(map.termen === map.n + map.zonder.length, 'jargonTermen() = de map plus de nog-uit-te-leggen termen (' + map.termen + ')');

  // --- 2. Het component is generiek: één nieuwe regel in de map volstaat ---
  const generiek = await page.evaluate(() => {
    JARGON['zwabberwoord'] = { nl: 'een verzonnen term om te testen', en: 'a made-up term for testing', vb: 'zwabbar', vben: 'zwabbar' };
    delete jargonRegex._re;
    const d = document.createElement('div');
    d.innerHTML = '<p>Een zwabberwoord in een zin.</p>';
    document.body.appendChild(d);
    jargonScan(d);
    const raak = d.querySelectorAll('.jrg[data-jrg="zwabberwoord"]').length;
    const pop = d.querySelector('.jrg .jrgpop');
    const tekst = pop ? pop.innerText : '';
    d.remove();
    delete JARGON['zwabberwoord'];
    delete jargonRegex._re;
    return { raak: raak, tekst: tekst };
  });
  ok(generiek.raak === 1, 'een term toevoegen aan de map is genoeg: hij wordt meteen gemarkeerd');
  ok(/verzonnen term|made-up term/.test(generiek.tekst), 'de uitleg uit de map komt in de tooltip terecht');

  // --- 3. Woordgrenzen: geen treffers midden in een woord ---
  const grenzen = await page.evaluate(() => {
    const d = document.createElement('div');
    d.innerHTML = '<p>infinitiefvorm en xxinfinitief en infinitief.</p>';
    document.body.appendChild(d);
    jargonScan(d);
    const n = d.querySelectorAll('.jrg').length;
    const tekst = d.innerText;
    d.remove();
    return { n: n, heeftTekst: tekst.indexOf('infinitiefvorm') >= 0 };
  });
  ok(grenzen.n === 1, 'alleen het losse woord wordt gemarkeerd, niet infinitiefvorm of xxinfinitief (' + grenzen.n + ')');
  ok(grenzen.heeftTekst, 'de omliggende tekst blijft intact');

  // --- 4. Term zonder uitleg: zichtbaar gemarkeerd, niet stilletjes niets ---
  const leeg = await page.evaluate(() => {
    const t = JARGON_ZONDER[0];
    const d = document.createElement('div');
    d.innerHTML = '<p>Hier staat ' + t + ' in een zin.</p>';
    document.body.appendChild(d);
    jargonScan(d);
    const el = d.querySelector('.jrg.leeg');
    const pop = el ? el.querySelector('.jrgleeg') : null;
    const res = { gemarkeerd: !!el, tekst: pop ? pop.innerText : '', term: t };
    d.remove();
    return res;
  });
  ok(leeg.gemarkeerd, '"' + leeg.term + '" krijgt een eigen markering (.jrg.leeg) ook zonder definitie');
  ok(/nog geen uitleg|no explanation/i.test(leeg.tekst), 'en zegt zelf dat er nog geen uitleg is ("' + leeg.tekst.trim() + '")');

  // --- 5. Tikken werkt, niet alleen hover ---
  await page.evaluate(() => {
    const d = document.createElement('div');
    d.id = 'jrgProef';
    // v21.5: dit proefblokje hing onderaan de body en kwam daardoor achter de vaste onderbalk
    // terecht, die sinds de vijfde navigatieplek net iets anders uitpakt. Het is een synthetisch
    // blokje voor deze test, dus zetten we het bovenaan en vrij van alles.
    d.style.cssText = 'position:fixed; top:8px; left:8px; right:8px; z-index:9999; background:#fff; padding:8px';
    d.innerHTML = '<p>De gerundio en de subjuntivo.</p>';
    document.body.appendChild(d);
    jargonScan(d);
  });
  await page.waitForTimeout(150);
  ok(await page.locator('#jrgProef .jrg').count() === 2, 'twee termen in één zin worden allebei gemarkeerd');
  ok(await page.locator('#jrgProef .jrg.open').count() === 0, 'in rust staat er niets open');
  await page.locator('#jrgProef .jrg').first().click();
  await page.waitForTimeout(150);
  ok(await page.locator('#jrgProef .jrg.open').count() === 1, 'tikken opent de uitleg (touch, niet alleen hover)');
  const popZichtbaar = await page.locator('#jrgProef .jrg.open .jrgpop').isVisible();
  ok(popZichtbaar, 'de uitleg is daarna ook echt zichtbaar');
  const popTekst = await page.locator('#jrgProef .jrg.open .jrgpop').innerText();
  ok(/-ndo|hablando/.test(popTekst), 'de uitleg van gerundio noemt de -ndo-vorm ("' + popTekst.replace(/\n/g, ' / ').trim() + '")');
  await page.locator('#jrgProef .jrg').first().click();
  await page.waitForTimeout(150);
  ok(await page.locator('#jrgProef .jrg.open').count() === 0, 'nog eens tikken sluit hem weer');
  await page.locator('#jrgProef .jrg').nth(1).click();
  await page.waitForTimeout(120);
  await page.locator('#jrgProef .jrg').first().click();
  await page.waitForTimeout(120);
  ok(await page.locator('#jrgProef .jrg.open').count() === 1, 'er staat er altijd hoogstens één open');
  await page.evaluate(() => { const d = document.getElementById('jrgProef'); if (d) d.remove(); });

  // --- 6. De uitleg legt zichzelf niet uit (geen oneindige nesting) ---
  const nesting = await page.evaluate(() => {
    const d = document.createElement('div');
    d.innerHTML = '<p>Het participio hier.</p>';
    document.body.appendChild(d);
    jargonScan(d);
    jargonScan(d);
    jargonScan(d);
    const n = d.querySelectorAll('.jrg').length;
    const diep = d.querySelectorAll('.jrg .jrg').length;
    d.remove();
    return { n: n, diep: diep };
  });
  ok(nesting.n === 1 && nesting.diep === 0, 'drie keer scannen levert nog steeds één markering op, zonder nesting');

  // --- 7. Echt in de app: de spiekbriefjes/grammatica ---
  await page.evaluate(() => show('spiekbrief'));
  await page.waitForTimeout(500);
  const inApp = await page.locator('#cheat .jrg').count();
  ok(inApp > 0, 'op de grammatica-pagina staan gemarkeerde vaktermen (' + inApp + ')');
  await page.locator('#cheat .jrg').first().click();
  await page.waitForTimeout(150);
  ok(await page.locator('#cheat .jrg.open').count() === 1, 'ook daar opent een tik de uitleg');
  // een tik op een term mag de onderliggende kaart niet meebedienen
  const naKlik = await page.evaluate(() => ({ tab: (document.querySelector('#tab-spiekbrief') || {}).className || '' }));
  ok(naKlik.tab.indexOf('hidden') === -1, 'een tik op een vakterm navigeert niet weg van de pagina');

  // --- 8. Punt 1: de start-les-kaart heeft geen knop meer ---
  const banner = await page.evaluate(() => {
    const h = lesFlowBannerHtml ? lesFlowBannerHtml() : '';
    return {
      html: h,
      stopWeg: typeof lesFlowStop === 'undefined',
      wire: typeof lesFlowWireBanner === 'function',
      chispaKnop: h.indexOf('btnLesFlowChispa') >= 0
    };
  });
  ok(banner.html.indexOf('btnLesFlowStop') === -1, 'de banner bevat geen "Later verder"-knop meer');
  ok(!/Later verder|Continue later/.test(banner.html), 'en ook de tekst ervan niet');
  ok(banner.stopWeg, 'lesFlowStop() is uit de code verdwenen');
  ok(banner.wire, 'lesFlowWireBanner() is de nieuwe wiring-functie');
  ok(banner.chispaKnop, 'Chispa zelf blijft aanklikbaar in de banner (dat is spel, geen keuze)');
  ok(await page.evaluate(() => document.querySelectorAll('#btnLesFlowStop').length) === 0, 'nergens in de DOM nog een stop-knop');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
