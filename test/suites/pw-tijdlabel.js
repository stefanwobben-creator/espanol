// pw-tijdlabel.js (24 aug, v23.192) — de toets meet de regel, niet ook nog de vormherkenning
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 24 aug: "het gaat hier meer mis omdat ik de vorm niet herken. Je toetst nu kan ik de regel
// toepassen en de vorm ineen." De vraag die hij liet zien:
//
//   Mientras ___ (esperar) el autobús, ___ (ver) a un viejo amigo.
//     esperaba, vi  |  esperé, vi  |  esperaba, veía
//
// De opties zijn vormen, dus om ze te kunnen lezen moet je al weten dat vi de indefinido van ver is.
// Ken je de regel en herken je die vorm niet, dan is het antwoord onbereikbaar. Vanaf v23.192 staat
// de tijd erbij, afgeleid en niet ingetypt. Zie de leerkaart "de toets die twee dingen tegelijk meet".
//
// WAT DEZE SUITE BEWAAKT, EN WAAROM DE EERSTE PROEF DE BELANGRIJKSTE IS
//
//   1. HET LABEL LIEGT NOOIT. Over álle werkwoorden, álle tijden en álle personen die de app kent:
//      geeft tijdVanVorm() een tijd terug, dan is dat een tijd waar die vorm ook echt bij hoort.
//      Dit is de proef die er het meest toe doet, want een verkeerd label is erger dan geen label.
//   2. En hij zegt niets als het onzeker is. cenamos is tegelijk presente en indefinido; daar hoort
//      geen label te komen. Het controlegeval bij 1: altijd maar iets gokken haalt proef 1 niet,
//      maar een classificatie die de twijfelgevallen wegmoffelt wel.
//   3. DE VRAAG VAN STEFAN krijgt labels, en ze staan bij de goede vorm.
//   4. EEN VRAAG DIE NIET OVER DE TIJD GAAT krijgt er geen. Bij "Indefinido: de juiste vorm" is
//      alles indefinido; een label voegt daar niets toe en leidt af. Tweede controlegeval: labelen
//      is triviaal overal aan te zetten.
//   5. EN ZE STAAN OP HET SCHERM, niet alleen in een functie.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTl' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(500);

  // ---- 1. het label liegt nooit ----
  console.log('\n-- 1. over alles wat de app aan vormen kent --');
  const eerlijk = await page.evaluate(() => {
    const T = ['presente', 'indefinido', 'imperfecto', 'perfecto', 'subjuntivo'];
    let gekeurd = 0, gelabeld = 0;
    const leugens = [];
    VERBOS.forEach(function (v) {
      T.forEach(function (t) {
        for (let pi = 0; pi < 6; pi++) {
          const w = conjVorm(v, pi, t);
          if (!w) continue;
          gekeurd++;
          // welke tijden dragen deze vorm werkelijk?
          const echt = {};
          T.forEach(function (t2) {
            for (let p2 = 0; p2 < 6; p2++) if (conjVorm(v, p2, t2) === w) echt[t2] = 1;
          });
          const gezegd = tijdVanVorm(w, v.inf);
          if (!gezegd) continue;
          gelabeld++;
          if (!echt[gezegd]) leugens.push(v.inf + ' ' + w + ': gezegd ' + gezegd + ', is ' + Object.keys(echt).join('/'));
        }
      });
    });
    return { gekeurd: gekeurd, gelabeld: gelabeld, leugens: leugens };
  });
  console.log('   ' + eerlijk.gekeurd + ' vormen gekeurd, ' + eerlijk.gelabeld + ' gelabeld');
  ok(eerlijk.gekeurd > 600, 'genoeg vormen om iets te betekenen (' + eerlijk.gekeurd + ')');
  ok(eerlijk.gelabeld > eerlijk.gekeurd * 0.5,
    'en meer dan de helft krijgt een label, anders zegt proef 1 weinig (' + eerlijk.gelabeld + ')');
  ok(eerlijk.leugens.length === 0,
    'geen enkel label spreekt de vorm tegen (' + (eerlijk.leugens.slice(0, 3).join(' · ') || 'geen') + ')');

  // ---- 2. en hij zwijgt bij twijfel ----
  console.log('\n-- 2. en hij zwijgt als het onzeker is --');
  const twijfel = await page.evaluate(() => ({
    /* mét én zonder infinitief, want dat zijn twee verschillende takken in tijdVanVorm() en een
       proef die er maar één raakt bewaakt de andere niet. */
    cenamos: tijdVanVorm('cenamos', 'cenar'),      // presente én indefinido
    cenamosKaal: tijdVanVorm('cenamos', null),
    vivimos: tijdVanVorm('vivimos', 'vivir'),      // idem
    vivimosKaal: tijdVanVorm('vivimos', null),
    podria: tijdVanVorm('podría', null),           // condicional, geen imperfecto
    hablare: tijdVanVorm('hablaré', null),         // futuro, geen indefinido
    esperaba: tijdVanVorm('esperaba', 'esperar'),
    espere: tijdVanVorm('esperé', 'esperar'),
    vi: tijdVanVorm('vi', 'ver'),
    veia: tijdVanVorm('veía', 'ver')
  }));
  console.log('   ' + JSON.stringify(twijfel));
  ok(twijfel.cenamos === null && twijfel.vivimos === null,
    'CONTROLE: -amos en -imos blijven ongelabeld, want die zijn presente én indefinido');
  ok(twijfel.cenamosKaal === null && twijfel.vivimosKaal === null,
    'CONTROLE: en ook zonder infinitief, want dat is een andere tak in tijdVanVorm()');
  ok(twijfel.podria === null, 'CONTROLE: podría wordt geen imperfecto (het is condicional)');
  ok(twijfel.hablare === null, 'CONTROLE: hablaré wordt geen indefinido (het is futuro)');
  ok(twijfel.esperaba === 'imperfecto' && twijfel.espere === 'indefinido' &&
     twijfel.vi === 'indefinido' && twijfel.veia === 'imperfecto',
    'en de vier vormen uit Stefans vraag kloppen wel');

  // ---- 3 en 4. welke vragen labels krijgen ----
  console.log('\n-- 3 en 4. welke vragen labels krijgen --');
  const vragen = await page.evaluate(() => {
    const uit = { gelabeld: 0, totaal: 0, perQuiz: {}, stefan: null, gelijkPatroon: [] };
    QUIZZES.forEach(function (qz) {
      let g = 0;
      qz.vragen.forEach(function (v) {
        uit.totaal++;
        const L = vraagTijdLabels(v);
        if (L) {
          g++; uit.gelabeld++;
          if (/esperar/.test(v.q) && /ver/.test(v.q) && !uit.stefan) uit.stefan = { q: v.q, opts: v.opts, L: L };
        } else {
          // gaat deze vraag wél over de tijd maar krijgt hij niets? dat mag, maar we tellen het
        }
      });
      if (g) uit.perQuiz[qz.id] = g + '/' + qz.vragen.length;
    });
    // het controlegeval: een toetsje waarvan alle opties dezelfde tijd dragen
    const q = QUIZZES.filter(function (x) { return x.id === 'q-vormen'; })[0];
    if (q) uit.gelijkPatroon = q.vragen.map(function (v) { return !!vraagTijdLabels(v); });
    return uit;
  });
  console.log('   ' + vragen.gelabeld + ' van de ' + vragen.totaal + ' vragen krijgen labels');
  console.log('   per toetsje: ' + JSON.stringify(vragen.perQuiz));
  ok(vragen.gelabeld >= 40, 'er worden er genoeg gelabeld om verschil te maken (' + vragen.gelabeld + ')');
  ok(Object.keys(vragen.perQuiz).filter(function (k) { return /relatar/.test(k); }).length >= 4,
    'de q-relatar-familie is erbij (' + Object.keys(vragen.perQuiz).filter(function (k) { return /relatar/.test(k); }).join(', ') + ')');
  ok(Object.keys(vragen.perQuiz).some(function (k) { return !/relatar/.test(k); }),
    'CONTROLE: en de regel is generiek, niet op q-relatar getuned (ook: ' +
    Object.keys(vragen.perQuiz).filter(function (k) { return !/relatar/.test(k); }).join(', ') + ')');
  ok(vragen.gelijkPatroon.length > 0 && vragen.gelijkPatroon.every(function (x) { return !x; }),
    'CONTROLE: een toetsje waarvan alle opties dezelfde tijd dragen krijgt geen labels (q-vormen: ' +
    vragen.gelijkPatroon.filter(Boolean).length + ' van de ' + vragen.gelijkPatroon.length + ')');
  if (vragen.stefan) {
    console.log('   Stefans vraag: ' + vragen.stefan.opts.map(function (o, i) {
      return o + ' → ' + vragen.stefan.L[i].join('+');
    }).join('  |  '));
    ok(vragen.stefan.L.length === vragen.stefan.opts.length, 'en Stefans eigen vraag krijgt labels');
  }

  // ---- 5. en ze staan op het scherm ----
  console.log('\n-- 5. op het scherm --');
  const scherm = await page.evaluate(() => {
    // zoek een toetsje met een gelabelde vraag en zet die als eerste
    let doel = null;
    QUIZZES.forEach(function (qz) {
      if (doel) return;
      qz.vragen.forEach(function (v, i) { if (!doel && vraagTijdLabels(v)) doel = { id: qz.id, i: i }; });
    });
    if (!doel) return null;
    show('toetsjes', true);
    startQuiz(doel.id);
    // spoel door tot de gelabelde vraag
    let wacht = 0;
    while (qState.volgorde[qState.i] && qState.volgorde[qState.i].oi !== doel.i && wacht++ < 30) {
      qState.i++; renderQuestion();
    }
    const kaart = document.getElementById('qCard');
    return { html: kaart.innerHTML, labels: kaart.querySelectorAll('.tijdlab').length,
             tekst: (kaart.textContent || '').replace(/\s+/g, ' ').slice(0, 200) };
  });
  ok(scherm && scherm.labels > 0, 'er staan tijdlabels in de knoppen (' + (scherm ? scherm.labels : 0) + ')');
  if (scherm) console.log('   ' + scherm.tekst);

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
