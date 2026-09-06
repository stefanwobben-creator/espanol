#!/bin/sh
# leveren.sh (6 sep, v23.247) - bouwt de patch voor deze ronde, en weigert als het nummer botst
#
# WAAROM DIT ER IS
#
# Elke ronde die ik aflever, lever ik als een patch: Stefan draait `git am` en heeft precies mijn
# boom. Dat ging tot nu toe met zes commando's die ik elke keer opnieuw intikte: fetchen, rebasen,
# format-patch, een wegwerp-werkmap, `git am` erin, en de twee bomen vergelijken.
#
# Op 6 september botste het versienummer: de avondrun publiceerde v23.245 terwijl mijn ronde met
# datzelfde nummer openstond. tools/versiehoger.js ziet dat, maar had geen plek om te draaien. Een
# controle zonder plek is een controle die je moet ONTHOUDEN, en dat is precies wat er die dag mis
# ging: ik keek langs de regel heen die het al zei.
#
#     Een regel die voor elke levering geldt, hoort door de levering zelf afgedwongen te worden.
#
# Dit script is die plek. Alles wat ik toch al deed, plus de drie controles ertussen, en er komt
# geen patch uit als er één rood is.
#
# GEBRUIK
#
#   sh tools/leveren.sh                   # naar ../lever/vamos-<versie>.patch
#   sh tools/leveren.sh --uit /pad        # ergens anders heen
#   sh tools/leveren.sh --basis <ref>     # tegen iets anders dan origin/main
#   sh tools/leveren.sh --zelftest
#
# Exitcodes:  0 = er ligt een geverifieerde patch   1 = een controle ging rood
#             2 = niets te leveren                  3 = de basis is niet te lezen
#
# ER IS GEEN --geen-fetch
#
# Die stond er even in, en de zelftest liet meteen zien waarom hij weg moest: zonder fetch meet de
# controle de origin/main die je TOEVALLIG nog had liggen, en meldt dan opgewekt "hoger dan wat er
# leeft" terwijl er iets nieuwers leeft. Dat is dezelfde vorm als de fout die deze ronde repareert:
# een controle die het verkeerde ding meet en groen wordt. Lukt het fetchen niet, dan kan deze
# levering niet nagerekend worden, en dan hoort er geen patch uit te komen.
#
# WAT HIJ NIET DOET
#
# De poort draaien. Die duurt een halfuur en hoort niet aan een levering vast te zitten; wat hier
# staat zijn de drie statische controles die in seconden klaar zijn. De poort blijft een aparte stap
# ervoor.
set -e

SCRIPT=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
WORTEL="${WORTEL:-$(cd "$(dirname "$0")/.." && pwd)}"
BASIS="${BASIS:-origin/main}"
UIT=""
ZELF=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --uit) UIT="$2"; shift 2 ;;
    --basis) BASIS="$2"; shift 2 ;;
    --zelftest) ZELF=1; shift ;;
    *) echo "onbekend argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$UIT" ] || UIT="$(dirname "$WORTEL")/lever"

