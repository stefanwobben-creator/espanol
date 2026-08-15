#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.112: een tegel in de Speeltuin doet altijd iets. De koppeling komt uit de lijst zelf.

## De fout

Stefan, na het installeren van v23.111: "alleen wie is dit niet klikbaar."

Hij heeft gelijk en het is mijn fout. In v23.109 heb ik de tegel toegevoegd aan spelInfo(), maar
de klikafhandeling stond ergens anders: een handgeschreven rij van tien regels onder aan
renderFun(), één per tegel, met de tegel-id als tekst erin. Ik heb er negen gezien en de tiende
niet toegevoegd. De tegel tekende netjes, en deed niets.

## De structurele oorzaak, niet het symptoom

Er waren twee lijsten die hetzelfde feit opschreven: spelInfo() wist welke tegels er zijn, en de
wire-rij wist welke tegels er zijn. Twee lijsten die met de hand synchroon gehouden worden, lopen
uit elkaar. Dat is precies de architectuurregel van 15 augustus.

Eén regel erbij plakken zou het symptoom oplossen en de val laten staan voor de volgende tegel.
Dus: de koppeling komt nu uit spelInfo() zelf. Wat per spel anders is, staat als data bij dat spel:

    verse    een functie die de spelstand leegmaakt voor je begint (kruisLos = null enzovoort)
    gezien   op false voor de spellen die niet in SPEEL_EIS staan en dus niets te "zien" hebben
    open     een eigen afhandeling voor het enige spel dat geen funView is (Música)

De rest doet wat elke tegel doet: gezien noteren, funView zetten, navPush, renderen. Een tegel
toevoegen is vanaf nu één regel data, en vergeten kan niet meer.

## Waarom de poort dit niet ving

pw-omkeer controleerde `de tegel staat in de Speeltuin` door te tellen of het element bestond, en
opende het scherm daarna met funView = "omkeer" in plaats van door te klikken. Dat is een check
die groen blijft terwijl de knop dood is. Dat is mijn fout in de suite, niet de suite van de app.

Twee dingen daaraan gedaan:

  - pw-omkeer klikt nu op de tegel in plaats van funView te zetten
  - nieuwe suite pw-tegels die over ALLE tegels loopt: klik elke tegel, en er moet iets veranderen.
    Dat vangt deze fout voor elke tegel die er ooit nog bij komt, niet alleen voor deze.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.112"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.112" not in src
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


# ------------------------- 1. wat per spel anders is, staat bij dat spel
A_INFO = u'''function spelInfo(){
  return [
    {v:"avt",     id:"ftAvt",     e:"\\ud83d\\uddfa\\ufe0f",     t:"Aventura",              s:fx("avS")},
    {v:"musica",  id:"ftMusica",  e:"\\ud83c\\udfb5",            t:"M\\u00fasica",            s:fx("muS")},
    {v:"ws",      id:"ftWs",      e:"\\ud83d\\udd0d",            t:fx("wsT"),               s:fx("wsS")},
    {v:"kruis",   id:"ftKruis",   e:"\\u270f\\ufe0f",            t:"Crucigrama",            s:fx("krS")},'''
N_INFO = u'''/* v23.112: elke tegel draagt zelf wat er bij hem anders is. De klikafhandeling onder aan
   renderFun() leest dit; daarvoor stond daar een handgeschreven rij van tien regels naast deze
   lijst, en die twee liepen uit elkaar (de omkering-tegel van v23.109 stond wel in deze lijst en
   niet in die rij, dus hij deed niets).

     verse    maakt de spelstand leeg voor je begint
     gezien   false voor spellen die niet in SPEEL_EIS staan en dus niets te "zien" hebben
     open     een eigen afhandeling, voor het enige spel dat geen funView is */
function spelInfo(){
  return [
    {v:"avt",     id:"ftAvt",     e:"\\ud83d\\uddfa\\ufe0f",     t:"Aventura",              s:fx("avS"), gezien:false},
    {v:"musica",  id:"ftMusica",  e:"\\ud83c\\udfb5",            t:"M\\u00fasica",            s:fx("muS"), open:function(){ show("musica"); }},
    {v:"ws",      id:"ftWs",      e:"\\ud83d\\udd0d",            t:fx("wsT"),               s:fx("wsS")},
    {v:"kruis",   id:"ftKruis",   e:"\\u270f\\ufe0f",            t:"Crucigrama",            s:fx("krS"), verse:function(){ kruisLos = null; }},'''
rep(A_INFO, N_INFO)

A_INFO2 = u'''    {v:"letras",  id:"ftLetras",  e:"\\ud83d\\udd24",            t:"Letras",                s:ct("Zeven letters, hoeveel woorden haal je eruit? Geen klok.","Seven letters, how many words can you find? No clock.")},
    {v:"adiv",    id:"ftAdiv",    e:"\\ud83d\\udfe9",            t:"Adivina",               s:ct("Raad het woord in vijf pogingen. De eerste letter krijg je.","Guess the word in five tries. You get the first letter.")},
    {v:"clas",    id:"ftClas",    e:"\\u26a1",                  t:"Clasificador",          s:ct("Links of rechts, en het gaat steeds sneller.","Left or right, and it keeps speeding up.")},'''
