#!/usr/bin/env python3
# v23.193 - de eerste twee van de dertien ontbrekende lessen
#
# Stefan, 24 aug: "eerst twee."
#
# De review "De grammatica als geheel" telde dat 98 van de 281 toetsvragen (35%) gaan over stof die
# nergens wordt uitgelegd: twaalf spiekkaarten hebben wél een toets en géén les. Dit zijn de eerste
# twee lessen die zo'n gat vullen, en ze zijn er ook om te kijken of de vorm bevalt voordat de
# andere elf geschreven worden.
#
# De leerkaart staat in het project ("Leerkaart - de twee ontbrekende lessen als proef") en is
# geschreven vóór deze code.
#
#   kaart 20  El imperativo (tú): recepten en instructies      8 vragen, geen les
#   kaart 25  Advies geven: imperativo + tener que / deber      8 vragen, geen les
#   kaart 12  Beleefd vragen en lenen (puedo, podrías, ...)    10 vragen, geen les
#
# Twee lessen, drie kaarten, 26 toetsvragen die nu een uitleg achter zich hebben.
#
# WAAROM DEZE TWEE
#
# Niet omdat ze het grootste gat zijn, maar omdat ze het duidelijkst zijn: allebei kernstof voor
# A2/B1 en allebei iets dat je in Spanje dagelijks nodig hebt. Een recept lezen, en iemand beleefd
# iets vragen zonder bot te klinken.
#
# WAAR ZE IN DE VOLGORDE KOMEN
#
# GC_ORDE is de leervolgorde. De imperativo komt ná gerundio: je moet de presente kennen, want de
# bevestigende tú-vorm ís de derde persoon enkelvoud van de presente, en dat is precies wat de les
# gebruikt om hem uit te leggen. De beleefdheidsvormen komen ná tuusted, want het verschil tussen
# tú en usted is de helft van het onderwerp.
#
# Ze staan allebei vóór de twee verleden tijden, en dat is met opzet: die staan al achteraan en de
# review noemt dat een probleem op zichzelf. Dit maakt het niet erger.
#
# WAT DEZE PATCH NIET DOET
#
# Er komt geen productiestap bij. Het microlesmodel is meerkeuze en dat blijft in deze ronde zo. De
# leerkaart zegt wat de productiestap voor de imperativo zou moeten zijn (een rij in de vormenladder,
# want de vorm volgt uit de presente) en dat die er nog niet is. Voor de beleefdheidsvormen is er
# geen goedkope productiestap: podría en te importaría zijn vaste wendingen, geen paradigma.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.193"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

