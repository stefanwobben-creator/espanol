#!/bin/sh
# Komen ze terug op dag 2?
#
# Stefan, 13 aug, op de vraag wat hij als eerste van een vreemde wil weten: "terugkomt op dag 2".
#
# Er hoefde niets gebouwd te worden om dat te weten. S.xp is in de app een map van datum naar
# punten, dus de sleutels zijn precies de dagen waarop iemand iets heeft gedaan, en /api/sync zet
# die hele state op de server. Het stond er dus al; het werd alleen nooit opgeteld.
#
# GEBRUIK
#     export ADMIN_KEY="dezelfde sleutel als in GitHub Secrets"
#     sh tools/terugkomst.sh
#
# WAT JE ZIET
#     dag1        de dag waarop een groep mensen begon
#     starters    hoeveel er die dag echt iets deden (aanmelden zonder iets doen telt niet mee)
#     dag2        hoeveel daarvan de dag erna terugkwamen
#     week        hoeveel daarvan binnen zeven dagen ooit terugkwamen
#
# WELK GETAL JE MOET GELOVEN
# Allebei, en ze zeggen iets anders. dag2 is de strenge: heeft de app een plek in iemands dag
# gekregen. week is de eerlijke voor wie vrijdagavond begint en zondag terugkomt. Zakt week, dan is
# er iets mis met de app. Zakt alleen dag2 terwijl week blijft, dan is er iets mis met het ritme:
# de herinnering, het moment van de dag, de lengte van de portie.
#
# WAT JE NIET MOET DOEN
# Dit op dag 1 openen en er iets uit concluderen. Met vijf starters is elk percentage ruis. Wacht
# tot er een week in staat en kijk dan naar de lijn, niet naar de laatste rij: de onderste rij is
# per definitie onvolledig, want die mensen hebben hun dag 2 nog niet gehad.
set -e

BASIS="${API_BASIS:-https://espanol-qbm8.onrender.com}"

if [ -z "$ADMIN_KEY" ]; then
  echo "Zet eerst ADMIN_KEY. Dat is dezelfde sleutel die in GitHub Secrets staat."
  echo "    export ADMIN_KEY=\"...\""
  exit 1
fi

UIT=$(curl -sS "$BASIS/api/admin/terugkomst?key=$ADMIN_KEY")

echo "$UIT" | node -e '
let ruw = "";
process.stdin.on("data", d => ruw += d);
process.stdin.on("end", () => {
  let j;
  try { j = JSON.parse(ruw); } catch(e){ console.log("Geen JSON terug:\n" + ruw.slice(0,300)); process.exit(1); }
  if (!j.ok) { console.log("De server zegt nee: " + (j.error || ruw.slice(0,200))); process.exit(1); }
  const r = j.perDag || [];
  if (!r.length) { console.log("Nog geen enkele starter. Dat is geen fout, dat is dag nul."); return; }
  console.log("");
  console.log("dag1         starters   dag2          week          dagen gem.");
  r.forEach(x => {
    const pad = (s,n) => String(s).padEnd(n);
    console.log(pad(String(x.dag1).slice(0,10), 13) + pad(x.starters, 11) +
      pad(x.terugDag2 + " (" + x.pctDag2 + "%)", 14) +
      pad(x.terugWeek + " (" + x.pctWeek + "%)", 14) + x.dagenGem);
  });
  const t = j.totaal || {};
  console.log("");
  console.log("alles bij elkaar: " + t.starters + " starters, " + t.dag2 + " terug op dag 2 (" +
    t.pctDag2 + "%), " + t.week + " binnen een week (" + t.pctWeek + "%)");
  console.log("");
  console.log("De onderste rij is altijd onvolledig: die mensen hebben hun dag 2 nog niet gehad.");
});
'
