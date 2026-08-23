#!/usr/bin/env python3
# v23.180 - de undefined op de opfrisser, en zes knoppen worden er twee
#
# Stefan, 23 aug, met twee schermafdrukken: "dit lijkt een bug 'undefined'" en "hier zijn veel te
# veel knoppen opties voor een lekkere flow".
#
# A. DE UNDEFINED
#
# Op de opfrisser stond "undefined Even opfrissen". renderGramWiz() zet o.icon vóór de stapkop, en
# gcOpfrisOnderwerp() bouwt zijn eigen onderwerp-object zonder icon-veld. Elk concept heeft er wel
# een (serestar is 🪞), dus de opfrisser hoort dat van zijn concept over te nemen.
#
# Twee reparaties, want één is te weinig: het icoon erbij, én de render die nooit meer "undefined"
# kan tonen. Zonder dat tweede staat het er de volgende keer weer zodra iemand een onderwerp bouwt
# dat één veld mist, en dat is precies wat hier gebeurde.
#
# B. ZES KNOPPEN
#
# Na een fout antwoord op de schrijfstap stonden er zes bedieningen op één scherm: het overtypvak
# met "Klaar", "Probeer opnieuw", "Is mijn variant ook goed?", "Volgende zin", "Oefen <regel>", plus
# "Hoor hem". Twee daarvan waren primair gekleurd. Dat is geen keuze meer maar een menu.
#
# Wat de leerkaart van de correctielaag hierover al zei, en wat toen niet is doorgevoerd:
#
#   "Standaard is een recast met verhoogde salience. Eén actieve stap erna: hij typt de goede zin
#    één keer over. Dat is de pushed output waar de prompt-theorie het werkzame deel legt, zonder de
#    gokfase. Wat ik afwijs is de raadronde: die kost tijd, beloont voorzichtig schrijven, en het
#    bewijs voor zijn meerwaarde is betwist."
#
# "Probeer opnieuw" ís die raadronde. Hij is niet weggehaald toen het overtypvak erbij kwam, dus nu
# staan de afgewezen en de gekozen aanpak naast elkaar, allebei in het primair.
#
# Wat er verandert:
#   - het overtypvak krijgt de primaire knop, en die brengt je bij een goed antwoord meteen naar de
#     volgende zin. Dat is de afspraak van v23.60: "er moet altijd een knop zijn die controleert en
#     dan automatisch doorgaat."
#   - "Volgende zin" blijft ernaast staan als stille knop, want overtypen is een aanbod en geen poort.
#   - "Probeer opnieuw", "Is mijn variant ook goed?" en "Oefen <regel>" verhuizen naar één regel
#     "meer opties", dichtgeklapt. Niets weggehaald, alles één tik verder weg.
#
# Van zes bedieningen naar twee zichtbare knoppen en één regel. Eén primair.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.180"

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

# ---------------------------------------------------------------- A. de undefined
if DOE_APP:
    rep(
        '  var naam = ct(c.naam, c.naamEn || c.naam);\n'
        '  return {\n'
        '    id: id, concept: cid, opfris: true,',
        '  var naam = ct(c.naam, c.naamEn || c.naam);\n'
        '  return {\n'
        '    /* v23.180: het icoon stond hier niet, en renderGramWiz() zet o.icon vóór de stapkop.\n'
        '       Op het scherm stond dus letterlijk "undefined Even opfrissen". Het concept heeft er\n'
        '       een, dus die nemen we over: de opfrisser is hetzelfde onderwerp in het klein. */\n'
        '    icon: c.icon || "\\ud83d\\udd01",\n'
        '    id: id, concept: cid, opfris: true,')

    rep(
        '    "<h2>"+o.icon+" "+ct(stap.kop, stap.kopEn)+"</h2>"+',
        '    /* v23.180: en hier het vangnet. Een onderwerp zonder icoon hoort geen "undefined" op te\n'
        '       leveren maar gewoon een kop zonder icoon. Eén ontbrekend veld mag nooit zichtbaar zijn\n'
        '       voor de leerling; dat is precies wat hier weken heeft gestaan. */\n'
        '    "<h2>"+(o.icon ? o.icon+" " : "")+ct(stap.kop, stap.kopEn)+"</h2>"+')

