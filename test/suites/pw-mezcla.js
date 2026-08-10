// v23.34: la mezcla. Een tapa plus een dans wordt een naam, en die naam buigt mee.
//
// Wat hier vastligt:
//   - het bijvoeglijk naamwoord volgt het lidwoord van de tapa. Dit is het hele punt: het spelletje
//     drilt de overeenkomst tussen zelfstandig en bijvoeglijk naamwoord, en een fout hierin leert
//     iemand precies verkeerd. Vier vormen worden op de letter nagerekend.
//   - de bestaande gebaren veranderen niet. Een tapa aantikken voert haar nog steeds, een dans
//     aantikken laat haar nog steeds dansen; de mezcla ontstaat ernaast.
//   - een gevonden mezcla blijft staan, en de teller kan nooit boven zijn noemer uitkomen (zie de
//     tapateller van v23.33 en de luisterteller van v22.10: dat is hier een terugkerende fout).
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
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Mez' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true; S.tapas = 20;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- de vier vormen, op de letter --');
  const vormen = await page.evaluate(() => ({
    pulpo: mezclaMaak('pulpo', 'flamenco').es,
    aceitunas: mezclaMaak('aceitunas', 'salsa').es,
    tortilla: mezclaMaak('tortilla', 'tango').es,
    calamares: mezclaMaak('calamares', 'reggaeton').es,
    jarabe: mezclaMaak('bravas', 'jarabe').es,
    onzin: mezclaMaak('bestaat-niet', 'salsa')
  }));
  ok(vormen.pulpo === 'el pulpo flamenco', 'el (m enkelvoud): ' + vormen.pulpo);
  ok(vormen.aceitunas === 'las aceitunas salseras', 'las (v meervoud): ' + vormen.aceitunas);
  ok(vormen.tortilla === 'la tortilla tanguera', 'la (v enkelvoud): ' + vormen.tortilla);
  ok(vormen.calamares === 'los calamares reggaetoneros', 'los (m meervoud): ' + vormen.calamares);
  ok(vormen.jarabe === 'las patatas tapatías', 'en de kern zonder zijn staart: ' + vormen.jarabe);
  ok(vormen.onzin === null, 'een tapa die niet bestaat levert niets op, geen halve naam');

  console.log('\n-- alle 144 combinaties leveren een naam op --');
  const alle = await page.evaluate(() => {
    let n = 0, stuk = [];
    TAPAS.forEach((t) => BAILES.forEach((b) => {
      const m = mezclaMaak(t.id, b.id);
      if (!m || !/^(el|la|los|las) \S+ \S+$/.test(m.es)) stuk.push(t.id + '+' + b.id + ': ' + (m ? m.es : 'null'));
      else n++;
    }));
    return { n: n, stuk: stuk.slice(0, 4), totaal: TAPAS.length * BAILES.length };
  });
  ok(alle.n === alle.totaal, 'alle ' + alle.totaal + ' combinaties geven een lidwoord, een kern en een bijvoeglijk naamwoord ('
     + alle.n + ')' + (alle.stuk.length ? ' -- ' + alle.stuk.join(' | ') : ''));

  console.log('\n-- de strip staat tussen de tapas en de dansen --');
  await page.evaluate(() => show('chispa'));
  await page.waitForTimeout(600);
  const plek = await page.evaluate(() => {
    const s = document.getElementById('mezclaStrip');
    const t = document.getElementById('tapaMenuRij');
    const b = document.getElementById('baileRij');
    if (!s || !t || !b) return null;
    const y = (e) => e.getBoundingClientRect().top;
    return { inPet: !!s.closest('#petCard'), tussen: y(t) < y(s) && y(s) < y(b),
             leeg: s.querySelectorAll('.mezVak.leeg').length };
  });
  ok(plek && plek.inPet, 'de strip staat in de kaart van Chispa');
  ok(plek && plek.tussen, 'tussen de tapas en de dansen in');
  ok(plek && plek.leeg === 2, 'met twee lege vakjes om te beginnen (' + (plek ? plek.leeg : '-') + ')');

  console.log('\n-- aantikken doet nog steeds wat het deed, en vult het vakje --');
  const voor = await page.evaluate(() => ({ tapas: S.tapas || 0, bailes: (S.bailes || []).length }));
  await page.locator('#tapaMenuRij button.tapachip').first().click();
  await page.waitForTimeout(500);
  const naTapa = await page.evaluate(() => ({
    tapas: S.tapas || 0, gehad: (S.tapaMenu || []).length,
    vakken: document.querySelectorAll('#mezclaStrip .mezVak.leeg').length
  }));
  ok(naTapa.tapas === voor.tapas - 1, 'een tapa aantikken voert haar nog steeds (' + voor.tapas + ' -> ' + naTapa.tapas + ')');
  ok(naTapa.vakken === 1, 'en er is nog één vakje leeg (' + naTapa.vakken + ')');

  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(700);
  const naBaile = await page.evaluate(() => ({
    bailes: (S.bailes || []).length,
    mezclas: (S.mezcla || []).length,
    tekst: (document.getElementById('mezclaStrip') || {}).innerText || '',
    tel: (document.getElementById('mezclaTel') || {}).innerText || '',
    // op het woord "nieuw" zoeken kan niet: de knop ernaast heet "opnieuw". Dus op de markering zelf.
    nieuw: !!document.querySelector('#mezclaStrip .mezNieuw')
  }));
  ok(naBaile.bailes > voor.bailes, 'een dans aantikken laat haar nog steeds dansen');
  ok(naBaile.mezclas === 1, 'en samen leveren ze één gevonden mezcla op (' + naBaile.mezclas + ')');
  ok(/\S+ \S+/.test(naBaile.tekst) && !/\?/.test(naBaile.tekst), 'de uitkomst staat in de strip: ' + naBaile.tekst.replace(/\n/g, ' | '));
  ok(naBaile.nieuw, 'met erbij dat hij nieuw is');

  console.log('\n-- de tapa danst mee, op haar formaat en in haar tempo --');
  /* Eerst haar in beeld schuiven. Staat de kaart weggescrold, dan danst ze in de meeloopbalk en is
     alles daar kleiner; dan meet deze test twee verschillende podia tegen elkaar en valt hij om op
     iets wat klopt. */
  await page.evaluate(() => {
    const b = document.getElementById('petBox');
    if (b && b.scrollIntoView) b.scrollIntoView({ block: 'center' });
    try { chispaBalkCheck(); } catch (e) {}
  });
  await page.waitForTimeout(300);
  await page.evaluate(() => { mezclaWis(); document.querySelectorAll('.chmez').forEach((e) => e.remove()); });
  await page.evaluate(() => { mezclaKies('tapa', TAPAS[0].id); mezclaKies('baile', BAILES[0].id); });
  await page.waitForTimeout(400);
  /* v23.36: hij krijgt dezelfde klasse en dezelfde animatieduur als Chispa. Dat is het punt: een
     eigen animatie die er ongeveer op lijkt kan uit de pas lopen, deze niet. */
  const mee = await page.evaluate(() => {
    const el = document.querySelector('.chmez');
    if (!el) return null;
    const b = BAILES.filter((x) => x.id === mezclaBaile)[0];
    /* Niet vergelijken met chispaBox().style: welke box er danst hangt ervan af of je naar haar
       kijkt of naar de meeloopbalk, en dat wisselt tijdens het scrollen. Wat vastligt is de bron:
       de duur hoort de slagen-per-bpm van deze dans te zijn, en geen eigen benadering. */
    const hoort = b ? Math.round(b.slagen * 60 / b.bpm * 1000) / 1000 : null;
    const zij = document.getElementById('petBox');
    return {
      klas: el.className,
      danst: !!(b && el.classList.contains(b.klas)),
      duur: el.style.animationDuration,
      hoort: hoort === null ? null : hoort + 's',
      hoogEl: Math.round(el.getBoundingClientRect().height),
      hoogZij: zij ? Math.round(zij.getBoundingClientRect().height) : 0
    };
  });
  ok(mee, 'er staat een meedanser naast haar');
  ok(mee && mee.danst, 'met dezelfde dansklasse als Chispa (' + (mee ? mee.klas : '-') + ')');
  ok(mee && mee.duur && mee.duur === mee.hoort,
     'en met de duur die uit de bpm van deze dans volgt (' + (mee ? mee.duur + ' tegenover ' + mee.hoort : '-') + ')');
  ok(mee && mee.hoogZij > 0 && mee.hoogEl > mee.hoogZij * 0.3 && mee.hoogEl < mee.hoogZij * 1.2,
     'ongeveer even groot als zij (' + (mee ? mee.hoogEl + ' tegenover ' + mee.hoogZij : '-') + ')');

  console.log('\n-- ook als je de tapa als laatste aantikt, danst hij --');
  await page.evaluate(() => { mezclaWis(); document.querySelectorAll('.chmez').forEach((e) => e.remove()); });
  await page.locator('#baileRij button.bailechip').nth(1).click();
  await page.waitForTimeout(400);
  await page.locator('#tapaMenuRij button.tapachip').nth(1).click();
  await page.waitForTimeout(600);
  const andersom = await page.evaluate(() => ({
    mee: !!document.querySelector('.chmez'),
    bezig: !!(chispaBox() && chispaBox().classList.contains('chbezig'))
  }));
  ok(andersom.mee, 'de meedanser staat er ook als de tapa het laatste tikje was');
  ok(andersom.bezig, 'en Chispa danst dan zelf ook, in plaats van alleen de naam te zeggen');

  console.log('\n-- dezelfde nog eens telt niet dubbel --');
  const voorHerhaling = await page.evaluate(() => { mezclaWis(); return (S.mezcla || []).length; });
  await page.locator('#tapaMenuRij button.tapachip').first().click();
  await page.waitForTimeout(300);
  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(500);
  const weer = await page.evaluate(() => ({
    mezclas: (S.mezcla || []).length,
    nieuw: !!document.querySelector('#mezclaStrip .mezNieuw')
  }));
  ok(weer.mezclas === voorHerhaling, 'dezelfde combinatie telt niet twee keer (' + weer.mezclas + ')');
  ok(!weer.nieuw, 'en hij doet ook niet alsof hij nieuw is');

  console.log('\n-- de teller kan niet boven zijn noemer uitkomen --');
  const tel = await page.evaluate(() => {
    S.mezcla = (S.mezcla || []).concat(['bestaat-niet|salsa']);
    mezclaTeken(false);
    const t = (document.getElementById('mezclaTel') || {}).innerText || '';
    const m = t.match(/(\d+)\D+(\d+)/);
    return { tekst: t, gevonden: m ? +m[1] : -1, totaal: m ? +m[2] : -1, echt: TAPAS.length * BAILES.length };
  });
  ok(tel.totaal === tel.echt, 'de noemer is achttien maal acht (' + tel.totaal + ')');
  ok(tel.gevonden <= tel.totaal, 'en de teller blijft eronder (' + tel.tekst.replace(/\n/g, ' ') + ')');

  console.log('\n-- opnieuw maakt de vakjes leeg --');
  await page.evaluate(() => { mezclaTapa = 'pulpo'; mezclaBaile = 'tango'; mezclaTeken(false); });
  await page.waitForTimeout(200);
  await page.click('#btnMezWis');
  await page.waitForTimeout(300);
  const leeg = await page.evaluate(() => document.querySelectorAll('#mezclaStrip .mezVak.leeg').length);
  ok(leeg === 2, 'na "opnieuw" staan er weer twee lege vakjes (' + leeg + ')');

  const echt = errors.filter((e) => !/Failed to load resource|net::/.test(e));
  ok(echt.length === 0, 'geen JS-fouten (' + echt.length + ')');
  if (echt.length) echt.forEach((e) => console.log('  -> ' + e));

  await browser.close();
  console.log(fout === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
