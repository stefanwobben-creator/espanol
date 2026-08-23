#!/usr/bin/env python3
# v23.178 (alleen gereedschap) - waarom de avondrun zo vaak misgaat, en wat eraan gedaan is
#
# Stefan, 23 aug: "kijk maar de avondrun doet het heel vaak niet goed. hoe kan dit?"
#
# EERST GETELD, EN DAT KAN, WANT DE HARTSLAG STAAT IN GIT
#
# Elke nacht committeert de run tools/avondrun-hart.json. Achttien nachten terugkijken geeft:
#
#   rood op 8, 9, 14, 20, 21, 22 en 23 augustus; groen op de rest.
#
# Zeven mislukte nachten, en de redenen zien er verschillend uit. Maar ze zijn het niet.
#
#   8 aug   het besluit vroeg om 4 stukken werk en er is niets van weggeschreven
#   9 aug   "alt bevat het eigen antwoord niet" op 2 zinnen -> hele levering weg
#   14 aug  de poort ging dicht op wat de bot schreef
#   20 aug  "lvl moet 1-5 zijn" op 3 van de 4 zinnen -> hele levering weg
#   21 aug  ReferenceError: oud is not defined
#   22 aug  ReferenceError: oud is not defined
#   23 aug  "uitleg legt niets uit" + "una vez" op 2 van de 10 -> hele levering weg
#
# EEN OORZAAK, DRIE AANLEIDINGEN
#
# De run is één lange ketting: gaten dichten, kale zinnen, toetsje, wegschrijven, nieuwe les. Wat er
# ook misgaat, waar dan ook, alles wat er tot dan toe gemaakt is gaat mee de prullenbak in. Dat is
# waarom zeven nachten met vijf verschillende oorzaken allemaal op precies hetzelfde uitkomen:
# geleverd null.
#
# v23.177 heeft daar de eerste helft van gerepareerd: één slechte zin gooit niet meer de hele
# levering weg. Dit is de tweede helft: één klappende stap gooit niet meer de hele nacht weg.
#
# WAT HIER IN GAAT
#
# A. DE ECHTE FOUT VAN 21 EN 22 AUGUSTUS. In maakToets() staat `if (oud && ...)`, maar `oud` is nooit
#    in die functie gedeclareerd; hij hoort bij promptToets(), veertig regels hoger. Dus zodra de
#    corrector iets afkeurde en de ijking begon, klapte de run op een ReferenceError. Twee nachten.
#
#    Die tak wordt alleen geraakt als de corrector iets afkeurt én er al een toetsje met die tag in
#    de app staat, en dat is precies waarom hij twee weken kon blijven staan zonder op te vallen.
#    node --check ziet dit niet: het is geldige JavaScript, alleen niet uitvoerbaar.
#
# B. ELKE STAP IN ZIJN EIGEN VANGNET. De vier productiestappen krijgen elk een try/catch. Klapt er
#    één, dan gaat de rest gewoon door en staat er 's ochtends wél iets. De klacht komt in de
#    hartslag, dus je ziet het nog steeds; je verliest alleen niet meer de hele nacht.
#
#    Dit is nadrukkelijk geen fouten wegmoffelen. Klapt alles, dan is er niets geleverd, en dan slaat
#    de bestaande belofte-controle aan het eind van main() alsnog toe en is de nacht rood.
#
# C. DE FOUTMELDING DIE NIETS ZEI. De schermafdruk van vanochtend: "De avondrun heeft niets
#    gepubliceerd ()." Die lege haakjes horen `wat` te bevatten. avondrun.sh draait met `set -e`, dus
#    zodra curriculum.js met 1 eindigt springt het script eruit vóórdat het ooit een `wat` schrijft.
#    Wie 's ochtends kijkt krijgt dus de mededeling dat er iets mis is, zonder wát. Nu schrijft het
#    script `wat=geklapt` en de exitcode erbij.
#
# D. DE HARTSLAG DIE IK ZELF HEB OVERSCHREVEN. Mijn zelftest van v23.177 schreef één keer een lege
#    hartslag, en die is meegecommit. Daarmee heb ik het verslag van run #25 gewist: precies het
#    bestand waaruit ik hierboven de geschiedenis heb geteld. De echte staat komt terug.
import json, pathlib, subprocess

