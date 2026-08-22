// De verbouwing van 12 aug (v23.64 t/m v23.69). Stefan, over het dagscherm: "je ziet nu heel veel
// info in een keer in je scherm. Geen idee wat de app allemaal te bieden heeft, wat dit allemaal
// betekent. Je hebt overwhelm. Deze ux is echt kapot."
//
// Vijf beloften uit die ronde, en ze staan hier omdat een belofte zonder test wegrot:
//   1. het dagscherm heeft hoogstens een handvol getallen, en geen dashboard
//   2. wie klaar is hoort wat er morgen gebeurt, én dat er geen herinnering komt
//   3. Chispa spreekt de eerste week eerst jouw taal
//   4. het eerste kaartje legt uit wat je moet doen, en stopt daarmee zodra je een les af hebt
//   5. onder "Even spelen" staan spellen en geen oefeningen, en elk spel zegt wat het is
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

async function versProfiel(page, naam) {
  await page.goto(U); await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.clear(); localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload(); await page.waitForTimeout(900);
  await page.fill('input[placeholder="Naam / Name"], input[placeholder="Naam"], input[placeholder="Name"]', naam + Date.now());
  await page.click('button[data-lvl="A0"]');
  await page.click('#btnNewProf');
  await page.waitForFunction(() => !!activeProfile(), { timeout: 15000 });
  await page.waitForTimeout(1200);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
}
async function dagOpnieuw(page) {
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(400);
}

/* 22 aug, v23.167: het dagscherm heeft een voorkant en een achterkant gekregen. Vóór je les staat
   er één ding, je les; het bord, de lijn en de speelkaart komen pas tevoorschijn als je les van
   vandaag af is. Reden: zeven kaarten onder elkaar maakten van dit scherm een menu, en op een menu
   is beginnen de saaiste optie.

   Deze suite meet daarom op twee momenten. Belofte 1 (geen dashboard) geldt op allebei, dus wordt
   hij op allebei gemeten: het is juist de achterkant waar een dashboard weer zou kunnen groeien.
   Belofte 3 (Chispa's groet) hoort bij de voorkant, want als je klaar bent zegt ze iets anders.
   Belofte 5 (de speelkaart) hoort bij de achterkant. */
