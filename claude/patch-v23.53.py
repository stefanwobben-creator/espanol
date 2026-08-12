#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.53: de grammatica heeft een volgorde, en die volgorde is een poort.

Stefan, telefoontest 11 aug, bevinding 2 en 5:
  "de grammatica cual of que is veel te moeilijk. Je moet met de makkelijkste als begonnen, dat is
   denk ik el of la, les of las"
  "en wat fout is dat ik alles kan doen, dus dingen die nog ver boven mijn niveau liggen"

Dat zijn twee klachten met dezelfde oorzaak: de app heeft geen idee welk grammaticaonderwerp
makkelijk is. Nergens staat een volgorde. Waar de code toch moest kiezen, koos hij op de volgorde
van het array of op wat er toevallig in de spiekbrief van je les stond.

## Wat er gemeten is, op een vers A0-profiel

    Grammatica-tab, dag 1:      23 conceptkaartjes
                              +  5 diepe lessen  (waaronder subjuntivo)
                              + 22 gegenereerde onderwerpen
                              = 50 onderwerpen, allemaal open

    De grammatica-stap in je eerste dagles:  concept-quecual
    Chispa's Clasificador biedt aan:         muymucho, serestar, porpara, perfindef,
                                             saberconocer, gustar, genero, quecual,
                                             apersonal, negacion

Stefans voorbeeld was geen ongelukje: `lesFlowGramId()` kiest een concept dat hangt aan een
spiekbriefkaart van je huidige les, en les 1 verwijst nu eenmaal naar kaart 4, en dat is qué of
cuál. De app deed precies wat er stond.

## Wat ik eerst probeerde, en waarom het niet werkt

De curriculumdata bevat al een soort volgorde: elke les verwijst naar spiekbriefkaarten, en elk
concept hangt aan zo'n kaart. Daaruit valt een rangorde af te leiden. Gemeten:

    les 0  quecual      les 3  muymucho     les 5  gustar        les 9  perfindef
    les 1  serestar     les 3  hayestar     les 6  reflexivo     les 9  saberpoder
    les 2  genero       les 4  concordancia les 7  pedirpreguntar
                        les 4  demostrativo

En elf van de drieentwintig concepten hangen aan geen enkele les. Die afgeleide volgorde zet
quecual dus op nummer 1 en genero op nummer 3: precies verkeerd om, op precies het concept waar
Stefan over viel. De lessenreeks is geschreven om woorden te ordenen, niet om grammatica te
ordenen. Hem hiervoor gebruiken is data hergebruiken voor iets waar hij nooit voor bedoeld was.

## Wat het wel is

Een expliciete, met de hand geschreven volgorde: `GC_ORDE`, drieentwintig ids van makkelijk naar
moeilijk. Dat is een oordeel, en dat hoort het te zijn: welk grammaticaonderwerp makkelijk is, is
didactiek en geen meetwaarde. Maar de *vorm* is wel machinaal controleerbaar, en dat is het
verschil met een getalletje dat ik verzin:

  - elk concept in GC_CONCEPTEN staat precies een keer in GC_ORDE
  - elke id in GC_ORDE bestaat
  - elke voorwaarde in GC_VOOR bestaat en staat eerder in GC_ORDE (dus: geen kringetjes)
  - op dag 1 staat er minstens een concept open, en genero is er een van

Die vier regels staan in test/suites/pw-gramorde.js. Als iemand later een concept toevoegt en
vergeet het in de volgorde te zetten, gaat de poort rood.

Daarnaast `GC_VOOR`: hoogstens twee voorgangers per concept, en alleen waar het onvermijdelijk is.
Vijf regels, meer niet:

    concordancia -> genero          je kunt woorden niet laten meebuigen als je el/la niet kent
    demostrativo -> genero          este/esta is hetzelfde probleem
    hayestar     -> serestar        hay tegenover está gaat over estar
    pronombre    -> apersonal       lo/la/le vervangt precies wat de persoonlijke a markeert
    indefimperf  -> perfindef       twee verledens vergelijken kan pas als je er een kent
    subjuntivo   -> indefimperf     (de handgeschreven diepe les)

## De poort

