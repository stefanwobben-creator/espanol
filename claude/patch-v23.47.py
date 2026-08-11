#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.47: de onboarding zegt alleen nog dingen die waar zijn.

Stefan, 11 aug, na het doorlopen van de schermen: "het verwijst ook nog naar oude dingen zoals
grammatica, want dat is maar een klein onderdeel nu."

Dat klopte, en het waren er vier. Alle vier hetzelfde soort fout: de tekst is niet meegegroeid met
wat de app doet. Geen van de vier is een bug, en juist daarom vindt niemand ze: de app werkt, hij
vertelt het alleen verkeerd.

## 1. De niveautest concurreerde met het voorstel

Onder "Op grond van je woorden zetten we je op A1" stond nog:

    [Weet ik niet: doe de niveautest]
    Kies een niveau, of doe de test van 10 vragen (2 minuten).

Twee problemen tegelijk. De app vraagt niet meer om een keuze, dus "Kies een niveau" is geen
instructie meer maar een tegenspraak. En die tien vragen gaan over grammatica, terwijl je niveau nu
uit dertig woorden komt: twee wegen naar hetzelfde antwoord die verschillend kunnen uitpakken.

Zodra er een voorstel staat, verdwijnt de instructieregel en heet de knop wat hij is: de
grammaticatest van tien vragen. Het woord "niveau" is nu van de dertig woorden. Wie de helling
overslaat krijgt gewoon het oude scherm met de oude tekst, want daar is het nog wél de manier om je
niveau te bepalen.

## 2. Grammatica kreeg een kwart van je dagles

    6 woordjes (5 nieuw) · 1 grammaticapunt · 1 toetsje · 1 oefenronde

Vier gelijkwaardige stukken in de zin, zes tegen één in werk. De opsomming gaf elk onderdeel
evenveel gewicht door ze alle vier als "1 iets" te tellen. Nu staat er wat het is: de woordjes, en
daarna kort de rest.

## 3. De rondleiding beloofde vijftien nieuwe woordjes

    "Elke dag een klein stapje: hooguit 15 nieuwe woordjes."

Bij het standaard dagdoel van tien minuten is je portie er vijf en je plafond acht. "Hooguit" maakt
de zin formeel waar en praktisch misleidend: je leest vijftien en je krijgt er vijf. De zin rekent
nu met jouw eigen instelling, via een plaatshouder die showTour() invult. Verandert je dagdoel, dan
verandert de zin mee.

## 4. De rondleiding wees naar schermen die niet meer bestaan

Twee stappen (die pas verschijnen als je de rondleiding later zelf opnieuw opent via de voetregel)
beschreven een app van maanden geleden:

    "Onder Grammatica staat elk onderwerp opgeknipt in stappen ... de ronde 📖-knop bovenin is je
     woordenboek ... en in de Speeltuin leer je spelenderwijs verder"
    "Tik op je naam bovenaan voor je voortgang, je geheime sync-code en Groepen"

Nagemeten hoe het nu werkelijk is: de balk heeft vijf plekken (Vandaag, Woordjes, Oefenen, Spelen,
Meer). Grammatica is één van vier tegels ónder Oefenen. De ronde 📖-knop bestaat niet meer, dat is
sinds v21.6 de pil "🔍 Zoek" rechtsboven — en die is toen juist veranderd omdat Stefan zelf niet
wist dat dat boekje het woordenboek was. De Speeltuin heet in de balk "Spelen". En je voortgang zit
sinds v23.32 niet meer bij je naam maar onder Meer als eigen ingang.

Dit is de gemeenste van de vier: het is de tekst achter de link "Rondleiding", dus precies wat
iemand opent als hij het even niet meer weet. Verouderde hulp is erger dan geen hulp.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.47"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "{{NIEUWPERDAG}}" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

