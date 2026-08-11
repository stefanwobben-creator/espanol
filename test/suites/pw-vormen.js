// pw-vormen.js (11 aug, v23.48) — geen verzonnen werkwoordsvormen.
//
// Aanleiding: Stefan zag op zijn scherm staan "Todos los días ___ con mi abuela. (Elke dag
// reizende ik met mijn oma.)" Dat was geen typefout maar een sjabloon: twee grammaticaconcepten
// bouwden hun Nederlandse en Engelse vertaling met knip- en plakwerk op de infinitief.
//
//     "Elke dag "+w.nl.replace(/r$/,"")+"de ik ..."   ->  reizen -> "reizende ik"
//     "heb ik veel ge"+w.nl.replace(/en$/,"")+"t."    ->  reizen -> "gereizt"
//     "I "+w.en+"ed a lot."                            ->  eat    -> "eated"
//
// Gemeten voor de reparatie: 90 kapotte Nederlandse en 68 kapotte Engelse vormen, uit 1074
// gegenereerde varianten. Bij "werken" komt er toevallig "gewerkt" uit, en dat is precies waarom
// het zo lang bleef staan: het werkte voor het eerste werkwoord dat je toetste.
//
// Deze suite bewaakt de regel en niet de zinnen. Hij leidt uit GC_PAS zelf af wat een naïeve
// afleiding zou opleveren, gooit weg wat toevallig ook een echte vorm is, en kijkt of die
// verzonnen vormen ergens in de gegenereerde tekst opduiken. Voeg je morgen een werkwoord toe, dan
// doet hij daar vanzelf aan mee.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await b.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));

  await page.goto(U);
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U);
  await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Vorm' + Date.now());
  await page.click('button[data-lvl="A2"]');   // A2 heeft de ruimste bak grammaticaconcepten
  await page.click('#btnNewProf');
  await page.waitForFunction(() => !!(typeof activeProfile === 'function' && activeProfile()),
                             null, { timeout: 20000 });
  await page.waitForTimeout(800);

  console.log('\n-- de vormen staan opgeschreven, niet afgeleid --');
  const velden = await page.evaluate(() => GC_PAS.map(w => ({
    inf: w.inf,
    compleet: !!(w.nlVt && w.nlVd && w.enVt && w.enVd)
  })));
  console.log('  werkwoorden ::', velden.length);
  ok(velden.every(v => v.compleet),
    'elk werkwoord in GC_PAS heeft nlVt, nlVd, enVt en enVd staan' +
    (velden.filter(v => !v.compleet).length ? ' (mist: ' + velden.filter(v => !v.compleet).map(v => v.inf).join(', ') + ')' : ''));

  console.log('\n-- geen enkele gegenereerde zin bevat een verzonnen vorm --');
  const res = await page.evaluate(() => {
    // Wat een naïeve afleiding zou opleveren, minus wat toevallig ook een echte vorm is.
    const verzonnen = [];
    GC_PAS.forEach(w => {
      const echt = {};
      [w.nl, w.nlVt, w.nlVd, w.en, w.enVt, w.enVd].forEach(x => { if (x) echt[x] = 1; });
      [
        String(w.nl).replace(/r$/, '') + 'de',
        'ge' + String(w.nl).replace(/en$/, '') + 't',
        'ge' + String(w.nl).replace(/en$/, '') + 'd',
        String(w.en) + 'ed'
      ].forEach(v => { if (!echt[v]) verzonnen.push({ inf: w.inf, vorm: v }); });
    });

    // Alles genereren wat de app kan tonen, uit alle concepten.
    const zinnen = [];
    GC_CONCEPTEN.forEach(c => {
      (c.patronen || []).forEach((fn, pi) => {
        const gezien = {};
        for (let k = 0; k < 200; k++) {
          let q = null;
          try { q = fn(); } catch (e) { break; }
          if (!q) continue;
          const sl = String(q.v) + '|' + String(q.vEn);
          if (gezien[sl]) continue;
          gezien[sl] = 1;
          zinnen.push({ c: c.id, p: pi, t: [q.v, q.vEn, q.w, q.wEn].filter(Boolean).join(' ~ ') });
        }
      });
    });

    const treffers = [];
    zinnen.forEach(z => {
      verzonnen.forEach(v => {
        if (new RegExp('\\b' + v.vorm + '\\b').test(z.t)) {
          treffers.push({ c: z.c, p: z.p, vorm: v.vorm, inf: v.inf, zin: z.t.slice(0, 90) });
        }
      });
    });
    return { varianten: zinnen.length, verzonnen: verzonnen.map(v => v.vorm), treffers: treffers };
  });
  console.log('  varianten ::', res.varianten, '· vormen die niet mogen voorkomen ::', res.verzonnen.join(', '));
  res.treffers.slice(0, 8).forEach(t => console.log('    ✗ ' + t.c + ' p' + t.p + ' :: "' + t.vorm + '" in "' + t.zin + '"'));
  ok(res.varianten > 500, 'er is genoeg gegenereerd om iets te kunnen zeggen (' + res.varianten + ')');
  ok(res.treffers.length === 0,
    'geen enkele naïef afgeleide vorm komt voor (' + res.treffers.length + ' treffers)');

  console.log('\n-- het patroon met een lijdend voorwerp trekt alleen uit werkwoorden die dat kunnen --');
  const obj = await page.evaluate(() => {
    const c = GC_CONCEPTEN.filter(x => x.id === 'indefimperf')[0];
    const gezien = {};
    // *hablé algo increíble* en *viajé algo increíble* zijn geen Spaans. Oefenen op een zin die niet
    // bestaat is erger dan een scheve vertaling, dus dit patroon mag daar niet uit trekken.
    const mag = {};
    GC_PAS.forEach(w => { if (w.obj) mag[w.indef] = 1; });
    const fouten = [];
    (c.patronen || []).forEach(fn => {
      for (let k = 0; k < 200; k++) {
        let q = null;
        try { q = fn(); } catch (e) { break; }
        if (!q || String(q.v).indexOf('algo increíble') === -1) continue;
        if (gezien[q.v]) continue;
        gezien[q.v] = 1;
        (q.o || []).forEach(o => { if (/^[a-záéíóúñ]+[éí]$/.test(o) && !mag[o]) fouten.push(o + ' :: ' + q.v); });
      }
    });
    return { gezien: Object.keys(gezien).length, mag: Object.keys(mag), fouten: fouten };
  });
  console.log('  varianten ::', obj.gezien, '· toegestaan ::', obj.mag.join(', '));
  obj.fouten.slice(0, 5).forEach(f => console.log('    ✗ ' + f));
  ok(obj.gezien > 0, 'het patroon bestaat nog');
  ok(obj.fouten.length === 0,
    'er staat geen onovergankelijk werkwoord voor "algo increíble" (' + obj.fouten.length + ')');

  console.log('\n-- "never" staat op zijn Engelse plek --');
  const never = await page.evaluate(() => {
    const c = GC_CONCEPTEN.filter(x => x.id === 'perfindef')[0];
    const uit = { fout: [], goed: 0 };
    (c.patronen || []).forEach(fn => {
      for (let k = 0; k < 200; k++) {
        let q = null;
        try { q = fn(); } catch (e) { break; }
        if (!q || String(q.v).indexOf('Nunca ___ mucho') === -1) continue;
        if (/\(Never I /.test(q.vEn)) uit.fout.push(q.vEn);
        else if (/never/.test(q.vEn)) uit.goed++;
      }
    });
    return uit;
  });
  ok(never.fout.length === 0 && never.goed > 0,
    '"Nunca" wordt "I have never ...", niet "Never I ..." (' + never.goed + ' goed, ' + never.fout.length + ' fout)');

  console.log('\n-- schone console --');
  ok(errs.length === 0, 'geen javascript-fouten onderweg' + (errs.length ? ' :: ' + errs.join(' | ') : ''));

  await b.close();
  console.log(fout === 0 ? '\nPOORT OPEN' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
