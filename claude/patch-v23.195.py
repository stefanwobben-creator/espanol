#!/usr/bin/env python3
# Nachtrun 25 aug: vier drillzinnen (s261-s264) op de verse fouten van 24 aug.
# Idempotent: draait alleen als s261 nog niet bestaat.
import io, sys

PAD = "index.html"
src = io.open(PAD, encoding="utf-8").read()

if '"s261"' in src:
    print("al toegepast, niets gedaan"); sys.exit(0)

def rep(anker, nieuw, n=1):
    global src
    k = src.count(anker)
    if k != n:
        print(f"FOUT: anker {k}x gevonden (verwacht {n}): {anker[:80]}"); sys.exit(1)
    src = src.replace(anker, nieuw)

ZINNEN = ''' {"id": "s261", "lvl": 2, "nl": "Ik haal de sleutels uit de tas en open de deur.", "en": "I take the keys out of the bag and open the door.", "es": "Saco las llaves del bolso y abro la puerta.", "alt": ["saco las llaves del bolso y abro la puerta", "saco las llaves de la bolsa y abro la puerta"], "uitleg": "Sacar = eruit halen, tevoorschijn halen, vier keer gemist als woordkaartje. Altijd met de erbij: sacar las llaves del bolso (de + el = del). Onthoud ook de vaste uitdrukkingen sacar fotos (foto's maken) en sacar buenas notas (goede cijfers halen). De yo-vorm is gewoon saco, maar in het indefinido komt er qu: saqué.", "ue": "Sacar = to take out, missed four times as a word card. It goes with de: sacar las llaves del bolso (de + el = del). Also remember the set phrases sacar fotos (to take pictures) and sacar buenas notas (to get good grades). The yo form is simply saco, but in the indefinido it takes qu: saqué.", "tag": "sacar"},
 {"id": "s262", "lvl": 2, "nl": "De koelkast zit vol verse groenten.", "en": "The fridge is full of fresh vegetables.", "es": "La nevera está llena de verduras frescas.", "alt": ["la nevera esta llena de verduras frescas", "el frigorífico está lleno de verduras frescas"], "uitleg": "Lleno = vol, nieuw in je foutenlog. Het buigt mee als een gewoon bijvoeglijk naamwoord: el vaso está lleno, la nevera está llena. Altijd met estar (het is een toestand) en met de erachter: lleno de gente, llena de verduras. Het werkwoord is llenar = vullen.", "ue": "Lleno = full, new in your error log. It agrees like any adjective: el vaso está lleno, la nevera está llena. Always with estar (it is a state) and followed by de: lleno de gente, llena de verduras. The verb is llenar = to fill.", "tag": "ser-estar"},
 {"id": "s263", "lvl": 2, "nl": "Als je twijfels hebt, vraag het dan in de les.", "en": "If you have doubts, ask in class.", "es": "Si tienes dudas, pregunta en clase.", "alt": ["si tienes dudas pregunta en clase", "si tienes dudas, pregunta en la clase", "si tienes una duda, pregunta en clase"], "uitleg": "La duda = de twijfel, vier keer misgegaan als woordkaartje. Het Spaans gebruikt het vaak in het meervoud: tener dudas = twijfels of vragen hebben. Sin duda = zonder twijfel (stond al op je kaartje), en het werkwoord is dudar. Pregunta is hier de imperativo van preguntar.", "ue": "La duda = the doubt, missed four times as a word card. Spanish often uses it in the plural: tener dudas = to have doubts or questions. Sin duda = without a doubt (already on your card), and the verb is dudar. Pregunta here is the imperativo of preguntar.", "tag": "duda"},
 {"id": "s264", "lvl": 2, "nl": "De rekening? Het kost me moeite om die te splitsen.", "en": "The bill? I find it hard to split it.", "es": "¿La cuenta? Me cuesta dividirla.", "alt": ["la cuenta me cuesta dividirla", "¿la cuenta? me cuesta dividirla"], "uitleg": "Bij deze zin typte je eerder 'lo dividir la cuenta', en daar zit de regel: een los voornaamwoord staat nooit vóór een infinitief. Het plakt eraan vast: dividir + la = dividirla (la, want la cuenta is vrouwelijk). Vóór een vervoegd werkwoord staat het wél los: la divido. Dus: me cuesta dividirla, of la divido yo.", "ue": "On this sentence you once typed 'lo dividir la cuenta', and that is exactly the rule: a loose pronoun never goes before an infinitive. It attaches to it: dividir + la = dividirla (la, because la cuenta is feminine). Before a conjugated verb it does stand alone: la divido. So: me cuesta dividirla, or la divido yo.", "tag": "pronombres"},
'''

# 1. Zinnen invoegen vóór het einde van SENTENCES (na s260).
rep('"tag": "hay"}\n];\n\nvar QUIZZES = [',
    '"tag": "hay"},\n' + ZINNEN + '];\n\nvar QUIZZES = [')

# 2. EXTRA_CONTENT-koppelingen.
rep('''    "s257",
    "s260"
   ],''', '''    "s257",
    "s260",
    "s261"
   ],''')                      # a2-4 <- s261
rep('''    "s160",
    "s228",
    "s242"
   ],''', '''    "s160",
    "s228",
    "s242",
    "s262"
   ],''')                      # a2-7 <- s262
rep('''    "s252",
    "s253"
   ],''', '''    "s252",
    "s253",
    "s263",
    "s264"
   ],''')                      # a2-1 <- s263, s264

# 3. Batch-label en versie.
rep('batch:"batch-23"', 'batch:"batch-24"')
rep('var APP_VERSIE = "v23.194";', 'var APP_VERSIE = "v23.195";')

io.open(PAD, "w", encoding="utf-8").write(src)
io.open("versie.txt", "w", encoding="utf-8").write("v23.195\n")
print("klaar: s261-s264, batch-24, v23.195")
