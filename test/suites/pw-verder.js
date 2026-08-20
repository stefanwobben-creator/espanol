// v20.2: verder waar je was. De knop die er al staat weet wat er nu te doen is.
//
// Stefan, 5 augustus: "Waar in een oefening is men nu." De les bestond tot nu toe alleen in het
// geheugen van het tabblad, dus wie halverwege wegklikte begon de volgende keer weer bij stap 1.
// Dat is precies wat de stopknop beloofde ("Klaar voor nu, je verliest niets") en niet waarmaakte.
//
// Wat deze suite vastlegt, in twee richtingen:
//   - het herstelpunt bestaat en wordt bij elke overgang bijgewerkt, overleeft een herlading en
//     de stopknop, en brengt je terug naar de stap waar je was en niet naar stap 1.
//   - en het dagscherm krijgt er geen blok bij. De bestaande startknop wordt contextueel: één
//     primaire knop, en opnieuw beginnen is een tekstregel eronder. Twee knoppen naast elkaar
//     zou precies de tweede bevinding van zijn moeder terugbrengen (knoppen waarvan de bedoeling
//     onduidelijk is), dus dat wordt hier hard afgevangen.
//   - een herstelpunt van gisteren is geen "waar je was" maar een verlopen plan, en gaat weg.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

function minstens(nu, vanaf) {
  const p = (v) => (v || '').replace(/^v/, '').split('.').map(Number);
  const [a, b] = [p(nu), p(vanaf)];
  return a[0] > b[0] || (a[0] === b[0] && a[1] >= b[1]);
}

async function stil(page) {
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    var w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
  await page.waitForTimeout(150);
}

async function nieuwProfiel(page) {
  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Test' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await stil(page);
}

// Wegklikken zoals een mens dat doet: het tabblad opnieuw laden. Het geheugen van de les is dan
// echt weg, en wat er nog is, is wat er bewaard is.
async function herlaad(page) {
  await page.goto(U);
  await page.waitForTimeout(800);
  await stil(page);
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(350);
}

async function dagOpnieuw(page) {
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(350);
}

async function startKaart(page) {
  return page.evaluate(() => {
    const knop = document.getElementById('btnStartLesFlow');
    const kaart = knop ? knop.closest('.card') : null;
    const kick = kaart ? kaart.querySelector('.kicker') : null;
    return {
      knop: !!knop,
      knopTekst: knop ? knop.innerText.replace(/\s+/g, ' ').trim() : '',
      kicker: kick ? kick.innerText.replace(/\s+/g, ' ').trim() : '',
      opnieuw: !!document.getElementById('btnLesOpnieuw'),
      knoppen: kaart ? kaart.querySelectorAll('button').length : -1,
      primair: kaart ? kaart.querySelectorAll('button.primary').length : -1,
      tekst: kaart ? kaart.innerText.replace(/\s+/g, ' ') : ''
    };
  });
}

