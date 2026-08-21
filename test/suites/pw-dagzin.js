// pw-dagzin.js (21 aug, v23.156) — schrijf je ooit iets voor een echt mens?
//
// WAAROM DIT ER IS
//
// Stefan: "we hadden ook chatten met anderen."
//
// Praten met Chispa staat er sinds v23.144 en zit sinds v23.150 in je les. Praten met een echt mens
// uit je groep niet. Wat er tussen mensen was is de krabbel: een emoji met een vaste Spaanse zin
// eraan vast. Een schouderklopje, geen gesprek.
//
// Het is geen chatvenster geworden, en dat is een keuze: drie gebruikers die op verschillende
// momenten oefenen leveren een leeg venster op, en een leeg venster meldt elke dag dat er niemand
// is. Dat is het probleem van Palabra Duel. Dus asynchroon: één vraag per dag, iedereen dezelfde.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ER IS ELKE DAG EEN VRAAG, EN VOOR IEDEREEN DEZELFDE. Anders is het geen gesprek maar een
//      dagboek. Vast per dag, en morgen een andere.
//   2. JE KUNT ÉÉN ZIN SCHRIJVEN, EN HIJ BLIJFT STAAN. Met de vraag erbij, want een antwoord zonder
//      vraag is over een week onleesbaar.
//   3. DAARNA PAS ZIE JE DE ANDEREN. Dit is de pedagogische kern: lezen vóór schrijven maakt er
//      lezen van, en de productie is juist het punt.
//   4. HET TELT ALS PRODUCEREN. Anders is het decor.
//   5. GEEN GROEP, GEEN KAART. Het controlegeval: iemand zonder groep krijgt geen belofte van een
//      publiek dat niet bestaat.
//   6. EN HET STAAT IN JE VOORSTELLEN NA JE LES, MAAR ALLEEN ALS ER IETS TE SCHRIJVEN VALT.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDz' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl'; S.dagen = { count: 5 };
    S.dagzin = null;

    // ---- 5. het controlegeval: geen groep, geen kaart ----
    S.groepen = null; muurData = null;
    uit.zonderGroep = dagZinHtml();
    uit.zonderGroepVoorstel = (function () {
      const w = lesFlowWinst();
      return !!(w && /vraag van vandaag/i.test(w.kop));
    })();

    // ---- 1. er is elke dag een vraag, en morgen een andere ----
    S.groepen = [{ gcode: 'testgroep', naam: 'Test' }];
    const v = dagVraag();
    uit.vraag = { es: v.es, nl: v.nl };
    uit.zelfde = dagVraag().es === dagVraag().es && dagVraag().es === v.es;
    uit.morgen = dagVraag(addDays(today(), 1)).es;
    uit.aantal = DAGVRAGEN.length;

    // ---- 2. je kunt één zin schrijven, en hij blijft staan ----
    muurData = {
      spelers: [
        { naam: 'Ilona', dagzin: { d: today(), v: v.es, es: 'Hoy he comido paella con mi hermana.' } },
        { naam: 'Martina', dagzin: { d: addDays(today(), -1), v: 'oud', es: 'Ayer no hice nada.' } }
      ]
    };
    show('perfil', true);
    const kaartVoor = dagZinHtml();
    uit.voorSchrijven = {
      heeftInvoer: kaartVoor.indexOf('dagzinInp') !== -1,
      vraagErin: kaartVoor.indexOf(v.es) !== -1,
      // ---- 3. de anderen staan er nog niet ----
      ilona: kaartVoor.indexOf('paella') !== -1
    };

    const xpVoor = S.xp[today()] || 0;
    dagZinBij('  Hoy he trabajado en el jardín.  ');
    uit.opgeslagen = S.dagzin ? { d: S.dagzin.d, v: S.dagzin.v, es: S.dagzin.es } : null;
    uit.xpErbij = (S.xp[today()] || 0) - xpVoor;
    uit.gedaanVink = (S.lesFlowSpel || {}).groepszin === today();

    const kaartNa = dagZinHtml();
    uit.naSchrijven = {
      mijn: kaartNa.indexOf('jard') !== -1,
      ilona: kaartNa.indexOf('paella') !== -1,
      // Martina schreef gisteren, dus die hoort er vandaag niet bij te staan
      martina: kaartNa.indexOf('Ayer no hice') !== -1,
      heeftInvoer: kaartNa.indexOf('dagzinInp') !== -1
    };
    uit.anderen = dagZinAnderen().map(function (a) { return a.naam; });

    // te lang wordt afgekapt, niet geweigerd
    S.dagzin = null;
    dagZinBij('a'.repeat(400));
    uit.afgekapt = S.dagzin.es.length;
    uit.max = DAGZIN_MAX;

    // leeg levert niets op
    S.dagzin = null;
    uit.leegLukt = dagZinBij('   ');
    uit.leegBewaard = !!S.dagzin;

    // ---- 6. en het staat in je voorstellen, maar alleen als er iets te schrijven valt ----
    S.dagzin = null; S.gram = {};
    const w1 = lesFlowWinst();
    uit.voorstelKop = w1 ? w1.kop : null;
    uit.voorstelIsZin = !!(w1 && /vraag van vandaag/i.test(w1.kop));
    dagZinBij('Ya está escrito.');
    const w2 = lesFlowWinst();
    uit.naZinKop = w2 ? w2.kop : null;
    uit.naZinIsZin = !!(w2 && /vraag van vandaag/i.test(w2.kop));

    S.groepen = null; muurData = null; S.dagzin = null;
    return uit;
  });

  console.log('\n-- 1. er is elke dag een vraag --');
  console.log('   "' + r.vraag.es + '" (' + r.vraag.nl + ')');
  ok(!!r.vraag.es && !!r.vraag.nl, 'de vraag staat er in het Spaans, met de vertaling');
  ok(r.zelfde, 'drie keer vragen geeft dezelfde vraag, dus je groep krijgt hem ook');
  ok(r.morgen !== r.vraag.es, 'en morgen een andere (' + r.aantal + ' in de lijst)');

  console.log('\n-- 2 en 3. eerst schrijven, dan pas lezen --');
  ok(r.voorSchrijven.heeftInvoer, 'er staat een invoerveld voordat je iets schreef');
  ok(r.voorSchrijven.vraagErin, 'met de vraag erboven');
  ok(!r.voorSchrijven.ilona, 'het controlegeval: wat Ilona schreef staat er nog niet');
  ok(r.opgeslagen && r.opgeslagen.es === 'Hoy he trabajado en el jardín.', 'je zin staat opgeslagen, zonder spaties eromheen');
  ok(r.opgeslagen && r.opgeslagen.v === r.vraag.es, 'met de vraag erbij, anders is hij over een week onleesbaar');
  ok(r.naSchrijven.mijn, 'daarna staat je eigen zin op de kaart');
  ok(r.naSchrijven.ilona, 'en die van Ilona erbij');
  ok(!r.naSchrijven.martina, 'maar niet die van gisteren (' + r.anderen.join(',') + ')');
  ok(!r.naSchrijven.heeftInvoer, 'en het invoerveld is weg: één zin per dag');
  ok(r.afgekapt === r.max, 'een te lange zin wordt afgekapt op ' + r.max + ' (nu: ' + r.afgekapt + ')');
  ok(r.leegLukt === false && !r.leegBewaard, 'en een lege zin levert niets op');

  console.log('\n-- 4. het telt als produceren --');
  ok(r.xpErbij > 0, 'er komen taco\'s bij (' + r.xpErbij + ')');
  ok(r.gedaanVink, 'en het staat vandaag afgevinkt, dus je krijgt het niet nog eens voorgesteld');

  console.log('\n-- 6. het staat in je voorstellen na je les --');
  ok(r.voorstelIsZin, 'zonder zin is de vraag het eerste voorstel ("' + r.voorstelKop + '")');
  ok(!r.naZinIsZin, 'het controlegeval: heb je hem geschreven, dan komt er iets anders ("' + r.naZinKop + '")');

  console.log('\n-- 5. het controlegeval: geen groep, geen kaart --');
  ok(r.zonderGroep === '', 'zonder groep staat er geen kaart');
  ok(!r.zonderGroepVoorstel, 'en geen voorstel: geen publiek beloven dat er niet is');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
