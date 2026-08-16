#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.117: gestold. Een grammaticapunt is pas af als je het dagen later nog kunt.

## Waarom dit de eerste ronde is en niet de laatste

Stefan gebruikte het woord "gestold" en dat is scherper dan "gehaald". Tot nu toe kende de app
alleen het tweede: alle stappen groen, klaar, door.

Kim & Webb (2022, 98 effectgroottes uit 48 experimenten, N = 3.411) vonden dat korte intervallen
even goed scoren op de DIRECTE toets en slechter op de UITGESTELDE. Precies dat verschil is wat een
app die vandaag afvinkt niet kan zien. Een pad dat je op de dag zelf laat doorstromen bouwt de
illusie op die deze hele verbouwing moest wegnemen.

Dit is ook de goedkoopste ronde van de vier die op de rol staan, en de enige die verandert wat de
app BEWEERT in plaats van wat hij doet. Zolang "gestold" niet bestaat, weet je van geen enkele
uitbreiding of hij werkt.

## Wat er verandert

    gehaald   alle stappen van het pad groen. Krijgt een datum.
    wachten   minstens drie dagen. De app zegt eerlijk dat er niets te doen valt aan dit punt.
    hertoets  tien opgaven, gemengd, uit alles wat het pad besloeg
    gestold   pas dan

De hertoets is een zesde stap in het pad en gebruikt dezelfde machinerie als de andere: een eis in
GRAM_EIS, een stand in GRAM_STAND. Acht van de tien.

## De verhouding die ertoe doet

Gemeten: in het indefinido volgen 13 van de 33 werkwoorden de regel en 20 niet. In het imperfecto
is dat 30 om 3. Een hertoets die alleen regelmatige werkwoorden pakt, meet dus iets heel anders dan
wat je in het wild tegenkomt, en zou "gestold" opnieuw tot een leugen maken.

De oplossing is geen weegcode maar het weglaten van een filter: de hertoets trekt uit ALLE
werkwoorden die de tijd kennen, niet uit de fasepool van de Conjugador. Daarmee komt de verhouding
onregelmatig vanzelf goed.

Dat "kennen" stond op twee plekken: conjVerbPool wist welke tabel bij welke tijd hoort, en de
hertoets zou het opnieuw moeten weten. Nu staat het in conjHeeftTijd() en lezen ze het allebei
daaruit. Architectuurregel 15 augustus.

## Wat de wachtdagen krijgen

Het pad zegt het eerlijk: aan dit punt valt nu niets te doen, en het wijst naar lezen, luisteren en
woorden. Dat is geen verlegenheidsoplossing. Zodra een pad wachttijden afdwingt, zijn die sporen
structureel nodig in plaats van versiering.

## Wat dit expres NIET doet

De onregelmatige werkwoorden gaan hier nog niet naar de woord-SRS (ronde 4), en er is nog geen
tweede grammaticapunt om naar uit te wijken. De wachtdagen wijzen daarom voorlopig naar wat er al
is.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.117"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.117" not in src
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


# ---------------- 1. "kent dit werkwoord deze tijd" op één plek
A_POOL = u'''function conjVerbPool(t){
  // v19.68: de bak werkwoorden komt uit de fase waar je staat. Fase 1 is er vier groot; dat is klein
  // genoeg om ze na een paar rondes \\u00e9cht te kennen in plaats van ze allemaal een beetje te herkennen.
  var basis = conjFasePool();
  if(t === "presente") return basis;
  // v23.107: de imperfecto is voor elk werkwoord te berekenen, dus daar valt niets te filteren.
  // Zonder deze regel zou hij de pool langs VERBOS_PASADO leggen en werkwoorden weglaten die hij
  // prima aankan.
  if(t === "imperfecto") return basis;
  var tabel = (t === "subjuntivo") ? VERBOS_SUBJ : VERBOS_PASADO;
  var pool = basis.filter(function(v){ return !!tabel[v.inf]; });
  return pool.length ? pool : basis;
}'''
N_POOL = u'''/* v23.117: "kent dit werkwoord deze tijd" stond alleen hier, en de hertoets heeft het ook nodig.
   Nu \\u00e9\\u00e9n regel met twee lezers in plaats van twee kopie\\u00ebn die uit elkaar kunnen lopen.

   presente en imperfecto zijn voor elk werkwoord te berekenen (de imperfecto heeft precies drie
   uitzonderingen en die zitten in VERBOS_IMPERF). De andere drie hangen aan een tabel; staat een
   werkwoord daar niet in, dan zou conjVorm terugvallen op het presente en dus een fout antwoord
   als juist rekenen. */
function conjHeeftTijd(v, t){
  if(t === "presente" || t === "imperfecto") return true;
  var tabel = (t === "subjuntivo") ? VERBOS_SUBJ : VERBOS_PASADO;
  return !!tabel[v.inf];
}
function conjVerbPool(t){
  // v19.68: de bak werkwoorden komt uit de fase waar je staat. Fase 1 is er vier groot; dat is klein
  // genoeg om ze na een paar rondes \\u00e9cht te kennen in plaats van ze allemaal een beetje te herkennen.
  var basis = conjFasePool();
  var pool = basis.filter(function(v){ return conjHeeftTijd(v, t); });
  return pool.length ? pool : basis;
}
/* Alle werkwoorden die deze tijd kennen, los van de fase waar je staat. De hertoets gebruikt dit
   en niet conjVerbPool: die laatste volgt je Conjugador-fase en zou dus precies de makkelijke
   werkwoorden pakken. Gemeten verhouding regelmatig tegenover onregelmatig: presente 11/22,
   indefinido 13/20, imperfecto 30/3. Wie alleen uit de fasepool trekt, meet iets anders dan wat je
   in het wild tegenkomt. */
function conjAlleVerbs(t){
  return VERBOS.filter(function(v){ return conjHeeftTijd(v, t); });
}'''
rep(A_POOL, N_POOL)

