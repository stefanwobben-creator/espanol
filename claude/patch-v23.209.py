#!/usr/bin/env python3
# v23.209 - een scherm zegt zelf of het een opgave is of een pagina
#
# Stefan, 30 aug: "nu is het nog teveel website", en na twee prototypes: "nee dit is duidelijk, veel
# beter zo. voer maar door."
#
# WAT ER GEMETEN IS
#
# Alle zeventien tabbladen op 390 pixels breed, met alle lessen open:
#
#   vertalen   0,4 scherm    lessen     0,4    woorden   0,5    chat      0,5
#   meting     0,5           speeltuin  0,8    oefenen   1,0    lezen     1,7
#   musica     2,4           steun      2,9    perfil    3,0    cursus    3,1
#   spiekbrief 3,5           privacy    3,6    chispa    4,3    voortgang 4,9
#   toetsjes   12,5
#
# Twee soorten, en de app maakt dat onderscheid nergens. De fout is niet dat voortgang een pagina is;
# Duolingo's statistiekschermen scrollen ook. De fout is dat vertalen, 0,4 scherm hoog, de hele
# sitekop meedraagt.
#
# Op zo'n taakscherm staat er boven de eerste vraag:
#
#   16 - 92    #lesFrame     de voortgangsstrook plus "pauzeer je les"
#   104 - 176  header        ¡Vamos <naam>! met de zoekknop en Chispa      72 pixels
#   190 - 210  #goalLine     0/30 tacos                                    20 pixels
#   221        de oefening
#
# En eronder de voettekst: Rondleiding · Hoe dit werkt & steun de app · Privacy · versienummer.
#
# WAT DEZE RONDE DOET
#
# TABS krijgt een veld `soort`. show() zet dat als data-schermsoort op body, en CSS doet de rest. Dat
# is de hele ingreep: één veld in de data, één regel in de ene plek waar alle schermen doorheen gaan,
# en geen enkele van de zeventig renderfuncties wordt aangeraakt.
#
#   soort:"taak"       woorden, vertalen, speeltuin, chat, meting
#   soort:"overzicht"  al het andere
#
# Op een taakscherm verdwijnen de sitekop, de dagbalk en de voettekst. De onderbalk blijft staan, en
# dat is met opzet: buiten een lopende les is die balk je uitgang. De volledige overname (ook de
# onderbalk weg, met een X als uitgang) hangt aan body.in-les en is de volgende ronde, want daar
# zit het vastlooprisico.
#
# En de pauzelink wordt een knop. Hij was een onderstreepte tekstspan van 20 pixels hoog, rechts
# uitgelijnd; dat is het sterkste "dit is een website" signaal dat er bestaat en meteen het kleinste
# tikdoel op het scherm. Nu een X van 44 bij 44 aan de linkerkant van de strook, waar een
# sluitknop hoort.
#
# WAT DEZE RONDE NIET DOET
#
# De 148 tikdoelen onder de 44 pixels aanpakken. Een blanco min-height op elke knop in een
# taakscherm raakt tegels, chipjes en inline knoppen tegelijk, en dat is honderdvijftig plekken
# blind verbouwen. Die krijgen hun eigen ronde met een meting per soort knop.
#
# Toetsjes blijft een overzicht. Dat scherm is 12,5 schermen hoog met 57 kaarten en 56 tikdoelen die
# allemaal te klein zijn; daar helpt geen schil, dat is een eigen ronde.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.209"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "data-schermsoort" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:120])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de schermen zeggen zelf wat ze zijn
# =============================================================================================
if DOE_APP:
    rep('''var TABS = [
  {id:"lessen", label:"Lessen"},
  {id:"cursus", label:"Cursus"},   // v19.90: de leerlijn, weg bij het profiel vandaan
  {id:"voortgang", label:"Voortgang", nav:false},   // v23.32: eigen scherm, weg bij het profiel vandaan
  {id:"woorden", label:"Woordjes"},
  {id:"vertalen", label:"Vertalen"},
  {id:"toetsjes", label:"Toetsjes", nav:false}, // v19.47: geen eigen tab meer, zit nu in Grammatica
  {id:"lezen", label:"Lezen"},
  {id:"chispa", label:"Chispa", nav:false},
  {id:"chat", label:"Praten met Chispa", nav:false},   // v23.144
  {id:"meting", label:"De weekmeting", nav:false},     // v23.174
  {id:"perfil", label:"Profiel", nav:false},
  {id:"steun", label:"Steun", nav:false},
  {id:"privacy", label:"Privacy", nav:false},
  {id:"musica", label:"Música", nav:false},
  {id:"oefenen", label:"Oefenen", nav:false},
  {id:"speeltuin", label:"Speeltuin"},
  {id:"spiekbrief", label:"Grammatica"}
];''',
        '''/* v23.209: elk scherm zegt zelf wat het is, en dat is het enige dat de schil aanstuurt.

   TAAK       een opgave, een antwoord, een knop. Alles wat je ogen van die opgave weghaalt gaat
              weg: de sitekop met je naam en de zoekknop, de dagbalk, de voettekst.
   OVERZICHT  je leest en navigeert. Blijft een pagina met alles erop, en dat hoort zo.

   Gemeten op 390 pixels breed: vertalen is 0,4 scherm hoog, woorden 0,5, speeltuin 0,8. Voortgang
   is 4,9 en spiekbrief 3,5. Het waren altijd al twee soorten; er stond alleen nergens welke.

   Toetsjes staat er met opzet niet bij. Dat tabblad is 12,5 schermen hoog met 57 kaarten, want het
   draagt het menu en de toets tegelijk. Daar helpt geen schil; dat is een eigen ronde.

   Lezen en musica ook niet: daar is de tekst een pagina en zijn de vragen opgaven, binnen hetzelfde
   tabblad. Die twee hebben een derde stand nodig en die is er nog niet. */
var TABS = [
  {id:"lessen", label:"Lessen", soort:"overzicht"},
  {id:"cursus", label:"Cursus", soort:"overzicht"},   // v19.90: de leerlijn, weg bij het profiel vandaan
  {id:"voortgang", label:"Voortgang", nav:false, soort:"overzicht"},   // v23.32: eigen scherm, weg bij het profiel vandaan
  {id:"woorden", label:"Woordjes", soort:"taak"},
  {id:"vertalen", label:"Vertalen", soort:"taak"},
  {id:"toetsjes", label:"Toetsjes", nav:false, soort:"overzicht"}, // v19.47: geen eigen tab meer, zit nu in Grammatica
  {id:"lezen", label:"Lezen", soort:"overzicht"},
  {id:"chispa", label:"Chispa", nav:false, soort:"overzicht"},
  {id:"chat", label:"Praten met Chispa", nav:false, soort:"taak"},   // v23.144
  {id:"meting", label:"De weekmeting", nav:false, soort:"taak"},     // v23.174
  {id:"perfil", label:"Profiel", nav:false, soort:"overzicht"},
  {id:"steun", label:"Steun", nav:false, soort:"overzicht"},
  {id:"privacy", label:"Privacy", nav:false, soort:"overzicht"},
  {id:"musica", label:"Música", nav:false, soort:"overzicht"},
  {id:"oefenen", label:"Oefenen", nav:false, soort:"overzicht"},
  {id:"speeltuin", label:"Speeltuin", soort:"taak"},
  {id:"spiekbrief", label:"Grammatica", soort:"overzicht"}
];
/* Eén plek leest dat veld. Staat er niets, dan is het een overzicht: een scherm dat vergeet zijn
   soort te noemen hoort niets kwijt te raken. */
function tabSoort(id){
  for(var i = 0; i < TABS.length; i++){ if(TABS[i].id === id) return TABS[i].soort || "overzicht"; }
  return "overzicht";
}''')

