#!/usr/bin/env python3
# Nachtrun 26 aug: vijf drillzinnen (s265-s269) op de verse fouten van 25 aug,
# plus het al drie runs openstaande kaart-advies uitgevoerd: cv196 (adivinar) en
# cv197 (devolver) krijgen een meer-veld met ezelsbrug.
# Idempotent: draait alleen als s265 nog niet bestaat.
import io, sys

PAD = "index.html"
src = io.open(PAD, encoding="utf-8").read()

if '"s265"' in src:
    print("al toegepast, niets gedaan"); sys.exit(0)

def rep(anker, nieuw, n=1):
    global src
    k = src.count(anker)
    if k != n:
        print(f"FOUT: anker {k}x gevonden (verwacht {n}): {anker[:80]}"); sys.exit(1)
    src = src.replace(anker, nieuw)

ZINNEN = ''' {"id": "s265", "lvl": 2, "nl": "We zijn verdwaald omdat ik de kaart ben verloren.", "en": "We are lost because I have lost the map.", "es": "Estamos perdidos porque he perdido el mapa.", "alt": ["estamos perdidos porque he perdido el mapa", "estamos perdidos porque perdí el mapa"], "uitleg": "Perdido, zes keer gemist als woordkaartje, heeft twee gezichten in één zin. Na haber is het het participio van perder en verandert het nooit: he perdido el mapa, hemos perdido las llaves. Met estar is het een bijvoeglijk naamwoord (verdwaald) en buigt het wél mee: estamos perdidos, ella está perdida. Je kende al: He perdido las gafas (met encontrar als tegenhanger).", "ue": "Perdido, missed six times as a word card, has two faces in one sentence. After haber it is the participle of perder and never changes: he perdido el mapa, hemos perdido las llaves. With estar it is an adjective (lost, astray) and does agree: estamos perdidos, ella está perdida. You already knew: He perdido las gafas (with encontrar as its counterpart).", "tag": "perder"},
 {"id": "s266", "lvl": 2, "nl": "Ik heb sinds gisteren pijn aan mijn oor.", "en": "My ear has been hurting since yesterday.", "es": "Me duele el oído desde ayer.", "alt": ["me duele el oído desde ayer", "me duele la oreja desde ayer"], "uitleg": "El oído, vier keer gemist, is drie dingen tegelijk: het (binnen)oor en het gehoor (me duele el oído), terwijl la oreja de zichtbare buitenkant is, én het is het participio van oír: ¿Has oído la noticia? = heb je het nieuws gehoord? Bij pijn werkt doler als gustar: me duele el oído, niet mi oído.", "ue": "El oído, missed four times, is three things at once: the (inner) ear and the sense of hearing (me duele el oído), while la oreja is the visible outer ear, and it is also the participle of oír: ¿Has oído la noticia? = have you heard the news? With pain, doler works like gustar: me duele el oído, not mi oído.", "tag": "doler"},
 {"id": "s267", "lvl": 2, "nl": "De apotheek is naast de supermarkt.", "en": "The pharmacy is next to the supermarket.", "es": "La farmacia está al lado del supermercado.", "alt": ["la farmacia está al lado del supermercado", "la farmacia esta al lado del supermercado"], "uitleg": "El lado = de kant, vijf keer gemist als kaartje. Je komt het vooral tegen in vaste combinaties: al lado de = naast (a + el = al, de + el = del), al otro lado = aan de andere kant, en por un lado... por otro lado = enerzijds... anderzijds. Estar, want het gaat om een plaats.", "ue": "El lado = the side, missed five times as a card. You mostly meet it in set combinations: al lado de = next to (a + el = al, de + el = del), al otro lado = on the other side, and por un lado... por otro lado = on the one hand... on the other hand. Estar, because it is about location.", "tag": "lado"},
 {"id": "s268", "lvl": 2, "nl": "Wat gebeurde er gisteren op het feest?", "en": "What happened yesterday at the party?", "es": "¿Qué pasó ayer en la fiesta?", "alt": ["qué pasó ayer en la fiesta", "que pasó ayer en la fiesta", "¿qué pasó ayer en la fiesta?"], "uitleg": "Pasó is de él/ella-vorm van pasar in het indefinido, drie keer gemist als kaartje. Pasar = gebeuren: ¿Qué pasa? = wat is er?, ¿Qué pasó? = wat is er gebeurd? Maar ook doorbrengen: pasé el verano en Alicante. Het accent doet het werk: pasó = het gebeurde, paso = ik passeer (presente, yo).", "ue": "Pasó is the él/ella form of pasar in the indefinido, missed three times as a card. Pasar = to happen: ¿Qué pasa? = what's up?, ¿Qué pasó? = what happened? But also to spend (time): pasé el verano en Alicante. The accent does the work: pasó = it happened, paso = I pass (presente, yo).", "tag": "pasar"},
 {"id": "s269", "lvl": 2, "nl": "In het begin begreep ik niets, maar uiteindelijk leerde ik veel.", "en": "At first I didn't understand anything, but in the end I learned a lot.", "es": "Al principio no entendí nada, pero al final aprendí mucho.", "alt": ["al principio no entendí nada pero al final aprendí mucho", "al principio no entendi nada pero al final aprendi mucho"], "uitleg": "El principio = het begin, nu vier keer mis. Bijna altijd in al principio = in het begin, met al final als tegenhanger — het vaste duo van elk verhaal. Verwar het niet met el príncipe (de prins) en ook niet met primero (eerst, als eerste), dat deze week ook misging. Entendí en aprendí zijn indefinido: afgeronde stappen in een verhaal.", "ue": "El principio = the beginning, now missed four times. Almost always in al principio = at first, with al final as its counterpart — the fixed pair of every story. Don't confuse it with el príncipe (the prince) nor with primero (first), which you also missed this week. Entendí and aprendí are indefinido: completed steps in a story.", "tag": "relatar"},
'''

