// pw-doos.js (22 aug, v23.170) — hangt je doosje af van wát je antwoordde of van de volgorde?
//
// WAAROM DIT ER IS
//
// Stefan, 22 aug: "ik heb el of la vandaag heel veel gedaan, waarbij ik ga twijfelen of het kapot is
// of dat de methode te streng is." Gemeten: genero stond op doos 0 met 52 goed tegen 17 fout, en op
// doos 0 stonden precies drie onderwerpen: genero, serestar, reflexivo.
//
// Het was kapot. In gramBij() gold de dagrem alleen omhoog:
//
//     goed  ->  doos omhoog, hoogstens één keer per dag (if st.bd !== today())
//     fout  ->  doos naar 0, altijd, zonder rem
//
// Zet die twee achter elkaar op één dag en je einddoos hangt af van de VOLGORDE van je antwoorden.
// Eerst goed dan fout eindigt op 0 en kan die dag niet meer omhoog, want de rem staat al aan. Eerst
// fout dan goed eindigt op doos 1. Eén fout per dag was dus genoeg om voor altijd op doos 0 te
// blijven, en doos 0 met twee of meer fouten is precies wat lesFlowGramId() de volledige microles
// laat geven.
//
// WAT ER NIET IS GEBOUWD, WANT DAT BEPAALT WAT HIER STAAT
//
// Mijn eerste ontwerp (leerkaart in het project) verzachtte de reset tot één doos omlaag en
// koppelde de vervaldatum los van de doos. Aangevallen en gesneuveld: SuperMemo noemt de
// één-stap-variant een onjuiste mutatie van Leitner, Anki reset standaard volledig, en het
// loskoppelen zou lesFlowGramId() stil slopen omdat die op doos 0 vuurt. Daarom bewaakt deze suite
// nadrukkelijk óók dat de reset er nog is.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE VOLGORDE VAN JE ANTWOORDEN DOET ER NIET TOE. Dit is het defect zelf, en het is met drie
//      regels na te rekenen in plaats van met vier weken veldmeting.
//
//      v23.225 heeft de regel hier aangescherpt, en het loont om te lezen waarom. De reparatie van
//      v23.170 maakte het EERSTE antwoord van de dag beslissend: dat haalde de volgorde-afhankelijk-
//      heid eruit voor [goed] tegenover [goed, fout], maar liet hem staan tussen [goed, fout] en
//      [fout, goed]. Dat viel niet op zolang een opfrisser één vraag had. Met twee vragen wel:
//      eerste goed, tweede fout, en je stond een doos hóger dan voor je begon.
//
//      De regel is nu: de dag wordt als geheel afgerekend, vanaf de doos waar hij vanochtend stond.
//      Eén misser vandaag en de promotie gaat niet door, in welke volgorde dan ook.
//   2. VIJF GOEDE ANTWOORDEN KLIMMEN ÉÉN DOOS, NIET VIJF. De dagrem, en die blijft.
//   3. DE RESET IS ER NOG. Het controlegeval, en het is de helft die het makkelijkst per ongeluk
//      wegvalt als iemand later "die straf is wel streng" denkt: een foute dag gaat helemaal terug
//      naar doos 0, niet één stapje.
//   4. EEN MISSER LATER OP DE DAG HAALT DE PROMOTIE WEG. Tot v23.225 bleef de doos staan en werd
//      alleen de datum teruggetrokken; dat was precies het gat waardoor een tweede vraag je hoger
//      kon zetten dan je stond.
//   5. HETZELFDE ONDERWERP STAAT NIET TWEE KEER IN ÉÉN LES. De opfrisser heet "opfris-genero" en de
//      microles "concept-genero", en de ontdubbeling vergeleek de hele string.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDs' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    /* Een dag naspelen: begin bij een bekende doos en geef een rij antwoorden. `vanaf` is de doos
       waar het onderwerp aan het begin van de dag staat, `rij` zijn de antwoorden op volgorde. */
    function dag(vanaf, rij) {
      S.gram = S.gram || {};
      S.gram.proef = { box: vanaf, due: '', goed: 0, fout: 0, laatst: '', bd: '' };
      rij.forEach(function (g) { gramBij('proef', g); });
      const st = S.gram.proef;
      return { box: st.box, due: st.due, goed: st.goed, fout: st.fout };
    }

    // ---- 1. de volgorde doet er niet toe ----
    uit.alleenGoed = dag(2, [true]);
    uit.goedDanFout = dag(2, [true, false]);
    uit.goedDanTweeFout = dag(2, [true, false, false]);
    uit.alleenFout = dag(2, [false]);
    uit.foutDanGoed = dag(2, [false, true]);
    /* En de lange versie van Stefans dag: één misser tussen een hoop goede antwoorden. Onder de
       oude regel eindigde dit onherroepelijk op doos 0. */
    uit.echteDag = dag(2, [true, true, true, false, true, true, true, true]);

    // ---- 2. de dagrem ----
    uit.vijfGoed = dag(1, [true, true, true, true, true]);

    // ---- 3. de reset is er nog ----
    uit.fouteStart = dag(4, [false]);
    uit.foutMetGoedErna = dag(4, [false, true, true, true]);

    // ---- 4. een misser later op de dag haalt de promotie weg ----
    uit.morgen = addDays(today(), 1);
    uit.laatFout = dag(3, [true, false]);
    uit.zonderFout = dag(3, [true]);

    // ---- 5. hetzelfde onderwerp niet twee keer in één les ----
    /* gcOpfrisId maakt "opfris-<id>" en lesFlowGramId geeft "concept-<id>". De ontdubbeling
       vergeleek de hele string, dus dezelfde genero kon er twee keer in. We dwingen dat geval af
       door lesFlowGramId hetzelfde onderwerp te laten teruggeven als de opfrisser. */
    const echteId = window.lesFlowGramId;
    const cid = (gcLijst()[0] || {}).id || 'concept-genero';
    const kaal = String(cid).replace(/^concept-/, '');
    S.gram[kaal] = { box: 0, goed: 0, fout: 1, due: today(), laatst: today(), bd: '' };
    window.lesFlowGramId = function () { return 'concept-' + kaal; };
    let lijst = [];
    try { lijst = lesFlowGramLijst(); } catch (e) { uit.lijstFout = e.message; }
    window.lesFlowGramId = echteId;
    uit.lijst = lijst;
    uit.kaalLijst = lijst.map(function (x) { return String(x).replace(/^(opfris|concept)-/, ''); });
    uit.dubbel = uit.kaalLijst.length !== new Set(uit.kaalLijst).size;
    return uit;
  });

  console.log('\n-- 1. de volgorde van je antwoorden doet er niet toe --');
  console.log('   [goed]=' + r.alleenGoed.box + ' [goed,fout]=' + r.goedDanFout.box +
    ' [goed,fout,fout]=' + r.goedDanTweeFout.box + ' · [fout]=' + r.alleenFout.box +
    ' [fout,goed]=' + r.foutDanGoed.box);
  ok(r.goedDanFout.box === r.foutDanGoed.box,
    'goed-dan-fout en fout-dan-goed komen op hetzelfde uit ('
      + r.goedDanFout.box + ' en ' + r.foutDanGoed.box + ')');
  ok(r.goedDanFout.box === r.goedDanTweeFout.box && r.goedDanFout.box === r.alleenFout.box,
    'en hoeveel goede antwoorden er ook omheen staan, één misser is één misser');
  /* De tegenmeting, anders is punt 1 groen te krijgen door de doos nooit te laten bewegen: een dag
     zonder missers en een dag met een misser moeten juist wél uit elkaar lopen. */
  ok(r.alleenGoed.box !== r.alleenFout.box,
    'terwijl een schone dag en een dag met een misser wél uit elkaar lopen ('
      + r.alleenGoed.box + ' tegen ' + r.alleenFout.box + ')');
  console.log('   een dag met één misser tussen zeven goede: doos ' + r.echteDag.box);
  /* v23.225: hier stond `=== 3`, oftewel: die dag klimt gewoon. Dat was de andere kant van
     hetzelfde gat. Een dag waarin je het onderwerp een keer mist is geen dag waarop je bewezen
     hebt dat je het kunt, en de datum alleen terugtrekken deed net alsof dat wel zo was. */
  ok(r.echteDag.box === 0,
    'zeven goede antwoorden met één misser ertussen leveren geen promotie op (doos ' + r.echteDag.box + ')');
  ok(r.echteDag.due === r.morgen, 'en het onderwerp komt morgen terug');

  console.log('\n-- 2. de dagrem: vijf goede antwoorden klimmen één doos --');
  ok(r.vijfGoed.box === 2, 'vijf goede antwoorden klimmen één doos, niet vijf (' + r.vijfGoed.box + ')');
  ok(r.vijfGoed.goed === 5, 'de teller loopt wel gewoon door (' + r.vijfGoed.goed + ')');

  console.log('\n-- 3. het controlegeval: de reset is er nog --');
  ok(r.fouteStart.box === 0, 'een fout eerste antwoord gaat van doos 4 naar 0 (' + r.fouteStart.box + ')');
  ok(r.foutMetGoedErna.box === 0,
    'een fout eerste antwoord gaat helemaal terug naar 0, ook met goede antwoorden erna (' + r.foutMetGoedErna.box + ')');
  ok(r.foutMetGoedErna.due === r.morgen, 'en komt morgen terug');

  console.log('\n-- 4. een misser later op de dag haalt de promotie weg --');
  console.log('   met misser: doos ' + r.laatFout.box + ' due ' + r.laatFout.due +
    ' · zonder: doos ' + r.zonderFout.box + ' due ' + r.zonderFout.due);
  ok(r.laatFout.box < r.zonderFout.box,
    'een misser na een goed antwoord laat de doos niet staan maar haalt de promotie weg ('
      + r.laatFout.box + ' tegen ' + r.zonderFout.box + ')');
  ok(r.laatFout.due === r.morgen, 'maar je ziet het morgen terug in plaats van over dagen');
  ok(r.zonderFout.due !== r.morgen, 'terwijl een dag zonder missers zijn volle wachttijd houdt (' + r.zonderFout.due + ')');

  console.log('\n-- 5. hetzelfde onderwerp niet twee keer in één les --');
  console.log('   ' + JSON.stringify(r.lijst));
  ok(!r.dubbel, 'geen enkel onderwerp staat er twee keer in (' + r.kaalLijst.join(', ') + ')');
  ok(r.lijst.length >= 1, 'en er staat wel iets in, dus dit meet geen lege lijst');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
