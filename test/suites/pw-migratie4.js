// pw-migratie4.js (24 aug, v23.191) — de opruiming van de opfrisser-uitslagen
//
// WAAROM DEZE SUITE ER IS
//
// Tussen v23.73 en v23.190 bouwde de opfrisser bij elke aanroep een nieuwe vraag, dus gwKies()
// rekende je klik op de ene trekking af tegen het juiste antwoord van een andere. Op twee opties is
// dat een muntje. Migratie 4 ruimt op wat daaruit is voortgekomen.
//
// Dit is de enige migratie tot nu toe die niet alleen sleutels wéggooit maar ook getallen bijstelt,
// en hij raakt Stefans echte voortgang. Dus vier proeven op wat hij moet doen, en vier op wat hij
// NIET mag doen. Die tweede helft is het belangrijkste: een opruiming die te veel weghaalt is erger
// dan de vervuiling, want die is niet terug te draaien.
//
// WAT HIJ MOET DOEN
//   1. De foutregels "gramwiz:opfris-*" verdwijnen.
//   2. Het kanaal opfris verdwijnt uit S.gramLog, en de dagtotalen gaan met precies dat aantal omlaag.
//   3. S.gram[cid].goed en .fout gaan omlaag met wat er uit het ledger bleek, met nul als bodem.
//   4. De doos van een geraakt concept gaat naar hoogstens 1 en komt vandaag terug.
//
// WAT HIJ NIET MAG DOEN (de controlegevallen)
//   5. Fouten van de microles blijven staan. Een opruiming die op "gramwiz:" filtert in plaats van
//      op "gramwiz:opfris-" is triviaal te schrijven en gooit je hele grammaticahistorie weg.
//   6. Het kanaal microles blijft staan, met zijn getallen.
//   7. Een concept waar de opfrisser nooit aan heeft gezeten, blijft ongemoeid — ook zijn doos.
//   8. Twee keer draaien verandert de tweede keer niets (eis 1 van het schemablok).
const { chromium } = require('playwright');

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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwM4' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  const r = await page.evaluate(() => {
    const gisteren = addDays(today(), -1);
    /* Een state zoals hij er bij Stefan uitziet: een concept met opfrisser én microles (genero),
       een concept met alleen microles (serestar), en een concept dat de opfrisser nooit zag
       (negacion). Plus een oude foutregel van vóór de migratie, om te zien dat die blijft. */
    const bouw = function () {
      return {
        schema: 3,
        errors: {
          'gramwiz:opfris-genero-0-0': { id: 'opfris-genero-0-0', type: 'gramwiz', tag: 'opfris-genero', count: 9 },
          'gramwiz:opfris-serestar-0-0': { id: 'opfris-serestar-0-0', type: 'gramwiz', tag: 'opfris-serestar', count: 4 },
          'gramwiz:concept-genero-1-0': { id: 'concept-genero-1-0', type: 'gramwiz', tag: 'concept-genero', count: 3 },
          'woord:w-casa': { id: 'w-casa', type: 'woord', tag: 'huis', count: 5 }
        },
        gramLog: {
          [gisteren]: {
            genero: { n: 5, goed: 3, k: { opfris: [2, 1], microles: [3, 2] } },
            negacion: { n: 4, goed: 4, k: { microles: [4, 4] } }
          },
          [today()]: {
            genero: { n: 2, goed: 1, k: { opfris: [1, 0], microles: [1, 1] } }
          }
        },
        gram: {
          genero: { box: 4, due: addDays(today(), 21), goed: 20, fout: 8, bd: today() },
          negacion: { box: 3, due: addDays(today(), 8), goed: 11, fout: 2, bd: today() }
        }
      };
    };
    const s = bouw();
    const gedaan = migreer(s);
    // en nog een keer, op het resultaat
    const voorTweede = JSON.stringify(s);
    const gedaan2 = migreer(s);
    return {
      gedaan: gedaan, gedaan2: gedaan2, schema: s.schema, SCHEMA: SCHEMA,
      errorSleutels: Object.keys(s.errors).sort(),
      logGisteren: s.gramLog[gisteren], logVandaag: s.gramLog[today()],
      gram: s.gram, vandaag: today(),
      tweedeKeerGelijk: JSON.stringify(s) === voorTweede
    };
  });

  console.log('\n-- wat er gedraaid heeft --');
  console.log('   ' + r.gedaan.map(function (g) { return 'schema ' + g.naar + ': ' + g.wat + ' (' + g.aantal + ')'; }).join('\n   '));
  ok(r.schema === r.SCHEMA, 'de state staat op het huidige schema (' + r.schema + ' van ' + r.SCHEMA + ')');
  ok(r.gedaan.some(function (g) { return g.naar === 4; }), 'migratie 4 heeft gedraaid');

  console.log('\n-- 1 en 5. de foutregels --');
  console.log('   over: ' + r.errorSleutels.join(', '));
  ok(r.errorSleutels.indexOf('gramwiz:opfris-genero-0-0') === -1 &&
     r.errorSleutels.indexOf('gramwiz:opfris-serestar-0-0') === -1,
    'de opfrisserfouten zijn weg');
  ok(r.errorSleutels.indexOf('gramwiz:concept-genero-1-0') !== -1,
    'CONTROLE: de fout van de microles staat er nog (filteren op "gramwiz:" zou je hele historie wissen)');
  ok(r.errorSleutels.indexOf('woord:w-casa') !== -1,
    'CONTROLE: en een woordfout is niet aangeraakt');

  console.log('\n-- 2 en 6. het ledger --');
  console.log('   gisteren, genero: ' + JSON.stringify(r.logGisteren.genero));
  console.log('   gisteren, negacion: ' + JSON.stringify(r.logGisteren.negacion));
  ok(!r.logGisteren.genero.k.opfris && !(r.logVandaag.genero || {}).k.opfris,
    'het kanaal opfris is uit het ledger');
  ok(r.logGisteren.genero.k.microles && r.logGisteren.genero.k.microles[0] === 3,
    'CONTROLE: het kanaal microles staat er nog, met zijn getallen');
  ok(r.logGisteren.genero.n === 3 && r.logGisteren.genero.goed === 2,
    'en het dagtotaal is met precies het opfrisdeel omlaag (5→' + r.logGisteren.genero.n + ', goed 3→' + r.logGisteren.genero.goed + ')');
  ok(r.logGisteren.negacion.n === 4 && r.logGisteren.negacion.k.microles[0] === 4,
    'CONTROLE: een dag zonder opfrisser is niet aangeraakt');

  console.log('\n-- 3 en 4. de tellers en de doos --');
  console.log('   genero:   ' + JSON.stringify(r.gram.genero));
  console.log('   negacion: ' + JSON.stringify(r.gram.negacion));
  // opfris droeg 3 beurten bij (2 gisteren, 1 vandaag), waarvan 1 goed → 1 goed en 2 fout eraf
  ok(r.gram.genero.goed === 19 && r.gram.genero.fout === 6,
    'de tellers zijn met precies het opfrisdeel omlaag (goed 20→' + r.gram.genero.goed +
    ', fout 8→' + r.gram.genero.fout + ')');
  ok(r.gram.genero.box <= 1, 'de doos van een geraakt concept staat op hoogstens 1 (nu: ' + r.gram.genero.box + ')');
  ok(r.gram.genero.due === r.vandaag, 'en het komt vandaag terug (' + r.gram.genero.due + ')');
  ok(r.gram.genero.bd === '', 'en het oordeel van vandaag is losgelaten, anders blijft de doos nog een dag staan');
  ok(r.gram.negacion.box === 3 && r.gram.negacion.goed === 11 && r.gram.negacion.fout === 2,
    'CONTROLE: een concept zonder opfrisser is volledig ongemoeid (doos ' + r.gram.negacion.box + ')');

  console.log('\n-- 8. en twee keer draaien --');
  ok(r.gedaan2.length === 0, 'de tweede keer draait migratie 4 niet opnieuw');
  ok(r.tweedeKeerGelijk, 'CONTROLE: en de state is er geen byte van veranderd');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