Alles wat je ooit hebt aangeraakt blijft open: wat je fout deed moet terug kunnen komen. Daarbovenop
staan er `GC_VENSTER` = 3 nieuwe onderwerpen open, in volgorde, en een onderwerp waarvan de
voorganger nog niet goed is gegaan slaat zijn beurt over (dan schuift de volgende op, zodat er
altijd echt drie te kiezen zijn).

Op dag 1 levert dat: genero, serestar, negacion. Concordancia en hayestar wachten op hun voorganger.

Dezelfde poort geldt nu voor de drie plekken waar het misging:

  1. de dagles                 lesFlowGramId(): een spiekbriefkaart mag geen concept meer openen
                               dat nog dicht staat, en er is een stap bij gekomen die het eerste
                               open concept pakt. Dag 1 wordt daarmee concept-genero.
  2. de Grammatica-tab         gcLijst() staat in volgorde en toont alleen wat open is, GRAMWIZ
                               volgt dezelfde poort (subjuntivo verdwijnt tot je zover bent), en de
                               gegenereerde onderwerpen volgen je lespositie.
  3. Chispa's Clasificador     clConcepten() speelt alleen met wat open staat.

## Wat er niet verandert

Het aantal blijft zichtbaar. Er staat nu "nog 20 komen later" onder de lijst, want verstoppen zonder
te zeggen dat je verstopt is precies de fout die de onboarding in v23.45 maakte.

En het zoekvenster vindt nog steeds elk concept. Zoeken is een bewuste handeling; als je expliciet
"por para" intikt mag je het krijgen. De poort gaat over wat de app je aanbiedt.

## Wat hierna komt, en bewust niet nu

Stefan: "veel tekst, weinig voorbeelden, weinig stap voor stap, dat kan denk ik nog meer micro
steps." Dat is de herontwerp van de uitleg zelf (voorbeeld eerst, dan de keuze, dan een regel van
een zin) en dat is na de lancering. Deze versie gaat alleen over welk onderwerp je krijgt, niet over
hoe het eruitziet. Staat in claude/lancering.md.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.53"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "var GC_ORDE" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_GCCONCEPT = '''function gcConcept(id){'''

A_GCLIJST = '''function gcLijst(){
  return GC_CONCEPTEN.map(function(c){ return gcOnderwerp("concept-" + c.id); }).filter(Boolean);
}'''

A_VANDAAG = '''function gcVandaagLijst(){
  var t = today(), fout = [], due = [], nieuw = [];
  GC_CONCEPTEN.forEach(function(c){
    var st = gramLees(c.id);
    if(!st.goed && !st.fout){ nieuw.push(c); return; }
    if(st.fout && (st.box || 0) === 0){ fout.push({c:c, st:st}); return; }
    if(!st.due || st.due <= t) due.push({c:c, st:st});
  });
  function opBox(a, b){ return (a.st.box || 0) - (b.st.box || 0); }
  fout.sort(opBox); due.sort(opBox);
  // twee plekken voor wat terug moet komen, en altijd een plek voor iets nieuws:
  // anders zou een slechte week je nooit meer iets nieuws laten zien
  var uit = fout.concat(due).slice(0, 2).map(function(x){ return x.c; });
  if(nieuw.length) uit.push(nieuw[0]);
  if(!uit.length) uit = GC_CONCEPTEN.slice(0, 3);
  return uit;
}'''

A_VERS = '''function gramVersKandidaat(les){
  var tk = (typeof gwTrackKey === "function") ? gwTrackKey() : "a2";
  var idxs = (les && les.spiek) || [], uit = null;
  GC_CONCEPTEN.forEach(function(c){
    if(uit) return;
    if(gramAangeraakt(c.id)) return;
    var lijst = (c.spiek && c.spiek[tk]) || [];
    for(var i = 0; i < idxs.length; i++){ if(lijst.indexOf(idxs[i]) !== -1){ uit = c; return; } }
  });
  return uit;
}'''

A_GRAMID = '''  var vers = gramVersKandidaat(les);
  if(vers) return "concept-" + vers.id;

  var kandidaten = [];'''

A_FALLBACK = '''  if(!kandidaten.length) kandidaten = GRAMWIZ.concat(gcLijst()).concat(gwGenLijst());'''

A_CL = '''function clConcepten(){
  return GC_CONCEPTEN.filter(function(c){'''

A_GEN = '''  var out = [];
  CHEATSHEET.forEach(function(c, i){
    if(bezet[i]) return;
    var o = gwVanSpiek(i);
    if(o) out.push(o);
  });
  return out;
}'''

