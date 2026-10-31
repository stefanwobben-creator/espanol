# patch-v23.258.py - kaart 32 krijgt zijn twee lessen, en de poort gaat open.
#
# WAT ER AAN DE HAND WAS
#
# De poort staat rood op main sinds 11 oktober, deel 4 van 4, en daardoor is er sinds v23.254
# (13 september) niets meer live gegaan. De logs van een Actions-run zijn alleen leesbaar als je
# bent ingelogd, dus de reden was van buitenaf niet te zien. Sinds de poort zijn rode suites als
# annotatie neerzet, is hij dat wel:
#
#   ::error title=pw-lesgat.js:: het aantal onverklaarde kaarten loopt niet op (1 van maximaal 0)
#   kaart 32 "De regel van 'costar' en vervoegingen van 'soler'" (7 vragen)
#
# Precies wat v23.254 voorspelde. Uit de kop van dat concept, toen kaart 31 werd aangehecht:
# "Zolang die weg niet keurt, komt kaart 32 er ook aan."
#
# De kaart kwam in de nacht mee met een nieuwe les: een spiekbriefkaart en een toetsje van zeven
# vragen, zonder grammaticaconcept dat de stof uitlegt. pw-lesgat telt dat en staat op nul.
#
# WAAROM TWEE CONCEPTEN EN NIET EEN
#
# De kaart gaat over twee dingen tegelijk, en dat is ook de reden dat hij nergens paste:
#
#   costar met een activiteit als onderwerp  ->  dat is de gustar-familie, letterlijk hetzelfde
#                                                patroon als me gustan. Hoort bij gustarfamilie.
#   de vervoeging van soler (o wordt ue)     ->  dat is een schoenwerkwoord. Hoort bij zapato.
#
# Hem alleen aan gustarfamilie hangen zou zeggen dat dat concept ook soler uitlegt, en dat doet het
# niet. Twee concepten die allebei een helft claimen is geen dubbeling maar de waarheid.
#
# WAT HIERMEE NIET IS OPGELOST
#
# Dit is de vierde keer in zeven weken dat een weeskaart met de hand wordt aangehecht (30 in
# v23.251, 30 nog eens, 31 in v23.254, 32 nu). De oorzaak ligt bij de nachtrun: een nieuwe les gaat
# via een pull request en brengt zijn spiekbriefkaart mee, en die kaart belandt op main zonder dat
# er ooit een concept bij gemaakt wordt. Zolang die weg niet keurt, komt kaart 33 er ook aan.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "spiek:{a2:[18,23,30,31,32]}" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


OUD_G = "  corr:[], spiek:{a2:[18,23,30,31]}, wizard:null,"
NIEUW_G = """  /* v23.258: en kaart 32, "De regel van 'costar' en vervoegingen van 'soler'". Voorspeld in de
     regel hierboven en inderdaad gekomen: zeven toetsvragen, geen concept. Alleen de costar-helft
     hoort hier; de vervoeging van soler is een schoenwerkwoord en staat bij zapato. */
  corr:[], spiek:{a2:[18,23,30,31,32]}, wizard:null,"""
rep(OUD_G, NIEUW_G)

OUD_Z = """  corr:[], spiek:{a2:[3]}, wizard:null,"""
NIEUW_Z = """  /* v23.258: kaart 32 erbij voor de helft die hier hoort. Die kaart heet "De regel van 'costar'
     en vervoegingen van 'soler'", en soler is een o-wordt-ue werkwoord: suelo, sueles, suele,
     solemos, soleis, suelen. Dat is dit concept en niet de gustar-familie, die de andere helft
     van dezelfde kaart claimt. */
  corr:[], spiek:{a2:[3,32]}, wizard:null,"""
rep(OUD_Z, NIEUW_Z)

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
