#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.26: een boekenplank voor het lezen, met per boek hoe ver je bent en hoe zwaar het voor jou is.

Onder Lezen stonden 23 hoofdstukken onder elkaar, gegroepeerd op deel. Dat werkte toen er één verhaal
was. Nu er twee boeken staan, en er straks meer komen, is de eerste vraag welk boek je wilt, en pas
daarna welk hoofdstuk.

Twee getallen per boek, en allebei zijn ze gemeten en niet geschat.

Hoe ver ben je: het aantal hoofdstukken dat je hebt afgerond, gedeeld door het totaal. Simpel, en het
is het enige percentage in deze app dat wél gewoon een percentage mag zijn, want teller en noemer
staan allebei vast.

Hoe zwaar is het voor jou: het aantal woorden per zin dat je nog niet kent. Dat is de maat die uit de
metingen van vandaag kwam als de enige die iets zegt. Niet een percentage dekking, want daar kun je
met drie redelijke definities drie verschillende antwoorden op krijgen (37, 62 en 75 procent voor
dezelfde tekst), en niet een CEFR-niveau, want dat zou een label zijn dat we niet kunnen onderbouwen.

Bekend is hier: een woord dat in jouw doosjes zit, of een van de achthonderd meest voorkomende
woorden van het Spaans. Het getal beweegt dus mee terwijl je leert: een boek dat vandaag zwaar is,
staat over een maand op pittig. Dat is precies de bedoeling.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function leesPlankHtml()" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. opmaak
rep(
    """  .lw{cursor:pointer; border-radius:3px; padding:0 1px; margin:0 -1px;}""",
    """  /* v23.26: de boekenplank. Een kaart per boek, met de balk die je van Vandaag kent. */
  .plankKop{display:flex; justify-content:space-between; align-items:baseline; gap:8px;}
  .plankSoort{font-size:.72rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted);}
  .plankBalk{height:8px; border-radius:4px; background:var(--border); overflow:hidden; margin:8px 0 6px;}
  .plankBalk div{height:100%; background:var(--accent);}
  .lw{cursor:pointer; border-radius:3px; padding:0 1px; margin:0 -1px;}""")

# ---------------------------------------------------------------- 2. de reeksen en de maten
rep(
    """function renderBoekMenu(){""",
    """/* ================= DE BOEKENPLANK (v23.26) =================
   Een reeks is een boek. Ze staan hier los van de hoofdstukken zelf, want een hoofdstuk hoort te
   weten waar het over gaat en niet hoe de kast eruitziet. */
var LEES_REEKSEN = [
 {id:"chispa", pre:"boek-", nl:"Chispa", en:"Chispa",
  soortNl:"verhaal", soortEn:"story",
  omNl:"Een wezentje zonder naam zoekt zijn eigen lied, van de kust tot het kasteel.",
  omEn:"A small creature without a name looks for its own song, from the coast to the castle."},
 {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco",
  soortNl:"geschiedenis", soortEn:"history",
  omNl:"Spanje van 1931 tot nu, in tien hoofdstukken: de oorlog, de honger, de stilte en de terugweg.",
  omEn:"Spain from 1931 until now, in ten chapters: the war, the hunger, the silence and the way back."}
];
var leesReeks = null;                     // welk boek staat open; null is de plank zelf
function leesReeksVan(h){
  for(var i = 0; i < LEES_REEKSEN.length; i++){
    if(String(h.id).indexOf(LEES_REEKSEN[i].pre) === 0) return LEES_REEKSEN[i];
  }
  return null;
}
/* Wat telt als bekend: een woord dat in jouw doosjes zit, plus de achthonderd meest voorkomende
   woorden van het Spaans. Die tweede groep moet erbij, anders zou "de", "que" en "en" als onbekend
   tellen en dan meet je vooral of iemand toevallig lidwoorden als leskaart heeft staan.

   Eenmaal opgebouwd per render, want dit loopt over een paar duizend woorden. */
var _leesBekend = null;
function leesBekendeSet(){
  if(_leesBekend) return _leesBekend;
  var s = {}, i, j, w, delen;
  for(i = 0; i < Math.min(800, (typeof FREQ !== "undefined" ? FREQ.length : 0)); i++){
    s[stripAcc(FREQ[i][0].toLowerCase()).replace(/[^a-z]/g, "")] = 1;
  }
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    if(!S.srs[w.id]) continue;
    delen = String(w.es).toLowerCase().replace(/\\([^)]*\\)/g, " ").split(/[\\/,]/);
    for(j = 0; j < delen.length; j++){
      stripAcc(delen[j]).replace(/[^a-z ]/g, "").split(" ").forEach(function(t){ if(t) s[t] = 1; });
    }
  }
  _leesBekend = s;
  return s;
}
/* Onbekende woorden per zin. Deze maat en niet een dekkingspercentage: op een dekking kun je met
   drie redelijke definities drie verschillende antwoorden krijgen, en dit is te tellen. */
function leesZwaarte(reeks){
  var bekend = leesBekendeSet(), tok, zin, onb = 0, zinnen = 0, i, j;
  for(i = 0; i < BOOK.length; i++){
    if(String(BOOK[i].id).indexOf(reeks.pre) !== 0) continue;
    tok = BOOK[i].tekst.split(/[^A-Za-z\\u00c0-\\u024f]+/).filter(Boolean);
    for(j = 0; j < tok.length; j++){
      if(!bekend[stripAcc(tok[j].toLowerCase()).replace(/[^a-z]/g, "")]) onb++;
    }
    zin = BOOK[i].tekst.split(/[.!?\\u2026]+/).filter(function(x){ return x.trim().length > 3; });
    zinnen += zin.length;
  }
  if(!zinnen) return null;
  return onb / zinnen;
}
function leesZwaarteWoord(z){
  if(z === null) return "";
  if(z < 1) return ct("goed te doen","comfortable");
  if(z < 2) return ct("pittig","demanding");
  return ct("zwaar","heavy");
}
function leesPlankHtml(){
  var h = "";
  LEES_REEKSEN.forEach(function(r){
    var hst = BOOK.filter(function(x){ return String(x.id).indexOf(r.pre) === 0; });
    if(!hst.length) return;
    var af = hst.filter(function(x){ return S.boek[x.id] && S.boek[x.id].done; }).length;
    var pct = Math.round(100 * af / hst.length);
    var z = leesZwaarte(r);
    h += "<div class='card'><div class='plankKop'><h2 style='margin:0'>"+(profLang() === "nl" ? r.nl : r.en)+"</h2>"+
        "<span class='plankSoort'>"+(profLang() === "nl" ? r.soortNl : r.soortEn)+"</span></div>"+
      "<p class='muted' style='margin:4px 0 0; font-size:.88rem'>"+(profLang() === "nl" ? r.omNl : r.omEn)+"</p>"+
      "<div class='plankBalk'><div style='width:"+pct+"%'></div></div>"+
      "<p class='muted' style='margin:0; font-size:.85rem'>"+
        ct(af+" van de "+hst.length+" hoofdstukken gelezen ("+pct+"%)",
           af+" of "+hst.length+" chapters read ("+pct+"%)")+"</p>"+
      (z === null ? "" :
        "<p class='muted' style='margin:4px 0 0; font-size:.85rem'>"+
          ct("Voor jou nu: <b>"+leesZwaarteWoord(z)+"</b>, ongeveer "+getal1(z)+" onbekende woorden per zin.",
             "For you right now: <b>"+leesZwaarteWoord(z)+"</b>, about "+getal1(z)+" unknown words per sentence.")+"</p>")+
      "<div class='row' style='margin-top:10px'><button class='"+(af ? "ghost" : "primary")+"' data-reeks='"+r.id+"'>"+
        (af && af < hst.length ? ct("Verder lezen","Keep reading")
                               : (af ? ct("Nog eens lezen","Read again") : ct("Beginnen","Start")))+" \\u2192</button></div>"+
      "</div>";
  });
  return h;
}

function renderBoekMenu(){""")

