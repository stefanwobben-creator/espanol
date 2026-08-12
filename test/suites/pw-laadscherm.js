// pw-laadscherm.js (12 aug, v23.54) — het gordijn gaat open, altijd.
//
// claude/lancering.md punt 2. Gemeten op traag 4G (1,6 Mbit, 300 ms rtt, cpu 4x geremd): de
// statische HTML staat er na ~950 ms, het script is pas na ~13,5 seconden klaar. In dat gat zag je
// "¡Vamos …! Chispa ↑" en verder niets — een pagina die eruitziet alsof hij klaar is en niet
// reageert. Wit had eerlijker geweest.
//
// Deze suite bewaakt niet de teksten van het laadscherm maar de enige eigenschap die er echt toe
// doet: dat het weer weggaat. Een laadscherm is een gordijn dat je voor je eigen app hangt. Blijft
// het hangen, dan heb je de app niet trager gemaakt maar onbruikbaar, en dat is een ergere bug dan
// die we hier oplossen. Er zijn drie wegen naar buiten en alle drie worden hier gelopen:
//
//   1. de normale: boot() of renderProfileScreen() is klaar
//   2. window.onerror: een scriptfout mag geen dode app opleveren
//   3. een noodrem na 30 seconden, ook als er geen fout was
//
// Plus de kop: "¡Vamos …!" met drie puntjes als plaatshouder leest een vreemde als een fout.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM });

  console.log('\n-- het staat er vóór het script klaar is --');
  {
    // Het script tegenhouden is de enige manier om te zien wat de bezoeker in dat gat ziet. Zonder
    // rem is de app in 400 ms klaar en meet je niets.
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
    const page = await ctx.newPage();
    const cdp = await ctx.newCDPSession(page);
    await cdp.send('Network.enable');
    await cdp.send('Network.emulateNetworkConditions', {
      offline: false, latency: 300,
      downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8
    });
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });

    /* v23.55: sinds het vroege proefscherm gaat het gordijn al open zodra de eerste vraag getekend
       is, en dat is rond de 600 ms. Een waitForSelector gevolgd door een evaluate viel daardoor in
       de volle poort tussen wal en schip: het element was er bij de eerste stap en weg bij de
       tweede. Eén lus die alles opneemt terwijl het gebeurt is hier het juiste gereedschap. */
    page.goto(U, { waitUntil: 'commit' }).catch(() => {});
    let gezienGordijn = null, gordijnWegBij = null, tEind = Date.now() + 90000;
    while (Date.now() < tEind) {
      const st = await page.evaluate(() => {
        const el = document.getElementById('laadScherm');
        const r = el ? el.getBoundingClientRect() : null;
        return {
          er: !!el,
          dekt: !!(r && r.width > 300 && r.height > 700),
          js: typeof window.boot === 'function',
          links: document.querySelectorAll('link[rel="stylesheet"]').length,
          proef: document.querySelectorAll('button[data-proef]').length > 0,
          form: !!document.getElementById('btnNewProf') &&
                !document.getElementById('tab-profiel').classList.contains('hidden')
        };
      }).catch(() => null);
      if (st) {
        if (st.er && !gezienGordijn) gezienGordijn = st;
        if (!st.er && gezienGordijn && !gordijnWegBij) { gordijnWegBij = st; break; }
      }
      await new Promise((r) => setTimeout(r, 50));
    }
    ok(!!gezienGordijn, 'het laadscherm staat er');
    ok(gezienGordijn && gezienGordijn.js === false,
      'en het staat er vóórdat het grote script klaar is (dát is het punt)');
    ok(gezienGordijn && gezienGordijn.dekt === true, 'het dekt het scherm af, dus je ziet de dode kop niet meer');
    ok(gezienGordijn && gezienGordijn.links === 0,
      'de stijl komt uit het bestaande blok: geen extra verzoek op een trage lijn');
    ok(!!gordijnWegBij, 'en het gaat weer weg');
    ok(!!(gordijnWegBij && (gordijnWegBij.proef || gordijnWegBij.form)),
      'pas als er iets achter staat: een proefvraag of het aanmeldformulier');
    await ctx.close();
  }

  const page = await b.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });

  console.log('\n-- een scriptfout laat geen gordijn achter --');
  {
    // De eerlijke manier om dit te toetsen: het grote script écht laten omvallen. Een gordijn dat
    // blijft hangen is een ergere bug dan de trage start die we hier oplossen, dus dit hoort niet
    // met een nagespeeld error-event te worden afgedaan.
    const stuk = await b.newPage({ viewport: { width: 390, height: 844 }, locale: 'nl-NL' });
    await stuk.route('**/espanol-stefan.html', async (route) => {
      const res = await route.fetch();
      let html = await res.text();
      const anker = 'var APP_VERSIE = ';
      html = html.replace(anker, 'throw new Error("kapot met opzet"); ' + anker);
      await route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: html });
    });
    const gezien = [];
    stuk.on('pageerror', (e) => gezien.push(e.message));
    await stuk.goto(U);
    /* Wachten tot de fout er echt is, niet 2500 ms gokken. In de volle poort draaien er vier
       browsers naast elkaar en dan haalt deze pagina die 2500 ms niet altijd; de suite was groen
       solo en rood in de poort, en dat is geen test maar een dobbelsteen. */
    const tEind = Date.now() + 90000;
    while (Date.now() < tEind && !gezien.length) await stuk.waitForTimeout(100);
    await stuk.waitForTimeout(700);   // de foutafhandeling ruimt na 400 ms op
    const uit = await stuk.evaluate(() => ({
      gordijn: !!document.getElementById('laadScherm'),
      /* niet op typeof boot toetsen: het hele scriptblok wordt geparseerd voordat er ook maar iets
         draait, dus functiedeclaraties bestaan ook na een throw. Wat er níét is, is alles wat pas
         tijdens het uitvoeren ontstaat. */
      /* Niet op typeof renderProef toetsen — dezelfde valkuil als hieronder, en ik ben er twee keer
         in gelopen: functiedeclaraties worden bij het parsen gehoist en bestaan dus ook na een
         throw. APP_VERSIE is een var waarvan de tóekenning nooit draait, en de profielenlijst wordt
         door renderProfileScreen() gevuld. Allebei alleen waar als het script echt gedraaid heeft. */
      versie: typeof window.APP_VERSIE,
      profiellijst: (document.getElementById('profileList') || { children: [] }).children.length,
      /* v23.55: hier stond dat er dan "geen enkel scherm" is, en dat klopte tot het vroege
         proefscherm er kwam. Nu blijkt er een tweede winst te zitten die niet het doel was: valt het
         grote script om, dan staan de drie proefwoorden er tóch, want die komen uit een eigen blok.
         Een kapotte app is daarmee geen wit scherm meer maar een app die minder kan. */
      vroegScherm: document.querySelectorAll('button[data-proef]').length > 0
    }));
    ok(gezien.some((m) => /kapot met opzet/.test(m)), 'het script viel echt om (' + (gezien[0] || '-') + ')');
    ok(uit.versie === 'undefined' && uit.profiellijst === 0,
      'en de app is daardoor niet opgestart');
    ok(uit.gordijn === false, 'tóch is het laadscherm weg: een scriptfout levert geen dode app op');
    ok(uit.vroegScherm === true,
      'en het vroege proefscherm staat er nog: een vreemde kan zelfs dan zijn eerste woordje leren');
    await stuk.close();
  }

  console.log('\n-- de kop vraagt niet om een naam die er nog niet is --');
  {
    await page.goto(U);
    await page.waitForTimeout(500);
    await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
    await page.reload();
    await page.waitForTimeout(900);
    const voor = await page.evaluate(() => ({
      kop: (document.querySelector('header h1') || {}).textContent || '',
      naam: (document.getElementById('userName') || {}).textContent || ''
    }));
    console.log('  kop vóór aanmelden :: "' + voor.kop.trim() + '"');
    ok(voor.naam === '', 'de naamplek is leeg vóór er een profiel is (was: "…")');
    ok(voor.kop.indexOf('…') === -1, 'er staan geen drie puntjes in de kop');
    ok(/^\s*¡Vamos!\s*$/.test(voor.kop), 'en de kop leest als "¡Vamos!", zonder losse spatie');

    await page.fill('input[placeholder="Naam / Name"], input[placeholder="Naam"], input[placeholder="Name"]', 'Kop' + Date.now());
    await page.click('button[data-lvl="A0"]');
    await page.click('#btnNewProf');
    await page.waitForFunction(() => !!activeProfile(), { timeout: 8000 });
    await page.waitForTimeout(900);
    const na = await page.evaluate(() => ({
      kop: (document.querySelector('header h1') || {}).textContent || '',
      naam: (document.getElementById('userName') || {}).textContent || ''
    }));
    console.log('  kop ná aanmelden   :: "' + na.kop.trim() + '"');
    ok(na.naam.charAt(0) === ' ' && na.naam.trim().length > 0,
      'met een naam zit de spatie aan de naam vast, niet in de HTML');
    ok(/¡Vamos Kop\d+!/.test(na.kop), 'en de kop leest als "¡Vamos Naam!"');
    ok(!/¡Vamos {2,}/.test(na.kop), 'zonder dubbele spatie');
  }

  await b.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
