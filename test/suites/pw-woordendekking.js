// pw-woordendekking.js (5 sep, v23.237) — is elk woord op de leesplank op te zoeken?
//
// WAAROM DEZE SUITE ER IS
//
// Stefan, 5 september, met een schermafbeelding van "aspas" uit Don Quijote 4: "dit gaat niet goed,
// de woorden van de verhalen worden niet toegevoegd aan het woordenboek."
//
// Nagemeten over alle hoofdstukken: 7900 woorden, 154 missers, 102 verschillende. Franco 0 procent,
// Chispa 0,5, Cultura 3,1, Quijote 4,8. De twee reeksen die er het laatst bij kwamen waren de twee
// met de gaten, en dat is geen toeval: er was niets dat een nieuwe tekst tegenhield.
//
// Dat is wat deze suite doet. Een tekst mag niet op de plank staan als je zijn woorden niet kunt
// opzoeken, en dat is vanaf nu een poortvoorwaarde in plaats van een goede gewoonte.
//
// WAT DEZE SUITE BEWAAKT
//
//   1. NUL MISSERS, over elk hoofdstuk van elke reeks. Geen uitzonderingslijst, ook niet voor de
//      geluiden: pum, shhh en pío staan gewoon in het woordenboek met de uitleg dat het een geluid
//      is. Een uitzonderingslijst is een lijst die groeit.
//   2. DE METING KAN FALEN. Een verzonnen woord in dezelfde meting hoort wél als misser terug te
//      komen. Zonder dit controlegeval zou een kapotte leesBetekenis() die overal iets teruggeeft
//      proef 1 met vlag en wimpel halen.
//   3. NAMEN WORDEN NIET STIEKEM WEGGEREKEND. Ze tellen niet als misser (Sancho hoort niet in een
//      woordenboek) maar ze worden wel geteld, en het aantal blijft klein. Anders is "alles gedekt"
//      te halen door elk lastig woord een hoofdletter te geven.
//   4. DE TWEE REGELS DOEN HET WERK, EN NIET DE DATA. Vastgeplakte voornaamwoorden gaan eraf, en een
//      onbekende vorm wordt teruggebracht tot een infinitief die de app al kent. Gebouwd met woorden
//      die met opzet NIET in de data staan.
//   5. EN ZE VERZINNEN NIETS. Een vorm van een werkwoord dat de app niet kent, hoort een misser te
//      blijven. Dit is de proef die afgaat zodra iemand de infinitief-eis eruit haalt "omdat het dan
//      meer woorden vindt".
//   6. GEEN VORMEN IN DE DATA. Wie een nieuw woord toevoegt, zet de infinitief neer en niet zijn
//      vervoegingen; anders groeit LEES_EXTRA per tekst in plaats van per woord.
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
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwWd' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(900);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(600);
  await page.evaluate(() => { S.lang = 'nl'; try { persist(); } catch (e) {} });

  // ---- 1 t/m 3. de hele plank ----
  console.log('\n-- 1 t/m 3. elk woord van elk hoofdstuk --');
  const dek = await page.evaluate(() => {
    const mis = {}, namen = {}, perReeks = {};
    let tot = 0;
    BOOK.forEach(function (h) {
      const reeks = (LEES_REEKSEN.filter(function (x) { return String(h.id).indexOf(x.pre) === 0; })[0] || {}).id || '?';
      perReeks[reeks] = perReeks[reeks] || { hst: 0, n: 0, mis: 0 };
      perReeks[reeks].hst++;
      const toks = String(h.tekst || '').match(/[A-Za-zÀ-ɏ]+/g) || [];
      toks.forEach(function (w) {
        tot++; perReeks[reeks].n++;
        let bet = null;
        try { bet = leesBetekenis(w); } catch (e) { bet = null; }
        if (bet) return;
        if (/^[A-ZÁÉÍÓÚÑ]/.test(w)) { namen[leesPlat(w)] = 1; return; }
        perReeks[reeks].mis++;
        mis[leesPlat(w)] = (mis[leesPlat(w)] || 0) + 1;
        // waar staat hij, zodat een rode proef meteen bruikbaar is
        if (!mis['_waar']) mis['_waar'] = h.id;
      });
    });
    // het controlegeval: een woord dat zeker niet bestaat, in dezelfde meting
    const verzonnen = ['zqrtplim', 'nglofrastel'].filter(function (w) {
      let b = null; try { b = leesBetekenis(w); } catch (e) { b = null; }
      return b === null;
    });
    const lijst = Object.keys(mis).filter(function (k) { return k !== '_waar'; });
    return { tot: tot, hst: BOOK.length, mis: lijst, waar: mis['_waar'] || null,
             namen: Object.keys(namen).length, verzonnenGemist: verzonnen.length,
             reeksen: Object.keys(perReeks).map(function (k) {
               const x = perReeks[k];
               return { reeks: k, hst: x.hst, n: x.n, mis: x.mis };
             }) };
  });
  dek.reeksen.forEach(function (r) {
    console.log('   ' + String(r.reeks).padEnd(10) + String(r.hst).padStart(3) + ' hst  ' +
      String(r.n).padStart(5) + ' woorden  ' + String(r.mis).padStart(4) + ' missers');
  });
  ok(dek.hst >= 40 && dek.tot >= 7000,
    'CONTROLE: er is echt een plank om te meten (' + dek.hst + ' hoofdstukken, ' + dek.tot + ' woorden)');
  ok(dek.mis.length === 0,
    'elk woord van elk hoofdstuk is op te zoeken' +
      (dek.mis.length ? ' — mist: ' + dek.mis.slice(0, 12).join(', ') + ' (o.a. in ' + dek.waar + ')' : ''));
  ok(dek.verzonnenGemist === 2,
    'CONTROLE: een verzonnen woord komt in dezelfde meting wél als misser terug (' + dek.verzonnenGemist + '/2)');
  ok(dek.namen > 0 && dek.namen < 80,
    'namen tellen niet mee maar worden wel geteld, en het zijn er weinig (' + dek.namen + ')');

  // ---- 4 en 5. de regels, niet de data ----
  console.log('\n-- 4 en 5. de twee regels doen het werk --');
  const regels = await page.evaluate(() => {
    function zoek(w) {
      let b = null; try { b = leesBetekenis(w); } catch (e) { b = null; }
      return b ? { es: b.es, nl: String(b.nl).slice(0, 40), soort: b.soort } : null;
    }
    return {
      // regel A: vastgeplakte voornaamwoorden. Geen van deze staat als vorm in de data.
      inData: ['pedirte', 'imaginarla', 'mandarlo', 'iros', 'fijate', 'curarlo'].filter(function (w) {
        return typeof LEES_EXTRA[w] !== 'undefined';
      }),
      pedirte: zoek('pedirte'),
      imaginarla: zoek('imaginarla'),
      iros: zoek('iros'),
      fijate: zoek('fijate'),
      // regel B: vormen van werkwoorden die wél in de data staan, maar zelf niet
      saludan: zoek('saludan'),
      quemaban: zoek('quemaban'),
      aparecieron: zoek('aparecieron'),
      // en hij verzint niets: een vorm van een werkwoord dat de app niet kent
      onbekend: zoek('zampullaban'),
      onbekend2: zoek('flimbrando'),
      /* De val die de eerste versie van regel B wél in liep. Die hakte een tot zes letters van het
         eind en plakte ar, er of ir erop, en maakte zo van "redondo" een vorm van reír (re + ir).
         Dat viel niet op omdat redondo toevallig in de lijst staat, maar het volgende onbekende
         woord dat met "re" begint zou "lachen" hebben betekend. */
      redondo: zoek('redondo'),
      valstrik: (function () {
        let r = null; try { r = leesNaarInfinitief('rezumbroso'); } catch (e) { r = null; }
        let r2 = null; try { r2 = leesNaarInfinitief('cabecero'); } catch (e) { r2 = null; }
        return { rez: r && r.inf, cab: r2 && r2.inf };
      })()
    };
  });
  Object.keys(regels).forEach(function (k) {
    if (k === 'inData') return;
    console.log('   ' + k.padEnd(13) + (regels[k] ? regels[k].es + ' = ' + regels[k].nl : 'GEEN'));
  });
  ok(regels.inData.length === 0,
    'CONTROLE: geen van deze vormen staat als data-regel, dus er valt iets te bewijzen (' +
      (regels.inData.join(', ') || 'geen') + ')');
  ok(!!regels.pedirte && regels.pedirte.es.indexOf('pedir') === 0,
    'pedirte wordt pedir: het voornaamwoord gaat eraf');
  ok(!!regels.imaginarla && regels.imaginarla.es.indexOf('imaginar') === 0, 'imaginarla wordt imaginar');
  ok(!!regels.iros && regels.iros.es.indexOf('ir') === 0, 'iros wordt ir');
  ok(!!regels.fijate, 'fíjate krijgt een antwoord, ook al blijft er na het voornaamwoord geen infinitief over');
  ok(!!regels.saludan, 'saludan vindt saludar zonder dat saludan ergens staat');
  ok(!!regels.quemaban, 'quemaban vindt quemar');
  ok(!!regels.aparecieron, 'aparecieron vindt aparecer');
  ok(regels.onbekend === null && regels.onbekend2 === null,
    'CONTROLE: een vorm van een werkwoord dat de app niet kent blijft een misser, want de regel ' +
    'verzint geen infinitieven');
  ok(!!regels.redondo && /rond/.test(regels.redondo.nl),
    'redondo is rond en geen vorm van reír ("' + (regels.redondo || {}).nl + '")');
  ok(regels.valstrik.rez === undefined || regels.valstrik.rez === null,
    'CONTROLE: een onbekend woord dat met "re" begint wordt geen vorm van reír (' +
      regels.valstrik.rez + ')');
  ok(regels.valstrik.cab === undefined || regels.valstrik.cab === null,
    'CONTROLE: en een onbekend woord dat met "cab" begint geen vorm van caber (' +
      regels.valstrik.cab + ')');

  // ---- 6. geen vormen in de data ----
  console.log('\n-- 6. de data bevat woorden, geen vervoegingen --');
  const vormen = await page.evaluate(() => {
    // Elke sleutel die een vorm blijkt te zijn van een ANDERE sleutel in dezelfde lijst, is werk dat
    // de regel al doet. Historische regels van vóór v23.237 staan er nog; de proef bewaakt dat het
    // er niet méér worden.
    const sleutels = Object.keys(LEES_EXTRA);
    const dubbel = sleutels.filter(function (k) {
      if (k.length < 5) return false;
      let inf = null;
      try { inf = leesNaarInfinitief(k); } catch (e) { inf = null; }
      return !!(inf && typeof LEES_EXTRA[inf.inf] !== 'undefined');
    });
    return { n: sleutels.length, dubbel: dubbel };
  });
  console.log('   ' + vormen.n + ' sleutels, ' + vormen.dubbel.length + ' daarvan zijn een vorm van een andere: ' +
    (vormen.dubbel.join(', ') || 'geen'));
  ok(vormen.dubbel.length === 0,
    'geen enkele sleutel is een vorm van een andere sleutel (' + (vormen.dubbel.join(', ') || 'geen') + ')');

  ok(errs.length === 0, 'geen paginafouten' + (errs.length ? ': ' + errs[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
