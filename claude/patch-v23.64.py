#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.64: het dagscherm gaat over vandaag, de cijfers staan bij de cijfers.

Stefan, 12 aug, over het Vandaag-scherm: "je ziet nu heel veel info in een keer in je scherm. Geen
idee wat de app allemaal te bieden heeft, wat dit allemaal betekent. Je hebt overwhelm. Deze ux is
echt kapot." En over dezelfde kaart, apart: "leuk statistieken maar hoe moet ik die lezen wat zeggen
die?"

Gemeten met drieschermen.js, drie toestanden van hetzelfde scherm:

    1. nog niets gedaan       789 px  (0,9 scherm)    2 getallen   5 knoppen
    2. halverwege             914 px  (1,1 scherm)    2 getallen   7 knoppen
    3. klaar voor vandaag    1362 px  (1,6 scherm)   11 getallen   8 knoppen

Van die elf getallen in toestand 3 staan er negen in één kaart: de kaart met de kop "Waar je staat".
Grote teller, een balk in drie tinten, een legenda van vier woorden (bewezen vast / onderweg /
geschat al gekend / nog niet gezien), de noemer, en daaronder twee tegels met kracht en fout-
percentage. Dat is niet fout gerekend. Het is een meting van de binnenkant van de app, en de vier
woorden van die legenda zijn namen van SRS-doosjes. "Vast" is doos 5, en die kost 25 dagen, dus dat
getal meet vooral hoe lang je bezig bent. Dat weet Stefan omdat hij het zelf zo bedacht heeft. Een
vreemde op dag 3 leest daar niets in.

## Wat er weggaat, en waar het naartoe gaat

Niets gaat weg. De hele kaart staat al op Voortgang (`vgVastKaart`, mét legenda) en de twee tegels
staan een stuk lager op datzelfde scherm uitgesplitst, elk met een alinea uitleg eronder
(`cijferLijstHtml`). Op Vandaag blijft één zin over die dezelfde balk in woorden zegt:

    Waar je staat
    Je bent onderweg in A1 en houdt 34 woorden actief bij.
    [ Alle cijfers → ]

De vijf standen komen uit precies dezelfde som als de balk (actief plus geschat, gedeeld door de
noemer): net begonnen, onderweg, over de helft, bijna rond, zo goed als rond.

## Waarom de zin blijft en de kaart niet

v19.99 zette die balk hier neer om een reden die nog steeds klopt: Stefans kritiek op Duolingo was
"ik doe de habit maar ik leer niks", en een dagscherm met alleen veertien staafjes is precies dat.
Het bewijs dat er geleerd wordt hoort op je eerste scherm. Alleen: bewijs hoeft geen dashboard te
zijn. Eén zin die zegt waar je staat doet hetzelfde werk, en hij is leesbaar zonder dat je weet wat
een doosje is.

## En het vinkje

    ✓ herhalingen bij

Stefan: "herhaling bij? waarom staat dat hier is dat ook een extra knop? verwarrend." Het was geen
knop maar een `<span class='chip ok'>`; er gebeurde niets als je erop tikte. Hij verscheen als je
geen herhalingen open had staan én ooit iets geoefend had. Drie dingen mis: "bij" is jargon, hij
staat in dezelfde band als de rode knop eronder dus hij leest als knop, en er valt niets mee te
doen. Weg. Wat hij bedoelde (je hebt geen achterstand) is de afwezigheid van een probleem, en de
app meldt sinds v19.64 met opzet geen saldo's meer.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.64"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function dagBasisZinHtml" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_CHIP = '''  if(rel.chipHerhaal) chipsHtml += chip(true, ct("herhalingen bij","reviews done"));
'''

A_REL = '''    chipHerhaal: open === 0 && tel.geoefend > 0,
'''

A_KAART = '''  var rel = dagRelevantie();
  var basis = rel.basis ? dagBasisRegelHtml() : "";
  // v23.14: de twee kerncijfers horen bij de balk en niet in een eigen kaart. Ze kunnen er ook
  // staan als de balk zwijgt (wie geoefend heeft zonder dat er al iets onderweg is), dus ze zijn
  // een eigen reden om deze kaart te tonen.
  var kern = dagKerncijfersHtml();
  if(!basis && !kern && !rel.lijn) return "";
  return "<div class='card' id='lijnKaart'>"+basis+kern+'''

A_ZIN_ANKER = '''/* ================= DE TWEE KERNCIJFERS OP VANDAAG (v23.14) ================='''

A_PROFIEL = '''    ct("Het getal dat op Vandaag staat. Een woord in het weekdoosje telt voor "+'''

if DOE_APP:
    ontbreekt = [a for a in [A_CHIP, A_REL, A_KAART, A_ZIN_ANKER, A_PROFIEL] if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
              "\n\nEerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. het vinkje dat geen knop was ----------
    rep(A_CHIP, '''  /* v23.64: hier stond een chipje "\\u2713 herhalingen bij". Stefan: "herhaling bij? waarom staat
     dat hier is dat ook een extra knop? verwarrend." Het was een span en geen knop, maar het stond
     in dezelfde band als de rode knop eronder, dus het las als knop. En er viel niets mee te doen:
     het meldde de afwezigheid van een probleem, in jargon ("bij" van bijhouden). Weg. */
''')
    rep(A_REL, '''    /* v23.64: chipHerhaal is weg. Zie de toelichting bij het chipsblok in dagRitmeHtml(). */
