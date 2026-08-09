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
//   - dag een is klein. Geen nieuwskaart, geen lijnkaart, geen chiprij: alleen starten en spelen.
//   - en alles komt terug op het moment dat het over jou gaat. Per blok wordt hier de context
//     neergezet die het verdient, en daarna moet het er ook echt staan. Weglaten mag nooit
//     verstoppen worden; dat verschil is het hele verhaal van v19.64 en het geldt hier ook.
//   - de basisbalk gaat over jouw niveau, niet over een hardgecodeerde A1. Sinds v20.3 telt
//     daarvoor alleen bewijs mee en niet je eigen claim; die grens ligt hieronder vast.
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

async function dagFoto(page) {
  return page.evaluate(() => {
    const lijst = document.getElementById('lessonList');
    return {
      nieuws: !!document.getElementById('nieuwsKaart'),
      lijn: !!document.getElementById('lijnKaart'),
      basis: !!document.getElementById('dagBasisBalk'),
      strook: !!document.querySelector('#lijnKaart .lijnstrook'),
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
  const dag1 = await dagFoto(page);
  const rel1 = await page.evaluate(() => dagRelevantie());
  ok(dag1.start, 'de startknop staat er');
  ok(dag1.speel, 'en de speelkaart, want spelen kan altijd');
  ok(!dag1.nieuws, 'geen nieuwskaart die meldt dat er geen nieuws is');
  ok(!dag1.lijn, 'geen lijnkaart met een lege balk en dertien gaten');
  ok(!dag1.ritme, 'geen chiprij met alleen maar nullen');
  ok(dag1.kaarten <= 3, 'hoogstens drie kaarten op dag een (' + dag1.kaarten + ')');
  ok(!/0\/5|0\/30|0%/.test(dag1.tekst), 'nergens een nul als stand: ' + dag1.tekst.slice(0, 110));
  ok(rel1.nieuws === false && rel1.basis === false && rel1.lijn === false,
    'dagRelevantie() zegt zelf ook dat er niets te melden is (' + JSON.stringify(rel1) + ')');
  ok(rel1.chipNieuw === false && rel1.chipHerhaal === false && rel1.chipDoel === false,
    'en dat geldt voor alle drie de chipjes');
  ok(rel1.niveau === 'A1', 'het niveau van een vers profiel is A1 (' + rel1.niveau + ')');

  console.log('\n-- de basisbalk komt zodra er iets onderweg is --');
  const gezet = await zetOnderweg(page, 2, 'A1');
  ok(gezet === 2, 'er zijn twee A1-woorden in doos 3 gezet (' + gezet + ')');
  await dagOpnieuw(page);
  const naBasis = await dagFoto(page);
  ok(naBasis.basis, 'de balk staat er nu wel');
  ok(naBasis.lijn, 'en dus ook de kaart eromheen');
  ok(!naBasis.strook, 'maar de staafjes nog niet: één blok tegelijk, elk om zijn eigen reden');
  // v23.2: zie pw-a1vandaag. De noemer moet zichtbaar zijn, de rest staat in de legenda.
  // v23.15: het getal wordt opgehaald in plaats van opgeschreven, want het hoort bij de sleutellijst
  // en die groeit mee met wat de app aan Cervantes in huis heeft.
  const noemA1 = await page.evaluate(() => PCIC_NOEMER.A1);
  ok(naBasis.tekst.indexOf('van de ' + noemA1 + ' A1-woorden') !== -1,
    'de zin noemt jouw niveau en de noemer erbij (' + noemA1 + ')');
  ok(/onderweg/.test(naBasis.tekst), 'en wat er onderweg is telt zichtbaar mee');

  console.log('\n-- de lijn komt vanaf twee dagen --');
  await page.evaluate(() => { S.xp[today()] = 12; try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  const eenDag = await dagFoto(page);
  ok(!eenDag.strook, 'met één dag is er nog geen lijn om te tekenen');
  ok(eenDag.ritme && /dagdoel/i.test(eenDag.tekst), 'het dagdoel-chipje staat er wel, want daar staat iets in');
  await page.evaluate(() => { S.xp[addDays(today(), -1)] = 10; try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  const tweeDagen = await dagFoto(page);
  ok(tweeDagen.strook, 'vanaf de tweede dag verschijnt de strook');
  ok(/jouw lijn/i.test(tweeDagen.tekst), 'met zijn eigen kopje erboven');
  const volgorde = await page.evaluate(() => {
    const b = document.getElementById('dagBasisBalk');
    const s = document.querySelector('#lijnKaart .lijnstrook');
    return { basis: Math.round(b.getBoundingClientRect().top), lijn: Math.round(s.getBoundingClientRect().top) };
  });
  ok(volgorde.basis < volgorde.lijn, 'wat je kunt staat nog steeds boven hoe vaak je kwam');

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
  ok(/herhaling(en)? bij/i.test(chipBij), 'wie bij is krijgt het schouderklopje ("' + chipBij + '")');
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
  const kop = await page.evaluate(() => {
    const k = document.querySelector('#lijnKaart .kicker');
    return k ? k.innerText.replace(/\s+/g, ' ') : '';
  });
  // v23.0: het kopje heet "Waar je staat" in plaats van "Je basis". Wat deze test bewaakt is
  // niet de woordkeuze maar dat er een niveau in staat, want zonder niveau meet de balk iets
  // anders dan de lezer denkt. Dus: het niveau moet erin, de rest mag veranderen.
  ok(/A2/.test(kop) && kop.length > 2, 'het kopje boven de balk noemt A2 ("' + kop + '")');
  const noemA2 = await page.evaluate(() => PCIC_NOEMER.A2);
  ok(noemA2 !== noemA1 && naA2.tekst.indexOf('van de ' + noemA2 + ' A2-woorden') !== -1,
     'en de noemer is die van A2, niet die van A1 (' + noemA2 + ' tegenover ' + noemA1 + ')');

  console.log('\n-- weggelaten is niet verstopt --');
  await page.evaluate(() => show('perfil'));
  await page.waitForTimeout(500);
  const profiel = await page.evaluate(() => ({
    balken: document.querySelectorAll('.bar.duo').length,
    tekst: document.body.innerText
  }));
  ok(profiel.balken > 0, 'op Profiel staan de niveaubalken gewoon (' + profiel.balken + ')');
  ok(/A1/.test(profiel.tekst) && /A2/.test(profiel.tekst), 'met alle niveaus erbij');

  console.log('\n-- geen streepjes in wat er overblijft --');
  await dagOpnieuw(page);
  const eind = await dagFoto(page);
  ok(!/[—–]|--/.test(eind.tekst), 'geen em- of en-streepjes op het dagscherm');

  ok(errs.length === 0, 'geen javascriptfouten: ' + errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fout ? '\n' + fout + ' PUNT(EN) GEFAALD' : '\nALLES GROEN');
  process.exit(fout ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