# 1. Zinnen invoegen vóór het einde van SENTENCES (na s264).
rep('"tag": "pronombres"},\n];\n\nvar QUIZZES = [',
    '"tag": "pronombres"},\n' + ZINNEN + '];\n\nvar QUIZZES = [')

# 2. EXTRA_CONTENT-koppelingen.
rep('''    "s254",
    "s255",
    "s256",
    "s259"
   ],''', '''    "s254",
    "s255",
    "s256",
    "s259",
    "s265",
    "s269"
   ],''')                      # a2-10 <- s265, s269
rep('''    "s257",
    "s260",
    "s261"
   ],''', '''    "s257",
    "s260",
    "s261",
    "s267"
   ],''')                      # a2-4 <- s267
rep('''    "s142",
    "s143",
    "s176",''', '''    "s142",
    "s143",
    "s176",''')               # (anker-check a2-2 bestaat)
rep('''    "s234",
    "s238",
    "s258"
   ],''', '''    "s234",
    "s238",
    "s258",
    "s268"
   ],''')                      # a2-2 <- s268
# a2-8 heeft nog geen EXTRA_CONTENT-blok; nieuw blok aanmaken (consument itereert
# over les-ids en slaat ontbrekende keys over, dus een nieuwe key is veilig).
rep('''  "a2-7": {
   "words": [],
   "sents": [
    "s160",
    "s228",
    "s242",
    "s262"
   ],
   "quizzes": []
  }
 },''', '''  "a2-7": {
   "words": [],
   "sents": [
    "s160",
    "s228",
    "s242",
    "s262"
   ],
   "quizzes": []
  },
  "a2-8": {
   "words": [],
   "sents": [
    "s266"
   ],
   "quizzes": []
  }
 },''')                        # a2-8 <- s266

# 3. Kaart-advies (open sinds 22/23 aug, drie runs, cluster escaleert):
#    ezelsbrug als meer-veld op de kaart zelf, zoals de nachtrun-docs adviseren.
rep('{id:"cv196", es:"adivinar", nl:"raden", tag:"cerv-school", sl:"adivinar"}',
    '{id:"cv196", es:"adivinar", nl:"raden", tag:"cerv-school", sl:"adivinar", meer:"denk aan el adivino = de waarzegger, la adivinanza = het raadsel"}')
rep('{id:"cv197", es:"devolver", nl:"teruggeven", tag:"cerv-winkelen", sl:"devolver"}',
    '{id:"cv197", es:"devolver", nl:"teruggeven", tag:"cerv-winkelen", sl:"devolver", meer:"familie van volver (terugkeren): devolver = terug laten gaan"}')

# 4. Batch-label en versie.
rep('batch:"batch-24"', 'batch:"batch-25"')
rep('var APP_VERSIE = "v23.195";', 'var APP_VERSIE = "v23.196";')

io.open(PAD, "w", encoding="utf-8").write(src)
io.open("versie.txt", "w", encoding="utf-8").write("v23.196\n")
print("klaar: s265-s269, meer-veld cv196/cv197, batch-25, v23.196")
