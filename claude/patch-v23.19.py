#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.19: dit beheers je, dit is je zwakke plek.

Stefan wilde inzicht in waar zijn sterke en zwakke punten zitten, zodat hij gericht kan oefenen. Die
kennis lag er al, alleen verspreid over vijf plekken: S.errors, S.gram, S.comp, S.conjFase en de tags
op de woorden. Geen enkele functie bracht het bij elkaar, en dat is precies waarom het tweede deel
van de dag zijn spelletjes nog met een dobbelsteen kiest (dayHash) in plaats van met een reden.

zwakkePunten() is het broertje van voortgangCijfers(): één functie, alle schermen roepen hem aan.

Waarom dit op de doosjes rekent en niet op fouten. Fouten tellen straft oefenen af, precies zoals
Stefan zelf over dat opgetelde foutenaantal zei. In zijn eigen cijfers is dat direct te zien:
kern-mensen had acht fouten en kern-school maar twee, dus op fouten geteld lijkt school zijn sterkste
thema. In werkelijkheid staat school volledig in doos 2 en heeft mensen er al zeven in doos 3. De
doosjes meten wat er nu staat, niet wat er onderweg is misgegaan.

Het is dezelfde weging als het getal op Vandaag, alleen per thema in plaats van over alles. Dus als
je de thema's optelt kom je uit op de 195 die daar staat.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function zwakkePunten()" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. de functie
rep(
    """function krachtGewicht(box){""",
    """/* ================= WAAR ZIT JE STERK EN WAAR NIET (v23.19) =================
   Eén functie, net als voortgangCijfers(). Wat hier uitkomt voedt straks ook het tweede deel van de
   dag, dat nu nog met dayHash() een spelletje uitkiest.

   De maat is dezelfde als die van het getal op Vandaag: hoe ver staan je woorden in de doosjes,
   gewogen naar het herhaalinterval. Per thema in plaats van over alles. Tel je de thema's op, dan
   kom je uit op datzelfde getal, en dat is geen toeval maar de bedoeling.

   Bewust niet op fouten geteld. Een thema dat je vaak oefent verzamelt vanzelf de meeste fouten, dus
   dan wordt "waar oefen ik het meest" verkocht als "waar ben ik slecht in". Bij Stefan draait dat
   het antwoord om: kern-school had twee fouten en kern-mensen acht, terwijl school volledig in doos
   2 staat en mensen er al zeven in doos 3 heeft. */
var THEMA_MIN = 8;     // minder woorden en een percentage zegt niets
var GRAM_MIN = 5;      // minder beurten op een regel en het doosje is toeval
var THEMA_OVERSLAAN = {basis:1, woorden:1};
/* De kernwoorden en de Cervantes-woorden zijn los van elkaar getagd, dus er staan namen naast elkaar
   die hetzelfde bedoelen: winkel en winkelen, gezond en gezondheid, gevoel en gevoelens. Onopgelost
   levert dat twee halve thema's op die allebei te klein zijn om iets te zeggen, en een lijst waarin
   je jezelf twee keer tegenkomt. Hier staan ze bij elkaar. Meteen ook de rubrieknamen uit Cervantes
   die als los woord niets zeggen: "waar" en "wanneer" zijn plaats en tijd. */
var THEMA_SAMEN = {"winkel":"winkelen", "gezond":"gezondheid", "gevoel":"gevoelens",
                   "vrijetijd":"vrije tijd", "geloof":"religie", "waar":"plaats", "wanneer":"tijd",
                   "hoe":"eigenschappen", "hoeveel":"hoeveelheid", "wie je bent":"persoonlijk"};
/* De tags zijn Nederlands, en die stonden zo op het scherm van een Engelse gebruiker. pw-taal ving
   dat op "werkwoorden", maar het probleem was breder: elk thema was een Nederlands woord. Groeperen
   gebeurt daarom op de Nederlandse sleutel (taalonafhankelijk) en pas bij het tonen wordt vertaald. */
var THEMA_EN = {
  "bestaan":"existence", "denken":"thinking", "diensten":"services", "economie":"economy",
  "eigenschap":"qualities", "eigenschappen":"qualities", "eten":"food", "gevoelens":"feelings",
  "gezondheid":"health", "hoeveelheid":"quantity", "karakter":"character", "kunst":"arts",
  "lichaam":"body", "media":"media", "mensen":"people", "natuur":"nature", "oordeel":"judgement",
  "plaats":"place", "politiek":"politics", "reizen":"travel", "relaties":"relationships",
  "religie":"religion", "samenleving":"society", "school":"school", "techniek":"technology",
  "tijd":"time", "vrije tijd":"free time", "werk":"work", "winkelen":"shopping", "wonen":"housing",
  "persoonlijk":"personal", "biografie":"biography", "familie":"family", "getallen":"numbers",
  "leren":"learning", "werkwoorden":"verbs"
};
function themaSleutel(tag){
  var n = String(tag || "").replace(/^(cerv|kern)-/, "").replace(/-/g, " ");
  return THEMA_SAMEN[n] || n;
}
function themaToon(sleutel){
  if(profLang() === "nl") return sleutel;
  return THEMA_EN[sleutel] || sleutel;
}
/* les1 en boek-3 zijn geen thema's maar vindplaatsen. "Je bent zwak in les 2" zegt niemand iets,
   en het zou de lijst vullen met rijen waar je niets mee kunt. cerv- en kern- gaan er zonder prefix
   in, zodat cerv-school en kern-school samen één thema zijn in plaats van twee halve. */
function themaMeetelt(tag){
  if(!tag) return false;
  if(/^(les|boek)/.test(tag)) return false;
  return !THEMA_OVERSLAAN[themaSleutel(tag)];
}
function gramNaam(id){
  var i, c;
  for(i = 0; i < GC_CONCEPTEN.length; i++){
    c = GC_CONCEPTEN[i];
    if(c.id === id) return profLang() === "nl" ? c.naam : (c.naamEn || c.naam);
  }
  return id;
}
function zwakkePunten(){
  var perThema = {}, i, w, st, nm;
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    st = S.srs[w.id];
    if(!st || typeof st !== "object") continue;
    if(!themaMeetelt(w.tag)) continue;
    nm = themaSleutel(w.tag);
    perThema[nm] = perThema[nm] || {n:0, som:0};
    perThema[nm].n++;
    perThema[nm].som += krachtGewicht(st.box || 0);
  }
  var themas = [];
  for(nm in perThema){
    if(perThema[nm].n < THEMA_MIN) continue;
    themas.push({sleutel:nm, naam:themaToon(nm), n:perThema[nm].n,
                 kracht:Math.round(100 * perThema[nm].som / perThema[nm].n)});
  }
  themas.sort(function(a, b){ return a.kracht - b.kracht || b.n - a.n; });
  var regels = [], k, g, beurten, top = GRAM_INTERVALS[GRAM_INTERVALS.length - 1] || 150;
  for(k in (S.gram || {})){
    g = S.gram[k];
    if(!g || typeof g !== "object") continue;
    beurten = (g.goed || 0) + (g.fout || 0);
    if(beurten < GRAM_MIN) continue;
    regels.push({sleutel:k, naam:gramNaam(k), beurten:beurten, goed:(g.goed || 0), fout:(g.fout || 0),
                 kracht:Math.round(100 * (GRAM_INTERVALS[g.box || 0] || 0) / top)});
  }
  regels.sort(function(a, b){ return a.kracht - b.kracht || b.fout - a.fout; });
  return {themas:themas, regels:regels};
}

function krachtGewicht(box){""")

