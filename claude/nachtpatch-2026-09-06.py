#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtpatch 6 sep - twee A0-drillzinnen op Ilona's verse fouten van 4 september.

WAT HIER IN ZIT

Alle clusters komen uit de diff van de cumulatieve foutenmap tussen de
logsnapshot van 4 sep (1c486ac, de basis van de 5-sep-nachtrun) en die van
5 sep (e548705). Het venster bevat alleen nieuwe data van Ilona (sessie
4 sep 17:44-17:48) en Elise (4 sep 09:48). Stefans recentste entry (4 sep
05:53) staat in beide snapshots en is al door de 5-sep-run verwerkt: nul
gegroeide A2-clusters, dus geen A2-werk.

  bs85  schoolspullen: el lápiz (k79, 0→3), el bolígrafo (k78, 0→2),
        la goma (k80, 0→2) — het vervolg op het kern-school-cluster dat
        bs83/bs84 al dekten (pizarra/pregunta/ejercicio/unidad/página);
        deze drie spullen zaten daar nog niet in.
  bs86  woordvolgorde-reparatie van bs3 (2→4, letterlijke invoer
        "vivo los en países bajos"): en los Países Bajos als vast blokje,
        met el hermano (b20, +1) als tweede aanraking erbij.

Elise: alleen k14 en k15 elk 0→1, onder de drempel. Verder niets gedrild:
bq-preguntas/bq-pronunciacion/gramwiz-missers zijn gegenereerde drills
(vast beleid), en alle andere Ilona-groei is +1.

IDS: s284-s296 blijven van avondrun-draft + PR #4, s297-s312 zijn van de
wachtrij-patches van 4 en 5 sep. Deze patch raakt alleen B_SENTENCES en
gebruikt bs85/bs86 (laatste op main: bs84; de wachtrij gebruikt geen bs-ids).

Het versienummer wordt hier niet aangeraakt. Een nachtpatch levert inhoud;
het nummer hoort bij de aflevering.

    python3 claude/nachtpatch-2026-09-06.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import nachtpatch as np

PAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")

# ---------------------------------------------------------------------------
# A0, uit Ilona's fouten van 4 september
# ---------------------------------------------------------------------------
A0 = [
 ("a0-2", '''{id:"bs85", lvl:1, nl:"Ik heb voor de les een pen, een potlood en een gum nodig.", en:"For class I need a pen, a pencil and an eraser.", es:"Para la clase necesito un bolígrafo, un lápiz y una goma.", alt:["para la clase necesito un bolígrafo, un lápiz y una goma","para la clase necesito un boligrafo, un lapiz y una goma","necesito un bolígrafo, un lápiz y una goma para la clase"],
  uitleg:"Je drie schoolspullen van deze week in één zin: el bolígrafo = de pen, el lápiz = het potlood en la goma = de gum. Bolígrafo en lápiz zijn mannelijk, goma is vrouwelijk — daarom un bolígrafo, un lápiz, una goma. Lápiz draagt een accent op de a (meervoud: lápices). Necesito = ik heb nodig, van necesitar, gewoon regelmatig.", ue:"Your three school items of this week in one sentence: el bolígrafo = the pen, el lápiz = the pencil and la goma = the eraser. Bolígrafo and lápiz are masculine, goma is feminine — hence un bolígrafo, un lápiz, una goma. Lápiz carries an accent on the a (plural: lápices). Necesito = I need, from necesitar, plainly regular.", tag:"escuela"}'''),
 ("a0-1", '''{id:"bs86", lvl:1, nl:"Mijn broer woont ook in Nederland.", en:"My brother also lives in the Netherlands.", es:"Mi hermano también vive en los Países Bajos.", alt:["mi hermano también vive en los países bajos","mi hermano tambien vive en los paises bajos"],
  uitleg:"De volgorde ging deze week mis ('vivo los en países bajos'): het is altijd en los Países Bajos — eerst en (in), dan los (de), dan de naam. Zeg het als één blokje: en-los-Países-Bajos. Vivir: vivo, vives, vive — hier vive, want mi hermano is een hij. El hermano = de broer, la hermana = de zus. También = ook.", ue:"The word order slipped this week ('vivo los en países bajos'): it is always en los Países Bajos — first en (in), then los (the), then the name. Say it as one chunk: en-los-Países-Bajos. Vivir: vivo, vives, vive — here vive, because mi hermano is a he. El hermano = the brother, la hermana = the sister. También = also.", tag:"basis"}'''),
]


def main():
    src = np.laad(PAD)
    was = np.ids(src, "SENTENCES") + np.ids(src, "B_SENTENCES")

    for les, tekst in A0:
        src = np.zinToevoegen(src, "B_SENTENCES", tekst)
        src = np.lesKoppelen(src, les, [np._idVan(tekst)])

    nu = np.ids(src, "SENTENCES") + np.ids(src, "B_SENTENCES")
    nieuw = [x for x in nu if x not in was]
    if not nieuw:
        print("stond er al, niets gedaan")
        return

    # het batchlabel loopt per spoor één keer op, en alleen als er iets bij kwam
    if any(x.startswith("s") and not x.startswith("bs") for x in nieuw):
        src = np.batchOphogen(src, "a2")
    if any(x.startswith("bs") for x in nieuw):
        src = np.batchOphogen(src, "beginner")

    np.keuring(src)
    np.bewaar(PAD, src)
    print("toegevoegd:", ", ".join(nieuw))
    print("batch:", np.batchNu(src, "a2"), "/", np.batchNu(src, "beginner"))


if __name__ == "__main__":
    main()
