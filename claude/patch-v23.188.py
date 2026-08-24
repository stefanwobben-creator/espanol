#!/usr/bin/env python3
# v23.188 - drie dingen die stil misgingen
#
# Stefan, 24 aug, drie meldingen achter elkaar:
#
#   1. "gisteren tijdens de dagoefening liep ik vast, de volgende knop werkte niet. Die bug heb ik
#      nu weer."
#   2. "als ik op de suggestie 'puzzel' doen klik, gaat ie naar de puzzel die ik recent heb gedaan.
#      Hoe zou hij moeten refreshen."
#   3. "check ook nog even woordenzoeker en kruiswoord. Er zijn recente woorden die ik vaak fout
#      doe die ik hier niet terug zie."
#
# Alle drie nagemeten voordat er iets veranderde. Alle drie een andere fout, maar wel dezelfde
# soort: iets gebeurt niet, en niets zegt dat.
#
# ---------------------------------------------------------------------------------------------
# 1. DE KNOP DIE NIETS DEED, EN WAAROM HIJ MORGEN WEER NIETS DOET
#
# lesFlowVolgendeKern() is een rij van zes if-blokken, één per stap: woorden, grammatica, vormen,
# toetsjes, input, produceren. Er staat geen else onder. Draagt lesFlow.stap iets anders, dan valt
# de aanroep door alle zes heen en komt er onderaan uit. Geen fout, geen melding, geen schermwissel.
#
# Gemeten met een probe (test/probe-stap.js), zes verzonnen stapnamen:
#
#   stap          fout   toast   scherm veranderd
#   dictado       nee    nee     nee
#   lezen         nee    nee     nee
#   luisteren     nee    nee     nee
#   extra         nee    nee     nee
#   vertalen      nee    nee     nee
#   toetsjes-2    nee    nee     nee
#
# En dat blijft zo. lesFlowBewaar() staat in de finally van lesFlowVolgende en schrijft de kapotte
# stap netjes weg; lesFlowHervat() zet hem de volgende dag ongecontroleerd terug. Dat is precies wat
# Stefan beschrijft: gisteren vastgelopen, vandaag weer.
#
# De try/catch van v23.169 dekt dit niet af. Die vangt een fout die gegooid wordt. Hier wordt er
# niets gegooid; er gebeurt niets, en dat is erger, want een fout kun je zien.
#
# DE REPARATIE. Niet "controleer of de naam in een lijstje staat" (dat lijstje raakt achter, zoals
# elk lijstje naast een lijstje), maar: kijk of er iets geopend is. show() is de enige manier waarop
# de flow een scherm opent, dus een teller op show() zegt het onomstotelijk. Opende er niets, dan
# is de les klaargemaakt in plaats van doodgelopen, en er staat een regel in de console met de stap
# erbij, zodat de volgende melding een naam heeft.
#
# ---------------------------------------------------------------------------------------------
# 2. DE PUZZEL DIE AL AF WAS
#
# Er zijn twee wegen naar een spel, en maar één ervan maakt het schoon.
#
#   speelStart(g)  de tegel op de Speeltuin      roept g.verse() aan
#   speelNaar(v)   de suggestie na je les        heeft een eigen handgeschreven rijtje
#
# In dat handgeschreven rijtje staan audi, conj, hu, corr, kruis en adiv. letras staat er niet.
# Dus: via de tegel een verse puzzel, via de suggestie de puzzel die je net had uitgespeeld,
# inclusief "Alles gevonden! 🎉". Precies de schermafdruk van Stefan.
#
# Dit is dezelfde fout als de tien handgeschreven regels die v23.112 al eens opruimde, en de reden
# staat daar ook al opgeschreven: twee lijsten naast elkaar lopen uit elkaar. Nu leest speelNaar()
# de verse van spelInfo(), en dan is er nog één lijst.
#
# En de woordenzoeker had er helemaal geen. ws blijft staan tot je op "Nieuwe puzzel" klikt, via
# beide wegen. Die krijgt er dus een.
#
# ---------------------------------------------------------------------------------------------
# 3. DE WOORDEN DIE JE DEZE WEEK FOUT DEED
#
# gameVoorrang() bepaalt welke woorden in de woordenzoeker en het kruiswoord terechtkomen. Hij gaf
# drie rangen:
#
#   2   S.errors["woord:"+id].count >= 3      hardnekkig
#   1   S.srs[id].box <= 1                    wankel
#   0   de rest
#
# Er zit geen enkele verwijzing naar wannéér je dat woord fout deed in. S.errors draagt .dag en
# .laatst, en die worden hier niet gelezen. Twee gevolgen, en samen zijn ze exact Stefans zin:
#
#   - Een woord dat je gisteren en eergisteren fout deed heeft count 2, dus rang 0. Het staat
#     achteraan, tussen de woorden die je nooit fout hebt gedaan.
#   - Een woord dat je in mei drie keer fout deed heeft rang 2 en staat vóór alles van deze week.
#
# Nu telt eerst wanneer, dan hoe vaak. Wat je de laatste zeven dagen fout deed komt bovenaan,
# ongeacht hoe vaak; daarna het hardnekkige van langer geleden; daarna het wankele.
#
# WAT DIT NIET REPAREERT, en dat hoort erbij: wsWoordPool() laat alleen woorden door die uit één
# woord bestaan en na het strippen van accenten vier tot negen letters hebben. Een uitdrukking als
# "por favor" of een woord van drie letters kan niet in een raster, hoe vaak je hem ook fout doet.
# Ontbreekt zo'n woord, dan is dat geen voorrangskwestie maar de vorm van het spel.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.188"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "lesFlowOpende" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

