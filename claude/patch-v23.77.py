#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.77: de plank. Eén vorm voor "gehad, kan nu, komt nog", te beginnen bij Escuchar.

Stefan, 13 aug: "misschien wil ik bij dictado ook zien welke ik al heb gehad, welke ik nog moet
doen, welke unlocked zijn bij mijn huidige niveau (zelfde design principle) toepassen op alles."

## Wat er al was, op één plek

De boekenplank (v23.26) doet dit al: een kaart per hoofdstuk, een vinkje als je hem hebt gehad, en
bij een gesloten hoofdstuk de reden plus waar je staat ("Ontgrendelt na 5 afgeronde lessen · 3/5").
Dat is precies wat Stefan beschrijft, en het stond op één scherm van de app.

Overal elders loste elk scherm het opnieuw en anders op. Gemeten:

    Escuchar     audKies() pakt een willekeurige scene uit de pool en toont geen lijst.
                 Je ziet dus nooit hoeveel scenes er zijn, welke je had, of wat er nog komt.
    Speeltuin    een spel dat nog niet kan, verdwijnt. Geen slot, geen drempel, geen spoor.
    Toetsjes     een lijst zonder stand.
    Lessen       wel een lijst, eigen opmaak, ander slotgedrag.

Verdwijnen is de ergste van die vier. Een slot vertelt je dat er iets is en wat je ervoor moet
doen; verdwijnen vertelt je dat er niets is. Dat verschil is het hele punt van deze patch.

## Wat deze patch toevoegt

plankHtml(items) en plankWire(el, fn): één vorm, drie toestanden.

    klaar   je hebt hem gehad. Vinkje, en de knop wordt "nog eens".
    open    je kunt hem nu. Primaire knop.
    dicht   nog niet. Reden in gewone taal plus je stand ten opzichte van de drempel.

De volgorde is bewust: open eerst, dan klaar, dan dicht. Wat je nú kunt doen staat bovenaan, en wat
er nog komt staat onderaan waar het je niet in de weg zit maar wel te zien is.

## En Escuchar krijgt hem als eerste

Escuchar is de oefening waar het meest te winnen viel: zes scenes, willekeurig gekozen, geen
overzicht. Nu opent Escuchar op de plank, met per scene of je hem had, hoeveel vragen erin zitten,
en bij een gesloten scene waarom hij dicht zit. De ontgrendeling is niet nieuw en niet veranderd:
audPlafond() gaf al 10 + 2 per afgeronde scene, met een maximum van 30. Wat nieuw is, is dat je hem
kunt zien.

De willekeurige keuze blijft bestaan voor de lesflow (die kiest zelf een scene) en achter de knop
"Verras me". Wie geen zin heeft om te kiezen hoeft niet te kiezen.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.77"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.77" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_CSS = "  .plankKop{display:flex; justify-content:space-between; align-items:baseline; gap:8px;}"
A_MOTOR = "/* ================= ESCUCHAR: de motor ================= */"
A_RENDER = '''function renderFunAudicion(){
  var el = document.getElementById("funCard");
  if(!el) return;
  if(!audSc) audNieuw();
  var sc = audSc;'''
A_NIEUWKNOP = '''  var bn = document.getElementById("btnAudNieuw");
  if(bn) bn.onclick = function(){ audStop(); audNieuw(); renderFunAudicion(); };'''

