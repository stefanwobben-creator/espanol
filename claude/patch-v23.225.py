#!/usr/bin/env python3
# v23.225 - de dag wordt in één keer afgerekend, en een misser levert meteen oefening op
#
# Stefan, 1 sep: "wat bij de grammatica toetsjes soms wat raar is dat ik maar een vraag krijg, dat
# voelt beetje raar. en ik kreeg een toets met de verschillende tijden voor de werkwoorden, maar die
# was te moeilijk, dus daar zou je nu verwachten dat er een extra los komt."
#
# HET GETAL DAT ERONDER LIGT
#
# De opfrisser is één vraag met drie knoppen. Een goed antwoord daarop loopt via gramBij() naar de
# tak die het doosje een hele stap verder zet: van doos 2 (drie dagen) naar doos 3 (acht dagen), of
# van 3 naar 4 (drie weken). Eén keer raden is 33 procent, en dat is genoeg om een onderwerp weken
# van je scherm te halen.
#
# Dat is exact dezelfde fout als in v23.212, alleen op een andere as. Daar ging het over het aantal
# KNOPPEN (101 van de 153 patronen gaven er twee, dus vijftig procent raden); hier over het aantal
# VRAGEN. De regel die daar is ingevoerd, gramHalfBewijs(), zegt: bij twee knoppen is één goed
# antwoord een half bewijs. Bij één vraag met drie knoppen zei niemand iets.
#
# DRIE DINGEN, EN ZE HANGEN AAN ELKAAR
#
# 1. DE OPFRISSER WORDT TWEE VRAGEN. Twee keer drie knoppen is 11 procent raden in plaats van 33.
#    Dat is de goedkoopste ingreep die er is: één cijfer in gcOpfrisBouw().
#
# 2. DE DAG WORDT ALS GEHEEL AFGEREKEND. Dit is de echte reparatie, en zonder deze zou punt 1 niets
#    doen. gramBij() velde zijn oordeel op het EERSTE antwoord van de dag:
#
#        eerste antwoord goed  -> doos omhoog, due weken vooruit
#        tweede antwoord fout  -> due terug naar morgen, MAAR de doos blijft staan
#
#    Met twee vragen zou dat betekenen: eerste goed, tweede fout, en je staat een doos hoger dan
#    voordat je begon. De volgende keer dat je hem goed hebt, ga je vanaf dat te hoge punt verder.
#
#    Vanaf nu onthoudt de doos waar hij aan het begin van vandaag stond (boxVoor) en wordt de stand
#    bij elk antwoord opnieuw berekend vanaf dat punt. Ging er vandaag iets mis, dan geen promotie,
#    punt. Ging er niets mis, dan precies één stap, hoe vaak je het onderwerp vandaag ook aanraakt.
#
#    Bijeffect dat de moeite waard is: twee goede antwoorden op tweekeuzevragen (samen 25 procent
#    raden) tellen nu samen als vol bewijs. Bewijs is een kans en geen gebeurtenis, en dat is precies
#    wat v23.212 al zei.
#
# 3. EN NA EEN MISSER KOMT ER METEEN MEER. Ging er in een stap iets mis, dan staat er nu een knop
#    "Nog vijf van dit onderwerp": vijf vers gegenereerde vragen over hetzelfde concept. Tot nu toe
#    stond daar alleen "Klik gerust nog een keer door deze stap heen" als grijze zin, en de enige
#    echte vervolgstap kwam pas de volgende dag.
#
#    Die vijf vragen kunnen de doos niet omhoog duwen, en dat volgt vanzelf uit punt 2: er is vandaag
#    al een misser geweest. Ze zijn oefening, geen herkansing. Dat verschil is de reden dat deze
#    ronde geen zachtere doos-regel bevat: die is in v23.208 al een keer voorgesteld en afgewezen.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.225"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "st.boxVoor" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # =========================================================================================
    # 1. de dag als geheel
    # =========================================================================================
    rep("""  if(st.bd !== today()){
    st.bd = today();
    if(!goed){
      st.half = 0;
      st.box = 0;
      st.due = addDays(today(), 1);
    } else if(gramHalfBewijs(keuzes) && !st.half){
      /* Het eerste halve bewijs. De doos blijft staan, maar je ziet het morgen terug: een tweede
         meting die een week later komt meet een andere kennistoestand en bevestigt dus niets. */
      st.half = 1;
      st.due = addDays(today(), 1);
    } else {
      st.half = 0;
      st.box = Math.min((st.box || 0) + 1, GRAM_BOX.length - 1);
      st.due = addDays(today(), GRAM_BOX[st.box]);
    }
  } else if(!goed){
    /* Later op de dag alsnog mis. De doos blijft staan (het oordeel van vandaag is al geveld), maar
       je ziet het morgen terug in plaats van pas over drie of acht dagen. Zonder deze regel zou een
       onderwerp dat je 's ochtends goed had en 's middags vijf keer fout gewoon wegzakken.
       v23.212: en een half bewijs van vanochtend is na vijf keer mis geen bewijs meer. */
    st.half = 0;
    st.due = addDays(today(), 1);
  }
  S.gram[cid] = st;""",
"""  /* v23.225: de dag wordt als geheel afgerekend in plaats van op het eerste antwoord.

     Hier stond een tak voor "eerste antwoord van vandaag" en een tak voor "later op de dag". Het
     oordeel viel bij het eerste antwoord en kon daarna alleen nog de due-datum terugtrekken, niet
     de doos. Met één vraag per opfrisser viel dat niet op. Met twee vragen wel: eerste goed, tweede
     fout, en je stond een doos hoger dan voordat je begon.

     Nu onthoudt de doos waar hij aan het begin van vandaag stond, en wordt de stand bij elk antwoord
     opnieuw berekend vanaf dát punt. Daarmee is de uitkomst niet meer afhankelijk van de volgorde
     waarin je de vragen toevallig goed of fout had, en kan geen enkel aantal extra antwoorden op
     dezelfde dag de doos verder duwen dan één stap. */
  if(st.bd !== today()){
    st.bd = today();
    st.boxVoor = st.box || 0;    // waar stond hij toen vandaag begon
    st.dagMis = 0;
    st.dagGoed = 0;
  }
  if(goed) st.dagGoed = (st.dagGoed || 0) + 1;
  else st.dagMis = (st.dagMis || 0) + 1;

  if(st.dagMis){
    /* Eén misser vandaag en de promotie gaat niet door, hoeveel je er daarna ook goed hebt. Dit is
       bewust hetzelfde harde oordeel als voorheen: de zachtere variant is in v23.208 voorgesteld en
       door Stefan afgewezen. Wat je hierna nog oefent is oefening, geen herkansing. */
    st.half = 0;
    st.box = 0;
    st.due = addDays(today(), 1);
  } else if(gramHalfBewijs(keuzes) && st.dagGoed < 2 && !st.half){
    /* Het eerste halve bewijs. De doos blijft staan, maar je ziet het morgen terug: een tweede
       meting die een week later komt meet een andere kennistoestand en bevestigt dus niets.
       v23.225: `st.dagGoed < 2` erbij. Twee goede tweekeuzevragen op dezelfde dag is samen 25
       procent raden, en dat is minder dan de 33 procent van één driekeuzevraag die hier altijd al
       als vol bewijs gold. Bewijs is een kans, geen gebeurtenis. */
    st.half = 1;
    st.due = addDays(today(), 1);
  } else {
    st.half = 0;
    st.box = Math.min((st.boxVoor || 0) + 1, GRAM_BOX.length - 1);
    st.due = addDays(today(), GRAM_BOX[st.box]);
  }
  S.gram[cid] = st;""")

    # =========================================================================================
    # 2. de opfrisser krijgt een tweede vraag
    # =========================================================================================
    rep("""  var vragen = [];
  try { vragen = gcMaakVragen(c, 1); } catch(e){ vragen = []; }
  if(!vragen.length) return null;""",
"""  /* v23.225: twee vragen in plaats van één. Stefan: "dat ik maar een vraag krijg, dat voelt beetje
     raar." Dat gevoel klopte met een getal erachter: één driekeuzevraag is 33 procent raden, en een
     goed antwoord zette het doosje toch een hele stap verder. Twee vragen maakt er 11 procent van.

     Twee en niet drie: dit is een opfrisser en geen les. Hij hoort in een halve minuut klaar te
     zijn, want hij staat vóór het echte onderwerp in dezelfde dagles. */
  var vragen = [];
  try { vragen = gcMaakVragen(c, GC_OPFRIS_VRAGEN); } catch(e){ vragen = []; }
  if(vragen.length < GC_OPFRIS_VRAGEN) return null;""")
    rep("""    pitch: ct("Eén vraag. Je had dit al een keer goed.", "One question. You had this right before."),
    pitchEn: "One question. You had this right before.",""",
"""    pitch: ct("Twee vragen. Je had dit al een keer goed.", "Two questions. You had this right before."),
    pitchEn: "Two questions. You had this right before.",""")

    # =========================================================================================
    # 3. de drill: vijf verse vragen over hetzelfde concept
    # =========================================================================================
    rep("""function gcOpfrisId(cid){ return "opfris-" + String(cid || "").replace(/^concept-/, ""); }""",
"""function gcOpfrisId(cid){ return "opfris-" + String(cid || "").replace(/^concept-/, ""); }
/* v23.225: hoeveel vragen een opfrisser en een drill hebben. Als getal en niet als losse cijfers in
   de code, want de proef in pw-opfris.js rekent ermee en die mag niet zijn eigen aanname doen. */
var GC_OPFRIS_VRAGEN = 2;
var GC_DRILL_VRAGEN = 5;
function gcDrillId(cid){ return "drill-" + String(cid || "").replace(/^(concept|opfris)-/, ""); }
/* Vijf verse vragen over hetzelfde concept, aangeboden op het moment dat er net iets misging.

   Stefan, 1 sep: "die was te moeilijk, dus daar zou je nu verwachten dat er een extra los komt."
   Dat kwam er niet: er stond een grijze zin ("klik gerust nog een keer door deze stap heen") en het
   onderwerp kwam pas de volgende dag terug.

   Dit kan je doosje niet omhoog duwen en dat hoeft hier niet afgedwongen te worden: gramBij() ziet
   sinds v23.225 dat er vandaag een misser was en laat de promotie dan vallen, hoeveel je er hierna
   ook goed hebt. Oefening, geen herkansing. */
function gcDrillBouw(id){
  var cid = String(id || "").replace(/^drill-/, "");
  var c = gcConcept(cid);
  if(!c) return null;
  var vragen = [];
  try { vragen = gcMaakVragen(c, GC_DRILL_VRAGEN); } catch(e){ vragen = []; }
  if(!vragen.length) return null;
  var naam = ct(c.naam, c.naamEn || c.naam);
  return {
    icon: c.icon || "\\ud83c\\udfaf",
    id: id, concept: cid, drill: true,
    titel: ct("Nog even oefenen: " + naam, "A bit more practice: " + naam),
    titelEn: "A bit more practice: " + (c.naamEn || c.naam),
    pitch: ct(vragen.length + " nieuwe vragen. Ze tellen niet mee voor je doosje.",
              vragen.length + " fresh questions. They do not count towards your box."),
    pitchEn: vragen.length + " fresh questions. They do not count towards your box.",
    stappen: [{ kop: ct("Nog even oefenen", "A bit more practice"),
                kopEn: "A bit more practice",
                uitleg: "", uitlegEn: "",
                vragen: vragen }]
  };
}""")
    rep("""var GC_BOUWERS = [
  {pre: "concept-", bouw: function(id){ return gcBouw(id.replace(/^concept-/, "")); }},
  {pre: "opfris-",  bouw: function(id){ return gcOpfrisBouw(id); }}
];""",
"""var GC_BOUWERS = [
  {pre: "concept-", bouw: function(id){ return gcBouw(id.replace(/^concept-/, "")); }},
  {pre: "opfris-",  bouw: function(id){ return gcOpfrisBouw(id); }},
  {pre: "drill-",   bouw: function(id){ return gcDrillBouw(id); }}
];""")

    # =========================================================================================
    # 4. de knop, op het moment dat er net iets misging
    # =========================================================================================
    rep("""      (perfect ? "" : "<p class='muted'>"+ct("Klik gerust nog een keer door deze stap heen, dat is precies waar hij voor is.","Feel free to run through this step again, that's exactly what it's for.")+"</p>")+""",
"""      /* v23.225: hier stond alleen een grijze zin ("klik gerust nog een keer door deze stap heen").
         Dat is een uitnodiging zonder knop, en op het moment dat je net iets fout had is dat precies
         het moment waarop je hem nodig hebt. Nu een echte knop, en alleen als er iets misging en het
         onderwerp een concept heeft om vragen uit te maken. */
      (perfect ? "" : (o.concept && !o.drill
        ? "<div class='row' style='margin-top:10px'><button class='ghost' id='gwDrill'>\\u2795 "+
            ct("Nog "+GC_DRILL_VRAGEN+" van dit onderwerp","Another "+GC_DRILL_VRAGEN+" of this topic")+"</button></div>"+
          "<p class='muted' style='margin:6px 0 0; font-size:.85rem'>"+
            ct("Verse vragen, en ze tellen niet mee voor je doosje.",
               "Fresh questions, and they do not count towards your box.")+"</p>"
        : "<p class='muted'>"+ct("Klik gerust nog een keer door deze stap heen, dat is precies waar hij voor is.","Feel free to run through this step again, that's exactly what it's for.")+"</p>"))+""")
    rep("""  b = document.getElementById("gwHerhaal"); if(b) b.onclick = function(){ gwStart(gwSess.id, gwSess.stap); };""",
"""  b = document.getElementById("gwHerhaal"); if(b) b.onclick = function(){ gwStart(gwSess.id, gwSess.stap); };
  /* v23.225: stap 0, want een drill heeft er maar één. Zonder dat cijfer zou gwStart() de opgeslagen
     voortgang van dit id volgen en die staat na één ronde op "klaar". */
  b = document.getElementById("gwDrill");
  if(b) b.onclick = function(){ gwStart(gcDrillId(gwSess.id.replace(/^concept-/, "")), 0); };""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    # een drill mag nooit door de opfris-omleiding worden opgeslokt
    assert 'if(!/^concept-/.test(id || "")) return null;' in src, \
        "gwOpfrisInPlaats laat niet meer alleen concept- door"
    for nodig in ["function gcDrillBouw(", "function gcDrillId(", 'pre: "drill-"',
                  "var GC_OPFRIS_VRAGEN = 2", "var GC_DRILL_VRAGEN = 5",
                  'id="gwDrill"' if 'id="gwDrill"' in src else "gwDrill",
                  "st.boxVoor", "st.dagMis", "st.dagGoed"]:
        assert nodig in src, "ontbreekt: " + nodig
    # de oude takken moeten weg zijn, anders staan er twee oordelen naast elkaar
    assert "st.box = Math.min((st.box || 0) + 1, GRAM_BOX.length - 1)" not in src, \
        "de oude promotieregel staat er nog"
    assert src.count("st.box = Math.min((st.boxVoor || 0) + 1, GRAM_BOX.length - 1)") == 1, \
        "de nieuwe promotieregel hoort er precies één keer te staan"
    assert src.count("gcMaakVragen(c, GC_OPFRIS_VRAGEN)") == 1
    assert src.count("gcMaakVragen(c, GC_DRILL_VRAGEN)") == 1
    APP.write_text(src, encoding="utf-8")
    print("index.html: de dag wordt in één keer afgerekend, opfrisser 2 vragen, drill van 5 erbij")
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
