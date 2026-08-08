// Playwright-smoketest voor het uitgebreide woordenboek (v19.52) en de opgeruimde, consistente
// zoekresultaten (v19.53 + v19.54).
// v19.52: de frequentielijst is 4.219 woorden: de oude top-2866 op frequentie plus 1.353 thematische
// woorden (eten, huis, lichaam, reizen, werk, natuur, kleding, mensen, werkwoorden, bijwoorden,
// techniek/sport/feest, maatschappij, hoeveelheden/abstracta).
// v19.53: het kopje "uit het grote woordenboek" zei de gebruiker niets, een woord dat hierboven al als
// leswoord staat kwam er dubbel in, het #frequentienummer was ruis, en je kon niet op een woord klikken.
// v19.54 (Stefans tweede ronde): "waarom staat er uberhaupt meer spaanse woorden boven? die hele zin kan
// toch weg?" / "waar is hasta ahora met luister en ai functionaliteit dat moet niet, die moet net zo zijn
// als de andere resultaten in het woordenboek. Maak het consistent" / "achter ahora en ahora misma staat
// nu wel het bolletje maar niet direct de vertaling, dat wil je juist wel zien."
// Kern van het contract dat dit script vastlegt: ÉÉN lijst, elke rij "woord · vertaling", elke uitklap
// dezelfde opbouw, nergens knoppen of nummers die alleen in de zoekstaart bestaan.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);

  const naamVeld = page.locator('input[placeholder="Naam"], input[placeholder="Name"]').first();
  await naamVeld.fill('PwDic52' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")').first();
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // --- 1. de data zelf ---
  const data = await page.evaluate(() => ({
    len: FREQ.length,
    enLen: Object.keys(FREQ_EN).length,
    grens: typeof FREQ_RANGLIMIET !== 'undefined' ? FREQ_RANGLIMIET : null,
    kop: FREQ[0][0] + ',' + FREQ[1][0],
    mist: FREQ.filter(function (p) { return !FREQ_EN[p[0]]; }).length,
    leeg: FREQ.filter(function (p) { return !p[1] || !p[1].trim(); }).length,
    indexLen: freqZoekIndex().length
  }));
  ok(data.len === 4219, 'het woordenboek kent 4.219 zoekwoorden (was 2.866)');
  ok(data.enLen === 4219, 'FREQ_EN loopt parallel: ook 4.219 Engelse glossen');
  ok(data.mist === 0, 'geen enkel woord mist een Engelse gloss');
  ok(data.leeg === 0, 'geen enkel woord mist een Nederlandse gloss');
  ok(data.grens === 2866, 'de grens tussen frequentiekop en thematische staart is nog gedocumenteerd (2866)');
  ok(data.kop === 'que,la', 'de frequentie-ordening van de kop is niet verschoven (que, la, ...)');
  ok(data.indexLen === 4219, 'de zoekindex is even lang als de woordenlijst');

  // --- 2. het aantal staat ook echt in de UI ---
  // v21.6: de kop opent nu het globale zoekveld; het woordenboek zit daar een tik achter.
  await page.evaluate(() => dicModal());
  await page.waitForTimeout(250);
  // v23.6: dit stond in een alinea van vier zinnen boven het zoekveld. Stefan: "deze tekst kan korter".
  // Het getal is niet weg, het staat nu in het zoekveld zelf, op de plek waar het pas telt.
  const intro = await page.locator('#dicCard').innerText();
  const plaats = await page.locator('#dicZoek').getAttribute('placeholder');
  ok(/(buiten de lessen|beyond the lessons)/.test(plaats || ''),
     'het zoekveld zegt dat het verder reikt dan de lessen: "' + plaats + '"');
  ok(!/frequentietop|frequency top/i.test(intro + (plaats || '')), 'er staat geen jargon als "frequentietop"');

  // helper: alle rijen, in schermvolgorde, met hun sleutel en zichtbare tekst
  async function alleRijen() {
    return await page.evaluate(() => {
      return Array.prototype.slice.call(document.querySelectorAll('#dicCard .dicrow')).map(function (r) {
        return {
          key: r.getAttribute('data-dic'),
          woord: ((r.querySelector('b.es') || {}).textContent || ''),
          tekst: r.innerText.replace(/\s+/g, ' ').trim(),
          knoppen: r.querySelectorAll('button').length
        };
      });
    });
  }
  const zoekRijen = (rs) => rs.filter((r) => /^freq:/.test(r.key || ''));
  const lesRijen = (rs) => rs.filter((r) => r.key !== null && !/^freq:/.test(r.key));

  // --- 3. nieuwe thematische woorden zijn vindbaar via de echte zoekbalk ---
  const proeven = [
    { zoek: 'aguacate', verwacht: ['avocado'] },
    { zoek: 'martillo', verwacht: ['hamer', 'hammer'] },
    { zoek: 'andén', verwacht: ['perron', 'platform'] },
    { zoek: 'nómina', verwacht: ['loonstrook', 'payslip'] },
    { zoek: 'ajedrez', verwacht: ['schaken', 'chess'] },
    { zoek: 'grondwet', verwacht: ['constitución'] }
  ];
  for (const proef of proeven) {
    await page.fill('#dicZoek', proef.zoek);
    await page.waitForTimeout(200);
    const t = (await page.locator('#dicCard').innerText()).toLowerCase();
    const raak = proef.verwacht.some((v) => t.indexOf(v.toLowerCase()) !== -1);
    ok(raak, 'zoeken op "' + proef.zoek + '" vindt het nieuwe woord (verwacht een van: ' + proef.verwacht.join(' / ') + ')');
  }

  // --- 4. v19.54: geen tussenkop, geen jargon, geen nummers boven de lijst ---
  await page.fill('#dicZoek', 'hora');
  await page.waitForTimeout(250);
  let rijen = await alleRijen();
  const kaart = await page.locator('#dicCard').innerText();
  ok(zoekRijen(rijen).length > 0, 'de zoekresultaten uit de woordenlijst staan gewoon in dezelfde lijst');
  ok(!/Meer Spaanse woorden|More Spanish words/i.test(kaart), 'de tussenkop boven de zoekresultaten is helemaal weg (Stefan: "die hele zin kan toch weg?")');
  ok(!/grote woordenboek|big dictionary/i.test(kaart), 'ook het oude kopje "uit het grote woordenboek" is nergens meer');
  ok(!/frequentierang|frequency rank|frequentieplek/i.test(kaart), 'geen uitleg over frequentieranglijsten in de kaart');
  ok(rijen.every((r) => !/#\d+/.test(r.tekst)), 'geen enkele rij draagt een #frequentienummer');
  ok(/🎵/.test(kaart), 'het liedjesblok houdt wel zijn eigen kopje (Stefan: "uit liedjes is wel grappig")');

  // --- 5. v19.54: elke rij zet de vertaling direct achter het woord ---
  const lesH = lesRijen(rijen);
  const ahora = lesH.filter((r) => r.woord === 'ahora')[0];
  const ahoraM = lesH.filter((r) => r.woord === 'ahora mismo')[0];
  ok(!!ahora && /ahora · (nu|now)/.test(ahora.tekst), 'een leswoord toont de vertaling direct achter het woord: "' + (ahora ? ahora.tekst : '-') + '"');
  ok(!!ahoraM && /ahora mismo · /.test(ahoraM.tekst), 'dat geldt ook voor "ahora mismo"');
  ok(!!ahora && /[⚪🔴🟡🟢]/.test(ahora.tekst), 'het statusbolletje staat er nog bij, nu in de rechterkolom');
  ok(lesH.every((r) => / · /.test(r.tekst)), 'álle leswoordrijen tonen een vertaling, niet alleen een bolletje (' + lesH.length + ' rijen)');
  ok(zoekRijen(rijen).every((r) => / · /.test(r.tekst)), 'en de zoekresultaten doen dat op precies dezelfde manier');

  // --- 6. dedup: een woord dat hierboven al als leswoord staat, komt er niet dubbel in ---
  const lesKaal = lesH.map((r) => r.woord.replace(/^(el|la|los|las|un|una) /, ''));
  const zoekW = zoekRijen(rijen).map((r) => r.woord);
  const overlap = zoekW.filter((z) => lesKaal.indexOf(z) !== -1);
  ok(lesH.some((r) => r.woord === 'la hora' || r.woord === 'ahora'), 'bij "hora" staan er ook leswoorden in de lijst');
  ok(overlap.length === 0, 'geen woord staat twee keer in de lijst (was: "ahora · nu #30" dubbel) — gevonden: ' + JSON.stringify(overlap));
  ok(zoekW.indexOf('horas') !== -1, 'verwante vormen die géén leswoord zijn blijven wel staan (horas)');
  ok(zoekW.some((z) => /hasta ahora|media hora|cuarto de hora/.test(z)), 'nuttige uitdrukkingen met het woord erin blijven staan');

  // --- 7. beste treffer eerst blijft werken: prefix vóór een treffer in de vertaling ---
  await page.fill('#dicZoek', 'mart');
  await page.waitForTimeout(250);
  const mart = zoekRijen(await alleRijen());
  ok(mart.length > 0 && /^mart/i.test(mart[0].woord), 'bij "mart" begint de eerste treffer ook echt met mart (' + (mart[0] ? mart[0].woord : '-') + ')');

  // --- 8. v19.54: de uitklap van een zoekresultaat is dezelfde als die van een leswoord ---
  await page.fill('#dicZoek', 'media');
  await page.waitForTimeout(250);
  const selMedia = '.dicrow[data-dic="freq:media"]';
  ok(await page.locator(selMedia).count() === 1, 'een zoekresultaat is een echte, aanklikbare rij met eigen sleutel');
  ok((await page.locator(selMedia).innerText()).indexOf('▸') !== -1, 'de rij laat met ▸ zien dat er meer achter zit');
  await page.click(selMedia + ' .dichead');
  await page.waitForTimeout(250);
  const detail = (await page.locator(selMedia).innerText()).replace(/\s+/g, ' ');
  ok(/▾/.test(detail), 'de rij klapt open bij een tik');
  ok(await page.locator(selMedia + ' .dicbody').count() === 1, 'de uitklap gebruikt dezelfde .dicbody-schil als een leswoord');
  ok(await page.locator(selMedia + ' button').count() === 0, 'geen knoppen in de uitklap: geen luister- of AI-functie die leswoorden niet hebben');
  ok(/Voorbeeld|Example/.test(detail), 'de uitklap toont een voorbeeldzin, net als bij een leswoord');
  ok(/media hora/.test(detail), 'de uitklap toont verwante uitdrukkingen met hetzelfde woord (media hora)');
  ok(!/792/.test(detail) && !/plek \d+|rank \d+/.test(detail), 'het frequentienummer is ook uit de uitklap verdwenen: "' + detail + '"');
  await page.click(selMedia + ' .dichead');
  await page.waitForTimeout(200);
  ok((await page.locator(selMedia).innerText()).indexOf('▾') === -1, 'nog een tik klapt de uitklap weer dicht');

  // --- 9. de voorbeeldzin bevat het woord ook echt (woordgrens-fix) ---
  await page.fill('#dicZoek', 'media hora');
  await page.waitForTimeout(250);
  await page.click('.dicrow[data-dic="freq:media hora"] .dichead');
  await page.waitForTimeout(220);
  const mh = (await page.locator('.dicrow[data-dic="freq:media hora"]').innerText()).replace(/\s+/g, ' ');
  const zinRegel = (mh.match(/(Voorbeeld|Example): ([^]*?)(?= [A-Z¿]|$)/) || [])[2] || mh;
  ok(/(^|[^a-záéíóúñ])hora/i.test(zinRegel), 'de voorbeeldzin bevat "hora" als heel woord, niet toevallig in "ahora": "' + zinRegel + '"');
  ok(!/comiendo ahora/i.test(mh), 'de oude valse treffer ("Estoy comiendo ahora" bij media hora) komt niet terug');

  // --- 10. een thematisch woord: geen verzonnen nummer, en ook geen extra knoppen ---
  await page.fill('#dicZoek', 'aguacate');
  await page.waitForTimeout(250);
  const selAgu = '.dicrow[data-dic="freq:aguacate"]';
  await page.click(selAgu + ' .dichead');
  await page.waitForTimeout(220);
  const agu = (await page.locator(selAgu).innerText()).replace(/\s+/g, ' ');
  ok(!/#\d+/.test(agu) && !/plek \d+|rank \d+/.test(agu), 'bij een thematisch woord staat geen (verzonnen) frequentieplek: "' + agu + '"');
  ok(await page.locator(selAgu + ' button').count() === 0, 'ook een woord zonder voorbeeldzin krijgt geen knoppenbalk');
  ok(/avocado/i.test(agu), 'de uitklap toont wel de betekenis, ook als de app er verder niets over te zeggen heeft');

  // --- 11. een werkwoord uit de zoekstaart krijgt dezelfde behandeling, geen aparte rijtjesknop ---
  await page.fill('#dicZoek', 'hornear');
  await page.waitForTimeout(250);
  const selVerb = '.dicrow[data-dic="freq:hornear"]';
  await page.click(selVerb + ' .dichead');
  await page.waitForTimeout(220);
  ok(await page.locator(selVerb + ' button').count() === 0, 'een werkwoord uit de zoekstaart krijgt ook geen eigen knoppen (consistentie)');
  ok(await page.locator(selVerb + ' .dicbody').count() === 1, 'maar wel dezelfde uitklap als elk ander woord');
  const geenPopup = await page.evaluate(() => typeof woordPopup);
  ok(geenPopup === 'undefined', 'de AI-uitlegpopup van v19.53 is helemaal verwijderd, geen dode code');

  // --- 12. vervoegingsherkenning werkt nog ---
  await page.fill('#dicZoek', 'comiste');
  await page.waitForTimeout(250);
  const vervoeg = await page.locator('#dicCard').innerText();
  ok(/comer/.test(vervoeg), 'de vervoegingsherkenning werkt nog: comiste -> comer');

  // --- 13. zoeken blijft vlot met 4.219 woorden ---
  const ms = await page.evaluate(() => {
    const t0 = performance.now();
    for (let i = 0; i < 20; i++) freqZoekResultaten('ar', false, 50);
    return performance.now() - t0;
  });
  ok(ms < 1500, '20 zoekopdrachten over 4.219 woorden duren samen minder dan 1,5s (' + Math.round(ms) + 'ms)');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten in eigen app-code tijdens hele test (' + relevanteErrors.length + ' gevonden, ' + (errors.length - relevanteErrors.length) + ' netwerkruis genegeerd)');
  if (relevanteErrors.length) relevanteErrors.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
