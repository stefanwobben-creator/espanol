// pw-voorkant.js (22 aug, v23.167) — staat er vóór je les één ding op je dagscherm?
//
// WAAROM DIT ER IS
//
// Stefan, 22 aug: "we gaan tweaken terwijl het conceptueel nog niet helemaal klopt, dus we moeten
// grotere wijzigingen durven door te voeren." Gevraagd wat als eerste; gekozen: "de les wordt de
// app."
//
// Gemeten wat er stond: renderLessons() tekende zeven kaarten onder elkaar en de dagles was de
// eerste van zeven. Je uitnodiging voor een maatje, het nieuws van vandaag, de vraag van vandaag,
// de muur van je groep, je veertiendaagse strook, drie speltegels, en de installatiekaart. Dat is
// geen dagscherm maar een menu, en van de zeven kaarten waren er vijf leuker dan beginnen.
//
// Sinds v23.167 heeft de dag een voorkant en een achterkant: vóór je les staat er alleen je les,
// erna komt de rest terug.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. VÓÓR JE LES STAAT ER ÉÉN DING. Niet "minder dingen" maar precies dit: de leskaart en de
//      installatiekaart, en geen muur, geen spellen, geen strook, geen nieuws. Dit is de hele
//      beslissing, dus dit is wat rood hoort te worden als iemand er later een kaart bij zet.
//   2. EN HET IS ER NOG. Weghalen was niet de bedoeling; achter de les zetten wel. Zodra de les af
//      is hoort alles terug te zijn, en dat wordt hier geteld en niet aangenomen.
//   3. DE VRAAG VAN VANDAAG LANDT WAAR HET INVOERVELD STAAT. Het controlegeval, en het is de bug
//      die deze verbouwing zichtbaar maakte: het voorstel na de les deed show("perfil") terwijl
//      #dagzinInp op Vandaag staat. Die knop bracht je naar een scherm zonder invoerveld, en dat
//      kon niemand zien omdat niets de route naliep. Hier wordt hij nagelopen.
//
// WAT DEZE SUITE BEWUST NIET DOET
//
// Eisen dat de muur en de spellen onbereikbaar zijn vóór je les. Ze zijn het niet, en dat hoort:
// Spelen staat in de balk en de omweg mag bestaan. Wat niet mag is dat de omweg de eerste optie is,
// en dat is precies wat hier gemeten wordt.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwVk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    /* Een groep, anders bestaat de muur sowieso niet en zou punt 1 groen staan om de verkeerde
       reden: "de muur staat er niet" is geen meting als er nooit een muur is. muurGroep() leest
       S.groepen[0]; dit is precies wat samenMee() erin zet. */
    S.groepen = [{ gcode: 'PROEF1', naam: 'pw' }];
    /* En de muurdata er meteen bij. Zonder muurData tekent muurHtml() alleen "Even ophalen…" en
       laat het de vraag van vandaag weg; die haalt hij normaal van de server, en die is er hier
       niet. Zonder deze regel meet punt 2 dus de netwerkverbinding en niet de beslissing. */
    muurData = { ok: true, spelers: [] };
    muurGehaald = Date.now();

    function foto() {
      const el = document.getElementById('lessonList');
      const t = el.textContent.replace(/\s+/g, ' ');
      return {
        kaarten: el.querySelectorAll('.card').length,
        les: !!document.getElementById('btnStartLesFlow') || !!document.getElementById('btnLesOpnieuw') || !!document.getElementById('btnDagToch'),
        muur: !!document.getElementById('muurCard'),
        dagzin: !!document.getElementById('dagzinInp'),
        spellen: el.querySelectorAll('[data-speel]').length,
        lijn: !!document.getElementById('btnLijnMeer'),
        nieuws: el.querySelectorAll('[data-nwgo]').length,
        tekst: t.slice(0, 160)
      };
    }

    // ---- 1. de voorkant: les nog niet af ----
    S.lesFlow = {};
    show('lessen', true); renderLessons();
    uit.voor = foto();

    // ---- 2. de achterkant: les af ----
    S.lesFlow[today()] = true;
    renderLessons();
    uit.na = foto();

    // ---- 3. het controlegeval: waar landt "de vraag van vandaag" ----
    /* Niet nagerekend maar nagelopen: het voorstel wordt opgehaald zoals de app hem na de les
       toont, de knop wordt gedrukt, en daarna kijken we of het invoerveld waar hij naartoe wijst er
       ook echt staat. Dat is de enige vorm die deze bug had kunnen vangen. */
    S.dagzin = null;
    let v = null;
    try { v = lesFlowWinst(); } catch (e) { uit.winstFout = e.message; }
    uit.voorstelKop = v ? v.kop : null;
    if (v && /vraag van vandaag/i.test(v.kop || '')) {
      show('perfil', true);                 // eerst ergens anders heen, zodat de sprong iets doet
      try { v.doe(); } catch (e) { uit.doeFout = e.message; }
      uit.naSprong = {
        scherm: (function () {
          // show() verbergt elk #tab-<id> en haalt de hidden-klasse van precies één weg
          const uit = TABS.map(function (t) { return t.id; })
            .filter(function (id) {
              const el = document.getElementById('tab-' + id);
              return el && !el.classList.contains('hidden');
            });
          return uit.length === 1 ? uit[0] : uit.join('+') || null;
        })(),
        veld: !!document.getElementById('dagzinInp')
      };
    }
    return uit;
  });

  console.log('\n-- 1. vóór je les staat er één ding --');
  console.log('   ' + r.voor.kaarten + ' kaarten · "' + r.voor.tekst.slice(0, 90) + '"');
  ok(r.voor.les, 'je les staat er');
  ok(!r.voor.muur, 'de muur van je groep staat er niet');
  ok(!r.voor.dagzin, 'de vraag van vandaag staat er niet');
  ok(r.voor.spellen === 0, 'er staan geen speltegels (' + r.voor.spellen + ')');
  ok(!r.voor.lijn, 'je veertiendaagse strook staat er niet');
  ok(r.voor.nieuws === 0, 'en er staat geen nieuws dat je ergens anders heen stuurt (' + r.voor.nieuws + ')');

  console.log('\n-- 2. en na je les is alles er weer --');
  console.log('   ' + r.na.kaarten + ' kaarten');
  ok(r.na.kaarten > r.voor.kaarten, 'er komt echt iets bij (' + r.voor.kaarten + ' → ' + r.na.kaarten + ')');
  ok(r.na.muur, 'de muur is terug');
  ok(r.na.dagzin, 'de vraag van vandaag is terug');
  ok(r.na.spellen > 0, 'de speltegels zijn terug (' + r.na.spellen + ')');
  ok(r.na.lijn, 'je strook is terug');

  console.log('\n-- 3. het controlegeval: de vraag van vandaag landt op het invoerveld --');
  console.log('   voorstel: ' + (r.voorstelKop || 'geen'));
  if (r.naSprong) {
    ok(r.naSprong.scherm === 'lessen', 'de knop brengt je naar Vandaag (' + r.naSprong.scherm + ')');
    ok(r.naSprong.veld === true, 'en daar staat het invoerveld waar hij op mikt');
  } else {
    ok(false, 'het voorstel "de vraag van vandaag" kwam niet naar boven, dus de sprong is niet getest'
      + (r.winstFout ? ' (' + r.winstFout + ')' : ''));
  }

  ok(!r.doeFout, 'de knop klapt niet' + (r.doeFout ? ': ' + r.doeFout : ''));
  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
