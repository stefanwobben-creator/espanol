#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.116: het pad. Van losse tegels naar één route door de grammatica.

## De vraag

Stefan: "wanneer maak je er in plaats van losse elementen nu een geïntegreerde les van?"

Terecht. Er staan nu vijf tegels die stuk voor stuk iets goeds doen en die samen niets zijn:

    Achtergrond of gebeurtenis   v23.106   snap je het verschil, zonder Spaans
    De les                       v23.115   één tijd leren, vijf stappen
    Wie is dit?                  v23.109   herken je de persoon
    Welke tijd is dit?           v23.113   herken je de tijd
    Conjugador                             produceren

Jij moet kiezen welke je doet, in welke volgorde, en wanneer je klaar bent. Dat is precies het
werk dat de app hoort te doen, en het is ook waar het ontwerpadvies over ging: fasen kun je niet
overslaan, dus dan moet iets weten wat jouw volgende stap is.

## Wat dit toevoegt

Eén scherm, "Grammatica", met de route door één grammaticapunt: de verleden tijd, indefinido
tegenover imperfecto. Vijf stappen, met per stap of hij af is en wat je score was, en één knop:
verder waar je gebleven bent.

    1. Snap je het verschil?        Nederlands, geen Spaans      brok
    2. De imperfecto leren          vijf stappen, geblokkeerd    les
    3. De indefinido leren          vijf stappen, geblokkeerd    les
    4. Zie je welke tijd er staat?  door elkaar, herkennen       toets
    5. In een echte zin             komt nog

