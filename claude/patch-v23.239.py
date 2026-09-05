#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.239 - de nacht levert zijn lading af, niet zijn bestand
#
# Stefan, 5 september: "nee het mag autonoom live gaan."
#
# Goed. Dan moet de laatste stap kloppen, en die klopte niet.
#
# WAT ER MIS WAS AAN "REPARATIE DIRECT LIVE"
#
#     git add index.html versie.txt ... && git commit && git push
#
# Die index.html is de main van het moment dat de run begon, plús wat de bot erbij schreef. Op deze
# main publiceren drie schrijvers: de logboek-Action (die GitHub steeds later inplant, van 02:30 naar
# 13:01), de avondrun zelf, en Stefan. Verschuift main tijdens het venster van de avondrun, dan
# gebeurt er één van twee dingen:
#
#   - de push wordt geweigerd en de nacht valt weg. Dat is wat er nu gebeurt, en het is de veilige
#     helft: er raakt niets kwijt, er komt alleen niets aan.
#   - of iemand "repareert" dat door het bestand op verse main te kopiëren, en dan verdwijnt alles
#     wat er tussendoor op main is gezet, zonder dat iemand het ziet.
#
# De hartslagstap heeft die reparatie op 31 augustus al gekregen: avondrun-leveren.sh pakt verse
# main, legt de bestanden erop en probeert het opnieuw bij een botsing. Alleen mag je dat trucje niet
# op index.html toepassen, want dat bestand is niet van de avondrun alleen.
#
# EN ER WAS EEN TWEEDE, STILLERE FOUT: DE VERSIETELLER
#
# pasToe() hoogt APP_VERSIE op vanaf wat het in het bestand vindt, aan het BEGIN van de nacht. Dat is
# een nummer kiezen op grond van een main die er straks niet meer is. Gemeten: de avondrun van
# vannacht stond op v23.237, terwijl hier diezelfde dag v23.236, v23.237 en v23.238 zijn gemaakt.
# Twee schrijvers die uit dezelfde teller nummers uitdelen, en niets dat dat merkt. Zolang er niets
# gepusht wordt is dat onschadelijk. Vanaf de dag dat het wél lukt, bestaan er twee v23.237's.
#
# WAT ER NU STAAT
#
# Wat de nacht maakt is geen BESTAND maar een LADING: een stapelbare toevoeging. Dezelfde keuze als
# bij tools/nachtpatch.py van 3 september.
#
#   1. curriculum.js schrijft de lading zelf weg (tools/curriculum-lading.json), niet alleen de
#      id-lijst. Zonder de inhoud valt er niets te herhalen en is het bestand het enige dat je hebt.
#   2. tools/curriculum-toepassen.js legt die lading op de index.html die er op dat moment ligt, wat
#      die ook is. Met zelftest, en de zelftest bewijst vooral dat hij kán stranden.
#   3. avondrun-leveren.sh krijgt voor index.html hetzelfde uitzonderingsgeval dat audio/stemmen.json
#      al had: main wint, wij vullen aan. Dus geen cp maar een herhaling van de lading, ná de reset
#      op verse main.
#
# Daarmee wordt het versienummer als laatste gekozen, van wat er dan echt staat. Botsen kan niet meer:
# er is één plek waar het volgende nummer vandaan komt, en dat is het bestand op het moment van
# publiceren.
#
# WAT DIT NIET REPAREERT
#
# De avondrun komt op dit moment niet eens tót publiceren: de poort gaat dicht op wat de bot schrijft,
# in alle pogingen, drie nachten op rij. Welke suite dat is staat niet in de repo maar in het artefact
# avondrun-afgekeurd-<run_id> op de pagina van die run. Zonder dat artefact zou elke diagnose hier een
# gok zijn, en een verkeerde diagnose is erger dan geen.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
CUR = W / "tools" / "curriculum.js"
LEV = W / "tools" / "avondrun-leveren.sh"
WF = W / ".github" / "workflows" / "curriculum.yml"
NIEUW = "v23.239"

huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep_in(pad, anker, nieuw, n=1):
    tekst = pad.read_text(encoding="utf-8")
    c = tekst.count(anker)
    assert c == n, "%s: anker %d keer (verwacht %d): %r" % (pad.name, c, n, anker[:90])
    pad.write_text(tekst.replace(anker, nieuw, n), encoding="utf-8")


# ---------------------------------------------------------------- 1. de lading wegschrijven
cur = CUR.read_text(encoding="utf-8")
if "curriculum-lading.json" not in cur:
    rep_in(CUR, """const PLAN = path.join(__dirname, "curriculum-laatste.json");""",
"""const PLAN = path.join(__dirname, "curriculum-laatste.json");
/* v23.239: de lading zelf, naast de id-lijst hierboven.
   PLAN bewaart wát er is toegevoegd (s247, q-relatar-extra6) en dat is genoeg om 's ochtends te
   lezen wat de nacht deed. Het is niet genoeg om het nóg een keer te doen, en dat is precies wat er
   nodig is zodra main onder de run vandaan beweegt: dan wil je niet het BESTAND afleveren maar de
   TOEVOEGING, op verse main. Zie tools/curriculum-toepassen.js. */
const LADING = path.join(__dirname, "curriculum-lading.json");""")

    rep_in(CUR, """      reparatie: { zinnen: reparatie.sentences.map(s => s.id), toetsjes: reparatie.quizzes.map(q => q.id) },
      nieuweLes: nieuweLes ? nieuweLes.nieuweLessen[0] : null
    }, null, 1));
  }""",
"""      reparatie: { zinnen: reparatie.sentences.map(s => s.id), toetsjes: reparatie.quizzes.map(q => q.id) },
      nieuweLes: nieuweLes ? nieuweLes.nieuweLessen[0] : null
    }, null, 1));
    /* v23.239: en de lading zelf, in de vorm die pasToe() eet. Alleen de reparatie: de nieuwe les
       gaat via een pull request en hoort niet ongezien op main te belanden. */
    fs.writeFileSync(LADING, JSON.stringify(reparatie, null, 1));
  }""")
    print("curriculum.js: schrijft de lading weg")
