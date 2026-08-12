// De laatste drie punten van de lanceerlijst (v23.70 t/m v23.72), 13 aug.
//
//   1. de app zegt waaróm de AI niet antwoordt, en dat is sinds het slot bijna nooit "onbereikbaar"
//   2. je krijgt je herstelcode ná je eerste les, en hij blijft tot je hem wegtikt
//   3. de privacytekst noemt alles wat de server echt bewaart
//
// Punt 3 is bewust een tekstcheck en geen vormcheck: de vraag is niet hoe het eruitziet maar of het
// er staat. Zeven tabellen in server/index.js, en twee ervan werden niet genoemd.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

async function versProfiel(page, naam) {
  await page.goto(U); await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.clear(); localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload(); await page.waitForTimeout(900);
  await page.fill('input[placeholder="Naam / Name"], input[placeholder="Naam"], input[placeholder="Name"]', naam + Date.now());
  await page.click('button[data-lvl="A0"]');
  await page.click('#btnNewProf');
  await page.waitForFunction(() => !!activeProfile(), { timeout: 15000 });
  await page.waitForTimeout(1300);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await versProfiel(page, 'Lancering');

  // ---------------------------------------------------------------- 1
  console.log('\n-- 1. de AI zegt waarom hij niet antwoordt --');
  const ai = await page.evaluate(() => ({
    uit: aiFoutTekst({ ok: false, reden: 'uit', error: 'de AI-hulp staat even uit' }),
    dag: aiFoutTekst({ ok: false, reden: 'dagplafond' }),
    tempo: aiFoutTekst({ ok: false, reden: 'tempo' }),
    alleenError: aiFoutTekst({ ok: false, error: 'onleesbaar AI-antwoord' }),
    leeg: aiFoutTekst(null),
    nogEensUit: aiNogEensZin({ reden: 'uit' }),
    nogEensDag: aiNogEensZin({ reden: 'dagplafond' }),
    nogEensStuk: aiNogEensZin({ reden: 'stuk' }),
    nogEensLeeg: aiNogEensZin(null)
  }));
  ok(/staat even uit/i.test(ai.uit), 'reden "uit" wordt een eigen zin (' + ai.uit + ')');
  ok(/vandaag op/i.test(ai.dag), 'reden "dagplafond" ook (' + ai.dag + ')');
  ok(/rustig aan/i.test(ai.tempo), 'en "tempo" (' + ai.tempo + ')');
  /* De terugval is de reden dat deze app vóór de server live kan: een oude server stuurt geen
     reden mee, en dan is zijn eigen zin nog altijd waarheidsgetrouwer dan "onbereikbaar". */
  ok(ai.alleenError === 'onleesbaar AI-antwoord', 'zonder reden wint de zin van de server zelf');
  ok(/niet nakijken/i.test(ai.leeg), 'en zonder allebei staat er een algemene zin (' + ai.leeg + ')');
  ok(ai.nogEensUit === false && ai.nogEensDag === false,
    'bij "uit" en "dagplafond" komt de knop niet terug: opnieuw proberen kan niet lukken');
  ok(ai.nogEensStuk === true && ai.nogEensLeeg === true, 'in de andere gevallen wel');
  /* Blokcommentaar eruit voordat we zoeken. Dit is de derde keer in deze codebase dat een test op
     brontekst zijn eigen toelichting vond en daarom rood werd; de zin staat in de commentaren van
     v23.70 omdat daar wordt uitgelegd waarom hij weg moest. */
  const oudeZin = await page.evaluate(() => {
    const bron = document.documentElement.innerHTML.replace(/\/\*[\s\S]*?\*\//g, '');
    return (bron.match(/De AI is even niet bereikbaar/g) || []).length;
  });
  ok(oudeZin === 0, 'en de oude zin staat in geen enkel codepad meer (' + oudeZin + ' keer)');

  // ---------------------------------------------------------------- 2
  console.log('\n-- 2. de herstelcode komt na je eerste les --');
  const voor = await page.evaluate(() => ({
    inDagscherm: /[a-z0-9]+-[a-z0-9]{8,}/.test(document.getElementById('tab-lessen').innerText),
    instelVerborgen: (document.getElementById('instelBlok') || {}).className || ''
  }));
  /* Waarom dit blok bestaat: de code stond alleen in #instelBlok, en dat is standaard hidden.
     Meer, dan Profiel, dan Instellingen. De enige die hem tegenkwam wist al dat hij bestond. */
  ok(/hidden/.test(voor.instelVerborgen), 'de oude plek zit nog steeds achter een uitklapper');
  ok(!voor.inDagscherm, 'en op het dagscherm staat geen code');

  const eind = await page.evaluate(() => {
    lesFlow = { stap: 'woorden' };
    lesFlowKlaar();
    const kaart = document.getElementById('codeKaart');
    return {
      kaart: !!kaart,
      code: (activeProfile() || {}).code || '',
      tekst: kaart ? kaart.innerText.replace(/\s+/g, ' ') : '',
      knoppen: kaart ? kaart.querySelectorAll('button').length : 0
    };
  });
  await page.waitForTimeout(400);
  ok(eind.kaart, 'na de les staat er een blok met je code');
  ok(eind.code && eind.tekst.indexOf(eind.code) !== -1,
    'en dat is jouw echte code, niet een voorbeeld (' + eind.code + ')');
  ok(/browser/i.test(eind.tekst) && /telefoon/i.test(eind.tekst),
    'met erbij waar hij voor is');
  ok(eind.knoppen === 2, 'twee knoppen: kopiëren en wegtikken (' + eind.knoppen + ')');
  ok(/Meer/.test(eind.tekst) && /Instellingen/.test(eind.tekst),
    'en waar je hem later terugvindt');

  const naTik = await page.evaluate(() => {
    document.getElementById('btnCodeGezien').click();
    return { weg: !document.getElementById('codeKaart'), vlag: !!S.codeGezien, leeg: lesFlowCodeHtml() === '' };
  });
  ok(naTik.weg && naTik.vlag, 'wegtikken laat hem verdwijnen en onthoudt dat');
  ok(naTik.leeg, 'en daarna komt hij niet meer terug');
  /* De keerzijde van "blijft tot je hem wegtikt": wie hem laat staan, ziet hem na de vólgende les
     opnieuw. Dat is met opzet, want dit is het enige in de app waarvan het missen onherstelbaar is. */
  const opnieuw = await page.evaluate(() => {
    S.codeGezien = false;
    try { persist(); } catch (e) {}
    lesFlow = { stap: 'woorden' };
    lesFlowKlaar();
    return !!document.getElementById('codeKaart');
  });
  await page.waitForTimeout(300);
  ok(opnieuw, 'wie hem laat staan, krijgt hem na de volgende les weer te zien');

  // ---------------------------------------------------------------- 3
  console.log('\n-- 3. de privacytekst noemt wat de server bewaart --');
  const pr = await page.evaluate(() => {
    show('privacy');
    return document.getElementById('privacyCard').innerText.replace(/\s+/g, ' ');
  });
  await page.waitForTimeout(300);
  /* Zeven tabellen in server/index.js: profiles, logs, groups, group_members, maatjes, krabbels,
     duels. De laatste twee werden niet genoemd, en dat zijn juist de twee waarvan je niet verwacht
     dat ze blijven staan. */
  [['sync-code', /sync-code/i],
   ['e-mailadres', /e-mailadres/i],
   ['taalmodel', /taalmodel/i],
   ['Palabra Duel', /Palabra Duel/i],
   ['krabbel', /krabbel/i],
   ['Render en Neon', /Render/i]].forEach(function (x) {
    ok(x[1].test(pr), 'de tekst noemt ' + x[0]);
  });
  ok(/niets automatisch opgeruimd/i.test(pr),
    'en zegt eerlijk dat er niets automatisch wordt opgeruimd');
  ok(!/[—–]|--/.test(pr), 'geen streepjes in de privacytekst');

  ok(errs.length === 0, 'geen javascriptfouten: ' + errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fout ? '\n' + fout + ' PUNT(EN) GEFAALD' : '\nALLES GROEN');
  process.exit(fout ? 1 : 0);
})();
