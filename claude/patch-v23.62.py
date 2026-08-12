#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.62: gedoseerd betekent ook: niet acht vragen achter één stap.

Stefan, na het testen van v23.61: "dat met die microstappen werkt goed, dan heb je focus op een stap
en komt de kennis gedoseerd binnen, dat werkt veel beter."

Dat is een principe, en dus meetbaar. Geteld over alles wat de app aan grammatica heeft:

    soort          onderwerpen  stappen  vragen per stap  max  stappen met >4  1-staps
    concepten           23         69          1,7          2         0           0
    gegenereerd         24         65          3,2          8         3           1
    wizards              5         21          5,3          8        12           0

De concepten zijn wat hij prijst: **1,7 vragen per stap**. Korte brokjes, een zichtbare teller
(1 2 3), en een "stap klaar"-moment ertussen.

En dan het pijnlijke: het onderwerp dat hij gisteren opende, *Hoeveelheden*, staat nu op **één stap
met acht vragen**. Dat heb ik zelf gedaan. v23.61 plakt blokken die bij elkaar horen aan elkaar, en
bij dit onderwerp is dat álles: één brok, dus één stap, dus alle acht de vragen erachter. De
dubbeling was weg en het rijtje stond vooraan, maar de dosering was ik kwijt.

## Wat er verandert

Hoogstens drie vragen per stap voor de gegenereerde onderwerpen. Zijn er meer vragen dan stappen
maal drie, dan gebruikt de microles er minder; de rest blijft gewoon in het echte toetsje staan, en
dat is één knop verderop ("Doe het hele toetsje →"). Een microles is een portie, geen tentamen.

Drie en niet twee, omdat deze onderwerpen langere stappen hebben dan een concept en twee vragen dan
te mager wordt. De concepten blijven op twee: die werken.

## Wat er níét verandert, en dat staat op de lijst voor na de lancering

De vijf handgeschreven wizards zitten op 5,3 vragen per stap, met twaalf van de eenentwintig stappen
boven de vier. Die zijn het verst van de werkende dosering af. Maar hun stappen zijn met de hand
geschreven, met hun eigen vragenreeksen, en daar knippen betekent inhoud herverdelen die iemand
bewust zo heeft neergezet. Bovendien staan ze sinds v23.53 achter dezelfde poort als de concepten:
op dag 1 zijn alleen klemtoon en ser-of-estar open. Dat is werk voor na vrijdag, met de meting erbij.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.62"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "GW_VRAGEN_PER_STAP" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_K = '''  var brok = gwPlak(blokken);
  var k = Math.min(brok.length, 4, vragen.length);
  var bGroep = gwVerdeel(brok.length, k);
  var vGroep = gwVerdeel(vragen.length, k);'''

if DOE_APP:
    if A_K not in src:
        print("Deze index.html ziet er niet uit zoals verwacht; anker ontbreekt:\n  " +
              A_K[:100].replace("\n", " / ") +
              "\n\nDeze patch bouwt op v23.61. Eerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_K, '''  var brok = gwPlak(blokken);
  var k = Math.min(brok.length, 4, vragen.length);
  /* v23.62. Stefan over de microstappen van de concepten: "dan heb je focus op een stap en komt de
     kennis gedoseerd binnen, dat werkt veel beter." Geteld: de concepten zitten op 1,7 vragen per
     stap, de gegenereerde onderwerpen op 3,2 met een uitschieter van 8.

     Die uitschieter was Hoeveelheden, en die heb ik in v23.61 zelf gemaakt: door de blokken die bij
     elkaar horen aan elkaar te plakken werd het één brok, dus één stap, dus alle acht de vragen
     erachter elkaar. De dubbeling was weg en het rijtje stond vooraan, maar de dosering was ik kwijt.

     Meer vragen dan stappen maal drie gebruikt de microles niet. Die blijven gewoon in het echte
     toetsje staan, en dat is één knop verderop ("Doe het hele toetsje"). Een microles is een portie,
     geen tentamen. */
  if(vragen.length > k * GW_VRAGEN_PER_STAP) vragen = vragen.slice(0, k * GW_VRAGEN_PER_STAP);
  var bGroep = gwVerdeel(brok.length, k);
  var vGroep = gwVerdeel(vragen.length, k);''')

    rep('function gwVanSpiek(idx){', '''/* v23.62: hoogstens zoveel vragen per stap in een gegenereerde microles. Drie en niet twee, want
   deze stappen dragen meer tekst dan een concept; de concepten zelf blijven op twee, en die werken
   (gemeten: 1,7 gemiddeld). */
var GW_VRAGEN_PER_STAP = 3;
function gwVanSpiek(idx){''')

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