# ---------------------------------------------------------------- B. de knoppenrij
if DOE_APP:
    rep(
        '      "<div class=\'row\' style=\'margin-top:6px\'><button class=\'ghost\' id=\'btnOverTyp\'>"+\n'
        '        ct("Klaar","Done")+"</button></div>"+',
        '      "<div class=\'row\' style=\'margin-top:6px\'><button class=\'primary\' id=\'btnOverTyp\'>"+\n'
        '        ct("Klaar \\u2192","Done \\u2192")+"</button></div>"+')

    rep(
        '  html += "<div class=\'row\'>"+\n'
        '    (retryable ? "<button class=\'primary\' id=\'btnRetry\'>"+ct("Probeer opnieuw","Try again")+"</button>"+\n'
        '    (fregel ? "<button class=\'ghost\' id=\'btnFoutRegel\'>\\ud83d\\udcd8 "+ct("Oefen "+fregel.naam,"Practise "+fregel.naam)+"</button>" : "")+\n'
        '                 "<button class=\'ghost\' id=\'btnAiCheck\'>🤖 "+ct("Is mijn variant ook goed?","Is my version also correct?")+"</button>"+\n'
        '                 "<button class=\'ghost\' id=\'btnNext\'>"+ct("Volgende zin →","Next sentence →")+"</button>"\n'
        '               : "<button class=\'primary\' id=\'btnNext\'>"+ct("Volgende zin →","Next sentence →")+"</button><button class=\'ghost\' id=\'btnAiUitleg\'>🤖 "+ct("Meer uitleg","More explanation")+"</button>")+\n'
        '    "</div>";',
        '  /* v23.180: één primair, en de rest een tik verder weg.\n'
        '\n'
        '     Stefan, 23 aug: "hier zijn veel te veel knoppen opties voor een lekkere flow." Er stonden\n'
        '     er zes op één scherm, waarvan twee primair gekleurd: overtypen en Probeer opnieuw.\n'
        '\n'
        '     Dat die twee naast elkaar staan is geen smaakkwestie maar een niet-doorgevoerd besluit.\n'
        '     De leerkaart van de correctielaag koos de recast plus één overtypbeurt en wees de\n'
        '     raadronde af ("kost tijd, beloont voorzichtig schrijven, en het bewijs voor zijn\n'
        '     meerwaarde is betwist"). "Probeer opnieuw" ís die raadronde; hij is alleen nooit\n'
        '     weggehaald toen het overtypvak erbij kwam. Hij verdwijnt hier niet, want een besluit\n'
        '     terugdraaien mag niet stiekem: hij gaat achter "meer opties".\n'
        '\n'
        '     Bij een goed antwoord blijft alles zoals het was: daar staat één primaire knop en dat was\n'
        '     nooit het probleem. */\n'
        '  html += "<div class=\'row\'>"+\n'
        '    (retryable ? "<button class=\'ghost\' id=\'btnNext\'>"+ct("Volgende zin →","Next sentence →")+"</button>"\n'
        '               : "<button class=\'primary\' id=\'btnNext\'>"+ct("Volgende zin →","Next sentence →")+"</button><button class=\'ghost\' id=\'btnAiUitleg\'>🤖 "+ct("Meer uitleg","More explanation")+"</button>")+\n'
        '    "</div>";\n'
        '  if(retryable){\n'
        '    html += "<details class=\'meerOpties\' style=\'margin-top:8px\'>"+\n'
        '      "<summary class=\'muted\' style=\'font-size:.9rem; cursor:pointer\'>"+\n'
        '        ct("meer opties","more options")+"</summary>"+\n'
        '      "<div class=\'row\' style=\'margin-top:8px\'>"+\n'
        '        "<button class=\'ghost\' id=\'btnRetry\'>"+ct("Probeer opnieuw","Try again")+"</button>"+\n'
        '        (fregel ? "<button class=\'ghost\' id=\'btnFoutRegel\'>\\ud83d\\udcd8 "+ct("Oefen "+fregel.naam,"Practise "+fregel.naam)+"</button>" : "")+\n'
        '        "<button class=\'ghost\' id=\'btnAiCheck\'>🤖 "+ct("Is mijn variant ook goed?","Is my version also correct?")+"</button>"+\n'
        '      "</div></details>";\n'
        '  }')

    # de overtypknop gaat door naar de volgende zin
    rep(
        '      fbo.style.color = goed ? "var(--goed, #2e7d32)" : "";\n'
        '      if(goed) iot.disabled = true;\n'
        '    };',
        '      fbo.style.color = goed ? "var(--goed, #2e7d32)" : "";\n'
        '      /* v23.180: goed overgetypt is het einde van deze zin, dus dan gaan we door. Dat is de\n'
        '         afspraak van v23.60 ("er moet altijd een knop zijn die controleert en dan automatisch\n'
        '         doorgaat naar volgende"), en die gold nog niet voor het overtypvak van v23.168. Even\n'
        '         wachten zodat je "Ja, zo is het" nog leest; zonder die pauze voelt het als wegspringen. */\n'
        '      if(goed){\n'
        '        iot.disabled = true;\n'
        '        setTimeout(function(){\n'
        '          var bn = document.getElementById("btnNext");\n'
        '          if(bn) bn.click();\n'
        '        }, 900);\n'
        '      }\n'
        '    };')

# ---------------------------------------------------------------- schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar " + NIEUW)
else:
    print("index.html: stond al op " + NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
