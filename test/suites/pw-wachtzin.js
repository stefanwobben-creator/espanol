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
//   1. DE WACHTZIN TELT. Niet alleen "er zijn er drie nodig" maar hoeveel je er hebt, en vanaf
//      wanneer de volgende kan komen.
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
    // precies de stand van Stefan op 21 augustus: twee weken in de nieuwe maat
    S.meting = {
      '2026-W33': { d: '2026-08-11', dekw: { A1: 180, A2: 90 }, dek: { A1: 150, A2: 70 } },
      '2026-W34': { d: '2026-08-18', dekw: { A1: 215, A2: 110 }, dek: { A1: 175, A2: 85 } }
    };
    S.doelNiv = 'A1'; S.doelDatum = '2026-12-01';
    uit.stand = tempoStand('A1');
    uit.maandag = komendeMaandag();
    uit.zin = tempoWachtZin('A1');
    /* De vroegst mogelijke dag is de eerstvolgende maandag, want een meting wordt geschreven zodra
       je de app voor het eerst in een nieuwe ISO-week opent. */
    uit.isMaandag = (function () {
      try { return new Date(uit.maandag + 'T00:00:00').getDay() === 1; } catch (e) { return false; }
    })();
    uit.inToekomst = uit.maandag > today();

    show('voortgang', true); renderStats();
    const scherm = document.getElementById('statsCard').textContent.replace(/\s+/g, ' ');
    uit.opVoortgang = scherm.indexOf(uit.zin.trim().slice(0, 40)) !== -1;
    uit.hoeVaak = (scherm.match(/van de 3/g) || []).length;
    uit.fragment = (scherm.match(/Wat je nu haalt[^]{0,150}/) || [''])[0];

    // 3. het controlegeval: met drie metingen is de wachtzin weg
    S.meting['2026-W35'] = { d: '2026-08-25', dekw: { A1: 250, A2: 130 }, dek: { A1: 200, A2: 95 } };
    uit.metDrie = {
      stand: tempoStand('A1'),
      zin: tempoWachtZin('A1'),
      tempo: (function () { try { const m = tempoMeting('A1'); return m ? m.gem : null; } catch (e) { return 'FOUT'; } })()
    };
    renderStats();
    uit.metDrieOpScherm = document.getElementById('statsCard').textContent.indexOf('van de 3') === -1;

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
  ok(r.stand.heeft === 2 && r.stand.nodig === 3, 'de app weet hoeveel metingen je hebt (' + r.stand.heeft + ' van ' + r.stand.nodig + ')');
  ok(/2 van de 3/.test(r.zin), 'en zegt dat ook, in plaats van alleen dat er drie nodig zijn');
  ok(r.isMaandag, 'de genoemde dag is een maandag, want dat is de vroegst mogelijke (' + r.maandag + ')');
  ok(r.inToekomst, 'en hij ligt in de toekomst');
  ok(/10 augustus/.test(r.zin), 'met erbij sinds wanneer een meting meetelt');

  console.log('\n-- 2. op beide schermen dezelfde zin --');
  ok(r.opVoortgang, 'de zin staat op Voortgang');
  console.log('   "' + r.fragment.slice(0, 130) + '"');
  ok(r.hoeVaak >= 1, 'en op elke plek waar de voorspelling zwijgt (' + r.hoeVaak + 'x)');

  console.log('\n-- 3. het controlegeval: bij drie metingen is hij weg --');
  ok(r.metDrie.stand.genoeg, 'met drie metingen is het genoeg');
  ok(r.metDrie.zin === '', 'dan levert de wachtzin niets meer op');
  ok(typeof r.metDrie.tempo === 'number', 'en er komt een tempo uit (' + r.metDrie.tempo + ' per week)');
  ok(r.metDrieOpScherm, 'het scherm zegt niet meer dat er iets ontbreekt');

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
