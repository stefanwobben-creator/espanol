#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.124: de verhuizing. Grammatica woont op de Grammatica-tab.

## Waarom

Stefan, met twee schermafbeeldingen naast elkaar: "er staan nu dingen verspreid bij Spelen en
dingen bij Grammatica. Zijn ze op elkaar afgestemd? Het moet sowieso niet bij Spelen maar bij
Grammatica."

En een dag later, toen hij de route zocht die ik hem net geleverd had: "hoe heet ie dan? ik vind
hem niet."

Hij kon hem niet vinden omdat hij de goede tab openhad. De route heette "Grammatica", stond elfde
in de Speeltuin tussen Crucigrama en Memory, en de tab die Grammatica heet wist niet dat hij
bestond.

## De regel stond er al

Sinds v21.5 staat in dit bestand: onder Oefenen telt het mee voor je niveau, onder Spelen niet.
De route, de les, de brok, "Wie is dit?" en "Welke tijd is dit?" tellen allemaal mee. Ze stonden
aan de verkeerde kant van die streep, en dat was geen ontwerpkeuze maar luiheid: de speeltuinkaart
was de enige plek waar ik een nieuw scherm kwijt kon zonder iets te verbouwen.

## Wat er verandert

    spelInfo()          elke tegel draagt zelf waar hij woont:  gram:true
    Speeltuin           spelInfo() zonder de gram-tegels
    Grammatica-tab      de routekaart + de vier losse oefeningen
    dagkaart            afgeleid uit gram, niet uit een tweede handgeschreven lijst
    terugknop           uit een grammatica-oefening kom je uit op de Grammatica-tab
    balk                Oefenen licht op zolang je in een grammatica-oefening zit

De Grammatica-tab wordt daarmee:

    De route            wat het pad nu van je vraagt, met een knop die dat opent
    Los oefenen         de les, de brok, wie is dit?, welke tijd is dit?
    Onder de knie       de bestaande onderwerpen (ongewijzigd)
    Naslag / toetsjes   (ongewijzigd)

## Wat dit expres NIET doet

Geen enkele oefening verandert van binnen. Dit is een verhuizing, geen verbouwing: één variabele,
zodat als er iets stukgaat, duidelijk is wat het was. Het pad per tijd (presente met -ar/-er/-ir,
subjuntivo, perfecto) is de volgende ronde.

## Twee lijsten die uit elkaar liepen, weg

DAGSPEL_UIT somde met de hand op welke tegels niet op de dagkaart horen: {avt, duel, brok, omkeer,
tijdvorm, les, pad}. Die laatste vijf zijn precies de gram-tegels. Dat is nu afgeleid, en houdt
op te bestaan als vergeetplek. Wat overblijft is de echte inhoud van die lijst: Aventura staat
vast op de kaart, en Palabra Duel heeft een tweede speler nodig.

