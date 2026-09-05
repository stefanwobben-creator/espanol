#!/bin/sh
# avondrun-leveren.sh (31 aug, v23.217) - wat deze run gemaakt heeft op main krijgen, zonder rebase.
#
# WAAROM DIT BESTAAT
#
# De avondrun eindigde met `git pull --rebase` en dan `git push`. Sinds 23 augustus mislukte die
# rebase elke nacht: acht runs achter elkaar met de melding
#
#     ::warning::rebase mislukt; hartslag en opnames blijven liggen tot de volgende run.
#
# en daarna exitcode 0. Groen dus, terwijl de hartslag en de opnames op de vloer bleven liggen.
# Gevolg, gemeten: tools/avondrun-hart.json op main stond acht dagen stil op 23 augustus, en in elke
# rode nacht staat "Audio: 42 ingesproken · 18.529 tekens" die daarna werden weggegooid. Ongeveer
# 148.000 ElevenLabs-tekens voor niets.
#
# TWEE DINGEN DIE HIER MISGINGEN, EN ZE ZIJN ALLEBEI ERGER DAN DE REBASE ZELF
#
# 1. De melding zei niet wat git zei. "rebase mislukt" is geen diagnose. De echte foutregel stond in
#    het staplogboek, en dat is alleen te lezen met een ingelogde sessie. Wie 's ochtends naar de
#    runpagina keek, zag acht keer dezelfde inhoudsloze zin. Dezelfde fout als "telling klopt niet:
#    sentences" van v23.216: een controle die wel afgaat maar niet vertelt wat hij zag.
# 2. Rebasen is het verkeerde gereedschap. Op deze main publiceren drie schrijvers: deze Action, de
#    geplande nachttaak, en de logboek-Action. Die laatste wordt door GitHub steeds later ingepland
#    (van 02:30 naar 13:01), dus main verschuift tegenwoordig middenin het venster van de avondrun.
#    Een bot die zijn eigen commits op een bewegende tak probeert te herspelen, vecht elke nacht een
#    gevecht dat hij niet hoeft te voeren.
#
# WAT DIT SCRIPT IN PLAATS DAARVAN DOET
#
# Wat deze run wil afleveren zijn geen commits maar BESTANDEN. Dus: bestanden apart zetten, verse
# main pakken, de bestanden erop leggen, één commit, pushen. Er valt niets te herspelen en dus niets
# te botsen. Wordt de push toch geweigerd omdat iemand er ondertussen weer overheen ging, dan begint
# het opnieuw met nog versere main. Drie pogingen.
#
# De mp3's van deze run staan niet in git en overleven `git reset --hard` gewoon. audio/stemmen.json
# staat er wel in, en daarvoor geldt de regel van v23.179: wat op main staat wint, wij vullen aan.
# Die samenvoeging gebeurt dus ná de reset, tegen de verse main, in plaats van tegen de main van drie
# uur geleden. Dat is niet alleen robuuster maar ook juister.
#
# EN ALS HET DAN TOCH MISLUKT
#
# Dan komt de foutregel van git in de melding te staan en eindigt dit script op 1. Een levering die
# stil wegvalt en groen blijft is precies hoe dit acht nachten kon duren.
#
# GEBRUIK
#     sh tools/avondrun-leveren.sh "<commitregel>" <pad> [<pad> ...]
#     sh tools/avondrun-leveren.sh --zelftest
set -u

# Allebei te overschrijven, en dat is niet voor de sier: de zelftest onderaan draait dit script
# tegen een wegwerprepository in plaats van tegen de echte. Zonder die knop zou de proef het
# gedrag van dit script niet kunnen aantonen zonder naar main te pushen, en een proef die je niet
# durft te draaien is geen proef.
WORTEL=${WORTEL:-$(cd "$(dirname "$0")/.." && pwd)}
POGINGEN=${POGINGEN:-3}

