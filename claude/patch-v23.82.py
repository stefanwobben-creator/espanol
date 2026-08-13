#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.82: geen luisterknop bij een recept, en de zes trucs worden oefenzinnen.

Stefan, 13 aug: "1. recepten behoeft geen audio. 2. ja goed idee, doe maar."

## 1. De knop die niets goeds kon doen

renderBoekLectura() zet onvoorwaardelijk een knop "Luisteren" boven elke tekst. Bij Chispa en bij
Franco hoort die er: daar ligt een opname van een verteller. Bij een recept ligt die er niet en
komt er ook geen, en sinds v23.76 betekent dat niet stilte maar de browserstem. Die zou dan een
ingrediëntenlijst gaan voorlezen: "een kilo tomaten, een komkommer, een groene paprika". Dat is
geen luisteroefening, dat is een boodschappenlijst met een stem.

De knop verschijnt daarom alleen nog bij een reeks die audio heeft. Dat staat nu als eigenschap op
de reeks (`stem: true`), niet als lijstje van voorvoegsels ergens in een functie: de volgende reeks
hoeft dan alleen te zeggen of hij een verteller heeft.

## 2. De trucs worden oefenzinnen

Dit was mijn eigen voorstel en Stefan zei ja: de zes trucs onderaan de recepten zijn de meest
herbruikbare zinnen van de hele reeks. Niet omdat ze over koken gaan, maar omdat ze dicht zitten:
"Aparta la sartén del fuego antes de echar el pimentón" is één zin met de gebiedende wijs, antes de
+ infinitief, en een lidwoord dat je moet kiezen.

Wat ik níét heb gedaan is de avondrun leren ze zelf te oogsten. Dat is een verandering in
tools/curriculum.js, en die kan ik hier niet uitproberen: er is geen ADMIN_KEY in deze omgeving, dus
promptwijzigingen zouden ongetest de nacht in gaan. Een prompt die je niet kunt draaien, is een
prompt waarvan je hoopt. In plaats daarvan staan de zes zinnen er nu gewoon in, met tag "receta",
zodat ze meteen in de rotatie zitten en de avondrun ze als bestaande zinnen van die tag ziet
(promptZinnenVerschijnsel toont de eerste acht van een tag als voorbeeld) en er zelf op verder kan.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.82"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.82" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_KNOP = '''    "<div class='row' style='margin:6px 0 10px'><button class='ghost' id='btnBoekLuister'>\U0001f50a "+ct("Luisteren","Listen")+"</button></div>"+'''

A_CHISPA = ''' {id:"chispa", pre:"boek-", nl:"Chispa", en:"Chispa",'''
A_FRANCO = ''' {id:"franco", pre:"hist-", nl:"Espa\u00f1a: los a\u00f1os de Franco", en:"Espa\u00f1a: los a\u00f1os de Franco",'''
A_COCINA = ''' {id:"cocina", pre:"receta-", nl:"La cocina espa\u00f1ola", en:"La cocina espa\u00f1ola",'''

# Laatste zin van SENTENCES. De avondrun kan hier 's nachts achteraan schrijven, dus dit anker is
# bewust de sluithaak van de array en niet een zin-id dat morgen anders kan zijn.
# Het einde van SENTENCES. Eerst stond hier "];\n\nvar B_SENTENCES = [", en dat was fout: de array
# die vlak vóór B_SENTENCES eindigt is B_WORDS, niet SENTENCES. Het anker kwam precies één keer voor,
# de rep() gaf dus geen kik, de poort bleef 70/70 groen, en de zes zinnen stonden een halve dag
# lang als woordkaarten in de A0-woordenlijst. Alleen de telling van content-lib verried het:
# "178 zinnen" terwijl er 184 in het bestand stonden.
#
# Les: een anker dat één keer voorkomt is nog geen anker op de goede plek. Na SENTENCES komt QUIZZES.
A_ZINEIND = '''\n];\n\nvar QUIZZES = ['''

