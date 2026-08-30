#!/usr/bin/env python3
# v23.212 - een muntje is een half bewijs
#
# Stefan, 30 aug: "grammatica maken en zinnen maken gaat nog niet zo goed."
#
# WAT IK GEMETEN HEB
#
# De 31 concepten van de leermachine maken samen 153 zinpatronen. Daarvan geven er 101 precies twee
# keuzes. Dat is geen slordigheid: het is de definitie van het onderwerp. Het Nederlands heeft een
# woord waar het Spaans er twee heeft, en dus is er ook geen derde antwoord.
#
#   por / para       5x      es / esta         5x      el / la          5x
#   a / (niets)      5x      No / (niets)      8x      pedir / preguntar 8x
#   tu / usted       8x      que / cual        5x      gusta / gustan    4x
#   he hablado / hable  4x   hable / hablaba   4x      Se / Conozco      4x
#   ... 101 in totaal
#
# WAAROM IK ER GEEN DERDE OPTIE BIJ ZET
#
# Dat was mijn eerste plan, en het klopt niet. Bij "Estoy ___ cansado" is er naast muy en mucho geen
# derde woord dat een leerling ooit zou overwegen; bij por/para al helemaal niet. Een afleider die
# niemand kiest verlaagt de gokkans niet, hij verlengt alleen de knoppenrij. Rodriguez telde in 2005
# tachtig jaar aan meerkeuze-onderzoek bij elkaar (80 studies) en kwam op drie opties als optimum,
# precies omdat de vierde in de praktijk nooit plausibel is [bron: Rodriguez, Educational Measurement:
# Issues and Practice, 2005]. Voor deze 101 geldt dat al bij de derde.
#
# Van de 101 heb ik er acht gevonden waar een echte derde bestaat (gustar kan "gusto" hebben, de
# demonstrativos hebben naast geslacht ook afstand). Acht van 101 is geen ronde.
#
# WAT ER DAN WEL MIS IS
#
# Niet de vraag, maar wat de app met het antwoord doet. gramBij() zet het doosje een stap omhoog bij
# elk goed antwoord van de dag, of dat antwoord nu uit twee knoppen kwam of uit je toetsenbord. Bij
# twee knoppen is de helft van je goede antwoorden geen kennis.
#
# Gesimuleerd, 90 dagen, 4000 lopen per cel, met de echte GRAM_BOX = [0,1,3,8,21,55]:
#
#   kennis   regel   einddoos  beurten  dagen in doos 3+   eindigt in doos 3+
#   0.00     nu      2.80      16.5     36.9               65%
#   0.00     nieuw   1.22      48.1      9.0               17%
#   0.50     nu      3.64       7.7     59.0               94%
#   0.50     nieuw   2.91      21.9     38.0               68%
#   1.00     nu      4.00       4.0     73.0              100%
#   1.00     nieuw   4.00       8.0     70.0              100%
#
# Lees de eerste rij nog een keer. Een leerling die dit onderwerp NIET kent belandt onder de huidige
# regel in 65% van de gevallen in doosje 3 of hoger, en dat doosje betekent 8 tot 55 dagen rust. Dat
# is de lek: niet dat hij het fout doet, maar dat de app dan denkt dat het klaar is.
#
# En kijk naar de onderste rij voor de prijs: wie het onderwerp wel kent betaalt vier extra beurten
# in drie maanden. Dat is de hele rekening.
#
# DE REGEL
#
# Een goed antwoord uit twee keuzes is een half bewijs. Twee halve bewijzen, op twee verschillende
# dagen, zijn samen een doosje. Alles met drie of meer keuzes, en alles wat je typt, telt vol zoals
# nu. Gokken loopt daarmee van 50% naar 25% per doosje, precies de kans van een vierkeuzevraag.
#
# WAT DE DAGLES ERVAN MERKT
#
# Niets, in aantal. lesFlowGramLijst() haalt precies een opfrisvraag plus een microles per les, en
# dat blijft zo. Wat verandert is WELK onderwerp vooraan staat: minder onderwerpen die op een
# muntworp zijn weggeschoven, meer onderwerpen die er echt nog liggen.
#
# TWEE PLEKKEN DIE ANDERS SILENT KAPOT ZOUDEN GAAN
#
# 1. gramWachtrij() laat een concept met doosje 0 en een openstaande fout de datum overslaan. Onder
#    de oude regel sloot een goed antwoord die rekening door het doosje op 1 te zetten. Onder de
#    nieuwe blijft het doosje 0 staan, dus zonder aanpassing zou hetzelfde onderwerp de rest van de
#    dag vooraan blijven staan zonder dat er iets kan gebeuren (de dagrem laat het tweede antwoord
#    van vandaag toch niet tellen). Een half bewijs sluit de rekening van vandaag net zo goed.
# 2. lesFlowGramLijst() serveert de hele microles in plaats van een opfrisvraag bij doosje 0 met
#    twee fouten. Ook daar geldt: heb je vandaag al een half bewijs geleverd, dan is de microles
#    over-bedienen.
#
# WAT BEWUST NIET MEEDOET
#
# De clasificador roept gramBij() pas aan bij een reeks van vijf goed (CL_DANS_BIJ), en vijf keer
# een muntworp is 3%. Dat is al meer dan twee bits. Het toetsje roept hem aan bij 80% over een hele
# reeks vragen. De Corrector en de zinnencheck geven een getypt antwoord door. Alle vier houden dus
# vol krediet, en dat is geen uitzondering maar dezelfde regel: waar je niet kunt gokken telt het vol.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.212"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function gramHalfBewijs(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:120])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de regel zelf
# =============================================================================================
if DOE_APP:
    rep("""function gramBij(cid, goed){
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
}""",
"""/* ================= v23.212: EEN MUNTJE IS EEN HALF BEWIJS =================

   Van de 153 zinpatronen van de leermachine geven er 101 precies twee keuzes, en dat is geen
   slordigheid maar de definitie van het onderwerp: het Nederlands heeft één woord waar het Spaans
   er twee heeft (por/para, es/está, el/la, a of niets). Er is dus ook geen derde antwoord om erbij
   te zetten, en een afleider die niemand kiest verlaagt de gokkans niet.

   Wat wel kan: niet de vraag veranderen maar wat de app met het antwoord doet. Hier stond
   één regel voor alles, en die gaf een muntworp hetzelfde gewicht als een getypt antwoord.

   Gesimuleerd over 90 dagen met de echte GRAM_BOX, voor een leerling die het onderwerp NIET kent:
   onder de oude regel eindigt hij in 65% van de lopen in doosje 3 of hoger, oftewel 8 tot 55 dagen
   rust op iets wat hij niet kan. Onder deze regel is dat 17%. De prijs voor wie het wél kent:
   vier extra beurten in drie maanden.

   Twee halve bewijzen op twee verschillende dagen zijn samen een doosje. Gokken loopt daarmee van
   50% naar 25% per doosje: precies de kans van een vierkeuzevraag. */
function gramHalfBewijs(keuzes){ return keuzes === 2; }
/* keuzes = uit hoeveel knoppen de leerling koos. Weggelaten of 0 betekent getypt of samengesteld
   over een hele reeks, en dat telt vol: waar je niet kunt gokken hoeft er niets af. */
function gramBij(cid, goed, keuzes){
  if(!cid) return;
  S.gram = S.gram || {};
  var st = S.gram[cid] || {box:0, due:"", goed:0, fout:0, laatst:""};
  // de tellers lopen altijd door; die zijn de geschiedenis en niet het oordeel
  if(goed) st.goed++;
  else { st.fout++; st.laatst = today(); }

  if(st.bd !== today()){
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
  S.gram[cid] = st;
}""")

