#!/usr/bin/env python3
# Nachtrun 29 aug: drie drillzinnen (s273-s275) op de verse fouten van 27-28 aug
# (snapshot e6fb80d, handmatig gestart 28 aug 13:01 — de cron leverde opnieuw
# niets), plus het kaart-regime voor perdido (cv247) en pasó (cv224): allebei
# tweede groei na drill, conform de herchecklijst van 28 aug. Devolver (cv197,
# +9 ondanks twee drills én ezelsbrug) krijgt een derde invalshoek: presente-
# vorm + prestar-partner (s273) en een aangescherpt meer-veld. Liedverzoek van
# 28 aug 10:21 verwerkt: song-chevere (ARIA VEGA, Ryan Castro - CHÉVERE).
# Versie springt naar v23.201: v23.200 is geclaimd door Stefans dag-patch
# (vamos-v23.200.patch, nog niet op main), zie het v23.200-doc.
# Idempotent: draait alleen als s273 nog niet bestaat.
import io, sys

PAD = "index.html"
src = io.open(PAD, encoding="utf-8").read()

if '"s273"' in src:
    print("al toegepast, niets gedaan"); sys.exit(0)

def rep(anker, nieuw, n=1):
    global src
    k = src.count(anker)
    if k != n:
        print(f"FOUT: anker {k}x gevonden (verwacht {n}): {anker[:80]}"); sys.exit(1)
    src = src.replace(anker, nieuw)

ZINNEN = ''' {"id": "s273", "lvl": 2, "nl": "Als je me je fiets leent, geef ik hem je zondag terug.", "en": "If you lend me your bike, I'll give it back to you on Sunday.", "es": "Si me prestas tu bici, te la devuelvo el domingo.", "alt": ["si me prestas tu bici te la devuelvo el domingo", "si me prestas tu bicicleta, te la devuelvo el domingo"], "uitleg": "Devolver = teruggeven, je meest gemiste kaartje deze week (negen keer erbij). Nieuwe invalshoek: het is de vaste partner van prestar (lenen aan) — me prestas, te devuelvo. In het presente is het een o→ue-schoenwerkwoord: devuelvo, devuelves. En te la: eerst de persoon (te), dan het ding (la, want la bici).", "ue": "Devolver = to give back, your most-missed card this week (nine more). New angle: it is the fixed partner of prestar (to lend) — me prestas, te devuelvo. In the present it is an o→ue boot verb: devuelvo, devuelves. And te la: person first (te), then the thing (la, for la bici).", "tag": "les5"},
 {"id": "s274", "lvl": 2, "nl": "Eindelijk heb ik de verloren sleutels gevonden.", "en": "I have finally found the lost keys.", "es": "Por fin he encontrado las llaves perdidas.", "alt": ["por fin he encontrado las llaves perdidas", "he encontrado por fin las llaves perdidas"], "uitleg": "Encontrado = participio van encontrar, vier verse missers als kaartje. In het presente wisselt de stam (encuentro), maar het participio is gewoon regelmatig: encontrado. En zie het verschil met perdido: na haber verandert het participio nooit (he perdido las llaves), maar als bijvoeglijk naamwoord buigt het mee — las llaves perdidas.", "ue": "Encontrado = participle of encontrar, four fresh misses as a card. The stem changes in the present (encuentro), but the participle is simply regular: encontrado. And note the contrast with perdido: after haber the participle never changes (he perdido las llaves), but as an adjective it agrees — las llaves perdidas.", "tag": "relatar"},
 {"id": "s275", "lvl": 2, "nl": "In de winter trek ik mijn jas aan om niet ziek te worden.", "en": "In winter I put on my coat so I don't get sick.", "es": "En invierno me pongo el abrigo para no ponerme enfermo.", "alt": ["en invierno me pongo el abrigo para no ponerme enfermo", "me pongo el abrigo en invierno para no ponerme enfermo"], "uitleg": "Ponerse is twee werkwoorden in één, en allebei zitten ze in deze zin: me pongo el abrigo = ik trek mijn jas aan (kleding), en ponerse enfermo = ziek wórden (een verandering: ponerse nervioso, ponerse rojo). Let op el abrigo, niet mi — bij kleding met een reflexief werkwoord gebruikt het Spaans het lidwoord, net als bij me duele el oído.", "ue": "Ponerse is two verbs in one, and both are in this sentence: me pongo el abrigo = I put on my coat (clothing), and ponerse enfermo = to get sick (a change: ponerse nervioso, ponerse rojo). Note el abrigo, not mi — with clothing and a reflexive verb Spanish uses the article, just like me duele el oído.", "tag": "salud"},
'''

