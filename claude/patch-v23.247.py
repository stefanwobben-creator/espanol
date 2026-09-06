#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.247 - het nummer wordt gekozen waar het gekozen hoort te worden
#
# Stefan, 6 september, na de hernummering van v23.245 naar v23.246: "machinerie is toch niet zo
# duur?"
#
# Nee. En mijn vervolgvraag daarvoor was slecht gesteld. Ik zette het neer als een afweging tussen
# "een botsing per paar weken met de hand hernummeren" en "machinerie bouwen", alsof de kosten van
# die botsing het hernummeren zijn. Dat is niet waar de kosten zitten. De botsing van gisteren was
# STIL: er kwam geen enkele melding uit, en het gevolg zou geweest zijn dat er twee verschillende
# bomen leefden die allebei v23.245 heten. Het nummer onderaan het scherm is het enige waaraan
# Stefan kan zien wat hij draait. Wijst het er twee aan, dan wijst het er geen aan.
#
#     De kosten van een stille fout zijn niet het repareren, maar de tijd dat je hem niet weet.
#
# ================ DE FOUT, PRECIES ================
#
# Elk patchscript had deze twee regels:
#
#     DOE_VER = _num(huidig_ver) < _num(NIEUW)
#     ...
#     else: print("versie.txt: stond al op " + huidig_ver)
#
# Die else-tak bestaat voor herhaalbaarheid: draai je hetzelfde script twee keer, dan hoort de
# tweede keer niets te doen. Maar hij kan twee verschillende situaties niet uit elkaar houden:
#
#     "ik heb dit al gedaan"                -> terecht niets doen
#     "iemand heeft mijn nummer ingenomen"  -> dit is een botsing en het hoort te knallen
#
# In allebei de gevallen zei hij hetzelfde en ging hij door.
#
#     Een controle waarin de goede en de foute uitkomst dezelfde tak krijgen, controleert niets.
#
# ================ WAT ER NU STAAT ================
#
# Drie stukken, elk met een zelftest die de botsing van 6 september nabouwt en eist dat hij rood
# wordt. Ze zitten op de drie plekken waar het mis kon gaan:
#
#   claude/patchhulp.py     BIJ HET KIEZEN. nummerKiezen(huidig, gepland, doe_app) trekt de twee
#                           vragen uit elkaar. "Moet ik nog iets doen" hangt aan het merkteken van
#                           de ronde; "welk nummer" hangt aan wat er LIGT. Het geplande nummer is
#                           een bodem, geen belofte: ligt er al v23.247, dan wordt deze ronde
#                           v23.248, en dat gebeurt hardop. Een bodem en geen "altijd huidig+1",
#                           want tools/patches.sh speelt de scripts op volgorde na en daar hoort een
#                           ronde het nummer te krijgen waaronder hij bekend staat.
#
#   tools/versiehoger.js    BIJ HET AFLEVEREN. versie.txt hier tegen versie.txt op origin/main.
#                           Hoger is goed. Gelijk terwijl er niets te leveren valt is ook goed.
#                           Gelijk met een andere boom is de botsing, en die is rood, met het
#                           nummer erbij dat het wél moet worden. Een basis die niet te lezen is,
#                           geeft exitcode 3 en geen groen: nul is geen bericht.
#
#   tools/leveren.sh        DE PLEK WAAR DIE CONTROLE DRAAIT. Dit is het stuk dat er echt toe doet.
#                           versiehoger.js bestond gisteren in mijn hoofd ook al; wat ontbrak was
#                           een plek waar hij vanzelf langskomt. De zes commando's die ik elke ronde
#                           met de hand intikte (fetchen, rebasen, format-patch, wegwerp-werkmap,
#                           git am, bomen vergelijken) staan nu in één script met de controles
#                           ertussen, en er komt geen patch uit als er één rood is.
#
#                               Een regel die je moet onthouden, is geen regel.
#
# ================ WAT DE ZELFTESTS ONDERWEG VONDEN ================
#
# Drie echte fouten in mijn eigen nieuwe code, alle drie gevonden door de proef en niet door mij:
#
#   1. `node tools/versiehoger.js | sed 's/^/  /'` gevolgd door `RES=$?` leest de exitcode van SED.
#      Die is altijd 0. De nummercontrole drukte netjes af dat het nummer botste en liet de levering
#      gewoon doorlopen. Exact dezelfde vorm als de fout die deze ronde repareert, twintig regels
#      verderop opnieuw gemaakt.
#   2. De rebase stond vóór de nummercontrole. Maar als de ander hetzelfde nummer heeft gepakt,
#      botsen precies die twee regels bij het rebasen, en dan lees je "de rebase loopt vast" waar
#      het antwoord "hernummer" is. De controle heeft de rebase niet nodig en staat er nu voor.
#   3. Er zat een --geen-fetch in. Die meet de origin/main die je toevallig nog had liggen en meldt
#      opgewekt "hoger dan wat er leeft". Weg.
#
# En één in de proef zelf: met `set -e` aan stopte de zelftest stil bij het eerste geval dat rood
# HOORT te zijn, en telde daarmee de helft van zijn eigen controles niet.
#
#     Een proef die afbreekt op wat hij meet, meet niets.
#
# ================ WAT DIT SCRIPT ZELF DOET ================
#
# Bijna niets, en dat is met opzet. De drie nieuwe bestanden komen via de git-patch; aan index.html
# verandert alleen het nummer. Deze ronde is machinerie, geen app-wijziging, dus er is ook geen
# merkteken in index.html om aan te haken: het nummer IS de hele inhoudelijke uitkomst hier. En hij
# kiest dat nummer via claude/patchhulp.py, want een patroon dat in zijn eigen ronde niet gebruikt
# wordt, is een patroon dat niemand overneemt.
import pathlib
import sys

W = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / "claude"))
import patchhulp  # noqa: E402

APP = W / "index.html"
VER = W / "versie.txt"
GEPLAND = "v23.247"

huidig = VER.read_text(encoding="utf-8").strip()

# Voor een ronde zonder app-wijziging is het nummer zelf het merkteken: er valt niets anders aan
# af te lezen of hij al geland is, en er is ook niets anders om herhaalbaar in te zijn.
DOE_APP = patchhulp.num(huidig) < patchhulp.num(GEPLAND)

nieuw, doe_ver, reden = patchhulp.nummerKiezen(huidig, GEPLAND, DOE_APP)
if reden:
    print("LET OP: " + reden)

if doe_ver:
    patchhulp.zetVersie(APP, VER, huidig, nieuw)
    print("versie.txt: %s -> %s" % (huidig, nieuw))
else:
    print("versie.txt: stond al op " + huidig)

# De controle op deze ronde is de ronde zelf: tools/leveren.sh weigert af te leveren als dit nummer
# al op origin/main leeft. Draai daarom niet dit script maar:
#
#     sh tools/leveren.sh
print("controleer met: node tools/versiehoger.js   (of gewoon: sh tools/leveren.sh)")
