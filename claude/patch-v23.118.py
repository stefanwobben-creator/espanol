#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.118: stap 4b, de overdracht. Ken je het patroon, of ken je hablar?

## Waarom

Wie alleen *hablar* in het imperfecto kan, kent een woord en geen patroon. Procedurele kennis is
skill-specifiek en draagt slecht over (DeKeyser & Suzuki), dus overdracht naar ongeziene
werkwoorden is precies wat je moet meten voordat "gehaald" iets betekent.

De les liep tot nu toe van stap 0 tot en met 4 op één werkwoord. Vijf stappen lang hetzelfde woord,
en dan heette het af. Dit is de stap die dat controleert.

## Wat het is

Zes opgaven, tabel weg, typen, met werkwoorden die je in stap 1 tot en met 4 niet gezien hebt.
Alle zes de personen komen langs.

## Twee keuzes die het meten scherp houden

**Alleen regelmatige werkwoorden.** De bedoeling is te toetsen of je het patroon kunt toepassen. Gooi
je *tuve* ertussen, dan meet deze stap patroon én uitzondering tegelijk, en dan zegt een fout weer
niet welke van de twee ontbrak. Dat is de klasse fout waar deze hele verbouwing over gaat. De
uitzonderingen krijgen hun eigen plek in ronde 4 (de woord-SRS).

**Alleen dezelfde groep.** Nog niet: overdracht van -ar naar -er. Dat is een andere sprong, en die
hoort bij ronde 3 waarin de les zijn groepen leert kennen. Nu blijft het binnen de groep van het
leswerkwoord.

## Waarom zes opgaven en niet zes werkwoorden

Gemeten hoeveel ongeziene regelmatige werkwoorden van dezelfde groep er zijn:

    imperfecto   8      perfecto     8      indefinido   4
    presente     3      subjuntivo   3

In het presente zijn dat er drie (trabajar, estudiar, comprar). Zes verschillende werkwoorden kan
dus niet. Zes opgaven met alle zes de personen wel: de werkwoorden rouleren, de personen niet.

## Onderweg opgeruimd

LES_STAPPEN was een lijst met ids, en de namen stonden als twee losse arrays in de rendercode, en
"/5" stond met de hand in twee teksten. Vijf plekken die wisten hoeveel stappen er zijn. Nu één:
LES_STAPPEN draagt zijn eigen namen en iedereen leest de lengte daaruit. Dat is dezelfde fout die
pw-pad in v23.117 omver haalde.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.118"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.118" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


# v23.120: alleen vooruit, ook als de app-wijziging nog moet gebeuren. Hiervoor stond hier
# "DOE_APP or ...", en toen de avondrun versie.txt naar v23.119 had gezet zette deze patch hem
# terug naar v23.118. Het nummer hoort monotoon te zijn: staat er al iets nieuwers, laat staan.
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


# ------------- 1. de stappen dragen hun eigen naam, en er komt er één bij
A_STAPPEN = u'''var LES_STAPPEN = ["ontmoeten", "opbouwen", "herkennen", "gat", "cel"];
var lesSpel = null;'''
N_STAPPEN = u'''/* v23.118: de stappen droegen hun naam niet zelf. De namen stonden als twee losse arrays in de
   rendercode en "/5" stond met de hand in twee teksten: vijf plekken die wisten hoeveel stappen er
   zijn. Nu één. Dezelfde fout haalde pw-pad om toen de hertoets erbij kwam. */
var LES_STAPPEN = [
  {id:"ontmoeten", nl:"ontmoeten",  en:"meet it"},
  {id:"opbouwen",  nl:"opbouwen",   en:"build it"},
  {id:"herkennen", nl:"herkennen",  en:"recognise"},
  {id:"gat",       nl:"\\u00e9\\u00e9n gat", en:"one gap"},
  {id:"cel",       nl:"losse cel",  en:"single cell"},
  /* v23.118: het bewijs. Wie alleen hablar kan, kent een woord en geen patroon. */
  {id:"overdracht", nl:"nieuwe werkwoorden", en:"new verbs"}
];
var lesSpel = null;

/* Volgt dit werkwoord het regelmatige patroon van zijn eigen groep IN DEZE TIJD? conjRegelmatig()
   hiernaast kijkt alleen naar het presente; voor de overdrachtsstap moet het per tijd. Gemeten
   verhoudingen: imperfecto 30 regelmatig om 3, indefinido 13 om 20, presente 11 om 22. */
var LES_MODEL = {ar:"hablar", er:"comer", ir:"vivir"};
function conjRegelmatigIn(v, t){
  var m = VERBOS.filter(function(w){ return w.inf === LES_MODEL[conjGroep(v)]; })[0];
  if(!m || !conjHeeftTijd(v, t) || !conjHeeftTijd(m, t)) return false;
  var s = v.inf.slice(0, -2), ms = m.inf.slice(0, -2);
  var verwacht = conjAlleVormen(m, t).map(function(f){ return f.split(ms).join(s); });
  return JSON.stringify(verwacht) === JSON.stringify(conjAlleVormen(v, t));
}
/* De werkwoorden voor stap 4b: ongezien (niet het leswerkwoord), regelmatig in deze tijd, en uit
   dezelfde groep. Dat laatste omdat overdracht van -ar naar -er een andere sprong is; die hoort bij
   de groepen-as van de volgende ronde. */
function lesOverdrachtPool(t, lesV){
  return VERBOS.filter(function(v){
    return v.inf !== lesV.inf && conjGroep(v) === conjGroep(lesV) && conjRegelmatigIn(v, t);
  });
}'''
rep(A_STAPPEN, N_STAPPEN)

