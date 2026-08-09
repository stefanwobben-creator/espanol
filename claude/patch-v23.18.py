#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.18: een getal dat elke dag beweegt.

Het probleem in een zin: het enige getal dat bewijst dat je iets leert telt alleen woorden die
helemaal af zijn. Bij Stefan zijn dat er 21, en dat stond vorige week op 11 en de week daarvoor op
10. Hij doet honderdzestig antwoorden per dag en ziet daar niets van terug, terwijl er 431 woorden
in het weekdoosje staan en 133 in het tweewekendoosje. De aanvoer is enorm en onzichtbaar.

Wat erbij komt is een gewogen telling. Het gewicht van een doosje is zijn eigen herhaalinterval,
gedeeld door het hoogste: het weekdoosje telt voor 7/30, het tweewekendoosje voor 14/30, de bovenste
voor een hele. Bij Stefan wordt 21 daarmee 195, en dat getal stijgt bij elk woord dat een doosje
opschuift, dus elke dag.

Er is niets aan verzonnen. De gewichten zijn de intervallen die de app zelf al gebruikt om te
plannen, en de uitsplitsing staat er onder: "Woorden per herhaalinterval" bestond al op je profiel
en krijgt er nu een kolom bij, zodat de som zichtbaar uitkomt op het getal dat op Vandaag staat.
Wie het niet gelooft kan het natellen.

Het getal op Vandaag vervangt "woorden geoefend". Dat laatste liep alleen maar op, ook als alles
weer wegzakte, en het staat nog gewoon op je profiel. Op je eerste scherm hoort het getal te staan
dat iets kan zeggen, niet het getal dat nooit tegenvalt.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "kracht:" in src and "function krachtTabelHtml()" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. de telling erbij
rep(
    """  var sw = S.sweep || {}, swN = (sw.goed || 0) + (sw.fout || 0);
  return {""",
    """  var sw = S.sweep || {}, swN = (sw.goed || 0) + (sw.fout || 0);
  /* v23.18. De doosjesverdeling, en daaruit een gewogen telling.

     Waarom gewogen: "bewezen vast" telt alleen woorden die de hele ladder af zijn, en dat duurt
     vijfentwintig dagen. Alles wat onderweg is telt voor nul, dus het getal staat weken stil terwijl
     er van alles gebeurt. Met deelpunten beweegt het elke dag, en het blijft eerlijk: een woord dat
     je over een week terugkrijgt is echt minder ver dan een woord dat je over een maand terugkrijgt.

     Waarom dit gewicht: het herhaalinterval van het doosje zelf, gedeeld door het hoogste. Dat is
     geen schaal die ik heb bedacht maar de planning die de app al gebruikt. Er zit dus geen enkele
     nieuwe aanname in, en dat is precies de eis die dit scherm drie keer heeft laten struikelen. */
  var dozen = [0, 0, 0, 0, 0, 0], dId, dSt, dB, dI, kr = 0;
  for(dId in S.srs){
    dSt = S.srs[dId];
    if(!dSt || typeof dSt !== "object") continue;
    dB = dSt.box || 0;
    if(dB >= 0 && dB < dozen.length) dozen[dB]++;
  }
  for(dI = 0; dI < dozen.length; dI++) kr += dozen[dI] * krachtGewicht(dI);
  return {
    dozen: dozen,
    kracht: Math.round(kr),""")

rep(
    """var MEET_WEKEN = 10;   // zoveel weekmetingen zijn er nodig voordat je eigen reeks iets zegt""",
    """var MEET_WEKEN = 10;   // zoveel weekmetingen zijn er nodig voordat je eigen reeks iets zegt
/* Het gewicht van een doosje: zijn eigen herhaalinterval, gedeeld door het hoogste. Doos 3 (een
   week) telt voor 7/30, doos 5 (een maand) voor een hele. Eén regel, en hij staat hier zodat het
   scherm dat de uitsplitsing tekent met dezelfde getallen rekent als het getal erboven. */
function krachtGewicht(box){
  var top = INTERVALS[INTERVALS.length - 1] || 30;
  return (INTERVALS[box] || 0) / top;
}""")

