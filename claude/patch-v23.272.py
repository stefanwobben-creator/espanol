# patch-v23.272.py - de woorden die in je eigen leesboek staan en die de app nooit leerde.
#
# WAT ER GEMETEN IS
#
# tools/leesdekking.js rekent van elke leestekst na hoeveel van de lopende woorden de lezer al kent.
# Hu en Nation (2000): bij 95 procent is een tekst te volgen met hulp, bij 98 lees je hem vlot, en
# onder de 90 is het ontcijferen. Gemeten over de 43 hoofdstukken en de 21 luisterscenes:
#
#     reeks                       voor       na deze patch
#     boek   Chispa              94,8%             97,9%
#     hist   Franco              96,4%             99,2%
#     quij   Don Quijote         91,7%             96,0%
#     vida   Espana por dentro   95,2%             97,8%
#     luisteren                  95,1%             96,8%
#     alles samen                94,5%             97,7%
#
# WAT ERIN ZIT
#
#   97 woordkaarten (L_WORDS). Elk woord komt letterlijk uit BOOK of AUDICIONES en stond in geen
#   enkele woordenbak van de app: niet in WORDS, niet in B_WORDS, niet in K_WORDS, niet in C_WORDS,
#   en ook niet in de FREQ-top-1000, ook niet als regelmatige vervoeging. Het is dus geen bedachte
#   lijst maar de gemeten rekening van wat zijn eigen leesmateriaal van hem vraagt.
#
#   31 werkwoorden (VERBOS). Zonder die helpt een kaart met "mover" niets voor "mueve": de app kent
#   dan de infinitief en niet de vorm. VERBOS gaat van 33 naar 64, en tien van de nieuwe wisselen de
#   klinker. Dat zijn precies de kaarten waar Rompecabezas het van moet hebben.
#
#   reir, sonreir, oir en oler staan er bewust NIET bij: de conjugatieladder leidt zijn zes rijen af
#   uit de vormen zelf en kan die vier niet plaatsen (accentverschuiving, een y erbij, een h ervoor).
#   pw-schoen eist dat elk onregelmatig werkwoord in minstens een rij valt, en terecht: wat de ladder
#   niet kan plaatsen, leert hij ook niet uit. Als woordkaart staan ze er wel.
#
# WAAROM EEN EIGEN BAK EN NIET IN EEN LES
#
# Dezelfde reden als bij K_WORDS (v19.84) en C_WORDS (v23.15): ze horen bij geen enkele les, dus er
# valt niets te ontgrendelen. Ze staan altijd open en de dagportie regelt de volgorde.
#
# WAT DIT NIET IS
#
# Geen vervanging van de leesgenerator. Dit maakt leesbaar wat er al ligt; nieuwe hoofdstukken
# schrijven is de volgende stap, en die kan nu mechanisch nagerekend worden voordat hij binnenkomt.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "var L_WORDS" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


