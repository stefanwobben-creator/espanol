#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.114: de verwarring krijgt een naam, en een foute keuze krijgt uitleg.

## De uitslag die dit uitlokt

Stefan, eerste ronde "Welke tijd is dit?":

    Wie is dit?        10/12   de persoon herkennen
    Welke tijd is dit?  6/12   de tijd herkennen

Dat lijkt een verschil van vier vragen. Gecorrigeerd voor gokken is het groter, want de twee
schermen hebben niet dezelfde kans:

    persoon   zes knoppen -> gokken levert 2,0 van de 12.   Stefan: 10.  8,0 van de 10 haalbare
    tijd      vijf knoppen -> gokken levert 2,4 van de 12.  Stefan:  6.  3,6 van de 9,6 haalbare

Dus 80% van wat er te halen viel bij de persoon, en 37% bij de tijd. Dat is wél een gat, en het
ligt precies waar het ontwerpadvies het na de eerste nulmeting verwachtte.

## Waarom dit de volgende ronde is en niet meteen een les

Zes fout van de twaalf, en de app weet niet wélke zes. Indefinido tegenover imperfecto is Stefans
bekende struikelblok, maar het kunnen net zo goed perfecto en subjuntivo zijn, of alles tegenover
presente. Een les bouwen voor de verkeerde verwarring is weggegooid werk, en dat is precies de
"van fout naar regel" fout waar deze hele verbouwing over gaat: eerst weten wat er mis is.

## Wat er verandert

**1. De verwarring wordt geteld.** Per antwoord onthoudt de app wat er stond en wat je koos, als
sleutel "getoond>gekozen", cumulatief in S.brok["vorm.tijd"].verwar. Dat is een verwarringsmatrix,
en na een paar rondes wijst hij het paar aan waar je werk heen moet.

**2. Het eindscherm noemt hem.** Niet "je had er zes fout" maar "je koos vier keer imperfecto waar
indefinido stond". Dat is een uitslag waar je morgen iets mee kunt.

**3. Een foute keuze krijgt uitleg op het moment zelf.** Naast de contrastrij komt te staan waaraan
je de twee tijden die jij door elkaar haalde uit elkaar houdt, aan de VORM. Niet aan de betekenis:
dat is een andere brok en die zit al in "Achtergrond of gebeurtenis". Hier gaat het puur om welke
letters je moet zien.

Die vormkenmerken staan als data bij de tijd zelf (veld `vorm` in CONJ_TIEMPOS), niet als tabel met
paren. Vijf tijden geven tien paren, en tien met de hand geschreven regels lopen uit elkaar zodra
er een zesde tijd bij komt. Nu is het per tijd één regel en zoekt het scherm de twee op die jij
verwarde. Architectuurregel 15 augustus.

## Wat dit expres NIET doet

Geen les, geen ladder, geen SRS-koppeling. Eerst deze meting een paar rondes laten lopen, dan weten
we welk paar de les verdient. Eén variabele per ronde.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.114"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.114" not in src
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


