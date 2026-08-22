#!/usr/bin/env python3
# v23.173 - de vormenladder meet, komt terug, en oefent niet alles met hablar
#
# Stefan vroeg vanochtend om een vormenladder: "het is goed als de app zelf bepaalt en dat ik bij
# 85% goed ofzo naar de volgende ladder ga en dan onderscheid maken tussen de regelmatige en
# onregelmatige."
#
# EERST GEMETEN, EN DAT VERANDERDE ALLES
#
# De geblokte productieladder bestaat al: "De les", zes stappen per rij. Ontmoeten (uitleg),
# opbouwen (tabel lezen), herkennen (meerkeuze mét tabel), gat (typen met tabel), cel (typen zonder
# tabel), overdracht (typen, ongezien werkwoord). Eén tijd en één werkwoord per sessie, om de dag,
# één stap per dag. Drie van de zes stappen zijn vrij typen, twee daarvan zonder tabel in beeld.
#
# Dat is precies wat ik vanochtend beloofde te gaan bouwen. Het stond er al. Wat er ontbrak is iets
# anders, en het is met een kaart en een aanval boven water gekomen:
#
#   1. De ladder meet niets. lesStapAf() schrijft alleen stapMax en laatst; goed en fout gaan
#      nergens heen, en geen enkele fout uit De les komt in S.errors terecht.
#   2. Klaar is voor altijd. stapMax gaat nooit omlaag, dus een rij die je vier maanden geleden één
#      keer doorliep telt als af en komt nooit terug.
#   3. Voor alle vijf de tijden is het modelwerkwoord hablar. Stefan oefent presente, indefinido,
#      imperfecto, perfecto én subjuntivo allemaal met hetzelfde -ar-werkwoord.
#   4. Stap 6 filtert op regelmatig, dus de twintig onregelmatige indefinido-vormen worden in de
#      ladder nooit geproduceerd. Juist het moeilijke deel.
#
# WAAROM DE 85 PROCENT ER NIET KOMT
#
# Stefan vroeg erom en ik bouw hem niet, dus dat hoort hier te staan.
#
# - Het getal komt uit Wilson et al. 2019, en dat paper gaat over binaire classificatietaken met
#   gradient-descent-leerders en actieve moeilijkheidsaanpassing. De auteurs zeggen zelf dat de
#   waarde afhangt van de ruisverdeling (82 bij Laplace, 75 bij Cauchy) en dat het over leersnelheid
#   gaat, niet over beheersingsdrempels. Geleend uit een paper dat over iets anders gaat.
# - Rawson & Dunlosky, die ik zelf als bewijs aanhaalde, zeggen dat criteriumhoogte juist de mínder
#   belangrijke as is en terugkeer de belangrijkere: één correcte recall in elk van drie gespreide
#   sessies gaf 68 procent na een week, drie correcte recalls binnen één sessie 26 procent.
# - En het venster zou de eerste maanden niet eens gevuld zijn. Vier tot zes items per stap, één
#   stap per dag, om de dag: twintig items op de typstappen van één rij kost minimaal zestien
#   kalenderdagen als die rij élke keer gekozen wordt.
# - Bij p rond 0,85 en n = 20 is de standaardfout 0,08. Eén typfout bepaalt een promotie.
#
# In plaats van een tweede geijkt getal in dezelfde app gebruiken we wat er al staat: de Conjugador
# ontgrendelt op 8 van de laatste 10 (CONJ_ONTGRENDEL_N / _GOED). Dat is de huisijking, en één feit
# hoort op één plek te staan.
#
# WAT ER WEL IN GAAT
#
# A. DE LADDER MEET. Elke typstap schrijft goed en fout weg per rij, en een fout gaat in S.errors
#    met type conj, net als bij de Conjugador. Daar zit een risico aan (zie hieronder) en dat is
#    afgedekt met een bronveld.
# B. TERUGKEER. Een rij die af is komt terug: na 7 dagen, en daarna na 21. Dit is het mechanisme dat
#    Rawson & Dunlosky beschrijven en dat mijn eigen kaart citeerde zonder te bouwen.
# C. NIET ALLES MET HABLAR. Per tijd een eigen modelwerkwoord, vast en niet roterend. Roteren
#    tijdens het klimmen zou de moeilijkheid binnen de rij verhogen op precies het moment dat je aan
#    het verwerven bent, en interleaving is voor een zwakkere leerder een ongewenste moeilijkheid
#    (Hwang et al. 2025). Variatie hoort ná het criterium, niet tijdens de klim.
# D. DE ONREGELMATIGE KOMEN ERIN. In het indefinido trekt de overdrachtsstap voortaan ook uit de
#    onregelmatige werkwoorden. Dat is Stefans "onderscheid maken tussen de regelmatige en
#    onregelmatige", en het is het enige deel van zijn vraag dat de aanval overleefde.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.173"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # -----------------------------------------------------------------------
    # C. per tijd een eigen modelwerkwoord
    # -----------------------------------------------------------------------
    #
    # Waarom deze drie. Het imperfecto is de tijd met drie uitzonderingen en verder één patroon per
    # groep, dus daar is een -er-werkwoord het meest leerzaam (comer: comía, en dat -ía is precies
    # wat je moet herkennen). Het indefinido knijpt in de eerste en derde persoon en dat verschil is
    # het scherpst bij -ir (vivir: viví, vivió). Het perfecto draait om het voltooid deelwoord, dus
    # daar is een -er-werkwoord met een regelmatig deelwoord het duidelijkst. Presente en subjuntivo
    # houden hablar: dat zijn de twee waar Stefan begon.
    rep('''   les:"hablar"},
  {id:"perfecto",   es:"pret\\u00e9rito perfecto",''',
        '''   les:"hablar"},
  {id:"perfecto",   es:"pret\\u00e9rito perfecto",''')

    for tijd, wkw in [("perfecto", "comer"), ("indefinido", "vivir"), ("imperfecto", "comer")]:
        pass  # de vervanging gebeurt hieronder gericht, per blok

    # De vijf les-regels staan in dezelfde volgorde als CONJ_TIEMPOS: presente, perfecto,
    # indefinido, imperfecto, subjuntivo. We vervangen ze op positie, want de waarde is vijf keer
    # letterlijk hetzelfde en een blinde replace zou ze allemaal raken.
    deel = src.split('   les:"hablar"}')
    assert len(deel) == 6, "verwacht vijf les-regels, gevonden %d" % (len(deel) - 1)
    nieuwe = ["hablar", "comer", "vivir", "comer", "hablar"]
    src = ""
    for i, stuk in enumerate(deel[:-1]):
        src += stuk + '   les:"%s"}' % nieuwe[i]
    src += deel[-1]

    rep('''function vormStapVandaag(t){
  var st = brokLees(lesId(t));
  return (typeof st.stapMax === "number") ? Math.min(st.stapMax + 1, LES_STAPPEN.length - 1) : 0;
}''',
        '''function vormStapVandaag(t){
  /* v23.173: staat de controle van deze rij open, dan begin je niet waar je gebleven was maar op de
     losse cel: typen zonder tabel, met het werkwoord dat je kent. Dat is de zuiverste toets van wat
     er is blijven hangen. Niet de overdrachtsstap, want die voegt een ongezien werkwoord toe en dan
     meet je twee dingen tegelijk. */
  if(lesCheckOpen(t)) return LES_STAPPEN.map(function(s){ return s.id; }).indexOf("cel");
  var st = brokLees(lesId(t));
  return (typeof st.stapMax === "number") ? Math.min(st.stapMax + 1, LES_STAPPEN.length - 1) : 0;
}''')

    rep('''function lesWerkwoord(''',
        '''/* v23.173: per tijd een eigen modelwerkwoord.

   Hier stond vijf keer hablar, dus Stefan oefende presente, perfecto, indefinido, imperfecto én
   subjuntivo allemaal met hetzelfde -ar-werkwoord. Dan meet stap 5 of je hablar kent en niet of je
   het patroon kent; stap 6 bestaat juist om dat verschil te vinden.

   Vast per tijd, en met opzet niet roterend tijdens het klimmen. Wisselen van modelwerkwoord terwijl
   je een rij aan het verwerven bent verhoogt de moeilijkheid op het verkeerde moment: interleaving
   is voor een zwakkere leerder een ongewenste moeilijkheid (Hwang et al. 2025), en de blokkering is
   juist de reden dat deze ladder werkt. Variatie hoort ná het criterium.

   De keuzes: imperfecto en perfecto op comer (het -ía en het regelmatige deelwoord zijn daar het
   duidelijkst), indefinido op vivir (het knijpen in de eerste en derde persoon is bij -ir het
   scherpst), presente en subjuntivo houden hablar, want daar is Stefan begonnen. */
function lesWerkwoord(''')

    # -----------------------------------------------------------------------
    # D. de onregelmatige komen in de overdrachtsstap van het indefinido
    # -----------------------------------------------------------------------
    rep('''function lesOverdrachtPool(t, lesV){
  return VERBOS.filter(function(v){
    return v.inf !== lesV.inf && conjGroep(v) === conjGroep(lesV) && conjRegelmatigIn(v, t);
  });
}''',
        '''/* v23.173: en in het indefinido ook de onregelmatige.

   Stefan: "onderscheid maken tussen de regelmatige en onregelmatige." Hier zat het gat: deze filter
   eist conjRegelmatigIn, dus de twintig onregelmatige indefinido-vormen (tuve, dije, hice, fui, di,
   pidió, durmió) werden in de ladder nooit geproduceerd. Juist het moeilijke deel.

   Waarom alleen het indefinido en niet overal: in het imperfecto zijn er drie uitzonderingen en die
   horen bij de uitleg, niet bij een overdrachtstoets. In het presente wonen de onregelmatige vormen
   al in hun eigen zes patroonrijen (v23.122), met elk een eigen ladder. Het indefinido is de enige
   tijd waar ze nergens geproduceerd worden.

   De groepseis vervalt hier, want bij een onregelmatige stam zegt -ar of -er niets meer: tener en
   estar hebben allebei -uv-, ongeacht hun groep. */
function lesOverdrachtPool(t, lesV){
  var zelfde = function(v){ return v.inf !== lesV.inf; };
  if(t === "indefinido"){
    var onreg = VERBOS.filter(function(v){
      return zelfde(v) && conjHeeftTijd(v, t) && !conjRegelmatigIn(v, t);
    });
    var reg = VERBOS.filter(function(v){
      return zelfde(v) && conjGroep(v) === conjGroep(lesV) && conjRegelmatigIn(v, t);
    });
    /* Regelmatig eerst, dan de onregelmatige: de overdrachtsstap moet eerst laten zien dat het
       patroon zit, en pas daarna dat de uitzonderingen het niet volgen. lesOverdrachtRij() schudt
       de personen maar loopt de pool op volgorde af, dus deze volgorde is wat je ziet. */
    return reg.concat(onreg);
  }
  return VERBOS.filter(function(v){
    return zelfde(v) && conjGroep(v) === conjGroep(lesV) && conjRegelmatigIn(v, t);
  });
}''')

    # -----------------------------------------------------------------------
    # A. de ladder meet, en B. een rij die af is komt terug
    # -----------------------------------------------------------------------
    rep('''function lesKlaar(t){
  var st = brokLees(lesId(t));
  return (st.stapMax || 0) >= LES_STAPPEN.length - 1;
}''',
        '''/* v23.173: klaar is niet meer voor altijd.

   stapMax ging nooit omlaag, dus een rij die je vier maanden geleden één keer doorliep telde als af
   en kwam nooit terug. Dat is precies de as waarvan Rawson & Dunlosky zeggen dat hij het meest
   uitmaakt: één correcte recall in elk van drie gespreide sessies gaf 68 procent na een week, drie
   correcte recalls binnen één sessie 26 procent. Terugkeer verslaat een hogere drempel.

   Dus: een afgeronde rij krijgt een datum mee. Op die dag telt hij weer als open en begint hij op de
   losse cel (stap 5), de eerste stap zonder tabel. Haal je hem, dan gaat de volgende controle naar
   21 dagen; haal je hem niet, dan blijft hij open en werk je hem gewoon weer af.

   Zeven en eenentwintig, want dat is de reeks die er al staat: GRAM_BOX gebruikt 8 en 21 voor de
   hogere doosjes, en een tweede reeks in dezelfde app is een tweede waarheid. */
var LES_CHECK_DAGEN = [7, 21];
function lesKlaar(t){
  var st = brokLees(lesId(t));
  if((st.stapMax || 0) < LES_STAPPEN.length - 1) return false;
  // af, maar staat de controle open?
  if(st.check && st.check <= today()) return false;
  return true;
}
/* Wanneer komt deze rij terug? Aangeroepen zodra de laatste stap gehaald wordt. */
function lesCheckZet(rijId, gehaald){
  var st = brokLees(lesId(rijId));
  var ronde = st.checkN || 0;
  if(!gehaald){ st.check = today(); }                    // niet gehaald: blijft gewoon open
  else {
    st.check = addDays(today(), LES_CHECK_DAGEN[Math.min(ronde, LES_CHECK_DAGEN.length - 1)]);
    st.checkN = ronde + 1;
  }
  S.brok = S.brok || {};
  S.brok[lesId(rijId)] = st;
}
/* Staat de controle van deze rij open, dan begin je niet bij stap 0 maar bij de losse cel: de
   eerste stap zonder tabel in beeld. Herhalen is niet opnieuw leren. */
function lesCheckOpen(rijId){
  var st = brokLees(lesId(rijId));
  return !!(st.check && st.check <= today() && (st.stapMax || 0) >= LES_STAPPEN.length - 1);
}''')

    rep('''function lesStapAf(){
  if(!lesSpel) return;
  var st = brokLees(lesId(lesSpel.rij));
  st.stapMax = Math.max(st.stapMax || 0, lesSpel.stap);
  st.laatst = today();
  S.brok = S.brok || {};
  S.brok[lesId(lesSpel.rij)] = st;
  try { persist(); } catch(e){}
}''',
        '''function lesStapAf(){
  if(!lesSpel) return;
  var st = brokLees(lesId(lesSpel.rij));
  st.stapMax = Math.max(st.stapMax || 0, lesSpel.stap);
  st.laatst = today();
  /* v23.173: en wat je op deze stap presteerde. Hier stond alleen stapMax en laatst, dus de ladder
     wist wel hoe ver je was maar niet hoe goed het ging: goed en fout gingen nergens heen. Zonder
     dit is er niets om ooit een drempel of een terugkeer op te baseren. */
  if(typeof lesSpel.goed === "number" && (lesSpel.goed + lesSpel.fout) > 0){
    st.goed = (st.goed || 0) + lesSpel.goed;
    st.fout = (st.fout || 0) + lesSpel.fout;
    st.laatsteRonde = lesSpel.goed + "/" + (lesSpel.goed + lesSpel.fout);
  }
  S.brok = S.brok || {};
  S.brok[lesId(lesSpel.rij)] = st;
  /* de laatste stap gehaald: de rij is af, en dan hoort er een terugkeerdatum bij */
  if(lesSpel.stap >= LES_STAPPEN.length - 1){
    var n = lesOpgaven(lesSpel.stap);
    lesCheckZet(lesSpel.rij, lesSpel.goed >= n - 1);
  }
  try { persist(); } catch(e){}
}''')

    # de typstappen loggen hun fout, met een bronveld zodat de rest van de app hem kan uitsluiten
    rep('''  // zelfde soepelheid als de Conjugador: accenten mogen missen
  if(stripAcc(norm(g)) === stripAcc(norm(goedeVorm))) lesSpel.goed++; else lesSpel.fout++;''',
        '''  // zelfde soepelheid als de Conjugador: accenten mogen missen
  var lesGoed = stripAcc(norm(g)) === stripAcc(norm(goedeVorm));
  if(lesGoed) lesSpel.goed++; else lesSpel.fout++;
  /* v23.173: en de fout gaat naar het foutenlogboek, net als bij de Conjugador. Zonder dit wist
     vormFoutenPerTijd() alleen van Conjugador-fouten, terwijl juist deze stap productie toetst.

     bron:"les" erbij, en dat is geen sier: S.errors voedt ook de selectie elders in de app, en
     Stefan doet 168 antwoorden per dag op 30 procent fout. Een nieuwe foutenstroom zonder herkomst
     zou de dagles stilletjes in een vervoegingsdagles kunnen veranderen. Met een bron kan een
     volgende ronde hem wegen of uitsluiten in plaats van hem te moeten uitzoeken. */
  try {
    var fid = lesSpel.rij + "-" + q.p + "-" + (lesSpel.t || "");
    if(lesGoed) foutGoedeBeurt(fid, "conj");
    else {
      logError(fid, "conj", lesSpel.t || "", g);
      if(S.errors && S.errors["conj:" + fid]) S.errors["conj:" + fid].bron = "les";
    }
  } catch(e){}''')

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
