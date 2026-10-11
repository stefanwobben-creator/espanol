// pw-doorstroom.js (11 okt, v23.255) — komt de grammatica ooit ergens aan?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan: "ik doe nu vaak de woordjes en ook grammatica komt voorbij (alhoewel ik bij grammatica nog
// wel het idee heb dat dit beter kan) (...) ik blijf nu te lang hangen, een klein slordigheidsfoutje
// en ik blijf hangen in de grammatica les."
//
// Nagerekend voordat er iets veranderde. 31 onderwerpen met samen 159 patroondoosjes (v23.228) plus
// 31 "in een echte zin"-doosjes is 190 doosjes, en elk heeft vijf schone beurten nodig. De dagles
// gaf er één leerbeurt. Een jaar nagespeeld met negentig procent goed per vraag:
//
//     2 beurten per dag      24 van 190 doosjes op doos 5    4,3 beurten per doosje per jaar
//     4 beurten per dag     185 van 190 doosjes op doos 5    8,8 beurten per doosje per jaar
//
// Vier beurten per jaar, en je hebt er vijf nodig. Het hangen is rekenkunde, geen gevoel. En let op
// wat er NIET uit kwam: de slordigheidsregel van v23.254 maakt er 21 van de 190 van in plaats van
// 24. Die ingreep is goed maar raakt dit knelpunt niet.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE DAGLES BIEDT MEER DAN ÉÉN LEERBEURT. Dit is de proef die vóór v23.255 rood stond.
//   2. HOOGSTENS ÉÉN PATROON PER ONDERWERP. De regel van v23.170 ("heel veel el of la") blijft
//      staan: vijf patronen van hetzelfde onderwerp op één dag is die klacht in een nieuwe jas.
//   3. DE ROTATIE. Wie het langst niet aan de beurt is geweest staat vooraan, en wat je vandaag al
//      deed zakt naar achteren. Zonder dit blijft het zwakste doosje elke dag winnen en is de
//      onderkant van de stapel een gesloten lus.
//   4. BINNEN DEZELFDE DAG TELT ALSNOG HET ZWAKSTE. Anders is de rotatie willekeur.
//   5. gramWachtrij() ZELF IS NIET VERANDERD. Het voortgangsscherm en gramOnderhoudTop() lezen hem
//      ook, en die willen wél oplopend op doos.
//   6. HET ONDERHOUD DRINGT NIET VOOR (v23.235 blijft gelden).
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDs' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1 en 2. meer dan één leerbeurt, en niet vijf keer hetzelfde onderwerp ----
  //
  // Let op de volgorde: eerst S.gram vullen, dan pas kijken wat er open staat. Een onderwerp gaat
  // open zodra het één beurt heeft gehad (gcOpenSet leest goed+fout), dus andersom meet je de
  // toestand van vóór de opzet en staan er maar drie onderwerpen open.
  console.log('\n-- 1 en 2. de dagles biedt meerdere patronen, van verschillende onderwerpen --');
  const breed = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null;
    const alle = gcGeordend().map((c) => c.id);
    const eerste = alle[0];
    // vijf patronen van hetzelfde onderwerp, allemaal toe en allemaal het langst wachtend: de val
    // van v23.170. Zonder de ontdubbeling vult dit onderwerp in zijn eentje de hele dagles.
    for (let i = 0; i < 5; i++) S.gram[gramSleutel(eerste, i)] = { box: 0, due: today(), goed: 3, fout: 1, bd: addDays(today(), -30) };
    // en zes andere onderwerpen die ook toe zijn, iets korter wachtend
    alle.slice(1, 7).forEach((id, k) => {
      S.gram[gramSleutel(id, 0)] = { box: 1, due: today(), goed: 4, fout: 1, bd: addDays(today(), -20 + k) };
    });
    const lijst = lesFlowGramLijst();
    const kaal = (x) => String(x || '').replace(/^(opfris|concept)-/, '').split('#')[0];
    const namen = lijst.map(kaal);
    return {
      opfris: lijst.filter((x) => /^opfris-/.test(x)).length,
      beurten: lijst.length, namen: namen,
      uniek: new Set(namen).size,
      eersteVaak: namen.filter((n) => n === eerste).length,
      max: GRAM_LEERBEURTEN
    };
  });
  ok(breed.opfris >= 2, 'er staan meerdere opfrissers in de dagles: ' + breed.opfris + ' (vóór v23.255 was het er één)');
  ok(breed.opfris <= breed.max, 'en niet meer dan GRAM_LEERBEURTEN: ' + breed.opfris + ' van ' + breed.max);
  ok(breed.beurten >= 4, 'met de microles erbij telt het grammaticablok ' + breed.beurten + ' beurten');
  ok(breed.eersteVaak <= 1, 'hoogstens één patroon per onderwerp: het onderwerp met vijf open patronen staat er ' + breed.eersteVaak + 'x in');
  ok(breed.uniek === breed.namen.length, 'elke beurt gaat over een ander onderwerp (' + breed.namen.join(', ') + ')');

  // ---- 3. de rotatie: vandaag gedaan zakt naar achteren ----
  console.log('\n-- 3. wie het langst niet aan de beurt was, staat vooraan --');
  const rot = await page.evaluate(() => {
    S.gram = {};
    const alle = gcGeordend().map((c) => c.id);
    const vandaag = alle[0], lang = alle[1];
    // allebei op doos 0 en allebei toe. Het enige verschil is wanneer je ze voor het laatst deed.
    S.gram[gramSleutel(vandaag, 0)] = { box: 0, due: today(), goed: 2, fout: 1, bd: today() };
    S.gram[gramSleutel(lang, 0)] = { box: 0, due: today(), goed: 2, fout: 1, bd: addDays(today(), -12) };
    const rij = gramLeerRij();
    return { eerste: rij[0] && rij[0].c.id, lang: lang, n: rij.length };
  });
  ok(rot.n === 2, 'beide doosjes staan in de leerrij');
  ok(rot.eerste === rot.lang, 'het doosje van twaalf dagen geleden staat vooraan, niet dat van vandaag');

  // ---- 4. binnen dezelfde wachttijd telt alsnog het zwakste ----
  console.log('\n-- 4. gelijke wachttijd: dan wint het zwakste doosje --');
  const gelijk = await page.evaluate(() => {
    S.gram = {};
    const alle = gcGeordend().map((c) => c.id);
    const sterk = alle[0], zwak = alle[1];
    S.gram[gramSleutel(sterk, 0)] = { box: 3, due: today(), goed: 9, fout: 1, bd: addDays(today(), -5) };
    S.gram[gramSleutel(zwak, 0)] = { box: 0, due: today(), goed: 2, fout: 2, bd: addDays(today(), -5) };
    const rij = gramLeerRij();
    return { eerste: rij[0] && rij[0].c.id, zwak: zwak };
  });
  ok(gelijk.eerste === gelijk.zwak, 'bij dezelfde wachttijd staat het zwakste doosje vooraan');

  // ---- 5. de gedeelde wachtrij is niet veranderd ----
  console.log('\n-- 5. gramWachtrij() sorteert nog steeds oplopend op doos --');
  const gedeeld = await page.evaluate(() => {
    S.gram = {};
    const alle = gcGeordend().map((c) => c.id);
    // het sterkste doosje wacht het langst: de leerrij draait ze om, de wachtrij niet
    S.gram[gramSleutel(alle[0], 0)] = { box: 4, due: today(), goed: 12, fout: 1, bd: addDays(today(), -30) };
    S.gram[gramSleutel(alle[1], 0)] = { box: 0, due: today(), goed: 2, fout: 2, bd: today() };
    const w = gramWachtrij(), l = gramLeerRij();
    return { wachtDoos: w[0] && (w[0].st.box || 0), leerDoos: l[0] && (l[0].st.box || 0) };
  });
  ok(gedeeld.wachtDoos === 0, 'gramWachtrij() zet het zwakste doosje vooraan (doos ' + gedeeld.wachtDoos + ')');
  ok(gedeeld.leerDoos === 4, 'en de leerrij zet juist het langst wachtende vooraan (doos ' + gedeeld.leerDoos + ')');

  // ---- 6. het onderhoud staat nog steeds achteraan, en alleen als er iets vervalt ----
  console.log('\n-- 6. het onderhoud dringt niet voor (v23.235) --');
  const oh = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null;
    const alle = gcGeordend().map((c) => c.id);
    // drie zwakke doosjes die het langst wachten: die vullen de drie leerbeurten
    alle.slice(0, 3).forEach((id, k) => {
      S.gram[gramSleutel(id, 0)] = { box: 0, due: today(), goed: 2, fout: 1, bd: addDays(today(), -20 + k) };
    });
    // en een vervallen doos-4-onderwerp dat korter wacht, dus de rotatie komt er niet aan toe.
    // Precies waar de onderhoudsbeurt van v23.235 voor is.
    const oud = alle[5];
    S.gram[gramSleutel(oud, 0)] = { box: 4, due: addDays(today(), -4), goed: 15, fout: 1, bd: addDays(today(), -9) };
    const kaal = (x) => String(x || '').replace(/^(opfris|concept)-/, '').split('#')[0];
    const met = lesFlowGramLijst();
    const plek = met.map(kaal).indexOf(oud);
    S.gram[gramSleutel(oud, 0)].due = addDays(today(), 20);   // niets meer vervallen
    const zonder = lesFlowGramLijst();
    return { plek: plek, n: met.length, nZonder: zonder.length, oud: oud, met: met.map(kaal) };
  });
  ok(oh.plek === oh.n - 1, 'het vervallen doos-4-onderwerp staat achteraan (plek ' + (oh.plek + 1) + ' van ' + oh.n + ': ' + oh.met.join(', ') + ')');
  ok(oh.nZonder === oh.n - 1, 'en valt weg zodra er niets meer vervallen is: ' + oh.nZonder + ' tegenover ' + oh.n);

  // ---- 7. en een sterk doosje wint gewoon een leerbeurt zodra het het langst wacht ----
  //
  // Dit is de andere helft van v23.235. Daar kon doos 4 alleen nog via de onderhoudsbeurt aan bod
  // komen omdat de leerbeurt altijd het zwakste pakte. Nu kan hij ook de leerbeurt winnen, en dat is
  // wat Stefan vroeg: "oude grammatica volgens spaced repetition toetsen".
  console.log('\n-- 7. een sterk doosje dat het langst wacht, wint gewoon een leerbeurt --');
  const sterk = await page.evaluate(() => {
    S.gram = {}; S.gramFocus = null;
    const alle = gcGeordend().map((c) => c.id);
    alle.slice(0, 3).forEach((id) => {
      S.gram[gramSleutel(id, 0)] = { box: 0, due: today(), goed: 2, fout: 1, bd: addDays(today(), -2) };
    });
    const oud = alle[5];
    S.gram[gramSleutel(oud, 0)] = { box: 4, due: addDays(today(), -4), goed: 15, fout: 1, bd: addDays(today(), -40) };
    const kaal = (x) => String(x || '').replace(/^(opfris|concept)-/, '').split('#')[0];
    const lijst = lesFlowGramLijst();
    return { eerste: kaal(lijst[0]), oud: oud, lijst: lijst.map(kaal) };
  });
  ok(sterk.eerste === sterk.oud, 'het doosje van veertig dagen geleden staat vooraan, ook al staat het op doos 4 (' + sterk.lijst.join(', ') + ')');

  ok(errs.length === 0, 'geen JS-fouten tijdens de hele test (' + errs.slice(0, 2).join(' | ') + ')');

  await browser.close();
  console.log(fout === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
