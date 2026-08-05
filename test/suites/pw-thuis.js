// v20.4: vamos hoort op een beginscherm te staan, niet in een adresbalk.
//
// Stefan, 5 augustus: "voel thet a native aan? kan je het toeveogen alsof het een app is".
//
// Het antwoord was nee, en de reden lag niet in de app maar ervoor: elke sessie begon met een adres
// intikken of een tabblad terugvinden. De enige indicator die telt is of hij vrijwillig opnieuw
// opengaat, dus een drempel van drie seconden vóór de eerste tik is duurder dan wat er ook achter
// die tik gebeurt. Deze suite legt vast wat daarvoor nodig is, en vooral ook wat er niet mag.
//
// Wat hier vastligt:
//   1. de kop draagt alles wat een browser nodig heeft om vamos te installeren, en het pictogram
//      is ingebakken: geen los bestand, want de deploy publiceert een expliciete lijst en een
//      pictogram dat niet meegaat is een grijs vierkant op iemands telefoon.
//   2. het manifest wordt bij de start gebouwd met het echte adres erin. Hardgecodeerd zou het op
//      localhost en op het tweede domein buiten scope vallen, en een manifest buiten scope wordt
//      door de browser stilzwijgend geweigerd. Stil falen is het ergste soort falen.
//   3. de uitnodiging om te installeren is contextueel en eindig. Niet op dag een (dan is het
//      reclame voor iets waarvan je nog niet weet of je het wilt), hoogstens drie keer, en weg
//      zodra je hem geïnstalleerd hebt of zegt dat je hem niet wilt.
//   4. de app zelf verandert niet van gedrag door dit alles. Geen console-fouten, geen extra
//      netwerkverkeer, geen scherm dat opeens anders staat.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

async function nieuwProfiel(page) {
  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Thuis' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });
  await page.waitForTimeout(200);
}