if DOE_APP:
    ontbreekt = [n for n, a in (("de luisterknop", A_KNOP), ("de reeks chispa", A_CHISPA),
                                ("de reeks franco", A_FRANCO), ("de reeks cocina", A_COCINA),
                                ("het einde van SENTENCES", A_ZINEIND)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.81. Eerst bijtrekken:\n\n    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


ZINNEN = u''',
 {"id":"s180","lvl":2,"nl":"Schil ze niet, het vel gaat weg met de blender.","en":"Don't peel them, the skin goes away in the blender.","es":"No los peles, la piel se va con la batidora.","alt":["no los peles, la piel se va con la batidora","no los peles la piel se va con la batidora"],"uitleg":"Bij een verbod staat het voornaamwoord v\u00f3\u00f3r het werkwoord: no los peles. Bij een gebod komt het er juist achter vast: p\u00e9lalos.","ue":"In a negative command the pronoun goes before the verb: no los peles. In a positive command it attaches to the end: p\u00e9lalos.","tag":"receta"},
 {"id":"s181","lvl":2,"nl":"Haal de pan van het vuur voordat je het paprikapoeder toevoegt.","en":"Take the pan off the heat before you add the paprika.","es":"Aparta la sart\u00e9n del fuego antes de echar el piment\u00f3n.","alt":["aparta la sarten del fuego antes de echar el pimenton","aparta la sart\u00e9n del fuego antes de echar el piment\u00f3n"],"uitleg":"Antes de wordt gevolgd door een infinitief, ook als er in het Nederlands 'voordat je' staat. Del is de samentrekking van de + el.","ue":"Antes de is followed by an infinitive, even where Dutch and English use a full clause. Del is de + el contracted.","tag":"receta"},
 {"id":"s182","lvl":2,"nl":"Als je alles in \u00e9\u00e9n keer toevoegt, schift de gazpacho.","en":"If you add it all at once, the gazpacho splits.","es":"Si lo echas todo de golpe, el gazpacho se corta.","alt":["si lo echas todo de golpe, el gazpacho se corta","si lo echas todo de golpe el gazpacho se corta"],"uitleg":"Na si komt gewoon de tegenwoordige tijd, en in de gevolgzin ook. Se corta is wederkerend: het schift vanzelf, niemand doet het.","ue":"After si you use the plain present, and so does the result clause. Se corta is reflexive: it splits by itself, nobody does it.","tag":"receta"},
 {"id":"s183","lvl":2,"nl":"Het brood moet warm zijn als je de knoflook erover wrijft.","en":"The bread has to be hot when you rub the garlic on it.","es":"El pan tiene que estar caliente cuando frotas el ajo.","alt":["el pan tiene que estar caliente cuando frotas el ajo"],"uitleg":"Tener que + infinitief is de gewone manier om moeten te zeggen. Estar caliente en niet ser: warm zijn is een toestand van nu, geen eigenschap van brood.","ue":"Tener que + infinitive is the usual way to say must. Estar caliente, not ser: being hot is a current state, not a property of bread.","tag":"receta"},
 {"id":"s184","lvl":3,"nl":"Met te veel champignons tegelijk laten ze water los.","en":"With too many mushrooms at once they release water.","es":"Con demasiados champi\u00f1ones a la vez sueltan agua.","alt":["con demasiados champinones a la vez sueltan agua","con demasiados champi\u00f1ones a la vez sueltan agua"],"uitleg":"Demasiado buigt mee met wat erachter staat: demasiados champi\u00f1ones, demasiada agua. Soltar is een schoenwerkwoord: o wordt ue, dus sueltan.","ue":"Demasiado agrees with the noun: demasiados champi\u00f1ones, demasiada agua. Soltar is stem-changing: o becomes ue, hence sueltan.","tag":"receta"},
 {"id":"s185","lvl":2,"nl":"Laat het deeg een half uur rusten.","en":"Let the dough rest for half an hour.","es":"Deja reposar la masa media hora.","alt":["deja reposar la masa media hora"],"uitleg":"Dejar + infinitief betekent laten: deja reposar, zonder que ertussen. Media hora heeft geen lidwoord, net als in 'een half uur' zonder de.","ue":"Dejar + infinitive means to let: deja reposar, with no que in between. Media hora takes no article.","tag":"receta"}'''

if DOE_APP:
    # 1. de luisterknop hangt aan de reeks
    rep(A_KNOP, '''    /* v23.82: alleen als de reeks een verteller heeft. Stefan, 13 aug: "recepten behoeft geen
       audio." Zonder deze regel zou de browserstem een ingredi\u00ebntenlijst gaan voorlezen, en dat is
       geen luisteroefening maar een boodschappenlijst met een stem. */
    (function(){ var r = leesReeksVan(h); return (r && r.stem === false) ? "" :
      "<div class='row' style='margin:6px 0 10px'><button class='ghost' id='btnBoekLuister'>\U0001f50a "+ct("Luisteren","Listen")+"</button></div>"; })()+''')

    rep(A_CHISPA, A_CHISPA + ''' stem:true,''')
    rep(A_FRANCO, A_FRANCO + ''' stem:true,''')
    # stem:false, en niet "veld weglaten": een ontbrekend veld zou hier als "geen audio" gelezen
    # worden en dan is de standaard stil in plaats van luid, wat voor elke volgende reeks de
    # verkeerde kant op faalt.
    rep(A_COCINA, A_COCINA + ''' stem:false,''')

    # De knop weghalen zonder de bedrading weg te halen is een lege verwijzing. Gemeten: startBoek()
    # klapte meteen op "Cannot set properties of null". Precies daarom is een schermtest goedkoper
    # dan een goed gevoel over een wijziging van vier regels.
    rep('  document.getElementById("btnBoekLuister").onclick = function(){ boekSpreek(h); };',
        '  var bl = document.getElementById("btnBoekLuister");\n'
        '  if(bl) bl.onclick = function(){ boekSpreek(h); };')

    # 2. de zes trucs als oefenzinnen
    rep(A_ZINEIND, ZINNEN + A_ZINEIND)

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s (luisterknop per reeks, zes trucszinnen s180-s185)" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
