// pw-markering.js (8 sep, v23.251) - wordt het goede antwoord echt groen, op élke antwoordknop?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 8 september: "de fout dat het goede antwoord groen moet (niet de balk eronder) is nog niet
// overal opgelost."
//
// Er stond al een proef op dit onderwerp (pw-antwoordkleur, v23.245) en die stond groen. Die meet of
// keuzeMerk/keuzeMarkeer wordt aangeroepen. Dat gebeurde ook: het scherm op zijn schermafbeelding
// zet de klasse gewoon. Alleen was hij onzichtbaar.
//
//     button.ghost{ background:var(--card); border:1.5px solid var(--border); }   (0,1,1)
//     .juist      { background:var(--green-soft); border-color:var(--green); }    (0,1,0)
//
// Element-plus-klasse wint van klasse, altijd, ongeacht de volgorde in het bestand. Op .opt-knoppen
// werkte het toevallig wel. En omdat een beantwoorde knop disabled is, zette button.ghost:disabled
// er ook nog opacity 0.5 overheen: het bleke grijs van zijn scherm.
//
//     Meet de uitkomst, niet het mechanisme. Anders bewaakt de proef je goede bedoeling.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE LIJST KOMT UIT DE BRON. Deze suite haalt index.html op en zoekt daarin élke knop waar een
//      antwoord op gemarkeerd wordt (een class= naast een data-attribuut dat de app als antwoord
//      leest). Geen handgeschreven lijst, dus een zesde antwoordscherm valt hier vanzelf onder.
//   2. PER KNOPKLASSE VERANDERT DE ECHTE KLEUR. Berekende achtergrond en rand, met en zonder de
//      markering, aan en uit. Niet de CSS-tekst: een regel die er staat maar verliest, is geen kleur.
//   3. EN HET CONTROLEGEVAL: een knop zonder markering verandert niet. Zonder dat zou "alles anders"
//      ook waar zijn als elke knop altijd groen was.
//   4. LIVE, OP HET SCHERM VAN ZIJN SCHERMAFBEELDING. De grammatica-microles echt beantwoorden en de
//      knop meten. De statische controle hierboven bewijst de cascade; deze bewijst dat het scherm
//      hem ook echt gebruikt.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwMk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1, 2 en 3: elke knopklasse waar een antwoord op gemarkeerd wordt ----
  console.log('\n-- 1. de klassen komen uit de bron van de app --');
  const meting = await page.evaluate(async (u) => {
    const bron = await (await fetch(u)).text();
    /* Elke knop die een antwoord DRAAGT, herkenbaar aan een data-attribuut dat de app als
       antwoordindex leest, plus de selectors die keuzeMarkeer meekrijgt. Uit de bron en niet uit
       mijn hoofd: dat is het verschil tussen "de vijf die ik ken" en "alle die er zijn". */
    const klassen = {};
    const voegToe = function (k) {
      const s = String(k || '').replace(/\s+/g, ' ').trim();
      if (s) klassen[s] = 1;
    };
    // class='...' op hetzelfde element als data-gwo / data-proef / data-ai / data-toefen / data-keuze
    const re = /class=['"]([^'"]*)['"][^>]{0,120}?data-(?:gwo|proef|ai|toefen|keuze)=/g;
    let m;
    while ((m = re.exec(bron)) !== null) voegToe(m[1]);
    // en andersom, want de volgorde van de attributen ligt niet vast
    const re2 = /data-(?:gwo|proef|ai|toefen|keuze)=[^>]{0,120}?class=['"]([^'"]*)['"]/g;
    while ((m = re2.exec(bron)) !== null) voegToe(m[1]);
    // klassen die met een variabele worden opgebouwd: pak de vaste kern die ervoor staat
    const re3 = /var klasse = "([^"]+)";\s*[\s\S]{0,200}?keuzeMerk\(/g;
    while ((m = re3.exec(bron)) !== null) voegToe(m[1]);

    const houder = document.createElement('div');
    houder.style.position = 'absolute'; houder.style.left = '-9999px';
    document.body.appendChild(houder);
    const meet = function (klas, uit) {
      const el = document.createElement('button');
      el.type = 'button';
      el.className = klas;
      el.textContent = 'x';
      if (uit) el.disabled = true;
      houder.appendChild(el);
      const c = getComputedStyle(el);
      return { bg: c.backgroundColor, rand: c.borderTopColor, op: +c.opacity };
    };
    const uit = Object.keys(klassen).map(function (basis) {
      // de opbouwvariabele zelf zit soms in de string; die telt niet mee als klasse
      const schoon = basis.replace(/"\s*\+\s*[^+]*\+\s*"/g, ' ').replace(/\s+/g, ' ').trim();
      const r = { basis: schoon };
      [false, true].forEach(function (uitgeschakeld) {
        const naam = uitgeschakeld ? 'uit' : 'aan';
        const kaal = meet(schoon, uitgeschakeld);
        const j = meet(schoon + ' juist', uitgeschakeld);
        const f = meet(schoon + ' jouw', uitgeschakeld);
        r[naam] = {
          kaalBg: kaal.bg,
          juistAnders: j.bg !== kaal.bg && j.rand !== kaal.rand,
          jouwAnders: f.bg !== kaal.bg && f.rand !== kaal.rand,
          juistBg: j.bg,
          zichtbaar: j.op >= 0.9 && f.op >= 0.9
        };
      });
      // het controlegeval: zonder markering verandert er niets
      const a = meet(schoon, false), b = meet(schoon, false);
      r.zelfdeZonder = a.bg === b.bg && a.rand === b.rand;
      return r;
    });
    houder.remove();
    return { klassen: Object.keys(klassen), uit: uit };
  }, U);

  meting.uit.forEach(function (r) {
    console.log('   ' + JSON.stringify(r.basis).padEnd(26) +
      ' aan: ' + (r.aan.juistAnders ? 'groen' : 'GEEN KLEUR') +
      '  uit: ' + (r.uit.juistAnders ? 'groen' : 'GEEN KLEUR') +
      (r.uit.zichtbaar ? '' : '  (halfdoorzichtig)'));
  });
  ok(meting.uit.length >= 3,
    'CONTROLE: er zijn minstens drie soorten antwoordknoppen gevonden in de bron (' + meting.uit.length + ')');
  ok(meting.uit.some(function (r) { return /ghost/.test(r.basis); }),
    'CONTROLE: en de knop van Stefans schermafbeelding zit erbij (ghost gw-optie)');
  ok(meting.uit.some(function (r) { return /\bopt\b/.test(r.basis); }),
    'CONTROLE: en die van het toetsje ook (opt)');

  console.log('\n-- 2. op elke soort verandert de echte kleur --');
  const geenKleur = meting.uit.filter(function (r) { return !r.aan.juistAnders || !r.aan.jouwAnders; });
  ok(geenKleur.length === 0,
    'elke antwoordknop wordt groen bij goed en rood bij fout (' +
      (geenKleur.map(function (r) { return r.basis; }).join(' | ') || 'geen uitzonderingen') + ')');
  const geenKleurUit = meting.uit.filter(function (r) { return !r.uit.juistAnders || !r.uit.jouwAnders; });
  ok(geenKleurUit.length === 0,
    'ook als de knop uitgeschakeld is, want dat is hij zodra je geantwoord hebt (' +
      (geenKleurUit.map(function (r) { return r.basis; }).join(' | ') || 'geen uitzonderingen') + ')');
  const bleek = meting.uit.filter(function (r) { return !r.uit.zichtbaar; });
  ok(bleek.length === 0,
    'en hij blijft ondoorzichtig, niet halfweg weggedimd (' +
      (bleek.map(function (r) { return r.basis; }).join(' | ') || 'geen uitzonderingen') + ')');

  console.log('\n-- 3. het controlegeval --');
  ok(meting.uit.every(function (r) { return r.zelfdeZonder; }),
    'twee keer dezelfde knop zonder markering geeft twee keer dezelfde kleur');

  // ---- 4. live: het scherm van de schermafbeelding ----
  console.log('\n-- 4. live in de grammatica-microles --');
  const live = await page.evaluate(async () => {
    /* het scherm dat Stefan fotografeerde: een conceptles met meerkeuzevragen. Gebouwd via de
       gewone weg (gwStart) zodat dit meet wat hij ziet en niet wat ik naboots. */
    const id = (gcLijst()[0] || {}).id || 'concept-genero';
    show('spiekbrief');
    gwStart(id);
    for (let n = 0; n < 12 && (!gwSess || gwSess.fase !== 'toets'); n++) {
      const knop = document.querySelector('#gwCard button.primary');
      if (!knop) break;
      knop.click();
    }
    if (!gwSess || gwSess.fase !== 'toets') return { geenToets: true, fase: gwSess ? gwSess.fase : null };
    const opties = Array.from(document.querySelectorAll('#gwOpties button'));
    if (opties.length < 2) return { geenOpties: opties.length };
    const q = gwVragen()[gwSess.vraag];
    if (!q) return { geenVraag: true };
    const juistIdx = q.g;
    const foutIdx = juistIdx === 0 ? 1 : 0;
    const voor = getComputedStyle(opties[juistIdx]).backgroundColor;
    opties[foutIdx].click();                       // met opzet fout, dan zijn er twee kleuren
    const na = Array.from(document.querySelectorAll('#gwOpties button')).map(function (b) {
      const c = getComputedStyle(b);
      return { klas: b.className, bg: c.backgroundColor, op: +c.opacity, uit: b.disabled };
    });
    return { juistIdx: juistIdx, foutIdx: foutIdx, voor: voor, na: na };
  });
  if (live.geenToets || live.geenOpties || live.geenVraag) {
    ok(false, 'CONTROLE: de microles komt niet bij zijn vragen (' + JSON.stringify(live) + ')');
  } else {
    live.na.forEach(function (b, i) {
      console.log('   knop ' + i + ': ' + b.bg + ' op' + b.op + (b.uit ? ' [uit]' : '') + '  ' + b.klas);
    });
    const juist = live.na[live.juistIdx], gekozen = live.na[live.foutIdx];
    ok(/juist/.test(juist.klas), 'CONTROLE: het juiste antwoord krijgt de klasse juist');
    ok(/jouw/.test(gekozen.klas), 'CONTROLE: en jouw misser de klasse jouw');
    ok(juist.bg !== live.voor, 'het juiste antwoord kleurt echt anders dan ervoor (' + juist.bg + ')');
    ok(juist.bg !== gekozen.bg, 'en groen en rood zijn niet dezelfde kleur (' + juist.bg + ' vs ' + gekozen.bg + ')');
    ok(juist.op >= 0.9 && gekozen.op >= 0.9,
      'allebei volledig zichtbaar terwijl de knop uitgeschakeld is (' + juist.op + ', ' + gekozen.op + ')');
  }

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
