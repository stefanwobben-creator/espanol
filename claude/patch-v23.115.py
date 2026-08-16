#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.115: de les. Eén tijd tegelijk, en de eerste twee stappen zijn geen toets.

## Waar dit vandaan komt

Stefan, na "Welke tijd is dit?": "bijna alles, want ik word direct getoetst en alle tijden door
elkaar, het is nog steeds losse toetsjes maar geen les."

Hij heeft gelijk, en het raakt mijn eigen ontwerpregel. In het advies van 15 augustus staat R5:

    "Eerst blokken, dan spreiden. Proceduralisatie is essentially complete after the first 16-item
     block. Vamos husselt nu vanaf vraag één, en dat is gif voor proceduralisatie."

En dat is precies wat het scherm doet dat ik daarna bouwde: vijf tijden door elkaar vanaf vraag
één. Ik heb vier rondes lang meetinstrumenten gebouwd en geen les. Dit is de les.

## De ladder uit het advies, en wat er ontbrak

    stap  wat je ziet                        tabel   antwoord     bestond
    ----  --------------------------------   ------  -----------  -------
    0     dit is de imperfecto, drie zinnen  n.v.t.  geen vraag   NEE
    1     het hele rijtje, cel voor cel      zicht   geen vraag   NEE
    2     welke van deze is de wij-vorm?     zicht   kiezen       nee
    3     hablaba, ___, hablaba, ...         zicht   typen        nee
    4     nosotros + hablar = ?              weg     typen        ja (Conjugador)

De app begon bij stap 4. Stap 0 en 1 stellen geen enkele vraag, en dat is geen luiheid maar het
punt: je kunt niets ophalen wat er nog niet in zit. Retrieval practice werkt alleen op materiaal
dat ooit is ingeprent.

## Wat dit scherm is

Eén tijd tegelijk. Je kiest hem (of je komt binnen via je struikelblok uit v23.114) en dan loop je
de vijf stappen door met hetzelfde werkwoord, geblokkeerd. Geen andere tijd in beeld tot je klaar
bent.

Het aantal opgaven per stap is klein met opzet: proceduralisatie is na ongeveer zestien items
grotendeels rond, en daarna is het automatisering, en dat is spreiden en niet meer blokken. Dus de
les is kort en komt terug, in plaats van lang en eenmalig.

## Waar hij op verder bouwt

  - het rijtje komt uit conjVorm, geen enkele vervoeging staat in deze code
  - de namen komen uit CONJ_TIEMPOS (v23.108)
  - het vormkenmerk per tijd komt uit CONJ_TIEMPOS (v23.114) en is de kern van stap 0
  - de voortgang gaat naar S.brok["les.<tijd>"], naast de andere brokken, niet naar S.gram

## Wat dit expres NIET doet

Geen koppeling aan de dagles, de SRS of de Conjugador-ladder. Eerst moet blijken dat de les werkt.
Eén variabele per ronde.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.115"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.115" not in src
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


# ------------------------- 1. wat een tijd DOET hoort bij de tijd
A_LES1 = u'''   vorm:"korte uitgang, geen accent: -o, -as/-es, -a/-e, -amos/-emos/-imos",
   vormEn:"short ending, no accent: -o, -as/-es, -a/-e, -amos/-emos/-imos"},'''
N_LES1 = u'''   vorm:"korte uitgang, geen accent: -o, -as/-es, -a/-e, -amos/-emos/-imos",
   vormEn:"short ending, no accent: -o, -as/-es, -a/-e, -amos/-emos/-imos",
   doet:"Wat er nu is, wat altijd zo is, en wat je gewoonlijk doet.",
   doetEn:"What is happening now, what is always true, and what you usually do.",
   les:"hablar"},'''
rep(A_LES1, N_LES1)

A_LES2 = u'''   vorm:"twee woorden: he/has/ha/hemos/hab\\u00e9is/han + -ado of -ido",
   vormEn:"two words: he/has/ha/hemos/hab\\u00e9is/han + -ado or -ido"},'''
N_LES2 = u'''   vorm:"twee woorden: he/has/ha/hemos/hab\\u00e9is/han + -ado of -ido",
   vormEn:"two words: he/has/ha/hemos/hab\\u00e9is/han + -ado or -ido",
   doet:"Iets uit een periode die nog loopt: vandaag, deze week, dit jaar, ooit in je leven.",
   doetEn:"Something from a period that is still running: today, this week, this year, ever in your life.",
   les:"hablar"},'''