# 1. Zinnen invoegen aan het einde van SENTENCES (na s272).
rep('"tag": "salud"},\n];\n\nvar QUIZZES = [',
    '"tag": "salud"},\n' + ZINNEN + '];\n\nvar QUIZZES = [')

# 2. EXTRA_CONTENT-koppelingen.
rep('''    "s237",
    "s241",
    "s246"
   ],''', '''    "s237",
    "s241",
    "s246",
    "s273"
   ],''')                      # a2-5 <- s273 (devolver/prestar, favors)
rep('''    "s265",
    "s269"
   ],''', '''    "s265",
    "s269",
    "s274"
   ],''')                      # a2-10 <- s274 (encontrado, perfecto/relatar)
rep('''    "s266",
    "s272"
   ],''', '''    "s266",
    "s272",
    "s275"
   ],''')                      # a2-8 <- s275 (ponerse, salud)

# 3. Kaart-regime perdido/pasó: tweede groei na drill (herchecklijst 28 aug):
#    meer-veld op de kaart, zelfde escalatie als sacar/lleno in v23.199.
rep('{id:"cv247", es:"perdido", nl:"verloren, verdwaald (van perder)", tag:"cerv-bestaan", sl:"perdido"}',
    '{id:"cv247", es:"perdido", nl:"verloren, verdwaald (van perder)", tag:"cerv-bestaan", sl:"perdido", meer:"na haber onveranderlijk: he perdido; met estar buigt het mee: estamos perdidos"}')
rep('{id:"cv224", es:"pasó", nl:"het gebeurde (van pasar)", tag:"cerv-reizen", sl:"paso"}',
    '{id:"cv224", es:"pasó", nl:"het gebeurde (van pasar)", tag:"cerv-reizen", sl:"paso", meer:"¿qué pasó? = wat is er gebeurd? — indefinido van pasar; zonder accent is paso ik passeer / de stap"}')

# 4. Devolver: derde invalshoek ook op de kaart (meer-veld aangescherpt).
rep('{id:"cv197", es:"devolver", nl:"teruggeven", tag:"cerv-winkelen", sl:"devolver", meer:"familie van volver (terugkeren): devolver = terug laten gaan"}',
    '{id:"cv197", es:"devolver", nl:"teruggeven", tag:"cerv-winkelen", sl:"devolver", meer:"familie van volver: devolver = terug laten gaan; partner van prestar — me prestas, te lo devuelvo (o→ue: devuelvo)"}')

