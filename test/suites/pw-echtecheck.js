// v20.0: de laatste stap naar vast is een check die je niet zelf beoordeelt.
//
// Het verhaal in één zin: een woord komt alleen in de bovenste doos als je het terugvindt zonder dat
// het antwoord op het scherm staat. Daarvoor was de woordoefening een flashcard met "wist ik" en
// "wist niet", en dus was de A1-balk op Vandaag een optelsom van hoe goed je over jezelf denkt.
//
// Wat deze suite bewaakt, in die volgorde: dat "wist ik" je niet meer voorbij de een-na-laatste doos
// brengt, dat je op dat punt een check krijgt met vier mogelijkheden in de productieve richting, dat
// goed het woord vastzet en de A1-teller laat stijgen, dat fout een doosje terugzet zonder de hele
// rij weg te gooien, en dat wie van voor v20.0 komt niets kwijtraakt.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

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

// Zet één woord klaar in de wachtrij, in de doos die de test nodig heeft. Rechtstreeks, want de
// echte weg naar doos 4 is vier goede beurten over veertien dagen en die heeft een test niet.
async function zetKlaar(page, box, gecheckt) {
  return page.evaluate(([b, k]) => {
    const map = pcicMap(), niv = pcicNiv();
    let id = null;
    for (const sleutel in map) {
      if ((map[sleutel] || []).some((x) => niv[x] === 'A1') && WORDS.some((w) => w.id === sleutel)) { id = sleutel; break; }
    }
    if (!id) return { fout: 'geen A1-woord gevonden dat ook in WORDS staat' };
    const w = WORDS.find((x) => x.id === id);
    S.srs = S.srs || {};
    S.srs[id] = k ? { box: b, due: today(), k: 1 } : { box: b, due: today() };
    wQueue = [w];
    wRondeZet(wQueue);
    wCheck = null;
    renderWord();
    return { id: id, es: w.es, nl: wTrans(w), dek: voortgangTellers().dek.A1 || 0 };
  }, [box, gecheckt ? 1 : 0]);
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 360, height: 780 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await nieuwProfiel(page);
  await page.evaluate(() => show('woorden'));
  await page.waitForTimeout(400);

  console.log('\n-- versie --');
  const versie = await page.evaluate(() => APP_VERSIE);
  ok(minstens(versie, 'v20.0'), 'versie is minstens v20.0 (nu ' + versie + ')');

  console.log('\n-- wanneer is een check nodig --');
  const nodig = await page.evaluate(() => {
    const d = stevigDrempel();
    return {
      een: wCheckNodig({ box: d - 1 }),
      met: wCheckNodig({ box: d - 1, k: 1 }),
      boven: wCheckNodig({ box: d, k: 1 }),
      laag: wCheckNodig({ box: d - 2 }),
      leeg: wCheckNodig(null),
      drempel: d
    };
  });
  ok(nodig.drempel === 5, 'de bovenste doos is nog steeds doos 5');
  ok(nodig.een === true, 'op de een-na-laatste doos zonder vinkje: check nodig');
  ok(nodig.met === false, 'met vinkje: geen check meer, die is al gedaan');
  ok(nodig.boven === false, 'een woord dat al vast staat krijgt geen check');
  ok(nodig.laag === false, 'lager in de rij is het gewoon een kaartje');
  ok(nodig.leeg === false, 'een woord dat je nooit zag krijgt geen check');

  console.log('\n-- "wist ik" brengt je niet meer in de bovenste doos --');
  const klaar3 = await zetKlaar(page, 3, false);
  ok(!klaar3.fout, 'er is een A1-woord om mee te testen (' + klaar3.es + ')');
  const flash = await page.evaluate(() => !!document.getElementById('btnShow'));
  ok(flash, 'op doos 3 staat er nog gewoon een flashcard');
  await page.click('#btnShow'); await page.waitForTimeout(150);
  await page.click('#btnGood'); await page.waitForTimeout(250);
  const na3 = await page.evaluate((id) => ({ box: S.srs[id].box, k: S.srs[id].k || 0 }), klaar3.id);
  ok(na3.box === 4, 'een goede beurt brengt hem naar doos 4 (nu ' + na3.box + ')');
  ok(!na3.k, 'zelfbeoordeling zet geen vinkje');

  console.log('\n-- op doos 4 krijg je de check --');
  const klaar4 = await zetKlaar(page, 4, false);
  const kaart = await page.evaluate(() => {
    const opties = Array.from(document.querySelectorAll('[data-wcheck]')).map((b) => b.getAttribute('data-wcheck'));
    const groot = document.querySelector('#wCard .big');
    return {
      opties: opties,
      uniek: new Set(opties).size,
      vraag: groot ? groot.innerText.trim() : '',
      show: !!document.getElementById('btnShow'),
      stop: !!document.getElementById('btnWStop'),
      balk: !!document.querySelector('#wCard .wbalk, #wCard .progressbar'),
      tekst: document.getElementById('wCard').innerText.replace(/\s+/g, ' ')
    };
  });
  ok(kaart.opties.length === 4, 'er staan vier mogelijkheden (' + kaart.opties.length + ')');
  ok(kaart.uniek === 4, 'ze zijn alle vier verschillend');
  ok(kaart.opties.indexOf(klaar4.es) !== -1, 'het goede antwoord zit erbij');
  ok(!kaart.show, 'er is geen knop die het antwoord voor je omdraait');
  ok(kaart.vraag === klaar4.nl, 'de vraag staat in jouw taal, het antwoord is Spaans: dit is produceren');
  ok(kaart.stop, 'stoppen kan hier net zo goed als op een gewoon kaartje');
  ok(kaart.balk, 'de voortgangsbalk van de ronde staat er ook op');
  ok(!/[—–]|--/.test(kaart.tekst), 'geen streepjes op de kaart');

  console.log('\n-- goed: vast, en de A1-teller loopt op --');
  await page.evaluate((es) => {
    const b = Array.from(document.querySelectorAll('[data-wcheck]')).find((x) => x.getAttribute('data-wcheck') === es);
    if (b) b.click();
  }, klaar4.es);
  await page.waitForTimeout(300);
  const naGoed = await page.evaluate((id) => ({
    box: S.srs[id].box, k: S.srs[id].k || 0, p: S.srs[id].p || 0,
    dek: voortgangTellers().dek.A1 || 0,
    verder: !!document.getElementById('btnWCheckVerder'),
    zegt: document.getElementById('wCard').innerText.replace(/\s+/g, ' ')
  }), klaar4.id);
  ok(naGoed.box === 5, 'het woord staat nu in de bovenste doos (' + naGoed.box + ')');
  ok(naGoed.k === 1, 'het vinkje staat, en alleen deze check kan dat zetten');
  ok(naGoed.p >= 1, 'de beurt telt als produceren (st.p = ' + naGoed.p + ')');
  ok(naGoed.dek === klaar4.dek + 1, 'de A1-teller staat een hoger (' + klaar4.dek + ' -> ' + naGoed.dek + ')');
  ok(naGoed.verder, 'je ziet wat je gekozen had en gaat zelf verder');

  console.log('\n-- fout: een doosje terug, niet helemaal opnieuw --');
  const klaarF = await zetKlaar(page, 4, false);
  await page.evaluate((es) => {
    const b = Array.from(document.querySelectorAll('[data-wcheck]')).find((x) => x.getAttribute('data-wcheck') !== es);
    if (b) b.click();
  }, klaarF.es);
  await page.waitForTimeout(300);
  const naFout = await page.evaluate((id) => ({
    box: S.srs[id].box, k: S.srs[id].k || 0,
    zegt: document.getElementById('wCard').innerText.replace(/\s+/g, ' ')
  }), klaarF.id);
  ok(naFout.box === 3, 'hij zakt één doosje, niet naar nul (' + naFout.box + ')');
  ok(!naFout.k, 'zonder goede check geen vinkje');
  ok(naFout.zegt.indexOf(klaarF.es) !== -1, 'het goede antwoord staat er daarna wel bij');

  console.log('\n-- met vinkje is het weer een gewoon kaartje --');
  await zetKlaar(page, 4, true);
  const metVink = await page.evaluate(() => ({
    show: !!document.getElementById('btnShow'),
    check: document.querySelectorAll('[data-wcheck]').length
  }));
  ok(metVink.show && metVink.check === 0, 'wie de check gehad heeft, krijgt hem niet elke keer opnieuw');

  console.log('\n-- niemand raakt iets kwijt door deze verbetering --');
  const oud = await page.evaluate(() => {
    const s = normaliseerState({ srs: { oud5: { box: 5, due: '2020-01-01' }, oud4: { box: 4, due: '2020-01-01' } } });
    return { vijf: s.srs.oud5.k || 0, vier: s.srs.oud4.k || 0 };
  });
  ok(oud.vijf === 1, 'een woord dat al vast stond houdt zijn plek in de balk');
  ok(oud.vier === 0, 'een woord dat er nog niet was, doet gewoon de check');

  ok(errs.length === 0, 'geen javascriptfouten: ' + errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fout ? '\n' + fout + ' PUNT(EN) GEFAALD' : '\nALLES GROEN');
  process.exit(fout ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
