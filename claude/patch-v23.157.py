#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.157: nieuw boek en nieuwe luisteroefeningen.

Stefan, 21 aug: "Verder ik ben door de boeken (muv recepten) en luisteroefeningen heen. Maak een
nieuw boek voor me en ook luisteroefeningen."

## Waarom dit vóór alle andere punten uit dat bericht komt

Zijn bericht bevatte zeven punten. Dit is het enige dat een blokkade is: het inputblok van de dagles
(v23.140) put uit het boek en uit Escuchar, en allebei zijn ze op. Elke dag dat dat zo blijft, krimpt
zijn les naar vier stappen en verdwijnt de draad waar Nation een kwart van de tijd voor reserveert.
De andere zes punten zijn verbeteringen aan iets dat werkt.

## Het nieuwe boek: "Un año en Cádiz"

Acht hoofdstukken, A2 met een randje B1, in dezelfde vorm als Chispa (tekst, drie vragen, een
reflectievraag). Wat het anders maakt:

**Een volwassen verhaal.** Chispa is een fabel voor een beginner: korte zinnen, dieren, een les per
hoofdstuk. Dit gaat over een Nederlandse die een jaar in Cádiz woont, en het gebruikt de taal die
Stefan echt nodig heeft: een huis zoeken, buren, de markt, je vergissen, een feest, een besluit.

**Verleden tijd als hoofdmoot.** Chispa staat vrijwel volledig in de tegenwoordige tijd. Dit boek
zet indefinido en imperfecto naast elkaar in echte zinnen, en dat is precies het onderwerp waar de
routes (GRAM_PADEN) op dit moment staan. De leesstof en de grammatica wijzen voor het eerst dezelfde
kant op.

**Drempels 8 en 10**, dus na Chispa. Wie nog aan het begin staat krijgt het niet voorgeschoteld.

## Zes nieuwe luisterscenes

Er waren er vijftien, waarvan vier op A2. De nieuwe zes zijn allemaal A2/B1 en gaan over situaties
die de bestaande niet hebben: de dokter over de telefoon, een klacht in een restaurant, een
sollicitatiegesprekje, de buurman over herrie, een misverstand over een afspraak, en het station.

Vorm precies als de bestaande: `lineas` met sprekers a en b, drie vragen met `waarom`, en een
Nederlandse plus Engelse versie van alles.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.157"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = NIEUW not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ================= 1. zes nieuwe luisterscenes =================

