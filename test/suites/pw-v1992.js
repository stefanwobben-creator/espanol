const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

const U = 'http://localhost:8321/espanol-stefan.html';

// Niet gelijk aan maar minstens. Acht suites zijn eerder rood geworden puur omdat het versienummer
// een keer omhoog ging; een suite hoort te breken als het gedrag verandert, niet als de teller loopt.
function minstens(nu, vanaf) {
  const p = (v) => (v || '').replace(/^v/, '').split('.').map(Number);
  const [a, b] = [p(nu), p(vanaf)];
  return a[0] > b[0] || (a[0] === b[0] && a[1] >= b[1]);
}

async function nieuwProfiel(page) {
  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Test' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    var w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
  await page.waitForTimeout(200);
}

async function wegMetOverlays(page) {
  await page.evaluate(() => {
    var w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
}

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await b.newPage({ viewport: { width: 400, height: 860 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));

  await nieuwProfiel(page);

  console.log('\n-- versie --');
  const versie = await page.evaluate(() => APP_VERSIE);
  ok(minstens(versie, 'v19.92'), 'versie is minstens v19.92 (nu ' + versie + ')');

  console.log('\n-- verse speeltuin: alleen wat iets kan tonen --');
  /* v23.145: de Speeltuin klapt zichzelf in tot drie tegels; de rest staat achter "alle spellen".
     Deze suite gaat over iets anders, namelijk welk spel al kán draaien en welk nog niet (SPEEL_EIS),
     en dat staat los van de opmaak. Dus zetten we hem hier open. Dat de inklap zelf werkt bewaakt
     pw-waarjeloopt. */
  await page.evaluate(() => { S.srs = {}; S.speelOoit = {}; S.speelAlles = false; S.spelAlles = true; try { persist(); } catch (e) {} show('speeltuin'); });
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot-v1992-speeltuin-vers.png' });

  const menu = await page.evaluate(() => {
    var el = document.getElementById('funCard');
    return {
      klaar: Array.prototype.map.call(el.querySelectorAll(".lesson[id^='ft']"), e => e.id),
      straks: el.querySelectorAll(".lesson:not([id])").length,
      kop: /Komt er straks bij/.test(el.innerHTML),
      alles: !!document.getElementById('speelAlles'),
      tekst: el.innerText
    };
  });
  console.log('  klaar ::', menu.klaar.join(','));
  console.log('  straks ::', menu.straks);
  // v21.5: de Speeltuin heeft alleen nog spelletjes; Escuchar, El Corrector en de Conjugador zijn
  // naar Oefenen verhuisd. Een exacte telling maakt elke verhuizing een valse regressie, dus we
  // toetsen wat de test eigenlijk bewaakt: niet alles staat meteen open.
  ok(menu.klaar.length >= 1 && menu.klaar.length < menu.klaar.length + menu.straks, 'niet alles staat meteen open (' + menu.klaar.length + ' klaar, ' + menu.straks + ' grijs)');
  // v23.147: Aventura is geschrapt (2057 regels, geen spoor van gebruik). Musica staat er nog.
  ok(menu.klaar.indexOf('ftAvt') === -1, 'Aventura is er niet meer');
  /* v23.218: hier stond ok(...'ftMusica'...). Muziek is eruit; Música was het enige spel zonder
     materiaal-eis en dus de enige die op dag 1 altijd meedeed. */
  // v21.5: de Conjugador is naar Oefenen verhuisd; de Speeltuin heeft alleen nog spelletjes.
  // v23.145: Palabra Duel staat niet meer vooraan (die heeft een tweede speler nodig), maar hij is
  // er nog wel, achter "alle spellen".
  ok(menu.klaar.indexOf('ftDuel') !== -1, 'Palabra Duel staat er nog');
  // v21.2: exacte tellingen maken elke nieuwe oefening een valse regressie (v19.52-les).
  ok(menu.straks >= 1, 'er staat nog iets in het grijs (' + menu.straks + ')');
  ok(menu.kop, 'kop "Komt er straks bij" staat er');
  ok(menu.alles, 'de escape-link staat er');
  ok(/nu 0/.test(menu.tekst), 'de wachtregel toont een levende teller');
  ok(!/[—–]|--/.test(menu.tekst), 'geen em-dash, en-dash of dubbel koppelteken in het menu');
  ok(!/slot|Slot|🔒|vergrendeld/.test(menu.tekst), 'geen sloten en geen vergrendeltaal');

  console.log('\n-- alles tonen kan met een tik --');
  await wegMetOverlays(page);
  await page.click('#speelAlles'); await page.waitForTimeout(350);
  const na = await page.evaluate(() => ({
    n: document.querySelectorAll("#funCard .lesson[id^='ft']").length,
    kop: /Komt er straks bij/.test(document.getElementById('funCard').innerHTML),
    s: S.speelAlles
  }));
  ok(na.n === menu.klaar.length + menu.straks, 'na de tik staan alle spellen er (' + na.n + ')');
  ok(!na.kop, 'het grijze blok is weg');
  ok(na.s === true, 'de keuze is opgeslagen in S.speelAlles');

  console.log('\n-- woorden laten de woordspellen verschijnen --');
  await page.evaluate(() => {
    S.speelAlles = false; S.speelOoit = {}; S.srs = {}; S.spelAlles = true;
    WORDS.slice(0, 12).forEach(function (w) { S.srs[w.id] = { n: 1, d: 0 }; });
    try { persist(); } catch (e) {}
    renderFun();
  });
  await page.waitForTimeout(350);
  const w12 = await page.evaluate(() => Array.prototype.map.call(document.querySelectorAll("#funCard .lesson[id^='ft']"), e => e.id));
  console.log('  klaar ::', w12.join(','));
  ok(w12.indexOf('ftWs') !== -1 && w12.indexOf('ftKruis') !== -1 && w12.indexOf('ftMem') !== -1, 'bij 12 woorden komen sopa, crucigrama en memory erbij');
  ok(await page.evaluate(() => speelKlaar('ws')) === true, 'speelKlaar(ws) is waar bij 12 woorden');
  ok(await page.evaluate(() => { S.srs = {}; WORDS.slice(0, 5).forEach(function (w) { S.srs[w.id] = { n: 1, d: 0 }; }); return speelKlaar('ws'); }) === false, 'bij 5 woorden nog niet');

  console.log('\n-- niemand raakt iets kwijt --');
  const ooit = await page.evaluate(() => {
    S.speelOoit = null; S.speelAlles = false;
    S.srs = {}; WORDS.slice(0, 3).forEach(function (w) { S.srs[w.id] = { n: 1, d: 0 }; });
    speelOoitInit();
    return { ws: speelKlaar('ws'), corr: speelKlaar('corr') };
  });
  ok(ooit.ws === true && ooit.corr === true, 'een bestaande speler met srs houdt alle spellen');

  console.log('\n-- dagknoppen bieden alleen speelbare spellen aan --');
  const dag = await page.evaluate(() => {
    S.speelOoit = {}; S.speelAlles = false; S.srs = {};
    var k = dagSpelKeuze();
    return { v: k.map(function (x) { return x.v; }), alle: k.every(function (x) { return speelKlaar(x.v); }) };
  });
  console.log('  dagspellen ::', dag.v.join(','));
  ok(dag.alle, 'elk aangeboden dagspel kan vandaag iets tonen');
  /* v23.218: hier stond `dag.v.length >= 1`. Deze proef zet S.srs op leeg, en Música was het enige
     spel zonder materiaal-eis; die garantie is met muziek meeverdwenen. Wat overeind blijft is de
     regel die er echt toe doet en die hierboven staat: alles wat wordt aangeboden kan ook echt.
     v23.65 koos daar bewust voor ("niets aanbieden is het eerlijke antwoord"). */
  ok(dag.v.length === 0 || dag.alle, 'of er is niets, of alles wat er is kan echt (' + dag.v.length + ')');

  /* v23.218: hier stonden vier blokken over de muziekpagina: wie de video mag wisselen, wie een
     liedje mag verbergen, wat er met een eigen liedje mag, en de beheerrol via ?beheer=chispa.
     Muziek is er niet meer, en de beheerrol bestond alleen om de liedjeslijst te mogen aanraken.
     Zie pw-muziekweg.js voor wat er in plaats daarvan bewaakt wordt. */

  console.log('\n-- speeltuin blijft werken: een spel openen --');
  await page.evaluate(() => { S.speelAlles = true; try { persist(); } catch (e) {} show('speeltuin'); });
  await page.waitForTimeout(350);
  await wegMetOverlays(page);
  await page.click('#ftMem'); await page.waitForTimeout(500);
  ok(await page.evaluate(() => funView) === 'mem', 'Memory opent nog gewoon');
  await page.screenshot({ path: 'shot-v1992-conj.png' });

  console.log('\nPAGE ERRORS:', errs);
  ok(errs.length === 0, 'geen js-fouten');
  console.log(fout ? '\n*** ' + fout + ' FOUT ***' : '\nALLES GROEN');
  await b.close();
  process.exit(fout ? 1 : 0);
})();
