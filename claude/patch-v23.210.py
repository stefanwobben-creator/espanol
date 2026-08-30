#!/usr/bin/env python3
# v23.210 - alles wat je aanraakt is minstens 44 bij 44
#
# Stefan, 30 aug: "voer maar door", en daarna "ja ga door".
#
# WAT ER GEMETEN IS
#
# Alle zichtbare tikdoelen op alle zeventien schermen, 390 pixels breed, alle lessen open,
# gegroepeerd op klasse in plaats van geteld op een hoop:
#
#   klasse        n    <44   hoog      voorbeeld
#   primary      69     69   42-43     "Start je les →"
#   ghost        55     25   39-93     "Iemand laten meekijken"
#   tapachip     18     18   32        de tapa's van Chispa
#   bailechip     8      8   26        "💃 la salsa"
#   dtegel        7      7   39        de woordtegels van een zin
#   kleurknop     6      6   38        de kleuren van Chispa
#   mini          4      4   25        "↔ Andersom oefenen"
#   modus-toets   2      2   25        "🧩 Tegels"
#   btn           1      1   21        "Inleveren"
#   instelrij     1      1   23        "⚙️ Instellingen"
#   muziekchip    1      1   20        "🔊 muziek staat aan"
#
#   totaal 189 tikdoelen, waarvan 152 onder de 44.
#
# Dat is de reden dat groeperen vóór verbouwen moest. Ik dacht dat dit honderdvijftig losse plekken
# waren; het zijn er elf, en de grootste twee (primary en ghost, samen 124 van de 152) missen maar
# één tot vijf pixels. Dat zijn twee CSS-regels.
#
# DE GRENS, EN WAAROM 44
#
# Apple houdt 44 bij 44 aan, Google 48. Ik neem 44 als eis in de poort en 48 als richting voor de
# knoppen die er ruim in passen. Een grens die je haalt is beter dan een grens die je noemt.
#
# WAT DEZE RONDE DOET
#
#   primary, ghost, good, bad   min-height 48. Ze staan op 42-43, dus dit is vijf pixels en geen
#                               nieuwe indeling. Samen 124 van de 152 te kleine doelen.
#   dtegel                      min-height 44. Dit zijn de tegels die je tijdens een oefening
#                               aanraakt; 39 is precies het formaat waarop je de verkeerde raakt.
#   mini, modus-toets, btn      min-height 44 met wat lucht eromheen. Kleine tekstknoppen die tot nu
#   instelrij                   toe alleen zo groot waren als hun letters.
#   tapachip, bailechip         min 44 bij 44. Dit zijn rasters, dus ze vloeien gewoon opnieuw uit.
#   kleurknop                   44 bij 44 in plaats van 38 bij 38.
#   muziekchip                  min-height 44.
#
# En een proef die de grens vasthoudt, want anders zakt hij binnen drie versies weer weg. Die staat
# in test/suites/pw-tikdoel.js en loopt langs alle zeventien schermen.
#
# WAT DEZE RONDE NIET DOET
#
# De hoofdknop naar de onderbalk brengen en het uitslagblad bouwen. Dat is 101 keer class='primary'
# en 58 feedbackblokken, en dat is een verbouwing per oefensoort. Deze ronde raakt alleen maten.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.210"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "TIKDOEL_MIN" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:120])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de twee grote groepen
# =============================================================================================
if DOE_APP:
    rep("""  button.primary{background:var(--accent); color:#fff; border:none; padding:12px 20px; border-radius:10px;
                 font-size:1rem; font-weight:700; cursor:pointer;}
  button.primary:active{transform:scale(.98);}
  button.ghost{background:var(--card); color:var(--ink); border:1.5px solid var(--border); padding:11px 18px;
               border-radius:10px; font-size:.95rem; font-weight:600; cursor:pointer;}
  button.good{background:var(--green); color:#fff; border:none; padding:12px 20px; border-radius:10px; font-weight:700; font-size:1rem; cursor:pointer;}
  button.bad{background:var(--red-soft); color:var(--red); border:1.5px solid var(--red); padding:12px 20px; border-radius:10px; font-weight:700; font-size:1rem; cursor:pointer;}""",
"""  /* ================= DE MAAT VAN EEN TIKDOEL (v23.210) =================
     Gemeten over alle zeventien schermen: 189 tikdoelen, waarvan 152 onder de 44 pixels. Ik dacht
     dat dat honderdvijftig losse plekken waren; gegroepeerd op klasse zijn het er elf, en de twee
     grootste (primary en ghost, samen 124 van de 152) misten één tot vijf pixels.

     Apple houdt 44 bij 44 aan, Google 48. De poort eist 44 (zie pw-tikdoel.js) en deze knoppen
     krijgen 48, want daar passen ze ruim in. Een grens die je haalt is beter dan een grens die je
     noemt.

     min-height en geen height: een knop met twee regels tekst moet gewoon meegroeien. */
  button.primary, button.ghost, button.good, button.bad{
    min-height:48px; display:inline-flex; align-items:center; justify-content:center;
  }
  button.primary{background:var(--accent); color:#fff; border:none; padding:12px 20px; border-radius:10px;
                 font-size:1rem; font-weight:700; cursor:pointer;}
  button.primary:active{transform:scale(.98);}
  button.ghost{background:var(--card); color:var(--ink); border:1.5px solid var(--border); padding:11px 18px;
               border-radius:10px; font-size:.95rem; font-weight:600; cursor:pointer;}
  button.good{background:var(--green); color:#fff; border:none; padding:12px 20px; border-radius:10px; font-weight:700; font-size:1rem; cursor:pointer;}
  button.bad{background:var(--red-soft); color:var(--red); border:1.5px solid var(--red); padding:12px 20px; border-radius:10px; font-weight:700; font-size:1rem; cursor:pointer;}""")

