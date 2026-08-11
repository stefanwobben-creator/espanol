#!/usr/bin/env python3
# De nachtrun kiest voortaan het gat dat er het meest toe doet, en maakt niets als er al genoeg ligt.
#
# Twee dingen gevonden bij het nakijken van vanmorgen (node tools/curriculum.js --analyse):
#
# 1. De code deed het omgekeerde van wat er in het commentaar staat. Boven de sortering in main()
#    staat: "verschijnselen wegen zwaarder dan losse woorden omdat een regel die je niet snapt
#    tientallen items blijft besmetten." Maar de twee soorten gaten kregen hun score uit twee
#    verschillende sommen: een verschijnsel uit fouten gedeeld door beschikbare oefenzinnen, een
#    woordgat uit fouten gedeeld door aantal woorden. Die getallen staan niet op dezelfde schaal, en
#    de woordgaten kwamen er stelselmatig bovenop. Uitkomst vanmorgen: de run pakte les3 en les5
#    (woorden) aan, terwijl sentirse 20 fouten had op 6 oefenzinnen en costar 16 op 5. Precies de
#    regels waarvan het commentaar zegt dat ze voorgaan.
#
#    Nu worden de verschijnselen eerst gesorteerd en daarna pas de woordgaten. Botter dan één
#    formule, maar wel precies wat het commentaar altijd al beloofde. Op hetzelfde log van vanmorgen
#    kiest de run nu sentirse en costar in plaats van les3 en les5. En de deling is gedempt: delen
#    door het aantal oefenzinnen geeft uitschieters zodra dat aantal klein is (posesivos, 3 fouten op
#    1 zin, stond boven indefinido met 17 op 6).
#
# 2. Er was geen enkele rem op "hier ligt al genoeg". Stefan, 11 aug: "iedereen die daarna komt kan
#    veel content hergebruiken, dan is het voor de LLM minder produceren en meer koppelen." Dit is de
#    kleinste versie daarvan: een onderwerp met minstens tien oefenzinnen en minstens drie zinnen per
#    verse fout wordt overgeslagen. Dan is er geen tekort aan materiaal maar aan herhaling, en nog
#    meer zinnen maken is het verkeerde medicijn: het maakt de gedeelde bak groter voor iedereen
#    terwijl de leerling wat er ligt nog niet gedaan heeft.
#
#    Vandaag springt die rem nog nergens aan (het volste onderwerp haalt zes zinnen). Dat is goed:
#    hij hoort er te staan vóór hij nodig is, want daarna is de bak al gegroeid.
import pathlib, sys

CUR = pathlib.Path.home() / "espanol" / "tools" / "curriculum.js"
src = CUR.read_text(encoding="utf-8")

if "VERZADIGD_ZINNEN" in src:
    print("  curriculum.js staat al bij")
    sys.exit(0)

def rep(anker, nieuw, n=1):
    global src
    aantal = src.count(anker)
    assert aantal == n, "anker %d keer gevonden, verwacht %d: %r" % (aantal, n, anker[:80])
    src = src.replace(anker, nieuw, n)

rep("""function analyseer(logboek, inv) {""",
    """/* Wanneer is een onderwerp verzadigd? Als er al ruim materiaal ligt én er ruim materiaal is per
   verse fout. Twee eisen, want één is te grof: een onderwerp met twee zinnen en één fout haalt de
   verhouding wel maar heeft alsnog te weinig om mee te oefenen. */
const VERZADIGD_ZINNEN = 10;      // zoveel oefenzinnen liggen er al
const VERZADIGD_PER_FOUT = 3;     // en zoveel per verse fout
/* Delen door het aantal oefenzinnen geeft rare uitschieters zodra dat aantal klein is: een
   onderwerp met één zin en drie fouten kwam boven een onderwerp met zes zinnen en zeventien fouten.
   Vandaar een demping in de noemer. Twee is geen magisch getal, het is "doe alsof er altijd al een
   paar zinnen liggen", en dat haalt de scherpste rand van de deling af. */
const DEMPING = 2;

function verzadigd(g) {
  return g.zinnen >= VERZADIGD_ZINNEN && g.zinnen / Math.max(1, g.fouten) >= VERZADIGD_PER_FOUT;
}

function analyseer(logboek, inv) {""")

