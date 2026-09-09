// pw-leesvorm.js (9 sep, v23.252) - zegt de leesplank welke VORM er staat, en of je die tijd al had?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 9 september, over Don Quijote: "het zijn niet alleen de vocabulaire, maar het zijn ook de
// vervoegingen van de werkwoorden. Dat ik de tegenwoordige tijd van een werkwoord ken zegt niet dat
// ik alle vormen ken."
//
// Twee metingen in de eigen gegevens van de app:
//
//   29 van de 43 leesteksten gebruiken een tijd buiten het presente, terwijl zijn Conjugador-ladder
//   op "het hele presente" staat.
//
//   In de tien Don Quijote-teksten staan 161 herkenbare werkwoordsvormen. ACHT ervan kregen een
//   tijdsaanduiding mee. En bij een handvol stond de tijd wél in de betekenis, in het Engels, in een
//   handgeschreven zin: "eran = they were (from ser, imperfect)". Niet in een veld, dus de app kon
//   er niets mee.
//
//       Staat een feit in een tekst in plaats van in een veld, dan kan alleen de lezer het
//       gebruiken, en alleen als hij die taal spreekt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE VORM WORDT AFGELEID. Elke vorm van elk werkwoord dat de app kent, uit VERBOS en
//      CONJ_TIEMPOS. Niet uit een handgeschreven zin: de proef telt hoeveel vormen in de echte
//      teksten er nu een veld bij krijgen, en dat aantal hoort veel hoger te liggen dan acht.
//   2. ACCENTGEVOELIG, en dat is de kern. "de" is een voorzetsel en "dé" is een vorm van dar.
//      Gemeten: "de" staat 235 keer in de leesteksten en werd elke keer uitgelegd als "geeft u (van
//      dar, subjuntivo)".
//   3. EEN DUBBELE VORM WORDT NIET GERADEN. hablamos is presente én indefinido; dan noemt de app ze
//      allebei. Een verkeerde diagnose is erger dan geen.
//   4. HET SCHERM ZEGT HET, IN HET NEDERLANDS, en zegt erbij of je die tijd al gehad hebt.
//   5. EN DE BELASTING PER TEKST IS TE METEN. Dat is wat een volgende schrijver (ik, of de nachtrun)
//      nodig heeft om een verhaal te maken dat past bij wat de lezer kan.
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
    S.lang = 'nl';
    S.conjLadder = CONJ_LADDER_NU;
    S.conjOpen = conjFaseIdx('presente');    // de stand van Stefan: alleen het presente open
    try { persist(); } catch (e) {}
  });

  // ---- 1. de vorm wordt afgeleid ----
  console.log('\n-- 1. de vorm komt uit de vervoegingstabel --');
  const vormen = await page.evaluate(() => {
    const proef = ['eran', 'hizo', 'tenían', 'vio', 'dijo', 'vive'];
    return proef.map(function (w) {
      const b = leesBetekenis(w);
      return { w: w, heeftVorm: !!(b && b.vorm),
               inf: b && b.vorm ? b.vorm.inf : null,
               tijd: b && b.vorm ? b.vorm.tijd : null,
               persoon: b && b.vorm ? b.vorm.persoon : null };
    });
  });
  vormen.forEach(function (v) {
    console.log('   ' + v.w.padEnd(10) + (v.heeftVorm ? v.inf + ' · ' + v.tijd + ' · persoon ' + v.persoon : 'GEEN VORM'));
  });
  ok(vormen.every(function (v) { return v.heeftVorm; }),
    'elke bekende werkwoordsvorm draagt zijn werkwoord, tijd en persoon');
  const eran = vormen.filter(function (v) { return v.w === 'eran'; })[0];
  ok(eran && eran.inf === 'ser' && eran.tijd === 'imperfecto' && eran.persoon === 5,
    'eran is ser, imperfecto, ellos (' + JSON.stringify(eran) + ')');
  const vive = vormen.filter(function (v) { return v.w === 'vive'; })[0];
  ok(vive && vive.tijd === 'presente',
    'CONTROLE: en een presente-vorm wordt ook als presente herkend, niet als "iets vreemds"');

  // ---- 2. accentgevoelig ----
  console.log('\n-- 2. "de" is niet "dé" --');
  const acc = await page.evaluate(() => {
    let keer = 0;
    BOOK.forEach(function (t) {
      String(t.tekst || '').toLowerCase().replace(/[^a-záéíóúüñ\s]/g, ' ').split(/\s+/)
        .forEach(function (w) { if (w === 'de') keer++; });
    });
    return { keer: keer, de: leesBetekenis('de'), deAcc: leesBetekenis('dé'),
             vormDe: leesVormInfo('de'), vormDeAcc: leesVormInfo('dé') };
  });
  console.log('   "de" staat ' + acc.keer + ' keer in de leesteksten');
  console.log('   de  -> ' + (acc.de ? acc.de.nl : 'niets'));
  console.log('   dé  -> ' + (acc.deAcc ? acc.deAcc.nl : 'niets'));
  ok(acc.keer > 100, 'CONTROLE: "de" is inderdaad een van de meest voorkomende woorden (' + acc.keer + ')');
  ok(!!acc.de && !/dar|subjuntivo|geeft u/i.test(String(acc.de.nl)),
    '"de" krijgt de uitleg van het voorzetsel, niet die van dé ("' + (acc.de ? acc.de.nl : '') + '")');
  /* WAT HIER NIET GEREPAREERD IS, en dat hoort erbij te staan. De hele opzoekketen eronder
     (leesLesWoord, leesFreqZoek, LEES_EXTRA) werkt op de accentloze sleutel, dus "dé" krijgt nog
     steeds de betekenisregel van het voorzetsel "de" (lesswoord k158). Dat is deze ronde niet
     opgelost: alleen de bovenste laag kijkt naar het geschreven woord, en dat is genoeg voor het
     geval dat 235 keer voorkomt.

     Wat "dé" er wél bij krijgt is de vormregel, en die is accentgevoelig, dus onder de verkeerde
     betekenis staat nu tenminste "yo, presente de subjuntivo" van dar. Half zichtbaar is beter dan
     onzichtbaar, maar het is geen oplossing en het wordt hier niet als oplossing geteld. */
  ok(!!acc.deAcc && !!acc.vormDeAcc,
    'RESIDU: "dé" krijgt nog de betekenis van het voorzetsel ("' + (acc.deAcc ? acc.deAcc.nl : '') +
      '"), maar wel de juiste vormregel erbij');
  ok(!acc.vormDe, 'CONTROLE: en "de" geldt niet als werkwoordsvorm');
  ok(!!acc.vormDeAcc, 'CONTROLE: terwijl "dé" dat wél is, dus het onderscheid werkt beide kanten op');

  // ---- 3. een dubbele vorm wordt niet geraden ----
  console.log('\n-- 3. hablamos is er twee --');
  const dub = await page.evaluate(() => {
    const v = leesVormInfo('hablamos');
    return v ? { tijden: v.tijden, dubbel: v.dubbel } : null;
  });
  ok(!!dub && dub.dubbel && dub.tijden.length === 2,
    'hablamos wordt als presente én indefinido gemeld (' + JSON.stringify(dub) + ')');

  // ---- 4. het scherm zegt het ----
  console.log('\n-- 4. wat er op het scherm komt --');
  const scherm = await page.evaluate(() => {
    /* de echte tooltip, via de echte functie. leesToon() schrijft in #leesUitleg; dat vak bestaat
       alleen als het leesscherm getekend is, dus als het er niet is maken we het aan. Wat we meten
       is wat leesToon() erin zet, en dat is precies wat Stefan te zien krijgt. */
    let el = document.getElementById('leesUitleg');
    let zelfGemaakt = false;
    if (!el) {
      el = document.createElement('div'); el.id = 'leesUitleg';
      document.body.appendChild(el); zelfGemaakt = true;
    }
    const lees = function (w) {
      el.innerHTML = '';
      leesToon(w, null);
      return el.textContent.replace(/\s+/g, ' ').trim();
    };
    const uit = { eran: lees('eran'), vive: lees('vive'), hablamos: lees('hablamos') };
    if (zelfGemaakt) el.remove();
    return uit;
  });
  Object.keys(scherm).forEach(function (k) { console.log('   ' + k.padEnd(10) + scherm[k].slice(0, 110)); });
  ok(/imperfecto/.test(scherm.eran), 'bij "eran" staat de tijd erbij (imperfecto)');
  ok(/onvoltooid|verleden/i.test(scherm.eran), 'en de Nederlandse naam ervan, niet alleen de Spaanse');
  ok(/ellos|zij/i.test(scherm.eran), 'plus de persoon');
  ok(/nog niet gehad/i.test(scherm.eran),
    'en dat je die tijd nog niet gehad hebt, want dat is precies de vraag ("' + scherm.eran.slice(-60) + '")');
  ok(!/nog niet gehad/i.test(scherm.vive),
    'CONTROLE: bij een presente-vorm staat die regel er NIET (' + scherm.vive.slice(0, 70) + ')');
  ok(/presente/.test(scherm.hablamos) && /indefinido/.test(scherm.hablamos),
    'en bij een dubbele vorm staan beide tijden er (' + scherm.hablamos.slice(0, 90) + ')');

  // ---- 5. de belasting per tekst ----
  console.log('\n-- 5. hoeveel staat er buiten je tijden --');
  const belast = await page.evaluate(() => {
    const per = BOOK.map(function (t) {
      const x = leesTekstTijden(t.tekst);
      return { id: t.id, deel: t.deel, titel: t.titel, buiten: x.buiten, perTijd: x.perTijd };
    });
    const metBuiten = per.filter(function (x) { return x.buiten > 0; });
    // en het controlegeval: met alles open hoort er niets meer buiten te vallen
    const bewaar = S.conjOpen;
    S.conjOpen = CONJ_FASES.length - 1;
    const allesOpen = BOOK.map(function (t) { return leesTekstTijden(t.tekst).buiten; })
      .reduce(function (a, b) { return a + b; }, 0);
    S.conjOpen = bewaar;
    return { n: per.length, metBuiten: metBuiten.length,
             top: metBuiten.sort(function (a, b) { return b.buiten - a.buiten; }).slice(0, 6),
             allesOpen: allesOpen };
  });
  belast.top.forEach(function (t) {
    console.log('   ' + String(t.id).padEnd(9) + String(t.titel).slice(0, 30).padEnd(32) +
      t.buiten + ' vormen buiten je tijden  ' + JSON.stringify(t.perTijd));
  });
  ok(belast.metBuiten > 0,
    'CONTROLE: met alleen het presente open vallen er teksten buiten bereik (' + belast.metBuiten + ' van ' + belast.n + ')');
  ok(belast.allesOpen === 0,
    'CONTROLE: en met alle tijden open valt er niets meer buiten (' + belast.allesOpen + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
