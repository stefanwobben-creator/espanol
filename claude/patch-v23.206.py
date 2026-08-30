#!/usr/bin/env python3
# v23.206 - de voortgangspagina telt overal hetzelfde
#
# Stefan, 30 aug: "waarom kan de app nog niet voorspellen? ik heb inmiddels een streak van 40 dagen."
#
# WAT ER OP ZIJN SCHERM STOND
#
#   kop         : 639 woorden houd je actief bij
#   lijn eronder: "van 493 op 17 augustus naar 621 nu"
#   de as       : "de schaal loopt tot 715, je eigen hoogste punt"
#   doelkaart   : "Je hebt 3 dagmetingen over 13 dagen ... over 2 dagen"
#   voorspelling: "Er liggen 5 weekmetingen. Vanaf drie kan hier een strook staan. Nog 1 week."
#
# Vijf getallen over dezelfde vraag, en drie ervan kloppen niet.
#
#   621 is niet "nu". Het is zijn laatste WEEKmeting, van zes dagen eerder. De kop rekent live.
#   715 is niet zijn hoogste punt. Het is ceil(max * 1,15), de bovenkant van de as. Zijn hoogste
#       punt is 621, en dat getal staat er niet.
#   "5 weekmetingen, nog 1 week" is de verkeerde teller bij de verkeerde poort. voorspelWaar()
#       hangt sinds v23.203 aan tempoMeting(), en die kijkt naar DAGmetingen. De zin ernaast telde
#       Object.keys(S.meting).length (alles, ook de weken zonder dekw) en rekende nog = max(1, 3-5)
#       = 1. Dat getal is geklemd op 1, dus daar stond "nog 1 week te gaan" ongeacht wat er lag, en
#       het zou er over een maand nog staan.
#
# WAAROM DE VOORSPELLING ZELF NIET LIEGT
#
# Die zwijgt terecht. De dagmeting is er pas sinds v23.203; wat daarvoor ligt zijn weekmetingen, en
# alleen de weken die dekw bewaren doen mee. Dat zijn er bij Stefan twee (17 en 24 aug), plus het
# punt van vandaag: drie. tempoDagMeting() vraagt vijf punten over minstens zeven dagen. De spreiding
# is met dertien dagen al ruim genoeg; het zijn de punten die ontbreken, en die komen nu per dag
# binnen omdat boot() dagMetingSchrijf() aanroept.
#
# Veertig dagen oefenen leverde drie meetpunten op, en dat is de eigenlijke fout van de vorige opzet:
# de app schreef elke dag op hoeveel je DEED (S.dagStats, de streak) en maar eens per week waar je
# STOND. Die tweede reeks is de enige die een voorspelling voedt.
#
# WAT DEZE RONDE DOET
#
#   1. De lijn tekent dezelfde reeks als de meter. vgReeks() geeft de dagreeks zodra die twee punten
#      heeft en valt anders terug op de weekreeks. Eén reeks onder één kop.
#   2. Het bijschrift noemt de datum van het laatste punt in plaats van "nu", tenzij dat punt echt
#      van vandaag is.
#   3. Het getal dat "je hoogste punt" heet is het hoogste punt. De as-top staat er los naast, met
#      wat hij is.
#   4. De voorspelling wacht met dezelfde zin en dezelfde getallen als de doelkaart: tempoWachtZin().
#      Eén plek, en die hangt aan tempoStand(), dezelfde drempels als tempoDagMeting().
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.206"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function vgReeks(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:120])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. één reeks voor de lijn
# =============================================================================================
REEKS = r'''/* v23.206: welke reeks tekent de lijn hieronder.

   Tot deze versie was dat altijd de weekreeks, terwijl de meter sinds v23.203 de dagreeks gebruikt.
   Twee reeksen onder één kop lopen uit elkaar, en dat deden ze ook: op Stefans scherm stond "639
   woorden houd je actief bij" boven een lijn die op 621 eindigde met het woord "nu" erbij. 621 was
   zijn laatste weekmeting, van zes dagen eerder.

   De dagreeks gaat voor zodra er twee punten liggen, want met één punt is er geen lijn. Daaronder
   ligt de weekreeks als terugval, in dezelfde maat (dekw), zodat iemand die net begint niet naar
   een leeg vak kijkt. */
function vgReeks(nivs){
  var d = S.dagMeting || {}, ds = Object.keys(d).sort(), uit = [], i, m;
  for(i = 0; i < ds.length; i++){
    m = d[ds[i]];
    if(!m || !m.dekw) continue;
    uit.push({d: ds[i], actief: vgSomVeld(m.dekw, nivs), bron: "dag"});
  }
  if(uit.length >= 2) return uit;
  return vgWeken(nivs).filter(function(x){ return x.actief !== null; })
    .map(function(x){ return {d: x.d, actief: x.actief, bron: "week"}; });
}
'''

if DOE_APP:
    rep("function vgRij(naam, sub, pct, cijf, soort){", REEKS + "function vgRij(naam, sub, pct, cijf, soort){")

