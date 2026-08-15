// pw-omkeer.js (15 aug, v23.109) — meet "Wie is dit?" wat hij belooft te meten?
//
// WAAROM DIT ER IS
//
// Stefan, na de vormdril: "ik had alles goed. maar dat is niet goed. want ik herken nu gewoon de
// yo en nosotors maar nog steeds niet wat de vorm is."
//
// De Conjugador zet de persoon in de vraag ("nosotros + hablar -> ?"), dus de uitgang draagt daar
// geen informatie. Dit scherm draait de richting om: er staat alleen een vorm, en jij zegt wie.
//
// De hele waarde van dit scherm zit in de betrouwbaarheid van de uitslag, want die uitslag is de
// falsificatietest van het ontwerpadvies: scoort Stefan hier veel lager dan in de Conjugador, dan
// meet de Conjugador iets anders dan hij belooft. Een scherm dat een te hoog of te laag cijfer
// geeft maakt die conclusie waardeloos. Vandaar deze suite.
//
// DE CONTROLEGEVALLEN
//
// Vier stuks, elk sluit een andere manier uit waarop dit scherm groen kan zijn zonder te werken:
//
//   1. GEEN DUBBELZINNIGE VRAAG. Dit is de belangrijkste. "hablaba" is zowel yo als él/ella; een
//      vraag met twee goede antwoorden meet niets. Gecontroleerd over de HELE pool, niet over een
//      steekproef, want een steekproef mist precies het geval dat je zoekt.
//   2. altijd dezelfde knop kiezen mag nooit 12/12 geven (anders keurt het scherm alles goed)
//   3. het juiste antwoord per vraag moet wél 12/12 geven (anders keurt het alles af)
//   4. de vraag mag het antwoord niet weggeven: er staat geen voornaamwoord op het scherm vóór je
//      geantwoord hebt. Dit is exact de fout die in de Conjugador zit (288/288 meerkeuzevragen met
//      een unieke persoonsuitgang tussen de opties), en dit scherm bestaat om hem niet te maken.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

