#!/usr/bin/env python3
# v23.207 - één reeks, één schatter, en de marge doet het werk van de drempel
#
# Stefan, 30 aug: "nou ik vraag me af waarom een weekmeting, dit hebben we al een keer besproken.
# Volgens mij wil je een dagmeting en dan een voorspelling met een foutmarge die steeds minder groot
# wordt."
#
# Hij heeft gelijk, en het is erger dan hij denkt: de weekmeting zat er nog op vier plekken in.
#
# WAT ER LAG
#
#   tempoMeting()   pakte de dagreeks, en viel anders terug op de weekreeks MET EEN ANDERE SCHATTER:
#                   de dagreeks doet kleinste kwadraten op de datums, de weekterugval nam het
#                   gemiddelde van de verschillen tussen opeenvolgende weken. Twee schatters onder
#                   één naam, precies de bugsoort van deze hele week.
#   TEMPO_MIN_PUNTEN stond op 5. Dat getal is niet afgeleid van iets; het was voorzichtigheid.
#   vier wachtteksten telden allemaal zelf hoeveel WEEKmetingen er lagen, elk met
#                   nog = Math.max(1, 3 - aantal). Dat is geklemd op 1, dus alle vier stonden ze
#                   eeuwig op "nog 1 week te gaan". v23.203 repareerde de doelkaart, v23.206 de
#                   voorspelling, en ik liet de band en de lesregel staan: het geval gerepareerd in
#                   plaats van de soort, dezelfde fout als bij de Door-knop.
#
# WAAROM DRIE EN NIET VIJF
#
# Drie is geen smaak maar de bodem van de rekensom. De standaardfout van een helling deelt door
# n - 2 vrijheidsgraden; bij twee punten is dat nul en is er geen marge, bij drie is er voor het
# eerst een. En zodra er een marge is, zegt die alles wat een drempel op het aantal punten probeerde
# te zeggen, alleen in de goede eenheid: niet "je hebt er nog niet genoeg" maar "het ligt tussen
# zoveel en zoveel, en dat wordt smaller".
#
# Op Stefans eigen drie punten (17 aug 493, 24 aug 621, 30 aug 639) geeft dat 80 per week met een
# marge van 61: de band loopt van 19 tot 141. Hij heeft er 16,8 nodig. De hele band ligt erboven,
# dus het antwoord is er al en de drempel van vijf hield het tegen.
#
# EN WAAROM DE WEEKTERUGVAL WEG KAN ZONDER IETS TE VERLIEZEN
#
# dagMetingSchrijf() zaait de dagreeks met elke weekmeting die dekw draagt, op de datum die de
# weekmeting zelf bewaart. Drie bruikbare weken zijn dus drie dagpunten, en drie verschillende
# ISO-weken liggen altijd minstens acht dagen uit elkaar. Elke toestand waarin de weekterugval iets
# zou zeggen, is een toestand waarin de dagreeks bij een drempel van drie ook iets zegt. De terugval
# is per constructie onbereikbaar, en onbereikbare code die een ANDER antwoord zou geven is precies
# het soort ding dat over een half jaar ineens weer aan gaat.
#
# WAT DEZE RONDE DOET
#
#   1. TEMPO_MIN_PUNTEN 5 -> 3, met de reden erbij.
#   2. tempoMeting() heeft nog één bron en één schatter. metingenNieuweMaat() verdwijnt.
#   3. Alle vier de wachtteksten komen uit tempoWachtZin(). Er is geen plek meer die zelf telt.
#   4. De uitspraak "op koers" komt pas als de HELE band aan één kant van de nodige snelheid ligt.
#      Daarboven schommelde hij: met een brede band vertelt een puntschatting je elke dag iets
#      anders, en dat is precies het soort indicator dat Stefan een liegende indicator noemt.
#   5. De band telt in dagen gemeten, niet in weken. tempoDagMeting() gaf weken als span/7, en dat
#      stond als 1.8571428571428572 op het scherm te wachten tot er ooit een band zou zijn.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.207"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "TEMPO_MIN_PUNTEN = 3" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:120])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. drie punten, want daar begint de marge
# =============================================================================================
if DOE_APP:
    rep("""   Twee drempels, en ze meten twee verschillende dingen. TEMPO_MIN_PUNTEN gaat over hoeveel bewijs
   er is; TEMPO_MIN_SPAN gaat over waarover. Vijf metingen uit drie dagen zeggen iets over drie
   dagen en niets over een tempo, dus daar hoort de voorspeller nog te zwijgen. */
var TEMPO_MIN_PUNTEN = 5;
var TEMPO_MIN_SPAN = 7;""",
        """   Twee drempels, en ze meten twee verschillende dingen. TEMPO_MIN_PUNTEN gaat over hoeveel bewijs
   er is; TEMPO_MIN_SPAN gaat over waarover. Vijf metingen uit drie dagen zeggen iets over drie
   dagen en niets over een tempo, dus daar hoort de voorspeller nog te zwijgen.

   v23.207. Stefan: "volgens mij wil je een dagmeting en dan een voorspelling met een foutmarge die
   steeds minder groot wordt." Daar had hij gelijk in, en de drempel van vijf stond die marge in de
   weg. Drie is geen smaak maar de bodem van de som: de standaardfout van een helling deelt door
   n - 2 vrijheidsgraden, dus bij twee punten is er geen marge en bij drie voor het eerst wel. En
   zodra er een marge is zegt die alles wat een puntendrempel probeerde te zeggen, alleen in de
   goede eenheid: niet "nog niet genoeg" maar "tussen zoveel en zoveel, en dat wordt smaller".

   De spandrempel blijft staan en om een andere reden: drie punten die netjes op een lijn liggen
   geven een kleine marge, ook als ze uit drie opeenvolgende dagen komen. Dan is de schatting
   scherp over drie dagen en zegt hij nog steeds niets over een week. Marge en spreiding vangen
   verschillende fouten; wie er één weglaat houdt de andere niet tegen. */
var TEMPO_MIN_PUNTEN = 3;
var TEMPO_MIN_SPAN = 7;""")

