// Playwright-test voor de muur (8 aug, v22.7). Stefan: "iets anders kan zijn in je beginscherm een
// wall ilona deed x en dat je dan een reactie kunt plaatsen."
// Wat hier bewaakt wordt, en het zijn allemaal beslissingen en geen details:
//  - een regel per persoon per dag, de zwaarste van die dag (anders verdrinken mijlpalen in dagoogst)
//  - "oud" gestempelde mijlpalen komen er nooit op (anders vier je op dag een je hele geschiedenis)
//  - alleen de mijlpaal van vandaag krijgt een tegel, die van gisteren is een gewone regel
//  - je staat er zelf tussen, maar je kunt niet op jezelf reageren
//  - een naam uit een ander profiel gaat als HTML het scherm op en moet dus ontsmet worden
//  - er is geen enkel getal dat van twee mensen tegelijk is: geen ranglijst, geen winnaar
//  - en sinds v22.8 geldt dat ook voor de groepkaart: de week-race is daar opgeheven
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
  await page.fill('input[placeholder="Name"]', 'Stefan');
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);

  // Een groep met drie mensen, nepdata in precies de vorm die /api/groep/:gcode teruggeeft.
  const html = await page.evaluate(() => {
    const vandaag = today();
    const g = new Date(Date.now() - 86400000);
    const gisteren = g.getFullYear() + '-' + String(g.getMonth() + 1).padStart(2, '0') + '-' + String(g.getDate()).padStart(2, '0');
    S.groepen = [{ gcode: 'gtest', naam: 'Proef' }];
    muurData = {
      ok: true,
      spelers: [
        { naam: 'Ilona', niveau: 'beginner', txp: 400, petKleur: 'rosa', wear: {}, baile: 'salsa', bailes: ['salsa'],
          woorden: 100,
          // drie dingen op dezelfde dag: alleen de zwaarste hoort op de muur
          mijlpalen: { 'woorden-100': vandaag, 'baile-salsa': vandaag, 'woorden-25': 'oud' },
          oogst: { [vandaag]: { w: 5, z: 3 } } },
        { naam: 'Stefan', niveau: 'a2', txp: 9000, petKleur: 'rosa', wear: { sombrero: true }, baile: 'tango',
          bailes: ['tango'], woorden: 353, mijlpalen: { 'les-a2-8': gisteren }, oogst: { [vandaag]: { w: 0, z: 18 } } },
        { naam: '<img src=x onerror=alert(1)>', niveau: 'a2', txp: 100, wear: {}, baile: null, bailes: [],
          woorden: 10, mijlpalen: {}, oogst: { [vandaag]: { w: 2, z: 0 } } }
      ],
      krabbels: []
    };
    return { html: muurHtml(), vandaag, gisteren };
  });

  const h = html.html;
  ok(/Ilona/.test(h) && /(kent nu 100 woorden|now knows 100 words)/.test(h), 'Ilona haar mijlpaal staat erop');
  ok(!/la salsa/.test(h), 'haar tweede mijlpaal van dezelfde dag niet: een regel per persoon per dag');
  ok(!/(5 nieuwe woorden|5 new words)/.test(h), 'en haar dagoogst ook niet, want de mijlpaal woog zwaarder');
  ok(!/(25 woorden|25 words)/.test(h), 'een mijlpaal met stempel "oud" komt er nooit op');
  ok(/muurTegel/.test(h), 'de mijlpaal van vandaag krijgt een tegel');
  ok(/(18 zinnen|18 sentences)/.test(h), 'Stefan heeft vandaag geen mijlpaal, dus zijn dagoogst staat er');
  ok(/(les 8|lesson 8)/.test(h), 'zijn mijlpaal van gisteren staat er ook');

  const tegels = (h.match(/muurTegelKop/g) || []).length;
  ok(tegels === 1, 'alleen vandaag krijgt een tegel, gisteren is een gewone regel: ' + tegels);

  ok(!/<img src=x/.test(h), 'een naam uit een ander profiel wordt ontsmet');
  ok(/&lt;img src=x/.test(h), 'en verschijnt als tekst');

  ok(!/klassement|ranglijst|winnaar|streak|dagen op rij/i.test(h), 'geen ranglijst en geen streak op de muur');

  const knoppen = await page.evaluate(() => {
    const el = document.createElement('div');
    el.innerHTML = muurHtml();
    const rijen = el.querySelectorAll('.muurTegel, .muurRij');
    let eigenMetKnop = 0;
    rijen.forEach((r) => { if (/Jij/.test(r.textContent) && r.querySelector('[data-mopen]')) eigenMetKnop++; });
    return { rijen: rijen.length, eigenMetKnop, knoppen: el.querySelectorAll('[data-mopen]').length };
  });
  ok(knoppen.rijen === 4, 'vier regels: Ilona vandaag, Stefan vandaag en gisteren, en de derde: ' + knoppen.rijen);
  ok(knoppen.eigenMetKnop === 0, 'je kunt niet op je eigen regel reageren');
  ok(knoppen.knoppen === 2, 'wel op die van de anderen: ' + knoppen.knoppen);

  // een dansje van een maatje toont zijn eigen Chispa met de zin die al bij dat dansje hoort
  const dans = await page.evaluate(() => {
    const vandaag = today();
    muurData.krabbels = [{ van: 'stefan', naar: 'ilona', sleutel: 'baile', dag: vandaag }];
    return muurHtml();
  });
  ok(/muurDans/.test(dans), 'het dansje verschijnt als dansje, niet als tekstregel');
  ok(/El tango es una pasi/.test(dans), 'met de Spaanse zin die al in BAILES stond');
  ok(/chtango/.test(dans), 'en met de bestaande animatieklasse van de app');
  ok(/(Tango is een passie|Tango is a passion)/.test(dans), 'met de vertaling eronder');

  // een gewone krabbel blijft een gewone krabbel
  const krab = await page.evaluate(() => {
    muurData.krabbels = [{ van: 'stefan', naar: 'ilona', sleutel: 'ole', dag: today() }];
    return muurHtml();
  });
  ok(/Ol/.test(krab) && /muurRe/.test(krab), 'een gewone krabbel komt er als regel bij');

  // zonder groep is er geen muur
  const zonder = await page.evaluate(() => { S.groepen = []; return muurHtml(); });
  ok(zonder === '', 'zonder groep staat er niets, ook geen lege kaart');

  // ---- v22.8: de week-race is opgeheven ----
  const race = await page.evaluate(() => {
    const voor = JSON.stringify(S.weekOnthuld || null);
    checkWeekWinnaar();
    return {
      reveal: typeof toonWinnaarReveal,
      onthuld: JSON.stringify(S.weekOnthuld || null) === voor,
      introNl: GROEP_TXT.nl.intro,
      introEn: GROEP_TXT.en.intro
    };
  });
  ok(race.reveal === 'undefined', 'het onthullingsscherm van de weekwinnaar bestaat niet meer');
  ok(race.onthuld, 'checkWeekWinnaar() doet niets meer, ook niet stiekem');
  ok(!/klassement/i.test(race.introNl), 'de groepstekst belooft geen klassement meer');
  ok(!/leaderboard/i.test(race.introEn), 'ook niet in het Engels');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));

  await browser.close();
  console.log(fails === 0 ? 'ALLES GROEN' : fails + ' FOUT');
  process.exit(fails === 0 ? 0 : 1);
})();
