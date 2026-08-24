#!/usr/bin/env python3
# v23.192 - de toets meet nog maar één ding, en de nachtrun heeft een rem
#
# Stefan, 24 aug: "het gaat hier meer mis omdat ik de vorm niet herken. Je toetst nu kan ik de regel
# toepassen en de vorm ineen. Dat is al feedback die ik eerder gaf." En: "pak het direct goed aan."
#
# De leerkaart staat in het project ("Leerkaart - de toets die twee dingen tegelijk meet") en is
# geschreven vóór deze code, zoals de leerpoort voorschrijft. Wat daar staat, in het kort:
#
# INGETROKKEN: het ontwerp dat ik gisteren voorstelde (de toets in tweeën knippen, eerst een
# regelvraag met rollen, dan een vormvraag) is een interpretatieoefening plus een herkennings-
# oefening. Shintani 2015 (a) en de leerkaart "de vorm in een zin" hebben daar al nee tegen gezegd.
# De leerpoort heeft mijn eigen voorstel tegengehouden, en dat is waarvoor hij er is.
#
# WAT HET PROBLEEM WEL IS
#
#   Mientras ___ (esperar) el autobús, ___ (ver) a un viejo amigo.
#     esperaba, vi   |   esperé, vi   |   esperaba, veía
#
# De drie opties verschillen elk in precies één tijd, dus als minimale paren is dit goed gebouwd en
# gaat de vraag over de regel. Maar de opties zíjn vormen: om ze te kunnen lezen moet je al weten dat
# vi de indefinido van ver is en veía de imperfecto. Ken je de regel en herken je die twee niet, dan
# is het antwoord onbereikbaar, en het cijfer zegt "fout" en verder niets.
#
# WAT ERAAN VERANDERT: bij elke optie komt de tijd te staan.
#
#     esperaba (imperfecto), vi (indefinido)
#     esperé (indefinido), vi (indefinido)
#     esperaba (imperfecto), veía (imperfecto)
#
# Eén regel verschil op het scherm, een heel andere meting. De vorm wordt geproduceerd waar dat al
# gebeurt: de vormenladder en "In een echte zin".
#
# NIET MET DE HAND. Het label wordt afgeleid, zodat het nooit iets anders kan zeggen dan de vorm.
# tijdVanVorm() kijkt in deze volgorde:
#
#   1. de vormentabel van VERBOS, exact, mét accenten. Levert dat precies één tijd op, dan die.
#   2. de drie onregelmatige imperfectos van het Spaans (era, iba, en die van ver) - een gesloten rij.
#   3. uitgangen die in het hele Spaans maar bij één tijd horen: -aba*, -aste, -asteis, -aron,
#      -iste, -isteis, -ieron, -ó. Die hebben geen infinitief nodig.
#   4. en met de infinitief erbij ook -ía* en -é. Niet zonder, want condicional en futuro plakken
#      diezelfde uitgangen achter de hele infinitief (podría, hablaré) en dan zou het label liegen.
#
# Lukt geen van vieren, dan komt er geen label. Een ontbrekend label is eerlijk, een verkeerd label
# is erger dan geen. Met opzet blijft -amos (ar) en -imos (ir) dus ongelabeld: die vormen zijn
# tegelijk presente en indefinido, en dat is geen tekortkoming maar het Spaans.
#
# EN HET LABEL VERSCHIJNT ALLEEN ALS DE VRAAG OVER DE TIJD GAAT. Voorwaarden, alle drie:
#   - elke optie heeft evenveel gaten, en elk gat is te labelen (alles of niets per vraag)
#   - de opties dragen niet allemaal hetzelfde tijdenpatroon; anders gaat de vraag niet over de
#     tijd en is het label ruis (denk aan "Indefinido: de juiste vorm", waar alles indefinido is)
#
# GEMETEN: 64 van de 281 vragen krijgen labels, waarvan 38 van de 53 in de q-relatar-familie, plus
# q-tijden, q-imperfecto, q-antesahora en q-perfectoindefinido2. Dat de regel ook buiten q-relatar
# aanslaat is het bewijs dat hij generiek is en niet op één toetsje getuned.
#
# ------------------------------------------------------------------------------------------------
# EN DE REM, EEN ANDER PROBLEEM MET DEZELFDE OORZAAK
#
# analyseer() in tools/curriculum.js stuurt zinnen en woorden door verzadigd() ("ligt hier al
# genoeg?") en toetsjes niet. Elke nacht maakt hij dus een nieuw toetsje voor het onderwerp met de
# meeste fouten, zonder ooit te vragen of daar al genoeg ligt.
#
#   spiekkaart   toetsjes   vragen
#   26                  7       53      Een verhaal vertellen: indefinido of imperfecto?
#   5                   2       18
#   elke andere         1    10-12
#
# 53 van de 281 vragen hangen aan één kaart. En dat is een lus: meer toetsjes op wat je lastig vindt
# geeft meer beurten, meer fouten, en morgen staat het weer bovenaan. De analyse van vandaag zegt
# letterlijk "nieuw toetsje bij: q-relatar", dus vanavond zou er een achtste bij komen.
#
# De rem heeft dezelfde vorm als verzadigd(): genoeg materiaal ÉN genoeg per verse fout.
#   - 20 vragen per spiekkaart. Twee toetsjes van tien is een ronde die je kunt afmaken.
#   - en minstens één vraag per verse fout.
# q-relatar: 53 vragen en 27 fouten, dus 53 >= 20 en 53/27 = 2,0 >= 1. Verzadigd, dus overslaan.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
CUR = W / "tools" / "curriculum.js"
VER = W / "versie.txt"
NIEUW = "v23.192"