L_WORDS = """/* ================= DE LEESWOORDEN (v23.272) =================

   De woorden die in het leesboek en de luisterscenes van deze app staan en die geen enkele
   woordenbak kende. Gemeten met tools/leesdekking.js, niet bedacht: elk woord hieronder komt uit
   BOOK of AUDICIONES en zat niet in WORDS, B_WORDS, K_WORDS, C_WORDS of de FREQ-top-1000, ook niet
   als regelmatige vervoeging van iets wat daar wel in stond.

   Wat ze doen met de leesbaarheid, over alle 43 hoofdstukken: van 94,5 naar 97,7 procent. Hu en
   Nation (2000): bij 95 procent volg je een tekst met hulp, bij 98 lees je hem vlot.

   Ze hangen aan geen enkele les, net als K_WORDS en C_WORDS, dus er valt niets te ontgrendelen en
   ze staan altijd open. De dagportie regelt de volgorde. */
var L_WORDS = [
 {id:"l1",es:"once",nl:"elf",en:"eleven",tag:"lees-getal"},
 {id:"l2",es:"cuarenta",nl:"veertig",en:"forty",tag:"lees-getal"},
 {id:"l3",es:"ochenta",nl:"tachtig",en:"eighty",tag:"lees-getal"},
 {id:"l4",es:"trescientos",nl:"driehonderd",en:"three hundred",tag:"lees-getal",meer:"vrouwelijk: trescientas"},
 {id:"l5",es:"el millón",nl:"het miljoen",en:"million",tag:"lees-getal",meer:"un millón de personas, met de"},
 {id:"l6",es:"el jueves",nl:"donderdag",en:"Thursday",tag:"lees-tijd"},
 {id:"l7",es:"abril",nl:"april",en:"April",tag:"lees-tijd"},
 {id:"l8",es:"julio",nl:"juli",en:"July",tag:"lees-tijd"},
 {id:"l9",es:"noviembre",nl:"november",en:"November",tag:"lees-tijd"},
 {id:"l10",es:"el mediodía",nl:"het midden van de dag",en:"midday, noon",tag:"lees-tijd"},
 {id:"l11",es:"la siesta",nl:"het middagdutje",en:"afternoon nap",tag:"lees-tijd"},
 {id:"l12",es:"durar",nl:"duren",en:"to last",tag:"lees-tijd"},
 {id:"l13",es:"la sonrisa",nl:"de glimlach",en:"smile",tag:"lees-mens"},
 {id:"l14",es:"sonreír",nl:"glimlachen",en:"to smile",tag:"lees-mens"},
 {id:"l15",es:"la risa",nl:"het gelach",en:"laughter",tag:"lees-mens"},
 {id:"l16",es:"suspirar",nl:"zuchten",en:"to sigh",tag:"lees-mens"},
 {id:"l17",es:"el beso",nl:"de kus",en:"kiss",tag:"lees-mens"},
 {id:"l18",es:"besar",nl:"kussen",en:"to kiss",tag:"lees-mens"},
 {id:"l19",es:"saludar",nl:"groeten",en:"to greet",tag:"lees-mens"},
 {id:"l20",es:"el humor",nl:"de stemming",en:"mood",tag:"lees-mens",meer:"de buen humor is goedgehumeurd"},
 {id:"l21",es:"flaco",nl:"mager",en:"skinny",tag:"lees-mens"},
 {id:"l22",es:"herido",nl:"gewond",en:"wounded",tag:"lees-mens"},
 {id:"l23",es:"incómodo",nl:"ongemakkelijk",en:"uncomfortable",tag:"lees-mens"},
 {id:"l24",es:"la valentía",nl:"de moed",en:"courage",tag:"lees-mens"},
 {id:"l25",es:"la pasión",nl:"de hartstocht",en:"passion",tag:"lees-mens"},
 {id:"l26",es:"acercarse",nl:"dichterbij komen",en:"to come closer",tag:"lees-doen"},
 {id:"l27",es:"esconder",nl:"verstoppen",en:"to hide",tag:"lees-doen"},
 {id:"l28",es:"sentarse",nl:"gaan zitten",en:"to sit down",tag:"lees-doen",meer:"sentado is zittend"},
 {id:"l29",es:"contestar",nl:"antwoord geven",en:"to answer",tag:"lees-doen"},
 {id:"l30",es:"pelear",nl:"vechten",en:"to fight",tag:"lees-doen"},
 {id:"l31",es:"aparecer",nl:"tevoorschijn komen",en:"to appear",tag:"lees-doen"},
 {id:"l32",es:"observar",nl:"aandachtig kijken",en:"to observe",tag:"lees-doen"},
 {id:"l33",es:"oler",nl:"ruiken",en:"to smell",tag:"lees-doen",meer:"huele a mar: het ruikt naar zee"},
 {id:"l34",es:"brillar",nl:"schitteren",en:"to shine",tag:"lees-doen"},
 {id:"l35",es:"explotar",nl:"ontploffen",en:"to explode",tag:"lees-doen"},
 {id:"l36",es:"quemar",nl:"verbranden",en:"to burn",tag:"lees-doen"},
 {id:"l37",es:"prohibir",nl:"verbieden",en:"to forbid",tag:"lees-doen",meer:"prohibido is verboden"},
 {id:"l38",es:"cubrir",nl:"bedekken",en:"to cover",tag:"lees-doen",meer:"cubierto is bedekt"},
 {id:"l39",es:"caber",nl:"erin passen",en:"to fit",tag:"lees-doen",meer:"no cabe: het past er niet in"},
 {id:"l40",es:"debajo de",nl:"onder",en:"under",tag:"lees-plek"},
 {id:"l41",es:"lejano",nl:"ver weg gelegen",en:"distant",tag:"lees-plek"},
 {id:"l42",es:"la roca",nl:"de rots",en:"rock",tag:"lees-natuur"},
 {id:"l43",es:"el monte",nl:"de berg",en:"mountain, hill",tag:"lees-natuur"},
 {id:"l44",es:"la mina",nl:"de mijn",en:"mine",tag:"lees-natuur"},
 {id:"l45",es:"el búho",nl:"de uil",en:"owl",tag:"lees-natuur"},
 {id:"l46",es:"el zorro",nl:"de vos",en:"fox",tag:"lees-natuur"},
 {id:"l47",es:"la vaca",nl:"de koe",en:"cow",tag:"lees-natuur"},
 {id:"l48",es:"redondo",nl:"rond",en:"round",tag:"lees-vorm"},
 {id:"l49",es:"torcido",nl:"scheef",en:"crooked",tag:"lees-vorm"},
 {id:"l50",es:"fino",nl:"dun",en:"thin, fine",tag:"lees-vorm"},
 {id:"l51",es:"transparente",nl:"doorzichtig",en:"transparent",tag:"lees-vorm"},
 {id:"l52",es:"entero",nl:"heel, compleet",en:"whole",tag:"lees-vorm"},
 {id:"l53",es:"completo",nl:"volledig",en:"complete",tag:"lees-vorm"},
 {id:"l54",es:"distinto",nl:"anders, verschillend",en:"different",tag:"lees-vorm"},
 {id:"l55",es:"el metal",nl:"het metaal",en:"metal",tag:"lees-vorm"},
 {id:"l56",es:"la figura",nl:"de gestalte",en:"figure, shape",tag:"lees-vorm"},
 {id:"l57",es:"el trozo",nl:"het stuk",en:"piece",tag:"lees-vorm"},
 {id:"l58",es:"lentamente",nl:"langzaam",en:"slowly",tag:"lees-vorm"},
 {id:"l59",es:"la melodía",nl:"de wijs",en:"melody",tag:"lees-muziek"},
 {id:"l60",es:"tararear",nl:"neuriën",en:"to hum",tag:"lees-muziek"},
 {id:"l61",es:"silencioso",nl:"stil",en:"silent",tag:"lees-muziek"},
 {id:"l62",es:"el mago",nl:"de tovenaar",en:"wizard",tag:"lees-verhaal"},
 {id:"l63",es:"el monstruo",nl:"het monster",en:"monster",tag:"lees-verhaal"},
 {id:"l64",es:"el reino",nl:"het koninkrijk",en:"kingdom",tag:"lees-verhaal"},
 {id:"l65",es:"la armadura",nl:"het harnas",en:"armour",tag:"lees-verhaal"},
 {id:"l66",es:"el casco",nl:"de helm",en:"helmet",tag:"lees-verhaal"},
 {id:"l67",es:"el yelmo",nl:"de ridderhelm",en:"knight's helmet",tag:"lees-verhaal",meer:"ouderwets woord, uit Don Quijote"},
 {id:"l68",es:"el escudero",nl:"de schildknaap",en:"squire",tag:"lees-verhaal"},
 {id:"l69",es:"la bacía",nl:"de scheerbekken",en:"barber's basin",tag:"lees-verhaal",meer:"het bekken dat Don Quijote voor een helm aanziet"},
 {id:"l70",es:"el barbero",nl:"de kapper",en:"barber",tag:"lees-verhaal"},
 {id:"l71",es:"el ventero",nl:"de herbergier",en:"innkeeper",tag:"lees-verhaal"},
 {id:"l72",es:"el aspa",nl:"de wiek",en:"sail of a windmill",tag:"lees-verhaal",meer:"las aspas, van een molen"},
 {id:"l73",es:"el guardia",nl:"de bewaker",en:"guard",tag:"lees-verhaal"},
 {id:"l74",es:"el preso",nl:"de gevangene",en:"prisoner",tag:"lees-verhaal"},
 {id:"l75",es:"el vencedor",nl:"de overwinnaar",en:"winner",tag:"lees-verhaal"},
 {id:"l76",es:"la reverencia",nl:"de buiging",en:"bow",tag:"lees-verhaal"},
 {id:"l77",es:"el motivo",nl:"de reden",en:"reason",tag:"lees-verhaal"},
 {id:"l78",es:"la lengua",nl:"de taal",en:"language",tag:"lees-spanje",meer:"ook de tong"},
 {id:"l79",es:"el castellano",nl:"het Spaans uit Castilië",en:"Castilian Spanish",tag:"lees-spanje"},
 {id:"l80",es:"el gallego",nl:"de taal van Galicië",en:"Galician",tag:"lees-spanje"},
 {id:"l81",es:"el catalán",nl:"de taal van Catalonië",en:"Catalan",tag:"lees-spanje"},
 {id:"l82",es:"el euskera",nl:"de taal van Baskenland",en:"Basque",tag:"lees-spanje"},
 {id:"l83",es:"la región",nl:"de streek",en:"region",tag:"lees-spanje"},
 {id:"l84",es:"la sobremesa",nl:"het napraten aan tafel",en:"after-dinner talk",tag:"lees-spanje"},
 {id:"l85",es:"el obrero",nl:"de arbeider",en:"worker",tag:"lees-spanje"},
 {id:"l86",es:"bombardear",nl:"bombarderen",en:"to bomb",tag:"lees-spanje"},
 {id:"l87",es:"la cartilla",nl:"het bonnenboekje",en:"ration book",tag:"lees-spanje",meer:"la cartilla de racionamiento, uit de jaren veertig"},
 {id:"l88",es:"el racionamiento",nl:"de distributie op bonnen",en:"rationing",tag:"lees-spanje"},
 {id:"l89",es:"gobernar",nl:"regeren",en:"to govern",tag:"lees-spanje"},
 {id:"l90",es:"el gobernador",nl:"de bestuurder van een gebied",en:"governor",tag:"lees-spanje"},
 {id:"l91",es:"votar",nl:"stemmen",en:"to vote",tag:"lees-spanje"},
 {id:"l92",es:"el pacto",nl:"het akkoord",en:"pact",tag:"lees-spanje"},
 {id:"l93",es:"el bikini",nl:"het tweedelig badpak",en:"bikini",tag:"lees-spanje"},
 {id:"l94",es:"el maletero",nl:"de kofferbak",en:"car boot",tag:"lees-spanje"},
 {id:"l95",es:"la casilla",nl:"het hokje",en:"box on a form",tag:"lees-spanje"},
 {id:"l96",es:"bienvenido",nl:"welkom",en:"welcome",tag:"lees-spanje"},
 {id:"l97",es:"perdone",nl:"neemt u mij niet kwalijk",en:"excuse me",tag:"lees-spanje",meer:"beleefde vorm van perdonar"}
];

"""

