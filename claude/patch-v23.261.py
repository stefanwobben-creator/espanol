# patch-v23.261.py - de drill telt nu echt niet mee, in plaats van bij ongeluk.
#
# WAT ER AAN DE HAND IS
#
# Op het scherm van de drill staat, sinds hij bestaat: "Verse vragen, en ze tellen niet mee voor je
# doosje." Dat was waar, maar niet omdat iets het afdwong. Het was waar omdat de oude regel elke
# misser onherroepelijk afstrafte: je kwam alleen in de drill terecht NA een misser, en daarmee lag
# de doos die dag toch al op nul.
#
# v23.259 haalt die regel weg. Vijf of meer antwoorden met 75 procent goed levert nu een doos
# omhoog, en daarmee zou een drill van acht vragen direct na de uitleg je doosje kunnen promoveren.
# Dan staat er een onwaarheid op het scherm, en dat is erger dan een strenge regel.
#
# Het is ook inhoudelijk mis. Wat je goed doet meteen nadat je de uitleg hebt gelezen, meet of je
# het net gelezen hebt. Kornell en Bjork noemen dat illusions of competence: vlot kunnen ophalen
# binnen de sessie voorspelt slecht of je het volgende week nog weet. De opfrisser en de
# oefensessie beginnen allebei zonder uitleg; de drill komt er juist vlak achteraan.
#
# WAT DEZE PATCH DOET
#
# De drill krijgt een eigen kanaal, en een antwoord uit dat kanaal werkt wel de tellers en het
# ledger bij (het is geschiedenis) maar raakt de doos, de vervaldatum en de staat van dienst niet
# aan. Daarmee klopt de zin op het scherm omdat de code hem afdwingt, en niet bij toeval.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if 'GRAM_KANAAL_TELT_NIET' in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


# 1. de drill herkenbaar maken
rep("""    id: id, concept: cid, drill: true,""",
    """    // v23.261: drillSess en niet drill, want `drill` betekent bij een concept iets anders (de
    // doorsteek naar de Conjugador). gwKanaal() leest dit veld.
    id: id, concept: cid, drill: true, drillSess: true,""")

# 2. het kanaal
rep('function gwKanaal(o){ return o && o.sessie ? "sessie" : (o && o.opfris ? "opfris" : "microles"); }',
    '''function gwKanaal(o){
  if(o && o.drillSess) return "drill";
  if(o && o.sessie) return "sessie";
  return (o && o.opfris) ? "opfris" : "microles";
}''')

# 3. en gramBij laat de doos met rust
OUD = """  // de tellers lopen altijd door; die zijn de geschiedenis en niet het oordeel
  if(goed) st.goed++;
  else { st.fout++; st.laatst = today(); }
"""
NIEUW = """  // de tellers lopen altijd door; die zijn de geschiedenis en niet het oordeel
  if(goed) st.goed++;
  else { st.fout++; st.laatst = today(); }

  /* v23.261: er zijn kanalen die niets over je geheugen zeggen, en de drill is er een. Hij komt
     direct na de uitleg en direct na een misser, dus wat je daar goed doet meet of je het net
     gelezen hebt (Kornell en Bjork, illusions of competence). Op het scherm van de drill staat al
     dat hij niet meetelt voor je doosje; tot v23.259 was dat waar omdat elke misser toch alles
     kostte, en vanaf nu is het waar omdat het hier staat.

     De tellers en het ledger hierboven lopen wel door: dat is geschiedenis, geen oordeel. Wat er
     NIET gebeurt is de doos, de vervaldatum en de staat van dienst (st.rij), want die drie zijn
     samen het oordeel. */
  if(GRAM_KANAAL_TELT_NIET[kanaal || ""]){ S.gram[sleutel] = st; return; }
"""
rep(OUD, NIEUW)

rep("var GRAM_OORDEEL_MIN = 5;     // minder antwoorden vandaag op dit doosje is geen oordeel",
    """/* Kanalen waarvan een antwoord de doos niet mag raken. Zie de kop in gramBij. */
var GRAM_KANAAL_TELT_NIET = {drill: 1};
var GRAM_OORDEEL_MIN = 5;     // minder antwoorden vandaag op dit doosje is geen oordeel""")

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
