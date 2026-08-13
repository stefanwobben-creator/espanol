#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.73: grammatica krijgt een leermachine in plaats van een rondleiding.

Stefan, 13 aug: "dan wil ik graag dat je nog een keer naar alle grammatica kijkt, dat moet
conceptueel echter beter."

## Wat er gemeten is

Dertig dagen gesimuleerd op een vers profiel, elke dag het grammaticapunt van de dagles, alles goed
beantwoord:

    dag  1 genero · dag 2 concordancia · ... · dag 23 indefimperf
    dag 24 t/m 30: spiek-a0-0, zeven dagen achter elkaar dezelfde uitspraakkaart

Drieentwintig concepten, elk precies één keer, en daarna niets meer. **Geen enkel concept komt ooit
terug.** `gramBij()` schrijft trouw een doosje en een vervaldatum, en `gramDueTop()` staat klaar om
te vertellen wat er vandaag op herhaling staat — maar die functie wordt nergens aangeroepen. Dode
code. Alleen fouten kwamen terug, via `gramFoutTop()`.

Voor woorden is er een leermachine; voor grammatica was het een rondleiding.

## En een tweede bug, zichtbaar zodra je fouten meesimuleert

Met een foutkans van 25% bleef hetzelfde onderwerp negen dagen achter elkaar staan
(`pedirpreguntar` op dag 26 t/m 34). Oorzaak: `gramFoutTop()` selecteert op `st.fout > 0`, en die
teller wordt nooit gewist. Eén fout betekende dus voor altijd in de foutenpot zitten, en omdat die
pot op laagste doosje sorteert wint de laatste misser telkens opnieuw.

## Wat er nu is: één wachtrij

De foutenpot is weg. `gramBij()` gaf een fout al "morgen" mee en een goed antwoord een langere
adem, dus een wachtrij op vervaldatum zet fouten vanzelf vooraan. Eén lijst in plaats van twee, en
`gramDueTop()` doet eindelijk waar hij voor geschreven is.

    gramWachtrij()   alles wat je ooit aanraakte, dat open staat en waarvan de datum is verstreken,
                     laagste doosje eerst, en bij gelijke stand wie het langst wacht

## En waarom dat alleen niet genoeg was

De eerste versie hiervan liet de wachtrij vóór het nieuwe onderwerp gaan. Gesimuleerd over 60 dagen:
**acht verschillende onderwerpen in twee maanden**, en de andere vijftien nooit gezien. Op de lage
doosjes (1 en 3 dagen) staat er altijd wel iets open, dus kennismaking kwam nooit meer aan de beurt.

Dat is dezelfde spanning die de woordenkant al opgelost heeft: woorden krijgen een **portie** met
herhalingen én nieuwe, grammatica had één plek per dag. Elke volgorde in één plek is een nulsomspel
tussen leren en onthouden.

Dus krijgt grammatica ook een portie, maar een goedkope:

    opfrissen      één vraag, geen uitleg, geen stappen. Tien seconden.
    kennismaken    de microles van drie stappen, zoals hij was.

Staat er iets op herhaling, dan begint de grammaticastap met één opfrisvraag en gaat daarna door
naar het nieuwe onderwerp. Goed: het doosje schuift op. Fout: het concept staat morgen weer vooraan,
en dan als hele microles, want dan is er meer aan de hand dan een geheugenkwestie.

De dag wordt daarmee één vraag langer, niet één les.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.73"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function gramWachtrij" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_FOUTTOP = '''/* Het concept waar je op struikelde en dat vandaag mag terugkomen. Laagste doosje eerst, en bij
   gelijke stand de verste fout eerst, want die is het langst blijven liggen. */
function gramFoutTop(){
  var t = today(), uit = [];
  GC_CONCEPTEN.forEach(function(c){
    var st = gramLees(c.id);
    if(!st.fout) return;
    // Een fout staat op doosje nul tot je hem een keer goed hebt gedaan. Zolang dat niet gebeurd is,
    // telt de wachttijd niet: hij mag vandaag nog terugkomen. Anders zou de fout die je net maakte
    // pas morgen aan bod komen, en dat is precies de dag dat je hem al vergeten bent.
    if((st.box || 0) > 0 && st.due && st.due > t) return;
    uit.push({c:c, st:st});
  });
  if(!uit.length) return null;
  uit.sort(function(a, b){
    if((a.st.box || 0) !== (b.st.box || 0)) return (a.st.box || 0) - (b.st.box || 0);
    return (a.st.laatst || "") < (b.st.laatst || "") ? -1 : 1;
  });
  return uit[0];
}'''

