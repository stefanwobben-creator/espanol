#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.20: sterk en zwak gaat over het hele thema, niet alleen over wat je al hebt aangeraakt.

Stefan zag het meteen: "vrije tijd 100 procent" klopte niet. Het betekende dat de 22 woorden die hij
van dat thema had geoefend allemaal in de bovenste doos stonden, terwijl er nog honderd andere
vrije-tijd-woorden in de app kunnen liggen die hij nooit heeft gezien. Een thema kan dus op honderd
procent staan terwijl je er bijna niets van kent, en dan stuurt de lijst je precies de verkeerde kant
op: hij noemt je sterk waar je het minst hebt gedaan.

De fout zat in de noemer. Die was "de woorden van dit thema die je hebt aangeraakt". Nu is het "de
woorden van dit thema die de app je op jouw niveau kan aanbieden", en een woord dat je nooit hebt
gezien telt gewoon voor nul. Dan betekent honderd procent wat je verwacht: dit thema ken je.

De teller blijft dezelfde weging als het getal op Vandaag, dus de betekenis van een rij verandert
niet, alleen waar hij tegen afgezet wordt.

Wat er binnen de noemer valt: woorden van jouw niveau of lager (de poort bepaalt dat al voor je
dagportie), plus alles wat je al hebt aangeraakt. Dat laatste omdat een woord dat je via een spel of
het boek hebt gekregen bij je hoort, ook als het formeel boven je poort ligt. Woorden van drie
niveaus hoger tellen niet mee: daar afgerekend worden zou betekenen dat elk thema altijd rood staat.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "themaInBereik" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


rep(
    """var THEMA_MIN = 8;     // minder woorden en een percentage zegt niets""",
    """var THEMA_MIN = 8;     // minder woorden en een percentage zegt niets
/* v23.20. Welke woorden tellen mee in de noemer van een thema? Alles wat de app je op jouw niveau
   kan aanbieden, plus wat je al hebt aangeraakt. Dat tweede is er niet voor de netheid: via de
   spellen en het boek krijg je woorden die formeel boven je poort liggen, en die horen bij je zodra
   je ze hebt gehad. Woorden van drie niveaus hoger blijven erbuiten; daarop afgerekend worden zou
   elk thema permanent rood zetten en dan is de lijst geen stuurinformatie meer maar een verwijt. */
function themaInBereik(w, poort){
  if(S.srs[w.id]) return true;
  var n = 9;
  try { n = woordNiveau(w.id); } catch(e){ n = 9; }
  return n <= poort;
}""")

rep(
    """function zwakkePunten(){
  var perThema = {}, i, w, st, nm;
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    st = S.srs[w.id];
    if(!st || typeof st !== "object") continue;
    if(!themaMeetelt(w.tag)) continue;
    nm = themaSleutel(w.tag);
    perThema[nm] = perThema[nm] || {n:0, som:0};
    perThema[nm].n++;
    perThema[nm].som += krachtGewicht(st.box || 0);
  }
  var themas = [];
  for(nm in perThema){
    if(perThema[nm].n < THEMA_MIN) continue;
    themas.push({sleutel:nm, naam:themaToon(nm), n:perThema[nm].n,
                 kracht:Math.round(100 * perThema[nm].som / perThema[nm].n)});
  }""",
    """function zwakkePunten(){
  var perThema = {}, i, w, st, nm, poort = 0;
  try { poort = poortRang(); } catch(e){ poort = 0; }
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    if(!themaMeetelt(w.tag)) continue;
    if(!themaInBereik(w, poort)) continue;
    nm = themaSleutel(w.tag);
    perThema[nm] = perThema[nm] || {n:0, gehad:0, som:0};
    perThema[nm].n++;                                   // in de noemer, ook als je hem nooit zag
    st = S.srs[w.id];
    if(st && typeof st === "object"){
      perThema[nm].gehad++;
      perThema[nm].som += krachtGewicht(st.box || 0);   // ongezien telt voor nul, en dat is het punt
    }
  }
  var themas = [];
  for(nm in perThema){
    if(perThema[nm].n < THEMA_MIN) continue;
    themas.push({sleutel:nm, naam:themaToon(nm), n:perThema[nm].n, gehad:perThema[nm].gehad,
                 kracht:Math.round(100 * perThema[nm].som / perThema[nm].n)});
  }""")

# de rij op het scherm noemt nu ook hoeveel je er van gezien hebt
rep(
    """  function rij(x, eenheid){
    return "<div class='cijfRij'><div class='cijfW'>"+x.kracht+"%</div>"+
      "<div class='cijfT'>"+x.naam+"<span>"+x.n+" "+eenheid+"</span></div></div>";
  }""",
    """  /* v23.20: er staat nu bij hoeveel van het thema je al hebt gehad. Zonder dat getal is 12 procent
     niet te lezen: dat kan betekenen dat je alles hebt gezien en niets onthoudt, of dat je er net aan
     begonnen bent. Dat zijn twee heel verschillende adviezen. */
  function rij(x){
    return "<div class='cijfRij'><div class='cijfW'>"+x.kracht+"%</div>"+
      "<div class='cijfT'>"+x.naam+"<span>"+
        ct(x.gehad+" van de "+x.n+" woorden gehad", x.gehad+" of "+x.n+" words seen")+
      "</span></div></div>";
  }""")

rep(
    """      sterk.map(function(x){ return rij(x, ct("woorden","words")); }).join("")+"</div>"+""",
    """      sterk.map(function(x){ return rij(x); }).join("")+"</div>"+""")
rep(
    """      zwak.map(function(x){ return rij(x, ct("woorden","words")); }).join("")+"</div>";""",
    """      zwak.map(function(x){ return rij(x); }).join("")+"</div>";""")

rep(
    """      ct("Hoe ver je woorden per thema in de doosjes staan, met dezelfde weging als het getal op "+
         "Vandaag. Niet het aantal fouten: een thema dat je vaak oefent verzamelt vanzelf de meeste "+
         "fouten, en dan lijkt oefenen een zwakte.",
         "How far your words sit in the boxes per topic, weighted the same way as the number on "+
         "Today. Not the number of mistakes: a topic you practise a lot collects the most mistakes, "+
         "which would make practice look like a weakness.")+"</p>";""",
    """      ct("Van alle woorden die dit thema op jouw niveau heeft: hoe ver staan ze in de doosjes. "+
         "Woorden die je nog nooit zag tellen voor nul, dus honderd procent betekent dat je het thema "+
         "echt kent. Niet het aantal fouten geteld: een thema dat je vaak oefent verzamelt vanzelf de "+
         "meeste fouten, en dan lijkt oefenen een zwakte.",
         "Of all the words this topic has at your level: how far they sit in the boxes. Words you "+
         "have never seen count as zero, so a hundred percent means you really know the topic. Not "+
         "counted on mistakes: a topic you practise a lot collects the most mistakes, which would "+
         "make practice look like a weakness.")+"</p>";""")

rep('var APP_VERSIE = "v23.19";', 'var APP_VERSIE = "v23.20";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.20 toegepast op", PAD)