# ------------------------------------------------------------------ 1. de bodem onder de knop
if DOE_APP:
    # a. show() telt hoe vaak hij een scherm heeft geopend
    rep("function show(tabId, skipPush){",
        "function show(tabId, skipPush){\n"
        "  /* v23.188: één teller, en verder verandert er niets aan show(). Hij is er zodat\n"
        "     lesFlowVolgende() kan vaststellen of er echt een scherm is opengegaan. Dat is de enige\n"
        "     vraag die telt bij een knop die niets doet, en er was geen manier om hem te stellen. */\n"
        "  lesFlowOpende++;")

    rep('var lesFlow = null; // {stap: null|"woorden"|"grammatica"|"toetsjes"|"produceren", quizzesTeDoen:[...ids], gramId, gekozenSpel, vertalenTeGaan}',
        'var lesFlow = null; // {stap: null|"woorden"|"grammatica"|"toetsjes"|"produceren", quizzesTeDoen:[...ids], gramId, gekozenSpel, vertalenTeGaan}\n'
        '/* v23.188: hoe vaak show() een scherm heeft geopend. Zie de bodem in lesFlowVolgende(). */\n'
        'var lesFlowOpende = 0;')

    # b. lesFlowVolgende kijkt of er iets geopend is
    rep(
        "  try {\n"
        "    lesFlowVolgendeKern();\n"
        "  } catch(e){\n"
        "    try { console.error(\"lesFlowVolgende:\", e && e.message, e); } catch(e2){}\n"
        "    try { toast(ct(\"Deze stap kon niet openen. Je les staat nog waar je was.\",\n"
        "                   \"This step could not open. Your session is still where you left it.\")); } catch(e3){}\n"
        "    try { show(\"lessen\"); } catch(e4){}\n"
        "  } finally {\n"
        "    lesFlowBewaar();\n"
        "  }",
        "  /* v23.188: en een bodem onder de bodem. De try/catch hierboven vangt een fout die gegooid\n"
        "     wordt. Wat Stefan op 23 en 24 augustus zag was iets anders: lesFlowVolgendeKern() is een\n"
        "     rij van zes if-blokken zonder else, dus een lesFlow.stap die geen van de zes namen draagt\n"
        "     valt er onderdoor. Geen fout, geen melding, geen schermwissel, en de knop is dood.\n"
        "\n"
        "     En hij blijft dood: lesFlowBewaar() hieronder schrijft die stap weg en lesFlowHervat()\n"
        "     zet hem morgen ongecontroleerd terug.\n"
        "\n"
        "     Niet gerepareerd met een lijstje geldige namen naast de zes if-blokken: twee lijsten\n"
        "     naast elkaar lopen uit elkaar, en dat is de fout in punt 2 van deze patch. In plaats\n"
        "     daarvan de vraag die er echt toe doet, en die maar één goed antwoord heeft: is er een\n"
        "     scherm opengegaan? show() is de enige weg daarheen, dus die telt mee. */\n"
        "  var opendeVoor = lesFlowOpende;\n"
        "  var stapVoor = lesFlow && lesFlow.stap;\n"
        "  try {\n"
        "    lesFlowVolgendeKern();\n"
        "    if(lesFlow && lesFlowOpende === opendeVoor){\n"
        "      try { console.error(\"lesFlowVolgende: stap \\\"\" + stapVoor + \"\\\" opende niets; les afgerond.\"); } catch(e5){}\n"
        "      /* Afronden en niet repareren-naar-de-volgende-stap: welke stap dat zou moeten zijn is\n"
        "         onbekend, en gokken levert een les op die halverwege opnieuw begint. Klaar is een\n"
        "         eerlijke uitkomst, hij ruimt S.lesFlowNu op (lesFlow wordt null) en morgen begin je\n"
        "         schoon in plaats van weer vast te lopen. */\n"
        "      try { toast(ct(\"Je les was hier klaar.\", \"Your session ended here.\")); } catch(e6){}\n"
        "      lesFlowKlaar();\n"
        "    }\n"
        "  } catch(e){\n"
        "    try { console.error(\"lesFlowVolgende:\", e && e.message, e); } catch(e2){}\n"
        "    try { toast(ct(\"Deze stap kon niet openen. Je les staat nog waar je was.\",\n"
        "                   \"This step could not open. Your session is still where you left it.\")); } catch(e3){}\n"
        "    try { show(\"lessen\"); } catch(e4){}\n"
        "  } finally {\n"
        "    lesFlowBewaar();\n"
        "  }")

