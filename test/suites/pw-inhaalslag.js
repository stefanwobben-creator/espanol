// v23.8: de inhaalslag. Eenmalig zeggen wat je al kent, daarna gespreid terugkrijgen.
//
// Stefan: "zou ik een eenmalige push kunnen doen met woorden die ik al ken (maar die nog niet zijn
// getoetst)? gewoon alles van A1 en A2, ik zal eerlijk zeggen wat ik niet ken." En: "nee eenmalig de
// sweep en dan verspreid terug laten komen."
//
// Wat deze suite bewaakt is niet dat het scherm er is, maar de drie dingen die stuk kunnen zonder dat
// je het ziet: dat zelf gezegd niet doorgaat voor bewezen, dat de vervaldatums echt gespreid zijn, en
// dat de eerste echte check telt of je goed zat.
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
  await page.fill('input[placeholder="Name"]', 'PwSw' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // ---- 1. wat er wel en niet in de lijst hoort ----
  const kand = await page.evaluate(() => {
    S.srs = S.srs || {};
    const eerste = WORDS.filter((w) => !(w.tag || '').startsWith('boek-'))[0];
    S.srs[eerste.id] = { box: 2, due: today(), n: 3 };
    const lijst = sweepKandidaten();
    return {
      aantal: lijst.length,
      totaal: WORDS.length,
      alGeoefend: lijst.some((w) => w.id === eerste.id),
      boek: lijst.filter((w) => (w.tag || '').indexOf('boek-') === 0).length
    };
  });
  ok(kand.aantal > 100, 'er staat een flinke lijst klaar: ' + kand.aantal + ' van ' + kand.totaal);
  ok(kand.alGeoefend === false, 'een woord dat je al oefent staat er niet bij, want dat mag niet overschreven worden');
  ok(kand.boek === 0, 'boekwoorden doen niet mee: die horen bij een hoofdstuk dat je nog moet vrijspelen');

  // ---- 2. de kern: zelf gezegd is geen bewijs ----
  const na = await page.evaluate(() => {
    const lijst = sweepKandidaten();
    const uit = {};
    lijst.slice(0, 5).forEach((w) => { uit[w.id] = 1; });     // vijf woorden: "die ken ik niet"
    const kenIds = lijst.slice(5).map((w) => w.id);
    const r = sweepBewaar(uit);
    const dagen = {};
    let vast = 0, claim = 0, box = {};
    kenIds.forEach((id) => {
      const st = S.srs[id];
      if (!st) return;
      dagen[st.due] = (dagen[st.due] || 0) + 1;
      box[st.box] = (box[st.box] || 0) + 1;
      if (st.claim) claim++;
      // vast = de laatste doos EN een echte getypte check (st.k). Zie voortgangTellers().
      if (st.box >= stevigDrempel() && st.k) vast++;
    });
    return {
      ken: r.ken, niet: r.niet,
      onbekendZonderRegel: lijst.slice(0, 5).every((w) => !S.srs[w.id]),
      dagen: Object.keys(dagen).length,
      drukste: Math.max.apply(null, Object.keys(dagen).map((d) => dagen[d])),
      boxen: Object.keys(box),
      claim: claim, vast: vast, gezaaid: kenIds.length,
      vandaagDue: Object.keys(S.srs).filter((id) => S.srs[id].due <= today()).length
    };
  });
  ok(na.niet === 5 && na.ken === na.gezaaid, 'vijf op "ken ik niet", de rest gezaaid: ' + na.ken);
  ok(na.onbekendZonderRegel === true, 'wat je niet kent krijgt geen srs-regel: de les introduceert het op het normale tempo');
  ok(na.vast === 0, 'GEEN ENKEL gezaaid woord telt als bewezen vast, hoe zeker je ook was');
  ok(na.boxen.length === 1 && na.boxen[0] === '3', 'ze staan allemaal in doosje drie: ze komen terug en moeten zich bewijzen');
  ok(na.claim === na.gezaaid, 'elk gezaaid woord draagt de vlag dat jij het claimde: ' + na.claim);

  // ---- 3. de spreiding, want zonder die spreiding stopt hij ermee ----
  ok(na.dagen > 30, 'de vervaldatums liggen over tientallen dagen verspreid: ' + na.dagen + ' verschillende dagen');
  ok(na.drukste <= Math.ceil(na.gezaaid / 30), 'geen enkele dag krijgt een bult: hoogstens ' + na.drukste + ' woorden');
  ok(na.vandaagDue <= 2, 'en vandaag staat er niets extra klaar (' + na.vandaagDue + '), dus de les van vandaag verandert niet');

  // ---- 4. de eerste echte check haalt de claim weg en telt of je goed zat ----
  const check = await page.evaluate(() => {
    const ids = Object.keys(S.srs).filter((id) => S.srs[id].claim);
    const goedId = ids[0], foutId = ids[1];
    S.sweep.goed = 0; S.sweep.fout = 0;
    wCur = WORDS.filter((w) => w.id === goedId)[0]; answerWord(true);
    wCur = WORDS.filter((w) => w.id === foutId)[0]; answerWord(false);
    // nog een keer hetzelfde woord: de vlag is weg, dus het mag niet dubbel tellen
    wCur = WORDS.filter((w) => w.id === goedId)[0]; answerWord(true);
    return {
      goed: S.sweep.goed, fout: S.sweep.fout,
      vlagWeg: !S.srs[goedId].claim && !S.srs[foutId].claim,
      foutTerug: S.srs[foutId].box === 0
    };
  });
  ok(check.goed === 1 && check.fout === 1, 'de eerste check per woord telt mee: ' + check.goed + ' goed, ' + check.fout + ' fout');
  ok(check.vlagWeg === true, 'daarna is de vlag weg, dus hetzelfde woord telt niet twee keer');
  ok(check.foutTerug === true, 'een woord dat je toch niet bleek te kennen valt terug naar doosje nul');

  // ---- 5. het is eenmalig, en het profiel vertelt wat eruit kwam ----
  const profiel = await page.evaluate(() => {
    const uitnodiging = sweepBlokHtml();
    show('perfil');
    const tekst = document.getElementById('perfilCard').innerText;
    return { gedaan: sweepGedaan(), knop: /btnSweepStart/.test(uitnodiging), tekst: tekst };
  });
  await page.waitForTimeout(300);
  ok(profiel.gedaan === true, 'de inhaalslag staat als gedaan genoteerd');
  ok(profiel.knop === false, 'en de uitnodiging om te beginnen is weg: hij is eenmalig');
  ok(/(inhaalslag|Catching up)/.test(profiel.tekst), 'op je profiel staat wat eruit kwam');
  ok(/(tien nagekeken|ten checked|inschat|judge yourself)/.test(profiel.tekst),
     'inclusief de belofte dat hier komt te staan hoe vaak je inschatting klopte');

  // ---- 6. en het scherm zelf doet wat het belooft ----
  const scherm = await page.evaluate(() => {
    S.srs = {}; delete S.sweep;
    sweepUit = {};
    sweepModal();
    const chips = document.querySelectorAll('#sweepCard [data-sw]');
    const eerste = chips[0];
    eerste.click();
    return {
      chips: chips.length,
      standaardAan: !chips[1].classList.contains('uit'),
      naTik: eerste.classList.contains('uit'),
      inUit: !!sweepUit[eerste.getAttribute('data-sw')],
      voet: !!document.querySelector('#sweepCard .swVoet'),
      rijen: document.querySelectorAll('#sweepCard .swRij').length,
      genest: document.querySelectorAll('#sweepCard .swRij .swRij').length
    };
  });
  ok(scherm.chips > 100, 'alle woorden staan als knop op het scherm: ' + scherm.chips);
  ok(scherm.standaardAan === true, 'alles staat standaard op "ken ik", zodat je alleen de uitzonderingen aantikt');
  ok(scherm.naTik === true && scherm.inUit === true, 'een tik zet een woord op "ken ik niet"');
  ok(scherm.voet === true, 'onderaan staat de telling met de knop om af te ronden');
  ok(scherm.rijen > 1 && scherm.genest === 0, 'de groepen staan naast elkaar, niet in elkaar genest');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
