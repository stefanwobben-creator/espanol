// pw-vormenblok.js (21 aug, v23.160) — oefen je ooit een werkwoordsvorm zonder ernaar te zoeken?
//
// WAAROM DIT ER IS
//
// Stefan, 21 aug: "hoe zijn de vervoegingen, ik moet dat veel oefenen."
//
// Ik ging een rijtjesoefening bouwen. Die staat er al, in drie soorten: de Conjugador (13 fasen),
// De les (6 stappen per rij, per tijd en per patroon) en De route (twee paden van 9 stappen, met
// "Het imperfecto in je vingers" erin). Plus omkeer, zin, tijdvorm en brok.
//
// Wat de dagles daarvan gebruikte, gemeten op een profiel met alle lessen af:
//
//     woorden · grammatica · toetsje · input · produceren
//
// Nul. Geen enkel blok raakte een werkwoordsvorm aan. Al die machinerie hing aan zes tegels op de
// Grammatica-tab en werd door niets gepland. Wie er niet uit zichzelf heen klikte, oefende nooit
// een vorm. Het antwoord op "ik moet dat veel oefenen" was dus niet nog een oefening maar een plek
// in de dag.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET BLOK STAAT IN JE PLAN, VOORDAT JE BEGINT. Een blok dat halverwege opduikt is een
//      verrassing; een blok dat in het plan staat is een afspraak (v23.135).
//   2. OM DE DAG, EN NIET OP DE PRAATDAGEN. Anders groeit de dag op twee assen tegelijk.
//   3. HET IS ÉÉN STAP. Niet de hele les van zes stappen: dan is het geen dagles meer, en de
//      afstand tussen de stappen is hier juist het werk.
//   4. EN DIE STAP SCHUIFT OP. Morgen de volgende, niet elke dag opnieuw stap 1.
//   5. JE KOMT ERUIT. Het controlegeval: een blok dat je in een spel achterlaat zonder weg terug is
//      erger dan geen blok. Eén knop, en de les gaat verder.
//   6. EN PAUZEREN MAG. Hervatten zet je terug in je rijtje, niet in het keuzemenu van De les.
//   7. HET RIJTJE VOLGT JE FOUTEN (v23.161). Stefan, gevraagd waar het misgaat: "soms vorm vooral
//      bijv Indefinido en imperfecto maar ook het ophalen van de rijtjes en de onregematige."
//      Het blok liep de lijst van boven af en die begint bij het presente, dus hij kreeg elke
//      tweede dag een stap in de tijd waar hij geen werk had. S.errors weet allang waar het werk
//      ligt; die teller werd alleen door niemand gelezen.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwVb' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    S.lessons = S.lessons || {};
    (tLessons() || []).forEach(function (l) {
      S.lessons[l.id] = { done: true, woorden: true, zinnen: true, quiz: true, spiek: true };
    });

    // ---- 1 en 2. het blok staat in je plan, om de dag ----
    function planVoor(d) {
      S.dagen = { count: d }; dagPlanVerval();
      const p = dagPlan();
      return { stappen: p.stappen, min: p.min, blok: p.blokken.filter(function (b) { return b.stap === 'vormen'; })[0] || null,
               praat: (function () { try { return praatBeurt(); } catch (e) { return null; } })() };
    }
    uit.dagen = [8, 9, 10, 11].map(function (d) {
      const x = planVoor(d);
      return { d: d, vormen: x.stappen.indexOf('vormen') !== -1, praat: x.praat, min: x.min,
               wat: x.blok ? x.blok.wat : null, draad: x.blok ? x.blok.draad : null, naam: x.blok ? x.blok.naam : null };
    });
    // de eerste dag telt niet mee: een blok beloven aan iemand die nog nooit iets deed
    S.dagen = { count: 1 }; dagPlanVerval();
    uit.dag1 = dagPlan().stappen.indexOf('vormen') !== -1;
    /* De pariteit los van alle andere voorwaarden: op welke soort dag valt elk van de twee? */
    uit.pariteit = {
      vorm: (function () { S.dagen = { count: 10 }; return vormBeurt(); })(),
      praat: (function () { S.dagen = { count: 10 }; return (dagenTotaal() % 2) === 1; })()
    };

    // ---- 3, 4 en 5. door de les heen ----
    S.dagen = { count: 10 }; dagPlanVerval();
    uit.rij = vormRijVandaag();
    uit.stapVoor = vormStapVandaag(uit.rij);
    lesFlowStart();
    const gezien = [];
    for (let i = 0; i < 8 && lesFlow; i++) {
      gezien.push({ stap: lesFlow.stap, naam: lesFlowStapNaam(), num: lesFlowStapNum(), tot: lesFlowStapTotaal() });
      if (lesFlow.stap === 'vormen') break;
      lesFlow.quizzesTeDoen = []; lesFlow.vertalenTeGaan = 0;
      lesFlowVolgendeKern();
    }
    uit.flow = gezien;
    uit.bijVormen = {
      spel: lesFlow && lesFlow.gekozenSpel,
      view: funView,
      lesRij: lesSpel && lesSpel.rij,
      lesStap: lesSpel && lesSpel.stap,
      // en niet op het keuzescherm van De les: dat is een menu middenin een dagles
      keuzescherm: !!document.getElementById('lesKeuze')
    };
    renderFun();
    uit.scherm = (document.getElementById('funCard').textContent || '').replace(/\s+/g, ' ').slice(0, 120);
    // de strook boven je scherm noemt dit blok
    lesFrameSync();
    uit.frame = (document.getElementById('lesFrame').textContent || '').replace(/\s+/g, ' ').trim();

    // ---- 6. pauzeren en hervatten ----
    lesFlowBewaar();
    const bewaard = JSON.parse(JSON.stringify(S.lesFlowNu));
    uit.bewaardRij = bewaard.vormRij;
    lesFlow = null; lesSpel = null; funView = null;
    S.lesFlowNu = bewaard;
    lesFlowHervat();
    uit.naHervat = { stap: lesFlow && lesFlow.stap, rij: lesSpel && lesSpel.rij, stapN: lesSpel && lesSpel.stap,
                     view: funView, keuzescherm: (renderFun(), !!document.getElementById('lesKeuze')) };

    // ---- 5. je komt eruit, en de stap schuift op ----
    // de leesstappen (0 en 1) stellen geen vraag; loop door tot de eerste die dat wel doet
    let veilig = 0;
    while (lesSpel && lesSpel.stap < 2 && veilig++ < 5) {
      renderFun();
      const b = document.getElementById('btnLesVerder');
      if (!b) break;
      b.click();
    }
    uit.naLezen = lesSpel && lesSpel.stap;
    // de vragen goed beantwoorden tot de stap af is
    veilig = 0;
    while (lesSpel && lesSpel.i < lesOpgaven(lesSpel.stap) && veilig++ < 12) {
      const q = lesOpgaveNu();
      if (!q) break;
      lesAntwoord(conjVorm(q.v, q.p, lesSpel.t));
      lesSpel.i++; lesSpel.gekozen = null; lesSpel.opties = null;
    }
    renderFun();
    uit.eind = {
      /* v23.197: de Door-knop had een id en heeft nu een class, omdat vier schermen hem tekenden
         en getElementById() de eerste in de pagina gaf in plaats van die op je scherm. Zoek hem
         daarom binnen de kaart waar hij op staat, precies zoals de app het nu doet. */
      door: !!document.querySelector('#funCard .lesflow-door'),
      // in je dagles staat er geen "volgende stap": dat is morgen
      volgendeStap: !!document.getElementById('btnLesVerder'),
      opnieuw: !!document.getElementById('btnLesOpnieuw')
    };
    const stapVoorKlik = lesSpel && lesSpel.stap;
    const dk = document.querySelector('#funCard .lesflow-door');
    if (dk) dk.click();
    uit.naDoor = { stap: lesFlow && lesFlow.stap, lesSpel: !!lesSpel, stapMax: brokLees(lesId(uit.rij)).stapMax };
    uit.stapVoorKlik = stapVoorKlik;
    // en morgen sta je een stap verder
    uit.stapMorgen = vormStapVandaag(uit.rij);

    // ---- 7. het rijtje volgt je fouten (v23.161) ----
    lesFlow = null; lesSpel = null; funView = null; S.lesFlowNu = null;
    S.brok = {}; S.errors = {}; S.conjOpen = CONJ_FASES.length - 1;
    dagPlanVerval();
    uit.fout = { zonder: vormRijVandaag() };
    // fouten in het indefinido en het imperfecto, en eentje in het presente
    ['tener', 'hacer', 'ir', 'poder', 'decir'].forEach(function (inf) {
      const v = VERBOS.filter(function (w) { return w.inf === inf; })[0];
      [0, 2, 4].forEach(function (pp) { logError(conjErrKey(v, pp, 'indefinido'), 'conj', inf, 'x'); });
    });
    ['ser', 'ver'].forEach(function (inf) {
      const v = VERBOS.filter(function (w) { return w.inf === inf; })[0];
      [1, 3].forEach(function (pp) { logError(conjErrKey(v, pp, 'imperfecto'), 'conj', inf, 'x'); });
    });
    const hab = VERBOS.filter(function (w) { return w.inf === 'hablar'; })[0];
    logError(conjErrKey(hab, 0, 'presente'), 'conj', 'hablar', 'x');
    uit.fout.perTijd = vormFoutenPerTijd();
    dagPlanVerval();
    uit.fout.met = vormRijVandaag();
    uit.fout.wat = (dagPlan().blokken.filter(function (b) { return b.stap === 'vormen'; })[0] || {}).wat;
    /* Het controlegeval: is het indefinido af, dan hoort hij naar de volgende rij mét fouten te
       gaan en niet terug naar boven. Een lijst die van boven af loopt zou hier presente zeggen.

       v23.227: "het indefinido" is sinds die versie niet één rij meer maar zeven (de tijd plus zes
       patroonrijen), en die dragen allemaal t === 'indefinido'. Alleen de tijdrij afvinken laat de
       patroonrijen staan, en die winnen dan terecht met dezelfde vijftien fouten. Dus worden ze nu
       allemaal afgevinkt, en dat is meteen scherper: de vraag is of hij naar de volgende TIJD gaat
       als er in deze niets meer te doen is. */
    lesRijIds().forEach(function (id) {
      var r = null;
      try { r = lesRij(id); } catch (e) { r = null; }
      if (r && r.t === 'indefinido') S.brok[lesId(id)] = { stapMax: LES_STAPPEN.length - 1 };
    });
    dagPlanVerval();
    uit.fout.naAf = vormRijVandaag();
    S.errors = {}; S.brok = {};

    lesFlow = null; lesSpel = null; funView = null; S.lesFlowNu = null;
    return uit;
  });

  console.log('\n-- 1 en 2. het blok staat in je plan, om de dag --');
  r.dagen.forEach(function (d) {
    console.log('   dag ' + d.d + ': ' + (d.vormen ? 'vormen (' + d.wat + ')' : 'geen vormen') + ' · praten: ' + d.praat + ' · ' + d.min + ' min');
  });
  const even = r.dagen.filter(function (d) { return d.d % 2 === 0; });
  const oneven = r.dagen.filter(function (d) { return d.d % 2 === 1; });
  ok(even.every(function (d) { return d.vormen; }), 'op even dagen staat het vormenblok in het plan');
  ok(oneven.every(function (d) { return !d.vormen; }), 'op oneven dagen niet');
  /* Het gaat om de pariteit, niet om of er vandaag toevallig gepraat wordt: praatBeurt() vraagt
     daarnaast een vertaaltrede die dit proefprofiel niet heeft, dus die staat hier altijd op false.
     Wat bewaakt moet worden is dat de twee blokken elkaars dagen niet pakken. */
  ok(r.pariteit.vorm !== r.pariteit.praat,
    'en de twee blokken staan op elkaars tegendagen: de dag groeit op één as tegelijk (vormen op ' +
    (r.pariteit.vorm ? 'even' : 'oneven') + ', praten op ' + (r.pariteit.praat ? 'even' : 'oneven') + ')');
  ok(!r.dag1, 'het controlegeval: op je eerste dag beloven we dit niet');
  ok(even.every(function (d) { return !!d.wat && !!d.naam; }), 'het blok zegt in het plan welk rijtje en welke stap ("' + even[0].wat + '")');
  ok(even.every(function (d) { return d.draad === 'leren'; }), 'en het telt als de draad "leren" (' + even[0].draad + ')');

  console.log('\n-- 3. het staat op zijn plek in de les --');
  console.log('   ' + r.flow.map(function (g) { return g.num + '/' + g.tot + ' ' + g.naam; }).join(' → '));
  const v = r.flow[r.flow.length - 1];
  ok(v.stap === 'vormen', 'de les komt bij het vormenblok uit');
  ok(v.naam === 'Vormen', 'en de stap heeft een naam (' + v.naam + ')');
  ok(v.num === 3, 'hij staat na de grammatica en vóór het toetsje (stap ' + v.num + ' van ' + v.tot + ')');
  ok(r.frame.indexOf('Vormen') !== -1, 'de strook boven je scherm noemt hem ook ("' + r.frame + '")');
  ok(r.bijVormen.view === 'les' && r.bijVormen.spel === 'les', 'en je zit in De les, niet in een nieuw spel');
  ok(!r.bijVormen.keuzescherm, 'het controlegeval: geen keuzemenu middenin je dagles');
  ok(r.bijVormen.lesRij === r.rij, 'het rijtje is dat van vandaag (' + r.bijVormen.lesRij + ')');
  ok(r.bijVormen.lesStap === r.stapVoor, 'en je begint waar je gebleven was (stap ' + r.bijVormen.lesStap + ')');

  console.log('\n-- 5. je komt eruit, en de stap schuift op --');
  ok(r.eind.door, 'na de stap staat er één knop terug naar je les');
  ok(!r.eind.volgendeStap, 'en geen "volgende stap": die is morgen, dat is het hele idee');
  ok(r.naDoor.stap !== 'vormen', 'de knop brengt je verder in de les (' + r.naDoor.stap + ')');
  ok(!r.naDoor.lesSpel, 'en laat geen halve les achter');
  ok(r.naDoor.stapMax === r.stapVoorKlik, 'de gehaalde stap staat genoteerd (' + r.naDoor.stapMax + ')');
  ok(r.stapMorgen === r.stapVoorKlik + 1, 'dus morgen krijg je de volgende (' + r.stapVoorKlik + ' → ' + r.stapMorgen + ')');

  console.log('\n-- 6. pauzeren mag --');
  ok(r.bewaardRij === r.rij, 'het rijtje reist mee in wat er bewaard wordt');
  ok(r.naHervat.stap === 'vormen' && r.naHervat.view === 'les', 'hervatten zet je terug in het vormenblok');
  ok(r.naHervat.rij === r.rij && r.naHervat.stapN === r.stapVoor, 'bij hetzelfde rijtje en dezelfde stap');
  ok(!r.naHervat.keuzescherm, 'en niet in het keuzemenu van De les');

  console.log('\n-- 7. het rijtje volgt je fouten --');
  console.log('   openstaande fouten per tijd: ' + JSON.stringify(r.fout.perTijd));
  ok(r.fout.zonder === 'presente', 'zonder fouten begint het gewoon bovenaan (' + r.fout.zonder + ')');
  ok(r.fout.met === 'indefinido', 'met fouten in het indefinido gaat het rijtje daarheen (' + r.fout.met + ')');
  ok(/fouten staan open/.test(r.fout.wat || ''), 'en het plan zegt waaróm juist dit rijtje ("' + r.fout.wat + '")');
  ok(r.fout.naAf === 'imperfecto',
    'het controlegeval: is dat rijtje af, dan de volgende mét fouten en niet terug naar boven (' + r.fout.naAf + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
