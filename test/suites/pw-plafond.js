// pw-plafond.js (15 aug, v23.111) — kun je de ladder op door te herkennen?
//
// WAAROM DIT ER IS
//
// "Geleerd" betekent in de Conjugador precies één ding: de volgende fase gaat open bij acht van je
// laatste tien goed. Tot v23.110 telde een aangeklikt antwoord daar even zwaar als een getypt
// antwoord. Herkennen en produceren zijn verschillende vaardigheden die slecht naar elkaar
// overdragen, dus je kon omhoog klimmen door te herkennen en boven aan de ladder ontdekken dat je
// de vormen niet kunt maken. Dat is precies wat Stefan beschreef na de vormdril.
//
// Grappig detail: de code wist het al. Bij de XP staat sinds v19.44 "meerkeuze telt als lichter
// bewijs dan zelf typen". Dat inzicht zat in de puntentelling en niet in de ladder.
//
// DE CONTROLEGEVALLEN
//
// Deze suite is te bedriegen door de ontgrendeling gewoon helemaal kapot te maken. Vandaar dat
// beide richtingen gemeten worden:
//
//   1. twintig GOEDE aangeklikte antwoorden mogen de fase NIET openen, en de meter moet op nul
//      blijven staan
//   2. tien goede GETYPTE antwoorden moeten hem WEL openen
//   3. een aangeklikt antwoord moet verder alles gewoon doen: XP, streak en het foutenboek. Anders
//      is dit geen plafond maar een dood scherm.
//   4. de regel staat op het scherm zodra je in meerkeuze staat, en niet als je typt. Een stille
//      regel is een valstrik.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

// Beantwoordt n opgaven goed in de gevraagde modus, via de echte schermknoppen.
async function speel(page, modus, n) {
  await page.evaluate((m) => {
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.conj = m;
    conjRonde = null; conjIdx = null; cjMk = null;
    funView = 'conj'; renderFun();
  }, modus);
  await page.waitForTimeout(250);
  for (let i = 0; i < n; i++) {
    const correct = await page.evaluate(() => conjVorm(conjIdx.verb, conjIdx.p, conjIdx.t || 'presente'));
    if (modus === 'makkelijk') {
      await page.evaluate((c) => {
        const b = Array.prototype.filter.call(document.querySelectorAll('#cjOpties button'),
          (x) => x.innerText.trim() === c)[0];
        if (b) b.click();
      }, correct);
    } else {
      // via de staat en niet via page.fill: het invoerveld staat niet altijd zichtbaar in deze
      // opzet, en wat deze suite meet is de ladderregel, niet het invoerveld. Dat laatste is elders
      // gedekt (pw-conjfase, pw-vormen).
      await page.evaluate((c) => {
        const el = document.getElementById('cjInput');
        if (el) el.value = c;
        checkConjugador();
      }, correct);
    }
    await page.waitForTimeout(60);
    await page.evaluate(() => {
      conjRonde.n++; conjIdx = null; cjMk = null;
      if (conjRonde.n >= conjRonde.lengte) conjRonde = null;
      renderFunConjugadorDrill();
    });
    await page.waitForTimeout(60);
  }
}

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwPlaf' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  await page.evaluate(() => { S.lang = 'nl'; S.rvDrill = 1; S.conjOpen = 0; S.conjFase = CONJ_FASES[0].id; try { persist(); } catch (e) {} });

  const start = await page.evaluate(() => ({ open: S.conjOpen, xp: (S.xp && S.xp[today()]) || 0 }));

  // ---- 1. klikken opent de fase niet ----
  await speel(page, 'makkelijk', 20);
  const naKlikken = await page.evaluate(() => ({
    open: S.conjOpen,
    meter: conjFaseScore(CONJ_FASES[0].id),
    xp: (S.xp && S.xp[today()]) || 0,
    streak: (conjRonde && conjRonde.streak) || 0
  }));

  console.log('\n-- twintig goede antwoorden, aangeklikt --');
  ok(naKlikken.open === start.open,
    'CONTROLE: de fase gaat NIET open van aangeklikte antwoorden (open: ' + start.open + ' → ' + naKlikken.open + ')');
  ok(naKlikken.meter.n === 0,
    'en de meter naar de volgende fase blijft leeg (' + naKlikken.meter.goed + '/' + naKlikken.meter.n + ')');
  ok(naKlikken.xp > start.xp,
    'CONTROLE: maar je krijgt wel gewoon XP, dit is een plafond en geen dood scherm (' + start.xp + ' → ' + naKlikken.xp + ')');

  // ---- 2. de regel staat op het scherm ----
  const zichtbaar = await page.evaluate(() => {
    S.modusKeuze.conj = 'makkelijk'; conjRonde = null; conjIdx = null; funView = 'conj'; renderFun();
    const a = (document.getElementById('cjFaseTypen') || {}).innerText || '';
    S.modusKeuze.conj = 'moeilijk'; conjRonde = null; conjIdx = null; renderFun();
    const b = (document.getElementById('cjFaseTypen') || {}).innerText || '';
    return { makkelijk: a, moeilijk: b, modusNu: conjModusNu() };
  });

  console.log('\n-- de regel is niet stil --');
  ok(/tellen niet mee/.test(zichtbaar.makkelijk),
    'in meerkeuze staat er dat aangeklikte antwoorden niet meetellen ("' + zichtbaar.makkelijk + '")');
  ok(zichtbaar.moeilijk === '',
    'CONTROLE: en als je typt staat die zin er niet, want dan slaat hij nergens op');

  // ---- 3. typen opent de fase wel ----
  await page.evaluate(() => { conjRonde = null; conjIdx = null; cjMk = null; });
  await speel(page, 'moeilijk', 10);
  const naTypen = await page.evaluate(() => ({
    open: S.conjOpen,
    meter: conjFaseScore(CONJ_FASES[0].id)
  }));

  console.log('\n-- tien goede antwoorden, getypt --');
  ok(naTypen.open === start.open + 1,
    'CONTROLE: de fase gaat WEL open van getypte antwoorden (open: ' + start.open + ' → ' + naTypen.open + ')');

  // ---- 4. een foute klik gaat nog steeds het foutenboek in ----
  const foutBoek = await page.evaluate(() => {
    S.errors = {};
    S.modusKeuze.conj = 'makkelijk';
    conjRonde = null; conjIdx = null; cjMk = null; funView = 'conj'; renderFun();
    const c = conjIdx, t = c.t || 'presente';
    const correct = conjVorm(c.verb, c.p, t);
    const fouteKnop = Array.prototype.map.call(document.querySelectorAll('#cjOpties button'), (b) => b.innerText.trim())
      .filter((x) => x !== correct)[0];
    const b = Array.prototype.filter.call(document.querySelectorAll('#cjOpties button'), (x) => x.innerText.trim() === fouteKnop)[0];
    if (b) b.click();
    return { sleutels: Object.keys(S.errors || {}).length, meter: conjFaseScore(conjFaseNu().id).n };
  });

  console.log('\n-- een foute klik telt nog steeds als fout --');
  ok(foutBoek.sleutels > 0,
    'CONTROLE: een foute aangeklikte vorm gaat het foutenboek in, dus de herhaling brengt hem terug (' + foutBoek.sleutels + ')');
  ok(foutBoek.meter === 0, 'en hij vult de meter niet, ook niet als fout');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
