#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.135: je ziet je les voordat je hem doet.

Stefan, 19 aug: "daarbij zie ik vooraf wat de hele dagles is met min per onderdeel."

## Wat er stond

Op Vandaag stond één regel: "18 woordjes (5 nieuw) · daarna kort: grammatica, een toetsje en
oefenen · ongeveer 9 min". Dat is een samenvatting van drie kwart van je les in zeven woorden,
zonder aantallen en zonder verdeling. En die "ongeveer 9 min" werd gerekend als
`portie.totaal + toetsvragenPerDag() + 8`, waarbij die 8 een hardgecodeerde handvol beurten was voor
grammatica plus oefenen samen.

Erger: de stappen van de dagles bestonden helemaal niet als data. Ze waren een keten van
if-blokken in lesFlowVolgendeKern(), en vier plekken schreven onafhankelijk van elkaar op dat het er
vier waren (lesFlowStapNaam, lesFlowStapNum, de banner "/4", en ritmeCard twee keer). Een stap
toevoegen of overslaan betekende dus vier plekken die uit elkaar konden lopen, en dat is precies wat
er gebeurt als er geen toetsje meer over is: dan doe je drie stappen en zegt het scherm nog steeds
"stap 3/4".

## Wat er nu staat

`dagPlan()` beschrijft de les van vandaag als data: per blok een naam, wat er in zit, hoeveel
beurten dat zijn en hoeveel minuten dat kost. Op het dagscherm staat dat als lijstje, vóór de
startknop:

    Je les vandaag · ongeveer 11 min, gerekend met jouw tempo
    1  Woordjes      18 kaartjes (5 nieuw)   4 min
    2  Grammatica    2 onderwerpen           2 min
    3  Toetsje       6 vragen                2 min
    4  Schrijven     3 zinnen                2 min

Alles daarin komt uit de functies die de les ook echt draaien: `dagPortie()`, `lesFlowGramLijst()`,
`lesFlowQuizId()`, `toetsvragenPerDag()` en `SCHRIJF_PER_LES`. Is er geen toetsje meer over, dan
staat het blok er niet, en dan is de les ook echt drie stappen lang.

De minuten komen uit je eigen gemeten seconden per antwoord (`tijdVenster(7).perPoging`, vanaf 30
pogingen). Zolang die er niet zijn wordt er met twaalf seconden gerekend, en dan zegt de kop
"geschat" in plaats van "gerekend met jouw tempo". Schrijven telt met vijfentwintig seconden per
zin, het getal waar `lesFlowOpenProductie()` zelf al mee rekende.

## En "/4" is nu afgeleid

`lesFlowStapNum()` zoekt de stap op in de stappenlijst in plaats van vier nummers uit te schrijven,
en de banner en het dagscherm vragen het totaal op in plaats van "4" te typen. De lijst reist mee in
`lesFlow.stappen` en wordt bewaard in `S.lesFlowNu`, zodat "verder waar je was" hetzelfde totaal
laat zien als waar je aan begon. Een les die als vier stappen begon, blijft vier stappen, ook als er
halverwege een toetsje bij komt.

Hervat je een les, dan staan de blokken die je gehad hebt afgevinkt en telt de kop alleen nog wat er
over is.

## Niet op dag een

