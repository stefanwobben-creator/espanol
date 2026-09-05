// v23.32: Voortgang is een eigen scherm, in de volgorde die Stefan gaf.
//
// Wat deze suite vastlegt, en waarom precies dit:
//   - de zes blokken staan er, in zijn volgorde. Een volgorde die niemand bewaakt is een volgorde
//     die bij de volgende versie omvalt, en dan is het weer het scherm van de bouwer.
//   - de cijfers op dit scherm komen uit voortgangCijfers(). Dat is de hele afspraak van dit
//     hoofdstuk: één functie levert de getallen, alle schermen roepen hem aan.
//   - wat hier weg is bij Profiel, is daar niet verstopt maar staat er met een knop erheen.
//   - sterk en zwak staan hier één keer, niet ook nog onderaan bij de cijfers.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Voort' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  // een profiel met genoeg geschiedenis om alle blokken iets te laten zeggen
  await page.evaluate(() => {
    const map = pcicMap(), niv = pcicNiv();
    const a1 = Object.keys(map).filter((k) => (map[k] || []).some((s) => niv[s] === 'A1'));
    a1.slice(0, 120).forEach((k) => { S.srs[k] = { box: 5, k: 1, due: addDays(today(), 30), n: 9 }; });
    a1.slice(120, 200).forEach((k) => { S.srs[k] = { box: 3, due: addDays(today(), 3), n: 3 }; });
    /* Sterk en zwak gaan over thema's, en die hangen aan de tag van een leswoord. Zonder dit stukje
       heeft dit profiel wel Cervantes-sleutels maar geen thema's, en dan staan blok 5 en 6 er
       terecht niet. Twee tags helemaal vast, twee tags net begonnen: dat is precies het verschil dat
       die twee kaarten horen te laten zien. */
    const perKey = {};
    WORDS.forEach((w) => {
      if (!themaMeetelt(w.tag)) return;
      const k = themaSleutel(w.tag);
      (perKey[k] = perKey[k] || []).push(w);
    });
    // op tag groeperen werkt niet: de tag van een woord en de sleutel van een thema zijn niet
    // hetzelfde, en "familie" komt als tag wel voor maar als thema niet
    const keys = Object.keys(perKey).filter((k) => perKey[k].length >= 8);
    keys.slice(0, 2).forEach((k) => perKey[k].forEach((w) => {
      S.srs[w.id] = { box: 5, k: 1, due: addDays(today(), 30), n: 9 };
    }));
    keys.slice(2, 4).forEach((k) => perKey[k].forEach((w) => {
      S.srs[w.id] = { box: 1, due: addDays(today(), 1), n: 1 };
    }));
    const t = today();
    for (let i = 0; i < 10; i++) S.xp[addDays(t, -i)] = 20;
    for (let i = 0; i < 5; i++) S.lesFlow[addDays(t, -i)] = true;
    /* v23.38: de weekkop komt hieruit en niet meer uit S.meting. Zeven dagen maal twaalf beurten is
       84, maal 300 seconden is 35 minuten, en 21 fouten op 84 beurten is 25%. Drie getallen die op
       het scherm bij elkaar horen te passen, dus alle drie uit dezelfde bron en hetzelfde venster. */
    S.dagStats = {};
    for (let i = 0; i < 7; i++) S.dagStats[addDays(t, -i)] = { pogingen: 12, fouten: 3, sec: 300 };
    // een niveaudoel, anders heeft het doelblok niets te tonen en toetst maatstaf 2 niets
    S.doelNiv = 'A1'; S.doelDatum = addDays(t, 140);
    S.meting = {
      '2026-W30': { d: addDays(t, -21), dek: { A1: 40 }, stevig: 40, geoefend: 90, pog: 200, fout: 60 },
      '2026-W31': { d: addDays(t, -14), dek: { A1: 78 }, stevig: 78, geoefend: 150, pog: 220, fout: 55 },
      '2026-W32': { d: addDays(t, -7), dek: { A1: 120 }, stevig: 120, geoefend: 200, pog: 240, fout: 50 }
    };
    try { persist(); } catch (e) {}
  });

  /* v23.224: hier stond dat de knop "Alle cijfers" op Vandaag staat en je hierheen brengt. Die
     knop is met de kaart "Waar je staat" van het dagscherm af (Stefan: "deze functionaliteit mag
     wel uit het scherm"). Wat overblijft is de eis die er echt toe doet: het scherm bestaat, het
     is bereikbaar, en het is NIET je profiel. De route ernaartoe loopt nu via de balk. */
  console.log('\n-- het scherm bestaat en is bereikbaar --');
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(400);
  const weg = await page.evaluate(() => !!document.getElementById('btnLijnMeer'));
  ok(!weg, 'op Vandaag staat geen knop naar je cijfers meer (v23.224)');
  await page.evaluate(() => { show('voortgang'); });
  await page.waitForTimeout(500);
  const open = await page.evaluate(() => ({
    zichtbaar: !document.getElementById('tab-voortgang').classList.contains('hidden'),
    profiel: !document.getElementById('tab-perfil').classList.contains('hidden'),
    inBalk: TABS.some(function (t) { return t.id === 'voortgang'; })
  }));
  ok(open.zichtbaar, 'het voortgangsscherm gaat open');
  ok(!open.profiel, 'en het is niet je profiel');
  ok(open.inBalk, 'en het staat als eigen scherm in TABS, dus het is te bereiken');

  /* v23.244: DE VOLGORDE IS VERANDERD, OP VERZOEK VAN DEGENE DIE HEM KOOS.
     Hier stond ['Je week', 'Je doel', 'Waar je staat', 'Onderweg', 'Sterke punten', 'Zwakke
     plekken'], met de kop "de zes blokken staan in Stefans volgorde". Dat klopte: die volgorde was
     zijn keuze uit v23.32.
     Op 7 november vroeg hij om een scherm dat rangschikt. Dan hoort het antwoord op de vraag
     waarvóór je dit scherm opent bovenaan: waar je staat. Je week is een tussenstand, je doel is een
     instelling. En sterk en zwak zijn één lijst geworden, oplopend gesorteerd, zodat je ze naast
     elkaar ziet in plaats van in twee kaarten met dezelfde eenheid.
     Een proef die een keuze vastlegt, hoort mee te veranderen als degene die de keuze maakte hem
     herziet, en hoort dan te zeggen wanneer en waarom. */
  console.log('\n-- de blokken staan in de volgorde van v23.244 --');
  const volgorde = await page.evaluate(() => {
    const kop = [...document.querySelectorAll('#voortgangCard .kicker')].map((k) => k.innerText.trim());
    return kop;
  });
  const wil = ['Waar je staat', 'Je week', 'Waar het werk ligt', 'Je doel', 'Onderweg'];
  // de kickers staan in kapitalen op het scherm (text-transform), dus vergelijken zonder hoofdletters
  wil.forEach((w, i) => {
    ok((volgorde[i] || '').toLowerCase().indexOf(w.toLowerCase()) === 0,
      'blok ' + (i + 1) + ' is "' + w + '" (' + (volgorde[i] || 'niets') + ')');
  });
  ok(volgorde.indexOf('Sterke punten') === -1 && volgorde.indexOf('Zwakke plekken') === -1,
    'CONTROLE: de twee losse kaarten staan er niet meer naast, anders is het er drie in plaats van een');

  console.log('\n-- de getallen komen uit voortgangCijfers --');
  const cijf = await page.evaluate(() => {
    const c = voortgangCijfers();
    const kaart = document.getElementById('vgVastKaart');
    return { samen: JSON.parse(JSON.stringify(c.samen)),
             tekst: (kaart ? kaart.innerText : '').replace(/\s+/g, ' ') };
  });
  ok(cijf.tekst.indexOf(String(cijf.samen.actief)) !== -1,
    'wat je actief bijhoudt staat er (' + cijf.samen.actief + ')');
  ok(cijf.tekst.indexOf(String(cijf.samen.noem)) !== -1,
    'en de noemer erbij (' + cijf.samen.noem + ')');

  console.log('\n-- je week telt wat je gedaan hebt, niet wat er in S.srs staat --');
  const week = await page.evaluate(() => {
    /* v23.244: de kaart bij zijn kop zoeken en niet op plek [0]. Hier stond de eerste kaart van het
       scherm, en dat wás de weekkaart tot de volgorde veranderde. Een proef die zijn onderwerp op
       positie vindt, gaat af zodra iets ernaast verschuift terwijl er niets mis is met wat hij
       meet. */
    const kaarten = [...document.querySelectorAll('#voortgangCard .card')];
    const k = kaarten.filter((el) => {
      const kop = el.querySelector('.kicker');
      return kop && /je week/i.test(kop.innerText || '');
    })[0];
    return (k ? k.innerText : '').replace(/\s+/g, ' ');
  });
  /* v23.38. Hier stond de aanwas van `geoefend` tussen twee weekmetingen (+50 in deze fixture). Dat
     getal springt met de inhaalslag mee en heeft niets met je week te maken. Nu: de beurten uit
     S.dagStats over zeven dagen, hetzelfde venster als de minuten en het foutpercentage eronder. */
  ok(/\b84\b/.test(week), 'de kop is het aantal beurten van deze week (84)');
  ok(/beurten/.test(week), 'en zegt ook beurten, niet woorden');
  ok(!/\+50/.test(week), 'de aanwas uit de weekmeting staat er niet meer');
  ok(/\/7/.test(week), 'met het aantal dagen dat je er was');
  ok(/\b35\b/.test(week), 'de gemeten minuten staan erbij (35)');
  ok(/per beurt/.test(week), 'en de seconden per beurt, zodat de minuten na te rekenen zijn');
  ok(/ondergrens/.test(week), 'met erbij dat de klok alleen tussen je antwoorden loopt');

  /* ---------- de drie regels uit claude/rapport.md, machinaal ----------
     Deze drie bewaken de maatstaf zelf en niet de tekst. Ze staan hier omdat elke fout die ik op dit
     scherm gemaakt heb er een van deze drie was, en omdat een maatstaf die alleen in een document
     staat de volgende versie niet haalt. */
  console.log('\n-- maatstaf 1: dezelfde zin is hetzelfde getal --');
  const zelfde = await page.evaluate(() => {
    /* Op een A1-profiel zijn "alleen je niveau" en "alle niveaus samen" hetzelfde getal, en dan kan
       deze regel niet omvallen: hij zou groen staan zonder iets te bewaken. Daarom even A2 als
       balkniveau. Dan telt de balk A1 en A2 samen, en moet elke regel die diezelfde woorden gebruikt
       dat ook doen. Dit is precies de fout die op Stefans scherm stond: 50 onderaan, 406 bovenaan. */
    const oudNiv = balkNiveau;
    balkNiveau = function () { return 'A2'; };
    try {
      const c = voortgangCijfers();
      const doos = document.createElement('div');
      doos.innerHTML = cijferLijstHtml();
      const rijen = [...doos.querySelectorAll('.cijfRij')]
        .filter((r) => /actief bij/.test(r.textContent || ''));
      return { samen: c.samen.actief, perNiveau: c.actief, nivs: c.samen.nivs,
               getallen: rijen.map((r) => ((r.querySelector('.cijfW') || {}).textContent || '').trim()) };
    } finally { balkNiveau = oudNiv; }
  });
  ok(zelfde.nivs.length > 1 && zelfde.samen !== zelfde.perNiveau,
    'de proef zet twee verschillende getallen tegenover elkaar (samen ' + zelfde.samen +
    ', alleen A2 ' + zelfde.perNiveau + ')');
  ok(zelfde.getallen.length > 0, 'de regel "actief bij" staat in de cijferlijst');
  ok(zelfde.getallen.every((g) => Number(g) === zelfde.samen),
    'en toont hetzelfde getal als de balk (' + (zelfde.getallen.join(', ') || 'niets') + ')');

  console.log('\n-- maatstaf 2: geen tempo uit een meting die het niet weet --');
  /* De metingen in deze fixture kennen geen dekw, want die bestaat pas sinds v23.37. Dan is er geen
     tempo in de maat van de balk, en dus ook geen koersoordeel. Dit is de fout die ik in v23.37 zelf
     maakte: de stand omgezet naar de nieuwe maat en het tempo uit de oude laten komen. */
  const doel = await page.evaluate(() => {
    const k = [...document.querySelectorAll('#voortgangCard .card')][1];
    const ds = doelStand();
    return { tekst: (k ? k.innerText : '').replace(/\s+/g, ' '), tempo: ds ? ds.tempo : null };
  });
  ok(doel.tempo === null, 'zonder dekw in de weekmetingen is er geen tempo (' + doel.tempo + ')');
  ok(!/op koers|later dan je datum/.test(doel.tekst), 'en dus staat er ook geen koersoordeel');

  console.log('\n-- maatstaf 3: elk percentage heeft woorden bij zich --');
  const losPct = await page.evaluate(() => {
    /* Naar het vak eromheen kijken en niet naar de regel: een meetbalk zet naam, staaf en getal in
       drie elementen, dus in innerText staat "23%" bijna altijd alleen op zijn eigen regel terwijl
       het label er in beeld pal naast staat. De vraag is of het vak waarin het percentage staat
       zegt wat het meet. */
    const vakken = [...document.querySelectorAll('#tab-voortgang .vgMeet, #tab-voortgang .stat, ' +
      '#tab-voortgang .cijfRij, #tab-voortgang p, #tab-voortgang li')];
    const kaal = vakken.filter((v) => {
      const t = (v.innerText || '').replace(/\s+/g, ' ').trim();
      if (!/%/.test(t)) return false;
      return !/[a-z\u00e0-\u017f]{3}/i.test(t.replace(/[\d.,%]+/g, ' '));
    }).map((v) => (v.innerText || '').replace(/\s+/g, ' ').trim());
    // en een percentage dat in helemaal geen vak staat is per definitie kaal
    const zwevend = [...document.querySelectorAll('#tab-voortgang *')].filter((e) => {
      if (e.children.length) return false;
      return /%/.test((e.textContent || '')) && !e.closest('.vgMeet, .stat, .cijfRij, p, li');
    }).map((e) => (e.textContent || '').trim());
    return kaal.concat(zwevend);
  });
  ok(losPct.length === 0, 'geen kaal percentage zonder wat het meet (' +
    (losPct.join(' | ') || 'geen') + ')');

  console.log('\n-- sterk en zwak staan er één keer --');
  const dubbel = await page.evaluate(() => {
    const t = document.getElementById('tab-voortgang').innerText;
    return { sterk: (t.match(/Sterke punten/g) || []).length,
             zwak: (t.match(/Zwakke plekken/g) || []).length,
             oud: (t.match(/Dit beheers je/g) || []).length };
  });
  ok(dubbel.sterk <= 1 && dubbel.zwak <= 1, 'niet twee keer hetzelfde blok op één scherm');
  ok(dubbel.oud === 0, 'en het oude gecombineerde blok is weg, niet blijven staan');

  /* v23.244: de cijferlijst staat achter een vouw, en die vouw is dicht bij binnenkomst. Weggelaten
     is niet verstopt, dus de proef eist allebei: hij bestaat, en hij staat dicht. Zonder het tweede
     zou "altijd open" deze proef ook halen, en dan is er niets veranderd. */
  const vouw = await page.evaluate(() => {
    const d = document.getElementById('cijferVouw');
    if (!d) return { erIs: false };
    const kop = (d.querySelector('summary') || {}).innerText || '';
    /* textContent en niet innerText: een dichte vouw is niet zichtbaar, en innerText geeft van
       onzichtbare inhoud een lege string terug. Dan meet je of hij open staat, terwijl je wilt
       weten of er iets in zit. */
    const inhoud = (d.querySelector('.inner') || {}).textContent || '';
    return { erIs: true, dicht: !d.open, kop: kop.trim(), tekens: inhoud.length };
  });
  console.log('   "' + (vouw.kop || 'geen vouw') + '", ' + (vouw.tekens || 0) + ' tekens erin');
  ok(vouw.erIs, 'de cijferlijst zit achter een vouw');
  ok(vouw.dicht, 'en die staat dicht bij binnenkomst, want dit is een ander moment dan de rest');
  ok(vouw.tekens > 200, 'CONTROLE: er zit ook echt iets in die vouw (' + (vouw.tekens || 0) + ' tekens)');

  console.log('\n-- weggelaten is niet verstopt --');
  await page.evaluate(() => show('perfil'));
  await page.waitForTimeout(400);
  const prof = await page.evaluate(() => ({
    knop: !!document.getElementById('btnNaarVoortgang'),
    stats: !!document.querySelector('#tab-perfil #statsCard')
  }));
  ok(prof.knop, 'op je profiel staat een knop naar je voortgang');
  ok(!prof.stats, 'en de cijfers staan er niet ook nog een keer');

  const echt = errors.filter((e) => !/Failed to load resource|net::/.test(e));
  ok(echt.length === 0, 'geen JS-fouten (' + echt.length + ')');
  if (echt.length) echt.forEach((e) => console.log('  -> ' + e));

  await browser.close();
  console.log(fout === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
