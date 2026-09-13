#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.254 - de vraagkant droeg het antwoord, en het doosje telde alleen wat misging
#
# Stefan, 13 september, vier punten in een adem:
#
#   1. "nog te vaak bij woordjes zie ik al een hint."
#   2. "het helpt om ook een simpele zin (context) te zien, die kan dan ook weer terugkomen bij de
#      woordjes."
#   3. "ik denk dat het beter is om van nederlands naar spaans te gaan (produceren) in plaats van
#      andersom (herkennen), dus dit zou de default moeten zijn."
#   4. "grammatica: ik blijf te lang hangen bij een doosje. Een fout en ik kom niet verder (zie
#      bijv el en la). Soms maak ik een slordigheidsfoutje of weet ik iets niet, maar als je niet
#      alleen de fouten maar ook wanneer het goed gaat telt zul je zien dat ik dit allang gehad heb.
#      Bij grammatica is het denk ik ook goed om de toetsen wat uitgebreider te doen. Echt even een
#      lesje waarbij je de instructie nog een keer kunt lezen, een of meerdere vragen krijgt om te
#      toetsen of je de regel snapt en daarna wat meerkeuzevragen om de toepassing te toetsen. Nu
#      zijn het maar twee vragen."
#
# Het zijn er vier, maar het zijn twee paren. 1 en 3 zijn dezelfde fout van twee kanten, en 2 en 4
# ook.
#
# ================ EERST GEMETEN ================
#
# EEN. DE HINT ZIT IN DE BRON, NIET IN EEN KAARTJE.
#
# FREQ is het woordenboek achter de leesplank: 4219 rijen. Geteld:
#
#     856 noemen de infinitief tussen haakjes   "sale = hij/zij gaat weg/uit (van salir)"
#     239 zetten een Spaanse uitdrukking achter een isgelijkteken
#                                               "encima = bovenop; encima de = boven op"
#     330 herhalen het Spaanse woord zelf       "mamá = mama"
#
# Allebei de kaartjes op Stefans schermafbeelding staan in die lijst, precies zo. In de ingebouwde
# woordenlijsten (2250 woorden) staan er nog eens 26 met "(van X)", waarvan er 12 de stam van het
# antwoord weggeven: "encontrado = gevonden (van encontrar)".
#
# En geen van die rijen is FOUT. Ze zijn geschreven om NAAST het Spaanse woord te staan, als tooltip
# terwijl je een hoofdstuk leest. Daar is "(van salir)" precies de goede toevoeging. Maar wie zo'n
# woord aantikt zet hem in zijn stapel (v23.133), en dan wordt de tooltip de VRAAG, met het Spaans
# als antwoord.
#
#     Een tekst die geschreven is om naast het antwoord te staan, is geen vraag.
#
# Dat is dezelfde vorm als de rest van deze weken: het feit klopt, maar het staat op een plek waar
# het iets anders betekent. v23.246 (een index die niet is wat hij lijkt), v23.249 (de zin die
# beoordeeld werd ging niet mee), v23.252 (de tijd stond in een tekst en niet in een veld).
#
# TWEE. EN DE ERGSTE PLEK IS DE LAATSTE STAP.
#
# renderWordCheck() is de enige stap in de hele app die je niet kunt bluffen: je typt het Spaanse
# woord, en het staat nergens op het scherm. Die stap toont wTrans(w), onbewerkt. Daar stond de stam
# dus in de vraag.
#
# En die stap is ALTIJD productief, ongeacht S.dir. Dat is punt 3 al half beantwoord door de app
# zelf: de laatste stap toetst produceren, en alle kaartjes ervoor oefenden standaard het
# omgekeerde. defaultState() staat op dir:"es-nl".
#
# DRIE. DE ZIN WAARIN JE HET WOORD VOND, WORDT WEGGEGOOID.
#
#     282 van de 2250 woorden hebben een voorbeeldzin (w.ej)
#       0 van de woorden die je ZELF opzoekt hebben er een
#
# En dat laatste is het pijnlijke: elk woord uit S.mijn komt uit een zin die je op dat moment aan
# het lezen was. De zin staat op het scherm, de tik gaat eroverheen, en wat er wordt opgeslagen is
# {es, nl, d}. De zin is er wel en gaat niet mee.
#
# VIER. HET DOOSJE MEET JE LAATSTE BEURT, NIET JE KENNIS.
#
# 300 lopen van 30 dagen gesimuleerd met de ECHTE gramBij(), op genero (vijf patronen, zes
# antwoorden per dag):
#
#     goed        eindigt op doos 0      haalt doos 5
#     100%               0%                  100%
#      97%              22%                   29%
#      93%              45%                    6%
#      85%              68%                    0%
#
# Een onderwerp dat je 93 procent goed doet staat bijna de helft van de tijd op doos 0. Alleen een
# FOUTLOZE loop komt betrouwbaar boven. Twee dingen samen doen dat: één misser vandaag zet box op 0,
# en een concept is zo sterk als zijn ZWAKSTE van vijf patroondoosjes. Met vijf doosjes meet hij dus
# je slechtste laatste beurt.
#
# Op Stefans scherm stond het naast elkaar: "doos 0/5 · 93% goed deze week".
#
#     Een cijfer dat naast het oordeel staat en er niet in meetelt, is een verwijt.
#
# En st.goed/st.fout worden wél bijgehouden, al sinds het begin. Ze werden alleen nooit gelezen door
# de regel die de doos zet.
#
# VIJF. EN WAT JE KRIJGT ALS JE VASTZIT, IS DE DUNSTE VERSIE DIE ER IS.
#
# Per onderwerp geteld wat de app aanbiedt:
#
#     de volle microles (gcBouw)      31 onderwerpen, 5 vragen, met de regel en een begripsvraag
#     de opfrisser (gcOpfrisBouw)     2 vragen, geen uitleg, geen regel
#
# De opfrisser is wat de dagles je geeft als een onderwerp op herhaling staat. Stefan telde goed. En
# het is precies andersom: hoe zwakker het doosje, hoe dunner de hulp.
#
# ================ WAT ER VERANDERT ================
#
# EEN. DE BETEKENIS WORDT IN TWEEEN GEKNIPT.
#
# kaartSplits(nl, es) geeft {vraag, rest}. Wat het antwoord verraadt gaat naar de ACHTERKANT, waar
# het hoort (net als w.meer sinds v23.100). De rest is de vraag.
#
# "Verraadt" wordt gemeten tegen het ECHTE antwoord en niet geraden aan de vorm:
#
#     "gevonden (van encontrar)"            -> vraag "gevonden",  rest "(van encontrar)"
#     "bovenop; encima de = boven op"       -> vraag "bovenop",   rest "encima de = boven op"
#     "hij/zij gaat weg/uit (van salir)"    -> vraag "hij/zij gaat weg/uit"
#     "lang (van lengte)"                   -> vraag "lang (van lengte)"     ONGEWIJZIGD
#
# Die laatste is de controle. "lengte" deelt geen stam met "alto", dus hij blijft staan: het is
# uitleg en geen hint.
#
#     Kijk eerst naar wat er STAAT, en pas daarna naar waar het op lijkt.
#
# Blijft er niets over (bij "mamá = mama" is de hele betekenis het antwoord), dan blijft de hele
# betekenis staan. Een lege vraag is erger dan een hint.
#
# TWEE. NL -> ES WORDT DE STANDAARD, EN DE KEUZE WORDT VOORTAAN VASTGELEGD.
#
# defaultState() gaat om. Voor wie de app al gebruikt is er migratie 5. Die kan niet zien of je
# es-nl ooit zelf hebt gekozen, want dat werd nergens opgeschreven: S.dir draagt de stand en niet de
# herkomst. Dat is nog een keer dezelfde fout, en hij wordt hier ook gerepareerd. De migratie zet
# iedereen die geen vlag heeft één keer om, en vanaf nu legt btnDir de keuze vast, zodat dit nooit
# meer over iemand heen gaat. De knop staat nog steeds onder elk kaartje.
#
# DRIE. DE ZIN GAAT MEE, EN KOMT MET EEN GAT TERUG.
#
# leesTekstHtml() knipt een alinea eerst in zinnen en onthoudt per woord in welke zin het stond
# (leesZinnen, naast leesWoorden). Tik je een woord aan en zet je het in je woorden, dan gaat die
# zin mee als w.ej: hetzelfde veld dat de kernwoorden al hebben, dus geen tweede soort.
#
# Op de VRAAGkant staat de zin met het antwoord eruit geknipt, en alleen als dat aantoonbaar gelukt
# is. Lukt het gat niet (het woord staat er in een andere vorm), dan komt de zin daar niet. Op de
# achterkant staat hij heel.
#
#     Een controlegeval hoor je te BOUWEN, niet te VINDEN. Hier: het gat wordt niet aangenomen maar
#     nagemeten, en de zin komt alleen langs als het antwoord er echt uit is.
#
# VIER. EEN MISSER TUSSEN BEWIJS DOOR IS EEN SLORDIGHEID.
#
# st.rij is nieuw: de laatste twaalf antwoorden op DIT doosje, nieuwste rechts, als "101111...".
# Twaalf tekens per doosje, en het is de eerste keer dat de doos naar je staat van dienst kijkt.
#
#     doosje met minstens 6 antwoorden en minstens 80% goed  ->  een misser kost EEN doos
#     alles daaronder                                        ->  een misser kost ALLE dozen
#
# Wat NIET verandert: een misser blijft een misser. De promotie gaat niet door en je ziet het morgen
# terug. De variant "altijd één stap omlaag" is in v23.208 voorgesteld en door Stefan afgewezen, en
# terecht: wie het onderwerp niet kent hoort naar nul. Het verschil is dat de app nu kijkt of je het
# kent, in plaats van het aan te nemen.
#
# Opnieuw gesimuleerd, zelfde 300 lopen, zelfde functie:
#
#     goed        doos 0 oud   doos 0 nieuw
#      97%           22%           (zie de suite)
#      93%           45%           (zie de suite)
#
# VIJF. DE OPFRISSER HANGT AAN HET DOOSJE, NIET AAN ZIJN NAAM.
#
#     doosje 1 of hoger  ->  twee vragen. Dit is een opfrisser en die hoort kort te zijn.
#     doosje 0           ->  de regel opnieuw, een begripsvraag, dan vier toepassingsvragen.
#
# Precies de volgorde die Stefan beschrijft. Er komt geen letter nieuwe tekst bij: GC_HULP heeft de
# kern en de ezelsbrug, het concept heeft c.uitleg en c.begrip, en gcMaakVragen maakt verse
# voorbeelden. Het bestond allemaal al en kwam alleen nooit langs op het moment dat het helpt.
#
#   python3 claude/patch-v23.254.py
import pathlib
import re
import sys

W = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / "claude"))
import patchhulp  # noqa: E402

APP = W / "index.html"
VER = W / "versie.txt"
GEPLAND = "v23.254"

src = APP.read_text(encoding="utf-8")
huidig = VER.read_text(encoding="utf-8").strip()
DOE_APP = "function kaartSplits(" not in src


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- EEN: de vraagkant mag het antwoord niet dragen ----------
    rep(
        """function wTrans(w){""",
        """/* ================= DE VRAAGKANT MAG HET ANTWOORD NIET DRAGEN (v23.254) =================

   Stefan, 13 september: "nog te vaak bij woordjes zie ik al een hint."

   Gemeten in FREQ, het woordenboek achter de leesplank, 4219 rijen:

       856 noemen de infinitief tussen haakjes   "sale = hij/zij gaat weg/uit (van salir)"
       239 zetten een Spaanse uitdrukking achter een isgelijkteken
                                                 "encima = bovenop; encima de = boven op"
       330 herhalen het Spaanse woord zelf       "mamá = mama"

   Plus 26 rijen met "(van X)" in de ingebouwde woordenlijsten, waarvan 12 de stam van het antwoord
   weggeven ("encontrado = gevonden (van encontrar)").

   Geen van die rijen is fout. Ze zijn geschreven om NÁÁST het Spaanse woord te staan, als tooltip
   terwijl je leest, en daar is "(van salir)" precies de goede toevoeging. Maar wie zo'n woord
   aantikt zet hem in zijn stapel (v23.133), en dan is de tooltip de VRAAG geworden.

       Een tekst die geschreven is om naast het antwoord te staan, is geen vraag.

   De betekenis wordt hier in tweeën geknipt. Wat het antwoord verraadt gaat naar de ACHTERKANT,
   waar het hoort (net als w.meer sinds v23.100); de rest is de vraag. En "verraadt" wordt gemeten
   tegen het echte antwoord, niet geraden aan de vorm: "lang (van lengte)" blijft staan, want
   "lengte" deelt geen stam met "alto".

       Kijk eerst naar wat er STAAT, en pas daarna naar waar het op lijkt.

   Blijft er niets over, dan blijft de hele betekenis staan. Een lege vraag is erger dan een hint. */
function kaartPlat(s){
  return stripAcc(String(s || "").toLowerCase()).replace(/[^a-z]+/g, " ").trim();
}
/* De woorden van het antwoord, accentloos. Alles van twee letters of langer telt mee: op een kaartje
   is "ir" net zo goed het antwoord als "encontrado". */
function kaartAntwoordDelen(es){
  var uit = [], i, d = kaartPlat(es).split(" ");
  for(i = 0; i < d.length; i++) if(d[i].length >= 2) uit.push(d[i]);
  return uit;
}
/* Dezelfde stam? Twee gelijke beginletters is genoeg en is met opzet grof: een kaartje is vaak een
   VORM terwijl de betekenis de INFINITIEF noemt (encontrado tegen "van encontrar", sale tegen "van
   salir", dado tegen "van dar"). Deze toets wordt alleen losgelaten op het woord binnen "(van X)",
   waar al vaststaat dat X het werkwoord is. In een gewone zin geldt de strengere toets hieronder. */
function kaartDeeltStam(a, b){
  if(!a || !b || a.length < 2 || b.length < 2) return false;
  return a.charAt(0) === b.charAt(0) && a.charAt(1) === b.charAt(1);
}
/* En soms deelt de infinitief geen letter met de vorm: "voy :: ik ga (van ir)", "es :: is (van
   ser)". Dan zegt de stam niets en de UITGANG alles: een woord op -ar, -er of -ir (met eventueel
   -se erachter) is een Spaanse infinitief.

   De korte werkwoorden (ir, ver, dar) halen die drempel niet, en daarvoor is VERBOS er: de
   werkwoordentabel van de app zelf. Liever de eigen gegevens bevragen dan een lijstje namen in een
   functie zetten, want zo'n lijstje is bij het volgende werkwoord alweer verouderd.

   Gemeten voordat deze regel erin ging, over alle 6469 betekenissen met een "(van X)" erin: hij
   raakt geen enkele Nederlandse toelichting. "lengte", "vloeistof", "iemand", "een straat", "mist",
   "een gerecht", "een wolf", "afstand/duur" en "een deur" blijven allemaal staan. */
var _kaartInf = null;
function kaartInfSet(){
  if(_kaartInf) return _kaartInf;
  _kaartInf = {};
  try {
    VERBOS.forEach(function(v){
      var i = kaartPlat(v.inf);
      if(i) _kaartInf[i] = 1;
    });
  } catch(e){}
  return _kaartInf;
}
function kaartIsInfinitief(w){
  var s = String(w || "");
  if(!s) return false;
  if(/^[a-z]{1,}(?:ar|er|ir)(?:se)?$/.test(s)) return true;
  return !!kaartInfSet()[s] || !!kaartInfSet()[s.replace(/se$/, "")];
}
/* Staat er een woord van het antwoord letterlijk in dit stuk tekst? Heel woord, geen stam: anders
   zou "de" uit "de acuerdo" op elk Nederlands lidwoord vallen. */
function kaartVerraadt(stuk, delen){
  var w = kaartPlat(stuk).split(" "), i, j;
  for(i = 0; i < w.length; i++){
    if(w[i].length < 2) continue;
    for(j = 0; j < delen.length; j++) if(w[i] === delen[j]) return true;
  }
  return false;
}
function kaartSplits(nl, es){
  var heel = String(nl || "");
  var delen = kaartAntwoordDelen(es);
  if(!heel || !delen.length) return {vraag:heel, rest:""};
  var weg = [], wegStuk = [];
  /* Eerst de haakjes. Twee soorten gaan eruit: "(van X)" waarin X het werkwoord van het antwoord is,
     en elk haakje waarin het antwoord letterlijk staat ("probleem (el problema!)"). Een haakje dat
     geen van beide doet is uitleg en blijft staan: "lang (van lengte)" bij alto. */
  var kaal = heel.replace(/\\s*\\(([^)]*)\\)/g, function(m, x){
    var binnen = String(x), inf = /^\\s*(?:van|from)\\s+/i.test(binnen);
    var w = kaartPlat(binnen).split(" "), i, j;
    if(inf){
      for(i = 0; i < w.length; i++){
        if(kaartIsInfinitief(w[i])){ weg.push(m.replace(/^\\s+/, "")); return ""; }
        for(j = 0; j < delen.length; j++){
          if(kaartDeeltStam(w[i], delen[j])){ weg.push(m.replace(/^\\s+/, "")); return ""; }
        }
      }
      return m;
    }
    if(kaartVerraadt(binnen, delen)){ weg.push(m.replace(/^\\s+/, "")); return ""; }
    return m;
  });
  /* Dan de losse stukken achter een puntkomma die het Spaanse woord zelf herhalen. */
  var houd = [];
  kaal.split(/\\s*;\\s*/).forEach(function(stuk){
    var s = stuk.replace(/\\s+/g, " ").trim();
    if(!s) return;
    if(kaartVerraadt(s, delen)){ weg.push(s); wegStuk.push(s); } else houd.push(s);
  });
  /* Blijft er niets over, dan is er nog één plek om te kijken: "digas = no digas = zeg niet (van
     decir)". Daar staat de Spaanse uitdrukking links van het isgelijkteken en de Nederlandse
     betekenis rechts, en die rechterkant is een prima vraag.

     Alleen de STUKKEN mogen hier terugkomen, niet de haakjes: die zijn er net uit gehaald omdat ze
     het werkwoord noemen, en via deze achterdeur weer binnenlaten zou dat ongedaan maken. Vandaar
     twee emmers in plaats van één. Gemeten toen ze nog één emmer waren: 27 rijen kregen hun
     "(van decir)" langs deze weg terug op de vraagkant. */
  if(!houd.length){
    wegStuk.forEach(function(stuk){
      stuk.split(/\\s*=\\s*/).forEach(function(kant){
        var k = kant.replace(/\\s+/g, " ").trim();
        if(k && !kaartVerraadt(k, delen) && houd.indexOf(k) === -1) houd.push(k);
      });
    });
  }
  var vraag = houd.join("; ").replace(/\\s+([,;])/g, "$1").replace(/[,;]+\\s*$/, "").trim();
  if(!vraag) return {vraag:heel, rest:""};
  return {vraag:vraag, rest:weg.join("; ")};
}
function kaartVraag(w){ return kaartSplits(wTrans(w), w && w.es).vraag; }
function kaartRest(w){ return kaartSplits(wTrans(w), w && w.es).rest; }
/* ================= EN EEN ZIN OM HET IN TE ZIEN (v23.254) =================

   Stefan: "de focus moet wel het woordje zijn maar het helpt om ook een simpele zin (context) te
   zien." Geteld: 282 van de 2250 woorden hebben een voorbeeldzin, en de woorden die je zelf opzoekt
   nul, terwijl elk van die woorden uit een zin kwam die op dat moment op je scherm stond.

   Op de vraagkant staat die zin met het antwoord eruit. En niet op goed vertrouwen: het gat wordt
   nagemeten, en lukt het niet (het woord staat er in een andere vorm), dan komt de zin daar niet.
   Op de achterkant staat hij heel. */
function kaartZinGat(zin, es){
  var z = String(zin || "");
  if(!z || !es) return "";
  var doelen = String(es).split("/"), raak = false, i, kaal, re;
  for(i = 0; i < doelen.length; i++){
    kaal = doelen[i].replace(/[^A-Za-z\\u00c0-\\u024f ]/g, " ").replace(/\\s+/g, " ").trim();
    if(kaal.length < 2) continue;
    re = new RegExp("(^|[^A-Za-z\\\\u00c0-\\\\u024f])(" + kaal.replace(/ /g, "\\\\s+") +
                    ")(?![A-Za-z\\\\u00c0-\\\\u024f])", "gi");
    if(re.test(z)){ z = z.replace(re, "$1___"); raak = true; }
  }
  if(!raak) return "";
  // de controle die telt: staat er echt niets van het antwoord meer in?
  if(kaartVerraadt(z, kaartAntwoordDelen(es))) return "";
  return z;
}
function kaartZinHtml(w, kant){
  if(!w || !w.ej) return "";
  var t = kant === "voor" ? kaartZinGat(w.ej, w.es) : String(w.ej);
  if(!t) return "";
  return "<p class='muted' style='margin:8px 2px 0; line-height:1.5'>" + t +
    (kant !== "voor" && profLang() === "nl" && w.ejnl
      ? "<br><span style='opacity:.65'>" + w.ejnl + "</span>" : "") + "</p>";
}
function wTrans(w){""",
    )

    # ---------- de drie plekken waar de Nederlandse kant de VRAAG is ----------
    # 1. de gewone kaart, voorkant
    rep(
        """  var front = S.dir==="es-nl" ? wCur.es : wTrans(wCur);
  var inFlow = !!(lesFlow && lesFlow.stap === "woorden");""",
        """  var front = S.dir==="es-nl" ? wCur.es : kaartVraag(wCur);
  var inFlow = !!(lesFlow && lesFlow.stap === "woorden");""",
    )
    rep(
        """    "<p class='muted'>"+(S.dir==="es-nl"?tt("watBetekent"):tt("hoeZegJe"))+"</p>"+
    kaartUitlegHtml("voor")+""",
        """    "<p class='muted'>"+(S.dir==="es-nl"?tt("watBetekent"):tt("hoeZegJe"))+"</p>"+
    (S.dir==="es-nl" ? "" : kaartZinHtml(wCur, "voor"))+
    kaartUitlegHtml("voor")+""",
    )
    # 2. de gewone kaart, achterkant: dezelfde vraag blijft staan, en wat eraf ging komt hier terug
    rep(
        """  var front = S.dir==="es-nl" ? wCur.es : wTrans(wCur);
  var back  = S.dir==="es-nl" ? wTrans(wCur) : wCur.es;""",
        """  var front = S.dir==="es-nl" ? wCur.es : kaartVraag(wCur);
  var back  = S.dir==="es-nl" ? wTrans(wCur) : wCur.es;
  /* v23.254: wat van de vraagkant af moest omdat het het antwoord verried, hoort hier. Precies
     dezelfde afspraak als w.meer sinds v23.100: naslag voor wie het antwoord al heeft. */
  var afgehaald = S.dir==="es-nl" ? "" : kaartRest(wCur);""",
    )
    rep(
        """    (wCur.meer ? "<p class='muted' style='margin:2px 2px 0; font-size:.9rem'>"+wCur.meer+"</p>" : "")+""",
        """    (afgehaald ? "<p class='muted' style='margin:2px 2px 0; font-size:.9rem'>"+afgehaald+"</p>" : "")+
    (wCur.meer ? "<p class='muted' style='margin:2px 2px 0; font-size:.9rem'>"+wCur.meer+"</p>" : "")+""",
    )
    # 3. de Laatste stap: de enige stap die je niet kunt bluffen
    rep(
        """    "<p class='big'>"+wTrans(w)+"</p>"+
    "<p class='muted'>"+ct("Hoe zeg je dat in het Spaans?","How do you say that in Spanish?")+"</p>"+""",
        """    /* v23.254: hier stond wTrans(w) onbewerkt, en dit is de enige stap in de app die je niet kunt
       bluffen: je typt het woord en het staat nergens op het scherm. Juist daar stond de stam van
       het antwoord in de vraag ("gevonden (van encontrar)"). Zie kaartSplits(). */
    "<p class='big'>"+kaartVraag(w)+"</p>"+
    "<p class='muted'>"+ct("Hoe zeg je dat in het Spaans?","How do you say that in Spanish?")+"</p>"+
    kaartZinHtml(w, "voor")+""",
    )
    rep(
        """      : "<p class='big es' style='margin:2px 0 0'>"+w.es+"</p>");""",
        """      : "<p class='big es' style='margin:2px 0 0'>"+w.es+"</p>"+
        (kaartRest(w) ? "<p class='muted' style='margin:2px 2px 0; font-size:.9rem'>"+kaartRest(w)+"</p>" : "")+
        kaartZinHtml(w, "achter"));""",
    )

    # ---------- TWEE: produceren is de standaard ----------
    rep(
        """dagStats:{}, dir:"es-nl", newIntro:{}""",
        """dagStats:{}, dir:"nl-es", newIntro:{}""",
    )
    rep(
        """  document.getElementById("btnDir").onclick = function(){ S.dir = S.dir==="es-nl"?"nl-es":"es-nl"; persist(); renderWord(); };""",
        """  /* v23.254: de KEUZE wordt vastgelegd, niet alleen de stand. Tot nu toe droeg S.dir alleen waar
     de schakelaar stond, en niet of jij hem daar had gezet. Daardoor kon migratie 5 niet zien wie
     es-nl bewust wilde. Vanaf nu wel, en gaat er nooit meer een standaard over iemand heen. */
  document.getElementById("btnDir").onclick = function(){
    S.dir = S.dir==="es-nl"?"nl-es":"es-nl"; S.dirGekozen = 1; persist(); renderWord();
  };""",
    )
    rep("""var SCHEMA = 4;""", """var SCHEMA = 5;""")
    rep(
        """    return weg;
  }}
];
""",
        """    return weg;
  }},
  {naar: 5, wat: "de standaardrichting van de woordkaartjes op produceren zetten", doe: function(s){
    /* v23.254. Stefan: "ik denk dat het beter is om van nederlands naar spaans te gaan
       (produceren) in plaats van andersom (herkennen), dus dit zou de default moeten zijn."

       De app was het zelf al met hem eens en zei het nergens: renderWordCheck(), de Laatste stap,
       toetst ALTIJD productief, ongeacht S.dir. Alle kaartjes ervoor oefenden standaard het
       omgekeerde.

       Deze migratie kan niet zien of je es-nl ooit zelf hebt gekozen, want dat werd nergens
       opgeschreven: S.dir droeg de stand en niet de herkomst. Dus gaat iedereen zonder vlag één keer
       om, en legt btnDir de keuze vanaf nu vast zodat dit niet nog een keer gebeurt. De schakelaar
       staat onder elk kaartje, dus terug is één tik. */
    if(s.dirGekozen) return 0;
    if(s.dir !== "es-nl") return 0;
    s.dir = "nl-es";
    return 1;
  }}
];
""",
    )

    # ---------- DRIE: de zin waarin je het woord vond, gaat mee ----------
    rep(
        """function leesTekstHtml(p){
  var veilig = String(p).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return veilig.replace(/([A-Za-z\\u00c0-\\u024f]+)/g, function(m){
    var i = leesWoorden.length;
    leesWoorden.push(m);
    return "<span class='lw' data-lw=\\""+m+"\\" data-li='"+i+"'>"+m+"</span>";
  });
}""",
        """/* ================= DE ZIN WAARIN JE HET WOORD VOND (v23.254) =================

   Stefan: "het helpt om ook een simpele zin (context) te zien, die kan dan ook weer terugkomen bij
   de woordjes."

   Geteld: 282 van de 2250 woorden hebben een voorbeeldzin, en de woorden die je zelf opzoekt nul.
   Terwijl elk van die woorden uit een zin komt die op dat moment op je scherm staat. De zin is er,
   de tik gaat eroverheen, en wat er wordt opgeslagen is {es, nl, d}.

   leesZinnen loopt precies gelijk op met leesWoorden: één rij per aantikbaar woord, met de zin
   waarin dat woord stond. Geen tweede bron en geen tweede index.

   De splitsing moet SLUITEND zijn, anders verandert de tekst op het scherm. Daarom wordt hij
   nagemeten in plaats van aangenomen: past hij niet precies op de alinea, dan valt deze functie
   terug op het oude gedrag en is er alleen geen zin bekend. */
var leesZinnen = [];
function leesZinDelen(p){
  var d = String(p).match(/[^.!?\\u2026]*[.!?\\u2026]+[\\s]*|[^.!?\\u2026]+$/g);
  if(!d || !d.length) return null;
  if(d.join("") !== String(p)) return null;   // niet sluitend: dan liever geen zinnen dan een gat
  return d;
}
function leesTekstHtml(p){
  var delen = leesZinDelen(p) || [String(p)];
  return delen.map(function(zin){
    var kort = zin.replace(/\\s+/g, " ").trim();
    var veilig = String(zin).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return veilig.replace(/([A-Za-z\\u00c0-\\u024f]+)/g, function(m){
      var i = leesWoorden.length;
      leesWoorden.push(m);
      leesZinnen[i] = kort;
      return "<span class='lw' data-lw=\\""+m+"\\" data-li='"+i+"'>"+m+"</span>";
    });
  }).join("");
}""",
    )
    rep(
        """  leesWoorden = [];
  /* v23.81: enkele regelovergangen worden <br>.""",
        """  leesWoorden = []; leesZinnen = [];
  /* v23.81: enkele regelovergangen worden <br>.""",
    )
    # de zin hangen aan het woord dat nu open staat
    rep(
        """  leesNu = {woord:woord, doel:(b.uitdrukking ? null : mijnDoel(b))};""",
        """  /* v23.254: en de zin waarin het stond. Hij komt uit leesZinnen en niet uit de DOM, om dezelfde
     reden als leesWoorden: uit de opmaak teruglezen zou betekenen dat de opmaak bepaalt wat je
     leert. Een zin van boven de 160 tekens is geen context meer maar een alinea. */
  var nuZin = "";
  try {
    if(span && span.getAttribute("data-li") !== null){
      nuZin = String(leesZinnen[+span.getAttribute("data-li")] || "");
      if(nuZin.length > 160) nuZin = "";
    }
  } catch(e){ nuZin = ""; }
  leesNu = {woord:woord, zin:nuZin, doel:(b.uitdrukking ? null : mijnDoel(b))};""",
    )
    rep(
        """function mijnBij(d){
  if(!d || !d.id) return false;
  if(mijnHeeft(d)) return false;
  if(d.eigen){
    S.mijn = S.mijn || {};
    S.mijn[d.plat] = {es:d.es, nl:d.nl, d:today()};""",
        """function mijnBij(d, zin){
  if(!d || !d.id) return false;
  if(mijnHeeft(d)) return false;
  if(d.eigen){
    S.mijn = S.mijn || {};
    /* v23.254: z is de zin waarin je het woord tegenkwam. Hij gaat verderop als w.ej de pool in,
       hetzelfde veld dat de kernwoorden al hebben, zodat geen enkele andere plek in de app hoeft te
       weten dat dit woord anders is ontstaan. */
    S.mijn[d.plat] = {es:d.es, nl:d.nl, d:today(), z:String(zin || "") || undefined};""",
    )
    rep(
        """    uit.push({id:mijnWoordId(k), es:m[k].es, nl:m[k].nl, en:m[k].en || m[k].nl, tag:"mijn"});""",
        """    uit.push({id:mijnWoordId(k), es:m[k].es, nl:m[k].nl, en:m[k].en || m[k].nl, tag:"mijn",
              ej:m[k].z || undefined});""",
    )
    rep(
        """  var nieuw = mijnBij(d);
  var el = document.getElementById("leesUitleg");""",
        """  var nieuw = mijnBij(d, leesNu && leesNu.zin);
  var el = document.getElementById("leesUitleg");""",
    )

    # ---------- VIER: het doosje leest je staat van dienst ----------
    rep(
        """function gramBij(cid, goed, keuzes, pi, kanaal){""",
        """/* ================= EEN MISSER TUSSEN BEWIJS DOOR IS EEN SLORDIGHEID (v23.254) =================

   Stefan, 13 september: "ik blijf te lang hangen bij een doosje. Een fout en ik kom niet verder
   (zie bijv el en la). Soms maak ik een slordigheidsfoutje of weet ik iets niet, maar als je niet
   alleen de fouten maar ook wanneer het goed gaat telt zul je zien dat ik dit allang gehad heb."

   300 lopen van 30 dagen gesimuleerd met de echte gramBij(), op genero (vijf patronen, zes
   antwoorden per dag):

       goed        eindigt op doos 0      haalt doos 5
       100%               0%                  100%
        97%              22%                   29%
        93%              45%                    6%
        85%              68%                    0%

   Alleen een FOUTLOZE loop komt betrouwbaar boven. Twee dingen samen doen dat: één misser vandaag
   zet de doos op 0, en een concept is zo sterk als zijn zwakste van vijf patroondoosjes. De doos
   meet dus je slechtste laatste beurt en niet je kennis. Op Stefans scherm stond het naast elkaar:
   "doos 0/5 · 93% goed deze week".

       Een cijfer dat naast het oordeel staat en er niet in meetelt, is een verwijt.

   st.goed en st.fout werden al bijgehouden sinds het begin. Ze werden alleen nooit gelezen door de
   regel die de doos zet, en als totaal zijn ze ook niet bruikbaar: twintig goede antwoorden van
   drie maanden geleden zeggen niets over vandaag. st.rij wel: de laatste twaalf antwoorden op DIT
   doosje, nieuwste rechts.

   Wat NIET verandert: een misser blijft een misser. De promotie gaat niet door en je ziet het
   morgen terug. De variant "altijd één stap omlaag" is in v23.208 voorgesteld en door Stefan
   afgewezen, en terecht: wie het onderwerp niet kent hoort naar nul. Het verschil is dat de app nu
   kijkt of je het kent in plaats van het aan te nemen. */
var GRAM_RIJ = 12;         // zoveel antwoorden per doosje worden onthouden
var GRAM_RIJ_MIN = 6;      // minder dan dit is geen staat van dienst, en dan geldt de oude regel
var GRAM_RIJ_EIS = 0.8;    // en dit aandeel goed maakt van een misser een slordigheid
function gramRijBij(st, goed){
  st.rij = (String(st.rij || "") + (goed ? "1" : "0")).slice(-GRAM_RIJ);
  return st.rij;
}
/* Geeft null als er te weinig ligt om iets te vinden. Nul is geen bericht, en te weinig ook niet.

   LEEST st.rijVoor EN NIET st.rij, en dat verschil is de hele functie. rijVoor is de rij zoals hij
   er vanochtend uitzag; rij loopt vandaag door. Zou het oordeel op rij staan, dan telde een misser
   minder zwaar zodra je er die dag een paar makkelijke goede antwoorden omheen zette. Dat is
   precies wat de kop van v23.170 hierboven al een keer heeft rechtgezet: wat je op dezelfde dag nog
   oefent is besmet door wat je net gezien hebt.

   De poort vond dit, niet ik. pw-doos.js speelt een dag na met acht antwoorden waarvan één fout, en
   die eindigde op doos 1 in plaats van 0. */
function gramStaat(st){
  var r = String((st && st.rijVoor) || ""), goed = 0, i;
  if(r.length < GRAM_RIJ_MIN) return null;
  for(i = 0; i < r.length; i++) if(r.charAt(i) === "1") goed++;
  return {n:r.length, goed:goed, deel:goed / r.length};
}
function gramSlordig(st){
  var s = gramStaat(st);
  return !!(s && s.deel >= GRAM_RIJ_EIS);
}
function gramBij(cid, goed, keuzes, pi, kanaal){""",
    )
    rep(
        """    st.boxVoor = st.box || 0;    // waar stond hij toen vandaag begon""",
        """    st.boxVoor = st.box || 0;    // waar stond hij toen vandaag begon
    st.rijVoor = st.rij || "";   // v23.254: en zo zag je staat van dienst er vanochtend uit""",
    )
    rep(
        """  if(goed) st.dagGoed = (st.dagGoed || 0) + 1;
  else st.dagMis = (st.dagMis || 0) + 1;

  if(st.dagMis){""",
        """  if(goed) st.dagGoed = (st.dagGoed || 0) + 1;
  else st.dagMis = (st.dagMis || 0) + 1;
  gramRijBij(st, !!goed);   // v23.254: de staat van dienst op DIT doosje, voordat er geoordeeld wordt

  if(st.dagMis){""",
    )
    rep(
        """    st.half = 0;
    st.box = 0;
    st.due = addDays(today(), 1);
  } else if(gramHalfBewijs(keuzes)""",
        """    /* v23.254: hoe ver je terugvalt hangt af van je staat van dienst op dit doosje. Minstens zes
       antwoorden en minstens tachtig procent goed: dan kost een misser één doos. Alles daaronder
       valt naar nul, precies zoals hiervoor. */
    st.half = 0;
    st.box = gramSlordig(st) ? Math.max(0, (st.boxVoor || 0) - 1) : 0;
    st.due = addDays(today(), 1);
  } else if(gramHalfBewijs(keuzes)""",
    )

    # ---------- VIJF: de opfrisser hangt aan het doosje ----------
    rep(
        """var GC_OPFRIS_VRAGEN = 2;""",
        """var GC_OPFRIS_VRAGEN = 2;
/* v23.254: en zoveel als het doosje op nul staat. Zie gcOpfrisBouw(). */
var GC_OPFRIS_LES_VRAGEN = 4;""",
    )
    rep(
        """  if(vragen.length < GC_OPFRIS_VRAGEN) return null;
  var naam = ct(c.naam, c.naamEn || c.naam);
  return {""",
        """  if(vragen.length < GC_OPFRIS_VRAGEN) return null;
  var naam = ct(c.naam, c.naamEn || c.naam);
  /* ================= EN ALS HET DOOSJE OP NUL STAAT, IS TWEE VRAGEN NIET WAT JE NODIG HEBT =======

     Stefan, 13 september: "bij grammatica is het denk ik ook goed om de toetsen wat uitgebreider te
     doen. Echt even een lesje waarbij je de instructie nog een keer kunt lezen, een of meerdere
     vragen krijgt om te toetsen of je de regel snapt en daarna wat meerkeuzevragen om de toepassing
     te toetsen. Nu zijn het maar twee vragen."

     Hij telde goed. Geteld over alle 31 onderwerpen: de volle microles geeft er vijf, met de regel
     en een begripsvraag erbij. De opfrisser geeft er twee, zonder uitleg en zonder regel. En de
     opfrisser is precies wat je krijgt als een onderwerp op herhaling staat, dus hoe zwakker het
     doosje, hoe dunner de hulp. Dat is andersom.

     Vanaf nu hangt de maat aan het doosje en niet aan de naam van het onderdeel:

         doosje 1 of hoger  ->  twee vragen. Dit is een opfrisser en die hoort kort te zijn.
         doosje 0           ->  de regel opnieuw, een begripsvraag, dan vier toepassingsvragen.

     Er komt geen letter nieuwe tekst bij. GC_HULP heeft de kern en de ezelsbrug, het concept heeft
     c.uitleg en c.begrip, gcMaakVragen maakt verse voorbeelden. Het bestond allemaal al en kwam
     alleen nooit langs op het moment dat het helpt. */
  /* En dan de val die de poort eruit haalde, en het is dezelfde als in v23.251.

     Doos 0 betekent twee dingen: "hier heb ik nog nooit een vraag van gehad" en "hier ben ik op
     teruggevallen". Een tak die die twee hetzelfde behandelt geeft een beginner een herhalingsles
     over iets wat hij nog moet leren. Vier suites zeiden dat tegelijk (pw-drill, pw-gramflow,
     pw-leermachine, pw-patroondoos): die bouwen een opfrisser op een verse staat, en kregen een
     lesje.

     Dus niet "de doos staat op nul" maar "de doos staat op nul EN er ligt genoeg achter om dat een
     terugval te noemen". Dezelfde drempel als gramStaat() hierboven, want het is dezelfde vraag:
     hoeveel antwoorden heb je nodig voordat een cijfer iets zegt. */
  var doosje = null;
  try { doosje = gramRuw((pi === null || isNaN(pi)) ? cid : gramSleutel(cid, pi)); }
  catch(e){ doosje = null; }
  var vast = !!doosje && (doosje.box || 0) === 0 &&
             ((doosje.goed || 0) + (doosje.fout || 0)) >= GRAM_RIJ_MIN;
  if(vast && c.begrip){
    var meer = [];
    try {
      meer = (pi === null || isNaN(pi))
        ? gcMaakVragen(c, GC_OPFRIS_LES_VRAGEN)
        : gcVragenUitPatroon(c, pi, GC_OPFRIS_LES_VRAGEN);
    } catch(e){ meer = []; }
    if(meer.length){
      var beg = gcSchud({v:c.begrip.v, vEn:c.begrip.vEn, o:c.begrip.o.slice(),
                         oEn:c.begrip.oEn ? c.begrip.oEn.slice() : null,
                         g:c.begrip.g, w:c.begrip.w, wEn:c.begrip.wEn});
      return {
        icon: c.icon || "\\ud83d\\udd01",
        id: id, concept: cid, opfris: true, lesje: true,
        titel: ct("Nog een keer door: " + naam, "Once more through: " + naam),
        titelEn: "Once more through: " + (c.naamEn || c.naam),
        pitch: ct("Hier ben je op teruggevallen. Eerst de regel, dan " + meer.length + " vragen.",
                  "You slipped back here. The rule first, then " + meer.length + " questions."),
        pitchEn: "You slipped back here. The rule first, then " + meer.length + " questions.",
        stappen: [
          { kop: ct("De regel nog een keer", "The rule once more"),
            kopEn: "The rule once more", procedureel: true, kern: true, hulp: gcHulp(c.id),
            uitleg: "", uitlegEn: "",
            diep: c.uitleg, diepEn: c.uitlegEn,
            diepKop: GC_STAP_TXT.nl.d, diepKopEn: GC_STAP_TXT.en.d,
            vragen: [beg] },
          { kop: ct("En nu toepassen", "Now apply it"), kopEn: "Now apply it",
            hulp: gcHulp(c.id), uitleg: "", uitlegEn: "", vragen: meer }
        ]
      };
    }
  }
  return {""",
    )

    # ---------- EN EEN WEESKAART DIE NIET VAN DEZE RONDE IS ----------
    rep(
        """  corr:[], spiek:{a2:[18,23,30]}, wizard:null,""",
        """  /* v23.254: en kaart 31 erbij, "De constructie 'me cuesta' en lidwoorden". Die is in de nacht
     van 12 september met een nieuwe les meegekomen, met een toetsje van acht vragen en zonder
     grammaticaconcept dat hem uitlegt, en daar ging pw-lesgat op af. De poort stond dus al rood op
     main voordat deze ronde begon.

     Hij hoort hier: de kaart gaat letterlijk over me cuesta tegenover me gustan, en dat IS de
     gustar-familie. Maar dit is de DERDE keer in twee weken dat ik een weeskaart met de hand
     aanhecht (kaart 30 in v23.251, kaart 30 nog eens, nu 31), en drie keer dezelfde pleister is
     geen oplossing maar een gewoonte.

     De echte fout zit niet hier: een nieuwe les gaat via een pull request en brengt zijn
     spiekbriefkaart mee, en die kaart komt op main terecht zonder dat er ooit een concept bij
     gemaakt is. Zolang die weg niet keurt, komt kaart 32 er ook aan. */
  corr:[], spiek:{a2:[18,23,30,31]}, wizard:null,""",
    )

    kaal = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
    assert kaal.count("function kaartSplits(") == 1, "kaartSplits niet precies een keer"
    assert kaal.count("function kaartIsInfinitief(") == 1, "de uitgangstoets staat er niet"
    assert kaal.count("function kaartInfSet(") == 1, "de werkwoordentabel wordt niet bevraagd"
    assert kaal.count("wegStuk") == 3, "de haakjes en de stukken zitten niet in twee emmers"
    assert kaal.count("function kaartZinGat(") == 1, "kaartZinGat niet precies een keer"
    assert kaal.count("kaartVraag(") == 4, "kaartVraag staat niet op de drie vraagplekken"
    assert kaal.count("kaartRest(") == 4, "wat eraf ging komt niet op de achterkant terug"
    assert kaal.count("kaartZinHtml(") == 4, "de zin staat niet op beide kanten"
    assert 'dir:"nl-es"' in kaal, "de standaardrichting staat niet op produceren"
    assert 'dir:"es-nl"' not in kaal, "de oude standaardrichting staat er nog"
    assert kaal.count("S.dirGekozen = 1") == 1, "de keuze wordt niet vastgelegd"
    assert kaal.count("var SCHEMA = 5;") == 1, "het schemanummer loopt niet mee met migratie 5"
    assert kaal.count("{naar: 5,") == 1, "migratie 5 staat er niet"
    assert kaal.count("var leesZinnen") == 1, "leesZinnen bestaat niet"
    assert kaal.count("leesZinnen[i] = kort") == 1, "de zin wordt niet per woord bewaard"
    assert kaal.count("function gramRijBij(") == 1, "gramRijBij niet precies een keer"
    assert kaal.count("function gramSlordig(") == 1, "gramSlordig niet precies een keer"
    assert kaal.count("gramRijBij(st, !!goed)") == 1, "de rij wordt niet bijgewerkt"
    assert kaal.count("st.rijVoor") == 2, "de staat van dienst wordt niet op de dag bevroren"
    assert kaal.count("gramSlordig(st) ? Math.max(0, (st.boxVoor || 0) - 1) : 0") == 1, \
        "de misser leest de staat van dienst niet"
    assert kaal.count("GC_OPFRIS_LES_VRAGEN") == 3, "het lesje heeft geen eigen aantal vragen"
    assert kaal.count("lesje: true") == 1, "de opfrisser kent geen lesvariant"
    assert kaal.count("var vast = !!doosje") == 1, "nooit gedaan en teruggevallen zijn niet uit elkaar gehaald"
    assert kaal.count("spiek:{a2:[18,23,30,31]}") == 1, "de weeskaart hangt nergens aan"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de vraagkant is schoon, produceren is de standaard, en het doosje leest mee")
else:
    print("index.html: stond er al")

nieuw, doe_ver, reden = patchhulp.nummerKiezen(huidig, GEPLAND, DOE_APP)
if reden:
    print("LET OP: " + reden)
if doe_ver:
    patchhulp.zetVersie(APP, VER, huidig, nieuw)
    print("versie.txt: %s -> %s" % (huidig, nieuw))
else:
    print("versie.txt: stond al op " + huidig)
