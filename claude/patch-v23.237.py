#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.237 - de tekst en het woordenboek waren twee losse lijsten
#
# Stefan, 5 september, met een schermafbeelding van "aspas" uit Don Quijote hoofdstuk 4:
# "dit gaat niet goed, de woorden van de verhalen worden niet toegevoegd aan het woordenboek"
#
# NAGEMETEN, OVER DE HELE PLANK
#
# Alle 43 hoofdstukken door leesBetekenis() gehaald, het woord voor woord:
#
#     7900 woorden, 154 missers, 102 verschillende woorden
#
#     franco    10 hst  1441 woorden     0 missers    0%
#     chispa    13 hst  2986 woorden    16 missers  0,5%
#     cultura   10 hst  1695 woorden    53 missers  3,1%
#     quijote   10 hst  1778 woorden    85 missers  4,8%
#
# De twee reeksen die er het laatst bij kwamen zijn de twee met gaten. Dat is geen toeval: er was
# niets dat een nieuwe tekst tegenhield.
#
# WAT ER STRUCTUREEL MIS WAS
#
# LEES_EXTRA stond al vol met regels als:
#
#     besan:["kussen (van besar)"], votan:["stemmen (van votar)"], sonrie:["glimlacht (van sonreír)"]
#
# Elke nieuwe tekst voegde zijn eigen VORMEN toe aan een lijst die woorden hoort te bevatten. Dat
# schaalt niet en het is ook niet nodig: dat "besan" bij "besar" hoort is een regel, geen feit.
#
# Daarom eerst twee regels, en pas daarna data.
#
#   REGEL A  Vastgeplakte voornaamwoorden gaan eraf. pedirte, imaginarla, mandarlo, iros,
#            confesarse, fíjate: vijftien van de 102, en alle toekomstige.
#   REGEL B  Een onbekende vorm wordt teruggebracht tot een infinitief die de app al kent. Hij
#            staat helemaal achteraan, ná alles wat er al was, dus geen enkel woord dat nu een
#            antwoord krijgt, krijgt een ander antwoord. Hij kan alleen iets vinden waar nu
#            "staat niet in het woordenboek" staat.
#
# En dan de data: de woorden die echt ontbreken, met de hand nagelopen in hun eigen zin. Want
# "práctico" in "el ventero es un hombre práctico" is het bijvoeglijk naamwoord en niet een vorm van
# practicar, en een verkeerde diagnose is erger dan geen. Alle infinitieven die ontbraken zijn erbij
# gezet in plaats van hun vormen, zodat regel B de rest doet.
#
# EN EEN POORT, WANT DIT IS DE KERN VAN DE KLACHT
#
# Er was niets dat een tekst tegenhield waarvan de woorden niet op te zoeken zijn. Nu wel:
# pw-woordendekking.js loopt alle hoofdstukken langs en eist NUL missers. Geen uitzonderingslijst,
# ook niet voor de geluiden: pum, shhh en pío staan er gewoon in, met de eerlijke uitleg dat het een
# geluid is. Een uitzonderingslijst is een lijst die groeit.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.237"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function leesZonderClitica(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- de twee regels
REGELS = r"""
/* ================= DE TEKST EN HET WOORDENBOEK WAREN TWEE LOSSE LIJSTEN (v23.237) =================

   Stefan, 5 september, met een schermafbeelding van "aspas" uit Don Quijote 4: "dit gaat niet goed,
   de woorden van de verhalen worden niet toegevoegd aan het woordenboek."

   Nagemeten over alle 43 hoofdstukken: 7900 woorden, 154 missers, 102 verschillende. Franco 0
   procent, Chispa 0,5, Cultura 3,1, Quijote 4,8. De twee reeksen die er het laatst bij kwamen zijn
   de twee met gaten, en dat is geen toeval: er was niets dat een nieuwe tekst tegenhield.

   Onder in LEES_EXTRA stonden regels als besan:["kussen (van besar)"] en votan:["stemmen (van
   votar)"]. Elke nieuwe tekst voegde zijn eigen VORMEN toe aan een lijst die woorden hoort te
   bevatten. Dat schaalt niet, en het hoeft ook niet: dat "besan" bij "besar" hoort is een regel.

   Deze twee functies zijn die regel. Ze staan helemaal achteraan in leesBetekenis(), ná alles wat er
   al was, dus geen enkel woord dat nu een antwoord krijgt, krijgt een ander antwoord. Ze kunnen
   alleen iets vinden waar tot nu toe "staat niet in het woordenboek" stond. */

/* Twee achter elkaar kan ook: dármelo, decírselo. De langste eerst, anders haalt "lo" er bij
   "dármelo" alleen het laatste stukje af en houd je "dárme" over. */
var LEES_CLITICA = ["melo","mela","melos","melas","telo","tela","telos","telas",
                    "selo","sela","selos","selas","noslo","nosla","noslos","noslas",
                    "los","las","les","nos","me","te","se","lo","la","le","os"];
function leesZonderClitica(plat){
  var uit = [], i, c, stam;
  for(i = 0; i < LEES_CLITICA.length; i++){
    c = LEES_CLITICA[i];
    if(plat.length <= c.length + 1) continue;
    if(plat.slice(-c.length) !== c) continue;
    stam = plat.slice(0, plat.length - c.length);
    /* Een infinitief of een gerundio herken je aan zijn eind, en dan is het zeker een vastgeplakt
       voornaamwoord. Alles wat daar niet aan voldoet gaat als kandidaat mee (fíjate laat "fija"
       achter, en dat is een gebiedende wijs) maar dan moet regel B er nog iets van maken. */
    if(/(ar|er|ir)$/.test(stam) || /(ando|iendo|yendo)$/.test(stam)) uit.unshift(stam);
    else if(stam.length >= 3) uit.push(stam);
  }
  return uit;
}
/* De uitgangen per klasse. Dit was eerst "hak één tot zes letters van het eind en plak ar, er of ir
   erop", en dat is te grof gebleken: van "redondo" maakte hij een vorm van reír (re + ir), van
   "refrán" ook, en van "cabecera" een vorm van caber. Die zes woorden staan toevallig in de lijst,
   dus het viel niet op, maar het volgende onbekende woord dat met "re" begint zou "lachen" hebben
   betekend. Een verkeerde diagnose is erger dan geen.

   Nu moet het afgehakte stuk een échte uitgang zijn. De y-uitgangen staan erbij omdat huir en leer
   die nodig hebben: huyen, leyeron, leyendo. */
var LEES_UITGANGEN = {
  ar: ["o","as","a","amos","ais","an",
       "e","es","emos","eis","en",
       "aste","asteis","aron","o",
       "aba","abas","abamos","abais","aban",
       "ado","ada","ados","adas","ando",
       "are","aras","ara","aremos","areis","aran",
       "aria","arias","ariamos","ariais","arian",
       "ase","ases","asemos","aseis","asen","aramos","ad"],
  er: ["o","es","e","emos","eis","en",
       "a","as","amos","an",
       "i","iste","io","imos","isteis","ieron",
       "ia","ias","iamos","iais","ian",
       "ido","ida","idos","idas","iendo",
       "ere","eras","era","eremos","ereis","eran",
       "eria","erias","eriamos","eriais","erian",
       "iera","ieras","ieramos","ieran","ed",
       "yo","yes","ye","yen","yeron","yendo","yera","yeras"],
  ir: ["o","es","e","imos","is","en",
       "a","as","amos","an",
       "i","iste","io","isteis","ieron",
       "ia","ias","iamos","iais","ian",
       "ido","ida","idos","idas","iendo",
       "ire","iras","ira","iremos","ireis","iran",
       "iria","irias","iriamos","iriais","irian",
       "iera","ieras","ieramos","ieran","id",
       "yo","yes","ye","yen","yeron","yendo","yera","yeras"]
};
/* Een onbekende vorm terugbrengen tot een infinitief die de app AL kent. Die voorwaarde is het hele
   veiligheidsmechanisme: hij verzint geen werkwoorden, hij vindt alleen wat er al ligt. En hij komt
   pas aan de beurt als het woordenboek, de lessen, de frequentielijst, de vormanalyse en de
   meervouds- en geslachtsvarianten allemaal niets hadden. */
function leesNaarInfinitief(plat){
  var klassen = ["ar","er","ir"], k, i, u, stam, inf, hit;
  for(k = 0; k < klassen.length; k++){
    u = LEES_UITGANGEN[klassen[k]];
    for(i = 0; i < u.length; i++){
      if(plat.length <= u[i].length + 1) continue;
      if(plat.slice(-u[i].length) !== u[i]) continue;
      stam = plat.slice(0, plat.length - u[i].length);
      inf = stam + klassen[k];
      if(inf === plat) continue;
      if(LEES_EXTRA[inf]) return {inf:inf, nl:ct(LEES_EXTRA[inf][0], LEES_EXTRA[inf][1])};
      hit = leesLesWoord(inf) || leesFreqZoek(inf);
      if(hit) return {inf:hit.es, nl:hit.nl, id:hit.id};
    }
  }
  return null;
}
"""

