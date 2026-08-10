#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.34: la mezcla. Tik een tapa en een dans aan en er komt iets uit.

Stefan wilde iets in de geest van Emoji Kitchen, met de opdracht erbij: denk goed na over de
interface zodat het intuïtief voelt.

Wat er niet komt: een knop, een scherm, een sleepgebaar. Sinds v23.33 staan de tapas en de dansen
onder elkaar bij Chispa, en dat suggereert de combinatie al. Ertussen zit nu een strip met twee
vakjes. Tik je een tapa aan, dan eet ze hem zoals altijd en vult het linkervakje. Tik je een dans
aan, dan danst ze zoals altijd en vult het rechtervakje. Zijn ze allebei vol, dan staat de uitkomst
er. Alles wat je al deed blijft precies hetzelfde; de mezcla ontstaat ernaast.

Waarom dit meer is dan een grap: de uitkomst is grammaticaal. De dans wordt een bijvoeglijk
naamwoord dat meebuigt met de tapa.

  el pulpo      + flamenco  -> el pulpo flamenco
  las aceitunas + salsa     -> las aceitunas salseras
  el queso      + tango     -> el queso tanguero
  las patatas   + reggaeton -> las patatas reggaetoneras

Achttien tapas maal acht dansen is 144 combinaties, en er staan er geen 144 in dit bestand: het
geslacht en het getal zitten al in het lidwoord van de tapa, dus acht stammen maal vier uitgangen is
de hele tabel. Daarmee drilt dit spelletje precies de regel waar Nederlandstaligen op blijven
struikelen, zonder dat het als oefening voelt.

Twee dingen die ik expres wel in de gegevens heb gezet in plaats van slim opgelost:

1. Een kernwoord per tapa. "el pulpo a la gallega flamenco" leest als een fout, dus de mezcla
   gebruikt de kern ("el pulpo"). Dat automatisch afknippen zou een parser vragen die het verschil
   moet zien tussen "las patatas bravas" (adjectief eraf) en "el pan con tomate" (bijzin eraf), en
   die parser heeft bij achttien regels geen bestaansrecht.
2. De bijvoeglijke naamwoorden zijn echte woorden: salsero, tanguero, cumbiambero, bachatero,
   merenguero, reggaetonero, flamenco en tapatío (van de jarabe tapatío). Verzonnen vormen zouden
   iemand die dit leest iets fouts leren, en dit is een leerapp.

Een tapa kost hier niets extra: de tapa die je aantikt wordt gewoon gegeven zoals altijd, en heb je
er geen, dan vult het vakje toch. Een woordspel achter een muntje zetten maakt er een winkel van.

Gevonden mezclas blijven staan, dus er komt een derde verzameling bij die alleen maar kan groeien.

Suite erbij: pw-mezcla.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")
MAP_S = os.path.join(WORTEL, "test", "suites")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function mezclaMaak" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)
if 'var APP_VERSIE = "v23.33";' not in src:
    print("Deze index.html staat niet op v23.33. Eerst bijtrekken:\n\n    git pull --rebase\n")
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. opmaak
rep(
    """  /* v23.32: de compacte meetregel van de voortgangspagina.""",
    """  /* v23.34: la mezcla. Twee vakjes en een uitkomst, tussen de tapas en de dansen in. Gestippeld
     omdat het geen kaart is maar een werkbank: hier gebeurt iets terwijl je bezig bent. */
  .mezcla{border:1px dashed var(--border); border-radius:12px; padding:9px 10px; margin:10px 0 2px;
          display:flex; align-items:center; justify-content:center; gap:8px; flex-wrap:wrap;}
  .mezVak{width:42px; height:42px; border-radius:10px; background:#faf7f2; border:1px solid var(--border);
          display:flex; align-items:center; justify-content:center; font-size:1.35rem; flex:0 0 42px;}
  .mezVak.leeg{color:var(--muted); font-size:.78rem; font-weight:700;}
  .mezOp{color:var(--muted); font-weight:800;}
  .mezUit{font-size:.95rem; text-align:center;}
  .mezUit b{display:block; font-size:1.05rem;}
  /* elk deel op zijn eigen regel: zonder display:block plakte "nieuw!" tegen de vertaling aan
     ("...die flamenco danstnieuw!") en dat leest als een fout in plaats van als een vondst. */
  .mezUit span{display:block; color:var(--muted); font-size:.82rem;}
  .mezNieuw{display:block; margin-top:2px; color:var(--accent); font-weight:700; font-size:.78rem;}
  .mezWis{background:none; border:0; color:var(--muted); text-decoration:underline; cursor:pointer;
          font-size:.8rem; padding:2px 4px;}
  /* v23.32: de compacte meetregel van de voortgangspagina.""")

