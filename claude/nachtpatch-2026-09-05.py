#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nachtpatch 5 sep - acht drillzinnen op de verse fouten van 3 en 4 september.

WAT HIER IN ZIT

Alle clusters komen uit de diff van de cumulatieve foutenmap tussen de
logsnapshot van 3 sep (03ffc24) en die van 4 sep (1c486ac) — dus alleen
fouten die NA de basis van de vorige nachtrun zijn gegroeid. Niet opnieuw
gedrild: beca/matrícula/asignatura/apuntes/carpeta, andén/vía/retraso/
carril/atasco, adjuntar/buzón, despedir/cobrar/contratar — die zitten al in
de wachtrij-patch van 4 sep (s297-s304), die nog niet live is; hun verdere
groei deze week is daarmee gedekt.

  s305  stoffen bij het winkelen: algodón (0→5), lana, seda, liso (0→3)
  s306  materialen in huis: acero (0→6, grootste nieuwe kaartje), hierro,
        vidrio
  s307  huis-werkwoorden: encender (0→4), apagar (0→3), colgar (0→2)
  s308  doler (w203, +5 naar 6): le duelen + lidwoord bij lichaamsdelen
  s309  werk en maatschappij: la huelga (0→5), el sindicato (0→2)
  s310  atender (0→4), de valse vriend: bedienen, niet bijwonen
  s311  natuur: la selva (0→3), el ave (+2, el-maar-vrouwelijk zoals agua),
        el granizo (0→2)
  s312  mientras + imperfecto tegen indefinido: vier verse missers op
        q-relatar-extra2 plus een imperfecto-misser in de Conjugador