# ---------------------------------------------------------------------------------------------
# de levering
# ---------------------------------------------------------------------------------------------
leveren() {
  REGEL="$1"; shift
  BEWAAR="${TMPDIR:-/tmp}/avondrun-leveren-$$"
  rm -rf "$BEWAAR"; mkdir -p "$BEWAAR"

  # 1. de lading apart zetten, precies zoals hij nu in de werkmap staat
  for PAD in "$@"; do
    [ -e "$WORTEL/$PAD" ] || continue
    mkdir -p "$BEWAAR/$(dirname "$PAD")"
    cp -R "$WORTEL/$PAD" "$BEWAAR/$(dirname "$PAD")/"
  done

  N=1
  while [ "$N" -le "$POGINGEN" ]; do
    UIT=$(
      cd "$WORTEL" || exit 1
      git fetch origin main --quiet 2>&1 || exit 1

      # Staat er nog werk van een eerdere stap dat nooit gepusht is (bijvoorbeeld de reparatie die
      # direct live had gemoeten), dan mag de reset hieronder dat niet opruimen. Eerst proberen te
      # pushen; lukt dat niet, dan is dit geen levering maar een reddingsactie en stoppen we.
      EIGEN=$(git log --oneline FETCH_HEAD..HEAD 2>/dev/null | wc -l | tr -d ' ')
      if [ "$EIGEN" != "0" ]; then
        git push origin HEAD:main 2>&1 || exit 1
        git fetch origin main --quiet 2>&1 || exit 1
      fi

      # 2. verse main, met de mp3's van deze run er nog naast (die staan niet in git)
      git reset --hard FETCH_HEAD --quiet 2>&1 || exit 1

      # 3. de lading erop
      for PAD in "$@"; do
        [ -e "$BEWAAR/$PAD" ] || continue
        # het manifest is geen bestand maar een administratie: main wint, wij vullen aan (v23.179)
        if [ "$PAD" = "audio/stemmen.json" ]; then
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
        else
          mkdir -p "$(dirname "$PAD")"
          cp -R "$BEWAAR/$PAD" "$(dirname "$PAD")/"
        fi
      done

      git add -A "$@" 2>&1 || exit 1
      if git diff --cached --quiet; then echo "NIETSTELEVEREN"; exit 0; fi
      git commit -q -m "$REGEL" 2>&1 || exit 1
      git push origin HEAD:main 2>&1 || exit 1
      echo "GELEVERD"
    ) 2>&1
    CODE=$?

    case "$UIT" in
      *GELEVERD*)      echo "geleverd: $REGEL"; rm -rf "$BEWAAR"; return 0 ;;
      *NIETSTELEVEREN*) echo "niets te leveren"; rm -rf "$BEWAAR"; return 0 ;;
    esac

    echo "poging $N van $POGINGEN mislukt (code $CODE):"
    echo "$UIT" | sed 's/^/    /'
    N=$((N + 1))
    [ "$N" -le "$POGINGEN" ] && sleep $((N * 5))
  done

  # De foutregel gaat mee de melding in. Dít ontbrak acht nachten lang.
  KORT=$(echo "$UIT" | tr '\n' ' ' | cut -c1-300)
  echo "::warning::leveren mislukt na $POGINGEN pogingen: $KORT"
  rm -rf "$BEWAAR"
  return 1
}

