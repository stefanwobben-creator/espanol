#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.56: v23.50 en v23.51 alsnog, want ze zijn bij het herbouwen van de tak overgeslagen.

Wat er gebeurde: na de botsing met de avondrun is de tak opnieuw opgebouwd door de zes patches over
de index van de avondrun te draaien. Vier daarvan pakten, twee niet. De poort in CI ging rood op
shard 1, en nagemeten op de gepushte index (30ea03b):

    function woordSoort            0 keer   <- v23.50 ontbreekt
    "v23.51: de knoppen stonden"   0 keer   <- v23.51 ontbreekt
    "v23.52: hier stond alleen"    1 keer
    var GC_ORDE                    8 keer
    id="laadScherm"                1 keer
    function vroegVraag            1 keer
    Brujer                         1 keer   <- de avondrun staat er wel in

Twee rode suites, en het is één oorzaak:

  - `pw-helling.js` viel om in een evaluate die `woordSoort()` aanroept, en die functie bestond niet.
  - `pw-zintegels.js` meldde "de knoppenrij staat direct onder de uitslag (uitslag 0, knoppen 3)",
    en dat is precies de oude volgorde van vóór v23.51.

Deze patch zet die twee er alsnog in, met ankers die passen op wat er nú staat. Inhoudelijk is het
woord voor woord hetzelfde als v23.50 en v23.51; alleen het versieanker verschilt, want dat staat
inmiddels op v23.55.

## Wat v23.50 deed (Stefan, telefoontest 11 aug)

"Ik denk dat op basis van de toets A1 ook te hoog is ingeschaald, omdat je veel woorden (bijna de
helft) wel een beetje kunt raden." Gemeten op 200 getrokken vragen: bij **30 (15%)** was het goede
antwoord het enige van zijn woordsoort. Zijn voorbeeld was *el jardín* met *de badkamer*, *hoeveel
kost het?* en *blauw* ernaast: een kamer, een vraag en een kleur.

`peilOpties()` koos afleiders uit dezelfde `tag` alleen als er drie beschikbaar waren, en viel
anders terug op de hele bak van 2184 woorden. Nu is de volgorde: zelfde tag én soort, dan zelfde
soort, dan zelfde tag, dan pas alles. De soort wordt uit het Spaans afgeleid en niet uit de
vertaling, want het Spaans is er altijd en is regelmatiger.

En de uitslag belooft geen onderscheid meer dat er niet is: A0 en A1 hebben allebei
`data-track="beginner"` en `lvl` wordt nergens bewaard, dus ze leveren exact dezelfde app op.

## Wat v23.51 deed (bevinding 3)

"Je controleert, resultaat is goed of fout, maar dan moet je zelf op de knop volgende zin klikken,
dat vind je niet." Na Check stond eerst de uitslag, dan de uitleg, dan de luisterknoppen, en pas
daaronder de knop. Op 390 pixels valt die onder de vouw. Nu: uitslag, knoppen, uitleg,
luisterknoppen. Bewust géén automatische doorloop.

## Les voor de volgende keer

De patches falen luid als een anker ontbreekt (`sys.exit(1)` met een melding), maar in een blok van
zes achter elkaar scrollt zo'n melding voorbij. Draai ze één voor één, of kijk naar de exitcode.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.56"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_50 = "function woordSoort" not in src
DOE_51 = "v23.51: de knoppen stonden" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_50 and not DOE_51 and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

OUD_PEIL = '''function peilOpties(w){
  var goed = wTrans(w);
  /* v23.49: de afleiders moeten in dezelfde taal staan als het goede antwoord. Zonder deze filter
     kreeg een Engelse bezoeker "the garden" naast "de badkamer" en "blauw", en dan raad je niet op
     betekenis maar op taal. */
  var pool = WORDS.filter(function(x){ return x.id !== w.id && wTrans(x) !== goed && woordVertaald(x); });
  var zelfde = pool.filter(function(x){ return x.tag === w.tag; });
  var bron = zelfde.length >= 3 ? zelfde : pool;'''

OUD_FB = '''  html += "<div class='uitleg'><b>"+ct("Waarom:","Why:")+"</b> "+zinUitleg(s)+"</div>";
  // De juiste zin staat nu in beeld. Dit is het enige moment waarop horen hoe hij klinkt iets
  // toevoegt: je weet wat er staat en wat het betekent, dus je hoort de uitspraak en niet een raadsel.
  html += "<div class='row' style='margin-top:6px'>"+ct("<span class='muted' style='font-size:.85rem; align-self:center'>Zo klinkt hij:</span>","<span class='muted' style='font-size:.85rem; align-self:center'>This is how it sounds:</span>")+zinLuisterKnopHtml()+"</div>";
  html += "<div class='row'>"+
    (retryable ? "<button class='primary' id='btnRetry'>"+ct("Probeer opnieuw","Try again")+"</button>"+
                 "<button class='ghost' id='btnAiCheck'>🤖 "+ct("Is mijn variant ook goed?","Is my version also correct?")+"</button>"+
                 "<button class='ghost' id='btnNext'>"+ct("Volgende zin →","Next sentence →")+"</button>"
               : "<button class='primary' id='btnNext'>"+ct("Volgende zin →","Next sentence →")+"</button><button class='ghost' id='btnAiUitleg'>🤖 "+ct("Meer uitleg","More explanation")+"</button>")+
    "</div><div id='aiFb'></div>";'''