Het plan staat er vanaf dag twee. Op dag een is het dagscherm het eerste wat een vreemde ziet, en
dan is een rooster van vier regels met elf getallen geen hulp maar een drempel. Twee suites bewaakten
dat al en werden hier terecht rood: pw-verbouw eist hoogstens zes getallen op dag een ("het dagscherm
is geen dashboard") en pw-dag1 eist dat grammatica geen kwart van de zin krijgt. Een derde,
pw-v1998, zag de kaart zo lang worden dat de onderste knop onder de navigatiebalk verdween.

Wie hier voor het eerst staat heeft een knop nodig, geen agenda. Vanaf dag twee weet je wat een les
is, en dan is de vraag een andere: waar zeg ik nu ja op. Op dag een staat de oude regel er dus nog:
"5 woordjes (5 nieuw) · daarna kort: grammatica, een toetsje en oefenen".

Bewaakt door test/suites/pw-dagplan.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.135"

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


# ------------- 1. de dagles als data

rep(
    '''function vaardigheidTijd(){
  // een kwart van je dag gaat naar de vaardigheid, verdeeld over de blokken van vandaag
  return (doelMinuten() * 60 * 0.25) / vaardigheidAantal();
}''',
    '''function vaardigheidTijd(){
  // een kwart van je dag gaat naar de vaardigheid, verdeeld over de blokken van vandaag
  return (doelMinuten() * 60 * 0.25) / vaardigheidAantal();
}

/* ================= DE DAGLES ALS DATA (v23.135) =================

   Stefan, 19 aug: "daarbij zie ik vooraf wat de hele dagles is met min per onderdeel."

   Tot nu toe bestonden de stappen van de dagles nergens als lijst. Ze waren een keten van
   if-blokken in lesFlowVolgendeKern(), en vier plekken schreven onafhankelijk van elkaar op dat het
   er vier waren: lesFlowStapNaam, lesFlowStapNum, de banner ("/4") en ritmeCard (twee keer). Dat is
   niet alleen dubbel, het is ook fout zodra er geen toetsje meer over is: dan doe je drie stappen en
   zegt het scherm "stap 3/4".

   dagPlan() is die lijst. Alles erin komt uit de functies die de les ook echt draaien, dus er kan
   niets in staan wat je daarna niet krijgt. Staat een feit in de data, dan schrijft geen enkele
   codeplek dat feit opnieuw.

   Over de minuten: die komen uit je eigen gemeten seconden per antwoord (tijdVenster, vanaf 30
   pogingen). Zolang die er niet zijn wordt er met DAGBLOK_SEC gerekend en zegt de kop "geschat" in
   plaats van "gerekend met jouw tempo". Dat is de erfenis van v23.17, waar "±5 min" hardgecodeerd
   op het scherm stond ook als je portie drie keer zo groot was: een getal mag hier alleen staan als
   erbij staat waar het vandaan komt. */
var DAGBLOK_SEC = 12;     // seconden per beurt zolang er nog niets gemeten is
var SCHRIJF_SEC = 25;     // per zin; hetzelfde getal waar lesFlowOpenProductie() mee rekent
function dagSecPerBeurt(){
  var tv = null;
  try { tv = tijdVenster(7); } catch(e){ tv = null; }
  return (tv && tv.perPoging) || DAGBLOK_SEC;
}
function dagTempoGemeten(){
  try { return !!tijdVenster(7).perPoging; } catch(e){ return false; }
}
/* Hoeveel vragen de grammaticastap vandaag stelt: de stap waar je staat, niet het hele onderwerp.
   Valt terug op GW_VRAGEN_PER_STAP, het getal waarmee de stappen gebouwd worden. */
function dagGramVragen(id){
  try {
    var o = gwOnderwerp(id), v = gwVoortgang(id);
    var s = o.stappen[Math.min(v.stap, o.stappen.length - 1)];
    return (s && s.vragen && s.vragen.length) || GW_VRAGEN_PER_STAP;
  } catch(e){ return GW_VRAGEN_PER_STAP; }
}
/* Eén keer per dagscherm rekenen. De portie en de wachtrijen veranderen alleen als je iets doet, en
   newToday() telt precies dat; verandert dat getal, dan wordt het plan opnieuw gemaakt. Geen echte
   cachesleutel dus, maar wel de goedkoopste die niet stilstaat terwijl jij bezig bent. */
var _dagPlan = null;
function dagPlanVerval(){ _dagPlan = null; }
function dagPlan(){
  var sleutel = today() + "|" + newToday() + "|" + doelMinuten();
  if(_dagPlan && _dagPlan.sleutel === sleutel) return _dagPlan;
  var sec = dagSecPerBeurt(), blokken = [], portie = null, gram = [], qid = null;
  try { portie = dagPortie(); } catch(e){ portie = null; }
  var nWoord = portie ? (portie.totaal || 0) : 0;
  var nNieuw = portie && portie.nieuw ? portie.nieuw.length : 0;
  if(nWoord){
    blokken.push({stap:"woorden", naam:ct("Woordjes","Words"),
      wat:nWoord + " " + ct("kaartjes","cards") + (nNieuw ? " (" + nNieuw + " " + ct("nieuw","new") + ")" : ""),
      sec:nWoord * sec});
  }
  try { gram = lesFlowGramLijst(); } catch(e){ gram = []; }
  if(gram.length){
    var gBeurten = 0;
    gram.forEach(function(id){ gBeurten += dagGramVragen(id) + 1; });   // +1 voor de uitleg lezen
    blokken.push({stap:"grammatica", naam:ct("Grammatica","Grammar"),
      wat:gram.length + " " + (gram.length === 1 ? ct("onderwerp","topic") : ct("onderwerpen","topics")),
      sec:gBeurten * sec});
  }
  try { qid = lesFlowQuizId(); } catch(e){ qid = null; }
  if(qid){
    var qn = toetsvragenPerDag();
    blokken.push({stap:"toetsjes", naam:ct("Toetsje","Quiz"),
      wat:qn + " " + ct("vragen","questions"), sec:qn * sec});
  }
  var kanSchrijven = false;
  try { kanSchrijven = !!allowedSentIds().length; } catch(e){ kanSchrijven = false; }
  if(kanSchrijven){
    blokken.push({stap:"produceren", naam:ct("Schrijven","Writing"),
      wat:SCHRIJF_PER_LES + " " + ct("zinnen","sentences"), sec:SCHRIJF_PER_LES * SCHRIJF_SEC});
  }
  var tot = 0;
  blokken.forEach(function(b, i){
    b.nr = i + 1;
    b.min = Math.max(1, Math.round(b.sec / 60));
    tot += b.sec;
  });
  _dagPlan = {sleutel:sleutel, blokken:blokken, sec:tot,
              min:Math.max(1, Math.round(tot / 60)), gemeten:dagTempoGemeten(),
              stappen:blokken.map(function(b){ return b.stap; })};
  return _dagPlan;
}
function dagPlanStappen(){ return dagPlan().stappen; }
/* Het lijstje op het dagscherm. Hervat je een les, dan staan de blokken die je gehad hebt afgevinkt
   en telt de kop alleen nog wat er over is: "nog ongeveer 6 min" is het antwoord op de vraag die je
   dan stelt, en "ongeveer 11 min" is dat niet. */
function dagPlanHtml(nu, stappen){
  var p = dagPlan();
  var rij = stappen && stappen.length ? stappen : p.stappen;
  var blokken = p.blokken.filter(function(b){ return rij.indexOf(b.stap) !== -1; });
  if(!blokken.length) return "";
  var iNu = nu ? rij.indexOf(nu) : -1;
  var rest = 0;
  blokken.forEach(function(b){ if(iNu < 0 || rij.indexOf(b.stap) >= iNu) rest += b.sec; });
  var restMin = Math.max(1, Math.round(rest / 60));
  var kop = (iNu > 0 ? ct("Nog ongeveer "+restMin+" min","About "+restMin+" min to go")
                     : ct("Je les vandaag","Your session today")+" · "+
                       ct("ongeveer "+p.min+" min","about "+p.min+" min")) +
            (p.gemeten ? ct(", gerekend met jouw tempo",", based on your own pace")
                       : ct(", geschat",", estimated"));
  var r = "<p class='muted' style='margin:8px 0 2px; font-size:.82rem'><b>"+kop+"</b></p>";
  blokken.forEach(function(b){
    var gehad = iNu > 0 && rij.indexOf(b.stap) < iNu;
    r += "<div style='display:flex; gap:8px; align-items:baseline; font-size:.85rem; padding:1px 0"+
         (gehad ? "; opacity:.5" : "")+"'>"+
      "<span class='muted' style='min-width:1.1em; text-align:right'>"+(gehad ? "\\u2713" : b.nr)+"</span>"+
      "<span style='flex:1'>"+(gehad ? b.naam : "<b>"+b.naam+"</b>")+
        " <span class='muted'>"+b.wat+"</span></span>"+
      "<span class='muted' style='white-space:nowrap'>"+b.min+" min</span></div>";
  });
  return r;
}''',
)

# ------------- 2. het stapnummer is niet meer met de hand geteld

rep(
    '''function lesFlowStapNum(f){
  f = f || lesFlow;
  if(!f) return 0;
  if(f.stap === "woorden") return 1;
  if(f.stap === "grammatica") return 2;
  if(f.stap === "toetsjes") return 3;
  if(f.stap === "produceren") return 4;
  return 0;
}''',
    '''/* v23.135: opzoeken in de stappenlijst in plaats van vier nummers uitschrijven. De lijst reist mee
   in f.stappen (gezet bij de start, bewaard in S.lesFlowNu), zodat een les die als vier stappen
   begon vier stappen blijft. Staat hij er niet, dan is dit een les van vóór deze versie en valt hij
   terug op het plan van vandaag. */
var LESFLOW_VOLGORDE = ["woorden", "grammatica", "toetsjes", "produceren"];
function lesFlowStapRij(f){
  f = f || lesFlow;
  if(f && f.stappen && f.stappen.length) return f.stappen;
  var r = [];
  try { r = dagPlanStappen(); } catch(e){ r = []; }
  return r.length ? r : LESFLOW_VOLGORDE;
}
function lesFlowStapTotaal(f){ return lesFlowStapRij(f).length; }
function lesFlowStapNum(f){
  f = f || lesFlow;
  if(!f || !f.stap) return 0;
  var i = lesFlowStapRij(f).indexOf(f.stap);
  if(i >= 0) return i + 1;
  i = LESFLOW_VOLGORDE.indexOf(f.stap);
  return i >= 0 ? i + 1 : 0;
}''',
)

# ------------- 3. de banner telt zelf niet meer

rep(
    '''        "<span class='kicker'>🚦 "+ct("Start je les","Start your session")+" · "+ct("stap","step")+" "+lesFlowStapNum()+"/4 · "+lesFlowStapNaam()+"</span>"+''',
    '''        "<span class='kicker'>🚦 "+ct("Start je les","Start your session")+" · "+ct("stap","step")+" "+lesFlowStapNum()+"/"+lesFlowStapTotaal()+" · "+lesFlowStapNaam()+"</span>"+''',
)

# ------------- 4. de stappenlijst reist mee met de les

rep(
    '''function lesFlowStart(){
  lesFlow = {stap:null, quizzesTeDoen:[], gekozenSpel:null, vertalenTeGaan:0};
  lesFlowVolgende();
}''',
    '''function lesFlowStart(){
  /* v23.135: het plan waar je ja op zei reist mee. Zonder deze lijst zou "stap 2 van 3" halverwege
     "stap 2 van 4" kunnen worden omdat er ondertussen een toetsje op herhaling kwam te staan, en
     dan verandert de belofte terwijl je hem aan het nakomen bent. */
  var stappen = [];
  try { dagPlanVerval(); stappen = dagPlanStappen().slice(); } catch(e){ stappen = []; }
  lesFlow = {stap:null, quizzesTeDoen:[], gekozenSpel:null, vertalenTeGaan:0, stappen:stappen};
  lesFlowVolgende();
}''',
)

rep(
    '''  S.lesFlowNu = {
    d: today(),
    stap: lesFlow.stap,''',
    '''  S.lesFlowNu = {
    d: today(),
    stap: lesFlow.stap,
    stappen: (lesFlow.stappen || []).slice(),   // v23.135: hetzelfde totaal als waar je aan begon''',
)

rep(
    '''  lesFlow = {
    stap: n.stap,
    gramId: n.gramId || null,''',
    '''  lesFlow = {
    stap: n.stap,
    stappen: (n.stappen || []).slice(),         // v23.135
    gramId: n.gramId || null,''',
)

# ------------- 5. het dagscherm laat de les zien in plaats van hem samen te vatten

rep(
    """  var hStap = hervat ? lesFlowStapNum(S.lesFlowNu) : 0;
  var hNaam = hervat ? lesFlowStapNaam(S.lesFlowNu) : "";""",
    """  var hStap = hervat ? lesFlowStapNum(S.lesFlowNu) : 0;
  var hTot = hervat ? lesFlowStapTotaal(S.lesFlowNu) : 0;   // v23.135: niet meer met de hand "4"
  var hNaam = hervat ? lesFlowStapNaam(S.lesFlowNu) : "";
  /* v23.135: het plan staat er vanaf dag twee, niet op dag een.

     Waarom niet meteen: op dag een is het dagscherm het eerste wat een vreemde ziet, en dan is een
     rooster van vier regels met elf getallen geen hulp maar een drempel. Twee suites bewaken dat
     ook, en terecht: pw-verbouw eist hoogstens zes getallen op dag een ("het dagscherm is geen
     dashboard") en pw-dag1 eist dat grammatica geen kwart van de zin krijgt. Wie hier voor het eerst
     staat heeft een knop nodig, geen agenda.

     Vanaf dag twee weet je wat een les is, en dan is de vraag een andere: waar zeg ik nu ja op. */
  var toonPlan = dagenTotaal() > 1;""",
)

rep(
    """+ct("stap","step")+" "+hStap+"/4 \u00b7 "+hNaam""",
    """+ct("stap","step")+" "+hStap+"/"+hTot+" \u00b7 "+hNaam""",
)

rep(
    """      "<p class='muted' style='margin:6px 0 0'>"+(hervat ? ct("Je stopte bij stap "+hStap+" van 4: "+hNaam+". De rest van je portie staat klaar.",
                                                              "You stopped at step "+hStap+" of 4: "+hNaam+". The rest of your session is waiting.") : portieTxt)+"</p>"+""",
    """      (hervat
        ? "<p class='muted' style='margin:6px 0 0'>"+
            ct("Je stopte bij stap "+hStap+" van "+hTot+": "+hNaam+"."+(toonPlan ? "" : " De rest van je portie staat klaar."),
               "You stopped at step "+hStap+" of "+hTot+": "+hNaam+"."+(toonPlan ? "" : " The rest of your session is waiting."))+"</p>"+
          (toonPlan ? dagPlanHtml(S.lesFlowNu && S.lesFlowNu.stap, S.lesFlowNu && S.lesFlowNu.stappen) : "")
        : toonPlan ? dagPlanHtml()
                   : "<p class='muted' style='margin:6px 0 0'>"+portieTxt+"</p>")+""",
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
