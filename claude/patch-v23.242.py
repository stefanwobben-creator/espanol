#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.242 - vijf kaarten zetten de bijbetekenis vooraan
#
# Stefan, bij het woordkaartje van derecho: "klein foutje moet rechts zijn niet recht". En daarna:
# "misschien moet je even grote check doen of je nog meer van dit soort fouten ziet."
#
# EERST HET CONFLICT, WANT DE CORRECTIE ZELF KLOPTE NIET
#
#     el derecho        het recht (juridisch), en de studie Rechten. Vandaar tag cerv-school.
#     derecho           als bijwoord: rechtdoor. "Todo derecho hasta la plaza."
#     derecho / derecha als bijvoeglijk naamwoord: rechter-. "La mano derecha."
#     a la derecha      RECHTS. Dat is la derecha, het vrouwelijke zelfstandig naamwoord.
#
# "Rechts" is geen betekenis van derecho. Maar de kaart had die verwarring wél zelf veroorzaakt, want
# in het veld "meer" stond kaal:
#
#     meer:"rechts; rechtdoor"
#
# Een betekenis die het woord niet heeft, zonder de vorm erbij die je er wél voor nodig hebt.
#
# DE GROTE CHECK
#
# Alle 319 woordkaarten met een "meer"-veld nagelopen (van de 2217 kaarten in totaal). Ik heb eerst
# geprobeerd er een mechanische regel van te maken: "de hoofdvertaling staat rechts van een = in het
# meer-veld, dus hij hoort bij de uitdrukking en niet bij het woord". Die vlagt er vijftien, en twaalf
# daarvan zijn goed: bij "a pie = te voet" en "sin duda = zonder twijfel" betekent het woord zelf
# gewoon voet en twijfel, de uitdrukking hergebruikt dat. Die regel houdt dus geen stand en er komt
# geen proef van; een controle die twaalf keer vals alarm geeft, leert je hem negeren.
#
# Met de hand gelezen blijven er vijf over, en het is steeds dezelfde fout: DE BIJBETEKENIS STAAT
# VOORAAN EN DE HOOFDBETEKENIS IN HET EXTRA-VELD.
#
#   derecho    "recht"        de kaart bood "rechts" aan als losse betekenis van het woord
#   razón      "gelijk"       la razón = de reden. Gelijk hebben is tener razón, en dat stond al
#                             in het meer-veld: de twee velden stonden omgedraaid
#   menudo     "vaak"         menudo = klein, gering. Vaak is a menudo, ook dat stond al in meer
#   odio       "ik haat"      el odio = de haat. Alle acht zusjes (uso, pago, voto, disparo,
#                             comienzo, encuentro, aprecio, cuento) hebben het zelfstandig naamwoord
#                             vooraan en de werkwoordsvorm erachter. Deze ene stond omgekeerd
#   puño       "manchet"      el puño = de vuist, en de kaart draagt tag cerv-lichaam. Een manchet
#                             is geen lichaamsdeel
#
# Vier van de vijf hadden het goede antwoord al in hun eigen extra-veld staan. Dat is geen toeval maar
# de vorm van deze fout: wie een kaart schrijft noteert eerst wat hij tegenkwam en daarna wat het woord
# eigenlijk betekent, en dan blijft de volgorde staan zoals hij ontstond.
#
# WAT ER NIET VERANDERT
#
# presente ("aanwezig", meer "heden; cadeau"): cadeau is voor el presente een formeel en zeldzaam
# gebruik naast el regalo, maar het is niet fout, en de hoofdvertaling klopt. Laten staan.
#
# EN WAT ER OPEN BLIJFT
#
# "Rechts" heeft geen eigen woordkaartje: la derecha komt alleen voor binnen voorbeeldzinnen ("La
# salida está a la derecha"). Dat is een echt gat in de woordenschat, maar een nieuw woord toevoegen
# raakt de Cervantes-nummering en de herhaalwachtrij, en dat is geen reparatie van een klein foutje.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.242"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


# (id, oude regel, nieuwe regel)
KAARTEN = [
    ("cv36",
     '{id:"cv36", es:"derecho", nl:"recht", tag:"cerv-school", sl:"derecho", meer:"rechts; rechtdoor"},',
     '{id:"cv36", es:"derecho", nl:"het recht (juridisch)", tag:"cerv-school", sl:"derecho", meer:"rechtdoor (todo derecho); a la derecha = rechts"},'),
    ("cv609",
     '{id:"cv609", es:"razón", nl:"gelijk", tag:"cerv-religie", sl:"razon", meer:"reden; tener razón = gelijk hebben"},',
     '{id:"cv609", es:"razón", nl:"reden, verstand", tag:"cerv-religie", sl:"razon", meer:"tener razón = gelijk hebben"},'),
    ("cv1306",
     '{id:"cv1306", es:"menudo", nl:"vaak", tag:"cerv-hoeveel", sl:"menudo", meer:"a menudo = vaak; ¡menudo...! = wat een...!"},',
     '{id:"cv1306", es:"menudo", nl:"klein, gering", tag:"cerv-hoeveel", sl:"menudo", meer:"a menudo = vaak; ¡menudo...! = wat een...!"},'),
    ("cv627",
     '{id:"cv627", es:"odio", nl:"ik haat", tag:"cerv-gevoel", sl:"odio", meer:"haat"},',
     '{id:"cv627", es:"odio", nl:"de haat", tag:"cerv-gevoel", sl:"odio", meer:"ik haat (van odiar)"},'),
    ("cv1225",
     '{id:"cv1225", es:"puño", nl:"manchet", tag:"cerv-lichaam", sl:"puno", meer:"vuist"},',
     '{id:"cv1225", es:"puño", nl:"de vuist", tag:"cerv-lichaam", sl:"puno", meer:"manchet (van een mouw)"},'),
    ("cv1314",
     '{id:"cv1314", es:"ruego", nl:"ik smeek je (van rogar)", tag:"cerv-religie", sl:"ruego", meer:"te lo ruego = ik smeek je (van rogar)"},',
     '{id:"cv1314", es:"ruego", nl:"ik smeek (van rogar)", tag:"cerv-religie", sl:"ruego", meer:"te lo ruego = ik smeek je"},'),
]

DOE_APP = any(oud in src for _, oud, _ in KAARTEN)
DOE_VER = _num(huidig_ver) < _num(NIEUW)

if DOE_APP:
    for kid, oud, nieuw in KAARTEN:
        c = src.count(oud)
        assert c == 1, "%s: regel %d keer gevonden (verwacht 1)" % (kid, c)
        src = src.replace(oud, nieuw, 1)
    # de betekenis die derecho niet heeft, staat niet meer kaal op de kaart
    assert 'meer:"rechts;' not in src, "rechts staat nog steeds als losse betekenis"
    assert "a la derecha = rechts" in src, "de vorm die je wel nodig hebt ontbreekt"
    # en geen enkele van de zes heeft nog dezelfde tekst in nl en meer
    for kid, _, nieuw in KAARTEN:
        m = re.search(r'nl:"([^"]*)"[^\n]*?meer:"([^"]*)"', nieuw)
        assert m and m.group(1) != m.group(2), kid + ": nl en meer zijn hetzelfde"
    APP.write_text(src, encoding="utf-8")
    print("index.html: %d kaarten hebben hun hoofdbetekenis terug" % len(KAARTEN))
else:
    print("index.html: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
