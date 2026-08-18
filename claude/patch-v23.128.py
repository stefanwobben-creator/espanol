#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.128: in een echte zin. De vorm krijgt eindelijk een zin eromheen.

## De hoofdvraag

Alles wat de app over werkwoorden doet is losse vormen: cellen, rijtjes, patronen. Spaans spreek
je in zinnen. Je kunt straks 22 werkwoorden foutloos vervoegen en nog steeds vastlopen zodra je
iets wilt zeggen, en dat is precies het gat dat elke grammaticacursus laat vallen.

De hoofdvraag ("helpt dit Stefan sneller en met meer plezier Spaans leren") geeft hier het
duidelijkste ja van alles wat er open stond, duidelijker dan een subjuntivo-route.

## Is dit niet gewoon "Zinnen maken"?

Nee, en dat is de eerste vraag die ik mezelf gesteld heb. Zinnen maken is NL -> ES, de hele zin,
alles tegelijk: woordenschat, woordvolgorde, lidwoorden en de vorm. Als je daar de mist in gaat
weet je niet waarop.

Een gatzin isoleert precies één ding (de vorm) en laat de rest staan. De betekenis staat er
gewoon bij, in het Nederlands, want daar hoort de vorm uit te volgen. Dat is form-focused
instruction binnen betekenis, en niet een vervoegingstabel met decor.

## De meting eerst

Uit de 216 zinnen in SENTENCES:

    zinnen met precies één herkenbare vervoegde vorm, één werkwoord       62
    werkwoorden daarin                                                    11
    ser 18, estar 12, tener 10, sentir 6, ir 5, preferir 3, poder 3,
    trabajar 2, pedir 1, salir 1, vivir 1

Scheef, en dat is niet erg: het zijn de werkwoorden die in élke zin voorkomen die je ooit gaat
zeggen. Wat wel telt is dat de pool AFGELEID is. Zet de avondrun er vannacht tien zinnen bij met
quiero of duermo erin, dan staan die er morgen in zonder dat er iets bijgewerkt hoeft te worden.

## Twee vallen die de meting opleverde

"Van Gogh pintó unos 900 cuadros." Van is de ellos-vorm van ir, dus zonder rem zet deze oefening
een gat in een eigennaam. De rem: een vorm met een hoofdletter middenin de zin telt niet mee.

Maar "¿Puedo pedirte un favor?" begint óók met een hoofdletter, want er staat een ¿ voor. Die
uitzondering hoort erbij, anders gooit de rem de goede zinnen weg met de verkeerde.

## Wat het wordt

Een nieuw scherm (funView "zin"), acht opgaven per ronde:

    de Nederlandse zin          zodat de betekenis er is voordat je de vorm kiest
    de Spaanse zin met ___      alles staat er, behalve dat ene woord
    de infinitief + persoon     dus je weet welk werkwoord, niet welke vorm
    typen, geen tabel

Na je antwoord: de hele zin, en de uitleg die bij die zin hoort als hij er is. Die uitleg staat er
al bij honderden zinnen, geschreven door de avondrun, en werd tot nu toe alleen in de Corrector
gebruikt.