async function lesVandaag(page, af) {
  await page.evaluate((a) => {
    S.lesFlow = S.lesFlow || {};
    if (a) S.lesFlow[today()] = true; else delete S.lesFlow[today()];
    try { persist(); } catch (e) {}
  }, af);
  await dagOpnieuw(page);
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await versProfiel(page, 'Verbouw');

  // ---------------------------------------------------------------- 1
  console.log('\n-- 1. het dagscherm is geen dashboard --');
  const meetDag = () => page.evaluate(() => {
    const el = document.getElementById('tab-lessen');
    const t = (el.innerText || '').replace(/\s+/g, ' ');
    return {
      getallen: (t.replace(/\b[ABC][12]\b/g, '').match(/\d+/g) || []),
      hoogte: document.body.scrollHeight,
      venster: window.innerHeight,
      legenda: !!document.querySelector('#tab-lessen .vgLegenda'),
      tegels: !!document.querySelector('#tab-lessen .statgrid'),
      balk: !!document.querySelector('#tab-lessen #dagBasisBalk')
    };
  });
  await lesVandaag(page, false);
  const voorLes = await meetDag();
  console.log('    voor de les ::', JSON.stringify({ getallen: voorLes.getallen, px: voorLes.hoogte }));
  ok(voorLes.getallen.length <= 6, 'ook vóór je les hoogstens zes getallen (' + voorLes.getallen.join(',') + ')');
  // en nu met de les van vandaag af, want dat is de volle stand van het scherm: op de achterkant
  // is de ruimte waar een dashboard opnieuw zou kunnen groeien.
  await lesVandaag(page, true);
  const dag1 = await meetDag();
  console.log('   ', JSON.stringify({ getallen: dag1.getallen, px: dag1.hoogte }));
  /* Gemeten op Stefans scherm vóór deze ronde: 11 getallen en 1362 px in de drukste toestand. De
     grens hieronder is ruim, want dit hoort niet rood te worden van een dagdoel dat verandert; hij
     hoort rood te worden als er weer een dashboard op dit scherm groeit. */
  ok(dag1.getallen.length <= 6, 'hoogstens zes getallen op dag 1 (' + dag1.getallen.join(',') + ')');
  ok(!dag1.legenda, 'geen legenda met SRS-doosnamen op het dagscherm');
  ok(!dag1.tegels, 'geen tegelraster met kracht en foutpercentage');
  ok(!dag1.balk, 'en geen voortgangsbalk: die staat op Voortgang, mét uitleg');

  // ---------------------------------------------------------------- 3
  console.log('\n-- 3. Chispa spreekt eerst jouw taal --');
  // haar groet hoort bij het begin van je dag, dus terug naar de voorkant: is je les af, dan zegt
  // ze iets anders ("¡Muy bien!") en gaat dit blok over een andere zin.
  await lesVandaag(page, false);
  const groet = await page.evaluate(() => {
    const p = document.querySelector('.lfsay');
    if (!p) return null;
    const es = p.querySelector('.es'), nl = p.querySelector('.nl');
    return {
      omgekeerd: p.classList.contains('omgekeerd'),
      esTop: es ? Math.round(es.getBoundingClientRect().top) : -1,
      nlTop: nl ? Math.round(nl.getBoundingClientRect().top) : -1,
      esGrootte: es ? parseFloat(getComputedStyle(es).fontSize) : 0,
      nlGrootte: nl ? parseFloat(getComputedStyle(nl).fontSize) : 0,
      esTekst: es ? es.innerText : '', nlTekst: nl ? nl.innerText : ''
    };
  });
  ok(!!groet, 'Chispa zegt iets op de dagkaart');
  ok(groet && groet.omgekeerd, 'en op dag 1 staat die zin omgekeerd');
  ok(groet && groet.nlTop < groet.esTop,
    'jouw taal staat boven (' + (groet ? groet.nlTop + ' vs ' + groet.esTop : '-') + ')');
  ok(groet && groet.nlGrootte > groet.esGrootte,
    'en in het grotere formaat (' + (groet ? groet.nlGrootte + ' vs ' + groet.esGrootte : '-') + ')');
  ok(groet && groet.esTekst.length > 0, 'het Spaans staat er nog steeds ("' + (groet ? groet.esTekst : '') + '")');
  const naWeek = await page.evaluate(() => {
    S.dagen = S.dagen || {}; S.dagen.count = 20;
    try { persist(); } catch (e) {}
    show('lessen');
    const p = document.querySelector('.lfsay');
    const es = p.querySelector('.es'), nl = p.querySelector('.nl');
    return { omgekeerd: p.classList.contains('omgekeerd'),
             esTop: Math.round(es.getBoundingClientRect().top),
             nlTop: Math.round(nl.getBoundingClientRect().top) };
  });
  ok(!naWeek.omgekeerd && naWeek.esTop < naWeek.nlTop,
    'na een week draait het om: dan staat het Spaans weer boven');
  await page.evaluate(() => { S.dagen.count = 1; try { persist(); } catch (e) {} });

  // ---------------------------------------------------------------- 5
  console.log('\n-- 5. onder "Even spelen" staan spellen, geen oefeningen --');
  const spel = await page.evaluate(() => {
    const oef = oefenItems().map(o => o.id);
    const dag = dagSpellen().map(g => g.v);
    const menu = spelInfo().map(g => g.v);
    return {
      oef: oef, dag: dag, menu: menu,
      overlapDag: dag.filter(v => oef.indexOf(v) !== -1),
      overlapMenu: menu.filter(v => oef.indexOf(v) !== -1),
      zonderZin: spelInfo().filter(g => !g.s || String(g.s).trim().length < 12).map(g => g.v),
      geenZin: spelInfo().filter(g => !/[.!?]$/.test(spelZin(g.s))).map(g => g.v)
    };
  });
  console.log('    dagrotatie ::', spel.dag.join(','));
  /* v21.5, Stefans eigen regel: onder Oefenen telt het mee voor je niveau, onder Spelen niet. De
     speeltuin hield zich eraan, de dagkaart niet: Escuchar, El Corrector en Rompecabezas stonden
     onder de kop "Even spelen". */
  ok(spel.overlapDag.length === 0, 'de dagrotatie bevat geen oefeningen (' + spel.overlapDag.join(',') + ')');
  ok(spel.overlapMenu.length === 0, 'en de speeltuin ook niet (' + spel.overlapMenu.join(',') + ')');
  ok(spel.zonderZin.length === 0, 'elk spel heeft een regel die zegt wat je doet (' + spel.zonderZin.join(',') + ')');
  ok(spel.geenZin.length === 0, 'en die regel is een hele zin, met een punt (' + spel.geenZin.join(',') + ')');
  // de speelkaart staat achter je les, dus die eerst op af zetten; zie de toelichting bovenin.
  await lesVandaag(page, true);
  const kaart = await page.evaluate(() => {
    const k = document.getElementById('speelKaart');
    return {
      er: !!k,
      rijen: k ? k.querySelectorAll('.speelrij').length : -1,
      tekst: k ? k.innerText.replace(/\s+/g, ' ') : '',
      allemaalSpeelbaar: k ? [].slice.call(k.querySelectorAll('[data-speel]'))
        .every(b => speelKlaar(b.getAttribute('data-speel'))) : false
    };
  });
  ok(kaart.er && kaart.rijen >= 1, 'de speelkaart toont regels in plaats van tegels (' + kaart.rijen + ')');
  /* v19.92: een knop op je dagscherm die uitkomt op "leer eerst wat meer woordjes" leert je dat de
     knoppen hier niet betrouwbaar zijn. Vóór v23.65 stond er een noodgreep in dagSpelKeuze() die
     precies dat deed zodra niets kon. */
  ok(kaart.allemaalSpeelbaar, 'en alles wat er staat kan vandaag ook echt draaien');
  ok(/komen erbij|komt erbij/.test(kaart.tekst),
    'met erbij hoeveel spellen er nog komen (' + kaart.tekst.slice(0, 140) + ')');

  // ---------------------------------------------------------------- 4
  console.log('\n-- 4. het eerste kaartje legt zichzelf uit --');
  await page.evaluate(() => { scopeLesson = null; buildQueue(); show('woorden'); renderWord(); });
  await page.waitForTimeout(400);
  const voor = await page.evaluate(() => document.getElementById('wCard').innerText);
  ok(/eerst zelf te bedenken/i.test(voor), 'op de voorkant staat dat je het eerst zelf moet proberen');
  await page.evaluate(() => showWord());
  await page.waitForTimeout(300);
  const achter = await page.evaluate(() => document.getElementById('wCard').innerText);
  ok(/Beoordeel jezelf eerlijk/i.test(achter), 'op de achterkant staat wat de twee knoppen doen');
  ok(/langer weg/i.test(achter) && /morgen terug/i.test(achter),
    'en het zegt allebei de kanten, niet alleen "wees eerlijk"');
  const naLes = await page.evaluate(() => {
    S.lesFlowEerste = today();
    try { persist(); } catch (e) {}
    renderWord();
    const v = document.getElementById('wCard').innerText;
    showWord();
    return { voor: v, achter: document.getElementById('wCard').innerText };
  });
  ok(!/eerst zelf te bedenken/i.test(naLes.voor) && !/Beoordeel jezelf eerlijk/i.test(naLes.achter),
    'en zodra je je eerste les af hebt is de uitleg weg');

  // ---------------------------------------------------------------- 2
  console.log('\n-- 2. wie klaar is hoort wat er morgen gebeurt --');
  const klaar = await page.evaluate(() => {
    const t = today();
    allowedWordIds().slice(0, 9).forEach(id => { S.srs[id] = { box: 2, due: addDays(t, 1), n: 2 }; });
    S.lesFlow = S.lesFlow || {}; S.lesFlow[t] = true;
    S.dag = S.dag || {}; S.dag.klaar = t;
    S.dagen = S.dagen || {}; S.dagen.count = 1;
    try { persist(); } catch (e) {}
    show('lessen');
    return { tekst: document.getElementById('tab-lessen').innerText.replace(/\s+/g, ' '),
             n: morgenTerug() };
  });
  await page.waitForTimeout(300);
  console.log('    morgenTerug() ::', klaar.n);
  ok(klaar.n > 0, 'er staat morgen echt iets klaar (' + klaar.n + ')');
  ok(new RegExp('Morgen komen er ' + klaar.n + '\\b').test(klaar.tekst),
    'en de kaart noemt datzelfde getal, niet een eigen sommetje');
  /* Geteld vóór deze ronde: nul aanroepen van Notification, serviceWorker of showNotification in de
     hele app, en geen enkele regel over morgen op het dagscherm. Dat is precies de combinatie waar
     iemand op wacht die denkt dat hij wel gepord wordt. */
  ok(/geen herinnering/i.test(klaar.tekst), 'en dat er geen herinnering komt');
  /* Twee keer kijken, want de bron alleen is niet genoeg: de eerste versie van deze regel zocht op
     "showNotification" zonder haakje en vond zijn eigen toelichting in het commentaar erboven. Nu
     wordt er op aanroepen gezocht én wordt er gekeken of er tijdens het draaien iets geregistreerd
     staat. */
  const geenPush = await page.evaluate(async () => {
    let regs = 0;
    try { regs = (await navigator.serviceWorker.getRegistrations()).length; } catch (e) { regs = 0; }
    return {
      bron: (document.documentElement.innerHTML.match(/showNotification\(|serviceWorker\.register\(|new Notification\(/g) || []).length,
      regs: regs,
      perm: (window.Notification && Notification.permission) || 'geen'
    };
  });
  ok(geenPush.bron === 0, 'want de app roept nergens een melding aan (' + geenPush.bron + ' aanroepen)');
  ok(geenPush.regs === 0 && geenPush.perm !== 'granted',
    'en er staat ook niets geregistreerd (' + geenPush.regs + ' servicewerkers, toestemming: ' + geenPush.perm + ')');
  const naDrie = await page.evaluate(() => {
    S.dagen.count = 9;
    try { persist(); } catch (e) {}
    show('lessen');
    return document.getElementById('tab-lessen').innerText.replace(/\s+/g, ' ');
  });
  ok(/Morgen komen er/.test(naDrie), 'na je eerste dagen blijft het aantal staan');
  ok(!/geen herinnering/i.test(naDrie),
    'maar de zin over de herinnering niet: die hoef je één keer te horen');

  ok(errs.length === 0, 'geen javascriptfouten: ' + errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fout ? '\n' + fout + ' PUNT(EN) GEFAALD' : '\nALLES GROEN');
  process.exit(fout ? 1 : 0);
})();