# Niet op "imperativo" alleen: dat woord staat al in de titel van toetsje en spiekkaart, en
# dan zou deze patch zichzelf voor gedaan houden zonder iets te doen.
DOE_APP = '{id:"imperativo"' not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de woordvoorraad waar de twee lessen uit putten
# =============================================================================================
DATA = r'''
/* v23.193: de werkwoorden waar de imperativo-les mee werkt. Bewust keukenwerkwoorden en
   instructies, want dat is waar je de gebiedende wijs tegenkomt (spiekkaart 20 heet niet voor
   niets "recepten en instructies").

   `tu` is de bevestigende tú-vorm, `neg` de ontkennende. Die twee staan er allebei omdat ze in het
   Spaans niet uit elkaar volgen: corta wordt no cortes, en dat is de hele moeilijkheid. */
var GC_IMP = [
 {inf:"cortar",  tu:"corta",  neg:"no cortes",  obj:"la cebolla",
  geb:"Snijd de ui.",            gebNeg:"Snijd de ui niet.",          hij:"Hij snijdt de ui.",           ik:"Ik snijd de ui.",
  gebEn:"Cut the onion.",        gebNegEn:"Do not cut the onion.",    hijEn:"He cuts the onion.",        ikEn:"I cut the onion."},
 {inf:"a\u00f1adir",  tu:"a\u00f1ade",  neg:"no a\u00f1adas",  obj:"la sal",
  geb:"Voeg het zout toe.",      gebNeg:"Voeg het zout niet toe.",    hij:"Hij voegt het zout toe.",     ik:"Ik voeg het zout toe.",
  gebEn:"Add the salt.",         gebNegEn:"Do not add the salt.",     hijEn:"He adds the salt.",         ikEn:"I add the salt."},
 {inf:"mezclar", tu:"mezcla", neg:"no mezcles", obj:"todo",
  geb:"Meng alles.",             gebNeg:"Meng niet alles.",           hij:"Hij mengt alles.",            ik:"Ik meng alles.",
  gebEn:"Mix everything.",       gebNegEn:"Do not mix everything.",   hijEn:"He mixes everything.",      ikEn:"I mix everything."},
 {inf:"abrir",   tu:"abre",   neg:"no abras",   obj:"la puerta",
  geb:"Doe de deur open.",       gebNeg:"Doe de deur niet open.",     hij:"Hij doet de deur open.",      ik:"Ik doe de deur open.",
  gebEn:"Open the door.",        gebNegEn:"Do not open the door.",    hijEn:"He opens the door.",        ikEn:"I open the door."},
 {inf:"beber",   tu:"bebe",   neg:"no bebas",   obj:"agua",
  geb:"Drink water.",            gebNeg:"Drink geen water.",          hij:"Hij drinkt water.",           ik:"Ik drink water.",
  gebEn:"Drink water.",          gebNegEn:"Do not drink water.",      hijEn:"He drinks water.",          ikEn:"I drink water."},
 {inf:"escribir",tu:"escribe",neg:"no escribas",obj:"tu nombre",
  geb:"Schrijf je naam op.",     gebNeg:"Schrijf je naam niet op.",   hij:"Hij schrijft zijn naam op.",  ik:"Ik schrijf mijn naam op.",
  gebEn:"Write your name.",      gebNegEn:"Do not write your name.",  hijEn:"He writes his name.",       ikEn:"I write my name."}
];/* De acht onregelmatige tú-vormen van het Spaans. Een gesloten rij: er zijn er geen negen. */
var GC_IMP_ONREG = [
 {inf:"hacer", tu:"haz", geb:"Doe het!",     gebEn:"Do it!"},
 {inf:"poner", tu:"pon", geb:"Zet neer!",    gebEn:"Put it down!"},
 {inf:"venir", tu:"ven", geb:"Kom!",         gebEn:"Come!"},
 {inf:"tener", tu:"ten", geb:"Hou vast!",    gebEn:"Hold this!"},
 {inf:"decir", tu:"di",  geb:"Zeg het!",     gebEn:"Say it!"},
 {inf:"salir", tu:"sal", geb:"Ga weg!",      gebEn:"Get out!"},
 {inf:"ser",   tu:"s\u00e9",  geb:"Wees aardig!", gebEn:"Be nice!"},
 {inf:"ir",    tu:"ve",  geb:"Ga!",          gebEn:"Go!"}
];/* v23.193: waar je beleefd om vraagt. GC_PEDIR bestond al maar is korter en zit vast aan de
   pedir-of-preguntar-les; deze rij draagt ook een werkwoord, want ¿Podrías + infinitivo? vraagt er
   een. */
var GC_CORTES = [
 {ww:"traer",   tu:"traes",   obj:"la cuenta",  vraag:"Zou je de rekening kunnen brengen?",     vraagEn:"Could you bring the bill?",
  inf:"brengen",   infEn:"bring",   te:"de rekening te brengen",  teEn:"bringing the bill"},
 {ww:"pasar",   tu:"pasas",   obj:"la sal",     vraag:"Zou je het zout kunnen aangeven?",       vraagEn:"Could you pass the salt?",
  inf:"aangeven",  infEn:"pass",    te:"het zout aan te geven",   teEn:"passing the salt"},
 {ww:"prestar", tu:"prestas", obj:"un boli",    vraag:"Zou je me een pen kunnen lenen?",        vraagEn:"Could you lend me a pen?",
  inf:"lenen",     infEn:"lend",    te:"een pen te lenen",        teEn:"lending a pen"},
 {ww:"abrir",   tu:"abres",   obj:"la ventana", vraag:"Zou je het raam kunnen openen?",         vraagEn:"Could you open the window?",
  inf:"openen",    infEn:"open",    te:"het raam te openen",      teEn:"opening the window"},
 {ww:"repetir", tu:"repites", obj:"eso",        vraag:"Zou je dat kunnen herhalen?",            vraagEn:"Could you repeat that?",
  inf:"herhalen",  infEn:"repeat",  te:"dat te herhalen",         teEn:"repeating that"}
];'''

if DOE_APP:
    rep("var GC_ADJ_SER = [", DATA.lstrip("\n") + "var GC_ADJ_SER = [")

