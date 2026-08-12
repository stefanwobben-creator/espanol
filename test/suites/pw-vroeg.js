// pw-vroeg.js (12 aug, v23.55) — de vreemde begint na een halve seconde, niet na vijf.
//
// Stefan koos, gevraagd wat erger is: de vreemde die vijf seconden wacht en wegklikt, of Ilona die
// op dag 12 wacht omdat er die ochtend gedeployd is. Het antwoord was de vreemde. Daarom staat het
// proefscherm nu in een eigen klein scriptblok bóven het grote: drie woordjes met twee knoppen is
// 2,3 KB en dat kan mee met de statische HTML.
//
// Wat deze suite bewaakt is niet dat het scherm er mooi uitziet maar de vier beloften eronder:
//
//   1. de eerste vraag staat er vóórdat het grote script bestaat (anders is het hele blok zinloos)
//   2. wat je vóór dat moment antwoordt gaat niet verloren bij de overdracht
//   3. het blok houdt zich koest voor iedereen die geen vreemde is
//   4. er is geen tweede kopie van de proefdata: verhuisd, niet gekopieerd
//
// Meetnotitie, want hier ben ik een keer op ingelopen: gebruik hier géén waitForSelector. Die draait
// in de pagina en kan dus pas iets doen als de hoofddraad vrij is, en die is vanaf ongeveer één
// seconde bezig met het parsen van 800 KB script. Een eerste meting rapporteerde daardoor 5560 ms
// terwijl de knop er al op 567 ms stond. Pollen met evaluate in de gaten tussen de chunks door geeft
// het echte moment.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

async function traag(browser) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions', {
    offline: false, latency: 300,
    downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8
  });
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  return { ctx, page };
}

