#!/usr/bin/env python3
# v23.160 - de vormen komen in je dag
#
# Stefan, 21 aug: "ja wat is preterito imperfecto, perfecto, indefinido enzo maar ook hoe zijn de
# vervoegingen, ik moet dat veel oefenen."
#
# Ik ging dit bouwen. Dat was fout: het staat er al, en dat is precies het probleem.
#
# WAT ER AL IS, GETELD
#
#   Conjugador        13 fasen, van "-ar in het presente" tot "alles door elkaar", 33 werkwoorden
#   De les             6 stappen per rij (ontmoeten, opbouwen, herkennen, een gat, losse cel,
#                      nieuwe werkwoorden), voor elke open tijd en voor de zes patronen
#   De route           2 paden van 9 stappen, waaronder "Het imperfecto in je vingers" en
#                      "Het indefinido in je vingers"
#   Plus omkeer, zin, tijdvorm en brok.
#
# WAT DE DAGLES ERVAN GEBRUIKT
#
#   Gemeten op een profiel met alle lessen af, 30 minuten, A2:
#
#     woorden      leren        5 kaartjes
#     grammatica   leren        El of la, stap 1 van 3
#     toetsje      sneller      6 vragen
#     input        begrijpen    een gesprek
#     produceren   zelf maken   3 zinnen
#
#   Nul. Geen enkel blok in de dagles raakt een werkwoordsvorm aan. Al die machinerie hangt aan
#   zes tegels op de Grammatica-tab en wordt door niets gepland. Wie er niet uit zichzelf heen
#   klikt, oefent nooit een vorm. Dat is het antwoord op "ik moet dat veel oefenen": niet nog een
#   oefening erbij, maar de bestaande in je dag zetten.
#
# WAT DEZE RONDE DOET
#
#   Een blok "Vormen" in de dagles, om de dag, dat precies een stap van "De les" doet: een rijtje,
#   op de plek waar je gebleven was. Een stap per keer en niet de hele les, want zes stappen achter
#   elkaar is geen dagles meer, en omdat de afstand tussen de stappen het werk doet.
#
#   Om de dag, en wel op de dagen dat je NIET met Chispa praat. Zo groeit de dag niet op twee assen
#   tegelijk. Gemeten draadverdeling voor die dag: leren 96 sec van 393, tegenover Nation's kwart.
#   Er is dus ruimte in precies de draad waar een vormdrill hoort.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.160"

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
    # 1. wanneer, en welk rijtje
    # -----------------------------------------------------------------------
    rep('''function lesKlaar(t){''',
        '''/* ================= HET VORMENBLOK (v23.160) =================

   Stefan: "hoe zijn de vervoegingen, ik moet dat veel oefenen."

   Het bestond al, in drie soorten zelfs, en de dagles raakte er geen van aan. Dit blok is dus geen
   nieuwe oefening maar een afspraak: om de dag doe je een stap van De les, en die stap staat in je
   plan voordat je begint.

   Waarom een stap en niet de hele les: zes stappen achter elkaar is geen dagles meer, en de
   afstand tussen de stappen is hier het werk. Wie het rijtje op zes achtereenvolgende dagen
   aanraakt onthoudt het; wie het op een middag zes keer doet, niet.

   Waarom om de dag, en juist op de dagen dat je niet met Chispa praat: anders groeit de dag op
   twee assen tegelijk. praatBeurt() draait op oneven dagen, dit dus op even. */
function vormBeurt(){
  var d = 0;
  try { d = dagenTotaal(); } catch(e){ d = 0; }
  if(d <= 1) return false;
  return (d % 2) === 0;
}
/* Welk rijtje vandaag. Eerst waar je al aan begonnen bent en nog niet af is (een halve les afmaken
   gaat voor een nieuwe beginnen), dan wat "Welke tijd is dit?" als struikelblok gemeten heeft, dan
   gewoon de eerste die nog niet af is. Geen nieuwe volgorde: lesRijIds() bepaalt hem al. */
function vormRijVandaag(){
  var ids = [];
  try { ids = lesRijIds(); } catch(e){ ids = []; }
  var open = ids.filter(function(t){ return !lesKlaar(t); });
  if(!open.length) return null;
  var bezig = open.filter(function(t){
    var st = brokLees(lesId(t));
    return (st.stapMax || 0) > 0;
  });
  if(bezig.length) return bezig[0];
  var w = null;
  try { w = tijdvormTopVerwar(); } catch(e){ w = null; }
  if(w && w.getoond && open.indexOf(w.getoond) !== -1) return w.getoond;
  return open[0];
}
/* De stap waar je vandaag aan toe bent. stapMax is de hoogste stap die je AF hebt, dus de volgende
   is stapMax + 1; is er nog niets, dan stap 0. */
function vormStapVandaag(t){
  var st = brokLees(lesId(t));
  return (typeof st.stapMax === "number") ? Math.min(st.stapMax + 1, LES_STAPPEN.length - 1) : 0;
}
function vormKan(){ return vormBeurt() && !!vormRijVandaag(); }
function vormWat(){
  var t = vormRijVandaag();
  if(!t) return "";
  var r = lesRij(t), s = LES_STAPPEN[vormStapVandaag(t)] || {};
  return (r ? r.es : t) + " \\u00b7 " + ct(s.nl || "", s.en || "");
}
function lesKlaar(t){''')

    # -----------------------------------------------------------------------
    # 2. het blok in het plan
    # -----------------------------------------------------------------------
    rep('''  try { qid = lesFlowQuizId(); } catch(e){ qid = null; }
  if(qid){''',
        '''  /* v23.160: het vormenblok, tussen de grammatica en het toetsje. Grammatica gaat over de regel,
     dit over de vorm, en dat zijn sinds v23.107 (het brokkenmodel) twee verschillende dingen die
     apart gemeten horen te worden. Ze staan dus naast elkaar en niet door elkaar. */
  var vormOk = false;
  try { vormOk = vormKan(); } catch(e){ vormOk = false; }
  if(vormOk){
    blokken.push({stap:"vormen", naam:ct("Vormen","Forms"), draad:ct("leren","study"),
      wat:vormWat(), sec:6 * sec});
  }
  try { qid = lesFlowQuizId(); } catch(e){ qid = null; }
  if(qid){''')

    # -----------------------------------------------------------------------
    # 3. de stap in de flow
    # -----------------------------------------------------------------------
    rep('''    lesFlow.stap = "toetsjes";
    // v19.49: precies één toetsje per dagles (dat van dit grammatica-onderwerp), niet de hele
    // herhaallijst achter elkaar. Anders is de dagles zo lang dat je er niet aan begint.
    var qid = lesFlowQuizId();
    if(qid){
      lesFlow.quizzesTeDoen = [qid];
      show("toetsjes");
      startQuiz(qid, toetsvragenPerDag());
      return;
    }
  }''',
        '''    /* v23.160: het vormenblok. Elke route naar het toetsje loopt hier langs, ook op de dagen dat er
       geen vormenblok is: dan zet deze stap zichzelf meteen door. Zo staat de opening van het
       toetsje op één plek in plaats van op twee. */
    lesFlow.stap = "vormen";
    var vt = null;
    try { vt = vormKan() ? vormRijVandaag() : null; } catch(e){ vt = null; }
    if(vt && lesStart(vt)){
      lesSpel.stap = vormStapVandaag(vt);
      lesFlow.vormRij = vt;
      lesFlow.gekozenSpel = "les";
      funView = "les";
      show("speeltuin");
      lesFlowBewaar();
      return;
    }
  }
  if(lesFlow.stap === "vormen"){
    lesSpel = null;
    lesFlow.stap = "toetsjes";
    // v19.49: precies één toetsje per dagles (dat van dit grammatica-onderwerp), niet de hele
    // herhaallijst achter elkaar. Anders is de dagles zo lang dat je er niet aan begint.
    var qid = lesFlowQuizId();
    if(qid){
      lesFlow.quizzesTeDoen = [qid];
      show("toetsjes");
      startQuiz(qid, toetsvragenPerDag());
      return;
    }
  }''')

    rep('''var LESFLOW_VOLGORDE = ["woorden", "grammatica", "toetsjes", "input", "produceren"];''',
        '''var LESFLOW_VOLGORDE = ["woorden", "grammatica", "vormen", "toetsjes", "input", "produceren"];''')

    rep('''  if(f.stap === "grammatica") return ct("Grammatica","Grammar");''',
        '''  if(f.stap === "grammatica") return ct("Grammatica","Grammar");
  if(f.stap === "vormen") return ct("Vormen","Forms");''')

    # -----------------------------------------------------------------------
    # 4. De les weet dat hij in een dagles zit: één stap, dan terug
    # -----------------------------------------------------------------------
    rep('''function renderFunLes(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var terug = function(){ lesSpel = null; funTerug(); };''',
        '''function renderFunLes(){
  var el = document.getElementById("funCard");
  if(!el) return;
  /* v23.160: draait deze les binnen je dagles, dan is hij één stap lang en gaat de knop terug naar
     de les in plaats van naar de volgende stap. De afstand tussen de stappen is hier het werk. */
  var inFlowLes = !!(lesFlow && lesFlow.stap === "vormen" && lesFlow.gekozenSpel === "les");
  var terug = function(){ lesSpel = null; if(inFlowLes){ lesFlowVolgende(); return; } funTerug(); };''')

    # de knoppen na een stap: in de dagles is "Door →" de enige
    rep('''        "<div class='row' style='margin-top:10px'>" +
          (gehaald && L.stap < LES_STAPPEN.length - 1
            ? "<button class='primary' id='btnLesVerder'>" + ct("Volgende stap \\u2192", "Next step \\u2192") + "</button>"
            : "") +
          (gehaald && L.stap >= LES_STAPPEN.length - 1
            ? "<button class='primary' id='btnLesKlaar'>" + ct("Klaar \\u2713", "Done \\u2713") + "</button>"
            : "") +
          "<button class='ghost' id='btnLesOpnieuw'>" + ct("Deze stap opnieuw", "This step again") + "</button></div>";
      el.innerHTML = html;
      var bv = document.getElementById("btnLesVerder");''',
        '''        "<div class='row' style='margin-top:10px'>" +
          /* v23.160: in je dagles is dit blok één stap. Er staat dus geen "volgende stap" maar
             "Door", en de volgende stap krijg je morgen. Wie meer wil kan de les altijd los doen. */
          (inFlowLes
            ? "<button class='primary' id='btnLesFlowDoor'>" + ct("Door \\u2192", "Continue \\u2192") + "</button>"
            : (gehaald && L.stap < LES_STAPPEN.length - 1
                ? "<button class='primary' id='btnLesVerder'>" + ct("Volgende stap \\u2192", "Next step \\u2192") + "</button>"
                : "") +
              (gehaald && L.stap >= LES_STAPPEN.length - 1
                ? "<button class='primary' id='btnLesKlaar'>" + ct("Klaar \\u2713", "Done \\u2713") + "</button>"
                : "")) +
          "<button class='ghost' id='btnLesOpnieuw'>" + ct("Deze stap opnieuw", "This step again") + "</button></div>";
      el.innerHTML = html;
      /* de stap gaat af zodra je hem gehaald hebt, ook in de dagles: anders krijg je morgen weer
         dezelfde stap en komt de les nooit vooruit */
      var bd = document.getElementById("btnLesFlowDoor");
      if(bd) bd.onclick = function(){ if(gehaald) lesStapAf(); lesSpel = null; lesFlowVolgende(); };
      var bv = document.getElementById("btnLesVerder");''')

    # De stappen 0 en 1 stellen geen vraag: die lezen alleen. In je dagles lopen ze dus door naar de
    # eerste stap die wel iets vraagt, in plaats van het blok af te sluiten met "gelezen". Dat
    # gebeurt vanzelf: btnLesVerder roept al lesStapAf() aan en zet L.stap door, en het blok eindigt
    # pas bij btnLesFlowDoor hierboven. Er is hier dus niets te doen, en dat is precies waarom deze
    # regel er staat: anders gaat de volgende lezer ernaar zoeken.

    # -----------------------------------------------------------------------
    # 5. pauzeren en hervatten midden in het vormenblok
    # -----------------------------------------------------------------------
    rep('    gekozenSpel: lesFlow.gekozenSpel || null,\n    vaardigheid: lesFlow.vaardigheid || null,   // v23.140: draagt ook de keuze van het inputblok', '    gekozenSpel: lesFlow.gekozenSpel || null,\n    vormRij: lesFlow.vormRij || null,           // v23.160: welk rijtje het vormenblok doet\n    vaardigheid: lesFlow.vaardigheid || null,   // v23.140: draagt ook de keuze van het inputblok')
    rep('    gekozenSpel: n.gekozenSpel || null,\n    vaardigheid: n.vaardigheid || null,', '    gekozenSpel: n.gekozenSpel || null,\n    vormRij: n.vormRij || null,\n    vaardigheid: n.vaardigheid || null,')
    rep('  if(lesFlow.stap === "toetsjes"){ lesFlowVolgende(); return; }', '  /* v23.160: pauzeer je midden in het vormenblok, dan komt het rijtje terug waar je was. Zonder\n     deze tak zou hervatten je op het keuzescherm van De les zetten (lesSpel is null na een\n     herlaad), en dan sta je in een dagles ineens in een menu. */\n  if(lesFlow.stap === "vormen"){\n    var vr = lesFlow.vormRij;\n    if(!vr || !lesStart(vr)){ lesFlowVolgende(); return; }\n    lesSpel.stap = vormStapVandaag(vr);\n    lesFlow.gekozenSpel = "les";\n    funView = "les";\n    show("speeltuin");\n    lesFlowBewaar();\n    return;\n  }\n  if(lesFlow.stap === "toetsjes"){ lesFlowVolgende(); return; }')

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
