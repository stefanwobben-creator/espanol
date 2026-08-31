#!/usr/bin/env python3
# v23.222 - het sociale gaat van het dagscherm af, het meten blijft
#
# Stefan, 31 aug, bij de vraag hoe ver dit eruit moest: "wat is het beste voor het leerproces? de
# muur was er om het sociale te bevorderen maar dat wordt niet echt gebruikt, dus ik denk nu dat we
# dat helemaal opnieuw moeten ontwerpen en dan kunnen we het nu beter eerst weghalen (maar wel
# blijven meten op de achtergrond)."
#
# WAT ERUIT GAAT
#
#   de vraag van vandaag   DAGVRAGEN + dagZin* (v23.156)
#   de muur                muur* (v22.7)
#
# Allebei alleen op het dagscherm. Wat blijft staan: groepen, uitnodigen, krabbels op het
# familieblok, en de sync die de hele state naar de server schrijft.
#
# WAAROM DE VRAAG VAN VANDAAG NIET APART TE REDDEN WAS
#
# Ze zijn technisch één ding. dagZinHtml() staat in muurHtml(), dagZinAnderen() leest muurData, en
# dagZinWire() wordt aangeroepen vanuit muurTeken(). Er is geen versie van dit scherm waarin de
# vraag blijft en de muur gaat: de vraag toont wat je groep schreef, en dat komt uit dezelfde
# ophaal. Het was ook één antwoord van Stefan: het sociale wordt niet gebruikt.
#
# EN DAT IS EEN MEETBAAR ANTWOORD, GEEN GEVOEL
#
# De vraag van vandaag kostte de duurste regel van v23.167: hij staat achter "les af", dus schrijft
# iemand in je groep iets terwijl jij je les niet doet, dan zie je het pas de volgende dag. Die prijs
# is genomen met een expliciete meting erbij ("meting als dit fout is: schrijft hij minder vaak een
# zin dan hiervoor"). De uitkomst is: hij schrijft er geen. Een kaart die elke dag bovenaan het
# dagscherm staat en niets oplevert, is geen neutrale kaart; hij staat vóór het werk.
#
# WAT "BLIJVEN METEN" HIER BETEKENT
#
# Niets extra's, en dat is precies waarom het kan. syncUp() stuurt de HELE state naar /api/sync:
# S.mijlpalen, S.oogst per dag, S.groepen, alles. De muur was daar alleen een LEZER van, via
# /api/groep/:gcode. Het scherm weghalen raakt de schrijfkant dus niet. Wie dit over drie maanden
# opnieuw ontwerpt vindt de gebeurtenissen van al die tussenliggende dagen gewoon op de server.
#
# De server blijft ook helemaal ongemoeid: /api/groep en /api/krabbel blijven bestaan. Een endpoint
# dat niemand aanroept kost niets; een endpoint dat je weghaalt en later terug moet bouwen kost een
# migratie.
#
# WAT ER BLIJFT STAAN EN WAAROM DAT GEEN HALF WERK IS
#
#   KRABBELS, krabbelVind(), krabbelIkBen()   het familieblok toont binnengekomen krabbels
#                                             (dagKrabbels() leest famCache, niet muurData)
#   samenKaartNu() / uitnodigKaart()          uitnodigen staat los van de muur
#   renderGroepen()                           de groepenpagina onder Profiel
#   S.dagzin in opgeslagen profielen          wordt niet meer gelezen; weghalen zou een migratie
#                                             zijn en een migratie die alleen opruimt is risico
#                                             zonder opbrengst (zelfde afweging als v23.218)
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.222"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "var DAGVRAGEN = [" in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

verwijderd = {}

def _balans(s):
    b = max(re.findall(r"<script>(.*?)</script>", s, re.S), key=len)
    return b.count("/*") - b.count("*/")

balansVoor = _balans(src)

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
    """Commentaar dat direct boven een definitie staat hoort erbij. Commentaar dat een functie
       beschrijft die er niet meer is, stuurt de volgende lezer het bos in.

       DE VERSIE IN v23.218 KON DIT NIET, EN DAT LEVERDE GEEN FOUTMELDING OP.

       Die klom regel voor regel omhoog en accepteerde alleen regels die met /*, * of // beginnen
       of op */ eindigen. In dit bestand zijn blokcommentaren opgemaakt als lopende tekst: de
       eerste regel begint met /*, de laatste eindigt op */, en alles ertussen begint met een
       gewoon woord. De klim stopte dus MIDDEN in het blok en knipte de onderste helft weg,
       inclusief de */. Wat overbleef was een niet-afgesloten /* dat de rest van het bestand
       opslokte tot de volgende */ - zichtbaar als een accolade die niet klopte, honderd regels
       verderop, in een functie waar niets aan veranderd was.

       Deze versie zoekt bij een regel die op */ eindigt de bijbehorende /* op en springt daar in
       één keer naartoe. Een lege regel scheidt: wat daarboven staat hoort bij iets anders."""
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

def knipVarArray(naam):
    global src
    m = re.search(r"^var " + re.escape(naam) + r" = \[", src, re.M)
    assert m, "array niet gevonden: " + naam
    a = _kopErboven(m.start())
    eind = _blok(m.end() - 1, "[", "]")
    while src[eind:eind+1] in ("]", ";"): eind += 1
    if src[eind:eind+1] == "\n": eind += 1
    verwijderd[naam] = src[a:eind].count("\n")
    src = src[:a] + src[eind:]

def knipRegel(fragment, n=1):
    global src
    treffers = [r for r in src.split("\n") if fragment in r]
    assert len(treffers) == n, "regel %d keer (verwacht %d): %r" % (len(treffers), n, fragment)
    for r in treffers:
        src = src.replace(r + "\n", "", 1)
        verwijderd.setdefault("losse regels", 0)
        verwijderd["losse regels"] += 1

if DOE_APP:
    # =========================================================================================
    # 1. de stijl
    # =========================================================================================
    a = src.index("  /* de muur (v22.7) */")
    b = src.index("  /* voortgang (v23.0)", a)
    verwijderd["css"] = src[a:b].count("\n")
    src = src[:a] + src[b:]

    # =========================================================================================
    # 2. het voorstel in "wat nu"
    #
    # lesFlowWinst() loopt van boven naar beneden en geeft het eerste voorstel dat past. De vraag
    # van vandaag stond op plek twee, vóór het gesprek met Chispa. Die schuift dus gewoon op; er
    # blijft altijd een voorstel over.
    # =========================================================================================
    a = src.index("  /* v23.156: en de vraag van vandaag staat daar weer vóór.")
    b = src.index("  /* v23.144: het gesprek staat op plek twee", a)
    verwijderd["voorstel in wat-nu"] = src[a:b].count("\n")
    src = src[:a] + src[b:]

    # =========================================================================================
    # 3. het dagscherm
    # =========================================================================================
    rep("""    /* v22.7: de muur. v23.167: hij staat nu achter je les in plaats van eronder, en dat is de
       duurste regel van deze versie: schrijft je groep iets terwijl jij je les niet doet, dan zie
       je het pas morgen. Ik neem die prijs omdat de muur pas iets waard is als je zelf geschreven
       hebt (dagZinAnderen toont de anderen pas ná je eigen zin), en dat schrijven hoort in je les.
       Meting als dit fout is: schrijft hij minder vaak een zin dan hiervoor. */
    html += muurHtml();
""", "")
    rep("""  /* v23.167: alleen als de muur er staat. muurWire() en muurHaal() zijn veilig zonder kaart
     (beide beginnen met een getElementById-controle), maar muurHaal() doet een netwerkverzoek en
     dat is voor een scherm zonder muur een vraag om niets. */
  if(lesAf){ muurWire(); muurHaal(); try { dagZinWire(); } catch(e){} }
""", "")

    # =========================================================================================
    # 4. de functies en de data
    #
    # Volgorde is van buiten naar binnen: de aanroepers eerst, zodat een misser meteen als
    # "functie niet gevonden" naar boven komt en niet als stille rest.
    # =========================================================================================
    for f in ["muurTeken", "muurWire", "muurHaal", "muurHtml", "muurItemHtml",
              "muurReactieHtml", "muurReactiesVoor", "muurGebeurtenissen", "muurMijlpaalZin",
              "muurLesTitel", "muurGisteren",
              "dagZinWire", "dagZinHtml", "dagZinAnderen", "dagZinBij", "dagZinMijn", "dagVraag",
              "muurGroep"]:
        knipFunctie(f)

    # muurEsc kan niet langs knipFunctie: de body bevat de regexliteral /"/g, en de blokzoeker
    # hierboven leest die aanhaling als het begin van een string. Vanaf dat punt telt hij de
    # accolades verkeerd en knipt hij een willekeurig eind verderop weg. Letterlijk dus, en dat
    # is meteen de reden dat elke knip hieronder een naam-assertie achteraf krijgt: deze fout
    # gaf geen foutmelding maar een stil verdwenen array (DAGVRAGEN).
    rep("""// Namen komen van andere profielen en gaan als HTML het scherm op, dus altijd hierlangs.
function muurEsc(x){ return String(x == null ? "" : x)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
""", "")
    verwijderd["muurEsc"] = 3
    # muurEsc was teken voor teken veiligHtml(), en die stond er al. De groepenlijst gebruikte hem
    # ook, dus dit is geen weglaten maar het samenvoegen van twee kopieën van dezelfde regel.
    rep("""        return "<div class='duelrow'><span><b>"+muurEsc(sp.naam)+"</b>""",
        """        return "<div class='duelrow'><span><b>"+veiligHtml(sp.naam)+"</b>""")
    knipVarArray("DAGVRAGEN")
    knipRegel("var DAGZIN_MAX = 140")
    knipRegel("var muurData = null, muurBezig = false")

    # =========================================================================================
    # 5. de kop, en wat er van deze twee schermen overblijft
    #
    # De vier ontwerpregels van de muur en de redenering achter de dagvraag verdwijnen niet: ze
    # zijn het beste dat er over dit onderwerp is opgeschreven, en wie het opnieuw ontwerpt begint
    # daar. Ze staan hier ingekort en met de uitkomst erbij, want een ontwerpregel zonder meting
    # ernaast leest als een belofte.
    # =========================================================================================
    kop = src.index("/* ================= DE MUUR (v22.7) =================")
    eind = src.index("*/", kop) + 3
    src = src[:kop] + """/* ================= WAAR DE MUUR EN DE DAGVRAAG STONDEN (v22.7 - v23.222) =================

   Hier stonden twee schermen die het sociale moesten dragen, en ze zijn allebei weg omdat ze niet
   gebruikt werden. Wat ze probeerden, en wat de volgende poging moet meenemen:

   DE MUUR (v22.7) had vier regels, en ze zijn alle vier nog goed. 1. Gebeurtenissen, geen
   aanwezigheid: "Ilona kent nu 100 woorden" is inhoud, "dag 12" is een streak. 2. Eén regel per
   persoon per dag, de zwaarste die er die dag was, anders verdrinken mijlpalen zodra er meer dan
   twee maatjes zijn. 3. Jij staat er zelf tussen, in dezelfde lijst en met dezelfde maat. 4.
   Wegblijven is onzichtbaar: er is geen gebeurtenis voor niets doen, want schaamte is een slechte
   motor. Nergens stond een getal dat van twee mensen tegelijk was.

   DE VRAAG VAN VANDAAG (v23.156) was het enige in de app dat Chispa niet kan: je schrijft voor een
   echt mens die het gaat lezen. Niet synchroon (drie gebruikers die op verschillende momenten
   oefenen leveren een leeg chatvenster op, en een leeg venster meldt elke dag dat er niemand is),
   maar wel echt: één vraag per dag, voor iedereen in de groep dezelfde, en de anderen zie je pas
   ná je eigen zin.

   WAT ER MIS WAS, EN DAT ZIT NIET IN DIE REGELS. Beide schermen kwamen pas in beeld na "les af"
   (v23.167). Dat is verdedigd met een meting erbij: "schrijft hij minder vaak een zin dan
   hiervoor". Het antwoord na twee weken was nul zinnen. Een uitnodiging om te schrijven die je
   alleen ziet als je die dag al klaar bent, komt aan op het moment dat je weggaat.

   Stefan, 31 aug: "de muur was er om het sociale te bevorderen maar dat wordt niet echt gebruikt,
   dus dat moeten we helemaal opnieuw ontwerpen, en dan kunnen we het nu beter eerst weghalen, maar
   wel blijven meten op de achtergrond."

   HET METEN LOOPT DOOR. syncUp() stuurt de hele state naar /api/sync, dus S.mijlpalen, de dagoogst
   en S.groepen komen er nog elke dag aan. De muur was alleen een lezer (/api/groep/:gcode), en die
   endpoints staan er nog. Wie dit opnieuw ontwerpt heeft dus de gebeurtenissen van alle dagen
   ertussen, en hoeft niet vanaf nul te beginnen met tellen. */
""" + src[eind:]

if DOE_APP:
    # =========================================================================================
    # 6. het gat dichttrekken
    #
    # Negentien functies achter elkaar weg laat een rij lege regels achter. Die valt niemand op in
    # een diff maar wel bij het lezen, en het is precies het soort spoor dat de volgende lezer laat
    # denken dat er iets ontbreekt. Alleen hier, tussen de nieuwe kop en renderLessons().
    a = src.index("ertussen, en hoeft niet vanaf nul te beginnen met tellen. */")
    b = src.index("function renderLessons(){", a)
    src = src[:a] + "ertussen, en hoeft niet vanaf nul te beginnen met tellen. */\n\n" + src[b:]

    # =========================================================================================
    # de controle: wijst er nog iets naar de muur of de dagvraag?
    #
    # Over CODE, niet over commentaar: het blok hierboven noemt muurHtml en dagZinAnderen bij naam
    # en dat is juist de bedoeling.
    # =========================================================================================
    zonderCommentaar = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    zonderCommentaar = re.sub(r"^\s*//.*$", "", zonderCommentaar, flags=re.M)
    resten = {}
    for naam in ["DAGVRAGEN", "DAGZIN_MAX", "dagVraag", "dagZinMijn", "dagZinBij", "dagZinAnderen",
                 "dagZinHtml", "dagZinWire", "muurEsc", "muurGroep", "muurGisteren", "muurLesTitel",
                 "muurMijlpaalZin", "muurGebeurtenissen", "muurReactiesVoor", "muurReactieHtml",
                 "muurItemHtml", "muurHtml", "muurHaal", "muurTeken", "muurWire",
                 "muurData", "muurBezig", "muurGehaald", "muurOpen",
                 "dagzinCard", "dagzinInp", "btnDagzin", "muurCard"]:
        n = len(re.findall(r"\b" + re.escape(naam) + r"\b", zonderCommentaar))
        if n: resten[naam] = n
    assert not resten, "er wijst nog iets naar de muur of de dagvraag: %r" % resten
    assert "muur" not in re.sub(r"/\*.*?\*/", "", src, flags=re.S).split("<style>")[1].split("</style>")[0], \
        "er staat nog muur-stijl in het style-blok"

    # en wat er MOET blijven staan, want anders is dit geen verwijdering maar een sloop
    for blijft in ["function syncUp(", "var KRABBELS = [", "function krabbelVind(",
                   "function krabbelIkBen(", "function renderGroepen(", "function samenKaartNu(",
                   "function dagKrabbels("]:
        assert blijft in src, "dit had moeten blijven staan: " + blijft
    assert "state: S" in src, "syncUp stuurt de state niet meer mee: het meten is gestopt"

    # en de controle die v23.218 gemist zou hebben: een half weggeknipt blokcommentaar slokt de
    # code erachter op.
    #
    # Niet "evenveel /* als */": dat klopt in dit bestand sowieso niet, want een regexliteral als
    # /\s*([,·])\s*/ eindigt op */ zonder er een te zijn. Wel: het VERSCHIL mag niet veranderen.
    # Deze patch knipt alleen hele commentaarblokken weg, dus elke /* die verdwijnt neemt zijn */
    # mee. Loopt dat uiteen, dan is er een blok halverwege afgeknipt.
    na = _balans(src)
    assert na == balansVoor, \
        "commentaar loopt niet meer rond: /* min */ was %d en is nu %d" % (balansVoor, na)

    n = sum(verwijderd.values())
    APP.write_text(src, encoding="utf-8")
    print("index.html: de muur en de vraag van vandaag eruit, %d regels weg" % n)
    for k in sorted(verwijderd, key=lambda x: -verwijderd[x])[:6]:
        print("   %-22s %4d" % (k, verwijderd[k]))
else:
    print("index.html: stonden er al niet meer")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
