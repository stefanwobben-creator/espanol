#!/usr/bin/env python3
# v23.202 - de Door-knop hangt aan het scherm waar hij op staat
# (gebouwd als v23.197; hernummerd naar v23.202 omdat de nachtrun v23.197 onder ons uit main pakte)
#
# Stefan, 26 aug: "ben met de dagles bezig en kom niet verder" (stap 4/6, toetsjes, 5/6).
# Eerder al op 23 aug ("gisteren tijdens de dagoefening liep ik vast, de volgende knop werkte net")
# en op 24 aug.
#
# WAT ER MIS WAS
#
# Zes schermen tekenen een "Door →" knop. Vier ervan gaven hem hetzelfde id:
#
#   renderFunRompecabezas()        tab-speeltuin    id="btnLesFlowDoor"
#   renderConjugadorRondeKlaar()   tab-speeltuin    id="btnLesFlowDoor"
#   renderFunLes()                 tab-speeltuin    id="btnLesFlowDoor"
#   renderQuestion()               tab-toetsjes     id="btnLesFlowDoor"
#
# tab-speeltuin staat in de pagina vóór tab-toetsjes. show() verbergt een tabblad, het gooit de
# inhoud niet weg, dus de knop van de vormenstap blijft staan als de toets begint. En dan doet de
# toetsuitslag dit:
#
#   document.getElementById("btnLesFlowDoor").onclick = function(){ lesFlowVolgende(); };
#
# getElementById geeft de eerste in de pagina. De klikafhandeling ging dus naar de onzichtbare knop
# uit de vorige stap, en de knop die Stefan aankeek had er geen. Nagemeten in de app:
#
#   aantal knoppen met dit id : 2
#   getElementById geeft      : de oude knop in de speeltuin
#   handler op de zichtbare   : nee
#   handler op de oude        : ja
#
# Daarom was het "soms": alleen op dagen dat de vormenstap draait blijft die knop achter. En daarom
# ving de bodem van v23.188 het niet: die vraagt "is er een scherm opengegaan", en er werd helemaal
# niets aangeroepen. Een bodem onder een functie die nooit begint, ligt op de verkeerde plek.
#
# DE REPARATIE, EN WAAROM NIET "GEEF ZE VIER VERSCHILLENDE ID'S"
#
# Vier id's is vier plekken die uniek moeten blijven ten opzichte van elkaar, en dat is precies het
# soort afspraak dat na twee versies uit elkaar loopt. De echte fout zit een laag dieper: er werd
# gezocht in het hele document terwijl bekend was in wélk element net getekend was.
#
# Vanaf nu tekent en koppelt één plek de knop, en de koppeling is gebonden aan de container:
#
#   lesFlowDoorHtml     de knop, met een class in plaats van een id
#   lesFlowDoorBind     zoekt hem binnen de meegegeven container, en nergens anders
#
# Alle zes de plekken gebruiken dat, ook de twee die vandaag nog geen botsing hadden (musica en
# audición). Twee overslaan omdat ze nu toevallig uniek zijn, is twee kansen laten liggen.
#
# WAT DE PROEF METEN GAAT (test/suites/pw-doorknop.js)
#
#   1. DE ZICHTBARE DOOR-KNOP HEEFT EEN KLIKAFHANDELING. Dat is de eigenlijke regel, en hij wordt
#      gemeten in precies de volgorde die stukging: eerst een vormenstap die een knop achterlaat,
#      dan de toetsuitslag.
#   2. EN HIJ BRENGT JE VERDER. Het controlegeval bij 1: een knop met een lege functie eraan haalt
#      proef 1 wel en helpt Stefan niet.
#   3. GEEN ENKEL ID KOMT TWEE KEER VOOR in de hele pagina, op elke stap van de dagles. Dit is de
#      algemene regel waar de Door-knop een geval van was, en hij meet ook de plekken die ik niet
#      heb bekeken.
#   4. HET CONTROLEGEVAL BIJ 3: de meting vindt een dubbel id wel degelijk als je er een neerzet.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.202"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function lesFlowDoorBind(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:100])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de ene plek
# =============================================================================================
HELPER = r'''/* v23.197: de "Door →" knop van de dagles, op één plek.

   Hier stonden zes losse kopieën, waarvan vier met hetzelfde id (btnLesFlowDoor). Drie daarvan
   wonen in tab-speeltuin, dat in de pagina vóór tab-toetsjes staat, en show() verbergt een tabblad
   zonder de inhoud weg te gooien. Stond er dus een vormenblok in je dagles, dan bleef die knop
   staan, gaf document.getElementById() hém in plaats van de knop op de toetsuitslag, en kreeg de
   knop die je aankeek nooit een klikafhandeling. Dat is de vastloper van 23, 24 en 26 augustus.

   De reparatie is niet "vier verschillende id's" maar "zoek niet in het hele document als je weet
   in welk element je net getekend hebt". De bind-functie krijgt die container mee en kijkt er
   niet buiten. Daarmee kan een oude knop in een ander tabblad er per constructie niet meer
   tussenkomen, en maakt het niet uit hoeveel schermen deze knop tekenen. */
function lesFlowDoorHtml(label){
  return "<button class='primary lesflow-door'>" + (label || ct("Door →", "Continue →")) + "</button>";
}
function lesFlowDoorBind(el, fn){
  if(!el) return null;
  var b = el.querySelector(".lesflow-door");
  if(!b) return null;
  b.onclick = fn || function(){ lesFlowVolgende(); };
  return b;
}

'''

