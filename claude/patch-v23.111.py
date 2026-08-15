#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.111: het plafond. Meerkeuze opent een deur, maar zet nooit een vorm op geleerd.

## Waar dit vandaan komt

Uit het ontwerpadvies, regel R2: procedurele kennis is skill-specifiek en draagt slecht over
tussen herkennen en produceren. En uit de meta-analyses: expliciete toetsen bevoordelen expliciete
instructie. Meet je met meerkeuze, dan meet je je eigen optimisme.

In de Conjugador betekent "geleerd" precies één ding: de fase opent. Acht van je laatste tien goed
en de volgende fase gaat van het slot. Tot nu toe telde een aangeklikt antwoord daar even zwaar
als een getypt antwoord, terwijl de code zelf al wist dat dat niet klopt: bij XP staat sinds v19.44
letterlijk "makkelijk (meerkeuze) telt als lichter bewijs dan zelf typen, dus minder XP". Dat
inzicht zat in de puntentelling en niet in de ladder, en de ladder is het enige wat er echt toe
doet.

Het gevolg was dat je omhoog kon klimmen door te herkennen, om vervolgens boven aan de ladder te
ontdekken dat je de vormen niet kunt maken. Dat is precies wat Stefan beschreef.

## Wat er verandert

Eén ding: **alleen getypte antwoorden vullen de meter naar de volgende fase.**

Een aangeklikt antwoord doet verder alles wat het deed. Je krijgt je feedback, je XP, je streak,
je tapa, en een fout gaat gewoon het foutenboek in zodat de herhaling hem terugbrengt. Alleen de
ontgrendeling telt hem niet mee.

En het staat op het scherm, want een stille regel is een valstrik: onder de meter komt te staan
dat aangeklikte antwoorden niet meetellen, precies op het moment dat je in meerkeuze staat.

## Waarom dit de ladder niet vastzet

De modus is adaptief: cjAdaptiefModus geeft meerkeuze alleen voor opgaven waar je eerder een fout
op maakte, en typen voor de rest. Voor een fase die je nog niet kent is dus verreweg het meeste
typen. Wie de modus met de hand op "makkelijk" zet kiest bewust voor oefenen zonder klimmen, en
dat is een geldige keuze; hij ziet nu alleen dat hij die maakt.

## Waarom dit een eigen ronde is

Het had samen met v23.110 gekund, maar dan zou een verandering in je scores niet toe te wijzen
zijn aan de afleiders of aan het plafond. Elke bouwronde is een close replication: één variabele,
de rest gelijk.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.111"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.111" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = huidig_ver != NIEUW and (DOE_APP or _num(huidig_ver) < _num(NIEUW))

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# --------------------------------------------------- 1. het plafond zelf
A_LOG = u'''  conjLog(goedBeantwoord);
  var nieuweFase = conjProbeerOntgrendelen();'''
N_LOG = u'''  /* v23.111: het plafond. Een aangeklikt antwoord telt niet mee voor de ontgrendeling.

     "Geleerd" betekent in de Conjugador precies \\u00e9\\u00e9n ding: de volgende fase gaat open bij acht van
     je laatste tien goed. Herkennen en produceren zijn verschillende vaardigheden die slecht naar
     elkaar overdragen, dus klimmen op herkenning levert een ladder op waarvan de bovenste sport
     niets waard is. De code wist dit al bij de XP hierboven ("meerkeuze telt als lichter bewijs")
     maar niet bij de ladder, en de ladder is het enige wat er echt toe doet.

     Alles behalve de ontgrendeling gaat gewoon door: feedback, XP, streak, tapa, en een fout gaat
     het foutenboek in zodat de herhaling hem terugbrengt. */
  var teltVoorLadder = modus !== "makkelijk";
  if(teltVoorLadder) conjLog(goedBeantwoord);
  var nieuweFase = teltVoorLadder ? conjProbeerOntgrendelen() : null;'''
rep(A_LOG, N_LOG)

# ------------------------------------------- 2. en het staat op het scherm
A_METER = u'''         "<p class='muted' id='cjFaseDoel' style='margin:0 0 6px; font-size:0.8rem'>"+
           ct(CONJ_ONTGRENDEL_GOED+" van je laatste "+CONJ_ONTGRENDEL_N+" goed opent de volgende fase ("+vol+"/"+CONJ_ONTGRENDEL_GOED+")",
              CONJ_ONTGRENDEL_GOED+" out of your last "+CONJ_ONTGRENDEL_N+" correct opens the next phase ("+vol+"/"+CONJ_ONTGRENDEL_GOED+")")+
         "</p>";'''
N_METER = u'''         "<p class='muted' id='cjFaseDoel' style='margin:0 0 6px; font-size:0.8rem'>"+
           ct(CONJ_ONTGRENDEL_GOED+" van je laatste "+CONJ_ONTGRENDEL_N+" goed opent de volgende fase ("+vol+"/"+CONJ_ONTGRENDEL_GOED+")",
              CONJ_ONTGRENDEL_GOED+" out of your last "+CONJ_ONTGRENDEL_N+" correct opens the next phase ("+vol+"/"+CONJ_ONTGRENDEL_GOED+")")+
         "</p>"+
         /* v23.111: een stille regel is een valstrik. Deze zin verschijnt alleen als je op dit
            moment in meerkeuze staat, want dan is hij van toepassing. */
         (conjModusNu() === "makkelijk"
           ? "<p class='muted' id='cjFaseTypen' style='margin:0 0 6px; font-size:0.78rem'>"+
               ct("Aangeklikte antwoorden tellen niet mee voor de volgende fase. Typen wel.",
                  "Answers you click do not count towards the next phase. Typed answers do.")+
             "</p>"
           : "");'''
rep(A_METER, N_METER)

# De fasekaart weet niet welke opgave er staat, dus hij kan cjHuidigeModus niet aanroepen zonder
# een werkwoord. Deze functie beantwoordt de vraag "sta ik nu in meerkeuze" uit de staat die er
# w\u00e9l is, en gebruikt dezelfde volgorde als cjHuidigeModus zodat de twee niet uit elkaar lopen.
A_MODUSNU = u'''function cjHuidigeModus(v, p, t){'''
N_MODUSNU = u'''/* v23.111: "sta ik nu in meerkeuze?" voor schermdelen die geen opgave bij de hand hebben (de
   fasekaart). Zelfde volgorde als cjHuidigeModus hieronder, met de opgave als die er is, zodat de
   twee niet uit elkaar kunnen lopen. */
function conjModusNu(){
  if(S.modusKeuze && S.modusKeuze.conj) return S.modusKeuze.conj;
  if(cjModusOverride) return cjModusOverride;
  var c = conjIdx;
  if(c && c.verb) return cjAdaptiefModus(c.verb, c.p, c.t || "presente");
  return "moeilijk";
}
function cjHuidigeModus(v, p, t){'''
rep(A_MODUSNU, N_MODUSNU)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
