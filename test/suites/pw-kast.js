// pw-kast.js -- de kledingkast in de browser (v19.77)
//
// De node-suite bewijst dat wearAan() en shopVrij() kloppen. Dat is niet hetzelfde als: je ziet
// het, je kunt erop klikken, en er gaat werkelijk iets anders van haar hoofd. Dit script test
// die keten, en vooral het stuk dat je alleen in een echte DOM ziet: dat de twee groepen
// (lessen en oefenen) uit elkaar te houden zijn, dat een slot ook echt een slot is als je erop
// klikt, en dat een gesloten item geen knop heeft om op te drukken.
const { chromium } = require('playwright');
let fouten = 0;
function ok(v, m) { if (v) { console.log('PASS ' + m); } else { fouten++; console.log('FAIL ' + m); } }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 480, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });

  const BASIS = 'http://localhost:8321/espanol-stefan.html';
  await page.goto(BASIS);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(BASIS);
  await page.waitForTimeout(600);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Kast' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // ---- 1. de kast staat er, in twee groepen ----
  await page.evaluate(() => { S.txp = 0; S.owned = {}; S.wear = {}; persist(); show('chispa'); });
  await page.waitForTimeout(500);

  const koppen = await page.evaluate(() =>
    Array.prototype.map.call(document.querySelectorAll('.zorglabel'), (e) => e.textContent));
  ok(koppen.some((k) => /lesson/i.test(k)), 'er is een kop voor wat je met lessen verdient');
  ok(koppen.some((k) => /practis|practic/i.test(k)), 'en een aparte kop voor wat je met oefenen verdient');

  const aantal = await page.locator('#kastBlok .shopitem').count();
  ok(aantal === 11, 'alle elf items staan in de kast (' + aantal + ')');

  // ---- 2. dicht is dicht: geen knop, wel een leesbaar doel ----
  const dicht = await page.evaluate(() => {
    var uit = { zonderKnop: 0, metSlot: 0, tekst: [] };
    Array.prototype.forEach.call(document.querySelectorAll('#kastBlok .shopitem'), function (el) {
      if (!el.querySelector('button[data-wear]')) {
        uit.zonderKnop++;
        var m = el.querySelector('.muted');
        if (m && m.textContent.indexOf('🔒') === 0) { uit.metSlot++; uit.tekst.push(m.textContent); }
      }
    });
    return uit;
  });
  ok(dicht.zonderKnop > 0, 'met nul lessen en nul oefening is er nog van alles dicht');
  ok(dicht.metSlot === dicht.zonderKnop, 'en alles wat dicht is draagt een slotje, geen dode knop');
  ok(dicht.tekst.some((t) => /lesson/i.test(t)), 'bij een lesitem staat hoeveel lessen je nog moet');
  ok(dicht.tekst.some((t) => /to go/i.test(t)), 'en bij een oefenitem hoeveel oefening je nog nodig hebt');

  // ---- 3. oefenen zet de oude rangen open, en dat wordt gevierd ----
  await page.evaluate(() => { S.txp = 0; S.owned = {}; persist(); });
  const gevierd = await page.evaluate(() => {
    var geteld = 0, oudeToast = window.toast;
    window.toast = function (t) { if (/wardrobe|kledingkast/i.test(t)) geteld++; };
    addXP(2100);
    window.toast = oudeToast;
    return { geteld: geteld, bigote: !!(S.owned && S.owned.bigote) };
  });
  ok(gevierd.bigote, 'genoeg oefening en de snor ligt in de kast');
  ok(gevierd.geteld >= 1, 'en dat gaat niet stilletjes: je krijgt het te horen');

  // ---- 4. aantrekken werkt, en is te zien aan haar ----
  await page.evaluate(() => {
    S.txp = 999999; S.wear = {}; S.owned = {};
    SHOP.forEach(function (it) { S.owned[it.id] = true; });
    persist(); show('chispa');
  });
  await page.waitForTimeout(500);
  const allesOpen = await page.locator('#kastBlok .shopitem button[data-wear]').count();
  ok(allesOpen === 11, 'met alles verdiend heeft elk item een knop (' + allesOpen + ')');

  const voor = await page.evaluate(() => document.querySelector('#petBox').innerHTML.length);
  await page.click('.shopitem button[data-wear="corona"]');
  await page.waitForTimeout(400);
  const na = await page.evaluate(() => document.querySelector('#petBox').innerHTML.length);
  ok(na > voor, 'op Draag klikken verandert werkelijk haar tekening');
  ok(await page.evaluate(() => !!S.wear.corona), 'en de kroon staat aan in haar profiel');
  const knopTekst = await page.textContent('.shopitem button[data-wear="corona"]');
  ok(/off|af/i.test(knopTekst), 'de knop zegt nu Doe af in plaats van Draag');

  // ---- 5. een plek, een ding: dit is de hele reden dat slots bestaan ----
  await page.click('.shopitem button[data-wear="gorro"]');
  await page.waitForTimeout(400);
  const hoofd = await page.evaluate(() => ({ corona: !!S.wear.corona, gorro: !!S.wear.gorro }));
  ok(hoofd.gorro && !hoofd.corona, 'de koksmuts duwt de kroon van haar hoofd af');
  await page.click('.shopitem button[data-wear="medalla"]');
  await page.waitForTimeout(400);
  const hals = await page.evaluate(() => ({ gorro: !!S.wear.gorro, medalla: !!S.wear.medalla }));
  ok(hals.gorro && hals.medalla, 'maar de medaille om haar hals raakt de muts niet aan');

  // ---- 6. het blijft staan als je weg bent geweest ----
  await page.reload();
  await page.waitForTimeout(900);
  const bewaard = await page.evaluate(() => ({ gorro: !!S.wear.gorro, medalla: !!S.wear.medalla, corona: !!S.wear.corona }));
  ok(bewaard.gorro && bewaard.medalla && !bewaard.corona, 'na herladen draagt ze nog precies wat je haar gaf');

  // ---- 7. alle zes de oude rangen komen echt op haar te staan ----
  const zichtbaar = await page.evaluate(() => {
    var uit = {};
    S.txp = PET_LEVELS[6].min + 5;
    S.wear = {};
    var kaal = petSVG().length;
    ['bigote', 'birrete', 'boina', 'gorro', 'medalla', 'corona'].forEach(function (id) {
      S.wear = {}; S.wear[id] = true;
      uit[id] = petSVG().length - kaal;
    });
    return uit;
  });
  Object.keys(zichtbaar).forEach((id) => ok(zichtbaar[id] > 60, id + ' voegt echt tekenwerk toe (+' + zichtbaar[id] + ')'));

  // ---- 8. en het is ook in het Nederlands te lezen ----
  const nl = await page.evaluate(() => {
    var uit = [];
    SHOP.forEach(function (it) { uit.push(itemHint(it)); });
    return uit;
  });
  ok(nl.length === 11 && nl.every((t) => t && t.length > 3), 'elk item heeft een uitleg in de taal van de gebruiker');

  const echt = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(echt.length === 0, 'geen JS-fouten onderweg' + (echt.length ? ': ' + echt[0] : ''));

  await browser.close();
  if (fouten) { console.log('\n' + fouten + ' TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