# =============================================================================================
# 2. de wizard weet uit hoeveel knoppen je koos, en geeft dat door
# =============================================================================================
if DOE_APP:
    rep("""  if(stap && stap.brok){ brokBij(stap.brok, goed); return; }
  if(!o || !o.concept) return;
  gramBij(o.concept, goed);
  gramLog(o.concept, gwKanaal(o), goed);""",
"""  if(stap && stap.brok){ brokBij(stap.brok, goed); return; }
  if(!o || !o.concept) return;
  /* v23.212: het aantal knoppen gaat mee. Dit is de enige plek in de app waar een doosje omhoog
     kan op een antwoord dat je ook had kunnen raden, en dus de enige plek die het hoeft door te
     geven. De vraag draagt het feit al (q.o); geen enkele andere plek schrijft het opnieuw. */
  gramBij(o.concept, goed, (q && q.o) ? q.o.length : 0);
  gramLog(o.concept, gwKanaal(o), goed);""")

# =============================================================================================
# 3. een half bewijs sluit de rekening van vandaag, net als een doosje dat deed
# =============================================================================================
if DOE_APP:
    rep("""    /* Een openstaande fout (doosje nul) wacht niet op zijn datum. Dat stond al zo in de oude
       foutenpot en de reden klopt nog steeds: anders komt de fout die je net maakte pas morgen aan
       bod, en dat is precies de dag dat je hem al vergeten bent. Het verschil met vroeger is dat
       één goed antwoord het doosje op één zet en de rekening daarmee sluit; vroeger bleef st.fout
       staan en bleef het onderwerp levenslang vooraan. */
    var open = (st.box || 0) === 0 && (st.fout || 0) > 0;""",
"""    /* Een openstaande fout (doosje nul) wacht niet op zijn datum. Dat stond al zo in de oude
       foutenpot en de reden klopt nog steeds: anders komt de fout die je net maakte pas morgen aan
       bod, en dat is precies de dag dat je hem al vergeten bent. Het verschil met vroeger is dat
       één goed antwoord de rekening sluit; vroeger bleef st.fout staan en bleef het onderwerp
       levenslang vooraan.

       v23.212: die rekening sloot doordat het doosje op één ging. Bij een tweekeuzevraag blijft
       het doosje nu op nul staan en is het halve bewijs de sluiting. Zonder dit stukje zou een
       goed beantwoord onderwerp de rest van de dag vooraan blijven staan terwijl de dagrem in
       gramBij() het tweede antwoord van vandaag toch niet laat tellen: een slot dat op zichzelf
       dichtklapt. */
    var open = (st.box || 0) === 0 && (st.fout || 0) > 0 && !st.half;""")

