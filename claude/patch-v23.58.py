#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.58: het eindscherm van je les wijst je niet meer naar de uitgang.

Stefan, telefoontest 12 aug: "als ik klaar ben loopt het nog steeds dood, geen follow up, niet van
hier staat Chispa of je kunt de spelletjes doen."

Dit was bevinding 4 van 11 augustus, en ik heb hem in v23.52 "opgelost". Nagemeten met een
schermafdruk in plaats van met de code, op 390 bij 844, en de voorstellen stáán er wel:

    LES AFGEROND 🎉
    ¡Muy bien! Chispa is blij met je.
    +3 🫒 tapas voor Chispa
    [🌮 Geef Chispa el taco]
    [ KLAAR VOOR VANDAAG ✓ ]  [Nog een les doen]     <- 348 px, groot en rood
    Tot morgen? ...
    ── EN NU? ──────────────────                      <- 521 px, andere kaart
    ✍️ Zinnen vertalen · hier win je het meeste
    🧩 Rompecabezas · of gewoon leuk
    [Even spelen →]                                   <- 802 px, achter de navigatiebalk

Het probleem is niet dat ze er niet zijn maar waar ze staan. **De opvallendste knop van het scherm
zegt "stop".** Hij is rood, hij is primair, hij staat bovenaan, en het antwoord op "en nu?" staat
eronder in een aparte kaart. Wie die knop tikt landt op de lessenlijst, en dáár is niets. De app
wijst je zelf naar de uitgang en Stefan liep er netjes doorheen.

## Waarom hij daar stond, en waarom dat nu anders mag

v20.5 heeft die knop bewust primair en bovenaan gezet. Dat was de zesde bevinding van Stefans
moeder: "ze wilde stoppen maar zag niet hoe." Dat is een echte bevinding en die gooien we niet weg.

Maar vindbaar en dominant zijn niet hetzelfde. Stoppen moet één tik zijn en duidelijk gelabeld;
het hoeft niet het luidste ding op het scherm te zijn. Nu:

    LES AFGEROND 🎉
    ¡Muy bien! Chispa is blij met je.
    +3 🫒 tapas voor Chispa
    [🌮 Geef Chispa el taco]
    [Klaar voor vandaag ✓]  [Nog een les doen]        <- rustig, maar meteen in beeld
    EN NU?
    ✍️ Zinnen vertalen · hier win je het meeste
    [ VIJF MINUTEN, DOEN ]                            <- de enige primaire knop
    🧩 Rompecabezas · of gewoon leuk
    [Even spelen →]
    Tot morgen? ...

Eerst geprobeerd met de voorstellen bóven de knoppenrij. Gemeten: "Klaar voor vandaag" belandde dan
op 797 pixels en "Nog een les doen" op 849, allebei achter de navigatiebalk. Dat is precies de
bevinding van v20.5 terugbrengen. Dus staat de rij waar hij stond, alleen niet meer als de luidste
knop van het scherm.

Alles in één kaart in plaats van twee, want het is één moment. Dat scheelt ook een kaartrand, een
kop en twee marges, en dat is precies wat er nodig was om "Klaar voor vandaag" boven de vouw te
houden.

## Wat er niet verandert

De volgorde van de voorstellen zelf: eerst wat het meeste oplevert, dan iets wat gewoon leuk is.
Dat is Stefans eigen formulering uit v20.5 en die klopt nog steeds. En de tapa-knop blijft geen
primaire knop: die gaat over wat je zojuist gedáán hebt, niet over wat je nu kunt doen.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.58"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.58" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_HTML = r'''function lesFlowVoorstellenHtml(vs){
  if(!vs.length) return "";
  return "<div class='card' style='margin-top:10px'><span class='kicker'>" +
    ct("En nu?", "What now?") + "</span>" +
    vs.map(function(v, i){
      return "<div style='margin:" + (i ? "14px" : "4px") + " 0 0'>" +
        "<p style='margin:0 0 2px; font-size:1.05rem'><b>" + v.icon + " " + v.kop + "</b>" +
        "<span class='muted' style='font-size:.8rem'> \u00b7 " +
          (i === 0 ? ct("hier win je het meeste", "this is where you gain most")
                   : ct("of gewoon leuk", "or just fun")) + "</span></p>" +
        "<p class='muted' style='margin:0 0 8px; font-size:.9rem'>" + v.waarom + "</p>" +
        "<button class='ghost' data-voorstel='" + i + "'>" + v.knop + " \u2192</button></div>";
    }).join("") + "</div>";
}'''

