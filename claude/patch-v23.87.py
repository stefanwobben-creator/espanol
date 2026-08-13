#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.87: drie zinnen die een vreemde niet kon begrijpen.

De onboarding doorlopen op een vers profiel, telefoonformaat, elke stap afgebeeld. Nul fouten, en
drie plekken waar een nieuwe bezoeker vastloopt op tekst.

## 1. "ververs dan de pagina hard"

Onderaan het aanmeldformulier stond: "App-versie: v23.86 · zie je hier een lager nummer dan verwacht,
ververs dan de pagina hard." Ontwikkelaarstaal op het scherm van iemand die nog niet eens een naam
heeft ingevuld. "Hard verversen" kent niemand buiten de bouw, en de zin zaait twijfel op precies het
moment dat je vertrouwen wil wekken: er kán dus iets misgaan, nog voor er iets gebeurd is.

Het versienummer blijft staan, want dat is nuttig als iemand iets meldt. De rest gaat weg. Dat is
dezelfde tekst als bij de andere plek waar het nummer staat (`av`), dus nu zijn ze ook gelijk.

## 2. "Daarna mag je Chispa el pulpo a la gallega geven"

Dit stond op het allereerste scherm ná aanmelden, boven "Start je les". Drie onbekenden in één zin:
wie Chispa is, wat el pulpo a la gallega is, en waarom dat een beloning zou zijn. Chispa stelt zich
pas één scherm later voor, in de les zelf. De beloning kwam dus vóór het personage.

Op dag 1 staat er nu wie ze is en wat het gerecht is. Daarna blijft het kort, want dan weet je het.

## 3. "6/30 taco's" zonder dat ergens staat wat een taco is

De balk staat er vanaf de eerste seconde. De uitleg zit op slide 2 van de rondleiding, en dan nog
alleen wat een taco dóét ("van taco's groei ík"), niet wat hij is. Wie op "Overslaan" tikt, hoort het
nooit.

Eén regel op dag 1, op het dagscherm zelf, en daarna weg. Met het stukje dat er het meest toe doet:
dat een fout antwoord er ook een oplevert. Dat staat al in de rondleiding, maar juist die zin wil je
zien op het moment dat je je eerste fout maakt en niet ervoor.

Toon: kort en vriendelijk, zoals Stefan het vroeg.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.87"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.87" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_VERSIE = '''  if(avp) avp.textContent = "App-versie: " + APP_VERSIE + " \u00b7 zie je hier een lager nummer dan verwacht, ververs dan de pagina hard";'''

A_TAPA = '''      "<p class='muted' style='margin:2px 0 0'>"+ct("Daarna mag je Chispa "+tapaHoy.e+" <b>"+tapaHoy.es+"</b> geven.",
                                                    "Then you get to give Chispa "+tapaHoy.e+" <b>"+tapaHoy.es+"</b>.")+"</p>")+'''

if DOE_APP:
    ontbreekt = [n for n, a in (("de app-versieregel", A_VERSIE), ("de tapa-regel op het dagscherm", A_TAPA))
                 if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.86. Eerst bijtrekken:\n\n    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # 1. het versienummer zonder de instructie erachter
    rep(A_VERSIE, '''  /* v23.87: hier stond "\u00b7 zie je hier een lager nummer dan verwacht, ververs dan de pagina hard".
     Dat is ontwikkelaarstaal op het scherm van iemand die nog niet eens een naam heeft ingevuld, en
     het zaait twijfel voordat er iets gebeurd is. Het nummer blijft, want daar heb je iets aan als
     iemand een probleem meldt; de instructie gaat weg. */
  if(avp) avp.textContent = "App-versie: " + APP_VERSIE;''')

    # 2 en 3. dag 1 krijgt twee zinnen erbij, daarna blijft het kort
    rep(A_TAPA, '''      /* v23.87: op dag 1 stond hier "Daarna mag je Chispa \U0001f419 el pulpo a la gallega geven", en dat
         waren drie onbekenden in \u00e9\u00e9n zin: wie Chispa is (ze stelt zich pas in de les voor), wat het
         gerecht is (onvertaald), en waarom het een beloning zou zijn.

         Dus: op dag 1 staat erbij wie ze is en wat het gerecht is, plus \u00e9\u00e9n regel over taco's, want
         de balk telt ze vanaf de eerste seconde terwijl de uitleg pas op slide 2 van de rondleiding
         komt, en die kun je overslaan. Vanaf dag 2 is het weer \u00e9\u00e9n korte regel. */
      (dagenTotaal() <= 1
        ? "<p class='muted' style='margin:6px 0 0'>"+ct(
            "Taco's zijn je punten van vandaag. Ook een fout antwoord levert er een op.",
            "Tacos are today's points. A wrong answer earns one too.")+"</p>"+
          "<p class='muted' style='margin:2px 0 0'>"+ct(
            "Chispa is het diertje bovenin; ze groeit mee met jou. Na je les mag je haar iets lekkers geven: "+
              tapaHoy.e+" <b>"+tapaHoy.es+"</b> ("+tapaHoy.nl+").",
            "Chispa is the little creature up top; she grows along with you. After your session you get to give her a treat: "+
              tapaHoy.e+" <b>"+tapaHoy.es+"</b> ("+tapaHoy.en+").")+"</p>"
        : "<p class='muted' style='margin:2px 0 0'>"+ct(
            "Daarna mag je Chispa "+tapaHoy.e+" <b>"+tapaHoy.es+"</b> ("+tapaHoy.nl+") geven.",
            "Then you get to give Chispa "+tapaHoy.e+" <b>"+tapaHoy.es+"</b> ("+tapaHoy.en+").")+"</p>"))+''')

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
