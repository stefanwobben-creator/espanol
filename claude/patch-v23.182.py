#!/usr/bin/env python3
# v23.182 - Cádiz eruit, Don Quijote erin
#
# Stefan, 23 aug: "cadiz mag er uit." En: "ik denk dat een hoofdstuk nu een heel boek kan zijn, doe
# dat en daarna gaan we door met geschiedenis. Maar doen 1 boek per week, want ik moet veel lezen."
# En daarna: "lengte zoals boek van chispa of franco is eigenlijk perfect."
#
# WAT DAT SAMEN BETEKENT, GEMETEN
#
#   reeks    hoofdstukken  gemiddeld  totaal
#   Chispa             13       1304   16.957
#   Franco             10        794    7.940
#   El hilo            10        819    8.192
#   Cádiz               8       1185    9.478
#
# El hilo de las palabras heeft dus al precies de maat van Franco. Dat is prettig nieuws: die reeks
# ÍS al een boek van de goede lengte, en de tien klassiekers daarin zijn de inhoudsopgave van wat er
# nog komt. Elk van die tien hoofdstukken kan uitgroeien tot een eigen boek van tien hoofdstukken.
#
# Dit is het eerste: Don Quijote, tien hoofdstukken, gemiddeld 950 tekens. Eén boek per week, dus dit
# is de leesstof van de komende week; het volgende boek komt daarna.
#
# WAT ERUIT GAAT
#
# Un año en Cádiz: acht hoofdstukken en zijn plek op de plank. Reden staat in het projectdoc "De
# leesregel": elke leesreeks heeft een tweede vak, en Cádiz heeft er geen. Nagemeten voordat er iets
# verdween: nul woorden en nul zinnen dragen een cadiz-tag, dus er hangt geen woordenschat aan.
#
# De acht mp3's blijven staan in audio/boek/. Weggooien levert niets op (ze staan al in git en in het
# manifest) en een verwijderde opname die later toch nodig blijkt kost tekens om terug te krijgen.
#
# EN DE ROMMEL DIE ACHTERBLIJFT
#
# Stefan heeft voortgang op cadiz-hoofdstukken staan in S.boek. Als die hoofdstukken verdwijnen
# blijven er sleutels achter die naar niets wijzen. Dat is precies de fout die migratie 2 voor de
# luistersleutels heeft opgeruimd ("ze maakten van Luisteren 55 van de 6"), en die hier weer zou
# ontstaan. Dus komt er een migratie mee die S.boek opruimt: alles wat niet in BOOK staat gaat eruit.
#
# Die migratie is met opzet algemeen en niet cadiz-specifiek. Er verdwijnt vaker een hoofdstuk, en
# een opruiming die één keer een lijst met namen bevat is de volgende keer weer verouderd.
import re, pathlib, json, runpy

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.182"

H = runpy.run_path(str(W / "claude" / "hoofdstukken-quijote.py"))["H"]
assert len(H) == 10, "verwacht tien hoofdstukken, kreeg %d" % len(H)

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "quij-1" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

def js(s):
    return json.dumps(s, ensure_ascii=False)

DEEL = "Don Quijote"

def hoofdstuk(h):
    r = [' {id:"quij-%d", num:%d, deel:"%s", titel:%s, drempel:0,'
         % (h["num"], h["num"], DEEL, js(h["titel"]))]
    r.append('  tekst:%s,' % js(h["tekst"]))
    vr = ['   {q:%s,\n    opts:[%s], c:%d}'
          % (js(v["q"]), ", ".join(js(o) for o in v["opts"]), v["c"]) for v in h["vragen"]]
    r.append('  vragen:[\n%s\n  ],' % ",\n".join(vr))
    r.append('  reflectie:%s},' % js(h["reflectie"]))
    return "\n".join(r)

# ---------------------------------------------------------------- 1. Cádiz eruit
if DOE_APP:
    start = src.index(' {id:"cadiz-1", num:1, deel:"Un año en Cádiz"')
    eind = src.index(' {id:"receta-1", num:1, deel:"La cocina española"')
    weg = src[start:eind]
    assert weg.count('deel:"Un año en Cádiz"') == 8, \
        "verwacht acht Cádiz-hoofdstukken, vond %d" % weg.count('deel:"Un año en Cádiz"')
    assert 'id:"receta' not in weg and 'id:"lit-' not in weg, "de snede pakt te veel mee"
    src = src[:start] + src[eind:]

    # en de reeks van de plank
    r0 = src.index(' {id:"cadiz", pre:"cadiz-"')
    r1 = src.index(' {id:"letras", pre:"lit-"')
    tussen = src[r0:r1]
    assert tussen.count('{id:"') == 1, "de snede op de plank pakt te veel mee"
    src = src[:r0] + src[r1:]

    # het commentaarblok dat alleen over Cádiz ging staat er nog boven; dat mag mee
    src = src.replace(
        ' /* v23.162: de acht hoofdstukken van v23.157 stonden wel in BOOK maar op geen enkele plank, want\n'
        '    de plank zoekt op id-voorvoegsel en er was geen reeks met pre:"cadiz-". Ze telden mee in je\n'
        '    leesvoortgang en waren nergens te vinden. */\n'
        ' /* Dezelfde verteller en dus dezelfde map als Chispa: het manifest houdt de stem per map bij,\n'
        '     dus een eigen map zou betekenen dat je een tweede stem moet kiezen voordat er iets klinkt. */\n',
        ' /* v23.182: Un año en Cádiz stond hier. Eruit op verzoek van Stefan, en met een reden die nu een\n'
        '    regel is: elke leesreeks heeft een tweede vak. Chispa geeft filosofie, Franco geschiedenis, La\n'
        '    cocina española koken. Cádiz gaf niets; iemand komt aan, kijkt rond en went. De acht opnames\n'
        '    blijven in audio/boek/ staan, want weggooien levert niets op en terughalen kost tekens. */\n')

