#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.81: La cocina, deel 1. Zes Spaanse recepten die al vegan zijn, en die je echt kunt koken.

Stefan, 13 aug: "ik zat te denken wellicht ook wat typische spaanse recepten (en dan wel vegan
gemaakt) ... en deze content komt dan terug in woordjes, zinnen, lees en luisteroefeningen." En op
de vraag of het een leestekst is die toevallig over eten gaat: "ook kookbaar."

Dat woord bepaalt de vorm. Een leestekst over gazpacho kun je mooi schrijven zonder ooit een
hoeveelheid te noemen. Een recept dat naast het fornuis moet liggen, kan dat niet: dan wil je 1 kg
tomaten, 50 ml olie, vijftien minuten, en op welk vuur. Elk recept hier heeft dus een kop met
personen en tijd, een ingrediëntenlijst met maten, genummerde stappen, en een truc onderaan.

## Deel 1 is niet "vegan gemaakt", het is gewoon vegan

Stefan koos beide delen. Dit is het eerste: gerechten die in Spanje al eeuwen zonder dier op tafel
staan. Gazpacho, pan con tomate, pisto, patatas bravas, ajoblanco, champiñones al ajillo. Geen
vervangers, geen uitleg, geen excuus. Deel 2 (tortilla zonder ei, paella de verduras) is het
verhaal van het veranderen; dit deel is het verhaal van wat er al was.

Twee dingen zijn met opzet gecontroleerd op echtheid: de bravasaus zonder chorizo of vlees is de
gewone Madrileense saus op meel en pimentón, en de ajoblanco is een amandelsoep die ouder is dan
gazpacho. Er is dus niets geveganiseerd.

## Waarom dit als leesreeks en niet als nieuw scherm

LEES_REEKSEN is al een register op id-voorvoegsel: Chispa is boek-, Franco is hist-. Een derde
reeks toevoegen kost één regel daar plus hoofdstukken met id receta-N. Wat je gratis meekrijgt is
precies wat een recept nodig heeft: tik op een woord voor de vertaling (leesTekstHtml), voorlezen,
begripsvragen die meetellen, en de plank die laat zien wat je al hebt gelezen.

En de grammatica komt er bovenop zonder dat iemand er les over hoeft te geven: een recept is de
imperativo in het wild. Corta, añade, deja reposar, no los laves. Zesendertig gebiedende wijzen in
zes teksten, allemaal in een context waar ze vanzelf logisch zijn.

## Eén verandering aan de weergave

renderBoekLectura() splitste de tekst op lege regels en gooide enkele regelovergangen weg. Dat kon,
want geen van de drieëntwintig bestaande hoofdstukken gebruikt er een: geteld, nul. Een
ingrediëntenlijst heeft ze wel nodig, anders wordt "1 kg de tomates 1 pepino 1 pimiento verde" één
doorlopende zin. Enkele regelovergangen worden nu <br>. Voor de bestaande hoofdstukken verandert er
dus niets, en dat is nagemeten en niet aangenomen.

## Woordenschat

Zesendertig woorden in K_WORDS, zes per recept, getagd receta-N. K_WORDS zit in beide sporen (zie
de twee regels met `WORDS = tr.words.concat(...)`), dus één set ids bedient A0 en A2. boekWoorden()
koppelt ze aan het hoofdstuk via de tag; dat mechanisme lag er al voor het Chispa-boek.

## Audio

Nog niet. Recepten groeien niet vanzelf, dus ze horen niet in de nachtelijke audiostap; dit is
handwerk met tools/generate-boek-audio.js, net als het boek. Tot die tijd valt het voorlezen terug
op de browserstem, en dat is sinds v23.76 ook echt zo in plaats van stilte.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.81"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.81" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_KWOORD = '''  {id:"k244", es:"creer", nl:"geloven, denken", tag:"kern-bestaan", ej:"Creo que tienes raz\u00f3n.", ejnl:"Ik denk dat je gelijk hebt."}
];'''