leveren() {
  cd "$WORTEL"

  # 1. een schone werkmap, want een patch bevat commits en geen losse wijzigingen
  if [ -n "$(git status --porcelain)" ]; then
    echo "DE WERKMAP IS NIET SCHOON."
    git status --short | sed 's/^/  /'
    echo "Een patch bevat commits. Wat hier los staat, gaat niet mee en zou stil verdwijnen."
    return 1
  fi

  # 2. weten waar main staat
  if git remote get-url origin >/dev/null 2>&1; then
    git fetch origin --quiet || {
      echo "KAN NIET METEN: git fetch mislukt, dus wat hier origin/main heet kan verouderd zijn."
      echo "Zonder verse main is niet na te rekenen of dit nummer al vergeven is."
      return 3
    }
  fi
  git rev-parse --verify --quiet "$BASIS" >/dev/null || {
    echo "KAN NIET METEN: $BASIS bestaat niet in dit repository."
    return 3
  }

  # controleren en de uitvoer inspringen, MET behoud van de exitcode.
  #
  # Hier stond `node ... | sed 's/^/  /'` en daarachter `RES=$?`, en dat is de exitcode van sed. Die
  # is altijd 0. De hele nummercontrole was daarmee versiering: hij drukte netjes af dat het nummer
  # botste en liet de levering gewoon doorlopen. Precies dezelfde vorm als de fout die deze ronde
  # repareert, twintig regels verderop opnieuw gemaakt. Vandaar: eerst opvangen, dan afdrukken.
  stap() {
    KOP="$1"; shift
    echo "-- $KOP --"
    UIT_STAP=$("$@" 2>&1)
    RES=$?
    echo "$UIT_STAP" | sed 's/^/  /'
    return "$RES"
  }

  # 3. het nummer, VOORDAT er gerebased wordt.
  #
  # Deze controle heeft de rebase niet nodig: versie.txt hier tegen versie.txt op $BASIS is genoeg.
  # En hij hoort er juist vóór, want als de ander hetzelfde nummer heeft gepakt botsen precies die
  # twee regels bij het rebasen. Dan zou je "de rebase loopt vast" lezen waar het antwoord
  # "hernummer naar het volgende nummer" is. De zelftest liet dat meteen zien.
  stap "het nummer wijst één boom aan" node "$WORTEL/tools/versiehoger.js" --basis "$BASIS" || return $?

  # 4. erop rebasen, zodat de patch schoon toe te passen is op wat er nu leeft
  git rebase "$BASIS" >/dev/null 2>&1 || {
    echo "DE REBASE OP $BASIS LOOPT VAST."
    git rebase --abort >/dev/null 2>&1 || true
    echo "Los dat eerst met de hand op; een patch die niet op $BASIS past, is voor Stefan onbruikbaar."
    return 1
  }

  # 5. en de twee controles die pas na het rebasen iets zeggen over wat je aflevert
  stap "versie.txt en APP_VERSIE zeggen hetzelfde" node "$WORTEL/tools/versiegelijk.js" || return $?
  stap "de scriptblokken parseren" node "$WORTEL/tools/syntaxcheck.js" "$WORTEL/index.html" || return $?

  # 6. is er eigenlijk iets te leveren?
  AANTAL=$(git rev-list --count "$BASIS"..HEAD)
  if [ "$AANTAL" = "0" ]; then
    echo
    echo "Niets te leveren: HEAD staat gelijk met $BASIS."
    return 2
  fi

  # 7. de patch
  VERSIE=$(tr -d ' \n' < versie.txt)
  mkdir -p "$UIT"
  PATCH="$UIT/vamos-$VERSIE.patch"
  git format-patch "$BASIS" --stdout > "$PATCH"

  # 8. en meteen bewijzen dat hij doet wat hij belooft: in een wegwerp-werkmap vanaf $BASIS
  #    toepassen en de twee bomen vergelijken. Zonder deze stap is "hier is je patch" een bewering.
  PROEF="${TMPDIR:-/tmp}/leverproef-$$"
  rm -rf "$PROEF"
  git worktree add --detach "$PROEF" "$BASIS" >/dev/null 2>&1
  set +e
  ( cd "$PROEF" && git am "$PATCH" >/dev/null 2>&1 )
  AM=$?
  set -e
  MIJN=$(git rev-parse "HEAD^{tree}")
  HUN=$(cd "$PROEF" && git rev-parse "HEAD^{tree}" 2>/dev/null || echo geen)
  ( cd "$PROEF" && git am --abort >/dev/null 2>&1 ) || true
  git worktree remove --force "$PROEF" >/dev/null 2>&1 || true

  echo
  if [ "$AM" != "0" ]; then
    echo "DE PATCH PAST NIET SCHOON OP $BASIS (git am gaf $AM)."
    rm -f "$PATCH"
    return 1
  fi
  if [ "$MIJN" != "$HUN" ]; then
    echo "DE PATCH LEVERT EEN ANDERE BOOM DAN DIE HIER STAAT."
    echo "  hier : $MIJN"
    echo "  patch: $HUN"
    rm -f "$PATCH"
    return 1
  fi

  # De basis erbij, want een patch van meer dan één commit zegt niets over waar hij op past. Ik liep
  # daar bij de eerste echte levering meteen tegenaan: v23.246 was al naar Stefan gegaan, dus deze
  # patch (gebouwd vanaf main) bevat een commit die hij misschien al heeft. Dat hoort in de uitvoer
  # te staan en niet in mijn hoofd.
  echo "TREES GELIJK :: $AANTAL commit(s), $VERSIE"
  echo "past op     :: $BASIS = $(git rev-parse --short "$BASIS")"
  echo "$PATCH"
  return 0
}

