#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.83: de grammatica zegt geen onwaarheden meer, en de magere onderwerpen staan achteraan.

Stefan, 13 aug: "vijf commits allemaal live en morgen lanceren, zijn we er klaar voor?" Gemeten, en
het antwoord was nee. Niet vanwege de app maar vanwege vier generatoren die Nederlandse zinnen
maken die niet kloppen, en zes onderwerpen die maar één oefenzin kunnen produceren.

## Wat er gemeten is

Zestig trekkingen per concept uit gcMaakVragen(). Unieke vragen:

    pronombre 1 · tuusted 1 · negacion 1 · pedirpreguntar 1 · gerundio 1 · futuroir 1
    quecual 3 · saberpoder 3 · porpara 4 · indefimperf 6 · reflexivo 6 · saberconocer 6 · apersonal 6
    de overige tien: 8 of meer

En vier soorten zin die gewoon fout zijn:

    gustar         Me ___ la pregunta.    (Ik vind het vraag leuk.)
    concordancia   La pregunta es ___.    (Het vraag is blond.)
    comparar       Pablo es ___ simpático que Pablo.
    comparar       Tengo ___ ciudades como tú. (net zoveel staden als jij)

## 1. Het lidwoord was hardgecodeerd

Vijf plekken schreven "Het " of "het " voor s.nl, ongeacht welk woord erachter kwam. GC_SUST had
wel het Spaanse geslacht (g) maar niet het Nederlandse lidwoord, dus er was ook niets om mee te
kiezen. Dat staat er nu bij als `dl`, plus `mvnl` voor het Nederlandse meervoud, want "staden" en
"vraagen" kwamen uit s.nl + "en".

Dit is dezelfde soort fout als de lidwoorden in de Cervantes-brug van v23.78: de data wist het
antwoord niet, dus verzon de code er een. Het verschil is dat het hier acht woorden zijn en daar
1376.

## 2. Een vraag kan niet blond zijn

concordancia trok zijn bijvoeglijk naamwoord uit GC_ADJ_SER, en dat is een lijst voor personen:
rubio, tímido, generoso. Grammaticaal klopt "La pregunta es rubia" precies, en dat is nou juist het
gevaar: het onderwerp is verbuiging, dus de fout valt niet op in de vorm. Er is nu een aparte lijst
GC_ADJ_COSA (rojo, nuevo, pequeño, caro, viejo, grande, verde), en pregunta doet niet meer mee, want
een vraag is niet rood of duur. Die staat als `abs:1` in de lijst.

## 3. Pablo vergeleek zichzelf

Beide comparar-patronen zetten een gekozen persoon tegenover een hardgecodeerde "Pablo". Eén op de
zes keer is die persoon Pablo. De tweede persoon wordt nu apart gekozen, met de eerste eruit.

## 4. De magere onderwerpen naar achteren

Vier van de zes eenzins-onderwerpen staan vooraan: negacion op plek 5, tuusted op 7, futuroir op 8,
gerundio op 14. Met een venster van drie betekent dat een nieuwe gebruiker er in zijn eerste week
tegenaan loopt, en dan is elke herhaling letterlijk dezelfde zin.

Ze gaan naar het eind van GC_ORDE. Dat is een uitstel en geen reparatie, en dat hoort hier hardop te
staan: patronen bijschrijven is het echte werk en dat komt na de lancering. pedirpreguntar en
pronombre stonden al op plek 20 en 21 en blijven waar ze zijn.

De volgorde blijft compleet: pw-gramorde.js eist dat elk concept er precies één keer in staat en dat
elke voorwaarde in GC_VOOR eerder komt. Verplaatsen mag, weglaten niet.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.83"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.83" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_SUST = u'''var GC_SUST = [
 {es:"libro", nl:"boek", en:"book", g:"m"}, {es:"coche", nl:"auto", en:"car", g:"m"},
 {es:"piso", nl:"appartement", en:"flat", g:"m"}, {es:"perro", nl:"hond", en:"dog", g:"m"},
 {es:"casa", nl:"huis", en:"house", g:"f"}, {es:"pregunta", nl:"vraag", en:"question", g:"f"},
 {es:"ciudad", nl:"stad", en:"city", g:"f"}, {es:"mesa", nl:"tafel", en:"table", g:"f"}
];'''

