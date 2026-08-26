// pw-wachtzin.js (21 aug, v23.165) — zegt de app wanneer er iets komt, en klopt het getal dat hij noemt?
//
// WAAROM DIT ER IS
//
// Twee meldingen van Stefan op v23.162, allebei over een getal dat er wel is maar niet stond.
//
// 1. "maar ik zie ook nog steeds: Wat je nu haalt is nog niet te meten: daar zijn drie
//    weekmetingen voor nodig."
//
//    De crash van v23.162 was echt en is weg, maar er was tegelijk iets anders waar: er zijn drie
//    weekmetingen nodig mét het veld dekw, en dat veld bestaat pas sinds 10 augustus. Op 21 augustus
//    zijn dat er hoogstens twee. Twee verschillende oorzaken achter precies hetzelfde scherm, en dat
//    is de fout die v23.162 al beschreef. Nu ze niet meer allebei kunnen, hoort het scherm te zeggen
//    wélke van de twee het is, en dat kan het weten.
//
// 2. "het woordenboek was ooit meer dan 4000 woorden, nu zijn het veel minder."
//
//    Niets gekrompen. Het woordenboek toont 2.120 woordgroepen uit je lessen; de zoeklijst erachter
//    heeft er 4.219 en die zijn nog steeds te vinden. Wat verdween was de zin die dat vertelde, in
//    een opruimronde in v23.6. De zin deed dus werk, en dat bleek pas toen hij weg was.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE WACHTZIN TELT. Niet alleen "er zijn er meer nodig" maar hoeveel je er hebt, waarover ze
//      verspreid staan, en over hoeveel dagen je er bent als je blijft komen.
//      v23.198: de eenheid is van weken naar dagen gegaan, want het weekritme volgde de kalender in
//      plaats van de gebruiker. De reden dat deze suite bestaat is niet veranderd.
//   2. OP BEIDE SCHERMEN HETZELFDE. De zin stond op twee plekken met twee formuleringen; nu komt hij
//      uit één functie. Twee plekken die hetzelfde uitleggen lopen uit elkaar.
//   3. EN HIJ VERDWIJNT ALS HET KAN. Het controlegeval: bij drie metingen staat er een tempo en geen
//      excuus meer. Een wachtzin die blijft staan terwijl er gerekend wordt is erger dan geen.
//   4. DE WOORDEN ACHTER DE ZOEKBALK ZIJN ER NOG. Dit is het antwoord op Stefans tweede melding, en
//      het is een meting en geen belofte: er wordt een woord opgezocht dat in geen enkele les zit,
//      en dat hoort gevonden te worden. Zolang dat lukt is er niets gekrompen, wat de kop er ook
//      over zegt of zwijgt.
//
// WAT DEZE SUITE BEWUST NIET DOET
//
// Eisen dat het getal 4.219 ergens op het scherm staat. Ik heb het teruggezet, eerst in de kopregel
// en daarna in de placeholder, en beide keren ging de poort dicht op pw-dic52 en pw-zoekwoord. Die
// twee bewaken wat Stefan zelf vroeg in v23.6 en v23.7: die regel kort, dat bijschrift weg. Dit is
// dus geen bug maar een botsing tussen wat hij toen vroeg en wat hij nu mist, en die keuze is aan
// hem. Wat hier wel staat is de meting die de vraag beantwoordt.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwWz' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    // ---- 1 t/m 3. de wachtzin ----
    /* v23.198: hier stonden twee WEEKmetingen en de zin telde naar drie maandagen toe. De
       voorspelling rekent sinds die versie op dagpunten, precies omdat het weekritme de kalender
       volgde in plaats van de gebruiker (Stefan, 26 aug: "als je dagelijks meet en je ziet iemand
       komt dagelijks heb je sneller goede data"). De reden dat deze suite bestaat verandert daar
       niet door: het scherm hoort te zeggen hoeveel je er hebt en wanneer de volgende komt, in
       plaats van alleen dat er meer nodig zijn. Alleen de eenheid is veranderd.

       Drie dagpunten over drie dagen: te weinig bewijs én te weinig spreiding, dus de zin hoort er
       nog te staan. */
    S.meting = {};
    S.dagMeting = {};
    for (var dI = 2; dI >= 0; dI--) {
      S.dagMeting[addDays(today(), -dI)] = { dekw: { A1: 180 + (2 - dI) * 4, A2: 90 }, dek: { A1: 150, A2: 70 } };
    }
    S.doelNiv = 'A1'; S.doelDatum = '2026-12-01';
    uit.stand = tempoStand('A1');
    uit.zin = tempoWachtZin('A1');

    show('voortgang', true); renderStats();
    const scherm = document.getElementById('statsCard').textContent.replace(/\s+/g, ' ');
    uit.opVoortgang = scherm.indexOf(uit.zin.trim().slice(0, 40)) !== -1;
    uit.hoeVaak = (scherm.match(/dagmeting/g) || []).length;
    uit.fragment = (scherm.match(/Wat je nu haalt[^]{0,150}/) || [''])[0];

    // 3. het controlegeval: met genoeg dagpunten over genoeg dagen is de wachtzin weg
    S.dagMeting = {};
    for (var dJ = 13; dJ >= 0; dJ--) {
      S.dagMeting[addDays(today(), -dJ)] = { dekw: { A1: 180 + (13 - dJ) * 4, A2: 90 }, dek: { A1: 150, A2: 70 } };
    }
    uit.metGenoeg = {
      stand: tempoStand('A1'),
      zin: tempoWachtZin('A1'),
      tempo: (function () { try { const m = tempoMeting('A1'); return m ? m.gem : null; } catch (e) { return 'FOUT'; } })()
    };
    renderStats();
    uit.metGenoegOpScherm = document.getElementById('statsCard').textContent.indexOf('dagmeting') === -1;
    S.dagMeting = {};

    // ---- 4 en 5. het woordenboek noemt de zoeklijst, en dat getal is waar ----
    S.meting = {};
    dicZoek = ''; dicOpen = null; dicAutoQ = null;
    show('woorden', true);
    try { dicModal(); } catch (e) {}
    renderDic();
    const dic = document.getElementById('dicCard').textContent.replace(/\s+/g, ' ');
    uit.dicKop = dic.slice(0, 110);
    uit.freqN = FREQ.length;
    uit.uitLessen = dicGroups(dicZichtbareWoorden()).length;

    /* En nu het punt: klopt dat getal met iets dat je ook echt kunt vinden? Zoek een woord op dat in
       geen enkele les zit. Vindt de zoekbalk het niet, dan adverteert de kop een lijst die er niet
       is, en dat is precies hoe die zin ooit kon verdwijnen zonder dat iemand het merkte. */
    const inLessen = {};
    WORDS.forEach(function (w) {
      inLessen[String(w.es).replace(/^(el|la|los|las|un|una)\s+/i, '').trim().toLowerCase()] = 1;
    });
    const buiten = FREQ.filter(function (f) {
      return !inLessen[String(f[0]).toLowerCase()] && /^[a-záéíóúñ]{5,9}$/.test(f[0]);
    });
    uit.buitenN = buiten.length;
    const proef = buiten[3];
    uit.proef = proef ? proef[0] + ' = ' + proef[1] : null;
    if (proef) {
      dicZoek = proef[0]; dicOpen = null; dicAutoQ = null;
      renderDic();
      const t = document.getElementById('dicCard').textContent.toLowerCase();
      uit.gevonden = t.indexOf(String(proef[0]).toLowerCase()) !== -1;
    }
    dicZoek = '';
    return uit;
  });

  console.log('\n-- 1. de wachtzin telt --');
  console.log('   "' + r.zin + '"');
  ok(r.stand.heeft === 3 && r.stand.nodig === 5,
    'de app weet hoeveel metingen je hebt (' + r.stand.heeft + ' van ' + r.stand.nodig + ')');
  ok(/3 dagmetingen/.test(r.zin), 'en zegt dat ook, in plaats van alleen dat er meer nodig zijn');
  ok(/2 dagen/.test(r.zin), 'met erbij waarover ze verspreid staan, want dat is de tweede drempel');
  ok(/(\d+) dag(en)?\.$/.test(r.zin.trim()), 'en over hoeveel dagen je er bent als je blijft komen ("' + r.zin.trim().slice(-40) + '")');
  ok(!/maandag/.test(r.zin),
    'CONTROLE: en er staat geen maandag meer in, want je wacht op jezelf en niet op de kalender');

  console.log('\n-- 2. op beide schermen dezelfde zin --');
  ok(r.opVoortgang, 'de zin staat op Voortgang');
  console.log('   "' + r.fragment.slice(0, 130) + '"');
  ok(r.hoeVaak >= 1, 'en op elke plek waar de voorspelling zwijgt (' + r.hoeVaak + 'x)');

  console.log('\n-- 3. het controlegeval: bij genoeg dagpunten is hij weg --');
  ok(r.metGenoeg.stand.genoeg, 'veertien dagpunten over veertien dagen is genoeg');
  ok(r.metGenoeg.zin === '', 'dan levert de wachtzin niets meer op');
  ok(typeof r.metGenoeg.tempo === 'number' && Math.abs(r.metGenoeg.tempo - 28) < 0.01,
    'en er staat een tempo dat klopt: +4 per dag is 28 per week (' + r.metGenoeg.tempo + ')');
  ok(r.metGenoegOpScherm, 'en het scherm noemt geen dagmetingen meer');

  console.log('\n-- 4. de woorden achter de zoekbalk zijn er nog --');
  console.log('   ' + r.uitLessen + ' woordgroepen uit je lessen, ' + r.freqN + ' in de zoeklijst erachter');
  console.log('   kop: "' + r.dicKop + '"');
  ok(r.freqN > 4000, 'de zoeklijst is er nog, en is groter dan vierduizend (' + r.freqN + ')');
  ok(r.buitenN > 500, 'er zijn ook echt woorden buiten je lessen (' + r.buitenN + ')');
  ok(r.gevonden === true, 'en zo eentje wordt gevonden als je hem opzoekt (' + r.proef + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