ontbreekt = []
if DOE_50:
    for a in [OUD_PEIL, '     start:function(l){ return "Je begint op "+l+"."; },',
              '     start:function(l){ return "You start at "+l+"."; },']:
        if a not in src:
            ontbreekt.append(a)
if DOE_51 and OUD_FB not in src:
    ontbreekt.append(OUD_FB)

if ontbreekt:
    print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
          "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
          "\n\nEerst bijtrekken, dan pas patchen:\n\n    git pull --rebase\n")
    sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_50:
    # ---------- v23.50, deel 1: afleiders van dezelfde woordsoort ----------
    rep(OUD_PEIL, '''/* v23.50: de woordsoort, afgeleid uit het Spaans en niet uit de vertaling. Het Spaans is er altijd
   en is regelmatiger: een lidwoord ervoor maakt het een zelfstandig naamwoord, één woord op
   -ar/-er/-ir is een werkwoord (infinitief), meer dan één woord zonder lidwoord is een uitdrukking.
   Grof, maar het hoeft alleen goed genoeg te zijn om te voorkomen dat het juiste antwoord het enige
   van zijn soort is. */
function woordSoort(w){
  try {
    var es = String(w.es || "").split("/")[0].split("(")[0].trim();
    if(/^(el|la|los|las|un|una)\\s/i.test(es)) return "zn";
    if(/[?\\u00bf]/.test(es)) return "vraag";
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
           : (zelfdeTag.length >= 3 ? zelfdeTag : pool));''')

    # ---------- v23.50, deel 2: de uitslag belooft geen verschil dat er niet is ----------
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
    print("v23.50 alsnog toegepast")
else:
    print("v23.50 stond er al")

if DOE_51:
    # ---------- v23.51: de knop staat waar je hem zoekt ----------
    rep(OUD_FB, '''  /* v23.51: de knoppen stonden hier onderaan, ná de uitleg en de luisterknoppen, en op een telefoon
     van 390 pixels valt dat onder de vouw. Stefan: "je controleert, resultaat is goed of fout, maar
     dan moet je zelf op de knop volgende zin klikken, dat vind je niet." De volgorde eronder klopte
     wel (horen hoe het klinkt heeft pas zin als je weet wat er staat), maar de handeling hoort niet
     achter de toelichting. Uitslag, dan wat je nu kunt doen, dan waarom.

     Bewust geen automatische doorloop: dan pak je het moment af waarop je de zin nog kunt horen, en
     dat moment staat er met opzet. Het probleem was dat je de knop niet zag, niet dat je erop moest
     tikken. */
  html += "<div class='row'>"+
    (retryable ? "<button class='primary' id='btnRetry'>"+ct("Probeer opnieuw","Try again")+"</button>"+
                 "<button class='ghost' id='btnAiCheck'>🤖 "+ct("Is mijn variant ook goed?","Is my version also correct?")+"</button>"+
                 "<button class='ghost' id='btnNext'>"+ct("Volgende zin →","Next sentence →")+"</button>"
               : "<button class='primary' id='btnNext'>"+ct("Volgende zin →","Next sentence →")+"</button><button class='ghost' id='btnAiUitleg'>🤖 "+ct("Meer uitleg","More explanation")+"</button>")+
    "</div>";
  html += "<div class='uitleg'><b>"+ct("Waarom:","Why:")+"</b> "+zinUitleg(s)+"</div>";
  // De juiste zin staat nu in beeld. Dit is het enige moment waarop horen hoe hij klinkt iets
  // toevoegt: je weet wat er staat en wat het betekent, dus je hoort de uitspraak en niet een raadsel.
  html += "<div class='row' style='margin-top:6px'>"+ct("<span class='muted' style='font-size:.85rem; align-self:center'>Zo klinkt hij:</span>","<span class='muted' style='font-size:.85rem; align-self:center'>This is how it sounds:</span>")+zinLuisterKnopHtml()+"</div>";
  html += "<div id='aiFb'></div>";''')
    print("v23.51 alsnog toegepast")
else:
    print("v23.51 stond er al")

if DOE_50 or DOE_51:
    # het versienummer los, want de avondrun kan het onderweg hebben opgehoogd en dan is een
    # hard anker op een bepaalde versie precies wat er hierboven misging
    import re
    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
