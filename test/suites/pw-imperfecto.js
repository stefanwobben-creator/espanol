// pw-imperfecto.js (15 aug, v23.107) — kan de app de imperfecto vervoegen, en landt een brok apart?
//
// WAAROM DIT ER IS
//
// De conceptkaart liet je een imperfecto-tabel zien en zei eronder: "Drill de vormen in de
// Speeltuin." Die drill bestond niet. conjVorm() kende presente, indefinido, perfecto en
// subjuntivo, en de elf fasen van de ladder net zo. De imperfecto zat er nergens in, en dat is
// uitgerekend de tijd waar Stefan op vastloopt.
//
// Deze suite legt twee dingen vast:
//
//  1. de vormen zelf, want die worden bérekend en niet opgezocht. Eén verkeerde uitgang levert
//     stilletjes zes verkeerde vormen per werkwoord op, en niemand die het merkt behalve de
//     leerling die het uit zijn hoofd leert.
//  2. dat een brok-stap in zijn eigen pot landt en niet in de doos van het onderwerp. Dat is de
//     hele reden dat het brokkenmodel bestaat: 23 dozen voor 122 patronen betekent dat "doos 2"
//     vier verschillende dingen kan betekenen.
//
// DE CONTROLEGEVALLEN
//
//  - een werkwoord dat NIET in VERBOS_IMPERF staat moet berekend worden (trabajar -> trabajaba).
//    Zonder die check zou een tabel met alleen ser/ir/ver hier net zo groen staan.
//  - conjVorm met een andere tijd mag géén imperfecto teruggeven: de nieuwe tak mag niet lekken.
//  - een gewone patroonvraag moet nog steeds in S.gram landen. Zonder die check zou "alles gaat
//    naar S.brok" ook groen zijn, en dan is de bestaande boekhouding stil kapot.
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
  await page.waitForTimeout(1500);

  const r = await page.evaluate(() => {
    const v = (i) => VERBOS.filter((x) => x.inf === i)[0];
    const rij = (i) => conjAlleVormen(v(i), 'imperfecto');
    return {
      hablar: rij('hablar'), comer: rij('comer'), vivir: rij('vivir'),
      ser: rij('ser'), ir: rij('ir'), ver: rij('ver'),
      // controle: staat niet in VERBOS_IMPERF, dus moet berekend worden
      trabajar: rij('trabajar'),
      berekend: !VERBOS_IMPERF.trabajar,
      // controle: de nieuwe tak mag niet lekken naar een andere tijd
      presenteNog: conjVorm(v('hablar'), 0, 'presente'),
      label: conjTiempoLabel('imperfecto'),
      fasen: CONJ_FASES.map((f) => f.tijd),
      inMix: (function () {
        // conjTiempoActief() trekt willekeurig uit de mix; dertig keer is ruim genoeg om te zien
        // of imperfecto er überhaupt in zit zonder de test wisselvallig te maken
        const gezien = {};
        const echt = conjFaseNu;
        window.conjFaseNu = function () { return { tijd: 'mix' }; };
        for (let i = 0; i < 60; i++) gezien[conjTiempoActief()] = 1;
        window.conjFaseNu = echt;
        return Object.keys(gezien).sort().join(',');
      })(),
      // de pool mag voor imperfecto niet langs VERBOS_PASADO gefilterd worden
      poolImperf: conjVerbPool('imperfecto').length,
      poolIndef: conjVerbPool('indefinido').length,
      verbenTotaal: VERBOS.length
    };
  });

  console.log('\n-- de regelmatige uitgangen --');
  ok(r.hablar.join(' ') === 'hablaba hablabas hablaba hablábamos hablabais hablaban',
    '-ar: ' + r.hablar.join(' '));
  ok(r.comer.join(' ') === 'comía comías comía comíamos comíais comían', '-er: ' + r.comer.join(' '));
  ok(r.vivir.join(' ') === 'vivía vivías vivía vivíamos vivíais vivían', '-ir: ' + r.vivir.join(' '));
  // de stam eraf (com-, viv-), want alleen de uitgangen horen gelijk te zijn
  ok(r.comer.map((x) => x.slice(3)).join() === r.vivir.map((x) => x.slice(3)).join(),
    'en -er en -ir hebben dezelfde uitgangen, wat de enige tijd is waarin dat zo is');

  console.log('\n-- de drie onregelmatige, en er zijn er niet meer --');
  ok(r.ser.join(' ') === 'era eras era éramos erais eran', 'ser: ' + r.ser.join(' '));
  ok(r.ir.join(' ') === 'iba ibas iba íbamos ibais iban', 'ir: ' + r.ir.join(' '));
  ok(r.ver.join(' ') === 'veía veías veía veíamos veíais veían', 'ver: ' + r.ver.join(' '));

  console.log('\n-- de controlegevallen --');
  ok(r.berekend === true, 'CONTROLE: trabajar staat niet in de uitzonderingentabel');
  ok(r.trabajar.join(' ') === 'trabajaba trabajabas trabajaba trabajábamos trabajabais trabajaban',
    'CONTROLE: en wordt dus berekend uit de infinitief (' + r.trabajar[0] + ')');
  ok(r.presenteNog === 'hablo',
    'CONTROLE: conjVorm met een andere tijd geeft geen imperfecto (nu: ' + r.presenteNog + ')');
  ok(r.poolImperf === r.verbenTotaal || r.poolImperf > r.poolIndef,
    'de imperfecto-pool is niet langs VERBOS_PASADO gefilterd (' + r.poolImperf + ' tegenover ' + r.poolIndef + ')');

  console.log('\n-- de ladder --');
  ok(r.label === 'pretérito imperfecto', 'de tijd heeft een naam (' + r.label + ')');
  ok(r.fasen.filter((t) => t === 'imperfecto').length === 2, 'er zijn twee imperfecto-fasen');
  ok(r.fasen.lastIndexOf('indefinido') < r.fasen.indexOf('imperfecto'),
    'ze staan na het indefinido, zoals in AULA 2');
  ok(r.fasen.indexOf('imperfecto') < r.fasen.indexOf('perfecto'), 'en voor het perfecto');
  ok(/imperfecto/.test(r.inMix), 'de mix trekt ook imperfecto (' + r.inMix + ')');

  // ---- de signaalwoorden en de brok-stap ----
  const s = await page.evaluate(() => {
    const o = gcOnderwerp('concept-indefimperf');
    const stap = o.stappen[0];
    return {
      n: BROK_SIGNAAL.length,
      a: BROK_SIGNAAL.filter((z) => z.s === 'a').length,
      velden: BROK_SIGNAAL.every((z) => z.es && z.w && z.wEn && (z.s === 'a' || z.s === 'g')),
      eersteStapBrok: stap.brok,
      vragen: stap.vragen.length,
      tweeOpties: stap.vragen.every((q) => q.o.length === 2),
      // de patroonstappen erna dragen géén brok, dus die gaan naar het onderwerp
      restZonderBrok: o.stappen.slice(1).every((st) => !st.brok)
    };
  });

  console.log('\n-- de signaalwoorden (brok 9) --');
  ok(s.n === 8, 'acht signaalwoorden (nu: ' + s.n + ')');
  ok(s.a === 4, 'vier naar imperfecto en vier naar indefinido (nu: ' + s.a + ')');
  ok(s.velden === true, 'elk woord heeft een uitleg in beide talen en een geldig bakje');
  ok(s.eersteStapBrok === 'indefimperf.signaal',
    'de stap staat vooraan in het onderwerp en draagt een brok-id (' + s.eersteStapBrok + ')');
  ok(s.vragen === 8 && s.tweeOpties, 'acht vragen, elk met twee bakjes');
  ok(s.restZonderBrok === true, 'CONTROLE: de patroonstappen erna dragen géén brok-id');

  // ---- en het antwoord landt in de goede pot ----
  // Hiervoor is een profiel nodig: gwKies() roept addXP() aan en die schrijft in S.xp, dat pas
  // bestaat zodra er iemand is aangemeld. Alles hierboven is pure data en kan zonder.
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwImp' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  const pot = await page.evaluate(() => {
    S.brok = {}; S.gram = {};
    gwStart('concept-indefimperf', 0);
    gwSess.fase = 'toets';
    const q = gwOnderwerp('concept-indefimperf').stappen[0].vragen[0];
    gwKies(q.g);                       // goed antwoord in de brok-stap
    const naBrok = { brok: Object.keys(S.brok), gram: Object.keys(S.gram) };
    S.brok = {}; S.gram = {};
    gwStart('concept-indefimperf', 1);  // een gewone patroonstap
    gwSess.fase = 'toets';
    const q2 = gwOnderwerp('concept-indefimperf').stappen[1].vragen[0];
    gwKies(q2.g);
    return { naBrok: naBrok, naPatroon: { brok: Object.keys(S.brok), gram: Object.keys(S.gram) } };
  });

  console.log('\n-- elke stap in zijn eigen pot --');
  ok(pot.naBrok.brok.join() === 'indefimperf.signaal',
    'een brok-antwoord landt in S.brok onder zijn eigen id (' + pot.naBrok.brok.join() + ')');
  ok(pot.naBrok.gram.length === 0,
    'en niet in de doos van het onderwerp (nu: ' + pot.naBrok.gram.join() + ')');
  ok(pot.naPatroon.gram.join() === 'indefimperf',
    'CONTROLE: een gewone patroonvraag landt nog steeds in S.gram (' + pot.naPatroon.gram.join() + ')');
  ok(pot.naPatroon.brok.length === 0, 'CONTROLE: en die raakt S.brok niet aan');

  // ---- de ontgrendeling mag niemand terugzetten ----
  // S.conjOpen is een index in CONJ_FASES. Twee fasen ertussen betekent dat index 9 ineens
  // "imperf" aanwijst in plaats van "subjuntivo", en dan raakt een bestaande gebruiker drie fasen
  // kwijt. conjOpenInit zegt in zijn eigen kop dat dat niet mag gebeuren.
  const mig = await page.evaluate(() => {
    const uit = {};
    // Stefans stand op 15 augustus: oude ladder, ontgrendeld tot en met de subjuntivo
    delete S.conjLadder; S.conjOpen = 9; S.conjFase = 'subjuntivo';
    uit.subj = conjFaseNu().id;
    uit.imperfBereikbaar = conjFaseIdx('imperf') <= conjOpenMax();
    // controle: wie pas bij -er was hoort daar te blijven en de ladder niet cadeau te krijgen
    delete S.conjLadder; S.conjOpen = 1; S.conjFase = 'er';
    uit.beginner = conjFaseNu().id;
    uit.beginnerIdx = conjOpenMax();
    // controle: de bovenste blijft de bovenste
    delete S.conjLadder; S.conjOpen = 10; S.conjFase = 'mix';
    uit.top = conjFaseNu().id;
    // controle: een tweede keer draaien mag niet nog eens verschuiven
    const naEen = S.conjOpen;
    conjLadderMigratie(); conjLadderMigratie();
    uit.stabiel = S.conjOpen === naEen;
    return uit;
  });

  console.log('\n-- een update neemt je niets af --');
  ok(mig.subj === 'subjuntivo',
    'wie op de subjuntivo stond staat daar nog steeds (nu: ' + mig.subj + ')');
  ok(mig.imperfBereikbaar === true,
    'en de nieuwe imperfecto-fasen staan meteen open, want ze liggen onder waar hij al stond');
  ok(mig.beginner === 'er' && mig.beginnerIdx === 1,
    'CONTROLE: wie pas bij -er was blijft daar (' + mig.beginner + ', idx ' + mig.beginnerIdx + ')');
  ok(mig.top === 'mix', 'CONTROLE: en de bovenste fase blijft de bovenste');
  ok(mig.stabiel === true, 'CONTROLE: twee keer migreren verschuift niet nog een keer');

  // ---- de doorsteek naar de vormdrill ----
  const door = await page.evaluate(() => ({
    drill: gcOnderwerp('concept-indefimperf').drill,
    anderDrill: gcOnderwerp('concept-serestar').drill
  }));

  console.log('\n-- de knop naar de vormdrill --');
  ok(door.drill === 'imperfecto',
    'het onderwerp draagt een drill, dus het slotscherm krijgt een knop naar de Conjugador (' + door.drill + ')');
  ok(!door.anderDrill, 'CONTROLE: een onderwerp zonder vormdrill krijgt die knop niet');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
