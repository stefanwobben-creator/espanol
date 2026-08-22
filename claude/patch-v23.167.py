#!/usr/bin/env python3
# v23.167 - de dag heeft een voorkant en een achterkant
#
# Stefan, 22 aug: "ik heb daarom toen ook gevraagd maak een prototype want ik heb het idee dat we
# qua ontwikkeling beetje vastlopen en gaan tweaken terwijl het conceptueel nog niet helemaal klopt
# dus we moeten grotere wijzigingen durven door te voeren." Gevraagd wat als eerste; gekozen: "de
# les wordt de app."
#
# WAT ER GEMETEN IS
#
# renderLessons() tekende zeven dingen onder elkaar, en de dagles was het eerste van zeven:
#
#   1. ritmeCard()        je les
#   2. samenKaartNu()     de uitnodiging voor een maatje
#   3. dagNieuwsHtml()    wat er nieuw is
#   4. muurHtml()         de vraag van vandaag en de muur van je groep
#   5. dagLijnHtml()      je 14-daagse strook
#   6. dagSpeelHtml()     drie speltegels
#   7. thuisKaartHtml()   zet hem op je beginscherm
#
# Dat is geen dagscherm maar een menu waarop je les toevallig bovenaan staat. Wie hier komt heeft
# zes redenen om iets anders te doen dan zijn les, en vijf ervan zijn leuker dan beginnen.
#
# En het is niet wat het prototype van 20 augustus zei. Beslissing 8 daar: het spel gaat open op
# "les af", niet ernaast. Dat is Nation's vierde draad (vloeiendheid: bekende dingen sneller doen),
# en die hoort ná de andere drie te komen, niet in plaats van.
#
# WAT ER VERANDERT
#
# De dag krijgt een voorkant en een achterkant.
#
#   voorkant (les nog niet af)   alleen je les, plus de installatiekaart
#   achterkant (les af)          alles wat er nu ook staat: je groep, je lijn, het nieuws, de spellen
#
# Dit is met opzet weghalen en niet verplaatsen. Alles blijft bestaan en blijft bereikbaar; het komt
# alleen niet meer vóór je les te staan. Wie echt eerst wil spelen kan dat nog steeds via Spelen in
# de balk, en dat is precies goed: een omweg mag bestaan, hij hoort alleen niet de eerste optie te
# zijn.
#
# HET RISICO, EN WAAROM IK HET NEEM
#
# De muur is het enige sociale dat de app heeft, en die schuift nu achter je les. Als Ilona iets
# schrijft en Stefan doet zijn les niet, ziet hij het pas morgen. Dat is een echte prijs.
#
# Ik neem hem omdat de tegenprijs groter is en gemeten: Stefans eigen klacht is dat de app hem
# toetst en niet onderwijst, en zes kaarten die om aandacht vragen naast de enige kaart die lesgeeft
# maken dat erger, niet beter. Bovendien is de muur pas iets waard als je zelf iets geschreven hebt
# (dagZinAnderen() toont de anderen pas nadat je zelf hebt gepost), en dat schrijven is de
# productiedraad die in de les hoort.
#
# Als dit fout blijkt, is de meting simpel: schrijft hij minder vaak een zin dan hiervoor. Dan gaat
# de muur terug naar voren en is dit besluit verkeerd geweest.
#
# EN EEN BUG DIE HIERDOOR ZICHTBAAR WERD
#
# lesFlowWinst() stelt na de les voor om de vraag van vandaag te beantwoorden, en deed dan
# show("perfil"). Het invoerveld #dagzinInp staat niet op Profiel maar op Vandaag, in muurHtml().
# Die knop bracht je dus al die tijd naar een scherm zonder invoerveld. Nu naar Vandaag, waar het
# veld staat, en waar het na deze versie ook precies op het goede moment staat: je les is net af.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.167"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # -----------------------------------------------------------------------
    # 1. het dagscherm: vóór je les staat er één ding
    # -----------------------------------------------------------------------
    rep('''  var html = ritmeCard();
  // v19.57: de uitnodiging staat direct onder de dagkaart, dus meteen in beeld. Hij verdwijnt
  // zodra je gedeeld hebt of zodra er iemand naast je zit; blijven vragen is zeuren.
  // v19.58: ook hier hoogstens één vraag tegelijk; samenKaartNu() bepaalt welke.
  html += samenKaartNu(true);
  // v19.69: het dagbord. Wat is er nieuw, hoe loopt het, waar kan ik nu spelen.
  html += dagNieuwsHtml();
  // v22.7: de muur, direct onder het nieuws van vandaag en boven de rest. Wat je maatjes leerden is
  // nieuws, geen bijzaak, maar het staat wél onder je eigen dagles: eerst jij, dan de anderen.
  html += muurHtml();
  html += dagLijnHtml();
  html += dagSpeelHtml();
  // v20.4: onderaan, want hij gaat niet over vandaag leren maar over hoe je hier morgen weer komt.
  html += thuisKaartHtml();''',
        '''  /* v23.167: DE VOORKANT EN DE ACHTERKANT VAN DE DAG.

     Hier stonden zeven kaarten onder elkaar, waarvan je les de eerste was. Dat is geen dagscherm
     maar een menu, en op een menu is beginnen de saaiste optie: van de zeven kaarten waren er vijf
     leuker dan je les. Nu staat er vóór je les één ding, en komt de rest erachter vandaan zodra je
     klaar bent.

     Dit volgt beslissing 8 uit het prototype van 20 aug: het spel gaat open op "les af", niet
     ernaast. Dat is Nation's vierde draad, vloeiendheid, en die hoort ná de andere drie te komen.

     Weggehaald is niets: alles hieronder bestaat nog en is nog bereikbaar via de balk. Het staat
     alleen niet meer vóór het enige dat lesgeeft. */
  var lesAf = !!(S.lesFlow && S.lesFlow[today()]);
  var html = ritmeCard();
  if(lesAf){
    // v19.57: de uitnodiging staat direct onder de dagkaart, dus meteen in beeld. Hij verdwijnt
    // zodra je gedeeld hebt of zodra er iemand naast je zit; blijven vragen is zeuren.
    // v19.58: ook hier hoogstens één vraag tegelijk; samenKaartNu() bepaalt welke.
    html += samenKaartNu(true);
    // v19.69: het dagbord. Wat is er nieuw, hoe loopt het, waar kan ik nu spelen.
    html += dagNieuwsHtml();
    /* v22.7: de muur. v23.167: hij staat nu achter je les in plaats van eronder, en dat is de
       duurste regel van deze versie: schrijft je groep iets terwijl jij je les niet doet, dan zie
       je het pas morgen. Ik neem die prijs omdat de muur pas iets waard is als je zelf geschreven
       hebt (dagZinAnderen toont de anderen pas ná je eigen zin), en dat schrijven hoort in je les.
       Meting als dit fout is: schrijft hij minder vaak een zin dan hiervoor. */
    html += muurHtml();
    html += dagLijnHtml();
    html += dagSpeelHtml();
  }
  // v20.4: onderaan, want hij gaat niet over vandaag leren maar over hoe je hier morgen weer komt.
  html += thuisKaartHtml();''')

    # De muur ophalen is een netwerkverzoek; zonder muur op het scherm is dat een verzoek om niets.
    rep('''  muurWire();
  muurHaal();''',
        '''  /* v23.167: alleen als de muur er staat. muurWire() en muurHaal() zijn veilig zonder kaart
     (beide beginnen met een getElementById-controle), maar muurHaal() doet een netwerkverzoek en
     dat is voor een scherm zonder muur een vraag om niets. */
  if(lesAf){ muurWire(); muurHaal(); }''')

    # -----------------------------------------------------------------------
    # 2. de knop naar de vraag van vandaag ging naar een scherm zonder invoerveld
    # -----------------------------------------------------------------------
    rep('''        doe:function(){ show("perfil"); setTimeout(function(){
          var el = document.getElementById("dagzinInp"); if(el) el.focus();
        }, 300); }};''',
        '''        /* v23.167: hier stond show("perfil"). #dagzinInp staat niet op Profiel maar op Vandaag,
           in muurHtml(), dus deze knop bracht je naar een scherm zonder invoerveld. Nu naar Vandaag,
           waar het veld staat en waar het sinds deze versie ook pas verschijnt als je les af is:
           precies het moment waarop dit voorstel gedaan wordt. */
        doe:function(){ show("lessen"); setTimeout(function(){
          var el = document.getElementById("dagzinInp"); if(el) el.focus();
        }, 300); }};''')

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
