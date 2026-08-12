#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.50: de afleiders zijn van dezelfde soort, en het voorstel zegt wat er gebeurt.

Stefan, na de telefoontest van 11 aug: "ik denk dat op basis van de toets A1 ook te hoog is
ingeschaald, omdat je veel woorden (bijna de helft) wel een beetje kunt raden."

Nagemeten op tweehonderd getrokken vragen. Zijn gevoel klopt, maar de oorzaak is anders dan hij
dacht, en er zat een grotere vondst onder.

## 1. Raden op woordsoort: 15%, en dat is echt kapot

Stefans voorbeeld was *el jardín* met als afleiders *de badkamer*, *hoeveel kost het?* en *blauw*.
Een kamer, een vraag en een kleur. Je hoeft het woord niet te kennen om te zien welk antwoord bij
een zelfstandig naamwoord hoort dat met "el" begint.

Gemeten: bij **30 van de 200 vragen (15%)** is het goede antwoord het enige van zijn woordsoort. Bij
24 vragen staan er meer dan twee verschillende woordsoorten door elkaar.

`peilOpties()` koos afleiders uit dezelfde `tag` alleen als er drie beschikbaar waren, en viel
anders terug op de hele bak van 2184 woorden. Die terugval is precies waar het misgaat: een tag met
weinig woorden levert een vraag op waar je op vorm kunt gokken.

Nu is de volgorde: zelfde tag én zelfde soort, dan zelfde soort, dan zelfde tag, dan pas de hele
bak. De soort wordt uit het Spaans afgeleid en niet uit de vertaling, want het Spaans is er altijd
en is regelmatiger: een lidwoord ervoor is een zelfstandig naamwoord, één woord op -ar/-er/-ir is
een werkwoord, meer dan één woord zonder lidwoord is een uitdrukking, de rest is de rest.

## 2. Wat er níét kapot is, en dat is de eerlijke helft van het verhaal

De andere kant van "je kunt de helft raden" zijn de cognaten: *el hospital*, *el mapa*, *el café*,
*la biblioteca*, *el taxi*. Wie die herkent, kent ze ook echt. Dat is geen fout in de meting maar
woordenschat die je meebrengt uit het Nederlands, Engels of Frans, en een A1-schatting hoort die
mee te tellen. Daar valt niets te repareren zonder de meting te laten liegen.

## 3. De grootste vondst: A0 en A1 zijn hetzelfde

Bij het nakijken wat de schatting eigenlijk stuurt, bleek dit:

    <button data-track="beginner" data-lvl="A0">A0 · helemaal nieuw</button>
    <button data-track="beginner" data-lvl="A1">A1 · een paar woorden</button>
    <button data-track="a2"       data-lvl="A2">A2 · ik ken de basis</button>

En bij het aanmaken van het profiel: `profiles.list.push({name, track: newTrack, ...})`. Het veld
`lvl` wordt nergens bewaard. `TRACKS` kent er twee: `beginner` en `a2`.

**Drie knoppen, twee uitkomsten.** A0 en A1 leveren exact dezelfde app op: dezelfde woorden,
dezelfde zinnen, dezelfde lessen. Het enige echte verschil zit bij A2, en dat is er dan ook een:
die krijgt de grote bak én `niveauClaim(0)`, wat heel A1 als geclaimd wegzet.

Dat verandert hoe erg Stefans zorg is. "Te hoog ingeschaald op A1" heeft geen gevolg voor wat je
leert, want A1 en A0 zijn hetzelfde pad. De grens die er wél toe doet is die naar A2, en die staat
op POORT_PCT (0,85): je moet ongeveer 348 van de 409 A1-woorden herkennen. Dat is streng, en dat
mag ook, want daarachter wordt heel A1 overgeslagen.

Wat er dan overblijft is een belofte die de app niet waarmaakt: het uitslagscherm zegt "Je begint op
A1" alsof dat iets anders is dan A0. Deze versie laat het zeggen wat er echt gebeurt. De knoppen
blijven staan (ze zijn een prima manier om te zeggen hoe je jezelf ziet), maar de uitslag belooft
geen onderscheid dat er niet is.

Of A0 en A1 écht uit elkaar moeten: dat is curriculumwerk en het hoort na de lancering. Het staat in
claude/lancering.md.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.50"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function woordSoort" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

