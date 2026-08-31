// v22.9: het familie-klassement is opgeheven. Stefan: "familieklassement kan weg als we nu met de
// wall werken. geen competitie, dat is met jezelf."
// Deze suite vervangt pw-familie.js en pw-krabbels.js. Hij bewaakt niet dat het scherm werkt maar
// dat het wég is, en dat de onderdelen die er nog gelezen worden níet zijn meegesneuveld: KRABBELS
// (het reactiepalet), krabbelVind() en krabbelIkBen().
//
// v23.222: de muur is óók opgeheven, en daarmee de enige plek waar je een krabbel kon VERSTUREN.
// Het palet blijft staan omdat dagKrabbels() op het dagbord de binnengekomen krabbels nog toont, en
// die leest famCache en niet de muur. Zolang het sociale opnieuw ontworpen wordt is dat de goedkope
// kant om te bewaren: data en leeskant blijven, de schermen zijn weg.
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
  await page.fill('input[placeholder="Name"]', 'PwFw' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);

  const weg = await page.evaluate(() => ({
    kaart: !!document.getElementById('familieCard'),
    render: typeof renderFamilia,
    lijst: typeof famLijstRender,
    stuur: typeof krabbelStuur,
    rij: typeof krabbelRijHtml
  }));
  ok(weg.kaart === false, 'de familie-klassementkaart staat niet meer in het profielscherm');
  ok(weg.render === 'undefined', 'renderFamilia() bestaat niet meer');
  ok(weg.lijst === 'undefined', 'famLijstRender() ook niet');
  ok(weg.stuur === 'undefined', 'en krabbelStuur() evenmin');
  ok(weg.rij === 'undefined', 'en krabbelRijHtml() evenmin');

  // Wat het dagbord nog leest, moet er wél zijn.
  const blijft = await page.evaluate(() => ({
    palet: Array.isArray(KRABBELS) && KRABBELS.length,
    vind: typeof krabbelVind === 'function' && !!krabbelVind('ole'),
    ikben: typeof krabbelIkBen === 'function',
    dagkrab: typeof dagKrabbels === 'function',
    muur: typeof muurHtml   // v23.222: en de muur hoort er nu juist NIET meer te zijn
  }));
  ok(blijft.palet >= 6, 'het reactiepalet KRABBELS bestaat nog: ' + blijft.palet);
  ok(blijft.vind, 'krabbelVind() werkt nog, het dagbord toont er de Spaanse zin mee');
  ok(blijft.ikben, 'krabbelIkBen() werkt nog');
  ok(blijft.dagkrab, 'dagKrabbels() werkt nog: binnengekomen krabbels komen nog op je dagbord');
  ok(blijft.muur === 'undefined', 'en de muur is weg (v23.222)');

  // Nergens in het profielscherm nog een medaille of een klassement.
  await page.evaluate(() => { try { show('perfil'); } catch (e) {} });
  await page.waitForTimeout(400);
  const tekst = await page.evaluate(() => (document.getElementById('tab-perfil') || {}).innerText || '');
  ok(!/klassement|leaderboard/i.test(tekst), 'het woord klassement komt niet meer voor op je profiel');
  ok(!/🥇|🥈|🥉/.test(tekst), 'en er staan geen medailles meer');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