# ---------------------------------------------------------------- 2. de kern per tapa
for oud, kern in [
    ('{id:"aceitunas",   e:"\U0001f9c9",  es:"las aceitunas",              nl:"olijven",', "las aceitunas"),
]:
    pass

KERNEN = [
    ("aceitunas", "las aceitunas"), ("bravas", "las patatas"), ("padron", "los pimientos"),
    ("sardinas", "las sardinas"), ("pantomate", "el pan"), ("taco", "el taco"),
    ("tortilla", "la tortilla"), ("gambas", "las gambas"), ("jamon", "el jam\u00f3n"),
    ("manchego", "el queso"), ("calamares", "los calamares"), ("champis", "los champi\u00f1ones"),
    ("pulpo", "el pulpo"), ("albondigas", "las alb\u00f3ndigas"), ("croquetas", "las croquetas"),
    ("ensaladilla", "la ensaladilla"), ("boquerones", "los boquerones"), ("chorizo", "el chorizo"),
]
for tid, kern in KERNEN:
    anker = '{id:"%s",' % tid
    aantal = src.count(anker)
    assert aantal == 1, "tapa-anker %s komt %d keer voor" % (tid, aantal)
    src = src.replace(anker, '{id:"%s", kern:"%s",' % (tid, kern), 1)

