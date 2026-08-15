#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.109: de omkering. Niet "nosotros + hablar -> ?" maar "hablamos -> wie?"

## Waar dit vandaan komt

Stefan, na de vormdril, met vier schermafbeeldingen erbij: "ik had alles goed. maar dat is niet
goed. want ik herken nu gewoon de yo en nosotros maar nog steeds niet wat de vorm is."

Dat is geen klacht over de moeilijkheidsgraad. Het is een diagnose, en hij heeft gelijk. De
Conjugador stelt zijn vraag zo:

        hablar (praten)
        nosotros
        pretérito imperfecto
        -> typ of kies de vorm

De persoon staat in de vraag. Dus de uitgang -amos draagt op dat moment geen informatie: je weet
al wie het is voordat je naar de vorm kijkt. En bij meerkeuze is het nog erger, want de afleiders
komen uit de andere personen van hetzelfde werkwoord: 288 van de 288 meerkeuzevragen hebben een
unieke persoonsuitgang tussen de opties, dus je kunt ze oplossen zonder de vorm te kennen.

De vraagvorm van de app veroorzaakt precies de blokkade die de app zou moeten opheffen. Dat is
geen woordspeling maar de kern van learned attention (Ellis & Sagarra): staat de informatie al
ergens anders, dan leert het brein de uitgang niet. Bij Cintrón-Valentín & Ellis ging de
gevoeligheid voor de werkwoordsvorm van 0.03 naar 0.61 door precies één ingreep: voortraining
waarin de concurrerende aanwijzing weg was.

## Wat dit scherm doet

Eén richting, en het is de richting die nergens in de app bestond:

        hablabais
        (hablar)
        pretérito imperfecto
        -> yo | tú | él/ella | nosotros | vosotros | ellos

Geen voornaamwoord in de vraag. Geen zin, geen tijdsbijwoord, geen context. De uitgang is het
enige wat je hebt. Dit is stap 2 uit de ladder van het ontwerpadvies: begrip vóór productie.

Na je antwoord verschijnt het hele rijtje met jouw cel gemarkeerd. Dat is niet alleen feedback,
dat is stap 1 (opbouwen): je ziet de zes vormen als groep in plaats van als losse cellen.

## Waarom dit de tweede bouwronde is en niet de tiende

Omdat het het hele ontwerp falsifieerbaar maakt voor de prijs van één scherm.

  - haal je hier veel lager dan in de Conjugador, dan is aangetoond dat je de vormen niet kent en
    dat de Conjugador iets anders meet dan hij beweert. Dan klopt het ontwerpadvies en is de
    verbouwing de moeite waard.
  - haal je hier ongeveer hetzelfde, dan zit het gat ergens anders en heb je jezelf een dure
    verbouwing bespaard voor de prijs van één schermpje.

Vandaar dat het eindscherm allebei de getallen naast elkaar zet.

## De dubbelzinnigheid, en waarom die de pool bepaalt

Niet elke vorm hoort bij één persoon. In het imperfecto is "hablaba" zowel yo als él/ella; in het
subjuntivo geldt hetzelfde voor "hable". Een vraag met twee goede antwoorden meet niets, en dit
scherm bestaat juist omdat de app te vaak iets anders meet dan hij beweert.

Dus: de pool bevat alleen vormen die binnen hun werkwoord én tijd bij precies één persoon horen.
De poort dwingt dat af over de hele pool, niet over een steekproef.

Dat de rest bestaat is geen bug maar een feit over het Spaans, en het is een van de nuttigste
dingen die je kunt weten. Daarom staat het op het eindscherm, geteld uit de data: zoveel procent
van de vormen in jouw open fasen is dubbelzinnig, en dáárom staat er in het imperfecto zo vaak
wél een voornaamwoord bij.

## Waar de uitslag heen gaat

S.brok onder "vorm.persoon", naast de betekenisbrok van v23.106. Niet in S.gram: dat is de
SRS-boekhouding per concept, en het brokkenmodel is nog niet bewezen. Eerst meten, dan koppelen.

## Wat dit expres NIET doet

