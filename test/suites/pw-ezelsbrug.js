// pw-ezelsbrug.js (21 aug, v23.158) — gebeurt er iets als je het fout doet?
//
// WAAROM DIT ER IS
//
// Stefan, 21 aug: "ik mis nog vaak uitleg of als ik een foutmaak, waarom ik het fout maak en dan
// een ezelsbrug of andere hulp. De hele grammatica sectie voelt niet logisch. trouwens alsof de
// toetsjes te moeilijk zijn of niet stap voor stap aansluiten bij wat je leerde."
//
// Gemeten voordat deze ronde begon: bij een fout kreeg je het veld w, en dat legt uit waarom het
// JUISTE antwoord goed is. Over jouw antwoord stond er niets. Een ezelsbrug bestond nergens in de
// 23 concepten. En stap 1 begon met twee vragen zonder dat er één woord Spaans aan vooraf ging: de
// regel zelf zat achteraan in stap 3, dichtgeklapt onder "De hele regel". Je kon dus niet stap voor
// stap aansluiten bij wat je leerde, want je leerde niets voordat de eerste vraag kwam.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE HULP IS ER, EN HIJ IS COMPLEET. Voor alle 23 concepten, in beide talen. Dit is het soort
//      content dat makkelijk half wordt aangevuld als er morgen een concept bij komt.
//   2. DE REGEL STAAT VOOR DE EERSTE VRAAG. Niet erna, niet dichtgeklapt.
//   3. BIJ EEN FOUT KRIJG JE DE DIAGNOSE EN DE BRUG. Dit is de vraag die Stefan stelde.
//   4. EN BIJ EEN GOED ANTWOORD NIET. Het controlegeval. Hulp die er altijd staat is geen hulp maar
//      behang, en dan lees je hem ook niet op het moment dat je hem nodig hebt.
//   5. DE FOUT KOMT TERUG. Eén keer, aan het eind van de stap, met andere volgorde.
//   6. MAAR HIJ TELT NIET MEE. Anders is fout antwoorden een manier om taco's te halen en gaat
//      "2 van de 2 goed" opeens over vier vragen.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwEz' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    // ---- 1. de hulp is er, voor alle concepten, in beide talen ----
    uit.concepten = GC_CONCEPTEN.length;
    uit.zonderHulp = GC_CONCEPTEN.filter(function (c) { return !gcHulp(c.id); }).map(function (c) { return c.id; });
    uit.halfHulp = GC_CONCEPTEN.filter(function (c) {
      const h = gcHulp(c.id);
      if (!h) return false;
      return ['kern', 'brug', 'mis'].some(function (v) {
        return !h[v] || !h[v + 'En'] || String(h[v]).length < 40 || String(h[v + 'En']).length < 40;
      });
    }).map(function (c) { return c.id; });
    // de drie velden moeten ook echt drie verschillende dingen zeggen
    uit.kopieHulp = GC_CONCEPTEN.filter(function (c) {
      const h = gcHulp(c.id);
      return h && (h.kern === h.brug || h.brug === h.mis || h.kern === h.mis);
    }).map(function (c) { return c.id; });

    // ---- 2. de regel staat vóór de eerste vraag ----
    const o = gcOnderwerp('concept-zapato');
    uit.stapHeeftKern = !!(o.stappen[0] && o.stappen[0].kern && o.stappen[0].hulp);
    uit.alleStappenHulp = o.stappen.every(function (s) { return !!s.hulp; });
    // en hij krijgt nog steeds geen eigen scherm (v23.154)
    uit.geenEigenScherm = gwStapHeeftTekst(o, 0) === false;

    /* gwStart roept gcVernieuw aan en bouwt het onderwerp opnieuw op, met een nieuwe schudding.
       Het object hierboven is daarna oud nieuws: de g van vraag 0 klopt niet meer. Dat kostte deze
       suite één rode run, en het is precies de bedoeling dat je vragen ná de start ophaalt. */
    gwStart('concept-zapato', 0);
    const scherm1 = renderGramWiz();
    uit.eersteScherm = {
      kern: scherm1.indexOf('gwkern') !== -1,
      regelErin: scherm1.indexOf('klemtoon') !== -1,
      brugErin: /Ezelsbruggetje/.test(scherm1) && scherm1.indexOf('schoen') !== -1,
      // de vraag staat op hetzelfde scherm: het is geen tussenpagina
      vraagErin: scherm1.indexOf('gwOpties') !== -1
    };

    // ---- 4. het controlegeval: bij een goed antwoord geen diagnose ----
    gwKies(gwVragen()[0].g);
    const naGoed = renderGramWiz();
    uit.naGoed = {
      mis: naGoed.indexOf('gwmis') !== -1,
      misgaat: /Waar het meestal misgaat/.test(naGoed),
      correcto: /Correcto/.test(naGoed)
    };
    uit.goedTeller = gwSess.goed;
    uit.extraNaGoed = (gwSess.extra || []).length;

    // ---- 3. bij een fout krijg je de diagnose en de brug ----
    gwVolgende();
    const q2 = gwVragen()[gwSess.vraag];
    const xpVoor = S.xp[today()] || 0;
    gwKies(q2.g === 0 ? 1 : 0);
    const naFout = renderGramWiz();
    uit.naFout = {
      mis: naFout.indexOf('gwmis') !== -1,
      misgaat: /Waar het meestal misgaat/.test(naFout),
      brug: /Ezelsbruggetje/.test(naFout),
      // de oude uitleg blijft er ook staan: waarom het juiste antwoord goed is
      waarom: naFout.indexOf(gwWaarom(q2).slice(0, 25)) !== -1,
      diagnose: naFout.indexOf('puedemos') !== -1
    };

    // ---- 5. de fout komt terug ----
    uit.extraNaFout = (gwSess.extra || []).length;
    uit.basisN = gwBasisAantal();
    uit.totaalNu = gwVragen().length;
    gwVolgende();
    uit.inCorrectie = gwInCorrectie();
    const corrScherm = renderGramWiz();
    uit.corrScherm = {
      kicker: /Nog een keer/.test(corrScherm),
      uitleg: /Dit had je net fout/.test(corrScherm),
      zelfdeVraag: corrScherm.indexOf(gwVraagTekst(q2).slice(0, 20)) !== -1
    };

    // ---- 6. maar hij telt niet mee ----
    const corrQ = gwVragen()[gwSess.vraag];
    const goedVoor = gwSess.goed, foutVoor = gwSess.fout;
    const xpVoorCorr = S.xp[today()] || 0;
    const boxVoor = JSON.stringify(gramLees('zapato'));
    gwKies(corrQ.g);
    uit.correctie = {
      goedGelijk: gwSess.goed === goedVoor,
      foutGelijk: gwSess.fout === foutVoor,
      geenXp: (S.xp[today()] || 0) === xpVoorCorr,
      geenDoos: JSON.stringify(gramLees('zapato')) === boxVoor,
      geteld: gwSess.correctieGoed
    };
    // en een tweede fout in de correctie laat hem niet nóg eens terugkomen
    const nExtra = (gwSess.extra || []).length;
    uit.geenLus = nExtra === uit.extraNaFout;

    gwVolgende();
    const klaar = renderGramWiz();
    uit.stapklaar = {
      score: /van de/.test(klaar),
      // de correctie staat er apart bij, niet in het cijfer
      corrGenoemd: /verbeterd/.test(klaar),
      basisScore: klaar.indexOf(gwSess.goed + ' van de ' + uit.basisN) !== -1
    };
    uit.xpTotaal = (S.xp[today()] || 0) - xpVoor;

    // ---- en het werkt ook in het Engels ----
    S.lang = 'en';
    gwStart('concept-gustar', 0);
    const en = renderGramWiz();
    uit.engels = { kern: en.indexOf('gwkern') !== -1, hook: /Memory hook/.test(en), nl: /Ezelsbruggetje/.test(en) };
    S.lang = 'nl';
    gwSluit();
    return uit;
  });

  console.log('\n-- 1. de hulp is er, en compleet --');
  console.log('   ' + r.concepten + ' concepten');
  ok(r.zonderHulp.length === 0, 'elk concept heeft een kern, een ezelsbrug en een diagnose (' + (r.zonderHulp.join(',') || 'alle') + ')');
  ok(r.halfHulp.length === 0, 'en alle drie in beide talen, met echte tekst erin (' + (r.halfHulp.join(',') || 'alle') + ')');
  ok(r.kopieHulp.length === 0, 'de drie velden zeggen ook drie verschillende dingen (' + (r.kopieHulp.join(',') || 'alle') + ')');

  console.log('\n-- 2. de regel staat vóór de eerste vraag --');
  ok(r.stapHeeftKern, 'stap 1 draagt de kern van het onderwerp');
  ok(r.alleStappenHulp, 'en elke stap draagt de hulp, zodat de brug ook later beschikbaar is');
  ok(r.geenEigenScherm, 'zonder dat het een eigen tussenscherm wordt (v23.154 blijft staan)');
  ok(r.eersteScherm.kern, 'op het scherm staat het kernblok');
  ok(r.eersteScherm.regelErin, 'met de regel zelf erin');
  ok(r.eersteScherm.brugErin, 'en het ezelsbruggetje eronder');
  ok(r.eersteScherm.vraagErin, 'en de vraag staat op datzelfde scherm, dus je leest hem terwijl je hem gebruikt');

  console.log('\n-- 3. bij een fout krijg je de diagnose en de brug --');
  ok(r.naFout.mis && r.naFout.misgaat, 'er staat waar het meestal misgaat');
  ok(r.naFout.diagnose, 'en dat is de echte misvatting van dit onderwerp (puedemos)');
  ok(r.naFout.brug, 'met het ezelsbruggetje erbij');
  ok(r.naFout.waarom, 'en de uitleg waarom het juiste antwoord goed is blijft ook staan');

  console.log('\n-- 4. het controlegeval: bij een goed antwoord niet --');
  ok(r.naGoed.correcto, 'een goed antwoord krijgt gewoon ¡Correcto!');
  ok(!r.naGoed.mis && !r.naGoed.misgaat, 'en geen diagnose: hulp die er altijd staat is behang');
  ok(r.extraNaGoed === 0, 'en niets om te herhalen');

  console.log('\n-- 5. de fout komt terug --');
  ok(r.extraNaFout === 1, 'de fout gaat op de stapel voor het eind van de stap (' + r.extraNaFout + ')');
  ok(r.totaalNu === r.basisN + 1, 'de stap heeft er één vraag bij (' + r.basisN + ' + ' + r.extraNaFout + ')');
  ok(r.inCorrectie, 'en na de laatste gewone vraag zit je in de correctieronde');
  ok(r.corrScherm.kicker, 'die zich ook zo noemt ("Nog een keer")');
  ok(r.corrScherm.uitleg, 'met de reden erbij');
  ok(r.corrScherm.zelfdeVraag, 'en het is dezelfde vraag');

  console.log('\n-- 6. maar hij telt niet mee --');
  ok(r.correctie.goedGelijk && r.correctie.foutGelijk, 'je score verandert niet');
  ok(r.correctie.geenXp, 'er komen geen taco\'s bij: fout antwoorden mag geen verdienmodel worden');
  ok(r.correctie.geenDoos, 'en je doosje blijft staan');
  ok(r.correctie.geteld === 1, 'maar het wordt wel geteld (' + r.correctie.geteld + ')');
  ok(r.geenLus, 'en een tweede fout laat hem niet nóg eens terugkomen: geen lus');
  ok(r.stapklaar.basisScore, 'het eindcijfer gaat over de gewone vragen (' + r.basisN + ')');
  ok(r.stapklaar.corrGenoemd, 'en de correctie staat er apart bij genoemd');

  console.log('\n-- en in het Engels --');
  ok(r.engels.kern && r.engels.hook && !r.engels.nl, 'het Engelse profiel krijgt Memory hook, niet Ezelsbruggetje');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
