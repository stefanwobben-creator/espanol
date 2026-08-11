// v23.39: Adivina, het negende spel. Lingo met je eigen woordenschat.
//
// Wat deze suite vastlegt, en waarom precies dit:
//   - de kleurregel. Een letter die twee keer in je gok staat en een keer in het doel mag een keer
//     oranje worden en niet twee keer. Dat is de enige regel in dit spel die je met blote ogen niet
//     ziet als hij fout is: het voelt gewoon "raar".
//   - de eerste letter krijg je en die kun je niet weggummen. Zonder die letter is een woord van
//     vijf letters in een vreemde taal geen puzzel maar een gok.
//   - een spel duwt een woord tot doosje 3 en niet verder. Dat is SPEL_PLAFOND en het is de afspraak
//     die dit spel eerlijk houdt tegenover de balk op je voortgangspagina.
//   - elke gok telt als beurt. Sinds v23.38 is dat de teller waar je week en je gemeten tijd op
//     staan; een spel dat trackPoging overslaat is een half uur dat nergens terugkomt.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 1000 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Adiv' + Date.now());
  await page.click('button:has-text("A2 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(1000);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true; S.speelAlles = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- de kleurregel --');
  const kleur = await page.evaluate(() => ({
    dubbelGok: adivKleur('sssss', 'casas'),   // twee s in het doel, vijf in de gok
    oranje: adivKleur('sacas', 'casas'),      // verschoven letters
    niets: adivKleur('mmmmm', 'casas')
  }));
  ok(JSON.stringify(kleur.dubbelGok) === JSON.stringify(['weg', 'weg', 'goed', 'weg', 'goed']),
    'vijf keer dezelfde letter levert alleen de twee juiste plekken op (' + kleur.dubbelGok.join(',') + ')');
  ok(JSON.stringify(kleur.oranje) === JSON.stringify(['bijna', 'goed', 'bijna', 'goed', 'goed']),
    'een letter op de verkeerde plek wordt oranje (' + kleur.oranje.join(',') + ')');
  ok(kleur.niets.every((k) => k === 'weg'), 'een letter die er niet in zit blijft grijs');

  console.log('\n-- de vijver --');
  const pool = await page.evaluate(() => {
    const l = adivPool();
    return { n: l.length, fout: l.filter((w) => [5, 6].indexOf(w.plat.length) === -1 || /\s|ñ/.test(w.es)).length,
             zonderId: l.filter((w) => !w.id).length };
  });
  ok(pool.n >= 100, 'er zijn genoeg woorden om mee te spelen (' + pool.n + ')');
  ok(pool.fout === 0, 'alleen losse woorden van vijf of zes letters, zonder ñ');
  ok(pool.zonderId === 0, 'en allemaal met een id, want anders kan het spel je woordjes niet raken');

  console.log('\n-- het scherm is bereikbaar en speelt --');
  await page.evaluate(() => { funView = null; show('speeltuin'); });
  await page.waitForTimeout(400);
  const inMenu = await page.evaluate(() => !!document.getElementById('ftAdiv'));
  ok(inMenu, 'Adivina staat in de speeltuin');
  await page.evaluate(() => { document.getElementById('ftAdiv').click(); });
  await page.waitForTimeout(400);

  // een gecontroleerd doelwoord, anders hangt de test aan het toeval van adivKies()
  const doel = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[0];
    S.srs[w.id] = { box: 1, due: today(), n: 1 };
    S.dagStats = {};
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivBewaar(); renderFunAdivina();
    return { plat: w.plat, id: w.id, nl: w.nl };
  });

  const start = await page.evaluate(() => ({
    nu: adivSpel.nu,
    vakken: document.querySelectorAll('.adivVak').length,
    toetsen: document.querySelectorAll('[data-adivk]').length
  }));
  ok(start.nu.length === 1 && start.nu === doel.plat.charAt(0), 'de eerste letter staat er al');
  ok(start.vakken === 25, 'vijf rijen van vijf vakken (' + start.vakken + ')');
  ok(start.toetsen >= 28, 'er staat een toetsenbord (' + start.toetsen + ' toetsen)');

  console.log('\n-- de eerste letter kun je niet weghalen --');
  await page.evaluate(() => { adivWis(); adivWis(); adivWis(); });
  const naWis = await page.evaluate(() => adivSpel.nu);
  ok(naWis.length === 1, 'wissen stopt bij de eerste letter (' + naWis + ')');

  console.log('\n-- raden gaat via het toetsenbord --');
  // een foute gok van de goede lengte: de rest van het woord omgedraaid
  const gok1 = doel.plat.charAt(0) + doel.plat.slice(1).split('').reverse().join('');
  const anders = gok1 !== doel.plat ? gok1 : doel.plat.slice(0, 4) + (doel.plat.charAt(4) === 'a' ? 'o' : 'a');
  for (const c of anders.slice(1)) {
    await page.evaluate((k) => { document.querySelector("[data-adivk='" + k + "']").click(); }, c);
  }
  const voorRaden = await page.evaluate(() => adivSpel.nu);
  ok(voorRaden === anders, 'de letters komen in het vak terecht (' + voorRaden + ')');
  await page.evaluate(() => { document.querySelector("[data-adivk='@doe']").click(); });
  await page.waitForTimeout(200);
  const na1 = await page.evaluate(() => ({
    gok: adivSpel.gok.slice(), nu: adivSpel.nu, klaar: adivSpel.klaar,
    pog: (S.dagStats[today()] || {}).pogingen || 0, fouten: (S.dagStats[today()] || {}).fouten || 0
  }));
  ok(na1.gok.length === 1 && na1.gok[0] === anders, 'de gok staat op het bord');
  ok(na1.nu.length === 1, 'en de volgende rij begint weer met de eerste letter');
  ok(na1.pog === 1 && na1.fouten === 1, 'de gok telt als beurt, en als foute beurt (' + na1.pog + '/' + na1.fouten + ')');

  console.log('\n-- een gok van de verkeerde lengte doet niets --');
  await page.evaluate(() => { adivSpel.nu = adivSpel.doel.slice(0, 3); adivDoe(); });
  const naKort = await page.evaluate(() => adivSpel.gok.length);
  ok(naKort === 1, 'een half woord wordt niet ingediend');

  console.log('\n-- winnen: punten, doosje, reeks --');
  const win = await page.evaluate(() => {
    const xpVoor = S.txp || 0;
    adivSpel.nu = adivSpel.doel;
    adivDoe();
    return { klaar: adivSpel.klaar, xp: adivSpel.xp, xpErbij: (S.txp || 0) - xpVoor,
             box: (S.srs[adivSpel.id] || {}).box, reeks: S.adiv.reeks, best: S.adiv.best,
             gewonnen: S.adiv.gewonnen, gespeeld: S.adiv.gespeeld,
             pog: (S.dagStats[today()] || {}).pogingen || 0 };
  });
  ok(win.klaar === 1, 'het spel is gewonnen');
  ok(win.xp === 8 && win.xpErbij === 8, 'twee pogingen levert 8 punten op (' + win.xp + ')');
  ok(win.box === 2, 'het woord schuift een doosje op (' + win.box + ')');
  ok(win.reeks === 1 && win.best === 1, 'de reeks staat op 1');
  ok(win.gewonnen === 1 && win.gespeeld === 1, 'de teller klopt (' + win.gewonnen + '/' + win.gespeeld + ')');
  ok(win.pog === 2, 'ook de winnende gok telt als beurt (' + win.pog + ')');

  console.log('\n-- het plafond van doosje 3 geldt ook hier --');
  const plafond = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[1];
    S.srs[w.id] = { box: SPEL_PLAFOND, due: today(), n: 5 };
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivSpel.nu = adivSpel.doel; adivDoe();
    return { box: S.srs[w.id].box, plafond: SPEL_PLAFOND };
  });
  ok(plafond.box === plafond.plafond, 'een woord op het plafond blijft daar (' + plafond.box + ')');

  console.log('\n-- de hint kost de helft --');
  const hint = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[2];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: true, klaar: 0, xp: 0 };
    adivSpel.nu = adivSpel.doel; adivDoe();
    return adivSpel.xp;
  });
  ok(hint === 5, 'in een poging met hint: 5 in plaats van 10 (' + hint + ')');

  console.log('\n-- verliezen laat het woord zien --');
  const verlies = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[3];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    const mis = w.plat.charAt(0) + (w.plat.slice(1).split('').reverse().join('') === w.plat.slice(1)
      ? w.plat.slice(1, 4) + (w.plat.charAt(4) === 'a' ? 'o' : 'a')
      : w.plat.slice(1).split('').reverse().join(''));
    for (let i = 0; i < 5; i++) { adivSpel.nu = mis; adivDoe(); }
    renderFunAdivina();
    const t = document.getElementById('funCard').innerText;
    return { klaar: adivSpel.klaar, gokken: adivSpel.gok.length, es: w.es,
             toont: t.indexOf(w.es) !== -1, kbWeg: document.querySelectorAll('[data-adivk]').length };
  });
  ok(verlies.klaar === -1 && verlies.gokken === 5, 'na vijf pogingen is het klaar');
  ok(verlies.toont, 'en het woord staat er, met zijn accenten (' + verlies.es + ')');
  ok(verlies.kbWeg === 0, 'het toetsenbord is weg als er niets meer te raden valt');

  console.log('\n-- een half spel overleeft een herlading --');
  await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 6)[0];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 6, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivSpel.nu = w.plat.charAt(0) + w.plat.slice(1).split('').reverse().join('');
    if (adivSpel.nu !== w.plat) adivDoe(); else { adivSpel.gok.push(adivSpel.nu); adivBewaar(); }
  });
  await page.reload(); await page.waitForTimeout(900);
  const herstel = await page.evaluate(() => {
    funView = 'adiv'; adivSpel = null; show('speeltuin'); renderFunAdivina();
    return { gokken: adivSpel ? adivSpel.gok.length : -1, len: adivSpel ? adivSpel.len : 0 };
  });
  ok(herstel.gokken === 1 && herstel.len === 6, 'de gedane gok staat er nog na een herlading');

  ok(errors.length === 0, 'geen JS-fouten (' + errors.length + ')' + (errors[0] ? ' ' + errors[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
