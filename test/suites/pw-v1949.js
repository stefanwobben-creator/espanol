// Playwright-test voor v19.49 - drie van Stefans zes wensen die UI raken:
//   2. "zou chispa ook in de interface terug komen komen bijv na de onboarding bij je eerste les?"
//      -> mini-Chispa in de dagles-banner (één plek, twaalf views), met een Spaanse regel per stap
//         en een aparte begroeting bij je allereerste les.
//   4. "welke mechanics van tamagotchi kan je beter toepassen op chispa doe dat"
//      -> hongermeter die per dag oploopt, dagwens die Chispa zélf stelt, zorgreeks, nachtstand.
//   6. "bij de familie zou je een krabbel acher kunnen latne met een hyes banaan bij een
//      familie/teamlid, maar alleen in het spaans" -> vaste Spaanse krabbels, geen vrij tekstveld.
// De sandbox kan Render niet bereiken, dus /api/* geeft hier altijd null: de krabbel-test stubt
// window.api zodat de renderlogica toch getest wordt, en checkt daarna de offline-fallback.
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

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);

  await page.fill('input[placeholder="Name"]', 'PwV1949' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(400);

  /* ---------------- verzoek 2: Chispa loopt mee door de dagles ---------------- */
  await page.evaluate(() => { lesFlow = { stap: null, quizzesTeDoen: [], gekozenSpel: null, vertalenTeGaan: 0 }; lesFlowVolgende(); });
  await page.waitForTimeout(500);
  ok(await page.evaluate(() => lesFlow && lesFlow.stap === 'woorden'), 'de dagles start op de woordjes-stap');
  ok(await page.locator('#btnLesFlowChispa').count() === 1, 'Chispa staat in de dagles-banner, niet meer alleen in haar eigen tabje');
  ok(await page.locator('#btnLesFlowChispa svg').count() === 1, 'het is echt haar sprite (svg) en geen emoji-plaatsvervanger');
  // v19.66: Chispa staat sinds deze versie óók op de dagkaart zelf (de begroeting vóór je begint),
  // dus .lfsay komt nu twee keer voor. Deze test gaat over de banner ín de les: scope hem daarop.
  const zegtEerste = await page.locator('.lfrow:has(#btnLesFlowChispa) .lfsay .es').first().innerText();
  ok(/Soy Chispa/.test(zegtEerste), 'bij je allereerste les stelt ze zich eerst voor (' + zegtEerste + ')');

  // per stap een andere Spaanse regel: dat maakt haar aanwezigheid informatief i.p.v. decoratief
  const regels = await page.evaluate(() => {
    const uit = {};
    ['woorden', 'grammatica', 'toetsjes', 'produceren'].forEach((s) => {
      lesFlow.stap = s;
      uit[s] = lesFlowChispaFrase().es;
    });
    return uit;
  });
  const unieke = Object.keys(regels).map((k) => regels[k]).filter((v, i, a) => a.indexOf(v) === i);
  ok(unieke.length === 4, 'elke stap heeft zijn eigen Spaanse regel (' + unieke.length + '/4 uniek)');
  ok(/gram/i.test(regels.grammatica), 'bij de grammatica-stap zegt ze iets over grammatica (' + regels.grammatica + ')');

  // zonder actieve dagles geen banner, dus ook geen zwevende Chispa
  // let op: het is niet genoeg om een ánder tabblad te hertekenen, want verborgen tabs blijven in de
  // DOM staan. We hertekenen de view waar de banner net nog stond (show('woorden') -> renderWord()).
  await page.evaluate(() => { lesFlow = null; show('woorden'); });
  await page.waitForTimeout(200);
  ok(await page.locator('#btnLesFlowChispa').count() === 0, 'buiten de dagles verschijnt de banner-Chispa niet');

  /* ---------------- verzoek 4: Tamagotchi-mechanics ---------------- */
  await page.evaluate(() => show('chispa'));
  await page.waitForTimeout(300);
  // v19.63: de hongermeter is eruit. Een leeg buikje is een verwijt, en dan kom je terug uit
  // schuld. De dagwens, de nachtstand en het voeren blijven wél staan.
  ok(await page.locator('#hongerBar').count() === 0, 'er is geen hongermeter meer');
  ok(await page.locator('#hongerLabel').count() === 0, 'en ook geen buikje-percentage');
  ok(await page.evaluate(() => typeof chispaHonger) === 'undefined', 'chispaHonger() bestaat niet meer');
  ok(await page.locator('#wensRij').count() === 1, 'Chispa stelt zelf een wens voor vandaag');

  const moods = await page.evaluate(() => {
    const uit = {};
    const t = today();
    S.xp = {}; S.fed = t;                     uit.netGevoerd = petMoodKey();
    S.fed = ''; S.xp[t] = 20;                 uit.geoefend = petMoodKey();
    S.xp = {}; S.fed = addDays(t, -40);       uit.langWeg = petMoodKey();
    uit.tekst = petMoodText();
    return uit;
  });
  ok(moods.netGevoerd === 'happy', 'net gevoerd = blije Chispa');
  ok(moods.geoefend === 'happy', 'vandaag geoefend maakt haar net zo blij, ook zonder tapa');
  ok(moods.langWeg === 'ok', 'veertig dagen weggebleven levert een rustige Chispa op, geen chagrijnige');
  ok(!/honger|rammel/i.test(moods.tekst), 'ze verwijt je niets over eten (' + moods.tekst + ')');

  // 2. nachtstand: gebaseerd op het uur, en zonder straf (Stefan leert 's avonds laat)
  const nacht = await page.evaluate(() => ({
    middag: chispaSlaapt(14), avond: chispaSlaapt(21), nacht: chispaSlaapt(2), ochtend: chispaSlaapt(8)
  }));
  ok(!nacht.middag && !nacht.avond && nacht.nacht && !nacht.ochtend, 'Chispa slaapt \'s nachts en is \'s avonds nog wakker');

  // 3. de dagwens: vervullen levert een tapa op, en kan maar één keer per dag
  const wens = await page.evaluate(() => {
    S.zorg = {}; S.tapas = 5; S.fed = '';
    const w = chispaWens();
    const voor = S.tapas;
    const eerst = chispaWensDoe(w.id);
    const na = S.tapas;
    const tweedeKeer = chispaWensDoe(w.id);
    const anderId = CHISPA_WENSEN.filter((x) => x.id !== w.id)[0].id;
    S.zorg.wensOp = '';
    const verkeerde = chispaWensDoe(anderId);
    return { id: w.id, es: w.es, eerst, na: na - voor, tweedeKeer, verkeerde, aantal: CHISPA_WENSEN.length };
  });
  ok(wens.eerst === true && wens.na === 1, 'de dagwens vervullen levert een tapa terug op');
  ok(wens.tweedeKeer === false, 'dezelfde wens kan niet twee keer op één dag verzilverd worden');
  ok(wens.verkeerde === false, 'een andere handeling dan de gevraagde vervult de wens niet (ze vraagt echt iets specifieks)');
  /* v23.35: de wens "haar cadeautje openmaken" is weg omdat de knop weg is, en een wens die je niet
     kunt vervullen is erger dan geen wens. Er blijven er drie, en die kunnen alle drie: een tapa
     geven, laten dansen, aaien. */
  ok(wens.aantal >= 3 && /^¡/.test(wens.es) === false && /Chispa/.test(wens.es), 'de wens staat in het Spaans (' + wens.es + ')');

  // 4. v19.63: de zorgreeks kon breken. Nu is het het aantal dagen dat je samen iets deed,
  //    en dat kan alleen oplopen: wegblijven kost niets.
  const reeks = await page.evaluate(() => {
    S.zorg = { reeks: 0, beste: 0, laatst: '', wensOp: '' };
    const na1 = chispaZorgTik();
    const nogmaals = chispaZorgTik();          // tweede keer vandaag verandert niets
    S.zorg.laatst = addDays(today(), -1); S.zorg.reeks = 4;
    const doorgeteld = chispaZorgTik();        // gisteren gezorgd -> gewoon +1
    S.zorg.laatst = addDays(today(), -300); S.zorg.reeks = 9;
    const naLangWeg = chispaZorgReeks();       // driehonderd dagen niets: het getal staat er nog
    const opnieuw = chispaZorgTik();           // en loopt door waar je gebleven was
    return { na1, nogmaals, doorgeteld, naLangWeg, opnieuw, beste: S.zorg.beste };
  });
  ok(reeks.na1 === 1 && reeks.nogmaals === 1, 'het aantal dagen samen tikt maximaal één keer per dag');
  ok(reeks.doorgeteld === 5, 'een dag erbij is gewoon +1 (' + reeks.doorgeteld + ')');
  ok(reeks.naLangWeg === 9, 'na driehonderd dagen weg staat het getal er nog steeds (' + reeks.naLangWeg + ')');
  ok(reeks.opnieuw === 10, 'terugkomen telt door waar je gebleven was, het valt nooit terug naar nul');
  ok(reeks.beste >= 9, 'je hoogste stand blijft bewaard (' + reeks.beste + ')');

  // een tapa geven is nog steeds gewoon een tapa geven, plus een dag samen erbij
  const feed = await page.evaluate(() => {
    S.tapas = 3; S.fed = addDays(today(), -2); S.zorg = { reeks: 0, beste: 0, laatst: '', wensOp: '' };
    renderPet();
    feedPet();
    return { tapas: S.tapas, fed: S.fed === today(), reeks: chispaZorgReeks() };
  });
  ok(feed.tapas === 2 || feed.tapas === 3, 'een tapa geven kost een tapa (en kan er via de wens één teruggeven)');
  ok(feed.fed, 'na het voeren staat de dag van voeren op vandaag');
  ok(feed.reeks === 1, 'voeren telt als een dag samen');

  await page.waitForTimeout(200);
  const gloed = await page.evaluate(() => {
    S.zorg = { reeks: 4, beste: 4, laatst: today(), wensOp: '' };
    renderPet();
    const aan = document.querySelector('#petCard .petstage');
    const glowAan = !!(aan && aan.classList.contains('zorgglow'));
    S.zorg.laatst = addDays(today(), -3);
    renderPet();
    const uit = document.querySelector('#petCard .petstage');
    return { glowAan, glowUit: !!(uit && uit.classList.contains('zorgglow')), badge: !!document.getElementById('zorgReeks') };
  });
  ok(gloed.glowAan, 'wie er vandaag was ziet Chispa oplichten');
  ok(!gloed.glowUit, 'en anders licht ze niet op: aandacht wordt beloond, afwezigheid niet bestraft');
  ok(!gloed.badge, 'er hangt geen reeks-badge meer onder die je kwijt kunt raken');

  /* ---------------- verzoek 6: krabbels, alleen in het Spaans ----------------
     v22.9: dit werd getest op het familie-klassement, en dat scherm is opgeheven (geen competitie).
     De wens erachter staat nog fier overeind en is verhuisd naar de muur: je kunt een schouderklopje
     achterlaten, en je kunt daarbij niets anders dan Spaans. Dus wordt hij nu daar gecontroleerd. */
  const palet = await page.evaluate(() => {
    const uit = KRABBELS.map((k) => k.es);
    return { aantal: uit.length, teksten: uit };
  });
  ok(palet.aantal >= 8, 'er is genoeg keuze om iets persoonlijks te sturen (' + palet.aantal + ' krabbels)');
  ok(palet.teksten.some((t) => /plátano/i.test(t)), 'de banaan die Stefan vroeg zit erbij, als ¡Un plátano para ti!');
  ok(palet.teksten.some((t) => /Choca esos cinco/i.test(t)), 'de high-five zit erbij, als ¡Choca esos cinco!');
  const nlWoorden = /\b(je|een|voor|goed|hoi|gaan|hallo|knuffel)\b/i;
  ok(!palet.teksten.some((t) => nlWoorden.test(t)), 'geen enkele krabbel bevat Nederlands: alleen in het Spaans');

  // De muur bouwt de reactieknoppen uit datzelfde palet, en er is nergens een vrij tekstveld.
  const muur = await page.evaluate(() => {
    const vandaag = today();
    S.groepen = [{ gcode: 'gtest', naam: 'Proef' }];
    muurData = { ok: true, krabbels: [], spelers: [
      { naam: 'Elise', niveau: 'a2', txp: 900, wear: {}, baile: 'salsa', mijlpalen: {},
        oogst: { [vandaag]: { w: 4, z: 2 } } }
    ] };
    muurOpen = 'Elise|' + vandaag;
    const el = document.createElement('div');
    el.innerHTML = muurHtml();
    return {
      knoppen: el.querySelectorAll('[data-mk]').length,
      velden: el.querySelectorAll('input, textarea').length
    };
  });
  ok(muur.knoppen >= 8, 'de muur zet dat palet als knoppen neer (' + muur.knoppen + ')');
  ok(muur.velden === 0, 'er is geen vrij tekstveld: je kúnt niets anders dan Spaans achterlaten');

  const echte = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(echte.length === 0, 'geen JS-fouten in eigen app-code (' + echte.length + ' gevonden, ' + (errors.length - echte.length) + ' netwerkruis genegeerd)');
  if (echte.length) echte.forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
