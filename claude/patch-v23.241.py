#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.241 - twee ladingen, twee routes, en één werkmap was er één te weinig
#
# Stefan leverde het artefact van de afgekeurde run aan. Binnen twee minuten stond het er:
#
#     ROOD  pw-lesgat.js
#     ✗ het aantal onverklaarde kaarten loopt niet op (1 van maximaal 0)
#
# En de onverklaarde kaart was nummer 30, "Subjuntivo met wensen en verlangen", met acht vragen.
#
# WAT ER ECHT GEBEURDE
#
# De nacht maakt TWEE dingen met TWEE verschillende routes:
#
#     reparatie    10 oefenzinnen + 1 toetsje op costar en gustar  ->  direct live
#     nieuwe les   b1-12 "El tiempo libre y los hobbies", met een  ->  via een pull request
#                  eigen spiekbriefkaart (30) en toets q-b1-12
#
# Alleen: curriculum.js schrijft ze allebei in DEZELFDE index.html. `pasToe(nieuweLes, {})` zet de
# les gewoon in de werkmap, ook al gaat hij daarna via een pull request. Daarna keurt de poort die
# gecombineerde boom, en pw-lesgat zegt: kaart 30 heeft een toets en geen les. Die regel is
# volkomen terecht (hij bestaat sinds v23.193, toen 35 procent van de toetsvragen over onuitgelegde
# stof ging), maar hij gaat hier af op de LES, en het zijn de tien oefenzinnen die er niet doorkomen.
#
# En het is nog erger, want er is ook maar één etiket. avondrun.sh zet WAT="nieuwe-les" zodra er een
# les in het plan staat, en de workflow heeft dan géén stap "Reparatie direct live". Dus zelfs met een
# groene poort waren die tien zinnen niet live gegaan: ze zaten in de pull request.
#
# Eén werkmap, één etiket en één poort voor twee ladingen die niet dezelfde kant op gaan.
#
# WAT ER NU STAAT
#
#   1. DE LES BLIJFT UIT DE WERKMAP. curriculum.js schrijft hem als lading weg
#      (tools/curriculum-les-lading.json) en raakt index.html niet aan. De poort keurt dan wat er
#      werkelijk direct live gaat, en niets anders.
#   2. HET ETIKET SPLITST. avondrun.sh geeft `wat` (de reparatie) en daarnaast `les=1`. De twee
#      stappen in de workflow sluiten elkaar niet meer uit: een nacht met allebei levert de
#      reparatie live én opent een pull request.
#   3. DE PULL REQUEST BOUWT ZICHZELF. Hij maakt een tak op verse main en past de leslading daar toe
#      met tools/curriculum-toepassen.js. De poort draait op die tak vanzelf mee (poort.yml draait op
#      pull requests), dus het oordeel over de les komt op de les te staan in plaats van op de nacht.
#   4. EN DE HARTSLAG ZEGT WELKE PROEF DICHTGING. tools/hartslag-poort.js, met zelftest. Drie nachten
#      stond er drie keer dezelfde zin; de twee regels die het antwoord waren, stonden in een
#      artefact dat iemand met de hand moest downloaden.
#
# WAT DIT NIET OPLOST, EN DAT HOORT HIER TE STAAN
#
# De les zelf komt hierdoor niet door de poort. Een nieuwe les die een spiekbriefkaart introduceert
# zonder grammaticaconcept dat die kaart uitlegt, valt over pw-lesgat, en dat is precies wat die regel
# hoort te doen. De generator van nieuwe lessen schrijft op dit moment geen concept mee. Zolang dat zo
# is, komt elke nieuwe les met een eigen kaart als rode pull request binnen. Dat is nu wel zichtbaar
# op de juiste plek in plaats van dat het de rest tegenhoudt.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
CUR = W / "tools" / "curriculum.js"
SH = W / "tools" / "avondrun.sh"
WF = W / ".github" / "workflows" / "curriculum.yml"
NIEUW = "v23.241"

huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep_in(pad, anker, nieuw, n=1):
    tekst = pad.read_text(encoding="utf-8")
    c = tekst.count(anker)
    assert c == n, "%s: anker %d keer (verwacht %d): %r" % (pad.name, c, n, anker[:90])
    pad.write_text(tekst.replace(anker, nieuw, n), encoding="utf-8")


