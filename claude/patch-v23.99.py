#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.99: twintig plekken waar een Engelstalige Nederlands kreeg (punt 16).

De app spreekt twee talen, en `ct()` regelt dat overal. Behalve op twintig plekken, en die zitten
uitgerekend waar het het meest pijn doet: het aanmeldscherm.

Wie in het Engels binnenkomt en een naam vergeet in te vullen, krijgt "Vul eerst een naam in."
Wie zijn voortgang zoekt via e-mail krijgt "Geen voortgang gevonden bij dit e-mailadres." Wie een
groepscode invult krijgt "Die code lijkt te kort, check hem even." Dat zijn precies de momenten
waarop iemand vastloopt, en dan staat er een taal die hij niet leest.

De rest zit in Palabra Duel, de groepen, het bewaren van je e-mail en het importeren van voortgang.

Alle twintig gaan nu door `ct()`. Geen nieuwe mechaniek, alleen consequent zijn.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.99"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.99" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

PAREN = [
  ('nk.textContent = "Welkom! Maak je profiel";',
   'nk.textContent = ct("Welkom! Maak je profiel","Welcome! Create your profile");'),
  ('"<p class=\'muted\'>Vul eerst een geldig e-mailadres in.</p>"',
   '"<p class=\'muted\'>"+ct("Vul eerst een geldig e-mailadres in.","Please enter a valid e-mail address first.")+"</p>"'),
  ('"<p class=\'muted\'>Geen voortgang gevonden bij dit e-mailadres. Check de spelling, of was het profiel zonder e-mail aangemaakt?</p>"',
   '"<p class=\'muted\'>"+ct("Geen voortgang gevonden bij dit e-mailadres. Check de spelling, of was het profiel zonder e-mail aangemaakt?","No progress found for this e-mail address. Check the spelling, or was the profile created without an e-mail?")+"</p>"'),
  ('"<p class=\'muted\'>Gevonden! Kies je profiel:</p>"',
   '"<p class=\'muted\'>"+ct("Gevonden! Kies je profiel:","Found it! Pick your profile:")+"</p>"'),
  ('"Die code lijkt te kort, check hem even."',
   'ct("Die code lijkt te kort, check hem even.","That code looks too short, have another look.")'),
  ('"Code niet gevonden (of de server slaapt even, probeer zo nog eens)."',
   'ct("Code niet gevonden (of de server slaapt even, probeer zo nog eens).","Code not found (or the server is asleep, try again shortly).")'),
  ('"Vul eerst een naam in."',
   'ct("Vul eerst een naam in.","Please enter a name first.")'),
  ('"Kies eerst een niveau (Beginner of A2)."',
   'ct("Kies eerst een niveau (Beginner of A2).","Pick a level first (Beginner or A2).")'),
  ('"Vul eerst een naam in, dan start de test."',
   'ct("Vul eerst een naam in, dan start de test.","Enter a name first, then the test starts.")'),
  ('toast("Duel niet gevonden.")',
   'toast(ct("Duel niet gevonden.","Duel not found."))'),
  ('"<div class=\'feedback bijna\'>Typ of tik eerst een woord van minstens 2 letters.</div>"',
   '"<div class=\'feedback bijna\'>"+ct("Typ of tik eerst een woord van minstens 2 letters.","Type or tap a word of at least 2 letters first.")+"</div>"'),
  ('"<div class=\'feedback fout\'>Dat past niet in deze letters (elke letter mag maar zo vaak als hij er ligt).</div>"',
   '"<div class=\'feedback fout\'>"+ct("Dat past niet in deze letters (elke letter mag maar zo vaak als hij er ligt).","That does not fit these letters (each letter only as often as it is there).")+"</div>"'),
  ('"<div class=\'feedback bijna\'>Server even niet bereikbaar, probeer zo opnieuw.</div>"',
   '"<div class=\'feedback bijna\'>"+ct("Server even niet bereikbaar, probeer zo opnieuw.","Server briefly unreachable, try again in a moment.")+"</div>"'),
  ('toast(m ? "E-mail bewaard ✓ Hiermee kun je je voortgang altijd terugvinden." : "E-mail verwijderd.")',
   'toast(m ? ct("E-mail bewaard ✓ Hiermee kun je je voortgang altijd terugvinden.","E-mail saved ✓ This lets you find your progress again any time.") : ct("E-mail verwijderd.","E-mail removed."))'),
  ('toast("Meedoen met de groep lukte nog niet. Ga naar Profiel 👤 en vul code "+gcode+" in.")',
   'toast(ct("Meedoen met de groep lukte nog niet. Ga naar Profiel 👤 en vul code "+gcode+" in.","Joining the group did not work yet. Go to Profile 👤 and enter code "+gcode+"."))'),
  ('st.textContent = "Server even niet bereikbaar, probeer zo opnieuw."',
   'st.textContent = ct("Server even niet bereikbaar, probeer zo opnieuw.","Server briefly unreachable, try again in a moment.")'),
  ('toast("Geef je groep eerst een naam.")',
   'toast(ct("Geef je groep eerst een naam.","Give your group a name first."))'),
  ('toast("Vul eerst een groepscode in.")',
   'toast(ct("Vul eerst een groepscode in.","Enter a group code first."))'),
  ('toast("Je doet mee met \'"+res.groep.naam+"\'! 🎉")',
   'toast(ct("Je doet mee met \'"+res.groep.naam+"\'! 🎉","You have joined \'"+res.groep.naam+"\'! 🎉"))'),
  ('alertBox("Dat lijkt geen geldige voortgang. Plak precies wat je eerder exporteerde.")',
   'alertBox(ct("Dat lijkt geen geldige voortgang. Plak precies wat je eerder exporteerde.","That does not look like valid progress. Paste exactly what you exported earlier."))'),
]

if DOE_APP:
    ontbreekt = [i + 1 for i, p in enumerate(PAREN) if p[0] not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; anker %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.98. Eerst bijtrekken:\n\n    git pull --rebase\n"
              % ", ".join(map(str, ontbreekt)))
        sys.exit(1)
    for a, b in PAREN:
        n = src.count(a)
        assert n == 1, "anker komt %d keer voor in plaats van 1:\n%s" % (n, a[:160])
        src = src.replace(a, b, 1)

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