# ---------------- 2. de hertoets
A_HER = u'''/* ================= HET PAD (v23.116) ================='''
N_HER = u'''/* ================= DE HERTOETS (v23.117) =================

   Stefan gebruikte het woord "gestold", en dat is scherper dan "gehaald". Kim & Webb (2022) vonden
   dat korte intervallen even goed scoren op de directe toets en slechter op de uitgestelde. Een app
   die vandaag afvinkt kan dat verschil niet zien, en bouwt dus de illusie op die deze verbouwing
   moest wegnemen.

   Tien opgaven, gemengd over alles wat het pad besloeg, op zijn vroegst drie dagen na "gehaald".
   Acht goed en het punt heet gestold.

   De werkwoorden komen uit conjAlleVerbs en niet uit conjVerbPool: die laatste volgt je
   Conjugador-fase en zou precies de makkelijke werkwoorden pakken. */
var HERTOETS_WACHT = 3;
var HERTOETS_LEN = 10;
var HERTOETS_EIS = 8;
var hertoetsSpel = null;

function padId(p){ return "pad." + p.id; }
/* Alle stappen behalve de hertoets zelf groen. De hertoets is de laatste stap en kan niet zijn
   eigen voorwaarde zijn. */
function padGehaald(p){
  for(var i = 0; i < p.stappen.length; i++){
    var s = p.stappen[i];
    if(s.soort === "hertoets") continue;
    var x = gramPadStap(p, i);
    if(x.bestaat && !x.af) return false;
  }
  return true;
}
/* De datum van "gehaald" wordt \\u00e9\\u00e9n keer gezet en daarna niet meer verschoven, anders zou elke
   extra ronde de wachttijd opnieuw laten beginnen. */
function padGehaaldStempel(p){
  if(!padGehaald(p)) return null;
  S.brok = S.brok || {};
  var st = brokLees(padId(p));
  if(!st.gehaald){ st.gehaald = today(); S.brok[padId(p)] = st; try { persist(); } catch(e){} }
  return st.gehaald;
}
function padMagHertoets(p){
  var d = padGehaaldStempel(p);
  if(!d) return false;
  return today() >= addDays(d, HERTOETS_WACHT);
}
function padDagenTeGaan(p){
  var st = brokLees(padId(p));
  if(!st.gehaald) return null;
  var doel = addDays(st.gehaald, HERTOETS_WACHT), n = 0, d = today();
  while(d < doel && n < 60){ d = addDays(d, 1); n++; }
  return n;
}

/* De opgaven. Drie betekenisvragen uit BROK_TIJD en zeven vormvragen uit de tijden van dit pad,
   getypt en zonder tabel. Dat is de zwaarste vraagvorm, en dat hoort: dit is de toets die bepaalt
   of je verder mag. */
function hertoetsBouw(p){
  var tijden = (p.tijden || ["imperfecto", "indefinido"]).filter(function(t){ return !!conjTiempo(t); });
  var rij = [];
  geschud(BROK_TIJD.slice()).slice(0, 3).forEach(function(z){ rij.push({soort:"betekenis", z:z}); });
  var vorm = [];
  tijden.forEach(function(t){
    geschud(conjAlleVerbs(t)).forEach(function(v){
      for(var i = 0; i < 6; i++) vorm.push({soort:"vorm", v:v, p:i, t:t});
    });
  });
  geschud(vorm).slice(0, HERTOETS_LEN - rij.length).forEach(function(x){ rij.push(x); });
  return geschud(rij);
}
function hertoetsStart(p){
  hertoetsSpel = {pad:p, rij:hertoetsBouw(p), i:0, goed:0, gekozen:null};
  return hertoetsSpel;
}
function hertoetsAntwoord(gegeven){
  if(!hertoetsSpel || hertoetsSpel.gekozen !== null) return;
  var q = hertoetsSpel.rij[hertoetsSpel.i];
  var g = String(gegeven || "").trim();
  if(!g) return;
  hertoetsSpel.gekozen = g;
  var goed = (q.soort === "betekenis")
    ? (g === q.z.s)
    : (stripAcc(norm(g)) === stripAcc(norm(conjVorm(q.v, q.p, q.t))));
  if(goed) hertoetsSpel.goed++;
  renderFunHertoets();
}
function hertoetsVolgende(){
  if(!hertoetsSpel) return;
  hertoetsSpel.i++;
  hertoetsSpel.gekozen = null;
  if(hertoetsSpel.i >= hertoetsSpel.rij.length){
    var p = hertoetsSpel.pad;
    S.brok = S.brok || {};
    var st = brokLees(padId(p));
    st.pogingen = (st.pogingen || 0) + 1;
    st.beste = Math.max(st.beste || 0, hertoetsSpel.goed);
    st.laatst = today();
    if(hertoetsSpel.goed >= HERTOETS_EIS && !st.gestold) st.gestold = today();
    S.brok[padId(p)] = st;
    try { persist(); } catch(e){}
  }
  renderFunHertoets();
}

function renderFunHertoets(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var terug = function(){ funView = "pad"; hertoetsSpel = null; renderFun(); };
  if(!hertoetsSpel) hertoetsStart(GRAM_PADEN[0]);
  var H = hertoetsSpel, totaal = H.rij.length;
  var kop = "<h2>" + ct("De hertoets \\ud83e\\uddca", "The recheck \\ud83e\\uddca") + "</h2>";

  if(H.i >= totaal){
    var gehaald = H.goed >= HERTOETS_EIS;
    el.innerHTML = kop +
      "<div class='feedback " + (gehaald ? "ok" : "fout") + "' id='herUitslag'>" + H.goed + " / " + totaal + "</div>" +
      "<p class='muted'>" + (gehaald
        ? ct("Gestold. Je kon het drie dagen geleden, en je kunt het nu nog. D\\u00e1t is het verschil met afvinken.",
             "Set. You could do it three days ago and you still can. That is the difference from ticking a box.")
        : ct("Nog niet gestold. Dat is geen terugval maar informatie: op de dag zelf kon je het, en dat is iets anders dan het kennen. Doe de stappen die misgingen nog een keer.",
             "Not set yet. That is not a relapse but information: you could do it on the day itself, and that is not the same as knowing it. Redo the steps that went wrong.")) + "</p>" +
      "<div class='row' style='margin-top:10px'><button class='primary' id='btnHerTerug'>" +
        ct("Terug naar het pad", "Back to the path") + "</button></div>";
    var bt = document.getElementById("btnHerTerug");
    if(bt) bt.onclick = terug;
    return;
  }

  var q = H.rij[H.i];
  var af = H.gekozen !== null;
  var goed, juist;
  if(q.soort === "betekenis"){
    juist = q.z.s === "a" ? ct("achtergrond", "background") : ct("gebeurtenis", "event");
    goed = af && H.gekozen === q.z.s;
  } else {
    juist = conjVorm(q.v, q.p, q.t);
    goed = af && stripAcc(norm(H.gekozen)) === stripAcc(norm(juist));
  }

  var html = kop +
    "<span class='kicker'>" + (H.i + 1) + "/" + totaal + " \\u00b7 " +
      ct(q.soort === "betekenis" ? "de regel" : "de vorm", q.soort === "betekenis" ? "the rule" : "the form") + "</span>";

  if(q.soort === "betekenis"){
    html += "<p class='big' style='margin:10px 0'>" + brokZin(q.z) + "</p>" +
      (af ? "" : "<div class='row' style='margin-top:6px'>" +
        "<button class='ghost her-b' data-b='a' style='flex:1; min-height:56px'>" + ct("Achtergrond", "Background") + "</button>" +
        "<button class='ghost her-b' data-b='g' style='flex:1; min-height:56px'>" + ct("Gebeurtenis", "Event") + "</button></div>");
  } else {
    html += "<div class='card' style='text-align:center; margin:10px 0'>" +
      "<p class='muted' style='margin:0 0 2px'>" + q.v.inf + " <span style='font-weight:400'>(" + conjGloss(q.v) + ")</span></p>" +
      "<p class='big' style='margin:4px 0'>" + CONJ_PRONOMBRES[q.p] + "</p>" +
      "<p class='muted' style='margin:0; font-size:.82rem'>" + conjTiempoNaam(q.t) + "</p></div>" +
      (af ? "" : "<input type='text' id='herInput' autocomplete='off' autocapitalize='off' spellcheck='false' placeholder='" +
        ct("Typ de vorm...", "Type the form...") + "' style='width:100%; padding:12px; font-size:1rem'>" +
        "<div class='row' style='margin-top:8px'><button class='primary' id='btnHerCheck'>" + ct("Nakijken", "Check") + "</button></div>");
  }

  if(af){
    html += "<div class='feedback " + (goed ? "ok" : "fout") + "'>" +
      (goed ? ct("Goed \\u2713", "Correct \\u2713") : ct("Nog niet. Het is: ", "Not yet. It is: ") + "<b>" + juist + "</b>") + "</div>" +
      "<div class='row' style='margin-top:10px'><button class='primary' id='btnHerNext'>" +
        (H.i + 1 >= totaal ? ct("Uitslag \\u2192", "Result \\u2192") : ct("Volgende \\u2192", "Next \\u2192")) + "</button></div>";
  }
  html += "<div class='row' style='margin-top:10px'><button class='mini' id='btnHerStop'>" + fx("terug") + "</button></div>";
  el.innerHTML = html;

  Array.prototype.forEach.call(el.querySelectorAll(".her-b"), function(b){
    b.onclick = function(){ hertoetsAntwoord(b.getAttribute("data-b")); };
  });
  var bc = document.getElementById("btnHerCheck");
  if(bc) bc.onclick = function(){ var i2 = document.getElementById("herInput"); hertoetsAntwoord(i2 ? i2.value : ""); };
  var inp = document.getElementById("herInput");
  if(inp){ inp.focus(); inp.onkeydown = function(e){ if(e.key === "Enter") hertoetsAntwoord(inp.value); }; }
  var bn = document.getElementById("btnHerNext");
  if(bn) bn.onclick = hertoetsVolgende;
  var bs = document.getElementById("btnHerStop");
  if(bs) bs.onclick = terug;
}

/* ================= HET PAD (v23.116) ================='''
rep(A_HER, N_HER)

