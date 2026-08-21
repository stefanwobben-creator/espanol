#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.156: de vraag van de dag, en je groep leest mee.

Stefan, 21 aug: "we hadden ook chatten met anderen."

Hij heeft gelijk en ik moet het toegeven: praten met Chispa is er (v23.144, in je les sinds v23.150),
maar praten met een echt mens uit je groep niet. Wat er wél was tussen mensen is de krabbel: een
emoji met een vaste Spaanse zin eraan vast. Dat is een schouderklopje, geen gesprek.

## Waarom het geen chatvenster wordt

Een open chatvenster tussen drie gebruikers die op verschillende momenten van de dag oefenen, staat
leeg. Dat is precies het probleem van Palabra Duel: het belooft een tegenspeler die er niet is. En
een leeg chatvenster is erger dan geen, want het meldt elke dag dat er niemand is.

Dus: **niet synchroon, wel echt.** Eén vraag per dag in het Spaans, voor iedereen in je groep
dezelfde. Jij schrijft één zin. Daarna zie je wat de anderen schreven. Wie 's ochtends oefent en wie
's avonds komen elkaar tegen zonder tegelijk online te zijn, en de vraag staat er ook als er nog
niemand geantwoord heeft.

Pedagogisch is dit het sterkste wat de app kan bieden en het enige wat Chispa niet kan: je schrijft
voor een echt mens die het gaat lezen. Dat is betekenisgerichte output met een publiek, en het is de
draad waar Vamos het dunst in zit.

## Wat het technisch nodig had: bijna niets

Het antwoord hoeft geen tabel. De hele S van elk groepslid wordt al gesynchroniseerd en komt al mee
in het antwoord van /api/groep/:gcode. Dus: de zin komt in S.dagzin, en muurVelden() op de server
geeft hem door. Eén veld erbij op één plek, geen migratie, geen nieuw eindpunt.

Wel op de server, want daar staat muurVelden(). Dat is de enige serverwijziging.

## De remmen

  * Eén zin per dag per persoon, hoogstens 140 tekens. Geen draad, geen antwoorden op antwoorden.
  * Alleen binnen je eigen groep, en dat is de bestaande grens (zie /api/groep en de krabbels).
  * Je ziet de anderen pas nadat je zelf iets hebt geschreven. Anders is het lezen in plaats van
    schrijven, en dan is het geen productie meer.

Bewaakt door test/suites/pw-dagzin.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_SRV = os.path.join(WORTEL, "server", "index.js")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.156"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()
with io.open(PAD_SRV, encoding="utf-8") as f:
    srv = f.read()

DOE_APP = NIEUW not in src
DOE_SRV = "v23.156" not in srv
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER and not DOE_SRV:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


def repsrv(anker, nieuw, n=1):
    global srv
    if not DOE_SRV:
        return
    gevonden = srv.count(anker)
    assert gevonden == n, "serveranker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    srv = srv.replace(anker, nieuw, n)


# ================= 1. de server geeft de zin door =================

repsrv(
    '''    oogst: oogstKort((st && st.oogst) || {}),
  };''',
    '''    oogst: oogstKort((st && st.oogst) || {}),
    /* v23.156: de zin van vandaag, het antwoord op de vraag van de dag. Geen tabel nodig: de hele
       state van elk groepslid wordt al gesynchroniseerd en komt hier al langs. Alleen vandaag en
       gisteren, en afgekapt, want dit antwoord wordt bij elk bezoek opgehaald. */
    dagzin: (function(){
      const dz = st && st.dagzin;
      if (!dz || !dz.es || !dz.d) return null;
      const vandaag = new Date().toISOString().slice(0, 10);
      const gisteren = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
      if (dz.d !== vandaag && dz.d !== gisteren) return null;
      return { d: dz.d, v: String(dz.v || ""), es: String(dz.es).slice(0, 140) };
    })(),
  };''',
)

