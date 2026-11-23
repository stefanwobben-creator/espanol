#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtpatch 23 nov - drie A2-drillzinnen bij a2-4 (Mi casa, tu casa) op Stefans verse fouten.

WAT HIER IN ZIT

Diff van de cumulatieve foutenmap tussen logsnapshot 7b57b29 (21 nov, laatste
Stefan-dagdoel 20 nov 09:59) en 5a45685 (22 nov, nieuw dagdoel 21 nov 21:00).
Gegroeid, en nog nergens in een zin gedrild (alleen in C_WORDS, de Cervantes-
woordenlijst; grep op index.html vindt ze in geen enkele oefenzin):

  la sábana  (cv1171)  2 -> 5, goed 0
  la lejía   (cv1169)  2 -> 5, goed 0
  el colchón (cv1166)  2 -> 4, goed 0

Alle drie huis-woorden, dus ze horen bij a2-4, net als s306/s307 eerder (die
haalden ook losse huiswoorden uit de foutenlog naar deze les).

Bewust NIET gedrild:
  - herramienta 2 -> 3 en alle andere cv-woorden: +1, onder de drempel.
  - w414-w423 (relatie) en q-b1-19#3: eerste kennismaking met een B1-les,
    geen gegroeid cluster.
  - quecual/imperativo/negacion in gram: alleen goed-tellingen omhoog.

IDS: de keuring-helper volgendeVrij en tools/ids.json uit de instructies
bestaan (nog) niet in de repo. Daarom kiest dit script zijn ids pas bij het
toepassen: hoogste s-id in het bestand en in tools/curriculum-laatste.json
(beloofde maar nog niet geplaatste avondrun-ids, nu s562-s573) plus 1. Gaten
(s570, s571, s580) worden overgeslagen. Idempotent op de Spaanse zin, niet op
het id: draait hij twee keer, of heeft de avondrun intussen ids opgeschoven,
dan zegt hij "stond er al" of pakt hij gewoon de volgende vrije.

Het versienummer wordt hier niet aangeraakt.

    python3 claude/nachtpatch-2026-11-23.py
