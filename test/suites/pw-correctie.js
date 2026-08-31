// pw-correctie.js (22 aug, v23.168) — krijg je te zien wat er mis was, en blijft het buiten je dossier?
//
// WAAROM DIT ER IS
//
// Stefan, 22 aug, over de vraag van de dag: "deze is leuk maar hij corrigeert niet mijn fout."
// Gemeten in dagZinBij(): afknippen op 140 tekens, opslaan, +4 XP, naar de groep. Geen check, geen
// AI-aanroep, geen fout gelogd. Zijn zin stond ongecorrigeerd bij zijn groep op het scherm.
//
// En bij de zinnen stond het andersom scheef: bij een fout antwoord verscheen de goede zin met de
// afwijkende woorden onderstreept, maar jouw eigen zin was op dat moment al van het scherm. Je zag
// dus wat het moest zijn zonder te zien wat jij schreef.
//
// DE KAART ERACHTER, EN WAT ER NIET GEBOUWD IS
//
// Dit is de eerste ronde onder de leerpoort. De eerste versie van de kaart stelde een raadronde
// voor: fout aanwijzen, niet verbeteren, één nieuwe poging. Die is aangevallen en gesneuveld op
// vier punten, waarvan twee hier het vermelden waard zijn omdat ze bepalen wat deze suite bewaakt:
//
//   - Truscott & Hsu 2008 heeft dat ontwerp al uitgevoerd. Beter in de revisie, en een week later
//     op een nieuwe tekst gelijk aan de controlegroep.
//   - Taalmodellen halen op grammaticacorrectie ruwweg 52 tot 59 procent precisie, met
//     overcorrectie als bekend gedrag. Bij vrije A2-productie is veel van wat "fout" heet geen
//     fout. Een gemiste fout kost bijna niets; een verzonnen fout zou weken in de herhaalwachtrij
//     worden gedrild.
//
// Wat er wel staat is de goedkoopste ingreep met bewijs: dezelfde informatie zichtbaarder maken
// (Leeman 2003), plus één actieve stap.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. JE ZIET WAT JIJ SCHREEF NAAST WAT ER HOORDE. Aan beide kanten gemarkeerd, want een
//      markering aan één kant laat het verschil nog steeds aan jou over.
//   2. OVERTYPEN IS EEN AANBOD EN GEEN POORT. Het blok staat er, én de knop naar de volgende zin
//      staat er. Een verplichte stap na elke fout maakt fout maken duurder, en dat beloont
//      voorzichtig schrijven. Het levert ook geen XP op, want dan zou overtypen gaan lonen boven
//      het meteen goed hebben.
//   3. DE FOUT KRIJGT EEN IDENTITEIT. Niet "zin s142 ging fout" maar "waar 'es' hoorde stond
//      'está'". Zonder dat is "maak ik deze fout vaker" onbeantwoordbaar, en dan is de meting die
//      moet uitwijzen of deze hele laag iets doet niet te maken.
//   4. HET CONTROLEGEVAL: EEN MODELOORDEEL BLIJFT BUITEN JE DOSSIER. Het komt in beeld, en het
//      zet niets in S.errors. Dit is de regel die het precisieprobleem hierboven afvangt, en het
//      is precies het soort regel dat later per ongeluk wordt omgedraaid omdat "die fouten zijn
//      toch nuttig".
//
//      v23.222: dit werd gemeten op de vraag van de dag, en die bestaat niet meer. Het gesprek met
//      Chispa doet hetzelfde: chatStuur() zet res.naast onder jouw beurt. Dat is nu de plek waar
//      een model iets over je Spaans zegt, dus daar hoort dit controlegeval. En het is de betere
//      plek, want dit blok zit in je dagles en de vraag van de dag stond ernaast.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwCo' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 1 t/m 3. de zin ----
  const zin = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    /* Een zin die ver genoeg naast het antwoord ligt om in de foute tak te vallen, niet in de
       bijna-tak: die laatste roept /api/ai/check aan en dat willen we hier niet meten. De foute tak
       is ook de tak waarin Stefan het vaakst terechtkomt. */
    show('vertalen', true);
    renderSentence(true);
    /* renderSentence(true) kiest zelf de volgende zin, dus sIdx staat pas ná die aanroep vast. Hem
       vooraf zetten en daarna renderen levert een suite op die een andere zin meet dan het scherm
       toont, en dan meet je niets. */
    const s = sIdx;
    zinGeteld = false; vertWacht = false;

    const inp = document.getElementById('sInput');
    // elk woord anders, zodat bestDiff niet in de bijna-tak belandt
    const mis = s.es.split(' ').map(function () { return 'xxx'; }).join(' ');
    inp.value = mis;
    uit.jouw = mis;
    uit.goed = s.es;
    const xpVoor = S.txp || 0;
    checkSentence();

    const fb = document.getElementById('sFeedback');
    const vgl = fb.querySelector('.zinvgl');
    uit.vglErIs = !!vgl;
    if (vgl) {
      const rijen = vgl.querySelectorAll('.zinvglrij');
      uit.rijen = rijen.length;
      uit.labels = Array.prototype.map.call(rijen, function (r) {
        return (r.querySelector('.zinvgllbl') || {}).textContent || '';
      });
      uit.jouwRij = rijen[0] ? rijen[0].textContent.replace(/\s+/g, ' ') : '';
      uit.goedRij = rijen[1] ? rijen[1].textContent.replace(/\s+/g, ' ') : '';
      uit.markJouw = rijen[0] ? rijen[0].querySelectorAll('.diffmis').length : 0;
      uit.markGoed = rijen[1] ? rijen[1].querySelectorAll('.diffword').length : 0;
    }

    // overtypen: aanbod, geen poort
    uit.overtypBlok = !!document.getElementById('sOverTyp');
    uit.volgendeStaatErOok = !!document.getElementById('btnNext');
    const xpNa = S.txp || 0;
    const iot = document.getElementById('sOverTyp');
    if (iot) {
      iot.value = s.es;
      document.getElementById('btnOverTyp').click();
      uit.overtypFb = (document.getElementById('overTypFb') || {}).textContent || '';
      uit.overtypGeslotenNaGoed = iot.disabled === true;
    }
    uit.xpDoorOvertypen = (S.txp || 0) - xpNa;
    uit.xpDoorFout = xpNa - xpVoor;

    // en nu: wat weet het foutenlogboek?
    const k = 'zin:' + s.id;
    const e = S.errors[k];
    uit.foutErIs = !!e;
    uit.paren = e && e.paren ? e.paren : null;
    return uit;
  });

  console.log('\n-- 1. je ziet wat jij schreef naast wat er hoorde --');
  console.log('   jij:  ' + zin.jouwRij);
  console.log('   goed: ' + zin.goedRij);
  ok(zin.vglErIs, 'de vergelijking staat er');
  ok(zin.rijen === 2, 'twee regels, jouw zin en de goede (' + zin.rijen + ')');
  ok(/Jij/.test(zin.labels ? zin.labels[0] : ''), 'de bovenste is die van jou');
  ok(zin.markJouw > 0, 'jouw afwijkende woorden zijn gemarkeerd (' + zin.markJouw + ')');
  ok(zin.markGoed > 0, 'en de goede woorden ook (' + zin.markGoed + ')');

  console.log('\n-- 2. overtypen is een aanbod, geen poort --');
  console.log('   "' + zin.overtypFb + '"');
  ok(zin.overtypBlok, 'het overtypblok staat er na een fout antwoord');
  ok(zin.volgendeStaatErOok, 'en de knop naar de volgende zin staat er óók, dus je kunt eromheen');
  ok(zin.overtypGeslotenNaGoed === true, 'goed overgetypt wordt bevestigd');
  ok(zin.xpDoorOvertypen === 0, 'en het levert geen XP op (' + zin.xpDoorOvertypen + ')');

  console.log('\n-- 3. de fout krijgt een identiteit --');
  console.log('   ' + JSON.stringify(zin.paren));
  ok(zin.foutErIs, 'de fout staat in het logboek');
  ok(!!zin.paren && zin.paren.length > 0, 'met erbij welk woord er hoorde en wat jij schreef');
  ok(!!zin.paren && zin.paren.every(function (p) { return p.v && p.g; }),
    'en beide kanten van dat paar zijn ingevuld');
  ok(!!zin.paren && zin.paren.length <= 4, 'hoogstens vier paren, want dit staat in localStorage');

  // ---- 4. het gesprek met Chispa ----
  const dag = await page.evaluate(async () => {
    const uit = {};
    S.lang = 'nl';
    S.chat = null;

    /* De aanroep wordt onderschept, want deze suite gaat over wat de app met het antwoord doet en
       niet over of het model bereikbaar is. Het antwoord is met opzet een correctie die ergens op
       slaat, zodat punt 4 iets te controleren heeft. */
    const echt = window.api;
    let geroepen = null;
    window.api = function (pad, methode, body) {
      if (pad === '/api/ai/chat') {
        geroepen = body;
        return Promise.resolve({ ok: true, naast: 'Je schreef "he reíando", en dat moet "me hizo reír" zijn.', es: 'Qué bien.', nl: 'Wat goed.' });
      }
      return Promise.resolve({ ok: true });
    };

    show('chat', true);
    try { renderChat(); } catch (e) { uit.tekenFout = e.message; }
    const inp = document.getElementById('chatInvoer');
    uit.veld = !!inp;
    const xpVoor = S.txp || 0;
    const foutenVoor = Object.keys(S.errors).length;
    if (inp) {
      inp.value = 'he reíando qué una video';
      document.getElementById('chatStuur').click();
      uit.direct = document.getElementById('chatWrap').textContent.replace(/\s+/g, ' ');
      await new Promise(function (r) { setTimeout(r, 250); });
      uit.na = document.getElementById('chatWrap').textContent.replace(/\s+/g, ' ');
    }
    uit.geroepen = geroepen;
    uit.xpVerschil = (S.txp || 0) - xpVoor;
    uit.foutenErbij = Object.keys(S.errors).length - foutenVoor;
    uit.bewaard = (chatStand().beurten || []).some(function (b) { return b.van === 'jij' && b.naast; });
    window.api = echt;
    return uit;
  });

  console.log('\n-- 4. je zin in het gesprek krijgt een oordeel --');
  ok(!dag.tekenFout, 'het gespreksscherm tekent' + (dag.tekenFout ? ': ' + dag.tekenFout : ''));
  ok(dag.veld, 'het invoerveld staat er');
  ok(!!dag.geroepen && dag.geroepen.modus === 'gesprek', 'je zin gaat langs de check');
  ok(/Chispa denkt na/.test(dag.direct || ''), 'meteen na het versturen staat er dat ze ernaar kijkt');
  ok(/moet "me hizo reír" zijn/.test(dag.na || ''), 'en daarna staat het oordeel onder je eigen zin');
  ok(dag.bewaard, 'het wordt bewaard, dus een hertekening gooit het niet weg');

  console.log('\n   het controlegeval: en verder verandert er niets aan je dossier');
  ok(dag.foutenErbij === 0, 'er komt niets in je foutenlogboek (' + dag.foutenErbij + ' erbij)');
  ok(dag.xpVerschil === 3, 'de XP is die van het versturen en niet meer of minder (' + dag.xpVerschil + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
