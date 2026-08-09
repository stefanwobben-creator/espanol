// v20.3: de peiling en de balk als bevestiging.
//
// Stefan, 5 augustus: "ik moet het gevoel hebben dat ik echt een stap heb gemaakt met Spaans en de
// voortgangsbalk moet een soort bevestiging zijn zo van dit klopt idd ongeveer met het niveau
// waarvan ikzelf denk dat ik ben."
//
// De balk telde alleen wat je hier had vastgezet, dus alles wat je al kende telde als nul. Wat
// deze suite vastlegt:
//   - de peiling is een meting en geen les: geen XP, geen doosjes, niets in S.srs.
//   - elke Cervantes-sleutel wordt hoogstens een keer gepeild, anders meet je jezelf dubbel.
//   - de schatting rekent zoals ze zegt te rekenen: census op wat bewezen is, steekproef op de
//     rest, gokcorrectie r - f/3, en een Wilson-band eromheen. Vier gevallen worden op de cent
//     nagerekend, want een balk die verkeerd rekent is erger dan geen balk.
//   - onder de twintig antwoorden geen schatting. Een percentage uit vier woorden is een gok.
//   - alleen niveaus waarvan de app genoeg materiaal heeft: A1 wel, A2 niet.
//   - het niveau in de balk komt niet uit je eigen claim. Een balk die op jouw eigen verklaring
//     rust kan nooit een bevestiging zijn.
//   - de stap staat in dezelfde balk (streepje plus zin), niet in een nieuw blok. Dat is de regel
//     van v20.1 en die blijft staan.
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

async function dagOpnieuw(page) {
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(350);
}

// de basisregel zoals hij op het dagscherm staat
async function basis(page) {
  return page.evaluate(() => {
    const balk = document.getElementById('dagBasisBalk');
    const kaart = balk ? balk.closest('.card') : null;
    const knop = document.getElementById('btnPeilStart');
    return {
      balk: !!balk,
      kop: balk ? (balk.querySelector('b') || {}).innerText || '' : '',
      lagen: balk ? balk.querySelectorAll('.bar > div').length : -1,
      merk: balk ? balk.querySelectorAll('.bar .merk').length : -1,
      knop: !!knop,
      knopTekst: knop ? knop.innerText.replace(/\s+/g, ' ').trim() : '',
      knopKaart: knop && knop.closest('.card') ? (knop.closest('.card').id || '') : '',
      tekst: kaart ? kaart.innerText.replace(/\s+/g, ' ') : ''
    };
  });
}

// items rechtstreeks neerzetten, zodat we de rekensom op de cent kunnen nakijken
async function zetItems(page, goed, mis, geen) {
  return page.evaluate(([g, m, x]) => {
    S.peil.items = {};
    const app = pcicKeysApp()['A1'], dk = dekKeysNu();
    const ks = Object.keys(app).filter(k => !dk.vast[k]);
    let i = 0;
    for (let n = 0; n < g; n++) S.peil.items[ks[i++]] = { r: 1, d: today(), niv: 'A1' };
    for (let n = 0; n < m; n++) S.peil.items[ks[i++]] = { r: 0, d: today(), niv: 'A1' };
    for (let n = 0; n < x; n++) S.peil.items[ks[i++]] = { r: -1, d: today(), niv: 'A1' };
    try { persist(); } catch (e) {}
    const s = niveauSchatting('A1');
    return s ? JSON.parse(JSON.stringify(s)) : null;
  }, [goed, mis, geen]);
}