rep("var C_WORDS = [", L_WORDS + "var C_WORDS = [")

L_VERBOS = """
/* ================= DE WERKWOORDEN UIT HET LEESBOEK (v23.272) =================

   Een woordkaart met "mover" helpt niet voor "mueve": dan kent de app de infinitief en niet de
   vorm. VERBOS draagt per werkwoord de volledige presente, en dat is ook wat Rompecabezas als
   scheidsrechter gebruikt. Met deze lijst gaat VERBOS van 33 naar 64 werkwoorden, en tien van de
   nieuwe wisselen de klinker (mover, perder, entender, seguir, elegir, repetir, sentar, gobernar,
   asentir, rendir). Dat zijn juist de interessante kaarten in dat spel.

   Reflexieve werkwoorden staan hier als kale vorm (sentar en niet sentarse): de vorm in de tekst
   is "se sienta", en het werkwoordsdeel daarvan is sienta. */
var L_VERBOS = [
 {inf:"suspirar",nl:"zuchten",en:"to sigh",presente:["suspiro", "suspiras", "suspira", "suspiramos", "suspiráis", "suspiran"]},
 {inf:"asentir",nl:"ja knikken",en:"to nod",presente:["asiento", "asientes", "asiente", "asentimos", "asentís", "asienten"]},
 {inf:"besar",nl:"kussen",en:"to kiss",presente:["beso", "besas", "besa", "besamos", "besáis", "besan"]},
 {inf:"saludar",nl:"groeten",en:"to greet",presente:["saludo", "saludas", "saluda", "saludamos", "saludáis", "saludan"]},
 {inf:"enfadar",nl:"boos maken",en:"to anger",presente:["enfado", "enfadas", "enfada", "enfadamos", "enfadáis", "enfadan"]},
 {inf:"mover",nl:"verplaatsen",en:"to move",presente:["muevo", "mueves", "mueve", "movemos", "movéis", "mueven"]},
 {inf:"acercar",nl:"dichterbij brengen",en:"to bring closer",presente:["acerco", "acercas", "acerca", "acercamos", "acercáis", "acercan"]},
 {inf:"esconder",nl:"verstoppen",en:"to hide",presente:["escondo", "escondes", "esconde", "escondemos", "escondéis", "esconden"]},
 {inf:"sentar",nl:"neerzetten",en:"to seat",presente:["siento", "sientas", "sienta", "sentamos", "sentáis", "sientan"]},
 {inf:"repetir",nl:"herhalen",en:"to repeat",presente:["repito", "repites", "repite", "repetimos", "repetís", "repiten"]},
 {inf:"contestar",nl:"antwoord geven",en:"to answer",presente:["contesto", "contestas", "contesta", "contestamos", "contestáis", "contestan"]},
 {inf:"elegir",nl:"uitkiezen",en:"to choose",presente:["elijo", "eliges", "elige", "elegimos", "elegís", "eligen"]},
 {inf:"perder",nl:"kwijtraken",en:"to lose",presente:["pierdo", "pierdes", "pierde", "perdemos", "perdéis", "pierden"]},
 {inf:"pelear",nl:"vechten",en:"to fight",presente:["peleo", "peleas", "pelea", "peleamos", "peleáis", "pelean"]},
 {inf:"rendir",nl:"opleveren",en:"to yield",presente:["rindo", "rindes", "rinde", "rendimos", "rendís", "rinden"]},
 {inf:"aparecer",nl:"tevoorschijn komen",en:"to appear",presente:["aparezco", "apareces", "aparece", "aparecemos", "aparecéis", "aparecen"]},
 {inf:"seguir",nl:"doorgaan",en:"to keep going",presente:["sigo", "sigues", "sigue", "seguimos", "seguís", "siguen"]},
 {inf:"observar",nl:"aandachtig kijken",en:"to observe",presente:["observo", "observas", "observa", "observamos", "observáis", "observan"]},
 {inf:"entender",nl:"snappen",en:"to understand",presente:["entiendo", "entiendes", "entiende", "entendemos", "entendéis", "entienden"]},
 {inf:"brillar",nl:"schitteren",en:"to shine",presente:["brillo", "brillas", "brilla", "brillamos", "brilláis", "brillan"]},
 {inf:"explotar",nl:"ontploffen",en:"to explode",presente:["exploto", "explotas", "explota", "explotamos", "explotáis", "explotan"]},
 {inf:"quemar",nl:"verbranden",en:"to burn",presente:["quemo", "quemas", "quema", "quemamos", "quemáis", "queman"]},
 {inf:"prohibir",nl:"verbieden",en:"to forbid",presente:["prohíbo", "prohíbes", "prohíbe", "prohibimos", "prohibís", "prohíben"]},
 {inf:"avisar",nl:"waarschuwen",en:"to warn",presente:["aviso", "avisas", "avisa", "avisamos", "avisáis", "avisan"]},
 {inf:"cubrir",nl:"bedekken",en:"to cover",presente:["cubro", "cubres", "cubre", "cubrimos", "cubrís", "cubren"]},
 {inf:"durar",nl:"duren",en:"to last",presente:["duro", "duras", "dura", "duramos", "duráis", "duran"]},
 {inf:"tararear",nl:"neuriën",en:"to hum",presente:["tarareo", "tarareas", "tararea", "tarareamos", "tarareáis", "tararean"]},
 {inf:"bombardear",nl:"bombarderen",en:"to bomb",presente:["bombardeo", "bombardeas", "bombardea", "bombardeamos", "bombardeáis", "bombardean"]},
 {inf:"gobernar",nl:"regeren",en:"to govern",presente:["gobierno", "gobiernas", "gobierna", "gobernamos", "gobernáis", "gobiernan"]},
 {inf:"votar",nl:"stemmen",en:"to vote",presente:["voto", "votas", "vota", "votamos", "votáis", "votan"]},
 {inf:"caber",nl:"erin passen",en:"to fit",presente:["quepo", "cabes", "cabe", "cabemos", "cabéis", "caben"]}
];
VERBOS = VERBOS.concat(L_VERBOS);

"""

