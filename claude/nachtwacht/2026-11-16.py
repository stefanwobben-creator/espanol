#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nachtpatch 16 nov 2026: lidwoord bij algemene begrippen (b1-12).

FOUT: s323, 15 nov: "...entre trabajo y el tiempo libre" (lidwoord vergeten voor trabajo).
Zelfde patroon als s5 ("me cuestan palabras largas") en s10 ("nos gustan retos"):
het Nederlands zegt "werk", "uitdagingen", "lange woorden" zonder lidwoord, het Spaans
zet er bij een algemeen begrip wel een lidwoord voor. Drie zinnen die de regel oefenen,
een vierde als grens (onbepaalde hoeveelheid als lijdend voorwerp: geen lidwoord).

IDS: deze run kon OPENSTAAND.md niet lezen en tools/nachtpatch.py in de repo had nog geen
volgendeVrij(). Daarom kiest het script zijn ids PAS BIJ HET TOEPASSEN: via
np.volgendeVrij als die bestaat, anders boven het hoogste s-id in het bestand en boven
alles wat de avondrun in tools/avondrun-hart.json / curriculum-laatste.json noemt.
Idempotent op de Spaanse tekst: een tweede run zegt "stond er al".

b1-12 is een nieuweLes in EXTRA_CONTENT; lessen["b1-12"] wordt door pasExtraContentToe
NIET toegepast (die loopt vóór de nieuweLessen erbij komen), dus de zinnen gaan direct
in nieuweLessen[b1-12].sents.
"""
import os, re, sys, json, io
HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HIER, ".."))  if os.path.basename(HIER) == "claude" else None
sys.path.insert(0, os.path.join(os.getcwd(), "tools"))
import nachtpatch as np

PAD = sys.argv[1] if len(sys.argv) > 1 else "index.html"
LES = "b1-12"

ZINNEN = [
    {"lvl": 2, "nl": "Ik houd van muziek, maar ik haat lawaai.",
     "en": "I love music, but I hate noise.",
     "es": "Me gusta la música, pero odio el ruido.",
     "alt": ["me gusta la musica pero odio el ruido", "me encanta la música, pero odio el ruido",
             "me encanta la musica pero odio el ruido"],
     "uitleg": "Muziek en lawaai in het algemeen: in het Nederlands zonder lidwoord, in het Spaans mét: la música, el ruido. Net als bij s10 (nos gustan los retos): na gustar en odiar staat het lidwoord er altijd.",
     "ue": "Music and noise in general: no article in English or Dutch, but Spanish needs one: la música, el ruido. Same as s10 (nos gustan los retos): after gustar and odiar the article is always there.",
     "tag": "artículos"},
    {"lvl": 2, "nl": "Werk is belangrijk, maar gezondheid gaat voor.",
     "en": "Work is important, but health comes first.",
     "es": "El trabajo es importante, pero la salud es lo primero.",
     "alt": ["el trabajo es importante pero la salud es lo primero",
             "el trabajo es importante pero la salud va primero",
             "el trabajo es importante, pero la salud va primero"],
     "uitleg": "Werk en gezondheid als algemeen begrip, als onderwerp van de zin: el trabajo, la salud. Dit is de fout uit s323 (entre trabajo): ook na entre blijft het el trabajo y el tiempo libre.",
     "ue": "Work and health as general ideas, as the subject: el trabajo, la salud. This is the slip from s323 (entre trabajo): after entre it stays el trabajo y el tiempo libre.",
     "tag": "artículos"},
    {"lvl": 2, "nl": "Groenten zijn gezond, maar suiker niet.",
     "en": "Vegetables are healthy, but sugar isn't.",
     "es": "Las verduras son sanas, pero el azúcar no.",
     "alt": ["las verduras son sanas pero el azucar no", "las verduras son saludables pero el azúcar no",
             "las verduras son saludables pero el azucar no", "las verduras son sanas, pero el azúcar no"],
     "uitleg": "Groenten in het algemeen, als onderwerp: las verduras, met lidwoord, ook in het meervoud. Suiker in het algemeen: el azúcar.",
     "ue": "Vegetables in general, as the subject: las verduras, with the article, plural too. Sugar in general: el azúcar.",
     "tag": "artículos"},
    {"lvl": 2, "nl": "Ik eet geen vlees en ik drink koffie zonder suiker.",
     "en": "I don't eat meat and I drink coffee without sugar.",
     "es": "No como carne y tomo café sin azúcar.",
     "alt": ["no como carne y tomo cafe sin azucar", "no como carne y bebo café sin azúcar",
             "no como carne y bebo cafe sin azucar"],
     "uitleg": "De grens van de regel: gaat het om 'wat' je eet of drinkt (een onbepaalde hoeveelheid, lijdend voorwerp), dan GEEN lidwoord: no como carne, tomo café, sin azúcar. Zeg je iets over het begrip zelf (onderwerp, of na gustar), dan wel: la carne es cara, me gusta el café.",
     "ue": "Where the rule stops: when it is about 'some' of something you eat or drink (an unspecified amount, the object), NO article: no como carne, tomo café, sin azúcar. When you say something about the thing itself (subject, or after gustar), you do use it: la carne es cara, me gusta el café.",
     "tag": "artículos"},
]

def _num(x):
    m = re.match(r"^s(\d+)$", x)
    return int(m.group(1)) if m else None

def _geclaimd():
    """s-ids die de avondrun noemt (ook afgekeurde): die laten we met rust."""
    uit = set()
    for f in ["tools/avondrun-hart.json", "tools/curriculum-laatste.json"]:
        try:
            uit |= set(int(n) for n in re.findall(r'\bs(\d+)\b', io.open(f, encoding="utf-8").read()))
        except IOError:
            pass
    return uit

def volgende(src):
    if hasattr(np, "volgendeVrij"):
        return np.volgendeVrij(src, "s")
    alle = [n for rij in np.alleIds(src).values() for n in map(_num, rij) if n]
    hoog = max(alle + list(_geclaimd()) + [0])
    return "s%d" % (hoog + 1)

src = np.laad(PAD)
d = np.extraLees(src)
les = [l for l in d["nieuweLessen"] if l.get("id") == LES]
assert les, "les %s niet gevonden in nieuweLessen" % LES
nieuw = []
for z in ZINNEN:
    if ('"es":"%s"' % z["es"]) in src or ('"es": "%s"' % z["es"]) in src:
        print("stond er al:", z["es"])
        continue
    zid = volgende(src)
    item = dict([("id", zid)] + list(z.items()))
    src = np.zinToevoegen(src, "SENTENCES", json.dumps(item, ensure_ascii=False, separators=(",", ":")))
    nieuw.append(zid)
    print("toegevoegd:", zid, z["es"])
if nieuw:
    d = np.extraLees(src)
    les = [l for l in d["nieuweLessen"] if l.get("id") == LES][0]
    for x in nieuw:
        if x not in les["sents"]:
            les["sents"].append(x)
    src = np.extraSchrijf(src, d)
    src = np.batchOphogen(src, "a2")
np.keuring(src)
np.bewaar(PAD, src)
print("klaar:", ", ".join(nieuw) if nieuw else "niets nieuw")
