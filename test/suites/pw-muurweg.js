// pw-muurweg.js (31 aug, v23.222) — het sociale is van het dagscherm af, en het meten loopt door
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 31 aug: "de muur was er om het sociale te bevorderen maar dat wordt niet echt gebruikt,
// dus dat moeten we helemaal opnieuw ontwerpen, en dan kunnen we het nu beter eerst weghalen (maar
// wel blijven meten op de achtergrond)."
//
// Die tweede helft is de reden dat deze suite bestaat. Een scherm weghalen is makkelijk te zien;
// dat het meten daarbij intact blijft is dat niet. Wie over drie maanden het sociale opnieuw
// ontwerpt heeft de gebeurtenissen van alle tussenliggende dagen nodig, en als die stil zijn
// weggevallen merkt niemand dat tot het moment dat ze nodig zijn. Dan is het te laat: je kunt geen
// data van gisteren alsnog gaan verzamelen.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE TWEE SCHERMEN ZIJN WEG, OOK ALS JE EEN GROEP HEBT. Dat laatste is het punt: de muur werd
//      alleen getekend voor wie in een groep zit, dus "hij staat er niet" is geen meting zolang er
//      geen groep is. Deze proef zet er dus eerst een.
//   2. HET DAGSCHERM WERKT NOG, VOOR EN NA JE LES. Een verwijdering die een leeg scherm oplevert is
//      erger dan de kaart die weg moest.
//   3. HET METEN LOOPT DOOR, EN DAT WORDT AFGELUISTERD IN PLAATS VAN AANGENOMEN. /api/sync wordt
//      onderschept en er wordt gekeken wat er daadwerkelijk in het pakket zit: de mijlpalen, de
//      dagoogst en de groep. Dit is het verschil tussen "syncUp bestaat nog" en "de gegevens komen
//      er nog aan".
//   4. EN ER WORDT NIETS MEER OPGEHAALD VOOR EEN SCHERM DAT ER NIET IS. /api/groep hoort niet meer
//      aangeroepen te worden bij het tekenen van je dag. Een netwerkverzoek voor een kaart die
//      niemand ziet is precies het soort rest dat na een verwijdering blijft hangen.
//   5. WAT ER BEWUST BLIJFT STAAN. KRABBELS, krabbelVind() en dagKrabbels(): binnengekomen
//      krabbels komen nog op je dagbord. Versturen kan niet meer, want dat kon alleen op de muur.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwMw' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);

  // ---- 1 en 2. het dagscherm, met een groep ----
  console.log('\n-- 1 en 2. het dagscherm, mét een groep --');
  const scherm = await page.evaluate(() => {
    S.lang = 'nl';
    /* De groep is het controlegeval. Zonder groep tekende de muur zichzelf sowieso niet, dus dan
       zou punt 1 groen staan om de verkeerde reden. */
    S.groepen = [{ gcode: 'PROEF1', naam: 'pw' }];
    function foto() {
      const el = document.getElementById('lessonList');
      return {
        kaarten: el.querySelectorAll('.card').length,
        muur: !!document.getElementById('muurCard'),
        dagzin: !!document.getElementById('dagzinInp'),
        tekst: el.textContent.replace(/\s+/g, ' ')
      };
    }
    S.lesFlow = {};
    show('lessen', true); renderLessons();
    const voor = foto();
    S.lesFlow[today()] = true;
    renderLessons();
    const na = foto();
    return { voor: voor, na: na,
             functies: [typeof muurHtml, typeof dagZinHtml, typeof muurHaal, typeof dagVraag] };
  });
  console.log('   vóór je les ' + scherm.voor.kaarten + ' kaarten, erna ' + scherm.na.kaarten);
  ok(!scherm.voor.muur && !scherm.na.muur, 'de muur staat er niet, ook niet na je les');
  ok(!scherm.voor.dagzin && !scherm.na.dagzin, 'en de vraag van vandaag ook niet');
  ok(scherm.functies.every(function (t) { return t === 'undefined'; }),
    'de functies erachter bestaan niet meer (' + scherm.functies.join(', ') + ')');
  ok(scherm.voor.kaarten >= 1 && scherm.na.kaarten > scherm.voor.kaarten,
    'CONTROLE: en het dagscherm werkt nog, met meer erop na je les');
  ok(!/vraag van vandaag/i.test(scherm.na.tekst), 'het woord staat er ook nergens meer');

  // ---- 3 en 4. het meten ----
  console.log('\n-- 3 en 4. wat er nog naar de server gaat --');
  const sync = await page.evaluate(async () => {
    const echt = window.api;
    const gezien = [];
    window.api = function (pad, methode, body) {
      gezien.push({ pad: pad, body: body });
      return Promise.resolve({ ok: true, updated_at: 1 });
    };

    // iets om te meten: een mijlpaal van vandaag en een dagoogst
    S.mijlpalen = S.mijlpalen || {};
    S.mijlpalen['woorden-100'] = today();
    S.oogst = S.oogst || {};
    S.oogst[today()] = { w: 4, z: 2 };

    renderLessons();                 // punt 4: tekenen mag niets ophalen voor een dood scherm
    const naTekenen = gezien.map(function (x) { return x.pad; });

    syncUp();
    await new Promise(function (r) { setTimeout(r, 150); });
    const pakket = gezien.filter(function (x) { return x.pad === '/api/sync'; }).pop();
    window.api = echt;

    const st = (pakket && pakket.body && pakket.body.state) || null;
    return {
      naTekenen: naTekenen,
      gestuurd: !!pakket,
      mijlpaal: !!(st && st.mijlpalen && st.mijlpalen['woorden-100']),
      oogst: !!(st && st.oogst && st.oogst[today()]),
      groep: !!(st && st.groepen && st.groepen.length)
    };
  });
  ok(sync.gestuurd, 'syncUp() stuurt nog een pakket naar /api/sync');
  ok(sync.mijlpaal, 'en de mijlpaal van vandaag zit erin');
  ok(sync.oogst, 'en de dagoogst ook');
  ok(sync.groep, 'en in welke groep je zit');
  ok(!sync.naTekenen.some(function (p) { return /^\/api\/groep/.test(p); }),
    'het tekenen van je dag haalt niets meer op voor de muur (' + (sync.naTekenen.join(', ') || 'geen aanroepen') + ')');

  // ---- 5. wat er bewust blijft ----
  console.log('\n-- 5. wat er bewust blijft staan --');
  const blijft = await page.evaluate(() => ({
    palet: Array.isArray(KRABBELS) ? KRABBELS.length : 0,
    vind: typeof krabbelVind === 'function' && !!krabbelVind('ole'),
    dagkrab: typeof dagKrabbels === 'function',
    groepen: typeof renderGroepen === 'function'
  }));
  ok(blijft.palet >= 6 && blijft.vind, 'het krabbelpalet staat er nog (' + blijft.palet + ')');
  ok(blijft.dagkrab, 'dagKrabbels() ook: binnengekomen krabbels komen nog op je dagbord');
  ok(blijft.groepen, 'en de groepenpagina bestaat nog, want daar hangt het meten aan');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
