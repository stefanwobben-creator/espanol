// pw-spelronde.js (8 sep, v23.251) - kom je terug waar je was, of begint het spel opnieuw?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 8 september: "dat een spel altijd opnieuw moet beginnen ook niet [is opgelost]."
//
// Gemeten: negen spellen gestart, één stap gezet, pagina herladen, en gekeken of DEZELFDE ronde
// terugkwam. Let op het verschil met "is er weer een ronde": dat was er altijd, en precies daarom
// viel het niet op. Eén van de acht herstelde echt.
//
// De oorzaak stond in vijf regels die naast elkaar te zetten zijn:
//
//     if(!brokSpel)     brokStart();
//     if(!omkeerSpel)   omkeerStart();
//     if(!tijdvormSpel) tijdvormStart();
//     if(!zinSpel)      zinStart(null, null);
//     if(!adivSpel && !adivHerstel()) adivNieuw();     <- de enige die het goed doet
//
//     Een tak die "nog niet begonnen" en "je was al bezig" hetzelfde behandelt,
//     kan je voortgang niet bewaren.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE LIJST KOMT UIT DE APP. Deze suite loopt SPEL_RONDE af en niet een eigen lijstje. Komt er
//      een spel bij, dan wordt het hier vanzelf gemeten.
//   2. DEZELFDE RONDE KOMT TERUG NA EEN HERLAAD. Dezelfde opgaven in dezelfde volgorde, en op
//      dezelfde plek in de rij. Niet "er is weer een ronde".
//   3. HET CONTROLEGEVAL: "Nog een" gooit hem wél weg. Anders zou herstellen betekenen dat je nooit
//      meer een nieuwe ronde krijgt, en dat is de val die in v23.232 bij Letras beschreven staat.
//   4. EN EEN RONDE VAN GISTEREN KOMT NIET TERUG.
//   4b. LEG JE HEM ZELF WEG, DAN BLIJFT HIJ WEG. Dat onderscheid is de hele truc: een herlaad wist
//      het geheugen vóórdat de app ook maar één keer gekeken heeft, een knop wist hem daarna.
//      Zonder dat verschil kun je in De les niet meer terug naar het keuzemenu, want dat menu zet
//      de stand op null en de eerstvolgende render zette hem terug. pw-schoen viel daar als eerste
//      over om.
//   5. ELK GRAMMATICASPEL MET EEN VERSE-HAAK STAAT IN DE TABEL. Dat is de regel die "overal"
//      afdwingbaar maakt: een nieuw grammaticaspel dat zijn ronde niet bewaart, valt hier om.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

/* Per spel: hoe je hem start en hoe je één stap zet. Alleen dít staat hier, want het is de enige
   kennis die de proef zelf nodig heeft; welke spellen er zijn komt uit de app. */
const HOE = {
  brok:     { start: 'brokStart()',              stap: 'brokSpel.i = 4; brokSpel.goed = 3;' },
  omkeer:   { start: 'omkeerStart()',            stap: 'omkeerSpel.i = 4; omkeerSpel.goed = 3;' },
  tijdvorm: { start: 'tijdvormStart()',          stap: 'tijdvormSpel.i = 4; tijdvormSpel.goed = 3;' },
  zin:      { start: 'zinStart(null, null)',     stap: 'zinSpel.i = 3; zinSpel.goed = 2;' },
  les:      { start: 'lesStart(lesRijIds()[0])', stap: 'lesSpel.stap = 2;' }
};

/* De vingerafdruk van een ronde: de sleutels van de opgaven plus waar je staat. Bewust NIET de hele
   toestand, want die bevat werkwoord- en zinobjecten die na een herlaad nieuwe objecten zijn met
   dezelfde inhoud. Wat deze proef wil weten is of het dezelfde ronde is, niet of het dezelfde
   objecten in het geheugen zijn. */
