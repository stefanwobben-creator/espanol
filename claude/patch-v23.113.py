#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.113: "Welke tijd is dit?" De tweede helft van de omkering.

## Waar dit vandaan komt

De uitslag van "Wie is dit?" (v23.109), Stefans eerste ronde:

    Conjugador   27/30   90%   persoon staat in de vraag
    Wie is dit?  10/12   83%   geen aanwijzing

Bij twaalf vragen is de standaardfout ongeveer 11 procentpunt. Dat verschil van 6,7 punt is ruis.
Geen gat. Mijn blocking-hypothese voor de PERSOON wordt hier niet bevestigd, en dat is precies wat
ik in het advies als uitkomst had opgeschreven.

En bij nader inzien klopte de analogie ook niet. Cintrón-Valentín & Ellis gaat over TIJDsmorfologie
die geblokkeerd wordt door TIJDsbijwoorden: "ayer" verdringt de uitgang. Ik heb daar de
persoonsvariant van gebouwd. Maar bij persoon is er geen concurrerende aanwijzing in de taal zelf:
het Spaans laat het voornaamwoord meestal juist weg, dus je bent al gedwongen de uitgang te lezen.
Vandaar dat Stefan die uitgangen gewoon kent.

Stefans klacht was: "ik herken nu gewoon de yo en nosotros maar nog steeds niet wat de vorm is."
Ik las "de vorm" als de persoonsuitgang. Dat was fout. Uit de meting volgt dat de persoon zit, en
dat het gat bij de TIJD zit. Wat precies aansluit op zijn echte struikelblok, dat nooit over
personen ging maar over indefinido tegenover imperfecto.

## Waarom dit geen blocking-experiment is geworden

Het plan was twaalf zinnen mét tijdsbijwoord tegenover twaalf zonder. Eerst gemeten of dat met de
echte zinnen in de app kon:

    272 zinnen, waarvan 133 met precies één eenduidige werkwoordsvorm erin
     18 daarvan hebben een tijdsbijwoord, 115 niet
    106 van de 133 staan in het presente

Te scheef om er iets uit te concluderen, en zelf Spaanse zinnen genereren om het rond te krijgen is
precies waar deze app al eerder werkwoordsvormen mee zat te verzinnen (v23.48). Dus dat experiment
gaat niet door, en dat staat hier zodat niemand het over een halfjaar alsnog "even" probeert.

Wat overblijft is wat sowieso nodig was: de tijd leren herkennen.

## Wat dit scherm doet

    aprendía
    (aprender, leren)
    -> presente | pretérito indefinido | pretérito imperfecto | pretérito perfecto | subjuntivo

Twaalf vormen, gespreid over de tijden die je open hebt. Geen voornaamwoord, geen zin, geen
bijwoord: de vorm is het enige wat je hebt.

Na je antwoord verschijnt dezelfde persoon van hetzelfde werkwoord in ALLE open tijden onder
elkaar. Dat is de contrastrij, en die bestond nergens in de app: je zag altijd één tijd tegelijk,
nooit aprendo / aprendí / aprendía / he aprendido naast elkaar.

## De vergelijking die dit oplevert

Het eindscherm zet de score naast die van "Wie is dit?". Dat zijn twee metingen van dezelfde
soort (herkennen, twaalf vragen, geen aanwijzing), dus die zijn eerlijk te vergelijken. De
vergelijking met de Conjugador was dat niet: dat is produceren tegenover herkennen.

    persoon hoog, tijd laag   -> het gat zit bij de tijden, en daar hoort het werk heen
    allebei hoog              -> het gat zit niet in het herkennen maar in het toepassen,
                                 en dan is de volgende stap een andere

## De pool

Alleen vormen die bij precies één tijd horen, gemeten over alle werkwoorden en alle personen:
888 van de 903. "hablamos" is zowel presente als indefinido en valt dus af, net als in v23.109.
Een vraag met twee goede antwoorden meet niets.

Minder dan twee open tijden en het scherm zegt eerlijk dat er nog niets te vergelijken valt, in
plaats van twaalf keer "presente" te vragen.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.113"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.113" not in src
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