# =============================================================================================
# 2. show() zet het, en verder niemand
# =============================================================================================
if DOE_APP:
    rep('''  TABS.forEach(function(t){
    document.getElementById("tab-"+t.id).classList.toggle("hidden", t.id!==tabId);
  });''',
        '''  TABS.forEach(function(t){
    document.getElementById("tab-"+t.id).classList.toggle("hidden", t.id!==tabId);
  });
  /* v23.209: de enige plek die de soort zet. Alles wat de schil doet hangt hieraan, en geen enkele
     renderfunctie weet ervan. Een regel die voor zeventien schermen geldt, hoort door één plek
     afgedwongen te worden. */
  try { document.body.setAttribute("data-schermsoort", tabSoort(tabId)); } catch(e){}''')

# =============================================================================================
# 3. de schil zelf: CSS, en niets anders
# =============================================================================================
if DOE_APP:
    rep("""  .wrap{padding-bottom:84px;}""",
        """  .wrap{padding-bottom:84px;}
  /* ================= DE SCHIL VAN EEN TAAKSCHERM (v23.209) =================
     Op een scherm met één opgave gaat alles weg wat je ogen van die opgave weghaalt. Gemeten op
     Stefans telefoon stond de eerste vraag op 221 van de 844 pixels, en daarboven stonden zijn
     eigen naam, een zoekknop en een dagbalk.

     De onderbalk blijft met opzet staan: buiten een lopende les is dat je uitgang. Tijdens een les
     verdwijnt hij al sinds v23.155 (body.in-les), en daar hoort de X bij die hieronder staat. */
  body[data-schermsoort="taak"] header,
  body[data-schermsoort="taak"] #goalLine,
  body[data-schermsoort="taak"] #appFooter{ display:none !important; }""")

