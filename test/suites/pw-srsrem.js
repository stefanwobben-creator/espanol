// pw-srsrem.js (14 aug, v23.92) — mag een goedkope handeling een dure staat veranderen?
//
// WAAROM DIT ER IS
//
// Drie keer dezelfde fout, op drie plekken, allemaal ontdekt op 14 augustus:
//
//   1. spelGetyptBij() (tot v23.147 avtSrsBij) zette `st.k = 1` bij élk goed antwoord in Aventura, ook bij een klik op een
//      meerkeuze-optie en bij het galgje. `k` is definitief: wCheckNodig() slaat de Laatste stap
//      voorgoed over zodra hij bestaat, en answerWord mag er de laatste doos mee halen op een
//      zelfbeoordeling. Eén klik zette dus de hele bewijsvoering van v20.0 uit voor dat woord.
//      Stefan heeft die Laatste stap in 814 woorden nooit gezien.
//   2. spelSrsBij() en spelGetyptBij() keken niet of een woord vandaag aan de beurt was. Drie spellen
//      achter elkaar brachten hetzelfde woord van doos 0 naar doos 3 in tien minuten.
//   3. gramBij() verhoogde de doos bij elk goed antwoord: vijf goede antwoorden in één sessie
//      zetten een onderwerp van 0 naar 5, en dan zie je het 55 dagen niet meer.
//
// Alle drie zijn onzichtbaar vanaf de buitenkant. Je ziet geen foutmelding, geen rood scherm; je
// ziet alleen een balk die te snel vol loopt en een app die je iets niet meer vraagt. Precies het
// soort fout dat een half jaar blijft zitten. Vandaar deze suite.
//
// HET CONTROLEGEVAL
//
// Een dagrem is triviaal te "halen" door hem overal te laten blokkeren. Dan meet je niets meer en
// gaat de suite groen terwijl de app kapot is. Daarom staat er een controle in die MOET stijgen:
// hetzelfde woord met een oude `bd` hoort morgen wél een doos op te schuiven. Zakt die mee, dan is
// niet de app stuk maar deze meting.
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
  await page.waitForTimeout(1500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.xp = S.xp || {}; S.newIntro = S.newIntro || {}; S.srs = S.srs || {};
    const w1 = WORDS[0], w2 = WORDS[1], w3 = WORDS[2];

    // een klik uit vier is geen bewijs
    S.srs[w1.id] = { box: 1, due: today() };
    spelGetyptBij(w1, true, false);
    uit.klikZetK = !!S.srs[w1.id].k;

    // intikken wel
    S.srs[w2.id] = { box: 1, due: today() };
    spelGetyptBij(w2, true, true);
    uit.typZetK = !!S.srs[w2.id].k;

    // de dagrem: tweede keer op dezelfde dag schuift niet op
    const voor = S.srs[w2.id].box;
    spelGetyptBij(w2, true, true);
    uit.tweedeKeerStil = S.srs[w2.id].box === voor;

    // HET CONTROLEGEVAL: met een oude dag hoort hij wél op te schuiven.
    // v23.132: hoevéél dozen hij opschuift is niet aan deze suite. Een woord dat je nog nooit fout
    // had schuift sinds die ronde twee dozen tegelijk op (srsStap). De rem hier gaat over de dag,
    // niet over de stapgrootte; die staat in pw-ladder.js. Deze regel eiste `voor + 1` en werd
    // daardoor rood op een gedragsverandering die hij niet bewaakt.
    S.srs[w2.id].bd = '2000-01-01';
    spelGetyptBij(w2, true, true);
    uit.controleStijgt = S.srs[w2.id].box > voor;

    // spelSrsBij levert de tweede keer op dezelfde dag niets meer op
    S.srs[w3.id] = { box: 0, due: today() };
    uit.spelEerste = spelSrsBij(w3.id) === true;
    uit.spelTweede = spelSrsBij(w3.id) === false;
    S.srs[w3.id].bd = '2000-01-01';
    uit.spelControle = spelSrsBij(w3.id) === true;

    // grammatica: vijf goede antwoorden in één sessie is hoogstens één doos
    S.gram = {};
    for (let i = 0; i < 5; i++) gramBij('serestar', true);
    uit.gramBox = (S.gram.serestar || {}).box;
    uit.gramGoed = (S.gram.serestar || {}).goed;
    S.gram.serestar.bd = '2000-01-01';
    gramBij('serestar', true);
    uit.gramControle = (S.gram.serestar || {}).box === 2;

    // en wat een taalmodel terugstuurt is tekst, geen opmaak
    uit.escape = typeof veiligHtml === 'function' ? veiligHtml('<b>x</b>') : 'ONTBREEKT';
    return uit;
  });

  console.log('\n-- alleen intikken telt als bewijs --');
  ok(r.klikZetK === false, 'een klik uit vier zet st.k niet');
  ok(r.typZetK === true, 'het woord intikken zet st.k wel');

  console.log('\n-- hoogstens een doos per dag --');
  ok(r.tweedeKeerStil, 'een tweede goede beurt op dezelfde dag schuift het woord niet verder op');
  ok(r.spelEerste, 'het eerste spel van de dag laat het woord wel opschuiven');
  ok(r.spelTweede, 'het tweede spel van dezelfde dag levert geen extra doos op');
  ok(r.gramBox === 1, 'vijf goede grammatica-antwoorden in een sessie geven een doos, geen vijf (nu: ' + r.gramBox + ')');
  ok(r.gramGoed === 5, 'het aantal goede antwoorden loopt wel gewoon door (nu: ' + r.gramGoed + ')');

  console.log('\n-- de controlegevallen: morgen moet het wel --');
  // Zakken deze mee, dan blokkeert de rem alles en meet de suite hierboven niets.
  ok(r.controleStijgt, 'hetzelfde woord schuift op een andere dag wel op');
  ok(r.spelControle, 'hetzelfde spel schuift op een andere dag wel op');
  ok(r.gramControle, 'hetzelfde onderwerp schuift op een andere dag wel op');

  console.log('\n-- en de uitvoer van het taalmodel --');
  ok(r.escape === '&lt;b&gt;x&lt;/b&gt;', 'veiligHtml maakt van opmaakcode gewone tekst (nu: ' + r.escape + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
