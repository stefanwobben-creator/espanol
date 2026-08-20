// pw-gramtab.js (16 aug, v23.124) — woont grammatica op de Grammatica-tab?
//
// WAAROM DIT ER IS
//
// Stefan, met twee schermafbeeldingen naast elkaar: "er staan nu dingen verspreid bij Spelen en
// dingen bij Grammatica. Zijn ze op elkaar afgestemd? Het moet sowieso niet bij Spelen maar bij
// Grammatica." En een dag later, toen hij de route zocht die hij net geïnstalleerd had: "hoe heet
// ie dan? ik vind hem niet."
//
// Hij keek op de tab die Grammatica heet. De route heette óók Grammatica, stond elfde in de
// Speeltuin tussen Crucigrama en Memory, en de tab wist niet dat hij bestond.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. GEEN GRAMMATICA IN DE SPEELTUIN. Wie gram:true draagt staat daar niet meer. Dit is de hele
//      reden dat deze ronde bestaat, dus dit is de eerste meting.
//   2. EN WEL OP DE GRAMMATICA-TAB. Weghalen zonder ergens neerzetten is verstoppen, en dat is de
//      fout die de onboarding in v23.45 maakte.
//   3. DE ROUTEKAART LEEST DE DATA. De regel "Nu: ..." komt uit GRAM_PADEN en niet uit een vaste
//      tekst: verzet de stand en de kaart verzet mee.
//   4. TERUG KOMT UIT WAAR JE VANDAAN KWAM. Uit een grammatica-oefening op de Grammatica-tab, uit
//      een spel in de Speeltuin. Dat tweede staat er als controle: een verhuizing mag het oude
//      gedrag niet meenemen.
//   5. DE BALK SPRINGT NIET OM. Oefenen blijft oplichten zolang je in een grammatica-oefening zit,
//      ook al woont het scherm technisch in de speeltuinkaart.
//   6. DE DAGKAART BIEDT GEEN GRAMMATICA AAN. Dat stond in een tweede handgeschreven lijst
//      (DAGSPEL_UIT) en is nu afgeleid; deze meting is wat die afleiding vasthoudt.
//
// Alles wordt afgeleid uit spelInfo() en GRAM_PADEN. Geen enkel lijstje met de hand: dat ging in
// twee dagen vier keer mis, zie de kop van padvul.js.
const { chromium } = require('playwright');
const { VUL } = require('./padvul.js');

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwGrt' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  // alles zichtbaar, anders staat de helft onder "komt er straks bij" en zonder id op het scherm
  await page.evaluate(() => {
    S.lang = 'nl'; S.speelAlles = true;
    S.conjOpen = CONJ_FASES.length - 1; S.conjFase = CONJ_FASES[CONJ_FASES.length - 1].id;
    try { persist(); } catch (e) {}
  });

  const tegels = await page.evaluate(() => spelInfo().map((g) => ({ v: g.v, id: g.id, gram: !!g.gram })));
  const gram = tegels.filter((g) => g.gram);
  const speel = tegels.filter((g) => !g.gram);

  async function naarSpeeltuin() {
    /* v23.145: de Speeltuin toont er drie vooraan en de rest achter "alle spellen". Deze suite gaat
       over wáár een tegel woont en niet over hoeveel er vooraan staan, dus we klappen hem open: dan
       is "geen enkele grammatica-tegel in de Speeltuin" ook echt over alle tegels. */
    await page.evaluate(() => { funView = null; S.spelAlles = true; });
    await page.click('#nav button[data-tab="speeltuin"]');
    await page.waitForTimeout(250);
  }
  async function naarGram() {
    await page.evaluate(() => { funView = null; gwSess = null; gcLeesId = null; show('spiekbrief'); });
    await page.waitForTimeout(250);
  }

  // ---- 1. DE KERN: geen grammatica meer in de Speeltuin ----
  await naarSpeeltuin();
  const inSpeeltuin = [];
  for (const g of gram) if (await page.locator('#' + g.id).count()) inSpeeltuin.push(g.id);
  const speelStaatEr = [];
  for (const g of speel) if (await page.locator('#' + g.id).count()) speelStaatEr.push(g.id);

  console.log('\n-- DE KERN: de Speeltuin --');
  ok(gram.length >= 5, 'er zijn ' + gram.length + ' grammatica-tegels (' + gram.map((g) => g.v).join(', ') + ')');
  ok(inSpeeltuin.length === 0,
    'DE REGEL: geen enkele grammatica-tegel in de Speeltuin (nu: ' + (inSpeeltuin.join(', ') || 'geen') + ')');
  ok(speelStaatEr.length === speel.length,
    'CONTROLE: de spellen staan er nog wél, alle ' + speel.length + ' (gevonden: ' + speelStaatEr.length + ')');

  // ---- 2. en wel op de Grammatica-tab ----
  await naarGram();
  const opGram = [];
  for (const g of gram) if (await page.locator('#' + g.id).count()) opGram.push(g.id);

  console.log('\n-- de Grammatica-tab --');
  ok(opGram.length === gram.length,
    'elke grammatica-tegel staat op de Grammatica-tab (' + opGram.length + '/' + gram.length + ')');
  ok(await page.locator('#gramRoute').count() === 1, 'de routekaart staat er');
  ok(await page.locator('#gramOefen').count() === 1, 'en de losse oefeningen eronder');
  // de bestaande inhoud is niet weggevallen
  const nogSteeds = await page.evaluate(() => document.getElementById('cheat').innerText);
  ok(/Onder de knie krijgen/.test(nogSteeds), 'CONTROLE: de bestaande onderwerpen staan er nog onder');

  // ---- en ze doen ook iets ----
  console.log('\n-- elke tegel doet iets --');
  const dood = [];
  for (const g of gram) {
    await naarGram();
    const voor = await page.evaluate(() => funView);
    await page.click('#' + g.id);
    await page.waitForTimeout(350);
    const na = await page.evaluate(() => funView);
    if (na === voor) dood.push(g.id);
    ok(na !== voor, g.id + ' → funView ' + (na || 'null'));
  }
  ok(dood.length === 0, 'DE REGEL: geen dode tegel op deze tab (nu: ' + (dood.join(', ') || 'geen') + ')');

  // ---- 3. de routekaart leest GRAM_PADEN, en toont de route waar je in staat ----
  // v23.126: er is meer dan één route. Welke er bovenaan staat is een regel op zichzelf: die waar
  // je in staat, en pas als je nergens in staat de eerste uit de Conjugador-ladder. Deze suite
  // leidt dat overal af en somt geen enkele route met de hand op.
  const route = await page.evaluate(new Function(VUL + `
    const p = GRAM_PADEN[0];
    function toon() {
      gwSess = null; gcLeesId = null; show('spiekbrief');
      const nu = gramPadNu();
      const v = gramPadVolgende(nu);
      return {
        id: nu.id, volgende: v,
        titel: v >= 0 ? ct(nu.stappen[v].nl, nu.stappen[v].en) : null,
        regel: (document.getElementById('gramRouteNu') || {}).innerText || '',
        knop: (document.getElementById('btnGramVerder') || {}).innerText || '',
        kaart: (document.getElementById('gramRoute') || {}).innerText || '',
        andere: (document.getElementById('gramRoutes') || {}).innerText || '',
        rijen: document.querySelectorAll('#gramRoutes [data-padga]').length
      };
    }
    S.brok = {}; S.gramwiz = {};
    const leeg = toon();
    vulPad(p, 4);
    const half = toon();
    vulPad(p, p.stappen.length);
    const vol = toon();
    return {
      leeg, half, vol,
      eerste: gramPadenGeordend()[0].id,
      orde: gramPadenGeordend().map(function (x) { return x.id; }),
      rang: gramPadenGeordend().map(function (x) { return gramPadRang(x); }),
      paden: GRAM_PADEN.length, test: p.id
    };
  `));

  console.log('\n-- de volgorde van de routes --');
  ok(route.paden >= 2, 'er zijn ' + route.paden + ' routes');
  ok(route.rang.join(',') === route.rang.slice().sort((x, y) => x - y).join(','),
    'DE REGEL: de volgorde komt uit de Conjugador-ladder (' +
    route.orde.map((id, i) => id + ':' + route.rang[i]).join(', ') + ')');

  console.log('\n-- welke route staat er bovenaan --');
  ok(route.leeg.id === route.eerste,
    'niets gedaan → de eerste uit de ladder (' + route.leeg.id + ')');
  ok(route.half.id === route.test,
    'DE REGEL: halverwege een route → die route, ook al staat hij verderop in de ladder (' + route.half.id + ')');
  ok(route.vol.id !== route.test,
    'CONTROLE: en zodra hij klaar is, schuift hij door naar de volgende (' + route.vol.id + ')');

  console.log('\n-- de routekaart --');
  ok(route.leeg.volgende === 0 && route.leeg.regel.indexOf(route.leeg.titel) !== -1,
    'niets gedaan → de kaart wijst stap 1 aan ("' + route.leeg.regel.replace(/\s+/g, ' ') + '")');
  ok(route.half.titel && route.half.regel.indexOf(route.half.titel) !== -1,
    'DE REGEL: vier stappen af → de kaart wijst de vijfde aan ("' + route.half.regel.replace(/\s+/g, ' ') + '")');
  ok(route.leeg.regel !== route.half.regel,
    'CONTROLE: de regel verandert dus echt mee met de stand, hij staat niet vast');
  ok(route.half.knop.indexOf(route.half.titel) !== -1,
    'en de knop noemt diezelfde stap ("' + route.half.knop.replace(/\s+/g, ' ') + '")');
  ok(/\d\s*\/\s*\d/.test(route.leeg.kaart), 'er staat een teller op de kaart');

  console.log('\n-- de andere routes staan eronder --');
  ok(route.leeg.rijen === route.paden - 1,
    'alle andere routes staan er, klein (' + route.leeg.rijen + ' van de ' + (route.paden - 1) + ')');
  ok(/Gestold|Set/.test(route.vol.andere),
    'DE REGEL: een afgeronde route zegt daar "gestold" ("' + route.vol.andere.replace(/\s+/g, ' ').slice(0, 90) + '")');

  /* De knop opent de stap waar hij naar wijst. Elke stapsoort in de route van dat moment, en niet
     één: een bestaandeles opent een wizard op de Grammatica-tab, de rest een scherm in de
     speeltuinkaart. Welke van de twee het is, wordt uit de stap zelf afgeleid. */
  const opent = await page.evaluate(new Function(VUL + `
    const uit = [];
    GRAM_PADEN.forEach(function (p) {
      for (let n = 0; n < p.stappen.length; n++) {
        vulPad(p, n);
        funView = null; padView = null; gwSess = null; gcLeesId = null; show('spiekbrief');
        const nu = gramPadNu();
        const v = gramPadVolgende(nu);
        const knop = document.getElementById('btnGramVerder');
        if (v < 0 || !knop) continue;
        const s = nu.stappen[v];
        knop.click();
        uit.push({
          pad: nu.id, i: v, soort: s.soort, titel: ct(s.nl, s.en),
          goed: s.soort === 'bestaandeles'
            ? (!!gwSess && !document.getElementById('tab-spiekbrief').classList.contains('hidden'))
            : (funView === s.view && !document.getElementById('tab-speeltuin').classList.contains('hidden'))
        });
      }
    });
    return uit;
  `));
  const mis = opent.filter((x) => !x.goed);
  const soorten = new Set(opent.map((x) => x.soort));
  console.log('\n-- de knop opent wat hij belooft --');
  ok(opent.length >= 5, 'de knop is voor ' + opent.length + ' verschillende standen getest');
  ok(mis.length === 0,
    'DE REGEL: de knop opent de stap waar hij naar wijst, welke soort het ook is (mis: ' +
    (mis.map((x) => x.pad + '/' + x.soort + ' "' + x.titel + '"').join(', ') || 'geen') + ')');
  ok(soorten.size >= 3, 'en dat is over ' + soorten.size + ' verschillende stapsoorten gemeten');

  // ---- 5. de balk springt niet om ----
  const balk = await page.evaluate(() => {
    const aan = () => Array.prototype.filter.call(document.querySelectorAll('#nav button'),
      (b) => b.classList.contains('active')).map((b) => b.getAttribute('data-tab')).join(',');
    return { nu: aan() };
  });
  console.log('\n-- de balk --');
  ok(balk.nu === 'oefenen',
    'DE REGEL: Oefenen licht op in een grammatica-oefening, niet Spelen (nu: "' + balk.nu + '")');

  // ---- 4. terug komt uit waar je vandaan kwam ----
  console.log('\n-- de terugknop --');
  await naarGram();
  await page.click('#ftLes');
  await page.waitForTimeout(350);
  const heeftTerug = await page.locator('#btnFunTerug').count();
  ok(heeftTerug === 1, 'de les heeft een terugknop');
  if (heeftTerug) {
    await page.click('#btnFunTerug');
    await page.waitForTimeout(350);
  }
  const naTerug = await page.evaluate(() => ({
    view: funView,
    gram: !document.getElementById('tab-spiekbrief').classList.contains('hidden'),
    speeltuin: !document.getElementById('tab-speeltuin').classList.contains('hidden'),
    route: document.querySelectorAll('#gramRoute').length
  }));
  ok(naTerug.gram === true && naTerug.speeltuin === false,
    'DE REGEL: terug uit een grammatica-oefening komt uit op de Grammatica-tab');
  ok(naTerug.route === 1, 'en de routekaart staat er weer');
  ok(naTerug.view === null, 'en er loopt geen oefening meer');

  // controle: een spel gedraagt zich nog als vanouds
  await naarSpeeltuin();
  await page.click('#ftLetras');
  await page.waitForTimeout(350);
  const terugSpel = await page.locator('#btnFunTerug').count();
  if (terugSpel) { await page.click('#btnFunTerug'); await page.waitForTimeout(300); }
  const naSpel = await page.evaluate(() => ({
    view: funView,
    speeltuin: !document.getElementById('tab-speeltuin').classList.contains('hidden'),
    tegels: document.querySelectorAll('#ftLetras').length
  }));
  ok(naSpel.speeltuin === true && naSpel.view === null && naSpel.tegels === 1,
    'CONTROLE: terug uit een spel komt nog steeds uit in de Speeltuin');

  // ---- 6. de dagkaart biedt geen grammatica aan ----
  const dag = await page.evaluate(() => ({
    dag: dagSpellen().map((x) => x.v),
    gram: spelInfo().filter((x) => x.gram).map((x) => x.v),
    uit: Object.keys(DAGSPEL_UIT)
  }));
  console.log('\n-- de dagkaart --');
  ok(dag.gram.every((v) => dag.dag.indexOf(v) === -1),
    'geen grammatica-oefening in dagSpellen() (' + dag.dag.join(', ') + ')');
  ok(dag.gram.every((v) => dag.uit.indexOf(v) === -1),
    'DE REGEL: en dat staat niet meer met de hand in DAGSPEL_UIT (daar staat nu: ' + dag.uit.join(', ') + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
