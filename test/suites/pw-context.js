// v20.1: een blok op Vandaag verdient zijn plek uit jouw context, of het staat er niet.
//
// Stefan, 5 augustus: "laten we voorzichtig zijn met dingen toevoegen. Eerder dingen weghalen en
// veel meer contextueel werken (...) Context koppelen aan relevantie." Zijn moeder haakte af op
// precies dit scherm: te veel informatie, te veel knoppen waarvan de bedoeling niet duidelijk was.
// De reden dat er zoveel stond, is dat elk blok zichzelf tekende ook als het niets te zeggen had:
// een nieuwskaart die meldde dat er geen nieuws was, een balk op 0%, dertien lege staafjes met een
// knop naar cijfers die nog nergens over gingen, en drie chipjes met een nul erin.
//
// Wat deze suite vastlegt, en dat is bewust in twee richtingen:
//   - dag een is klein. Geen nieuwskaart, geen chiprij: alleen starten en spelen.
//   - en alles komt terug op het moment dat het over jou gaat. Per blok wordt hier de context
//     neergezet die het verdient, en daarna moet het er ook echt staan. Weglaten mag nooit
//     verstoppen worden; dat verschil is het hele verhaal van v19.64 en het geldt hier ook.
//   - de basisbalk gaat over jouw niveau, niet over een hardgecodeerde A1. Sinds v20.3 telt
//     daarvoor alleen bewijs mee en niet je eigen claim; die grens ligt hieronder vast.
//
// v23.224: de kaart "Waar je staat" is van Vandaag af (Stefan: "deze functionaliteit mag wel uit
// het scherm"). Alles wat hier over die kaart ging, gaat nu over het voortgangsscherm, waar de balk
// mét legenda al stond. De regel eronder verandert niet: de balk moet jouw niveau noemen en een
// claim is geen bewijs. Wat wél weg is: de vraag of het blok zichzelf op tijd toont, want het staat
// niet meer op het scherm waar dat over ging.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

function minstens(nu, vanaf) {
  const p = (v) => (v || '').replace(/^v/, '').split('.').map(Number);
  const [a, b] = [p(nu), p(vanaf)];
  return a[0] > b[0] || (a[0] === b[0] && a[1] >= b[1]);
}

async function nieuwProfiel(page) {
  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Test' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    var w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
  await page.waitForTimeout(200);
}

// Zet n woorden van het gevraagde niveau rechtstreeks in doos 3. De echte weg daarheen is drie
// goede beurten over een week, en die heeft een test niet.
async function zetOnderweg(page, aantal, niveau) {
  return page.evaluate(([n, nv]) => {
    const map = pcicMap(), niv = pcicNiv();
    let gezet = 0;
    for (const k in map) {
      if (gezet >= n) break;
      if ((map[k] || []).some((s) => niv[s] === nv) && !(S.srs || {})[k]) {
        S.srs[k] = { box: 3, due: addDays(today(), 3), n: 3 };
        gezet++;
      }
    }
    try { persist(); } catch (e) {}
    return gezet;
  }, [aantal, niveau]);
}

async function dagOpnieuw(page) {
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(350);
}

/* 22 aug, v23.167: het dagscherm heeft een voorkant en een achterkant gekregen. Vóór je les staat
   er één ding, je les. Alles wat deze suite meet (nieuws, lijn, chiprij, spelen) zit sindsdien
   achter "les af", omdat het dagscherm anders een menu is waarop beginnen de saaiste optie is.

   Voor deze suite verandert dat de vraag niet, alleen het moment: elk blok moet nog steeds zijn
   eigen plek verdienen uit jouw context. Zou hier niets gezet worden, dan werd elke "die staat er
   niet"-regel waar omdat de hele achterkant weg is, en dat is geen test meer. */
async function lesAfVandaag(page) {
  await page.evaluate(() => {
    S.lesFlow = S.lesFlow || {}; S.lesFlow[today()] = true;
    try { persist(); } catch (e) {}
  });
  await dagOpnieuw(page);
}

