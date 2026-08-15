// pw-afleiders.js (15 aug, v23.110) — verklappen de meerkeuzeknoppen het antwoord?
//
// WAAROM DIT ER IS
//
// De meerkeuzevraag zag er zo uit:
//
//     hablar, nosotros, presente
//     [ hablo ] [ hablas ] [ hablamos ] [ habláis ]
//
// De vraag zegt "nosotros", de opties zijn de andere personen van hetzelfde werkwoord. Je zoekt de
// optie op -mos en je bent klaar, zonder ooit naar de stam of de tijd te kijken. Gemeten over alle
// 990 opgaven: 990 keer was de goede optie de enige die bij de gevraagde persoon kón horen.
//
// Stefan, na de vormdril: "ik had alles goed. maar dat is niet goed."
//
// DE REGEL DIE DEZE SUITE BEWAAKT
//
// Elke optie is een vorm van de GEVRAAGDE persoon. Dan draagt de persoonsuitgang geen informatie
// meer. Dat is de kern van learned attention: staat de aanwijzing er al, dan leert het brein de
// uitgang nooit.
//
// DE CONTROLEGEVALLEN
//
//   1. de meting loopt over alle 990 opgaven, niet over een steekproef. Een steekproef mist
//      precies het geval dat je zoekt.
//   2. de check heeft tanden: dezelfde meetfunctie wordt losgelaten op de OUDE manier van
//      afleiders maken. Die moet 990 keer rood geven. Zonder deze controle zou de suite ook groen
//      staan als de meetfunctie stiekem altijd "goed" zegt.
//   3. geen verzonnen vormen. Elke optie moet uit conjVorm() komen. De app heeft ooit zelf
//      werkwoordsvormen zitten bedenken (v23.48); dat mag hier niet terugkomen.
//   4. ook met alleen fase 1 open (presente, geen andere tijd om uit te putten) moeten er vier
//      knoppen zijn. Dat is het pad waar de aanvulling uit andere werkwoorden moet werken.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwAfl' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // ---- 1. alles open: de volle meting over alle opgaven ----
  const alles = await page.evaluate(() => {
    S.conjOpen = CONJ_FASES.length - 1;
    const tijden = conjOpenTijden();

    // Kan deze vorm bij de gevraagde persoon horen, bij welk werkwoord of welke tijd dan ook?
    // Zo niet, dan sluit de persoonsuitgang hem uit en helpt hij je gokken.
    const kanPersoon = (o, p) => tijden.some((t2) => VERBOS.some((v2) => conjVorm(v2, p, t2) === o));
    // Is deze vorm überhaupt een echte vorm uit de tabel, of verzonnen?
    const isEchteVorm = (o) => tijden.some((t2) => VERBOS.some((v2) =>
      conjAlleVormen(v2, t2).indexOf(o) !== -1));

    function meet(maker) {
      let n = 0, verklapt = 0, anderePersoon = 0, accentGelijk = 0, nietVier = 0,
          zonderCorrect = 0, verzonnen = 0;
      const voorbeeld = [];
      tijden.forEach((t) => conjVerbPool(t).forEach((v) => {
        for (let p = 0; p < 6; p++) {
          const correct = conjVorm(v, p, t);
          const opties = maker(v, p, t);
          n++;
          if (opties.length !== 4 || new Set(opties).size !== 4) nietVier++;
          if (opties.indexOf(correct) === -1) zonderCorrect++;
          if (opties.filter((o) => kanPersoon(o, p)).length === 1) {
            verklapt++;
            if (voorbeeld.length < 2) voorbeeld.push(v.inf + '/' + p + '/' + t + ': ' + opties.join(' '));
          }
          opties.forEach((o) => {
            if (o === correct) return;
            for (let q = 0; q < 6; q++) if (q !== p && conjVorm(v, q, t) === o) anderePersoon++;
            if (stripAcc(norm(o)) === stripAcc(norm(correct))) accentGelijk++;
            if (!isEchteVorm(o)) verzonnen++;
          });
        }
      }));
      return { n, verklapt, anderePersoon, accentGelijk, nietVier, zonderCorrect, verzonnen, voorbeeld };
    }

    // de OUDE manier, alleen hier, alleen om te bewijzen dat de meting tanden heeft
    function oudeManier(v, p, t) {
      const vormen = conjAlleVormen(v, t);
      const correct = vormen[p];
      const andere = vormen.filter((vorm, i) => i !== p && vorm !== correct);
      return geschud([correct].concat(geschud(andere).slice(0, 3)));
    }

    return { nu: meet(cjMeerkeuzeOpties), oud: meet(oudeManier), tijden: tijden };
  });

  console.log('\n-- de volle meting, alle opgaven --');
  ok(alles.nu.n === 990, 'alle opgaven gemeten, geen steekproef (' + alles.nu.n + ')');
  ok(alles.nu.verklapt === 0,
    'DE REGEL: geen enkele opgave waar de goede optie de enige is die bij de gevraagde persoon kan horen (nu: ' +
    alles.nu.verklapt + (alles.nu.voorbeeld.length ? ' — ' + alles.nu.voorbeeld[0] : '') + ')');
  ok(alles.nu.anderePersoon === 0,
    'geen enkele afleider is een andere persoon van hetzelfde werkwoord in dezelfde tijd (nu: ' + alles.nu.anderePersoon + ')');
  ok(alles.nu.accentGelijk === 0,
    'geen afleider die alleen in accenten verschilt, want de nakijker telt die als goed (nu: ' + alles.nu.accentGelijk + ')');
  ok(alles.nu.nietVier === 0, 'elke opgave heeft vier verschillende knoppen (mis: ' + alles.nu.nietVier + ')');
  ok(alles.nu.zonderCorrect === 0, 'het goede antwoord staat er altijd bij (mis: ' + alles.nu.zonderCorrect + ')');
  ok(alles.nu.verzonnen === 0,
    'geen verzonnen vormen: elke optie komt uit de tabel (nu: ' + alles.nu.verzonnen + ')');

  console.log('\n-- controle: heeft de meting tanden? --');
  ok(alles.oud.verklapt === alles.oud.n,
    'CONTROLE: de oude manier valt hier ' + alles.oud.n + ' keer door de mand (nu: ' + alles.oud.verklapt + ')');
  ok(alles.oud.anderePersoon > 1000,
    'CONTROLE: en had ' + alles.oud.anderePersoon + ' afleiders uit een andere persoon');
  ok(alles.oud.nietVier > 0,
    'CONTROLE: de oude manier had ook opgaven met minder dan vier knoppen (' + alles.oud.nietVier + ')');

  // ---- 2. het smalle pad: alleen fase 1 open, dus geen andere tijd om uit te putten ----
  const smal = await page.evaluate(() => {
    S.conjOpen = 0; S.conjFase = CONJ_FASES[0].id;
    const t = 'presente';
    let n = 0, nietVier = 0, verklapt = 0, andereTijd = 0;
    const tijden = conjOpenTijden();
    const kanPersoon = (o, p) => VERBOS.some((v2) => conjVorm(v2, p, t) === o);
    conjVerbPool(t).forEach((v) => {
      for (let p = 0; p < 6; p++) {
        const opties = cjMeerkeuzeOpties(v, p, t);
        n++;
        if (opties.length !== 4 || new Set(opties).size !== 4) nietVier++;
        if (opties.filter((o) => kanPersoon(o, p)).length === 1) verklapt++;
        // met alleen presente open mag er geen vorm uit een andere tijd tussen zitten
        opties.forEach((o) => {
          if (['indefinido', 'imperfecto', 'perfecto', 'subjuntivo'].some((t2) =>
            VERBOS.some((v2) => conjVorm(v2, p, t2) === o) &&
            !VERBOS.some((v2) => conjVorm(v2, p, t) === o))) andereTijd++;
        });
      }
    });
    return { n, nietVier, verklapt, andereTijd, tijden: tijden };
  });

  console.log('\n-- het smalle pad: alleen fase 1 open --');
  ok(JSON.stringify(smal.tijden) === '["presente"]', 'met fase 1 open staat alleen het presente open (' + smal.tijden.join(', ') + ')');
  ok(smal.n > 0 && smal.nietVier === 0,
    'ook zonder andere tijd om uit te putten zijn er vier knoppen (' + smal.n + ' opgaven, ' + smal.nietVier + ' mis)');
  ok(smal.verklapt === 0, 'en ze verklappen nog steeds niets (nu: ' + smal.verklapt + ')');
  ok(smal.andereTijd === 0,
    'geen afleider uit een tijd die je nog niet open hebt: dat zou ruis zijn, geen tegenstelling (nu: ' + smal.andereTijd + ')');

  // ---- 3. het scherm doet het nog ----
  await page.evaluate(() => {
    S.conjOpen = CONJ_FASES.length - 1; S.rvDrill = 1;
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.conj = 'makkelijk';
    conjRonde = null; conjIdx = null; cjMk = null;
    funView = 'conj'; renderFun();
  });
  await page.waitForTimeout(400);
  const scherm = await page.evaluate(() => {
    const knoppen = Array.prototype.map.call(document.querySelectorAll('#cjOpties button'), (b) => b.innerText.trim());
    return { n: knoppen.length, uniek: new Set(knoppen).size, bevatGoed: knoppen.indexOf(conjVorm(conjIdx.verb, conjIdx.p, conjIdx.t || 'presente')) !== -1 };
  });

  console.log('\n-- het scherm --');
  ok(scherm.n === 4 && scherm.uniek === 4, 'er staan vier verschillende knoppen op het scherm (' + scherm.n + '/' + scherm.uniek + ')');
  ok(scherm.bevatGoed === true, 'en het goede antwoord staat erbij');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
