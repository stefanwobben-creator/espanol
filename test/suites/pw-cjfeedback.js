// Playwright-test voor v19.46: de Conjugador-meerkeuze moet je eigen antwoord in het optieveld zelf
// bevestigen. Stefans melding: "bij vier als ik er een aanvink krijg ik niet echt in het veld zelf
// bevestiging te zien en ik kan ook niet meer controleren, dit lijkt een bug".
const { chromium } = require('playwright');

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
  // v19.48: nieuwe bezoekers krijgen eerst de leer-eerst-proeverij; die slaan we hier over
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(400);
  await page.fill('input[placeholder="Name"]', 'PwCjFb' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(500);
  const skip = page.locator('button:has-text("Skip")');
  if (await skip.count()) await skip.click();
  await page.waitForTimeout(300);

  // meerkeuze forceren (in headless is de UI-taal Engels, dus niet op Nederlandse labels klikken)
  await page.evaluate(() => {
    S.modusKeuze = S.modusKeuze || {}; S.modusKeuze.conj = 'makkelijk';
    S.conjTiempo = 'presente'; persist();
    S.rvDrill = 1; // v21.8: de voordeur van Conjugador is nu het puzzelspel; deze suite test de drill
    funView = 'conj'; conjIdx = null; conjRonde = null; cjMk = null; show('speeltuin');
  });
  await page.waitForTimeout(400);

  ok(await page.locator('#cjOpties .cjOptie').count() === 4, 'meerkeuzemodus toont vier opties');

  // ---------- juist antwoord ----------
  const goed = await page.evaluate(() => conjVorm(conjIdx.verb, conjIdx.p, conjIdx.t || 'presente'));
  const xpVoor = await page.evaluate(() => S.txp || 0);
  await page.click('#cjOpties .cjOptie[data-v="' + goed.replace(/"/g, '\\"') + '"]');
  await page.waitForTimeout(250);

  const gemarkeerd = await page.locator('#cjOpties .cjOptie.primary').count();
  ok(gemarkeerd === 1, 'na het aanvinken is precies één optie gemarkeerd als het juiste antwoord');
  const markTekst = await page.locator('#cjOpties .cjOptie.primary').innerText();
  ok(markTekst.indexOf('✓') !== -1 && markTekst.indexOf(goed) !== -1,
    'die gemarkeerde optie is de gekozen juiste vorm met een vinkje (' + markTekst.trim() + ')');
  ok(await page.locator('#cjOpties .cjOptie.bad').count() === 0, 'bij een goed antwoord wordt niets rood gemarkeerd');
  const alleDisabled = await page.locator('#cjOpties .cjOptie').evaluateAll((els) => els.every((e) => e.disabled));
  ok(alleDisabled, 'alle opties zijn na het antwoord uitgeschakeld');
  ok((await page.locator('#cjFeedback').innerHTML()).length > 0, 'er staat feedback onder de opties');

  // feedback moet BOVEN de doorgaan-knop staan, anders valt die op telefoon onder de fold
  const ordeGoed = await page.evaluate(() => {
    const fb = document.getElementById('cjFeedback');
    const btn = document.getElementById('btnCjSkip');
    if (!fb || !btn) return false;
    return !!(fb.compareDocumentPosition(btn) & Node.DOCUMENT_POSITION_FOLLOWING);
  });
  ok(ordeGoed, 'de feedback staat in de DOM boven de doorgaan-knop, niet eronder');

  const skipPrimary = await page.evaluate(() => {
    const b = document.getElementById('btnCjSkip');
    return b ? b.className.indexOf('primary') !== -1 && b.innerText.indexOf('→') !== -1 : false;
  });
  ok(skipPrimary, 'de doorgaan-knop wordt opvallend (primary) met een pijl zodra je geantwoord hebt');

  const xpNa = await page.evaluate(() => S.txp || 0);
  ok(xpNa - xpVoor === 1, 'een juist meerkeuze-antwoord geeft 1 XP (' + (xpNa - xpVoor) + ')');

  // ---------- tweede klik levert niets extra op ----------
  await page.evaluate(() => {
    const b = document.querySelector('#cjOpties .cjOptie');
    if (b) { b.disabled = false; b.click(); }
  });
  await page.waitForTimeout(200);
  ok(await page.evaluate(() => S.txp || 0) === xpNa, 'nog een keer klikken op een optie levert geen extra XP op');

  // ---------- fout antwoord ----------
  await page.click('#btnCjSkip');
  await page.waitForTimeout(300);
  const info = await page.evaluate(() => {
    const juist = conjVorm(conjIdx.verb, conjIdx.p, conjIdx.t || 'presente');
    const opties = Array.prototype.map.call(document.querySelectorAll('#cjOpties .cjOptie'), function (b) { return b.getAttribute('data-v'); });
    return { juist: juist, fout: opties.filter(function (o) { return o !== juist; })[0] };
  });
  ok(!!info.fout, 'er is een foute optie om te testen (' + info.fout + ')');
  await page.click('#cjOpties .cjOptie[data-v="' + info.fout.replace(/"/g, '\\"') + '"]');
  await page.waitForTimeout(250);

  const foutMark = await page.locator('#cjOpties .cjOptie.bad').innerText();
  ok((await page.locator('#cjOpties .cjOptie.bad').count()) === 1 && foutMark.indexOf('✗') !== -1,
    'jouw foute keuze wordt rood gemarkeerd met een kruisje (' + foutMark.trim() + ')');
  const goedMark = await page.locator('#cjOpties .cjOptie.primary').innerText();
  ok(goedMark.indexOf(info.juist) !== -1 && goedMark.indexOf('✓') !== -1,
    'het juiste antwoord wordt er tegelijk bij gemarkeerd (' + goedMark.trim() + ')');
  ok((await page.locator('#cjFeedback').innerText()).length > 0, 'bij een fout antwoord staat de uitleg ook onder de opties');

  // ---------- typmodus: Enter-spam mag niet dubbel tellen ----------
  await page.click('#btnCjSkip');
  await page.waitForTimeout(250);
  await page.evaluate(() => { S.modusKeuze.conj = 'moeilijk'; persist(); renderFunConjugador(); });
  await page.waitForTimeout(300);
  ok(await page.locator('#cjInput[type="text"]').count() === 1, 'typmodus geeft een tekstveld');
  const goedTyp = await page.evaluate(() => conjVorm(conjIdx.verb, conjIdx.p, conjIdx.t || 'presente'));
  const xpVoorTyp = await page.evaluate(() => S.txp || 0);
  await page.fill('#cjInput', goedTyp);
  await page.click('#btnCjCheck');
  await page.waitForTimeout(250);
  const xpNaTyp = await page.evaluate(() => S.txp || 0);
  ok(xpNaTyp - xpVoorTyp === 3, 'zelf typen geeft 3 XP (' + (xpNaTyp - xpVoorTyp) + ')');
  ok(await page.locator('#btnCjCheck').count() === 0, 'de Controleer-knop verdwijnt na het antwoord, zodat je niet dubbel kunt checken');
  const typtStaatEr = await page.evaluate(() => document.getElementById('cjInput').value);
  ok(typtStaatEr === goedTyp, 'wat je typte blijft in het veld staan als bevestiging (' + typtStaatEr + ')');
  await page.evaluate(() => checkConjugador());
  await page.waitForTimeout(150);
  ok(await page.evaluate(() => S.txp || 0) === xpNaTyp, 'checkConjugador nog eens aanroepen levert geen extra XP op');

  const echte = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));
  ok(echte.length === 0, 'geen JS-fouten in eigen app-code (' + echte.length + ' gevonden, ' + (errors.length - echte.length) + ' netwerkruis genegeerd)');
  if (echte.length) console.log(echte.join('\n'));

  await browser.close();
  console.log(fails === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fails + ' FAILURES');
  process.exit(fails === 0 ? 0 : 1);
})();
