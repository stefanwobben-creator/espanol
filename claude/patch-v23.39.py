#!/usr/bin/env python3
# v23.39 - Adivina, het negende spel. Lingo, maar met jouw eigen woorden erin.
#
# Stefan: "lingo met punten en een reeks en niet ter vervanging maar als aanvulling want kruiswoord
# is wel lekker ontspannen." Dus: erbij, met punten en een dagreeks, en er verdwijnt niets.
#
# Waarom dit spel er iets aan toevoegt en Boggle niet: Letras is al een letterpot waar je woorden
# uit bouwt, en Sopa de letras is al het raster. Wat hier nieuw is, is de terugkoppeling per letter.
# Alle acht bestaande spellen zijn "weet je het of niet"; dit is "je weet het half en je redeneert je
# erheen", en het traint spelling (b tegen v, ll tegen y, c tegen z) die nergens anders apart aan bod
# komt.
#
# Drie keuzes die het spel bepalen, en waarom:
#   - De eerste letter staat er, zoals bij Lingo. Zonder die letter is een woord van vijf letters in
#     een taal die je aan het leren bent geen puzzel maar een gok.
#   - Een gok hoeft geen bestaand woord te zijn. Wordle eist dat, maar die heeft een woordenboek;
#     deze app kent 1648 losse woorden en zou dus geldige Spaanse gokken afkeuren. Een spel dat jou
#     vertelt dat je woord niet bestaat terwijl het bestaat, leer je wantrouwen.
#   - De Nederlandse betekenis is een knop en geen gegeven. Staat hij er meteen, dan is het alleen
#     nog spellen; staat hij er nooit, dan zit je vast. Als hint kost hij de helft van je punten, en
#     dan is het een keuze in plaats van een instelling.
#
# Het doelwoord komt bij voorkeur uit je eigen SRS (doosje 1 tot en met 3), zodat een potje geen
# puzzel is maar herhaling. Oplossen duwt het woord een doosje omhoog via spelSrsBij(), dus het
# plafond van doosje 3 geldt hier net als bij elk ander spel: spelen brengt je in de marge, nooit
# over de streep. Dat blijft de woordtrainer.
import pathlib, sys

WORTEL = pathlib.Path.home() / "espanol"
APP = WORTEL / "index.html"
VERSIE = WORTEL / "versie.txt"

