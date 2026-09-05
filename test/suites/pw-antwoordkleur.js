// pw-antwoordkleur.js (5 sep, v23.238) — zie je aan de knop of je het goed had?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 5 september, met een schermafbeelding van de leesvraag bij Los molinos de viento: "als ik
// het antwoord klik krijg ik geen rode en groene achtergrond (...) dit moet je even globaal
// oplossen."
//
// answerBoekVraag() zette classList.add("correct") en classList.add("wrong"), en had dat altijd
// gedaan. Alleen: v23.191 heeft die twee klassen hernoemd naar juist en jouw, en heeft het toetsje
// en de opfrisser omgebouwd. De leesvraag en de luistervraag niet. Die zetten sindsdien een klasse
// waar geen enkele CSS-regel bij hoort: geen foutmelding, geen kapotte knop, gewoon niets gebeurt.
//
// DE REDEN DAT DEZE SUITE DE KLEUR LEEST EN NIET DE KLASSE
//
// Een proef die controleert of de knop class="correct" krijgt, zou vier maanden groen hebben
// gestaan terwijl er niets te zien was. Daarom leest élke meting hieronder
// getComputedStyle().backgroundColor van de knop, na de klik, en vergelijkt die met de knop ernaast
// die je niet hebt aangeklikt. Een klasse zonder opmaak is geen terugkoppeling.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE LEESVRAAG. Precies het scherm uit Stefans schermafbeelding: het goede antwoord kleurt, en
//      als je fout klikt kleurt jouw knop anders dan het goede.
//   2. HET TOETSJE. Dat deed het al; hij staat erbij zodat een verbouwing van keuzeMarkeer() hem
//      niet stilletjes meesleept.
//   3. GROEN EN ROOD ZIJN NIET DEZELFDE KLEUR. Zonder dit haalt "kleur alles groen" proef 1 ook.
//   4. EN EEN NIET-AANGEKLIKTE KNOP BLIJFT ONGEKLEURD. Zonder dit haalt "kleur alles" alles.
//   5. NIEMAND SCHRIJFT NOG EEN KLASSENAAM OP. De acht schermen die een antwoord markeren doen dat
//      via keuzeMarkeer(); de dode namen (correct, wrong, opt good, opt bad) staan nergens meer.
//   6. DE NIVEAUTEST DOET MET OPZET NIET MEE. Die meet en onderwijst niet, en toont dus geen goed
//      antwoord. Dat staat hier vast zodat niemand hem er per ongeluk bij trekt.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwAk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1. de leesvraag: Stefans scherm ----
  console.log('\n-- 1. de leesvraag (Los molinos de viento) --');
  const lees = await page.evaluate(() => {
    function kleur(el) { return getComputedStyle(el).backgroundColor; }
    // een hoofdstuk met minstens drie opties, zodat er een knop overblijft die je niet aanraakt
    const h = BOOK.filter(function (x) {
      return x.vragen && x.vragen.length && vraagOpts(x.vragen[0]).length >= 3;
    })[0];
    if (!h) return { geen: true };
    startBoek(h.id);
    bState = { h: h, fase: 'vragen', i: 0, score: 0, locked: false };
    renderBoekVraag();
    const v = h.vragen[0];
    let opts = document.querySelectorAll('#lezenCard .opt');
    const voor = kleur(opts[0]);
    // met opzet FOUT klikken: een andere index dan het goede antwoord
    const mis = (v.c === 0) ? 1 : 0;
    const derde = [0, 1, 2].filter(function (i) { return i !== v.c && i !== mis; })[0];
    answerBoekVraag(mis, opts[mis]);
    opts = document.querySelectorAll('#lezenCard .opt');
    return { titel: h.titel, c: v.c, mis: mis, derde: derde,
             voor: voor,
             goedNa: kleur(opts[v.c]),
             jouwNa: kleur(opts[mis]),
             restNa: derde === undefined ? null : kleur(opts[derde]) };
  });
  console.log('   "' + lees.titel + '"  goed=' + lees.c + '  geklikt=' + lees.mis);
  console.log('   onbeantwoord ' + lees.voor);
  console.log('   goede knop   ' + lees.goedNa);
  console.log('   jouw knop    ' + lees.jouwNa);
  console.log('   derde knop   ' + lees.restNa);
  ok(!lees.geen, 'CONTROLE: er is een hoofdstuk met minstens drie opties om op te meten');
  ok(lees.goedNa !== lees.voor,
    'het goede antwoord krijgt een andere achtergrond dan een onbeantwoorde knop');
  ok(lees.jouwNa !== lees.voor, 'en jouw foute knop ook');
  ok(lees.goedNa !== lees.jouwNa,
    'CONTROLE: en het zijn twee verschillende kleuren, niet allebei groen');
  ok(lees.restNa === lees.voor,
    'CONTROLE: de knop die je niet aanraakte blijft kleurloos (anders kleurt hij gewoon alles)');

  // ---- 2. het toetsje, dat het al deed ----
  console.log('\n-- 2. het toetsje --');
  const toets = await page.evaluate(() => {
    function kleur(el) { return getComputedStyle(el).backgroundColor; }
    const qz = QUIZZES.filter(function (q) { return q.vragen && vraagOpts(q.vragen[0]).length >= 3; })[0];
    if (!qz) return { geen: true };
    startQuiz(qz.id);
    /* Binnen #qCard zoeken en niet in het hele document: de leesvraag van proef 1 staat nog in de
       DOM en heeft ook knoppen met class "opt". En het juiste antwoord komt uit qState en niet uit
       qz.vragen[0], want quizVraagVolgorde() schudt de vragen: welke vraag je ziet is niet
       noodzakelijk de eerste uit de lijst. Allebei zijn het meetfouten die deze proef groen konden
       laten staan over de verkeerde knoppen. */
    let opts = document.querySelectorAll('#qCard .opt');
    const v = qState.volgorde[qState.i].v;
    if (!opts.length) return { geen: true, reden: 'geen knoppen in #qCard' };
    const voor = kleur(opts[0]);
    const mis = (v.c === 0) ? 1 : 0;
    answerQuestion(mis, opts[mis]);
    opts = document.querySelectorAll('#qCard .opt');
    return { voor: voor, goedNa: kleur(opts[v.c]), jouwNa: kleur(opts[mis]),
             n: opts.length, c: v.c, mis: mis };
  });
  console.log('   ' + JSON.stringify(toets));
  ok(!toets.geen && toets.goedNa !== toets.voor && toets.jouwNa !== toets.voor,
    'het toetsje kleurt allebei de knoppen');
  ok(!toets.geen && toets.goedNa === lees.goedNa && toets.jouwNa === lees.jouwNa,
    'en met dezelfde kleuren als de leesvraag, want het is dezelfde vraag aan dezelfde lezer');

  // ---- 3 t/m 5. niemand schrijft nog een klassenaam op ----
  console.log('\n-- 5. één plek die de klassen kent --');
  const bron = await page.evaluate(() => {
    const t = document.documentElement.innerHTML;
    // het commentaar eruit: een controle die zijn eigen toelichting leest, controleert niets
    const kaal = t.replace(/\/\*[\s\S]*?\*\//g, '').split('\n').map(function (r) {
      return r.split('//')[0];
    }).join('\n');
    const dood = ['classList.add("correct")', 'classList.add("wrong")', '"opt good"', '"opt bad"']
      .filter(function (d) { return kaal.indexOf(d) !== -1; });
    const merkers = (kaal.match(/keuzeMarkeer\(/g) || []).length;
    return { dood: dood, merkers: merkers,
             heeftJuist: /\.juist\s*\{/.test(t), heeftJouw: /\.jouw\s*\{/.test(t) };
  });
  console.log('   keuzeMarkeer-aanroepen: ' + bron.merkers + ', dode namen: ' + (bron.dood.join(', ') || 'geen'));
  ok(bron.dood.length === 0, 'geen enkele plek schrijft nog een dode klassenaam op');
  ok(bron.merkers >= 5, 'en de markering loopt via één functie (' + bron.merkers + ' aanroepen)');
  ok(bron.heeftJuist && bron.heeftJouw,
    'CONTROLE: de twee klassen die overblijven hebben ook echt opmaak, want daar ging dit over');

  // ---- 6. de niveautest doet met opzet niet mee ----
  console.log('\n-- 6. de niveautest toont geen goed antwoord --');
  const niveau = await page.evaluate(() => {
    const bron = String(renderPlacement);
    return { markeert: bron.indexOf('keuzeMarkeer') !== -1,
             springtDoor: /pIdx\+\+/.test(bron) };
  });
  ok(niveau.markeert === false,
    'de niveautest kleurt niets: hij meet en onderwijst niet, dus er is geen goed antwoord te tonen');
  ok(niveau.springtDoor === true,
    'CONTROLE: hij gaat wel gewoon door naar de volgende vraag, dus dit is een keuze en geen gat');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
