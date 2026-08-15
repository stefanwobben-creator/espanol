#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.110: de afleiders verklappen het antwoord niet meer.

## Waar dit vandaan komt

De meerkeuzevraag van de Conjugador zag er zo uit:

        hablar, nosotros, presente
        [ hablo ] [ hablas ] [ hablamos ] [ habláis ]

De vraag zegt "nosotros". De opties zijn de andere personen van hetzelfde werkwoord. Dus je
zoekt de optie die op -mos eindigt en je hebt hem, zonder ooit naar de stam of de tijd te kijken.

Nagemeten over alle 990 opgaven in de drill (vijf tijden, alle werkwoorden, zes personen):

    990 van de 990   de goede optie is de enige die bij de gevraagde persoon kán horen
    3279             afleiders die een andere persoon van hetzelfde werkwoord zijn
      81             opgaven met minder dan vier verschillende opties

Dat laatste is een eigen bug: cjMeerkeuzeOpties filtert dubbelen weg en vult niet aan, dus bij
werkwoorden waar twee personen dezelfde vorm hebben kreeg je drie knoppen in plaats van vier.

Stefan, na de vormdril: "ik had alles goed. maar dat is niet goed. want ik herken nu gewoon de yo
en nosotros maar nog steeds niet wat de vorm is." Dit is de code waar dat uit voortkomt.

## De regel

**Elke optie is een vorm van de gevraagde persoon.** Dan draagt de persoonsuitgang geen informatie
meer en moet je naar de stam en de tijd kijken. Dat is precies wat learned attention voorschrijft:
haal de concurrerende aanwijzing weg, anders leert het brein de uitgang nooit.

Twee soorten afleiders, in deze volgorde, allebei echte vormen uit conjVorm():

  1. dezelfde persoon, dit werkwoord, een andere tijd die je open hebt staan
     -> hablamos tegenover hablábamos: dit leert je de tijd aflezen
  2. dezelfde persoon, dezelfde tijd, een ander werkwoord
     -> hablamos tegenover comemos: dit leert je de stam aflezen

Eerst 1, dan aanvullen met 2 tot er vier zijn. Omdat er 33 werkwoorden zijn, lukt dat altijd, dus
er is geen noodrem nodig die alsnog een andere persoon binnenlaat.

## Eén filter dat er echt toe doet

Een afleider die alleen in accenten van het goede antwoord verschilt mag niet. De nakijker
accepteert een accentloos antwoord als "bijna goed" en telt het als goed; zo'n knop zou dus twee
goede knoppen opleveren. Gefilterd op stripAcc(norm(...)), dezelfde vergelijking als de nakijker
zelf gebruikt, zodat de twee niet uit elkaar kunnen lopen.

## Waarom conjOpenTijden en niet alle tijden

Sta je in fase 2, dan heb je alleen het presente open. Een afleider in de subjuntivo is dan geen
leerzame tegenstelling maar ruis. De functie die de omkering (v23.109) al gebruikte om te bepalen
welke tijden open staan heet daarom nu conjOpenTijden en wordt door allebei gelezen.

## Wat dit expres NIET doet

Het plafond (meerkeuze mag nooit een vorm als geleerd afvinken) zit hier niet in. Dat is de
volgende ronde. Eén variabele per ronde, anders is achteraf niet te zeggen wat het deed.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.110"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.110" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = huidig_ver != NIEUW and (DOE_APP or _num(huidig_ver) < _num(NIEUW))

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


