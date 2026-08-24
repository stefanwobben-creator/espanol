#!/usr/bin/env python3
# v23.190 - de opfrisser trok bij elke aanraking een nieuwe vraag
#
# Stefan, 24 aug: "Bij opfrissen laat ie niet het goede of foute antwoord zien maar gaat ie
# automatisch direct door naar volgende." Op mijn vraag of het misging bij goed of bij fout: "dat
# weet ik niet meer."
#
# Ik heb eerst twee verklaringen doodgelopen, en dat hoort erbij:
#
#   1. Een automatische doorschuiver in de code. Bestaat niet: gwVolgende() en gwVolgendeStap()
#      hangen allebei aan een onclick en aan niets anders.
#   2. De knop landt onder je vinger. Nagemeten op tien opfrissers maal goed en fout, venster 420
#      bij 880: minimaal 97 pixels tussen de knop waarop je klikte en "Volgende", gemiddeld 148.
#      Geen enkele overlap.
#
# EN TOEN VIEL DE ECHTE OP, DOORDAT MIJN EIGEN TESTSUITE ONREGELMATIG ROOD WERD
#
# gcOnderwerp() (de microles) heeft een cache, met daarboven deze regels, al sinds v20.5:
#
#     De vragen worden bij elke start opnieuw gemaakt, maar BINNEN een sessie moet het object stil
#     blijven staan: gwKies() en gwVolgende() halen het onderwerp opnieuw op, en zonder cache zou de
#     vraag onder je handen veranderen.
#
# gcOpfrisOnderwerp() (v23.73) gaat langs die cache heen en roept gcMaakVragen() aan. Elke aanroep.
#
# Gemeten, vijf keer gwVragen() achter elkaar op hetzelfde onderwerp zonder iets aan te raken:
#
#   opfris-genero          3 verschillende trekkingen uit 5      microles: 1 uit 5
#   opfris-concordancia    5 uit 5                                microles: 1 uit 5
#   opfris-serestar        5 uit 5                                microles: 1 uit 5
#   opfris-hayestar        5 uit 5                                microles: 1 uit 5
#   opfris-negacion        2 uit 5                                microles: 1 uit 5
#   opfris-muymucho        3 uit 5                                microles: 1 uit 5
#   opfris-tuusted         2 uit 5                                microles: 1 uit 5
#   opfris-futuroir        4 uit 5                                microles: 1 uit 5
#
# Acht van de acht opfrissers wisselen, acht van de acht microlessen niet.
#
# WAT DAT OP HET SCHERM DOET
#
# Eén klik raakt drie verschillende trekkingen:
#
#   renderCheat()   tekent trekking A en zet de opties in die volgorde neer
#   jij klikt       op knop i van trekking A
#   gwKies(i)       haalt trekking B op en rekent i af tegen B.g
#   renderCheat()   tekent trekking C en markeert C.g als het juiste antwoord
#
# Bij opfris-muymucho staat dezelfde vraag er twee keer met de opties omgewisseld, en juist springt
# van 1 naar 0. Je klikt dus "muy", wordt afgerekend alsof je "mucho" koos, en ziet daarna een
# markering die bij geen van beide hoort. Bij opfris-concordancia verandert de vraag zelf mee ("The
# house is old" wordt "The house is red"), dus de uitleg eronder gaat over een vraag die je nooit
# hebt gezien.
#
# Dat is precies "laat niet het goede of foute antwoord zien", en het staat er sinds v23.73.
#
# DE REPARATIE
#
# Dezelfde cache, dezelfde vernieuwing bij de start. Niet een eigen oplossing ernaast: de microles
# had dit probleem al opgelost en de opfrisser hoorde daar gewoon in mee te gaan.
#
#   - gcOpfrisOnderwerp() bouwt nog één keer per sessie, via gcCache, met dezelfde sleutel.
#   - gwStart() vernieuwt ook voor opfris-, zodat je elke keer dat je begint een verse vraag krijgt.
#     Zonder die regel zou je vandaag en morgen dezelfde vraag zien, en dat is de andere fout.
#   - gcVernieuw() gaat via gwOnderwerp() in plaats van gcOnderwerp(), anders bouwt hij een
#     opfris-id nooit terug.
#
# EN DE MARKERING ZELF
#
# Los daarvan, en ook waar: de opfrisser markeerde alleen het juiste antwoord en niet dat van jou.
# Het toetsje doet dit al jaren met twee kleuren (answerQuestion: .correct groen op het juiste,
# .wrong rood op jouw knop). Dat verschil is v23.189; deze patch is de oorzaak eronder.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.190"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "gcOpfrisBouw" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

