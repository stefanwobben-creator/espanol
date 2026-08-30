// pw-schermsoort.js (30 aug, v23.209) — een scherm zegt zelf of het een opgave is of een pagina
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 30 aug: "nu is het nog teveel website." Gemeten op 390 pixels breed, met alle lessen open:
//
//   vertalen 0,4 scherm · lessen 0,4 · woorden 0,5 · chat 0,5 · meting 0,5 · speeltuin 0,8
//   oefenen 1,0 · lezen 1,7 · musica 2,4 · steun 2,9 · perfil 3,0 · cursus 3,1
//   spiekbrief 3,5 · privacy 3,6 · chispa 4,3 · voortgang 4,9 · toetsjes 12,5
//
// Het waren altijd al twee soorten scherm; er stond alleen nergens welke. Op een taakscherm van 0,4
// scherm hoog stond boven de eerste vraag: de sitekop met zijn naam en een zoekknop (72 pixels), de
// dagbalk (20), en eronder de voettekst. De eerste vraag begon op 221 van de 844 pixels.
//
// v23.209 zet één veld in TABS en laat show() dat als data-schermsoort op body zetten. De rest is
// CSS. Geen van de zeventig renderfuncties is aangeraakt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ELK SCHERM HEEFT EEN SOORT, en die komt uit TABS en niet uit een tweede lijst ergens anders.
//   2. OP EEN TAAKSCHERM ZIJN DE SITEKOP, DE DAGBALK EN DE VOETTEKST WEG. Dit is de eigenlijke regel.
//   3. CONTROLEGEVAL BIJ 2: op een overzichtsscherm staan ze er alle drie nog. Zonder dit verschil
//      bewijst proef 2 niets: alles verbergen haalt hem ook.
//   4. DE ONDERBALK BLIJFT OP EEN TAAKSCHERM STAAN. Dat is geen smaak maar de uitgang: buiten een
//      lopende les is dat de enige manier om weg te komen, en dit is de proef die voorkomt dat
//      iemand hem later "voor de rust" ook verbergt.
//   5. IN EEN LES IS ER EEN UITGANG DIE EEN KNOP IS. Tijdens een les verbergt v23.155 de onderbalk
//      al, dus dan is de pauzeknop het enige wat je hebt. Hij was een onderstreepte tekstspan van
//      twintig pixels; nu minstens 44 bij 44, en hij doet ook echt wat hij belooft.
//   6. EN DE OEFENING BEGINT HOGER OP HET SCHERM. Het getal waar het allemaal om begon.
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

  // ---- 1. het veld ----
  console.log('\n-- 1. elk scherm draagt zijn soort --');
  const soorten = await page.evaluate(() => {
    const uit = { zonder: [], taak: [], overzicht: [] };
    TABS.forEach(function (t) {
      if (!t.soort) uit.zonder.push(t.id);
      else uit[t.soort].push(t.id);
    });
    uit.viaFunctie = TABS.map(function (t) { return t.id + '=' + tabSoort(t.id); });
    uit.onbekend = tabSoort('bestaatniet');
    return uit;
  });
  console.log('   taak      : ' + soorten.taak.join(', '));
  console.log('   overzicht : ' + soorten.overzicht.join(', '));
  ok(soorten.zonder.length === 0, 'geen enkel scherm mist het veld (' + (soorten.zonder.join(', ') || 'geen') + ')');
  ok(soorten.taak.length >= 4 && soorten.overzicht.length >= 8,
    'en ze staan niet allemaal in hetzelfde vakje (' + soorten.taak.length + ' taak, ' + soorten.overzicht.length + ' overzicht)');
  ok(soorten.onbekend === 'overzicht',
    'CONTROLE: een onbekend scherm valt terug op overzicht, dus het raakt niets kwijt');

  /* De app start bij binnenkomst zelf een dagles, en die verbergt de onderbalk sinds v23.155. Die
     pauzeren we eerst, anders meet de lus hieronder in-les in plaats van de schermsoort. */
  await page.evaluate(() => { try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {} });
  await page.waitForTimeout(400);
  const schoon = await page.evaluate(() => document.body.className);
  ok(schoon.indexOf('in-les') === -1, 'CONTROLE: er loopt geen les meer, dus de lus meet de soort (body="' + schoon + '")');

  // ---- 2 t/m 4. de schil per scherm ----
  console.log('\n-- 2 t/m 4. de schil volgt de soort --');
  const ids = await page.evaluate(() => TABS.map(function (t) { return t.id; }));
  const meting = [];
  for (const id of ids) {
    await page.evaluate((x) => show(x, true), id);
    await page.waitForTimeout(220);
    meting.push(await page.evaluate(() => ({
      id: TABS.filter(function (t) { return !document.getElementById('tab-' + t.id).classList.contains('hidden'); })[0].id,
      soort: document.body.getAttribute('data-schermsoort'),
      kop: !!document.querySelector('header').offsetParent,
      voet: !!(document.getElementById('appFooter') || {}).offsetParent,
      dag: !!(document.getElementById('goalLine') || {}).offsetParent,
      /* de onderbalk staat position:fixed, en dan is offsetParent altijd null. Op de hoogte meten
         is hier de enige eerlijke manier. */
      nav: document.getElementById('nav').getBoundingClientRect().height > 0
    })));
  }
  const taken = meting.filter(function (m) { return m.soort === 'taak'; });
  const paginas = meting.filter(function (m) { return m.soort === 'overzicht'; });
  meting.forEach(function (m) {
    console.log('   ' + m.id.padEnd(12) + m.soort.padEnd(11) +
      'kop ' + (m.kop ? 'ja ' : 'nee') + ' · voet ' + (m.voet ? 'ja ' : 'nee') +
      ' · dagbalk ' + (m.dag ? 'ja ' : 'nee') + ' · onderbalk ' + (m.nav ? 'ja' : 'NEE'));
  });
  ok(taken.length >= 4 && taken.every(function (m) { return !m.kop && !m.voet && !m.dag; }),
    'op elk taakscherm zijn de sitekop, de dagbalk en de voettekst weg (' + taken.length + ' schermen)');
  ok(paginas.length >= 8 && paginas.every(function (m) { return m.kop && m.voet; }),
    'CONTROLE: op elk overzichtsscherm staan ze er nog (' + paginas.length + ' schermen)');
  ok(meting.every(function (m) { return m.nav; }),
    'de onderbalk staat overal, want buiten een les is dat je uitgang');

  // ---- 5. de uitgang in een les ----
  console.log('\n-- 5. de uitgang tijdens een les is een knop --');
  await page.evaluate(() => { show('lessen', true); lesFlowStart(); });
  await page.waitForTimeout(800);
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
    return { open: TABS.filter(function (t) { return !document.getElementById('tab-' + t.id).classList.contains('hidden'); }).map(function (t) { return t.id; }),
             lesWeg: !lesFlow, navTerug: document.getElementById('nav').getBoundingClientRect().height > 0 };
  });
  await page.waitForTimeout(400);
  console.log('   na de klik: ' + JSON.stringify(naKlik));
  ok(naKlik.lesWeg && naKlik.navTerug,
    'en hij doet wat hij belooft: de les stopt en de onderbalk komt terug');

  // ---- 6. het getal waar het om begon ----
  console.log('\n-- 6. de oefening begint hoger op het scherm --');
  const hoog = await page.evaluate(() => {
    show('woorden', true);
    const k = document.querySelector('#tab-woorden .card');
    return k ? Math.round(k.getBoundingClientRect().top) : null;
  });
  console.log('   de eerste kaart van Woordjes begint op ' + hoog + ' van de 844 pixels');
  ok(hoog !== null && hoog < 150, 'boven de oefening staat minder dan 150 pixels (was 221)');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