Zelfde reden voor de rij-opmaak en de klikafhandeling: die stonden in renderFun() en zouden nu op
twee plekken staan. Ze zijn eruit gelicht (tegelLijstHtml / tegelWire / speelStart) zodat beide
tabs dezelfde regel tekenen en dezelfde klik afhandelen. Dat is dezelfde fout die v23.112
repareerde en die ik hier bijna opnieuw maakte.
"""

import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.124"

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


# ------------- 1. elke tegel draagt zelf waar hij woont

rep(
    '''    {v:"brok",    id:"ftBrok",    e:"\\ud83c\\udfad",            t:ct("Achtergrond of gebeurtenis","Background or event"),''',
    '''    {v:"brok",    id:"ftBrok",    e:"\\ud83c\\udfad", gram:true,  t:ct("Achtergrond of gebeurtenis","Background or event"),''',
)

rep(
    '''    {v:"omkeer",  id:"ftOmkeer",  e:"\\ud83d\\udd0e",            t:ct("Wie is dit?","Who is this?"),''',
    '''    {v:"omkeer",  id:"ftOmkeer",  e:"\\ud83d\\udd0e", gram:true,  t:ct("Wie is dit?","Who is this?"),''',
)

rep(
    '''    {v:"pad",     id:"ftPad",     e:"\\ud83e\\udded",            t:ct("Grammatica","Grammar"),''',
    '''    {v:"pad",     id:"ftPad",     e:"\\ud83e\\udded", gram:true,  t:ct("De route","The route"),''',
)

# en meteen: "in vijf stappen" stond er nog terwijl LES_STAPPEN er sinds v23.118 zes heeft.
# Vierde keer dat een getal in tekst achterliep op de data, dus nu uit de data.
rep(
    '''    {v:"les",     id:"ftLes",     e:"\\ud83d\\udcd6",            t:ct("De les","The lesson"), s:ct("E\\u00e9n tijd tegelijk, in vijf stappen. De eerste twee stellen geen vraag.","One tense at a time, in five steps. The first two ask nothing."), gezien:false, verse:function(){ lesSpel = null; }},''',
    '''    {v:"les",     id:"ftLes",     e:"\\ud83d\\udcd6", gram:true,  t:ct("De les","The lesson"), s:ct("E\\u00e9n tijd tegelijk, in " + LES_STAPPEN.length + " stappen. De eerste twee stellen geen vraag.","One tense at a time, in " + LES_STAPPEN.length + " steps. The first two ask nothing."), gezien:false, verse:function(){ lesSpel = null; }},''',
)

rep(
    '''    {v:"tijdvorm", id:"ftTijdvorm", e:"\\u23f3",                t:ct("Welke tijd is dit?","Which tense is this?"),''',
    '''    {v:"tijdvorm", id:"ftTijdvorm", e:"\\u23f3",     gram:true,  t:ct("Welke tijd is dit?","Which tense is this?"),''',
)

# ------------- 2. de twee lijsten die uit spelInfo() volgen

rep(
    '''function spelInfoVan(v){
  var L = spelInfo(), i;
  for(i = 0; i < L.length; i++){ if(L[i].v === v) return L[i]; }
  return null;
}''',
    '''function spelInfoVan(v){
  var L = spelInfo(), i;
  for(i = 0; i < L.length; i++){ if(L[i].v === v) return L[i]; }
  return null;
}
/* ===== v23.124: waar een tegel woont =====

   Stefan: "het moet sowieso niet bij Spelen maar bij Grammatica." En toen hij de route zocht die
   ik hem net geleverd had: "hoe heet ie dan? ik vind hem niet." Hij keek op de Grammatica-tab, en
   de route stond elfde in de Speeltuin tussen Crucigrama en Memory.

   De streep bestond al sinds v21.5: onder Oefenen telt het mee voor je niveau, onder Spelen niet.
   Deze vijf tellen mee. Ze staan nu aan de goede kant, en de tegel draagt dat zelf (gram:true), zodat
   de Speeltuin, de Grammatica-tab en de dagkaart alle drie hetzelfde ene veld lezen. */
function speelTegels(){ return spelInfo().filter(function(x){ return !x.gram; }); }
function gramTegels(){ return spelInfo().filter(function(x){ return !!x.gram; }); }
/* De hertoets heeft geen eigen tegel (je komt er alleen via het pad) maar hoort wel bij dit blok:
   ook daaruit hoor je terug te komen op de Grammatica-tab en niet in de Speeltuin. */
function gramViews(){
  var r = ["hertoets"];
  gramTegels().forEach(function(x){ r.push(x.v); });
  return r;
}
function isGramView(v){ return !!v && gramViews().indexOf(v) !== -1; }''',
)

rep(
    '''/* v23.109: omkeer erbij, om dezelfde reden als brok. Dit zijn metingen, geen dagportie: ze
   horen niet mee te tellen in het dagritme en het dagscherm hoort er niet naar te wijzen. */
var DAGSPEL_UIT = {avt:1, duel:1, brok:1, omkeer:1, tijdvorm:1, les:1, pad:1};''',
    '''/* v23.124: hier stonden brok, omkeer, tijdvorm, les en pad ook in, en dat waren precies de
   gram-tegels. Een tweede handgeschreven lijst met dezelfde namen erin is een vergeetplek: wie er
   morgen een grammatica-oefening bij zet, zet hem hier niet bij en vindt hem dan op de dagkaart
   terug tussen de spelletjes. Nu afgeleid. Wat overblijft is wat er echt in thuishoort: Aventura
   staat vast op de kaart (dat is het grote spel) en Palabra Duel heeft een tweede speler nodig. */
var DAGSPEL_UIT = {avt:1, duel:1};''',
)

rep(
    '''function dagSpellen(){
  return spelInfo().filter(function(x){ return !DAGSPEL_UIT[x.v]; });
}''',
    '''function dagSpellen(){
  return speelTegels().filter(function(x){ return !DAGSPEL_UIT[x.v]; });
}''',
)

# ------------- 3. één rij-opmaak en één klikafhandeling, voor beide tabs

rep(
    '''  var SPEELMENU = spelInfo();
  var nuHtml = "", straksHtml = "";
  SPEELMENU.forEach(function(g){
    var kop = "<div class='lnum'>"+g.e+"</div><div class='lbody'><b>"+g.t+"</b><span>";
    if(speelKlaar(g.v)){
      nuHtml += "<div class='lesson' id='"+g.id+"'>"+kop+spelZin(g.s)+"</span></div><div class='lstatus'>\\u25b6</div></div>";
    } else {
      straksHtml += "<div class='lesson' style='opacity:.5'>"+kop+speelWacht(g.v)+"</span></div><div class='lstatus'>\\u00b7</div></div>";
    }
  });''',
    '''  /* v23.124: de grammatica-tegels staan hier niet meer, die wonen op de Grammatica-tab. De
     opmaak en de klik staan in tegelLijstHtml/tegelWire, want anders zou dezelfde rij op twee
     plekken getekend worden en dat is precies wat in v23.112 een dode tegel opleverde. */
  var SPEELMENU = speelTegels();
  var rijen = tegelLijstHtml(SPEELMENU);
  var nuHtml = rijen.nu, straksHtml = rijen.straks;''',
)

rep(
    '''  bindUitnodig("speeltuin");
  function wire(id, fn){ var b = document.getElementById(id); if(b) b.onclick = fn; }
  /* v23.112: hier stond een handgeschreven rij van tien wire-regels naast SPEELMENU. Twee lijsten
     met dezelfde tegels erin, met de hand synchroon gehouden, en dus liepen ze uit elkaar: de
     omkering-tegel van v23.109 stond wel in spelInfo() en niet in die rij, dus hij tekende netjes
     en deed niets. Nu loopt de koppeling over SPEELMENU, en is een tegel zonder afhandeling
     onmogelijk. Wat per spel anders is staat als data bij dat spel (zie spelInfo). */
  SPEELMENU.forEach(function(g){
    wire(g.id, g.open || function(){
      if(g.gezien !== false) speelGezien(g.v);
      if(g.verse) g.verse();
      funView = g.v;
      navPush({t:"fun", v:g.v});
      renderFun();
    });
  });''',
    '''  bindUitnodig("speeltuin");
  /* v23.112: hier stond een handgeschreven rij van tien wire-regels naast SPEELMENU, en die liep
     uit de pas: de omkering-tegel stond wel in spelInfo() en niet in die rij, dus hij tekende
     netjes en deed niets. De koppeling loopt sindsdien over de lijst zelf. v23.124 verhuist hem
     naar tegelWire(), zodat de Grammatica-tab hem hergebruikt in plaats van hem na te bouwen. */
  tegelWire(SPEELMENU);''',
)

# de gedeelde opmaak + klik, vlak boven renderFun()
rep(
    '''function renderFun(){
  var el = document.getElementById("funCard");
  if(!el) return;
  if(duelCur){ renderDuel(); return; }''',
    '''/* ===== v23.124: één rij, twee tabs =====
   De Speeltuin en de Grammatica-tab tekenen dezelfde soort regel en handelen dezelfde klik af.
   Twee kopieën daarvan zouden na precies één ronde uit elkaar lopen; zie de toelichting bij
   speelTegels(). */
function tegelLijstHtml(lijst){
  var nu = "", straks = "";
  lijst.forEach(function(g){
    var kop = "<div class='lnum'>"+g.e+"</div><div class='lbody'><b>"+g.t+"</b><span>";
    if(speelKlaar(g.v)){
      nu += "<div class='lesson' id='"+g.id+"'>"+kop+spelZin(g.s)+"</span></div><div class='lstatus'>\\u25b6</div></div>";
    } else {
      straks += "<div class='lesson' style='opacity:.5'>"+kop+speelWacht(g.v)+"</span></div><div class='lstatus'>\\u00b7</div></div>";
    }
  });
  return {nu:nu, straks:straks};
}
/* show() en niet renderFun(), en dat is nieuw: de tegel kan nu vanaf twee tabs aangeklikt worden.
   Vanaf Grammatica moet de speeltuinkaart eerst zichtbaar worden, en show() zet meteen het juiste
   vak in de balk aan. Op de Speeltuin zelf verandert er niets, want show("speeltuin") tekent de
   kaart opnieuw. */
function speelStart(g){
  if(!g) return;
  if(g.open){ g.open(); return; }
  if(g.gezien !== false) speelGezien(g.v);
  if(g.verse) g.verse();
  funView = g.v;
  navPush({t:"fun", v:g.v});
  show("speeltuin", true);
}
function tegelWire(lijst){
  lijst.forEach(function(g){
    var b = document.getElementById(g.id);
    if(b) b.onclick = function(){ speelStart(g); };
  });
}
/* Waar je uitkomt als je een oefening verlaat, hangt af van waar hij woont. Een
   grammatica-oefening brengt je terug naar de Grammatica-tab: daar ben je vandaan gekomen, en
   daar staat wat je nu kunt doen. */
function funTerug(){
  var v = funView;
  funView = null;
  if(isGramView(v)){ gwSess = null; gcLeesId = null; show("spiekbrief"); return; }
  renderFun();
}

function renderFun(){
  var el = document.getElementById("funCard");
  if(!el) return;
  if(duelCur){ renderDuel(); return; }''',
)

# ------------- 4. de balk: Oefenen licht op in een grammatica-oefening

rep(
    '''var OEFEN_FUNVIEWS = ["audi", "corr", "conj"];''',
    '''var OEFEN_FUNVIEWS = ["audi", "corr", "conj"];
/* v23.124: de grammatica-oefeningen komen er afgeleid bij. Ze wonen op de Grammatica-tab, en die
   laat Oefenen oplichten, dus hoort de balk niet om te springen zodra je er een opent. */
function inOefenFunView(v){ return OEFEN_FUNVIEWS.indexOf(v) !== -1 || isGramView(v); }''',
)

rep(
    '''                (tabId === "speeltuin" && OEFEN_FUNVIEWS.indexOf(funView) !== -1);''',
    '''                (tabId === "speeltuin" && inOefenFunView(funView));''',
)

# ------------- 5. de terugknoppen van de vijf grammatica-schermen

rep(
    '''function(){ funView = null; brokSpel = null; renderFun(); }''',
    '''function(){ brokSpel = null; funTerug(); }''',
    n=2,
)

rep(
    '''function(){ funView = null; omkeerSpel = null; renderFun(); }''',
    '''function(){ omkeerSpel = null; funTerug(); }''',
    n=3,
)

rep(
    '''  var bv = document.getElementById("btnPadVerder");
  if(bv) bv.onclick = function(){ gramPadGa(p, volgende); };
  var tb = document.getElementById("btnFunTerug");
  if(tb) tb.onclick = function(){ funView = null; renderFun(); };''',
    '''  var bv = document.getElementById("btnPadVerder");
  if(bv) bv.onclick = function(){ gramPadGa(p, volgende); };
  var tb = document.getElementById("btnFunTerug");
  if(tb) tb.onclick = function(){ funTerug(); };''',
)

rep(
    '''  var terug = function(){ funView = null; lesSpel = null; renderFun(); };''',
    '''  var terug = function(){ lesSpel = null; funTerug(); };''',
)

rep(
    '''  var terug = function(){ funView = null; tijdvormSpel = null; renderFun(); };''',
    '''  var terug = function(){ tijdvormSpel = null; funTerug(); };''',
)

# ------------- 6. het routescherm: de wachtzin eruit gelicht, en de verwijzing naar de Speeltuin klopt niet meer

rep(
    '''  var stPad = brokLees(padId(p));
  if(padGehaald(p) && !stPad.gestold && !padMagHertoets(p)){
    padGehaaldStempel(p);
    var teGaan = padDagenTeGaan(p);
    html += "<div class='feedback bijna' id='padWacht'>" +
      ct("Gehaald. Nog " + teGaan + " " + (teGaan === 1 ? "dag" : "dagen") + " tot de hertoets.",
         "Passed. " + teGaan + " more " + (teGaan === 1 ? "day" : "days") + " until the recheck.") + "</div>" +''',
    '''  var stPad = brokLees(padId(p));
  if(padGehaald(p) && !stPad.gestold && !padMagHertoets(p)){
    padGehaaldStempel(p);
    html += "<div class='feedback bijna' id='padWacht'>" + padWachtZin(p) + "</div>" +''',
)

rep(
    '''  html += "<p class='muted' style='font-size:.82rem; margin-top:10px'>" +
    ct("Je kunt alles ook los blijven doen in de Speeltuin. Dit scherm dwingt niets af, het wijst alleen waar je bent.",
       "You can still do everything separately in the Playground. This screen enforces nothing, it just shows where you are.") + "</p>" +''',
    '''  html += "<p class='muted' style='font-size:.82rem; margin-top:10px'>" +
    ct("Je kunt alles ook los blijven doen: ze staan onder \\u201eLos oefenen\\u201d op deze tab. Dit scherm dwingt niets af, het wijst alleen waar je bent.",
       "You can still do everything separately: they are under \\u201cPractise separately\\u201d on this tab. This screen enforces nothing, it just shows where you are.") + "</p>" +''',
)

# het pad kan nu ook vanaf de Grammatica-tab starten, dus moet de speeltuinkaart zichtbaar worden
rep(
    '''  funView = s.view;
  navPush({t:"fun", v:s.view});
  renderFun();
}

function renderFunPad(){''',
    '''  funView = s.view;
  navPush({t:"fun", v:s.view});
  /* v23.124: show() en niet renderFun(), want dit wordt nu ook aangeroepen vanaf de routekaart op
     de Grammatica-tab, en dan staat de speeltuinkaart nog verstopt. */
  show("speeltuin", true);
}

function renderFunPad(){''',
)

# ------------- 7. de Grammatica-tab zelf

rep(
    '''/* ================= DE LES (v23.115) =================''',
    '''/* ================= DE GRAMMATICA-TAB (v23.124) =================

   Wat hieronder staat is geen nieuw scherm maar een adres. De route, de les en de drie metingen
   bestonden al; wat ontbrak was dat de tab die "Grammatica" heet ernaar wees. Stefan zocht de
   route daar, en vond alleen de spiekbrieven.

   De kaart bovenaan is met opzet een samenvatting en geen tweede routescherm: hij zegt wat de
   route nu van je vraagt en heeft \\u00e9\\u00e9n knop die dat opent. Alles wat hij toont is afgeleid uit
   GRAM_PADEN, dus een stap erbij verandert hier niets. */
function padWachtZin(p){
  var d = padDagenTeGaan(p);
  if(d === null) return "";
  return ct("Gehaald. Nog " + d + " " + (d === 1 ? "dag" : "dagen") + " tot de hertoets.",
            "Passed. " + d + " more " + (d === 1 ? "day" : "days") + " until the recheck.");
}
function gramRouteRegel(p){
  if(gramPadKlaar(p)) return ct("Gestold. Dit punt is echt af.", "Set. This point is really done.");
  var v = gramPadVolgende(p);
  if(v >= 0) return ct("Nu: ", "Now: ") + ct(p.stappen[v].nl, p.stappen[v].en);
  /* geen volgende stap en toch niet klaar: dan sta je in de wachttijd voor de hertoets */
  return padWachtZin(p);
}
/* Stappen die nog niet bestaan tellen niet mee in de teller. Anders zou de balk nooit vol kunnen
   worden en zou "8/9" blijven staan terwijl er niets meer te doen is. */
function gramRouteTelling(p){
  var af = 0, telt = 0;
  p.stappen.forEach(function(s, i){
    var x = gramPadStap(p, i);
    if(!x.bestaat) return;
    telt++;
    if(x.af) af++;
  });
  return {af:af, telt:telt};
}
function gramRouteHtml(){
  var p = GRAM_PADEN[0];
  if(!p) return "";
  var t = gramRouteTelling(p);
  var pct = t.telt ? Math.round(100 * t.af / t.telt) : 0;
  var v = gramPadVolgende(p);
  return "<div class='card' id='gramRoute'><h2>" + ct("De route", "The route") + " \\ud83e\\udded</h2>" +
    "<p class='muted' style='margin:0 0 2px'><b>" + ct(p.nl, p.en) + "</b></p>" +
    "<p class='muted' style='font-size:.88rem; margin:0 0 8px'>" + ct(p.uitNl, p.uitEn) + "</p>" +
    "<div class='boxrow'><div class='bar'><div style='width:" + pct + "%'></div></div>" +
      "<b style='width:52px; text-align:right'>" + t.af + "/" + t.telt + "</b></div>" +
    "<p id='gramRouteNu' style='margin:8px 0 10px'>" + gramRouteRegel(p) + "</p>" +
    (v >= 0
      ? "<div class='row'><button class='primary' id='btnGramVerder'>" +
          ct("Verder: ", "Continue: ") + ct(p.stappen[v].nl, p.stappen[v].en) + " \\u2192</button></div>"
      : "") +
    /* De knop draagt het id van de routetegel uit spelInfo(). Niet uit netheid: pw-tegels klikt
       elke tegel uit die lijst echt aan en eist dat er iets verandert. Zou de route hier onder een
       eigen naam staan, dan zou de tegel "pad" nergens meer op het scherm staan en zou precies de
       dode-tegelcontrole van v23.112 blind worden voor het pad. */
    "<div class='row' style='margin-top:8px'><button class='mini' id='" +
      ((spelInfoVan("pad") || {}).id || "btnGramRoute") + "'>" +
      ct("Bekijk de hele route", "See the whole route") + "</button></div></div>";
}
/* De routetegel zelf staat hier niet tussen: die is de kaart hierboven, met de knop eronder. */
function gramLosseTegels(){ return gramTegels().filter(function(g){ return g.v !== "pad"; }); }
function gramOefenHtml(){
  var lijst = gramLosseTegels();
  if(!lijst.length) return "";
  var r = tegelLijstHtml(lijst);
  return "<div class='card' id='gramOefen'><h2>" + ct("Los oefenen", "Practise separately") + "</h2>" +
    "<p class='muted'>" +
    ct("Dit zijn de oefeningen uit de route hierboven. De route wijst de volgorde aan; hier kies je zelf.",
       "These are the exercises from the route above. The route sets the order; here you choose yourself.") +
    "</p>" + r.nu + r.straks + "</div>";
}
function gramHomeHtml(){ return gramRouteHtml() + gramOefenHtml(); }
function gramHomeWire(){
  var p = GRAM_PADEN[0];
  var bv = document.getElementById("btnGramVerder");
  if(bv && p) bv.onclick = function(){ gramPadGa(p, gramPadVolgende(p)); };
  /* alle gram-tegels, de route incluis: die hangt aan de knop onder de routekaart */
  tegelWire(gramTegels());
}

/* ================= DE LES (v23.115) =================''',
)

rep(
    '''  el.innerHTML = gwLijstHtml() + spiekNaslagHtml() + gwToetsSectieHtml();''',
    '''  /* v23.124: de route en de losse oefeningen staan bovenaan, want dat is wat je hier komt doen.
     De onderwerpen eronder zijn naslag en herhaling, en die stonden er al. */
  el.innerHTML = gramHomeHtml() + gwLijstHtml() + spiekNaslagHtml() + gwToetsSectieHtml();
  gramHomeWire();''',
)

# ------------- 8. de rij in het Oefenen-menu zegt nu wat er staat

rep(
    '''    {id:"spiekbrief", soort:"tab", ico:"\U0001f4d0", t:ct("Grammatica","Grammar"),
     s:ct("Regels opzoeken en oefenen, zonder ze uit je hoofd te leren.","Look up the rules and practise them, no memorising.")}''',
    '''    {id:"spiekbrief", soort:"tab", ico:"\U0001f4d0", t:ct("Grammatica","Grammar"),
     s:ct("De route door de verleden tijd, de losse oefeningen en alle regels om op te zoeken.","The route through the past tense, the separate exercises, and all the rules to look up.")}''',
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
