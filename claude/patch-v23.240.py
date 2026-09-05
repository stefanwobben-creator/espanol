#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.240 - bruikbaar is geen stijleis
#
# Stefan, 5 september: "het belangrijkste bij genereren van zinnen is dat je checkt of zinnen zijn
# die echte mensen zouden zeggen, dus praktisch toepasbaar"
#
# EERST HET GOEDE NIEUWS, WANT DIT IS GEMETEN EN GEEN AANNAME
#
# Die eis staat er al, en hij werkt. In de hartslag van vannacht staan twee afkeuringen, allebei van
# precies deze soort:
#
#   s286: afgekeurd — De inhoud is onzin: niemand zegt dat het 'moeite kost om een prijs te betalen'
#   s289: afgekeurd — grammaticaal correct, maar inhoudelijk onnatuurlijk in het Spaans
#
# Er is dus een tegenlezer die hierop let en die er ook echt zinnen om weggooit.
#
# EN NU HET PROBLEEM MET WAAR HIJ STAAT
#
# In de schrijfopdracht staat de eis als bullet 2 van een blok dat "Stijl-eisen" heet. Bruikbaarheid
# is geen stijl. Stijl is of je "coche" of "carro" schrijft; dit is de vraag of de zin überhaupt de
# moeite waard is om te leren. Een taalmodel dat een lijstje met een kop leest, weegt die kop mee.
#
# En bij de tegenlezer staat hij als punt (4) van vier, ná de grammatica, de vertaling en de uitleg.
# Dat is de omgekeerde volgorde: een zin die niemand zegt hoef je niet meer op zijn uitleg te
# controleren.
#
# WAT ER NU STAAT
#
# Eén blok, BRUIKBAAR, dat in alle drie de schrijfopdrachten vooraan staat en bij de tegenlezer punt
# (1) is. Met Stefans eigen woord erin: praktisch toepasbaar. Niet "zou een mens dit kunnen zeggen"
# maar "zou Stefan dit deze maand kunnen gebruiken" — in een bar, op zijn werk, bij familie, op reis,
# in een gesprek over het leren zelf. Dat is een strengere eis dan grammaticaal correct én dan
# alledaags, en het is de eis die hij noemt.
#
# De zelftest controleert dat het blok in alle drie de opdrachten zit en dat hij vóór de stijl-eisen
# komt. Een volgorde die alleen in een commentaar staat, is geen volgorde.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
CUR = W / "tools" / "curriculum.js"
NIEUW = "v23.240"

huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep_in(pad, anker, nieuw, n=1):
    tekst = pad.read_text(encoding="utf-8")
    c = tekst.count(anker)
    assert c == n, "%s: anker %d keer (verwacht %d): %r" % (pad.name, c, n, anker[:90])
    pad.write_text(tekst.replace(anker, nieuw, n), encoding="utf-8")


cur = CUR.read_text(encoding="utf-8")