SUITE_TEKST = r"""// v23.39: Adivina, het negende spel. Lingo met je eigen woordenschat.
//
// Wat deze suite vastlegt, en waarom precies dit:
//   - de kleurregel. Een letter die twee keer in je gok staat en een keer in het doel mag een keer
//     oranje worden en niet twee keer. Dat is de enige regel in dit spel die je met blote ogen niet
//     ziet als hij fout is: het voelt gewoon "raar".
//   - de eerste letter krijg je en die kun je niet weggummen. Zonder die letter is een woord van
//     vijf letters in een vreemde taal geen puzzel maar een gok.
//   - een spel duwt een woord tot doosje 3 en niet verder. Dat is SPEL_PLAFOND en het is de afspraak
//     die dit spel eerlijk houdt tegenover de balk op je voortgangspagina.
//   - elke gok telt als beurt. Sinds v23.38 is dat de teller waar je week en je gemeten tijd op
//     staan; een spel dat trackPoging overslaat is een half uur dat nergens terugkomt.
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 1000 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Adiv' + Date.now());
  await page.click('button:has-text("A2 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(1000);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true; S.speelAlles = true;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- de kleurregel --');
  const kleur = await page.evaluate(() => ({
    dubbelGok: adivKleur('sssss', 'casas'),   // twee s in het doel, vijf in de gok
    oranje: adivKleur('sacas', 'casas'),      // verschoven letters
    niets: adivKleur('mmmmm', 'casas')
  }));
  ok(JSON.stringify(kleur.dubbelGok) === JSON.stringify(['weg', 'weg', 'goed', 'weg', 'goed']),
    'vijf keer dezelfde letter levert alleen de twee juiste plekken op (' + kleur.dubbelGok.join(',') + ')');
  ok(JSON.stringify(kleur.oranje) === JSON.stringify(['bijna', 'goed', 'bijna', 'goed', 'goed']),
    'een letter op de verkeerde plek wordt oranje (' + kleur.oranje.join(',') + ')');
  ok(kleur.niets.every((k) => k === 'weg'), 'een letter die er niet in zit blijft grijs');

  console.log('\n-- de vijver --');
  const pool = await page.evaluate(() => {
    const l = adivPool();
    return { n: l.length, fout: l.filter((w) => [5, 6].indexOf(w.plat.length) === -1 || /\s|ñ/.test(w.es)).length,
             zonderId: l.filter((w) => !w.id).length };
  });
  ok(pool.n >= 100, 'er zijn genoeg woorden om mee te spelen (' + pool.n + ')');
  ok(pool.fout === 0, 'alleen losse woorden van vijf of zes letters, zonder ñ');
  ok(pool.zonderId === 0, 'en allemaal met een id, want anders kan het spel je woordjes niet raken');

  console.log('\n-- het scherm is bereikbaar en speelt --');
  await page.evaluate(() => { funView = null; show('speeltuin'); });
  await page.waitForTimeout(400);
  const inMenu = await page.evaluate(() => !!document.getElementById('ftAdiv'));
  ok(inMenu, 'Adivina staat in de speeltuin');
  await page.evaluate(() => { document.getElementById('ftAdiv').click(); });
  await page.waitForTimeout(400);

  // een gecontroleerd doelwoord, anders hangt de test aan het toeval van adivKies()
  const doel = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[0];
    S.srs[w.id] = { box: 1, due: today(), n: 1 };
    S.dagStats = {};
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivBewaar(); renderFunAdivina();
    return { plat: w.plat, id: w.id, nl: w.nl };
  });

  const start = await page.evaluate(() => ({
    nu: adivSpel.nu,
    vakken: document.querySelectorAll('.adivVak').length,
    toetsen: document.querySelectorAll('[data-adivk]').length
  }));
  ok(start.nu.length === 1 && start.nu === doel.plat.charAt(0), 'de eerste letter staat er al');
  ok(start.vakken === 25, 'vijf rijen van vijf vakken (' + start.vakken + ')');
  ok(start.toetsen >= 28, 'er staat een toetsenbord (' + start.toetsen + ' toetsen)');

  console.log('\n-- de eerste letter kun je niet weghalen --');
  await page.evaluate(() => { adivWis(); adivWis(); adivWis(); });
  const naWis = await page.evaluate(() => adivSpel.nu);
  ok(naWis.length === 1, 'wissen stopt bij de eerste letter (' + naWis + ')');

  console.log('\n-- raden gaat via het toetsenbord --');
  // een foute gok van de goede lengte: de rest van het woord omgedraaid
  const gok1 = doel.plat.charAt(0) + doel.plat.slice(1).split('').reverse().join('');
  const anders = gok1 !== doel.plat ? gok1 : doel.plat.slice(0, 4) + (doel.plat.charAt(4) === 'a' ? 'o' : 'a');
  for (const c of anders.slice(1)) {
    await page.evaluate((k) => { document.querySelector("[data-adivk='" + k + "']").click(); }, c);
  }
  const voorRaden = await page.evaluate(() => adivSpel.nu);
  ok(voorRaden === anders, 'de letters komen in het vak terecht (' + voorRaden + ')');
  await page.evaluate(() => { document.querySelector("[data-adivk='@doe']").click(); });
  await page.waitForTimeout(200);
  const na1 = await page.evaluate(() => ({
    gok: adivSpel.gok.slice(), nu: adivSpel.nu, klaar: adivSpel.klaar,
    pog: (S.dagStats[today()] || {}).pogingen || 0, fouten: (S.dagStats[today()] || {}).fouten || 0
  }));
  ok(na1.gok.length === 1 && na1.gok[0] === anders, 'de gok staat op het bord');
  ok(na1.nu.length === 1, 'en de volgende rij begint weer met de eerste letter');
  ok(na1.pog === 1 && na1.fouten === 1, 'de gok telt als beurt, en als foute beurt (' + na1.pog + '/' + na1.fouten + ')');

  console.log('\n-- een gok van de verkeerde lengte doet niets --');
  await page.evaluate(() => { adivSpel.nu = adivSpel.doel.slice(0, 3); adivDoe(); });
  const naKort = await page.evaluate(() => adivSpel.gok.length);
  ok(naKort === 1, 'een half woord wordt niet ingediend');

  console.log('\n-- winnen: punten, doosje, reeks --');
  const win = await page.evaluate(() => {
    const xpVoor = S.txp || 0;
    adivSpel.nu = adivSpel.doel;
    adivDoe();
    return { klaar: adivSpel.klaar, xp: adivSpel.xp, xpErbij: (S.txp || 0) - xpVoor,
             box: (S.srs[adivSpel.id] || {}).box, reeks: S.adiv.reeks, best: S.adiv.best,
             gewonnen: S.adiv.gewonnen, gespeeld: S.adiv.gespeeld,
             pog: (S.dagStats[today()] || {}).pogingen || 0 };
  });
  ok(win.klaar === 1, 'het spel is gewonnen');
  ok(win.xp === 8 && win.xpErbij === 8, 'twee pogingen levert 8 punten op (' + win.xp + ')');
  ok(win.box === 2, 'het woord schuift een doosje op (' + win.box + ')');
  ok(win.reeks === 1 && win.best === 1, 'de reeks staat op 1');
  ok(win.gewonnen === 1 && win.gespeeld === 1, 'de teller klopt (' + win.gewonnen + '/' + win.gespeeld + ')');
  ok(win.pog === 2, 'ook de winnende gok telt als beurt (' + win.pog + ')');

  console.log('\n-- het plafond van doosje 3 geldt ook hier --');
  const plafond = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[1];
    S.srs[w.id] = { box: SPEL_PLAFOND, due: today(), n: 5 };
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivSpel.nu = adivSpel.doel; adivDoe();
    return { box: S.srs[w.id].box, plafond: SPEL_PLAFOND };
  });
  ok(plafond.box === plafond.plafond, 'een woord op het plafond blijft daar (' + plafond.box + ')');

  console.log('\n-- de hint kost de helft --');
  const hint = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[2];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: true, klaar: 0, xp: 0 };
    adivSpel.nu = adivSpel.doel; adivDoe();
    return adivSpel.xp;
  });
  ok(hint === 5, 'in een poging met hint: 5 in plaats van 10 (' + hint + ')');

  console.log('\n-- verliezen laat het woord zien --');
  const verlies = await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 5)[3];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 5, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    const mis = w.plat.charAt(0) + (w.plat.slice(1).split('').reverse().join('') === w.plat.slice(1)
      ? w.plat.slice(1, 4) + (w.plat.charAt(4) === 'a' ? 'o' : 'a')
      : w.plat.slice(1).split('').reverse().join(''));
    for (let i = 0; i < 5; i++) { adivSpel.nu = mis; adivDoe(); }
    renderFunAdivina();
    const t = document.getElementById('funCard').innerText;
    return { klaar: adivSpel.klaar, gokken: adivSpel.gok.length, es: w.es,
             toont: t.indexOf(w.es) !== -1, kbWeg: document.querySelectorAll('[data-adivk]').length };
  });
  ok(verlies.klaar === -1 && verlies.gokken === 5, 'na vijf pogingen is het klaar');
  ok(verlies.toont, 'en het woord staat er, met zijn accenten (' + verlies.es + ')');
  ok(verlies.kbWeg === 0, 'het toetsenbord is weg als er niets meer te raden valt');

  console.log('\n-- een half spel overleeft een herlading --');
  await page.evaluate(() => {
    const w = adivPool().filter((x) => x.plat.length === 6)[0];
    adivSpel = { id: w.id, es: w.es, nl: w.nl, doel: w.plat, len: 6, gok: [], nu: w.plat.charAt(0),
                 hint: false, klaar: 0, xp: 0 };
    adivSpel.nu = w.plat.charAt(0) + w.plat.slice(1).split('').reverse().join('');
    if (adivSpel.nu !== w.plat) adivDoe(); else { adivSpel.gok.push(adivSpel.nu); adivBewaar(); }
  });
  await page.reload(); await page.waitForTimeout(900);
  const herstel = await page.evaluate(() => {
    funView = 'adiv'; adivSpel = null; show('speeltuin'); renderFunAdivina();
    return { gokken: adivSpel ? adivSpel.gok.length : -1, len: adivSpel ? adivSpel.len : 0 };
  });
  ok(herstel.gokken === 1 && herstel.len === 6, 'de gedane gok staat er nog na een herlading');

  ok(errors.length === 0, 'geen JS-fouten (' + errors.length + ')' + (errors[0] ? ' ' + errors[0] : ''));

  await browser.close();
  if (fout) { console.log('\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD'); process.exit(1); }
  console.log('\nALLE PLAYWRIGHT-TESTS GESLAAGD');
})();
"""