# ---------------- 3. de zesde stap in het pad
A_EIS = u'''  keuze:     function(st){ return (st.beste || 0) >= 11; }
};'''
N_EIS = u'''  keuze:     function(st){ return (st.beste || 0) >= 11; },
  /* v23.117: de hertoets leest zijn eigen pot (pad.<id>) en niet die van een stap, want hij gaat
     over het hele pad. Gestold is een datum en geen score: hij wordt \\u00e9\\u00e9n keer gezet. */
  hertoets:  function(st){ return !!st.gestold; }
};'''
rep(A_EIS, N_EIS)

A_STAND = u'''  keuze:     function(st){ return st.rondes ? ct("beste ", "best ") + (st.beste || 0) + "/12" : ""; }
};'''
N_STAND = u'''  keuze:     function(st){ return st.rondes ? ct("beste ", "best ") + (st.beste || 0) + "/12" : ""; },
  hertoets:  function(st){
    if(st.gestold) return ct("gestold op ", "set on ") + st.gestold;
    if(st.pogingen) return ct("beste ", "best ") + (st.beste || 0) + "/" + HERTOETS_LEN;
    return "";
  }
};'''
rep(A_STAND, N_STAND)

A_STAP5 = u'''     {brok:"indefimperf.keuze", soort:"keuze", view:null,
      nl:"In een echte zin kiezen", en:"Choosing inside a real sentence",
      subNl:"Komt nog. Dit is de stap waar de regel en de vorm samenkomen.",
      subEn:"Coming. This is where the rule and the form come together."}
   ]}'''