A_DUETOP = '''/* Elk concept dat vandaag op herhaling staat, ongeacht of het ooit fout ging. */
function gramDueTop(){
  var t = today(), uit = [];
  GC_CONCEPTEN.forEach(function(c){
    var st = gramLees(c.id);
    if(st.due && st.due > t) return;
    uit.push({c:c, st:st});
  });
  uit.sort(function(a, b){ return (a.st.box || 0) - (b.st.box || 0); });
  return uit.length ? uit[0] : null;
}'''

A_GRAMID = '''  // v20.5, in deze volgorde. Stefan: "alle fouten die maak moeten weer terug, mijn leermachine is".
  // Dus eerst het concept waar je op struikelde en dat vandaag mag terugkomen. Dat is de enige
  // reden waarom de les van vandaag anders is dan die van gisteren.
  var fout = gramFoutTop();
  if(fout) return "concept-" + fout.c.id;

  // Daarna een concept uit de les van vandaag dat je hier nog nooit hebt gedaan. Nieuw voor je,
  // en het hoort bij de woorden die je net hebt geleerd.
  var vers = gramVersKandidaat(les);
  if(vers) return "concept-" + vers.id;'''

A_ONDERWERP = '''function gwOnderwerp(id){
  // handgeschreven wizards eerst, daarna de automatisch opgeknipte spiekbrief-onderwerpen
  var hand = GRAMWIZ.filter(function(o){ return o.id === id; })[0];
  if(hand) return hand;
  if(/^concept-/.test(id || "")) return gcOnderwerp(id);'''

A_FLOWSTAP = '''  if(lesFlow.stap === "woorden"){
    // v19.47 (Stefan: "en ik de daglessen terug laten komen"): na de woordjes een uitleg-stap over
    // het grammatica-onderwerp van je huidige les, in dezelfde opgeknipte vorm als de wizards.
    lesFlow.stap = "grammatica";
    var gid = lesFlowGramId();
    if(gid){
      lesFlow.gramId = gid;
      show("spiekbrief");
      gwStart(gid);
      return;
    }
  }
  if(lesFlow.stap === "grammatica"){'''

