#!/usr/bin/env python3
# v23.223 - een reeks op de maat van de lezer
#
# Stefan, 31 aug, over de proefalinea's: "dit is een goede tekst die ik zo 90% comfortabel kan
# lezen." Daarvoor: "ik zie dit meer als soort bevestiging van kijk wat je allemaal al kunt in
# plaats van flink uitdagend", en op de vraag welk onderwerp: cultuur en dagelijks leven.
#
# WAT DE METING ERVOOR ZEI, EN WAAROM DIE NIET HET ANTWOORD GAF
#
# Eerst is de bestaande plank doorgemeten. De zinsbouw bleek niet het probleem:
#
#     chispa    7,95 woorden per zin   0,33 bijzinnen per zin   1,5% zinnen boven 25 woorden
#     franco    9,68                   0,35                     0,8%
#     quijote  10,45                   0,55                     1,3%
#
# Alle drie dus al kort. Wat er wél anders is bij Franco is hoe abstract de woorden zijn: el miedo,
# los militares, el pueblo, el desorden. Woorden die je kent maar niet ziet.
#
# En wat NIET gemeten kon worden is Stefans eigen dekking, want de app weet die zelf niet. FREQ leek
# een frequentielijst maar is het niet: 4219 regels, waarin "y", "en", "no" en "con" ontbreken en
# "una" op plek 3252 staat. Het is een uitleglijst met een toevallige volgorde. Daar kan geen
# 98%-regel op. Wat er wel aankomt: sinds v23.219 sturen leesZoek en leesVert mee wat hij opzoekt en
# omdraait, en dat is de lijst die er echt toe doet. Die is er over een week.
#
# Daarom is deze reeks niet op een berekende drempel gebouwd maar op één geijkte tekst. Hoofdstuk 1
# is voorgelegd en goedgekeurd; de andere negen hebben hetzelfde profiel:
#
#     160 tot 190 woorden, 18 tot 25 zinnen, 6,5 tot 9,3 woorden per zin, langste zin 21 woorden
#
# DE VORM, EN WAAROM ELK HOOFDSTUK ZO IS OPGEBOUWD
#
# Eerst een tafereel dat je kunt zien (een straat die om acht uur volloopt, veertien mensen aan
# tafel), dan pas de verklaring. Dat is de omkering van hoe de Franco-reeks het doet, waar het
# abstracte woord eerst komt en het voorbeeld erachteraan. En de kernwoorden van elk hoofdstuk komen
# er minstens drie keer in voor, zodat het lezen zelf de herhaling doet in plaats van de doosjes.
#
# De reeks loopt van de tafel (de cena van tien uur) naar de tafel terug (de zondagse comida bij de
# abuela). Losse hoofdstukken, drempel 0: je kunt overal beginnen.
#
# DE STEM
#
# verteller is die van de Franco-reeks. Dat is geen keuze maar een uitgangswaarde: het register
# klopt (iemand die iets uitlegt, geen verhalenverteller) en een voice-id verzinnen kan niet, die
# kiest Stefan. Eén regel veranderen en de hele reeks klinkt anders. De tien hoofdstukken zijn samen
# ongeveer 10.500 tekens, ruim onder de 40.000 per nachtrun.
import re, pathlib, json

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.223"
BRON = "claude/reeks-cultura.json"
DEEL = "España por dentro"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = '{id:"vida-1"' not in src
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

def js(x):
    return json.dumps(x, ensure_ascii=False)