N_STAP5 = u'''     {brok:"indefimperf.keuze", soort:"keuze", view:null,
      nl:"In een echte zin kiezen", en:"Choosing inside a real sentence",
      subNl:"Komt nog. Dit is de stap waar de regel en de vorm samenkomen.",
      subEn:"Coming. This is where the rule and the form come together."},
     {brok:"pad.indefimperf", soort:"hertoets", view:"hertoets",
      nl:"Gestold?", en:"Has it set?",
      subNl:"Tien gemengde opgaven, op zijn vroegst drie dagen na de rest. Pas dan is dit punt echt af.",
      subEn:"Ten mixed items, at the earliest three days after the rest. Only then is this point really done."}
   ]}'''
rep(A_STAP5, N_STAP5)

# de tijden van dit pad, zodat de hertoets weet waar hij uit put
A_TIJDEN = u'''  {id:"indefimperf",
   nl:"De verleden tijd: indefinido of imperfecto",'''
N_TIJDEN = u'''  {id:"indefimperf",
   tijden:["imperfecto", "indefinido"],
   nl:"De verleden tijd: indefinido of imperfecto",'''
rep(A_TIJDEN, N_TIJDEN)

# ---------------- 4. het pad houdt de hertoets tegen tot de wachttijd om is
A_SLOT = u'''function gramPadOpSlot(p, i){
  for(var j = 0; j < i; j++){
    var x = gramPadStap(p, j);
    if(x.bestaat && !x.af) return true;
  }
  return false;
}'''
N_SLOT = u'''function gramPadOpSlot(p, i){
  for(var j = 0; j < i; j++){
    var x = gramPadStap(p, j);
    if(x.bestaat && !x.af) return true;
  }
  /* v23.117: de hertoets zit \\u00f3\\u00f3k op slot zolang de wachttijd loopt. Dat is het hele punt: je mag
     hem niet op de dag zelf doen, want dan meet hij hetzelfde als de stappen ervoor. */
  if(p.stappen[i] && p.stappen[i].soort === "hertoets" && !padMagHertoets(p)) return true;
  return false;
}'''
rep(A_SLOT, N_SLOT)

