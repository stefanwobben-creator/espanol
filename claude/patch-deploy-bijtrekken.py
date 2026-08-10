#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEPLOY.md: bijtrekken hoort stap 1 te zijn.

Aanleiding van 10 aug. De patch voor v23.30 vond s154 niet, want de avondrun had die zin die nacht
toegevoegd en gepusht, en de Mac had dat nog niet opgehaald. De patch sloeg stil over, de commit ging
door met een boodschap die niet klopte, en de push werd geweigerd.

Twee lessen, allebei op papier want anders zijn ze over drie weken weer nieuw:

1. Bijtrekken hoort in de ronde, als stap 1. Sinds de avondrun 's nachts in index.html schrijft is de
   werkkopie 's ochtends bijna nooit meer waar je hem gisteren achterliet. Dat stond wel in het
   hoofdstuk over de avondrun, maar niet op de plek waar je 's ochtends kijkt.
2. Een patchscript moet "al gedaan" en "hier valt niets te doen" uit elkaar houden. Het eerste is een
   geruststelling, het tweede is een fout die je nu wil zien en niet pas bij de push.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "DEPLOY.md")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "git pull --rebase" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


rep(
    """1. Eén verhaal uitkiezen (zie hieronder).
2. Bouwen. `APP_VERSIE` in `index.html` en `versie.txt` allebei ophogen, altijd samen.
3. Lokaal `node tools/syntaxcheck.js index.html` en `node test/poort.js`.
4. Pushen naar `main`. De poort draait opnieuw, want lokaal groen is geen bewijs.
5. Groen: het staat live, ongeveer drie minuten na de push. Rood: er is niets gebeurd, en onder
   Actions staan de schermafdrukken van het moment waarop het misging.

Stap 3 mag je overslaan als je haast hebt. De poort in CI is de echte; de lokale is om niet te
hoeven wachten op een fout die je in tien seconden zelf had gezien.""",
    """1. **Eerst bijtrekken: `git pull --rebase`.** De avondrun schrijft 's nachts in `index.html` en
   `versie.txt`, dus je begint bijna nooit op wat je gisteren achterliet.
2. Eén verhaal uitkiezen (zie hieronder).
3. Bouwen. `APP_VERSIE` in `index.html` en `versie.txt` allebei ophogen, altijd samen.
4. Lokaal `node tools/syntaxcheck.js index.html` en `node test/poort.js`.
5. Pushen naar `main`. De poort draait opnieuw, want lokaal groen is geen bewijs.
6. Groen: het staat live, ongeveer drie minuten na de push. Rood: er is niets gebeurd, en onder
   Actions staan de schermafdrukken van het moment waarop het misging.

Stap 4 mag je overslaan als je haast hebt. De poort in CI is de echte; de lokale is om niet te
hoeven wachten op een fout die je in tien seconden zelf had gezien.

Stap 1 niet. Die kost een seconde en hij is de enige stap die iets voorkomt wat je pas veel later
merkt. Wat er gebeurt als je hem overslaat, op 10 aug: de patch voor v23.30 zocht een zin die de
avondrun die nacht had toegevoegd, vond hem niet, deed niets, en de commit ging door met een
boodschap over werk dat niet gedaan was. Pas de push liep vast, en toen leek het een gitprobleem.

## Patchen

Veranderingen aan `index.html` gaan via een idempotent pythonscript in `claude/`, met een
`rep(anker, nieuw, n=1)` die vastloopt als het anker niet precies n keer voorkomt. Nooit los zoeken
en vervangen: dat bestand is te groot om te overzien en een halve treffer merk je niet.

Drie dingen die zo'n script moet doen, alle drie geleerd op 10 aug:

- **Twee keer draaien mag niets stukmaken.** Vandaar de idempotentiecheck bovenaan.
- **"Al gedaan" en "hier valt niets te doen" zijn niet hetzelfde.** Het eerste is een
  geruststelling, het tweede is een fout. Een script dat in beide gevallen "niets te doen" zegt,
  laat je doorlopen met een verkeerd beeld. Kijk of het bestand is wat je denkt dat het is, en stop
  met een uitleg als dat niet zo is.
- **Schrijft een script in meer dan één bestand, dan hoort de check per bestand.** Anders slaat hij
  het tweede stilletjes over omdat het eerste al klaar was.

Een handpatch moet ook zelf aan `versie.txt` denken. `pasToe()` in `tools/content-lib.js` doet dat
wel, een script in `claude/` niet, en dan wacht de servicewerker op een versie die nooit komt.

Een `id` uit een melding opzoeken zonder in twee megabyte te gaan zoeken: `node tools/zin.js s154`.
Werkt op zinnen, woorden en toetsjes.""")

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("DEPLOY.md bijgewerkt:", PAD)
