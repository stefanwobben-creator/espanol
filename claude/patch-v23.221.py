#!/usr/bin/env python3
# v23.221 - Chispa en Don Quijote krijgen hun Nederlandse regel
#
# Stefan, 31 aug: "en voor Don Quijote en Chispa de NL vertaling toevoegen."
#
# Vervolg op v23.219, waar de trede tussen één woord en de hele tekst gebouwd is en de reeks over
# Franco als eerste vertaald werd. Nu de andere twee die overblijven na v23.220:
#
#     chispa    boek-1 t/m boek-13    191 alinea's
#     quijote   quij-1 t/m quij-10     66 alinea's
#
# Daarmee heeft elk hoofdstuk op de plank een Nederlandse regel per alinea: 311 in totaal over drie
# reeksen. Het knopje "Nederlands" verschijnt alleen waar er een vertaling is, dus vanaf nu overal.
#
# DE ENIGE CONTROLE DIE ER ECHT TOE DOET
#
# Eén Nederlandse regel per Spaanse alinea, in dezelfde volgorde. Loopt dat ergens één plek uit de
# pas, dan staat vanaf die alinea overal de verkeerde vertaling en zegt niets het: je leest een
# regel die klopt als Nederlands, klopt als vertaling van íets, en niet hoort bij wat je ziet.
#
# Dat is precies wat er bij de liedjes misging (zeven uitleggen bij woorden die niet in het nummer
# stonden), en het is daar niet opgemerkt omdat er niets was dat de twee kanten aan elkaar hield.
# Deze patch telt de alinea's uit de BRON en weigert te schrijven als het niet klopt; pw-leesvert.js
# telt ze daarna nog eens in de browser.
#
# OVER DE DIALOOGSTREEPJES
#
# Het Spaans zet dialoog tussen lange streepjes (—Hola —dice el cangrejo—). Het Nederlands doet dat
# met aanhalingstekens, en dat is hier ook praktischer: de vertaling staat als losse regel onder de
# alinea, niet als doorlopende tekst ernaast, en dan is een streepje aan het begin van een regel
# eerder verwarrend dan behulpzaam.
import re, pathlib, json

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.221"
BRONNEN = ["claude/vert-chispa.json", "claude/vert-quijote.json"]

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = '{id:"boek-1"' in src and "vert:[" not in src.split('{id:"boek-1"')[1][:6000]
DOE_VER = _num(huidig_ver) < _num(NIEUW)

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

geschreven = 0
if DOE_APP:
    for bron in BRONNEN:
        vert = json.loads((W / bron).read_text(encoding="utf-8"))
        ids = [k for k in vert if not k.startswith("_")]
        for hid in sorted(ids, key=lambda x: int(x.split("-")[1])):
            a = src.index('{id:"%s"' % hid)
            eind = _blok(a, "{", "}")
            blok = src[a:eind + 1]
            assert "vert:[" not in blok, hid + " heeft al een vertaling"
            # het aantal Spaanse alinea's uit de bron zelf halen, niet aannemen
            mt = re.search(r'tekst:\s*((?:"(?:[^"\\]|\\.)*"\s*\+?\s*)+)', blok)
            assert mt, "geen tekst in " + hid
            stukken = re.findall(r'"((?:[^"\\]|\\.)*)"', mt.group(1))
            tekst = "".join(stukken).replace("\\n", "\n").replace('\\"', '"')
            paras = [p for p in tekst.split("\n\n") if p.strip()]
            nl = vert[hid]
            assert len(paras) == len(nl), \
                "%s: %d Spaanse alinea's, %d Nederlandse" % (hid, len(paras), len(nl))
            for i, r in enumerate(nl):
                assert str(r).strip(), "%s alinea %d is leeg" % (hid, i)
            regels = ",\n   ".join(json.dumps(x, ensure_ascii=False) for x in nl)
            nieuw = blok[:-1].rstrip() + ",\n  vert:[\n   " + regels + "\n  ]}"
            src = src[:a] + nieuw + src[eind + 1:]
            geschreven += len(nl)

if DOE_APP:
    n = len(re.findall(r"\n  vert:\[", src))
    assert n == 33, "verwacht 33 hoofdstukken met een vertaling (10 franco + 13 chispa + 10 quijote), kreeg %d" % n
    APP.write_text(src, encoding="utf-8")
    print("index.html: %d alinea's vertaald erbij, %d hoofdstukken hebben er nu een" % (geschreven, n))
else:
    print("index.html: stonden er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