N_SUST = u'''/* v23.83: dl en mvnl erbij. Vijf generatoren schreven "Het " voor s.nl, ongeacht het woord
   erachter, want er was geen Nederlands lidwoord om mee te kiezen: alleen g, het Spaanse geslacht.
   Zo ontstond "Het vraag is blond" en "net zoveel staden als jij". De data wist het antwoord niet,
   dus verzon de code er een - dezelfde soort fout als de ontbrekende lidwoorden in de
   Cervantes-brug (v23.78), alleen acht woorden groot in plaats van 1376.

   abs markeert wat geen kleur, prijs of formaat heeft. Een vraag is niet rood en niet duur, dus die
   doet niet mee bij concordancia. Bij gustar kan hij prima mee: een vraag leuk vinden kan wel. */
var GC_SUST = [
 {es:"libro", nl:"boek", en:"book", g:"m", dl:"het", mvnl:"boeken"},
 {es:"coche", nl:"auto", en:"car", g:"m", dl:"de", mvnl:"auto's"},
 {es:"piso", nl:"appartement", en:"flat", g:"m", dl:"het", mvnl:"appartementen"},
 {es:"perro", nl:"hond", en:"dog", g:"m", dl:"de", mvnl:"honden"},
 {es:"casa", nl:"huis", en:"house", g:"f", dl:"het", mvnl:"huizen"},
 {es:"pregunta", nl:"vraag", en:"question", g:"f", dl:"de", mvnl:"vragen", abs:1},
 {es:"ciudad", nl:"stad", en:"city", g:"f", dl:"de", mvnl:"steden"},
 {es:"mesa", nl:"tafel", en:"table", g:"f", dl:"de", mvnl:"tafels"}
];
/* Bijvoeglijke naamwoorden die bij een ding passen. GC_ADJ_SER is een lijst voor personen (rubio,
   tímido, generoso) en concordancia trok daaruit, met "La pregunta es rubia" tot gevolg.
   Grammaticaal klopt dat precies, en dat is juist het gevaar: het onderwerp is verbuiging, dus aan
   de vorm is niets te zien. */
var GC_ADJ_COSA = [
 {es:"rojo", nl:"rood", en:"red"}, {es:"nuevo", nl:"nieuw", en:"new"},
 {es:"pequeño", nl:"klein", en:"small"}, {es:"caro", nl:"duur", en:"expensive"},
 {es:"viejo", nl:"oud", en:"old"},
 {es:"grande", nl:"groot", en:"big", inv:1}, {es:"verde", nl:"groen", en:"green", inv:1}
];
/* Het Nederlandse lidwoord met een hoofdletter, voor aan het begin van een zin. */
function gcDlH(s){ var d = (s && s.dl) || "de"; return d.charAt(0).toUpperCase() + d.slice(1); }'''

A_ORDE_NEG = u'''  "negacion",        // no ... nada: een regel, geen keuze\n'''
A_ORDE_TU = u'''  "tuusted",         // tu of usted\n'''
A_ORDE_FUT = u'''  "futuroir",        // ir a + infinitief, je eerste toekomst\n'''
A_ORDE_GER = u'''  "gerundio",        // presente of estar + gerundio\n'''
A_ORDE_EIND = u'''  "indefimperf"      // indefinido of imperfecto
];'''

SITES = [
    # gustar
    (u'''     return {v:"Me ___ "+art+" "+s.es+". (Ik vind het "+s.nl+" leuk.)",''',
     u'''     return {v:"Me ___ "+art+" "+s.es+". (Ik vind "+(s.dl||"de")+" "+s.nl+" leuk.)",'''),
    # hayestar / estar-locatie, twee plekken met een eigen werkwoord
    (u'''     return {v:art+" "+s.es+" ___ "+l.es+". (Het "+s.nl+" is "+l.nl+".)",''',
     u'''     return {v:art+" "+s.es+" ___ "+l.es+". ("+gcDlH(s)+" "+s.nl+" is "+l.nl+".)",'''),
    (u'''     return {v:art+" "+s.es+" ___ "+l.es+". (Het "+s.nl+" staat "+l.nl+".)",''',
     u'''     return {v:art+" "+s.es+" ___ "+l.es+". ("+gcDlH(s)+" "+s.nl+" staat "+l.nl+".)",'''),
    # demostrativo
    (u'''     return {v:"Het "+s.nl+" ligt daar op jouw tafel. Welk woord kies je?",''',
     u'''     return {v:gcDlH(s)+" "+s.nl+" ligt daar op jouw tafel. Welk woord kies je?",'''),
    # comparar, het meervoud
    (u'''     return {v:"Tengo ___ "+mv+" como tú. (net zoveel "+s.nl+"en als jij)",''',
     u'''     return {v:"Tengo ___ "+mv+" como tú. (net zoveel "+(s.mvnl||s.nl)+" als jij)",'''),
]

A_CONC = u'''   function(){ var s = gcKies(GC_SUST), a = gcKies(GC_ADJ_SER.filter(function(x){ return !x.inv; })),
                   art = s.g === "f" ? "La" : "El", goed = gcAdj(a, s.g, "sg");
     return {v:art+" "+s.es+" es ___. (Het "+s.nl+" is "+a.nl+".)",'''