# ---------------------------------------------------------------- 1. de opfrisser in de cache
if DOE_APP:
    rep("function gcOpfrisOnderwerp(id){\n"
        "  var cid = String(id || \"\").replace(/^opfris-/, \"\");",
        "/* v23.190. Hier stond gcOpfrisOnderwerp() zelf, en die bouwde bij ELKE aanroep een nieuwe\n"
        "   vraag. gwKies() en renderCheat() halen het onderwerp allebei opnieuw op, dus één klik\n"
        "   raakte drie verschillende trekkingen: je klikte op de opties van A, werd afgerekend tegen\n"
        "   B, en zag de markering van C. Gemeten: acht van de acht opfrissers wisselden binnen vijf\n"
        "   aanroepen, acht van de acht microlessen niet.\n"
        "\n"
        "   Dat verschil zat 'm in de cache van gcOnderwerp(), met daarboven al sinds v20.5 precies de\n"
        "   waarschuwing waar dit in liep: \"BINNEN een sessie moet het object stil blijven staan\".\n"
        "   De opfrisser van v23.73 ging daar langsheen. Nu gaat hij er doorheen, met dezelfde sleutel\n"
        "   en dezelfde vernieuwing bij de start (zie gwStart). */\n"
        "function gcOpfrisOnderwerp(id){\n"
        "  var key = id + \"|\" + profLang();\n"
        "  if(!gcCache[key]) gcCache[key] = gcOpfrisBouw(id);\n"
        "  return gcCache[key];\n"
        "}\n"
        "function gcOpfrisBouw(id){\n"
        "  var cid = String(id || \"\").replace(/^opfris-/, \"\");")

# ---------------------------------------------------------------- 2. en vers bij elke start
if DOE_APP:
    rep("  // v20.5: een conceptles wordt bij elke start opnieuw gegenereerd. Je kunt geen antwoord\n"
        "  // onthouden van een vraag die nog niet bestond.\n"
        "  if(/^concept-/.test(id || \"\")) gcVernieuw(id);",
        "  // v20.5: een conceptles wordt bij elke start opnieuw gegenereerd. Je kunt geen antwoord\n"
        "  // onthouden van een vraag die nog niet bestond.\n"
        "  /* v23.190: en de opfrisser net zo goed. Hij zit sinds deze versie in dezelfde cache, en\n"
        "     zonder deze regel zou hij daardoor juist het omgekeerde krijgen: elke dag dezelfde vraag.\n"
        "     Vers bij de start, stil binnen de sessie. */\n"
        "  if(/^(concept|opfris)-/.test(id || \"\")) gcVernieuw(id);")

    rep("function gcVernieuw(id){\n"
        "  delete gcCache[id + \"|\" + profLang()];\n"
        "  return gcOnderwerp(id);\n"
        "}",
        "function gcVernieuw(id){\n"
        "  delete gcCache[id + \"|\" + profLang()];\n"
        "  /* v23.190: via gwOnderwerp() en niet via gcOnderwerp(), want die kent alleen concept-ids.\n"
        "     Met de oude regel bouwde een opfris-id na het legen nooit meer terug. */\n"
        "  return gwOnderwerp(id);\n"
        "}")

# ---------------------------------------------------------------- schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: de opfrisser staat stil binnen een sessie, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
