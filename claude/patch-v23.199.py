#!/usr/bin/env python3
# Nachtrun 28 aug: drie drillzinnen (s270-s272) op de verse fouten van 26-27 aug
# (snapshot 9929c91, handmatig gestart op 27 aug nadat de cron-run uitbleef; dekt
# de twee onverwerkte dagen sinds f073dc4), plus het kaart-regime voor sacar
# (cv290) en lleno (cv297): tweede groei na drill, conform de herchecklijst van
# 26 aug. Versie springt naar v23.199 (v23.197/198 bestaan als dag-patches naast
# main, zie het 27-aug-doc).
# Idempotent: draait alleen als s270 nog niet bestaat.
import io, sys

PAD = "index.html"
src = io.open(PAD, encoding="utf-8").read()

if '"s270"' in src:
    print("al toegepast, niets gedaan"); sys.exit(0)

def rep(anker, nieuw, n=1):
    global src
    k = src.count(anker)
    if k != n:
        print(f"FOUT: anker {k}x gevonden (verwacht {n}): {anker[:80]}"); sys.exit(1)
    src = src.replace(anker, nieuw)

ZINNEN = ''' {"id": "s270", "lvl": 2, "nl": "De twee appartementen hebben dezelfde grootte.", "en": "The two flats are the same size.", "es": "Los dos pisos tienen el mismo tamaño.", "alt": ["los dos pisos tienen el mismo tamaño", "los dos pisos tienen el mismo tamano"], "uitleg": "El tamaño = de grootte, het formaat, zes keer gemist als kaartje. Het komt van het Latijnse tam magnus = 'zo groot' — daar zit je ezelsbrug. Vaste combinaties: del mismo tamaño = even groot, ¿qué tamaño tiene? = hoe groot is het? Verwar het niet met la talla (kledingmaat) of el número (schoenmaat).", "ue": "El tamaño = the size, missed six times as a card. It comes from Latin tam magnus = 'so big' — there is your mnemonic. Set phrases: del mismo tamaño = the same size, ¿qué tamaño tiene? = how big is it? Don't confuse it with la talla (clothing size) or el número (shoe size).", "tag": "les4"},
 {"id": "s271", "lvl": 2, "nl": "Eet niet zo snel, geniet van het eten.", "en": "Don't eat so fast, enjoy the food.", "es": "No comas tan deprisa, disfruta de la comida.", "alt": ["no comas tan deprisa disfruta de la comida", "no comas tan deprisa, disfruta de la comida"], "uitleg": "Deprisa = snel, vlug (bijwoord, één woord), vijf keer gemist als kaartje. Familie van la prisa (de haast): tener prisa = haast hebben, ¡date prisa! = schiet op! No comas is de ontkennende imperativo (subjuntivo-vorm), en disfrutar krijgt de: disfruta de la comida — hetzelfde de dat je eerder miste in disfrutar de la obra.", "ue": "Deprisa = fast, quickly (adverb, one word), missed five times as a card. Family of la prisa (the hurry): tener prisa = to be in a hurry, ¡date prisa! = hurry up! No comas is the negative imperative (subjuntivo form), and disfrutar takes de: disfruta de la comida — the same de you missed before in disfrutar de la obra.", "tag": "cocina"},
 {"id": "s272", "lvl": 2, "nl": "Mijn zus zorgt voor onze zieke oma.", "en": "My sister takes care of our sick grandmother.", "es": "Mi hermana cuida de nuestra abuela enferma.", "alt": ["mi hermana cuida de nuestra abuela enferma", "mi hermana cuida a nuestra abuela enferma"], "uitleg": "Cuidar (de) = zorgen voor, vier keer gemist als kaartje. Cuidar de alguien of cuidar a alguien — allebei goed. Cuidarse = voor jezelf zorgen, en ¡cuídate! = pas goed op jezelf: de vaste afscheidsgroet én de titel van deze les. Ook familie: el cuidado = de zorg, ¡cuidado! = pas op!", "ue": "Cuidar (de) = to take care of, missed four times as a card. Cuidar de alguien or cuidar a alguien — both are fine. Cuidarse = to look after yourself, and ¡cuídate! = take care: the standard goodbye and the title of this lesson. Same family: el cuidado = care, ¡cuidado! = watch out!", "tag": "salud"},
'''

# 1. Zinnen invoegen aan het einde van SENTENCES (na s269).
rep('"tag": "relatar"},\n];\n\nvar QUIZZES = [',
    '"tag": "relatar"},\n' + ZINNEN + '];\n\nvar QUIZZES = [')

# 2. EXTRA_CONTENT-koppelingen.
rep('''    "s260",
    "s261",
    "s267"
   ],''', '''    "s260",
    "s261",
    "s267",
    "s270"
   ],''')                      # a2-4 <- s270 (tamaño, wonen/vergelijken)
rep('''    "s228",
    "s242",
    "s262"
   ],''', '''    "s228",
    "s242",
    "s262",
    "s271"
   ],''')                      # a2-7 <- s271 (deprisa, eten/imperativo)
rep('''  "a2-8": {
   "words": [],
   "sents": [
    "s266"
   ],''', '''  "a2-8": {
   "words": [],
   "sents": [
    "s266",
    "s272"
   ],''')                      # a2-8 <- s272 (cuidar, Cuídate)

# 3. Kaart-regime sacar/lleno: tweede groei na drill (herchecklijst 26 aug,
#    zelfde escalatie als adivinar/devolver in v23.196): meer-veld op de kaart.
rep('{id:"cv290", es:"sacar", nl:"eruit halen, tevoorschijn halen", tag:"cerv-school", sl:"sacar"}',
    '{id:"cv290", es:"sacar", nl:"eruit halen, tevoorschijn halen", tag:"cerv-school", sl:"sacar", meer:"denk aan el saco = de zak: sacar = uit de zak halen; sacar fotos, sacar buenas notas"}')
rep('{id:"cv297", es:"lleno", nl:"vol", tag:"cerv-bestaan", sl:"lleno"}',
    '{id:"cv297", es:"lleno", nl:"vol", tag:"cerv-bestaan", sl:"lleno", meer:"familie van llenar (vullen): lleno de = vol met; tegenover vacío (leeg)"}')

# 4. Batch-label en versie.
rep('batch:"batch-25"', 'batch:"batch-26"')
rep('var APP_VERSIE = "v23.196";', 'var APP_VERSIE = "v23.199";')

io.open(PAD, "w", encoding="utf-8").write(src)
io.open("versie.txt", "w", encoding="utf-8").write("v23.199\n")
print("klaar: s270-s272, meer-veld cv290/cv297, batch-26, v23.199")
