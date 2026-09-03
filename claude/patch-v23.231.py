#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.231 - twee gaten en één antwoord is geen vraag
#
# Stefan, 3 sep, met een schermafbeelding van q-relatar-extra2 vraag 1:
# "deze oefeningen blijf ik gek vinden want ik moet twee antwoorden intypen, maar kan er maar een
# kiezen."
#
# Hij heeft gelijk, en het is erger dan hij denkt.
#
#     Cuando ___ a la estación, el tren ya ___ .
#     [ llegué ]  [ llegaba ]  [ había salido ]  [ salió ]
#
# Twee gaten, vier losse vormen, en één van de vier is "goed". Hij koos llegué en kreeg rood, terwijl
# llegué het juiste antwoord is voor het eerste gat. De vraag is niet moeilijk, hij is onbeantwoordbaar.
#
# GEMETEN OVER ALLE 467 TOETSVRAGEN
#
#   31 vragen hebben twee of meer gaten
#   17 daarvan zijn in orde: het antwoord vult ze allemaal ("era, vivía", "Llovía, llegué")
#   14 zijn onbeantwoordbaar: het antwoord vult er één
#
# Alle veertien zitten in q-relatar-extra2, -extra3 en -extra5. Dat zijn precies de toetsen over
# indefinido en imperfecto.
#
# EN DAAR ZIT DE ECHTE SCHADE
#
# De nachtrun van 3 september meldde: "q-relatar-extra2 ging op 1 sep op 7 van de 8 vragen mis
# (gram-topic indefimperf 18 fout)" en concludeerde dat dit Stefans zwakste onderdeel is. Van die
# acht vragen zijn er zes onbeantwoordbaar. Zeven van de acht fout is dan geen meting van Stefan
# maar van de toets.
#
# Sterker: bij een paar staat het gemarkeerde antwoord ronduit fout, en spreekt de uitleg het tegen.
#
#   extra2 v7  "Mientras ___ en la playa, ___ un tiburón"   goed gemarkeerd: veíamos
#              De Nederlandse zin zegt "zagen we ineens", dus vimos. De uitleg zegt zelf
#              "Vimos is de gebeurtenis die de scène onderbreekt".
#   extra5 v7  "Cuando ___ (llegar) a casa, mi hermano ___" goed gemarkeerd: llegaba
#              De uitleg zegt zelf "De gebeurtenis (thuis komen) is indefinido", dus llegué.
#   extra3 v5  "Cuando ___ (tener) veinte años, ___ (viajar)" goed gemarkeerd: viajé
#              De uitleg zegt "de duur of gewoonte is ook imperfecto", dus viajaba. Twee verhalen.
#
# Een verkeerde diagnose is erger dan geen. De app stuurde hem naar extra oefening op een onderdeel
# waarvan het bewijs uit een kapotte toets kwam.
#
# WAT ER NU STAAT
#
# De veertien vragen krijgen de vorm die q-relatar-extra1, -extra4 en -extra6 al hadden: het
# antwoord is een PAAR dat allebei de gaten vult, en de drie afleiders zijn de drie andere
# combinaties. Dat is niet alleen antwoordbaar, het is ook de betere oefening: bij indefinido tegen
# imperfecto gaat het juist om de KOPPELING tussen achtergrond en onderbreking, en die kies je nu in
# één keer.
#
#     Cuando ___ a la estación, el tren ya ___ .
#     [ llegué, había salido ]  [ llegaba, salió ]  [ llegué, salió ]  [ llegaba, había salido ]
#
# Twee uitleggen die zichzelf tegenspraken zijn herschreven, en twee die eindigden op "maar hier
# gaat het om de achtergrond" (een slag om de arm bij een vraag die geen slag om de arm nodig heeft)
# ook.
#
# De regel wordt vanaf nu bewaakt door pw-gatentelling.js: het aantal gaten in een vraag is één, of
# het juiste antwoord vult ze allemaal.
import io, json, pathlib, re, sys

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.231"
sys.path.insert(0, str(W / "tools"))
import nachtpatch as np

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_VER = _num(huidig_ver) < _num(NIEUW)
# Idempotent op het antwoord uit Stefans schermafbeelding: staat dat er al als paar, dan is deze
# ronde gedraaid. De vragen worden op hun Spaanse zin gezocht, en die verandert niet, dus zonder
# deze vlag zou het script elke keer opnieuw melden dat hij veertien vragen herstelde.
AL_GEDAAN = '"llegu\u00e9, hab\u00eda salido"' in src

