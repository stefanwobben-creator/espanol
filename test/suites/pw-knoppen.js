// pw-knoppen.js (23 aug, v23.180) — één primaire knop na een fout, en geen undefined op de opfrisser
//
// WAAROM DIT ER IS
//
// Twee schermafdrukken van Stefan op 23 augustus.
//
//   1. "dit lijkt een bug 'undefined'" — op de opfrisser stond letterlijk "undefined Even
//      opfrissen". renderGramWiz() zet o.icon vóór de stapkop en de opfris-bouwer maakte een
//      onderwerp zonder icon-veld.
//   2. "hier zijn veel te veel knoppen opties voor een lekkere flow" — na een fout antwoord op de
//      schrijfstap stonden er zes bedieningen, waarvan twee primair gekleurd.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. GEEN ONDEFINEERD VELD OP HET SCHERM. Niet alleen bij de opfrisser: nergens in de microles.
//      Dit is de goedkoopste regel met de meeste dekking, en hij was er niet.
//   2. DE OPFRISSER DRAAGT HET ICOON VAN ZIJN CONCEPT. Het controlegeval bij punt 1: de regel
//      hierboven is ook te halen door het icoon overal weg te laten, en dan is de kop kaler dan hij
//      hoort te zijn.
//   3. NA EEN FOUT IS ER PRECIES ÉÉN PRIMAIRE KNOP. Twee primaire knoppen is geen keuze maar een
//      menu.
//   4. EN NIETS IS WEGGEHAALD. Probeer opnieuw, de AI-check en de foutregel staan er nog, achter
//      "meer opties". Dit is het controlegeval bij punt 3: minder knoppen is triviaal te halen door
//      ze te slopen, en dan verlies je paden die iemand gebruikt.
//   5. GOED OVERGETYPT GAAT DOOR NAAR DE VOLGENDE ZIN. De afspraak van v23.60, die nog niet gold
//      voor het overtypvak van v23.168.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwKn' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 1 en 2. de opfrisser ----
  const opfris = await page.evaluate(() => {
    S.lang = 'nl';
    const uit = { kaal: [], zonderIcoon: [] };
    gcGeordend().forEach(function (c) {
      // v23.191: gcGebouwd() is sindsdien de enige weg naar een gebouwd onderwerp.
      const o = gcGebouwd(gcOpfrisId(c.id));
      if (!o) return;
      if (!o.icon) uit.zonderIcoon.push(c.id);
      if (o.icon !== c.icon) uit.kaal.push(c.id + ' (' + o.icon + ' tegenover ' + c.icon + ')');
    });
    // en het echte scherm van één opfrisser
    const c = gcGeordend()[0];
    lesFlow = null;
    gwSess = null;
    gwStart(gcOpfrisId(c.id));
    show('spiekbrief', true);
    renderCheat();
    uit.scherm = (document.getElementById('cheat').textContent || '').replace(/\s+/g, ' ').slice(0, 90);
    return uit;
  });
  console.log('\n-- 1 en 2. de opfrisser --');
  console.log('   ' + opfris.scherm);
  ok(!/undefined/i.test(opfris.scherm), 'er staat geen "undefined" op het scherm');
  ok(opfris.zonderIcoon.length === 0, 'elke opfrisser heeft een icoon (mist: ' + (opfris.zonderIcoon.join(', ') || 'niets') + ')');
  ok(opfris.kaal.length === 0, 'en het is het icoon van zijn eigen concept (' + (opfris.kaal.slice(0, 3).join(' · ') || 'alle gelijk') + ')');

  // ---- de bredere regel: nergens undefined in een microles ----
  const alle = await page.evaluate(() => {
    const stuk = [];
    gcGeordend().forEach(function (c) {
      ['concept-' + c.id, gcOpfrisId(c.id)].forEach(function (id) {
        let o = null;
        try { o = gwOnderwerp(id); } catch (e) { o = null; }
        if (!o) return;
        const tekst = JSON.stringify({ t: o.titel, i: o.icon, p: o.pitch,
          k: (o.stappen || []).map(function (s) { return [s.kop, s.uitleg]; }) });
        if (/undefined|\[object Object\]/.test(tekst)) stuk.push(id);
      });
    });
    return stuk;
  });
  ok(alle.length === 0, 'geen enkel onderwerp draagt undefined in kop, titel of uitleg (' + (alle.slice(0, 4).join(', ') || 'geen') + ')');

  /* ---- 3, 4 en 5. de schrijfstap na een fout ----
     Zelfde aanpak als pw-correctie: renderSentence(true) kiest zélf de zin, dus sIdx staat pas ná
     die aanroep vast, en het antwoord gaat rechtstreeks in het veld. Vooraf een zin kiezen levert
     een suite op die iets anders meet dan er op het scherm staat. */
  const knop = await page.evaluate(() => {
    show('vertalen', true);
    renderSentence(true);
    const s = sIdx;
    zinGeteld = false; vertWacht = false;
    const inp = document.getElementById('sInput');
    inp.value = s.es.split(' ').map(function () { return 'xxx'; }).join(' ');
    checkSentence();

    const kaart = document.getElementById('tab-vertalen') || document.body;
    const zichtbaar = function (el) {
      const d = el.closest('details');
      return !(d && !d.open);
    };
    const alle = Array.prototype.slice.call(kaart.querySelectorAll('button'));
    return {
      es: s.es,
      primair: alle.filter(function (b) { return b.classList.contains('primary') && zichtbaar(b); })
        .map(function (b) { return b.textContent.trim(); }),
      zichtbaar: alle.filter(zichtbaar).map(function (b) { return b.textContent.trim(); }),
      verstopt: alle.filter(function (b) { return !zichtbaar(b); }).map(function (b) { return b.textContent.trim(); }),
      overtyp: !!document.getElementById('sOverTyp'),
      details: !!kaart.querySelector('details.meerOpties')
    };
  });
  console.log('\n-- 3 en 4. de knoppen na een fout --');
  console.log('   zichtbaar: ' + knop.zichtbaar.join(' | '));
  console.log('   achter meer opties: ' + knop.verstopt.join(' | '));
  ok(knop.overtyp, 'het overtypvak staat er (anders meet de rest niets)');
  ok(knop.primair.length === 1, 'precies één primaire knop (nu: ' + knop.primair.join(', ') + ')');
  ok(/Klaar/.test(knop.primair[0] || ''), 'en dat is de overtypknop (' + knop.primair[0] + ')');
  ok(knop.details, 'er is een "meer opties"-regel');
  ok(knop.verstopt.some(function (t) { return /Probeer opnieuw/.test(t); }),
    'CONTROLE: Probeer opnieuw is niet weg maar verplaatst');
  ok(knop.verstopt.some(function (t) { return /variant/.test(t); }),
    'CONTROLE: de AI-check ook');
  ok(knop.zichtbaar.some(function (t) { return /Volgende zin/.test(t); }),
    'en doorgaan zonder overtypen kan nog steeds');

  // 5. goed overtypen gaat door naar de volgende zin
  await page.fill('#sOverTyp', knop.es);
  await page.click('#btnOverTyp');
  await page.waitForTimeout(1600);
  const na = await page.evaluate(() => ({ nogOvertyp: !!document.getElementById('sOverTyp'),
                                          nuAnder: !!document.getElementById('sInput') }));
  console.log('\n-- 5. goed overgetypt gaat door --');
  ok(!na.nogOvertyp && na.nuAnder, 'het overtypvak is weg en er staat een nieuwe zin klaar');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