# =============================================================================================
# 4. de pauzelink wordt een knop
# =============================================================================================
if DOE_APP:
    rep('''  el.innerHTML = lesStrookHtml() +
    "<span class='lesuit muted' id='btnLesPauze'>"+
      ct("pauzeer je les","pause your session")+"</span>";''',
        '''  /* v23.209: dit was een onderstreepte tekstspan van twintig pixels hoog, rechts uitgelijnd. Twee
     dingen mis: een onderstreepte link is het sterkste "dit is een website" signaal dat er bestaat,
     en twintig pixels is het kleinste tikdoel op het scherm terwijl dit de enige uitgang is. Nu een
     sluitknop van 44 bij 44 links in de strook, waar een sluitknop hoort. De tekst blijft ernaast
     staan zolang er ruimte voor is, want een kale X zonder woord is een knop waarvan je niet weet
     wat hij doet. */
  el.innerHTML = "<button type='button' class='lesuit' id='btnLesPauze' " +
      "title='" + ct("pauzeer je les", "pause your session") + "'>" +
      "<span aria-hidden='true'>\\u2715</span>" +
      "<span class='lesuittxt'>" + ct("pauzeer", "pause") + "</span></button>" +
    lesStrookHtml();''')

    # de bestaande regel vervangen in plaats van er een tweede naast te zetten: "#lesFrame .lesuit"
    # is specifieker dan "button.lesuit" en zou de onderstreping gewoon terugzetten. Dat is precies
    # de cascadebotsing waar je op moet letten als je klassen stapelt.
    rep("""  #lesFrame{position:sticky; top:0; z-index:90; background:var(--bg); padding:8px 0 6px;
            border-bottom:1px solid var(--border); margin:0 0 12px;}
  #lesFrame.leeg{display:none;}
  #lesFrame .lesstrook{margin:0;}
  #lesFrame .lesuit{display:block; margin-top:6px; font-size:.82rem; text-align:right;
                    text-decoration:underline; cursor:pointer;}""",
        """  #lesFrame{position:sticky; top:0; z-index:90; background:var(--bg); padding:8px 0 6px;
            border-bottom:1px solid var(--border); margin:0 0 12px;
            /* v23.209: de uitgang en de voortgangsstrook op een rij. Ze stonden onder elkaar, en dat
               kostte een halve regel op het scherm waar de opgave op staat. */
            display:flex; align-items:center; gap:10px;}
  #lesFrame.leeg{display:none;}
  #lesFrame .lesstrook{margin:0; flex:1 1 auto; min-width:0;}
  /* v23.209: dit was een blokspan van twintig pixels hoog, rechts uitgelijnd en onderstreept. Twee
     dingen mis: een onderstreepte link is het sterkste "dit is een website" signaal dat er bestaat,
     en twintig pixels is het kleinste tikdoel op het scherm terwijl dit tijdens een les je enige
     uitgang is; de tabbalk is dan weg, zie de regel hieronder. */
  #lesFrame .lesuit{
    display:flex; align-items:center; gap:6px; flex:0 0 auto;
    min-width:44px; min-height:44px; padding:0 10px; margin:0;
    border:0; background:none; color:var(--muted); cursor:pointer;
    font-size:1.15rem; line-height:1; border-radius:12px; text-decoration:none;
  }
  #lesFrame .lesuit .lesuittxt{font-size:.8rem; font-weight:700;}
  #lesFrame .lesuit:active{background:var(--bg);}
  @media (max-width:360px){ #lesFrame .lesuit .lesuittxt{display:none;} }""")

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    assert src.count('data-schermsoort') == 4, "verwacht één zetter en drie CSS-selectors"
    assert src.count("function tabSoort(") == 1
    assert src.count("soort:\"taak\"") == 5, "vijf taakschermen"
    assert src.count("soort:\"overzicht\"") == 12, "twaalf overzichtsschermen"
    assert "<span class='lesuit muted'" not in src, "de oude pauzespan staat er nog"
    APP.write_text(src, encoding="utf-8")
    print("index.html: elk scherm zegt zelf of het een opgave is of een pagina")
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
