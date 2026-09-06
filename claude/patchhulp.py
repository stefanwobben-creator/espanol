#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# patchhulp.py (6 sep, v23.247) - welk versienummer krijgt deze ronde?
#
# WAAROM DIT ER IS
#
# Op 6 september botsten twee versienummers. Ik schreef een ronde met NIEUW = "v23.245" terwijl mijn
# basis op v23.244 stond. Terwijl die ronde openstond ging de avondrun voor het eerst zelfstandig
# live en publiceerde ZIJN v23.245. Toen ik mijn script draaide, deed het dit:
#
#     DOE_VER = _num(huidig_ver) < _num(NIEUW)     # v23.245 < v23.245 -> False
#     ...
#     print("versie.txt: stond al op " + huidig_ver)
#
# Dat is de hele fout. Die tak bestaat voor herhaalbaarheid: draai je hetzelfde script twee keer,
# dan hoort de tweede keer niets te doen. Maar hij kan "ik heb dit al gedaan" niet onderscheiden van
# "iemand anders heeft mijn nummer ingenomen", en in dat tweede geval zegt hij vrolijk dat het al
# goed staat. Gevolg: twee verschillende bomen die allebei v23.245 heten, en geen enkel signaal.
#
#     Een versienummer dat twee bomen aanwijst, wijst niets aan.
#     Een controle die de goede en de foute uitkomst dezelfde tak geeft, controleert niets.
#
# DE TWEE DINGEN DIE HIER UIT ELKAAR GETROKKEN WORDEN
#
# Er zaten twee vragen in die ene regel geknoopt:
#
#   1. IS DEZE RONDE AL TOEGEPAST?  Dat hangt aan de inhoud, niet aan het nummer. Elk patchscript
#      heeft daar al een merkteken voor (DOE_APP). Dat is het enige eerlijke antwoord op "moet ik
#      nog iets doen".
#   2. WELK NUMMER KRIJGT HIJ DAN?  Dat hangt aan wat er LIGT op het moment van toepassen, niet aan
#      wat ik dacht toen ik het schreef.
#
# nummerKiezen() beantwoordt alleen de tweede vraag, en krijgt het antwoord op de eerste mee.
#
# WAAROM NIET GEWOON ALTIJD huidig + 1
#
# Omdat tools/patches.sh de scripts in claude/ op volgorde naspeelt om een tak opnieuw op te bouwen.
# Daar moet een ronde het nummer krijgen waaronder hij bekend staat, ook als er tussendoor rondes
# van de avondrun ontbreken. Vandaar: het geplande nummer is een BODEM, geen belofte.
#
#     gepland v23.247, er ligt v23.246  ->  v23.247   (het gewone geval, en het naspelen)
#     gepland v23.247, er ligt v23.247  ->  v23.248   (iemand was me voor)
#     gepland v23.247, er ligt v23.250  ->  v23.251   (iemand was me ver voor)
#
# In de twee onderste gevallen klopt de titel van de ronde niet meer met het nummer dat hij krijgt.
# Dat is geen ramp maar het moet wel HARDOP: nummerKiezen geeft daarom een reden terug, en de
# patchscripts drukken die af. tools/versiehoger.js vangt hetzelfde geval nog een keer af, vlak
# voor het afleveren, voor het geval ik langs die regel heen kijk.
#
#   python3 claude/patchhulp.py --zelftest
import re
import sys


def num(v):
    """v23.246 -> (23, 246). Een versie zonder cijfers is geen versie."""
    d = [int(x) for x in re.findall(r"\d+", str(v))]
    if not d:
        raise ValueError("dit leest niet als een versie: %r" % (v,))
    return tuple(d)


def volgende(v):
    """v23.246 -> v23.247. Alleen het laatste deel loopt op."""
    m = re.match(r"^(v?\d+(?:\.\d+)*\.)(\d+)$", str(v).strip())
    if not m:
        raise ValueError("dit leest niet als een versie: %r" % (v,))
    return m.group(1) + str(int(m.group(2)) + 1)


def nummerKiezen(huidig, gepland, doe_app):
    """Geeft (nieuw, doe_ver, reden).

    huidig   : wat er nu in versie.txt staat
    gepland  : het nummer waarop deze ronde geschreven is
    doe_app  : heeft deze ronde zijn inhoudelijke wijziging nog te doen?

    doe_ver hangt aan doe_app en aan niets anders. Ligt de wijziging er al, dan is het nummer al
    verzet toen dat gebeurde; nog een keer bumpen zou bij elke herhaling een nummer verbruiken.
    """
    if not doe_app:
        # reden blijft leeg: de patchscripts drukken die af als LET OP, en "ik heb dit al gedaan"
        # is geen waarschuwing. Alleen de botsing hoort hardop te zijn, anders went het.
        return (huidig, False, "")
    if num(huidig) < num(gepland):
        return (gepland, True, "")
    nieuw = volgende(huidig)
    return (nieuw, True,
            "het geplande nummer %s was al vergeven (er ligt %s), dus deze ronde wordt %s"
            % (gepland, huidig, nieuw))


