#!/bin/sh
# De avondrun in één script: genereren, keuren, en bij afkeuring nog één keer proberen.
#
# WAAROM DIT BESTAAT
#
# Stefan, 13 aug: "avondrun gaat niet goed en doe ik in github re-run jobs dan gaat het wel goed.
# fix it structureel."
#
# Dat klopte, en het waarom is minder toevallig dan het lijkt. "Re-run all jobs" draait niet dezelfde
# content nog een keer langs de poort: het draait `curriculum.js` opnieuw, en die vraagt een
# taalmodel om nieuwe zinnen. Een re-run is dus geen herkansing voor de poort maar een nieuwe worp.
# Zolang dat met de hand moest, was de avondrun een machine die je 's ochtends zelf moest aanzwengelen.
#
# Dit script doet die worp automatisch, hoogstens twee keer, en houdt van elke mislukte poging het
# bewijs vast. Twee en niet vijf: als het twee keer op rij misgaat is er iets anders aan de hand dan
# een ongelukkige zin, en dan wil je het 's ochtends zien in plaats van dat de bot het wegpoetst.
#
# WAT HET SCHRIJFT
#   $GITHUB_OUTPUT   wat=niets|reparatie|nieuwe-les · titel=... · pogingen=N
#   $BEWIJS/poging-N het volledige spoor van elke afgekeurde poging (diff, log, schermafdrukken)
#
# Exitcode 0 betekent: er staat iets klaar dat door de poort is (of er viel niets te doen).
# Exitcode 1 betekent: alle pogingen zijn afgekeurd, er is niets om te publiceren.
set -e

MAX_POGINGEN="${MAX_POGINGEN:-2}"
WERK="${RUNNER_TEMP:-/tmp}"
BEWIJS="${BEWIJS:-$WERK/mislukt}"
UIT="${GITHUB_OUTPUT:-/dev/null}"
SAMENVATTING="${GITHUB_STEP_SUMMARY:-/dev/null}"
VLAGGEN="$1"

# Niet aannemen dat de map bestaat. Op een runner bestaat RUNNER_TEMP wel, maar toen ik dit script
# lokaal natestte klapte hij op precies die aanname, en dan is de eerste echte nacht de test.
mkdir -p "$WERK"

zeg() { echo "$@"; }

# 28 augustus: het bewijs wordt nu vanaf twee plekken bewaard (een afgekeurde poging én een klapper),
# en twee kopieën van deze regels zouden na één ronde uit elkaar lopen.
bewaar_bewijs() {
  MAP="$BEWIJS/poging-$1"
  mkdir -p "$MAP"
  git diff > "$MAP/wat-de-bot-schreef.diff" 2>/dev/null || true
  cp "${POORTLOG:-/dev/null}" "$MAP/poort.log" 2>/dev/null || true
  cp index.html versie.txt "$MAP/" 2>/dev/null || true
  cp tools/curriculum-laatste.json tools/avondrun-hart.json "$MAP/" 2>/dev/null || true
  cp -r test/uitvoer "$MAP/schermen" 2>/dev/null || true
  {
    echo "### Poging $1: $2"
    echo ""
    echo '```'
    cat tools/avondrun-hart.json 2>/dev/null | head -c 2000 || echo "(geen hartslag)"
    echo '```'
  } >> "$SAMENVATTING"
  zeg "bewijs staat in $MAP"
}

