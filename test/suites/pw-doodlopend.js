// pw-doodlopend.js (24 aug, v23.188) — drie plekken waar iets stil niet gebeurde
//
// WAAROM DEZE SUITE ER IS
//
// Drie meldingen van Stefan op 24 augustus, en alle drie hetzelfde patroon: er gebeurt niets, en
// niets zegt dat. Een fout die iets gooit vind je terug; deze soort niet.
//
//   1. "de volgende knop werkte niet. Die bug heb ik nu weer." lesFlowVolgendeKern() is een rij van
//      zes if-blokken zonder else. Een lesFlow.stap die geen van de zes namen draagt valt eronderdoor
//      en de knop is dood, vandaag en morgen weer, want lesFlowBewaar() schrijft die stap weg.
//   2. "als ik op de suggestie 'puzzel' klik, gaat ie naar de puzzel die ik recent heb gedaan."
//      speelStart() (de tegel) roept g.verse() aan, speelNaar() (de suggestie) had een eigen rijtje
//      waar letras en ws niet in stonden.
//   3. "er zijn recente woorden die ik vaak fout doe die ik hier niet terug zie." gameVoorrang()
//      las nergens wannéér je een woord fout deed.
//
// WAT DEZE SUITE BEWAAKT, EN WAT DE CONTROLEGEVALLEN ZIJN
//
//   1. Een onbekende stap loopt niet dood. CONTROLE: en een bekende stap wordt niet afgekapt — de
//      bodem is triviaal groen te maken door élke stap af te ronden, en dan is er geen dagles meer.
//   2. Beide wegen naar een spel maken hem vers. CONTROLE: de twee wegen zijn het over álle spellen
//      eens, niet alleen over letras; anders staat er over een half jaar weer een derde spel buiten.
//   3. Wat je deze week fout deed komt vooraan. CONTROLE: een oude hardnekkige fout staat nog steeds
//      vóór een woord dat je nooit fout deed — anders is de ene voorkeur ingeruild voor de andere.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDl' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 1. de knop die niets deed ----
  console.log('\n-- 1. een onbekende stap loopt niet dood --');
  const dood = await page.evaluate(() => {
    const uit = [];
    ['dictado', 'lezen', 'luisteren', 'vertalen', 'extra', 'toetsjes-2'].forEach(function (st) {
      lesFlow = { stap: st, quizzesTeDoen: [], vaardigheidRij: [] };
      const voor = lesFlowOpende;
      let f = null;
      try { lesFlowVolgende(); } catch (e) { f = e.message; }
      uit.push({ stap: st, fout: f, opende: lesFlowOpende > voor, flowWeg: lesFlow === null });
    });
    return uit;
  });
  dood.forEach(function (d) {
    ok(!d.fout && d.opende && d.flowWeg,
      'stap "' + d.stap + '" opent een scherm en rondt de les af' + (d.fout ? ' (fout: ' + d.fout + ')' : ''));
  });

  // HET CONTROLEGEVAL: een bekende stap wordt niet afgekapt
  const echt = await page.evaluate(() => {
    lesFlow = { stap: null, quizzesTeDoen: [], vaardigheidRij: [] };
    const voor = lesFlowOpende;
    lesFlowVolgende();
    return { opende: lesFlowOpende > voor, flowErNog: !!lesFlow, stap: lesFlow && lesFlow.stap };
  });
  ok(echt.opende && echt.flowErNog,
    'CONTROLE: een gewone les gaat gewoon door (stap nu: ' + echt.stap + ')');

  // ---- 2. beide wegen naar een spel maken hem vers ----
  console.log('\n-- 2. de suggestie geeft dezelfde verse puzzel als de tegel --');
  const vers = await page.evaluate(() => {
    // een puzzel neerzetten alsof hij al gespeeld is
    /* Niet op null toetsen: renderFunLetras() bouwt meteen een nieuwe puzzel zodra ltSpel leeg is,
       dus na afloop staat er wéér iets. De vraag is of het de oude is. Vandaar het merkteken. */
    ltSpel = { letters: ['a'], gekozen: [], doelen: [], gevonden: { x: 1 }, melding: 'oud', merk: 'OUD' };
    ws = { grid: [], woorden: [], merk: 'OUD' };
    speelNaar('letras');
    const naLetras = ltSpel;
    speelNaar('ws');
    const naWs = ws;
    return {
      letrasVers: !naLetras || naLetras.merk !== 'OUD',
      letrasGevonden: naLetras ? Object.keys(naLetras.gevonden || {}).length : 0,
      wsVers: !naWs || naWs.merk !== 'OUD'
    };
  });
  ok(vers.letrasVers, 'de suggestie zet Letras vers neer');
  ok(vers.letrasGevonden === 0, 'en er staat niets meer als al gevonden (nu: ' + vers.letrasGevonden + ')');
  ok(vers.wsVers, 'en de woordenzoeker ook');

  // HET CONTROLEGEVAL: de twee wegen zijn het over alle spellen eens
  const eens = await page.evaluate(() => {
    const uit = [];
    spelInfo().forEach(function (g) {
      if (!g.verse || g.open) return;
      // via de tegel
      const zetOud = function () {
        // elk spel bewaart zijn stand in een eigen globale; die halen we uit de verse zelf
        return String(g.verse);
      };
      uit.push({ v: g.v, verse: zetOud() });
    });
    // welke spellen speelNaar() nog met de hand doet
    const metDeHand = String(speelNaar).match(/if\(v === "(\w+)"\)/g) || [];
    return { metVerse: uit.map(function (u) { return u.v; }), metDeHand: metDeHand };
  });
  const dubbel = eens.metVerse.filter(function (v) {
    return eens.metDeHand.some(function (h) { return h.indexOf('"' + v + '"') >= 0; });
  });
  console.log('   spellen met verse: ' + eens.metVerse.join(', '));
  console.log('   nog met de hand in speelNaar: ' + eens.metDeHand.join(' '));
  ok(dubbel.length === 0,
    'CONTROLE: geen enkel spel staat zowel in spelInfo().verse als in het handwerk van speelNaar (' +
    (dubbel.join(', ') || 'geen') + ')');

  // ---- 3. wat je deze week fout deed komt vooraan ----
  console.log('\n-- 3. verse fouten voorop --');
  const rang = await page.evaluate(() => {
    const vandaag = today();
    const oud = '2020-01-01';
    const pool = [
      { id: 'nooit', woord: 'nooit' },
      { id: 'oudvaak', woord: 'oudvaak' },
      { id: 'verstwee', woord: 'verstwee' },
      { id: 'wankel', woord: 'wankel' }
    ];
    S.errors['woord:oudvaak'] = { id: 'oudvaak', count: 9, dag: oud, laatst: oud };
    S.errors['woord:verstwee'] = { id: 'verstwee', count: 2, dag: vandaag, laatst: vandaag };
    S.srs.wankel = { box: 0 };
    const volgorde = gameVoorrang(pool).map(function (p) { return p.id; });
    return { volgorde: volgorde };
  });
  console.log('   volgorde: ' + rang.volgorde.join(' → '));
  ok(rang.volgorde[0] === 'verstwee',
    'twee fouten van deze week gaan vóór negen fouten van 2020 (nu: ' + rang.volgorde[0] + ')');
  ok(rang.volgorde.indexOf('oudvaak') < rang.volgorde.indexOf('nooit'),
    'CONTROLE: een oude hardnekkige fout staat nog steeds vóór een woord dat je nooit fout deed');
  ok(rang.volgorde.indexOf('wankel') < rang.volgorde.indexOf('nooit'),
    'CONTROLE: en een wankel woord ook');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
