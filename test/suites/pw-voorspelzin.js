// pw-voorspelzin.js (30 aug, v23.206) — de voortgangspagina telt overal hetzelfde
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 30 aug: "waarom kan de app nog niet voorspellen? ik heb inmiddels een streak van 40 dagen."
//
// Op één scherm stonden vijf getallen over die ene vraag, en drie klopten niet:
//
//   kop          639 woorden houd je actief bij          (live gerekend)
//   lijn         "van 493 op 17 augustus naar 621 nu"    (621 = de WEEKmeting van zes dagen eerder)
//   as           "tot 715, je eigen hoogste punt"        (715 = ceil(max * 1,15), niet zijn hoogste punt)
//   doelkaart    "3 dagmetingen over 13 dagen, over 2 dagen"
//   voorspelling "5 weekmetingen ... nog 1 week te gaan" (de verkeerde teller bij de verkeerde poort)
//
// Die laatste is de ergste: voorspelWaar() hangt sinds v23.203 aan tempoMeting(), en die kijkt naar
// DAGmetingen. De zin ernaast telde S.meting en rekende nog = max(1, 3 - gemeten). Met vijf
// weekmetingen is dat max(1, -2) = 1, geklemd, dus daar stond "nog 1 week" ongeacht wat er lag en
// dat zou er over een maand nog staan.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE WACHTZIN VAN DE VOORSPELLING KOMT UIT DEZELFDE FUNCTIE ALS DIE VAN DE DOELKAART, en noemt
//      dus dagen en geen weken. Dit is de eigenlijke regel.
//   2. CONTROLE BIJ 1: leg er genoeg dagpunten neer en de strook verschijnt echt. Anders zou proef 1
//      slagen op een scherm dat altijd wacht.
//   3. DE LIJN TEKENT DE REEKS DIE DE METER GEBRUIKT: de dagreeks zodra die twee punten heeft.
//   4. CONTROLE BIJ 3: met één dagpunt valt hij terug op de weekreeks, en dan staat er een ander
//      eindgetal. Zonder dit verschil bewijst proef 3 niets.
//   5. HET BIJSCHRIFT ZEGT ALLEEN "NU" ALS HET LAATSTE PUNT VAN VANDAAG IS.
//   6. HET GETAL DAT "JE HOOGSTE PUNT" HEET IS HET MAXIMUM VAN DE GETEKENDE REEKS, en de as-top
//      staat er los naast. Controle: zet het maximum in het midden, dan verandert dat getal mee.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwVz' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  /* De toestand van Stefans scherm, exact: drie dagmetingen over dertien dagen, vijf weekmetingen
     waarvan er twee dekw kennen. Zo hoort de app te wachten, en zo hoort de zin te klinken. */
  const zet = async (dagen, weken) => page.evaluate(([dagen, weken]) => {
    S.dagMeting = {};
    dagen.forEach(function (p) { S.dagMeting[p[0]] = { dek: { A1: 0, A2: 0 }, dekw: { A1: p[1], A2: 0 } }; });
    S.meting = {};
    weken.forEach(function (w) {
      S.meting[w[0]] = w[2] === null
        ? { d: w[1], dek: { A1: 0, A2: 0 } }
        : { d: w[1], dek: { A1: 0, A2: 0 }, dekw: { A1: w[2], A2: 0 } };
    });
    S.doelNiv = 'A1'; S.doelDatum = addDays(today(), 70);
    S.lang = 'nl';                      // de proef leest de Nederlandse zinnen
    try { persist(); } catch (e) {}
  }, [dagen, weken]);

  const D = async (n) => page.evaluate((n) => addDays(today(), n), n);
  const d13 = await D(-13), d6 = await D(-6), d0 = await D(0);

  // ---- 1 en 2. de wachtzin ----
  console.log('\n-- 1 en 2. de voorspelling wacht in dezelfde eenheid als de doelkaart --');
  /* vijf weekmetingen in de pot, waarvan er maar één dekw draagt, en twee dagpunten. Zo staat de
     meter nog stil (TEMPO_MIN_PUNTEN is sinds v23.207 drie) terwijl de oude teller vijf zou hebben
     geroepen. Dat verschil is precies wat deze proef meet. */
  await zet([[d13, 493], [d6, 621]],
            [['2026-W31', await D(-27), null], ['2026-W32', await D(-20), null],
             ['2026-W33', await D(-17), null], ['2026-W34', await D(-10), null],
             ['2026-W35', d6, 621]]);

  const w = await page.evaluate(() => {
    return { voorspel: voorspelHtml().replace(/<[^>]+>/g, ''),
             wacht: tempoWachtZin('A1'),
             stand: tempoStand('A1'),
             meting: Object.keys(S.meting).length };
  });
  console.log('   weekmetingen in de pot: ' + w.meting + ', dagpunten: ' + w.stand.heeft + ' over ' + w.stand.span + ' dagen');
  console.log('   voorspelling: ' + w.voorspel.slice(0, 220));
  ok(w.wacht && w.voorspel.indexOf(w.wacht) >= 0,
    'de voorspelling gebruikt letterlijk de wachtzin van de doelkaart');
  ok(!/nog\s*1\s*week/i.test(w.voorspel) && !/weekmeting/i.test(w.voorspel),
    'en telt geen weken of weekmetingen meer (dit was de bug)');
  ok(/dan is dat over 1 dag\./.test(w.voorspel),
    'hij zegt hoeveel dagen het nog is, uit dezelfde drempels als de meter (' + w.stand.heeft + '/' + w.stand.nodig + ')');

  /* CONTROLE: zonder dit zou proef 1 ook slagen op een scherm dat altijd wacht. Vijf dagpunten over
     dertien dagen haalt beide drempels, en dan hoort er een strook te staan. */
  await zet([[await D(-13), 493], [await D(-9), 540], [await D(-6), 590], [await D(-3), 615], [d0, 639]],
            [['2026-W35', d0, 639]]);
  const v2 = await page.evaluate(() => ({ h: voorspelHtml().replace(/<[^>]+>/g, ''),
                                          m: tempoMeting('A1') }));
  console.log('   met vijf punten: ' + JSON.stringify(v2.m && { gem: Math.round(v2.m.gem * 10) / 10, punten: v2.m.punten, bron: v2.m.bron }));
  ok(v2.m && v2.m.bron === 'dag' && !/Nog niet te zeggen/.test(v2.h),
    'CONTROLE: met vijf dagpunten over dertien dagen zwijgt hij niet meer');

  // ---- 3 t/m 6. de lijn ----
  console.log('\n-- 3 t/m 6. de lijn tekent de reeks die de meter gebruikt --');
  const lijn = async () => page.evaluate(() => {
    const c = voortgangCijfers ? voortgangCijfers() : null;
    const nivs = (c && c.samen && c.samen.nivs) || ['A1'];
    return { html: vgLijnHtml({ samen: { nivs: nivs } }).replace(/<[^>]+>/g, ''),
             reeks: vgReeks(nivs) };
  });

  await zet([[d13, 493], [d6, 621], [d0, 639]],
            [['2026-W33', d13, 493], ['2026-W34', d6, 621]]);
  const a = await lijn();
  console.log('   ' + a.html.slice(0, 200));
  ok(a.reeks.length === 3 && a.reeks.every(function (p) { return p.bron === 'dag'; }),
    'de lijn pakt de dagreeks (' + a.reeks.length + ' punten)');
  ok(a.html.indexOf('639') >= 0 && a.html.indexOf('621 nu') < 0,
    'en eindigt op het dagpunt van vandaag (639), niet op de weekmeting (621)');
  ok(/naar\s*639\s*nu/.test(a.html),
    'proef 5: het laatste punt is van vandaag, dus daar mag "nu" staan');
  ok(/hoogste punt is 639/.test(a.html) && /as loopt tot 735/.test(a.html),
    'proef 6: het hoogste punt is 639 en de as-top staat er los naast (735)');

  /* CONTROLE bij 3: met één dagpunt is er geen dagreeks en valt hij terug op de weken. Het
     eindgetal wordt dan een ander, en zonder dat verschil bewijst de proef hierboven niets. */
  await zet([[d0, 639]], [['2026-W33', d13, 493], ['2026-W34', d6, 621]]);
  const b = await lijn();
  console.log('   ' + b.html.slice(0, 200));
  ok(b.reeks.length === 2 && b.reeks.every(function (p) { return p.bron === 'week'; }),
    'CONTROLE: met één dagpunt valt de lijn terug op de weekreeks');
  ok(b.html.indexOf('621') >= 0 && b.html.indexOf('639') < 0,
    'CONTROLE: en dan staat er een ander eindgetal (621), dus proef 3 mat echt iets');
  ok(/op\s/.test(b.html) && !/621\s*nu/.test(b.html),
    'proef 5, andere kant: het laatste punt is van ' + d6 + ' en niet van vandaag, dus geen "nu"');

  /* CONTROLE bij 6: zet het maximum in het midden. Het getal achter "je hoogste punt" hoort mee te
     bewegen; deed het dat niet, dan noemde het gewoon het laatste punt. */
  await zet([[d13, 400], [d6, 800], [d0, 500]], [['2026-W33', d13, 400]]);
  const cM = await lijn();
  console.log('   ' + cM.html.slice(0, 200));
  ok(/hoogste punt is 800/.test(cM.html) && /naar\s*500\s*nu/.test(cM.html),
    'CONTROLE: het hoogste punt (800) is niet het laatste punt (500), en allebei staan er goed');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
