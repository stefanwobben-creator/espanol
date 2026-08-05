// Playwright-test voor de acht levensfases van Chispa (v19.74).
//
// Stefan: "je moet iets van 7 stadia van het basis karakter tekenen. van ei, baby, peuter,
// kleuter, kind, tiener, volwassene, senior" en, bij het customizen: "maar het is nog steeds
// chispa".
//
// Die tweede zin is de eigenlijke opdracht. Acht verschillende tekeningen maken is makkelijk;
// acht tekeningen maken die alle acht hetzelfde dier zijn, is het punt. Wat hier dus vastligt
// is een spanning, geen lijst:
//   1. elke fase ziet er anders uit (anders is het geen groei)
//   2. elke levende fase heeft dezelfde herkenningsset: zes kieuwtakken, roze, twee ogen met
//      een lichtje, één brede mond (anders is het een ander dier)
//   3. de kaart vertelt eerlijk waar je bent: naam van de fase, "Vorm n/8", en wat er hierna komt
//   4. wat ze aanheeft volgt haar vorm mee, en gaat niet over haar gezicht heen
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

  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'PwFases' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // --- 1. Acht fases, oplopend, en het begin is dichtbij ---
  const fases = await page.evaluate(() => ({
    n: PET_LEVELS.length,
    namen: PET_LEVELS.map((l) => l.naam),
    drempels: PET_LEVELS.map((l) => l.min),
    lang: profLang()
  }));
  ok(fases.n === 8, 'Chispa heeft acht levensfases (' + fases.n + ')');
  ok(fases.namen[0] === 'huevo', 'het begint bij een ei');
  ok(fases.namen[7] === 'abuela sabia', 'en het eindigt bij een abuela, niet bij een rang');
  ok(fases.drempels.every((m, i) => i === 0 || m > fases.drempels[i - 1]), 'de drempels lopen op');
  ok(fases.drempels[1] <= 100, 'uit het ei kom je binnen een paar lessen (' + fases.drempels[1] + ' xp)');

  // --- 2. De groeikaart vertelt waar je bent en wat er hierna komt ---
  await page.evaluate(() => show('chispa'));
  await page.waitForTimeout(500);

  const kaart = await page.evaluate(() => {
    const uit = [];
    for (let i = 0; i < PET_LEVELS.length; i++) {
      S.txp = PET_LEVELS[i].min + 5;
      renderGroei(); renderPet();
      const g = document.getElementById('groeiCard');
      // v19.77: de kledingkast staat sinds deze versie in dezelfde kaart, en daar ligt nu een
      // kroon met de tekst "van een estrella". Dat is geen belofte van een dertiende rang maar
      // een kledingstuk, dus voor de vraag "wat belooft deze fase" hoort hij er niet bij.
      const gKlon = g ? g.cloneNode(true) : null;
      if (gKlon) { const k = gKlon.querySelector('#kastBlok'); if (k) k.remove(); }
      const pet = document.getElementById('petBox') || document.getElementById('petCard');
      uit.push({
        tekst: gKlon ? gKlon.innerText : '',
        svg: pet ? pet.innerHTML : '',
        naam: PET_LEVELS[i].naam
      });
    }
    return uit;
  });

  ok(kaart.every((k, i) => k.tekst.indexOf(k.naam) !== -1), 'elke fase noemt zichzelf bij naam op de kaart');
  const vormRe = fases.lang === 'en' ? /Form (\d)\/8/ : /Vorm (\d)\/8/;
  const nummers = kaart.map((k) => { const m = k.tekst.match(vormRe); return m ? +m[1] : 0; });
  ok(nummers.join(',') === '1,2,3,4,5,6,7,8', 'de teller loopt van 1/8 tot 8/8 (' + nummers.join(',') + ')');
  ok(kaart.slice(0, 7).every((k, i) => k.tekst.indexOf(fases.namen[i + 1]) !== -1),
     'elke fase behalve de laatste laat zien wat er hierna komt: dat is het hele mechanisme');
  ok(/abuela/i.test(kaart[7].tekst) && !/estrella|12/.test(kaart[7].tekst),
     'de laatste fase belooft geen dertiende rang meer, maar zegt dat jullie samen verder leren');

  // --- 3. Elke fase is anders getekend ---
  const uniek = new Set(kaart.map((k) => k.svg));
  ok(uniek.size === 8, 'alle acht fases leveren een andere tekening (' + uniek.size + ')');

  // --- 4. ...en toch is het acht keer hetzelfde dier ---
  const levend = kaart.slice(1).map((k) => k.svg);
  // v19.76: de bleke tint van de abuela is geen vaste hexcode meer maar wordt uit de gekozen
  // kleur afgeleid, zodat een mintgroene Chispa niet als oude dame ineens roze wordt.
  const herken = await page.evaluate(() => ({ lijf: petKleur().lijf, bleek: petBleek(petKleur().lijf, 0.52) }));
  ok(levend.every((s) => s.indexOf(herken.lijf) !== -1 || s.indexOf(herken.bleek) !== -1),
     'elke levende fase draagt haar eigen kleur (de abuela is verbleekt, maar in diezelfde kleur)');
  ok(levend.every((s) => (s.match(/stroke-linecap=["']round["']/g) || []).length >= 3),
     'elke levende fase heeft haar kieuwtakken');
  ok(levend.every((s) => (s.match(/<circle/g) || []).length >= 8),
     'twee ogen met een lichtje en zes kieuwpunten, in elke fase');
  ok(kaart[0].svg.indexOf('#fde8d8') !== -1, 'en fase 0 is geen dier maar een ei');

  // --- 5. De tekening verandert precies op de drempel, niet ergens ertussenin ---
  const drempel = await page.evaluate(() => {
    S.txp = PET_LEVELS[3].min - 1; renderPet();
    const voor = document.getElementById('petBox').innerHTML;
    S.txp = PET_LEVELS[3].min; renderPet();
    const na = document.getElementById('petBox').innerHTML;
    S.txp = PET_LEVELS[3].min + 400; renderPet();
    const later = document.getElementById('petBox').innerHTML;
    return { anders: voor !== na, zelfde: na === later, lvlVoor: petLevel(PET_LEVELS[3].min - 1), lvlNa: petLevel(PET_LEVELS[3].min) };
  });
  ok(drempel.lvlVoor === 2 && drempel.lvlNa === 3, 'de drempel valt op de xp die erbij hoort');
  ok(drempel.anders, 'één xp over de drempel en ze is zichtbaar veranderd');
  ok(drempel.zelfde, 'daarbinnen verandert ze niet: groeien gebeurt in stappen die je ziet');

  // --- 6. Wat ze aanheeft volgt haar vorm ---
  const kleren = await page.evaluate(() => {
    const uit = [];
    SHOP.forEach(function (it) { S.owned[it.id] = true; });
    S.wear = { sombrero: true, gafas: true, bufanda: true, flor: true };
    for (const i of [1, 6]) {
      S.txp = PET_LEVELS[i].min + 5;
      renderPet();
      const svg = document.getElementById('petBox').innerHTML;
      const v = petFaseVorm(i);
      uit.push({ svg: svg, mondY: v.mondY, T: v.T, W: v.W });
    }
    return uit;
  });
  ok(kleren[0].svg !== kleren[1].svg, 'dezelfde kleren zien er op een baby anders uit dan op een volwassene');
  ok(kleren[0].W < kleren[1].W, 'want de hoed moet passen: de vorm eronder is breder geworden');
  ok(kleren.every((k) => k.svg.indexOf('petwear') !== -1 || k.svg.length > 800), 'de kleren worden ook echt getekend');

  // --- 7. De hints vertalen mee ---
  const taal = await page.evaluate(() => ({
    lang: profLang(),
    hints: PET_LEVELS.map((l) => petHint(l)),
    nl: PET_LEVELS.map((l) => l.hint),
    en: PET_LEVELS.map((l) => l.hintEn)
  }));
  ok(taal.hints.every((h) => h && h.length > 3), 'elke fase heeft een hint');
  if (taal.lang === 'en') {
    ok(taal.hints.join('|') === taal.en.join('|'), 'een Engels profiel krijgt de Engelse hints');
    ok(!/waggelt|leest alles|grijs aan de kieuwen/.test(taal.hints.join(' ')), 'en geen Nederlandse resten');
  } else {
    ok(taal.hints.join('|') === taal.nl.join('|'), 'een Nederlands profiel krijgt de Nederlandse hints');
  }

  // --- 8. Geen JS-fouten in eigen code ---
  const eigen = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(eigen.length === 0, 'geen JS-fouten tijdens de hele test (' + eigen.length + ' gevonden)');
  if (eigen.length) eigen.slice(0, 4).forEach((e) => console.log('   ', e));

  await browser.close();
  if (fails === 0) console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
  else { console.log('\n' + fails + ' TESTS GEFAALD'); process.exit(1); }
})();
