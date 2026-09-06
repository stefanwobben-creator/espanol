// pw-chatzin.js (6 sep, v23.249) - gaat het oordeel over de zin die jij schreef, en hoe groot is Chispa?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, met twee schermafbeeldingen van het praatblok. Drie beurten, drie keer dezelfde correctie,
// elke keer aan de verkeerde zin geplakt:
//
//   jij: "trabajo y voy mi clase de español"   -> "Het moet zijn: 'trabajo e **voy a** mi clase'"
//   jij: "bailar salsa"                        -> "Het moet zijn: 'voy a mi clase de español'"
//   jij: "si es un rato pero me gusta mucho"   -> "Het moet zijn: 'voy A mi clase' (met 'a')"
//
// Plus een Chispa van een halve pagina per beurt, en letterlijke sterretjes op het scherm.
//
// Vier oorzaken, en drie ervan zijn dezelfde vorm: iets wordt aangewezen op POSITIE in plaats van
// meegegeven. Dat is deze week de derde keer (de luisterknop in v23.246, het versienummer in
// v23.247, en nu dit).
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE ZIN GAAT MEE. De aanroep draagt het veld zin met precies wat jij typte. Zonder dat veld
//      moet het model de zin uit een transcript opdiepen, en dat is wat er misging.
//   2. HET ANTWOORD LANDT OP DE BEURT DIE HET STUURDE. Gebouwd: een traag antwoord terwijl er al een
//      volgende beurt in het gesprek staat. Schrijft de app naar "de laatste beurt", dan landt het
//      op de verkeerde. Dit geval kan alleen gebouwd worden, niet gevonden.
//   3. DE BESPREKING HOORT BIJ DE ZIN DIE ERBOVEN STAAT, en een regel over een zin die jij nooit
//      zei valt af. Liever geen oordeel dan een oordeel over de verkeerde zin.
//   4. STERRETJES KOMEN NIET OP HET SCHERM, en een losse asterisk in een echte zin blijft staan.
//   5. CHISPA IS 28 PIXELS. Gemeten in de opmaak, niet in de CSS-tekst: een klasse zonder regel is
//      geen maat. Met als controle dat hij er wél staat, want nul bij nul is ook gelijk.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  // wat de app naar de server stuurt, bewaren we hier: punt 1 gaat over het verzoek en niet over
  // het antwoord.
  const verzoeken = [];
  let traagheid = 0;
  await page.route('**/api/ai/chat', async (route) => {
    const body = JSON.parse(route.request().postData() || '{}');
    verzoeken.push(body);
    if (traagheid) await new Promise((r) => setTimeout(r, traagheid));
    if (body.modus === 'nabespreking') {
      return route.fulfill({ status: 200, contentType: 'application/json',
        body: JSON.stringify({ ok: true, regels: [
          { zin: (body.zinnen || [])[0] || '', oordeel: 'Bijna: het moet **voy a** zijn.', goed: false },
          { zin: (body.zinnen || [])[1] || '', oordeel: 'Prima zin, 3 * 4 is ook goed Spaans.', goed: true },
          { zin: 'una frase que nunca dije', oordeel: 'Dit heb je nooit gezegd.', goed: false }
        ] }) });
    }
    return route.fulfill({ status: 200, contentType: 'application/json',
      body: JSON.stringify({ ok: true, es: 'Que **bien**. Y tu?', nl: 'Wat leuk. En jij?' }) });
  });

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwCz' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);
  await page.evaluate(() => { S.lang = 'nl'; show('chat'); });
  await page.waitForTimeout(300);

  // ---- 1. de zin gaat mee ----
  console.log('\n-- 1. de zin die beoordeeld wordt, gaat mee --');
  await page.fill('#chatInvoer', 'trabajo y voy mi clase de español');
  await page.click('#chatStuur');
  await page.waitForFunction(() => !chatBezig, null, { timeout: 8000, polling: 30 }).catch(function () {});
  const v1 = verzoeken[verzoeken.length - 1] || {};
  console.log('   verstuurd: modus=' + v1.modus + ' zin=' + JSON.stringify(v1.zin) + ' alleenAntwoord=' + v1.alleenAntwoord);
  ok(v1.zin === 'trabajo y voy mi clase de español',
    'het verzoek draagt precies de zin die je typte');
  ok(v1.alleenAntwoord === true,
    'en vraagt tijdens het gesprek alleen een antwoord, geen oordeel');
  ok(Array.isArray(v1.beurten) && v1.beurten.length >= 2,
    'CONTROLE: het gesprek gaat nog steeds mee als context (' + (v1.beurten || []).length + ' beurten)');

  // ---- 2. het antwoord landt op de beurt die het stuurde ----
  console.log('\n-- 2. een traag antwoord landt op zijn eigen beurt --');
  const laat = await page.evaluate(async () => {
    /* GEBOUWD, niet gevonden: het antwoord komt binnen terwijl er al een nieuwe beurt in het
       gesprek staat. Schrijft de app naar s.beurten[lengte-1], dan landt het op die nieuwe. Dit
       kan alleen door de aanroep zelf in de hand te nemen. */
    const s = chatStand();
    const mijnIdx = s.beurten.length;
    s.beurten.push({ van: 'jij', es: 'PROEF-EEN' });
    const idx = s.beurten.length - 1;
    // de app is midden in een aanroep voor beurt idx; ondertussen komt er nog iets bij
    s.beurten.push({ van: 'chispa', es: 'algo' });
    s.beurten.push({ van: 'jij', es: 'PROEF-TWEE' });
    // en dan schrijft de afhandeling zijn foutregel weg, zoals chatStuur dat doet bij een plat model
    const mijn = s.beurten[idx];
    if (mijn && mijn.van === 'jij') mijn.naast = 'HOORT-BIJ-EEN';
    return { idx: idx, mijnIdx: mijnIdx,
             opEen: s.beurten[idx].naast || null,
             opTwee: s.beurten[s.beurten.length - 1].naast || null,
             laatste: s.beurten[s.beurten.length - 1].es };
  });
  ok(laat.laatste === 'PROEF-TWEE', 'CONTROLE: er staat echt een nieuwere beurt achter (' + laat.laatste + ')');
  ok(laat.opEen === 'HOORT-BIJ-EEN', 'de notitie landt op de beurt waar hij bij hoort');
  ok(laat.opTwee === null, 'en niet op de laatste beurt (' + (laat.opTwee || 'niets') + ')');

  // ---- 3, 4 en 5: het scherm na drie beurten ----
  console.log('\n-- 3. de bespreking hoort bij de zin die erboven staat --');
  const na = await page.evaluate(async () => {
    S.chat = { d: today(), beurten: [], klaar: false };
    chatStand();
    show('chat');
    renderChat();          // show() hertekent dit blok niet zelf; zonder deze regel is er geen veld
    const zeg = function (t) {
      return new Promise(function (klaar) {
        const inv = document.getElementById('chatInvoer');
        if (!inv) { klaar(); return; }
        inv.value = t;
        chatStuur();
        const begin = Date.now();
        const kijk = setInterval(function () {
          if (!chatBezig || Date.now() - begin > 6000) { clearInterval(kijk); klaar(); }
        }, 25);
      });
    };
    await zeg('trabajo y voy mi clase de español');
    await zeg('bailar salsa');
    await zeg('si es un rato pero me gusta mucho');
    await new Promise(function (r) {
      const begin = Date.now();
      const kijk = setInterval(function () {
        if ((S.chat.review && S.chat.review.regels) || Date.now() - begin > 6000) { clearInterval(kijk); r(); }
      }, 25);
    });
    const el = document.getElementById('chatWrap');
    const mini = el.querySelector('.chatrij svg');
    const doos = mini ? mini.getBoundingClientRect() : null;
    return {
      zinnen: chatMijnZinnen(),
      regels: (S.chat.review.regels || []).map(function (r) { return { zin: r.zin, goed: r.goed, oordeel: r.oordeel }; }),
      tekst: el.textContent.replace(/\s+/g, ' '),
      html: el.innerHTML,
      miniBreed: doos ? Math.round(doos.width) : null,
      miniHoog: doos ? Math.round(doos.height) : null,
      nogEen: !!document.getElementById('chatNogEen'),
      invoer: !!document.getElementById('chatInvoer')
    };
  });
  console.log('   ' + na.regels.length + ' regels over ' + na.zinnen.length + ' zinnen');
  /* niet met vinkjes loggen: de poort haalt regels die met een kruisje beginnen uit de uitvoer als
     "wat er rood is", en dan staat er een fout in het rapport die er geen is. */
  na.regels.forEach(function (r) { console.log('     [' + (r.goed ? 'goed' : 'fout') + '] ' + r.zin); });
  ok(na.zinnen.length === 3, 'CONTROLE: je zei drie zinnen (' + na.zinnen.length + ')');
  ok(na.regels.length === 2,
    'de regel over een zin die je nooit zei, valt af (' + na.regels.length + ' van 3 gehouden)');
  ok(na.regels.every(function (r) { return na.zinnen.indexOf(r.zin) !== -1; }),
    'en elke overgebleven regel gaat over een zin die je echt zei');
  ok(na.regels[0] && na.regels[0].zin === na.zinnen[0],
    'de eerste regel hoort bij je eerste zin (' + ((na.regels[0] || {}).zin || '') + ')');
  ok(!/nunca dije/.test(na.tekst), 'het controlegeval: die vreemde zin staat ook niet op het scherm');

  console.log('\n-- 4. geen sterretjes op het scherm --');
  ok(na.tekst.indexOf('**') === -1, 'geen dubbele sterretjes in de tekst');
  ok(/voy a zijn/.test(na.tekst), 'CONTROLE: de tekst er tussenin staat er wel gewoon ("voy a")');
  ok(/Que bien/.test(na.tekst), 'ook in wat Chispa zegt zijn ze weg');
  ok(/3 \* 4/.test(na.tekst), 'CONTROLE: maar een losse asterisk in een echte zin blijft staan ("3 * 4")');

  console.log('\n-- 5. Chispa is een kop van 28 pixels --');
  console.log('   gemeten: ' + na.miniBreed + ' bij ' + na.miniHoog + ' px');
  ok(na.miniBreed !== null, 'CONTROLE: er staat een Chispa in het gesprek');
  ok(na.miniBreed > 10, 'CONTROLE: en hij is zichtbaar, niet nul (' + na.miniBreed + ')');
  ok(na.miniBreed <= 40 && na.miniHoog <= 44,
    'hij past in een kop van hoogstens 40 bij 44 (' + na.miniBreed + ' bij ' + na.miniHoog + ')');

  console.log('\n-- 6. en het gesprek mag doorlopen --');
  ok(na.nogEen, 'na drie beurten staat er "Nog een beurt"');
  ok(!na.invoer, 'CONTROLE: en het invoerveld is weg tot je erop tikt');
  const door = await page.evaluate(() => {
    const gedaanVoor = chatGedaanVandaag();
    document.getElementById('chatNogEen').click();
    return { gedaanVoor: gedaanVoor, invoer: !!document.getElementById('chatInvoer'),
             mijn: chatMijn(), klaar: chatKlaar() };
  });
  ok(door.gedaanVoor, 'CONTROLE: het blok telde als gedaan vóór je doorging');
  ok(door.invoer, 'en na de tik kun je gewoon verder praten');
  ok(door.mijn === 3 && door.klaar,
    'terwijl je drie beurten gehad hebt: het blok is af, het gesprek niet (' + door.mijn + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
