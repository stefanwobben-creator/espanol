// pw-doorknop.js (26 aug, v23.197) — de knop die je aankijkt is de knop die werkt
//
// WAAROM DEZE SUITE ER IS
//
// Stefan liep drie keer vast op dezelfde plek: 23, 24 en 26 augustus, telkens op de uitslag van het
// toetsje in zijn dagles. "Door →" deed niets.
//
// De oorzaak was geen dode knop maar de verkeerde knop. Vier schermen tekenden er een met hetzelfde
// id (btnLesFlowDoor), en drie daarvan wonen in tab-speeltuin, dat in de pagina vóór tab-toetsjes
// staat. show() verbergt een tabblad zonder de inhoud weg te gooien, dus de knop van de vormenstap
// bleef staan. document.getElementById() geeft de eerste in de pagina, en dus kreeg de onzichtbare
// knop de klikafhandeling en die op het scherm geen enkele.
//
// Nagemeten vóór de reparatie: twee knoppen met dat id, handler op de oude, geen op de zichtbare.
//
// Het was dag-afhankelijk (alleen als er een vormenblok in je dagles zit) en daarom leek het "soms".
// De bodem van v23.188 kon het niet vangen: die vraagt "is er een scherm opengegaan", en er werd
// helemaal niets aangeroepen. Een bodem onder een functie die nooit begint, ligt verkeerd.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE ZICHTBARE DOOR-KNOP HEEFT EEN KLIKAFHANDELING, in precies de volgorde die stukging: eerst
//      een scherm dat een knop achterlaat, dan de toetsuitslag. Dit is de eigenlijke regel.
//   2. EN HIJ BRENGT JE VERDER. Controlegeval bij 1: een knop met een lege functie eraan haalt proef
//      1 wel en helpt niemand.
//   3. GEEN ENKEL ID KOMT TWEE KEER VOOR, op elke stap van de dagles. Dat is de algemene regel waar
//      deze bug een geval van was, en die meet ook de plekken die niemand heeft bekeken.
//   4. CONTROLEGEVAL BIJ 3: de meting vindt een dubbel id wél als je er een neerzet.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 1 en 2. de volgorde die stukging ----
  console.log('\n-- 1 en 2. een achtergebleven knop mag de zichtbare niet kapen --');
  /* De vormenstap draait niet elke dag, en een proef die van de datum afhangt meet op de meeste
     dagen niets. Daarom wordt de situatie hier nagebouwd in plaats van afgewacht: de speeltuin
     krijgt de knop die die stap achterlaat, en dán rendert de toetsuitslag. Dat is precies de
     toestand van Stefans scherm. */
  const r = await page.evaluate(() => {
    (tLessons() || []).forEach(function (l) {
      S.lessons[l.id] = { done: true, woorden: true, zinnen: true, quiz: true, spiek: true };
    });
    try { persist(); } catch (e) {}

    lesFlowStart();
    lesFlow.stap = 'vormen';
    lesFlowVolgende();                       // → toetsjes, en startQuiz()

    // de knop die de vormenstap achterlaat, in het tabblad dat vóór de toetsjes staat
    const sp = document.getElementById('tab-speeltuin');
    sp.innerHTML = "<div class='card'>" + lesFlowDoorHtml() + '</div>';
    let gekaapt = 0;
    sp.querySelectorAll('.lesflow-door').forEach(function (b) { b.onclick = function () { gekaapt++; }; });

    // en nu de toets uitspelen, zoals Stefan deed
    let n = 0;
    while (document.querySelector('#qCard .opt') && n++ < 40) {
      const oi = qState.volgorde[qState.i].oi;
      document.querySelectorAll('#qCard .opt')[qState.qz.vragen[oi].c].click();
      const nb = document.getElementById('btnNextQ');
      if (nb) nb.click(); else break;
    }

    const kaart = document.getElementById('qCard');
    const knop = kaart ? kaart.querySelector('.lesflow-door') : null;
    const stapVoor = lesFlow && lesFlow.stap;
    const opendeVoor = lesFlowOpende;
    if (knop) knop.click();
    return {
      knopOpDeKaart: !!knop,
      heeftHandler: !!(knop && knop.onclick),
      knoppenInDePagina: document.querySelectorAll('.lesflow-door').length,
      gekaapt: gekaapt,
      stapVoor: stapVoor,
      stapNa: lesFlow && lesFlow.stap,
      schermGing: lesFlowOpende > opendeVoor
    };
  });
  console.log('   ' + JSON.stringify(r));
  ok(r.knopOpDeKaart, 'de toetsuitslag heeft een Door-knop');
  ok(r.heeftHandler, 'en die knop heeft een klikafhandeling (dit was de bug)');
  ok(r.knoppenInDePagina >= 2,
    'CONTROLE: en er stond wel degelijk een tweede knop in de pagina (' + r.knoppenInDePagina + '), anders bewijst dit niets');
  ok(r.gekaapt === 0, 'CONTROLE: de klik ging niet naar de achtergebleven knop (' + r.gekaapt + ' keer)');
  ok(r.stapNa !== r.stapVoor && r.schermGing,
    'en de les gaat verder: ' + r.stapVoor + ' → ' + r.stapNa + (r.schermGing ? ', met een nieuw scherm' : ', zonder scherm'));

  // ---- 3 en 4. geen enkel id twee keer, op elke stap ----
  console.log('\n-- 3 en 4. geen dubbele id\'s door de hele dagles heen --');
  const dubbelOp = async () => page.evaluate(() => {
    const gezien = {}, dubbel = [];
    document.querySelectorAll('[id]').forEach(function (e) {
      const i = e.id;
      if (!i) return;
      if (gezien[i]) { if (dubbel.indexOf(i) < 0) dubbel.push(i); }
      gezien[i] = 1;
    });
    return { dubbel: dubbel, totaal: Object.keys(gezien).length,
             stap: lesFlow && lesFlow.stap };
  });

  /* opnieuw beginnen, want proef 1 heeft de les al tot voorbij het toetsje gespeeld en dan blijven
     er twee stappen over. De regel geldt voor de hele les, dus die wordt ook helemaal doorlopen. */
  await page.evaluate(() => { try { lesFlowKlaar(); } catch (e) {} lesFlowStart(); });
  await page.waitForTimeout(400);

  const stappen = [];
  for (let k = 0; k < 10; k++) {
    const d = await dubbelOp();
    stappen.push(d);
    console.log('   stap "' + d.stap + '": ' + d.totaal + ' id\'s, ' + (d.dubbel.length ? 'DUBBEL: ' + d.dubbel.join(',') : 'geen dubbele'));
    const verder = await page.evaluate(() => {
      if (!lesFlow) return false;
      /* staat er een toets open, speel hem uit: anders draait de lus acht keer op dezelfde stap en
         meet proef 3 één scherm in plaats van de hele les. */
      let n = 0;
      while (document.querySelector('#qCard .opt') && n++ < 40) {
        const oi = qState.volgorde[qState.i].oi;
        document.querySelectorAll('#qCard .opt')[qState.qz.vragen[oi].c].click();
        const nb = document.getElementById('btnNextQ');
        if (nb) nb.click(); else break;
      }
      const tabs = TABS.filter(function (t) { return !document.getElementById('tab-' + t.id).classList.contains('hidden'); });
      const el = tabs.length ? document.getElementById('tab-' + tabs[0].id) : null;
      const b = el && el.querySelector('.lesflow-door');
      if (b) { b.click(); return true; }
      try { lesFlowVolgende(); return !!lesFlow; } catch (e) { return false; }
    });
    await page.waitForTimeout(500);
    if (!verder) break;
  }
  const metDubbel = stappen.filter(function (s) { return s.dubbel.length; });
  ok(metDubbel.length === 0,
    'geen enkele stap heeft een dubbel id (' + (metDubbel.map(function (s) { return s.stap + ': ' + s.dubbel.join(','); }).join(' · ') || 'geen') + ')');
  /* niet alleen "genoeg rondjes" maar "genoeg verschillende stappen": acht keer dezelfde stap
     bekijken is één meting die er acht uitziet. */
  const uniek = stappen.map(function (s) { return s.stap; }).filter(function (v, i, a) { return a.indexOf(v) === i; });
  ok(uniek.length >= 4 && stappen.some(function (s) { return s.totaal > 40; }),
    'CONTROLE: en de les is echt doorlopen (' + uniek.join(' → ') + ', tot ' +
    Math.max.apply(null, stappen.map(function (s) { return s.totaal; })) + " id's)");

  const vindt = await page.evaluate(() => {
    const d = document.createElement('div');
    d.id = 'qCard';                       // een id dat gegarandeerd al bestaat
    document.body.appendChild(d);
    const gezien = {}; let dubbel = false;
    document.querySelectorAll('[id]').forEach(function (e) { if (gezien[e.id]) dubbel = true; gezien[e.id] = 1; });
    d.remove();
    return dubbel;
  });
  ok(vindt, 'CONTROLE: de meting vindt een dubbel id wel als je er een neerzet');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
