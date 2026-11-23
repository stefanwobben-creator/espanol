# Nachtwacht 23 nov 2026

Status: **openstaand** (niet live). Patch: `claude/nachtpatch-2026-11-23.py`.

## Verwerkt
Foutendiff 7b57b29 -> 5a45685 (Stefan-dagdoel 21 nov 21:00). Gegroeid en nog nergens in een oefenzin gedrild:
- la sábana (cv1171) 2 -> 5
- la lejía (cv1169) 2 -> 5
- el colchón (cv1166) 2 -> 4

Drie zinnen bij a2-4 "Mi casa, tu casa", tag les4, batch a2 +1. Ids kiest het script bij toepassen
(hoogste s-id in bestand en in curriculum-laatste.json + 1; op de huidige main worden dat s582-s584).
Idempotent op de Spaanse zin. Proef, patch (2x, tweede keer "stond er al"), keuring, syntaxcheck en
poort (174/174 groen) gedraaid op main 723e364.

## Gezien, niet gedrild
- herramienta en overige cv-woorden: +1.
- w414-w423 en q-b1-19#3: eerste kennismaking met B1-relatieles.
- gram: alleen goed-tellingen omhoog.

## Afwijking avondrun (22 nov, d449db0)
curriculum-laatste.json belooft reparatiezinnen s562-s569, s572, s573 en toetsje q-imperativo-extra7
(costar, les2). De mp3's staan in audio/dictado, maar de zinnen en het toetsje staan NIET in index.html.
Nieuwe les b1-25 staat er wel, maar s574-s579 en s581 hebben geen dictado-mp3. Costar/les2 dus niet
dubbel gedrild.

## Waarom niet live
- OPENSTAAND.md en INBOX.md zijn projectdocs; deze sessie kan ze niet lezen of schrijven. Daarom geen
  zekerheid over ids in de wachtrij, en dus niet naar main gepusht.
- `np.volgendeVrij` en `tools/ids.json` uit de instructies bestaan niet in de repo.
- Nieuwe zinnen hebben nog geen dictado-mp3 (browser-TTS vangt op tot tools/generate-audio.js draait).
