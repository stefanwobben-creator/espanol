#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.126: de tweede route. Het presente in zes patronen, en de volgorde komt uit de ladder.

## Wat erbij komt

De zes patroonlessen van v23.125 stonden los. Nu staan ze in een route, met een hertoets erachter:

    1  de yo-vorm op -go              6 werkwoorden, één letter
    2  la bota: e wordt ie            7, de grootste rij
    3  la bota: o/u wordt ue          4
    4  la bota: e wordt i             2
    5  de yo-vorm op -oy              4
    6  de twee losse                  sé, veo
    7  welk patroon is dit?           komt nog
    8  gestold?                       tien vormen uit de 22, drie dagen later

-go eerst, en dat is met opzet. Het is één letter en zes werkwoorden, en drie ervan (tener, venir,
decir) hebben daarnaast ook nog een schoen. Ken je -go, dan is de schoen daarna het enige wat er
aan die drie nog overblijft. Andersom leer je tengo twee keer als iets nieuws.

## De volgorde is geen tweede lijst

CONJ_FASES beschrijft al in welke volgorde de tijden opengaan:

    ar er ir seis onreg presente | indefreg indef | imperfreg imperf | perfecto | subjuntivo | mix

Een route erft zijn plaats uit die ladder (gramPadRang), en niet uit zijn positie in het array.
Dat is precies de fout die v23.120 rechtzette: vier systemen die iets zeggen over hetzelfde
onderwerp en niets van elkaar weten.

De volgorde stelt voor, hij sluit niets af. Op slot zetten doet de Conjugador al. Welke route
bovenaan staat is daarom: de route waar je in staat (begonnen, nog niet gestold), en anders de
eerste die nog niet klaar is. Zo word je niet van een route afgeduwd waar je halverwege in zit.

## De hertoets werd generiek

hertoetsBouw() trok drie betekenisvragen uit BROK_TIJD (Nederlandse zinnen over achtergrond of
gebeurtenis) en zeven vormvragen uit p.tijden. Voor het presente klopt geen van beide: die zinnen
gaan over de verleden tijd, en "alle presente-werkwoorden" is 33 terwijl deze route er 22
onderwijst.

Nu leidt hij allebei af uit het pad zelf:

    betekenisvragen   alleen als het pad een betekenisstap heeft
    de werkwoorden    de pools van de lesstappen van dat pad

Voor de verleden tijd verandert daarmee niets (die lesstappen zijn hele tijden, dus alle
werkwoorden van die tijd). Voor het presente meet de hertoets precies de 22 die de route
onderwijst, en niet hablar.

## Wat dit expres NIET doet

