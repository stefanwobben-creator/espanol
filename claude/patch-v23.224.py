#!/usr/bin/env python3
# v23.224 - de cijfers gaan van het dagscherm af, de peiling blijft
#
# Stefan, 1 sep, met een schermafbeelding van de kaart "Waar je staat" erbij: "deze functionaliteit
# mag wel uit het scherm."
#
# WAT ERUIT GAAT
#
#   de zin        "A1 en A2 is bijna rond. Je houdt er 643 actief bij."   dagBasisZinHtml()
#   de vouw       "Jouw lijn", veertien staafjes                          dagLijnHtml()
#   de knop       "Alle cijfers ->"                                       btnLijnMeer
#
# Dit is dezelfde beweging als v23.222, en om dezelfde reden: het staat op het scherm waar je je dag
# begint, het vraagt aandacht, en het verandert niets aan wat je vandaag doet. De staafjes stonden
# sinds v23.2 al onder een vouw en de balk is in v23.64 al vervangen door één zin. Twee keer
# ingekrompen omdat het niet weg mocht; nu mag het wel weg.
#
# Er gaat niets verloren: de hele kaart staat op Voortgang, mét legenda en met de twee tegels
# eronder uitgesplitst. Dat scherm zit in de balk.
#
# WAT ER BLIJFT, EN WAAROM DAT GEEN HALVE VERWIJDERING IS
#
# In diezelfde kaart zat de PEILING. Die is geen statistiek maar een handeling: twintig woorden,
# ongeveer een minuut, en daarna weet de app beter wat je al kent. Hij komt hoogstens eens per paar
# weken langs (peilAanbod() bepaalt wanneer) en hij is precies het soort ding dat je één keer doet
# als het langskomt en nooit als je ernaar moet zoeken.
#
# Hij stáát ook op Voortgang, in dagBasisRegelHtml(). Maar een aanbod dat alleen op een scherm staat
# dat je zelden opzoekt, wordt nooit aangenomen, en de schatting die eruit komt is juist wat de hele
# leesronde nodig heeft. Daarom krijgt hij zijn eigen kaartje op Vandaag, en alleen op de dagen dat
# er iets aan te bieden is.
#
# Dat is een aanname en die staat hier expliciet: Stefan wees op de cijfers, niet op de peiling.
# Blijkt de kaart alsnog te vaak in beeld te komen, dan is het één regel om hem ook weg te halen.
#
# DE OPRUIMING DIE ERACHTER ZAT
#
# dagRelevantie() rekende twee dingen uit die alleen deze kaart gebruikte: `basis` (loopt over alle
# WORDS) en `lijn` (loopt over veertien dagen). Beide velden worden nu nergens meer gelezen, dus
# beide lussen zijn weg. Dat scheelt twee volledige doorlopen bij elke keer dat het dagscherm
# tekent.
#
# In dezelfde functie stond `open`: een variabele die met een lus over alle WORDS gevuld werd en
# vervolgens nergens werd teruggegeven. Die stond er al langer en gaat nu mee.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.224"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function dagLijnHtml(){" in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

verwijderd = {}

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)

def _blok(start, open_t, sluit_t):
    d = 0; i = start; inStr = None; esc = False
    while i < len(src):
        c = src[i]
        if inStr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == inStr: inStr = None
            i += 1; continue
        if c in "\"'":
            inStr = c; i += 1; continue
        if c == "/" and src[i+1:i+2] == "/":
            i = src.index("\n", i); continue
        if c == "/" and src[i+1:i+2] == "*":
            i = src.index("*/", i) + 2; continue
        if c == open_t: d += 1
        elif c == sluit_t:
            d -= 1
            if d == 0: return i
        i += 1
    raise AssertionError("ongebalanceerd blok vanaf %d" % start)

def _kopErboven(a):
    """Commentaar dat direct boven een definitie staat hoort erbij. Zie v23.222 voor waarom deze
       versie van de */ naar de bijbehorende /* springt in plaats van regel voor regel te klimmen."""
    while True:
        eind = src.rfind("\n", 0, a)
        if eind <= 0: return a
        regelStart = src.rfind("\n", 0, eind) + 1
        regel = src[regelStart:eind].strip()
        if regel == "": return a
        if regel.startswith("//"):
            a = regelStart; continue
        if regel.endswith("*/"):
            sluit = src.rindex("*/", regelStart, eind + 1)
            open_i = src.rfind("/*", 0, sluit)
            assert open_i >= 0, "een */ zonder /* boven positie %d" % a
            a = src.rfind("\n", 0, open_i) + 1
            continue
        return a

