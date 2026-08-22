#!/usr/bin/env python3
# v23.166 - de map waar een opname staat is een eigenschap van het boek
#
# Stefan, 22 aug: "check ook dat het goed gaat, dan doet de voorspelling het maar ook de audio bijv
# bij het leesboek."
#
# GEMETEN
#
# audio/boek/ bevat 13 bestanden: precies de dertien Chispa-hoofdstukken. De acht hoofdstukken van
# Un año en Cádiz (v23.157) hebben er geen, en de zes recepten evenmin. audio/hist/ is compleet
# (10 van 10). Het gaat dus om acht hoofdstukken, 9.381 tekens.
#
# De oorzaak is dezelfde vorm als bij de zes luisterscenes van gisteren: tools/generate-boek-audio.js
# is handwerk met een sleutel uit je eigen terminal, en geen enkele workflow raakte het aan. In de
# kop van avondrun-audio.js stond het zelfs als besluit: "Het boek staat er bewust niet bij. Dat
# groeit niet vanzelf; een nieuw hoofdstuk is een besluit dat Stefan neemt, en dan draai je het
# script met de hand." Die aanname is gemeten onwaar. Niemand draait het, en dat is geen slordigheid
# maar precies wat je verwacht: een stap die alleen bestaat als iemand eraan denkt, gebeurt niet.
#
# EN TOEN VIEL ER IETS ANDERS OP
#
# Bij het aanzetten bleek dat drie plekken los van elkaar opschrijven in welke map de opname van een
# hoofdstuk hoort:
#
#   index.html, boekSpreek()          hist- -> audio/hist, receta- -> audio/receta, rest -> audio/boek
#   tools/generate-boek-audio.js      hist- -> hist, rest -> boek
#   tools/avondrun-audio.js           hist- eruit, rest -> boek
#
# Ze zijn het niet eens. De app zoekt de recepten in audio/receta/, de generator schrijft ze in
# audio/boek/, en een receta-stem bestaat helemaal niet. In de praktijk gebeurt er niets, want de
# recepten hebben stem:false en dus geen luisterknop. Maar het is één feit dat op drie plekken
# opnieuw wordt opgeschreven, en dan is de vraag niet óf het misgaat maar wanneer. Was dit blijven
# staan, dan had de nachtrun vannacht zes recepten ingesproken (4.850 tekens) in een map waar de app
# nooit kijkt.
#
# WAT ER VERANDERT
#
# De map wordt een veld van de reeks, op de boekenplank waar de rest van wat een reeks is ook staat.
# Wie een verteller heeft (stem:true) krijgt een map; wie er geen heeft (de recepten) krijgt er ook
# geen, want een map voor geluid dat nooit klinkt is precies de fantoomafspraak die hier misging.
#
# Daarmee is het weer de regel van het huis: staat een feit in de data, dan schrijft geen enkele
# codeplek dat feit opnieuw. De drie lezers (de app, de handgenerator, de nachtrun) lezen nu alle
# drie dezelfde regel, en pw-stem.js gaat rood zodra ze uit elkaar lopen.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.166"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # -----------------------------------------------------------------------
    # 1. de plank vertelt zelf waar de stem van een reeks staat
    # -----------------------------------------------------------------------
    rep('''/* ================= DE BOEKENPLANK (v23.26) =================
   Een reeks is een boek. Ze staan hier los van de hoofdstukken zelf, want een hoofdstuk hoort te
   weten waar het over gaat en niet hoe de kast eruitziet. */''',
        '''/* ================= DE BOEKENPLANK (v23.26) =================
   Een reeks is een boek. Ze staan hier los van de hoofdstukken zelf, want een hoofdstuk hoort te
   weten waar het over gaat en niet hoe de kast eruitziet.

   v23.166: en de reeks vertelt ook wie hem inspreekt. stem:false is "geen verteller, geen knop";
   map is de map onder audio/ waar zijn opnames staan. Dat stond hiervoor drie keer los opgeschreven
   (boekSpreek hier, groepVan in generate-boek-audio.js, de filterregel in avondrun-audio.js) en die
   drie waren het al niet meer eens: de app zocht de recepten in audio/receta/, de generator schreef
   ze in audio/boek/, en een receta-stem bestond niet. Onschadelijk omdat de recepten geen knop
   hebben, maar zo begint elk verschil dat later wel iets kost. Een reeks zonder verteller krijgt
   dus ook geen map: geluid dat nooit klinkt hoort nergens te staan. */''')

    rep(''' {id:"chispa", pre:"boek-", nl:"Chispa", en:"Chispa", stem:true,''',
        ''' {id:"chispa", pre:"boek-", nl:"Chispa", en:"Chispa", stem:true, map:"boek",''')

    rep(''' {id:"cadiz", pre:"cadiz-", nl:"Un año en Cádiz", en:"Un año en Cádiz", stem:true,''',
        ''' /* Dezelfde verteller en dus dezelfde map als Chispa: het manifest houdt de stem per map bij,
     dus een eigen map zou betekenen dat je een tweede stem moet kiezen voordat er iets klinkt. */
 {id:"cadiz", pre:"cadiz-", nl:"Un año en Cádiz", en:"Un año en Cádiz", stem:true, map:"boek",''')

    rep(''' {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco", stem:true,''',
        ''' {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco", stem:true, map:"hist",''')

    # -----------------------------------------------------------------------
    # 2. boekSpreek() leest de map, in plaats van hem opnieuw af te leiden
    # -----------------------------------------------------------------------
    rep('''    /* v23.27: de geschiedenisreeks heeft een eigen verteller en dus een eigen map. Het voorvoegsel
       van het id bepaalt waar we zoeken, net zoals de boekenplank er de reeks aan herkent. Ontbreekt
       het bestand, dan valt de app terug op de voorleesstem van de browser; dat was al zo. */
    /* v23.81: derde reeks. Elke reeks heeft zijn eigen verteller en dus zijn eigen map; het
       voorvoegsel van het id bepaalt welke. */
    var pre = String(h.id);
    var map = pre.indexOf("hist-") === 0 ? "hist" : pre.indexOf("receta-") === 0 ? "receta" : "boek";''',
        '''    /* v23.166: welke map, dat weet de reeks. Hier stond die vraag voor de derde keer beantwoord,
       als een rij voorvoegsels, en die rij was het niet eens met de twee andere plekken (zie de kop
       bij LEES_REEKSEN). Ontbreekt het bestand, dan valt de app terug op de voorleesstem van de
       browser; dat was al zo en blijft zo. */
    var reeks = leesReeksVan(h);
    var map = (reeks && reeks.map) || "boek";''')

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
