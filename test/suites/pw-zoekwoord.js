// v23.5 en v23.6: van zoekterm naar betekenis, zonder tussenscherm.
//
// v23.5 was de verkeerde reparatie. Stefan liet twee schermafbeeldingen zien: een zoekvenster met de
// treffer als kaartje onder een kopje WOORDEN, en het woordenboek met datzelfde woord opengeklapt.
// "deze hele weergave wil ik niet" bij de eerste, "ik wil alleen deze" bij de tweede. Ik had de omweg
// korter gemaakt terwijl de omweg zelf het probleem was.
//
// v23.6 haalt het zoekvenster weg. De pil in de kop opent het woordenboek, typen laat de betekenis
// zien, en bij precies één treffer klapt die vanzelf open. Deze suite bewaakt dat pad en de dingen
// die bij de verhuizing niet verloren mochten gaan.
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
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);


  /* v23.209: de zoekpil woont in de kop, en op een taakscherm is die kop weg. Dat is geen
     ongelukje: de app zegt bij elk woordkaartje "probeer het antwoord eerst zelf te bedenken", en
     een zoekknop naast die zin is een uitweg uit precies de poging die het werk doet. Buiten een
     oefening is opzoeken juist wel de bedoeling, en daar staat de pil dus gewoon.

     De app opent bij binnenkomst zelf je dagles, dus die pauzeren we hier eerst. Wat deze suite
     bewaakt verandert daar niet door: er is één zoekingang, hij heet iets, en hij opent het
     woordenboek. */
  await page.evaluate(() => { try { if(document.getElementById('btnLesPauze')) lesFramePauze(); } catch(e){} });
  await page.waitForTimeout(400);

  // ---- 1. de pil opent het woordenboek, leeg en met de cursor erin ----
  await page.click('#dicFab');
  await page.waitForTimeout(300);
  const start = await page.evaluate(() => ({
    open: !document.getElementById('dicWrap').classList.contains('hidden'),
    veld: document.getElementById('dicZoek').value,
    cursor: document.activeElement === document.getElementById('dicZoek')
  }));
  ok(start.open, 'de zoekpil opent het woordenboek');
  ok(start.veld === '', 'met een leeg veld, dus je begint niet in andermans zoekopdracht');
  ok(start.cursor, 'en je kunt meteen typen');

  // ---- 2. typen geeft de betekenis, niet een lijst om nog eens uit te kiezen ----
  const doelwit = await page.evaluate(() => {
    const zichtbaar = dicZichtbareWoorden();
    for (const w of zichtbaar) {
      const kern = w.es.replace(/^(el|la|los|las|un|una)\s+/i, '').split(/[\/(]/)[0].trim();
      if (kern.length < 5 || /\s/.test(kern)) continue;
      const q = kern.toLowerCase();
      const treffers = zichtbaar.filter(function (x) {
        return x.es.toLowerCase().indexOf(q) !== -1 || x.nl.toLowerCase().indexOf(q) !== -1;
      });
      const groepen = {};
      treffers.forEach(function (x) { groepen[x.es] = 1; });
      if (Object.keys(groepen).length === 1) return { id: w.id, es: w.es, kern: kern };
    }
    return null;
  });
  ok(!!doelwit, 'een testwoord met precies één treffer gevonden: ' + (doelwit ? doelwit.es : 'geen'));

  if (doelwit) {
    await page.fill('#dicZoek', doelwit.kern);
    await page.waitForTimeout(400);
    const na = await page.evaluate(() => {
      const kaart = document.getElementById('dicCard');
      return {
        rijen: kaart.querySelectorAll('.dicrow[data-dic]').length,
        open: kaart.querySelectorAll('.dicrow[data-dic] .dicbody').length,
        tekst: kaart.innerText || ''
      };
    });
    ok(na.rijen === 1, 'er staat precies één woordrij: ' + na.rijen);
    ok(na.open >= 1, 'en die staat open, dus de betekenis staat er zonder nog een tik');
    ok(na.tekst.indexOf(doelwit.es) !== -1, 'het woord staat op het scherm: ' + doelwit.es);

    // dichtklappen mag, en dan moet hij dicht blijven bij de volgende render
    await page.evaluate(() => document.querySelector('#dicCard .dicrow[data-dic] .dichead').click());
    await page.waitForTimeout(200);
    await page.evaluate(() => renderDic());
    await page.waitForTimeout(200);
    const dicht = await page.evaluate(() => document.querySelectorAll('#dicCard .dicrow[data-dic] .dicbody').length);
    ok(dicht === 0, 'wat je dichtklapt blijft dicht, het openklappen springt niet terug');
  }

  // ---- 3. meerdere treffers: dan kies je zelf, niets klapt open ----
  const meer = await page.evaluate(() => {
    dicZoek = 'a'; dicOpen = null; dicAutoQ = null;
    dicZoek = 'ar';
    renderDic();
    const kaart = document.getElementById('dicCard');
    // alleen de woordrijen tellen: liedregels krijgen ook een .dicbody, en die zegt niets over openklappen
    return { rijen: kaart.querySelectorAll('.dicrow[data-dic]').length,
             open: kaart.querySelectorAll('.dicrow[data-dic] .dicbody').length };
  });
  ok(meer.rijen > 1, 'een brede zoekterm geeft meerdere rijen: ' + meer.rijen);
  ok(meer.open === 0, 'en dan klapt er niets vanzelf open, want er valt iets te kiezen');

  // ---- 4. de uitleg boven het veld wijkt zodra je typt ----
  const kop = await page.evaluate(() => {
    dicZoek = ''; dicOpen = null; dicAutoQ = null;
    renderDic();
    const bladeren = document.getElementById('dicCard').innerText;
    dicZoek = 'casa';
    renderDic();
    const zoeken = document.getElementById('dicCard').innerText;
    return { bladeren: bladeren, zoeken: zoeken };
  });
  ok(/(lastig|tricky)/.test(kop.bladeren), 'bij bladeren staat er nog uitleg van de bolletjes');
  ok(!/(lastig|tricky)/.test(kop.zoeken), 'zodra je typt is die uitleg weg');
  ok(!/(Jouw woordenboek|Your dictionary)/.test(kop.bladeren), 'de kop zegt niet nog een keer wat er in de balk erboven al staat');
  ok(kop.bladeren.split('\n')[0].length < 120, 'en de eerste regel is kort: "' + kop.bladeren.split('\n')[0].slice(0, 90) + '"');

  // ---- 5. wat het oude venster wél vond, is niet verdwenen ----
  const ander = await page.evaluate(() => {
    dicZoek = 'casa'; dicOpen = null; dicAutoQ = null;
    renderDic();
    const vouw = document.querySelector('#dicCard details');
    return {
      erIn: !!vouw,
      rijen: vouw ? vouw.querySelectorAll('.dicrow[data-oz]').length : 0,
      soorten: vouw ? Array.from(vouw.querySelectorAll('.dicrow[data-oz]')).map((r) => r.getAttribute('data-oz')) : []
    };
  });
  ok(ander.erIn && ander.rijen > 0, 'zinnen en grammatica staan onder de vouw: ' + ander.rijen);
  ok(ander.soorten.indexOf('woord') === -1, 'en daar staat geen woord tussen, die horen bovenaan');

  // ---- 6. "+ leren" is meeverhuisd naar de woordrij ----
  const leren = await page.evaluate(() => {
    const w = dicZichtbareWoorden().filter(function (x) { return !S.srs[x.id]; })[0];
    if (!w) return { geen: true };
    dicZoek = w.es; dicOpen = null; dicAutoQ = null;
    renderDic();
    const knop = document.querySelector('#dicCard button[data-dmee]');
    if (!knop) return { geen: false, knop: false };
    knop.click();
    return { geen: false, knop: true, inRotatie: !!S.srs[w.id], box: S.srs[w.id] && S.srs[w.id].box, zelf: S.srs[w.id] && S.srs[w.id].zelf };
  });
  if (leren.geen) {
    console.log('PASS elk woord zit al in de rotatie, niets te toetsen');
  } else {
    ok(leren.knop === true, 'op een woord dat je nog niet oefent staat een knop om het mee te nemen');
    ok(leren.inRotatie === true, 'en die zet het woord in je woordjes');
    ok(leren.box === 0 && leren.zelf === 1, 'in doosje nul en gemarkeerd als zelf opgezocht');
  }

  const bladerKnop = await page.evaluate(() => {
    dicZoek = ''; dicOpen = null; dicAutoQ = null;
    renderDic();
    return document.querySelectorAll('#dicCard button[data-dmee]').length;
  });
  ok(bladerKnop === 0, 'in de alfabetische lijst staat die knop niet, daar zou hij honderden keren staan');

  // ---- 7. dicToonWoord blijft werken voor wie er van buitenaf in komt ----
  const direct = await page.evaluate(() => {
    dicZoek = ''; dicOpen = null;
    const w = dicZichtbareWoorden()[0];
    return { geraakt: dicToonWoord(w.id), zoek: dicZoek, open: dicOpen, es: w.es, mis: dicToonWoord('bestaat-niet-w99999') };
  });
  ok(direct.geraakt === true && direct.zoek === direct.es && direct.open === direct.es, 'dicToonWoord vult veld en opent de rij: ' + direct.open);
  ok(direct.mis === false, 'een onbekende id verandert niets');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
