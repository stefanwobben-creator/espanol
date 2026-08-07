// v19.98: de vaste onderbalk en de verhuisde boekknop. Twee dingen die je alleen ziet als je meet
// waar iets staat, niet of het bestaat: het defect was juist dat de knoppen er wel waren.
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
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await b.newPage({ viewport: { width: 360, height: 780 }, locale: 'nl-NL' });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await nieuwProfiel(page);

  console.log('\n-- versie --');
  const versie = await page.evaluate(() => APP_VERSIE);
  ok(minstens(versie, 'v19.98'), 'versie is minstens v19.98 (nu ' + versie + ')');

  console.log('\n-- de onderbalk: vier vakken, altijd in beeld --');
  const nav = await page.evaluate(() => {
    const n = document.getElementById('nav');
    const r = n.getBoundingClientRect();
    const bs = getComputedStyle(n);
    const knoppen = Array.prototype.map.call(n.querySelectorAll('button'), (b) => ({
      tab: b.getAttribute('data-tab'),
      tekst: b.innerText.replace(/\s+/g, ' ').trim(),
      breed: Math.round(b.getBoundingClientRect().width),
      hoog: Math.round(b.getBoundingClientRect().height)
    }));
    return { pos: bs.position, onder: Math.round(window.innerHeight - r.bottom), scroll: n.scrollWidth > n.clientWidth + 1, knoppen };
  });
  console.log('  ', JSON.stringify(nav.knoppen));
  ok(nav.pos === 'fixed', 'de balk hangt vast aan het scherm');
  ok(nav.onder === 0, 'hij staat tegen de onderrand (afstand ' + nav.onder + 'px)');
  // v21.5: er is een vijfde plek bijgekomen, Oefenen, tussen Woordjes en Spelen.
  ok(nav.knoppen.length === 5, 'precies vijf vakken');
  ok(!nav.scroll, 'er valt niets weg te schuiven, dus niets kan zich verstoppen');
  ok(nav.knoppen.every((k) => k.hoog >= 44), 'elk vak is minstens 44px hoog (duimmaat)');
  ok(nav.knoppen.every((k) => /[A-Za-zÀ-ÿ]{3,}/.test(k.tekst)), 'elk vak heeft een woord, niet alleen een plaatje');
  ok(nav.knoppen.map((k) => k.tab).join(',') === 'lessen,woorden,oefenen,speeltuin,__meer', 'de volgorde is Vandaag, Woordjes, Oefenen, Spelen, Meer');
  ok(!/[—–]|--/.test(nav.knoppen.map((k) => k.tekst).join(' ')), 'geen streepjes in de balk');

  console.log('\n-- de balk blijft staan als je scrollt --');
  await page.evaluate(() => window.scrollTo(0, 1200));
  await page.waitForTimeout(250);
  const naScroll = await page.evaluate(() => {
    const r = document.getElementById('nav').getBoundingClientRect();
    return { onder: Math.round(window.innerHeight - r.bottom), y: Math.round(window.scrollY) };
  });
  ok(naScroll.onder === 0, 'na 1200px scrollen staat hij nog tegen de onderrand');
  await page.evaluate(() => window.scrollTo(0, 0));

  console.log('\n-- de balk ligt nergens over een knop heen --');
  const bedekt = await page.evaluate(() => {
    const nr = document.getElementById('nav').getBoundingClientRect();
    const uit = [];
    ['lessen', 'woorden', 'speeltuin', 'cursus', 'vertalen', 'lezen', 'spiekbrief', 'musica', 'perfil'].forEach((t) => {
      show(t);
      const sec = document.getElementById('tab-' + t);
      Array.prototype.forEach.call(sec.querySelectorAll('button, a, input'), (el) => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return;
        // een element ligt onder de balk als het midden ervan binnen de balk valt
        const my = r.top + r.height / 2;
        if (my > nr.top && my < nr.bottom && r.left < nr.right && r.right > nr.left) {
          const mx = r.left + r.width / 2;
          if (document.elementFromPoint(mx, my) !== el && !el.contains(document.elementFromPoint(mx, my))) {
            uit.push(t + ' :: ' + (el.id || el.textContent || el.tagName).toString().slice(0, 40));
          }
        }
      });
    });
    show('lessen');
    return uit;
  });
  console.log('  bedekt ::', bedekt.length ? bedekt.join(' | ') : 'niets');
  ok(bedekt.length === 0, 'geen enkele knop op negen schermen ligt onder de balk');

  console.log('\n-- de zoekknop staat in de kop, niet meer over het scherm --');
  const fab = await page.evaluate(() => {
    const f = document.getElementById('dicFab');
    const bs = getComputedStyle(f);
    return { pos: bs.position, inKop: !!f.closest('header'), zichtbaar: f.offsetParent !== null, br: Math.round(f.getBoundingClientRect().width) };
  });
  ok(fab.pos !== 'fixed', 'de zoekknop hangt niet meer vast aan het scherm');
  ok(fab.inKop, 'hij staat in de kop');
  ok(fab.zichtbaar, 'en hij is gewoon zichtbaar');
  // v21.6: was een rond boekicoontje van 38px, is nu een pil met het woord "Zoek" erin, dus breder.
  ok(fab.br >= 32 && fab.br <= 140, 'hij heeft kopformaat (' + fab.br + 'px)');
  await page.click('#dicFab'); await page.waitForTimeout(400);
  ok(await page.evaluate(() => { const w = document.getElementById('zoekWrap'); return !!w && !w.classList.contains('hidden'); }), 'hij opent het zoekveld');
  ok(await page.evaluate(() => { const v = document.getElementById('zoekVeld'); return !!v && document.activeElement === v; }), 'met de cursor er meteen in');
  await page.evaluate(() => zoekSluit());

  console.log('\n-- Meer: elke tab is bereikbaar en elke regel legt zichzelf uit --');
  await page.click("#nav button[data-tab='__meer']"); await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot-v1998-meer.png' });
  const meer = await page.evaluate(() => {
    const l = document.getElementById('meerLijst');
    return {
      rijen: Array.prototype.map.call(l.querySelectorAll('[data-meer]'), (b) => ({
        id: b.getAttribute('data-meer'),
        kop: b.querySelector('b').textContent,
        uit: b.querySelector('b + span').textContent
      })),
      stop: document.getElementById('meerStop').textContent
    };
  });
  console.log('  ', meer.rijen.map((r) => r.id).join(','));
  // wat via Oefenen te bereiken is telt net zo goed mee als wat in de balk of onder Meer staat
  const viaOefenen = await page.evaluate(() => oefenItems().map((o) => o.id));
  const bereikbaar = meer.rijen.map((r) => r.id).concat(['lessen', 'woorden', 'oefenen', 'speeltuin']).concat(viaOefenen);
  const alleTabs = await page.evaluate(() => TABS.filter((t) => ['steun', 'privacy', 'toetsjes'].indexOf(t.id) === -1).map((t) => t.id));
  ok(alleTabs.every((t) => bereikbaar.indexOf(t) !== -1), 'elke tab is via de balk of via Meer te bereiken');
  ok(meer.rijen.every((r) => r.kop.length > 1 && r.uit.length > 15), 'elke regel heeft een naam en een uitleg');
  ok(/[Ss]toppen mag altijd/.test(meer.stop), 'er staat dat stoppen altijd mag');
  ok(!/[—–]|--/.test(JSON.stringify(meer)), 'geen streepjes in het Meer-blad');

  console.log('\n-- Meer brengt je er ook echt heen en licht dan op --');
  // spiekbrief is naar Oefenen verhuisd, dus hier nemen we cursus als proef op de som
  await page.click("[data-meer='cursus']"); await page.waitForTimeout(500);
  const na = await page.evaluate(() => ({
    open: !document.getElementById('tab-cursus').classList.contains('hidden'),
    blad: document.getElementById('meerWrap').classList.contains('hidden'),
    actief: Array.prototype.filter.call(document.querySelectorAll('#nav button'), (b) => b.classList.contains('active')).map((b) => b.getAttribute('data-tab'))
  }));
  ok(na.open, 'Cursus staat open');
  ok(na.blad, 'het blad is dicht');
  ok(na.actief.join(',') === '__meer', 'Meer licht op, en alleen Meer');

  await page.evaluate(() => show('woorden')); await page.waitForTimeout(300);
  ok(await page.evaluate(() => Array.prototype.filter.call(document.querySelectorAll('#nav button'), (b) => b.classList.contains('active')).map((b) => b.getAttribute('data-tab')).join(',')) === 'woorden', 'terug bij Woordjes licht Woordjes op');
  await page.screenshot({ path: 'shot-v1998-woorden.png' });

  console.log('\n-- Engels profiel: de balk praat mee --');
  await page.evaluate(() => { S.lang = 'en'; try { persist(); } catch (e) {} buildNav(); });
  await page.waitForTimeout(300);
  const en = await page.evaluate(() => document.getElementById('nav').innerText.replace(/\s+/g, ' ').trim());
  console.log('  ', en);
  ok(/Today/.test(en) && /Words/.test(en) && /Play/.test(en) && /More/.test(en), 'de vier woorden staan in het Engels');
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} buildNav(); });

  console.log('\n-- Grammatica toont geen enkel onderwerp twee keer --');
  await page.evaluate(() => show('spiekbrief')); await page.waitForTimeout(500);
  const gram = await page.evaluate(() => {
    const el = document.getElementById('cheat');
    const titels = Array.prototype.map.call(el.querySelectorAll('[data-gwstart] b, #spiekNaslag details summary'), (e) => e.textContent.trim());
    const dubbel = titels.filter((t, i) => titels.indexOf(t) !== i);
    // de naslaglijst mag alleen bestaan als er spiekbrieven zijn waar geen onderwerp bij hoort
    let wees = 0;
    CHEATSHEET.forEach((c, i) => { if (!gwOnderwerpVoorSpiek(i)) wees++; });
    return { dubbel, wees, naslag: !!document.getElementById('spiekNaslag'), tekst: el.innerText };
  });
  console.log('  weesspiekbrieven ::', gram.wees, '· naslaglijst ::', gram.naslag);
  ok(gram.dubbel.length === 0, 'geen titel staat er twee keer (' + gram.dubbel.join(', ') + ')');
  ok(gram.naslag === (gram.wees > 0), 'de naslaglijst staat er alleen als er iets in staat');
  ok(!/rechtsonder|bottom right/.test(gram.tekst), 'geen tekst wijst nog naar de oude plek van de boekknop');

  console.log('\n-- het profielscherm houdt de balk en de boekknop weg --');
  await page.evaluate(() => renderProfileScreen());
  await page.waitForTimeout(400);
  const prof = await page.evaluate(() => ({
    nav: document.getElementById('nav').classList.contains('hidden'),
    fab: document.getElementById('dicFab').classList.contains('hidden')
  }));
  ok(prof.nav, 'geen tabbalk op het profielscherm');
  ok(prof.fab, 'geen zoekknop op het profielscherm');

  console.log('\nPAGE ERRORS:', errs);
  ok(errs.length === 0, 'geen js-fouten');
  console.log(fout ? '\n*** ' + fout + ' FOUT ***' : '\nALLES GROEN');
  await b.close();
  process.exit(fout ? 1 : 0);
})();
