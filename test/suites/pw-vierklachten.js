// pw-vierklachten.js (3 sep, v23.232) — zegt de app iets over jou dat klopt, en vergeet hij wat hij moet vergeten?
//
// WAAROM DEZE SUITE ER IS
//
// Vier klachten van Stefan op één dag. Ze lijken los maar hebben dezelfde vorm: de app beweert iets
// wat niet waar is, of onthoudt iets wat hij hoort te vergeten.
//
//   1. "el la los las die ken ik echt wel (...) het blijft fout zeggen terwijl ik nu al dagen lang
//      alles goed doe."
//   2. "als ik naar de puzzel ga staat ie nog voorgevuld met het antwoord van vorige keer, hij moet
//      opnieuw beginnen standaard."
//   3. "als ik een antwoord intyp wordt het vakje niet groen of rood."
//   4. "het spiekbriefje kan ik ook niet vinden."
//
// WAT DEZE SUITE BEWAAKT
//
//   1. "FOUT GEGAAN" LEEST DE DATUM EN NIET DE OPTELSOM. Gebouwd: een concept met honderd fouten van
//      vorige maand en een doosje op nul zegt niets meer. Eentje dat vandaag misging wél. Dit was op
//      VIER plekken met de hand uitgeschreven, en de vierde is de ergste: gcVandaagLijst() zette
//      alles wat "fout ging" vooraan, dus El of la werd elke dag opnieuw het onderwerp van vandaag.
//   2. EEN OUDE FOUT KIEST NIET MEER HET ONDERWERP VAN VANDAAG. Het gevolg dat Stefan voelde.
//   3. EEN AFGEMAAKTE PUZZEL KOMT NOOIT TERUG. Gebouwd: alle woorden gevonden, opslag gevuld,
//      ltHerstel() weigert. Plus het controlegeval: een half afgemaakte puzzel komt WEL terug, want
//      anders bewijst de proef alleen dat herstellen stuk is.
//   4. HET WOORD KLEURT. Een lang genoeg woord dat er niet in zit wordt rood, een woord dat er wel in
//      zit groen, en te kort blijft neutraal. Drie uitkomsten, want twee zou ook door "altijd rood"
//      gehaald worden.
//   5. DE SPIEKBRIEF GAAT OPEN. spiekOpen(i) toont die ene kaart met zijn titel en een weg terug, en
//      het tabblad langs de gewone weg toont weer de route.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwVk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1 en 2. "fout gegaan" leest de datum ----
  console.log('\n-- 1 en 2. een fout van vorige maand is geen bericht --');
  const oordeel = await page.evaluate(() => {
    const cid = 'genero';
    function zet(laatst, box) {
      S.gram = {};
      S.gram[cid] = { box: box, due: today(), goed: 40, fout: 17, laatst: laatst };
      /* Niet meten of het concept vandaag gekozen wordt (dat mag: het is gewoon toe), maar in welk
         BAKJE het valt. gcVandaagReden() zegt dat in woorden, en dat is precies de zin die Stefan
         elke dag opnieuw zag. */
      return { staat: gcStaatFout(gramLees(cid)),
               html: gcStatusHtml(cid).replace(/<[^>]*>/g, ''),
               reden: gcVandaagReden() };
    }
    return {
      vandaagFout: zet(today(), 0),
      gisteren: zet(addDays(today(), -1), 0),
      oud: zet(addDays(today(), -30), 0),
      sterk: zet(today(), 4)
    };
  });
  Object.keys(oordeel).forEach(function (k) {
    const o = oordeel[k];
    console.log('   ' + k.padEnd(12) + 'fout=' + String(o.staat).padEnd(6) + '"' + o.html + '"' +
      '  · reden vandaag: "' + o.reden + '"');
  });
  ok(oordeel.vandaagFout.staat && /fout gegaan/.test(oordeel.vandaagFout.html),
    'een fout van vandaag heet "fout gegaan"');
  ok(oordeel.gisteren.staat, 'gisteren telt ook nog mee, want een dag is geen bewijs van beterschap');
  ok(!oordeel.oud.staat && !/fout gegaan/.test(oordeel.oud.html),
    'CONTROLE: honderd fouten van dertig dagen terug zeggen niets meer ("' + oordeel.oud.html + '")');
  ok(!oordeel.sterk.staat,
    'CONTROLE: en een concept dat wél in een doosje zit heet nooit "fout gegaan", ook niet vandaag');
  ok(/fout/i.test(oordeel.vandaagFout.reden),
    'een verse fout komt terug als "wat fout ging" op je dagscherm');
  ok(!/fout/i.test(oordeel.oud.reden),
    'en dit is waar Stefan het aan merkte: een oude fout doet dat niet meer ("' + oordeel.oud.reden + '")');

  // ---- 3. de puzzel begint opnieuw ----
  console.log('\n-- 3. een afgemaakte puzzel komt niet terug --');
  const puzzel = await page.evaluate(() => {
    funView = 'letras';
    ltVergeet();
    ltNieuw();
    if (!ltSpel) return { geenPuzzel: true };
    const alle = ltSpel.doelen.map(function (d) { return ltPlat(d.es); });
    // alles gevonden, en dan bewaren: precies de toestand van Stefans schermafbeelding
    alle.forEach(function (p) { ltSpel.gevonden[p] = 1; });
    ltBewaar();
    const opgeslagen = !!(S.letras && S.letras.gevonden && S.letras.gevonden.length === alle.length);
    const vlag = !!(S.letras && S.letras.af);
    ltSpel = null;
    const herstelAf = ltHerstel();
    const naAf = !!S.letras;

    // het controlegeval: half af hoort WEL terug te komen
    ltVergeet(); ltNieuw();
    const helft = ltSpel.doelen.slice(0, 1).map(function (d) { return ltPlat(d.es); });
    helft.forEach(function (p) { ltSpel.gevonden[p] = 1; });
    ltBewaar();
    ltSpel = null;
    const herstelHalf = ltHerstel();
    const halfGev = ltSpel ? Object.keys(ltSpel.gevonden).length : -1;

    // en de verversing van de speeltuin wist geheugen én opslag
    ltVergeet(); ltNieuw(); ltBewaar();
    const voorVers = !!S.letras;
    speelVers('letras');
    return { geenPuzzel: false, doelen: alle.length, opgeslagen: opgeslagen,
             herstelAf: herstelAf, naAf: naAf, vlag: vlag,
             herstelHalf: herstelHalf, halfGev: halfGev,
             voorVers: voorVers, naVers: !!S.letras, spelNaVers: !!ltSpel };
  });
  console.log('   ' + JSON.stringify(puzzel));
  ok(!puzzel.geenPuzzel, 'er is een puzzel om mee te meten');
  ok(puzzel.opgeslagen, 'CONTROLE: de afgemaakte puzzel stond echt in de opslag, dus er valt iets te weigeren');
  ok(puzzel.vlag, 'en hij droeg de vlag "af", gezet door het spel dat het zeker wist');
  ok(puzzel.herstelAf === false, 'en ltHerstel() weigert hem');
  ok(puzzel.naAf === false, 'en ruimt hem meteen op, zodat hij ook langs een andere weg niet terugkomt');
  ok(puzzel.herstelHalf === true && puzzel.halfGev === 1,
    'CONTROLE: een half afgemaakte puzzel komt wél terug (' + puzzel.halfGev + ' gevonden)');
  ok(puzzel.voorVers && !puzzel.naVers && !puzzel.spelNaVers,
    'de verversing van de speeltuin wist het geheugen én de opslag');

  // ---- 4. het woord kleurt ----
  console.log('\n-- 4. het gevormde woord wordt rood of groen --');
  const kleur = await page.evaluate(() => {
    ltVergeet(); ltNieuw();
    function tik(woord) {
      ltSpel.gekozen = [];
      const over = ltSpel.letters.slice();
      String(woord).split('').forEach(function (L) {
        for (let i = 0; i < ltSpel.letters.length; i++) {
          if (ltSpel.gekozen.indexOf(i) === -1 && ltSpel.letters[i] === L) { ltSpel.gekozen.push(i); return; }
        }
      });
      return { woord: ltHuidig(), staat: ltStaat() };
    }
    const doel = ltPlat(ltSpel.doelen[0].es);
    const goed = tik(doel);
    // een woord van dezelfde lengte uit dezelfde letters dat geen doel is
    let mis = null;
    const gedraaid = doel.split('').reverse().join('');
    if (gedraaid !== doel) mis = tik(gedraaid);
    const kort = tik(doel.slice(0, 1));
    return { doel: doel, goed: goed, mis: mis, kort: kort, min: LT_MIN };
  });
  console.log('   doel "' + kleur.doel + '" -> ' + kleur.goed.staat +
    (kleur.mis ? ' · omgedraaid "' + kleur.mis.woord + '" -> ' + kleur.mis.staat : '') +
    ' · te kort "' + kleur.kort.woord + '" -> "' + kleur.kort.staat + '"');
  ok(kleur.goed.staat === 'raak', 'een woord dat in de puzzel zit wordt groen');
  ok(!kleur.mis || kleur.mis.staat === 'mis',
    'CONTROLE: een even lang woord uit dezelfde letters dat er niet in zit wordt rood');
  ok(kleur.kort.staat === '', 'en te kort blijft neutraal, want daar valt nog niets van te vinden');

  // ---- 5. de spiekbrief gaat open ----
  console.log('\n-- 5. de spiekbrief gaat open, met een weg terug --');
  const spiek = await page.evaluate(() => {
    // pak een toetsje dat een spiekbrief heeft; dat is de knop na een matig resultaat
    const qz = (QUIZZES || []).filter(function (q) { return q.spiek && q.spiek.length; })[0];
    spiekOpen(qz.spiek[0]);
    renderCheat();
    const el = document.getElementById('cheat');
    const tekst = (el.innerText || '').replace(/\s+/g, ' ');
    const titel = spiekTitel(CHEATSHEET[qz.spiek[0]]);
    const uit = { qz: qz.id, idx: qz.spiek[0], titel: titel,
                  toontTitel: tekst.indexOf(titel) !== -1,
                  terug: !!document.getElementById('btnSpiekTerug'),
                  lengte: tekst.length,
                  route: /31 onderwerpen|onderwerpen, in de volgorde/.test(tekst) };
    // terug, en dan hoort de route er weer te staan
    document.getElementById('btnSpiekTerug').click();
    const na = (document.getElementById('cheat').innerText || '').replace(/\s+/g, ' ');
    uit.naTerugRoute = /in de volgorde waarin ze op elkaar bouwen/.test(na);
    // en langs de gewone weg binnenkomen laat ook de route zien
    spiekOpen(qz.spiek[0]);
    show('lessen', true);
    show('spiekbrief', true);
    const gewoon = (document.getElementById('cheat').innerText || '').replace(/\s+/g, ' ');
    uit.gewoneWegRoute = /in de volgorde waarin ze op elkaar bouwen/.test(gewoon);
    return uit;
  });
  console.log('   ' + spiek.qz + ' -> spiekbrief ' + spiek.idx + ': "' + spiek.titel + '" (' + spiek.lengte + ' tekens)');
  ok(spiek.toontTitel, 'de kaart staat er, met zijn eigen titel erboven');
  ok(spiek.lengte > 200, 'en er staat echt een spiekbrief in en niet alleen een kop (' + spiek.lengte + ' tekens)');
  ok(!spiek.route, 'CONTROLE: de route van 31 onderwerpen staat er niet, dus je landt niet op het tabblad');
  ok(spiek.terug, 'er is een weg terug');
  ok(spiek.naTerugRoute, 'en die brengt je bij de route');
  ok(spiek.gewoneWegRoute, 'en wie het tabblad langs de gewone weg opent ziet de route, niet de laatste kaart');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