const AFDRUK = `(function (v) {
  var e = SPEL_RONDE[v]; if (!e) return null;
  var st = e.lees(); if (!st) return null;
  if (e.krimp) return JSON.stringify(e.krimp(st));
  return JSON.stringify({ rij: (st.rij || []).map(e.sleutel), i: st.i, goed: st.goed, fout: st.fout });
})`;

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwSr' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => {
    S.lang = 'nl';
    for (let i = 0; i < 20; i++) S.lessons['__proef' + i] = { done: true };
    try { persist(); } catch (e) {}
  });

  // ---- 1. de lijst komt uit de app ----
  console.log('\n-- 1. welke spellen bewaren hun ronde --');
  const spellen = await page.evaluate(() => Object.keys(SPEL_RONDE));
  console.log('   ' + spellen.join(', '));
  ok(spellen.length >= 4, 'CONTROLE: er staan minstens vier spellen in SPEL_RONDE (' + spellen.length + ')');
  const zonderHoe = spellen.filter(function (v) { return !HOE[v]; });
  ok(zonderHoe.length === 0,
    'CONTROLE: en deze proef weet van elk hoe je hem start (' + (zonderHoe.join(',') || 'alle') + ')');

  // ---- 2. dezelfde ronde komt terug ----
  console.log('\n-- 2. na een herlaad sta je waar je was --');
  for (const v of spellen) {
    const h = HOE[v];
    const voor = await page.evaluate(([v, h, afdruk]) => {
      funView = v;
      try { S.spelRonde = {}; eval(h.start); } catch (e) { return { fout: e.message }; }
      const e2 = SPEL_RONDE[v];
      if (!e2.lees()) return { fout: 'geen ronde na start' };
      try { eval(h.stap); } catch (e) { return { fout: 'stap: ' + e.message }; }
      try { renderFun(); } catch (e) {}                 // hier gebeurt het bewaren
      return { afdruk: eval(afdruk)(v), opslag: !!(S.spelRonde || {})[v] };
    }, [v, h, AFDRUK]);
    if (voor.fout) { ok(false, v + ': ' + voor.fout); continue; }
    await page.reload();
    await page.waitForTimeout(800);
    const na = await page.evaluate(([v, afdruk]) => {
      funView = v;
      const leegVoorRender = !SPEL_RONDE[v].lees();
      try { renderFun(); } catch (e) {}
      return { leegVoorRender: leegVoorRender, afdruk: eval(afdruk)(v) };
    }, [v, AFDRUK]);
    ok(na.leegVoorRender, '   CONTROLE ' + v + ': het geheugen is na een herlaad echt leeg');
    ok(!!voor.opslag, '   CONTROLE ' + v + ': de ronde is opgeslagen');
    ok(na.afdruk === voor.afdruk,
      v + ': dezelfde ronde, op dezelfde plek' +
        (na.afdruk === voor.afdruk ? '' : '\n        voor: ' + String(voor.afdruk).slice(0, 120) +
                                          '\n        na  : ' + String(na.afdruk).slice(0, 120)));
  }

  // ---- 3. "Nog een" gooit hem wel weg ----
  console.log('\n-- 3. maar opnieuw beginnen kan gewoon --');
  const vers = await page.evaluate(([afdruk]) => {
    const v = Object.keys(SPEL_RONDE)[0];
    funView = v;
    S.spelRonde = {};
    brokStart(); brokSpel.i = 5;
    renderFun();
    const voor = eval(afdruk)(v);
    const inOpslag = !!(S.spelRonde || {})[v];
    speelVers(v);                       // dit is wat de tegel en "Nog een" doen
    const naVers = !!(S.spelRonde || {})[v];
    SPEL_RONDE[v].zet(null);
    renderFun();                        // en dan hoort er een NIEUWE ronde te komen
    return { v: v, voor: voor, na: eval(afdruk)(v), inOpslag: inOpslag, naVers: naVers };
  }, [AFDRUK]);
  ok(vers.inOpslag, 'CONTROLE: er stond een ronde in de opslag');
  ok(!vers.naVers, 'speelVers() gooit de bewaarde ronde weg, niet alleen het geheugen');
  ok(vers.na && vers.na !== vers.voor,
    'en daarna staat er een nieuwe ronde (' + String(vers.na).slice(0, 60) + ')');

  // ---- 4. een ronde van gisteren ----
  console.log('\n-- 4. gisteren is geen vandaag --');
  const oud = await page.evaluate(([afdruk]) => {
    const v = 'brok';
    funView = v;
    S.spelRonde = {};
    brokStart(); brokSpel.i = 6;
    renderFun();
    const voor = eval(afdruk)(v);
    S.spelRonde[v].d = addDays(today(), -1);      // dezelfde ronde, gedateerd op gisteren
    SPEL_RONDE[v].zet(null);
    renderFun();
    return { voor: voor, na: eval(afdruk)(v) };
  }, [AFDRUK]);
  ok(oud.na && oud.na !== oud.voor,
    'een ronde van gisteren wordt niet hersteld (' + String(oud.na).slice(0, 60) + ')');

  // ---- 4b. zelf weggelegd blijft weggelegd ----
  console.log('\n-- 4b. zelf weglopen is geen herlaad --');
  const zelf = await page.evaluate(([afdruk]) => {
    const v = 'les';
    funView = v;
    S.spelRonde = {}; _spelGezien = {};
    lesStart(lesRijIds()[0]); lesSpel.stap = 2;
    renderFun();                                  // bewaard
    const inOpslag = !!(S.spelRonde || {})[v];
    SPEL_RONDE[v].zet(null);                      // dit is wat de terugknop van De les doet
    renderFun();
    return { inOpslag: inOpslag, naKnop: eval(afdruk)(v), nogInOpslag: !!(S.spelRonde || {})[v] };
  }, [AFDRUK]);
  ok(zelf.inOpslag, 'CONTROLE: de lesronde stond in de opslag');
  ok(zelf.naKnop === null,
    'zet je hem zelf op leeg, dan blijft hij leeg (' + String(zelf.naKnop).slice(0, 50) + ')');
  ok(!zelf.nogInOpslag, 'en dan wordt de bewaarde ronde ook opgeruimd');

  // ---- 5. elk grammaticaspel met een verse-haak staat in de tabel ----
  console.log('\n-- 5. en dit geldt voor élk grammaticaspel --');
  const dekking = await page.evaluate(() => {
    const tegels = spelInfo().filter(function (g) { return g.gram && g.verse; });
    return {
      tegels: tegels.map(function (g) { return g.v; }),
      mist: tegels.filter(function (g) { return !SPEL_RONDE[g.v]; }).map(function (g) { return g.v; })
    };
  });
  console.log('   grammaticategels met een verse-haak: ' + dekking.tegels.join(', '));
  ok(dekking.tegels.length >= 4,
    'CONTROLE: er zijn er meerdere om te dekken (' + dekking.tegels.length + ')');
  ok(dekking.mist.length === 0,
    'ze staan allemaal in SPEL_RONDE (' + (dekking.mist.join(',') || 'niets ontbreekt') + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
