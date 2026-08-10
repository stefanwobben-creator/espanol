// Playwright-test voor de opsplitsing van Chispa's pagina in v19.70.
// Stefan: "chispa begint beetje rommelig scherm te worden."
// Dat kwam niet door de hoeveelheid maar doordat één kolom vier dingen tegelijk deed. Elke kaart
// heeft nu precies één taak, en dat is wat hier vastligt zodat een latere versie het niet
// stilletjes weer op één hoop gooit:
//   1. petCard     - het dier zelf: hoe ze eruitziet, hoe ze zich voelt, wat ze wil, wat je kunt doen
//   2. groeiCard   - haar groei plus de kledingkast (kleren gaan over hoe ze eruitziet)
//   3. vitrineCard - de twee verzamelingen: tapas en dansen, elk in een eigen vak met een teller
//   4. kamerCard   - haar kamer
// En: de straattaal staat NIET meer op deze pagina, want dat is een woordles.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  const BASIS = 'http://localhost:8321/espanol-stefan.html';
  await page.goto(BASIS);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(BASIS);
  await page.waitForTimeout(600);

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwKaarten' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // Chispa moet wakker zijn, anders slaat de pagina de helft van haar reacties over
  await page.evaluate(() => {
    window.chispaSlaapt = function () { return false; };
    S.txp = 4000;            // ver genoeg om ook de kamer wat te laten tonen
    S.tapas = 12;
    S.owned = S.owned || {};
    S.owned[SHOP[0].id] = true;   // kleren komen van lessen; er hoeft er maar één open te staan
    show('chispa');
  });
  await page.waitForTimeout(600);

  // --- 1. Vier kaarten, in deze volgorde, en de oude winkel is weg ---
  const bouw = await page.evaluate(() => {
    const ids = ['petCard', 'groeiCard', 'vitrineCard', 'kamerCard'];
    const kids = Array.prototype.slice.call(document.getElementById('tab-chispa').children);
    return {
      pos: ids.map((i) => kids.indexOf(document.getElementById(i))),
      gevuld: ids.map((i) => (document.getElementById(i) || { innerHTML: '' }).innerHTML.length > 60),
      shop: !!document.getElementById('shopCard'),
      shopFn: typeof window.renderShop
    };
  });
  ok(bouw.pos.every((p) => p > -1), 'alle vier de kaarten staan in tab-chispa (' + bouw.pos.join(',') + ')');
  ok(bouw.pos[0] < bouw.pos[1] && bouw.pos[1] < bouw.pos[2] && bouw.pos[2] < bouw.pos[3],
    'in de volgorde: het dier, haar groei, de vitrine, haar kamer');
  /* v23.33: de vitrinekaart is leeg sinds de twee verzamelingen bij Chispa zelf staan. Hij blijft
     als element bestaan (schermen en suites verwijzen ernaar) maar hij toont niets. */
  ok(bouw.gevuld[0] && bouw.gevuld[1] && bouw.gevuld[3],
    'het dier, haar groei en haar kamer zijn gevuld (' + bouw.gevuld.join(',') + ')');
  ok(!bouw.gevuld[2], 'en de vitrinekaart is leeg, want zijn inhoud staat nu bij haar');
  ok(!bouw.shop, 'de oude verzamelkaart #shopCard bestaat niet meer');
  ok(bouw.shopFn === 'undefined', 'en renderShop() is helemaal opgeruimd, geen slapende tweede winkel');

  // --- 2. Kaart 1 gaat alleen over Chispa zelf ---
  const pet = await page.evaluate(() => {
    const c = document.getElementById('petCard');
    return {
      dier: c.querySelectorAll('#petBox svg').length,
      naam: c.querySelectorAll('.petname').length,
      stemming: c.querySelectorAll('.petmood').length,
      wens: c.querySelectorAll('#wensRij').length,
      knoppen: ['btnFiesta', 'btnSerenade', 'btnCadeau'].filter((i) => !!c.querySelector('#' + i)).length,
      mezcla: !!c.querySelector('#mezclaStrip'),
      tapachips: c.querySelectorAll('.tapachip').length,
      bailechips: c.querySelectorAll('.bailechip').length,
      shopitems: c.querySelectorAll('.shopitem').length,
      badge: c.querySelectorAll('.tapabadge').length,
      jerga: c.querySelectorAll('.jergaes').length
    };
  });
  ok(pet.dier >= 1 && pet.naam === 1 && pet.stemming === 1 && pet.wens === 1, 'kaart 1: het dier, haar naam, stemming en wens');
  /* v23.35, op Stefans verzoek: de knoppenrij Fiesta/Serenade/Dagcadeautje is weg. Wat je met haar
     doet staat in de twee rijen (een tapa geven, laten dansen) en in de mezcla ertussen; aaien doe je
     door haar aan te tikken. Deze suite bewaakt vanaf nu dat er iets te doen is, niet dat er precies
     drie knoppen staan. */
  ok(pet.knoppen === 0, 'kaart 1: geen losse knoppenrij meer (' + pet.knoppen + ')');
  ok(pet.mezcla, 'kaart 1: de mezcla staat er wel, want dat is wat je hier doet');
  /* v23.33 draait v19.70 op dit punt om, en dat is een besluit en geen slordigheid. Toen zijn de
     verzamelingen bij Chispa weggehaald omdat er tussen haar voeten ook een kledingkast, een kamer
     en een straattaalles stonden; dat blijft weg. Maar de tapas en de dansen zijn precies de twee
     dingen die je mét haar doet, en die stonden twee kaarten lager dan het dier waar ze over gaan.
     Wat deze suite nu bewaakt is de grens die er echt toe doet: doen mag hier, bezit en beheer niet. */
  ok(pet.tapachips >= 12 && pet.bailechips >= 4,
     'kaart 1: de tapas en de dansen staan bij haar, want daar geef je ze (' + pet.tapachips + '/' + pet.bailechips + ')');
  ok(pet.shopitems === 0 && pet.badge === 0, 'kaart 1: geen kledingkast, geen kamer, geen tapateller');
  ok(pet.jerga === 0, 'kaart 1: geen straattaalles; dat is geen onderdeel van wie ze is');

  // --- 3. Kaart 2 is de groei, met de kledingkast erbij ---
  const groei = await page.evaluate(() => {
    const c = document.getElementById('groeiCard');
    return {
      balk: c.querySelectorAll('.goalbar').length,
      wear: c.querySelectorAll('button[data-wear]').length,
      rincon: c.querySelectorAll('button[data-rincon]').length,
      tekst: c.innerText
    };
  });
  ok(groei.balk === 1, 'kaart 2: één balk die laat zien hoever de volgende vorm nog is');
  ok(/Vorm \d+\/\d+|Form \d+\/\d+/.test(groei.tekst), 'kaart 2: welke vorm van hoeveel je nu hebt');
  ok(groei.wear > 0, 'kaart 2: de kledingkast staat hier (' + groei.wear + ' te dragen)');
  ok(groei.rincon === 0, 'kaart 2: en de kamer nadrukkelijk niet');

  // --- 4. De verzamelingen: twee vakken, twee tellers, nu in kaart 1 ---
  const vit = await page.evaluate(() => {
    const c = document.getElementById('petCard');
    const leeg = document.getElementById('vitrineCard');
    return {
      vakken: c.querySelectorAll('.vitrinevak').length,
      tapas: c.querySelectorAll('.tapachip').length,
      bailes: c.querySelectorAll('.bailechip').length,
      tapaTel: !!c.querySelector('#tapaTel'),
      baileTel: !!c.querySelector('#baileTel'),
      hoy: c.querySelectorAll('.tapachip.hoy').length + c.querySelectorAll('.bailechip.hoy').length,
      shopitems: c.querySelectorAll('.shopitem').length,
      vitrineLeeg: !!leeg && leeg.classList.contains('hidden') && leeg.innerText.trim() === '',
      teller: (c.querySelector('#tapaTel') || {}).innerText || ''
    };
  });
  ok(vit.vakken === 2, 'twee vakken onder elkaar (' + vit.vakken + ')');
  ok(vit.tapas >= 12 && vit.bailes >= 4, 'alle tapas en alle dansen staan er (' + vit.tapas + '/' + vit.bailes + ')');
  ok(vit.tapaTel && vit.baileTel, 'elke verzameling heeft een eigen teller');
  ok(vit.hoy === 2, 'de tapa én de dans van vandaag zijn aangewezen (' + vit.hoy + ')');
  ok(vit.shopitems === 0, 'hier valt niets te kopen, alleen te geven');
  ok(vit.vitrineLeeg, 'de oude vitrinekaart is leeg en uit beeld, niet blijven staan met een kop erboven');
  /* v23.33: op Stefans scherm stond "Chispa proefde 29 van de 18 tapas". S.tapaMenu bewaart ids en
     TAPAS is sindsdien veranderd; de teller telde alles wat er ooit in kwam. Dezelfde fout als de
     luisterteller van v22.10, en hij ziet er als een prestatie uit, dus je merkt hem nooit. */
  const gek = await page.evaluate(() => {
    S.tapaMenu = (S.tapaMenu || []).concat(['bestaat-niet-1', 'bestaat-niet-2']);
    renderPet();
    const t = (document.getElementById('tapaTel') || {}).innerText || '';
    const m = t.match(/(\d+)\D+(\d+)/);
    return { tekst: t, gehad: m ? +m[1] : -1, totaal: m ? +m[2] : -1, tapas: TAPAS.length };
  });
  ok(gek.totaal === gek.tapas && gek.gehad <= gek.totaal,
     'de teller kan nooit boven zijn eigen noemer uitkomen (' + gek.tekst.slice(0, 60) + ')');

  // --- 5. Kaart 4 is de kamer ---
  const kamer = await page.evaluate(() => {
    const c = document.getElementById('kamerCard');
    return {
      badge: c.querySelectorAll('.tapabadge').length,
      rincon: c.querySelectorAll('button[data-rincon]').length,
      wear: c.querySelectorAll('button[data-wear]').length,
      items: c.querySelectorAll('.shopitem').length
    };
  });
  ok(kamer.badge === 1, 'kaart 4: hier staat je tapavoorraad, waar je hem uitgeeft');
  ok(kamer.items > 0 && kamer.rincon > 0, 'kaart 4: de spullen voor de kamer (' + kamer.items + ' items)');
  ok(kamer.wear === 0, 'kaart 4: geen kleren; die horen bij hoe ze eruitziet');

  // --- 6. De kaarten kijken naar dezelfde cijfers en verversen samen ---
  const samen = await page.evaluate(() => {
    S.tapaMenu = [];
    renderChispaPagina();
    const voor = document.querySelectorAll('#petCard .tapachip.gehad').length;
    S.tapaMenu = [TAPAS[0].id, TAPAS[1].id, TAPAS[2].id];
    renderChispaPagina();
    return { voor: voor, na: document.querySelectorAll('#petCard .tapachip.gehad').length };
  });
  ok(samen.voor === 0 && samen.na === 3, 'een gegroeide verzameling is meteen zichtbaar (' + samen.voor + ' -> ' + samen.na + ')');

  // --- 7. Kleren aantrekken werkt nog en tekent Chispa opnieuw ---
  const kleding = await page.evaluate(() => {
    const b = document.querySelector('#groeiCard button[data-wear]');
    const id = b.getAttribute('data-wear');
    const voor = b.textContent;
    b.click();
    const b2 = document.querySelector('#groeiCard button[data-wear="' + id + '"]');
    return { voor: voor, na: b2 ? b2.textContent : '', aan: !!S.wear[id], dier: document.querySelectorAll('#petCard #petBox svg').length };
  });
  ok(kleding.aan && kleding.voor !== kleding.na, 'een kledingstuk aandoen wisselt de knop ("' + kleding.voor + '" -> "' + kleding.na + '")');
  ok(kleding.dier >= 1, 'en Chispa staat er daarna nog steeds');

  // --- 8. Geen JS-fouten in eigen code ---
  // netwerkruis (favicon 404, geblokkeerde externe tunnels naar sync/audio-CDN in deze sandbox)
  const eigen = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(eigen.length === 0, 'geen JS-fouten tijdens de hele test (' + eigen.length + ' gevonden)');
  if (eigen.length) eigen.slice(0, 4).forEach((e) => console.log('   ', e));

  await browser.close();
  if (fails === 0) console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
  else { console.log('\n' + fails + ' TESTS GEFAALD'); process.exit(1); }
})();
