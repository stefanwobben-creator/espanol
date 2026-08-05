// pw-taal.js (31 juli, v19.67) — de taalwacht.
//
// Stefan, 31 juli: "en ik zag in de Engelse tekst nog hardcoded NL teksten".
// Dat klopte, en het was niet één plek: Chispa's pagina, het profielscherm, de muziekpagina,
// de lesdoelen en een handvol toasts spraken Nederlands tegen iemand die de app in het Engels
// had gezet. Losse fouten zijn te repareren; het patroon niet, want elke nieuwe regel tekst kan
// er weer eentje bij zijn. Daarom staat de sweep die ik gebruikte om ze te vinden hier nu als
// test: hij zet een Engels profiel op, loopt elk scherm en elke speeltuinweergave af, en faalt
// zodra hij Nederlandse woorden ziet.
//
// De markerlijst is bewust klein en scherp: alleen woorden die in het Engels of Spaans niet
// voorkomen. "tapas" en "van" stonden er eerst in en zijn eruit gehaald: tapas is in deze app
// gewoon Engels, en "van" is Spaans (ir). Een test die false positives geeft, wordt genegeerd,
// en een genegeerde test is erger dan geen test.
const { chromium } = require('playwright');

// Woorden die in een Engelse UI nooit horen te staan. Geen "je", "dat", "een": die zijn te kort
// en te grabbelig. Dit zijn woorden die alleen Nederlands kunnen zijn.
// De ratel die niet terug mag draaien. Hij telde eerst vragen zonder v.qe, en dat was fout:
// ruim 350 van de 424 toetsvragen zijn Spaanse invuloefeningen (___ / →) die juist nooit een
// Engelse variant mogen krijgen. Zo'n teller eist vertalingen die niet horen te bestaan en zakt
// dus nooit naar nul. Nu telt hij wat het probleem echt was: vragen waarvan de zichtbare tekst,
// dus vraagTekst() plus vraagOpts() op een Engels profiel, nog Nederlands bevat.
const DREMPEL_NL = 0;