geschreven = 0
if DOE_APP:
    data = json.loads((W / BRON).read_text(encoding="utf-8"))
    ids = sorted([k for k in data if not k.startswith("_")], key=lambda x: int(x.split("-")[1]))
    assert len(ids) == 10, "verwacht tien hoofdstukken, kreeg %d" % len(ids)

    stukken = []
    for n, hid in enumerate(ids, 1):
        h = data[hid]
        alineas, vert = h["tekst"], h["vert"]
        # dezelfde controle als v23.221, en om dezelfde reden: loopt dit één plek uit de pas, dan
        # staat vanaf die alinea overal de verkeerde vertaling en zegt niets het.
        assert len(alineas) == len(vert), \
            "%s: %d Spaanse alinea's, %d Nederlandse" % (hid, len(alineas), len(vert))
        for i, p in enumerate(alineas):
            assert p.strip(), "%s alinea %d is leeg" % (hid, i)
            assert vert[i].strip(), "%s vertaling %d is leeg" % (hid, i)
            assert "\n" not in p, "%s alinea %d bevat een regeleinde" % (hid, i)
        # de vragen moeten beantwoordbaar zijn: drie opties (Rodriguez 2005) en een geldig antwoord
        assert len(h["vragen"]) == 4, "%s heeft %d vragen" % (hid, len(h["vragen"]))
        for v in h["vragen"]:
            assert len(v["opts"]) == 3, "%s: een vraag heeft %d opties" % (hid, len(v["opts"]))
            assert 0 <= v["c"] < 3, "%s: antwoord %d wijst buiten de opties" % (hid, v["c"])
        # en de maat waarop deze reeks geijkt is
        woorden = len(re.findall(r"[a-záéíóúüñA-ZÁÉÍÓÚÑ]+", " ".join(alineas)))
        assert 140 <= woorden <= 210, "%s heeft %d woorden, buiten de maat" % (hid, woorden)

        tekstJs = ('+\n   "\\n\\n"+\n   ').join(js(p) for p in alineas)
        vragenJs = ",\n   ".join(
            '{q:%s, opts:[%s], c:%d}' % (js(v["q"]), ",".join(js(o) for o in v["opts"]), v["c"])
            for v in h["vragen"])
        vertJs = ",\n   ".join(js(x) for x in vert)
        stukken.append(
            ' {id:%s, num:%d, deel:%s, titel:%s, drempel:0,\n'
            '  tekst:%s,\n'
            '  vragen:[\n   %s\n  ],\n'
            '  reflectie:%s,\n'
            '  vert:[\n   %s\n  ]}'
            % (js(hid), n, js(DEEL), js(h["titel"]), tekstJs, vragenJs, js(h["reflectie"]), vertJs))
        geschreven += len(alineas)

    # ---------------------------------------------------------------------------------------
    # de hoofdstukken achteraan BOOK
    # ---------------------------------------------------------------------------------------
    m = re.search(r"^var BOOK = \[", src, re.M)
    assert m, "BOOK niet gevonden"
    eind = _blok(m.end() - 1, "[", "]")
    voor = src[:eind].rstrip().rstrip(",")
    assert voor.endswith("}"), "BOOK eindigt niet op een hoofdstuk maar op %r" % voor[-40:]
    src = voor + ",\n\n" + ",\n\n".join(stukken) + "\n" + src[eind:]

    # ---------------------------------------------------------------------------------------
    # de reeks op de plank
    # ---------------------------------------------------------------------------------------
    reeks = (
        ' /* v23.223: de eerste reeks die niet op een onderwerp is gekozen maar op een maat.\n'
        '    Hoofdstuk 1 is aan Stefan voorgelegd ("dit kan ik zo 90% comfortabel lezen") en de\n'
        '    andere negen zijn op dat profiel geschreven: 160 tot 190 woorden, hoogstens negen\n'
        '    woorden per zin, tafereel eerst en verklaring daarna.\n\n'
        '    De verteller is die van de Franco-reeks. Dat register klopt hier (iemand die iets\n'
        '    uitlegt), en een voice-id kiest Stefan; dit is een uitgangswaarde, geen besluit. */\n'
        ' {id:"cultura", pre:"vida-", nl:"España por dentro", en:"España por dentro", stem:true,\n'
        '  map:"cultura", verteller:"YKrm0N1EAM9Bw27j8kuD",\n'
        '  soortNl:"cultuur", soortEn:"culture",\n'
        '  omNl:"Waarom er om tien uur gegeten wordt, waarom niemand opstaat van tafel, en wie de familie draaiend houdt. Tien stukken over hoe Spanje van binnen werkt.",\n'
        '  omEn:"Why dinner is at ten, why nobody leaves the table, and who keeps the family running. Ten pieces on how Spain works from the inside."}')
    m = re.search(r"^var LEES_REEKSEN = \[", src, re.M)
    assert m, "LEES_REEKSEN niet gevonden"
    eind = _blok(m.end() - 1, "[", "]")
    voor = src[:eind].rstrip().rstrip(",")
    assert voor.endswith("}"), "LEES_REEKSEN eindigt niet op een reeks"
    src = voor + ",\n" + reeks + "\n" + src[eind:]

if DOE_APP:
    # ---------------------------------------------------------------------------------------
    # de controles achteraf
    # ---------------------------------------------------------------------------------------
    for i in range(1, 11):
        assert src.count('{id:"vida-%d"' % i) == 1, "vida-%d staat er niet één keer in" % i
    n = len(re.findall(r"\n  vert:\[", src))
    assert n == 43, "verwacht 43 hoofdstukken met een vertaling (33 + 10), kreeg %d" % n
    m = re.search(r"^var LEES_REEKSEN = \[", src, re.M)
    blok = src[m.end() - 1:_blok(m.end() - 1, "[", "]") + 1]
    reeksen = re.findall(r'\{id:"([a-z]+)", pre:"([^"]*)"', blok)
    assert len(reeksen) == 4, "verwacht vier reeksen, kreeg %r" % reeksen
    for rid, pre in reeksen:
        assert len(re.findall(r'\{id:"' + pre + r'\d+"', src)) > 0, "reeks %s heeft geen hoofdstukken" % rid
        assert re.search(r'\{id:"' + rid + r'".{0,400}?verteller:"', src, re.S), "reeks %s heeft geen verteller" % rid
    APP.write_text(src, encoding="utf-8")
    print("index.html: reeks cultura erbij, 10 hoofdstukken, %d alinea's met vertaling" % geschreven)
    print("            op de plank: " + ", ".join(r[0] for r in reeksen))
else:
    print("index.html: de reeks stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
