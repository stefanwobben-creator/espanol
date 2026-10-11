#!/usr/bin/env python3
# v23.255 - de grammatica krijgt doorstroom, en de leerrij roteert.
#
# Stefan: "ik doe nu vaak de woordjes en ook grammatica komt voorbij (alhoewel ik bij grammatica nog
# wel het idee heb dat dit beter kan). Misschien hier ook dagelijks een lesje doen en dan direct
# toetsen en oude grammatica volgens spaced repetition toetsen. Ik blijf nu te lang hangen, een klein
# slordigheidsfoutje en ik blijf hangen in de grammatica les."
#
# Nagerekend voordat er iets veranderde. 31 onderwerpen met samen 159 patroondoosjes (v23.228) plus
# 31 "in een echte zin"-doosjes is 190 doosjes, en elk doosje heeft vijf schone beurten nodig om
# GRAM_BOX uit te lopen. De dagles gaf er een leerbeurt en soms een onderhoudsbeurt.
#
# Een jaar nagespeeld met de regels van deze app (wachtrij oplopend op doos, promotie geblokkeerd bij
# een misser, negentig procent goed per vraag, twee vragen per beurt):
#
#     2 beurten per dag      24 van 190 doosjes op doos 5    820 beurten    4,3 per doosje per jaar
#     4 beurten per dag     185 van 190 doosjes op doos 5   1677 beurten    8,8 per doosje per jaar
#     8 beurten per dag     185 van 190 doosjes op doos 5   2325 beurten
#
# Vier beurten per doosje per jaar, en je hebt er vijf nodig. Dat is het hangen, en het is rekenkunde
# en geen gevoel. Let ook op wat er NIET uit komt: met de slordigheidsregel van v23.254 erbij wordt
# het 21 in plaats van 24. Die ingreep is goed maar raakt dit knelpunt niet, want hoe diep je valt
# doet er niet toe als je vier keer per jaar langskomt.
#
# En boven de vier houdt het op (185 tegenover 185), want een doosje klimt sinds v23.225 hoogstens
# een stap per dag. Meer vragen over hetzelfde leveren niets op; meer verschillende patronen wel.
#
# Twee ingrepen, en de tweede is de belangrijkste.
import io, sys

P = "index.html"
s = io.open(P, encoding="utf-8").read()

if "v23.255" in s:
    print("al gepatcht"); sys.exit(0)

def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer (verwacht %d): %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw, n)

rep('var APP_VERSIE = "v23.254";', 'var APP_VERSIE = "v23.255";')

# ---------- 1. de leerrij ----------
rep('''function gramWachtrij(){
  var t = today(), uit = [];''',
'''/* ================= DE LEERRIJ: ROTEREN IN PLAATS VAN ALTIJD HET ZWAKSTE (v23.255) =================

   gramWachtrij() hieronder sorteert oplopend op doos, want het zwakste hoort vooraan. Voor de
   planning klopt dat. Als keuze voor de dagles maakt het een lus: een misser zet due op morgen, dus
   het doosje waar je vandaag op struikelde staat morgen weer vooraan, en overmorgen weer. Met een
   plek per dag raakt de onderkant van de stapel nooit leeg en komt de bovenkant nooit aan de beurt.

   Hier wint wie het langst niet aan de beurt is geweest. st.bd is de dag waarop dit doosje voor het
   laatst een antwoord kreeg (v23.225 schrijft hem). Leeg betekent langer geleden dan de boekhouding
   reikt, en staat dus vooraan. Binnen dezelfde dag telt alsnog het zwakste doosje eerst, want dan is
   de rotatie uitgewerkt en is de oude regel weer de beste.

   Gevolg dat je meteen merkt: wat je vandaag al deed zakt naar achteren. Een tweede les op dezelfde
   dag geeft daardoor andere patronen in plaats van dezelfde nog een keer.

   gramWachtrij() zelf blijft ongemoeid. Die wordt ook gelezen door het voortgangsscherm en door
   gramOnderhoudTop(), en die willen wel degelijk op doos sorteren. */
var GRAM_LEERBEURTEN = 3;   // zoveel verschillende patronen biedt de dagles aan
function gramLeerRij(){
  var rij = [];
  try { rij = gramWachtrij(); } catch(e){ return []; }
  return rij.slice().sort(function(a, b){
    var ad = (a.st && a.st.bd) || "", bd = (b.st && b.st.bd) || "";
    if(ad !== bd) return ad < bd ? -1 : 1;
    return ((a.st.box || 0) - (b.st.box || 0));
  });
}
function gramWachtrij(){
  var t = today(), uit = [];''')

# ---------- 2. meer dan een leerbeurt per dagles ----------
start = """  var rij = [];
  try { rij = gramWachtrij(); } catch(e){ rij = []; }
  if(rij.length){
    var top = rij[0];"""
eind = """  var kaal = function(x){ return String(x || "").replace(/^(opfris|concept)-/, "").split("#")[0]; };"""
i = s.index(start)
j = s.index(eind, i)
assert 0 < i < j, "het blok in lesFlowGramLijst ligt niet zoals verwacht"
nieuw = '''  /* v23.255: hier stond een leerbeurt, rij[0], en dat was het knelpunt. Zie de kop van
     patch-v23.255 voor de meting: met een beurt haalt 24 van de 190 doosjes doos 5 in een jaar, met
     vier beurten 185. Boven de vier levert het niets meer op, want een doosje klimt hoogstens een
     stap per dag (v23.225).

     Drie opfrissers plus de microles hieronder maakt vier, plus de onderhoudsbeurt op dagen dat er
     iets vervalt. Dat is zes vragen extra, ongeveer een minuut.

     Hoogstens een patroon per onderwerp per les. Dat is de regel van v23.170 en die blijft staan:
     "heel veel el of la" was een klacht, en vijf patronen van hetzelfde onderwerp op een dag is die
     klacht in een nieuwe jas. Verschillende onderwerpen is precies wat deze ronde wil. */
  var rij = gramLeerRij();
  var gezien = {};
  for(var ri = 0; ri < rij.length && uit.length < GRAM_LEERBEURTEN; ri++){
    var top = rij[ri];
    if(gezien[top.c.id]) continue;
    /* Twee keer mis op hetzelfde is geen geheugenkwestie: dan geen opfrisvraag maar de hele
       microles, en die komt uit lesFlowGramId() hieronder.
       v23.212: tenzij er vandaag al een half bewijs ligt. Het doosje blijft dan op nul staan tot het
       tweede bewijs er is, en zonder deze uitzondering zou de hele microles twee dagen achter elkaar
       komen op een onderwerp dat je gisteren goed had.
       v23.248: gcVersMissers in plaats van st.fout, want st.fout is de levenslange optelsom en stond
       bij Stefan op zestien onderwerpen boven nul, dus deze uitzondering gold bijna altijd.
       v23.255: dit sloeg vroeger de hele leerbeurt over. Nu slaat het dit doosje over en kijkt de
       lus verder, want er is geen reden om de les een beurt te laten missen. */
    if((top.st.box || 0) === 0 && gcVersMissers(top.c.id) >= 2 && !top.st.half) continue;
    var o = null;
    try { o = gcGebouwd(gcOpfrisId(top.c.id, top.pi)); } catch(e){ o = null; }
    if(!o) continue;
    gezien[top.c.id] = 1;
    uit.push(o.id);
  }
'''
s = s[:i] + nieuw + s[j:]

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", len(s), "tekens")
