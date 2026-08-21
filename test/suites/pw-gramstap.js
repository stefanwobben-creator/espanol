// pw-gramstap.js (21 aug, v23.152) — begint de grammaticastap met Spaans of met een aankondiging?
//
// WAAROM DIT ER IS
//
// Stefan, na een echte doorloop: "Hier krijg je een grammatica vraag op van 2 van 3 zomaar en die
// lijkt uit het niets te komen."
//
// Wat er op dat scherm stond: een kicker met het onderwerp, "STAP 1/3", de titel "Probeer eens",
// een regel waarom dit onderwerp aan de beurt is, drie bolletjes, de zin "Eerst een voorbeeld, en
// gok gerust: het antwoord komt er meteen achteraan", en twee knoppen. Zes lagen, geen woord Spaans.
// De hele inhoud van dat scherm was: hier komt zo een vraag.
//
// De oorzaak: gcBouw() geeft stap 1 een uitleg die over de oefening gaat en niet over Spaans, en
// gwStapHeeftTekst() keek alleen of er tekst stond, niet waar die over ging.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE EERSTE STAP BEGINT MET DE VRAAG. Geen tussenscherm, geen "Toets me →" waar niets te
//      toetsen viel.
//   2. MAAR ER STAAT WEL IETS BIJ DIE EERSTE VRAAG. Anders komt de vraag alsnog uit het niets.
//      v23.158: dat was de gebruiksaanwijzing "gok gerust", en het is nu de regel zelf met de
//      ezelsbrug eronder. Wat er staat mag veranderen, dat er iets staat niet. Deze suite haalt de
//      tekst daarom op uit wat de stap draagt, niet uit een vaste zin.
//   3. EN ALLEEN DAAR. Bij vraag twee is hij weg; anders is het behang.
//   4. ECHTE UITLEG HOUDT WEL ZIJN SCHERM. Dit is het controlegeval: een stap met grammatica erin
//      hoort die grammatica te laten lezen vóór de vraag. Alles overslaan is net zo fout.
//   5. TWEE TELLERS DIE ALLEBEI "STAP" HETEN. "Stap klaar: 2/2" was je score, met "STAP 1/3"
//      erboven. Nu staat er wat het is.
//   6. EN DE DOOSJES HEBBEN EEN NAAM. Er stonden drie regels "undefined 0" op Voortgang, omdat
//      INTERVALS negen doosjes heeft en de labellijst er zes had.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwGst' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    // ---- 6. de doosjes hebben een naam ----
    uit.namen = intervalNamen();
    uit.dozen = INTERVALS.length;
    uit.geenUndefined = uit.namen.every(function (n) { return !!n && n !== 'undefined'; });
    show('voortgang', true); renderStats();
    const vg = document.getElementById('statsCard').textContent;
    uit.vgUndefined = (vg.match(/undefined/g) || []).length;

    // ---- 1 t/m 3. de eerste stap begint met de vraag ----
    // gcLijst() geeft al opgebouwde onderwerpen; hun id is "concept-xxx", dus niet nog eens prefixen
    const o = gcLijst()[0];
    const cid = o.id;
    uit.cid = cid;
    uit.stappen = o.stappen.length;
    uit.eersteProcedureel = !!o.stappen[0].procedureel;
    uit.heeftTekst0 = gwStapHeeftTekst(o, 0);

    gwStart(cid, 0);
    uit.fase = gwSess.fase;
    show('spiekbrief', true); renderCheat();
    const el = document.getElementById('cheat');
    uit.scherm1 = el.textContent.replace(/\s+/g, ' ');
    uit.heeftToetsMe = !!document.getElementById('gwNaarToets');
    uit.heeftOpties = el.querySelectorAll('#gwOpties button').length;
    /* v23.158: de tekst die bij vraag 1 hoort komt uit de stap zelf. Draagt hij hulp, dan is dat de
       kern van het onderwerp; zo niet, dan de oude gebruiksaanwijzing. Zo blijft deze suite meten
       dát er iets staat, ook als er morgen weer iets beters staat. */
    uit.uitlegZin = o.stappen[0].hulp
      ? gcHulpTekst(o.stappen[0].hulp, 'kern')
      : String(ct(o.stappen[0].uitleg, o.stappen[0].uitlegEn) || '').replace(/<[^>]*>/g, '');
    uit.zinBijVraag1 = uit.scherm1.indexOf(uit.uitlegZin.slice(0, 30)) !== -1;

    // vraag 2: dezelfde zin hoort er niet meer te staan
    gwSess.vraag = 1; gwSess.gekozen = null;
    renderCheat();
    uit.scherm2 = document.getElementById('cheat').textContent.replace(/\s+/g, ' ');
    uit.zinBijVraag2 = uit.scherm2.indexOf(uit.uitlegZin.slice(0, 30)) !== -1;

    // ---- 4. het controlegeval: echte uitleg houdt zijn scherm ----
    let echt = null;
    for (let i = 0; i < o.stappen.length && echt === null; i++) {
      const s = o.stappen[i];
      const t = String(ct(s.uitleg, s.uitlegEn) || '').replace(/<[^>]*>/g, '').trim();
      if (t && !s.procedureel) echt = i;
    }
    // en anders een handgeschreven wizard, die heeft altijd echte uitleg
    uit.echtIdx = echt;
    if (echt !== null) {
      gwStart(cid, echt);
      uit.echtFase = gwSess.fase;
    } else {
      const hw = (typeof CHEATSHEET !== 'undefined' && CHEATSHEET.length) ? gwSpiekId(0) : null;
      uit.hw = hw;
      if (hw) { gwStart(hw, 0); uit.echtFase = gwSess.fase; }
    }

    // ---- 5. twee tellers die allebei "stap" heetten ----
    gwStart(cid, 0);
    gwSess.fase = 'stapklaar';
    gwSess.goed = o.stappen[0].vragen.length;
    renderCheat();
    uit.klaar = document.getElementById('cheat').textContent.replace(/\s+/g, ' ');
    return uit;
  });

  console.log('\n-- 6. de doosjes hebben een naam --');
  console.log('   ' + r.namen.join(' · '));
  ok(r.namen.length === r.dozen, 'er is een naam per doosje (' + r.namen.length + ' bij ' + r.dozen + ')');
  ok(r.geenUndefined, 'en geen ervan is leeg');
  ok(r.vgUndefined === 0, 'op Voortgang staat geen "undefined" meer (' + r.vgUndefined + ')');

  console.log('\n-- 1 t/m 3. de eerste stap begint met de vraag --');
  console.log('   ' + r.scherm1.slice(0, 110));
  ok(r.eersteProcedureel, 'stap 1 is gemarkeerd als procedureel (hij krijgt geen eigen leesscherm)');
  ok(r.heeftTekst0 === false, 'en krijgt daarom geen eigen uitlegscherm');
  ok(r.fase === 'toets', 'de sessie begint meteen bij de vraag (nu: ' + r.fase + ')');
  ok(!r.heeftToetsMe, 'er staat geen "Toets me" waar niets te toetsen viel');
  ok(r.heeftOpties >= 2, 'er staan antwoordopties op het scherm (' + r.heeftOpties + ')');
  ok(r.zinBijVraag1, 'er staat begeleidende tekst bij de eerste vraag ("' + r.uitlegZin.slice(0, 45) + '...")');
  ok(!r.zinBijVraag2, 'en bij de tweede vraag niet meer');

  console.log('\n-- 4. het controlegeval: echte uitleg houdt zijn scherm --');
  ok(r.echtFase === 'uitleg', 'een stap met echte uitleg begint wél met lezen (nu: ' + r.echtFase + ')');

  console.log('\n-- 5. twee tellers die allebei "stap" heetten --');
  ok(!/Stap klaar/.test(r.klaar), '"Stap klaar: 2/2" staat er niet meer');
  ok(/goed/.test(r.klaar), 'er staat wat het getal is: hoeveel je er goed had');
  ok(/deel \d+ van \d+/.test(r.klaar), 'en waar je bent, in woorden');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
