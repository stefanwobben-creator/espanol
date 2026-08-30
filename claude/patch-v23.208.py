#!/usr/bin/env python3
# v23.208 - de dagrem van v23.170 landde maar op één van de twee doosjes
#
# Stefan, 30 aug: "Grammatica maken en zinnen maken maak ik me meer zorgen over. Dat gaat nog niet
# zo goed heb ik het idee." Op zijn scherm, onder "zwakke plekken":
#
#   Me, te of se              11 fout van 22 beurten     doosje 0/5
#   Lo, la of le               9 fout van 16 beurten     doosje 0/5
#   Woorden die meetellen      4 fout van 28 beurten     doosje 0/5
#
# EERST MIJN EIGEN FOUT
#
# Ik stelde voor om de reset te verzachten tot één doosje terug. Dat is precies het ontwerp dat op
# 22 augustus is voorgesteld, aangevallen en gesneuveld (claude/Leerkaart - de doos die niet omhoog
# kon). De redenen staan er nog steeds: SuperMemo noemt de één-stap-variant een onjuiste mutatie van
# Leitner, Anki reset volledig na een lapse, en lesFlowGramId() vuurt de volledige microles af op
# "doos 0 met twee of meer fouten", dus onderwerpen van doos 0 weghouden sloopt de remediatie stil.
# pw-doos.js bewaakt die reset sindsdien met opzet. Ik had dat moeten opzoeken voordat ik het opnieuw
# voorstelde, en de reset blijft dus staan.
#
# WAT ER WEL AAN DE HAND IS, EN HET IS HETZELFDE DEFECT ALS IN v23.170
#
# v23.170 repareerde de dagrem in gramBij(): het eerste antwoord van de dag bepaalt de doos, en wat
# je daarna die dag nog doet verandert hem niet meer. Zonder die rem hing je einddoos af van de
# VOLGORDE van je antwoorden binnen een dag, en dat noemde die ronde onverdedigbaar.
#
# corrSrsBij() heeft die rem nooit gekregen. Daar schrijft elk antwoord naar de doos, dus het
# laatste antwoord van je sessie wint. Nagemeten over 200 rondes van El Corrector (8 zinnen per
# ronde, alle lessen open):
#
#   rondes waarin minstens één regel meer dan eens langskomt : 188 van 200  (94%)
#   unieke regels per ronde                                  : 5,9 van 8
#   beurten op de meest voorkomende regel, per ronde          : 2,3 gemiddeld
#
# Een echte ronde uit die meting:
#
#   reflexivo acento reflexivo predicado lidwoord reflexivo porpara porpara
#
# Drie keer reflexivo, dat is "Me, te of se". Ga je goed, goed, fout, dan eindig je op doos 0. Ga je
# fout, goed, goed, dan eindig je op doos 1. Zelfde ronde, zelfde kennis, andere doos, puur op
# volgorde. En omdat corrRegelVolgorde() de regels die due zijn vooraan zet, krijgen juist de regels
# die je het meest oefent de meeste beurten per ronde, dus de meeste kans om op een fout te eindigen.
# Dat is een ratel: hoe meer je oefent, hoe vaster je op nul staat. Precies wat Stefan ziet bij de
# twee regels die hij het vaakst tegenkomt.
#
# WAT DEZE RONDE DOET
#
# corrSrsBij() krijgt dezelfde drie regels die gramBij() sinds v23.170 heeft:
#
#   1. het eerste antwoord van vandaag op die regel bepaalt de doos;
#   2. daarna verandert de doos die dag niet meer, in geen van beide richtingen;
#   3. gaat het later op de dag alsnog mis, dan blijft de doos staan maar komt de vervaldatum naar
#      overmorgen, zodat hij morgen of overmorgen opnieuw wordt beoordeeld door een eerste antwoord.
#
# De reset blijft volledig. De tellers goed en fout blijven elk antwoord tellen; die zijn de
# geschiedenis en niet het oordeel, net als bij de concepten.
#
# WAT DEZE RONDE NIET DOET
#
# De diagnose van de leerkaart van 22 augustus staat nog: een regel als "el of la" is geen concept
# met één geheugenspoor maar honderden zelfstandige naamwoorden, en één doos over zo'n heterogene
# verzameling convergeert nooit. Het antwoord daarop is het item splitsen, niet het herplannen. Dat
# is een eigen ronde en die verandert deze niet.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.208"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "v23.208: dezelfde dagrem" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:120])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    rep("""/* het Leitner-doosje per regel. Fout betekent niet "morgen weer", dat voelt als
   straf; het betekent overmorgen, en dan opnieuw opbouwen. */
