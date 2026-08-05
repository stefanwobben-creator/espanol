// Playwright-test voor v19.81: kiezen, zien en horen.
//
// Stefan: "op een tpas klikken is niet direct geven", "dansje klikken chispa dans niet in de versei
// die blijft staan in de sticky header en ook de muziek hoor ik niet", "Bij dans bijv is leuk als
// ze helemaal van links naar rehts gaat en weer terug bijv en de sticky header mag ook nog wat
// groter, kan bij wel 1,5 keer zo groot zijn als nu".
//
// Wat hier vastligt, in dezelfde volgorde als hij het opschreef:
//   1. een tapa aantikken voert hem echt (voorraad omlaag, menu bij, toast)
//   2. de balk is anderhalf keer zo groot, dus een dans van dertien pixels is weer te zien
//   3. tijdens een dans reist ze door de hele breedte, op het podium waar je op dat moment kijkt
//   4. er start muziek, en er is een knop om dat tegen te houden
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

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwBaile' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  await page.evaluate(() => {
    window.chispaSlaapt = function () { return false; };
    window.petMoodKey = function () { return 'happy'; };
    S.txp = 30000;
    S.tapas = 6;
    S.tapaMenu = [];
    try { zorgState().wensOp = today(); } catch (e) {} // anders krijg je de tapa soms terug
    show('chispa');
  });
  await page.waitForTimeout(1200);
  await page.evaluate(() => { try { chispaStop(); } catch (e) {} });
  await page.waitForTimeout(300);

  // --- 1. Een tapa aantikken is hem geven ---
  const chips = page.locator('#tapaMenu button.tapachip, button.tapachip');
  ok(await chips.count() > 0, 'het menu staat er met aanklikbare tapas');
  // Bewust niet de eerste: als de app stiekem toch zelf koos, valt dat dan meteen op.
  const doel = await page.evaluate(() => {
    const bs = document.querySelectorAll('button.tapachip');
    const b = bs[bs.length - 1];
    return b ? b.getAttribute('data-tapa') : null;
  });
  const voorraadVoor = await page.evaluate(() => S.tapas || 0);
  await page.locator('button.tapachip[data-tapa="' + doel + '"]').click();
  await page.waitForTimeout(700);
  const na = await page.evaluate(() => ({
    tapas: S.tapas || 0,
    menu: (S.tapaMenu || []).slice(),
    toast: (document.getElementById('toast') || {}).textContent || ''
  }));
  ok(na.tapas === voorraadVoor - 1, 'aantikken voert haar echt: er gaat een tapa af (' + voorraadVoor + ' → ' + na.tapas + ')');
  ok(na.menu.indexOf(doel) !== -1, 'en juist de tapa die jij aanwees staat nu op het menu (' + doel + ')');

  // --- 2. De balk is anderhalf keer zo groot ---
  // v19.80: stage 84x76, svg 80x73. Stefan vroeg om 1,5x. Onder deze grenzen is een dans van
  // dertien pixels weer onzichtbaar, en dat was precies zijn klacht.
  await page.evaluate(() => { window.scrollTo(0, 1400); });
  await page.waitForTimeout(700);
  const balk = await page.evaluate(() => {
    const st = document.querySelector('.chbalkstage');
    const sv = document.querySelector('#balkBox svg');
    return {
      aan: chispaBalkAan(),
      stage: st ? { w: st.getBoundingClientRect().width, h: st.getBoundingClientRect().height } : null,
      svg: sv ? { w: sv.getBoundingClientRect().width, h: sv.getBoundingClientRect().height } : null
    };
  });
  ok(balk.aan, 'de sticky balk staat aan als je bij de knoppen bent (anders valt er niets te zien)');
  ok(!!balk.svg && balk.svg.w >= 112 && balk.svg.h >= 102,
     'Chispa in de balk is ~1,5x zo groot geworden (' + Math.round((balk.svg || {}).w) + 'x' + Math.round((balk.svg || {}).h) + ', was 80x73)');
  ok(!!balk.stage && balk.stage.h >= 104,
     'en haar podium is meegegroeid (' + Math.round((balk.stage || {}).h) + 'px hoog, was 76)');
  ok(!!balk.stage && balk.stage.w > 126,
     'het podium rekt mee met de breedte van het scherm, zodat "helemaal naar links" overal klopt (' + Math.round((balk.stage || {}).w) + 'px)');

  // --- 3. Tijdens een dans reist ze door de breedte ---
  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(500);
  const reis = await page.evaluate(() => {
    const l = document.getElementById('balkViaje');
    const cs = l ? getComputedStyle(l) : null;
    return {
      klas: l ? l.className : '',
      anim: cs ? cs.animationName : '',
      play: cs ? cs.animationPlayState : '',
      reis: cs ? cs.getPropertyValue('--reis').trim() : '',
      dansKlas: (chispaBox() || {}).className || '',
      dansAnim: chispaBox() ? getComputedStyle(chispaBox()).animationName : ''
    };
  });
  ok(reis.klas.indexOf('viaja') !== -1 && reis.anim === 'chviaje' && reis.play === 'running',
     'ze gaat op reis op het podium waar je naar kijkt (' + reis.anim + ', ' + reis.play + ')');
  ok(parseFloat(reis.reis) >= 20,
     'en die reis is gemeten aan de echte breedte, niet een symbolisch duwtje (' + reis.reis + ')');
  // Dit is de kern van de oplossing: twee transforms die samenvallen in plaats van elkaar te
  // overschrijven. Danst ze niet meer terwijl ze reist, dan is de reis een regressie.
  ok(reis.dansAnim && reis.dansAnim !== 'none' && reis.dansAnim !== 'chvive',
     'terwijl ze reist danst ze gewoon door (' + reis.dansAnim + ')');

  // Ze komt van links naar rechts en weer terug: drie metingen, drie verschillende plekken.
  const posities = [];
  for (let i = 0; i < 9; i++) {
    posities.push(await page.evaluate(() => {
      const b = document.getElementById('balkBox');
      return b ? Math.round(b.getBoundingClientRect().left) : 0;
    }));
    await page.waitForTimeout(320);
  }
  const spreiding = Math.max.apply(null, posities) - Math.min.apply(null, posities);
  ok(spreiding >= 40, 'ze legt echt een afstand af van links naar rechts (' + spreiding + 'px spreiding: ' + posities.join(', ') + ')');

  await page.evaluate(() => { try { chispaStop(); } catch (e) {} });
  await page.waitForTimeout(300);
  const stil = await page.evaluate(() => {
    const a = document.getElementById('balkViaje'), b = document.getElementById('chispaViaje');
    return [a ? a.className : '', b ? b.className : ''].join(' | ');
  });
  ok(stil.indexOf('viaja') === -1,
     'en als het uit is reist er niets meer door, op geen van beide podia (' + stil + ')');

  // --- 4. Er is muziek, en er is een knop om het stil te houden ---
  const muz = await page.evaluate(() => ({
    tabel: typeof BAILE_MUZIEK === 'object' && Object.keys(BAILE_MUZIEK).length,
    dansen: BAILES.length,
    knop: !!document.getElementById('btnChMuziek'),
    label: (document.getElementById('btnChMuziek') || {}).textContent || ''
  }));
  ok(muz.tabel === muz.dansen, 'elke dans heeft zijn eigen muziek (' + muz.tabel + '/' + muz.dansen + ')');
  ok(muz.knop, 'en er staat een geluidsknop bij de dansen');

  // De knop moet echt iets doen: aan -> uit -> geen enkele noot meer.
  await page.locator('#btnChMuziek').click();
  await page.waitForTimeout(300);
  const uit = await page.evaluate(() => ({
    stil: !!S.chispaStil,
    label: document.getElementById('btnChMuziek').textContent,
    geplandeMs: baileMuziek('salsa', 4400)
  }));
  ok(uit.stil && uit.geplandeMs === 0, 'uitzetten betekent echt stil: er wordt geen noot meer ingepland');
  ok(uit.label !== muz.label, 'en de knop laat zien in welke stand hij staat (' + muz.label.trim() + ' → ' + uit.label.trim() + ')');

  await page.locator('#btnChMuziek').click();
  await page.waitForTimeout(300);
  const weer = await page.evaluate(() => ({ stil: !!S.chispaStil, ms: baileMuziek('flamenco', 4400) }));
  ok(!weer.stil && weer.ms > 0, 'en weer aanzetten plant de maten van de flamenco gewoon opnieuw in (' + weer.ms + 'ms)');
  await page.evaluate(() => { try { chMuziekUit(); } catch (e) {} });

  // --- 5. Geen JS-fouten in eigen code ---
  const eigen = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(eigen.length === 0, 'geen JS-fouten tijdens de hele test (' + eigen.length + ' gevonden)');
  if (eigen.length) eigen.slice(0, 4).forEach((e) => console.log('   ', e));

  await browser.close();
  if (fails === 0) console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
  else { console.log('\n' + fails + ' TESTS GEFAALD'); process.exit(1); }
})();
