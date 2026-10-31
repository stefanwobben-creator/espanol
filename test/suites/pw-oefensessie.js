// pw-oefensessie.js (31 okt, v23.259 t/m v23.261) — een oordeel over vijf antwoorden, en een
// sessie die door elkaar oefent.
//
// WAAROM DEZE SUITE ER IS
//
// Stefan: "het oefenen van grammatica, nu zijn er twee en dan stop ik (...) wil ik echt oefenen
// dan wil ik er veel meer achter elkaar oefenen, 10 of 20 of 50 (...) en als er 2 vragen zijn en
// ik heb een fout is al 50% fout, maar fouten gebeuren, dus ook hier minimaal 5 ofzo, maar dat ik
// vanaf niveau 4 terug kan naar 3 of naar 5 kan."
//
// Uitgerekend wat twee vragen meten, kans op promotie bij een werkelijk kennisniveau p:
//
//     2 van 2 (oud)   p=0,90: 81%   p=0,60: 36%   gokker: 25%
//     4 van 5         p=0,90: 92%   p=0,60: 34%   gokker: 19%
//     6 van 8         p=0,90: 96%   p=0,60: 32%   gokker: 14%
//
// Meer vragen is dus niet milder maar scherper: de kenner zakt minder vaak en de gokker komt er
// minder vaak doorheen. Dat is de hele rechtvaardiging van v23.259.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DRIE UITKOMSTEN IN PLAATS VAN TWEE. 75 procent of meer is een doos omhoog, 50 tot 74 blijft
//      staan, daaronder een doos omlaag. En omlaag is één doos, niet alles.
//   2. DE GRENS. Onder de vijf antwoorden verandert er niets: dan geldt de oude regel, en die is
//      hard. Zonder deze proef is punt 1 een sluiproute om met twee makkelijke antwoorden te
//      promoveren.
//   3. DE BODEM EN HET PLAFOND. Doos 0 kan niet verder omlaag, de bovenste doos niet verder omhoog.
//   4. DE SESSIE DEELT UIT OVER ONDERWERPEN. Hoogstens GC_SESSIE_PER_ONDERWERP per onderwerp, en
//      door elkaar en niet gebundeld. Rohrer, Dedrick en Stershic (2015): dezelfde oefenstof
//      gebundeld tegenover door elkaar, een maand later getoetst, 38 procent tegen 72.
//   5. ELKE VRAAG DRAAGT ZIJN EIGEN ONDERWERP. Zonder dat zou een sessie alles op één doosje
//      schrijven, en dat is de fout die v23.107 al eens heeft rechtgezet voor de microles.
//   6. EN HET SLOTSCHERM ZEGT WAT ER MET JE KAART GEBEURDE, niet wat je score was.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwOs' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1 tot en met 3. het oordeel ----
  console.log('\n-- 1. drie uitkomsten in plaats van twee --');
  const doos = await page.evaluate(() => {
    function dag(vanaf, rij) {
      S.gram = {};
      S.gram['proef#0'] = { box: vanaf, due: '', goed: 0, fout: 0, laatst: '', bd: '' };
      rij.forEach(function (g) { gramBij('proef', g, 3, 0, 'sessie'); });
      const st = S.gram['proef#0'];
      return { box: st.box, due: st.due };
    }
    const G = true, F = false;
    return {
      min: GRAM_OORDEEL_MIN, op: GRAM_OORDEEL_OP, neer: GRAM_OORDEEL_NEER,
      maxDoos: GRAM_BOX.length - 1, morgen: addDays(today(), 1),
      // 4 van 5 = 80 procent: omhoog
      omhoog: dag(3, [G, G, F, G, G]),
      // 3 van 5 = 60 procent: blijft staan
      blijft: dag(3, [G, F, G, F, G]),
      // 2 van 5 = 40 procent: een doos omlaag, en niet naar nul
      omlaag: dag(3, [F, G, F, G, F]),
      // vier antwoorden met een misser: te weinig voor een oordeel, dus de oude regel
      tekort: dag(3, [G, G, G, F]),
      // de bodem
      bodem: dag(0, [F, F, F, F, G]),
      // het plafond
      plafond: dag(5, [G, G, G, G, G])
    };
  });
  console.log('   omhoog ' + doos.omhoog.box + ' · blijft ' + doos.blijft.box +
    ' · omlaag ' + doos.omlaag.box + ' · tekort ' + doos.tekort.box);
  ok(doos.min === 5, 'een oordeel gaat over minstens ' + doos.min + ' antwoorden');
  ok(doos.omhoog.box === 4, 'vier van de vijf goed (80%) is een doos omhoog: 3 → ' + doos.omhoog.box);
  ok(doos.blijft.box === 3, 'drie van de vijf (60%) blijft staan: 3 → ' + doos.blijft.box);
  ok(doos.blijft.due === doos.morgen, 'en komt morgen terug');
  ok(doos.omlaag.box === 2, 'twee van de vijf (40%) is EEN doos omlaag: 3 → ' + doos.omlaag.box);
  ok(doos.omlaag.due === doos.morgen, 'en komt ook morgen terug');

  console.log('\n-- 2. de grens: onder de vijf antwoorden verandert er niets --');
  ok(doos.tekort.box === 0,
    'vier antwoorden met een misser valt nog gewoon naar nul (' + doos.tekort.box + '), ' +
    'anders is dit een sluiproute om met twee makkelijke antwoorden te promoveren');

  console.log('\n-- 3. de bodem en het plafond --');
  ok(doos.bodem.box === 0, 'doos 0 kan niet verder omlaag (' + doos.bodem.box + ')');
  ok(doos.plafond.box === doos.maxDoos, 'en de bovenste doos niet verder omhoog (' + doos.plafond.box + ')');

  // ---- 4 en 5. de sessie ----
  console.log('\n-- 4. de sessie deelt uit over onderwerpen --');
  const sess = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
    const o = gcVernieuw(gcSessieId(20));
    if (!o) return { fout: 'geen sessie gebouwd' };
    const vr = o.stappen[0].vragen;
    const per = {};
    vr.forEach(function (q) { per[q.cid] = (per[q.cid] || 0) + 1; });
    // hoe vaak staan twee buren van hetzelfde onderwerp naast elkaar?
    let buren = 0;
    for (let i = 1; i < vr.length; i++) if (vr[i].cid === vr[i - 1].cid) buren++;
    return {
      n: vr.length, stappen: o.stappen.length, sessie: !!o.sessie, concept: o.concept,
      onderwerpen: Object.keys(per).length, max: Math.max.apply(null, Object.values(per)),
      grens: GC_SESSIE_PER_ONDERWERP, buren: buren,
      zonderCid: vr.filter(function (q) { return !q.cid; }).length,
      lengtes: GC_SESSIE_LENGTES.slice(),
      // de eerste ronde: zoveel vragen als er onderwerpen zijn. Bij een schone lei staan er maar
      // drie open (GC_VENSTER), dus "de eerste vijf" zou hier niets zeggen.
      eersteRonde: vr.slice(0, Object.keys(per).length).map(function (q) { return q.cid; })
    };
  });
  console.log('   ' + sess.n + ' vragen over ' + sess.onderwerpen + ' onderwerpen, hoogstens ' +
    sess.max + ' per onderwerp, ' + sess.buren + ' keer twee dezelfde naast elkaar');
  ok(!sess.fout, 'er wordt een sessie gebouwd' + (sess.fout ? ': ' + sess.fout : ''));
  ok(sess.n >= 10, 'met een flink aantal vragen (' + sess.n + ' gevraagd: 20)');
  ok(sess.stappen === 1, 'in één stap, want een sessie is oefenen en geen les');
  ok(sess.onderwerpen >= 2, 'over meer dan één onderwerp (' + sess.onderwerpen + ')');
  ok(sess.max <= sess.grens, 'en hoogstens ' + sess.grens + ' vragen per onderwerp (' + sess.max + ')');
  ok(new Set(sess.eersteRonde).size === sess.eersteRonde.length && sess.eersteRonde.length === sess.onderwerpen,
    'de eerste ronde raakt elk onderwerp precies één keer (' + sess.eersteRonde.join(', ') + ')');
  ok(sess.buren <= Math.floor(sess.n / 4),
    'en er staan nauwelijks twee vragen van hetzelfde onderwerp naast elkaar (' + sess.buren + ' van ' + sess.n + ')');
  ok(sess.lengtes.length === 3, 'er zijn drie lengtes om uit te kiezen (' + sess.lengtes.join(', ') + ')');

  console.log('\n-- 5. elke vraag draagt zijn eigen onderwerp --');
  ok(sess.zonderCid === 0, 'geen enkele vraag zonder onderwerp (' + sess.zonderCid + ')');
  ok(!sess.concept, 'en de sessie zelf hangt niet aan één concept (' + sess.concept + ')');

  const schrijft = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
    const o = gcVernieuw(gcSessieId(10));
    const stap = o.stappen[0];
    // twee vragen van verschillende onderwerpen, allebei goed beantwoord
    const q1 = stap.vragen[0], q2 = stap.vragen.filter(function (q) { return q.cid !== stap.vragen[0].cid; })[0];
    gramAntwoord(o, stap, q1, q1.g);
    gramAntwoord(o, stap, q2, q2.g);
    return {
      cid1: q1.cid, cid2: q2.cid,
      sleutels: Object.keys(S.gram),
      goed1: (gramLees(q1.cid).goed || 0), goed2: (gramLees(q2.cid).goed || 0)
    };
  });
  ok(schrijft.cid1 !== schrijft.cid2, 'twee vragen van twee onderwerpen (' + schrijft.cid1 + ', ' + schrijft.cid2 + ')');
  ok(schrijft.goed1 >= 1 && schrijft.goed2 >= 1,
    'allebei de antwoorden landen op hun eigen doosje (' + schrijft.sleutels.join(', ') + ')');

  // ---- 6. het slotscherm ----
  console.log('\n-- 6. het slotscherm zegt wat er met je kaart gebeurde --');
  const slot = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null; S.gcKeuze = [];
    show('spiekbrief');
    gcSessieStart(10);
    if (!gwSess) return { fout: 'geen sessie gestart' };
    const o = gwOnderwerp(gwSess.id);
    const stap = o.stappen[0];
    const eerste = stap.vragen[0].cid;
    // vijf goede antwoorden op één onderwerp: dat doosje hoort omhoog te gaan
    stap.vragen.filter(function (q) { return q.cid === eerste; })
      .concat(stap.vragen.filter(function (q) { return q.cid === eerste; }))
      .slice(0, 5)
      .forEach(function (q) { gramBij(eerste, true, 3, q.pi, 'sessie'); });
    const html = gcSessieSlotHtml();
    return { fout: null, eerste: eerste, html: html, voor: gwSess.voorBox ? Object.keys(gwSess.voorBox).length : 0,
             box: gramLees(eerste).box };
  });
  ok(!slot.fout, 'de sessie start' + (slot.fout ? ': ' + slot.fout : ''));
  ok(slot.voor > 0, 'en legt vast waar de doosjes stonden (' + slot.voor + ' onderwerpen)');
  ok(/Wat er met je kaart gebeurde/.test(slot.html || ''), 'het slotscherm heeft een kop over je kaart');
  ok(/doos omhoog/i.test(slot.html || ''), 'en noemt wat omhoog ging (doos van ' + slot.eerste + ': ' + slot.box + ')');

  // ---- 7. en de knop staat er ook echt ----
  console.log('\n-- 7. de knoppen staan op de grammaticatab --');
  await page.evaluate(() => { gwSluit(); show('spiekbrief'); try { renderCheat(); } catch (e) {} });
  await page.waitForTimeout(400);
  const knoppen = await page.evaluate(() => ({
    n: document.querySelectorAll('[data-gcsessie]').length,
    labels: Array.from(document.querySelectorAll('[data-gcsessie]')).map(function (d) { return d.getAttribute('data-gcsessie'); })
  }));
  ok(knoppen.n === 3, 'er staan drie knoppen (' + knoppen.labels.join(', ') + ')');
  await page.locator('[data-gcsessie="10"]').scrollIntoViewIfNeeded();
  await page.click('[data-gcsessie="10"]');
  await page.waitForTimeout(500);
  const naKlik = await page.evaluate(() => ({
    id: gwSess ? gwSess.id : null,
    foto: gwSess && gwSess.voorBox ? Object.keys(gwSess.voorBox).length : 0,
    opScherm: (document.getElementById('cheat') || {}).textContent ?
      document.getElementById('cheat').textContent.replace(/\s+/g, ' ').slice(0, 90) : ''
  }));
  ok(naKlik.id === 'sessie-10', 'een klik start de sessie (' + naKlik.id + ')');
  ok(naKlik.foto > 0, 'met de foto van je doosjes erbij (' + naKlik.foto + ' onderwerpen)');
  console.log('   ' + naKlik.opScherm);

  ok(errs.length === 0, 'geen pagina-fouten: ' + (errs.slice(0, 3).join(' | ') || 'geen'));

  await browser.close();
  console.log(fout ? '\n' + fout + ' GEFAALD' : '\nalles goed');
  process.exit(fout ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