rep(A_LES2, N_LES2)

A_LES3 = u'''   vorm:"accent achteraan bij yo en \\u00e9l: -\\u00e9/-\\u00ed en -\\u00f3/-i\\u00f3. Of een onregelmatige stam zonder accent (tuve, hice, fui)",
   vormEn:"accent at the end for yo and \\u00e9l: -\\u00e9/-\\u00ed and -\\u00f3/-i\\u00f3. Or an irregular stem with no accent (tuve, hice, fui)"},'''
N_LES3 = u'''   vorm:"accent achteraan bij yo en \\u00e9l: -\\u00e9/-\\u00ed en -\\u00f3/-i\\u00f3. Of een onregelmatige stam zonder accent (tuve, hice, fui)",
   vormEn:"accent at the end for yo and \\u00e9l: -\\u00e9/-\\u00ed and -\\u00f3/-i\\u00f3. Or an irregular stem with no accent (tuve, hice, fui)",
   doet:"E\\u00e9n gebeurtenis in een afgesloten periode. Het verhaal gaat erdoor vooruit.",
   doetEn:"One event in a closed period. It moves the story forward.",
   les:"hablar"},'''
rep(A_LES3, N_LES3)

A_LES4 = u'''   vorm:"altijd -aba- of -\\u00eda- v\\u00f3\\u00f3r de uitgang. Slechts drie uitzonderingen: ser, ir, ver",
   vormEn:"always -aba- or -\\u00eda- before the ending. Only three exceptions: ser, ir, ver"},'''
N_LES4 = u'''   vorm:"altijd -aba- of -\\u00eda- v\\u00f3\\u00f3r de uitgang. Slechts drie uitzonderingen: ser, ir, ver",
   vormEn:"always -aba- or -\\u00eda- before the ending. Only three exceptions: ser, ir, ver",
   doet:"Het toneel waarop het verhaal zich afspeelt: hoe het wás, wat er steeds gebeurde, wat er aan de gang was.",
   doetEn:"The stage the story plays out on: how things were, what kept happening, what was going on.",
   les:"hablar"},'''
rep(A_LES4, N_LES4)

A_LES5 = u'''   vorm:"de klinker is omgewisseld: -ar krijgt een e (hable), -er en -ir krijgen een a (aprenda)",
   vormEn:"the vowel is swapped: -ar takes an e (hable), -er and -ir take an a (aprenda)"}'''
N_LES5 = u'''   vorm:"de klinker is omgewisseld: -ar krijgt een e (hable), -er en -ir krijgen een a (aprenda)",
   vormEn:"the vowel is swapped: -ar takes an e (hable), -er and -ir take an a (aprenda)",
   doet:"Geen feit maar een wens, twijfel of gevoel erover. Komt bijna altijd na \\u201eque\\u201d.",
   doetEn:"Not a fact but a wish, a doubt or a feeling about it. Almost always after \\u201cque\\u201d.",
   les:"hablar"}'''
rep(A_LES5, N_LES5)

