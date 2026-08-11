#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.46: de meting is een meting, en je dagdoel wacht op je eerste les.

Gemeten op een verse bezoeker die de helling van v23.44 doorloopt:

    taco's van vandaag   50
    dagdoel              30
    kopbalk              "doel gehaald ✓"
    daaronder            "🚦 START JE LES ... Start je les →"

Je dagdoel is dus gehaald voordat je je eerste les hebt gedaan, en de app zegt in dezelfde
schermhoogte "je bent klaar" en "begin". Dat is een tegenstrijdig bevel op het enige moment waarop
een vreemde nog moet besluiten of hij hier iets gaat doen.

De oorzaak is dat ik de helling XP liet uitdelen alsof het een oefening was: twee taco's per goed
antwoord, één per fout, zevenentwintig keer. Dat was niet doordacht maar overgenomen van de proef.

## De regel die de app zelf al had

De peiling zegt het al letterlijk op zijn eigen scherm:

    "Dit is een meting, geen les. Je punten en je doosjes veranderen er niet van."

De helling ís een peiling (sinds v23.45 schrijft hij zich ook zo weg), dus hij hoort zich aan
diezelfde regel te houden. Stefan, 11 aug: "de meting is de meting."

Wat blijft: de drie vaste proefwoorden geven hun taco's gewoon (+5). Dat is het momentje waarop een
vreemde voor het eerst iets terugkrijgt, en dat is precies waar het voor bedoeld is. Je begint dus
op 5/30 en je eerste les is nog steeds de weg naar je dagdoel.

Wat weggaat: de zevenentwintig antwoorden van de helling leveren geen XP meer op. De beloning voor
die dertig woorden is niet een teller maar de uitslag: je weet waar je staat, en de woorden die je
al kende staan al in je leerlijn.

## Ook: het scherm zegt nu wat het doet

Op de vraagschermen van de helling staat er een regel bij, in dezelfde geest als de peiling maar
zonder het woord "meting" (dat klinkt als een toets, en dit is het eerste scherm van iemand die nog
niets van deze app weet). Wie het niet leest verliest niets; wie zich afvraagt waarom hier geen
taco's binnenkomen, vindt het antwoord op het scherm waar de vraag ontstaat.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.46"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.46: de helling deelde XP uit" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

if DOE_APP:
    ANKERS = [
        '    if(keuze === v.goed){ proefStand.helGoed = (proefStand.helGoed || 0) + 1; proefStand.xp += 2; }\n    else proefStand.xp += 1;',
        'var APP_VERSIE = "v23.45";',
        '     klaarKop:"Klaar. En nu weten we iets.", stop:"Genoeg voor nu",',
    ]
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:80] for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.45. Eerst die draaien, of eerst bijtrekken:\n"
              "\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.45";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 1. geen XP uit de helling ----------
    rep('    if(keuze === v.goed){ proefStand.helGoed = (proefStand.helGoed || 0) + 1; proefStand.xp += 2; }\n'
        '    else proefStand.xp += 1;',
        '    /* v23.46: de helling deelde XP uit alsof het een oefening was, twee per goed antwoord en\n'
        '       één per fout. Zevenentwintig keer, en dan sta je op vijftig taco\'s met een dagdoel van\n'
        '       dertig: "doel gehaald ✓" boven een knop die zegt "start je les". De peiling zegt op zijn\n'
        '       eigen scherm al hoe dit hoort ("Dit is een meting, geen les. Je punten en je doosjes\n'
        '       veranderen er niet van"), en de helling is sinds v23.45 ook echt een peiling.\n'
        '       De drie vaste proefwoorden houden hun taco\'s: dat is het eerste dat een vreemde\n'
        '       terugkrijgt, en daar is het voor bedoeld. Je begint dus op 5/30 en je eerste les is nog\n'
        '       steeds de weg naar je dagdoel. */\n'
        '    if(keuze === v.goed) proefStand.helGoed = (proefStand.helGoed || 0) + 1;')

    # ---------- 2. het scherm zegt wat het doet ----------
    rep('     klaarKop:"Klaar. En nu weten we iets.", stop:"Genoeg voor nu",',
        '     klaarKop:"Klaar. En nu weten we iets.", stop:"Genoeg voor nu",\n'
        '     telt:"Deze woorden tellen niet voor je taco\'s, wel voor je startpunt.",')
    rep('     klaarKop:"Done. And now we know something.", stop:"Enough for now",',
        '     klaarKop:"Done. And now we know something.", stop:"Enough for now",\n'
        '     telt:"These words do not count towards your tacos, but they do set your starting point.",')

    rep('''    "<button type='button' class='ghost' id='btnHelGeen' style='margin-top:8px; width:100%'>"+h.geen+"</button>"+
    "<p class='muted' style='margin-top:12px; text-align:center'><a href='#' id='lnkHelStop'>"+h.stop+"</a></p>";''',
        '''    "<button type='button' class='ghost' id='btnHelGeen' style='margin-top:8px; width:100%'>"+h.geen+"</button>"+
    // Zelfde belofte als op het peilingscherm, maar zonder het woord "meting": dat klinkt als een
    // toets, en dit is het eerste scherm van iemand die nog niets van deze app weet.
    "<p class='muted' style='margin:12px 0 0; text-align:center; font-size:.85rem'>"+h.telt+"</p>"+
    "<p class='muted' style='margin-top:10px; text-align:center'><a href='#' id='lnkHelStop'>"+h.stop+"</a></p>";''')

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