src = APP.read_text(encoding="utf-8")
# Per bestand een eigen vlag, en niet meteen stoppen: dan slaat hij de suites niet stilletjes over
# omdat index.html al klaar was (zie DEPLOY.md, het stuk over patchen).
DOE_APP = 'var APP_VERSIE = "v23.39"' not in src
if DOE_APP and 'var APP_VERSIE = "v23.38"' not in src:
    print("Deze index.html staat niet op v23.38. Eerst bijtrekken:\n    git pull --rebase\n")
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP: return          # index.html is al bij; de suites hieronder gaan gewoon door
    aantal = src.count(anker)
    assert aantal == n, "anker %d keer gevonden, verwacht %d: %r" % (aantal, n, anker[:90])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. de opmaak
rep("""  .cl-balkbox{height:6px;""",
    """  .adivGrid{display:flex; flex-direction:column; gap:6px; align-items:center; margin:12px 0 10px;}
  .adivRij{display:flex; gap:6px;}
  .adivVak{width:44px; height:48px; border-radius:10px; border:2px solid var(--border);
           background:var(--card); display:flex; align-items:center; justify-content:center;
           font-size:1.35rem; font-weight:800; text-transform:uppercase; color:var(--ink);}
  .adivVak.nu{border-color:var(--accent);}
  .adivVak.goed{background:var(--green); border-color:var(--green); color:#fff;}
  .adivVak.bijna{background:var(--amber); border-color:var(--amber); color:#fff;}
  .adivVak.weg{background:var(--bg); border-color:var(--border); color:var(--muted);}
  .adivVak.vast{border-style:dashed;}
  .adivKb{display:flex; flex-direction:column; gap:6px; align-items:center; margin-top:10px;}
  .adivKbRij{display:flex; gap:4px; justify-content:center; flex-wrap:nowrap; width:100%;}
  .adivToets{flex:1 1 0; min-width:0; padding:13px 0; border-radius:8px; border:1.5px solid var(--border);
             background:var(--card); font-size:1rem; font-weight:700; text-transform:uppercase;
             color:var(--ink); cursor:pointer;}
  /* Raden en wissen staan op een eigen rij. Stonden ze tussen de letters, dan hield elke letter op
     de smalste telefoon nog een tekenbreedte over en las de onderste rij als een streepjescode. */
  .adivKbRij.doe{margin-top:4px; gap:8px;}
  .adivToets.breed{padding:12px 0; font-size:.95rem; text-transform:none; font-weight:800;}
  .adivToets.breed.aan{background:var(--accent); border-color:var(--accent); color:#fff;}
  .adivToets.goed{background:var(--green); border-color:var(--green); color:#fff;}
  .adivToets.bijna{background:var(--amber); border-color:var(--amber); color:#fff;}
  .adivToets.weg{background:var(--bg); color:var(--muted); opacity:.6;}
  .adivStand{display:flex; gap:14px; justify-content:center; margin-top:10px; font-size:.85rem;
             color:var(--muted);}
  .adivStand b{display:block; text-align:center; font-size:1.1rem; color:var(--ink);}
  .cl-balkbox{height:6px;""")

