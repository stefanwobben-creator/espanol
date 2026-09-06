#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.248 - de app toetste de tijd die nog dicht was, en liep de route van de tijd die open stond niet
#
# Stefan: "ja fix dat nu ook", over "de keuze los van de vorm" (het openstaande advies uit v23.233).
#
# Ik heb eerst gemeten in zijn eigen logboek (tools/logs-latest.json, opname van 6 sep 05:09) en in
# de app met die gegevens erin geladen. Wat daar staat is scherper dan het advies:
#
# ================ DE DRIE METINGEN ================
#
# 1. HET ZWAARSTE ONDERWERP IS EEN COMBINATIE WAARVAN DE BROKKEN ONTBREKEN.
#
#      indefimperf   57 beurten, 64% goed, doos 0, laatst gedaan 5 september
#      S.brok        {}   -- nul routestappen, ooit
#      conjOpen      5    -- "het hele presente"; de verleden tijd staat NIET open
#
#    Hij oefent dus al maanden de keuze tussen indefinido en imperfecto terwijl de vormladder de
#    verleden tijd nog niet eens heeft geopend. Dat is precies zijn eigen klacht van vorige week:
#    "die is veel te moeilijk want ik moet alle tijden van alle werkwoorden herkennen terwijl ik
#    net tegenwoordige tijd ken." Het is geen moeilijkheidsprobleem maar een volgordeprobleem.
#
#      Een combinatievraag stellen terwijl de brokken eronder ongemeten zijn,
#      meet niets en leert niets.
#
# 2. DE APP ZEGT WAARAAN JE WERKT EN GEEFT JE IETS ANDERS.
#
#    v23.234 bouwde gcFocus(): hoogstens twee onderwerpen onderhanden, op zijn eigen verzoek
#    ("dwing dit meer af"). Gemeten met zijn gegevens:
#
#      gcFocus()            ["genero", "concordancia"]     <- dit zegt het scherm
#      lesFlowGramLijst()   ["concept-comparar"]           <- dit geeft de dagles
#
#    gcFocus() stuurt het routescherm en de regel "Waar je nu aan werkt". De dagles komt uit
#    lesFlowGramId(), en die kent gcFocus() helemaal niet: hij loopt een eigen keten van vijf
#    terugvallen af. De limiet die hij vroeg af te dwingen, gold overal behalve waar hij oefent.
#
#      Een belofte die op het scherm staat en nergens wordt afgedwongen, is een mededeling.
#
# 3. DE ROUTE DIE WEL OPEN STAAT, WORDT NIET GELOPEN.
#
#      gramPadNu()                 "presente"
#      gramPadVolgende(presente)   0   -- de eerste stap, "De yo-vorm op -go"
#      acht stappen, nul gedaan
#
#    De presente-route bestaat sinds v23.126 en is precies de ladder uit het advies. Niets in de
#    dagles plant hem. Het vormenblok (v23.160) doet wel lesrijen, maar kiest ze met een eigen
#    regel ("de eerste open rij"), en die volgt de route-volgorde niet. Die volgorde is niet
#    willekeurig: -go staat vooraan omdat drie van die zes werkwoorden daarna ook nog een schoen
#    krijgen. Wie de schoen eerst doet, leert tengo twee keer als iets nieuws.
#
# ================ WAT ER VERANDERT ================
#
# EEN. EEN ONDERWERP WAARVAN DE ROUTE OP SLOT STAAT, WORDT NIET GEVRAAGD.
#
# gcOpenSet() hield alles open wat je ooit had aangeraakt, en dat is terecht: fouten moeten terug
# kunnen komen. Maar niet als de voorwaarde eronder nog niet gehaald is. gcRouteOpen() leest dat uit
# de route zelf (gramPadOpen), dus er komt geen tweede lijst bij en er staat nergens een naam van
# een onderwerp in de code: staat een feit in de data, dan schrijft geen codeplek dat feit opnieuw.
#
# Vandaag raakt dat precies één onderwerp, indefimperf, en niet voor lang: conjOpen staat op 5 en de
# eerstvolgende fase is "verleden tijd 1". Eén fase, niet maanden. Het routescherm zei het al:
# "Gaat open zodra je in de Conjugador bij verleden tijd 1 bent."
#
# TWEE. DE DAGLES KIEST BINNEN DE FOCUS.
#
# lesFlowGramId() vraagt nu eerst gcVandaagLijst(), dezelfde lijst waarmee het routescherm en de
# regel "Waar je nu aan werkt" gevuld worden. Pas als die niets oplevert (een vers profiel) begint
# de oude keten.
#
# De prijs, en die is echt: gramVersKandidaat() koppelde het grammatica-onderwerp aan de les van
# vandaag, en die koppeling verdwijnt zolang de focus gevuld is. Ik betaal hem bewust. Twee
# onderwerpen tot ze op doos 3 staan is wat hij vroeg, en een onderwerp dat bij de woorden van
# vandaag past maar niet bij waar je aan werkt, is de reden dat er zestien halve onderwerpen open
# stonden. De verse-foutuitzondering blijft: gcVandaagLijst() zet die vooraan.
#
# DRIE. HET VORMENBLOK VOLGT DE ROUTE.
#
# vormRijVandaag() koos: de rij met de meeste openstaande fouten, dan een rij waar je al aan begon,
# dan het struikelblok uit "Welke tijd is dit?", dan de eerste open rij. Die laatste stap wordt de
# volgende LESSTAP VAN DE ROUTE. Repareren blijft dus voorgaan op vooruitkomen (dat is de regel van
# v23.161 en die blijft staan); alleen als er niets te repareren valt, loopt de dag de route af.
#
# Wat hierdoor NIET verandert, en dat hoort erbij: de niet-lesstappen van een route (de
# betekenis-brok met twaalf Nederlandse zinnen, "Welke tijd is dit?", de zin, de hertoets) komen
# nog steeds niet vanzelf in de dagles langs. Dat is de rest van "de keuze los van de vorm", en het
# levert vandaag niets op omdat de enige route mét een betekenisstap (indefimperf) op slot staat.
# Het hoort in de ronde waarin die route opengaat, samen met een terugweg naar de les per scherm
# (renderFunLes heeft die, de andere vier niet). Een belofte die alleen in het commentaar staat is
# geen belofte, dus hij staat hier als wat hij is: niet gebouwd.
import pathlib
import re
import sys

W = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / "claude"))
import patchhulp  # noqa: E402

APP = W / "index.html"
VER = W / "versie.txt"
GEPLAND = "v23.248"

src = APP.read_text(encoding="utf-8")
huidig = VER.read_text(encoding="utf-8").strip()
DOE_APP = "function gcRouteOpen(" not in src


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- EEN: een onderwerp waarvan de route op slot staat ----------
    rep(
        """function gcOpenSet(){
  var open = {}, nieuw = 0;
  GC_ORDE.forEach(function(id){
    var st = {};
    try { st = gramLees(id) || {}; } catch(e){ st = {}; }
    if(((st.goed || 0) + (st.fout || 0)) > 0){ open[id] = 1; return; }""",
        """/* v23.248: een onderwerp waarvan de ROUTE nog op slot staat, staat zelf ook op slot.

   Gemeten bij Stefan: indefimperf heeft 57 beurten en staat op 64% en op doos 0, terwijl S.brok
   leeg is en de vormladder op "het hele presente" staat. Hij oefende dus al maanden de keuze
   tussen twee verleden tijden waarvan hij de vormen nog niet had gehad. Dat is geen moeilijk
   onderwerp maar een onderwerp dat te vroeg komt.

   De voorwaarde komt uit de route zelf (gramPadOpen leest lesRijIds), dus er staat hier geen naam
   van een onderwerp en er komt geen tweede lijst bij. Heeft een onderwerp geen route, dan is er
   ook geen voorwaarde en verandert er niets. */
function gcRouteOpen(id){
  var p = null;
  try { p = gramPadVan(String(id || "").replace(/^concept-/, "").split("#")[0]); } catch(e){ p = null; }
  if(!p) return true;
  try { return gramPadOpen(p); } catch(e){ return true; }
}
function gcOpenSet(){
  var open = {}, nieuw = 0;
  GC_ORDE.forEach(function(id){
    var st = {};
    try { st = gramLees(id) || {}; } catch(e){ st = {}; }
    /* vóór de regel hieronder, en niet erna: die houdt alles open wat je ooit hebt aangeraakt, en
       juist een onderwerp met veel beurten is er een waarvan de brokken kunnen ontbreken. */
    if(!gcRouteOpen(id)) return;
    if(((st.goed || 0) + (st.fout || 0)) > 0){ open[id] = 1; return; }""",
    )
    rep(
        """function gcConceptOpen(id){
  id = String(id || "").replace(/^concept-/, "");
  if(GC_ORDE.indexOf(id) === -1) return gcVoorOk(id);   // handgeschreven wizard zonder concept
  return !!gcOpenSet()[id];
}""",
        """function gcConceptOpen(id){
  id = String(id || "").replace(/^concept-/, "");
  /* v23.248: ook de handgeschreven wizards langs de routecontrole, anders zou een onderwerp dat
     niet in GC_ORDE staat maar wel een route heeft er langs de achterdeur toch in komen. */
  if(!gcRouteOpen(id)) return false;
  if(GC_ORDE.indexOf(id) === -1) return gcVoorOk(id);   // handgeschreven wizard zonder concept
  return !!gcOpenSet()[id];
}""",
    )

    # ---------- TWEE-A: "twee keer mis" gaat over deze week, niet over ooit ----------
    rep(
        """function gcStaatFout(st, cid){""",
        """/* v23.248: hoe vaak ging dit onderwerp de afgelopen dagen mis? Zelfde venster en dezelfde bron
   als gcVersFout hierboven, alleen tellend in plaats van oordelend.

   Waarom dit erbij komt: v23.236 verving "st.fout > 0" door de datum uit het ledger, met de reden
   "een fout van vorige maand is geen bericht". Die reparatie landde op gcStaatFout() en dus op het
   routescherm en de daglijst. Maar op twee andere plekken stond dezelfde optelsom nog:
   lesFlowGramId() en lesFlowGramLijst() lezen (st.fout || 0) >= 2 om te beslissen of je de hele
   microles terugkrijgt. Dat is de levenslange teller. Bij Stefan staan zestien onderwerpen op doos
   nul, dus die voorwaarde was praktisch altijd waar, en daardoor kwam de focus nooit aan de beurt.

     Een fout van vorige maand is geen bericht, ook niet als je hem optelt. */
function gcVersMissers(cid){
  var s = String(cid || "").split("#")[0];
  if(!s) return 0;
  var log = null, n = 0;
  try { log = S.gramLog || {}; } catch(e){ return 0; }
  for(var i = 0; i <= GC_VERS_DAGEN; i++){
    var r = (log[addDays(today(), -i)] || {})[s];
    if(!r || !(r.n > 0)) continue;
    n += Math.max(0, r.n - (r.goed || 0));
  }
  return n;
}
function gcStaatFout(st, cid){""",
    )
    rep(
        """    if(!((top.st.box || 0) === 0 && (top.st.fout || 0) >= 2 && !top.st.half)){""",
        """    /* v23.248: gcVersMissers in plaats van st.fout. Zie de kop bij die functie: st.fout is de
       levenslange optelsom en stond bij Stefan op zestien onderwerpen boven nul, dus deze
       uitzondering gold bijna altijd. */
    if(!((top.st.box || 0) === 0 && gcVersMissers(top.c.id) >= 2 && !top.st.half)){""",
    )

    # de uitleg "waarom krijg ik dit" leidt zijn antwoord uit dezelfde toestand af als de keuze;
    # laat je die staan, dan zegt het scherm iets anders dan de app doet
    rep(
        """  if(st && (st.box || 0) === 0 && (st.fout || 0) >= 2){
    return ct("Hier ging het " + st.fout + " keer mis, dus je krijgt de hele uitleg.",
              "This went wrong " + st.fout + " times, so you get the full explanation.");
  }""",
        """  /* v23.248: dezelfde teller als de keuze hierboven. De kop van deze functie belooft dat er geen
     tweede waarheid ontstaat; met de levenslange optelsom hier en het verse venster daar zou het
     scherm "hier ging het 21 keer mis" zeggen op een dag dat de app dit om een heel andere reden
     koos. */
  var vm = 0;
  try { vm = gcVersMissers(cid); } catch(e){ vm = 0; }
  if(st && (st.box || 0) === 0 && vm >= 2){
    return ct("Hier ging het deze week " + vm + " keer mis, dus je krijgt de hele uitleg.",
              "This went wrong " + vm + " times this week, so you get the full explanation.");
  }""",
    )

    # ---------- TWEE-B: de dagles kiest binnen de focus ----------
    rep(
        """  var fout = gramFoutTop();
  if(fout && (fout.st.box || 0) === 0 && (fout.st.fout || 0) >= 2) return "concept-" + fout.c.id;
""",
        """  var fout = gramFoutTop();
  if(fout && (fout.st.box || 0) === 0 && gcVersMissers(fout.c.id) >= 2) return "concept-" + fout.c.id;

  /* v23.248: en dan de focus, uit dezelfde lijst waarmee het routescherm en de regel "Waar je nu
     aan werkt" gevuld worden.

     Gemeten bij Stefan: gcFocus() gaf ["genero", "concordancia"] en de dagles gaf comparar. De
     limiet van v23.234 ("hoogstens twee onderhanden", op zijn eigen verzoek om dat af te dwingen)
     stuurde het scherm en niet het oefenen. Een belofte die nergens wordt afgedwongen is een
     mededeling.

     De prijs: gramVersKandidaat() hieronder koppelde het onderwerp aan de les van vandaag, en die
     koppeling vervalt zolang de focus gevuld is. Bewust betaald. Een onderwerp dat bij de woorden
     van vandaag past maar niet bij waar je aan werkt, is precies hoe er zestien halve onderwerpen
     open kwamen te staan. Verse fouten gaan niet verloren: gcVandaagLijst() zet die vooraan. */
  var fk = gcFocusKandidaat(mijd);
  if(fk) return "concept-" + fk;
""",
    )
    rep(
        """function lesFlowGramId(){""",
        """/* De eerste uit de focuslijst waar ook echt een les van te bouwen is. Zonder die controle zou een
   onderwerp zonder bouwer de dagles zijn grammatica-stap kosten.

   Binnen die lijst geldt nog steeds: afmaken gaat voor beginnen. Dat is de regel van v23.143 en die
   verdwijnt hier niet, hij krijgt alleen een kleinere zaal. Zonder deze lus zou de focus een half
   onderwerp elke dag opnieuw bij stap 1 kunnen laten liggen, en dat is precies wat v23.143 kwam
   repareren. */
function gcFocusKandidaat(mijd){
  var rij = [], bouwbaar = [];
  mijd = mijd || [];
  try { rij = gcVandaagLijst(); } catch(e){ rij = []; }
  for(var i = 0; i < rij.length; i++){
    var id = rij[i] && rij[i].id;
    if(!id) continue;
    /* wat al als opfrisvraag in de les staat, hoeft er niet ook nog als hele microles bij: dan zou
       de dagles \u00e9\u00e9n onderwerp hebben in plaats van opfrissen \u00e9n leren. */
    if(mijd.indexOf(id) !== -1) continue;
    var o = null;
    try { o = gcGebouwd("concept-" + id); } catch(e){ o = null; }
    if(o) bouwbaar.push(id);
  }
  if(!bouwbaar.length) return null;
  for(var j = 0; j < bouwbaar.length; j++){
    var v = {};
    try { v = gwVoortgangLees("concept-" + bouwbaar[j]) || {}; } catch(e){ v = {}; }
    if((v.stap || 0) > 0 && !v.klaar) return bouwbaar[j];
  }
  return bouwbaar[0];
}
function lesFlowGramId(mijd){""",
    )

    # wie kiest, moet weten wat er al ligt: anders kiest de focus het onderwerp dat er als
    # opfrisvraag al in staat, valt het weg tegen de ontdubbeling, en houdt de dag \u00e9\u00e9n
    # grammatica-onderdeel over in plaats van twee
    rep(
        """  var gid = null;
  try { gid = lesFlowGramId(); } catch(e){ gid = null; }""",
        """  var kaal = function(x){ return String(x || "").replace(/^(opfris|concept)-/, "").split("#")[0]; };
  var alHier = uit.map(kaal);
  var gid = null;
  /* v23.248: mét de lijst van wat er al ligt. De ontdubbeling hieronder blijft staan als vangnet,
     maar hij kwam te laat: hij gooide het onderwerp weg dat de dagles net had gekozen, en dan stond
     er alleen nog een opfrisvraag. Opfrissen vervangt het leren niet. */
  try { gid = lesFlowGramId(alHier); } catch(e){ gid = null; }""",
    )

    rep(
        """  var kaal = function(x){ return String(x || "").replace(/^(opfris|concept)-/, "").split("#")[0]; };
  var alHier = uit.map(kaal);
  if(gid && alHier.indexOf(kaal(gid)) === -1) uit.push(gid);""",
        """  if(gid && alHier.indexOf(kaal(gid)) === -1) uit.push(gid);""",
    )

    # ---------- DRIE: het vormenblok volgt de route ----------
    rep(
        """  var w = null;
  try { w = tijdvormTopVerwar(); } catch(e){ w = null; }
  if(w && w.getoond && open.indexOf(w.getoond) !== -1) return w.getoond;
  return open[0];
}""",
        """  var w = null;
  try { w = tijdvormTopVerwar(); } catch(e){ w = null; }
  if(w && w.getoond && open.indexOf(w.getoond) !== -1) return w.getoond;
  /* v23.248: en anders de volgende LESSTAP VAN DE ROUTE, in plaats van simpelweg de eerste open
     rij. Die volgorde is niet willekeurig: -go staat vooraan omdat drie van die zes werkwoorden
     daarna ook nog een schoen krijgen, en wie de schoen eerst doet leert tengo twee keer als iets
     nieuws. Repareren blijft vóór vooruitkomen (de drie regels hierboven); dit is wat er gebeurt
     als er niets te repareren valt.

     Gemeten bij Stefan: de presente-route heeft acht stappen en nul ervan zijn gedaan, terwijl het
     vormenblok sinds v23.160 elke tweede dag draait. */
  var uitRoute = vormRijUitRoute(open);
  if(uitRoute) return uitRoute;
  return open[0];
}
/* De eerste lesstap van de route van nu die nog niet af is en die vandaag te doen is. Geeft null
   als er geen route is, als de route geen lesstappen heeft, of als de rij die hij aanwijst niet in
   de open rijen staat: dan beslist de aanroeper, niet deze functie. */
function vormRijUitRoute(open){
  var p = null;
  try { p = gramPadNu(); } catch(e){ p = null; }
  if(!p) return null;
  for(var i = 0; i < (p.stappen || []).length; i++){
    var s = p.stappen[i];
    if(s.soort !== "les" || !s.arg) continue;
    if(open.indexOf(s.arg) === -1) continue;
    var x = null;
    try { x = gramPadStap(p, i); } catch(e){ x = null; }
    if(x && x.af) continue;
    return s.arg;
  }
  return null;
}""",
    )

    kaal = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
    assert kaal.count("function gcRouteOpen(") == 1, "gcRouteOpen niet precies een keer"
    assert kaal.count("function gcFocusKandidaat(") == 1, "gcFocusKandidaat niet precies een keer"
    assert kaal.count("function vormRijUitRoute(") == 1, "vormRijUitRoute niet precies een keer"
    assert kaal.count("gcRouteOpen(id)") == 3, "gcRouteOpen wordt niet op twee plekken gebruikt"
    assert kaal.count("function gcVersMissers(") == 1, "gcVersMissers niet precies een keer"
    assert kaal.count("gcVersMissers(") == 4, "gcVersMissers: een definitie en drie lezers"
    assert "(st.fout || 0) >= 2" not in kaal and "(top.st.fout || 0) >= 2" not in kaal, \
        "er staat nog een levenslange fouttelling met drempel twee"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de route bepaalt wat er gevraagd wordt en wat je vandaag doet")
else:
    print("index.html: stond er al")

nieuw, doe_ver, reden = patchhulp.nummerKiezen(huidig, GEPLAND, DOE_APP)
if reden:
    print("LET OP: " + reden)
if doe_ver:
    patchhulp.zetVersie(APP, VER, huidig, nieuw)
    print("versie.txt: %s -> %s" % (huidig, nieuw))
else:
    print("versie.txt: stond al op " + huidig)