# ================= 2. de vraag zelf =================

rep(
    '''function muurGroep(){ return (S.groepen && S.groepen[0]) || null; }''',
    '''function muurGroep(){ return (S.groepen && S.groepen[0]) || null; }

/* ================= DE VRAAG VAN DE DAG (v23.156) =================

   Stefan: "we hadden ook chatten met anderen."

   Praten met Chispa staat er sinds v23.144; praten met een echt mens niet. Wat er tussen mensen was
   is de krabbel: een emoji met een vaste Spaanse zin. Een schouderklopje, geen gesprek.

   Waarom dit geen chatvenster is: drie gebruikers die op verschillende momenten oefenen, leveren een
   leeg venster op. Dat is het probleem van Palabra Duel, en een leeg venster is erger dan geen,
   want het meldt elke dag dat er niemand is.

   Dus niet synchroon, wel echt: één vraag per dag, voor iedereen in je groep dezelfde, en je ziet
   wat de anderen schreven. Wie 's ochtends oefent en wie 's avonds komt, komen elkaar tegen zonder
   tegelijk online te zijn.

   Dit is het enige in de app wat Chispa niet kan: je schrijft voor een echt mens die het gaat lezen. */
var DAGVRAGEN = [
  {es:"\\u00bfQu\\u00e9 has hecho hoy?",            nl:"Wat heb je vandaag gedaan?",          en:"What did you do today?"},
  {es:"\\u00bfQu\\u00e9 comiste ayer?",             nl:"Wat heb je gisteren gegeten?",        en:"What did you eat yesterday?"},
  {es:"\\u00bfC\\u00f3mo es tu barrio?",            nl:"Hoe is jouw buurt?",                  en:"What's your neighbourhood like?"},
  {es:"\\u00bfQu\\u00e9 haces los domingos?",       nl:"Wat doe je op zondag?",               en:"What do you do on Sundays?"},
  {es:"\\u00bfAd\\u00f3nde quieres viajar?",        nl:"Waar wil je naartoe reizen?",         en:"Where do you want to travel?"},
  {es:"\\u00bfQu\\u00e9 m\\u00fasica te gusta?",         nl:"Naar welke muziek luister je graag?", en:"What music do you like?"},
  {es:"\\u00bfC\\u00f3mo empieza tu d\\u00eda?",         nl:"Hoe begint jouw dag?",                en:"How does your day start?"},
  {es:"\\u00bfQu\\u00e9 vas a hacer este fin de semana?", nl:"Wat ga je dit weekend doen?",   en:"What are you doing this weekend?"},
  {es:"\\u00bfQui\\u00e9n es importante para ti?",  nl:"Wie is belangrijk voor je?",          en:"Who is important to you?"},
  {es:"\\u00bfQu\\u00e9 te hizo re\\u00edr esta semana?", nl:"Waar moest je deze week om lachen?", en:"What made you laugh this week?"}
];
var DAGZIN_MAX = 140;
function dagVraag(datum){
  return DAGVRAGEN[dagHashVoor(datum || today(), "dagvraag") % DAGVRAGEN.length];
}
function dagZinMijn(){
  var d = S.dagzin;
  return (d && d.d === today() && d.es) ? d : null;
}
function dagZinBij(es){
  var t = String(es || "").trim().slice(0, DAGZIN_MAX);
  if(!t) return false;
  S.dagzin = {d:today(), v:dagVraag().es, es:t};
  /* Het telt als produceren, net als de zinnen en het gesprek: je hebt zelf iets gemaakt. En het
     vinkje zorgt dat de app het vandaag niet nog een keer voorstelt. */
  S.lesFlowSpel = S.lesFlowSpel || {};
  S.lesFlowSpel.groepszin = today();
  addXP(4);
  persist();
  try { syncUp(); } catch(e){}   // meteen zichtbaar voor je groep, niet pas bij de volgende sync
  return true;
}
/* Wat de anderen schreven. Pas ná jouw eigen zin: anders lees je in plaats van dat je schrijft, en
   dan is het geen productie meer. Dat is dezelfde reden waarom een toets je het antwoord niet toont
   voordat je hebt geantwoord. */
function dagZinAnderen(){
  var ik = "";
  try { ik = String(krabbelIkBen() || "").toLowerCase(); } catch(e){}
  var sp = (muurData && muurData.spelers) || [];
  return sp.filter(function(x){
    if(String(x.naam).toLowerCase() === ik) return false;
    return !!(x.dagzin && x.dagzin.d === today() && x.dagzin.es);
  }).map(function(x){ return {naam:x.naam, es:x.dagzin.es}; });
}
function dagZinHtml(){
  if(!muurGroep()) return "";
  var v = dagVraag(), mijn = dagZinMijn();
  var h = "<div class='card' id='dagzinCard'><span class='kicker'>"+
      ct("De vraag van vandaag","Today's question")+" \\u00b7 "+ct("je groep leest mee","your group reads along")+"</span>"+
    "<p class='big es' style='margin:4px 0 2px'>"+muurEsc(v.es)+"</p>"+
    "<p class='muted' style='margin:0 0 8px; font-size:.88rem'>"+muurEsc(ct(v.nl, v.en))+"</p>";
  if(!mijn){
    h += "<input type='text' id='dagzinInp' maxlength='"+DAGZIN_MAX+"' autocomplete='off' "+
           "placeholder='"+ct("Eén zin in het Spaans","One sentence in Spanish")+"'>"+
      "<div class='row' style='margin-top:8px'><button class='primary' id='btnDagzin'>"+
        ct("Zet hem erbij","Post it")+"</button></div>"+
      "<p class='muted' style='margin:6px 0 0; font-size:.85rem'>"+
        ct("Eén zin, en fout mag. Daarna zie je wat de anderen schreven.",
           "One sentence, and mistakes are fine. Then you see what the others wrote.")+"</p>";
    return h + "</div>";
  }
  h += "<div class='oogst'><b>"+muurEsc(ct("Jij","You"))+"</b> \\u00b7 <span class='es'>"+muurEsc(mijn.es)+"</span></div>";
  var and = dagZinAnderen();
  h += and.length
    ? and.map(function(a){
        return "<div class='oogst'><b>"+muurEsc(a.naam)+"</b> \\u00b7 <span class='es'>"+muurEsc(a.es)+"</span></div>";
      }).join("")
    : "<p class='muted' style='margin:8px 0 0; font-size:.88rem'>"+
        ct("De anderen hebben vandaag nog niets geschreven. Kom er later op terug.",
           "The others have not written anything yet today. Come back later.")+"</p>";
  return h + "</div>";
}
function dagZinWire(){
  var b = document.getElementById("btnDagzin"), inp = document.getElementById("dagzinInp");
  if(!b || !inp) return;
  function zet(){
    if(!dagZinBij(inp.value)) return;
    var el = document.getElementById("dagzinCard");
    if(el){
      var n = document.createElement("div");
      n.innerHTML = dagZinHtml();
      if(n.firstChild){ el.parentNode.replaceChild(n.firstChild, el); dagZinWire(); }
    }
    try { muurGehaald = 0; muurHaal(); } catch(e){}
  }
  b.onclick = zet;
  inp.onkeydown = function(e){ if(e.key === "Enter"){ e.preventDefault(); zet(); } };
}''',
)

