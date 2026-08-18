// pw-les.js (16 aug, v23.115) — is dit een les, of alwéér een toets?
//
// WAAROM DIT ER IS
//
// Stefan, na vier rondes meetinstrumenten: "ik word direct getoetst en alle tijden door elkaar,
// het is nog steeds losse toetsjes maar geen les."
//
// Hij had gelijk, en het raakt regel R5 uit het ontwerpadvies: eerst blokken, dan spreiden. Elk
// scherm in de app begon bij stap 4 (produceren, tabel weg) en hutselde alles door elkaar.
//
// WAT DEZE SUITE BEWAAKT
//
// De twee eigenschappen die dit een les maken in plaats van een toets, en die allebei stilletjes
// kunnen sneuvelen zodra iemand het scherm "verbetert":
//
//   1. STAP 0 EN 1 STELLEN GEEN VRAAG. Geen invoerveld, geen knoppen met antwoorden, geen score.
//      Je kunt niets ophalen wat er nog niet in zit; dat is het hele punt van die twee stappen.
//   2. ÉÉN TIJD TEGELIJK. Nergens in de hele les mag een vorm uit een andere tijd op het scherm
//      staan. Dat is precies wat Stefan als "alle tijden door elkaar" beschreef.
//
// En de gebruikelijke controles: de opgaven zijn niet te bedriegen, de tabel is er in stap 2 en 3
// en wég in stap 4, en de voortgang wordt onthouden.
const { chromium } = require('playwright');
const { naarTegel, naarTegelTab } = require('./tegelhulp.js');

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwLes' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  await page.evaluate(() => {
    S.lang = 'nl'; S.speelAlles = true;
    S.conjOpen = CONJ_FASES.length - 1;
    S.conjFase = CONJ_FASES[CONJ_FASES.length - 1].id;
    try { persist(); } catch (e) {}
  });

  // ---- 1. de data ----
  const data = await page.evaluate(() => ({
    zonderDoet: CONJ_TIEMPOS.filter((t) => !t.doet || !t.doetEn).map((t) => t.id),
    zonderLes: CONJ_TIEMPOS.filter((t) => !t.les).map((t) => t.id),
    // het lesbenoemde werkwoord moet echt bestaan, anders valt de les stil
    onbekend: CONJ_TIEMPOS.filter((t) => !VERBOS.some((v) => v.inf === t.les)).map((t) => t.id + '=' + t.les),
    stappen: LES_STAPPEN.length,
    stapNamen: LES_STAPPEN.filter((x) => !x.id || !x.nl || !x.en).map((x) => x.id || '?'),
    laatste: LES_STAPPEN[LES_STAPPEN.length - 1].id,
    // ongeziene regelmatige werkwoorden per tijd: zonder die pool valt stap 4b stil
    overdracht: CONJ_TIEMPOS.map((t) => ({
      t: t.id,
      n: lesOverdrachtPool(t.id, VERBOS.filter((v) => v.inf === t.les)[0]).length
    }))
  }));

  console.log('\n-- de data --');
  ok(data.zonderDoet.length === 0, 'DEKKING: elke tijd zegt wat hij doet (mist: ' + (data.zonderDoet.join(', ') || 'niets') + ')');
  ok(data.zonderLes.length === 0, 'DEKKING: elke tijd heeft een leswerkwoord (mist: ' + (data.zonderLes.join(', ') || 'niets') + ')');
  ok(data.onbekend.length === 0, 'DEKKING: dat werkwoord bestaat ook echt (fout: ' + (data.onbekend.join(', ') || 'niets') + ')');
  // v23.118: geen magisch getal. De suite hoort te breken als de les van gedrag verandert, niet
  // als er een stap bij komt.
  ok(data.stappen >= 5, 'minstens vijf stappen (nu: ' + data.stappen + ')');
  ok(data.stapNamen.length === 0,
    'DEKKING: elke stap draagt zijn eigen naam in beide talen (mist: ' + (data.stapNamen.join(', ') || 'niets') + ')');
  ok(data.laatste === 'overdracht', 'en de laatste stap is de overdracht (nu: ' + data.laatste + ')');
  ok(data.overdracht.every((x) => x.n >= 3),
    'DEKKING: elke tijd heeft ongeziene regelmatige werkwoorden om mee te toetsen (' +
    data.overdracht.map((x) => x.t + ':' + x.n).join(' ') + ')');

  // ---- 2. het keuzescherm en de aanbeveling ----
  const tegel = await naarTegel(page, 'ftLes');
  const keuze = await page.evaluate(() => ({
    view: funView,
    knoppen: document.querySelectorAll('.les-t').length,
    // v23.125: hier stond "5". Sinds de les ook patronen onderwijst zijn het er elf, en het
    // vaste getal is de vijfde keer dat testcode een aantal napraatte dat in de data staat.
    rijen: lesRijIds().length,
    aanbevolen: (document.getElementById('lesAanbevolen') || {}).innerText || ''
  }));
  const metStruikel = await page.evaluate(() => {
    S.brok = {'vorm.tijd': {goed: 6, fout: 6, beste: 6, laatst: today(), rondes: 1,
                            verwar: {'imperfecto>indefinido': 4}}};
    lesSpel = null; renderFunLes();
    return (document.getElementById('lesAanbevolen') || {}).innerText || '';
  });

  console.log('\n-- het keuzescherm --');
  ok(tegel === 1 && keuze.view === 'les', 'de tegel staat er en klikken opent de les (nu: ' + keuze.view + ')');
  ok(keuze.knoppen === keuze.rijen, 'één knop per rij die de les kan onderwijzen (nu: ' + keuze.knoppen + ' van de ' + keuze.rijen + ')');
  ok(keuze.aanbevolen === '', 'zonder struikelblok geen aanbeveling (geen verzonnen advies)');
  ok(/imperfecto/.test(metStruikel),
    'met een struikelblok uit v23.114 wijst hij die tijd aan ("' + metStruikel.replace(/\s+/g, ' ').slice(0, 90) + '")');

  // ---- 3. DE KERN: stap 0 en 1 stellen geen vraag ----
  const stap0 = await page.evaluate(() => {
    lesStart('imperfecto'); renderFunLes();
    return {
      stap: lesSpel.stap,
      invoer: document.querySelectorAll('#lesInput').length,
      antwoordknoppen: document.querySelectorAll('.les-o').length,
      tekst: document.getElementById('funCard').innerText,
      verder: document.querySelectorAll('#btnLesVerder').length
    };
  });
  const stap1 = await page.evaluate(() => {
    document.getElementById('btnLesVerder').click();
    return {
      stap: lesSpel.stap,
      invoer: document.querySelectorAll('#lesInput').length,
      antwoordknoppen: document.querySelectorAll('.les-o').length,
      rijtje: document.querySelectorAll('#lesRijtje').length,
      cellen: (document.getElementById('funCard').innerText.match(/\n/g) || []).length,
      tekst: document.getElementById('funCard').innerText
    };
  });

  console.log('\n-- DE KERN: de eerste twee stappen zijn geen toets --');
  ok(stap0.stap === 0 && stap0.invoer === 0 && stap0.antwoordknoppen === 0,
    'CONTROLE: stap 0 heeft geen invoerveld en geen antwoordknoppen');
  ok(/Wat doet hij|What does it do/.test(stap0.tekst) && /Waaraan zie je hem|How do you spot/.test(stap0.tekst),
    'stap 0 vertelt wat de tijd doet én waaraan je hem ziet');
  ok(stap0.verder === 1, 'en er is één weg vooruit, geen keuzestress');
  ok(stap1.stap === 1 && stap1.invoer === 0 && stap1.antwoordknoppen === 0,
    'CONTROLE: stap 1 heeft ook geen invoerveld en geen antwoordknoppen');
  ok(stap1.rijtje === 1, 'stap 1 laat het hele rijtje zien');

  // alle zes de vormen staan er in stap 1
  const rij = await page.evaluate(() => {
    const t = document.getElementById('funCard').innerText;
    const alle = conjAlleVormen(lesSpel.v, lesSpel.t);
    return { mist: alle.filter((f) => t.indexOf(f) === -1), n: alle.length };
  });
  ok(rij.mist.length === 0, 'en alle ' + rij.n + ' vormen staan erin (mist: ' + (rij.mist.join(', ') || 'niets') + ')');

  // ---- 4. DE TWEEDE KERN: nergens een vorm uit een andere tijd ----
  const lekken = await page.evaluate(() => {
    const anders = [];
    const eigen = lesSpel.t;
    function scan(waar) {
      const t = document.getElementById('funCard').innerText;
      CONJ_TIEMPOS.forEach((x) => {
        if (x.id === eigen) return;
        conjAlleVormen(lesSpel.v, x.id).forEach((f) => {
          // een vorm die toevallig in beide tijden hetzelfde is telt niet als lek
          if (conjAlleVormen(lesSpel.v, eigen).indexOf(f) !== -1) return;
          // op HELE woorden zoeken. Met indexOf vond deze check "habla" (presente) terug in
          // "hablaba" (imperfecto) en meldde een lek dat er niet was. Vals alarm in de suite,
          // niet in de app, en precies het soort meting dat je moet controleren voor je hem
          // gelooft.
          const heel = new RegExp('(^|[^a-záéíóúñü])' + f.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '([^a-záéíóúñü]|$)', 'i');
          if (heel.test(t)) anders.push(waar + ': ' + f + ' (' + x.id + ')');
        });
      });
    }
    lesStart('imperfecto'); renderFunLes(); scan('stap 0');
    document.getElementById('btnLesVerder').click(); scan('stap 1');
    document.getElementById('btnLesVerder').click(); scan('stap 2');
    // stap 2 doorlopen met goede antwoorden
    for (let i = 0; i < 8 && lesSpel.stap === 2; i++) {
      const p = lesPersoonRij(2)[lesSpel.i % lesPersoonRij(2).length];
      lesAntwoord(conjVorm(lesSpel.v, p, lesSpel.t));
      scan('stap 2 na antwoord');
      const nx = document.getElementById('btnLesNext');
      if (nx) nx.click(); else break;
    }
    const vd = document.getElementById('btnLesVerder');
    if (vd) vd.click();
    scan('stap 3');
    return { anders: anders.slice(0, 4), n: anders.length, stapNu: lesSpel.stap };
  });

  console.log('\n-- DE TWEEDE KERN: één tijd tegelijk --');
  ok(lekken.n === 0,
    'CONTROLE: nergens in de les staat een vorm uit een andere tijd (' + lekken.n +
    (lekken.anders.length ? ' — ' + lekken.anders.join(' | ') : '') + ')');
  ok(lekken.stapNu === 3, 'de les liep door tot stap 3 (nu: ' + lekken.stapNu + ')');

  // ---- 5. de tabel is er in stap 2 en 3, en wég in stap 4 ----
  const tabellen = await page.evaluate(() => {
    function doorStap() {
      for (let i = 0; i < 10; i++) {
        const rijp = lesPersoonRij(lesSpel.stap);
        const p = rijp[lesSpel.i % rijp.length];
        lesAntwoord(conjVorm(lesSpel.v, p, lesSpel.t));
        const nx = document.getElementById('btnLesNext');
        if (nx) nx.click(); else break;
        if (!document.getElementById('btnLesNext') && document.getElementById('btnLesVerder')) break;
      }
    }
    lesStart('imperfecto'); renderFunLes();
    document.getElementById('btnLesVerder').click();
    document.getElementById('btnLesVerder').click();
    const s2 = document.querySelectorAll('#funCard table').length;
    doorStap();
    let v = document.getElementById('btnLesVerder'); if (v) v.click();
    const s3 = { tabellen: document.querySelectorAll('#funCard table').length, invoer: document.querySelectorAll('#lesInput').length, stap: lesSpel.stap };
    doorStap();
    v = document.getElementById('btnLesVerder'); if (v) v.click();
    const s4 = { tabellen: document.querySelectorAll('#funCard table').length, invoer: document.querySelectorAll('#lesInput').length, stap: lesSpel.stap };
    return { s2, s3, s4, opgaven: [lesOpgaven(2), lesOpgaven(3), lesOpgaven(4)] };
  });

  console.log('\n-- de tabel verdwijnt op het juiste moment --');
  ok(tabellen.s2 >= 1, 'stap 2: de tabel staat er (kiezen mét tabel)');
  ok(tabellen.s3.stap === 3 && tabellen.s3.tabellen >= 1 && tabellen.s3.invoer === 1,
    'stap 3: tabel met een gat, en typen (stap ' + tabellen.s3.stap + ')');
  ok(tabellen.s4.stap === 4 && tabellen.s4.tabellen === 0 && tabellen.s4.invoer === 1,
    'CONTROLE: stap 4 heeft GEEN tabel meer, alleen typen (stap ' + tabellen.s4.stap + ', tabellen ' + tabellen.s4.tabellen + ')');
  ok(tabellen.opgaven[2] === 6 && tabellen.opgaven[0] === 4,
    'stap 4 doet alle zes de personen, de stappen ervoor vier (' + tabellen.opgaven.join('/') + ')');

  // ---- 6. de meting is niet te bedriegen, en de voortgang blijft ----
  const scoren = await page.evaluate(() => {
    lesStart('imperfecto'); lesSpel.stap = 4; lesSpel.i = 0; lesSpel.goed = 0;
    renderFunLes();
    // fout antwoord
    lesAntwoord('zzzz');
    const naFout = { goed: lesSpel.goed, fout: lesSpel.fout };
    document.getElementById('btnLesNext').click();
    // goed antwoord, mét ontbrekend accent: dat hoort te mogen, net als in de Conjugador
    const rijp = lesPersoonRij(4);
    const p = rijp[lesSpel.i % rijp.length];
    const zonderAccent = conjVorm(lesSpel.v, p, lesSpel.t).normalize('NFD').replace(/[̀-ͯ]/g, '');
    lesAntwoord(zonderAccent);
    return { naFout, goed: lesSpel.goed, accentTelt: lesSpel.goed === 1 };
  });

  console.log('\n-- de meting --');
  ok(scoren.naFout.goed === 0 && scoren.naFout.fout === 1, 'CONTROLE: een fout antwoord telt als fout');
  ok(scoren.accentTelt === true, 'een ontbrekend accent telt als goed, net als in de Conjugador');

  const bewaard = await page.evaluate(() => {
    S.brok = {};
    lesStart('imperfecto'); lesSpel.stap = 2; lesStapAf();
    lesStart('imperfecto'); lesSpel.stap = 1; lesStapAf();   // terugval mag de stand niet verlagen
    return { st: S.brok['les.imperfecto'], klaar: lesKlaar('imperfecto'), gram: Object.keys(S.gram || {}).length };
  });

  console.log('\n-- de voortgang --');
  ok(bewaard.st && bewaard.st.stapMax === 2,
    'de hoogst bereikte stap wordt bewaard en gaat niet omlaag (nu: ' + (bewaard.st && bewaard.st.stapMax) + ')');
  ok(bewaard.klaar === false, 'en de les heet pas klaar bij de laatste stap');
  ok(bewaard.gram === 0, 'niets in S.gram: geen koppeling aan de SRS tot de les zich bewezen heeft');

  // ---- 8. v23.118: DE OVERDRACHT ----
  //
  // Wie alleen hablar kan, kent een woord en geen patroon. Deze stap controleert dat, en de twee
  // checks die ertoe doen zijn: de werkwoorden zijn ONGEZIEN, en ze zijn REGELMATIG. Zonder dat
  // tweede meet de stap patroon en uitzondering tegelijk, en dat is precies de fout waar deze hele
  // verbouwing over gaat.
  const over = await page.evaluate(() => {
    lesStart('imperfecto');
    const stap = LES_STAPPEN.findIndex((x) => x.id === 'overdracht');
    lesSpel.stap = stap; lesSpel.i = 0; lesSpel.over = null;
    renderFunLes();
    const rij = lesOverNu();
    return {
      stap,
      n: rij.length,
      personen: rij.map((x) => x.p).sort().join(','),
      lesVerb: lesSpel.v.inf,
      bevatLesVerb: rij.some((x) => x.v.inf === lesSpel.v.inf),
      onregelmatig: rij.filter((x) => !conjRegelmatigIn(x.v, lesSpel.t)).map((x) => x.v.inf),
      andereGroep: rij.filter((x) => conjGroep(x.v) !== conjGroep(lesSpel.v)).map((x) => x.v.inf),
      opScherm: document.getElementById('funCard').innerText,
      invoer: document.querySelectorAll('#lesInput').length,
      tabellen: document.querySelectorAll('#funCard table').length,
      getoond: (document.getElementById('lesOverInf') || {}).innerText || ''
    };
  });

  console.log('\n-- DE OVERDRACHT --');
  ok(over.n === 6, 'zes opgaven (nu: ' + over.n + ')');
  ok(over.personen === '0,1,2,3,4,5', 'alle zes de personen komen langs (nu: ' + over.personen + ')');
  ok(over.bevatLesVerb === false,
    'CONTROLE: het leswerkwoord (' + over.lesVerb + ') zit er NIET tussen, anders is het geen overdracht');
  ok(over.onregelmatig.length === 0,
    'CONTROLE: alleen regelmatige werkwoorden, anders meet deze stap patroon én uitzondering tegelijk (fout: ' +
    (over.onregelmatig.join(', ') || 'niets') + ')');
  ok(over.andereGroep.length === 0,
    'CONTROLE: dezelfde groep, want -ar naar -er is een andere sprong (fout: ' + (over.andereGroep.join(', ') || 'niets') + ')');
  ok(over.tabellen === 0 && over.invoer === 1, 'geen tabel, wel typen');
  ok(over.getoond.length > 0 && over.opScherm.indexOf(over.getoond.split(' ')[0]) !== -1,
    'het werkwoord staat op het scherm ("' + over.getoond + '")');

  // de nakijker kijkt het JUISTE werkwoord na, niet het leswerkwoord
  const nakijken = await page.evaluate(() => {
    lesStart('imperfecto');
    lesSpel.stap = LES_STAPPEN.findIndex((x) => x.id === 'overdracht');
    lesSpel.i = 0; lesSpel.over = null; renderFunLes();
    const q = lesOpgaveNu();
    const juist = conjVorm(q.v, q.p, lesSpel.t);
    const vanLesVerb = conjVorm(lesSpel.v, q.p, lesSpel.t);
    lesAntwoord(vanLesVerb);            // het antwoord van het LESwerkwoord: hoort fout te zijn
    const naLes = {goed: lesSpel.goed, fout: lesSpel.fout};
    lesSpel.gekozen = null; lesSpel.goed = 0; lesSpel.fout = 0;
    lesAntwoord(juist);                 // het antwoord van het GETOONDE werkwoord: hoort goed
    return {naLes, goed: lesSpel.goed, verschillend: juist !== vanLesVerb, juist, vanLesVerb};
  });

  ok(nakijken.verschillend === true,
    'de vormen verschillen echt (' + nakijken.vanLesVerb + ' tegenover ' + nakijken.juist + ')');
  ok(nakijken.naLes.fout === 1 && nakijken.naLes.goed === 0,
    'CONTROLE: het antwoord van het leswerkwoord invullen is FOUT');
  ok(nakijken.goed === 1, 'en het antwoord van het getoonde werkwoord is goed');

  // en de les heet pas af na deze stap
  const afNa = await page.evaluate(() => {
    S.brok = {};
    const laatste = LES_STAPPEN.length - 1;
    lesStart('imperfecto'); lesSpel.stap = laatste - 1; lesStapAf();
    const voor = lesKlaar('imperfecto');
    lesStart('imperfecto'); lesSpel.stap = laatste; lesStapAf();
    return { voor, na: lesKlaar('imperfecto') };
  });
  ok(afNa.voor === false && afNa.na === true,
    'CONTROLE: de les heet pas af NA de overdrachtsstap');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