def _balans(s):
    b = max(re.findall(r"<script>(.*?)</script>", s, re.S), key=len)
    return b.count("/*") - b.count("*/")

balansVoor = _balans(src)

def knipFunctie(naam):
    global src
    m = re.search(r"^function " + re.escape(naam) + r"\(", src, re.M)
    assert m, "functie niet gevonden: " + naam
    a = _kopErboven(m.start())
    eind = _blok(m.start(), "{", "}")
    while src[eind:eind+1] in ("}", ";"): eind += 1
    if src[eind:eind+1] == "\n": eind += 1
    verwijderd[naam] = src[a:eind].count("\n")
    src = src[:a] + src[eind:]

if DOE_APP:
    # =========================================================================================
    # 1. de peiling krijgt haar eigen kaartje, vóór de rest wordt weggehaald
    #
    # Bewust een aparte functie en geen restant van dagLijnHtml(): die kaart ging over "waar sta
    # ik" en deze gaat over één handeling. Een kaart die overblijft na een verwijdering draagt de
    # naam en de vorm van iets anders, en dat is precies hoe een scherm dichtslibt.
    # =========================================================================================
    rep("""function dagLijnHtml(){""",
"""/* v23.224: het enige dat van de kaart "Waar je staat" op Vandaag overblijft.

   De peiling is geen statistiek maar een handeling: twintig woorden, ongeveer een minuut, en
   daarna weet de app beter wat je al kent. peilAanbod() bepaalt wanneer hij langskomt, en dat is
   hoogstens eens per paar weken. Op de dagen dat er niets aan te bieden is staat hier niets.

   Waarom hij niet met de cijfers is meegegaan: hij staat ook op Voortgang (in dagBasisRegelHtml),
   maar een aanbod dat alleen op een scherm staat dat je zelden opzoekt wordt nooit aangenomen. En
   de schatting die eruit komt is precies wat de leesplank nodig heeft om te kunnen sturen. */
function dagPeilKaartHtml(){
  var aanbod = null;
  try { aanbod = peilAanbod(); } catch(e){ aanbod = null; }
  if(!aanbod) return "";
  return "<div class='card' id='peilKaart'><span class='kicker'>"+
    ct("Even peilen","A quick check")+"</span>"+
    "<p class='muted' style='margin:6px 0 10px; font-size:.9rem'>"+
      ct("Hiermee schat de app beter in wat je al kent, en dat bepaalt wat hij je voorlegt.",
         "This helps the app judge what you already know, and that decides what it puts in front of you.")+
    "</p>"+dagPeilKnopHtml(aanbod)+"</div>";
}

function dagLijnHtml(){""")

    # =========================================================================================
    # 2. het dagscherm
    # =========================================================================================
    rep("    html += dagLijnHtml();\n", "    html += dagPeilKaartHtml();\n")
    rep("""  var bl = document.getElementById("btnLijnMeer");
  // v23.32: naar het voortgangsscherm, niet meer naar je profiel
  if(bl) bl.onclick = function(){ show("voortgang"); };
""", "")

    # =========================================================================================
    # 3. de twee functies en hun stijl
    # =========================================================================================
    knipFunctie("dagLijnHtml")
    knipFunctie("dagBasisZinHtml")
    knipFunctie("dagBasisStand")

    a = src.index("  .lijnstrook{")
    b = src.index("\n", src.index("  .lijnstaaf[data-vandaag]")) + 1
    verwijderd["css"] = src[a:b].count("\n")
    src = src[:a] + src[b:]

    # =========================================================================================
    # 4. dagRelevantie: twee velden weg, en twee lussen die alleen voor die velden liepen
    # =========================================================================================
    rep("""function dagRelevantie(){
  var t = today(), tel = voortgangTellers(), niv = balkNiveau();
  var onderweg = Math.max((tel.dek && tel.dek[niv]) || 0, (tel.dekw && tel.dekw[niv]) || 0);
  var open = 0, dagenMetXp = 0, i, d, st;
  for(i = 0; i < WORDS.length; i++){ st = S.srs[WORDS[i].id]; if(st && st.due <= t) open++; }
  for(i = 0; i < 14; i++){ d = addDays(t, -i); if(((S.xp && S.xp[d]) || 0) > 0) dagenMetXp++; }
  return {
    // een kaart die meldt dat er niets te melden is, is zelf de melding
    nieuws: dagNieuwsRegels().length > 0,
    // je basis verschijnt zodra er iets onderweg is. Doos 3 kost ongeveer een week, of staat er
    // meteen als je je niveau geclaimd hebt. Daarvoor kan de balk niets anders tonen dan 0%, en
    // een balk die dagenlang stil staat leert je vooral dat de balk niets zegt (zie v19.87).
    // v20.3: en ook zodra er een schatting ligt of er een peiling aan te bieden is, want dan
    // heeft de balk iets te zeggen wat je nergens anders ziet.
    basis: onderweg > 0 || !!peilSchattingStil(niv) || !!peilAanbodStil(),
    // een lijn heb je pas vanaf twee punten. Een staafje en dertien gaten is geen lijn.
    lijn: dagenMetXp >= 2,
    // deze drie stonden er ook als ze nul waren, en nul is geen bericht
    chipNieuw: newToday() > 0,""",
"""function dagRelevantie(){
  var t = today(), niv = balkNiveau();
  /* v23.224: hier stonden ook `basis` en `lijn`, de twee vragen van de kaart "Waar je staat". Die
     kaart is van dit scherm af, dus leest niemand ze meer. Met hen mee gingen twee lussen: een over
     alle WORDS en een over veertien dagen, allebei bij elke keer dat het dagscherm tekent.

     En `open`: een teller die met een volledige lus over WORDS werd gevuld en vervolgens nergens
     werd teruggegeven. Die stond er al langer dood bij. */
  return {
    // een kaart die meldt dat er niets te melden is, is zelf de melding
    nieuws: dagNieuwsRegels().length > 0,
    // deze twee stonden er ook als ze nul waren, en nul is geen bericht
    chipNieuw: newToday() > 0,""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    zonderCommentaar = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    zonderCommentaar = re.sub(r"^\s*//.*$", "", zonderCommentaar, flags=re.M)
    resten = {}
    for naam in ["dagLijnHtml", "dagBasisZinHtml", "dagBasisStand", "btnLijnMeer", "lijnKaart",
                 "lijnstrook", "lijnstaaf"]:
        n = len(re.findall(r"\b" + re.escape(naam) + r"\b", zonderCommentaar))
        if n: resten[naam] = n
    assert not resten, "er wijst nog iets naar de cijferkaart: %r" % resten
    for veld in ["basis:", "lijn:"]:
        assert veld not in zonderCommentaar.split("function dagRelevantie(){")[1].split("\n}")[0], \
            "dagRelevantie geeft %s nog terug" % veld

    # en wat er MOET blijven staan
    for blijft in ["function dagPeilKaartHtml(", "function dagPeilKnopHtml(", "function peilAanbod(",
                   'id="btnPeilStart"' if 'id="btnPeilStart"' in src else "btnPeilStart",
                   "function dagBasisRegelHtml(", "function voortgangCijfers("]:
        assert blijft in src, "dit had moeten blijven staan: " + blijft
    assert "html += dagPeilKaartHtml();" in src, "het dagscherm tekent de peilkaart niet"
    # de peiling moet op BEIDE plekken aangeboden blijven worden
    assert len(re.findall(r"dagPeilKnopHtml\(", zonderCommentaar)) == 3, \
        "dagPeilKnopHtml hoort één definitie en twee aanroepen te hebben (Vandaag en Voortgang)"

    na = _balans(src)
    assert na == balansVoor, \
        "commentaar loopt niet meer rond: /* min */ was %d en is nu %d" % (balansVoor, na)

    n = sum(verwijderd.values())
    APP.write_text(src, encoding="utf-8")
    print("index.html: de cijferkaart van Vandaag af, %d regels weg" % n)
    for k in sorted(verwijderd, key=lambda x: -verwijderd[x]):
        print("   %-22s %4d" % (k, verwijderd[k]))
else:
    print("index.html: de cijferkaart stond er al niet meer")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
