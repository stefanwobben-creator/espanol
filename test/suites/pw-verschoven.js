// pw-verschoven.js (20 aug, v23.138) — zie je na je les wat er is veranderd?
//
// WAAROM DIT ER IS
//
// Stefan, 20 aug: "nadat je een les hebt gedaan wil je ook live feedback op je ontwikkeling."
//
// Het eindscherm zei "¡Muy bien! Chispa is blij met je" en "+2 tapas". Geen enkel getal over wat je
// zojuist had gedaan. Dat was geen vergeten regel maar een gat in de meting: de app hield nergens
// bij wat er op een dag aan je woorden veranderde. st.box gaat omhoog en dat is alles; er is geen
// datum bij, dus na afloop is niet te zeggen welke woorden vandaag zijn opgeschoven.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ELKE WEG OMHOOG ZET DE DATUM. Drie plekken laten een doos stijgen: srsOmhoog (woordtrainer
//      en Aventura), wCheckAntwoord (de Laatste stap) en spelSrsBij (de spellen). Vergeet er één de
//      datum, dan telt het scherm te weinig en merk je dat nooit.
//   2. EEN BEURT DIE NIETS VERSCHUIFT ZET HEM NIET. Tegen het plafond aanlopen is geen vooruitgang.
//   3. DE GETALLEN KLOPPEN. Omhoog, gered, nieuw, en de trede van de zinnenladder.
//   4. "VAST" IS EEN GEBEURTENIS, GEEN TELLER. Een woord dat vandaag stevig werd staat er met naam;
//      "bewezen vast" als getal staat er niet, want dat beweegt na één les bijna nooit.
//   5. GEEN LIJSTJE MET NULLEN. Verschoof er niets, dan staat er niets.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door st.od overal en altijd te zetten: dan telt punt 1 en 3 en
// staat er elke dag hetzelfde. Daarom staat punt 2 ertegenover, en wordt gemeten dat een woord van
// gisteren NIET meetelt.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwVer' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    const t = today(), gisteren = addDays(t, -1);

    // ---- 1. elke weg omhoog zet de datum ----
    // srsOmhoog: de weg van de woordtrainer en van Aventura sinds v23.132
    const a = { box: 2, due: t, n: 9, f: 3 };
    srsOmhoog(a, 8);
    uit.srsOmhoog = a.od === t;
    // wCheckAntwoord: de Laatste stap. Via de echte functie, want de doos wordt daar rechtstreeks gezet.
    const w = WORDS[0];
    S.srs[w.id] = { box: stevigDrempel() - 1, due: t, n: 4 };
    wCur = w; wQueue = [w]; wCheck = { id: w.id, gekozen: null, goed: false };
    try { wCheckAntwoord(w.es); } catch (e) { uit.checkFout = e.message; }
    uit.wCheck = S.srs[w.id].od === t;
    uit.wCheckVast = (S.srs[w.id].box || 0) >= stevigDrempel() && !!S.srs[w.id].k;
    // spelSrsBij: de spellen
    const w2 = WORDS[1];
    S.srs[w2.id] = { box: 0, due: t };
    spelSrsBij(w2.id);
    uit.spel = S.srs[w2.id].od === t;

    // ---- 2. een beurt die niets verschuift zet hem niet ----
    const b = { box: 8, due: t, n: 9, f: 3 };
    srsOmhoog(b, 8);
    uit.plafond = b.od === undefined;
    const c = { box: SPEL_PLAFOND, due: t };
    S.srs['zzz-test'] = c;
    spelSrsBij('zzz-test');
    uit.spelPlafond = c.od === undefined;
    delete S.srs['zzz-test'];

    // ---- 3. de getallen kloppen ----
    S.srs = {};
    S.mijn = {};
    S.newIntro = {}; S.newIntro[t] = 4;
    WORDS.slice(0, 5).forEach(function (x, i) {
      S.srs[x.id] = { box: 3, due: t, n: 5, od: t, f: i < 2 ? 1 : 0 };   // 5 omhoog, 2 gered
    });
    WORDS.slice(5, 8).forEach(function (x) {
      S.srs[x.id] = { box: 3, due: t, n: 5, od: gisteren, f: 1 };        // van gisteren: telt niet
    });
    S.mijn['aceite'] = { es: 'el aceite', nl: 'olie', d: t };
    S.vert = { trede: 4, reeks: 0, d: t, dagStart: 3 };
    const d = dagVerschoven();
    uit.d = { omhoog: d.omhoog, gered: d.gered, nieuw: d.nieuw, uitLezen: d.uitLezen,
              voor: d.tredeVoor, na: d.tredeNa };
    uit.html = dagVerschovenHtml();

    // ---- 4. "vast" is een gebeurtenis ----
    S.srs[WORDS[0].id] = { box: stevigDrempel(), due: t, n: 7, od: t, k: 1 };
    uit.vast = dagVerschoven().vast;
    uit.vastHtml = dagVerschovenHtml();

    // ---- 5. geen lijstje met nullen ----
    S.srs = {}; S.mijn = {}; S.newIntro = {}; S.vert = { trede: 3, reeks: 0 };
    uit.leeg = dagVerschovenHtml();
    return uit;
  });

  console.log('\n-- 1. elke weg omhoog zet de datum --');
  ok(r.srsOmhoog, 'srsOmhoog (woordtrainer en Aventura)');
  ok(r.wCheck, 'wCheckAntwoord (de Laatste stap)' + (r.checkFout ? ' :: ' + r.checkFout : ''));
  ok(r.wCheckVast, 'en die zet het woord ook echt op stevig');
  ok(r.spel, 'spelSrsBij (de spellen)');

  console.log('\n-- 2. een beurt die niets verschuift zet hem niet --');
  ok(r.plafond, 'tegen het plafond aanlopen telt niet als vooruitgang');
  ok(r.spelPlafond, 'ook niet bij een spel');

  console.log('\n-- 3. de getallen kloppen --');
  console.log('   ' + JSON.stringify(r.d));
  ok(r.d.omhoog === 5, 'vijf kaartjes omhoog, en die van gisteren tellen niet mee (nu: ' + r.d.omhoog + ')');
  ok(r.d.gered === 2, 'twee gered: eerder fout, vandaag omhoog (nu: ' + r.d.gered + ')');
  ok(r.d.nieuw === 4, 'vier nieuw uit je dagportie (nu: ' + r.d.nieuw + ')');
  ok(r.d.uitLezen === 1, 'en één die je zelf aantikte tijdens het lezen (nu: ' + r.d.uitLezen + ')');
  ok(r.d.voor === 3 && r.d.na === 4, 'de ladder ging van 3 naar 4 (nu: ' + r.d.voor + ' -> ' + r.d.na + ')');
  ok(/kaartjes een doosje omhoog/.test(r.html), 'het staat ook echt op het scherm');
  ok(/aantikte tijdens het lezen/.test(r.html), 'met de leeswoorden apart benoemd');
  ok(/trede 4 van 6/.test(r.html), 'en de trede erbij');

  console.log('\n-- 4. "vast" is een gebeurtenis, geen teller --');
  ok(r.vast.length === 1, 'één woord werd vandaag vast (nu: ' + r.vast.length + ')');
  ok(r.vast[0] && r.vast[0].n === 7, 'met het aantal beurten erbij (nu: ' + (r.vast[0] || {}).n + ')');
  ok(/staat nu vast/.test(r.vastHtml), 'en dat staat er met naam en al');
  ok(!/bewezen vast/.test(r.vastHtml), 'de teller "bewezen vast" staat er niet: die beweegt na één les bijna nooit');

  console.log('\n-- 5. geen lijstje met nullen --');
  ok(r.leeg === '', 'verschoof er niets, dan staat er niets (nu: ' + JSON.stringify(r.leeg.slice(0, 40)) + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
