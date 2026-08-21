#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.155: de dagles krijgt zijn eigen frame.

Stefan, 21 aug: "de flow voelt nog steeds gebroken. Dat doet duolingo echt veel beter. (...) Ik weet
niet echt wanneer wat gebeurt of waar ik wat kan vinden."

## De diagnose

De dagles had geen eigen scherm. Hij bestaat uit vijf blokken, en elk blok stuurde je naar het
tabblad waar die oefening toevallig woont:

  woordjes   -> Woordjes        eigen kop, eigen knoppen
  grammatica -> Grammatica-tab  kicker, stapbolletjes, eigen terugknop
  toetsje    -> Cursus          eigen voortgangsbalk
  input      -> Lezen / Speeltuin / Música   drie totaal verschillende schermen
  schrijven  -> Vertalen        eigen invoer

Vijf schermen, vijf soorten chrome, vijf manieren terug. En onderaan bleef de tabbalk staan, dus op
elk moment in je les nodigen vijf knoppen je uit om ergens anders heen te gaan.

Duolingo doet precies één ding anders, en dat verklaart het hele verschil: **een les is één scherm
dat van binnen verandert.** Je verlaat het nooit, dus de vraag "waar ben ik en hoe kom ik terug"
bestaat daar niet.

## Wat deze ronde doet

Niet: alle vijftien renderfuncties in één container hertekenen. Dat is een verbouwing van weken en
elke stap ervan kan de les breken.

Wel: een frame eromheen, dat op drie manieren werkt.

**1. Eén strook, altijd dezelfde, altijd op dezelfde plek.** De lesstrook stond tot nu toe vijftien
keer in de code, elke keer met een eigen `inFlow`-controle vooraf, en op sommige schermen (het lied,
Escuchar, de grammaticawizard) helemaal niet. Nu hangt hij vast bovenaan het scherm, buiten alle
tabbladen, en wordt hij op één plek getekend. De vijftien aanroepen blijven staan maar leveren niets
meer zolang het frame er is: `lesFlowBannerHtml()` geeft dan een lege string terug. Eén waarheid,
zonder vijftien plekken aan te raken.

**2. De tabbalk verdwijnt tijdens je les.** Dit is de grootste. Vijf knoppen onderaan die je
uitnodigen om weg te gaan, precies terwijl je iets aan het afmaken bent. Weg zolang je bezig bent,
terug zodra je klaar bent of pauzeert.

**3. Eén manier terug, en die staat er.** In de strook staat "pauzeer" met de belofte erbij: je komt
terug waar je was. Dat is de knoop die op elk van die vijf schermen anders heette.

## Wat het niet doet

De schermen zelf houden hun eigen koppen ("Rompecabezas 🧩", "La Biblioteca"). Dat mag: je ziet dan
welke oefening je doet. Wat weg moest is de navigatie eromheen, en die is weg.

Bewaakt door test/suites/pw-lesframe.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.155"

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


# ================= 1. de strook zelf, vast bovenaan =================

rep(
    '''  .lesstrook{margin:0 0 10px;}''',
    '''  .lesstrook{margin:0 0 10px;}
  /* v23.155: het frame om je dagles. Vast bovenaan, buiten alle tabbladen, zodat er tijdens je les
     precies één ding op het scherm staat dat niet per blok verandert. */
  #lesFrame{position:sticky; top:0; z-index:90; background:var(--bg); padding:8px 0 6px;
            border-bottom:1px solid var(--border); margin:0 0 12px;}
  #lesFrame.leeg{display:none;}
  #lesFrame .lesstrook{margin:0;}
  #lesFrame .lesuit{display:block; margin-top:6px; font-size:.82rem; text-align:right;
                    text-decoration:underline; cursor:pointer;}
  /* En de tabbalk gaat weg zolang je bezig bent. Vijf knoppen die je uitnodigen om ergens anders
     heen te gaan, precies terwijl je iets afmaakt, is de kern van "ik weet niet waar ik ben". */
  body.in-les nav#nav{display:none;}''',
)

rep(
    '''<div class="wrap">
  <header>''',
    '''<div class="wrap">
  <!-- v23.155: het lesframe. Staat altijd in de DOM en is leeg zolang er geen les loopt. -->
  <div id="lesFrame" class="leeg"></div>
  <header>''',
)

# ================= 2. één plek die hem tekent =================