async function dagFoto(page) {
  return page.evaluate(() => {
    const lijst = document.getElementById('lessonList');
    return {
      /* v23.224: binnen het DAGSCHERM kijken en niet in het hele document. dagBasisBalk bestaat
         nog gewoon, alleen op Voortgang, en dat tabblad blijft in de DOM staan als je wegklikt.
         Zonder deze scope zou "staat er nog een balk op Vandaag" altijd waar zijn, om precies de
         reden die onderaan deze suite al een keer is opgeschreven. */
      nieuws: !!(lijst && lijst.querySelector('#nieuwsKaart')),
      lijn: !!(lijst && lijst.querySelector('#lijnKaart')),
      basis: !!(lijst && lijst.querySelector('#dagBasisBalk')),
      peil: !!(lijst && lijst.querySelector('#peilKaart')),
      speel: !!document.getElementById('speelKaart'),
      start: !!document.getElementById('btnStartLesFlow'),
      ritme: !!document.querySelector('.ritme'),
      chips: document.querySelectorAll('.ritme .chip').length,
      kaarten: lijst ? lijst.querySelectorAll('.card').length : -1,
      tekst: lijst ? lijst.innerText.replace(/\s+/g, ' ') : ''
    };
  });
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 360, height: 780 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await nieuwProfiel(page);

  console.log('\n-- versie --');
  const versie = await page.evaluate(() => APP_VERSIE);
  ok(minstens(versie, 'v20.1'), 'versie is minstens v20.1 (nu ' + versie + ')');

  console.log('\n-- dag een: alleen wat over jou gaat --');
  await dagOpnieuw(page);
  const voorLes = await dagFoto(page);
  ok(voorLes.start, 'de startknop staat er');
  /* 22 aug, v23.167: hier stond "en de speelkaart, want spelen kan altijd". Dat is bewust
     teruggedraaid: spelen kan nu zodra je les af is, niet ernaast. Zeven kaarten waarvan er vijf
     leuker waren dan beginnen, maakten van het dagscherm een menu. Dus wordt het hier twee regels:
     vóór je les staat de speelkaart er niet, erna wel. */
  ok(!voorLes.speel, 'vóór je les staat de speelkaart er niet, want beginnen is het enige aanbod');
  await lesAfVandaag(page);
  const dag1 = await dagFoto(page);
  const rel1 = await page.evaluate(() => dagRelevantie());
  ok(dag1.speel, 'en zodra je les af is staat hij er wel, want dan kan spelen altijd');
  ok(!dag1.nieuws, 'geen nieuwskaart die meldt dat er geen nieuws is');
  ok(!dag1.lijn, 'geen cijferkaart (v23.224: die staat op geen enkele dag meer op Vandaag)');
  ok(!dag1.ritme, 'geen chiprij met alleen maar nullen');
  ok(dag1.kaarten <= 3, 'hoogstens drie kaarten op dag een (' + dag1.kaarten + ')');
  ok(!/0\/5|0\/30|0%/.test(dag1.tekst), 'nergens een nul als stand: ' + dag1.tekst.slice(0, 110));
  ok(rel1.nieuws === false,
    'dagRelevantie() zegt zelf ook dat er niets te melden is (' + JSON.stringify(rel1) + ')');
  /* v23.224: `basis` en `lijn` waren de twee vragen van de cijferkaart. Die kaart is weg, dus
     horen de velden het ook te zijn: een veld dat niemand leest is precies waar over een half jaar
     weer een blok uit groeit. */
  ok(!('basis' in rel1) && !('lijn' in rel1),
    'en de twee velden van de cijferkaart zijn uit dagRelevantie verdwenen');
  // v23.64: chipHerhaal bestaat niet meer. Stefan: "herhaling bij? waarom staat dat hier is dat
  // ook een extra knop? verwarrend." Wat deze regel bewaakt blijft hetzelfde: op dag een staat er
  // geen enkel chipje, en dagRelevantie() zegt dat zelf ook.
  ok(rel1.chipNieuw === false && rel1.chipDoel === false,
    'en dat geldt voor de chipjes die er nog zijn');
  ok(!('chipHerhaal' in rel1), 'het vinkje "herhalingen bij" is helemaal weg, ook uit dagRelevantie');
  ok(rel1.niveau === 'A1', 'het niveau van een vers profiel is A1 (' + rel1.niveau + ')');

  console.log('\n-- de basisbalk staat op Voortgang, en gaat over jouw niveau --');
  const gezet = await zetOnderweg(page, 2, 'A1');
  ok(gezet === 2, 'er zijn twee A1-woorden in doos 3 gezet (' + gezet + ')');
  await dagOpnieuw(page);
  const naBasis = await dagFoto(page);
  /* v23.64 haalde de balk van Vandaag af en zette er één zin voor in de plaats. v23.224 heeft ook
     die zin weggehaald. Wat hier overblijft is de eis dat Vandaag er niets van terugkrijgt, en dat
     de balk op Voortgang wél zegt over welk niveau hij gaat. */
  ok(!naBasis.basis && !naBasis.lijn, 'op Vandaag staat er niets van (geen balk, geen kaart)');
  const noemA1 = await page.evaluate(() => PCIC_NOEMER.A1);
  const vgA1 = await page.evaluate(() => {
    show('voortgang');
    const el = document.getElementById('voortgangCard') || document.getElementById('tab-voortgang');
    return { balk: !!document.getElementById('dagBasisBalk'),
             tekst: (el.innerText || '').replace(/\s+/g, ' ') };
  });
  ok(vgA1.balk, 'op Voortgang staat de balk wel');
  ok(/\bA1\b/.test(vgA1.tekst), 'en die noemt jouw niveau (' + vgA1.tekst.slice(0, 90) + ')');
  ok(new RegExp('\\b' + noemA1 + '\\b').test(vgA1.tekst),
    'met de noemer erbij, want zonder noemer is de balk maatloos (' + noemA1 + ')');

  console.log('\n-- het dagdoel staat op één plek --');
  await page.evaluate(() => { S.xp[today()] = 12; try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  /* v23.31: het dagdoel-chipje is weg van de leskaart. Het stond twee keer op hetzelfde scherm.
     Deze test bewaakt vanaf nu dat het bij die ene plek blijft: eentje op het dagscherm, niet nul
     en niet twee. */
  const doelPlekken = await page.evaluate(() => ({
    lijst: /dagdoel/i.test((document.getElementById('lessonList') || {}).innerText || ''),
    kop: ((document.getElementById('goalTxt') || {}).innerText || '')
  }));
  ok(!doelPlekken.lijst, 'het dagdoel-chipje staat niet meer op de leskaart');
  ok(/\d+\/\d+/.test(doelPlekken.kop),
     'en de stand staat nog wel bovenin, op die ene plek ("' + doelPlekken.kop + '")');
  await page.evaluate(() => { S.xp[addDays(today(), -1)] = 10; try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  const tweeDagen = await dagFoto(page);
  /* v23.224: hier stond dat de strook vanaf de tweede dag verschijnt. De veertien staafjes zijn
     met de kaart mee weg. Wat ervoor in de plaats staat is de omgekeerde eis: twee dagen oefenen
     zet geen enkel blok terug op dit scherm. */
  ok(!tweeDagen.lijn && !/jouw lijn/i.test(tweeDagen.tekst),
    'twee dagen oefenen zet de strook niet terug op Vandaag');

  console.log('\n-- de chipjes zeggen alleen iets als er iets in staat --');
  const chipNieuw = await page.evaluate(() => {
    S.newIntro[today()] = 2;
    show('lessen');
    const el = document.querySelector('.ritme');
    return el ? el.innerText.replace(/\s+/g, ' ') : '';
  });
  ok(/nieuwe woorden 2/.test(chipNieuw), 'wie vandaag nieuwe woorden zag, ziet er hoeveel ("' + chipNieuw + '")');
  const chipBij = await page.evaluate(() => {
    const t = today();
    for (const id in S.srs) S.srs[id].due = addDays(t, 3);
    show('lessen');
    const el = document.querySelector('.ritme');
    return el ? el.innerText.replace(/\s+/g, ' ') : '';
  });
  // v23.64: het vinkje "herhalingen bij" is weg. Zie de toelichting in pw-tellersweg; hier blijft
  // staan dat er dan ook echt niets in de plaats komt.
  ok(!/herhaling(en)? bij/i.test(chipBij), 'wie bij is krijgt daar geen chipje over ("' + chipBij + '")');
  ok(!/\bopen\b/i.test(chipBij), 'en nog steeds nergens een saldo');

  console.log('\n-- nieuws is er pas als er nieuws is --');
  const nieuws = await page.evaluate(() => {
    // de ochtendfoto is de stand bij je eerste bezoek van vandaag; het verschil met nu is je nieuws.
    // Hier zetten we die foto één les lager, wat hetzelfde is als: je hebt vandaag een les afgerond.
    dagSnapOchtend();
    S.snap.lessen = (dagSnapNu().lessen || 0) - 1;
    show('lessen');
    return { kaart: !!document.getElementById('nieuwsKaart'), regels: dagNieuwsRegels().length };
  });
  ok(nieuws.regels > 0, 'er is nu iets te melden (' + nieuws.regels + ' regel(s))');
  ok(nieuws.kaart, 'en dan staat de nieuwskaart er ook');

  console.log('\n-- je basis gaat over jouw niveau, niet over een hardgecodeerde A1 --');
  // v20.1 liet de balk simpelweg poortRang() volgen. v20.3 heeft dat voor de claim teruggedraaid:
  // poortRang() telt niveauClaim() mee, dus wie bij het instellen "ik ken de basis" aanvinkt zou een
  // balk krijgen die op zijn eigen verklaring rust. Een balk die op jouw eigen verklaring rust kan
  // nooit een bevestiging zijn, en bevestiging is precies wat die balk moet doen. Wat blijft staan
  // is de helft die er toen echt toe deed: bewijs verschuift de balk wel. Zie ook pw-peiling.js.
  const claim = await page.evaluate(() => {
    const voor = balkNiveau();
    const n = niveauClaim(0);              // "ik ken de basis": alle A1-woorden in doos 3
    return { voor: voor, gezet: n, dag: dagNiveau(), balk: balkNiveau() };
  });
  ok(claim.voor === 'A1', 'zonder claim was het A1');
  ok(claim.gezet > 100, 'de claim heeft het hele A1-niveau neergezet (' + claim.gezet + ')');
  ok(claim.dag === 'A2', 'poortRang telt die claim mee, dus dagNiveau() zegt A2 (' + claim.dag + ')');
  ok(claim.balk === 'A1', 'maar de balk blijft op A1 staan: aanvinken is geen bewijs (' + claim.balk + ')');

  // en nu hetzelfde niveauverschil, maar dan verdiend: 85 procent van A1 echt vastgezet.
  const bewijs = await page.evaluate(() => {
    niveauClaimTerug();
    const app = pcicKeysApp()['A1'] || {};
    const drempel = stevigDrempel();
    const nodig = Math.ceil(0.87 * (PCIC_NOEMER['A1'] || 390));
    let gezet = 0;
    for (const k in app) {
      if (gezet >= nodig) break;
      (app[k] || []).forEach((id) => { S.srs[id] = { box: drempel, due: addDays(today(), 30), n: drempel, k: 1 }; });
      gezet++;
    }
    try { persist(); } catch (e) {}
    return { gezet: gezet, dag: dagNiveau(), balk: balkNiveau() };
  });
  ok(bewijs.balk === 'A2', 'wie A1 wel bewijst, ziet A2 als zijn basis (' + bewijs.balk + ')');
  const a2 = await zetOnderweg(page, 3, 'A2');
  await dagOpnieuw(page);
  const naA2 = await dagFoto(page);
  ok(a2 === 3, 'er zijn drie A2-woorden onderweg gezet (' + a2 + ')');
  /* v23.224: dit las de kaart op Vandaag. Die is weg, dus wordt dezelfde vraag op Voortgang
     gesteld: noemt de balk het niveau waar hij over gaat? */
  const kop = await page.evaluate(() => {
    show('voortgang');
    /* De kaart waar de BALK in zit, niet de eerste kaart van het scherm. Op Voortgang staat
       bovenaan "Je week", en die noemt geen niveau; dan zou deze proef groen of rood worden om
       iets dat er niets mee te maken heeft. */
    const b = document.getElementById('dagBasisBalk');
    const kaart = b ? b.closest('.card') : null;
    return kaart ? kaart.innerText.replace(/\s+/g, ' ') : '';
  });
  /* v23.0: het kopje heet "Waar je staat" in plaats van "Je basis". Wat deze test bewaakt is niet
     de woordkeuze maar dat er een niveau in staat, want zonder niveau meet de balk iets anders dan
     de lezer denkt.
     v23.64: het niveau staat niet meer in de kop maar in de zin eronder, want twee keer hetzelfde
     op één kaart is de fout waar dit scherm mee bezig was. Dus wordt het blok als geheel gelezen. */
  ok(/A2/.test(kop) && kop.length > 2, 'het blok noemt A2 ("' + kop.slice(0, 100) + '")');
  /* v23.31: de balk telt vanaf nu alle niveaus tot en met het jouwe bij elkaar op, dus op A2 is
     de noemer A1 plus A2. Wat deze test bewaakt is niet veranderd: de noemer moet zichtbaar zijn en
     hij moet meegroeien met het niveau, want anders meet de balk iets anders dan de lezer denkt.
     Erbij: wat je op A1 hebt opgebouwd mag niet van het scherm verdwijnen op de dag dat je A1
     haalt, en dat is precies wat een noemer van 403 zou betekenen. */
  /* v23.224: de zin op Vandaag bestond niet meer, dus wordt hier hetzelfde op Voortgang gevraagd:
     de balk moet A1 en A2 samen noemen en niet het losse niveaugetal doen alsof het de noemer is. */
  const samenA2 = await page.evaluate(() => PCIC_NOEMER.A1 + PCIC_NOEMER.A2);
  ok(samenA2 !== noemA1, 'de noemer van A1 en A2 samen verschilt van die van A1 (' + samenA2 + ' tegenover ' + noemA1 + ')');
  ok(/A1 en A2|A1-A2/.test(kop),
     'de balk noemt allebei de niveaus (' + kop.slice(0, 130) + ')');
  ok(!naA2.lijn && !naA2.basis,
     'en op Vandaag staat er nog steeds niets van');

  /* v23.64. Hier stond document.querySelectorAll('.bar.duo') na show('perfil'), en dat telde het
     hele document: het dagscherm blijft in de DOM staan als je van tabblad wisselt, dus de balk die
     hier geteld werd was de balk van Vandaag. De test was groen om een reden die niets met zijn
     eigen zin te maken had. Zesde geval van die familie in deze codebase.

     Nu wordt er gemeten binnen het zichtbare tabblad, en op de plek waar de balk sinds v23.64
     hoort: Voortgang. */
  console.log('\n-- weggelaten is niet verstopt --');
  await page.evaluate(() => show('voortgang'));
  await page.waitForTimeout(600);
  const vg = await page.evaluate(() => {
    const tab = document.getElementById('tab-voortgang') || document.body;
    return { balken: tab.querySelectorAll('.bar.duo').length, tekst: tab.innerText };
  });
  ok(vg.balken > 0, 'op Voortgang staat de balk gewoon (' + vg.balken + ')');
  ok(/A1/.test(vg.tekst) && /A2/.test(vg.tekst), 'met alle niveaus erbij');
  await page.evaluate(() => show('perfil'));
  await page.waitForTimeout(600);
  const profiel = await page.evaluate(() => {
    const tab = document.getElementById('tab-perfil') || document.body;
    return { tekst: tab.innerText };
  });
  ok(/A1/.test(profiel.tekst), 'en op Profiel staat je niveau er ook nog (' + profiel.tekst.slice(0, 60).replace(/\n/g, ' ') + ')');

  console.log('\n-- geen streepjes in wat er overblijft --');
  await dagOpnieuw(page);
  const eind = await dagFoto(page);
  ok(!/[—–]|--/.test(eind.tekst), 'geen em- of en-streepjes op het dagscherm');

  ok(errs.length === 0, 'geen javascriptfouten: ' + errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fout ? '\n' + fout + ' PUNT(EN) GEFAALD' : '\nALLES GROEN');
  process.exit(fout ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
