#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.246 - twee keer dezelfde fout: een index die niet is wat hij lijkt
#
# Stefan, 6 september, met twee schermafbeeldingen:
#   "dit is een goede combi in mijn memory spel maar klopt [niet]"  (de kaart "el" naast "de zanger(es)")
#   "bij de luisteroefening maakt hij nu standaard altijd de bovenste groen maar het lijkt niet
#    gekoppeld te zijn aan het goede of foute antwoord"
#
# Twee verschillende schermen, twee verschillende oorzaken, en toch dezelfde vorm: iets wordt
# aangewezen met een getal of een positie die niet betekent wat de code denkt dat hij betekent.
#
# ================ EEN: DE MEMORY-KAART DIE "EL" HEET ================
#
# memPool() haalt het woord uit de kaart met:
#
#     var es = w.es.split("/")[0].trim();
#
# Dat is bedoeld voor "claro / clara": twee vormen, neem de eerste. Maar er zijn woorden waar de
# streep niet twee vormen scheidt maar twee LIDWOORDEN van hetzelfde woord:
#
#     el / la cantante        de zanger(es)
#     el / la estudiante      de student(e)
#     el / la hispanohablante de Spaanstalige
#     el / la taxista         de taxichauffeur
#     el / la turista         de toerist
#
# Daar levert split("/")[0] het woord "el" op. Dat is precies wat op Stefans scherm staat: een kaart
# met "el" ernaast "de zanger(es)", en die twee matchen omdat ze uit hetzelfde woord komen. Het spel
# doet niets fout; het heeft een woord gekregen dat geen woord is.
#
# EN HET IS NIET ALLEEN MEMORY. Gemeten: 133 kaarten hebben een streep in es, vijf daarvan hebben
# alleen een lidwoord als eerste stuk, en die vijf gaan op ZES plekken mis omdat overal dezelfde
# split staat:
#
#   memPool          de kaart heet "el"
#   woordZoekerPool  kern wordt leeg, dus deze vijf woorden komen er nooit in
#   dicVoorbeeld     kern wordt leeg, dus geen voorbeeldzin in het woordenboek
#   dicSorteer       "el" blijft staan, dus ze sorteren onder de E in plaats van onder C, H of T
#   infGloss         kern is "el", dus hij vindt het werkwoord nooit
#   woordSoort       "el" zonder spatie erachter voldoet niet aan de lidwoordtest, dus geen "zn"
#
# Eén regel, zes plekken, vijf woorden. Daarom staat de kennis nu op één plek: woordEerste() weet dat
# een streep tussen twee vormen iets anders is dan een streep tussen twee lidwoorden.
#
# ================ TWEE: DE LUISTERVRAAG KLEURT DE BOVENSTE ================
#
# Dit heb ik zelf gemaakt, in v23.238. Toen liep ik alle schermen langs die een antwoord markeren en
# haalde ze door één functie, keuzeMarkeer(). Die markeert op POSITIE in de rij knoppen:
#
#     m = keuzeMerk(i, juist, gekozen)      // i = de hoeveelste knop
#
# Voor vier van de vijf schermen klopt dat. Het luisterscherm SCHUDT zijn opties (v._orde) en zet de
# oorspronkelijke index in data-ai. Daar is de hoeveelste knop dus niet het hoeveelste antwoord, en
# v.c wijst een plek aan in plaats van een antwoord. Omdat het juiste antwoord in deze data meestal
# index 0 heeft, kleurde vrijwel altijd de bovenste knop groen. Precies wat Stefan beschrijft.
#
# De oude code deed het goed, met dode klassen maar met de juiste index:
#
#     var bi = +b.getAttribute("data-ai");
#     if(bi === v.c) b.classList.add("correct");
#
# Ik heb bij het samenvoegen de klassen gerepareerd en de index gesloopt.
#
# EN DE PROEF ZAG HET NIET, want die mat het toetsje en de leesvraag: twee schermen die niet
# schudden. Een proef die alleen het makkelijke geval bouwt, bewijst het makkelijke geval.
#
# WAT ER NU STAAT: de index komt van de knop zelf. Elke keuzeknop draagt data-keuze met zijn eigen
# antwoordindex, en keuzeMarkeer() leest die. Geen enkele aanroeper hoeft nog te weten of zijn scherm
# schudt, en een scherm dat gaat schudden hoeft niets aan te passen.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.246"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function woordEerste(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------------------------------------------------------------- 1. woordEerste
    rep("""function esVormen(es){""",
'''/* ================= EEN STREEP IS NIET ALTIJD EEN KEUZE (v23.245) =================

   Stefan, 6 september, over zijn memory-spel: een kaart met "el" ernaast "de zanger(es)".

   Op zes plekken stond `w.es.split("/")[0]`, bedoeld voor "claro / clara": twee vormen, neem de
   eerste. Maar bij vijf woorden scheidt die streep geen vormen maar twee LIDWOORDEN van hetzelfde
   woord: el / la cantante, estudiante, hispanohablante, taxista, turista. Daar levert die regel het
   woord "el" op, en dat is geen woord.

   Gemeten gevolg van die vijf woorden, op zes schermen: een memorykaart die "el" heet, een lege kern
   in de woordenzoeker (dus ze komen er nooit in), geen voorbeeldzin in het woordenboek, sorteren
   onder de E, een werkwoordsopzoeker die ze niet vindt, en een woordsoort die niet "zn" wordt.

   Deze functie is dat verschil, op één plek. Wie het woord wil, vraagt het hier. */
var WOORD_ARTIKELEN = {el:1, la:1, los:1, las:1, un:1, una:1, unos:1, unas:1};
function woordEerste(es){
  var ruw = String(es || "");
  var delen = ruw.split("/").map(function(d){ return d.trim(); }).filter(Boolean);
  if(!delen.length) return ruw.trim();
  var eerste = delen[0];
  /* Is het eerste stuk niets meer dan een lidwoord, dan stond de streep tussen twee lidwoorden en
     hoort de kern uit het tweede stuk te komen: "el / la cantante" wordt "el cantante". Het tweede
     stuk draagt zijn eigen lidwoord, en dat gaat eraf zodat er niet "el la cantante" staat. */
  if(delen.length > 1 && WOORD_ARTIKELEN[eerste.toLowerCase()]){
    var rest = delen[1].split(" ").filter(Boolean);
    if(rest.length > 1 && WOORD_ARTIKELEN[rest[0].toLowerCase()]) rest.shift();
    if(rest.length) return eerste + " " + rest.join(" ");
  }
  return eerste;
}
function esVormen(es){''')

    # de zes aanroepers
    rep("""    var es = String(w.es || "").split("/")[0].split("(")[0].trim();
    if(/^(el|la|los|las|un|una)\\s/i.test(es)) return "zn";""",
"""    var es = woordEerste(w.es).split("(")[0].trim();
    if(/^(el|la|los|las|un|una)\\s/i.test(es)) return "zn";""")

    rep("""    var delen = w.es.toLowerCase().split("/")[0].trim().split(" ").filter(function(t){ return !artikelen[t]; });
    if(delen.length !== 1) return; // uitdrukkingen van meer woorden passen niet in een woordenzoeker""",
"""    var delen = woordEerste(w.es).toLowerCase().trim().split(" ").filter(function(t){ return !artikelen[t]; });
    if(delen.length !== 1) return; // uitdrukkingen van meer woorden passen niet in een woordenzoeker""")

    rep("""  var kern = w.es.toLowerCase().split("/")[0].trim().split(" ").filter(function(t){ return !artikelen[t]; });""",
        """  var kern = woordEerste(w.es).toLowerCase().trim().split(" ").filter(function(t){ return !artikelen[t]; });""")

    rep("""  var delen = w.es.toLowerCase().split("/")[0].trim().split(" ");""",
        """  var delen = woordEerste(w.es).toLowerCase().trim().split(" ");""")

    rep("""    var kern = w.es.toLowerCase().split("/")[0].trim().split(" ")[0];""",
        """    var kern = woordEerste(w.es).toLowerCase().trim().split(" ")[0];""")

    rep("""    var es = w.es.split("/")[0].trim();
    var nl = wTrans(w).split("/")[0].trim();""",
"""    /* v23.245: woordEerste() en niet split("/")[0]. Bij "el / la cantante" gaf die regel het woord
       "el", en dan staat er een memorykaart met een lidwoord op. Zie de kop bij woordEerste(). */
    var es = woordEerste(w.es);
    var nl = wTrans(w).split("/")[0].trim();""")

    # ---------------------------------------------------------------- 2. de index komt van de knop
    rep("""function keuzeMarkeer(knoppen, juist, gekozen){
  if(!knoppen) return;
  var i, m;
  for(i = 0; i < knoppen.length; i++){
    if(!knoppen[i] || !knoppen[i].classList) continue;
    knoppen[i].classList.remove("juist");
    knoppen[i].classList.remove("jouw");
    m = keuzeMerk(i, juist, gekozen);
    if(m) knoppen[i].classList.add(m);
  }
}""",
"""/* v23.245: DE INDEX KOMT VAN DE KNOP ZELF EN NIET VAN ZIJN PLEK IN DE RIJ.

   Deze functie markeerde op positie: de hoeveelste knop tegen het hoeveelste antwoord. Voor vier van
   de vijf schermen klopt dat. Het luisterscherm SCHUDT zijn opties (v._orde) en zet de
   oorspronkelijke index in data-ai; daar is de hoeveelste knop dus niet het hoeveelste antwoord.

   Stefan, 6 september: "bij de luisteroefening maakt hij nu standaard altijd de bovenste groen maar
   het lijkt niet gekoppeld te zijn aan het goede of foute antwoord." Klopt, en het is mijn fout van
   v23.238: ik repareerde daar de klassen en sloopte de index. Omdat het juiste antwoord in deze data
   meestal index 0 heeft, kleurde vrijwel altijd de bovenste knop.

   Nu draagt elke keuzeknop data-keuze met zijn eigen antwoordindex en leest deze functie die.
   Daarmee hoeft geen enkele aanroeper te weten of zijn scherm schudt, en een scherm dat gaat
   schudden hoeft hier niets voor aan te passen. */
function keuzeMarkeer(knoppen, juist, gekozen){
  if(!knoppen) return;
  var i, m, eigen, idx;
  for(i = 0; i < knoppen.length; i++){
    if(!knoppen[i] || !knoppen[i].classList) continue;
    knoppen[i].classList.remove("juist");
    knoppen[i].classList.remove("jouw");
    eigen = knoppen[i].getAttribute ? knoppen[i].getAttribute("data-keuze") : null;
    idx = (eigen === null || eigen === "" || isNaN(+eigen)) ? i : +eigen;
    m = keuzeMerk(idx, juist, gekozen);
    if(m) knoppen[i].classList.add(m);
  }
}""")

    # de knoppen dragen hun eigen index
    rep("""        return "<button type='button' class='opt audOpt' data-ai='" + i + "'>" + opties[i] + "</button>";""",
"""        /* v23.245: data-keuze naast data-ai. De opties staan geschud, dus de plek van de knop zegt
           niets over welk antwoord het is; keuzeMarkeer() leest dit attribuut. */
        return "<button type='button' class='opt audOpt' data-ai='" + i + "' data-keuze='" + i + "'>" +
          opties[i] + "</button>";""")

if DOE_APP:
    for nodig in ["function woordEerste(", "var WOORD_ARTIKELEN", "data-keuze='\" + i + \"'",
                  'getAttribute("data-keuze")']:
        assert nodig in src, "ontbreekt: " + nodig
    # commentaar eruit voordat we tellen: een controle die zijn eigen toelichting leest, telt niets
    kaal = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
    # geen enkele plek haalt het woord nog met een kale split uit es
    for weg in ['w.es.split("/")[0]', 'String(w.es || "").split("/")[0]',
                'w.es.toLowerCase().split("/")[0]']:
        assert weg not in kaal, "er staat nog een kale split op een woord: " + weg
    assert kaal.count("function woordEerste(") == 1, "woordEerste staat er meer dan een keer"
    assert kaal.count("woordEerste(") >= 7, "niet alle aanroepers zijn omgezet"
    APP.write_text(src, encoding="utf-8")
    print("index.html: een streep is niet altijd een keuze, en de index komt van de knop")
else:
    print("index.html: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
