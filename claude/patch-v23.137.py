#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.137: jouw andere woord is geen fout meer, het is een vraag.

Stefan, 20 aug: "of ik gebruik een alternatief woord wat goed is."

## Wat er stond

De controle vergelijkt je zin met `s.es` en met `s.alt`. Gemeten over de 231 zinnen: elke zin heeft
alternatieven, gemiddeld 2,1, maximaal 5. Maar als je kijkt wát die alternatieven zijn, zijn het
accentvarianten en cijfervarianten van dezelfde zin ("nació" / "nacio" / "1907" / "mil novecientos
siete"). Er zit geen enkel synoniem tussen, en dat kan ook niet: je kunt geen lijst maken van alle
goede manieren om een zin te zeggen.

Een geldig alternatief woord werd dus per definitie fout gerekend.

## En de knop die het al kon

Dit is de correctie op mijn eigen gap-analyse van vanochtend: `/api/ai/check` bestaat, is
aangesloten, en er staat een knop onder een fout antwoord: "🤖 Is mijn variant ook goed?". Hij was
dus niet afwezig. Het probleem is de volgorde:

  1. je zin wordt fout gerekend
  2. `logError(s.id, "zin", ...)` schrijft de fout weg
  3. de ladder van v23.136 zakt
  4. en dán mag je zelf vragen of het toch goed was

Je moest zelf bedenken dat je gelijk had, en de knop vinden. De regel eronder zei letterlijk: "Denk
je dat jouw variant ook goed Spaans is? Kan zomaar. Vraag het in de les of aan Claude."

## Wat er nu staat

Bij een bijna-treffer (hoogstens twee woorden anders, en minstens de helft klopt) vraagt de app het
uit zichzelf. Je ziet:

    Zó dichtbij! 1 woord wijkt af: ... · 🤖 ik vraag even na of jouw variant ook goed is

en een tel later of het goed was, met de reden erbij.

**De ladder wacht op het antwoord.** Dat is het enige dat is uitgesteld: `vertBij()` wordt pas
aangeroepen als de uitslag er is. Zonder dat zou een geldige variant je een trede kosten en zou de
correctie te laat komen.

Wat NIET is uitgesteld: het foutenlogboek en `gramBij`. Die blijven synchroon, want de suites die
ze bewaken meten meteen na `checkSentence()`, en een geldige variant haalt de fout er alsnog uit via
`foutWeg()` (dat deed de knop sinds v23.94 al). De grammaticaregistratie blijft staan bij een
geldige variant; dat is een oneffenheid die ik hier bewust laat liggen en niet vergeet.

**De knop blijft**, maar alleen als vangnet. Is het model onbereikbaar, dan komt hij terug zodat je
het later nog eens kunt vragen. Is het antwoord binnen, dan is er niets meer te vragen.

## Waarom bij twijfel fout

De prompt op de server zegt al "wees streng op grammatica maar accepteer natuurlijke alternatieven".
Daar komt bij dat dit nu automatisch draait op elke bijna-treffer in plaats van alleen als je erom
vraagt. Een model dat te aardig is, keurt dan structureel goed wat fout is, en dan leer je niets van
de oefening. De regel staat er nu expliciet bij in de prompt.

Bewaakt door test/suites/pw-variant.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")
PAD_SRV = os.path.join(WORTEL, "server", "index.js")

NIEUW = "v23.137"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = NIEUW not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ------------- 1. de bijna-treffer wacht op het oordeel in plaats van het al te vellen

rep(
    '''      html = "<div class='feedback bijna'>"+ct("Zó dichtbij! "+d.m+" woord"+(d.m>1?"en":"")+" wijkt af (onderstreept): ","So close! "+d.m+" word"+(d.m>1?"s":"")+" differ"+(d.m>1?"":"s")+" (underlined): ")+"<b>"+d.html+"</b> (+2 "+xpw()+")</div>"+
        "<p class='muted' style='margin-top:6px'>"+ct("Denk je dat jouw variant ook goed Spaans is? Kan zomaar: er zijn vaak meer goede vertalingen. Vraag het in de les of aan Claude.","Think your version might also be correct Spanish? Quite possible: there are often several good translations. Ask in class or ask Claude.")+"</p>";
      addXP(2); retryable = true;
      logError(s.id, "zin", s.tag, given);''',
    '''      /* v23.137. Hier stond: "Denk je dat jouw variant ook goed Spaans is? Kan zomaar: er zijn vaak
         meer goede vertalingen. Vraag het in de les of aan Claude." Dat is de app die weet dat hij
         het antwoord niet zeker weet, en de vraag doorschuift naar jou. Nu vraagt hij het zelf, en
         wacht de ladder op de uitslag. Zie zinAiCheck(). */
      html = "<div class='feedback bijna'>"+ct("Zó dichtbij! "+d.m+" woord"+(d.m>1?"en":"")+" wijkt af (onderstreept): ","So close! "+d.m+" word"+(d.m>1?"s":"")+" differ"+(d.m>1?"":"s")+" (underlined): ")+"<b>"+d.html+"</b> (+2 "+xpw()+")</div>"+
        "<p class='muted' style='margin-top:6px' id='zinVraagt'>🤖 "+
          ct("Ik vraag even na of jouw variant ook goed is...","Let me check whether your version is also correct...")+"</p>";
      addXP(2); retryable = true; vertWacht = true;
      logError(s.id, "zin", s.tag, given);''',
)

# ------------- 2. de ladder wacht

rep(
    '''  /* v23.136: de ladder beweegt op de eerste poging van deze zin, en zegt het als hij beweegt.
     Boven de uitleg en onder de knoppen: het is een mededeling over morgen, geen uitslag van nu. */
  if(!zinGeteld){ zinGeteld = true; vTrap = vertBij(gehaald); }''',
    '''  /* v23.136: de ladder beweegt op de eerste poging van deze zin, en zegt het als hij beweegt.
     Boven de uitleg en onder de knoppen: het is een mededeling over morgen, geen uitslag van nu.
     v23.137: behalve bij een bijna-treffer. Dan staat de vraag "is dit ook goed?" nog open, en een
     ladder die alvast zakt zou een geldige variant een trede kosten. */
  if(!zinGeteld && !vertWacht){ zinGeteld = true; vTrap = vertBij(gehaald); }''',
)

rep(
    '''var zinGeteld = false;
function renderSentence(fresh){
  if(fresh || sIdx===null){ sIdx = pickSentence(); zinGeteld = false; }''',
    '''var zinGeteld = false;
/* v23.137: er loopt een vraag aan het model over deze zin, dus de ladder wacht. */
var vertWacht = false;
function renderSentence(fresh){
  if(fresh || sIdx===null){ sIdx = pickSentence(); zinGeteld = false; }
  vertWacht = false;''',
)

# ------------- 3. de check als functie, en hij gaat vanzelf

rep(
    '''  var ba = document.getElementById("btnAiCheck");
  if(ba) ba.onclick = function(){
    ba.disabled = true; ba.textContent = "🤖 Claude denkt na...";
    api("/api/ai/check", "POST", {nl:s.nl, verwacht:s.es, gegeven:rauw}).then(function(res){
      var af = document.getElementById("aiFb");
      if(!af) return;
      if(!res || !res.ok){''',
    '''  /* v23.137: één functie, twee aanroepers. Hij ging alleen op een tik; nu gaat hij vanzelf bij een
     bijna-treffer, en blijft de knop als vangnet voor het geval het model niet bereikbaar is.
     De ladder wordt hier afgehandeld en nergens anders: vertWacht staat aan, dus checkSentence()
     heeft hem overgeslagen. */
  function zinAiKlaar(goed){
    if(!vertWacht) return;
    vertWacht = false;
    if(zinGeteld) return;
    zinGeteld = true;
    var t = vertBij(goed);
    var af = document.getElementById("aiFb");
    if(af && t && t.na !== t.voor) af.innerHTML += vertTredeHtml(t);
  }
  var ba = document.getElementById("btnAiCheck");
  function zinAiCheck(){
    if(ba){ ba.disabled = true; ba.textContent = "🤖 Claude denkt na..."; }
    var vraagt = document.getElementById("zinVraagt");
    api("/api/ai/check", "POST", {nl:s.nl, verwacht:s.es, gegeven:rauw}).then(function(res){
      if(vraagt && vraagt.parentNode) vraagt.parentNode.removeChild(vraagt);
      var af = document.getElementById("aiFb");
      if(!af){ zinAiKlaar(false); return; }
      if(!res || !res.ok){
        zinAiKlaar(false);''',
)

rep(
    '''        af.innerHTML = "<div class='feedback bijna'>\\ud83e\\udd16 "+aiFoutTekst(res)+"</div>";
        if(aiNogEensZin(res)){ ba.disabled=false; ba.textContent="🤖 Is mijn variant ook goed?"; }
        else { ba.classList.add("hidden"); }
        return;
      }
      if(res.goed){''',
    '''        af.innerHTML = "<div class='feedback bijna'>\\ud83e\\udd16 "+aiFoutTekst(res)+"</div>";
        if(ba){
          if(aiNogEensZin(res)){ ba.disabled=false; ba.textContent="🤖 Is mijn variant ook goed?"; }
          else { ba.classList.add("hidden"); }
        }
        return;
      }
      zinAiKlaar(!!res.goed);
      if(res.goed){''',
)

rep(
    '''      } else {
        af.innerHTML = "<div class='feedback fout'>🤖 Claude: helaas, niet helemaal. "+veiligHtml(res.uitleg)+"</div>";
      }
      ba.classList.add("hidden");
    });
  };''',
    '''      } else {
        af.innerHTML = "<div class='feedback fout'>🤖 Claude: helaas, niet helemaal. "+veiligHtml(res.uitleg)+"</div>";
      }
      if(ba) ba.classList.add("hidden");
    });
  }
  if(ba) ba.onclick = zinAiCheck;
  /* Vanzelf, en alleen bij een bijna-treffer. Bij een antwoord dat er helemaal naast zit valt er
     niets te vragen, en dan is een modelaanroep alleen wachttijd. */
  if(vertWacht) zinAiCheck();''',
)

# ------------- 4. de bug die de knop al die tijd stukmaakte

rep(
    """  var given = norm(document.getElementById("sInput").value || "");
  if(!given) return;""",
    """  /* v23.137: hier stond alleen `given` (genormaliseerd). De ruwe tekst werd pas onderaan gelezen,
     ná fb.innerHTML en ná zinInvoerDicht(), en die laatste vervangt de innerHTML van #sInvoer,
     waar #sInput in zit. Op dat moment bestaat het invoerveld niet meer en was `rauw` dus altijd
     leeg. De knop "Is mijn variant ook goed?" stuurde daardoor een leeg antwoord naar de server, en
     die antwoordt daarop met 400 "nl en gegeven verplicht". De knop was stuk, en niemand kon dat
     zien: je kreeg gewoon een foutmelding van de AI te zien.
     Nu wordt de ruwe tekst gelezen op hetzelfde moment als `given`, want dat is het enige moment
     waarop hij er zeker nog staat. */
  var rauw = document.getElementById("sInput").value || "";
  var given = norm(rauw);
  if(!given) return;""",
)

rep(
    """  var rauw = document.getElementById("sInput") ? document.getElementById("sInput").value : "";
""",
    """""",
)

# ------------- 5. de server: bij twijfel fout, want dit draait nu vanzelf

if os.path.exists(PAD_SRV):
    with io.open(PAD_SRV, encoding="utf-8") as f:
        srv = f.read()
    oud = ('"Wees streng op grammatica maar accepteer natuurlijke alternatieven '
           '(andere woordvolgorde, synoniemen, weglaten van onderwerp). "')
    nieuw = ('"Wees streng op grammatica maar accepteer natuurlijke alternatieven '
             '(andere woordvolgorde, synoniemen, weglaten van onderwerp). " +\n      '
             '"Bij twijfel: goed=false. Deze check draait automatisch bij elk bijna-goed antwoord, '
             'dus te soepel goedkeuren maakt de oefening waardeloos. " +\n      '
             '"Zeg in de uitleg altijd of jouw variant de gewoonste keuze is of alleen ook mogelijk. "')
    if nieuw not in srv:
        assert srv.count(oud) == 1, "server-anker komt %d keer voor" % srv.count(oud)
        srv = srv.replace(oud, nieuw, 1)
        with io.open(PAD_SRV, "w", encoding="utf-8") as f:
            f.write(srv)
        print("server/index.js: de check is strenger bij twijfel")

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
