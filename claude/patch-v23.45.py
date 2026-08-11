#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.45: op dag 1 staat er niets dat nul is, en niemand wordt twee keer gepeild.

Punt 1 van claude/lancering.md gaat over dag 1 van een vreemde. v23.43 haalde de knoppen weg die
niets konden. Dit is de tweede helft: de blokken die er staan zonder iets te zeggen.

Nagemeten op een vers A0-profiel, telefoonformaat, met en zonder de helling van v23.44.

## Zonder de helling (drie woorden), 15 klikbare dingen

    🚦 START JE LES        de ene handeling. Goed.
    0                      "van je 3 woorden, gewogen naar hoe lang je ze onthoudt"
    Alle cijfers →
    EVEN SPELEN            Aventura, Rompecabezas. Allebei speelbaar sinds v23.43.

Die nul is het eerste getal dat een vreemde van deze app te zien krijgt. En hij kán op dag 1 niets
anders zijn: `kracht` weegt naar hoe lang je een woord vasthoudt, en dat is per definitie nul als je
vandaag begonnen bent. Een tegel die op zijn eerste dag alleen nul kan tonen is geen meting maar een
plaatshouder, en de kaart eromheen weet dat al beter dan de tegel zelf. Zie dagRelevantie():

    // een kaart die meldt dat er niets te melden is, is zelf de melding
    // deze drie stonden er ook als ze nul waren, en nul is geen bericht

De krachttegel verscheen bij `c.geoefend > 0`, en dat is de verkeerde voorwaarde: hij zegt "er staat
iets in je lijst", niet "er valt iets te melden". Hij verschijnt nu bij `c.kracht > 0`.

## Met de helling (zeventien woorden), 18 klikbare dingen

Hier staat iets dat ik gisteren zelf heb veroorzaakt:

    WAAR JE STAAT · A1
    ...
    Peil je niveau opnieuw
    12 woorden, ongeveer een minuut. Telt niet mee voor je punten.

De app biedt een peiling van twaalf woorden aan iemand die net dertig woorden heeft gedaan. Dat is
niet alleen overbodig, het ondermijnt precies waar de helling voor is.

De oorzaak is één ontbrekende regel. peilKlaar() zet `S.peil.laatst` en schrijft een regel in
`S.peil.log`; de helling schreef alleen `S.peil.items`. peilAanbod() leest dan een schatting (die er
nu wél is), ziet `peilDagenGeleden("")` als 9999, en dat is meer dan de veertien dagen tussenpoos.

    if(!sch){
      if(!S.lesFlowEerste) return null;      <- dit vangnet gold alleen zonder schatting
      return {niv:niv, eerste:!S.peil.laatst};
    }
    if(peilDagenGeleden(S.peil.laatst) < PEIL_HERHAAL) return null;

De helling is een peiling, dus schrijft hij zich nu ook zo weg: `laatst` op vandaag en een regel in
`log` met dezelfde velden die peilKlaar() gebruikt. Dat lost twee dingen tegelijk op. Er komt de
eerste twee weken geen tweede peiling meer, en de voortgangspagina heeft vanaf dag 1 een nulpunt om
groei tegen af te zetten in plaats van pas na je eerste losse peiling.

## Wat er bewust NIET gebeurt

EVEN SPELEN blijft op dag 1 staan. "Eén handeling op dag 1" was het uitgangspunt, maar Stefan koos
op 11 aug expliciet dat er spellen zichtbaar moeten zijn, en sinds v23.43 staan er alleen nog
spellen die ook echt kunnen draaien. Een blok van twee tegels die allebei werken is geen ruis.

En de kaart WAAR JE STAAT blijft staan voor wie de helling deed. Vijftien regels is veel, maar dat
is precies de opbrengst van dertig woorden beantwoorden: het is de beloning, niet de rommel.

Wat wel blijft staan als open punt: op dat scherm zeggen "15 woorden houd je actief bij" (bovenin)
en "3 van je 17 woorden, gewogen naar hoe lang je ze onthoudt" (onderin) twee verschillende dingen
met bijna dezelfde woorden. Dat is dicht bij maatstaf 1 uit claude/rapport.md en het verdient een
eigen versie, want het gaat over de inhoud van dat scherm en niet over dag 1.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.45"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.45: de helling is een peiling" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

if DOE_APP:
    ANKERS = [
        '  if(c.geoefend > 0){',
        '    for(kh in items0) if(!S.peil.items[kh]) S.peil.items[kh] = {r:items0[kh], d:today(), niv:"A1"};',
        'var APP_VERSIE = "v23.44";',
    ]
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:80] for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.44 (de helling). Eerst die draaien, of eerst bijtrekken:\n"
              "\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. versie ----------
    rep('var APP_VERSIE = "v23.44";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 2. nul is geen bericht, ook niet in een tegel ----------
    rep('  if(c.geoefend > 0){',
        '  /* v23.45: hier stond c.geoefend > 0, en dat is de verkeerde vraag. Die zegt "er staat iets\n'
        '     in je lijst", niet "er valt iets te melden". Op dag 1 kan kracht niets anders zijn dan\n'
        '     nul (hij weegt naar hoe lang je een woord vasthoudt), dus kreeg elke vreemde als eerste\n'
        '     getal van deze app een 0 te zien, met "van je 3 woorden" eronder. De kaart eromheen wist\n'
        '     dat al beter: zie dagRelevantie(), "nul is geen bericht". */\n'
        '  if(c.geoefend > 0 && c.kracht > 0){')

    # ---------- 3. de helling is een peiling, dus schrijft hij zich zo weg ----------
    rep('    for(kh in items0) if(!S.peil.items[kh]) S.peil.items[kh] = {r:items0[kh], d:today(), niv:"A1"};',
        '    for(kh in items0) if(!S.peil.items[kh]) S.peil.items[kh] = {r:items0[kh], d:today(), niv:"A1"};\n'
        '    /* v23.45: de helling is een peiling, dus schrijft hij zich ook zo weg. Zonder deze regels\n'
        '       stond S.peil.laatst nog op "" terwijl er wél een schatting lag, en dan komt peilAanbod()\n'
        '       via peilDagenGeleden("") = 9999 uit op "aanbieden". Gevolg: de app bood een peiling van\n'
        '       twaalf woorden aan iemand die net dertig woorden had gedaan. Meteen erbij: de\n'
        '       voortgangspagina heeft nu vanaf dag 1 een nulpunt om groei tegen af te zetten, in\n'
        '       plaats van pas na je eerste losse peiling. Zelfde velden als peilKlaar() schrijft. */\n'
        '    if(Object.keys(items0).length){\n'
        '      S.peil.laatst = today();\n'
        '      S.peil.log = S.peil.log || [];\n'
        '      var schH = null;\n'
        '      try { schH = niveauSchatting("A1"); } catch(e){ schH = null; }\n'
        '      if(schH) S.peil.log.push({d:today(), niv:"A1", punt:schH.punt, onder:schH.onder,\n'
        '                                boven:schH.boven, n:schH.n, vast:schH.vast, hel:1});\n'
        '    }')

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
