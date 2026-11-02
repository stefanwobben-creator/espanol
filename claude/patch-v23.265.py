# patch-v23.265.py - het toetsje van de nieuwe les van vannacht deugde niet, op vier van de acht.
#
# WAT DE POORT VOND
#
#   pw-gatentelling: "elke vraag is met één keuze te beantwoorden (3 problemen)"
#   q-b1-16 v4, v6 en v8: 2 gaten, antwoord "hay / hay" vult er 1
#
# Drie vragen hadden twee gaten in één zin en een antwoordoptie met een schuine streep erin. De app
# vult één keuze in één gat; de tweede ___ blijft gewoon staan. Daar is de poort op afgegaan, en
# terecht.
#
# WAT DE POORT NIET VOND, EN IK WEL
#
# Bij het nalezen bleken er nog drie mis in hetzelfde toetsje:
#
#   v2  "___ de menos la tranquilidad" met opties Echo / Extraño / Pienso, en c=1 (Extraño).
#       Dat is fout. Echar de menos is de vaste uitdrukking; extrañar betekent ook missen maar
#       dan zonder "de menos". Het juiste antwoord staat er wel, maar de sleutel wijst de
#       verkeerde aan, en de uitleg legt de fout ook nog eens uit.
#   v5  "___ alquilar un piso" met opties "Me cuesta" / "Me cuesta mucho" / "Me cuesta un poco".
#       Alle drie zijn correct Spaans. Dat is geen vraag.
#   v7  "___ ir al supermercado" met Prefiero / Quiero / Necesito. Ook alle drie correct.
#
# Vier van de acht vragen onbruikbaar, en de tegenlezer heeft het toetsje goedgekeurd. Dat is geen
# incident maar een gat in de keuring: zie de tweede patch van vandaag voor de twee regels die er
# in de prompt bij gaan.
#
# WAT HIER GEBEURT
#
# De zes kapotte vragen worden vervangen. Niet geschrapt: het toetsje hoort bij de les van vannacht
# en met drie vragen over zou het helemaal wegvallen. De vervangingen blijven op het onderwerp van
# de les (stad tegenover platteland) en op het grammaticapunt (hay tegenover estar), en de twee
# andere krijgen afleiders die echt fout zijn in plaats van synoniemen.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "El parque ___ al lado de mi casa" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:80])
    s = s.replace(anker, nieuw)


# v2: de sleutel wees de verkeerde optie aan
rep('"opts":["Echo","Extraño","Piensa"]' if False else
    '"opts":["Echo","Extraño","Pienso"],"c":1,"u":"Extraño is het juiste werkwoord voor \'missen\' in deze context.",'
    '"ue":"Extraño is the correct verb for \'to miss\' in this context."',
    '"opts":["Echo","Extraño","Pienso"],"c":0,'
    '"u":"Echar de menos is de vaste uitdrukking: echo de menos la tranquilidad. Extrañar betekent ook missen, '
    'maar dan zónder de menos: extraño la tranquilidad.",'
    '"ue":"Echar de menos is the fixed expression: echo de menos la tranquilidad. Extrañar also means to miss, '
    'but without de menos: extraño la tranquilidad."')

# v4: twee gaten -> een vraag over hay tegenover estar
rep('{"q":"En la ciudad ___ más ruido, pero ___ más oferta cultural.",'
    '"nl":"In de stad is er meer lawaai, maar er is meer aanbod aan cultuur.",'
    '"ne":"In the city there is more noise, but there is more cultural offer.",'
    '"opts":["hay / hay","hace / hace","está / está"],"c":0,'
    '"u":"Hay beschrijft hoeveelheden (ruido / oferta cultural) die aanwezig zijn.",'
    '"ue":"Hay describes amounts (ruido / oferta cultural) that are present."}',
    '{"q":"El parque ___ al lado de mi casa.",'
    '"nl":"Het park ligt naast mijn huis.",'
    '"ne":"The park is next to my house.",'
    '"opts":["está","hay","es"],"c":0,'
    '"u":"De plaats van iets bepaalds geef je met estar: el parque está. Hay gebruik je alleen om iets te '
    'introduceren dat je nog niet genoemd hebt: hay un parque cerca.",'
    '"ue":"The location of something specific takes estar: el parque está. Hay only introduces something you '
    'have not mentioned yet: hay un parque cerca."}')

