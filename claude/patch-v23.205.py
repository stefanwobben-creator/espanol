#!/usr/bin/env python3
# v23.205 - het schrijven staat niet meer achteraan, en de app noteert welke stand je hielp
# (gebouwd als v23.200; hernummerd naar v23.205 omdat de nachtrun v23.199 en v23.201 onder ons uit main pakte)
#
# Stefan, 27 aug: "ik heb trouwens idee dat zinnen maken, typen ook heel goed werkt" en
# "ik denk gewoon beginnen met simpele zinnen en dan langzaam opbouwen, dan werkt het".
#
# WAT ER AL WAS, EN WAAROM DAT NIET HET PUNT IS
#
# Die opbouw bestaat. pickSentence() snijdt op zwaarte met vertPlafond(), zes tredes, omhoog na drie
# goede eerste pogingen en omlaag na twee foute:
#
#     trede 1  max 6 woorden     64 van de 265 zinnen
#     trede 2  max 8            139
#     trede 3  max 10           205
#     trede 4  max 13           248
#     trede 5  max 16           263
#     trede 6  alles            265
#
# Het probleem is niet dat de ladder ontbreekt maar dat Stefan er nauwelijks op staat. Uit zijn
# eigen logboek, aantal keer geopend over 38 dagen:
#
#     spiekbrief 42 · oefenen 41 · gramles 37 · speeltuin 28 · woorden 26 · ... · vertalen 4
#
# Vier keer. De vorm waarvan hij zegt dat hij het beste werkt is een van de minst bezochte schermen
# van de app.
#
# WAAROM: HET SCHRIJVEN STAAT ACHTER HET LEESBLOK
#
# De dagles loopt woorden → grammatica → vormen → toetsje → lezen/luisteren → schrijven. Dat leesblok
# is een heel hoofdstuk. v23.140 zette input bewust vóór productie ("eerst input, dan pas zelf iets
# maken") en die redenering klopt binnen één sessie, maar alleen als je ze allebei haalt. Gemeten
# haalt hij ze niet allebei: lezen 16 keer, schrijven 4 keer.
#
# Dus wisselen die twee van plaats: toetsje → schrijven → lezen/luisteren. Dit is een omkering van
# een eerdere beslissing en niet het repareren van een fout, en dat hoort er zo te staan. De grond
# eronder is niet "productie hoort voor input" maar "drie zinnen typen duurt twee minuten en een
# hoofdstuk lezen een kwartier, en het korte blok hoort niet achter het lange te wachten".
#
# EN DE APP NOTEERT VOORTAAN WELKE STAND JE HIELP
#
# Stefans waarneming is nu niet te toetsen. Een zin draagt wel of hij gehaald is (S.done) en of er een
# fout open staat, maar niet in wélke stand het goede antwoord kwam. Daardoor is "typen werkt beter
# dan tegels" een gevoel en blijft het dat.
#
# S.zinRoute[id] = {r:"typ"|"tegel", d:datum} bij elk goed antwoord. Over twee weken is de vraag dan
# te beantwoorden op zijn eigen data: van de zinnen die het laatst via typen goed gingen, hoeveel
# hebben er sindsdien een nieuwe fout opgelopen, tegenover de zinnen die het laatst via tegels goed
# gingen? Dat is klein, onzichtbaar, en het is de voorwaarde voor elke volgende beslissing over de
# steiger.
#
# WAT IK BEWUST NIET DOE
#
# De steiger korter maken. De regel is nu: nooit gedaan → tegels, openstaande fout → tegels, anders
# typen. Gemeten staan 125 van Stefans 249 zinnen (50%) in tegelstand door een openstaande fout, en
# 103 daarvan op nul goede beurten. De verleiding is die drempel te verlagen, maar tegels bestaan
# sinds v21.4 met een reden (meerkeuze tussen vier hele zinnen was te raden), en een zin die je nog
# niet kent blind laten typen levert frustratie in plaats van productie. Of die steiger korter mag is
# precies wat de meting hierboven moet uitwijzen, en tot die tijd is elke keuze een gok.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.205"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function zinRouteBij(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:100])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de route wordt genoteerd
# =============================================================================================
ROUTE = r'''/* ================= WELKE STAND HIELP (v23.200) =================
   Stefan, 27 aug: "ik heb trouwens idee dat zinnen maken, typen ook heel goed werkt."

   Dat was niet te toetsen. Een zin draagt wel of hij gehaald is en of er een fout open staat, maar
   niet in wélke stand het goede antwoord kwam. Zonder dat veld blijft "typen werkt beter dan
   tegels" een gevoel, en een gevoel is geen grond om de steiger korter te maken.

   Eén regel per zin, overschreven bij elk goed antwoord: welke stand, en wanneer. Over twee weken
   is de vraag te beantwoorden op zijn eigen data: van de zinnen die het laatst via typen goed
   gingen, hoeveel hebben er sindsdien een nieuwe fout opgelopen, tegenover die via tegels?

   Bewust niet per woord maar per zin. De zin is waar de stand aan hangt; een woord kan uit drie
   verschillende oefeningen omhoog komen en dan meet je een mengsel. */
function zinRouteBij(id, modus){
  try {
    if(!id) return;
    S.zinRoute = S.zinRoute || {};
    S.zinRoute[id] = {r: modus === "moeilijk" ? "typ" : "tegel", d: today()};
  } catch(e){}                       // een meter mag de app nooit omver duwen
}
/* Wat er van die reeks te zeggen valt, op één plek zodat het scherm en een latere ronde hetzelfde
   getal lezen. Een zin telt als "weer misgegaan" als er ná de goede beurt een fout is bijgekomen. */
function zinRouteStand(){
  var uit = {typ:{n:0, mis:0}, tegel:{n:0, mis:0}};
  try {
    var r = S.zinRoute || {}, id;
    for(id in r){
      var e = r[id], vak = e && uit[e.r];
      if(!vak) continue;
      vak.n++;
      var f = S.errors["zin:" + id];
      if(f && f.count > 0 && f.dag && f.dag > e.d) vak.mis++;
    }
  } catch(e){}
  return uit;
}

'''