# ---------------------------------------------------------------- 2. het blok op je profiel
rep(
    """function krachtTabelHtml(){""",
    """/* Twee korte lijstjes en geen lange. Wie tien thema's op een rij ziet gaat er geen een van
   oefenen; dat is de eerste bevinding van Stefans moeder, te veel op één scherm. Drie boven en drie
   onder, en de rest kun je uit de uitsplitsing halen als je hem echt wilt. */
function sterkZwakHtml(){
  var z = zwakkePunten();
  // minder dan vier thema's is geen vergelijking maar een lijstje, en dan zegt boven en onder niets
  if(z.themas.length < 4 && z.regels.length < 2) return "";
  function rij(x, eenheid){
    return "<div class='cijfRij'><div class='cijfW'>"+x.kracht+"%</div>"+
      "<div class='cijfT'>"+x.naam+"<span>"+x.n+" "+eenheid+"</span></div></div>";
  }
  var h = "<h2 style='margin-top:16px'>"+ct("Dit beheers je, dit is je zwakke plek",
                                            "What you have down, and where the gaps are")+"</h2>"+
    "<p class='muted' style='margin:0 0 6px'>"+
      ct("Hoe ver je woorden per thema in de doosjes staan, met dezelfde weging als het getal op "+
         "Vandaag. Niet het aantal fouten: een thema dat je vaak oefent verzamelt vanzelf de meeste "+
         "fouten, en dan lijkt oefenen een zwakte.",
         "How far your words sit in the boxes per topic, weighted the same way as the number on "+
         "Today. Not the number of mistakes: a topic you practise a lot collects the most mistakes, "+
         "which would make practice look like a weakness.")+"</p>";
  if(z.themas.length >= 4){
    var zwak = z.themas.slice(0, 3), sterk = z.themas.slice(-3).reverse();
    h += "<p class='muted' style='margin:10px 0 2px; font-size:.85rem'>"+
        ct("Hier zit je het verst","Furthest along")+"</p><div class='cijfLijst'>"+
      sterk.map(function(x){ return rij(x, ct("woorden","words")); }).join("")+"</div>"+
      "<p class='muted' style='margin:10px 0 2px; font-size:.85rem'>"+
        ct("Hier valt het meest te halen","Most to gain here")+"</p><div class='cijfLijst'>"+
      zwak.map(function(x){ return rij(x, ct("woorden","words")); }).join("")+"</div>";
  }
  /* Alleen regels die echt wankelen. Zonder die grens vulde deze lijst zich met de drie laagste
     die er waren, ook als dat er een van honderd procent was, en dan staat er een regel onder het
     kopje "wankelt nog" die juist vaststaat. */
  var wankel = z.regels.filter(function(x){ return x.kracht < 60; });
  if(wankel.length >= 2){
    var gz = wankel.slice(0, 3);
    h += "<p class='muted' style='margin:10px 0 2px; font-size:.85rem'>"+
        ct("Grammatica die nog wankelt","Grammar that still wobbles")+"</p><div class='cijfLijst'>"+
      gz.map(function(x){
        return "<div class='cijfRij'><div class='cijfW'>"+x.kracht+"%</div>"+
          "<div class='cijfT'>"+x.naam+"<span>"+
            ct(x.goed+" goed, "+x.fout+" fout", x.goed+" right, "+x.fout+" wrong")+"</span></div></div>";
      }).join("")+"</div>";
  }
  return h;
}

function krachtTabelHtml(){""")

rep(
    """    krachtTabelHtml()+""",
    """    krachtTabelHtml()+
    sterkZwakHtml()+""")

# ---------------------------------------------------------------- 3. versie
rep('var APP_VERSIE = "v23.18";', 'var APP_VERSIE = "v23.19";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.19 toegepast op", PAD)
