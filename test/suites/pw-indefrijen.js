// pw-indefrijen.js (1 sep, v23.227) — heeft het indefinido dezelfde soort rijen als het presente?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 1 sep: "de grammatica gaat niet helemaal goed. ik mis daar denk ik goede uitleg /
// instructie op het moment. werkwoorden vervoegen (presente) gaat nu wel goed, dus die vorm kunnen
// we ook voor de andere tijdsvormen voor werkwoorden."
//
// Gemeten waar het verschil zat, en het was niet de vorm. "De les" (LES_STAPPEN) werkte al voor elke
// open tijd. Het verschil was het AANTAL rijen: het presente had één tijdrij plus zes patroonrijen,
// het indefinido had er één. De twintig onregelmatige indefinido-vormen stonden in één berg, terwijl
// de 22 onregelmatige van het presente in zes behapbare families waren geknipt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ELK ONREGELMATIG WERKWOORD STAAT IN PRECIES ÉÉN RIJ. Niet nul (dan valt het buiten de les) en
//      niet twee (dan leert de rij iets anders dan hij belooft). Dit is de proef die afgaat zodra
//      iemand een werkwoord toevoegt dat nergens in past, en dat is precies wanneer je het wil weten.
//   2. HET CONTROLEGEVAL: EEN REGELMATIG WERKWOORD STAAT IN GEEN ENKELE RIJ. Zonder dat bewijst
//      punt 1 niets, want een herkenner die overal ja op zegt haalt hem ook.
//   3. DE RIJ DRAAGT ZIJN EIGEN TIJD. lesRij() zette hier hardgecodeerd "presente" neer. Een rij over
//      estuve zou dus met "estoy" zijn voorgedaan, en dat is erger dan geen rij.
//   4. DE POORT. Wie alleen het presente open heeft, krijgt geen rij over dije en dijeron. Gebouwd:
//      de fase wordt in het geheugen op presente gezet en daarna op indefinido.
//   5. HET VOORBEELD KLOPT. conjPatroonModel() kiest een werkwoord dat in díe tijd in precies één rij
//      staat, anders doet de les over de sterke u zijn voorbeeld met een werkwoord dat ook een
//      klinkerwissel heeft.
//   6. HET PRESENTE IS NIET VERANDERD. Zes rijen, dezelfde werkwoorden erin. Deze ronde bouwde de
//      herkenning om (van soort/sleutel naar een functie per rij) en dat mag niets verschuiven aan
//      wat er al werkte.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwIr' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1 en 2. de dekking ----
  console.log('\n-- 1 en 2. elk onregelmatig werkwoord in precies één rij --');
  const dekking = await page.evaluate(() => {
    const zonder = [], dubbel = [], regMetRij = [];
    let onreg = 0, reg = 0;
    VERBOS.forEach(function (v) {
      if (!conjHeeftTijd(v, 'indefinido')) return;
      const n = conjPatroonAantal(v, 'indefinido');
      if (conjRegelmatigIn(v, 'indefinido')) {
        reg++;
        if (n > 0) regMetRij.push(v.inf + ' (' + n + ')');
      } else {
        onreg++;
        if (n === 0) zonder.push(v.inf);
        if (n > 1) dubbel.push(v.inf + ' (' + n + ')');
      }
    });
    const rijen = CONJ_PATRONEN
      .filter(function (p) { return conjPatroonTijd(p) === 'indefinido'; })
      .map(function (p) { return { id: p.id, n: conjPatroonPool(p.id).length,
                                   model: (conjPatroonModel(p.id) || {}).inf }; });
    return { onreg: onreg, reg: reg, zonder: zonder, dubbel: dubbel, regMetRij: regMetRij, rijen: rijen };
  });
  dekking.rijen.forEach(function (r) {
    console.log('   ' + r.id.padEnd(15) + String(r.n).padStart(2) + ' werkwoorden · voorbeeld ' + r.model);
  });
  console.log('   ' + dekking.onreg + ' onregelmatig, ' + dekking.reg + ' regelmatig');
  ok(dekking.rijen.length >= 6, 'er zijn genoeg rijen om van een opdeling te spreken (' + dekking.rijen.length + ')');
  ok(dekking.zonder.length === 0,
    'geen enkel onregelmatig werkwoord valt buiten de rijen (' + (dekking.zonder.join(', ') || 'geen') + ')');
  ok(dekking.dubbel.length === 0,
    'en geen enkel werkwoord staat in twee rijen (' + (dekking.dubbel.join(', ') || 'geen') + ')');
  ok(dekking.regMetRij.length === 0,
    'CONTROLE: een regelmatig werkwoord staat in geen enkele rij (' + (dekking.regMetRij.join(', ') || 'geen') + ')');
  ok(dekking.reg > 0 && dekking.onreg > 0, 'en er zijn er van allebei, dus die twee proeven meten iets');

  // ---- 3 en 5. de rij draagt zijn tijd, en het voorbeeld klopt ----
  console.log('\n-- 3 en 5. de rij draagt zijn eigen tijd --');
  const rij = await page.evaluate(() => {
    const uit = [];
    CONJ_PATRONEN.filter(function (p) { return conjPatroonTijd(p) === 'indefinido'; }).forEach(function (p) {
      const r = lesRij(p.id);
      const v0 = conjPatroonModel(p.id);
      uit.push({ id: p.id, t: r ? r.t : null, vb: r ? r.vb : null,
                 presente: v0 ? conjVorm(v0, 0, 'presente') : null,
                 indef: v0 ? conjVorm(v0, 0, 'indefinido') : null,
                 alleen: v0 ? conjPatroonAantal(v0, 'indefinido') : -1 });
    });
    return uit;
  });
  rij.forEach(function (r) { console.log('   ' + r.id.padEnd(15) + r.t + ' · toont "' + r.vb + '" (presente zou "' + r.presente + '" zijn)'); });
  ok(rij.every(function (r) { return r.t === 'indefinido'; }), 'elke indefinido-rij zegt zelf dat hij indefinido is');
  ok(rij.every(function (r) { return r.vb === r.indef; }), 'en doet zich voor met de indefinido-vorm');
  ok(rij.every(function (r) { return r.vb !== r.presente; }),
    'CONTROLE: die vorm is echt een andere dan de presente-vorm van hetzelfde werkwoord');
  ok(rij.every(function (r) { return r.alleen === 1; }),
    'het voorbeeldwerkwoord van elke rij staat in díe tijd in precies één rij');

  // ---- 4. de poort ----
  console.log('\n-- 4. de poort: geen dije voordat het indefinido open is --');
  const poort = await page.evaluate(() => {
    function meet(fase) {
      S.conjFase = fase;
      S.conjOpen = conjFaseIdx(fase);
      const ids = lesRijIds();
      return { tijden: conjOpenTijden().join(','),
               indefRijen: ids.filter(function (x) { return x.indexOf('indef.') === 0; }).length,
               presRijen: ids.filter(function (x) { return /^(schoen|yo)\./.test(x); }).length };
    }
    const voor = meet('presente');
    const na = meet('indef');
    return { voor: voor, na: na };
  });
  console.log('   op fase presente: ' + JSON.stringify(poort.voor));
  console.log('   op fase indef   : ' + JSON.stringify(poort.na));
  ok(poort.voor.indefRijen === 0, 'met alleen het presente open staat er geen indefinido-rij in de les');
  ok(poort.na.indefRijen > 0, 'en zodra het indefinido open is wel (' + poort.na.indefRijen + ')');
  ok(poort.voor.presRijen > 0 && poort.na.presRijen === poort.voor.presRijen,
    'CONTROLE: de presente-rijen staan er in allebei de gevallen, dus de poort meet de tijd en niet het bestaan');

  // ---- 6. het presente is niet veranderd ----
  console.log('\n-- 6. het presente is niet veranderd --');
  const pres = await page.evaluate(() => {
    return CONJ_PATRONEN.filter(function (p) { return conjPatroonTijd(p) === 'presente'; })
      .map(function (p) { return p.id + ':' + conjPatroonPool(p.id).map(function (v) { return v.inf; }).join('+'); });
  });
  pres.forEach(function (x) { console.log('   ' + x); });
  /* De verwachting staat hier voluit en niet als aantal. Deze ronde bouwde de herkenning om van
     soort/sleutel naar een functie per rij, en dan is "er zijn er nog steeds zes" geen bewijs: de
     vraag is of er in elke rij nog dezelfde werkwoorden staan. */
  const verwacht = [
    'schoen.ie:tener+querer+venir+empezar+pensar+sentir+preferir',
    'schoen.ue:poder+jugar+dormir+volver',
    'yo.go:tener+hacer+decir+poner+salir+venir',
    'yo.oy:ser+estar+ir+dar',
    'schoen.i:decir+pedir',
    'yo.los:saber+ver'
  ];
  ok(pres.join(' | ') === verwacht.join(' | '),
    'de zes presente-rijen bevatten nog precies dezelfde werkwoorden');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
