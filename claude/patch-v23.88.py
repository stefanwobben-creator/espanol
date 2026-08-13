#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.88: vier grammatica-onderwerpen krijgen echte generatoren, en v23.83 draait deels terug.

## Eerst de correctie, want ik heb me vergist

Gisteren meldde ik: "zes onderwerpen leveren precies één unieke oefenzin op zestig trekkingen". Dat
was een meetfout, en hij zat in mijn eigen proef.

gcMaakVragen(c, n) roteert over de patronen en begint bij patroon nul voor wie het onderwerp nog
nooit deed. Ik riep hem zestig keer aan met n=1, op een verse pagina zonder geschiedenis. Dus zestig
keer patroon nul. De concepten die "8" scoorden, scoorden dat alleen omdat hún patroon nul toevallig
een gcKies() bevat en dus vanbinnen varieert.

Zo gemeten als een gebruiker ze krijgt (twaalf rondes van vijf vragen):

    pronombre        5        saberpoder      12        genero          28
    tuusted          5        gerundio        14        zapato          29
    negacion         5        quecual         15        reflexivo       31
    pedirpreguntar   5        saberconocer    16        comparar        33
    futuroir         8        porpara         20        demostrativo    34
                              indefimperf     20        concordancia    40
                              apersonal       20        perfindef       43
                              gustar          24        hayestar        44
                              muymucho        26        serestar        51

Vier onderwerpen zitten echt vast op vijf: hun vijf patronen zijn allemaal een vaste zin zonder één
gcKies(). Wie zo'n onderwerp één keer doet, heeft het uitgeput; elke herhaling daarna is een
herhaling in de letterlijke zin.

Maar gerundio (14) en futuroir (8) zijn dat niet, en die heb ik in v23.83 wél naar achteren
geschoven in GC_ORDE. Dat was een ingreep op een verkeerde meting. Gerundio zit met 14 boven
saberpoder en quecual, die gewoon bleven staan.

Dit is de derde meetfout in deze reeks waarbij de meting stuk was en niet de code (de TTS-proef die
window.speechSynthesis overschreef, de \b-regex die door de shell werd opgegeten, en nu deze). De
eerste twee kostten alleen tijd. Deze heeft een verandering opgeleverd die niet had gemoeten.

## Wat deze patch doet

**1. Vier onderwerpen krijgen er drie generatoren bij.** De bestaande vijf vaste patronen blijven
staan en blijven vooraan, want die volgorde is bewust: wie een onderwerp voor het eerst doet begint
bij patroon nul, en dat hoort de regel te zijn en niet de uitzondering (zie de opmerking bij
gcMaakVragen, v23.59). De generatoren komen erachter, voor wie terugkomt.

    negacion         no ... nada/nadie met GC_LUGAR, nunca vóór het werkwoord met GC_YO,
                     en nada-of-algo na een ontkenning
    tuusted          tiene/tienes met GC_SUST, es/eres met GC_PROF, en een situatiekeuze
    pronombre        lo/la dat meebuigt met GC_SUST, le bij een persoon, los/las in het meervoud
    pedirpreguntar   pedir bij een ding, preguntar bij een vraag, pide/pregunta bij een persoon

De pronombre-generator is de belangrijkste van de vier: lo of la kiezen op het geslacht van het
zelfstandig naamwoord ís het onderwerp, en dat kon je met vijf vaste zinnen niet oefenen.

**2. GC_ORDE gaat terug zoals het was.** Alle vier de verplaatste onderwerpen keren terug naar hun
oude plek, want na deze patch is er geen enkele reden meer om ze weg te houden en voor gerundio en
futuroir was die reden er nooit.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.88"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.88" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

# ---- ankers ----------------------------------------------------------------

A_HELPERS = '''function gcMv(s){ return /[aeiou]$/.test(s) ? s + "s" : s + "es"; }'''

A_ORDE = '''  "negacion",        // no ... nada
  "tuusted",         // tu of usted
  "futuroir",        // ir a + infinitief
  "gerundio"         // presente of estar + gerundio
];'''

# Elk van de vier: het laatste patroon van het concept, gevolgd door de sluithaak van patronen.
# We haken aan op de sluithaak van het pátroonblok, en die is per concept uniek te maken door er
# de eerste regel van het volgende veld bij te nemen.
STOPPERS = {}

