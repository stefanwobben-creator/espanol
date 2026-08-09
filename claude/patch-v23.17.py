#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.17: de app gaat meten hoe lang je er echt over doet.

Stefan zet dertig minuten per dag en is in vier minuten klaar. Die dertig minuten gaan bovendien niet
alleen over woordjes maar over de hele sessie: woorden, een grammaticapunt, een toetsje en een
oefenronde. De app wist daar tot nu toe niets van. Hij stuurt de portie met dagPortieNieuw(), en dat
is doelMinuten() maal 0,5, dus dertig minuten worden vijftien nieuwe woorden. Dat impliceert twee
minuten per woord. Er is nergens een seconde gemeten om dat te controleren.

En de startkaart beloofde "ongeveer 5 min", hardgecodeerd, ongeacht wat je instelt en ongeacht hoe
groot je portie is. Dat is geen schatting maar een tekst.

Wat er nu gebeurt is alleen meten. Actieve tijd per dag, opgeteld uit de gaten tussen twee antwoorden
en alleen als dat gat korter is dan twee minuten, zodat een tabblad dat een uur openstaat niet als
een uur oefenen telt. Die seconden komen naast pogingen en fouten in S.dagStats.

Wat er bewust nog NIET gebeurt is de portie op tijd sturen. Dat kan pas als er gemeten is, en dat is
precies de volgorde die dit project overal aanhoudt: eerst weten, dan beweren. Op de startkaart staat
dus ook geen tijd meer zolang er niets gemeten is. Een geleend getal weglaten is beter dan het
opschrijven.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function trackTijd()" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. meten
rep(
    """function trackPoging(fout){
  var d = today();
  S.dagStats = S.dagStats || {};
  S.dagStats[d] = S.dagStats[d] || {pogingen:0, fouten:0};
  S.dagStats[d].pogingen++;
  if(fout) S.dagStats[d].fouten++;
}""",
    """function trackPoging(fout){
  var d = today();
  S.dagStats = S.dagStats || {};
  S.dagStats[d] = S.dagStats[d] || {pogingen:0, fouten:0};
  S.dagStats[d].pogingen++;
  if(fout) S.dagStats[d].fouten++;
  trackTijd();
}
/* v23.17. Hoe lang doe je er echt over? De app stuurde je dagportie op doelMinuten() zonder ooit een
   seconde te meten: dertig minuten werden vijftien nieuwe woorden, wat neerkomt op twee minuten per
   woord, en niemand wist of dat klopte. Stefan was in vier minuten klaar.

   Dit is de goedkoopste eerlijke meting die bestaat. Geen start- en stopknop (die vergeet je, en dan
   meet je alsnog niets), maar de gaten tussen twee antwoorden bij elkaar opgeteld. Is het gat langer
   dan twee minuten, dan telt het niet mee: dan stond het tabblad open en zat jij ergens anders. Dat
   onderschat je tijd iets, want de laatste kaart voor een pauze telt niet af, en dat is de goede
   kant om je in te vergissen: liever te weinig beloven dan te veel.

   trackPoging() wordt bij elk nagekeken antwoord aangeroepen, dus dit hangt automatisch onder alles
   wat je doet: woorden, toetsjes, dictado, de spellen en de corrector. Er is niets aan te onderhouden. */
var TIJD_GAT = 120000;                      // langer weg dan dit telt niet als oefentijd
var tijdLaatst = 0;
function trackTijd(){
  var nu = Date.now(), d = today();
  S.dagStats[d] = S.dagStats[d] || {pogingen:0, fouten:0};
  if(tijdLaatst && nu - tijdLaatst < TIJD_GAT){
    S.dagStats[d].sec = (S.dagStats[d].sec || 0) + Math.round((nu - tijdLaatst) / 1000);
  }
  tijdLaatst = nu;
}
/* Wat je de laatste zeven dagen echt hebt gedaan: seconden en pogingen. Twee getallen die alleen
   samen iets zeggen, want tijd zonder pogingen is een tabblad dat openstond. */
function tijdVenster(dagen){
  var t = today(), sec = 0, pog = 0, dagenMet = 0, i, e;
  for(i = 0; i < dagen; i++){
    e = (S.dagStats || {})[addDays(t, -i)];
    if(!e) continue;
    if(e.sec){ sec += e.sec; dagenMet++; }
    pog += e.pogingen || 0;
  }
  return {sec:sec, pog:pog, dagen:dagenMet,
          perPoging: pog >= 30 && sec > 0 ? sec / pog : null,
          perDag: dagenMet ? Math.round(sec / dagenMet / 60) : null};
}""")

# ---------------------------------------------------------------- 2. de startkaart schat met jouw seconden
rep(
    """    d.push("1 " + ct("oefenronde","practice round"));
    return d.join(" · ") + " · ±5 min";""",
    """    d.push("1 " + ct("oefenronde","practice round"));
    /* v23.17: hier stond "±5 min", hardgecodeerd. Dat was geen schatting maar een tekst: hij stond
       er ook als je portie drie keer zo groot was. Nu wordt hij gerekend uit jouw eigen seconden per
       antwoord, en zolang die er niet zijn staat er niets. De onderdelen tellen mee zoals ze op de
       kaart staan: de woordjes, de vragen van het toetsje, en een handvol beurten voor het
       grammaticapunt en de oefenronde. */
    var tv = tijdVenster(7);
    if(tv.perPoging){
      var beurten = portie.totaal + toetsvragenPerDag() + 8;
      var min = Math.max(1, Math.round(beurten * tv.perPoging / 60));
      d.push(ct("ongeveer "+min+" min","about "+min+" min"));
    }
    return d.join(" · ");""")

# ---------------------------------------------------------------- 3. op je profiel, met wat het betekent
rep(
    """  r += cijferRij(c.geoefend, ct("woorden ooit geoefend","words practised ever"),""",
    """  var tv = tijdVenster(7);
  if(tv.perDag !== null && tv.dagen >= 3){
    var doelMin = doelMinuten();
    var oordeel;
    if(tv.perDag >= doelMin * 0.8){
      oordeel = ct("Dat komt overeen met de "+doelMin+" minuten die je hebt ingesteld.",
                   "That matches the "+doelMin+" minutes you set.");
    } else {
      oordeel = ct("Je hebt "+doelMin+" minuten ingesteld, dus de app vraagt je minder dan je zelf van "+
                   "plan was. Zet je instelling lager als dit genoeg voelt, of hoger als je meer wilt: "+
                   "je dagportie hangt eraan.",
                   "You set "+doelMin+" minutes, so the app is asking less of you than you planned. "+
                   "Set it lower if this feels like enough, or higher if you want more: your daily "+
                   "portion depends on it.");
    }
    r += cijferRij(tv.perDag, ct("minuten per dag, gemeten","minutes a day, measured"),
      ct("Opgeteld uit de tijd tussen je antwoorden, over "+tv.dagen+" gemeten "+
         (tv.dagen === 1 ? "dag" : "dagen")+". Sta je langer dan twee minuten stil, dan telt dat niet mee. "+
         oordeel,
         "Added up from the time between your answers, across "+tv.dagen+" measured "+
         (tv.dagen === 1 ? "day" : "days")+". A pause longer than two minutes does not count. " + oordeel));
  }
  r += cijferRij(c.geoefend, ct("woorden ooit geoefend","words practised ever"),""")

# ---------------------------------------------------------------- 4. versie
rep('var APP_VERSIE = "v23.16";', 'var APP_VERSIE = "v23.17";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.17 toegepast op", PAD)
