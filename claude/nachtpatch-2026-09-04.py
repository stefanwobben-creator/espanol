#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtpatch 4 sep - acht drillzinnen op de verse fouten van 2 september.

WAT HIER IN ZIT

Alle clusters komen uit de diff van de cumulatieve foutenmap tussen de
logsnapshot van 2 sep (43bed94) en die van 3 sep (03ffc24) — dus alleen
fouten die NA de vorige nachtrun zijn gegroeid. Niet opnieuw gedrild:
regar/fregar/cesta/rendirse/amenaza/hueso/tobillo/despedida — die zitten al
in de wachtrij-patch van 3 sep (s278-s283), die nog niet live is.

  s297/s298  school: beca (0→8, grootste nieuwe kaartje), matrícula,
             asignatura, apuntes, carpeta
  s299/s300  onderweg: andén (+6), vía, retraso, tranvía / carril (0→7),
             atasco (+4)
  s301       mail: adjuntar (0→5), buzón (+4)
  s302       werk: despedir, cobrar, contratar (indefinido, les 2)
  s303       reparatie van "que divertido esta el concierto" → fue (s61)
  s304       reparatie van "toma mucho agua" → mucha agua (s80)

IDS: s284-s296 zijn NIET vrij, ook al staan ze niet op main: de avondrun
reserveerde s289-s296 en de curriculum-Action (PR #4, 3 sep) gebruikt
s278-s296. Daarom begint deze patch bij s297.

Het versienummer wordt hier niet aangeraakt. Een nachtpatch levert inhoud;
het nummer hoort bij de aflevering.

    python3 claude/nachtpatch-2026-09-04.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import nachtpatch as np

PAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")

# ---------------------------------------------------------------------------
# A2, uit Stefans fouten van 2 september
# ---------------------------------------------------------------------------
A2 = [
 ("a2-1", '{"id": "s297", "lvl": 2, "nl": "Ik vraag een studiebeurs aan, want ik kan het inschrijfgeld van de cursus niet betalen.", "en": "I am applying for a scholarship, because I cannot pay the course tuition fee.", "es": "Pido una beca porque no puedo pagar la matrícula del curso.", "alt": ["pido una beca porque no puedo pagar la matrícula del curso", "pido una beca porque no puedo pagar la matricula del curso"], "uitleg": "La beca = de studiebeurs, acht verse missers deze week en daarmee je grootste nieuwe kaartje. La matrícula = het inschrijfgeld of de inschrijving, met het accent op de í — buiten school is la matrícula ook het kentekenbord van een auto. Pido komt van pedir (e naar i: pido, pides), en no puedo pagar = poder + infinitief.", "ue": "La beca = the scholarship, eight fresh misses this week and your biggest new card. La matrícula = the tuition fee or enrolment, with the accent on the í — outside school la matrícula is also a car’s number plate. Pido comes from pedir (e to i: pido, pides), and no puedo pagar = poder + infinitive.", "tag": "escuela"}'),
 ("a2-1", '{"id": "s298", "lvl": 2, "nl": "Ik bewaar de aantekeningen van elk vak in een aparte map.", "en": "I keep the notes for each subject in a separate folder.", "es": "Guardo los apuntes de cada asignatura en una carpeta.", "alt": ["guardo los apuntes de cada asignatura en una carpeta"], "uitleg": "Drie schoolwoorden uit je foutenlog in één zin: los apuntes = de aantekeningen (vrijwel altijd meervoud, van apuntar = noteren), la asignatura = het schoolvak (valse vriend: niet de handtekening, dat is la firma), en la carpeta = de map (nog een valse vriend: geen tapijt, dat is la alfombra). Guardar = bewaren, opbergen — die miste je deze week ook weer. Na cada blijft het zelfstandig naamwoord enkelvoud: cada asignatura.", "ue": "Three school words from your error log in one sentence: los apuntes = the notes (nearly always plural, from apuntar = to note down), la asignatura = the school subject (false friend: not the signature, that is la firma), and la carpeta = the folder (another false friend: not a carpet, that is la alfombra). Guardar = to keep, to put away — you missed that one again this week. After cada the noun stays singular: cada asignatura.", "tag": "escuela"}'),
 ("a2-6", '{"id": "s299", "lvl": 2, "nl": "De trein vertrekt met vertraging: we wachten op het perron van spoor twee.", "en": "The train is leaving late: we are waiting on the platform of track two.", "es": "El tren sale con retraso: esperamos en el andén de la vía dos.", "alt": ["el tren sale con retraso esperamos en el andén de la vía dos", "el tren sale con retraso, esperamos en el andén de la vía dos", "el tren sale con retraso esperamos en el anden de la via dos"], "uitleg": "Drie stationswoorden die deze week bleven haken: el andén = het perron (zes verse missers), la vía = het spoor en el retraso = de vertraging. Con retraso = met vertraging, het vaste duo. En la vía zit verstopt in el tranvía (de tram, letterlijk over-de-weg), die je ook miste — twee kaartjes met één ezelsbrug. Let op de accenten: andén en vía.", "ue": "Three station words that kept slipping this week: el andén = the platform (six fresh misses), la vía = the track and el retraso = the delay. Con retraso = delayed, the fixed pair. And la vía hides inside el tranvía (the tram, literally along-the-way), which you also missed — two cards with one mnemonic. Mind the accents: andén and vía.", "tag": "viaje"}'),
 ("a2-6", '{"id": "s300", "lvl": 2, "nl": "Er staat een enorme file omdat de rechterrijstrook dicht is.", "en": "There is a huge traffic jam because the right lane is closed.", "es": "Hay un atasco enorme porque el carril derecho está cerrado.", "alt": ["hay un atasco enorme porque el carril derecho está cerrado", "hay un atasco enorme porque el carril derecho esta cerrado"], "uitleg": "El carril = de rijstrook, zeven verse missers en daarmee een nieuw kaartje — un carril bici is een fietspad. El atasco = de file (vier missers erbij, van atascarse = vastlopen). Hay voor er is, en está cerrado: estar + participio voor een toestand, net als in je schoenen-zin (están rotos).", "ue": "El carril = the lane, seven fresh misses and thus a new card — un carril bici is a bike lane. El atasco = the traffic jam (four more misses, from atascarse = to get stuck). Hay for there is, and está cerrado: estar + participle for a state, just like your shoes sentence (están rotos).", "tag": "viaje"}'),
 ("a2-5", '{"id": "s301", "lvl": 2, "nl": "Kun je het document nog een keer bijvoegen? Mijn postvak is bijna vol.", "en": "Can you attach the document again? My inbox is almost full.", "es": "¿Puedes adjuntar el documento otra vez? Mi buzón está casi lleno.", "alt": ["puedes adjuntar el documento otra vez mi buzón está casi lleno", "puedes adjuntar el documento otra vez mi buzon esta casi lleno", "¿puedes adjuntar el documento otra vez? mi buzón está casi lleno"], "uitleg": "Adjuntar = bijvoegen, vijf verse missers: un archivo adjunto is de bijlage van een mail. El buzón = de brievenbus én je digitale postvak (vier missers erbij). Het verzoek loopt precies zoals deze les hem leert: ¿puedes + infinitief? En casi lleno = bijna vol — lleno bleef eerder ook al plakken.", "ue": "Adjuntar = to attach, five fresh misses: un archivo adjunto is an email attachment. El buzón = the letterbox and your digital inbox (four more misses). The request runs exactly as this lesson teaches it: ¿puedes + infinitive? And casi lleno = almost full — lleno kept sticking before as well.", "tag": "les5"}'),
 ("a2-2", '{"id": "s302", "lvl": 2, "nl": "Het bedrijf ontsloeg me in maart, maar gelukkig kreeg ik mijn laatste loon nog.", "en": "The company fired me in March, but luckily I still received my last salary.", "es": "La empresa me despidió en marzo, pero por suerte cobré el último sueldo.", "alt": ["la empresa me despidió en marzo pero por suerte cobré el último sueldo", "la empresa me despidio en marzo pero por suerte cobre el ultimo sueldo"], "uitleg": "Despedir = ontslaan (me despidió = ze ontsloeg mij), het spiegelbeeld van contratar = aannemen — allebei deze week gemist. Cobrar = geld ontvangen, innen: cobrar el sueldo = je loon krijgen. Niet verwarren met pagar: jij betaalt, de ander cobra. Despidió en cobré staan in de indefinido: afgeronde gebeurtenissen in een levensverhaal, het gereedschap van deze les. En despedirse (met se) = afscheid nemen: una fiesta de despedida ken je al.", "ue": "Despedir = to fire (me despidió = they fired me), the mirror image of contratar = to hire — both missed this week. Cobrar = to receive money, to collect: cobrar el sueldo = to get your wages. Don’t confuse it with pagar: you pay, the other person cobra. Despidió and cobré are in the indefinido: completed events in a life story, this lesson’s tool. And despedirse (with se) = to say goodbye: una fiesta de despedida you already know.", "tag": "les2"}'),
 ("a2-6", '{"id": "s303", "lvl": 2, "nl": "Wat was het concert van gisteravond leuk!", "en": "How fun last night’s concert was!", "es": "¡Qué divertido fue el concierto de anoche!", "alt": ["qué divertido fue el concierto de anoche", "que divertido fue el concierto de anoche"], "uitleg": "Reparatie van je eigen zin: je schreef que divertido esta el concierto. Een concert van gisteravond is afgelopen, dus verleden tijd: fue, de indefinido van ser, met anoche als signaalwoord. En het is ser, niet estar: divertido is hier een oordeel over het evenement zelf. ¡Qué + bijvoeglijk naamwoord! = wat ...!, met accent op qué — het uitroep-gereedschap van deze les.", "ue": "A repair of your own sentence: you wrote que divertido esta el concierto. Last night’s concert is over, so past tense: fue, the indefinido of ser, with anoche as its signal word. And it is ser, not estar: divertido here judges the event itself. ¡Qué + adjective! = how ...!, with an accent on qué — this lesson’s exclamation tool.", "tag": "planesocio"}'),
 ("a2-8", '{"id": "s304", "lvl": 2, "nl": "Als je keel pijn doet, rust dan uit en drink veel water.", "en": "If your throat hurts, rest and drink a lot of water.", "es": "Si te duele la garganta, descansa y bebe mucha agua.", "alt": ["si te duele la garganta descansa y bebe mucha agua", "si te duele la garganta, descansa y bebe mucha agua"], "uitleg": "Reparatie van je eigen advies: je schreef toma mucho agua. Agua is vrouwelijk, dus mucha agua. Dat het lidwoord el is (el agua) komt alleen door de klank — twee a-klanken botsen — maar het woord blijft vrouwelijk: el agua fría, mucha agua. Descansa en bebe zijn imperativo (tú), en te duele la garganta: lidwoord bij lichaamsdelen, geen bezittelijk voornaamwoord — dezelfde regel als bij me duele el tobillo.", "ue": "A repair of your own advice: you wrote toma mucho agua. Agua is feminine, so mucha agua. The article el (el agua) is only there for the sound — two a-sounds clash — but the word stays feminine: el agua fría, mucha agua. Descansa and bebe are imperativo (tú), and te duele la garganta: the article with body parts, no possessive — the same rule as me duele el tobillo.", "tag": "salud"}'),
]

# Geen A0 dit keer: Elise had nul gegroeide clusters en van Ilona kwam geen
# nieuwe data binnen.


def main():
    src = np.laad(PAD)
    was = np.ids(src, "SENTENCES") + np.ids(src, "B_SENTENCES")

    for les, tekst in A2:
        src = np.zinToevoegen(src, "SENTENCES", tekst)
        src = np.lesKoppelen(src, les, [np._idVan(tekst)])

    nu = np.ids(src, "SENTENCES") + np.ids(src, "B_SENTENCES")
    nieuw = [x for x in nu if x not in was]
    if not nieuw:
        print("stond er al, niets gedaan")
        return

    # het batchlabel loopt per spoor één keer op, en alleen als er iets bij kwam
    if any(x.startswith("s") for x in nieuw):
        src = np.batchOphogen(src, "a2")
    if any(x.startswith("bs") for x in nieuw):
        src = np.batchOphogen(src, "beginner")

    np.keuring(src)
    np.bewaar(PAD, src)
    print("toegevoegd:", ", ".join(nieuw))
    print("batch:", np.batchNu(src, "a2"), "/", np.batchNu(src, "beginner"))


if __name__ == "__main__":
    main()