A_WIZLIJST = '''    "<p style='margin:14px 0 4px'><b>" + ct("De diepe lessen", "The deep dives") + "</b> <span class='muted'>\\u00b7 " + ct("meer stappen, meer valkuilen, apart geschreven", "more steps, more pitfalls, written by hand") + "</span></p>" +
    GRAMWIZ.map(gwKaartHtml).join("") +'''

A_KAARTJES = '''function gcVandaagKaartjes(con){
  var kies = {};
  gcVandaagLijst().forEach(function(c){ kies["concept-" + c.id] = 1; });
  return con.filter(function(o){ return kies[o.id]; }).map(gcKaartHtml).join("");
}'''

A_TOGGLE = '''            "<button type='button' class='ghost' id='gcToggleAlles' style='margin-top:8px; font-size:.85rem'>" +
              ct("Alle " + con.length + " onderwerpen \\u2192", "All " + con.length + " topics \\u2192") + "</button>")
      : "") +'''

if DOE_APP:
    ANKERS = ['var APP_VERSIE = "v23.52";', A_GCCONCEPT, A_GCLIJST, A_VANDAAG, A_VERS,
              A_GRAMID, A_FALLBACK, A_CL, A_GEN, A_KAARTJES, A_WIZLIJST, A_TOGGLE]
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:90].replace("\n", " / ") for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.52. Eerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.52";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 1. de volgorde zelf ----------
    rep(A_GCCONCEPT, r'''/* ================= DE VOLGORDE VAN DE GRAMMATICA (v23.53) =================

   Stefan, telefoontest 11 aug: "de grammatica cual of que is veel te moeilijk. Je moet met de
   makkelijkste als begonnen, dat is denk ik el of la" en "wat fout is dat ik alles kan doen, dus
   dingen die nog ver boven mijn niveau liggen".

   Tot hier had de app geen enkel idee welk grammaticaonderwerp makkelijk is. Waar er toch gekozen
   moest worden, koos hij op de volgorde van het array of op wat er toevallig in de spiekbrief van je
   les stond. Gemeten op een vers A0-profiel: vijftig onderwerpen open, en de grammatica-stap van je
   eerste dagles was concept-quecual.

   Ik heb eerst geprobeerd de volgorde uit de curriculumdata af te leiden (elke les verwijst naar
   spiekbriefkaarten, elk concept hangt aan zo'n kaart). Die afgeleide volgorde zet quecual op
   nummer 1 en genero op nummer 3, en elf concepten hangen aan geen enkele les. De lessenreeks is
   geschreven om woorden te ordenen, niet om grammatica te ordenen.

   Dus staat het hier met de hand. Dat is een oordeel, en dat hoort het te zijn: welk onderwerp
   makkelijk is, is didactiek en geen meetwaarde. Maar de vorm is wel controleerbaar, en dat doet
   test/suites/pw-gramorde.js: elk concept staat er precies een keer in, elke voorwaarde bestaat en
   staat eerder in de rij, en op dag 1 staat er iets open. */
var GC_ORDE = [
  "genero",          // el of la: het eerste dat je bij elk zelfstandig naamwoord moet weten
  "concordancia",    // en dan buigt de rest mee
  "serestar",        // ser of estar: de kern van A1
  "hayestar",        // hay of esta, een aftakking van estar
  "negacion",        // no ... nada: een regel, geen keuze
  "muymucho",        // muy of mucho: kijk naar het woord erachter
  "tuusted",         // tu of usted
  "futuroir",        // ir a + infinitief, je eerste toekomst
  "gustar",          // gusta of gustan
  "demostrativo",    // este, ese, aquel
  "zapato",          // wisselt de klinker mee
  "reflexivo",       // me, te, se
  "comparar",        // mas que, tan como
  "gerundio",        // presente of estar + gerundio
  "apersonal",       // de persoonlijke a
  "saberconocer",    // saber of conocer
  "quecual",         // que of cual: hier zat Stefan, en hier hoort het pas
  "saberpoder",      // saber of poder
  "pedirpreguntar",  // pedir of preguntar
  "pronombre",       // lo, la, le
  "porpara",         // por of para
  "perfindef",       // perfecto of indefinido
  "indefimperf"      // indefinido of imperfecto
];
/* Hoogstens twee voorgangers per onderwerp, en alleen waar het onvermijdelijk is. Een lange lijst
   voorwaarden zou een boom worden die niemand meer kan nalopen; dit zijn er vijf plus een wizard. */
var GC_VOOR = {
  concordancia: ["genero"],      // meebuigen kan niet zonder el/la
  demostrativo: ["genero"],      // este/esta is hetzelfde probleem
  hayestar:     ["serestar"],    // hay tegenover esta gaat over estar
  pronombre:    ["apersonal"],   // lo/la/le vervangt precies wat de persoonlijke a markeert
  indefimperf:  ["perfindef"],   // twee verledens vergelijken kan pas als je er een kent
  subjuntivo:   ["indefimperf"]  // de handgeschreven diepe les
};
/* Hoeveel nieuwe onderwerpen er tegelijk open staan. Drie: genoeg om te kiezen, weinig genoeg om
   niet weer een menu van vijftig te zijn. Alles wat je ooit hebt aangeraakt blijft daarnaast open,
   want wat je fout deed moet terug kunnen komen. */
var GC_VENSTER = 3;

function gcRang(id){
  var i = GC_ORDE.indexOf(String(id || "").replace(/^concept-/, ""));
  return i === -1 ? 999 : i;
}
function gcGeordend(){
  return GC_CONCEPTEN.slice().sort(function(a, b){ return gcRang(a.id) - gcRang(b.id); });
}
// "goed gedaan" en niet "aangeraakt": een voorwaarde die je vier keer fout deed is geen voorwaarde
// waar je op mag bouwen. Blijft hij hangen, dan haalt gramFoutTop() hem vanzelf terug.
function gcGedaan(id){
  try { return (gramLees(String(id).replace(/^concept-/, "")).goed || 0) > 0; } catch(e){ return false; }
}
function gcVoorOk(id){
  var v = GC_VOOR[String(id || "").replace(/^concept-/, "")] || [];
  for(var i = 0; i < v.length; i++){ if(!gcGedaan(v[i])) return false; }
  return true;
}
function gcOpenSet(){
  var open = {}, nieuw = 0;
  GC_ORDE.forEach(function(id){
    var st = {};
    try { st = gramLees(id) || {}; } catch(e){ st = {}; }
    if(((st.goed || 0) + (st.fout || 0)) > 0){ open[id] = 1; return; }
    if(nieuw >= GC_VENSTER) return;
    // een onderwerp dat op zijn voorganger wacht slaat zijn beurt over en verbruikt geen plek:
    // anders zou het venster op dag 1 half leeg staan (concordancia en hayestar wachten allebei)
    if(!gcVoorOk(id)) return;
    open[id] = 1; nieuw++;
  });
  return open;
}
function gcConceptOpen(id){
  id = String(id || "").replace(/^concept-/, "");
  if(GC_ORDE.indexOf(id) === -1) return gcVoorOk(id);   // handgeschreven wizard zonder concept
  return !!gcOpenSet()[id];
}
// Het eerste open onderwerp dat je nog nooit hebt gedaan: waar de dagles op terugvalt.
function gcVolgendeOpen(){
  var open = gcOpenSet(), uit = null;
  GC_ORDE.forEach(function(id){
    if(uit || !open[id]) return;
    var st = {};
    try { st = gramLees(id) || {}; } catch(e){ st = {}; }
    if(((st.goed || 0) + (st.fout || 0)) > 0) return;
    uit = id;
  });
  return uit;
}
function gcDichtAantal(){
  var open = gcOpenSet(), n = 0;
  GC_ORDE.forEach(function(id){ if(!open[id]) n++; });
  return n;
}
function gcConcept(id){''')

    # ---------- 2. de lijst op de Grammatica-tab ----------
    rep(A_GCLIJST, '''function gcLijst(){
  /* v23.53: dit gaf alle drieentwintig concepten in arrayvolgorde. Nu in leervolgorde, en alleen
     wat open staat. Stefan: "wat fout is dat ik alles kan doen." */
  return gcGeordend().filter(function(c){ return gcConceptOpen(c.id); })
    .map(function(c){ return gcOnderwerp("concept-" + c.id); }).filter(Boolean);
}''')

    # ---------- 3. wat er vandaag telt ----------
    rep(A_VANDAAG, '''function gcVandaagLijst(){
  /* v23.53: dit liep over GC_CONCEPTEN in arrayvolgorde, en "iets nieuws" was daarmee het eerste
     onderwerp in het bestand (muymucho). Nu de leervolgorde, en alleen wat open staat. Wat je al
     hebt aangeraakt telt altijd mee, ook als het inmiddels buiten het venster valt: fouten moeten
     terug kunnen komen. */
  var t = today(), fout = [], due = [], nieuw = [], open = gcOpenSet();
  gcGeordend().forEach(function(c){
    var st = gramLees(c.id);
    if(!st.goed && !st.fout){ if(open[c.id]) nieuw.push(c); return; }
    if(st.fout && (st.box || 0) === 0){ fout.push({c:c, st:st}); return; }
    if(!st.due || st.due <= t) due.push({c:c, st:st});
  });
  function opBox(a, b){ return (a.st.box || 0) - (b.st.box || 0); }
  fout.sort(opBox); due.sort(opBox);
  // twee plekken voor wat terug moet komen, en altijd een plek voor iets nieuws:
  // anders zou een slechte week je nooit meer iets nieuws laten zien
  var uit = fout.concat(due).slice(0, 2).map(function(x){ return x.c; });
  if(nieuw.length) uit.push(nieuw[0]);
  if(!uit.length) uit = gcGeordend().filter(function(c){ return open[c.id]; }).slice(0, 3);
  return uit;
}''')

    # ---------- 4. het verse concept uit je les ----------
    rep(A_VERS, '''function gramVersKandidaat(les){
  var tk = (typeof gwTrackKey === "function") ? gwTrackKey() : "a2";
  var idxs = (les && les.spiek) || [], uit = null;
  /* v23.53: hier kwam concept-quecual vandaan op dag 1. Les 1 verwijst naar spiekbriefkaart 4, en
     daar hangt que-of-cual aan. De les koos dus een grammaticaonderwerp waar hij nooit voor
     geschreven is. De volgorde van GC_ORDE gaat hier voor: een kaart mag een onderwerp naar voren
     halen, maar geen onderwerp openen dat nog dicht staat. */
  gcGeordend().forEach(function(c){
    if(uit) return;
    if(gramAangeraakt(c.id)) return;
    if(!gcConceptOpen(c.id)) return;
    var lijst = (c.spiek && c.spiek[tk]) || [];
    for(var i = 0; i < idxs.length; i++){ if(lijst.indexOf(idxs[i]) !== -1){ uit = c; return; } }
  });
  return uit;
}''')

    # ---------- 5. de dagles valt terug op het eerste open onderwerp ----------
    rep(A_GRAMID, '''  var vers = gramVersKandidaat(les);
  if(vers) return "concept-" + vers.id;

  /* v23.53: deze stap is er bij gekomen. Als de spiekbrief van je les niets oplevert dat open
     staat, pak dan gewoon het eerste onderwerp uit de leervolgorde dat je nog nooit hebt gedaan.
     Zonder deze stap viel de dagles terug op de kandidatenlijst hieronder, en die begint met de
     handgeschreven wizards: op dag 1 kreeg je dan klemtoon in plaats van el of la. */
  var volgende = gcVolgendeOpen();
  if(volgende) return "concept-" + volgende;

  var kandidaten = [];''')

    rep(A_FALLBACK, '''  /* v23.53: GRAMWIZ ging hier ongefilterd in. Subjuntivo is een van de vijf, en die hoort niet in
     de dagles van iemand die drie woorden kent. Wizards zonder eigen concept (klemtoon) hebben geen
     voorwaarde en blijven dus gewoon open. */
  if(!kandidaten.length) kandidaten = GRAMWIZ.filter(function(o){ return gcConceptOpen(o.id); })
    .concat(gcLijst()).concat(gwGenLijst());''')

    # ---------- 6. Chispa's Clasificador ----------
    rep(A_CL, '''function clConcepten(){
  /* v23.53: het sorteerspel bood op dag 1 ook porpara en perfindef aan. Snel kiezen tussen twee
     bakken heeft alleen zin als je de regel kent; anders is het gokken op tijd. */
  return gcGeordend().filter(function(c){ return gcConceptOpen(c.id); }).filter(function(c){''')

    # ---------- 7. de gegenereerde onderwerpen volgen je lespositie ----------
    rep(A_GEN, '''  /* v23.53: hier gingen alle drieentwintig spiekbriefkaarten van je track in, ongeacht waar je in
     de lessenreeks staat. Elke kaart wordt door minstens een les genoemd (nagemeten: 23 van de 23),
     dus die lespositie is er gewoon en hoeft niet verzonnen te worden. Een onderwerp verschijnt als
     de les die ernaar verwijst is aangebroken. */
  var out = [], grens = gwLesIndex(), lessen = [];
  try { lessen = tLessons() || []; } catch(e){ lessen = []; }
  function kaartOpen(i){
    for(var k = 0; k < lessen.length; k++){
      if(((lessen[k] && lessen[k].spiek) || []).indexOf(i) !== -1) return k <= grens;
    }
    return true;   // geen enkele les noemt hem: niet verstoppen, want dan komt hij nooit
  }
  CHEATSHEET.forEach(function(c, i){
    if(bezet[i]) return;
    if(!kaartOpen(i)) return;
    var o = gwVanSpiek(i);
    if(o) out.push(o);
  });
  return out;
}
// Waar sta je in de lessenreeks? huidigeLes() geeft het lesobject, hier is de plek in de rij nodig.
function gwLesIndex(){
  try {
    var ls = tLessons() || [], les = huidigeLes();
    if(!les) return 0;
    for(var i = 0; i < ls.length; i++){ if(ls[i].id === les.id) return i; }
  } catch(e){}
  return 0;
}''')

    # ---------- 7b. de kaartjes staan in de volgorde van gcVandaagLijst ----------
    rep(A_KAARTJES, '''function gcVandaagKaartjes(con){
  /* v23.53: dit filterde con (de volledige lijst) op wat vandaag telt, en gaf dus de volgorde van
     die lijst terug in plaats van de volgorde van gcVandaagLijst(). Zolang GC_CONCEPTEN toevallig
     op arrayvolgorde stond viel dat niet op; met GC_ORDE ervoor kwam het nieuwe onderwerp boven de
     fout van gisteren te staan. De volgorde van gcVandaagLijst is niet willekeurig: eerst wat fout
     ging, dan wat terugkomt, dan iets nieuws. */
  var index = {};
  con.forEach(function(o){ index[o.id] = o; });
  return gcVandaagLijst().map(function(c){ return index["concept-" + c.id]; })
    .filter(Boolean).map(gcKaartHtml).join("");
}''')

    # ---------- 8. de diepe lessen volgen dezelfde poort ----------
    rep(A_WIZLIJST, '''    /* v23.53: hier stonden alle vijf de diepe lessen onvoorwaardelijk, subjuntivo incluis. Ze volgen
       nu dezelfde poort als de concepten: perfindef, serestar en porpara via hun eigen concept,
       subjuntivo via GC_VOOR, en klemtoon heeft geen voorwaarde en staat dus altijd open. */
    (function(){
      var wz = GRAMWIZ.filter(function(o){ return gcConceptOpen(o.id); });
      return wz.length ? "<p style='margin:14px 0 4px'><b>" + ct("De diepe lessen", "The deep dives") + "</b> <span class='muted'>\\u00b7 " + ct("meer stappen, meer valkuilen, apart geschreven", "more steps, more pitfalls, written by hand") + "</span></p>" + wz.map(gwKaartHtml).join("") : "";
    })() +''')

    # ---------- 9. zeggen dat je verstopt ----------
    rep(A_TOGGLE, '''            "<button type='button' class='ghost' id='gcToggleAlles' style='margin-top:8px; font-size:.85rem'>" +
              ct("Alle " + con.length + " onderwerpen \\u2192", "All " + con.length + " topics \\u2192") + "</button>")
      : "") +
    /* v23.53: verstoppen zonder te zeggen dat je verstopt is precies de fout die de onboarding in
       v23.45 maakte. Het aantal blijft dus zichtbaar. */
    (gcDichtAantal()
      ? "<p class='muted' style='margin:8px 0 0; font-size:.8rem'>" +
        ct("Nog " + gcDichtAantal() + " onderwerpen komen later, als je verder bent.",
           gcDichtAantal() + " more topics unlock as you get further.") + "</p>"
      : "") +''')

    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
