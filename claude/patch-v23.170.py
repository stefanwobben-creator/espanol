#!/usr/bin/env python3
# v23.170 - het eerste antwoord van de dag beslist over je doosje
#
# Stefan, 22 aug: "kijk ook even hoe vaak ik vandaag el of la heb gedaan. want dat vind ik wel heel
# veel waarbij ik ga twijfelen of het kapot is of dat de methode te streng is."
#
# Het was kapot, en niet op de manier die hij dacht.
#
# WAT ER GEMETEN IS
#
#     el of la (genero):  box 0, goed 52, fout 17, bd = vandaag, due = morgen
#     op doos 0:          genero, serestar, reflexivo   (3 van ruim 20 onderwerpen)
#
# Correctie op mijn eigen eerste lezing, want die zat fout en dat hoort hier te staan: goed en fout
# tellen over de hele tijd door en niet per dag. Ik heb 52 en 17 gelezen als "vandaag", en dat is
# nergens uit af te leiden.
#
# HET DEFECT, EN DAT IS WEL HARD
#
# In gramBij() gold de dagrem alleen omhoog:
#
#     goed  ->  doos omhoog, maar hoogstens één keer per dag  (if st.bd !== today())
#     fout  ->  doos naar 0, altijd, zonder enige rem
#
# Zet die twee achter elkaar op één dag en je einddoos hangt af van de VOLGORDE van je antwoorden.
# Eerst goed dan fout eindigt op 0 en kan die dag niet meer omhoog, want de rem staat al aan. Eerst
# fout dan goed eindigt op doos 1. Zelfde dag, zelfde antwoorden, andere uitkomst.
#
# Praktisch betekende dat: één fout per dag is genoeg om voor altijd op doos 0 te blijven, hoeveel
# je er daarna ook goed doet. En doos 0 met twee of meer fouten is precies de voorwaarde waarop
# lesFlowGramId() de volledige microles geeft. Vandaar dat el of la elke dag won.
#
# WAT ER NIET GEBOUWD IS, EN WAAROM DAT HET BELANGRIJKSTE IS
#
# Mijn eerste voorstel (leerkaart in het project) was: één dooswijziging per dag, richting uit de
# dagscore, en één stap zakken in plaats van naar nul. Aangevallen en gesneuveld op vijf punten:
#
#   - "alles goed op die dag" is bij tientallen pogingen op 75 procent vrijwel onhaalbaar, dus zou
#     el of la élke dag zakken. Ik ruilde "vast op 0" in voor "blijft zakken tot 0".
#   - het traint volume-minimalisatie: onder die regel is de beste strategie je zwakke punten
#     vermijden en stoppen na één goed antwoord.
#   - één stap zakken is expliciet afgekeurd door SuperMemo (het heet daar een onjuiste mutatie van
#     Leitner) en Anki reset standaard volledig. Ik stelde voor wat die twee afraden.
#   - de vervaldatum loskoppelen van de doos zou lesFlowGramId() stil slopen: die vuurt op doos 0.
#   - en mijn onderbouwing citeerde twee bronnen tegen hun strekking plus een rekenfout: 75 procent
#     is niet "bijna af" maar ónder de optimale retentie van ruwweg 85 tot 90 procent.
#
# WAT ER WEL IN GAAT
#
# HET EERSTE ANTWOORD VAN DE DAG BESLIST. Dat is de echte toets; alles daarna diezelfde dag is
# herhaling binnen de sessie en besmet door wat je net gezien hebt.
#
#   1. het eerste antwoord van vandaag bepaalt de doos, en daarna beweegt de doos die dag niet meer,
#      in geen van beide richtingen
#   2. goed is één doos omhoog, fout is volledig terug naar 0. De reset blijft, want Stefan vroeg er
#      zelf om en de literatuur staat aan die kant
#   3. gaat het later op de dag alsnog mis, dan blijft de doos staan maar gaat de vervaldatum naar
#      morgen. Dan wordt het morgen opnieuw beoordeeld in plaats van dat het dagen wegzakt
#
# Voor Stefan: zolang zijn eerste antwoord van de dag goed is klimt el of la, en een misser later op
# de dag gooit dat niet meer weg. De ratel is weg, de strengheid blijft.
#
# EN DE DUBBELE INVOER
#
# lesFlowGramLijst() ontdubbelt op de volledige id, maar de opfrisser heet "opfris-genero" en de
# microles "concept-genero". Verschillende strings, dus hetzelfde onderwerp kon twee keer in één les
# staan. Met twee lessen op een dag zijn dat er vier.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.170"

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
    # 1. het eerste antwoord van de dag beslist
    # -----------------------------------------------------------------------
    rep('''function gramBij(cid, goed){
  if(!cid) return;
  S.gram = S.gram || {};
  var st = S.gram[cid] || {box:0, due:"", goed:0, fout:0, laatst:""};
  if(goed){
    st.goed++;
    /* v23.92: dezelfde dagrem als bij de woorden. Vijf goede antwoorden in één sessie zetten dit
       onderwerp van doos 0 naar doos 5, en dan zag je het 55 dagen niet meer, na één goede bui.
       Het aantal goede antwoorden loopt gewoon door; alleen de doos wacht op morgen. */
    if(st.bd !== today()){
      st.bd = today();
      st.box = Math.min((st.box || 0) + 1, GRAM_BOX.length - 1);
      st.due = addDays(today(), GRAM_BOX[st.box]);
    }
  } else {
    // Stefan: "alle fouten die maak moeten weer terug". Niet over een week, morgen.
    st.fout++;
    st.box = 0;
    st.due = addDays(today(), 1);
    st.laatst = today();
  }
  S.gram[cid] = st;
}''',
        '''/* v23.170: HET EERSTE ANTWOORD VAN DE DAG BESLIST.

   Hier stond een dagrem die alleen omhoog werkte:

       goed  ->  doos omhoog, hoogstens één keer per dag (if st.bd !== today())
       fout  ->  doos naar 0, altijd, zonder rem

   Zet die twee achter elkaar op één dag en je einddoos hangt af van de VOLGORDE van je antwoorden.
   Eerst goed dan fout eindigt op 0 en kan die dag niet meer omhoog, want de rem staat al aan. Eerst
   fout dan goed eindigt op doos 1. Zelfde dag, zelfde antwoorden, andere uitkomst. Dat heeft
   niemand ontworpen.

   Wat het in de praktijk deed: één fout per dag was genoeg om voor altijd op doos 0 te blijven,
   hoeveel je er daarna ook goed deed. En doos 0 met twee of meer fouten is precies de voorwaarde
   waarop lesFlowGramId() de volledige microles geeft. Stefan, 22 aug: "ik heb el of la vandaag heel
   veel gedaan." Zijn genero stond op doos 0 met 52 goed tegen 17 fout.

   De nieuwe regel is dat het eerste antwoord van de dag beslist, en dat is niet willekeurig: de
   eerste keer dat je een onderwerp die dag ophaalt is de echte toets. Alles daarna is herhaling
   binnen dezelfde sessie, besmet door wat je net gezien hebt, en dus geen bewijs van geheugen.

   De reset naar 0 blijft staan en is met opzet niet verzacht tot "één stap omlaag". Stefan vroeg
   er zelf om ("alle fouten die ik maak moeten weer terug"), SuperMemo noemt de één-stap-variant een
   onjuiste mutatie van Leitner, en Anki reset standaard volledig. Zachter maken vertraagt bovendien
   het herkennen van een onderwerp dat echt vastzit, en dat is precies wat we hier zoeken. */
function gramBij(cid, goed){
  if(!cid) return;
  S.gram = S.gram || {};
  var st = S.gram[cid] || {box:0, due:"", goed:0, fout:0, laatst:""};
  // de tellers lopen altijd door; die zijn de geschiedenis en niet het oordeel
  if(goed) st.goed++;
  else { st.fout++; st.laatst = today(); }

  if(st.bd !== today()){
    st.bd = today();
    if(goed){
      st.box = Math.min((st.box || 0) + 1, GRAM_BOX.length - 1);
      st.due = addDays(today(), GRAM_BOX[st.box]);
    } else {
      st.box = 0;
      st.due = addDays(today(), 1);
    }
  } else if(!goed){
    /* Later op de dag alsnog mis. De doos blijft staan (het oordeel van vandaag is al geveld), maar
       je ziet het morgen terug in plaats van pas over drie of acht dagen. Zonder deze regel zou een
       onderwerp dat je 's ochtends goed had en 's middags vijf keer fout gewoon wegzakken. */
    st.due = addDays(today(), 1);
  }
  S.gram[cid] = st;
}''')

    # -----------------------------------------------------------------------
    # 2. hetzelfde onderwerp niet twee keer in één les
    # -----------------------------------------------------------------------
    rep('''  var gid = null;
  try { gid = lesFlowGramId(); } catch(e){ gid = null; }
  if(gid && uit.indexOf(gid) === -1) uit.push(gid);
  return uit;''',
        '''  var gid = null;
  try { gid = lesFlowGramId(); } catch(e){ gid = null; }
  /* v23.170: ontdubbelen op de kále concept-id. Hier stond uit.indexOf(gid), en dat vergelijkt
     "opfris-genero" met "concept-genero": verschillende strings, dus hetzelfde onderwerp kon twee
     keer in dezelfde les staan, één keer als opfrisvraag en één keer als volledige microles. Met
     twee lessen op een dag zijn dat er vier, en dat is een deel van Stefans "heel veel el of la". */
  var kaal = function(x){ return String(x || "").replace(/^(opfris|concept)-/, ""); };
  var alHier = uit.map(kaal);
  if(gid && alHier.indexOf(kaal(gid)) === -1) uit.push(gid);
  return uit;''')

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