# =============================================================================================
# 2. één bron, één schatter
# =============================================================================================
if DOE_APP:
    rep("""function metingenNieuweMaat(niveau){
  var ws = Object.keys(S.meting || {}).sort(), uit = [], i, m;
  for(i = 0; i < ws.length; i++){
    m = S.meting[ws[i]] || {};
    if(m.dekw && typeof m.dekw[niveau] === "number") uit.push(m.dekw[niveau]);
  }
  return uit;
}
""", "")

    rep("""function tempoMeting(niveau){
  /* v23.198: de dagreeks gaat voor. Eén functie blijft de bron voor voortgangBand() en
     voorspelWaar(), want twee plekken die allebei een tempo uitrekenen lopen uit elkaar en dan
     spreekt hetzelfde scherm zichzelf tegen. De weekreeks blijft eronder liggen als terugval voor
     wie nog geen dagpunten heeft. */
  var dag = null;
  try { dag = tempoDagMeting(niveau); } catch(e){ dag = null; }
  if(dag) return dag;
  var reeks = metingenNieuweMaat(niveau);
  if(reeks.length < 3) return null;
  var d = [], i;
  for(i = 1; i < reeks.length; i++) d.push(reeks[i] - reeks[i-1]);
  var som = d.reduce(function(a, b){ return a + b; }, 0), gem = som / d.length;
  var v = d.reduce(function(a, b){ return a + (b - gem) * (b - gem); }, 0) / Math.max(1, d.length - 1);""",
        """function tempoMeting(niveau){
  /* v23.198: één functie blijft de bron voor voortgangBand(), voorspelWaar() en doelStand(), want
     twee plekken die allebei een tempo uitrekenen lopen uit elkaar en dan spreekt hetzelfde scherm
     zichzelf tegen.

     v23.207: en nu ook één reeks en één schatter. Hieronder lag een terugval op de weekreeks die
     het gemiddelde van de verschillen nam in plaats van een lijn door de datums. Twee schatters
     onder één naam is dezelfde soort fout als twee knoppen met één id.

     Weggooien kost niets, en dat is na te rekenen in plaats van te hopen: dagMetingSchrijf() zaait
     de dagreeks met elke weekmeting die dekw draagt, op de datum die de weekmeting zelf bewaart.
     Drie bruikbare weken zijn dus drie dagpunten, en drie verschillende ISO-weken liggen altijd
     minstens acht dagen uit elkaar. Bij een drempel van drie punten over zeven dagen zegt de
     dagreeks dus overal waar de weekterugval iets zou zeggen. Zie pw-wachtzin.js, proef 5. */
  try { return tempoDagMeting(niveau); } catch(e){ return null; }
}
function _tempoWeekOud(reeks){
  var d = [], i;
  for(i = 1; i < reeks.length; i++) d.push(reeks[i] - reeks[i-1]);
  var som = d.reduce(function(a, b){ return a + b; }, 0), gem = som / d.length;
  var v = d.reduce(function(a, b){ return a + (b - gem) * (b - gem); }, 0) / Math.max(1, d.length - 1);""")

    # de staart van de oude functie is nu de staart van _tempoWeekOud; die hoort weg
    rep("""  /* v23.162: hier stond `weken: ws.length`, en er is geen ws in deze functie. JavaScript pakte dan
     de globale ws van de woordenzoeker (var ws = null, twaalfduizend regels verderop). Nooit
     gewoordenzoekerd betekende dus een TypeError op ws.length, en daarmee klapte tempoMeting en
     alles wat eraan hangt: voortgangBand, voorspelWaar en voorspelHtml. De hele voorspelling, voor
     iedereen, sinds v19.90.

     Niets ving het, en dat is het echte probleem: elke aanroeper vangt fouten af ("een meter mag de
     app nooit omver duwen"), dus een kapotte voorspeller ziet er op het scherm precies zo uit als
     een voorspeller die nog zwijgt omdat er te weinig weken zijn. */
  return {gem:gem, marge:2 * Math.sqrt(v / d.length), weken:reeks.length, nu:reeks[reeks.length - 1]};
}
""", "")
    rep("function _tempoWeekOud(reeks){\n", "")
    rep("""  var d = [], i;
  for(i = 1; i < reeks.length; i++) d.push(reeks[i] - reeks[i-1]);
  var som = d.reduce(function(a, b){ return a + b; }, 0), gem = som / d.length;
  var v = d.reduce(function(a, b){ return a + (b - gem) * (b - gem); }, 0) / Math.max(1, d.length - 1);
""", "")

