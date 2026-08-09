#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.23: tien hoofdstukken over de jaren van Franco, en losse letters zijn ook op te zoeken.

Stefan was door de Chispa-verhalen heen en vroeg om lezen over cultuur en geschiedenis, tijdloos in
plaats van dagelijks nieuws, zodat je na tien of twaalf hoofdstukken ook echt iets van een onderwerp
weet. Dit is de eerste reeks: Spanje van 1931 tot nu, in tien hoofdstukken van ongeveer 140 woorden.

Waarom tijdloos en niet dagelijks nieuws: nieuws vraagt elke dag een geslaagde generatie en een
externe bron, en de avondrun levert op dit moment nul dagen voorraad. Een functie die vaker leeg is
dan vol went snel af. Geschiedenis kan vooruit gemaakt worden en veroudert niet.

Het niveau is gemeten en niet geschat, met dezelfde telling als bij Chispa:

                        ken je zelf   opzoekbaar in de app
  Chispa                    56%              95%
  deze reeks                62%              91%

Dus iets makkelijker dan Chispa, en met de woordtik van v23.21 goed te doen. Per hoofdstuk zitten er
acht tot tien echt nieuwe woorden in (aceite, cartilla, racionamiento, obreros, montes, pacto), en
dat is ongeveer waar je wilt zitten: genoeg om iets te leren, weinig genoeg om te blijven lezen.

Ze verschijnen vanzelf als eigen blok in het leesmenu, want dat menu groepeert al op "deel". Er is
dus geen enkele schermwijziging voor nodig, alleen inhoud.

Meteen ook een kleinigheid uit v23.21: woorden van één letter (y, o, a) gaven "staat niet in het
woordenboek", omdat de opzoeker minstens twee letters eiste. Juist die woorden komen het vaakst voor.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if 'id:"hist-1"' in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


HIER = os.path.dirname(os.path.abspath(__file__))
with io.open(os.path.join(HIER, "hist-hoofdstukken.js"), encoding="utf-8") as f:
    HOOFDSTUKKEN = f.read()

# ---------------------------------------------------------------- 1. de hoofdstukken in BOOK
i = src.index("var BOOK = [")
j = src.index("\n];", i)
src = src[:j] + ",\n\n" + \
    "/* ================= ESPAÑA: LOS AÑOS DE FRANCO (v23.23) =================\n" \
    "   Tien hoofdstukken, geschreven binnen Stefans woordenschat en daarna nagerekend: 62 procent van\n" \
    "   de lopende woorden kent hij al, 91 procent is op te zoeken met de woordtik. Bij Chispa is dat\n" \
    "   56 en 95 procent, dus dit leest iets makkelijker en is even goed te ontsluiten.\n\n" \
    "   Het zijn geen losse teksten maar een reeks met een chronologie: wie ze op volgorde leest, weet\n" \
    "   aan het eind waarom er in Spanje nog steeds graven worden geopend. Dat was de opdracht: na tien\n" \
    "   hoofdstukken ook echt iets van het onderwerp weten.\n\n" \
    "   Feitelijk gehouden en zonder oordeel over personen. Waar iets omstreden is (het pacto del\n" \
    "   olvido) staat het als keuze beschreven en niet als vanzelfsprekendheid. */\n" + \
    HOOFDSTUKKEN.strip("\n").rstrip(",") + src[j:]

# ---------------------------------------------------------------- 2. losse letters ook opzoeken
rep(
    """function leesBetekenis(ruw){
  var plat = stripAcc(String(ruw || "").toLowerCase()).replace(/[^a-z]/g, "");
  if(plat.length < 2) return null;""",
    """function leesBetekenis(ruw){
  var plat = stripAcc(String(ruw || "").toLowerCase()).replace(/[^a-z]/g, "");
  /* v23.23: hier stond een ondergrens van twee letters, overgenomen van de zoekfunctie. Daar is die
     terecht (op een letter zoeken geeft duizend treffers), hier niet: y, o en a zijn juist woorden
     die op elke bladzijde staan, en die kreeg je dus als enige nooit uitgelegd. Ze staan ook in geen
     enkele lijst die de app heeft, want een frequentielijst begint pas bij twee letters. Vijf regels
     data dus, en dan is de bladzijde compleet. */
  if(!plat) return null;
  if(LEES_LETTERS[plat]) return {es:plat, nl:ct(LEES_LETTERS[plat][0], LEES_LETTERS[plat][1]), soort:"woordenboek"};""")

# ---------------------------------------------------------------- 3. de woorden van een letter
rep(
    """var leesFreqIdx = null;""",
    """/* Woorden van een letter. Ze staan in geen enkele lijst die de app heeft, en juist die kwamen op
   elke bladzijde langs. e en u zijn de vormen van y en o voor een woord dat met dezelfde klank
   begint: padres e hijos, siete u ocho. */
var LEES_LETTERS = {y:["en","and"], o:["of","or"], a:["naar, aan, tot","to, at"],
                    e:["en (voor i- of hi-)","and (before i- or hi-)"],
                    u:["of (voor o- of ho-)","or (before o- or ho-)"]};
var leesFreqIdx = null;""")

rep('var APP_VERSIE = "v23.22";', 'var APP_VERSIE = "v23.23";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.23 toegepast op", PAD)