if DOE_APP:
    ontbreekt = [a for a in [A_FOUTTOP, A_DUETOP, A_GRAMID, A_ONDERWERP, A_FLOWSTAP] if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
              "\n\nEerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. één wachtrij in plaats van een foutenpot naast een lijst ----------
    rep(A_FOUTTOP, '''/* ================= ÉÉN WACHTRIJ VOOR GRAMMATICA (v23.73) =================
   Hier stonden twee lijsten naast elkaar: een foutenpot (gramFoutTop) en een herhaallijst
   (gramDueTop). De eerste bepaalde alles, de tweede werd nergens aangeroepen.

   Twee dingen gemeten die daaruit volgden. Dertig dagen gesimuleerd met alles goed: elk van de
   drieentwintig concepten precies één keer, daarna zeven dagen dezelfde uitspraakkaart. Geen enkel
   concept kwam ooit terug, want de vervaldatum die gramBij() netjes schreef werd door niemand
   gelezen. En met een foutkans van 25%: negen dagen achter elkaar hetzelfde onderwerp, omdat
   st.fout nooit gewist wordt en de foutenpot dus levenslang is.

   De pot is weg. gramBij() geeft een fout al "morgen" mee en een goed antwoord een langere adem,
   dus een wachtrij op vervaldatum zet fouten vanzelf vooraan. De tellers st.goed en st.fout blijven
   bestaan voor de cijfers op je profiel; ze sturen alleen niets meer aan. */
function gramWachtrij(){
  var t = today(), uit = [];
  GC_CONCEPTEN.forEach(function(c){
    if(!gramAangeraakt(c.id)) return;          // nooit gedaan is geen herhaling maar kennismaking
    try { if(!gcConceptOpen(c.id)) return; } catch(e){}
    var st = gramLees(c.id);
    /* Een openstaande fout (doosje nul) wacht niet op zijn datum. Dat stond al zo in de oude
       foutenpot en de reden klopt nog steeds: anders komt de fout die je net maakte pas morgen aan
       bod, en dat is precies de dag dat je hem al vergeten bent. Het verschil met vroeger is dat
       één goed antwoord het doosje op één zet en de rekening daarmee sluit; vroeger bleef st.fout
       staan en bleef het onderwerp levenslang vooraan. */
    var open = (st.box || 0) === 0 && (st.fout || 0) > 0;
    if(!open && st.due && st.due > t) return;
    uit.push({c:c, st:st});
  });
  uit.sort(function(a, b){
    if((a.st.box || 0) !== (b.st.box || 0)) return (a.st.box || 0) - (b.st.box || 0);
    return (a.st.due || "") < (b.st.due || "") ? -1 : 1;
  });
  return uit;
}
/* Twee functies, twee vragen, en dat onderscheid was er niet.

   gramWachtrij() beantwoordt "wat staat er vandaag op herhaling" en stuurt het dagritme. Die kijkt
   naar de vervaldatum, want dat is wat een doosje betekent.

   gramFoutTop() beantwoordt "waar ben je zojuist op gestruikeld" en voedt het eindscherm ("Nog een
   keer: ser of estar") en de regel dat twee missers de hele microles terugbrengen. Die mag juist
   níét op de datum wachten: het moment om het nog eens aan te bieden is meteen erna, niet morgen.
   Een concept met doosje nul en minstens één fout is een openstaande rekening. */
function gramFoutTop(){
  var uit = [];
  GC_CONCEPTEN.forEach(function(c){
    var st = gramLees(c.id);
    if(!st.fout) return;
    if((st.box || 0) > 0) return;           // je had hem daarna weer goed: geen openstaande rekening
    uit.push({c:c, st:st});
  });
  if(!uit.length) return null;
  uit.sort(function(a, b){ return (a.st.laatst || "") < (b.st.laatst || "") ? 1 : -1; });
  return uit[0];
}''')

    rep(A_DUETOP, '''/* v23.73: leest uit de wachtrij, zodat er één plek is waar de volgorde bepaald wordt. */
function gramDueTop(){
  var rij = gramWachtrij();
  return rij.length ? rij[0] : null;
}
/* ---- de opfrisser: herhalen mag geen les zijn ----
   De eerste versie van v23.73 zette de wachtrij vóór het nieuwe onderwerp. Gesimuleerd over zestig
   dagen: acht verschillende onderwerpen in twee maanden, de andere vijftien nooit gezien. Op de
   lage doosjes (1 en 3 dagen) staat er altijd wel iets open, dus kennismaken kwam nooit meer aan
   de beurt.

   Dat is dezelfde spanning die de woordenkant allang heeft opgelost: woorden krijgen een portie met
   herhalingen én nieuwe, grammatica had één plek per dag. Elke volgorde binnen één plek is een
   nulsomspel tussen leren en onthouden.

   Dus: herhalen kost één vraag en geen les. Staat er iets op herhaling, dan begint de
   grammaticastap daarmee en gaat daarna door naar het nieuwe onderwerp. Fout? Dan staat het concept
   morgen vooraan in de wachtrij, en dan wél als hele microles: twee keer mis is geen geheugenkwestie
   meer. */
function gcOpfrisId(cid){ return "opfris-" + String(cid || "").replace(/^concept-/, ""); }
function gcOpfrisOnderwerp(id){
  var cid = String(id || "").replace(/^opfris-/, "");
  var c = gcConcept(cid);
  if(!c) return null;
  var vragen = [];
  try { vragen = gcMaakVragen(c, 1); } catch(e){ vragen = []; }
  if(!vragen.length) return null;
  var naam = ct(c.naam, c.naamEn || c.naam);
  return {
    id: id, concept: cid, opfris: true,
    titel: ct("Even opfrissen: " + naam, "Quick refresher: " + naam),
    titelEn: "Quick refresher: " + (c.naamEn || c.naam),
    pitch: ct("Eén vraag. Je had dit al een keer goed.", "One question. You had this right before."),
    pitchEn: "One question. You had this right before.",
    stappen: [{ kop: ct("Even opfrissen", "Quick refresher"),
                kopEn: "Quick refresher",
                uitleg: "", uitlegEn: "",
                vragen: vragen }]
  };
}''')

    # ---------- 2. de dagles: eerst opfrissen, dan kennismaken ----------
    rep(A_GRAMID, '''  /* v23.73: de foutenpot is weg. Wat er op herhaling staat komt terug als opfrisvraag (zie
     lesFlowGramLijst), en deze functie kiest alleen nog wat je erná leert. Wie twee keer op
     hetzelfde struikelt krijgt wel de hele microles: dan is het geen geheugenkwestie meer. */
  var fout = gramFoutTop();
  if(fout && (fout.st.box || 0) === 0 && (fout.st.fout || 0) >= 2) return "concept-" + fout.c.id;

  // Daarna een concept uit de les van vandaag dat je hier nog nooit hebt gedaan. Nieuw voor je,
  // en het hoort bij de woorden die je net hebt geleerd.
  var vers = gramVersKandidaat(les);
  if(vers) return "concept-" + vers.id;''')

    rep(A_ONDERWERP, '''function gwOnderwerp(id){
  // handgeschreven wizards eerst, daarna de automatisch opgeknipte spiekbrief-onderwerpen
  var hand = GRAMWIZ.filter(function(o){ return o.id === id; })[0];
  if(hand) return hand;
  // v23.73: de opfrisser is een onderwerp van één stap met één vraag en geen uitleg.
  if(/^opfris-/.test(id || "")) return gcOpfrisOnderwerp(id);
  if(/^concept-/.test(id || "")) return gcOnderwerp(id);''')

    rep(A_FLOWSTAP, '''  if(lesFlow.stap === "woorden"){
    // v19.47 (Stefan: "en ik de daglessen terug laten komen"): na de woordjes een uitleg-stap over
    // het grammatica-onderwerp van je huidige les, in dezelfde opgeknipte vorm als de wizards.
    lesFlow.stap = "grammatica";
    /* v23.73: de grammaticastap is een lijstje geworden in plaats van één ding. Eerst hoogstens één
       opfrisvraag over wat vandaag op herhaling staat, dan het nieuwe onderwerp. Twee items, samen
       korter dan de ene les die er stond, want een opfrisser is één vraag. */
    lesFlow.gramLijst = lesFlowGramLijst();
    lesFlow.gramId = lesFlow.gramLijst[0] || null;
    if(lesFlow.gramId){
      show("spiekbrief");
      gwStart(lesFlow.gramId);
      return;
    }
  }
  if(lesFlow.stap === "grammatica"){
    /* v23.73: staat er nog een tweede grammatica-item klaar (de opfrisser was de eerste), dan gaat
       de stap door in plaats van af. */
    if(lesFlow.gramLijst && lesFlow.gramLijst.length > 1){
      lesFlow.gramLijst = lesFlow.gramLijst.slice(1);
      lesFlow.gramId = lesFlow.gramLijst[0];
      show("spiekbrief");
      gwStart(lesFlow.gramId);
      lesFlowBewaar();
      return;
    }''')

    rep('''function lesFlowGramId(){''', '''/* v23.73: wat de grammaticastap vandaag doet, op volgorde. Hoogstens twee dingen: één opfrisvraag
   en één onderwerp. De opfrisser valt weg als er niets op herhaling staat, het onderwerp als je
   alles al hebt gezien; blijft er niets over, dan slaat de stap zichzelf over zoals altijd. */
function lesFlowGramLijst(){
  var uit = [];
  var rij = [];
  try { rij = gramWachtrij(); } catch(e){ rij = []; }
  if(rij.length){
    var top = rij[0];
    /* Twee keer mis op hetzelfde is geen geheugenkwestie: dan geen opfrisvraag maar de hele
       microles, en die komt uit lesFlowGramId() hieronder. */
    if(!((top.st.box || 0) === 0 && (top.st.fout || 0) >= 2)){
      var o = null;
      try { o = gcOpfrisOnderwerp(gcOpfrisId(top.c.id)); } catch(e){ o = null; }
      if(o) uit.push(o.id);
    }
  }
  var gid = null;
  try { gid = lesFlowGramId(); } catch(e){ gid = null; }
  if(gid && uit.indexOf(gid) === -1) uit.push(gid);
  return uit;
}
function lesFlowGramId(){''')

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
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
