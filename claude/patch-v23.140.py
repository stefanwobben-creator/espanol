#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.140: lezen of luisteren staat in je les, niet erachter.

Stefan, 20 aug: "we zitten nog ver van het prototype af."

Dit is de grootste structurele stap eruit: de dagles krijgt zijn derde draad terug.

## Waarom dit de belangrijkste ronde is

Nation's vier draden (2007) zeggen dat een taalcursus zijn tijd ongeveer gelijk hoort te verdelen
over vier soorten werk: betekenisgerichte input (lezen, luisteren), betekenisgerichte output (zelf
iets maken), taalgerichte studie (woorden, grammatica) en vloeiendheid (sneller worden in wat je al
kent).

De dagles van Vamos was: woordjes, grammatica, toetsje, drie zinnen schrijven. Dat is ongeveer 90
procent taalgerichte studie en 10 procent output. Input stond erachter, als opt-in ná het punt
waarop je klaar was, en in Stefans logboek van 26 dagen staat "escucha" drie keer.

Nu is het blok 4 van 5, en staat het vóór het schrijven.

## Het risico, met naam

Dit is dezelfde ingreep die v20.5 heeft teruggedraaid. Stefan toen: "daarna krijg ik dacht dictado
en daarna lezen. ik merk dat ik afhaak als dit in de verplichte lijst is." Wat toen is weggehaald
was een blok van vijf tot tien zinnen dictado ná het eindpunt van de les. Dit is iets anders: een
kort stukje lezen of één gesprek luisteren, vóór het schrijven, dus midden in de les en niet erachter.

Maar het blijft de ingreep waar je eerder op afhaakte. Vandaar drie remmen:

  * **Het staat in het plan.** Je ziet op Vandaag dat het erin zit voordat je begint, met minuten
    erbij (v23.135). Geen verrassing halverwege.
  * **Ik kies, jij niet.** Even dagen lezen, oneven luisteren. Zelf laten kiezen betekent dat
    luisteren nooit gekozen wordt, en dan is de draad er alsnog niet.
  * **Is er niets, dan is er niets.** Geen boekhoofdstuk open of geen audio: het blok staat niet in
    het plan en de les is gewoon vier stappen. Het plan liegt niet (v23.135).

## Wat er technisch gebeurt

`lesFlowOpenProductie()` wist al hoe het een hoofdstuk of een luisterscene opent; dat was de
opt-in-machinerie van v20.5. Er komt een stap `"input"` bij die dezelfde machinerie gebruikt, en de
twee plekken die "klaar met het blok" melden (het boek en Escuchar) kennen die stap nu ook.

`dagPlan()` zet het blok tussen het toetsje en het schrijven, en `lesFlowStapNaam()` noemt het bij
naam, zodat de banner "stap 4 van 5 · Lezen" zegt.

Bewaakt door test/suites/pw-inputblok.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.140"

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


# ------------- 1. welke input er vandaag is, en of er iets is

rep(
    '''function lesFlowGramLijst(){''',
    '''/* ================= HET INPUTBLOK (v23.140) =================

   De derde draad van Nation: iets begrijpen, niet iets oefenen. Even dagen lezen, oneven luisteren.

   Waarom ik kies en jij niet: laat je de gebruiker kiezen, dan wordt luisteren nooit gekozen, en dan
   is de draad er alsnog niet. Het staat wel in het plan op Vandaag voordat je begint, dus het is
   geen verrassing halverwege.

   Is er niets, dan is er niets: geen open hoofdstuk of geen audio betekent dat dit blok niet in het
   plan staat en de les gewoon vier stappen telt. Een plan dat iets belooft wat er niet is, is
   erger dan een korter plan (v23.135). */
function lesFlowInputKeuze(){
  var lezen = null, audi = false;
  try { lezen = lesFlowBoekHoofdstuk(); } catch(e){ lezen = null; }
  /* audOpen(sc) vraagt of één scene open is; wat we hier nodig hebben is of er überhaupt iets
     open staat, en dat is audLijst(). Eerst per ongeluk audOpen() zonder scene aangeroepen: die
     valt dan over sc.id, wordt opgevangen door de catch, en luisteren zou nooit gekozen worden. */
  try { audi = typeof audLijst === "function" && audLijst().length > 0; } catch(e){ audi = false; }
  if(!lezen && !audi) return null;
  if(!lezen) return "luisteren";
  if(!audi) return "lezen";
  return (dayHash("input") % 2) === 0 ? "lezen" : "luisteren";
}

function lesFlowGramLijst(){''',
)

# ------------- 2. het blok staat in het plan

