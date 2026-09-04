#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.236 - de ladder stond open op de bovenste trede
#
# Stefan, 4 sep: "ik heb net el la gedaan weer goed en die blijft zeggen fout gegaan, ik zie ook niet
# de voortgang en de oefening met alle tijden bij grammatica staat er nog maar die is veel te
# moeilijk want ik moet alle tijden van alle werkwoorden herkennen terwijl ik net tegenwoordige tijd
# ken en nu misschien toe ben aan een verleden tijd en daarna de twee verleden tijdsvormen etc, die
# grote wijzigingen om me te helpen met grammatica blijven maar uit"
#
# Drie klachten, twee oorzaken, en de tweede is de grote.
#
# ============ EEN: "FOUT GEGAAN" KON NIET UITGEZET WORDEN DOOR IETS GOED TE DOEN ============
#
# v23.232 verving "st.fout && box === 0" (de optelsom van alle fouten ooit) door een datum:
#
#     box === 0  &&  st.laatst >= vandaag - 2
#
# Beter, en nog steeds fout. st.laatst wordt in gramBij() alleen bij een FOUT geschreven, en
# gramLees() vat een concept samen door de doos van het ZWAKSTE doosje te nemen en de laatst-datum
# van het MEEST RECENTE doosje. Twee feiten uit twee verschillende rijen, als één toestand gelezen.
#
# Gevolg, precies wat Stefan beschrijft: een fout van eergisteren zet het rood aan, en daarna kan
# geen enkel goed antwoord het uitzetten. Alleen wachten helpt. De goede en de foute uitkomst
# krijgen dezelfde waarde, en dan controleert de controle niets.
#
# Nu beslist de laatste DAG dat je dit onderwerp deed, uit S.gramLog (dat ligt er sinds v23.211 en
# is zeven dagen diep, dus het venster van twee dagen past er ruim in):
#
#     de meest recente dag binnen het venster waarop je beurten had, telt
#     alles goed die dag  ->  niet fout gegaan
#     een misser die dag  ->  wel
#     geen beurten        ->  geen bericht
#
# Eén dag goed en het rood is weg. Dat is dezelfde maat die de doos gebruikt ("één misser vandaag en
# de promotie gaat niet door"), dus het rode woord en het doosje zeggen vanaf nu hetzelfde.
#
# En het oordeel heeft nu het concept nodig, niet alleen zijn samenvatting. Alle vier de aanroepers
# geven hem mee; zonder concept geeft de functie geen oordeel in plaats van een verkeerd oordeel.
#
# ============ TWEE: DE LADDER STOND OPEN OP DE BOVENSTE TREDE ============
#
# De ladder die Stefan beschrijft bestaat al, en precies in zijn volgorde. CONJ_FASES heeft dertien
# treden:
#
#     1-6   het presente     -ar, -er, -ir, alle zes de personen, de onregelmatige, het geheel
#     7-8   indefinido       verleden tijd 1, en compleet
#     9-10  imperfecto       hoe het was, en compleet
#     11    perfecto         verleden tijd 2
#     12    subjuntivo
#     13    mix              alles door elkaar
#
# Alleen: conjOpenInit() zette voor iedereen die ooit een fout in de Conjugador had gemaakt
#
#     open = CONJ_FASES.length - 1
#
# dus trede DERTIEN, en conjFaseNu() kiest bij gebrek aan een keuze de hoogste die openstaat. Stefan
# heeft 42 conj:-sleutels in zijn foutenboek (gemeten in tools/logs-latest.json), dus hij staat sinds
# dag één op "alles door elkaar" en heeft geen enkele trede beklommen.
#
# Het werkt door tot in zijn dagles: conjOpenTijden() leest dezelfde stand en geeft dan alle vijf de
# tijden terug, en lesRijIds() bouwt daaruit de rijen van het vormenblok. Vandaar dat hij subjuntivo-
# rijen krijgt terwijl hij het presente nog aan het verwerven is. Niet één oefening die te moeilijk
# staat: de hele ladder stond op de eindstand.
#
# De bedoeling was vriendelijk ("wat je gisteren al kon, neemt een update je niet af"), maar wat
# gemeten is, is dat hij het nooit kon: hij kreeg het cadeau.
#
# Wat er nu staat:
#
#   1. De migratie zet hem terug op "het hele presente", tenzij hij die trede aantoonbaar heeft
#      afgerond (8 van de laatste 10 goed, dezelfde eis die het klimmen stelt). Alleen omlaag, nooit
#      omhoog, en nooit lager dan het hele presente: een beginner die op trede 1 staat blijft daar.
#   2. Wie ooit zelf een trede heeft geopend (verdiend of overgeslagen) draagt S.conjKlim en wordt
#      met rust gelaten.
#   3. Er komt een knop "Ik kan dit al" naast de meter. Er wordt dus niets afgepakt: het kost één
#      tik, en het is zijn keuze in plaats van de aanname van de app.
#   4. En nieuw binnenkomen met een oefengeschiedenis geeft niet langer de eindstand maar het hele
#      presente, zodat dit niet opnieuw ontstaat.
#
# ============ EN DE MIGRATIE KON ZICHZELF SLOPEN ============
#
# Terwijl ik daar was: conjLadderMigratie() draaide zijn oude elfdelige omnummering opnieuw bij elke
# volgende ladderversie. CONJ_FASES_OUD11[8] is "perfecto", en dat is in de huidige dertiendelige
# lijst nummer 11 in plaats van 9. Wie op trede 9 stond zou bij de volgende bump naar 11 springen,
# twee tijden cadeau. Een migratie die twee keer kan draaien is geen migratie. Hij kijkt nu naar de
# versie die hij verlaat en doet elke stap één keer.
#
# ============ DRIE: "IK ZIE OOK NIET DE VOORTGANG" ============
#
# Met (1) verdwijnt het rode woord zodra hij een dag goed doet, en dan staat er weer "doos 1/5 · 80%
# goed deze week". En op de tijdenkaart staat vanaf nu waar hij op de ladder staat en welke tijden
# nog dicht zijn, want een kaart met zes tijden erop terwijl je er één oefent, leest als een lijst
# van wat je allemaal nog niet kunt.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.236"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function gcVersFout(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. het oordeel "fout gegaan" ----------
    rep("""var GC_VERS_DAGEN = 2;
function gcStaatFout(st){
  if(!st || !st.laatst) return false;
  if((st.box || 0) !== 0) return false;
  return st.laatst >= addDays(today(), -GC_VERS_DAGEN);
}""",
"""/* v23.236: en dat las nog steeds twee feiten uit twee verschillende rijen.

   st.laatst wordt in gramBij() alleen bij een FOUT geschreven, dus als datum klopt hij. Maar
   gramLees() vat een concept samen door de doos van het ZWAKSTE doosje te nemen en de laatst-datum
   van het MEEST RECENTE doosje. Die twee hoeven niet uit hetzelfde doosje te komen.

   Gevolg, Stefan op 4 september: "ik heb net el la gedaan weer goed en die blijft zeggen fout
   gegaan." Een misser van eergisteren zet het rood aan, en daarna kan geen enkel goed antwoord het
   uitzetten; alleen wachten helpt. De goede en de foute uitkomst krijgen dezelfde waarde, en dan
   controleert de controle niets.

   Nu beslist de laatste dag dat je dit onderwerp deed, uit het ledger. Alles goed die dag: geen
   bericht. Een misser die dag: wel. Geen beurten binnen het venster: geen bericht. Dat is dezelfde
   maat als de doos zelf hanteert, dus het rode woord en het doosje spreken elkaar niet meer tegen,
   en één dag goed doen is genoeg om het uit te zetten. */
var GC_VERS_DAGEN = 2;
function gcVersFout(cid){
  var s = String(cid || "").split("#")[0];
  if(!s) return false;
  var log = null;
  try { log = S.gramLog || {}; } catch(e){ return false; }
  for(var i = 0; i <= GC_VERS_DAGEN; i++){
    var r = (log[addDays(today(), -i)] || {})[s];
    if(!r || !(r.n > 0)) continue;   /* die dag geen beurt: die zegt niets */
    return (r.goed || 0) < r.n;      /* de laatste dag dat je het deed, beslist */
  }
  return false;
}
/* Het concept moet mee. Zonder concept is er geen ledger om te lezen, en dan geeft deze functie
   liever geen oordeel dan het oude verkeerde: een verkeerde diagnose is erger dan geen. */
function gcStaatFout(st, cid){
  if(!st || !cid) return false;
  if((st.box || 0) !== 0) return false;
  return gcVersFout(cid);
}""")

    rep("""  if(gcStaatFout(st)) return "<span style='color:var(--red)'>""",
        """  if(gcStaatFout(st, cid)) return "<span style='color:var(--red)'>""")

    rep("""  var af = (st.goed || 0) > 0 && (st.box || 0) > 0 && !gcStaatFout(st);""",
        """  var af = (st.goed || 0) > 0 && (st.box || 0) > 0 && !gcStaatFout(st, c.id);""")

    rep("""    if(open[c.id] && gcStaatFout(st)){ fout.push({c:c, st:st}); return; }""",
        """    if(open[c.id] && gcStaatFout(st, c.id)){ fout.push({c:c, st:st}); return; }""")

    rep("""    else if(gcStaatFout(st)) fout++;""",
        """    else if(gcStaatFout(st, c.id)) fout++;""")

    # ---------- 1b. wie de doos bijwerkt, schrijft ook het ledger ----------
    rep("""function gramBij(cid, goed, keuzes, pi){
  if(!cid) return;
  S.gram = S.gram || {};""",
"""/* v23.236: het ledger wordt hier geschreven en niet meer door de aanroeper.

   Zeven plekken deden dit tot nu toe met de hand, en alle zeven schreven ze twee regels achter
   elkaar: gramBij() voor de doos, gramLog() voor het ledger. Zolang het ledger alleen een
   weekpercentage voedde was een vergeten regel een schoonheidsfoutje. Sinds hierboven het oordeel
   "fout gegaan" uit datzelfde ledger komt, is een vergeten regel een verkeerd oordeel.

   Een regel die voor zeven plekken geldt hoort door één plek afgedwongen te worden. Het kanaal komt
   mee als vijfde argument; wie het weglaat schrijft "overig", want dát er een beurt was is het
   feit dat telt, en welk scherm hem gaf is de verfijning. */
function gramBij(cid, goed, keuzes, pi, kanaal){
  if(!cid) return;
  try { gramLog(cid, kanaal || "overig", !!goed); } catch(e){}
  S.gram = S.gram || {};""")

    for oud, nieuw in [
        ("""gcConceptenVoorQuiz(qz).forEach(function(cid){ gramBij(cid, pct >= 0.8); gramLog(cid, "toets", pct >= 0.8); });""",
         """gcConceptenVoorQuiz(qz).forEach(function(cid){ gramBij(cid, pct >= 0.8, 0, null, "toets"); });"""),
        ("""if(!t.echt && t.cid){ gramBij(t.cid, false); gramLog(t.cid, "tegels", false); }""",
         """if(!t.echt && t.cid){ gramBij(t.cid, false, 0, null, "tegels"); }"""),
        ("""if(fregel){ gramBij(fregel.cid, false); gramLog(fregel.cid, "zin", false); }""",
         """if(fregel){ gramBij(fregel.cid, false, 0, null, "zin"); }"""),
        ("""  gramBij(clSpel.c.id, false); gramLog(clSpel.c.id, "clasificador", false);""",
         """  gramBij(clSpel.c.id, false, 0, null, "clasificador");"""),
        ("""    gramBij(clSpel.c.id, true); gramLog(clSpel.c.id, "clasificador", true);""",
         """    gramBij(clSpel.c.id, true, 0, null, "clasificador");"""),
        ("""  gramBij(gcConceptVoorCorr(id), goed); gramLog(gcConceptVoorCorr(id), "corrector", goed);""",
         """  gramBij(gcConceptVoorCorr(id), goed, 0, null, "corrector");"""),
    ]:
        rep(oud, nieuw)

    rep("""  gramBij(o.concept, goed, (q && q.o) ? q.o.length : 0, (q && typeof q.pi === "number") ? q.pi : null);
  gramLog(o.concept, gwKanaal(o), goed);""",
"""  gramBij(o.concept, goed, (q && q.o) ? q.o.length : 0,
          (q && typeof q.pi === "number") ? q.pi : null, gwKanaal(o));""")

    # ---------- 2. de ladder ----------
    rep("""var CONJ_FASES_OUD11 = ["ar","er","ir","seis","onreg","presente","indefreg","indef","perfecto","subjuntivo","mix"];
var CONJ_LADDER_NU = 13;
function conjLadderMigratie(){
  if(S.conjLadder === CONJ_LADDER_NU) return;
  if(typeof S.conjOpen === "number"){
    var oudId = CONJ_FASES_OUD11[S.conjOpen];
    var n = oudId ? conjFaseIdx(oudId) : -1;
    if(n >= 0) S.conjOpen = n;
  }
  S.conjLadder = CONJ_LADDER_NU;
  try { persist(); } catch(e){}
}""",
"""var CONJ_FASES_OUD11 = ["ar","er","ir","seis","onreg","presente","indefreg","indef","perfecto","subjuntivo","mix"];
/* Heeft deze trede het criterium gehaald? Dezelfde eis die conjProbeerOntgrendelen() stelt, want
   twee plekken die "af" verschillend uitrekenen zijn twee waarheden. */
function conjFaseAf(id){
  var sc = conjFaseScore(id);
  return sc.n >= CONJ_ONTGRENDEL_N && sc.goed >= CONJ_ONTGRENDEL_GOED;
}
/* ================= DE LADDER STOND OPEN OP DE BOVENSTE TREDE (v23.236) =================

   Stefan: "die oefening met alle tijden is veel te moeilijk want ik moet alle tijden van alle
   werkwoorden herkennen terwijl ik net tegenwoordige tijd ken."

   Hieronder gaf conjOpenInit() aan iedereen met ook maar één conj:-fout in zijn foutenboek de hele
   ladder open, en conjFaseNu() kiest bij gebrek aan een keuze de hoogste die openstaat. Stefan heeft
   er 42, dus hij stond sinds dag één op trede dertien, "alles door elkaar", zonder ooit een trede
   beklommen te hebben. En conjOpenTijden() leest dezelfde stand, dus zijn dagles bouwde vormenblokken
   in alle vijf de tijden.

   De migratie hieronder zet hem terug op "het hele presente". Alleen omlaag, nooit omhoog, en nooit
   lager dan die trede: wie op trede 1 staat blijft daar. Wie de trede aantoonbaar heeft afgerond
   blijft staan, en wie ooit zelf een trede opende (S.conjKlim) wordt met rust gelaten. Er wordt niets
   afgepakt: naast de meter staat een knop "Ik kan dit al" die dezelfde sprong met de hand maakt.

   EN DE MIGRATIE KON ZICHZELF SLOPEN. Hier stond de omnummering van de oude elfdelige ladder zonder
   te kijken wélke versie hij verliet, dus hij draaide opnieuw bij elke volgende bump.
   CONJ_FASES_OUD11[8] is "perfecto" en dat is in de dertiendelige lijst nummer 11 in plaats van 9:
   wie op 9 stond zou naar 11 springen, twee tijden cadeau. Een migratie die twee keer kan draaien is
   geen migratie. Elke stap kijkt nu naar de versie die hij verlaat, en doet zichzelf één keer. */
var CONJ_LADDER_NU = 14;
function conjLadderMigratie(){
  var was = (typeof S.conjLadder === "number") ? S.conjLadder : 0;
  if(was === CONJ_LADDER_NU) return;
  if(was < 13 && typeof S.conjOpen === "number"){
    var oudId = CONJ_FASES_OUD11[S.conjOpen];
    var n = oudId ? conjFaseIdx(oudId) : -1;
    if(n >= 0) S.conjOpen = n;
  }
  if(was < 14 && typeof S.conjOpen === "number" && !S.conjKlim){
    var p = conjFaseIdx("presente");
    if(p >= 0 && S.conjOpen > p && !conjFaseAf("presente")){
      S.conjOpen = p;
      if(conjFaseIdx(S.conjFase) > p) S.conjFase = "presente";
    }
  }
  S.conjLadder = CONJ_LADDER_NU;
  try { persist(); } catch(e){}
}""")

    rep("""  if(geoefend || S.conjStap === "breed" || S.conjStap === "tijden"){
    open = CONJ_FASES.length - 1;
  } else {
    var p = null;
    try { p = activeProfile(); } catch(e){}
    open = (p && p.track === "beginner") ? 0 : conjFaseIdx("presente");
  }""",
"""  /* v23.236: hier kreeg wie al eens geoefend had de laatste trede van de ladder toegewezen, oftewel
     de eindstand. Bedoeld als vriendelijkheid, in de praktijk een leerling die op "alles
     door elkaar" begint zonder ooit een trede te hebben gehaald. Een oefengeschiedenis zegt dat je
     het presente hebt gezien, niet dat je de subjuntivo kunt: dus het hele presente, en klimmen. */
  if(S.conjStap === "breed" || S.conjStap === "tijden") geoefend = true;
  var p = null;
  try { p = activeProfile(); } catch(e){}
  open = (p && p.track === "beginner" && !geoefend) ? 0 : conjFaseIdx("presente");""")

    # het klimmen laat vanaf nu een spoor achter, zodat de migratie het herkent
    rep("""  S.conjOpen = i + 1;
  S.conjFase = CONJ_FASES[i+1].id;
  if(S.conjLaatste) S.conjLaatste[CONJ_FASES[i].id] = [];""",
"""  S.conjOpen = i + 1;
  S.conjFase = CONJ_FASES[i+1].id;
  S.conjKlim = 1;   /* v23.236: wie zelf geklommen is, wordt door geen enkele migratie teruggezet */
  if(S.conjLaatste) S.conjLaatste[CONJ_FASES[i].id] = [];""")

    # ---------- 3. de handrem: "Ik kan dit al" ----------
    rep("""              CONJ_ONTGRENDEL_GOED+" out of your last "+CONJ_ONTGRENDEL_N+" correct opens the next phase ("+vol+"/"+CONJ_ONTGRENDEL_GOED+")")+
         "</p>"+""",
"""              CONJ_ONTGRENDEL_GOED+" out of your last "+CONJ_ONTGRENDEL_N+" correct opens the next phase ("+vol+"/"+CONJ_ONTGRENDEL_GOED+")")+
         "</p>"+
         /* v23.236: de handrem. De app plaatst je op de trede waar het werk ligt, maar hij weet het
            niet beter dan jij. Dit staat alleen op de bovenste open trede, want lager overslaan doet
            niets: die zijn al open. */
         (i === open
           ? "<div class='row' style='margin:0 0 6px'><button type='button' class='ghost' id='btnCjOverslaan' style='padding:5px 10px; font-size:0.78rem; min-width:0'>"+
               ct("Ik kan dit al, open de volgende", "I know this already, open the next one")+"</button></div>"
           : "")+""")

    rep("""function wireConjFaseKiezer(){
  var row = document.getElementById("cjFase");
  if(!row) return;""",
"""function wireConjFaseKiezer(){
  var row = document.getElementById("cjFase");
  if(!row) return;
  /* v23.236: met de hand een trede hoger. Precies één, want "sla alles over" is weer de eindstand
     cadeau, en dat is nu juist wat we repareren. S.conjKlim erbij: vanaf nu is de stand een keuze
     van de leerling en geen aanname van de app, en geen migratie zet hem meer terug. */
  var ov = document.getElementById("btnCjOverslaan");
  if(ov) ov.onclick = function(){
    var i = conjFaseIdx(conjFaseNu().id);
    if(i < 0 || i >= CONJ_FASES.length - 1 || i !== conjOpenMax()) return;
    S.conjOpen = i + 1;
    S.conjFase = CONJ_FASES[i+1].id;
    S.conjKlim = 1;
    try { persist(); } catch(e){}
    conjIdx = pickConjugacion();
    cjModusOverride = null;
    cjMk = null;
    renderFunConjugador();
  };""")

    # ---------- 4. waar sta je, op de tijdenkaart ----------
    rep("""function tijdenRijHtml(t){
  var vb = (profLang() === "nl" ? t.vb : (t.vbEn || t.vb));
  return "<details class='tijdrij' data-tijd='" + t.id + "'><summary><b>" + t.es + "</b> \\u00b7 " +
      ct(t.nl, t.en) + "</summary><div class='inner'>" +""",
"""/* De tijden die op de conjugatieladder staan. Afgeleid en niet overgeschreven: futuroir staat wel
   op deze kaart en niet op de ladder, en dan hoort er ook geen "komt later" bij te staan. */
function tijdLadderTijden(){
  var uit = [];
  try {
    CONJ_FASES.forEach(function(f){
      if(f.tijd && f.tijd !== "mix" && uit.indexOf(f.tijd) === -1) uit.push(f.tijd);
    });
  } catch(e){ return []; }
  return uit;
}
/* v23.236: zes tijden op een kaart terwijl je er één oefent, leest als een lijst van wat je nog
   niet kunt. Deze regel zegt welke van de zes vandaag jouw werk is. */
function tijdenLadderHtml(){
  var f = null, open = [], lad = tijdLadderTijden();
  try { f = conjFaseNu(); open = conjOpenTijden(); } catch(e){ return ""; }
  if(!f || !lad.length) return "";
  function naam(id){ var t = tijdVan(id); return t ? t.es : id; }
  var dicht = lad.filter(function(x){ return open.indexOf(x) === -1; });
  return "<p class='muted' id='tijdLadder' style='margin:0 0 12px; font-size:.85rem'>" +
    ct("Je oefent nu: ", "You are drilling: ") + "<b>" +
      (f.tijd === "mix" ? ct("alles door elkaar", "everything mixed") : naam(f.tijd)) + "</b>" +
    (dicht.length ? " \\u00b7 " + ct("nog dicht: ", "still locked: ") + dicht.map(naam).join(", ") : "") +
    "</p>";
}
function tijdenRijHtml(t){
  var vb = (profLang() === "nl" ? t.vb : (t.vbEn || t.vb));
  var merk = "";
  try {
    var lad = tijdLadderTijden();
    if(lad.indexOf(t.id) !== -1){
      var nu = conjFaseNu().tijd, open = conjOpenTijden();
      if(t.id === nu) merk = " <span style='color:var(--accent); font-size:.76rem'>\\u00b7 " +
        ct("hier oefen je nu", "you are here") + "</span>";
      else if(open.indexOf(t.id) === -1) merk = " <span class='muted' style='font-size:.76rem'>\\u00b7 " +
        ct("komt later", "comes later") + "</span>";
    }
  } catch(e){ merk = ""; }
  return "<details class='tijdrij' data-tijd='" + t.id + "'><summary><b>" + t.es + "</b> \\u00b7 " +
      ct(t.nl, t.en) + merk + "</summary><div class='inner'>" +""")

    rep("""    "<h3 style='margin:14px 0 6px'>" + ct("De zes op een rij", "The six of them") + "</h3>" +
    TIJDEN.map(tijdenRijHtml).join("") +""",
"""    "<h3 style='margin:14px 0 6px'>" + ct("De zes op een rij", "The six of them") + "</h3>" +
    tijdenLadderHtml() +
    TIJDEN.map(tijdenRijHtml).join("") +""")