if DOE_APP:
    ontbreekt = [n for n, a in (("de plank-CSS", A_CSS), ("de Escuchar-motor", A_MOTOR),
                                ("renderFunAudicion", A_RENDER), ("de knop Volgende scene", A_NIEUWKNOP))
                 if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.76. Eerst bijtrekken:\n\n"
              "    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


PLANK_CSS = '''  /* v23.77: de plank. Dezelfde vorm als de boekenplank hieronder, maar los van het boek, zodat
     Escuchar, de toetsjes, de spellen en de lessen hem allemaal kunnen gebruiken. Zie plankHtml(). */
  .plankRij{display:flex; align-items:flex-start; gap:10px; padding:11px 0; border-top:1px solid var(--border);}
  .plankRij:first-of-type{border-top:0;}
  .plankRij.dicht{opacity:.62;}
  .plankMerk{width:26px; height:26px; border-radius:50%; flex:0 0 26px; font-size:.85rem;
             display:flex; align-items:center; justify-content:center;
             background:var(--accent-soft); color:var(--accent);}
  .plankMerk.klaar{background:var(--accent); color:#fff;}
  .plankMerk.dicht{background:#f2eee6; color:var(--muted);}
  .plankTekst{flex:1 1 auto; min-width:0;}
  /* display:block, want dit zijn spans in een span. Zonder deze twee regels lopen de titel en de
     regel eronder aan elkaar vast ("Een ontmoeting3 vragen"), en dat zag ik pas op de schermafdruk.
     Het staat er dus omdat het gemeten is en niet omdat het netjes leek. */
  .plankTitel{display:block; font-weight:600; line-height:1.25;}
  .plankOnder{display:block; font-size:.82rem; color:var(--muted); margin-top:2px;}
  .plankStand{font-size:.78rem; color:var(--muted); white-space:nowrap;}
  .plankRij button{flex:0 0 auto; align-self:center;}
  .plankKopje{font-size:.72rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted);
              margin:16px 0 2px;}
  .plankKopje:first-child{margin-top:0;}
'''

PLANK_JS = '''/* ================= DE PLANK (v23.77) =================
   Stefan, 13 aug: "misschien wil ik bij dictado ook zien welke ik al heb gehad, welke ik nog moet
   doen, welke unlocked zijn bij mijn huidige niveau (zelfde design principle) toepassen op alles."

   De boekenplank deed dit al, en alleen daar. Elk ander scherm loste het opnieuw op, en de
   speeltuin loste het verkeerd op: een spel dat nog niet kan verdwijnt daar. Verdwijnen vertelt je
   dat er niets is; een slot vertelt je dat er iets is en wat je ervoor moet doen. Dat verschil is
   waarom dit bestaat.

   Drie toestanden, en niet meer:
     klaar   gehad. Vinkje, en de knop heet "nog eens".
     open    kan nu. Primaire knop.
     dicht   nog niet. De reden in gewone taal, plus waar je staat ("3/5").

   Een item:
     { id, titel, onder, staat:"klaar"|"open"|"dicht", slot, nu, van, knop, merk }

   De volgorde is open, klaar, dicht. Wat je nu kunt doen bovenaan; wat er nog komt onderaan, waar
   het niet in de weg zit maar wel te zien is. Wie een eigen volgorde wil geeft opt.ruw mee. */
function plankRijHtml(it){
  var staat = it.staat || "open";
  var merk = it.merk || (staat === "klaar" ? "\\u2713" : staat === "dicht" ? "\\ud83d\\udd12" : "\\u25b8");
  var h = "<div class='plankRij " + staat + "'>" +
    "<span class='plankMerk " + staat + "'>" + merk + "</span>" +
    "<span class='plankTekst'><span class='plankTitel'>" + it.titel + "</span>" +
    (it.onder ? "<span class='plankOnder'>" + it.onder + "</span>" : "");
  if(staat === "dicht"){
    var stand = (typeof it.nu === "number" && typeof it.van === "number") ? " \\u00b7 " + it.nu + "/" + it.van : "";
    h += "<span class='plankOnder'>" + (it.slot || ct("Nog niet open","Not open yet")) + stand + "</span>";
  }
  h += "</span>";
  if(staat !== "dicht"){
    h += "<button type='button' class='" + (staat === "klaar" ? "ghost" : "primary") + "' data-plank='" +
      String(it.id).replace(/'/g, "") + "'>" +
      (it.knop || (staat === "klaar" ? ct("Nog eens","Again") : ct("Doen","Start"))) + "</button>";
  }
  return h + "</div>";
}
function plankHtml(items, opt){
  opt = opt || {};
  var lijst = items.slice();
  if(!opt.ruw){
    var orde = {open:0, klaar:1, dicht:2};
    lijst = lijst.map(function(it, i){ return {it:it, i:i}; }).sort(function(a, b){
      var d = (orde[a.it.staat] || 0) - (orde[b.it.staat] || 0);
      return d || (a.i - b.i);
    }).map(function(x){ return x.it; });
  }
  /* De telling staat erboven en niet eronder, want dit is het antwoord op "hoeveel zijn er en waar
     sta ik". Onderaan zou je hem pas zien na alles wat je nog niet kunt. */
  var klaar = lijst.filter(function(x){ return x.staat === "klaar"; }).length;
  var dicht = lijst.filter(function(x){ return x.staat === "dicht"; }).length;
  var kop = opt.kop === false ? "" :
    "<div class='plankKopje'>" + klaar + "/" + lijst.length + ct(" gehad"," done") +
    (dicht ? " \\u00b7 " + dicht + ct(" nog op slot"," still locked") : "") + "</div>";
  return kop + "<div class='plank'>" + lijst.map(plankRijHtml).join("") + "</div>";
}
function plankWire(el, fn){
  if(!el) return;
  el.querySelectorAll("[data-plank]").forEach(function(b){
    b.onclick = function(){ fn(b.getAttribute("data-plank")); };
  });
}

'''

ESC_MENU = '''/* v23.77: Escuchar opent op de plank in plaats van op een willekeurige scene. audKies() bestaat
   nog, want de lesflow kiest zelf en "Verras me" doet hetzelfde als vroeger; wat erbij komt is dat
   je kunt zien wat er is. */
var audMenu = true;
/* Wat "open" betekent is niet audPlafond() maar audLijst(), en dat verschil is precies waar deze
   patch bijna in trapte.

   Gemeten op een vers profiel: audPlafond() geeft 10 en de lichtste scene weegt 13. Op het plafond
   alléén afgaand staan dus alle zes de scenes op slot en is Escuchar op dag 1 onspeelbaar. Dat was
   nooit zo, want audLijst() heeft een vangnet: valt de pool onder de twee, dan pakt hij de drie
   lichtste en negeert hij het plafond. Het plafond gatet in de praktijk dus niets op dag 1; het
   vangnet bepaalt wat je krijgt.

   Dat is dezelfde vorm als de lege spelpool van v23.65: een stille terugval die het echte gedrag
   bepaalt terwijl de zichtbare regel iets anders zegt. Een plank die de zichtbare regel toont zou
   zes sloten laten zien op een oefening die gewoon open is. Dus vragen we het aan de pool zelf. */
function audOpen(sc){
  return audLijst().some(function(x){ return x.id === sc.id; });
}
/* Hoeveel scenes moet je nog afmaken voordat deze opengaat? audPlafond() is 10 + 2 per afgeronde
   scene, dus de rekensom is terug te draaien. Dat getal is te begrijpen ("nog 2 scenes"); het
   plafond zelf ("10/13") is dat niet, want zwaarte is geen woord dat de gebruiker kent. */
function audNodig(sc){
  var af = Object.keys(S.audDone || {}).length;
  var moet = Math.ceil((audZwaarte(sc) - 10) / 2);
  return Math.max(1, moet - af);
}
function audPlankItems(){
  return AUDICIONES.map(function(sc){
    var gehad = !!(S.audDone || {})[sc.id];
    var open = audOpen(sc);
    var keer = (S.audLuister || {})[sc.id] || 0;
    var nodig = audNodig(sc);
    return {
      id: sc.id,
      titel: profLang() === "nl" ? sc.titel : sc.titelEn,
      onder: sc.vragen.length + ct(" vragen"," questions") +
             (keer ? " \\u00b7 " + keer + ct(" keer geluisterd"," listens") : ""),
      staat: gehad ? "klaar" : open ? "open" : "dicht",
      slot: nodig === 1
        ? ct("Gaat open als je nog \\u00e9\\u00e9n scene afmaakt", "Opens when you finish one more scene")
        : ct("Gaat open als je nog " + nodig + " scenes afmaakt", "Opens when you finish " + nodig + " more scenes"),
      knop: gehad ? ct("Nog eens","Again") : ct("Luisteren","Listen")
    };
  });
}
function renderAudPlank(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var items = audPlankItems();
  var open = items.filter(function(x){ return x.staat !== "dicht"; }).length;
  el.innerHTML = "<h2>Escuchar \\ud83d\\udc42</h2>" +
    "<p class='muted'>" + ct("Een gesprek horen en zeggen waar het over ging.",
                             "Hear a conversation and say what it was about.") + "</p>" +
    plankHtml(items) +
    (open > 1 ? "<div class='row' style='margin-top:10px'><button class='ghost' id='btnAudGok'>" +
      ct("Verras me","Surprise me") + "</button></div>" : "");
  plankWire(el, function(id){
    var sc = AUDICIONES.filter(function(x){ return x.id === id; })[0];
    if(!sc) return;
    audStop(); audSc = sc; audStap = 0; audGoed = 0; audGehoord = 0; audAnt = []; audGeenAudio = false; audRegel = -1;
    audMenu = false; renderFunAudicion();
  });
  var bg = document.getElementById("btnAudGok");
  if(bg) bg.onclick = function(){ audStop(); audNieuw(); audMenu = false; renderFunAudicion(); };
}

'''

if DOE_APP:
    rep(A_CSS, PLANK_CSS + A_CSS)
    rep(A_MOTOR, PLANK_JS + A_MOTOR)

    # Escuchar-plank achter de motor, en renderFunAudicion begint met de vraag of we op het menu staan.
    rep(A_RENDER, ESC_MENU + '''function renderFunAudicion(){
  var el = document.getElementById("funCard");
  if(!el) return;
  /* v23.77: de plank is het beginscherm van Escuchar. De lesflow zet audMenu zelf op false via
     audNieuw(), want daar heb je geen keuze: die scene hoort bij je les. */
  if(audMenu && !(lesFlow && lesFlow.stap === "produceren" && lesFlow.gekozenSpel === "audi")){
    renderAudPlank(); return;
  }
  if(!audSc) audNieuw();
  var sc = audSc;''')

    # "Volgende scene" gaat terug naar de plank in plaats van blind de volgende te kiezen.
    rep(A_NIEUWKNOP, '''  var bn = document.getElementById("btnAudNieuw");
  /* v23.77: terug naar de plank in plaats van blind de volgende scene. Je hebt er net een af; dit
     is precies het moment waarop je wil zien wat dat opende. */
  if(bn) bn.onclick = function(){ audStop(); audMenu = true; renderFunAudicion(); };''')

    # Vanuit de speeltuin land je voortaan op de plank, ook als je er net een scene af had. En de
    # regel voor dictado gaat weg: die zet twee variabelen die nergens meer bestaan. Dictado is er
    # sinds v21.4 niet meer (het traint transcriberen, geen begrijpen) en is vervangen door
    # Escuchar; Stefan, 13 aug: "dictado kan weg en werd vervangen door escuchar."
    rep('''  if(v === "dictado"){ dIdx = null; dRonde = null; }''',
        '''  /* v23.77: hier stond een regel voor dictado, die twee variabelen leegzette die nergens
     meer bestaan: het scherm is er sinds v21.4 niet meer. Stefan, 13 aug: "dictado kan weg en werd
     vervangen door escuchar." In de plaats daarvan land je bij Escuchar altijd op de plank, ook als
     je er net een scene af had; dat is precies het moment waarop je wil zien wat dat opende. */
  if(v === "audi"){ audMenu = true; }''')

    # audNieuw() wordt door de lesflow gebruikt en moet het menu dus overslaan.
    rep('''function audNieuw(){
  audSc = audKies(); audStap = 0; audGoed = 0; audGehoord = 0; audAnt = []; audGeenAudio = false; audRegel = -1;
}''', '''function audNieuw(){
  audSc = audKies(); audStap = 0; audGoed = 0; audGehoord = 0; audAnt = []; audGeenAudio = false; audRegel = -1;
  // v23.77: wie hier komt heeft al een scene, dus geen menu. Zie renderFunAudicion().
  audMenu = false;
}''')

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