if DOE_APP:
    ontbreekt = [n for n, a in (("gcMv", A_HELPERS), ("de staart van GC_ORDE", A_ORDE)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.87. Eerst bijtrekken:\n\n    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


def voeg_patronen_toe(cid, code):
    """Zet extra patronen achter de bestaande van dit concept.

    Het anker is het einde van het patronen-blok van precies dit concept: we zoeken vanaf
    id:"<cid>", icon: naar de eerste regel die exact "  ]," of "  ]}," is op patroon-niveau. Dat is
    steviger dan de laatste zin van het laatste patroon uitschrijven, want die tekst verandert nog
    weleens, en het faalt hard als er iets niet klopt."""
    global src
    kop = 'id:"%s", icon:' % cid
    i = src.index(kop)
    j = src.index("  patronen:[", i)
    # tel haken vanaf de openende [ van patronen
    k = src.index("[", j + len("  patronen:"))
    diepte, m = 0, k
    while m < len(src):
        c = src[m]
        if c == "[":
            diepte += 1
        elif c == "]":
            diepte -= 1
            if diepte == 0:
                break
        m += 1
    assert diepte == 0, "patronen-blok van %s is niet gebalanceerd" % cid
    src = src[:m] + ",\n" + code + "\n  " + src[m:]


if DOE_APP:
    # ---- nieuwe woordenlijstjes -------------------------------------------
    rep(A_HELPERS, A_HELPERS + '''
/* v23.88: lijstjes voor de vier onderwerpen die tot nu toe alleen vaste zinnen hadden. Zie de kop
   van claude/patch-v23.88.py: die vier leverden precies vijf oefenzinnen op, en daarmee is het
   onderwerp na één ronde uitgeput. */
var GC_NEG = [
 {es:"nada", nl:"niets", ding:1}, {es:"nadie", nl:"niemand", ding:0}
];
/* Situaties waarin je tú of usted kiest. g is het goede antwoord: 0 = usted, 1 = tú. De regel is
   niet "formeel is usted" maar "wie je niet kent en wie ouder of in functie is, krijgt usted, en je
   wacht tot de ander overschakelt". */
var GC_TUSITUATIE = [
 {nl:"Je meldt je bij de balie van een ziekenhuis.", en:"You report at a hospital reception desk.", g:0},
 {nl:"Je vraagt een oudere buurvrouw of ze hulp nodig heeft.", en:"You ask an elderly neighbour if she needs help.", g:0},
 {nl:"Je praat met een kind van acht op straat.", en:"You are talking to an eight-year-old in the street.", g:1},
 {nl:"Je vriend stelt je voor aan zijn zus van jouw leeftijd.", en:"Your friend introduces you to his sister, your age.", g:1},
 {nl:"Je belt met een medewerker van de bank.", en:"You are on the phone with a bank employee.", g:0},
 {nl:"Je zit op een terras naast iemand van je eigen leeftijd.", en:"You are on a terrace next to someone your own age.", g:1}
];
/* Dingen waar je in het echt om vraagt. GC_SUST is hier te algemeen: "Voy a pedir el perro" en
   "Voy a pedir la ciudad" zijn geen Spaans maar ook geen Nederlands, en dat zag ik pas toen ik de
   gegenereerde zinnen las. Derde keer deze week dat een eigen lijstje per generator het antwoord
   is; zie GC_ADJ_COSA (v23.83) en plek/hand (v23.84). */
var GC_PEDIR = [
 {es:"la cuenta", nl:"de rekening", en:"the bill"},
 {es:"el men\u00fa", nl:"de kaart", en:"the menu"},
 {es:"la llave", nl:"de sleutel", en:"the key"},
 {es:"un caf\u00e9", nl:"een koffie", en:"a coffee"},
 {es:"ayuda", nl:"hulp", en:"help"}
];''')

    # ---- negacion ----------------------------------------------------------
    voeg_patronen_toe("negacion", '''   /* v23.88: drie generatoren erbij. Hierboven staan vijf vaste zinnen, en die blijven vooraan
      staan omdat wie dit onderwerp voor het eerst doet bij patroon nul begint (zie gcMaakVragen).
      Deze drie zijn voor wie terugkomt. */
   function(){ var n = gcKies(GC_NEG), l = gcKies(GC_LUGAR);
     return {v:"___ hay "+n.es+" "+l.es+". (Er is "+n.nl+" "+l.nl+".)",
             vEn:"___ hay "+n.es+" "+l.es+". (There is "+(n.ding?"nothing":"nobody")+" "+l.en+".)",
             o:["No","(niets)"], oEn:["No","(nothing)"], g:0,
             w:n.es+" staat achter het werkwoord, en dan is no verplicht. Twee ontkenningen is in het Spaans gewoon één ontkenning.",
             wEn:n.es+" comes after the verb, so no is required. Two negatives in Spanish make one negation."}; },
   function(){ var y = gcKies(GC_YO);
     return {v:"Nunca ___ los domingos. ("+y.nl+" nooit op zondag.)",
             vEn:"Nunca ___ los domingos. ("+y.en+" never on Sundays.)",
             o:[y.es, "no "+y.es], g:0,
             w:"Nunca staat hier vóór het werkwoord, en dan valt de no juist weg. Achter het werkwoord zou het no "+y.es+" nunca zijn.",
             wEn:"Here nunca comes before the verb, and then the no drops out. After the verb it would be no "+y.es+" nunca."}; },
   function(){ var l = gcKies(GC_LUGAR);
     return {v:gcHoofd(l.es)+" no hay ___. ("+gcHoofd(l.nl)+" is niets.)",
             vEn:gcHoofd(l.es)+" no hay ___. (There is nothing "+l.en+".)",
             o:["nada","algo"], g:0,
             w:"Na no hoort het ontkennende woord: no hay nada. No hay algo bestaat niet.",
             wEn:"After no you need the negative word: no hay nada. No hay algo does not exist."}; }''')

    # ---- tuusted -----------------------------------------------------------
    voeg_patronen_toe("tuusted", '''   /* v23.88: drie generatoren erbij, waarvan de derde de eigenlijke vraag stelt: niet welke vorm
      hoort bij usted, maar wanneer je usted kiest. */
   function(){ var s = gcKies(gcOpPlek()), art = s.g === "f" ? "la" : "el";
     return {v:"\\u00bf___ usted "+art+" "+s.es+"? (Heeft u "+(s.dl||"de")+" "+s.nl+"?)",
             vEn:"\\u00bf___ usted "+art+" "+s.es+"? (Do you have the "+s.en+"? Formal.)",
             o:["tiene","tienes"], g:0,
             w:"Usted neemt de vorm van \\u00e9l en ella: tiene. Tienes hoort bij t\\u00fa.",
             wEn:"Usted takes the \\u00e9l and ella form: tiene. Tienes belongs to t\\u00fa."}; },
   function(){ var pr = gcKies(GC_PROF);
     return {v:"\\u00bf___ usted "+pr.m+"? (Bent u "+pr.nl+"?)",
             vEn:"\\u00bf___ usted "+pr.m+"? (Are you "+pr.en+"? Formal.)",
             o:["es","eres"], g:0,
             w:"Bij usted hoort es, de vorm van \\u00e9l en ella. Eres hoort bij t\\u00fa.",
             wEn:"Usted goes with es, the \\u00e9l and ella form. Eres belongs to t\\u00fa."}; },
   function(){ var sit = gcKies(GC_TUSITUATIE);
     return {v:sit.nl+" Wat gebruik je?", vEn:sit.en+" What do you use?",
             o:["usted","t\\u00fa"], g:sit.g,
             w:sit.g === 0
               ? "Iemand die je niet kent, ouder is of in functie is, krijgt usted. Je wacht tot de ander overschakelt."
               : "Leeftijdsgenoten, kinderen en vrienden van vrienden krijgen t\\u00fa. Usted zou hier afstandelijk klinken.",
             wEn:sit.g === 0
               ? "Someone you don't know, who is older or acting in a role, gets usted. You wait for them to switch."
               : "People your own age, children and friends of friends get t\\u00fa. Usted would sound distant here."}; }''')

    # ---- pronombre ---------------------------------------------------------
    voeg_patronen_toe("pronombre", '''   /* v23.88: drie generatoren erbij. De eerste is de belangrijkste van deze hele patch: lo of la
      kiezen op het geslacht van het zelfstandig naamwoord \\u00eds dit onderwerp, en met vijf vaste
      zinnen kon je daar niet op oefenen. */
   function(){ var s = gcKies(gcOpPlek()), art = s.g === "f" ? "la" : "el";
     return {v:"\\u00bfVes "+art+" "+s.es+"? S\\u00ed, ___ veo. (Zie je "+(s.dl||"de")+" "+s.nl+"? Ja, ik zie "+(s.dl === "het" ? "het" : "hem")+".)",
             vEn:"\\u00bfVes "+art+" "+s.es+"? S\\u00ed, ___ veo. (Do you see the "+s.en+"? Yes, I see it.)",
             o:["lo","la"], g:(s.g === "f" ? 1 : 0),
             w:s.es+" is "+(s.g === "f" ? "vrouwelijk, dus la" : "mannelijk, dus lo")+". Het voornaamwoord buigt mee met het woord dat het vervangt, niet met jou.",
             wEn:s.es+" is "+(s.g === "f" ? "feminine, so la" : "masculine, so lo")+". The pronoun agrees with the word it replaces, not with you."}; },
   function(){ var p = gcKies(GC_PERS);
     return {v:"___ doy el libro a "+gcKleinEs(p)+". (Ik geef "+gcKlein(p)+" het boek.)",
             vEn:"___ doy el libro a "+gcKleinEs(p)+". (I give "+gcKleinEn(p)+" the book.)",
             o:["Le","Lo"], g:0,
             w:"Aan wie je iets geeft is het meewerkend voorwerp, en dat is le. Lo zou het boek zelf zijn.",
             wEn:"The person you give something to is the indirect object: le. Lo would be the book itself."}; },
   function(){ var s = gcKies(gcOpPlek()), mv = gcMv(s.es);
     return {v:"\\u00bfCompras los "+mv+"? S\\u00ed, ___ compro. (Koop je de "+(s.mvnl||s.nl)+"? Ja, ik koop ze.)",
             vEn:"\\u00bfCompras los "+mv+"? S\\u00ed, ___ compro. (Are you buying the "+s.en+"s? Yes, I'm buying them.)",
             o:["los","las"], g:(s.g === "f" ? 1 : 0),
             w:"Meervoud van "+(s.g === "f" ? "la wordt las" : "lo wordt los")+". Geslacht en aantal komen allebei van het woord dat je vervangt.",
             wEn:"The plural of "+(s.g === "f" ? "la is las" : "lo is los")+". Gender and number both come from the word you replace."}; }''')

    # ---- pedirpreguntar ----------------------------------------------------
    voeg_patronen_toe("pedirpreguntar", '''   /* v23.88: drie generatoren erbij. Het verschil is niet formeel maar praktisch: pedir gaat over
      een ding dat je wil hebben, preguntar over iets dat je wil weten. */
   function(){ var s = gcKies(GC_PEDIR);
     return {v:"Voy a ___ "+s.es+". (Ik ga om "+s.nl+" vragen.)",
             vEn:"Voy a ___ "+s.es+". (I'm going to ask for "+s.en+".)",
             o:["pedir","preguntar"], g:0,
             w:"Je vraagt om een d\\u00edng, dus pedir. Preguntar is vragen naar iets dat je wil weten.",
             wEn:"You are asking for a thing, so pedir. Preguntar is asking about something you want to know."}; },
   function(){ var l = gcKies(GC_LUGAR);
     return {v:"Voy a ___ d\\u00f3nde est\\u00e1 la parada. (Ik ga vragen waar de halte is.)",
             vEn:"Voy a ___ d\\u00f3nde est\\u00e1 la parada. (I'm going to ask where the stop is.)",
             o:["preguntar","pedir"], g:0,
             w:"Je wil iets w\\u00e9ten, dus preguntar. Na pedir hoort een ding, niet een vraagzin.",
             wEn:"You want to know something, so preguntar. Pedir is followed by a thing, not a question."}; },
   function(){ var p = gcKies(GC_PERS);
     return {v:p.es+" me ___ la hora. ("+p.nl+" vraagt me hoe laat het is.)",
             vEn:p.es+" me ___ la hora. ("+p.en+" asks me what time it is.)",
             o:["pregunta","pide"], g:0,
             w:"Hoe laat het is wil je weten, dus preguntar. Me pide la hora zou betekenen dat hij jouw tijd komt halen.",
             wEn:"What time it is, is something you want to know, so preguntar. Me pide la hora would mean he's asking you to hand over the time."}; }''')

    # ---- GC_ORDE terug zoals het was --------------------------------------
    rep(A_ORDE, '''  /* v23.88: hier stonden negacion, tuusted, futuroir en gerundio, in v23.83 naar achteren
     geschoven omdat ze "maar \\u00e9\\u00e9n oefenzin" zouden hebben. Dat was een meetfout: gcMaakVragen
     begint bij patroon nul voor wie het onderwerp nog nooit deed, en ik riep hem zestig keer met
     n=1 aan op een verse pagina. Dus zestig keer hetzelfde patroon.

     Zo gemeten als een gebruiker ze krijgt, gaven gerundio er 14 en futuroir er 8. Die hadden hier
     dus nooit moeten staan. negacion en tuusted zaten wél vast op vijf, en dat is nu opgelost met
     echte generatoren. Alle vier gaan terug naar hun oude plek. */
];''')

    for anker, plek in (
        ('  "negacion",        // no ... nada: een regel, geen keuze\n', None),
        ('  "tuusted",         // tu of usted\n', None),
        ('  "futuroir",        // ir a + infinitief, je eerste toekomst\n', None),
        ('  "gerundio",        // presente of estar + gerundio\n', None)):
        pass  # zie hieronder: de oude regels zijn in v23.83 verwijderd en worden hier teruggezet

    rep('''  "hayestar",        // hay of esta, een aftakking van estar
''', '''  "hayestar",        // hay of esta, een aftakking van estar
  "negacion",        // no ... nada: een regel, geen keuze
''')
    rep('''  "muymucho",        // muy of mucho: kijk naar het woord erachter
''', '''  "muymucho",        // muy of mucho: kijk naar het woord erachter
  "tuusted",         // tu of usted
  "futuroir",        // ir a + infinitief, je eerste toekomst
''')
    rep('''  "comparar",        // mas que, tan como
''', '''  "comparar",        // mas que, tan como
  "gerundio",        // presente of estar + gerundio
''')

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