# ---------------------------------------------------------------- de ontbrekende woorden
# Elk woord in zijn eigen zin nagelopen; de zin staat erbij waar de keuze niet vanzelf spreekt.
NIEUWE_WOORDEN = [
    # --- geluiden. Geen uitzonderingslijst maar gewoon een eerlijk antwoord. ---
    ("pum", "boem (een geluid, geen woord)", "boom (a sound, not a word)"),
    ("shhh", "sjjj (een geluid, geen woord)", "shhh (a sound, not a word)"),
    ("pio", "piep (het geluid van een vogel)", "cheep (the sound of a bird)"),
    # --- Don Quijote: de wereld van het boek ---
    ("armadura", "het harnas", "the suit of armour"),
    ("armar", "tot ridder slaan, bewapenen", "to knight, to arm"),
    ("desvan", "de zolder", "the attic"),
    ("yelmo", "de helm", "the helmet"),
    ("bacia", "het scheerbekken (de metalen schaal van de barbier)",
     "the barber's basin (the metal bowl of the barber)"),
    ("baciyelmo", "scheerhelm: het woord dat ze verzinnen om niet te hoeven kiezen tussen bacía en yelmo",
     "basin-helmet: the word they invent so they need not choose between bacía and yelmo"),
    ("barbero", "de barbier", "the barber"),
    ("ventero", "de waard (de baas van de herberg)", "the innkeeper"),
    ("viajero", "de reiziger", "the traveller"),
    ("escudero", "de schildknaap", "the squire"),
    ("labrador", "de boer, de landarbeider", "the farmhand, the labourer"),
    ("mago", "de tovenaar", "the wizard"),
    ("noble", "edel; een edelman", "noble; a nobleman"),
    ("refran", "het spreekwoord", "the proverb"),
    ("galera", "de galei (het roeischip van de koning)", "the galley (the king's rowing ship)"),
    ("remar", "roeien", "to row"),
    ("preso", "de gevangene; gevangen", "the prisoner; imprisoned"),
    ("forzado", "gedwongen", "forced, against your will"),
    ("liberar", "bevrijden", "to free, to release"),
    ("obedecer", "gehoorzamen", "to obey"),
    ("vencedor", "de winnaar", "the winner, the victor"),
    ("humillar", "vernederen", "to humiliate"),
    ("dolorido", "met pijn, beurs", "sore, aching"),
    ("tumbar", "neerleggen, neerhalen", "to knock down, to lay down"),
    ("atar", "vastbinden", "to tie up"),
    ("aguantar", "inhouden, verdragen", "to hold back, to bear"),
    ("quemar", "verbranden", "to burn"),
    ("aparecer", "verschijnen, opduiken", "to appear"),
    ("aspa", "de wiek (van een molen)", "the sail (of a windmill)"),
    ("mojarse", "nat worden", "to get wet"),
    ("afeitar", "scheren", "to shave"),
    ("proponer", "voorstellen", "to propose, to suggest"),
    ("convencer", "overtuigen", "to convince"),
    ("huir", "vluchten", "to flee"),
    ("marchar", "weggaan, vertrekken", "to leave, to march off"),
    ("confesarse", "biechten", "to confess (to a priest)"),
    ("notario", "de notaris", "the notary"),
    ("testamento", "het testament", "the will, the testament"),
    ("antano", "vroeger, van weleer", "of long ago, of yesteryear"),
    ("cuerdo", "helder van geest, bij zijn verstand", "sane, clear-headed"),
    ("calcular", "berekenen, inschatten", "to calculate, to reckon"),
    ("confundir", "verwarren, in de war brengen", "to confuse"),
    ("imaginar", "je voorstellen", "to imagine"),
    ("curar", "genezen, beter maken", "to cure, to heal"),
    # fijar naast fijarse: "fíjate" laat na regel A "fija" achter, en regel B zoekt dan een
    # infinitief die letterlijk zo heet. Wie alleen het wederkerende werkwoord opschrijft, laat het
    # gebiedende "fíjate" staan waar de lezer hem tegenkomt.
    ("fijar", "vastzetten; fíjate = let op, kijk", "to fix; fíjate = look, notice"),
    ("rien", "lachen (van reírse)", "laugh (from reírse)"),
    ("fijarse", "opletten, kijken naar", "to notice, to pay attention"),
    # --- Cultura: het land en de taal ---
    ("apellido", "de achternaam", "the surname"),
    ("confusion", "de verwarring", "the confusion"),
    ("sorprendente", "verrassend", "surprising"),
    ("castellano", "het Castiliaans (het Spaans van heel Spanje)",
     "Castilian (the Spanish of all of Spain)"),
    ("gallego", "het Galicisch; Galicisch", "Galician (the language and the adjective)"),
    ("catalan", "het Catalaans; Catalaans", "Catalan (the language and the adjective)"),
    ("euskera", "het Baskisch", "Basque (the language)"),
    ("portugues", "het Portugees; Portugees", "Portuguese"),
    ("latin", "het Latijn", "Latin"),
    ("region", "de streek, de regio", "the region"),
    ("cartel", "het bord, de poster", "the sign, the poster"),
    ("nombrar", "benoemen, een naam geven aan", "to name, to call"),
    ("verbo", "het werkwoord", "the verb"),
    ("pronombre", "het voornaamwoord", "the pronoun"),
    ("tutear", "tutoyeren, iemand met tú aanspreken", "to address someone as tú"),
    ("siesta", "de siësta, het middagdutje", "the siesta, the afternoon nap"),
    ("mediodia", "de middag, het midden van de dag", "midday, noon"),
    ("baston", "de wandelstok", "the walking stick"),
    ("funcion", "de functie, het doel", "the function, the purpose"),
    ("orquesta", "het orkest, de band", "the band, the orchestra"),
    ("colgar", "hangen, ophangen", "to hang"),
    ("cabecera", "het hoofd van de tafel", "the head of the table"),
    ("guarderia", "de kinderopvang, het kinderdagverblijf", "the day nursery, the daycare"),
    ("sed", "de dorst", "thirst"),
    ("saludar", "groeten", "to greet"),
    ("contestar", "antwoorden", "to answer"),
    # práctico is hier het bijvoeglijk naamwoord ("el ventero es un hombre práctico") en niet een
    # vorm van practicar. Zonder deze regel zou regel B er het werkwoord van maken, en dat is precies
    # het soort verkeerde diagnose dat erger is dan geen antwoord.
    ("practico", "praktisch, nuchter", "practical, down to earth"),
    ("larguisimo", "hartstikke lang (largo + ísimo)", "very long indeed (largo + ísimo)"),
    # --- de getallen die ontbraken ---
    ("once", "elf (11)", "eleven (11)"),
    ("catorce", "veertien (14)", "fourteen (14)"),
    ("dieciseis", "zestien (16)", "sixteen (16)"),
    # de honderdtallen buigen mee met het geslacht, en geen enkele meervoudsregel maakt van
    # trescientas trescientos. Twee regels dus, want dat zijn het in het Spaans ook.
    ("trescientos", "driehonderd (300)", "three hundred (300)"),
    ("trescientas", "driehonderd (300, bij vrouwelijke woorden)",
     "three hundred (300, with feminine nouns)"),
]