if DOE_APP:
    rep("var sIdx = null;\nfunction sAdaptiefModus(s){", ROUTE + "var sIdx = null;\nfunction sAdaptiefModus(s){")

    # bij een exact goed antwoord
    rep("""    S.done[s.id] = true; gehaald = true; addXP(xpExact);
    foutGoedeBeurt(s.id, "zin");   // v23.94""",
        """    S.done[s.id] = true; gehaald = true; addXP(xpExact);
    foutGoedeBeurt(s.id, "zin");   // v23.94
    zinRouteBij(s.id, modus);      // v23.200: welke stand hielp""")

    # en bij bijna-goed (alleen de accenten): dat is dezelfde productie
    rep("""    S.done[s.id] = true; gehaald = true; addXP(4); compMark("schrijven", s.id); trackPoging(false);
    foutGoedeBeurt(s.id, "zin");   // v23.94""",
        """    S.done[s.id] = true; gehaald = true; addXP(4); compMark("schrijven", s.id); trackPoging(false);
    foutGoedeBeurt(s.id, "zin");   // v23.94
    zinRouteBij(s.id, modus);      // v23.200: een accentfout is nog steeds productie""")

# =============================================================================================
# 2. het schrijven vóór het leesblok
# =============================================================================================
if DOE_APP:
    rep("""    /* v23.140: eerst input, dan pas zelf iets maken. lesFlowOpenProductie() weet sinds v20.5 al hoe
       het een hoofdstuk of een luisterscene opent; die machinerie wordt hier hergebruikt. */
    var inputV = null;
    try { inputV = lesFlowInputKeuze(); } catch(e){ inputV = null; }
    if(inputV){
      lesFlow.stap = "input";
      lesFlow.vaardigheid = inputV;
      lesFlow.vaardigheidRij = [];
      lesFlowOpenProductie();
      return;
    }
    if(lesFlowNaarProduceren()) return;   // v23.150
    lesFlowKlaar();
    return;
  }
  /* v23.140: klaar met lezen of luisteren, door naar het schrijven. Dezelfde afhandeling als
     hieronder, maar met een vaste volgende stap in plaats van een rij vaardigheden. */
  if(lesFlow.stap === "input"){
    if(lesFlow.vaardigheid) S.lesFlowSpel[lesFlow.vaardigheid] = today();
    if(lesFlowNaarProduceren()) return;   // v23.150
    lesFlowKlaar();
    return;
  }
  if(lesFlow.stap === "produceren"){
    // deze vaardigheid is vandaag aan bod geweest, ook als je hem oversloeg: anders krijg je morgen
    // precies hetzelfde blok weer voorgeschoteld
    if(lesFlow.vaardigheid) S.lesFlowSpel[lesFlow.vaardigheid] = today();
    if(lesFlow.vaardigheidRij && lesFlow.vaardigheidRij.length){
      lesFlow.vaardigheid = lesFlow.vaardigheidRij.shift();
      lesFlowOpenProductie();
      return;
    }
    lesFlowKlaar();
    return;
  }""",
        """    /* v23.200: het schrijven ging hier ná het leesblok, en dat is omgedraaid.

       v23.140 zette input bewust eerst ("eerst input, dan pas zelf iets maken"), en die redenering
       klopt binnen één sessie, maar alleen als je ze allebei haalt. Gemeten over Stefans 38 dagen:
       lezen 16 keer geopend, vertalen 4 keer. Hij haalt ze niet allebei, en dan wint het blok dat
       vooraan staat.

       Dit is dus een omkering van een eerdere beslissing en geen reparatie van een fout. De grond
       eronder is niet "productie hoort voor input" maar: drie zinnen typen duurt twee minuten en
       een hoofdstuk lezen een kwartier, en het korte blok hoort niet achter het lange te wachten.
       Zeker niet als het het enige moment van de dag is waarop je het Spaans zelf moet ophalen. */
    if(lesFlowNaarProduceren()) return;   // v23.150
    if(lesFlowNaarInput()) return;        // v23.200
    lesFlowKlaar();
    return;
  }
  if(lesFlow.stap === "produceren"){
    // deze vaardigheid is vandaag aan bod geweest, ook als je hem oversloeg: anders krijg je morgen
    // precies hetzelfde blok weer voorgeschoteld
    if(lesFlow.vaardigheid) S.lesFlowSpel[lesFlow.vaardigheid] = today();
    if(lesFlow.vaardigheidRij && lesFlow.vaardigheidRij.length){
      lesFlow.vaardigheid = lesFlow.vaardigheidRij.shift();
      lesFlowOpenProductie();
      return;
    }
    /* v23.200: en dán het leesblok, in plaats van klaar. Zo blijft de derde draad in de les staan;
       hij staat alleen niet meer vóór het stuk waar je het Spaans zelf moet maken. */
    if(lesFlowNaarInput()) return;
    lesFlowKlaar();
    return;
  }
  if(lesFlow.stap === "input"){
    if(lesFlow.vaardigheid) S.lesFlowSpel[lesFlow.vaardigheid] = today();
    lesFlowKlaar();
    return;
  }""")

    # de nieuwe opener, naast lesFlowNaarProduceren zodat de twee er hetzelfde uitzien
    rep("""// De lengte van elk blok komt uit je tijdbudget: bij 30 minuten zeven zinnen dictado, bij 5 twee.
/* v23.150: één plek die het schrijfblok opent, want er waren er twee die hetzelfde deden en dan
   krijgt er straks eentje het gesprek niet mee. Geeft terug of er iets geopend is. */""",
        """/* v23.200: en één plek die het leesblok opent, om precies dezelfde reden als hieronder. Sinds het
   schrijven vóór het lezen komt wordt deze stap vanaf twee plekken bereikt (na het toetsje als er
   niets te schrijven is, en na het schrijven), en twee kopieën van deze vier regels zouden na één
   ronde uit elkaar lopen. Geeft terug of er iets geopend is. */
function lesFlowNaarInput(){
  var v = null;
  try { v = lesFlowInputKeuze(); } catch(e){ v = null; }
  if(!v) return false;
  lesFlow.stap = "input";
  lesFlow.vaardigheid = v;
  lesFlow.vaardigheidRij = [];
  lesFlowOpenProductie();
  return true;
}

// De lengte van elk blok komt uit je tijdbudget: bij 30 minuten zeven zinnen dictado, bij 5 twee.
/* v23.150: één plek die het schrijfblok opent, want er waren er twee die hetzelfde deden en dan
   krijgt er straks eentje het gesprek niet mee. Geeft terug of er iets geopend is. */""")

