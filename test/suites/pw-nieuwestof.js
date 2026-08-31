// pw-nieuwestof.js (21 aug, v23.157) — is er nog iets te lezen en te luisteren?
//
// WAAROM DIT ER IS
//
// Stefan: "ik ben door de boeken (muv recepten) en luisteroefeningen heen. Maak een nieuw boek voor
// me en ook luisteroefeningen."
//
// Dat is geen wens maar een blokkade. Het inputblok van de dagles (v23.140) put uit het boek en uit
// Escuchar; zijn die op, dan krimpt zijn les naar vier stappen en verdwijnt de draad waar Nation een
// kwart van de tijd voor reserveert. Nieuwe stof is dus niet "meer van hetzelfde" maar de reden dat
// het inputblok blijft bestaan.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE STOF IS ER, EN HIJ IS COMPLEET. Losse content is makkelijk half toe te voegen: een scene
//      zonder Engelse vertaling, een hoofdstuk zonder vragen. Dit loopt elk veld langs dat de app
//      leest, voor álle stof, dus ook voor wat er morgen bij komt.
//   2. HET IS OOK ECHT TE BEREIKEN. Een drempel die hoger ligt dan het aantal lessen dat bestaat, is
//      stof die niemand ooit ziet. Dit is precies de fout die ik in deze ronde eerst maakte
//      (drempel 12 bij elf lessen).
//   3. HET RENDERT. Niet alleen in de data, maar op het scherm, zonder paginafouten.
//   4. EN HET INPUTBLOK VINDT HET. Dat is waar het om begonnen was.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door alleen de nieuwe stof te controleren. Daarom loopt punt 1 over
// ALLE hoofdstukken en scenes: als iemand morgen iets toevoegt zonder Engelse vertaling, valt hij om.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwNs' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    // ---- 1. de stof is compleet, en dit loopt over ALLES ----
    uit.scenes = AUDICIONES.length;
    uit.scenesStuk = AUDICIONES.filter(function (s) {
      if (!s.id || !s.titel || !s.titelEn || !s.nivel) return true;
      if (!s.lineas || s.lineas.length < 2) return true;
      if (s.lineas.some(function (l) { return !l.v || !l.es; })) return true;
      if (!s.vragen || s.vragen.length < 3) return true;
      return s.vragen.some(function (v) {
        return !v.q || !v.qEn || !v.opts || !v.optsEn ||
               v.opts.length !== v.optsEn.length || typeof v.c !== 'number' ||
               v.c < 0 || v.c >= v.opts.length || !v.waarom || !v.waaromEn;
      });
    }).map(function (s) { return s.id; });

    uit.hoofdstukken = BOOK.length;
    uit.boekStuk = BOOK.filter(function (h) {
      if (!h.id || !h.titel || !h.deel || typeof h.drempel !== 'number' || typeof h.num !== 'number') return true;
      if (!h.tekst || h.tekst.split(/\s+/).length < 60) return true;
      if (!h.vragen || h.vragen.length < 3) return true;
      return h.vragen.some(function (v) {
        return !v.q || !v.opts || v.opts.length < 2 || typeof v.c !== 'number' || v.c < 0 || v.c >= v.opts.length;
      });
    }).map(function (h) { return h.id; });

    const ids = BOOK.map(function (h) { return h.id; }).concat(AUDICIONES.map(function (s) { return s.id; }));
    uit.dubbel = ids.filter(function (x, i) { return ids.indexOf(x) !== i; });

    // ---- 2. het is ook echt te bereiken ----
    S.lessons = S.lessons || {};
    (tLessons() || []).forEach(function (l) {
      S.lessons[l.id] = { done: true, woorden: true, zinnen: true, quiz: true, spiek: true };
    });
    uit.lessenTotaal = doneLessonCount();
    uit.teHoog = BOOK.filter(function (h) { return h.drempel > uit.lessenTotaal; }).map(function (h) { return h.id; });
    /* v23.182: hier stond "cadiz". Un año en Cádiz is eruit gegaan, en een suite die één reeks bij
       naam noemt meet alleen de reeks die toevallig de laatste was toen hij geschreven werd. Nu per
       reeks op de plank, zodat de volgende reeks er automatisch onder valt. */
    uit.perReeks = LEES_REEKSEN.map(function (r) {
      var hs = BOOK.filter(function (h) { return String(h.id).indexOf(r.pre) === 0; });
      return { id: r.id, n: hs.length,
               open: hs.filter(boekOntgrendeld).length,
               eerste: hs.length ? hs[0].id : null };
    });

    // ---- 3. het rendert ----
    show('lezen', true);
    /* Elke reeks één keer openen. Een reeks die niet rendert is onbereikbaar, en dat merk je anders
       pas als je hem wilt lezen. */
    uit.rendert = uit.perReeks.map(function (r) {
      if (!r.eerste) return { id: r.id, n: 0 };
      startBoek(r.eerste);
      var t = (document.getElementById('lezenCard') || {}).textContent || '';
      closeBoek();
      return { id: r.id, n: t.length };
    });
    show('lezen', true);
    startBoek(uit.perReeks[0].eerste);
    uit.leesTekst = (document.getElementById('lezenCard') || {}).textContent || '';
    closeBoek();
    audSc = AUDICIONES.filter(function (s) { return s.id === 'e19'; })[0];
    audMenu = false; funView = 'audi';
    show('speeltuin', true); renderFun();
    uit.audTekst = document.getElementById('funCard').textContent || '';

    // ---- 4. en het inputblok vindt het ----
    S.dagen = { count: 5 };
    uit.boekHoofdstuk = (function () { try { const h = lesFlowBoekHoofdstuk(); return h ? h.id : null; } catch (e) { return 'FOUT'; } })();
    uit.audOpen = (function () { try { return audLijst().length; } catch (e) { return -1; } })();
    uit.inputKeuze = (function () { try { return lesFlowInputKeuze(); } catch (e) { return 'FOUT'; } })();
    return uit;
  });

  console.log('\n-- 1. de stof is compleet --');
  console.log('   ' + r.hoofdstukken + ' hoofdstukken, ' + r.scenes + ' luisterscenes');
  ok(r.scenesStuk.length === 0, 'elke luisterscene heeft regels, drie vragen en een Engelse versie (' + (r.scenesStuk.join(',') || 'alle') + ')');
  ok(r.boekStuk.length === 0, 'elk hoofdstuk heeft tekst, drie vragen en een juist antwoord (' + (r.boekStuk.join(',') || 'alle') + ')');
  ok(r.dubbel.length === 0, 'geen dubbele ids (' + (r.dubbel.join(',') || 'geen') + ')');

  console.log('\n-- 2. het is ook echt te bereiken --');
  console.log('   ' + r.lessenTotaal + ' lessen bestaan');
  r.perReeks.forEach(function (x) { console.log('   ' + x.id + ': ' + x.n + ' hoofdstukken, ' + x.open + ' open'); });
  ok(r.teHoog.length === 0, 'geen enkel hoofdstuk staat achter een drempel die niet te halen is (' + (r.teHoog.join(',') || 'geen') + ')');
  ok(r.perReeks.every(function (x) { return x.n > 0; }),
    'elke reeks op de plank heeft hoofdstukken (' + r.perReeks.filter(function (x) { return !x.n; }).map(function (x) { return x.id; }).join(',') + ')');
  ok(r.perReeks.every(function (x) { return x.open === x.n; }),
    'en wie alle lessen af heeft kan ze allemaal lezen');

  console.log('\n-- 3. het rendert --');
  console.log('   rendert: ' + r.rendert.map(function (x) { return x.id + ' ' + x.n; }).join(' · '));
  ok(r.rendert.every(function (x) { return x.n > 200; }),
    'elke reeks rendert een hoofdstuk met tekst (' + r.rendert.filter(function (x) { return x.n <= 200; }).map(function (x) { return x.id; }).join(',') + ')');
  ok(r.leesTekst.length > 400, 'met de tekst erin (' + r.leesTekst.length + ' tekens)');
  ok(/Escuchar/.test(r.audTekst), 'en de nieuwe scene op het luisterscherm');

  console.log('\n-- 4. en het inputblok vindt het --');
  ok(!!r.boekHoofdstuk, 'het leesblok van je les vindt een hoofdstuk (' + r.boekHoofdstuk + ')');
  ok(r.audOpen > 0, 'en het luisterblok vindt scenes (' + r.audOpen + ')');
  ok(['lezen', 'luisteren'].indexOf(r.inputKeuze) !== -1, 'dus het inputblok heeft iets te doen (' + r.inputKeuze + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
