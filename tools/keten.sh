#!/bin/sh
# Hoe ver draagt een uitnodiging?
#
# Stefan, 15 aug, over wie er straks binnenkomt: "voor onbekende mensen die straks via Linkedin
# binnen komen, en zei nodig op hun beur weer mensen uit en die nodigen weer mensen uit etc."
#
# Bij zo'n ketting is er precies één getal dat telt, en dat heet k:
#
#     k = starters in generatie n+1, gedeeld door starters in generatie n
#
# Wat de uitkomsten betekenen:
#
#     k = 0      niemand nodigde iemand uit die bleef. Je hebt geen ketting, je hebt een post.
#     k = 0,4    100 mensen van LinkedIn leveren er in totaal ongeveer 167 op. Twee derde gratis
#                groei bovenop je eigen werk. Dit is een goede uitkomst en het normale geval.
#     k = 1      elke generatie is even groot. Vrijwel niemand haalt dit.
#     k > 1      oneindige groei. Dit haalt bijna niemand, ook niet de bedrijven waarvan je denkt
#                dat ze het halen.
#
# GEBRUIK
#     export ADMIN_KEY="dezelfde sleutel als in GitHub Secrets"
#     sh tools/keten.sh
#
# WAT JE ZIET
#     gen        0 is iedereen die op eigen kracht binnenkwam. 1 is uitgenodigd door iemand uit 0.
#     starters   hoeveel er in die generatie echt iets deden (aanmelden zonder iets doen telt niet)
#     dag2       hoeveel daarvan de dag erna terugkwamen
#     week       hoeveel daarvan binnen zeven dagen ooit terugkwamen
#     bracht     hoeveel van hen zelf iemand hebben binnengehaald die bleef
#     k          hoeveel deze generatie er opleverde in de volgende
#
# WAAROM PER GENERATIE EN NIET IN TOTAAL
# Een totaal kan er prima uitzien terwijl generatie 2 nul is. Dan heb je geen ketting maar één goede
# LinkedIn-post, en dat is een heel ander bedrijf met een heel ander plan. Je ziet dat alleen als je
# de generaties uit elkaar houdt.
#
# WAT JE NIET MOET DOEN
# Hier naar kijken voordat generatie 1 tijd heeft gehad. k van de onderste generatie is per definitie
# te laag: die mensen hebben nog niemand kunnen uitnodigen. Wacht twee weken, en vergelijk dan de
# bovenste rijen met elkaar.
#
# EN LET OP DE KOLOM DAG2
# Als generatie 1 slechter blijft hangen dan generatie 0, dan werkt de uitnodiging wel en de app
# niet: mensen komen binnen uit beleefdheid tegenover degene die vroeg, niet uit interesse. Dan is
# meer uitnodigen precies het verkeerde antwoord.
set -e

BASIS="${API_BASIS:-https://espanol-qbm8.onrender.com}"

if [ -z "$ADMIN_KEY" ]; then
  echo "Zet eerst ADMIN_KEY. Dat is dezelfde sleutel die in GitHub Secrets staat."
  echo "    export ADMIN_KEY=\"...\""
  exit 1
fi

UIT=$(curl -sS "$BASIS/api/admin/keten?key=$ADMIN_KEY")

echo "$UIT" | node -e '
let ruw = "";
process.stdin.on("data", d => ruw += d);
process.stdin.on("end", () => {
  let j;
  try { j = JSON.parse(ruw); } catch(e){ console.log("Geen JSON terug:\n" + ruw.slice(0,300)); process.exit(1); }
  if (!j.ok) { console.log("De server zegt nee: " + (j.error || ruw.slice(0,200))); process.exit(1); }
  const r = j.perGeneratie || [];
  if (!r.length) { console.log("Nog geen enkele starter. Dat is geen fout, dat is dag nul."); return; }
  const pad = (s,n) => String(s).padEnd(n);
  console.log("");
  console.log("gen   starters   dag2          week          bracht    k");
  r.forEach(x => {
    console.log(pad(x.generatie, 6) + pad(x.starters, 11) +
      pad(x.terugDag2 + " (" + x.pctDag2 + "%)", 14) +
      pad(x.terugWeek + " (" + x.pctWeek + "%)", 14) +
      pad(x.brachtIemand, 10) + (x.k === null ? "-" : x.k));
  });
  console.log("");
  if (r.length === 1) {
    console.log("Eén generatie. Er is nog geen ketting: niemand heeft iemand binnengehaald die bleef.");
  } else {
    const k = r[0].k;
    console.log("Generatie 0 leverde " + k + " op in generatie 1." + (k >= 1
      ? " Dat is hoog. Kijk of het klopt voordat je het gelooft: bij kleine aantallen is één actieve uitnodiger genoeg om dit getal te maken."
      : " Elke generatie is dus kleiner, en dat is het normale geval. Bij " + k + " levert elke 100 mensen die je zelf binnenhaalt er ongeveer " + Math.round(100/(1-k)) + " op in totaal."));
  }
  if (j.wezen) console.log("\n" + j.wezen + " mensen hangen aan iemand die zelf nooit iets deed; die staan hierboven in generatie 0.");
  console.log("\nDe onderste generatie is altijd te laag: die mensen hebben nog niemand kunnen uitnodigen.");
});
'