rep(
    '''var AUDICIONES = [''',
    '''/* v23.157: zes scenes erbij, allemaal A2 of hoger. Er waren er vijftien en Stefan is erdoorheen,
   en het inputblok van de dagles (v23.140) put hieruit: is de plank leeg, dan krimpt zijn les.
   Deze zes gaan over situaties die de bestaande niet hebben, en ze staan bewust in de verleden tijd
   waar dat natuurlijk is, want dat is waar zijn route nu loopt. */
var AUDICIONES = [
 {id:"e16", nivel:"a2", tema:"telefono", titel:"De dokter aan de telefoon", titelEn:"The doctor on the phone",
  lineas:[
   {v:"a", es:"Centro de salud, buenos días."},
   {v:"b", es:"Hola, buenos días. Quería pedir cita con el médico de cabecera."},
   {v:"a", es:"¿Es urgente o puede esperar?"},
   {v:"b", es:"Puede esperar. Llevo una semana con dolor de espalda, pero no ha empeorado."},
   {v:"a", es:"Entonces le doy hueco el jueves a las once y media. ¿Le viene bien?"},
   {v:"b", es:"El jueves trabajo hasta las doce. ¿Tiene algo por la tarde?"},
   {v:"a", es:"A las seis menos cuarto, con la doctora Ferrer."},
   {v:"b", es:"Perfecto, me lo apunto. Muchas gracias."}
  ],
  vragen:[
   {q:"Waarom krijgt hij geen plek 's ochtends?", qEn:"Why does he not take the morning slot?",
    opts:["Hij werkt tot twaalf uur","De dokter is er niet","Het is te vroeg","Hij woont te ver"],
    optsEn:["He works until twelve","The doctor is away","It is too early","He lives too far"], c:0,
    waarom:"\\"El jueves trabajo hasta las doce\\": hij werkt donderdag tot twaalf, en de afspraak was half twaalf.",
    waaromEn:"\\"El jueves trabajo hasta las doce\\": he works until twelve on Thursday, and the slot was half past eleven."},
   {q:"Hoe laat wordt de afspraak?", qEn:"What time does the appointment end up being?",
    opts:["Kwart voor zes","Half twaalf","Zes uur","Kwart over zes"],
    optsEn:["Quarter to six","Half past eleven","Six o'clock","Quarter past six"], c:0,
    waarom:"\\"A las seis menos cuarto\\" = kwart vóór zes. Menos betekent hier eraf, net als bij rekenen.",
    waaromEn:"\\"A las seis menos cuarto\\" = quarter to six. Menos means minus here, just as in arithmetic."},
   {q:"Waarom is het niet urgent?", qEn:"Why is it not urgent?",
    opts:["De pijn is niet erger geworden","Hij heeft er al medicijnen voor","Het is pas sinds gisteren","Hij heeft geen pijn"],
    optsEn:["The pain has not got worse","He already has medication","It is only one day","He is not in pain"], c:0,
    waarom:"\\"No ha empeorado\\" = het is niet erger geworden. Empeorar komt van peor, slechter.",
    waaromEn:"\\"No ha empeorado\\" = it has not got worse. Empeorar comes from peor, worse."}
  ]},

 {id:"e17", nivel:"a2", tema:"restaurante", titel:"Dit heb ik niet besteld", titelEn:"I did not order this",
  lineas:[
   {v:"a", es:"Perdone, creo que esto no es lo mío. Yo pedí el pescado."},
   {v:"b", es:"Ay, perdón. ¿Usted era la mesa cuatro?"},
   {v:"a", es:"Sí, y mi amiga pidió la ensalada, que tampoco ha llegado."},
   {v:"b", es:"Lo siento muchísimo. Se lo cambio ahora mismo."},
   {v:"a", es:"No pasa nada, pero tenemos un poco de prisa."},
   {v:"b", es:"Le pongo el pescado en cinco minutos y la ensalada va de mi parte."},
   {v:"a", es:"Muy amable, gracias."}
  ],
  vragen:[
   {q:"Wat is er verkeerd gegaan?", qEn:"What went wrong?",
    opts:["Ze kreeg het verkeerde gerecht","Het eten was koud geworden","De rekening klopte niet helemaal","Er was geen tafel vrij"],
    optsEn:["She got the wrong dish","The food was cold","The bill was wrong","There was no table"], c:0,
    waarom:"\\"Esto no es lo mío\\" = dit is niet het mijne. Lo mío is een handige manier om \\"dat van mij\\" te zeggen.",
    waaromEn:"\\"Esto no es lo mío\\" = this is not mine. Lo mío is a handy way to say \\"the one that is mine\\"."},
   {q:"Wat biedt de ober aan?", qEn:"What does the waiter offer?",
    opts:["De salade van het huis","Korting op de rekening","Een gratis toetje","Een andere tafel"],
    optsEn:["The salad on the house","A discount on the bill","A free dessert afterwards","A table by the window"], c:0,
    waarom:"\\"Va de mi parte\\" = van mij, ik trakteer. Letterlijk: het gaat van mijn kant.",
    waaromEn:"\\"Va de mi parte\\" = on me. Literally: it goes from my side."},
   {q:"Waarom moet het snel?", qEn:"Why does it need to be quick?",
    opts:["Ze hebben haast","Het restaurant sluit","Ze zijn boos","De keuken is dicht"],
    optsEn:["They are in a hurry","The restaurant is closing","They are angry","The kitchen is closed"], c:0,
    waarom:"\\"Tener prisa\\" = haast hebben. Let op: hebben, niet zijn, net als tener hambre en tener frío.",
    waaromEn:"\\"Tener prisa\\" = to be in a hurry. Note: Spanish uses have, not be, as with tener hambre."}
  ]},

 {id:"e18", nivel:"a2", tema:"vecinos", titel:"De buurman over de herrie", titelEn:"The neighbour about the noise",
  lineas:[
   {v:"a", es:"Hola, buenas. Soy Manolo, del tercero."},
   {v:"b", es:"Ah, hola. ¿Va todo bien?"},
   {v:"a", es:"Sí, sí. Es solo que anoche se oía la música hasta muy tarde."},
   {v:"b", es:"Uy, lo siento. Tuvimos una cena y se nos fue la hora."},
   {v:"a", es:"No pasa nada, hombre. Pero mi mujer se levanta a las cinco."},
   {v:"b", es:"Entiendo. La próxima vez bajamos el volumen a partir de las once."},
   {v:"a", es:"Perfecto. Y si un día hacéis fiesta, avisad y ya está."}
  ],
  vragen:[
   {q:"Waarom komt de buurman langs?", qEn:"Why does the neighbour come by?",
    opts:["De muziek was gisteravond te laat","Er lekt water","Hij wil kennismaken","Er stond een fiets in de weg"],
    optsEn:["The music went on too late last night","There is a leak in the bathroom","He wants to introduce himself properly","Someone left a bike in the hallway"], c:0,
    waarom:"\\"Anoche\\" = gisteravond. \\"Se oía\\" is imperfecto: het was te horen, een tijdje lang.",
    waaromEn:"\\"Anoche\\" = last night. \\"Se oía\\" is imperfect: it could be heard, over a stretch of time."},
   {q:"Wat is de reden dat het uitkomt?", qEn:"Why does it matter to him?",
    opts:["Zijn vrouw staat om vijf uur op","Hij werkt thuis aan de straatkant","Hij houdt niet van harde muziek","Hij is al een week ziek"],
    optsEn:["His wife gets up at five","He works from home all day","He dislikes loud music","He has been ill for a week"], c:0,
    waarom:"\\"Se levanta a las cinco\\": levantarse is opstaan, wederkerend, want je staat jezelf op.",
    waaromEn:"\\"Se levanta a las cinco\\": levantarse is to get up, reflexive, because you raise yourself."},
   {q:"Wat spreken ze af?", qEn:"What do they agree?",
    opts:["Vanaf elf uur zachter","Nooit meer muziek","Alleen in het weekend","Ze bellen de politie niet"],
    optsEn:["Turn it down from eleven","No more music ever","Only at weekends","They will not call the police"], c:0,
    waarom:"\\"A partir de las once\\" = vanaf elf uur. Een vaste uitdrukking die je overal tegenkomt.",
    waaromEn:"\\"A partir de las once\\" = from eleven onwards. A fixed phrase you meet everywhere."}
  ]},

 {id:"e19", nivel:"a2", tema:"estacion", titel:"De trein die niet ging", titelEn:"The train that did not go",
  lineas:[
   {v:"a", es:"Perdona, ¿sabes si el tren de las diez sale con retraso?"},
   {v:"b", es:"Ese tren lo han cancelado. Lo acaban de decir por megafonía."},
   {v:"a", es:"¿Cancelado? Pero yo tengo que estar en Sevilla a mediodía."},
   {v:"b", es:"Hay otro a las once menos veinte, pero para en todos los pueblos."},
   {v:"a", es:"¿Y a qué hora llegaría?"},
   {v:"b", es:"Sobre la una y media, creo. Yo iría a la taquilla a preguntar."},
   {v:"a", es:"Sí, mejor. Gracias, me has salvado el viaje."}
  ],
  vragen:[
   {q:"Wat is er met de trein van tien uur?", qEn:"What happened to the ten o'clock train?",
    opts:["Hij is geschrapt","Hij heeft vertraging","Hij is al weg","Hij is vol"],
    optsEn:["It has been cancelled","It is delayed","It has already left","It is full"], c:0,
    waarom:"\\"Lo han cancelado\\" = ze hebben hem geschrapt. Cancelado is iets anders dan retraso, vertraging.",
    waaromEn:"\\"Lo han cancelado\\" = they have cancelled it. Cancelado is different from retraso, delay."},
   {q:"Waarom is de andere trein niet ideaal?", qEn:"Why is the other train not ideal?",
    opts:["Hij stopt overal","Hij is duurder","Hij gaat naar een ander station","Hij rijdt morgen"],
    optsEn:["It stops everywhere","It costs more","It goes to another station","It runs tomorrow"], c:0,
    waarom:"\\"Para en todos los pueblos\\": para komt van parar, stoppen, en niet van para, voor.",
    waaromEn:"\\"Para en todos los pueblos\\": para here is from parar, to stop, not the preposition para."},
   {q:"Wat raadt de ander aan?", qEn:"What does the other person suggest?",
    opts:["Naar het loket gaan","Een taxi nemen","Wachten op het perron","Morgen gaan"],
    optsEn:["Go to the ticket office","Take a taxi","Wait on the platform","Go tomorrow"], c:0,
    waarom:"\\"Yo iría a la taquilla\\" is condicional: ik zou gaan. Een beleefde manier om advies te geven.",
    waaromEn:"\\"Yo iría a la taquilla\\" is the conditional: I would go. A polite way of giving advice."}
  ]},

 {id:"e20", nivel:"a2", tema:"trabajo", titel:"Het gesprek", titelEn:"The interview",
  lineas:[
   {v:"a", es:"Cuéntame un poco: ¿qué hacías antes de venir a España?"},
   {v:"b", es:"Trabajaba en una oficina en Ámsterdam, en atención al cliente."},
   {v:"a", es:"¿Y por qué lo dejaste?"},
   {v:"b", es:"Quería aprender el idioma de verdad, no solo en clase."},
   {v:"a", es:"Aquí tendrías que atender al público en español todo el día."},
   {v:"b", es:"Lo sé. Todavía me equivoco, pero me hago entender."},
   {v:"a", es:"Eso es lo que buscamos. Empezamos con un mes de prueba."}
  ],
  vragen:[
   {q:"Wat deed zij hiervoor?", qEn:"What did she do before?",
    opts:["Klantenservice in Amsterdam","Ze studeerde nog","Ze werkte in een restaurant","Ze gaf les"],
    optsEn:["Customer service in Amsterdam","She was still studying","She worked in a restaurant","She taught"], c:0,
    waarom:"\\"Trabajaba\\" is imperfecto: wat ze een tijd lang deed. \\"Trabajé\\" zou één afgeronde periode zijn.",
    waaromEn:"\\"Trabajaba\\" is imperfect: what she used to do. \\"Trabajé\\" would mark one closed period."},
   {q:"Waarom is ze gestopt?", qEn:"Why did she leave?",
    opts:["Ze wilde de taal echt leren","Het salaris was laag","Ze werd ontslagen","Ze verhuisde met haar partner"],
    optsEn:["She wanted to really learn the language","The pay was too low to live on","She was let go last winter","She moved to Spain with her partner"], c:0,
    waarom:"\\"Lo dejaste\\" van dejar: laten, hier in de zin van ermee stoppen. \\"Dejé el trabajo\\" = ik nam ontslag.",
    waaromEn:"\\"Lo dejaste\\" from dejar: to leave, here meaning to quit. \\"Dejé el trabajo\\" = I quit the job."},
   {q:"Wat zegt ze over haar Spaans?", qEn:"What does she say about her Spanish?",
    opts:["Ze maakt fouten maar wordt begrepen","Het is inmiddels vloeiend","Ze durft nog niet vrijuit te praten","Ze leert het nog op school"],
    optsEn:["She makes mistakes but gets understood","It is completely fluent by now","She does not dare to speak freely yet","She is still learning at school"], c:0,
    waarom:"\\"Me hago entender\\" = ik maak me verstaanbaar. Precies de zin die je nodig hebt als je nog fouten maakt.",
    waaromEn:"\\"Me hago entender\\" = I make myself understood. Exactly the phrase you need while still making mistakes."}
  ]},

 {id:"e21", nivel:"a2", tema:"cita", titel:"Een misverstand", titelEn:"A misunderstanding",
  lineas:[
   {v:"a", es:"Oye, ¿dónde estás? Llevo media hora esperando."},
   {v:"b", es:"¿Esperando? Si quedamos mañana, ¿no?"},
   {v:"a", es:"Me dijiste el martes, y hoy es martes."},
   {v:"b", es:"Ay, no. Yo pensaba el martes que viene. Perdona, ha sido culpa mía."},
   {v:"a", es:"Bueno, no pasa nada. Ya que estoy aquí, me tomo un café."},
   {v:"b", es:"Te invito yo la semana que viene, ¿vale? Y esta vez lo apunto."}
  ],
  vragen:[
   {q:"Waar zit het misverstand in?", qEn:"Where is the misunderstanding?",
    opts:["Welke dinsdag ze bedoelden","De plek van de afspraak","Het tijdstip van de afspraak","Wie er nog meer zou komen"],
    optsEn:["Which Tuesday they meant","The place they agreed on","The time they agreed on","Who else would be coming"], c:0,
    waarom:"\\"El martes\\" is deze dinsdag; \\"el martes que viene\\" is dinsdag over een week. Eén woordje verschil.",
    waaromEn:"\\"El martes\\" is this Tuesday; \\"el martes que viene\\" is next Tuesday. One word apart."},
   {q:"Wat zegt hij over de schuld?", qEn:"What does he say about the blame?",
    opts:["Het was zijn fout","Het was haar fout","Niemands fout","Ze weet het niet"],
    optsEn:["It was his fault","It was her fault","Nobody's fault","She does not know"], c:0,
    waarom:"\\"Ha sido culpa mía\\" = het was mijn schuld. Culpa is schuld in de zin van fout, niet van geld.",
    waaromEn:"\\"Ha sido culpa mía\\" = it was my fault. Culpa is fault, not debt."},
   {q:"Wat doet zij nu ze er toch is?", qEn:"What does she do now that she is there?",
    opts:["Koffie drinken","Naar huis gaan","Wachten","Bellen"],
    optsEn:["Have a coffee","Go home","Wait","Make a call"], c:0,
    waarom:"\\"Ya que estoy aquí\\" = nu ik er toch ben. Een verbinder die je in gesprekken vaak hoort.",
    waaromEn:"\\"Ya que estoy aquí\\" = since I am here anyway. A connector you hear a lot in conversation."}
  ]},
''',
)