# ------------------------------------------------------------------ 2. één lijst voor "vers"
if DOE_APP:
    rep(' {v:"ws",      id:"ftWs",      e:"\\ud83d\\udd0d",            t:fx("wsT"),               s:fx("wsS")},',
        ' /* v23.188: de woordenzoeker had als enige rasterspel geen verse, dus je kwam terug op het\n'
        '     raster dat je al had uitgespeeld. Zelfde afspraak als bij Letras en Crucigrama. */\n'
        ' {v:"ws",      id:"ftWs",      e:"\\ud83d\\udd0d",            t:fx("wsT"),               s:fx("wsS"), verse:function(){ ws = null; }},')

    rep(
        '  if(v === "audi"){ audMenu = true; }\n'
        '  if(v === "conj"){ conjIdx = null; conjRonde = null; }\n'
        '  if(v === "hu"){ huIdx = null; huRonde = null; }\n'
        '  if(v === "corr"){ corrOpg = null; corrRonde = null; }\n'
        '  if(v === "kruis"){ kruisLos = null; }\n'
        '  if(v === "adiv"){ adivSpel = null; }\n'
        '  show("speeltuin");',
        '  if(v === "audi"){ audMenu = true; }\n'
        '  /* v23.188. Hier stond ook "kruis" en "adiv", en niet "letras" en niet "ws". Gevolg: klikte\n'
        '     je de suggestie na je les aan, dan stond de puzzel er nog zoals je hem had achtergelaten,\n'
        '     compleet met "Alles gevonden!". Via de tegel op de Speeltuin kreeg je wél een verse, want\n'
        '     speelStart() roept g.verse() aan.\n'
        '\n'
        '     Dat is exact de fout die v23.112 al eens heeft opgeruimd: een handgeschreven rij naast\n'
        '     spelInfo(), die ermee uit de pas loopt. Nu leest deze weg dezelfde verse als de tegel, en\n'
        '     is er nog één lijst. De drie regels hieronder blijven met de hand, want conj, hu en corr\n'
        '     staan niet in spelInfo(): zij hebben geen tegel. */\n'
        '  var info = null;\n'
        '  try { info = spelInfoVan(v); } catch(e){ info = null; }\n'
        '  if(info && info.verse){ try { info.verse(); } catch(e){} }\n'
        '  if(v === "conj"){ conjIdx = null; conjRonde = null; }\n'
        '  if(v === "hu"){ huIdx = null; huRonde = null; }\n'
        '  if(v === "corr"){ corrOpg = null; corrRonde = null; }\n'
        '  show("speeltuin");')

