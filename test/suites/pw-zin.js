// pw-zin.js (18 aug, v23.128) — staat de vorm in een echte zin, en op de goede plek?
//
// WAAROM DIT ER IS
//
// Alles wat deze app over werkwoorden deed was losse vormen: cellen, rijtjes, patronen. Spaans
// spreek je in zinnen. Deze oefening zet één woord uit een hele Spaanse zin, met de Nederlandse
// betekenis erboven, en laat je dat woord typen.
//
// De pool wordt AFGELEID uit SENTENCES: geen lijst met gaten die iemand bijhoudt. Dat is waarom
// deze suite bestaat, want afleiden gaat op twee manieren stil mis.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE EIGENNAAM-REM. "Van Gogh pintó unos 900 cuadros." Van is de ellos-vorm van ir. Zonder
//      rem zet deze oefening een gat in een schildersnaam. Maar "¿Puedo pedirte un favor?" heeft
//      óók een hoofdletter, door de ¿, en die zin hoort er wél in. Beide kanten worden gemeten.
//   2. HET GAT STAAT OP DE GOEDE PLEK. Op index knippen en niet zoek-en-vervang, want hetzelfde
//      woord kan twee keer in de zin staan. De zin met het gat terug-gevuld moet letterlijk de
//      originele zin zijn.
//   3. ELKE OPGAVE IS EENDUIDIG. Precies één vorm, precies één werkwoord, precies één persoon.
//      Twee mogelijke antwoorden op één gat is een vraag die je niet kunt winnen.
//   4. ALLEEN VRIJGESPEELDE ZINNEN, EN ALLEEN OPEN TIJDEN. Anders staat er Spaans op je scherm dat
//      je nergens hebt gezien.
//   5. DE TWEE ROUTES HEBBEN HEM ALLEBEI, elk met hun eigen tijden en hun eigen stand.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwZin' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  await page.evaluate(() => {
    S.lang = 'nl'; S.speelAlles = true;
    S.conjOpen = CONJ_FASES.length - 1; S.conjFase = CONJ_FASES[CONJ_FASES.length - 1].id;
    try { persist(); } catch (e) {}
    // alles vrijgespeeld, zodat deze meting over de hele bak gaat en niet over les 1
    window.__alles = SENTENCES.map((z) => z.id);
    window.__orig = window.allowedSentIds;
    window.allowedSentIds = function () { return window.__alles; };
  });

  // ---- 1. de pool ----
  const pool = await page.evaluate(() => {
    const p = zinPool(null);
    const perT = {}, perV = {};
    p.forEach((k) => { perT[k.t] = (perT[k.t] || 0) + 1; perV[k.v.inf] = (perV[k.v.inf] || 0) + 1; });
    return { n: p.length, perT, perV, verbs: Object.keys(perV).length,
             presente: zinPool(['presente']).length,
             verleden: zinPool(['indefinido', 'imperfecto']).length };
  });

  console.log('\n-- de pool --');
  ok(pool.n > 40, 'er zijn ' + pool.n + ' bruikbare zinnen');
  ok(pool.verbs >= 10, 'over ' + pool.verbs + ' werkwoorden');
  ok(pool.presente >= 8, 'genoeg voor een presente-ronde (' + pool.presente + ')');
  ok(pool.verleden >= 8, 'en genoeg voor een verleden-tijdronde (' + pool.verleden + ')');
  console.log('  · per tijd: ' + JSON.stringify(pool.perT));

  // ---- 2. DE KERN: de eigennaam-rem, allebei de kanten ----
  const namen = await page.evaluate(() => {
    function zoek(re) { return SENTENCES.filter((z) => re.test(z.es || ''))[0] || null; }
    const vg = zoek(/Van Gogh/);
    const puedo = zoek(/^¿Puedo/);
    // en twee verzonnen zinnen, zodat deze meting niet afhangt van wat er toevallig in de bak zit
    const nepNaam = { id: 'zzz1', nl: 'Van Dijk speelt goed.', en: 'Van Dijk plays well.', es: 'Van Dijk juega bien.' };
    const nepGoed = { id: 'zzz2', nl: 'Ik kan het.', en: 'I can do it.', es: '¿Puedo hacerlo?' };
    return {
      vgEs: vg ? vg.es : null, vg: vg ? !!zinKandidaat(vg) : null,
      puedoEs: puedo ? puedo.es : null, puedo: puedo ? (zinKandidaat(puedo) || {}).w || null : null,
      nepNaam: !!zinKandidaat(nepNaam),
      nepGoed: (zinKandidaat(nepGoed) || {}).w || null
    };
  });

  console.log('\n-- DE KERN: eigennamen --');
  ok(namen.vg === false,
    'DE REGEL: "' + namen.vgEs + '" doet niet mee, want Van is daar geen werkwoord');
  ok(namen.nepNaam === false,
    'CONTROLE: en "Van Dijk juega bien." ook niet (verzonnen, dus dit hangt niet af van de bak)');
  ok(namen.puedo === 'Puedo',
    'CONTROLE: maar "' + namen.puedoEs + '" doet wél mee, want die hoofdletter komt van de ¿');
  ok(namen.nepGoed === 'Puedo',
    'CONTROLE: idem voor een verzonnen ¿Puedo-zin (' + namen.nepGoed + ')');

  // ---- 3. het gat staat op de goede plek ----
  const gaten = await page.evaluate(() => {
    const p = zinPool(null);
    let mis = 0, tweeKeer = 0, misVoorbeeld = null;
    p.forEach((k) => {
      // het gat terugvullen moet letterlijk de originele zin geven
      const terug = k.z.es.slice(0, k.i) + k.w + k.z.es.slice(k.i + k.w.length);
      if (terug !== k.z.es) { mis++; if (!misVoorbeeld) misVoorbeeld = k.z.es; }
      // staat het woord meer dan één keer in de zin? dan zou zoek-en-vervang twee gaten maken
      const n = (k.z.es.match(new RegExp('\\\\b' + k.w.replace(/[.*+?^${}()|[\]\\\\]/g, '\\\\$&') + '\\\\b', 'gi')) || []).length;
      if (n > 1) tweeKeer++;
      // en het gat mag nooit leeg of de hele zin zijn
      const gat = zinMetGat(k);
      if (gat === k.z.es || gat.indexOf('____') === -1) { mis++; if (!misVoorbeeld) misVoorbeeld = k.z.es; }
    });
    return { n: p.length, mis, tweeKeer, misVoorbeeld };
  });

  console.log('\n-- het gat --');
  ok(gaten.mis === 0,
    'DE REGEL: het gat terugvullen geeft precies de originele zin, ' + gaten.n + ' keer (mis: ' +
    gaten.mis + (gaten.misVoorbeeld ? ' — ' + gaten.misVoorbeeld : '') + ')');
  console.log('  · ' + gaten.tweeKeer + ' zinnen waarin het woord meer dan één keer staat');

  // ---- 4. elke opgave is eenduidig ----
  const eenduidig = await page.evaluate(() => {
    const p = zinPool(null);
    let dubbel = 0, voorbeeld = null;
    p.forEach((k) => {
      // hoeveel (werkwoord, persoon, tijd) leveren dezelfde letterreeks op?
      const idx = zinVormen()[k.w.toLowerCase()] || [];
      if (idx.length !== 1) { dubbel++; if (!voorbeeld) voorbeeld = k.z.es + ' → ' + k.w; }
    });
    return { dubbel, voorbeeld, n: p.length };
  });
  console.log('\n-- eenduidig --');
  ok(eenduidig.dubbel === 0,
    'DE REGEL: elk gat heeft precies één goed antwoord (' + eenduidig.dubbel +
    (eenduidig.voorbeeld ? ' — ' + eenduidig.voorbeeld : '') + ')');

  // ---- 5. een ronde spelen ----
  const spelen = await page.evaluate(() => {
    function ronde(goedSpelen, tijden, brok) {
      zinStart(tijden, brok);
      const n = zinSpel.rij.length;
      for (let i = 0; i < n; i++) {
        const k = zinNu();
        zinAntwoord(goedSpelen ? k.w : 'zzzz');
        zinVolgende();
      }
      // meteen uitlezen: brokLees geeft het levende object terug, dus een latere ronde zou dit
      // getal onder je handen veranderen
      const st = brokLees(brok || 'zin.vorm');
      return { n, beste: st.beste || 0, rondes: st.rondes || 0, len: st.len || 0 };
    }
    S.brok = {};
    const fout = ronde(false, null, null);
    const goed = ronde(true, null, null);
    const scoped = ronde(true, ['presente'], 'zin.presente');
    return {
      fout: fout.beste, na: goed.beste, len: goed.n,
      rondes: goed.rondes, opgeslagenLen: goed.len,
      sleutels: Object.keys(S.brok).sort(),
      scopedLen: scoped.n, scopedBeste: scoped.beste,
      eisLos: GRAM_EIS.zin(brokLees('zin.vorm')),
      eisLeeg: GRAM_EIS.zin({})
    };
  });

  console.log('\n-- een ronde --');
  ok(spelen.fout === 0, 'CONTROLE: alles fout geeft 0 (nu: ' + spelen.fout + ')');
  ok(spelen.na === spelen.len, 'alles goed geeft ' + spelen.na + '/' + spelen.len);
  ok(spelen.rondes === 2, 'twee rondes geteld op deze sleutel (nu: ' + spelen.rondes + ')');
  ok(spelen.opgeslagenLen === spelen.len, 'de rondelengte wordt bewaard (' + spelen.opgeslagenLen + ')');
  ok(spelen.sleutels.join(',') === 'zin.presente,zin.vorm',
    'DE REGEL: elke route houdt zijn eigen stand bij (' + spelen.sleutels.join(', ') + ')');
  ok(spelen.eisLos === true, 'alles goed haalt de eis');
  ok(spelen.eisLeeg === false, 'CONTROLE: en zonder ronde haal je hem niet');

  const ZIN_LEN = await page.evaluate(() => ZIN_LEN);

  // ---- 6. de twee routes ----
  const routes = await page.evaluate(() => GRAM_PADEN.map((p) => {
    const i = p.stappen.findIndex((s) => s.soort === 'zin');
    const s = i >= 0 ? p.stappen[i] : null;
    return {
      pad: p.id, heeft: i >= 0, brok: s ? s.brok : null, tijden: s ? (s.tijden || p.tijden) : null,
      pool: s ? zinPool(s.tijden || p.tijden).length : 0,
      // geen enkele stap mag nog "komt nog" zijn
      zonderScherm: p.stappen.filter((x, j) => !gramPadStap(p, j).bestaat).length
    };
  }));

  console.log('\n-- de routes --');
  routes.forEach((r) => {
    ok(r.heeft, r.pad + ' heeft een zin-stap (' + r.brok + ', ' + (r.tijden || []).join('/') + ')');
    ok(r.pool >= ZIN_LEN, 'en ' + r.pool + ' zinnen om uit te trekken');
    ok(r.zonderScherm === 0,
      'DE REGEL: geen enkele stap staat nog op "komt nog" (' + r.zonderScherm + ')');
  });
  ok(new Set(routes.map((r) => r.brok)).size === routes.length,
    'CONTROLE: de routes delen hun stand niet');

  // ---- het scherm ----
  await page.evaluate(() => { zinSpel = null; funView = 'zin'; show('speeltuin', true); });
  await page.waitForTimeout(300);
  const scherm = await page.evaluate(() => ({
    gat: (document.getElementById('zinGat') || {}).innerText || '',
    hint: (document.getElementById('zinHint') || {}).innerText || '',
    invoer: document.querySelectorAll('#zinInput').length,
    tekst: document.getElementById('funCard').innerText
  }));
  console.log('\n-- het scherm --');
  ok(/_{3,}/.test(scherm.gat), 'de zin staat er met een gat ("' + scherm.gat.replace(/\s+/g, ' ') + '")');
  ok(scherm.invoer === 1, 'en een invoerveld, geen keuzeknoppen');
  ok(scherm.hint.length > 3, 'met de infinitief en de persoon erbij ("' + scherm.hint.replace(/\s+/g, ' ') + '")');

  // de betekenis staat erboven: zonder dat is de vorm niet af te leiden
  const betekenis = await page.evaluate(() => {
    const k = zinNu();
    return { nl: ct(k.z.nl, k.z.en || k.z.nl), staat: document.getElementById('funCard').innerText.indexOf(ct(k.z.nl, k.z.en || k.z.nl)) !== -1 };
  });
  ok(betekenis.staat === true,
    'DE REGEL: de betekenis staat erboven, want daar hoort de vorm uit te volgen ("' + betekenis.nl + '")');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
