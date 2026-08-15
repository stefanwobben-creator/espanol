// pw-herkomst.js (15 aug, v23.105) — weet de app nog waar je vandaan kwam?
//
// WAAROM DIT ER IS
//
// Er staat een kolom "bron" in tools/terugkomst.sh die precies bedoeld is om een klik uit een
// tijdlijn te scheiden van een link die iemand je persoonlijk stuurde. Die twee zaten daar op één
// hoop, en dat kwam door een volgorde: de app haalt de groepscode uit de adresbalk en veegt de
// zoekreeks weg tijdens het inlezen van het script, terwijl de herkomst pas veel later werd
// gemeten. Nagemeten vóór de reparatie:
//
//     ?van=linkedin              -> "linkedin"      goed
//     ?groep=gtest1              -> "direct"        fout
//     ?groep=gtest1&van=linkedin -> "direct"        fout, de van was ook weg
//
// Herkomst is het soort gegeven dat je niet met terugwerkende kracht kunt repareren. Retentie wel:
// S.xp is een map van datum naar punten, dus wie op dag 2 terugkwam staat er altijd al in. Maar of
// iemand via een uitnodiging binnenkwam is één moment zichtbaar en daarna nooit meer. Vandaar een
// eigen suite, en vandaar dat hij ook de herlaadbeurt nabootst: dat is waar de eerste twee
// reparatiepogingen op stukliepen.
//
// DE CONTROLEGEVALLEN
//
// Een herkomstmeting die overal "uitnodiging" van maakt is net zo groen als een die overal "direct"
// van maakt. Dus: een gewoon bezoek zonder zoekreeks MOET "direct" blijven, en een expliciete
// ?van= moet zwaarder wegen dan de uitnodiging. En de verwijscode mag nooit de sync-code zijn: met
// een sync-code geeft GET /api/state/:code je hele voortgang weg, en dit is een code die je in een
// WhatsApp-groep plakt.
const { chromium } = require('playwright');

const U = 'http://localhost:8321/espanol-stefan.html';

let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }

// Eén compleet bezoek: link openen, rondkijken, herladen, en dan pas aanmelden. Die herlaadbeurt
// staat er met opzet in: na het vegen van de zoekreeks is de link daarna niet meer terug te vinden,
// en zonder bewaren werd "uitnodiging" alsnog "direct".
async function bezoek(browser, zoek) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errs = [];
  let sync = null;
  page.on('pageerror', (e) => errs.push(e.message));
  await page.route('**/api/**', (r) => {
    try {
      const d = r.request().postData();
      if (d && r.request().url().indexOf('/sync') !== -1) sync = JSON.parse(d);
    } catch (e) { /* niet elk verzoek heeft een body */ }
    r.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' });
  });
  await page.goto(U + zoek);
  await page.waitForTimeout(500);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.reload();
  await page.waitForTimeout(700);
  await page.fill('input[placeholder="Name"]', 'PwHerk' + Date.now());
  await page.click('button:has-text("A2")');
  await page.click('button:has-text("Start")');
  await page.waitForTimeout(1200);
  const uit = await page.evaluate(() => ({
    bron: S.bron, via: viaNu(), rcode: mijnVerwijsCode(),
    synccode: (activeProfile() || {}).code,
    groepslink: groepLink({ gcode: 'g999' }),
    duellink: duelLink({ id: 'd999' })
  }));
  uit.sync = sync; uit.errs = errs;
  await ctx.close();
  return uit;
}

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });

  const li = await bezoek(browser, '?van=linkedin');
  const groep = await bezoek(browser, '?groep=gtest1');
  const beide = await bezoek(browser, '?groep=gtest1&van=linkedin');
  const metVia = await bezoek(browser, '?groep=g1&v=abc123def');
  const kaal = await bezoek(browser, '');
  const duel = await bezoek(browser, '?duel=d1');

  console.log('\n-- waar kwam je vandaan --');
  ok(li.bron === 'linkedin', 'een ?van=-link levert die naam op (nu: ' + li.bron + ')');
  ok(groep.bron === 'uitnodiging',
    'een uitnodigingslink heet "uitnodiging" en niet "direct" (nu: ' + groep.bron + ')');
  ok(duel.bron === 'uitnodiging', 'een duel-uitnodiging ook (nu: ' + duel.bron + ')');
  ok(beide.bron === 'linkedin',
    'staat er allebei iets, dan wint de expliciete ?van= (nu: ' + beide.bron + ')');

  console.log('\n-- de controlegevallen --');
  ok(kaal.bron === 'direct',
    'CONTROLE: een gewoon bezoek zonder zoekreeks blijft "direct" (nu: ' + kaal.bron + ')');
  ok(li.via === null && kaal.via === null,
    'CONTROLE: zonder ?v= in de link is er geen verwijzer (nu: ' + li.via + ' / ' + kaal.via + ')');

  console.log('\n-- wie heeft je binnengehaald --');
  ok(metVia.via === 'abc123def', 'de verwijscode uit de link wordt onthouden (nu: ' + metVia.via + ')');
  ok(!!metVia.sync && metVia.sync.via === 'abc123def',
    'en gaat mee naar de server bij het synchroniseren (nu: ' + (metVia.sync && metVia.sync.via) + ')');
  ok(!!metVia.sync && !!metVia.sync.rcode, 'je eigen verwijscode gaat ook mee');

  console.log('\n-- een link die je in een WhatsApp-groep mag plakken --');
  // Dit is de belangrijkste van de hele suite: met een sync-code geeft GET /api/state/:code de hele
  // voortgang weg. Een verwijscode mag alleen kunnen zeggen "ik heb deze persoon binnengehaald".
  ok(kaal.rcode && kaal.rcode !== kaal.synccode,
    'de verwijscode is niet je sync-code (' + kaal.rcode + ' tegenover ' + kaal.synccode + ')');
  ok(kaal.groepslink.indexOf('&v=' + kaal.rcode) !== -1,
    'de groepslink draagt een afzender mee: ' + kaal.groepslink);
  ok(kaal.duellink.indexOf('&v=' + kaal.rcode) !== -1, 'de duellink ook');
  ok(kaal.groepslink.indexOf(kaal.synccode) === -1, 'en de sync-code staat er níét in');

  const alleFouten = [].concat(li.errs, groep.errs, beide.errs, metVia.errs, kaal.errs, duel.errs);
  ok(alleFouten.length === 0, 'geen paginafouten' + (alleFouten.length ? ': ' + alleFouten[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' fout'); process.exit(1); }
  console.log('\nalles goed');
})();