A_KNOPPEN = '''    "<div class='row'><button class='primary' id='btnLesFlowTerug'>"+ct("Klaar voor vandaag ✓","Done for today ✓")+"</button>"+
    "<button class='ghost' id='btnLesFlowNogEens'>"+ct("Nog een les doen","Do another session")+"</button></div>"+'''

A_SLOT = '''    "</div>"+
    lesFlowVoorstellenHtml(voorstellen)+'''

if DOE_APP:
    ontbreekt = [a for a in [A_HTML, A_KNOPPEN, A_SLOT] if a not in src]
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
    # ---------- 1. de voorstellen kunnen nu ook binnen een bestaande kaart ----------
    rep(A_HTML, r'''/* v23.58: dit maakte een eigen kaart, en die kwam dus ná de knoppenrij van het eindscherm te
   staan. Met "kaal" erbij kan hetzelfde blok binnen de vieringskaart, boven die knoppen. Eén kaart
   in plaats van twee scheelt een rand, een kop en twee marges, en dat is precies wat nodig was om
   "Klaar voor vandaag" boven de vouw te houden.

   Het eerste voorstel krijgt de primaire knop: dat is het antwoord op "en nu?". Tot v23.58 was de
   enige primaire knop op dit scherm "Klaar voor vandaag ✓", en dan wijst de app je zelf de deur. */
function lesFlowVoorstellenHtml(vs, kaal){
  if(!vs.length) return "";
  var binnen = "<span class='kicker'>" + ct("En nu?", "What now?") + "</span>" +
    vs.map(function(v, i){
      return "<div style='margin:" + (i ? "14px" : "4px") + " 0 0'>" +
        "<p style='margin:0 0 2px; font-size:1.05rem'><b>" + v.icon + " " + v.kop + "</b>" +
        "<span class='muted' style='font-size:.8rem'> \u00b7 " +
          (i === 0 ? ct("hier win je het meeste", "this is where you gain most")
                   : ct("of gewoon leuk", "or just fun")) + "</span></p>" +
        "<p class='muted' style='margin:0 0 8px; font-size:.9rem'>" + v.waarom + "</p>" +
        "<button class='" + (kaal && i === 0 ? "primary" : "ghost") + "' data-voorstel='" + i + "'>" +
        v.knop + " \u2192</button></div>";
    }).join("");
  return kaal ? "<div style='margin-top:14px'>" + binnen + "</div>"
              : "<div class='card' style='margin-top:10px'>" + binnen + "</div>";
}''')

    # ---------- 2. het eindscherm: eerst wat nu kan, dan pas de uitgang ----------
    rep(A_KNOPPEN, '''    /* v23.58: hier stond "Klaar voor vandaag ✓" als primaire knop bovenaan, met de voorstellen in
       een aparte kaart eronder. De opvallendste knop van het scherm zei dus "stop", en wie hem tikte
       landde op de lessenlijst waar niets staat. Stefan, 12 aug: "als ik klaar ben loopt het nog
       steeds dood, geen follow up."

       De bevinding van v20.5 (Stefans moeder: "ze wilde stoppen maar zag niet hoe") blijft staan,
       maar vindbaar en dominant zijn niet hetzelfde. De rij blijft dus staan waar hij stond en is
       alleen niet meer de luidste knop; de voorstellen eronder hebben nu de primaire knop.

       Met de voorstellen erbóven gemeten viel deze rij op 797 en 849 pixels, achter de
       navigatiebalk. Dan had ik de ene bevinding met de andere geruild. */
    "<div class='row' style='margin-top:12px'><button class='ghost' id='btnLesFlowTerug'>"+ct("Klaar voor vandaag ✓","Done for today ✓")+"</button>"+
    "<button class='ghost' id='btnLesFlowNogEens'>"+ct("Nog een les doen","Do another session")+"</button></div>"+
    lesFlowVoorstellenHtml(voorstellen, true)+''')

    rep(A_SLOT, '''    "</div>"+''')

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
