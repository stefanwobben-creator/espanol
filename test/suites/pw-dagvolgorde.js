// pw-dagvolgorde.js (27 aug, v23.200) — de balk zegt dezelfde volgorde als de les loopt
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 27 aug: "ik heb trouwens idee dat zinnen maken, typen ook heel goed werkt."
//
// Gemeten over zijn 38 dagen, aantal keer geopend: spiekbrief 42, oefenen 41, gramles 37,
// speeltuin 28, woorden 26 ... en vertalen 4. De vorm waarvan hij zegt dat hij het beste werkt is
// een van de minst bezochte schermen. Reden: het schrijfblok stond ná het leesblok, en dat is een
// heel hoofdstuk.
//
// v23.200 draait die twee om: toetsje → schrijven → lezen/luisteren.
//
// EN WAAROM DAT EEN PROEF NODIG HEEFT
//
// De volgorde staat op twee plekken. dagPlan() bouwt de blokkenlijst die je op Vandaag ziet en die
// de balk boven je les tekent; lesFlowVolgendeKern() loopt de stappen echt af. Twee plekken die
// hetzelfde weten lopen uit elkaar, en dan belooft de balk iets anders dan wat er komt. Dat is
// precies de vorm van alle bugs van deze week, dus die twee horen naast elkaar gelegd te worden in
// plaats van er allebei op te vertrouwen.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET SCHRIJVEN KOMT VOOR HET LEZEN, in de flow die echt loopt. Dit is de eigenlijke regel.
//   2. EN DE BALK ZEGT HETZELFDE. De blokkenlijst van dagPlan() staat in dezelfde volgorde als de
//      stappen die lesFlowVolgendeKern() aflegt.
//   3. HET LEESBLOK IS NIET WEGGEVALLEN. Het controlegeval bij 1: het schrijven vooraan zetten door
//      het lezen te laten verdwijnen haalt proef 1 ook, en dat is precies wat we niet willen.
//   4. DE ROUTE WORDT GENOTEERD: een goed antwoord schrijft op in welke stand het kwam, en typen en
//      tegels komen er verschillend uit. Zonder dat veld blijft "typen werkt beter" een gevoel.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDv' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 1 t/m 3. de volgorde ----
  console.log('\n-- 1 t/m 3. schrijven voor lezen, en de balk zegt hetzelfde --');
  const v = await page.evaluate(() => {
    (tLessons() || []).forEach(function (l) {
      S.lessons[l.id] = { done: true, woorden: true, zinnen: true, quiz: true, spiek: true };
    });
    try { persist(); } catch (e) {}

    // wat de balk belooft
    const plan = dagPlan().blokken.map(function (b) { return b.stap + (b.vaardigheid ? ':' + b.vaardigheid : ''); });

    /* en wat de les echt doet. De stappen worden afgelezen na elke overgang; de flow zelf opent
       schermen, dus dit is de volgorde zoals hij op het scherm aankomt en niet zoals hij bedoeld is. */
    lesFlowStart();
    const echt = [];
    for (let k = 0; k < 12 && lesFlow; k++) {
      lesFlowVolgende();
      if (!lesFlow) break;
      const stap = lesFlow.stap + (lesFlow.vaardigheid ? ':' + lesFlow.vaardigheid : '');
      if (echt[echt.length - 1] !== stap) echt.push(stap);
      // een toets openhouden zou de lus laten hangen; die spelen we uit
      let n = 0;
      while (document.querySelector('#qCard .opt') && n++ < 40) {
        const oi = qState.volgorde[qState.i].oi;
        document.querySelectorAll('#qCard .opt')[qState.qz.vragen[oi].c].click();
        const nb = document.getElementById('btnNextQ');
        if (nb) nb.click(); else break;
      }
    }
    const kaal = function (s) { return String(s).split(':')[0]; };
    return { plan: plan, echt: echt, planKaal: plan.map(kaal), echtKaal: echt.map(kaal) };
  });
  console.log('   balk : ' + v.plan.join(' → '));
  console.log('   echt : ' + v.echt.join(' → '));

  const iSchrijf = v.echtKaal.indexOf('produceren');
  const iInput = v.echtKaal.indexOf('input');
  ok(iSchrijf >= 0, 'het schrijfblok zit in de les (plek ' + iSchrijf + ')');
  ok(iInput >= 0, 'CONTROLE: en het leesblok is niet weggevallen (plek ' + iInput + ')');
  ok(iSchrijf >= 0 && iInput >= 0 && iSchrijf < iInput,
    'het schrijven komt vóór het lezen (' + iSchrijf + ' < ' + iInput + ')');

  /* de twee volgordes naast elkaar. Alleen de stappen die in allebei voorkomen, want de balk toont
     geen stap die vandaag niets te doen heeft en de flow slaat die dan ook over. */
  const gedeeld = v.planKaal.filter(function (s) { return v.echtKaal.indexOf(s) >= 0; });
  const echtGedeeld = v.echtKaal.filter(function (s) { return v.planKaal.indexOf(s) >= 0; });
  ok(gedeeld.length >= 3, 'er zijn genoeg blokken om over te vergelijken (' + gedeeld.join(', ') + ')');
  ok(gedeeld.join('>') === echtGedeeld.join('>'),
    'de balk staat in dezelfde volgorde als de les loopt\n     balk: ' + gedeeld.join(' → ') +
    '\n     echt: ' + echtGedeeld.join(' → '));

  // ---- 4. de route wordt genoteerd ----
  console.log('\n-- 4. welke stand hielp --');
  const r = await page.evaluate(() => {
    S.zinRoute = {};
    zinRouteBij('sA', 'moeilijk');
    zinRouteBij('sB', 'tegels');
    zinRouteBij('sC', 'moeilijk');
    const na = JSON.parse(JSON.stringify(S.zinRoute));
    // sC is daarna weer misgegaan
    S.errors['zin:sC'] = { count: 1, dag: addDays(today(), 1) };
    const stand = zinRouteStand();
    delete S.errors['zin:sC'];
    return { na: na, stand: stand };
  });
  console.log('   ' + JSON.stringify(r.stand));
  ok(r.na.sA && r.na.sA.r === 'typ' && r.na.sB && r.na.sB.r === 'tegel',
    'typen en tegels komen er verschillend uit (' + JSON.stringify(r.na.sA) + ' / ' + JSON.stringify(r.na.sB) + ')');
  ok(r.stand.typ.n === 2 && r.stand.tegel.n === 1,
    'de stand telt per stand (' + r.stand.typ.n + ' getypt, ' + r.stand.tegel.n + ' via tegels)');
  ok(r.stand.typ.mis === 1 && r.stand.tegel.mis === 0,
    'CONTROLE: en een zin die daarna weer misging telt als misgegaan, de andere niet');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