# =============================================================================================
# 2. de twee lessen
# =============================================================================================
IMPERATIVO = r'''
 /* v23.193. Kaart 20 en 25 dragen samen zestien toetsvragen over de imperativo en er stond geen
    les tegenover. Zie de review "De grammatica als geheel": 35 procent van de toetsvragen ging
    over stof die nergens werd uitgelegd, en dit is het eerste gat dat gedicht wordt. */
 {id:"imperativo", icon:"👉", naam:"Zeg wat iemand moet doen", naamEn:"Telling someone what to do",
  corr:[], spiek:{a2:[20,25]}, wizard:null,
  uitleg:"<p>De gebiedende wijs tegen <b>tú</b> is in het Spaans verrassend makkelijk: je neemt de vorm die bij <i>él</i> hoort in de tegenwoordige tijd, en klaar.</p>"+
    "<p><i>cortar</i> → <i>él corta</i> → <b>corta</b> la cebolla. <i>beber</i> → <i>él bebe</i> → <b>bebe</b> agua. <i>escribir</i> → <i>él escribe</i> → <b>escribe</b> tu nombre.</p>"+
    "<p>Acht werkwoorden doen het anders, en die zijn de moeite van het uit je hoofd leren waard, want het zijn er precies acht: <b>haz, pon, ven, ten, di, sal, sé, ve</b> (hacer, poner, venir, tener, decir, salir, ser, ir).</p>"+
    "<p>En dan de valkuil: <b>ontkennend is het een heel andere vorm.</b> Niet <i>no corta</i> maar <i>no <b>cortes</b></i>, niet <i>no bebe</i> maar <i>no <b>bebas</b></i>. De -ar-werkwoorden krijgen -es, de -er- en -ir-werkwoorden -as. Precies andersom dan je verwacht.</p>",
  uitlegEn:"<p>The command form for <b>tú</b> is surprisingly easy in Spanish: take the form that goes with <i>él</i> in the present tense, and that is it.</p>"+
    "<p><i>cortar</i> → <i>él corta</i> → <b>corta</b> la cebolla. <i>beber</i> → <i>él bebe</i> → <b>bebe</b> agua. <i>escribir</i> → <i>él escribe</i> → <b>escribe</b> tu nombre.</p>"+
    "<p>Eight verbs do it differently, and they are worth memorising because there are exactly eight: <b>haz, pon, ven, ten, di, sal, sé, ve</b> (hacer, poner, venir, tener, decir, salir, ser, ir).</p>"+
    "<p>And then the trap: <b>the negative is a completely different form.</b> Not <i>no corta</i> but <i>no <b>cortes</b></i>, not <i>no bebe</i> but <i>no <b>bebas</b></i>. The -ar verbs take -es, the -er and -ir verbs take -as. Exactly the other way round from what you expect.</p>",
  begrip:{v:"Hoe maak je de bevestigende gebiedende wijs tegen tú?",
    vEn:"How do you make the affirmative command form for tú?",
    o:["Je neemt de él-vorm van de tegenwoordige tijd","Je neemt de infinitief zonder -r","Je neemt de tú-vorm van de tegenwoordige tijd","Je zet het werkwoord in de verleden tijd"],
    oEn:["You take the él form of the present tense","You take the infinitive without the -r","You take the tú form of the present tense","You put the verb in the past tense"],
    g:0,
    w:"Habla, come, escribe: dat zijn de él-vormen. De tú-vorm (hablas) is het net niet, en dat is de fout die het vaakst gemaakt wordt.",
    wEn:"Habla, come, escribe: those are the él forms. The tú form (hablas) is nearly right, and that is the most common slip."},
  patronen:[
   function(){ var w = gcKies(GC_IMP);
     return {v:"___ "+w.obj+". ("+w.geb+")", vEn:"___ "+w.obj+". ("+w.gebEn+")",
             o:[w.tu, w.inf, w.tu+"s"], g:0,
             w:"De \u00e9l-vorm van "+w.inf+" is "+w.tu+", en dat is de gebiedende wijs. "+w.tu+"s is de t\u00fa-vorm en betekent iets anders.",
             wEn:"The \u00e9l form of "+w.inf+" is "+w.tu+", and that is the command. "+w.tu+"s is the t\u00fa form and means something else."}; },
   function(){ var w = gcKies(GC_IMP_ONREG);
     return {v:"\u00a1___! ("+w.geb+") \u00b7 van "+w.inf,
             vEn:"\u00a1___! ("+w.gebEn+") \u00b7 from "+w.inf,
             o:[w.tu, w.inf.replace(/r$/, ""), w.inf], g:0,
             w:w.inf+" is een van de acht onregelmatige: "+w.tu+". Die acht zijn haz, pon, ven, ten, di, sal, s\u00e9, ve.",
             wEn:w.inf+" is one of the eight irregulars: "+w.tu+". The eight are haz, pon, ven, ten, di, sal, s\u00e9, ve."}; },
   function(){ var w = gcKies(GC_IMP);
     return {v:"___ "+w.obj+". ("+w.gebNeg+")", vEn:"___ "+w.obj+". ("+w.gebNegEn+")",
             o:[w.neg, "no "+w.tu, "no "+w.inf], g:0,
             w:"Ontkennend verandert de vorm: "+w.neg+", niet no "+w.tu+". Dat is de valkuil van dit onderwerp.",
             wEn:"The negative changes the form: "+w.neg+", not no "+w.tu+". That is the trap here."}; },
   function(){ var w = gcKies(GC_IMP);
     return {v:"Wat betekent \u00ab"+w.tu+" "+w.obj+"\u00bb?",
             vEn:"What does \u00ab"+w.tu+" "+w.obj+"\u00bb mean?",
             o:[w.geb+" (een opdracht)", w.hij, w.ik],
             oEn:[w.gebEn+" (a command)", w.hijEn, w.ikEn], g:0,
             w:"De vorm is dezelfde als de \u00e9l-vorm, dus de zin vertelt het je: geen onderwerp erbij en een opdracht, dus de gebiedende wijs. "+w.hij+" zou "+w.inf.replace(/r$/, "")+" zijn met \u00e9l erbij.",
             wEn:"The form is the same as the \u00e9l form, so the sentence tells you: no subject and an instruction means a command."}; },
   function(){ var w = gcKies(GC_IMP_ONREG);
     return {v:"Hoeveel werkwoorden hebben een onregelmatige t\u00fa-gebiedende wijs, zoals \u00ab"+w.tu+"\u00bb?",
             vEn:"How many verbs have an irregular t\u00fa command, like \u00ab"+w.tu+"\u00bb?",
             o:["Acht","Twee","Zoveel dat je ze niet kunt leren","Geen enkele"],
             oEn:["Eight","Two","So many you cannot learn them","None"], g:0,
             w:"Precies acht: haz, pon, ven, ten, di, sal, s\u00e9, ve. Een lijstje van acht is te leren, en daarmee is dit onderwerp af.",
             wEn:"Exactly eight: haz, pon, ven, ten, di, sal, s\u00e9, ve. A list of eight is learnable, and that finishes this topic."}; }
  ]},

'''

