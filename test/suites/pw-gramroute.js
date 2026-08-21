// pw-gramroute.js (21 aug, v23.159) — staat elk onderwerp precies één keer op de Grammatica-tab?
//
// WAAROM DIT ER IS
//
// Stefan, 21 aug: "De hele grammatica sectie voelt niet logisch."
//
// Gemeten op de tab van iemand die alle lessen af heeft (A2): 52 kaartjes onder drie koppen. "De
// keuzes" (23 concepten), "De diepe lessen" (5) en "Alle onderwerpen" (24). Die laatste kop ging
// over 24 van de 52, en dat is geen vage kop maar een onjuiste.
//
// En het stond er dubbel. "Ser of estar" als concept én als diepe les ("Ser vs. estar"), hetzelfde
// voor perfecto/indefinido en por/para. "Wisselt de klinker mee?" als concept én als
// spiekbriefkaart ("Schoenwerkwoorden"). De oorzaak lag in de data: gwGenLijst() reserveerde de
// kaarten die een handgeschreven wizard afdekt, maar niet die een concept afdekt, terwijl elk
// concept dat in zijn eigen spiek-veld heeft staan.
//
// En er ís een leervolgorde (GC_ORDE, met voorwaarden in GC_VOOR). Die was nergens te zien: de
// uitgeklapte lijst was een ongeordende muur van alleen wat open stond, met eronder "nog 20 komen
// later" zonder te zeggen welke of waarom.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. GEEN ENKEL ONDERWERP STAAT ER TWEE KEER. Niet als concept naast een diepe les met dezelfde
//      naam, en niet als concept naast de spiekbriefkaart die het afdekt.
//   2. DE UITGEKLAPTE LIJST IS DE ROUTE. Alle onderwerpen, in leervolgorde, genummerd.
//   3. INCLUSIEF DE GESLOTEN, MET DE REDEN ERBIJ. Verstoppen zonder te zeggen wat je verstopt is de
//      fout van v23.45; een slot zonder reden is dezelfde fout een laag dieper.
//   4. MAAR JE KUNT ER NIET IN. Het controlegeval: zichtbaar is niet hetzelfde als open, en een
//      slot dat toch klikt is erger dan geen slot.
//   5. DE KORTE OPENING BLIJFT. v20.7: hoogstens drie kaartjes, knop eronder, keuze onthouden. Deze
//      ronde mag die beslissing niet omduwen.
//   6. EN DE VOLGORDE IS OVERAL DEZELFDE. De vorige/volgende-knoppen op de leespagina liepen in
//      bestandsvolgorde en de tab in leervolgorde. Twee volgordes voor één rij.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwGr' + Date.now());
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

    // ---- 1. geen dubbelen, en dit meet de data, niet het scherm ----
    const tk = gwTrackKey();
    // welke spiekbriefkaarten dekt de route af?
    const doorRoute = {};
    GC_CONCEPTEN.forEach(function (c) { ((c.spiek && c.spiek[tk]) || []).forEach(function (i) { doorRoute[i] = c.id; }); });
    GRAMWIZ.forEach(function (o) { ((o.spiek && o.spiek[tk]) || []).forEach(function (i) { doorRoute[i] = o.id; }); });
    uit.genLekken = gwGenLijst().map(function (o) {
      const m = /^spiek-(?:a2|a0)-(\d+)$/.exec(o.id);
      return m && doorRoute[Number(m[1])] ? o.id + ' (al bij ' + doorRoute[Number(m[1])] + ')' : null;
    }).filter(Boolean);
    uit.genN = gwGenLijst().length;
    uit.diepLos = GRAMWIZ.filter(function (o) { return gcConceptOpen(o.id) && !gcConcept(o.id); }).map(function (o) { return o.id; });

    // ---- 2 t/m 4. de route op het scherm ----
    gwSess = null; gcLeesId = null;
    S.gcAlles = true;
    show('spiekbrief', true); renderCheat();
    const el = document.getElementById('cheat');
    const rijen = [...el.querySelectorAll('.gcroute')];
    uit.routeN = rijen.length;
    uit.ordeN = GC_ORDE.length;
    /* De naam vergelijken via textContent gaat mis: de begrippenuitlegger hangt bij sommige rijen
       een verklaring in het element ("gerundio: de -ndo-vorm ..."). Dus: begint de regel met dit
       onderwerp? Dat is precies de vraag en niets meer. */
    uit.opPlek = gcGeordend().map(function (c, i) {
      const b = rijen[i] && rijen[i].querySelector('.lbody b');
      return b && b.textContent.indexOf(c.icon + ' ' + c.naam) === 0 ? null : c.id;
    }).filter(Boolean);
    // een diepe les met een concept van dezelfde naam hoort niet als los kaartje op de tab
    uit.diepDubbel = [...el.querySelectorAll('[data-gwstart]')]
      .map(function (d) { return d.getAttribute('data-gwstart'); })
      .filter(function (id) { return !!gcConcept(id); });
    uit.nummers = rijen.map(function (d) { return d.querySelector('.lnum').textContent.trim(); });
    uit.open = rijen.filter(function (d) { return d.hasAttribute('data-gclees'); }).length;
    uit.opengeteld = gcLijst().length;
    // gesloten rijen: staan ze er, met een reden, en zijn ze niet klikbaar?
    const dicht = rijen.filter(function (d) { return !d.hasAttribute('data-gclees'); });
    uit.dichtN = dicht.length;
    uit.dichtGeteld = gcDichtAantal();
    uit.dichtZonderReden = dicht.filter(function (d) { return !d.querySelector('.lbody span').textContent.trim(); }).length;
    uit.dichtMetSlot = dicht.filter(function (d) { return d.querySelector('.lstatus').textContent.indexOf('🔒') !== -1; }).length;
    uit.slotRedenen = dicht.slice(0, 3).map(function (d) { return d.querySelector('.lbody span').textContent.trim(); });
    // en het cijfer blijft ook bij een slot staan, anders is de route niet te lezen
    uit.nummersOplopend = uit.nummers.every(function (n, i) { return n === '✓' || n === String(i + 1); });

    // de kop zegt wat er staat, en "Alle onderwerpen" is weg
    const tekst = el.textContent.replace(/\s+/g, ' ');
    uit.kopRoute = /De route/.test(tekst);
    uit.kopOud = /Alle onderwerpen|De keuzes|De diepe lessen/.test(tekst);
    uit.kopLessen = /Uit je lessen/.test(tekst);

    // ---- 5. het controlegeval: de korte opening blijft ----
    S.gcAlles = false; renderCheat();
    uit.kortKlikbaar = document.querySelectorAll('#cheat [data-gclees]').length;
    uit.kortRoute = document.querySelectorAll('#cheat .gcroute').length;
    uit.kortKnop = !!document.getElementById('gcToggleAlles');
    uit.kortReden = /nieuws|terugkomt|fout/.test(document.getElementById('cheat').textContent);
    document.getElementById('gcToggleAlles').click();
    uit.naKlik = { alles: S.gcAlles, route: document.querySelectorAll('#cheat .gcroute').length };
    document.getElementById('gcToggleAlles').click();
    uit.naTerug = { alles: S.gcAlles, klikbaar: document.querySelectorAll('#cheat [data-gclees]').length };

    // ---- 6. één volgorde, en de diepe les hangt aan zijn concept ----
    gcLeesOpen('serestar'); renderCheat();
    uit.lees = {
      diep: !!document.querySelector('#cheat [data-gwstart="serestar"]'),
      buren: [...document.querySelectorAll('#cheat [data-gclees]')].map(function (d) { return d.getAttribute('data-gclees'); })
    };
    const rij = gcGeordend().map(function (c) { return c.id; });
    const i = rij.indexOf('serestar');
    uit.verwachteBuren = [rij[i - 1], rij[i + 1]].filter(Boolean);
    // een concept zonder diepe les krijgt die knop niet
    gcLeesOpen('genero'); renderCheat();
    uit.geenDiep = !document.querySelector('#cheat [data-gwstart]');

    gcLeesSluit(); S.gcAlles = false;
    return uit;
  });

  console.log('\n-- 1. geen enkel onderwerp staat er twee keer --');
  console.log('   ' + r.genN + ' spiekbriefkaarten over, ' + r.diepLos.join(',') + ' apart uitgediept');
  ok(r.genLekken.length === 0, 'geen spiekbriefkaart die de route al afdekt (' + (r.genLekken.join('; ') || 'geen') + ')');
  ok(r.diepDubbel.length === 0, 'en geen diepe les als los kaartje naast zijn eigen concept (' + (r.diepDubbel.join(',') || 'geen') + ')');
  ok(r.diepLos.length > 0, 'wat echt naast de route staat blijft wel staan (' + r.diepLos.join(',') + ')');
  ok(!r.kopOud, 'de oude koppen zijn weg ("Alle onderwerpen" ging over 24 van de 52)');
  ok(r.kopRoute && r.kopLessen, 'en de koppen zeggen nu wat er staat');

  console.log('\n-- 2. de uitgeklapte lijst is de route --');
  ok(r.routeN === r.ordeN, 'alle ' + r.ordeN + ' onderwerpen staan erin (' + r.routeN + ')');
  ok(r.opPlek.length === 0, 'in leervolgorde, niet in bestandsvolgorde (' + (r.opPlek.join(',') || 'klopt') + ')');
  ok(r.nummersOplopend, 'genummerd, en het cijfer blijft ook bij een slot staan');
  ok(r.open === r.opengeteld, 'wat open staat klopt met de machine (' + r.open + ' van ' + r.routeN + ')');

  console.log('\n-- 3. inclusief de gesloten, met de reden erbij --');
  console.log('   ' + r.slotRedenen.join(' | '));
  ok(r.dichtN === r.dichtGeteld, 'de gesloten onderwerpen staan er allemaal (' + r.dichtN + ')');
  ok(r.dichtZonderReden === 0, 'en bij elk staat waarom (' + r.dichtZonderReden + ' zonder)');
  ok(r.dichtMetSlot === r.dichtN, 'met een slot ernaast');

  console.log('\n-- 4. het controlegeval: zichtbaar is niet open --');
  ok(r.open + r.dichtN === r.routeN, 'elke rij is óf klikbaar óf op slot, nooit allebei of geen van beide');

  console.log('\n-- 5. het controlegeval: de korte opening blijft (v20.7) --');
  ok(r.kortKlikbaar <= 3, 'de tab opent met hoogstens drie kaartjes (' + r.kortKlikbaar + ')');
  ok(r.kortRoute === 0, 'en dan staat de hele route er nog niet');
  ok(r.kortKnop && r.kortReden, 'met een knop en de reden waarom juist deze');
  ok(r.naKlik.alles === true && r.naKlik.route === r.ordeN, 'de knop klapt de route uit (' + r.naKlik.route + ')');
  ok(r.naTerug.alles === false && r.naTerug.klikbaar <= 3, 'en weer in, en die keuze wordt onthouden');

  console.log('\n-- 6. één volgorde, en de diepe les hangt aan zijn concept --');
  ok(r.lees.diep, 'de leespagina van ser/estar heeft een knop naar de diepe les');
  ok(r.geenDiep, 'het controlegeval: een concept zonder diepe les krijgt die knop niet');
  ok(JSON.stringify(r.lees.buren) === JSON.stringify(r.verwachteBuren),
    'en vorige/volgende volgen de route (' + r.lees.buren.join(',') + ' tegenover ' + r.verwachteBuren.join(',') + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