# =============================================================================================
# 4. en de hele microles is over-bedienen als je vandaag al geleverd hebt
# =============================================================================================
if DOE_APP:
    rep("""    /* Twee keer mis op hetzelfde is geen geheugenkwestie: dan geen opfrisvraag maar de hele
       microles, en die komt uit lesFlowGramId() hieronder. */
    if(!((top.st.box || 0) === 0 && (top.st.fout || 0) >= 2)){""",
"""    /* Twee keer mis op hetzelfde is geen geheugenkwestie: dan geen opfrisvraag maar de hele
       microles, en die komt uit lesFlowGramId() hieronder.
       v23.212: tenzij er vandaag al een half bewijs ligt. Het doosje blijft dan op nul staan tot
       het tweede bewijs er is, en zonder deze uitzondering zou de hele microles twee dagen achter
       elkaar komen op een onderwerp dat je gisteren goed had. */
    if(!((top.st.box || 0) === 0 && (top.st.fout || 0) >= 2 && !top.st.half)){""")

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    assert src.count("function gramHalfBewijs(") == 1
    assert src.count("gramBij(o.concept, goed, (q && q.o) ? q.o.length : 0)") == 1
    assert src.count("(st.fout || 0) > 0 && !st.half") == 1
    assert src.count("(top.st.fout || 0) >= 2 && !top.st.half") == 1
    APP.write_text(src, encoding="utf-8")
    print("index.html: een goed antwoord uit twee knoppen is nog geen doosje")
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