# ---------------- 5. het padscherm vertelt wat de wachtdagen zijn
A_KLAAR = u'''  if(klaar){
    html += "<div class='feedback ok' id='padKlaar'>" +
      ct("Je hebt dit hele pad gelopen.", "You have walked this whole path.") + "</div>";
  } else if(volgende >= 0){'''
N_KLAAR = u'''  /* v23.117: tussen "gehaald" en "gestold" zit een wachttijd, en dan hoort het scherm te zeggen
     wat je in die dagen w\\u00e9l doet. Anders is wachten gewoon dood. */
  var stPad = brokLees(padId(p));
  if(padGehaald(p) && !stPad.gestold && !padMagHertoets(p)){
    padGehaaldStempel(p);
    var teGaan = padDagenTeGaan(p);
    html += "<div class='feedback bijna' id='padWacht'>" +
      ct("Gehaald. Nog " + teGaan + " " + (teGaan === 1 ? "dag" : "dagen") + " tot de hertoets.",
         "Passed. " + teGaan + " more " + (teGaan === 1 ? "day" : "days") + " until the recheck.") + "</div>" +
      "<p class='muted' style='font-size:.88rem'>" +
      ct("Dit is met opzet. Wat je vandaag kunt, weet je over drie dagen misschien niet, en alleen dat tweede telt. Aan dit punt valt nu niets te doen: doe woorden, lezen of luisteren.",
         "This is deliberate. What you can do today you may not know in three days, and only the second counts. There is nothing to do on this point right now: do words, reading or listening.") + "</p>";
  }

  if(klaar){
    html += "<div class='feedback ok' id='padKlaar'>" +
      ct("Gestold. Dit punt is echt af.", "Set. This point is really done.") + "</div>";
  } else if(volgende >= 0){'''
rep(A_KLAAR, N_KLAAR)

# ---------------- 6. de router
A_ROUTE = u'''  if(funView === "pad"){ renderFunPad(); return; }   // v23.116'''
N_ROUTE = u'''  if(funView === "pad"){ renderFunPad(); return; }   // v23.116
  if(funView === "hertoets"){ renderFunHertoets(); return; }   // v23.117'''
rep(A_ROUTE, N_ROUTE)

# ---------------- 7. gramPadGa kent de hertoets
A_GA = u'''  if(s.view === "tijdvorm"){ tijdvormSpel = null; }'''
N_GA = u'''  if(s.view === "tijdvorm"){ tijdvormSpel = null; }
  if(s.view === "hertoets"){ hertoetsStart(p); }'''
rep(A_GA, N_GA)

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
