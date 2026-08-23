// pw-leskaart.js (22 aug, v23.169) — zegt de leskaart vanaf dag 2 alleen nog wat je gaat doen?
//
// WAAROM DIT ER IS
//
// Stefan, 22 aug, met zijn dagles open op dag 32. Vier regels op de leskaart, en hij noemt ze één
// voor één:
//
//   "Sin prisa, pero sin pausa."                 -> "we zouden Chispa zuiniger inzetten"
//   "Elke dag raak je alle vier de manieren aan" -> "deze zin is maar een keer nuttig om te lezen"
//   "Je route: ..., nog 3 stappen."              -> "dit snap ik niet? waarom zit ik in deze route?"
//   "Daarna mag je Chispa la tortilla geven."    -> "dit zegt me niet zoveel"
//
// Het is één fout en geen vier. Alle vier leggen ze op dag 1 iets uit en zijn ze vanaf dag 2
// behang: wie Chispa is, waarom je plan eruitziet zoals het eruitziet, dat er een beloning bestaat,
// dat er een route loopt. Stefan heeft ze alle vier ongeveer dertig keer gelezen.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. OP DAG 1 STAAT DE INTRODUCTIE ER. Dit is de helft die het makkelijkst per ongeluk sneuvelt
//      als iemand later "die regel kan ook weg" denkt. Een nieuwe gebruiker heeft geen idee wie dat
//      diertje is en waarom hij taco's krijgt.
//   2. EN VANAF DAG 2 NIET MEER. Vier regels, vier keer afwezig, elk apart benoemd, zodat je uit de
//      uitslag kunt lezen wélke er is teruggeslopen.
//   3. WAT JE GAAT DOEN BLIJFT WEL STAAN. Het controlegeval, en het is het halve punt van deze
//      versie: er is geknipt in de uitleg eromheen en niet in het plan zelf. Blijft het dagplan of
//      de startknop weg, dan is dit geen opgeruimde kaart maar een lege.
//   4. DE ROUTE IS NIET WEG, HIJ IS VERHUISD. Hij loopt door als de grammaticastap van je dagles en
//      staat ná je les nog als voorstel. Alleen de aankondiging vooraf is weg, plus de knop die je
//      uit je dag naar de Grammatica-tab bracht.
//   5. EEN ONAFGEMAAKTE LES WINT VAN EEN GEHAALD DAGDOEL. Stefan, 22 aug, op stap 4 van 6: "ik moet
//      op pauzeer klikken en toen zei het lesje dat ik al klaar was, wat niet zo is, ik heb niet
//      gelezen of geschreven." Twee dingen heetten allebei "klaar" en de kaart geloofde de
//      verkeerde: S.dag.klaar (je dagdoel in XP, kan halverwege je les afgaan) verdrong
//      S.lesFlowNu (je les staat open op stap 4). Gevolg: kicker "Klaar voor vandaag", alle zes de
//      blokken afgevinkt, en geen knop meer terug naar je eigen les.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwLk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    function foto() {
      show('lessen', true); renderLessons();
      const t = document.getElementById('lessonList').textContent.replace(/\s+/g, ' ');
      return {
        tekst: t,
        /* 23 aug (nachtrun): /Sin prisa/ was dag-afhankelijk rood. De groet komt uit
           chispaGroet() = CHISPA_GROET[dayHash("groet") % 8], en "Sin prisa, pero sin pausa."
           is maar één van de acht: de suite was alleen groen op dagen dat de rotatie precies
           die koos (zelfde klasse als pw-nav215 op 22 aug en pw-schrijven op 21 aug).
           Nu: vraag de app zelf welke groet vandaag geldt en zoek díe in de kaarttekst.
           Dag 32 gebruikt dezelfde foto(), dus ook de afwezigheids-check blijft kloppen. */
        spreuk: t.indexOf(chispaGroet().es) !== -1,
        draden: /alle vier de manieren/.test(t),
        route: /Je route/.test(t) || !!document.getElementById('btnRouteDag'),
        tapa: /mag je Chispa/.test(t) || /iets lekkers geven/.test(t),
        // en wat er wél hoort te staan
        plan: !!document.getElementById('dagPlan') || /min/.test(t),
        start: !!document.getElementById('btnStartLesFlow'),
        chispaKnop: !!document.getElementById('btnRitmeChispa')
      };
    }

    // ---- dag 1 ----
    S.dagen = { count: 1, last: today() };
    uit.dag1 = foto();

    // ---- dag 32, de stand van Stefan ----
    S.dagen = { count: 32, last: today() };
    uit.dag32 = foto();

    /* ---- 5. halverwege je les, met het dagdoel al gehaald ----
       Precies de stand van Stefan: stap 4 van 6 opgeslagen, dagdoel afgevinkt, les niet af. */
    function kaartFoto() {
      show('lessen', true); renderLessons();
      const kick = document.querySelector('#lessonList .kicker');
      return {
        kicker: kick ? kick.textContent.replace(/\s+/g, ' ') : '',
        hervatKnop: !!document.getElementById('btnStartLesFlow'),
        vinkjes: document.querySelectorAll('#lessonList .dagblok .op, #lessonList .dagblokaf').length
          || (document.getElementById('lessonList').textContent.match(/✓/g) || []).length
      };
    }
    S.dagen = { count: 32, last: today() };
    S.dag = S.dag || {}; S.dag.klaar = today();          // dagdoel gehaald, feestscherm weggeklikt
    S.lesFlow = {};                                       // maar de les is niet af
    S.lesFlowNu = { d: today(), stap: 'toetsjes',
                    stappen: ['woorden','grammatica','vormen','toetsjes','input','produceren'] };
    uit.halverwege = kaartFoto();

    // en het controlegeval: een les die wél af is
    S.lesFlow[today()] = true;
    S.lesFlowNu = null;
    uit.echtAf = kaartFoto();
    S.dag.klaar = '';

    // ---- 4. de route is verhuisd, niet weg ----
    uit.routeStandBestaat = (function () { try { return typeof routeStand === 'function'; } catch (e) { return false; } })();
    uit.voorstelBestaat = (function () { try { return typeof routeVoorstel === 'function'; } catch (e) { return false; } })();
    uit.regelWeg = (typeof routeRegelHtml === 'undefined') && (typeof routeRegelWire === 'undefined');
    /* En de reden staat nog steeds waar hij hoort: in de les zelf. Dit is het antwoord op Stefans
       "waarom zit ik in deze route?", en het stond er al sinds v23.143, alleen twee schermen
       verderop dan de aankondiging. */
    uit.waarom = (function () {
      try {
        const c = gcGeordend()[0];
        return c ? gramWaaromHtml('concept-' + c.id) : '';
      } catch (e) { return 'FOUT: ' + e.message; }
    })();
    return uit;
  });

  console.log('\n-- 1. op dag 1 staat de introductie er --');
  ok(r.dag1.spreuk, 'Chispa stelt zich voor');
  ok(r.dag1.tapa, 'en er staat wat je na je les mag doen');
  ok(r.dag1.start, 'met een startknop');

  console.log('\n-- 2. en vanaf dag 2 niet meer --');
  ok(!r.dag32.spreuk, 'geen spreuk van Chispa meer');
  ok(!r.dag32.draden, 'geen uitleg meer over de vier manieren');
  ok(!r.dag32.route, 'geen routeregel en geen knop die je uit je dag haalt');
  ok(!r.dag32.tapa, 'geen aankondiging van de tapa meer');

  console.log('\n-- 3. het controlegeval: wat je gaat doen blijft staan --');
  console.log('   "' + r.dag32.tekst.slice(0, 120) + '"');
  ok(r.dag32.start, 'de startknop staat er');
  ok(r.dag32.plan, 'en je dagplan ook');
  ok(r.dag32.chispaKnop, 'en Chispa zelf staat er nog, als knop: zuiniger is niet weg');
  ok(r.dag32.tekst.length > 60, 'de kaart is opgeruimd en niet leeg (' + r.dag32.tekst.length + ' tekens)');

  console.log('\n-- 4. de route is verhuisd, niet weg --');
  console.log('   waarom in de les: "' + r.waarom + '"');
  ok(r.regelWeg, 'de regel op het dagscherm bestaat niet meer als functie');
  ok(r.routeStandBestaat && r.voorstelBestaat, 'maar de route en zijn voorstel na de les wel');
  ok(!!r.waarom && r.waarom.indexOf('FOUT') !== 0,
    'en in de les staat waaróm je dit onderwerp krijgt, wat de aankondiging nooit zei');

  console.log('\n-- 5. een onafgemaakte les wint van een gehaald dagdoel --');
  console.log('   kicker: "' + r.halverwege.kicker + '"');
  ok(r.halverwege.hervatKnop, 'de knop terug naar je les staat er');
  ok(/stap 4/i.test(r.halverwege.kicker), 'en de kaart zegt waar je gebleven was (' + r.halverwege.kicker + ')');
  ok(!/Klaar voor vandaag/.test(r.halverwege.kicker), 'hij beweert niet dat je klaar bent');
  ok(r.halverwege.vinkjes < 6, 'en vinkt niet alle zes de blokken af (' + r.halverwege.vinkjes + ')');

  console.log('\n   het controlegeval: een les die wél af is, is ook echt af');
  ok(!r.echtAf.hervatKnop, 'geen knop terug naar een les die af is');
  ok(/Klaar voor vandaag/.test(r.echtAf.kicker), 'en dan zegt de kaart dat wel (' + r.echtAf.kicker + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