CORTES = r'''
 /* v23.193. Kaart 12 draagt tien toetsvragen over beleefd vragen en er stond geen les tegenover.
    Dit onderwerp is geen paradigma maar een handjevol vaste wendingen, en zo staat het er ook: de
    vraag is niet welke vorm maar hoe direct je klinkt. */
 {id:"cortesia", icon:"🙏", naam:"Beleefd iets vragen", naamEn:"Asking politely",
  corr:[], spiek:{a2:[12]}, wizard:null,
  uitleg:"<p>Met <i>puedes</i> vraag je gewoon of iets kan. Dat is niet onbeleefd, maar het is wel direct: <i>¿Puedes abrir la ventana?</i> is “kun je het raam openen?”.</p>"+
    "<p>Wil je zachter klinken, dan zet je er een <b>-ía</b> achter: <b>podría</b> (ik/hij/u) en <b>podrías</b> (jij). <i>¿Podrías abrir la ventana?</i> is “zou je het raam kunnen openen?”. Let op de stam: het is <i>podr-</i> en niet <i>poder-</i>.</p>"+
    "<p>Nog een stap beleefder is <b>¿Te importaría + infinitief?</b> — letterlijk “zou het je uitmaken om...”. <i>¿Te importaría repetir eso?</i> Tegen iemand die u is: <i>¿Le importaría...?</i></p>"+
    "<p>Na al deze vormen komt altijd een <b>infinitief</b>, nooit een vervoegd werkwoord: <i>¿Podrías traer la cuenta?</i>, nooit <i>¿Podrías traes...?</i></p>",
  uitlegEn:"<p>With <i>puedes</i> you simply ask whether something is possible. That is not rude, but it is direct: <i>¿Puedes abrir la ventana?</i> is “can you open the window?”.</p>"+
    "<p>To sound softer, add <b>-ía</b>: <b>podría</b> (I/he/you formal) and <b>podrías</b> (you). <i>¿Podrías abrir la ventana?</i> is “could you open the window?”. Note the stem: it is <i>podr-</i>, not <i>poder-</i>.</p>"+
    "<p>One step more polite is <b>¿Te importaría + infinitive?</b> — literally “would it bother you to...”. <i>¿Te importaría repetir eso?</i> To someone you address formally: <i>¿Le importaría...?</i></p>"+
    "<p>All these forms are followed by an <b>infinitive</b>, never a conjugated verb: <i>¿Podrías traer la cuenta?</i>, never <i>¿Podrías traes...?</i></p>",
  begrip:{v:"Wat komt er na podrías of te importaría?",
    vEn:"What comes after podrías or te importaría?",
    o:["Een infinitief: podrías traer","Een vervoegd werkwoord: podrías traes","Een verleden tijd: podrías trajiste","Een zelfstandig naamwoord, nooit een werkwoord"],
    oEn:["An infinitive: podrías traer","A conjugated verb: podrías traes","A past tense: podrías trajiste","A noun, never a verb"],
    g:0,
    w:"Net als na puedo en quiero: het tweede werkwoord blijft in de infinitief staan.",
    wEn:"Just as after puedo and quiero: the second verb stays in the infinitive."},
  patronen:[
   function(){ var c = gcKies(GC_CORTES);
     return {v:"\u00bf___ "+c.ww+" "+c.obj+"? ("+c.vraag+" \u2014 je wilt zacht klinken)",
             vEn:"\u00bf___ "+c.ww+" "+c.obj+"? ("+c.vraagEn+" \u2014 you want to sound soft)",
             o:["Podr\u00edas","Puedes","Podes"], g:0,
             w:"Puedes kan ook en is niet onbeleefd, maar podr\u00edas is de zachte vorm en daar vroeg de zin om. Podes bestaat niet in Spanje.",
             wEn:"Puedes works too and is not rude, but podr\u00edas is the soft form, and that is what the sentence asked for. Podes does not exist in Spain."}; },
   function(){ var c = gcKies(GC_CORTES);
     return {v:"\u00bfPodr\u00edas ___ "+c.obj+"? ("+c.vraag+")",
             vEn:"\u00bfPodr\u00edas ___ "+c.obj+"? ("+c.vraagEn+")",
             /* Twee opties, en allebei bestaande Spaanse woorden. Hier stond een derde afleider die
                uit het werkwoord werd gerekend ("trao"), en dat is geen Spaans: een afleider die
                niet bestaat is een gratis punt. */
             o:[c.ww, c.tu], g:0,
             w:"Na podr\u00edas komt de infinitief: "+c.ww+". Een vervoegde vorm kan daar niet staan.",
             wEn:"After podr\u00edas comes the infinitive: "+c.ww+". A conjugated form cannot go there."}; },
   function(){ var c = gcKies(GC_CORTES);
     return {v:"\u00bfTe ___ "+c.ww+" "+c.obj+"? (Zou het je uitmaken om "+c.te+"?)",
             vEn:"\u00bfTe ___ "+c.ww+" "+c.obj+"? (Would you mind "+c.teEn+"?)",
             o:["importar\u00eda","importas","importar"], g:0,
             w:"Te importar\u00eda + infinitief. Dit is de beleefdste van de drie vormen op deze kaart.",
             wEn:"Te importar\u00eda + infinitive. This is the most polite of the three forms on this card."}; },
   function(){
     return {v:"Je spreekt iemand aan met usted. Wat wordt het?",
             vEn:"You are addressing someone with usted. Which one?",
             o:["\u00bfPodr\u00eda ayudarme?","\u00bfPodr\u00edas ayudarme?","\u00bfPuedes ayudarme?","\u00bfPodr\u00e1n ayudarme?"],
             oEn:["\u00bfPodr\u00eda ayudarme?","\u00bfPodr\u00edas ayudarme?","\u00bfPuedes ayudarme?","\u00bfPodr\u00e1n ayudarme?"], g:0,
             w:"Usted gebruikt de derde persoon: podr\u00eda. Podr\u00edas is t\u00fa, en dat botst met de aanspreekvorm.",
             wEn:"Usted takes the third person: podr\u00eda. Podr\u00edas is t\u00fa, which clashes with the form of address."}; },
   function(){
     return {v:"Waar komt podr\u00eda vandaan?",
             vEn:"Where does podr\u00eda come from?",
             o:["podr- + \u00eda","poder- + \u00eda","pued- + \u00eda","pod- + \u00eda"],
             oEn:["podr- + \u00eda","poder- + \u00eda","pued- + \u00eda","pod- + \u00eda"], g:0,
             w:"Poder verliest zijn e: podr- + \u00eda. Pas op dat pod\u00eda iets anders is: dat is de imperfecto, \u201cik kon\u201d.",
             wEn:"Poder drops its e: podr- + \u00eda. Watch out: pod\u00eda is something else, the imperfect, \u201cI could\u201d."}; }
  ]},

'''

