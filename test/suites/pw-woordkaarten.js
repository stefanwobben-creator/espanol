// pw-woordkaarten.js (14 aug, v23.100) — is een woordkaart een vraag of een woordenboekregel?
//
// WAAROM DIT ER IS
//
// Op 14 augustus bleek van de 1376 Cervantes-woorden dat er 80 het Spaanse antwoord al op de
// Nederlandse kant hadden staan, en 295 meerdere betekenissen op elkaar stapelden:
//
//     "a pesar de = ondanks; wegen"                        -> antwoord: pesar
//     "overblijven; afspreken; quedar bien = goed staan"   -> antwoord: quedar
//     "vinger; teen: dedo del pie"                         -> antwoord: dedo
//
// De eerste drie vragen je een woord te raden dat er al staat. De rest vraagt je te raden wélke van
// drie betekenissen bedoeld wordt, en dat is geen taalvraag maar een gokspel.
//
// De oorzaak is niet slordigheid maar herkomst: het nl-veld komt uit een frequentielijst, waar het
// een woordenboekvertaling is en dus alles hoort te vermelden. Op een kaart is het een vraag.
// Zolang er woorden uit die lijst bij komen, kan dit terugkomen. Vandaar deze suite.
//
// HET CONTROLEGEVAL
//
// Een lekcontrole is triviaal groen te krijgen door hem overal te laten toeslaan of nergens. Daarom
// staan er twee kanten in: een kaart die evident lekt MOET gezien worden, en een leenwoord (virus,
// club, motor) mag NIET als lek gelden. Dat laatste is geen detail: als je die als fout rekent,
// verdwijnen er tientallen goede kaarten uit de app.
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
    const kaal = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    const tok = (s) => kaal(s).split(/[^a-z]+/).filter((w) => w.length > 2);
    // puntkomma's binnen haakjes horen bij het haakje: "pakken, nemen (Spanje; grof in Lat-Am!)"
    function splitsTop(s, teken) {
      const uit = []; let diep = 0, cur = '';
      for (const ch of s) {
        if (ch === '(') diep++; else if (ch === ')') diep--;
        if (ch === teken && diep === 0) { uit.push(cur.trim()); cur = ''; } else cur += ch;
      }
      if (cur.trim()) uit.push(cur.trim());
      return uit;
    }
    // aan beide kanten het lidwoord eraf: "de metro" tegenover "el metro" is geen lek maar hetzelfde
    // leenwoord. Zonder deze regel vallen er tientallen goede kaarten uit de app.
    function leenwoord(kant, es) {
      const b = kaal(es).replace(/^(el|la|los|las|un|una) /, '').replace(/[^a-z ]/g, '').trim();
      return splitsTop(kant, ',').some((d) =>
        kaal(d).replace(/\([^)]*\)/g, '').replace(/^(de|het|een) /, '').replace(/[^a-z ]/g, '').trim() === b);
    }
    function lekt(w) {
      const kant = String(w.nl || ''), es = String(w.es || '');
      if (!kant || !es || leenwoord(kant, es)) return false;
      if (/=/.test(kant)) return true;
      const esT = new Set(tok(es));
      return tok(kant).some((t) => esT.has(t));
    }

    const alle = [].concat(
      typeof C_WORDS !== 'undefined' ? C_WORDS : [],
      typeof K_WORDS !== 'undefined' ? K_WORDS : [],
      typeof WORDS !== 'undefined' ? WORDS : []);
    const lekkers = alle.filter(lekt);
    const gestapeld = alle.filter((w) => splitsTop(String(w.nl || ''), ';').length > 1);

    return {
      totaal: alle.length,
      lekt: lekkers.length,
      lektVoorbeeld: lekkers.slice(0, 3).map((w) => w.id + ': ' + w.nl + ' -> ' + w.es),
      gestapeld: gestapeld.length,
      gestapeldVoorbeeld: gestapeld.slice(0, 3).map((w) => w.id + ': ' + w.nl),
      metMeer: alle.filter((w) => w.meer).length,
      // de controlegevallen
      zietEenLek: lekt({ id: 'x', es: 'pesar', nl: 'a pesar de = ondanks; wegen' }),
      spaartLeenwoord: !lekt({ id: 'y', es: 'virus', nl: 'virus' }),
      spaartLidwoord: !lekt({ id: 'z', es: 'el metro', nl: 'de metro' })
    };
  });

  console.log('\n-- de vraagkant verklapt het antwoord niet --');
  ok(r.lekt === 0, 'geen enkele woordkaart deelt een woord met zijn eigen antwoord (nu: ' + r.lekt + ')');
  if (r.lekt) r.lektVoorbeeld.forEach((v) => console.log('      ' + v));

  console.log('\n-- en hij stelt één vraag, geen drie --');
  ok(r.gestapeld === 0, 'geen enkele kaart stapelt betekenissen met een puntkomma (nu: ' + r.gestapeld + ')');
  if (r.gestapeld) r.gestapeldVoorbeeld.forEach((v) => console.log('      ' + v));
  ok(r.metMeer > 100, 'de rest staat wel degelijk ergens: ' + r.metMeer + ' kaarten hebben een meer-veld');

  console.log('\n-- de controlegevallen --');
  // Zonder deze twee is een lekcontrole die alles of niets ziet ook groen.
  ok(r.zietEenLek === true, 'een kaart die het antwoord echt verklapt wordt wél gezien');
  ok(r.spaartLeenwoord === true, 'een leenwoord (virus = virus) telt níét als lek');
  ok(r.spaartLidwoord === true, 'en "de metro" tegenover "el metro" ook niet: het lidwoord telt niet mee');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