async function dagOpnieuw(page) {
  await page.evaluate(() => { scopeLesson = null; show('lessen'); });
  await page.waitForTimeout(350);
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 430, height: 860 } });
  const fouten = [];
  page.on('pageerror', (e) => fouten.push('pageerror: ' + e.message));
  page.on('console', (m) => { if (m.type() === 'error') fouten.push('console.error: ' + m.text()); });

  await nieuwProfiel(page);

  console.log('\n-- 1. de kop draagt het pictogram zelf --');
  const kop = await page.evaluate(() => {
    const meta = (n) => { const e = document.querySelector('meta[name="' + n + '"]'); return e ? e.getAttribute('content') : null; };
    const link = (r) => { const e = document.querySelector('link[rel="' + r + '"]'); return e ? (e.getAttribute('href') || '') : null; };
    return {
      viewport: meta('viewport') || '',
      thema: meta('theme-color'),
      appelKan: meta('apple-mobile-web-app-capable'),
      appelNaam: meta('apple-mobile-web-app-title'),
      appelBalk: meta('apple-mobile-web-app-status-bar-style'),
      appelIcoon: link('apple-touch-icon') || '',
      icoon192: (document.getElementById('icoon192') || {}).href || '',
      manifestEl: !!document.getElementById('manifestLink')
    };
  });
  ok(/viewport-fit=cover/.test(kop.viewport), 'viewport rekt tot in de hoeken (' + kop.viewport + ')');
  ok(kop.thema === '#faf6ef', 'de statusbalk krijgt de kleur van de app (' + kop.thema + ')');
  ok(kop.appelKan === 'yes', 'iOS mag hem zonder browserbalk openen');
  ok(kop.appelNaam === '¡Vamos!', 'en hij heet ¡Vamos! op het beginscherm (' + kop.appelNaam + ')');
  ok(kop.appelBalk !== null, 'de stijl van de statusbalk staat vast');
  ok(kop.appelIcoon.indexOf('data:image/png;base64,') === 0, 'het beginscherm-pictogram zit ingebakken, niet als los bestand');
  ok(kop.appelIcoon.length > 2000, 'en het is een echt plaatje, geen stipje (' + kop.appelIcoon.length + ' tekens)');
  ok(kop.icoon192.indexOf('data:image/png;base64,') === 0, 'het 192-pictogram ook');
  ok(kop.manifestEl === true, 'er staat een manifest-link klaar in de kop');

  console.log('\n-- 2. het manifest wijst naar dít adres, niet naar een adres uit de broncode --');
  const man = await page.evaluate(() => {
    const l = document.getElementById('manifestLink');
    const href = l ? (l.getAttribute('href') || '') : '';
    let json = null;
    try { json = JSON.parse(decodeURIComponent(href.replace(/^data:application\/manifest\+json,/, ''))); } catch (e) {}
    return { href: href.slice(0, 40), json: json, hier: location.origin + location.pathname };
  });
  ok(man.href.indexOf('data:application/manifest+json,') === 0, 'het manifest hangt als data-adres aan de link');
  ok(!!man.json, 'en het is geldige json');
  ok(man.json && man.json.start_url === man.hier, 'start_url is het adres waar je nu staat (' + (man.json || {}).start_url + ')');
  ok(man.json && man.json.start_url.indexOf(man.json.scope) === 0, 'en valt binnen de eigen scope, anders weigert de browser hem');
  ok(man.json && man.json.display === 'standalone', 'hij gaat open zonder browserbalk');
  ok(man.json && man.json.short_name === '¡Vamos!', 'korte naam ¡Vamos! (' + (man.json || {}).short_name + ')');
  ok(man.json && man.json.theme_color === '#faf6ef' && man.json.background_color === '#faf6ef',
     'het opstartscherm heeft dezelfde kleur als de app, dus geen witte flits');
  const icons = (man.json && man.json.icons) || [];
  ok(icons.length === 3, 'drie pictogrammen: 192, 512 en één met veilige marge (' + icons.length + ')');
  ok(icons.every((i) => String(i.src).indexOf('data:image/png;base64,') === 0), 'alle drie ingebakken, dus geen kapotte verwijzing na een deploy');
  ok(icons.some((i) => i.sizes === '192x192') && icons.some((i) => i.sizes === '512x512'), 'de maten die een installatie nodig heeft staan erbij');
  ok(icons.some((i) => i.purpose === 'maskable'), 'en er is er één die tegen een ronde uitsnede kan');

  console.log('\n-- 3. de uitnodiging komt pas als hij ergens op slaat --');
  const dag1 = await page.evaluate(() => ({
    dagen: dagenTotaal(), kaart: !!document.getElementById('thuisKaart'), html: thuisKaartHtml().length
  }));
  ok(dag1.dagen < 3, 'op dag een ben je nog geen drie dagen bezig (' + dag1.dagen + ')');
  ok(dag1.kaart === false && dag1.html === 0, 'dus er staat niets over installeren op je scherm');

  await page.evaluate(() => { S.dagen = { count: 3, last: today() }; try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  const dag3 = await page.evaluate(() => {
    const k = document.getElementById('thuisKaart');
    return { kaart: !!k, tekst: k ? k.innerText.replace(/\s+/g, ' ') : '', teller: S.thuis || 0, knop: !!document.getElementById('btnThuisNee') };
  });
  ok(dag3.kaart === true, 'na drie dagen oefenen staat de uitnodiging er wel');
  ok(/beginscherm/i.test(dag3.tekst), 'en hij zegt waar het over gaat (' + dag3.tekst.slice(0, 70) + ')');
  ok(dag3.knop === true, 'met een knop om hem weg te doen');
  ok(dag3.teller === 1, 'hij is één keer geteld (' + dag3.teller + ')');

  await dagOpnieuw(page);
  const zelfdeDag = await page.evaluate(() => ({ teller: S.thuis || 0, kaart: !!document.getElementById('thuisKaart') }));
  ok(zelfdeDag.teller === 1, 'nog eens kijken op dezelfde dag telt niet dubbel (' + zelfdeDag.teller + ')');

  console.log('\n-- 4. en hij houdt op met vragen --');
  const op = await page.evaluate(() => {
    S.thuis = 3; try { persist(); } catch (e) {}
    return { html: thuisKaartHtml().length, nu: thuisKaartNu() };
  });
  ok(op.html === 0 && op.nu === false, 'na drie keer vragen houdt hij erover op');

  await page.evaluate(() => { S.thuis = 0; S.thuisDag = null; try { persist(); } catch (e) {} });
  await dagOpnieuw(page);
  await page.click('#btnThuisNee');
  await page.waitForTimeout(300);
  const weg = await page.evaluate(() => ({ kaart: !!document.getElementById('thuisKaart'), thuis: S.thuis }));
  ok(weg.kaart === false, '"Niet nodig" haalt hem meteen weg');
  ok(weg.thuis >= 3, 'en hij komt nooit meer terug (' + weg.thuis + ')');

  console.log('\n-- 5. wie hem al geïnstalleerd heeft, krijgt geen reclame voor installeren --');
  const alApp = await page.evaluate(() => {
    S.thuis = 0; S.thuisDag = null; try { persist(); } catch (e) {}
    const echt = window.matchMedia;
    window.matchMedia = (q) => (/standalone/.test(q) ? { matches: true, media: q } : echt.call(window, q));
    const r = { modus: appModus(), html: thuisKaartHtml().length };
    window.matchMedia = echt;
    return r;
  });
  ok(alApp.modus === true, 'de app ziet dat hij vanaf het beginscherm draait');
  ok(alApp.html === 0, 'en vraagt niet of je hem wilt installeren');

  const gewoon = await page.evaluate(() => ({ modus: appModus(), klas: document.documentElement.classList.contains('appmodus') }));
  ok(gewoon.modus === false, 'in een gewoon tabblad staat hij weer uit');
  ok(gewoon.klas === false, 'en de app-opmaak staat dan niet aan');

  console.log('\n-- 6. in app-modus maakt hij zelf ruimte voor de inkeping --');
  const ruimte = await page.evaluate(() => {
    const wrap = document.querySelector('.wrap');
    const voor = getComputedStyle(wrap).paddingTop;
    document.documentElement.classList.add('appmodus');
    const na = getComputedStyle(wrap).paddingTop;
    document.documentElement.classList.remove('appmodus');
    let regel = false;
    for (const blad of document.styleSheets) {
      try {
        for (const r of blad.cssRules) {
          if (r.selectorText === '.appmodus .wrap' && /safe-area-inset-top/.test(r.style.paddingTop)) regel = true;
        }
      } catch (e) {}
    }
    return { voor: voor, na: na, regel: regel };
  });
  // Let op wat dit wel en niet bewijst: een testbrowser heeft geen inkeping, dus env(safe-area-inset-top)
  // is hier 0 en de uitkomst blijft 16px. Wat hier vastligt is dat de regel bestaat, alleen in
  // app-modus geldt, en dat de calc() klopt. Of het op een echte iPhone goed staat, ziet Stefan.
  ok(ruimte.voor === '16px', 'in een tabblad vangt de browserbalk dat op (' + ruimte.voor + ')');
  ok(parseFloat(ruimte.na) >= 16, 'in app-modus rekent de app de inkeping er zelf bij (' + ruimte.na + ')');
  ok(ruimte.regel === true, 'en die regel staat er alleen voor app-modus');

  console.log('\n-- 7. een knop voelt als een knop --');
  const tik = await page.evaluate(() => {
    const b = document.querySelector('#nav button');
    const st = getComputedStyle(b);
    return { kies: st.webkitUserSelect || st.userSelect, raak: st.touchAction, body: getComputedStyle(document.body).overscrollBehaviorY };
  });
  ok(tik.kies === 'none', 'lang drukken selecteert niet het opschrift (' + tik.kies + ')');
  ok(tik.raak === 'manipulation', 'geen wachttijd op dubbeltikken (' + tik.raak + ')');
  ok(tik.body === 'none', 'de pagina veert niet door tot je het grijs erachter ziet (' + tik.body + ')');

  console.log('\n-- 8. en de app doet verder precies wat hij deed --');
  const rest = await page.evaluate(() => {
    const lijst = document.getElementById('lessonList');
    return { start: !!document.getElementById('btnStartLesFlow'), kaarten: lijst ? lijst.querySelectorAll('.card').length : -1 };
  });
  ok(rest.start === true, 'de startknop staat er gewoon');
  ok(rest.kaarten > 0, 'en Vandaag heeft nog steeds inhoud (' + rest.kaarten + ' kaarten)');
  // Dezelfde ruisfilter als de rest van de kern: versie.txt bestaat niet in de testmap en de fetch
  // naar de familieserver wordt door geenserver.js afgebroken. Beide zijn omgeving, geen app.
  const echt = fouten.filter((e) => !/Failed to load resource|Failed to fetch|ERR_TUNNEL_CONNECTION_FAILED|net::/.test(e));
  ok(echt.length === 0, 'geen fouten in de console' + (echt.length ? ': ' + echt.join(' | ') : ''));

  await browser.close();
  console.log(fout === 0 ? '\nALLES GROEN' : '\n' + fout + ' ROOD');
  process.exit(fout === 0 ? 0 : 1);
})();
