#!/usr/bin/env python3
# v23.203 - de voorspelling meet je dagen, niet je maandagen
# (gebouwd als v23.198; hernummerd naar v23.203 omdat de nachtrun v23.198 onder ons uit main pakte)
#
# Stefan, 26 aug: "waarom werkt de voorspelling nog niet? je kent inmiddels mijn foutpercentage en
# weet dat ik iedere dag de dagles doe, je zou moeten kunnen extrapoleren toch?" En daarna, scherper:
# "als je dagelijks meet en je ziet iemand komt dagelijks heb je sneller goede data om een
# voorspelling te doen dan iemand die af en toe komt toch?"
#
# WAT ER MIS WAS, EN DAT HET NOOIT GEKOZEN IS
#
# De voorspelling rekent op weekmetingen en zwijgt onder de drie. Stefan komt 36 dagen op rij en
# heeft er twee. Iemand die twee keer per maand komt heeft er na dezelfde drie weken evenveel, en
# krijgt dus dezelfde voorspelling. Het ritme van de meting volgt de kalender in plaats van de
# gebruiker, en dat staat precies verkeerd om.
#
# Nagekeken waar dat weekritme vandaan komt. Uit de kop van v19.87, letterlijk:
#
#   voortgangBand(), die al sinds v19.83 in het bestand lag zonder ooit getoond te worden: een
#   ondergrens en een bovengrens in weken, gerekend over je WEKELIJKSE metingen
#
# De functie was er al, hij rekende al op weken, en die werd getoond. In v23.37 heb ik de maat
# gerepareerd (dek werd dekw) en het ritme laten staan. De drie-punten-regel is zorgvuldig
# beargumenteerd; het weekritme is nooit onderwerp van een beslissing geweest.
#
# En de dagsnapshot die er al is bewaart de inspanning en niet de voortgang:
#
#   S.dagStats[dag] = {pogingen, fouten, sec, asec}      36 dagen, geen dekkingsteller
#   S.meting[week]  = {dek, dekw, stevig, ...}            2 bruikbare punten
#
# WAT ERVOOR IN DE PLAATS KOMT
#
# S.dagMeting[dag] = {dek, dekw}, één regel per dag, geschreven op het moment dat de weekmeting ook
# al werd geschreven. En het tempo komt uit een kleinste-kwadratenlijn door die punten in plaats van
# uit een gemiddelde van twee verschillen.
#
# Dat is niet alleen sneller maar ook eerlijker. Het ruisargument dat "drie punten" rechtvaardigt,
# rechtvaardigt "per week" niet: hobbelige data (0, 0, 3, 0, 1) hoort met een regressie over veel
# punten behandeld te worden, niet met optellen tot je er weinig overhoudt. Een lijn door dertig
# dagpunten kan prima tegen hobbels en levert een echte standaardfout; een gemiddelde van twee
# verschillen levert geen enkele.
#
# WAAROM IK DE GESCHIEDENIS NIET TERUGREKEN
#
# Het kon: elk woord draagt due en box, dus due - INTERVALS[box] is de dag van zijn laatste
# promotie, en daarmee is de hele curve achterwaarts te reconstrueren. Ik doe het niet. Die schatting
# legt het moment waarop een woord doos 3 haalde te laat, want een woord dat lang op doos 3 bleef
# staan voordat het doorschoof krijgt de datum van dat doorschuiven. De reconstructie helt daardoor
# systematisch naar "recent", en dat betekent een tempo dat te hoog is en een voorspelling die te veel
# belooft. Een voorspelling die te veel belooft is erger dan een die nog even zwijgt.
#
# Wat wel mag, want het is exact en geen schatting: de weekmetingen die er liggen dragen dekw én de
# dag waarop ze geschreven zijn. Die gaan als startpunten de dagreeks in.
#
# WAT DE PROEF METEN GAAT (test/suites/pw-dagmeting.js)
#
#   1. DE HELLING KLOPT. Zet een reeks van precies +3 per dag neer en het gemeten weektempo is 21.
#      Dit is de proef die er het meest toe doet: een voorspeller die de verkeerde helling meet is
#      erger dan een die zwijgt.
#   2. EN HIJ BELOOFT NIETS BIJ EEN VLAKKE REEKS. Het controlegeval bij 1.
#   3. DE BAND WORDT SMALLER BIJ MEER PUNTEN. Dat is de hele reden om dagelijks te meten, en zonder
#      deze proef is het een aanname.
#   4. EÉN PUNT PER DAG, en een tweede opening dezelfde dag schrijft er geen tweede bij.
#   5. DE WEEKMETINGEN GAAN MEE ALS STARTPUNT, met hun eigen datum.
#   6. EN HIJ ZWIJGT ALS ER TE WEINIG IS, of als alle punten uit drie dagen komen.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.203"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function dagMetingSchrijf(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:100])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de dagmeting
# =============================================================================================
DAG = r'''/* ================= DE DAGMETING (v23.198) =================
   Stefan, 26 aug: "als je dagelijks meet en je ziet iemand komt dagelijks heb je sneller goede
   data om een voorspelling te doen dan iemand die af en toe komt toch?"

   Ja, en dat stond precies verkeerd om. De weekmeting hierboven legt één punt per kalenderweek
   vast, dus wie 36 dagen op rij komt heeft er evenveel als wie twee keer per maand komt. Hier komt
   één regel per DAG bij, met dezelfde maat (dekw), zodat het aantal punten volgt hoe vaak jij er
   bent in plaats van hoeveel maandagen er voorbij zijn.

   Twee velden en niet meer: dek (bewezen vast) en dekw (wat je actief bijhoudt). De inspanning per
   dag staat al in S.dagStats; wat daar ontbrak was de voortgang, en dat is precies het getal dat de
   voorspelling nodig heeft.

   De pot wordt afgekapt op DAGMETING_MAX dagen. Een reeks die eeuwig doorgroeit in localStorage is
   een lek, en meer dan een jaar terugkijken voegt aan een tempo van vandaag niets toe. */
var DAGMETING_MAX = 400;
function dagMetingSchrijf(){
  try{
    S.dagMeting = S.dagMeting || {};
    /* de weekmetingen die er al liggen gaan mee als startpunt. Dat mag, want het is dezelfde maat
       (dekw) op een datum die de weekregel zelf draagt: exact, geen schatting. Terugrekenen uit
       due en box zou wél een schatting zijn, en die helt naar "recent" en belooft dus te veel. */
    var wk;
    for(wk in (S.meting || {})){
      var wm = S.meting[wk];
      if(!wm || !wm.d || !wm.dekw) continue;
      if(!S.dagMeting[wm.d]) S.dagMeting[wm.d] = {dek:wm.dek, dekw:wm.dekw, uitWeek:1};
    }
    var t = today();
    if(S.dagMeting[t] && !S.dagMeting[t].uitWeek) return;   // vandaag al echt gemeten
    var c = voortgangTellers();
    S.dagMeting[t] = {dek:c.dek, dekw:c.dekw};
    var dagen = Object.keys(S.dagMeting).sort();
    while(dagen.length > DAGMETING_MAX) delete S.dagMeting[dagen.shift()];
    persist();
  }catch(e){}                                // een meter mag de app nooit omver duwen
}
/* Het tempo uit de dagreeks: een kleinste-kwadratenlijn, en de marge is twee standaardfouten op de
   helling. Niet het gemiddelde van de verschillen, want dat is precies wat een reeks van twee
   punten deed en dat gaf geen enkele onzekerheidsmaat.

   Twee drempels, en ze meten twee verschillende dingen. TEMPO_MIN_PUNTEN gaat over hoeveel bewijs
   er is; TEMPO_MIN_SPAN gaat over waarover. Vijf metingen uit drie dagen zeggen iets over drie
   dagen en niets over een tempo, dus daar hoort de voorspeller nog te zwijgen. */
var TEMPO_MIN_PUNTEN = 5;
var TEMPO_MIN_SPAN = 7;
function dagMetingPunten(niveau){
  var d = S.dagMeting || {}, ds = Object.keys(d).sort(), uit = [], i, m, x0 = null;
  for(i = 0; i < ds.length; i++){
    m = d[ds[i]];
    if(!m || !m.dekw || typeof m.dekw[niveau] !== "number") continue;
    if(x0 === null) x0 = ds[i];
    uit.push({dag:ds[i], x:dagMetingDelta(x0, ds[i]), y:m.dekw[niveau]});
  }
  return uit;
}
/* Niet dagenSinds() genoemd, en dat is geen smaak. Die naam is al bezet (regel ~21742, één
   argument, telt vanaf een datum tot vandaag). Twee function-declaraties met dezelfde naam is geen
   fout in JavaScript: de laatste wint stilletjes, en de eerste aanroeper krijgt een functie die
   iets anders betekent. Precies dezelfde botsing als de Door-knop van v23.197, nu in de namen in
   plaats van in de id's. Zie tools/dubbelenaam.js, die dit voortaan narekent. */
function dagMetingDelta(a, b){
  var p = String(a).split("-"), q = String(b).split("-");
  if(p.length !== 3 || q.length !== 3) return 0;
  return Math.round((Date.UTC(+q[0], +q[1]-1, +q[2]) - Date.UTC(+p[0], +p[1]-1, +p[2])) / 86400000);
}
function tempoDagMeting(niveau){
  var p = dagMetingPunten(niveau);
  if(p.length < TEMPO_MIN_PUNTEN) return null;
  var span = p[p.length-1].x - p[0].x;
  if(span < TEMPO_MIN_SPAN) return null;
  var n = p.length, sx = 0, sy = 0, i;
  for(i = 0; i < n; i++){ sx += p[i].x; sy += p[i].y; }
  var mx = sx / n, my = sy / n, sxx = 0, sxy = 0;
  for(i = 0; i < n; i++){ sxx += (p[i].x - mx) * (p[i].x - mx); sxy += (p[i].x - mx) * (p[i].y - my); }
  if(sxx <= 0) return null;
  var hel = sxy / sxx;                        // per dag
  var sse = 0, e;
  for(i = 0; i < n; i++){ e = p[i].y - (my + hel * (p[i].x - mx)); sse += e * e; }
  /* de standaardfout van de helling. Bij n = 2 is er geen vrijheidsgraad over en is dit oneindig;
     dat kan hier niet voorkomen omdat TEMPO_MIN_PUNTEN op vijf staat, maar de deling wordt
     afgeschermd omdat een NaN op dit scherm er precies zo uitziet als een getal. */
  var se = n > 2 ? Math.sqrt((sse / (n - 2)) / sxx) : 0;
  return {gem: hel * 7, marge: 2 * se * 7, weken: span / 7,
          nu: p[p.length-1].y, punten: n, dagen: span, bron:"dag"};
}

'''