# 5. Liedverzoek 28 aug 10:21: ARIA VEGA, Ryan Castro - CHÉVERE (yt uit het verzoek).
SONG = ''',
 {id:"song-chevere", titel:"CHÉVERE", artiest:"ARIA VEGA & Ryan Castro", yt:"IAMBPsFPK0I", lvl:"A2",
  intro:"Reggaeton uit Colombia: Ryan Castro komt uit Medellín. De titel ken je al van Chispa's straattaal: chévere = top, gaaf — hét Latijns-Amerikaanse woord voor wat in Spanje guay is. De oogst hieronder is de Colombiaanse feest-woordenschat die bij dit nummer hoort.",
  oogst:[
   {es:"chévere", nl:"top, gaaf, cool", u:"De titel. In heel Latijns-Amerika te horen (vooral Colombia en Venezuela); de Spaanse tegenhanger is guay. Uit Chispa's straattaal-collectie!"},
   {es:"pasarlo chévere", nl:"het naar je zin hebben", u:"Variant van pasarlo bien. En let op het werkwoord: ¿qué tal lo pasaste? — pasar ken je ook van ¿qué pasó? = wat is er gebeurd?"},
   {es:"la rumba", nl:"het feest", u:"Colombiaans voor fiesta. Irse de rumba = gaan stappen. Het woord gaf zijn naam aan het muziekgenre."},
   {es:"el ambiente", nl:"de sfeer", u:"Hay buen ambiente = er hangt een goede sfeer. Stond deze week nog in je foutenlog — hier komt hij terug in feestcontext."},
   {es:"bailar contigo", nl:"met jou dansen", u:"Niet con ti maar één woord: contigo. Net als conmigo = met mij. Vaste reggaeton-woorden."},
   {es:"el parcero / parce", nl:"vriend, maat (Colombia)", u:"Hét Medellín-woord, Ryan Castro's thuisstad. Zoals España tío zegt en México güey."},
   {es:"gozar", nl:"genieten, losgaan", u:"Gozar (de) = genieten van, het feest-synoniem van disfrutar de — mét hetzelfde vaste de erachter."}
  ],
  vragen:[
   {q:"Chévere hoor je vooral in Latijns-Amerika. Wat zeggen ze in Spanje?", qe:"Chévere is mostly Latin American. What do they say in Spain?", optse:["guay","talla"], ue:"Guay is the Spanish counterpart of chévere. La talla is a clothing size — nothing to do with it.", opts:["guay","talla"], c:0, u:"Guay is de Spaanse tegenhanger van chévere. La talla is een kledingmaat — heeft er niets mee te maken."},
   {q:"'Bailar contigo' = met jou dansen. Waarom niet 'con ti'?", qe:"'Bailar contigo' = to dance with you. Why not 'con ti'?", optse:["mí and ti merge with con: conmigo, contigo","con always takes tú"], ue:"After con, mí and ti become one word: conmigo, contigo. All other pronouns stay separate: con él, con nosotros.", opts:["mí en ti versmelten met con: conmigo, contigo","na con komt altijd tú"], c:0, u:"Na con versmelten mí en ti tot één woord: conmigo, contigo. Alle andere voornaamwoorden blijven los: con él, con nosotros."},
   {q:"'¿Qué tal lo pasaste?' — welk werkwoord zit hier in de indefinido?", qe:"'¿Qué tal lo pasaste?' — which verb is in the indefinido here?", optse:["pasar (pasaste, like pasó)","poner (you put)"], ue:"Pasaste is the tú-form of pasar in the indefinido — same family as ¿qué pasó? = what happened? Poner would be pusiste.", opts:["pasar (pasaste, net als pasó)","poner (jij zette)"], c:0, u:"Pasaste is de tú-vorm van pasar in de indefinido — zelfde familie als ¿qué pasó? = wat is er gebeurd? Poner zou pusiste zijn."}
  ]}
];'''
rep("""relatar-toetsje."}
  ]}
];

function ytId(url){""",
"""relatar-toetsje."}
  ]}""" + SONG + """

function ytId(url){""")

# 6. Batch-label en versie.
rep('batch:"batch-26"', 'batch:"batch-27"')
rep('var APP_VERSIE = "v23.199";', 'var APP_VERSIE = "v23.201";')

io.open(PAD, "w", encoding="utf-8").write(src)
io.open("versie.txt", "w", encoding="utf-8").write("v23.201\n")
print("klaar: s273-s275, meer-veld cv247/cv224, cv197 aangescherpt, song-chevere, batch-27, v23.201")
