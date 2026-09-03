#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtpatch.py (3 sep, v23.230) - veilig aanhaken van nachtelijke content.

WAAROM DIT BESTAAT

De nachtelijke patches haakten hun nieuwe zinnen aan met een tekstanker op het
LAATSTE element van de array:

    rep('"tag": "les4"}\\n];', '"tag": "les4"},\\n ' + NIEUW + '\\n];')

Dat werkt precies één nacht. Zodra er twee nachten op elkaar stapelen (en dat
gebeurde: de patch van 1 sep bleef liggen en moest op 3 sep met de hand worden
teruggevonden) klopt het anker niet meer, want het laatste element is dan een
ander. De patch doet dan niets, of erger: hij doet het op de verkeerde plek.

Hetzelfde gold voor de batchlabels ('batch-28' -> 'batch-29') en voor het
versienummer. Drie soorten literalen die een tweede schrijver niet kan kennen.

Deze module haakt aan op de STRUCTUUR in plaats van op de inhoud: het einde van
de array, de sleutel in EXTRA_CONTENT, het getal in het batchlabel. Een patch die
hier doorheen gaat kan gestapeld worden, en kan twee keer draaien zonder schade.

DE REGELS DIE HIER WORDEN AFGEDWONGEN

  1. Een zin die al bestaat wordt niet nog een keer toegevoegd (idempotent op id).
  2. Elke zin draagt alle verplichte velden. _veldenZin() is de enige plek waar die
     lijst staat; de avondrun leverde op 2 sep acht zinnen zonder "tag" en de
     keuring wees ze af, omdat generator en keuring hun eigen lijstje hadden.
  3. Een lesverwijzing wijst naar een zin die bestaat.
  4. Geen enkel id komt twee keer voor.
  5. Het versienummer wordt hier NIET aangeraakt. Een nachtpatch levert inhoud;
     het nummer hoort bij de aflevering, en die doet de dagsessie in één keer.

GEBRUIK

    import nachtpatch as np
    src = np.laad("index.html")
    src = np.zinToevoegen(src, "SENTENCES", TEKST_VAN_S280)
    src = np.lesKoppelen(src, "a2-4", ["s280"])
    src = np.batchOphogen(src, "a2")
    np.keuring(src)                      # gooit op het eerste probleem
    np.bewaar("index.html", src)