async function pollTot(page, fn, max) {
  const t0 = Date.now();
  while (Date.now() - t0 < (max || 60000)) {
    const r = await page.evaluate(fn).catch(() => false);
    if (r) return Date.now() - t0;
    await new Promise((r) => setTimeout(r, 50));
  }
  return -1;
}

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM });

  console.log('\n-- de eerste vraag staat er vóór het grote script --');
  let vroegState = null;
  {
    const { ctx, page } = await traag(b);
    const errs = []; page.on('pageerror', (e) => errs.push(e.message));
    page.goto(U, { waitUntil: 'commit' }).catch(() => {});

    const tKnop = await pollTot(page, () => document.querySelectorAll('button[data-proef]').length > 0, 30000);
    const toen = await page.evaluate(() => ({
      groot: typeof window.renderProef === 'function',
      ver: typeof window.APP_VERSIE,
      gordijn: !!document.getElementById('laadScherm'),
      kicker: (document.querySelector('#proefBox .kicker') || {}).textContent || '',
      knoppen: document.querySelectorAll('button[data-proef]').length
    }));
    console.log('  eerste knop in de dom :: ' + tKnop + ' ms');
    ok(tKnop >= 0 && tKnop < 2500, 'de eerste vraag staat er binnen 2,5 seconde (' + tKnop + ' ms)');
    ok(toen.groot === false && toen.ver === 'undefined',
      'en het grote script bestaat op dat moment nog niet — dát is het hele punt');
    ok(toen.knoppen === 2, 'met twee antwoordknoppen');
    ok(/1\/3/.test(toen.kicker), 'en de teller staat op 1/3 (' + toen.kicker.trim() + ')');

    console.log('\n-- wat je vroeg antwoordt overleeft de overdracht --');
    const woord = await page.evaluate(() => {
      const w = PROEF_WOORDEN[proefStand.i];
      document.querySelectorAll('button[data-proef]')[w.c].click();
      return w.es;
    });
    await new Promise((r) => setTimeout(r, 400));
    const naTik = await page.evaluate(() => ({
      uit: (document.getElementById('vroegUit') || {}).innerText || '',
      opgeslagen: localStorage.getItem('espanol-proef-v1'),
      groot: typeof window.renderProef === 'function'
    }));
    console.log('  getikt op "' + woord + '" · opgeslagen :: ' + naTik.opgeslagen);
    ok(naTik.groot === false, 'er is nog steeds geen groot script (de tik was echt vroeg)');
    ok(naTik.uit.length > 0, 'er staat een uitslagregel in het kaartje zelf (' + naTik.uit.trim() + ')');
    let bew = null;
    try { bew = JSON.parse(naTik.opgeslagen); } catch (e) { bew = null; }
    ok(!!(bew && bew.bezig && bew.stand && bew.stand.i === 1),
      'de stand is weggeschreven in het formaat waar renderProef() uit hervat');
    ok(!!(bew && bew.stand && bew.stand.res && Object.keys(bew.stand.res).length === 1),
      'met het antwoord erin');

    await page.waitForFunction(() => typeof window.APP_VERSIE !== 'undefined', { timeout: 90000 });
    await new Promise((r) => setTimeout(r, 1600));
    vroegState = await page.evaluate(() => ({
      i: window.proefStand ? proefStand.i : -1,
      res: window.proefStand ? Object.keys(proefStand.res).length : -1,
      xp: window.proefStand ? proefStand.xp : -1,
      kicker: (document.querySelector('#proefBox .kicker') || {}).textContent || '',
      chispa: !!document.querySelector('#proefBox svg'),
      dubbel: document.querySelectorAll('#proefBox').length
    }));
    console.log('  na overdracht :: ' + vroegState.kicker.trim() + ' · i=' + vroegState.i);
    ok(vroegState.i === 1, 'het grote script hervat op dezelfde vraag en begint niet opnieuw');
    ok(vroegState.res === 1 && vroegState.xp === 2, 'met het vroege antwoord en de punten intact');
    ok(vroegState.dubbel === 1, 'er staat één proefkaart, niet twee');
    ok(vroegState.chispa === true, 'en Chispa verschijnt in het vak dat voor haar was vrijgehouden');
    ok(errs.length === 0, 'geen scriptfouten' + (errs.length ? ' :: ' + errs[0] : ''));
    await ctx.close();
  }

  console.log('\n-- het gordijn gaat open zodra er een vraag staat --');
  {
    const { ctx, page } = await traag(b);
    page.goto(U, { waitUntil: 'commit' }).catch(() => {});
    await pollTot(page, () => document.querySelectorAll('button[data-proef]').length > 0, 30000);
    const t = await pollTot(page, () => !document.getElementById('laadScherm'), 5000);
    const groot = await page.evaluate(() => typeof window.renderProef === 'function');
    ok(t >= 0, 'het laadscherm is weg');
    ok(groot === false, 'en dat gebeurde vóór het grote script, dus niet via boot()');
    await ctx.close();
  }

  console.log('\n-- het blok houdt zich koest voor wie geen vreemde is --');
  /* Dit moet op een geremde verbinding, anders is het venster waarin je het verschil kunt zien maar
     een paar honderd milliseconde breed. En "er staat geen proefkaart" is niet de goede vraag: het
     grote script tekent er zelf ook een (dat is zijn werk). De vraag is of er er een verschijnt
     terwijl het grote script nog niet bestaat, want dan is het vroege blok aan het werk geweest waar
     dat niet hoort. */
  const gevallen = [
    ['proef al klaar', () => localStorage.setItem('espanol-proef-v1', JSON.stringify({ klaar: true, xp: 5 }))],
    ['proef overgeslagen', () => localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true }))],
    ['helling al bezig', () => localStorage.setItem('espanol-proef-v1', JSON.stringify({ bezig: true, stand: { i: 3, xp: 6, res: {} } }))],
    ['er is al een profiel', () => localStorage.setItem('espanol-profiles-v1', JSON.stringify({ active: null, list: [{ name: 'X', key: 'k', track: 'beginner' }] }))],
    ['uitnodigingslink (?uit=)', null]
  ];
  for (const [naam, zet] of gevallen) {
    const { ctx, page } = await traag(b);
    await page.goto(U, { waitUntil: 'commit' });
    await page.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
    if (zet) await page.evaluate(zet);
    page.goto(zet ? U : U + '?uit=abc', { waitUntil: 'commit' }).catch(() => {});
    /* Wachten op een voorwaarde en niet op een vast aantal tikken. In de volle poort draaien vier
       browsers tegelijk op een geremde verbinding, en dan haalt het grote script de vier seconden
       niet die deze lus eerst had. Dat maakte de suite een dobbelsteen: groen solo, rood in de
       poort. Precies het soort test dat je niet wilt hebben. */
    let betrapt = false, gezien = false;
    const tEind = Date.now() + 120000;
    while (Date.now() < tEind) {
      const st = await page.evaluate(() => ({
        box: !!document.getElementById('proefBox'),
        vroeg: !!document.getElementById('vroegUit') || (window.vroegBezig === true),
        groot: typeof window.renderProef === 'function'
      })).catch(() => null);
      if (st) {
        if (!st.groot && (st.box || st.vroeg)) betrapt = true;
        if (st.groot) { gezien = true; break; }
      }
      await new Promise((r) => setTimeout(r, 50));
    }
    ok(gezien && !betrapt, naam + ': het vroege blok tekent niets');
    await ctx.close();
  }

  const page = await b.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  await page.goto(U);

  console.log('\n-- verhuisd, niet gekopieerd --');
  {
    const html = await page.evaluate(async () => (await fetch(location.pathname)).text());
    const tel = (s) => (html.match(new RegExp(s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
    const eenmalig = ['var PROEF_WOORDEN = [', 'var PROEF_TXT = {', 'var UI_LANGS = {',
      'function browserTaal(', 'function proefBewaar(', 'function proefTaal('];
    let mis = [];
    eenmalig.forEach((n) => { if (tel(n) !== 1) mis.push(n + ' (' + tel(n) + 'x)'); });
    ok(mis.length === 0, 'elk verhuisd blok bestaat precies één keer' + (mis.length ? ' — ' + mis.join(', ') : ''));
    ok(tel('function renderProef(') === 1, 'en renderProef() is niet nagebouwd maar hergebruikt');
  }

  await b.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