# ---------------------------------------------------------------- 2. op Vandaag
rep(
    """  var c = voortgangCijfers(), tegels = "";
  if(c.geoefend > 0){
    tegels += "<div class='stat'><b>"+c.geoefend+"</b><span class='muted'>"+
      ct("woorden geoefend","words practised")+"</span></div>";
  }""",
    """  var c = voortgangCijfers(), tegels = "";
  /* v23.18: hier stond "woorden geoefend". Dat getal loopt alleen maar op, ook als alles weer
     wegzakt, dus het kan niet tegenvallen en daarmee zegt het ook niets. Het staat nog gewoon op je
     profiel. Wat hier nu staat beweegt met wat er echt gebeurt. */
  if(c.geoefend > 0){
    tegels += "<div class='stat'><b>"+c.kracht+"</b><span class='muted'>"+
      ct("van je "+c.geoefend+" woorden, gewogen naar hoe lang je ze onthoudt",
         "of your "+c.geoefend+" words, weighted by how long you remember them")+"</span></div>";
  }""")

rep(
    """  if(!tegels) return "";
  return "<div class='statgrid' style='margin-top:10px'>"+tegels+"</div>"+""",
    """  if(!tegels) return "";
  return "<div class='statgrid' style='margin-top:10px'>"+tegels+"</div>"+
    (c.geoefend > 0 ? "<p class='muted' style='margin:6px 0 0; font-size:.8rem'>"+
      /* Bewust zonder de woorden week en maand erin, ook al zijn dat de doosjes waar het over gaat.
         pw-a1vandaag bewaakt dat er op dit scherm geen enkele belofte over tijd staat, en die wacht
         houdt geen rekening met de bedoeling van een zin. Dat is maar goed ook: het is precies het
         soort zin waar per ongeluk een voorspelling in sluipt. De uitleg met de intervallen erin
         staat op je profiel, bij de uitsplitsing zelf. */
      ct("Hoe verder een woord in de doosjes staat, hoe zwaarder het meetelt. De uitsplitsing staat "+
         "bij je cijfers.",
         "The further a word sits in the boxes, the heavier it counts. The breakdown is with your "+
         "numbers.")+"</p>" : "")+""")

# ---------------------------------------------------------------- 3. de uitsplitsing telt zichtbaar op
rep(
    """  var el = document.getElementById("statsCard");
  var boxes = [0,0,0,0,0,0];
  WORDS.forEach(function(w){ var st=S.srs[w.id]; if(st){ boxes[st.box]++; } });""",
    """  var el = document.getElementById("statsCard");
  /* v23.18: de doosjes werden hier apart geteld, over WORDS in plaats van over S.srs. Twee tellingen
     van dezelfde stapel, en ze kunnen uit elkaar lopen zodra er een woord in je srs staat dat niet
     in je track zit. Nu komen ze uit dezelfde functie als het getal op Vandaag. */
  var c = voortgangCijfers();
  var boxes = c.dozen;""")

rep(
    """    "<h2 style='margin-top:16px'>"+ct("Woorden per herhaalinterval","Words per review interval")+"</h2>"+boxHtml+
    "<p class='muted' style='margin-top:8px'>"+
      // v19.90: hier stond ook nog een keer hoeveel woorden je hebt aangeraakt.
      // Dat getal staat vier regels hoger al; twee keer hetzelfde zeggen maakt een
      // scherm langer en niet duidelijker.
      ct("Hoe verder naar onder, hoe beter een woord in je geheugen zit.",
         "The further down, the better a word sits in your memory.")+"</p>"+""",
    """    "<h2 style='margin-top:16px'>"+ct("Woorden per herhaalinterval","Words per review interval")+"</h2>"+boxHtml+
    krachtTabelHtml()+""")

