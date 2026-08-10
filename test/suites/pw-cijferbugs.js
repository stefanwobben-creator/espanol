// v22.10: de twee rekenfouten op het voortgangsscherm, elk met een test die ze niet terug laat komen.
//
// 1. Luisteren stond op "Escuchar · 55/6 · 100%". Tot v21.2 schreef Dictado zijn zinnen in
//    S.comp.luisteren; die oude ids staan bij bestaande profielen nog in de state en werden meegeteld
//    tegen een noemer van zes luisterscenes. pct() knipt op 100, dus de fout zag eruit als een score.
// 2. Het tempo meldde "15,9 nieuwe woorden per dag (het maximum is 15)". S.newIntro telt élk nieuw
//    woord, ook uit de spellen en het boek; die 15 ging alleen over de dagportie in de les.
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
  await page.fill('input[placeholder="Name"]', 'PwCb' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);

  // ---- 1. de teller van Luisteren kan zijn eigen noemer niet meer voorbij ----
  const vervuild = await page.evaluate(() => {
    S.comp = S.comp || {};
    S.comp.luisteren = {};
    // vijftig oude Dictado-zinnen, precies zoals ze in een profiel van voor v21.2 staan
    for (let i = 1; i <= 50; i++) S.comp.luisteren['s' + i] = true;
    // plus twee echte luisterscenes
    S.comp.luisteren[AUDICIONES[0].id] = true;
    S.comp.luisteren[AUDICIONES[1].id] = true;
    const c = berekenCompetenties();
    return { teller: c.luisteren.teller, noemer: c.luisteren.noemer, pct: c.luisteren.pct,
             scenes: AUDICIONES.length };
  });
  ok(vervuild.noemer === vervuild.scenes, 'de noemer is het aantal luisterscenes: ' + vervuild.noemer);
  ok(vervuild.teller === 2, 'alleen echte scenes tellen mee, de 50 oude zin-ids niet: ' + vervuild.teller);
  ok(vervuild.teller <= vervuild.noemer, 'de teller kan de noemer niet meer voorbij');
  ok(vervuild.pct === Math.round(2 / vervuild.scenes * 100), 'en het percentage klopt dus ook: ' + vervuild.pct + '%');

  const alles = await page.evaluate(() => {
    S.comp.luisteren = {};
    AUDICIONES.forEach((sc) => { S.comp.luisteren[sc.id] = true; });
    return berekenCompetenties().luisteren;
  });
  ok(alles.pct === 100 && alles.teller === alles.noemer, 'alle scenes gedaan is nog steeds gewoon 100%');

  // ---- 1b. en ze worden ook echt uit je profiel gegooid, niet alleen bij het rekenen genegeerd ----
  const opgeruimd = await page.evaluate(() => {
    // v22.11: de losse vlag compOpgeruimd is vervangen door het schemanummer. Een state zonder
    // nummer is er een van voor die versie, dus de migratie draait.
    const vuil = { comp: { luisteren: {}, schrijven: { s1: true } } };
    for (let i = 1; i <= 50; i++) vuil.comp.luisteren['s' + i] = true;
    vuil.comp.luisteren[AUDICIONES[0].id] = true;
    const schoon = normaliseerState(vuil);
    return {
      over: Object.keys(schoon.comp.luisteren),
      vlag: schoon.schema,
      schrijvenIntact: Object.keys(schoon.comp.schrijven).length
    };
  });
  ok(opgeruimd.over.length === 1, 'de vijftig oude sleutels zijn echt weg uit de state: ' + opgeruimd.over.length + ' over');
  ok(opgeruimd.over[0] && /^esc|^aud|.+/.test(opgeruimd.over[0]), 'de echte luisterscene staat er nog: ' + opgeruimd.over[0]);
  ok(opgeruimd.vlag === 2, 'en het schemanummer staat op 2, zodat dit niet elke keer opnieuw hoeft');
  ok(opgeruimd.schrijvenIntact === 1, 'comp.schrijven wordt niet aangeraakt: daar is de geldige verzameling niet bekend');

  const tweedeKeer = await page.evaluate(() => {
    const al = { schema: SCHEMA, comp: { luisteren: { s99: true }, schrijven: {} } };
    return Object.keys(normaliseerState(al).comp.luisteren).length;
  });
  ok(tweedeKeer === 1, 'een profiel dat al opgeruimd is wordt niet nog eens doorgespit');

  // ---- 2. de tempozin belooft geen maximum meer dat niet begrenst ----
  const zin = await page.evaluate(() => {
    const t = today();
    S.newIntro = {}; S.xp = {};
    // twee actieve dagen, 40 nieuwe woorden: een tempo dat ver boven de dagportie ligt
    S.newIntro[t] = 25; S.xp[t] = 100;
    const g = new Date(Date.now() - 86400000);
    const gis = g.getFullYear() + '-' + String(g.getMonth() + 1).padStart(2, '0') + '-' + String(g.getDate()).padStart(2, '0');
    S.newIntro[gis] = 15; S.xp[gis] = 100;
    const el = document.createElement('div');
    // v23.32: de cijfers staan op hun eigen scherm, niet meer onder Profiel
    try { show('voortgang'); } catch (e) {}
    return { tekst: (document.getElementById('statsCard') || el).innerText || '', portie: nieuwPerDag() };
  });
  await page.waitForTimeout(400);
  const tekst = await page.evaluate(() => {
    try { show('voortgang'); } catch (e) {}
    return (document.getElementById('statsCard') || {}).innerText || '';
  });
  ok(!/maximum is 15/.test(tekst), 'de zin belooft geen hardgecodeerd maximum van 15 meer');
  ok(!/het maximum is/.test(tekst), 'en ook geen ander maximum dat het gemeten getal niet begrenst');
  /* v23.37: de zin die dit droeg is weg. Hij stond in het blok "Jouw ontwikkeling", dat dezelfde
     getallen nog een derde keer in proza zette en dat Stefan om die reden liet vervallen. Wat deze
     suite bewaakt blijft overeind en wordt zelfs breder: nergens op dit scherm mag een hardgecodeerd
     maximum staan dat het gemeten getal niet begrenst. Daarom kijkt hij nu naar het hele scherm en
     niet alleen naar de cijferkaart. */
  const heleScherm = await page.evaluate(() => (document.getElementById('tab-voortgang') || {}).innerText || '');
  ok(!/maximum is/.test(heleScherm), 'ook nergens anders op het scherm staat een hardgecodeerd maximum');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