W = pathlib.Path(__file__).resolve().parents[1]
CUR = W / "tools" / "curriculum.js"
SH = W / "tools" / "avondrun.sh"
HART = W / "tools" / "avondrun-hart.json"

cur = CUR.read_text(encoding="utf-8")
sh = SH.read_text(encoding="utf-8")

DOE_CUR = "const oud = inv.quizzes.find(q => q.id === gat.tag);\n  let bezwaren" not in cur
DOE_SH = "wat=geklapt" not in sh

def rep(bron, anker, nieuw, n=1):
    c = bron.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    return bron.replace(anker, nieuw, n)

# ---------------------------------------------------------------- A. de ReferenceError
if DOE_CUR:
    cur = rep(cur,
        '  const kaart = inv.cheat[gat.spiek[0]]\n'
        '    ? String(inv.cheat[gat.spiek[0]].html).replace(/<[^>]+>/g, " ").replace(/\\s+/g, " ").slice(0, 1200)\n'
        '    : "";\n'
        '  let bezwaren = null;',
        '  const kaart = inv.cheat[gat.spiek[0]]\n'
        '    ? String(inv.cheat[gat.spiek[0]].html).replace(/<[^>]+>/g, " ").replace(/\\s+/g, " ").slice(0, 1200)\n'
        '    : "";\n'
        '  /* v23.178: hier stond niets, en veertig regels lager werd `oud` gebruikt om de corrector op\n'
        '     te ijken. `oud` hoorde bij promptToets(), een andere functie. Twee nachten (21 en 22\n'
        '     augustus) klapte de run daarop met "oud is not defined", en omdat alles in één ketting\n'
        '     zat ging de hele nacht mee. De tak wordt alleen geraakt als de corrector iets afkeurt én\n'
        '     er al een toetsje met deze tag bestaat, en daarom kon hij zo lang blijven staan.\n'
        '     node --check ziet dit niet: het is geldige JavaScript, alleen niet uitvoerbaar. */\n'
        '  const oud = inv.quizzes.find(q => q.id === gat.tag);\n'
        '  let bezwaren = null;')

# ---------------------------------------------------------------- B. elke stap in zijn eigen vangnet
if DOE_CUR:
    # de gatenlus
    cur = rep(cur,
        '  for (const gat of gaten.slice(0, OPT.max)) {\n'
        '    const aantal = gat.soort === "woorden"',
        '  /* v23.178: elke productiestap krijgt zijn eigen vangnet. De run was één lange ketting, dus\n'
        '     een klapper in stap drie gooide ook weg wat stap één en twee al gemaakt hadden. Dat is de\n'
        '     gemeenschappelijke oorzaak onder zeven mislukte nachten met vijf verschillende directe\n'
        '     aanleidingen. Niets wordt hier weggemoffeld: de klacht gaat naar stderr en dus in de\n'
        '     hartslag, en levert alles niets op, dan slaat de belofte-controle aan het eind alsnog toe. */\n'
        '  for (const gat of gaten.slice(0, OPT.max)) {\n'
        '   try {\n'
        '    const aantal = gat.soort === "woorden"')
    cur = rep(cur,
        '    console.log(`    ${goed.length} zinnen goedgekeurd → les ${lesId}`);\n'
        '  }',
        '    console.log(`    ${goed.length} zinnen goedgekeurd → les ${lesId}`);\n'
        '   } catch (e) { console.error(`    ${gat.tag} klapte: ${e && e.message}; de rest van de nacht gaat door`); }\n'
        '  }')

    # de kale stap
    cur = rep(cur,
        '  if (kaal.length) {\n'
        '    const gat = kaal[0];\n'
        '    const n = Math.min(KAAL_PER_NACHT, gat.tekort);',
        '  if (kaal.length) try {\n'
        '    const gat = kaal[0];\n'
        '    const n = Math.min(KAAL_PER_NACHT, gat.tekort);')
    cur = rep(cur,
        '      console.log(`    ${goed.length} kale zinnen goedgekeurd (${gat.heeft} + ${goed.length} van de ${KAAL_DOEL})`);\n'
        '    }\n'
        '  }',
        '      console.log(`    ${goed.length} kale zinnen goedgekeurd (${gat.heeft} + ${goed.length} van de ${KAAL_DOEL})`);\n'
        '    }\n'
        '  } catch (e) { console.error(`    de kale zinnen klapten: ${e && e.message}; de rest van de nacht gaat door`); }')

    # het toetsje
    cur = rep(cur,
        '  if (an.toetsGaten.length) {\n'
        '    const gat = an.toetsGaten[0];',
        '  if (an.toetsGaten.length) try {\n'
        '    const gat = an.toetsGaten[0];')
    cur = rep(cur,
        '      console.log(`    toetsje ${qz.id} goedgekeurd met ${qz.vragen.length} vragen`);\n'
        '    }\n'
        '  }',
        '      console.log(`    toetsje ${qz.id} goedgekeurd met ${qz.vragen.length} vragen`);\n'
        '    }\n'
        '  } catch (e) { console.error(`    het toetsje klapte: ${e && e.message}; de zinnen hierboven blijven staan`); }')

    # de nieuwe les
    cur = rep(cur,
        '  let nieuweLes = null;\n'
        '  if (verlengen) {',
        '  let nieuweLes = null;\n'
        '  if (verlengen) try {')
    cur = rep(cur,
        '          else { versie = echt.versie; console.log(`  nieuwe les weggeschreven → ${echt.versie} (zet dit in een pull request)`); }\n'
        '        }\n'
        '      }\n'
        '    }\n'
        '  }',
        '          else { versie = echt.versie; console.log(`  nieuwe les weggeschreven → ${echt.versie} (zet dit in een pull request)`); }\n'
        '        }\n'
        '      }\n'
        '    }\n'
        '  } catch (e) { nieuweLes = null; console.error(`  de nieuwe les klapte: ${e && e.message}; de reparatie hierboven staat er wel`); }')

