// pw-opfrismarkering.js (24 aug, v23.189 en v23.190) — de opfrisser staat stil en laat zien wat JIJ deed
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 24 aug: "Bij opfrissen laat ie niet het goede of foute antwoord zien maar gaat ie
// automatisch direct door naar volgende." Twee dingen bleken waar te zijn, en het tweede is de
// oorzaak van het eerste.
//
//   v23.190: gcOpfrisOnderwerp() bouwde bij ELKE aanroep een nieuwe vraag, langs de cache van
//   gcOnderwerp() heen. gwKies() en renderCheat() halen het onderwerp allebei opnieuw op, dus één
//   klik raakte drie trekkingen: je klikte op de opties van A, werd afgerekend tegen B en zag de
//   markering van C. Gemeten: acht van de acht opfrissers wisselden binnen vijf aanroepen, acht van
//   de acht microlessen niet. Boven die cache staat al sinds v20.5 de waarschuwing waar dit in liep.
//
//   v23.189: en de opfrisser markeerde alleen het juiste antwoord, nooit dat van jou. Het toetsje
//   doet dat al jaren met twee kleuren.
//
// WAT DEZE SUITE BEWAAKT
//
//   0. DE VRAAG STAAT STIL binnen een sessie, en is toch VERS bij elke start. Die twee samen, want
//      elk van beide is los triviaal te halen en dan is de andere stuk.
//   1. FOUT ANTWOORD: het juiste staat groen én jouw keuze staat rood.
//   2. GOED ANTWOORD: precies één merkteken, en dat is groen. Het controlegeval bij 1: altijd
//      allebei de klassen zetten is triviaal groen, en dan staat er bij een goed antwoord een rode
//      knop op je scherm.
//   3. VOOR HET ANTWOORDEN staat er niets gemarkeerd: markeren mag het antwoord niet weggeven.
//   4. EN HET TOETSJE DOET HET NOG STEEDS. Dat is het scherm waar dit gedrag vandaan komt.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwOm' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 0. stil binnen een sessie, vers bij elke start ----
  console.log('\n-- 0. de vraag staat stil, en is toch vers bij een nieuwe start --');
  const stil = await page.evaluate(() => {
    const uit = [];
    gcGeordend().slice(0, 8).forEach(function (c) {
      const id = gcOpfrisId(c.id);
      const merk = function (q) { return gwVraagTekst(q) + '|' + gwOpties(q).join('/') + '|' + q.g; };
      lesFlow = null; gwSess = null;
      try { gwStart(id); } catch (e) { return; }
      if (!gwSess) return;
      gwSess.fase = 'toets';
      const binnen = [];
      for (let k = 0; k < 6; k++) binnen.push(merk(gwVragen()[0]));
      // en nu opnieuw beginnen: dat hoort wél een nieuwe trekking te geven
      const overStarts = [binnen[0]];
      for (let k = 0; k < 12; k++) {
        gwSess = null;
        gwStart(id);
        gwSess.fase = 'toets';
        overStarts.push(merk(gwVragen()[0]));
      }
      uit.push({ id: id,
        binnenUniek: new Set(binnen).size,
        overStartsUniek: new Set(overStarts).size,
        opties: gwOpties(gwVragen()[0]).length });
    });
    return uit;
  });
  stil.forEach(function (s) {
    ok(s.binnenUniek === 1,
      s.id + ': zes keer opvragen geeft zes keer dezelfde vraag (' + s.binnenUniek + ' verschillend)');
  });
  const veranderlijk = stil.filter(function (s) { return s.overStartsUniek > 1; });
  console.log('   verse trekking bij een nieuwe start: ' +
    stil.map(function (s) { return s.id.replace('opfris-', '') + ' ' + s.overStartsUniek; }).join(', '));
  ok(veranderlijk.length >= Math.ceil(stil.length * 0.75),
    'CONTROLE: en dertien starts geven wél verschillende vragen (' + veranderlijk.length + ' van de ' +
    stil.length + ' onderwerpen) — anders is de cache een groef geworden');

  // ---- 1, 2 en 3: elke opfrisser, goed en fout ----
  const uit = await page.evaluate(() => {
    const rapport = [];
    const lees = function () {
      return Array.prototype.slice.call(document.querySelectorAll('#cheat .gw-optie')).map(function (b) {
        return { juist: b.classList.contains('juist'), jouw: b.classList.contains('jouw') };
      });
    };
    gcGeordend().slice(0, 10).forEach(function (c) {
      const id = gcOpfrisId(c.id);
      ['goed', 'fout'].forEach(function (hoe) {
        lesFlow = null; gwSess = null;
        try { gwStart(id); } catch (e) { return; }
        if (!gwSess) return;
        if (gwSess.fase !== 'toets') gwSess.fase = 'toets';
        show('spiekbrief', true); renderCheat();
        const q = gwVragen()[gwSess.vraag];
        const n = gwOpties(q).length;
        const voor = lees();
        const kies = hoe === 'goed' ? q.g : (q.g === 0 ? (n > 1 ? 1 : 0) : 0);
        if (hoe === 'fout' && kies === q.g) return;   // één optie: geen fout mogelijk
        gwKies(kies);
        const na = lees();
        rapport.push({ id: id, hoe: hoe, n: n, juistIdx: q.g, kies: kies,
          voorGemarkeerd: voor.filter(function (x) { return x.juist || x.jouw; }).length,
          juistGemerkt: na[q.g] && na[q.g].juist,
          jouwGemerkt: na[kies] && na[kies].jouw,
          totaal: na.filter(function (x) { return x.juist || x.jouw; }).length });
      });
    });
    return rapport;
  });

  console.log('\n-- 1 en 2. wat er gemarkeerd staat na het antwoorden --');
  let foutN = 0, goedN = 0;
  uit.forEach(function (r) {
    if (r.hoe === 'fout') {
      foutN++;
      ok(r.juistGemerkt && r.jouwGemerkt && r.totaal === 2,
        r.id + ' (fout): juist groen én jouw keuze rood (' + r.totaal + ' gemarkeerd)');
    } else {
      goedN++;
      ok(r.juistGemerkt && r.totaal === 1,
        'CONTROLE: ' + r.id + ' (goed): precies één merkteken, en dat is het groene (' + r.totaal + ')');
    }
  });
  console.log('   ' + foutN + ' foute en ' + goedN + ' goede rondes gelopen');
  ok(foutN >= 5 && goedN >= 5, 'genoeg rondes om iets te betekenen');

  console.log('\n-- 3. en vooraf staat er niets --');
  ok(uit.every(function (r) { return r.voorGemarkeerd === 0; }),
    'CONTROLE: vóór het antwoorden is geen enkele optie gemarkeerd (het antwoord staat er dus niet al)');

  // ---- 4. en het toetsje, waar dit gedrag vandaan komt ----
  console.log('\n-- 4. het toetsje doet het nog steeds --');
  const qz = await page.evaluate(() => {
    show('toetsjes', true);
    const eerste = QUIZZES[0];
    startQuiz(eerste.id);
    const v = qState.volgorde[qState.i].v;
    const knoppen = document.querySelectorAll('#qCard .opt');
    const mis = v.c === 0 ? 1 : 0;
    answerQuestion(mis, knoppen[mis]);
    const na = document.querySelectorAll('#qCard .opt');
    return { juist: na[v.c].classList.contains('correct'), jouw: na[mis].classList.contains('wrong') };
  });
  ok(qz.juist && qz.jouw, 'CONTROLE: het toetsje markeert nog steeds allebei (juist=' + qz.juist + ', jouw=' + qz.jouw + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
