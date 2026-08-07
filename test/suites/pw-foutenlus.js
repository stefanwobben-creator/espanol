// Playwright-test voor de foutenlus (7 aug, v22.0). Stefan: "denk jij na over de back-end dat de
// fouten die ik maak goed worden opgeslagen en verwerkt in de volgende les."
// De lus werkte, maar er lekten vier gaten in:
//  1. het veld laatst bevatte soms je invoer en soms een datum, en bijnaGoedIds() vergeleek het met
//     een datum. "la mujer" >= "2026-08-05" is waar in JavaScript, dus gold elke woordfout ooit als
//     "gisteren gemaakt". Er is nu een apart veld dag.
//  2. de foutenkaart ging alleen mee bij dagdoel en les-af; wie dat niet haalde was onzichtbaar voor
//     de nachtelijke contenttaak. Nu stuurt elke fout zelf een opname, hoogstens eens per half uur.
//  3. Clasificador, Rompecabezas en Escuchar logden helemaal niets.
//  4. S.gram (de conceptdoosjes) zat niet in de logpayload.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  const posts = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error' && !/Failed to load resource/.test(msg.text())) errors.push('console.error: ' + msg.text()); });
  // de logaanroepen onderscheppen: we willen weten wat er naar buiten gaat, zonder de server te bellen
  await page.route('**/api/log', (route) => {
    try { posts.push(JSON.parse(route.request().postData() || '{}')); } catch (e) {}
    route.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' });
  });
  await page.route('**/api/sync', (route) => route.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' }));

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
  await page.fill('input[placeholder="Name"]', 'PwLus' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. de datum staat apart van de invoer ----
  const velden = await page.evaluate(() => {
    S.errors = {};
    logError('w9', 'woord', 'les1', 'la mujer');
    const e = S.errors['woord:w9'];
    return { laatst: e.laatst, dag: e.dag, vandaag: today(), count: e.count };
  });
  ok(velden.laatst === 'la mujer', 'laatst bewaart nog steeds wat je typte ("' + velden.laatst + '")');
  ok(velden.dag === velden.vandaag, 'en dag bewaart de datum (' + velden.dag + ')');

  // ---- 2. bijnaGoedIds kijkt naar de datum, niet naar de tekst ----
  const bijna = await page.evaluate(() => {
    S.errors = {};
    const oud = addDays(today(), -9);
    S.errors['woord:oud1'] = { id: 'oud1', type: 'woord', tag: 't', count: 3, laatst: 'la mujer', dag: oud };
    S.errors['woord:vers1'] = { id: 'vers1', type: 'woord', tag: 't', count: 1, laatst: 'el hombre', dag: today() };
    S.errors['woord:legacy'] = { id: 'legacy', type: 'woord', tag: 't', count: 5, laatst: 'viuda' };  // van vóór v22.0
    const r = bijnaGoedIds();
    return { vers: !!r.vers1, oud: !!r.oud1, legacy: !!r.legacy, n: Object.keys(r).length };
  });
  ok(bijna.vers === true, 'een verse fout krijgt voorrang');
  ok(bijna.oud === false, 'een fout van negen dagen geleden niet, ook al staat er tekst in laatst');
  ok(bijna.legacy === false, 'een regel van vóór v22.0 zonder datum telt als oud');

  // ---- 3. elke fout stuurt een opname, maar hoogstens eens per half uur ----
  const opnames = await page.evaluate(() => {
    S.errors = {}; delete S.logOpname;
    logError('a1', 'zin', 't', 'iets');
    const na1 = S.logOpname;
    logError('a2', 'zin', 't', 'iets anders');
    const na2 = S.logOpname;
    S.logOpname = Date.now() - (LOG_OPNAME_MS + 1000);
    logError('a3', 'zin', 't', 'nog iets');
    const na3 = S.logOpname;
    return { na1: !!na1, zelfde: na1 === na2, opnieuw: na3 !== na2, venster: LOG_OPNAME_MS };
  });
  ok(opnames.na1 === true, 'de eerste fout zet meteen een opname klaar');
  ok(opnames.zelfde === true, 'een tweede fout meteen erna stuurt niet nog een opname');
  ok(opnames.opnieuw === true, 'na een half uur wel weer');
  ok(opnames.venster === 30 * 60 * 1000, 'het venster is een half uur');

  await page.waitForTimeout(400);
  const opnamePost = posts.filter((p) => p.kind === 'opname').slice(-1)[0];
  ok(!!opnamePost, 'er gaat echt een logregel de deur uit (' + posts.map((p) => p.kind).join(',') + ')');
  if (opnamePost) {
    ok(!!opnamePost.payload.fouten, 'met de foutenkaart erin');
    ok(opnamePost.payload.gram !== undefined, 'en met de conceptdoosjes erin');
  }

  // ---- 4. de twee bestaande logmomenten sturen gram nu ook mee ----
  const bron = await page.content();
  const plat = bron.replace(/\s+/g, ' ');
  ok(/logServer\("dagdoel", \{streak:S\.streak\.count, fouten:S\.errors, gram:S\.gram/.test(plat),
     'de dagdoel-log stuurt gram mee');
  ok(/logServer\("les-af", \{les:l\.id, titel:l\.titel, fouten:S\.errors, gram:S\.gram/.test(plat),
     'de les-af-log ook');

  // ---- 5. de drie nieuwe oefeningen leveren voer ----
  const nieuw = await page.evaluate(() => {
    S.errors = {}; S.speelAlles = true; lesFlow = null;
    // Clasificador
    show('speeltuin'); funView = 'clas'; clNieuwSpel();
    const cid = clSpel.c.id;
    clKies(clSpel.item.g === 0 ? 1 : 0);
    // Rompecabezas
    funView = 'conj'; S.rvDrill = 0; rvSpel = null; rvNieuweRonde();
    const i = rvIndex();
    let fs = -1, fu = -1;
    rvSpel.stammen.forEach((sk, si) => rvSpel.uitgangen.forEach((u, ui) => {
      if (fs !== -1 || u.op) return;
      const g = i.geldig[sk.stam + u.e];
      if (!g || g.stam !== sk.stam) { fs = si; fu = ui; }
    }));
    if (fs !== -1) rvZet(fs, fu);
    // Escuchar
    funView = 'audi'; audStop(); audNieuw(); renderFun();
    const scid = audSc.id;
    audAntwoord(audSc.vragen[0].c === 0 ? 1 : 0, null);
    const k = Object.keys(S.errors);
    return { sleutels: k, concept: !!S.errors['concept:' + cid], escucha: !!S.errors['escucha:' + scid],
             verbo: k.some((x) => x.indexOf('verbo:') === 0) };
  });
  ok(nieuw.concept === true, 'een misser in Clasificador komt in het foutenlogboek (' + nieuw.sleutels.join(',') + ')');
  ok(nieuw.verbo === true, 'een onbestaande werkwoordsvorm in Rompecabezas ook');
  ok(nieuw.escucha === true, 'en een fout antwoord bij Escuchar ook');

  // de sleutels zijn bruikbaar voor de nachtbot: type:id met een teller en wat je koos
  const vorm = await page.evaluate(() => {
    const k = Object.keys(S.errors).filter((x) => x.indexOf('verbo:') === 0)[0];
    return k ? S.errors[k] : null;
  });
  ok(!!vorm && vorm.count >= 1 && !!vorm.laatst && !!vorm.dag,
     'zo\'n regel heeft een teller, je invoer en een datum (' + JSON.stringify(vorm) + ')');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
