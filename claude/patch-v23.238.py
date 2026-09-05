#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.238 - een klasse zonder opmaak is geen terugkoppeling
#
# Stefan, 5 september, met een schermafbeelding van de leesvraag bij Los molinos de viento:
# "als ik het antwoord klik krijg ik geen rode en groene achtergrond (...) dit moet je even globaal
# oplossen"
#
# WAT ER AAN DE HAND WAS
#
# answerBoekVraag() doet dit, en heeft dat altijd gedaan:
#
#     opts[v.c].classList.add("correct");
#     btn.classList.add("wrong");
#
# Alleen: v23.191 heeft die twee klassen hernoemd. Toen stonden .opt.correct/.opt.wrong (het toetsje)
# naast .gw-optie.juist/.gw-optie.jouw (de opfrisser), twee paren voor hetzelfde, en die zijn
# samengevoegd tot .juist en .jouw met keuzeMerk() als enige plek die zegt wie welke krijgt.
#
# Het toetsje en de opfrisser zijn toen omgebouwd. De leesvraag en de luistervraag niet. Die zetten
# sindsdien een klasse waar geen enkele CSS-regel meer bij hoort. Geen foutmelding, geen kapotte
# knop, gewoon: niets gebeurt. Vier maanden lang.
#
# En het commentaar van v23.191 belooft letterlijk: "Een derde scherm krijgt het gedrag mee zodra het
# deze functie gebruikt, en de poort merkt het als het dat niet doet." Dat tweede deel bestond niet.
#
# DE INVENTARIS, WANT STEFAN VROEG HET GLOBAAL
#
#   toetsje (answerQuestion)        keuzeMerk           goed
#   grammatica-opfrisser            keuzeMerk           goed
#   leesvraag (answerBoekVraag)     correct / wrong     DOOD, geen opmaak
#   luistervraag (audAntwoord)      correct / wrong     DOOD, geen opmaak
#   ¡Vamos!-vraag (helVraagRender)  opt good / opt bad  werkte, maar met een derde woordenschat
#   proefvraag (renderProef)        niets               alleen een toast
#   vroege proefvraag               niets               alleen een regel tekst
#   rondleiding                     niets               alleen een toast
#   niveautest                      niets               met opzet: gokken mag, er is geen goed antwoord
#                                                       om te tonen want de test meet en onderwijst niet
#
# Zeven van de negen deden het dus niet of anders. Dat is geen reeks vergissingen maar een ontbrekende
# afdwinging.
#
# WAT ER NU STAAT
#
# keuzeMarkeer(knoppen, juist, gekozen) markeert een hele rij knoppen in één keer, via keuzeMerk().
# Geen enkele aanroeper schrijft nog een klassenaam op. Acht schermen gebruiken hem; de niveautest
# staat er met opzet buiten en dat staat als proef vast, zodat niemand hem er per ongeluk bij trekt.
#
# EN DE POORT LEEST DE KLEUR, NIET DE KLASSE
#
# Dit is de kern. Een proef die controleert of de knop class="correct" krijgt, stond vier maanden
# groen terwijl er niets te zien was. pw-antwoordkleur.js leest getComputedStyle().backgroundColor
# van de knop nadat je erop hebt geklikt, en eist dat die verschilt van de onbeantwoorde knop.
# Een klasse zonder opmaak is geen terugkoppeling.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.238"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function keuzeMarkeer(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. één functie die een hele rij markeert ----------
    rep("""function keuzeMerk(i, juist, gekozen){
  if(i === juist) return "juist";
  if(gekozen !== null && gekozen !== undefined && i === gekozen) return "jouw";
  return "";
}""",
"""function keuzeMerk(i, juist, gekozen){
  if(i === juist) return "juist";
  if(gekozen !== null && gekozen !== undefined && i === gekozen) return "jouw";
  return "";
}
/* ================= EEN KLASSE ZONDER OPMAAK IS GEEN TERUGKOPPELING (v23.238) =================

   Stefan, 5 september, bij de leesvraag van Los molinos de viento: "als ik het antwoord klik krijg
   ik geen rode en groene achtergrond (...) dit moet je even globaal oplossen."

   answerBoekVraag() zette classList.add("correct") en classList.add("wrong"), en dat had hij altijd
   gedaan. Alleen: hierboven zijn die twee klassen in v23.191 hernoemd naar juist en jouw. Het toetsje
   en de opfrisser zijn toen omgebouwd, de leesvraag en de luistervraag niet. Die zetten sindsdien een
   klasse waar geen enkele CSS-regel bij hoort. Geen foutmelding, geen kapotte knop, gewoon niets.

   De kop van keuzeMerk() belooft: "een derde scherm krijgt het gedrag mee zodra het deze functie
   gebruikt, en de poort merkt het als het dat niet doet." Dat tweede deel bestond niet, en een
   belofte die alleen in het commentaar staat is geen belofte.

   Deze functie is de afdwinging. Hij markeert een hele rij in één keer, zodat een aanroeper geen
   klassenaam meer hoeft te kennen en er dus ook geen verkeerde kan opschrijven. */
function keuzeMarkeer(knoppen, juist, gekozen){
  if(!knoppen) return;
  var i, m;
  for(i = 0; i < knoppen.length; i++){
    if(!knoppen[i] || !knoppen[i].classList) continue;
    knoppen[i].classList.remove("juist");
    knoppen[i].classList.remove("jouw");
    m = keuzeMerk(i, juist, gekozen);
    if(m) knoppen[i].classList.add(m);
  }
}""")

    # ---------- 2. de leesvraag: Stefans schermafbeelding ----------
    rep("""  var opts = el.querySelectorAll(".opt");
  opts[v.c].classList.add("correct");
  var goed = idx === v.c;
  if(goed){ st.score++; addXP(2); trackPoging(false); } else { btn.classList.add("wrong"); addXP(1); trackPoging(true); }""",
"""  var opts = el.querySelectorAll(".opt");
  /* v23.238: via keuzeMarkeer(). Hier stonden classList.add("correct") en add("wrong"), en die twee
     klassen bestaan sinds v23.191 niet meer in de opmaak. Dit is de knop uit Stefans
     schermafbeelding van 5 september. */
  keuzeMarkeer(opts, v.c, idx);
  var goed = idx === v.c;
  if(goed){ st.score++; addXP(2); trackPoging(false); } else { addXP(1); trackPoging(true); }""")

    # ---------- 3. de luistervraag ----------
    rep("""  el.querySelectorAll(".audOpt").forEach(function(b){
    var bi = +b.getAttribute("data-ai");
    if(bi === v.c) b.classList.add("correct");
    else if(b === knop) b.classList.add("wrong");
    b.onclick = null;
  });""",
"""  /* v23.238: dezelfde reparatie als bij de leesvraag. Ook hier stonden correct en wrong. */
  keuzeMarkeer(el.querySelectorAll(".audOpt"), v.c, i);
  el.querySelectorAll(".audOpt").forEach(function(b){ b.onclick = null; });""")

    # ---------- 4. de ¡Vamos!-vraag: derde woordenschat weg ----------
    rep("""  var knoppen = v.opties.map(function(o){
    var cls = "opt";
    if(gekozen !== undefined && gekozen !== null){
      if(o === v.goed) cls = "opt good";
      else if(o === gekozen) cls = "opt bad";
    }""",
"""  /* v23.238: dit scherm had een derde stel klassen (good en bad) voor precies hetzelfde. Nu via
     keuzeMerk(), zodat er één woordenschat is. Op index vergelijken en niet op tekst: twee opties
     met dezelfde tekst zouden anders allebei oplichten. */
  var iGoed = v.opties.indexOf(v.goed);
  var iGekozen = (gekozen === undefined || gekozen === null) ? null : v.opties.indexOf(gekozen);
  var knoppen = v.opties.map(function(o, oi){
    var cls = "opt";
    if(iGekozen !== null) cls = ("opt " + keuzeMerk(oi, iGoed, iGekozen)).replace(/\\s+$/, "");""")

    # ---------- 5. de proefvraag in het grote script ----------
    rep("""      var goed = (+b.getAttribute("data-proef")) === w.c;
      proefStand.xp += goed ? 2 : 1;
      proefStand.res[w.id] = goed;""",
"""      var goed = (+b.getAttribute("data-proef")) === w.c;
      /* v23.238: ook hier zie je nu welke knop de jouwe was en welke de goede. Er stond alleen een
         toast, en die is weg voordat je hem gelezen hebt. */
      keuzeMarkeer(box.querySelectorAll("button[data-proef]"), w.c, +b.getAttribute("data-proef"));
      proefStand.xp += goed ? 2 : 1;
      proefStand.res[w.id] = goed;""")

    # ---------- 6. de rondleiding ----------
    rep("""        var goed = (+b.getAttribute("data-toefen")) === t.oefen.c;
        // woordje meteen echt het herhaalsysteem in""",
"""        var goed = (+b.getAttribute("data-toefen")) === t.oefen.c;
        /* v23.238: het eerste keuzeknopje dat een nieuwe gebruiker ooit ziet, liet niet zien welke
           knop de goede was. Nu wel, met dezelfde kleuren als overal. */
        keuzeMarkeer(wrap.querySelectorAll("button[data-toefen]"), t.oefen.c,
                     +b.getAttribute("data-toefen"));
        // woordje meteen echt het herhaalsysteem in""")

if DOE_APP:
    for nodig in ["function keuzeMarkeer(", "keuzeMarkeer(opts, v.c, idx)",
                  'keuzeMarkeer(el.querySelectorAll(".audOpt"), v.c, i)',
                  'keuzeMarkeer(box.querySelectorAll("button[data-proef]")',
                  'keuzeMarkeer(wrap.querySelectorAll("button[data-toefen]")']:
        assert nodig in src, "ontbreekt: " + nodig
    # commentaar eerst weg: een controle die zijn eigen toelichting leest, controleert niets
    kaal = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
    for dood in ['classList.add("correct")', 'classList.add("wrong")', '"opt good"', '"opt bad"']:
        assert dood not in kaal, "er schrijft nog iemand een dode klassenaam: " + dood
    # en de klassen die er wél zijn, staan in de opmaak
    for klas in [".juist{", ".jouw{"]:
        assert klas in src, "de klasse mist zijn opmaak: " + klas
    APP.write_text(src, encoding="utf-8")
    print("index.html: acht schermen markeren via een plek")
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