const NL = /\b(niet|geen|wordt|werkwoorden|vervoeging(en)?|oefenen|volgende|opnieuw|zinnen|woorden|woordje|woordjes|jouw|jezelf|kiezen|kies|klaar|heerlijk|smult|nieuwe|alleen|samen|verdien(en|t|je)?|krijgt?|krijgen|zoek|nog|welke|hoeveel|elkaar|zodat|omdat|terug|verder|beetje|straks|morgen|vandaag|gisteren|dagen|weken|maanden|neerzetten|smaakt|lekker|vragen|antwoorden|fouten|helaas|jij|jou|deze|zijn|voor|het|ook|dagje|voortgang|instellingen|profiel|volgens|steeds|vaker|minder|meer dan|gewoon)\b/gi;

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push('console.error: ' + msg.text()); });

  let fails = 0;
  function ok(cond, name) {
    if (cond) { console.log('PASS', name); }
    else { fails++; console.log('FAIL', name); }
  }

  await page.goto('http://localhost:8321/espanol-stefan.html');
  await page.waitForTimeout(400);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"], input[placeholder="Naam"]', 'PwTaal' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(600);
  const skip = page.locator('button:has-text("Skip"), button:has-text("Overslaan")');
  if (await skip.count()) await skip.first().click();
  await page.waitForTimeout(400);

  // ---------- 0. staat de app echt in het Engels? ----------
  const lang = await page.evaluate(() => (typeof profLang === 'function' ? profLang() : '?'));
  ok(lang === 'en', 'het testprofiel draait in het Engels (profLang = ' + lang + ')');
  if (lang !== 'en') {
    console.log('  -> zonder Engels profiel zegt de rest van deze test niets; afgebroken');
    await browser.close();
    console.log('\n' + (fails + 1) + ' PLAYWRIGHT-TEST(S) GEFAALD');
    process.exit(1);
  }

  const ctWerkt = await page.evaluate(() => ct('nl-kant', 'en-kant'));
  ok(ctWerkt === 'en-kant', 'ct() geeft de Engelse kant terug (de helper waar alles op leunt)');

  // ---------- 1. elk scherm ----------
  const schermen = ['lessen', 'chispa', 'perfil', 'speeltuin', 'toetsjes', 'woorden',
                    'vertalen', 'lezen', 'spiekbrief', 'privacy', 'steun', 'musica'];
  for (const s of schermen) {
    await page.evaluate((n) => { scopeLesson = null; try { show(n); } catch (e) {} }, s);
    await page.waitForTimeout(300);
    const t = await page.evaluate((n) => {
      const el = document.getElementById('tab-' + n);
      return el ? el.innerText : '(geen tab-' + n + ')';
    }, s);
    keur('scherm ' + s, t);
  }

  // ---------- 2. elke speeltuinweergave ----------
  const funs = ['ws', 'mem', 'kruis', 'dictado', 'conj', 'hu', 'avt'];
  for (const f of funs) {
    const t = await page.evaluate((n) => {
      scopeLesson = null; funView = n;
      try { show('speeltuin'); } catch (e) {}
      try { renderFun(); } catch (e) { return 'RENDERFOUT ' + e.message; }
      const el = document.getElementById('funCard');
      return el ? el.innerText : '(geen funCard)';
    }, f);
    ok(t.indexOf('RENDERFOUT') !== 0, 'speeltuin ' + f + ' rendert zonder fout');
    keur('speeltuin ' + f, t);
  }

  // ---------- 3. de tekstbronnen die de sweep niet ziet ----------
  // Toasts flitsen voorbij en datavelden staan in tabellen; die controleer ik direct.
  const bronnen = await page.evaluate(() => {
    const uit = {};
    uit.petHints = PET_LEVELS.map((l) => petHint(l));
    uit.decos = DAYDECO.map((d) => decoTxt(d));
    uit.fiestas = FIESTAS.map((f) => ct(f.txt, f.txtEn || f.txt));
    uit.shop = SHOP.concat(RINCON).map((i) => itemHint(i));
    uit.amigos = AMIGOS.map((a) => ct(a.frase.nl, a.frase.en || a.frase.nl));
    uit.frases = FRASES.map((f) => ct(f.nl, f.en || f.nl));
    uit.moods = [petMoodText()];
    uit.getal = getal(1234);
    return uit;
  });
  for (const naam of ['petHints', 'decos', 'fiestas', 'shop', 'amigos', 'frases', 'moods']) {
    keur('data ' + naam, (bronnen[naam] || []).join('\n'));
  }
  ok(bronnen.getal === '1,234', 'getallen krijgen Engelse duizendtallen (' + bronnen.getal + ')');

  // ---------- 4. lesdoelen ----------
  const doelen = await page.evaluate(() => tLessons().map((l) => lesDoel(l)).join('\n'));
  keur('lesdoelen', doelen);

  // ---------- 5. de voetnoot (v19.96) ----------
  // Stond als vaste HTML in de pagina en viel dus buiten elke sweep hierboven, want die kijkt
  // alleen in tab-<naam>. Hij staat wel onder elk actiescherm, dus juist die zag je het vaakst.
  const voet = await page.evaluate(() => {
    const f = document.getElementById('appFooter');
    return f ? (f.innerText || '') : '(geen appFooter)';
  });
  keur('voetnoot', voet);
  ok(/Tour/.test(voet) && /Privacy/.test(voet), 'de voetnootlinks staan in het Engels (' + voet.replace(/\s+/g, ' ').trim().slice(0, 70) + ')');

  // ---------- 6. een echte toetsvraag (v19.96) ----------
  // De sweep keek naar het toetsmenu, nooit naar een geopende vraag. Precies daar zat de bug:
  // v.q en v.opts hadden geen Engelse kant, dus de vraag zelf bleef Nederlands.
  const vraagTxt = await page.evaluate(() => {
    try {
      show('toetsjes');
      const b = document.querySelector('#qMenu button[data-qz]') || document.querySelector('#qMenu button');
      if (!b) return '(geen toets te starten)';
      b.click();
      const el = document.getElementById('qCard');
      return el ? el.innerText : '(geen qCard)';
    } catch (e) { return 'RENDERFOUT ' + e.message; }
  });
  ok(vraagTxt.indexOf('RENDERFOUT') !== 0 && vraagTxt.indexOf('(geen') !== 0, 'er opent een toetsvraag om te keuren');
  keur('geopende toetsvraag', vraagTxt);

  // ---------- 7. de data zelf (v19.96, herzien in v19.97) ----------
  // Een steekproef vangt geen 424 vragen; deze telling wel. Hij loopt alle vier de vraagbronnen af
  // en keurt wat de speler daadwerkelijk leest: vraagTekst(v) en vraagOpts(v) op een Engels profiel.
  // Spaanse invulvragen blijven dus gewoon Spaans zonder te klagen, en een half vertaalde vraag
  // (Engelse vraag, Nederlandse opties) valt wel op.
  const gaten = await page.evaluate((bron) => {
    const R = new RegExp(bron, 'gi');
    const uit = { totaal: 0, nl: 0, mismatch: 0, voorbeelden: [] };
    function keurV(v, waar) {
      if (!v || !v.q) return;
      uit.totaal++;
      if (v.opts && v.optse && v.optse.length !== v.opts.length) uit.mismatch++;
      const zicht = [vraagTekst(v)].concat(vraagOpts(v) || []).join(' | ');
      R.lastIndex = 0;
      if (R.test(zicht)) {
        uit.nl++;
        if (uit.voorbeelden.length < 8) uit.voorbeelden.push(waar + ' :: ' + zicht.slice(0, 120));
      }
    }
    (typeof QUIZZES === 'undefined' ? [] : QUIZZES).forEach((qz) => (qz.vragen || []).forEach((v) => keurV(v, 'quiz ' + qz.id)));
    (typeof BOOK === 'undefined' ? [] : BOOK).forEach((h) => (h.vragen || []).forEach((v) => keurV(v, 'boek ' + h.id)));
    (typeof SONGS === 'undefined' ? [] : SONGS).forEach((sg) => (sg.vragen || []).forEach((v) => keurV(v, 'song ' + sg.id)));
    (typeof PLACEMENT === 'undefined' ? [] : PLACEMENT).forEach((v) => keurV(v, 'niveautest'));
    return uit;
  }, NL.source);
  console.log('  toetsvragen: ' + gaten.totaal + ' · met Nederlands in beeld: ' + gaten.nl + ' · scheve optielijst: ' + gaten.mismatch);
  gaten.voorbeelden.forEach((r) => console.log('  -> ' + r));
  ok(gaten.nl <= DREMPEL_NL, 'niet meer dan ' + DREMPEL_NL + ' vragen met Nederlands in beeld (nu ' + gaten.nl + ')');
  ok(gaten.mismatch === 0, 'geen vraag met een optielijst van afwijkende lengte (' + gaten.mismatch + ')');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED|ERR_NAME_NOT_RESOLVED|ERR_CONNECTION_REFUSED/.test(e));
  ok(relevanteErrors.length === 0, 'geen JS-fouten tijdens de hele rondgang (' + relevanteErrors.length + ' gevonden)');
  if (relevanteErrors.length) relevanteErrors.slice(0, 6).forEach((e) => console.log('  ->', e));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fails === 0 ? 0 : 1);

  function keur(naam, tekst) {
    const regels = (tekst || '').split('\n').filter((r) => { NL.lastIndex = 0; return r.trim() && NL.test(r); });
    NL.lastIndex = 0;
    ok(regels.length === 0, 'geen Nederlands in ' + naam);
    regels.slice(0, 8).forEach((r) => console.log('  -> ' + r.trim().slice(0, 140)));
  }
})();
