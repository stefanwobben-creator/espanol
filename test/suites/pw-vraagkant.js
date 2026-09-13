// pw-vraagkant.js (13 sep, v23.254) - draagt de vraagkant van een woordkaartje nog het antwoord?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 13 september: "nog te vaak bij woordjes zie ik al een hint." Twee schermafbeeldingen
// erbij, en allebei de kaartjes staan letterlijk zo in FREQ:
//
//     encima  ::  bovenop; encima de = boven op
//     sale    ::  hij/zij gaat weg/uit (van salir)
//
// Geteld in FREQ (4219 rijen): 856 noemen de infinitief tussen haakjes, 239 zetten een Spaanse
// uitdrukking achter een isgelijkteken, 330 herhalen het Spaanse woord zelf.
//
// Geen van die rijen is FOUT. Ze zijn geschreven om NAAST het Spaanse woord te staan, als tooltip
// terwijl je leest. Maar wie zo'n woord aantikt zet hem in zijn stapel (v23.133), en dan is de
// tooltip de vraag geworden.
//
//     Een tekst die geschreven is om naast het antwoord te staan, is geen vraag.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DE WEGGEVER GAAT ERAF, en gaat niet weg: hij komt terug op de achterkant, waar hij hoort.
//   2. DE UITLEG BLIJFT STAAN. "lang (van lengte)" bij alto is geen hint. Dit is de controle die
//      het verschil maakt tussen meten en gokken, en hij wordt hier op de ECHTE gegevens gedraaid:
//      van alle 895 haakjes met "(van X)" horen er precies tien te blijven staan, en alle tien
//      zijn Nederlands.
//   3. EEN LEGE VRAAG BESTAAT NIET. Bij "mamá :: mama" is de betekenis het antwoord. Dan blijft de
//      hele betekenis staan: een lege vraag is erger dan een hint.
//   4. DE LAATSTE STAP IS SCHOON. renderWordCheck() is de enige stap die je niet kunt bluffen, en
//      juist daar stond wTrans(w) onbewerkt op het scherm.
//   5. DE ZIN KOMT MEE EN HET GAT KLOPT. Een zin op de vraagkant mag het antwoord niet bevatten, en
//      als het gat niet gemaakt kan worden komt de zin daar niet. Nagemeten, niet aangenomen.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  // Een echt profiel, want show('woorden') bouwt de wachtrij en die leest S.lessons. Een
  // handgemaakte S is geen goedkopere versie daarvan maar een andere app.
  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Test' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
  await page.evaluate(() => show('woorden'));
  await page.waitForTimeout(400);

  // ---------- 1. de weggever gaat eraf en komt achterop terug ----------
  console.log('\n1. wat het antwoord verraadt gaat van de vraagkant af');
  const splits = await page.evaluate(() => {
    const proef = [
      ['encontrado', 'gevonden (van encontrar)'],
      ['sale', 'hij/zij gaat weg/uit (van salir)'],
      ['encima', 'bovenop; encima de = boven op'],
      ['siento', 'ik voel; lo siento = sorry'],
      ['irá', 'hij/zij zal gaan (van ir)'],
      ['es', 'is (van ser)'],
      ['digas', 'no digas = zeg niet (van decir)']
    ];
    return proef.map(([es, nl]) => Object.assign({ es, nl }, kaartSplits(nl, es)));
  });
  const perEs = {};
  splits.forEach((x) => { perEs[x.es] = x; });
  ok(perEs.encontrado.vraag === 'gevonden', 'encontrado: "gevonden (van encontrar)" -> "' + perEs.encontrado.vraag + '"');
  ok(perEs.encontrado.rest.indexOf('encontrar') !== -1, 'en "(van encontrar)" staat op de achterkant');
  ok(perEs.sale.vraag === 'hij/zij gaat weg/uit', 'sale: het werkwoord is eraf ("' + perEs.sale.vraag + '")');
  ok(perEs.encima.vraag === 'bovenop', 'encima: de uitdrukking met het antwoord erin is eraf ("' + perEs.encima.vraag + '")');
  ok(perEs.siento.vraag === 'ik voel', 'siento: "lo siento = sorry" is eraf ("' + perEs.siento.vraag + '")');
  ok(perEs['irá'].vraag === 'hij/zij zal gaan', 'irá: ook een werkwoord van twee letters ("' + perEs['irá'].vraag + '")');
  ok(perEs.es.vraag === 'is', 'es: en een dat geen letter met de vorm deelt ("' + perEs.es.vraag + '")');
  ok(perEs.digas.vraag === 'zeg niet',
     'digas: "no digas = zeg niet (van decir)" -> "' + perEs.digas.vraag + '" (de Nederlandse kant van het isgelijkteken)');
  ok(perEs.digas.vraag.indexOf('decir') === -1,
     'CONTROLE: en het haakje komt niet via die achterdeur terug ("' + perEs.digas.vraag + '")');

  // ---------- 2. de uitleg blijft staan, op de echte gegevens ----------
  console.log('\n2. een Nederlandse toelichting is geen hint en blijft staan');
  const haakjes = await page.evaluate(() => {
    const woorden = [].concat(TRACKS.a2.words, TRACKS.beginner.words, B_WORDS, K_WORDS, C_WORDS).map((w) => [w.es, w.nl]);
    const alle = woorden.concat(FREQ);
    let n = 0; const blijft = {};
    alle.forEach(([es, nl]) => {
      const m = String(nl || '').match(/\((?:van|from)\s+([^)]+)\)/i);
      if (!m) return;
      n++;
      if (kaartSplits(nl, es).vraag.indexOf(m[0]) !== -1) blijft[m[1]] = (blijft[m[1]] || 0) + 1;
    });
    return { n, blijft: Object.keys(blijft) };
  });
  ok(haakjes.n > 800, 'er staan ' + haakjes.n + ' haakjes met "(van X)" in de gegevens');
  const nederlands = ['lengte', 'iemand', 'vloeistof', 'een straat', 'mist, vloeistof', 'een gerecht',
                      'een wolf', 'afstand/duur', 'de straat', 'een deur'];
  ok(haakjes.blijft.length <= 12, 'daarvan blijven er ' + haakjes.blijft.length + ' staan (was: allemaal)');
  const vreemd = haakjes.blijft.filter((x) => nederlands.indexOf(x) === -1);
  ok(vreemd.length === 0, 'en die zijn allemaal Nederlandse toelichting' + (vreemd.length ? ' — maar dit niet: ' + vreemd.join(', ') : ''));
  nederlands.forEach((x) => {
    if (x === 'lengte') ok(haakjes.blijft.indexOf(x) !== -1, 'CONTROLE: "(van ' + x + ')" blijft staan');
  });

  // ---------- 3. een lege vraag bestaat niet ----------
  console.log('\n3. blijft er niets over, dan blijft alles staan');
  const leeg = await page.evaluate(() => ['mamá|mama', 'oh|oh', 'auto|auto (Lat-Am)'].map((x) => {
    const [es, nl] = x.split('|');
    return { es, nl, vraag: kaartSplits(nl, es).vraag };
  }));
  leeg.forEach((x) => ok(x.vraag === x.nl, x.es + ': de betekenis IS het antwoord, dus blijft hij heel ("' + x.vraag + '")'));
  const legeVragen = await page.evaluate(() => {
    const woorden = [].concat(TRACKS.a2.words, TRACKS.beginner.words, B_WORDS, K_WORDS, C_WORDS).map((w) => [w.es, w.nl]);
    return woorden.concat(FREQ).filter(([es, nl]) => !String(kaartSplits(nl, es).vraag || '').trim()).length;
  });
  ok(legeVragen === 0, 'en over alle gegevens samen levert dit ' + legeVragen + ' lege vragen op');

  // ---------- 4. de drie schermen ----------
  console.log('\n4. de vraag op het scherm, ook op de stap die je niet kunt bluffen');
  const schermen = await page.evaluate(() => {
    const w = { id: 'proef-lek', es: 'encontrado', nl: 'gevonden (van encontrar)', tag: 'proef' };
    WORDS.push(w);
    S.dir = 'nl-es';
    wQueue = [w]; wCur = w; wShown = false; wCheck = null;
    wRondeZet(wQueue);
    delete S.srs[w.id];
    renderWord();
    const voor = document.getElementById('wCard').innerText;
    showWord();
    const achter = document.getElementById('wCard').innerText;
    // en de Laatste stap
    S.srs[w.id] = { box: zelfDrempel(), due: today(), n: 9 };
    wCheck = null;
    renderWordCheck();
    const laatste = document.getElementById('wCard').innerText;
    return { voor, achter, laatste };
  });
  ok(schermen.voor.indexOf('gevonden') !== -1, 'de voorkant vraagt naar "gevonden"');
  ok(schermen.voor.indexOf('encontrar') === -1, 'en noemt encontrar niet' + (schermen.voor.indexOf('encontrar') !== -1 ? ' — maar het staat er: ' + schermen.voor.replace(/\n/g, ' | ') : ''));
  ok(schermen.achter.indexOf('encontrado') !== -1, 'de achterkant geeft het antwoord');
  ok(schermen.achter.indexOf('encontrar') !== -1, 'en zet de weggenomen toelichting er alsnog bij');
  ok(schermen.laatste.indexOf('gevonden') !== -1, 'de Laatste stap vraagt naar "gevonden"');
  ok(schermen.laatste.indexOf('encontrar') === -1,
     'en noemt encontrar niet, want dit is de enige stap die je niet kunt bluffen' +
     (schermen.laatste.indexOf('encontrar') !== -1 ? ' — maar het staat er: ' + schermen.laatste.replace(/\n/g, ' | ') : ''));

  // ---------- 5. de zin, met een gat dat wordt nagemeten ----------
  console.log('\n5. de zin waarin je het woord vond, met het antwoord eruit');
  const zin = await page.evaluate(() => ({
    lukt: kaartZinGat('Siempre sale de casa a las ocho.', 'sale'),
    lukt2: kaartZinGat('El libro está encima de la mesa.', 'encima'),
    anderevorm: kaartZinGat('Don Quijote salió de la venta.', 'sale'),
    leeg: kaartZinGat('', 'sale')
  }));
  ok(zin.lukt === 'Siempre ___ de casa a las ocho.', 'het gat staat waar het woord stond ("' + zin.lukt + '")');
  ok(zin.lukt2.indexOf('encima') === -1, 'en het antwoord staat er echt niet meer in ("' + zin.lukt2 + '")');
  ok(zin.anderevorm === '',
     'CONTROLE: staat het woord er in een andere vorm, dan komt de zin NIET op de vraagkant ("' + zin.anderevorm + '")');
  ok(zin.leeg === '', 'CONTROLE: geen zin is geen zin');

  const opScherm = await page.evaluate(() => {
    const w = { id: 'proef-zin', es: 'encima', nl: 'bovenop; encima de = boven op', tag: 'proef',
                ej: 'El libro está encima de la mesa.' };
    WORDS.push(w);
    S.dir = 'nl-es';
    delete S.srs[w.id];
    wQueue = [w]; wCur = w; wShown = false; wCheck = null; wRondeZet(wQueue);
    renderWord();
    const voor = document.getElementById('wCard').innerText;
    showWord();
    return { voor, achter: document.getElementById('wCard').innerText };
  });
  ok(opScherm.voor.indexOf('___') !== -1, 'de zin staat met een gat op de vraagkant');
  ok(opScherm.voor.indexOf('encima') === -1,
     'en nergens op die kant staat het antwoord' + (opScherm.voor.indexOf('encima') !== -1 ? ' — maar: ' + opScherm.voor.replace(/\n/g, ' | ') : ''));
  ok(opScherm.achter.indexOf('El libro está encima de la mesa.') !== -1, 'op de achterkant staat de zin heel');

  // ---------- 6. en de zin komt ook echt uit het lezen mee ----------
  console.log('\n6. een woord dat je in een hoofdstuk aantikt, neemt zijn zin mee');
  const uitLezen = await page.evaluate(() => {
    leesWoorden = []; leesZinnen = [];
    const html = leesTekstHtml('El gato duerme. La casa es grande y blanca.');
    const woordN = leesWoorden.length;
    // de splitsing moet sluitend zijn: de tekst op het scherm mag niet veranderen
    const plat = html.replace(/<[^>]*>/g, '');
    return { woordN, plat, zinEerste: leesZinnen[0], zinLaatste: leesZinnen[woordN - 1] };
  });
  ok(uitLezen.plat === 'El gato duerme. La casa es grande y blanca.',
     'de tekst op het scherm verandert niet ("' + uitLezen.plat + '")');
  ok(uitLezen.zinEerste === 'El gato duerme.', 'het eerste woord onthoudt zijn zin ("' + uitLezen.zinEerste + '")');
  ok(uitLezen.zinLaatste === 'La casa es grande y blanca.', 'en het laatste die van hem ("' + uitLezen.zinLaatste + '")');

  const bewaard = await page.evaluate(() => {
    S.mijn = {};
    const d = { id: 'mijn-duerme', eigen: true, plat: 'duerme', es: 'dormir', nl: 'slapen' };
    mijnBij(d, 'El gato duerme.');
    const rij = mijnWoordLijst().filter((w) => w.id === 'mijn-duerme')[0] || null;
    return { opgeslagen: (S.mijn.duerme || {}).z, ej: rij && rij.ej };
  });
  ok(bewaard.opgeslagen === 'El gato duerme.', 'de zin wordt opgeslagen bij het woord');
  ok(bewaard.ej === 'El gato duerme.', 'en komt als voorbeeldzin de pool in, in hetzelfde veld als de kernwoorden');

  ok(errs.length === 0, 'geen javascriptfouten' + (errs.length ? ': ' + errs.slice(0, 3).join(' | ') : ''));

  await browser.close();
  console.log(fout ? '\n' + fout + ' fout' : '\nalles groen');
  process.exit(fout ? 1 : 0);
})();
