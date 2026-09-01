// pw-gramflow.js (22 aug, v23.172) — hervat een afgerond onderwerp op zijn laatste stap?
//
// WAAROM DIT ER IS
//
// Stefan, 22 aug: "die hele grammatica flow, ook van andere oefeningen, loopt niet lekker, helemaal
// niet het herhaal. Ik krijg een vraag en spring van stap 1 naar 4 bijvoorbeeld, of oefenen twee
// keer en aan het einde nog een keer."
//
// Het eerste is een echt defect en het is in de code na te lopen. `v.stap` is een hoogwatermerk: hij
// gaat alleen omhoog, nooit terug, en gwStart() hervat op Math.min(v.stap, aantalStappen - 1).
// Zodra je een conceptles één keer hebt afgerond wijst dat altijd naar de laatste stap, de
// begripsvraag, en zie je de voorbeelden nooit meer.
//
// WAT ER NIET IS GEBOUWD, WANT DAT BEPAALT WAT HIER STAAT
//
// Mijn hoofdvoorstel was: één concept, één blok per dagles. Grond: "drie ontmoetingen binnen één
// sessie tellen samen als ongeveer één gespreide ontmoeting." Precies omgekeerd, en Karpicke &
// Bauernschmidt 2011 hebben dat experiment gedaan: drie keer ophalen direct achter elkaar geeft 26
// procent retentie na een week, drie keer mét andere items ertussen 49 tot 75 procent, één keer 25
// procent. De vier blokken van Vamos liggen verspreid over een sessie van 168 antwoorden, dus dat
// is de gúnstige conditie. Deze suite bewaakt daarom nadrukkelijk NIET dat een concept maar één keer
// per les langskomt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. EEN AFGEROND ONDERWERP KOMT TERUG ALS OPFRISSER. Eén vraag, niet de laatste stap van een les
//      die je al kent.
//   2. EN EEN ONAFGEROND ONDERWERP GEWOON WAAR JE GEBLEVEN WAS. Het controlegeval: dit is groen te
//      krijgen door alles naar de opfrisser te sturen, en dan is de microles onbereikbaar geworden.
//   3. ZELF EEN STAP KIEZEN BLIJFT ZELF EEN STAP KIEZEN. Klikken op stap 3 in de stapbalk opent
//      stap 3, ook bij een afgerond onderwerp. De omleiding geldt alleen als de app kiest.
//   4. JE ZIET WAAR JE GEBLEVEN WAS, OOK BUITEN DE DAGLES. gramWaaromHtml() zei dat alleen in de
//      flow, en alleen als je niet eerder in de fout-tak of de klaar-tak viel.
//   5. DE LEDGER KIJKT MEE EN BESLIST NIETS. Hij telt per concept per dag hoeveel vragen, hoeveel
//      goed en via welk kanaal, en hij verandert geen doos, geen XP en geen volgorde. Dat laatste is
//      de helft die ertoe doet: dit is een meetinstrument, en een meetinstrument dat stiekem stuurt
//      is geen meetinstrument.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwGf' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    /* Een concept dat genoeg vragen oplevert om meerdere stappen te hebben, anders meet punt 2
       niets: bij één stap is "waar je gebleven was" altijd stap 1. */
    let cid = null, stappen = 0;
    gcGeordend().some(function (c) {
      const o = gwOnderwerp('concept-' + c.id);
      if (o && o.stappen && o.stappen.length >= 2) { cid = c.id; stappen = o.stappen.length; return true; }
      return false;
    });
    uit.cid = cid; uit.stappen = stappen;
    if (!cid) return uit;

    const wid = 'concept-' + cid;

    // ---- 1. afgerond onderwerp -> opfrisser ----
    S.gramwiz = S.gramwiz || {};
    S.gramwiz[wid] = { stap: stappen, klaar: true, rondes: 3 };
    gwSess = null;
    gwStart(wid);
    uit.naKlaar = gwSess ? { id: gwSess.id, stap: gwSess.stap,
                             vragen: (gwOnderwerp(gwSess.id).stappen[gwSess.stap].vragen || []).length,
                             stappen: gwOnderwerp(gwSess.id).stappen.length } : null;

    // ---- 2. het controlegeval: onafgerond hervat gewoon ----
    S.gramwiz[wid] = { stap: 1, klaar: false, rondes: 1 };
    gwSess = null;
    gwStart(wid);
    uit.naHalf = gwSess ? { id: gwSess.id, stap: gwSess.stap } : null;

    // ---- 3. zelf een stap kiezen blijft zelf kiezen ----
    S.gramwiz[wid] = { stap: stappen, klaar: true, rondes: 3 };
    gwSess = null;
    gwStart(wid, 0);
    uit.metStap = gwSess ? { id: gwSess.id, stap: gwSess.stap } : null;

    // ---- 4. "hier was je gebleven", buiten de dagles ----
    lesFlow = null;
    S.gramwiz[wid] = { stap: 1, klaar: false, rondes: 1 };
    gwSess = null;
    gwStart(wid);
    show('spiekbrief', true);
    renderCheat();
    uit.buitenFlow = document.getElementById('cheat').textContent.replace(/\s+/g, ' ');
    uit.zegtGebleven = /Hier was je gebleven/.test(uit.buitenFlow);

    // ---- 5. de ledger kijkt mee en beslist niets ----
    S.gramLog = {};
    S.gram = S.gram || {};
    S.gram.proefc = { box: 3, due: '2026-12-01', goed: 4, fout: 1, laatst: '', bd: today() };
    const doosVoor = JSON.stringify(S.gram.proefc);
    const xpVoor = S.txp || 0;
    gramLog('proefc', 'microles', true);
    gramLog('proefc', 'microles', false);
    gramLog('proefc', 'toets', true);
    uit.doosOnaangeroerd = JSON.stringify(S.gram.proefc) === doosVoor;
    uit.xpOnaangeroerd = (S.txp || 0) === xpVoor;
    const vandaag = gramLogVandaag().filter(function (x) { return x.cid === 'proefc'; })[0];
    uit.ledger = vandaag || null;

    // en hij groeit niet eindeloos
    for (let i = 0; i < 12; i++) {
      S.gramLog[addDays(today(), -i - 1)] = { x: { n: 1, goed: 1, k: {} } };
    }
    gramLog('proefc', 'microles', true);
    uit.dagenBewaard = Object.keys(S.gramLog).length;
    uit.opfrisVragen = GC_OPFRIS_VRAGEN;
    return uit;
  });

  console.log('\n-- opzet --');
  console.log('   concept: ' + r.cid + ' met ' + r.stappen + ' stappen');
  ok(!!r.cid, 'er is een concept met meer dan één stap om mee te meten');

  console.log('\n-- 1. een afgerond onderwerp komt terug als opfrisser --');
  console.log('   ' + JSON.stringify(r.naKlaar));
  ok(!!r.naKlaar && /^opfris-/.test(r.naKlaar.id), 'de app opent de opfrisser (' + (r.naKlaar || {}).id + ')');
  ok(!!r.naKlaar && r.naKlaar.stappen === 1, 'die één stap heeft');
  /* v23.225: hier stond `=== 1`. De opfrisser heeft twee vragen gekregen, want één driekeuzevraag
     is 33 procent raden en zette het doosje toch een hele stap verder. Het getal komt uit de app
     (GC_OPFRIS_VRAGEN) en niet uit deze suite: een proef die zijn eigen aanname meeneemt kan hem
     niet weerspreken. */
  ok(!!r.naKlaar && r.naKlaar.vragen === r.opfrisVragen,
    'met ' + r.opfrisVragen + ' vragen erin (' + (r.naKlaar || {}).vragen + ')');

  console.log('\n-- 2. het controlegeval: onafgerond hervat gewoon --');
  console.log('   ' + JSON.stringify(r.naHalf));
  ok(!!r.naHalf && r.naHalf.id === 'concept-' + r.cid, 'een onafgerond onderwerp opent gewoon de microles');
  ok(!!r.naHalf && r.naHalf.stap === 1, 'op de stap waar je gebleven was (' + (r.naHalf || {}).stap + ')');

  console.log('\n-- 3. zelf een stap kiezen blijft zelf kiezen --');
  ok(!!r.metStap && r.metStap.id === 'concept-' + r.cid && r.metStap.stap === 0,
    'gwStart(id, 0) opent stap 1 van de microles, ook als het onderwerp af is');

  console.log('\n-- 4. je ziet waar je gebleven was, ook buiten de dagles --');
  ok(r.zegtGebleven, 'de stapregel staat er ("' + (r.buitenFlow || '').slice(0, 80) + '")');

  console.log('\n-- 5. de ledger kijkt mee en beslist niets --');
  console.log('   ' + JSON.stringify(r.ledger));
  ok(!!r.ledger && r.ledger.n === 3, 'drie antwoorden geteld (' + ((r.ledger || {}).n) + ')');
  ok(!!r.ledger && r.ledger.goed === 2, 'waarvan twee goed (' + ((r.ledger || {}).goed) + ')');
  ok(!!r.ledger && r.ledger.blokken === 2, 'uit twee verschillende kanalen (' + ((r.ledger || {}).kanalen || []).join(', ') + ')');
  ok(r.doosOnaangeroerd, 'en het doosje is niet aangeraakt: dit meet, het stuurt niet');
  ok(r.xpOnaangeroerd, 'net zomin als je XP');
  ok(r.dagenBewaard <= 7, 'de ledger blijft zeven dagen diep (' + r.dagenBewaard + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