# ---------------------------------------------------------------- 2. de motor
MOTOR = r'''
/* ================= ADIVINA (v23.39) =================
   Lingo met jouw eigen woordenschat. Vijf pogingen, de eerste letter krijg je, en per letter zie je
   of hij goed staat (groen), ergens anders in het woord zit (oranje) of er niet in zit (grijs).

   Wat dit spel doet dat de andere acht niet doen: terugkoppeling per letter. Letras en Sopa de
   letras werken met woorden die je al kent of niet; hier redeneer je je naar een woord toe, en
   onderweg oefen je spelling. Dat is precies het stuk Spaans waar een Nederlander op struikelt:
   b tegen v, ll tegen y, c tegen z.

   Het doelwoord komt bij voorkeur uit je eigen SRS, doosje 1 tot en met 3. Dan is een potje geen
   puzzel maar herhaling. Oplossen loopt via spelSrsBij(), dus SPEL_PLAFOND geldt: een spel kan een
   woord tot doosje 3 duwen en niet verder. Stevig blijft vijf keer los uit je hoofd. */
var ADIV_POG = 5;                       // vijf pogingen, zoals Lingo
var ADIV_LEN = [5, 6];                  // woorden van vijf of zes letters
var ADIV_XP = [10, 8, 6, 4, 2];         // minder punten naarmate je er langer over doet
var ADIV_KB = ["qwertyuiop", "asdfghjkl", "zxcvbnm"];
var adivSpel = null;

function adivPlat(w){ return stripAcc(String(w || "").toLowerCase()).replace(/[^a-z]/g, ""); }

/* De vijver. Alleen woorden met een id, want alleen die kunnen een doosje opschuiven: een spel dat
   je woordenschat niet raakt is tijdverdrijf, en dat hebben we in v23.11 bij Letras al een keer
   moeten repareren. Geen uitdrukkingen, geen n met tilde (die valt weg bij het platslaan, dezelfde
   afspraak als in Letras), lidwoord eraf. */
var _adivPool = null;
function adivPool(){
  if(_adivPool && _adivPool.n === WORDS.length) return _adivPool.lijst;
  var zien = {}, uit = [];
  WORDS.forEach(function(w){
    var es = String(w.es || "").replace(/^(el|la|los|las|un|una)\s+/i, "").split(/[\/(]/)[0].trim();
    if(!es || /\s/.test(es) || /[ñÑ]/.test(es)) return;
    var plat = adivPlat(es);
    if(ADIV_LEN.indexOf(plat.length) === -1) return;
    if(zien[plat]) return;
    zien[plat] = 1;
    uit.push({id: w.id, es: es, nl: wTrans(w), plat: plat});
  });
  _adivPool = {n: WORDS.length, lijst: uit};
  return uit;
}
function adivStand(){
  S.adiv = S.adiv || {reeks:0, best:0, gespeeld:0, gewonnen:0, laatst:"", gehad:[]};
  if(!S.adiv.gehad) S.adiv.gehad = [];
  return S.adiv;
}
function adivKies(){
  var pool = adivPool();
  if(!pool.length) return null;
  var gehad = adivStand().gehad;
  var vers = pool.filter(function(w){ return gehad.indexOf(w.id) === -1; });
  if(vers.length < 5) vers = pool;        // vijver rond: opnieuw beginnen is beter dan niets tonen
  /* Eerst woorden die je aan het leren bent. Kent je SRS er te weinig, dan gewoon een woord van je
     niveau: een spel dat "kom later terug" zegt leert je dat de knoppen hier niet kloppen, en dat
     is dezelfde regel als bij dagSpelKeuze(). */
  var leer = vers.filter(function(w){
    var st = S.srs && S.srs[w.id];
    return st && (st.box || 0) >= 1 && (st.box || 0) <= SPEL_PLAFOND;
  });
  var bak = leer.length >= 3 ? leer : vers;
  return bak[Math.floor(Math.random() * bak.length)];
}
function adivNieuw(){
  var w = adivKies();
  if(!w){ adivSpel = null; return; }
  adivSpel = {id:w.id, es:w.es, nl:w.nl, doel:w.plat, len:w.plat.length,
              gok:[], nu:w.plat.charAt(0), hint:false, klaar:0, xp:0};
  adivBewaar();
}
function adivBewaar(){
  var s = adivStand();
  s.spel = adivSpel ? {id:adivSpel.id, es:adivSpel.es, nl:adivSpel.nl, doel:adivSpel.doel,
                       len:adivSpel.len, gok:adivSpel.gok.slice(), nu:adivSpel.nu,
                       hint:adivSpel.hint, klaar:adivSpel.klaar, xp:adivSpel.xp} : null;
  try { persist(); } catch(e){}
}
function adivHerstel(){
  var s = adivStand();
  if(s.spel && s.spel.doel){
    adivSpel = {id:s.spel.id, es:s.spel.es, nl:s.spel.nl, doel:s.spel.doel, len:s.spel.len,
                gok:(s.spel.gok || []).slice(), nu:s.spel.nu || s.spel.doel.charAt(0),
                hint:!!s.spel.hint, klaar:s.spel.klaar || 0, xp:s.spel.xp || 0};
    return true;
  }
  return false;
}
/* Twee rondes, want een letter die twee keer in je gok staat en een keer in het doel mag maar een
   keer oranje worden. Eerst alle groene eruit, dan pas de rest tegen wat er overblijft. */
function adivKleur(gok, doel){
  var uit = [], rest = {}, i, c;
  for(i = 0; i < doel.length; i++){
    if(gok.charAt(i) === doel.charAt(i)) uit[i] = "goed";
    else { uit[i] = "weg"; c = doel.charAt(i); rest[c] = (rest[c] || 0) + 1; }
  }
  for(i = 0; i < doel.length; i++){
    if(uit[i] === "goed") continue;
    c = gok.charAt(i);
    if(rest[c] > 0){ uit[i] = "bijna"; rest[c]--; }
  }
  return uit;
}
// De stand per letter op het toetsenbord: groen wint van oranje, oranje van grijs.
function adivLetters(){
  var st = {}, rang = {weg:1, bijna:2, goed:3};
  (adivSpel ? adivSpel.gok : []).forEach(function(g){
    var kl = adivKleur(g, adivSpel.doel), i, c;
    for(i = 0; i < g.length; i++){
      c = g.charAt(i);
      if(!st[c] || rang[kl[i]] > rang[st[c]]) st[c] = kl[i];
    }
  });
  return st;
}
function adivTik(c){
  if(!adivSpel || adivSpel.klaar) return;
  if(adivSpel.nu.length >= adivSpel.len) return;
  adivSpel.nu += c;
  renderFunAdivina();
}
function adivWis(){
  if(!adivSpel || adivSpel.klaar) return;
  if(adivSpel.nu.length <= 1) return;              // de eerste letter krijg je, die blijft staan
  adivSpel.nu = adivSpel.nu.slice(0, -1);
  renderFunAdivina();
}
function adivDoe(){
  if(!adivSpel || adivSpel.klaar) return;
  if(adivSpel.nu.length !== adivSpel.len) return;
  var g = adivSpel.nu;
  adivSpel.gok.push(g);
  adivSpel.nu = adivSpel.doel.charAt(0);
  /* Elke gok is een nagekeken antwoord: hij telt mee in je beurten en dus ook in de tijdmeting.
     Zonder dit zou een half uur Adivina op je voortgangspagina nul minuten zijn (zie v23.38). */
  try { trackPoging(g !== adivSpel.doel); } catch(e){}
  if(g === adivSpel.doel) adivAf(true);
  else if(adivSpel.gok.length >= ADIV_POG) adivAf(false);
  else adivBewaar();
  renderFunAdivina();
}
function adivAf(gewonnen){
  var s = adivStand(), t = today();
  adivSpel.klaar = gewonnen ? 1 : -1;
  s.gespeeld = (s.gespeeld || 0) + 1;
  if(gewonnen){
    s.gewonnen = (s.gewonnen || 0) + 1;
    var xp = ADIV_XP[Math.min(adivSpel.gok.length, ADIV_POG) - 1] || 2;
    if(adivSpel.hint) xp = Math.max(1, Math.floor(xp / 2));
    adivSpel.xp = xp;
    addXP(xp);
    try { spelSrsBij(adivSpel.id); } catch(e){}
    /* De reeks telt dagen waarop je er een oploste, niet potjes achter elkaar. Tien potjes op een
       zondag is geen gewoonte; tien dagen wel. Hij springt terug naar 1 na een gemiste dag en
       daar staat geen straftekst bij: zie v19.63, het getal dat telt blijft hoe vaak je terugkomt.
       Daarom staat je beste reeks ernaast, en die kan alleen omhoog. */
    if(s.laatst !== t){
      s.reeks = (s.laatst === addDays(t, -1)) ? (s.reeks || 0) + 1 : 1;
      s.laatst = t;
      if((s.reeks || 0) > (s.best || 0)) s.best = s.reeks;
    }
    try { confetti(["🟩", "✨", "🎉"], 16); } catch(e){}
  } else {
    adivSpel.xp = 1;
    addXP(1);                                    // meedoen levert altijd iets op
  }
  s.gehad = s.gehad.concat([adivSpel.id]).slice(-60);
  adivBewaar();
}
function renderFunAdivina(){
  var el = document.getElementById("funCard");
  if(!el) return;
  if(!adivSpel && !adivHerstel()) adivNieuw();
  if(!adivSpel){
    el.innerHTML = "<h2>Adivina 🟩</h2><p class='muted'>" +
      ct("Nog geen woorden van vijf of zes letters om mee te spelen.",
         "No five or six letter words to play with yet.") + "</p>" +
      "<div class='row' style='margin-top:10px'><button class='ghost' id='btnFunTerug'>" + fx("terug") +
      "</button></div>";
    var tb = document.getElementById("btnFunTerug");
    if(tb) tb.onclick = function(){ funView = null; renderFun(); };
    return;
  }
  var s = adivStand(), klaar = adivSpel.klaar, i, r;
  var rijen = "";
  for(r = 0; r < ADIV_POG; r++){
    var vakken = "";
    if(r < adivSpel.gok.length){
      var g = adivSpel.gok[r], kl = adivKleur(g, adivSpel.doel);
      for(i = 0; i < adivSpel.len; i++) vakken += "<div class='adivVak " + kl[i] + "'>" + g.charAt(i) + "</div>";
    } else if(r === adivSpel.gok.length && !klaar){
      for(i = 0; i < adivSpel.len; i++){
        vakken += "<div class='adivVak nu" + (i === 0 ? " vast" : "") + "'>" +
          (i < adivSpel.nu.length ? adivSpel.nu.charAt(i) : "&nbsp;") + "</div>";
      }
    } else {
      for(i = 0; i < adivSpel.len; i++) vakken += "<div class='adivVak'>&nbsp;</div>";
    }
    rijen += "<div class='adivRij'>" + vakken + "</div>";
  }
  var letters = adivLetters();
  var vol = adivSpel.nu.length === adivSpel.len;
  var kb = ADIV_KB.map(function(rij){
    return "<div class='adivKbRij'>" + rij.split("").map(function(c){
      return "<button type='button' class='adivToets " + (letters[c] || "") + "' data-adivk='" + c + "'>" +
        c + "</button>";
    }).join("") + "</div>";
  }).join("") +
    "<div class='adivKbRij doe'>" +
      "<button type='button' class='adivToets breed" + (vol ? " aan" : "") + "' data-adivk='@doe'>" +
        ct("Raden","Guess") + "</button>" +
      "<button type='button' class='adivToets breed' data-adivk='@wis'>⌫ " + ct("wis","clear") + "</button>" +
    "</div>";

  var kop = "<h2>Adivina 🟩</h2>" +
    "<span class='kicker'>" + adivSpel.len + " " + ct("letters","letters") + " · " +
      Math.max(0, ADIV_POG - adivSpel.gok.length) + " " +
      (ADIV_POG - adivSpel.gok.length === 1 ? ct("poging over","guess left") : ct("pogingen over","guesses left")) +
    "</span>" +
    "<p class='muted'>" + ct("De eerste letter krijg je. Groen staat goed, oranje zit er wel in maar " +
      "ergens anders, grijs zit er niet in.",
      "You get the first letter. Green is in the right spot, amber is in the word elsewhere, grey is " +
      "not in the word.") + "</p>";

  var hint = adivSpel.hint || klaar
    ? "<p class='muted' style='margin:-4px 0 6px'>" + ct("Betekenis","Meaning") + ": <b>" + adivSpel.nl + "</b></p>"
    : "<div class='row' style='margin:-4px 0 6px'><button class='mini' id='btnAdivHint'>" +
      ct("Wat betekent het? (kost de helft van je punten)","What does it mean? (costs half your points)") +
      "</button></div>";

  var slot = "";
  if(klaar === 1){
    slot = "<div class='feedback ok' style='margin-top:10px'><b>" + adivSpel.es + "</b> · " +
      adivSpel.nl + "<br>" + ct("Gevonden in " + adivSpel.gok.length + " " +
        (adivSpel.gok.length === 1 ? "poging" : "pogingen") + ", +" + adivSpel.xp + " punten.",
        "Found in " + adivSpel.gok.length + " " + (adivSpel.gok.length === 1 ? "guess" : "guesses") +
        ", +" + adivSpel.xp + " points.") + "</div>";
  } else if(klaar === -1){
    /* Geen "helaas". Het woord staat er, met zijn accenten, want dat is het enige wat je hier nog
       kunt leren, en het staat morgen gewoon weer in je herhalingen. */
    slot = "<div class='feedback' style='margin-top:10px'>" + ct("Het was","It was") + " <b>" +
      adivSpel.es + "</b> · " + adivSpel.nl + "<br>" +
      ct("Hij komt vanzelf terug in je herhalingen.","It comes back in your reviews on its own.") + "</div>";
  }

  el.innerHTML = kop + hint +
    "<div class='adivGrid'>" + rijen + "</div>" +
    (klaar ? "" : "<div class='adivKb'>" + kb + "</div>") + slot +
    "<div class='adivStand'>" +
      "<div><b>" + (s.reeks || 0) + "</b>" + ct("dagen op rij","days in a row") + "</div>" +
      "<div><b>" + (s.best || 0) + "</b>" + ct("je beste reeks","your best run") + "</div>" +
      "<div><b>" + (s.gewonnen || 0) + "/" + (s.gespeeld || 0) + "</b>" + ct("opgelost","solved") + "</div>" +
    "</div>" +
    "<div class='row' style='margin-top:10px'>" +
      (klaar ? "<button class='primary' id='btnAdivNieuw'>" + ct("Nog een","Another one") + "</button>"
             : "<button class='ghost' id='btnAdivNieuw'>" + ct("Ander woord","Another word") + "</button>") +
      "<button class='ghost' id='btnFunTerug'>" + fx("terug") + "</button></div>" +
    (klaar === 1 ? naRondeHtml() : "");

  el.querySelectorAll("[data-adivk]").forEach(function(b){
    b.onclick = function(){
      var k = b.getAttribute("data-adivk");
      if(k === "@doe") adivDoe();
      else if(k === "@wis") adivWis();
      else adivTik(k);
    };
  });
  var hb = document.getElementById("btnAdivHint");
  if(hb) hb.onclick = function(){ adivSpel.hint = true; adivBewaar(); renderFunAdivina(); };
  document.getElementById("btnAdivNieuw").onclick = function(){ adivNieuw(); renderFunAdivina(); };
  document.getElementById("btnFunTerug").onclick = function(){ funView = null; renderFun(); };
  if(klaar === 1) naRondeWire();
}

'''