poging=1
while [ "$poging" -le "$MAX_POGINGEN" ]; do
  zeg ""
  zeg "=================== poging $poging van $MAX_POGINGEN ==================="

  # ---- 1. genereren ----
  # 23 aug (v23.178): hier stond alleen de aanroep, en dit script draait met `set -e`. Eindigde
  # curriculum.js met 1, dan sprong het script er meteen uit, vóórdat het ooit een `wat`
  # schreef. De laatste stap van de workflow zei dan letterlijk: "De avondrun heeft niets
  # gepubliceerd ()." Melden dát er iets mis is zonder te melden wát, is de helft van een
  # meldsysteem. Nu blijft de exitcode staan en gaat er een reden mee naar buiten.
  # shellcheck disable=SC2086
  CODE=0
  node tools/curriculum.js $VLAGGEN || CODE=$?
  if [ "$CODE" -ne 0 ]; then
    zeg "curriculum.js eindigde met code $CODE. Wat de run daar zelf over zegt:"
    cat tools/avondrun-hart.json 2>/dev/null || true

    # 28 AUGUSTUS: EEN KLAPPER LIEP OM DE HERKANSING HEEN
    #
    # Hier stond `exit "$CODE"`, en dat is de reden dat de avondrun vijf nachten op rij rood stond
    # met "niets gepubliceerd (geklapt)". Dit script heet "hoogstens twee pogingen" en heeft een lus
    # die daarvoor bestaat, maar een klapper sprong er bij poging één meteen uit. De herkansing dekte
    # dus alleen "de poort keurde de tekst af" en niet "de run viel om".
    #
    # En sinds v23.178 is dat tweede geval juist het gewone geval: toen kreeg curriculum.js exitcode
    # 1 voor "beloofd en niets geleverd". De herkansing was er, en precies de meest voorkomende
    # mislukking liep eromheen.
    #
    # Niet elke klapper verdient een herkansing: twaalf minuten opnieuw draaien om weer te horen dat
    # er geen taalmodel is, kost een nacht en levert niets. Dat onderscheid is een regel met gevallen
    # en staat daarom in tools/avondrun-herkansing.js, mét een zelftest. Zie de kop daar.
    if node tools/avondrun-herkansing.js "$CODE" tools/avondrun-hart.json; then
      if [ "$poging" -lt "$MAX_POGINGEN" ]; then
        bewaar_bewijs "$poging" "klapper (code $CODE)"
        git checkout -- . 2>/dev/null || true
        cp "$BEWIJS/poging-$poging/avondrun-hart.json" tools/avondrun-hart.json 2>/dev/null || true
        poging=$((poging + 1))
        continue
      fi
      zeg "Ook de laatste poging klapte."
    fi
    bewaar_bewijs "$poging" "klapper (code $CODE)"
    echo "wat=geklapt" >> "$UIT"
    echo "pogingen=$poging" >> "$UIT"
    echo "code=$CODE" >> "$UIT"
    exit "$CODE"
  fi

  # ---- 2. wat is er veranderd? ----
  # De hartslag verandert per definitie elke nacht en telt hier dus niet mee. Anders zou "er is iets
  # veranderd" altijd waar zijn en draaide de poort elke nacht voor niets.
  if git diff --quiet -- . ':(exclude)tools/avondrun-hart.json'; then
    zeg "Er is niets weggeschreven. Wat de run daar zelf over zegt:"
    cat tools/avondrun-hart.json 2>/dev/null || true
    echo "wat=niets" >> "$UIT"
    echo "pogingen=$poging" >> "$UIT"
    exit 0
  fi

  # v23.241: TWEE LADINGEN, TWEE ETIKETTEN.
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
  fi
  zeg "soort: $WAT ${TITEL:+($TITEL)}"

  # ---- 3. keuren ----
  # Twee kernen op een GitHub-runner, dus twee browsers tegelijk. Met de standaard van vier vecht de
  # poort met zichzelf om processortijd en lopen suites tegen hun eigen tijdslimiet aan.
  POORTLOG="$WERK/poort-poging-$poging.log"
  set +e
  node tools/syntaxcheck.js index.html > "$POORTLOG" 2>&1
  SYNTAX=$?
  if [ $SYNTAX -eq 0 ]; then
    TEGELIJK="${TEGELIJK:-2}" node test/poort.js >> "$POORTLOG" 2>&1
    GROEN=$?
  else
    GROEN=1
  fi
  set -e
  tail -n 40 "$POORTLOG"

  if [ $GROEN -eq 0 ]; then
    zeg "poging $poging is door de poort"
    echo "wat=$WAT" >> "$UIT"
    [ -n "$TITEL" ] && echo "titel=$TITEL" >> "$UIT"
    [ -n "$LES" ] && echo "les=1" >> "$UIT"
    echo "pogingen=$poging" >> "$UIT"
    exit 0
  fi

  # ---- 4. afgekeurd: het bewijs vasthouden ----
  # Hier zat het gat. De oude workflow kopieerde de kapotte poging naar /tmp/mislukt en liet hem
  # daar staan; die map wordt met de runner opgeruimd. De stap die het bewijs moest bewaren, gooide
  # het dus weg, en 's ochtends was de enige informatie "er is niets gepusht".
  MAP="$BEWIJS/poging-$poging"
  mkdir -p "$MAP"
  git diff > "$MAP/wat-de-bot-schreef.diff" 2>/dev/null || true
  cp "$POORTLOG" "$MAP/poort.log" 2>/dev/null || true
  cp index.html versie.txt "$MAP/" 2>/dev/null || true
  cp tools/curriculum-laatste.json tools/avondrun-hart.json "$MAP/" 2>/dev/null || true
  cp -r test/uitvoer "$MAP/schermen" 2>/dev/null || true

  {
    echo "### Poging $poging kwam niet door de poort"
    echo ""
    echo '```'
    grep -E "^  ROOD|^POORT DICHT|GEFAALD" "$POORTLOG" || echo "(geen rode suites in het log; kijk in het artefact)"
    echo '```'
  } >> "$SAMENVATTING"

  # v23.241: en de hartslag zegt vanaf nu WELKE proef dichtging. Drie nachten stond er drie keer
  # dezelfde zin ("de poort ging dicht op wat de bot schreef"), terwijl de twee regels die het
  # antwoord waren in dit logboek stonden. Een controle die wel afgaat maar niet vertelt wat hij zag,
  # is de helft van een meldsysteem.
  node tools/hartslag-poort.js "$POORTLOG" tools/avondrun-hart.json || true
  cp tools/avondrun-hart.json "$MAP/avondrun-hart.json" 2>/dev/null || true

  zeg "afgekeurd. Bewijs staat in $MAP"

  # ---- 5. de poging terugdraaien en opnieuw ----
  # Zonder dit zou de volgende poging op de kapotte tekst verder bouwen, en zouden de id's
  # doorlopen. Terugdraaien geeft dezelfde uitgangspositie en dus dezelfde id's, met nieuwe inhoud.
  git checkout -- .
  # Behalve de hartslag. Die gaat over vannacht en niet over de vorige poging, en zonder deze regel
  # draai je hem terug naar die van gisteren: dan staat er 's ochtends een meting van de verkeerde
  # nacht, en dat is precies het soort halve waarheid dat deze reparatie moest wegnemen.
  cp "$MAP/avondrun-hart.json" tools/avondrun-hart.json 2>/dev/null || true
  poging=$((poging + 1))
done

zeg ""
zeg "Alle $MAX_POGINGEN pogingen zijn afgekeurd. Er is niets gepusht."
echo "wat=afgekeurd" >> "$UIT"
echo "pogingen=$MAX_POGINGEN" >> "$UIT"
exit 1
