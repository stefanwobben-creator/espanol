// Playwright-test voor v19.61: het Etiquetas-spel is weg.
// Stefan: "etiquetas werkt niet echt en kan helemaal weg."
// Contract dat we hier vastleggen:
//  - er is geen ESCENAS, ESC_TXT, escStart, escSvg, escSpel of renderFunEsc meer
//  - escChispaMini blijft wel, want het kruiswoord en de strips tekenen hun
//    sprite ermee; die zou anders leeg blijven
//  - de Speeltuin heeft geen rij met een etiquettenspel
//  - er blijft een spel over dat wél werkt en zonder JS-fout rendert
//
// v23.147: de tweede helft van deze test ging over Aventura, en dat spel is nu zelf geschrapt
// (2057 regels, geen spoor van gebruik in 26 dagen). De bewering die overeind blijft is de eerste:
// een geschrapt spel laat geen resten achter en sloopt de buren niet. Die staat nu op het
// kruiswoord, want dat is wat er uit het Aventura-blok is blijven staan. Dat Aventura zelf weg is,
// bewaakt pw-geschrapt.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => {
    // audio- en fontverzoeken lukken niet in de sandbox; dat is geen appfout
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

  await page.fill('input[placeholder="Name"]', 'Stefan');
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // 1. de dode code is echt weg
  const weg = await page.evaluate(() => ({
    escenas: typeof ESCENAS,
    esctxt: typeof ESC_TXT,
    start: typeof escStart,
    svg: typeof escSvg,
    render: typeof renderFunEsc,
    mini: typeof escChispaMini
  }));
  ok(weg.escenas === 'undefined', 'ESCENAS bestaat niet meer');
  ok(weg.esctxt === 'undefined', 'ESC_TXT bestaat niet meer');
  ok(weg.start === 'undefined', 'escStart bestaat niet meer');
  ok(weg.svg === 'undefined', 'escSvg bestaat niet meer');
  ok(weg.render === 'undefined', 'renderFunEsc bestaat niet meer');
  ok(weg.mini === 'function', 'escChispaMini blijft, de spellen tekenen hun sprite ermee');

  // 2. de Speeltuin biedt het spel niet meer aan
  await page.evaluate(() => { funView = null; show("speeltuin"); });
  await page.waitForTimeout(400);
  const speeltuin = (await page.locator('#funCard').innerText()).toLowerCase();
  ok(!speeltuin.includes('etiqueta'), 'geen etiquettenrij in de Speeltuin');
  // v23.147: Aventura stond hier als bewijs dat er nog spellen over waren. Dat spel is nu zelf
  // geschrapt, dus de bewering verschuift naar wat hij eigenlijk was: er staat nog wél iets.
  ok(!speeltuin.includes('aventura'), 'Aventura ook niet, die is in v23.147 geschrapt');
  // niet op de schermtekst: de Speeltuin klapt sinds v23.145 in tot drie tegels en op een vers
  // profiel staat het meeste nog op slot. De vraag is of de lijst zelf nog spellen kent.
  const spellenOver = await page.evaluate(() => speelTegels().map((x) => x.v));
  ok(spellenOver.length >= 5, 'maar er staan nog wel spellen (' + spellenOver.join(',') + ')');
  ok(spellenOver.indexOf('avt') === -1 && spellenOver.indexOf('esc') === -1, 'en geen van de twee geschrapte');

  // 3. wat er overbleef werkt nog: het kruiswoord uit hetzelfde blok
  await page.evaluate(() => {
    S.speelAlles = true; S.spelAlles = true;
    S.srs = {};
    WORDS.slice(0, 120).forEach(function (w) { S.srs[w.id] = { box: 2, due: today(), n: 3 }; });
    funView = 'kruis'; kruisLos = null; renderFun();
  });
  await page.waitForTimeout(400);
  const kruisScherm = await page.locator('#funCard').innerText();
  ok(/Biblioteca/i.test(kruisScherm), 'het kruiswoord rendert (' + kruisScherm.split('\n')[0] + ')');
  ok(await page.evaluate(() => !!kruisLos), 'en er staat echt een puzzel');

  ok(errors.length === 0, 'geen JS-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  if (fails) { console.log('\n' + fails + ' TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