rep("""function renderFun(){
  var el = document.getElementById("funCard");""",
    MOTOR.lstrip("\n") + """function renderFun(){
  var el = document.getElementById("funCard");""")

# ---------------------------------------------------------------- 3. inhaken op de spelmachine
rep("""  if(funView === "letras"){ renderFunLetras(); return; }""",
    """  if(funView === "letras"){ renderFunLetras(); return; }
  if(funView === "adiv"){ renderFunAdivina(); return; }""")

rep("""    {v:"letras",  id:"ftLetras",  e:"\\ud83d\\udd24",        t:"Letras",             s:ct("Zeven letters, hoeveel woorden haal je eruit? Geen klok.","Seven letters, how many words can you find? No clock.")},""",
    """    {v:"letras",  id:"ftLetras",  e:"\\ud83d\\udd24",        t:"Letras",             s:ct("Zeven letters, hoeveel woorden haal je eruit? Geen klok.","Seven letters, how many words can you find? No clock.")},
    {v:"adiv",    id:"ftAdiv",    e:"\\ud83d\\udfe9",        t:"Adivina",            s:ct("Raad het woord in vijf pogingen. De eerste letter krijg je.","Guess the word in five tries. You get the first letter.")},""")

rep("""  wire("ftLetras", function(){ speelGezien("letras"); funView = "letras"; ltSpel = null; navPush({t:"fun", v:"letras"}); renderFun(); });""",
    """  wire("ftLetras", function(){ speelGezien("letras"); funView = "letras"; ltSpel = null; navPush({t:"fun", v:"letras"}); renderFun(); });
  wire("ftAdiv", function(){ speelGezien("adiv"); funView = "adiv"; adivSpel = null; navPush({t:"fun", v:"adiv"}); renderFun(); });""")