# ---------------------------------------------------------------------------------------------
# de zelftest
#
# Bouwt een echt repository met een origin ernaast en zet daar de gevallen op die ertoe doen. De
# twee die deze ronde bestaansreden zijn, staan als CONTROLE gemarkeerd: die MOETEN rood worden,
# anders houdt dit script niets tegen.
# ---------------------------------------------------------------------------------------------
zelftest() {
  # set -e uit binnen de proef: hier is een niet-nul exitcode juist het onderwerp. Met set -e aan
  # stopte deze functie stilletjes bij het eerste geval dat rood HOORT te zijn, en dan telt hij de
  # helft van zijn eigen controles niet. Een proef die afbreekt op wat hij meet, meet niets.
  set +e
  FOUT=0
  ok() { if [ "$1" = "0" ]; then echo "  ok   $2"; else echo "  FOUT $2"; FOUT=$((FOUT + 1)); fi; }

  ECHTE=$(cd "$(dirname "$SCRIPT")/.." && pwd)
  W="${TMPDIR:-/tmp}/leverenproef-$$"
  rm -rf "$W"; mkdir -p "$W"

  git init -q --bare "$W/kaal.git"
  git init -q -b main "$W/repo"
  cd "$W/repo"
  git config user.email proef@proef
  git config user.name proef
  git remote add origin "$W/kaal.git"
  mkdir -p tools claude
  # de controles die leveren.sh aanroept horen in de proefrepo te staan, want ze meten die repo
  cp "$ECHTE/tools/versiehoger.js" "$ECHTE/tools/versiegelijk.js" "$ECHTE/tools/syntaxcheck.js" tools/
  printf '<html><body>\n<script>\nvar A = 1;\n</script>\n<script>\nvar APP_VERSIE = "v1.9";\n</script>\n</body></html>\n' > index.html
  echo "v1.9" > versie.txt
  git add -A; git commit -qm start; git push -q origin HEAD:main
  git branch -q --set-upstream-to=origin/main main 2>/dev/null || true

  ronde() {   # $1 = nieuw nummer, $2 = commitregel
    sed -i.bak "s/var APP_VERSIE = \"[^\"]*\"/var APP_VERSIE = \"$1\"/" index.html && rm -f index.html.bak
    echo "$1" > versie.txt
    echo "// $2" >> index.html
    git add -A; git commit -qm "$2"
  }

  echo "-- het gewone geval --"
  ronde v1.10 "mijn ronde"
  UITVOER=$(WORTEL="$W/repo" sh "$SCRIPT" --uit "$W/lever" 2>&1)
  RES=$?
  echo "$UITVOER" | sed 's/^/    /'
  ok "$RES" "de levering slaagt"
  [ -f "$W/lever/vamos-v1.10.patch" ]
  ok "$?" "de patch heet naar het versienummer (vamos-v1.10.patch)"
  echo "$UITVOER" | grep -q "TREES GELIJK"
  ok "$?" "en hij is nagerekend tegen origin/main (TREES GELIJK)"

  echo
  echo "-- DE BOTSING VAN 6 SEPTEMBER --"
  # main beweegt onder ons vandaan en neemt v1.11 in; mijn ronde staat op datzelfde nummer
  git clone -q -b main "$W/kaal.git" "$W/ander"
  ( cd "$W/ander" && git config user.email a@a && git config user.name a && \
    sed -i.bak 's/var APP_VERSIE = "[^"]*"/var APP_VERSIE = "v1.11"/' index.html && rm -f index.html.bak && \
    echo v1.11 > versie.txt && echo "// van de avondrun" >> index.html && \
    git add -A && git commit -qm "avondrun v1.11" && git push -q origin HEAD:main )
  ronde v1.11 "mijn ronde met hetzelfde nummer"
  UITVOER=$(WORTEL="$W/repo" sh "$SCRIPT" --uit "$W/lever" 2>&1)
  RES=$?
  echo "$UITVOER" | sed 's/^/    /'
  git fetch -q origin
  [ "$RES" != "0" ]
  ok "$?" "CONTROLE: de levering WEIGERT als het nummer al vergeven is (exit $RES)"
  echo "$UITVOER" | grep -q "AL VERGEVEN"
  ok "$?" "  en zegt waarom, met het nummer dat het wél moet worden"
  [ ! -f "$W/lever/vamos-v1.11.patch" ]
  ok "$?" "  CONTROLE: en er ligt geen patch onder dat nummer"

  echo
  echo "-- na hernummeren gaat hij wel door --"
  # Wat ik met de hand ook zou doen: opnieuw beginnen bovenop wat er leeft, met een vrij nummer.
  # (De rebase van de oude ronde botst hier echt, want beide schrijvers raakten dezelfde twee regels
  # aan. Dat is geen tekortkoming van de proef maar de reden waarom hernummeren de uitweg is.)
  git fetch -q origin; git reset -q --hard origin/main
  ronde v1.12 "mijn ronde, hernummerd"
  UITVOER=$(WORTEL="$W/repo" sh "$SCRIPT" --uit "$W/lever" 2>&1)
  RES=$?
  echo "$UITVOER" | sed 's/^/    /'
  ok "$RES" "met v1.12 boven de v1.11 van main slaagt dezelfde ronde wel (exit $RES)"
  [ -f "$W/lever/vamos-v1.12.patch" ]
  ok "$?" "  en daar ligt de patch"

  echo
  echo "-- een vuile werkmap --"
  echo "los werk" >> index.html
  UITVOER=$(WORTEL="$W/repo" sh "$SCRIPT" --uit "$W/lever" 2>&1); RES=$?
  { [ "$RES" != "0" ] && echo "$UITVOER" | grep -q "NIET SCHOON"; }
  ok "$?" "CONTROLE: los werk in de map wordt geweigerd (exit $RES)"
  git checkout -q -- index.html

  echo
  echo "-- versie.txt zonder APP_VERSIE --"
  echo v1.13 > versie.txt
  git add -A; git commit -qm "alleen versie.txt verzet"
  UITVOER=$(WORTEL="$W/repo" sh "$SCRIPT" --uit "$W/lever" 2>&1); RES=$?
  { [ "$RES" != "0" ] && echo "$UITVOER" | grep -q "GELIJK TE ZIJN"; }
  ok "$?" "CONTROLE: die twee uit elkaar laten lopen wordt geweigerd (exit $RES)"
  [ ! -f "$W/lever/vamos-v1.13.patch" ]
  ok "$?" "  CONTROLE: en er ligt geen patch onder dat nummer"
  git reset -q --hard HEAD~1

  echo
  echo "-- niets te leveren --"
  git push -q origin HEAD:main 2>/dev/null
  git fetch -q origin
  UITVOER=$(WORTEL="$W/repo" sh "$SCRIPT" --uit "$W/lever" 2>&1); RES=$?
  echo "$UITVOER" | sed 's/^/    /'
  [ "$RES" = "2" ]
  ok "$?" "HEAD gelijk aan main geeft exit 2, niet een lege patch (exit $RES)"

  cd /
  rm -rf "$W"
  echo
  if [ "$FOUT" != "0" ]; then echo "$FOUT fout"; return 1; fi
  echo "alles goed"
  return 0
}

# ---------------------------------------------------------------------------------------------
export SCRIPT

if [ "$ZELF" = "1" ]; then
  zelftest
  exit $?
fi

leveren
exit $?
