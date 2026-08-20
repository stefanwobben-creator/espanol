// pw-chat.js (20 aug, v23.144) — kun je met Chispa praten, en houdt het op tijd op?
//
// WAAROM DIT ER IS
//
// Stefan: "ik kan ook nog niet chatten met chispa." En eerder: "chatten met chispa of bijv ilona kan
// heel goed helpen bij produceren."
//
// Nation's tweede draad is betekenisgerichte output: iets zeggen omdat je iets wilt zeggen. Alles
// wat Vamos aan produceren deed is van het andere soort: een Nederlandse zin, een Spaanse vertaling,
// goed of fout.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. CHISPA BEGINT, ZONDER MODELAANROEP. De openingszin komt uit een lijst en staat er dus ook als
//      de server plat ligt. Dat is de reden dat hij als index bewaard wordt en niet als tekst: in
//      een Engels profiel hoort er morgen geen Nederlands te staan.
//   2. JE KUNT ANTWOORDEN, EN DE CORRECTIE STAAT ERNAAST. Wat jij schreef staat in het gesprek; of
//      het klopt staat eronder in een aparte regel. Zet je de correctie in Chispa's beurt, dan is ze
//      geen gesprekspartner meer.
//   3. DRIE BEURTEN, DAN KLAAR. Een gesprek zonder eind is waar je op afhaakt. Na drie beurten geen
//      invoerveld meer.
//   4. HET GESPREK OVERLEEFT EEN PLATTE SERVER. Geen antwoord betekent: jouw zin blijft staan, de
//      beurt telt, en er staat waarom er niets terugkomt. Niet: een leeg scherm.
//   5. EEN GESPREK PER DAG, EN HET VOORSTEL VERDWIJNT DAARNA. Na je les is het een voorstel; heb je
//      vandaag al gepraat, dan niet meer. Aandringen is geen voorstel.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door het gesprek nooit te laten eindigen: dan klopt punt 2 en is
// punt 3 stuk. Daarom wordt er precies tot voorbij de derde beurt doorgeteld en gemeten dat het
// invoerveld dan weg is.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  // Het model wordt niet echt gebeld: deze suite gaat over de machinerie eromheen, en een echte
  // aanroep zou de poort van het weer laten afhangen.
  await page.route('**/api/ai/chat', (route) => {
    const body = JSON.parse(route.request().postData() || '{}');
    if (body.modus === 'hulp') {
      return route.fulfill({ status: 200, contentType: 'application/json',
        body: JSON.stringify({ ok: true, es: 'Me la ha regalado mi vecina.', uitleg: 'Letterlijk: mijn buurvrouw heeft hem aan mij cadeau gedaan.' }) });
    }
    return route.fulfill({ status: 200, contentType: 'application/json',
      body: JSON.stringify({ ok: true, naast: 'Klopt, maar natuurlijker zonder una.', es: 'Que rico. Y tu?', nl: 'Lekker. En jij?' }) });
  });

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwCh' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 1. Chispa begint, zonder modelaanroep ----
  const start = await page.evaluate(() => {
    S.lang = 'nl';
    show('chat');
    const st = chatStand();
    return { beurten: st.beurten.length, eerste: st.beurten[0],
             tekst: document.getElementById('chatWrap').textContent.replace(/\s+/g, ' '),
             invoer: !!document.getElementById('chatInvoer'),
             perTaal: (function () {
               S.lang = 'en'; const en = chatTekst(st.beurten[0]).nl;
               S.lang = 'nl'; const nl = chatTekst(st.beurten[0]).nl;
               return { en: en, nl: nl };
             })() };
  });
  console.log('\n-- 1. Chispa begint, zonder modelaanroep --');
  console.log('   ' + start.tekst.slice(0, 110));
  ok(start.beurten === 1, 'er staat één beurt en die is van haar');
  ok(typeof start.eerste.i === 'number', 'bewaard als index, niet als tekst (i=' + start.eerste.i + ')');
  ok(start.perTaal.en !== start.perTaal.nl, 'dus de vertaling volgt de taal van het profiel');
  ok(start.invoer, 'en er staat een invoerveld klaar');
  ok(/beurt 1\/3/.test(start.tekst), 'met erbij hoeveel beurten het er zijn');

  // ---- 2. je kunt antwoorden, en de correctie staat ernaast ----
  await page.fill('#chatInvoer', 'He comido una tortilla.');
  await page.click('#chatStuur');
  await page.waitForTimeout(700);
  const na1 = await page.evaluate(() => ({
    beurten: S.chat.beurten.map(function (b) { return { van: b.van, es: b.es, naast: b.naast || null }; }),
    naastInBel: document.querySelectorAll('.bel .naast').length,
    naastLos: document.querySelectorAll('.naast').length,
    tekst: document.getElementById('chatWrap').textContent.replace(/\s+/g, ' ')
  }));
  console.log('\n-- 2. je kunt antwoorden, en de correctie staat ernaast --');
  ok(na1.beurten.length === 3, 'jouw zin en haar antwoord staan erin (' + na1.beurten.length + ' beurten)');
  ok(na1.beurten[1].van === 'jij' && /tortilla/.test(na1.beurten[1].es), 'jouw zin staat er letterlijk');
  ok(na1.beurten[1].naast === 'Klopt, maar natuurlijker zonder una.', 'met de notitie erover aan jouw beurt gehangen');
  ok(na1.naastLos >= 1 && na1.naastInBel === 0, 'en die staat náást het gesprek, niet in een tekstballon');
  ok(/Que rico/.test(na1.tekst), 'haar antwoord staat er ook');

  // ---- 3. drie beurten, dan klaar ----
  for (let i = 0; i < 2; i++) {
    await page.fill('#chatInvoer', 'Si, muy rico.');
    await page.click('#chatStuur');
    await page.waitForTimeout(700);
  }
  const na3 = await page.evaluate(() => ({
    mijn: chatMijn(), klaar: chatKlaar(), vlag: !!S.chat.klaar,
    invoer: !!document.getElementById('chatInvoer'),
    gedaan: chatGedaanVandaag(),
    tekst: document.getElementById('chatWrap').textContent.replace(/\s+/g, ' ')
  }));
  console.log('\n-- 3. drie beurten, dan klaar --');
  ok(na3.mijn === 3, 'je hebt drie keer wat gezegd (' + na3.mijn + ')');
  ok(na3.klaar && na3.vlag, 'en het gesprek staat op klaar');
  ok(na3.invoer === false, 'het controlegeval: er is geen invoerveld meer');
  ok(/klaar/.test(na3.tekst), 'en dat staat er ook');

  // ---- 5. een gesprek per dag ----
  const voorstel = await page.evaluate(() => {
    const gedaan = chatGedaanVandaag();
    S.gram = {};
    const w1 = lesFlowWinst();
    S.chat.klaar = false;                     // doen alsof je vandaag nog niet praatte
    const w2 = lesFlowWinst();
    S.chat.klaar = true;
    return { gedaan: gedaan, metGesprek: w1 ? w1.kop : null, zonderGesprek: w2 ? w2.kop : null };
  });
  console.log('\n-- 5. een gesprek per dag --');
  ok(voorstel.gedaan, 'na je gesprek staat vandaag als gedaan');
  ok(/Chispa/.test(voorstel.zonderGesprek || ''), 'heb je nog niet gepraat, dan is het een voorstel na je les ("' + voorstel.zonderGesprek + '")');
  ok(!/Praat even met Chispa/.test(voorstel.metGesprek || ''), 'heb je wel gepraat, dan niet meer ("' + voorstel.metGesprek + '")');

  // ---- 4. het gesprek overleeft een platte server ----
  await page.route('**/api/ai/chat', (route) => route.fulfill({ status: 502, contentType: 'application/json', body: JSON.stringify({ ok: false, fout: 'AI-fout' }) }));
  const plat = await page.evaluate(async () => {
    S.chat = { d: today(), beurten: [], klaar: false };
    show('chat');
    document.getElementById('chatInvoer').value = 'Hola, soy Stefan.';
    chatStuur();
    await new Promise(function (r) { setTimeout(r, 900); });
    const mijne = S.chat.beurten.filter(function (b) { return b.van === 'jij'; });
    return { mijn: mijne.length, es: mijne[0] ? mijne[0].es : null, naast: mijne[0] ? mijne[0].naast : null,
             tekst: document.getElementById('chatWrap').textContent.replace(/\s+/g, ' ') };
  });
  console.log('\n-- 4. het gesprek overleeft een platte server --');
  ok(plat.mijn === 1, 'je beurt telt gewoon mee');
  ok(plat.es === 'Hola, soy Stefan.', 'en wat je schreef blijft staan');
  ok(!!plat.naast && plat.naast.length > 5, 'met een regel waarom er niets terugkomt ("' + plat.naast + '")');
  ok(!/undefined/.test(plat.tekst), 'en er staat nergens undefined op het scherm');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
