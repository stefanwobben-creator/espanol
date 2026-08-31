#!/usr/bin/env python3
# v23.219 - de trede tussen één woord en de hele tekst
#
# Stefan, 31 aug: "ik vind de tekst nog te moeilijk hoor, begrijp de grote lijn maar heb nog DeepL
# nodig." En daarna, gevraagd of het per zin of per alinea moest: "per alinea denk ik."
#
# WAT ER MIS WAS, EN HET WAS NIET WAT IK DACHT
#
# Ik had eerst gemeten dat de teksten juist makkelijk waren: met alle lesswoorden in de doosjes komt
# leesBetekenis() op ongeveer 0,05 onbekende woorden per zin. Dat klopt ook, en het is het verkeerde
# getal. Stefan kent de woorden en snapt de zin nog niet, en dat is iets anders.
#
# Een hoofdstuk had deze velden: id, num, deel, titel, drempel, tekst, vragen, reflectie. Geen
# vertaling. Nergens. Het leesscherm kon precies één ding: tik op een woord, krijg dat woord. Er was
# geen trede tussen "één woord" en "de hele tekst", dus liep je bij een zin die je niet rond kreeg
# de app uit naar DeepL.
#
# EN DAAR KOMT HET ANDERE GETAL VANDAAN
#
# Uit Stefans eigen nachtelijke logboek, over alle onderdelen:
#
#     woord 334   zin 130   quiz 81   gramwiz 50   conj 40   corrector 22   escucha 4   LEZEN 0
#     gezien.lezen: 20 bezoeken
#
# Twintig keer op die pagina, en nul signaal terug. Lezen was het enige onderdeel waar de app niets
# van hem leerde, en dus ook het enige waar hij niet kon sturen. Elke keer dat je naar DeepL gaat is
# een meting die de app misloopt.
#
# WAT DEZE RONDE DOET
#
# 1. Een hoofdstuk krijgt `vert`: één Nederlandse regel per Spaanse alinea, in dezelfde volgorde.
#    De reeks "España: los años de Franco" (hist-1 t/m hist-10, 54 alinea's) is helemaal vertaald.
#    De andere vier reeksen hebben nog niets, en dat is geen half werk maar het ontwerp: staat er
#    geen vertaling, dan staat er ook geen knopje. Zo kan de rest er per reeks bij zonder dat er
#    ooit een knop is die niets doet.
#
# 2. Per alinea een klein knopje dat de Nederlandse regel eronder zet. Bewust per alinea en niet per
#    zin: per zin lees je algauw regel voor regel in het Nederlands mee, en dan is het Spaans
#    versiering geworden. Per alinea moet je hem eerst zelf proberen.
#
# 3. Elke tik wordt geteld, per hoofdstuk, in S.leesVert. Dít is de eigenlijke opbrengst. Nul tikken
#    in een hoofdstuk betekent te makkelijk, een tik op elke alinea betekent te zwaar, en daartussen
#    zit waar je iets leert. Dat is een maat uit gedrag in plaats van uit een woordenlijst, en die
#    heeft de app nooit gehad.
#
# 4. S.leesZoek en S.leesVert gaan mee naar de server. leesZoek telt sinds v23.21 elke opzoeking en
#    stond in geen enkel logje; hij werd dus wel geschreven en door niemand gelezen.
#
# WAT DEZE RONDE NIET DOET
#
# Sturen. Stefan wil dat de app hem naar de goede reeks stuurt, en dat kan pas als er metingen zijn.
# leesZwaarte() is aantoonbaar kapot (hij telt vervoegde vormen als onbekend en zet daardoor alle
# vijf de reeksen op "zwaar"), maar hem repareren met woordenlijsten zou hetzelfde soort getal
# opleveren als hij nu geeft. Na een week of twee lezen staat er echte data, en dan pas is sturen
# een meting en geen gok.
import re, pathlib, json

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
VERT = W / "claude" / "vert-hist.json"
NIEUW = "v23.219"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()
vert = json.loads(VERT.read_text(encoding="utf-8"))

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function leesVertHtml(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)

def _blok(start, o, s):
    d = 0; i = start; inStr = None; esc = False
    while i < len(src):
        c = src[i]
        if inStr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == inStr: inStr = None
            i += 1; continue
        if c in "\"'":
            inStr = c; i += 1; continue
        if c == o: d += 1
        elif c == s:
            d -= 1
            if d == 0: return i
        i += 1
    raise AssertionError("ongebalanceerd blok")

