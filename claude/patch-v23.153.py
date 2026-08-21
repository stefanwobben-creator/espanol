#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.153: morgen zing je.

Stefan, 20 aug: "Wat is het beste en leukste?" (over: laten de blokken zichzelf inroosteren, of wil
je op Vandaag zien wat er de komende week aankomt)

## Waarom het geen van tweeën wordt

**Een weekoverzicht kan niet kloppen.** Alle drie de roosters lopen op `dagenTotaal()`, en die telt
jouw actieve dagen, niet de kalender. Sla je woensdag over, dan schuift alles een dag op. Een grid
met dinsdag-woensdag-donderdag erin moet dus of gokken wanneer je komt, of het rooster aan de
kalender vastspijkeren. Dat tweede is erger dan het niet tonen: dan mis je een liedje door een dag
vrij te nemen, en dat is precies het soort straf die in v19.64 is weggehaald ("een getal dat groeit
terwijl je niets doet").

En het is een dashboard, op het scherm waarvan in pw-verbouw vastligt dat het er geen mag zijn.

**Onzichtbaar laten is ook niet het beste.** Vooruitkijken is gratis motivatie. Weten dat je morgen
gaat zingen is een leukere reden om terug te komen dan weten dat je morgen woordjes gaat doen.

## Wat het wel wordt: één zin, over morgen

Er staat al een regel over morgen, precies op het moment dat die vraag opkomt: als je klaar bent voor
vandaag (v23.67, "klaar voor vandaag betekende tot nu toe geen enkel bericht over morgen, op het
scherm waar die vraag juist opkomt"). Daar hoort dit bij.

  "Morgen komen er 14 woordjes terug. En je zingt mee met Brujería."
  "Morgen komen er 9 woordjes terug. En je praat met Chispa."
  "Morgen komen er 11 woordjes terug. En je zingt mee met La Bachata, en je praat met Chispa."

Alleen als er morgen iets bijzonders is. Is het een gewone dag, dan staat er niets extra: een regel
die elke dag hetzelfde zegt is geen bericht meer.

## Wat dit technisch nodig had

`dayHash()` rekende altijd met vandaag, dus "welk lied is het morgen" was niet te beantwoorden zonder
te wachten. Nu rekent hij met een datum die je meegeeft, en `dayHash()` is de versie die vandaag
invult. Dat is dezelfde ingreep als bij `today()` destijds: één functie die het echt uitrekent, en
één die de gewone vraag stelt.

Bewaakt door test/suites/pw-morgen.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.153"

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


# ================= 1. de dagsleutel kan ook een andere dag zijn =================

rep(
    '''function dayHash(extra){
  var s = today() + "|" + (extra || "");
  var h = 0;
  for(var i=0;i<s.length;i++){ h = ((h<<5)-h+s.charCodeAt(i))|0; }
  return Math.abs(h);
}''',
    '''/* v23.153: hier stond alleen de versie met today() erin, en daardoor was "welk lied is het morgen"
   niet te beantwoorden zonder te wachten tot morgen. Nu rekent hij met de datum die je meegeeft, en
   is dayHash() de versie die vandaag invult. Dezelfde splitsing als bij today() zelf. */
function dagHashVoor(datum, extra){
  var s = (datum || today()) + "|" + (extra || "");
  var h = 0;
  for(var i=0;i<s.length;i++){ h = ((h<<5)-h+s.charCodeAt(i))|0; }
  return Math.abs(h);
}
function dayHash(extra){ return dagHashVoor(today(), extra); }''',
)

rep(
    '''function musVanDag(){
  var alles = musLijst();
  if(!alles.length) return null;
  var vers = alles.filter(function(sg){ return !musGedaan(sg); });
  var pot = vers.length ? vers : alles;
  return pot[dayHash("musica") % pot.length];
}''',
    '''function musVanDag(datum){
  var alles = musLijst();
  if(!alles.length) return null;
  var vers = alles.filter(function(sg){ return !musGedaan(sg); });
  var pot = vers.length ? vers : alles;
  return pot[dagHashVoor(datum || today(), "musica") % pot.length];   // v23.153: ook voor morgen
}''',
)

# ================= 2. wat er morgen bijzonder is =================

rep(
    '''function morgenZin(){''',
    '''/* ================= MORGEN (v23.153) =================

   Stefan vroeg of de roosters zichzelf moeten inroosteren of dat hij de week vooruit wil zien. Geen
   van beide: een weekoverzicht kán niet kloppen, want alle drie de roosters lopen op dagenTotaal()
   en die telt jouw actieve dagen. Sla je een dag over, dan schuift alles op. Een kalendergrid moet
   dus gokken of het rooster aan de kalender vastspijkeren, en dat tweede straft een dag vrijnemen
   af. Dat is wat in v19.64 is weggehaald.

   Dus: één zin, over morgen, op het scherm waar die vraag opkomt (v23.67). En alleen als er morgen
   echt iets bijzonders is: een regel die elke dag hetzelfde zegt is geen bericht meer. */
function morgenBijzonder(){
  var d = 0, uit = [];
  try { d = dagenTotaal() + 1; } catch(e){ return uit; }
  if(d <= 1) return uit;
  var morgenDatum = addDays(today(), 1);
  try {
    if((d % MUS_OM_DE) === 0){
      var sg = musVanDag(morgenDatum);
      if(sg) uit.push(ct("je zingt mee met "+sg.titel, "you sing along with "+sg.titel));
    }
  } catch(e){}
  try {
    /* praatKan() vraagt onder meer of je vandaag al gepraat hebt, en dat zegt niets over morgen.
       Wat wél over morgen gaat is de trede: sta je nog op één, dan is vrij praten ook morgen een
       muur. */
    if((d % 2) === 1 && vertTrede() >= PRAAT_TREDE_MIN){
      uit.push(ct("je praat met Chispa", "you talk with Chispa"));
    }
  } catch(e){}
  return uit;
}
function morgenBijzonderZin(){
  var r = morgenBijzonder();
  if(!r.length) return "";
  var lijst = r.length === 1 ? r[0] : r.slice(0, -1).join(", ") + ct(" en ", " and ") + r[r.length - 1];
  return " " + ct("En ", "And ") + lijst + ".";
}

function morgenZin(){''',
)

rep(
    '''  if(dg <= 3){
    z += " " + ct("Je krijgt geen herinnering, dus kom terug wanneer het jou uitkomt.",
                  "You will not get a reminder, so come back whenever it suits you.");
  }
  return z;''',
    '''  z += morgenBijzonderZin();   // v23.153
  if(dg <= 3){
    z += " " + ct("Je krijgt geen herinnering, dus kom terug wanneer het jou uitkomt.",
                  "You will not get a reminder, so come back whenever it suits you.");
  }
  return z;''',
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
