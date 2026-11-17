#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtwacht 2026-11-11: imperfecto, de vormen die Stefan als indefinido invult.

FOUTINPUT (tools/logs-latest.json van 10 nov, nieuwste log 9 nov 21:04, vergeleken
met de vorige snapshot a63f7ac en met wat er sinds 7 nov bijkwam):

  conj tener-2-imperfecto  "tenebas"     (moet: tenía)      nieuw op 8 nov
  conj dar-2-imperfecto    "dariá"       (moet: daba)       nieuw op 8 nov
  conj observar-1-imperf.  "observó"     (moet: observabas) 8 nov
  conj pedir-1-imperfecto  "pediste" x2  (moet: pedías)     7 nov
  conj salir-1-imperfecto  "saliste" x2  (moet: salías)     7 nov
  conj estudiar-1-imperf.  "estudiste"   (moet: estudiabas) 7 nov
  conj estar-4-imperfecto  "estuvisteis" (moet: estabais)   7 nov
  conj sentir-5-imperfecto "sentieron"   (moet: sentían)    7 nov

Het patroon: waar het imperfecto gevraagd wordt, pakt Stefan de indefinido-vorm
(-iste, -ó, -isteis, -ieron), vooral bij tú en bij -er/-ir-werkwoorden. De les
a2-9 ("Cómo cambian las cosas") heeft achttien imperfecto-zinnen, maar bijna
allemaal in yo/él/ellos en geen enkele met pedías, salías, estabais of sentían.
Deze zeven vullen precies dat gat, in context, zodat de vorm aan een signaal
(antes, siempre, de pequeño, cuando + achtergrond) vast komt te zitten.

NIET gedrild: costar en les2 (de avondrun drilt die al elke nacht), de losse
woordfouten van b1-17 (eerste kennismaking, geen cluster) en de Cervantes-woorden
(die draaien in het herhaalsysteem).

IDS: tools/nachtpatch.py op main heeft (nog) geen volgendeVrij() en er is geen
tools/ids.json. Daarom kiest deze patch zijn ids pas BIJ HET TOEPASSEN, en herkent
hij zijn eigen zinnen aan de Spaanse tekst in plaats van aan het id. Zo kan hij
gestapeld worden op wat de avondrun of een andere wachtrijpatch intussen uitdeelt,
en zegt hij bij een tweede run "stond er al".

