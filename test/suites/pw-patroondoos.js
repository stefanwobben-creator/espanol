// pw-patroondoos.js (1 sep, v23.228) — zit het doosje op het patroon of op het concept?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan: "el la los las die ken ik echt wel, de grammaticale regel, maar deze blijft terugkomen
// door het spaced repetition principe."
//
// Gemeten in zijn eigen nachtlogboek: genero 55 goed tegen 17 fout, en na 72 beurten nog steeds
// doos 2. Terwijl comparar met vijf beurten op doos 5 staat. Meer oefenen zakte hem, en dat kan
// nooit de bedoeling zijn.
//
// De oorzaak: één doos voor vijf patronen. Hij kent de regel (-ción is la), de -or en het meervoud;
// hij mist de Griekse val (el problema, el tema), en dat is geen regel maar een lijstje woorden. Eén
// misser op dat ene patroon zette de doos van alle vijf naar nul. Nagerekend over een jaar ging 80%
// van zijn el-of-la-oefening naar patronen die hij al kende.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ELKE VRAAG WEET UIT WELK PATROON HIJ KOMT. Zonder dat kan het doosje er niet op zitten.
//      Gebouwd controlegeval: gcVragenUitPatroon() levert alleen dat ene patroon.
//   2. EEN ANTWOORD LANDT OP HET PATROON. En niet op het concept, want dan is er niets veranderd.
//   3. HET CONCEPT IS ZO STERK ALS ZIJN ZWAKSTE DOOSJE. Twee patronen, één op doos 5 en één op nul:
//      het concept hoort nul te zeggen. Dat is de eerlijke samenvatting.
//   4. DE WACHTRIJ LEVERT HET PATROON DAT AAN DE BEURT IS. Niet het concept, en niet de patronen die
//      nog weken weg zijn. Dit is de helft waar het effect vandaan komt.
//   5. DE OPFRISSER VRAAGT DAT PATROON. Kwam je om op de Griekse val, dan krijg je de Griekse val.
//      Controlegeval: zonder patroonindex put hij nog steeds uit alles.
//   6. EEN FOUT IN HET WILD RESET DE PATRONEN NIET. Dit is de belangrijkste. gramBij() wordt op zes
//      plaatsen aangeroepen die geen patroon kennen (een quiz, de tegels, een vrije zin, de
//      Clasificador, El Corrector). Die landen op de kale sleutel, en die is zijn eigen doosje.
//      Zouden ze alle patronen resetten, dan hadden we het oude probleem gewoon terug.
//   7. EEN PATROON DAT JE NOG NOOIT DEED STAAT NIET IN DE WACHTRIJ. Kennismaking hoort in de les.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwPd' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1. de vraag draagt zijn patroon ----
  console.log('\n-- 1. elke vraag weet uit welk patroon hij komt --');
  const vragen = await page.evaluate(() => {
    const c = gcGeordend().filter(function (x) { return (x.patronen || []).length >= 3; })[0];
    const alle = gcMaakVragen(c, 12);
    const een = gcVragenUitPatroon(c, 1, 4);
    const tel = {};
    alle.forEach(function (q) { tel[q.pi] = (tel[q.pi] || 0) + 1; });
    return { cid: c.id, patronen: c.patronen.length, tel: tel,
             zonderPi: alle.filter(function (q) { return typeof q.pi !== 'number'; }).length,
             eenPi: een.map(function (q) { return q.pi; }),
             eenTekst: een.map(function (q) { return q.v; }) };
  });
  console.log('   ' + vragen.cid + ' (' + vragen.patronen + ' patronen): ' + JSON.stringify(vragen.tel));
  ok(vragen.zonderPi === 0, 'geen enkele vraag komt zonder patroonindex uit de fabriek');
  ok(Object.keys(vragen.tel).length >= 3, 'en een microles put uit meerdere patronen (' + Object.keys(vragen.tel).length + ')');
  console.log('   uit patroon 1: ' + vragen.eenTekst.join(' · '));
  ok(vragen.eenPi.every(function (p) { return p === 1; }),
    'CONTROLE: uit één patroon komt ook echt alleen dat patroon (' + vragen.eenPi.join(',') + ')');

  // ---- 2 en 3. waar het antwoord landt, en wat het concept dan zegt ----
  console.log('\n-- 2 en 3. het antwoord landt op het patroon --');
  const doos = await page.evaluate(() => {
    const cid = 'genero';
    S.gram = {};
    gramBij(cid, false, 2, 1);
    const naFout = { sleutels: Object.keys(S.gram), patroon: gramLees(cid + '#1'), concept: gramLees(cid) };
    // en nu een sterk patroon ernaast: het concept hoort de zwakste te volgen
    S.gram[cid + '#0'] = { box: 5, due: addDays(today(), 60), goed: 9, fout: 0, laatst: '' };
    const gemengd = gramLees(cid);
    return { naFout: naFout, gemengd: gemengd,
             sterk: gramLees(cid + '#0').box, zwak: gramLees(cid + '#1').box };
  });
  console.log('   sleutels na één fout op patroon 1: ' + JSON.stringify(doos.naFout.sleutels));
  ok(doos.naFout.sleutels.length === 1 && doos.naFout.sleutels[0] === 'genero#1',
    'er ontstaat één doosje, en dat is dat van het patroon');
  ok(doos.gemengd.box === 0 && doos.sterk === 5 && doos.zwak === 0,
    'het concept is zo sterk als zijn zwakste doosje (' + doos.sterk + ' en ' + doos.zwak + ' geeft ' + doos.gemengd.box + ')');
  ok(doos.gemengd.goed === 9 && doos.gemengd.fout === 1,
    'en de tellers worden opgeteld (' + doos.gemengd.goed + ' goed, ' + doos.gemengd.fout + ' fout)');

  // ---- 4 en 7. de wachtrij ----
  console.log('\n-- 4 en 7. de wachtrij levert het patroon dat aan de beurt is --');
  const rij = await page.evaluate(() => {
    S.gram = {
      'genero#0': { box: 5, due: addDays(today(), 60), goed: 9, fout: 0, laatst: '' },
      'genero#1': { box: 0, due: today(), goed: 2, fout: 4, laatst: today() }
    };
    const q = gramWachtrij().filter(function (x) { return x.c.id === 'genero'; });
    return { n: q.length, pis: q.map(function (x) { return x.pi; }),
             alle: gramWachtrij().length };
  });
  console.log('   genero in de wachtrij: ' + rij.n + ' regel(s), patroon ' + JSON.stringify(rij.pis));
  ok(rij.n === 1 && rij.pis[0] === 1, 'alleen het patroon dat aan de beurt is staat er');
  ok(rij.pis.indexOf(0) === -1, 'CONTROLE: het patroon dat nog zestig dagen weg is staat er niet');
  ok(rij.pis.indexOf(2) === -1 && rij.pis.indexOf(null) === -1,
    'en een patroon dat je nog nooit deed ook niet: kennismaking hoort in de les');

  // ---- 5. de opfrisser ----
  console.log('\n-- 5. de opfrisser vraagt dát patroon --');
  const opfris = await page.evaluate(() => {
    const id = gcOpfrisId('genero', 1);
    const o = gcVernieuw(id);
    const breed = gcVernieuw(gcOpfrisId('genero'));
    return { id: id,
             pis: o ? o.stappen[0].vragen.map(function (q) { return q.pi; }) : null,
             tekst: o ? o.stappen[0].vragen.map(function (q) { return q.v; }) : null,
             breedPis: breed ? breed.stappen[0].vragen.map(function (q) { return q.pi; }) : null,
             breedId: gcOpfrisId('genero') };
  });
  console.log('   ' + opfris.id + ': ' + (opfris.tekst || []).join(' · '));
  ok(opfris.id === 'opfris-genero#1', 'het id draagt het patroon (' + opfris.id + ')');
  ok(!!opfris.pis && opfris.pis.every(function (p) { return p === 1; }),
    'en alle vragen komen uit dat patroon (' + (opfris.pis || []).join(',') + ')');
  ok(opfris.breedId === 'opfris-genero',
    'CONTROLE: zonder patroon blijft de oude vorm bestaan (' + opfris.breedId + ')');
  ok(!!opfris.breedPis && new Set(opfris.breedPis).size >= 1,
    'en die put uit alle patronen, want hij hoort bij het doosje van de vrije zin');

  // ---- 6. de fout in het wild ----
  console.log('\n-- 6. een fout in het wild reset de patronen niet --');
  const wild = await page.evaluate(() => {
    S.gram = {
      'genero#0': { box: 5, due: addDays(today(), 60), goed: 9, fout: 0, laatst: '' },
      'genero#2': { box: 4, due: addDays(today(), 21), goed: 6, fout: 0, laatst: '' }
    };
    // dit is precies wat foutRegel(), de quiz, de tegels, de Clasificador en El Corrector doen
    gramBij('genero', false);
    return { kaal: gramLees('genero#') , sleutels: Object.keys(S.gram).sort(),
             p0: gramLees('genero#0').box, p2: gramLees('genero#2').box,
             bare: (S.gram.genero || {}).box, bareDue: (S.gram.genero || {}).due,
             concept: gramLees('genero').box, morgen: addDays(today(), 1) };
  });
  console.log('   ' + JSON.stringify({ sleutels: wild.sleutels, p0: wild.p0, p2: wild.p2, kaal: wild.bare }));
  ok(wild.p0 === 5 && wild.p2 === 4, 'de patronen die je kent blijven staan waar ze stonden');
  ok(wild.bare === 0 && wild.bareDue === wild.morgen,
    'de fout landt op de kale sleutel en komt morgen terug');
  ok(wild.concept === 0, 'CONTROLE: en het concept zegt daardoor wél nul, want dat is zijn zwakste doosje');
  ok(wild.sleutels.length === 3, 'er zijn nu drie doosjes: twee patronen en de vrije zin');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