if DOE_APP:
    rep("function lesFlowVolgende(){\n", HELPER + "function lesFlowVolgende(){\n")

# =============================================================================================
# 2. de zes plekken die hem tekenen
# =============================================================================================
if DOE_APP:
    # --- renderFunRompecabezas (speeltuin) ---
    rep("""      (inFlow ? "<div class='row' style='margin-top:10px'><button class='primary' id='btnLesFlowDoor'>" + ct("Door →","Continue →") + "</button></div>\"""",
        """      (inFlow ? "<div class='row' style='margin-top:10px'>" + lesFlowDoorHtml() + "</div>\"""")
    rep("""    if(inFlow){ document.getElementById("btnLesFlowDoor").onclick = function(){ lesFlowVolgende(); }; return; }""",
        """    if(inFlow){ lesFlowDoorBind(el); return; }""")

    # --- renderConjugadorRondeKlaar (speeltuin) ---
    rep("""    (inFlowCj ? "<div class='row'><button class='primary' id='btnLesFlowDoor'>"+ct("Door →","Continue →")+"</button></div>\"""",
        """    (inFlowCj ? "<div class='row'>" + lesFlowDoorHtml() + "</div>\"""")
    rep("""  if(inFlowCj){
    document.getElementById("btnLesFlowDoor").onclick = function(){ lesFlowVolgende(); };
    return;
  }""",
        """  if(inFlowCj){
    lesFlowDoorBind(el);
    return;
  }""")

    # --- renderFunLes (speeltuin) ---
    rep("""          (inFlowLes
            ? "<button class='primary' id='btnLesFlowDoor'>" + ct("Door \\u2192", "Continue \\u2192") + "</button>\"""",
        """          (inFlowLes
            ? lesFlowDoorHtml()""")
    rep("""      var bd = document.getElementById("btnLesFlowDoor");
      if(bd) bd.onclick = function(){ if(gehaald) lesStapAf(); lesSpel = null; lesFlowVolgende(); };""",
        """      lesFlowDoorBind(el, function(){ if(gehaald) lesStapAf(); lesSpel = null; lesFlowVolgende(); });""")

    # --- renderQuestion (toetsjes) - dit is de knop die Stefan aankeek ---
    rep("""        "<div class='row'><button class='primary' id='btnLesFlowDoor'>"+ct("Door →","Continue →")+"</button></div>";
      document.getElementById("btnLesFlowDoor").onclick = function(){ lesFlowVolgende(); };""",
        """        "<div class='row'>" + lesFlowDoorHtml() + "</div>";
      lesFlowDoorBind(el);""")

    # --- renderSongQuiz (musica) - vandaag nog geen botsing, wel hetzelfde patroon ---
    rep("""        ? "<div class='row' style='margin-top:8px'><button class='primary' id='btnMusFlowDoor'>"+ct("Door →","Continue →")+"</button></div>"
        : "");
    var door = document.getElementById("btnMusFlowDoor");
    if(door) door.onclick = function(){ lesFlowVolgende(); };""",
        """        ? "<div class='row' style='margin-top:8px'>" + lesFlowDoorHtml() + "</div>"
        : "");
    lesFlowDoorBind(el);""")

    # --- renderFunAudicion (speeltuin) ---
    rep("""        ? "<div class='row' style='margin-top:8px'><button class='primary' id='btnAudFlowDoor'>" + ct("Door →","Continue →") + "</button></div>\"""",
        """        ? "<div class='row' style='margin-top:8px'>" + lesFlowDoorHtml() + "</div>\"""")
    rep("""  var bf = document.getElementById("btnAudFlowDoor");
  if(bf) bf.onclick = function(){ audStop(); persist(); lesFlowVolgende(); };""",
        """  lesFlowDoorBind(el, function(){ audStop(); persist(); lesFlowVolgende(); });""")

# =============================================================================================
# 3. en geen enkel spoor van de oude id's
# =============================================================================================
if DOE_APP:
    # de toelichting in de code noemt de oude naam, dus deze controle kijkt naar code en niet naar
    # het woord: een attribuut dat gezet wordt, of een opzoeking in het hele document.
    for oud in ["btnLesFlowDoor", "btnMusFlowDoor", "btnAudFlowDoor"]:
        for vorm in ["id='%s'" % oud, 'id="%s"' % oud, 'getElementById("%s")' % oud]:
            assert vorm not in src, "staat er nog: %s" % vorm
    assert src.count("lesFlowDoorHtml()") == 6, "verwacht zes knoppen, gevonden %d" % src.count("lesFlowDoorHtml()")
    assert src.count("lesFlowDoorBind(el") == 7, "verwacht zes koppelingen plus de definitie, gevonden %d" % src.count("lesFlowDoorBind(el")

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    APP.write_text(src, encoding="utf-8")
    print("index.html: de Door-knop komt uit één plek en hangt aan zijn eigen scherm")
else:
    print("index.html: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
