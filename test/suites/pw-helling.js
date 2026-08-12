// pw-helling.js (11 aug, v23.44) — het aanmeldscherm vraagt je niveau niet meer.
//
// Stefan, 11 aug: "je krijgt 30 woorden, dan schatten we je niveau in", en daarna "kunnen we er
// niet een geïntegreerde beleving van maken?"
//
// Dertig is geen rond getal. PEIL_MIN_N staat op 20, en daaronder weigert niveauSchatting() iets
// te zeggen. De oude peiling gaf er twaalf, en dus kreeg een vreemde op zijn eerste dag te lezen
// "nog 8 antwoorden en de balk kan je niveau schatten": een meting die niets meet.
//
// Wat deze suite bewaakt is niet het scherm maar de vier beloftes eronder:
//   1. de helling levert genoeg antwoorden dat de schatter mág spreken
//   2. het voorstel dat eruit komt klopt met de schatting
//   3. wat je goed had wordt een voorsprong en geen bewijs (claim, zoals de inhaalslag)
//   4. de oude weg blijft heel, op elk punt waar hij nodig kan zijn
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

/* Wachten op de toestand en niet op de klok. renderProef en helVraagRender tekenen het volgende
   scherm pas na een setTimeout van 850 respectievelijk 700 ms, en een vaste pauze die daar vlak
   onder zit werkt prima op een lege machine en valt om zodra de poort vier suites tegelijk draait.
   Precies dat gebeurde: deze suite was groen als losse run en rood in de poort. Zie ook
   claude/lancering.md, punt 5 over wisselvallige suites: een vaste pauze is een dobbelsteen die
   meestal goed valt. */
async function wachtOpProef(page, wat) {
  await page.waitForFunction(w => {
    if (typeof proefStand === 'undefined' || !proefStand) return false;
    const box = document.getElementById('proefBox');
    if (!box || box.classList.contains('hidden')) return false;
    if (w === 'vraag') {
      return (proefStand.helGekozen === null || proefStand.helGekozen === undefined) &&
             document.querySelectorAll('#proefBox [data-hel]').length > 0;
    }
    return !!document.querySelector('#proefBox ' + w);
  }, wat, { timeout: 20000 });
}

async function driVaste(page) {
  await page.goto(U);
  await page.waitForSelector('#proefBox button[data-proef]', { timeout: 20000 });
  for (let i = 0; i < 3; i++) {
    const nu = await page.evaluate(() => proefStand.i);
    await page.locator('#proefBox button[data-proef]').first().click();
    await page.waitForFunction(v => proefStand.i > v, nu, { timeout: 20000 });
  }
  // Het aanbod (of, als de bak onverwacht niet meetbaar is, het oude bewaarscherm).
  await page.waitForSelector('#btnHelJa, #btnProefDoor', { timeout: 20000 });
}

