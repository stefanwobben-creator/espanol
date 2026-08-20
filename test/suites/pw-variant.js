// pw-variant.js (20 aug, v23.137) — is jouw andere woord een fout of een vraag?
//
// WAAROM DIT ER IS
//
// Stefan, 20 aug: "of ik gebruik een alternatief woord wat goed is."
//
// Gemeten over de 231 zinnen: elke zin heeft alternatieven, gemiddeld 2,1. Maar het zijn allemaal
// accent- en cijfervarianten van dezelfde zin ("nació" / "nacio" / "1907" / "mil novecientos
// siete"). Er zit geen enkel synoniem tussen, en dat kan ook niet: je kunt geen lijst maken van
// alle goede manieren om een zin te zeggen. Een geldig alternatief woord werd dus per definitie
// fout gerekend.
//
// De check bestónd: /api/ai/check, met een knop "Is mijn variant ook goed?" onder een fout
// antwoord. Het probleem was de volgorde: fout rekenen, fout wegschrijven, ladder laten zakken, en
// dán mag je zelf vragen of je gelijk had.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HIJ VRAAGT UIT ZICHZELF. Bij een bijna-treffer gaat de vraag naar het model zonder dat je
//      een knop hoeft te vinden.
//   2. DE LADDER WACHT OP HET ANTWOORD. Zou hij alvast zakken, dan kost een geldige variant je een
//      trede en komt de correctie te laat.
//   3. JA = GOED. De fout gaat uit het logboek, de zin telt als gehaald, de ladder gaat omhoog.
//   4. NEE = FOUT. De fout blijft staan en de ladder zakt. Anders is dit geen check maar een
//      vrijbrief.
//   5. ONBEREIKBAAR = FOUT, MET EEN WEG TERUG. Geen model betekent het oude gedrag, en de knop komt
//      terug zodat je het later nog eens kunt vragen.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door bij élk fout antwoord te vragen: dan klopt punt 1 en 3 en is
// de app een modelaanroep per beurt kwijt. Daarom staat er tegenover punt 1 een meting die NIET mag
// bewegen: bij een antwoord dat er helemaal naast zit wordt er niet gevraagd, en zakt de ladder
// meteen.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwVar' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  const r = await page.evaluate(async () => {
    const uit = {};
    S.lang = 'nl';
    const echteApi = api;
    let gevraagd = [];
    function stub(antwoord) {
      api = function (pad, m, body) {
        // Alleen de modelaanroepen tellen. De app praat tijdens een beurt ook met /api/sync, en dat
        // is geen vraag over jouw zin.
        if (String(pad).indexOf('/api/ai/') === 0) gevraagd.push({ pad: pad, body: body });
        return Promise.resolve(antwoord);
      };
    }
    const wacht = () => new Promise(function (r) { setTimeout(r, 40); });

    // Een zin met minstens vier woorden, zodat één woord veranderen een bijna-treffer oplevert
    // (hoogstens twee anders én minstens de helft goed). Afgeleid, niet met de hand gekozen.
    const zin = SENTENCES.filter(function (z) { return String(z.es).split(/\s+/).length >= 5; })[0];
    uit.zin = zin.es;
    const bijna = zin.es.replace(/\S+\s*$/, 'zzzz');           // laatste woord vervangen
    const mis = 'qqq www eee rrr ttt';                          // er helemaal naast

    async function beurt(invoer, antwoord) {
      gevraagd = [];
      S.vert = { trede: 3, reeks: 0 };
      delete S.errors['zin:' + zin.id];
      delete S.done[zin.id];
      S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.zin = 'moeilijk';
      show('vertalen', true);
      sIdx = zin;
      renderSentence(false);
      zinGeteld = false; vertWacht = false;
      renderSentenceBody();
      stub(antwoord);
      document.getElementById('sInput').value = invoer;
      checkSentence();
      const direct = { reeks: S.vert.reeks, trede: S.vert.trede, wacht: vertWacht,
                       vraagt: !!document.getElementById('zinVraagt') };
      await wacht();
      return {
        direct: direct,
        gevraagd: gevraagd.slice(),
        reeks: S.vert.reeks, trede: S.vert.trede,
        foutEr: !!S.errors['zin:' + zin.id],
        gehaald: !!S.done[zin.id],
        knop: (function () { const b = document.getElementById('btnAiCheck'); return b && !b.classList.contains('hidden') && !b.disabled; })(),
        fb: (document.getElementById('sFeedback') || {}).textContent || ''
      };
    }

    uit.ja = await beurt(bijna, { ok: true, goed: true, uitleg: 'Ook goed, maar minder gewoon.' });
    uit.nee = await beurt(bijna, { ok: true, goed: false, uitleg: 'Nee, dat werkwoord kan hier niet.' });
    uit.stuk = await beurt(bijna, null);
    uit.mis = await beurt(mis, { ok: true, goed: true, uitleg: 'zou niet gevraagd moeten worden' });
    uit.goed = await beurt(zin.es, { ok: true, goed: true, uitleg: 'n.v.t.' });

    api = echteApi;
    return uit;
  });

  console.log('\n-- 1. hij vraagt uit zichzelf --');
  console.log('   zin: ' + r.zin);
  ok(r.ja.gevraagd.length === 1, 'één vraag aan het model bij een bijna-treffer (nu: ' + r.ja.gevraagd.length + ')');
  ok(r.ja.gevraagd[0] && r.ja.gevraagd[0].pad === '/api/ai/check', 'en hij gaat naar /api/ai/check');
  // v23.137: dit was de vondst van deze ronde. `rauw` werd gelezen ná zinInvoerDicht(), en die
  // vervangt de innerHTML van #sInvoer waar #sInput in zit. Het veld bestond op dat moment niet
  // meer, dus ging er altijd een leeg antwoord naar de server en die geeft daarop 400. De knop
  // was stuk zonder dat iemand het kon zien.
  ok(r.ja.gevraagd[0] && r.ja.gevraagd[0].body && !!r.ja.gevraagd[0].body.gegeven,
    'met wat je zelf hebt getypt erin, en niet leeg (nu: "' +
    ((r.ja.gevraagd[0] && r.ja.gevraagd[0].body && r.ja.gevraagd[0].body.gegeven) || '') + '")');
  ok(r.ja.direct.vraagt, 'op het scherm staat dat hij het navraagt');

  console.log('\n-- 2. de ladder wacht op het antwoord --');
  ok(r.ja.direct.wacht === true, 'meteen na het controleren staat de ladder in de wacht');
  ok(r.ja.direct.reeks === 0, 'en is er nog niets geteld (nu: ' + r.ja.direct.reeks + ')');

  console.log('\n-- 3. ja = goed --');
  ok(r.ja.reeks === 1, 'de ladder telt hem als goed (reeks nu: ' + r.ja.reeks + ')');
  ok(r.ja.foutEr === false, 'de fout is uit het logboek gehaald');
  ok(r.ja.gehaald === true, 'en de zin telt als gehaald');

  console.log('\n-- 4. nee = fout --');
  ok(r.nee.reeks === -1, 'de ladder telt hem als fout (reeks nu: ' + r.nee.reeks + ')');
  ok(r.nee.foutEr === true, 'en de fout blijft staan');

  console.log('\n-- 5. onbereikbaar = fout, met een weg terug --');
  ok(r.stuk.reeks === -1, 'zonder model gedraagt hij zich als fout (reeks nu: ' + r.stuk.reeks + ')');
  ok(r.stuk.foutEr === true, 'de fout blijft staan');
  ok(r.stuk.knop === true, 'en de knop komt terug om het later nog eens te vragen');

  console.log('\n-- 6. het controlegeval: niet bij elk fout antwoord --');
  ok(r.mis.gevraagd.length === 0, 'een antwoord dat er helemaal naast zit kost geen modelaanroep (nu: ' + r.mis.gevraagd.length + ')');
  ok(r.mis.direct.wacht === false, 'en de ladder wacht daar niet');
  ok(r.mis.reeks === -1, 'die zakt meteen (nu: ' + r.mis.reeks + ')');
  ok(r.goed.gevraagd.length === 0, 'een goed antwoord ook niet (nu: ' + r.goed.gevraagd.length + ')');
  ok(r.goed.reeks === 1, 'en telt meteen als goed (nu: ' + r.goed.reeks + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