function corrSrsBij(id, goed){
  S.corr = S.corr || {};
  var st = S.corr[id] || {box:0, due:"", goed:0, fout:0};
  if(goed){
    st.goed++;
    st.box = Math.min((st.box || 0) + 1, CORR_INTERVALS.length - 1);
    st.due = addDays(today(), CORR_INTERVALS[st.box]);
  } else {
    st.fout++;
    st.box = 0;
    st.due = addDays(today(), 2);
  }
  S.corr[id] = st;""",
        """/* het Leitner-doosje per regel. Fout betekent niet "morgen weer", dat voelt als
   straf; het betekent overmorgen, en dan opnieuw opbouwen.

   v23.208: dezelfde dagrem als gramBij() sinds v23.170. Die ronde repareerde de rem bij de
   concepten en liet hem hier staan, en dat is dezelfde bug op de tweede plek.

   Zonder rem schrijft elk antwoord naar de doos, dus het laatste antwoord van je sessie wint.
   Nagemeten over 200 rondes van El Corrector, acht zinnen per ronde: in 188 ervan (94 procent) komt
   minstens één regel meer dan eens langs, gemiddeld 5,9 unieke regels op acht zinnen, en de meest
   voorkomende regel krijgt er gemiddeld 2,3. Een echte ronde uit die meting:

       reflexivo acento reflexivo predicado lidwoord reflexivo porpara porpara

   Drie keer reflexivo, oftewel "Me, te of se". Goed, goed, fout eindigt op doos 0; fout, goed, goed
   eindigt op doos 1. Zelfde ronde, zelfde kennis, andere doos, alleen op volgorde. En omdat
   corrRegelVolgorde() de regels die due zijn vooraan zet, krijgen juist de regels die je het meest
   oefent de meeste beurten per ronde en dus de grootste kans om op een fout te eindigen. Hoe meer je
   oefent, hoe vaster je op nul staat.

   De reset zelf blijft volledig, en met opzet: één stap terug is op 22 augustus voorgesteld en
   afgewezen (SuperMemo noemt het een onjuiste mutatie van Leitner, Anki reset volledig, en
   lesFlowGramId() vuurt de microles af op doos 0). Zie claude/Leerkaart - de doos die niet omhoog
   kon, en pw-doos.js, die die reset bewaakt.

   De tellers goed en fout tellen elk antwoord; die zijn de geschiedenis en niet het oordeel. */
function corrSrsBij(id, goed){
  S.corr = S.corr || {};
  var st = S.corr[id] || {box:0, due:"", goed:0, fout:0};
  if(goed) st.goed++; else st.fout++;
  if(st.bd !== today()){
    st.bd = today();
    if(goed){
      st.box = Math.min((st.box || 0) + 1, CORR_INTERVALS.length - 1);
      st.due = addDays(today(), CORR_INTERVALS[st.box]);
    } else {
      st.box = 0;
      st.due = addDays(today(), 2);
    }
  } else if(!goed){
    /* Later op de dag alsnog mis. De doos blijft staan (het oordeel van vandaag is al geveld), maar
       je ziet de regel overmorgen terug in plaats van pas over dertig dagen. Zonder deze regel zou
       een regel die je 's ochtends goed had en 's middags drie keer fout gewoon wegzakken. */
    st.due = addDays(today(), 2);
  }
  S.corr[id] = st;""")

    rep("""/* hoeveel regels staan er stevig? Dat is het enige getal dat dit spel over
   grammatica kan claimen, en het gaat alleen omhoog als je ze blijft halen. */""",
        """/* hoeveel regels staan er stevig? Dat is het enige getal dat dit spel over
   grammatica kan claimen, en het gaat alleen omhoog als je ze blijft halen.
   v23.208: "blijven halen" is sindsdien het eerste antwoord van de dag, niet het laatste van je
   sessie. Zie de kop van corrSrsBij(). */""")

if DOE_APP:
    assert src.count("v23.208: dezelfde dagrem") == 1
    # de rem hoort binnen corrSrsBij te staan, niet ergens anders in het bestand
    _i = src.index("function corrSrsBij(")
    _j = src.index("\nfunction ", _i + 10)
    assert "st.bd !== today()" in src[_i:_j], "de dagrem staat niet in corrSrsBij"
    assert src.count("st.box = 0;") >= 2, "de reset hoort er nog te zijn"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de dagrem staat nu ook op de regels van El Corrector")
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
