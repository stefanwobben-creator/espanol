#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.235 - leren en onderhouden krijgen elk hun eigen beurt
#
# Stefan, op de mededeling dat de derde plek voor iets nieuws weg is: "maar hoe kan ik dan
# progressie maken want met grammatica doen we ook spaced repetition toch?"
#
# Goede vraag, en nagemeten in plaats van beantwoord.
#
# WAT ER AL GOED GING
#
# De focus van v23.234 stuurt alleen gcVandaagLijst(): welke onderwerpen de Grammatica-tab vandaag
# aanwijst. De herhaling loopt langs een andere lijst, gramWachtrij(), en die kijkt naar ALLE open
# concepten en pakt elk doosje waarvan de datum is verstreken. Gemeten met een gebouwd geval: een
# onderwerp op doos 4 dat vandaag toe is en buiten de focus valt, staat gewoon in de wachtrij.
#
# WAT ER NIET GOED GING, EN DAT IS OUDER DAN DE FOCUS
#
# lesFlowGramLijst() pakt uit die wachtrij precies één regel: rij[0]. En de wachtrij is oplopend op
# DOOS gesorteerd, want het zwakste hoort vooraan. Gevolg: zolang er ook maar íets op doos 0 staat,
# komt doos 4 nooit aan de beurt.
#
# In Stefans logboek staan zestien onderwerpen op doos 0, 1 of 2. Zijn negen onderwerpen op doos 5
# vervallen tussen 1 en 26 oktober. Vanaf 1 oktober staan die dus achter zestien zwakkere in een rij
# die er maar één per dag doorlaat, en dan is de herhaling van wat hij al kan stilletjes stuk. Nu
# nog niet: nul van de negen staat over tijd. Over vier weken wel.
#
# Dat is precies het omgekeerde van het lege midden: onderaan komt niets omhoog, en bovenaan valt
# straks alles om. Dezelfde oorzaak, één lijst die twee verschillende dingen moet doen.
#
# WAT ER NU STAAT
#
# Twee beurten met twee budgetten, want verwerven en onderhouden zijn niet hetzelfde werk:
#
#     LEREN        het zwakste doosje  (rij[0], zoals altijd)
#     ONDERHOUDEN  het langst vervallen doosje op doos 3 of hoger
#
# De onderhoudsbeurt komt er alleen als er ook echt iets te onderhouden is. Staat er niets op doos 3
# of hoger dat toe is, dan blijft de dagles precies zoals hij was: nul is geen bericht. Voor Stefan
# betekent dat vandaag geen enkel verschil, en vanaf 1 oktober één extra opfrisvraag op een dag dat
# er iets vervalt.
#
# En hij dringt niet voor: het leren staat vooraan in de lijst en het onderhoud erachter.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.235"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function gramOnderhoudTop(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep("""function gramWachtrij(){""",
"""/* ================= LEREN EN ONDERHOUDEN ZIJN TWEE BUDGETTEN (v23.235) =================

   Stefan: "maar hoe kan ik dan progressie maken want met grammatica doen we ook spaced repetition
   toch?"

   De wachtrij hieronder ziet alles wat toe is, ook buiten de focus van v23.234. Alleen pakt
   lesFlowGramLijst() daar precies één regel uit: rij[0]. En de wachtrij is oplopend op DOOS
   gesorteerd, want het zwakste hoort vooraan.

   Gevolg: zolang er íets op doos 0 staat komt doos 4 nooit aan de beurt. In Stefans logboek staan
   zestien onderwerpen op doos 0, 1 of 2, en zijn negen op doos 5 vervallen tussen 1 en 26 oktober.
   Vanaf 1 oktober zou de herhaling van alles wat hij al kan stilletjes stoppen.

   Dat is het spiegelbeeld van het lege midden: onderaan komt niets omhoog en bovenaan valt straks
   alles om, en het is dezelfde oorzaak. Eén lijst die twee verschillende dingen moet doen.

   Verwerven en onderhouden zijn niet hetzelfde werk en horen dus niet om dezelfde plek te vechten.
   Deze functie levert de onderhoudskant: het langst vervallen doosje dat al op doos 3 of hoger
   staat. Is er niets, dan komt er ook niets bij; nul is geen bericht. */
var GRAM_ONDERHOUD_DOOS = 3;
function gramOnderhoudTop(){
  var rij = [];
  try { rij = gramWachtrij(); } catch(e){ rij = []; }
  var kand = rij.filter(function(x){ return (x.st.box || 0) >= GRAM_ONDERHOUD_DOOS; });
  if(!kand.length) return null;
  /* Op vervaldatum en niet op doos: bij onderhoud telt wie het langst wacht, niet wie het zwakst
     is. Wie op doos gaat sorteren bouwt de rij van hierboven na, en dan wint doos 3 altijd van
     doos 5 en komt doos 5 nooit meer aan bod. */
  kand.sort(function(a, b){ return (a.st.due || "") < (b.st.due || "") ? -1 : 1; });
  return kand[0];
}
function gramWachtrij(){""")

    rep("""  var alHier = uit.map(kaal);
  if(gid && alHier.indexOf(kaal(gid)) === -1) uit.push(gid);
  return uit;
}""",
"""  var alHier = uit.map(kaal);
  if(gid && alHier.indexOf(kaal(gid)) === -1) uit.push(gid);

  /* v23.235: de onderhoudsbeurt, achteraan. Het leren staat vooraan omdat dat het werk van de dag
     is; het onderhoud is een tik op iets dat je al kunt. Hij komt er alleen als er echt iets
     vervallen is op doos 3 of hoger, dus op de meeste dagen verandert er niets aan je les. */
  var oh = null;
  try { oh = gramOnderhoudTop(); } catch(e){ oh = null; }
  if(oh){
    var ohId = gcOpfrisId(oh.c.id, oh.pi);
    if(uit.map(kaal).indexOf(kaal(ohId)) === -1){
      var ohO = null;
      try { ohO = gcGebouwd(ohId); } catch(e){ ohO = null; }
      if(ohO) uit.push(ohO.id);
    }
  }
  return uit;
}""")

if DOE_APP:
    for nodig in ["function gramOnderhoudTop(", "var GRAM_ONDERHOUD_DOOS = 3",
                  "oh = gramOnderhoudTop();", "gcOpfrisId(oh.c.id, oh.pi)"]:
        assert nodig in src, "ontbreekt: " + nodig
    assert src.count("function gramOnderhoudTop(") == 1, "gramOnderhoudTop staat er meer dan een keer"
    # het onderhoud sorteert op datum en niet op doos, anders wint doos 3 altijd van doos 5
    blok = src[src.index("function gramOnderhoudTop("):src.index("function gramWachtrij(")]
    assert "a.st.due" in blok and "a.st.box" not in blok.split("kand.sort")[1], \
        "het onderhoud sorteert op doos in plaats van op vervaldatum"
    # en hij staat achteraan: het leren eerst
    i_gid = src.index("if(gid && alHier.indexOf(kaal(gid)) === -1) uit.push(gid);")
    i_oh = src.index("oh = gramOnderhoudTop();")
    assert i_gid < i_oh, "de onderhoudsbeurt dringt voor op het leren"
    APP.write_text(src, encoding="utf-8")
    print("index.html: leren en onderhouden hebben elk hun eigen beurt")
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