Niets aan de Conjugador. De afleiders blijven kapot en meerkeuze kan nog steeds een vorm groen
maken. Dat is ronde 3. Eén variabele per ronde, anders is achteraf niet te zeggen wat het deed.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.109"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.109" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))
# versie.txt mag alleen vooruit. Zonder deze regel zet een oudere patch die je per ongeluk nog
# eens draait het versienummer terug, en dan denkt de app dat hij ouder is dan hij is.
DOE_VER = huidig_ver != NIEUW and (DOE_APP or _num(huidig_ver) < _num(NIEUW))

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    # Staat de app al op deze versie, dan is er niets te vervangen en loopt hoogstens versie.txt
    # nog achter (dat gebeurt als de avondrun er tussendoor een nieuwer nummer in heeft gezet).
    # Zonder deze regel valt een oudere patch om zodra er een nieuwere overheen is gegaan.
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ============================================================ de motor
A_MOTOR = u'''function spelInfo(){
  return ['''
N_MOTOR = u'''/* ================= DE OMKERING (v23.109) =================

   "hablamos -> wie?" in plaats van "nosotros + hablar -> ?".

   Zie de kop van patch-v23.109 voor het waarom. Kort: de Conjugador zet de persoon in de vraag,
   dus de uitgang draagt daar geen informatie. Dit scherm haalt die aanwijzing weg, zodat de
   uitgang het enige is wat je hebt. Dat is de voortrainingsconditie uit Cintrón-Valentín & Ellis,
   en stap 2 uit de ladder van het ontwerpadvies: begrip vóór productie.

   Alles hieronder leest uit de bestaande bronnen (CONJ_FASES, VERBOS, conjVorm, CONJ_TIEMPOS).
   Er staat geen enkele werkwoordsvorm in deze code. Architectuurregel 15 augustus. */
var OMKEER_ID = "vorm.persoon";
var OMKEER_LEN = 12;
var omkeerSpel = null;

/* de tijden die je open hebt staan. "mix" is geen tijd maar een fase-instelling, dus die valt af. */
function omkeerTijden(){
  var open = conjOpenMax(), uit = [];
  for(var i = 0; i <= open && i < CONJ_FASES.length; i++){
    var t = CONJ_FASES[i].tijd;
    if(t && t !== "mix" && uit.indexOf(t) === -1) uit.push(t);
  }
  return uit.length ? uit : ["presente"];
}

/* Het hart van dit scherm. Een vraag met twee goede antwoorden meet niets, en dit scherm bestaat
   juist omdat de app te vaak iets anders meet dan hij belooft. Dus: alleen vormen die binnen hun
   eigen werkwoord én tijd bij precies één persoon horen.

   Dat "hablaba" zowel yo als él/ella is, is geen fout in de data maar een feit over het Spaans.
   Het wordt geteld en op het eindscherm gezet, want het is precies waarom er in het imperfecto zo
   vaak wél een voornaamwoord bij staat. */
function omkeerPool(){
  var tijden = omkeerTijden(), pool = [], dubbel = 0, totaal = 0;
  tijden.forEach(function(t){
    var verbs = conjVerbPool(t);
    verbs.forEach(function(v){
      var vormen = conjAlleVormen(v, t);
      for(var p = 0; p < vormen.length; p++){
        var vorm = vormen[p];
        if(!vorm) continue;
        totaal++;
        var uniek = true;
        for(var q = 0; q < vormen.length; q++) if(q !== p && vormen[q] === vorm) uniek = false;
        if(uniek) pool.push({v:v, p:p, t:t, vorm:vorm});
        else dubbel++;
      }
    });
  });
  return {items:pool, dubbel:dubbel, totaal:totaal};
}

/* Een ronde van twaalf. Twee dingen bewust geregeld:
     - niet twee keer dezelfde vorm in één ronde
     - gespreid over de personen, want een ronde van acht keer "yo" meet één uitgang en niet zes.
   Zonder die spreiding zou de score omhoog kunnen zonder dat je meer weet, en dat is precies het
   soort meting waar deze week aan opgegaan is. */
function omkeerStart(){
  var pool = omkeerPool();
  var perPersoon = [[], [], [], [], [], []];
  geschud(pool.items).forEach(function(x){ perPersoon[x.p].push(x); });
  var rij = [], ronde = 0;
  while(rij.length < OMKEER_LEN && ronde < 40){
    var iets = false;
    for(var p = 0; p < 6 && rij.length < OMKEER_LEN; p++){
      if(perPersoon[p].length > ronde){ rij.push(perPersoon[p][ronde]); iets = true; }
    }
    if(!iets) break;
    ronde++;
  }
  omkeerSpel = {rij:geschud(rij), i:0, goed:0, gekozen:null, dubbel:pool.dubbel, totaal:pool.totaal};
  return omkeerSpel;
}
function omkeerAntwoord(p){
  if(!omkeerSpel || omkeerSpel.gekozen !== null) return;
  omkeerSpel.gekozen = p;
  if(p === omkeerSpel.rij[omkeerSpel.i].p) omkeerSpel.goed++;
  renderFunOmkeer();
}
function omkeerVolgende(){
  if(!omkeerSpel) return;
  omkeerSpel.i++;
  omkeerSpel.gekozen = null;
  if(omkeerSpel.i >= omkeerSpel.rij.length) brokRonde(OMKEER_ID, omkeerSpel.goed, omkeerSpel.rij.length);
  renderFunOmkeer();
}

/* De vergelijking die dit scherm de moeite waard maakt. S.conjLaatste houdt per fase de laatste
   tien antwoorden bij (1 goed, 0 fout). Opgeteld over alle fasen is dat je recente score in de
   Conjugador, waar de persoon wél in de vraag staat. Twee getallen naast elkaar, en het verschil
   is het antwoord op de vraag of de Conjugador meet wat hij belooft. */
function omkeerConjScore(){
  var r = S.conjLaatste || {}, n = 0, goed = 0;
  for(var k in r){
    if(!Object.prototype.hasOwnProperty.call(r, k)) continue;
    var lijst = r[k] || [];
    for(var i = 0; i < lijst.length; i++){ n++; goed += lijst[i] ? 1 : 0; }
  }
  return {n:n, goed:goed};
}
function omkeerUitslag(goed, totaal){
  var pct = Math.round((goed / totaal) * 100);
  if(pct >= 90) return ct("Je kent de uitgangen echt, niet alleen de voornaamwoorden. Dit is de stap waarop je door mag naar typen zonder tabel.",
                          "You really know the endings, not just the pronouns. This is the step that lets you move on to typing without the table.");
  if(pct >= 60) return ct("Het zit er half in. Sommige uitgangen herken je, andere gok je. Dat is normaal op deze stap en het is precies wat herhaling oplost.",
                          "It is half there. You recognise some endings and guess others. That is normal at this step, and it is exactly what repetition fixes.");
  return ct("Hier zit het gat. Je kunt de vorm wél maken als de persoon erbij staat, maar je herkent hem niet zonder. Meer vervoegingen typen helpt hier niet: dit is een andere oefening.",
            "This is the gap. You can produce the form when the person is given, but you do not recognise it without. Typing more conjugations will not help: this is a different exercise.");
}

function renderFunOmkeer(){
  var el = document.getElementById("funCard");
  if(!el) return;
  if(!omkeerSpel) omkeerStart();
  var totaal = omkeerSpel.rij.length;
  var kop = "<h2>" + ct("Wie is dit? \\ud83d\\udd0e", "Who is this? \\ud83d\\udd0e") + "</h2>";

  if(!totaal){
    el.innerHTML = kop + "<p class='muted'>" +
      ct("Er zijn nog geen vormen om te herkennen. Speel eerst een ronde Conjugador.",
         "There are no forms to recognise yet. Play a round of Conjugador first.") + "</p>" +
      "<div class='row' style='margin-top:10px'><button class='mini' id='btnFunTerug'>" + fx("terug") + "</button></div>";
    var bt = document.getElementById("btnFunTerug");
    if(bt) bt.onclick = function(){ funView = null; omkeerSpel = null; renderFun(); };
    return;
  }

  if(omkeerSpel.i >= totaal){
    var st = brokLees(OMKEER_ID);
    var cj = omkeerConjScore();
    var pctDub = omkeerSpel.totaal ? Math.round((omkeerSpel.dubbel / omkeerSpel.totaal) * 100) : 0;
    el.innerHTML = kop +
      "<div class='feedback " + (omkeerSpel.goed >= totaal - 1 ? "ok" : omkeerSpel.goed >= totaal - 4 ? "bijna" : "fout") + "' id='omkUitslag'>" +
        omkeerSpel.goed + " / " + totaal + "</div>" +
      "<p class='muted'>" + omkeerUitslag(omkeerSpel.goed, totaal) + "</p>" +
      (cj.n >= 5
        ? "<p class='muted' id='omkVergelijk' style='font-size:.9rem'><b>" +
            ct("Naast elkaar: ", "Side by side: ") + "</b>" +
            ct("in de Conjugador, waar de persoon in de vraag staat, had je ", "in Conjugador, where the person is given in the question, you got ") +
            Math.round((cj.goed / cj.n) * 100) + "% " + ct("van je laatste ", "of your last ") + cj.n +
            ct(" goed. Hier, zonder die aanwijzing, ", " correct. Here, without that clue, ") +
            Math.round((omkeerSpel.goed / totaal) * 100) + "%.</p>"
        : "") +
      (st.rondes > 1 ? "<p class='muted' style='font-size:.85rem'>" +
        ct("Je beste ronde tot nu toe: ", "Your best round so far: ") + st.beste + " / " + totaal + "</p>" : "") +
      "<p class='muted' id='omkDubbel' style='font-size:.85rem'>" +
        ct("Weetje: " + pctDub + "% van de vormen in je open fasen hoort bij méér dan één persoon (hablaba is zowel yo als él). Die staan hier niet tussen, want een vraag met twee goede antwoorden meet niets. En dát is de reden dat er in het imperfecto zo vaak wél een voornaamwoord bij staat.",
           "Did you know: " + pctDub + "% of the forms in your open phases belong to more than one person (hablaba is both yo and él). Those are left out here, because a question with two correct answers measures nothing. And that is exactly why the imperfecto so often keeps the pronoun.") + "</p>" +
      "<div class='row' style='margin-top:10px'>" +
        "<button class='primary' id='btnOmkNieuw'>" + ct("Nog een ronde", "Another round") + "</button>" +
        "<button class='ghost' id='btnFunTerug'>" + fx("terug") + "</button></div>";
    document.getElementById("btnOmkNieuw").onclick = function(){ omkeerStart(); renderFunOmkeer(); };
    document.getElementById("btnFunTerug").onclick = function(){ funView = null; omkeerSpel = null; renderFun(); };
    return;
  }

  var q = omkeerSpel.rij[omkeerSpel.i];
  var af = omkeerSpel.gekozen !== null;
  var goed = af && omkeerSpel.gekozen === q.p;
  var rijtje = "";
  if(af){
    /* het hele rijtje als feedback. Dat is stap 1 uit de ladder (opbouwen): de zes vormen als
       groep zien in plaats van als losse cellen. Zonder deze stap is een fout alleen een rood
       kruisje en leer je er niets van. */
    rijtje = "<table style='width:100%; margin-top:10px'>" +
      conjAlleVormen(q.v, q.t).map(function(vorm, i){
        var mij = i === q.p;
        return "<tr" + (mij ? " style='background:var(--green-soft)'" : "") + ">" +
          "<td class='muted' style='font-size:.85rem'>" + CONJ_PRONOMBRES[i] + "</td>" +
          "<td" + (mij ? " style='font-weight:700'" : "") + ">" + vorm + (mij ? " \\u2190" : "") + "</td></tr>";
      }).join("") + "</table>";
  }

  el.innerHTML = kop +
    "<span class='kicker'>" + ct("Vorm ", "Form ") + (omkeerSpel.i + 1) + "/" + totaal + "</span>" +
    (omkeerSpel.i === 0 && !af
      ? "<p class='muted'>" + ct("Er staat geen voornaamwoord bij. De uitgang is het enige wat je hebt, en dat is precies het punt: in de Conjugador staat de persoon in de vraag, dus daar hoef je de uitgang nooit te lezen.",
                                 "There is no pronoun. The ending is all you get, and that is the point: in Conjugador the person is given in the question, so you never have to read the ending.") + "</p>"
      : "") +
    "<div class='card' style='text-align:center; margin:10px 0'>" +
      "<p class='big' style='margin:4px 0' id='omkVorm'>" + q.vorm + "</p>" +
      "<p class='muted' style='margin:0; font-size:.85rem'>" + q.v.inf + " <span style='font-weight:400'>(" + conjGloss(q.v) + ")</span></p>" +
      "<p class='muted' style='margin:2px 0 0; font-size:.8rem' id='omkTijd'>" + conjTiempoNaam(q.t) + "</p>" +
    "</div>" +
    (af
      ? "<div class='feedback " + (goed ? "ok" : "fout") + "'>" +
          (goed ? ct("Goed \\u2713", "Correct \\u2713")
                : ct("Nog niet. Het is: ", "Not yet. It is: ") + "<b>" + CONJ_PRONOMBRES[q.p] + "</b>") +
        "</div>" + rijtje +
        "<div class='row' style='margin-top:10px'><button class='primary' id='btnOmkVerder'>" +
          (omkeerSpel.i + 1 >= totaal ? ct("Uitslag \\u2192", "Result \\u2192") : ct("Volgende \\u2192", "Next \\u2192")) + "</button></div>"
      : "<div id='omkKnoppen' style='display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:6px'>" +
          CONJ_PRONOMBRES.map(function(pr, i){
            return "<button type='button' class='ghost omk-p' data-p='" + i + "' style='min-height:52px'>" + pr + "</button>";
          }).join("") + "</div>") +
    "<div class='row' style='margin-top:10px'><button class='mini' id='btnFunTerug'>" + fx("terug") + "</button></div>";

  Array.prototype.forEach.call(el.querySelectorAll(".omk-p"), function(b){
    b.onclick = function(){ omkeerAntwoord(Number(b.getAttribute("data-p"))); };
  });
  var vb = document.getElementById("btnOmkVerder");
  if(vb) vb.onclick = omkeerVolgende;
  var tb = document.getElementById("btnFunTerug");
  if(tb) tb.onclick = function(){ funView = null; omkeerSpel = null; renderFun(); };
}

function spelInfo(){
  return ['''
