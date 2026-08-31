#!/usr/bin/env python3
# v23.217 - de nacht levert af zonder te rebasen, en zegt het als het misgaat
#
# WAT ER STOND
#
# De laatste stap van curriculum.yml deed `git pull --rebase` en dan `git push`. Sinds 23 augustus
# mislukte die rebase elke nacht, acht runs achter elkaar, met deze melding:
#
#     ::warning::rebase mislukt; hartslag en opnames blijven liggen tot de volgende run.
#
# en daarna exitcode 0. De stap werd dus groen terwijl de lading op de vloer bleef liggen.
#
# Gemeten: tools/avondrun-hart.json op main stond acht dagen stil op 23 augustus, terwijl er in die
# tijd acht runs waren. En in elke rode nacht staat in de samenvatting "Audio: 42 ingesproken ·
# 18.529 tekens". Die opnames zijn elke nacht gemaakt, betaald, en daarna weggegooid: ongeveer
# 148.000 ElevenLabs-tekens.
#
# IK HEB TWEE VERKLARINGEN BEDACHT EN ZE ALLEBEI ZELF ONDERUIT GEHAALD
#
#   1. Ondiepe kloon. actions/checkout haalt standaard één commit op, en dan zou de rebase geen
#      gemeenschappelijke voorouder vinden. Nagespeeld met een echte --depth 1 kloon waarvan de
#      bron intussen vooruitliep: `git pull --rebase` werkt gewoon, exitcode 0.
#   2. Een commit die bij het herspelen leeg wordt. De stap zet eerst main's audio/ terug en
#      committeert die, dus die commit kan bij het rebasen niets meer toevoegen. Nagespeeld: git
#      meldt "skipped previously applied commit" en gaat door.
#
# De echte foutregel staat in het staplogboek van de run, en dat is alleen te lezen met een
# ingelogde sessie. Die had ik niet. Een derde gok erbovenop zetten is precies wat je niet moet
# doen: een verkeerde diagnose is erger dan geen.
#
# DUS NIET DE REBASE REPAREREN MAAR HEM WEGHALEN
#
# Dit is geen omweg om de diagnose heen, het is de juiste vorm. Op deze main publiceren drie
# schrijvers: deze Action, de geplande nachttaak, en de logboek-Action. Die laatste wordt door
# GitHub steeds later ingepland (gemeten: van 02:30 naar 06:54, 07:58, 11:37 en 13:01), dus main
# verschuift tegenwoordig middenin het venster van de avondrun.
#
# En wat de avondrun wil afleveren zijn geen commits maar BESTANDEN: een hartslag en een handvol
# mp3's. Voor bestanden is rebasen het verkeerde gereedschap. tools/avondrun-leveren.sh doet het
# in de vorm die bij de lading past: bestanden apart zetten, verse main pakken, de bestanden erop
# leggen, één commit, pushen. Er valt niets te herspelen en dus niets te botsen. Wordt de push toch
# geweigerd omdat iemand er ondertussen weer overheen ging, dan begint het opnieuw met nog versere
# main. Drie pogingen.
#
# Twee dingen die daardoor beter kloppen dan eerst, niet alleen robuuster:
#
#   - De samenvoeging van audio/stemmen.json (de regel van v23.179: main wint, wij vullen aan)
#     gebeurt nu ná het ophalen van verse main, dus tegen de main van nu in plaats van tegen de main
#     van drie uur geleden.
#   - Staat er werk van een eerdere stap dat nooit gepusht is, dan gaat dat eerst de deur uit vóór
#     er iets gereset wordt. Anders zou een mislukte push in "Reparatie direct live" hier stilletjes
#     worden opgeruimd.
#
# EN DE MELDING
#
# "rebase mislukt" is geen diagnose. De foutregel van git stond in het staplogboek en de melding
# waar iedereen naar kijkt was leeg. Dat is dezelfde fout als "telling klopt niet: sentences" van
# v23.216: een controle die wel afgaat maar niet vertelt wat hij zag. De foutregel gaat nu mee de
# melding in, en het script eindigt op 1 in plaats van op 0. Een levering die stil wegvalt en groen
# blijft is precies hoe dit acht nachten kon duren.
#
# DE PROEF, EN WAAROM HIJ ZICHZELF MOET KUNNEN LATEN VALLEN
#
# `sh tools/avondrun-leveren.sh --zelftest` bouwt een echt kaal repository met twee klonen, laat
# main onder de leverende kloon vandaan bewegen (precies wat de logboek-Action elke nacht doet) en
# levert dan. Vijf uitspraken, waarvan twee controlegevallen.
#
# Die twee zijn nagemeten door het script expres te slopen:
#
#     git push  ->  git push --force en de reset eruit
#         "het werk van de andere schrijver is niet weggegooid"  wordt ROOD
#     de "niets te leveren"-tak eruit en commit --allow-empty
#         "een tweede levering zonder nieuws maakt geen lege commit"  wordt ROOD
#
# Zonder die twee metingen zou "alles groen" niets betekenen, want een proef die nergens op valt is
# geen proef. De workflow draait hem voortaan naast de andere zelftests.
#
# WAT DEZE RONDE BEWUST NIET DOET
#
# De stap "Reparatie direct live" heeft dezelfde kwetsbaarheid (een kale `git push` die geweigerd
# wordt zodra main verschoven is) maar krijgt dit script nog niet. Zijn lading bevat index.html en
# versie.txt, en dan komt er een vraag bij die hier niet thuishoort: wat als de nachttaak intussen
# een hoger versienummer heeft gepubliceerd? Een bestand blind over main heen kopiëren zou dan een
# versie terugdraaien. Dat verdient een eigen ronde met een eigen meting, niet een regel die ik er
# hier even bij verzin.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
WF = W / ".github" / "workflows" / "curriculum.yml"
NIEUW = "v23.217"

