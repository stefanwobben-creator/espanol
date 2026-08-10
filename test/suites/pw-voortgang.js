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
    S.meting = {
      '2026-W30': { d: addDays(t, -21), dek: { A1: 40 }, stevig: 40, geoefend: 90, pog: 200, fout: 60 },
      '2026-W31': { d: addDays(t, -14), dek: { A1: 78 }, stevig: 78, geoefend: 150, pog: 220, fout: 55 },
      '2026-W32': { d: addDays(t, -7), dek: { A1: 120 }, stevig: 120, geoefend: 200, pog: 240, fout: 50 }
    };
    try { persist(); } catch (e) {}
  });

  console.log('\n-- het scherm bestaat en is bereikbaar vanaf Vandaag --');
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(400);
  const knop = await page.evaluate(() => !!document.getElementById('btnLijnMeer'));
  ok(knop, 'op Vandaag staat de knop naar je cijfers');
  await page.evaluate(() => { document.getElementById('btnLijnMeer').click(); });
  await page.waitForTimeout(500);
  const open = await page.evaluate(() => ({
    zichtbaar: !document.getElementById('tab-voortgang').classList.contains('hidden'),
    profiel: !document.getElementById('tab-perfil').classList.contains('hidden')
  }));
  ok(open.zichtbaar, 'de knop brengt je op het voortgangsscherm');
  ok(!open.profiel, 'en niet meer op je profiel');

  console.log('\n-- de zes blokken staan in Stefans volgorde --');
  const volgorde = await page.evaluate(() => {
    const kop = [...document.querySelectorAll('#voortgangCard .kicker')].map((k) => k.innerText.trim());
    return kop;
  });
  const wil = ['Je week', 'Je doel', 'Waar je staat', 'Onderweg', 'Sterke punten', 'Zwakke plekken'];
  // de kickers staan in kapitalen op het scherm (text-transform), dus vergelijken zonder hoofdletters
  wil.forEach((w, i) => {
    ok((volgorde[i] || '').toLowerCase().indexOf(w.toLowerCase()) === 0,
      'blok ' + (i + 1) + ' is "' + w + '" (' + (volgorde[i] || 'niets') + ')');
  });

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

  console.log('\n-- je week rekent met het verschil, niet met de stand --');
  const week = await page.evaluate(() => {
    const k = [...document.querySelectorAll('#voortgangCard .card')][0];
    return (k ? k.innerText : '').replace(/\s+/g, ' ');
  });
  /* v23.37: de week telt geoefende woorden, niet bewezen vast. De fixture gaat van 150 naar 200
     geoefend, dus +50. Bewezen vast ging van 78 naar 120; dat is wat hier eerst stond, en precies
     de teller waarvan Stefan zei dat hij als weekcijfer niets zegt. */
  ok(/\+50/.test(week), 'de aanwas is die van geoefende woorden (+50)');
  ok(/\/7/.test(week), 'met het aantal dagen dat je er was');

  console.log('\n-- sterk en zwak staan er één keer --');
  const dubbel = await page.evaluate(() => {
    const t = document.getElementById('tab-voortgang').innerText;
    return { sterk: (t.match(/Sterke punten/g) || []).length,
             zwak: (t.match(/Zwakke plekken/g) || []).length,
             oud: (t.match(/Dit beheers je/g) || []).length };
  });
  ok(dubbel.sterk <= 1 && dubbel.zwak <= 1, 'niet twee keer hetzelfde blok op één scherm');
  ok(dubbel.oud === 0, 'en het oude gecombineerde blok is weg, niet blijven staan');

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