"""
import io, json, os, re, sys
HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "tools"))
import nachtpatch as np

PAD = os.path.join(HIER, "..", "index.html")
BELOFTE = os.path.join(HIER, "..", "tools", "curriculum-laatste.json")
LES = "a2-4"

ZINNEN = [
 {"lvl": 2,
  "nl": "Elke zondag was ik de lakens en leg ik een schoon laken op het bed.",
  "en": "Every Sunday I wash the sheets and put a clean sheet on the bed.",
  "es": "Cada domingo lavo las sábanas y pongo una sábana limpia en la cama.",
  "alt": ["todos los domingos lavo las sábanas y pongo una sábana limpia en la cama",
          "cada domingo lavo las sabanas y pongo una sabana limpia en la cama"],
  "uitleg": "La sábana = het laken, vijf missers en nog geen enkele keer goed. Let op het accent: SÁ-ba-na, klemtoon vooraan. Zonder accent is la sabana de savanne, een heel ander woord. Sábana is vrouwelijk, dus una sábana limpia (limpia met -a). Lavar = wassen, poner = leggen/zetten, met pongo als onregelmatige ik-vorm.",
  "ue": "La sábana = the sheet, five misses and not one hit yet. Mind the accent: SÁ-ba-na, stress at the front. Without the accent, la sabana is the savanna, a different word entirely. Sábana is feminine, so una sábana limpia (limpia with -a). Lavar = to wash, poner = to put, with pongo as the irregular I-form.",
  "tag": "les4"},
 {"lvl": 2,
  "nl": "Ik maak de badkamer schoon met een beetje bleekwater en veel water.",
  "en": "I clean the bathroom with a little bleach and lots of water.",
  "es": "Limpio el baño con un poco de lejía y mucha agua.",
  "alt": ["limpio el cuarto de baño con un poco de lejía y mucha agua",
          "limpio el baño con un poco de lejia y mucha agua"],
  "uitleg": "La lejía = bleekwater, ook vijf missers. Klemtoon op de í: le-JÍ-a, drie lettergrepen; het accent breekt de ie in tweeën. Vrouwelijk: la lejía. Zo heet het in Spanje; in Latijns-Amerika hoor je vaker el cloro. Un poco de + zelfstandig naamwoord = een beetje: un poco de lejía. En mucha agua, niet mucho: agua is vrouwelijk, al zeg je el agua.",
  "ue": "La lejía = bleach, also five misses. Stress on the í: le-JÍ-a, three syllables; the accent splits the ie in two. Feminine: la lejía. That is the word in Spain; in Latin America you will more often hear el cloro. Un poco de + noun = a little: un poco de lejía. And mucha agua, not mucho: agua is feminine, even though you say el agua.",
  "tag": "les4"},
 {"lvl": 2,
  "nl": "Het matras in de logeerkamer is te hard, daarom slaap ik slecht.",
  "en": "The mattress in the guest room is too hard, so I sleep badly.",
  "es": "El colchón de la habitación de invitados es demasiado duro, por eso duermo mal.",
  "alt": ["el colchón del cuarto de invitados es demasiado duro por eso duermo mal",
          "el colchon de la habitacion de invitados es demasiado duro por eso duermo mal"],
  "uitleg": "El colchón = het matras, vier missers. Ezelsbrug: la colcha is de sprei, en -ón maakt iets groots, dus el colchón is de dikke 'sprei' waar je op ligt. Woorden op -ón zijn bijna altijd mannelijk: el colchón, dus duro met -o. Meervoud: los colchones, zonder accent (de klemtoon blijft op dezelfde lettergreep). Dormir is een schoenwerkwoord: o wordt ue, duermo.",
  "ue": "El colchón = the mattress, four misses. Memory hook: la colcha is the bedspread, and -ón makes something big, so el colchón is the thick 'bedspread' you lie on. Words ending in -ón are almost always masculine: el colchón, hence duro with -o. Plural: los colchones, without the accent (the stress stays on the same syllable). Dormir is a boot verb: o becomes ue, duermo.",
  "tag": "les4"},
]


def _hoogste(src):
    hoog = 0
    for naam in ["SENTENCES", "B_SENTENCES"]:
        for x in np.ids(src, naam):
            m = re.match(r"^s(\d+)$", x)
            if m:
                hoog = max(hoog, int(m.group(1)))
    try:
        b = json.load(io.open(BELOFTE, encoding="utf-8"))
        beloofd = (b.get("reparatie") or {}).get("zinnen", []) + (b.get("nieuweLes") or {}).get("sents", [])
        for x in beloofd:
            m = re.match(r"^s(\d+)$", x)
            if m:
                hoog = max(hoog, int(m.group(1)))
    except (IOError, ValueError):
        pass
    return hoog


def _bestaatAl(src, es):
    return json.dumps(es, ensure_ascii=False) in np.arrayTekst(src, "SENTENCES")


def main():
    src = np.laad(PAD)
    nieuw = []
    for z in ZINNEN:
        if _bestaatAl(src, z["es"]):
            continue
        zid = "s%d" % (_hoogste(src) + 1)
        item = dict([("id", zid)] + list(z.items()))
        src = np.zinToevoegen(src, "SENTENCES", json.dumps(item, ensure_ascii=False))
        src = np.lesKoppelen(src, LES, [zid])
        nieuw.append(zid)
    if not nieuw:
        print("stond er al, niets gedaan")
        return
    src = np.batchOphogen(src, "a2")
    np.keuring(src)
    np.bewaar(PAD, src)
    print("toegevoegd:", ", ".join(nieuw), "bij", LES)
    print("batch:", np.batchNu(src, "a2"))


if __name__ == "__main__":
    main()
