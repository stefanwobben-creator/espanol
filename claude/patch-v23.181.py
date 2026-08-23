#!/usr/bin/env python3
# v23.181 - El hilo de las palabras: tien Spaanse klassiekers als leesreeks
#
# Stefan, 23 aug: "Cádiz leer ik te weinig van (en dan bedoel ik niet Spaans) maar bij Chispa leer je
# filosofie, bij Franco leer je geschiedenis."
#
# DE REGEL DIE DAARONDER ZIT
#
# Elke leesreeks heeft een tweede vak. Spaans is de eerste en die is overal hetzelfde; de reeks
# verdient zijn plek door wat er ná het Spaans overblijft. Chispa geeft filosofie, Franco geeft
# geschiedenis, La cocina española geeft koken. Un año en Cádiz geeft niets: iemand komt aan, kijkt
# rond en went. Dat is een prima romanopzet en een slechte leesreeks.
#
# Cádiz is er precies zo gekomen als deze reeks had kunnen komen: netjes op A2, goed nagelezen, en
# niemand die vroeg wat je ervan leert. Vandaar dat het nu een regel is, en dat deze reeks zijn
# tweede vak vooraf op papier had staan (zie het projectdoc "De leesregel").
#
# DEZE REEKS
#
# Tweede vak: de Spaanse literatuur, en per boek één idee dat je meeneemt.
#
#    1 Don Quijote (1605)           zien wat er is tegenover zien wat je wilt dat er is
#    2 Lazarillo de Tormes (1554)   honger maakt slim; de eerste antiheld
#    3 La vida es sueño (1635)      en als je leven een droom was
#    4 Las Meninas (1656)           wie kijkt naar wie, en wie staat buiten beeld
#    5 Bécquer (1871)               wat een gedicht kan dat een zin niet kan
#    6 Platero y yo (1914)          groot kijken naar iets kleins
#    7 Machado (1912/1939)          caminante, no hay camino
#    8 Lorca (1928/1936)            de duende, en wat er met de dichter gebeurde
#    9 Cien años de soledad (1967)  het Spaans van de andere kant van de oceaan
#   10 terug bij hoofdstuk 1        waarom deze boeken nog gelezen worden
#
# DRIE BESLUITEN
#
# 1. GEEN NIEUWE STEM, DUS map:"boek". Het manifest houdt de stem per map bij. Een eigen map zou
#    betekenen dat er eerst een stem gekozen moet worden voordat er iets klinkt, en tot die tijd
#    staat de reeks er stil bij. Met de verteller van Chispa klinkt hij de eerstvolgende nacht. Dat
#    is dezelfde afweging als bij Cádiz, en daar staat hij ook zo opgeschreven.
#
# 2. DREMPEL 0. De reeks staat vanaf nu open. Franco staat ook op 0 en Chispa begint op 0; alleen
#    Cádiz wacht op acht afgeronde lessen. Hier is er geen reden om te wachten: het is geen vervolg.
#
# 3. VÓÓR CÁDIZ IN DE LIJST. lesFlowBoekHoofdstuk() pakt het eerste hoofdstuk dat nog niet af is, in
#    de volgorde van BOOK. Stefan zit midden in Cádiz, dus achteraan zetten zou betekenen dat hij
#    deze reeks pas over weken ziet. Cádiz blijft gewoon staan met zijn voortgang; hij staat alleen
#    niet meer vooraan.
#
# De tien hoofdstukken staan in claude/hoofdstukken-letras.py, want een patchscript met achtduizend
# tekens verhaal erin is niet meer na te lezen.
import re, pathlib, sys, json

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.181"

import runpy
_ns = runpy.run_path(str(W / "claude" / "hoofdstukken-letras.py"))
H = _ns["H"]
assert len(H) == 10, "verwacht tien hoofdstukken, kreeg %d" % len(H)

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "lit-1" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

def js(s):
    """Een JS-stringliteral met dubbele aanhalingstekens, met \\n voor de regelovergangen."""
    return json.dumps(s, ensure_ascii=False)

DEEL = "El hilo de las palabras"

def hoofdstuk(h):
    regels = []
    regels.append(' {id:"lit-%d", num:%d, deel:"%s", titel:%s, drempel:0,'
                  % (h["num"], h["num"], DEEL, js(h["titel"])))
    regels.append('  tekst:%s,' % js(h["tekst"]))
    vr = []
    for v in h["vragen"]:
        vr.append('   {q:%s,\n    opts:[%s], c:%d}'
                  % (js(v["q"]), ", ".join(js(o) for o in v["opts"]), v["c"]))
    regels.append('  vragen:[\n%s\n  ],' % ",\n".join(vr))
    regels.append('  reflectie:%s},' % js(h["reflectie"]))
    return "\n".join(regels)

if DOE_APP:
    blok = ("\n /* ================= EL HILO DE LAS PALABRAS (v23.181) =================\n"
            "    Tien Spaanse klassiekers, elk één werk, één idee, één beeld. Het tweede vak van deze\n"
            "    reeks is de literatuur; zonder tweede vak hoort een reeks er niet te zijn (zie de kop\n"
            "    van claude/patch-v23.181.py en het projectdoc \"De leesregel\").\n\n"
            "    Vóór Cádiz, want lesFlowBoekHoofdstuk() pakt het eerste onafgeronde hoofdstuk in deze\n"
            "    volgorde en Stefan zit midden in Cádiz. */\n"
            + "\n".join(hoofdstuk(h) for h in H) + "\n")

    rep(' {id:"cadiz-1", num:1, deel:"Un año en Cádiz", titel:"La llave que no giraba", drempel:8,',
        blok + ' {id:"cadiz-1", num:1, deel:"Un año en Cádiz", titel:"La llave que no giraba", drempel:8,')

    # de plank
    rep(' {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco", stem:true, map:"hist",',
        ' /* v23.181: dezelfde verteller en dus dezelfde map als Chispa, om dezelfde reden als bij\n'
        '    Cádiz: het manifest houdt de stem per map bij, dus een eigen map zou betekenen dat er\n'
        '    eerst een stem gekozen moet worden voordat er iets klinkt. */\n'
        ' {id:"letras", pre:"lit-", nl:"El hilo de las palabras", en:"El hilo de las palabras", stem:true, map:"boek",\n'
        '  soortNl:"literatuur", soortEn:"literature",\n'
        '  omNl:"Tien Spaanse klassiekers, van Don Quijote tot Macondo. Elk hoofdstuk \\u00e9\\u00e9n boek, \\u00e9\\u00e9n idee en \\u00e9\\u00e9n beeld dat blijft hangen.",\n'
        '  omEn:"Ten Spanish classics, from Don Quijote to Macondo. Each chapter one book, one idea and one image that stays."},\n'
        ' {id:"franco", pre:"hist-", nl:"España: los años de Franco", en:"España: los años de Franco", stem:true, map:"hist",')

# ---------------------------------------------------------------- schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: tien hoofdstukken en de reeks toegevoegd, versie " + NIEUW)
else:
    print("index.html: de reeks stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