De volgorde binnen de verleden tijd blijft zoals hij is: imperfecto vóór indefinido, terwijl
CONJ_FASES het andersom doet. Ik heb die volgorde niet gekozen maar geërfd van welke uitleglessen
toevallig bestonden, en indefinido hoort eerst. Maar Stefan staat er middenin (3 van de 8), en de
route omgooien waar iemand in staat is het soort verandering waarvan je de app niet meer
vertrouwt. Bij de volgende lege route recht getrokken, niet nu.
"""

import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.126"

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


# ------------- 1. de tweede route

rep(
    '''     {brok:"pad.indefimperf", soort:"hertoets", view:"hertoets",
      nl:"Gestold?", en:"Has it set?",
      subNl:"Tien gemengde opgaven, op zijn vroegst drie dagen na de rest. Pas dan is dit punt echt af.",
      subEn:"Ten mixed items, at the earliest three days after the rest. Only then is this point really done."}
   ]}
];''',
    '''     {brok:"pad.indefimperf", soort:"hertoets", view:"hertoets",
      nl:"Gestold?", en:"Has it set?",
      subNl:"Tien gemengde opgaven, op zijn vroegst drie dagen na de rest. Pas dan is dit punt echt af.",
      subEn:"Ten mixed items, at the earliest three days after the rest. Only then is this point really done."}
   ]},
  /* v23.126: de tweede route. De zes patroonlessen van v23.125 stonden los; hier staan ze in een
     volgorde met een hertoets erachter.

     -go staat vooraan en dat is met opzet: het is \\u00e9\\u00e9n letter en zes werkwoorden, en drie ervan
     (tener, venir, decir) hebben daarn\\u00e1ast ook nog een schoen. Ken je -go, dan is de schoen
     daarna het enige wat er aan die drie nog overblijft. Andersom leer je tengo twee keer als
     iets nieuws.

     Geen stap voor het regelmatige presente. Die staat al vijf fasen lang in de Conjugador, en
     een route die je opnieuw hablar laat typen is een route die je overslaat. */
  {id:"presente",
   tijden:["presente"],
   nl:"Het presente: de 22 onregelmatige zijn zes patronen",
   en:"The present tense: the 22 irregulars are six patterns",
   uitNl:"Van de 33 werkwoorden zijn er 22 onregelmatig in het presente. Dat lijken 22 rijtjes om uit je hoofd te leren. Uitgerekend zijn het er zes, en het zijn de werkwoorden die je het vaakst nodig hebt.",
   uitEn:"Of the 33 verbs, 22 are irregular in the present tense. That looks like 22 rows to memorise. Worked out, there are six, and they are the verbs you need most often.",
   stappen:[
     {brok:"les.yo.go", soort:"les", view:"les", arg:"yo.go",
      nl:"De yo-vorm op -go", en:"The yo form in -go",
      subNl:"Zes werkwoorden, \\u00e9\\u00e9n letter. Begin hier: drie van deze zes krijgen straks ook nog een schoen.",
      subEn:"Six verbs, one letter. Start here: three of these six also get a boot later on."},
     {brok:"les.schoen.ie", soort:"les", view:"les", arg:"schoen.ie",
      nl:"La bota: e wordt ie", en:"La bota: e becomes ie",
      subNl:"De grootste rij, zeven werkwoorden. De stam wisselt bij yo, t\\u00fa, \\u00e9l en ellos, en juist niet bij nosotros en vosotros.",
      subEn:"The biggest row, seven verbs. The stem changes at yo, t\\u00fa, \\u00e9l and ellos, and not at nosotros and vosotros."},
     {brok:"les.schoen.ue", soort:"les", view:"les", arg:"schoen.ue",
      nl:"La bota: o wordt ue", en:"La bota: o becomes ue",
      subNl:"Dezelfde laars, andere klinker. Jugar hoort erbij met een u, en is daar het enige werkwoord in.",
      subEn:"The same boot, another vowel. Jugar belongs here with a u, and is the only verb that does that."},
     {brok:"les.schoen.i", soort:"les", view:"les", arg:"schoen.i",
      nl:"La bota: e wordt i", en:"La bota: e becomes i",
      subNl:"De kleinste laars: geen ie maar een enkele i. Twee werkwoorden, en die ken je nu allebei al van -go.",
      subEn:"The smallest boot: a single i, not ie. Two verbs, and you know both from -go by now."},
     {brok:"les.yo.oy", soort:"les", view:"les", arg:"yo.oy",
      nl:"De yo-vorm op -oy", en:"The yo form in -oy",
      subNl:"Vier werkwoorden: ser, estar, ir en dar. Vier die je elke dag nodig hebt.",
      subEn:"Four verbs: ser, estar, ir and dar. Four you need every day."},
     {brok:"les.yo.los", soort:"les", view:"les", arg:"yo.los",
      nl:"De twee losse", en:"The two loose ones",
      subNl:"S\\u00e9 en veo volgen niets. Twee vormen om gewoon te onthouden, en dat mag: twee is te doen.",
      subEn:"S\\u00e9 and veo follow nothing. Two forms to simply memorise, and that is fine: two is doable."},
     {brok:"presente.patroon", soort:"keuze", view:null,
      nl:"Welk patroon is dit?", en:"Which pattern is this?",
      subNl:"Komt nog. Door elkaar herkennen is de laatste stap, niet de eerste.",
      subEn:"Coming. Telling them apart comes last, not first."},
     {brok:"pad.presente", soort:"hertoets", view:"hertoets",
      nl:"Gestold?", en:"Has it set?",
      subNl:"Tien vormen uit de tweeëntwintig, op zijn vroegst drie dagen na de rest.",
      subEn:"Ten forms out of the twenty-two, at the earliest three days after the rest."}
   ]}
];

/* ===== v23.126: welke route staat er nu? =====

   De volgorde van de routes is die van de Conjugador-ladder en niet een tweede lijst. CONJ_FASES
   zegt al in welke volgorde de tijden opengaan; een route erft daaruit zijn plaats. Zijn positie
   in het array hierboven zegt niets.

   De volgorde stelt voor, hij sluit niets af: op slot zetten doet de Conjugador al. Daarom is de
   route die bovenaan staat de route waar je in st\\u00e1\\u00e1t, en pas als je nergens in staat de eerste
   die nog niet klaar is. Anders zou een nieuwe route je van een route afduwen waar je halverwege
   in zit. */
function gramPadRang(p){
  var beste = CONJ_FASES.length;
  (p.tijden || []).forEach(function(t){
    for(var i = 0; i < CONJ_FASES.length; i++){
      if(CONJ_FASES[i].tijd === t){ if(i < beste) beste = i; return; }
    }
  });
  return beste;
}
function gramPadenGeordend(){
  return GRAM_PADEN.slice().sort(function(a, b){ return gramPadRang(a) - gramPadRang(b); });
}
function gramPadVan(id){
  for(var i = 0; i < GRAM_PADEN.length; i++) if(GRAM_PADEN[i].id === id) return GRAM_PADEN[i];
  return null;
}''',
)

# ------------- 2. gramPadBegonnen / gramPadNu, na gramPadKlaar

rep(
    '''function gramPadKlaar(p){
  for(var i = 0; i < p.stappen.length; i++){
    var x = gramPadStap(p, i);
    if(x.bestaat && !x.af) return false;
  }
  return true;
}''',
    '''function gramPadKlaar(p){
  for(var i = 0; i < p.stappen.length; i++){
    var x = gramPadStap(p, i);
    if(x.bestaat && !x.af) return false;
  }
  return true;
}
function gramPadBegonnen(p){
  for(var i = 0; i < p.stappen.length; i++) if(gramPadStap(p, i).af) return true;
  return false;
}
function gramPadNu(){
  var L = gramPadenGeordend(), i;
  for(i = 0; i < L.length; i++) if(gramPadBegonnen(L[i]) && !gramPadKlaar(L[i])) return L[i];
  for(i = 0; i < L.length; i++) if(!gramPadKlaar(L[i])) return L[i];
  return L[0] || null;
}
/* Welke route het routescherm laat zien. Null betekent "die van nu"; klik je in de lijst op een
   andere, dan staat hij hier tot je het scherm verlaat. */
var padView = null;
function gramPadHuidig(){
  return (padView && gramPadVan(padView)) || gramPadNu();
}''',
)

# ------------- 3. de drie plekken die GRAM_PADEN[0] hardcodeerden

rep(
    '''  if(!hertoetsSpel) hertoetsStart(GRAM_PADEN[0]);''',
    '''  if(!hertoetsSpel) hertoetsStart(gramPadHuidig());''',
)

rep(
    '''function renderFunPad(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var p = GRAM_PADEN[0];''',
    '''function renderFunPad(){
  var el = document.getElementById("funCard");
  if(!el) return;
  var p = gramPadHuidig();
  if(!p) return;''',
)

rep(
    '''function gramRouteHtml(){
  var p = GRAM_PADEN[0];
  if(!p) return "";''',
    '''function gramRouteHtml(){
  var p = gramPadNu();
  if(!p) return "";''',
)

rep(
    '''function gramHomeWire(){
  var p = GRAM_PADEN[0];
  var bv = document.getElementById("btnGramVerder");
  if(bv && p) bv.onclick = function(){ gramPadGa(p, gramPadVolgende(p)); };
  /* alle gram-tegels, de route incluis: die hangt aan de knop onder de routekaart */
  tegelWire(gramTegels());
}''',
    '''function gramHomeWire(){
  var p = gramPadNu();
  var bv = document.getElementById("btnGramVerder");
  if(bv && p) bv.onclick = function(){ padView = p.id; gramPadGa(p, gramPadVolgende(p)); };
  /* alle gram-tegels, de route incluis: die hangt aan de knop onder de routekaart */
  tegelWire(gramTegels());
  Array.prototype.forEach.call(document.querySelectorAll("[data-padga]"), function(b){
    b.onclick = function(){
      padView = b.getAttribute("data-padga");
      speelStart(spelInfoVan("pad"));
    };
  });
}''',
)

# de knop onder de routekaart opent de route van nu, niet een blijven hangen keuze van daarnet
rep(
    '''    "<div class='row' style='margin-top:8px'><button class='mini' id='" +
      ((spelInfoVan("pad") || {}).id || "btnGramRoute") + "'>" +
      ct("Bekijk de hele route", "See the whole route") + "</button></div></div>";
}''',
    '''    "<div class='row' style='margin-top:8px'><button class='mini' data-padga='" + p.id + "' id='" +
      ((spelInfoVan("pad") || {}).id || "btnGramRoute") + "'>" +
      ct("Bekijk de hele route", "See the whole route") + "</button></div></div>" +
    gramAndereRoutesHtml(p);
}
/* v23.126: de andere routes. Weglaten mag nooit verstoppen worden (v23.53), dus staan ze er, maar
   klein en zonder knop: de route van nu is de route van nu. De volgorde komt uit de ladder. */
function gramAndereRoutesHtml(nu){
  var rest = gramPadenGeordend().filter(function(p){ return p.id !== (nu || {}).id; });
  if(!rest.length) return "";
  return "<div class='card' id='gramRoutes'><h2>" + ct("De andere routes", "The other routes") + "</h2>" +
    "<p class='muted' style='font-size:.88rem'>" +
    ct("In de volgorde waarin de Conjugador ze openzet. Je mag vooruit kijken; de route hierboven is waar je nu staat.",
       "In the order the Conjugador unlocks them. You may look ahead; the route above is where you stand now.") + "</p>" +
    rest.map(function(p){
      var t = gramRouteTelling(p);
      return "<div class='lesson' data-padga='" + p.id + "' style='cursor:pointer'>" +
        "<div class='lnum'>" + (gramPadKlaar(p) ? "\\u2713" : t.af + "/" + t.telt) + "</div>" +
        "<div class='lbody'><b>" + ct(p.nl, p.en) + "</b><span>" + gramRouteRegel(p) + "</span></div>" +
        "<div class='lstatus'>\\u25b6</div></div>";
    }).join("") + "</div>";
}''',
)

# het routescherm zelf: de keuze vasthouden zolang je erin zit, en loslaten als je weggaat
rep(
    '''  var tb = document.getElementById("btnFunTerug");
  if(tb) tb.onclick = function(){ funTerug(); };
}

/* ================= DE GRAMMATICA-TAB (v23.124) =================''',
    '''  var tb = document.getElementById("btnFunTerug");
  if(tb) tb.onclick = function(){ padView = null; funTerug(); };
}

/* ================= DE GRAMMATICA-TAB (v23.124) =================''',
)

# ------------- 4. de hertoets leidt zijn inhoud af uit het pad

rep(
    '''function hertoetsBouw(p){
  var tijden = (p.tijden || ["imperfecto", "indefinido"]).filter(function(t){ return !!conjTiempo(t); });
  var rij = [];
  geschud(BROK_TIJD.slice()).slice(0, 3).forEach(function(z){ rij.push({soort:"betekenis", z:z}); });
  var vorm = [];
  tijden.forEach(function(t){
    geschud(conjAlleVerbs(t)).forEach(function(v){
      for(var i = 0; i < 6; i++) vorm.push({soort:"vorm", v:v, p:i, t:t});
    });
  });
  geschud(vorm).slice(0, HERTOETS_LEN - rij.length).forEach(function(x){ rij.push(x); });
  return geschud(rij);
}''',
    '''/* v23.126: hier stonden twee dingen vast die per route verschillen. Drie betekenisvragen uit
   BROK_TIJD zijn Nederlandse zinnen over achtergrond-of-gebeurtenis, en die gaan alleen over de
   verleden tijd. En "alle werkwoorden van p.tijden" is voor het presente 33 stuks, terwijl die
   route er 22 onderwijst; dan zou de hertoets vooral hablar meten.

   Allebei nu afgeleid uit het pad zelf: betekenisvragen alleen als het pad een betekenisstap heeft,
   en de werkwoorden uit de pools van zijn lesstappen. Voor de verleden tijd verandert er daarmee
   niets, want die lesstappen zijn hele tijden. */
function hertoetsPool(p){
  var uit = [], gezien = {};
  (p.stappen || []).forEach(function(s){
    if(s.soort !== "les" || !s.arg) return;
    var r = lesRij(s.arg);
    if(!r) return;
    var vs = r.tijd ? conjAlleVerbs(r.t) : conjPatroonPool(s.arg);
    vs.forEach(function(v){
      var k = v.inf + "|" + r.t;
      if(gezien[k]) return;
      gezien[k] = 1;
      uit.push({v:v, t:r.t});
    });
  });
  if(uit.length) return uit;
  /* een pad zonder lesstap valt terug op zijn tijden */
  (p.tijden || []).filter(function(t){ return !!conjTiempo(t); }).forEach(function(t){
    conjAlleVerbs(t).forEach(function(v){ uit.push({v:v, t:t}); });
  });
  return uit;
}
function hertoetsBetekenisN(p){
  var heeft = (p.stappen || []).some(function(s){ return s.soort === "betekenis"; });
  return heeft ? 3 : 0;
}
function hertoetsBouw(p){
  var rij = [];
  geschud(BROK_TIJD.slice()).slice(0, hertoetsBetekenisN(p)).forEach(function(z){
    rij.push({soort:"betekenis", z:z});
  });
  var vorm = [];
  geschud(hertoetsPool(p)).forEach(function(x){
    for(var i = 0; i < 6; i++) vorm.push({soort:"vorm", v:x.v, p:i, t:x.t});
  });
  geschud(vorm).slice(0, HERTOETS_LEN - rij.length).forEach(function(x){ rij.push(x); });
  return geschud(rij);
}''',
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