// De helling doorlopen met een gestuurd aantal goede antwoorden.
async function helling(page, deelGoed) {
  for (let i = 0; i < 27; i++) {
    const klaar = await page.evaluate(() => !proefStand.hel || proefStand.helI >= proefStand.hel.length);
    if (klaar) break;
    await wachtOpProef(page, 'vraag');
    const goed = await page.evaluate(() => {
      const v = proefStand.hel[proefStand.helI];
      return v ? v.goed : null;
    });
    if (goed === null) break;
    const nu = await page.evaluate(() => proefStand.helI);
    const pak = (i * 100 / 27) < deelGoed * 100;
    await page.evaluate(([g, j]) => {
      const bs = Array.prototype.slice.call(document.querySelectorAll('#proefBox [data-hel]'));
      const b = j ? bs.filter(x => x.getAttribute('data-hel') === g)[0]
                  : bs.filter(x => x.getAttribute('data-hel') !== g)[0];
      if (b) b.click();
    }, [goed, pak]);
    await page.waitForFunction(v => proefStand.helI > v, nu, { timeout: 20000 });
  }
  await page.waitForSelector('#btnHelVerder', { timeout: 20000 });
}

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await b.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));

  console.log('\n-- de proef houdt niet meer op na drie --');
  await driVaste(page);
  ok(await page.locator('#btnHelJa').count() === 1, 'na drie woorden staat er een aanbod om door te gaan');
  ok(await page.locator('#lnkHelNee').count() === 1, 'en een uitweg naar het gewone aanmeldscherm');

  console.log('\n-- de bak is vóór het aanmelden groot genoeg om A1 te meten --');
  const bank = await page.evaluate(() => ({
    woorden: WORDS.length,
    meetbaar: peilMeetbaar('A1'),
    kandidaten: peilKandidaten('A1').length,
    vragen: proefStand.hel ? proefStand.hel.length : 0
  }));
  console.log('  bank ::', JSON.stringify(bank));
  ok(bank.meetbaar === true, 'A1 is meetbaar vóór het eerste profiel (was: geen enkel niveau)');
  ok(bank.vragen === 27, 'er staan 27 vragen klaar, samen met de drie vaste maakt dat 30');

  console.log('\n-- vóór het aanmelden wordt er niet in andermans profiel geschreven --');
  // store.key staat tot boot() op de standaardsleutel. Een persist() hier schrijft dus in het
  // profiel van wie deze browser al gebruikte. De helling bewaart in zijn eigen blob.
  const voorKey = await page.evaluate(() => {
    try { return localStorage.getItem('espanol-stefan-v1'); } catch (e) { return null; }
  });
  await page.locator('#btnHelJa').click();
  await helling(page, 0.55);
  const naKey = await page.evaluate(() => {
    try { return localStorage.getItem('espanol-stefan-v1'); } catch (e) { return null; }
  });
  ok(voorKey === naKey, 'de helling raakt de opslagsleutel van een ander profiel niet aan');

  console.log('\n-- de uitslag --');
  const uit = await page.evaluate(() => ({
    tekst: document.getElementById('proefBox').innerText,
    items: Object.keys(proefStand.items || {}).length,
    voorstel: proefStand.voorstel,
    schatting: (function () { try { return niveauSchatting('A1'); } catch (e) { return null; } })()
  }));
  console.log('  items ::', uit.items, '· voorstel ::', JSON.stringify(uit.voorstel));
  ok(uit.items >= 20, 'er liggen minstens PEIL_MIN_N (20) gemeten sleutels, dus de schatter mag spreken');
  ok(uit.items === 28,
    'achtentwintig unieke sleutels: 27 uit de bak plus gracias. Stond die er 27, dan is gracias ' +
    'twee keer gevraagd en trekt de helling uit een vijver waar hij zelf al in zat');
  ok(uit.schatting !== null, 'niveauSchatting() geeft een uitkomst in plaats van null');
  ok(/Je herkende \d+ van de 30 woorden/.test(uit.tekst),
    'de uitslag telt alle dertig antwoorden, ook de twee vaste zonder Cervantes-sleutel');
  // v23.50: hier stond /Je begint op A[012]\./. Die tekst is weg omdat A0 en A1 dezelfde track
  // opleveren en de uitslag geen onderscheid hoort te beloven dat de app niet maakt. Wat blijft is
  // de eis eronder: er staat een uitkomst, geen vraag.
  ok(/Je begint/.test(uit.tekst) && !/\?/.test(uit.tekst.split('Je begint')[1] || ''),
    'er staat een uitkomst en geen vraag');
  // Dit is het punt waar ik de eerste versie fout had: hier stond een puntschatting ("ongeveer 195
  // van de 409"), en na het aanmelden rekent dezelfde schatter over een kleinere bak en zegt 182.
  // Twee getallen voor dezelfde vraag, twee schermen na elkaar. Zie claude/rapport.md maatstaf 1.
  ok(!/van de 409/.test(uit.tekst) && !/ergens tussen/.test(uit.tekst),
    'de uitslag noemt geen absolute A1-schatting, want die verandert na het aanmelden van bak');

  console.log('\n-- het voorstel volgt de schatting --');
  const grens = await page.evaluate(() => {
    const mk = p => ({ niv: 'A1', noem: 409, punt: Math.round(p * 409), onder: 0, boven: 409, n: 30 });
    return {
      hoog: helVoorstel(mk(0.95)),
      midden: helVoorstel(mk(0.5)),
      laag: helVoorstel(mk(0.05)),
      leeg: helVoorstel(null),
      poort: POORT_PCT
    };
  });
  console.log('  grenzen ::', JSON.stringify(grens));
  ok(grens.hoog.lvl === 'A2' && grens.hoog.track === 'a2', 'boven POORT_PCT is het voorstel A2');
  ok(grens.midden.lvl === 'A1' && grens.midden.track === 'beginner', 'in het midden A1');
  ok(grens.laag.lvl === 'A0' && grens.laag.track === 'beginner', 'onderaan A0');
  ok(grens.leeg.zeker === false, 'zonder schatting is er geen zeker voorstel');

  console.log('\n-- het aanmeldscherm staat op het voorstel --');
  await page.locator('#btnHelVerder').click();
  await page.waitForSelector('#helRegel:not(.hidden)', { timeout: 20000 });
  const kaart = await page.evaluate(() => ({
    regel: (document.getElementById('helRegel') || {}).textContent || '',
    zichtbaar: !!(document.getElementById('helRegel') &&
                  !document.getElementById('helRegel').classList.contains('hidden')),
    track: newTrack,
    actief: Array.prototype.map.call(document.querySelectorAll('.trackpick[data-lvl].active'),
                                     x => x.getAttribute('data-lvl')),
    knoppenErNog: document.querySelectorAll('.trackpick[data-lvl]').length,
    b1Uit: !!document.querySelector('#profCard button[disabled]'),
    testErNog: !!document.getElementById('btnPlacement') ||
               /niveautest/i.test(document.getElementById('profCard').innerText)
  }));
  console.log('  kaart ::', JSON.stringify(kaart));
  ok(kaart.zichtbaar && /A[012]/.test(kaart.regel), 'er staat een regel met het voorgestelde niveau');
  ok(kaart.track === 'beginner' || kaart.track === 'a2', 'newTrack is alvast gezet');
  ok(kaart.actief.length === 1, 'precies één niveauknop staat aan');
  ok(kaart.knoppenErNog === 3 && kaart.b1Uit && kaart.testErNog,
    'de drie kiesbare niveaus, het grijze B1 en de niveautest staan er nog: dit is een voorstel, ' +
    'geen uitspraak');

  console.log('\n-- de grammaticatest concurreert niet meer met het voorstel (v23.47) --');
  const test = await page.evaluate(() => ({
    hint: (document.getElementById('profHint') || {}).textContent || '',
    knop: (document.getElementById('btnPlacement') || {}).textContent || '',
    erNog: !!document.getElementById('btnPlacement')
  }));
  console.log('  test ::', JSON.stringify(test));
  ok(test.hint === '',
    '"Kies een niveau, of doe de test van 10 vragen" staat er niet meer: de app vraagt niets meer');
  ok(test.erNog && /grammatica/i.test(test.knop) && !/niveau/i.test(test.knop),
    'de knop blijft als uitweg staan maar heet wat hij is: een grammaticatest, geen niveautest');

  console.log('\n-- een niveauknop laat je dagdoel met rust --');
  const doel = await page.evaluate(() => {
    document.getElementById('lnkMeerOpties').click();
    const voor = document.querySelectorAll('.doelpick.active').length;
    document.querySelector('.trackpick[data-lvl="A2"]').click();
    return { voor: voor, na: document.querySelectorAll('.doelpick.active').length, min: newMinuten };
  });
  console.log('  doel ::', JSON.stringify(doel));
  ok(doel.voor === 1 && doel.na === 1,
    'na een tik op een niveau staat je gekozen aantal minuten nog steeds aan');

  console.log('\n-- verzilveren bij het aanmelden --');
  await page.evaluate(() => { document.querySelector('.trackpick[data-lvl="A1"]').click(); });
  await page.fill('#newProfName', 'Helling' + Date.now());
  await page.click('#btnNewProf');
  await page.waitForFunction(() => !!(typeof activeProfile === 'function' && activeProfile()),
                             null, { timeout: 20000 });
  await page.waitForTimeout(600);
  const na = await page.evaluate(() => {
    const goedeIds = {}, fouteIds = {};
    // proefStand is weg na het aanmelden; we lezen terug wat er in S staat.
    const claims = Object.keys(S.srs).filter(k => S.srs[k].claim);
    return {
      peilItems: Object.keys((S.peil || {}).items || {}).length,
      srs: Object.keys(S.srs).length,
      claims: claims.length,
      claimDoos: claims.length ? S.srs[claims[0]].box : null,
      sweepKen: (S.sweep || {}).ken || 0,
      schatting: (function () { try { return !!niveauSchatting('A1'); } catch (e) { return false; } })(),
      keysCache: Object.keys(pcicKeysApp().A1 || {}).length,
      woorden: WORDS.length
    };
  });
  console.log('  na ::', JSON.stringify(na));
  ok(na.peilItems >= 20, 'de meting staat in S.peil.items, dus de voortgangspagina hoeft niet te zwijgen');
  ok(na.schatting === true, 'en niveauSchatting() spreekt meteen, zonder tweede peiling');
  ok(na.claims > 0 && na.claimDoos === 3,
    'wat je goed had staat met claim in doosje SWEEP_BOX: een voorsprong, geen bewijs');
  ok(na.sweepKen === na.claims, 'S.sweep telt ze, zodat later blijkt hoe vaak je "die ken ik" klopte');
  ok(na.srs === na.claims + 3,
    'alleen de goede antwoorden en de drie proefwoorden staan in S.srs; de foute niet ' +
    '(die zouden meetellen als geoefend terwijl je ze alleen zag)');
  // De cache van pcicKeysApp() hoort bij de bak van dit profiel en niet bij de ruime bak die de
  // helling laadde. Zonder de reset in boot() bleef hij de hele sessie op 405 staan.
  ok(na.keysCache < 405 && na.keysCache > 300,
    'pcicKeysApp() is opnieuw opgebouwd voor de bak van dit profiel (' + na.keysCache + ' A1-sleutels)');

  console.log('\n-- de afleiders zijn van dezelfde woordsoort (v23.50) --');
  const afl = await page.evaluate(() => {
    // Stefan zag "el jardín" met "de badkamer", "hoeveel kost het?" en "blauw" ernaast: een kamer,
    // een vraag en een kleur. Dan hoef je het woord niet te kennen om het eruit te pikken.
    const kand = geschud(peilKandidaten('A1')).slice(0, 150);
    let n = 0, alleen = 0, soorten = 0;
    const vb = [];
    kand.forEach(k => {
      const w = peilWoordVoor(pcicKeysApp().A1[k]);
      if (!w) return;
      const opts = peilOpties(w);
      if (opts.length < 4) return;
      const bij = opts.map(o => WORDS.filter(x => wTrans(x) === o)[0]).filter(Boolean);
      if (bij.length < 4) return;
      n++;
      const s = bij.map(woordSoort);
      const mijn = woordSoort(w);
      if (s.filter(x => x === mijn).length === 1) {
        alleen++;
        if (vb.length < 3) vb.push(w.es + ' [' + mijn + '] :: ' + opts.join(' · '));
      }
      if (new Set(s).size > 2) soorten++;
    });
    return { n: n, alleen: alleen, soorten: soorten, vb: vb };
  });
  console.log('  vragen ::', afl.n, '· alleen van zijn soort ::', afl.alleen, '· meer dan twee soorten ::', afl.soorten);
  afl.vb.forEach(v => console.log('    ✗ ' + v));
  ok(afl.n > 50, 'er zijn genoeg vragen bekeken om iets te kunnen zeggen (' + afl.n + ')');
  ok(afl.alleen === 0,
    'geen enkele vraag waar het goede antwoord het enige van zijn woordsoort is (was: 30 van de 200)');
  ok(afl.soorten === 0, 'en nergens meer dan twee woordsoorten door elkaar');

  console.log('\n-- de uitslag belooft geen verschil dat er niet is (v23.50) --');
  const paden = await page.evaluate(() => ({
    knoppen: Array.prototype.map.call(document.querySelectorAll('.trackpick[data-lvl]'),
      b => b.getAttribute('data-lvl') + '=' + b.getAttribute('data-track')),
    tracks: Object.keys(TRACKS)
  }));
  console.log('  knoppen ::', paden.knoppen.join(' · '), '· tracks ::', paden.tracks.join(', '));
  // A0 en A1 wijzen allebei naar dezelfde track. Zolang dat zo is mag de uitslag niet doen alsof
  // het uitmaakt. Gaan ze ooit echt uit elkaar, dan valt deze test om en hoort de tekst terug.
  const zelfdePad = paden.knoppen.indexOf('A0=beginner') !== -1 && paden.knoppen.indexOf('A1=beginner') !== -1;
  const tekstA1 = await page.evaluate(() => helTxt().start('A1'));
  const tekstA2 = await page.evaluate(() => helTxt().start('A2'));
  ok(!zelfdePad || !/A1/.test(tekstA1),
    'zolang A0 en A1 dezelfde track opleveren, noemt de uitslag dat verschil niet ("' + tekstA1 + '")');
  ok(/A2/.test(tekstA2), 'A2 is wél een ander pad en wordt dus wel genoemd ("' + tekstA2 + '")');

  console.log('\n-- de meting is een meting (v23.46) --');
  const punten = await page.evaluate(() => ({
    vandaag: (S.xp || {})[today()] || 0,
    txp: S.txp || 0,
    doel: S.doel,
    balk: (document.getElementById('goalLine') || {}).innerText || '',
    gehaald: ((S.xp || {})[today()] || 0) >= S.doel
  }));
  console.log('  punten ::', JSON.stringify(punten));
  ok(punten.vandaag > 0 && punten.vandaag <= 6,
    'alleen de drie vaste proefwoorden gaven taco\'s (' + punten.vandaag + '), de dertig niet');
  ok(!punten.gehaald,
    'je dagdoel is niet gehaald voordat je je eerste les hebt gedaan (was: 50 van 30)');
  ok(!/gehaald/.test(punten.balk),
    'en de kopbalk zegt dus niet "doel gehaald" boven een knop die zegt "start je les"');

  console.log('\n-- de oude weg blijft heel --');
  const oud = await b.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  const errs2 = []; oud.on('pageerror', e => errs2.push(e.message));
  await driVaste(oud);
  await oud.locator('#lnkHelNee').click();
  await oud.waitForSelector('#btnProefDoor', { timeout: 20000 });
  const weg = await oud.evaluate(() => ({
    knop: !!document.getElementById('btnProefDoor'),
    tekst: document.getElementById('proefBox').innerText
  }));
  ok(weg.knop && /Bewaar mijn woorden/.test(weg.tekst),
    '"nee, maak gewoon een profiel" komt uit op precies het scherm van vóór v23.44');
  await oud.locator('#btnProefDoor').click();
  await oud.waitForSelector('#profCard:not(.hidden)', { timeout: 20000 });
  const kaart2 = await oud.evaluate(() => ({
    zichtbaar: !document.getElementById('profCard').classList.contains('hidden'),
    regel: document.getElementById('helRegel').classList.contains('hidden'),
    track: newTrack
  }));
  ok(kaart2.zichtbaar && kaart2.regel && kaart2.track === null,
    'dan staat er geen voorstel en kies je gewoon zelf');
  await oud.close();

  console.log('\n-- schone console --');
  ok(errs.length === 0 && errs2.length === 0,
    'geen javascript-fouten onderweg' + ((errs.concat(errs2)).length ? ' :: ' + errs.concat(errs2).join(' | ') : ''));

  await b.close();
  console.log(fout === 0 ? '\nPOORT OPEN' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