# ================= 3. hij staat bij je groep =================

rep(
    '''  return "<div class='card' id='muurCard'>" +
    (lijst.length''',
    '''  return dagZinHtml() +   /* v23.156: de vraag van vandaag staat boven de muur */
    "<div class='card' id='muurCard'>" +
    (lijst.length''',
)

rep(
    '''  if(nieuw.firstChild){ el.parentNode.replaceChild(nieuw.firstChild, el); muurWire(); }''',
    '''  if(nieuw.firstChild){ el.parentNode.replaceChild(nieuw.firstChild, el); muurWire(); }
  try { dagZinWire(); } catch(e){}   // v23.156''',
)

# ================= 4. en na je les, als voorstel =================

rep(
    '''  /* v23.144: het gesprek staat op plek twee, vóór je route.''',
    '''  /* v23.156: en de vraag van vandaag staat daar weer vóór.

     Waarom vóór het gesprek met Chispa: allebei zijn ze productie en allebei zijn ze er één per dag,
     maar hier leest een echt mens mee. Dat is het enige voorstel met een publiek, en het is precies
     de draad waar Vamos het dunst in zit. Chispa is er morgen ook nog; je groep schrijft vandaag. */
  try {
    if(muurGroep() && !dagZinMijn()){
      var dv = dagVraag();
      return {icon:"\\ud83d\\udc65",
        kop:ct("De vraag van vandaag","Today\'s question"),
        waarom:ct("\\u201c"+dv.es+"\\u201d ("+dv.nl+") Eén zin, en je groep leest mee. Schrijven voor iemand die het echt leest is iets anders dan schrijven voor een toets.",
                  "\\u201c"+dv.es+"\\u201d ("+dv.en+") One sentence, and your group reads it. Writing for someone who really reads it is not the same as writing for a test."),
        knop:ct("Schrijf je zin","Write your sentence"),
        doe:function(){ show("perfil"); setTimeout(function(){
          var el = document.getElementById("dagzinInp"); if(el) el.focus();
        }, 300); }};
    }
  } catch(e){}
  /* v23.144: het gesprek staat op plek twee, vóór je route.''',
)

