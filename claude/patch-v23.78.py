#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.78: het lidwoord hoort bij het Spaanse woord, niet in het antwoord.

Stefan, 13 aug, met een schermafdruk erbij: "bij de nieuwe woordjes valt me op dat soms het spaanse
woord er ook bij staat en verder valt me op dat de lidwoorden niet meer worden toegevoegd. Dat moet
altijd en de spaanse zin mag nooit al worden getoond."

Op die kaart stond:

    planeet (el planeta!)          <- de vraagkant
    planeta                        <- het antwoord

Twee dingen tegelijk mis. Het antwoord staat op de vraag, en het lidwoord staat op de verkeerde
kant: "el planeta" hoort de Spaanse kaart te zijn, niet een geheugensteun in de Nederlandse.

## Geteld, want "soms" is geen maat

    lijst      woorden   met lidwoord op de Spaanse kant
    WORDS         313    149
    B_WORDS       251    112
    K_WORDS       244    166
    C_WORDS      1376      0

En het lek is precies drie keer, alle drie in C_WORDS, alle drie hetzelfde geval: een Grieks
-ma-woord dat mannelijk is en waar iemand dat als uitroep in het antwoordveld heeft gezet.

    cv67    es=planeta   nl=planeet (el planeta!)
    cv655   es=tema      nl=onderwerp, thema (el tema!)
    cv1078  es=sistema   nl=systeem (el sistema!)

Deze patch repareert die drie: het lidwoord verhuist naar de Spaanse kant en de haakjes gaan weg.
Daarmee klopt de kaart én blijft de gendernotitie behouden, want "el planeta" zégt dat het
mannelijk is; dat hoeft er niet nog eens naast te staan.

## Wat deze patch níét doet

De 1376 woorden van de Cervantes-brug hebben geen enkel lidwoord. Dat is geen slordigheid van drie
kaarten maar een eigenschap van hoe die lijst in v23.15 is gegenereerd: het lemma komt uit het Plan
Curricular en de vertaling uit FREQ, en geen van beide bronnen levert een geslacht.

Dat repareren is geen zoek-en-vervang. Per woord zijn er twee vragen ("is dit een zelfstandig
naamwoord?" en "welk geslacht?") en de eerste is de lastige: de lijst zit vol werkwoorden
(quedar), bijvoeglijke naamwoorden (medio) en functiewoorden (lo, que). Een regelmachine haalt daar
misschien negentig procent, en de overige tien procent zijn kaarten die iets beweren wat niet waar
is. Een fout lidwoord op een flitskaart is erger dan geen lidwoord, want je leert het uit je hoofd.

Dat werk hoort dus bij de avondrun, die een taalmodel tot zijn beschikking heeft, met een lijst om
na te lezen. Zie de aantekening in het project.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.78"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.78" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

# (id, oud, nieuw). Het lidwoord verhuist naar es; sl blijft het kale lemma, want pcicNiv() zoekt
# daarmee het niveau op en dat staat in het Plan Curricular zonder lidwoord.
KAARTEN = [
    ('{id:"cv67", es:"planeta", nl:"planeet (el planeta!)", tag:"cerv-natuur", sl:"planeta"}',
     '{id:"cv67", es:"el planeta", nl:"planeet", tag:"cerv-natuur", sl:"planeta"}'),
]

if DOE_APP:
    # De andere twee zoeken we op, want hun tag en volgorde staan hier niet vast en een anker dat
    # ik uit mijn hoofd opschrijf is een anker dat niet klopt.
    for wid, kaal, lid, schoon in (("cv655", "tema", "el tema", None), ("cv1078", "sistema", "el sistema", None)):
        m = re.search(r'\{id:"%s",[^}]*\}' % wid, src)
        if not m:
            print("Kaart %s staat er niet zoals verwacht. Deze patch bouwt op v23.77." % wid)
            sys.exit(1)
        oud = m.group(0)
        nw = oud.replace('es:"%s"' % kaal, 'es:"%s"' % lid)
        nw = re.sub(r'\s*\((el|la) %s!?\)' % kaal, '', nw)
        if nw == oud:
            print("Kaart %s is al goed of ziet er anders uit dan verwacht:\n  %s" % (wid, oud))
            sys.exit(1)
        KAARTEN.append((oud, nw))


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    for oud, nw in KAARTEN:
        rep(oud, nw)
        print("  " + nw)

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
