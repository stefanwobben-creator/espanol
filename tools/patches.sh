#!/bin/sh
# Draait de patchscripts in claude/ op volgorde en stopt bij de eerste die faalt.
#
#   sh tools/patches.sh v23.50              # vanaf v23.50, op ~/espanol
#   sh tools/patches.sh v23.50 /pad/naar/map
#
# De beginversie is verplicht. De patches uit de oude doos hebben een andere aanroep (die nemen het
# bestand mee in plaats van de map) en zijn allang toegepast; "draai alles vanaf het begin" is dus
# geen zinnige opdracht en zou hier alleen maar op zijn bek gaan.
#
# Waarom dit bestaat, 12 augustus. Na een botsing met de avondrun is de tak opnieuw opgebouwd door
# zes patches achter elkaar in één blok te plakken. Twee ervan faalden, precies zoals ze horen te
# doen: met een melding welk anker ontbrak en exitcode 1. Maar in een blok van zes scrolt zo'n
# melding voorbij, en de rest liep gewoon door. Resultaat: v23.50 en v23.51 stonden niet in het
# bestand, de poort ging rood in CI, en er ging een uur in zoeken zitten.
#
# De patches waren niet stuk. De manier waarop ze gedraaid werden was stuk. Dit script maakt dat
# onmogelijk: één voor één, en bij de eerste fout houdt alles op.
set -e

VANAF="${1:-}"
WORTEL="${2:-$HOME/espanol}"

[ -n "$VANAF" ] || { echo "gebruik: sh tools/patches.sh v23.50 [map]"; exit 1; }

cd "$WORTEL"
WORTEL=$(pwd)          # absoluut, want de patchscripts plakken er index.html achter
[ -f index.html ] || { echo "geen index.html in $WORTEL"; exit 1; }

# sort -V zet v23.5 vóór v23.50 en v23.9 vóór v23.10, wat een gewone sort niet doet
LIJST=$(ls claude/patch-v*.py 2>/dev/null | sort -V)
[ -n "$LIJST" ] || { echo "geen patchscripts gevonden in claude/"; exit 1; }

BEGONNEN=0
for P in $LIJST; do
  if [ "$BEGONNEN" = "0" ]; then
    case "$P" in
      *"$VANAF"*) BEGONNEN=1 ;;
      *) continue ;;
    esac
  fi
  printf '%-34s ' "$(basename "$P")"
  UIT=$(python3 "$P" "$WORTEL" 2>&1) || {
    echo "GEFAALD"
    echo "$UIT" | sed 's/^/    /'
    echo
    echo "Gestopt bij $(basename "$P"). Alles ervóór is wél toegepast."
    exit 1
  }
  echo "$UIT" | tr '\n' ' ' | sed 's/  */ /g'
  echo
done

echo
node tools/syntaxcheck.js index.html
echo
echo "versie.txt :: $(cat versie.txt)"
