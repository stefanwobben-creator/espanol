# patch-toetsprompt.py - twee eisen erbij die de nacht van 1 november had moeten tegenhouden.
#
# WAT ER GEBEURDE
#
# Het toetsje van de nieuwe les van 1 november (q-b1-16) had acht vragen, waarvan er vier niet
# deugden. De poort ving er drie, bij het nalezen vond ik er nog drie:
#
#   drie vragen met TWEE gaten in een zin en een optie als "hay / hay". De app vult een keuze in
#   een gat; de tweede ___ blijft gewoon staan. (pw-gatentelling zag deze.)
#
#   "___ alquilar un piso" met de opties "Me cuesta", "Me cuesta mucho" en "Me cuesta un poco".
#   Alle drie correct Spaans, dus er is niets te kiezen. Idem bij "___ ir al supermercado" met
#   Prefiero, Quiero en Necesito.
#
#   "___ de menos la tranquilidad" met Echo, Extraño en Pienso, en de sleutel op Extraño. Echar de
#   menos is de vaste uitdrukking; extrañar betekent ook missen maar dan zonder "de menos". Het
#   goede antwoord stond er dus wel en werd fout gerekend, en de uitleg legde de fout nog eens uit.
#
# De eisenlijst in de prompt noemt al dat opties onderling moeten verschillen en niet alleen in een
# accent. Die twee regels staan er omdat ze eerder zijn misgegaan. Deze twee komen erbij om dezelfde
# reden. Van de derde fout (de sleutel wijst de verkeerde optie aan) is de tegenlezer de aangewezen
# vanger, en die heeft dit toetsje goedgekeurd; dat is een apart probleem en geen promptregel.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/tools/curriculum.js")
s = io.open(P, encoding="utf-8").read()

if "precies EEN gat" in s:
    print("al gepatcht")
    sys.exit(0)

ANKER = """- Opties mogen ook niet alleen in een ACCENT verschillen (ibamos tegenover íbamos). Die vraag wordt
  weggegooid: de app rekent een antwoord zonder accent overal goed, dus zo'n vraag toetst een regel
  die de app zelf niet hanteert. Laat de opties in verschillende woorden of vormen verschillen."""

NIEUW = ANKER + """
- Elke vraag heeft precies EEN gat (___). De app vult de gekozen optie in dat ene gat; staat er een
  tweede ___ in de zin, dan blijft die gewoon staan en is de vraag onleesbaar. Een optie met een
  schuine streep erin ("hay / hay") is dus altijd fout: splits zo'n vraag of laat de tweede helft weg.
- ELKE AFLEIDER MOET ECHT FOUT ZIJN op de plek van het gat. Niet ongebruikelijker, niet minder mooi:
  fout. "Me cuesta" tegenover "Me cuesta mucho" is geen vraag, want allebei kan. Toets een vorm die
  mis kan gaan (persoon, getal, tijd, geslacht, ser tegenover estar), niet een woordkeuze waar de
  leerling net zo goed gelijk kan hebben als jij."""

assert s.count(ANKER) == 1, s.count(ANKER)
io.open(P, "w", encoding="utf-8").write(s.replace(ANKER, NIEUW))
print("gepatcht:", P)
