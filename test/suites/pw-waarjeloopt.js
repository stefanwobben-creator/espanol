// pw-waarjeloopt.js (20 aug, v23.145) — telt de app waar je loopt, en doet hij er iets mee?
//
// WAAROM DIT ER IS
//
// Stefan: "Ja zodat we alleen het beste behouden."
//
// Om alleen het beste te behouden moet je weten wat het beste is. Uit de meting van 20 aug: van elf
// onderdelen, waaronder alle spellen en het boek, staat er in zesentwintig dagen geen enkel gegeven,
// van niemand. De app registreerde alleen waar je struikelt (het foutenlogboek), niet waar je loopt.
// Een spel waarin je geen fout kúnt maken laat per definitie geen spoor na.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ELKE OVERGANG WORDT GETELD. Een tab, een spel, een grammaticales: alle drie komen langs
//      navPush() en alle drie krijgen een naam en een teller.
//   2. EN HIJ GAAT MEE NAAR DE SERVER. Een teller die alleen op je toestel staat is geen meting.
//   3. MAAR HIJ SCHRIJFT NIET BIJ ELKE TIK. Alleen de eerste keer per dag kost een schrijfactie.
//      Anders kost bladeren evenveel als leren.
//   4. EN HIJ WORDT GELEZEN. Dit is de belangrijkste: drie keer eerder bleek iets verzameld te
//      worden dat nooit gelezen werd. Het spel van vandaag is dat wat je het langst niet opende, en
//      dat weet hij hiervan.
//   5. DE SPEELTUIN STAAT NIET MEER VOL. Drie tegels vooraan, de rest achter één regel, en niets is
//      weg: de knop brengt ze terug.
//   6. WAT NOG NIET KAN BLIJFT STAAN. Open of dicht: de grijze lijst met de eis erbij verandert niet.
//      Verdwijnen is geen opruimen.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door alles te tellen en er niets mee te doen: dan klopt punt 1 en
// is punt 4 leeg. Daarom wordt gemeten dat de keuze van het spel verspringt als de teller verandert,
// en dat hij binnen dezelfde dag juist niet verspringt.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwWl' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl'; S.speelAlles = true; S.spelAlles = false;
    S.gezien = {};

    // ---- 1. elke overgang wordt geteld ----
    uit.namen = {
      tab: gezienNaam({ t: 'tab', id: 'woorden' }),
      spel: gezienNaam({ t: 'fun', v: 'mem' }),
      gram: gezienNaam({ t: 'gramwiz', id: 'concept-genero' }),
      lees: gezienNaam({ t: 'gclees', id: 'genero' }),
      onzin: gezienNaam({ t: 'iets-anders' })
    };
    show('woorden'); show('woorden'); show('lezen');
    navPush({ t: 'fun', v: 'mem' });
    uit.geteld = JSON.parse(JSON.stringify(S.gezien));

    // ---- 3. maar niet bij elke tik opslaan ----
    let schrijf = 0;
    const echtePersist = persist;
    persist = function () { schrijf++; return echtePersist.apply(this, arguments); };
    S.gezien = {};
    navPush({ t: 'fun', v: 'ws' });        // eerste keer vandaag: één schrijfactie
    uit.schrijfEerst = schrijf;
    navPush({ t: 'fun', v: 'ws' });
    navPush({ t: 'fun', v: 'ws' });        // zelfde dag, zelfde plek: geen extra
    uit.schrijfDaarna = schrijf;
    uit.wsN = S.gezien['spel:ws'].n;
    persist = echtePersist;

    // ---- 2. en hij gaat mee naar de server ----
    let verstuurd = null;
    const echteApi = api;
    api = function (pad, m, body) { if (pad === '/api/log') verstuurd = body; return Promise.resolve(null); };
    logServer('proef', {});
    api = echteApi;
    uit.naarServer = verstuurd && verstuurd.payload ? Object.keys(verstuurd.payload.gezien || {}) : null;

    // ---- 4. en hij wordt gelezen ----
    const kand = speelTegels().filter(function (g) { return SPEL_ROTEERT_NIET.indexOf(g.v) === -1 && speelKlaar(g.v); });
    // Palabra Duel heeft een tweede speler nodig: vooraan zetten belooft iets dat je alleen niet kunt
    S.gezien = {}; S.gezien['spel:duel'] = { n: 0, l: '' };
    uit.duelNooit = (spelVanVandaag() || {}).v !== 'duel';
    uit.kandidaten = kand.map(function (g) { return g.v; });
    S.gezien = {};
    kand.forEach(function (g) { S.gezien['spel:' + g.v] = { n: 1, l: '2026-08-19' }; });
    const oudste = kand[kand.length - 1];
    S.gezien['spel:' + oudste.v] = { n: 1, l: '2020-01-01' };
    uit.gekozen = (spelVanVandaag() || {}).v;
    uit.oudste = oudste.v;
    uit.stabiel = (spelVanVandaag() || {}).v === (spelVanVandaag() || {}).v;
    // en als die van gisteren is, verspringt hij
    S.gezien['spel:' + oudste.v] = { n: 2, l: today() };
    uit.naSpelen = (spelVanVandaag() || {}).v;

    // ---- 5 en 6. de Speeltuin staat niet meer vol ----
    S.gezien = {};
    funView = null; show('speeltuin'); renderFun();
    const el = document.getElementById('funCard');
    uit.dichtN = el.querySelectorAll('.lesson[id]').length;
    uit.dichtKop = /Het spel van vandaag/.test(el.textContent);
    uit.knop = !!document.getElementById('spelMeer');
    uit.knopTekst = uit.knop ? document.getElementById('spelMeer').textContent : '';
    uit.grijsDicht = el.querySelectorAll(".lesson[style*='opacity']").length;
    document.getElementById('spelMeer').click();
    const el2 = document.getElementById('funCard');
    uit.openN = el2.querySelectorAll('.lesson[id]').length;
    uit.grijsOpen = el2.querySelectorAll(".lesson[style*='opacity']").length;
    uit.alleTegels = speelTegels().filter(function (g) { return speelKlaar(g.v); }).length;
    S.spelAlles = false;
    return uit;
  });

  console.log('\n-- 1. elke overgang wordt geteld --');
  console.log('   ' + JSON.stringify(r.namen));
  ok(r.namen.tab === 'woorden', 'een tab heet naar zichzelf');
  ok(r.namen.spel === 'spel:mem', 'een spel krijgt zijn eigen voorvoegsel');
  ok(r.namen.gram === 'gramles' && r.namen.lees === 'gramlezen', 'grammatica oefenen en lezen zijn twee dingen');
  ok(r.namen.onzin === null, 'en iets zonder naam wordt niet geteld');
  ok(r.geteld.woorden && r.geteld.woorden.n === 2, 'twee keer naar de woordjes is twee (nu: ' + JSON.stringify(r.geteld.woorden) + ')');
  ok(!!r.geteld.lezen && !!r.geteld['spel:mem'], 'lezen en het spel staan er ook');
  ok(r.geteld.woorden.l && r.geteld.woorden.l.length === 10, 'met de datum van de laatste keer erbij');

  console.log('\n-- 2. en hij gaat mee naar de server --');
  ok(!!r.naarServer && r.naarServer.length > 0, 'het logje draagt de teller mee (' + (r.naarServer || []).join(',') + ')');

  console.log('\n-- 3. maar hij schrijft niet bij elke tik --');
  ok(r.schrijfEerst === 1, 'de eerste keer vandaag kost één schrijfactie (' + r.schrijfEerst + ')');
  ok(r.schrijfDaarna === 1, 'de twee keer erna kosten er nul (' + r.schrijfDaarna + ')');
  ok(r.wsN === 3, 'maar er is wel drie keer geteld (' + r.wsN + ')');

  console.log('\n-- 4. het controlegeval: en hij wordt gelezen --');
  console.log('   kandidaten: ' + r.kandidaten.join(',') + ' · gekozen: ' + r.gekozen);
  ok(r.gekozen === r.oudste, 'het spel van vandaag is dat wat je het langst niet opende (' + r.gekozen + ')');
  ok(r.stabiel, 'en hij verspringt niet onder je handen binnen dezelfde dag');
  ok(r.naSpelen !== r.oudste, 'speel je hem, dan komt er een ander (' + r.naSpelen + ')');
  ok(r.duelNooit, 'en Palabra Duel is nooit het spel van vandaag: die kun je niet alleen');

  console.log('\n-- 5. de Speeltuin staat niet meer vol --');
  ok(r.dichtN <= 3, 'er staan hoogstens drie tegels vooraan (nu: ' + r.dichtN + ' van ' + r.alleTegels + ')');
  ok(r.dichtKop, 'met erboven welk spel dat van vandaag is');
  ok(r.knop, 'en een regel die de rest terugbrengt ("' + r.knopTekst + '")');
  ok(r.openN === r.alleTegels, 'die dan ook echt alles laat zien (' + r.openN + ')');
  ok(r.openN > r.dichtN, 'dus er is echt iets ingeklapt');

  console.log('\n-- 6. wat nog niet kan blijft staan --');
  ok(r.grijsDicht === r.grijsOpen, 'de grijze lijst verandert niet mee (' + r.grijsDicht + ' / ' + r.grijsOpen + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
