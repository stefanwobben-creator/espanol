#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.30: het alternatief bij s154 eruit, en een kijkertje om zo'n melding zelf na te lopen.

De alt-poort gaf een waarschuwing bij s154. Nagekeken, en hij heeft gelijk, alleen om een andere
reden dan bij s158.

  zin:      Todavía tenemos que hacer la compra antes de que cierre la tienda.
  uitleg:   Tenemos que hacer is de vaste constructie "we moeten doen". De subjuntivo cierre is
            nodig na antes de que.
  alt:      antes de que cierre la tienda nos falta hacer la compra

Dat alternatief is geen fout Spaans. Het is alleen geen antwoord op deze zin. De uitleg drilt twee
dingen, tener que en de subjuntivo na antes de que, en dit alternatief laat het eerste vallen. Wie
"nos falta" intikt krijgt goed te horen terwijl hij de constructie die geoefend wordt heeft omzeild.

Erbij: niemand die "We moeten nog boodschappen doen" vertaalt komt uit op "nos falta". Dit is geen
variant die een leerling toevallig typt, dus hij vangt niets af en kan alleen maar iets doorlaten.

Weg ermee. De accentloze variant blijft staan, want die vangt precies wat hij moet vangen: dezelfde
zin zonder accenten.

Ook nieuw: tools/zin.js. De alt-poort meldt een id, en dan wil je die zin kunnen zien zonder in
index.html te gaan zoeken. node tools/zin.js s154 en je hebt hem, met zijn les erbij.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_ZIN = os.path.join(WORTEL, "tools", "zin.js")
PAD_VER = os.path.join(WORTEL, "versie.txt")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "antes de que cierre la tienda nos falta hacer la compra" in src
DOE_ZIN = not os.path.exists(PAD_ZIN)

# "Niets te doen" en "hier valt niets te doen" zijn twee verschillende dingen, en die moet een patch
# uit elkaar houden. De eerste keer deed hij dat niet: op een index.html die s154 nog niet kende
# sloeg hij stil over, en dan denk je dat het gelukt is. Nu zegt hij waar het aan ligt.
if not DOE_APP and '"id":"s154"' not in src:
    print("Deze index.html kent s154 nog niet, dus je repo loopt achter op wat de nachtrun heeft\n"
          "gepusht. Eerst bijtrekken, dan pas patchen:\n\n    git pull --rebase\n")
    sys.exit(1)

if not DOE_APP and not DOE_ZIN:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(
        """"alt":["todavia tenemos que hacer la compra antes de que cierre la tienda","antes de que cierre la tienda nos falta hacer la compra"]""",
        """"alt":["todavia tenemos que hacer la compra antes de que cierre la tienda"]""")
    rep('var APP_VERSIE = "v23.29";', 'var APP_VERSIE = "v23.30";')
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    # versie.txt hoort in dezelfde beweging mee, anders staat de servicewerker op een oude versie te
    # wachten die nooit komt. pasToe doet dat zelf, een handpatch niet.
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write("v23.30\n")
    print("s154 opgeschoond in", PAD, "· versie.txt op v23.30")

ZIN = '''#!/usr/bin/env node
/* Een zin opzoeken op id. De alt-poort en de nachtrun melden ids, en dan wil je die zin kunnen zien
   zonder in een bestand van twee megabyte te gaan zoeken.

     node tools/zin.js s154
     node tools/zin.js s154 s158 w12 q-imperfecto

   Werkt op zinnen, woorden en toetsjes: het id zegt zelf al genoeg over waar hij hoort. */
const lib = require("./content-lib.js");
const inv = lib.inventaris();
const ids = process.argv.slice(2);

if (!ids.length) {
  console.log("gebruik: node tools/zin.js <id> [id...]   bijvoorbeeld: node tools/zin.js s154");
  process.exit(1);
}

function lesVan(id) {
  const l = (inv.perLes || []).find(x => (x.sents || []).includes(id) || (x.words || []).includes(id)
                                      || (x.quizzes || []).includes(id));
  return l ? l.id + " \\u00b7 " + l.titel : null;
}

let mis = 0;
ids.forEach(id => {
  const bak = ["sentences", "words", "quizzes"].find(k => (inv[k] || []).some(x => x.id === id));
  if (!bak) { console.log(id + ": niet gevonden"); mis++; return; }
  const item = inv[bak].find(x => x.id === id);
  console.log("== " + id + " (" + bak + (lesVan(id) ? ", " + lesVan(id) : "") + ") ==");
  console.log(JSON.stringify(item, null, 1));
  console.log("");
});
process.exit(mis ? 1 : 0);
'''

if DOE_ZIN:
    with io.open(PAD_ZIN, "w", encoding="utf-8") as f:
        f.write(ZIN)
    print("tools/zin.js aangemaakt")
