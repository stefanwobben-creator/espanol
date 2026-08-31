#!/usr/bin/env python3
# v23.216 - de val blijft weg, ook als de volgende schrijver hem er weer in legt
#
# Stefan, 30 aug: "de drie actions aan de praat lijkt me het belangrijkste toch nu?"
#
# WAT ER ECHT AAN DE HAND WAS
#
# De diagnose die er lag ("de nachtelijke Actions zijn dood") klopte niet. In GitHub staat:
#
#   logboek.yml      34 runs, 34 groen, elke nacht, ook de laatste vier
#   curriculum.yml   32 runs; #25 t/m #32 (23 t/m 30 aug) allemaal rood, elke nacht 12 a 13 minuten
#
# Ze draaien dus allebei. De avondrun valt om, en zijn eigen hartslag zegt waarom:
#
#     "AFGEKEURD:\n - telling klopt niet na schrijven: sentences — bestand teruggedraaid"
#
# pasToe() schrijft de nieuwe content weg, leest het bestand opnieuw in en telt na. Klopt de telling
# niet, dan draait hij alles terug. Acht nachten lang klopte de telling van SENTENCES niet.
#
# DE OORZAAK, IN EEN TEKEN
#
# Nagespeeld met twee doodgewone proefzinnen, zonder taalmodel:
#
#     voor 271 -> na het invoegen van 2 zinnen: 274
#
# Drie erbij in plaats van twee. voegToeAanArray() plakt onvoorwaardelijk ",\n" achter het laatste
# element. Staat er al een komma, dan krijg je ",," en dat is in JavaScript geen scheidingsteken
# maar een overgeslagen plek: [1,2,,] heeft lengte 3. De telling klopt dan met precies een te veel,
# en de run draait zichzelf terug.
#
# En de staarten van de vier arrays, zoals ze op main stonden:
#
#     WORDS       ..."tag":"general"}\n];       schoon
#     SENTENCES   ..."tag": "salud"},\n];       KOMMA
#     QUIZZES     ...indefinido."}]}\n];        schoon
#     CHEATSHEET  ...menos ... que</i>.</p>"}\n];  schoon
#
# Precies een, en precies degene die de hartslag elke nacht noemde.
#
# WAAR HIJ VANDAAN KWAM
#
# Uitgezocht over zestig commits: de komma verschijnt in `24ddb0c`, "content-update 25 aug
# (v23.195): vier drillzinnen". Dat is de geplande Claude-nachttaak, die zinnen met de hand aan de
# array plakt en er een komma achter liet staan. Vanaf die nacht kon de avondrun geen enkele zin
# meer publiceren.
#
# Twee nachtsystemen op dezelfde array, waarvan de een een teken achterlaat waar de ander over
# struikelt. Dat de twee elkaar in de weg zitten stond al in de kop van curriculum.yml (28 aug);
# dit is de eerste keer dat het hard te zien is.
#
# 31 AUGUSTUS: DE KOMMA IS AL WEG, DE VAL NIET
#
# Tussen het schrijven van deze ronde en het aanbrengen ervan draaide de geplande nachttaak. Die
# heeft de komma zelf opgeruimd en als v23.215 gepubliceerd; alle vier de arrays op main eindigen nu
# schoon. Punt 1 hieronder is daarmee een lege handeling geworden en de patch slaat hem netjes over.
#
# Punt 2, 3 en 4 blijven onverkort nodig, en dat is de hele reden dat deze ronde alsnog doorgaat.
# De nachttaak plakt elke nacht met de hand zinnen aan diezelfde array. Ruimt hij de komma de
# volgende keer niet op, dan ligt de val er weer, en dan is er opnieuw niets in de code dat hem
# tegenhoudt en niets in de melding dat hem aanwijst. De inhoud is gerepareerd; het mechanisme
# nog niet.
#
# WAT DEZE RONDE DOET
#
# 1. De komma weg, als hij er nog ligt (op 31 augustus niet meer).
# 2. voegToeAanArray() kijkt voortaan wat er staat in plaats van aan te nemen wat er staat. Anders
#    ligt de val er morgen weer, want de nachttaak schrijft gewoon door.
# 3. De telling zegt voortaan wat hij verwachtte en wat hij vond, per lijst. Acht nachten lang stond
#    er alleen "sentences", en dat is het verschil tussen een melding en een diagnose.
# 4. Een zelftest die precies dit geval afdekt: invoegen in een array die al op een komma eindigt,
#    en invoegen in een lege array.
#
# WAT DEZE RONDE NIET DOET
#
# De mislukte rebase (waardoor de hartslag sinds 23 augustus niet meer op main kwam, en waardoor de
# 42 opnames van elke nacht werden weggegooid) staat hier bewust naast. Die verbergt het bewijs maar
# houdt geen content tegen, en hij verdient zijn eigen ronde met zijn eigen meting.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
LIB = W / "tools" / "content-lib.js"
NIEUW = "v23.216"

