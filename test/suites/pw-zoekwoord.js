// v23.5: een woord aantikken in het zoekveld opent dat woord, niet de lijst van 705.
//
// Stefan, met twee schermafbeeldingen naast elkaar: "kijk het resultaat van het eerste en klik ik dan
// kom ik op resultaat van het tweede, die extra stap is niet nodig toch."
//
// zoekGaNaar("woord", id) riep dicModal() aan en gebruikte de id nergens. Je had het woord al
// gevonden en al aangetikt, en stond daarna weer in een alfabetische lijst.
//
// Deze suite loopt de weg die hij liep: zoekveld open, woord typen, treffer aantikken, en dan moet de
// uitleg er staan. Plus de randgevallen die de reparatie niet mag stukmaken.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error' && !/Failed to load resource/.test(msg.text())) errors.push('console.error: ' + msg.text()); });

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
  await page.fill('input[placeholder="Name"]', 'PwZw' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);

  // ---- 1. de weg van Stefan, via het echte scherm ----
  // Een woord kiezen dat het woordenboek kan tonen en dat maar één treffer geeft, zodat de test niet
  // afhangt van welke track er toevallig actief is.
  const doelwit = await page.evaluate(() => {
    const zichtbaar = dicZichtbareWoorden();
    for (const w of zichtbaar) {
      const kern = w.es.replace(/^(el|la|los|las|un|una)\s+/i, '').split(/[\/(]/)[0].trim();
      if (kern.length < 5 || /\s/.test(kern)) continue;
      const groepen = zoekResultaten(kern);
      const woorden = groepen.filter((g) => g.soort === 'woord')[0];
      if (woorden && woorden.rijen.length === 1 && woorden.rijen[0].id === w.id) return { id: w.id, es: w.es, kern: kern };
    }
    return null;
  });
  ok(!!doelwit, 'een testwoord met precies één zoektreffer gevonden: ' + (doelwit ? doelwit.es : 'geen'));

  if (doelwit) {
    await page.evaluate(() => zoekOpen());
    await page.waitForTimeout(150);
    await page.fill('#zoekVeld', doelwit.kern);
    await page.waitForTimeout(300);
    const treffers = await page.locator('#zoekUit .zoekrij[data-zs="woord"]').count();
    ok(treffers === 1, 'het zoekveld toont precies één woordtreffer: ' + treffers);

    // Aantikken via de knoop zelf. Een echte muisklik is hier onbetrouwbaar omdat het paneel na 120 ms
    // stilte opnieuw tekent; de afhandelaar die eronder hangt is dezelfde.
    await page.evaluate(() => document.querySelector('#zoekUit .zoekrij[data-zs="woord"]').click());
    await page.waitForTimeout(300);

    const na = await page.evaluate(() => {
      const wrap = document.getElementById('dicWrap');
      const zoekDicht = (document.getElementById('zoekWrap') || {}).className || '';
      const veld = document.getElementById('dicZoek');
      const open = document.querySelectorAll('#dicCard .dicbody').length;
      const rijen = document.querySelectorAll('#dicCard .dicrow').length;
      return {
        dicZichtbaar: !!wrap && !wrap.classList.contains('hidden'),
        zoekWeg: /hidden/.test(zoekDicht),
        veld: veld ? veld.value : null,
        open: open,
        rijen: rijen,
        tekst: (document.getElementById('dicCard') || {}).innerText || ''
      };
    });
    ok(na.dicZichtbaar, 'het woordenboek staat open');
    ok(na.zoekWeg, 'en het zoekvenster is dicht, dus er staat er maar één');
    ok(na.veld === doelwit.es, 'het zoekveld van het woordenboek is gevuld met het woord zelf: ' + na.veld);
    ok(na.open === 1, 'precies één rij staat opengeklapt, dus je hoeft niet nog eens te tikken: ' + na.open);
    ok(na.rijen <= 3, 'en de lijst is teruggebracht tot de treffer in plaats van alle leswoorden: ' + na.rijen);
    ok(na.tekst.indexOf(doelwit.es) !== -1, 'het woord staat op het scherm: ' + doelwit.es);
  }

  // ---- 2. dezelfde stap zonder scherm, zodat de oorzaak zelf vastligt ----
  const direct = await page.evaluate(() => {
    dicZoek = ''; dicOpen = null;
    const w = dicZichtbareWoorden()[0];
    const geraakt = dicToonWoord(w.id);
    return { geraakt: geraakt, zoek: dicZoek, open: dicOpen, es: w.es };
  });
  ok(direct.geraakt === true, 'dicToonWoord meldt dat het gelukt is');
  ok(direct.zoek === direct.es && direct.open === direct.es, 'zoekterm en open rij wijzen allebei naar het woord: ' + direct.open);

  // ---- 3. een onbekende id verandert niets, in plaats van het woordenboek leeg te filteren ----
  const onbekend = await page.evaluate(() => {
    dicZoek = ''; dicOpen = null;
    const geraakt = dicToonWoord('bestaat-niet-w99999');
    return { geraakt: geraakt, zoek: dicZoek, open: dicOpen };
  });
  ok(onbekend.geraakt === false, 'een onbekende id levert false op');
  ok(onbekend.zoek === '' && onbekend.open === null, 'en laat het woordenboek staan zoals het stond');

  // ---- 4. een woord uit een hoofdstuk dat nog op slot staat valt terug op het oude gedrag ----
  // Zonder deze terugval zou de zoeker een woord tonen dat het woordenboek daarna niet kán laten
  // zien, en dan staat er "niets gevonden" over iets wat je net zag staan. Een stap extra is minder erg.
  const opSlot = await page.evaluate(() => {
    const zichtbaar = {};
    dicZichtbareWoorden().forEach((w) => { zichtbaar[w.id] = 1; });
    const dicht = WORDS.filter((w) => !zichtbaar[w.id])[0];
    if (!dicht) return { geen: true };
    dicZoek = ''; dicOpen = null;
    const geraakt = dicToonWoord(dicht.id);
    return { geen: false, geraakt: geraakt, zoek: dicZoek, open: dicOpen, es: dicht.es };
  });
  if (opSlot.geen) {
    console.log('PASS geen woord op slot in dit profiel, niets te toetsen');
  } else {
    ok(opSlot.geraakt === false, 'een woord uit een vergrendeld hoofdstuk geeft false: ' + opSlot.es);
    ok(opSlot.zoek === '' && opSlot.open === null, 'en het woordenboek wordt niet leeggefilterd');
  }

  // ---- 5. de andere soorten treffers gaan nog steeds hun eigen kant op ----
  const anders = await page.evaluate(() => {
    const bron = zoekGaNaar.toString();
    return {
      zin: /soort === "zin"/.test(bron),
      concept: /soort === "concept"/.test(bron),
      woordEerst: bron.indexOf('dicToonWoord') < bron.indexOf('soort === "zin"')
    };
  });
  ok(anders.zin && anders.concept, 'zinnen en grammaticaconcepten hebben hun eigen route nog');
  ok(anders.woordEerst, 'en de woordroute staat er nog vóór, dus de volgorde is niet omgegooid');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