# ============================================================ de motor
A_MOTOR = u'''/* v23.112: elke tegel draagt zelf wat er bij hem anders is.'''
N_MOTOR = u'''/* ================= WELKE TIJD IS DIT? (v23.113) =================

   De tweede helft van de omkering. v23.109 vroeg "hablamos -> wie?" en daar bleek Stefan gewoon
   goed in (10/12, tegenover 27/30 in de Conjugador: geen gat). Zijn gat zit bij de TIJD, en dat
   sluit aan op zijn echte struikelblok, indefinido tegenover imperfecto.

   Zie de kop van patch-v23.113 voor waarom hier geen bijwoord-experiment in zit: de zinnen in de
   app zijn er te scheef voor (18 met bijwoord tegenover 115 zonder, en 106 van de 133 in het
   presente), en zelf Spaans genereren om dat recht te trekken is precies waar deze app al eerder
   vormen mee zat te verzinnen.

   Alles hieronder leest uit conjVorm, VERBOS en CONJ_TIEMPOS. Geen vervoeging staat in deze code. */
var TIJDVORM_ID = "vorm.tijd";
var TIJDVORM_LEN = 12;
var tijdvormSpel = null;
var tijdvormKaartCache = null;

/* vorm -> de tijden waarin die vorm voorkomt, over ALLE werkwoorden en personen. Een vorm die in
   twee tijden voorkomt (hablamos is presente én indefinido) kan geen vraag zijn: dan zijn er twee
   goede antwoorden en meet je niets. Zelfde regel als de pool van v23.109. */
function tijdvormKaart(){
  if(tijdvormKaartCache) return tijdvormKaartCache;
  var kaart = {};
  CONJ_TIEMPOS.forEach(function(x){
    VERBOS.forEach(function(v){
      for(var i = 0; i < 6; i++){
        var f = conjVorm(v, i, x.id);
        if(!f) continue;
        if(!kaart[f]) kaart[f] = [];
        if(kaart[f].indexOf(x.id) === -1) kaart[f].push(x.id);
      }
    });
  });
  tijdvormKaartCache = kaart;
  return kaart;
}
function tijdvormPool(){
  var open = conjOpenTijden(), kaart = tijdvormKaart(), pool = [], dubbel = 0, totaal = 0;
  open.forEach(function(t){
    conjVerbPool(t).forEach(function(v){
      for(var p = 0; p < 6; p++){
        var f = conjVorm(v, p, t);
        if(!f) continue;
        totaal++;
        if(kaart[f] && kaart[f].length === 1) pool.push({v:v, p:p, t:t, vorm:f});
        else dubbel++;
      }
    });
  });
  return {items:pool, dubbel:dubbel, totaal:totaal, tijden:open};
}

/* Een ronde van twaalf, gespreid over de open tijden. Zonder die spreiding zou een ronde acht keer
   presente kunnen zijn, en dan meet je één tijd in plaats van het onderscheid ertussen. */
function tijdvormStart(){
  var pool = tijdvormPool();
  var perTijd = {};
  pool.tijden.forEach(function(t){ perTijd[t] = []; });
  geschud(pool.items).forEach(function(x){ if(perTijd[x.t]) perTijd[x.t].push(x); });
  var rij = [], ronde = 0;
  while(rij.length < TIJDVORM_LEN && ronde < 40){
    var iets = false;
    for(var i = 0; i < pool.tijden.length && rij.length < TIJDVORM_LEN; i++){
      var lijst = perTijd[pool.tijden[i]];
      if(lijst && lijst.length > ronde){ rij.push(lijst[ronde]); iets = true; }
    }
    if(!iets) break;
    ronde++;
  }
  tijdvormSpel = {rij:geschud(rij), i:0, goed:0, gekozen:null, tijden:pool.tijden,
                  dubbel:pool.dubbel, totaal:pool.totaal};
  return tijdvormSpel;
}
function tijdvormAntwoord(t){
  if(!tijdvormSpel || tijdvormSpel.gekozen !== null) return;
  tijdvormSpel.gekozen = t;
  if(t === tijdvormSpel.rij[tijdvormSpel.i].t) tijdvormSpel.goed++;
  renderFunTijdvorm();
}
function tijdvormVolgende(){
  if(!tijdvormSpel) return;
  tijdvormSpel.i++;
  tijdvormSpel.gekozen = null;
  if(tijdvormSpel.i >= tijdvormSpel.rij.length) brokRonde(TIJDVORM_ID, tijdvormSpel.goed, tijdvormSpel.rij.length);
  renderFunTijdvorm();
}
function tijdvormUitslag(goed, totaal){
  var pct = Math.round((goed / totaal) * 100);
  if(pct >= 90) return ct("Je leest de tijd uit de vorm. Dat is de stap waar de rest op rust: pas als je ziet welke tijd er staat, kun je leren kiezen welke er hoort te staan.",
                          "You read the tense from the form. That is the step everything else rests on: only when you can see which tense is there can you learn to choose which one belongs.");
  if(pct >= 60) return ct("Half. Sommige tijden herken je, andere lopen door elkaar. Kijk op het antwoordscherm welke rijen op elkaar lijken: daar zit je verwarring.",
                          "Half. You recognise some tenses and mix up others. Look at the answer screen to see which rows resemble each other: that is where the confusion sits.");
  return ct("Hier zit het gat. Je kunt de vormen wel maken als de app je vertelt welke tijd hij wil, maar je ziet niet welke tijd er staat. Dat is een andere oefening dan meer vervoegen.",
            "This is the gap. You can produce the forms when the app tells you which tense it wants, but you cannot see which tense is in front of you. That needs a different exercise than more conjugating.");
}

function renderFunTijdvorm(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var kop = "<h2>" + ct("Welke tijd is dit? \\u23f3", "Which tense is this? \\u23f3") + "</h2>";
  var terug = function(){ funView = null; tijdvormSpel = null; renderFun(); };

  /* Met \u00e9\u00e9n open tijd valt er niets te onderscheiden en zou dit scherm twaalf keer hetzelfde
     antwoord vragen. Dan liever eerlijk zeggen dat het er nog niet is. */
  if(conjOpenTijden().length < 2){
    el.innerHTML = kop + "<p class='muted'>" +
      ct("Je hebt nog maar \u00e9\u00e9n tijd open staan, dus er valt nog niets te onderscheiden. Kom terug zodra je in de Conjugador bij de verleden tijd bent.",
         "You only have one tense unlocked, so there is nothing to tell apart yet. Come back once you reach the past tense in Conjugador.") + "</p>" +
      "<div class='row' style='margin-top:10px'><button class='mini' id='btnFunTerug'>" + fx("terug") + "</button></div>";
    var b0 = document.getElementById("btnFunTerug");
    if(b0) b0.onclick = terug;
    return;
  }

  if(!tijdvormSpel) tijdvormStart();
  var totaal = tijdvormSpel.rij.length;

  if(tijdvormSpel.i >= totaal){
    var st = brokLees(TIJDVORM_ID);
    var pers = brokLees(OMKEER_ID);
    el.innerHTML = kop +
      "<div class='feedback " + (tijdvormSpel.goed >= totaal - 1 ? "ok" : tijdvormSpel.goed >= totaal - 4 ? "bijna" : "fout") + "' id='tvUitslag'>" +
        tijdvormSpel.goed + " / " + totaal + "</div>" +
      "<p class='muted'>" + tijdvormUitslag(tijdvormSpel.goed, totaal) + "</p>" +
      /* de eerlijke vergelijking: twee keer herkennen, twaalf vragen, geen aanwijzing. De
         Conjugador ernaast leggen zou produceren tegenover herkennen zijn, en dat is geen
         vergelijking maar een verwarring. */
      (pers.beste
        ? "<p class='muted' id='tvVergelijk' style='font-size:.9rem'><b>" +
            ct("Naast elkaar: ", "Side by side: ") + "</b>" +
            ct("bij \u201eWie is dit?\u201d (de persoon herkennen) haalde je ", "on \u201cWho is this?\u201d (recognising the person) your best was ") +
            pers.beste + "/12. " + ct("Hier, de tijd herkennen, ", "Here, recognising the tense, ") +
            tijdvormSpel.goed + "/12.</p>"
        : "") +
      (st.rondes > 1 ? "<p class='muted' style='font-size:.85rem'>" +
        ct("Je beste ronde tot nu toe: ", "Your best round so far: ") + st.beste + " / " + totaal + "</p>" : "") +
      "<div class='row' style='margin-top:10px'>" +
        "<button class='primary' id='btnTvNieuw'>" + ct("Nog een ronde", "Another round") + "</button>" +
        "<button class='ghost' id='btnFunTerug'>" + fx("terug") + "</button></div>";
    document.getElementById("btnTvNieuw").onclick = function(){ tijdvormStart(); renderFunTijdvorm(); };
    document.getElementById("btnFunTerug").onclick = terug;
    return;
  }

  var q = tijdvormSpel.rij[tijdvormSpel.i];
  var af = tijdvormSpel.gekozen !== null;
  var goed = af && tijdvormSpel.gekozen === q.t;
  var rijtje = "";
  if(af){
    /* de contrastrij: dezelfde persoon van hetzelfde werkwoord in alle open tijden onder elkaar.
       Die bestond nergens in de app; je zag altijd \u00e9\u00e9n tijd tegelijk en dus nooit aprendo naast
       aprend\u00ed naast aprend\u00eda. Precies dat naast elkaar zetten is waar het onderscheid vandaan komt. */
    rijtje = "<table style='width:100%; margin-top:10px'>" +
      tijdvormSpel.tijden.map(function(t){
        var mij = t === q.t;
        var x = conjTiempo(t);
        return "<tr" + (mij ? " style='background:var(--green-soft)'" : "") + ">" +
          "<td class='muted' style='font-size:.8rem'>" + (x ? x.es : t) + "<br><span style='font-size:.75rem'>" + (x ? ct(x.nl, x.en) : "") + "</span></td>" +
          "<td" + (mij ? " style='font-weight:700'" : "") + ">" + conjVorm(q.v, q.p, t) + (mij ? " \\u2190" : "") + "</td></tr>";
      }).join("") + "</table>" +
      "<p class='muted' style='font-size:.8rem; margin-top:4px'>" +
        ct("Dezelfde persoon (" + CONJ_PRONOMBRES[q.p] + "), alle tijden die je open hebt.",
           "Same person (" + CONJ_PRONOMBRES[q.p] + "), every tense you have unlocked.") + "</p>";
  }

  el.innerHTML = kop +
    "<span class='kicker'>" + ct("Vorm ", "Form ") + (tijdvormSpel.i + 1) + "/" + totaal + "</span>" +
    (tijdvormSpel.i === 0 && !af
      ? "<p class='muted'>" + ct("Geen zin, geen bijwoord, geen voornaamwoord. Alleen de vorm. In de Conjugador stáát de tijd in de vraag, dus daar hoef je hem nooit te lezen.",
                                 "No sentence, no adverb, no pronoun. Just the form. In Conjugador the tense is given in the question, so you never have to read it.") + "</p>"
      : "") +
    "<div class='card' style='text-align:center; margin:10px 0'>" +
      "<p class='big' style='margin:4px 0' id='tvVorm'>" + q.vorm + "</p>" +
      "<p class='muted' style='margin:0; font-size:.85rem'>" + q.v.inf + " <span style='font-weight:400'>(" + conjGloss(q.v) + ")</span></p>" +
    "</div>" +
    (af
      ? "<div class='feedback " + (goed ? "ok" : "fout") + "'>" +
          (goed ? ct("Goed \\u2713", "Correct \\u2713")
                : ct("Nog niet. Het is: ", "Not yet. It is: ") + "<b>" + conjTiempoNaam(q.t) + "</b>") +
        "</div>" + rijtje +
        "<div class='row' style='margin-top:10px'><button class='primary' id='btnTvVerder'>" +
          (tijdvormSpel.i + 1 >= totaal ? ct("Uitslag \\u2192", "Result \\u2192") : ct("Volgende \\u2192", "Next \\u2192")) + "</button></div>"
      : "<div id='tvKnoppen' style='display:flex; flex-direction:column; gap:8px; margin-top:6px'>" +
          tijdvormSpel.tijden.map(function(t){
            var x = conjTiempo(t);
            return "<button type='button' class='ghost tv-t' data-t='" + t + "' style='min-height:52px'>" +
              (x ? x.es : t) + "<br><span class='muted' style='font-weight:400; font-size:.78rem'>" + (x ? ct(x.nl, x.en) : "") + "</span></button>";
          }).join("") + "</div>") +
    "<div class='row' style='margin-top:10px'><button class='mini' id='btnFunTerug'>" + fx("terug") + "</button></div>";

  Array.prototype.forEach.call(el.querySelectorAll(".tv-t"), function(b){
    b.onclick = function(){ tijdvormAntwoord(b.getAttribute("data-t")); };
  });
  var vb = document.getElementById("btnTvVerder");
  if(vb) vb.onclick = tijdvormVolgende;
  var tb = document.getElementById("btnFunTerug");
  if(tb) tb.onclick = terug;
}

/* v23.112: elke tegel draagt zelf wat er bij hem anders is.'''
rep(A_MOTOR, N_MOTOR)

