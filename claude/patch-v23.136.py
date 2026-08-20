#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.136: de zinnen krijgen een ladder die naar jou luistert.

Stefan, 20 aug: "voor het produceren van zinnen bouw dit stap voor stap op. nu zijn de zinnen soms
te lang en dat is te moeilijk voor me."

## Wat er stond, en het is niet wat ik dacht

Ik dacht eerst dat er geen lengteregeling was. Die is er wel, sinds v21.4, en dat maakt de fout
interessanter dan een omissie:

    function dicPlafond(){ return Math.min(30, 6 + getyptN() * 0.5); }

Het plafond hangt aan `getyptN()`: hoeveel zinnen je ooit hebt getypt. Na twintig zinnen staat het
op 16, na achtenveertig op 30, en de zwaarste zin in de bak is een 19. Vanaf ongeveer vijftig
getypte zinnen is het plafond dus uit. Stefan zit op honderden.

Het plafond meet hoe lang je bezig bent, niet hoe goed het gaat. Het gaat maar één kant op, het gaat
vanzelf, en het gaat nooit terug. Precies de klacht: soms is een zin te lang, en er is niets dat dat
merkt.

## Wat er nu staat

Zes treden, met een grens op de zwaarte die `dicZwaarte()` al berekende (woorden + accenten/2 +
2 voor een jaartal):

    trede 1  zwaarte ≤ 6     57 zinnen
    trede 2  zwaarte ≤ 8     58 erbij, 115 beschikbaar
    trede 3  zwaarte ≤ 10    59 erbij, 174 beschikbaar
    trede 4  zwaarte ≤ 13    40 erbij, 214 beschikbaar
    trede 5  zwaarte ≤ 16    15 erbij, 229 beschikbaar
    trede 6  geen plafond     2 erbij, 231 beschikbaar

Drie goed op rij en je gaat een trede omhoog. Twee fout op rij en je gaat er een omlaag. Dat is
dezelfde vorm als de Conjugador-ladder, en het is de enige regeling die kan zakken.

De grenzen zijn niet verzonnen: ze zijn zo gekozen dat elke trede minstens veertig nieuwe zinnen
oplevert, gemeten over de 231. Bij de A0-bak (82 zinnen) lopen trede 4 tot 6 leeg, en dat hoort:
die zinnen bestaan daar niet.

## Alleen de eerste poging telt

Je mag een zin opnieuw proberen. Zou die tweede poging ook meetellen, dan klim je door te blijven
proberen in plaats van door het te kunnen. `zinGeteld` zorgt dat er per verse zin precies één keer
geteld wordt.

## De migratie

Wie al twintig zinnen heeft getypt begint niet op trede 1. Maar ook niet op de trede die het oude
plafond hem gaf, want dat plafond stond bij Stefan al op 30 en dat is precies de klacht. Iedereen
met ervaring start op **trede 3**: de middelste band, 174 zinnen open, en binnen een paar dagen
staat de ladder waar hij hoort. Wie nieuw is start op 1.

## En de teller die niets zei gaat weg

De kop boven het scherm zei "Vertalen · niveau 2". Dat is `s.lvl`, en 183 van de 231 zinnen staan op
2: het is geen niveau maar een standaardwaarde. Er staat nu "trede 3 van 6", en dat getal beweegt
wel.

`dicPlafond()` is verwijderd. Hij had één aanroeper en die is vervangen; de naam kwam bovendien van
dictado, en dat scherm bestaat sinds v21.4 niet meer.

Bewaakt door test/suites/pw-vertladder.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.136"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = NIEUW not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ------------- 1. de ladder in plaats van het plafond