# =============================================================================================
# 2. de tegels van een zin
# =============================================================================================
if DOE_APP:
    rep("""  .dtegel{padding:9px 13px; border-radius:9px; border:1.5px solid var(--border); background:var(--card);
       color:var(--ink); font-size:1rem; font-family:inherit; cursor:pointer; line-height:1.2;}""",
"""  /* v23.210: 39 pixels hoog is precies het formaat waarop je met een duim de tegel ernaast raakt,
     en dit zijn de tegels die je tijdens een oefening aanraakt. Ook min-width, want een tegel met
     een kort woordje erop (de, y, a) was maar dertig pixels breed. */
  .dtegel{padding:9px 13px; border-radius:9px; border:1.5px solid var(--border); background:var(--card);
       color:var(--ink); font-size:1rem; font-family:inherit; cursor:pointer; line-height:1.2;
       min-height:44px; min-width:44px; display:inline-flex; align-items:center; justify-content:center;}""")

# =============================================================================================
# 3. de kleine tekstknoppen
# =============================================================================================
if DOE_APP:
    rep("""  button.mini{background:none; border:none; padding:5px 0; margin:6px 0 0; color:var(--muted);
              font-size:.85rem; font-weight:600; text-decoration:underline; cursor:pointer;
              font-family:inherit; display:block;}""",
"""  /* v23.210: 25 pixels hoog, en dat is precies de knop waar je twee keer naar tikt. De padding gaat
     omhoog in plaats van de letters, zodat de regel er hetzelfde uitziet en het doel groter is. */
  button.mini{background:none; border:none; padding:11px 0; margin:2px 0 0; color:var(--muted);
              font-size:.85rem; font-weight:600; text-decoration:underline; cursor:pointer;
              font-family:inherit; display:flex; align-items:center; min-height:44px;}""")

    rep("""  .instelrij{display:flex; align-items:center; justify-content:space-between; gap:10px; width:100%;
             padding:2px 0; background:none; border:none; color:var(--ink); font-weight:700;
             font-size:1rem; cursor:pointer; text-align:left;}""",
"""  .instelrij{display:flex; align-items:center; justify-content:space-between; gap:10px; width:100%;
             padding:2px 0; background:none; border:none; color:var(--ink); font-weight:700;
             font-size:1rem; cursor:pointer; text-align:left;
             min-height:44px;}   /* v23.210: was 23 hoog */""")

