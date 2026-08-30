#!/usr/bin/env python3
# v23.211 - de zin die je fout deed vertelt nu waarom juist die fout blijft plakken
#
# Stefan, 30 aug: "ja door maar, bepaal zelf wat de goede volgorde is."
#
# WAAROM DEZE RONDE EERST
#
# De grote schilronde (de hoofdknop naar de onderbalk, de uitslag als blad) raakt 101 knoppen en 58
# feedbackblokken, en het feedbackblok van de zinnenoefening is een scherm waar sinds v23.57 vier
# keer bewust aan gesleuteld is. Dat is geen eerste stap.
#
# De tegelregel (een zin die je ooit fout had gaat naar tegels) wacht op zijn eigen meting:
# zinRouteStand() verzamelt sinds v23.205 wie er beter werkt, en die reeks is drie dagen oud.
#
# Wat wél nu kan, en precies raakt waar Stefan zich zorgen over maakt ("grammatica maken en zinnen
# maken gaat nog niet zo goed"): het moment van de fout meer laten zeggen. Twee dingen, allebei
# data plus een handvol regels.
#
# 1. HET VELD DAT OP DE VERKEERDE PLEK STOND
#
# Elk grammaticaconcept draagt een zin over waarom juist die fout hardnekkig is. Bij reflexivo:
#
#     "Se blijft vaak staan omdat je het werkwoord zo geleerd hebt: levantarse. Maar se hoort alleen
#      bij hij, zij, u en zij-meervoud, nooit bij een ik-vorm."
#
# Alle 31 concepten hebben er een, 84 tot 211 tekens lang. Ze staan alle 31 in de naslagtekst van de
# microles, dus je leest ze op het moment dat je iets naslaat en nooit op het moment dat je precies
# die fout maakt. In het prototype van 30 augustus stond die zin in het rode blad zodra je in de val
# liep, en dat is waar hij hoort.
#
# checkSentence() vindt de regel achter je fout al (foutRegel), noemt hem al, en zet het concept al
# op doosje 0. De zin erbij is drie regels.
#
# 2. VIER CONCEPTEN DIE ZWEGEN
#
# foutRegel() werkt met woordparen: jij schreef de ene, er hoorde de andere. Van de 31 concepten
# hebben er 12 geen enkel paar, en vier daarvan hebben ze wel degelijk:
#
#     tijdmarkers   hace / desde / durante
#     imperativo    habla-hable, come-coma, ven-viene, haz-hace, pon-pone, sal-sale
#     cortesia      podría-puedes, quisiera-quiero
#     posesivo      mi-mío, su-suyo, tu-tuyo
#
# Maak je die fout in een zin, dan zei de app tot nu toe alleen "Nog niet" met het verschil erbij.
# Nu noemt hij de regel, zet hij het concept op doosje 0 voor morgen, en zegt hij waarom die fout
# blijft terugkomen.
#
# DE ACHT DIE BLIJVEN ZWIJGEN, EN WAAROM DAT KLOPT
#
# perfindef en apersonal zijn een woord meer of minder: dan schuift de hele zin op en ziet een
# woord-voor-woordvergelijking vijf verschillen in plaats van één keuze. concordancia en gerundio
# zijn niet te onderscheiden van een tikfout. seimpersonal en gustarfamilie hebben alleen paren die
# al bij gustar staan. cantidad overlapt met muymucho. En exclamacion zou qué-cómo willen, maar dat
# paar is al van comparar, en foutRegel neemt de eerste treffer: een tweede eigenaar zou nooit aan
# de beurt komen. Een regel toevoegen die per constructie niet kan vuren is erger dan geen regel.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.211"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = 'cid:"tijdmarkers"' not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:120])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. vier concepten die nu wel te herkennen zijn
# =============================================================================================
if DOE_APP:
    rep("""  /* De klassieke uitkomst van "de klinker wisselt niet mee": een leerling schrijft de stam van de
     infinitief. Dit is de enige plek waar de tabel een vorm bevat die geen goed Spaans is, en dat
     hoort zo: het is precies de vorm die je typt als je de regel niet kent. */""",
"""  /* v23.211: vier concepten die tot nu toe zwegen terwijl ze wel degelijk schone paren hebben.
     Maakte je deze fout in een zin, dan zei de app alleen "Nog niet" met het verschil erbij; nu
     noemt hij de regel en zet hij het onderwerp op doosje 0 voor morgen.

     Wat hier bewust NIET bij staat en waarom, zodat niemand het later alsnog "vergeten" noemt:
     exclamacion zou qué-cómo willen, maar dat paar is al van comparar en foutRegel neemt de eerste
     treffer, dus een tweede eigenaar komt per constructie nooit aan de beurt. gustarfamilie en
     seimpersonal hebben alleen paren die al bij gustar staan, en cantidad overlapt met muymucho. */
  {cid:"tijdmarkers", p:[["hace","desde"],["hace","durante"],["desde","durante"]]},
  /* de tú-gebiedende wijs tegenover de derde persoon: habla (spreek!) tegenover hable (spreekt u).
     Bewust zonder di-dice: "di" is ook de verleden tijd van dar, en dan zou de app een tijdfout
     aanzien voor een gebiedende wijs. Een verkeerde diagnose is erger dan geen. */
  {cid:"imperativo", p:[["habla","hable"],["come","coma"],["escribe","escriba"],
                        ["ven","viene"],["haz","hace"],["pon","pone"],["sal","sale"]]},
  {cid:"cortesia", p:[["podria","puedes"],["podrias","puedes"],["podria","puedo"],
                      ["quisiera","quiero"],["quisiera","quisiste"]]},
  /* mi tegenover mio: het bezittelijk voornaamwoord voor het zelfstandig naamwoord tegenover de
     zelfstandige vorm erachter. tu-usted en tuyo-suyo staan al bij tuusted; dit zijn andere paren
     en botsen er dus niet mee. */
  {cid:"posesivo", p:[["mi","mio"],["mis","mios"],["tu","tuyo"],["su","suyo"],
                      ["nuestro","nuestros"],["mi","mia"]]},
  /* De klassieke uitkomst van "de klinker wisselt niet mee": een leerling schrijft de stam van de
     infinitief. Dit is de enige plek waar de tabel een vorm bevat die geen goed Spaans is, en dat
     hoort zo: het is precies de vorm die je typt als je de regel niet kent. */""")

