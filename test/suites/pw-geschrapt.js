// pw-geschrapt.js (20 aug, v23.147) — is Aventura echt weg, en staat wat eruit moest blijven er nog?
//
// WAAROM DIT ER IS
//
// Stefan: "we moeten denk ik echt dingen schrappen ook al is het goedkoop en er moet een balans zijn
// tussen makkelijk te doen (ontspanning, beloning, leuk daarom kruiswoord en woordenzoeker) maar
// andere dingen aventure, letras, musica zijn denk ik overbodig."
//
// Aventura was 2057 regels, 4,1 procent van het bestand, en het grootste enkele onderdeel van de
// app. Twee dingen woonden erin die de rest van de app nodig heeft: de geluidsmotor (Chispa's
// serenade draait erop) en het kruiswoord, dat er om historische redenen in zat.
//
// Een verwijdering van deze grootte kan op twee manieren mislukken. Ze staan hier allebei.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET SPEL IS ECHT WEG. Geen tegel, geen scherm, geen functies, geen restje in de dagkaart.
//   2. DE GELUIDSMOTOR STAAT ER NOG. Chispa's serenade hangt eraan, en die woonde in het spel.
//   3. HET KRUISWOORD STAAT ER NOG, EN SPEELT. Dit is de kant die Stefan expliciet wilde houden.
//   4. EN TELT NOG STEEDS MEE. spelGetyptBij() is de reden dat het kruiswoord wél je doosjes raakt
//      en de woordenzoeker niet: je typt het woord, dus het is ophalen.
//   5. LETRAS BLIJFT. Ik had hem afgeschreven als "vorm zonder betekeniscue"; dat klopt niet. Je
//      krijgt de Nederlandse betekenis erbij, dus het is betekenis naar vorm ophalen met de letters
//      als steun. Dat hoort bewaakt te worden, juist omdat ik hem bijna had weggegooid.
//   6. EN DE SPEELTUIN ZEGT WAT HIJ IS. Ontspanning die niet meetelt, en dat staat er ook.
//
// HET CONTROLEGEVAL
//
// Deze suite is groen te krijgen door alles weg te gooien: dan klopt punt 1 en 5 en is de app stuk.
// Daarom staan 2, 3 en 4 ertegenover, en die meten niet dat de functies bestaan maar dat ze draaien.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwGs' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl'; S.speelAlles = true; S.spelAlles = true;
    // genoeg woorden om een kruiswoord te kunnen bouwen
    S.srs = {};
    WORDS.slice(0, 120).forEach(function (w) { S.srs[w.id] = { box: 2, due: today(), n: 3 }; });

    // ---- 1. het spel is echt weg ----
    uit.functies = ['renderFunAvt', 'avtGear', 'avtSave', 'avtStartWereld', 'avtMove', 'avtSnakeStart',
                    'avtAhorStart', 'avtBaasStart', 'avtStopAlles', 'at', 'AVT_TXT', 'AVT_SCHERMEN']
      .filter(function (n) { return typeof window[n] !== 'undefined'; });
    uit.inSpelInfo = spelInfo().map(function (x) { return x.v; });
    uit.inDagSpellen = dagSpellen().map(function (x) { return x.v; });
    uit.eis = Object.keys(SPEEL_EIS);
    /* Letras had ik afgeschreven als "vorm zonder betekeniscue". Dat is de bewering die hier
       sneuvelt: elk open plekje draagt de Nederlandse betekenis, dus je haalt het Spaanse woord op
       vanuit de betekenis. Zonder die cue zou het een anagram zijn en dan hoorde hij er niet. */
    ltSpel = null;
    try { ltNieuw(); } catch (e) {}
    uit.letrasDoelen = ltSpel ? ltSpel.doelen.length : 0;
    uit.letrasBetekenis = !!(ltSpel && ltSpel.doelen.length &&
      ltSpel.doelen.every(function (d) { return !!d.nl && !!d.es; }));
    uit.vast = SPEL_VAST.slice();

    // ---- 2. de geluidsmotor staat er nog ----
    uit.geluid = ['avtCtx', 'avtNoot', 'avtPluk', 'avtPalmas', 'avtSfx']
      .filter(function (n) { return typeof window[n] !== 'function'; });
    uit.cadens = typeof AVT_CADENS !== 'undefined' && AVT_CADENS.length > 0;
    // en de serenade van Chispa draait er echt op, zonder te struikelen
    let serenadeFout = null;
    try { if (typeof chispaSerenade === 'function') chispaSerenade(); } catch (e) { serenadeFout = e.message; }
    uit.serenadeFout = serenadeFout;

    // ---- 3. het kruiswoord staat er nog, en speelt ----
    uit.kruisTegel = spelInfo().some(function (x) { return x.v === 'kruis'; });
    funView = 'kruis'; kruisLos = null;
    show('speeltuin', true); renderFun();
    const el = document.getElementById('funCard');
    uit.kruisScherm = el.textContent.replace(/\s+/g, ' ').slice(0, 90);
    uit.kruisCellen = el.querySelectorAll('[data-avtkw]').length;
    uit.kruisGebouwd = !!kruisLos;
    uit.kruisNamen = ['kruisBouw', 'kruisCellen', 'kruisBekend', 'renderKruisUI', 'renderFunKruisLos']
      .filter(function (n) { return typeof window[n] !== 'function'; });

    // ---- 4. en telt nog steeds mee ----
    /* Het verschil zit in het plafond en niet in de stapgrootte: allebei zetten ze een kaartje één
       doosje omhoog. Dus zetten we een woord precies op het spelplafond en kijken wie er nog
       overheen mag. */
    const w = WORDS.filter(function (x) { return S.srs[x.id]; })[0];
    S.srs[w.id] = { box: SPEL_PLAFOND, due: today(), n: 3 };
    spelGetyptBij(w, true, true);
    uit.naGetypt = { box: S.srs[w.id].box, k: S.srs[w.id].k || 0 };
    const w2 = WORDS.filter(function (x) { return S.srs[x.id]; })[3];
    S.srs[w2.id] = { box: SPEL_PLAFOND, due: today(), n: 3 };
    spelSrsBij(w2.id);
    uit.naSpel = S.srs[w2.id].box;
    uit.plafond = SPEL_PLAFOND;

    funView = null; show('speeltuin'); renderFun();
    uit.speeltuinTekst = document.getElementById('funCard').textContent.replace(/\s+/g, ' ');
    return uit;
  });

  console.log('\n-- 1. het spel is echt weg --');
  console.log('   tegels: ' + r.inSpelInfo.join(','));
  ok(r.functies.length === 0, 'geen enkele functie of tabel is blijven hangen (' + (r.functies.join(',') || 'niets') + ')');
  ok(r.inSpelInfo.indexOf('avt') === -1, 'geen tegel in de Speeltuin');
  ok(r.inDagSpellen.indexOf('avt') === -1, 'en niet op de dagkaart');
  ok(r.vast.indexOf('avt') === -1, 'en hij staat niet meer vast vooraan (' + r.vast.join(',') + ')');

  console.log('\n-- 5. Letras blijft --');
  ok(r.inSpelInfo.indexOf('letras') !== -1, 'de tegel staat er nog');
  ok(r.eis.indexOf('letras') !== -1, 'en zijn ontgrendeleis ook (' + r.eis.join(',') + ')');
  ok(r.letrasBetekenis, 'en elk van de ' + r.letrasDoelen + ' open plekken draagt de Nederlandse betekenis, dus het is ophalen');

  console.log('\n-- 2. de geluidsmotor staat er nog --');
  ok(r.geluid.length === 0, 'de vijf geluidsfuncties bestaan (' + (r.geluid.join(',') || 'alle vijf') + ')');
  ok(r.cadens, 'en de cadens waar de serenade op speelt');
  ok(r.serenadeFout === null, 'Chispa\'s serenade draait zonder te struikelen (' + (r.serenadeFout || 'goed') + ')');

  console.log('\n-- 3. het kruiswoord staat er nog, en speelt --');
  console.log('   ' + r.kruisScherm);
  ok(r.kruisTegel, 'de tegel staat er');
  ok(r.kruisNamen.length === 0, 'en de functies heten nu naar zichzelf (' + (r.kruisNamen.join(',') || 'alle vijf') + ')');
  ok(r.kruisGebouwd, 'er wordt echt een kruiswoord gebouwd');
  ok(r.kruisCellen >= 4, 'met omschrijvingen om aan te klikken (' + r.kruisCellen + ')');

  console.log('\n-- 4. en telt nog steeds mee --');
  ok(r.naGetypt.box > r.plafond, 'een getypt woord mag hoger dan het spelplafond (' + r.naGetypt.box + ' > ' + r.plafond + ')');
  ok(r.naGetypt.k === 1, 'en het telt als bewijs dat je het kon opschrijven');
  ok(r.naSpel === r.plafond, 'het controlegeval: een spel zonder typen komt niet boven het plafond (' + r.naSpel + ')');

  console.log('\n-- 6. en de Speeltuin zegt wat hij is --');
  ok(/telt niet mee/.test(r.speeltuinTekst), 'er staat dat het niet meetelt, en dat dat de bedoeling is');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
