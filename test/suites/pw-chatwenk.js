// pw-chatwenk.js (31 okt, v23.257) — kijkt Chispa mee tijdens het gesprek, en mag je het eerst
// zelf oplossen?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan: "hij zou direct op de eerste zin al feedback moeten geven met corrigeren, me echt helpen
// een goede zin te schrijven. nu doet ie dat helemaal niet."
//
// Dat klopte en het was met opzet: v23.144 haalde de correctie uit de beurt ("een gesprekspartner
// die elke zin verbetert is er geen") en v23.249 maakte dat af met alleenAntwoord:true. Alle
// feedback kwam daarna pas na afloop. Goed gesprek, slechte leraar.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. EEN FOUTE ZIN KRIJGT EERST EEN WENK, GEEN VERBETERING. Lyster en Saito (2010): een prompt
//      (wijzen dat er iets mis is) doet meer dan een recast (het goed voorzeggen). De uitleg staat
//      er dus nog niet, en dat is de proef die vóór v23.257 niet kon slagen.
//   2. JE KUNT HEM ALSNOG OPVRAGEN. Vastlopen mag, wegklikken niet (v23.150). Eén tik.
//   3. EEN HERKANSING KOST GEEN BEURT. Drie beurten is de maat van het blok (CHAT_BEURTEN); een
//      tweede poging op dezelfde zin is dezelfde beurt en niet een nieuwe.
//   4. TWEE POGINGEN EN DAN KOMT DE UITLEG VANZELF (CHAT_POGINGEN). Zelf zoeken is de oefening,
//      maar blijven zoeken zonder dat je verder komt is geen oefening meer.
//   5. EEN GOEDE ZIN KRIJGT GEEN KNOPPEN. Anders is "er is iets mis" geen bericht meer.
//   6. HET GESPREK LOOPT DOOR. Chispa antwoordt op wat je bedoelde, ook als de vorm rammelt.
//   7. EEN OORDEEL OVER EEN ANDERE ZIN VALT AF (v23.249: liever geen oordeel dan het verkeerde).
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