# =============================================================================================
# 4. de chips van Chispa. Rasters, dus ze vloeien gewoon opnieuw uit.
# =============================================================================================
if DOE_APP:
    rep("""  .tapachip{font-size:1.15rem; line-height:1; padding:6px 8px; border-radius:10px; border:1px solid var(--border);
    background:var(--card); cursor:pointer; filter:grayscale(1); opacity:.35;}""",
"""  /* v23.210: 32 bij 32 was te klein om te raken, en dit zijn er achttien naast elkaar. Ze staan in
     een raster, dus ze vloeien gewoon opnieuw uit. */
  .tapachip{font-size:1.15rem; line-height:1; padding:6px 8px; border-radius:10px; border:1px solid var(--border);
    background:var(--card); cursor:pointer; filter:grayscale(1); opacity:.35;
    min-width:44px; min-height:44px; display:inline-flex; align-items:center; justify-content:center;}""")

    rep("""  .bailechip{font-size:.74rem; font-weight:700; border:1.5px solid var(--border); background:var(--card); color:var(--muted);
             border-radius:999px; padding:5px 10px; cursor:pointer; transition:transform .12s ease;}""",
"""  .bailechip{font-size:.74rem; font-weight:700; border:1.5px solid var(--border); background:var(--card); color:var(--muted);
             border-radius:999px; padding:5px 10px; cursor:pointer; transition:transform .12s ease;
             min-height:44px; display:inline-flex; align-items:center;}   /* v23.210: was 26 hoog */""")

    rep("""  .kleurknop{width:38px; height:38px; border-radius:50%; border:3px solid var(--border); cursor:pointer; padding:0; position:relative;}""",
"""  .kleurknop{width:44px; height:44px; border-radius:50%; border:3px solid var(--border); cursor:pointer; padding:0; position:relative;}   /* v23.210: was 38 */""")

# =============================================================================================
# 4b. drie doelen die buiten de tabbladen wonen, en die mijn eerste meting daarom miste
# =============================================================================================
if DOE_APP:
    rep("""  .zoekpil{display:flex; align-items:center; gap:6px; flex:0 0 auto; cursor:pointer;
           height:34px; padding:0 12px; border-radius:99px; border:1.5px solid var(--border);""",
"""  /* v23.210: 34 hoog. Deze woont in de kop en viel daardoor buiten mijn eerste meting, die per
     tabblad keek; pw-tikdoel.js loopt langs het hele document en vond hem alsnog. */
  .zoekpil{display:flex; align-items:center; gap:6px; flex:0 0 auto; cursor:pointer;
           min-height:44px; padding:0 12px; border-radius:99px; border:1.5px solid var(--border);""")

    rep("""  .chbalkop{flex:0 0 auto; width:32px; height:32px; border-radius:999px; cursor:pointer;""",
"""  /* v23.210: was 32 bij 32, en dit is de enige weg van de zwevende balk naar Chispa zelf. */
  .chbalkop{flex:0 0 auto; width:44px; height:44px; border-radius:999px; cursor:pointer;""")

    rep("""  .appfooter a{color:var(--muted); text-decoration:none; border-bottom:1px dotted var(--muted);}""",
"""  /* v23.210: zestien pixels hoog, en het zijn wel degelijk knoppen: rondleiding, uitleg, privacy.
     inline-block met lucht eromheen, zodat de regel hetzelfde leest en het doel groter is. */
  .appfooter a{color:var(--muted); text-decoration:none; border-bottom:1px dotted var(--muted);
               display:inline-block; min-height:44px; line-height:44px; padding:0 4px;}""")


# =============================================================================================
# 5. de rest, met een vangnet dat zichzelf noemt
# =============================================================================================
if DOE_APP:
    rep("""  .row{display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;}""",
"""  /* v23.210: de losse eindjes. modus-toets, btn en muziekchip zijn elk één of twee knoppen, te
     weinig voor een eigen verhaal en te klein om te laten staan. TIKDOEL_MIN staat hier als
     leesbaar getal zodat de proef en de stijl dezelfde grens noemen. */
  .modus-toets, button.btn, .muziekchip{min-height:44px; display:inline-flex; align-items:center;}
  .row{display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;}""")

    # het getal ook in de code, zodat de proef er niet zijn eigen versie van maakt
    rep("var TABS = [", "var TIKDOEL_MIN = 44;   // v23.210: Apple houdt 44 bij 44 aan; zie pw-tikdoel.js\nvar TABS = [")

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    assert src.count("TIKDOEL_MIN") == 2   # de var en de toelichting erboven
    assert src.count("min-height:48px") == 1
    APP.write_text(src, encoding="utf-8")
    print("index.html: alles wat je aanraakt is minstens 44 bij 44")
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
