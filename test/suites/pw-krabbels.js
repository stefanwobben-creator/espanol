// Playwright-smoketest voor v19.51 deel A: Martina + de opgeruimde krabbel-interface.
// Stefan: "martina hoort ook bij famile  de krabbels is leuk maar de interface wat rommlig."
// Contract dat we hier vastleggen:
//  - één blok (.famrij) per familielid, met daarin score, ontvangen krabbels en één knop
//  - géén tien brede pillen meer per persoon: het palet zit achter één Spaanse toggle
//  - de palet-knoppen zijn emoji-only, de Spaanse zin zit in title/aria-label
//  - er staat er nooit meer dan één palet open
//  - openen/sluiten van een palet doet GEEN nieuwe /api/familia-fetch (famCache)
//  - ontvangen krabbels zijn compacte chips met de afzender erbij
//  - na versturen klapt het palet dicht en zie je wat je gestuurd hebt
//  - bij jezelf staat geen knop
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

  // we heten zelf Elise: zo kunnen we ook testen dat je bij jezelf geen knop krijgt
  await page.fill('input[placeholder="Name"]', 'Elise');
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // de sandbox kan de Render-server niet bereiken; we zetten er dus een nep-api voor
  await page.evaluate(() => {
    const track = Object.keys(TRACKS)[0];
    window.apiCalls = [];
    window.api = function (path, method, body) {
      window.apiCalls.push({ path: path, method: method || 'GET', body: body || null });
      if (path === '/api/familia') {
        return Promise.resolve({
          ok: true,
          spelers: [
            { naam: 'Stefan', niveau: track, txp: 900, streak: 4, lessen: 12 },
            { naam: 'Elise', niveau: track, txp: 600, streak: 2, lessen: 8 },
            { naam: 'Martina', niveau: track, txp: 300, streak: 1, lessen: 3 }
          ],
          krabbels: [{ van: 'Stefan', naar: 'Martina', sleutel: 'platano' }]
        });
      }
      return Promise.resolve({ ok: true });
    };
  });

  await page.evaluate(() => show('perfil'));
  await page.waitForTimeout(600);

  // --- 1. Eén blok per familielid ---
  ok(await page.locator('#famLijst .famrij').count() === 3, 'ieder familielid krijgt één eigen blok (.famrij)');
  ok(await page.locator('#famLijst .duelrow').count() === 3, 'in elk blok staat de scoreregel');

  // --- 2. Eén knop per persoon in plaats van tien pillen, en niet bij jezelf ---
  ok(await page.locator('#famLijst button.krabtoggle').count() === 2, 'per ander familielid precies één knop (en niet bij jezelf)');
  ok(await page.locator('#famLijst button.krabbelknop').count() === 0, 'het palet met tien krabbels staat dicht tot je erop klikt');
  const toggleTekst = (await page.locator('#famLijst button.krabtoggle').first().innerText()).trim();
  ok(/Dejar un saludo/.test(toggleTekst), 'de knop is Spaans-only: "' + toggleTekst + '"');
  ok(!/(laat|achter|krabbel|schrijf)/i.test(toggleTekst), 'geen Nederlands in de knoptekst');
  const eigenRij = await page.evaluate(() => {
    const rijen = Array.prototype.slice.call(document.querySelectorAll('#famLijst .famrij'));
    const mijn = rijen.filter(function (r) { return /Elise/.test(r.innerText); })[0];
    return mijn ? mijn.querySelectorAll('button.krabtoggle').length : -1;
  });
  ok(eigenRij === 0, 'bij je eigen naam staat geen krabbelknop (' + eigenRij + ')');

  // --- 3. Ontvangen krabbels zijn compacte chips met afzender ---
  const chip = await page.evaluate(() => {
    const c = document.querySelector('#famLijst .krabchip');
    if (!c) return null;
    const rij = c.closest('.famrij');
    return {
      titel: c.getAttribute('title') || '',
      tekst: c.innerText.replace(/\s+/g, ' ').trim(),
      van: c.querySelector('.van') ? c.querySelector('.van').innerText.trim() : '',
      bijNaam: rij ? /Martina/.test(rij.innerText) : false
    };
  });
  ok(!!chip, 'een ontvangen krabbel wordt als chip getoond');
  ok(chip && chip.bijNaam, 'de chip staat in het blok van degene die hem kreeg (Martina)');
  ok(chip && /plátano/i.test(chip.titel), 'de hele Spaanse zin zit in de title: "' + (chip ? chip.titel : '') + '"');
  ok(chip && /Stefan/.test(chip.van), 'de afzender staat erbij ("' + (chip ? chip.van : '') + '")');

  // --- 4. Palet openen: emoji-only knoppen, Spaans in de title ---
  const fetchesVoor = await page.evaluate(() => window.apiCalls.filter(function (c) { return c.path === '/api/familia'; }).length);
  await page.locator('#famLijst button.krabtoggle').first().click();
  await page.waitForTimeout(250);
  ok(await page.locator('#famLijst .krabpal').count() === 1, 'na de klik staat er precies één palet open');
  ok(await page.locator('#famLijst button.krabbelknop').count() === 10, 'het palet bevat alle tien krabbels');
  const knop = await page.evaluate(() => {
    const b = document.querySelector('#famLijst button.krabbelknop');
    return { titel: b.getAttribute('title') || '', aria: b.getAttribute('aria-label') || '', tekst: b.innerText.trim() };
  });
  ok(/^[¡¡]/.test(knop.titel), 'de Spaanse zin zit in de title: "' + knop.titel + '"');
  ok(knop.aria === knop.titel, 'ook aria-label heeft de Spaanse zin (toegankelijk)');
  ok(knop.tekst.length <= 3, 'de knop zelf is emoji-only, dus smal: "' + knop.tekst + '"');
  const inZelfdeRij = await page.evaluate(() => {
    const pal = document.querySelector('#famLijst .krabpal');
    const rij = pal ? pal.closest('.famrij') : null;
    const tog = rij ? rij.querySelector('button.krabtoggle') : null;
    return !!(tog && /Cerrar/.test(tog.innerText));
  });
  ok(inZelfdeRij, 'het palet hoort bij de aangeklikte persoon en die knop zegt nu "Cerrar"');

  // --- 5. Toggelen doet geen nieuwe serverfetch (famCache) ---
  const fetchesNa = await page.evaluate(() => window.apiCalls.filter(function (c) { return c.path === '/api/familia'; }).length);
  ok(fetchesNa === fetchesVoor, 'open/dicht klappen haalt de scores niet opnieuw op (' + fetchesVoor + ' -> ' + fetchesNa + ')');

  // --- 6. Nooit twee paletten tegelijk ---
  await page.locator('#famLijst button.krabtoggle').nth(1).click();
  await page.waitForTimeout(250);
  ok(await page.locator('#famLijst .krabpal').count() === 1, 'een tweede persoon openen sluit de eerste (nooit twee paletten)');

  // --- 7. Versturen: palet dicht, bevestiging in het Spaans, POST met de juiste inhoud ---
  const naarNaam = await page.evaluate(() => {
    const b = document.querySelector('#famLijst button.krabbelknop');
    return b ? b.getAttribute('data-naar') : '';
  });
  await page.locator('#famLijst button.krabbelknop').first().click();
  await page.waitForTimeout(400);
  ok(await page.locator('#famLijst button.krabbelknop').count() === 0, 'na het versturen klapt het palet dicht');
  const verstuurd = await page.evaluate(() => {
    const v = document.querySelector('#famLijst .krabverstuurd');
    return v ? v.innerText.replace(/\s+/g, ' ').trim() : '';
  });
  ok(verstuurd.length > 0, 'je ziet terug wat je gestuurd hebt ("' + verstuurd + '")');
  ok(!/(gestuurd|verstuurd|jij)/i.test(verstuurd), 'die bevestiging blijft Spaans-only');
  const post = await page.evaluate(() => window.apiCalls.filter(function (c) { return c.path === '/api/krabbel'; })[0] || null);
  ok(!!post && post.method === 'POST', 'er gaat een POST naar /api/krabbel');
  ok(!!post && post.body && post.body.van === 'elise', 'de afzender is je eigen profiel ("' + (post && post.body ? post.body.van : '') + '")');
  ok(!!post && post.body && post.body.naar === naarNaam, 'de ontvanger klopt ("' + (post && post.body ? post.body.naar : '') + '")');
  ok(!!post && post.body && !!krabbelSleutelBestaat(post.body.sleutel, await page.evaluate(() => KRABBELS.map(function (k) { return k.k; }))), 'de verstuurde sleutel bestaat in KRABBELS');

  // --- 8. Martina hoort erbij: het klassement toont haar gewoon mee ---
  ok(/Martina/.test(await page.locator('#famLijst').innerText()), 'Martina staat in het familie-klassement');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();

function krabbelSleutelBestaat(sleutel, alle) {
  return alle.indexOf(sleutel) >= 0;
}
