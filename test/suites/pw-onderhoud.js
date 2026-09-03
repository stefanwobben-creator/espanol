// pw-onderhoud.js (3 sep, v23.235) — komt wat je al kunt ooit nog terug?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, op de mededeling dat de focus van v23.234 de derde plek voor iets nieuws kostte: "maar hoe
// kan ik dan progressie maken want met grammatica doen we ook spaced repetition toch?"
//
// Nagemeten. De focus stuurt alleen gcVandaagLijst(); de herhaling loopt langs gramWachtrij() en die
// ziet ALLE open concepten. Dat deel was in orde.
//
// Maar lesFlowGramLijst() pakt uit die wachtrij precies één regel: rij[0], en de wachtrij is
// oplopend op DOOS gesorteerd. Zolang er íets op doos 0 staat komt doos 4 dus nooit aan de beurt.
//
// In Stefans logboek staan zestien onderwerpen op doos 0, 1 of 2, en zijn negen op doos 5 vervallen
// tussen 1 en 26 oktober. Nu staat er nog niets over tijd; vanaf 1 oktober zou de herhaling van
// alles wat hij al kan stilletjes stoppen. Dit is het spiegelbeeld van het lege midden: onderaan
// komt niets omhoog en bovenaan valt straks alles om, met dezelfde oorzaak.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE FOCUS RAAKT DE WACHTRIJ NIET. Een onderwerp op doos 4 dat vandaag toe is staat erin, ook
//      als het buiten de focus valt. Gebouwd, met de controle dat het echt buiten de focus ligt.
//   2. EN HET KOMT IN JE DAGLES. Dit is de proef die vóór v23.235 rood stond: zestien onderwerpen op
//      doos 0 ervoor, en toch komt de vervallen doos 4 aan de beurt.
//   3. HET ONDERHOUD DRINGT NIET VOOR. Het leren staat vooraan, want dat is het werk van de dag.
//   4. NUL IS GEEN BERICHT. Is er niets vervallen op doos 3 of hoger, dan komt er geen extra beurt
//      bij en blijft de les precies zoals hij was. Zonder dit controlegeval zou "altijd een beurt
//      erbij" proef 2 ook halen.
//   5. HET ONDERHOUD SORTEERT OP WACHTTIJD EN NIET OP DOOS. Bij onderhoud telt wie het langst
//      wacht; op doos sorteren bouwt de wachtrij na en dan wint doos 3 altijd van doos 5.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwOh' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1 t/m 3. Stefans toestand van 1 oktober, nagebouwd ----
  console.log('\n-- 1 t/m 3. zestien op doos 0, en toch komt de vervallen doos 4 aan de beurt --');
  const stand = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null;
    const alle = gcGeordend().map(function (c) { return c.id; });
    // zestien onderwerpen op doos 0: precies de gemeten toestand
    alle.slice(0, 16).forEach(function (id) {
      S.gram[id] = { box: 0, due: today(), goed: 5, fout: 5, laatst: addDays(today(), -10) };
    });
    // en eentje dat je al kunt, dat vandaag toe is. Buiten de focus, want die zit vol.
    const oud = alle[19] || alle[alle.length - 1];
    S.gram[oud] = { box: 4, due: today(), goed: 20, fout: 1, laatst: addDays(today(), -40) };

    const focus = gcFocus();
    const rij = gramWachtrij().map(function (x) { return x.c.id; });
    const oh = gramOnderhoudTop();
    const lijst = lesFlowGramLijst();
    const kaal = function (x) { return String(x || '').replace(/^(opfris|concept)-/, '').split('#')[0]; };
    return { oud: oud, focus: focus,
             inFocus: focus.indexOf(oud) !== -1,
             inWachtrij: rij.indexOf(oud) !== -1,
             wachtrijPlek: rij.indexOf(oud),
             rij0: rij[0],
             onderhoud: oh ? oh.c.id : null,
             lijst: lijst, lijstKaal: lijst.map(kaal),
             opDeBeurt: lijst.map(kaal).indexOf(oud) };
  });
  console.log('   focus: ' + stand.focus.join(' + ') + '  ·  onderhoud: ' + stand.onderhoud);
  console.log('   dagles: ' + stand.lijst.join(' + '));
  ok(!stand.inFocus,
    'CONTROLE: ' + stand.oud + ' valt buiten de focus, dus er valt iets te bewijzen');
  ok(stand.inWachtrij, 'hij staat wel in de wachtrij, want die trekt zich niets van de focus aan');
  ok(stand.wachtrijPlek > 0 && stand.rij0 !== stand.oud,
    'CONTROLE: en niet vooraan, want de wachtrij zet het zwakste eerst (plek ' + (stand.wachtrijPlek + 1) + ')');
  ok(stand.onderhoud === stand.oud,
    'de onderhoudsbeurt wijst hem aan (' + stand.onderhoud + ')');
  ok(stand.opDeBeurt !== -1,
    'en hij staat in je dagles, ondanks zestien zwakkere ervoor');
  ok(stand.opDeBeurt === stand.lijstKaal.length - 1,
    'achteraan: het leren is het werk van de dag, het onderhoud is een tik (' + stand.lijstKaal.join(' > ') + ')');

  // ---- 4. nul is geen bericht ----
  console.log('\n-- 4. niets te onderhouden, niets erbij --');
  const leeg = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null;
    const alle = gcGeordend().map(function (c) { return c.id; });
    alle.slice(0, 16).forEach(function (id) {
      S.gram[id] = { box: 0, due: today(), goed: 5, fout: 5, laatst: addDays(today(), -10) };
    });
    // alles wat sterk is, is pas over een maand toe: precies Stefans stand van vandaag
    const sterk = alle[19] || alle[alle.length - 1];
    S.gram[sterk] = { box: 5, due: addDays(today(), 31), goed: 20, fout: 1, laatst: '' };
    return { onderhoud: gramOnderhoudTop(), lijst: lesFlowGramLijst() };
  });
  console.log('   ' + JSON.stringify(leeg));
  ok(leeg.onderhoud === null, 'niets vervallen op doos 3 of hoger, dus geen onderhoudsbeurt');
  ok(leeg.lijst.length === stand.lijst.length - 1,
    'en de dagles is precies één beurt korter dan met onderhoud (' + leeg.lijst.length + ' tegen ' + stand.lijst.length + ')');

  // ---- 5. wachttijd, niet doos ----
  console.log('\n-- 5. bij onderhoud telt wie het langst wacht --');
  const orde = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null;
    const alle = gcGeordend().map(function (c) { return c.id; });
    const a = alle[18], b = alle[19];
    // doos 5, drie weken over tijd  tegen  doos 3, gisteren toe
    S.gram[a] = { box: 5, due: addDays(today(), -21), goed: 30, fout: 0, laatst: '' };
    S.gram[b] = { box: 3, due: addDays(today(), -1), goed: 9, fout: 1, laatst: '' };
    const oh = gramOnderhoudTop();
    return { langstWachtend: a, kortst: b, gekozen: oh ? oh.c.id : null,
             doosA: 5, doosB: 3 };
  });
  console.log('   doos 5 (21 dagen over tijd) tegen doos 3 (1 dag): gekozen ' + orde.gekozen);
  ok(orde.gekozen === orde.langstWachtend,
    'de langst wachtende wint, ook al staat hij in een hoger doosje');
  ok(orde.gekozen !== orde.kortst,
    'CONTROLE: op doos sorteren zou de ander hebben gekozen, en dan komt doos 5 nooit meer aan bod');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
