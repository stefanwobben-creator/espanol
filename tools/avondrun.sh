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

poging=1
while [ "$poging" -le "$MAX_POGINGEN" ]; do
  zeg ""
  zeg "=================== poging $poging van $MAX_POGINGEN ==================="

  # ---- 1. genereren ----
  # shellcheck disable=SC2086
  node tools/curriculum.js $VLAGGEN

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

  if [ -f tools/curriculum-laatste.json ] && \
     node -e "process.exit(require('./tools/curriculum-laatste.json').nieuweLes ? 0 : 1)"; then
    WAT="nieuwe-les"
    TITEL=$(node -e "console.log(require('./tools/curriculum-laatste.json').nieuweLes.titel)")
  else
    WAT="reparatie"
    TITEL=""
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
