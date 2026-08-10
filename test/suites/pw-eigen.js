// Playwright-test voor "haar van jou maken" (v19.76).
//
// Stefan: "dan misschien al beetje kunnen aanpassen (bijv kleur, vorm, beetje eigen maken)" en
// "hem ook beetje customizen met apparal en bijv een kleurtje verstrekt denk ik je gevoel bij
// chispa maar het is nog steeds chispa".
//
// Die laatste zin is opnieuw de eigenlijke opdracht, en hij snijdt hier twee kanten op:
//   1. de keuze moet écht iets doen (anders is het geen keuze),
//   2. maar ze moet in elke kleur en elk figuur nog steeds Chispa zijn, en haar leeftijd moet
//      leesbaar blijven. Een figuurkeuze die zwaarder weegt dan haar leeftijd sloopt het
//      kindschema uit v19.74, en dan is de hele groei-arc weg voor een cosmetisch knopje.
// Verder: kleur en figuur zijn meteen vrij. Dat is een ontwerpkeuze en geen omissie, dus hij
// staat hier vast: er mag geen slotje bij staan.
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

  const BASIS = 'http://localhost:8321/espanol-stefan.html';
  await page.goto(BASIS);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(BASIS);
  await page.waitForTimeout(600);

  const naam = 'PwEigen' + Date.now();
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', naam);
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(700);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  await page.evaluate(() => { S.txp = PET_LEVELS[6].min + 5; show('chispa'); });
  await page.waitForTimeout(500);

  // --- 1. Er valt echt iets te kiezen, en niets ervan zit op slot ---
  const aanbod = await page.evaluate(() => ({
    kleuren: PET_KLEUREN.map((k) => k.id),
    vormen: PET_VORMEN.map((v) => v.id),
    kNu: petKleur().id,
    vNu: petVorm().id,
    knoppenK: document.querySelectorAll('#kleurRij button[data-kleur]').length,
    knoppenV: document.querySelectorAll('#vormRij button[data-vorm]').length,
    vormRij: !!document.getElementById('vormRij'),
    tekst: (document.getElementById('groeiCard') || {}).innerText || ''
  }));
  ok(aanbod.kleuren.length >= 5, 'er is meer dan één kleur om uit te kiezen (' + aanbod.kleuren.length + ')');
  ok(aanbod.vormen.length === 3, 'en drie figuren (' + aanbod.vormen.length + ')');
  ok(aanbod.kNu === 'rosa' && aanbod.vNu === 'clasica', 'standaard is ze gewoon roze en klassiek: wie niets kiest merkt er niets van');
  ok(aanbod.knoppenK === aanbod.kleuren.length, 'elke kleur heeft een eigen knop, en die knop is de kleur zelf');
  /* v23.35, op Stefans verzoek: het figuurkiezertje is weg van het scherm. PET_VORMEN blijft
     bestaan, want die voedt de tekening, en petVorm() valt terug op clásica. Wie ooit iets anders
     koos houdt dat: de keuze is niet weggegooid, alleen het kiezertje. Wat hier nu vastligt is dat
     die terugval echt werkt, want anders zou een verwijderd kiezertje een lege tekening opleveren. */
  ok(!aanbod.vormRij, 'het figuurkiezertje staat niet meer op het scherm');
  ok(aanbod.vormen.length === 3 && aanbod.vNu === 'clasica',
     'maar de drie figuren bestaan nog en de terugval is clásica (' + aanbod.vNu + ')');

  // het blok zelf mag geen enkel slotje dragen: identiteit is geen prestatie
  const slotjes = await page.evaluate(() => {
    const rij = [document.getElementById('kleurRij'), document.getElementById('vormRij')];
    return rij.map((r) => (r ? r.innerHTML : '')).join('').indexOf('🔒');
  });
  ok(slotjes === -1, 'er staat geen slotje bij kleur of figuur: dit hoef je niet te verdienen');

  // --- 2. De groeiteller heet Vorm n/8, en dat gaat over haar leeftijd ---
  ok(/Vorm \d\/8|Form \d\/8/.test(aanbod.tekst), 'de groeiteller heet nog steeds Vorm n/8 (dat is haar leeftijd)');
  /* v23.35: hier stond dat de figuurkeuze géén "vorm" mocht heten, omdat twee betekenissen van
     hetzelfde woord op één kaart iemand kwijtraken. Dat probleem is opgelost door het kiezertje weg
     te halen, dus de eis vervalt met het ding waar hij over ging. */

  // --- 3. Een klik doet echt iets, en het blijft ---
  const voor = await page.evaluate(() => document.getElementById('petBox').innerHTML);
  await page.click("#kleurRij button[data-kleur='menta']");
  await page.waitForTimeout(300);
  const na = await page.evaluate(() => ({
    svg: document.getElementById('petBox').innerHTML,
    id: petKleur().id,
    aan: document.querySelectorAll('#kleurRij button.kleurknop.aan').length,
    gekozen: (document.querySelector("#kleurRij button[data-kleur='menta']") || {}).className || ''
  }));
  ok(na.id === 'menta', 'een klik op mint maakt haar mint');
  ok(na.svg !== voor, 'en dat zie je meteen aan de tekening');
  ok(na.aan === 1 && /aan/.test(na.gekozen), 'precies één kleur staat aangevinkt: de jouwe');

  /* Het kiezertje is weg, maar de figuren moeten nog wel dóórwerken in de tekening: wie ooit
     esbelta koos heeft dat nog staan, en die tekening hoort er dan ook anders uit te zien. Dus
     zetten we hem hier rechtstreeks, precies zoals een oud profiel hem heeft staan. */
  await page.evaluate(() => { S.petVorm = 'esbelta'; try { persist(); } catch (e) {} renderPet(); });
  await page.waitForTimeout(300);
  const naVorm = await page.evaluate(() => ({ id: petVorm().id, svg: document.getElementById('petBox').innerHTML }));
  ok(naVorm.id === 'esbelta', 'een profiel dat ooit esbelta koos, heeft dat nog steeds');
  ok(naVorm.svg !== na.svg, 'en dat zie je nog steeds aan de tekening');

  await page.reload();
  await page.waitForTimeout(900);
  const naHerlaad = await page.evaluate(() => { show('chispa'); return { k: petKleur().id, v: petVorm().id }; });
  ok(naHerlaad.k === 'menta' && naHerlaad.v === 'esbelta',
     'je keuze overleeft een herlaadbeurt: anders is het geen eigen Chispa maar een filter');

  // --- 4. In elke kleur en elk figuur is het nog steeds hetzelfde dier ---
  const allen = await page.evaluate(() => {
    const uit = [];
    PET_KLEUREN.forEach(function (k) {
      PET_VORMEN.forEach(function (vv) {
        S.petKleur = k.id; S.petVorm = vv.id;
        for (let lvl = 1; lvl < PET_LEVELS.length; lvl++) {
          S.txp = PET_LEVELS[lvl].min + 5;
          const svg = petSVG();
          uit.push({
            k: k.id, v: vv.id, lvl: lvl,
            cirkels: (svg.match(/<circle/g) || []).length,
            kieuwen: (svg.match(/stroke-linecap='round'/g) || []).length,
            eigenKleur: svg.indexOf(k.lijf) !== -1,
            roze: svg.indexOf('#f8b8ce') !== -1,
            W: petFaseVorm(lvl).W
          });
        }
      });
    });
    S.petKleur = 'rosa'; S.petVorm = 'clasica'; S.txp = PET_LEVELS[6].min + 5;
    return uit;
  });
  ok(allen.every((r) => r.cirkels >= 10), 'in elke combinatie houdt ze twee ogen, zes kieuwpunten en twee handen');
  ok(allen.every((r) => r.kieuwen >= 2), 'en haar kieuwtakken');
  const levendEigen = allen.filter((r) => r.lvl < 7);
  ok(levendEigen.every((r) => r.eigenKleur), 'elke levende fase gebruikt echt de gekozen kleur, geen vaste roze');
  ok(levendEigen.filter((r) => r.k !== 'rosa').every((r) => !r.roze), 'en een mintgroene Chispa heeft nergens meer roze aan');

  // de abuela is verbleekt, maar verbleekt in háár kleur en niet stiekem terug naar roze
  const oudjes = await page.evaluate(() => PET_KLEUREN.map(function (k) {
    S.petKleur = k.id; S.txp = PET_LEVELS[7].min + 5;
    const svg = petSVG();
    S.petKleur = 'rosa';
    return { id: k.id, svg: svg, bleek: petBleek(k.lijf, 0.52) };
  }));
  ok(oudjes.every((o) => o.svg.indexOf(o.bleek) !== -1), 'ook oud worden gebeurt in je eigen kleur');
  ok(new Set(oudjes.map((o) => o.svg)).size === oudjes.length, 'zes kleuren geven zes verschillende abuelas');

  // --- 5. Haar leeftijd blijft zwaarder wegen dan haar figuur ---
  // Dit is de belangrijkste assertie van deze versie. Het kindschema uit v19.74 is wat je haar
  // leeftijd laat aflezen; een figuurknop die dat overstemt maakt de hele groei-arc onleesbaar.
  const orde = await page.evaluate(() => {
    const uit = {};
    PET_VORMEN.forEach(function (vv) {
      S.petVorm = vv.id;
      uit[vv.id] = [1, 2, 3, 4, 5, 6].map(function (l) { const f = petFaseVorm(l); return { W: f.W, M: f.M, oogR: f.oogR }; });
    });
    S.petVorm = 'clasica';
    return uit;
  });
  Object.keys(orde).forEach(function (id) {
    ok(orde[id].every((f, i) => i === 0 || f.W >= orde[id][i - 1].W), 'binnen figuur ' + id + ' wordt ze nog steeds breder met de jaren');
    ok(orde[id].every((f, i) => i === 0 || f.oogR <= orde[id][i - 1].oogR), 'en haar ogen krimpen nog steeds mee met het kindschema (' + id + ')');
  });
  ok(orde.redonda[0].W < orde.esbelta[5].W,
     'een baby in het rondste figuur blijft smaller dan een volwassene in het slankste: leeftijd wint van smaak');

  // --- 6. De keuze vertaalt mee ---
  const taal = await page.evaluate(() => ({
    lang: profLang(),
    kop: (document.getElementById('groeiCard') || {}).innerText || '',
    nl: PET_KLEUREN.map((k) => k.nl),
    en: PET_KLEUREN.map((k) => k.en),
    es: PET_KLEUREN.map((k) => k.naam)
  }));
  ok(taal.es.every((n) => n && n.length > 2), 'elke kleur heeft ook een Spaanse naam: je leert er nog iets van ook');
  if (taal.lang === 'en') {
    ok(!/Haar kleur|Haar figuur|klassiek/.test(taal.kop), 'een Engels profiel ziet geen Nederlandse labels bij de keuze');
    ok(/Her colour|Her build|Make her yours/.test(taal.kop), 'maar wel de Engelse');
  } else {
    ok(/Haar kleur|Haar figuur/.test(taal.kop), 'een Nederlands profiel ziet de Nederlandse labels');
    ok(true, 'taalcheck uitgevoerd op een Nederlands profiel');
  }

  // --- 7. Geen JS-fouten in eigen code ---
  const eigen = errors.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(eigen.length === 0, 'geen JS-fouten tijdens de hele test (' + eigen.length + ' gevonden)');
  if (eigen.length) eigen.slice(0, 4).forEach((e) => console.log('   ', e));

  await browser.close();
  if (fails === 0) console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
  else { console.log('\n' + fails + ' TESTS GEFAALD'); process.exit(1); }
})();