# v5: drie goede antwoorden -> afleiders die echt fout zijn
rep('"opts":["Me cuesta","Me cuesta mucho","Me cuesta un poco"],"c":0,'
    '"u":"Me cuesta beschrijft een activiteit (alquilar) die moeilijk is.",'
    '"ue":"Me cuesta describes an activity (alquilar) that is difficult."',
    '"opts":["Me cuesta","Me cuestan","Me cuestas"],"c":0,'
    '"u":"Bij costar is het onderwerp de activiteit (alquilar), en dat is er één, dus cuesta. Me cuestan '
    'hoort bij een meervoudig onderwerp: me cuestan los verbos.",'
    '"ue":"With costar the subject is the activity (alquilar), and that is one thing, so cuesta. Me cuestan goes '
    'with a plural subject: me cuestan los verbos."')

# v6: twee gaten -> hay in het meervoud
rep('{"q":"En el campo ___ más tranquilidad, pero ___ menos trabajo.",'
    '"nl":"Op het platteland is er meer rust, maar er zijn minder banen.",'
    '"ne":"In the countryside there is more peace, but there are fewer jobs.",'
    '"opts":["hay / hay","hace / hace","está / está"],"c":0,'
    '"u":"Hay beschrijft hoeveelheden (tranquilidad / trabajos) die aanwezig zijn.",'
    '"ue":"Hay describes amounts (tranquilidad / trabajos) that are present."}',
    '{"q":"En mi barrio ___ dos supermercados.",'
    '"nl":"In mijn wijk zijn er twee supermarkten.",'
    '"ne":"There are two supermarkets in my neighbourhood.",'
    '"opts":["hay","están","son"],"c":0,'
    '"u":"Hay blijft hay, ook bij een meervoud: hay dos supermercados. Están komt pas in beeld als allebei de '
    'supermarkten al bekend zijn: los supermercados están cerrados.",'
    '"ue":"Hay stays hay, also with a plural: hay dos supermercados. Están only comes in once both supermarkets '
    'are already known: los supermercados están cerrados."}')

# v7: drie goede antwoorden -> de persoonsuitgang
rep('"opts":["Prefiero","Quiero","Necesito"],"c":0,'
    '"u":"Prefiero beschrijft een voorkeur voor een activiteit (ir).",'
    '"ue":"Prefiero describes a preference for an activity (ir)."',
    '"opts":["Prefiero","Prefiere","Preferimos"],"c":0,'
    '"u":"Preferir wisselt de klinker mee: prefiero (ik), prefieres (jij), prefiere (hij of zij). Bij preferimos '
    '(wij) blijft de e staan, en hier gaat het over jezelf.",'
    '"ue":"Preferir is a stem-changing verb: prefiero (I), prefieres (you), prefiere (he or she). In preferimos '
    '(we) the e stays, and here it is about yourself."')

# v8: twee gaten -> waar staat iets
rep('{"q":"En la ciudad ___ más tráfico, pero ___ más opciones para salir.",'
    '"nl":"In de stad is er meer verkeer, maar er zijn meer opties om uit te gaan.",'
    '"ne":"In the city there is more traffic, but there are more options to go out.",'
    '"opts":["hay / hay","hace / hace","está / está"],"c":0,'
    '"u":"Hay beschrijft hoeveelheden (tráfico / opciones) die aanwezig zijn.",'
    '"ue":"Hay describes amounts (tráfico / opciones) that are present."}',
    '{"q":"¿Dónde ___ la estación de tren?",'
    '"nl":"Waar is het treinstation?",'
    '"ne":"Where is the train station?",'
    '"opts":["está","hay","es"],"c":0,'
    '"u":"Je vraagt naar de plaats van één bepaald station, dus estar. ¿Dónde hay una '
    'estación? vraagt naar welk station dan ook; ¿dónde está la estación? naar dat ene.",'
    '"ue":"You are asking for the location of one specific station, so estar. ¿Dónde hay una '
    'estación? asks for any station at all; ¿dónde está la estación? asks for that one."}')

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