# ---------------------------------------------------------------- 1. de les uit de werkmap
cur = CUR.read_text(encoding="utf-8")
if "curriculum-les-lading.json" not in cur:
    rep_in(CUR, """const LADING = path.join(__dirname, "curriculum-lading.json");""",
"""const LADING = path.join(__dirname, "curriculum-lading.json");
/* v23.241: en de nieuwe les apart, want die gaat een andere kant op. Zie de kop bij het wegschrijven
   hieronder: een les die via een pull request gaat, hoort niet in de boom te staan die de poort
   keurt voor wat er direct live moet. */
const LES_LADING = path.join(__dirname, "curriculum-les-lading.json");""")

    rep_in(CUR, """        if (!OPT.droog) {
          const echt = lib.pasToe(nieuweLes, {});
          if (!echt.ok) { console.error("nieuwe les alsnog afgekeurd bij schrijven:\\n - " + echt.fouten.join("\\n - ")); nieuweLes = null; }
          else { versie = echt.versie; console.log(`  nieuwe les weggeschreven → ${echt.versie} (zet dit in een pull request)`); }
        }""",
"""        /* v23.241: DE LES BLIJFT UIT DE WERKMAP.

           Hier stond `lib.pasToe(nieuweLes, {})`, en dat schreef de les in dezelfde index.html als
           de reparatie. Daarna keurt de poort die gecombineerde boom. Gemeten in de nacht van 5
           september: de les b1-12 bracht spiekbriefkaart 30 mee zonder grammaticaconcept dat die
           kaart uitlegt, pw-lesgat ging daarop af, en de tien oefenzinnen van diezelfde nacht kwamen
           er niet doorheen. Drie nachten achter elkaar, om drie verschillende lessen.

           Een lading die via een pull request gaat, hoort niet in de boom te staan die geoordeeld
           wordt over wat er direct live moet. Hij gaat als lading naar de tak, en daar keurt de poort
           hem op zijn eigen merites. */
        if (!OPT.droog) {
          fs.writeFileSync(LES_LADING, JSON.stringify(nieuweLes, null, 1));
          console.log(`  nieuwe les klaargezet als lading → ${LES_LADING} (gaat via een pull request)`);
        }""")
    print("curriculum.js: de nieuwe les blijft uit de werkmap")
else:
    print("curriculum.js: stond er al")

# ---------------------------------------------------------------- 2. het etiket splitst
sh = SH.read_text(encoding="utf-8")
if "les=1" not in sh:
    rep_in(SH, """  if [ -f tools/curriculum-laatste.json ] && \\
     node -e "process.exit(require('./tools/curriculum-laatste.json').nieuweLes ? 0 : 1)"; then
    WAT="nieuwe-les"
    TITEL=$(node -e "console.log(require('./tools/curriculum-laatste.json').nieuweLes.titel)")
  else
    WAT="reparatie"
    TITEL=""
  fi""",
"""  # v23.241: TWEE LADINGEN, TWEE ETIKETTEN.
  #
  # Hier stond één woord voor twee dingen: was er een nieuwe les, dan heette de hele nacht
  # "nieuwe-les" en had de workflow geen stap "Reparatie direct live". De oefenzinnen van diezelfde
  # nacht gingen dan mee in de pull request, ook als er niets mis mee was. In de nacht van 5
  # september waren dat er tien.
  #
  # De reparatie staat sinds v23.241 als enige in de werkmap (de les gaat als lading naar zijn eigen
  # tak), dus `wat` gaat over de reparatie en `les` is een tweede vlag ernaast.
  WAT="reparatie"
  TITEL=""
  LES=""
  if [ -f tools/curriculum-les-lading.json ]; then
    LES="1"
    TITEL=$(node -e "console.log(require('./tools/curriculum-les-lading.json').nieuweLessen[0].titel)")
  fi""")

    rep_in(SH, """  if [ $GROEN -eq 0 ]; then
    zeg "poging $poging is door de poort"
    echo "wat=$WAT" >> "$UIT"
    [ -n "$TITEL" ] && echo "titel=$TITEL" >> "$UIT"
    echo "pogingen=$poging" >> "$UIT"
    exit 0
  fi""",
"""  if [ $GROEN -eq 0 ]; then
    zeg "poging $poging is door de poort"
    echo "wat=$WAT" >> "$UIT"
    [ -n "$TITEL" ] && echo "titel=$TITEL" >> "$UIT"
    [ -n "$LES" ] && echo "les=1" >> "$UIT"
    echo "pogingen=$poging" >> "$UIT"
    exit 0
  fi""")

    # de hartslag krijgt de diagnose mee, bij elke afgekeurde poging
    rep_in(SH, """  zeg "afgekeurd. Bewijs staat in $MAP\"""",
"""  # v23.241: en de hartslag zegt vanaf nu WELKE proef dichtging. Drie nachten stond er drie keer
  # dezelfde zin ("de poort ging dicht op wat de bot schreef"), terwijl de twee regels die het
  # antwoord waren in dit logboek stonden. Een controle die wel afgaat maar niet vertelt wat hij zag,
  # is de helft van een meldsysteem.
  node tools/hartslag-poort.js "$POORTLOG" tools/avondrun-hart.json || true
  cp tools/avondrun-hart.json "$MAP/avondrun-hart.json" 2>/dev/null || true

  zeg "afgekeurd. Bewijs staat in $MAP\"""")
    print("avondrun.sh: twee etiketten, en de hartslag krijgt de diagnose")