src = APP.read_text(encoding="utf-8")
lib = LIB.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = '"tag": "salud"},\n];' in src
DOE_LIB = "function staartVanArray(" not in lib
DOE_VER = _num(huidig_ver) < _num(NIEUW)

# =============================================================================================
# 1. de komma weg
# =============================================================================================
if DOE_APP:
    anker = '"tag": "salud"},\n];'
    assert src.count(anker) == 1, "anker %d keer" % src.count(anker)
    src = src.replace(anker, '"tag": "salud"}\n];', 1)
    APP.write_text(src, encoding="utf-8")
    print("index.html: de losse komma achter s275 is weg")
else:
    print("index.html: geen losse komma meer")

# =============================================================================================
# 2. de invoeger kijkt wat er staat
# =============================================================================================
if DOE_LIB:
    oud = """function voegToeAanArray(src, naam, items) {
  if (!items || !items.length) return src;
  const { sluit } = vindArray(src, naam);
  // laatste item krijgt een komma, nieuwe items komen elk op een eigen regel vóór de sluithaak
  const voor = src.slice(0, sluit).replace(/\\s*$/, "");
  const blok = items.map(jsonRegel).join(",\\n");
  return voor + ",\\n" + blok + "\\n" + src.slice(sluit);
}"""
    assert lib.count(oud) == 1, "anker in content-lib.js niet gevonden"
    nieuw = """/* 30 augustus. Wat staat er vlak vóór de sluithaak: een element, een komma, of niets?
   Deze vraag stond hier niet, en het antwoord werd aangenomen. Acht nachten lang plakte de
   invoeger hieronder een komma achter een komma, en ",," is in JavaScript geen scheidingsteken
   maar een overgeslagen plek: [1,2,,] heeft lengte 3. De telling na afloop kwam daardoor één te
   hoog uit, pasToe() draaide het bestand terug, en de avondrun publiceerde niets. */
function staartVanArray(src, sluit) {
  const voor = src.slice(0, sluit).replace(/\\s*$/, "");
  const laatste = voor[voor.length - 1];
  if (laatste === "[") return { voor, scheiding: "" };   // de array is leeg
  if (laatste === ",") return { voor, scheiding: "" };   // er staat al een komma
  return { voor, scheiding: "," };
}

function voegToeAanArray(src, naam, items) {
  if (!items || !items.length) return src;
  const { sluit } = vindArray(src, naam);
  // nieuwe items komen elk op een eigen regel vóór de sluithaak; of er een komma vóór moet, staat
  // in het bestand en niet in een aanname (zie staartVanArray hierboven)
  const { voor, scheiding } = staartVanArray(src, sluit);
  const blok = items.map(jsonRegel).join(",\\n");
  return voor + scheiding + "\\n" + blok + "\\n" + src.slice(sluit);
}"""
    lib = lib.replace(oud, nieuw, 1)

