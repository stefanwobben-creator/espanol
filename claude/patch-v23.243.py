#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.243 - rechts en links krijgen een kaartje
#
# Stefan, na de reparatie van derecho: "ja doe maar."
#
# HET GAT, GEMETEN
#
# "Rechts" bestond nergens als woordkaart. la derecha kwam alleen voor BINNEN voorbeeldzinnen ("La
# salida está a la derecha") en in FREQ, de zoeklijst van het woordenboek. Je kon het dus opzoeken,
# maar je kreeg het nooit te leren. Voor links geldt hetzelfde: izquierda staat in FREQ en verder
# nergens.
#
# En dat is precies het gat waar Stefan in liep: hij las derecho, dacht "rechts", en de app had geen
# enkele plek waar die twee uit elkaar werden gehaald.
#
# WAAR ZE HEEN GAAN, EN WAAROM NIET BIJ DE CERVANTES-LIJST
#
# De eerste ingeving was een cv-nummer, want daar staat derecho ook. Nagemeten kan dat niet:
#
#   - de cv-ids lopen aaneengesloten van 1 tot 1376, zonder gaten. Een nummer erbij is een plek
#     claimen in een frequentielijst.
#   - en derecha stáát niet in die lijst. Ik heb PCIC_KEYNIV_RAW nagezocht: derecho wel, derecha
#     niet, izquierda niet. Een woord in de Cervantes-lijst zetten dat er niet in staat, maakt van
#     die lijst een verzameling waar iemand iets bij heeft gedaan, en dan is hij geen bron meer.
#
# Ze gaan naar K_WORDS, de kernwoorden. Die hangen aan geen enkele les en staan altijd open
# (allowedWordIds: "de A1-kernwoorden hangen aan geen enkele les, dus er is niets om te
# ontgrendelen"). Een kaart erbij komt daarmee vanzelf in de wachtrij, zonder dat er een les of een
# nummering aan te pas komt. Tag kern-plaats, waar aquí, allí, entrar en salir ook staan.
#
# ALS PAAR, EN NIET ALLEEN RECHTS
#
# Alleen rechts toevoegen zou een halve kaart zijn. Een richting leer je tegenover zijn tegendeel, en
# wie "a la derecha" kent zonder "a la izquierda" heeft de helft van een aanwijzing.
#
# DE VORM: a la derecha, EN NIET la derecha
#
# Dat is de brok die je zegt en hoort ("gira a la derecha", "está a la derecha"). Het losse la derecha
# staat in het extra-veld erbij, want dat is de vorm waar het lidwoord zichtbaar wordt en dus waar het
# verschil met derecho aan hangt. En op de kaart van rechts staat die val er meteen bij, in dezelfde
# richting als de reparatie van v23.242: derecho is rechtdoor.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.243"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


ANKER = '{id:"k280", es:"dorar", nl:"bruin bakken", tag:"cocina", ej:"Dora los ajos treinta segundos.", ejnl:"Bak de knoflook dertig seconden bruin."}'

NIEUWE = ANKER + ''',
  /* v23.243: rechts en links. Ze bestonden alleen binnen voorbeeldzinnen en in de zoeklijst, dus je
     kon ze opzoeken maar nooit leren. Naar K_WORDS en niet naar de Cervantes-lijst: die loopt
     aaneengesloten van cv1 tot cv1376 en derecha en izquierda staan niet in PCIC_KEYNIV_RAW. Een
     woord in een bronlijst zetten dat er niet in hoort, maakt die lijst waardeloos als bron. */
  {id:"k281", es:"a la derecha", nl:"rechts", tag:"kern-plaats", ej:"La farmacia está a la derecha.", ejnl:"De apotheek is rechts.", meer:"la derecha = de rechterkant; let op: derecho is rechtdoor"},
  {id:"k282", es:"a la izquierda", nl:"links", tag:"kern-plaats", ej:"Gira a la izquierda en la esquina.", ejnl:"Sla op de hoek linksaf.", meer:"la izquierda = de linkerkant"}'''

DOE_APP = 'id:"k281"' not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

if DOE_APP:
    c = src.count(ANKER)
    assert c == 1, "het anker staat %d keer in het bestand" % c
    src = src.replace(ANKER, NIEUWE, 1)
    for nodig in ['id:"k281"', 'id:"k282"', 'es:"a la derecha"', 'es:"a la izquierda"']:
        assert nodig in src, "ontbreekt: " + nodig
    # de val staat op de kaart, want dat is waar Stefan over struikelde
    assert "derecho is rechtdoor" in src, "de verwijzing naar derecho ontbreekt"
    # en ze staan in K_WORDS en niet in de Cervantes-lijst
    i = src.index("var K_WORDS"); j = src.index("\n];", i)
    assert 'id:"k281"' in src[i:j] and 'id:"k282"' in src[i:j], "ze staan niet in K_WORDS"
    # Op de es-velden en niet op de kale tekst: "a la derecha" staat sinds v23.242 in het meer-veld
    # van cv36, en dat hoort daar. Een controle die de toelichting van de buurman aanwijst,
    # controleert niets.
    i2 = src.index("var C_WORDS"); j2 = src.index("\n];", i2)
    assert 'es:"a la derecha"' not in src[i2:j2], "ze zijn in de Cervantes-lijst beland"
    assert 'es:"a la izquierda"' not in src[i2:j2], "ze zijn in de Cervantes-lijst beland"
    APP.write_text(src, encoding="utf-8")
    print("index.html: rechts en links staan erin (k281, k282)")
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