# ------------------------------------------------------------- 2. de les zelf
A_LES = u'''/* ================= WELKE TIJD IS DIT? (v23.113) ================='''
N_LES = u'''/* ================= DE LES (v23.115) =================

   Stefan, na vier rondes meetinstrumenten: "ik word direct getoetst en alle tijden door elkaar,
   het is nog steeds losse toetsjes maar geen les."

   Hij heeft gelijk, en het raakt regel R5 uit mijn eigen ontwerpadvies: eerst blokken, dan
   spreiden. Elk scherm in deze app begint bij stap 4 van de ladder (produceren, tabel weg) en
   hutselt alles door elkaar. Stap 0 en 1 stelden nergens een vraag, en dat is nou juist het punt:
   je kunt niets ophalen wat er nog niet in zit.

       stap 0  ONTMOETEN   wat deze tijd doet en waaraan je hem ziet   geen vraag
       stap 1  OPBOUWEN    het hele rijtje, cel voor cel               geen vraag
       stap 2  HERKENNEN   welke van deze vier is de wij-vorm?         tabel zichtbaar
       stap 3  ÉÉN GAT     hablaba, ___, hablaba, hablábamos           tabel zichtbaar
       stap 4  LOSSE CEL   nosotros + hablar = ?                       tabel weg, typen

   Eén tijd tegelijk. Geen andere tijd in beeld tot je klaar bent. Kort met opzet: proceduralisatie
   is na ongeveer zestien items grotendeels rond (DeKeyser & Suzuki), en daarna is het automatiseren
   en dus spreiden, niet meer blokken. De les hoort kort te zijn en terug te komen.

   Alles komt uit conjVorm en CONJ_TIEMPOS. Geen enkele vervoeging staat in deze code. */
var LES_STAPPEN = ["ontmoeten", "opbouwen", "herkennen", "gat", "cel"];
var lesSpel = null;

function lesId(t){ return "les." + t; }
function lesWerkwoord(t){
  var x = conjTiempo(t);
  var naam = (x && x.les) || "hablar";
  var v = VERBOS.filter(function(w){ return w.inf === naam; })[0];
  return v || conjVerbPool(t)[0] || VERBOS[0];
}
function lesStart(t){
  var v = lesWerkwoord(t);
  lesSpel = {t:t, v:v, stap:0, i:0, goed:0, fout:0, gekozen:null, getypt:"", af:false, opties:null};
  return lesSpel;
}
/* De opgaven van stap 2 en 3: vier personen, zodat de les kort blijft. Stap 4 doet er zes, want
   dan is de tabel weg en telt elke cel. Samen veertien opgaven, dicht bij de zestien waarna
   proceduralisatie grotendeels rond is. */
function lesOpgaven(stap){ return stap === 4 ? 6 : 4; }
function lesPersoonRij(stap){
  var alle = [0, 1, 2, 3, 4, 5];
  return stap === 4 ? alle : [0, 1, 3, 5];
}
function lesKlaar(t){
  var st = brokLees(lesId(t));
  return (st.stapMax || 0) >= LES_STAPPEN.length - 1;
}
function lesStapAf(){
  if(!lesSpel) return;
  var st = brokLees(lesId(lesSpel.t));
  st.stapMax = Math.max(st.stapMax || 0, lesSpel.stap);
  st.laatst = today();
  S.brok = S.brok || {};
  S.brok[lesId(lesSpel.t)] = st;
  try { persist(); } catch(e){}
}

function lesTabelHtml(v, t, verberg){
  return "<table style='width:100%; margin:8px 0'>" +
    CONJ_PRONOMBRES.map(function(pr, i){
      var toon = (verberg === i) ? "<b>___</b>" : conjVorm(v, i, t);
      return "<tr><td class='muted' style='font-size:.85rem; width:45%'>" + pr + "</td><td>" + toon + "</td></tr>";
    }).join("") + "</table>";
}

function renderFunLes(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var terug = function(){ funView = null; lesSpel = null; renderFun(); };

  /* geen tijd gekozen: het keuzescherm. Je struikelblok uit v23.114 staat vooraan, want dat is de
     tijd waar je werk zit. */
  if(!lesSpel){
    var open = conjOpenTijden();
    var w = tijdvormTopVerwar();
    var aanbevolen = w ? w.getoond : null;
    el.innerHTML = "<h2>" + ct("De les \\ud83d\\udcd6", "The lesson \\ud83d\\udcd6") + "</h2>" +
      "<p class='muted'>" + ct("E\\u00e9n tijd tegelijk, in vijf stappen. De eerste twee stellen geen vraag: eerst zien, dan pas ophalen.",
                               "One tense at a time, in five steps. The first two ask nothing: see it first, retrieve it later.") + "</p>" +
      (aanbevolen && conjTiempo(aanbevolen)
        ? "<p class='muted' id='lesAanbevolen' style='font-size:.9rem'>" +
            ct("Op grond van \\u201eWelke tijd is dit?\\u201d zou ik met <b>" + conjTiempo(aanbevolen).es + "</b> beginnen.",
               "Based on \\u201cWhich tense is this?\\u201d I would start with <b>" + conjTiempo(aanbevolen).es + "</b>.") + "</p>"
        : "") +
      "<div id='lesKeuze' style='display:flex; flex-direction:column; gap:8px; margin-top:8px'>" +
        open.map(function(t){
          var x = conjTiempo(t);
          var st = brokLees(lesId(t));
          var merk = lesKlaar(t) ? " \\u2713" : (st.stapMax ? " \\u00b7 " + ct("stap ", "step ") + ((st.stapMax || 0) + 1) + "/5" : "");
          return "<button type='button' class='" + (t === aanbevolen ? "primary" : "ghost") + " les-t' data-t='" + t + "' style='min-height:52px'>" +
            (x ? x.es : t) + merk + "<br><span class='muted' style='font-weight:400; font-size:.78rem'>" + (x ? ct(x.nl, x.en) : "") + "</span></button>";
        }).join("") + "</div>" +
      "<div class='row' style='margin-top:10px'><button class='mini' id='btnFunTerug'>" + fx("terug") + "</button></div>";
    Array.prototype.forEach.call(el.querySelectorAll(".les-t"), function(b){
      b.onclick = function(){ lesStart(b.getAttribute("data-t")); renderFunLes(); };
    });
    var tb0 = document.getElementById("btnFunTerug");
    if(tb0) tb0.onclick = terug;
    return;
  }

  var L = lesSpel, x = conjTiempo(L.t), v = L.v;
  var kop = "<h2>" + (x ? x.es : L.t) + " \\ud83d\\udcd6</h2>" +
    "<span class='kicker' id='lesKicker'>" + ct("Stap ", "Step ") + (L.stap + 1) + "/5 \\u00b7 " +
      ct(["ontmoeten","opbouwen","herkennen","\\u00e9\\u00e9n gat","losse cel"][L.stap],
         ["meet it","build it","recognise","one gap","single cell"][L.stap]) + "</span>";
  var html = kop;

  // ---- stap 0: ontmoeten. Geen vraag. ----
  if(L.stap === 0){
    html += "<div class='card' style='margin:10px 0'>" +
      "<p style='margin:0 0 8px'><b>" + ct("Wat doet hij?", "What does it do?") + "</b><br>" + ct(x.doet, x.doetEn) + "</p>" +
      "<p style='margin:0 0 8px'><b>" + ct("Waaraan zie je hem?", "How do you spot it?") + "</b><br>" + ct(x.vorm, x.vormEn) + "</p>" +
      "<p class='muted' style='margin:0'><b>" + x.vb + "</b> = " + ct(x.vbNl, x.vbEn) + "</p></div>" +
      "<p class='muted' style='font-size:.85rem'>" +
        ct("Er komt hier geen vraag. Lees het, dan gaan we het rijtje bekijken.",
           "There is no question here. Read it, then we look at the row.") + "</p>" +
      "<div class='row' style='margin-top:10px'><button class='primary' id='btnLesVerder'>" +
        ct("Laat het rijtje zien \\u2192", "Show me the row \\u2192") + "</button></div>";
  }

  // ---- stap 1: opbouwen. Ook geen vraag. ----
  else if(L.stap === 1){
    html += "<p class='muted'>" + ct("Het hele rijtje van <b>" + v.inf + "</b> (" + conjGloss(v) + "). Lees het hardop, van boven naar beneden.",
                                     "The whole row for <b>" + v.inf + "</b> (" + conjGloss(v) + "). Read it out loud, top to bottom.") + "</p>" +
      "<div class='card' id='lesRijtje'>" + lesTabelHtml(v, L.t, -1) + "</div>" +
      "<p class='muted' style='font-size:.85rem'>" + ct(x.vorm, x.vormEn) + "</p>" +
      "<div class='row' style='margin-top:10px'><button class='primary' id='btnLesVerder'>" +
        ct("Gelezen \\u2192", "Read it \\u2192") + "</button></div>";
  }

  // ---- stap 2, 3, 4: nu pas vragen ----
  else {
    var rij = lesPersoonRij(L.stap);
    var n = lesOpgaven(L.stap);
    if(L.i >= n){
      var gehaald = L.goed >= n - 1;
      html += "<div class='feedback " + (gehaald ? "ok" : "bijna") + "'>" + L.goed + " / " + n + "</div>" +
        "<p class='muted'>" + (gehaald
          ? ct("Deze stap zit. Door naar de volgende.", "This step is in. On to the next.")
          : ct("Nog niet helemaal. Deze stap nog een keer is geen straf: dat is precies hoe het erin gaat.",
               "Not quite. Doing this step again is not a punishment: that is exactly how it sinks in.")) + "</p>" +
        "<div class='row' style='margin-top:10px'>" +
          (gehaald && L.stap < LES_STAPPEN.length - 1
            ? "<button class='primary' id='btnLesVerder'>" + ct("Volgende stap \\u2192", "Next step \\u2192") + "</button>"
            : "") +
          (gehaald && L.stap >= LES_STAPPEN.length - 1
            ? "<button class='primary' id='btnLesKlaar'>" + ct("Klaar \\u2713", "Done \\u2713") + "</button>"
            : "") +
          "<button class='ghost' id='btnLesOpnieuw'>" + ct("Deze stap opnieuw", "This step again") + "</button></div>";
      el.innerHTML = html;
      var bv = document.getElementById("btnLesVerder");
      if(bv) bv.onclick = function(){ lesStapAf(); L.stap++; L.i = 0; L.goed = 0; L.gekozen = null; L.opties = null; renderFunLes(); };
      var bk = document.getElementById("btnLesKlaar");
      if(bk) bk.onclick = function(){ lesStapAf(); lesSpel = null; renderFunLes(); };
      var bo = document.getElementById("btnLesOpnieuw");
      if(bo) bo.onclick = function(){ L.i = 0; L.goed = 0; L.gekozen = null; L.opties = null; renderFunLes(); };
      return;
    }

    var p = rij[L.i % rij.length];
    var goedeVorm = conjVorm(v, p, L.t);
    var af = L.gekozen !== null;
    var isGoed = af && norm(String(L.gekozen)) === norm(goedeVorm);

    if(L.stap === 2){
      // herkennen, tabel zichtbaar, kiezen uit de zes vormen van DEZE tijd (niet uit andere tijden:
      // dat is stap 4-materiaal en hier gaat het om het rijtje zelf)
      if(!L.opties) L.opties = geschud(conjAlleVormen(v, L.t).filter(function(f, i, a){ return a.indexOf(f) === i; })).slice(0, 4);
      if(L.opties.indexOf(goedeVorm) === -1) L.opties = geschud([goedeVorm].concat(L.opties.slice(0, 3)));
      html += "<p class='muted'>" + ct("Welke vorm hoort bij <b>" + CONJ_PRONOMBRES[p] + "</b>?",
                                       "Which form goes with <b>" + CONJ_PRONOMBRES[p] + "</b>?") + "</p>" +
        "<div class='card'>" + lesTabelHtml(v, L.t, -1) + "</div>" +
        (af ? "" : "<div id='lesOpties' style='display:flex; flex-direction:column; gap:8px; margin-top:6px'>" +
          L.opties.map(function(o){ return "<button type='button' class='ghost les-o' data-o='" + o + "'>" + o + "</button>"; }).join("") + "</div>");
    } else {
      var verberg = (L.stap === 3) ? p : -1;
      html += "<p class='muted'>" + (L.stap === 3
          ? ct("Vul het gat in: <b>" + CONJ_PRONOMBRES[p] + "</b>", "Fill the gap: <b>" + CONJ_PRONOMBRES[p] + "</b>")
          : ct("Zonder tabel. <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + v.inf + "</b>, in de " + x.es + ".",
               "No table. <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + v.inf + "</b>, in the " + x.es + ".")) + "</p>" +
        (L.stap === 3 ? "<div class='card'>" + lesTabelHtml(v, L.t, verberg) + "</div>" : "") +
        (af ? "" : "<input type='text' id='lesInput' autocomplete='off' autocapitalize='off' spellcheck='false' placeholder='" +
             ct("Typ de vorm...", "Type the form...") + "' style='width:100%; padding:12px; font-size:1rem'>" +
           "<div class='row' style='margin-top:8px'><button class='primary' id='btnLesCheck'>" + ct("Nakijken", "Check") + "</button></div>");
    }

    if(af){
      html += "<div class='feedback " + (isGoed ? "ok" : "fout") + "'>" +
        (isGoed ? ct("Goed \\u2713", "Correct \\u2713")
                : ct("Nog niet. Het is: ", "Not yet. It is: ") + "<b>" + goedeVorm + "</b>") + "</div>" +
        "<div class='row' style='margin-top:10px'><button class='primary' id='btnLesNext'>" +
          (L.i + 1 >= n ? ct("Uitslag \\u2192", "Result \\u2192") : ct("Volgende \\u2192", "Next \\u2192")) + "</button></div>";
    }
    html += "<div class='row' style='margin-top:10px'><button class='mini' id='btnLesStop'>" + fx("terug") + "</button></div>";
    el.innerHTML = html;

    Array.prototype.forEach.call(el.querySelectorAll(".les-o"), function(b){
      b.onclick = function(){ lesAntwoord(b.getAttribute("data-o")); };
    });
    var bc = document.getElementById("btnLesCheck");
    if(bc) bc.onclick = function(){ var inp = document.getElementById("lesInput"); lesAntwoord(inp ? inp.value : ""); };
    var inp2 = document.getElementById("lesInput");
    if(inp2){ inp2.focus(); inp2.onkeydown = function(e){ if(e.key === "Enter") lesAntwoord(inp2.value); }; }
    var bn = document.getElementById("btnLesNext");
    if(bn) bn.onclick = function(){ L.i++; L.gekozen = null; L.opties = null; renderFunLes(); };
    var bs = document.getElementById("btnLesStop");
    if(bs) bs.onclick = terug;
    return;
  }

  html += "<div class='row' style='margin-top:10px'><button class='mini' id='btnLesStop'>" + fx("terug") + "</button></div>";
  el.innerHTML = html;
  var bv2 = document.getElementById("btnLesVerder");
  if(bv2) bv2.onclick = function(){ lesStapAf(); L.stap++; L.i = 0; L.goed = 0; renderFunLes(); };
  var bs2 = document.getElementById("btnLesStop");
  if(bs2) bs2.onclick = terug;
}

function lesAntwoord(gegeven){
  if(!lesSpel || lesSpel.gekozen !== null) return;
  var g = String(gegeven || "").trim();
  if(!g) return;
  lesSpel.gekozen = g;
  var p = lesPersoonRij(lesSpel.stap)[lesSpel.i % lesPersoonRij(lesSpel.stap).length];
  var goedeVorm = conjVorm(lesSpel.v, p, lesSpel.t);
  // zelfde soepelheid als de Conjugador: accenten mogen missen
  if(stripAcc(norm(g)) === stripAcc(norm(goedeVorm))) lesSpel.goed++; else lesSpel.fout++;
  renderFunLes();
}

/* ================= WELKE TIJD IS DIT? (v23.113) ================='''
rep(A_LES, N_LES)

