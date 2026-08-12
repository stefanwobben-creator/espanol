#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.51: de knop staat waar je hem zoekt.

Stefan, na de telefoontest van 11 aug, bevinding 3: "de zinnen, die interface is raar. Je
controleert, resultaat is goed of fout, maar dan moet je zelf op de knop volgende zin klikken, dat
vind je niet."

Hij heeft gelijk, en het is een volgordeprobleem. Na Check bouwde `sFeedback` dit op:

    1. de uitslag           ¡Perfecto! ✓ (+5 taco's)
    2. de uitleg            Waarom: Me llamo = letterlijk 'ik noem mijzelf'...
    3. de luisterknoppen    Zo klinkt hij: 🔊 Afspelen 🐢
    4. de knoppen           Volgende zin →   🤖 Meer uitleg

Op een telefoon van 390 pixels staat stap 4 daarmee onder de vouw. Je hebt net goed geantwoord, je
krijgt een groen vinkje, en dan lijkt het op te houden. Op Stefans schermafdruk is precies dat te
zien: de groene balk en de uitleg vullen het scherm, en "Next sentence" hangt er half onder.

De volgorde eronder klopte wel. De uitleg en de luisterknoppen staan er bewust ná de uitslag: pas
als je weet wat er staat en wat het betekent, voegt horen hoe het klinkt iets toe (zie het
commentaar bij `zinLuisterKnopHtml`). Alleen hoort de handeling niet achter de toelichting te
staan.

Nu is het:

    1. de uitslag
    2. de knoppen           Volgende zin →  (of: Probeer opnieuw)
    3. de uitleg
    4. de luisterknoppen

Wat er niet verandert: er komt geen automatische doorloop. De verleiding is om bij een goed antwoord
vanzelf door te gaan, maar dan pak je het moment af waarop je de zin nog even kunt horen, en dat
moment is er met opzet. Het probleem was dat je de knop niet zag, niet dat je erop moest tikken.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.51"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.51: de knoppen stonden" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

OUD = '''  html += "<div class='uitleg'><b>"+ct("Waarom:","Why:")+"</b> "+zinUitleg(s)+"</div>";
  // De juiste zin staat nu in beeld. Dit is het enige moment waarop horen hoe hij klinkt iets
  // toevoegt: je weet wat er staat en wat het betekent, dus je hoort de uitspraak en niet een raadsel.
  html += "<div class='row' style='margin-top:6px'>"+ct("<span class='muted' style='font-size:.85rem; align-self:center'>Zo klinkt hij:</span>","<span class='muted' style='font-size:.85rem; align-self:center'>This is how it sounds:</span>")+zinLuisterKnopHtml()+"</div>";
  html += "<div class='row'>"+
    (retryable ? "<button class='primary' id='btnRetry'>"+ct("Probeer opnieuw","Try again")+"</button>"+
                 "<button class='ghost' id='btnAiCheck'>🤖 "+ct("Is mijn variant ook goed?","Is my version also correct?")+"</button>"+
                 "<button class='ghost' id='btnNext'>"+ct("Volgende zin →","Next sentence →")+"</button>"
               : "<button class='primary' id='btnNext'>"+ct("Volgende zin →","Next sentence →")+"</button><button class='ghost' id='btnAiUitleg'>🤖 "+ct("Meer uitleg","More explanation")+"</button>")+
    "</div><div id='aiFb'></div>";'''

if DOE_APP:
    if 'var APP_VERSIE = "v23.50";' not in src or OUD not in src:
        print("Deze index.html ziet er niet uit zoals verwacht (v23.50 met het oude sFeedback-blok).\n"
              "Eerst bijtrekken, dan pas patchen:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.50";', 'var APP_VERSIE = "%s";' % NIEUW)

    NIEUW_CODE = '''  /* v23.51: de knoppen stonden hier onderaan, ná de uitleg en de luisterknoppen, en op een telefoon
     van 390 pixels valt dat onder de vouw. Stefan: "je controleert, resultaat is goed of fout, maar
     dan moet je zelf op de knop volgende zin klikken, dat vind je niet." De volgorde eronder klopte
     wel (horen hoe het klinkt heeft pas zin als je weet wat er staat), maar de handeling hoort niet
     achter de toelichting. Uitslag, dan wat je nu kunt doen, dan waarom.

     Bewust geen automatische doorloop: dan pak je het moment af waarop je de zin nog kunt horen, en
     dat moment staat er met opzet. Het probleem was dat je de knop niet zag, niet dat je erop moest
     tikken. */
  html += "<div class='row'>"+
    (retryable ? "<button class='primary' id='btnRetry'>"+ct("Probeer opnieuw","Try again")+"</button>"+
                 "<button class='ghost' id='btnAiCheck'>🤖 "+ct("Is mijn variant ook goed?","Is my version also correct?")+"</button>"+
                 "<button class='ghost' id='btnNext'>"+ct("Volgende zin →","Next sentence →")+"</button>"
               : "<button class='primary' id='btnNext'>"+ct("Volgende zin →","Next sentence →")+"</button><button class='ghost' id='btnAiUitleg'>🤖 "+ct("Meer uitleg","More explanation")+"</button>")+
    "</div>";
  html += "<div class='uitleg'><b>"+ct("Waarom:","Why:")+"</b> "+zinUitleg(s)+"</div>";
  // De juiste zin staat nu in beeld. Dit is het enige moment waarop horen hoe hij klinkt iets
  // toevoegt: je weet wat er staat en wat het betekent, dus je hoort de uitspraak en niet een raadsel.
  html += "<div class='row' style='margin-top:6px'>"+ct("<span class='muted' style='font-size:.85rem; align-self:center'>Zo klinkt hij:</span>","<span class='muted' style='font-size:.85rem; align-self:center'>This is how it sounds:</span>")+zinLuisterKnopHtml()+"</div>";
  html += "<div id='aiFb'></div>";'''
    rep(OUD, NIEUW_CODE)

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
