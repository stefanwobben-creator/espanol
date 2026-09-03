#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.234 - twee adviezen worden twee regels
#
# Stefan, op mijn vier aanbevelingen: "1 en 2 dwing dit meer af. 3 ok. 4 ok."
#
# Advies 1 was: lees de kaart van de tijden één keer, niet om hem te leren maar om de woorden te
# hebben. Advies 2 was: doe minder tegelijk, kies twee onderwerpen en laat de rest liggen.
#
# Allebei stonden ze in een chatbericht, en een advies in een chatbericht is geen app-gedrag. Nu
# zijn het regels.
#
# 1. EEN TIJD DIE JE NOG NOOIT GELEZEN HEBT, WORDT NIET GEDRILD
#
# v23.233 zette de kaart van de tijden achter een knop bovenaan de Grammatica-tab. Een knop kun je
# negeren, en precies dat was de klacht: de app leert je vormen en je weet niet wat de tijd doet.
#
# Het vormenblok (de les, zes stappen per rijtje) begint nu met de uitleg van zijn eigen tijd,
# eenmalig per tijd. Je leest vier regels over wat het indefinido doet, je tikt "begrepen", en de
# oefening staat er. De tweede keer zie je die poort niet meer.
#
# Hoogstens zes keer in je leven, één per tijd. Dat is de grens tussen afdwingen en zeuren.
#
# Openklappen op de kaart zelf telt ook als gelezen: wie hem daar doorneemt hoort niet nog een keer
# gestopt te worden. De HANDELING is wat telt, niet de plek.
#
# 2. HOOGSTENS TWEE ONDERWERPEN TEGELIJK ONDERHANDEN
#
# Gemeten in Stefans logboek: 25 onderwerpen, waarvan 16 op doos 0, 1 of 2, en NUL op doos 3 of 4.
# Overal een beetje, nergens iets af. gcOpenSet() houdt namelijk alles open wat je ooit hebt
# aangeraakt (terecht: fouten moeten terug kunnen komen) en gcVandaagLijst() koos daar elke dag drie
# uit. Met zestien kandidaten betekent dat rondjes draaien.
#
# Nu is er een focus: gcFocus() houdt hoogstens twee onderwerpen vast, en een onderwerp verlaat de
# focus pas als het op doos 3 staat. Dan pas schuift het volgende uit de leervolgorde erin.
#
# WAT DIT KOST, EXPLICIET. gcVandaagLijst() had een derde plek die altijd voor iets nieuws was, met
# als reden "anders zou een slechte week je nooit meer iets nieuws laten zien". Die plek is weg. Dat
# is een echte prijs en hij is bewust betaald: de gemeten toestand is niet "te weinig nieuws" maar
# zestien halve onderwerpen. Het slot kan ook niet klemmen, want doos 3 haal je met drie schone
# beurten, en pw-focus bewijst dat een onderwerp de focus verlaat zodra het er staat.
#
# En de regel staat op het scherm. Een limiet die je niet ziet voelt als willekeur; deze zegt
# waaraan je werkt en wat er moet gebeuren voordat er iets bij komt.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.234"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function gcFocus(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # =========================================================================================
    # 1. de poort: een ongelezen tijd wordt niet gedrild
    # =========================================================================================
    rep("""var tijdenOpenNu = false;""",
"""/* ================= EEN ONGELEZEN TIJD WORDT NIET GEDRILD (v23.234) =================

   Stefan, op het advies om de kaart één keer te lezen: "dwing dit meer af."

   Terecht. v23.233 zette de kaart achter een knop, en een knop kun je negeren; precies dat wás de
   klacht. Het vormenblok begint nu met de uitleg van zijn eigen tijd, en pas daarna met de oefening.

   Eenmalig per tijd, dus hoogstens zes keer. Dat is de grens tussen afdwingen en zeuren: een poort
   die elke dag terugkomt is geen poort maar een drempel, en dan klik je hem weg zonder te lezen.

   Openklappen op de kaart zelf telt ook. De handeling is wat telt, niet de plek. */
function tijdVan(id){
  for(var i = 0; i < TIJDEN.length; i++){ if(TIJDEN[i].id === id) return TIJDEN[i]; }
  return null;
}
function tijdGelezen(id){
  try { return !!(S.tijdGelezen || {})[id]; } catch(e){ return true; }
}
function tijdLees(id){
  if(!id || !tijdVan(id)) return;
  try {
    S.tijdGelezen = S.tijdGelezen || {};
    if(!S.tijdGelezen[id]){ S.tijdGelezen[id] = today(); persist(); }
  } catch(e){}
}
/* De poort zelf: dezelfde inhoud als één rij op de kaart, maar uitgeklapt en met een knop eronder.
   Niet de hele kaart: je staat op het punt om ÉÉN tijd te oefenen, en de andere vijf zijn dan ruis. */
function tijdPoortHtml(id){
  var t = tijdVan(id);
  if(!t) return "";
  var vb = (profLang() === "nl" ? t.vb : (t.vbEn || t.vb));
  return "<div class='card'><span class='kicker'>" +
      ct("Eerst even dit", "First, this") + "</span>" +
    "<h2 style='margin-top:2px'>" + t.es + "</h2>" +
    "<p class='muted' style='margin:0 0 10px'>" + ct(t.nl, t.en) + "</p>" +
    "<p style='margin:0 0 8px'><b>" + ct("Wat doet hij?", "What does it do?") + "</b><br>" +
      ct(t.doet, t.doetEn) + "</p>" +
    "<p class='muted' style='margin:0 0 8px; font-size:.88rem'><b>" +
      ct("Je herkent hem aan:", "You spot it by:") + "</b> " + t.herken + "</p>" +
    "<ul style='margin:0 0 8px; padding-left:18px'>" +
      vb.map(function(x){ return "<li>" + x + "</li>"; }).join("") + "</ul>" +
    "<p style='margin:0 0 8px'><span class='es'>" + t.es1 + "</span> \\u00b7 " +
      "<span class='muted'>" + t.nl1 + "</span></p>" +
    "<p class='muted' style='margin:0 0 12px; font-size:.88rem'>" + ct(t.let, t.letEn) + "</p>" +
    "<div class='row'><button class='primary' id='btnTijdBegrepen'>" +
      ct("Begrepen, aan de slag", "Got it, let's go") + " \\u2192</button>" +
      "<button class='ghost' id='btnFunTerug'>" + ct("Later", "Later") + "</button></div>" +
    "<p class='muted' style='margin:10px 0 0; font-size:.8rem'>" +
      ct("Dit zie je één keer per tijd. Daarna staat de uitleg bij Grammatica.",
         "You see this once per tense. After that the explanation lives under Grammar.") + "</p>" +
    "</div>";
}
var tijdenOpenNu = false;""")

    rep("""  var L = lesSpel, x = lesRij(L.rij), v = L.v;""",
"""  /* v23.234: de poort. Een tijd die je nog nooit gelezen hebt wordt niet gedrild; eerst vier regels
     over wat hij DOET, dan pas de vormen. Eenmalig per tijd, en een rij zonder bekende tijd (een
     patroonrij binnen het presente bijvoorbeeld) draagt de tijd van zijn tijdrij, dus die is dan al
     gelezen. */
  var _poortT = null;
  try { _poortT = (lesRij(lesSpel.rij) || {}).t; } catch(e){ _poortT = null; }
  if(_poortT && tijdVan(_poortT) && !tijdGelezen(_poortT)){
    el.innerHTML = tijdPoortHtml(_poortT);
    var bTb = document.getElementById("btnTijdBegrepen");
    if(bTb) bTb.onclick = function(){ tijdLees(_poortT); renderFunLes(); };
    var bTl = document.getElementById("btnFunTerug");
    if(bTl) bTl.onclick = terug;
    return;
  }

  var L = lesSpel, x = lesRij(L.rij), v = L.v;""")

    # openklappen op de kaart telt ook als gelezen
    rep("""  return "<details class='tijdrij'><summary><b>" + t.es + "</b> \\u00b7 " +""",
"""  return "<details class='tijdrij' data-tijd='" + t.id + "'><summary><b>" + t.es + "</b> \\u00b7 " +""")

    rep("""    el.querySelectorAll("#btnTijdenTerug").forEach(function(b){
      b.onclick = function(){ tijdenOpenNu = false; renderCheat(); try { window.scrollTo(0, 0); } catch(e){} };
    });""",
"""    el.querySelectorAll("#btnTijdenTerug").forEach(function(b){
      b.onclick = function(){ tijdenOpenNu = false; renderCheat(); try { window.scrollTo(0, 0); } catch(e){} };
    });
    /* v23.234: hier lezen telt ook. Wie de kaart doorneemt hoort straks in zijn les niet nog een
       keer tegengehouden te worden; de handeling is wat telt, niet de plek. */
    el.querySelectorAll("[data-tijd]").forEach(function(d){
      d.addEventListener("toggle", function(){ if(d.open) tijdLees(d.getAttribute("data-tijd")); });
    });""")

    # =========================================================================================
    # 2. de focus: hoogstens twee onderwerpen onderhanden
    # =========================================================================================
    rep("""function gcConceptOpen(id){""",
"""/* ================= HOOGSTENS TWEE ONDERHANDEN (v23.234) =================

   Stefan, op het advies om minder tegelijk te doen: "dwing dit meer af."

   Gemeten in zijn logboek: 25 onderwerpen, 16 op doos 0, 1 of 2, en NUL op doos 3 of 4. Overal een
   beetje, nergens iets af. gcOpenSet() houdt alles open wat je ooit hebt aangeraakt, en dat is
   terecht (fouten moeten terug kunnen komen), maar gcVandaagLijst() koos daar elke dag opnieuw uit.
   Met zestien kandidaten is dat rondjes draaien.

   Een onderwerp verlaat de focus pas als het op doos 3 staat. Dat is drie schone beurten, dus het
   slot kan niet klemmen; het duurt alleen zolang als het duurt. Pas dan schuift het volgende uit de
   leervolgorde erin.

   De focus wordt BEWAARD (S.gramFocus). Elke dag opnieuw de twee zwakste kiezen zou hetzelfde
   rondjes draaien opleveren met een kleiner getal: je moet aan hetzelfde blijven werken, ook op de
   dag dat er iets anders toevallig zwakker staat. */
var GC_FOCUS_N = 2;
var GC_FOCUS_KLAAR = 3;
function gcFocusKlaar(id){
  try { return (gramLees(id).box || 0) >= GC_FOCUS_KLAAR; } catch(e){ return false; }
}
function gcFocus(){
  var open = {};
  try { open = gcOpenSet(); } catch(e){ open = {}; }
  var rij = [];
  try {
    rij = (S.gramFocus || []).filter(function(id){ return open[id] && !gcFocusKlaar(id); });
  } catch(e){ rij = []; }
  if(rij.length < GC_FOCUS_N){
    gcGeordend().forEach(function(c){
      if(rij.length >= GC_FOCUS_N) return;
      if(!open[c.id] || gcFocusKlaar(c.id) || rij.indexOf(c.id) !== -1) return;
      rij.push(c.id);
    });
  }
  try {
    if((S.gramFocus || []).join(",") !== rij.join(",")){ S.gramFocus = rij.slice(); persist(); }
  } catch(e){}
  return rij.slice();
}
function gcConceptOpen(id){""")

    rep("""  var t = today(), fout = [], due = [], nieuw = [], open = gcOpenSet();
  gcGeordend().forEach(function(c){
    var st = gramLees(c.id);
    if(!st.goed && !st.fout){ if(open[c.id]) nieuw.push(c); return; }
    if(gcStaatFout(st)){ fout.push({c:c, st:st}); return; }
    if(!st.due || st.due <= t) due.push({c:c, st:st});
  });
  function opBox(a, b){ return (a.st.box || 0) - (b.st.box || 0); }
  fout.sort(opBox); due.sort(opBox);
  // twee plekken voor wat terug moet komen, en altijd een plek voor iets nieuws:
  // anders zou een slechte week je nooit meer iets nieuws laten zien
  var uit = fout.concat(due).slice(0, 2).map(function(x){ return x.c; });
  if(nieuw.length) uit.push(nieuw[0]);
  if(!uit.length) uit = gcGeordend().filter(function(c){ return open[c.id]; }).slice(0, 3);
  return uit;""",
"""  /* v23.234: hier stond "twee plekken voor wat terug moet komen, en altijd een plek voor iets
     nieuws: anders zou een slechte week je nooit meer iets nieuws laten zien." Die derde plek is
     weg, en dat is een echte prijs.

     Hij is bewust betaald. De gemeten toestand was niet "te weinig nieuws" maar zestien halve
     onderwerpen en nul op doos 3 of 4. Wat er nu gebeurt is dat er pas iets nieuws bij komt als er
     iets af is, en dat is precies wat Stefan vroeg af te dwingen. */
  var t = today(), fout = [], due = [], rest = [], focus = {}, open = {};
  gcFocus().forEach(function(id){ focus[id] = 1; });
  try { open = gcOpenSet(); } catch(e){ open = {}; }
  gcGeordend().forEach(function(c){
    var st = gramLees(c.id);
    /* Een VERSE fout telt altijd mee, ook buiten de focus. De focus zegt waar je systematisch aan
       bouwt; iets wat gisteren misging is geen nieuw project maar een reparatie, en die hoort
       dezelfde week terug te komen. gcStaatFout() is twee dagen breed, dus dit dooft vanzelf.
       Zonder deze uitzondering zou een fout in een vrije zin pas maanden later aan de beurt zijn,
       en dan is de app niet streng maar doof. */
    if(open[c.id] && gcStaatFout(st)){ fout.push({c:c, st:st}); return; }
    if(!focus[c.id]) return;
    if(!st.goed && !st.fout){ rest.push({c:c, st:st}); return; }
    if(!st.due || st.due <= t){ due.push({c:c, st:st}); return; }
    rest.push({c:c, st:st});
  });
  function opBox(a, b){ return (a.st.box || 0) - (b.st.box || 0); }
  fout.sort(opBox); due.sort(opBox);
  return fout.concat(due).concat(rest).slice(0, GC_FOCUS_N).map(function(x){ return x.c; });""")

    # de regel staat op het scherm
    rep("""function gramHomeHtml(){ return tijdenIngangHtml() + gramRouteHtml() + gramOefenHtml(); }""",
"""/* v23.234: een limiet die je niet ziet voelt als willekeur. Deze zegt waaraan je werkt en wat er
   moet gebeuren voordat er iets bij komt. */
function gcFocusRegelHtml(){
  var rij = [];
  try { rij = gcFocus(); } catch(e){ rij = []; }
  if(!rij.length) return "";
  var namen = rij.map(function(id){
    var c = gcConcept(id);
    return "<b>" + (c ? ct(c.naam, c.naamEn) : id) + "</b>";
  }).join(ct(" en ", " and "));
  return "<div class='card' id='gcFocus' style='padding:12px 14px; margin-bottom:12px'>" +
    "<span class='kicker'>" + ct("Waar je nu aan werkt", "What you are working on") + "</span>" +
    "<p style='margin:4px 0 0'>" + namen + "</p>" +
    "<p class='muted' style='margin:6px 0 0; font-size:.85rem'>" +
      ct("Er komt pas iets nieuws bij als hier iets op doos " + GC_FOCUS_KLAAR + " staat. Minder tegelijk, verder komen.",
         "Nothing new joins until one of these reaches box " + GC_FOCUS_KLAAR + ". Fewer at a time, further along.") +
    "</p></div>";
}
function gramHomeHtml(){ return tijdenIngangHtml() + gcFocusRegelHtml() + gramRouteHtml() + gramOefenHtml(); }""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    for nodig in ["function tijdVan(", "function tijdGelezen(", "function tijdLees(",
                  "function tijdPoortHtml(", "function gcFocus(", "function gcFocusKlaar(",
                  "function gcFocusRegelHtml(", "var GC_FOCUS_N = 2", "var GC_FOCUS_KLAAR = 3",
                  "btnTijdBegrepen", "data-tijd=", "S.gramFocus"]:
        assert nodig in src, "ontbreekt: " + nodig
    for naam in ["tijdVan", "tijdGelezen", "tijdLees", "tijdPoortHtml",
                 "gcFocus", "gcFocusKlaar", "gcFocusRegelHtml"]:
        c = src.count("function " + naam + "(")
        assert c == 1, "function %s staat %d keer in het bestand" % (naam, c)
    # de derde plek voor iets nieuws is echt weg uit de dagkeuze
    assert "if(nieuw.length) uit.push(nieuw[0]);" not in src, \
        "gcVandaagLijst heeft nog steeds een losse plek voor iets nieuws"
    assert "gcFocus().forEach(function(id){ focus[id] = 1; });" in src, \
        "gcVandaagLijst kiest niet uit de focus"
    # de poort staat vóór de oefening en niet erachter
    i_poort = src.index("_poortT && tijdVan(_poortT)")
    i_les = src.index("var L = lesSpel, x = lesRij(L.rij), v = L.v;")
    assert i_poort < i_les, "de poort staat na de oefening in plaats van ervoor"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de tijdpoort staat voor het vormenblok, en de focus houdt het op twee")
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
