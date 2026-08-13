#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.84: de rest van wat de generatoren beweerden en niet waar was.

v23.83 haalde vier soorten onzin weg, en de meting daarna liet zien dat er nog vier over waren.
Precies daarom staat er in dit project steeds "meten slaat redeneren": elke ronde legt de volgende
laag bloot, en die zie je niet door naar de code te kijken.

    hayestar       En la cocina ___ una ciudad.   (In de keuken is een stad.)
    hayestar       en la oficina ___ un perro.    (kleine letter aan het begin)
    demostrativo   ___ mesa que tengo en la mano. (deze tafel hier bij mij)
    comparar       Mi hermano es ___ alto que Mi jefe. (dan Mijn baas)
    comparar       Ana es ___ inteligente que Marta. (Ana is slimer dan Marta)

## 1. Niet alles past in een keuken of in een hand

GC_SUST is één lijst voor alle generatoren, en die generatoren stellen verschillende eisen. Een stad
kan geen plaats innemen in een keuken; een tafel kan niet in je hand. Er staan nu twee vlaggen bij:
`plek` (kan ergens staan) en `hand` (kan je vasthouden). Boek is allebei, auto en hond en tafel
alleen plek, en huis, appartement, stad en vraag geen van beide.

Dat is dezelfde ingreep als `abs` in v23.83, en dat het er nu twee keer achter elkaar bij moet
zeggen iets: één woordenlijst die alle contexten moet bedienen, is een lijst die in elke context
een beetje verkeerd is. Wat hier eigenlijk hoort is per generator een eigen selectie, en dat is wat
deze vlaggen nu mogelijk maken.

## 2. Een zin begint met een hoofdletter

Eén hay-patroon zette de plaats vooraan en liet die met een kleine letter beginnen: "en la cocina
___ un perro." Het Spaans is goed, de zin ziet er alleen uit alsof hij half is. gcHoofd() bestond al
en werd er in de Nederlandse vertaling al gebruikt, alleen niet in het Spaans.

## 3. Mijn baas hoort niet halverwege met een hoofdletter

Dit is er eentje van mezelf, uit v23.83. Ik liet de tweede persoon uit GC_PERS komen in plaats van
hardgecodeerd Pablo, en die namen staan in de lijst zoals ze aan het begin van een zin horen:
"Mijn baas". Halverwege wordt dat "dan Mijn baas". Nu wordt de eerste letter klein gemaakt bij alles
wat geen eigennaam is, en dat is te zien aan het Spaans: "Mi " ervoor betekent geen naam.

## 4. Slimer

`a.nl + "er"` maakt de vergrotende trap, en dat gaat goed voor lang, aardig, blond, slank, verlegen
en vriendelijk. Niet voor slim en gul, waar de medeklinker verdubbelt: slimmer, guller. Die twee
staan er nu bij als `nlc`.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.84"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.84" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_SUST = u''' {es:"libro", nl:"boek", en:"book", g:"m", dl:"het", mvnl:"boeken"},
 {es:"coche", nl:"auto", en:"car", g:"m", dl:"de", mvnl:"auto's"},
 {es:"piso", nl:"appartement", en:"flat", g:"m", dl:"het", mvnl:"appartementen"},
 {es:"perro", nl:"hond", en:"dog", g:"m", dl:"de", mvnl:"honden"},
 {es:"casa", nl:"huis", en:"house", g:"f", dl:"het", mvnl:"huizen"},
 {es:"pregunta", nl:"vraag", en:"question", g:"f", dl:"de", mvnl:"vragen", abs:1},
 {es:"ciudad", nl:"stad", en:"city", g:"f", dl:"de", mvnl:"steden"},
 {es:"mesa", nl:"tafel", en:"table", g:"f", dl:"de", mvnl:"tafels"}
];'''