# ---------------------------------------------------------------- 3. de mezcla zelf
rep(
    """function tapaVanDaag(){ return TAPAS[dayHash("tapa") % TAPAS.length]; }""",
    """function tapaVanDaag(){ return TAPAS[dayHash("tapa") % TAPAS.length]; }

/* ================= LA MEZCLA (v23.34) =================
   Een tapa plus een dans wordt een naam, en die naam buigt. Het lidwoord van de tapa zegt al welk
   geslacht en welk getal het is, dus de tabel hieronder is acht stammen maal vier uitgangen en niet
   honderdvierenveertig regels.

   De woorden zijn echt: salsero, tanguero, cumbiambero, bachatero, merenguero, reggaetonero,
   flamenco en tapatío (van de jarabe tapatío). Verzonnen vormen zouden hier iets fouts aanleren, en
   dat is precies wat een leerapp niet mag doen met iets dat op een grap lijkt. */
var MEZCLA_ADJ = {
  salsa:     ["salsero", "salsera", "salseros", "salseras"],
  flamenco:  ["flamenco", "flamenca", "flamencos", "flamencas"],
  cumbia:    ["cumbiambero", "cumbiambera", "cumbiamberos", "cumbiamberas"],
  merengue:  ["merenguero", "merenguera", "merengueros", "merengueras"],
  bachata:   ["bachatero", "bachatera", "bachateros", "bachateras"],
  tango:     ["tanguero", "tanguera", "tangueros", "tangueras"],
  reggaeton: ["reggaetonero", "reggaetonera", "reggaetoneros", "reggaetoneras"],
  jarabe:    ["tapat\\u00edo", "tapat\\u00eda", "tapat\\u00edos", "tapat\\u00edas"]
};
// el = 0, la = 1, los = 2, las = 3. Het lidwoord draagt allebei de gegevens die we nodig hebben.
function mezclaVorm(kern){
  var w = String(kern || "").split(" ")[0].toLowerCase();
  if(w === "la") return 1;
  if(w === "los") return 2;
  if(w === "las") return 3;
  return 0;
}
function mezclaMaak(tapaId, baileId){
  var tp = TAPAS.filter(function(x){ return x.id === tapaId; })[0];
  var bl = BAILES.filter(function(x){ return x.id === baileId; })[0];
  if(!tp || !bl) return null;
  var adj = MEZCLA_ADJ[bl.id];
  if(!adj) return null;
  var kern = tp.kern || tp.es;
  return {id:tp.id + "|" + bl.id, tapa:tp, baile:bl,
          es:kern + " " + adj[mezclaVorm(kern)],
          nl:ct(tp.nl, tp.en) + " " + ct("die " + bl.nl.replace(/^de /, "") + " danst",
                                         "dancing the " + bl.nl.replace(/^de /, ""))};
}
function mezclaState(){ if(!S.mezcla) S.mezcla = []; return S.mezcla; }
function mezclaTotaal(){ return TAPAS.length * BAILES.length; }
// de twee vakjes leven alleen in dit tabblad: het is een handeling, geen bezit
var mezclaTapa = null, mezclaBaile = null;
/* Aantikken vult het vakje, en dat is alles wat deze functie doet. De tapa geven en het dansen
   gebeuren gewoon in hun eigen afhandeling; die zijn niet aangeraakt. Zo blijft de mezcla iets wat
   ontstaat terwijl je bezig bent, en niet iets waarvoor je eerst een stand moet klaarzetten. */
function mezclaKies(soort, id){
  if(soort === "tapa") mezclaTapa = id; else mezclaBaile = id;
  var m = (mezclaTapa && mezclaBaile) ? mezclaMaak(mezclaTapa, mezclaBaile) : null;
  var nieuw = false;
  if(m && mezclaState().indexOf(m.id) < 0){ mezclaState().push(m.id); nieuw = true; try { persist(); } catch(e){} }
  mezclaTeken(nieuw);
  if(m) try { chispaSay({es:"\\u00a1" + m.es + "!", nl:m.nl, en:m.nl}); } catch(e){}
  return m;
}
function mezclaWis(){ mezclaTapa = null; mezclaBaile = null; mezclaTeken(false); }
function mezclaHtml(nieuw){
  var tp = mezclaTapa ? TAPAS.filter(function(x){ return x.id === mezclaTapa; })[0] : null;
  var bl = mezclaBaile ? BAILES.filter(function(x){ return x.id === mezclaBaile; })[0] : null;
  var m = (tp && bl) ? mezclaMaak(tp.id, bl.id) : null;
  var vak = function(x){
    return x ? "<span class='mezVak'>"+x.e+"</span>"
             : "<span class='mezVak leeg'>?</span>";
  };
  return "<div class='mezcla' id='mezclaStrip'>"+
    vak(tp)+"<span class='mezOp'>+</span>"+vak(bl)+"<span class='mezOp'>=</span>"+
    (m ? "<span class='mezUit'><b class='es'>"+m.es+"</b><span>"+m.nl+"</span>"+
           (nieuw ? "<span class='mezNieuw'>"+ct("nieuw!","new!")+"</span>" : "")+"</span>"+
         "<button class='mezWis' id='btnMezWis' type='button'>"+ct("opnieuw","again")+"</button>"
       : "<span class='mezUit'><span>"+
           ct("Tik een tapa en een dans aan","Tap a tapa and a dance")+"</span></span>")+
    "</div>"+
    "<p class='zorglabel' id='mezclaTel'>"+
      ct("Je vond "+mezclaState().length+" van de "+mezclaTotaal()+" mezclas",
         "You found "+mezclaState().length+" of "+mezclaTotaal()+" mezclas")+"</p>";
}
/* Alleen de strip opnieuw tekenen en niet de hele kaart. Een hertekening van renderPet zou de
   tapa-rij en de dansrij laten knipperen terwijl er niets aan veranderd is, en dat leest als een
   foutje op precies het moment dat er iets leuks gebeurt. */
function mezclaTeken(nieuw){
  var strip = document.getElementById("mezclaStrip");
  if(!strip || !strip.parentNode) return;
  var tel = document.getElementById("mezclaTel");
  var wrap = document.createElement("div");
  wrap.innerHTML = mezclaHtml(nieuw);
  strip.parentNode.replaceChild(wrap.firstChild, strip);
  if(tel && tel.parentNode) tel.parentNode.replaceChild(wrap.lastChild, tel);
  var bw = document.getElementById("btnMezWis");
  if(bw) bw.onclick = mezclaWis;
}""")