Hij staat als stap 8 in de presente-route, tussen "de zes door elkaar" en "gestold". Dat is de
volgorde die de rest van de route ook aanhoudt: eerst blokken, dan mengen, dan in context, dan
uitgesteld toetsen.
"""

import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.128"

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


# ------------- 1. het scherm

rep(
    '''function lesAntwoord(gegeven){''',
    '''/* ================= IN EEN ECHTE ZIN (v23.128) =================

   Alles wat deze app over werkwoorden doet was tot nu toe losse vormen: cellen, rijtjes, patronen.
   Spaans spreek je in zinnen. Je kunt 22 werkwoorden foutloos vervoegen en nog steeds vastlopen
   zodra je iets wilt zeggen.

   Dit is niet hetzelfde als Zinnen maken. Dat is NL \\u2192 ES, de hele zin, alles tegelijk:
   woordenschat, volgorde, lidwoorden \\u00e9n de vorm. Ga je daar de mist in, dan weet je niet waarop.
   Een gatzin isoleert precies \\u00e9\\u00e9n ding en laat de rest staan, met de betekenis er in het
   Nederlands naast, want daar hoort de vorm uit te volgen.

   GEMETEN in de 216 zinnen: 62 hebben precies \\u00e9\\u00e9n herkenbare vervoegde vorm van precies \\u00e9\\u00e9n
   werkwoord. Elf werkwoorden, scheef verdeeld (ser 18, estar 12, tener 10, sentir 6, ir 5, \\u2026), en
   dat is niet erg: het zijn de werkwoorden die in elke zin zitten die je ooit gaat zeggen. Wat wel
   telt is dat de pool wordt AFGELEID. Zet de avondrun er vannacht zinnen met quiero of duermo bij,
   dan staan die er morgen in zonder dat hier iets bijgewerkt hoeft te worden.

   TWEE VALLEN die de meting opleverde:

     "Van Gogh pinto unos 900 cuadros."   Van is de ellos-vorm van ir. Zonder rem zet deze oefening
                                          een gat in een eigennaam.
     "\\u00bfPuedo pedirte un favor?"            Puedo staat ook met een hoofdletter, maar door de \\u00bf.

   De rem is dus: een hoofdletter telt alleen als eigennaam-signaal midden in de zin, en niet direct
   na het begin of na \\u00bf \\u00a1 . ! ? */
var ZIN_LEN = 8;
var zinSpel = null;

/* Staat dit woord aan het begin van een zin? Dan zegt zijn hoofdletter niets. */
function zinAanBegin(es, idx){
  for(var i = idx - 1; i >= 0; i--){
    var c = es.charAt(i);
    if(c === " " || c === "\\u00bf" || c === "\\u00a1" || c === "\\"" || c === "'") continue;
    return c === "." || c === "!" || c === "?" || c === ":" || c === ";";
  }
  return true;
}
/* Begint het eerstvolgende woord met een hoofdletter? Dan is dit vermoedelijk de eerste helft van
   een naam, en geen werkwoord. */
function zinVolgendeHoofdletter(es, na){
  var rest = es.slice(na);
  var m = /^[^A-Za-z\u00c0-\u017f]*([A-Za-z\u00c0-\u017f])/.exec(rest);
  if(!m) return false;
  return m[1] !== m[1].toLowerCase();
}
/* Alle vormen van alle tijden, één keer opgebouwd: welke (werkwoord, persoon, tijd) hoort bij deze
   letterreeks? Meerdere treffers betekent dubbelzinnig, en dan doet de zin niet mee. */
var zinVormIdx = null;
function zinVormen(){
  if(zinVormIdx) return zinVormIdx;
  zinVormIdx = {};
  var tijden = CONJ_TIEMPOS.map(function(x){ return x.id; });
  VERBOS.forEach(function(v){
    tijden.forEach(function(t){
      if(!conjHeeftTijd(v, t)) return;
      for(var p = 0; p < 6; p++){
        var f = conjVorm(v, p, t);
        if(!f) continue;
        var k = f.toLowerCase();
        zinVormIdx[k] = zinVormIdx[k] || [];
        zinVormIdx[k].push({v:v, p:p, t:t});
      }
    });
  });
  return zinVormIdx;
}
/* Eén kandidaat uit één zin, of null. Precies één bruikbare treffer die naar precies één
   (werkwoord, persoon, tijd) wijst; alles daarbuiten is dubbelzinnig en doet niet mee. */
function zinKandidaat(z){
  if(!z || !z.es) return null;
  var idx = zinVormen(), treffers = [], m;
  var re = /[A-Za-z\\u00c0-\\u017f]+/g;
  while((m = re.exec(z.es)) !== null){
    var w = m[0], k = w.toLowerCase();
    if(!idx[k]) continue;
    /* Twee eigennaam-remmen, allebei nodig en allebei door de meting afgedwongen:
       "Van Gogh pinto..."  Van is de ellos-vorm van ir, staat vooraan, en de hoofdletter zegt dus
                            niets. Wat het wel verraadt is het woord erna: Gogh.
       "Suzuki dice..."     hoofdletter midden in de zin.
       "\u00bfPuedo pedirte...?"  hoofdletter door de \u00bf, en dat is geen eigennaam. */
    var hoofd = w.charAt(0) !== w.charAt(0).toLowerCase();
    if(hoofd && !zinAanBegin(z.es, m.index)) return null;
    if(hoofd && zinVolgendeHoofdletter(z.es, m.index + w.length)) return null;
    treffers.push({w:w, i:m.index, kans:idx[k]});
  }
  if(treffers.length !== 1) return null;
  var t = treffers[0];
  if(t.kans.length !== 1) return null;
  var k1 = t.kans[0];
  return {z:z, w:t.w, i:t.i, v:k1.v, p:k1.p, t:k1.t};
}
/* De pool: alleen zinnen die je hebt vrijgespeeld, en alleen tijden die open staan. */
function zinPool(tijden){
  var toe = {};
  allowedSentIds().forEach(function(id){ toe[id] = true; });
  var open = conjOpenTijden();
  return SENTENCES.filter(function(z){ return toe[z.id]; })
    .map(zinKandidaat)
    .filter(function(k){
      if(!k) return false;
      if(open.indexOf(k.t) === -1) return false;
      return !tijden || tijden.indexOf(k.t) !== -1;
    });
}
/* Elke route houdt zijn eigen stand bij, net als bij de les: zin.presente en zin.indefimperf zijn
   twee verschillende stappen, en de losse tegel is er weer een andere. */
function zinStart(tijden, brok){
  var pool = geschud(zinPool(tijden));
  zinSpel = {rij:pool.slice(0, ZIN_LEN), i:0, goed:0, fout:0, gekozen:null,
             tijden:tijden || null, brok:brok || "zin.vorm"};
  return zinSpel;
}
function zinNu(){
  if(!zinSpel || !zinSpel.rij.length) return null;
  return zinSpel.rij[Math.min(zinSpel.i, zinSpel.rij.length - 1)];
}
function zinAntwoord(gegeven){
  if(!zinSpel || zinSpel.gekozen !== null) return;
  var g = String(gegeven || "").trim();
  if(!g) return;
  var k = zinNu();
  if(!k) return;
  zinSpel.gekozen = g;
  // zelfde soepelheid als overal: accenten mogen missen
  if(stripAcc(norm(g)) === stripAcc(norm(k.w))) zinSpel.goed++; else zinSpel.fout++;
  renderFunZin();
}
function zinVolgende(){
  if(!zinSpel) return;
  zinSpel.i++;
  zinSpel.gekozen = null;
  if(zinSpel.i >= zinSpel.rij.length){
    S.brok = S.brok || {};
    var st = brokLees(zinSpel.brok);
    st.rondes = (st.rondes || 0) + 1;
    st.beste = Math.max(st.beste || 0, zinSpel.goed);
    /* de lengte erbij, want een ronde over een kleine pool is korter dan acht en dan zou "7 van de
       8" een eis zijn die niemand kan halen */
    st.len = zinSpel.rij.length;
    st.laatst = today();
    S.brok[zinSpel.brok] = st;
    try { persist(); } catch(e){}
  }
  renderFunZin();
}
/* De zin met het gat erin. Op index knippen en niet op zoek-en-vervang: hetzelfde woord kan twee
   keer in de zin staan, en dan zou vervangen allebei de plekken leeghalen. */
function zinMetGat(k){
  return k.z.es.slice(0, k.i) + "<b>____</b>" + k.z.es.slice(k.i + k.w.length);
}

function renderFunZin(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var terug = function(){ zinSpel = null; funTerug(); };
  var kop = "<h2>" + ct("In een echte zin \\u270d\\ufe0f", "In a real sentence \\u270d\\ufe0f") + "</h2>";

  if(!zinSpel) zinStart(null, null);
  if(!zinSpel.rij.length){
    el.innerHTML = kop + "<p class='muted'>" +
      ct("Er zijn nog geen zinnen vrijgespeeld waarin precies \\u00e9\\u00e9n werkwoordsvorm staat. Doe eerst wat lessen; dan komen ze vanzelf.",
         "No unlocked sentences yet with exactly one verb form in them. Do a few lessons first and they will come.") + "</p>" +
      "<div class='row' style='margin-top:10px'><button class='mini' id='btnFunTerug'>" + funTerugLabel() + "</button></div>";
    var tb0 = document.getElementById("btnFunTerug");
    if(tb0) tb0.onclick = terug;
    return;
  }

  var n = zinSpel.rij.length;
  if(zinSpel.i >= n){
    var st = brokLees(zinSpel.brok);
    el.innerHTML = kop +
      "<div class='feedback " + (zinSpel.goed >= n - 1 ? "ok" : "bijna") + "' id='zinUitslag'>" +
        zinSpel.goed + " / " + n + "</div>" +
      "<p class='muted'>" + ct("Beste tot nu toe: ", "Best so far: ") + (st.beste || 0) + "/" + n +
        " \\u00b7 " + (st.rondes || 0) + " " + ct("rondes", "rounds") + "</p>" +
      "<div class='row' style='margin-top:10px'><button class='primary' id='btnZinNieuw'>" +
        ct("Nog een ronde", "Another round") + "</button>" +
      "<button class='mini' id='btnFunTerug'>" + funTerugLabel() + "</button></div>";
    var bn = document.getElementById("btnZinNieuw");
    if(bn) bn.onclick = function(){ zinStart(zinSpel.tijden, zinSpel.brok); renderFunZin(); };
    var tb1 = document.getElementById("btnFunTerug");
    if(tb1) tb1.onclick = terug;
    return;
  }

  var k = zinNu();
  var af = zinSpel.gekozen !== null;
  var isGoed = af && stripAcc(norm(String(zinSpel.gekozen))) === stripAcc(norm(k.w));
  var html = kop +
    "<span class='kicker'>" + (zinSpel.i + 1) + "/" + n + " \\u00b7 " + conjTiempoLabel(k.t) + "</span>" +
    /* de betekenis eerst: de vorm hoort uit de zin te volgen en niet uit een tabel */
    "<p style='margin:10px 0 2px'><b>" + ct(k.z.nl, k.z.en || k.z.nl) + "</b></p>" +
    "<div class='card' style='margin:8px 0'>" +
      "<p class='big' style='margin:0 0 6px' id='zinGat'>" + (af ? k.z.es : zinMetGat(k)) + "</p>" +
      "<p class='muted' style='margin:0; font-size:.85rem' id='zinHint'>" +
        "<b>" + k.v.inf + "</b> (" + conjGloss(k.v) + ") \\u00b7 " + CONJ_PRONOMBRES[k.p] + "</p></div>" +
    (af ? "" : "<input type='text' id='zinInput' autocomplete='off' autocapitalize='off' spellcheck='false' placeholder='" +
        ct("Typ de vorm...", "Type the form...") + "' style='width:100%; padding:12px; font-size:1rem'>" +
      "<div class='row' style='margin-top:8px'><button class='primary' id='btnZinCheck'>" + ct("Nakijken", "Check") + "</button></div>");

  if(af){
    html += "<div class='feedback " + (isGoed ? "ok" : "fout") + "'>" +
      (isGoed ? ct("Goed \\u2713", "Correct \\u2713")
              : ct("Nog niet. Het is: ", "Not yet. It is: ") + "<b>" + k.w + "</b>") + "</div>" +
      /* de uitleg die bij deze zin hoort staat er al, geschreven door de avondrun, en werd tot nu
         toe alleen in de Corrector gebruikt */
      (k.z.uitleg ? "<p class='muted' style='font-size:.9rem' id='zinUitleg'>" + ct(k.z.uitleg, k.z.ue || k.z.uitleg) + "</p>" : "") +
      "<div class='row' style='margin-top:10px'><button class='primary' id='btnZinNext'>" +
        (zinSpel.i + 1 >= n ? ct("Uitslag \\u2192", "Result \\u2192") : ct("Volgende \\u2192", "Next \\u2192")) + "</button></div>";
  }
  html += "<div class='row' style='margin-top:10px'><button class='mini' id='btnFunTerug'>" + funTerugLabel() + "</button></div>";

  el.innerHTML = html;
  var inp = document.getElementById("zinInput");
  var doe = function(){ zinAntwoord(inp ? inp.value : ""); };
  if(inp){
    inp.focus();
    inp.onkeydown = function(e){ if(e && (e.key === "Enter" || e.keyCode === 13)){ e.preventDefault(); doe(); } };
  }
  var bc = document.getElementById("btnZinCheck");
  if(bc) bc.onclick = doe;
  var bx = document.getElementById("btnZinNext");
  if(bx) bx.onclick = function(){ zinVolgende(); };
  var tb = document.getElementById("btnFunTerug");
  if(tb) tb.onclick = terug;
}

function lesAntwoord(gegeven){''',
)

# ------------- 2. het scherm aanmelden

rep(
    '''  if(funView === "hertoets"){ renderFunHertoets(); return; }   // v23.117''',
    '''  if(funView === "hertoets"){ renderFunHertoets(); return; }   // v23.117
  if(funView === "zin"){ renderFunZin(); return; }   // v23.128''',
)

rep(
    '''    {v:"tijdvorm", id:"ftTijdvorm", e:"\\u23f3",     gram:true,  t:ct("Welke tijd is dit?","Which tense is this?"),''',
    '''    /* v23.128: de vorm in een zin in plaats van in een cel. Staat bij grammatica en niet bij de
       spellen, om dezelfde reden als de rest: dit telt mee voor je niveau. */
    {v:"zin",     id:"ftZin",     e:"\\u270d\\ufe0f",  gram:true,  t:ct("In een echte zin","In a real sentence"), s:ct("Een hele Spaanse zin met \\u00e9\\u00e9n woord eruit: de werkwoordsvorm. De betekenis staat erbij, de tabel niet.","A whole Spanish sentence with one word missing: the verb form. The meaning is there, the table is not."), gezien:false, verse:function(){ zinSpel = null; }},
    {v:"tijdvorm", id:"ftTijdvorm", e:"\\u23f3",     gram:true,  t:ct("Welke tijd is dit?","Which tense is this?"),''',
)

# ------------- 3. de route: de zin komt tussen mengen en stollen

rep(
    '''     {brok:"pad.presente", soort:"hertoets", view:"hertoets",
      nl:"Gestold?", en:"Has it set?",
      subNl:"Tien vormen uit de tweeëntwintig, op zijn vroegst drie dagen na de rest.",
      subEn:"Ten forms out of the twenty-two, at the earliest three days after the rest."}''',
    '''     /* v23.128: eerst blokken, dan mengen, dan in context, en pas dan uitgesteld toetsen. */
     {brok:"zin.presente", soort:"zin", view:"zin", tijden:["presente"],
      nl:"In een echte zin", en:"In a real sentence",
      subNl:"Een hele Spaanse zin met \\u00e9\\u00e9n woord eruit. De betekenis staat erbij; daar hoort de vorm uit te volgen.",
      subEn:"A whole Spanish sentence with one word missing. The meaning is there; the form should follow from it."},
     {brok:"pad.presente", soort:"hertoets", view:"hertoets",
      nl:"Gestold?", en:"Has it set?",
      subNl:"Tien vormen uit de tweeëntwintig, op zijn vroegst drie dagen na de rest.",
      subEn:"Ten forms out of the twenty-two, at the earliest three days after the rest."}''',
)

rep(
    '''var GRAM_EIS = {
  /* de bestaande lessen houden {stap, klaar, rondes} bij; "klaar" is precies het vinkje dat je in
     de Oefenen-tab ziet staan. De route leest dat en claimt niets zelf. */
  bestaandeles: function(st){ return !!st.klaar; },''',
    '''var GRAM_EIS = {
  /* de bestaande lessen houden {stap, klaar, rondes} bij; "klaar" is precies het vinkje dat je in
     de Oefenen-tab ziet staan. De route leest dat en claimt niets zelf. */
  bestaandeles: function(st){ return !!st.klaar; },
  /* v23.128: alles op één na goed. Even streng als een lesstap en minder streng dan de hertoets,
     want dit is oefenen en niet het examen. De noemer komt uit de ronde zelf: is de pool voor deze
     tijden kleiner dan acht, dan is de ronde korter en zou "7 van de 8" onhaalbaar zijn. */
  zin:       function(st){ var n = st.len || ZIN_LEN; return st.rondes ? (st.beste || 0) >= n - 1 : false; },''',
)

rep(
    '''var GRAM_STAND = {''',
    '''var GRAM_STAND = {
  zin:       function(st){ return st.rondes ? ct("beste ", "best ") + (st.beste || 0) + "/" + (st.len || ZIN_LEN) : ""; },''',
)

# de stap opent het scherm; brok/tijdvorm doen dat via hun eigen tak, zin heeft er ook een nodig
rep(
    '''  else if(s.view === "brok"){ brokSpel = null; }''',
    '''  else if(s.view === "brok"){ brokSpel = null; }
  else if(s.view === "zin"){ zinStart(s.tijden || p.tijden, s.brok); }''',
)

# ------------- 4. de stap die in de verleden-tijdroute op "komt nog" stond

# Gemeten in de volle bak: 108 presente, 15 indefinido, 3 imperfecto. Achttien is genoeg voor een
# ronde van acht, dus de laatste "komt nog" van Stefans eigen route kan weg.
rep(
    '''     {brok:"indefimperf.keuze", soort:"keuze", view:null,
      nl:"In een echte zin kiezen", en:"Choosing inside a real sentence",
      subNl:"Komt nog. Dit is de stap waar de regel en de vorm samenkomen.",
      subEn:"Coming. This is where the rule and the form come together."},''',
    '''     /* v23.128: dit was de laatste stap die op "komt nog" stond. Gemeten in de volle zinnenbak:
        18 zinnen met precies \u00e9\u00e9n vorm in het indefinido of imperfecto, genoeg voor een ronde. */
     {brok:"zin.indefimperf", soort:"zin", view:"zin", tijden:["indefinido", "imperfecto"],
      nl:"In een echte zin", en:"In a real sentence",
      subNl:"Hier komen de regel en de vorm samen: de zin zegt wat er gebeurde, jij zet het werkwoord in de goede tijd.",
      subEn:"This is where the rule and the form come together: the sentence says what happened, you put the verb in the right tense."},''',
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