# ------------------------------------------------------------------ 3. eerst wanneer, dan hoe vaak
if DOE_APP:
    rep(
        'function gameVoorrang(pool){\n'
        '  function score(id){\n'
        '    var e = S.errors["woord:" + id];\n'
        '    if(e && e.count >= 3) return 2;            // hardnekkig: komt het eerst\n'
        '    var st = S.srs[id];\n'
        '    if(st && st.box <= 1) return 1;            // wankel: daarna\n'
        '    return 0;                                   // de rest vult aan\n'
        '  }',
        '/* v23.188. Stefan, 24 aug: "er zijn recente woorden die ik vaak fout doe die ik hier niet\n'
        '   terug zie." Nagelopen, en hij heeft gelijk: hier stond nergens wannéér je een woord fout\n'
        '   deed. S.errors draagt .dag (de dag van de laatste fout) en die werd niet gelezen.\n'
        '\n'
        '   Twee gevolgen, en samen zijn ze precies zijn zin. Een woord dat je gisteren én eergisteren\n'
        '   fout deed heeft count 2, haalde de drempel van 3 niet, en stond dus achteraan tussen de\n'
        '   woorden die je nooit fout hebt gedaan. En een woord dat je in mei drie keer fout deed stond\n'
        '   vóór alles van deze week.\n'
        '\n'
        '   Nu eerst wanneer, dan hoe vaak. De grens ligt op zeven dagen: dat is de week waar je zelf\n'
        '   nog een herinnering aan hebt, en het is dezelfde orde als de eerste doosjes van de SRS.\n'
        '\n'
        '   Wat dit NIET repareert: wsWoordPool() laat alleen losse woorden van vier tot negen letters\n'
        '   door. Een uitdrukking of een woord van drie letters past niet in een raster, hoe vaak je\n'
        '   hem ook fout doet. Ontbreekt zo\'n woord, dan is dat de vorm van het spel en niet de\n'
        '   voorrang. */\n'
        'var GAME_VERS_DAGEN = 7;\n'
        'function gameVoorrang(pool){\n'
        '  function score(id){\n'
        '    var e = S.errors["woord:" + id];\n'
        '    var dagen = 9999;\n'
        '    try { if(e) dagen = peilDagenGeleden(e.dag || e.laatst); } catch(x){ dagen = 9999; }\n'
        '    if(e && dagen <= GAME_VERS_DAGEN) return 3;  // deze week fout: dat is waar je nu staat\n'
        '    if(e && e.count >= 3) return 2;            // hardnekkig van langer geleden: daarna\n'
        '    var st = S.srs[id];\n'
        '    if(st && st.box <= 1) return 1;            // wankel: daarna\n'
        '    return 0;                                   // de rest vult aan\n'
        '  }')

# ------------------------------------------------------------------ schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: de bodem onder de knop, één verse-lijst, en verse fouten voorop, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
