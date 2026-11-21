// pw-kaaldoosje.js (21 nov, v23.278) - mag het doosje dat alleen omlaag kan beslissen of iets af is?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 21 november: "ik heb het idee dat er niet veel nieuwe content bij komt en dat grammatica
// beetje blijft hangen. Zoek uit of er wel progressie wordt gemeten maar het gewoon langzaam gaat."
//
// Gemeten op zijn echte doosjes van 20 november, door de app zelf heen gehaald:
//
//     genero   249 antwoorden
//              #0 doos 5   #1 doos 5   #2 doos 5   #3 doos 5   #4 doos 5
//              kaal doos 1
//
// gramLees() gaf het ZWAKSTE doosje terug, dus genero gold als onaf. gcFocusKlaar() liet het
// daarom nooit los, en de dagles biedt er twee aan. In de tijdreeks van zijn logboek kwam genero
// terug op 13 van de 17 dagen waarop hij grammatica deed, terwijl 30 onderwerpen open stonden en
// 68 doosjes toe waren.
//
// Het kale doosje is geen patroon. Het is de plek waar fouten landen die je in het wild maakt: de
// losse oefenzin, de chatcorrector, het toetsje, de clasificador roepen gramBij() aan zonder
// patroonnummer. De microles schrijft naar de patroondoosjes. Dat doosje krijgt dus nooit gerichte
// oefening en kan alleen omlaag.
//
//     Een doosje dat alleen omlaag kan, mag niet beslissen of iets af is.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. HET OORDEEL KOMT VAN DE PATROONDOOSJES. Alle patronen op doos 5 en het kale op 1: dan is
//      het onderwerp af, en dan verlaat het de focus.
//   2. HET CONTROLEGEVAL. Dezelfde toestand, maar met het kale doosje meegerekend zoals vroeger,
//      hoort juist NIET af te zijn. Zonder dit zou proef 1 ook slagen als "klaar" altijd waar is.
//   3. DE ZWAKSTE-REGEL BLIJFT BINNEN DE PATRONEN. Een patroon op doos 0 houdt het onderwerp
//      tegen, ook als de vier andere op 5 staan. Dat was de reden dat die regel er staat en die
//      reden verandert niet.
//   4. EEN VERSE FOUT IN HET WILD KOMT NOG STEEDS TERUG. Dat is de andere helft van de taak van het
//      kale doosje, en die blijft. Zonder deze proef zou proef 1 te halen zijn door het kale
//      doosje helemaal te negeren, en dan is de app niet streng maar doof.
//   5. ZONDER PATRONEN TELT HET KALE DOOSJE GEWOON. Een handgeschreven onderwerp heeft niets
//      anders, en "geen bewijs" mag niet "dus af" gaan betekenen.
//   6. DE REGEL STAAT IN ELKE HERHALING, EN HIJ STAAT NA DE EERSTE VRAAG. Stefan vroeg om uitleg
//      vóór elke toets; dit is de ene plek waar deze ronde hem tegenspreekt. Uitleg vlak voor de
//      toets meet of je net gelezen hebt (Kornell en Bjork), en dat is dezelfde reden waarom de
//      drill sinds v23.261 niet meetelt voor het doosje.
//   7. EN DE HERHALING WORDT ER NIET LANGER VAN. Dezelfde vragen, alleen gesplitst.
//   8. HET ONDERHOUD LEVERT MEER DAN EEN ONDERWERP. Drie doosjes uit DRIE VERSCHILLENDE
//      onderwerpen, want drie patronen van hetzelfde onderwerp is nog steeds één onderwerp.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwKd' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---------- 1 tot en met 3: wie beslist of een onderwerp af is ----------
  console.log('\n-- 1 tot en met 3. het oordeel komt van de patronen --');
  const oordeel = await page.evaluate(() => {
    const ver = '2027-06-01';
    function zet(sleutel, box) {
      S.gram[sleutel] = { box: box, due: ver, goed: 20, fout: 2, laatst: '', rij: '111111' };
    }
    function stand(cid) {
      const l = gramLees(cid);
      return { box: l.box, kaalBox: l.kaalBox, klaar: (l.box || 0) >= GC_FOCUS_KLAAR, doosjes: l.doosjes };
    }
    const c = GC_CONCEPTEN.filter(function (x) { return (x.patronen || []).length >= 3; })[0];

    // de gemeten toestand van genero: alle patronen boven, het kale doosje onderaan
    S.gram = {};
    zet(c.id, 1);
    (c.patronen || []).forEach(function (_, i) { zet(c.id + '#' + i, 5); });
    const alsGenero = stand(c.id);

    // het controlegeval: dezelfde toestand, maar geteld zoals vroeger (zwakste van ALLE doosjes)
    const oudeManier = (function () {
      let zwak = null;
      gramDoosjes(c.id).forEach(function (x) {
        if (!zwak || (x.st.box || 0) < (zwak.box || 0)) zwak = x.st;
      });
      return zwak ? (zwak.box || 0) : 0;
    })();

    // en de zwakste-regel binnen de patronen zelf
    S.gram = {};
    zet(c.id, 5);
    (c.patronen || []).forEach(function (_, i) { zet(c.id + '#' + i, i === 1 ? 0 : 5); });
    const eenPatroonOnder = stand(c.id);

    // zonder patroondoosjes telt het kale gewoon
    S.gram = {};
    zet(c.id, 1);
    const alleenKaal = stand(c.id);

    return { cid: c.id, patronen: (c.patronen || []).length, alsGenero: alsGenero,
             oudeManier: oudeManier, eenPatroonOnder: eenPatroonOnder, alleenKaal: alleenKaal,
             klaarBij: GC_FOCUS_KLAAR };
  });

  console.log('   proefkonijn: ' + oordeel.cid + ' met ' + oordeel.patronen + ' patronen');
  console.log('   alle patronen op 5, kaal op 1  -> doos ' + oordeel.alsGenero.box +
    ' (oude manier: doos ' + oordeel.oudeManier + ')');
  ok(oordeel.alsGenero.klaar,
    'alle patronen af en alleen het kale doosje laag: het onderwerp is af (doos ' + oordeel.alsGenero.box + ')');
  ok(oordeel.oudeManier < oordeel.klaarBij,
    'CONTROLE: met het kale doosje meegerekend zou het NIET af zijn (doos ' + oordeel.oudeManier + ')');
  ok(oordeel.alsGenero.kaalBox === 1,
    'en het kale doosje is niet weg, het staat er nog bij (kaalBox ' + oordeel.alsGenero.kaalBox + ')');
  ok(!oordeel.eenPatroonOnder.klaar,
    'een patroon op doos 0 houdt het onderwerp wel tegen, ook met vier patronen op 5 (doos ' +
      oordeel.eenPatroonOnder.box + ')');
  ok(!oordeel.alleenKaal.klaar && oordeel.alleenKaal.box === 1,
    'zonder patroondoosjes telt het kale doosje gewoon mee (doos ' + oordeel.alleenKaal.box + ')');

  // ---------- 4. een verse fout in het wild komt terug ----------
  console.log('\n-- 4. en een slordigheid in een vrije zin brengt het onderwerp terug --');
  const wild = await page.evaluate(() => {
    const c = GC_CONCEPTEN.filter(function (x) { return (x.patronen || []).length >= 3; })[0];
    function bouw(kaalBox) {
      S.gram = {};
      S.gram[c.id] = { box: kaalBox, due: today(), goed: 9, fout: 5, laatst: today(), rij: '0' };
      (c.patronen || []).forEach(function (_, i) {
        S.gram[c.id + '#' + i] = { box: 5, due: '2027-06-01', goed: 20, fout: 1, laatst: '', rij: '111111' };
      });
      // het ledger zegt dat het vandaag misging: dat is wat gcVersFout leest
      S.gramLog = {};
      S.gramLog[today()] = {}; S.gramLog[today()][c.id] = { n: 2, goed: 1 };
    }
    bouw(0);
    const naFout = gcStaatFout(gramLees(c.id), c.id);
    // het controlegeval: zelfde dag, alles goed in het wild -> geen bericht
    bouw(0);
    S.gramLog[today()][c.id] = { n: 2, goed: 2 };
    const naGoed = gcStaatFout(gramLees(c.id), c.id);
    return { cid: c.id, naFout: naFout, naGoed: naGoed };
  });
  ok(wild.naFout === true,
    'alle patronen op 5, maar vandaag een misser in het wild: het onderwerp staat als fout');
  ok(wild.naGoed === false,
    'CONTROLE: dezelfde dag alles goed in het wild, dan juist niet');

  // ---------- 5 en 6. de regel staat in elke herhaling ----------
  console.log('\n-- 5 en 6. de regel komt terug, en hij staat na de eerste vraag --');
  const opfris = await page.evaluate(() => {
    const c = GC_CONCEPTEN.filter(function (x) {
      return (x.patronen || []).length >= 3 && String(x.uitleg || '').trim();
    })[0];
    function bouwBij(box) {
      S.gram = {};
      S.gram[c.id + '#0'] = { box: box, due: today(), goed: 9, fout: 1, laatst: '', rij: '111111' };
      let o = null;
      try { o = gcVernieuw(gcOpfrisId(c.id, 0)); } catch (e) { o = null; }
      if (!o) return null;
      const stappen = o.stappen.map(function (s) {
        return { kop: String(ct(s.kop, s.kopEn) || ''), vragen: s.vragen.length,
                 uitleg: String(ct(s.uitleg, s.uitlegEn) || '').replace(/<[^>]*>/g, '').trim().length };
      });
      return { onderhoud: !!o.onderhoud, stappen: stappen,
               totaal: stappen.reduce(function (a, s) { return a + s.vragen; }, 0) };
    }
    return { cid: c.id, leren: bouwBij(1), onderhoud: bouwBij(GRAM_ONDERHOUD_DOOS),
             vragenN: GC_OPFRIS_VRAGEN, onderhoudN: GC_OPFRIS_ONDERHOUD };
  });

  ['leren', 'onderhoud'].forEach(function (soort) {
    const o = opfris[soort];
    if (!o) { fout++; console.log('  ✗ geen opfrisser gebouwd voor ' + soort); return; }
    console.log('   ' + soort + ': ' + o.stappen.map(function (s) {
      return s.kop + ' (' + s.vragen + 'v, ' + s.uitleg + ' tekens uitleg)';
    }).join('  ->  '));
    ok(o.stappen.length === 2, soort + ': de opfrisser heeft twee stappen (' + o.stappen.length + ')');
    ok(o.stappen[0].uitleg === 0 && o.stappen[0].vragen >= 1,
      soort + ': eerst een vraag en geen uitleg, want ophalen gaat voor lezen');
    ok(o.stappen[1].uitleg > 40 && o.stappen[1].vragen >= 1,
      soort + ': daarna de regel, en daarna nog een vraag (' + o.stappen[1].uitleg + ' tekens)');
  });
  ok(opfris.leren && opfris.leren.totaal === opfris.vragenN,
    'de herhaling wordt niet langer: ' + (opfris.leren ? opfris.leren.totaal : '?') +
      ' vragen, net als voorheen (' + opfris.vragenN + ')');
  ok(opfris.onderhoud && opfris.onderhoud.totaal === opfris.onderhoudN,
    'en onderhoud is korter: ' + (opfris.onderhoud ? opfris.onderhoud.totaal : '?') +
      ' vragen (' + opfris.onderhoudN + ')');
  ok(opfris.onderhoud && opfris.onderhoud.onderhoud === true,
    'een doosje op doos 3 of hoger wordt als onderhoud gebouwd en niet als les');

  // ---------- 7. het onderhoud levert meer dan één onderwerp ----------
  console.log('\n-- 7. drie onderhoudsbeurten, uit drie verschillende onderwerpen --');
  const onderhoud = await page.evaluate(() => {
    S.gram = {};
    const gekozen = [];
    GC_CONCEPTEN.forEach(function (c) {
      if (!(c.patronen || []).length) return;
      if (gekozen.length >= 5) return;
      gekozen.push(c.id);
      // twee doosjes per onderwerp, allebei lang vervallen en allebei op onderhoudshoogte
      S.gram[c.id + '#0'] = { box: 4, due: '2026-01-01', goed: 20, fout: 1, laatst: '', rij: '111111' };
      if ((c.patronen || []).length > 1) {
        S.gram[c.id + '#1'] = { box: 4, due: '2026-01-02', goed: 20, fout: 1, laatst: '', rij: '111111' };
      }
    });
    const rij = gramOnderhoudRij(GRAM_ONDERHOUD_N);
    const top = gramOnderhoudTop();
    return { gekozen: gekozen, n: GRAM_ONDERHOUD_N,
             rij: rij.map(function (x) { return x.c.id + '#' + x.pi; }),
             onderwerpen: rij.map(function (x) { return x.c.id; })
               .filter(function (v, i, a) { return a.indexOf(v) === i; }).length,
             top: top ? top.c.id + '#' + top.pi : null };
  });
  console.log('   ' + onderhoud.rij.join('  '));
  ok(onderhoud.rij.length === onderhoud.n,
    'de onderhoudsrij levert er ' + onderhoud.n + ' (' + onderhoud.rij.length + ')');
  ok(onderhoud.onderwerpen === onderhoud.rij.length,
    'en allemaal uit een ander onderwerp (' + onderhoud.onderwerpen + ' onderwerpen op ' +
      onderhoud.rij.length + ' beurten)');
  ok(onderhoud.top !== null && onderhoud.rij[0] === onderhoud.top,
    'CONTROLE: de oude eenling staat er nog en is nog steeds de eerste van de rij (' + onderhoud.top + ')');

  ok(errs.length === 0, 'geen pagina-fouten: ' + (errs.slice(0, 3).join(' | ') || 'geen'));

  await browser.close();
  console.log(fout ? '\n' + fout + ' GEFAALD' : '\nalles goed');
  process.exit(fout ? 1 : 0);
})().catch(function (e) { console.error(e); process.exit(1); });