# ------------------------- 1. het vormkenmerk hoort bij de tijd, niet in een parentabel
A_TIEMPOS = u'''var CONJ_TIEMPOS = [
  {id:"presente",   es:"presente",
   nl:"tegenwoordige tijd (tt)",                    en:"present tense",
   vb:"aprendo",      vbNl:"ik leer",                     vbEn:"I learn"},
  {id:"perfecto",   es:"pret\\u00e9rito perfecto",
   nl:"voltooid tegenwoordige tijd (vtt)",          en:"present perfect",
   vb:"he aprendido", vbNl:"ik heb geleerd",              vbEn:"I have learned"},
  {id:"indefinido", es:"pret\\u00e9rito indefinido",
   nl:"verleden tijd, afgesloten",                  en:"simple past, finished",
   vb:"aprend\\u00ed",  vbNl:"ik leerde (toen, \\u00e9\\u00e9n keer)",    vbEn:"I learned (once, back then)"},
  {id:"imperfecto", es:"pret\\u00e9rito imperfecto",
   nl:"verleden tijd, achtergrond",                 en:"past continuous / used to",
   vb:"aprend\\u00eda", vbNl:"ik leerde (steeds, gewoonlijk)", vbEn:"I was learning / I used to learn"},
  {id:"subjuntivo", es:"presente de subjuntivo",
   nl:"aanvoegende wijs",                           en:"present subjunctive",
   vb:"aprenda",      vbNl:"(dat) ik leer",               vbEn:"(that) I learn"}
];'''
N_TIEMPOS = u'''var CONJ_TIEMPOS = [
  {id:"presente",   es:"presente",
   nl:"tegenwoordige tijd (tt)",                    en:"present tense",
   vb:"aprendo",      vbNl:"ik leer",                     vbEn:"I learn",
   vorm:"korte uitgang, geen accent: -o, -as/-es, -a/-e, -amos/-emos/-imos",
   vormEn:"short ending, no accent: -o, -as/-es, -a/-e, -amos/-emos/-imos"},
  {id:"perfecto",   es:"pret\\u00e9rito perfecto",
   nl:"voltooid tegenwoordige tijd (vtt)",          en:"present perfect",
   vb:"he aprendido", vbNl:"ik heb geleerd",              vbEn:"I have learned",
   vorm:"twee woorden: he/has/ha/hemos/hab\\u00e9is/han + -ado of -ido",
   vormEn:"two words: he/has/ha/hemos/hab\\u00e9is/han + -ado or -ido"},
  {id:"indefinido", es:"pret\\u00e9rito indefinido",
   nl:"verleden tijd, afgesloten",                  en:"simple past, finished",
   vb:"aprend\\u00ed",  vbNl:"ik leerde (toen, \\u00e9\\u00e9n keer)",    vbEn:"I learned (once, back then)",
   vorm:"accent achteraan bij yo en \\u00e9l: -\\u00e9/-\\u00ed en -\\u00f3/-i\\u00f3. Of een onregelmatige stam zonder accent (tuve, hice, fui)",
   vormEn:"accent at the end for yo and \\u00e9l: -\\u00e9/-\\u00ed and -\\u00f3/-i\\u00f3. Or an irregular stem with no accent (tuve, hice, fui)"},
  {id:"imperfecto", es:"pret\\u00e9rito imperfecto",
   nl:"verleden tijd, achtergrond",                 en:"past continuous / used to",
   vb:"aprend\\u00eda", vbNl:"ik leerde (steeds, gewoonlijk)", vbEn:"I was learning / I used to learn",
   vorm:"altijd -aba- of -\\u00eda- v\\u00f3\\u00f3r de uitgang. Slechts drie uitzonderingen: ser, ir, ver",
   vormEn:"always -aba- or -\\u00eda- before the ending. Only three exceptions: ser, ir, ver"},
  {id:"subjuntivo", es:"presente de subjuntivo",
   nl:"aanvoegende wijs",                           en:"present subjunctive",
   vb:"aprenda",      vbNl:"(dat) ik leer",               vbEn:"(that) I learn",
   vorm:"de klinker is omgewisseld: -ar krijgt een e (hable), -er en -ir krijgen een a (aprenda)",
   vormEn:"the vowel is swapped: -ar takes an e (hable), -er and -ir take an a (aprenda)"}
];'''
rep(A_TIEMPOS, N_TIEMPOS)