wf = WF.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_WF = "avondrun-leveren.sh" not in wf
DOE_VER = _num(huidig_ver) < _num(NIEUW)

# =============================================================================================
# 1. de zelftest van de levering draait mee met de andere zelftests
# =============================================================================================
if DOE_WF:
    anker = """      # 28 augustus: de regel die bepaalt of een klapper een tweede worp krijgt. Zie de kop van
      # tools/avondrun-herkansing.js: dat onderscheid liep vijf nachten om de herkansing heen.
      - name: Zelftest van de herkansing
        run: node tools/avondrun-herkansing.js --zelftest"""
    assert wf.count(anker) == 1, "anker voor de zelftests niet gevonden"
    wf = wf.replace(anker, anker + """

      # 31 augustus: de levering zelf. Deze proef bouwt een echt kaal repository, laat main eronder
      # vandaan bewegen zoals de logboek-Action elke nacht doet, en levert dan af. Hij staat hier
      # tussen de andere zelftests omdat het afleveren acht nachten lang de stille blokkade was:
      # er werd wél gegenereerd en wél ingesproken, en het kwam alleen nooit op main.
      - name: Zelftest van de levering
        run: sh tools/avondrun-leveren.sh --zelftest""", 1)

# =============================================================================================
# 2. de laatste stap levert af in plaats van te rebasen
# =============================================================================================
if DOE_WF:
    start = wf.index("      - name: Hartslag en audio wegschrijven")
    eind = wf.index("      # 28 AUGUSTUS: DE HARTSLAG MOET ERGENS STAAN WAAR HIJ NIET KAN VERDWIJNEN")
    oud = wf[start:eind]
    assert "git pull --rebase" in oud, "de rebase staat niet in de stap die ik vervang"
    assert "stemmen-samenvoegen" in oud, "de manifestsamenvoeging staat niet in deze stap"

    nieuw = """      # DE HARTSLAG EN DE OPNAMES OP MAIN KRIJGEN
      #
      # Hier stond een blok van veertig regels shell dat eindigde op `git pull --rebase` en dan
      # `git push`. Die rebase mislukte acht nachten op rij (23 t/m 30 augustus), waarna de stap met
      # een ::warning:: en exitcode 0 eindigde. Groen dus, en de hartslag en de opnames van die
      # nacht bleven liggen. Gemeten gevolg: avondrun-hart.json stond acht dagen stil, en er is elke
      # nacht voor ongeveer 18.500 ElevenLabs-tekens ingesproken dat daarna is weggegooid.
      #
      # Wat deze stap wil afleveren zijn geen commits maar bestanden, en voor bestanden is rebasen
      # het verkeerde gereedschap: op deze main publiceren drie schrijvers, en de logboek-Action
      # wordt door GitHub steeds later ingepland (van 02:30 naar 13:01), dus main verschuift
      # tegenwoordig middenin het venster van de avondrun.
      #
      # tools/avondrun-leveren.sh zet de lading apart, pakt verse main, legt de bestanden erop,
      # committeert één keer en pusht. Geweigerd omdat iemand er ondertussen overheen ging? Dan
      # opnieuw met nog versere main, drie pogingen. De foutregel van git gaat mee de melding in en
      # het script eindigt op 1, want een levering die stil wegvalt en groen blijft is precies hoe
      # dit acht nachten kon duren. De proef staat in het script zelf en draait hierboven mee.
      - name: Hartslag en audio wegschrijven
        if: always()
        run: |
          [ -f tools/avondrun-hart.json ] || exit 0
          git config user.name "curriculum-bot"
          git config user.email "actions@users.noreply.github.com"
          REGEL="avondrun: hartslag $(node -e "const h=require('./tools/avondrun-hart.json'); console.log(h.gepubliceerd ? 'geleverd' : 'niets geleverd (' + (h.reden||'geen reden') + ')')")"
          sh tools/avondrun-leveren.sh "$REGEL" tools/avondrun-hart.json audio

"""
    wf = wf[:start] + nieuw + wf[eind:]

