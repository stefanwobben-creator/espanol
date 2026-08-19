#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.132: de ladder loopt door boven de maand.

## Wat er stuk was

De herhaalladder voor woorden was [0,1,3,7,14,30]. De bovenste doos was 30 dagen, en dat was
tegelijk de doos waar een woord voorgoed in bleef zitten. Elk woord dat je ooit bewijst komt dus
twaalf keer per jaar terug, voor altijd.

De rekensom: 313 basiswoorden geven zo'n tien herhalingen per dag aan dingen die je al kunt. Met
een niveauprofiel staan er 1907 woorden in, en dan zijn het er ruim zestig. Elke dag. Daar komt de
leesmotor nog overheen, die per gelezen tekst nieuwe woorden aandraagt.

Dat is de reden dat deze ronde vooraan staat en niet de leuke ronde is: zolang de bovenste doos 30
dagen is, groeit de dagelijkse last lineair mee met alles wat je erbij leert. Een app die je straft
voor doorleren is geen leerapp.

## Wat er nu staat

    [0, 1, 3, 7, 14, 30, 60, 120, 240]

De ladder tot en met de maand blijft precies zoals hij was, inclusief de Laatste stap op doos 4 en
de eis dat alleen een echte check je in doos 5 brengt (v20.0). Er komen alleen dozen boven: twee
maanden, vier maanden, acht maanden. 1907 woorden op de bovenste doos geven acht herhalingen per
dag in plaats van 63.

Grond: hoe langer het interval dat je nog net haalt, hoe langer het daarna blijft zitten (Bahrick
op jarenschaal; Kim & Webb 2022, 98 effectgroottes, vonden hetzelfde patroon op weken- en
maandenschaal). Een fout antwoord zet je nog steeds terug op doos 0, dus een interval dat te lang
blijkt corrigeert zichzelf binnen een beurt.

## "Bewezen vast" schuift NIET mee

Dat was de valkuil. `stevigDrempel()` gaf `INTERVALS.length - 1` terug, en die functie zit onder
de voortgangsbalk, de poort, de niveaupeiling en de Laatste stap. De ladder verlengen zou al die
betekenissen stilletjes verzetten: op de dag van de update zou de balk van Stefan naar nul gaan en
zou hij nog drie herhalingen per woord moeten doen voordat er weer iets "vast" is.

Daarom is de bovenste doos nu twee dingen die uit elkaar zijn getrokken:

  * `STEVIG_BOX` (5) is waar het bewijs compleet is. Onveranderd.
  * `srsTop()` (8) is waar de wachttijd ophoudt.

Alles boven stevig is wachttijd, geen extra bewijs. Zo blijft elk bestaand profiel exact staan waar
het stond, en gaat de ladder toch door.

## De stapgrootte beweegt mee met het woord

De ladder was voor elk woord even lang. "gracias" doorliep evenveel herhalingen als "atardecer".
Een woord dat je nog nooit fout had, minstens drie beurten heeft gehad en voorbij doos 2 is, schuift
nu twee dozen per goed antwoord op in plaats van een.

De eis is streng met opzet. `st.f` gaat nooit meer weg, dus een woord dat ergens onderuit ging staat
voorgoed weer op een doos per keer. En overslaan kan de Laatste stap niet passeren, want de
bovengrens van elke zelfbeoordeling is `zelfDrempel()` en de check zit daar precies op.

## Wat er niet in zit: het pensioen

Het plan was om een woord na een aantal keer op de bovenste doos met rust te laten. Doorgerekend is
dat overbodig: 1907 woorden op 240 dagen geven acht herhalingen per dag samen. Een pensioen haalt
daar hooguit acht vanaf, en het kost je de enige meting die zegt of het er nog zit. Geschrapt, met
opzet, en niet vergeten.

## Meebewegen dat wel moest

  * `krachtGewicht()` deelde door het hoogste interval. Met 240 als noemer zou een bewezen woord
    ineens voor 12,5 procent meetellen en het getal op Vandaag instorten. De noemer is nu de
    maanddoos, met een plafond op honderd procent.
  * De doosjesverdeling in `voortgangCijfers()` stond hardgecodeerd op zes vakjes. Woorden in de
    nieuwe dozen vielen daarmee buiten de telling: de balk zou dalen zodra je goed werd.
  * De tabel met herhaalintervallen kreeg drie labels erbij.
  * `vgLegendaUitlegHtml()` legt uit wat "bewezen vast" betekent en rekende dat uit de lengte van
    de ladder. Nu uit `stevigDrempel()`, zodat de uitleg blijft kloppen: vijf keer goed over
    minstens 25 dagen.