# ---------------------------------------------------------------- 3. het menu in twee lagen
rep(
    """function renderBoekMenu(){
  var el = document.getElementById("lezenMenu");
  var html = "";
  var huidigDeel = null;
  BOOK.forEach(function(h){""",
    """function renderBoekMenu(){
  var el = document.getElementById("lezenMenu");
  _leesBekend = null;                       // per render opnieuw: je doosjes veranderen
  if(!leesReeks){
    el.innerHTML = leesPlankHtml();
    el.querySelectorAll("button[data-reeks]").forEach(function(b){
      b.onclick = function(){ leesReeks = b.getAttribute("data-reeks"); renderBoekMenu(); };
    });
    return;
  }
  var reeks = LEES_REEKSEN.filter(function(r){ return r.id === leesReeks; })[0];
  var html = "<div class='row' style='margin-bottom:6px'><button class='ghost' id='btnPlankTerug'>\\u2190 "+
      ct("Alle boeken","All books")+"</button></div>"+
    "<h2 style='margin:0 0 2px'>"+(profLang() === "nl" ? reeks.nl : reeks.en)+"</h2>";
  var huidigDeel = null;
  BOOK.filter(function(h){ return String(h.id).indexOf(reeks.pre) === 0; }).forEach(function(h){""")

rep(
    """  el.innerHTML = html;
  el.querySelectorAll("button[data-boek]").forEach(function(b){
    b.onclick = function(){ startBoek(b.getAttribute("data-boek")); };
  });
}""",
    """  el.innerHTML = html;
  var bt = document.getElementById("btnPlankTerug");
  if(bt) bt.onclick = function(){ leesReeks = null; renderBoekMenu(); };
  el.querySelectorAll("button[data-boek]").forEach(function(b){
    b.onclick = function(){ startBoek(b.getAttribute("data-boek")); };
  });
}""")

# de kop van een deel alleen tonen als het boek er meer dan een heeft
rep(
    """    if(h.deel !== huidigDeel){ huidigDeel = h.deel; html += "<p style='margin:14px 0 4px'><b>"+huidigDeel+"</b></p>"; }""",
    """    // de deelkop alleen als hij iets toevoegt: bij Franco heet elk deel hetzelfde als het boek
    if(h.deel !== huidigDeel && h.deel !== reeks.nl){
      huidigDeel = h.deel; html += "<p style='margin:14px 0 4px'><b>"+huidigDeel+"</b></p>";
    }""")

rep('var APP_VERSIE = "v23.25";', 'var APP_VERSIE = "v23.26";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.26 toegepast op", PAD)