N_SUST = u''' /* v23.84: plek en hand. Eén lijst bedient alle generatoren en die stellen verschillende eisen:
    een stad staat niet in een keuken en een tafel past niet in je hand. Dat het er nu twee keer
    achter elkaar bij moet (abs in v23.83, deze twee nu) zegt iets: een woordenlijst die alle
    contexten bedient, is in elke context een beetje verkeerd. */
 {es:"libro", nl:"boek", en:"book", g:"m", dl:"het", mvnl:"boeken", plek:1, hand:1},
 {es:"coche", nl:"auto", en:"car", g:"m", dl:"de", mvnl:"auto's", plek:1},
 {es:"piso", nl:"appartement", en:"flat", g:"m", dl:"het", mvnl:"appartementen"},
 {es:"perro", nl:"hond", en:"dog", g:"m", dl:"de", mvnl:"honden", plek:1},
 {es:"casa", nl:"huis", en:"house", g:"f", dl:"het", mvnl:"huizen"},
 {es:"pregunta", nl:"vraag", en:"question", g:"f", dl:"de", mvnl:"vragen", abs:1},
 {es:"ciudad", nl:"stad", en:"city", g:"f", dl:"de", mvnl:"steden"},
 {es:"mesa", nl:"tafel", en:"table", g:"f", dl:"de", mvnl:"tafels", plek:1}
];
/* Alles wat ergens kan staan, en alles wat je kunt vasthouden. Twee aparte vragen, dus twee
   aparte functies; wie er later een woord bij zet, hoeft alleen de vlaggen goed te zetten. */
function gcOpPlek(){ return GC_SUST.filter(function(x){ return x.plek; }); }
function gcInHand(){ return GC_SUST.filter(function(x){ return x.hand; }); }
/* Halverwege een zin hoort "Mijn baas" klein. Eigennamen niet, en die zijn te herkennen aan het
   Spaans: "Mi " ervoor betekent geen naam. */
function gcKlein(p){
  var n = String((p && p.nl) || "");
  return /^Mi /.test(String((p && p.es) || "")) ? n.charAt(0).toLowerCase() + n.slice(1) : n;
}
function gcKleinEn(p){
  var n = String((p && p.en) || "");
  return /^My /.test(n) ? n.charAt(0).toLowerCase() + n.slice(1) : n;
}
/* De vergrotende trap. a.nl + "er" klopt voor lang, aardig, blond, slank, verlegen en vriendelijk,
   maar niet voor slim en gul: daar verdubbelt de medeklinker. Die twee dragen hun eigen vorm. */
function gcVergroot(a){ return (a && a.nlc) || ((a && a.nl) || "") + "er"; }'''

A_ADJ = u''' {es:"inteligente", nl:"slim", en:"clever", inv:1}, {es:"amable", nl:"vriendelijk", en:"kind", inv:1}'''
N_ADJ = u''' {es:"inteligente", nl:"slim", en:"clever", inv:1, nlc:"slimmer"}, {es:"amable", nl:"vriendelijk", en:"kind", inv:1}'''

A_GUL = u'''{es:"generoso", nl:"gul", en:"generous"},'''
N_GUL = u'''{es:"generoso", nl:"gul", en:"generous", nlc:"guller"},'''

# hay: de plaats vooraan, met een kleine letter, en met een zelfstandig naamwoord dat er niet past
A_HAY = u'''     return {v:l.es+" ___ "+art+" "+s.es+". ("+gcHoofd(l.nl)+" is een "+s.nl+".)",
             vEn:l.es+" ___ "+art+" "+s.es+". (There is a "+s.en+" "+l.en+".)",'''
N_HAY = u'''     /* v23.84: gcHoofd ook op het Spaans (hier stond "en la cocina ___ un perro." met een kleine
        letter), en alleen zelfstandige naamwoorden die ergens kunnen staan. */
     return {v:gcHoofd(l.es)+" ___ "+art+" "+s.es+". ("+gcHoofd(l.nl)+" is een "+s.nl+".)",
             vEn:gcHoofd(l.es)+" ___ "+art+" "+s.es+". (There is a "+s.en+" "+l.en+".)",'''

