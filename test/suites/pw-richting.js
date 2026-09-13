// pw-richting.js (13 sep, v23.254) - staan de woordkaartjes standaard op produceren?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 13 september: "ik denk dat het beter is om van nederlands naar spaans te gaan
// (produceren) in plaats van andersom (herkennen), dus dit zou de default moeten zijn."
//
// De app was het zelf al met hem eens en zei het nergens. renderWordCheck(), de Laatste stap, toont
// de Nederlandse kant en laat je het Spaanse woord TYPEN, ongeacht S.dir. Dat is de enige stap die
// meetelt voor de A1-balk. Alle kaartjes ervoor oefenden standaard het omgekeerde, want
// defaultState() stond op dir:"es-nl".
//
// WAT DEZE SUITE BEWAAKT
//
//   1. EEN NIEUWE GEBRUIKER BEGINT PRODUCTIEF, en ziet dus de Nederlandse kant met de vraag "hoe
//      zeg je dit in het Spaans?".
//   2. DE LAATSTE STAP IS ALTIJD PRODUCTIEF. Dat was al zo en blijft zo, in beide standen. Dit is
//      het feit waar de standaard op berust; gaat dit om, dan klopt de redenering niet meer.
//   3. DE MIGRATIE ZET IEDEREEN EEN KEER OM, EN NOOIT TWEE KEER. Ze kan niet zien of je es-nl ooit
//      zelf koos, want dat werd nergens opgeschreven. Daarom legt de knop de keuze vanaf nu vast,
//      en respecteert de migratie die vlag.
//   4. DE KNOP BLIJFT DOEN WAT HIJ DEED, en zet de vlag.
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
  await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Test' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
  await page.evaluate(() => show('woorden'));
  await page.waitForTimeout(400);

  // ---------- 1. een nieuwe gebruiker begint productief ----------
  console.log('\n1. een verse gebruiker krijgt de Nederlandse kant');
  const vers = await page.evaluate(() => ({ standaard: defaultState().dir, nu: S.dir }));
  ok(vers.standaard === 'nl-es', 'defaultState() staat op nl-es (staat: "' + vers.standaard + '")');
  ok(vers.nu === 'nl-es', 'en het verse profiel ook (staat: "' + vers.nu + '")');

  const scherm = await page.evaluate(() => {
    const w = { id: 'proef-richting', es: 'la ventana', nl: 'het raam', tag: 'proef' };
    WORDS.push(w);
    delete S.srs[w.id];
    wQueue = [w]; wCur = w; wShown = false; wCheck = null; wRondeZet(wQueue);
    renderWord();
    return document.getElementById('wCard').innerText;
  });
  ok(scherm.indexOf('het raam') !== -1, 'de vraag is de Nederlandse kant');
  ok(scherm.indexOf('ventana') === -1, 'en het Spaanse woord staat er niet');
  ok(/Hoe zeg je dit in het Spaans/.test(scherm), 'en de app vraagt om te produceren');

  // ---------- 2. de Laatste stap is altijd productief ----------
  console.log('\n2. de stap die meetelt toetst produceren, in beide standen');
  const laatste = await page.evaluate(() => {
    const w = WORDS.filter((x) => x.id === 'proef-richting')[0];
    const uit = {};
    ['nl-es', 'es-nl'].forEach((d) => {
      S.dir = d;
      S.srs[w.id] = { box: zelfDrempel(), due: today(), n: 9 };
      wQueue = [w]; wCur = w; wCheck = null; wRondeZet(wQueue);
      renderWordCheck();
      uit[d] = { tekst: document.getElementById('wCard').innerText,
                 typen: !!document.getElementById('wCheckInp') };
    });
    S.dir = 'nl-es';
    return uit;
  });
  ['nl-es', 'es-nl'].forEach((d) => {
    ok(laatste[d].tekst.indexOf('het raam') !== -1, 'met S.dir=' + d + ' toont de Laatste stap de Nederlandse kant');
    ok(laatste[d].tekst.indexOf('ventana') === -1, '  en het antwoord staat niet op het scherm');
    ok(laatste[d].typen, '  en je moet het zelf typen (invoerveld aanwezig)');
  });

  // ---------- 3. de migratie ----------
  console.log('\n3. migratie 5: een keer om, en nooit over een eigen keuze heen');
  const mig = await page.evaluate(() => {
    const m5 = MIGRATIES.filter((m) => m.naar === 5)[0];
    if (!m5) return { bestaat: false };
    const nooitGekozen = { dir: 'es-nl' };
    const n1 = m5.doe(nooitGekozen);
    const n2 = m5.doe(nooitGekozen);         // tweede keer: er valt niets meer om te zetten
    const zelfGekozen = { dir: 'es-nl', dirGekozen: 1 };
    const z = m5.doe(zelfGekozen);
    const alAnders = { dir: 'nl-es' };
    const a = m5.doe(alAnders);
    return { bestaat: true, schema: SCHEMA, na1: nooitGekozen.dir, n1, n2,
             zelf: zelfGekozen.dir, z, alAnders: alAnders.dir, a };
  });
  ok(mig.bestaat, 'migratie 5 bestaat');
  ok(mig.schema === 5, 'en SCHEMA loopt mee (staat op ' + mig.schema + ')');
  ok(mig.na1 === 'nl-es' && mig.n1 === 1, 'wie nooit koos, gaat om (' + mig.na1 + ', ' + mig.n1 + ' gewijzigd)');
  ok(mig.n2 === 0, 'CONTROLE: en een tweede keer draaien doet niets (' + mig.n2 + ' gewijzigd)');
  ok(mig.zelf === 'es-nl' && mig.z === 0,
     'CONTROLE: wie zelf voor herkennen koos, houdt herkennen (' + mig.zelf + ')');
  ok(mig.alAnders === 'nl-es' && mig.a === 0, 'CONTROLE: wie al productief stond, blijft staan');

  // ---------- 4. de knop ----------
  console.log('\n4. de knop onder het kaartje draait om en legt de keuze vast');
  const knop = await page.evaluate(() => {
    const w = WORDS.filter((x) => x.id === 'proef-richting')[0];
    S.dir = 'nl-es'; delete S.dirGekozen;
    delete S.srs[w.id];
    wQueue = [w]; wCur = w; wShown = false; wCheck = null; wRondeZet(wQueue);
    renderWord();
    const b = document.getElementById('btnDir');
    const bestond = !!b;
    if (b) b.onclick();
    const na = { dir: S.dir, gekozen: S.dirGekozen, tekst: document.getElementById('wCard').innerText };
    const b2 = document.getElementById('btnDir');
    if (b2) b2.onclick();
    return { bestond, na, terug: S.dir, gekozenNaTerug: S.dirGekozen };
  });
  ok(knop.bestond, 'de knop staat er');
  ok(knop.na.dir === 'es-nl', 'een tik zet hem op herkennen ("' + knop.na.dir + '")');
  ok(knop.na.gekozen === 1, 'en legt vast dat jij dat koos, zodat geen standaard er ooit overheen gaat');
  ok(knop.na.tekst.indexOf('ventana') !== -1, 'en het kaartje toont nu de Spaanse kant');
  ok(knop.terug === 'nl-es' && knop.gekozenNaTerug === 1, 'terugtikken werkt, en de vlag blijft staan');

  ok(errs.length === 0, 'geen javascriptfouten' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));

  await browser.close();
  console.log(fout ? '\n' + fout + ' fout' : '\nalles groen');
  process.exit(fout ? 1 : 0);
})();
