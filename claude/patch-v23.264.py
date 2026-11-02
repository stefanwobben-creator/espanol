# patch-v23.264.py - het oordeel telt op conceptniveau, de doos beweegt per patroon.
#
# WAT ER GEMETEN IS, IN STEFANS ECHTE PROFIEL
#
# De opfrisser ging in v23.259 van twee naar vijf vragen, en dat werkt: 31 oktober 21 vragen,
# 1 november 18, tegen vijf tot acht in de week ervoor. Drie keer zoveel.
#
# Maar het oordeel dat erbij hoorde vuurt nooit. Op 1 november zijn er zestien doosjes geraakt,
# veertien met precies een antwoord en twee met twee. Nul doosjes kwamen aan vijf.
#
# De reden: gcMaakVragen() rouleert over de patronen van een onderwerp (v23.59, en terecht: vier
# keer hetzelfde patroon leert de oppervlakte), en sinds v23.228 heeft elk patroon zijn eigen
# doosje. Vijf vragen gaan dus naar vijf doosjes, een antwoord elk, en GRAM_OORDEEL_MIN telt per
# doosje. Alles valt daarmee terug op de oude regel, en dat is in de data te zien:
#
#     genero#0   doos 4 -> 5   op EEN goed antwoord
#     quecual#3  doos 0        op EEN misser, terwijl quecual die dag 4 van de 5 goed stond
#
# Op conceptniveau is het bewijs er wel: 1 november genero 6, gustar 5, quecual 5 antwoorden.
#
# DE REGEL
#
#     minstens GRAM_OORDEEL_MIN antwoorden op dit ONDERWERP vandaag
#       75% of meer   ->  elk patroon dat je vandaag goed deed gaat een doos omhoog
#                         het patroon waar je op misging blijft staan, en valt niet naar nul
#       daaronder     ->  elk geraakt patroon een doos omlaag
#     minder dan zoveel antwoorden op het onderwerp: de oude regel, ongewijzigd
#
# EN DE MIDDENBAND IS WEG, WANT HIJ LIET EEN 70-PROCENTLEERLING KLIMMEN
#
# v23.259 had er drie: omhoog boven 75, blijven staan tussen 50 en 75, omlaag daaronder. De
# simulatie in pw-doosje (30 dagen, zes antwoorden per dag, 200 lopen) liet zien wat dat doet: een
# leerling die 70 procent kent kwam in 55 procent van de lopen in doos 4 of 5 terecht. Nagerekend
# waarom, met zes antwoorden per dag:
#
#     kans op een dag van 5 of 6 goed    p=0,97: 99%   p=0,93: 94%   p=0,85: 78%   p=0,70: 42%
#
# Met een middenband is alles onder de 50 procent nodig om te zakken, en dat gebeurt bij 70 procent
# maar in een kwart van de dagen. Netto klim je dus, elke dag een beetje. Zonder middenband is de
# drift precies goed: +0,55 per dag bij 85 procent, -0,16 bij 70 procent. Het omslagpunt ligt rond
# de 78 procent, en dat is een verdedigbare grens voor "ken je dit".
#
# Een dag is dus goed genoeg of niet. Dat is ook gewoon Leitner.
#
# Dit is ook pas de echte slordigheidsreparatie. v23.254 gaf er een halve (een misser kostte nog
# maar een doos als je staat van dienst goed genoeg was); nu kost een misser tussen vier goede
# antwoorden dat ene patroon helemaal niets meer dan een dag uitstel.
#
# WAAROM HET OORDEEL OVER HET ONDERWERP GAAT EN DE DOOS OVER HET PATROON
#
# De vijf vragen van een opfrisser gaan over hetzelfde onderwerp, dus samen zijn ze een meting van
# dat onderwerp. Welke doos er beweegt is iets anders: dat blijft het patroon, want "indefimperf
# doos 2" moet blijven betekenen welke regel wiebelt (v23.228). Meten doe je op de plek waar het
# bewijs ligt, boeken op de plek waar het hoort.
#
# EN DE VOLGORDE DOET ER NIET TOE
#
# Het oordeel wordt bij elk antwoord opnieuw geveld over ALLE doosjes van dit onderwerp die vandaag
# zijn aangeraakt, telkens vanaf de stand van vanochtend (boxVoor). Zonder dat zou het eerste
# doosje van de ronde met de oude regel beoordeeld blijven en het vijfde met de nieuwe. Dezelfde
# eis als v23.225: dezelfde antwoorden geven dezelfde uitkomst, in welke volgorde je ze ook geeft.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "gramDagConcept" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


# ---------------------------------------------------------------- 1. tellen en vellen

