// Playwright-test voor v19.61: het Etiquetas-spel is weg.
// Stefan: "etiquetas werkt niet echt en kan helemaal weg."
// Contract dat we hier vastleggen:
//  - er is geen ESCENAS, ESC_TXT, escStart, escSvg, escSpel of renderFunEsc meer
//  - escChispaMini blijft wel, want Aventura, het kruiswoord en de strips tekenen
//    hun sprite ermee; die zou anders leeg blijven
//  - de Speeltuin heeft geen rij met een etiquettenspel
//  - Aventura werkt nog: de wereldkeuze en de kaart renderen zonder JS-fout
//  - de huisjes in Aventura leveren nog steeds hun dagelijkse schat op
//    (+1 tapa en +5 monedas, één keer per dag per huis), want dat was de enige
//    reden dat je er als speler naar binnen liep
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
  ok(speeltuin.includes('aventura'), 'Aventura staat er nog wel');

  // 3. Aventura zelf blijft werken
  await page.evaluate(() => { funView = 'avt'; avt = null; renderFun(); });
  await page.waitForTimeout(400);
  const wereldkeuze = await page.locator('#funCard').innerText();
  ok(/aventura/i.test(wereldkeuze), 'de wereldkeuze van Aventura rendert');

  const kaart = await page.evaluate(() => {
    avtWereld = 'a0';
    avtStartWereld();
    return !!document.getElementById('avtKaart');
  });
  await page.waitForTimeout(400);
  ok(kaart, 'de kaart van La Costa rendert');

  // 4. een huisje betreden levert nog steeds de dagschat op
  const schat = await page.evaluate(() => {
    var sav = avtSave();
    sav.casa = {};
    var voorTapas = S.tapas || 0, voorMonedas = S.monedas || 0;

    // zoek een scherm in deze wereld met een huisje (H of F) erop en ga erheen
    var si = -1, doel = null;
    for (var i = 0; i < AVT_SCHERMEN.length && si < 0; i++) {
      var sch = AVT_SCHERMEN[i];
      if (sch.w !== 'a0') continue;
      for (var y = 0; y < sch.grid.length && si < 0; y++) {
        for (var x = 0; x < sch.grid[y].length; x++) {
          var c = sch.grid[y].charAt(x);
          if (c === 'H' || c === 'F') { si = i; doel = { x: x, y: y }; break; }
        }
      }
    }
    if (si < 0) return { gevonden: false };
    avt.scherm = si;
    avtLaadScherm(si, true);

    avt.x = doel.x; avt.y = doel.y - 1;
    avtMove(0, 1);
    var na1 = { tapas: S.tapas || 0, monedas: S.monedas || 0 };

    // en nog een keer, dat mag vandaag niets meer opleveren
    avt.x = doel.x; avt.y = doel.y - 1;
    avtMove(0, 1);
    var na2 = { tapas: S.tapas || 0, monedas: S.monedas || 0 };

    return {
      gevonden: true,
      tapaErbij: na1.tapas - voorTapas,
      monedaErbij: na1.monedas - voorMonedas,
      tweedeKeerTapa: na2.tapas - na1.tapas,
      tweedeKeerMoneda: na2.monedas - na1.monedas
    };
  });
  ok(schat.gevonden, 'er staat een huisje op de eerste kaart');
  ok(schat.tapaErbij === 1, 'een huis betreden geeft +1 tapa');
  ok(schat.monedaErbij === 5, 'een huis betreden geeft +5 monedas');
  ok(schat.tweedeKeerTapa === 0 && schat.tweedeKeerMoneda === 0, 'dezelfde dag nog eens levert niets extra op');

  ok(errors.length === 0, 'geen JS-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  if (fails) { console.log('\n' + fails + ' TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
