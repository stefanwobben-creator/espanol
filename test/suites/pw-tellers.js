// pw-tellers.js (14 aug, v23.94) — vertellen de tellers de waarheid?
//
// WAAROM DIT ER IS
//
// Vijf punten uit de doorlichting van 14 augustus, allemaal van het type "de app zegt iets anders
// dan er gebeurt". Geen van vijven gaf een foutmelding; ze gaven een verkeerd getal, en dat is erger,
// want een verkeerd getal geloof je.
//
//   3.  De dagportie gaf één nieuw woord per dag zodra je lespad op was, terwijl de instelling er
//       twintig belooft. Stefan: 814 woorden geleerd, nul dagen voorraad, één woord per dag. Dat is
//       de reden dat hij geen voortgang voelde: die was er niet.
//   6.  Een fout in S.errors werd nooit afgebouwd. Eén typefout zette een zin voorgoed in tegelmodus
//       en liet hem 40 procent van de tijd terugkomen.
//   7.  Keurde het taalmodel je variant goed, dan bleef de fout van drie regels eerder staan. Je
//       kreeg punten én een strafregistratie voor hetzelfde antwoord.
//   10. Het chipje "nieuwe woorden" telde met drie functies tegelijk: teller, noemer en maximum
//       kwamen alle drie ergens anders vandaan.
//   11. voortgangTellers() telde de rijen die niveauClaim() neerzet als "ooit geoefend".
//
// DE CONTROLEGEVALLEN
//
// Elk van deze reparaties is triviaal groen te krijgen door hem te ver door te voeren: fouten die
// altijd meteen verdwijnen, een portie die alles uitdeelt, een teller die niets meer telt. Daarom
// staat er bij elke meting ook een geval dat het tegenovergestelde moet doen.
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
    const u = {};
    S.xp = S.xp || {}; S.newIntro = S.newIntro || {}; S.errors = S.errors || {};

    // --- punt 6: drie goede beurten wissen de fout, twee niet ---
    logError('s1', 'zin', 'les1', 'iets fouts');
    u.naFout = !!S.errors['zin:s1'];
    foutGoedeBeurt('s1', 'zin'); foutGoedeBeurt('s1', 'zin');
    u.naTwee = !!S.errors['zin:s1'];
    foutGoedeBeurt('s1', 'zin');
    u.naDrie = !!S.errors['zin:s1'];

    // controlegeval: een nieuwe fout zet de teller terug op nul, dus twee goede beurten
    // daarna mogen hem NIET wissen
    logError('s2', 'zin', 'les1', 'x'); foutGoedeBeurt('s2', 'zin'); foutGoedeBeurt('s2', 'zin');
    logError('s2', 'zin', 'les1', 'x'); foutGoedeBeurt('s2', 'zin'); foutGoedeBeurt('s2', 'zin');
    u.resetBlijft = !!S.errors['zin:s2'];

    // --- punt 7: een goedgekeurde variant wist de fout helemaal ---
    logError('s3', 'zin', 'les1', 'x');
    foutWeg('s3', 'zin');
    u.aiWist = !S.errors['zin:s3'];

    // --- punt 11: een geclaimde rij is geen geoefend woord ---
    const bewaard = S.srs;
    S.srs = { w1: { box: 3, due: today(), claim: 1 } };
    u.claimTeltNiet = voortgangTellers().geoefend;
    S.srs.w1.n = 1;                       // controlegeval: eenmaal echt gehad, dan telt hij wel
    u.claimNaGebruik = voortgangTellers().geoefend;
    S.srs = bewaard;

    // --- punt 3: de dagportie vult aan tot je dagbudget ---
    S.srs = {}; S.newIntro[today()] = 0; S.doelMin = 30; S.tempo = null;
    u.belooft = nieuwPerDag();
    const echtePoort = window.poortRang, echteLes = window.lessonUnlocked;
    window.poortRang = function () { return 0; };      // alles buiten de poort, zoals bij een af lespad
    window.lessonUnlocked = function () { return false; };
    u.levert = dagPortie().nieuw.length;
    window.poortRang = echtePoort; window.lessonUnlocked = echteLes;
    S.srs = bewaard;

    return u;
  });

  console.log('\n-- een fout mag slijten, maar niet te snel --');
  ok(r.naFout === true, 'een fout wordt genoteerd');
  ok(r.naTwee === true, 'na twee goede beurten staat hij er nog');
  ok(r.naDrie === false, 'na drie goede beurten is hij weg');
  ok(r.resetBlijft === true, 'een nieuwe fout zet de teller terug, dus twee beurten wissen hem niet');

  console.log('\n-- een goedgekeurde variant was geen fout --');
  ok(r.aiWist === true, 'keurt het taalmodel je variant goed, dan verdwijnt de foutregistratie');

  console.log('\n-- de teller telt wat je deed, niet wat je claimde --');
  ok(r.claimTeltNiet === 0, 'een geclaimde rij telt niet als geoefend (nu: ' + r.claimTeltNiet + ')');
  ok(r.claimNaGebruik === 1, 'zodra je hem echt een keer had, telt hij wel (nu: ' + r.claimNaGebruik + ')');

  console.log('\n-- de dagportie houdt zijn belofte --');
  // Dit is het geval van Stefan: lespad af, dus alles wat er nog is ligt buiten de poort.
  // Vóór v23.94 leverde dit precies één woord per dag.
  ok(r.levert === r.belooft,
    'met een af lespad levert de portie nog steeds ' + r.belooft + ' nieuwe woorden (nu: ' + r.levert + ')');
  ok(r.belooft > 1, 'en die belofte is meer dan één (nu: ' + r.belooft + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