# meedoen in de dagrotatie, en pas als er iets te raden valt
rep("""  letras:  {soort:"w", n:10},""",
    """  letras:  {soort:"w", n:10},
  adiv:    {soort:"w", n:15},""")

rep("""  {v:"letras",  e:"\\ud83d\\udd24", n:"Letras"},""",
    """  {v:"letras",  e:"\\ud83d\\udd24", n:"Letras"},
  {v:"adiv",    e:"\\ud83d\\udfe9", n:"Adivina"},""")

# een verse pot bij binnenkomst via het dagscherm, net als conj en corr
rep("""  if(v === "kruis"){ kruisLos = null; }""",
    """  if(v === "kruis"){ kruisLos = null; }
  if(v === "adiv"){ adivSpel = null; }""")

rep('var APP_VERSIE = "v23.38";', 'var APP_VERSIE = "v23.39";')
if DOE_APP:
    APP.write_text(src, encoding="utf-8")
    print("  index.html: Adivina erbij, v23.39")
else:
    print("  index.html staat al op v23.39, die sla ik over")

v = VERSIE.read_text(encoding="utf-8").strip()
if v != "v23.39":
    VERSIE.write_text("v23.39\n", encoding="utf-8")
    print("  versie.txt: " + v + " -> v23.39")
# ---------------------------------------------------------------- 2. de suite
SUITE = WORTEL / "test" / "suites" / "pw-adivina.js"
if SUITE.exists():
    print("  pw-adivina.js staat er al")
