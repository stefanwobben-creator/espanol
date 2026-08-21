// Playwright-test voor Letras (7 aug, v22.1). Stefan: "die snelheid game is leuk maar nog wel te
// intensief. ik bedoel iets nog meer casual zoals woordzoeker, iets wat speels en ontspannend is."
// Dit is het tegenovergestelde van Clasificador: geen klok, geen levens, geen game over. Zeven
// letters, een lijstje open plekken met de Nederlandse betekenis erbij, en je stopt wanneer je wilt.
// Wat hier bewaakt wordt: elke puzzel is oplosbaar (elk doelwoord past echt in de letters), er zit
// geen tijdmechaniek in, en het is productieve recall en geen gokwerk.
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
  await page.fill('input[placeholder="Name"]', 'PwLt' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. het woordenboek komt uit eigen materiaal ----
  const wb = await page.evaluate(() => {
    const w = ltWoordenboek();
    const k = Object.keys(w);
    return {
      n: k.length,
      metSpatie: k.filter((x) => /\s/.test(w[x].es)).length,
      metNtilde: k.filter((x) => /ñ/i.test(w[x].es)).length,
      teKort: k.filter((x) => x.length < 3).length,
      voorbeeld: w[k[0]]
    };
  });
  /* v23.156: de drempel stond op 800 en dat gold voor een Nederlands profiel. De browser van deze
     suite staat op en-US, en sindsdien doen woorden zonder Engelse vertaling niet meer mee (anders
     krijg je een Spaans woord met een Nederlandse omschrijving, zie wTransEcht). Dat is een echte
     inperking en die hoort zichtbaar te zijn: in het Nederlands is de vijver ruim twee keer zo
     groot. Wat de drempel moet bewaken is "genoeg om te spelen", en dat is een paar honderd. */
  const nlPool = await page.evaluate(() => {
    const was = S.lang; S.lang = 'nl';
    const n = Object.keys(ltWoordenboek()).length;
    S.lang = was; ltWbCache = null;
    return n;
  });
  ok(wb.n >= 400, 'het woordenboek is groot genoeg voor variatie (' + wb.n + ' woorden in dit profiel)');
  ok(nlPool > wb.n, 'en in het Nederlands groter, want daar is voor elk woord een omschrijving (' + nlPool + ')');

  // ---- 1b. de horizon: alleen de meestgebruikte woorden, en hij groeit mee ----
  // v22.2: "reo" (de gedaagde) kwam uit de frequentielijst, die op ondertitels is gebaseerd en dus
  // vol rechtbanktaal zit. Nu doet alleen de kop van die lijst mee, plus alles wat de app zelf leert.
  const horizon = await page.evaluate(() => {
    const uit = {};
    S.srs = {};
    uit.leeg = ltHorizon();
    for (let i = 0; i < 50; i++) S.srs['x' + i] = { box: 3, due: today() };
    uit.na50 = ltHorizon();
    for (let i = 0; i < 40; i++) S.srs['z' + i] = { box: 1, due: today() };   // doosje 1 telt niet mee
    uit.naZwak = ltHorizon();
    uit.basis = LT_BASIS; uit.perStap = LT_PER_STAP; uit.freq = FREQ.length;
    S.srs = {};
    return uit;
  });
  ok(horizon.leeg === horizon.basis, 'een nieuwe speler begint bij de ' + horizon.basis + ' meestgebruikte woorden');
  ok(horizon.na50 === horizon.basis + 2 * horizon.perStap, 'vijftig vaste woorden schuiven de horizon twee stappen op (' + horizon.na50 + ')');
  ok(horizon.naZwak === horizon.na50, 'woorden in doosje 1 tellen niet mee: het gaat om wat je aantoonbaar kent');
  ok(horizon.basis < horizon.freq, 'er valt dus echt iets af aan het begin (' + horizon.basis + ' van ' + horizon.freq + ')');

  const rechtbank = await page.evaluate(() => {
    S.srs = {};
    const w = ltWoordenboek();
    return { reo: !!w['reo'], carajo: !!w['carajo'], casa: !!w['casa'], agua: !!w['agua'] };
  });
  ok(rechtbank.reo === false, 'rechtbanktaal als "reo" doet niet meer mee op het startniveau');
  ok(rechtbank.casa === true && rechtbank.agua === true, 'gewone woorden als casa en agua wel');

  /* v23.147: de horizon groeit mee via FREQ, en FREQ heeft alleen een Nederlandse kolom. In een
     Engels profiel doet die lijst sindsdien niet meer mee (anders krijg je Spaanse woorden met een
     Nederlandse omschrijving, zie pw-taal). De browser van deze suite staat op en-US, dus de
     groeimeting hoort in een Nederlands profiel te gebeuren. */
  const groeit = await page.evaluate(() => {
    S.lang = 'nl';
    S.srs = {};
    const klein = Object.keys(ltWoordenboek()).length;
    for (let i = 0; i < 400; i++) S.srs['g' + i] = { box: 3, due: today() };
    const groot = Object.keys(ltWoordenboek()).length;
    S.srs = {};
    return { klein: klein, groot: groot };
  });
  ok(groeit.groot > groeit.klein, 'wie meer woorden vast heeft, speelt met een grotere lijst (' + groeit.klein + ' naar ' + groeit.groot + ')');

  const talen = await page.evaluate(() => {
    S.srs = {};
    for (let i = 0; i < 400; i++) S.srs['g' + i] = { box: 3, due: today() };
    S.lang = 'nl';
    const nl = Object.keys(ltWoordenboek()).length;
    S.lang = 'en';
    const en = Object.keys(ltWoordenboek()).length;
    S.lang = 'nl';
    S.srs = {};
    return { nl: nl, en: en };
  });
  ok(talen.en < talen.nl, 'een Engels profiel speelt met een kleinere vijver, want FREQ is Nederlands (' + talen.en + ' vs ' + talen.nl + ')');
  ok(talen.en > 500, 'maar nog steeds met genoeg woorden om te spelen (' + talen.en + ')');
  ok(wb.metSpatie === 0, 'geen uitdrukkingen met spaties');
  ok(wb.metNtilde === 0, 'geen woorden met ñ (die verdwijnt bij het platslaan)');
  ok(wb.teKort === 0, 'niets korter dan drie letters');
  ok(!!wb.voorbeeld.nl, 'elk woord heeft een Nederlandse betekenis');

  // ---- 2. elke puzzel is echt oplosbaar ----
  const deals = await page.evaluate(() => {
    const uit = [];
    for (let k = 0; k < 20; k++) {
      const d = ltDeel();
      if (!d) { uit.push(null); continue; }
      const bsig = ltSig(d.basis);
      const passen = d.doelen.every((x) => ltPast(ltSig(x.es), bsig));
      uit.push({ n: d.doelen.length, letters: d.letters.length, passen: passen, basis: d.basis });
    }
    return uit;
  });
  ok(deals.every(Boolean), 'er komt altijd een puzzel uit');
  ok(deals.every((d) => d.passen), 'elk doelwoord past echt in de gegeven letters');
  ok(deals.every((d) => d.n >= 5), 'elke puzzel heeft minstens vijf woorden (min ' + Math.min.apply(null, deals.map((d) => d.n)) + ')');
  ok(deals.every((d) => d.letters === 6 || d.letters === 7), 'zes of zeven letters (' + Array.from(new Set(deals.map((d) => d.letters))).join(',') + ')');

  // ---- 3. geen klok, geen levens ----
  const bron = await page.content();
  const motor = bron.slice(bron.indexOf('LETRAS (v22.1)'), bron.indexOf('function renderFunClasificador'));
  ok(!/setInterval|setTimeout/.test(motor), 'er zit geen enkele timer in het spel');
  // op de mechaniek toetsen, niet op de woorden: de toelichting bovenin noemt "geen levens" juist wel
  ok(!/\.levens|levens--|klaar\s*=\s*true/.test(motor), 'en geen levensteller of eindtoestand');
  const geenTijd = await page.evaluate(() => ltSpel === null || (!('tijd' in ltSpel) && !('levens' in ltSpel)));
  ok(geenTijd === true, 'de speltoestand kent geen tijd en geen levens');

  // ---- 4. een woord vinden vult de regel, een verkeerde reeks doet niets ----
  await page.evaluate(() => { S.speelAlles = true; lesFlow = null; show('speeltuin'); funView = 'letras'; ltSpel = null; renderFun(); });
  await page.waitForTimeout(300);
  ok(await page.locator('.lt-letter').count() >= 6, 'de letters staan op het scherm');
  ok(await page.locator('.lt-rij').count() >= 5, 'en de open plekken met hun betekenis');
  const verborgen = await page.evaluate(() => Array.from(document.querySelectorAll('.lt-rij:not(.gev) .lt-es')).every((e) => /^·+$/.test(e.textContent)));
  ok(verborgen === true, 'een woord dat je nog niet vond staat als puntjes, niet als tekst');

  const vinden = await page.evaluate(() => {
    const doel = ltSpel.doelen[0];
    const plat = ltPlat(doel.es);
    const voorXp = S.xp[today()] || 0;
    // de letters van dat woord aantikken, in volgorde
    ltSpel.gekozen = [];
    plat.split('').forEach((L) => {
      for (let i = 0; i < ltSpel.letters.length; i++) {
        if (ltSpel.letters[i] === L && ltSpel.gekozen.indexOf(i) === -1) { ltSpel.gekozen.push(i); break; }
      }
    });
    ltCheck();
    return { gevonden: !!ltSpel.gevonden[plat], gekozenLeeg: ltSpel.gekozen.length === 0,
             xpErbij: (S.xp[today()] || 0) - voorXp, woord: doel.es };
  });
  ok(vinden.gevonden === true, 'het juiste woord wordt herkend (' + vinden.woord + ')');
  ok(vinden.gekozenLeeg === true, 'en de invoer wordt weer leeggemaakt');
  ok(vinden.xpErbij === 1, 'een gevonden woord levert 1 taco op');

  const onzin = await page.evaluate(() => {
    const voor = Object.keys(ltSpel.gevonden).length;
    ltSpel.gekozen = [0, 1, 2];
    ltCheck();
    return Object.keys(ltSpel.gevonden).length - voor;
  });
  ok(onzin === 0 || onzin === 1, 'een willekeurige reeks vult hoogstens een woord dat er echt in zit');

  // ---- 5. alles gevonden geeft een afsluiting, geen mislukking ----
  const af = await page.evaluate(() => {
    ltNieuw();
    ltSpel.doelen.forEach((d) => { ltSpel.gevonden[ltPlat(d.es)] = 1; });
    renderFunLetras();
    return { rondes: S.ltRondes || 0, knop: !!document.getElementById('btnLtNieuw') };
  });
  ok(af.knop === true, 'er staat een knop voor een nieuwe puzzel');
  await page.waitForTimeout(200);
  ok(await page.locator('.feedback.ok').count() >= 1, 'en een vriendelijke afsluiting');

  // ---- 6. de "wanneer doe je hem morgen"-vraag is weg ----
  const moment = await page.evaluate(() => {
    S.ritme = {};
    return { kaart: samenKaartNu(false).indexOf('momentKaart') !== -1 };
  });
  ok(moment.kaart === false, 'de planningsvraag komt niet meer als kaart terug (v22.1)');
  const feest = await page.evaluate(() => {
    S.ritme = {};
    const h = typeof feestKaart === 'function' ? feestKaart() : (typeof dagFeestHtml === 'function' ? dagFeestHtml() : '');
    return { heeftVraag: /Wanneer doe je hem morgen|When will you do it tomorrow/.test(h), leeg: h === '' };
  });
  ok(feest.leeg === true || feest.heeftVraag === false, 'het feestscherm vraagt niet meer wanneer je hem morgen doet');

  // ---- v23.11: wat Rueda kwam brengen, zit nu in Letras zelf ----
  //
  // Rueda stond één versie lang naast Letras met het argument dat je bij Letras niet weet wat je
  // zoekt. Dat argument was onjuist: lt-lijst toont de vertaling en het aantal letters allang. Stefan,
  // na het spelen: "het is niet zoveel anders dan letras, ik zie niet waarom dit nou beter is."
  // Wat er wél verschilde waren twee dingen die je niet ziet, en die staan hier nu op.
  const opgenomen = await page.evaluate(() => {
    delete S.letras; ltSpel = null;
    funView = 'letras'; show('speeltuin', true); renderFun();
    // Een doelwoord kiezen dat een leswoord is, want alleen die kan de app volgen. En waarvan geen
    // enkel begin zelf ook een doelwoord is: bij "leer" is "lee" (hij leest) er ook een, en dan vindt
    // het spel dat eerst en begint het wiel opnieuw. Dat is goed gedrag van de app en slecht gedrag
    // van een test die blind letters aantikt.
    const alle = ltSpel.doelen.map((d) => ltPlat(d.es));
    let plat = null, id = null;
    for (const d of ltSpel.doelen) {
      const q = ltPlat(d.es), i = ltIdVoor(q);
      if (!i) continue;
      let botst = false;
      for (let n = LT_MIN; n < q.length; n++) if (alle.indexOf(q.slice(0, n)) !== -1) botst = true;
      if (botst) continue;
      plat = q; id = i; break;
    }
    if (!plat) return { geen: true };
    S.srs[id] = { box: 1, due: today(), n: 1 };
    plat.split('').forEach((L) => {
      for (let i = 0; i < ltSpel.letters.length; i++) {
        if (ltSpel.letters[i] === L && ltSpel.gekozen.indexOf(i) === -1) { ltTik(i); return; }
      }
    });
    return {
      geen: false, plat: plat,
      diag: { letters: ltSpel.letters.join(''), huidig: ltHuidig(), gev: Object.keys(ltSpel.gevonden).join(',') },
      gevonden: !!ltSpel.gevonden[plat],
      box: S.srs[id].box,
      uitSpel: S.srs[id].sp === 1,
      bewaard: (S.letras.gevonden || []).indexOf(plat) !== -1,
      letters: S.letras.letters
    };
  });
  if (opgenomen.geen) {
    console.log('PASS geen leswoord in deze puzzel, niets te toetsen');
  } else {
    ok(opgenomen.gevonden === true, 'een woord uit het wiel tikken vult het in: ' + opgenomen.plat + ' :: ' + JSON.stringify(opgenomen.diag));
    ok(opgenomen.box > 1, 'en een gevonden leswoord schuift een doosje op, net als bij de andere spellen');
    ok(opgenomen.uitSpel === true, 'gemarkeerd als uit een spel, zodat "werkt de app" en "werkt spelen" apart leesbaar blijven');
    ok(opgenomen.bewaard === true, 'je puzzel staat bewaard, dus halverwege stoppen mag');
  }

  await page.reload();
  await page.waitForTimeout(700);
  const terug = await page.evaluate(() => {
    const bewaard = S.letras;
    if (!bewaard) return { geen: true };
    funView = 'letras'; show('speeltuin', true); renderFun();
    return {
      geen: false,
      zelfdeLetters: ltSpel && ltSpel.letters.join('') === bewaard.letters,
      gevonden: ltSpel ? Object.keys(ltSpel.gevonden).length : -1,
      wasGevonden: (bewaard.gevonden || []).length
    };
  });
  if (!terug.geen) {
    ok(terug.zelfdeLetters === true, 'na herladen krijg je dezelfde puzzel terug, geen nieuwe');
    ok(terug.gevonden === terug.wasGevonden, 'met wat je al had gevonden er nog in: ' + terug.gevonden);
  }

  const weg = await page.evaluate(() => ({
    spel: typeof renderFunRueda,
    tegel: !!document.getElementById('ftRueda'),
    // v23.65: de lijst heet dagSpellen() en komt uit spelInfo(). Wat hier gemeten wordt is
    // onveranderd: Rueda mag nergens meer in de dagrotatie opduiken.
    dag: dagSpellen().some((g) => g.v === 'rueda'),
    eis: !!SPEEL_EIS.rueda
  }));
  ok(weg.spel === 'undefined' && !weg.tegel && !weg.dag && !weg.eis,
     'en Rueda is echt weg, niet alleen onbereikbaar');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
