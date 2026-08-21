// pw-blokken.js (20 aug, v23.142) — zie je de blokken van je dag, en waar je erin zit?
//
// WAAROM DIT ER IS
//
// Stefan: "wat ik nog steeds niet snap is dat als ik naar vandaag [ga] ik niet de blokken zie wat ik
// vandaag ga doen. Het prototype wat je maakte was goed, ik snap niet waarom we dit niet live
// doorvoeren."
//
// Het plan bestond sinds v23.135 en de getallen klopten (dat bewaakt pw-dagplan). Wat er niet was:
// het was te lezen als voetnoot, het stond er niet meer als je klaar was, en tijdens je les zag je
// nergens waar dat "stap 4 van 5" zat.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE BALK STAAT ER, OP SCHAAL. Eén staafje per blok, en de breedte is de tijd van dat blok.
//      Een balk met gelijke staafjes liegt over de verhouding, en die verhouding is het punt.
//   2. EN HIJ LOOPT MEE. In de banner tijdens je les is het blok waar je in zit "aan" en zijn de
//      blokken die je gehad hebt "vol". Dat is de "waar ben ik"-vraag zonder te tellen.
//   3. ELK BLOK ZEGT WAAR HET VOOR IS. leren / begrijpen / zelf maken / sneller: Nation's vier
//      draden in gewone woorden.
//   4. DE UITLEG ALLEEN ALS HET WAAR IS. De regel over "alle vier de manieren" staat er alleen als
//      alle vier de draden er vandaag echt zijn. Anders belooft het plan iets wat er niet is.
//   5. NA JE LES STAAT HET ER NOG, AFGEVINKT. "Dit deed je vandaag", alle blokken met een vinkje.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door de balk altijd te tonen met vaste breedtes: dan klopt punt 1
// half en is punt 4 stuk. Daarom wordt de breedte vergeleken met de seconden van het blok zelf, en
// staat tegenover elke aanwezigheid een afwezigheid: mist er een draad, dan verdwijnt de uitlegregel.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwBl' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    S.dagen = { count: 5 };                       // het plan staat er vanaf dag twee (v23.135)
    dagPlanVerval();

    const p = dagPlan();
    uit.blokken = p.blokken.map(function (b) { return { stap: b.stap, naam: b.naam, draad: b.draad, sec: b.sec }; });

    // ---- 1. de balk staat er, op schaal ----
    const doos = document.createElement('div');
    doos.innerHTML = dagBalkHtml();
    const staaf = doos.querySelectorAll('.dagbalk i');
    uit.nStaaf = staaf.length;
    // style.flex is de shorthand en die leest niet altijd terug; flexGrow is wat er echt gezet wordt
    uit.flex = Array.prototype.map.call(staaf, function (x) { return Number(x.style.flexGrow); });
    uit.klassen = Array.prototype.map.call(staaf, function (x) { return x.className; });

    // ---- 2. en hij loopt mee ----
    lesFlowStart();
    lesFlow.stap = p.stappen[2];
    const ban = document.createElement('div');
    /* v23.155: de strook is uit de schermen gehaald en staat nu in het lesframe bovenaan;
       lesFlowBannerHtml() cijfert zichzelf daarom weg zolang die les loopt. lesStrookHtml() is
       de functie die hem nog steeds bouwt, en daar gaat deze meting over. */
    ban.innerHTML = lesStrookHtml();
    const bs = ban.querySelectorAll('.dagbalk i');
    uit.banStaaf = bs.length;
    uit.banKlassen = Array.prototype.map.call(bs, function (x) { return x.className; });
    lesFlow = null;

    // ---- 3, 4 en 5. het lijstje ----
    const toon = function (arg) {
      const d = document.createElement('div');
      d.innerHTML = dagPlanHtml(arg);
      return d;
    };
    const d = toon();
    uit.rijen = Array.prototype.map.call(d.querySelectorAll('.dagrij'), function (x) {
      const dr = x.querySelector('.d');
      return { n: x.querySelector('.n').textContent, draad: dr ? dr.textContent : null,
               tekst: x.textContent.replace(/\s+/g, ' ').trim() };
    });
    uit.uitleg = /alle vier de manieren/.test(d.textContent);
    uit.kop = d.querySelector('p') ? d.querySelector('p').textContent : '';

    // ---- 4. het controlegeval: mist er een draad, dan geen belofte ----
    const echt = dagPlan;
    dagPlan = function () {
      const q = echt();
      return { p: q.p, sleutel: q.sleutel, min: q.min, sec: q.sec, gemeten: q.gemeten,
               stappen: q.stappen.slice(),
               blokken: q.blokken.map(function (b) { return Object.assign({}, b, { draad: 'leren' }); }) };
    };
    uit.eenDraadUitleg = /alle vier de manieren/.test(toon().textContent);
    dagPlan = echt;

    // ---- 5. na je les ----
    const k = toon('klaar');
    uit.klaarKop = k.querySelector('p') ? k.querySelector('p').textContent : '';
    uit.klaarVink = (k.textContent.match(/✓/g) || []).length;
    uit.klaarUitleg = /alle vier de manieren/.test(k.textContent);
    uit.klaarRijen = k.querySelectorAll('.dagrij').length;
    return uit;
  });

  const n = r.blokken.length;
  console.log('\n-- 1. de balk staat er, op schaal --');
  console.log('   ' + r.blokken.map(function (b) { return b.naam + '(' + b.draad + ') ' + Math.round(b.sec) + 's'; }).join(' | '));
  ok(r.nStaaf === n, 'één staafje per blok (' + r.nStaaf + ' van ' + n + ')');
  ok(r.flex.every(function (f, i) { return f === Math.max(1, Math.round(r.blokken[i].sec)); }),
    'en de breedte is de tijd van dat blok, niet een vaste maat (' + JSON.stringify(r.flex) + ')');
  ok(r.klassen.every(function (c) { return c === 'vol'; }), 'vóór je begint staat alles ingekleurd');

  console.log('\n-- 2. en hij loopt mee door je les --');
  ok(r.banStaaf === n, 'de balk staat ook in de banner tijdens je les');
  ok(r.banKlassen[2] === 'aan', 'het blok waar je in zit is aan (nu: "' + r.banKlassen[2] + '")');
  ok(r.banKlassen[0] === 'vol' && r.banKlassen[1] === 'vol', 'wat je gehad hebt is vol');
  ok(r.banKlassen.slice(3).every(function (c) { return c === ''; }), 'en wat nog komt is leeg');

  console.log('\n-- 3. elk blok zegt waar het voor is --');
  console.log('   ' + r.rijen.map(function (x) { return x.n + ' ' + x.tekst; }).join(' / '));
  ok(r.rijen.length === n, 'er staat een rij per blok');
  ok(r.rijen.every(function (x) { return !!x.draad; }), 'en elke rij heeft een draad');
  ok(r.blokken.every(function (b) { return ['leren', 'begrijpen', 'zelf maken', 'sneller'].indexOf(b.draad) !== -1; }),
    'en dat is er een van de vier');
  ok(/min/.test(r.rijen[0].tekst), 'met de minuten erbij');

  console.log('\n-- 4. de uitleg alleen als het waar is --');
  ok(r.uitleg, 'met alle vier de draden staat de regel erover eronder');
  ok(r.eenDraadUitleg === false, 'het controlegeval: één draad, geen belofte over vier');

  console.log('\n-- 5. na je les staat het er nog, afgevinkt --');
  ok(/Dit deed je vandaag/.test(r.klaarKop), 'de kop vraagt niet meer wat je gaat doen (nu: "' + r.klaarKop + '")');
  ok(r.klaarVink === n, 'alle blokken staan afgevinkt (' + r.klaarVink + ' van ' + n + ')');
  ok(r.klaarUitleg === false, 'en de uitleg over de draden staat er niet meer bij');
  ok(r.klaarRijen === n, 'met alle rijen er nog in');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
