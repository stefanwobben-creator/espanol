// Playwright-test voor tegels bij Vertalen en de luisterknop (7 aug, v21.3). Stefan zag zelf dat
// Vertalen, Husselen en Dictado één oefening met opties zijn. Dit is de eerste helft van dat
// opruimen: Vertalen krijgt de tegelstand erbij, zodat de meerkeuze tussen vier hele zinnen en het
// losse Husselen in de volgende versie weg kunnen. Bewaakt hier: drie treden met drie prijzen, het
// antwoord loopt door de bestaande controle (geen tweede controlemachine), alleen zelf typen telt
// mee voor schrijfvaardigheid, en de luisterknop staat er pas nadat je geantwoord hebt.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error' && !/Failed to load resource/.test(msg.text())) errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"]', 'PwZTegel' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  await page.evaluate(() => { show('vertalen'); });
  await page.waitForTimeout(400);

  // ---- 1. drie treden, en alleen bij zinnen ----
  // v21.4: de meerkeuze tussen vier hele zinnen is weg, want die kon je raden op lengte. Er blijven
  // twee treden over: tegels leggen en zelf typen.
  ok(await page.locator('#sModus .modus-toets').count() === 2, 'Vertalen heeft twee treden');
  const treden = await page.evaluate(() => Array.from(document.querySelectorAll('#sModus .modus-toets')).map(b => b.getAttribute('data-m')));
  ok(treden.join(',') === 'tegels,moeilijk', 'de treden zijn tegels en typen (' + treden.join(',') + ')');
  const woordRij = await page.evaluate(() => moeilijkModusHtml('x', 'makkelijk'));
  ok(/data-m='makkelijk'/.test(woordRij), 'zonder de tegelvlag blijft makkelijk bestaan (woordjes, Conjugador)');
  ok(!/data-m='tegels'/.test(woordRij), 'en komt de tegelstand daar niet opdagen');
  // een oude opgeslagen keuze mag niet op een verdwenen stand blijven staan
  const oud = await page.evaluate(() => {
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.zin = 'makkelijk';
    const m = sHuidigeModus(sIdx);
    delete S.modusKeuze.zin;
    return m;
  });
  ok(oud === 'tegels', 'een oude keuze "makkelijk" leest nu als tegels (' + oud + ')');

  // ---- 2. de tegelstand rendert, met afleiders en zonder invoerveld ----
  await page.evaluate(() => {
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.zin = 'tegels';
    zTegel = null; renderSentenceBody();
  });
  await page.waitForTimeout(300);
  ok(await page.locator('.dtegel[data-zbank]').count() > 0, 'de tegelbank staat op het scherm');
  ok(await page.locator('#sInput[type=hidden]').count() === 1, 'het invoerveld is verborgen: je kunt niet typen');
  const afl = await page.evaluate(() => ({
    bank: zTegel.bank.length,
    echt: zTegel.bank.filter(t => t.echt).length,
    nep: zTegel.bank.filter(t => !t.echt).length
  }));
  // Er ligt er altijd minstens een: zonder afleider zijn alle tegels goed en is de opgave op te
  // lossen zonder te lezen. Levert de conceptmachine er geen (korte zin zonder conceptwoord), dan
  // valt hij terug op een echt Spaans woord uit een andere zin.
  ok(afl.nep >= 1 && afl.nep <= 3, 'er liggen 1 tot 3 afleiders bij (' + afl.nep + ' van ' + afl.bank + ')');
  const kort = await page.evaluate(() => {
    const t = dicSleepTegels('Vivo en Madrid');
    return dicSleepAfleiders(t).length;
  });
  ok(kort >= 1, 'ook een korte zin zonder conceptwoord krijgt een afleider (' + kort + ')');
  ok(afl.echt === afl.bank - afl.nep, 'de rest zijn de echte woorden van de zin');

  // aantikken en weer weghalen
  await page.click('.dtegel[data-zbank]:not(.weg)');
  await page.waitForTimeout(150);
  ok(await page.locator('.dtegel[data-zrij]').count() === 1, 'een aangetikte tegel verschijnt in de antwoordrij');
  await page.click('.dtegel[data-zrij]');
  await page.waitForTimeout(150);
  ok(await page.locator('.dtegel[data-zrij]').count() === 0, 'nog eens aantikken haalt hem weg');

  // ---- 3. goed leggen loopt door de bestaande controle ----
  const uit = await page.evaluate(() => {
    const s = sIdx;
    const voorXp = S.xp[today()] || 0;
    const voorSchrijven = Object.keys(S.comp.schrijven || {}).length;
    zTegel.rij = [];
    dicSleepTegels(s.es).forEach(function (w) {
      for (var i = 0; i < zTegel.bank.length; i++) {
        if (zTegel.bank[i].woord === w && zTegel.rij.indexOf(i) === -1) { zTegel.rij.push(i); break; }
      }
    });
    document.getElementById('btnZTegelCheck').click();
    return {
      done: !!S.done[s.id],
      xpErbij: (S.xp[today()] || 0) - voorXp,
      schrijvenErbij: Object.keys(S.comp.schrijven || {}).length - voorSchrijven,
      id: s.id
    };
  });
  ok(uit.done === true, 'de zin telt als gehaald');
  ok(uit.xpErbij === 3, 'tegels leveren 3 tacos op, tussen meerkeuze (2) en typen (5) in (' + uit.xpErbij + ')');
  ok(uit.schrijvenErbij === 0, 'tegels tellen niet mee voor schrijfvaardigheid: leggen is herkennen, geen produceren');

  // ---- 4. de luisterknop staat er pas na het antwoord ----
  ok(await page.locator('#btnZinLuister').count() === 1, 'na het antwoord staat er een luisterknop');
  ok(await page.locator('#btnZinLuisterLento').count() === 1, 'en een langzame variant');
  const paden = await page.evaluate(() => {
    const echt = Audio;
    let gevraagd = '';
    window.Audio = function (src) { gevraagd = src; return { play: function () { return { catch: function () {} }; }, pause: function () {}, playbackRate: 1 }; };
    zinSpreek(sIdx, 1);
    window.Audio = echt;
    return gevraagd;
  });
  ok(paden === 'audio/dictado/' + uit.id + '.mp3', 'de knop speelt de bestaande opname van die zin (' + paden + ')');

  await page.evaluate(() => { S.modusKeuze.zin = 'moeilijk'; renderSentence(true); });
  await page.waitForTimeout(300);
  ok(await page.locator('#btnZinLuister').count() === 0, 'voordat je geantwoord hebt staat de luisterknop er niet');

  // ---- 5. typen telt wel mee voor schrijven ----
  const typen = await page.evaluate(() => {
    const s = sIdx;
    const voor = Object.keys(S.comp.schrijven || {}).length;
    document.getElementById('sInput').value = s.es;
    checkSentence();
    return Object.keys(S.comp.schrijven || {}).length - voor;
  });
  ok(typen === 1, 'zelf typen telt wel mee voor schrijfvaardigheid');

  // ---- 6. v23.51: de knop staat waar je hem zoekt ----
  // Stefan, telefoontest 11 aug: "je controleert, resultaat is goed of fout, maar dan moet je zelf
  // op de knop volgende zin klikken, dat vind je niet." Hij stond ná de uitleg én de luisterknoppen,
  // en dat is op 390 pixels onder de vouw.
  const plek = await page.evaluate(() => {
    /* v23.57: de vorige stap heeft al gecontroleerd, en sindsdien klapt de invoer daarna dicht.
       Zonder deze hertekening bestaat #sInput niet meer en viel deze meting om op een null. */
    renderSentence(false);
    const s = sIdx;
    document.getElementById('sInput').value = s.es;
    checkSentence();
    const fb = document.getElementById('sFeedback');
    const kids = Array.prototype.slice.call(fb.children);
    const idx = (test) => kids.findIndex(test);
    return {
      uitslag: idx(c => /feedback/.test(c.className || '')),
      knoppen: idx(c => !!c.querySelector('#btnNext')),
      uitleg: idx(c => /uitleg/.test(c.className || '')),
      volgorde: kids.map(c => (c.className || c.id || c.tagName)).join(' | '),
      knopY: (function () { const b = document.getElementById('btnNext'); return b ? Math.round(b.getBoundingClientRect().top) : -1; })(),
      hoogte: window.innerHeight,
      /* v23.57: na Controleer bleef de hele invoermachine staan — een leeg tegelvak, de tegels, en
         een rode Controleer-knop die niets meer deed, met daaronder een tweede rode knop. Twee
         primaire knoppen op één scherm en de bovenste dood. Dat is wat Stefan twee telefoontests
         achter elkaar "verwarrend" noemde; het verschuiven van de knop in v23.51 raakte het niet. */
      invoerDicht: !document.getElementById('btnZTegelCheck') && !document.getElementById('btnCheck') &&
                   !document.querySelector('.dsleep-bank'),
      antwoordRegel: /Jouw antwoord|Your answer/.test((document.getElementById('sInvoer') || {}).innerText || ''),
      primair: Array.prototype.map.call(document.querySelectorAll('#sCard button.primary'), b => b.id || b.innerText.trim())
    };
  });
  console.log('  volgorde ::', plek.volgorde, '· primair ::', plek.primair.join(','));
  ok(plek.invoerDicht === true,
    'na Controleer staan de tegels, de invoer en de Controleer-knop er niet meer');
  ok(plek.antwoordRegel === true, 'maar wat je invulde staat er nog wel, als regel');
  ok(plek.primair.length === 1 && plek.primair[0] === 'btnNext',
    'en er is precies één primaire knop over: die naar de volgende zin (' + plek.primair.join(',') + ')');
  ok(plek.uitslag !== -1 && plek.knoppen !== -1 && plek.uitleg !== -1, 'uitslag, knoppen en uitleg staan er alle drie');
  ok(plek.knoppen === plek.uitslag + 1,
    'de knoppenrij staat direct onder de uitslag (uitslag ' + plek.uitslag + ', knoppen ' + plek.knoppen + ')');
  ok(plek.knoppen < plek.uitleg,
    'en dus vóór de uitleg en de luisterknoppen, niet erachter');
  ok(plek.knopY > 0 && plek.knopY < plek.hoogte,
    'Volgende zin staat binnen het scherm (' + plek.knopY + ' van ' + plek.hoogte + ' px)');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  // ---- 7. v23.60: één knop, één rode knop, en hij gaat vanzelf door ----
  /* Stefan, 12 aug, als ontwerpregels: "er moet altijd een knop zijn die controleert en dan
     automatisch doorgaat naar volgende", "je moet altijd in beeld zien waar je bent en hoeveel je
     nog moet", "een toggle makkelijk/moeilijk zou een toggle moeten zijn", en "na Check zie je drie
     rode buttons als call to action, dat is vragen om moeilijkheden".
     Die laatste was te tellen: de actieve moduskeuze rendeerde als .primary, dus Tegels + Controleer
     + Volgende zin waren alle drie rood, en twee ervan deden niets meer. */
  console.log('\n-- v23.60: één rode knop per moment --');
  const knop = await page.evaluate(() => {
    renderSentence(false);
    const rood = () => [].slice.call(document.querySelectorAll('#sCard button.primary'))
      .map((b) => (b.innerText || '').trim());
    const voor = rood();
    const seg = document.querySelector('#sCard .segrij');
    const segRood = !!(seg && seg.querySelector('button.primary'));
    const balk = document.querySelector('#sCard .progressbar');
    document.getElementById('sInput').value = sIdx.es;
    checkSentence();
    return {
      voor: voor, na: rood(),
      segrij: !!seg, segRood: segRood,
      voortgang: !!balk,
      doorbalk: !!document.querySelector('.doorbalk'),
      doorbalkZichtbaar: (function () {
        const d = document.querySelector('.doorbalk');
        if (!d) return false;
        const r = d.getBoundingClientRect();
        return r.height >= 2 && r.width > 50;   // in een flexrij werd hij platgedrukt tot niets
      })()
    };
  });
  ok(knop.voor.length === 1 && /Controleer|Check/.test(knop.voor[0]),
    'vóór het controleren is er precies één rode knop, en dat is Controleer (' + knop.voor.join(',') + ')');
  ok(knop.na.length === 1 && /Volgende zin|Next sentence/.test(knop.na[0]),
    'erna precies één, en dat is de volgende zin (' + knop.na.join(',') + ')');
  ok(knop.segrij === true && knop.segRood === false,
    'de moduskeuze is een schakelaar en geen rode knop: het is een instelling, geen call to action');
  ok(knop.voortgang === true, 'en er staat een balkje bij "zin 1/3", zodat je ziet waar je bent');
  ok(knop.doorbalk === true && knop.doorbalkZichtbaar === true,
    'na een goed antwoord telt een zichtbaar balkje af naar de volgende zin');

  console.log('\n-- en hij gaat vanzelf door, behalve waar dat schaadt --');
  const auto = await page.evaluate(() => new Promise((klaar) => {
    renderSentence(false);
    const oud = sIdx.id;
    const t0 = Date.now();
    document.getElementById('sInput').value = sIdx.es;
    checkSentence();
    const t = setInterval(() => {
      if (sIdx && sIdx.id !== oud) { clearInterval(t); klaar(Date.now() - t0); }
      if (Date.now() - t0 > 6000) { clearInterval(t); klaar(-1); }
    }, 50);
  }));
  console.log('  goed antwoord :: doorgelopen na ' + auto + ' ms');
  ok(auto > 800 && auto < 4000,
    'een goed antwoord gaat vanzelf door, maar niet zo snel dat je de uitslag mist (' + auto + ' ms)');

  const fout = await page.evaluate(() => new Promise((klaar) => {
    renderSentence(false);
    const oud = sIdx.id;
    document.getElementById('sInput').value = 'zzz qqq xxx';
    checkSentence();
    setTimeout(() => klaar({ zelfdeZin: sIdx.id === oud, balk: !!document.querySelector('.doorbalk') }), 3200);
  }));
  ok(fout.zelfdeZin === true && fout.balk === false,
    'een fout antwoord blijft staan: dan staat het juiste antwoord er net en moet je kunnen kijken');

  const geluid = await page.evaluate(() => new Promise((klaar) => {
    let klaar0 = false;
    renderSentence(false);
    const oud = sIdx.id;
    document.getElementById('sInput').value = sIdx.es;
    checkSentence();
    /* De zin willen horen zet de doorloop stil — dat was het bezwaar tegen automatisch doorgaan.
       Expliciet de luisterknop en niet "de eerste knop in het feedbackblok": dat is btnNext, en die
       gaat juist wél door. Groen solo en rood in de volle poort, en terecht: de test klopte niet. */
    const l = document.getElementById('btnZinLuister');
    klaar0 = !l;
    if (l) l.click();
    setTimeout(() => klaar({
      erWasEenLuisterknop: !!l,
      zelfdeZin: sIdx.id === oud, balk: !!document.querySelector('.doorbalk')
    }), 3200);
  }));
  ok(geluid.erWasEenLuisterknop === true, 'de luisterknop staat er na een goed antwoord');
  ok(geluid.zelfdeZin === true && geluid.balk === false,
    'en wie hem aantikt houdt de doorloop stil: het moment om de zin te horen blijft bestaan');

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