src = APP.read_text(encoding="utf-8")
cur = CUR.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "tijdVanVorm" not in src
DOE_CUR = "toetsVerzadigd" not in cur
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

def crep(anker, nieuw, n=1):
    global cur
    c = cur.count(anker)
    assert c == n, "cur-anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    cur = cur.replace(anker, nieuw, n)

# =============================================================================================
# 1. welke tijd hoort bij deze vorm
# =============================================================================================
if DOE_APP:
    rep('function vraagVert(v){ return profLang() === "nl" ? v.nl : (v.ne || v.nl); }',
        '/* ================= WELKE TIJD HOORT BIJ DEZE VORM (v23.192) =================\n'
        '\n'
        '   Zie de leerkaart "de toets die twee dingen tegelijk meet". Kort: een vraag met de titel\n'
        '   "indefinido of imperfecto?" hoort de regel te meten, en dat deed hij niet, want je moest\n'
        '   eerst weten wélke vorm welke tijd is om de antwoorden te kunnen lezen. Nu staat de tijd\n'
        '   erbij, en dat label wordt afgeleid in plaats van ingetypt: één feit, één plek.\n'
        '\n'
        '   Vier wegen, in deze volgorde, en alle vier geven ze of precies één tijd of niets terug.\n'
        '   Niets is het goede antwoord als het onzeker is: een ontbrekend label is eerlijk, een\n'
        '   verkeerd label is erger dan geen. */\n'
        'var TIJD_TABEL = null;\n'
        'function tijdTabel(){\n'
        '  if(TIJD_TABEL) return TIJD_TABEL;\n'
        '  TIJD_TABEL = {};\n'
        '  try {\n'
        '    VERBOS.forEach(function(v){\n'
        '      ["presente","indefinido","imperfecto","perfecto","subjuntivo"].forEach(function(t){\n'
        '        for(var pi = 0; pi < 6; pi++){\n'
        '          var w = conjVorm(v, pi, t);\n'
        '          if(!w) continue;\n'
        '          var sl = String(w).toLowerCase();\n'
        '          (TIJD_TABEL[sl] = TIJD_TABEL[sl] || {})[t] = 1;\n'
        '        }\n'
        '      });\n'
        '    });\n'
        '  } catch(e){}\n'
        '  return TIJD_TABEL;\n'
        '}\n'
        '/* De enige drie onregelmatige imperfectos die het Spaans heeft. Een gesloten rij, dus hij\n'
        '   veroudert niet. ver staat meestal in VERBOS en wordt dan al door de tabel gevonden; hij\n'
        '   staat hier voor het geval dat niet zo is. */\n'
        'var TIJD_ONREG_IMP = {\n'
        '  "era":1,"eras":1,"\\u00e9ramos":1,"erais":1,"eran":1,\n'
        '  "iba":1,"ibas":1,"\\u00edbamos":1,"ibais":1,"iban":1,\n'
        '  "ve\\u00eda":1,"ve\\u00edas":1,"ve\\u00edamos":1,"ve\\u00edais":1,"ve\\u00edan":1\n'
        '};\n'
        '/* Deze uitgangen horen in het hele Spaans maar bij één tijd, dus die kunnen zonder dat we\n'
        '   weten welk werkwoord het is. -amos en -imos staan er met opzet NIET bij: die zijn tegelijk\n'
        '   presente en indefinido (cenamos), en dat is geen gat in de lijst maar het Spaans. */\n'
        'var TIJD_UIT_IMP = /(?:aba|abas|\\u00e1bamos|abais|aban)$/;\n'
        'var TIJD_UIT_IND = /(?:aste|asteis|aron|iste|isteis|ieron|\\u00f3)$/;\n'
        '/* Met de infinitief erbij kan ook -\u00eda en -\u00e9. Zonder infinitief niet: condicional en futuro\n'
        '   plakken diezelfde uitgangen achter de hele infinitief (podr\u00eda, hablar\u00e9), en dan zou het\n'
        '   label liegen. */\n'
        'var TIJD_INF_IMP = {ar: /(?:aba|abas|\\u00e1bamos|abais|aban)$/, er: /(?:\\u00eda|\\u00edas|\\u00edamos|\\u00edais|\\u00edan)$/};\n'
        'var TIJD_INF_IND = {ar: /(?:\\u00e9|aste|asteis|aron|\\u00f3)$/, er: /(?:\\u00ed|iste|isteis|ieron|i\\u00f3)$/};\n'
        'function tijdVanVorm(w, inf){\n'
        '  var woord = String(w || "").trim().toLowerCase();\n'
        '  if(!woord) return null;\n'
        '  var raak = tijdTabel()[woord];\n'
        '  if(raak){\n'
        '    var k = Object.keys(raak);\n'
        '    return k.length === 1 ? k[0] : null;   // twee tijden delen deze vorm: dan zeggen we niets\n'
        '  }\n'
        '  if(TIJD_ONREG_IMP[woord]) return "imperfecto";\n'
        '  if(TIJD_UIT_IMP.test(woord)) return "imperfecto";\n'
        '  if(TIJD_UIT_IND.test(woord)) return "indefinido";\n'
        '  if(!inf || !/[aei]r$/.test(inf)) return null;\n'
        '  var kl = /ar$/.test(inf) ? "ar" : "er";\n'
        '  if(TIJD_INF_IMP[kl].test(woord)) return "imperfecto";\n'
        '  if(TIJD_INF_IND[kl].test(woord)) return "indefinido";\n'
        '  return null;\n'
        '}\n'
        '\n'
        '/* De labels van één vraag, of null als deze vraag er geen hoort te krijgen.\n'
        '\n'
        '   Drie voorwaarden, en ze staan er alle drie om te voorkomen dat het label ruis wordt:\n'
        '     - elke optie heeft evenveel gaten als de andere\n'
        '     - elk gat is te labelen (alles of niets per vraag, want half gelabeld leest slordiger\n'
        '       dan niet gelabeld)\n'
        '     - de opties dragen niet allemaal hetzelfde tijdenpatroon. Bij "Indefinido: de juiste\n'
        '       vorm" is alles indefinido, en dan gaat de vraag niet over de tijd. */\n'
        'function vraagTijdLabels(v){\n'
        '  if(!v || !v.opts || v.opts.length < 2) return null;\n'
        '  var infs = (String(v.q || "").match(/\\(([a-z\\u00e1\\u00e9\\u00ed\\u00f3\\u00fa\\u00f1]+r)\\)/g) || [])\n'
        '    .map(function(s){ return s.slice(1, -1); });\n'
        '  var rijen = v.opts.map(function(o){\n'
        '    var delen = String(o).split(/\\s*[,\\u00b7]\\s*/);\n'
        '    var t = delen.map(function(d, i){ return tijdVanVorm(d, infs[i]); });\n'
        '    return t.every(function(x){ return !!x; }) ? t : null;\n'
        '  });\n'
        '  if(rijen.some(function(x){ return !x; })) return null;\n'
        '  var lengtes = {}, patronen = {};\n'
        '  rijen.forEach(function(x){ lengtes[x.length] = 1; patronen[x.join("+")] = 1; });\n'
        '  if(Object.keys(lengtes).length !== 1) return null;\n'
        '  if(Object.keys(patronen).length < 2) return null;\n'
        '  return rijen;\n'
        '}\n'
        '\n'
        'function vraagVert(v){ return profLang() === "nl" ? v.nl : (v.ne || v.nl); }')