# =============================================================================================
# 3. en het dagplan zegt dezelfde volgorde als de flow
# =============================================================================================
# dagPlan() bouwt de blokkenlijst in volgorde en lesFlowVolgendeKern() loopt diezelfde volgorde af.
# Twee plekken die hetzelfde weten; die moeten dus samen mee. Lopen ze uit elkaar, dan zegt de balk
# boven je les iets anders dan wat er komt, en dat is precies het soort stille verschil waar deze week
# vol mee zat. pw-dagvolgorde legt ze voortaan naast elkaar.
INPUT_DUW = """  if(inputV){
    var musDag = inputV === "musica" ? musVanDag() : null;
    blokken.push({stap:"input", draad:ct("begrijpen","input"),
      naam: inputV === "musica" ? ct("Liedje","Song")
          : inputV === "lezen" ? ct("Lezen","Reading") : ct("Luisteren","Listening"),
      wat: inputV === "musica" ? (musDag ? musDag.titel : "M\\u00fasica")
         : inputV === "lezen" ? ct("een stukje uit je boek","a piece from your book")
                              : ct("een gesprek","one conversation"),
      sec: doelMinuten() * 60 * 0.25, vaardigheid: inputV});
  }
"""

if DOE_APP:
    rep("""  /* v23.140: de derde draad. Tussen het toetsje en het schrijven, want het is input en input hoort
     vóór wat je er zelf mee doet. De tijd is een kwart van je dag, hetzelfde budget dat
     vaardigheidTijd() al aan een vaardigheidsblok gaf. */
  var inputV = null;
  try { inputV = lesFlowInputKeuze(); } catch(e){ inputV = null; }
""" + INPUT_DUW,
        """  /* v23.140: de derde draad. v23.200: verhuisd naar ACHTER het schrijven. De oude kop hier zei
     "input hoort vóór wat je er zelf mee doet", en dat klopt binnen één sessie, maar alleen als je
     ze allebei haalt. Gemeten over Stefans 38 dagen: lezen 16 keer geopend, vertalen 4 keer. Het
     korte blok hoort niet achter het lange te wachten. Deze volgorde loopt gelijk met
     lesFlowVolgendeKern(); pw-dagvolgorde bewaakt dat ze niet uit elkaar lopen. De tijd is een
     kwart van je dag, hetzelfde budget dat vaardigheidTijd() al aan een vaardigheidsblok gaf. */
  var inputV = null;
  try { inputV = lesFlowInputKeuze(); } catch(e){ inputV = null; }
""")

    rep("""    blokken.push({stap:"produceren", naam:ct("Schrijven","Writing"), draad:ct("zelf maken","output"),
      wat:SCHRIJF_PER_LES + " " + ct("zinnen","sentences"), sec:SCHRIJF_PER_LES * SCHRIJF_SEC});
  }
""",
        """    blokken.push({stap:"produceren", naam:ct("Schrijven","Writing"), draad:ct("zelf maken","output"),
      wat:SCHRIJF_PER_LES + " " + ct("zinnen","sentences"), sec:SCHRIJF_PER_LES * SCHRIJF_SEC});
  }
""" + INPUT_DUW)

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    APP.write_text(src, encoding="utf-8")
    print("index.html: het schrijven staat voor het leesblok, en de app noteert welke stand hielp")
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