# ================= 5. en een restje uit v23.147 =================
#
# pw-taal ging af en toe rood op "geen Nederlands in speeltuin letras". v23.147 haalde FREQ al uit de
# Letras-vijver voor Engelse profielen, maar de tweede bron bleef: wTrans() valt terug op w.nl zodra
# er geen Engelse vertaling voor dat woordid bestaat. Welke woorden de puzzel pakt is toeval, dus de
# fout was het ook.
#
# Nu vraagt de vijver de vertaling via wTrans() én controleert hij of die er echt in jouw taal is.
# Zonder Engelse vertaling doet het woord niet mee: liever een kleinere vijver dan een omschrijving
# die je niet leest. Voor een Nederlands profiel verandert er niets.

rep(
    """  if(l !== "nl" && TRANS[l] && TRANS[l][w.id]) return TRANS[l][w.id];
  return w.nl;
}""",
    """  if(l !== "nl" && TRANS[l] && TRANS[l][w.id]) return TRANS[l][w.id];
  return w.nl;
}
/* v23.156: is die vertaling er echt in jouw taal, of is dit de Nederlandse terugval? Alleen nodig op
   plekken waar een Nederlandse omschrijving in een Engels profiel onleesbaar is en het woord ook
   gemist kan worden, zoals de woordenvijver van Letras. */
function wTransEcht(w){
  var l = profLang();
  if(l === "nl") return true;
  return !!(TRANS[l] && TRANS[l][w.id]);
}""",
)

rep(
    """      var es = String(w.es || "").replace(/^(el|la|los|las|un|una)\\s+/i, "").split(/[\\/(]/)[0].trim();
      voeg(es, wTrans(w));""",
    """      var es = String(w.es || "").replace(/^(el|la|los|las|un|una)\\s+/i, "").split(/[\\/(]/)[0].trim();
      // v23.156: zonder vertaling in jouw taal doet het woord niet mee, zie wTransEcht
      if(!wTransEcht(w)) return;
      voeg(es, wTrans(w));""",
)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_SRV:
    with io.open(PAD_SRV, "w", encoding="utf-8") as f:
        f.write(srv)
    print("server/index.js bijgewerkt")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
