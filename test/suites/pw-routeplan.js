// pw-routeplan.js (6 sep, v23.248) - vraagt de app wat er open staat, en loopt hij de route?
//
// WAAROM DEZE SUITE ER IS
//
// Drie metingen in Stefans eigen logboek van 6 september, en alle drie wezen dezelfde kant op: de
// app toetste de tijd die nog dicht was en liep de route van de tijd die open stond niet.
//
//   indefimperf        57 beurten, 64% goed, doos 0, terwijl S.brok leeg was en de vormladder op
//                      "het hele presente" stond. Maanden de keuze tussen twee verleden tijden
//                      oefenen waarvan je de vormen nog niet hebt gehad.
//   gcFocus()          zei ["genero", "concordancia"], de dagles gaf comparar. De limiet van
//                      v23.234 stuurde het scherm en niet het oefenen.
//   presente-route     acht stappen, nul gedaan, terwijl het vormenblok elke tweede dag draait.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. EEN ONDERWERP WAARVAN DE ROUTE OP SLOT STAAT, WORDT NIET GEVRAAGD. Gebouwd: indefimperf met
//      beurten erin en de ladder op presente. En het controlegeval erbij: zet de ladder op de
//      verleden tijd en het onderwerp hoort terug te komen. Zonder dat tweede geval zou deze proef
//      ook groen staan als er nooit meer iets open ging.
//   2. "TWEE KEER MIS" GAAT OVER DEZE WEEK. Gebouwd: twintig fouten in de levenslange teller en een
//      leeg ledger geeft GEEN microles; twee missers van vandaag in het ledger wel.
//   3. DE DAGLES KIEST BINNEN DE FOCUS. Gebouwd: twee onderwerpen in de focus en niets verse
//      missers; het onderwerp van de dag hoort er een van te zijn.
//   4. HET VORMENBLOK VOLGT DE ROUTE. Gebouwd: geen openstaande fouten, niets begonnen, geen
//      verwarring. Dan hoort de eerste lesstap van de route eruit te komen en niet de eerste rij
//      uit de lijst. Die twee verschillen echt: de route slaat het regelmatige presente met opzet
//      over, en dat is precies de rij die vooraan staat.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwRp' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1. een onderwerp waarvan de route op slot staat ----
  console.log('\n-- 1. de route bepaalt of het onderwerp gevraagd wordt --');
  const slot = await page.evaluate(() => {
    // gebouwd: het onderwerp heeft een route én een geschiedenis, dus zonder de regel van v23.248
    // zou gcOpenSet hem openhouden ("alles wat je ooit hebt aangeraakt").
    const pad = GRAM_PADEN.filter(function (p) {
      return GC_ORDE.indexOf(p.id) !== -1 && (p.stappen || []).some(function (s) { return s.soort === 'les' && s.arg; });
    })[0];
    if (!pad) return { geenPad: true };
    S.gram = {}; S.gram[pad.id] = { box: 0, goed: 37, fout: 20, laatst: today() };
    S.gramFocus = null;
    S.conjLadder = CONJ_LADDER_NU;
    S.conjOpen = conjFaseIdx('presente');
    try { persist(); } catch (e) {}
    const dicht = { rijen: lesRijIds(), padOpen: gramPadOpen(pad), open: !!gcOpenSet()[pad.id],
                    concept: gcConceptOpen(pad.id),
                    wachtrij: gramWachtrij().filter(function (x) { return x.c.id === pad.id; }).length };
    // het controlegeval: de ladder gaat naar de verleden tijd, en dan hoort hij terug te komen
    S.conjOpen = conjFaseIdx('imperf');
    try { persist(); } catch (e) {}
    const los = { rijen: lesRijIds(), padOpen: gramPadOpen(pad), open: !!gcOpenSet()[pad.id],
                  concept: gcConceptOpen(pad.id) };
    S.conjOpen = conjFaseIdx('presente');
    try { persist(); } catch (e) {}
    return { id: pad.id, dicht: dicht, los: los };
  });
  ok(!slot.geenPad, 'CONTROLE: er is een onderwerp met een route die lesstappen heeft (' + (slot.id || 'geen') + ')');
  ok(slot.dicht && slot.dicht.padOpen === false,
    'CONTROLE: met de ladder op presente staat die route echt op slot');
  ok(slot.dicht && slot.dicht.open === false,
    'het onderwerp staat dan niet in gcOpenSet, ondanks 57 beurten in zijn geschiedenis');
  ok(slot.dicht && slot.dicht.concept === false, 'en gcConceptOpen zegt hetzelfde');
  ok(slot.dicht && slot.dicht.wachtrij === 0, 'en het staat ook niet in de wachtrij van vandaag');
  ok(slot.los && slot.los.padOpen === true,
    'CONTROLE: met de ladder op de verleden tijd gaat de route open');
  ok(slot.los && slot.los.open === true && slot.los.concept === true,
    'en dan komt het onderwerp terug, met zijn doosje en al');

  // ---- 2. "twee keer mis" gaat over deze week ----
  console.log('\n-- 2. twee keer mis gaat over het verse venster, niet over ooit --');
  const vers = await page.evaluate(() => {
    const cid = GC_ORDE[0];
    S.gram = {}; S.gram[cid] = { box: 0, goed: 3, fout: 20, laatst: today() };
    S.gramLog = {};
    try { persist(); } catch (e) {}
    const zonderLog = { missers: gcVersMissers(cid), gramId: lesFlowGramId() };
    // gebouwd: twee missers van vandaag in het ledger, precies wat de regel bedoelt te vangen
    S.gramLog = {}; S.gramLog[today()] = {}; S.gramLog[today()][cid] = { n: 3, goed: 1 };
    try { persist(); } catch (e) {}
    const metLog = { missers: gcVersMissers(cid), gramId: lesFlowGramId() };
    return { cid: cid, zonderLog: zonderLog, metLog: metLog };
  });
  ok(vers.zonderLog.missers === 0,
    'twintig fouten in de levenslange teller en een leeg ledger geeft 0 verse missers (' + vers.zonderLog.missers + ')');
  ok(vers.metLog.missers === 2,
    'CONTROLE: drie beurten waarvan één goed geeft er 2 (' + vers.metLog.missers + ')');
  ok(vers.metLog.gramId === 'concept-' + vers.cid,
    'en dán komt de hele microles van dat onderwerp (' + vers.metLog.gramId + ')');

  // ---- 3. de dagles kiest binnen de focus ----
  console.log('\n-- 3. wat het scherm belooft is wat de les geeft --');
  const focus = await page.evaluate(() => {
    // gebouwd: een geschiedenis op vier onderwerpen, geen ledger (dus geen verse missers), zodat
    // alleen de focus nog kan beslissen.
    S.gram = {}; S.gramLog = {}; S.gramFocus = null;
    GC_ORDE.slice(0, 4).forEach(function (id, i) {
      S.gram[id] = { box: i === 3 ? 4 : 0, goed: 5, fout: 2, laatst: '2026-01-01', due: '2026-01-02' };
    });
    try { persist(); } catch (e) {}
    const f = gcFocus();
    const lijst = gcVandaagLijst().map(function (c) { return c.id; });
    const id = lesFlowGramId();
    return { focus: f, lijst: lijst, gramId: id, kaal: String(id || '').replace(/^concept-/, '').split('#')[0],
             kandidaat: gcFocusKandidaat() };
  });
  console.log('   focus: ' + focus.focus.join(', ') + '  ·  dagles: ' + focus.gramId);
  ok(focus.focus.length > 0 && focus.focus.length <= 2,
    'CONTROLE: er staat een focus van hoogstens twee onderwerpen (' + focus.focus.join(',') + ')');
  ok(focus.lijst.length > 0, 'CONTROLE: en de daglijst is niet leeg (' + focus.lijst.join(',') + ')');
  ok(focus.lijst.indexOf(focus.kaal) !== -1,
    'het onderwerp van de dagles staat in diezelfde lijst (' + focus.kaal + ')');

  // ---- 4. het vormenblok volgt de route ----
  console.log('\n-- 4. het vormenblok loopt de route af --');
  const route = await page.evaluate(() => {
    // gebouwd: schoon veld. Geen conj-fouten, niets begonnen, geen verwarring, zodat de drie
    // reparatieregels vóór deze allemaal zwijgen en de route aan de beurt is.
    S.errors = {}; S.brok = {}; S.conjLadder = CONJ_LADDER_NU; S.conjOpen = conjFaseIdx('presente');
    try { persist(); } catch (e) {}
    const open = lesRijIds().filter(function (t) { return !lesKlaar(t); });
    const p = gramPadNu();
    const stap = p ? (p.stappen || []).filter(function (s) { return s.soort === 'les' && s.arg; })[0] : null;
    return { open: open, eerste: open[0], route: vormRijUitRoute(open),
             gekozen: vormRijVandaag(), pad: p ? p.id : null, eersteLesstap: stap ? stap.arg : null,
             fouten: vormFoutenPerTijd(), verwar: tijdvormTopVerwar() };
  });
  console.log('   route: ' + route.pad + '  ·  eerste rij in de lijst: ' + route.eerste +
              '  ·  eerste lesstap van de route: ' + route.eersteLesstap);
  ok(Object.keys(route.fouten).length === 0 && !route.verwar,
    'CONTROLE: er valt niets te repareren, dus de route is aan de beurt');
  ok(route.eerste !== route.eersteLesstap,
    'CONTROLE: de eerste rij in de lijst is NIET de eerste stap van de route (' +
      route.eerste + ' tegen ' + route.eersteLesstap + '), anders bewijst deze proef niets');
  ok(route.route === route.eersteLesstap,
    'vormRijUitRoute geeft de eerste onafgemaakte lesstap van de route (' + route.route + ')');
  ok(route.gekozen === route.eersteLesstap,
    'en dat is ook wat het vormenblok vandaag kiest (' + route.gekozen + ')');

  // ---- 5. en repareren blijft vóór vooruitkomen ----
  console.log('\n-- 5. maar een openstaande fout gaat nog steeds voor --');
  const rep = await page.evaluate(() => {
    // gebouwd: een fout op een tijd die een andere rij aanwijst dan de route zou kiezen
    const open = lesRijIds().filter(function (t) { return !lesKlaar(t); });
    const viaRoute = vormRijUitRoute(open);
    const ander = open.filter(function (t) {
      const r = lesRij(t);
      return t !== viaRoute && r && r.t;
    })[0];
    if (!ander) return { geenAnder: true, viaRoute: viaRoute };
    const r = lesRij(ander);
    /* de vorm van een echte foutregel, zoals conjErrKey hem schrijft: type "conj" en een id
       "<infinitief>-<persoon>-<tijd>". Zelf verzinnen zou hier een sleutel opleveren die
       vormFoutenPerTijd niet leest, en dan bewijst deze proef het tegenovergestelde van wat hij wil. */
    S.errors = {};
    for (let i = 0; i < 4; i++) {
      S.errors['proef' + i] = { type: 'conj', id: 'hablar-' + i + '-' + r.t, count: 2 };
    }
    try { persist(); } catch (e) {}
    return { viaRoute: viaRoute, ander: ander, tijd: r.t,
             fouten: vormFoutenPerTijd(), gekozen: vormRijVandaag() };
  });
  if (rep.geenAnder) {
    ok(false, 'CONTROLE: geen tweede rij met een eigen tijd om de reparatie op te zetten');
  } else {
    console.log('   fout gezet op ' + rep.tijd + ' (rij ' + rep.ander + '), route wees ' + rep.viaRoute + ' aan');
    ok(Object.keys(rep.fouten).length > 0, 'CONTROLE: die fout wordt ook echt geteld');
    ok(rep.gekozen !== rep.viaRoute,
      'de reparatie wint van de route (' + rep.gekozen + ')');
  }

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
