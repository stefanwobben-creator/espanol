// pw-tijdvorm.js (15 aug, v23.113) — meet "Welke tijd is dit?" wat hij belooft?
//
// WAAROM DIT ER IS
//
// De uitslag van "Wie is dit?" (v23.109) was 10/12 tegenover 27/30 in de Conjugador. Met een
// standaardfout van ~11 procentpunt bij twaalf vragen is dat ruis: geen gat. Stefan kent de
// persoonsuitgangen. Zijn gat zit bij de TIJD, en dat sluit aan op zijn echte struikelblok
// (indefinido tegenover imperfecto).
//
// Dit scherm vraagt dus de andere helft: welke tijd is dit? En de uitslag ernaast is die van
// "Wie is dit?", want dat zijn twee metingen van dezelfde soort (herkennen, twaalf vragen, geen
// aanwijzing). De Conjugador ernaast leggen zou produceren tegenover herkennen zijn.
//
// DE CONTROLEGEVALLEN
//
//   1. GEEN DUBBELZINNIGE VRAAG, over de HELE pool gemeten. "hablamos" is presente én indefinido;
//      een vraag met twee goede antwoorden meet niets. Zelfde regel als v23.109.
//   2. altijd dezelfde knop mag nooit alles goed geven
//   3. het juiste antwoord per vraag moet wél alles goed geven
//   4. gespreid over de tijden: een ronde van twaalf keer presente meet één tijd in plaats van het
//      onderscheid ertussen
//   5. met één open tijd valt er niets te onderscheiden, en dan hoort het scherm dat te zeggen in
//      plaats van twaalf keer hetzelfde antwoord te vragen
//   6. de tegel wordt AANGEKLIKT, niet geteld (zie pw-tegels en de les van v23.112)
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