# ============================================================ de tegel
A_TEGEL = u'''    /* v23.113: de tweede helft van de omkering. Wie is dit? vraagt de persoon, deze de tijd. */'''
N_TEGEL = u'''    /* v23.115: geen meting maar een les, en daarom staat hij bovenaan. */
    {v:"les",     id:"ftLes",     e:"\\ud83d\\udcd6",            t:ct("De les","The lesson"), s:ct("E\\u00e9n tijd tegelijk, in vijf stappen. De eerste twee stellen geen vraag.","One tense at a time, in five steps. The first two ask nothing."), gezien:false, verse:function(){ lesSpel = null; }},
    /* v23.113: de tweede helft van de omkering. Wie is dit? vraagt de persoon, deze de tijd. */'''
rep(A_TEGEL, N_TEGEL)

# ============================================================ de router
A_ROUTE = u'''  if(funView === "tijdvorm"){ renderFunTijdvorm(); return; }   // v23.113'''
N_ROUTE = u'''  if(funView === "tijdvorm"){ renderFunTijdvorm(); return; }   // v23.113
  if(funView === "les"){ renderFunLes(); return; }   // v23.115'''
rep(A_ROUTE, N_ROUTE)

# ============================================================ uit de dagportie
A_DAG = u'''var DAGSPEL_UIT = {avt:1, duel:1, brok:1, omkeer:1, tijdvorm:1};'''
N_DAG = u'''var DAGSPEL_UIT = {avt:1, duel:1, brok:1, omkeer:1, tijdvorm:1, les:1};'''
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
