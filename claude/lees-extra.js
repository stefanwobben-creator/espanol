/* v23.24. Woorden die in de leesteksten voorkomen en die de app nergens had staan: niet als
   leswoord en niet in de frequentielijst. Gevonden door alle 23 hoofdstukken langs de opzoeker te
   halen en op te schrijven wat er niet uit kwam, dus dit is geen gok maar een gatenlijst.

   De eerste zeven zijn de belangrijkste: por, todo, me, mundo, perder, calor en mal bestonden alleen
   binnen een uitdrukking (por favor, todo el mundo, me llamo), en werden daardoor uitgelegd als die
   uitdrukking. Samen zijn ze goed voor 82 treffers in deze teksten.

   De rest zijn woorden uit de verhalen zelf. Vervoegde vormen staan er los bij waar de vormherkenning
   ze niet kan terugrekenen: sonríe komt van sonreír, en die klinkerwissel kent VORM_TABEL niet. */
var LEES_EXTRA = {
 por:["voor, door, per","for, by, per"], todo:["alles, heel","all, everything"],
 me:["mij, me","me, myself"], mundo:["wereld","world"], perder:["verliezen, missen","to lose, to miss"],
 calor:["warmte, hitte","heat"], mal:["slecht","bad, badly"], vosotras:["jullie (v)","you (fem. plural)"],
 treinta:["dertig","thirty"], cuarenta:["veertig","forty"], cincuenta:["vijftig","fifty"],
 sesenta:["zestig","sixty"], setenta:["zeventig","seventy"], ochenta:["tachtig","eighty"],
 noventa:["negentig","ninety"], cien:["honderd","a hundred"], mil:["duizend","a thousand"],
 millon:["miljoen","a million"],
 enero:["januari","January"], febrero:["februari","February"], marzo:["maart","March"],
 abril:["april","April"], mayo:["mei","May"], junio:["juni","June"], julio:["juli","July"],
 agosto:["augustus","August"], septiembre:["september","September"], octubre:["oktober","October"],
 noviembre:["november","November"], diciembre:["december","December"],
 redondo:["rond","round"], moverse:["bewegen","to move"], sonreir:["glimlachen","to smile"],
 sonrie:["glimlacht (van sonreír)","smiles (from sonreír)"],
 sonriendo:["glimlachend","smiling"], reir:["lachen","to laugh"], rie:["lacht (van reír)","laughs (from reír)"],
 torcido:["scheef, krom","crooked"], melodia:["melodie","melody"], fino:["fijn, dun","fine, thin"],
 transparente:["doorzichtig","transparent"], metal:["metaal","metal"], casco:["schild, helm","shell, helmet"],
 aceite:["olie","oil"], obrero:["arbeider","worker"], monte:["berg, heuvel","mountain, hill"],
 prohibido:["verboden","forbidden"], tranquilidad:["rust","calm"], vaca:["koe","cow"],
 maletero:["kofferbak","car boot, trunk"], pacto:["pact, afspraak","pact, agreement"],
 republica:["republiek","republic"], gobernar:["regeren","to govern"], votar:["stemmen","to vote"],
 saludarse:["elkaar groeten","to greet each other"], bombardear:["bombarderen","to bomb"],
 besar:["kussen","to kiss"], mirarse:["elkaar aankijken","to look at each other"],
 caber:["passen, erin gaan","to fit"], reaccionar:["reageren","to react"],
 cartilla:["bonnenboekje","ration book"], racionamiento:["rantsoenering","rationing"],
 casilla:["hokje, vakje","box, square"], bikini:["bikini","bikini"],
 apretado:["opeengepakt, krap","cramped, tight"], lejano:["ver weg","distant"],
 pegado:["geplakt, dicht tegen","stuck, close against"], tembloroso:["bevend","trembling"],
 expectante:["afwachtend","expectant"], observar:["kijken naar, observeren","to watch, to observe"],
 guardian:["bewaker","guardian"], valentia:["moed","courage"], brillar:["schitteren","to shine"],
 explotar:["ontploffen","to explode"], tararear:["neuriën","to hum"], jugueton:["speels","playful"],
 picaro:["ondeugend","mischievous"], silencioso:["stil","silent"], reverencia:["buiging","bow"],
 exagerado:["overdreven","exaggerated"], ofenderse:["beledigd zijn","to take offence"],
 incomodo:["ongemakkelijk","uncomfortable"], ideal:["ideaal","ideal"], flaco:["mager","skinny"],
 lentamente:["langzaam","slowly"], rendirse:["opgeven","to give up"], luchar:["vechten","to fight"],
 sentarse:["gaan zitten","to sit down"], acercarse:["naderen","to approach"],
 oyen:["horen (van oír)","hear (from oír)"], oyeron:["hoorden (van oír)","heard (from oír)"],
 juegan:["spelen (van jugar)","play (from jugar)"], piensen:["denken (van pensar)","think (from pensar)"],
 sientan:["gaan zitten (van sentarse)","sit down (from sentarse)"],
 acercan:["naderen (van acercarse)","approach (from acercarse)"],
 explota:["ontploft (van explotar)","explodes (from explotar)"],
 brilla:["schittert (van brillar)","shines (from brillar)"],
 tararea:["neuriet (van tararear)","hums (from tararear)"],
 luche:["vecht (van luchar)","fight (from luchar)"],
 rendirte:["je overgeven, opgeven","to give up"],
 encontremos:["laten we vinden (van encontrar)","let us find (from encontrar)"],
 ensenarte:["je laten zien, je leren","to show you, to teach you"],
 observando:["kijkend, observerend","watching, observing"],
 buscarlo:["hem zoeken","to look for it"],
 bombardean:["bombarderen (van bombardear)","bomb (from bombardear)"],
 bombardea:["bombardeert (van bombardear)","bombs (from bombardear)"],
 besan:["kussen (van besar)","kiss (from besar)"],
 cabe:["past erin (van caber)","fits (from caber)"],
 reacciona:["reageert (van reaccionar)","reacts (from reaccionar)"],
 votan:["stemmen (van votar)","vote (from votar)"],
 votado:["gestemd (van votar)","voted (from votar)"],
 dona:["mevrouw (voor een voornaam)","lady (before a first name)"], don:["meneer (voor een voornaam)","sir (before a first name)"],
 abrirse:["opengaan","to open up"], pequenita:["heel klein","very small"]
};