async function ronde(page, keuze) {
  await page.evaluate(() => { funView = 'tijdvorm'; tijdvormSpel = null; renderFun(); });
  await page.waitForTimeout(200);
  const n = await page.evaluate(() => tijdvormSpel.rij.length);
  for (let i = 0; i < n; i++) {
    const t = keuze === 'echt'
      ? await page.evaluate(() => tijdvormSpel.rij[tijdvormSpel.i].t)
      : keuze;
    await page.click('.tv-t[data-t="' + t + '"]');
    await page.waitForTimeout(50);
    await page.click('#btnTvVerder');
    await page.waitForTimeout(50);
  }
  return page.evaluate(() => ({
    goed: tijdvormSpel.goed,
    n: tijdvormSpel.rij.length,
    tekst: document.getElementById('funCard').innerText,
    brok: JSON.parse(JSON.stringify(S.brok || {}))
  }));
}

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTv' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  await page.evaluate(() => { S.lang = 'nl'; S.speelAlles = true; try { persist(); } catch (e) {} });

  // ---- 1. het smalle geval eerst: één open tijd ----
  const smal = await page.evaluate(() => {
    S.conjOpen = 0; S.conjFase = CONJ_FASES[0].id;
    funView = 'tijdvorm'; tijdvormSpel = null; renderFun();
    return {
      tijden: conjOpenTijden().length,
      tekst: document.getElementById('funCard').innerText,
      knoppen: document.querySelectorAll('.tv-t').length
    };
  });

  console.log('\n-- met één open tijd --');
  ok(smal.tijden === 1, 'met fase 1 open staat er één tijd open');
  ok(smal.knoppen === 0 && /nog niets te onderscheiden|only one tense/i.test(smal.tekst),
    'CONTROLE: dan vraagt het scherm niets en zegt het waarom ("' + smal.tekst.replace(/\s+/g, ' ').slice(0, 90) + '")');

  // ---- 2. alles open: de pool ----
  // óók S.conjFase omhoog: conjVerbPool volgt de fase waar je STAAT, niet alleen wat er open is.
  // Zonder deze regel meet de pooltest alleen de vier werkwoorden van fase 1 en zou hij een fout in
  // de brede pool niet zien.
  await page.evaluate(() => {
    S.conjOpen = CONJ_FASES.length - 1;
    S.conjFase = CONJ_FASES[CONJ_FASES.length - 1].id;
    tijdvormSpel = null; try { persist(); } catch (e) {}
  });
  const pool = await page.evaluate(() => {
    const p = tijdvormPool();
    const kaart = tijdvormKaart();
    // over de HELE pool: hoort elke vorm bij precies één tijd?
    const dubbelzinnig = p.items.filter((x) => !kaart[x.vorm] || kaart[x.vorm].length !== 1);
    return {
      n: p.items.length, dubbel: p.dubbel, totaal: p.totaal, tijden: p.tijden,
      dubbelzinnig: dubbelzinnig.length,
      voorbeeld: dubbelzinnig.slice(0, 2).map((x) => x.vorm),
      klopt: p.items.every((x) => x.vorm === conjVorm(x.v, x.p, x.t)),
      // en een positief bewijs dat de kaart werkt: hablamos hoort bij twee tijden
      hablamos: (kaart['hablamos'] || []).length
    };
  });

  console.log('\n-- de pool --');
  ok(pool.n > 800, 'er is genoeg te vragen (' + pool.n + ' eenduidige vormen uit ' + pool.totaal + ')');
  ok(pool.dubbelzinnig === 0,
    'CONTROLE: geen enkele vraag heeft twee goede antwoorden, over de hele pool (fout: ' +
    pool.dubbelzinnig + (pool.voorbeeld.length ? ' — ' + pool.voorbeeld.join(', ') : '') + ')');
  ok(pool.dubbel > 0, 'en de dubbelzinnige vormen zijn er wel, ze zijn eruit gefilterd (' + pool.dubbel + ')');
  ok(pool.hablamos === 2,
    'CONTROLE: de kaart ziet dat "hablamos" bij twee tijden hoort, dus hij kan dubbelzinnigheid zien (nu: ' + pool.hablamos + ')');
  ok(pool.klopt === true, 'elke vorm komt uit conjVorm(), er staat geen vervoeging in de schermcode');
  ok(pool.tijden.length === 5, 'met alles open doen alle vijf de tijden mee (' + pool.tijden.join(', ') + ')');

  // ---- 3. de ronde is gespreid ----
  const opzet = await page.evaluate(() => {
    tijdvormStart();
    const tijden = tijdvormSpel.rij.map((x) => x.t);
    const uniek = {};
    tijden.forEach((t) => { uniek[t] = (uniek[t] || 0) + 1; });
    return {
      n: tijdvormSpel.rij.length,
      uniekeVormen: new Set(tijdvormSpel.rij.map((x) => x.vorm)).size,
      soorten: Object.keys(uniek).length,
      max: Math.max.apply(null, Object.keys(uniek).map((k) => uniek[k]))
    };
  });

  console.log('\n-- de ronde --');
  ok(opzet.n === 12, 'twaalf vragen (nu: ' + opzet.n + ')');
  ok(opzet.uniekeVormen === opzet.n, 'geen vorm twee keer in dezelfde ronde');
  ok(opzet.soorten === 5, 'alle vijf de tijden komen voor in één ronde (nu: ' + opzet.soorten + ')');
  ok(opzet.max <= 3, 'CONTROLE: gespreid, niet twaalf keer presente (hoogste: ' + opzet.max + ')');

  // ---- 4. de tegel, aangeklikt ----
  await page.evaluate(() => { funView = null; renderFun(); });
  await page.click('#nav button[data-tab="speeltuin"]');
  await page.waitForTimeout(250);
  await page.evaluate(() => { funView = null; renderFun(); });
  await page.waitForTimeout(200);
  const tegel = await page.locator('#ftTijdvorm').count();
  if (tegel) await page.click('#ftTijdvorm');
  await page.waitForTimeout(300);
  const viaTegel = await page.evaluate(() => funView);

  console.log('\n-- de tegel --');
  ok(tegel === 1, 'de tegel staat in de Speeltuin');
  ok(viaTegel === 'tijdvorm', 'en klikken opent het scherm ook echt (nu: ' + viaTegel + ')');

  // ---- 5. de meting keurt niet alles goed en niet alles fout ----
  const altijdPres = await ronde(page, 'presente');
  const echt = await ronde(page, 'echt');

  console.log('\n-- de meting --');
  ok(altijdPres.goed < altijdPres.n,
    'CONTROLE: altijd "presente" kiezen geeft niet alles goed (' + altijdPres.goed + '/' + altijdPres.n + ')');
  ok(echt.goed === echt.n,
    'CONTROLE: het juiste antwoord per vraag geeft alles goed (' + echt.goed + '/' + echt.n + ')');

  // ---- 6. de vraag verklapt niets, en de contrastrij verschijnt erna ----
  const vraag = await page.evaluate(() => {
    funView = 'tijdvorm'; tijdvormSpel = null; renderFun();
    const q = tijdvormSpel.rij[0];
    const voor = document.getElementById('funCard').innerText;
    const x = conjTiempo(q.t);
    return {
      vorm: (document.getElementById('tvVorm') || {}).innerText || '',
      echteVorm: q.vorm,
      knoppen: document.querySelectorAll('.tv-t').length,
      // de naam van de goede tijd mag niet in de vraag staan (de knoppen tonen alle vijf, dus die
      // verklappen niets); daarom de kaart minus de knoppen
      lektTijd: voor.split('\n')
        .filter((r) => !/presente|pretérito|subjuntivo|tegenwoordige|verleden|aanvoegende/i.test(r))
        .join('\n').indexOf(x.es) !== -1,
      bijwoord: /\b(ayer|siempre|anoche|mañana|ahora|nunca)\b/i.test(voor)
    };
  });
  const naAntwoord = await page.evaluate(() => {
    const q = tijdvormSpel.rij[tijdvormSpel.i];
    tijdvormAntwoord(q.t);
    const tekst = document.getElementById('funCard').innerText;
    // de contrastrij: alle open tijden van hetzelfde werkwoord en dezelfde persoon
    const alle = conjOpenTijden().map((t) => conjVorm(q.v, q.p, t));
    return { mist: alle.filter((f) => tekst.indexOf(f) === -1), n: alle.length };
  });

  console.log('\n-- de vraag en de contrastrij --');
  ok(vraag.vorm === vraag.echteVorm && vraag.vorm.length > 0, 'de vorm staat groot op het scherm ("' + vraag.vorm + '")');
  ok(vraag.knoppen === 5, 'vijf knoppen, één per open tijd (nu: ' + vraag.knoppen + ')');
  ok(vraag.lektTijd === false, 'CONTROLE: de naam van de goede tijd staat nergens in de vraag');
  ok(vraag.bijwoord === false, 'CONTROLE: geen tijdsbijwoord in de vraag, de vorm is de enige drager');
  ok(naAntwoord.mist.length === 0,
    'na je antwoord staat de hele contrastrij er (alle ' + naAntwoord.n + ' tijden; mist: ' + (naAntwoord.mist.join(', ') || 'niets') + ')');

  // ---- 7. de uitslag en de eerlijke vergelijking ----
  const st = echt.brok['vorm.tijd'];
  console.log('\n-- de uitslag --');
  ok(!!st, 'de stand staat in S.brok onder vorm.tijd');
  ok(st && st.beste === 12, 'de beste ronde is bewaard (nu: ' + (st && st.beste) + ')');
  const gram = await page.evaluate(() => Object.keys(S.gram || {}).length);
  ok(gram === 0, 'en niet in S.gram, want het brokkenmodel is nog niet bewezen (nu: ' + gram + ')');

  const zonder = await page.evaluate(() => {
    S.brok = {}; tijdvormStart(); tijdvormSpel.i = tijdvormSpel.rij.length; tijdvormSpel.goed = 7;
    funView = 'tijdvorm'; renderFun();
    return !!document.getElementById('tvVergelijk');
  });
  const met = await page.evaluate(() => {
    S.brok = {'vorm.persoon': {goed: 10, fout: 2, beste: 10, laatst: today(), rondes: 1}};
    tijdvormStart(); tijdvormSpel.i = tijdvormSpel.rij.length; tijdvormSpel.goed = 5;
    funView = 'tijdvorm'; renderFun();
    return (document.getElementById('tvVergelijk') || {}).innerText || '';
  });

  console.log('\n-- de vergelijking --');
  ok(zonder === false, 'zonder een score op "Wie is dit?" staat er geen vergelijking (geen verzonnen getal)');
  ok(/10\/12/.test(met) && /5\/12/.test(met),
    'met een score staan beide er, en het is herkennen tegenover herkennen ("' + met.slice(0, 110) + '")');

  // ---- 8. v23.114: de verwarring krijgt een naam ----
  //
  // "zes fout" zegt niet welke zes. Zonder deze telling zouden we een les moeten bouwen voor een
  // verwarring die we alleen vermoeden. De controle hieronder is dat de matrix het JUISTE paar
  // aanwijst en niet gewoon het eerste het beste.
  const verwar = await page.evaluate(() => {
    S.brok = {};
    tijdvormStart();
    // met opzet drie keer imperfecto kiezen waar indefinido stond, en één keer iets anders fout:
    // de top hoort dan indefinido>imperfecto te zijn en niet die ene.
    let gedaan = 0, andere = 0;
    tijdvormSpel.rij.forEach((q) => {
      if (q.t === 'indefinido' && gedaan < 3) { tijdvormVerwarBij('indefinido', 'imperfecto'); gedaan++; }
      else if (andere < 1) { tijdvormVerwarBij('presente', 'subjuntivo'); andere++; }
    });
    const top = tijdvormTopVerwar();
    return {
      gedaan, andere, top,
      sleutels: Object.keys((S.brok['vorm.tijd'] || {}).verwar || {}),
      // één losse vergissing mag géén struikelblok heten
      naEen: (function () {
        S.brok = {};
        tijdvormVerwarBij('presente', 'perfecto');
        return tijdvormTopVerwar();
      })()
    };
  });

  console.log('\n-- de verwarringsmatrix --');
  ok(verwar.gedaan === 3, 'de opzet kon drie keer indefinido→imperfecto noteren (nu: ' + verwar.gedaan + ')');
  ok(verwar.sleutels.length === 2, 'twee verschillende verwisselingen genoteerd (' + verwar.sleutels.join(', ') + ')');
  ok(verwar.top && verwar.top.getoond === 'indefinido' && verwar.top.gekozen === 'imperfecto' && verwar.top.n === 3,
    'CONTROLE: de top wijst het juiste paar aan, niet het eerste het beste (' +
    (verwar.top ? verwar.top.getoond + '→' + verwar.top.gekozen + ' ×' + verwar.top.n : 'geen') + ')');
  ok(verwar.naEen === null,
    'CONTROLE: één losse vergissing heet nog geen struikelblok (nu: ' + JSON.stringify(verwar.naEen) + ')');

  // en hij komt op het eindscherm te staan
  const eind = await page.evaluate(() => {
    S.brok = {'vorm.tijd': {goed: 6, fout: 6, beste: 6, laatst: today(), rondes: 1,
                            verwar: {'indefinido>imperfecto': 4}}};
    tijdvormStart(); tijdvormSpel.i = tijdvormSpel.rij.length; tijdvormSpel.goed = 6;
    funView = 'tijdvorm'; renderFun();
    return (document.getElementById('tvVerwar') || {}).innerText || '';
  });
  ok(/indefinido/.test(eind) && /imperfecto/.test(eind) && /4/.test(eind),
    'het eindscherm noemt het paar en hoe vaak ("' + eind.slice(0, 100) + '")');

  // ---- 9. v23.114: een foute keuze krijgt uitleg over die twee tijden ----
  const hint = await page.evaluate(() => {
    funView = 'tijdvorm'; tijdvormSpel = null; renderFun();
    // zet de eerste vraag op een indefinido-vorm en kies imperfecto
    const idx = tijdvormSpel.rij.findIndex((x) => x.t === 'indefinido');
    if (idx < 0) return null;
    tijdvormSpel.i = idx;
    tijdvormAntwoord('imperfecto');
    const el = document.getElementById('tvHint');
    const tekst = el ? el.innerText : '';
    // en bij een GOED antwoord hoort hij er niet te staan
    tijdvormSpel.gekozen = null;
    tijdvormAntwoord('indefinido');
    return { fout: tekst, goed: (document.getElementById('tvHint') || {}).innerText || '' };
  });

  console.log('\n-- uitleg bij een fout --');
  ok(hint && /indefinido/i.test(hint.fout) && /imperfecto/i.test(hint.fout),
    'bij een fout staat er hoe je die twee aan de VORM uit elkaar houdt');
  ok(hint && /aba|ía/.test(hint.fout),
    'en het gaat echt over de letters, niet over de betekenis ("' + (hint ? hint.fout.replace(/\s+/g, ' ').slice(0, 120) : '') + '")');
  ok(hint && hint.goed === '',
    'CONTROLE: bij een goed antwoord staat die uitleg er niet, want dan is het ruis');

  // elke tijd moet een vormkenmerk hebben, anders valt de uitleg stil zodra er een tijd bij komt
  const dekking = await page.evaluate(() => CONJ_TIEMPOS.filter((t) => !t.vorm || !t.vormEn).map((t) => t.id));
  ok(dekking.length === 0, 'DEKKING: elke tijd heeft een vormkenmerk (mist: ' + (dekking.join(', ') || 'niets') + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
