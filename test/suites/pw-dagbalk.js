// pw-dagbalk.js (2 sep, v23.229) — zegt de balk bovenin waar je les staat én waar je doel staat?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 2 sep, over de progress indicator: "daar denk ik is wellicht een ander opzet nog beter,
// bijv dat je kan zien hoever je bent in je dagles maar ook tov je doel."
//
// Er stond "18/30 taco's · 42 dagen". Eén ding, en niet het ding waar je op dat moment in zit. Je
// dagles is wat je opent; je dagdoel is wat de dag sluit. Allebei horen ze op die ene regel.
//
// DE VERDELING DIE ERONDER LIGT
//
// Tijdens een lopende les is deze regel weg (v23.229 verbergt de schil zodra er een les loopt).
// Wat hier staat gaat dus altijd over een les die je gepauzeerd hebt, nog moet beginnen, of vandaag
// al afmaakte. Binnen de les vertelt het lesframe je waar je bent, buiten de les vertelt deze balk
// het. Proef 5 houdt die verdeling vast.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. DRIE TOESTANDEN, EN NIET MEER: les af, les halverwege, les nog te doen. Alle drie gebouwd.
//   2. HET DOEL STAAT ER NAAST, ALTIJD. Anders is het een lesbalk geworden en geen dagbalk.
//   3. HET TOTAAL WORDT NIET MET DE HAND GESCHREVEN. Vier stappen of drie: de regel verandert mee.
//      Dit is de proef die de fout van v23.135 (vier plekken die zelf "4" opschreven) buiten houdt.
//   4. DE BALK ZELF BLIJFT HET DAGDOEL VOLGEN. Twee metingen in één streepje zou geen van beide
//      meten. De les staat in de tekst, het doel in het streepje.
//   5. IN EEN LES IS DE REGEL WEG, en dan draagt het lesframe de stap. CONTROLEGEVAL: zonder dit
//      zou "de les staat in de dagbalk" een tweede plek zijn die hetzelfde zegt.
//   6. HET PAST OP 390 PIXELS, en de balk is niet tot een streepje van niets gekrompen.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(900);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwDb' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);

  // de app start zelf een dagles; die pauzeren we, want anders is de balk verborgen
  await page.evaluate(() => { try { if (document.getElementById('btnLesPauze')) lesFramePauze(); } catch (e) {} });
  await page.waitForTimeout(400);
  await page.evaluate(() => {
    S.lang = 'nl';
    S.doel = 30;
    S.xp[today()] = 15;
    S.dagen = { count: 42, laatst: today() };
    try { persist(); } catch (e) {}
  });

  // één toestand neerzetten en de balk opnieuw laten schrijven
  async function balk(zet) {
    return page.evaluate((z) => {
      const t = today();
      S.lesFlow = {}; S.lesFlowNu = null; lesFlow = null;
      if (z.af) S.lesFlow[t] = true;
      if (z.bezig) S.lesFlowNu = { d: t, stap: z.bezig.stap, stappen: z.bezig.stappen };
      if (z.xp !== undefined) S.xp[t] = z.xp;
      show('lessen', true);
      updateGoalUI();
      const lijn = document.getElementById('goalLine');
      const bar = document.querySelector('.goalbar');
      return {
        txt: (document.getElementById('goalTxt').textContent || '').replace(/\s+/g, ' ').trim(),
        vul: document.getElementById('goalFill').style.width,
        zichtbaar: !!lijn.offsetParent,
        past: lijn.scrollWidth <= lijn.clientWidth + 1,
        barBreed: Math.round(bar.getBoundingClientRect().width),
        lijnBreed: Math.round(lijn.getBoundingClientRect().width)
      };
    }, zet);
  }

  const VIER = ['woorden', 'grammatica', 'toetsjes', 'produceren'];

  // ---- 1 en 2. drie toestanden, en het doel staat er altijd naast ----
  console.log('\n-- 1 en 2. drie toestanden, met het doel ernaast --');
  const nog = await balk({});
  const halve = await balk({ bezig: { stap: 'toetsjes', stappen: VIER } });
  const af = await balk({ af: true });
  const afDoel = await balk({ af: true, xp: 40 });
  [['nog te doen', nog], ['halverwege', halve], ['af', af], ['af + doel', afDoel]]
    .forEach(function (p) { console.log('   ' + p[0].padEnd(12) + '"' + p[1].txt + '"'); });
  ok(/les nog te doen/.test(nog.txt), 'zonder les van vandaag staat er "les nog te doen"');
  ok(/les 3\/4/.test(halve.txt), 'een gepauzeerde les op stap 3 van 4 zegt "les 3/4" (' + halve.txt + ')');
  ok(/les af ✓/.test(af.txt), 'en een afgemaakte les zegt "les af ✓"');
  ok([nog, halve, af].every(function (m) { return /15\/30 taco/.test(m.txt); }),
    'in alle drie de gevallen staat je doel ernaast');
  ok(/doel gehaald ✓/.test(afDoel.txt) && /les af ✓/.test(afDoel.txt),
    'en les af en doel gehaald zijn twee losse dingen (' + afDoel.txt + ')');
  ok([nog, halve, af].every(function (m) { return /42 dagen/.test(m.txt); }),
    'de dagenteller staat er nog gewoon bij');

  // ---- 3. het totaal komt niet uit een vinger ----
  console.log('\n-- 3. het totaal komt uit de stappenlijst en niet uit een vinger --');
  const drie = await balk({ bezig: { stap: 'toetsjes', stappen: ['woorden', 'toetsjes', 'produceren'] } });
  const zes = await balk({ bezig: { stap: 'toetsjes', stappen: ['woorden', 'grammatica', 'vormen', 'toetsjes', 'input', 'produceren'] } });
  console.log('   drie stappen: "' + drie.txt + '"');
  console.log('   zes stappen : "' + zes.txt + '"');
  ok(/les 2\/3/.test(drie.txt), 'een les van drie stappen zegt 2/3 (' + drie.txt + ')');
  ok(/les 4\/6/.test(zes.txt), 'CONTROLE: dezelfde stap in een les van zes zegt 4/6 (' + zes.txt + ')');

  // ---- 4. het streepje meet het doel ----
  console.log('\n-- 4. het streepje meet het dagdoel en niet de les --');
  const leeg = await balk({ xp: 0 });
  const half = await balk({ xp: 15 });
  const vol = await balk({ xp: 30 });
  const lesVer = await balk({ xp: 0, bezig: { stap: 'produceren', stappen: VIER } });
  console.log('   0 taco\'s: ' + leeg.vul + ' · 15: ' + half.vul + ' · 30: ' + vol.vul +
              ' · 0 maar les 4/4: ' + lesVer.vul);
  ok(leeg.vul === '0%' && half.vul === '50%' && vol.vul === '100%',
    'de vulling volgt je taco\'s (' + leeg.vul + ', ' + half.vul + ', ' + vol.vul + ')');
  ok(lesVer.vul === '0%' && /les 4\/4/.test(lesVer.txt),
    'CONTROLE: een les die bijna af is vult het streepje niet, want dat meet het doel (' + lesVer.txt + ')');

  // ---- 5. in een les is de regel weg ----
  console.log('\n-- 5. in een les draagt het lesframe de stap, niet deze balk --');
  const tijdens = await page.evaluate(() => {
    show('lessen', true); lesFlowStart();
    return { zichtbaar: !!document.getElementById('goalLine').offsetParent,
             soort: document.body.getAttribute('data-schermsoort'),
             frame: ((document.getElementById('lesFrame') || {}).innerText || '').replace(/\s+/g, ' ').trim() };
  });
  await page.waitForTimeout(600);
  console.log('   ' + JSON.stringify(tijdens));
  ok(!tijdens.zichtbaar && tijdens.soort === 'taak', 'tijdens een les staat de dagbalk er niet');
  ok(/stap 1/i.test(tijdens.frame) || /1\/\d/.test(tijdens.frame),
    'en het lesframe zegt zelf waar je bent ("' + tijdens.frame.slice(0, 70) + '")');
  /* Dit is de scherpste proef van de suite, en hij ging bij het bouwen meteen af. De dagbalk werd
     alleen herschreven als je punten veranderden, dus stond er na het pauzeren nog de stand van
     daarvóór. Vandaar de vergelijking met het lesframe: de balk moet dezelfde stap noemen als het
     frame een tel eerder toonde, en niet een stap uit een vorig leven. */
  const stapFrame = (tijdens.frame.match(/(\d+)\s*\/\s*(\d+)/) || []).slice(1).join('/');
  await page.evaluate(() => { try { lesFramePauze(); } catch (e) {} });
  await page.waitForTimeout(400);
  const naPauze = await page.evaluate(() => ({
    zichtbaar: !!document.getElementById('goalLine').offsetParent,
    txt: (document.getElementById('goalTxt').textContent || '').replace(/\s+/g, ' ').trim()
  }));
  console.log('   het frame zei ' + stapFrame + ' · na pauzeren: "' + naPauze.txt + '"');
  ok(naPauze.zichtbaar, 'CONTROLE: en zodra je pauzeert staat hij er weer');
  ok(!!stapFrame && naPauze.txt.indexOf('les ' + stapFrame) === 0,
    'met dezelfde stap als het lesframe net toonde, en niet met een oude stand ("' + naPauze.txt + '")');

  // ---- 6. het past ----
  console.log('\n-- 6. het past op 390 pixels --');
  const langst = await balk({ bezig: { stap: 'toetsjes', stappen: ['woorden', 'grammatica', 'vormen', 'toetsjes', 'input', 'produceren'] }, xp: 15 });
  console.log('   "' + langst.txt + '" · regel ' + langst.lijnBreed + ' px, streepje ' + langst.barBreed + ' px');
  ok(langst.past, 'de langste regel loopt niet buiten zijn kader');
  ok(langst.barBreed >= 48, 'en het streepje is niet tot niets gekrompen (' + langst.barBreed + ' px)');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