if DOE_APP:
    for nodig in ["function gcVersFout(", "function gcStaatFout(st, cid)",
                  "gcStaatFout(st, cid)", "gcStaatFout(st, c.id)",
                  "function conjFaseAf(", "var CONJ_LADDER_NU = 14",
                  "S.conjKlim = 1", "btnCjOverslaan",
                  "function tijdLadderTijden(", "function tijdenLadderHtml("]:
        assert nodig in src, "ontbreekt: " + nodig
    # geen enkele aanroeper mag het oordeel nog zonder concept vragen
    assert "gcStaatFout(st)" not in src, "er is nog een aanroeper zonder concept"
    assert src.count("function gcStaatFout(") == 1, "gcStaatFout staat er meer dan een keer"
    # het oordeel leest het ledger en niet meer de laatst-datum
    blok = src[src.index("function gcVersFout("):src.index("function gcStatusHtml(")]
    assert "S.gramLog" in blok, "het oordeel leest het ledger niet"
    assert "st.laatst" not in blok, "het oordeel leest nog steeds de laatst-datum"
    # de eindstand wordt nergens meer cadeau gedaan bij binnenkomst
    ini = src[src.index("function conjOpenInit("):src.index("function conjOpenMax(")]
    assert "CONJ_FASES.length - 1" not in ini, "conjOpenInit geeft nog steeds de eindstand"
    # de migratie doet elke stap één keer
    mig = src[src.index("function conjLadderMigratie("):src.index("function conjOpenInit(")]
    assert "was < 13" in mig and "was < 14" in mig, "de migratie kijkt niet naar de versie die hij verlaat"
    assert "conjFaseAf(\"presente\")" in mig, "de migratie negeert een afgeronde trede"
    # het ledger wordt op één plek geschreven, en niet meer door de aanroepers
    ENIGE = 'gramLog(cid, kanaal || "overig"'
    assert src.count(ENIGE) == 1, "gramBij schrijft het ledger niet"
    # Commentaar eerst weg: dit is de derde keer deze ronde dat een controle zijn eigen toelichting
    # aanwees als overtreding. Een controle die zijn eigen tekst leest, controleert niets.
    kaal = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
    los = [r.strip() for r in kaal.split("\n")
           if "gramLog(" in r and "function gramLog(" not in r and "S.gramLog" not in r
           and ENIGE not in r and "gramLogVandaag" not in r]
    assert not los, "er schrijft nog een aanroeper zelf naar het ledger: " + str(los[:2])
    APP.write_text(src, encoding="utf-8")
    print("index.html: het oordeel leest het ledger, en de ladder staat weer onderaan")
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