else:
    print("avondrun.sh: stond er al")

# ---------------------------------------------------------------- 3. de workflow
wf = WF.read_text(encoding="utf-8")
if "curriculum-les-lading.json" not in wf:
    rep_in(WF, """        run: node tools/curriculum-toepassen.js --zelftest""",
"""        run: node tools/curriculum-toepassen.js --zelftest

      # v23.241: de hartslag hoort te zeggen welke proef dichtging en niet dat er een dichtging.
      - name: Zelftest van de poortdiagnose
        run: node tools/hartslag-poort.js --zelftest""")

    rep_in(WF, """      - name: Reparatie direct live
        if: steps.run.outputs.wat == 'reparatie'""",
"""      # v23.241: deze stap en de pull request hieronder sluiten elkaar niet meer uit. Ze gingen over
      # twee verschillende ladingen die toevallig in dezelfde nacht ontstaan, en één etiket voor
      # allebei betekende dat een nacht met een nieuwe les zijn oefenzinnen niet live kreeg.
      - name: Reparatie direct live
        if: steps.run.outputs.wat == 'reparatie'""")

    rep_in(WF, """      - name: Nieuwe les als pull request
        if: steps.run.outputs.wat == 'nieuwe-les'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "curriculum-bot"
          git config user.email "actions@users.noreply.github.com"
          TAK="curriculum/les-$(date +%Y%m%d)"
          git checkout -b "$TAK"
          git add index.html versie.txt tools/curriculum-laatste.json audio
          git commit -m "curriculum: nieuwe les \\"${{ steps.run.outputs.titel }}\\""
          git push -u origin "$TAK\"""",
"""      # v23.241: DE PULL REQUEST BOUWT ZICHZELF, OP VERSE MAIN.
      #
      # Hier stond `git checkout -b` op de werkmap van de run, en die bevatte de nieuwe les ómdat
      # curriculum.js hem daarin schreef. Precies dat maakte dat de poort van de nacht over de les
      # oordeelde in plaats van over de reparatie, en dat de zinnen van diezelfde nacht bleven liggen.
      #
      # De les komt nu als lading binnen en wordt op een verse tak toegepast. poort.yml draait op
      # pull requests, dus het oordeel over de les komt op de les te staan. Is die rood, dan zie je
      # dat op de PR en houdt hij niets anders tegen.
      - name: Nieuwe les als pull request
        if: steps.run.outputs.les == '1'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "curriculum-bot"
          git config user.email "actions@users.noreply.github.com"
          cp tools/curriculum-les-lading.json "$RUNNER_TEMP/les-lading.json"
          git fetch origin main --quiet
          TAK="curriculum/les-$(date +%Y%m%d)"
          git checkout -b "$TAK" FETCH_HEAD
          node tools/curriculum-toepassen.js "$RUNNER_TEMP/les-lading.json"
          git add index.html versie.txt tools/curriculum-laatste.json audio
          git commit -m "curriculum: nieuwe les \\"${{ steps.run.outputs.titel }}\\""
          git push -u origin "$TAK\"""")

    rep_in(WF, """          node -e "const l=require('./tools/curriculum-laatste.json').nieuweLes;""",
        """          node -e "const l=require('./tools/curriculum-les-lading.json').nieuweLessen[0];""")
    print("curriculum.yml: de les krijgt zijn eigen tak en zijn eigen oordeel")
else:
    print("curriculum.yml: stond er al")

# ---------------------------------------------------------------- controles
cur = CUR.read_text(encoding="utf-8")
sh = SH.read_text(encoding="utf-8")
wf = WF.read_text(encoding="utf-8")
kaal = re.sub(r"/\*.*?\*/", "", cur, flags=re.S)
kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
assert "lib.pasToe(nieuweLes, {})" not in kaal, "de nieuwe les gaat nog steeds de werkmap in"
assert "fs.writeFileSync(LES_LADING," in cur, "de leslading wordt niet weggeschreven"
assert "wat == 'nieuwe-les'" not in wf, "de workflow werkt nog met één etiket"
assert "steps.run.outputs.les == '1'" in wf, "de pull request hangt niet aan zijn eigen vlag"
assert "hartslag-poort.js" in sh and "hartslag-poort.js --zelftest" in wf, "de diagnose draait niet mee"
# de reparatie en de les sluiten elkaar niet meer uit
assert wf.count("if: steps.run.outputs.wat == 'reparatie'") == 1, "de reparatiestap is verdwenen"

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
