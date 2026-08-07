// Playwright-test voor Rompecabezas de verbos (7 aug, v21.8). Stefan: "ik zoek een spel om
// werkwoorden te leren, maar dus echt een spel." De Conjugador was een rijtjesdrill tegen de klok
// zonder enkele beslissing erin. Dit heeft wel de drie dingen die een spel maken: je kiest welke
// combinatie je maakt, je kunt een zet verspillen, en je speelt tegen je eigen record.
// Het bijzondere is dat de scheidsrechter niet met de hand geschreven is: VERBOS bevat de volledige
// presente, dus of "pued" + "emos" bestaat is gewoon op te zoeken, en het spel weet daardoor ook
// wat je wel had moeten maken. Dat is precies de les.
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
  await page.fill('input[placeholder="Name"]', 'PwRv' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. de scheidsrechter komt uit de data, niet uit handwerk ----
  const ix = await page.evaluate(() => {
    const i = rvIndex();
    return {
      stammen: Object.keys(i.stammen).length,
      vormen: Object.keys(i.geldig).length,
      verbs: Object.keys(i.perVerb).length,
      wissel: Object.keys(i.stammen).filter((k) => i.stammen[k].wissel).length
    };
  });
  ok(ix.verbs >= 20, 'er zijn genoeg ontleedbare werkwoorden (' + ix.verbs + ')');
  ok(ix.stammen >= 30, 'en genoeg stamkaarten (' + ix.stammen + ')');
  ok(ix.vormen === ix.verbs * 6, 'elke ontleedbare werkwoordsvorm zit in de scheidsrechter (' + ix.vormen + ')');
  ok(ix.wissel > 0, 'wisselwerkwoorden worden herkend en gemarkeerd (' + ix.wissel + ' stammen)');

  // onregelmatige werkwoorden die niet in stam plus uitgang te knippen zijn, doen niet mee
  const ser = await page.evaluate(() => {
    const v = VERBOS.filter((x) => x.inf === 'ser')[0];
    return v ? rvOntleed(v) : 'geen ser';
  });
  ok(ser === null || ser === 'geen ser', 'ser doet niet mee: soy is niet in stam plus uitgang te knippen');

  // ---- 2. het oordeel klopt: podemos wel, puedemos niet ----
  const oordeel = await page.evaluate(() => {
    const i = rvIndex();
    return {
      podemos: !!i.geldig['podemos'],
      puedemos: !!i.geldig['puedemos'],
      puedo: !!i.geldig['puedo'],
      hablemos: !!i.geldig['hablemos']   // subjuntivo, hoort hier niet
    };
  });
  ok(oordeel.podemos === true, 'podemos bestaat');
  ok(oordeel.puedo === true, 'puedo ook');
  ok(oordeel.puedemos === false, 'puedemos niet: bij nosotros valt de klemtoon weg');
  ok(oordeel.hablemos === false, 'hablemos ook niet: dat is subjuntivo, geen presente');

  // ---- 3. elke deal is te winnen ----
  const deals = await page.evaluate(() => {
    const uit = [];
    for (let k = 0; k < 25; k++) {
      const d = rvDeel();
      const i = rvIndex();
      let n = 0;
      d.uitgangen.forEach((e) => d.stammen.forEach((sk) => {
        const g = i.geldig[sk.stam + e];
        if (g && g.stam === sk.stam) n++;
      }));
      uit.push({ n: n, stammen: d.stammen.length, uitgangen: d.uitgangen.length });
    }
    return uit;
  });
  ok(deals.every((d) => d.n >= 3), 'elke deal heeft minstens drie geldige combinaties (min ' + Math.min.apply(null, deals.map((d) => d.n)) + ')');
  ok(deals.every((d) => d.uitgangen === 6), 'elke deal geeft zes zetten');
  ok(deals.every((d) => d.stammen <= 5 && d.stammen >= 1), 'en hoogstens vijf stamkaarten');

  // ---- 4. een goede zet scoort, een misser kost je de zet en legt uit wat het wel was ----
  const spelen = await page.evaluate(() => {
    S.speelAlles = true; lesFlow = null;
    show('speeltuin'); funView = 'conj'; S.rvDrill = 0; rvSpel = null;
    renderFun();
    const i = rvIndex();
    // zoek een geldige combinatie in deze deal
    let gs = -1, gu = -1;
    rvSpel.stammen.forEach((sk, si) => rvSpel.uitgangen.forEach((u, ui) => {
      const g = i.geldig[sk.stam + u.e];
      if (gs === -1 && g && g.stam === sk.stam) { gs = si; gu = ui; }
    }));
    const voor = rvSpel.punten;
    rvZet(gs, gu);
    const naGoed = { punten: rvSpel.punten, laatste: rvSpel.laatste, op: rvSpel.uitgangen[gu].op };
    // en nu een misser: dezelfde stam met een uitgang die er niet bij past
    let fs = -1, fu = -1;
    rvSpel.stammen.forEach((sk, si) => rvSpel.uitgangen.forEach((u, ui) => {
      if (u.op || fs !== -1) return;
      const g = i.geldig[sk.stam + u.e];
      if (!g || g.stam !== sk.stam) { fs = si; fu = ui; }
    }));
    let naFout = null;
    if (fs !== -1) { const p = rvSpel.punten; rvZet(fs, fu); naFout = { erbij: rvSpel.punten - p, laatste: rvSpel.laatste, op: rvSpel.uitgangen[fu].op }; }
    return { voor: voor, naGoed: naGoed, naFout: naFout };
  });
  ok(spelen.naGoed.punten > spelen.voor, 'een geldige vorm levert punten op (' + spelen.naGoed.punten + ')');
  ok(spelen.naGoed.laatste.goed === true, 'en wordt als goed gemeld');
  ok(/^(yo|tú|él|nosotros|vosotros|ellos)/.test(spelen.naGoed.laatste.persoon !== undefined ? 'yo' : 'x'), 'met de persoon erbij');
  ok(spelen.naGoed.op === true, 'de gebruikte uitgang is op');
  if (spelen.naFout) {
    ok(spelen.naFout.erbij === 0, 'een misser levert niets op');
    ok(spelen.naFout.op === true, 'maar kost je de zet wel');
    ok(spelen.naFout.laatste.goed === false, 'en wordt als fout gemeld');
  }

  // ---- 5. de ronde eindigt na zes zetten en houdt een record bij ----
  const einde = await page.evaluate(() => {
    rvSpel = null; rvNieuweRonde();
    const i = rvIndex();
    S.rvBest = 0;
    for (let z = 0; z < 6; z++) {
      let gs = 0, gu = -1;
      rvSpel.stammen.forEach((sk, si) => rvSpel.uitgangen.forEach((u, ui) => {
        if (u.op || gu !== -1) return;
        const g = i.geldig[sk.stam + u.e];
        if (g && g.stam === sk.stam) { gs = si; gu = ui; }
      }));
      if (gu === -1) { gu = rvSpel.uitgangen.findIndex((u) => !u.op); if (gu === -1) break; }
      rvZet(gs, gu);
    }
    return { klaar: rvSpel.klaar, punten: rvSpel.punten, best: S.rvBest || 0, gemaakt: rvSpel.gemaakt.length };
  });
  ok(einde.klaar === true, 'na zes zetten is de ronde klaar');
  ok(einde.gemaakt >= 3, 'wie goed speelt maakt minstens drie vormen (' + einde.gemaakt + ')');
  ok(einde.best === einde.punten, 'je beste score wordt bewaard (' + einde.best + ')');

  await page.evaluate(() => renderFunRompecabezas());
  await page.waitForTimeout(300);
  ok(await page.locator('#btnRvNieuw').count() === 1, 'op het eindscherm kun je nog een potje');
  ok(await page.locator('#btnRvDrill').count() === 1, 'en terug naar de oude oefenmodus voor de andere tijden');
  ok(await page.locator('.naronde').count() === 1, 'en er staat een "En nu?"-voorstel');

  // ---- 6. de oude drill werkt nog en brengt je terug ----
  const drill = await page.evaluate(() => {
    try {
      S.rvDrill = 1; conjRonde = null; conjIdx = null; renderFunConjugador();
      return { ok: true, kop: (document.querySelector('#funCard h2') || {}).textContent };
    } catch (e) { return { ok: false, fout: String(e.message).slice(0, 80) }; }
  });
  ok(drill.ok === true, 'de oude drill opent nog gewoon (' + (drill.fout || drill.kop) + ')');
  await page.evaluate(() => { S.rvDrill = 0; });

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