# ---------------------------------------------------------------- 4. in het scherm
# De strip hoort tussen de twee vakken, niet in het dansvak. Eerst zat hij eronder, en dan staat de
# werkbank onder allebei de rijen in plaats van ertussen.
rep(
    """    "</div>"+
    "<div class='vitrinevak'>"+
      "<p class='bailehoy' id='baileHoy'>""",
    """    "</div>"+
    mezclaHtml(false)+
    "<div class='vitrinevak'>"+
      "<p class='bailehoy' id='baileHoy'>""")

rep(
    """      feedPet(tp);   // regelt zelf de lege-voorraadmelding, het slapen, en het opnieuw tekenen
    };
  });
}""",
    """      feedPet(tp);   // regelt zelf de lege-voorraadmelding, het slapen, en het opnieuw tekenen
      /* v23.34: en het vult het linkervakje van de mezcla. Na feedPet, want die kan de kaart
         opnieuw tekenen; dan staat er weer een verse strip om in te vullen. */
      try { mezclaKies("tapa", tp.id); } catch(e){}
    };
  });
}""")

rep(
    """      var bl = BAILES.filter(function(x){ return x.id === id; })[0];
      if(bl) chispaBaila(bl);""",
    """      var bl = BAILES.filter(function(x){ return x.id === id; })[0];
      if(bl) chispaBaila(bl);
      try { mezclaKies("baile", id); } catch(e){}""")

rep(
    """  chVerzamelWire(el);
  var bfi = document.getElementById("btnFiesta");""",
    """  chVerzamelWire(el);
  var bmw = document.getElementById("btnMezWis");
  if(bmw) bmw.onclick = mezclaWis;
  var bfi = document.getElementById("btnFiesta");""")

