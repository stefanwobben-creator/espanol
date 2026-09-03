#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtpatch 3 sep - acht drillzinnen die op de plank bleven liggen.

WAT HIER IN ZIT

s278/s279 en bs83/bs84 komen uit de nachtrun van 1 september. Die kon niet
pushen (het token stond nog op de placeholder) en is blijven liggen. s280-s283
komen uit de nachtrun van 3 september, die opnieuw niet kon pushen, nu omdat de
git-proxy van de sandbox geen schrijftoegang geeft.

WAAROM DIT SCRIPT ER ANDERS UITZIET DAN ZIJN VOORGANGERS

Twee nachten stapelen was precies wat de oude patchvorm niet kon. Die haakte aan
met een tekstanker op het laatste element van de array ('"tag": "les4"}\\n];'),
en dat anker klopt na één nacht niet meer. Daarom draait alles hier door
tools/nachtpatch.py: dat haakt aan op het EINDE van de array en op de SLEUTEL in
EXTRA_CONTENT, niet op wat er toevallig het laatst staat.

Het versienummer wordt hier niet aangeraakt. Een nachtpatch levert inhoud; het
nummer hoort bij de aflevering.

    python3 claude/nachtpatch-2026-09-03.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import nachtpatch as np

PAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")

# ---------------------------------------------------------------------------
# A2, uit Stefans fouten van 31 aug tot en met 2 sep
# ---------------------------------------------------------------------------
A2 = [
 ("a2-1", '{"id": "s278", "lvl": 2, "nl": "Soms wil ik opgeven, maar ik blijf elke dag oefenen.", "en": "Sometimes I want to give up, but I keep practising every day.", "es": "A veces quiero rendirme, pero sigo practicando cada día.", "alt": ["a veces quiero rendirme pero sigo practicando cada día", "a veces quiero rendirme, pero sigo practicando cada día", "a veces quiero rendirme pero sigo practicando cada dia"], "uitleg": "Rendirse = opgeven, vijf verse missers deze week, en je kent hem uit je boek: \'tu manera de no rendirte\' (hoofdstuk 9). Na een ander werkwoord blijft het een infinitief met het pronomen eraan vast: quiero rendirme. Vervoegd wisselt de klinker e naar i: me rindo, te rindes, se rinde (net als pedir). Sigo practicando = seguir + gerundio: ik blijf oefenen.", "ue": "Rendirse = to give up, five fresh misses this week, and you know it from your book: \'tu manera de no rendirte\' (chapter 9). After another verb it stays an infinitive with the pronoun attached: quiero rendirme. Conjugated, the vowel shifts e to i: me rindo, te rindes, se rinde (just like pedir). Sigo practicando = seguir + gerundio: I keep practising.", "tag": "leren"}'),
 ("a2-10", '{"id": "s279", "lvl": 2, "nl": "Opeens verdween de kat en we zochten hem door het hele huis.", "en": "Suddenly the cat disappeared and we searched the whole house for him.", "es": "De repente, el gato desapareció y lo buscamos por toda la casa.", "alt": ["de repente el gato desapareció y lo buscamos por toda la casa", "de repente, el gato desapareció y lo buscamos por toda la casa", "de repente el gato desaparecio y lo buscamos por toda la casa"], "uitleg": "Desaparecer = verdwijnen, vijf verse missers als kaartje deze week (aparecer = verschijnen, met des- ervoor). In een anekdote staat de plotse gebeurtenis in de indefinido: desapareció, met de repente als signaalwoord, en dat zat deze week ook in je foutenlog. En lo buscamos: el gato is mannelijk, dus lo, en het pronomen staat vóór het vervoegde werkwoord.", "ue": "Desaparecer = to disappear, five fresh misses as a card this week (aparecer = to appear, with des- in front). In an anecdote the sudden event takes the indefinido: desapareció, with de repente as its signal word, also in your error log this week. And lo buscamos: el gato is masculine, so lo, and the pronoun goes before the conjugated verb.", "tag": "relatar"}'),
 ("a2-4", '{"id": "s280", "lvl": 2, "nl": "Na het afwassen geef ik de planten water en ruim ik de boodschappenmand op.", "en": "After doing the dishes I water the plants and put away the shopping basket.", "es": "Después de fregar los platos, riego las plantas y guardo la cesta de la compra.", "alt": ["después de fregar los platos riego las plantas y guardo la cesta de la compra", "despues de fregar los platos riego las plantas y guardo la cesta de la compra", "después de fregar los platos, riego las plantas y guardo la cesta de la compra"], "uitleg": "Drie huisgenoten uit je foutenlog van deze week in één zin: fregar = afwassen of schrobben, regar = water geven en la cesta = de mand (la cesta de la compra = de boodschappenmand). Fregar en regar wisselen allebei e naar ie zodra de klemtoon erop valt: friego, riego. Hier blijft fregar heel, want na después de staat altijd een infinitief. En guardo = ik berg op (guardar), die miste je deze week ook weer.", "ue": "Three housemates from this week\'s error log in one sentence: fregar = to do the dishes or scrub, regar = to water and la cesta = the basket (la cesta de la compra = the shopping basket). Fregar and regar both shift e to ie when stressed: friego, riego. Here fregar stays an infinitive, because después de always takes one. And guardo = I put away (guardar), which you missed again this week too.", "tag": "les4"}'),
 ("a2-1", '{"id": "s281", "lvl": 2, "nl": "Ik maak me geen zorgen: een twijfel is geen bedreiging, maar een kans om te leren.", "en": "I don\'t worry: a doubt is not a threat, but a chance to learn.", "es": "No me preocupo: una duda no es una amenaza, sino una oportunidad para aprender.", "alt": ["no me preocupo una duda no es una amenaza sino una oportunidad para aprender", "no me preocupo: una duda no es una amenaza, sino una oportunidad para aprender", "no me preocupo, una duda no es una amenaza, sino una oportunidad para aprender"], "uitleg": "Twee verse missers in één zin: la duda = de twijfel (blijft plakken sinds vorige week) en la amenaza = de bedreiging, zeven missers als nieuw kaartje. En de opening repareert je zinfout van deze week: \'a veces me preocupar\'. Preocuparse moet vervoegd worden: me preocupo, te preocupas. Sino in plaats van pero, omdat er een ontkenning vóór staat: no es X, sino Y = niet X, maar juist Y.", "ue": "Two fresh misses in one sentence: la duda = the doubt (sticking since last week) and la amenaza = the threat, seven misses as a new card. And the opening repairs this week\'s sentence error: \'a veces me preocupar\'. Preocuparse must be conjugated: me preocupo, te preocupas. Sino instead of pero, because a negation precedes it: no es X, sino Y = not X, but rather Y.", "tag": "leren"}'),
 ("a2-8", '{"id": "s282", "lvl": 2, "nl": "Mijn enkel doet pijn, maar volgens de dokter is het bot niet gebroken.", "en": "My ankle hurts, but according to the doctor the bone is not broken.", "es": "Me duele el tobillo, pero según el médico el hueso no está roto.", "alt": ["me duele el tobillo pero según el médico el hueso no está roto", "me duele el tobillo pero segun el medico el hueso no esta roto", "me duele el tobillo, pero según el médico el hueso no está roto"], "uitleg": "El hueso = het bot en el tobillo = de enkel: allebei deze week gemist als kaartje. En de opening repareert je zinfout \'me duele mi cabeza\'. Bij lichaamsdelen gebruikt het Spaans het lidwoord en niet het bezittelijk voornaamwoord: me duele el tobillo, want het me zegt al van wie hij is. No está roto: estar bij een toestand, met roto als onregelmatig participio van romper, die zag je al in je schoenen-zin (estos zapatos están rotos).", "ue": "El hueso = the bone and el tobillo = the ankle: both missed as cards this week. And the opening repairs your sentence error \'me duele mi cabeza\'. With body parts Spanish uses the article, not the possessive: me duele el tobillo, because the me already says whose it is. No está roto: estar for a state, with roto as the irregular participle of romper, which you already saw in your shoes sentence (estos zapatos están rotos).", "tag": "salud"}'),
 ("a2-6", '{"id": "s283", "lvl": 2, "nl": "Vrijdag gaan we een afscheidsfeest voor mijn collega organiseren.", "en": "On Friday we are going to organise a farewell party for my colleague.", "es": "El viernes vamos a organizar una fiesta de despedida para mi compañero.", "alt": ["el viernes vamos a organizar una fiesta de despedida para mi compañero", "el viernes vamos a organizar una fiesta de despedida para mi companero", "vamos a organizar una fiesta de despedida para mi compañero el viernes"], "uitleg": "La despedida = het afscheid, vier verse missers als kaartje deze week. Hij komt van despedirse (afscheid nemen, e naar i: me despido), en una fiesta de despedida is het vaste duo: afscheidsfeest. Vamos a organizar = ir a + infinitief voor een plan, precies het gereedschap van deze les. En el viernes: bij dagen van de week gebruik je het lidwoord en geen voorzetsel, dus niet \'en viernes\'.", "ue": "La despedida = the farewell, four fresh misses as a card this week. It comes from despedirse (to say goodbye, e to i: me despido), and una fiesta de despedida is the fixed pair: farewell party. Vamos a organizar = ir a + infinitive for a plan, exactly this lesson\'s tool. And el viernes: with days of the week you use the article and no preposition, so not \'en viernes\'.", "tag": "planesocio"}'),
]

