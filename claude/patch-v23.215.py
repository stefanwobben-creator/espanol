#!/usr/bin/env python3
# Nachtrun 31 aug: twee drillzinnen (s276-s277) op de verse fouten van de
# sessie van 29 aug 14:12-14:50 UTC — de éérste sessie waarin v23.201 echt
# geserveerd was (snapshot 0bdfaa6, logboek-Action van 30 aug 06:54).
# Sencillo (cv415, 0->4 vers) en tirar (cv395, 3->7, +4 — stond al op de
# volglijst van 29 aug met precies deze drempel). Kaart-regime voor deprisa
# (cv371, 10->12) en tamano (cv373, 9->13): tweede groei na de s270-s272-drill,
# conform de herchecklijst van 30 aug, meer-velden naar de suggesties daar.
# Twee liedverzoeken van 29 aug verwerkt: song-fukuoka (Juan Luis Guerra -
# Bachata en Fukuoka, yt DBu6FZr95mk) en song-orion (Boza & Elena Rose -
# Orion, yt Z2pblquztK0), beide yt-id's uit het verzoek zelf.
# Bijvangst: de staart-komma achter s275 in SENTENCES gaat weg — precies de
# komma waar de avondrun volgens het v23.214-doc acht nachten over struikelde
# (de v23.214-fix in tools/curriculum.js staat nog naast main; met een schone
# staart werkt ook de oude invoeger weer).
# Versie springt naar v23.215: v23.214 is geclaimd door het actions-herstel-doc
# van 30 aug (nog niet op main), zelfde afspraak als bij v23.200/v23.201.
# Idempotent: draait alleen als s276 nog niet bestaat.
import io, sys

PAD = "index.html"
src = io.open(PAD, encoding="utf-8").read()

if '"s276"' in src:
    print("al toegepast, niets gedaan"); sys.exit(0)

def rep(anker, nieuw, n=1):
    global src
    k = src.count(anker)
    if k != n:
        print(f"FOUT: anker {k}x gevonden (verwacht {n}): {anker[:80]}"); sys.exit(1)
    src = src.replace(anker, nieuw)

ZINNEN = ''' {"id": "s276", "lvl": 2, "nl": "Dit recept is eenvoudig: je hebt maar drie ingrediënten nodig.", "en": "This recipe is simple: you only need three ingredients.", "es": "Esta receta es sencilla: solo necesitas tres ingredientes.", "alt": ["esta receta es sencilla solo necesitas tres ingredientes", "esta receta es sencilla, solo necesitas tres ingredientes"], "uitleg": "Sencillo = eenvoudig, simpel — vier verse missers als kaartje deze week. Het buigt mee met het zelfstandig naamwoord: una receta sencilla, un plato sencillo. Synoniem van fácil, tegenovergestelde van complicado. En het woord kan meer: un billete sencillo = een enkeltje, una persona sencilla = een bescheiden, gewoon mens.", "ue": "Sencillo = simple, plain — four fresh misses as a card this week. It agrees with the noun: una receta sencilla, un plato sencillo. Synonym of fácil, opposite of complicado. And it does more: un billete sencillo = a one-way ticket, una persona sencilla = a modest, down-to-earth person.", "tag": "cocina"},
 {"id": "s277", "lvl": 2, "nl": "Deze schoenen zijn kapot: ik gooi ze in de vuilnisbak.", "en": "These shoes are broken: I'm throwing them in the bin.", "es": "Estos zapatos están rotos: los tiro a la basura.", "alt": ["estos zapatos están rotos los tiro a la basura", "estos zapatos están rotos, los tiro a la basura", "estos zapatos estan rotos los tiro a la basura"], "uitleg": "Tirar = gooien én weggooien, vier verse missers als kaartje (en je kaartje kent nog een derde betekenis: trekken — tirar de la puerta). Tirar a la basura = in de vuilnisbak gooien. Los tiro: het lijdend voorwerp (los zapatos) schuift als los vóór het werkwoord. En están rotos: estar bij een toestand, met roto als onregelmatig participio van romper.", "ue": "Tirar = to throw and to throw away, four fresh misses as a card (and your card knows a third meaning: to pull — tirar de la puerta). Tirar a la basura = to throw in the bin. Los tiro: the direct object (los zapatos) moves in front of the verb as los. And están rotos: estar for a state, with roto as the irregular participle of romper.", "tag": "les4"}
'''