rep(
    '''function dicPlafond(){
  return Math.min(30, 6 + getyptN() * 0.5);
}''',
    '''/* ================= DE LADDER VOOR ZINNEN (v23.136) =================

   Stefan, 20 aug: "nu zijn de zinnen soms te lang en dat is te moeilijk voor me."

   Hier stond dit:

       function dicPlafond(){ return Math.min(30, 6 + getyptN() * 0.5); }

   Een plafond dat hangt aan hoeveel zinnen je ooit hebt getypt. Na twintig zinnen staat het op 16,
   na achtenveertig op 30, en de zwaarste zin in de bak is een 19. Vanaf een stuk of vijftig getypte
   zinnen is het plafond dus uit. Het mat hoe lang je bezig was, niet hoe het ging: het ging maar een
   kant op, het ging vanzelf, en het ging nooit terug.

   Zes treden nu, met grenzen op dezelfde zwaarte die dicZwaarte() al berekende. De grenzen zijn
   gekozen op de bak zoals hij is: elke trede levert minstens veertig nieuwe zinnen op, gemeten over
   de 231 (57 / 58 / 59 / 40 / 15 / 2). Bij de A0-bak lopen de bovenste drie leeg, en dat hoort:
   die zinnen bestaan daar niet.

   Drie goed op rij omhoog, twee fout op rij omlaag. Dezelfde vorm als de Conjugador-ladder, en de
   enige lengteregeling in de app die ook kan zakken. */
var VERT_TREDES = [6, 8, 10, 13, 16, 99];
var VERT_OMHOOG = 3;   // goede eerste pogingen op rij
var VERT_OMLAAG = 2;   // foute eerste pogingen op rij
function vertStand(){
  if(!S.vert || typeof S.vert !== "object"){
    /* Migratie. Wie al twintig zinnen heeft getypt begint niet op trede 1. Maar ook niet op de
       trede die het oude plafond hem gaf, want dat stond bij een ervaren gebruiker al op 30 en dat
       is precies de klacht. Trede 3 is de middelste band: 174 zinnen open, en binnen een paar dagen
       staat de ladder waar hij hoort. */
    S.vert = {trede: getyptN() >= 20 ? 3 : 1, reeks: 0};
    try { persist(); } catch(e){}
  }
  if(typeof S.vert.trede !== "number") S.vert.trede = 1;
  if(typeof S.vert.reeks !== "number") S.vert.reeks = 0;
  S.vert.trede = Math.max(1, Math.min(VERT_TREDES.length, S.vert.trede));
  return S.vert;
}
function vertTrede(){ return vertStand().trede; }
function vertPlafond(){ return VERT_TREDES[vertTrede() - 1]; }
/* Een positieve reeks is goed op rij, een negatieve is fout op rij. Een goed antwoord na een foute
   reeks begint dus op 1 en niet op nul: één keer goed na twee keer mis is een stap vooruit, geen
   schone lei. */
function vertBij(goed){
  var v = vertStand(), voor = v.trede;
  v.reeks = goed ? Math.max(0, v.reeks) + 1 : Math.min(0, v.reeks) - 1;
  if(goed && v.reeks >= VERT_OMHOOG && v.trede < VERT_TREDES.length){ v.trede++; v.reeks = 0; }
  if(!goed && v.reeks <= -VERT_OMLAAG && v.trede > 1){ v.trede--; v.reeks = 0; }
  try { persist(); } catch(e){}
  return {voor:voor, na:v.trede};
}
function vertTredeHtml(t){
  if(!t || t.na === t.voor) return "";
  if(t.na > t.voor){
    return "<div class='feedback ok' style='margin-top:6px'>"+
      ct("Trede "+t.na+" van "+VERT_TREDES.length+": de zinnen worden vanaf nu iets langer.",
         "Step "+t.na+" of "+VERT_TREDES.length+": the sentences get a bit longer from here.")+"</div>";
  }
  return "<div class='feedback bijna' style='margin-top:6px'>"+
    ct("Trede "+t.na+" van "+VERT_TREDES.length+": even wat kortere zinnen.",
       "Step "+t.na+" of "+VERT_TREDES.length+": shorter sentences for a bit.")+"</div>";
}''',
)

rep(
    '''  var plafond = dicPlafond();''',
    '''  var plafond = vertPlafond();   // v23.136: de ladder, niet de teller''',
)

# ------------- 2. tellen bij de eerste poging, en de uitslag laten zien

rep(
    '''function renderSentence(fresh){
  if(fresh || sIdx===null){ sIdx = pickSentence(); }''',
    '''/* v23.136: je mag een zin opnieuw proberen, en die tweede poging telt niet mee voor de ladder.
   Zonder deze vlag klim je door te blijven proberen in plaats van door het te kunnen. */
var zinGeteld = false;
function renderSentence(fresh){
  if(fresh || sIdx===null){ sIdx = pickSentence(); zinGeteld = false; }''',
)

rep(
    '''  var html = "", gehaald = false, retryable = false, fregel = null;   // v23.101: zie foutRegel()''',
    '''  var html = "", gehaald = false, retryable = false, fregel = null;   // v23.101: zie foutRegel()
  var vTrap = null;''',
)

rep(
    '''  html += "<div class='uitleg'><b>"+ct("Waarom:","Why:")+"</b> "+zinUitleg(s)+"</div>";''',
    '''  /* v23.136: de ladder beweegt op de eerste poging van deze zin, en zegt het als hij beweegt.
     Boven de uitleg en onder de knoppen: het is een mededeling over morgen, geen uitslag van nu. */
  if(!zinGeteld){ zinGeteld = true; vTrap = vertBij(gehaald); }
  html += vertTredeHtml(vTrap);
  html += "<div class='uitleg'><b>"+ct("Waarom:","Why:")+"</b> "+zinUitleg(s)+"</div>";''',
)

# ------------- 3. de kop zegt de trede in plaats van een getal dat niet beweegt

rep(
    '''(inFlowVertalen ? ct("Zin ","Sentence ")+((lesFlow.vertalenTotaal||5)-lesFlow.vertalenTeGaan+1)+"/"+(lesFlow.vertalenTotaal||5) : ct("Vertalen · niveau ","Translate · level ")+s.lvl+" · "+doneCount+"/"+allowIds.length+ct(" gehaald"," done"))''',
    '''/* v23.136: hier stond "niveau "+s.lvl. Dat is geen niveau maar een standaardwaarde: 183 van de
       231 zinnen staan op 2. De trede beweegt wel, en hij zegt iets over de zin die je nu krijgt. */
      (inFlowVertalen ? ct("Zin ","Sentence ")+((lesFlow.vertalenTotaal||5)-lesFlow.vertalenTeGaan+1)+"/"+(lesFlow.vertalenTotaal||5)+ct(" · trede "," · step ")+vertTrede()+"/"+VERT_TREDES.length : ct("Vertalen · trede ","Translate · step ")+vertTrede()+"/"+VERT_TREDES.length+" · "+doneCount+"/"+allowIds.length+ct(" gehaald"," done"))''',
)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