# =============================================================================================
# 1. de vertalingen in de hoofdstukken
# =============================================================================================
if DOE_APP:
    ids = [k for k in vert if not k.startswith("_")]
    for hid in sorted(ids, key=lambda x: int(x.split("-")[1])):
        a = src.index('{id:"%s"' % hid)
        eind = _blok(a, "{", "}")
        blok = src[a:eind + 1]
        # het aantal Spaanse alinea's uit de bron zelf halen, niet aannemen
        mt = re.search(r'tekst:\s*((?:"(?:[^"\\]|\\.)*"\s*\+?\s*)+)', blok)
        assert mt, "geen tekst in " + hid
        stukken = re.findall(r'"((?:[^"\\]|\\.)*)"', mt.group(1))
        tekst = "".join(stukken).replace("\\n", "\n").replace('\\"', '"')
        paras = [p for p in tekst.split("\n\n") if p.strip()]
        nl = vert[hid]
        assert len(paras) == len(nl), "%s: %d Spaanse alinea's, %d Nederlandse" % (hid, len(paras), len(nl))
        regels = ",\n   ".join(json.dumps(x, ensure_ascii=False) for x in nl)
        nieuw = blok[:-1].rstrip() + ",\n  vert:[\n   " + regels + "\n  ]}"
        src = src[:a] + nieuw + src[eind + 1:]
    print("index.html: %d hoofdstukken hebben nu een Nederlandse regel per alinea" % len(ids))

# =============================================================================================
# 2. het knopje, de onthulling en de telling
# =============================================================================================
if DOE_APP:
    rep("""function leesTekstHtml(p){""",
"""/* ================= DE TREDE TUSSEN ÉÉN WOORD EN DE HELE TEKST (v23.219) =================

   Stefan: "ik begrijp de grote lijn maar heb nog DeepL nodig." Het leesscherm kon precies één
   ding: tik op een woord, krijg dat woord. Wie de woorden kent en de zin niet rond krijgt, had
   hier niets, en ging dus de app uit.

   Per ALINEA en niet per zin, en dat is Stefans eigen keuze met de goede reden erbij: per zin lees
   je algauw regel voor regel in het Nederlands mee, en dan is het Spaans versiering geworden.

   De tik is niet alleen een dienst maar ook de meting. Lezen was het enige onderdeel waar de app
   niets van je terugkreeg (twintig bezoeken, nul fouten, nul opzoekingen in het logboek), en
   daarom kon geen enkel niveau-etiket ooit kloppen. Nul tikken in een hoofdstuk betekent te
   makkelijk, een tik op elke alinea betekent te zwaar. */
function leesVertHtml(h, i){
  var v = h && h.vert;
  if(!v || !v[i]) return "";
  return "<div class='leesvert'>" +
    "<button type='button' class='leesvertknop' data-vert='" + i + "'>" +
    ct("Nederlands", "Dutch") + "</button>" +
    "<p class='leesvertnl weg' data-vertnl='" + i + "'>" + veiligHtml(v[i]) + "</p></div>";
}
/* Per hoofdstuk bijhouden WELKE alinea's je hebt opengeklapt, niet hoe vaak je tikte. Twee keer op
   dezelfde alinea is dezelfde alinea, en anders meet je driftig tikken in plaats van moeite. */
function leesVertBij(h, i){
  if(!h || !h.id) return;
  try {
    S.leesVert = S.leesVert || {};
    var r = S.leesVert[h.id] || (S.leesVert[h.id] = {});
    if(r[i]) return;
    r[i] = today();
    persist();
  } catch(e){}
}
/* Hoeveel van de alinea's van dit hoofdstuk heb je vertaald willen zien. Dit getal is de bedoeling
   van deze hele ronde; het sturen dat erop volgt komt pas als er een week of twee data ligt. */
function leesVertStand(h){
  try {
    var r = (S.leesVert || {})[h.id] || {};
    var n = Object.keys(r).length;
    var totaal = (h.vert || []).length;
    return {n:n, totaal:totaal};
  } catch(e){ return {n:0, totaal:0}; }
}
function leesTekstHtml(p){""")

    rep("""  var paras = h.tekst.split("\\n\\n").map(function(p){
    return "<p>"+p.split("\\n").map(leesTekstHtml).join("<br>")+"</p>";
  }).join("");""",
"""  var paras = h.tekst.split("\\n\\n").map(function(p, i){
    return "<p>"+p.split("\\n").map(leesTekstHtml).join("<br>")+"</p>"+leesVertHtml(h, i);
  }).join("");""")

    rep("""    if(t && t.id === "btnLeesMijn"){ leesMijnKlik(); return; }""",
"""    if(t && t.id === "btnLeesMijn"){ leesMijnKlik(); return; }
    /* v23.219: de Nederlandse regel onder een alinea. Vóór de tooltip-afhandeling, want deze knop
       staat binnen dezelfde kaart en zou anders als "ergens anders" gelden en de tooltip sluiten. */
    if(t && t.classList && t.classList.contains("leesvertknop")){
      var vi = t.getAttribute("data-vert");
      var vp = el.querySelector("[data-vertnl='" + vi + "']");
      if(vp){
        var open = !vp.classList.contains("weg");
        vp.classList.toggle("weg");
        t.classList.toggle("aan", !open);
        if(!open) leesVertBij(h, +vi);
      }
      return;
    }""")