# ------------------------------------ 2. de opgaven van de nieuwe stap
A_OPG = u'''function lesOpgaven(stap){ return stap === 4 ? 6 : 4; }
function lesPersoonRij(stap){
  var alle = [0, 1, 2, 3, 4, 5];
  return stap === 4 ? alle : [0, 1, 3, 5];
}'''
N_OPG = u'''function lesStapId(stap){ return (LES_STAPPEN[stap] || {}).id; }
function lesOpgaven(stap){
  var id = lesStapId(stap);
  return (id === "cel" || id === "overdracht") ? 6 : 4;
}
function lesPersoonRij(stap){
  var alle = [0, 1, 2, 3, 4, 5];
  return lesOpgaven(stap) === 6 ? alle : [0, 1, 3, 5];
}
/* Zes opgaven, alle zes de personen, met ongeziene werkwoorden. In het presente zijn er maar drie
   ongeziene regelmatige -ar werkwoorden (trabajar, estudiar, comprar), dus zes verschillende
   werkwoorden kan niet. De werkwoorden rouleren, de personen niet. */
function lesOverdrachtRij(t, lesV){
  var pool = geschud(lesOverdrachtPool(t, lesV));
  var pers = geschud([0, 1, 2, 3, 4, 5]);
  if(!pool.length) return [];
  return pers.map(function(p, i){ return {v:pool[i % pool.length], p:p}; });
}'''
rep(A_OPG, N_OPG)

# ------------------------------------ 3. de ronde onthoudt zijn werkwoorden
A_START = u'''function lesStart(t){
  var v = lesWerkwoord(t);
  lesSpel = {t:t, v:v, stap:0, i:0, goed:0, fout:0, gekozen:null, getypt:"", af:false, opties:null};
  return lesSpel;
}'''
N_START = u'''function lesStart(t){
  var v = lesWerkwoord(t);
  lesSpel = {t:t, v:v, stap:0, i:0, goed:0, fout:0, gekozen:null, getypt:"", af:false, opties:null, over:null};
  return lesSpel;
}
/* De rij van stap 4b wordt \\u00e9\\u00e9n keer per doorloop gemaakt en vastgehouden, anders zou elke render
   een ander werkwoord kunnen tonen dan het antwoord dat je net gaf. */
function lesOverNu(){
  if(!lesSpel) return null;
  if(!lesSpel.over) lesSpel.over = lesOverdrachtRij(lesSpel.t, lesSpel.v);
  return lesSpel.over;
}
/* Bij stap 4b hoort de opgave bij het werkwoord uit die rij; bij alle andere stappen bij het
   leswerkwoord. E\\u00e9n plek die dat weet, zodat het scherm en de nakijker niet uit elkaar lopen. */
function lesOpgaveNu(){
  if(!lesSpel) return null;
  var rij = lesPersoonRij(lesSpel.stap);
  if(lesStapId(lesSpel.stap) === "overdracht"){
    var o = lesOverNu();
    return o.length ? o[lesSpel.i % o.length] : null;
  }
  return {v:lesSpel.v, p:rij[lesSpel.i % rij.length]};
}'''
rep(A_START, N_START)