rep('var APP_VERSIE = "v23.33";', 'var APP_VERSIE = "v23.34";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
with io.open(PAD_VER, "w", encoding="utf-8") as f:
    f.write("v23.34\n")
print("v23.34 toegepast op", PAD)

SUITE = r'''// v23.34: la mezcla. Een tapa plus een dans wordt een naam, en die naam buigt mee.
//
// Wat hier vastligt:
//   - het bijvoeglijk naamwoord volgt het lidwoord van de tapa. Dit is het hele punt: het spelletje
//     drilt de overeenkomst tussen zelfstandig en bijvoeglijk naamwoord, en een fout hierin leert
//     iemand precies verkeerd. Vier vormen worden op de letter nagerekend.
//   - de bestaande gebaren veranderen niet. Een tapa aantikken voert haar nog steeds, een dans
//     aantikken laat haar nog steeds dansen; de mezcla ontstaat ernaast.
//   - een gevonden mezcla blijft staan, en de teller kan nooit boven zijn noemer uitkomen (zie de
//     tapateller van v23.33 en de luisterteller van v22.10: dat is hier een terugkerende fout).
const { chromium } = require('playwright');
let fout = 0;
function ok(c, m) { if (!c) { fout++; console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); }
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({ overgeslagen: true })); } catch (e) {} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Mez' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    S.lang = 'nl'; S.tour = true; S.tapas = 20;
    try { persist(); } catch (e) {}
    const w = document.getElementById('tourWrap'); if (w && w.remove) w.remove();
  });

  console.log('\n-- de vier vormen, op de letter --');
  const vormen = await page.evaluate(() => ({
    pulpo: mezclaMaak('pulpo', 'flamenco').es,
    aceitunas: mezclaMaak('aceitunas', 'salsa').es,
    tortilla: mezclaMaak('tortilla', 'tango').es,
    calamares: mezclaMaak('calamares', 'reggaeton').es,
    jarabe: mezclaMaak('bravas', 'jarabe').es,
    onzin: mezclaMaak('bestaat-niet', 'salsa')
  }));
  ok(vormen.pulpo === 'el pulpo flamenco', 'el (m enkelvoud): ' + vormen.pulpo);
  ok(vormen.aceitunas === 'las aceitunas salseras', 'las (v meervoud): ' + vormen.aceitunas);
  ok(vormen.tortilla === 'la tortilla tanguera', 'la (v enkelvoud): ' + vormen.tortilla);
  ok(vormen.calamares === 'los calamares reggaetoneros', 'los (m meervoud): ' + vormen.calamares);
  ok(vormen.jarabe === 'las patatas tapatías', 'en de kern zonder zijn staart: ' + vormen.jarabe);
  ok(vormen.onzin === null, 'een tapa die niet bestaat levert niets op, geen halve naam');

  console.log('\n-- alle 144 combinaties leveren een naam op --');
  const alle = await page.evaluate(() => {
    let n = 0, stuk = [];
    TAPAS.forEach((t) => BAILES.forEach((b) => {
      const m = mezclaMaak(t.id, b.id);
      if (!m || !/^(el|la|los|las) \S+ \S+$/.test(m.es)) stuk.push(t.id + '+' + b.id + ': ' + (m ? m.es : 'null'));
      else n++;
    }));
    return { n: n, stuk: stuk.slice(0, 4), totaal: TAPAS.length * BAILES.length };
  });
  ok(alle.n === alle.totaal, 'alle ' + alle.totaal + ' combinaties geven een lidwoord, een kern en een bijvoeglijk naamwoord ('
     + alle.n + ')' + (alle.stuk.length ? ' -- ' + alle.stuk.join(' | ') : ''));

  console.log('\n-- de strip staat tussen de tapas en de dansen --');
  await page.evaluate(() => show('chispa'));
  await page.waitForTimeout(600);
  const plek = await page.evaluate(() => {
    const s = document.getElementById('mezclaStrip');
    const t = document.getElementById('tapaMenuRij');
    const b = document.getElementById('baileRij');
    if (!s || !t || !b) return null;
    const y = (e) => e.getBoundingClientRect().top;
    return { inPet: !!s.closest('#petCard'), tussen: y(t) < y(s) && y(s) < y(b),
             leeg: s.querySelectorAll('.mezVak.leeg').length };
  });
  ok(plek && plek.inPet, 'de strip staat in de kaart van Chispa');
  ok(plek && plek.tussen, 'tussen de tapas en de dansen in');
  ok(plek && plek.leeg === 2, 'met twee lege vakjes om te beginnen (' + (plek ? plek.leeg : '-') + ')');

  console.log('\n-- aantikken doet nog steeds wat het deed, en vult het vakje --');
  const voor = await page.evaluate(() => ({ tapas: S.tapas || 0, bailes: (S.bailes || []).length }));
  await page.locator('#tapaMenuRij button.tapachip').first().click();
  await page.waitForTimeout(500);
  const naTapa = await page.evaluate(() => ({
    tapas: S.tapas || 0, gehad: (S.tapaMenu || []).length,
    vakken: document.querySelectorAll('#mezclaStrip .mezVak.leeg').length
  }));
  ok(naTapa.tapas === voor.tapas - 1, 'een tapa aantikken voert haar nog steeds (' + voor.tapas + ' -> ' + naTapa.tapas + ')');
  ok(naTapa.vakken === 1, 'en er is nog één vakje leeg (' + naTapa.vakken + ')');

  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(700);
  const naBaile = await page.evaluate(() => ({
    bailes: (S.bailes || []).length,
    mezclas: (S.mezcla || []).length,
    tekst: (document.getElementById('mezclaStrip') || {}).innerText || '',
    tel: (document.getElementById('mezclaTel') || {}).innerText || '',
    // op het woord "nieuw" zoeken kan niet: de knop ernaast heet "opnieuw". Dus op de markering zelf.
    nieuw: !!document.querySelector('#mezclaStrip .mezNieuw')
  }));
  ok(naBaile.bailes > voor.bailes, 'een dans aantikken laat haar nog steeds dansen');
  ok(naBaile.mezclas === 1, 'en samen leveren ze één gevonden mezcla op (' + naBaile.mezclas + ')');
  ok(/\S+ \S+/.test(naBaile.tekst) && !/\?/.test(naBaile.tekst), 'de uitkomst staat in de strip: ' + naBaile.tekst.replace(/\n/g, ' | '));
  ok(naBaile.nieuw, 'met erbij dat hij nieuw is');

  console.log('\n-- dezelfde nog eens telt niet dubbel --');
  await page.locator('#tapaMenuRij button.tapachip').first().click();
  await page.waitForTimeout(300);
  await page.locator('#baileRij button.bailechip').first().click();
  await page.waitForTimeout(500);
  const weer = await page.evaluate(() => ({
    mezclas: (S.mezcla || []).length,
    nieuw: !!document.querySelector('#mezclaStrip .mezNieuw')
  }));
  ok(weer.mezclas === 1, 'dezelfde combinatie telt niet twee keer (' + weer.mezclas + ')');
  ok(!weer.nieuw, 'en hij doet ook niet alsof hij nieuw is');

  console.log('\n-- de teller kan niet boven zijn noemer uitkomen --');
  const tel = await page.evaluate(() => {
    S.mezcla = (S.mezcla || []).concat(['bestaat-niet|salsa']);
    mezclaTeken(false);
    const t = (document.getElementById('mezclaTel') || {}).innerText || '';
    const m = t.match(/(\d+)\D+(\d+)/);
    return { tekst: t, gevonden: m ? +m[1] : -1, totaal: m ? +m[2] : -1, echt: TAPAS.length * BAILES.length };
  });
  ok(tel.totaal === tel.echt, 'de noemer is achttien maal acht (' + tel.totaal + ')');
  ok(tel.gevonden <= tel.totaal, 'en de teller blijft eronder (' + tel.tekst.replace(/\n/g, ' ') + ')');

  console.log('\n-- opnieuw maakt de vakjes leeg --');
  await page.evaluate(() => { mezclaTapa = 'pulpo'; mezclaBaile = 'tango'; mezclaTeken(false); });
  await page.waitForTimeout(200);
  await page.click('#btnMezWis');
  await page.waitForTimeout(300);
  const leeg = await page.evaluate(() => document.querySelectorAll('#mezclaStrip .mezVak.leeg').length);
  ok(leeg === 2, 'na "opnieuw" staan er weer twee lege vakjes (' + leeg + ')');

  const echt = errors.filter((e) => !/Failed to load resource|net::/.test(e));
  ok(echt.length === 0, 'geen JS-fouten (' + echt.length + ')');
  if (echt.length) echt.forEach((e) => console.log('  -> ' + e));

  await browser.close();
  console.log(fout === 0 ? '\nALLE PLAYWRIGHT-TESTS GESLAAGD' : '\n' + fout + ' PLAYWRIGHT-TEST(S) GEFAALD');
  process.exit(fout === 0 ? 0 : 1);
})();
'''

pad_s = os.path.join(MAP_S, "pw-mezcla.js")
if os.path.exists(pad_s):
    print("  pw-mezcla.js: bestaat al")
else:
    with io.open(pad_s, "w", encoding="utf-8") as f:
        f.write(SUITE)
    print("  pw-mezcla.js: aangemaakt")