# =============================================================================================
# 3. de opmaak
# =============================================================================================
if DOE_APP:
    rep("""function leesTooltipPlaats(el, span){""",
"""/* v23.219: het knopje is klein en grijs, de vertaling staat ingesprongen en in een andere kleur.
   Allebei met opzet: het moet te vinden zijn en niet uitnodigen. De knop haalt wel de 44 pixels van
   TIKDOEL_MIN (v23.210), want een tikdoel is een tikdoel. */
function leesTooltipPlaats(el, span){""")

    anker_css = """.lw{cursor:pointer"""
    if anker_css in src:
        rep(anker_css, """.leesvert{margin:-6px 0 12px}
.leesvertknop{background:none; border:0; color:var(--muted); font-size:.78rem; padding:0 6px;
  min-height:44px; min-width:44px; cursor:pointer; text-align:left}
.leesvertknop.aan{color:var(--accent)}
.leesvertnl{margin:0 0 0 10px; padding:6px 10px; border-left:2px solid var(--rand);
  color:var(--muted); font-size:.92rem}
.leesvertnl.weg{display:none}
.lw{cursor:pointer""")
    else:
        # geen .lw-regel gevonden: dan aan het eind van het stijlblok
        i = src.index("</style>")
        src = src[:i] + """.leesvert{margin:-6px 0 12px}
.leesvertknop{background:none; border:0; color:var(--muted); font-size:.78rem; padding:0 6px;
  min-height:44px; min-width:44px; cursor:pointer; text-align:left}
.leesvertknop.aan{color:var(--accent)}
.leesvertnl{margin:0 0 0 10px; padding:6px 10px; border-left:2px solid var(--rand);
  color:var(--muted); font-size:.92rem}
.leesvertnl.weg{display:none}
""" + src[i:]

# =============================================================================================
# 4. de twee tellers gaan mee naar de server
# =============================================================================================
if DOE_APP:
    rep("""    payload.gezien = S.gezien || {};   // v23.145: waar je liep, niet alleen waar je struikelde
  }catch(e){}""",
"""    payload.gezien = S.gezien || {};   // v23.145: waar je liep, niet alleen waar je struikelde
    /* v23.219: lezen was het enige onderdeel waarvan er niets in dit logje stond. leesZoek telt
       sinds v23.21 elke opzoeking en is nooit ergens heen gegaan; leesVert telt sinds vandaag welke
       alinea's je in het Nederlands wilde zien. Samen zijn dat de twee maten waarmee de app kan
       gaan zien wat voor jou te zwaar is, in plaats van het uit een woordenlijst te schatten. */
    payload.leesZoek = S.leesZoek || {};
    payload.leesVert = S.leesVert || {};
  }catch(e){}""")

if DOE_APP:
    assert src.count("function leesVertHtml(") == 1
    assert src.count("+leesVertHtml(h, i)") == 1
    assert src.count("payload.leesVert") == 1
    assert src.count("vert:[") == 10, src.count("vert:[")
    APP.write_text(src, encoding="utf-8")
    print("index.html: de trede staat erin, en de twee tellers gaan mee naar de server")
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