# --------------------------------------------- 2. de verwarring wordt geteld
A_ANTW = u'''function tijdvormAntwoord(t){
  if(!tijdvormSpel || tijdvormSpel.gekozen !== null) return;
  tijdvormSpel.gekozen = t;
  if(t === tijdvormSpel.rij[tijdvormSpel.i].t) tijdvormSpel.goed++;
  renderFunTijdvorm();
}'''
N_ANTW = u'''/* v23.114: "zes fout" zegt niet welke zes. Per antwoord onthouden we wat er stond en wat je koos,
   als sleutel "getoond>gekozen". Dat is een verwarringsmatrix, en na een paar rondes wijst hij het
   paar aan waar het werk heen moet. Zonder dit zouden we een les moeten bouwen voor een verwarring
   die we alleen vermoeden. */
function tijdvormVerwarBij(getoond, gekozen){
  if(getoond === gekozen) return;
  S.brok = S.brok || {};
  var st = brokLees(TIJDVORM_ID);
  st.verwar = st.verwar || {};
  var k = getoond + ">" + gekozen;
  st.verwar[k] = (st.verwar[k] || 0) + 1;
  S.brok[TIJDVORM_ID] = st;
}
/* het paar dat het vaakst misgaat, over alle rondes heen. Geeft null als er nog niets te melden
   is, zodat het scherm kan zwijgen in plaats van een toevalstreffer op te blazen. */
function tijdvormTopVerwar(){
  var st = brokLees(TIJDVORM_ID), v = st.verwar || {}, best = null;
  for(var k in v){
    if(!Object.prototype.hasOwnProperty.call(v, k)) continue;
    if(!best || v[k] > best.n){
      var d = k.split(">");
      best = {getoond:d[0], gekozen:d[1], n:v[k]};
    }
  }
  return (best && best.n >= 2) ? best : null;
}
function tijdvormAntwoord(t){
  if(!tijdvormSpel || tijdvormSpel.gekozen !== null) return;
  tijdvormSpel.gekozen = t;
  var q = tijdvormSpel.rij[tijdvormSpel.i];
  if(t === q.t) tijdvormSpel.goed++;
  else tijdvormVerwarBij(q.t, t);
  renderFunTijdvorm();
}
/* Waaraan je de twee tijden die JIJ door elkaar haalde uit elkaar houdt, aan de vorm. Niet aan de
   betekenis: dat is een andere brok, en die zit al in "Achtergrond of gebeurtenis". Hier gaat het
   puur om welke letters je moet zien.

   De kenmerken staan per tijd in CONJ_TIEMPOS en niet als tabel met paren. Vijf tijden geven tien
   paren, en tien met de hand geschreven regels lopen uit elkaar zodra er een zesde tijd bij komt. */
function tijdvormVormHint(getoond, gekozen){
  var a = conjTiempo(getoond), b = conjTiempo(gekozen);
  if(!a || !b || !a.vorm || !b.vorm) return "";
  return "<div class='card' style='margin-top:10px' id='tvHint'>" +
    "<p class='muted' style='margin:0 0 6px; font-size:.85rem'><b>" +
      ct("Hoe je deze twee uit elkaar houdt aan de vorm", "How to tell these two apart by their form") + "</b></p>" +
    "<p style='margin:0 0 4px; font-size:.88rem'><b>" + a.es + "</b>: " + ct(a.vorm, a.vormEn) + "</p>" +
    "<p style='margin:0; font-size:.88rem'><b>" + b.es + "</b>: " + ct(b.vorm, b.vormEn) + "</p></div>";
}'''
rep(A_ANTW, N_ANTW)

# ------------------------------------ 3. de hint verschijnt bij een fout antwoord
A_FOUT = u'''                : ct("Nog niet. Het is: ", "Not yet. It is: ") + "<b>" + conjTiempoNaam(q.t) + "</b>") +
        "</div>" + rijtje +'''
N_FOUT = u'''                : ct("Nog niet. Het is: ", "Not yet. It is: ") + "<b>" + conjTiempoNaam(q.t) + "</b>") +
        "</div>" + rijtje +
        /* v23.114: alleen bij een fout, en alleen over de twee tijden die JIJ verwarde. Bij een
           goed antwoord is dit ruis. */
        (goed ? "" : tijdvormVormHint(q.t, tijdvormSpel.gekozen)) +'''
rep(A_FOUT, N_FOUT)

# ------------------------------------------- 4. het eindscherm noemt de verwarring
A_EIND = u'''      "<p class='muted'>" + tijdvormUitslag(tijdvormSpel.goed, totaal) + "</p>" +'''
N_EIND = u'''      "<p class='muted'>" + tijdvormUitslag(tijdvormSpel.goed, totaal) + "</p>" +
      /* v23.114: "zes fout" is geen uitslag waar je morgen iets mee kunt. Dit wel. Pas vanaf twee
         keer dezelfde verwisseling, want \u00e9\u00e9n keer is een vergissing en geen patroon. */
      (function(){
        var w = tijdvormTopVerwar();
        if(!w) return "";
        var a = conjTiempo(w.getoond), b = conjTiempo(w.gekozen);
        if(!a || !b) return "";
        return "<p class='muted' id='tvVerwar' style='font-size:.9rem'><b>" +
          ct("Je struikelblok: ", "Your stumbling block: ") + "</b>" +
          ct("je koos " + w.n + " keer <b>" + b.es + "</b> waar <b>" + a.es + "</b> stond. Daar zit je werk, niet in de tijden die je al ziet.",
             "you picked <b>" + b.es + "</b> " + w.n + " times where <b>" + a.es + "</b> was shown. That is where your work is, not in the tenses you already see.") +
          "</p>";
      })() +'''
rep(A_EIND, N_EIND)

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
