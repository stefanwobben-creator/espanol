#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtpatch 25 nov - vijf B1-drillzinnen bij b1-19 (La vida en pareja) op Stefans verse fouten.

WAT HIER IN ZIT

Diff van de cumulatieve foutenmap tussen logsnapshot 3096174 (laatste Stefan-dagdoel
21 nov 21:00) en 9b7c1d9 (dagdoel 23 nov 21:19). Gegroeid in de relatiewoorden van
b1-19, en in geen enkele oefenzin van die les gebruikt (s457-s464 noemen ze niet):

  el noviazgo        (w423)  1 -> 8
  la convivencia     (w416)  2 -> 8
  el compromiso      (w418, 'de verplichting')  2 -> 7
  el compromiso      (w424, 'de verloving')     0 -> 3
  la reconciliación  (w422)  1 -> 4

Compromiso staat twee keer in de woordenlijst met twee betekenissen. Los geleerd is
dat een gok; alleen in een zin is te zien welke bedoeld is. Daarom twee zinnen, een
per betekenis, die naar elkaar verwijzen.

Bewust NIET gedrild:
  - sábana/lejía/colchón (cv1166/1169/1171): groeien door, maar zitten al in de
    wachtrijpatch van 23 nov (tak claude/magical-faraday-ojncbn), nog niet live.
  - overige cv-woorden (esguince, estirar, hinchado, ...): Cervantes-leesplank, daar
    blijft de nachtrun af.
  - les2/comparativos: daar claimt de avondrun reparatiezinnen voor (zie logboek).
  - s222 (les5): een keer 'un momento' weggelaten, geen patroon.
  - geldwoorden w427-w439: elk 0 -> 1 of 2, eerste kennismaking.

LES: b1-19 is een nieuweLessen-les. EXTRA_CONTENT.lessen wordt in pasExtraContentToe()
toegepast VOOR de nieuweLessen worden aangehangen, dus np.lesKoppelen("b1-19") zou
stil niets doen. Daarom gaat de koppeling hier via np.extraLees/np.extraSchrijf
rechtstreeks in de sents van de les zelf.

IDS: np.volgendeVrij en tools/ids.json bestaan (nog) niet in de repo. Dit script kiest
ids bij het toepassen: hoogste s-id in index.html, in tools/curriculum-laatste.json
(beloofd, ook als het nooit geplaatst is) en in audio/dictado (een mp3 bij een id dat
niet bestaat mag niet aan een andere zin komen te hangen), plus 1. Idempotent op de
Spaanse zin: tweede keer draaien zegt "stond er al".

Het versienummer wordt hier niet aangeraakt.

    python3 claude/nachtwacht/2026-11-25.py