if DOE_APP:
    rep("function metingenNieuweMaat(niveau){", DAG + "function metingenNieuweMaat(niveau){")

# =============================================================================================
# 2. tempoMeting kiest de dagreeks als die er is
# =============================================================================================
if DOE_APP:
    rep("""function tempoMeting(niveau){
  var reeks = metingenNieuweMaat(niveau);""",
        """function tempoMeting(niveau){
  /* v23.198: de dagreeks gaat voor. Eén functie blijft de bron voor voortgangBand() en
     voorspelWaar(), want twee plekken die allebei een tempo uitrekenen lopen uit elkaar en dan
     spreekt hetzelfde scherm zichzelf tegen. De weekreeks blijft eronder liggen als terugval voor
     wie nog geen dagpunten heeft. */
  var dag = null;
  try { dag = tempoDagMeting(niveau); } catch(e){ dag = null; }
  if(dag) return dag;
  var reeks = metingenNieuweMaat(niveau);""")

    # en de meting wordt geschreven waar de weekmeting ook geschreven wordt
    rep("""  snapshotSchrijf(); // v19.83: nulmeting van de week, onzichtbaar""",
        """  snapshotSchrijf(); // v19.83: nulmeting van de week, onzichtbaar
  dagMetingSchrijf(); // v23.198: en één punt per dag, want daar hangt de voorspelling aan""")
    rep("""  try { snapshotSchrijf(); } catch(e){}""",
        """  try { snapshotSchrijf(); } catch(e){}
  try { dagMetingSchrijf(); } catch(e){}""")
    rep("""      snapshotSchrijf();
""",
        """      snapshotSchrijf();
      try { dagMetingSchrijf(); } catch(e){}
""")

