// pw-doosje.js (13 sep, v23.254) - telt het grammaticadoosje ook wat er goed ging?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 13 september: "ik blijf te lang hangen bij een doosje. Een fout en ik kom niet verder
// (zie bijv el en la). Soms maak ik een slordigheidsfoutje of weet ik iets niet, maar als je niet
// alleen de fouten maar ook wanneer het goed gaat telt zul je zien dat ik dit allang gehad heb."
//
// Zijn scherm zei het zelf, in één regel: "El of la · doos 0/5 · 93% goed deze week".
//
// GEMETEN, met de echte gramBij(), 300 lopen van 30 dagen op genero (vijf patronen, zes antwoorden
// per dag):
//
//     goed        eindigde op doos 0      haalde doos 5
//     100%               0%                   100%
//      97%              22%                    29%
//      93%              45%                     6%
//      85%              68%                     0%
//
// Alleen een FOUTLOZE loop kwam betrouwbaar boven. Twee dingen samen deden dat: één misser vandaag
// zette de doos op 0, en een concept is zo sterk als zijn ZWAKSTE van vijf patroondoosjes. De doos
// mat dus je slechtste laatste beurt en niet je kennis.
//
//     Een cijfer dat naast het oordeel staat en er niet in meetelt, is een verwijt.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE STAAT VAN DIENST WORDT BIJGEHOUDEN, per doosje, begrensd, nieuwste rechts.
//   2. EEN MISSER TUSSEN BEWIJS DOOR KOST EEN DOOS. Niet alle dozen.
//   3. EEN MISSER ZONDER BEWIJS KOST NOG STEEDS ALLES. Dit is de controle die telt: als de zachtere
//      regel iedereen doorlaat, is hij geen regel maar een cadeau.
//   4. TE WEINIG GESCHIEDENIS IS GEEN GESCHIEDENIS. Onder de zes antwoorden geldt de oude regel:
//      nul is geen bericht, en te weinig ook niet.
//   5. EN DE UITKOMST OVER DERTIG DAGEN KLOPT. Dezelfde simulatie als hierboven, en met dezelfde
//      eis aan beide kanten: wie het kent komt boven, wie het niet kent niet.
//      Meet de uitkomst, niet het mechanisme.
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
  await page.waitForTimeout(700);

  // ---------- 1. de staat van dienst ----------
  console.log('\n1. per doosje wordt bijgehouden hoe het de laatste keren ging');
  const rij = await page.evaluate(() => {
    const st = {};
    for (let i = 0; i < 20; i++) gramRijBij(st, i % 3 !== 0);
    st.rijVoor = st.rij;
    return { rij: st.rij, max: GRAM_RIJ, staat: gramStaat(st),
             // gramStaat leest de rij van VANOCHTEND, niet die van vandaag
             zonderVoor: gramStaat({ rij: st.rij }) };
  });
  ok(rij.rij.length === rij.max, 'de rij is begrensd op ' + rij.max + ' (staat: ' + rij.rij.length + ')');
  ok(/^[01]+$/.test(rij.rij), 'en bestaat uit enen en nullen ("' + rij.rij + '")');
  ok(rij.staat && rij.staat.n === rij.max, 'gramStaat leest hem terug (' + JSON.stringify(rij.staat) + ')');
  ok(rij.zonderVoor === null,
     'CONTROLE: en hij leest de rij van VANOCHTEND, niet die van vandaag — anders verzacht je je eigen misser ' +
     'door er nog wat makkelijke goede antwoorden omheen te zetten');
  const nieuwste = await page.evaluate(() => {
    const st = { rij: '111111' };
    gramRijBij(st, false);
    return st.rij;
  });
  ok(nieuwste === '1111110', 'de nieuwste staat rechts ("' + nieuwste + '")');

  // ---------- 2 t/m 4. wat een misser kost ----------
  console.log('\n2. wat een misser kost, hangt af van wat eraan voorafging');
  const gevallen = await page.evaluate(() => {
    const echteToday = window.today;
    function loop(reeks, start) {
      S.gram = {};
      const d0 = new Date('2026-07-01T12:00:00Z');
      reeks.forEach((goed, i) => {
        const dag = new Date(d0.getTime() + i * 86400000).toISOString().slice(0, 10);
        window.today = () => dag;
        gramBij('porpara', goed, 3, 0, 'microles');
      });
      const st = S.gram['porpara#0'];
      return { box: st.box, rij: st.rij, boxVoor: st.boxVoor, slordig: gramSlordig(st) };
    }
    const uit = {};
    // tien dagen goed, dan een misser
    uit.slordig = loop([true, true, true, true, true, true, true, true, true, true, false]);
    // de doos zoals hij stond vlak voor die misser
    uit.slordigVoor = uit.slordig.boxVoor;
    // om en om: geen staat van dienst, wel genoeg antwoorden
    uit.onbekend = loop([true, false, true, false, true, false, true, false, true, false, false]);
    // maar vier antwoorden: te weinig om iets te vinden
    uit.tekort = loop([true, true, true, false]);
    // en alles op EEN dag: dat is geen staat van dienst maar dezelfde sessie
    S.gram = {};
    window.today = () => '2026-07-01';
    [true, true, true, false, true, true, true, true].forEach((g) => gramBij('eendag', g, 3, 0, 'microles'));
    uit.eenDag = { box: S.gram['eendag#0'].box, rij: S.gram['eendag#0'].rij,
                   rijVoor: S.gram['eendag#0'].rijVoor };
    window.today = echteToday;
    return uit;
  });
  ok(gevallen.slordig.slordig === true,
     'tien keer goed en dan een misser telt als slordigheid (rij "' + gevallen.slordig.rij + '")');
  ok(gevallen.slordig.box === Math.max(0, gevallen.slordigVoor - 1),
     'en kost precies EEN doos: van ' + gevallen.slordigVoor + ' naar ' + gevallen.slordig.box);
  ok(gevallen.slordig.box > 0, 'dus je staat niet meer op nul na een slordigheidsfoutje');

  console.log('\n3. maar wie het onderwerp niet kent valt gewoon naar nul');
  ok(gevallen.onbekend.slordig === false,
     'om en om goed en fout is geen staat van dienst (rij "' + gevallen.onbekend.rij + '")');
  ok(gevallen.onbekend.box === 0,
     'CONTROLE: dan kost een misser nog steeds ALLE dozen (doos ' + gevallen.onbekend.box + ')');

  console.log('\n4. en te weinig geschiedenis is geen geschiedenis');
  ok(gevallen.eenDag.rijVoor === '',
     'zeven goede antwoorden en één misser op DEZELFDE dag zijn geen staat van dienst (rijVoor "' +
     gevallen.eenDag.rijVoor + '", rij "' + gevallen.eenDag.rij + '")');
  ok(gevallen.eenDag.box === 0,
     'CONTROLE: dus die dag eindigt gewoon op nul (doos ' + gevallen.eenDag.box + '). ' +
     'Anders kun je je eigen misser wegpoetsen in dezelfde sessie');
  ok(gevallen.tekort.rij.length < 6, 'vier antwoorden is minder dan de drempel (rij "' + gevallen.tekort.rij + '")');
  ok(gevallen.tekort.box === 0, 'CONTROLE: dan geldt de oude regel (doos ' + gevallen.tekort.box + ')');

  // ---------- 5. de uitkomst over dertig dagen ----------
  console.log('\n5. en dan de uitkomst, met dezelfde simulatie als de meting');
  const sim = await page.evaluate(() => {
    const echteToday = window.today;
    function loop(dagen, perDag, foutKans, patronen, zaad) {
      let rnd = zaad || 1;
      const r = () => { rnd = (rnd * 1103515245 + 12345) & 0x7fffffff; return rnd / 0x7fffffff; };
      S.gram = {};
      const d0 = new Date('2026-07-01T12:00:00Z');
      for (let d = 0; d < dagen; d++) {
        const dag = new Date(d0.getTime() + d * 86400000).toISOString().slice(0, 10);
        window.today = () => dag;
        for (let i = 0; i < perDag; i++) gramBij('genero', r() >= foutKans, 3, Math.floor(r() * patronen), 'microles');
      }
      return gramLees('genero').box;
    }
    function verdeel(foutKans) {
      const tel = [0, 0, 0, 0, 0, 0];
      const N = 200;
      for (let s = 1; s <= N; s++) tel[loop(30, 6, foutKans, 5, s * 7919)]++;
      return { opNul: Math.round(100 * tel[0] / N), hoog: Math.round(100 * (tel[4] + tel[5]) / N) };
    }
    const uit = { f00: verdeel(0.0), f03: verdeel(0.03), f07: verdeel(0.07), f15: verdeel(0.15), f30: verdeel(0.30) };
    window.today = echteToday;
    return uit;
  });
  console.log('     foutloos: ' + JSON.stringify(sim.f00) + '   97%: ' + JSON.stringify(sim.f03) +
              '   93%: ' + JSON.stringify(sim.f07) + '   85%: ' + JSON.stringify(sim.f15) +
              '   70%: ' + JSON.stringify(sim.f30));
  ok(sim.f00.hoog === 100 && sim.f00.opNul === 0, 'foutloos komt nog steeds altijd boven');
  ok(sim.f03.opNul <= 5, '97% goed staat vrijwel nooit meer op nul (' + sim.f03.opNul + '%, was 22%)');
  ok(sim.f07.opNul <= 20, '93% goed staat nog zelden op nul (' + sim.f07.opNul + '%, was 45%)');
  ok(sim.f07.hoog >= 50, 'en komt nu meestal in doos 4 of 5 (' + sim.f07.hoog + '%, was 12%)');
  ok(sim.f15.opNul >= 25,
     'CONTROLE: 85% goed staat nog vaak op nul (' + sim.f15.opNul + '%) — de regel is geen cadeau');
  ok(sim.f30.hoog <= 10,
     'CONTROLE: 70% goed komt vrijwel nooit hoog (' + sim.f30.hoog + '%) — wie het niet kent, komt niet door');

  ok(errs.length === 0, 'geen javascriptfouten' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));

  await browser.close();
  console.log(fout ? '\n' + fout + ' fout' : '\nalles groen');
  process.exit(fout ? 1 : 0);
})();