# =============================================================================================
# 2. en ze komen op het scherm
# =============================================================================================
if DOE_APP:
    rep('  vraagOpts(v).forEach(function(o,idx){\n'
        '    html += "<button class=\'opt\' data-i=\'"+idx+"\'>"+o+"</button>";\n'
        '  });',
        '  /* v23.192: met de tijd erbij als deze vraag over de tijd gaat. Zie vraagTijdLabels(). */\n'
        '  var tijdL = null;\n'
        '  try { tijdL = vraagTijdLabels(v); } catch(e){ tijdL = null; }\n'
        '  vraagOpts(v).forEach(function(o,idx){\n'
        '    var tekst = o;\n'
        '    if(tijdL && tijdL[idx]){\n'
        '      var delen = String(o).split(/\\s*([,\\u00b7])\\s*/);   // scheidingsteken houden we vast\n'
        '      var n = 0;\n'
        '      tekst = delen.map(function(d){\n'
        '        if(d === "," || d === "\\u00b7") return d + " ";\n'
        '        var lab = tijdL[idx][n++];\n'
        '        return d + (lab ? " <span class=\'tijdlab\'>(" + lab + ")</span>" : "");\n'
        '      }).join("");\n'
        '    }\n'
        '    html += "<button class=\'opt\' data-i=\'"+idx+"\'>"+tekst+"</button>";\n'
        '  });')

    rep("  .jouw{border-color:var(--red); background:var(--red-soft); color:var(--red);}",
        "  .jouw{border-color:var(--red); background:var(--red-soft); color:var(--red);}\n"
        "  /* v23.192: de tijd naast de vorm. Kleiner en grijzer dan het antwoord zelf, want het is\n"
        "     geen deel van je keuze maar de vertaling ervan. */\n"
        "  .tijdlab{color:var(--muted); font-weight:400; font-size:.82em;}")