HULP = '''/* ================= HET BEWIJS LIGT BIJ HET ONDERWERP (v23.264) =================

   Gemeten in Stefans profiel op 1 november: zestien doosjes geraakt, veertien met precies een
   antwoord, twee met twee, nul met vijf. GRAM_OORDEEL_MIN telt per doosje en vuurde dus nooit.

   De oorzaak is geen fout maar een botsing tussen twee goede beslissingen. gcMaakVragen rouleert
   over de patronen van een onderwerp (v23.59: vier keer hetzelfde patroon leert de oppervlakte),
   en elk patroon heeft een eigen doosje (v23.228: anders kan "indefimperf doos 2" vier dingen
   betekenen). Vijf vragen over een onderwerp zijn daarmee vijf doosjes met een antwoord.

   Het bewijs ligt dus bij het onderwerp en de boekhouding bij het patroon. Deze twee functies
   doen precies dat: tellen over het hele onderwerp, vellen per patroon.

   De sleutels worden gescand in plaats van via gramDoosjes() opgehaald, want gramDoosjes leunt op
   gcConcept() en dat kent alleen de echte concepten. Hier moet ook een doosje meetellen dat bij
   een onderwerp hoort dat de concepttabel niet kent. */
function gramDagConcept(cid){
  var s = String(cid || "").split("#")[0], d = today(), n = 0, goed = 0;
  try {
    Object.keys(S.gram || {}).forEach(function(k){
      if(k !== s && k.indexOf(s + "#") !== 0) return;
      var x = S.gram[k];
      if(!x || x.bd !== d) return;
      n += (x.dagGoed || 0) + (x.dagMis || 0);
      goed += (x.dagGoed || 0);
    });
  } catch(e){ return {n:0, goed:0}; }
  return {n:n, goed:goed};
}
/* Het oordeel over elk doosje van dit onderwerp dat vandaag is aangeraakt, telkens vanaf de stand
   van vanochtend. Bij elk antwoord opnieuw, zodat de uitkomst niet afhangt van de volgorde waarin
   je de vragen toevallig goed of fout had (dezelfde eis als v23.225).

   Twee banden en geen derde: een dag haalt de drempel of hij haalt hem niet. De middenband van
   v23.259 liet een leerling die 70 procent kent gewoon doorklimmen, want zakken vroeg daar minder
   dan 50 procent en dat gebeurt bijna nooit. Zie de kop van deze patch voor de cijfers.

   Binnen een geslaagde dag is er wel een uitzondering, en die gaat over het verschil tussen "je
   kent dit onderwerp niet" en "deze ene ging mis": een patroon waar je vandaag op misging gaat
   niet omhoog, maar valt ook niet terug. Tenzij je datzelfde patroon vandaag vaker had en het op
   zichzelf ook boven de drempel staat, want dan heeft het zijn eigen bewijs. */
function gramVelConcept(cid, deel){
  var s = String(cid || "").split("#")[0], d = today();
  try {
    Object.keys(S.gram || {}).forEach(function(k){
      if(k !== s && k.indexOf(s + "#") !== 0) return;
      var x = S.gram[k];
      if(!x || x.bd !== d) return;
      x.half = 0;
      if(deel < GRAM_OORDEEL_OP){
        x.box = Math.max(0, (x.boxVoor || 0) - 1);
        x.due = addDays(d, 1);
        return;
      }
      var eigenN = (x.dagGoed || 0) + (x.dagMis || 0);
      var eigen = eigenN ? (x.dagGoed || 0) / eigenN : 1;
      if(!(x.dagMis || 0) || eigen >= GRAM_OORDEEL_OP){
        x.box = Math.min((x.boxVoor || 0) + 1, GRAM_BOX.length - 1);
        x.due = addDays(d, GRAM_BOX[x.box]);
      } else {
        x.box = x.boxVoor || 0;
        x.due = addDays(d, 1);
      }
    });
  } catch(e){}
}

'''

rep("function gramBij(cid, goed, keuzes, pi, kanaal){", HULP + "function gramBij(cid, goed, keuzes, pi, kanaal){")

# ---------------------------------------------------------------- 2. het doosje meteen in S.gram

rep("""  var st = S.gram[sleutel] || {box:0, due:"", goed:0, fout:0, laatst:""};""",
    """  var st = S.gram[sleutel] || {box:0, due:"", goed:0, fout:0, laatst:""};
  /* v23.264: meteen vastzetten en niet pas aan het eind. gramDagConcept() scant S.gram, en een
     gloednieuw doosje zou zijn eigen antwoord anders niet meetellen in het bewijs. */
  S.gram[sleutel] = st;""")

# ---------------------------------------------------------------- 3. het oordeel

OUD = """  var dagN = (st.dagGoed || 0) + (st.dagMis || 0);
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

NIEUW = """  /* v23.259, bijgesteld in v23.264: genoeg antwoorden vandaag OP DIT ONDERWERP, dus het oordeel is
     een aandeel en geen gebeurtenis.

     Dit keert v23.170 en v23.254 om, en met reden. Die schreven op dat een misser altijd de
     promotie kost en dat de reset naar nul blijft staan, omdat Stefan daar zelf om vroeg en
     omdat SuperMemo de een-stap-variant een onjuiste mutatie van Leitner noemt. Dat klopte bij
     een oordeel over een of twee vragen: dan weet je niets en is nul het enige veilige antwoord.
     Bij vijf of meer weet je wel iets, en dan is naar nul gooien informatie weggooien.

     v23.264 telt het bewijs over het hele onderwerp in plaats van over dit ene doosje. Gemeten:
     een opfrisser van vijf vragen raakt vijf verschillende patronen met een antwoord elk, dus per
     doosje werd de vijf nooit gehaald en gold deze tak in de praktijk nooit.

     Onder de drempel verandert er niets: dan geldt de oude regel hieronder. */
  var dagC = gramDagConcept(cid);
  if(dagC.n >= GRAM_OORDEEL_MIN){
    gramVelConcept(cid, dagC.goed / dagC.n);
  } else if(st.dagMis){"""
rep(OUD, NIEUW)

# ---------------------------------------------------------------- 4. de middenband opruimen

rep("var GRAM_OORDEEL_NEER = 0.5;  // hieronder: een doos omlaag. Ertussenin: blijven staan.",
    """/* v23.264: de middenband is weg. Hij stond op 0,5 en liet daarmee een leerling die 70 procent
   kent elke dag een beetje klimmen: met zes antwoorden per dag haal je de 75 procent in 42 procent
   van de dagen en zak je pas onder de 50, wat maar in een kwart van de dagen gebeurt. Netto omhoog
   dus, en dat is precies wat een doosjessysteem niet mag doen. Met twee banden is de drift +0,55
   per dag bij 85 procent en -0,16 bij 70 procent. */""")

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
