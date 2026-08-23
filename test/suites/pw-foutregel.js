// pw-foutregel.js (14 aug, v23.101) — wijst een fout naar de regel erachter?
//
// WAAROM DIT ER IS
//
// Stefan, 14 augustus: "dit foutje es está die maak ik vaker, wordt dat inhoudelijk goed gelogd?"
// Het antwoord was nee. De fout ging naar S.errors op de zín, dus de app wist dat zin s142 fout was
// en niet dat ser en estar door elkaar liepen. Een strafregister, geen diagnose.
//
// bestDiff() wist het al: die weet precies dat er "es" hoorde te staan en dat jij "está" schreef.
// Dat paar ging nergens heen. Nu gaat het langs FOUT_REGEL, en bij een treffer noteert de app de
// fout op het grammatica-onderwerp (gramBij), zet er een zin onder die zegt welke regel het is, en
// een knop die rechtstreeks de microles opent.
//
// DE CONTROLEGEVALLEN
//
// Dit is een meting die op twee manieren triviaal groen wordt: een tabel die overal iets in ziet, en
// een tabel die nooit iets ziet. Allebei kapot, allebei groen als je alleen de treffers telt.
// Daarom staan er drie tegenproeven in:
//
//   - "mesa" tegenover "silla" is een woordje dat je niet kende. Daar hoort de app te zwijgen.
//   - een goed antwoord levert geen regel op.
//   - en zet ook geen enkel onderwerp op fout. Dat laatste is de duurste fout die deze verandering
//     zou kunnen maken: een concept naar doos 0 duwen op grond van een goede beurt.
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
  // v19.48: nieuwe bezoekers krijgen eerst de proeverij; die slaan we hier over. Daarna een echt
  // profiel, want show('vertalen') loopt via lessonProgress() en die heeft een track nodig.
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"]', 'PwFoutregel' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. de tabel zelf: welk paar wijst naar welk onderwerp? ----
  const t = await page.evaluate(() => {
    // Een nepzin met een verwacht antwoord, en daarnaast wat de leerling typte. Precies de weg die
    // checkSentence() aflegt, alleen zonder scherm.
    const regel = (es, getypt) => {
      const r = foutRegel(bestDiff(getypt, { es: es, alt: [] }));
      return r ? r.cid : null;
    };
    return {
      serestar: regel('Mi hermana es alta', 'mi hermana está alta'),
      hayestar: regel('Hay un problema', 'está un problema'),
      porpara: regel('Es un regalo para ti', 'es un regalo por ti'),
      indefimperf: regel('Ayer fue difícil', 'ayer era difícil'),
      genero: regel('El agua está fría', 'la agua está fría'),
      pronombre: regel('Lo veo cada día', 'le veo cada día'),
      muymucho: regel('Trabajo mucho', 'trabajo muy'),
      gustar: regel('Me gustan los libros', 'me gusta los libros'),
      negacion: regel('No sé nada', 'no sé algo'),
      // de tegenproef: geen regel, gewoon een woord dat je niet kende
      woordje: regel('La mesa es grande', 'la silla es grande'),
      // en een goed antwoord heeft geen afwijkend woord, dus ook geen paren
      goed: regel('La mesa es grande', 'la mesa es grande'),
      // hoeveel onderwerpen dekt de tabel, en bestaan ze allemaal?
      dekking: FOUT_REGEL.length,
      alleBestaan: FOUT_REGEL.every((r) => !!gcConcept(r.cid)),
      // accentfouten horen hier nooit te komen: bestDiff vergelijkt zonder accenten
      accent: regel('Mi hermana está alta', 'mi hermana esta alta')
    };
  });

  console.log('\n-- een verkeerde keuze krijgt een naam --');
  ok(t.serestar === 'serestar', 'es tegenover está is ser-of-estar (nu: ' + t.serestar + ')');
  ok(t.hayestar === 'hayestar', 'hay tegenover está is hay-of-está, en niet ser-of-estar (nu: ' + t.hayestar + ')');
  ok(t.porpara === 'porpara', 'por tegenover para (nu: ' + t.porpara + ')');
  ok(t.indefimperf === 'indefimperf', 'fue tegenover era is indefinido-of-imperfecto (nu: ' + t.indefimperf + ')');
  ok(t.genero === 'genero', 'el tegenover la is het lidwoord (nu: ' + t.genero + ')');
  ok(t.pronombre === 'pronombre', 'lo tegenover le is het voornaamwoord, niet het lidwoord (nu: ' + t.pronombre + ')');
  ok(t.muymucho === 'muymucho', 'muy tegenover mucho (nu: ' + t.muymucho + ')');
  ok(t.gustar === 'gustar', 'gusta tegenover gustan (nu: ' + t.gustar + ')');
  ok(t.negacion === 'negacion', 'nada tegenover algo (nu: ' + t.negacion + ')');
  ok(t.alleBestaan === true, 'elk onderwerp in FOUT_REGEL bestaat ook echt in GC_CONCEPTEN');
  ok(t.dekking >= 15, 'de tabel dekt minstens 15 onderwerpen (nu: ' + t.dekking + ')');

  console.log('\n-- en zwijgt als het geen regel is --');
  ok(t.woordje === null, 'CONTROLE: mesa tegenover silla is een woordje, geen regel (nu: ' + t.woordje + ')');
  ok(t.goed === null, 'CONTROLE: een goed antwoord levert geen regel op (nu: ' + t.goed + ')');
  ok(t.accent === null, 'een missend accent is geen keuze en komt hier niet langs (nu: ' + t.accent + ')');

  // ---- 2. en het gebeurt ook echt, via de gewone weg door checkSentence() ----
  await page.evaluate(() => show('vertalen'));
  await page.waitForTimeout(300);
  const r = await page.evaluate(() => {
    // Zelfde patroon als pw-jaartallen: rechtstreeks sIdx zetten en typen.
    const s = SENTENCES.filter((x) => /\bes\b/.test(x.es))[0];
    const uit = { es: s && s.es };
    S.gram = {};
    sIdx = s;
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.zin = 'moeilijk';
    renderSentenceBody();
    // vervang alleen het losse woord "es" door "está", zodat de rest van de zin klopt
    document.getElementById('sInput').value = s.es.replace(/\bes\b/, 'está');
    checkSentence();
    uit.getypt = s.es.replace(/\bes\b/, 'está');
    uit.gram = JSON.parse(JSON.stringify(S.gram));
    uit.knop = !!document.getElementById('btnFoutRegel');
    uit.zegtRegel = /Ser of estar|Ser or estar/.test(document.getElementById('sFeedback').innerText || '');

    // tegenproef: dezelfde zin goed getypt zet niets op fout
    S.gram = {};
    sIdx = s;
    renderSentenceBody();
    document.getElementById('sInput').value = s.es;
    checkSentence();
    uit.gramNaGoed = JSON.parse(JSON.stringify(S.gram));
    uit.knopNaGoed = !!document.getElementById('btnFoutRegel');
    return uit;
  });

  console.log('\n-- de weg door de app, niet alleen de tabel --');
  ok(!!(r.gram && r.gram.serestar && r.gram.serestar.fout === 1),
    'een echte fout in een zin ("' + r.getypt + '") noteert een fout op serestar');
  ok(!!(r.gram && r.gram.serestar && (r.gram.serestar.box || 0) === 0),
    'en zet dat onderwerp op doos 0, dus het komt morgen terug');
  ok(r.knop === true, 'er staat een knop onder je antwoord die de microles opent');
  ok(r.zegtRegel === true, 'en er staat bij welke regel het is, niet alleen dat het fout was');

  console.log('\n-- de tegenproef --');
  ok(Object.keys(r.gramNaGoed || {}).length === 0,
    'CONTROLE: een goed antwoord zet geen enkel onderwerp op fout (nu: ' +
      JSON.stringify(r.gramNaGoed) + ')');
  ok(r.knopNaGoed === false, 'CONTROLE: en er staat geen oefenknop onder een goed antwoord');

  // ---- 3. punt 23: de knop brengt je ook echt in de microles, niet in een overzicht ----
  // Een knop die naar een lijst met kaartjes gaat, is geen antwoord op "waar vind ik het toetsje".
  // Dan moet je alsnog zoeken welk kaartje het was, en dan ben je de fout al vergeten.
  await page.evaluate(() => {
    const s = SENTENCES.filter((x) => /\bes\b/.test(x.es))[0];
    sIdx = s;
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.zin = 'moeilijk';
    renderSentenceBody();
    document.getElementById('sInput').value = s.es.replace(/\bes\b/, 'está');
    checkSentence();
  });
  await page.waitForTimeout(200);
  /* v23.180: de knop staat sinds vandaag achter "meer opties", want er stonden er zes op één scherm
     met twee primaire kleuren. Hij is niet weg, alleen een tik verder, dus deze suite doet die tik
     ook. Dat de knop dáár staat en niet vooraan is de claim van pw-knoppen; hier gaat het er alleen
     om dat hij nog wérkt. */
  const meer = page.locator('#tab-vertalen details.meerOpties summary');
  if (await meer.count()) await meer.first().click();
  await page.waitForTimeout(150);
  await page.click('#btnFoutRegel');
  await page.waitForTimeout(500);
  const na = await page.evaluate(() => ({
    sess: gwSess && gwSess.id,
    tekst: (document.body.innerText || '').replace(/\s+/g, ' ')
  }));

  console.log('\n-- en de knop brengt je in de les, niet in een overzicht --');
  ok(na.sess === 'concept-serestar', 'de knop opent de microles van serestar (nu: ' + na.sess + ')');
  ok(/Ser of estar|Ser or estar/i.test(na.tekst), 'en het onderwerp staat op het scherm');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
