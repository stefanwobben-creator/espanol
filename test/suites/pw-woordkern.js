// pw-woordkern.js (6 sep, v23.246): is een streep tussen twee vormen iets anders dan tussen twee lidwoorden?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 6 september, met een schermafbeelding van zijn memory-spel: een kaartje met alleen het
// woord "el" erop, naast een kaartje "de zanger(es)". Die twee matchen ook nog, want ze komen uit
// hetzelfde woord.
//
// De oorzaak stond op zes plekken, steeds in dezelfde vorm:
//
//     w.es.split("/")[0]
//
// Bedoeld voor "claro / clara": twee vormen, neem de eerste. Maar bij vijf woorden scheidt die
// streep geen vormen maar twee LIDWOORDEN van hetzelfde woord:
//
//     el / la cantante        el / la estudiante      el / la hispanohablante
//     el / la taxista         el / la turista
//
// Daar levert die regel het woord "el" op, en dat is geen woord. Gemeten gevolg van die vijf woorden
// op zes schermen: een memorykaart die "el" heet, een lege kern in de woordenzoeker (dus ze komen er
// nooit in), geen voorbeeldzin in het woordenboek, sorteren onder de E, een werkwoordsopzoeker die
// ze niet vindt, en een woordsoort die niet "zn" wordt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE VIJF WOORDEN HOUDEN HUN KERN. woordEerste() maakt van "el / la cantante" niet "el" maar
//      "el cantante".
//   2. EN "CLARO / CLARA" VERANDERT NIET. Dat is het controlegeval: een streep tussen twee echte
//      vormen hoort nog steeds de eerste te geven, anders is de reparatie een nieuwe fout.
//   3. GEEN ENKELE MEMORYKAART IS EEN KAAL LIDWOORD. Gebouwd: alle vijf de woorden in de stapel.
//   4. HET WOORDENBOEK SORTEERT ZE OP HUN WOORD. Ze stonden onder de E van "el".
//   5. ZE ZIJN EEN ZELFSTANDIG NAAMWOORD. woordSoort() zag "el" zonder spatie en gaf niets terug.
//   6. EN DE VIJF BESTAAN ECHT. Zonder deze telling zou de suite groen staan op een lege lijst.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwWk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1, 2 en 6. de regel zelf ----
  console.log('\n-- 1, 2 en 6. wat woordEerste van een streep maakt --');
  const kern = await page.evaluate(() => {
    const art = { el: 1, la: 1, los: 1, las: 1, un: 1, una: 1, unos: 1, unas: 1 };
    const alle = [].concat(
      typeof WORDS !== 'undefined' ? WORDS : [],
      typeof K_WORDS !== 'undefined' ? K_WORDS : [],
      typeof C_WORDS !== 'undefined' ? C_WORDS : [],
      typeof B_WORDS !== 'undefined' ? B_WORDS : []
    );
    // de woorden waar de streep twee lidwoorden scheidt
    const lidwoordig = alle.filter(function (w) {
      const d = String(w.es || '').split('/');
      return d.length > 1 && art[d[0].trim().toLowerCase()];
    });
    return {
      totaal: alle.length,
      metStreep: alle.filter(function (w) { return String(w.es || '').indexOf('/') !== -1; }).length,
      lidwoordig: lidwoordig.map(function (w) {
        return { es: w.es, kern: woordEerste(w.es), kaal: !!art[woordEerste(w.es).trim().toLowerCase()] };
      }),
      // het controlegeval: een streep tussen twee echte vormen
      vormen: ['claro / clara', 'pequeño / pequeña', 'un / una'].map(function (s) {
        return { in: s, uit: woordEerste(s) };
      }),
      zonderStreep: woordEerste('la mesa')
    };
  });
  kern.lidwoordig.forEach(function (x) {
    console.log('   ' + x.es.padEnd(26) + '-> ' + x.kern);
  });
  console.log('   controle: ' + kern.vormen.map(function (v) { return v.in + ' -> ' + v.uit; }).join('  ·  '));
  ok(kern.lidwoordig.length >= 5,
    'CONTROLE: er zijn woorden waar de streep twee lidwoorden scheidt (' + kern.lidwoordig.length + ')');
  ok(kern.metStreep > 50,
    'CONTROLE: en veel meer woorden met een streep die geen lidwoord is (' + kern.metStreep + ')');
  ok(kern.lidwoordig.every(function (x) { return !x.kaal; }),
    'geen van die woorden houdt alleen een lidwoord over');
  ok(kern.lidwoordig.every(function (x) { return x.kern.split(' ').length >= 2; }),
    'ze houden hun lidwoord én hun woord ("' + (kern.lidwoordig[0] || {}).kern + '")');
  ok(kern.vormen[0].uit === 'claro',
    'CONTROLE: "claro / clara" geeft nog steeds gewoon claro (' + kern.vormen[0].uit + ')');
  ok(kern.vormen[1].uit === 'pequeño',
    'CONTROLE: en "pequeño / pequeña" ook (' + kern.vormen[1].uit + ')');
  ok(kern.zonderStreep === 'la mesa',
    'CONTROLE: een woord zonder streep blijft heel (' + kern.zonderStreep + ')');

  // ---- 3. de memorykaarten ----
  console.log('\n-- 3. geen memorykaart is een kaal lidwoord --');
  const memo = await page.evaluate(() => {
    const art = { el: 1, la: 1, los: 1, las: 1, un: 1, una: 1, unos: 1, unas: 1 };
    // gebouwd: precies de vijf woorden in je stapel, plus genoeg vulling om te kunnen spelen
    S.srs = {};
    const alle = [].concat(typeof WORDS !== 'undefined' ? WORDS : [],
                           typeof K_WORDS !== 'undefined' ? K_WORDS : []);
    const lidwoordig = alle.filter(function (w) {
      const d = String(w.es || '').split('/');
      return d.length > 1 && art[d[0].trim().toLowerCase()];
    });
    lidwoordig.concat(alle.slice(0, 20)).forEach(function (w) {
      S.srs[w.id] = { box: 2, due: today(), n: 3, k: 1 };
    });
    const pool = memPool();
    const kaal = pool.filter(function (p) { return !!art[String(p.es).trim().toLowerCase()]; });
    return { n: pool.length, kaal: kaal.map(function (p) { return p.es + ' = ' + p.nl; }),
             gezet: lidwoordig.length,
             inPool: pool.filter(function (p) { return /cantante|estudiante|taxista|turista|hispanohablante/.test(p.es); })
               .map(function (p) { return p.es; }) };
  });
  console.log('   pool: ' + memo.n + ' woorden, waarvan uit de vijf: ' + (memo.inPool.join(', ') || 'geen'));
  ok(memo.gezet >= 5, 'CONTROLE: de vijf woorden staan echt in de stapel (' + memo.gezet + ')');
  ok(memo.kaal.length === 0,
    'geen enkele memorykaart is een kaal lidwoord (' + (memo.kaal.join(' | ') || 'geen') + ')');
  ok(memo.inPool.length >= 1,
    'en de woorden zelf doen gewoon mee (' + (memo.inPool.join(', ') || 'geen') + ')');

  // ---- 4 en 5. het woordenboek ----
  console.log('\n-- 4 en 5. het woordenboek --');
  const boek = await page.evaluate(() => {
    const art = { el: 1, la: 1, los: 1, las: 1, un: 1, una: 1, unos: 1, unas: 1 };
    const alle = [].concat(typeof WORDS !== 'undefined' ? WORDS : [],
                           typeof K_WORDS !== 'undefined' ? K_WORDS : [],
                           typeof C_WORDS !== 'undefined' ? C_WORDS : []);
    const vijf = alle.filter(function (w) {
      const d = String(w.es || '').split('/');
      return d.length > 1 && art[d[0].trim().toLowerCase()];
    });
    return vijf.map(function (w) {
      let sort = null, soort = null;
      try { sort = dicSorteer(w); } catch (e) { sort = 'KLAPT'; }
      try { soort = woordSoort(w); } catch (e) { soort = 'KLAPT'; }
      return { es: w.es, sort: String(sort), soort: soort };
    });
  });
  boek.forEach(function (b) { console.log('   ' + b.es.padEnd(26) + 'sorteert op "' + b.sort + '", soort ' + b.soort); });
  ok(boek.every(function (b) { return b.sort.indexOf('el') !== 0 && b.sort.indexOf('la') !== 0; }),
    'ze sorteren op hun woord en niet op het lidwoord');
  ok(boek.every(function (b) { return b.soort === 'zn'; }),
    'en ze gelden als zelfstandig naamwoord (' + boek.map(function (b) { return b.soort; }).join(',') + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