const GOED = 'Ayer comí una tortilla.';
const MIS = 'Ayer yo comer una tortilla.';
const VERBETERD = 'Ayer comí la tortilla.';
const OORDEEL = 'Na ayer hoort het indefinido: comí in plaats van comer.';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  // Het model wordt niet gebeld. De nabespreking keurt alles af wat het woord "comer" bevat: dat is
  // precies de zin hierboven, en de verbeterde versie komt er dan doorheen.
  let naCalls = 0;
  await page.route('**/api/ai/chat', (route) => {
    const body = JSON.parse(route.request().postData() || '{}');
    if (body.modus === 'nabespreking') {
      naCalls++;
      return route.fulfill({ status: 200, contentType: 'application/json',
        body: JSON.stringify({ ok: true, regels: (body.zinnen || []).map(function (z) {
          return { zin: z, oordeel: /comer/.test(z) ? OORDEEL : 'Die klopt.', goed: !/comer/.test(z) };
        }) }) });
    }
    return route.fulfill({ status: 200, contentType: 'application/json',
      body: JSON.stringify({ ok: true, es: 'Que rico. Y tu?', nl: 'Lekker. En jij?' }) });
  });

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwWk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);
  await page.evaluate(() => { S.lang = 'nl'; show('chat'); });
  await page.waitForTimeout(300);

  // ---- 1. een foute zin: eerst een wenk, nog geen verbetering ----
  console.log('\n-- 1. een foute zin krijgt eerst een wenk --');
  await page.fill('#chatInvoer', MIS);
  await page.click('#chatStuur');
  await page.waitForTimeout(900);
  const w = await page.evaluate((oordeel) => {
    const t = document.getElementById('chatWrap').textContent.replace(/\s+/g, ' ');
    const b = S.chat.beurten.filter(function (x) { return x.van === 'jij'; })[0] || {};
    return { tekst: t, goed: b.goed, pogingen: b.pogingen, toon: b.toon,
             oordeelInBeurt: (b.oordeel || '').indexOf('indefinido') !== -1,
             oordeelOpScherm: t.indexOf(oordeel) !== -1,
             herkansKnop: document.querySelectorAll('[data-chatherkans]').length,
             toonKnop: document.querySelectorAll('[data-chattoon]').length,
             beurtenTotaal: S.chat.beurten.length,
             chispaAntwoordde: S.chat.beurten.some(function (x) { return x.van === 'chispa' && /Que rico/.test(x.es || ''); }) };
  }, OORDEEL);
  ok(w.goed === false, 'de zin is als fout beoordeeld');
  ok(w.oordeelInBeurt, 'het oordeel is wel opgehaald en bewaard');
  ok(!w.toon, 'maar het staat nog niet aan (toon=' + w.toon + ')');
  ok(!w.oordeelOpScherm, 'en het staat dus niet op het scherm: eerst de wenk, niet het antwoord');
  ok(/iets niet goed/.test(w.tekst), 'er staat wel dat er iets mis is');
  ok(w.herkansKnop === 1 && w.toonKnop === 1, 'met twee knoppen eronder (' + w.herkansKnop + ' en ' + w.toonKnop + ')');
  ok(w.chispaAntwoordde, 'en het gesprek loopt gewoon door: Chispa heeft geantwoord');

  // ---- 2. zelf proberen kost geen beurt ----
  console.log('\n-- 2. een herkansing is dezelfde beurt --');
  const voorBeurten = w.beurtenTotaal;
  await page.click('[data-chatherkans]');
  await page.waitForTimeout(300);
  const inVeld = await page.evaluate(() => ({
    waarde: (document.getElementById('chatInvoer') || {}).value || '',
    melding: document.getElementById('chatWrap').textContent.replace(/\s+/g, ' ')
  }));
  ok(inVeld.waarde === MIS, 'je eigen zin staat terug in het veld om aan te passen');
  ok(/kost je geen beurt/.test(inVeld.melding), 'en het scherm zegt dat dit geen beurt kost');

  await page.fill('#chatInvoer', VERBETERD);
  await page.click('#chatStuur');
  await page.waitForTimeout(900);
  const na = await page.evaluate(() => {
    const b = S.chat.beurten.filter(function (x) { return x.van === 'jij'; })[0] || {};
    return { beurtenTotaal: S.chat.beurten.length, mijn: S.chat.beurten.filter(function (x) { return x.van === 'jij'; }).length,
             es: b.es, goed: b.goed, pogingen: b.pogingen,
             tekst: document.getElementById('chatWrap').textContent.replace(/\s+/g, ' '),
             knoppen: document.querySelectorAll('[data-chatherkans]').length };
  });
  ok(na.beurtenTotaal === voorBeurten, 'er is geen beurt bijgekomen (' + voorBeurten + ' → ' + na.beurtenTotaal + ')');
  ok(na.mijn === 1, 'en jij hebt er nog steeds één gezegd');
  ok(na.es === VERBETERD, 'de beurt draagt nu je verbeterde zin');
  ok(na.goed === true, 'die is goedgekeurd');
  ok(na.knoppen === 0, 'en de knoppen zijn weg');
  ok(/beurt 2\/3/.test(na.tekst), 'de teller staat op beurt 2 van 3, niet op 3 van 3 (' +
     (na.tekst.match(/beurt \d\/\d/) || ['geen teller'])[0] + ')');

  // ---- 3. twee keer mis: dan komt de uitleg vanzelf ----
  console.log('\n-- 3. twee pogingen en dan de uitleg --');
  await page.fill('#chatInvoer', MIS);
  await page.click('#chatStuur');
  await page.waitForTimeout(900);
  const p1 = await page.evaluate((o) => {
    const b = S.chat.beurten.filter(function (x) { return x.van === 'jij'; })[1] || {};
    return { toon: b.toon, pogingen: b.pogingen,
             opScherm: document.getElementById('chatWrap').textContent.indexOf(o) !== -1 };
  }, OORDEEL);
  ok(p1.pogingen === 1 && !p1.toon, 'na de eerste poging staat de uitleg er nog niet');
  ok(!p1.opScherm, 'en hij staat niet op het scherm');

  const knoppen2 = await page.locator('[data-chatherkans]');
  await knoppen2.last().click();
  await page.waitForTimeout(300);
  await page.fill('#chatInvoer', 'Ayer yo comer la tortilla.');
  await page.click('#chatStuur');
  await page.waitForTimeout(900);
  const p2 = await page.evaluate((o) => {
    const b = S.chat.beurten.filter(function (x) { return x.van === 'jij'; })[1] || {};
    return { toon: b.toon, pogingen: b.pogingen, max: CHAT_POGINGEN,
             opScherm: document.getElementById('chatWrap').textContent.indexOf(o) !== -1 };
  }, OORDEEL);
  ok(p2.pogingen === p2.max, 'na de tweede poging zijn de pogingen op (' + p2.pogingen + ' van ' + p2.max + ')');
  ok(p2.toon, 'en dan gaat de uitleg vanzelf aan');
  ok(p2.opScherm, 'hij staat ook echt op het scherm');

  // ---- 4. een goede zin krijgt geen knoppen ----
  console.log('\n-- 4. een goede zin krijgt een bevestiging en verder niets --');
  const nu = await page.evaluate(() => ({ klaar: chatKlaar(), door: !!S.chat.door }));
  if (nu.klaar) await page.evaluate(() => { S.chat.door = true; renderChat(); });
  await page.waitForTimeout(200);
  await page.fill('#chatInvoer', GOED);
  await page.click('#chatStuur');
  await page.waitForTimeout(900);
  const g = await page.evaluate(() => {
    const mijne = S.chat.beurten.filter(function (x) { return x.van === 'jij'; });
    const b = mijne[mijne.length - 1] || {};
    return { goed: b.goed, toon: b.toon,
             knoppen: document.querySelectorAll('[data-chatherkans]').length,
             vink: document.getElementById('chatWrap').textContent.indexOf('✓') !== -1 };
  });
  ok(g.goed === true, 'de goede zin is goedgekeurd');
  ok(g.toon === true, 'en het oordeel staat meteen aan, want er valt niets zelf op te lossen');
  ok(g.knoppen === 0, 'er staan geen herkansknoppen meer op het scherm');
  ok(g.vink, 'wel een vinkje');

  // ---- 5. een oordeel over een andere zin valt af ----
  console.log('\n-- 5. een oordeel over de verkeerde zin wordt niet getoond --');
  const mis = await page.evaluate(() => {
    const idx = S.chat.beurten.length;
    S.chat.beurten.push({ van: 'jij', es: 'Hola, que tal.' });
    renderChat();
    // het oordeel gaat over een zin die er niet staat: dat hoort te worden weggegooid
    return new Promise(function (klaar) {
      const echt = window.api;
      window.api = function () {
        window.api = echt;
        return Promise.resolve({ ok: true, regels: [{ zin: 'Een heel andere zin.', oordeel: 'Fout.', goed: false }] });
      };
      chatKeur(idx, 'Hola, que tal.');
      setTimeout(function () {
        const b = S.chat.beurten[idx] || {};
        klaar({ goed: b.goed, oordeel: b.oordeel || '', knoppen: document.querySelectorAll('[data-chatherkans]').length });
      }, 300);
    });
  });
  ok(mis.goed !== false, 'een oordeel over een andere zin maakt jouw zin niet fout (goed=' + mis.goed + ')');
  ok(!mis.oordeel, 'en er wordt niets van overgenomen');
  ok(mis.knoppen === 0, 'dus er verschijnen ook geen knoppen');

  ok(naCalls >= 4, 'de nabespreking is per zin aangeroepen (' + naCalls + 'x)');
  ok(errs.length === 0, 'geen pagina-fouten: ' + (errs.slice(0, 3).join(' | ') || 'geen'));

  await browser.close();
  console.log(fout ? '\n' + fout + ' GEFAALD' : '\nalles goed');
  process.exit(fout ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
