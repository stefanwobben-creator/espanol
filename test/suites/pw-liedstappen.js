// pw-liedstappen.js (20 aug, v23.149) — eerst luisteren, dan pas meezingen
//
// WAAROM DIT ER IS
//
// Stefan: "hoe ga je me helpen met het liedje. Alleen het refrein. Meezingen of eerst alleen
// luisteren?"
//
// Meezingen met woorden die je niet begrijpt is een uitspraakoefening en geen taaloefening: je maakt
// klanken na zonder betekenis. Andersom werkt wel. Dus: luisteren, dan de betekenis, dan meezingen.
//
// Het liedblok was één pagina met alles er tegelijk op: video, zeven uitdrukkingen mét vertaling en
// uitleg, en drie vragen. Wie dat opent leest, en luistert niet.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DRIE STAPPEN, IN DEZE VOLGORDE. Luisteren, de woorden erbij, meezingen.
//   2. IN STAP 1 STAAT DE VERTALING ER NIET. Dat is het hele punt: staat de goede er in het
//      Nederlands naast, dan is "welke van deze drie hoor je" geen luistervraag meer.
//   3. DE AFLEIDERS ZIJN ECHT. Ze komen uit andere liedjes, niet uit een verzinsel: even echt, even
//      lang, even moeilijk. Anders gaat de vraag over welke er het gekst uitziet.
//   4. EN ZE ZIJN VAST. Twee keer dezelfde vraag geeft dezelfde keuzes, anders kun je gokken tot je
//      je eigen antwoord ziet veranderen.
//   5. DE OOGST KOMT PAS AAN HET EIND BIJ JE WOORDEN. Niet in stap 1, want dan heb je ze niet gehad.
//   6. GEEN UITDRUKKING LANGER DAN VIJF WOORDEN. Stefans grens.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door in stap 1 helemaal niets te tonen: dan klopt punt 2 en is er
// geen oefening. Daarom staat ertegenover dat er in stap 1 wél keuzes staan en dat het Spaans van de
// goede optie er echt bij hoort.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwLs' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl'; S.musKlaar = {}; S.dagen = { count: 6 };
    const tekst = () => document.getElementById('songView').textContent.replace(/\s+/g, ' ');

    // ---- 6. geen uitdrukking langer dan vijf woorden ----
    uit.max = MUS_MAX_WOORDEN;
    let langste = 0, teLang = 0, totaal = 0;
    SONGS.forEach(function (s) {
      (s.oogst || []).forEach(function (o) {
        totaal++;
        const n = musPlat(o.es).split(' ').filter(Boolean).length;
        if (n > langste) langste = n;
        if (musTeLang(o.es)) teLang++;
      });
    });
    uit.langste = langste; uit.totaalOogst = totaal; uit.teLang = teLang;
    // en de grens houdt echt tegen, ook als er morgen iets langers bij komt
    uit.langDoel = musOogstDoel({ es: 'una frase mucho mas larga que esto', nl: 'test' });
    uit.kortDoel = !!musOogstDoel({ es: 'te bloqueo', nl: 'ik blokkeer je' });

    // ---- 1 en 2. stap 1 is luisteren, zonder vertaling ----
    const sg = musVanDag();
    uit.titel = sg.titel;
    show('musica', true);
    openSong(sg);                       // verse opening: begint bij stap 1
    uit.stap1 = musStap;
    const t1 = tekst();
    uit.t1Kop = /Stap 1\/3/.test(t1);
    uit.t1Vraag = /hoor je in het lied/.test(t1);
    const rij = musHoorRij(sg);
    uit.hoorN = rij.length;
    uit.optiesN = rij.length ? rij[0].opties.length : 0;
    uit.t1Opties = rij.length ? rij[0].opties.every(function (o) { return t1.indexOf(o) !== -1; }) : false;
    // de vertalingen van dit lied horen er in stap 1 niet te staan. Gemeten buiten de vaste
    // stapkop: die instructiezin is gewone Nederlandse lopende tekst ("je hoeft alleen te horen
    // wat er staat") en botste op 26 aug met de oogst-vertaling "alleen" van No Me Dejes Solo —
    // een dagafhankelijke valse rode, want welk lied aan de beurt is rouleert per dag.
    const t1Kaal = (function () {
      const k = document.getElementById('songView').cloneNode(true);
      k.querySelectorAll('.kicker').forEach(function (kick) {
        if (/Stap 1\/3/.test(kick.textContent) && kick.closest('.card')) kick.closest('.card').remove();
      });
      return k.textContent.replace(/\s+/g, ' ');
    })();
    uit.t1Vertaling = (sg.oogst || []).filter(function (o) { return t1Kaal.indexOf(o.nl) !== -1; }).length;
    uit.t1Uitleg = (sg.oogst || []).filter(function (o) { return o.u && t1Kaal.indexOf(o.u) !== -1; }).length;

    // ---- 3. de afleiders zijn echt ----
    const eigenEs = (sg.oogst || []).map(function (o) { return o.es; });
    const vreemd = rij.length ? rij[0].opties.filter(function (o) { return eigenEs.indexOf(o) === -1; }) : [];
    const alleAndere = [];
    SONGS.forEach(function (s) { if (s.id !== sg.id) (s.oogst || []).forEach(function (o) { alleAndere.push(o.es); }); });
    uit.afleidersEcht = vreemd.length > 0 && vreemd.every(function (o) { return alleAndere.indexOf(o) !== -1; });
    uit.afleidersN = vreemd.length;

    // ---- 4. en ze zijn vast ----
    uit.vast = JSON.stringify(musHoorRij(sg)) === JSON.stringify(musHoorRij(sg));

    // ---- 5. de oogst komt pas aan het eind ----
    uit.oogstNaStap1 = musOogstOpen(sg).length;
    musStap = 2; openSong(sg, true);
    const t2 = tekst();
    uit.t2Kop = /Stap 2\/3/.test(t2);
    uit.t2Vertaling = (sg.oogst || []).filter(function (o) { return t2.indexOf(o.nl) !== -1; }).length;
    uit.t2Uitleg = (sg.oogst || []).filter(function (o) { return o.u && t2.indexOf(o.u) !== -1; }).length;
    uit.t2Quiz = !!document.getElementById('songQuiz');
    uit.t2Oogstknop = !!document.getElementById('btnMusOogst');

    musStap = 3; openSong(sg, true);
    const t3 = tekst();
    uit.t3Kop = /Stap 3\/3/.test(t3);
    uit.t3Zing = /zing deze stukjes mee/i.test(t3);
    uit.t3Quiz = !!document.getElementById('songQuiz');
    uit.t3Oogstknop = !!document.getElementById('btnMusOogst');
    uit.t3Brokjes = (sg.oogst || []).every(function (o) { return t3.indexOf(o.es) !== -1; });

    S.musKlaar = {};
    return uit;
  });

  console.log('\n-- 6. geen uitdrukking langer dan vijf woorden --');
  console.log('   ' + r.totaalOogst + ' uitdrukkingen, langste ' + r.langste + ' woorden');
  ok(r.langste <= r.max, 'niets in de app is langer dan ' + r.max + ' woorden (langste nu: ' + r.langste + ')');
  ok(r.teLang === 0, 'en dus valt er ook niets af (' + r.teLang + ')');
  ok(r.langDoel === null, 'het controlegeval: iets van zeven woorden komt er niet in');
  ok(r.kortDoel, 'en iets korts wel');

  console.log('\n-- 1 en 2. stap 1 is luisteren, zonder vertaling --');
  console.log('   ' + r.titel + ' · ' + r.hoorN + ' vragen van ' + r.optiesN + ' keuzes');
  ok(r.stap1 === 1, 'een verse opening begint bij stap 1 (nu: ' + r.stap1 + ')');
  ok(r.t1Kop, 'het scherm zegt welke stap dit is');
  ok(r.t1Vraag, 'met de vraag welke je hoort');
  ok(r.hoorN >= 2, 'er zijn meerdere luistervragen (' + r.hoorN + ')');
  ok(r.optiesN >= 2, 'met meerdere keuzes (' + r.optiesN + ')');
  ok(r.t1Opties, 'en die keuzes staan echt op het scherm');
  ok(r.t1Vertaling === 0, 'geen enkele Nederlandse vertaling in stap 1 (' + r.t1Vertaling + ')');
  ok(r.t1Uitleg === 0, 'en geen uitleg (' + r.t1Uitleg + ')');

  console.log('\n-- 3 en 4. de afleiders zijn echt, en vast --');
  ok(r.afleidersN >= 1, 'er staan afleiders bij (' + r.afleidersN + ')');
  ok(r.afleidersEcht, 'en die komen uit andere liedjes, niet uit een verzinsel');
  ok(r.vast, 'twee keer vragen geeft dezelfde keuzes');

  console.log('\n-- stap 2: de woorden erbij --');
  ok(r.t2Kop, 'het scherm zegt stap 2');
  ok(r.t2Vertaling >= 1, 'nu staan de vertalingen er wel (' + r.t2Vertaling + ')');
  ok(r.t2Uitleg >= 1, 'en de uitleg (' + r.t2Uitleg + ')');
  ok(!r.t2Quiz, 'de vragen komen nog niet');

  console.log('\n-- stap 3: meezingen --');
  ok(r.t3Kop, 'het scherm zegt stap 3');
  ok(r.t3Zing, 'met de opdracht om mee te zingen');
  ok(r.t3Brokjes, 'en de brokjes staan ernaast om mee te zingen');
  ok(r.t3Quiz, 'nu pas komen de vragen');

  console.log('\n-- 5. de oogst komt pas aan het eind bij je woorden --');
  ok(r.oogstNaStap1 > 0, 'na stap 1 staat er nog niets bij je woorden (' + r.oogstNaStap1 + ' open)');
  ok(!r.t2Oogstknop, 'in stap 2 staat de knop er nog niet');
  ok(r.t3Oogstknop, 'in stap 3 wel');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