# ---------------------------------------------------------------------------
# de nieuwe vragen, gezocht op hun Spaanse zin (die is uniek binnen de toets)
# ---------------------------------------------------------------------------
NIEUWE = {
 "q-relatar-extra2": {
  "Cuando ___ pequeño, siempre ___ con mi abuelo en el jardín.": {
   "opts": ["era, jugaba", "fui, jugué", "era, jugué", "fui, jugaba"], "c": 0,
   "u": "Allebei imperfecto. Era beschrijft de toestand (toen ik klein was) en jugaba de gewoonte; siempre is daarvan het signaalwoord. Fui en jugué zouden er één afgeronde gebeurtenis van maken, en dan is 'altijd' onzin.",
   "ue": "Both imperfect. Era describes the state (when I was little) and jugaba the habit; siempre is the signal word for it. Fui and jugué would turn it into one completed event, which makes 'always' nonsense."},
  "De repente, alguien ___ a la puerta mientras ___ la cena.": {
   "opts": ["llamó, cenábamos", "llamaba, cenamos", "llamó, cenamos", "llamaba, cenábamos"], "c": 0,
   "u": "Twee signaalwoorden in één zin, elk bij hun eigen tijd. De repente kondigt de onderbreking aan: llamó (indefinido). Mientras kondigt de achtergrond aan: cenábamos (imperfecto).",
   "ue": "Two signal words in one sentence, each with its own tense. De repente announces the interruption: llamó (indefinite). Mientras announces the background: cenábamos (imperfect)."},
  "El otro día ___ un accidente en la calle cuando ___ al trabajo.": {
   "opts": ["hubo, iba", "había, fui", "hubo, fui", "había, iba"], "c": 0,
   "u": "Hubo (indefinido) is de gebeurtenis: er gebeurde één ongeluk, afgerond. Iba (imperfecto) is wat jij op dat moment aan het doen was. Let op de twee vormen van hay: hubo in de indefinido, había in de imperfecto.",
   "ue": "Hubo (indefinite) is the event: one accident happened, completed. Iba (imperfect) is what you were doing at that moment. Note the two forms of hay: hubo in the indefinite, había in the imperfect."},
  "Cuando ___ a la estación, el tren ya ___ .": {
   "opts": ["llegué, había salido", "llegaba, salió", "llegué, salió", "llegaba, había salido"], "c": 0,
   "u": "Llegué (indefinido) is het moment waarop je aankwam. Había salido is de pluscuamperfecto (había + participio): wat dáárvoor al gebeurd was, met ya als signaalwoord. Salió zou betekenen dat de trein vertrok op het moment dat jij aankwam.",
   "ue": "Llegué (indefinite) is the moment you arrived. Había salido is the pluperfect (había + participle): what had already happened before that, with ya as its signal word. Salió would mean the train left at the moment you arrived."},
  "Mientras ___ en la playa, ___ un tiburón en el agua.": {
   "opts": ["estábamos, vimos", "estuvimos, veíamos", "estábamos, veíamos", "estuvimos, vimos"], "c": 0,
   "u": "Mientras kondigt de achtergrond aan: estábamos (imperfecto), we lagen daar. Wat die scène onderbreekt staat in de indefinido: vimos, we zagen hem ineens. Veíamos zou betekenen dat je hem de hele tijd al zag.",
   "ue": "Mientras announces the background: estábamos (imperfect), we were lying there. What interrupts that scene takes the indefinite: vimos, we suddenly saw it. Veíamos would mean you had been seeing it the whole time."},
  "Cuando ___ niño, ___ mucho con mis amigos en el barrio.": {
   "opts": ["era, jugaba", "fui, jugué", "era, jugué", "fui, jugaba"], "c": 0,
   "u": "Dezelfde bouw als eerder in deze toets, met een andere zin: era is de toestand (toen ik een kind was), jugaba de gewoonte in die tijd. Mucho hoort bij die herhaling, net als siempre.",
   "ue": "Same construction as earlier in this quiz, with a different sentence: era is the state (when I was a child), jugaba the habit in that period. Mucho belongs to that repetition, just like siempre."},
 },
 "q-relatar-extra3": {
  "Cuando ___ (ser) niño, ___ (vivir) en un pueblo pequeño.": {
   "opts": ["era, vivía", "fui, viví", "era, viví", "fui, vivía"], "c": 0,
   "u": "Allebei imperfecto: era is de toestand (toen ik een kind was) en vivía de duur (jarenlang wonen). Fui en viví zouden er afgeronde blokken van maken, en daar gaat deze zin niet over.",
   "ue": "Both imperfect: era is the state (when I was a child) and vivía the duration (living there for years). Fui and viví would turn them into completed blocks, which is not what this sentence is about."},
  "___ (llover) mucho cuando ___ (llegar) a casa.": {
   "opts": ["Llovía, llegué", "Llovió, llegaba", "Llovía, llegaba", "Llovió, llegué"], "c": 0,
   "u": "Llovía (imperfecto) is het weer als decor: het regende al toen je aankwam. Llegué (indefinido) is het moment zelf. Cuando wijst hier dat ene moment aan.",
   "ue": "Llovía (imperfect) is the weather as scenery: it was already raining when you got there. Llegué (indefinite) is the moment itself. Cuando points at that single moment here."},
  "Mientras ___ (estudiar) para el examen, mi hermano ___ (romper) mi taza favorita.": {
   "opts": ["estudiaba, rompió", "estudié, rompía", "estudiaba, rompía", "estudié, rompió"], "c": 0,
   "u": "Mientras kondigt de achtergrond aan: estudiaba (imperfecto). Wat die scène onderbreekt staat in de indefinido: rompió, één keer, klaar.",
   "ue": "Mientras announces the background: estudiaba (imperfect). What interrupts that scene takes the indefinite: rompió, once, done."},
  "De repente, el teléfono ___ (sonar) y ___ (despertarme).": {
   "opts": ["sonó, me desperté", "sonaba, me despertaba", "sonó, me despertaba", "sonaba, me desperté"], "c": 0,
   "u": "Hier twee keer indefinido, en dat is het punt van deze vraag: de repente kondigt een plotselinge gebeurtenis aan (sonó), en wakker worden is de directe reactie daarop (me desperté). Twee afgeronde momenten na elkaar, geen achtergrond.",
   "ue": "Here it is the indefinite twice, and that is this question's point: de repente announces a sudden event (sonó), and waking up is the direct reaction to it (me desperté). Two completed moments in a row, no background."},
  "Cuando ___ (tener) veinte años, ___ (viajar) por América del Sur.": {
   "opts": ["tenía, viajé", "tuve, viajaba", "tenía, viajaba", "tuve, viajé"], "c": 0,
   "u": "Tenía (imperfecto) is je leeftijd als achtergrond: hoe oud je toen was. Viajé (indefinido) is de reis zelf, een afgerond hoofdstuk. Viajaba zou betekenen dat je er in die jaren steeds opnieuw heen ging.",
   "ue": "Tenía (imperfect) is your age as background: how old you were then. Viajé (indefinite) is the trip itself, a closed chapter. Viajaba would mean you kept going back during those years."},
  "Mientras ___ (esperar) el autobús, ___ (ver) un accidente en la calle.": {
   "opts": ["esperaba, vi", "esperé, veía", "esperaba, veía", "esperé, vi"], "c": 0,
   "u": "Mientras kondigt de achtergrond aan: esperaba (imperfecto). Wat er tijdens die scène gebeurde staat in de indefinido: vi. Esperé zou het wachten zelf tot de gebeurtenis maken, en dan valt het ongeluk buiten de zin.",
   "ue": "Mientras announces the background: esperaba (imperfect). What happened during that scene takes the indefinite: vi. Esperé would make the waiting itself the event, leaving the accident outside the sentence."},
 },
 "q-relatar-extra5": {
  "Cuando ___ (ser) niño, ___ (vivir) en un pueblo pequeño.": {
   "opts": ["era, vivía", "fui, viví", "era, viví", "fui, vivía"], "c": 0,
   "u": "Allebei imperfecto: era is de toestand (toen ik een kind was) en vivía de duur. Een jeugd is geen gebeurtenis met een begin en een eind in deze zin, dus geen indefinido.",
   "ue": "Both imperfect: era is the state (when I was a child) and vivía the duration. A childhood is not an event with a start and a finish in this sentence, so no indefinite."},
  "Cuando ___ (llegar) a casa, mi hermano ___ (cocinar) la cena.": {
   "opts": ["llegué, cocinaba", "llegaba, cocinó", "llegué, cocinó", "llegaba, cocinaba"], "c": 0,
   "u": "Llegué (indefinido) is het moment waarop je binnenkwam. Cocinaba (imperfecto) is wat er al aan de gang was: hij was aan het koken. Cocinó zou betekenen dat hij pas begon toen jij er was.",
   "ue": "Llegué (indefinite) is the moment you came in. Cocinaba (imperfect) is what was already going on: he was cooking. Cocinó would mean he only started once you were there."},
  # twee uitleggen die eindigden op een slag om de arm bij een vraag met maar één gat
  "Mientras ___ (caminar) por el parque, vi un perro muy raro.": {
   "u": "Mientras kondigt de achtergrond aan, en die staat in de imperfecto: caminaba. De gebeurtenis die erdoorheen komt (vi) staat al ingevuld, zodat je hier alleen de achtergrond hoeft te kiezen.",
   "ue": "Mientras announces the background, and that takes the imperfect: caminaba. The event cutting through it (vi) is already filled in, so here you only choose the background."},
  "___ (llover) mucho cuando llegamos a la montaña.": {
   "u": "Llovía (imperfecto) is het weer als decor. De gebeurtenis (llegamos) staat al ingevuld in de indefinido, dus je kiest hier alleen de achtergrond.",
   "ue": "Llovía (imperfect) is the weather as scenery. The event (llegamos) is already filled in as an indefinite, so here you only choose the background."},
 },
}