# ------------------------------------ 4. de nakijker leest dezelfde opgave
A_ANTW = u'''function lesAntwoord(gegeven){
  if(!lesSpel || lesSpel.gekozen !== null) return;
  var g = String(gegeven || "").trim();
  if(!g) return;
  lesSpel.gekozen = g;
  var p = lesPersoonRij(lesSpel.stap)[lesSpel.i % lesPersoonRij(lesSpel.stap).length];
  var goedeVorm = conjVorm(lesSpel.v, p, lesSpel.t);
  // zelfde soepelheid als de Conjugador: accenten mogen missen
  if(stripAcc(norm(g)) === stripAcc(norm(goedeVorm))) lesSpel.goed++; else lesSpel.fout++;
  renderFunLes();
}'''
N_ANTW = u'''function lesAntwoord(gegeven){
  if(!lesSpel || lesSpel.gekozen !== null) return;
  var g = String(gegeven || "").trim();
  if(!g) return;
  lesSpel.gekozen = g;
  var q = lesOpgaveNu();
  if(!q) return;
  var goedeVorm = conjVorm(q.v, q.p, lesSpel.t);
  // zelfde soepelheid als de Conjugador: accenten mogen missen
  if(stripAcc(norm(g)) === stripAcc(norm(goedeVorm))) lesSpel.goed++; else lesSpel.fout++;
  renderFunLes();
}'''
rep(A_ANTW, N_ANTW)

# ------------------------------------ 5. de kicker leest de stapnaam uit de data
A_KICK = u'''  var kop = "<h2>" + (x ? x.es : L.t) + " \\ud83d\\udcd6</h2>" +
    "<span class='kicker' id='lesKicker'>" + ct("Stap ", "Step ") + (L.stap + 1) + "/5 \\u00b7 " +
      ct(["ontmoeten","opbouwen","herkennen","\\u00e9\\u00e9n gat","losse cel"][L.stap],
         ["meet it","build it","recognise","one gap","single cell"][L.stap]) + "</span>";'''
N_KICK = u'''  var sN = LES_STAPPEN[L.stap] || {};
  var kop = "<h2>" + (x ? x.es : L.t) + " \\ud83d\\udcd6</h2>" +
    "<span class='kicker' id='lesKicker'>" + ct("Stap ", "Step ") + (L.stap + 1) + "/" + LES_STAPPEN.length +
      " \\u00b7 " + ct(sN.nl || "", sN.en || "") + "</span>";'''
rep(A_KICK, N_KICK)

A_STAND = u'''  les:       function(st){ return st.stapMax !== undefined ? ct("stap ", "step ") + ((st.stapMax || 0) + 1) + "/5" : ""; },'''
N_STAND = u'''  les:       function(st){ return st.stapMax !== undefined ? ct("stap ", "step ") + ((st.stapMax || 0) + 1) + "/" + LES_STAPPEN.length : ""; },'''
rep(A_STAND, N_STAND)

A_MERK = u'''          var merk = lesKlaar(t) ? " \\u2713" : (st.stapMax ? " \\u00b7 " + ct("stap ", "step ") + ((st.stapMax || 0) + 1) + "/5" : "");'''
N_MERK = u'''          var merk = lesKlaar(t) ? " \\u2713" : (st.stapMax ? " \\u00b7 " + ct("stap ", "step ") + ((st.stapMax || 0) + 1) + "/" + LES_STAPPEN.length : "");'''
rep(A_MERK, N_MERK)

# ------------------------------------ 6. het scherm van stap 4b
A_SCHERM = u'''    var p = rij[L.i % rij.length];
    var goedeVorm = conjVorm(v, p, L.t);
    var af = L.gekozen !== null;
    var isGoed = af && norm(String(L.gekozen)) === norm(goedeVorm);

    if(L.stap === 2){'''