else:
    SUITE.write_text(SUITE_TEKST, encoding="utf-8")
    print("  test/suites/pw-adivina.js geschreven")

# ---------------------------------------------------------------- 3. pw-mezcla los van de kalender
# Deze viel om terwijl er niets aan de app veranderd was: op 10 aug groen, op 11 aug rood. Chispa
# heeft elke dag een wens, en is die wens "een tapa", dan geeft ze er een terug zodra je haar voert.
# Je voorraad gaat dan van 20 naar 20 en de test rekende op 19. Dat is geen fout in de app maar wel
# een poort die een op de drie dagen dichtzit zonder reden.
MEZ = WORTEL / "test" / "suites" / "pw-mezcla.js"
mz = MEZ.read_text(encoding="utf-8")
oudmz = """  console.log('\\n-- aantikken doet nog steeds wat het deed, en vult het vakje --');
  const voor = await page.evaluate(() => ({ tapas: S.tapas || 0, bailes: (S.bailes || []).length }));"""
nieuwmz = """  console.log('\\n-- aantikken doet nog steeds wat het deed, en vult het vakje --');
  /* De wens van de dag eerst afvinken. Is die wens toevallig "een tapa", dan geeft Chispa er een
     terug zodra je haar voert (chispaWensDoe), en dan gaat je voorraad van 20 naar 20. Dat is geen
     fout in de app maar wel een test die op een derde van de dagen omvalt, en een poort die van de
     kalender afhangt is geen poort. Op 10 aug was hij groen en op 11 aug rood, met dezelfde code. */
  await page.evaluate(() => { zorgState().wensOp = today(); try { persist(); } catch (e) {} });
  const voor = await page.evaluate(() => ({ tapas: S.tapas || 0, bailes: (S.bailes || []).length }));"""
if oudmz in mz:
    MEZ.write_text(mz.replace(oudmz, nieuwmz, 1), encoding="utf-8")
    print("  pw-mezcla.js: los van de kalender")
else:
    print("  pw-mezcla.js stond al bij")

print("\nklaar. Draai nu de poort:")
print("  CHROMIUM=<pad naar chromium> node test/poort.js")