Stap 4 gaat pas open als 2 en 3 af zijn. Dat is de regel "fasen niet overslaan" in code: door
elkaar husselen is de laatste stap, niet de eerste. Precies Stefans klacht van vanavond ("ik word
direct getoetst en alle tijden door elkaar").

## Wat "af" betekent

Elk scherm scoorde tot nu toe op zijn eigen manier: de brok in beste-van-twaalf, de les in hoogste
stap. Zonder één definitie van "af" kan geen enkel pad bestaan. Daarom staat de eis nu per SOORT
stap in data (GRAM_EIS), niet per stap:

    betekenis   beste >= 11 van de 12   (de regel snappen is bijna-foutloos of niet)
    les         alle vijf de stappen doorlopen
    herkennen   beste >= 10 van de 12

Een zesde stap toevoegen is één regel data, en de eis komt uit zijn soort.

## Wat dit expres NIET doet

De losse tegels blijven staan en werken. Dit scherm dwingt niets af: het wijst alleen. En er is
nog geen koppeling aan de dagles of aan de SRS. Eerst moet blijken dat het pad klopt.

Stap 5 bestaat nog niet en staat er daarom als "komt nog" in plaats van als een lege knop. Liever
eerlijk grijs dan een deur naar niets.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.116"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.116" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = huidig_ver != NIEUW and (DOE_APP or _num(huidig_ver) < _num(NIEUW))

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


# ============================================================ het pad
A_PAD = u'''/* ================= DE LES (v23.115) ================='''
N_PAD = u'''/* ================= HET PAD (v23.116) =================

   Stefan: "wanneer maak je er in plaats van losse elementen nu een geïntegreerde les van?"

   Er stonden vijf tegels die stuk voor stuk iets goeds doen en die samen niets zijn. Jij moest
   kiezen welke je deed, in welke volgorde, en wanneer je klaar was. Dat is het werk dat de app
   hoort te doen.

   Dit scherm is de route door één grammaticapunt. Het dwingt niets af: het wijst. De losse tegels
   blijven gewoon werken.

   De volgorde is niet willekeurig. Stap 4 (alles door elkaar) gaat pas open als de twee lessen af
   zijn, want door elkaar husselen is de laatste stap en niet de eerste. Dat is regel R5 uit het
   ontwerpadvies, en het is precies wat Stefan miste: "ik word direct getoetst en alle tijden door
   elkaar". */

/* Wat "af" betekent, per SOORT stap en niet per stap. Elk scherm scoorde op zijn eigen manier
   (de brok in beste-van-twaalf, de les in hoogste stap) en zonder één definitie kan geen pad
   bestaan. Een zesde stap toevoegen is één regel data; de eis komt uit zijn soort. */
var GRAM_EIS = {
  betekenis: function(st){ return (st.beste || 0) >= 11; },
  les:       function(st){ return (st.stapMax || 0) >= LES_STAPPEN.length - 1; },
  herkennen: function(st){ return (st.beste || 0) >= 10; },
  /* het scherm hiervoor bestaat nog niet, de eis wel. Zo staat de lat er al voordat er iemand
     onder door kan lopen, en de poort kan afdwingen dat elk soort stap een eis heeft. Elf van de
     twaalf, want kiezen tussen twee tijden betekent dat gokken je al de helft geeft. */
  keuze:     function(st){ return (st.beste || 0) >= 11; }
};
var GRAM_STAND = {
  betekenis: function(st){ return st.rondes ? (st.beste || 0) + "/12" : ""; },
  les:       function(st){ return st.stapMax !== undefined ? ct("stap ", "step ") + ((st.stapMax || 0) + 1) + "/5" : ""; },
  herkennen: function(st){ return st.rondes ? ct("beste ", "best ") + (st.beste || 0) + "/12" : ""; },
  keuze:     function(st){ return st.rondes ? ct("beste ", "best ") + (st.beste || 0) + "/12" : ""; }
};

var GRAM_PADEN = [
  {id:"indefimperf",
   nl:"De verleden tijd: indefinido of imperfecto",
   en:"The past tense: indefinido or imperfecto",
   uitNl:"Het Nederlands heeft \\u00e9\\u00e9n verleden tijd, het Spaans heeft er twee die je uit elkaar moet houden. Dit is de route.",
   uitEn:"Dutch has one past tense, Spanish has two you need to tell apart. This is the route.",
   stappen:[
     {brok:"indefimperf.betekenis", soort:"betekenis", view:"brok",
      nl:"Snap je het verschil?", en:"Do you get the difference?",
      subNl:"Twaalf Nederlandse zinnen, geen woord Spaans.", subEn:"Twelve English sentences, no Spanish at all."},
     {brok:"les.imperfecto", soort:"les", view:"les", arg:"imperfecto",
      nl:"De imperfecto leren", en:"Learn the imperfecto",
      subNl:"Vijf stappen, \\u00e9\\u00e9n tijd. De eerste twee stellen geen vraag.", subEn:"Five steps, one tense. The first two ask nothing."},
     {brok:"les.indefinido", soort:"les", view:"les", arg:"indefinido",
      nl:"De indefinido leren", en:"Learn the indefinido",
      subNl:"Zelfde vijf stappen, de andere tijd.", subEn:"Same five steps, the other tense."},
     {brok:"vorm.tijd", soort:"herkennen", view:"tijdvorm",
      nl:"Zie je welke tijd er staat?", en:"Can you see which tense it is?",
      subNl:"Nu pas door elkaar. Door elkaar is de laatste stap, niet de eerste.",
      subEn:"Only now mixed. Mixing is the last step, not the first."},
     {brok:"indefimperf.keuze", soort:"keuze", view:null,
      nl:"In een echte zin kiezen", en:"Choosing inside a real sentence",
      subNl:"Komt nog. Dit is de stap waar de regel en de vorm samenkomen.",
      subEn:"Coming. This is where the rule and the form come together."}
   ]}
];

function gramPadStap(p, i){
  var s = p.stappen[i];
  var st = brokLees(s.brok);
  var eis = GRAM_EIS[s.soort];
  var af = !!(eis && eis(st));
  var stand = GRAM_STAND[s.soort] ? GRAM_STAND[s.soort](st) : "";
  return {s:s, st:st, af:af, stand:stand, bestaat:!!s.view};
}
/* De eerste stap die nog niet af is EN te doen is. Stappen die nog niet bestaan blokkeren het pad
   niet: die worden overgeslagen als volgende, maar staan wel in de lijst zodat je ziet wat er komt. */
function gramPadVolgende(p){
  for(var i = 0; i < p.stappen.length; i++){
    var x = gramPadStap(p, i);
    if(!x.af && x.bestaat) return i;
  }
  return -1;
}
/* Op slot: een stap is pas te doen als alle stappen ervoor die WEL bestaan af zijn. Zo kan
   "alles door elkaar" niet je eerste oefening zijn. */
function gramPadOpSlot(p, i){
  for(var j = 0; j < i; j++){
    var x = gramPadStap(p, j);
    if(x.bestaat && !x.af) return true;
  }
  return false;
}
function gramPadKlaar(p){
  for(var i = 0; i < p.stappen.length; i++){
    var x = gramPadStap(p, i);
    if(x.bestaat && !x.af) return false;
  }
  return true;
}

function gramPadGa(p, i){
  var s = p.stappen[i];
  if(!s.view) return;
  if(s.view === "les"){ lesStart(s.arg); }
  if(s.view === "brok"){ brokSpel = null; }
  if(s.view === "tijdvorm"){ tijdvormSpel = null; }
  funView = s.view;
  navPush({t:"fun", v:s.view});
  renderFun();
}

function renderFunPad(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var p = GRAM_PADEN[0];
  var volgende = gramPadVolgende(p);
  var klaar = gramPadKlaar(p);

  var html = "<h2>" + ct("Grammatica \\ud83e\\udded", "Grammar \\ud83e\\udded") + "</h2>" +
    "<p class='muted'><b>" + ct(p.nl, p.en) + "</b></p>" +
    "<p class='muted' style='font-size:.9rem'>" + ct(p.uitNl, p.uitEn) + "</p>" +
    "<div id='padLijst' style='margin:10px 0'>";

  p.stappen.forEach(function(s, i){
    var x = gramPadStap(p, i);
    var slot = gramPadOpSlot(p, i);
    var isNu = i === volgende;
    var merk = x.af ? "\\u2713" : (!x.bestaat ? "\\u00b7" : (slot ? "\\ud83d\\udd12" : (i + 1)));
    var kleur = x.af ? "var(--green)" : (isNu ? "var(--accent)" : "var(--muted)");
    html += "<div class='lesson pad-stap" + (x.af ? " pad-af" : "") + (isNu ? " pad-nu" : "") + "'" +
      " id='pad" + i + "'" +
      " data-i='" + i + "'" +
      (x.bestaat && !slot ? "" : " style='opacity:.5'") + ">" +
      "<div class='lnum' style='color:" + kleur + "'>" + merk + "</div>" +
      "<div class='lbody'><b>" + ct(s.nl, s.en) + "</b><span>" + ct(s.subNl, s.subEn) +
        (x.stand ? " \\u00b7 " + x.stand : "") + "</span></div>" +
      "<div class='lstatus'>" + (x.af ? "\\u2713" : (x.bestaat && !slot ? "\\u25b6" : "")) + "</div></div>";
  });
  html += "</div>";

  if(klaar){
    html += "<div class='feedback ok' id='padKlaar'>" +
      ct("Je hebt dit hele pad gelopen.", "You have walked this whole path.") + "</div>";
  } else if(volgende >= 0){
    html += "<div class='row' style='margin-top:6px'><button class='primary' id='btnPadVerder'>" +
      ct("Verder: ", "Continue: ") + ct(p.stappen[volgende].nl, p.stappen[volgende].en) + " \\u2192</button></div>";
  }
  html += "<p class='muted' style='font-size:.82rem; margin-top:10px'>" +
    ct("Je kunt alles ook los blijven doen in de Speeltuin. Dit scherm dwingt niets af, het wijst alleen waar je bent.",
       "You can still do everything separately in the Playground. This screen enforces nothing, it just shows where you are.") + "</p>" +
    "<div class='row' style='margin-top:8px'><button class='mini' id='btnFunTerug'>" + fx("terug") + "</button></div>";

  el.innerHTML = html;
  Array.prototype.forEach.call(el.querySelectorAll(".pad-stap"), function(d){
    var i = Number(d.getAttribute("data-i"));
    var x = gramPadStap(p, i);
    if(!x.bestaat || gramPadOpSlot(p, i)) return;
    d.style.cursor = "pointer";
    d.onclick = function(){ gramPadGa(p, i); };
  });
  var bv = document.getElementById("btnPadVerder");
  if(bv) bv.onclick = function(){ gramPadGa(p, volgende); };
  var tb = document.getElementById("btnFunTerug");
  if(tb) tb.onclick = function(){ funView = null; renderFun(); };
}

/* ================= DE LES (v23.115) ================='''
rep(A_PAD, N_PAD)

# ============================================================ de tegel
A_TEGEL = u'''    /* v23.115: geen meting maar een les, en daarom staat hij bovenaan. */'''
N_TEGEL = u'''    /* v23.116: de route door de grammatica. Staat bovenaan omdat hij de andere drie aanstuurt. */
    {v:"pad",     id:"ftPad",     e:"\\ud83e\\udded",            t:ct("Grammatica","Grammar"), s:ct("De route door de verleden tijd, van het verschil snappen tot in een echte zin. Wijst je volgende stap aan.","The route through the past tense, from getting the difference to using it in a real sentence. Points at your next step."), gezien:false},
    /* v23.115: geen meting maar een les, en daarom staat hij bovenaan. */'''
rep(A_TEGEL, N_TEGEL)

# ============================================================ de router
A_ROUTE = u'''  if(funView === "les"){ renderFunLes(); return; }   // v23.115'''
N_ROUTE = u'''  if(funView === "les"){ renderFunLes(); return; }   // v23.115
  if(funView === "pad"){ renderFunPad(); return; }   // v23.116'''
rep(A_ROUTE, N_ROUTE)

# ============================================================ uit de dagportie
A_DAG = u'''var DAGSPEL_UIT = {avt:1, duel:1, brok:1, omkeer:1, tijdvorm:1, les:1};'''
N_DAG = u'''var DAGSPEL_UIT = {avt:1, duel:1, brok:1, omkeer:1, tijdvorm:1, les:1, pad:1};'''
rep(A_DAG, N_DAG)

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