"""
import io, json, os, re, sys
HIER = os.path.dirname(os.path.abspath(__file__))
WORTEL = os.path.join(HIER, "..", "..")
sys.path.insert(0, os.path.join(WORTEL, "tools"))
import nachtpatch as np

PAD = os.path.join(WORTEL, "index.html")
BELOFTE = os.path.join(WORTEL, "tools", "curriculum-laatste.json")
DICTADO = os.path.join(WORTEL, "audio", "dictado")
LES = "b1-19"

ZINNEN = [
 {"lvl": 2,
  "nl": "Na drie jaar verkering besloten ze te trouwen.",
  "en": "After three years of going out together, they decided to get married.",
  "es": "Después de tres años de noviazgo, decidieron casarse.",
  "alt": ["despues de tres anos de noviazgo decidieron casarse",
          "tras tres años de noviazgo decidieron casarse",
          "después de tres años de noviazgo se decidieron a casarse"],
  "uitleg": "El noviazgo = de verkering, de periode dat je iemands novio of novia bent. Acht keer mis en het woord kwam in geen enkele zin voor, dus hier staat het in zijn natuurlijke omgeving: tres años de noviazgo, net als in het Nederlands 'drie jaar verkering', zonder lidwoord na de. Het is mannelijk (el noviazgo, -azgo is altijd mannelijk, net als el liderazgo). Ezelsbrug: novio + -azgo. Decidieron is de pretérito van decidir, want het is een afgerond besluit op een moment.",
  "ue": "El noviazgo = the courtship, the period when you are someone's novio or novia. Eight misses and the word appeared in no sentence at all, so here it is in its natural setting: tres años de noviazgo, without an article after de. It is masculine (el noviazgo; -azgo is always masculine, like el liderazgo). Memory hook: novio + -azgo. Decidieron is the preterite of decidir, a completed decision at one moment.",
  "tag": "relatie"},
 {"lvl": 2,
  "nl": "Mijn zus heeft haar verloving een maand voor de bruiloft verbroken.",
  "en": "My sister broke off her engagement a month before the wedding.",
  "es": "Mi hermana rompió su compromiso un mes antes de la boda.",
  "alt": ["mi hermana rompio su compromiso un mes antes de la boda",
          "mi hermana ha roto su compromiso un mes antes de la boda"],
  "uitleg": "El compromiso heeft twee betekenissen en jij kreeg ze allebei als losse kaart: de verloving (deze zin) en de verplichting (de volgende). Los is dat een gok; in een zin beslist de context. Hier: romper el compromiso = de verloving verbreken, en het anillo de compromiso is de verlovingsring. Rompió is pretérito van romper; met ha roto is het ook goed. Let op su compromiso: su, niet suyo, voor het zelfstandig naamwoord.",
  "ue": "El compromiso has two meanings and you got both as separate cards: the engagement (this sentence) and the commitment (the next one). On its own that is a guess; in a sentence the context decides. Here: romper el compromiso = to break off the engagement, and the anillo de compromiso is the engagement ring. Rompió is the preterite of romper; ha roto is also fine. Note su compromiso: su, not suyo, before the noun.",
  "tag": "relatie"},
 {"lvl": 2,
  "nl": "Een kind krijgen is een verplichting voor het hele leven.",
  "en": "Having a child is a commitment for life.",
  "es": "Tener un hijo es un compromiso para toda la vida.",
  "alt": ["tener un hijo es un compromiso para toda la vida",
          "tener hijos es un compromiso para toda la vida",
          "tener un hijo es un compromiso de por vida"],
  "uitleg": "Hetzelfde woord als in de vorige zin, nu met de betekenis verplichting of toewijding: iets waar je je aan bindt. Zie je geen bruiloft of ring in de buurt, dan is het bijna altijd deze. Valkuil voor Nederlanders: ons 'compromis' (elkaar halverwege tegemoetkomen) is in het Spaans meestal un acuerdo of un término medio. Para toda la vida = voor het hele leven; toda staat voor la vida, net als todo el día.",
  "ue": "The same word as in the previous sentence, now meaning commitment or obligation: something you bind yourself to. If there is no wedding or ring nearby, it is almost always this one. Trap for Dutch and English speakers: a 'compromise' (meeting halfway) is usually un acuerdo or un término medio in Spanish. Para toda la vida = for life; toda comes before la vida, just like todo el día.",
  "tag": "relatie"},
 {"lvl": 2,
  "nl": "Het samenwonen met mijn partner gaat makkelijk, want we zijn allebei netjes.",
  "en": "Living together with my partner is easy, because we are both tidy.",
  "es": "La convivencia con mi pareja es fácil porque los dos somos ordenados.",
  "alt": ["la convivencia con mi pareja es facil porque los dos somos ordenados",
          "la convivencia con mi pareja es fácil porque ambos somos ordenados"],
  "uitleg": "La convivencia = het samenwonen, acht keer mis. Het komt van convivir: con + vivir, samen leven. Woorden op -encia zijn altijd vrouwelijk (la convivencia, la paciencia, la experiencia), dus es fácil zonder -a-gedoe maar wel la ervoor. Waar het Nederlands een werkwoord als zelfstandig naamwoord gebruikt (het samenwonen), heeft het Spaans vaak een eigen woord. Los dos somos = we zijn allebei; ordenados met -os omdat los dos mannelijk of gemengd is.",
  "ue": "La convivencia = living together, eight misses. It comes from convivir: con + vivir, to live together. Words ending in -encia are always feminine (la convivencia, la paciencia, la experiencia). Where Dutch and English turn a verb into a noun (living together), Spanish often has a word of its own. Los dos somos = we are both; ordenados with -os because los dos is masculine or mixed.",
  "tag": "samenwonen"},
 {"lvl": 2,
  "nl": "Na twee maanden uit elkaar kwam eindelijk de verzoening.",
  "en": "After two months apart, the reconciliation finally came.",
  "es": "Después de dos meses separados, por fin llegó la reconciliación.",
  "alt": ["despues de dos meses separados por fin llego la reconciliacion",
          "tras dos meses separados por fin llegó la reconciliación",
          "después de dos meses separados la reconciliación llegó por fin"],
  "uitleg": "La reconciliación = de verzoening, het zelfstandig naamwoord bij reconciliarse dat je uit s462 kent (nos hemos reconciliado). Woorden op -ción zijn altijd vrouwelijk, met de klemtoon op de ó. In het meervoud valt dat accent weg: las reconciliaciones. Separados = uit elkaar, een voltooid deelwoord dat hier als bijvoeglijk naamwoord werkt; daarom de -os, want het slaat op twee mensen. Llegó: pretérito, een moment dat het gebeurde.",
  "ue": "La reconciliación = the reconciliation, the noun that goes with reconciliarse from s462 (nos hemos reconciliado). Words ending in -ción are always feminine, stressed on the ó. In the plural the accent disappears: las reconciliaciones. Separados = apart, a past participle used as an adjective; hence -os, since it refers to two people. Llegó: preterite, a single moment when it happened.",
  "tag": "relatie"},
]


def _num(x):
    m = re.match(r"^s(\d+)$", x)
    return int(m.group(1)) if m else 0


def _hoogste(src):
    hoog = 0
    for naam in ["SENTENCES", "B_SENTENCES"]:
        for x in np.ids(src, naam):
            hoog = max(hoog, _num(x))
    try:
        b = json.load(io.open(BELOFTE, encoding="utf-8"))
        beloofd = (b.get("reparatie") or {}).get("zinnen", []) + (b.get("nieuweLes") or {}).get("sents", [])
        for x in beloofd:
            hoog = max(hoog, _num(x))
    except (IOError, ValueError):
        pass
    if os.path.isdir(DICTADO):
        for f in os.listdir(DICTADO):
            hoog = max(hoog, _num(f.rsplit(".", 1)[0]))
    return hoog


def _bestaatAl(src, es):
    return json.dumps(es, ensure_ascii=False) in np.arrayTekst(src, "SENTENCES")


def _koppel(src, zid):
    d = np.extraLees(src)
    lessen = [l for l in d.get("nieuweLessen", []) if l.get("id") == LES]
    assert len(lessen) == 1, "les %s niet (eenduidig) gevonden in nieuweLessen" % LES
    if zid not in lessen[0]["sents"]:
        lessen[0]["sents"].append(zid)
    return np.extraSchrijf(src, d)


def main():
    src = np.laad(PAD)
    nieuw = []
    for z in ZINNEN:
        if _bestaatAl(src, z["es"]):
            continue
        zid = "s%d" % (_hoogste(src) + 1)
        item = dict([("id", zid)] + list(z.items()))
        src = np.zinToevoegen(src, "SENTENCES", json.dumps(item, ensure_ascii=False))
        src = _koppel(src, zid)
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