"""
import io, json, re

# Welke velden een oefenzin draagt staat NIET hier. Dat staat in content-lib.js,
# waar de avondrun zijn eigen zinnen mee keurt, en dat is de enige plek waar het
# hoort te staan. Op 2 sep keurde de avondrun acht eigen zinnen af omdat "tag"
# ontbrak; zou deze module zijn eigen lijstje bijhouden, dan konden de twee gaan
# afwijken en zou dezelfde nacht hier stilletjes goed zijn gegaan.
def _veldenZin():
    tekst = io.open(_naast("content-lib.js"), encoding="utf-8").read()
    m = re.search(r"zin:\s*\[([^\]]*)\]", tekst)
    assert m, "NL_VELDEN.zin niet gevonden in content-lib.js"
    velden = re.findall(r'"([^"]+)"', m.group(1))
    assert "tag" in velden and "id" in velden, "NL_VELDEN.zin ziet er onverwacht uit: " + m.group(1)
    return velden


def _naast(bestand):
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), bestand)

# De arrays waar nachtelijke content in mag, en het spoor waar ze bij horen.
ARRAYS = {"SENTENCES": "a2", "B_SENTENCES": "beginner"}
BATCHVELD = {"a2": "batch", "beginner": "batch"}


def laad(pad="index.html"):
    return io.open(pad, encoding="utf-8").read()


def bewaar(pad, src):
    io.open(pad, "w", encoding="utf-8").write(src)


# ---------------------------------------------------------------------------
# de arraystaart vinden zonder op inhoud te ankeren
# ---------------------------------------------------------------------------
def _arrayGrenzen(src, naam):
    """Geeft (index van de openende [, index van de sluitende ]) van var <naam> = [...]."""
    kop = "var " + naam + " = ["
    a = src.find(kop)
    assert a >= 0, "array niet gevonden: " + naam
    i = a + len(kop) - 1                      # op de [
    diepte = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c in '"\'':
            slot = c
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == slot:
                    break
                i += 1
        elif c == "/" and i + 1 < n and src[i + 1] == "/":
            i = src.find("\n", i)
            if i < 0:
                break
        elif c == "/" and i + 1 < n and src[i + 1] == "*":
            i = src.find("*/", i) + 1
        elif c in "[{":
            diepte += 1
        elif c in "]}":
            diepte -= 1
            if diepte == 0:
                return a + len(kop) - 1, i
        i += 1
    raise AssertionError("geen sluitende ] gevonden voor " + naam)


def arrayTekst(src, naam):
    a, b = _arrayGrenzen(src, naam)
    return src[a:b + 1]


def ids(src, naam):
    """Alle ids in een array, in volgorde. Dekt zowel {"id":"s1"} als {id:"bs1"}."""
    tekst = arrayTekst(src, naam)
    return re.findall(r'[{,]\s*"?id"?\s*:\s*"([^"]+)"', tekst)


def alleIds(src):
    uit = {}
    for naam in ["WORDS", "SENTENCES", "QUIZZES", "B_WORDS", "B_SENTENCES", "B_QUIZZES"]:
        try:
            uit[naam] = ids(src, naam)
        except AssertionError:
            pass
    return uit


# ---------------------------------------------------------------------------
# toevoegen
# ---------------------------------------------------------------------------
def _idVan(tekst):
    m = re.search(r'"?id"?\s*:\s*"([^"]+)"', tekst)
    assert m, "dit item heeft geen id: " + tekst[:80]
    return m.group(1)


def zinToevoegen(src, naam, tekst):
    """Hangt één item achter aan de array. Bestaat het id al, dan gebeurt er niets.

    Het item wordt vóór de sluitende ] gezet, met een komma achter het huidige
    laatste element. Dat is de enige plek waar de staartkomma van SENTENCES ooit
    misging (v23.214 kostte acht nachten aan een komma), dus staat hij hier één
    keer goed in plaats van in elk patchscript opnieuw.
    """
    nieuw = _idVan(tekst)
    assert naam in ARRAYS, "onbekende array voor nachtelijke content: " + naam
    if nieuw in ids(src, naam):
        return src                                    # al toegepast
    ontbreekt = [v for v in _veldenZin() if not re.search(r'"?' + v + r'"?\s*:', tekst)]
    assert not ontbreekt, "%s mist verplichte velden: %s" % (nieuw, ", ".join(ontbreekt))
    a, b = _arrayGrenzen(src, naam)
    voor = src[:b].rstrip()
    assert voor.endswith("}") or voor.endswith("["), \
        "de array eindigt op iets onverwachts: " + repr(voor[-40:])
    scheiding = ",\n " if voor.endswith("}") else "\n "
    return voor + scheiding + tekst.strip() + "\n" + src[b:]


# ---------------------------------------------------------------------------
# EXTRA_CONTENT als data, niet als tekst
# ---------------------------------------------------------------------------
def _extraGrenzen(src):
    kop = "var EXTRA_CONTENT = "
    a = src.index(kop)
    b = src.index("\n};", a) + 3
    return a + len(kop), b


def extraLees(src):
    a, b = _extraGrenzen(src)
    return json.loads(src[a:b - 1])          # zonder de puntkomma


def extraSchrijf(src, data):
    """Terugschrijven met dezelfde inspringing, zodat de diff alleen de wijziging toont."""
    a, b = _extraGrenzen(src)
    return src[:a] + json.dumps(data, indent=1, ensure_ascii=False) + ";" + src[b:]


def lesKoppelen(src, lesId, nieuwe, soort="sents"):
    """Hangt ids aan een les in EXTRA_CONTENT. Bestaat de les nog niet, dan komt hij erbij."""
    d = extraLees(src)
    lessen = d.setdefault("lessen", {})
    les = lessen.setdefault(lesId, {"words": [], "sents": [], "quizzes": []})
    for k in ["words", "sents", "quizzes"]:
        les.setdefault(k, [])
    for x in nieuwe:
        if x not in les[soort]:
            les[soort].append(x)
    return extraSchrijf(src, d)


# ---------------------------------------------------------------------------
# batchlabels: het getal komt uit het bestand, niet uit het patchscript
# ---------------------------------------------------------------------------
def batchNu(src, spoor):
    m = re.search(r'\b' + spoor + r':\s*\{[^}]*batch:"([^"]+)"', src)
    assert m, "geen batchlabel gevonden voor spoor " + spoor
    return m.group(1)


def batchOphogen(src, spoor):
    huidig = batchNu(src, spoor)
    m = re.match(r"^(.*?)(\d+)$", huidig)
    assert m, "batchlabel heeft geen getal aan het eind: " + huidig
    nieuw = m.group(1) + str(int(m.group(2)) + 1)
    a = src.index('batch:"' + huidig + '"')
    return src[:a] + 'batch:"' + nieuw + '"' + src[a + len('batch:"' + huidig + '"'):]


# ---------------------------------------------------------------------------
# de keuring: dezelfde vier vragen, elke nacht
# ---------------------------------------------------------------------------
def keuring(src):
    problemen = []
    bekend = alleIds(src)

    # 1. geen enkel id twee keer, ook niet over de arrays heen
    plat = []
    for naam, rij in bekend.items():
        for x in rij:
            plat.append((x, naam))
    gezien = {}
    for x, naam in plat:
        if x in gezien:
            problemen.append("id %s staat twee keer (%s en %s)" % (x, gezien[x], naam))
        gezien[x] = naam

    # 2. elke zin draagt alle verplichte velden
    for naam in ARRAYS:
        tekst = arrayTekst(src, naam)
        for stuk in re.findall(r"\{[^{}]*\}", tekst.replace("\n", " ")):
            if '"id"' not in stuk and "id:" not in stuk:
                continue
            m = re.search(r'"?id"?\s*:\s*"([^"]+)"', stuk)
            if not m:
                continue
            # alt is een array en valt buiten de simpele {..}-vangst; sla die over
            if '"alt"' not in stuk and "alt:" not in stuk:
                continue
            ontbreekt = [v for v in _veldenZin() if not re.search(r'"?' + v + r'"?\s*:', stuk)]
            if ontbreekt:
                problemen.append("%s mist %s" % (m.group(1), ", ".join(ontbreekt)))

    # 3. elke lesverwijzing wijst naar iets dat bestaat
    alles = set(gezien)
    d = extraLees(src)
    # "lessen" is een map van lesId naar aanvullingen; "nieuweLessen" een lijst van
    # hele lessen die hun eigen id dragen. Twee vormen, dezelfde vraag.
    paren = list((d.get("lessen") or {}).items())
    paren += [(les.get("id", "?"), les) for les in (d.get("nieuweLessen") or [])]
    for lesId, les in paren:
        for soort in ["words", "sents", "quizzes"]:
            for x in (les.get(soort) or []):
                if x not in alles:
                    problemen.append("les %s verwijst naar %s, en die bestaat niet" % (lesId, x))

    assert not problemen, "keuring afgekeurd:\n  - " + "\n  - ".join(problemen)
    return True


# ---------------------------------------------------------------------------
# de zelfproef: een keuring die alles goedkeurt keurt niets
# ---------------------------------------------------------------------------
def proef(src):
    """Bouwt vier kapotte gevallen en eist dat de keuring ze allemaal ziet.

    Een controlegeval hoor je te BOUWEN, niet te VINDEN: deze vier kunnen niet per
    ongeluk groen staan omdat het bestand toevallig in orde is.
    """
    uit = []

    def moetKlappen(naam, kapot):
        try:
            keuring(kapot)
        except AssertionError as e:
            uit.append("  ✓ " + naam)
            return
        uit.append("  ✗ " + naam + " -- de keuring liet dit door")
        raise AssertionError(naam)

    # 1. een zin zonder tag (dit is wat de avondrun op 2 sep acht keer leverde)
    z = ids(src, "SENTENCES")[-1]
    a, b = _arrayGrenzen(src, "SENTENCES")
    stuk = src[a:b]
    m = list(re.finditer(r'"?id"?\s*:\s*"' + re.escape(z) + r'"', stuk))[-1]
    eind = stuk.index("}", m.start())
    zonderTag = stuk[:m.start()] + re.sub(r',\s*"?tag"?\s*:\s*"[^"]*"', "", stuk[m.start():eind]) + stuk[eind:]
    assert zonderTag != stuk, "het controlegeval veranderde niets, dus meet proef 1 niets"
    moetKlappen("een zin zonder tag wordt afgekeurd", src[:a] + zonderTag + src[b:])

    # 2. een les die naar een onbestaande zin wijst
    moetKlappen("een les die naar een onbestaande zin wijst wordt afgekeurd",
                lesKoppelen(src, "a2-4", ["s99999"]))

    # 3. een dubbel id
    d = extraLees(src)
    dubbel = zinToevoegen(src, "SENTENCES",
                          '{"id":"' + z + '","lvl":2,"nl":"x","en":"x","es":"x","alt":["x"],'
                          '"uitleg":"x","ue":"x","tag":"x"}')
    if dubbel == src:
        # zinToevoegen weigert het al, en dat is de bedoeling: dan bouwen we het met de hand
        aa, bb = _arrayGrenzen(src, "SENTENCES")
        voor = src[:bb].rstrip()
        dubbel = (voor + ',\n {"id":"' + z + '","lvl":2,"nl":"x","en":"x","es":"x","alt":["x"],'
                  '"uitleg":"x","ue":"x","tag":"x"}\n' + src[bb:])
    moetKlappen("een dubbel id wordt afgekeurd", dubbel)

    # 4. en het omgekeerde: het echte bestand komt er wél doorheen
    keuring(src)
    uit.append("  ✓ CONTROLE: het echte bestand komt er wel doorheen")

    # 5. EXTRA_CONTENT gaat er ongeschonden doorheen als je niets verandert
    heen = extraSchrijf(src, extraLees(src))
    assert heen == src, "EXTRA_CONTENT verandert al bij lezen-en-terugschrijven"
    uit.append("  ✓ EXTRA_CONTENT overleeft lezen en terugschrijven letterlijk")

    # 6. tweemaal dezelfde zin toevoegen levert één zin op
    nieuw = ('{"id":"zzz-proef","lvl":2,"nl":"x","en":"x","es":"x","alt":["x"],'
             '"uitleg":"x","ue":"x","tag":"x"}')
    een = zinToevoegen(src, "SENTENCES", nieuw)
    twee = zinToevoegen(een, "SENTENCES", nieuw)
    assert een != src and een == twee, "zinToevoegen is niet idempotent"
    assert ids(een, "SENTENCES")[-1] == "zzz-proef", "de nieuwe zin staat niet achteraan"
    keuring(een)
    uit.append("  ✓ tweemaal dezelfde zin toevoegen levert één zin op, achteraan")

    # 7. het batchlabel telt door zonder dat het oude getal in de patch staat
    op = batchOphogen(src, "a2")
    assert batchNu(op, "a2") != batchNu(src, "a2"), "het batchlabel liep niet op"
    assert batchNu(op, "beginner") == batchNu(src, "beginner"), "het andere spoor liep mee op"
    uit.append("  ✓ het batchlabel loopt op zonder dat het oude getal in de patch staat (%s -> %s)"
               % (batchNu(src, "a2"), batchNu(op, "a2")))
    return uit


if __name__ == "__main__":
    import sys
    args = [a for a in sys.argv[1:] if a != "--proef"]
    pad = args[0] if args else "index.html"
    s = laad(pad)
    if "--proef" in sys.argv:
        print("zelfproef:")
        for r in proef(s):
            print(r)
        print("alles goed")
    else:
        keuring(s)
        tel = {k: len(v) for k, v in alleIds(s).items()}
        print("keuring akkoord ::", tel)
        print("batch ::", batchNu(s, "a2"), "/", batchNu(s, "beginner"))
