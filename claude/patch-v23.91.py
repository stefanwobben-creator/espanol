#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.91: het verhaal achter ¡Vamos!, door Stefan herschreven.

Stefan leverde op 14 aug een nieuwe Nederlandse tekst aan voor de kaart "Het verhaal achter ¡Vamos!"
op de pagina Hoe dit werkt & steun de app. Dit voert die tekst één op één door.

## Wat er verandert

De oude tekst zei dat de bekende apps "gebouwd zijn om je elke dag te laten terugkomen, niet om je
iets te leren". Dat is een verwijt. De nieuwe zegt iets scherpers en eerlijkers: ze zijn juist erg
goed in waar ze op gebouwd zijn, en het probleem is dat wat je meet is wat je krijgt. Zij meten of je
terugkomt, hij wilde iets dat meet of hij het kán. Dat is dezelfde observatie zonder de neerbuigende
toon, en het is meteen de belofte van de app.

Nieuw is ook de alinea over wat "geleerd" betekent: vijf keer echt ingetypt, verspreid over minstens
vijfentwintig dagen. Nagekeken in de code voordat het erin ging, want een belofte op de steunpagina
moet waar zijn: `stevigDrempel()` geeft `INTERVALS.length - 1`, oftewel doos 5, en die kost vijf keer
achter elkaar goed over minstens 25 dagen. Klopt dus.

En het klassement is nu een verhaal in plaats van een detail. De oude tekst noemde het onderlinge
klassement als leuk kenmerk; de nieuwe vertelt dat het eruit is gesloopt omdat mensen gingen spelen
om te winnen in plaats van om te leren, en wat ervoor in de plaats kwam. Dat is de betere zin, want
het is het enige stuk van de tekst dat een keuze laat zien in plaats van een eigenschap.

## Wat er niet verandert

Alleen het Nederlands. Dezelfde kaart bestaat in het Engels (steunEN), Frans (steunFR) en Duits
(steunDE) en die dragen nog de oude tekst. Dat is een bewuste beperking van deze patch en geen
vergissing: Stefan heeft de Nederlandse versie geschreven en de andere drie zijn vertaalwerk dat hij
zelf wil kunnen nakijken.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.91"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.91" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

# De drie alinea's die vervangen worden. De vetgedrukte openingszin en de Chispa-alinea blijven
# ongemoeid, dus die staan hier niet in.
A_OUD = '''        <p>Sinds ik van Nederland naar Spanje verhuisde, probeer ik de taal echt te leren. Ik testte alle bekende apps, maar die zijn gebouwd om je elke dag te laten terugkomen, niet om je iets te leren. En de meeste mensen stoppen niet omdat Spaans te moeilijk is, maar omdat het te saai wordt. Dus maakte ik er zelf een.</p>
        <p>\u00a1Vamos! volgt de boeken van mijn echte Spaanse les (twee keer per week bij <a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, aanrader). Je typt je antwoorden in plaats van ze aan te klikken, elk woord komt precies terug op het moment dat je het bijna vergeten bent, en jouw fouten worden \'s nachts verwerkt in nieuwe oefeningen. Fouten maken kost geen punten, het levert ze juist op. En een dagje missen? Echt prima. Deze app is een aanvulling op spr\u00e9ken, geen vervanging. Taal leer je in gesprek; de app zorgt dat je in dat gesprek iets te zeggen hebt.</p>'''

A_SLOT = '''        <p>Ik bouwde dit voor mezelf, maar inmiddels leert mijn hele familie mee, compleet met onderling klassement. Dat vind ik stiekem het mooiste. Want een nieuwe taal is de beste workout die je je brein kunt geven.</p>'''

NIEUW_MIDDEN = '''        <p>Sinds ik van Nederland naar Spanje verhuisde, probeer ik de taal echt te leren. Ik testte alle bekende apps, en ze zijn erg goed in waar ze op gebouwd zijn: zorgen dat je morgen terugkomt. Dat werkte ook, ik had een streak van maanden. Alleen kon ik nog steeds geen zin maken op de markt. Elke app meet iets, en wat je meet is wat je krijgt. Zij meten of je terugkomt. Ik wilde iets dat meet of ik het k\u00e1n.</p>
        <p>En ik stopte nooit omdat Spaans te moeilijk was, maar omdat het te saai werd. Dus maakte ik er zelf een.</p>
        <p>\u00a1Vamos! volgt de boeken van mijn echte Spaanse les (twee keer per week bij <a href="https://escuela-elcano.com/" target="_blank" rel="noopener">Escuela Elcano</a>, aanrader). Je typt je antwoorden in plaats van ze aan te klikken, en elk woord komt precies terug op het moment dat je het bijna vergeten bent.</p>
        <p>Het verschil zit in wat "geleerd" betekent. In de meeste apps tik je het goede plaatje aan uit vier, en dan telt het. Hier telt een woord pas als je het vijf keer echt hebt ingetypt, verspreid over minstens vijfentwintig dagen. Dat gaat traag. Dat is de bedoeling, want anders meet je alleen hoe vaak je hebt getikt.</p>
        <p>En jouw fouten worden \'s nachts verwerkt in nieuwe oefeningen. Niet over een willekeurig thema, maar over precies dat ene ding waar jij steeds over struikelt. Fouten maken kost geen punten, het levert ze juist op. En een dagje missen? Echt prima. Deze app is een aanvulling op spr\u00e9ken, geen vervanging. Taal leer je in gesprek; de app zorgt dat je in dat gesprek iets te zeggen hebt.</p>'''

NIEUW_SLOT = '''        <p>Ik bouwde dit voor mezelf, maar inmiddels leert mijn hele familie mee. Er was een onderling klassement, en dat heb ik er weer uitgesloopt. Je ging spelen om te winnen in plaats van om iets te leren. Nu zie je op je beginscherm gewoon wat de anderen die dag hebben geleerd, zonder punten en zonder vergelijking, en kun je er iets terugroepen. Dat vind ik stiekem het mooiste. Want een nieuwe taal is de beste workout die je je brein kunt geven.</p>'''

if DOE_APP:
    ontbreekt = [n for n, a in (("de twee middelste alinea's", A_OUD), ("de slotalinea", A_SLOT))
                 if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.88. Eerst bijtrekken:\n\n    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_OUD, NIEUW_MIDDEN)
    rep(A_SLOT, NIEUW_SLOT)

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