# =============================================================================================
# 3. en de wachtzin zegt waar je nu echt op wacht
# =============================================================================================
if DOE_APP:
    rep("""function tempoStand(niveau){
  var n = 0;
  try { n = metingenNieuweMaat(niveau).length; } catch(e){ n = 0; }
  return {heeft:n, nodig:TEMPO_NODIG, genoeg:n >= TEMPO_NODIG};
}""",
        """function tempoStand(niveau){
  /* v23.198: sinds de dagmeting wacht je niet meer op maandagen maar op dagen dat je er bent.
     Deze functie voedt de wachtzin, dus hij moet dezelfde drempels gebruiken als tempoDagMeting();
     twee plekken met elk hun eigen drempel is een zin die iets anders belooft dan de meter doet. */
  var p = [];
  try { p = dagMetingPunten(niveau); } catch(e){ p = []; }
  var span = p.length ? p[p.length-1].x - p[0].x : 0;
  var genoeg = p.length >= TEMPO_MIN_PUNTEN && span >= TEMPO_MIN_SPAN;
  return {heeft:p.length, nodig:TEMPO_MIN_PUNTEN, span:span, spanNodig:TEMPO_MIN_SPAN,
          genoeg:genoeg, dag:true};
}""")

    rep("""function tempoWachtZin(niveau){
  var st = tempoStand(niveau);
  if(st.genoeg) return "";
  var m = komendeMaandag();
  return ct("Je hebt er " + st.heeft + " van de " + st.nodig + ". ",
            "You have " + st.heeft + " of " + st.nodig + ". ") +
    (m ? ct("De volgende kan er vanaf maandag " + datumUit(m) + " bij, de eerste keer dat je de app die week opent.",
            "The next one can arrive from Monday " + datumUit(m) + ", the first time you open the app that week.")
       : ct("De volgende komt de eerste keer dat je de app in een nieuwe week opent.",
            "The next one arrives the first time you open the app in a new week.")) +
    ct(" Een weekmeting telt pas mee sinds 10 augustus, toen de maat van de balk hierboven werd vastgelegd.",
       " A weekly measurement only counts since 10 August, when the unit of the bar above was fixed.");
}""",
        """function tempoWachtZin(niveau){
  var st = tempoStand(niveau);
  if(st.genoeg) return "";
  /* v23.198: dit zei "de volgende kan er vanaf maandag bij". Dat klopte en het was het antwoord op
     de verkeerde vraag: je wachtte op de kalender in plaats van op jezelf. Nu wachten allebei de
     drempels op dagen dat je er bent, en de zin zegt welke van de twee nog niet gehaald is. */
  var mistPunten = st.heeft < st.nodig;
  var nogPunten = Math.max(0, st.nodig - st.heeft);
  var nogSpan = Math.max(0, st.spanNodig - st.span);
  var nog = Math.max(nogPunten, nogSpan);
  return ct("Je hebt " + st.heeft + " dagmeting" + (st.heeft === 1 ? "" : "en") + " over " + st.span + " dag" + (st.span === 1 ? "" : "en") + ". ",
            "You have " + st.heeft + " daily measurement" + (st.heeft === 1 ? "" : "s") + " across " + st.span + " day" + (st.span === 1 ? "" : "s") + ". ") +
    ct("Er is een lijn nodig door minstens " + st.nodig + " metingen over minstens " + st.spanNodig + " dagen; " +
       (mistPunten && nogSpan > nogPunten
         ? "de spreiding is nu wat ontbreekt."
         : "elke dag dat je de app opent komt er een punt bij.") + " ",
       "A line needs at least " + st.nodig + " measurements across at least " + st.spanNodig + " days; " +
       (mistPunten && nogSpan > nogPunten
         ? "the spread is what is missing now."
         : "every day you open the app adds a point.") + " ") +
    ct("Kom je elke dag, dan is dat over " + nog + " dag" + (nog === 1 ? "" : "en") + ".",
       "If you come every day, that is " + nog + " day" + (nog === 1 ? "" : "s") + " away.");
}"""
)

# =============================================================================================
# 4. controle
# =============================================================================================
if DOE_APP:
    assert src.count("function tempoDagMeting(") == 1
    assert src.count("dagMetingSchrijf()") == 4, "verwacht drie aanroepen plus de definitie, gevonden %d" % src.count("dagMetingSchrijf()")
    assert "komendeMaandag()" in src, "komendeMaandag wordt elders nog gebruikt en mag niet wegvallen"

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    APP.write_text(src, encoding="utf-8")
    print("index.html: de voorspelling rekent op dagpunten, met een regressie in plaats van een gemiddelde")
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