# =============================================================================================
# 3. de telling zegt wat hij verwachtte en wat hij vond
# =============================================================================================
if DOE_LIB:
    oud2 = """  const mis = Object.keys(verwacht).filter(k => na[k].length !== verwacht[k]);
  if (mis.length) {
    fs.writeFileSync(INDEX, voor.src);            // terugdraaien
    return { ok: false, fouten: ["telling klopt niet na schrijven: " + mis.join(", ") + " — bestand teruggedraaid"] };
  }"""
    assert lib.count(oud2) == 1, "anker voor de telling niet gevonden"
    nieuw2 = """  const mis = Object.keys(verwacht).filter(k => na[k].length !== verwacht[k]);
  if (mis.length) {
    fs.writeFileSync(INDEX, voor.src);            // terugdraaien
    /* 30 augustus: hier stond alleen de naam van de lijst. Acht nachten op rij las Stefan
       "telling klopt niet na schrijven: sentences" en dat was alles wat de app erover kwijt wilde.
       Met de drie getallen erbij was het een avond werk geweest in plaats van acht nachten:
       271 + 2 = 273 verwacht, 274 gevonden, dus er kwam er één te veel bij en niet één te weinig.
       Dat verschil wijst meteen naar de invoeger en niet naar het taalmodel. */
    const uitleg = mis.map(k =>
      k + ": " + voor[k].length + " + " + ((nieuw[k === "cheat" ? "cheat" : k] || []).length) +
      " = " + verwacht[k] + " verwacht, " + na[k].length + " gevonden" +
      " (" + (na[k].length > verwacht[k] ? "+" : "") + (na[k].length - verwacht[k]) + ")").join("; ");
    return { ok: false, fouten: ["telling klopt niet na schrijven: " + uitleg + " — bestand teruggedraaid"] };
  }"""
    lib = lib.replace(oud2, nieuw2, 1)

# =============================================================================================
# 4. de zelftest die dit geval afdekt
# =============================================================================================
if DOE_LIB:
    oud3 = """module.exports = { altWaarschuwingen, altVoornaamwoorden, tijdsaanduidingen, isKaleZin,
                   INDEX, VERSIE, inventaris, leesArray, leesLessen, leesExtra,
                   valideer, pasToe, volgendeId, voegToeAanArray, bumpVersie,
                   altNorm, altKaal, herstelAlt, lektHetAntwoord, topPuntkomma };"""
    assert lib.count(oud3) == 1
    nieuw3 = """module.exports = { altWaarschuwingen, altVoornaamwoorden, tijdsaanduidingen, isKaleZin,
                   INDEX, VERSIE, inventaris, leesArray, leesLessen, leesExtra,
                   valideer, pasToe, volgendeId, voegToeAanArray, bumpVersie, staartVanArray,
                   altNorm, altKaal, herstelAlt, lektHetAntwoord, topPuntkomma };

/* ---------- de proef bij de komma van 30 augustus ----------

   Deze staat los van de grote zelftest hieronder, want hij hoort bij de invoeger en niet bij de
   inhoud. Hij draait op een stukje broncode in het geheugen: geen index.html, geen taalmodel, geen
   netwerk. Dat is met opzet, want de fout die hij bewaakt was er een van tekens en niet van
   betekenis, en hij lag acht nachten onder een run van dertien minuten. */
function proefInvoegen() {
  const gevallen = [
    { naam: "zonder komma",  src: 'var T = [\\n {"id":1}\\n];\\n', erbij: 2, verwacht: 3 },
    { naam: "met komma",     src: 'var T = [\\n {"id":1},\\n];\\n', erbij: 2, verwacht: 3 },
    { naam: "lege array",    src: 'var T = [\\n];\\n',              erbij: 2, verwacht: 2 },
    { naam: "twee erin",     src: 'var T = [\\n {"id":1},\\n {"id":2}\\n];\\n', erbij: 1, verwacht: 3 }
  ];
  const uit = [];
  gevallen.forEach(g => {
    const items = []; for (let i = 0; i < g.erbij; i++) items.push({ id: 90 + i });
    const na = voegToeAanArray(g.src, "T", items);
    // eslint-disable-next-line no-new-func
    const lijst = new Function("return " + vindArray(na, "T").tekst)();
    const gaten = []; for (let i = 0; i < lijst.length; i++) if (!(i in lijst)) gaten.push(i);
    uit.push({ naam: g.naam, verwacht: g.verwacht, kreeg: lijst.length,
               gaten: gaten.length, ok: lijst.length === g.verwacht && gaten.length === 0 });
  });
  return uit;
}
module.exports.proefInvoegen = proefInvoegen;"""
    lib = lib.replace(oud3, nieuw3, 1)

    assert lib.count("function staartVanArray(") == 1
    assert lib.count("function proefInvoegen(") == 1
    LIB.write_text(lib, encoding="utf-8")
    print("tools/content-lib.js: de invoeger kijkt, de telling vertelt, en er is een proef")
else:
    print("tools/content-lib.js: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