# ---------------------------------------------------------------- C. de foutmelding die niets zei
if DOE_SH:
    sh = rep(sh,
        '  # ---- 1. genereren ----\n'
        '  # shellcheck disable=SC2086\n'
        '  node tools/curriculum.js $VLAGGEN',
        '  # ---- 1. genereren ----\n'
        '  # 23 aug (v23.178): hier stond alleen de aanroep, en dit script draait met `set -e`. Eindigde\n'
        '  # curriculum.js met 1, dan sprong het script er meteen uit, vóórdat het ooit een `wat`\n'
        '  # schreef. De laatste stap van de workflow zei dan letterlijk: "De avondrun heeft niets\n'
        '  # gepubliceerd ()." Melden dát er iets mis is zonder te melden wát, is de helft van een\n'
        '  # meldsysteem. Nu blijft de exitcode staan en gaat er een reden mee naar buiten.\n'
        '  # shellcheck disable=SC2086\n'
        '  CODE=0\n'
        '  node tools/curriculum.js $VLAGGEN || CODE=$?\n'
        '  if [ "$CODE" -ne 0 ]; then\n'
        '    zeg "curriculum.js eindigde met code $CODE. Wat de run daar zelf over zegt:"\n'
        '    cat tools/avondrun-hart.json 2>/dev/null || true\n'
        '    echo "wat=geklapt" >> "$UIT"\n'
        '    echo "pogingen=$poging" >> "$UIT"\n'
        '    echo "code=$CODE" >> "$UIT"\n'
        '    exit "$CODE"\n'
        '  fi')

CUR.write_text(cur, encoding="utf-8")
SH.write_text(sh, encoding="utf-8")
print("tools/curriculum.js: " + ("oud gerepareerd en vangnetten erin" if DOE_CUR else "stond er al"))
print("tools/avondrun.sh: " + ("wat=geklapt toegevoegd" if DOE_SH else "stond er al"))

# ---------------------------------------------------------------- E. de controle die dit had gevangen
#
# node --check leest alleen of het geldige JavaScript is, en `oud` gebruiken zonder hem te
# declareren is geldig JavaScript. Wat dit wél vangt is eslint met de regel no-undef. Nagemeten: met
# de reparatie van A teruggedraaid meldt eslint vijf keer "'oud' is not defined" op de regels
# 723-729, en met de reparatie erin nul fouten over alle vijf de gereedschapsbestanden.
#
# Dat is precies het gat tussen "het draait" en "het is nagekeken": de tak met `oud` wordt alleen
# geraakt als de corrector iets afkeurt én er al een toetsje met die tag bestaat. Zo'n tak haalt
# geen enkele proefrun, en dus moet een controle hem zonder uitvoeren kunnen zien.
CFG = W / "eslint.config.mjs"
PKG = W / "package.json"

