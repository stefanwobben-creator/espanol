#!/usr/bin/env python3
# v23.226 - één suggestie, en hij zegt waarom hij er staat
#
# Stefan, 1 sep, bij een schermafbeelding van de kaart "Even spelen": "deze suggesties moeten we
# even kijken of je er eentje toont of iets wat zwakke punt is waar ik nog wat meer kan oefenen."
#
# WAT ER STOND
#
# dagSpelKeuze(3) koos drie spellen met dayHash("spel"): een rotatie op de datum. Er zat geen enkel
# verband met wat jij die week fout deed, en de kaart zei ook niet waarom die drie er stonden. Drie
# willekeurige knoppen naast elkaar zijn drie keer dezelfde vraag ("wil je dit?") en nul keer een
# antwoord ("hier valt voor jou wat te halen").
#
# WAT ER NU STAAT
#
# Eén regel, gekozen uit je fouten van de afgelopen zeven dagen, met de reden erbij:
#
#     Deze week ging het 12 keer mis op werkwoordsvormen.
#     [ Conjugador ]
#
# ZEVEN DAGEN, EN NIET ALLES
#
# Dat is de belangrijkste keuze in deze ronde. S.errors bewaart alles, en over de hele historie
# wint "woord" altijd: Stefans logboek zegt woord 334, zin 130, quiz 81, gramwiz 50, conj 40,
# corrector 22, escucha 4. Dat is geen zwakte maar blootstelling; hij doet nu eenmaal het meest met
# woorden. Een teller waarin het vaakst geoefende onderdeel per definitie wint, meet de oefening en
# niet de leerling.
#
# Zeven dagen is kort genoeg om te bewegen en lang genoeg om niet op één slechte avond te slaan. De
# regels dragen sinds v22.0 een `dag`, dus dit is te berekenen zonder iets nieuws op te slaan.
#
# WAT DE SOORTEN WORDEN
#
#   woord, quiz          een woordspel (welk, dat rouleert nog steeds op de dag)
#   zin, corrector       El Corrector: hele zinnen nakijken
#   conj, verbo          Rompecabezas: vormen bouwen
#   escucha              Escuchar: luisteren
#
# EN DAARMEE KOMEN ER OEFENINGEN OP EEN KAART DIE "EVEN SPELEN" HEETTE
#
# In v23.65 is precies dat een fout genoemd: onder Oefenen telt het mee voor je niveau, onder Spelen
# niet, en de dagkaart bood drie oefeningen aan onder de kop "Even spelen". Die regel blijft staan;
# de kop volgt nu gewoon de inhoud. Wijst de kaart een zwak punt aan, dan heet hij "Even oefenen" en
# staat er waarom. Valt er niets te wijzen, dan is het weer een spel onder "Even spelen".
#
# gramwiz en concept staan er NIET bij, en dat is bewust. Grammatica heeft sinds v23.225 zijn eigen
# vervolg (de drill van vijf, direct na een misser) en lesFlowWinst() zet een fout concept al
# bovenaan het voorstel na je les. Nog een derde plek die hetzelfde aanwijst maakt het niet
# duidelijker; het maakt het drukker.
#
# EN ALS ER NIETS TE WIJZEN IS
#
# Dan staat er gewoon één spel uit de oude rotatie, zonder reden erbij. Geen fouten deze week is
# geen zwakte, en een verzonnen reden ("je hebt hier vast moeite mee") is erger dan geen reden. Dat
# is dezelfde regel als bij de blokken op het dagscherm: nul is geen bericht.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.226"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function dagZwakPunt(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # =========================================================================================
    # 1. het zwakke punt
    # =========================================================================================
    rep("""function dagSpeelHtml(){""",
"""/* ================= HET ZWAKKE PUNT VAN DEZE WEEK (v23.226) =================

   Stefan: "kijken of je er eentje toont of iets wat zwakke punt is waar ik nog wat meer kan
   oefenen."

   ZEVEN DAGEN, EN NIET ALLES. S.errors bewaart je hele historie, en daarin wint "woord" altijd:
   334 tegen 130 zinnen, 40 conj, 22 corrector. Dat is blootstelling en geen zwakte; hij doet nu
   eenmaal het meest met woorden. Een teller waarin het vaakst geoefende onderdeel per definitie
   wint, meet de oefening en niet de leerling. De regels dragen sinds v22.0 een `dag`, dus zeven
   dagen terugkijken kost niets extra's.

   GRAMMATICA STAAT ER BEWUST NIET BIJ. Die heeft sinds v23.225 zijn eigen vervolg (de drill van
   vijf, direct na de misser) en lesFlowWinst() zet een fout concept al bovenaan het voorstel na je
   les. Een derde plek die hetzelfde aanwijst maakt het drukker, niet duidelijker. */
var ZWAK_DAGEN = 7;
var ZWAK_SOORT = [
  {soorten:["conj", "verbo"],     spel:"conj",
   nl:"werkwoordsvormen",         en:"verb forms"},
  {soorten:["zin", "corrector"],  spel:"corr",
   nl:"hele zinnen",              en:"whole sentences"},
  {soorten:["escucha"],           spel:"audi",
   nl:"luisteren",                en:"listening"},
  {soorten:["woord", "quiz"],     spel:"",     // leeg: dan kiest de dagrotatie een woordspel
   nl:"losse woorden",            en:"single words"}
];
/* Een rij voor de kaart, uit spelInfo() of uit oefenItems(). De Conjugador, El Corrector en
   Escuchar hebben geen speeltegel: ze staan onder Oefenen, en dat is precies waarom ze hier alleen
   verschijnen als de kaart "Even oefenen" heet. */
function zwakRij(v){
  var g = null;
  try { g = spelInfoVan(v); } catch(e){ g = null; }
  if(g) return g;
  var o = null;
  try {
    oefenItems().forEach(function(x){ if(x.id === v) o = x; });
  } catch(e2){ o = null; }
  return o ? {v:o.id, e:o.ico, t:o.t, s:o.s} : null;
}
function dagZwakPunt(){
  var grens = addDays(today(), -ZWAK_DAGEN), tel = {};
  var e, k;
  for(k in (S.errors || {})){
    e = S.errors[k];
    if(!e || !e.dag || e.dag < grens) continue;
    tel[e.type] = (tel[e.type] || 0) + (e.count || 1);
  }
  var beste = null;
  ZWAK_SOORT.forEach(function(z){
    var n = 0;
    z.soorten.forEach(function(s){ n += tel[s] || 0; });
    if(!n) return;
    /* Alleen als het spel vandaag ook echt iets kan tonen. Een knop die uitkomt op "leer eerst
       wat meer woordjes" leert je dat de knoppen hier niet betrouwbaar zijn (v19.92). */
    var v = z.spel;
    if(!v){
      var w = dagSpelKeuze(1)[0];
      if(!w) return;
      v = w.v;
    } else {
      try { if(!speelKlaar(v)) return; } catch(err){ return; }
    }
    if(!beste || n > beste.n) beste = {n:n, v:v, nl:z.nl, en:z.en};
  });
  return beste;
}

function dagSpeelHtml(){""")

    # =========================================================================================
    # 2. de kaart
    # =========================================================================================
    rep("""  /* v23.147: hier stond Aventura vast bovenaan en kwamen er twee wisselende bij. Nu drie
     wisselende, want die vaste plek hoorde bij een spel dat er niet meer is. */
  var keus = dagSpelKeuze(3);
  var knoppen = "";
  keus.forEach(function(k){ knoppen += dagSpeelRij(k); });""",
"""  /* v23.147: hier stond Aventura vast bovenaan en kwamen er twee wisselende bij. Nu drie
     wisselende, want die vaste plek hoorde bij een spel dat er niet meer is.
     v23.226: en nu één, gekozen uit je fouten van de afgelopen week. Drie willekeurige knoppen
     naast elkaar stellen drie keer dezelfde vraag ("wil je dit?") en geven nul keer een antwoord
     ("hier valt voor jou wat te halen"). */
  var zwak = null;
  try { zwak = dagZwakPunt(); } catch(e){ zwak = null; }
  var keus = zwak ? [zwakRij(zwak.v)].filter(Boolean) : dagSpelKeuze(1);
  if(zwak && !keus.length){ zwak = null; keus = dagSpelKeuze(1); }
  var knoppen = "";
  keus.forEach(function(k){ knoppen += dagSpeelRij(k); });
  /* De reden staat vóór de knop en niet erna: hij is het antwoord op "waarom deze", en die vraag
     stel je terwijl je ernaar kijkt. Geen reden als er niets te wijzen valt; een verzonnen reden
     is erger dan geen (nul is geen bericht, zie dagRelevantie). */
  var reden = zwak
    ? "<p class='muted' style='margin:0 0 8px; font-size:.88rem'>"+
        ct("Deze week ging het "+zwak.n+" keer mis op "+zwak.nl+".",
           "This week you got "+zwak.n+" wrong on "+zwak.en+".")+"</p>"
    : "";""")
    rep("""  return "<div class='card' id='speelKaart'><span class='kicker'>"+ct("Even spelen","Play something")+"</span>"+
    "<div class='speellijst'>"+knoppen+"</div>"+""",
"""  return "<div class='card' id='speelKaart'><span class='kicker'>"+
      (zwak ? ct("Even oefenen","A bit of practice") : ct("Even spelen","Play something"))+"</span>"+
    reden+
    "<div class='speellijst'>"+knoppen+"</div>"+""")
    # de zin over dichte spellen hoort bij een kaart die er drie toonde
    rep("""    (dicht > 0
      ? "<p class='muted' style='margin:8px 0 0; font-size:.85rem'>"+
          ct("Nog "+dicht+" "+(dicht === 1 ? "spel komt" : "spellen komen")+" erbij als je meer woorden kent.",
             "Another "+dicht+" "+(dicht === 1 ? "game joins" : "games join")+" in once you know more words.")+"</p>"
      : "")+""",
"""    (dicht > 0 && !zwak
      ? "<p class='muted' style='margin:8px 0 0; font-size:.85rem'>"+
          ct("Nog "+dicht+" "+(dicht === 1 ? "spel komt" : "spellen komen")+" erbij als je meer woorden kent.",
             "Another "+dicht+" "+(dicht === 1 ? "game joins" : "games join")+" in once you know more words.")+"</p>"
      : "")+""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    for nodig in ["function dagZwakPunt(", "function zwakRij(", "var ZWAK_DAGEN = 7",
                  "var ZWAK_SOORT = [", "dagSpelKeuze(1)", "zwakRij(zwak.v)"]:
        assert nodig in src, "ontbreekt: " + nodig
    assert "dagSpelKeuze(3)" not in src, "de kaart vraagt nog om drie spellen"
    # grammatica hoort er NIET in te staan, anders wijzen drie plekken hetzelfde aan
    blok = src[src.index("var ZWAK_SOORT = ["):src.index("function dagZwakPunt(")]
    for niet in ["gramwiz", "concept"]:
        assert '"' + niet + '"' not in blok, "grammatica staat in ZWAK_SOORT: " + niet
    # en de terugval moet er zijn: geen fouten is geen zwakte
    assert "zwak ? [zwakRij(zwak.v)].filter(Boolean) : dagSpelKeuze(1)" in src, \
        "er is geen terugval naar de dagrotatie"
    APP.write_text(src, encoding="utf-8")
    print("index.html: één gerichte suggestie in plaats van drie willekeurige")
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