Bewaakt door test/suites/pw-ladder.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.132"

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


# ------------- 1. de ladder zelf

rep(
    '''var INTERVALS = [0,1,3,7,14,30];''',
    '''/* ================= DE LADDER (v23.132) =================
   Stond tot v23.132 op [0,1,3,7,14,30]. De bovenste doos was 30 dagen, en dat was tegelijk de doos
   waar een woord voorgoed in bleef zitten: elk woord dat je ooit bewijst kwam twaalf keer per jaar
   terug, voor altijd. Bij 313 woorden is dat een stuk of tien per dag; bij de 1907 die er met een
   niveauprofiel in zitten ruim zestig, elke dag, alleen aan dingen die je al kunt. De dagelijkse
   last groeide dus lineair mee met alles wat je erbij leerde.

   Er komen drie dozen boven: twee maanden, vier maanden, acht maanden. Dezelfde 1907 woorden geven
   dan acht herhalingen per dag. Grond: hoe langer het interval dat je nog nét haalt, hoe langer het
   daarna blijft zitten (Bahrick op jarenschaal, Kim & Webb 2022 op weken- en maandenschaal). Blijkt
   een interval te lang, dan zet het foute antwoord je terug op doos 0 en corrigeert het zichzelf
   binnen een beurt.

   Wat NIET verandert is de ladder tot en met de maand, inclusief de Laatste stap op doos 4. Er komt
   niets bij aan bewijslast en er gaat niets af. */
var INTERVALS = [0,1,3,7,14,30,60,120,240];
/* De doos waar het bewijs compleet is. Dit was hetzelfde getal als de bovenste doos, en daarom
   stond het er niet: stevigDrempel() rekende het uit de lengte van de ladder. Sinds de ladder
   doorloopt zijn het twee verschillende dingen, en dit is degene waar de voortgangsbalk, de poort,
   de niveaupeiling en de Laatste stap aan hangen. Verzet je hem, dan verzet je al die betekenissen
   tegelijk; daarom staat hij hier met naam en toenaam. Alles erboven is wachttijd, geen bewijs. */
var STEVIG_BOX = 5;''',
)

# ------------- 2. stevig, de top, en de stapgrootte

rep(
    '''// Stevig = de bovenste box. Omdat een fout antwoord de box terugzet op 0 (zie
// answerWord), betekent die box vijf keer achter elkaar goed over minstens 25
// dagen. Er is dus geen aparte "beheerst"-vlag nodig; de ladder is het bewijs.
function stevigDrempel(){ return INTERVALS.length - 1; }''',
    '''// Stevig = de doos waar het bewijs compleet is. Omdat een fout antwoord de box terugzet op 0 (zie
// answerWord), betekent die box vijf keer achter elkaar goed over minstens 25 dagen. Er is dus geen
// aparte "beheerst"-vlag nodig; de ladder is het bewijs.
function stevigDrempel(){ return STEVIG_BOX; }
// De bovenste doos van de ladder. Sinds v23.132 hoger dan stevig: daarboven zit alleen wachttijd.
function srsTop(){ return INTERVALS.length - 1; }
/* De hoogste doos die je op je eigen woord mag halen. De Laatste stap (wCheckNodig) zit op de doos
   eronder, dus zonder die check kom je hier niet voorbij. Dit stond overal als INTERVALS.length-2
   en dat was hetzelfde getal, tot de ladder doorliep. */
function zelfDrempel(){ return stevigDrempel() - 1; }
/* Hoeveel dozen een goed antwoord dit woord omhoog brengt.

   Waarom niet altijd een: de ladder was voor elk woord even lang. "gracias" doorliep evenveel
   herhalingen als "atardecer". Elke herhaling die een woord niet nodig had is een minuut die niet
   naar een woord ging dat het wel nodig had.

   De eis is streng met opzet: nog nooit fout, minstens drie beurten, en pas voorbij doos 2. st.f
   gaat nooit meer weg, dus wie ergens onderuit gaat staat voorgoed weer op een doos per keer. En
   overslaan kan de Laatste stap niet passeren: die zit op zelfDrempel(), en zelfDrempel() is de
   bovengrens van elke zelfbeoordeling. */
function srsStap(st){
  if(!st || typeof st !== "object") return 1;
  if((st.f || 0) > 0) return 1;
  if((st.n || 0) < 3) return 1;
  if((st.box || 0) < 2) return 1;
  return 2;
}
/* Een goed antwoord, met "mag" als hoogste doos die deze beurt mag opleveren. Eén plek, want tot nu
   toe stond dezelfde som op drie plaatsen met drie verschillende schrijfwijzen van hetzelfde
   plafond, en die zijn twee keer uit elkaar gelopen. */
function srsOmhoog(st, mag){
  st.box = Math.min(Math.max(0, st.box || 0) + srsStap(st), mag);
  return st.box;
}''',
)

