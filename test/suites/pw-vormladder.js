// pw-vormladder.js (22 aug, v23.173) — meet de vormenladder iets, en komt een afgeronde rij terug?
//
// WAAROM DIT ER IS
//
// Stefan vroeg om een vormenladder: "het is goed als de app zelf bepaalt en dat ik bij 85% goed ofzo
// naar de volgende ladder ga en dan onderscheid maken tussen de regelmatige en onregelmatige."
//
// Eerst gemeten, en dat veranderde de opdracht. De geblokte productieladder bestáát al ("De les",
// zes stappen, drie daarvan vrij typen, twee zonder tabel in beeld). Wat ontbrak:
//
//   1. hij meet niets: lesStapAf() schreef alleen stapMax en laatst
//   2. klaar was voor altijd: stapMax gaat nooit omlaag, dus een rij kwam nooit terug
//   3. voor alle vijf de tijden was het modelwerkwoord hablar
//   4. de overdrachtsstap filterde op regelmatig, dus de twintig onregelmatige indefinido-vormen
//      werden in de ladder nooit geproduceerd
//
// WAAROM DE 85 PROCENT ER NIET IN ZIT, WANT DAT IS EEN BESLUIT TEGEN STEFANS VRAAG IN
//
// Het getal komt uit Wilson et al. 2019, over binaire classificatietaken met gradient-descent-
// leerders; de auteurs noemen zelf 82 bij een andere ruisverdeling en 75 bij weer een andere, en het
// gaat daar over leersnelheid en niet over beheersing. Rawson & Dunlosky, die ik zelf als bewijs
// aanhaalde, zeggen dat criteriumhoogte de mínder belangrijke as is en terugkeer de belangrijkere.
// En het venster zou de eerste maanden niet gevuld zijn: twintig items op de typstappen van één rij
// kost minimaal zestien kalenderdagen. Bij p rond 0,85 en n = 20 is de standaardfout 0,08, dus één
// typfout bepaalt een promotie.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE LADDER MEET. Goed en fout komen per rij binnen, en een fout gaat het foutenlogboek in met
//      een bron erbij, zodat een volgende ronde hem kan wegen in plaats van te moeten uitzoeken
//      waar hij vandaan kwam.
//   2. EEN AFGERONDE RIJ KOMT TERUG. Na zeven dagen, en daarna na eenentwintig.
//   3. EN DAN OP DE LOSSE CEL. Typen zonder tabel, met het werkwoord dat je kent. Niet de
//      overdrachtsstap, want die voegt een ongezien werkwoord toe en dan meet je twee dingen.
//   4. HET CONTROLEGEVAL: EEN RIJ DIE NET AF IS BLIJFT AF. Dit is met één regel groen te krijgen
//      door alles altijd te laten terugkomen, en dan is de ladder een tredmolen.
//   5. NIET ALLES MET HABLAR, en de onregelmatige indefinido-vormen worden geproduceerd.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwVl' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    const CEL = LES_STAPPEN.map(function (s) { return s.id; }).indexOf('cel');
    const LAATSTE = LES_STAPPEN.length - 1;
    uit.celIndex = CEL;

    // ---- 5a. modelwerkwoord per tijd ----
    uit.modellen = {};
    ['presente', 'perfecto', 'indefinido', 'imperfecto', 'subjuntivo'].forEach(function (t) {
      const w = lesWerkwoord(t);
      uit.modellen[t] = w ? w.inf : null;
    });
    uit.verschillend = new Set(Object.values(uit.modellen)).size;

    // ---- 5b. de onregelmatige in de overdrachtsstap van het indefinido ----
    const model = lesWerkwoord('indefinido');
    const pool = lesOverdrachtPool('indefinido', model);
    uit.poolN = pool.length;
    uit.poolOnreg = pool.filter(function (v) { return !conjRegelmatigIn(v, 'indefinido'); })
      .map(function (v) { return v.inf; });
    uit.poolReg = pool.filter(function (v) { return conjRegelmatigIn(v, 'indefinido'); }).length;
    // en het imperfecto blijft wél alleen regelmatig, want daar horen de drie uitzonderingen bij de uitleg
    const mImp = lesWerkwoord('imperfecto');
    uit.impOnreg = lesOverdrachtPool('imperfecto', mImp)
      .filter(function (v) { return !conjRegelmatigIn(v, 'imperfecto'); }).length;

    // ---- 1. de ladder meet ----
    S.brok = {}; S.errors = {};
    const t = 'presente';
    lesStart(t);
    lesSpel.stap = CEL;
    const q = lesOpgaveNu();
    const goedeVorm = conjVorm(q.v, q.p, lesSpel.t);
    lesAntwoord(goedeVorm);                       // goed
    lesSpel.gekozen = null; lesSpel.i = (lesSpel.i || 0) + 1;
    const q2 = lesOpgaveNu();
    lesAntwoord('zzzfout');                       // fout
    uit.rondeGoed = lesSpel.goed;
    uit.rondeFout = lesSpel.fout;
    const foutKeys = Object.keys(S.errors).filter(function (k) { return k.indexOf('conj:') === 0; });
    uit.foutGelogd = foutKeys.length;
    uit.foutBron = foutKeys.length ? S.errors[foutKeys[0]].bron : null;
    lesStapAf();
    const st1 = brokLees(lesId(t));
    uit.opgeslagen = { goed: st1.goed, fout: st1.fout, ronde: st1.laatsteRonde };

    // ---- 2, 3, 4. terugkeer ----
    function rijStand(check, checkN) {
      S.brok = S.brok || {};
      S.brok[lesId(t)] = { stapMax: LAATSTE, laatst: today(), check: check, checkN: checkN || 0 };
      return { klaar: lesKlaar(t), open: lesCheckOpen(t), stap: vormStapVandaag(t) };
    }
    uit.netAf = rijStand(addDays(today(), 7), 1);          // controle staat over een week
    uit.checkDag = rijStand(today(), 1);                   // vandaag is het zover
    uit.checkVoorbij = rijStand(addDays(today(), -3), 1);  // en gemist telt ook

    // en de reeks 7 dan 21
    S.brok[lesId(t)] = { stapMax: LAATSTE, laatst: today(), checkN: 0 };
    lesSpel = { rij: t, t: t, stap: LAATSTE, goed: 6, fout: 0, i: 0, gekozen: null };
    lesCheckZet(t, true);
    uit.eersteCheck = brokLees(lesId(t)).check;
    lesCheckZet(t, true);
    uit.tweedeCheck = brokLees(lesId(t)).check;
    // en niet gehaald betekent: blijft gewoon open
    lesCheckZet(t, false);
    uit.nietGehaald = brokLees(lesId(t)).check;
    uit.vandaag = today();
    uit.over7 = addDays(today(), 7);
    uit.over21 = addDays(today(), 21);
    return uit;
  });

  console.log('\n-- 1. de ladder meet --');
  console.log('   ronde ' + r.rondeGoed + ' goed, ' + r.rondeFout + ' fout · opgeslagen: ' + JSON.stringify(r.opgeslagen));
  ok(r.rondeGoed === 1 && r.rondeFout === 1, 'goed en fout worden geteld in de ronde');
  ok(r.opgeslagen.goed === 1 && r.opgeslagen.fout === 1, 'en per rij weggeschreven, wat eerst niet gebeurde');
  ok(r.opgeslagen.ronde === '1/2', 'met de uitslag van de laatste ronde erbij (' + r.opgeslagen.ronde + ')');
  ok(r.foutGelogd === 1, 'de fout staat in het foutenlogboek (' + r.foutGelogd + ')');
  ok(r.foutBron === 'les', 'met een bron erbij, zodat de rest van de app hem kan wegen (' + r.foutBron + ')');

  console.log('\n-- 2 en 3. een afgeronde rij komt terug, op de losse cel --');
  console.log('   controle vandaag: ' + JSON.stringify(r.checkDag) + ' · gemist: ' + JSON.stringify(r.checkVoorbij));
  ok(r.checkDag.open === true, 'op de controledag staat de rij weer open');
  ok(r.checkDag.klaar === false, 'en telt hij niet meer als af, dus de dagles kan hem kiezen');
  ok(r.checkDag.stap === r.celIndex, 'en je begint op de losse cel (' + r.checkDag.stap + ' van ' + r.celIndex + ')');
  ok(r.checkVoorbij.open === true, 'een gemiste controledag verdwijnt niet');

  console.log('\n-- 4. het controlegeval: een rij die net af is blijft af --');
  console.log('   ' + JSON.stringify(r.netAf));
  ok(r.netAf.klaar === true, 'met de controle nog een week weg telt de rij gewoon als af');
  ok(r.netAf.open === false, 'en staat hij niet open');

  console.log('\n   de reeks: ' + r.eersteCheck + ' dan ' + r.tweedeCheck);
  ok(r.eersteCheck === r.over7, 'de eerste controle staat over zeven dagen');
  ok(r.tweedeCheck === r.over21, 'de tweede over eenentwintig');
  ok(r.nietGehaald === r.vandaag, 'en een ronde die je niet haalt houdt de rij open (' + r.nietGehaald + ')');

  console.log('\n-- 5. niet alles met hablar, en de onregelmatige doen mee --');
  console.log('   ' + JSON.stringify(r.modellen));
  ok(r.verschillend >= 3, 'er zijn minstens drie verschillende modelwerkwoorden (' + r.verschillend + ')');
  ok(r.modellen.imperfecto !== 'hablar' && r.modellen.indefinido !== 'hablar',
    'de twee tijden waar Stefan over struikelt gebruiken niet hetzelfde -ar-werkwoord');
  console.log('   indefinido-pool: ' + r.poolN + ' werkwoorden, waarvan onregelmatig: ' + r.poolOnreg.slice(0, 8).join(', '));
  ok(r.poolOnreg.length >= 5, 'de overdrachtsstap van het indefinido bevat onregelmatige werkwoorden (' + r.poolOnreg.length + ')');
  ok(r.poolReg > 0, 'en de regelmatige nog steeds (' + r.poolReg + ')');
  ok(r.impOnreg === 0, 'terwijl het imperfecto wél alleen regelmatig blijft, want daar horen de drie uitzonderingen bij de uitleg');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
