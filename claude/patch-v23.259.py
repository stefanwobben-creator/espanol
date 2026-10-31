# patch-v23.259.py - een oordeel gaat over minstens vijf antwoorden, en kent drie uitkomsten.
#
# WAT STEFAN ZEI
#
# "als er 2 vragen zijn en ik heb een fout is al 50% fout, maar fouten gebeuren, dus ook hier
# minimaal 5 ofzo, maar dat ik vanaf niveau 4 terug kan naar 3 (= vaker oefenen) of naar 5 kan
# (is minder vaak oefenen). en de aantallen die graag baseren op wetenschap."
#
# WAT TWEE VRAGEN METEN
#
# Uitgerekend, kans dat je de promotie haalt bij een gegeven werkelijk kennisniveau p:
#
#     regel                      p=0,95  p=0,90  p=0,80  p=0,70  p=0,60  gokker (p=0,5)
#     nu: 2 van 2                  90%     81%     64%     49%     36%      25%
#     4 van 5   (80%)              98%     92%     74%     53%     34%      19%
#     6 van 8   (75%)              99%     96%     80%     55%     32%      14%
#     8 van 10  (80%)              99%     93%     68%     38%     17%       6%
#
# Twee regels staan daarin. Iemand die een onderwerp voor negentig procent beheerst zakt nu in
# bijna een op de vijf beurten: dat is ruis en geen strengheid. En omdat 101 van de 153 patronen
# maar twee keuzes hebben, haalt wie puur gokt nu een op de vier keer een promotie. Meer vragen
# maakt het oordeel aan allebei de kanten tegelijk eerlijker, en dat is zeldzaam.
#
# DE REGEL
#
#     minstens GRAM_OORDEEL_MIN antwoorden vandaag op dit doosje, anders geen oordeel
#     75% of meer goed  ->  een doos omhoog
#     50 tot 74%        ->  blijft staan, morgen weer
#     minder dan 50%    ->  een doos omlaag, en niet meer naar nul
#
# Toegestane missers is daarmee het aantal vragen gedeeld door vier: bij vijf vragen een, bij acht
# twee, bij twaalf drie. Hoe langer je oefent, hoe betrouwbaarder het oordeel.
#
# DIT KEERT EEN EERDERE BESLISSING OM, EN DAT IS MET REDEN
#
# v23.170 en v23.254 schrijven allebei op dat de reset naar nul blijft staan, omdat Stefan daar zelf
# om vroeg ("alle fouten die ik maak moeten weer terug") en omdat SuperMemo de een-stap-variant een
# onjuiste mutatie van Leitner noemt. Die redenering klopte bij een oordeel over een of twee
# vragen: dan is nul het enige veilige antwoord, want je weet niets. Bij vijf of meer antwoorden
# weet je wel iets, en dan is naar nul gooien geen voorzichtigheid meer maar informatie weggooien.
# Onder de vijf antwoorden blijft de oude regel daarom onveranderd staan.
#
# DE AANTALLEN VRAGEN
#
# De opfrisser gaat van twee naar vijf vragen, want anders kan het oordeel hierboven nooit vallen in
# de dagles. En de leerbeurten per dag gaan van drie naar twee, zodat het grammaticablok tien vragen
# telt in plaats van zes en niet vijftien. De drill gaat van vijf naar acht: hij hoort meer te zijn
# dan de opfrisser, dat is zijn hele bestaansreden (pw-drill bewaakt het).
#
# Rohrer en Taylor (2006) over doorploegen binnen een sessie, Cepeda e.a. (2006) over de beste
# tussenpoos, Vaughn en Rawson (2011) over drie tot vier keer ophalen: zie de begeleidende notitie.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "GRAM_OORDEEL_MIN" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


# ---------------------------------------------------------------- 1. de constanten