A_MANO = u'''     return {v:"___ "+s.es+" que tengo en la mano. (dit/deze "+s.nl+" hier bij mij)",'''
N_MANO = u'''     return {v:"___ "+s.es+" que tengo en la mano. (dit/deze "+s.nl+" hier bij mij)",'''

A_COMP1 = u'''     return {v:p.es+" es ___ "+gcAdj(a, p.g, "sg")+" que "+q.es+". ("+p.nl+" is "+a.nl+"er dan "+q.nl+")",
             vEn:p.es+" es ___ "+gcAdj(a, p.g, "sg")+" que "+q.es+". ("+p.en+" is more "+a.en+" than "+q.en+")",'''
N_COMP1 = u'''     return {v:p.es+" es ___ "+gcAdj(a, p.g, "sg")+" que "+q.es+". ("+p.nl+" is "+gcVergroot(a)+" dan "+gcKlein(q)+")",
             vEn:p.es+" es ___ "+gcAdj(a, p.g, "sg")+" que "+q.es+". ("+p.en+" is more "+a.en+" than "+gcKleinEn(q)+")",'''

A_COMP2 = u'''     return {v:p.es+" es tan "+gcAdj(a, p.g, "sg")+" ___ "+q.es+". (net zo "+a.nl+" als "+q.nl+")",
             vEn:p.es+" es tan "+gcAdj(a, p.g, "sg")+" ___ "+q.es+". (just as "+a.en+" as "+q.en+")",'''
N_COMP2 = u'''     return {v:p.es+" es tan "+gcAdj(a, p.g, "sg")+" ___ "+q.es+". (net zo "+a.nl+" als "+gcKlein(q)+")",
             vEn:p.es+" es tan "+gcAdj(a, p.g, "sg")+" ___ "+q.es+". (just as "+a.en+" as "+gcKleinEn(q)+")",'''

PAREN = [("GC_SUST", A_SUST, N_SUST), ("inteligente", A_ADJ, N_ADJ), ("generoso", A_GUL, N_GUL),
         ("het hay-patroon", A_HAY, N_HAY), ("comparar 1", A_COMP1, N_COMP1),
         ("comparar 2", A_COMP2, N_COMP2)]

if DOE_APP:
    ontbreekt = [n for n, a, _ in PAREN if a not in src]
    if A_MANO not in src:
        ontbreekt.append("het en-la-mano-patroon")
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.83. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    for _, a, n in PAREN:
        rep(a, n)

    # De twee generatoren die een selectie nodig hebben. gcKies staat vlak vóór het patroon, dus
    # het anker is de regel met de trekking en niet de regel met de zin.
    rep(u'''   function(){ var s = gcKies(GC_SUST), l = gcKies(GC_LUGAR), art = s.g === "f" ? "La" : "El";''',
        u'''   function(){ var s = gcKies(gcOpPlek()), l = gcKies(GC_LUGAR), art = s.g === "f" ? "La" : "El";''', 2)
    rep(u'''   function(){ var s = gcKies(GC_SUST), l = gcKies(GC_LUGAR), art = s.g === "f" ? "una" : "un";''',
        u'''   function(){ var s = gcKies(gcOpPlek()), l = gcKies(GC_LUGAR), art = s.g === "f" ? "una" : "un";''')

    # en la mano: alleen wat je kunt vasthouden. De trekking staat op de regel erboven.
    i = src.index(A_MANO)
    j = src.rfind("function(){", 0, i)
    kop = src[j:i]
    if "gcKies(GC_SUST)" not in kop:
        print("Het en-la-mano-patroon trekt niet uit GC_SUST zoals verwacht:\n" + kop[:200])
        sys.exit(1)
    src = src[:j] + kop.replace("gcKies(GC_SUST)", "gcKies(gcInHand())", 1) + src[i:]

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
