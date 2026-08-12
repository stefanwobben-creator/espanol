#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.72: de privacytekst zegt precies wat de server bewaart, niet ongeveer.

Van de lanceerlijst, punt 5: "De privacytekst moet kloppen met wat de server echt bewaart."

Ik heb elke schrijfopdracht in `server/index.js` opgezocht en naast de tekst gelegd. Zeven tabellen,
zestien plekken waar er iets in gaat:

    profiles       code, naam, track, state (de hele S), updated_at        ✓ genoemd
    logs           code, soort, payload, tijdstip                          ✓ genoemd
    groups         gcode, naam                                             ✓ genoemd
    group_members  gcode, pcode                                            ✓ genoemd
    maatjes        mcode, pcode, naam                                      ✓ genoemd
    krabbels       van, naar, sleutel, dag                                 ✗ niet genoemd
    duels          id, letters, players (namen), moves (jouw woorden)      ✗ niet genoemd

Twee gaten dus, en allebei van dezelfde soort: iets wat je naar een ander stuurt en waarvan je niet
verwacht dat het blijft staan.

**Palabra Duel** bewaart je naam en elk woord dat je speelt, met de punten en de vertaling, in een
rij die nooit wordt opgeruimd. Dat woord gaat bovendien langs een taalmodel (de scheidsrechter). Het
staat nergens.

**Krabbels** bewaren wie wie een schouderklopje gaf, per dag. Geen tekst (de sleutel wijst naar een
zin die op de server staat, dat was juist het ontwerp), maar wel wie en wanneer.

En één zin die te mooi was. Er stond "Voor de kopie op de server is er nog geen knop: stuur een
mailtje met je sync-code en hij wordt verwijderd." Dat klopt voor je profiel, maar niet voor de rest:
`/api/admin/schoon` gooit alleen lege profielen weg, en logs, duels en krabbels worden nergens
opgeruimd. Zolang dat zo is hoort er te staan hoe lang iets blijft staan, en het eerlijke antwoord
is: totdat je het vraagt.

## Wat er níét verandert

De rest van de tekst was goed en blijft staan, inclusief de twee scherpe zinnen die een
privacytekst zelden haalt: dat je sync-code een wachtwoord is, en dat wie je e-mailadres kent je
code kan opvragen.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.72"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "Wat er blijft staan, en hoe lang" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_ANDEREN = u'''    blok("\U0001f440 "+ct("Wat anderen van je zien","What others see of you"),
      "<p>"+ct("In een familie of groep zien de anderen je naam en je punten. Je oefeningen, je fouten en je antwoorden blijven van jou; die krijgt niemand te zien.","In a family or group the others see your name and your points. Your exercises, your mistakes and your answers stay yours; nobody gets to see those.")+"</p>"+
      "<p class='muted'>"+ct("Een groep of familie verlaten kan altijd, en dan ben je daar meteen weg.","You can leave a group or family at any time, and then you're gone from it straight away.")+"</p>")+'''

A_WEG = u'''    blok("\U0001f9f9 "+ct("Weg is weg","Gone is gone"),
      "<p>"+ct("De kopie op je toestel wis je door de browsergegevens van deze site te wissen. Voor de kopie op de server is er nog geen knop: stuur een mailtje met je sync-code en hij wordt verwijderd.","You erase the copy on your device by clearing this site's browser data. For the copy on the server there's no button yet: send an email with your sync code and it gets deleted.")+"</p>"+
      "<p class='muted'>"+ct("Je kunt je voortgang ook zelf exporteren naar een bestand via Profiel, en die overal naartoe meenemen.","You can also export your progress to a file yourself via Profile, and take it anywhere.")+"</p>")+'''

if DOE_APP:
    ontbreekt = [a for a in [A_ANDEREN, A_WEG] if a not in src]
    if ontbreekt:
        print("De privacytekst ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
              "\n\nEerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_ANDEREN, A_ANDEREN + u'''

    /* v23.72: dit blok ontbrak. Palabra Duel bewaart je naam en elk woord dat je speelt in de tabel
       `duels`, en krabbels bewaren wie wie een schouderklopje gaf. Allebei dingen die je naar een
       ander stuurt en waarvan je niet verwacht dat ze blijven staan. */
    blok("\\u2694\\ufe0f "+ct("Als je met iemand speelt","When you play with someone"),
      "<p>"+ct("Doe je een Palabra Duel, dan gaan de naam die je daar invult en elk woord dat je speelt naar de server, met de punten erbij. Je tegenstander ziet die woorden, en ze blijven bij het duel staan.","If you play a Palabra Duel, the name you enter there and every word you play go to the server, with the points. Your opponent sees those words, and they stay with the duel.")+"</p>"+
      "<p class='muted'>"+ct("Je woord gaat ook langs een taalmodel, want dat is de scheidsrechter die bepaalt of het bestaat. Verder gaat er niets van je mee.","Your word also goes past a language model, because that is the referee deciding whether it exists. Nothing else of yours goes with it.")+"</p>"+
      "<p class='muted'>"+ct("Een krabbel bij een familielid bewaart wie wie een schouderklopje gaf en op welke dag. De tekst zelf staat op de server en kies je uit een lijstje, dus er kan niets anders in.","A note left for a family member records who gave whom a pat on the back and on what day. The text itself lives on the server and you pick it from a list, so nothing else can go into it.")+"</p>")+''')

    rep(A_WEG, u'''    /* v23.72: hier stond dat een mailtje met je sync-code je gegevens verwijdert. Dat klopt voor je
       profiel, maar niet voor de rest: /api/admin/schoon gooit alleen lege profielen weg, en logs,
       duels en krabbels worden nergens opgeruimd. Zolang dat zo is hoort er te staan hoe lang iets
       blijft staan, en het eerlijke antwoord is: totdat je het vraagt. */
    blok("\U0001f9f9 "+ct("Wat er blijft staan, en hoe lang","What is kept, and for how long"),
      "<p>"+ct("De kopie op je toestel wis je door de browsergegevens van deze site te wissen. Op de server is er nog geen knop: stuur een mailtje met je sync-code en je profiel wordt verwijderd.","You erase the copy on your device by clearing this site's browser data. On the server there is no button yet: send an email with your sync code and your profile is deleted.")+"</p>"+
      "<p class='muted'>"+ct("Eerlijk over de rest: er wordt niets automatisch opgeruimd. De logregels van je afgeronde lessen, je duels en je krabbels blijven staan totdat iemand ze weghaalt. Vraag je erom, dan gaan die ook weg.","Honestly about the rest: nothing is cleaned up automatically. The log lines from your finished sessions, your duels and your notes stay until someone removes them. Ask, and those go too.")+"</p>"+
      "<p class='muted'>"+ct("Je kunt je voortgang ook zelf exporteren naar een bestand via Profiel, en die overal naartoe meenemen.","You can also export your progress to a file yourself via Profile, and take it anywhere.")+"</p>")+''')

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