# 1. Zinnen invoegen aan het einde van SENTENCES (na s275) — en de staart-komma
#    opruimen: de nieuwe laatste regel eindigt zonder komma.
rep('"tag": "salud"},\n];\n\nvar QUIZZES = [',
    '"tag": "salud"},\n' + ZINNEN + '];\n\nvar QUIZZES = [')

# 2. EXTRA_CONTENT-koppelingen.
rep('''    "s262",
    "s271"
   ],''', '''    "s262",
    "s271",
    "s276"
   ],''')                      # a2-7 <- s276 (sencillo, recetas)
rep('''    "s267",
    "s270"
   ],''', '''    "s267",
    "s270",
    "s277"
   ],''')                      # a2-4 <- s277 (tirar, huis/opruimen)

# 3. Kaart-regime deprisa/tamano: tweede groei na de s270-s272-drill
#    (herchecklijst 30 aug), meer-velden conform de suggesties daar.
rep('{id:"cv371", es:"deprisa", nl:"snel, vlug", tag:"cerv-hoeveel", sl:"deprisa"}',
    '{id:"cv371", es:"deprisa", nl:"snel, vlug", tag:"cerv-hoeveel", sl:"deprisa", meer:"bijwoord, één woord: ¡ven deprisa! = kom snel; familie van la prisa — tener prisa = haast hebben"}')
rep('{id:"cv373", es:"tamaño", nl:"grootte, formaat", tag:"cerv-hoeveel", sl:"tamano"}',
    '{id:"cv373", es:"tamaño", nl:"grootte, formaat", tag:"cerv-hoeveel", sl:"tamano", meer:"¿de qué tamaño es? = hoe groot is het? — zelfstandig naamwoord (el tamaño), geen werkwoordsvorm"}')

