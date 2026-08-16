// pw-pad.js (16 aug, v23.116) — is het een route, of een lijstje?
//
// WAAROM DIT ER IS
//
// Stefan: "wanneer maak je er in plaats van losse elementen nu een geïntegreerde les van?"
//
// Er stonden vijf tegels die stuk voor stuk iets goeds doen en die samen niets zijn. Jij moest
// kiezen welke je deed, in welke volgorde, en wanneer je klaar was.
//
// WAT DEZE SUITE BEWAAKT
//
// De drie eigenschappen die van een lijstje een route maken:
//
//   1. DE VOLGORDE IS AFDWINGBAAR. "Alles door elkaar" mag niet je eerste oefening zijn. Dat is
//      regel R5 uit het ontwerpadvies en precies Stefans klacht ("ik word direct getoetst en alle
//      tijden door elkaar").
//   2. "AF" IS ÉÉN BEGRIP. Elk scherm scoorde op zijn eigen manier; zonder één definitie kan geen
//      pad bestaan. De eis hangt aan het SOORT stap, niet aan de stap.
//   3. DE KNOP GAAT NAAR DE JUISTE PLEK, en een stap die nog niet bestaat is geen deur naar niets.
//
// En de controle die dit alles tanden geeft: als je de brokken vult alsof je alles gehaald hebt,
// moet het pad kantelen. Een pad dat altijd hetzelfde zegt is geen pad.
const { chromium } = require('playwright');
// v23.120: de fixture staat in padvul.js, want vier suites hielden hun eigen lijstje bij en
// vier keer viel er een om toen er een stap bij kwam. Zie de kop van dat bestand.
const { VUL } = require('./padvul.js');

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwPad' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  await page.evaluate(() => {
    S.lang = 'nl'; S.speelAlles = true;
    S.conjOpen = CONJ_FASES.length - 1; S.conjFase = CONJ_FASES[CONJ_FASES.length - 1].id;
    try { persist(); } catch (e) {}
  });



  // ---- 1. de data ----
  const data = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    return {
      paden: GRAM_PADEN.length,
      stappen: p.stappen.length,
      soorten: p.stappen.map((s) => s.soort),
      zonderEis: p.stappen.filter((s) => !GRAM_EIS[s.soort]).map((s) => s.brok),
      zonderTekst: p.stappen.filter((s) => !s.nl || !s.en || !s.subNl || !s.subEn).map((s) => s.brok),
      // elke stap met een view moet naar een view wijzen die renderFun ook echt kent
      views: p.stappen.filter((s) => s.view).map((s) => s.view),
      // v23.120: elke verwijzing naar een bestaande les moet oplossen naar een les die bestaat.
      // De verwijzing gaat op TITEL en niet op indexnummer, want dat nummer schuift zodra er een
      // spiekbrief tussen komt. Wordt een titel herschreven, dan valt deze check om in plaats van
      // dat de route stilletjes naar niets wijst.
      spiekStappen: p.stappen.filter((s) => s.soort === 'bestaandeles').map((s) => s.spiek),
      spiekKapot: p.stappen.filter((s) => s.soort === 'bestaandeles' && !gramLesId(s)).map((s) => s.spiek),
      spiekIds: p.stappen.filter((s) => s.soort === 'bestaandeles').map((s) => gramLesId(s))
    };
  });

  console.log('\n-- de data --');
  // v23.117: geen magisch getal meer. Deze suite viel om toen de hertoets erbij kwam, precies zoals
  // pw-conjfase omviel toen er een fase bij kwam. De suite hoort te breken als het pad van GEDRAG
  // verandert, niet als er een stap bij komt.
  ok(data.stappen >= 5, 'het pad heeft minstens vijf stappen (nu: ' + data.stappen + ')');
  ok(data.soorten[data.soorten.length - 1] === 'hertoets',
    'en de laatste stap is de hertoets (nu: ' + data.soorten[data.soorten.length - 1] + ')');
  ok(data.zonderEis.length === 0,
    'DEKKING: elk soort stap heeft een eis in GRAM_EIS (mist: ' + (data.zonderEis.join(', ') || 'niets') + ')');
  ok(data.zonderTekst.length === 0,
    'DEKKING: elke stap heeft een titel en een uitleg, in beide talen (mist: ' + (data.zonderTekst.join(', ') || 'niets') + ')');
  ok(data.spiekStappen.length >= 3,
    'de route wijst naar bestaande lessen in plaats van ze over te doen (' + data.spiekStappen.length + ')');
  ok(data.spiekKapot.length === 0,
    'DEKKING: elke verwijzing naar een bestaande les lost op (kapot: ' + (data.spiekKapot.join(' | ') || 'niets') + ')');

  // ---- 2. verse gebruiker: alles dicht behalve stap 1 ----
  const vers = await page.evaluate(() => {
    S.brok = {};
    funView = 'pad'; renderFun();
    const p = GRAM_PADEN[0];
    return {
      volgende: gramPadVolgende(p),
      klaar: gramPadKlaar(p),
      opSlot: p.stappen.map((s, i) => gramPadOpSlot(p, i)),
      af: p.stappen.map((s, i) => gramPadStap(p, i).af),
      knop: (document.getElementById('btnPadVerder') || {}).innerText || '',
      klikbaar: Array.prototype.filter.call(document.querySelectorAll('.pad-stap'), (d) => d.style.cursor === 'pointer').length
    };
  });

  console.log('\n-- verse gebruiker --');
  ok(vers.volgende === 0, 'de volgende stap is stap 1 (nu: ' + (vers.volgende + 1) + ')');
  ok(vers.klaar === false, 'en het pad is niet af');
  ok(vers.opSlot[0] === false && vers.opSlot.slice(1).every((x) => x === true),
    'DE REGEL: alles behalve stap 1 zit op slot (' + vers.opSlot.map((x) => (x ? 'slot' : 'open')).join(',') + ')');
  ok(vers.klikbaar === 1, 'CONTROLE: precies één stap is aanklikbaar (nu: ' + vers.klikbaar + ')');
  const eersteTitel = await page.evaluate(() => ct(GRAM_PADEN[0].stappen[0].nl, GRAM_PADEN[0].stappen[0].en));
  ok(vers.knop.indexOf(eersteTitel) !== -1, 'de knop wijst naar stap 1 ("' + vers.knop + '")');

  // ---- 3. DE KERN: "alles door elkaar" kan niet je eerste oefening zijn ----
  const doorElkaar = await page.evaluate(new Function(VUL + `
    const p = GRAM_PADEN[0];
    const i = p.stappen.findIndex((s) => s.soort === 'herkennen');
    // alleen de allereerste stap gehaald: de herkentoets hoort nog dicht te zitten
    vulPad(p, 1);
    const naEerste = gramPadOpSlot(p, i);
    // alles ervoor gehaald: nu pas open
    vulPad(p, i);
    const naAlles = gramPadOpSlot(p, i);
    return { i, naEerste, naAlles, volgende: gramPadVolgende(p) };
  `));

  console.log('\n-- DE KERN: door elkaar is de laatste stap --');
  ok(doorElkaar.naEerste === true,
    'CONTROLE: met alleen de eerste stap gehaald zit "welke tijd is dit" nog op slot');
  ok(doorElkaar.naAlles === false,
    'CONTROLE: pas als alles ervoor af is gaat hij open');
  ok(doorElkaar.volgende === doorElkaar.i,
    'en dan is hij ook de volgende stap (nu: ' + (doorElkaar.volgende + 1) + ')');

  // ---- 4. "af" is één begrip, en het kantelt op de goede grens ----
  const grens = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    function afBij(brok, st) { S.brok[brok] = st; return gramPadStap(p, p.stappen.findIndex((s) => s.brok === brok)).af; }
    return {
      betekenis10: afBij('indefimperf.betekenis', {beste: 10, rondes: 1}),
      betekenis11: afBij('indefimperf.betekenis', {beste: 11, rondes: 1}),
      les3: afBij('les.imperfecto', {stapMax: LES_STAPPEN.length - 2}),
      les4: afBij('les.imperfecto', {stapMax: LES_STAPPEN.length - 1}),
      herken9: afBij('vorm.tijd', {beste: 9, rondes: 1}),
      herken10: afBij('vorm.tijd', {beste: 10, rondes: 1})
    };
  });

  console.log('\n-- de grens van "af" --');
  ok(grens.betekenis10 === false && grens.betekenis11 === true,
    'CONTROLE: de betekenisstap kantelt tussen 10 en 11 van de 12');
  ok(grens.les3 === false && grens.les4 === true,
    'CONTROLE: de les is pas af na de laatste stap, niet na de voorlaatste');
  ok(grens.herken9 === false && grens.herken10 === true,
    'CONTROLE: de herkentoets kantelt tussen 9 en 10 van de 12');

  // ---- 5. een stap die nog niet bestaat is geen deur naar niets ----
  const nietBestaand = await page.evaluate(new Function(VUL + `
    const p = GRAM_PADEN[0];
    // alles gehaald BEHALVE de hertoets: die mag pas na de wachttijd (v23.117), dus het pad hoort
    // nog niet klaar te zijn. Afgeleid uit de padvorm en niet uit een opgeschreven index.
    vulPad(p, p.stappen.findIndex((s) => s.soort === 'hertoets'));
    funView = 'pad'; renderFun();
    const keuze = p.stappen.findIndex((x) => x.soort === 'keuze');
    return {
      keuze,
      bestaat: gramPadStap(p, keuze).bestaat,
      volgendeIsKeuze: gramPadVolgende(p) === keuze,
      klaar: gramPadKlaar(p),
      volgende: gramPadVolgende(p),
      klaarMelding: (document.getElementById('padKlaar') || {}).innerText || '',
      knop: document.querySelectorAll('#btnPadVerder').length,
      klikbaar: Array.prototype.filter.call(document.querySelectorAll('.pad-stap'), (d) => d.style.cursor === 'pointer').length
    };
  `));

  console.log('\n-- de stap die nog niet bestaat --');
  ok(nietBestaand.bestaat === false, 'de keuze-stap heeft nog geen scherm');
  ok(nietBestaand.volgendeIsKeuze === false,
    'CONTROLE: hij wordt nooit de volgende stap, dus ook geen knop naar niets');
  // v23.117: met alles groen op de dag zelf is het pad NIET klaar meer, want de hertoets moet nog
  // en die mag pas over drie dagen. Dat is precies het gedrag dat pw-gestold bewaakt.
  ok(nietBestaand.klaar === false,
    'en het pad is nog niet klaar, want de hertoets komt nog (v23.117)');
  ok(nietBestaand.klikbaar >= 4, 'de bestaande stappen blijven aanklikbaar (nu: ' + nietBestaand.klikbaar + ')');

  // ---- 6. CONTROLE: het pad kantelt echt, het zegt niet altijd hetzelfde ----
  ok(vers.af.every((x) => x === false),
    'CONTROLE: vers stond het hele pad op nul, dus deze meting kan verschil zien');

  // ---- 7. de knop gaat naar de juiste plek ----
  await page.evaluate(() => { funView = null; renderFun(); });
  await page.click('#nav button[data-tab="speeltuin"]');
  await page.waitForTimeout(250);
  await page.evaluate(() => { funView = null; renderFun(); });
  await page.waitForTimeout(200);
  const tegel = await page.locator('#ftPad').count();
  if (tegel) await page.click('#ftPad');
  await page.waitForTimeout(300);
  const route = await page.evaluate(new Function(VUL + `
    const p = GRAM_PADEN[0];
    vulPad(p, 0);
    funView = null; gwSess = null;
    funView = 'pad'; renderFun();
    document.getElementById('btnPadVerder').click();
    const na1 = {view: funView, wiz: gwSess ? gwSess.id : null};
    // de eerste twee stappen gehaald: de knop hoort nu naar de derde te gaan
    vulPad(p, 2);
    funView = 'pad'; renderFun();
    const derde = p.stappen[2];
    document.getElementById('btnPadVerder').click();
    return { na1, na2: {view: funView, wiz: gwSess ? gwSess.id : null}, derde: derde.soort };
  `));

  console.log('\n-- de knop --');
  ok(tegel === 1, 'de tegel staat in de Speeltuin');
  ok(!!route.na1.wiz, 'stap 1 opent de bestaande uitleg (nu: ' + route.na1.wiz + ')');
  ok(route.na2.view === 'brok' || !!route.na2.wiz,
    'en met de eerste twee gehaald gaat de knop naar de derde stap, een ' + route.derde);

  // ---- 8. v23.120: DE AFSTEMMING ----
  //
  // Stefan had "Pretérito imperfecto: de vorming" op afgerond staan terwijl het pad zei dat hij de
  // imperfecto nog moest leren. Twee systemen die hetzelfde onderwerp claimen. De route hoort de
  // bestaande les te LEZEN, niet over te doen.
  const afstemming = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    const i = p.stappen.findIndex((s) => s.soort === 'bestaandeles');
    const id = gramLesId(p.stappen[i]);
    S.brok = {}; S.gramwiz = {};
    const voor = gramPadStap(p, i);
    // zet de bestaande les op afgerond, precies zoals de Oefenen-tab dat doet
    S.gramwiz[id] = {stap: 9, klaar: true, rondes: 1};
    const na = gramPadStap(p, i);
    // en half af moet ook half af heten
    S.gramwiz[id] = {stap: 1, klaar: false, rondes: 0};
    const half = gramPadStap(p, i);
    return { i, id, voor: {af: voor.af, stand: voor.stand}, na: {af: na.af, stand: na.stand},
             half: {af: half.af, stand: half.stand} };
  });

  console.log('\n-- DE AFSTEMMING --');
  ok(!!afstemming.id, 'de stap lost op naar een bestaande les ("' + afstemming.id + '")');
  ok(afstemming.voor.af === false, 'onaangeroerd staat hij niet op af');
  ok(afstemming.na.af === true && /afgerond|done/.test(afstemming.na.stand),
    'DE REGEL: staat de bestaande les op afgerond, dan is de stap van de route ook af ("' + afstemming.na.stand + '")');
  ok(afstemming.half.af === false && /stap|step/.test(afstemming.half.stand),
    'CONTROLE: half af is niet af, en de route laat zien hoe ver ("' + afstemming.half.stand + '")');

  // klikken opent de bestaande les en niet een eigen scherm
  const opent = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    const i = p.stappen.findIndex((s) => s.soort === 'bestaandeles');
    funView = null; gwSess = null;
    gramPadGa(p, i);
    return { sessie: gwSess ? gwSess.id : null, funView: funView };
  });
  ok(opent.sessie === afstemming.id,
    'klikken opent de bestaande les zelf (nu: ' + opent.sessie + ')');

  // de les-stap begint niet bij stap 1, want de uitleg is er net geweest
  const vanaf = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    const i = p.stappen.findIndex((s) => s.view === 'les');
    lesSpel = null;
    gramPadGa(p, i);
    return { vanaf: p.stappen[i].vanaf, stap: lesSpel ? lesSpel.stap : null,
             stapId: lesSpel ? lesStapId(lesSpel.stap) : null, t: lesSpel ? lesSpel.t : null };
  });
  ok(typeof vanaf.vanaf === 'number' && vanaf.stap === vanaf.vanaf,
    'CONTROLE: de les begint bij stap ' + (vanaf.vanaf + 1) + ' en niet bij 1, want de uitleg stond in de vorige stap');
  ok(vanaf.stapId === 'herkennen', 'en dat is de herkenstap (nu: ' + vanaf.stapId + ')');
  ok(vanaf.t === 'imperfecto', 'met de juiste tijd (nu: ' + vanaf.t + ')');

  // en de volgorde klopt nog steeds: de uitleg vóór de drill
  const volgorde = await page.evaluate(() => {
    const p = GRAM_PADEN[0];
    const uitleg = p.stappen.findIndex((s) => s.spiek === 'Pretérito imperfecto: de vorming');
    const drill = p.stappen.findIndex((s) => s.view === 'les' && s.arg === 'imperfecto');
    const herken = p.stappen.findIndex((s) => s.soort === 'herkennen');
    return { uitleg, drill, herken, n: p.stappen.length };
  });
  ok(volgorde.uitleg < volgorde.drill,
    'DE VOLGORDE: de uitleg staat vóór de drill (' + (volgorde.uitleg + 1) + ' voor ' + (volgorde.drill + 1) + ')');
  ok(volgorde.drill < volgorde.herken,
    'en de drill vóór het door elkaar herkennen (' + (volgorde.drill + 1) + ' voor ' + (volgorde.herken + 1) + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