# ============================================================ de tegel
A_TEGEL = u'''    {v:"mem",     id:"ftMem",     e:"\\ud83c\\udccf",            t:"Memory \\u00b7 Parejas",  s:fx("meS")},'''
N_TEGEL = u'''    /* v23.113: de tweede helft van de omkering. Wie is dit? vraagt de persoon, deze de tijd. */
    {v:"tijdvorm", id:"ftTijdvorm", e:"\\u23f3",                t:ct("Welke tijd is dit?","Which tense is this?"), s:ct("Een vervoegde vorm zonder zin en zonder bijwoord: in welke tijd staat hij?","A conjugated form with no sentence and no adverb: which tense is it in?"), gezien:false, verse:function(){ tijdvormSpel = null; }},
    {v:"mem",     id:"ftMem",     e:"\\ud83c\\udccf",            t:"Memory \\u00b7 Parejas",  s:fx("meS")},'''
rep(A_TEGEL, N_TEGEL)

# ============================================================ de router
A_ROUTE = u'''  if(funView === "omkeer"){ renderFunOmkeer(); return; }   // v23.109'''
N_ROUTE = u'''  if(funView === "omkeer"){ renderFunOmkeer(); return; }   // v23.109
  if(funView === "tijdvorm"){ renderFunTijdvorm(); return; }   // v23.113'''
rep(A_ROUTE, N_ROUTE)

# ============================================================ uit de dagportie
A_DAG = u'''var DAGSPEL_UIT = {avt:1, duel:1, brok:1, omkeer:1};'''
N_DAG = u'''var DAGSPEL_UIT = {avt:1, duel:1, brok:1, omkeer:1, tijdvorm:1};'''
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