OUD_C = '''var GRAM_RIJ = 12;         // zoveel antwoorden per doosje worden onthouden'''
NIEUW_C = '''/* ================= EEN OORDEEL GAAT OVER MINSTENS VIJF ANTWOORDEN (v23.259) =================

   Stefan: "als er 2 vragen zijn en ik heb een fout is al 50% fout, maar fouten gebeuren, dus ook
   hier minimaal 5 ofzo, maar dat ik vanaf niveau 4 terug kan naar 3 of naar 5 kan."

   Uitgerekend, kans op promotie bij een werkelijk kennisniveau p:

       regel            p=0,95  p=0,90  p=0,80  p=0,70  p=0,60  gokker
       2 van 2 (nu)       90%     81%     64%     49%     36%     25%
       4 van 5            98%     92%     74%     53%     34%     19%
       6 van 8            99%     96%     80%     55%     32%     14%
       8 van 10           99%     93%     68%     38%     17%      6%

   Wie een onderwerp voor negentig procent beheerst zakt nu in bijna een op de vijf beurten, en wie
   puur gokt haalt een op de vier keer een promotie (101 van de 153 patronen hebben twee keuzes).
   Meer vragen helpt die twee tegelijk, en dat is zeldzaam.

   De drempel is 75 procent, dus het aantal toegestane missers is het aantal antwoorden gedeeld
   door vier: bij vijf een, bij acht twee, bij twaalf drie. */
var GRAM_OORDEEL_MIN = 5;     // minder antwoorden vandaag op dit doosje is geen oordeel
var GRAM_OORDEEL_OP = 0.75;   // dit aandeel goed of meer: een doos omhoog
var GRAM_OORDEEL_NEER = 0.5;  // hieronder: een doos omlaag. Ertussenin: blijven staan.
var GRAM_RIJ = 12;         // zoveel antwoorden per doosje worden onthouden'''
rep(OUD_C, NIEUW_C)

# ---------------------------------------------------------------- 2. het oordeel zelf

OUD_O = """  if(st.dagMis){"""
NIEUW_O = """  var dagN = (st.dagGoed || 0) + (st.dagMis || 0);
  if(dagN >= GRAM_OORDEEL_MIN){
    /* v23.259: genoeg antwoorden vandaag, dus het oordeel is een aandeel en geen gebeurtenis.

       Dit keert v23.170 en v23.254 om, en met reden. Die schreven op dat een misser altijd de
       promotie kost en dat de reset naar nul blijft staan, omdat Stefan daar zelf om vroeg en
       omdat SuperMemo de een-stap-variant een onjuiste mutatie van Leitner noemt. Dat klopte bij
       een oordeel over een of twee vragen: dan weet je niets en is nul het enige veilige antwoord.
       Bij vijf of meer weet je wel iets, en dan is naar nul gooien informatie weggooien.

       Onder de vijf antwoorden verandert er niets: dan geldt de oude regel hieronder. */
    var deel = (st.dagGoed || 0) / dagN;
    st.half = 0;
    if(deel >= GRAM_OORDEEL_OP){
      st.box = Math.min((st.boxVoor || 0) + 1, GRAM_BOX.length - 1);
      st.due = addDays(today(), GRAM_BOX[st.box]);
    } else if(deel >= GRAM_OORDEEL_NEER){
      // blijven staan is een uitkomst en geen niets: je ziet het morgen terug op dezelfde doos
      st.box = st.boxVoor || 0;
      st.due = addDays(today(), 1);
    } else {
      st.box = Math.max(0, (st.boxVoor || 0) - 1);
      st.due = addDays(today(), 1);
    }
  } else if(st.dagMis){"""
rep(OUD_O, NIEUW_O)

# ---------------------------------------------------------------- 3. de aantallen vragen

rep("var GC_OPFRIS_VRAGEN = 2;",
    """/* v23.259: van twee naar vijf. Met twee vragen kan het oordeel van gramBij nooit vallen in de
   dagles, en dan zou de nieuwe regel alleen in een oefensessie gelden. Zie de kop bij
   GRAM_OORDEEL_MIN voor waarom vijf en niet twee of tien. */
var GC_OPFRIS_VRAGEN = 5;""")

rep("var GC_DRILL_VRAGEN = 5;",
    """/* v23.259: van vijf naar acht. De drill hoort meer te zijn dan de opfrisser, dat is zijn hele
   bestaansreden, en de opfrisser staat nu op vijf. Acht is ook het punt waar een gokker nog maar
   14 procent van de promoties haalt in plaats van 19. */
var GC_DRILL_VRAGEN = 8;""")

rep("var GRAM_LEERBEURTEN = 3;   // zoveel verschillende patronen biedt de dagles aan",
    """/* v23.259: van drie naar twee. De opfrisser ging van twee naar vijf vragen, en drie leerbeurten
   zouden het grammaticablok op vijftien vragen zetten. Tien is al bijna een verdubbeling van de
   zes van gisteren. De doorstroom die v23.255 kocht komt terug uit de oefensessie, en als Stefan
   die niet doet hoort dit getal terug naar drie. */
var GRAM_LEERBEURTEN = 2;   // zoveel verschillende patronen biedt de dagles aan""")

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