async function beantwoord(page, aantal) {
  for (let i = 0; i < aantal; i++) {
    const er = await page.$('#peilOpties button');
    if (!er) break;
    await er.click();
    await page.waitForTimeout(1000);
  }
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 360, height: 780 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await nieuwProfiel(page);

  console.log('\n-- versie --');
  const versie = await page.evaluate(() => APP_VERSIE);
  ok(minstens(versie, 'v20.3'), 'versie is minstens v20.3 (nu ' + versie + ')');

  console.log('\n-- wat de app kan nameten, en wat niet --');
  const dek = await page.evaluate(() => {
    const app = pcicKeysApp();
    const uit = {};
    ['A1', 'A2', 'B1'].forEach(n => {
      uit[n] = { keys: Object.keys(app[n] || {}).length, noem: PCIC_NOEMER[n], meetbaar: peilMeetbaar(n) };
    });
    return uit;
  });
  // De steekproef wordt getrokken uit de sleutels die de app in huis heeft, maar de uitspraak gaat
  // over de hele noemer. Dat mag alleen als het gat klein is: onder de 80 procent dekking zwijgt de
  // app (PEIL_DEKKING). Deze regel bewaakt dat het gat niet stilletjes groter wordt.
  ok(dek.A1.keys / dek.A1.noem >= 0.9, 'de app heeft minstens 90 procent van de ' + dek.A1.noem + ' A1-sleutels in huis (' + dek.A1.keys + ')');
  ok(dek.A1.meetbaar === true, 'A1 is dus meetbaar');
  ok(dek.A2.meetbaar === false, 'A2 niet: ' + dek.A2.keys + ' van ' + dek.A2.noem + ' sleutels');
  ok(await page.evaluate(() => niveauSchatting('A2') === null), 'en over A2 doet de app dan ook geen uitspraak');

  console.log('\n-- de rekensom, op de cent --');
  /* v23.15: deze vier getallen stonden hier als 390, 130 en 260. Dat waren geen losse waarden maar
     de noemer en twee breuken daarvan, en de noemer is 409 geworden. Ze worden nu uitgerekend uit
     PCIC_NOEMER, zodat de suite de rekensom bewaakt en niet de stand van de teller. */
  const noem = await page.evaluate(() => PCIC_NOEMER.A1);
  const alles = await zetItems(page, 30, 0, 0);
  ok(alles && alles.punt === noem, 'dertig keer goed op een leeg profiel: schatting ' + noem + ' (' + (alles && alles.punt) + ')');
  ok(alles && alles.onder < noem && alles.onder > noem * 0.8, 'met een ondergrens eronder, geen zekerheid (' + (alles && alles.onder) + ')');
  ok(alles && alles.boven === noem, 'en een bovengrens op de noemer (' + (alles && alles.boven) + ')');

  const niets = await zetItems(page, 0, 30, 0);
  ok(niets && niets.punt === 0, 'dertig keer fout: schatting 0 (' + (niets && niets.punt) + ')');

  const half = await zetItems(page, 15, 15, 0);
  ok(half && half.punt === Math.round(noem / 3), 'vijftien goed en vijftien fout is na gokcorrectie een derde: ' + Math.round(noem / 3) + ' (' + (half && half.punt) + ')');

  const geen = await zetItems(page, 20, 0, 10);
  ok(geen && geen.punt === Math.round(noem * 2 / 3), '"geen idee" telt als niet gekend maar niet als gokfout: ' + Math.round(noem * 2 / 3) + ' (' + (geen && geen.punt) + ')');

  console.log('\n-- onder de twintig antwoorden zwijgt de balk --');
  const weinig = await zetItems(page, 19, 0, 0);
  ok(weinig === null, 'negentien antwoorden geven geen schatting');
  const netaan = await zetItems(page, 20, 0, 0);
  ok(netaan !== null && netaan.n === 20, 'twintig wel (n = ' + (netaan && netaan.n) + ')');

  console.log('\n-- de balk staat niet op je eigen claim --');
  await page.evaluate(() => { S.peil.items = {}; S.peil.log = []; S.peil.laatst = ''; niveauClaim(0); });
  const nivs = await page.evaluate(() => ({ dag: dagNiveau(), balk: balkNiveau() }));
  ok(nivs.balk === 'A1', 'balkNiveau() blijft A1 zolang A1 niet bewezen is (' + nivs.balk + ')');

  /* v23.3: en andersom. Zegt de peiling dat A1 al vol zit, dan hoort de balk door te schuiven naar
     A2, ook als A2 zelf nog niet peilbaar is. Dat was de bug: peilNiveau() sloeg een niet-peilbaar
     niveau over en viel terug op dagNiveau(), en die kijkt alleen naar wat hier bewezen is. Gevolg:
     een peiling die zei "A1 ken je al" liet de balk gewoon op A1 staan. */
  const doorgeschoven = await page.evaluate(() => {
    const app = pcicKeysApp()['A1'];
    const ks = Object.keys(app);
    S.peil.items = {};
    for (let i = 0; i < 40; i++) S.peil.items[ks[i]] = { r: 1, d: today(), niv: 'A1' };
    return { af: peilAf('A1'), balk: balkNiveau() };
  });
  ok(doorgeschoven.af === true, 'een peiling die A1 volmaakt, sluit A1 af');
  ok(doorgeschoven.balk === 'A2', 'en dan staat de balk op A2, ook al is A2 nog niet peilbaar (' + doorgeschoven.balk + ')');
  await page.evaluate(() => { S.peil.items = {}; S.peil.log = []; S.peil.laatst = ''; });
  ok(nivs.dag === 'A2', 'terwijl dagNiveau() de claim wel volgt (' + nivs.dag + '), dus dit is echt een ander getal');
  await page.evaluate(() => { niveauClaimTerug(); });

  console.log('\n-- de peiling wordt niet op dag een gevraagd --');
  await page.evaluate(() => { S.lesFlowEerste = ''; try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  ok(await page.evaluate(() => peilAanbod() === null), 'wie nog geen les heeft afgerond krijgt geen peiling aangeboden');
  const dag1 = await basis(page);
  ok(!dag1.knop, 'en er staat dus ook geen knop op het dagscherm');

  console.log('\n-- daarna wel, en in de kaart die er al stond --');
  await page.evaluate(() => { S.lesFlowEerste = today(); try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  const aanbod = await basis(page);
  ok(aanbod.knop, 'na een afgeronde les staat het aanbod er');
  ok(/Klopt dit ongeveer/i.test(aanbod.knopTekst), 'de knop zegt waar het over gaat (' + aanbod.knopTekst + ')');
  ok(aanbod.knopKaart === 'lijnKaart', 'en hij staat in de bestaande kaart, niet in een nieuw blok (' + aanbod.knopKaart + ')');
  ok(/telt niet mee voor je punten/i.test(aanbod.tekst), 'met erbij dat het niet voor je punten telt');
  ok(!/—|–|--/.test(aanbod.tekst), 'geen streepjes in de tekst');

  console.log('\n-- een peiling is een meting, geen les --');
  const voor = await page.evaluate(() => ({ srs: Object.keys(S.srs).length, xp: (S.xp[today()] || 0), tapas: (S.tapas || 0) }));
  await page.click('#btnPeilStart');
  await page.waitForTimeout(600);
  const vraag = await page.evaluate(() => {
    const el = document.getElementById('lessonList');
    return {
      opties: document.querySelectorAll('#peilOpties button').length,
      geen: !!document.getElementById('btnPeilGeen'),
      stop: !!document.getElementById('btnPeilStop'),
      tekst: el ? el.innerText.replace(/\s+/g, ' ') : '',
      n: peilNu ? peilNu.vragen.length : 0
    };
  });
  ok(vraag.n === 12, 'de peiling is twaalf woorden lang (' + vraag.n + ')');
  ok(vraag.opties === 4, 'vier keuzes (' + vraag.opties + ')');
  ok(vraag.geen, 'plus een echte knop "geen idee"');
  ok(vraag.stop, 'en je kunt eruit stappen');
  ok(/1\/12/.test(vraag.tekst), 'je ziet waar je bent (' + vraag.tekst.slice(0, 60) + ')');

  await beantwoord(page, 12);
  const na = await page.evaluate(() => ({
    srs: Object.keys(S.srs).length, xp: (S.xp[today()] || 0), tapas: (S.tapas || 0),
    items: Object.keys(S.peil.items).length, laatst: S.peil.laatst, log: S.peil.log.length,
    tekst: (document.getElementById('lessonList') || {}).innerText || ''
  }));
  ok(na.srs === voor.srs, 'na twaalf antwoorden staat er geen woord extra in je doosjes (' + voor.srs + ' -> ' + na.srs + ')');
  ok(na.xp === voor.xp, 'en je punten zijn niet veranderd (' + voor.xp + ' -> ' + na.xp + ')');
  ok(na.tapas === voor.tapas, 'en je tapas ook niet');
  ok(na.items === 12, 'er staan twaalf antwoorden bewaard (' + na.items + ')');
  ok(na.laatst === (await page.evaluate(() => today())), 'de datum van de peiling is vastgelegd');
  ok(na.log === 0, 'nog geen uitslag in het logboek, want twaalf is te weinig voor een schatting');
  ok(/Nog 8 antwoorden/i.test(na.tekst.replace(/\s+/g, ' ')), 'het slotscherm zegt eerlijk hoeveel er nog nodig is');

  console.log('\n-- elke sleutel hoogstens een keer --');
  const dubbel = await page.evaluate(() => {
    const kand = peilKandidaten('A1'), it = S.peil.items;
    return kand.filter(k => !!it[k]).length;
  });
  ok(dubbel === 0, 'geen enkele gepeilde sleutel zit nog in de kandidaten');
  ok(await page.evaluate(() => peilAanbod() === null), 'en vandaag komt er geen tweede aanbod');

  console.log('\n-- met genoeg antwoorden wordt de balk een schatting --');
  await page.evaluate(() => {
    // vijftien antwoorden erbij van een eerdere peiling, zodat we boven de drempel komen
    const app = pcicKeysApp()['A1'], dk = dekKeysNu();
    const ks = Object.keys(app).filter(k => !dk.vast[k] && !S.peil.items[k]);
    for (let i = 0; i < 15; i++) S.peil.items[ks[i]] = { r: (i < 10 ? 1 : 0), d: today(), niv: 'A1' };
    peilNu = { niv: 'A1', i: 0, vragen: [] };
    peilKlaar();
  });
  await page.waitForTimeout(400);
  const uit = await page.evaluate(() => ({
    log: S.peil.log.length,
    eerste: S.peil.log[0] ? JSON.parse(JSON.stringify(S.peil.log[0])) : null,
    tekst: (document.getElementById('lessonList') || {}).innerText.replace(/\s+/g, ' ') || ''
  }));
  ok(uit.log === 1, 'nu staat er wel een uitslag in het logboek (' + uit.log + ')');
  ok(uit.eerste && uit.eerste.niv === 'A1' && uit.eerste.punt > 0, 'met het geschatte aantal erin (' + (uit.eerste && uit.eerste.punt) + ')');
  ok(/geschat al gekend|estimated already known/i.test(uit.tekst), 'het slotscherm toont dezelfde balk als het dagscherm');
  ok(!/—|–|--/.test(uit.tekst), 'geen streepjes op het slotscherm');

  await dagOpnieuw(page);
  const bal = await basis(page);
  ok(bal.balk, 'de balk staat op het dagscherm');
  ok(bal.lagen === 3, 'met drie lagen: bewezen, onderweg en geschat (' + bal.lagen + ')');
  ok(bal.merk === 1, 'en een streepje waar je eerste peiling stond (' + bal.merk + ')');
  const kop = parseInt(bal.kop, 10);
  const schat = await page.evaluate(() => JSON.parse(JSON.stringify(niveauSchatting('A1'))));
  /* v23.0: de kop was een percentage, en dat was precies de fout. Hetzelfde niveau stond hier op
     100% (de schatting) en op je profiel op 0% (het bewezen deel), allebei zonder te zeggen welk
     stuk ze maten. Nu staat er een aantal: wat je actief bijhoudt. De schatting is niet weg maar
     verhuisd naar de legenda, waar ze een naam heeft. Hieronder wordt dat allebei gecontroleerd. */
  const opweg = await page.evaluate(() => {
    const t = voortgangTellers();
    return Math.max((t.dekw && t.dekw.A1) || 0, (t.dek && t.dek.A1) || 0);
  });
  ok(kop === opweg, 'de kop is geen percentage meer maar wat je actief bijhoudt (' + bal.kop + ' vs ' + opweg + ')');
  ok(/geschat al gekend|estimated already known/i.test(bal.tekst), 'de schatting staat in de legenda, met een naam erbij');
  ok(/bewezen vast|proven solid/i.test(bal.tekst), 'en het bewezen deel staat er als eigen laag naast');
  /* v23.2: de zin "je kent er naar schatting X van de 390, daarvan staan er Y vast" is weg. Dat was
     hetzelfde getal als in de legenda, alleen als totaal in plaats van als restant, en daardoor leek
     de schatting twee verschillende dingen te zijn. De legenda draagt het nu alleen, dus daar wordt
     het ook gecontroleerd: de schatting min wat al in de andere lagen zit. */
  ok(!/naar schatting/i.test(bal.tekst), 'de dubbele zin met hetzelfde getal is weg');
  const rest = schat.punt - opweg;
  ok(new RegExp('\\b' + rest + '\\b').test(bal.tekst), 'de legenda noemt de schatting als restant (' + rest + ')');
  ok(/geschat al gekend|estimated already known/i.test(bal.tekst), 'met een naam erbij, zodat je ziet welk stuk het is');
  ok(!bal.knop, 'binnen veertien dagen wordt er geen nieuwe peiling gevraagd');

  console.log('\n-- de stap staat in dezelfde balk --');
  const zonder = await basis(page);
  ok(!/Sinds je eerste peiling/i.test(zonder.tekst), 'zonder verschil staat er geen stapzin: stilstand is geen bericht');
  await page.evaluate(() => {
    S.peil.log[0].punt = Math.max(0, S.peil.log[0].punt - 40);
    S.peil.log[0].d = addDays(today(), -21);
    try { persist(); } catch (e) {}
  });
  await dagOpnieuw(page);
  const met = await basis(page);
  ok(/Sinds je eerste peiling/i.test(met.tekst), 'is er wel verschil, dan staat de stap er (' + met.tekst.slice(0, 120) + ')');
  ok(/ging de schatting van/i.test(met.tekst), 'met beide getallen erin, zodat het na te rekenen is');
  ok(met.merk === 1, 'en het streepje verschuift mee naar het beginpunt');
  ok(!/—|–|--/.test(met.tekst), 'nog steeds geen streepjes in de tekst');

  console.log('\n-- na veertien dagen mag het opnieuw --');
  await page.evaluate(() => { S.peil.laatst = addDays(today(), -15); try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  const opnieuw = await basis(page);
  ok(opnieuw.knop, 'dan staat het aanbod er weer');
  ok(/opnieuw/i.test(opnieuw.knopTekst), 'en de knop zegt dat het een herhaling is (' + opnieuw.knopTekst + ')');

  console.log('\n-- stoppen kan altijd --');
  await page.evaluate(() => peilStart());
  await page.waitForTimeout(600);
  await page.click('#btnPeilStop');
  await page.waitForTimeout(400);
  const gestopt = await page.evaluate(() => ({ nu: peilNu, balk: !!document.getElementById('dagBasisBalk') }));
  ok(gestopt.nu === null, 'de peiling is weg');
  ok(gestopt.balk, 'en je staat gewoon terug op je dagscherm');

  ok(errs.length === 0, 'geen javascriptfouten: ' + errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fout ? '\n' + fout + ' PUNT(EN) GEFAALD' : '\nALLES GROEN');
  process.exit(fout ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