IDS: s284-s296 zijn NIET vrij (avondrun-draft + PR #4) en s297-s304 zijn
van de wachtrij-patch van 4 sep. Daarom begint deze patch bij s305.

Geen A0: Elise had nul gegroeide clusters (laatste data 1 sep, ongewijzigd),
van Ilona en Martina kwam niets binnen.

Het versienummer wordt hier niet aangeraakt. Een nachtpatch levert inhoud;
het nummer hoort bij de aflevering.

    python3 claude/nachtpatch-2026-09-05.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import nachtpatch as np

PAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")

# ---------------------------------------------------------------------------
# A2, uit Stefans fouten van 3 en 4 september
# ---------------------------------------------------------------------------
A2 = [
 ("a2-3", '{"id": "s305", "lvl": 2, "nl": "Ik zoek een effen overhemd van katoen; dat van wol kriebelt te veel.", "en": "I am looking for a plain cotton shirt; the wool one itches too much.", "es": "Busco una camisa lisa de algodón; la de lana pica demasiado.", "alt": ["busco una camisa lisa de algodón la de lana pica demasiado", "busco una camisa lisa de algodon la de lana pica demasiado", "busco una camisa lisa de algodón; la de lana pica demasiado"], "uitleg": "Stoffen bleven deze week haken: el algodón = katoen (vijf verse missers), la lana = wol, en daarnaast miste je la seda (zijde) en el lino (linnen). Het materiaal hangt er met de aan vast: de algodón, de lana. Liso = effen of glad (drie missers) — over haar gezegd betekent het steil: pelo liso. En la de lana = die van wol: het lidwoord vervangt het zelfstandig naamwoord dat je al noemde.", "ue": "Fabrics kept slipping this week: el algodón = cotton (five fresh misses), la lana = wool, and you also missed la seda (silk) and el lino (linen). The material attaches with de: de algodón, de lana. Liso = plain or smooth (three misses) — said of hair it means straight: pelo liso. And la de lana = the wool one: the article replaces the noun you already mentioned.", "tag": "ropa"}'),
 ("a2-4", '{"id": "s306", "lvl": 2, "nl": "De nieuwe trap is van staal, de oude pan is van ijzer en de tafel is van glas.", "en": "The new staircase is made of steel, the old pan is made of iron and the table is made of glass.", "es": "La escalera nueva es de acero, la sartén vieja es de hierro y la mesa es de vidrio.", "alt": ["la escalera nueva es de acero la sartén vieja es de hierro y la mesa es de vidrio", "la escalera nueva es de acero la sarten vieja es de hierro y la mesa es de vidrio"], "uitleg": "El acero = staal, zes verse missers en daarmee je grootste nieuwe kaartje. El hierro = ijzer (het ruwe metaal; acero is het bewerkte spul) en el vidrio = glas als materiaal — het glas waar je uit drinkt is un vaso, en una copa is er een op een voet. Ser de + materiaal = ergens van gemaakt zijn: es de acero. Ser, niet estar: waar iets van gemaakt is verandert niet.", "ue": "El acero = steel, six fresh misses and thus your biggest new card. El hierro = iron (the raw metal; acero is the refined stuff) and el vidrio = glass as a material — the glass you drink from is un vaso, and una copa is one on a stem. Ser de + material = to be made of something: es de acero. Ser, not estar: what something is made of does not change.", "tag": "les4"}'),
 ("a2-4", '{"id": "s307", "lvl": 2, "nl": "Als ik thuiskom, doe ik het licht aan, hang ik mijn jas op en zet ik mijn telefoon uit.", "en": "When I get home, I turn on the light, hang up my coat and turn off my phone.", "es": "Cuando llego a casa, enciendo la luz, cuelgo el abrigo y apago el móvil.", "alt": ["cuando llego a casa enciendo la luz cuelgo el abrigo y apago el móvil", "cuando llego a casa enciendo la luz cuelgo el abrigo y apago el movil", "cuando llego a casa, enciendo la luz, cuelgo el abrigo y apago el móvil"], "uitleg": "Drie huis-werkwoorden uit je foutenlog in één routine: encender = aanzetten, aansteken (vier verse missers, klinkerwissel e naar ie: enciendo), apagar = uitzetten, uitdoen (drie missers, gewoon regelmatig: apago), en colgar = ophangen (o naar ue: cuelgo). Colgar is ook digitaal: colgar el teléfono = ophangen, en una foto colgada en internet = online gezet. Encender en apagar zijn een vast paar — leer ze samen, net als abrir en cerrar.", "ue": "Three household verbs from your error log in one routine: encender = to switch on, to light (four fresh misses, vowel shift e to ie: enciendo), apagar = to switch off (three misses, plainly regular: apago), and colgar = to hang up (o to ue: cuelgo). Colgar is digital too: colgar el teléfono = to hang up, and una foto colgada en internet = posted online. Encender and apagar are a fixed pair — learn them together, like abrir and cerrar.", "tag": "les4"}'),
 ("a2-8", '{"id": "s308", "lvl": 2, "nl": "Mijn vader heeft pijn in zijn knieën als hij de trap oploopt.", "en": "My father\'s knees hurt when he climbs the stairs.", "es": "A mi padre le duelen las rodillas cuando sube la escalera.", "alt": ["a mi padre le duelen las rodillas cuando sube la escalera"], "uitleg": "Doler was deze week je grootste leswoord-cluster (vijf verse missers). Het werkt als gustar: het lichaamsdeel is het onderwerp, dus meervoud rodillas geeft duelen, en wie de pijn voelt krijgt le — met a mi padre ervoor om te zeggen wie dat is. En let op het lidwoord: las rodillas, niet sus rodillas. Bij lichaamsdelen gebruikt het Spaans het lidwoord, dezelfde regel als in me duele la garganta.", "ue": "Doler was your biggest lesson-word cluster this week (five fresh misses). It works like gustar: the body part is the subject, so plural rodillas gives duelen, and whoever feels the pain gets le — with a mi padre in front to say who that is. And mind the article: las rodillas, not sus rodillas. With body parts Spanish uses the article, the same rule as in me duele la garganta.", "tag": "salud"}'),
 ("a2-2", '{"id": "s309", "lvl": 2, "nl": "De vakbond organiseerde een staking omdat het bedrijf heel weinig betaalde.", "en": "The union organised a strike because the company paid very little.", "es": "El sindicato organizó una huelga porque la empresa pagaba muy poco.", "alt": ["el sindicato organizó una huelga porque la empresa pagaba muy poco", "el sindicato organizo una huelga porque la empresa pagaba muy poco"], "uitleg": "La huelga = de staking, vijf verse missers: estar en huelga = staken. El sindicato = de vakbond (twee missers) — geen syndicaat in de misdaadbetekenis, gewoon de werknemersclub. En kijk naar de twee verleden tijden naast elkaar: organizó (indefinido) is de gebeurtenis, pagaba (imperfecto) is de achtergrond die al aan de gang was. Precies de verdeling waar je in de toetsjes deze week op uitgleed.", "ue": "La huelga = the strike, five fresh misses: estar en huelga = to be on strike. El sindicato = the trade union (two misses) — not a crime syndicate, just the workers\' club. And look at the two past tenses side by side: organizó (indefinido) is the event, pagaba (imperfecto) is the background that was already going on. Exactly the split that tripped you in this week\'s quizzes.", "tag": "les2"}'),
 ("a2-7", '{"id": "s310", "lvl": 2, "nl": "De ober bediende ons heel goed en bracht meteen de tonijn.", "en": "The waiter served us very well and brought the tuna right away.", "es": "El camarero nos atendió muy bien y trajo el atún enseguida.", "alt": ["el camarero nos atendió muy bien y trajo el atún enseguida", "el camarero nos atendio muy bien y trajo el atun enseguida"], "uitleg": "Atender = bedienen, helpen (vier verse missers) — een valse vriend, want een les of vergadering bijwonen is asistir a, niet atender. In de winkel hoor je ¿le atienden? = wordt u al geholpen? Trajo komt van traer (brengen), onregelmatig in de indefinido: traje, trajiste, trajo. En el atún = de tonijn, ook uit je foutenlog, met het accent op de ú.", "ue": "Atender = to serve, to help (four fresh misses) — a false friend, because attending a class or meeting is asistir a, not atender. In a shop you hear ¿le atienden? = are you being helped? Trajo comes from traer (to bring), irregular in the indefinido: traje, trajiste, trajo. And el atún = the tuna, also from your error log, accent on the ú.", "tag": "cocina"}'),
 ("a2-6", '{"id": "s311", "lvl": 2, "nl": "In het oerwoud zagen we vogels in alle kleuren, maar opeens begon het te hagelen.", "en": "In the jungle we saw birds of every colour, but suddenly it started to hail.", "es": "En la selva vimos aves de todos los colores, pero de repente empezó a caer granizo.", "alt": ["en la selva vimos aves de todos los colores pero de repente empezó a caer granizo", "en la selva vimos aves de todos los colores pero de repente empezo a caer granizo"], "uitleg": "Drie natuurwoorden die deze week nieuw in je foutenlog kwamen: la selva = het oerwoud, el ave = de vogel (deftiger dan pájaro, zoals vogel tegenover beestje) en el granizo = de hagel. Ave is vrouwelijk maar krijgt el omdat twee a-klanken botsen — exact dezelfde regel als el agua: las aves, mucha agua. Empezó a caer granizo = het begon te hagelen: empezar a + infinitief, met de indefinido voor de plotselinge gebeurtenis.", "ue": "Three nature words that entered your error log this week: la selva = the jungle, el ave = the bird (loftier than pájaro, like fowl versus birdie) and el granizo = the hail. Ave is feminine but takes el because two a-sounds clash — exactly the same rule as el agua: las aves, mucha agua. Empezó a caer granizo = it started to hail: empezar a + infinitive, with the indefinido for the sudden event.", "tag": "viaje"}'),
 ("a2-10", '{"id": "s312", "lvl": 2, "nl": "Terwijl we op het terras aan het eten waren, gingen opeens alle lichten uit.", "en": "While we were eating on the terrace, all the lights suddenly went out.", "es": "Mientras cenábamos en la terraza, de repente se apagaron todas las luces.", "alt": ["mientras cenábamos en la terraza de repente se apagaron todas las luces", "mientras cenabamos en la terraza de repente se apagaron todas las luces", "mientras cenábamos en la terraza, de repente se apagaron todas las luces"], "uitleg": "Vier verse missers op het relatar-toetsje, allemaal met hetzelfde patroon: mientras + imperfecto voor wat aan de gang was (cenábamos, de filmrol), en de indefinido voor wat er middenin gebeurde (se apagaron, de knip). Mientras is zelf al een signaalwoord voor het imperfecto. Cenábamos: de imperfecto van -ar is -aba, met een accent op de wij-vorm (cenábamos, hablábamos) — die vorm miste je deze week ook in de Conjugador. En se apagaron: apagar uit je huisrij, hier vanzelf gebeurend met se.", "ue": "Four fresh misses on the relatar quiz, all with the same pattern: mientras + imperfecto for what was in progress (cenábamos, the film roll), and the indefinido for what happened in the middle of it (se apagaron, the snap). Mientras is itself a signal word for the imperfecto. Cenábamos: the -ar imperfecto is -aba, with an accent on the we-form (cenábamos, hablábamos) — the very form you missed in the Conjugador this week. And se apagaron: apagar from your household row, here happening by itself with se.", "tag": "relatar"}'),
]

# Geen A0 dit keer: Elise had nul gegroeide clusters en van Ilona en Martina
# kwam geen nieuwe data binnen.


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