# de twee scores op dezelfde schaal
rep("""      const zinnen = zinnenPerTag[g.sleutel] || 0;
      return { soort: "verschijnsel", tag: g.sleutel, fouten: g.fouten, items: g.items.length,
               zinnen, score: g.fouten / Math.max(1, zinnen) };
    })""",
    """      const zinnen = zinnenPerTag[g.sleutel] || 0;
      return { soort: "verschijnsel", tag: g.sleutel, fouten: g.fouten, items: g.items.length,
               zinnen, score: g.fouten / (zinnen + DEMPING) };
    })""")

# verzadigde onderwerpen eruit, maar wel zichtbaar
rep("""  return { zinGaten, woordGaten, toetsGaten };""",
    """  /* Eerst kijken of er al genoeg ligt, dan pas maken. De overgeslagen onderwerpen blijven wel in
     het rapport staan: "er is niets te doen" en "hier lag al genoeg" zijn niet hetzelfde, en dat
     verschil hoort zichtbaar te zijn. */
  const vol = zinGaten.filter(verzadigd).concat(woordGaten.filter(verzadigd));
  return { zinGaten: zinGaten.filter(g => !verzadigd(g)),
           woordGaten: woordGaten.filter(g => !verzadigd(g)),
           toetsGaten, verzadigd: vol };""")

# en in het rapport
rep("""  toon("grammatica-toetsjes", an.toetsGaten, g => `${g.tag} (${g.titel}): ${g.fouten} fouten · spiekkaart ${JSON.stringify(g.spiek)}`);
}""",
    """  toon("grammatica-toetsjes", an.toetsGaten, g => `${g.tag} (${g.titel}): ${g.fouten} fouten · spiekkaart ${JSON.stringify(g.spiek)}`);
  if ((an.verzadigd || []).length) {
    console.log("  overgeslagen, hier ligt al genoeg:");
    an.verzadigd.forEach(g => console.log(
      `    ${g.tag}: ${g.fouten} fouten · ${g.zinnen} oefenzinnen · dat is ` +
      `${(g.zinnen / Math.max(1, g.fouten)).toFixed(1)} zin per fout, dus herhalen en niet bijmaken`));
  }
}""")

rep("""  // gaten op één stapel, zwaarste eerst; verschijnselen wegen zwaarder dan losse woorden omdat een
  // regel die je niet snapt tientallen items blijft besmetten
  const gaten = [].concat(an.zinGaten, an.woordGaten).sort((a, b) => b.score - a.score);""",
    """  /* Gaten op één stapel, verschijnselen eerst. Een regel die je niet snapt blijft tientallen items
     besmetten, een woord dat je mist is één woord; bovendien komen die woorden hoe dan ook terug via
     de herhaling, en een verschijnsel heeft geen tweede kanaal.

     Dit stond tot 11 aug wel in dit commentaar maar niet in de code: de twee soorten werden op één
     hoop gegooid en op score gesorteerd, terwijl hun scores uit twee verschillende sommen komen en
     dus niet op dezelfde schaal staan. De woordgaten wonnen daardoor stelselmatig. Uitkomst van
     11 aug: de run pakte les3 en les5 aan terwijl sentirse 20 fouten had op 6 oefenzinnen. Sorteren
     op soort en pas daarbinnen op score is botter dan één formule, maar het is wél wat er staat. */
  const gaten = [].concat(
    an.zinGaten.slice().sort((a, b) => b.score - a.score),
    an.woordGaten.slice().sort((a, b) => b.score - a.score));""")

CUR.write_text(src, encoding="utf-8")
print("  curriculum.js: verschijnselen eerst, demping op de deling, en verzadigde onderwerpen overgeslagen")
print("\nklaar. Kijk met:  node tools/curriculum.js --analyse")