if DOE_APP:
    ANKERS = [
        'var APP_VERSIE = "v23.46";',
        '    d.push("1 " + ct("grammaticapunt","grammar point"));',
        'hooguit <b>15 nieuwe woordjes</b>',
        'at most <b>15 new words</b>',
        'Alles binnen handbereik',
        'Everything within reach',
        'function helVoorstelToepassen(v){',
    ]
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:80] for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.46. Eerst die draaien, of eerst bijtrekken:\n"
              "\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.46";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 1. de dagles: woordjes voorop, de rest kort ----------
    rep('    d.push("1 " + ct("grammaticapunt","grammar point"));\n'
        '    d.push("1 " + ct("toetsje","quiz"));\n'
        '    d.push("1 " + ct("oefenronde","practice round"));',
        '    /* v23.47: hier stonden drie losse "1 iets"-onderdelen naast de woordjes. Dat gaf elk\n'
        '       kwart van de zin evenveel gewicht terwijl het in werk zes tegen een is, en het maakte\n'
        '       van grammatica een kwart van je dagles. Stefan, 11 aug: "grammatica is maar een klein\n'
        '       onderdeel nu." Eén regel voor de rest, en de woordjes houden de kop. */\n'
        '    d.push(ct("daarna kort: grammatica, een toetsje en oefenen",\n'
        '              "then briefly: grammar, a quiz and practice"));')

    # ---------- 2. de rondleiding rekent met jouw dagportie ----------
    rep('txt:"Elke dag een klein stapje: hooguit <b>15 nieuwe woordjes</b>.',
        'txt:"Elke dag een klein stapje: bij jouw instelling zijn dat <b>{{NIEUWPERDAG}} nieuwe woordjes</b> per dag.')
    rep('txt:"One small step a day: at most <b>15 new words</b>.',
        'txt:"One small step a day: with your setting that is <b>{{NIEUWPERDAG}} new words</b> a day.')

    # showTour vult de plaatshouder. Eén plek, want zowel TOUR als TOUR_EN gaan hierdoorheen.
    rep('  } else {\n    midden = "<p>"+t.txt+"</p>";',
        '  } else {\n'
        '    /* v23.47: de rondleiding beloofde "hooguit 15 nieuwe woordjes" terwijl je er bij het\n'
        '       standaard dagdoel van tien minuten vijf krijgt. "Hooguit" maakt dat formeel waar en\n'
        '       praktisch misleidend. Nu rekent de zin met jouw eigen instelling; verandert je\n'
        '       dagdoel, dan verandert de zin mee. */\n'
        '    var txt = String(t.txt || "");\n'
        '    if(txt.indexOf("{{NIEUWPERDAG}}") !== -1){\n'
        '      var npd = 5;\n'
        '      try { npd = nieuwPerDag(); } catch(e){}\n'
        '      txt = txt.replace(/\\{\\{NIEUWPERDAG\\}\\}/g, npd);\n'
        '    }\n'
        '    midden = "<p>"+txt+"</p>";')

    # ---------- 3. de twee stappen die naar oude schermen wezen ----------
    OUD_NL_NAV = ('   txt:"Onder <b>Grammatica</b> staat elk onderwerp opgeknipt in stappen met vragen erbij '
                  '(plus alle spiekbrieven en toetsjes), de ronde 📖-knop bovenin is je woordenboek (opent als '
                  'popup, altijd bij de hand), en in de <b>Speeltuin</b> leer je spelenderwijs verder met '
                  'muziek, memory en meer."},')
    NIEUW_NL_NAV = ('   txt:"Onderin staan vijf plekken. <b>Vandaag</b> is je dagles. <b>Woordjes</b> en '
                    '<b>Spelen</b> open je uit jezelf. Onder <b>Oefenen</b> staat alles wat meetelt voor je '
                    'niveau, waaronder Grammatica: regels opzoeken en oefenen zonder ze uit je hoofd te leren. '
                    'Achter <b>Meer</b> zit de rest, met een zin erbij die zegt wat het is. En iets opzoeken kan '
                    'altijd: de pil <b>🔍 Zoek</b> rechtsboven opent je woordenboek."},')
    rep(OUD_NL_NAV, NIEUW_NL_NAV)

    OUD_EN_NAV = ('   txt:"Under <b>Grammar</b> every topic is cut into steps with questions (plus all the '
                  'cheat sheets and quizzes), the round 📖 button at the top is your dictionary (opens as a '
                  'popup, always at hand), and in the <b>Playground</b> you keep learning through music, '
                  'memory and more."},')
    NIEUW_EN_NAV = ('   txt:"There are five places along the bottom. <b>Today</b> is your daily lesson. '
                    '<b>Words</b> and <b>Play</b> you open yourself. Under <b>Practice</b> sits everything that '
                    'counts towards your level, including Grammar: look up the rules and practise them without '
                    'memorising them. Behind <b>More</b> is the rest, each with a line saying what it is. And '
                    'you can always look something up: the <b>🔍 Search</b> pill at the top opens your '
                    'dictionary."},')
    rep(OUD_EN_NAV, NIEUW_EN_NAV)

    OUD_NL_SAMEN = ('   txt:"Tik op je <b>naam</b> bovenaan voor je voortgang, je geheime sync-code en '
                    '<b>Groepen</b>: start er een met vrienden of klasgenoten en deel de uitnodigingslink. '
                    'Ben je docent? Maak een groep voor je klas en nodig je leerlingen uit."},')
    NIEUW_NL_SAMEN = ('   txt:"Achter <b>Meer</b> vind je <b>Voortgang</b> (je week, je doel en waar je staat) '
                      'en <b>Profiel</b>: je instellingen, je geheime sync-code en <b>Groepen</b>. Start er een '
                      'met vrienden of klasgenoten en deel de uitnodigingslink. Ben je docent? Maak een groep '
                      'voor je klas en nodig je leerlingen uit."},')
    rep(OUD_NL_SAMEN, NIEUW_NL_SAMEN)

    OUD_EN_SAMEN = ('   txt:"Tap your <b>name</b> at the top for your progress, your secret sync code and '
                    '<b>Groups</b>: start one with friends or classmates and share the invite link. Are you a '
                    'teacher? Create a group for your class and invite your students."},')
    NIEUW_EN_SAMEN = ('   txt:"Behind <b>More</b> you will find <b>Progress</b> (your week, your goal and where '
                      'you stand) and <b>Profile</b>: your settings, your secret sync code and <b>Groups</b>. '
                      'Start one with friends or classmates and share the invite link. Are you a teacher? '
                      'Create a group for your class and invite your students."},')
    rep(OUD_EN_SAMEN, NIEUW_EN_SAMEN)

    # ---------- 4. de niveautest concurreert niet meer met het voorstel ----------
    rep('''    var r = document.getElementById("helRegel");
    if(r){''',
        '''    /* v23.47: zodra er een voorstel staat, klopt "Kies een niveau, of doe de test van 10
       vragen" niet meer: de app vráágt niet meer om een keuze. En die tien vragen gaan over
       grammatica, terwijl je niveau nu uit dertig woorden komt; het woord "niveau" hoort daarbij.
       De knop blijft staan als uitweg, maar heet wat hij is. Wie de helling overslaat, houdt het
       oude scherm met de oude tekst, want daar is die test wél de manier om je niveau te bepalen. */
    var hint = document.getElementById("profHint");
    if(hint) hint.textContent = "";
    var bp = document.getElementById("btnPlacement");
    if(bp) bp.textContent = (proefTaal() === "nl")
      ? "Liever de grammaticatest van 10 vragen?"
      : "Rather take the 10-question grammar check?";
    var r = document.getElementById("helRegel");
    if(r){''')

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
