#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.79: Escuchar van zes naar vijftien scenes, allemaal op straat.

Stefan, 13 aug: "dictado kan weg en werd vervangen door escuchar. die moet fors worden uitgebreid."
En over de richting: "qua leren is denk ik een mooie mix tussen heel praktisch en gericht op
dagelijkse toepasbaarheid in de winkel, op straat, in de taxi enzo."

Dit is het praktische deel. Wat er lag: winkel, restaurant, dokter, ontmoeting, Fallas, waarom-zo-
laat-eten. Wat erbij komt, negen scenes op de plekken waar je als bezoeker echt staat:

    e7   taxi          een adres, het verkeer, en of je het haalt
    e8   mercado       een kilo hier, een half pondje daar
    e9   farmacia      wat je hebt, en hoe vaak je iets moet innemen
    e10  calle         de weg vragen en het antwoord kunnen volgen
    e11  peluqueria    zeggen wat er wel en niet af mag
    e12  cajero        de automaat houdt je pas, en het is zondag
    e13  piso          een kamer bekijken: wat deel je, en wat kost het
    e14  devolucion    iets terugbrengen zonder bonnetje
    e15  telefono      een afspraak maken en een dag afwijzen

## De vier regels zijn geen decoratie

Ze staan bovenin het ESCUCHAR-blok sinds v21.2 en elke scene hier houdt zich eraan:

1. De vraag staat in het Nederlands, anders test je stiekem ook lezen.
2. Afleiders blijven binnen de scene en verschillen op precies een betekenisdragend punt.
3. Minstens een vraag per scene staat niet letterlijk in de tekst.
4. Nooit vragen waar het zich afspeelt: dat staat al boven de oefening.

Plus de regel die pw-audicion.js afdwingt en die makkelijk te vergeten is: het juiste antwoord mag
niet meer dan vijf tekens langer zijn dan de langste afleider, in beide talen. Een meerkeuzevraag
over audio is verraderlijk makkelijk te raden op lengte alleen, en dan meet je algemene
ontwikkeling in plaats van Spaans.

Regel 3 is degene die het meeste werk kost. Bij elke scene is de derde vraag er een die je alleen
kunt beantwoorden als je begrijpt wat er gebeurt: "me sobra tiempo" betekent dat hij ruim op tijd
is, "el numero funciona igual" betekent dat het zondag toch kan, en aan het eind van het
telefoongesprek staat er nog geen afspraak, want er is alleen gevraagd.

## De audio

Niets. De avondrun spreekt ze vannacht in, want tools/avondrun-audio.js doet dialogo-a en dialogo-b
sinds vandaag ook. Dat is 36 nieuwe regels, ongeveer 1.800 tekens. Tot die tijd valt Escuchar
zichtbaar terug op de tekst en telt zo'n ronde niet mee als luisterbewijs; dat gedrag zat er al.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.79"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.79" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

ANKER = '''  ]}
];
function audZwaarte(sc){'''

if DOE_APP and ANKER not in src:
    print("Het einde van AUDICIONES staat er niet zoals verwacht.\n"
          "Deze patch bouwt op v23.78. Eerst bijtrekken:\n\n    git pull --rebase\n")
    sys.exit(1)

