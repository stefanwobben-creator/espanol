// pw-leesvert.js (31 aug, v23.219) — de trede tussen één woord en de hele tekst
//
// WAAROM DEZE SUITE ER IS
//
// Stefan: "ik vind de tekst nog te moeilijk hoor, begrijp de grote lijn maar heb nog DeepL nodig."
//
// Dat was niet wat ik gemeten had. Met alle lesswoorden in de doosjes komt leesBetekenis() op
// ongeveer 0,05 onbekende woorden per zin, en dat klopt ook: hij kent de woorden. Hij krijgt de zin
// niet rond, en dat is iets anders. Het leesscherm kon precies één ding, tik op een woord, dus bij
// een zin die niet rond kwam liep hij de app uit.
//
// EN HET ANDERE GETAL, DAT ZWAARDER WEEGT
//
// Uit zijn eigen nachtelijke logboek: woord 334, zin 130, quiz 81, gramwiz 50, conj 40, corrector
// 22, escucha 4, en LEZEN 0. Twintig bezoeken aan die pagina en nul signaal terug. Lezen was het
// enige onderdeel waar de app niets van hem leerde, en dus het enige waar hij niet kon sturen.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ELKE VERTALING HEEFT NET ZOVEEL ALINEA'S ALS DE TEKST. Dit is de controle die bij de liedjes
//      ontbrak en die daar drie verzonnen lessen opleverde. Een vertaling hoort bij precies één
//      alinea; loopt dat één plek uit de pas, dan staat overal de verkeerde regel en niets zegt het.
//   2. STAAT ER GEEN VERTALING, DAN STAAT ER GEEN KNOP. Vier van de vijf reeksen hebben er nog geen,
//      en een knop die niets doet is erger dan geen knop.
//   3. DE VERTALING STAAT ER NIET AL. Je leest eerst Spaans; dat is de hele reden dat het een tik is.
//   4. EN NA ÉÉN TIK STAAT HIJ ER, MET DE JUISTE TEKST BIJ DE JUISTE ALINEA.
//   5. DE TIK WORDT GETELD, en twee keer dezelfde alinea telt één keer. Anders meet je driftig
//      tikken in plaats van moeite.
//   6. DE TIK SLUIT DE WOORDTOOLTIP NIET, en de knop is een echt tikdoel (44 bij 44, v23.210).
//   7. DE TWEE TELLERS GAAN MEE NAAR DE SERVER. leesZoek telt sinds v23.21 en is nooit ergens heen
//      gegaan; zonder deze proef zakt dat zo weer weg.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwLv' + Date.now());
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
    try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {}
  });
  await page.waitForTimeout(400);

  // ---- 1. de tellingen ----
  console.log('\n-- 1. elke vertaling telt evenveel alinea\'s als de tekst --');
  const telling = await page.evaluate(() => {
    const mis = [], metVert = [];
    BOOK.forEach(function (h) {
      if (!h.vert) return;
      metVert.push(h.id);
      const paras = String(h.tekst).split('\n\n').filter(function (p) { return p.trim(); });
      if (paras.length !== h.vert.length) mis.push(h.id + ': ' + paras.length + ' es, ' + h.vert.length + ' nl');
      h.vert.forEach(function (r, i) { if (!String(r || '').trim()) mis.push(h.id + ' alinea ' + i + ' leeg'); });
    });
    return { metVert: metVert, zonder: BOOK.length - metVert.length, mis: mis };
  });
  console.log('   ' + telling.metVert.length + ' hoofdstukken met vertaling, ' + telling.zonder + ' zonder');
  ok(telling.mis.length === 0, 'geen enkele vertaling loopt uit de pas (' + (telling.mis.join('; ') || 'geen') + ')');
  ok(telling.metVert.length >= 10, 'en er is genoeg vertaald om iets te kunnen aantonen (' + telling.metVert.length + ')');
  /* v23.221: hier stond ok(telling.zonder > 0). Dat hield stand zolang er toevallig hoofdstukken
     zónder vertaling waren, en sinds Chispa en Don Quijote vertaald zijn is dat er geen meer. Toen
     viel deze proef om terwijl er niets kapot was.

     Dit is de derde keer in twee dagen dat een controlegeval sneuvelt omdat het van de data afhing
     (pw-morgen bij het morgenbericht, pw-stem bij de reeks zonder verteller, en nu deze). De regel
     die daaruit volgt: een controlegeval hoor je te BOUWEN, niet te VINDEN. Wat je vindt verdwijnt
     zodra iemand de data opruimt, en dan lijkt het net of de regel niet meer geldt. */
  ok(telling.zonder === 0,
    'elk hoofdstuk op de plank heeft nu een vertaling (' + telling.zonder + ' zonder)');

  // ---- 2 t/m 4. het scherm ----
  console.log('\n-- 2 t/m 4. het knopje en de onthulling --');
  /* Het geval "hoofdstuk zonder vertaling" bestaat op de plank niet meer, dus zetten we er zelf
     een neer. Dat is niet alleen netter maar ook scherper: nu weet je zeker dat het aan het
     ontbrekende veld ligt en niet aan iets anders in dat ene hoofdstuk. */
  const geen = await page.evaluate(() => {
    const hfd = { id: 'zonder-1', num: 1, deel: 'Proef', titel: 'Zonder vertaling', drempel: 0,
                  tekst: 'Primera frase.\n\nSegunda frase.', vragen: [], reflectie: '' };
    BOOK.push(hfd);
    let uit;
    try {
      show('lezen', true); startBoek('zonder-1');
      uit = { knoppen: document.querySelectorAll('#lezenCard .leesvertknop').length,
              alineas: document.querySelectorAll('#lezenCard p').length };
    } catch (e) { uit = { fout: e.message }; }
    BOOK.pop();
    return uit;
  });
  console.log('   verzonnen hoofdstuk zonder vert: ' + JSON.stringify(geen));
  ok(geen.knoppen === 0, 'een hoofdstuk zonder vertaling heeft geen enkel knopje');
  ok(geen.alineas >= 2, 'CONTROLE: en het hoofdstuk werd wel degelijk getekend, dus de nul zegt iets');

  const metId = telling.metVert[0];
  const voor = await page.evaluate((id) => {
    show('lezen', true); startBoek(id);
    const kaart = document.getElementById('lezenCard');
    const knoppen = kaart.querySelectorAll('.leesvertknop');
    const regels = kaart.querySelectorAll('.leesvertnl');
    const zichtbaar = [].slice.call(regels).filter(function (r) { return !r.classList.contains('weg'); });
    const k0 = knoppen[0] ? knoppen[0].getBoundingClientRect() : null;
    return { knoppen: knoppen.length, regels: regels.length, zichtbaar: zichtbaar.length,
             alineas: String(BOOK.filter(function (h) { return h.id === id; })[0].tekst).split('\n\n').filter(function (p) { return p.trim(); }).length,
             breed: k0 ? Math.round(k0.width) : 0, hoog: k0 ? Math.round(k0.height) : 0 };
  }, metId);
  console.log('   ' + metId + ': ' + JSON.stringify(voor));
  ok(voor.knoppen === voor.alineas, 'één knopje per alinea (' + voor.knoppen + ' van ' + voor.alineas + ')');
  ok(voor.zichtbaar === 0, 'en geen enkele Nederlandse regel staat er al: je leest eerst Spaans');
  ok(voor.breed >= 44 && voor.hoog >= 44, 'het knopje is een echt tikdoel (' + voor.breed + ' bij ' + voor.hoog + ')');

  await page.click('#lezenCard .leesvertknop');
  await page.waitForTimeout(250);
  const na = await page.evaluate((id) => {
    const kaart = document.getElementById('lezenCard');
    const regels = [].slice.call(kaart.querySelectorAll('.leesvertnl'));
    const open = regels.filter(function (r) { return !r.classList.contains('weg'); });
    const h = BOOK.filter(function (x) { return x.id === id; })[0];
    return { open: open.length, tekst: open[0] ? open[0].textContent.trim() : '',
             hoort: h.vert[0], geteld: Object.keys((S.leesVert || {})[id] || {}).length };
  }, metId);
  console.log('   na de tik: "' + na.tekst.slice(0, 60) + '..."');
  ok(na.open === 1, 'na één tik staat er precies één Nederlandse regel open');
  ok(na.tekst === na.hoort, 'en het is de regel die bij díe alinea hoort');

  // ---- 5. de telling ----
  console.log('\n-- 5. de tik is de meting --');
  ok(na.geteld === 1, 'de tik is geteld (' + na.geteld + ')');
  const dubbel = await page.evaluate((id) => {
    const k = document.querySelectorAll('#lezenCard .leesvertknop');
    k[0].click(); k[0].click();          // dicht en weer open: dezelfde alinea
    return Object.keys((S.leesVert || {})[id] || {}).length;
  }, metId);
  ok(dubbel === 1, 'CONTROLE: dezelfde alinea nog eens telt niet opnieuw (' + dubbel + ')');
  const tweede = await page.evaluate((id) => {
    const k = document.querySelectorAll('#lezenCard .leesvertknop');
    if (k[1]) k[1].click();
    return { n: Object.keys((S.leesVert || {})[id] || {}).length, stand: leesVertStand(BOOK.filter(function (x) { return x.id === id; })[0]) };
  }, metId);
  ok(tweede.n === 2, 'een tweede alinea telt wel (' + tweede.n + ')');
  ok(tweede.stand.totaal === voor.alineas,
    'en leesVertStand() weet hoeveel er te vertalen viel (' + tweede.stand.n + ' van ' + tweede.stand.totaal + ')');

  // ---- 6. de woordtooltip blijft werken ----
  console.log('\n-- 6. het woord opzoeken werkt nog gewoon --');
  const woord = await page.evaluate(() => {
    const w = document.querySelector('#lezenCard .lw');
    w.click();
    const u = document.getElementById('leesUitleg');
    return { open: u ? !u.classList.contains('weg') : false, woord: w.getAttribute('data-lw') };
  });
  ok(woord.open, 'op een woord tikken opent de uitleg nog steeds ("' + woord.woord + '")');

  // ---- 7. de tellers gaan mee naar de server ----
  console.log('\n-- 7. wat er naar de server gaat --');
  const payload = await page.evaluate(() => {
    const bron = String(logServer);
    return { zoek: bron.indexOf('payload.leesZoek') !== -1, vert: bron.indexOf('payload.leesVert') !== -1 };
  });
  ok(payload.zoek && payload.vert,
    'leesZoek en leesVert zitten in het logje (' + JSON.stringify(payload) + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