if "const BRUIKBAAR" not in cur:
    # 1. de eis uit het stijlblok halen en er een eigen blok van maken
    rep_in(CUR, """const STIJL = `Stijl-eisen (belangrijk):
- Alledaags, natuurlijk Spaans zoals in Spanje gesproken wordt. Geen letterlijk vertaald Nederlands.
- De zin moet ergens over gaan. Iets wat een mens op een gewone dag tegen een ander zegt. Grammaticaal
  kloppen is niet genoeg: "Las mesas son tímidas" (de tafels zijn verlegen) en "Busco las casas" (ik
  zoek de huizen) zijn correct Spaans en toch onbruikbaar, want niemand zegt dat. Kies liever een
  saaie ware zin dan een grammaticaal keurige onzinzin.
- A2-woordenschat, korte zinnen, geen literaire constructies.""",
'''/* ================= BRUIKBAAR IS GEEN STIJLEIS (v23.240) =================

   Stefan, 5 september: "het belangrijkste bij genereren van zinnen is dat je checkt of zinnen zijn
   die echte mensen zouden zeggen, dus praktisch toepasbaar."

   Deze eis stond hieronder als bullet 2 van een blok dat "Stijl-eisen" heet. Stijl is of je "coche"
   of "carro" schrijft. Dit is de vraag of de zin überhaupt de moeite waard is om te leren, en dat is
   de eerste vraag en niet de tweede. Een model dat een lijstje met een kop leest, weegt die kop mee.

   Hij staat nu vooraan in elke schrijfopdracht en is punt (1) bij de tegenlezer. En met Stefans eigen
   woord erin: niet "zou een mens dit kunnen zeggen" maar "zou Stefan dit deze maand kunnen
   gebruiken". Dat is strenger, en het is wat hij vroeg. */
const BRUIKBAAR = `DE EERSTE EIS, VÓÓR ALLE ANDERE: elke zin moet PRAKTISCH TOEPASBAAR zijn.

Stel je de leerling voor: een Nederlander van rond de veertig die Spaans leert om het te gebruiken.
In een bar, op reis, bij de buren, op zijn werk, aan tafel met familie, of in een gesprek over het
leren zelf. Zou hij deze zin deze maand kunnen zeggen of horen? Zo niet, schrijf hem niet op.

Grammaticaal kloppen is niet genoeg. "Las mesas son tímidas" (de tafels zijn verlegen) en "Busco las
casas" (ik zoek de huizen) zijn correct Spaans en toch waardeloos, want niemand zegt dat. Ook niet
genoeg is "het zou kunnen": een zin over een situatie die je met moeite kunt bedenken, is geen zin om
te leren.

Kies liever een saaie ware zin dan een grammaticaal keurige onzinzin. En liever een zin uit een
gesprek dan uit een oefenboek.`;

const STIJL = `Stijl-eisen:
- Alledaags, natuurlijk Spaans zoals in Spanje gesproken wordt. Geen letterlijk vertaald Nederlands.
- A2-woordenschat, korte zinnen, geen literaire constructies.''')

    # 2. het blok vooraan in ALLE DRIE de schrijfopdrachten. Ze delen dezelfde openingsregel, dus dit
    #    is één vervanging die er drie doet, en het aantal wordt afgedwongen.
    rep_in(CUR, """  return `Je maakt oefenmateriaal voor een Nederlandstalige die Spaans leert (A2, AULA 2).
""",
"""  return `Je maakt oefenmateriaal voor een Nederlandstalige die Spaans leert (A2, AULA 2).

${BRUIKBAAR}
""", n=3)

    # 3. en bij de tegenlezer wordt het punt (1). Een zin die niemand zegt hoef je niet meer op zijn
    #    uitleg na te kijken, dus deze vraag hoort vooraan en niet achteraan.
    rep_in(CUR, """  return `Je bent corrector Spaans (Spanje, niveau A2/B1) voor een leerapp. Controleer per item:
(1) is het Spaans correct en natuurlijk, (2) klopt de Nederlandse vertaling, (3) klopt de uitleg,
(4) SLAAT DE ZIN ERGENS OP? Zou een mens dit op een gewone dag tegen een ander zeggen? Keur af als de
    zin grammaticaal klopt maar inhoudelijk onzin is. Voorbeelden die zijn doorgeglipt en dus af
    hadden gemoeten: "Las mesas son tímidas" (de tafels zijn verlegen), "Busco las casas" (ik zoek de
    huizen). Correct Spaans, maar niemand zegt dat.""",
"""  return `Je bent corrector Spaans (Spanje, niveau A2/B1) voor een leerapp. Controleer per item, in
deze volgorde:
(1) IS DEZE ZIN PRAKTISCH TOEPASBAAR? De leerling is een Nederlander van rond de veertig die Spaans
    leert om het te gebruiken: in een bar, op reis, bij de buren, op zijn werk, aan tafel, of in een
    gesprek over het leren zelf. Zou hij deze zin deze maand kunnen zeggen of horen? Zo niet: afkeuren,
    ook als er verder niets mis mee is. Voorbeelden die zijn doorgeglipt en dus af hadden gemoeten:
    "Las mesas son tímidas" (de tafels zijn verlegen), "Busco las casas" (ik zoek de huizen). Correct
    Spaans, maar niemand zegt dat. Deze vraag komt eerst: een zin die niemand zegt hoef je niet meer
    op zijn uitleg na te kijken.
(2) is het Spaans correct en natuurlijk, (3) klopt de Nederlandse vertaling, (4) klopt de uitleg.""")

# ---------------------------------------------------------------- controles
cur = CUR.read_text(encoding="utf-8")
assert "const BRUIKBAAR" in cur, "het blok ontbreekt"
assert cur.count("${BRUIKBAAR}") == 3, \
    "het blok staat niet in alle drie de schrijfopdrachten (%d)" % cur.count("${BRUIKBAAR}")
# en hij staat vóór de stijl-eisen: een volgorde die alleen in een commentaar staat, is geen volgorde
for naam in ["promptZinnenKaal", "promptZinnenVerschijnsel", "promptZinnenWoorden"]:
    i = cur.index("function " + naam + "(")
    blok = cur[i:cur.index("\n}\n", i)]
    assert "${BRUIKBAAR}" in blok, naam + " mist het blok"
    assert blok.index("${BRUIKBAAR}") < blok.index("${STIJL}"), \
        naam + ": de stijl-eisen staan vóór de bruikbaarheid"
# de tegenlezer stelt de vraag als eerste
tl = cur[cur.index("function promptTegenlezerZinnen("):]
tl = tl[:tl.index("\n}\n")]
assert "(1) IS DEZE ZIN PRAKTISCH TOEPASBAAR?" in tl, "de tegenlezer vraagt het niet als eerste"
assert tl.index("PRAKTISCH TOEPASBAAR") < tl.index("is het Spaans correct"), \
    "de grammatica staat nog vóór de bruikbaarheid"

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