# ================= 2. het nieuwe boek =================

NIEUW_BOEK = r"""
 /* ================= UN AÑO EN CÁDIZ (v23.157) =================

    Stefan: "ik ben door de boeken (muv recepten) en luisteroefeningen heen. Maak een nieuw boek."

    Chispa is een fabel voor een beginner: dieren, korte zinnen, tegenwoordige tijd, een les per
    hoofdstuk. Dit is het vervolg voor wie daar doorheen is.

    Drie dingen zijn met opzet anders:

    1. Volwassen onderwerpen, en precies de taal die je op reis of bij een verhuizing nodig hebt:
       een huis zoeken, buren, de markt, je vergissen, een feest, een besluit.
    2. Verleden tijd als hoofdmoot. Chispa staat vrijwel volledig in het presente; hier staan
       indefinido en imperfecto naast elkaar in echte zinnen. Dat is precies waar de routes
       (GRAM_PADEN) nu lopen, dus voor het eerst wijzen de leesstof en de grammatica dezelfde kant op.
    3. Drempels 8 en 10, dus ná Chispa. Twaalf zou nooit opengaan: er zijn er elf. Wie net begint krijgt dit niet voorgeschoteld. */

 {id:"cadiz-1", num:1, deel:"Un año en Cádiz", titel:"La llave que no giraba", drempel:8,
  tekst:"El avión aterrizó a las once de la noche y a las doce y media Marta ya estaba delante de la puerta.\n\n"+
   "Era una puerta verde, vieja, con la pintura levantada. La casera le había mandado la llave por correo dos semanas antes, con una nota: «Gira despacio y hacia la izquierda.»\n\n"+
   "Marta giró despacio. Y hacia la izquierda. La llave no se movió.\n\n"+
   "Lo intentó otra vez. Nada. La maleta estaba en el suelo, la calle estaba vacía, y en algún sitio, lejos, alguien cantaba.\n\n"+
   "Una ventana se abrió encima de su cabeza.\n\n"+
   "—¿Eres la holandesa? —dijo una voz de mujer.\n\n"+
   "—Sí. No consigo abrir.\n\n"+
   "—Nadie consigue abrir esa puerta la primera noche —dijo la voz—. Espera.\n\n"+
   "Un minuto después bajó una señora en bata, con las zapatillas mal puestas. Cogió la llave, la metió, la levantó un poco y empujó con la cadera. La puerta se abrió.\n\n"+
   "—Hay que levantarla —dijo—. Eso no lo pone en ninguna nota.\n\n"+
   "—Gracias. De verdad.\n\n"+
   "—Me llamo Rosario. Vivo arriba. Si necesitas algo, das dos golpes en el techo y bajo.\n\n"+
   "Marta subió la maleta sola. El piso olía a cerrado. Abrió la ventana y se quedó un rato mirando la calle, sin desnudar la maleta, sin encender más luz que la del pasillo.\n\n"+
   "Había estudiado español cuatro años. Y la primera frase útil de su vida en España se la había enseñado una señora en bata: hay que levantarla.",
  vragen:[
   {q:"¿Por qué no se abría la puerta?", opts:["Había que levantar la llave","La llave era otra","La cerradura estaba rota","La puerta estaba cerrada por dentro"], c:0},
   {q:"¿Quién ayuda a Marta?", opts:["Una vecina de arriba","La casera","Un taxista","Un policía"], c:0},
   {q:"¿Qué hace Marta al entrar?", opts:["Abre la ventana y mira la calle","Deshace la maleta","Llama a su madre","Se acuesta enseguida"], c:0}
  ],
  reflectie:"¿Cuál fue la primera cosa práctica que aprendiste en un sitio nuevo, y quién te la enseñó?"},

 {id:"cadiz-2", num:2, deel:"Un año en Cádiz", titel:"El mercado de la Libertad", drempel:8,
  tekst:"El sábado Marta fue al mercado con una lista. La lista no le sirvió de nada.\n\n"+
   "En el puesto del pescado había ocho cosas que no sabía nombrar. Señaló una.\n\n"+
   "—¿Esto qué es?\n\n"+
   "—Eso es acedía. Se hace en la sartén, un minuto por cada lado, con harina.\n\n"+
   "—¿Y cuánto?\n\n"+
   "—¿Para cuántos?\n\n"+
   "—Para mí sola.\n\n"+
   "El hombre cogió tres, las envolvió y le dijo un precio que a Marta le pareció imposible de barato.\n\n"+
   "En la frutería le pasó lo contrario. Pidió un kilo de tomates y la mujer le dio unos tomates duros y verdes.\n\n"+
   "—Perdone, estos están verdes.\n\n"+
   "—Claro. ¿Para hoy o para la semana?\n\n"+
   "—Para hoy.\n\n"+
   "—Ah, haberlo dicho.\n\n"+
   "Y le cambió los tomates por otros rojos y blandos, sin discutir, como si fuera lo más normal del mundo. Porque lo era.\n\n"+
   "Marta volvió a casa con dos bolsas y una idea nueva: aquí no se compra un producto, se compra un momento. No preguntan qué quieres. Preguntan para cuándo lo quieres.\n\n"+
   "Esa noche hizo las acedías. Un minuto por cada lado. Con harina.",
  vragen:[
   {q:"¿Qué le pregunta el pescadero antes de darle el precio?", opts:["Para cuántas personas es","Si tiene prisa","Si sabe cocinar","Si es de aquí"], c:0},
   {q:"¿Por qué le dieron tomates verdes?", opts:["Porque no dijo que eran para hoy","Porque no quedaban otros","Porque son más baratos","Porque son mejores"], c:0},
   {q:"¿Qué idea se lleva Marta del mercado?", opts:["Aquí se compra para un momento, no solo un producto","Aquí todo es barato","Hay que regatear","Es mejor ir el domingo"], c:0}
  ],
  reflectie:"¿Compras pensando en el día que lo vas a usar, o compras y ya veremos?"},

 {id:"cadiz-3", num:3, deel:"Un año en Cádiz", titel:"Dos golpes en el techo", drempel:8,
  tekst:"En noviembre se fue la luz. No solo en el piso de Marta: en toda la calle.\n\n"+
   "Marta estaba trabajando con el ordenador y de repente se quedó a oscuras, con la pantalla apagada y el zumbido de la nevera cortado en seco. El silencio era enorme.\n\n"+
   "Buscó el móvil. Cuatro por ciento de batería.\n\n"+
   "Se acordó de lo que le había dicho Rosario en septiembre y dio dos golpes en el techo con el palo de la escoba. Se sintió ridícula haciéndolo.\n\n"+
   "Treinta segundos después oyó pasos en la escalera.\n\n"+
   "—¿Estás bien? —dijo Rosario desde la puerta, con una vela en la mano.\n\n"+
   "—Sí, es que no veo nada.\n\n"+
   "—Ven arriba. Tengo gas, así que hay café.\n\n"+
   "Subieron. En la cocina de Rosario había dos velas, una radio de pilas y una manta en la silla.\n\n"+
   "—Antes esto pasaba cada invierno —dijo Rosario mientras ponía la cafetera—. Mi marido bajaba a la calle a hablar con los vecinos y volvía dos horas después. Decía que era para ver si sabían algo.\n\n"+
   "—¿Y sabían algo?\n\n"+
   "—Nunca. Pero volvía contento.\n\n"+
   "La luz volvió a las once y media. Marta bajó a su piso, encendió el ordenador y no trabajó.\n\n"+
   "Escribió a su hermana: «Hoy he entendido para qué sirve tener a alguien encima.»",
  vragen:[
   {q:"¿Cómo avisa Marta a Rosario?", opts:["Con dos golpes en el techo","Por teléfono","Gritando por la ventana","Subiendo a su piso"], c:0},
   {q:"¿Por qué hay café en casa de Rosario?", opts:["Porque tiene gas","Porque tiene generador","Porque lo había hecho antes","Porque no se fue la luz arriba"], c:0},
   {q:"¿Qué hacía el marido de Rosario cuando se iba la luz?", opts:["Bajaba a hablar con los vecinos","Arreglaba los cables","Se acostaba","Llamaba a la compañía"], c:0}
  ],
  reflectie:"¿A quién avisarías tú si esta noche te quedaras sin luz y sin batería?"},

 {id:"cadiz-4", num:4, deel:"Un año en Cádiz", titel:"El error de los ochenta euros", drempel:8,
  tekst:"Marta llevaba cuatro meses en Cádiz cuando cometió su error más caro.\n\n"+
   "Fue en una tienda de muebles. Quería una estantería y el chico le enseñó dos.\n\n"+
   "—Esta cuesta ochenta y esta ciento ochenta —dijo él.\n\n"+
   "Marta entendió «ochenta» y «cien ochenta», y pensó que la segunda costaba ciento ocho. Le pareció poca diferencia para una estantería mucho más bonita, y se llevó la cara.\n\n"+
   "En la caja vio el número en la pantalla y se le paró el corazón un segundo. Pero ya había dicho que sí, y le dio vergüenza decir que no.\n\n"+
   "Pagó. Salió a la calle con la caja bajo el brazo y se sintió tonta durante tres días.\n\n"+
   "Se lo contó a Rosario el sábado, esperando que se riera.\n\n"+
   "—Ochenta, ciento ochenta —dijo Rosario—. Es normal. Los números son lo último que se aprende bien.\n\n"+
   "—Pero yo estudié cuatro años.\n\n"+
   "—Estudiaste. Otra cosa es oírlos en una tienda, con ruido y con un chico que habla rápido.\n\n"+
   "Rosario le dio un consejo que Marta usó el resto del año: cuando oigas un número que importa, repítelo en voz alta. «Ciento ochenta, ¿verdad?» Nadie se ofende. Y si te has equivocado, te enteras antes de pagar.\n\n"+
   "La estantería sigue en el pasillo. Marta dice que es la cosa más cara que ha comprado nunca, y también la que más le enseñó.",
  vragen:[
   {q:"¿Qué entendió mal Marta?", opts:["Ciento ochenta por ciento ocho","Ochenta por dieciocho","El color del mueble","La fecha de entrega"], c:0},
   {q:"¿Por qué no dijo nada en la caja?", opts:["Le dio vergüenza","No vio el precio","No tenía otra opción","Ya había pagado"], c:0},
   {q:"¿Qué consejo le da Rosario?", opts:["Repetir el número en voz alta","No comprar sin pensar","Ir siempre acompañada","Pedir el precio por escrito"], c:0}
  ],
  reflectie:"¿Repites en voz alta lo que crees haber entendido, o esperas y ya se verá?"},

 {id:"cadiz-5", num:5, deel:"Un año en Cádiz", titel:"La clase de los martes", drempel:10,
  tekst:"El primer martes que Marta fue a bailar, no bailó.\n\n"+
   "Se quedó en la esquina de la sala con una botella de agua en la mano, mirando cómo doce personas hacían algo que a ella le parecía imposible: escuchar la música y mover los pies al mismo tiempo.\n\n"+
   "El profesor se llamaba Curro y hablaba muy rápido. «Uno, dos, tres, pausa. Cinco, seis, siete, pausa.» Marta contaba en holandés por dentro y siempre iba medio tiempo tarde.\n\n"+
   "En el descanso, una chica se acercó.\n\n"+
   "—¿Es tu primer día? Yo llevo un mes. Al principio yo también contaba en mi idioma.\n\n"+
   "—¿Y cuándo dejaste de hacerlo?\n\n"+
   "—Cuando dejé de contar.\n\n"+
   "A Marta esa frase le pareció una tontería de esas que se dicen para animar. Tardó siete semanas en entender que era literal.\n\n"+
   "Porque un martes de febrero, en mitad de una vuelta, se dio cuenta de que llevaba media canción sin contar nada. Los pies iban solos. Y en cuanto lo pensó, se equivocó y pisó a Curro.\n\n"+
   "—¡Ahí estaba! —dijo él, riéndose—. Lo tenías y lo has mirado. Como cuando aprendes a montar en bici.\n\n"+
   "Esa noche Marta volvió andando a casa por el paseo marítimo. Iba pensando en el español, no en el baile.\n\n"+
   "Ella todavía traducía. Todavía contaba. Pero ya sabía qué se sentía cuando eso paraba, y sabía que llegaba.",
  vragen:[
   {q:"¿Qué hace Marta su primer día de baile?", opts:["Mirar desde la esquina","Bailar con el profesor","Irse pronto","Apuntarse a otra clase"], c:0},
   {q:"¿Qué le dice la chica del descanso?", opts:["Que dejó de contar en su idioma cuando dejó de contar","Que hay que practicar en casa","Que Curro habla muy rápido","Que es mejor empezar en enero"], c:0},
   {q:"¿Qué pasa cuando Marta se da cuenta de que no está contando?", opts:["Se equivoca","Sigue perfectamente","Se para","Se ríe"], c:0}
  ],
  reflectie:"¿En qué momento notaste que dejabas de traducir en tu cabeza, aunque fuera solo unos segundos?"},

 {id:"cadiz-6", num:6, deel:"Un año en Cádiz", titel:"La carta que no mandó", drempel:10,
  tekst:"En marzo, Marta tuvo un problema con el alquiler.\n\n"+
   "La casera le mandó un mensaje: a partir de junio, el piso subía ciento veinte euros. Marta leyó el mensaje tres veces y se enfadó cada una de las tres.\n\n"+
   "Esa noche escribió una respuesta larguísima. Le salió en holandés primero y luego la tradujo, y quedó una carta llena de frases como «me parece completamente inaceptable» y «exijo una explicación».\n\n"+
   "Antes de mandarla, se la enseñó a Rosario.\n\n"+
   "Rosario la leyó despacio, moviendo los labios.\n\n"+
   "—Está muy bien escrita —dijo—. Y no te va a servir de nada.\n\n"+
   "—¿Por qué no?\n\n"+
   "—Porque parece una carta de abogado, y tú no tienes abogado. Aquí eso se habla. Le dices: mira, yo llevo un año, pago el uno de cada mes, no doy problemas. ¿No podemos dejarlo en sesenta?\n\n"+
   "—¿Y si dice que no?\n\n"+
   "—Pues dice que no. Pero por preguntar no se pierde nada, y por escribir así se pierde el tono.\n\n"+
   "Marta llamó al día siguiente. Le temblaba un poco la voz al principio. Dijo casi exactamente lo que Rosario le había dicho.\n\n"+
   "Se quedaron en setenta.\n\n"+
   "Cuando colgó, se dio cuenta de que había tenido una conversación difícil entera en español, sin preparar, y que no se acordaba de ninguna palabra que hubiera buscado.",
  vragen:[
   {q:"¿Qué le pasa a Marta en marzo?", opts:["Le suben el alquiler","Se le rompe la caldera","La casera vende el piso","Pierde el trabajo"], c:0},
   {q:"¿Por qué dice Rosario que la carta no sirve?", opts:["Porque parece de abogado y aquí eso se habla","Porque tiene faltas","Porque es demasiado corta","Porque la casera no lee"], c:0},
   {q:"¿En cuánto se quedan al final?", opts:["Setenta euros más","Ciento veinte más","Sesenta más","Igual que antes"], c:0}
  ],
  reflectie:"¿Cuándo escribes algo que en realidad deberías decir por teléfono?"},

 {id:"cadiz-7", num:7, deel:"Un año en Cádiz", titel:"El carnaval por dentro", drempel:10,
  tekst:"Todo el mundo le había dicho que el carnaval de Cádiz era otra cosa. Marta pensaba que exageraban.\n\n"+
   "Lo que se encontró no fue una fiesta con disfraces. Fue una ciudad entera cantando letras que se había escrito ella misma, sobre cosas de este año, con nombres y apellidos.\n\n"+
   "Y ahí Marta descubrió su límite.\n\n"+
   "Entendía las palabras. Casi todas. Pero no entendía por qué la gente se reía. Un grupo cantaba, la plaza entera se venía abajo, y ella se quedaba con la cara de quien llega tarde a un chiste.\n\n"+
   "Se lo dijo a Curro, que estaba a su lado con una cerveza.\n\n"+
   "—Es que no es idioma —dijo él—. Eso es saber quién es el del bigote.\n\n"+
   "—¿Y cómo se aprende eso?\n\n"+
   "—Viviendo aquí. O preguntando mucho, que es más rápido.\n\n"+
   "Así que Marta preguntó. Toda la noche. «¿Quién es ese?» «¿Qué pasó con el puente?» «¿Por qué se ríen con eso del pescado?»\n\n"+
   "A las tres de la mañana ya se reía cuando se reían los demás, y unas cuantas veces se reía porque de verdad lo había entendido.\n\n"+
   "Volvió a casa ronca. En la escalera se encontró a Rosario, que subía con una silla plegable debajo del brazo.\n\n"+
   "—¿Qué tal? —dijo Rosario.\n\n"+
   "—Ahora sé quién es el del bigote.\n\n"+
   "Rosario se rió y no preguntó nada más.",
  vragen:[
   {q:"¿Qué le cuesta entender a Marta en el carnaval?", opts:["Por qué se ríe la gente","Las palabras","La música","Los disfraces"], c:0},
   {q:"¿Qué dice Curro que hace falta?", opts:["Saber de quién se habla","Estudiar más vocabulario","Ir todos los años","Cantar también"], c:0},
   {q:"¿Qué hace Marta durante la noche?", opts:["Preguntar mucho","Grabar las canciones","Irse pronto a casa","Buscar las letras en el móvil"], c:0}
  ],
  reflectie:"¿Qué parte de un idioma no está en el idioma, sino en saber de qué habla la gente?"},

 {id:"cadiz-8", num:8, deel:"Un año en Cádiz", titel:"La llave que sí giraba", drempel:10,
  tekst:"El año terminaba en septiembre y Marta tenía que decidir.\n\n"+
   "En Ámsterdam la esperaba su antiguo trabajo, un piso más grande y una vida que ya sabía usar. Aquí tenía un contrato de seis meses, un piso con humedad en el pasillo y una estantería carísima.\n\n"+
   "Hizo una lista a dos columnas. La lista decía claramente que tenía que volver.\n\n"+
   "La miró un rato largo y luego la tiró.\n\n"+
   "No fue por la ciudad, ni por el mar, ni por el baile de los martes. Fue por una tontería que le había pasado esa misma semana.\n\n"+
   "Había ido a la ferretería a comprar unos tornillos y, mientras el hombre se los buscaba, se habían puesto a hablar del calor, y del calor habían pasado al aire acondicionado, y del aire acondicionado a que el hijo del hombre se iba a estudiar a Granada.\n\n"+
   "Diez minutos. Sin pensar en ninguna palabra. Sin preparar ninguna frase.\n\n"+
   "Y al salir, con los tornillos en el bolsillo, Marta se había dado cuenta de que no era ella la que había aprendido español. Era que aquí tenía una vida entera que solo existía en español, y que si se iba, esa vida no se iba con ella. Se quedaba en la calle, en la ferretería, en el techo de Rosario.\n\n"+
   "Firmó los seis meses.\n\n"+
   "Esa noche llegó a casa, metió la llave en la puerta verde y la levantó un poco sin darse cuenta de que lo hacía.",
  vragen:[
   {q:"¿Qué dice la lista de dos columnas?", opts:["Que tiene que volver","Que tiene que quedarse","Que da igual","Que espere un año más"], c:0},
   {q:"¿Qué pasó en la ferretería?", opts:["Habló diez minutos sin preparar nada","Se equivocó de tornillos","No la entendieron","Pagó de más"], c:0},
   {q:"¿Qué hace al final con la llave?", opts:["La levanta sin pensarlo","La deja en el buzón","La devuelve a la casera","Se le rompe"], c:0}
  ],
  reflectie:"¿Qué parte de tu vida existiría solo en español si te quedaras un año en un sitio?"},
"""

rep(
    ''' {id:"receta-1",''',
    NIEUW_BOEK + '''
 {id:"receta-1",''',
)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