rep(A_MOTOR, N_MOTOR)

# ============================================================ de tegel
A_TEGEL = u'''    {v:"mem",     id:"ftMem",     e:"\\ud83c\\udccf",            t:"Memory \\u00b7 Parejas",  s:fx("meS")},'''
N_TEGEL = u'''    /* v23.109: net als de brok geen spel maar een meting, en om dezelfde reden hier: dit is de
       plek waar je iets kunt doen dat geen dagportie is. Zodra het brokkenmodel staat wordt dit
       stap 2 van de vormladder. */
    {v:"omkeer",  id:"ftOmkeer",  e:"\\ud83d\\udd0e",            t:ct("Wie is dit?","Who is this?"), s:ct("Een vervoegde vorm zonder voornaamwoord: wie is het? De omgekeerde richting van de Conjugador.","A conjugated form with no pronoun: who is it? The reverse direction of Conjugador.")},
    {v:"mem",     id:"ftMem",     e:"\\ud83c\\udccf",            t:"Memory \\u00b7 Parejas",  s:fx("meS")},'''
rep(A_TEGEL, N_TEGEL)

# ============================================================ de router
A_ROUTE = u'''  if(funView === "brok"){ renderFunBrok(); return; }   // v23.106'''
N_ROUTE = u'''  if(funView === "brok"){ renderFunBrok(); return; }   // v23.106
  if(funView === "omkeer"){ renderFunOmkeer(); return; }   // v23.109'''
rep(A_ROUTE, N_ROUTE)

# ============================================================ uit de dagportie
A_DAG = u'''var DAGSPEL_UIT = {avt:1, duel:1, brok:1};   // v23.106: zie de kop van deze patch'''
N_DAG = u'''/* v23.109: omkeer erbij, om dezelfde reden als brok. Dit zijn metingen, geen dagportie: ze
   horen niet mee te tellen in het dagritme en het dagscherm hoort er niet naar te wijzen. */
var DAGSPEL_UIT = {avt:1, duel:1, brok:1, omkeer:1};'''
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
