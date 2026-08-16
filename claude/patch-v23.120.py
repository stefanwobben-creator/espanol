#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.120: de afstemming. De route bouwt geen eigen lessen maar wijst naar de beste die er is.

## De fout die dit rechtzet

Stefan, met twee schermafbeeldingen: "er staan nu dingen verspreid bij Spelen en dingen bij
Grammatica. Zijn ze op elkaar afgestemd?"

Nee. Vier systemen zeiden iets over hetzelfde onderwerp en geen van ze wist van de andere:

    GC_CONCEPTEN     concept "indefimperf"                    SRS-doos 0..5     Oefenen
    gwGenLijst       "Pretérito imperfecto: de vorming"       afgerond ✓        Oefenen
                     "...wanneer gebruik je hem?"             afgerond ✓        Oefenen
    GRAMWIZ          vijf handgeschreven diepe lessen         stap 2/4          Oefenen
    het pad          "indefimperf", zes stappen               gestold           Spelen

Op zijn scherm stond "Pretérito imperfecto: de vorming" op **afgerond**, terwijl mijn pad zei dat
hij "De imperfecto leren" nog moest doen. Twee schermen die hetzelfde claimen.

En stap 0 en 1 van mijn les (wat doet hij, hier is het rijtje) deden precies wat die bestaande les
al deed. Dat is dubbel werk dat ik had kunnen zien als ik vóór het bouwen in de Oefenen-tab had
gekeken. Vier rondes lang niet gedaan.

## De regel

**De route bouwt geen eigen lessen maar wijst naar de beste die er is.** Bestaat er al een uitlegles
over de vorming van het imperfecto, dan is dat stap 2 van de route, en staat hij groen zodra je hem
afrondt. Wat de route toevoegt is alleen wat nergens anders bestond: het rijtje in je vingers
krijgen, door elkaar herkennen, en stollen.

## Het pad wordt

    1  imperfecto: wanneer gebruik je hem?    bestaande les      uitleg
    2  snap je het verschil?                  brok (v23.106)     meting, geen Spaans
    3  imperfecto: de vorming                 bestaande les      uitleg van de vorm
    4  imperfecto: het rijtje in de vingers   de les, vanaf stap 3
    5  indefinido: alle vormen op een rij     bestaande les
    6  indefinido: het rijtje in de vingers   de les, vanaf stap 3
    7  door elkaar herkennen                  Welke tijd is dit?
    8  in een echte zin                       komt nog
    9  gestold                                de hertoets

Stap 4 en 6 openen de les niet bij stap 1 maar bij stap 3 (herkennen), want stap 1 en 2 zijn dan net
in de bestaande uitleg gedaan. Dat is de dubbeling die eruit gaat.

## Hoe de route de bestaande les vindt

Niet op indexnummer. "spiek-a2-14" is het huidige id van de imperfecto-vorming, maar dat nummer
schuift zodra er een spiekbrief tussen komt, en dan wijst de route stilletjes naar het verkeerde
onderwerp.

De route verwijst daarom op **titel**, zoekt de spiekbrief op, en bouwt daar het id uit. Wordt de
titel ooit herschreven, dan vindt hij niets, en dan zegt de poort het: er is een dekkingscheck die
eist dat elke verwijzing in elk pad oplost naar een bestaande les. Fragiel-maar-gezien is beter dan
fragiel-en-stil.

## Wat dit expres NIET doet

De verhuizing uit Spelen naar Grammatica is ronde B. Deze ronde gaat alleen over wie wat claimt, en
verandert niets aan waar de tegels staan. Eén variabele.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.120"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.120" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


# v23.120: alleen vooruit, ook als de app-wijziging nog moet gebeuren. Hiervoor stond hier
# "DOE_APP or ...", en toen de avondrun versie.txt naar v23.119 had gezet zette deze patch hem
# terug naar v23.118. Het nummer hoort monotoon te zijn: staat er al iets nieuwers, laat staan.
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


# ------------- 1. een stap kan nu ook naar een bestaande les wijzen
A_EIS = u'''var GRAM_EIS = {
  betekenis: function(st){ return (st.beste || 0) >= 11; },'''
