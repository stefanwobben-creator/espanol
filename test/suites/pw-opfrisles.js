// pw-opfrisles.js (13 sep, v23.254) - krijg je een lesje als het onderwerp op nul staat?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 13 september: "bij grammatica is het denk ik ook goed om de toetsen wat uitgebreider te
// doen. Echt even een lesje waarbij je de instructie nog een keer kunt lezen, een of meerdere
// vragen krijgt om te toetsen of je de regel snapt en daarna wat meerkeuzevragen om de toepassing
// te toetsen. Nu zijn het maar twee vragen."
//
// Geteld over alle 31 onderwerpen:
//
//     de volle microles (gcBouw)       5 vragen, met de regel en een begripsvraag
//     de opfrisser (gcOpfrisBouw)      2 vragen, geen uitleg, geen regel
//
// En de opfrisser is precies wat de dagles je geeft als een onderwerp op herhaling staat. Dus: hoe
// zwakker het doosje, hoe dunner de hulp. Dat is andersom.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. EEN DOOSJE WAAR JE OP TERUGGEVALLEN BENT GEEFT EEN LESJE: de regel, een begripsvraag, dan
//      toepassingsvragen, in die volgorde.
//   2. EEN DOOSJE DAT STAAT GEEFT EEN OPFRISSER: twee vragen, kort. Dit is de controle. Wordt alles
//      een lesje, dan is er geen opfrisser meer en duurt elke dagles drie keer zo lang.
//   2b. EN DOOS 0 IS NIET GENOEG. Doos 0 betekent twee dingen: "nog nooit gedaan" en "teruggevallen".
//      Een tak die die twee hetzelfde behandelt geeft een beginner een herhalingsles. Vier bestaande
//      suites vonden dat tegelijk; vandaar de drempel van GRAM_RIJ_MIN antwoorden.
//   3. DE MAAT HANGT AAN HET DOOSJE VAN HET PATROON, niet aan het onderwerp als geheel. Kom je om
//      op de Griekse val, dan is die val het onderwerp van het lesje.
//   4. ER KOMT GEEN NIEUWE TEKST BIJ: de regel in het lesje is dezelfde c.uitleg die de microles
//      toont, en de begripsvraag is dezelfde c.begrip.
//   5. EN HET IS EEN GELDIG ONDERWERP voor de wizard, dus het rendert zonder fouten.
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
  await page.waitForTimeout(700);
  // Een echt profiel, want gwStart() navigeert en dat kan pas als er iemand is.
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Test' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  const bouw = await page.evaluate(() => {
    function beschrijf(o) {
      if (!o) return null;
      return {
        lesje: !!o.lesje, titel: o.titel, pitch: o.pitch,
        stappen: (o.stappen || []).map((s) => ({
          kop: s.kop, n: (s.vragen || []).length, diep: String(s.diep || ''),
          kern: !!s.kern, hulp: !!s.hulp,
          vragen: (s.vragen || []).map((q) => q.v)
        }))
      };
    }
    // teruggevallen: doos 0 met een geschiedenis erachter
    S.gram = { 'genero#0': { box: 0, due: '', goed: 12, fout: 6, laatst: '', rij: '110101', rijVoor: '110101' } };
    const opNul = beschrijf(gcOpfrisBouw('opfris-genero#0'));
    // staat gewoon: doos 3
    S.gram = { 'genero#0': { box: 3, due: '', goed: 9, fout: 1, laatst: '', rij: '111111111', rijVoor: '111111111' } };
    const opDrie = beschrijf(gcOpfrisBouw('opfris-genero#0'));
    // doos 0, maar je hebt hier pas twee vragen van gehad: dat is kennismaking, geen terugval
    S.gram = { 'genero#0': { box: 0, due: '', goed: 1, fout: 1, laatst: '', rij: '10', rijVoor: '10' } };
    const bijnaVers = beschrijf(gcOpfrisBouw('opfris-genero#0'));
    // en helemaal geen doosje
    S.gram = {};
    const helemaalVers = beschrijf(gcOpfrisBouw('opfris-genero#0'));
    // terug naar nul met geschiedenis
    S.gram = { 'genero#0': { box: 0, due: '', goed: 12, fout: 6, laatst: '', rij: '110101', rijVoor: '110101' } };
    const weerNul = beschrijf(gcOpfrisBouw('opfris-genero#0'));
    // en het onderwerp als geheel, zonder patroon
    S.gram = { genero: { box: 0, due: '', goed: 9, fout: 4, laatst: '', rij: '101101', rijVoor: '101101' } };
    const zonderPatroon = beschrijf(gcOpfrisBouw('opfris-genero'));
    // de volle microles, om mee te vergelijken
    const vol = beschrijf(gcBouw('genero'));
    const c = gcConcept('genero');
    return { opNul, opDrie, bijnaVers, helemaalVers, weerNul, zonderPatroon, vol, drempel: GRAM_RIJ_MIN,
             uitleg: c.uitleg, begripVraag: c.begrip.v, opfrisN: GC_OPFRIS_VRAGEN, lesN: GC_OPFRIS_LES_VRAGEN };
  });

  // ---------- 1. doosje op nul -> een lesje ----------
  console.log('\n1. een doosje waar je op TERUGGEVALLEN bent geeft een lesje');
  ok(bouw.opNul && bouw.opNul.lesje, 'het is een lesje en geen opfrisser');
  ok(bouw.opNul.stappen.length === 2, 'in twee stappen (' + bouw.opNul.stappen.length + ')');
  ok(!!bouw.opNul.stappen[0].diep, 'stap 1 draagt de hele regel als naslag');
  ok(bouw.opNul.stappen[0].kern === true, 'en zet de kern erboven, met de ezelsbrug');
  ok(bouw.opNul.stappen[0].n === 1, 'stap 1 stelt één vraag: snap je de regel? (' + bouw.opNul.stappen[0].n + ')');
  ok(bouw.opNul.stappen[1].n === bouw.lesN,
     'stap 2 stelt er ' + bouw.opNul.stappen[1].n + ' over de toepassing (afgesproken: ' + bouw.lesN + ')');
  const totaal = bouw.opNul.stappen.reduce((a, s) => a + s.n, 0);
  ok(totaal >= 5, 'samen ' + totaal + ' vragen, in plaats van twee');

  // ---------- 2. doosje dat staat -> de opfrisser blijft kort ----------
  console.log('\n2. een doosje dat staat blijft een opfrisser van twee vragen');
  ok(bouw.opDrie && !bouw.opDrie.lesje, 'CONTROLE: op doos 3 is het geen lesje');
  ok(bouw.bijnaVers && !bouw.bijnaVers.lesje,
     'CONTROLE: en op doos 0 met maar twee antwoorden erachter ook niet — dat is kennismaking, geen terugval');
  ok(bouw.helemaalVers && !bouw.helemaalVers.lesje,
     'CONTROLE: en zonder doosje al helemaal niet. Doos 0 betekent twee dingen, en dit is het andere');
  ok(bouw.opDrie.stappen.length === 1, 'CONTROLE: één stap (' + bouw.opDrie.stappen.length + ')');
  ok(bouw.opDrie.stappen[0].n === bouw.opfrisN,
     'CONTROLE: en ' + bouw.opDrie.stappen[0].n + ' vragen, want dit is een opfrisser (afgesproken: ' + bouw.opfrisN + ')');
  ok(!bouw.opDrie.stappen[0].diep, 'CONTROLE: zonder de hele regel eronder, want die heb je niet nodig');

  // ---------- 3. het doosje van het patroon beslist ----------
  console.log('\n3. de maat hangt aan het patroon waar je op omkwam');
  ok(bouw.weerNul && bouw.weerNul.lesje, 'zakt datzelfde patroon terug naar nul, dan komt het lesje terug');
  ok(bouw.zonderPatroon && bouw.zonderPatroon.lesje,
     'en zonder patroon kijkt hij naar het onderwerp als geheel');

  // ---------- 4. geen nieuwe tekst ----------
  console.log('\n4. er komt geen letter nieuwe tekst bij');
  ok(bouw.opNul.stappen[0].diep === bouw.uitleg,
     'de regel in het lesje is letterlijk dezelfde c.uitleg als in de microles');
  ok(bouw.opNul.stappen[0].vragen[0] === bouw.begripVraag,
     'en de begripsvraag is dezelfde c.begrip ("' + String(bouw.opNul.stappen[0].vragen[0]).slice(0, 50) + '...")');
  const volTotaal = bouw.vol.stappen.reduce((a, s) => a + s.n, 0);
  console.log('     de volle microles telt ' + volTotaal + ' vragen, het lesje ' + totaal + ', de opfrisser ' + bouw.opfrisN);

  // ---------- 5. en het rendert ----------
  console.log('\n5. en het is een onderwerp dat de wizard kan tonen');
  const scherm = await page.evaluate(() => {
    S.gram = { 'genero#0': { box: 0, due: '', goed: 12, fout: 6, laatst: '', rij: '110101', rijVoor: '110101' } };
    try {
      gwStart('opfris-genero#0', 0);
      // renderGramWiz() geeft de html van het onderwerp zelf terug; het body-scherm eromheen
      // hangt af van de navigatie en dat is hier niet wat er getoetst wordt.
      return { ok: true, tekst: renderGramWiz().replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').slice(0, 600) };
    } catch (e) { return { ok: false, fout: String(e) }; }
  });
  ok(scherm.ok, 'gwStart opent het lesje' + (scherm.ok ? '' : ': ' + scherm.fout));
  if (scherm.ok) {
    ok(/regel nog een keer|rule once more/i.test(scherm.tekst),
       'en de eerste stap gaat over de regel' + (/regel nog een keer|rule once more/i.test(scherm.tekst) ? '' : ' — op het scherm staat: ' + scherm.tekst));
  }

  ok(errs.length === 0, 'geen javascriptfouten' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));

  await browser.close();
  console.log(fout ? '\n' + fout + ' fout' : '\nalles groen');
  process.exit(fout ? 1 : 0);
})();