# =============================================================================================
# 3. de toelichting die naar de rebase wees, wijst nu naar wat er staat
#
# Een commentaar dat een mechanisme beschrijft dat er niet meer is, is erger dan geen commentaar:
# de volgende lezer gaat op zoek naar een rebase die nergens meer staat. En de meting erin klopt
# ook niet meer (vijf runs is er inmiddels acht).
# =============================================================================================
if DOE_WF:
    oud_c = """      # De hartslag is het enige kanaal waarlangs deze run vertelt wat er misging, en hij hing tot nu
      # toe volledig aan een push. Die push zit achter `git pull --rebase`, en als die rebase mislukt
      # eindigt de stap met een ::warning:: en exitcode 0: groen, en de hartslag blijft liggen.
      # Gemeten op 28 augustus: tools/avondrun-hart.json op main dateert van 23 augustus, terwijl er
      # sindsdien vijf runs waren. Vijf nachten lang was er dus geen enkele manier om te zien waarom."""
    assert wf.count(oud_c) == 1, "de toelichting bij de samenvatting niet gevonden"
    wf = wf.replace(oud_c, """      # De hartslag is het enige kanaal waarlangs deze run vertelt wat er misging, en hij hing tot nu
      # toe volledig aan een push. Die push zat achter `git pull --rebase`, en als die rebase mislukte
      # eindigde de stap met een ::warning:: en exitcode 0: groen, en de hartslag bleef liggen.
      # Gemeten op 28 augustus: tools/avondrun-hart.json op main dateerde van 23 augustus, terwijl er
      # sindsdien vijf runs waren. Op 31 augustus waren dat er acht, en toen is de rebase vervangen
      # door tools/avondrun-leveren.sh (v23.217).
      #
      # Die vervanging maakt deze stap niet overbodig, integendeel. Ook een levering die drie keer
      # opnieuw probeert kan uiteindelijk falen, en dan hoort de reden nog steeds ergens te staan
      # waar hij niet aan een push hangt.""", 1)

if DOE_WF:
    assert wf.count("avondrun-leveren.sh") == 4, wf.count("avondrun-leveren.sh")
    assert "if ! git pull --rebase" not in wf, "er staat nog een uitgevoerde rebase in de workflow"
    WF.write_text(wf, encoding="utf-8")
    print(".github/workflows/curriculum.yml: de nacht levert af in plaats van te rebasen")
else:
    print(".github/workflows/curriculum.yml: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