# ---------------------------------------------------------------- 2. Don Quijote erin
if DOE_APP:
    blok = ("\n /* ================= DON QUIJOTE (v23.182) =================\n"
            "    Het eerste van de tien klassiekers dat een heel boek wordt. Tien hoofdstukken, gemiddeld\n"
            "    950 tekens: tussen Franco (794) en Chispa (1304) in, en dat is de maat die Stefan noemde.\n\n"
            "    Tweede vak: literatuur, met binnen dit boek één doorlopende vraag. Is het beter de wereld\n"
            "    te zien zoals hij is, of zoals je wilt dat hij is? Het boek kiest niet. In hoofdstuk 10\n"
            "    keert de vraag zich om: als hij eindelijk gelijk krijgt van iedereen, wil niemand het. */\n"
            + "\n".join(hoofdstuk(h) for h in H) + "\n")
    rep(' {id:"receta-1", num:1, deel:"La cocina española"',
        blok + ' {id:"receta-1", num:1, deel:"La cocina española"')

    rep(' {id:"letras", pre:"lit-",',
        ' /* v23.182: Don Quijote, het eerste van de tien uitgewerkt tot een eigen boek. Dezelfde map en\n'
        '    dus dezelfde verteller als Chispa en El hilo: het manifest houdt de stem per map bij, en een\n'
        '    eigen map zou betekenen dat er eerst een stem gekozen moet worden voordat er iets klinkt. */\n'
        ' {id:"quijote", pre:"quij-", nl:"Don Quijote", en:"Don Quijote", stem:true, map:"boek",\n'
        '  soortNl:"verhaal", soortEn:"story",\n'
        '  omNl:"Een man leest zoveel over ridders dat hij er zelf een wordt. Tien hoofdstukken, van de molens tot de laatste ochtend.",\n'
        '  omEn:"A man reads so much about knights that he becomes one. Ten chapters, from the windmills to the last morning."},\n'
        ' {id:"letras", pre:"lit-",')

# ---------------------------------------------------------------- 3. de opruiming
if DOE_APP:
    rep(
        '    return weg;\n'
        '  }}\n'
        '];',
        '    return weg;\n'
        '  }},\n'
        '  {naar: 3, wat: "leessleutels opruimen die naar een verdwenen hoofdstuk wijzen", doe: function(s){\n'
        '    /* v23.182: Un año en Cádiz is eruit gegaan, en wie die hoofdstukken had gelezen houdt\n'
        '       sleutels in S.boek over die naar niets meer wijzen. Dat is exact de fout die migratie 2\n'
        '       voor de luistersleutels opruimde: ze telden mee en niemand zag waarom het getal niet\n'
        '       klopte.\n\n'
        '       Met opzet algemeen en niet op naam. Er verdwijnt vaker een hoofdstuk, en een opruiming\n'
        '       met een lijstje namen erin is de volgende keer alweer verouderd. */\n'
        '    if(typeof BOOK === "undefined" || !s.boek) return 0;\n'
        '    var geldig = {}, weg = 0;\n'
        '    BOOK.forEach(function(h){ geldig[h.id] = 1; });\n'
        '    Object.keys(s.boek).forEach(function(id){\n'
        '      if(!geldig[id]){ delete s.boek[id]; weg++; }\n'
        '    });\n'
        '    return weg;\n'
        '  }}\n'
        '];')

    # SCHEMA mee omhoog, anders draait de migratie nooit
    rep("var SCHEMA = 2;",
        "/* v23.182: 3, want er is een migratie bij gekomen. Blijft dit getal staan, dan denkt elke\n"
        "   bestaande state dat hij bij is en draait migratie 3 nooit. */\nvar SCHEMA = 3;")

# ---------------------------------------------------------------- schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: Cádiz eruit, Don Quijote erin, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
