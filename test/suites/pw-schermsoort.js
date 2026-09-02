// pw-schermsoort.js (2 sep, v23.229) — verdwijnt de schil om de opgave, of om het tabblad?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 30 aug: "nu is het nog teveel website." Gemeten op 390 pixels breed stond boven de eerste
// vraag van Woordjes: de sitekop met zijn naam en een zoekknop (72 pixels), de dagbalk (20), en
// eronder de voettekst. De eerste vraag begon op 221 van de 844 pixels. v23.209 zette daarom één
// veld in TABS (taak of overzicht) en liet show() dat als data-schermsoort op body zetten.
//
// Stefan, 2 sep: "als ik nu navigeer bijv naar woordjes of spelletjes dan mis ik nu wel de header
// met vamos Stefan, chispa en de zoekfunctie en ook de progress indicator."
//
// Allebei waar, en dat kan omdat de vraag te grof was. Het TABBLAD besliste, terwijl de TOESTAND
// hoort te beslissen. Woordjes tijdens je dagles is één opgave: daar geldt de meting van 30 aug.
// Woordjes waar je zelf naartoe klikt is je eigen sessie, en daar is het wegnemen van je naam, je
// zoekknop en je dagbalk geen rust maar verlies.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ELK SCHERM HEEFT EEN SOORT, en die komt uit TABS en niet uit een tweede lijst ergens anders.
//   2. BUITEN EEN LES HEEFT WOORDJES ZIJN SCHIL. Sitekop, dagbalk en voettekst staan er. Dit is de
//      melding van 2 sep, en dit is de proef die hem vasthoudt.
//   3. IN EEN LES IS ALLES WEG. Hetzelfde tabblad, andere toestand, andere uitkomst. Dit is het
//      GEBOUWDE controlegeval: zonder dit verschil bewijst proef 2 niets, want "overal alles tonen"
//      haalt hem ook. En het is meteen de meting van 30 aug, want dít is het scherm waar hij op sloeg.
//   4. EEN SCHERM DAT UIT ZICHZELF ÉÉN OPGAVE IS BLIJFT DAT. Chat en de weekmeting hebben geen les
//      nodig om een taakscherm te zijn.
//   5. EEN LOPEND SPEL IS EEN OPGAVE, HET SPEELTUINMENU NIET. Het verschil zit in funView, en dat
//      wisselt zonder dat er een tabblad verandert: de proef die de tweede aanroep van schilSync()
//      vasthoudt.
//   6. DE ONDERBALK BLIJFT BUITEN EEN LES OVERAL STAAN. Dat is geen smaak maar de uitgang.
//   7. IN EEN LES IS ER EEN UITGANG DIE EEN KNOP IS, minstens 44 bij 44. Dan is de onderbalk weg.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwSs' + Date.now());
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
    S.lang = 'nl';
    try { persist(); } catch (e) {}
  });

  // één meting: welk scherm staat er, welke soort draagt body, en wat is er van de schil te zien
  async function foto() {
    return page.evaluate(() => ({
      id: (TABS.filter(function (t) { return !document.getElementById('tab-' + t.id).classList.contains('hidden'); })[0] || {}).id,
      soort: document.body.getAttribute('data-schermsoort'),
      kop: !!document.querySelector('header').offsetParent,
      voet: !!(document.getElementById('appFooter') || {}).offsetParent,
      dag: !!(document.getElementById('goalLine') || {}).offsetParent,
      /* de onderbalk staat position:fixed, en dan is offsetParent altijd null. Op de hoogte meten
         is hier de enige eerlijke manier. */
      nav: document.getElementById('nav').getBoundingClientRect().height > 0,
      inLes: !!(typeof lesFlow !== 'undefined' && lesFlow && lesFlow.stap)
    }));
  }
  async function naar(id) {
    await page.evaluate((x) => show(x, true), id);
    await page.waitForTimeout(200);
    return foto();
  }

  // ---- 1. het veld ----
  console.log('\n-- 1. elk scherm draagt zijn soort --');
  const soorten = await page.evaluate(() => {
    const uit = { zonder: [], taak: [], overzicht: [] };
    TABS.forEach(function (t) {
      if (!t.soort) uit.zonder.push(t.id);
      else uit[t.soort].push(t.id);
    });
    uit.onbekend = tabSoort('bestaatniet');
    return uit;
  });
  console.log('   uit zichzelf een opgave : ' + soorten.taak.join(', '));
  console.log('   een pagina              : ' + soorten.overzicht.join(', '));
  ok(soorten.zonder.length === 0, 'geen enkel scherm mist het veld (' + (soorten.zonder.join(', ') || 'geen') + ')');
  ok(soorten.taak.length >= 2 && soorten.overzicht.length >= 8,
    'en ze staan niet allemaal in hetzelfde vakje (' + soorten.taak.length + ' opgave, ' + soorten.overzicht.length + ' pagina)');
  ok(soorten.onbekend === 'overzicht',
    'CONTROLE: een onbekend scherm valt terug op overzicht, dus het raakt niets kwijt');

  /* De app start bij binnenkomst zelf een dagles. Die pauzeren we, want proef 2 gaat over vrij
     navigeren en anders meet hij de les. */
  await page.evaluate(() => { try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {} });
  await page.waitForTimeout(400);
  const schoon = await page.evaluate(() => ({
    les: !!(typeof lesFlow !== 'undefined' && lesFlow),
    onbekend: schermSoort('bestaatniet')
  }));
  ok(!schoon.les, 'CONTROLE: er loopt geen les meer, dus de lus hieronder meet het vrij navigeren');
  ok(schoon.onbekend === 'overzicht',
    'en buiten een les valt een onbekend scherm ook op overzicht terug (' + schoon.onbekend + ')');

  // ---- 2, 4, 6. vrij navigeren ----
  console.log('\n-- 2, 4 en 6. vrij navigeren: waar staat je schil --');
  const ids = await page.evaluate(() => TABS.map(function (t) { return t.id; }));
  const vrij = [];
  for (const id of ids) vrij.push(await naar(id));
  vrij.forEach(function (m) {
    console.log('   ' + String(m.id).padEnd(12) + String(m.soort).padEnd(11) +
      'kop ' + (m.kop ? 'ja ' : 'nee') + ' · voet ' + (m.voet ? 'ja ' : 'nee') +
      ' · dagbalk ' + (m.dag ? 'ja ' : 'nee') + ' · onderbalk ' + (m.nav ? 'ja' : 'NEE'));
  });
  const w = vrij.filter(function (m) { return m.id === 'woorden'; })[0];
  const v = vrij.filter(function (m) { return m.id === 'vertalen'; })[0];
  const sp = vrij.filter(function (m) { return m.id === 'speeltuin'; })[0];
  ok(w && w.kop && w.dag && w.voet && w.soort === 'overzicht',
    'Woordjes heeft buiten een les zijn sitekop, dagbalk en voettekst (' + JSON.stringify(w) + ')');
  ok(v && v.kop && v.dag, 'Vertalen ook');
  ok(sp && sp.kop && sp.dag, 'en het speeltuinmenu ook');
  const opgaven = vrij.filter(function (m) { return m.soort === 'taak'; });
  console.log('   ook zonder les een opgave: ' + opgaven.map(function (m) { return m.id; }).join(', '));
  ok(opgaven.length >= 2 && opgaven.every(function (m) { return !m.kop && !m.dag && !m.voet; }),
    'chat en de weekmeting blijven ook zonder les een taakscherm (' + opgaven.length + ')');
  ok(vrij.every(function (m) { return m.nav; }),
    'en de onderbalk staat overal, want buiten een les is dat je uitgang');

  // ---- 5. het lopende spel ----
  console.log('\n-- 5. een lopend spel is wél een opgave --');
  const menu = await naar('speeltuin');
  await page.evaluate(() => speelNaar('mem'));
  await page.waitForTimeout(400);
  const spel = await foto();
  await page.evaluate(() => { funView = null; renderFun(); });
  await page.waitForTimeout(300);
  const terug = await foto();
  console.log('   menu ' + menu.soort + ' · in het spel ' + spel.soort + ' · terug ' + terug.soort);
  ok(menu.soort === 'overzicht' && menu.kop, 'het menu is een pagina en houdt zijn kop');
  ok(spel.soort === 'taak' && !spel.kop && !spel.dag, 'een lopend spel is een opgave en de schil gaat weg');
  ok(terug.soort === 'overzicht' && terug.kop,
    'CONTROLE: en hij komt terug zodra je het spel verlaat, zonder dat er een tabblad wisselt');

  // ---- 3. het gebouwde controlegeval: in een les ----
  console.log('\n-- 3. in een les is alles weg (hetzelfde tabblad, andere toestand) --');
  await page.evaluate(() => { show('lessen', true); lesFlowStart(); });
  await page.waitForTimeout(900);
  const inLes = [];
  for (const id of ['woorden', 'vertalen', 'speeltuin', 'lezen', 'lessen']) inLes.push(await naar(id));
  inLes.forEach(function (m) {
    console.log('   ' + String(m.id).padEnd(12) + String(m.soort).padEnd(11) +
      'kop ' + (m.kop ? 'ja ' : 'nee') + ' · dagbalk ' + (m.dag ? 'ja ' : 'nee') +
      ' · les loopt ' + (m.inLes ? 'ja' : 'NEE'));
  });
  ok(inLes.every(function (m) { return m.inLes; }),
    'CONTROLE: de les loopt nog op elk van die schermen, dus dit meet de toestand');
  ok(inLes.every(function (m) { return m.soort === 'taak' && !m.kop && !m.dag && !m.voet; }),
    'in een les is elk scherm een opgave en is de schil weg');
  const wLes = inLes.filter(function (m) { return m.id === 'woorden'; })[0];
  ok(w.kop && !wLes.kop,
    'en Woordjes geeft dus twee verschillende antwoorden op dezelfde vraag, afhankelijk van de toestand');

  console.log('\n-- en het getal waar het op 30 aug om begon --');
  const hoog = await page.evaluate(() => {
    show('woorden', true);
    const k = document.querySelector('#tab-woorden .card');
    return k ? Math.round(k.getBoundingClientRect().top) : null;
  });
  await page.waitForTimeout(200);
  console.log('   in een les begint de eerste kaart van Woordjes op ' + hoog + ' van de 844 pixels');
  ok(hoog !== null && hoog < 150, 'boven de opgave staat minder dan 150 pixels (was 221)');

  // ---- 7. de uitgang in een les ----
  console.log('\n-- 7. de uitgang tijdens een les is een knop --');
  const les = await page.evaluate(() => {
    const x = document.getElementById('btnLesPauze');
    const r = x ? x.getBoundingClientRect() : null;
    return { tag: x ? x.tagName : null,
             h: r ? Math.round(r.height) : 0, w: r ? Math.round(r.width) : 0,
             links: r ? Math.round(r.left) : null,
             navWeg: document.getElementById('nav').getBoundingClientRect().height === 0,
             onderstreept: x ? getComputedStyle(x).textDecorationLine : null };
  });
  console.log('   ' + JSON.stringify(les));
  ok(les.navWeg, 'CONTROLE: in een les is de onderbalk weg, dus deze knop is de enige uitgang');
  ok(les.tag === 'BUTTON', 'de uitgang is een knop en geen tekstlink');
  ok(les.h >= 44 && les.w >= 44, 'en hij is minstens 44 bij 44 (' + les.w + ' bij ' + les.h + ', was 20 hoog)');
  ok(les.links < 100, 'en hij staat links, waar een sluitknop hoort (' + les.links + ')');
  ok(les.onderstreept === 'none', 'zonder onderstreping');

  const naKlik = await page.evaluate(() => {
    document.getElementById('btnLesPauze').click();
    return { lesWeg: !lesFlow, navTerug: document.getElementById('nav').getBoundingClientRect().height > 0 };
  });
  await page.waitForTimeout(400);
  const naFoto = await foto();
  console.log('   na de klik: ' + JSON.stringify(naKlik) + ' · ' + naFoto.soort);
  ok(naKlik.lesWeg && naKlik.navTerug,
    'en hij doet wat hij belooft: de les stopt en de onderbalk komt terug');
  ok(naFoto.soort === 'overzicht' && naFoto.kop && naFoto.dag,
    'en je schil komt in dezelfde beweging terug, zonder tabwissel (' + naFoto.soort + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
