// pw-stem.js (22 aug, v23.166) — heeft elke luisteroefening ook echt een stem, en zoekt hij hem
// waar hij ligt?
//
// WAAROM DIT ER IS
//
// Stefan, 21 aug: "en de luisteroefeningen, de elevenlabs geluid is nog niet gemaakt."
//
// Dat klopte, en het is mijn eigen gat. In v23.157 heb ik zes luisterscenes toegevoegd en er een
// suite bij gezet (pw-nieuwestof) die elk veld nakijkt: regels, sprekers, drie vragen, Engelse
// vertaling, een geldig antwoord, een bereikbare drempel. Alles behalve het enige dat een
// luisteroefening tot een luisteroefening maakt. Zonder mp3 is het een leesoefening met extra
// stappen, en dat merkte niets.
//
// Gemeten toen het gemeld werd: 21 scenes, 15 compleet ingesproken, 6 helemaal leeg (precies de
// zes nieuwe), 0 half. De pijplijn zelf mankeerde niets: tools/avondrun-audio.js spreekt dialogo-a
// en dialogo-b elke nacht in, en de zes stonden er pas na de run van 03:01. Ze hadden nog geen
// beurt gehad.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. ELKE SCENE IS ZICHTBAAR VOOR HET INSPREEKSCRIPT. Dit is de fout die eeuwig duurt: een scene
//      in een vorm die tools/audio-lib.js niet leest, krijgt nooit een stem en niets zegt het. Een
//      scene zonder opname wordt vannacht ingesproken; een scene die de lijst niet haalt, nooit.
//   2. GEEN HALF INGESPROKEN SCENE. Helemaal leeg is normaal (hij wacht op de nachtrun); half is
//      dat nooit, want het script doet een scene in één keer. Half is een gesprek dat halverwege
//      stilvalt, en dat is erger dan een gesprek dat helemaal niet begint.
//   3. EN ALS ER GEEN GELUID IS, ZEGT DE APP DAT. Het controlegeval, en het is de reden dat punt 2
//      geen ramp is: bij een ontbrekend bestand schakelt de oefening over op tekst, zegt erbij dat
//      hij niet meetelt voor luisteren, en telt dan ook echt niet mee. Zonder die eerlijkheid zou
//      ontbrekend geluid als luisterbewijs de statistiek in lopen.
//
// 22 AUGUSTUS: HETZELFDE VOOR HET LEESBOEK, EN DAAR ZAT AL EEN VERSCHIL
//
// Stefan, 22 aug: "check ook dat het goed gaat, dan doet de voorspelling het maar ook de audio bijv
// bij het leesboek." Gemeten: audio/boek/ had dertien bestanden, precies de dertien Chispa-
// hoofdstukken, en de acht hoofdstukken van Un año en Cádiz stonden er sinds v23.157 zonder één
// opname. Dezelfde vorm als de zes luisterscenes hierboven: het inspreekscript voor het boek was
// handwerk en niemand draaide het. Sinds v23.166 doet de nachtrun het boek mee.
//
// Bij het aanzetten bleek er iets anders. Drie plekken schreven los van elkaar op in welke map de
// opname van een hoofdstuk hoort (boekSpreek() in de app, groepVan() in generate-boek-audio.js, de
// filterregel in de nachtrun) en ze waren het niet eens: de app zocht de recepten in audio/receta/,
// de generator schreef ze in audio/boek/, en een receta-stem bestond niet. Het deed niets omdat de
// recepten stem:false hebben en dus geen luisterknop, maar zonder deze suite zou de nachtrun zes
// recepten hebben ingesproken (4.850 tekens) in een map waar de app nooit kijkt.
//
//   4. ELK HOOFDSTUK HOORT BIJ EEN REEKS. Anders staat het ook op geen plank in de app, en dan is
//      ontbrekend geluid het kleinste van twee problemen (v23.162: acht hoofdstukken in BOOK die
//      nergens te vinden waren).
//   5. WAAR DE APP HET BESTAND ZOEKT, IS WAAR HET SCRIPT HET NEERZET. Dit is de meting die het
//      receta-verschil zou hebben gevangen, en hij gaat door de voordeur: de suite opent elk
//      hoofdstuk in de app en vangt op welke URL boekSpreek() opvraagt. Niet wat de plank belooft,
//      maar wat de knop doet.
//   6. GEEN VERTELLER, GEEN KNOP, GEEN OPNAME. Het controlegeval van deze helft: bij de recepten
//      staat er geen luisterknop, en dan hoort het inspreekscript ze ook niet op de lijst te
//      hebben. Een van de twee zonder de ander is precies het gat dat hier zat.
//
// WAT DEZE SUITE NIET DOET
//
// Rood worden omdat verse content nog geen opname heeft. Dat is de normale toestand tussen het
// schrijven van een scene en de nachtrun erna, en een poort die daarop dichtgaat blokkeert precies
// de run die het zou repareren. De achterstand wordt geteld en genoemd, niet afgekeurd.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const WORTEL = path.resolve(__dirname, '..', '..');
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwSt' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // Wat de APP kent: elke regel van elke scene, met zijn spreker. Dit is de waarheid waar het
  // inspreekscript langs gelegd wordt, en niet andersom.
  const scenes = await page.evaluate(() => AUDICIONES.map(function (s) {
    return { id: s.id, regels: s.lineas.map(function (l, i) { return { n: i + 1, v: l.v, es: l.es }; }) };
  }));

  // ---- 1. is elke regel zichtbaar voor het inspreekscript? ----
  const lib = require(path.join(WORTEL, 'tools', 'audio-lib.js'));
  const per = lib.leesDialogos();
  const gezien = {};
  ['dialogo-a', 'dialogo-b'].forEach(function (g) {
    (per[g] || []).forEach(function (x) { gezien[x.id] = g; });
  });

  const onzichtbaar = [];
  const verkeerdeStem = [];
  scenes.forEach(function (s) {
    s.regels.forEach(function (r) {
      const id = s.id + '-' + r.n;
      const hoort = 'dialogo-' + r.v;
      if (!gezien[id]) { onzichtbaar.push(id); return; }
      if (gezien[id] !== hoort) verkeerdeStem.push(id + ' (' + gezien[id] + ', hoort bij ' + hoort + ')');
    });
  });

  console.log('\n-- 1. elke scene is zichtbaar voor het inspreekscript --');
  const regelsTotaal = scenes.reduce(function (a, s) { return a + s.regels.length; }, 0);
  console.log('   ' + scenes.length + ' scenes, ' + regelsTotaal + ' regels');
  ok(onzichtbaar.length === 0,
    'elke regel staat op de lijst die vannacht wordt ingesproken (' + (onzichtbaar.slice(0, 6).join(', ') || 'alle') + ')');
  ok(verkeerdeStem.length === 0,
    'en bij de stem van zijn eigen spreker (' + (verkeerdeStem.slice(0, 4).join(', ') || 'alle') + ')');

  // ---- 2. geen half ingesproken scene ----
  const stand = scenes.map(function (s) {
    const er = s.regels.filter(function (r) {
      return fs.existsSync(path.join(WORTEL, 'audio', 'dialogo-' + r.v, s.id + '-' + r.n + '.mp3'));
    }).length;
    return { id: s.id, er: er, van: s.regels.length };
  });
  const compleet = stand.filter(function (x) { return x.er === x.van; });
  const leeg = stand.filter(function (x) { return x.er === 0; });
  const half = stand.filter(function (x) { return x.er > 0 && x.er < x.van; });

  console.log('\n-- 2. geen half ingesproken scene --');
  console.log('   ' + compleet.length + ' compleet · ' + leeg.length + ' wachten op de nachtrun · ' + half.length + ' half');
  if (leeg.length) console.log('   nog geen opname: ' + leeg.map(function (x) { return x.id; }).join(', '));
  ok(half.length === 0,
    'geen enkele scene valt halverwege stil (' + (half.map(function (x) { return x.id + ' ' + x.er + '/' + x.van; }).join(', ') || 'geen') + ')');
  // informatief, geen oordeel: verse content zonder opname is de normale toestand vóór de nachtrun
  ok(compleet.length > 0, 'er zijn ingesproken scenes (' + compleet.length + ' van ' + scenes.length + ')');

  // ---- 3. en als er geen geluid is, zegt de app dat ----
  const eerlijk = await page.evaluate(() => {
    const uit = {};
    S.lang = 'nl';
    const sc = AUDICIONES[0];
    audSc = sc; audStap = 0; audGoed = 0; audGehoord = 1; audAnt = []; audGeenAudio = false;
    audMenu = false; funView = 'audi';
    show('speeltuin', true); renderFun();
    uit.metGeluid = {
      speelKnop: !!document.getElementById('btnAudSpeel'),
      melding: /telt niet mee voor luisteren/.test(document.getElementById('funCard').textContent)
    };
    // nu alsof het bestand ontbreekt
    audGeenAudio = true;
    renderFunAudicion();
    uit.zonderGeluid = {
      speelKnop: !!document.getElementById('btnAudSpeel'),
      melding: /telt niet mee voor luisteren/.test(document.getElementById('funCard').textContent),
      // en de tekst staat er meteen: lezen is dan het enige dat overblijft
      tekstZichtbaar: document.getElementById('funCard').textContent.indexOf(sc.lineas[0].es.slice(0, 20)) !== -1
    };
    // telt het mee als luisterbewijs? de vragen goed beantwoorden, met en zonder geluid
    function rondeAf(geenAudio) {
      S.comp = null; S.audDone = {};
      audSc = sc; audStap = 0; audGoed = 0; audGehoord = 1; audAnt = []; audGeenAudio = geenAudio;
      /* audAfronden() hangt aan de knop "Naar het transcript", niet aan het laatste antwoord.
         Dus hier expliciet, anders lijkt het alsof luisterbewijs nooit wordt bijgeschreven. */
      sc.vragen.forEach(function (v, i) { audStap = i; audAntwoord(v.c); });
      audAfronden();
      try { return !!(S.comp && S.comp.luisteren && S.comp.luisteren[sc.id]); } catch (e) { return null; }
    }
    uit.teltMet = rondeAf(false);
    uit.teltZonder = rondeAf(true);
    audSc = null; funView = null;
    return uit;
  });

  console.log('\n-- 3. het controlegeval: geen geluid, en de app zegt het --');
  ok(eerlijk.metGeluid.speelKnop && !eerlijk.metGeluid.melding, 'met opname staat er een afspeelknop en geen excuus');
  ok(!eerlijk.zonderGeluid.speelKnop && eerlijk.zonderGeluid.melding, 'zonder opname staat er geen afspeelknop maar een melding');
  ok(eerlijk.zonderGeluid.tekstZichtbaar, 'en de tekst komt in beeld, want lezen is dan het enige dat overblijft');
  ok(eerlijk.teltMet === true, 'een ronde mét geluid telt als luisterbewijs');
  ok(eerlijk.teltZonder === false, 'en een ronde zonder geluid niet: gelezen is niet gehoord');

  // ---- 4 t/m 6. het leesboek ----
  const boekLib = lib.leesHoofdstukkenPerMap();

  /* Wat de APP doet als je op Luisteren drukt. Niet nagerekend maar afgekeken: Audio wordt
     vervangen door een dubbelganger die de src opschrijft en verder niets doet, en dan wordt
     boekSpreek() aangeroepen voor elk hoofdstuk. Wat er in vangst staat is dus letterlijk het
     bestand dat de app zou opvragen. Zo hoeft deze suite de voorvoegselregel niet te kennen, en
     dat is precies het punt: die regel hoort maar op één plek te staan. */
  const appKant = await page.evaluate(() => {
    const vangst = {};
    const knop = {};
    const echt = window.Audio;
    window.Audio = function (src) {
      this.src = src;
      this.play = function () { return { catch: function () {} }; };
      this.pause = function () {};
      this.addEventListener = function () {};
      vangst[window.__nu] = src;
    };
    BOOK.forEach(function (h) {
      window.__nu = h.id;
      try { boekSpreek(h); } catch (e) { vangst[h.id] = 'FOUT: ' + e.message; }
      /* En de voordeur ernaast: zet de app er een luisterknop bij? Dat is wat bepaalt of een
         opname ooit hoorbaar is. */
      try {
        startBoek(h.id);
        knop[h.id] = !!document.getElementById('btnBoekLuister');
      } catch (e) { knop[h.id] = 'FOUT'; }
    });
    window.Audio = echt;
    try { boekStop(); } catch (e) {}
    return { vangst: vangst, knop: knop, ids: BOOK.map(function (h) { return h.id; }) };
  });

  console.log('\n-- 4. elk hoofdstuk hoort bij een reeks --');
  console.log('   ' + appKant.ids.length + ' hoofdstukken · ' +
    Object.keys(boekLib.perMap).map(function (m) { return m + ': ' + boekLib.perMap[m].length; }).join(' · '));
  ok(boekLib.wees.length === 0,
    'geen hoofdstuk staat buiten de boekenplank (' + (boekLib.wees.join(', ') || 'geen') + ')');

  // waar het script het neerzet: id -> map, uit dezelfde bron die de nachtrun gebruikt
  const scriptMap = {};
  Object.keys(boekLib.perMap).forEach(function (m) {
    boekLib.perMap[m].forEach(function (h) { scriptMap[h.id] = m; });
  });

  const scheef = [];
  const zonderStem = [];
  appKant.ids.forEach(function (id) {
    const src = appKant.vangst[id] || '';
    const m = /^audio\/([^/]+)\/(.+)\.mp3$/.exec(src);
    if (!appKant.knop[id]) {
      // geen knop: dan hoort het script hem ook niet in te spreken
      if (scriptMap[id]) zonderStem.push(id + ' (geen knop, maar het script spreekt hem wel in)');
      return;
    }
    if (!m) { scheef.push(id + ' (de app vraagt niets op: "' + src + '")'); return; }
    if (m[2] !== id) { scheef.push(id + ' (de app vraagt ' + m[2] + '.mp3 op)'); return; }
    if (!scriptMap[id]) { scheef.push(id + ' (knop in de app, maar het script kent hem niet)'); return; }
    if (m[1] !== scriptMap[id]) scheef.push(id + ' (app: audio/' + m[1] + '/, script: audio/' + scriptMap[id] + '/)');
  });

  console.log('\n-- 5. de app zoekt waar het script neerzet --');
  const metKnop = appKant.ids.filter(function (id) { return appKant.knop[id]; });
  console.log('   ' + metKnop.length + ' hoofdstukken met een luisterknop, ' +
    (appKant.ids.length - metKnop.length) + ' zonder');
  ok(scheef.length === 0, 'elk hoofdstuk met een knop wordt gezocht waar het wordt neergezet (' +
    (scheef.slice(0, 4).join('; ') || 'alle') + ')');

  console.log('\n-- 6. het controlegeval: geen verteller, geen knop, geen opname --');
  const stil = appKant.ids.filter(function (id) { return !appKant.knop[id]; });
  console.log('   zonder knop: ' + (stil.join(', ') || 'geen'));
  /* v23.220: hier stond ok(stil.length > 0). Dat hield stand zolang er toevallig een reeks zonder
     verteller op de plank stond, en dat was La cocina española (stem:false). Die is er op Stefans
     verzoek af, en toen viel deze proef om terwijl er niets kapot was.

     Een controlegeval dat afhangt van wat er toevallig in de data staat, is geen controlegeval: het
     verdwijnt zodra iemand die data opruimt, en dan lijkt het net of de regel niet meer geldt. Dus
     bouwen we het geval nu zelf, net als bij morgenBijzonderZin() in pw-morgen (v23.218). */
  const verzonnen = await page.evaluate(() => {
    const reeks = { id: 'proefstil', pre: 'stil-', nl: 'Proef', en: 'Test', stem: false,
                    soortNl: 'proef', soortEn: 'test', omNl: '', omEn: '' };
    const hfd = { id: 'stil-1', num: 1, deel: 'Proef', titel: 'Zonder stem', drempel: 0,
                  tekst: 'Una frase de prueba.', vragen: [], reflectie: '' };
    LEES_REEKSEN.push(reeks);
    BOOK.push(hfd);
    let knop = null;
    try { show('lezen', true); startBoek('stil-1'); knop = !!document.getElementById('btnBoekLuister'); }
    catch (e) { knop = 'FOUT: ' + e.message; }
    /* en meteen weer weg: een proef die de app achterlaat met verzonnen data is een proef die de
       volgende proef laat omvallen */
    LEES_REEKSEN.pop();
    BOOK.pop();
    return { knop: knop, reeksenNa: LEES_REEKSEN.length, boekNa: BOOK.length };
  });
  console.log('   verzonnen reeks zonder verteller: knop = ' + verzonnen.knop);
  ok(verzonnen.knop === false,
    'een reeks zonder verteller krijgt geen luisterknop, ook al staat het hoofdstuk er wel');
  ok(stil.length === 0,
    'CONTROLE: en op de echte plank heeft elke reeks er een, dus er is niets stilzwijgend stil (' +
    (stil.join(', ') || 'alle drie') + ')');
  ok(zonderStem.length === 0,
    'en die staat ook niet op de lijst van de nachtrun (' + (zonderStem.join(', ') || 'geen') + ')');

  // hoeveel van het boek wacht nog op een nachtrun? informatief, net als bij de scenes hierboven
  const boekMist = [];
  Object.keys(boekLib.perMap).forEach(function (m) {
    boekLib.perMap[m].forEach(function (h) {
      if (!fs.existsSync(path.join(WORTEL, 'audio', m, h.id + '.mp3'))) boekMist.push(h.id);
    });
  });
  console.log('   nog geen opname: ' + (boekMist.join(', ') || 'geen, alles is ingesproken'));

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
