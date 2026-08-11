// v23.42: schrijven staat weer in de dagles, als vaste vierde stap van drie zinnen.
//
// Waarom hier een suite omheen: dit blok is er in v20.5 uitgehaald omdat Stefan erop afhaakte, en op
// 11 aug op zijn verzoek teruggezet in een kleinere vorm. Twee keer hetzelfde blok verplaatsen zonder
// dat iets de vorm bewaakt, en de derde keer staat het weer op tien zinnen achter het einde van de
// les. Wat hier vastligt is dus niet dat schrijven bestaat, maar dat het klein is en binnen de les.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 1000 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Schr' + Date.now());
  await page.click('button:has-text("A2 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(1100);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- na de toetsjes komt schrijven, niet het einde --');
  const na = await page.evaluate(() => {
    lesFlow = { stap: 'toetsjes', quizzesTeDoen: [], gekozenSpel: null, vertalenTeGaan: 0 };
    lesFlowVolgendeKern();
    return { stap: lesFlow && lesFlow.stap, vaardigheid: lesFlow && lesFlow.vaardigheid,
             spel: lesFlow && lesFlow.gekozenSpel, teGaan: lesFlow && lesFlow.vertalenTeGaan,
             totaal: lesFlow && lesFlow.vertalenTotaal, vast: SCHRIJF_PER_LES,
             num: lesFlowStapNum(), naam: lesFlowStapNaam(),
             zichtbaar: !document.getElementById('tab-vertalen').classList.contains('hidden') };
  });
  ok(na.stap === 'produceren' && na.vaardigheid === 'schrijven', 'de les gaat door naar schrijven (' + na.stap + '/' + na.vaardigheid + ')');
  ok(na.zichtbaar, 'en het scherm staat open');
  ok(na.num === 4 && /Schrijven/.test(na.naam || ''), 'het is stap 4 en heet Schrijven (' + na.num + ' ' + na.naam + ')');

  console.log('\n-- drie zinnen, niet tien --');
  ok(na.vast === 3, 'SCHRIJF_PER_LES is 3 (' + na.vast + ')');
  ok(na.teGaan === 3 && na.totaal === 3, 'de teller begint op drie (' + na.teGaan + '/' + na.totaal + ')');
  const kop = await page.evaluate(() => {
    const k = document.querySelector('#tab-vertalen .kicker');
    return (k ? k.innerText : '').replace(/\s+/g, ' ');
  });
  ok(/1\/3/.test(kop) || /4\/4/.test(kop), 'de kop zegt waar je bent (' + kop + ')');

  console.log('\n-- na de derde zin is de les af --');
  const af = await page.evaluate(() => {
    for (let i = 0; i < 3; i++) {
      if (!lesFlow || lesFlow.stap !== 'produceren') break;
      lesFlow.vertalenTeGaan--;
      if (lesFlow.vertalenTeGaan <= 0) { S.lesFlowSpel.vertalen = today(); lesFlowVolgende(); }
    }
    return { flow: lesFlow ? lesFlow.stap : null, klaar: !!(S.lesFlow || {})[today()],
             schrijvenGehad: (S.lesFlowSpel || {}).schrijven === today() ||
                             (S.lesFlowSpel || {}).vertalen === today() };
  });
  ok(af.flow === null, 'de les is afgelopen na de derde zin');
  ok(af.klaar, 'en telt als afgemaakte dagles');
  ok(af.schrijvenGehad, 'schrijven staat vandaag afgevinkt, dus je krijgt het niet nog eens voorgesteld');

  console.log('\n-- zonder zinnen valt de les niet stil --');
  const leeg = await page.evaluate(() => {
    const echt = allowedSentIds;
    allowedSentIds = function () { return []; };
    try {
      lesFlow = { stap: 'toetsjes', quizzesTeDoen: [], gekozenSpel: null, vertalenTeGaan: 0 };
      lesFlowVolgendeKern();
      return { flow: lesFlow ? lesFlow.stap : null };
    } finally { allowedSentIds = echt; }
  });
  ok(leeg.flow === null, 'heb je nog geen zinnen vrijgespeeld, dan sluit de les gewoon af');

  console.log('\n-- Adivina laat het lidwoord zien --');
  const adiv = await page.evaluate(() => {
    const pool = adivPool();
    const met = pool.filter((w) => /^(el|la) /.test(w.es));
    const stuk = met.filter((w) => /^(el|la) /.test(w.plat) || /\s/.test(w.plat));
    return { n: pool.length, metLidwoord: met.length, stuk: stuk.length,
             vb: met.slice(0, 2).map((w) => w.es + ' -> ' + w.plat) };
  });
  ok(adiv.metLidwoord > 50, 'de vijver bevat woorden mét lidwoord (' + adiv.metLidwoord + ' van ' + adiv.n + ')');
  ok(adiv.stuk === 0, 'maar op het bord staat alleen de kern (' + adiv.vb.join(', ') + ')');

  ok(errors.length === 0, 'geen JS-fouten (' + errors.length + ')' + (errors[0] ? ' ' + errors[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
