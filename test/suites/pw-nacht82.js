// Playwright-test voor v19.82: "als ik op een een dans klik, dan gebeurt er hier nu niks".
//
// Stefan stuurde die zin om 04:19 's nachts, met een schermafdruk van de sticky balk erbij. Er
// gebeurde wel iets: Chispa sliep, en ze zei keurig "Zzz... manana bailamos" - in de tekstballon
// van haar kamer, duizenden pixels onder de balk waar hij op dat moment stond te kijken. Dus voor
// hem gebeurde er letterlijk niets.
//
// Twee dingen liggen hier vast:
//   1. wat ze zegt komt aan op het podium waar je haar ziet (de balk heeft nu een eigen ballon)
//   2. slapen is geen doodlopende weg meer: van muziek wordt ze wakker, ze danst, en daarna
//      gaat ze weer slapen
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

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwNacht' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  await page.evaluate(() => {
    window.petMoodKey = function () { return 'happy'; };
    S.txp = 30000;
    S.tapas = 6;
    S.chispaStil = false;
    show('chispa');
  });
  await page.waitForTimeout(1000);
  await page.evaluate(() => { try { chispaStop(); } catch (e) {} });
  await page.waitForTimeout(200);

  // --- 1. Haar nachtrust bestaat nog, maar je kunt haar wekken ---
  const rust = await page.evaluate(() => ({
    nacht: chispaSlaapt(3),
    laat: chispaSlaapt(23),
    dag: chispaSlaapt(12),
    wakker: typeof chispaWakker === 'function',
    herstel: typeof chispaSlaapHerstel === 'function'
  }));
  ok(rust.nacht && rust.laat && !rust.dag, 'ze slaapt nog steeds van elf tot zeven: dat eigen ritme maakt haar levend');
  ok(rust.wakker && rust.herstel, 'maar er is nu een manier om haar te wekken, en om haar daarna weer te laten slapen');

  const gewekt = await page.evaluate(() => {
    chispaWakker(4000);
    return { nu: chispaSlaapt(), drie: chispaSlaapt(3) };
  });
  ok(gewekt.nu === false, 'na wakker maken is ze wakker, ook al is het midden in de nacht');
  ok(gewekt.drie === true, 'en "slaapt ze normaal om drie uur" blijft gewoon ja: de klok is niet verbogen');

  // --- 2. Op een dans klikken doet ook 's nachts iets, en je ziet het in de balk ---
  // Vanaf hier doen we alsof het 04:19 is, precies het moment van zijn schermafdruk.
  await page.evaluate(() => {
    window.chispaSlaapt = function (uur) { return uur === undefined ? true : (uur >= 23 || uur < 7); };
  });
  await page.evaluate(() => { window.scrollTo(0, 1400); });
  await page.waitForTimeout(700);

  const balkAan = await page.evaluate(() => chispaBalkAan());
  ok(balkAan, 'de sticky balk staat aan bij de dansknoppen (anders valt er niets te missen)');

  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(500);

  const nacht = await page.evaluate(() => {
    const bal = document.getElementById('balkBubble');
    const pet = document.getElementById('petBubble');
    const laag = document.getElementById('balkViaje');
    const r = bal ? bal.getBoundingClientRect() : null;
    return {
      balZichtbaar: !!bal && !bal.classList.contains('hidden'),
      balTekst: bal ? bal.textContent.trim() : '',
      petVerborgen: !pet || pet.classList.contains('hidden'),
      inBeeld: !!r && r.top >= 0 && r.top < 400 && r.width > 100,
      viaja: laag ? laag.className.indexOf('viaja') !== -1 : false,
      danst: chispaBox() ? getComputedStyle(chispaBox()).animationName : '',
      pijl: bal ? bal.style.getPropertyValue('--pijl') : ''
    };
  });
  ok(nacht.balZichtbaar && nacht.balTekst.length > 0,
     'ze antwoordt in de balk waar je staat te kijken (' + nacht.balTekst.slice(0, 40) + ')');
  ok(nacht.petVerborgen, 'en niet tegelijk in de kamer beneden, waar op dat moment niemand kijkt');
  ok(nacht.inBeeld, 'die ballon staat ook echt in beeld, vlak onder de balk');
  ok(!/Zzz/.test(nacht.balTekst), 'het is geen afwijzing meer: geen "Zzz, morgen dansen we" (' + nacht.balTekst.slice(0, 30) + ')');
  ok(nacht.viaja, 'ze gaat er ook echt van dansen en reizen, midden in de nacht');
  ok(nacht.danst && nacht.danst !== 'none' && nacht.danst !== 'chvive',
     'met een echte dansanimatie erbij (' + nacht.danst + ')');
  ok(parseFloat(nacht.pijl) > 0, 'en het pijltje van de ballon wijst naar waar ze staat (' + nacht.pijl + ')');

  // --- 3. Beneden in de kamer praat ze gewoon in haar eigen ballon ---
  await page.evaluate(() => { try { chispaStop(); } catch (e) {} window.scrollTo(0, 0); });
  await page.waitForTimeout(700);
  const kamer = await page.evaluate(() => {
    chispaSay({ es: 'Prueba', nl: 'Test', en: 'Test' });
    const bal = document.getElementById('balkBubble');
    const pet = document.getElementById('petBubble');
    return {
      balkAan: chispaBalkAan(),
      pet: !!pet && !pet.classList.contains('hidden'),
      bal: !!bal && !bal.classList.contains('hidden')
    };
  });
  ok(!kamer.balkAan && kamer.pet && !kamer.bal,
     'sta je bij Chispa zelf, dan praat ze daar en niet in een balk die je niet ziet');

  // --- 4. De geluidsknop zegt een stand, geen opdracht ---
  const knop = await page.evaluate(() => {
    const b = document.getElementById('btnChMuziek');
    return b ? { tekst: b.textContent.trim(), titel: b.title } : null;
  });
  ok(!!knop && /staat|is (on|off)/.test(knop.tekst),
     'de geluidsknop beschrijft een stand in plaats van een opdracht (' + (knop || {}).tekst + ')');
  ok(!!knop && knop.titel.length > 0,
     'en de titel vertelt wat een tik doet (' + (knop || {}).titel + ')');

  await page.evaluate(() => { try { chMuziekUit(); } catch (e) {} });

  const eigen = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(eigen.length === 0, 'geen JS-fouten tijdens de hele test (' + eigen.length + ' gevonden)');
  if (eigen.length) eigen.slice(0, 4).forEach((e) => console.log('   ', e));

  await browser.close();
  if (fails === 0) console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
  else { console.log('\n' + fails + ' TESTS GEFAALD'); process.exit(1); }
})();