# ------------------------------------------------- 1. de open tijden krijgen hun naam
# omkeerTijden() deed al precies dit en wordt vanaf nu door twee schermen gelezen. Een functie die
# "welke tijden staan open" beantwoordt hoort niet naar één van zijn aanroepers vernoemd te zijn.
A_TIJDEN = u'''/* de tijden die je open hebt staan. "mix" is geen tijd maar een fase-instelling, dus die valt af. */
function omkeerTijden(){'''
N_TIJDEN = u'''/* de tijden die je open hebt staan. "mix" is geen tijd maar een fase-instelling, dus die valt af.
   v23.110: hernoemd van omkeerTijden. Twee schermen lezen dit nu (de omkering en de afleiders van
   de Conjugador), dus een naam die naar één aanroeper verwijst klopt niet meer. */
function conjOpenTijden(){'''
rep(A_TIJDEN, N_TIJDEN)

A_TIJDEN2 = u'''  var tijden = omkeerTijden(), pool = [], dubbel = 0, totaal = 0;'''
N_TIJDEN2 = u'''  var tijden = conjOpenTijden(), pool = [], dubbel = 0, totaal = 0;'''
rep(A_TIJDEN2, N_TIJDEN2)

# ---------------------------------------------------------- 2. de afleiders zelf
A_OPTIES = u'''function cjMeerkeuzeOpties(v, p, t){
  var vormen = conjAlleVormen(v, t);
  var correct = vormen[p];
  var andereVormen = vormen.filter(function(vorm, i){ return i !== p && vorm !== correct; });
  var afleiders = geschud(andereVormen).slice(0, 3);
  return geschud([correct].concat(afleiders));
}'''
N_OPTIES = u'''/* v23.110: de afleiders kwamen hiervoor uit de andere PERSONEN van hetzelfde werkwoord. Gemeten
   over alle 990 opgaven was de goede optie in 990 gevallen de enige die bij de gevraagde persoon
   kon horen: je zocht de uitgang die bij het voornaamwoord in de vraag paste en je was klaar,
   zonder ooit naar de stam of de tijd te kijken. Bovendien had de oude versie 81 opgaven met
   minder dan vier knoppen, want hij filterde dubbelen weg en vulde niet aan.

   Nieuwe regel: elke optie is een vorm van de GEVRAAGDE persoon. Dan draagt de persoonsuitgang
   geen informatie meer en moet je wel naar de stam en de tijd kijken. Dat is de kern van learned
   attention: haal de concurrerende aanwijzing weg, anders leert het brein de uitgang nooit.

   Twee bronnen, in deze volgorde:
     1. dit werkwoord, dezelfde persoon, een andere OPEN tijd   -> leert je de tijd aflezen
     2. een ander werkwoord, dezelfde persoon, dezelfde tijd    -> leert je de stam aflezen

   Er zijn 33 werkwoorden, dus bron 2 vult altijd aan tot vier. Een noodrem die alsnog een andere
   persoon binnenlaat is daarom niet nodig, en die zou de hele regel ook weer weglekken. */
function cjMeerkeuzeOpties(v, p, t){
  var correct = conjVorm(v, p, t);
  var kaal = function(x){ return stripAcc(norm(x || "")); };
  var correctKaal = kaal(correct);
  var gezien = {}, afleiders = [];
  gezien[correct] = 1;
  function voegToe(vorm){
    if(!vorm || gezien[vorm]) return;
    // Een afleider die alleen in accenten verschilt mag niet: de nakijker telt een accentloos
    // antwoord als goed, dus zo'n knop zou een tweede goede knop zijn. Zelfde vergelijking als de
    // nakijker gebruikt, zodat de twee niet uit elkaar kunnen lopen.
    if(kaal(vorm) === correctKaal) return;
    gezien[vorm] = 1;
    afleiders.push(vorm);
  }
  geschud(conjOpenTijden()).forEach(function(t2){
    if(t2 === t || afleiders.length >= 2) return;
    voegToe(conjVorm(v, p, t2));
  });
  geschud(VERBOS.slice()).forEach(function(v2){
    if(v2.inf === v.inf || afleiders.length >= 3) return;
    voegToe(conjVorm(v2, p, t));
  });
  return geschud([correct].concat(afleiders.slice(0, 3)));
}'''
rep(A_OPTIES, N_OPTIES)

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