else:
    print("curriculum.js: stond er al")

# ---------------------------------------------------------------- 2. leveren: index.html is geen bestand
lev = LEV.read_text(encoding="utf-8")
if "curriculum-toepassen.js" not in lev:
    rep_in(LEV, """        if [ "$PAD" = "audio/stemmen.json" ]; then
          node tools/stemmen-samenvoegen.js "$BEWAAR/$PAD" >/dev/null 2>&1 || true
        else""",
"""        if [ "$PAD" = "audio/stemmen.json" ]; then
          node tools/stemmen-samenvoegen.js "$BEWAAR/$PAD" >/dev/null 2>&1 || true
        elif [ "$PAD" = "index.html" ]; then
          # v23.239: dezelfde regel als hierboven, om dezelfde reden. index.html is niet van de
          # avondrun alleen; op deze main publiceren drie schrijvers. Het bestand kopiëren zou alles
          # wegvagen wat er tussendoor op main is gezet, en dat verlies zou niemand zien.
          #
          # Wat van deze run is, is niet het bestand maar de LADING. Die leggen we op verse main:
          # pasToe() keurt hem daar opnieuw (een id dat vanochtend vrij was kan inmiddels vergeven
          # zijn) en hoogt de versie op vanaf wat er op dat moment echt staat. Daarmee is de
          # versieteller niet langer iets dat twee schrijvers los van elkaar bijhouden.
          #
          # versie.txt hoort hier niet bij: die wordt door dezelfde stap geschreven.
          node tools/curriculum-toepassen.js "$BEWAAR/tools/curriculum-lading.json"
          TCODE=$?
          # 2 betekent "niets toe te passen", en dat is geen mislukking.
          [ "$TCODE" = "0" ] || [ "$TCODE" = "2" ] || exit 1
        elif [ "$PAD" = "versie.txt" ]; then
          :
        else""")
    print("avondrun-leveren.sh: index.html gaat als lading mee")
else:
    print("avondrun-leveren.sh: stond er al")

# ---------------------------------------------------------------- 3. de workflow
wf = WF.read_text(encoding="utf-8")
if "curriculum-toepassen.js --zelftest" not in wf:
    rep_in(WF, """        run: node tools/avondrun-herkansing.js --zelftest""",
"""        run: node tools/avondrun-herkansing.js --zelftest

      # v23.239: de stap die de lading op verse main legt. Hij staat hier tussen de zelftests omdat
      # hij vanaf nu het enige pad naar main is voor de inhoud van de nacht, en omdat zijn proeven
      # vooral bewijzen dat hij KAN stranden: een publicatiestap die alles doorlaat is geen stap.
      - name: Zelftest van de lading
        run: node tools/curriculum-toepassen.js --zelftest""")

if "sh tools/avondrun-leveren.sh \"avondrun: $SAMENVATTING\"" not in wf:
    rep_in(WF, """          git add index.html versie.txt tools/curriculum-laatste.json tools/avondrun-hart.json audio
          git commit -m "avondrun: $SAMENVATTING"
          git push""",
"""          # v23.239: via avondrun-leveren.sh, net als de hartslag sinds 31 augustus. Hier stond een
          # kale commit-en-push op de main van drie uur geleden, en die wordt geweigerd zodra de
          # logboek-Action of Stefan er ondertussen overheen is gegaan. Gevolg: de hele nacht viel
          # weg, en dat is de veilige helft van fout.
          #
          # index.html gaat niet als bestand mee maar als lading (zie het uitzonderingsgeval in dat
          # script): verse main pakken, de zinnen erop leggen, en het versienummer pas dan kiezen.
          # versie.txt staat er wel bij, want hij moet mee de commit in, maar hij wordt niet
          # gekopieerd: het toepassen schrijft hem, van wat er op verse main stond.
          sh tools/avondrun-leveren.sh "avondrun: $SAMENVATTING" \\
            index.html versie.txt tools/curriculum-laatste.json tools/avondrun-hart.json audio""")
    print("curriculum.yml: de reparatie gaat via de levering")
else:
    print("curriculum.yml: stond er al")

# ---------------------------------------------------------------- controles
cur = CUR.read_text(encoding="utf-8")
lev = LEV.read_text(encoding="utf-8")
wf = WF.read_text(encoding="utf-8")
assert "fs.writeFileSync(LADING," in cur, "de lading wordt niet weggeschreven"
assert 'node tools/curriculum-toepassen.js "$BEWAAR/tools/curriculum-lading.json"' in lev, \
    "de levering past de lading niet toe"
# geen kale push meer op de inhoud: dat is het hele punt van deze ronde
kaal = [r for r in wf.split("\n") if r.strip() == "git push" ]
assert not kaal, "er staat nog een kale push in de workflow: " + str(kaal[:2])
assert "curriculum-toepassen.js --zelftest" in wf, "de zelftest draait niet mee"

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
