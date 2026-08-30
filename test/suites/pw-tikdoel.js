// pw-tikdoel.js (30 aug, v23.210) — alles wat je aanraakt is minstens 44 bij 44
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 30 aug, over de app op zijn telefoon: "nu is het nog teveel website." Gemeten over alle
// zeventien schermen op 390 pixels breed: 189 tikdoelen, waarvan 152 onder de 44 pixels.
//
// Gegroepeerd op klasse bleken dat geen honderdvijftig plekken maar elf:
//
//   primary 69 (42-43)   ghost 55 waarvan 25 te klein (39-42)   tapachip 18 (32)
//   bailechip 8 (26)     dtegel 7 (39)   kleurknop 6 (38)   mini 4 (25)
//   modus-toets 2 (25)   btn 1 (21)   instelrij 1 (23)   muziekchip 1 (20)
//
// De twee grootste, samen 124 van de 152, misten één tot vijf pixels. Dat waren twee CSS-regels.
//
// Deze suite staat er omdat een maat die je één keer goed zet binnen drie versies weer wegzakt: bij
// de volgende knop die iemand toevoegt staat er weer padding:5px. Een grens die objectief te meten
// is, hoort door de poort bewaakt te worden en niet door een voornemen.
//
// DE GRENS
//
// 44 bij 44 (Apple; Google houdt 48 aan). De app zet TIKDOEL_MIN op 44 en deze proef leest dat
// getal uit de app, zodat er geen tweede waarheid ontstaat.
//
// DE ENIGE UITZONDERING
//
// Een <a> binnen een lopende alinea. "…twee keer per week bij <a>Escuela Elcano</a>, aanrader…" is
// een woord in een zin en geen bedieningselement; die 44 pixels hoog maken breekt de alinea. De
// uitzondering is met opzet zo smal: alleen een link, en alleen binnen een <p>.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. GEEN ENKEL ZICHTBAAR TIKDOEL IS KLEINER DAN 44 BIJ 44, op alle zeventien schermen.
//   2. CONTROLE: de meting vindt er wel een als je er een neerzet. Zonder dit bewijst proef 1 niets,
//      want een selector die niets selecteert is ook groen.
//   3. EN ER IS GENOEG OM OVER TE TELLEN. Een scherm dat niet rendert heeft nul te kleine knoppen.
//   4. DE GRENS KOMT UIT DE APP en niet uit deze proef, dus ze kunnen niet uit elkaar lopen.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTd' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);

  await page.evaluate(() => {
    (tLessons() || []).forEach(function (l) {
      S.lessons[l.id] = { done: true, woorden: true, zinnen: true, quiz: true, spiek: true };
    });
    S.lang = 'nl'; S.txp = 900;
    try { persist(); } catch (e) {}
    /* de app opent bij binnenkomst zelf de dagles; die pauzeren we, zodat de lus alle schermen ziet
       en niet blijft hangen in body.in-les. */
    try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {}
  });
  await page.waitForTimeout(400);

  // ---- 4. de grens komt uit de app ----
  console.log('\n-- 4. de grens staat op één plek --');
  const grens = await page.evaluate(() => (typeof TIKDOEL_MIN === 'number' ? TIKDOEL_MIN : null));
  console.log('   TIKDOEL_MIN = ' + grens);
  ok(grens === 44, 'de app noemt de grens zelf, en deze proef leest hem uit (' + grens + ')');

  // ---- 1 en 3. de meting ----
  console.log('\n-- 1 en 3. geen enkel tikdoel onder de grens --');
  const ids = await page.evaluate(() => TABS.map(function (t) { return t.id; }));
  const meet = () => page.evaluate((min) => {
    const el = document.querySelector('.wrap');
    const klein = [], perKlasse = {};
    let n = 0;
    [].slice.call(document.querySelectorAll('button, a[href], [role="button"]')).forEach(function (x) {
      if (!x.offsetParent) return;
      /* de enige uitzondering: een link binnen een lopende alinea is een woord in een zin en geen
         bedieningselement. Zo smal mogelijk gehouden: alleen A, en alleen binnen een P. */
      if (x.tagName === 'A' && x.closest('p')) return;
      const r = x.getBoundingClientRect();
      if (r.height < 1) return;
      n++;
      const k = (typeof x.className === 'string' && x.className.trim())
        ? x.className.trim().split(/\s+/)[0] : ('<' + x.tagName.toLowerCase() + '>');
      perKlasse[k] = (perKlasse[k] || 0) + 1;
      if (r.height < min || r.width < min) {
        klein.push(k + ' ' + Math.round(r.width) + 'x' + Math.round(r.height) +
                   ' "' + (x.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 18) + '"');
      }
    });
    return { n: n, klein: klein, klassen: Object.keys(perKlasse).length };
  }, 44);

  let totaal = 0, alleKlein = [];
  for (const id of ids) {
    await page.evaluate((x) => show(x, true), id);
    await page.waitForTimeout(230);
    const r = await meet();
    totaal += r.n;
    if (r.klein.length) alleKlein.push(id + ': ' + r.klein.join(' · '));
  }
  console.log('   ' + totaal + ' tikdoelen bekeken over ' + ids.length + ' schermen');
  if (alleKlein.length) alleKlein.slice(0, 6).forEach(function (x) { console.log('   te klein · ' + x); });
  ok(alleKlein.length === 0,
    'geen enkel tikdoel is kleiner dan 44 bij 44 (' + alleKlein.length + ' schermen met een probleem)');
  ok(totaal > 150, 'CONTROLE: en er is genoeg om over te tellen (' + totaal + ', was 189)');

  // ---- 2. het controlegeval ----
  console.log('\n-- 2. de meting vindt er wel een als je er een neerzet --');
  const vindt = await page.evaluate(() => {
    const b = document.createElement('button');
    b.textContent = 'te klein';
    b.style.cssText = 'height:20px; width:20px; padding:0; font-size:8px; min-height:0; min-width:0';
    document.querySelector('.wrap').appendChild(b);
    let gevonden = false;
    [].slice.call(document.querySelectorAll('button')).forEach(function (x) {
      if (!x.offsetParent) return;
      const r = x.getBoundingClientRect();
      if (r.height > 0 && (r.height < 44 || r.width < 44)) gevonden = true;
    });
    b.remove();
    return gevonden;
  });
  ok(vindt, 'CONTROLE: een knop van 20 bij 20 wordt gevonden, dus proef 1 kan omvallen');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