rep(
    '''function lesFlowBannerHtml(){
  if(!lesFlow) return "";''',
    '''/* ================= HET LESFRAME (v23.155) =================

   Stefan: "Ik weet niet echt wanneer wat gebeurt of waar ik wat kan vinden."

   De dagles rende door vijf tabbladen heen, elk met eigen chrome en een eigen manier terug, en de
   tabbalk bleef er de hele tijd onder staan. Nu: één strook bovenaan die niet meeverhuist, geen
   tabbalk zolang je bezig bent, en één manier om te pauzeren.

   lesFrameAan() is de enige plek die bepaalt of het frame er is. Alles hangt daaraan: de strook, de
   body-klasse, en of de vijftien in-scherm-stroken zichzelf wegcijferen. */
function lesFrameAan(){
  return !!(lesFlow && lesFlow.stap && document.getElementById("lesFrame"));
}
function lesFrameSync(){
  var el = document.getElementById("lesFrame");
  if(!el) return;
  if(!lesFrameAan()){
    el.innerHTML = "";
    el.classList.add("leeg");
    document.body.classList.remove("in-les");
    return;
  }
  el.classList.remove("leeg");
  document.body.classList.add("in-les");
  el.innerHTML = lesStrookHtml() +
    "<span class='lesuit muted' id='btnLesPauze'>"+
      ct("pauzeer je les","pause your session")+"</span>";
  var p = document.getElementById("btnLesPauze");
  if(p) p.onclick = lesFramePauze;
}
/* Eén manier terug. Hij heette op elk van die vijf schermen anders ("Terug", "← Speeltuin", "Verder
   met je les", "Stoppen"), en op sommige stond hij er niet. lesFlowBewaar() bestaat al sinds v19.92
   en zet precies genoeg opzij om morgen of straks verder te kunnen. */
function lesFramePauze(){
  try { lesFlowBewaar(); } catch(e){}
  lesFlow = null;
  lesFrameSync();
  show("lessen");
  toast(ct("Je les staat klaar waar je gebleven was.","Your session is waiting where you left off."));
}
function lesStrookHtml(){
  if(!lesFlow) return "";
  return "<div class='lesstrook'>"+
    dagBalkHtml(lesFlow.stap, lesFlow.stappen)+
    "<div class='lesstap'>"+ct("stap","step")+" "+lesFlowStapNum()+"/"+lesFlowStapTotaal()+
      " · "+lesFlowStapNaam()+"</div></div>";
}
/* De vijftien aanroepen in de schermen zelf blijven staan en leveren niets meer zolang het frame er
   is. Dat is met opzet: vijftien plekken aanpassen om één strook te verplaatsen is vijftien kansen
   om iets te breken, en deze ene regel doet hetzelfde. */
function lesFlowBannerHtml(){
  if(lesFrameAan()) return "";
  if(!lesFlow) return "";''',
)

# ================= 3. hij wordt bijgewerkt bij elke schermwissel =================

rep(
    '''  // v19.78: wie de chispa-pagina verlaat neemt haar podium niet mee naar de woordjes
  try { chispaBalkCheck(); } catch(e){}''',
    '''  // v19.78: wie de chispa-pagina verlaat neemt haar podium niet mee naar de woordjes
  try { chispaBalkCheck(); } catch(e){}
  // v23.155: het frame hoort bij de app en niet bij het scherm, dus hier, na elke wissel.
  try { lesFrameSync(); } catch(e){}''',
)

# en bij elke stap van de les, want de strook telt mee
rep(
    '''function lesFlowVolgende(){''',
    '''/* v23.155: de strook staat buiten de schermen, dus hij wordt niet meer vanzelf meegetekend als een
   scherm zichzelf hertekent. Elke stapwissel gaat hierlangs. */
function lesFlowStap(){
  try { lesFrameSync(); } catch(e){}
}
function lesFlowVolgende(){''',
)

rep(
    '''function lesFlowVolgendeKern(){''',
    '''function lesFlowVolgendeKern(){
  setTimeout(lesFlowStap, 0);   // v23.155: na de schermwissel, zodat de strook de nieuwe stap toont''',
)

# klaar met de les: frame weg
rep(
    '''function lesFlowKlaar(){''',
    '''function lesFlowKlaar(){
  setTimeout(lesFlowStap, 0);   // v23.155: les klaar, dus frame en tabbalk komen terug''',
)

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
