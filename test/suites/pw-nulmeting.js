// pw-nulmeting.js (22 aug, v23.174) — meet de weekmeting, en stuurt hij niets?
//
// WAAROM DIT ER IS
//
// Stefan, 22 aug: "nou beide, nulmeting en dan de nachtrun."
//
// De leerkaart van de zinstap zet twee getallen op 5 september, en het tweede is "het aandeel
// tijdfouten in de wekelijkse schrijftaak daalt". Die schrijftaak bestond niet. Dit is hem.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE TAAK DWINGT VERLEDEN TIJD AF EN IS VOORSPELBAAR. Zes opdrachten, gekozen op weeknummer,
//      dus dezelfde week geeft altijd dezelfde opdracht en week 1 is met week 7 te vergelijken.
//   2. DE METING BEWAART EEN IDENTITEIT. Niet "drie fouten" maar per fout: grondwoord, categorie,
//      wat er stond, wat er had moeten staan. Plus de tekst zelf en het nummer van de prompt,
//      zodat een latere prompt oude weken opnieuw kan beoordelen.
//   3. HET CONTROLEGEVAL: DE METING STUURT NIETS. Geen foutenlogboek, geen doosje, geen wachtrij,
//      geen dagStats. Dat laatste is niet netheid: de weekmeting rekent haar eigen foutpercentage
//      uit dagStats, dus een schrijftaak die daarin landt vervuilt de reeks die hij moet meten.
//      Dit punt is met één regel groen te krijgen door de meting helemaal niets te laten doen, en
//      daarom staat er in punt 2 ook wat hij WEL moet opslaan.
//   4. EEN SYNC MAG DE METING NIET WISSEN. mengMeting() verving de hele weekregel zodra de andere
//      kant een hogere woordenstand had. De schrijftaak staat op één apparaat, dus dat wiste hem.
//   5. DE REEKS VERSCHIJNT PAS BIJ DRIE METINGEN, dezelfde regel als bij de band en de voorspeller.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwNm' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';

    // ---- 1. de taak ----
    uit.aantalTaken = MEET_TAKEN.length;
    uit.zelfdeWeek = meetTaakVanWeek('2026-W34').id === meetTaakVanWeek('2026-W34').id;
    uit.rondloopt = meetTaakVanWeek('2026-W01').id === meetTaakVanWeek('2026-W07').id;
    uit.verschilt = meetTaakVanWeek('2026-W01').id !== meetTaakVanWeek('2026-W02').id;
    uit.taakNu = meetTaakVanWeek().id;

    // ---- 2 en 3. bewaren en niets sturen ----
    S.meting = {}; S.errors = {}; S.gram = {}; S.dagStats = {}; S.srs = S.srs || {};
    const xpVoor = S.txp || 0;
    uit.openVoor = meetOpen();
    const taak = meetTaakVanWeek();
    const tekst = 'Ayer me levante temprano y desayune con mi mujer. Despues fuimos al mercado ' +
                  'y compramos pan y fruta. Por la tarde yo estaba muy cansado, asi que dormi un poco.';
    const nep = { fouten: [
      { lemma: 'levantarse', cat: 'spelling',  gegeven: 'levante',  doel: 'levanté' },
      { lemma: 'estar',      cat: 'serestar',  gegeven: 'estaba',   doel: 'era' },
      { lemma: 'dormir',     cat: 'tijd',      gegeven: 'dormi',    doel: 'dormía' },
      { lemma: 'comprar',    cat: 'ditbestaatniet', gegeven: 'compramos', doel: 'compramos' }
    ] };
    meetBewaar(tekst, taak, nep);
    const s = S.meting[meetWeek()].schrijf;
    uit.opgeslagen = { taak: s.taak, n: s.n, z: s.z, pv: s.pv, ok: s.ok,
                       heeftTekst: (s.tekst || '').length > 20, fouten: s.f.length };
    uit.eersteFout = s.f[0];
    uit.per = s.per;
    uit.onbekendeCat = s.f[3] ? s.f[3].c : null;
    uit.tijdPer100 = meetTijdPer100(s);
    uit.openNa = meetOpen();

    // het controlegeval
    uit.geenErrors = Object.keys(S.errors).length === 0;
    uit.geenGram = Object.keys(S.gram).length === 0;
    uit.geenDagStats = !(S.dagStats[today()] && S.dagStats[today()].pogingen);
    uit.xpErbij = (S.txp || 0) - xpVoor;

    // ---- 4. een sync mag hem niet wissen ----
    const w = meetWeek();
    S.meting[w].stevig = 10;
    const anderApparaat = {}; anderApparaat[w] = { d: today(), stevig: 99 };   // hoger, zonder schrijftaak
    mengMeting(anderApparaat);
    uit.naSync = !!(S.meting[w] && S.meting[w].schrijf);
    uit.naSyncStevig = S.meting[w].stevig;
    // en andersom: hij komt binnen van een ander apparaat en wij hebben hem niet
    S.meting['2026-W01'] = { d: '2026-01-05', stevig: 50 };
    const binnen = { '2026-W01': { d: '2026-01-05', stevig: 1, schrijf: { n: 60, per: { tijd: 2 }, f: [] } } };
    mengMeting(binnen);
    uit.binnengekomen = !!(S.meting['2026-W01'] && S.meting['2026-W01'].schrijf);

    // ---- 5. de reeks pas bij drie ----
    S.meting = {};
    S.meting['2026-W20'] = { d: '2026-05-11', schrijf: { n: 100, per: { tijd: 5 }, f: [] } };
    S.meting['2026-W21'] = { d: '2026-05-18', schrijf: { n: 100, per: { tijd: 3 }, f: [] } };
    uit.bijTwee = vgMetingHtml().length;
    S.meting['2026-W22'] = { d: '2026-05-25', schrijf: { n: 200, per: { tijd: 2 }, f: [] } };
    const html = vgMetingHtml();
    uit.bijDrie = html.length;
    uit.toontGetal = html.indexOf('>2.5<') !== -1 || html.indexOf('>1<') !== -1;
    uit.reeks = meetReeks().map(function (x) { return meetTijdPer100(x.s); });
    return uit;
  });

  console.log('\n-- 1. de taak dwingt verleden tijd af en is voorspelbaar --');
  console.log('   deze week: ' + r.taakNu + ' · ' + r.aantalTaken + ' opdrachten');
  ok(r.aantalTaken === 6, 'zes opdrachten (' + r.aantalTaken + ')');
  ok(r.zelfdeWeek, 'dezelfde week geeft dezelfde opdracht');
  ok(r.rondloopt, 'en na zes weken komt hij terug, zodat twee weken vergelijkbaar zijn');
  ok(r.verschilt, 'terwijl twee opvolgende weken verschillen');

  console.log('\n-- 2. de meting bewaart een identiteit --');
  console.log('   ' + JSON.stringify(r.opgeslagen));
  console.log('   eerste fout: ' + JSON.stringify(r.eersteFout));
  ok(r.openVoor === true && r.openNa === false, 'de week stond open en staat na het inleveren dicht');
  ok(r.opgeslagen.n === 30, 'de woorden zijn geteld (' + r.opgeslagen.n + ')');
  ok(r.opgeslagen.z === 3, 'en de zinnen (' + r.opgeslagen.z + ')');
  ok(r.opgeslagen.heeftTekst, 'de tekst zelf staat erbij, zodat een latere prompt hem opnieuw kan beoordelen');
  ok(r.opgeslagen.pv === 1, 'met het nummer van de prompt waarmee hij beoordeeld is (' + r.opgeslagen.pv + ')');
  ok(!!r.eersteFout && r.eersteFout.l === 'levantarse' && r.eersteFout.c === 'spelling' &&
     r.eersteFout.g === 'levante' && r.eersteFout.d === 'levanté',
    'en per fout een identiteit: grondwoord, categorie, wat er stond, wat er hoorde');
  ok(r.onbekendeCat === 'overig', 'een categorie die niet bestaat wordt overig en geen nieuwe kolom (' + r.onbekendeCat + ')');
  ok(r.tijdPer100 === 3.3, 'tijdfouten per honderd woorden: 1 op 30 is ' + r.tijdPer100);

  console.log('\n-- 3. het controlegeval: de meting stuurt niets --');
  ok(r.geenErrors, 'niets in het foutenlogboek, dus de wachtrij verandert niet');
  ok(r.geenGram, 'geen doosje aangeraakt');
  ok(r.geenDagStats, 'en niets in dagStats, want daaruit rekent de weekmeting haar eigen foutpercentage');
  ok(r.xpErbij === 15, 'XP wel, en vast: voor het inleveren en niet voor hoe goed het was (' + r.xpErbij + ')');

  console.log('\n-- 4. een sync mag de meting niet wissen --');
  ok(r.naSync === true, 'een pull met een hogere woordenstand laat de schrijftaak staan');
  ok(r.naSyncStevig === 99, 'terwijl de tellers wel gewoon meegaan (' + r.naSyncStevig + ')');
  ok(r.binnengekomen === true, 'en andersom komt een schrijftaak van een ander apparaat binnen');

  console.log('\n-- 5. de reeks verschijnt pas bij drie metingen --');
  console.log('   reeks: ' + r.reeks.join(', '));
  ok(r.bijTwee === 0, 'bij twee metingen staat er niets');
  ok(r.bijDrie > 0, 'bij drie wel');
  ok(r.toontGetal, 'en het getal dat ertoe doet staat erin');

  /* 6. DE VOORDEUR. Alles hierboven roept de functies rechtstreeks aan, en een controle die de
     voordeur overslaat bewijst niets over de voordeur. Hier wordt het scherm echt geopend, echt
     getypt en echt op de knop geklikt. De server is er niet in deze test, en dat is meegenomen:
     dan moet de meting alsnog bewaard worden met ok:false, want een kapotte verbinding mag geen
     stilzwijgend gat in de reeks maken. */
  await page.evaluate(() => { S.meting = {}; delete S.meetConcept; lesFlow = null; show('meting'); });
  await page.waitForTimeout(300);
  const knopVoor = await page.evaluate(() => {
    const b = document.getElementById('btnMeetKlaar');
    return { erIs: !!document.getElementById('meetInp'), uit: !!(b && b.disabled) };
  });
  ok(knopVoor.erIs, 'het scherm heeft een invoerveld');
  ok(knopVoor.uit === true, 'en de knop staat uit zolang er te weinig staat');

  await page.fill('#meetInp', 'Ayer me levante temprano y desayune con mi mujer. Despues fuimos al mercado ' +
    'y compramos pan y fruta. Por la tarde yo estaba muy cansado, asi que dormi un poco en el sofa. ' +
    'Cuando me desperte, mi hija ya habia llegado de la escuela y jugamos juntos en el jardin hasta la cena.');
  await page.waitForTimeout(200);
  const knopNa = await page.evaluate(() => !document.getElementById('btnMeetKlaar').disabled);
  ok(knopNa === true, 'bij genoeg woorden gaat hij aan');

  await page.click('#btnMeetKlaar');
  await page.waitForTimeout(1200);
  const na = await page.evaluate(() => {
    const s = (S.meting[meetWeek()] || {}).schrijf;
    return { er: !!s, ok: s ? s.ok : null, n: s ? s.n : 0, concept: !!S.meetConcept,
             scherm: (document.getElementById('metingWrap').textContent || '').slice(0, 60),
             open: meetOpen() };
  });
  console.log('\n-- 6. de voordeur --');
  console.log('   ' + JSON.stringify(na));
  ok(na.er === true, 'na klikken staat de meting er');
  ok(na.ok === false, 'met ok:false, want de server was er niet, en dat is beter dan een gat in de reeks');
  ok(na.n > 30, 'en de woorden zijn geteld (' + na.n + ')');
  ok(na.concept === false, 'het concept is opgeruimd');
  ok(na.open === false, 'de week staat dicht');
  ok(/Opgeslagen/.test(na.scherm), 'en op het scherm staat geen correctie ("' + na.scherm + '")');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