# =============================================================================================
# 2. de zin die zegt waarom juist die fout blijft plakken
# =============================================================================================
if DOE_APP:
    rep("""      ct("Je schreef "+fgG+" waar "+fgV+" hoort. Dat is geen woordje dat je miste maar een keuze, en daar hoort een regel bij: <b>"+fregel.naam+"</b>.",
         "You wrote "+fgG+" where "+fgV+" belongs. That is not a word you were missing but a choice, and there is a rule behind it: <b>"+fregel.naam+"</b>.")+"</p>";
  }""",
"""      ct("Je schreef "+fgG+" waar "+fgV+" hoort. Dat is geen woordje dat je miste maar een keuze, en daar hoort een regel bij: <b>"+fregel.naam+"</b>.",
         "You wrote "+fgG+" where "+fgV+" belongs. That is not a word you were missing but a choice, and there is a rule behind it: <b>"+fregel.naam+"</b>.")+"</p>";
    /* v23.211: en waarom juist die fout blijft terugkomen.

       Elk concept draagt zo'n zin (het veld `mis` in GC_HULP), alle 31, tussen de 84 en 211 tekens.
       Bij reflexivo: "Se blijft vaak staan omdat je het werkwoord zo geleerd hebt: levantarse."
       Ze stonden alle 31 in de naslagtekst van de microles, dus je las ze op het moment dat je iets
       naslaat en nooit op het moment dat je precies die fout maakte.

       Dit is geen nieuwe inhoud, alleen een andere plek. De feedback-meta-analyses gaan precies
       hierover: informatie over de taak op het moment dat hij ergens over gaat, in plaats van
       bekrachtiging achteraf. */
    var fmis = "";
    try { fmis = gcHulpTekst(gcHulp(fregel.cid), "mis"); } catch(e){ fmis = ""; }
    if(fmis){
      html += "<p class='muted' style='margin:6px 2px 0; font-size:.9rem'>" + veiligHtml(fmis) + "</p>";
    }
  }""")

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    for cid in ["tijdmarkers", "imperativo", "cortesia", "posesivo"]:
        assert src.count('cid:"%s"' % cid) == 1, cid
    assert src.count('gcHulpTekst(gcHulp(fregel.cid), "mis")') == 1
    APP.write_text(src, encoding="utf-8")
    print("index.html: vier concepten spreken, en de fout zegt waarom hij blijft plakken")
else:
    print("index.html: stond er al")

if DOE_VER:
    a = APP.read_text(encoding="utf-8")
    b = a.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    assert a != b, "APP_VERSIE niet gevonden op " + huidig_ver
    APP.write_text(b, encoding="utf-8")
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: %s -> %s" % (huidig_ver, NIEUW))
else:
    print("versie.txt: stond al op " + huidig_ver)
