// pw-boekuit.js (21 aug, v23.162) — werkt de voorspeller, staat elk boek op de plank, en is uit ook uit?
//
// WAAROM DIT ER IS
//
// Stefan, 21 aug, drie dingen op een rij: "de voortgang voorspeller werkt nog niet. het nieuwe boek
// is er niet. en ik had al een keer eerder gezegd dat als een boek uit is, het een feestje moet
// voelen. Dat is nu ook niet zo."
//
// Alle drie waar, en alle drie iets anders dan ik dacht.
//
// DE VOORSPELLER. tempoMeting() eindigde met `weken: ws.length`, en er is geen ws in die functie.
// JavaScript pakte de globale ws van de woordenzoeker (var ws = null, twaalfduizend regels
// verderop). Nooit gewoordenzoekerd is dus een TypeError, en daarmee klapt tempoMeting én alles wat
// eraan hangt: voortgangBand, voorspelWaar, voorspelHtml. Nagemeten met vier weekmetingen:
// "Cannot read properties of null (reading 'length')", vier keer.
//
// Het gemene is waaróm dit maanden bleef staan. Elke aanroeper vangt fouten af, want "een meter mag
// de app nooit omver duwen". Op het scherm ziet een kapotte voorspeller er dus precies zo uit als
// een voorspeller die zwijgt omdat er nog te weinig weken zijn. Twee heel verschillende toestanden,
// één beeld.
//
// HET BOEK. De plank wordt gebouwd uit LEES_REEKSEN en pakt hoofdstukken op id-voorvoegsel. De acht
// Cádiz-hoofdstukken uit v23.157 heten cadiz-1 tot cadiz-8 en er was geen reeks met pre:"cadiz-".
// Ze stonden wél in BOOK en telden wél mee in je leesvoortgang. Mijn eigen suite pw-nieuwestof riep
// startBoek('cadiz-1') rechtstreeks aan en zag een boek dat prima rendert; via de voordeur bestond
// het niet.
//
// HET FEESTJE. finishBoek() vierde een hoofdstuk en verder niets. Het laatste hoofdstuk van acht
// gaf dezelfde toast als het derde.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE VOORSPELLER REKENT, EN GOOIT NIET. Met genoeg weken komt er een getal uit, en de functies
//      die eraan hangen doen het ook. Dit is de eis die er niet was: niet "hij zegt iets" maar "hij
//      valt niet om", want omvallen zag eruit als zwijgen.
//   2. EN ZWIJGT ALS HET MOET. Het controlegeval: onder de drie weekmetingen in dezelfde maat is
//      elk tempo toeval, en dan hoort er niets te staan. Zwijgen en omvallen mogen niet allebei
//      "geen voorspelling" opleveren.
//   3. ELK BOEK IN BOOK IS VIA DE PLANK TE BEREIKEN. Niet alleen het nieuwe: elk hoofdstuk moet bij
//      een reeks horen. Dit is de regel die het volgende boek redt.
//   4. EEN BOEK UIT KRIJGT ZIJN EIGEN SCHERM, met getallen die uit de data komen.
//   5. ÉÉN KEER. Het controlegeval: nog eens lezen viert niet opnieuw, want dan is het geen moment
//      maar een animatie.
//   6. EN HET BLIJFT STAAN OP DE PLANK. Een feestje dat je volgende week niet meer kunt terugvinden
//      was geen feestje.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwBu' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    // ---- 1 en 2. de voorspeller ----
    function meet(weken) {
      const m = {};
      const basis = new Date('2026-07-27').getTime();
      for (let i = 0; i < weken; i++) {
        const d = new Date(basis + i * 604800000).toISOString().slice(0, 10);
        m[d] = { d: d, dekw: { A1: 120 + i * 30, A2: 60 + i * 17 } };
      }
      S.meting = m;
    }
    function probeer(fn) {
      try { return { uit: fn() }; } catch (e) { return { fout: e.message }; }
    }
    meet(4);
    uit.vier = {
      tempo: probeer(function () { return tempoMeting('A1'); }),
      band: probeer(function () { return voortgangBand('A1'); }),
      waar: probeer(function () { return voorspelWaar('A1', 13); }),
      html: probeer(function () { return voorspelHtml().replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim(); })
    };
    // het controlegeval: twee metingen is geen tempo
    meet(2);
    uit.twee = {
      tempo: probeer(function () { return tempoMeting('A1'); }),
      html: probeer(function () { return voorspelHtml().replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim(); })
    };
    // en helemaal niets gemeten mag ook niet omvallen
    S.meting = {};
    uit.nul = probeer(function () { return tempoMeting('A1'); });
    meet(4);

    // ---- 3. elk boek is via de plank te bereiken ----
    uit.zonderReeks = BOOK.filter(function (h) { return !leesReeksVan(h); }).map(function (h) { return h.id; });
    leesReeks = null;
    show('lezen', true); renderBoekMenu();
    const menu = document.getElementById('lezenMenu');
    uit.planken = [].slice.call(menu.querySelectorAll('button[data-reeks]')).map(function (b) { return b.getAttribute('data-reeks'); });
    uit.reeksen = LEES_REEKSEN.map(function (x) { return x.id; });
    /* Elke plank moet ook echt hoofdstukken hebben: een reeks met een voorvoegsel dat nergens op
       past is een lege kaart, en dat is de spiegelbeeldfout van een boek zonder plank. */
    uit.legeReeks = LEES_REEKSEN.filter(function (x) { return boekReeksHst(x).length === 0; }).map(function (x) { return x.id; });
    /* v23.182: hier stond "cadiz" bij naam. Un año en Cádiz is eruit gegaan (geen tweede vak, zie
       het projectdoc "De leesregel") en toen viel deze suite om op een reeks die niet meer bestaat.
       Een suite die één reeks bij naam noemt bewaakt alleen de reeks die toevallig de laatste was
       toen hij geschreven werd. Nu: elke reeks staat met zijn naam op de plank. */
    uit.naamOntbreekt = LEES_REEKSEN.filter(function (x) {
      return menu.textContent.indexOf(ct(x.nl, x.en)) === -1;
    }).map(function (x) { return x.id; });

    // ---- 4, 5 en 6. een boek uit ----
    S.lessons = S.lessons || {};
    (tLessons() || []).forEach(function (l) {
      S.lessons[l.id] = { done: true, woorden: true, zinnen: true, quiz: true, spiek: true };
    });
    /* v23.182: was 'cadiz'. Nu de langste reeks die je met alle lessen af helemaal open hebt: dat is
       de zwaarste proef voor "een boek uit", en hij blijft kloppen als er reeksen bij komen. */
    const reeks = LEES_REEKSEN.slice().sort(function (a, b) {
      return boekReeksHst(b).length - boekReeksHst(a).length;
    })[0];
    const hst = boekReeksHst(reeks);
    S.boek = {}; S.boekUit = {}; S.tapas = 0;
    hst.slice(0, hst.length - 1).forEach(function (h) {
      S.boek[h.id] = { done: true, score: 3, reflectie: '', d: '2026-08-01' };
    });
    const laatste = hst[hst.length - 1];
    uit.halfAf = { reeksAf: boekReeksAf(reeks), gevierd: !!S.boekUit[reeks.id] };

    function rondAf(h) {
      bState = { h: h, fase: 'preguntas', i: h.vragen.length, score: h.vragen.length, locked: false };
      document.getElementById('lezenCard').classList.remove('hidden');
      document.getElementById('lezenCard').innerHTML = "<textarea id='boekReflectieInput'></textarea>";
      finishBoek();
    }
    const tapasVoor = S.tapas;
    rondAf(laatste);
    uit.uit = {
      gevierd: S.boekUit[reeks.id] || null,
      scherm: (document.getElementById('lezenCard').textContent || '').replace(/\s+/g, ' ').trim(),
      knop: !!document.getElementById('btnBoekUitDoor'),
      tapasErbij: S.tapas - tapasVoor,
      cijfers: boekReeksCijfers(reeks)
    };
    // 6. het blijft op de plank staan
    if (document.getElementById('btnBoekUitDoor')) document.getElementById('btnBoekUitDoor').click();
    leesReeks = null; renderBoekMenu();
    uit.plankNa = document.getElementById('lezenMenu').textContent.indexOf('Uitgelezen') !== -1;
    // 5. het controlegeval: nog eens lezen viert niet opnieuw
    const tapas2 = S.tapas;
    rondAf(laatste);
    uit.herlezen = { scherm: !!document.getElementById('btnBoekUitDoor'), tapasErbij: S.tapas - tapas2 };

    return uit;
  });

  console.log('\n-- 1. de voorspeller rekent, en gooit niet --');
  ['tempo', 'band', 'waar', 'html'].forEach(function (k) {
    ok(!r.vier[k].fout, k + '() valt niet om' + (r.vier[k].fout ? ': ' + r.vier[k].fout : ''));
  });
  ok(r.vier.tempo.uit && r.vier.tempo.uit.weken === 4,
    'en telt de weken die er zijn (' + (r.vier.tempo.uit || {}).weken + ', niet undefined of de woordenzoeker)');
  ok(r.vier.tempo.uit && r.vier.tempo.uit.gem > 0, 'met een tempo per week (' + (r.vier.tempo.uit || {}).gem + ')');
  ok(r.vier.band.uit && r.vier.band.uit.onder > 0, 'de band geeft een ondergrens in weken (' + (r.vier.band.uit || {}).onder + ')');
  ok(r.vier.html.uit && r.vier.html.uit.length > 40, 'en er staat een voorspelling op het scherm');
  console.log('   "' + String((r.vier.html.uit || '')).slice(0, 130) + '"');

  console.log('\n-- 2. het controlegeval: en hij zwijgt als het moet --');
  ok(!r.twee.tempo.fout, 'met twee metingen valt hij ook niet om');
  ok(r.twee.tempo.uit === null, 'maar rekent hij niets uit: met twee punten is elk tempo toeval');
  ok(!r.nul.fout && r.nul.uit === null, 'en zonder metingen ook niet');

  console.log('\n-- 3. elk boek is via de plank te bereiken --');
  console.log('   planken: ' + r.planken.join(', '));
  ok(r.zonderReeks.length === 0,
    'elk hoofdstuk in BOOK hoort bij een plank (' + (r.zonderReeks.slice(0, 8).join(', ') || 'alle') + ')');
  ok(r.legeReeks.length === 0, 'en elke plank heeft hoofdstukken (' + (r.legeReeks.join(', ') || 'alle') + ')');
  ok(r.planken.length === r.reeksen.length, 'alle ' + r.reeksen.length + ' planken staan op het scherm (' + r.planken.length + ')');
  ok(r.naamOntbreekt.length === 0,
    'en elke reeks staat met zijn naam op de plank (mist: ' + (r.naamOntbreekt.join(', ') || 'geen') + ')');

  console.log('\n-- 4. een boek uit krijgt zijn eigen scherm --');
  ok(!r.halfAf.reeksAf && !r.halfAf.gevierd, 'op één hoofdstuk na is nog geen boek uit');
  ok(!!r.uit.gevierd, 'na het laatste hoofdstuk staat het boek als uitgelezen genoteerd (' + r.uit.gevierd + ')');
  ok(r.uit.knop, 'en er is een eigen scherm, geen toast die wegvalt terwijl je hem leest');
  console.log('   "' + r.uit.scherm.slice(0, 150) + '"');
  ok(/hoofdstukken/.test(r.uit.scherm) && /woorden/.test(r.uit.scherm), 'met wat je gedaan hebt erin');
  ok(r.uit.cijfers.woorden > 500, 'en die getallen komen uit de data (' + r.uit.cijfers.woorden + ' woorden)');
  ok(/dagen/.test(r.uit.scherm), 'inclusief hoeveel dagen je erover deed');
  ok(r.uit.tapasErbij >= 10, 'een boek uit is meer waard dan een hoofdstuk (+' + r.uit.tapasErbij + ' tapas)');

  console.log('\n-- 5 en 6. één keer, en het blijft staan --');
  ok(r.plankNa, 'de plank laat zien dat dit boek uit is');
  ok(!r.herlezen.scherm, 'het controlegeval: nog eens lezen geeft geen tweede feestje');
  ok(r.herlezen.tapasErbij < 10, 'en geen tweede bonus (+' + r.herlezen.tapasErbij + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