A_BOEK = '''  reflectie:"\u00bfEs mejor olvidar para vivir juntos, o hablar aunque duela?"}
];'''

A_REEKS = ''' {id:"franco", pre:"hist-", nl:"Espa\u00f1a: los a\u00f1os de Franco", en:"Espa\u00f1a: los a\u00f1os de Franco",'''

A_PARAS = '''  var paras = h.tekst.split("\\n\\n").map(function(p){ return "<p>"+leesTekstHtml(p)+"</p>"; }).join("");'''

A_MAP = '''    var map = String(h.id).indexOf("hist-") === 0 ? "hist" : "boek";'''

if DOE_APP:
    ontbreekt = [n for n, a in (("het einde van K_WORDS", A_KWOORD), ("het einde van BOOK", A_BOEK),
                                ("LEES_REEKSEN", A_REEKS), ("renderBoekLectura", A_PARAS),
                                ("de mapkeuze in boekSpreek", A_MAP)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.80. Eerst bijtrekken:\n\n    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


WOORDEN = u''' {id:"k245", es:"la batidora", nl:"de staafmixer, de blender", tag:"receta-1", ej:"Tritura los tomates con la batidora.", ejnl:"Maal de tomaten fijn met de blender."},
 {id:"k246", es:"el pepino", nl:"de komkommer", tag:"receta-1", ej:"Pela el pepino antes de triturarlo.", ejnl:"Schil de komkommer voor je hem fijnmaalt."},
 {id:"k247", es:"el vinagre", nl:"de azijn", tag:"receta-1", ej:"Una cucharada de vinagre es suficiente.", ejnl:"E\u00e9n eetlepel azijn is genoeg."},
 {id:"k248", es:"la nevera", nl:"de koelkast", tag:"receta-1", ej:"El gazpacho tiene que estar en la nevera dos horas.", ejnl:"De gazpacho moet twee uur in de koelkast."},
 {id:"k249", es:"maduro", nl:"rijp", tag:"receta-1", ej:"Busca tomates muy maduros, saben mucho mejor.", ejnl:"Zoek heel rijpe tomaten, die smaken veel beter."},
 {id:"k250", es:"triturar", nl:"fijnmalen, pureren", tag:"receta-1", ej:"Tritura todo dos minutos.", ejnl:"Maal alles twee minuten fijn."},
 {id:"k251", es:"la rebanada", nl:"de snee (brood)", tag:"receta-2", ej:"Necesitas cuatro rebanadas de pan.", ejnl:"Je hebt vier sneetjes brood nodig."},
 {id:"k252", es:"tostar", nl:"roosteren", tag:"receta-2", ej:"Tuesta el pan hasta que est\u00e9 dorado.", ejnl:"Rooster het brood tot het goudbruin is."},
 {id:"k253", es:"frotar", nl:"wrijven", tag:"receta-2", ej:"Frota el ajo sobre el pan caliente.", ejnl:"Wrijf de knoflook over het warme brood."},
 {id:"k254", es:"el chorro", nl:"de scheut", tag:"receta-2", ej:"Echa un chorro de aceite por encima.", ejnl:"Giet er een scheut olie overheen."},
 {id:"k255", es:"la pizca", nl:"het snufje", tag:"receta-2", ej:"Una pizca de sal y ya est\u00e1.", ejnl:"Een snufje zout en klaar."},
 {id:"k256", es:"crujiente", nl:"knapperig", tag:"receta-2", ej:"El pan tiene que quedar crujiente.", ejnl:"Het brood moet knapperig blijven."},
 {id:"k257", es:"la sart\u00e9n", nl:"de koekenpan", tag:"receta-3", ej:"Calienta el aceite en una sart\u00e9n grande.", ejnl:"Verhit de olie in een grote koekenpan."},
 {id:"k258", es:"sofre\u00edr", nl:"aanfruiten", tag:"receta-3", ej:"Sofr\u00ede la cebolla cinco minutos.", ejnl:"Fruit de ui vijf minuten aan."},
 {id:"k259", es:"el calabac\u00edn", nl:"de courgette", tag:"receta-3", ej:"Corta el calabac\u00edn en dados.", ejnl:"Snijd de courgette in blokjes."},
 {id:"k260", es:"la berenjena", nl:"de aubergine", tag:"receta-3", ej:"La berenjena tarda un poco m\u00e1s.", ejnl:"De aubergine doet er iets langer over."},
 {id:"k261", es:"a fuego lento", nl:"op laag vuur", tag:"receta-3", ej:"Deja el pisto a fuego lento quince minutos.", ejnl:"Laat de pisto vijftien minuten op laag vuur staan."},
 {id:"k262", es:"espesar", nl:"indikken", tag:"receta-3", ej:"Espera hasta que la salsa espese.", ejnl:"Wacht tot de saus indikt."},
 {id:"k263", es:"la patata", nl:"de aardappel", tag:"receta-4", ej:"Pela un kilo de patatas.", ejnl:"Schil een kilo aardappels."},
 {id:"k264", es:"fre\u00edr", nl:"bakken, frituren", tag:"receta-4", ej:"Fr\u00ede las patatas dos veces.", ejnl:"Bak de aardappels twee keer."},
 {id:"k265", es:"el piment\u00f3n", nl:"het paprikapoeder", tag:"receta-4", ej:"El piment\u00f3n se quema muy r\u00e1pido.", ejnl:"Paprikapoeder verbrandt heel snel."},
 {id:"k266", es:"la harina", nl:"de bloem", tag:"receta-4", ej:"A\u00f1ade una cucharada de harina.", ejnl:"Voeg een eetlepel bloem toe."},
 {id:"k267", es:"el caldo", nl:"de bouillon", tag:"receta-4", ej:"Usa caldo de verduras, no de carne.", ejnl:"Gebruik groentebouillon, geen vleesbouillon."},
 {id:"k268", es:"amargar", nl:"bitter maken, bitter worden", tag:"receta-4", ej:"Si se quema, amarga toda la salsa.", ejnl:"Als het verbrandt, wordt de hele saus bitter."},
 {id:"k269", es:"la almendra", nl:"de amandel", tag:"receta-5", ej:"El ajoblanco es una sopa de almendra.", ejnl:"Ajoblanco is een amandelsoep."},
 {id:"k270", es:"la corteza", nl:"de korst", tag:"receta-5", ej:"Quita la corteza del pan.", ejnl:"Haal de korst van het brood."},
 {id:"k271", es:"escurrir", nl:"uitlekken, uitknijpen", tag:"receta-5", ej:"Escurre el pan con la mano.", ejnl:"Knijp het brood uit met je hand."},
 {id:"k272", es:"en hilo", nl:"in een dun straaltje", tag:"receta-5", ej:"A\u00f1ade el aceite en hilo, poco a poco.", ejnl:"Voeg de olie in een dun straaltje toe, beetje bij beetje."},
 {id:"k273", es:"la uva", nl:"de druif", tag:"receta-5", ej:"S\u00edrvelo con unas uvas fr\u00edas.", ejnl:"Serveer het met een paar koude druiven."},
 {id:"k274", es:"reposar", nl:"rusten (van een gerecht)", tag:"receta-5", ej:"Deja reposar la masa media hora.", ejnl:"Laat het deeg een half uur rusten."},
 {id:"k275", es:"el champi\u00f1\u00f3n", nl:"de champignon", tag:"receta-6", ej:"Limpia los champi\u00f1ones con un papel.", ejnl:"Maak de champignons schoon met een doekje."},
 {id:"k276", es:"el diente de ajo", nl:"het teentje knoflook", tag:"receta-6", ej:"Corta tres dientes de ajo en l\u00e1minas.", ejnl:"Snijd drie teentjes knoflook in plakjes."},
 {id:"k277", es:"la guindilla", nl:"het pepertje", tag:"receta-6", ej:"Una guindilla peque\u00f1a es bastante.", ejnl:"E\u00e9n klein pepertje is genoeg."},
 {id:"k278", es:"el perejil", nl:"de peterselie", tag:"receta-6", ej:"Echa perejil picado por encima.", ejnl:"Strooi er gehakte peterselie overheen."},
 {id:"k279", es:"la l\u00e1mina", nl:"het plakje", tag:"receta-6", ej:"Corta los champi\u00f1ones en l\u00e1minas gruesas.", ejnl:"Snijd de champignons in dikke plakjes."},
 {id:"k280", es:"dorar", nl:"bruin bakken", tag:"receta-6", ej:"Dora los ajos treinta segundos.", ejnl:"Bak de knoflook dertig seconden bruin."}
];'''

RECEPTEN = u'''  reflectie:"\u00bfEs mejor olvidar para vivir juntos, o hablar aunque duela?"},

 /* ================= LA COCINA, deel 1: lo que ya era vegano =================
    Stefan, 13 aug: "typische spaanse recepten (en dan wel vegan gemaakt)", en op de vraag of het
    ook echt kookbaar moet zijn: "ook kookbaar." Vandaar de hoeveelheden, de tijden en het vuur.
    Deze zes zijn niet veganiseerd: ze stonden al zo op tafel. Deel 2 (tortilla zonder ei, paella
    de verduras) is een ander verhaal en komt apart. */
 {id:"receta-1", num:1, deel:"La cocina espa\u00f1ola", titel:"Gazpacho andaluz", drempel:0,
  tekst:"Para 4 personas \u00b7 15 minutos \u00b7 sin fuego\\n\\n"+
   "INGREDIENTES\\n1 kg de tomates muy maduros\\n1 pepino peque\u00f1o\\n1 pimiento verde\\n1 diente de ajo\\n50 ml de aceite de oliva virgen extra\\n1 cucharada de vinagre de vino\\n1 cucharadita de sal\\n200 ml de agua muy fr\u00eda\\n\\n"+
   "PREPARACI\u00d3N\\n1. Lava los tomates y c\u00f3rtalos en cuatro. No los peles: la piel se va con la batidora.\\n2. Pela el pepino y qu\u00edtale las semillas al pimiento.\\n3. Pon todo en la batidora con el ajo, la sal y el vinagre. Tritura dos minutos.\\n4. A\u00f1ade el aceite poco a poco, sin parar de batir. As\u00ed el gazpacho queda cremoso.\\n5. Pasa la mezcla por un colador si la quieres muy fina.\\n6. A\u00f1ade el agua fr\u00eda y prueba. \u00bfFalta sal? \u00bfFalta vinagre? Corrige ahora.\\n7. Deja el gazpacho en la nevera dos horas como m\u00ednimo.\\n\\n"+
   "EL TRUCO\\nEl aceite al final y poco a poco. Si lo echas todo de golpe, el gazpacho se corta y queda aguado.",
  vragen:[
   {q:"\u00bfCu\u00e1nto tiempo tiene que estar en la nevera?", opts:["Dos horas como m\u00ednimo","Diez minutos","No hace falta"], c:0},
   {q:"\u00bfPor qu\u00e9 se a\u00f1ade el aceite poco a poco?", opts:["Para que quede cremoso","Para gastar menos aceite","Para que sea m\u00e1s fr\u00edo"], c:0},
   {q:"\u00bfHay que pelar los tomates?", opts:["No, la piel se va con la batidora","S\u00ed, siempre","Solo los verdes"], c:0}
  ],
  reflectie:"\u00bfQu\u00e9 plato de tu pa\u00eds cambia mucho de una casa a otra, como el gazpacho en Espa\u00f1a?"},

 {id:"receta-2", num:2, deel:"La cocina espa\u00f1ola", titel:"Pan con tomate", drempel:0,
  tekst:"Para 2 personas \u00b7 5 minutos\\n\\n"+
   "INGREDIENTES\\n4 rebanadas de pan r\u00fastico\\n2 tomates maduros\\n1 diente de ajo\\naceite de oliva virgen extra\\nsal\\n\\n"+
   "PREPARACI\u00d3N\\n1. Tuesta el pan hasta que est\u00e9 dorado y crujiente.\\n2. Corta el ajo por la mitad y frota una mitad sobre el pan caliente.\\n3. Corta el tomate por la mitad y fr\u00f3talo tambi\u00e9n, con fuerza, hasta que solo quede la piel en la mano.\\n4. Echa un chorro de aceite y una pizca de sal.\\n5. C\u00f3melo enseguida. El pan con tomate no espera.\\n\\n"+
   "EL TRUCO\\nEl pan tiene que estar caliente cuando frotas el ajo. Fr\u00edo, el ajo resbala y no deja sabor.",
  vragen:[
   {q:"\u00bfQu\u00e9 se frota primero?", opts:["El ajo","El tomate","Los dos a la vez"], c:0},
   {q:"\u00bfPor qu\u00e9 el pan tiene que estar caliente?", opts:["Porque as\u00ed el ajo deja sabor","Porque es m\u00e1s barato","Porque el tomate est\u00e1 fr\u00edo"], c:0},
   {q:"\u00bfQu\u00e9 queda en la mano al final?", opts:["La piel del tomate","Las semillas","Nada"], c:0}
  ],
  reflectie:"\u00bfCu\u00e1l es el plato m\u00e1s simple que sabes hacer, y por qu\u00e9 te gusta?"},

 {id:"receta-3", num:3, deel:"La cocina espa\u00f1ola", titel:"Pisto manchego", drempel:0,
  tekst:"Para 4 personas \u00b7 45 minutos\\n\\n"+
   "INGREDIENTES\\n1 cebolla grande\\n1 pimiento verde\\n1 pimiento rojo\\n1 calabac\u00edn\\n1 berenjena\\n400 g de tomate triturado\\n4 cucharadas de aceite de oliva\\n1 cucharadita de az\u00facar\\nsal\\n\\n"+
   "PREPARACI\u00d3N\\n1. Corta toda la verdura en dados del mismo tama\u00f1o. As\u00ed se hace todo a la vez.\\n2. Calienta el aceite en una sart\u00e9n grande y sofr\u00ede la cebolla cinco minutos, a fuego medio.\\n3. A\u00f1ade los pimientos y d\u00e9jalos diez minutos m\u00e1s.\\n4. Echa el calabac\u00edn y la berenjena. Remueve de vez en cuando, quince minutos.\\n5. A\u00f1ade el tomate triturado, la sal y el az\u00facar. El az\u00facar quita la acidez del tomate.\\n6. Baja el fuego y deja el pisto a fuego lento quince minutos, sin tapar, hasta que espese.\\n\\n"+
   "EL TRUCO\\nSin tapa al final. Con tapa el agua no se va y el pisto queda como una sopa.",
  vragen:[
   {q:"\u00bfPor qu\u00e9 se corta toda la verdura del mismo tama\u00f1o?", opts:["Para que se haga todo a la vez","Para que sea m\u00e1s bonito","Para gastar menos aceite"], c:0},
   {q:"\u00bfPara qu\u00e9 sirve el az\u00facar?", opts:["Para quitar la acidez del tomate","Para que sea un postre","Para que espese antes"], c:0},
   {q:"\u00bfQu\u00e9 pasa si tapas la sart\u00e9n al final?", opts:["Queda como una sopa","Se quema","Sabe a ajo"], c:0}
  ],
  reflectie:"\u00bfPrefieres cocinar r\u00e1pido o dejar algo a fuego lento mientras haces otra cosa?"},

 {id:"receta-4", num:4, deel:"La cocina espa\u00f1ola", titel:"Patatas bravas", drempel:0,
  tekst:"Para 4 personas \u00b7 40 minutos\\n\\n"+
   "INGREDIENTES\\n1 kg de patatas\\naceite de oliva para fre\u00edr\\nsal\\n\\n"+
   "PARA LA SALSA BRAVA\\n2 cucharadas de aceite\\n1 cucharada de harina\\n1 cucharada de piment\u00f3n dulce\\n1 cucharadita de piment\u00f3n picante\\n300 ml de caldo de verduras\\n1 cucharada de vinagre\\n\\n"+
   "PREPARACI\u00d3N\\n1. Pela las patatas y c\u00f3rtalas en trozos grandes e irregulares, no en dados perfectos.\\n2. Fr\u00edelas en aceite no muy caliente quince minutos, hasta que est\u00e9n blandas por dentro.\\n3. S\u00e1calas, sube el fuego y fr\u00edelas otra vez tres minutos. As\u00ed quedan crujientes por fuera.\\n4. Para la salsa, calienta el aceite y a\u00f1ade la harina. Remueve un minuto.\\n5. Aparta la sart\u00e9n del fuego y echa los dos pimentones. Fuera del fuego, o el piment\u00f3n se quema y amarga.\\n6. Vuelve al fuego, a\u00f1ade el caldo poco a poco y el vinagre. Deja que espese cinco minutos.\\n7. Sirve las patatas con la salsa por encima y c\u00f3melas enseguida.\\n\\n"+
   "EL TRUCO\\nFre\u00edr dos veces. Una vez a fuego suave para el interior, otra vez fuerte para la corteza.",
  vragen:[
   {q:"\u00bfCu\u00e1ntas veces se fr\u00eden las patatas?", opts:["Dos veces","Una vez","Tres veces"], c:0},
   {q:"\u00bfPor qu\u00e9 se aparta la sart\u00e9n antes de echar el piment\u00f3n?", opts:["Porque se quema y amarga","Porque salpica","Porque pierde el color"], c:0},
   {q:"\u00bfC\u00f3mo se cortan las patatas?", opts:["En trozos grandes e irregulares","En dados peque\u00f1os","En rodajas finas"], c:0}
  ],
  reflectie:"\u00bfHay algo que en tu casa se coma siempre de pie, como las bravas en un bar?"},

 {id:"receta-5", num:5, deel:"La cocina espa\u00f1ola", titel:"Ajoblanco malague\u00f1o", drempel:0,
  tekst:"Para 4 personas \u00b7 15 minutos \u00b7 sin fuego\\n\\n"+
   "INGREDIENTES\\n150 g de almendras crudas peladas\\n100 g de pan del d\u00eda anterior, sin corteza\\n1 diente de ajo peque\u00f1o\\n750 ml de agua muy fr\u00eda\\n80 ml de aceite de oliva virgen extra\\n2 cucharadas de vinagre de jerez\\nsal\\nuvas o mel\u00f3n para servir\\n\\n"+
   "PREPARACI\u00d3N\\n1. Pon el pan en agua diez minutos y luego esc\u00farrelo con la mano.\\n2. Tritura las almendras con el ajo y un poco de agua, hasta que quede una pasta.\\n3. A\u00f1ade el pan y sigue batiendo. Echa el resto del agua poco a poco.\\n4. A\u00f1ade el aceite en hilo, sin parar la batidora, y despu\u00e9s el vinagre y la sal.\\n5. Prueba. Si el ajo es demasiado fuerte, a\u00f1ade m\u00e1s pan y m\u00e1s agua.\\n6. Deja reposar el ajoblanco dos horas en la nevera. S\u00edrvelo con unas uvas fr\u00edas encima.\\n\\n"+
   "EL TRUCO\\nMedio diente de ajo es suficiente. El ajoblanco es de almendra, no de ajo, aunque el nombre diga otra cosa.",
  vragen:[
   {q:"\u00bfDe qu\u00e9 es el ajoblanco, sobre todo?", opts:["De almendra","De ajo","De pan"], c:0},
   {q:"\u00bfQu\u00e9 se hace si el ajo est\u00e1 demasiado fuerte?", opts:["A\u00f1adir m\u00e1s pan y m\u00e1s agua","A\u00f1adir m\u00e1s ajo","Empezar otra vez"], c:0},
   {q:"\u00bfCon qu\u00e9 se sirve?", opts:["Con uvas o mel\u00f3n","Con pan tostado","Con patatas"], c:0}
  ],
  reflectie:"\u00bfTe sorprende que un plato lleve el nombre de lo que menos tiene dentro?"},

 {id:"receta-6", num:6, deel:"La cocina espa\u00f1ola", titel:"Champi\u00f1ones al ajillo", drempel:0,
  tekst:"Para 2 personas \u00b7 15 minutos\\n\\n"+
   "INGREDIENTES\\n400 g de champi\u00f1ones\\n3 dientes de ajo\\n1 guindilla peque\u00f1a\\n3 cucharadas de aceite de oliva\\n50 ml de vino blanco\\n1 cucharada de perejil picado\\nsal\\n\\n"+
   "PREPARACI\u00d3N\\n1. Limpia los champi\u00f1ones con un papel h\u00famedo. No los laves debajo del grifo: cogen agua y luego no se doran.\\n2. C\u00f3rtalos en l\u00e1minas gruesas.\\n3. Corta los ajos en l\u00e1minas finas y la guindilla en trozos.\\n4. Calienta el aceite y dora los ajos treinta segundos. Que no se pongan marrones.\\n5. Sube el fuego y echa los champi\u00f1ones. No los muevas mucho: d\u00e9jalos dorarse.\\n6. A\u00f1ade el vino y deja que se evapore dos minutos.\\n7. Sal, perejil por encima, y fuera del fuego.\\n\\n"+
   "EL TRUCO\\nFuego fuerte y la sart\u00e9n no muy llena. Con demasiados champi\u00f1ones a la vez sueltan agua y se cuecen en vez de dorarse.",
  vragen:[
   {q:"\u00bfPor qu\u00e9 no se lavan los champi\u00f1ones debajo del grifo?", opts:["Porque cogen agua y no se doran","Porque pierden el color","Porque se rompen"], c:0},
   {q:"\u00bfCu\u00e1nto tiempo se doran los ajos?", opts:["Treinta segundos","Cinco minutos","Diez minutos"], c:0},
   {q:"\u00bfQu\u00e9 pasa con demasiados champi\u00f1ones a la vez?", opts:["Se cuecen en vez de dorarse","Se queman","Saben a vino"], c:0}
  ],
  reflectie:"\u00bfCocinas con la sart\u00e9n llena para ir m\u00e1s r\u00e1pido, o en dos veces para que salga mejor?"}
];'''

if DOE_APP:
    rep(A_KWOORD, A_KWOORD.replace("\n];", ",\n") + WOORDEN)
    rep(A_BOEK, RECEPTEN)

    rep(A_REEKS, ''' {id:"cocina", pre:"receta-", nl:"La cocina espa\u00f1ola", en:"La cocina espa\u00f1ola",
  soortNl:"recepten", soortEn:"recipes",
  omNl:"Zes Spaanse gerechten die al vegan waren, met maten en tijden, zodat je ze naast het fornuis kunt leggen.",
  omEn:"Six Spanish dishes that were already vegan, with quantities and times, so you can cook from them."},
''' + A_REEKS)

    rep(A_PARAS, '''  /* v23.81: enkele regelovergangen worden <br>. Een recept heeft een ingredi\u00ebntenlijst, en zonder
     dit wordt "1 kg de tomates 1 pepino 1 pimiento verde" \u00e9\u00e9n doorlopende zin. Voor de bestaande
     hoofdstukken verandert er niets: geteld over alle drie\u00ebntwintig, nul enkele regelovergangen. */
  var paras = h.tekst.split("\\n\\n").map(function(p){
    return "<p>"+p.split("\\n").map(leesTekstHtml).join("<br>")+"</p>";
  }).join("");''')

    rep(A_MAP, '''    /* v23.81: derde reeks. Elke reeks heeft zijn eigen verteller en dus zijn eigen map; het
       voorvoegsel van het id bepaalt welke. */
    var pre = String(h.id);
    var map = pre.indexOf("hist-") === 0 ? "hist" : pre.indexOf("receta-") === 0 ? "receta" : "boek";''')

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s (zes recepten, 36 woorden)" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