# ---------------------------------------------------------------------------------------------
# de zelftest
#
# Bouwt een echt kaal repository met een kloon ernaast, laat main onder de kloon vandaan bewegen
# (precies wat de logboek-Action en de nachttaak elke nacht doen) en levert dan. Zonder deze proef
# is dit script een bewering.
# ---------------------------------------------------------------------------------------------
zelftest() {
  FOUT=0
  ok() { if [ "$1" = "0" ]; then echo "  ok   $2"; else echo "  FOUT $2"; FOUT=$((FOUT + 1)); fi; }

  W="${TMPDIR:-/tmp}/leverproef-$$"
  rm -rf "$W"; mkdir -p "$W"
  (
    cd "$W" || exit 1
    git init -q --bare kaal.git
    git init -q main-kant
    cd main-kant
    git config user.email proef@proef; git config user.name proef
    git remote add origin "$W/kaal.git"
    mkdir -p tools audio
    echo '{"wanneer":"oud"}' > tools/avondrun-hart.json
    echo '{"bestanden":{}}' > audio/stemmen.json
    echo "start" > index.html
    # versie.txt hoort in de proefrepo net zo goed onder versiebeheer te staan als in de echte, want
    # dat is precies waar de proef van afhangt: `git reset --hard` zet een GEVOLGD bestand terug op
    # main, en laat een ongevolgd bestand van de run gewoon staan. Zonder deze regel meet de proef
    # een repository die niet bestaat.
    echo "v0.1" > versie.txt
    git add -A; git commit -qm start; git push -q origin HEAD:main
  ) || { echo "  FOUT kon de proefrepo niet bouwen"; return 1; }

  # De kloon pas NA de eerste push, anders is hij leeg en bewijst de proef niets. En met -b main,
  # want een kaal repository dat met `git init` gemaakt is wijst met HEAD naar master; kloon je dat
  # zonder tak te noemen, dan krijg je een lege werkmap en een proef die nergens over gaat.
  git clone -q -b main "$W/kaal.git" "$W/run" >/dev/null 2>&1
  (cd "$W/run" && git config user.email bot@bot && git config user.name bot)
  [ -f "$W/run/tools/avondrun-hart.json" ] || { echo "  FOUT de proefkloon is leeg"; rm -rf "$W"; return 1; }

  # main beweegt onder ons vandaan, zoals de logboek-Action doet
  (cd "$W/main-kant" && echo "logboek" > logboek.txt && git add -A && git commit -qm "logboek" && git push -q origin HEAD:main)

  # deze run heeft iets gemaakt: een verse hartslag en een mp3 die niet in git staat
  echo '{"wanneer":"nieuw","gepubliceerd":true}' > "$W/run/tools/avondrun-hart.json"
  mkdir -p "$W/run/audio/dictado"
  echo "geluid" > "$W/run/audio/dictado/s999.mp3"

  UITVOER=$(cd "$W/run" && WORTEL="$W/run" POGINGEN=3 sh "$WORTEL_SCRIPT" "proef: hartslag en opnames" tools/avondrun-hart.json audio 2>&1)
  RES=$?
  echo "$UITVOER" | sed 's/^/    /'
  ok "$RES" "de levering slaagt terwijl main onderweg verschoven is"

  (cd "$W/main-kant" && git fetch -q origin main && git reset --hard -q FETCH_HEAD)
  [ "$(cat "$W/main-kant/tools/avondrun-hart.json" 2>/dev/null)" = '{"wanneer":"nieuw","gepubliceerd":true}' ]
  ok "$?" "de verse hartslag staat op main"
  [ -f "$W/main-kant/audio/dictado/s999.mp3" ]
  ok "$?" "de opname staat op main"
  [ -f "$W/main-kant/logboek.txt" ]
  ok "$?" "CONTROLE: en het werk van de andere schrijver is niet weggegooid"

  # v23.239: EN INDEX.HTML WORDT NIET GEKOPIEERD.
  #
  # Dit is het geval waarvoor deze ronde bestaat. Tot nu toe stond index.html niet in de levering,
  # want kopiëren zou alles wegvagen wat er tussendoor op main is gezet. Nu staat hij er wel in,
  # maar als LADING: de toevoeging van deze nacht wordt op verse main gelegd door
  # tools/curriculum-toepassen.js, en het bestand van de run raakt main niet aan.
  #
  # Deze proef bewijst de ROUTERING, niet de toepasser: die heeft zijn eigen zelftest en heeft de
  # echte index.html nodig, die hier niet staat. Vandaar een stukje dat opschrijft dát het is
  # aangeroepen en met 2 eindigt ("niets toe te passen"). Wat hier telt: main houdt de index.html
  # van de andere schrijver.
  mkdir -p "$W/run/tools"
  printf '%s\n' '#!/usr/bin/env node' \
    'require("fs").writeFileSync(process.env.PROEF_SPOOR, "aangeroepen");' \
    'process.exit(2);' > "$W/run/tools/curriculum-toepassen.js"
  SPOOR="$W/toepassen-aangeroepen"
  rm -f "$SPOOR"
  (cd "$W/main-kant" && echo "van de andere schrijver" > index.html && git add -A && \
     git commit -qm "andere schrijver raakt index.html aan" && git push -q origin HEAD:main)
  echo "wat de bot vannacht schreef" > "$W/run/index.html"
  echo "v99.99" > "$W/run/versie.txt"
  (cd "$W/run" && WORTEL="$W/run" PROEF_SPOOR="$SPOOR" POGINGEN=3 \
     sh "$WORTEL_SCRIPT" "proef: index als lading" index.html versie.txt tools/avondrun-hart.json >/dev/null 2>&1)
  ok "$?" "de levering slaagt met index.html erbij"
  [ -f "$SPOOR" ]
  ok "$?" "de lading wordt toegepast in plaats van het bestand gekopieerd"
  (cd "$W/main-kant" && git fetch -q origin main && git reset --hard -q FETCH_HEAD)
  [ "$(cat "$W/main-kant/index.html" 2>/dev/null)" = "van de andere schrijver" ]
  ok "$?" "CONTROLE: main houdt de index.html van de andere schrijver, niet die van de run"
  [ "$(cat "$W/main-kant/versie.txt" 2>/dev/null)" != "v99.99" ]
  ok "$?" "CONTROLE: en versie.txt van de run ook niet, want dat nummer hoort bij het toepassen"

  # tweede levering zonder dat er iets veranderd is: dat hoort geen lege commit op te leveren
  VOOR=$(cd "$W/main-kant" && git rev-parse HEAD)
  (cd "$W/run" && WORTEL="$W/run" sh "$WORTEL_SCRIPT" "proef: nog een keer" tools/avondrun-hart.json audio >/dev/null 2>&1)
  (cd "$W/main-kant" && git fetch -q origin main)
  NA=$(cd "$W/main-kant" && git rev-parse FETCH_HEAD)
  [ "$VOOR" = "$NA" ]
  ok "$?" "CONTROLE: een tweede levering zonder nieuws maakt geen lege commit"

  rm -rf "$W"
  if [ "$FOUT" != "0" ]; then echo "$FOUT fout"; return 1; fi
  echo "alles goed"
  return 0
}

# ---------------------------------------------------------------------------------------------
if [ "${1:-}" = "--zelftest" ]; then
  WORTEL_SCRIPT=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
  export WORTEL_SCRIPT
  zelftest
  exit $?
fi

if [ "$#" -lt 2 ]; then
  echo "gebruik: sh tools/avondrun-leveren.sh \"<commitregel>\" <pad> [<pad> ...]" >&2
  echo "         sh tools/avondrun-leveren.sh --zelftest" >&2
  exit 2
fi

leveren "$@"