''')

    # ---------- 2. de zin in plaats van de kaart ----------
    rep(A_KAART, '''  var rel = dagRelevantie();
  /* v23.64. Hier stond dagBasisRegelHtml(): de grote teller, de balk in drie tinten, de legenda van
     vier woorden en de noemer. Plus dagKerncijfersHtml() met kracht en foutpercentage. Samen negen
     van de elf getallen die op dit scherm stonden.

     Stefan: "leuk statistieken maar hoe moet ik die lezen wat zeggen die?" Dat is de juiste vraag,
     en het antwoord stond nergens op dit scherm. De vier woorden van de legenda zijn namen van
     SRS-doosjes; "vast" is doos 5 en die kost 25 dagen.

     Er gaat niets verloren. De hele kaart staat op Voortgang (vgVastKaart, mét legenda) en de twee
     tegels staan lager op datzelfde scherm uitgesplitst, elk met een alinea eronder. De knop
     "Alle cijfers" hieronder brengt je er in één tik heen.

     Wat blijft is de reden waarom v19.99 die balk hier neerzette: Stefans kritiek op Duolingo was
     "ik doe de habit maar ik leer niks", en een dagscherm met alleen staafjes is precies dat. Maar
     bewijs hoeft geen dashboard te zijn. Eén zin doet hetzelfde werk. */
  var basis = rel.basis ? dagBasisZinHtml() : "";
  if(!basis && !rel.lijn) return "";
  return "<div class='card' id='lijnKaart'>"+basis+''')

    rep(A_ZIN_ANKER, '''/* ================= WAAR JE STAAT, IN ÉÉN ZIN (v23.64) =================
   Dezelfde som als de balk: wat je actief bijhoudt plus wat de peiling erbij schat, gedeeld door de
   noemer van je niveau. Alleen niet als percentage en niet als balk, maar als een van vijf standen
   in woorden. Een percentage zegt niet wélk deel het meet (dat was de fout van vóór v23.0); een
   stand in woorden hoeft dat ook niet te zeggen.

   De grenzen zijn met opzet grof. Ze mogen niet zo fijn zijn dat de zin van dag tot dag verspringt,
   want dan is hij weer een getal. */
function dagBasisStand(pct){
  if(pct < 8) return 0;
  if(pct < 40) return 1;
  if(pct < 70) return 2;
  if(pct < 95) return 3;
  return 4;
}
function dagBasisZinHtml(){
  var c = voortgangCijfers();
  var sm = c.samen;
  var n = sm.noem || 390;
  var w = sm.actief;
  var aanbod = null;
  try { aanbod = peilAanbod(); } catch(e){ aanbod = null; }
  if(w <= 0 && !c.schat && !aanbod) return "";
  var nivTxt = samenNivTekst(sm.nivs) || c.niv;
  var pct = n ? Math.round(100 * Math.min(n, w + sm.geschat) / n) : 0;
  var stand = dagBasisStand(pct);
  var zinNl = [
    "Je bent net begonnen aan " + nivTxt + ".",
    "Je bent onderweg in " + nivTxt + ".",
    "Je bent over de helft van " + nivTxt + ".",
    nivTxt + " is bijna rond.",
    nivTxt + " is zo goed als rond."
  ][stand];
  var zinEn = [
    "You have just started on " + nivTxt + ".",
    "You are on your way in " + nivTxt + ".",
    "You are past the halfway point of " + nivTxt + ".",
    nivTxt + " is nearly complete.",
    nivTxt + " is as good as complete."
  ][stand];
  /* Eén getal erbij, en het is het enige getal op dit scherm dat over jouw werk gaat in plaats van
     over de administratie: hoeveel woorden je op dit moment actief bijhoudt. Staat er nul, dan
     staat er niets: nul is geen bericht (zie dagRelevantie).

     En als de peiling het zware werk doet, staat dat erbij. Anders leest "je bent over de helft van
     A1, je houdt er 7 actief bij" als een tegenspraak, en dan gaat de lezer aan allebei de helften
     twijfelen. Op de balk was dat opgelost met een aparte tint en het woord "geschat"; in een zin
     moet het met woorden. */
  if(w > 0 && sm.geschat > w){
    zinNl = zinNl.replace(/\\.$/, "") + ", volgens je peiling. Zelf houd je er " + w + " actief bij.";
    zinEn = zinEn.replace(/\\.$/, "") + ", according to your check. You are actively keeping up " + w + " yourself.";
  } else if(w > 0){
    zinNl += " Je houdt er " + w + " actief bij.";
    zinEn += " You are actively keeping up " + w + " of them.";
  }
  /* Geen niveau in de kop: dat staat in de zin eronder, en twee weergaven van hetzelfde getal is
     precies de fout waar dit scherm sinds v23.0 mee bezig is. */
  return "<span class='kicker'>"+ct("Waar je staat","Where you are")+"</span>"+
    "<p style='margin:6px 0 0'>"+ct(zinNl, zinEn)+"</p>"+
    (aanbod ? "<div style='margin-top:10px'>"+dagPeilKnopHtml(aanbod)+"</div>" : "");
}
/* ================= DE TWEE KERNCIJFERS (v23.14, sinds v23.64 alleen nog op je profiel) =========''')

    # ---------- 3. het profiel verwees naar een plek waar het getal niet meer staat ----------
    rep(A_PROFIEL, '''    ct("Hoe stevig je woorden erin zitten. Een woord in het weekdoosje telt voor "+''')
    rep('''       "The number shown on Today. A word in the one week box counts for "+''',
        '''       "How solidly your words are lodged. A word in the one week box counts for "+''')

    # ---------- 4. en nog een verwijzing naar een plek waar het getal niet meer staat ----------
    rep('''    ct("Dit is het getal dat op Vandaag boven de balk staat: bewezen vast plus onderweg, van de "+''',
        '''    ct("Het getal boven de balk hierboven: bewezen vast plus onderweg, van de "+''')
    rep('''       "This is the number above the bar on Today: proven solid plus on the way, out of the "+''',
        '''       "The number above the bar above: proven solid plus on the way, out of the "+''')

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