# =============================================================================================
# 2. de lijn, en een bijschrift dat geen dingen beweert die niet waar zijn
# =============================================================================================
if DOE_APP:
    rep("""  var wk = vgWeken(c.samen.nivs).filter(function(x){ return x.actief !== null; });
  if(wk.length < 2){""",
        """  var wk = vgReeks(c.samen.nivs);
  if(wk.length < 2){""")

    rep("""  var top = 0, i, x, y, d = "", pad = "";
  for(i = 0; i < wk.length; i++) top = Math.max(top, wk[i].actief);
  if(top <= 0) return "";
  top = Math.ceil(top * 1.15);""",
        """  var hoogst = 0, i, x, y, d = "", pad = "";
  for(i = 0; i < wk.length; i++) hoogst = Math.max(hoogst, wk[i].actief);
  if(hoogst <= 0) return "";
  /* v23.206: hier stond top = ceil(max * 1,15) en daarna "de schaal loopt tot 715, je eigen hoogste
     punt". 715 was niet zijn hoogste punt maar de bovenkant van de as, vijftien procent erboven
     zodat de lijn niet tegen de rand plakt. Twee dingen, één naam, en het getal dat hij wél zocht
     (621) stond er niet bij. Nu staan ze allebei, elk met wat het is. */
  var top = Math.ceil(hoogst * 1.15);""")

    rep("""    "<p class='muted' style='margin:0; font-size:.8rem'>"+
      ct("Wat je actief bijhoudt, van <b>"+wk[0].actief+"</b> op "+datumUit(wk[0].d)+" naar <b>"+
         wk[wk.length-1].actief+"</b> nu. De schaal loopt tot "+top+", je eigen hoogste punt.",
         "What you actively keep up, from <b>"+wk[0].actief+"</b> on "+datumUit(wk[0].d)+" to <b>"+
         wk[wk.length-1].actief+"</b> now. The scale runs to "+top+", your own highest point.")+"</p>";""",
        """    "<p class='muted' style='margin:0; font-size:.8rem'>"+
      /* v23.206: "nu" alleen als het laatste punt echt van vandaag is. Anders staat er de datum van
         dat punt, want een lijn die gisteren eindigt en "nu" zegt spreekt de kop erboven tegen. */
      ct("Wat je actief bijhoudt, van <b>"+wk[0].actief+"</b> op "+datumUit(wk[0].d)+" naar <b>"+
         wk[wk.length-1].actief+"</b> "+(wk[wk.length-1].d === today() ? "nu" : "op "+datumUit(wk[wk.length-1].d))+
         ". Je hoogste punt is "+hoogst+"; de as loopt tot "+top+" zodat de lijn niet tegen de rand plakt.",
         "What you actively keep up, from <b>"+wk[0].actief+"</b> on "+datumUit(wk[0].d)+" to <b>"+
         wk[wk.length-1].actief+"</b> "+(wk[wk.length-1].d === today() ? "now" : "on "+datumUit(wk[wk.length-1].d))+
         ". Your highest point is "+hoogst+"; the axis runs to "+top+" so the line doesn't hug the edge.")+"</p>";""")

# =============================================================================================
# 3. de voorspelling wacht met dezelfde zin en dezelfde getallen als de doelkaart
# =============================================================================================
if DOE_APP:
    rep("""    var gemeten = Object.keys(S.meting || {}).length, nog = Math.max(1, 3 - gemeten);
    return h + "<p class='muted'>"+
      ct("Nog niet te zeggen. "+weekMetingZin(gemeten)+" Vanaf drie kan hier een strook staan in plaats van een gok. Nog <b>"+nog+"</b> "+(nog === 1 ? "week" : "weken")+" te gaan.",
         "Can't be said yet. "+weekMetingZin(gemeten)+" From three on a band can appear here instead of a guess. <b>"+nog+"</b> more "+(nog === 1 ? "week" : "weeks")+" to go.")+"</p>"+
      doelRegelHtml();""",
        """    /* v23.206: hier stond het aantal WEEKmetingen naast een poort die sinds v23.203 op DAGmetingen
       staat, en "nog <b>1</b> week te gaan" uit nog = max(1, 3 - gemeten). Met vijf weekmetingen gaf
       dat max(1, -2) = 1: een getal dat door de klem nooit meer kon veranderen, dus daar stond
       eeuwig "nog 1 week". Stefan las dat naast "over 2 dagen" op de doelkaart en had gelijk dat het
       niet kon kloppen.

       De wachtzin komt nu uit tempoWachtZin(), dezelfde functie die de doelkaart voedt, die aan
       tempoStand() hangt, die dezelfde twee drempels gebruikt als tempoDagMeting(). Eén keten van de
       meter naar de zin, dus er is geen plek meer waar ze uit elkaar kunnen lopen. */
    var wz = tempoWachtZin("A1");
    return h + "<p class='muted'>"+
      ct("Nog niet te zeggen. ", "Can't be said yet. ") +
      (wz ? wz + ct(" Dan staat hier een strook in plaats van een gok.",
                    " Then a band appears here instead of a guess.")
          : ct("De reeks ligt er, maar een lijn erdoorheen levert nog geen tempo op.",
               "The series is there, but a line through it yields no pace yet.")) + "</p>"+
      doelRegelHtml();""")

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    # de toelichting erboven zei hetzelfde als het bijschrift, en was dus even onwaar
    rep("""  /* De schaal loopt tot je eigen hoogste punt en niet tot de noemer. Eerst deed hij dat wel, en dan""",
        """  /* De schaal loopt tot even boven je eigen hoogste punt en niet tot de noemer. Eerst deed hij dat wel, en dan""")
    assert src.count("function vgReeks(") == 1
    assert ", je eigen hoogste punt" not in src, "de oude bewering staat er nog"
    assert ", your own highest point" not in src, "de oude bewering staat er nog (en)"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de lijn en de wachtzin komen uit dezelfde reeks als de meter")
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
