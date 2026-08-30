// pw-corrdoos.js (30 aug, v23.208) — de dagrem staat nu ook op de regels van El Corrector
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 30 aug, over zijn zwakke plekken: "Me, te of se · 11 fout van 22 beurten · doosje 0/5" en
// "Lo, la of le · 9 fout van 16 · doosje 0/5". Dat zijn precies de twee regels die hij het vaakst
// tegenkomt, en dat is geen toeval.
//
// v23.170 repareerde de dagrem in gramBij(): het eerste antwoord van de dag bepaalt de doos, en wat
// je daarna die dag nog doet verandert hem niet meer. Zonder die rem hangt je einddoos af van de
// VOLGORDE van je antwoorden binnen een dag. corrSrsBij() heeft die rem nooit gekregen; daar wint
// het laatste antwoord van je sessie.
//
// Nagemeten over 200 rondes van El Corrector, acht zinnen per ronde, alle lessen open:
//
//   rondes waarin minstens één regel meer dan eens langskomt : 188 van 200 (94%)
//   unieke regels per ronde                                  : 5,9 van 8
//   beurten op de meest voorkomende regel per ronde          : 2,3 gemiddeld
//
// Een echte ronde uit die meting: reflexivo acento reflexivo predicado lidwoord reflexivo porpara
// porpara. Drie keer reflexivo, oftewel "Me, te of se". Goed, goed, fout eindigt op doos 0; fout,
// goed, goed eindigt op doos 1. En omdat corrRegelVolgorde() de regels die due zijn vooraan zet,
// krijgen juist de regels die je het meest oefent de meeste beurten per ronde en dus de grootste
// kans om op een fout te eindigen. Hoe meer je oefent, hoe vaster je op nul staat.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ALLEEN HET EERSTE ANTWOORD VAN DE DAG TELT VOOR DE DOOS. Dit is de eigenlijke regel.
//   2. TEGENMETING BIJ 1: een goede en een foute start lopen wél uit elkaar. Anders is proef 1
//      groen te krijgen door de doos nooit te laten bewegen.
//   3. DE RESET IS ER NOG. Een foute start gaat helemaal naar doos 0 en niet één stapje. Dit is met
//      opzet: één stap terug is op 22 augustus voorgesteld en afgewezen, zie pw-doos.js en de
//      leerkaart. Deze proef staat er zodat niemand hem later alsnog verzacht.
//   4. EEN MISSER LATER OP DE DAG VERDWIJNT NIET: de doos blijft staan, maar de regel komt
//      overmorgen terug in plaats van pas over dertig dagen.
//   5. DE TELLERS BLIJVEN ELK ANTWOORD TELLEN. Die zijn de geschiedenis, niet het oordeel.
//   6. EN DE VOLGORDE BINNEN EEN RONDE MAAKT NIET MEER UIT. Dit is Stefans geval, letterlijk
//      nagespeeld met de ronde uit de meting hierboven.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwCd' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    const id = (CORR_REGELS[0] || {}).id;
    uit.regelId = id;
    uit.intervallen = CORR_INTERVALS.slice();

    /* een dag naspelen: begin op een doos die je echt hebt opgebouwd, en geef dan de reeks
       antwoorden van vandaag. bd wordt leeggemaakt zodat "vandaag" nog niet beoordeeld is. */
    const dag = function (startBox, antwoorden) {
      S.corr = {};
      for (let i = 0; i < startBox; i++) { corrSrsBij(id, true); S.corr[id].bd = ''; }
      S.corr[id].bd = '';
      antwoorden.forEach(function (g) { corrSrsBij(id, g); });
      const st = S.corr[id];
      return { box: st.box, due: st.due, goed: st.goed, fout: st.fout };
    };

    // ---- 1 en 2 ----
    uit.alleenGoed = dag(2, [true]);
    uit.goedDanFout = dag(2, [true, false]);
    uit.goedDanTweeFout = dag(2, [true, false, false]);
    uit.alleenFout = dag(2, [false]);
    uit.foutDanGoed = dag(2, [false, true]);
    uit.vijfGoed = dag(2, [true, true, true, true, true]);

    // ---- 3. de reset ----
    uit.fouteStart = dag(4, [false]);
    uit.foutMetGoedErna = dag(4, [false, true, true, true]);

    // ---- 4. een misser later op de dag ----
    uit.overmorgen = addDays(today(), 2);
    uit.laatFout = dag(3, [true, false]);
    uit.zonderFout = dag(3, [true]);

    /* ---- 6. Stefans ronde, letterlijk. Drie beurten op reflexivo binnen één ronde van acht, in de
       twee volgordes die onder de oude regel uiteenliepen. ---- */
    uit.rondeAB = dag(2, [true, true, false]);
    uit.rondeBA = dag(2, [false, true, true]);
    S.corr = {};
    return uit;
  });

  console.log('\n-- 1 en 2. alleen het eerste antwoord van de dag telt --');
  console.log('   regel "' + r.regelId + '", intervallen ' + JSON.stringify(r.intervallen));
  console.log('   [goed]=' + r.alleenGoed.box + ' [goed,fout]=' + r.goedDanFout.box +
    ' [goed,fout,fout]=' + r.goedDanTweeFout.box + ' · [fout]=' + r.alleenFout.box +
    ' [fout,goed]=' + r.foutDanGoed.box);
  ok(r.alleenGoed.box === r.goedDanFout.box && r.goedDanFout.box === r.goedDanTweeFout.box,
    'na een goede start verandert geen enkele fout van die dag je doos nog (dit was de bug)');
  ok(r.alleenFout.box === r.foutDanGoed.box,
    'en na een foute start geen enkel goed antwoord van die dag');
  ok(r.alleenGoed.box !== r.alleenFout.box,
    'TEGENMETING: terwijl een goede en een foute start wél uit elkaar lopen (' +
      r.alleenGoed.box + ' tegen ' + r.alleenFout.box + ')');
  ok(r.vijfGoed.box === 3, 'vijf goede antwoorden klimmen één doos, niet vijf (' + r.vijfGoed.box + ')');

  console.log('\n-- 3. het controlegeval: de reset is er nog --');
  console.log('   ' + JSON.stringify(r.fouteStart));
  ok(r.fouteStart.box === 0,
    'een fout eerste antwoord gaat van doos 4 helemaal naar 0, niet één stapje (' + r.fouteStart.box + ')');
  ok(r.foutMetGoedErna.box === 0,
    'ook met goede antwoorden erna diezelfde dag (' + r.foutMetGoedErna.box + ')');

  console.log('\n-- 4. een misser later op de dag verdwijnt niet --');
  console.log('   met misser: due ' + r.laatFout.due + ' · zonder: due ' + r.zonderFout.due);
  ok(r.laatFout.box === r.zonderFout.box, 'de doos van vandaag staat al vast en beweegt niet meer');
  ok(r.laatFout.due === r.overmorgen, 'maar je ziet de regel overmorgen terug (' + r.laatFout.due + ')');
  ok(r.zonderFout.due !== r.overmorgen,
    'terwijl een dag zonder missers zijn volle wachttijd houdt (' + r.zonderFout.due + ')');

  console.log('\n-- 5 en 6. de tellers, en Stefans ronde --');
  /* twee goede beurten om op doos 2 te komen, plus de vijf van vandaag: de teller telt ze allemaal,
     ook de vier die de doos vandaag niet meer raken. */
  ok(r.vijfGoed.goed === 2 + 5,
    'de teller telt elk antwoord, ook de antwoorden die de doos niet meer raken (' + r.vijfGoed.goed + ' = 2 opbouw + 5 vandaag)');
  ok(r.goedDanTweeFout.fout === 2, 'en dat geldt ook voor de fouten (' + r.goedDanTweeFout.fout + ')');
  console.log('   goed,goed,fout → doos ' + r.rondeAB.box + ' · fout,goed,goed → doos ' + r.rondeBA.box);
  ok(r.rondeAB.box !== r.rondeBA.box,
    'de twee volgordes verschillen nog steeds, want hun eerste antwoord verschilt (' +
      r.rondeAB.box + ' tegen ' + r.rondeBA.box + ')');
  ok(r.rondeAB.box === r.alleenGoed.box,
    'maar drie beurten op reflexivo in één ronde geven dezelfde doos als één goede beurt (' +
      r.rondeAB.box + '), en dat was het defect');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