# =============================================================================================
# 3. de band telt dagen, niet weken
# =============================================================================================
if DOE_APP:
    rep("""  return {
    tempo: m.gem,
    weken: m.weken,""",
        """  return {
    tempo: m.gem,
    marge: m.marge,
    dagen: m.dagen,
    punten: m.punten,""")

# =============================================================================================
# 4. alle wachtteksten uit één functie
# =============================================================================================
if DOE_APP:
    # 4a. de band op de voortgangspagina
    rep("""function bandHtml(niveau){
  // v23.38: tellen wat meetelt. Weken zonder dekw staan wel in S.meting maar doen niet mee, dus met
  // Object.keys() zou hier "nog 1 week te gaan" staan die nooit voorbijgaat.
  var weken = metingenNieuweMaat(niveau).length;
  var b = voortgangBand(niveau);
  if(!b){
    var nog = Math.max(1, 3 - weken);
    return "<p class='muted' style='margin-top:6px'>"+
      ct("Er wordt gemeten: elke week legt de app vast hoeveel "+niveau+"-woorden er stevig staan. "+
         "Na drie metingen staat hier een schatting met marge, niet eerder, want met twee punten is elk tempo toeval. "+
         "Nog <b>"+nog+"</b> "+(nog === 1 ? "week" : "weken")+" te gaan.",
         "Measuring: every week the app records how many "+niveau+" words are solid. "+
         "After three measurements an estimate with a margin appears here, not before, because with two points any pace is coincidence. "+
         "<b>"+nog+"</b> more "+(nog === 1 ? "week" : "weeks")+" to go.")+"</p>";
  }""",
        """function bandHtml(niveau){
  var b = voortgangBand(niveau);
  if(!b){
    /* v23.207: hier telde deze functie zelf zijn weekmetingen en rekende nog = max(1, 3 - aantal).
       Geklemd op 1, dus daar stond eeuwig "nog 1 week te gaan". Dat was de derde van vier plekken
       met precies diezelfde som; ze komen nu alle vier uit tempoWachtZin(). */
    return "<p class='muted' style='margin-top:6px'>"+
      ct("Er wordt gemeten: elke dag dat je de app opent legt hij vast hoeveel "+niveau+"-woorden er staan. ",
         "Measuring: every day you open the app it records how many "+niveau+" words you hold. ")+
      tempoWachtZin(niveau)+"</p>";
  }""")

    rep("""      "<div class='stat'><b>"+b.weken+"</b><span class='muted'>"+ct("weken gemeten","weeks measured")+"</span></div>"+
      "</div>"+
    "<p class='muted' style='margin-top:6px'>"+
      ct("Dit is een marge, geen datum. Hij is berekend uit je eigen weekmetingen en wordt smaller naarmate er meer weken in zitten. \"""",
        """      "<div class='stat'><b>"+b.punten+"</b><span class='muted'>"+ct("dagen gemeten","days measured")+"</span></div>"+
      "</div>"+
    "<p class='muted' style='margin-top:6px'>"+
      ct("Dit is een marge, geen datum. Hij is berekend uit je eigen dagmetingen en wordt smaller met elke dag die erbij komt. \"""")
    rep("""         "This is a margin, not a date. It's computed from your own weekly measurements and narrows as more weeks come in. \"""",
        """         "This is a margin, not a date. It's computed from your own daily measurements and narrows with every day that comes in. \"""")

    # 4b. de regel na een les
    rep("""    var weken = 0;
    try { weken = metingenNieuweMaat(niv).length; } catch(e){ weken = 0; }
    var nog = Math.max(1, 3 - weken);
    staart = ct("hoe lang je nog te gaan hebt weet de app na nog "+nog+" "+(nog === 1 ? "week" : "weken")+" meten",
                "how long you have to go is known after "+nog+" more "+(nog === 1 ? "week" : "weeks")+" of measuring");""",
        """    /* v23.207: de vierde plek die zelf weekmetingen telde met nog = max(1, 3 - aantal). Eén bron,
       en hier kort: de hele wachtzin is te lang voor een regel onder een viering. */
    var st = tempoStand(niv);
    var nogD = Math.max(Math.max(0, st.nodig - st.heeft), Math.max(0, st.spanNodig - st.span));
    staart = ct("hoe lang je nog te gaan hebt weet de app na nog "+nogD+" dag"+(nogD === 1 ? "" : "en")+" meten",
                "how long you have to go is known after "+nogD+" more day"+(nogD === 1 ? "" : "s")+" of measuring");""")