# 4. Liedverzoeken 29 aug 10:38 en 11:55 (yt-id's uit de verzoeken zelf).
SONGS_NIEUW = ''',
 {id:"song-fukuoka", titel:"Bachata en Fukuoka", artiest:"Juan Luis Guerra", yt:"DBu6FZr95mk", lvl:"A2",
  intro:"Bachata van de Dominicaanse meester Juan Luis Guerra: hij reist naar Japan en leert het publiek in Fukuoka de bachata. De oogst hieronder is de reis- en muziek-woordenschat die bij dit nummer hoort.",
  oogst:[
   {es:"la bachata", nl:"de bachata", u:"Het genre uit de Dominicaanse Republiek — én een oude bekende: La Bachata van Manuel Turizo staat al in je liedjeslijst."},
   {es:"tocar la guitarra", nl:"gitaar spelen", u:"Bij een instrument gebruik je tocar, nooit jugar (dat is voor spelletjes: jugar al fútbol). Tocar is ook gewoon aanraken."},
   {es:"lejos de", nl:"ver van", u:"Fukuoka está muy lejos de la República Dominicana. Vast voorzetsel de erachter, net als cerca de en delante de — die laatste stond deze week nog in je foutenlog."},
   {es:"enseñar", nl:"leren (aan een ander), laten zien", u:"Hij enseña het publiek de bachata. Staat als eigen woord in je lijst en ging deze week nog mis: enseñar = aanleren, aprender = zelf leren."},
   {es:"bailar pegadito", nl:"dicht tegen elkaar dansen", u:"Zó dans je een bachata. Pegado = geplakt (van pegar), en het verkleinwoord -ito maakt het liefkozend: pegadito."},
   {es:"el viaje", nl:"de reis", u:"Van viajar. ¡Buen viaje! = goede reis! Hier een reis van de Caraïben naar Japan."},
   {es:"el mar", nl:"de zee", u:"Tussen die twee ligt een hele oceaan. Meestal el mar, maar dichters en zeelieden zeggen la mar."}
  ],
  vragen:[
   {q:"Gitaar spelen = ___ la guitarra?", qe:"To play the guitar = ___ la guitarra?", opts:["tocar","jugar"], optse:["tocar","jugar"], c:0, u:"Bij instrumenten altijd tocar. Jugar is voor spellen en sport: jugar al fútbol.", ue:"With instruments always tocar. Jugar is for games and sports: jugar al fútbol."},
   {q:"De juf ___ español a los niños.", qe:"The teacher ___ español a los niños.", opts:["enseña","aprende"], optse:["enseña","aprende"], c:0, u:"Enseñar = leren aan een ander (aanleren); aprender = zelf leren. Los niños aprenden, la profesora enseña.", ue:"Enseñar = to teach someone; aprender = to learn yourself. Los niños aprenden, la profesora enseña."},
   {q:"Fukuoka está muy lejos ___ España.", qe:"Fukuoka está muy lejos ___ España.", opts:["de","que"], optse:["de","que"], c:0, u:"Lejos de en cerca de hebben een vast de. Que hoort bij vergelijkingen: más grande que.", ue:"Lejos de and cerca de take a fixed de. Que belongs to comparisons: más grande que."}
  ]},
 {id:"song-orion", titel:"Orión", artiest:"Boza & Elena Rose", yt:"Z2pblquztK0", lvl:"A2",
  intro:"Een melodieuze reggaeton-ballad genoemd naar het sterrenbeeld Orión: Boza komt uit Panama, Elena Rose is Venezolaans. De oogst hieronder is de sterren- en gemis-woordenschat die bij dit nummer hoort.",
  oogst:[
   {es:"la estrella", nl:"de ster", u:"Orión is een sterrenbeeld: una constelación. Ook figuurlijk, net als in het Nederlands: una estrella de la música."},
   {es:"el cielo", nl:"de hemel, de lucht", u:"Mirar al cielo = naar de hemel kijken. En het is ook een koosnaampje: mi cielo."},
   {es:"brillar", nl:"schijnen, stralen", u:"Las estrellas brillan. Regelmatig -ar-werkwoord, ook figuurlijk: hoy brillas = vandaag straal je."},
   {es:"buscarte", nl:"jou zoeken", u:"Het pronomen plakt achteraan de infinitief: buscar + te — zelfde truc als olvidarte uit La Bachata."},
   {es:"extrañar", nl:"missen (Lat-Am)", u:"Te extraño = ik mis je. Boza is Panamees, Elena Rose Venezolaans — in Spanje zeggen ze meestal echar de menos: te echo de menos."},
   {es:"soñar con", nl:"dromen van", u:"Vast voorzetsel con, niet de: sueño contigo = ik droom van jou. En een o→ue-schoenwerkwoord: sueño, sueñas, soñamos."},
   {es:"la noche", nl:"de nacht", u:"Sterren zie je alleen 's nachts: por la noche. Buenas noches werkt bij aankomst én bij vertrek."}
  ],
  vragen:[
   {q:"'Ik droom van jou' = sueño ___", qe:"'I dream about you' = sueño ___", opts:["contigo","de ti"], optse:["contigo","de ti"], c:0, u:"Soñar heeft een vast con, en con + ti versmelt tot contigo — ken je van bailar contigo uit CHÉVERE.", ue:"Soñar takes a fixed con, and con + ti merges into contigo — you know it from bailar contigo in CHÉVERE."},
   {q:"In Spanje zeg je voor 'ik mis je' meestal:", qe:"In Spain, 'I miss you' is usually:", opts:["te echo de menos","te extraño"], optse:["te echo de menos","te extraño"], c:0, u:"Extrañar is vooral Latijns-Amerikaans; de Spaanse variant is echar de menos. Allebei goed Spaans, maar met een andere thuisbasis.", ue:"Extrañar is mostly Latin American; the Spanish variant is echar de menos. Both are good Spanish, with different home turf."},
   {q:"Waarom mag 'buscarte' aan één stuk?", qe:"Why can 'buscarte' be one word?", opts:["achter een infinitief mag het pronomen vastplakken","te staat altijd vóór het werkwoord"], optse:["after an infinitive the pronoun can attach","te always goes before the verb"], c:0, u:"Aan een infinitief (en een gerundio of bevel) mag het pronomen achteraan plakken: buscarte, olvidarte. Bij een vervoegde vorm staat het ervoor: te busco.", ue:"To an infinitive (and a gerund or command) the pronoun can attach at the end: buscarte, olvidarte. With a conjugated form it goes in front: te busco."}
  ]}'''

rep('''Poner zou pusiste zijn."}
  ]}
];

function ytId(url){''',
    '''Poner zou pusiste zijn."}
  ]}''' + SONGS_NIEUW + '''
];

function ytId(url){''')

# 5. Batch-label en versie.
rep('batch:"batch-27"', 'batch:"batch-28"')
rep('var APP_VERSIE = "v23.213";', 'var APP_VERSIE = "v23.215";')

io.open(PAD, "w", encoding="utf-8").write(src)
io.open("versie.txt", "w", encoding="utf-8").write("v23.215\n")
print("patch v23.215 toegepast")