if DOE_APP:
    # de imperativo ná gerundio: je hebt de presente nodig om de vorm te maken
    rep(' {id:"apersonal", icon:', IMPERATIVO.lstrip("\n") + ' {id:"apersonal", icon:')
    # en de beleefdheidsvormen ná tuusted, want tú tegenover usted is de helft van het onderwerp
    rep(' {id:"futuroir", icon:', CORTES.lstrip("\n") + ' {id:"futuroir", icon:')

# =============================================================================================
# 3. en de vragen die er al waren maar niet te bereiken
#
# Gevonden doordat de nieuwe les cortesia op precies acht vragen bleef steken terwijl zijn patronen
# er zeventien kunnen maken. De oorzaak zit in gcMaakVragen() en raakt alle 25 concepten.
#
# De lus roteert over de patronen en telt `ronde` alleen op als er een NIEUWE vraag uit komt. Een
# patroon dat een vaste vraag maakt (bijvoorbeeld "Waar komt podría vandaan?") levert de tweede keer
# een duplicaat, en dan gaat de lus met `continue` terug zonder door te draaien. Hij blijft dus op
# datzelfde patroon staan tot de pogingenteller op is, en de patronen erachter komen nooit aan bod.
#
# GEMETEN, per concept elk patroon los uitgeput tegenover wat de generator werkelijk teruggeeft:
#
#   concept          mogelijk   bereikbaar
#   comparar              407            8      -399
#   serestar              170           99
#   hayestar              150           99
#   concordancia           99           34
#   perfindef              90           26
#   reflexivo              56           14
#   ...
#   indefimperf            20           11
#
#   totaal               1416          580      836 onbereikbaar, oftewel 59%
#
# Bijna zestig procent van de grammaticavragen die deze app kan stellen, stelt hij nooit. Dat is
# meer materiaal dan alle lessen van deze week bij elkaar, en het lag er al.
#
# De reparatie is één regel: draai de rotatie door bij elke poging in plaats van bij elke treffer.
# Een patroon dat leeg is wordt dan overgeslagen en de rest krijgt zijn beurt. De afspraak van
# v23.59 blijft staan: wie een concept voor het eerst doet begint nog steeds bij patroon nul.
# =============================================================================================
if DOE_APP:
    rep("  while(uit.length < n && poging < n * 25){\n"
        "    poging++;\n"
        "    var p = c.patronen[(start + ronde) % c.patronen.length];\n"
        "    var q = null;\n"
        "    try { q = p(); } catch(e){ q = null; }\n"
        "    if(!q || gezien[q.v]) continue;\n"
        "    gezien[q.v] = 1;\n"
        "    ronde++;\n"
        "    uit.push(gcSchud(q));\n"
        "  }",
        "  while(uit.length < n && poging < n * 25){\n"
        "    poging++;\n"
        "    var p = c.patronen[(start + ronde) % c.patronen.length];\n"
        "    /* v23.193: doordraaien bij elke poging, niet alleen bij elke treffer.\n"
        "\n"
        "       Hier stond ronde++ onderaan, na het opslaan. Een patroon dat een vaste vraag maakt\n"
        "       levert de tweede keer een duplicaat, en dan sprong de lus met continue terug zonder\n"
        "       door te draaien: hij bleef op datzelfde patroon staan tot de pogingenteller op was, en\n"
        "       alles erachter kwam nooit aan bod.\n"
        "\n"
        "       Gemeten over alle 25 concepten, elk patroon los uitgeput tegenover wat hier uitkwam:\n"
        "       1416 vragen mogelijk, 580 bereikbaar. 836 vragen, 59 procent, werden nooit gesteld.\n"
        "       Het ergst bij comparar (407 mogelijk, 8 bereikbaar) en bij perfindef (90 om 26), en\n"
        "       dat laatste is precies het onderwerp waar Stefan de meeste fouten op maakt.\n"
        "\n"
        "       De afspraak van v23.59 blijft: wie een concept voor het eerst doet begint bij patroon\n"
        "       nul, want start is dan nul en dit is de eerste doorgang. */\n"
        "    ronde++;\n"
        "    var q = null;\n"
        "    try { q = p(); } catch(e){ q = null; }\n"
        "    if(!q || gezien[q.v]) continue;\n"
        "    gezien[q.v] = 1;\n"
        "    uit.push(gcSchud(q));\n"
        "  }")

