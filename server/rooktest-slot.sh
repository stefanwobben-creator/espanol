#!/bin/sh
# Rooktest voor de sloten op /api/sync, /api/log en /api/ai/* (13 aug).
#
# Wat hier bewezen wordt, en waarom het een test verdient: een slot dat te streng staat sluit echte
# gebruikers buiten, en dat merk je pas als iemand zegt dat zijn voortgang weg is. De vier dingen
# hieronder zijn precies de vier manieren waarop dit mis kan gaan.
#
#   1. zonder Origin gaat de deur dicht (dat is de rommel die we buiten willen)
#   2. mét de juiste Origin gaat de deur open (dat is de app zelf)
#   3. GET /api/state blijft open, want die is beveiligd met de sync-code en een browser stuurt
#      bij een GET niet altijd een Origin mee
#   4. POORT_UIT=1 zet alles weer open, binnen een minuut, zonder opnieuw uitrollen
#
# Er is geen database nodig. De test start de server met een onbereikbare DATABASE_URL: een verzoek
# dat "database-fout" oplevert is er langs het slot gekomen, en dat is precies wat we willen weten.
#
# Draaien:  sh server/rooktest-slot.sh
set -e
HIER=$(cd "$(dirname "$0")" && pwd)
PORT_A=10079
PORT_B=10080
H="http://127.0.0.1:$PORT_A"
O="https://vamos.stefanwobben.nl"
TMP=$(mktemp -d)
trap 'kill $PID_A $PID_B 2>/dev/null; rm -rf "$TMP" "$HIER/_rooktest-slot-tmp.js"' EXIT

# init() praat met de database voordat hij luistert; die stap slaan we over.
python3 - "$HIER" <<'PY'
import io, sys, os
hier = sys.argv[1]
s = io.open(os.path.join(hier, "index.js"), encoding="utf-8").read()
oud = '''const port = process.env.PORT || 10000;
init()
  .then(() => app.listen(port, () => console.log("¡Vamos! API draait op poort " + port)))
  .catch((e) => { console.error("init faalde:", e); process.exit(1); });'''
if oud not in s:
    print("server/index.js eindigt niet zoals verwacht; deze rooktest is verouderd")
    sys.exit(1)
s = s.replace(oud, '''const port = process.env.PORT || 10000;
app.listen(port, () => console.log("rooktest luistert op " + port));''')
io.open(os.path.join(hier, "_rooktest-slot-tmp.js"), "w", encoding="utf-8").write(s)
PY

export DATABASE_URL="postgres://x:x@127.0.0.1:5432/bestaatniet"
PORT=$PORT_A node "$HIER/_rooktest-slot-tmp.js" > "$TMP/a.log" 2>&1 & PID_A=$!
PORT=$PORT_B POORT_UIT=1 node "$HIER/_rooktest-slot-tmp.js" > "$TMP/b.log" 2>&1 & PID_B=$!
sleep 2

n=0; f=0
zeg() { n=$((n+1)); if [ "$2" = "$3" ]; then echo "  ✓ $1 ($2)"; else echo "  ✗ $1 :: verwacht $3, kreeg $2"; f=$((f+1)); fi; }
code() { curl -s -o "$TMP/uit.json" -w "%{http_code}" "$@"; }
veld() { python3 -c "import json;print(json.load(open('$TMP/uit.json')).get('$1','(geen)'))" 2>/dev/null || echo "(geen json)"; }
SYNC='{"code":"abcdefgh","name":"x","track":"beginner","state":{}}'
LOG='{"code":"abcdefgh","payload":{}}'

echo "-- 1. zonder Origin zit de deur dicht --"
zeg "POST /api/sync" "$(code -X POST -H 'content-type: application/json' -d "$SYNC" $H/api/sync)" "403"
zeg "  met een reden erbij" "$(veld reden)" "herkomst"
zeg "POST /api/log" "$(code -X POST -H 'content-type: application/json' -d "$LOG" $H/api/log)" "403"
zeg "POST /api/ai/check" "$(code -X POST -H 'content-type: application/json' -d '{"nl":"a","gegeven":"b"}' $H/api/ai/check)" "403"

echo "-- 2. mét de juiste Origin gaat hij open --"
zeg "POST /api/sync komt langs het slot" "$(code -X POST -H "origin: $O" -H 'content-type: application/json' -d "$SYNC" $H/api/sync)" "500"
zeg "  en strandt pas op de database" "$(veld error)" "database-fout"

echo "-- 3. GET /api/state blijft open --"
c=$(code $H/api/state/abcdefgh)
zeg "geen 403" "$([ "$c" = "403" ] && echo nee || echo ja)" "ja"

echo "-- 4. de teller weigert na 120 per uur --"
i=0
while [ $i -lt 200 ]; do
  c=$(code -X POST -H "origin: $O" -H 'content-type: application/json' -d "$SYNC" $H/api/sync)
  i=$((i+1))
  [ "$c" = "429" ] && break
done
zeg "er komt een 429" "$c" "429"
# Er ging er al één doorheen bij stap 2, dus de 120e in deze lus is de 121e in totaal.
zeg "  en dat is de 121e" "$i" "120"
zeg "  met reden" "$(veld reden)" "tempo"
c=$(code -X POST -H "origin: $O" -H 'content-type: application/json' -d "$LOG" $H/api/log)
zeg "log heeft een eigen teller" "$([ "$c" = "429" ] && echo nee || echo ja)" "ja"

echo "-- 5. de noodrem --"
c=$(code -X POST -H 'content-type: application/json' -d "$SYNC" http://127.0.0.1:$PORT_B/api/sync)
zeg "POORT_UIT=1 laat een verzoek zonder Origin door" "$([ "$c" = "403" ] && echo nee || echo ja)" "ja"
curl -s http://127.0.0.1:$PORT_B/health > "$TMP/uit.json"
zeg "en /health laat zien dat hij aanstaat" "$(python3 -c "import json;print(json.load(open('$TMP/uit.json'))['ai']['poortUit'])")" "True"

echo ""
echo "$((n-f))/$n goed"
[ $f -eq 0 ] || exit 1
