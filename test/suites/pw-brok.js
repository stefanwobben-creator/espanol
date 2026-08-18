// pw-brok.js (15 aug, v23.106) — meet "achtergrond of gebeurtenis" wat hij belooft te meten?
//
// WAAROM DIT ER IS
//
// Stefan, drie keer op één dag: "ik kan de regel 8 van de 10 keer goed toepassen maar niet alle
// vervoegingen uit mijn hoofd, dus dan gok ik maar wat." Elke grammaticavraag in de app test de
// regel en de vorm tegelijk, dus een fout zegt niet welke van de twee ontbrak. Dit schermpje haalt
// die twee uit elkaar door het Spaans weg te laten: twaalf Nederlandse zinnen, twee bakjes.
//
// De waarde van dit scherm zit volledig in de betrouwbaarheid van de uitslag. Een meting die je
// vertelt dat je het snapt terwijl je het niet snapt, is erger dan geen meting: dan gaat al het
// werk daarna naar de vormen terwijl het gat ergens anders zit. Vandaar deze suite.
//
// DE CONTROLEGEVALLEN
//
// Drie stuks, en ze sluiten alle drie een andere manier uit waarop dit scherm groen kan zijn
// zonder te werken:
//
//   1. altijd "achtergrond" kiezen moet precies 6 van de 12 geven, niet 12 en niet 0
//   2. altijd "gebeurtenis" kiezen ook
//   3. het goede antwoord per zin geven moet 12 van de 12 geven
//
// Zonder 1 en 2 zou een scherm dat alles goedkeurt hier groen staan. Zonder 3 zou een scherm dat
// alles afkeurt hier groen staan.
//
// En één inhoudelijke: het strikpaar. Twee zinnen met hetzelfde werkwoord en een ander antwoord
// ("ik werkte bij die firma toen ik hem leerde kennen" tegenover "ik werkte drie jaar bij die
// firma"). Zonder dat paar kun je op het werkwoord patroonherkennen en meet de test niets.
const { chromium } = require('playwright');
const { naarTegel, naarTegelTab } = require('./tegelhulp.js');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

// Speelt één hele ronde. keuze is 'a', 'g', of 'echt' (het juiste antwoord per zin).
async function ronde(page, keuze) {
  // v23.124: show() en niet renderFun(). De tegel woont nu op de Grammatica-tab, dus staat de
  // speeltuinkaart verstopt als je hier binnenkomt, en dan valt er niets aan te klikken.
  await page.evaluate(() => { funView = 'brok'; brokSpel = null; show('speeltuin', true); });
  await page.waitForTimeout(200);
  for (let i = 0; i < 12; i++) {
    const wil = keuze === 'echt'
      ? await page.evaluate(() => BROK_TIJD[brokSpel.rij[brokSpel.i]].s)
      : keuze;
    await page.click(wil === 'a' ? '#btnBrokA' : '#btnBrokG');
    await page.waitForTimeout(60);
    await page.click('#btnBrokVerder');
    await page.waitForTimeout(60);
  }
  return page.evaluate(() => ({
    goed: brokSpel.goed,
    tekst: document.getElementById('funCard').innerText,
    brok: JSON.parse(JSON.stringify(S.brok || {}))
  }));
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(500);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwBrok' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // ---- 1. de inhoud ----
  const data = await page.evaluate(() => {
    const spaans = /[áéíóúñ¿¡]/i;
    return {
      n: BROK_TIJD.length,
      a: BROK_TIJD.filter((z) => z.s === 'a').length,
      g: BROK_TIJD.filter((z) => z.s === 'g').length,
      velden: BROK_TIJD.every((z) => z.nl && z.en && z.w && z.wEn && (z.s === 'a' || z.s === 'g')),
      // het hele punt van dit scherm: er staat geen Spaans in, ook niet in de uitleg
      spaansInZin: BROK_TIJD.filter((z) => spaans.test(z.nl) || spaans.test(z.en)).length,
      // het strikpaar: hetzelfde werkwoord, een ander antwoord
      strik: (function () {
        const werkte = BROK_TIJD.filter((z) => /\bwerkte\b/.test(z.nl));
        return { n: werkte.length, soorten: Array.from(new Set(werkte.map((z) => z.s))).length };
      })()
    };
  });

  console.log('\n-- de twaalf zinnen --');
  ok(data.n === 12, 'er zijn twaalf zinnen (nu: ' + data.n + ')');
  ok(data.a === 6 && data.g === 6, 'zes achtergrond en zes gebeurtenis (nu: ' + data.a + '/' + data.g + ')');
  ok(data.velden === true, 'elke zin heeft nl, en, w, wEn en een geldig soort');
  ok(data.spaansInZin === 0,
    'er staat geen woord Spaans in, want dat is het hele punt (nu: ' + data.spaansInZin + ')');
  ok(data.strik.n === 2 && data.strik.soorten === 2,
    'het strikpaar staat erin: twee keer "werkte", twee verschillende antwoorden');

  // ---- 2. de drie controlerondes ----
  // v23.124: de tegel is verhuisd naar de Grammatica-tab. Welke tab dat is vraagt tegelhulp aan
  // de app, zodat deze suite dat feit niet napraat.
  const tegel = await naarTegelTab(page, 'ftBrok', false);

  const altijdA = await ronde(page, 'a');
  const altijdG = await ronde(page, 'g');
  const echt = await ronde(page, 'echt');

  console.log('\n-- de meting keurt niet alles goed en niet alles fout --');
  ok(tegel === 1, 'de tegel staat op de tab waar hij hoort');
  ok(altijdA.goed === 6, 'CONTROLE: altijd "achtergrond" geeft precies 6/12 (nu: ' + altijdA.goed + ')');
  ok(altijdG.goed === 6, 'CONTROLE: altijd "gebeurtenis" geeft precies 6/12 (nu: ' + altijdG.goed + ')');
  ok(echt.goed === 12, 'CONTROLE: het juiste antwoord per zin geeft 12/12 (nu: ' + echt.goed + ')');

  console.log('\n-- de uitslag zegt wat je morgen moet doen --');
  ok(/vormen|forms/i.test(echt.tekst),
    'bij een volle score wijst de uitslag naar de vormen, niet naar de regel');
  ok(/gat|gap/i.test(altijdA.tekst),
    'bij een halve score zegt hij dat het gat hier zit');

  console.log('\n-- de uitslag wordt onthouden --');
  const st = echt.brok['indefimperf.betekenis'];
  ok(!!st, 'de stand staat in S.brok onder een brok-id');
  ok(st && st.rondes === 3, 'drie rondes geteld (nu: ' + (st && st.rondes) + ')');
  ok(st && st.beste === 12, 'de beste ronde is bewaard (nu: ' + (st && st.beste) + ')');
  // Bewust NIET in S.gram: daar hangen gramFoutTop(), gcOpenSet() en de dagles aan, en het
  // brokkenmodel is nog niet bewezen. Eerst meten, dan koppelen.
  const gram = await page.evaluate(() => Object.keys(S.gram || {}).length);
  ok(gram === 0, 'en niet in S.gram, want dat model is nog niet bewezen (nu: ' + gram + ' sleutels)');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