N_SCHERM = u'''    var q = lesOpgaveNu();
    /* Geen ongeziene werkwoorden beschikbaar zou een lege stap opleveren. Gemeten: overal minstens
       drie, dus dit hoort niet te gebeuren; als het toch gebeurt zeggen we het in plaats van een
       leeg scherm te tonen. */
    if(!q){
      el.innerHTML = kop + "<p class='muted'>" +
        ct("Er zijn hier geen andere regelmatige werkwoorden om mee te oefenen.",
           "There are no other regular verbs to practise with here.") + "</p>" +
        "<div class='row' style='margin-top:10px'><button class='primary' id='btnLesVerder'>" +
          ct("Overslaan \\u2192", "Skip \\u2192") + "</button></div>";
      var bx = document.getElementById("btnLesVerder");
      if(bx) bx.onclick = function(){ lesStapAf(); L.stap++; L.i = 0; L.goed = 0; renderFunLes(); };
      return;
    }
    var p = q.p, qv = q.v;
    var goedeVorm = conjVorm(qv, p, L.t);
    var af = L.gekozen !== null;
    var isGoed = af && norm(String(L.gekozen)) === norm(goedeVorm);

    if(lesStapId(L.stap) === "overdracht"){
      html += "<p class='muted'>" +
        (L.i === 0
          ? ct("Nu met werkwoorden die je in deze les niet gezien hebt. Hier blijkt of je het patroon kent of alleen " + v.inf + ".",
               "Now with verbs you have not seen in this lesson. This is where it shows whether you know the pattern or just " + v.inf + ".")
          : ct("Zonder tabel. <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + qv.inf + "</b>.",
               "No table. <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + qv.inf + "</b>.")) + "</p>" +
        "<div class='card' style='text-align:center; margin:10px 0'>" +
          "<p class='muted' style='margin:0 0 2px' id='lesOverInf'>" + qv.inf +
            " <span style='font-weight:400'>(" + conjGloss(qv) + ")</span></p>" +
          "<p class='big' style='margin:4px 0'>" + CONJ_PRONOMBRES[p] + "</p>" +
          "<p class='muted' style='margin:0; font-size:.8rem'>" + conjTiempoNaam(L.t) + "</p></div>" +
        (af ? "" : "<input type='text' id='lesInput' autocomplete='off' autocapitalize='off' spellcheck='false' placeholder='" +
             ct("Typ de vorm...", "Type the form...") + "' style='width:100%; padding:12px; font-size:1rem'>" +
           "<div class='row' style='margin-top:8px'><button class='primary' id='btnLesCheck'>" + ct("Nakijken", "Check") + "</button></div>");
    }
    else if(L.stap === 2){'''
rep(A_SCHERM, N_SCHERM)

# het typpad van stap 3 en 4 mag stap 4b niet meer opnieuw tekenen
A_ELSE = u'''    } else {
      var verberg = (L.stap === 3) ? p : -1;'''
N_ELSE = u'''    } else {
      var verberg = (lesStapId(L.stap) === "gat") ? p : -1;'''
rep(A_ELSE, N_ELSE)

A_GAT = u'''      html += "<p class='muted'>" + (L.stap === 3
          ? ct("Vul het gat in: <b>" + CONJ_PRONOMBRES[p] + "</b>", "Fill the gap: <b>" + CONJ_PRONOMBRES[p] + "</b>")
          : ct("Zonder tabel. <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + v.inf + "</b>, in de " + x.es + ".",
               "No table. <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + v.inf + "</b>, in the " + x.es + ".")) + "</p>" +
        (L.stap === 3 ? "<div class='card'>" + lesTabelHtml(v, L.t, verberg) + "</div>" : "") +'''
N_GAT = u'''      html += "<p class='muted'>" + (verberg >= 0
          ? ct("Vul het gat in: <b>" + CONJ_PRONOMBRES[p] + "</b>", "Fill the gap: <b>" + CONJ_PRONOMBRES[p] + "</b>")
          : ct("Zonder tabel. <b>" + CONJ_PRONOMBRES[p] + "</b> van <b>" + v.inf + "</b>, in de " + x.es + ".",
               "No table. <b>" + CONJ_PRONOMBRES[p] + "</b> of <b>" + v.inf + "</b>, in the " + x.es + ".")) + "</p>" +
        (verberg >= 0 ? "<div class='card'>" + lesTabelHtml(v, L.t, verberg) + "</div>" : "") +'''
rep(A_GAT, N_GAT)

# de rij van stap 4b opnieuw maken bij "deze stap opnieuw" en bij "volgende stap"
A_RESET = u'''      if(bv) bv.onclick = function(){ lesStapAf(); L.stap++; L.i = 0; L.goed = 0; L.gekozen = null; L.opties = null; renderFunLes(); };'''
N_RESET = u'''      if(bv) bv.onclick = function(){ lesStapAf(); L.stap++; L.i = 0; L.goed = 0; L.gekozen = null; L.opties = null; L.over = null; renderFunLes(); };'''
rep(A_RESET, N_RESET)

A_RESET2 = u'''      if(bo) bo.onclick = function(){ L.i = 0; L.goed = 0; L.gekozen = null; L.opties = null; renderFunLes(); };'''
N_RESET2 = u'''      if(bo) bo.onclick = function(){ L.i = 0; L.goed = 0; L.gekozen = null; L.opties = null; L.over = null; renderFunLes(); };'''
rep(A_RESET2, N_RESET2)

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