def _regels_data():
    uit = []
    for w, nl, en in NIEUWE_WOORDEN:
        uit.append(' %s:[%s,%s],' % (w, _js(nl), _js(en)))
    return "\n".join(uit)


def _js(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


if DOE_APP:
    # 1. de twee regels, vlak vóór leesBetekenis
    rep("function leesBetekenis(ruw){", REGELS.strip() + "\nfunction leesBetekenis(ruw){")

    # 2. ze komen pas aan de beurt als al het bestaande niets had
    rep("""  hit = leesUitdrukking(plat);
  if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"les", uitdrukking:true};
  return null;
}""",
"""  hit = leesUitdrukking(plat);
  if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"les", uitdrukking:true};
  /* v23.237, regel A: een vastgeplakt voornaamwoord eraf, en dan het kale woord opzoeken. Eerst
     langs de lijsten (pedirte is pedir), en anders alsnog langs regel B (fíjate laat fija achter). */
  var kaal = leesZonderClitica(plat), ki, kw;
  for(ki = 0; ki < kaal.length; ki++){
    kw = kaal[ki];
    if(LEES_EXTRA[kw]) return {es:kw, nl:ct(LEES_EXTRA[kw][0], LEES_EXTRA[kw][1]), soort:"vorm"};
    hit = leesLesWoord(kw) || leesFreqZoek(kw);
    if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"vorm"};
  }
  /* v23.237, regel B: terugbrengen tot een infinitief die de app al kent. Ook voor de kale vormen
     die regel A overhield. */
  var inf = leesNaarInfinitief(plat);
  for(ki = 0; !inf && ki < kaal.length; ki++) inf = leesNaarInfinitief(kaal[ki]);
  if(inf) return {es:inf.inf, nl:inf.nl, id:inf.id, soort:"vorm"};
  return null;
}""")

    # 3. de vormen die de regel nu zelf doet, gaan eruit. Elf regels die er alleen stonden omdat een
    #    tekst ze nodig had; de infinitief staat er in alle elf gevallen al naast.
    for weg in ['explota:["ontploft (van explotar)","explodes (from explotar)"],',
                'brilla:["schittert (van brillar)","shines (from brillar)"],',
                'tararea:["neuriet (van tararear)","hums (from tararear)"],',
                'luche:["vecht (van luchar)","fight (from luchar)"],',
                'observando:["kijkend, observerend","watching, observing"],',
                'bombardean:["bombarderen (van bombardear)","bomb (from bombardear)"],',
                'bombardea:["bombardeert (van bombardear)","bombs (from bombardear)"],',
                'besan:["kussen (van besar)","kiss (from besar)"],',
                'reacciona:["reageert (van reaccionar)","reacts (from reaccionar)"],',
                'votan:["stemmen (van votar)","vote (from votar)"],',
                'votado:["gestemd (van votar)","voted (from votar)"],']:
        if weg in src:
            rep("\n " + weg, "")
        elif ("\n " + weg.rstrip(",")) in src:
            rep("\n " + weg.rstrip(","), "")

    # 3b. de woorden die er echt niet in stonden
    rep(""" abrirse:["opengaan","to open up"], pequenita:["heel klein","very small"]""",
        """ abrirse:["opengaan","to open up"], pequenita:["heel klein","very small"],
 /* v23.237: de woorden van de leesplank die nergens in stonden. Gemeten over alle 43 hoofdstukken,
    elk woord nagelopen in zijn eigen zin. Wat een INFINITIEF is staat hier als infinitief en niet
    als vorm: leesNaarInfinitief() maakt van armar vanzelf armado, en van saludar saluda en saludan.
    Wie hier een vorm bijzet in plaats van zijn woord, doet werk dat de regel al doet. */
""" + _regels_data().rstrip(","))

if DOE_APP:
    for nodig in ["function leesZonderClitica(", "function leesNaarInfinitief(",
                  "var LEES_CLITICA", "leesZonderClitica(plat)", "leesNaarInfinitief(plat)"]:
        assert nodig in src, "ontbreekt: " + nodig
    # de nieuwe regels staan ACHTER alles wat er al was: geen bestaand woord verandert van antwoord
    blok = src[src.index("function leesBetekenis(ruw){"):]
    blok = blok[:blok.index("\n}\n")]
    assert blok.index("leesUitdrukking(plat)") < blok.index("leesZonderClitica(plat)"), \
        "regel A dringt voor op het woordenboek"
    assert blok.index("leesZonderClitica(plat)") < blok.index("leesNaarInfinitief(plat)"), \
        "regel B komt vóór regel A"
    # en de data staat er als woord, niet als vorm
    for vorm in ["saluda:", "saludan:", "armado:", "queman:", "aparecen:"]:
        assert vorm not in src, "een vorm in plaats van een woord: " + vorm
    APP.write_text(src, encoding="utf-8")
    print("index.html: twee regels en %d woorden erbij" % len(NIEUWE_WOORDEN))
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