# =============================================================================================
# 3. de rem op de nachtrun
# =============================================================================================
if DOE_CUR:
    crep('function verzadigd(g) {\n'
         '  return g.zinnen >= VERZADIGD_ZINNEN && g.zinnen / Math.max(1, g.fouten) >= VERZADIGD_PER_FOUT;\n'
         '}',
         'function verzadigd(g) {\n'
         '  return g.zinnen >= VERZADIGD_ZINNEN && g.zinnen / Math.max(1, g.fouten) >= VERZADIGD_PER_FOUT;\n'
         '}\n'
         '\n'
         '/* v23.192. Zinnen en woorden gingen door verzadigd(), toetsjes niet. Elke nacht werd er dus\n'
         '   een nieuw toetsje gemaakt voor het onderwerp met de meeste fouten, zonder ooit te vragen\n'
         '   of daar al genoeg lag. Gemeten op 24 augustus:\n'
         '\n'
         '     spiekkaart 26   7 toetsjes   53 vragen    "indefinido of imperfecto?"\n'
         '     spiekkaart 5    2 toetsjes   18 vragen\n'
         '     elke andere     1 toetsje    10-12 vragen\n'
         '\n'
         '   53 van de 281 vragen aan één kaart, en het stopt niet vanzelf: meer toetsjes op wat je\n'
         '   lastig vindt geeft meer beurten, meer fouten, en morgen staat het weer bovenaan.\n'
         '\n'
         '   Dezelfde vorm als verzadigd(): genoeg materiaal én genoeg per verse fout. Twintig vragen\n'
         '   is twee toetsjes van tien, en dat is een ronde die je kunt afmaken. Eén vraag per fout is\n'
         '   ruimer dan de drie zinnen per fout hierboven, want een toetsvraag komt terug en een zin\n'
         '   niet: quizVraagVolgorde() zet de vragen die je fout deed vooraan. */\n'
         'const VERZADIGD_VRAGEN = 20;\n'
         'const VERZADIGD_VRAAG_PER_FOUT = 1;\n'
         '\n'
         'function toetsVerzadigd(g) {\n'
         '  return g.vragen >= VERZADIGD_VRAGEN &&\n'
         '         g.vragen / Math.max(1, g.fouten) >= VERZADIGD_VRAAG_PER_FOUT;\n'
         '}')

    crep('  const toetsGaten = groepeer(fouten.filter(f => f.type === "quiz"), f => f.tag)\n'
         '    .map(g => {\n'
         '      const qz = inv.quizzes.find(q => q.id === g.sleutel);\n'
         '      return { soort: "toets", tag: g.sleutel, fouten: g.fouten, items: g.items.length,\n'
         '               spiek: qz ? qz.spiek : null, titel: qz ? qz.titel : null, score: g.fouten / Math.max(1, g.items.length) };\n'
         '    })\n'
         '    .filter(g => g.spiek && g.spiek.length)\n'
         '    .sort((a, b) => b.fouten - a.fouten);',
         '  /* Hoeveel vragen liggen er al aan dezelfde spiekkaart? Dat is de eenheid en niet het\n'
         '     toetsje: een tweede toetsje bij dezelfde kaart is meer van hetzelfde onderwerp, en dat\n'
         '     is precies wat de rem hieronder moet zien. */\n'
         '  const vragenPerSpiek = {};\n'
         '  inv.quizzes.forEach(q => {\n'
         '    const sl = JSON.stringify(q.spiek || []);\n'
         '    vragenPerSpiek[sl] = (vragenPerSpiek[sl] || 0) + (q.vragen || []).length;\n'
         '  });\n'
         '  const toetsGaten = groepeer(fouten.filter(f => f.type === "quiz"), f => f.tag)\n'
         '    .map(g => {\n'
         '      const qz = inv.quizzes.find(q => q.id === g.sleutel);\n'
         '      return { soort: "toets", tag: g.sleutel, fouten: g.fouten, items: g.items.length,\n'
         '               spiek: qz ? qz.spiek : null, titel: qz ? qz.titel : null,\n'
         '               vragen: qz ? (vragenPerSpiek[JSON.stringify(qz.spiek || [])] || 0) : 0,\n'
         '               score: g.fouten / Math.max(1, g.items.length) };\n'
         '    })\n'
         '    .filter(g => g.spiek && g.spiek.length)\n'
         '    .sort((a, b) => b.fouten - a.fouten);\n'
         '  const toetsVol = toetsGaten.filter(toetsVerzadigd);')

    crep('  return { zinGaten: zinGaten.filter(g => !verzadigd(g)),\n'
         '           woordGaten: woordGaten.filter(g => !verzadigd(g)),\n'
         '           toetsGaten, verzadigd: vol };',
         '  return { zinGaten: zinGaten.filter(g => !verzadigd(g)),\n'
         '           woordGaten: woordGaten.filter(g => !verzadigd(g)),\n'
         '           toetsGaten: toetsGaten.filter(g => !toetsVerzadigd(g)),\n'
         '           verzadigd: vol, toetsVol };')

    # en het rapport zegt wat er is overgeslagen en waarom
    crep('  toon("grammatica-toetsjes", an.toetsGaten, g => `${g.tag} (${g.titel}): ${g.fouten} fouten · spiekkaart ${JSON.stringify(g.spiek)}`);',
         '  toon("grammatica-toetsjes", an.toetsGaten, g => `${g.tag} (${g.titel}): ${g.fouten} fouten · spiekkaart ${JSON.stringify(g.spiek)} · ${g.vragen} vragen`);\n'
         '  /* "Er is niets te doen" en "hier lag al genoeg" zijn niet hetzelfde, en dat verschil hoort\n'
         '     zichtbaar te zijn - dezelfde afspraak als bij de zinnen hierboven. */\n'
         '  if ((an.toetsVol || []).length) {\n'
         '    console.log("  toetsjes overgeslagen, hier ligt al genoeg:");\n'
         '    an.toetsVol.forEach(g => console.log(\n'
         '      `    ${g.tag} (${g.titel}): ${g.fouten} fouten · ${g.vragen} vragen aan spiekkaart ` +\n'
         '      `${JSON.stringify(g.spiek)}, dat is ${(g.vragen / Math.max(1, g.fouten)).toFixed(1)} vraag ` +\n'
         '      `per fout, dus herhalen en niet bijmaken`));\n'
         '  }')

    # en de zelftest van de zeef krijgt de rem erbij: hij draait elke nacht mee in de workflow
    crep('  proef(kaal.length === 1 && kaal[0].id === "b", "zeefKaal houdt alleen de kale zin over");',
         '  proef(kaal.length === 1 && kaal[0].id === "b", "zeefKaal houdt alleen de kale zin over");\n'
         '\n'
         '  /* v23.192: de rem op de toetsjes. Twee proeven die moeten slagen en twee die moeten\n'
         '     falen, want een rem die alles tegenhoudt is net zo stuk als een rem die niets doet. */\n'
         '  proef(toetsVerzadigd({ vragen: 53, fouten: 27 }),\n'
         '    "53 vragen op 27 fouten is verzadigd (dat is q-relatar op 24 augustus)");\n'
         '  proef(toetsVerzadigd({ vragen: 20, fouten: 20 }),\n'
         '    "precies op de grens telt als verzadigd");\n'
         '  proef(!toetsVerzadigd({ vragen: 12, fouten: 14 }),\n'
         '    "CONTROLE: 12 vragen op 14 fouten is niet verzadigd (q-imperfecto: daar hoort wel iets bij)");\n'
         '  proef(!toetsVerzadigd({ vragen: 60, fouten: 90 }),\n'
         '    "CONTROLE: en veel vragen met nog veel meer fouten ook niet");')

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: de tijd staat naast de vorm, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_CUR:
    CUR.write_text(cur, encoding="utf-8")
    print("tools/curriculum.js: de rem op de toetsjes")
else:
    print("tools/curriculum.js: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
