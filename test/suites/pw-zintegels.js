// Playwright-test voor tegels bij Vertalen en de luisterknop (7 aug, v21.3). Stefan zag zelf dat
// Vertalen, Husselen en Dictado één oefening met opties zijn. Dit is de eerste helft van dat
// opruimen: Vertalen krijgt de tegelstand erbij, zodat de meerkeuze tussen vier hele zinnen en het
// losse Husselen in de volgende versie weg kunnen. Bewaakt hier: drie treden met drie prijzen, het
// antwoord loopt door de bestaande controle (geen tweede controlemachine), alleen zelf typen telt
// mee voor schrijfvaardigheid, en de luisterknop staat er pas nadat je geantwoord hebt.
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
  await page.fill('input[placeholder="Name"]', 'PwZTegel' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  await page.evaluate(() => { show('vertalen'); });
  await page.waitForTimeout(400);

  // ---- 1. drie treden, en alleen bij zinnen ----
  // v21.4: de meerkeuze tussen vier hele zinnen is weg, want die kon je raden op lengte. Er blijven
  // twee treden over: tegels leggen en zelf typen.
  ok(await page.locator('#sModus .modus-toets').count() === 2, 'Vertalen heeft twee treden');
  const treden = await page.evaluate(() => Array.from(document.querySelectorAll('#sModus .modus-toets')).map(b => b.getAttribute('data-m')));
  ok(treden.join(',') === 'tegels,moeilijk', 'de treden zijn tegels en typen (' + treden.join(',') + ')');
  const woordRij = await page.evaluate(() => moeilijkModusHtml('x', 'makkelijk'));
  ok(/data-m='makkelijk'/.test(woordRij), 'zonder de tegelvlag blijft makkelijk bestaan (woordjes, Conjugador)');
  ok(!/data-m='tegels'/.test(woordRij), 'en komt de tegelstand daar niet opdagen');
  // een oude opgeslagen keuze mag niet op een verdwenen stand blijven staan
  const oud = await page.evaluate(() => {
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.zin = 'makkelijk';
    const m = sHuidigeModus(sIdx);
    delete S.modusKeuze.zin;
    return m;
  });
  ok(oud === 'tegels', 'een oude keuze "makkelijk" leest nu als tegels (' + oud + ')');

  // ---- 2. de tegelstand rendert, met afleiders en zonder invoerveld ----
  await page.evaluate(() => {
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.zin = 'tegels'; sModusOverride = 'tegels';
    zTegel = null; renderSentenceBody();
  });
  await page.waitForTimeout(300);
  ok(await page.locator('.dtegel[data-zbank]').count() > 0, 'de tegelbank staat op het scherm');
  ok(await page.locator('#sInput[type=hidden]').count() === 1, 'het invoerveld is verborgen: je kunt niet typen');
  const afl = await page.evaluate(() => ({
    bank: zTegel.bank.length,
    echt: zTegel.bank.filter(t => t.echt).length,
    nep: zTegel.bank.filter(t => !t.echt).length
  }));
  // Er ligt er altijd minstens een: zonder afleider zijn alle tegels goed en is de opgave op te
  // lossen zonder te lezen. Levert de conceptmachine er geen (korte zin zonder conceptwoord), dan
  // valt hij terug op een echt Spaans woord uit een andere zin.
  ok(afl.nep >= 1 && afl.nep <= 3, 'er liggen 1 tot 3 afleiders bij (' + afl.nep + ' van ' + afl.bank + ')');
  const kort = await page.evaluate(() => {
    const t = dicSleepTegels('Vivo en Madrid');
    return dicSleepAfleiders(t).length;
  });
  ok(kort >= 1, 'ook een korte zin zonder conceptwoord krijgt een afleider (' + kort + ')');
  ok(afl.echt === afl.bank - afl.nep, 'de rest zijn de echte woorden van de zin');

  // aantikken en weer weghalen
  await page.click('.dtegel[data-zbank]:not(.weg)');
  await page.waitForTimeout(150);
  ok(await page.locator('.dtegel[data-zrij]').count() === 1, 'een aangetikte tegel verschijnt in de antwoordrij');
  await page.click('.dtegel[data-zrij]');
  await page.waitForTimeout(150);
  ok(await page.locator('.dtegel[data-zrij]').count() === 0, 'nog eens aantikken haalt hem weg');

  // ---- 3. goed leggen loopt door de bestaande controle ----
  const uit = await page.evaluate(() => {
    const s = sIdx;
    const voorXp = S.xp[today()] || 0;
    const voorSchrijven = Object.keys(S.comp.schrijven || {}).length;
    zTegel.rij = [];
    dicSleepTegels(s.es).forEach(function (w) {
      for (var i = 0; i < zTegel.bank.length; i++) {
        if (zTegel.bank[i].woord === w && zTegel.rij.indexOf(i) === -1) { zTegel.rij.push(i); break; }
      }
    });
    document.getElementById('btnZTegelCheck').click();
    return {
      done: !!S.done[s.id],
      xpErbij: (S.xp[today()] || 0) - voorXp,
      schrijvenErbij: Object.keys(S.comp.schrijven || {}).length - voorSchrijven,
      id: s.id
    };
  });
  ok(uit.done === true, 'de zin telt als gehaald');
  ok(uit.xpErbij === 3, 'tegels leveren 3 tacos op, tussen meerkeuze (2) en typen (5) in (' + uit.xpErbij + ')');
  ok(uit.schrijvenErbij === 0, 'tegels tellen niet mee voor schrijfvaardigheid: leggen is herkennen, geen produceren');

  // ---- 4. de luisterknop staat er pas na het antwoord ----
  ok(await page.locator('#btnZinLuister').count() === 1, 'na het antwoord staat er een luisterknop');
  ok(await page.locator('#btnZinLuisterLento').count() === 1, 'en een langzame variant');
  const paden = await page.evaluate(() => {
    const echt = Audio;
    let gevraagd = '';
    window.Audio = function (src) { gevraagd = src; return { play: function () { return { catch: function () {} }; }, pause: function () {}, playbackRate: 1 }; };
    zinSpreek(sIdx, 1);
    window.Audio = echt;
    return gevraagd;
  });
  ok(paden === 'audio/dictado/' + uit.id + '.mp3', 'de knop speelt de bestaande opname van die zin (' + paden + ')');

  await page.evaluate(() => { S.modusKeuze.zin = 'moeilijk'; sModusOverride = 'moeilijk'; renderSentence(true); });
  await page.waitForTimeout(300);
  ok(await page.locator('#btnZinLuister').count() === 0, 'voordat je geantwoord hebt staat de luisterknop er niet');

  // ---- 5. typen telt wel mee voor schrijven ----
  const typen = await page.evaluate(() => {
    const s = sIdx;
    const voor = Object.keys(S.comp.schrijven || {}).length;
    document.getElementById('sInput').value = s.es;
    checkSentence();
    return Object.keys(S.comp.schrijven || {}).length - voor;
  });
  ok(typen === 1, 'zelf typen telt wel mee voor schrijfvaardigheid');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
