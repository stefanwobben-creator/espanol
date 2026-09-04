// pw-tredes.js (4 sep, v23.236) — kan een goed antwoord het rood uitzetten, en sta je op de goede trede?
//
// (De naam: pw-ladder.js bestaat al en gaat over de herhaalladder van de woorden. Dit gaat over de
// tredes van de conjugatieladder. Vierde naambotsing in dit project, en de vorige drie hebben elk
// een halve avond gekost.)
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 4 sep: "ik heb net el la gedaan weer goed en die blijft zeggen fout gegaan, ik zie ook
// niet de voortgang en de oefening met alle tijden bij grammatica staat er nog maar die is veel te
// moeilijk want ik moet alle tijden van alle werkwoorden herkennen terwijl ik net tegenwoordige tijd
// ken (...) die grote wijzigingen om me te helpen met grammatica blijven maar uit."
//
// TWEE OORZAKEN, GEMETEN
//
// 1. gcStaatFout() las "box 0 en st.laatst binnen twee dagen". st.laatst wordt alleen bij een FOUT
//    geschreven, maar gramLees() haalt de doos uit het ZWAKSTE doosje en de datum uit het MEEST
//    RECENTE. Twee rijen, één toestand. Gevolg: een misser van eergisteren zette het rood aan en
//    geen enkel goed antwoord kon het uitzetten. Alleen wachten hielp.
//
// 2. conjOpenInit() gaf iedereen met ook maar één conj:-fout de laatste trede van de ladder, en
//    conjFaseNu() kiest de hoogste die openstaat. In Stefans foutenboek staan 42 conj:-sleutels
//    (gemeten in tools/logs-latest.json), dus hij stond op trede 13, "alles door elkaar". Datzelfde
//    getal voedt conjOpenTijden() en dus de rijen van het vormenblok in zijn dagles.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. EEN GOEDE DAG ZET HET ROOD UIT, met het controlegeval ernaast (gisteren fout, vandaag niets
//      gedaan) want anders haalt "altijd groen" deze proef ook.
//   2. EEN MISSER VANDAAG BLIJFT STAAN: het rode woord en de doos hanteren dezelfde maat.
//   3. EEN OUDE FOUT IS GEEN BERICHT.
//   4. HET OORDEEL LEEST HET LEDGER EN NIET DE LAATST-DATUM. Dit is de proef die vóór v23.236 rood
//      stond: st.laatst op gisteren, ledger vandaag schoon.
//   5. DE LADDER BEGINT NIET OP DE EINDSTAND. Gebouwd: Stefans toestand, 42 conj:-fouten.
//   6. EN DE DAGLES VOLGT: geen enkele rij in een andere tijd. De klacht zelf, als proef.
//   7. DE MIGRATIE ZET ALLEEN OMLAAG, EN NOOIT LAGER DAN HET HELE PRESENTE.
//   8. WIE HEM AANTOONBAAR AF HEEFT BLIJFT STAAN. Zonder dit controlegeval zou "zet iedereen terug"
//      proef 7 ook halen.
//   9. DE MIGRATIE DRAAIT ZICHZELF ÉÉN KEER. Vóór v23.236 sprong wie op imperfreg stond bij de
//      volgende bump naar perfecto: twee tijden cadeau.
//  10. ER WORDT NIETS AFGEPAKT. De knop "Ik kan dit al" opent precies één trede.
//  11. DE KAART ZEGT WAAR JE STAAT, en welke tijden nog dicht zijn.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTr' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {} });
  await page.waitForTimeout(400);

  // ---- 1 t/m 4. kan een goed antwoord het rood uitzetten? ----
  console.log('\n-- 1 t/m 4. het oordeel "fout gegaan" --');
  const rood = await page.evaluate(() => {
    const cid = 'genero';
    // precies de vorm die de klacht maakte: de kale sleutel staat op doos 0 en komt daar niet
    // vanaf, en st.laatst draagt de datum van de laatste misser
    function zet(laatst, log) {
      S.gram = {}; S.gramLog = {};
      S.gram[cid] = { box: 0, due: today(), goed: 40, fout: 12, laatst: laatst };
      Object.keys(log || {}).forEach(function (d) {
        S.gramLog[d] = {}; S.gramLog[d][cid] = log[d];
      });
      return { fout: gcStaatFout(gramLees(cid), cid),
               html: gcStatusHtml(cid).replace(/<[^>]*>/g, '') };
    }
    const g = addDays(today(), -1), t = today(), oud = addDays(today(), -9);
    const uit = {};
    uit.hersteld = zet(g, (function () { const o = {}; o[g] = { n: 4, goed: 2 }; o[t] = { n: 6, goed: 6 }; return o; })());
    uit.nietsGedaan = zet(g, (function () { const o = {}; o[g] = { n: 4, goed: 2 }; return o; })());
    uit.versMis = zet(t, (function () { const o = {}; o[t] = { n: 6, goed: 5 }; return o; })());
    uit.oud = zet(oud, (function () { const o = {}; o[oud] = { n: 4, goed: 0 }; return o; })());
    uit.ledgerWint = zet(g, (function () { const o = {}; o[t] = { n: 3, goed: 3 }; return o; })());
    return uit;
  });
  Object.keys(rood).forEach(function (k) {
    console.log('   ' + k.padEnd(13) + (rood[k].fout ? 'FOUT GEGAAN' : 'schoon').padEnd(13) + '"' + rood[k].html + '"');
  });
  ok(rood.hersteld.fout === false,
    'gisteren fout, vandaag alles goed: het rood is weg');
  ok(/doos/.test(rood.hersteld.html),
    'en de doos staat er weer, dus je ziet waar je staat ("' + rood.hersteld.html + '")');
  ok(rood.nietsGedaan.fout === true,
    'CONTROLE: gisteren fout en vandaag niets gedaan, dan staat het er nog (anders is elk oordeel groen)');
  ok(rood.versMis.fout === true,
    'een misser van vandaag blijft staan: dezelfde maat als de doos hanteert');
  ok(rood.oud.fout === false,
    'CONTROLE: een fout van negen dagen terug is geen bericht');
  ok(rood.ledgerWint.fout === false,
    'het ledger beslist en niet st.laatst: dit is de proef die vóór v23.236 rood stond');

  // ---- 5 en 6. waar zet de ladder je neer ----
  console.log('\n-- 5 en 6. de ladder begint niet op de eindstand --');
  const ladder = await page.evaluate(() => {
    // Stefans gemeten toestand: 42 conj:-sleutels in het foutenboek, geen eigen keuze gemaakt
    S.errors = S.errors || {};
    for (let i = 0; i < 42; i++) S.errors['conj:proef' + i] = { type: 'conj', count: 1 };
    delete S.conjOpen; delete S.conjFase; delete S.conjLadder; delete S.conjKlim;
    const open = conjOpenMax();
    const nu = conjFaseNu();
    const tijden = conjOpenTijden();
    const rijen = lesRijIds();
    return { open: open, top: CONJ_FASES.length - 1,
             faseId: nu.id, faseNr: conjFaseIdx(nu.id) + 1, aantal: CONJ_FASES.length,
             tijden: tijden, rijen: rijen,
             rijTijden: rijen.map(function (r) { const x = lesRij(r); return x ? x.t : null; })
               .filter(function (v, i, a) { return v && a.indexOf(v) === i; }) };
  });
  console.log('   trede ' + ladder.faseNr + '/' + ladder.aantal + ' (' + ladder.faseId + ')');
  console.log('   open tijden: ' + ladder.tijden.join(', '));
  console.log('   tijden in het vormenblok: ' + ladder.rijTijden.join(', '));
  ok(ladder.open !== ladder.top,
    'met 42 conj:-fouten sta je niet op de bovenste trede (' + (ladder.open + 1) + ' van ' + (ladder.top + 1) + ')');
  ok(ladder.faseId === 'presente',
    'maar op "het hele presente", precies waar Stefan zegt dat hij staat');
  ok(ladder.tijden.length === 1 && ladder.tijden[0] === 'presente',
    'en dan geeft conjOpenTijden() alleen het presente (' + ladder.tijden.join(', ') + ')');
  ok(ladder.rijTijden.length === 1 && ladder.rijTijden[0] === 'presente',
    'dus je vormenblok bouwt geen enkele rij in een andere tijd: de klacht zelf, als proef');
  ok(ladder.rijen.length > 1,
    'CONTROLE: er zijn wel gewoon rijen te oefenen, de les is niet leeg (' + ladder.rijen.length + ')');

  // ---- 7 t/m 9. de migratie ----
  console.log('\n-- 7 t/m 9. de migratie zet alleen omlaag, en één keer --');
  const mig = await page.evaluate(() => {
    const p = conjFaseIdx('presente');
    function draai(start, opts) {
      S.conjOpen = start;
      S.conjFase = CONJ_FASES[start].id;
      S.conjLadder = 13;
      if (opts && opts.klim) S.conjKlim = 1; else delete S.conjKlim;
      S.conjLaatste = {};
      if (opts && opts.af) {
        const r = [];
        for (let i = 0; i < CONJ_ONTGRENDEL_N; i++) r.push(i < CONJ_ONTGRENDEL_GOED ? 1 : 0);
        S.conjLaatste['presente'] = r;
      }
      conjLadderMigratie();
      return S.conjOpen;
    }
    // twee keer draaien mag niets meer verschuiven
    S.conjOpen = conjFaseIdx('imperfreg'); S.conjFase = 'imperfreg';
    S.conjLadder = 13; S.conjKlim = 1; S.conjLaatste = {};
    conjLadderMigratie();
    const eenmaal = S.conjOpen;
    S.conjLadder = 13;            // alsof de migratie opnieuw langskomt
    conjLadderMigratie();
    const tweemaal = S.conjOpen;
    return {
      presenteIdx: p,
      top: CONJ_FASES.length - 1,
      cadeau: draai(CONJ_FASES.length - 1, {}),
      beginner: draai(0, {}),
      afgerond: draai(CONJ_FASES.length - 1, { af: true }),
      geklommen: draai(CONJ_FASES.length - 1, { klim: true }),
      imperfregIdx: conjFaseIdx('imperfreg'),
      eenmaal: eenmaal, tweemaal: tweemaal
    };
  });
  console.log('   cadeau 13 -> ' + (mig.cadeau + 1) + ' · beginner 1 -> ' + (mig.beginner + 1) +
              ' · afgerond 13 -> ' + (mig.afgerond + 1) + ' · geklommen 13 -> ' + (mig.geklommen + 1));
  ok(mig.cadeau === mig.presenteIdx,
    'een cadeau gekregen eindstand zakt naar het hele presente (trede ' + (mig.cadeau + 1) + ')');
  ok(mig.beginner === 0,
    'CONTROLE: een beginner op trede 1 wordt niet omhoog geduwd, de migratie gaat alleen omlaag');
  ok(mig.afgerond === mig.top,
    'CONTROLE: wie het presente aantoonbaar af heeft blijft staan (trede ' + (mig.afgerond + 1) + ')');
  ok(mig.geklommen === mig.top,
    'en wie zelf geklommen is wordt met rust gelaten (trede ' + (mig.geklommen + 1) + ')');
  ok(mig.eenmaal === mig.imperfregIdx && mig.tweemaal === mig.eenmaal,
    'twee keer draaien verschuift de trede niet (' + (mig.eenmaal + 1) + ' en dan ' + (mig.tweemaal + 1) + ')');

  // ---- 10. de handrem ----
  console.log('\n-- 10. er wordt niets afgepakt --');
  const knop = await page.evaluate(() => {
    delete S.conjKlim;
    S.conjOpen = conjFaseIdx('presente');
    S.conjFase = 'presente';
    S.conjLadder = 14;
    S.rvDrill = 1;              // dezelfde opstelling als pw-conjfase: de drill, niet het puzzelspel
    funView = 'conj';
    show('speeltuin');
    renderFun();
    const b = document.getElementById('btnCjOverslaan');
    const label = b ? (b.innerText || '').trim() : '';
    const voor = conjOpenMax();
    if (b) b.click();
    const na = conjOpenMax();
    // en op een trede die niet de bovenste open is, staat de knop er niet
    S.conjFase = 'presente';
    renderFun();
    const lager = !!document.getElementById('btnCjOverslaan');
    return { erIs: !!b, label: label, voor: voor, na: na,
             klim: S.conjKlim, lagerZichtbaar: lager };
  });
  console.log('   "' + knop.label + '" · trede ' + (knop.voor + 1) + ' -> ' + (knop.na + 1));
  ok(knop.erIs, 'er staat een knop om zelf een trede hoger te gaan');
  ok(knop.na === knop.voor + 1, 'en hij opent er precies één, niet de hele ladder');
  ok(knop.klim === 1, 'hij laat een spoor achter, zodat geen migratie je daarna nog terugzet');
  ok(!knop.lagerZichtbaar,
    'CONTROLE: op een trede die al open is staat hij er niet, want daar valt niets te openen');

  // ---- 11. de kaart zegt waar je staat ----
  console.log('\n-- 11. de tijdenkaart --');
  const kaart = await page.evaluate(() => {
    delete S.conjKlim;
    S.conjOpen = conjFaseIdx('presente'); S.conjFase = 'presente'; S.conjLadder = 14;
    tijdenOpen(); renderCheat();
    const el = document.getElementById('cheat');
    el.querySelectorAll('details').forEach(function (d) { d.open = true; });
    const regel = document.getElementById('tijdLadder');
    const tekst = (el.innerText || '');
    return { regel: regel ? (regel.innerText || '').replace(/\s+/g, ' ') : null,
             hier: tekst.indexOf('hier oefen je nu') !== -1,
             later: tekst.indexOf('komt later') !== -1,
             rijen: el.querySelectorAll('.tijdrij').length,
             tabel: /<table/i.test(el.innerHTML) };
  });
  console.log('   "' + (kaart.regel || 'NIET GEVONDEN') + '"');
  ok(!!kaart.regel, 'er staat een regel die zegt welke tijd vandaag jouw werk is');
  ok(!!kaart.regel && /nog dicht/.test(kaart.regel), 'en welke er nog dicht zitten');
  ok(kaart.hier, 'de tijd waar je staat is op de kaart gemerkt');
  ok(kaart.later, 'en de tijden die nog komen ook');
  ok(kaart.rijen === 6 && !kaart.tabel,
    'CONTROLE: de kaart heeft nog steeds zes rijen en geen vervoegingstabel');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