rep("var VERBOS_PASADO = {", L_VERBOS + "var VERBOS_PASADO = {")

# ---- de nieuwe bak meehangen waar de andere bakken ook hangen ----
rep("    WORDS = TRACKS.a2.words.concat(B_WORDS).concat(K_WORDS).concat(C_WORDS);",
    "    WORDS = TRACKS.a2.words.concat(B_WORDS).concat(K_WORDS).concat(C_WORDS).concat(L_WORDS);")
rep("    WORDS = tr.words.concat(B_WORDS).concat(K_WORDS).concat(C_WORDS);",
    "    WORDS = tr.words.concat(B_WORDS).concat(K_WORDS).concat(C_WORDS).concat(L_WORDS);")
rep("    WORDS = tr.words.concat(K_WORDS).concat(C_WORDS); SENTENCES = tr.sentences; QUIZZES = tr.quizzes;",
    "    WORDS = tr.words.concat(K_WORDS).concat(C_WORDS).concat(L_WORDS); SENTENCES = tr.sentences; QUIZZES = tr.quizzes;")

OUD_ALLOW = "  if(typeof C_WORDS !== \"undefined\") out = out.concat(C_WORDS.map(function(w){ return w.id; }));"
NIEUW_ALLOW = (OUD_ALLOW + "\n" +
    "  /* v23.272: en de leeswoorden, om dezelfde reden als de twee bakken hierboven. Ze hangen aan geen\n" +
    "     les, dus zonder deze regel liggen ze er wel maar komen ze nooit langs. */\n" +
    "  if(typeof L_WORDS !== \"undefined\") out = out.concat(L_WORDS.map(function(w){ return w.id; }));")
rep(OUD_ALLOW, NIEUW_ALLOW)

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
