// Playwright-test voor v19.80: de kamer als compositie.
//
// Stefan: "chispa mag ook veel wat groter hier", "juist het effect van die interactie op hen is
// leuk", "Dansen zie je nog niet gebueren", en "de huisdieren moet veel groter en echt in de
// compostie bij chispa staan er niet eromheen zoals de rest van de decoratie".
//
// De kamer was een lijst: zij bovenaan, een rijtje pictogrammetjes eronder, en het behang er in
// dezelfde maat omheen. Alles even groot is hetzelfde als niets belangrijk. Deze test meet de
// echte meetkunde op het scherm, want dit is precies het soort fout dat een assertie op de HTML
// niet ziet en je oog meteen wel. Wat hier vastligt:
//   1. Chispa is groot, en zij is het middelpunt
//   2. de dieren zijn dieren, geen icoontjes, en ze staan bij haar in beeld (niet ernaast)
//   3. het decor ligt zichtbaar achter het gezelschap
//   4. de dansvloer ligt onder haar voeten, niet als waas over haar buik
//   5. als zij danst, dansen zij mee, ieder net iets later
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 430, height: 860 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  const BASIS = 'http://localhost:8321/espanol-stefan.html';
  await page.goto(BASIS);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(BASIS);
  await page.waitForTimeout(600);

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwKamer' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  await page.evaluate(() => {
    window.chispaSlaapt = function () { return false; };
    window.petMoodKey = function () { return 'happy'; };
    S.txp = 30000; // alle drie de vriendjes verdiend
    SHOP.forEach(function (it) { S.owned[it.id] = true; });
    S.rincon = S.rincon || {};
    RINCON.forEach(function (it) { S.rincon[it.id] = true; });
    show('chispa');
  });
  await page.waitForTimeout(1400);
  await page.evaluate(() => { try { chispaStop(); } catch (e) {} });
  await page.waitForTimeout(300);

  // --- 1. Zij is groot, en zij staat in het midden ---
  const maten = await page.evaluate(() => {
    function box(sel) { const e = document.querySelector(sel); if (!e) return null; const r = e.getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top, b: r.bottom, w: r.width, h: r.height }; }
    const sc = box('#chScene');
    return {
      scene: sc,
      chispa: box('#petBox svg'),
      amigos: Array.prototype.map.call(document.querySelectorAll('.amigo svg'), function (s) {
        const r = s.getBoundingClientRect();
        return { l: r.left, r: r.right, t: r.top, b: r.bottom, w: r.width, h: r.height };
      })
    };
  });
  ok(!!maten.chispa && maten.chispa.w >= 250, 'Chispa is fors groter geworden (' + Math.round((maten.chispa || {}).w || 0) + 'px breed)');
  const midScene = maten.scene.l + maten.scene.w / 2;
  const midChispa = maten.chispa.l + maten.chispa.w / 2;
  ok(Math.abs(midScene - midChispa) < 14, 'ze staat midden in haar eigen kamer, niet aan de kant');
  ok(maten.chispa.r <= maten.scene.r + 1 && maten.chispa.l >= maten.scene.l - 1,
     'en ze past er nog wel helemaal in: niets valt van de kaart af');

  // --- 2. De dieren zijn dieren, en ze staan bij haar ---
  ok(maten.amigos.length === 3, 'alle drie de vriendjes staan in beeld');
  const kleinste = Math.min.apply(null, maten.amigos.map((a) => a.w));
  ok(kleinste >= 68, 'zelfs de kleinste (die achteraan staat) is nog een dier, geen pictogram (' + Math.round(kleinste) + 'px)');
  const voorste = maten.amigos.filter((a) => a.w >= 88);
  ok(voorste.length >= 2, 'de twee die vooraan staan zijn flink groot (' + voorste.map((a) => Math.round(a.w)).join(', ') + 'px)');
  // "In de compositie" betekent meetbaar iets: hun vlak raakt het hare. Stonden ze eromheen, dan
  // was er altijd lucht tussen. Dit is het verschil tussen een gezelschap en een lijstje.
  const overlapt = maten.amigos.filter((a) => a.r > maten.chispa.l && a.l < maten.chispa.r);
  ok(overlapt.length === 3, 'ze staan alle drie bij haar in de compositie, niet eromheen (' + overlapt.length + '/3)');
  const zelfdeGrond = maten.amigos.filter((a) => Math.abs(a.b - maten.chispa.b) < 130);
  ok(zelfdeGrond.length === 3, 'en ze staan op dezelfde grond als zij, niet in een rij eronder');

  // --- 3. Het decor is decor ---
  const decor = await page.evaluate(() => {
    const laag = document.querySelector('.chdecor');
    const items = document.querySelectorAll('.decoritem');
    const eerste = items[0] ? getComputedStyle(items[0]) : null;
    return {
      laag: !!laag,
      erin: laag ? laag.querySelectorAll('.decoritem').length : -1,
      totaal: items.length,
      opacity: eerste ? parseFloat(eerste.opacity) : -1,
      z: eerste ? eerste.zIndex : ''
    };
  });
  ok(decor.laag && decor.totaal > 0, 'er staat decoratie in de kamer');
  ok(decor.erin === decor.totaal, 'alle decoratie zit in de achtergrondlaag (' + decor.erin + '/' + decor.totaal + ')');
  ok(decor.opacity > 0 && decor.opacity < 0.8, 'het decor is naar achteren gezakt in plaats van mee te vechten om aandacht');

  // --- 4. De dansvloer ligt onder haar voeten ---
  await page.evaluate(() => { try { chispaVloer(true); } catch (e) {} });
  await page.waitForTimeout(300);
  const vloer = await page.evaluate(() => {
    const v = document.querySelector('.chvloer');
    const p = document.getElementById('petBox');
    if (!v || !p) return null;
    const rv = v.getBoundingClientRect(), rp = p.getBoundingClientRect();
    return {
      zVloer: parseInt(getComputedStyle(v).zIndex, 10),
      zChispa: parseInt(getComputedStyle(p).zIndex, 10),
      zLaag: getComputedStyle(document.getElementById('chispaProps')).zIndex,
      onderaan: rv.bottom > rp.top + rp.height * 0.5
    };
  });
  ok(!!vloer && vloer.zVloer < vloer.zChispa, 'de dansvloer ligt achter haar (licht onder haar voeten, geen waas over haar buik)');
  ok(!!vloer && vloer.zLaag === 'auto', 'de proppenlaag stapelt zelf niet, zodat elk stuk zijn eigen hoogte kan kiezen');
  ok(!!vloer && vloer.onderaan, 'en hij ligt bij haar voeten, niet bij haar hoofd');
  await page.evaluate(() => { try { chispaVloer(false); } catch (e) {} });

  // --- 5. Als zij danst, dansen zij mee ---
  const voor = await page.evaluate(() => document.getElementById('chScene').className);
  ok(voor.indexOf('baila') === -1, 'in rust staat het gezelschap stil');

  await page.evaluate(() => {
    const b = BAILES.filter(function (x) { return x.id === 'flamenco'; })[0] || BAILES[0];
    chispaBaila(b);
  });
  await page.waitForTimeout(700);
  const tijdens = await page.evaluate(() => {
    const sc = document.getElementById('chScene');
    const svgs = Array.prototype.slice.call(document.querySelectorAll('.amigo:not(.locked) svg'));
    return {
      klas: sc.className,
      anims: svgs.map(function (s) { return getComputedStyle(s).animationName; }),
      vertraging: svgs.map(function (s) { return getComputedStyle(s).animationDelay; }),
      zij: getComputedStyle(chispaBox()).animationName
    };
  });
  ok(tijdens.klas.indexOf('baila') !== -1, 'als het feest begint weet het hele toneel dat');
  ok(tijdens.zij && tijdens.zij !== 'none' && tijdens.zij !== 'chvive',
     'je ziet haar echt dansen op de grote Chispa (' + tijdens.zij + ')');
  ok(tijdens.anims.length === 3 && tijdens.anims.every((a) => a === 'petd'),
     'en de vriendjes dansen met haar mee (' + tijdens.anims.join(', ') + ')');
  // Gelijk op de maat is een machine; net niet gelijk is een gezelschap.
  const uniek = tijdens.vertraging.filter((v, i, arr) => arr.indexOf(v) === i);
  ok(uniek.length === 3, 'ieder begint net iets later, zodat het een gezelschap is en geen machine (' + tijdens.vertraging.join(', ') + ')');

  await page.evaluate(() => { try { chispaStop(); } catch (e) {} });
  await page.waitForTimeout(400);
  const na = await page.evaluate(() => ({
    klas: document.getElementById('chScene').className,
    anims: Array.prototype.map.call(document.querySelectorAll('.amigo:not(.locked) svg'), function (s) { return getComputedStyle(s).animationName; })
  }));
  ok(na.klas.indexOf('baila') === -1 && na.anims.every((a) => a === 'none'),
     'en als het uit is staat iedereen weer stil');

  // --- 6. Een vriendje aantikken stelt hem voor ---
  await page.locator('.amigo:not(.locked)').first().click();
  await page.waitForTimeout(400);
  const bel = await page.evaluate(() => {
    const b = document.getElementById('petBubble');
    return { zichtbaar: !b.classList.contains('hidden'), tekst: b.textContent || '' };
  });
  const namen = await page.evaluate(() => AMIGOS.map(function (a) { return a.naam; }));
  ok(bel.zichtbaar && namen.some((n) => bel.tekst.indexOf(n) !== -1),
     'wie je aantikt stelt zichzelf voor in de tekstballon, in plaats van een bordje onder zich te dragen');

  // --- 7. Geen JS-fouten in eigen code ---
  const eigen = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(eigen.length === 0, 'geen JS-fouten tijdens de hele test (' + eigen.length + ' gevonden)');
  if (eigen.length) eigen.slice(0, 4).forEach((e) => console.log('   ', e));

  await browser.close();
  if (fails === 0) console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
  else { console.log('\n' + fails + ' TESTS GEFAALD'); process.exit(1); }
})();