# =============================================================================================
# 3. de ezelsbruggen
# =============================================================================================
HULP = r''' imperativo:{
  kern:"Bevestigend tegen tú is de él-vorm van de presente: corta, bebe, escribe. Acht werkwoorden doen het anders: haz, pon, ven, ten, di, sal, sé, ve. Ontkennend is een andere vorm: no cortes, no bebas.",
  kernEn:"The affirmative tú command is the él form of the present: corta, bebe, escribe. Eight verbs differ: haz, pon, ven, ten, di, sal, sé, ve. The negative is a different form: no cortes, no bebas.",
  brug:"Bevestigend leen je van hem (él), ontkennend draai je de klinker om: -ar krijgt -es, -er en -ir krijgen -as. Precies andersom dan de tegenwoordige tijd.",
  brugEn:"Affirmative you borrow from him (él); negative you flip the vowel: -ar takes -es, -er and -ir take -as. Exactly the opposite of the present tense.",
  mis:"De fout die bijna iedereen maakt is de tú-vorm pakken: hablas in plaats van habla. En daarna no corta in plaats van no cortes, want ontkennend voelt als hetzelfde woord met no ervoor.",
  misEn:"The mistake nearly everyone makes is taking the tú form: hablas instead of habla. And then no corta instead of no cortes, because the negative feels like the same word with no in front."},
 cortesia:{
  kern:"Puedes vraagt of iets kan, podrías vraagt het zachter, te importaría is het beleefdst. Na alle drie komt een infinitief.",
  kernEn:"Puedes asks whether something is possible, podrías asks more softly, te importaría is the most polite. All three are followed by an infinitive.",
  brug:"De -ía is de zachte staart: hoe langer de staart, hoe beleefder. Puedes, podrías, te importaría.",
  brugEn:"The -ía is the soft tail: the longer the tail, the more polite. Puedes, podrías, te importaría.",
  mis:"Twee dingen. De stam is podr- en niet poder-, dus podría en nooit podería. En podía is iets heel anders: dat is de verleden tijd, niet de beleefde vorm.",
  misEn:"Two things. The stem is podr-, not poder-, so podría and never podería. And podía is something else entirely: that is the past tense, not the polite form."},
'''

