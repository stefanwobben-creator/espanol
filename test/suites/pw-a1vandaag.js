// v19.99: de A1-balk op Vandaag. Het verhaal was één zin: op het eerste scherm hoort te staan wat
// je kunt, niet alleen hoe vaak je kwam. Deze suite meet dat als volgordekwestie, niet als
// aanwezigheidskwestie: de balk bestond al, hij stond alleen op de verkeerde plek.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

// Niet gelijk aan maar minstens. Acht suites zijn eerder rood geworden puur omdat het versienummer
// een keer omhoog ging; een suite hoort te breken als het gedrag verandert, niet als de teller loopt.
function minstens(nu, vanaf) {
  const p = (v) => (v || '').replace(/^v/, '').split('.').map(Number);
  const [a, b] = [p(nu), p(vanaf)];
  return a[0] > b[0] || (a[0] === b[0] && a[1] >= b[1]);
}

async function nieuwProfiel(page) {
  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Test' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    var w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
  await page.waitForTimeout(200);
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 360, height: 780 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await nieuwProfiel(page);

  console.log('\n-- versie --');
  const versie = await page.evaluate(() => APP_VERSIE);
  ok(minstens(versie, 'v19.99'), 'versie is minstens v19.99 (nu ' + versie + ')');

  console.log('\n-- de balk telt alleen wat gecheckt is (v20.0) --');
  const zonderVinkje = await page.evaluate(() => {
    const map = pcicMap(), niv = pcicNiv();
    let id = null;
    for (const k in map) {
      if ((map[k] || []).some((sleutel) => niv[sleutel] === 'A1') && !(S.srs || {})[k]) { id = k; break; }
    }
    if (!id) return { fout: 'geen ongeoefend A1-woord gevonden' };
    S.srs = S.srs || {};
    S.srs[id] = { box: stevigDrempel(), due: '2020-01-01' };   // bovenste doos, geen check
    const zonder = voortgangTellers();
    S.srs[id].k = 1;
    const met = voortgangTellers();
    delete S.srs[id];
    return { zonder: zonder.dek.A1 || 0, met: met.dek.A1 || 0, bijna: zonder.bijna };
  });
  ok(!zonderVinkje.fout, 'er is een A1-woord om mee te testen');
  ok(zonderVinkje.met === zonderVinkje.zonder + 1,
    'hetzelfde woord telt wel mee mét het vinkje (' + zonderVinkje.zonder + ' -> ' + zonderVinkje.met + ')');

  // v20.1: de balk verschijnt pas als er iets onderweg is en de staafjes pas vanaf twee dagen.
  // Deze suite gaat over de plaatsing, dus zetten we die context eerst neer; dat de blokken
  // wegblijven als de context er niet is, staat in pw-context.js.
  await page.evaluate(() => {
    const map = pcicMap(), niv = pcicNiv(), t = today();
    let gezet = 0;
    for (const k in map) {
      if (gezet >= 2) break;
      if ((map[k] || []).some((sleutel) => niv[sleutel] === 'A1') && !(S.srs || {})[k]) {
        S.srs[k] = { box: 3, due: addDays(t, 3), n: 3 }; gezet++;
      }
    }
    S.xp[t] = (S.xp[t] || 0) + 12;
    S.xp[addDays(t, -1)] = 12;
    try { persist(); } catch (e) {}
  });

  console.log('\n-- de balk staat op Vandaag --');
  await page.evaluate(() => show('lessen'));
  await page.waitForTimeout(500);
  const er = await page.evaluate(() => {
    const b = document.getElementById('dagBasisBalk');
    if (!b) return null;
    const kaart = b.closest('.card');
    const r = b.getBoundingClientRect();
    return { kaart: kaart ? kaart.id : '', breed: Math.round(r.width), hoog: Math.round(r.height) };
  });
  ok(!!er, 'er staat een A1-balk op het dagscherm');
  ok(er && er.kaart === 'lijnKaart', 'hij zit in de kaart die er al was, er is geen blok bijgekomen');
  ok(er && er.breed > 100 && er.hoog > 4, 'hij is echt zichtbaar (' + (er ? er.breed + 'x' + er.hoog : '-') + ')');

  console.log('\n-- wat je kunt staat boven hoe vaak je kwam --');
  const volgorde = await page.evaluate(() => {
    const b = document.getElementById('dagBasisBalk');
    const strook = document.querySelector('#lijnKaart .lijnstrook');
    if (!b || !strook) return null;
    return { basis: Math.round(b.getBoundingClientRect().top), habit: Math.round(strook.getBoundingClientRect().top) };
  });
  ok(!!volgorde, 'de veertiendaagse strook staat in dezelfde kaart');
  ok(volgorde && volgorde.basis < volgorde.habit,
    'de A1-balk staat boven de staafjes (' + (volgorde ? volgorde.basis + ' vs ' + volgorde.habit : '-') + ')');

  console.log('\n-- de balk zegt hetzelfde als de voortgangspagina --');
  const cijfers = await page.evaluate(() => {
    const t = voortgangTellers();
    const tekst = document.getElementById('lijnKaart').innerText;
    return { dek: t.dek.A1 || 0, noemer: PCIC_NOEMER.A1, tekst: tekst.replace(/\s+/g, ' ') };
  });
  ok(cijfers.noemer === 390, 'de noemer is de 390 A1-eenheden van het Cervantes');
  ok(cijfers.tekst.indexOf(' van de ' + cijfers.noemer + ' A1-woorden staan stevig') !== -1,
    'de zin noemt de noemer erbij: ' + cijfers.tekst.slice(0, 90));
  ok(cijfers.tekst.indexOf(String(cijfers.dek)) !== -1,
    'de teller in de zin (' + cijfers.dek + ') komt uit voortgangTellers, niet uit een eigen sommetje');

  console.log('\n-- geen tempo, geen einddatum, op dit scherm --');
  const tekst = await page.evaluate(() => document.getElementById('lijnKaart').innerText);
  ok(!/(week|weken|maand|maanden|klaar in|over \d)/i.test(tekst),
    'er staat geen belofte over wanneer A1 vol is');
  ok(!/[—–]|--/.test(tekst), 'geen streepjes in de kaart');

  console.log('\n-- hij verandert mee als je iets leert --');
  const na = await page.evaluate(() => {
    const voor = document.getElementById('lijnKaart').innerText.match(/(\d+) van de/);
    // stevig = de bovenste box (vijf goede beurten over 25 dagen). Hier rechtstreeks gezet op een
    // woord waarvan de Cervantes-sleutel op A1 staat, want 25 dagen wachten kan een test niet.
    // v20.0: de bovenste box telt alleen mee met k:1, het vinkje van de check die je niet zelf
    // beoordeelt. Zonder dat vinkje is dit precies het geval dat de balk niet meer mag tellen.
    const map = pcicMap(), niv = pcicNiv();
    let id = null;
    for (const k in map) {
      if ((map[k] || []).some((sleutel) => niv[sleutel] === 'A1') && !(S.srs || {})[k]) { id = k; break; }
    }
    if (!id) return { fout: 'geen ongeoefend A1-woord gevonden in de mapping' };
    S.srs = S.srs || {};
    S.srs[id] = { box: stevigDrempel(), due: '2020-01-01', k: 1 };
    try { persist(); } catch (e) {}
    renderLessons();
    const nu = document.getElementById('lijnKaart').innerText.match(/(\d+) van de/);
    return { voor: voor ? Number(voor[1]) : -1, nu: nu ? Number(nu[1]) : -1 };
  });
  console.log('   ', JSON.stringify(na));
  ok(!na.fout, 'er is een A1-woord om mee te testen');
  ok(na.nu > na.voor, 'een woord dat stevig wordt, laat de teller stijgen (' + na.voor + ' -> ' + na.nu + ')');

  console.log('\n-- de oude plek werkt nog steeds --');
  await page.evaluate(() => show('perfil'));
  await page.waitForTimeout(500);
  const opProfiel = await page.evaluate(() => /A1/.test(document.body.innerText) && !!document.querySelector('.bar.duo'));
  ok(opProfiel, 'op Profiel staan de niveaubalken nog gewoon');

  ok(errs.length === 0, 'geen javascriptfouten: ' + errs.slice(0, 3).join(' | '));
  await browser.close();
  console.log(fout ? '\n' + fout + ' PUNT(EN) GEFAALD' : '\nALLES GROEN');
  process.exit(fout ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