async function bewaard(page) {
  return page.evaluate(() => (S.lesFlowNu ? JSON.parse(JSON.stringify(S.lesFlowNu)) : null));
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 360, height: 780 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await nieuwProfiel(page);

  console.log('\n-- versie --');
  const versie = await page.evaluate(() => APP_VERSIE);
  ok(minstens(versie, 'v20.2'), 'versie is minstens v20.2 (nu ' + versie + ')');

  console.log('\n-- wie nog niets deed, krijgt geen aanbod om verder te gaan --');
  await dagOpnieuw(page);
  const vers = await startKaart(page);
  ok((await bewaard(page)) === null, 'een vers profiel heeft geen herstelpunt');
  ok(/Start je les/i.test(vers.kicker), 'het kopje zegt gewoon "Start je les" (' + vers.kicker + ')');
  ok(/Start je les/i.test(vers.knopTekst), 'en de knop ook (' + vers.knopTekst + ')');
  ok(!vers.opnieuw, 'geen regel "liever opnieuw beginnen" als er niets is om te hervatten');
  ok(await page.evaluate(() => lesFlowHervatKan() === false), 'lesFlowHervatKan() zegt zelf ook nee');

  console.log('\n-- de les bewaart waar je bent --');
  await page.click('#btnStartLesFlow');
  await page.waitForTimeout(700);
  const naStart = await bewaard(page);
  ok(!!naStart, 'zodra de les begint staat er een herstelpunt');
  ok(naStart && naStart.stap === 'woorden', 'en het is de eerste stap (' + (naStart && naStart.stap) + ')');
  ok(await page.evaluate(() => today() === S.lesFlowNu.d), 'met de dag van vandaag erbij');
  const scherm = await page.evaluate(() => (document.querySelector('.view.on') || {}).id || '');
  ok(scherm === 'woorden' || scherm === '', 'je staat in de woordjes (' + scherm + ')');

  console.log('\n-- een herlading haalt je niet onderuit --');
  await herlaad(page);
  const na1 = await bewaard(page);
  ok(!!na1 && na1.stap === 'woorden', 'het herstelpunt overleeft het herladen van het tabblad');
  ok(await page.evaluate(() => lesFlow === null), 'terwijl de draaiende les wél weg is');
  /* v23.131: hier verwachtte deze suite meteen "Verder waar je was", terwijl er nog geen enkel
     antwoord gegeven was. Dat is precies de zin die een gloednieuwe gebruiker op zijn eerste scherm
     te lezen kreeg. Verdergaan veronderstelt dat je ergens wás, dus eerst de nieuwe regel meten, en
     daarna pas het gedrag waar deze suite voor bestaat. */
  const kaart0 = await startKaart(page);
  ok(/Start je les/i.test(kaart0.kicker),
    'DE REGEL: begonnen maar niets beantwoord blijft "Start je les" (' + kaart0.kicker + ')');
  ok(!!(await bewaard(page)),
    'CONTROLE: het herstelpunt staat er wél, dus je komt nog steeds op stap 1 terug');

  // en nu iemand die vandaag echt iets gedaan heeft
  await page.evaluate(() => {
    S.newIntro = S.newIntro || {}; S.newIntro[today()] = 1;
    try { persist(); } catch (e) {}
    show('lessen');   // het dagscherm opnieuw tekenen, anders lees je de vorige stand
  });
  await page.waitForTimeout(600);
  const kaart1 = await startKaart(page);
  /* v23.140: het aantal stappen is niet meer vast vier. Sinds v23.135 komt het uit dagPlan(), en
     sinds v23.140 zit het inputblok erin als er iets te lezen of te luisteren is. De bewering
     blijft dezelfde ("de stap staat erbij, met het totaal"), maar het totaal wordt gevraagd in
     plaats van bevroren. */
  const tot = await page.evaluate(() => lesFlowStapTotaal(S.lesFlowNu));
  ok(/Verder waar je was/i.test(kaart1.kicker), 'het kopje zegt nu "Verder waar je was" (' + kaart1.kicker + ')');
  ok(new RegExp('stap 1/' + tot, 'i').test(kaart1.kicker), 'met de stap erbij, zodat het geen vage belofte is (van ' + tot + ')');
  ok(/Woordjes/i.test(kaart1.kicker), 'en de naam van die stap');
  ok(/Verder waar je was/i.test(kaart1.knopTekst), 'de knop zegt hetzelfde (' + kaart1.knopTekst + ')');
  ok(kaart1.opnieuw, 'eronder staat "liever opnieuw beginnen"');
  ok(kaart1.primair === 1, 'precies één primaire knop, geen twee die om aandacht vechten (' + kaart1.primair + ')');
  ok(new RegExp('Je stopte bij stap 1 van ' + tot).test(kaart1.tekst), 'en in gewone taal eronder waar je gebleven was');
  ok(!/[—–]|--/.test(kaart1.tekst), 'geen streepjes in de nieuwe tekst');

  console.log('\n-- en brengt je terug naar die stap --');
  await page.click('#btnStartLesFlow');
  await page.waitForTimeout(700);
  const terug = await page.evaluate(() => ({
    stap: lesFlow ? lesFlow.stap : null,
    view: (document.querySelector('.view.on') || {}).id || ''
  }));
  ok(terug.stap === 'woorden', 'de les draait weer, op de stap waar je was (' + terug.stap + ')');

  console.log('\n-- elke overgang schuift het herstelpunt mee --');
  await page.evaluate(() => { lesFlow.stap = 'woorden'; wQueue = []; lesFlowVolgende(); });
  await page.waitForTimeout(600);
  const naStap = await page.evaluate(() => ({
    loopt: lesFlow ? lesFlow.stap : null,
    bewaard: S.lesFlowNu ? S.lesFlowNu.stap : null,
    num: S.lesFlowNu ? lesFlowStapNum(S.lesFlowNu) : 0,
    naam: S.lesFlowNu ? lesFlowStapNaam(S.lesFlowNu) : ''
  }));
  ok(naStap.loopt !== 'woorden', 'de les is een stap verder (' + naStap.loopt + ')');
  ok(naStap.bewaard === naStap.loopt, 'en het herstelpunt is meegeschoven (' + naStap.bewaard + ')');
  ok(naStap.num >= 2 && naStap.num <= tot, 'de stap heeft een nummer boven de eerste (' + naStap.num + ' van ' + tot + ')');
  ok(!!naStap.naam, 'en een naam om op het dagscherm te zetten ("' + naStap.naam + '")');
  await herlaad(page);
  // .kicker staat in kapitalen in de css, dus hier hoofdletterloos vergelijken
  const kaart2 = await startKaart(page);
  const kick2 = kaart2.kicker.toLowerCase();
  ok(kick2.indexOf('stap ' + naStap.num + '/' + tot) !== -1,
    'het dagscherm noemt diezelfde stap (' + kaart2.kicker + ')');
  ok(kick2.indexOf(naStap.naam.toLowerCase()) !== -1, 'en diezelfde naam');

  console.log('\n-- "Klaar voor nu" doet wat het belooft --');
  await page.evaluate(() => { lesFlowStart(); });
  await page.waitForTimeout(700);
  const heeftStop = await page.evaluate(() => !!document.getElementById('btnWStop'));
  if (heeftStop) {
    await page.click('#btnWStop');
    await page.waitForTimeout(500);
    ok(await page.evaluate(() => lesFlow === null), 'de stopknop stopt de draaiende les');
    ok(!!(await bewaard(page)), 'maar het herstelpunt blijft staan: je verliest niets');
    const kaart3 = await startKaart(page);
    ok(/Verder waar je was/i.test(kaart3.kicker), 'en het dagscherm biedt aan verder te gaan');
  } else {
    ok(false, 'de stopknop #btnWStop was niet te vinden in het woordjesscherm');
  }

  console.log('\n-- opnieuw beginnen mag, als tekstregel --');
  await dagOpnieuw(page);
  await page.click('#btnLesOpnieuw');
  await page.waitForTimeout(700);
  const naOpnieuw = await page.evaluate(() => (S.lesFlowNu ? S.lesFlowNu.stap : null));
  ok(naOpnieuw === 'woorden', 'na "liever opnieuw beginnen" sta je weer op stap 1 (' + naOpnieuw + ')');

  console.log('\n-- een plan van gisteren is geen "waar je was" --');
  await page.evaluate(() => {
    S.lesFlowNu = { d: addDays(today(), -1), stap: 'toetsjes', quizzesTeDoen: [], vaardigheidRij: [] };
    try { persist(); } catch (e) {}
  });
  await herlaad(page);
  ok((await bewaard(page)) === null, 'normaliseerState gooit het herstelpunt van gisteren weg');
  const kaart4 = await startKaart(page);
  ok(/Start je les/i.test(kaart4.kicker), 'en het dagscherm zegt weer gewoon "Start je les"');
  ok(!kaart4.opnieuw, 'zonder regel om iets te hervatten dat er niet is');

  console.log('\n-- een afgeronde les laat niets slingeren --');
  await page.evaluate(() => { lesFlowStart(); });
  await page.waitForTimeout(500);
  ok(!!(await bewaard(page)), 'er staat weer een herstelpunt');
  await page.evaluate(() => { lesFlow.stap = 'produceren'; lesFlow.vaardigheid = null; lesFlow.vaardigheidRij = []; lesFlowVolgende(); });
  await page.waitForTimeout(800);
  ok((await bewaard(page)) === null, 'na het afronden van de les is het herstelpunt opgeruimd');

  console.log('\n-- klaar voor vandaag is klaar --');
  await page.evaluate(() => {
    S.lesFlowNu = { d: today(), stap: 'grammatica', quizzesTeDoen: [], vaardigheidRij: [] };
    S.dag = S.dag || {}; S.dag.klaar = today();
    try { persist(); } catch (e) {}
  });
  await dagOpnieuw(page);
  const dicht = await page.evaluate(() => {
    const l = document.getElementById('lessonList');
    return {
      start: !!document.getElementById('btnStartLesFlow'),
      opnieuw: !!document.getElementById('btnLesOpnieuw'),
      tekst: l ? l.innerText.replace(/\s+/g, ' ') : ''
    };
  });
  ok(!dicht.start, 'wie de dag afsloot krijgt geen startknop, ook niet met een herstelpunt');
  ok(!dicht.opnieuw, 'en geen aanbod om opnieuw te beginnen');
  ok(/Klaar voor vandaag/i.test(dicht.tekst), 'het scherm zegt dat je klaar bent (' + dicht.tekst.slice(0, 80) + ')');

  ok(errs.length === 0, 'geen javascriptfouten: ' + errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fout ? '\n' + fout + ' PUNT(EN) GEFAALD' : '\nALLES GROEN');
  process.exit(fout ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
