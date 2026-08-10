#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Waarom er al twee nachten nul toetsjes doorheen komen, en waarom een hele B1-les daaraan meeging.

Uit de hartslag van 10 aug, drie klachten op een rij:

  toetsje afgekeurd (poging 1): Vraag 2: Optie 'vivíamos' komt twee keer voor...
  toetsje afgekeurd (poging 2): Vraag 1: Optie 0 en 1 zijn identiek ('vivíamos'); Vraag 2: idem
    ('pasabas'); Vraag 4: idem ('corría'); Vraag 6: idem ('decía'); Vraag 7: idem ('veíamos');
    Vraag 8: idem ('estudiabas')
  toetsje van de nieuwe les afgekeurd

Twee dingen kloppen daar niet aan de aanpak, los van wat het model uitspookt.

Ten eerste: een dubbele optie is geen inhoudelijke fout maar een mechanische. We vragen nu een
taalmodel om hem te herstellen, en dat werkte averechts: poging 1 had één dubbele optie, poging 2 had
er zes. Dat is ook logisch. Het model leest "optie 0 en 1 zijn identiek" en gaat vormen zitten
poetsen, terwijl je gewoon de tweede kopie kunt weghalen. valideer() in content-lib.js keurt dubbele
opties trouwens sowieso af, dus zelfs een tevreden tegenlezer had het niet gered.

Dus: eerst zelf opschonen, dan pas voorleggen. De dubbele optie eruit, de c-index verschuift mee naar
de kopie die blijft staan, en een vraag met minder dan drie opties over valt weg. Blijven er minder
dan vier vragen over, dan is het toetsje het niet waard en gaat het alsnog terug naar het model.

Opschonen op exacte tekst, niet accentloos. Twee opties die alleen in een accent verschillen zijn
hier een geldige vraag (comia tegenover comía is precies wat je wilt toetsen), en dat zou je met een
accentloze vergelijking kapotmaken.

Ten tweede: een afgekeurd toetsje sloopte de hele nieuwe les. Veertien woorden, acht zinnen en een
spiekkaart naar de prullenbak omdat het toetsje niet deugde. Dat is dezelfde alles-of-nietsfout die
twee regels erboven al voor de zinnen is opgelost, met dezelfde reden erbij geschreven. Nu gaat de
les door zonder toetsje. De lesindeling kon dat al aan (quizzes: les.quiz ? [...] : []), en de les
gaat als pull request, dus jij ziet hem toch nog.

Idempotent. Tooling, dus geen APP_VERSIE.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "tools", "curriculum.js")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function schoonToets" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ------------------------------------------------------------------ 1. de opschoner
rep(
    """async function maakToets(gat, inv, motor) {""",
    """/* Dubbele opties zijn mechanisch, dus repareren we ze mechanisch. Zie de kop van
   patch-toetspoort.py: het model erop aanspreken maakte het twee nachten op rij erger.

   Exacte tekst, niet accentloos: comia tegenover comía is hier een geldige vraag en die moet blijven
   kunnen. c verschuift mee naar de kopie die blijft staan, want anders wijst het juiste antwoord na
   het opschonen naar de verkeerde optie, en dat is erger dan het probleem dat we oplossen. */
function schoonToets(qz) {
  const gemeld = [];
  const vragen = ((qz && qz.vragen) || []).map((v, i) => {
    if (!Array.isArray(v.opts)) return v;
    const houd = [], heen = [];
    v.opts.forEach(o => {
      const al = houd.indexOf(String(o));
      if (al === -1) { heen.push(houd.length); houd.push(String(o)); } else heen.push(al);
    });
    if (houd.length === v.opts.length) return v;
    /* Alleen wegstrepen wat door het opschonen te mager wordt. Een vraag die zelf al met twee opties
       kwam blijft staan: die is niet stuk, en valideer() laat er twee toe. */
    if (houd.length < 3) { gemeld.push(`vraag ${i + 1}: te weinig opties over, valt weg`); return null; }
    gemeld.push(`vraag ${i + 1}: ${v.opts.length - houd.length} dubbele optie weg`);
    const c = typeof v.c === "number" && heen[v.c] !== undefined ? heen[v.c] : v.c;
    return Object.assign({}, v, { opts: houd, c });
  }).filter(Boolean);
  return { qz: Object.assign({}, qz, { vragen }), gemeld };
}

async function maakToets(gat, inv, motor) {""")

# ------------------------------------------------------------------ 2. opschonen voor de tegenlezer
rep(
    """    qz.id = id; qz.spiek = gat.spiek;
    const uit = await vraagModel(motor, promptTegenlezerToets(qz), 2000);
    if (uit && uit.ok === true) return qz;""",
    """    qz.id = id; qz.spiek = gat.spiek;
    const schoon = schoonToets(qz);
    if (schoon.gemeld.length) console.log("    opgeschoond: " + schoon.gemeld.join("; "));
    if (schoon.qz.vragen.length < 4) {
      console.error(`    te weinig vragen over na opschonen (poging ${poging})`);
      bezwaren = ["te veel vragen hadden dubbele opties; geef per vraag vier verschillende opties"];
      continue;
    }
    const uit = await vraagModel(motor, promptTegenlezerToets(schoon.qz), 2000);
    if (uit && uit.ok === true) return schoon.qz;""")

# ------------------------------------------------------------------ 3. de nieuwe les overleeft het
rep(
    """    if (les.quiz) {
      const uit = await vraagModel(motor, promptTegenlezerToets(les.quiz), 2000);
      if (!uit || uit.ok !== true) { console.error("    toetsje van de nieuwe les afgekeurd"); return null; }
    }""",
    """    if (les.quiz) {
      const schoon = schoonToets(les.quiz);
      if (schoon.gemeld.length) console.log("    toetsje opgeschoond: " + schoon.gemeld.join("; "));
      les.quiz = schoon.qz.vragen.length >= 4 ? schoon.qz : null;
      /* Zelfde reden als bij de zinnen hierboven: alles of niets was te streng. Een afgekeurd
         toetsje kostte tot nu toe de hele les, veertien woorden en acht zinnen erbij. De
         lesindeling kan een les zonder toetsje aan, en jij leest de pull request toch na. */
      if (les.quiz) {
        const uit = await vraagModel(motor, promptTegenlezerToets(les.quiz), 2000);
        if (!uit || uit.ok !== true) {
          console.error("    toetsje van de nieuwe les afgekeurd, de les gaat door zonder");
          les.quiz = null;
        }
      }
    }""")

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("toetspoort toegevoegd aan", PAD)