// Speelt één hele ronde. keuze is een persoonsnummer 0..5, of 'echt' voor het juiste antwoord.
async function ronde(page, keuze) {
  await page.evaluate(() => { funView = 'omkeer'; omkeerSpel = null; renderFun(); });
  await page.waitForTimeout(200);
  const n = await page.evaluate(() => omkeerSpel.rij.length);
  for (let i = 0; i < n; i++) {
    const p = keuze === 'echt'
      ? await page.evaluate(() => omkeerSpel.rij[omkeerSpel.i].p)
      : keuze;
    await page.click('.omk-p[data-p="' + p + '"]');
    await page.waitForTimeout(50);
    await page.click('#btnOmkVerder');
    await page.waitForTimeout(50);
  }
  return page.evaluate(() => ({
    goed: omkeerSpel.goed,
    n: omkeerSpel.rij.length,
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwOmk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // Alle fasen open: dan bevat de pool ook imperfecto en subjuntivo, en dáár zitten de
  // dubbelzinnige vormen. Met alleen fase 1 open zou controle 1 niets kunnen aantonen.
  await page.evaluate(() => { S.conjOpen = CONJ_FASES.length - 1; try { persist(); } catch (e) {} });

  // ---- 1. de pool ----
  const pool = await page.evaluate(() => {
    const p = omkeerPool();
    // over de HELE pool: hoort elke vorm bij precies één persoon binnen zijn werkwoord en tijd?
    const dubbelzinnig = p.items.filter((x) => {
      const vormen = conjAlleVormen(x.v, x.t);
      return vormen.filter((f) => f === x.vorm).length !== 1;
    });
    return {
      n: p.items.length,
      dubbel: p.dubbel,
      totaal: p.totaal,
      dubbelzinnig: dubbelzinnig.length,
      voorbeeldFout: dubbelzinnig.slice(0, 2).map((x) => x.vorm + ' (' + x.v.inf + ', ' + x.t + ')'),
      tijden: conjOpenTijden(),
      // elk item moet een vorm hebben die ook echt uit conjVorm komt: geen losse tekst in de code
      klopt: p.items.every((x) => x.vorm === conjVorm(x.v, x.p, x.t)),
      personen: Array.from(new Set(p.items.map((x) => x.p))).sort()
    };
  });

  console.log('\n-- de pool --');
  ok(pool.n > 100, 'er is genoeg te vragen (' + pool.n + ' eenduidige vormen uit ' + pool.totaal + ')');
  ok(pool.dubbelzinnig === 0,
    'CONTROLE: geen enkele vraag heeft twee goede antwoorden, over de hele pool gemeten (fout: ' +
    pool.dubbelzinnig + (pool.voorbeeldFout.length ? ' — ' + pool.voorbeeldFout.join(', ') : '') + ')');
  ok(pool.dubbel > 0,
    'en de dubbelzinnige vormen bestaan wel degelijk, ze zijn er alleen uit gefilterd (' + pool.dubbel + ' stuks)');
  ok(pool.klopt === true, 'elke vorm komt uit conjVorm(), er staat geen vervoeging in de schermcode');
  ok(JSON.stringify(pool.personen) === '[0,1,2,3,4,5]', 'alle zes de personen komen voor in de pool');
  ok(pool.tijden.indexOf('imperfecto') !== -1 && pool.tijden.indexOf('subjuntivo') !== -1,
    'met alles open doen imperfecto en subjuntivo mee (' + pool.tijden.join(', ') + ')');

  // ---- 2. de ronde ----
  const opzet = await page.evaluate(() => {
    omkeerStart();
    const vormen = omkeerSpel.rij.map((x) => x.vorm);
    const personen = omkeerSpel.rij.map((x) => x.p);
    return {
      n: omkeerSpel.rij.length,
      uniek: new Set(vormen).size,
      // spreiding: geen ronde van acht keer yo
      maxPerPersoon: Math.max.apply(null, [0, 1, 2, 3, 4, 5].map((p) => personen.filter((x) => x === p).length))
    };
  });

  console.log('\n-- de ronde --');
  ok(opzet.n === 12, 'twaalf vragen per ronde (nu: ' + opzet.n + ')');
  ok(opzet.uniek === opzet.n, 'geen vorm twee keer in dezelfde ronde (' + opzet.uniek + '/' + opzet.n + ')');
  ok(opzet.maxPerPersoon <= 3,
    'CONTROLE: gespreid over de personen, niet acht keer dezelfde uitgang (hoogste: ' + opzet.maxPerPersoon + ')');

  // ---- 3. de meting keurt niet alles goed en niet alles fout ----
  // v23.112: KLIKKEN, niet tellen. Hiervoor stond hier alleen of het element bestond, en daarna
  // werd het scherm geopend met funView = "omkeer". Zo bleef deze check groen terwijl de tegel
  // geen onclick had en dus niets deed. Stefan vond dat, niet de poort.
  await page.evaluate(() => { funView = null; S.speelAlles = true; renderFun(); });
  await page.click('#nav button[data-tab="speeltuin"]');
  await page.waitForTimeout(300);
  await page.evaluate(() => { funView = null; renderFun(); });
  await page.waitForTimeout(200);
  const tegel = await page.locator('#ftOmkeer').count();
  if (tegel) await page.click('#ftOmkeer');
  await page.waitForTimeout(300);
  const viaTegel = await page.evaluate(() => funView);

  const altijd0 = await ronde(page, 0);
  const altijd3 = await ronde(page, 3);
  const echt = await ronde(page, 'echt');

  console.log('\n-- de meting --');
  ok(tegel === 1, 'de tegel staat in de Speeltuin');
  ok(viaTegel === 'omkeer', 'en klikken erop opent het scherm ook echt (nu: ' + viaTegel + ')');
  ok(altijd0.goed < altijd0.n && altijd3.goed < altijd3.n,
    'CONTROLE: altijd dezelfde knop geeft nooit alles goed (' + altijd0.goed + '/' + altijd0.n + ' en ' + altijd3.goed + '/' + altijd3.n + ')');
  ok(echt.goed === echt.n, 'CONTROLE: het juiste antwoord per vraag geeft alles goed (' + echt.goed + '/' + echt.n + ')');

  // ---- 4. de vraag geeft het antwoord niet weg ----
  const vraag = await page.evaluate(() => {
    funView = 'omkeer'; omkeerSpel = null; renderFun();
    const q = omkeerSpel.rij[0];
    const kaart = document.getElementById('funCard').innerText;
    // het voornaamwoord van het juiste antwoord mag nergens op het scherm staan vóór je antwoordt,
    // behalve op de zes knoppen (die staan er voor alle zes, dus die verklappen niets)
    const knoppen = Array.prototype.map.call(document.querySelectorAll('.omk-p'), (b) => b.innerText).join('|');
    const zonderKnoppen = kaart.split('\n').filter((r) => knoppen.indexOf(r.trim()) === -1).join('\n');
    return {
      vorm: (document.getElementById('omkVorm') || {}).innerText || '',
      echteVorm: q.vorm,
      tijd: (document.getElementById('omkTijd') || {}).innerText || '',
      knoppen: document.querySelectorAll('.omk-p').length,
      lektVoornaamwoord: zonderKnoppen.indexOf(CONJ_PRONOMBRES[q.p]) !== -1,
      // en geen tijdsbijwoord: dat is de tweede redundante aanwijzing (learned attention)
      bijwoord: /\b(ayer|siempre|todos los d|ahora|mañana|anoche|nunca)/i.test(kaart)
    };
  });

  console.log('\n-- de vraag verklapt niets --');
  ok(vraag.vorm === vraag.echteVorm && vraag.vorm.length > 0,
    'de vorm staat groot op het scherm ("' + vraag.vorm + '")');
  ok(vraag.knoppen === 6, 'zes knoppen, één per persoon (nu: ' + vraag.knoppen + ')');
  ok(vraag.lektVoornaamwoord === false,
    'CONTROLE: het juiste voornaamwoord staat nergens in de vraag — dit is precies de fout die in de Conjugador zit');
  ok(vraag.bijwoord === false,
    'CONTROLE: geen tijdsbijwoord in de vraag, dus de uitgang is de enige drager (learned attention)');
  ok(/subjuntivo|presente|indefinido|imperfecto|perfecto/.test(vraag.tijd),
    'de tijd staat er wel bij, met Nederlandse naam uit v23.108 ("' + vraag.tijd + '")');

  // ---- 5. de uitslag wordt onthouden, en naast de Conjugador gezet ----
  const st = echt.brok['vorm.persoon'];
  console.log('\n-- de uitslag --');
  ok(!!st, 'de stand staat in S.brok onder vorm.persoon');
  ok(st && st.rondes === 3, 'drie rondes geteld (nu: ' + (st && st.rondes) + ')');
  ok(st && st.beste === 12, 'de beste ronde is bewaard (nu: ' + (st && st.beste) + ')');
  // Bewust NIET in S.gram: daar hangen gramFoutTop(), gcOpenSet() en de dagles aan, en het
  // brokkenmodel is nog niet bewezen. Eerst meten, dan koppelen. Zelfde afspraak als v23.106.
  const gram = await page.evaluate(() => Object.keys(S.gram || {}).length);
  ok(gram === 0, 'en niet in S.gram, want dat model is nog niet bewezen (nu: ' + gram + ' sleutels)');

  // de vergelijking met de Conjugador is de falsificatietest; hij hoort te verschijnen zodra er
  // genoeg Conjugador-antwoorden zijn, en weg te blijven als die er niet zijn
  const zonderCj = await page.evaluate(() => !!document.getElementById('omkVergelijk'));
  await page.evaluate(() => {
    S.conjLaatste = {ar: [1, 1, 1, 1, 1, 1, 1, 1, 0, 0]};
    omkeerStart(); omkeerSpel.i = omkeerSpel.rij.length; omkeerSpel.goed = 3;
    funView = 'omkeer'; renderFun();
  });
  await page.waitForTimeout(200);
  const metCj = await page.evaluate(() => (document.getElementById('omkVergelijk') || {}).innerText || '');
  ok(zonderCj === false, 'zonder Conjugador-historie staat er geen vergelijking (geen verzonnen getal)');
  ok(/80%/.test(metCj) && /25%/.test(metCj),
    'met historie staan beide scores naast elkaar: dat is de falsificatietest ("' + metCj.slice(0, 120) + '")');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
