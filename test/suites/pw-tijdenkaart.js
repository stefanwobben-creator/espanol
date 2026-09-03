// pw-tijdenkaart.js (3 sep, v23.233) — legt de app uit wat een tijd dóet, en zie je dat je vooruitgaat?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 3 sep: "de grammatica is lastig want ik weet gewoon ook nog niet zo goed wat presente, de
// subjuntivo, aanvoegende wijs, verleden tijd enzo allemaal is. Dus die basisregel ken ik nog niet,
// maar ik moet direct ook nog het juiste woord erbij kiezen (...) ik heb niet echt het gevoel dat ik
// door de oefeningen het beter word."
//
// Gemeten in zijn eigen logboek (tien opnames, txp 19381 tot 20937): van zijn 25 onderwerpen staan
// er negen op doos 5 en zestien op 0, 1 of 2. Op doos 3 en 4 staat er NUL. Het midden is leeg: er is
// geen enkel onderwerp dat onderweg is. En in datzelfde venster deed hij muymucho 75% goed terwijl
// de doos van 3 naar 0 ging, en genero 62% goed terwijl de doos van 2 naar 0 ging.
//
// De app had een hele machine voor VORMEN en geen enkele bladzijde over wat een tijd DOET. Van de
// 46 spiekbrieven gaat er geen enkele over de tijden als geheel.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE KAART BESTAAT EN IS TE VINDEN. Eén regel bovenaan de Grammatica-tab, en die opent hem.
//   2. ALLE ZES DE TIJDEN STAAN EROP, met wat ze doen en waaraan je ze herkent.
//   3. ER STAAT GEEN ENKELE VERVOEGINGSTABEL OP. Dat is het hele punt: die staan al in de les, en
//      voor wie hier komt zijn ze de verkeerde volgorde. Dit is de proef die afgaat zodra iemand
//      "even een tabelletje" toevoegt.
//   4. DE VOORBEELDEN ZIJN NEDERLANDS. Ook dat is het punt: de vraag "welke tijd" beantwoord je
//      eerst in je eigen taal, en dan doe je één ding tegelijk.
//   5. DE DRIE KEUZES STAAN EROP. Een lijstje van zes tijden vertelt je niet welke twee je tegen
//      elkaar afweegt, en dat is wat je in een zin doet.
//   6. DE WEEKSCORE STAAT NAAST DE DOOS. Gebouwd: een concept met 75% goed deze week en doos 0 zegt
//      allebei. Met het controlegeval: onder de drie beurten staat er niets, want 1 van de 1 is
//      geen percentage.
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
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {} });
  await page.waitForTimeout(400);

  // ---- 1. de ingang ----
  console.log('\n-- 1. de kaart is te vinden --');
  const ingang = await page.evaluate(() => {
    show('spiekbrief', true);
    renderCheat();
    const b = document.getElementById('btnTijdenKaart');
    const kaart = document.getElementById('cheat');
    const tekst = (kaart.innerText || '').replace(/\s+/g, ' ');
    return { erIs: !!b, label: b ? (b.innerText || '').replace(/\s+/g, ' ').slice(0, 60) : '',
             bovenRoute: b && document.getElementById('gramRoute')
               ? b.compareDocumentPosition(document.getElementById('gramRoute')) === 4 : false,
             routeErIs: /in de volgorde waarin ze op elkaar bouwen|De route/.test(tekst) };
  });
  console.log('   "' + ingang.label + '"');
  ok(ingang.erIs, 'er staat een regel op de Grammatica-tab die naar de kaart gaat');
  ok(ingang.bovenRoute, 'en hij staat bóven de route, want dit heb je eerder nodig');
  ok(ingang.routeErIs, 'CONTROLE: de route staat er nog gewoon onder, er is niets weggehaald');

  // ---- 2 t/m 5. wat er op de kaart staat ----
  console.log('\n-- 2 t/m 5. wat er op de kaart staat --');
  const kaart = await page.evaluate(() => {
    tijdenOpen();
    renderCheat();
    const el = document.getElementById('cheat');
    const html = el.innerHTML;
    const tekst = (el.innerText || '').replace(/\s+/g, ' ');
    // alle details openklappen, anders meet innerText alleen de zes kopjes
    el.querySelectorAll('details').forEach(function (d) { d.open = true; });
    const open = (el.innerText || '').replace(/\s+/g, ' ');
    return {
      tijden: TIJDEN.map(function (t) { return t.id; }),
      namen: TIJDEN.map(function (t) { return t.es; }),
      rijen: el.querySelectorAll('.tijdrij').length,
      keuzes: TIJD_KEUZES.length,
      tabel: /<table/i.test(html),
      terug: !!document.getElementById('btnTijdenTerug'),
      lengte: open.length,
      tekst: open,
      // staan de Spaanse voorbeelden er als illustratie (één per tijd) en niet als opgave?
      esPerTijd: TIJDEN.every(function (t) { return open.indexOf(t.nl1) !== -1; }),
      // de drie keuzevragen
      keuzeVragen: TIJD_KEUZES.map(function (k) { return open.indexOf(k.vraag) !== -1; })
    };
  });
  console.log('   ' + kaart.namen.join(' · '));
  console.log('   ' + kaart.rijen + ' rijen, ' + kaart.keuzes + ' keuzes, ' + kaart.lengte + ' tekens');
  ok(kaart.tijden.length === 6 && kaart.rijen === 6,
    'alle zes de tijden staan op de kaart (' + kaart.rijen + ' rijen)');
  ['presente', 'indefinido', 'imperfecto', 'perfecto', 'futuroir', 'subjuntivo'].forEach(function (t) {
    if (kaart.tijden.indexOf(t) === -1) ok(false, 'de tijd ' + t + ' ontbreekt');
  });
  ok(kaart.tijden.indexOf('subjuntivo') !== -1 && /aanvoegende wijs/.test(kaart.tekst),
    'de subjuntivo staat er met zijn Nederlandse naam erbij, want dat is het woord dat Stefan noemde');
  /* De kaart moet de namen uitleggen, dus mag hij ze zelf niet fout hebben. "Voltooid verleden
     tijd" is in het Nederlands 'ik had gebroken', en dat is geen van deze zes; het indefinido
     stond in de eerste versie zo genoemd. */
  ok(!/voltooid verleden tijd/i.test(kaart.tekst),
    'CONTROLE: geen enkele tijd draagt een verkeerde Nederlandse naam');
  ok(/vorm waar het Spaans er twee heeft/.test(kaart.tekst),
    'en de kaart zegt waaróm indefinido tegen imperfecto lastig is: wij hebben er een, zij twee');
  ok(!kaart.tabel, 'CONTROLE: er staat geen enkele vervoegingstabel op, en dat is het hele punt');
  ok(kaart.keuzes === 3 && kaart.keuzeVragen.every(Boolean),
    'de drie keuzes staan erop (af of niet af, tijdvak, feit of wens)');
  ok(kaart.esPerTijd, 'elke tijd heeft één Spaans voorbeeld met vertaling, als illustratie');
  ok(kaart.lengte > 1500, 'en er staat echt iets, geen kop met een belofte (' + kaart.lengte + ' tekens)');
  ok(kaart.terug, 'er is een weg terug');

  // de voorbeelden zijn Nederlands: geen enkele opsomming staat in het Spaans
  console.log('\n-- 4. de voorbeelden staan in het Nederlands --');
  const nl = await page.evaluate(() => {
    // een Spaanse zin herken je aan de Spaanse functiewoorden; die horen niet in de vb-lijstjes
    const spaans = /\b(el|la|los|las|que|de|en|un|una|por|para|con)\b/;
    const fout = [];
    TIJDEN.forEach(function (t) {
      (t.vb || []).forEach(function (v) {
        const woorden = v.toLowerCase().replace(/[^a-zà-ú ]/g, '').split(/\s+/);
        const treffers = woorden.filter(function (w) { return spaans.test(w) && w.length > 1; });
        // 'de', 'en', 'een' bestaan ook in het Nederlands; pas bij drie of meer is het Spaans
        if (treffers.length >= 3) fout.push(t.id + ': ' + v);
      });
    });
    return { fout: fout, totaal: TIJDEN.reduce(function (a, t) { return a + (t.vb || []).length; }, 0) };
  });
  console.log('   ' + nl.totaal + ' voorbeelden nagelopen');
  ok(nl.fout.length === 0, 'geen enkel voorbeeld is stiekem een Spaanse zin (' + (nl.fout[0] || 'geen') + ')');
  ok(nl.totaal >= 15, 'en er zijn er genoeg om iets aan te hebben (' + nl.totaal + ')');

  // ---- 6. de weekscore naast de doos ----
  console.log('\n-- 6. de doos zegt er je weekscore bij --');
  const week = await page.evaluate(() => {
    const cid = 'genero';
    function zet(n, goed) {
      S.gramLog = {};
      S.gram = {};
      S.gram[cid] = { box: 0, due: today(), goed: 60, fout: 20, laatst: addDays(today(), -30) };
      if (n > 0) {
        S.gramLog[today()] = {};
        S.gramLog[today()][cid] = { n: n, goed: goed, k: { toets: [n, goed] } };
      }
      return { w: gramWeek(cid), html: gcStatusHtml(cid).replace(/<[^>]*>/g, '') };
    }
    return {
      driekwart: zet(12, 9),
      eentje: zet(1, 1),
      niets: zet(0, 0),
      slecht: zet(10, 2)
    };
  });
  Object.keys(week).forEach(function (k) {
    console.log('   ' + k.padEnd(11) + '"' + week[k].html + '"');
  });
  ok(/75% goed deze week/.test(week.driekwart.html),
    'negen van de twaalf goed staat er als 75% (' + week.driekwart.html + ')');
  ok(/doos 0/.test(week.driekwart.html),
    'en de doos staat er nog gewoon naast, want die regel is niet veranderd');
  ok(!/%/.test(week.eentje.html),
    'CONTROLE: bij één beurt staat er niets, want 1 van de 1 is geen percentage');
  ok(!/%/.test(week.niets.html),
    'CONTROLE: en zonder beurten deze week ook niet, want nul is geen bericht');
  ok(/20% goed deze week/.test(week.slecht.html),
    'en een slechte week staat er net zo goed bij (' + week.slecht.html + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