if DOE_APP:
    rep("var GC_HULP = {\n", "var GC_HULP = {\n" + HULP)

# =============================================================================================
# 4. de naslag vangt op wat nog niet aan de beurt is
#
# Gevonden doordat pw-les7 rood werd: de spiekkaart van de imperativo was van de grammaticapagina
# verdwenen. Twee regels die allebei kloppen botsten:
#
#   v23.159  een kaart die een concept in zijn spiek-veld noemt, komt niet ook nog als automatisch
#            onderwerp in de route te staan. Anders staat "Wisselt de klinker mee?" naast
#            "Schoenwerkwoorden (klinkerwissel)"; er stonden er elf dubbel.
#   v19.98   de naslaglijst toont alleen kaarten waar geen onderwerp bij bestaat, zodat het een
#            vangnet is en geen kopie van de lijst erboven.
#
# Samen betekent dat: zodra een concept een kaart claimt, verdwijnt die kaart uit de route (want
# bezet) en uit de naslag (want er is een onderwerp). Zolang elk concept meteen open stond viel dat
# niet op. De imperativo staat op plek 15 van de leervolgorde, dus voor wie daar nog niet is, was de
# kaart nergens meer te vinden.
#
# Dat werkt precies de verkeerde kant op: elk gat dat de review dicht zou een stuk naslag onzichtbaar
# maken tot de les aan de beurt is.
#
# De reparatie zit in de naslag en niet in de route, want de dubbeling die v23.159 wegnam moet weg
# blijven. De vraag wordt: staat deze kaart ergens in de route? Zo niet, dan hoort hij in de naslag,
# of dat nu komt doordat er geen onderwerp is of doordat het onderwerp nog dicht zit.
# =============================================================================================
if DOE_APP:
    rep("  var wees = [];\n"
        "  CHEATSHEET.forEach(function(c, i){ if(!gwOnderwerpVoorSpiek(i)) wees.push(i); });",
        "  var wees = spiekWeesLijst();")

    # en de regel zelf, als één functie waar ook de poort naar kan vragen
    rep("function spiekNaslagHtml(){",
        "/* v23.193: welke spiekkaarten staan nergens in de route?\n"
        "\n"
        "   Dit stond als losse regel in spiekNaslagHtml() (\"geen onderwerp voor deze kaart\") en werd in\n"
        "   de poort nog een keer nagerekend. Twee plekken die hetzelfde bepalen, en ze zijn uit elkaar\n"
        "   gelopen zodra de regel veranderde. Nu is het één functie en vraagt de poort het hier.\n"
        "\n"
        "   De regel is ook veranderd, en dat is de reden dat deze functie er is. Hij was \"bestaat er een\n"
        "   onderwerp voor deze kaart\". Sinds v23.159 haalt een concept zijn kaart uit de route (tegen\n"
        "   dubbelingen), óók als dat concept nog tien onderwerpen verderop ligt: dan viel de kaart uit\n"
        "   de route én uit de naslag en was hij nergens meer te vinden. Dat gebeurde meteen bij de\n"
        "   eerste twee lessen die een gat in het curriculum dichtten.\n"
        "\n"
        "   De vraag is dus: staat deze kaart ergens op het scherm? Zo niet, dan hoort hij in de naslag,\n"
        "   of dat nu komt doordat er geen les is of doordat de les nog dicht zit. */\n"
        "function spiekWeesLijst(){\n"
        "  var inRoute = {}, tk = gwTrackKey();\n"
        "  try {\n"
        "    gwGenLijst().forEach(function(o){\n"
        "      var m = /^spiek-(?:a2|a0)-(\\d+)$/.exec(o && o.id);\n"
        "      if(m) inRoute[+m[1]] = 1;\n"
        "    });\n"
        "  } catch(e){}\n"
        "  GRAMWIZ.forEach(function(o){\n"
        "    ((o.spiek && o.spiek[tk]) || []).forEach(function(i){ inRoute[i] = 1; });\n"
        "  });\n"
        "  GC_CONCEPTEN.forEach(function(c){\n"
        "    var open = false;\n"
        "    try { open = gcConceptOpen(c.id); } catch(e){ open = true; }\n"
        "    if(!open) return;\n"
        "    ((c.spiek && c.spiek[tk]) || []).forEach(function(i){ inRoute[i] = 1; });\n"
        "  });\n"
        "  var uit = [];\n"
        "  CHEATSHEET.forEach(function(c, i){ if(!inRoute[i]) uit.push(i); });\n"
        "  return uit;\n"
        "}\n"
        "function spiekNaslagHtml(){")

# =============================================================================================
# 4. en in de leervolgorde
# =============================================================================================
if DOE_APP:
    rep('  "tuusted",         // tu of usted\n',
        '  "tuusted",         // tu of usted\n'
        '  "cortesia",        // v23.193: en meteen daarna hoe je het beleefd vraagt, want tu tegenover\n'
        '                     // usted is de helft van dat onderwerp\n')
    rep('  "gerundio",        // presente of estar + gerundio\n',
        '  "gerundio",        // presente of estar + gerundio\n'
        '  "imperativo",      // v23.193: na de presente, want de bevestigende tu-vorm IS de el-vorm\n'
        '                     // van de presente en de les legt hem daarmee uit\n')

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: twee lessen erbij (imperativo, cortesia), versie " + NIEUW)
else:
    print("index.html: stonden er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
