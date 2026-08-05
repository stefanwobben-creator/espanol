// Playwright-test voor het meereizende podium (v19.78).
//
// Stefan: "als je bijv chispa willen laten dansen, dan kan dat alleen zie je het nooit, alle
// acties voor chispa staan beneden terwijl het effect van de actie boven gebeurt."
//
// Dat is geen schoonheidsfoutje maar een kapotte lus: je doet iets en krijgt geen antwoord.
// Een knop waarvan je het gevolg niet ziet, voelt als een knop die stuk is. Wat hier vastligt
// is dus niet "er is een balk" maar "handeling en gevolg staan tegelijk in beeld":
//   1. zolang je haar gewoon ziet, is er geen balk (anders is het een banner)
//   2. zodra ze uit beeld is, staat ze bovenaan
//   3. wat je onderaan doet, gebeurt in die balk: dansen, kleren, kleur
//   4. de balk duwt niets opzij en hoort alleen bij haar eigen pagina
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 430, height: 860 } });
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

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwBalk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // Een gegroeide Chispa met alles in de kast, zodat er iets te zien valt.
  await page.evaluate(() => {
    window.chispaSlaapt = function () { return false; };
    window.petMoodKey = function () { return 'happy'; };
    S.txp = PET_LEVELS[6].min + 5;
    SHOP.forEach(function (it) { S.owned[it.id] = true; });
    show('chispa');
  });
  await page.waitForTimeout(1600);
  await page.evaluate(() => { try { chispaStop(); } catch (e) {} });
  await page.waitForTimeout(200);

  // --- 1. Bovenaan is er geen balk ---
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(400);
  const boven = await page.evaluate(() => ({
    bestaat: !!document.getElementById('chispaBalk'),
    aan: document.getElementById('chispaBalk').classList.contains('aan'),
    petZichtbaar: document.getElementById('petBox').getBoundingClientRect().bottom > 0
  }));
  ok(boven.bestaat, 'het podium bestaat in de pagina');
  ok(boven.petZichtbaar && !boven.aan, 'zolang je Chispa gewoon ziet, staat er niets bovenaan');

  // --- 2. Uit beeld: ze komt naar je toe ---
  await page.evaluate(() => {
    const b = document.querySelector('button[data-baile]');
    if (b) b.scrollIntoView({ block: 'center' });
  });
  await page.waitForTimeout(600);
  const beneden = await page.evaluate(() => ({
    aan: document.getElementById('chispaBalk').classList.contains('aan'),
    petWeg: document.getElementById('petBox').getBoundingClientRect().bottom < 8,
    svg: document.getElementById('balkBox').innerHTML.indexOf('<svg') !== -1,
    fase: (document.getElementById('balkFase').textContent || '').trim(),
    vast: getComputedStyle(document.getElementById('chispaBalk')).position
  }));
  ok(beneden.petWeg && beneden.aan, 'zodra ze uit beeld is, staat ze bovenaan');
  ok(beneden.svg, 'en het is echt zij, geen plaatje van een axolotl in het algemeen');
  ok(/adulta|abuela|joven|ni/i.test(beneden.fase) || beneden.fase.length > 2,
     'de balk zegt in welke levensfase ze is (' + beneden.fase + ')');
  ok(beneden.vast === 'fixed', 'de balk hangt aan het scherm, niet aan de pagina');

  // --- 3. De hele pagina schuift niet op als de balk verschijnt ---
  const hoogtes = await page.evaluate(() => {
    const h1 = document.body.scrollHeight;
    document.getElementById('chispaBalk').classList.remove('aan');
    const h2 = document.body.scrollHeight;
    document.getElementById('chispaBalk').classList.add('aan');
    return { h1: h1, h2: h2 };
  });
  ok(hoogtes.h1 === hoogtes.h2, 'de balk duwt niets opzij: de pagina blijft even hoog');

  // --- 4. Dansen gebeurt waar je kijkt ---
  await page.evaluate(() => {
    const b = document.querySelector('button[data-baile="flamenco"]') || document.querySelector('button[data-baile]');
    if (b) b.click();
  });
  await page.waitForTimeout(700);
  const dans = await page.evaluate(() => ({
    balk: document.getElementById('balkBox').className,
    pet: document.getElementById('petBox').className,
    props: document.getElementById('balkProps').children.length,
    onder: document.getElementById('chispaProps') ? document.getElementById('chispaProps').children.length : -1
  }));
  ok(/chbezig/.test(dans.balk), 'de dans zit op het podium in beeld, niet op de kaart eronder');
  ok(CHISPA_MOVES_TEST(dans.balk), 'en het is een echte danspas, geen los klassenaampje');
  ok(!/chbezig/.test(dans.pet), 'de kaart onderaan danst niet mee: er is er maar één tegelijk');
  ok(dans.props >= 2, 'de noten en de gitaar spelen ook boven mee (' + dans.props + ')');

  function CHISPA_MOVES_TEST(kl) {
    return /ch(giro|salto|salsa|flamenco|cumbia|merengue|bachata|tango|dembow|jarabe|guitarra)/.test(kl);
  }

  // --- 5. Terugscrollen tijdens de dans neemt de dans mee ---
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(500);
  const terug = await page.evaluate(() => ({
    aan: document.getElementById('chispaBalk').classList.contains('aan'),
    pet: document.getElementById('petBox').className,
    balk: document.getElementById('balkBox').className
  }));
  ok(!terug.aan, 'ben je weer bij haar, dan gaat het podium weg');
  ok(/chbezig/.test(terug.pet) && !/chbezig/.test(terug.balk),
     'de dans verhuist mee terug naar de kaart in plaats van halverwege te stoppen');
  await page.waitForTimeout(4200);
  const naDans = await page.evaluate(() => ({
    pet: document.getElementById('petBox').className,
    balk: document.getElementById('balkBox').className
  }));
  ok(!/chbezig/.test(naDans.pet) && !/chbezig/.test(naDans.balk),
     'en na afloop blijft er op geen van beide podia een danspas hangen');

  // --- 5b. De knop indrukken doet het podium zelf omhoog komen ---
  // Dit is het scherpste geval en tegelijk het echte: je staat bovenaan, tikt op een dansknop
  // die onderaan staat, en de pagina schuift mee terwijl je tikt. Dan wisselt het podium tussen
  // het indrukken en het dansen in. De dansvloer en de noten moeten die wissel meemaken, anders
  // danst ze boven in beeld terwijl haar vloer beneden ligt te gloeien waar niemand kijkt.
  await page.evaluate(() => { window.scrollTo(0, 0); try { chispaStop(); } catch (e) {} });
  await page.waitForTimeout(500);
  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(600);
  const meeVerhuisd = await page.evaluate(() => {
    const laag = chispaPropLaag();
    const anders = chispaPropLagen().filter(function (l) { return l !== laag; })[0];
    return {
      welk: laag ? laag.id : '(geen)',
      vloer: laag ? laag.querySelectorAll('.chvloer').length : -1,
      noten: laag ? laag.querySelectorAll('.chnota').length : -1,
      achter: anders ? anders.children.length : -1
    };
  });
  ok(meeVerhuisd.welk === 'balkProps', 'de knop indrukken brengt het podium omhoog (' + meeVerhuisd.welk + ')');
  ok(meeVerhuisd.vloer === 1 && meeVerhuisd.noten >= 1,
     'en haar dansvloer en noten verhuizen mee naar boven (' + meeVerhuisd.vloer + ' vloer, ' + meeVerhuisd.noten + ' noten)');
  ok(meeVerhuisd.achter === 0, 'er blijft niets gloeien op het podium dat je verliet');
  await page.evaluate(() => { try { chispaStop(); } catch (e) {} });
  await page.waitForTimeout(300);

  // --- 6. Kleren omdoen zie je meteen, ook al ligt de kast onderaan ---
  await page.evaluate(() => {
    const b = document.querySelector('#kastBlok button[data-wear="corona"]');
    if (b) b.scrollIntoView({ block: 'center' });
  });
  await page.waitForTimeout(600);
  const voorKroon = await page.evaluate(() => document.getElementById('balkBox').innerHTML);
  await page.evaluate(() => {
    const b = document.querySelector('#kastBlok button[data-wear="corona"]');
    if (b) b.click();
  });
  await page.waitForTimeout(600);
  const naKroon = await page.evaluate(() => ({
    html: document.getElementById('balkBox').innerHTML,
    aan: document.getElementById('chispaBalk').classList.contains('aan'),
    wear: !!S.wear.corona
  }));
  ok(naKroon.wear && naKroon.aan, 'de kroon gaat op terwijl je onderaan bij de kast staat');
  ok(naKroon.html.length > voorKroon.length + 60,
     'en je ziet hem bovenaan meteen op haar hoofd verschijnen (' + voorKroon.length + ' -> ' + naKroon.html.length + ')');

  // --- 7. Hetzelfde voor haar kleur ---
  await page.evaluate(() => {
    const b = document.querySelector('#kleurRij button[data-kleur]:not(.aan)');
    if (b) b.scrollIntoView({ block: 'center' });
  });
  await page.waitForTimeout(500);
  const kleur = await page.evaluate(() => {
    const voor = document.getElementById('balkBox').innerHTML;
    const b = document.querySelector('#kleurRij button[data-kleur]:not(.aan)');
    const id = b ? b.getAttribute('data-kleur') : '';
    if (b) b.click();
    return { voor: voor, id: id };
  });
  await page.waitForTimeout(600);
  const kleurNa = await page.evaluate(() => document.getElementById('balkBox').innerHTML);
  ok(kleur.id && kleurNa !== kleur.voor, 'een andere kleur kiezen kleurt haar bovenaan mee (' + kleur.id + ')');

  // --- 8. De balk brengt je terug naar haar ---
  await page.evaluate(() => { const b = document.getElementById('chispaBalkIn'); if (b) b.click(); });
  await page.waitForTimeout(1200);
  const naKlik = await page.evaluate(() => ({
    top: document.getElementById('petBox').getBoundingClientRect().top,
    aan: document.getElementById('chispaBalk').classList.contains('aan')
  }));
  ok(naKlik.top > -50 && naKlik.top < 400, 'op de balk tikken brengt je terug bij Chispa zelf');
  ok(!naKlik.aan, 'en dan verdwijnt hij weer, want je kijkt haar nu gewoon aan');

  // --- 9. Hij hoort bij haar pagina en gaat niet mee naar de woordjes ---
  await page.evaluate(() => {
    const b = document.querySelector('button[data-baile]');
    if (b) b.scrollIntoView({ block: 'center' });
  });
  await page.waitForTimeout(500);
  const voorWissel = await page.evaluate(() => document.getElementById('chispaBalk').classList.contains('aan'));
  await page.evaluate(() => show('woorden'));
  await page.waitForTimeout(500);
  const naWissel = await page.evaluate(() => document.getElementById('chispaBalk').classList.contains('aan'));
  ok(voorWissel && !naWissel, 'wie naar de woordjes gaat, neemt het podium niet mee');

  // --- 10. Geen JS-fouten in eigen code ---
  const eigen = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(eigen.length === 0, 'geen JS-fouten tijdens de hele test (' + eigen.length + ' gevonden)');
  if (eigen.length) eigen.slice(0, 4).forEach((e) => console.log('   ', e));

  await browser.close();
  if (fails === 0) console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
  else { console.log('\n' + fails + ' TESTS GEFAALD'); process.exit(1); }
})();
