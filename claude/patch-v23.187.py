#!/usr/bin/env python3
# v23.187 - Don Quijote krijgt zijn eigen stem
#
# (Geschreven als v23.184, hernummerd na de nachtrun van 24 aug. Inhoud ongewijzigd.)
#
# Stefan, 23 aug, na de vraag welke voice-id: wfTWLJ20rcMqvU8gIiAB.
#
# AANNAME, HARDOP: dit id is voor Don Quijote. Dat is de reeks waarvan ik zei dat er een id voor
# nodig was. El hilo de las palabras houdt de verteller van Chispa tot Stefan iets anders zegt.
#
# DIT KOST NIETS, EN DAT IS GEEN TOEVAL MAAR TIMING
#
# Nageteld voordat er iets veranderde:
#
#   mp3's in audio/boek/ die met quij- beginnen   0
#   regels in audio/stemmen.json voor quij-       0
#
# De tien hoofdstukken van v23.182 zijn nog nooit ingesproken; ze stonden voor vannacht op de
# planning. Ze verhuizen dus niet, ze worden gewoon meteen op de goede plek en met de goede stem
# ingesproken. Was dit een week later gekomen, dan had dezelfde wijziging tien opnames weggegooid en
# opnieuw betaald (9.500 tekens). Nu is het nul.
#
# WAT ER VERANDERT
#
#   map:"boek"      -> map:"quijote"      de app zoekt audio/quijote/quij-1.mp3 (index.html 14155)
#   verteller: ...  -> wfTWLJ20rcMqvU8gIiAB
#
# Meer niet. De leiding lag er al in v23.183: ALLE_GROEPEN telt de mappen van de reeksen mee,
# leesConfig() vult de stem uit de reeks, verwerk() maakt audio/quijote/ zelf aan, en de workflow
# doet `git add audio`. Dit is de eerste reeks die die weg loopt, en dat is precies waarvoor hij is
# aangelegd.
#
# GEEN EIGEN STEMINSTELLING
#
# quijote valt terug op die van `boek` (stability 0.4, similarity 0.75). Dat is de instelling voor
# een verteller en Don Quijote is een roman met een ironische verteller. Een eigen regel zou een
# getal zijn dat niemand heeft gekozen.
#
# WAT ER MIS KAN GAAN, EN WAT DAT KOST
#
# Ik kan dit id niet controleren: daar is de API-sleutel voor nodig en die hoor ik niet te hebben.
# Doet het id het niet, dan slaat de nachtrun alléén de groep quijote over (avondrun-audio.js regel
# 265) en de rest wordt gewoon ingesproken. Kosten van een verkeerd id: één stille nacht voor één
# reeks, en een melding in de samenvatting met de reden erbij.
#
# EN DE FOUT DIE HIERMEE MOGELIJK WORDT
#
# Vanaf nu kunnen map en stem uit elkaar lopen, en dat maakt een nieuwe stille fout mogelijk: twee
# reeksen in dezelfde map die een verschillende verteller noemen. reeksStemmen() houdt de eerste aan
# en de tweede liegt dan over wie hem voorleest, zonder dat iets dat zegt. Daar komt een controle
# voor, met een controlegeval dat aantoont dat hij het ook echt ziet.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
LIB = W / "tools" / "audio-lib.js"
VER = W / "versie.txt"
NIEUW = "v23.187"

STEM = "wfTWLJ20rcMqvU8gIiAB"

src = APP.read_text(encoding="utf-8")
lib = LIB.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = STEM not in src
DOE_LIB = "reeksStemBotsingen" not in lib
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

def lrep(anker, nieuw, n=1):
    global lib
    c = lib.count(anker)
    assert c == n, "lib-anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    lib = lib.replace(anker, nieuw, n)

# ---------------------------------------------------------------- 1. de eigen map en de eigen stem
if DOE_APP:
    rep(
        ' /* v23.182: Don Quijote, het eerste van de tien uitgewerkt tot een eigen boek. Dezelfde map en\n'
        '    dus dezelfde verteller als Chispa en El hilo: het manifest houdt de stem per map bij, en een\n'
        '    eigen map zou betekenen dat er eerst een stem gekozen moet worden voordat er iets klinkt. */\n'
        ' {id:"quijote", pre:"quij-", nl:"Don Quijote", en:"Don Quijote", stem:true, map:"boek", verteller:"imFXYz8XIletRKLZZQaA",',
        ' /* v23.182: Don Quijote, het eerste van de tien uitgewerkt tot een eigen boek. Stond hier met\n'
        '    map:"boek" en dus met de verteller van Chispa, omdat een eigen map betekende dat er niets\n'
        '    zou klinken. Dat was de omweg die v23.183 heeft weggehaald.\n\n'
        '    v23.184: eigen map, eigen stem. Stefan koos de voice-id. Dit kostte niets, en dat is geen\n'
        '    toeval maar timing: er stond nog geen enkele quij-opname, dus de tien hoofdstukken worden\n'
        '    meteen op de goede plek en met de goede stem ingesproken in plaats van verhuisd.\n\n'
        '    Geen eigen steminstelling: die valt terug op die van `boek`, en dat is de instelling voor\n'
        '    een verteller. Een eigen regel zou een getal zijn dat niemand heeft gekozen. */\n'
        ' {id:"quijote", pre:"quij-", nl:"Don Quijote", en:"Don Quijote", stem:true, map:"quijote", verteller:"' + STEM + '",')

