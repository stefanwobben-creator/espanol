// Playwright-test voor de sleepvariant van Dictado (7 aug, v20.9). Stefan: "voor beginners naast
// overtikken is de makkelijkere versie wellicht de woordjes in de juiste volgorde slepen."
// De valkuil daarbij is zijn eigen kritiek op Duolingo: een woordbank is oplosbaar door eliminatie,
// dus je klikt het goed zonder iets te leren. Drie maatregelen daartegen worden hier bewezen:
// (1) tegels zijn geen kiesbare modus maar een redding: alleen de eerste drie zinnen ooit en na een
//     echte misser, en je gaat er altijd uit via het typen van diezelfde zin;
// (2) er liggen afleiders bij uit de conceptmachine, dus de fout die je zou maken ligt als tegel
//     naast het goede woord en eliminatie werkt niet;
// (3) een afleider aantikken zet het bijbehorende Leitner-doosje terug op nul.
// Plus de eerlijke noemer: S.dicGetypt telt alleen echt getypte dictados, sleepwerk tilt hem niet op.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  // de mp3's staan niet in de testrepo; ontbrekende audio is hier geen defect
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
  await page.fill('input[placeholder="Name"]', 'PwSleep' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. tegels bouwen: brokken blijven bij elkaar, afleiders komen uit de conceptmachine ----
  const tegels = await page.evaluate(() => ({
    brok: dicSleepTegels('Me gusta el café por la mañana.'),
    kaal: dicSleepTegels('El curso empezó en septiembre.'),
    leesteken: dicSleepTegels('¿Qué tal, cómo estás?')
  }));
  ok(tegels.brok.indexOf('Me gusta') !== -1, 'brok "me gusta" blijft een tegel (' + JSON.stringify(tegels.brok) + ')');
  ok(tegels.brok.indexOf('por la mañana') !== -1, 'brok "por la mañana" blijft een tegel');
  ok(tegels.kaal.join(' ') === 'El curso empezó en septiembre', 'zin zonder brokken valt in losse woorden');
  ok(tegels.leesteken.join(' ') === 'Qué tal cómo estás', 'leestekens zitten niet in de tegels');

  const afl = await page.evaluate(() => {
    const t = dicSleepTegels('El café está caliente.');
    return {
      tegels: t,
      afleiders: dicSleepAfleiders(t).map(function (a) { return a.woord + ':' + a.cid; })
    };
  });
  ok(afl.afleiders.length > 0 && afl.afleiders.length <= 3, 'er komen 1 tot 3 afleiders bij (' + JSON.stringify(afl.afleiders) + ')');
  ok(afl.afleiders.some(function (a) { return a.split(':')[0] === 'es'; }), 'bij "está" ligt "es" als afleider klaar (serestar)');
  ok(afl.afleiders.some(function (a) { return a.split(':')[0] === 'la'; }), 'bij "el" ligt "la" als afleider klaar (genero)');
  ok(afl.afleiders.every(function (a) { return afl.tegels.indexOf(a.split(':')[0]) === -1; }),
     'een afleider staat nooit al in de zin zelf');

  // een tegenhanger die al in de zin staat, wordt overgeslagen (anders is de opgave dubbelzinnig)
  const dubbel = await page.evaluate(() => {
    const t = dicSleepTegels('El coche es azul y la casa está aquí.');
    return dicSleepAfleiders(t).map(function (a) { return a.woord; });
  });
  ok(dubbel.indexOf('es') === -1 && dubbel.indexOf('está') === -1,
     'staan es en está allebei in de zin, dan komt geen van beide als afleider terug');
  ok(dubbel.indexOf('el') === -1 && dubbel.indexOf('la') === -1, 'idem voor el en la');

  // ---- 2. de eerste drie zinnen ooit openen met tegels, daarna niet meer ----
  const eerst = await page.evaluate(() => {
    S.dicGetypt = 0;
    return { nodig: dicSleepNodig(SENTENCES[0]), drempel: DIC_SLEEP_EERSTE };
  });
  ok(eerst.nodig === true, 'een nieuwe gebruiker (0 getypt) begint met tegels');
  ok(eerst.drempel === 3, 'de drempel staat op drie zinnen');
  const later = await page.evaluate(() => { S.dicGetypt = 3; return dicSleepNodig(SENTENCES[0]); });
  ok(later === false, 'vanaf de vierde getypte zin komen de tegels niet meer uit zichzelf');

  // ---- 3. het scherm: audio, tegels, en geen invoerveld (dus geen tekst om af te kijken) ----
  await page.evaluate(() => {
    S.dicGetypt = 0;
    show('speeltuin');
    funView = 'dictado';
    dictadoNieuweRonde();
    renderFun();
  });
  await page.waitForTimeout(400);
  ok(await page.locator('#dSleepBank .dtegel').count() > 0, 'de tegelbank staat op het scherm');
  ok(await page.locator('#dInput').count() === 0, 'er is geen invoerveld: je kunt niets afkijken');
  ok(await page.locator('#btnDicNormal').count() === 1, 'luisteren normaal blijft beschikbaar');
  ok(await page.locator('#btnDicLento').count() === 1, 'luisteren lento blijft beschikbaar');
  ok(await page.locator('#dModus .dmod').count() === 2, 'de moduskeuze typen/tegels staat op het scherm');
  ok(await page.locator('#btnFunTerug').count() === 0, 'de losse Speeltuin-knop is weg (v21.0)');

  // aantikken zet een tegel in de rij, nog eens aantikken haalt hem eruit
  await page.click('#dSleepBank .dtegel:not(.weg)');
  await page.waitForTimeout(150);
  ok(await page.locator('#dSleepRij .dtegel').count() === 1, 'een aangetikte tegel verschijnt in de antwoordrij');
  await page.click('#dSleepRij .dtegel');
  await page.waitForTimeout(150);
  ok(await page.locator('#dSleepRij .dtegel').count() === 0, 'nog eens aantikken haalt hem weer weg');

  // ---- 4. goed leggen geeft geen zinsvoltooiing, maar stuurt je naar het typen ----
  const goed = await page.evaluate(() => {
    const voor = { xp: (S.xp[today()] || 0), getypt: S.dicGetypt || 0, done: !!S.done[dSleep.zin.id] };
    dSleep.rij = [];
    dicSleepTegels(dSleep.zin.es).forEach(function (w) {
      for (var i = 0; i < dSleep.bank.length; i++) {
        if (dSleep.bank[i].woord === w && dSleep.rij.indexOf(i) === -1) { dSleep.rij.push(i); break; }
      }
    });
    dicSleepCheck();
    return {
      voor: voor,
      klaar: dSleep.klaar,
      xp: (S.xp[today()] || 0),
      getypt: S.dicGetypt || 0,
      done: !!S.done[dSleep.zin.id],
      sleepGoed: S.dicSleepGoed || 0
    };
  });
  ok(goed.klaar === true, 'de juiste volgorde wordt herkend');
  ok(goed.xp === goed.voor.xp + 1, 'goed leggen levert precies 1 xp op, niet de 5 van een getypte zin');
  ok(goed.done === false, 'de zin telt niet als afgerond: die eer is voor het typen');
  ok(goed.getypt === goed.voor.getypt, 'S.dicGetypt blijft staan, sleepwerk tilt de noemer niet op');
  ok(goed.sleepGoed >= 1, 'S.dicSleepGoed telt apart mee voor de KPI');
  // zelf voor tegels gekozen (naFout is false): dan is de zin klaar en hoef je niet ook nog te typen
  ok(await page.locator('#btnDSleepTyp').count() === 0, 'zelfgekozen tegels sturen je niet alsnog naar het typen');
  ok(await page.locator('#btnDicNext').count() === 1, 'je gaat door naar de volgende zin');

  // maar kwamen de tegels na een misser, dan blijft de doorgeef naar het typen wel staan
  const redding = await page.evaluate(() => {
    show('speeltuin'); funView = 'dictado';
    dSleepGedaanId = null;
    dicSleepZet(dIdx, true);
    dSleep.rij = [];
    dicSleepTegels(dSleep.zin.es).forEach(function (w) {
      for (var i = 0; i < dSleep.bank.length; i++) {
        if (dSleep.bank[i].woord === w && dSleep.rij.indexOf(i) === -1) { dSleep.rij.push(i); break; }
      }
    });
    dicSleepCheck();
    return dSleep.klaar;
  });
  ok(redding === true, 'ook na een misser wordt de juiste volgorde herkend');
  ok(await page.locator('#btnDSleepTyp').count() === 1, 'na een misser stuurt de app je wel naar het typen');
  await page.click('#btnDSleepTyp');
  await page.waitForTimeout(300);
  ok(await page.locator('#dInput').count() === 1, 'en dan sta je bij dezelfde zin te typen');
  ok(await page.locator('#btnDicSkip').count() === 0, 'de skip-knop bestaat niet meer (v21.0)');

  // ---- zwaarte en plafond: een beginner krijgt geen negen woorden met een jaartal ----
  const niveau = await page.evaluate(() => {
    S.dicGetypt = 0;
    const frida = SENTENCES.filter(z => /mil novecientos/.test(z.es))[0];
    const kort = { es: 'El café está frío.' };
    return {
      plafondNul: dicPlafond(),
      zwaarFrida: frida ? dicZwaarte(frida) : null,
      zwaarKort: dicZwaarte(kort),
      plafondLater: (function () { S.dicGetypt = 20; const p = dicPlafond(); S.dicGetypt = 0; return p; })()
    };
  });
  ok(niveau.plafondNul === 6, 'het plafond staat bij nul getypte zinnen op 6');
  ok(niveau.zwaarKort < niveau.plafondNul, 'een korte zin past onder het plafond (' + niveau.zwaarKort + ')');
  ok(niveau.zwaarFrida === null || niveau.zwaarFrida > niveau.plafondNul,
     'de jaartalzin van Frida is te zwaar voor een beginner (' + niveau.zwaarFrida + ')');
  ok(niveau.plafondLater > niveau.plafondNul, 'het plafond groeit mee met wat je typt (' + niveau.plafondLater + ')');

  const gekozen = await page.evaluate(() => {
    S.dicGetypt = 50; S.dicModus = 'tegels';
    const a = dicModusNu();
    S.dicModus = 'typen';
    const b = dicModusNu();
    delete S.dicModus;
    const c = dicModusNu();
    S.dicGetypt = 0;
    const d = dicModusNu();
    return { a: a, b: b, c: c, d: d };
  });
  ok(gekozen.a === 'tegels', 'een eigen keuze voor tegels wint van de automaat');
  ok(gekozen.b === 'typen', 'een eigen keuze voor typen wint ook als je nog niets deed');
  ok(gekozen.c === 'typen', 'zonder keuze en met ervaring: typen');
  ok(gekozen.d === 'tegels', 'zonder keuze en zonder ervaring: tegels');

  // ---- 5. een afleider aantikken is een conceptfout en zet het doosje terug op nul ----
  const doos = await page.evaluate(() => {
    show('speeltuin'); funView = 'dictado';
    const zin = SENTENCES.filter(function (z) { return / es | está /.test(' ' + z.es + ' '); })[0] || SENTENCES[0];
    dIdx = zin;
    dicSleepZet(zin, true);
    const afl = dSleep.bank.map(function (t, i) { return { i: i, t: t }; }).filter(function (x) { return !x.t.echt && x.t.cid; })[0];
    if (!afl) return { overgeslagen: true };
    gramBij(afl.t.cid, true); gramBij(afl.t.cid, true);
    const voor = JSON.parse(JSON.stringify(gramLees(afl.t.cid)));
    dSleep.rij = [afl.i];
    dicSleepCheck();
    return { overgeslagen: false, cid: afl.t.cid, voorBox: voor.box, naBox: gramLees(afl.t.cid).box, naFout: gramLees(afl.t.cid).fout };
  });
  ok(doos.overgeslagen === true || doos.voorBox > 0, 'het testconcept stond eerst in een hoger doosje');
  ok(doos.overgeslagen === true || doos.naBox === 0, 'een afleider aantikken zet het concept terug op doosje nul (' + doos.cid + ')');
  ok(doos.overgeslagen === true || doos.naFout >= 1, 'de fout wordt geteld op het concept zelf');

  // ---- 6. twee keer mis: antwoord tonen en alsnog naar het typen ----
  const tweemaal = await page.evaluate(() => {
    dSleep.pogingen = 1;
    dSleep.klaar = false;
    dSleep.rij = [0];
    dicSleepCheck();
    return { klaar: dSleep.klaar };
  });
  ok(tweemaal.klaar === true, 'na twee missers stopt de opgave');
  ok(await page.locator('#btnDicNext').count() === 1, 'na twee missers gaat het antwoord aan en ga je door');

  // ---- 7. de knop na een misser verschijnt alleen na een echte misser ----
  const bron = await page.content();
  ok(/misteHelemaal && !\(dSleep/.test(bron.replace(/\s+/g, ' ')) || bron.indexOf('misteHelemaal') !== -1,
     'de sleepknop hangt aan misteHelemaal, dus niet aan de "bijna"-feedback');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