# ---------------------------------------------------------------------------
# toepassen: QUIZZES staat per regel als compacte JSON, dus dit gaat over data
# ---------------------------------------------------------------------------
a, b = np._arrayGrenzen(src, "QUIZZES")
blok = src[a:b + 1]
regels = blok.split("\n")
raak = 0
for i, regel in enumerate(regels):
    kaal = regel.strip().rstrip(",")
    if not kaal.startswith("{"):
        continue
    qz = json.loads(kaal)
    if qz.get("id") not in NIEUWE:
        continue
    wijzig = NIEUWE[qz["id"]]
    for v in qz["vragen"]:
        nw = wijzig.get(v.get("q"))
        if not nw:
            continue
        for sleutel, waarde in nw.items():
            v[sleutel] = waarde
        raak += 1
    terug = json.dumps(qz, ensure_ascii=False, separators=(",", ":"))
    regels[i] = " " + terug + ("," if regel.rstrip().endswith(",") else "")

DOE_APP = raak > 0 and not AL_GEDAAN
if DOE_APP:
    # 14 onbeantwoordbare vragen, plus twee uitleggen met een overbodige slag om de arm
    assert raak == 16, "verwacht 16 aangeraakte vragen, kreeg %d" % raak
    src = src[:a] + "\n".join(regels) + src[b + 1:]

    # =========================================================================================
    # de controles
    # =========================================================================================
    # Alleen QUIZZES, want B_QUIZZES staat niet als JSON in het bestand. Die kant wordt bewaakt
    # door pw-gatentelling.js, die de vragen bij de app zelf opvraagt en dus allebei de sporen ziet.
    gaten_fout, paar, gezien = [], 0, 0
    a2, b2 = np._arrayGrenzen(src, "QUIZZES")
    for regel in src[a2:b2 + 1].split("\n"):
        kaal = regel.strip().rstrip(",")
        if not kaal.startswith("{"):
            continue
        qz = json.loads(kaal)
        for j, v in enumerate(qz.get("vragen") or []):
            gezien += 1
            n = len(re.findall(r"_{2,}", v.get("q") or ""))
            opts = v.get("opts") or []
            c = v.get("c")
            if not (isinstance(c, int) and 0 <= c < len(opts)):
                gaten_fout.append("%s v%d heeft geen geldig antwoord" % (qz["id"], j + 1))
                continue
            if n < 2:
                continue
            delen = [x for x in re.split(r"\s*[·,]\s*", opts[c]) if x.strip()]
            if len(delen) < n:
                gaten_fout.append("%s v%d: %d gaten, antwoord '%s' vult er %d"
                                  % (qz["id"], j + 1, n, opts[c], len(delen)))
            else:
                paar += 1
            # en elke afleider hoort evenveel delen te hebben, anders verraadt de vorm het antwoord
            for o in opts:
                d = [x for x in re.split(r"\s*[·,]\s*", o) if x.strip()]
                if len(d) != len(delen):
                    gaten_fout.append("%s v%d: '%s' heeft %d delen en het antwoord %d"
                                      % (qz["id"], j + 1, o, len(d), len(delen)))
    assert not gaten_fout, "onbeantwoordbare vragen over:\n  - " + "\n  - ".join(gaten_fout)
    assert gezien >= 270, "er zijn maar %d vragen gezien, dus de controle keek niet overal" % gezien
    assert paar == 30, "verwacht 30 vragen met een volledig paar in QUIZZES, kreeg %d" % paar
    np.keuring(src)
    APP.write_text(src, encoding="utf-8")
    print("index.html: 14 onbeantwoordbare vragen hersteld, %d meergats-vragen vullen nu al hun gaten" % paar)
else:
    print("index.html: stond er al")

if DOE_VER:
    a3 = APP.read_text(encoding="utf-8")
    b3 = a3.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a3 != b3, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b3, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