GEBRUIK:  python3 claude/nachtwacht/2026-11-11.py [index.html]
"""
import io, os, re, sys, json

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "..", "tools"))
import nachtpatch as np

LES = "a2-9"
SPOOR = "a2"

ZINNEN = [
    {"lvl": 2,
     "nl": "Vroeger ging jij elke vrijdag uit, toch?",
     "en": "You used to go out every Friday, right?",
     "es": "Antes salías todos los viernes, ¿verdad?",
     "alt": ["antes salías todos los viernes, ¿verdad?", "antes salias todos los viernes verdad",
             "antes salías todos los viernes ¿no?", "antes salias todos los viernes no"],
     "uitleg": "Salir → salías (imperfecto, -ir: -ía, -ías, -ía). Jij schreef eerder 'saliste', maar dat is de indefinido: één keer, afgerond. Antes + todos los viernes = een gewoonte van vroeger, en een gewoonte is altijd imperfecto.",
     "ue": "Salir → salías (imperfecto, -ir: -ía, -ías, -ía). You wrote 'saliste' before, but that's the indefinido: once, finished. Antes + todos los viernes = a past habit, and a habit is always imperfecto."},
    {"lvl": 2,
     "nl": "In dat restaurant vroeg jij altijd om de rekening.",
     "en": "In that restaurant you always asked for the bill.",
     "es": "En ese restaurante siempre pedías la cuenta.",
     "alt": ["en ese restaurante siempre pedías la cuenta", "en ese restaurante siempre pedias la cuenta",
             "en ese restaurante tú siempre pedías la cuenta", "siempre pedías la cuenta en ese restaurante"],
     "uitleg": "Pedir → pedías. In het imperfecto is pedir gewoon regelmatig: geen e→i-wissel, die hoort bij het presente (pido) en de indefinido (pidió). 'Pediste' is indefinido. Siempre bij iets wat zich herhaalde = imperfecto.",
     "ue": "Pedir → pedías. In the imperfecto pedir is simply regular: no e→i change, that belongs to the present (pido) and the indefinido (pidió). 'Pediste' is indefinido. Siempre with something that kept happening = imperfecto."},
    {"lvl": 2,
     "nl": "Wat studeerde jij toen je in Madrid woonde?",
     "en": "What were you studying when you lived in Madrid?",
     "es": "¿Qué estudiabas cuando vivías en Madrid?",
     "alt": ["¿qué estudiabas cuando vivías en madrid?", "que estudiabas cuando vivias en madrid"],
     "uitleg": "Twee keer imperfecto, twee uitgangen: -ar krijgt -abas (estudiar → estudiabas), -er/-ir krijgt -ías (vivir → vivías). 'Estudiste' bestaat niet; de indefinido is estudiaste. Je vraagt naar een periode, niet naar één afgerond moment.",
     "ue": "Imperfecto twice, two endings: -ar gets -abas (estudiar → estudiabas), -er/-ir gets -ías (vivir → vivías). 'Estudiste' doesn't exist; the indefinido is estudiaste. You're asking about a period, not one finished moment."},
    {"lvl": 2,
     "nl": "Als kind gaf mijn opa me elke zondag een euro.",
     "en": "When I was a child, my grandfather gave me a euro every Sunday.",
     "es": "De pequeño, mi abuelo me daba un euro cada domingo.",
     "alt": ["de pequeño, mi abuelo me daba un euro cada domingo", "de pequeno mi abuelo me daba un euro cada domingo",
             "de pequeña, mi abuelo me daba un euro cada domingo", "de pequena mi abuelo me daba un euro cada domingo",
             "de pequeño, mi abuelo me daba un euro todos los domingos", "de pequeno mi abuelo me daba un euro todos los domingos"],
     "uitleg": "Dar → daba (helemaal regelmatig, -ar: -aba). 'Daría' met -ía is een andere tijd: de condicional, 'zou geven'. Dat -ía hoort alleen bij -er/-ir-werkwoorden in het imperfecto. Cada domingo = elke week weer, dus imperfecto.",
     "ue": "Dar → daba (fully regular, -ar: -aba). 'Daría' with -ía is a different tense: the conditional, 'would give'. That -ía only belongs to -er/-ir verbs in the imperfecto. Cada domingo = every week again, so imperfecto."},
    {"lvl": 2,
     "nl": "Mijn buurvrouw had vroeger drie katten.",
     "en": "My neighbour used to have three cats.",
     "es": "Mi vecina antes tenía tres gatos.",
     "alt": ["mi vecina antes tenía tres gatos", "mi vecina antes tenia tres gatos",
             "antes mi vecina tenía tres gatos", "antes mi vecina tenia tres gatos"],
     "uitleg": "Tener → tenía. Tener is een -er-werkwoord, dus -ía en nooit -aba ('tenebas' mengt de twee). Hij is in het imperfecto ook helemaal regelmatig: geen tuv- (dat is de indefinido: tuvo) en geen ie (dat is het presente: tiene).",
     "ue": "Tener → tenía. Tener is an -er verb, so -ía and never -aba ('tenebas' mixes the two). In the imperfecto it's completely regular too: no tuv- (that's the indefinido: tuvo) and no ie (that's the present: tiene)."},
    {"lvl": 2,
     "nl": "Toen ik jullie leerde kennen, zaten jullie nog op de universiteit.",
     "en": "When I met you, you were still at university.",
     "es": "Cuando os conocí, todavía estabais en la universidad.",
     "alt": ["cuando os conocí, todavía estabais en la universidad", "cuando os conoci todavia estabais en la universidad",
             "cuando os conocí, estabais todavía en la universidad", "cuando os conoci estabais todavia en la universidad",
             "cuando os conocí, aún estabais en la universidad", "cuando os conoci aun estabais en la universidad"],
     "uitleg": "Hier staan de twee tijden naast elkaar. Conocí = indefinido: het moment van kennismaken, afgerond. Estabais = imperfecto: de situatie op de achtergrond. Estar is in het imperfecto regelmatig (estaba, estabas, estaba, estábamos, estabais, estaban); 'estuvisteis' is de indefinido.",
     "ue": "Here the two tenses stand side by side. Conocí = indefinido: the moment of meeting, finished. Estabais = imperfecto: the background situation. Estar is regular in the imperfecto (estaba, estabas, estaba, estábamos, estabais, estaban); 'estuvisteis' is the indefinido."},
    {"lvl": 2,
     "nl": "In het dorp voelden mijn grootouders zich vaak alleen.",
     "en": "In the village my grandparents often felt lonely.",
     "es": "En el pueblo mis abuelos se sentían solos a menudo.",
     "alt": ["en el pueblo mis abuelos se sentían solos a menudo", "en el pueblo mis abuelos se sentian solos a menudo",
             "en el pueblo mis abuelos a menudo se sentían solos", "en el pueblo mis abuelos a menudo se sentian solos",
             "en el pueblo mis abuelos se sentían solos muchas veces", "en el pueblo mis abuelos se sentian solos muchas veces"],
     "uitleg": "Sentir → sentían (-ir: -ían). Een gevoel dat aanhield, met a menudo erbij, is imperfecto. 'Sentieron' bestaat niet: de indefinido is sintieron, met e→i. In het imperfecto blijft de stam gewoon sent-.",
     "ue": "Sentir → sentían (-ir: -ían). A feeling that lasted, with a menudo, is imperfecto. 'Sentieron' doesn't exist: the indefinido is sintieron, with e→i. In the imperfecto the stem simply stays sent-."},
]


def _volgendeVrij(src, prefix):
    """np.volgendeVrij als die er is; anders het eerste getal boven alles wat bekend is."""
    if hasattr(np, "volgendeVrij"):
        return np.volgendeVrij(src, prefix)
    bekend = [int(x) for x in re.findall(r'"' + prefix + r'(\d+)"', src)]
    # ook wat de avondrun beloofde maar (nog) niet in index.html staat telt als vergeven
    pad = os.path.join(HIER, "..", "..", "tools", "curriculum-laatste.json")
    try:
        bekend += [int(x) for x in re.findall(r'"' + prefix + r'(\d+)"', io.open(pad, encoding="utf-8").read())]
    except IOError:
        pass
    return prefix + str(max(bekend + [0]) + 1)


def _zinMetEs(src, es):
    tekst = np.arrayTekst(src, "SENTENCES")
    m = re.search(r'\{"id":"([^"]+)"[^{}]*"es":' + re.escape(json.dumps(es, ensure_ascii=False)), tekst)
    return m.group(1) if m else None


def pas(src):
    nieuw, al = [], []
    for z in ZINNEN:
        bestaand = _zinMetEs(src, z["es"])
        if bestaand:
            al.append(bestaand)
            continue
        zid = _volgendeVrij(src, "s")
        item = {"id": zid}
        item.update(z)
        item["tag"] = "imperfecto"
        src = np.zinToevoegen(src, "SENTENCES", json.dumps(item, ensure_ascii=False, separators=(",", ":")))
        assert _zinMetEs(src, z["es"]) == zid, "zin " + zid + " landde niet"
        nieuw.append(zid)
    alle = [_zinMetEs(src, z["es"]) for z in ZINNEN]
    src = np.lesKoppelen(src, LES, alle)
    if nieuw:
        src = np.batchOphogen(src, SPOOR)
    np.keuring(src)
    return src, nieuw, al


if __name__ == "__main__":
    pad = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    src = np.laad(pad)
    uit, nieuw, al = pas(src)
    if nieuw:
        np.bewaar(pad, uit)
        print("toegevoegd aan %s: %s (batch %s)" % (LES, ", ".join(nieuw), np.batchNu(uit, SPOOR)))
    if al:
        print("stond er al: " + ", ".join(al))
    if not nieuw and uit != src:
        np.bewaar(pad, uit)
        print("alleen de leskoppeling bijgewerkt")