if not CFG.exists():
    CFG.write_text("""// De controle die de nachten van 21 en 22 augustus had voorkomen (v23.178).
//
// In maakToets() stond `if (oud && ...)` terwijl `oud` bij een andere functie hoorde. Dat is geldige
// JavaScript, dus `node --check` liet het door; pas als de corrector iets afkeurde klapte de run met
// "oud is not defined", en omdat alles in één ketting zat ging de hele nacht mee.
//
// Eén regel is hier het doel: no-undef. Geen stijlregels, geen opmaak, niets waarover te twisteren
// valt. Een controle die over komma's begint wordt uitgezet, en dan vangt hij ook dit niet meer.
export default [
  {
    files: ["tools/**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "commonjs",
      globals: {
        require: "readonly", module: "writable", exports: "writable", process: "readonly",
        console: "readonly", __dirname: "readonly", __filename: "readonly", Buffer: "readonly",
        fetch: "readonly", setTimeout: "readonly", clearTimeout: "readonly",
        URL: "readonly", TextDecoder: "readonly", TextEncoder: "readonly", AbortController: "readonly"
      }
    },
    linterOptions: { reportUnusedDisableDirectives: false },
    rules: { "no-undef": "error" }
  }
];
""", encoding="utf-8")
    print("eslint.config.mjs: aangemaakt (alleen no-undef, op tools/)")

if not PKG.exists():
    PKG.write_text(json.dumps({
        "name": "vamos",
        "private": True,
        "description": "De app is een enkel bestand; dit package.json bestaat alleen voor de controle op tools/ (zie eslint.config.mjs).",
        "scripts": {"lint": "eslint tools"},
        "devDependencies": {"eslint": "9.39.5"}
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("package.json: aangemaakt")

GIT = W / ".gitignore"
gi = GIT.read_text(encoding="utf-8")
if "\n/node_modules/\n" not in gi:
    gi = gi.replace("server/node_modules/\n",
        "server/node_modules/\n"
        "# v23.178: de repo-root heeft sinds de lintstap ook een package.json. Alleen eslint, alleen\n"
        "# no-undef, alleen op tools/.\n"
        "/node_modules/\n/package-lock.json\n")
    GIT.write_text(gi, encoding="utf-8")
    print(".gitignore: node_modules van de root erbij")

YML = W / ".github" / "workflows" / "curriculum.yml"
yml = YML.read_text(encoding="utf-8")
if "npm run lint" not in yml:
    a = "      - name: Zelftest van de contentbibliotheek\n        run: node tools/content-lib.js --zelftest\n"
    assert yml.count(a) == 1
    yml = yml.replace(a,
        "      # v23.178: no-undef op tools/. Dit had de nachten van 21 en 22 augustus voorkomen, waar de\n"
        "      # run klapte op een `oud` die in die functie nooit gedeclareerd was. node --check ziet dat\n"
        "      # niet, want het is geldige JavaScript.\n"
        "      - name: Ongedeclareerde namen in tools/\n"
        "        run: |\n"
        "          npm install --no-audit --no-fund --silent\n"
        "          npm run lint\n"
        "\n" + a)
    YML.write_text(yml, encoding="utf-8")
    print(".github/workflows/curriculum.yml: lintstap toegevoegd")
else:
    print(".github/workflows/curriculum.yml: lintstap stond er al")

# ---------------------------------------------------------------- D. de hartslag terugzetten
ECHT = W / "claude" / "hartslag-run25.json"
if ECHT.exists():
    huidig = json.loads(HART.read_text(encoding="utf-8"))
    if huidig.get("beloofd") is None:
        HART.write_text(ECHT.read_text(encoding="utf-8"), encoding="utf-8")
        print("tools/avondrun-hart.json: het verslag van run #25 teruggezet")
    else:
        print("tools/avondrun-hart.json: er staat al een echte hartslag")
