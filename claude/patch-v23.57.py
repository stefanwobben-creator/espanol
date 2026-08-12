#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.57: na Controleer verdwijnt de knop die niets meer doet.

Stefan, telefoontest 12 aug: "ik vind die zin maken en dan controleer en knop volgende eronder nog
steeds verwarrend."

Hij zei dit ook op 11 augustus, en toen heb ik het verkeerde gerepareerd. In v23.51 heb ik "Volgende
zin" naar boven geschoven, want die viel onder de vouw. Dat klopte, maar het was niet waar de
verwarring zat. Vandaag heb ik een schermafdruk gemaakt in plaats van de code gelezen, en toen was
het meteen te zien. Dit staat er op 390 bij 844 ná Controleer:

    ZIN 1/3
    Ik begrijp het niet.
    [Tegels] [Moeilijk]
    ┌─────────────────────────────┐
    │ Tik hieronder een woord aan │   <- leeg, terwijl je net geantwoord hebt
    └─────────────────────────────┘
    [No] [entiendo] [bonita]          <- de tegels staan er nog
    [ CONTROLEER ]  [Wissen]          <- rode primaire knop, en hij doet niets meer
    ¡Perfecto! ✓ (+3 taco's)
    [ VOLGENDE ZIN → ]  [Meer uitleg] <- tweede rode primaire knop
    Waarom: ...

Twee primaire rode knoppen op één scherm, en de bovenste is dood. `checkSentence()` schrijft alleen
in `#sFeedback`; alles daarboven bleef staan zoals het was. Je hebt geantwoord en het scherm doet
alsof dat niet gebeurd is.

Nu klapt de invoer dicht zodra je gecontroleerd hebt. Wat overblijft is één regel met wat je hebt
ingevuld, en daaronder precies één primaire knop.

    ZIN 1/3
    Ik begrijp het niet.
    Jouw antwoord: No entiendo
    ¡Perfecto! ✓ (+3 taco's)
    [ VOLGENDE ZIN → ]  [Meer uitleg]
    Waarom: ...

De moeilijkheidsknoppen (Tegels/Moeilijk) gaan mee dicht: van modus wisselen terwijl je antwoord al
beoordeeld is slaat nergens op, en ze horen bij de invoer.

"Probeer opnieuw" blijft werken zoals het werkte: die roept `renderSentence(false)` aan en dan wordt
`#sBody` compleet opnieuw getekend, dus de tegels, de knoppen en de moduskeuze komen gewoon terug.

Nog steeds geen automatische doorloop, om dezelfde reden als in v23.51: dan pak je het moment af
waarop je de zin nog kunt horen. Het probleem was nooit dat je moest tikken.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.57"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function zinInvoerDicht" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_BODY = '''  var html = moeilijkModusHtml("sModus", modus, true);
  if(modus === "tegels"){
    if(!zTegel || zTegel.id !== s.id) zinTegelsZet(s);
    html += zinTegelsHtml() + "<input type='hidden' id='sInput' value=''>" + "<div id='sFeedback'></div>";
  } else {
    html += "<input type='text' id='sInput' autocomplete='off' autocapitalize='off' placeholder='"+ct("Typ de Spaanse zin...","Type the Spanish sentence...")+"'>"+
      accentToetsenHtml("sAccent")+
      "<div class='row'><button class='primary' id='btnCheck'>"+ct("Controleer","Check")+"</button></div>"+
      "<div id='sFeedback'></div>";
  }
  el.innerHTML = html;'''

A_FB = '''  fb.innerHTML = html;
  persist();
  if(gehaald){ checkLessonComplete(); }
  zinLuisterWire(s);'''

if DOE_APP:
    ontbreekt = [a for a in [A_BODY, A_FB] if a not in src]
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
    # ---------- 1. de invoer krijgt een eigen omhulsel ----------
    rep(A_BODY, '''  /* v23.57: alles wat bij het invullen hoort zit nu in één omhulsel (#sInvoer), zodat het na
     Controleer in zijn geheel dicht kan. Daarvoor bleef het gewoon staan: een leeg tegelvak, de
     tegels, en een rode Controleer-knop die niets meer deed, met daaronder een tweede rode knop.
     De moduskeuze gaat mee, want van Tegels naar Moeilijk wisselen terwijl je antwoord al
     beoordeeld is slaat nergens op. */
  var html = "<div id='sInvoer'>" + moeilijkModusHtml("sModus", modus, true);
  if(modus === "tegels"){
    if(!zTegel || zTegel.id !== s.id) zinTegelsZet(s);
    html += zinTegelsHtml() + "<input type='hidden' id='sInput' value=''>" + "</div><div id='sFeedback'></div>";
  } else {
    html += "<input type='text' id='sInput' autocomplete='off' autocapitalize='off' placeholder='"+ct("Typ de Spaanse zin...","Type the Spanish sentence...")+"'>"+
      accentToetsenHtml("sAccent")+
      "<div class='row'><button class='primary' id='btnCheck'>"+ct("Controleer","Check")+"</button></div>"+
      "</div><div id='sFeedback'></div>";
  }
  el.innerHTML = html;''')

    # ---------- 2. en klapt dicht zodra je gecontroleerd hebt ----------
    rep(A_FB, '''  fb.innerHTML = html;
  zinInvoerDicht(given);
  persist();
  if(gehaald){ checkLessonComplete(); }
  zinLuisterWire(s);''')

    # de functie zelf, vlak boven checkSentence
    rep('''function checkSentence(){
  var s = sIdx;''', '''/* v23.57: de invoer dicht, en in plaats daarvan één regel met wat je hebt ingevuld. Zonder dit
   bleef er na Controleer een dode primaire knop boven de levende staan, en dat is precies wat Stefan
   twee telefoontests achter elkaar "verwarrend" noemde.

   Bewust geen aparte opmaak of kleur: het is geen uitslag (die staat eronder), het is alleen een
   herinnering aan wat je deed. En bewust wél zichtbaar, want zonder die regel weet je bij een fout
   antwoord niet meer wat je precies had ingevuld terwijl het juiste antwoord er inmiddels staat.

   "Probeer opnieuw" hoeft hier niets terug te draaien: die roept renderSentence(false) aan en dan
   wordt #sBody in zijn geheel opnieuw getekend. */
function zinInvoerDicht(given){
  var inv = document.getElementById("sInvoer");
  if(!inv) return;
  var tekst = String(given || "").trim();
  inv.innerHTML = tekst
    ? "<p class='muted' style='margin:2px 0 10px'>" + ct("Jouw antwoord: ", "Your answer: ") +
      "<b style='color:var(--ink)'>" + tekst.replace(/[&<>]/g, function(c){
        return {"&":"&amp;", "<":"&lt;", ">":"&gt;"}[c]; }) + "</b></p>"
    : "";
}
function checkSentence(){
  var s = sIdx;''')

    import re
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
