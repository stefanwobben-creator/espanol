// pw-tegels.js (15 aug, v23.112) — doet elke tegel in de Speeltuin iets als je erop klikt?
//
// WAAROM DIT ER IS
//
// Stefan, na het installeren van v23.111: "alleen wie is dit niet klikbaar."
//
// De tegel was in v23.109 toegevoegd aan spelInfo(), maar de klikafhandeling stond in een aparte
// handgeschreven rij van tien wire-regels onder aan renderFun(). Negen tegels stonden er wel in,
// de tiende niet. De tegel tekende netjes en deed niets.
//
// Twee lijsten die met de hand synchroon gehouden worden, lopen uit elkaar. v23.112 haalt de
// koppeling uit spelInfo() zelf, zodat een tegel zonder afhandeling niet meer kan bestaan.
//
// WAAROM DE POORT HET NIET VING
//
// pw-omkeer controleerde "de tegel staat in de Speeltuin" door te tellen of het element bestond,
// en opende het scherm daarna met funView = "omkeer" in plaats van door te klikken. Zo'n check
// blijft groen terwijl de knop dood is.
//
// Deze suite loopt daarom over ALLE tegels uit spelInfo(), klikt er echt op, en eist dat er iets
// verandert. Dat vangt deze fout voor elke tegel die er ooit nog bij komt.
//
// v23.124: de tegels wonen niet meer allemaal op hetzelfde scherm. Wie gram:true draagt staat op de
// Grammatica-tab, de rest in de Speeltuin. Welke tab dat is leest deze suite uit datzelfde veld en
// niet uit een eigen lijstje: dat lijstje zou de zesde keer worden dat testcode een feit napraat dat
// al in de data staat (zie de kop van padvul.js).
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTeg' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  // alles zichtbaar, anders staat de helft onder "komt er straks bij" en zonder id op het scherm
  await page.evaluate(() => { S.lang = 'nl'; S.speelAlles = true; try { persist(); } catch (e) {} });

  const lijst = await page.evaluate(() => spelInfo().map((g) => ({ v: g.v, id: g.id, t: g.t, gram: !!g.gram })));

  console.log('\n-- de lijst --');
  ok(lijst.length >= 11, 'er staan ' + lijst.length + ' tegels in spelInfo()');
  ok(lijst.every((g) => g.v && g.id && g.t), 'elke tegel heeft een view, een id en een titel');
  ok(new Set(lijst.map((g) => g.id)).size === lijst.length, 'geen twee tegels met hetzelfde id');

  // naar het scherm waar deze tegel woont, in een schone staat
  async function naarThuis(gram) {
    await page.evaluate(() => { funView = null; });
    if (gram) {
      await page.evaluate(() => { gwSess = null; gcLeesId = null; show('spiekbrief'); });
    } else {
      await page.click('#nav button[data-tab="speeltuin"]');
      await page.waitForTimeout(200);
      await page.evaluate(() => { funView = null; renderFun(); });
    }
    await page.waitForTimeout(200);
  }

  console.log('\n-- elke tegel klikken --');
  const dood = [];
  for (const g of lijst) {
    await naarThuis(g.gram);

    const bestaat = await page.locator('#' + g.id).count();
    if (!bestaat) { dood.push(g.id + ' (staat niet op het scherm)'); continue; }

    const voor = await page.evaluate(() => ({
      view: funView,
      tab: (document.querySelector('#nav button.actief, #nav button.active') || {}).getAttribute
        ? (document.querySelector('#nav button.actief, #nav button.active') || {}).dataset.tab : null,
      kaart: (document.getElementById('funCard') || {}).innerText || ''
    }));

    await page.click('#' + g.id);
    await page.waitForTimeout(350);

    const na = await page.evaluate(() => ({
      view: funView,
      kaart: (document.getElementById('funCard') || {}).innerText || '',
      // Música is geen funView maar een eigen scherm; dan telt dat het scherm gewisseld is
      zichtbaar: Array.prototype.filter.call(document.querySelectorAll('section, .scherm, [id^="v-"]'),
        (s) => s.offsetParent !== null).map((s) => s.id).join(',')
    }));

    const veranderd = na.view !== voor.view || na.kaart !== voor.kaart;
    if (!veranderd) dood.push(g.id + ' (' + g.t + ')');
    ok(veranderd, g.id + ' → ' + (na.view || 'ander scherm') + (veranderd ? '' : ' DEED NIETS'));
  }

  console.log('\n-- de samenvatting --');
  ok(dood.length === 0, 'DE REGEL: geen enkele dode tegel (nu: ' + (dood.join(', ') || 'geen') + ')');

  // ---- controle: heeft deze suite tanden? ----
  // Een tegel zonder afhandeling moet hier omvallen. Simulatie: teken de Speeltuin, haal de
  // onclick van één tegel weg, klik, en kijk of er inderdaad niets verandert.
  await naarThuis(true);
  const tanden = await page.evaluate(() => {
    const el = document.getElementById('ftOmkeer');
    if (!el) return null;
    el.onclick = null;
    const voor = funView;
    el.click();
    return { voor: voor, na: funView };
  });

  console.log('\n-- controle --');
  ok(tanden && tanden.voor === tanden.na,
    'CONTROLE: zonder onclick verandert er niets, dus deze meting kán een dode tegel zien');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