SCENES = u''' ]},
 {id:"e7", nivel:"a0", tema:"taxi", titel:"In de taxi", titelEn:"In the taxi",
  lineas:[
   {v:"a", es:"Buenas noches. \u00bfA d\u00f3nde vamos?"},
   {v:"b", es:"A la estaci\u00f3n de Atocha, por favor. Tengo un tren a las diez."},
   {v:"a", es:"Con este tr\u00e1fico, mejor por el paseo. Llegamos en veinte minutos."},
   {v:"b", es:"Perfecto, entonces me sobra tiempo."}
  ],
  vragen:[
   {q:"Hoe laat gaat de trein?", qEn:"What time is the train?",
    opts:["Om tien uur","Om acht uur","Om twee uur","Om elf uur"],
    optsEn:["At ten","At eight","At two","At eleven"], c:0,
    waarom:"A las diez = om tien uur. Diez is tien, dos is twee.",
    waaromEn:"A las diez = at ten. Diez is ten, dos is two."},
   {q:"Waarom kiest de chauffeur een andere route?", qEn:"Why does the driver take another route?",
    opts:["Het is druk op de weg","De weg is afgesloten","Het is korter zo","Hij kent de stad niet"],
    optsEn:["The traffic is bad","The road is closed","It is shorter","He does not know the city"], c:0,
    waarom:"Con este tr\u00e1fico = met dit verkeer. Dat is de reden die hij zelf geeft.",
    waaromEn:"Con este tr\u00e1fico = with this traffic. That's the reason he gives himself."},
   {q:"Wat zegt de passagier over zijn tijd?", qEn:"What does the passenger say about his time?",
    opts:["Hij komt ruim op tijd","Hij moet zich haasten","Hij mist zijn trein","Hij wil een andere weg"],
    optsEn:["He'll be there in time","He has to hurry","He'll miss his train","He wants another route"], c:0,
    waarom:"Me sobra tiempo = ik heb tijd over. Sobrar is overblijven, en dat zegt hij pas nadat hij de twintig minuten heeft gehoord.",
    waaromEn:"Me sobra tiempo = I have time to spare. Sobrar is to be left over, and he says it only after hearing the twenty minutes."}
  ]},
 {id:"e8", nivel:"a0", tema:"mercado", titel:"Op de markt", titelEn:"At the market",
  lineas:[
   {v:"a", es:"\u00bfQu\u00e9 le pongo?"},
   {v:"b", es:"Un kilo de tomates y medio de cebollas."},
   {v:"a", es:"Los tomates est\u00e1n muy buenos hoy. \u00bfAlgo m\u00e1s?"},
   {v:"b", es:"No, nada m\u00e1s. \u00bfCu\u00e1nto es todo?"}
  ],
  vragen:[
   {q:"Hoeveel uien worden er gekocht?", qEn:"How many onions are bought?",
    opts:["Een halve kilo","Een hele kilo","Twee kilo","Geen uien"],
    optsEn:["Half a kilo","A whole kilo","Two kilos","No onions"], c:0,
    waarom:"Medio de cebollas = een half (kilo) uien. Medio slaat terug op het kilo van daarvoor.",
    waaromEn:"Medio de cebollas = half a (kilo of) onions. Medio refers back to the kilo mentioned before."},
   {q:"Wat zegt de verkoper over de tomaten?", qEn:"What does the seller say about the tomatoes?",
    opts:["Ze zijn vandaag goed","Ze zijn vandaag duur","Ze zijn bijna op","Ze zijn niet rijp"],
    optsEn:["They are good today","They are dear today","They are almost gone","They are not ripe"], c:0,
    waarom:"Est\u00e1n muy buenos hoy: met estar, dus hoe ze er n\u00fa bij staan. Son buenos zou over de soort gaan.",
    waaromEn:"Est\u00e1n muy buenos hoy: with estar, so how they are right now. Son buenos would be about the kind."},
   {q:"Wat gebeurt er direct hierna?", qEn:"What happens right after this?",
    opts:["Er wordt afgerekend","Er komt nog fruit bij","De klant loopt weg","De markt gaat dicht"],
    optsEn:["She pays for it","She adds some fruit","She walks away","The market closes"], c:0,
    waarom:"\u00bfCu\u00e1nto es todo? = hoeveel is het samen? Die vraag stel je vlak voor het betalen, en nada m\u00e1s sluit de bestelling af.",
    waaromEn:"\u00bfCu\u00e1nto es todo? = how much is it all? You ask that right before paying, and nada m\u00e1s closes the order."}
  ]},
 {id:"e9", nivel:"a0", tema:"farmacia", titel:"Bij de apotheek", titelEn:"At the pharmacy",
  lineas:[
   {v:"a", es:"Buenos d\u00edas. Me duele mucho la cabeza desde ayer."},
   {v:"b", es:"\u00bfTiene fiebre?"},
   {v:"a", es:"No, fiebre no. Solo dolor."},
   {v:"b", es:"Entonces esto cada ocho horas, y beba mucha agua."}
  ],
  vragen:[
   {q:"Wat is er aan de hand?", qEn:"What is the matter?",
    opts:["Hoofdpijn","Buikpijn","Keelpijn","Rugpijn"],
    optsEn:["A headache","A stomach ache","A sore throat","A bad back"], c:0,
    waarom:"Me duele la cabeza = mijn hoofd doet pijn. La cabeza is het hoofd.",
    waaromEn:"Me duele la cabeza = my head hurts. La cabeza is the head."},
   {q:"Hoe vaak moet het middel?", qEn:"How often should the medicine be taken?",
    opts:["Om de acht uur","Om de vier uur","Twee keer per dag","Alleen 's avonds"],
    optsEn:["Every eight hours","Every four hours","Twice a day","Only at night"], c:0,
    waarom:"Cada ocho horas = elke acht uur. Ocho is acht, cuatro is vier.",
    waaromEn:"Cada ocho horas = every eight hours. Ocho is eight, cuatro is four."},
   {q:"Wat wordt er uitdrukkelijk uitgesloten?", qEn:"What is explicitly ruled out?",
    opts:["Koorts","Hoofdpijn","Vermoeidheid","Slapeloosheid"],
    optsEn:["Fever","Headache","Tiredness","Sleeplessness"], c:0,
    waarom:"De apotheker vraagt \u00bfTiene fiebre? en het antwoord is fiebre no. Er is dus pijn zonder koorts, en dat verandert het advies.",
    waaromEn:"The pharmacist asks \u00bfTiene fiebre? and the answer is fiebre no. So there is pain without fever, and that changes the advice."}
  ]},
 {id:"e10", nivel:"a0", tema:"calle", titel:"De weg vragen", titelEn:"Asking the way",
  lineas:[
   {v:"a", es:"Perdone, \u00bfhay una parada de autob\u00fas por aqu\u00ed?"},
   {v:"b", es:"S\u00ed, la segunda calle a la derecha, al lado del banco."},
   {v:"a", es:"\u00bfEst\u00e1 lejos?"},
   {v:"b", es:"Cinco minutos andando, no m\u00e1s."}
  ],
  vragen:[
   {q:"Welke straat moet je nemen?", qEn:"Which street should you take?",
    opts:["De tweede rechts","De eerste rechts","De tweede links","De eerste links"],
    optsEn:["The second right","The first right","The second left","The first left"], c:0,
    waarom:"La segunda calle a la derecha = de tweede straat rechts. Segunda is tweede, derecha is rechts.",
    waaromEn:"La segunda calle a la derecha = the second street on the right. Segunda is second, derecha is right."},
   {q:"Hoe lang duurt het lopen?", qEn:"How long is the walk?",
    opts:["Vijf minuten","Vijftien minuten","Een half uur","Twee minuten"],
    optsEn:["Five minutes","Fifteen minutes","Half an hour","Two minutes"], c:0,
    waarom:"Cinco minutos andando = vijf minuten lopend. Cinco is vijf, quince is vijftien.",
    waaromEn:"Cinco minutos andando = five minutes on foot. Cinco is five, quince is fifteen."},
   {q:"Waaraan herken je de halte?", qEn:"How do you recognise the stop?",
    opts:["Aan de bank ernaast","Aan het bord erboven","Aan de rij mensen","Aan de kleur"],
    optsEn:["By the bank next to it","By the sign above it","By the queue","By its colour"], c:0,
    waarom:"Al lado del banco = naast de bank. Dat is het enige herkenningspunt dat erbij wordt gegeven.",
    waaromEn:"Al lado del banco = next to the bank. That's the only landmark given."}
  ]},
 {id:"e11", nivel:"a0", tema:"peluqueria", titel:"Bij de kapper", titelEn:"At the hairdresser",
  lineas:[
   {v:"a", es:"\u00bfC\u00f3mo lo quiere?"},
   {v:"b", es:"Corto por detr\u00e1s, pero por delante casi igual."},
   {v:"a", es:"\u00bfLe lavo el pelo antes?"},
   {v:"b", es:"No hace falta, lo lav\u00e9 esta ma\u00f1ana."}
  ],
  vragen:[
   {q:"Wat gebeurt er aan de voorkant?", qEn:"What happens at the front?",
    opts:["Bijna niets","Alles eraf","Veel korter","Alleen wassen"],
    optsEn:["Almost nothing","All of it off","Much shorter","Just a wash"], c:0,
    waarom:"Casi igual = bijna hetzelfde. Alleen por detr\u00e1s (achter) mag kort.",
    waaromEn:"Casi igual = almost the same. Only por detr\u00e1s (at the back) may go short."},
   {q:"Wordt het haar in de kapsalon gewassen?", qEn:"Is the hair washed at the salon?",
    opts:["Nee","Ja, eerst","Ja, daarna","Alleen voor"],
    optsEn:["No","Yes, first","Yes, after","Only at the front"], c:0,
    waarom:"No hace falta = het hoeft niet. Dat is een nette manier om nee te zeggen.",
    waaromEn:"No hace falta = there's no need. That's a polite way of saying no."},
   {q:"Waarom hoeft dat niet?", qEn:"Why is that not needed?",
    opts:["Het is al gewassen","Het kost extra geld","Er is geen tijd","De kapper raadt het af"],
    optsEn:["It was washed today","It costs extra","There is no time","The barber says no"], c:0,
    waarom:"Lo lav\u00e9 esta ma\u00f1ana = ik heb het vanmorgen gewassen. Lav\u00e9 is indefinido: af, vanmorgen, klaar.",
    waaromEn:"Lo lav\u00e9 esta ma\u00f1ana = I washed it this morning. Lav\u00e9 is the indefinido: done, this morning, finished."}
  ]},
 {id:"e12", nivel:"a2", tema:"cajero", titel:"Bij de pinautomaat", titelEn:"At the cash machine",
  lineas:[
   {v:"a", es:"Esta m\u00e1quina no me da el dinero. Se ha quedado con mi tarjeta."},
   {v:"b", es:"Tiene que llamar al n\u00famero de atr\u00e1s. Est\u00e1 abierto hasta las ocho."},
   {v:"a", es:"\u00bfY ma\u00f1ana? Ma\u00f1ana es domingo."},
   {v:"b", es:"Los domingos est\u00e1 cerrado, pero el n\u00famero funciona igual."}
  ],
  vragen:[
   {q:"Wat is er misgegaan?", qEn:"What went wrong?",
    opts:["De kaart is ingeslikt","De kaart is gestolen","De pincode klopt niet","Het geld is op"],
    optsEn:["The card is stuck","The card was stolen","The code is wrong","There is no money"], c:0,
    waarom:"Se ha quedado con mi tarjeta = hij heeft mijn pas gehouden. Quedarse con iets = iets houden.",
    waaromEn:"Se ha quedado con mi tarjeta = it kept my card. Quedarse con something = to keep something."},
   {q:"Wat moet er gebeuren?", qEn:"What needs to be done?",
    opts:["Bellen met een nummer","Morgen terugkomen","Naar een andere bank","Wachten tot acht uur"],
    optsEn:["Call a number","Come back tomorrow","Go to another bank","Wait until eight"], c:0,
    waarom:"Tiene que llamar = u moet bellen. Tener que + infinitief is de gewone manier om moeten te zeggen.",
    waaromEn:"Tiene que llamar = you have to call. Tener que + infinitive is the usual way to say must."},
   {q:"Kan het morgen ook nog?", qEn:"Can it still be done tomorrow?",
    opts:["Ja, per telefoon wel","Ja, aan de balie","Nee, helemaal niet","Alleen 's ochtends"],
    optsEn:["Yes, by phone","Yes, at the desk","No, not at all","Only in the morning"], c:0,
    waarom:"Est\u00e1 cerrado maar el n\u00famero funciona igual: het kantoor is dicht, het nummer werkt evengoed. Igual betekent hier toch, ondanks dat.",
    waaromEn:"Est\u00e1 cerrado but el n\u00famero funciona igual: the office is closed, the number works all the same. Igual here means anyway, despite that."}
  ]},
 {id:"e13", nivel:"a2", tema:"piso", titel:"Een kamer bekijken", titelEn:"Viewing a room",
  lineas:[
   {v:"a", es:"La habitaci\u00f3n es peque\u00f1a, pero da al patio. Es muy tranquila."},
   {v:"b", es:"\u00bfY la cocina la comparto?"},
   {v:"a", es:"S\u00ed, con dos personas. El ba\u00f1o tambi\u00e9n."},
   {v:"b", es:"\u00bfY cu\u00e1nto es al mes, con gastos?"}
  ],
  vragen:[
   {q:"Wat wordt er als voordeel genoemd?", qEn:"What is mentioned as an advantage?",
    opts:["Het is er stil","De kamer is groot","Er is een balkon","De huur is laag"],
    optsEn:["It is quiet","The room is big","It has a balcony","The rent is low"], c:0,
    waarom:"Da al patio, es muy tranquila = hij ligt aan de binnenplaats en is heel rustig. Dar a = uitkijken op.",
    waaromEn:"Da al patio, es muy tranquila = it looks onto the courtyard and is very quiet. Dar a = to look out onto."},
   {q:"Met hoeveel mensen deel je de keuken?", qEn:"With how many people is the kitchen shared?",
    opts:["Twee","E\u00e9n","Drie","Niemand"],
    optsEn:["Two","One","Three","Nobody"], c:0,
    waarom:"Con dos personas = met twee mensen. Dos is twee, tres is drie.",
    waaromEn:"Con dos personas = with two people. Dos is two, tres is three."},
   {q:"Wat wil de bezoeker nog weten?", qEn:"What does the visitor still want to know?",
    opts:["De prijs met kosten","De prijs zonder kosten","Wanneer het vrij is","Of er meubels zijn"],
    optsEn:["The price with bills","The price without bills","When it is free","If it is furnished"], c:0,
    waarom:"Con gastos = met de kosten erbij, dus gas, water en licht. Hij vraagt er expres naar, want al mes alleen zegt niets over de eindprijs.",
    waaromEn:"Con gastos = including bills, so gas, water and electricity. He asks on purpose, because al mes alone says nothing about the final price."}
  ]},
 {id:"e14", nivel:"a2", tema:"devolucion", titel:"Iets terugbrengen", titelEn:"Returning something",
  lineas:[
   {v:"a", es:"Quer\u00eda devolver esta camisa. Me queda peque\u00f1a."},
   {v:"b", es:"\u00bfTiene el tique?"},
   {v:"a", es:"Lo perd\u00ed. Pero pagu\u00e9 con tarjeta, aqu\u00ed est\u00e1 el movimiento."},
   {v:"b", es:"Entonces le doy un vale, no el dinero."}
  ],
  vragen:[
   {q:"Wat is er mis met het overhemd?", qEn:"What is wrong with the shirt?",
    opts:["Het is te klein","Het is te groot","Het is kapot","De kleur klopt niet"],
    optsEn:["It is too small","It is too big","It is torn","The colour is wrong"], c:0,
    waarom:"Me queda peque\u00f1a = hij zit me te klein. Quedar gaat hier over hoe iets past.",
    waaromEn:"Me queda peque\u00f1a = it's too small on me. Quedar here is about how something fits."},
   {q:"Wat krijgt de klant terug?", qEn:"What does the customer get back?",
    opts:["Een tegoedbon","Het hele bedrag","Een ander hemd","Helemaal niets"],
    optsEn:["A voucher","The money back","Another shirt","Nothing at all"], c:0,
    waarom:"Un vale, no el dinero = een bon, niet het geld. Dat zegt de verkoper er expliciet bij.",
    waaromEn:"Un vale, no el dinero = a voucher, not the money. The seller says so explicitly."},
   {q:"Waarom geen geld terug?", qEn:"Why no money back?",
    opts:["De bon is kwijt","Het is te laat","Het was afgeprijsd","Er is gepind"],
    optsEn:["The receipt is lost","It is too late","It was on sale","She paid by card"], c:0,
    waarom:"Lo perd\u00ed = ik ben hem kwijtgeraakt (perder, indefinido). Het bankafschrift bewijst wel de aankoop, maar zonder tique blijft het een vale.",
    waaromEn:"Lo perd\u00ed = I lost it (perder, indefinido). The bank statement proves the purchase, but without the receipt it stays a voucher."}
  ]},
 {id:"e15", nivel:"a2", tema:"telefono", titel:"Een afspraak maken", titelEn:"Making an appointment",
  lineas:[
   {v:"a", es:"Cl\u00ednica Sol, buenos d\u00edas."},
   {v:"b", es:"Quer\u00eda pedir cita con el dentista."},
   {v:"a", es:"\u00bfLe viene bien el jueves a las cinco?"},
   {v:"b", es:"El jueves no puedo. \u00bfHay algo el viernes por la ma\u00f1ana?"}
  ],
  vragen:[
   {q:"Welke dag wordt er afgewezen?", qEn:"Which day is turned down?",
    opts:["Donderdag","Vrijdag","Dinsdag","Maandag"],
    optsEn:["Thursday","Friday","Tuesday","Monday"], c:0,
    waarom:"El jueves no puedo = donderdag kan ik niet. Jueves is donderdag, viernes is vrijdag.",
    waaromEn:"El jueves no puedo = I can't on Thursday. Jueves is Thursday, viernes is Friday."},
   {q:"Wanneer zou het wel schikken?", qEn:"When would it suit?",
    opts:["Vrijdagochtend","Vrijdagmiddag","Donderdagochtend","Zaterdagochtend"],
    optsEn:["Friday morning","Friday afternoon","Thursday morning","Saturday morning"], c:0,
    waarom:"El viernes por la ma\u00f1ana = vrijdagochtend. Por la ma\u00f1ana is 's ochtends, por la tarde 's middags.",
    waaromEn:"El viernes por la ma\u00f1ana = Friday morning. Por la ma\u00f1ana is in the morning, por la tarde in the afternoon."},
   {q:"Staat de afspraak aan het eind vast?", qEn:"Is the appointment settled at the end?",
    opts:["Nee, nog niet","Ja, donderdag","Ja, vrijdag","Ja, maar later"],
    optsEn:["No, not yet","Yes, Thursday","Yes, Friday","Yes, but later"], c:0,
    waarom:"\u00bfHay algo el viernes...? is een vraag, en er komt geen antwoord meer. De donderdag is afgewezen en de vrijdag is nog niet bevestigd.",
    waaromEn:"\u00bfHay algo el viernes...? is a question, and no answer follows. Thursday was declined and Friday isn't confirmed yet."}
  ]}
];
function audZwaarte(sc){'''


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(ANKER, SCENES)
    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s (negen luisterscenes erbij)" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
