#!/usr/bin/env python3
# v23.213 - de belofte boven omkeerStart() stond er wel, maar nergens in de code
#
# GEVONDEN DOOR DE POORT, EEN OP DE VIJFHONDERD
#
# pw-omkeer viel om op "geen vorm twee keer in dezelfde ronde (11/12)". Drie keer opnieuw gedraaid:
# groen. Dat is precies het soort meldingen dat je wegwuift als flakiness, en dat is hier fout.
#
# Boven omkeerStart() staat sinds v23.109:
#
#     Een ronde van twaalf. Twee dingen bewust geregeld:
#       - niet twee keer dezelfde vorm in één ronde
#       - gespreid over de personen
#
# De tweede staat in de code. De eerste niet. Er is nooit iets geweest dat hem afdwong.
#
# WAT ER GEMETEN IS
#
# Met alle fasen open: 858 items in de pool, 837 verschillende vormen. Eenentwintig vormen staan er
# dus twee keer in, en dat komt doordat omkeerPool() de eenduidigheid per TIJD controleert. Binnen
# het presente is "vivimos" eenduidig (alleen nosotros) en binnen het indefinido ook, dus allebei
# komen ze in de pool. In de vraag staat de tijd niet, dus op het scherm zijn het twee keer dezelfde
# vraag.
#
# Alle eenentwintig wijzen naar dezelfde persoon. Er is dus geen ronde geweest met twee goede
# antwoorden; het ergste wat er kon gebeuren is dezelfde vraag twee keer in twaalf. Gemeten over
# 20.000 rondes: 0,2%. Dat is de een op de vijfhonderd waar de poort op viel.
#
# DE OPLOSSING, EN WAAROM DEZE
#
# De regel die omkeerPool() al hanteert, alleen een niveau breder: een vorm doet mee als hij naar
# precies één persoon wijst. Die controle stond per werkwoord en per tijd; nu staat hij ook over de
# pool als geheel. Verdwijnt daarmee inhoud? Nee: alle eenentwintig botsingen wijzen naar dezelfde
# persoon, dus de tweede kopie is letterlijk dezelfde vraag met een ander etiket dat niemand ziet.
#
# Wat NIET de oplossing is: in omkeerStart() dubbele vormen overslaan. Dan blijft de pool liegen
# over wat erin zit, en elke volgende aanroeper van omkeerPool() (de Conjugador leest hem inmiddels
# ook, v23.110) erft hetzelfde probleem opnieuw. Een regel die voor twee plekken geldt, hoort door
# één plek afgedwongen te worden.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.213"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

# let op: "var gezien = {}" komt elders in de app al voor, dus die is als merkteken waardeloos.
# Een controle die op een bestaande regel valt zou de patch stilletjes overslaan, en dat gebeurde
# hier ook echt bij de eerste poging.
DOE_APP = "v23.213: en over de pool als geheel" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:120])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    rep("""function omkeerPool(){
  var tijden = conjOpenTijden(), pool = [], dubbel = 0, totaal = 0;
  tijden.forEach(function(t){
    var verbs = conjVerbPool(t);
    verbs.forEach(function(v){
      var vormen = conjAlleVormen(v, t);
      for(var p = 0; p < vormen.length; p++){
        var vorm = vormen[p];
        if(!vorm) continue;
        totaal++;
        var uniek = true;
        for(var q = 0; q < vormen.length; q++) if(q !== p && vormen[q] === vorm) uniek = false;
        if(uniek) pool.push({v:v, p:p, t:t, vorm:vorm});
        else dubbel++;
      }
    });
  });
  return {items:pool, dubbel:dubbel, totaal:totaal};
}""",
"""function omkeerPool(){
  var tijden = conjOpenTijden(), pool = [], dubbel = 0, totaal = 0;
  /* v23.213: en over de pool als geheel, niet alleen binnen één werkwoord en één tijd.
     Gemeten met alles open: 858 items, 837 verschillende vormen. "vivimos" is binnen het presente
     eenduidig (nosotros) en binnen het indefinido ook, dus stond hij er twee keer in. In de vraag
     staat de tijd niet, dus op het scherm waren dat twee keer dezelfde vraag.
     Alle eenentwintig botsingen wijzen naar dezelfde persoon, dus er raakt geen enkele opgave weg:
     de tweede kopie is dezelfde vraag met een etiket dat niemand ziet. */
  var gezien = {};
  tijden.forEach(function(t){
    var verbs = conjVerbPool(t);
    verbs.forEach(function(v){
      var vormen = conjAlleVormen(v, t);
      for(var p = 0; p < vormen.length; p++){
        var vorm = vormen[p];
        if(!vorm) continue;
        totaal++;
        var uniek = true;
        for(var q = 0; q < vormen.length; q++) if(q !== p && vormen[q] === vorm) uniek = false;
        if(!uniek){ dubbel++; continue; }
        if(gezien[vorm]){ dubbel++; continue; }
        gezien[vorm] = true;
        pool.push({v:v, p:p, t:t, vorm:vorm});
      }
    });
  });
  return {items:pool, dubbel:dubbel, totaal:totaal};
}""")

if DOE_APP:
    rep("""/* Een ronde van twaalf. Twee dingen bewust geregeld:
     - niet twee keer dezelfde vorm in één ronde
     - gespreid over de personen, want een ronde van acht keer "yo" meet één uitgang en niet zes.""",
"""/* Een ronde van twaalf. Twee dingen bewust geregeld:
     - niet twee keer dezelfde vorm in één ronde. Die stond hier vanaf v23.109 als belofte en werd
       nergens afgedwongen; sinds v23.213 zit hij in omkeerPool(), zodat elke aanroeper hem erft.
     - gespreid over de personen, want een ronde van acht keer "yo" meet één uitgang en niet zes.""")

if DOE_APP:
    assert src.count("v23.213: en over de pool als geheel") == 1
    assert src.count("if(gezien[vorm]){ dubbel++; continue; }") == 1
    APP.write_text(src, encoding="utf-8")
    print("index.html: een vorm staat nog maar één keer in de pool")
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