# ---------------------------------------------------------------- 2. de fout die nu mogelijk is
if DOE_LIB:
    lrep(
        'function reeksStemmen(){\n'
        '  const uit = {};\n'
        '  try {\n'
        '    leesReeksen().forEach(function(r){\n'
        '      if(!r || !r.map || !r.verteller || r.stem === false) return;\n'
        '      if(!uit[r.map]) uit[r.map] = r.verteller;\n'
        '    });\n'
        '  } catch(e){}\n'
        '  return uit;\n'
        '}',
        'function reeksStemmen(){\n'
        '  const uit = {};\n'
        '  try {\n'
        '    leesReeksen().forEach(function(r){\n'
        '      if(!r || !r.map || !r.verteller || r.stem === false) return;\n'
        '      if(!uit[r.map]) uit[r.map] = r.verteller;\n'
        '    });\n'
        '  } catch(e){}\n'
        '  return uit;\n'
        '}\n'
        '\n'
        '/* v23.184: sinds Don Quijote een eigen map heeft kunnen map en stem uit elkaar lopen, en dat\n'
        '   maakt een nieuwe stille fout mogelijk: twee reeksen in dezelfde map die een verschillende\n'
        '   verteller noemen. reeksStemmen() houdt de eerste aan, en de tweede staat er dan met een\n'
        '   voice-id die niets doet. Niemand die het merkt, want er klinkt gewoon geluid.\n'
        '\n'
        '   Eén map is één stem: het manifest legt de stem per map vast, dus twee stemmen in één map\n'
        '   kan technisch niet eens. Wie twee stemmen wil, wil twee mappen. */\n'
        'function reeksStemBotsingen(){\n'
        '  const eerste = {}, botsingen = [];\n'
        '  leesReeksen().forEach(function(r){\n'
        '    if(!r || !r.map || !r.verteller || r.stem === false) return;\n'
        '    if(!eerste[r.map]){ eerste[r.map] = r; return; }\n'
        '    if(eerste[r.map].verteller !== r.verteller){\n'
        '      botsingen.push({ map: r.map, eerste: eerste[r.map].id, tweede: r.id,\n'
        '                       stem: eerste[r.map].verteller, andere: r.verteller });\n'
        '    }\n'
        '  });\n'
        '  return botsingen;\n'
        '}')

    lrep(' hashVan, steminstellingVoor, ALLE_GROEPEN, MANIFEST_PAD };',
         ' hashVan, steminstellingVoor, reeksStemBotsingen, ALLE_GROEPEN, MANIFEST_PAD };')

    # ---- en de proef, in de zelftest van v23.183 ----
    lrep(
        '  proef(zonder.length === 0,\n'
        '    "elke reeks met geluid noemt een verteller" +\n'
        '    (zonder.length ? " (mist bij: " + zonder.join(", ") + ")" : ""));',
        '  proef(zonder.length === 0,\n'
        '    "elke reeks met geluid noemt een verteller" +\n'
        '    (zonder.length ? " (mist bij: " + zonder.join(", ") + ")" : ""));\n'
        '\n'
        '  // v23.184: en twee reeksen in dezelfde map noemen dezelfde verteller\n'
        '  const bots = reeksStemBotsingen();\n'
        '  proef(bots.length === 0,\n'
        '    "één map is één stem" + (bots.length ? " (" + bots.map(function(b){\n'
        '      return b.map + ": " + b.eerste + " zegt " + b.stem + ", " + b.tweede + " zegt " + b.andere;\n'
        '    }).join(" · ") + ")" : ""));')

    # het controlegeval: de verzonnen reeks van de zelftest claimt map "boek" met een andere stem,
    # dus de kopie MOET die botsing wel zien. Zag hij hem niet, dan meet de proef hierboven niets.
    lrep(
        '  // 4. HET TWEEDE CONTROLEGEVAL: stem:false doet niet mee',
        '  /* CONTROLE bij "één map is één stem": de verzonnen reeks zt-botst claimt map "boek" met\n'
        '     ZT_ANDERS, dus in de kopie moet die botsing wél gevonden worden. Vindt hij hem daar niet,\n'
        '     dan bewijst de groene proef op de echte app niets. */\n'
        '  const botsKopie = kopie.reeksStemBotsingen();\n'
        '  proef(botsKopie.some(function(b){ return b.map === "boek" && b.andere !== b.stem; }),\n'
        '    "CONTROLE: en een echte botsing wordt wél gezien (" + botsKopie.length + " gevonden)");\n'
        '\n'
        '  // 4. HET TWEEDE CONTROLEGEVAL: stem:false doet niet mee')

# ---------------------------------------------------------------- schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: Don Quijote krijgt map quijote en zijn eigen stem, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_LIB:
    LIB.write_text(lib, encoding="utf-8")
    print("tools/audio-lib.js: één map is één stem, met controle")
else:
    print("tools/audio-lib.js: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