def zetVersie(app_pad, ver_pad, huidig, nieuw):
    """Zet het nummer op de twee plekken waar het staat. Faalt luid als APP_VERSIE niet meebeweegt,
    want versie.txt en APP_VERSIE uit elkaar laten lopen is precies wat tools/versiegelijk.js
    bewaakt."""
    a = app_pad.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig + '"', 'var APP_VERSIE = "' + nieuw + '"')
    if a == b:
        raise AssertionError("APP_VERSIE stond niet op " + huidig + ", dus er is niets verzet")
    app_pad.write_text(b, encoding="utf-8")
    ver_pad.write_text(nieuw + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------
def _zelftest():
    fout = [0]

    def ok(c, m):
        if c:
            print("  ok   " + m)
        else:
            fout[0] += 1
            print("  FOUT " + m)

    print("-- volgende() --")
    ok(volgende("v23.246") == "v23.247", 'v23.246 -> v23.247 (' + volgende("v23.246") + ")")
    ok(volgende("v23.9") == "v23.10", 'v23.9 -> v23.10, niet v23.91 (' + volgende("v23.9") + ")")
    ok(volgende("v23.99") == "v23.100", "v23.99 -> v23.100 (" + volgende("v23.99") + ")")
    for kaal in ["", "vlekkeloos", "v23", "23.4.x"]:
        try:
            volgende(kaal)
            ok(False, "CONTROLE: %r hoort geweigerd te worden, maar kwam er doorheen" % (kaal,))
        except ValueError:
            ok(True, "CONTROLE: %r wordt geweigerd" % (kaal,))

    print("\n-- num() sorteert als getal, niet als tekst --")
    ok(num("v23.9") < num("v23.10"), "v23.9 komt voor v23.10 (als tekst zou dat andersom zijn)")
    ok(num("v23.246") < num("v23.247"), "v23.246 komt voor v23.247")

    print("\n-- nummerKiezen(): het gewone geval --")
    n, dv, reden = nummerKiezen("v23.246", "v23.247", True)
    ok(n == "v23.247" and dv and not reden, "er ligt v23.246, gepland v23.247 -> v23.247, stil")

    print("\n-- nummerKiezen(): DE BOTSING VAN 6 SEPTEMBER --")
    n, dv, reden = nummerKiezen("v23.247", "v23.247", True)
    ok(n == "v23.248" and dv, "er ligt al v23.247 -> deze ronde wordt v23.248 (" + n + ")")
    ok(bool(reden), "en dat gebeurt HARDOP: " + (reden or "(geen reden!)"))
    n, dv, reden = nummerKiezen("v23.250", "v23.247", True)
    ok(n == "v23.251" and dv, "er ligt v23.250 -> v23.251, dus nooit terug in de tijd (" + n + ")")
    ok(bool(reden), "en ook dat is hardop")

    print("\n-- nummerKiezen(): tweede keer draaien doet niets --")
    n, dv, reden = nummerKiezen("v23.247", "v23.247", False)
    ok(n == "v23.247" and not dv, "wijziging ligt er al -> geen tweede bump (" + n + ")")
    ok(reden == "", "en dat is stil: alleen de botsing hoort hardop te zijn")
    n, dv, reden = nummerKiezen("v23.246", "v23.247", False)
    ok(not dv, "CONTROLE: ook als het nummer nog laag staat, want het merkteken beslist, niet het nummer")

    print("\n-- zetVersie() zet ze allebei, of hij faalt --")
    import pathlib
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        app = pathlib.Path(d) / "index.html"
        ver = pathlib.Path(d) / "versie.txt"
        app.write_text('x\nvar APP_VERSIE = "v1.1";\ny\n', encoding="utf-8")
        ver.write_text("v1.1\n", encoding="utf-8")
        zetVersie(app, ver, "v1.1", "v1.2")
        ok('var APP_VERSIE = "v1.2"' in app.read_text(encoding="utf-8"), "APP_VERSIE gaat mee")
        ok(ver.read_text(encoding="utf-8").strip() == "v1.2", "en versie.txt ook")
        try:
            zetVersie(app, ver, "v1.1", "v1.3")
            ok(False, "CONTROLE: een tweede keer op v1.1 hoort te FALEN, maar ging door")
        except AssertionError:
            ok(True, "CONTROLE: zetten op een nummer dat er niet staat, faalt luid")
        ok(ver.read_text(encoding="utf-8").strip() == "v1.2",
           "en dan blijft versie.txt staan waar hij stond (" + ver.read_text(encoding="utf-8").strip() + ")")

    print("")
    if fout[0]:
        print("%d fout" % fout[0])
        return 1
    print("alles goed")
    return 0


if __name__ == "__main__":
    if "--zelftest" in sys.argv:
        sys.exit(_zelftest())
    print("Dit bestand is hulp voor de patchscripts in claude/. Zie de kop.")
    print("  python3 claude/patchhulp.py --zelftest")