if DOE_APP:
    ANKERS = ['var APP_VERSIE = "v23.49";', 'function peilOpties(w){',
              '     start:function(l){ return "Je begint op "+l+"."; },']
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:80] for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.49. Eerst die draaien, of eerst bijtrekken:\n"
              "\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep('var APP_VERSIE = "v23.49";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 1. afleiders van dezelfde woordsoort ----------
    OUD = '''function peilOpties(w){
  var goed = wTrans(w);
  /* v23.49: de afleiders moeten in dezelfde taal staan als het goede antwoord. Zonder deze filter
     kreeg een Engelse bezoeker "the garden" naast "de badkamer" en "blauw", en dan raad je niet op
     betekenis maar op taal. */
  var pool = WORDS.filter(function(x){ return x.id !== w.id && wTrans(x) !== goed && woordVertaald(x); });
  var zelfde = pool.filter(function(x){ return x.tag === w.tag; });
  var bron = zelfde.length >= 3 ? zelfde : pool;'''

    NIEUW_CODE = '''/* v23.50: de woordsoort, afgeleid uit het Spaans en niet uit de vertaling. Het Spaans is er altijd
   en is regelmatiger: een lidwoord ervoor maakt het een zelfstandig naamwoord, één woord op
   -ar/-er/-ir is een werkwoord (infinitief), meer dan één woord zonder lidwoord is een uitdrukking.
   Grof, maar het hoeft alleen goed genoeg te zijn om te voorkomen dat het juiste antwoord het enige
   van zijn soort is. */
function woordSoort(w){
  try {
    var es = String(w.es || "").split("/")[0].split("(")[0].trim();
    if(/^(el|la|los|las|un|una)\\s/i.test(es)) return "zn";
    if(/[?¿]/.test(es)) return "vraag";
    if(/\\s/.test(es)) return "uitdrukking";
    if(/(ar|er|ir)$/i.test(es)) return "ww";
    return "rest";
  } catch(e){ return "rest"; }
}
function peilOpties(w){
  var goed = wTrans(w);
  /* v23.49: de afleiders moeten in dezelfde taal staan als het goede antwoord. Zonder deze filter
     kreeg een Engelse bezoeker "the garden" naast "de badkamer" en "blauw", en dan raad je niet op
     betekenis maar op taal. */
  var pool = WORDS.filter(function(x){ return x.id !== w.id && wTrans(x) !== goed && woordVertaald(x); });
  /* v23.50. Stefan zag "el jardín" met "de badkamer", "hoeveel kost het?" en "blauw" ernaast: een
     kamer, een vraag en een kleur. Je hoeft het woord dan niet te kennen om het eruit te pikken.
     Gemeten: bij 30 van de 200 vragen was het goede antwoord het enige van zijn woordsoort.
     De oude regel viel bij een tag met weinig woorden meteen terug op de hele bak van 2184; nu is
     er een tussenstap. Volgorde: zelfde tag én soort, dan zelfde soort, dan zelfde tag, dan pas
     alles. */
  var mijnSoort = woordSoort(w);
  var zelfdeSoort = pool.filter(function(x){ return woordSoort(x) === mijnSoort; });
  var zelfdeTag = pool.filter(function(x){ return x.tag === w.tag; });
  var beide = zelfdeTag.filter(function(x){ return woordSoort(x) === mijnSoort; });
  var bron = beide.length >= 3 ? beide
           : (zelfdeSoort.length >= 3 ? zelfdeSoort
           : (zelfdeTag.length >= 3 ? zelfdeTag : pool));'''
    rep(OUD, NIEUW_CODE)

    # ---------- 2. de uitslag belooft geen verschil dat er niet is ----------
    rep('     start:function(l){ return "Je begint op "+l+"."; },',
        '''     /* v23.50: hier stond "Je begint op A1." A0 en A1 hebben allebei data-track="beginner" en
        het veld lvl wordt nergens bewaard, dus ze leveren exact dezelfde app op: dezelfde woorden,
        zinnen en lessen. Alleen A2 is een ander pad (grote bak plus niveauClaim). Een uitslag die
        onderscheid maakt waar de app dat niet doet, is een belofte die je niet nakomt. */
     start:function(l){ return l === "A2"
       ? "Je slaat de basis over en begint op A2."
       : "Je begint bij het begin, bij les 1."; },''')
    rep('     start:function(l){ return "You start at "+l+"."; },',
        '''     start:function(l){ return l === "A2"
       ? "You skip the basics and start at A2."
       : "You start at the beginning, at lesson 1."; },''')

    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
