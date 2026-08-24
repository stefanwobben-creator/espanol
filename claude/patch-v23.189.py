#!/usr/bin/env python3
# v23.189 - de opfrisser laat zien wat JIJ antwoordde
#
# Stefan, 24 aug: "Bij opfrissen laat ie niet het goede of foute antwoord zien maar gaat ie
# automatisch direct door naar volgende." En daarna, op mijn vraag of het misgaat bij goed of bij
# fout: "dat weet ik niet meer."
#
# WAT IK HEB NAGEMETEN, EN WAT ERUIT KWAM
#
# Twee verklaringen voor "gaat automatisch door", allebei doodgelopen:
#
#   1. Een automatische doorschuiver in de code. Bestaat niet. gwVolgende() en gwVolgendeStap()
#      worden nergens vanzelf aangeroepen; ze hangen allebei aan een onclick en aan niets anders.
#   2. De knop landt onder je vinger, zodat een tweede tik doorschiet. Nagemeten op tien opfrissers
#      maal goed en fout, in een venster van 420 bij 880: de afstand tussen de onderkant van de knop
#      waarop je klikte en de bovenkant van "Volgende" is minimaal 97 pixels en gemiddeld 148. Geen
#      enkele overlap.
#
# Dus dat deel kan ik niet reproduceren en ik ga er niet naar raden.
#
# MAAR DE EERSTE HELFT VAN ZIJN ZIN IS WEL WAAR, EN DAT IS TE ZIEN
#
# Twee schermen in deze app stellen dezelfde vraag en tonen het antwoord anders.
#
#   het toetsje (answerQuestion)   opts[v.c].classList.add("correct")    het juiste antwoord groen
#                                  btn.classList.add("wrong")            JOUW antwoord rood
#
#   de opfrisser (renderCheat)     i === q.g ? "primary" : "ghost"       alleen het juiste, oranje
#                                                                        jouw antwoord: niets
#
# In de opfrisser staat dus nergens op het scherm wát je hebt geantwoord. Bij twee opties met één
# oranje knop is niet te zien of die oranje knop de jouwe is of juist de andere. Vergelijk Stefans
# eigen twee schermafdrukken: in het toetsje staat "saltó, rompió" groen en "saltaba, rompía" rood,
# in de opfrisser staat "viajé" oranje en "viajaba" gewoon wit.
#
# "Laat niet het goede of foute antwoord zien" is daarmee letterlijk waar, en het is dezelfde fout
# die in deze repo vaker langskwam: twee stukken code die toevallig over hetzelfde gaan, en die uit
# elkaar zijn gelopen.
#
# WAT ER VERANDERT
#
# De opfrisser krijgt dezelfde twee klassen als het toetsje: groen voor het juiste antwoord, rood
# voor jouw antwoord als dat een ander was. Hij houdt zijn eigen knopvorm (gw-optie is geen .opt),
# dus de kleuren komen mee in twee regels CSS die naar dezelfde variabelen wijzen.
#
# Geen nieuwe kleuren en geen nieuwe woorden: precies wat het toetsje al doet, op het scherm waar
# het nog niet gebeurde.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.189"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "gw-optie.jouw" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

# ---------------------------------------------------------------- 1. de twee kleuren
if DOE_APP:
    rep("  .opt.wrong{border-color:var(--red); background:var(--red-soft); color:var(--red);}",
        "  .opt.wrong{border-color:var(--red); background:var(--red-soft); color:var(--red);}\n"
        "  /* v23.189: dezelfde twee kleuren voor de opfrisser. Die markeerde alleen het juiste\n"
        "     antwoord, en niet dat van jou, dus bij twee opties was niet te zien welke van de twee\n"
        "     je had aangetikt. Het toetsje doet dit al sinds jaar en dag met .correct en .wrong; dit\n"
        "     zijn dezelfde variabelen op een knop die geen .opt is. */\n"
        "  .gw-optie.juist{border-color:var(--green); background:var(--green-soft); color:var(--green); font-weight:700;}\n"
        "  .gw-optie.jouw{border-color:var(--red); background:var(--red-soft); color:var(--red);}")

# ---------------------------------------------------------------- 2. en ze worden gezet
if DOE_APP:
    rep(
        '      opties.map(function(t, i){\n'
        '        var klasse = "ghost";\n'
        '        if(beantwoord && i === q.g) klasse = "primary";\n'
        '        return "<button type=\'button\' class=\'"+klasse+" gw-optie\' data-gwo=\'"+i+"\' "+(beantwoord?"disabled ":"")+"style=\'text-align:left\'>"+t+"</button>";\n'
        '      }).join("")+"</div>";',
        '      opties.map(function(t, i){\n'
        '        /* v23.189: twee dingen tegelijk zichtbaar, precies zoals het toetsje het doet. Hier\n'
        '           stond alleen "het juiste antwoord wordt primary", dus jouw eigen keuze liet geen\n'
        '           spoor achter en met twee opties was de oranje knop niet thuis te brengen. */\n'
        '        var klasse = "ghost gw-optie";\n'
        '        if(beantwoord && i === q.g) klasse += " juist";\n'
        '        else if(beantwoord && i === gwSess.gekozen) klasse += " jouw";\n'
        '        return "<button type=\'button\' class=\'"+klasse+"\' data-gwo=\'"+i+"\' "+(beantwoord?"disabled ":"")+"style=\'text-align:left\'>"+t+"</button>";\n'
        '      }).join("")+"</div>";')

# ---------------------------------------------------------------- schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: de opfrisser markeert ook jouw antwoord, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