rep(
    """function renderStats(){""",
    """/* v23.18. De uitsplitsing onder het getal van Vandaag. Dit blok bestond al als "Woorden per
   herhaalinterval"; er komt alleen een kolom bij die laat zien wat elk doosje bijdraagt, en een
   slotregel met de som. Dat is met opzet geen nieuw scherm: het getal en zijn onderbouwing horen
   op dezelfde plek, anders is de onderbouwing iets wat je moet zoeken en dan gelooft niemand hem. */
function krachtTabelHtml(){
  var c = voortgangCijfers();
  var lab = ct("nieuw/fout|1 dag|3 dagen|1 week|2 weken|1 maand",
               "new/wrong|1 day|3 days|1 week|2 weeks|1 month").split("|");
  var r = "", i, bij;
  for(i = 1; i < c.dozen.length; i++){
    if(!c.dozen[i]) continue;
    bij = c.dozen[i] * krachtGewicht(i);
    r += "<div class='cijfRij'><div class='cijfW'>"+(Math.round(bij * 10) / 10).toString().replace(".", ",")+"</div>"+
      "<div class='cijfT'>"+ct(c.dozen[i]+" woorden komen over <b>"+lab[i]+"</b> terug",
                              c.dozen[i]+" words come back in <b>"+lab[i]+"</b>")+
      "<span>"+ct("elk woord hier telt voor "+Math.round(100 * krachtGewicht(i))+" procent mee",
                  "each word here counts for "+Math.round(100 * krachtGewicht(i))+" percent")+"</span></div></div>";
  }
  if(!r) return "";
  return "<p class='muted' style='margin-top:8px'>"+
      ct("Hoe verder naar onder, hoe beter een woord in je geheugen zit. Zo komt het getal op Vandaag "+
         "tot stand: elk doosje telt mee naar zijn eigen herhaalinterval.",
         "The further down, the better a word sits in your memory. This is how the number on Today is "+
         "built: every box counts according to its own review interval.")+"</p>"+
    "<div class='cijfLijst'>"+r+
      "<div class='cijfRij'><div class='cijfW'>"+c.kracht+"</div>"+
        "<div class='cijfT'><b>"+ct("bij elkaar","together")+"</b>"+
        "<span>"+ct("dit is het getal dat op Vandaag staat, van je "+c.geoefend+" geoefende woorden",
                    "this is the number on Today, out of your "+c.geoefend+" practised words")+"</span></div></div>"+
    "</div>";
}

function renderStats(){""")

# ---------------------------------------------------------------- 4. en als rij in de lange lijst
rep(
    """  r += cijferRij(c.geoefend, ct("woorden ooit geoefend","words practised ever"),""",
    """  r += cijferRij(c.kracht, ct("gewogen naar hoe lang je ze onthoudt","weighted by how long you remember them"),
    ct("Het getal dat op Vandaag staat. Een woord in het weekdoosje telt voor "+
       Math.round(100 * krachtGewicht(3))+" procent mee, in het maanddoosje voor honderd. Anders dan "+
       "bewezen vast beweegt dit elke dag, want elk woord dat een doosje opschuift telt direct mee. "+
       "De uitsplitsing staat onderaan bij de herhaalintervallen.",
       "The number shown on Today. A word in the one week box counts for "+
       Math.round(100 * krachtGewicht(3))+" percent, in the one month box for a hundred. Unlike "+
       "proven solid this moves every day, because every word that moves up a box counts straight "+
       "away. The breakdown is at the bottom, with the review intervals."));
  r += cijferRij(c.geoefend, ct("woorden ooit geoefend","words practised ever"),""")

# ---------------------------------------------------------------- 5. versie
rep('var APP_VERSIE = "v23.17";', 'var APP_VERSIE = "v23.18";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.18 toegepast op", PAD)