# ------------- 3. answerWord: de zelfbeoordeling

rep(
    '''    st.box = Math.min(st.box+1, st.k ? INTERVALS.length-1 : INTERVALS.length-2);
    st.due = addDays(t, INTERVALS[st.box]);''',
    '''    // v23.132: de stap hoeft geen doos van een te zijn (zie srsStap), en het plafond staat nu in
    // zelfDrempel()/srsTop() in plaats van in twee losse sommen op de lengte van de ladder.
    srsOmhoog(st, st.k ? srsTop() : zelfDrempel());
    st.due = addDays(t, INTERVALS[st.box]);''',
)

# ------------- 4. Aventura

rep(
    '''      st.box = Math.min(st.box + 1, getypt ? INTERVALS.length - 1 : Math.max(0, INTERVALS.length - 2));
      st.due = addDays(t, INTERVALS[st.box]);''',
    '''      srsOmhoog(st, getypt ? srsTop() : zelfDrempel());   // v23.132, zie srsStap
      st.due = addDays(t, INTERVALS[st.box]);''',
)

# ------------- 5. het gewicht: de maanddoos is honderd, niet de bovenste doos

rep(
    '''function krachtGewicht(box){
  var top = INTERVALS[INTERVALS.length - 1] || 30;
  return (INTERVALS[box] || 0) / top;
}''',
    '''/* v23.132: de noemer is de maanddoos, niet de bovenste doos. Sinds de ladder doorloopt tot acht
   maanden zou "gedeeld door het hoogste interval" betekenen dat een bewezen woord ineens voor 12,5
   procent meetelt, en dan stort het getal op Vandaag in op de dag van de update terwijl er niets is
   gebeurd. De schaal blijft staan waar hij stond: de maanddoos is honderd, en alles daarboven ook.
   Wat erboven ligt is wachttijd, geen extra bewijs. */
function krachtGewicht(box){
  var top = INTERVALS[stevigDrempel()] || 30;
  return Math.min(1, (INTERVALS[box] || 0) / top);
}''',
)

# ------------- 6. de doosjesverdeling is even lang als de ladder

rep(
    '''  var dozen = [0, 0, 0, 0, 0, 0], dId, dSt, dB, dI, kr = 0;''',
    '''  // v23.132: even lang als de ladder, niet zes vakjes met de hand. Woorden in de nieuwe dozen
  // vielen anders stilletjes buiten deze telling, en dan daalt de balk zodra je goed wordt.
  var dozen = [], dId, dSt, dB, dI, kr = 0;
  for(dI = 0; dI < INTERVALS.length; dI++) dozen.push(0);''',
)

# ------------- 7. de tabel met herhaalintervallen

rep(
    '''  var lab = ct("nieuw/fout|1 dag|3 dagen|1 week|2 weken|1 maand",
               "new/wrong|1 day|3 days|1 week|2 weeks|1 month").split("|");''',
    '''  var lab = ct("nieuw/fout|1 dag|3 dagen|1 week|2 weken|1 maand|2 maanden|4 maanden|8 maanden",
               "new/wrong|1 day|3 days|1 week|2 weeks|1 month|2 months|4 months|8 months").split("|");''',
)

# ------------- 8. de uitleg van "bewezen vast" hangt aan stevig, niet aan de lengte

rep(
    '''function vgLegendaUitlegHtml(n){
  var top = INTERVALS.length - 1;''',
    '''function vgLegendaUitlegHtml(n){
  // v23.132: stevigDrempel(), niet de lengte van de ladder. De ladder loopt door tot acht maanden;
  // deze uitleg gaat over waar "bewezen vast" begint, en dat is niet meegeschoven.
  var top = stevigDrempel();''',
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
