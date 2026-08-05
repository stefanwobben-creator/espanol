// pw-conjfase.js (31 juli, v19.68) — de Conjugador is een ladder.
//
// Stefan, 31 juli: "het begin moet heel makkelijk, je wilt nu nog niet het gevoel hebben dat het te
// moeilijk is. Dus eerst bijv alleen ar werkwoorden tegenwoordige tijd, dan er dan ir dan
// onregelmatige dan verleden tijd 1 etc. Dat je door succes een nieuwe fase ontgrendeld."
//
// v19.67 maakte de start al kleiner maar liet je nog steeds zelf kiezen hoe klein. Dat is een keuze
// die je alleen kunt maken als je al weet wat er te kiezen valt. v19.68 vervangt hem door elf fasen
// in oplopende zwaarte, waarvan je er telkens één open hebt staan en de volgende verdient met acht
// van je laatste tien goed.
//
// Wat hier vastligt is precies wat stilletjes kapot kan: dat fase 1 ook echt vier werkwoorden en drie
// personen is, dat een fase op slot niet alsnog te bereiken is door S.conjFase te zetten, dat de
// sleutel alleen valt op je hóógste fase (anders drill je jezelf omhoog op stof die je al kende), en
// dat een bestaande gebruiker bij het updaten niet ineens terugvalt naar fase 1.
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwFase' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(600);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // ---------- 1. de ladder zelf ----------
  const ladder = await page.evaluate(() => ({
    ids: CONJ_FASES.map((f) => f.id),
    tijden: CONJ_FASES.map((f) => f.tijd),
    eersteDrie: CONJ_FASES.slice(0, 3).map((f) => f.personen.length),
    laatste: CONJ_FASES[CONJ_FASES.length - 1].id,
    regelmatig: ['hablar', 'comer', 'vivir'].map((i) => conjRegelmatig(VERBOS.filter((v) => v.inf === i)[0])),
    onregelmatig: ['ser', 'tener', 'poder'].map((i) => conjRegelmatig(VERBOS.filter((v) => v.inf === i)[0]))
  }));
  ok(JSON.stringify(ladder.ids) === JSON.stringify(['ar', 'er', 'ir', 'seis', 'onreg', 'presente', 'indefreg', 'indef', 'perfecto', 'subjuntivo', 'mix']),
    'de elf fasen staan in oplopende zwaarte: ' + ladder.ids.join(' → '));
  ok(ladder.tijden.slice(0, 6).every((t) => t === 'presente'),
    'de eerste zes fasen blijven allemaal in het presente — eerst de personen, dan pas de tijden');
  ok(JSON.stringify(ladder.eersteDrie) === '[3,3,3]', 'fase 1 t/m 3 drillen alleen yo, tú en él/ella');
  ok(ladder.laatste === 'mix', 'de mix (alle tijden door elkaar) is het eindpunt, niet het beginpunt');
  ok(ladder.regelmatig.every(Boolean), 'conjRegelmatig() herkent hablar, comer en vivir als regelmatig');
  ok(ladder.onregelmatig.every((r) => r === false), 'en ser, tener en poder als onregelmatig (uitgerekend, niet met de hand bijgehouden)');

  // ---------- 2. wat elke fase openzet ----------
  const per = await page.evaluate(() => {
    const bewaardO = S.conjOpen, bewaardF = S.conjFase, bewaardT = S.conjTiempo;
    S.conjOpen = CONJ_FASES.length - 1;      // alles open, zodat we elke fase kunnen inspecteren
    S.conjTiempo = 'subjuntivo';             // mag NIET doorlekken: de fase bepaalt de tijd
    const uit = {};
    CONJ_FASES.forEach((f) => {
      S.conjFase = f.id;
      uit[f.id] = {
        personen: conjPersonen().length,
        pool: conjFasePool().map((v) => v.inf),
        tiempo: conjTiempoKeuze()
      };
    });
    S.conjOpen = bewaardO; S.conjFase = bewaardF; S.conjTiempo = bewaardT;
    uit.alle = VERBOS.length;
    return uit;
  });
  ok(per.ar.pool.length > 0 && per.ar.pool.every((i) => /ar$/.test(i)),
    'fase 1 trekt alleen uit werkwoorden op -ar (' + per.ar.pool.join(', ') + ')');
  ok(per.er.pool.every((i) => /er$/.test(i)), 'fase 2 alleen uit -er (' + per.er.pool.join(', ') + ')');
  ok(per.ir.pool.every((i) => /ir$/.test(i)), 'fase 3 alleen uit -ir (' + per.ir.pool.join(', ') + ')');
  ok(per.ar.pool.length < per.alle / 2, 'fase 1 is echt klein: ' + per.ar.pool.length + ' van ' + per.alle + ' werkwoorden');
  ok(per.seis.personen === 6 && per.seis.pool.length === per.ar.pool.length + per.er.pool.length + per.ir.pool.length,
    'fase 4 voegt de drie regelmatige groepen samen en zet alle zes de personen open');
  ok(per.onreg.pool.length === 7 && per.onreg.pool.indexOf('ser') !== -1,
    'fase 5 is de zeven onregelmatige die je het vaakst nodig hebt (' + per.onreg.pool.length + ')');
  ok(per.presente.pool.length === per.alle, 'fase 6 zet pas het hele werkwoordenbestand open');
  ok(per.ar.tiempo === 'presente' && per.onreg.tiempo === 'presente',
    'de tijdkeuze uit de wizard lekt niet door naar de presente-fasen');
  ok(per.indefreg.tiempo === 'indefinido' && per.perfecto.tiempo === 'perfecto' && per.subjuntivo.tiempo === 'subjuntivo',
    'vanaf fase 7 bepaalt de fase zelf welke tijd je drilt');

  // ---------- 3. de getrokken opgaven blijven binnen de fase ----------
  const trek = await page.evaluate(() => {
    const bewaardO = S.conjOpen, bewaardF = S.conjFase, bewaardT = S.conjTiempo;
    S.conjOpen = CONJ_FASES.length - 1; S.conjFase = 'ar'; S.conjTiempo = 'mix';
    const personen = {}, verbs = {}, tijden = {};
    for (let i = 0; i < 300; i++) {
      const c = pickConjugacion();
      personen[c.p] = 1; verbs[c.verb.inf] = 1; tijden[c.t] = 1;
    }
    S.conjOpen = bewaardO; S.conjFase = bewaardF; S.conjTiempo = bewaardT;
    return { personen: Object.keys(personen).map(Number).sort(), verbs: Object.keys(verbs), tijden: Object.keys(tijden) };
  });
  ok(trek.personen.every((p) => p <= 2), '300 trekkingen op fase 1 leveren nooit nosotros/vosotros/ellos op (' + trek.personen.join(',') + ')');
  ok(trek.verbs.every((v) => /ar$/.test(v)), '300 trekkingen blijven binnen de -ar-werkwoorden');
  ok(trek.tijden.length === 1 && trek.tijden[0] === 'presente', 'en blijven allemaal in het presente (' + trek.tijden.join(',') + ')');

  // ---------- 4. een fase op slot is ook echt op slot ----------
  const slot = await page.evaluate(() => {
    const bewaardO = S.conjOpen, bewaardF = S.conjFase;
    S.conjOpen = 0; S.conjFase = 'subjuntivo';   // vals spelen: rechtstreeks naar de eindbaas
    const uit = { fase: conjFaseNu().id, tijd: conjTiempoKeuze() };
    S.conjOpen = bewaardO; S.conjFase = bewaardF;
    return uit;
  });
  ok(slot.fase === 'ar' && slot.tijd === 'presente',
    'wie S.conjFase op een gesloten fase zet, valt terug op zijn hoogste open fase (' + slot.fase + ')');

  // ---------- 5. ontgrendelen door succes ----------
  const unlock = await page.evaluate(() => {
    const bewaardO = S.conjOpen, bewaardF = S.conjFase, bewaardL = S.conjLaatste;
    const uit = {};
    // 7 van de 10 goed: nog niet
    S.conjOpen = 0; S.conjFase = 'ar'; S.conjLaatste = { ar: [1, 1, 1, 1, 1, 1, 1, 0, 0, 0] };
    uit.zeven = conjProbeerOntgrendelen();
    uit.zevenOpen = S.conjOpen;
    // 8 van de 10: wel
    S.conjOpen = 0; S.conjFase = 'ar'; S.conjLaatste = { ar: [1, 1, 1, 1, 1, 1, 1, 1, 0, 0] };
    const f = conjProbeerOntgrendelen();
    uit.acht = f ? f.id : null;
    uit.achtOpen = S.conjOpen;
    uit.achtFase = S.conjFase;
    // maar 6 antwoorden gegeven, allemaal goed: het venster is nog niet vol
    S.conjOpen = 0; S.conjFase = 'ar'; S.conjLaatste = { ar: [1, 1, 1, 1, 1, 1] };
    uit.tekortAntwoorden = conjProbeerOntgrendelen();
    // een oude fase opnieuw perfect doen mag je niet vooruit duwen
    S.conjOpen = 3; S.conjFase = 'ar'; S.conjLaatste = { ar: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] };
    uit.oudeFase = conjProbeerOntgrendelen();
    uit.oudeFaseOpen = S.conjOpen;
    // bovenaan de ladder valt er niets meer open
    S.conjOpen = CONJ_FASES.length - 1; S.conjFase = 'mix';
    S.conjLaatste = { mix: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] };
    uit.top = conjProbeerOntgrendelen();
    uit.topOpen = S.conjOpen;
    // het venster schuift mee: alleen de laatste tien tellen
    S.conjLaatste = {};
    S.conjOpen = 0; S.conjFase = 'ar';
    for (let i = 0; i < 12; i++) conjLog(false);
    uit.venster = conjFaseScore('ar');
    S.conjOpen = bewaardO; S.conjFase = bewaardF; S.conjLaatste = bewaardL;
    return uit;
  });
  ok(unlock.zeven === null && unlock.zevenOpen === 0, '7 van de 10 goed opent nog niets');
  ok(unlock.acht === 'er' && unlock.achtOpen === 1, '8 van de 10 goed opent de volgende fase (' + unlock.acht + ')');
  ok(unlock.achtFase === 'er', 'en je staat er meteen op — de beloning is de nieuwe stof, niet een badge');
  ok(unlock.tekortAntwoorden === null, 'zes goede antwoorden is nog geen bewijs: het venster van tien moet vol zijn');
  ok(unlock.oudeFase === null && unlock.oudeFaseOpen === 3, 'een al gehaalde fase nog eens perfect doen slaat geen fase over');
  ok(unlock.top === null && unlock.topOpen === ladder.ids.length - 1, 'bovenaan de ladder gebeurt er niets raars');
  ok(unlock.venster.n === 10 && unlock.venster.goed === 0, 'de teller kijkt naar je laatste tien, niet naar alles ooit (' + JSON.stringify(unlock.venster) + ')');

  // ---------- 6. de migratie: niemand raakt kwijt wat hij had ----------
  const migratie = await page.evaluate(() => {
    const bewaardO = S.conjOpen, bewaardE = S.errors, bewaardS = S.conjStap;
    const uit = {};
    const meet = (voor) => { S.conjOpen = undefined; voor(); const o = conjOpenInit(); S.conjOpen = undefined; return o; };
    const orig = window.activeProfile;
    try {
      window.activeProfile = function () { return { track: 'beginner' }; };
      uit.beginner = meet(() => { S.errors = {}; S.conjStap = undefined; });
      window.activeProfile = function () { return { track: 'a2' }; };
      uit.a2 = meet(() => { S.errors = {}; S.conjStap = undefined; });
      uit.geoefend = meet(() => { S.errors = { 'conj:hablar-0': { count: 2 } }; S.conjStap = undefined; });
      window.activeProfile = function () { return { track: 'beginner' }; };
      uit.oudeStap = meet(() => { S.errors = {}; S.conjStap = 'tijden'; });
      window.activeProfile = function () { throw new Error('geen profiel'); };
      uit.kapot = meet(() => { S.errors = {}; S.conjStap = undefined; });
    } finally { window.activeProfile = orig; }
    S.conjOpen = bewaardO; S.errors = bewaardE; S.conjStap = bewaardS;
    uit.presenteIdx = conjFaseIdx('presente');
    uit.max = CONJ_FASES.length - 1;
    return uit;
  });
  ok(migratie.beginner === 0, 'een nieuwe A0-gebruiker begint onderaan de ladder (fase 1)');
  ok(migratie.a2 === migratie.presenteIdx, 'wie A2 kiest start bij het volledige presente en hoeft de -ar/-er/-ir-trap niet op (' + migratie.a2 + ')');
  ok(migratie.geoefend === migratie.max, 'wie al conjugaties geoefend had, krijgt de hele ladder open — een update pakt je niets af');
  ok(migratie.oudeStap === migratie.max, 'en wie in v19.67 al breed had gekozen ook, ook al is dat een A0-profiel');
  ok(migratie.kapot === migratie.presenteIdx, 'zonder leesbaar profiel valt hij terug op het presente in plaats van te crashen');

  // ---------- 7. de fasekaart op het scherm ----------
  const scherm = await page.evaluate(() => {
    S.conjOpen = 1; S.conjFase = 'er'; S.conjLaatste = { er: [1, 1, 1, 1, 0] };
    funView = 'conj';
    show('speeltuin');
    renderFun();
    const kaart = document.getElementById('cjFase');
    const rij = document.getElementById('cjFaseRij');
    return {
      kaart: !!kaart,
      kop: (document.getElementById('cjFaseKop') || {}).textContent || '',
      uitleg: (document.getElementById('cjFaseUit') || {}).textContent || '',
      doel: (document.getElementById('cjFaseDoel') || {}).textContent || '',
      meter: !!document.getElementById('cjFaseMeter'),
      open: rij ? Array.from(rij.querySelectorAll('.cj-fase')).map((b) => b.getAttribute('data-f')) : null,
      sloten: rij ? rij.querySelectorAll('.cj-fase-slot').length : -1,
      actief: rij && rij.querySelector('.cj-fase.primary') ? rij.querySelector('.cj-fase.primary').getAttribute('data-f') : null,
      tijdrij: !!document.getElementById('cjTiempo')
    };
  });
  ok(scherm.kaart === true, 'de fasekaart staat boven de opgave');
  ok(/2\/11/.test(scherm.kop), 'de kop zegt waar je staat op de ladder ("' + scherm.kop.trim() + '")');
  ok(scherm.uitleg.length > 15, 'en eronder staat in één zin wat deze fase inhoudt');
  ok(scherm.meter === true && /4/.test(scherm.doel), 'een meter laat zien hoe ver je van de volgende fase af bent ("' + scherm.doel.trim() + '")');
  ok(JSON.stringify(scherm.open) === '["ar","er"]', 'alleen de vrijgespeelde fasen zijn aanklikbaar (' + (scherm.open || []).join(',') + ')');
  ok(scherm.sloten === 9, 'de negen fasen erboven staan zichtbaar op slot — je ziet waar je heen gaat (' + scherm.sloten + ')');
  ok(scherm.actief === 'er', 'de fase waar je staat is gemarkeerd');
  ok(scherm.tijdrij === false, 'de losse tijdknoppenrij bestaat niet meer: de fase ís de tijdkeuze');

  // terugstappen naar een eerdere fase mag altijd, en overleeft een herlaadbeurt
  await page.click('#cjFaseRij .cj-fase[data-f="ar"]');
  await page.waitForTimeout(250);
  const na = await page.evaluate(() => ({ fase: S.conjFase, personen: conjPersonen().length }));
  ok(na.fase === 'ar' && na.personen === 3, 'je mag altijd terug naar een makkelijkere fase (' + na.fase + ')');
  await page.reload();
  await page.waitForTimeout(700);
  const naReload = await page.evaluate(() => ({ fase: S.conjFase, open: S.conjOpen }));
  ok(naReload.fase === 'ar' && naReload.open === 1, 'fase én ontgrendeling overleven een herlaadbeurt (' + JSON.stringify(naReload) + ')');

  // ---------- 8. het echte pad: antwoorden tot de sleutel valt ----------
  const echt = await page.evaluate(() => {
    S.conjOpen = 0; S.conjFase = 'ar';
    S.conjLaatste = { ar: [1, 1, 1, 1, 1, 1, 1, 1, 0] };  // negen gegeven, acht goed
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.conj = 'moeilijk';
    const tapasVoor = S.tapas || 0;
    funView = 'conj'; conjRonde = null;
    show('speeltuin'); renderFun();
    const hablar = VERBOS.filter((v) => v.inf === 'hablar')[0];
    conjIdx = { verb: hablar, p: 0, t: 'presente' };
    cjMk = null;
    renderFunConjugador();
    const inp = document.getElementById('cjInput');
    if (!inp) return { fout: 'geen invoerveld' };
    inp.value = hablar.presente[0];
    checkConjugador();
    const fb = document.getElementById('cjFeedback');
    return {
      open: S.conjOpen,
      fase: S.conjFase,
      tapas: (S.tapas || 0) - tapasVoor,
      feedback: fb ? fb.textContent : '',
      kop: (document.getElementById('cjFaseKop') || {}).textContent || ''
    };
  });
  ok(!echt.fout, 'de Conjugador toont een invoerveld in de typmodus' + (echt.fout ? ' (' + echt.fout + ')' : ''));
  ok(echt.open === 1 && echt.fase === 'er', 'het tiende antwoord doet de sleutel vallen, gewoon door te oefenen (open=' + echt.open + ')');
  ok(echt.feedback.indexOf('🔓') !== -1, 'en je ziet het meteen bij je antwoord staan, niet pas aan het eind van de ronde');
  ok(echt.tapas === 1, 'de viering is een tapa voor Chispa, precies één (' + echt.tapas + ')');
  ok(/2\/11/.test(echt.kop), 'de fasekaart loopt meteen mee naar de nieuwe fase ("' + echt.kop.trim() + '")');

  // ---------- 9. de vertaling op de kaart ----------
  const gloss = await page.evaluate(() => ({
    metEn: conjGloss({ nl: 'praten', en: 'to talk' }),
    zonderEn: conjGloss({ nl: 'praten' }),
    alleVerbosHebbenEn: VERBOS.every((v) => typeof v.en === 'string' && v.en.length > 0)
  }));
  ok(gloss.metEn === 'to talk', 'in een Engels profiel staat de Engelse vertaling op de kaart');
  ok(gloss.zonderEn === 'praten', 'zonder Engelse vertaling valt hij terug op het Nederlands in plaats van leeg te blijven');
  ok(gloss.alleVerbosHebbenEn === true, 'alle werkwoorden in VERBOS hebben een Engelse vertaling');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED|ERR_NAME_NOT_RESOLVED|ERR_CONNECTION_REFUSED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten tijdens de hele test (' + relevanteErrors.length + ' gevonden)');
  if (relevanteErrors.length) relevanteErrors.slice(0, 6).forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);
})();