# ---------------------------------------------------------------------------
# A0, uit Ilona's schoolfouten
# ---------------------------------------------------------------------------
A0 = [
 ("a0-2", '{id:"bs83", lvl:1, nl:"De lerares schrijft de vraag op het bord.", en:"The teacher writes the question on the board.", es:"La profesora escribe la pregunta en la pizarra.", alt:["la profesora escribe la pregunta en la pizarra"],\n  uitleg:"La pizarra = het schoolbord en la pregunta = de vraag: allebei deze week gemist. Het Spaans zegt en la pizarra, letterlijk \'in het bord\', waar wij \'op\' zeggen. Escribir = schrijven, een regelmatig -ir-werkwoord: escribe = hij of zij schrijft.", ue:"La pizarra = the board and la pregunta = the question: both missed this week. Spanish says en la pizarra, literally \'in the board\', where English says \'on\'. Escribir = to write, a regular -ir verb: escribe = he or she writes.", tag:"escuela"}'),
 ("a0-2", '{id:"bs84", lvl:1, nl:"De oefening van hoofdstuk twee staat op bladzijde tien.", en:"The exercise in unit two is on page ten.", es:"El ejercicio de la unidad dos está en la página diez.", alt:["el ejercicio de la unidad dos está en la página diez","el ejercicio de la unidad dos esta en la pagina diez"],\n  uitleg:"Drie schoolwoorden uit je foutenlog in één zin: el ejercicio = de oefening, la unidad = het hoofdstuk van je lesboek, la página = de bladzijde. Waar iets staat zeg je met estar: está en la página diez. Página heeft een accent op de a, en die hoort erbij.", ue:"Three school words from your error log in one sentence: el ejercicio = the exercise, la unidad = the unit of your textbook, la página = the page. Where something is takes estar: está en la página diez. Página carries an accent on the a, and it belongs there.", tag:"escuela"}'),
]


def main():
    src = np.laad(PAD)
    was = np.ids(src, "SENTENCES") + np.ids(src, "B_SENTENCES")

    for les, tekst in A2:
        src = np.zinToevoegen(src, "SENTENCES", tekst)
        src = np.lesKoppelen(src, les, [np._idVan(tekst)])
    for les, tekst in A0:
        src = np.zinToevoegen(src, "B_SENTENCES", tekst)
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