# =============================================================================================
# 5. "op koers" pas als de hele band aan één kant ligt
# =============================================================================================
if DOE_APP:
    rep("""  return {niv:niv, datum:dat, weken:weken, nu:nu, noemer:noemer, rest:rest,
          nodig: weken > 0 ? rest / weken : null,
          tempo: m ? m.gem : null, klaar: rest === 0};""",
        """  return {niv:niv, datum:dat, weken:weken, nu:nu, noemer:noemer, rest:rest,
          nodig: weken > 0 ? rest / weken : null,
          /* v23.207: de marge hoort erbij. Zonder hem kan het scherm alleen een puntschatting tegen
             de nodige snelheid houden, en dat is bij een brede band elke dag een ander oordeel. */
          tempo: m ? m.gem : null, marge: m ? m.marge : null, klaar: rest === 0};""")

    rep("""  } else if(ds.nodig !== null && ds.tempo >= ds.nodig){
    h += "<p style='margin:8px 0 0; font-size:.9rem'><span class='vgKoers ja'>"+ct("op koers","on track")+
      "</span> "+ct("In dit tempo ben je er op tijd.","At this pace you'll get there in time.")+"</p>";
  } else {
    /* Geen rood. Stefan, v19.90: een deadline die je mist is een indicator die liegt. Het doel is
       een richting, en het getal dat telt blijft hoe vaak je terugkomt. */
    h += "<p style='margin:8px 0 0; font-size:.9rem'><span class='vgKoers nee'>"+ct("later","later")+
      "</span> "+ct("In dit tempo wordt het later dan je datum. Dat is geen fout; een doel is hier een "+
                    "richting.",
                    "At this pace it'll be later than your date. That's not a failure; a goal here is "+
                    "a direction.")+"</p>";
  }""",
        """  } else {
    /* v23.207: hier stond ds.tempo >= ds.nodig, een puntschatting tegen een grens. Bij een marge van
       61 op een tempo van 80 zegt zo'n vergelijking elke dag iets anders, en een indicator die
       omslaat op ruis is precies wat Stefan een liegende indicator noemt.

       De regel is nu: een oordeel pas als de HELE band aan één kant ligt. Ligt de nodige snelheid
       er middenin, dan staat er wat waar is, mét de band erbij, want dat getal wordt vanzelf
       smaller. Zo hangt de uitspraak aan de onzekerheid en niet aan een drempel op het aantal
       metingen; dat was de vorige manier om hetzelfde te zeggen, alleen grover. */
    var mg = ds.marge || 0;
    var laag = ds.tempo - mg, hoog = ds.tempo + mg;
    var bandZin = ct("Je band loopt van "+getal1(Math.max(0, laag))+" tot "+getal1(hoog)+" per week en wordt smaller met elke dag die je meet.",
                     "Your band runs from "+getal1(Math.max(0, laag))+" to "+getal1(hoog)+" a week and narrows with every day you measure.");
    if(ds.nodig !== null && laag >= ds.nodig){
      h += "<p style='margin:8px 0 0; font-size:.9rem'><span class='vgKoers ja'>"+ct("op koers","on track")+
        "</span> "+ct("Ook onderin je band haal je het op tijd. ","Even at the bottom of your band you make it in time. ")+bandZin+"</p>";
    } else if(ds.nodig !== null && hoog < ds.nodig){
      /* Geen rood. Stefan, v19.90: een deadline die je mist is een indicator die liegt. Het doel is
         een richting, en het getal dat telt blijft hoe vaak je terugkomt. */
      h += "<p style='margin:8px 0 0; font-size:.9rem'><span class='vgKoers nee'>"+ct("later","later")+
        "</span> "+ct("Ook bovenin je band wordt het later dan je datum. Dat is geen fout; een doel is hier een richting. ",
                      "Even at the top of your band it'll be later than your date. That's not a failure; a goal here is a direction. ")+bandZin+"</p>";
    } else {
      h += "<p class='muted' style='margin:8px 0 0; font-size:.9rem'>"+
        ct("Nog niet te zeggen: de "+getal1(ds.nodig)+" die je nodig hebt ligt binnen je band. ",
           "Can't be said yet: the "+getal1(ds.nodig)+" you need falls inside your band. ")+bandZin+"</p>";
    }
  }""")

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    assert "metingenNieuweMaat" not in src, "metingenNieuweMaat staat er nog"
    assert "Math.max(1, 3 - " not in src, "er telt nog een plek zelf zijn wachttijd"
    assert src.count("function tempoMeting(") == 1
    assert src.count("tempoWachtZin(") >= 5, "verwacht vier aanroepers plus de definitie"
    APP.write_text(src, encoding="utf-8")
    print("index.html: één reeks, één schatter, en de marge doet het werk van de drempel")
else:
    print("index.html: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