A_COMP1 = u'''   function(){ var p = gcKies(GC_PERS), a = gcKies(GC_ADJ_SER);
     return {v:p.es+" es ___ "+gcAdj(a, p.g, "sg")+" que Pablo. ("+p.nl+" is "+a.nl+"er)",
             vEn:p.es+" es ___ "+gcAdj(a, p.g, "sg")+" que Pablo. ("+p.en+" is more "+a.en+")",'''

A_COMP2 = u'''   function(){ var p = gcKies(GC_PERS), a = gcKies(GC_ADJ_SER);
     return {v:p.es+" es tan "+gcAdj(a, p.g, "sg")+" ___ Pablo. (net zo "+a.nl+" als)",
             vEn:p.es+" es tan "+gcAdj(a, p.g, "sg")+" ___ Pablo. (just as "+a.en+" as)",'''

if DOE_APP:
    ontbreekt = []
    for naam, anker in [("GC_SUST", A_SUST), ("concordancia", A_CONC), ("comparar 1", A_COMP1),
                        ("comparar 2", A_COMP2), ("het eind van GC_ORDE", A_ORDE_EIND),
                        ("negacion in GC_ORDE", A_ORDE_NEG), ("tuusted in GC_ORDE", A_ORDE_TU),
                        ("futuroir in GC_ORDE", A_ORDE_FUT), ("gerundio in GC_ORDE", A_ORDE_GER)]:
        if anker not in src:
            ontbreekt.append(naam)
    for oud, _ in SITES:
        if oud not in src:
            ontbreekt.append(oud.strip()[:50])
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.82. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_SUST, N_SUST)

    for oud, nw in SITES:
        rep(oud, nw)

    rep(A_CONC, u'''   /* v23.83: GC_ADJ_COSA in plaats van GC_ADJ_SER, en geen abstracte zelfstandige naamwoorden.
      Hier stond "La pregunta es ___. (Het vraag is blond.)": twee fouten in één zin, en allebei
      onzichtbaar voor wie het onderwerp nog leert. */
   function(){ var s = gcKies(GC_SUST.filter(function(x){ return !x.abs; })),
                   a = gcKies(GC_ADJ_COSA.filter(function(x){ return !x.inv; })),
                   art = s.g === "f" ? "La" : "El", goed = gcAdj(a, s.g, "sg");
     return {v:art+" "+s.es+" es ___. ("+gcDlH(s)+" "+s.nl+" is "+a.nl+".)",''')

    # comparar: de tweede persoon apart kiezen, en niet dezelfde als de eerste
    rep(A_COMP1, u'''   /* v23.83: de tweede persoon werd hardgecodeerd op Pablo terwijl de eerste uit GC_PERS kwam.
      Eén op de zes keer stond er dus "Pablo es más simpático que Pablo". */
   function(){ var p = gcKies(GC_PERS), a = gcKies(GC_ADJ_SER),
                   q = gcKies(GC_PERS.filter(function(x){ return x.es !== p.es; }));
     return {v:p.es+" es ___ "+gcAdj(a, p.g, "sg")+" que "+q.es+". ("+p.nl+" is "+a.nl+"er dan "+q.nl+")",
             vEn:p.es+" es ___ "+gcAdj(a, p.g, "sg")+" que "+q.es+". ("+p.en+" is more "+a.en+" than "+q.en+")",''')

    rep(A_COMP2, u'''   function(){ var p = gcKies(GC_PERS), a = gcKies(GC_ADJ_SER),
                   q = gcKies(GC_PERS.filter(function(x){ return x.es !== p.es; }));
     return {v:p.es+" es tan "+gcAdj(a, p.g, "sg")+" ___ "+q.es+". (net zo "+a.nl+" als "+q.nl+")",
             vEn:p.es+" es tan "+gcAdj(a, p.g, "sg")+" ___ "+q.es+". (just as "+a.en+" as "+q.en+")",''')

    # de vier magere onderwerpen naar achteren
    for anker in (A_ORDE_NEG, A_ORDE_TU, A_ORDE_FUT, A_ORDE_GER):
        rep(anker, u"")
    rep(A_ORDE_EIND, u'''  "indefimperf",     // indefinido of imperfecto
  /* v23.83, en dit is uitstel en geen reparatie. Deze vier leveren elk precies één unieke oefenzin
     op zestig trekkingen: hun patroonlijst bestaat uit een handvol vaste zinnen in plaats van een
     generator. Vooraan (plek 5, 7, 8 en 14) betekende dat een nieuwe gebruiker in zijn eerste week
     een onderwerp kreeg waarvan elke herhaling letterlijk dezelfde zin is. Achteraan koop je tijd
     om er echte patronen bij te schrijven. Weglaten mag niet: pw-gramorde.js eist dat elk concept
     precies één keer in deze rij staat, en dat is precies de bedoeling. */
  "negacion",        // no ... nada
  "tuusted",         // tu of usted
  "futuroir",        // ir a + infinitief
  "gerundio"         // presente of estar + gerundio
];''')

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