N_EIS = u'''/* v23.120: waar de stand van een stap vandaan komt. De brokken staan in S.brok, maar de bestaande
   lessen houden hun eigen boekhouding bij in S.gramwiz. Zonder deze splitsing zou de route naar een
   lege pot kijken en altijd "nog niet gedaan" zeggen, ook al staat de les op afgerond. */
function gramSpiekIdx(titel){
  for(var i = 0; i < CHEATSHEET.length; i++) if(CHEATSHEET[i].titel === titel) return i;
  return -1;
}
/* Op titel en niet op indexnummer: "spiek-a2-14" schuift zodra er een spiekbrief tussen komt, en
   dan wijst de route stilletjes naar een ander onderwerp. Wordt de titel herschreven dan vindt hij
   niets, en dat ziet de poort (dekkingscheck). Fragiel-maar-gezien boven fragiel-en-stil. */
function gramLesId(s){
  if(!s || !s.spiek) return null;
  var i = gramSpiekIdx(s.spiek);
  if(i < 0) return null;
  if(!gwVanSpiek(i)) return null;   // een spiekbrief zonder vragen levert geen les op
  return gwSpiekId(i);
}
function gramStapStand(s){
  if(s.soort === "bestaandeles"){
    var id = gramLesId(s);
    return id ? gwVoortgangLees(id) : {};
  }
  return brokLees(s.brok);
}

var GRAM_EIS = {
  /* de bestaande lessen houden {stap, klaar, rondes} bij; "klaar" is precies het vinkje dat je in
     de Oefenen-tab ziet staan. De route leest dat en claimt niets zelf. */
  bestaandeles: function(st){ return !!st.klaar; },
  betekenis: function(st){ return (st.beste || 0) >= 11; },'''
rep(A_EIS, N_EIS)

A_STAND2 = u'''var GRAM_STAND = {
  betekenis: function(st){ return st.rondes ? (st.beste || 0) + "/12" : ""; },'''
N_STAND2 = u'''var GRAM_STAND = {
  bestaandeles: function(st){
    if(st.klaar) return ct("afgerond", "done");
    return st.stap ? ct("stap ", "step ") + (st.stap + 1) : "";
  },
  betekenis: function(st){ return st.rondes ? (st.beste || 0) + "/12" : ""; },'''
rep(A_STAND2, N_STAND2)

# ------------- 2. gramPadStap leest via de nieuwe splitsing
A_STAP = u'''function gramPadStap(p, i){
  var s = p.stappen[i];
  var st = brokLees(s.brok);
  var eis = GRAM_EIS[s.soort];
  var af = !!(eis && eis(st));
  var stand = GRAM_STAND[s.soort] ? GRAM_STAND[s.soort](st) : "";
  return {s:s, st:st, af:af, stand:stand, bestaat:!!s.view};
}'''
N_STAP = u'''function gramPadStap(p, i){
  var s = p.stappen[i];
  var st = gramStapStand(s);
  var eis = GRAM_EIS[s.soort];
  var af = !!(eis && eis(st));
  var stand = GRAM_STAND[s.soort] ? GRAM_STAND[s.soort](st) : "";
  /* een bestaandeles bestaat als de spiekbrief hem oplevert; de rest als er een scherm bij hoort */
  var bestaat = (s.soort === "bestaandeles") ? !!gramLesId(s) : !!s.view;
  return {s:s, st:st, af:af, stand:stand, bestaat:bestaat};
}'''
rep(A_STAP, N_STAP)

# ------------- 3. erheen gaan
A_GA = u'''function gramPadGa(p, i){
  var s = p.stappen[i];
  if(!s.view) return;
  if(s.view === "les"){ lesStart(s.arg); }'''
N_GA = u'''function gramPadGa(p, i){
  var s = p.stappen[i];
  /* v23.120: een bestaande les leeft in de spiekbrief-tab en niet in funView. Zelfde route als de
     "Leg uit"-knop van de Corrector gebruikt sinds v19.88. */
  if(s.soort === "bestaandeles"){
    var lid = gramLesId(s);
    if(!lid) return;
    show("spiekbrief");
    gwStart(lid);
    return;
  }
  if(!s.view) return;
  /* vanaf: de les hoeft niet bij stap 1 te beginnen als de uitleg net in de bestaande les stond.
     Dat is de dubbeling die deze ronde eruit haalt. */
  if(s.view === "les"){ lesStart(s.arg); if(typeof s.vanaf === "number") lesSpel.stap = s.vanaf; }'''
