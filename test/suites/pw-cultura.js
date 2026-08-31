// pw-cultura.js (31 aug, v23.223) — blijft de nieuwe reeks op de maat waarop hij geijkt is?
//
// WAAROM DEZE SUITE ER IS
//
// España por dentro is de eerste reeks die niet op een onderwerp is gekozen maar op een MAAT.
// Stefan las hoofdstuk 1 en zei: "dit is een goede tekst die ik zo 90% comfortabel kan lezen." Dat
// zinnetje is het hele criterium; de andere negen hoofdstukken zijn erop geschreven.
//
// Zo'n maat verdwijnt zonder dat iemand het merkt. De nachttaak voegt content toe aan bestaande
// arrays, en één hoofdstuk van 400 woorden met zinnen van dertig zou hier gewoon tussen passen en
// nergens rood worden. Dan is de reeks over een maand precies zo zwaar als de rest, en dan hebben
// we de fout van de leesplank opnieuw gemaakt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE REEKS STAAT ER, EN JE KUNT ER METEEN IN. Drempel 0 op alle tien: dit zijn losse stukken,
//      geen verhaal met een volgorde.
//   2. DE MAAT. Per hoofdstuk 140 tot 210 woorden en gemiddeld hoogstens tien woorden per zin, en
//      geen enkele zin boven de 25. Dat zijn de getallen van de tekst die is goedgekeurd.
//   3. HET CONTROLEGEVAL, EN DAT WORDT GEBOUWD EN NIET GEVONDEN. Een verzonnen hoofdstuk met lange
//      zinnen moet door diezelfde meting worden afgekeurd. Anders meet punt 2 niets: een meting die
//      alles goedkeurt is geen meting. (De regel uit v23.221, nu meteen goed toegepast.)
//   4. DE VRAGEN ZIJN BEANTWOORDBAAR. Vier per hoofdstuk, drie opties, een geldig antwoord, en geen
//      twee opties die hetzelfde zeggen.
//   5. HET SCHERM DOET HET. Het hoofdstuk tekent, en er staat een vertaalknop per alinea.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwCu' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1. de reeks ----
  console.log('\n-- 1. de reeks staat op de plank --');
  const reeks = await page.evaluate(() => {
    const r = LEES_REEKSEN.filter(function (x) { return x.id === 'cultura'; })[0];
    const hs = BOOK.filter(function (h) { return h.id.indexOf('vida-') === 0; });
    return { er: !!r, verteller: !!(r && r.verteller), pre: r && r.pre,
             n: hs.length, drempels: hs.map(function (h) { return h.drempel; }),
             nums: hs.map(function (h) { return h.num; }) };
  });
  ok(reeks.er && reeks.pre === 'vida-', 'España por dentro staat in LEES_REEKSEN');
  ok(reeks.n === 10, 'met tien hoofdstukken (' + reeks.n + ')');
  ok(reeks.drempels.every(function (d) { return d === 0; }), 'en je kunt er meteen in, allemaal drempel 0');
  ok(reeks.nums.join(',') === '1,2,3,4,5,6,7,8,9,10', 'de nummers lopen door (' + reeks.nums.join(',') + ')');
  ok(reeks.verteller, 'de reeks heeft een verteller, dus hij kan ingesproken worden');

  // ---- 2 en 3. de maat, en het controlegeval ----
  console.log('\n-- 2 en 3. de maat waarop deze reeks geijkt is --');
  const maat = await page.evaluate(() => {
    /* De meting staat hier als functie, zodat punt 3 hem op een verzonnen tekst kan loslaten.
       Meten en dan met een andere meetlat controleren zou niets zeggen. */
    function meet(tekst) {
      const zinnen = String(tekst).replace(/\n+/g, ' ').split(/(?<=[.!?])\s+/)
        .filter(function (z) { return z.trim().length > 3; });
      const lengtes = zinnen.map(function (z) { return (z.match(/[a-záéíóúüñA-ZÁÉÍÓÚÑ]+/g) || []).length; });
      const woorden = lengtes.reduce(function (a, b) { return a + b; }, 0);
      return { woorden: woorden, zinnen: zinnen.length,
               gem: +(woorden / (lengtes.length || 1)).toFixed(1),
               langste: Math.max.apply(null, lengtes.concat([0])) };
    }
    function keurt(m) { return m.woorden >= 140 && m.woorden <= 210 && m.gem <= 10 && m.langste <= 25; }

    const echt = BOOK.filter(function (h) { return h.id.indexOf('vida-') === 0; })
      .map(function (h) { const m = meet(h.tekst); m.id = h.id; m.goed = keurt(m); return m; });

    /* Het controlegeval: één zin van veertig woorden, herhaald. Dit is precies wat een nachttaak
       zou kunnen toevoegen als niemand kijkt. */
    const lang = ('Aunque la historia de este país es larga y complicada y llena de nombres que ' +
      'nadie recuerda del todo, la verdad es que casi todo lo que ha pasado aquí desde el principio ' +
      'se puede contar en una sola frase que no termina nunca. ').repeat(4);
    const slecht = meet(lang);

    return { echt: echt, slecht: slecht, slechtGoed: keurt(slecht) };
  });
  maat.echt.forEach(function (m) {
    console.log('   ' + m.id.padEnd(8) + String(m.woorden).padStart(4) + 'w  ' + String(m.zinnen).padStart(3) +
      ' zinnen  gem ' + String(m.gem).padStart(4) + '  langste ' + m.langste);
  });
  ok(maat.echt.every(function (m) { return m.goed; }),
    'alle tien blijven op de maat van de goedgekeurde tekst (' +
    (maat.echt.filter(function (m) { return !m.goed; }).map(function (m) { return m.id; }).join(', ') || 'geen afwijkers') + ')');
  console.log('   verzonnen lange tekst: ' + JSON.stringify(maat.slecht));
  /* Het controlegeval valt met opzet binnen het woordenbereik (176 woorden), zodat hij alleen op
     de zinslengte zakt. Zakte hij ook op de lengte, dan wist je niet welke helft van de meting
     werkt. */
  ok(maat.slecht.woorden >= 140 && maat.slecht.woorden <= 210,
    'CONTROLE: de verzonnen tekst zit binnen het woordenbereik (' + maat.slecht.woorden + '), dus hij zakt alleen op de zinnen');
  ok(maat.slechtGoed === false, 'en een tekst met zinnen van veertig woorden wordt wél afgekeurd');

  // ---- 4. de vragen ----
  console.log('\n-- 4. de vragen zijn beantwoordbaar --');
  const vragen = await page.evaluate(() => {
    const mis = [];
    let n = 0;
    BOOK.filter(function (h) { return h.id.indexOf('vida-') === 0; }).forEach(function (h) {
      const vs = h.vragen || [];
      if (vs.length !== 4) mis.push(h.id + ': ' + vs.length + ' vragen');
      vs.forEach(function (v, i) {
        n++;
        if (!v.q || !v.q.trim()) mis.push(h.id + ' vraag ' + i + ' heeft geen tekst');
        if (!v.opts || v.opts.length !== 3) mis.push(h.id + ' vraag ' + i + ': geen drie opties');
        if (!(v.c >= 0 && v.c < (v.opts || []).length)) mis.push(h.id + ' vraag ' + i + ': antwoord wijst buiten de opties');
        const uniek = {};
        (v.opts || []).forEach(function (o) { uniek[String(o).toLowerCase().trim()] = 1; });
        if (Object.keys(uniek).length !== (v.opts || []).length) mis.push(h.id + ' vraag ' + i + ': twee opties zijn hetzelfde');
      });
    });
    return { n: n, mis: mis };
  });
  ok(vragen.n === 40, 'veertig vragen in totaal (' + vragen.n + ')');
  ok(vragen.mis.length === 0, 'en er mankeert niets aan (' + (vragen.mis.join('; ') || 'geen') + ')');

  // ---- 5. het scherm ----
  console.log('\n-- 5. het hoofdstuk tekent --');
  const scherm = await page.evaluate(() => {
    show('lezen', true); startBoek('vida-1');
    const kaart = document.getElementById('lezenCard');
    const h = BOOK.filter(function (x) { return x.id === 'vida-1'; })[0];
    return {
      alineas: kaart.querySelectorAll('p').length,
      knoppen: kaart.querySelectorAll('.leesvertknop').length,
      hoort: String(h.tekst).split('\n\n').filter(function (p) { return p.trim(); }).length,
      titel: (kaart.textContent || '').indexOf('cena') !== -1
    };
  });
  console.log('   vida-1: ' + JSON.stringify(scherm));
  ok(scherm.knoppen === scherm.hoort, 'één vertaalknop per alinea (' + scherm.knoppen + ' van ' + scherm.hoort + ')');
  ok(scherm.titel, 'en de tekst staat er ook echt');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