rep(
    '''  var kanSchrijven = false;
  try { kanSchrijven = !!allowedSentIds().length; } catch(e){ kanSchrijven = false; }''',
    '''  /* v23.140: de derde draad. Tussen het toetsje en het schrijven, want het is input en input hoort
     vóór wat je er zelf mee doet. De tijd is een kwart van je dag, hetzelfde budget dat
     vaardigheidTijd() al aan een vaardigheidsblok gaf. */
  var inputV = null;
  try { inputV = lesFlowInputKeuze(); } catch(e){ inputV = null; }
  if(inputV){
    blokken.push({stap:"input",
      naam: inputV === "lezen" ? ct("Lezen","Reading") : ct("Luisteren","Listening"),
      wat: inputV === "lezen" ? ct("een stukje uit je boek","a piece from your book")
                              : ct("een gesprek","one conversation"),
      sec: doelMinuten() * 60 * 0.25, vaardigheid: inputV});
  }
  var kanSchrijven = false;
  try { kanSchrijven = !!allowedSentIds().length; } catch(e){ kanSchrijven = false; }''',
)

# ------------- 3. de flow doet het blok ook echt

rep(
    '''    if(allowedSentIds().length){
      lesFlow.stap = "produceren";
      lesFlow.vaardigheid = "schrijven";''',
    '''    /* v23.140: eerst input, dan pas zelf iets maken. lesFlowOpenProductie() weet sinds v20.5 al hoe
       het een hoofdstuk of een luisterscene opent; die machinerie wordt hier hergebruikt. */
    var inputV = null;
    try { inputV = lesFlowInputKeuze(); } catch(e){ inputV = null; }
    if(inputV){
      lesFlow.stap = "input";
      lesFlow.vaardigheid = inputV;
      lesFlow.vaardigheidRij = [];
      lesFlowOpenProductie();
      return;
    }
    if(allowedSentIds().length){
      lesFlow.stap = "produceren";
      lesFlow.vaardigheid = "schrijven";''',
)

rep(
    '''  if(lesFlow.stap === "produceren"){
    // deze vaardigheid is vandaag aan bod geweest, ook als je hem oversloeg: anders krijg je morgen
    // precies hetzelfde blok weer voorgeschoteld
    if(lesFlow.vaardigheid) S.lesFlowSpel[lesFlow.vaardigheid] = today();''',
    '''  /* v23.140: klaar met lezen of luisteren, door naar het schrijven. Dezelfde afhandeling als
     hieronder, maar met een vaste volgende stap in plaats van een rij vaardigheden. */
  if(lesFlow.stap === "input"){
    if(lesFlow.vaardigheid) S.lesFlowSpel[lesFlow.vaardigheid] = today();
    if(allowedSentIds().length){
      lesFlow.stap = "produceren";
      lesFlow.vaardigheid = "schrijven";
      lesFlow.vaardigheidRij = [];
      lesFlow.gekozenSpel = "vertalen";
      lesFlow.vertalenTeGaan = lesFlow.vertalenTotaal = SCHRIJF_PER_LES;
      show("vertalen");
      return;
    }
    lesFlowKlaar();
    return;
  }
  if(lesFlow.stap === "produceren"){
    // deze vaardigheid is vandaag aan bod geweest, ook als je hem oversloeg: anders krijg je morgen
    // precies hetzelfde blok weer voorgeschoteld
    if(lesFlow.vaardigheid) S.lesFlowSpel[lesFlow.vaardigheid] = today();''',
)

# ------------- 4. de twee plekken die "klaar met het blok" melden

rep(
    '''  if(wasLezen && lesFlow && lesFlow.stap === "produceren" && lesFlow.gekozenSpel === "boek"){ lesFlowVolgende(); return; }''',
    '''  // v23.140: "input" erbij. Lezen is sinds deze versie een eigen stap in de les en niet meer alleen
  // het opt-in-blok van v20.5; zonder deze regel bleef je na het hoofdstuk in het boekenmenu staan.
  if(wasLezen && lesFlow && (lesFlow.stap === "produceren" || lesFlow.stap === "input") && lesFlow.gekozenSpel === "boek"){ lesFlowVolgende(); return; }''',
)

# ------------- 5. de banner noemt het bij naam

rep(
    '''  if(f.stap === "produceren"){
    var v = f.vaardigheid;''',
    '''  if(f.stap === "input" || f.stap === "produceren"){
    var v = f.vaardigheid;''',
)

# ------------- 6. de stappenlijst kent de volgorde

rep(
    '''var LESFLOW_VOLGORDE = ["woorden", "grammatica", "toetsjes", "produceren"];''',
    '''var LESFLOW_VOLGORDE = ["woorden", "grammatica", "toetsjes", "input", "produceren"];''',
)

# ------------- 7. hervatten kent de nieuwe stap

rep(
    '''    vaardigheid: lesFlow.vaardigheid || null,''',
    '''    vaardigheid: lesFlow.vaardigheid || null,   // v23.140: draagt ook de keuze van het inputblok''',
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