rep(A_GA, N_GA)

A_GA2 = u'''  if(s.view === "les"){ lesStart(s.arg); if(typeof s.vanaf === "number") lesSpel.stap = s.vanaf; }
  if(s.view === "brok"){ brokSpel = null; }'''
N_GA2 = u'''  if(s.view === "les"){ lesStart(s.arg); if(typeof s.vanaf === "number") lesSpel.stap = s.vanaf; }
  else if(s.view === "brok"){ brokSpel = null; }'''
rep(A_GA2, N_GA2)

# ------------- 4. het pad zelf
A_PAD = u'''   stappen:[
     {brok:"indefimperf.betekenis", soort:"betekenis", view:"brok",
      nl:"Snap je het verschil?", en:"Do you get the difference?",
      subNl:"Twaalf Nederlandse zinnen, geen woord Spaans.", subEn:"Twelve English sentences, no Spanish at all."},
     {brok:"les.imperfecto", soort:"les", view:"les", arg:"imperfecto",
      nl:"De imperfecto leren", en:"Learn the imperfecto",
      subNl:"Vijf stappen, \\u00e9\\u00e9n tijd. De eerste twee stellen geen vraag.", subEn:"Five steps, one tense. The first two ask nothing."},
     {brok:"les.indefinido", soort:"les", view:"les", arg:"indefinido",
      nl:"De indefinido leren", en:"Learn the indefinido",
      subNl:"Zelfde vijf stappen, de andere tijd.", subEn:"Same five steps, the other tense."},'''
N_PAD = u'''   stappen:[
     /* v23.120: de route wijst naar de bestaande uitleglessen in plaats van ze over te doen. Stefan
        had "Pretérito imperfecto: de vorming" al op afgerond staan terwijl dit pad zei dat hij de
        imperfecto nog moest leren. Verwijzing op titel, niet op indexnummer. */
     {spiek:"Pretérito imperfecto: wanneer gebruik je hem?", soort:"bestaandeles",
      nl:"Wanneer gebruik je het imperfecto?", en:"When do you use the imperfecto?",
      subNl:"De bestaande uitleg met vragen. Eerst weten waarvoor hij dient.",
      subEn:"The existing explanation with questions. First know what it is for."},
     {brok:"indefimperf.betekenis", soort:"betekenis", view:"brok",
      nl:"Snap je het verschil?", en:"Do you get the difference?",
      subNl:"Twaalf Nederlandse zinnen, geen woord Spaans. Dit meet of de regel zit.",
      subEn:"Twelve English sentences, no Spanish at all. This measures whether the rule is in."},
     {spiek:"Pretérito imperfecto: de vorming", soort:"bestaandeles",
      nl:"Het imperfecto: de vorming", en:"The imperfecto: how it is formed",
      subNl:"De bestaande uitleg over de vorm.", subEn:"The existing explanation of the form."},
     {brok:"les.imperfecto", soort:"les", view:"les", arg:"imperfecto", vanaf:2,
      nl:"Het imperfecto in je vingers", en:"The imperfecto in your fingers",
      subNl:"Herkennen, gat vullen, zonder tabel typen, en dan met werkwoorden die je niet gezien hebt.",
      subEn:"Recognise, fill the gap, type without the table, then with verbs you have not seen."},
     {spiek:"Indefinido: alle vormen op een rij", soort:"bestaandeles",
      nl:"Het indefinido: alle vormen", en:"The indefinido: all the forms",
      subNl:"De bestaande uitleg, inclusief de onregelmatige.", subEn:"The existing explanation, irregulars included."},
     {brok:"les.indefinido", soort:"les", view:"les", arg:"indefinido", vanaf:2,
      nl:"Het indefinido in je vingers", en:"The indefinido in your fingers",
      subNl:"Zelfde vier stappen, de andere tijd.", subEn:"Same four steps, the other tense."},'''
rep(A_PAD, N_PAD)

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
