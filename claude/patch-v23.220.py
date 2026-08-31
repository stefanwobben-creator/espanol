#!/usr/bin/env python3
# v23.220 - twee reeksen van de plank, en de keukenwoorden blijven
#
# Stefan, 31 aug: "deze boeken verwijderen: La cocina española, El hilo de las palabras."
#
# WAT ERUIT GAAT
#
#   cocina   La cocina española          receta-1 t/m receta-6   (6 hoofdstukken)
#   letras   El hilo de las palabras     lit-1 t/m lit-10       (10 hoofdstukken)
#
# WAT BLIJFT, EN WAAROM DAT GEEN HALVE VERWIJDERING IS
#
# Aan de recepten hangen 36 woorden: la batidora, el pepino, el vinagre, la nevera, maduro,
# triturar, en zo verder. Dat is gewone keukenwoordenschat en die staat los van of je die zes
# recepten wilt lezen. Ze staan in K_WORDS met tag "receta-N", en die tag wijst na deze ronde naar
# een hoofdstuk dat niet meer bestaat.
#
# Dat is niet gevaarlijk (dicZichtbareWoorden() schermt alleen "boek-"-tags af, dus ze blijven
# zichtbaar) maar het is wel een verwijzing naar niets, en dat is precies het soort spoor waar de
# volgende lezer over struikelt. Ze krijgen daarom de tag "cocina": dezelfde woorden, geen dood
# hoofdstuk meer aan de andere kant.
#
# El hilo de las palabras heeft nul getagde woorden, dus daar valt niets te redden.
#
# DE ACHT WEZEN DIE ER AL LAGEN
#
# audio/boek/ bevat 21 bestanden: dertien van Chispa en acht van cadiz-1 t/m cadiz-8. Die reeks is
# in v23.182 van de plank gehaald en de opnames zijn blijven staan. tools/avondrun-audio.js meldt
# zulke wezen ("hoofdstukken die bij geen enkele reeks horen") maar ruimt ze niet op, en terecht:
# een script dat bestanden weggooit omdat het ze niet herkent is gevaarlijker dan een paar losse
# mp3's. Met de hand dan, nu er toch opgeruimd wordt.
#
# El hilo had trouwens nooit opnames: geen enkele lit-*.mp3 in audio/boek/, ondanks stem:true. Dat
# is de avondrun die sinds 23 augustus niets kon publiceren (zie v23.217).
#
# WAT DIT NIET RAAKT
#
# De stem van Don Quijote. Stefan vroeg die in te spreken, en dat hoeft niet: de planner heeft de
# tien hoofdstukken al in de wachtrij staan (9.450 tekens, ruim onder de grens van 40.000 per run).
# audio/quijote/ is leeg omdat de avondrun sinds 23 augustus niets kon afleveren, en dat is met
# v23.217 gerepareerd.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.220"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = '{id:"receta-1"' in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

weg = {"hoofdstukken": 0, "reeksen": 0, "hertagd": 0}

def _blok(start, o, s):
    d = 0; i = start; inStr = None; esc = False
    while i < len(src):
        c = src[i]
        if inStr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == inStr: inStr = None
            i += 1; continue
        if c in "\"'":
            inStr = c; i += 1; continue
        if c == o: d += 1
        elif c == s:
            d -= 1
            if d == 0: return i
        i += 1
    raise AssertionError("ongebalanceerd blok vanaf %d" % start)

def knipObject(sleutel):
    """Het object dat met deze sleutel begint, plus de komma erachter."""
    global src
    a = src.find(sleutel)
    assert a >= 0, "niet gevonden: " + sleutel
    # terug naar het begin van de regel, zodat de inspringing meegaat
    regelStart = src.rfind("\n", 0, a) + 1
    eind = _blok(a, "{", "}")
    while src[eind:eind + 1] in ("}", ","): eind += 1
    if src[eind:eind + 1] == "\n": eind += 1
    src = src[:regelStart] + src[eind:]

if DOE_APP:
    # =========================================================================================
    # 1. de zestien hoofdstukken
    # =========================================================================================
    for pre, n in [("receta-", 6), ("lit-", 10)]:
        for i in range(1, n + 1):
            knipObject('{id:"%s%d"' % (pre, i))
            weg["hoofdstukken"] += 1

    # =========================================================================================
    # 2. de twee reeksen van de plank
    # =========================================================================================
    for rid in ["cocina", "letras"]:
        m = re.search(r'\n *\{id:"' + rid + r'", pre:', src)
        assert m, "reeks niet gevonden: " + rid
        a = m.start() + 1
        eind = _blok(m.start() + 1, "{", "}")
        while src[eind:eind + 1] in ("}", ","): eind += 1
        if src[eind:eind + 1] == "\n": eind += 1
        src = src[:a] + src[eind:]
        weg["reeksen"] += 1

    # =========================================================================================
    # 3. de keukenwoorden houden hun betekenis, niet hun dode hoofdstuk
    # =========================================================================================
    n_voor = len(re.findall(r'tag:"receta-\d+"', src))
    src = re.sub(r'tag:"receta-\d+"', 'tag:"cocina"', src)
    weg["hertagd"] = n_voor

if DOE_APP:
    for pre in ["receta-", "lit-"]:
        rest = re.findall(r'\{id:"' + pre + r'\d+"', src)
        assert not rest, "er staan nog hoofdstukken: %r" % rest
    for rid in ["cocina", "letras"]:
        assert '{id:"%s", pre:' % rid not in src, "de reeks %s staat er nog" % rid
    assert not re.findall(r'tag:"receta-\d+"', src), "er wijst nog een woord naar een recept"
    assert len(re.findall(r'tag:"cocina"', src)) == weg["hertagd"]
    # de plank moet drie reeksen overhouden en die moeten alle drie hoofdstukken hebben
    m = re.search(r'^var LEES_REEKSEN = \[', src, re.M)
    j = m.end() - 1
    blok = src[j:_blok(j, "[", "]") + 1]
    over = re.findall(r'\{id:"([a-z]+)", pre:"([^"]*)"', blok)
    assert len(over) == 3, "verwacht drie reeksen, kreeg %r" % over
    for rid, pre in over:
        n = len(re.findall(r'\{id:"' + pre + r'\d+"', src))
        assert n > 0, "reeks %s heeft geen hoofdstukken meer" % rid
    APP.write_text(src, encoding="utf-8")
    print("index.html: %d hoofdstukken en %d reeksen weg, %d woorden hertagd naar cocina"
          % (weg["hoofdstukken"], weg["reeksen"], weg["hertagd"]))
    print("            over op de plank: " + ", ".join(r[0] for r in over))
else:
    print("index.html: de twee reeksen stonden er al niet meer")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