N_INFO2 = u'''    {v:"letras",  id:"ftLetras",  e:"\\ud83d\\udd24",            t:"Letras",                s:ct("Zeven letters, hoeveel woorden haal je eruit? Geen klok.","Seven letters, how many words can you find? No clock."), verse:function(){ ltSpel = null; }},
    {v:"adiv",    id:"ftAdiv",    e:"\\ud83d\\udfe9",            t:"Adivina",               s:ct("Raad het woord in vijf pogingen. De eerste letter krijg je.","Guess the word in five tries. You get the first letter."), verse:function(){ adivSpel = null; }},
    {v:"clas",    id:"ftClas",    e:"\\u26a1",                  t:"Clasificador",          s:ct("Links of rechts, en het gaat steeds sneller.","Left or right, and it keeps speeding up."), verse:function(){ clNieuwSpel(); }},'''
rep(A_INFO2, N_INFO2)

A_INFO3 = u'''    {v:"brok",    id:"ftBrok",    e:"\\ud83c\\udfad",            t:ct("Achtergrond of gebeurtenis","Background or event"), s:ct("Twaalf Nederlandse zinnen, twee bakjes. Geen Spaans: dit meet of je de regel snapt, los van de vormen.","Twelve English sentences, two bins. No Spanish: this measures whether you get the rule, apart from the forms.")},'''
N_INFO3 = u'''    {v:"brok",    id:"ftBrok",    e:"\\ud83c\\udfad",            t:ct("Achtergrond of gebeurtenis","Background or event"), s:ct("Twaalf Nederlandse zinnen, twee bakjes. Geen Spaans: dit meet of je de regel snapt, los van de vormen.","Twelve English sentences, two bins. No Spanish: this measures whether you get the rule, apart from the forms."), gezien:false, verse:function(){ brokSpel = null; }},'''
rep(A_INFO3, N_INFO3)

A_INFO4 = u'''    {v:"omkeer",  id:"ftOmkeer",  e:"\\ud83d\\udd0e",            t:ct("Wie is dit?","Who is this?"), s:ct("Een vervoegde vorm zonder voornaamwoord: wie is het? De omgekeerde richting van de Conjugador.","A conjugated form with no pronoun: who is it? The reverse direction of Conjugador.")},'''
N_INFO4 = u'''    {v:"omkeer",  id:"ftOmkeer",  e:"\\ud83d\\udd0e",            t:ct("Wie is dit?","Who is this?"), s:ct("Een vervoegde vorm zonder voornaamwoord: wie is het? De omgekeerde richting van de Conjugador.","A conjugated form with no pronoun: who is it? The reverse direction of Conjugador."), gezien:false, verse:function(){ omkeerSpel = null; }},'''
rep(A_INFO4, N_INFO4)

A_INFO5 = u'''    {v:"duel",    id:"ftDuel",    e:"\\u2694\\ufe0f",            t:"Palabra Duel",          s:fx("duS")}'''
N_INFO5 = u'''    {v:"duel",    id:"ftDuel",    e:"\\u2694\\ufe0f",            t:"Palabra Duel",          s:fx("duS"), gezien:false}'''
rep(A_INFO5, N_INFO5)

# ------------------------------ 2. de koppeling komt uit de lijst zelf
A_WIRE = u'''  function wire(id, fn){ var b = document.getElementById(id); if(b) b.onclick = fn; }
  wire("ftAvt", function(){ funView = "avt"; navPush({t:"fun", v:"avt"}); renderFun(); });
  wire("ftMusica", function(){ show("musica"); });
  wire("ftWs", function(){ speelGezien("ws"); funView = "ws"; navPush({t:"fun", v:"ws"}); renderFun(); });
  wire("ftKruis", function(){ speelGezien("kruis"); funView = "kruis"; kruisLos = null; navPush({t:"fun", v:"kruis"}); renderFun(); });
  wire("ftLetras", function(){ speelGezien("letras"); funView = "letras"; ltSpel = null; navPush({t:"fun", v:"letras"}); renderFun(); });
  wire("ftAdiv", function(){ speelGezien("adiv"); funView = "adiv"; adivSpel = null; navPush({t:"fun", v:"adiv"}); renderFun(); });
  wire("ftClas", function(){ speelGezien("clas"); funView = "clas"; clNieuwSpel(); navPush({t:"fun", v:"clas"}); renderFun(); });
  wire("ftMem", function(){ speelGezien("mem"); funView = "mem"; navPush({t:"fun", v:"mem"}); renderFun(); });
  wire("ftDuel", function(){ funView = "duel"; navPush({t:"fun", v:"duel"}); renderFun(); });
  wire("ftBrok", function(){ funView = "brok"; brokSpel = null; navPush({t:"fun", v:"brok"}); renderFun(); });'''
N_WIRE = u'''  function wire(id, fn){ var b = document.getElementById(id); if(b) b.onclick = fn; }
  /* v23.112: hier stond een handgeschreven rij van tien wire-regels naast SPEELMENU. Twee lijsten
     met dezelfde tegels erin, met de hand synchroon gehouden, en dus liepen ze uit elkaar: de
     omkering-tegel van v23.109 stond wel in spelInfo() en niet in die rij, dus hij tekende netjes
     en deed niets. Nu loopt de koppeling over SPEELMENU, en is een tegel zonder afhandeling
     onmogelijk. Wat per spel anders is staat als data bij dat spel (zie spelInfo). */
  SPEELMENU.forEach(function(g){
    wire(g.id, g.open || function(){
      if(g.gezien !== false) speelGezien(g.v);
      if(g.verse) g.verse();
      funView = g.v;
      navPush({t:"fun", v:g.v});
      renderFun();
    });
  });'''
rep(A_WIRE, N_WIRE)

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
