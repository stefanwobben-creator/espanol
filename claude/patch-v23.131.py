#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.131: klaar voor vreemden. Vier dingen die alleen een eerste gebruiker ziet.

Doorlopen als vreemde op v23.128: verse browser, leeg geheugen, telefoonformaat, Nederlandse
browsertaal, A1, niveautest overgeslagen. Geen enkele JavaScript-fout. Wat er wel misging:

## 1. Het eerste scherm loog

De Vandaag-tab zei tegen iemand met nul woorden: "We gaan verder waar we gebleven waren. Je stopte
bij stap 1 van 4." De Woordjes-tab zei op datzelfde moment "Start je les". Een van de twee klopte
niet, en het was de tab waar je landt.

lesFlowHervatKan() keek alleen of er een opgeslagen stap van vandaag was. Die staat er al zodra de
flow begint, ook als je nog niets hebt beantwoord. De eis wordt: je zit voorbij de eerste stap, of
je hebt vandaag iets gedaan (newToday() > 0). Anders is er niets om verder te gaan.

## 2. De Grammatica-tab zette een beginner op onregelmatige werkwoorden

Wie hola, gracias en adiós kende, las: "Nu: De yo-vorm op -go". Alle zes de patroonlessen stonden
open, en de presente-route was "de route van nu" omdat hij rang 0 heeft in de ladder.

Dat is mijn fout van v23.125 en v23.126. De poort bestond al: CONJ_FASES zet de onregelmatige
werkwoorden pas open in fase "onreg", de vijfde van dertien. Een patroonles erft die poort nu, en
een route is pas "de route van nu" als zijn lesstappen ook echt te doen zijn. Staat er geen route
open, dan zegt het scherm wat er nodig is in plaats van een route te tonen die niemand kan lopen.

Niets hiervan is een nieuw niveau dat iemand bijhoudt: het volgt uit de Conjugador-ladder die er
al stond.

## 3. De browsertab heette "¡Vamos Stefan!"

Elke bookmark en elke gedeelde link van elke vreemde. Het manifest was al netjes ("¡Vamos! ·
Spaans oefenen"); die twee waren uit elkaar gelopen.

## 4. Er stond andermans naam in de leerstof

"Mi madre se llama Ilona." Voor een vreemde een willekeurige naam, dus geen leerprobleem, maar wel
de naam van een echt persoon in een publiek product. Wordt María.

## Drie kleinere dingen die dezelfde doorloop opleverde

- De mengrij toonde "0 werkwoorden" in het lesmenu: hij telde zichzelf als patroonrij.
- "In een echte zin" kon op dag 1 een ronde van één zin geven. Nu een ondergrens.
- De Oefenen-rij zei "de route door de verleden tijd" terwijl er twee routes zijn.
"""

import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.131"

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


# ------------- 1. "verder waar je was" alleen als er iets is om verder te gaan

rep(
    '''function lesFlowHervatKan(){
  var n = S.lesFlowNu;
  return !!(n && n.d === today() && n.stap);
}''',
    '''/* v23.131: hier stond alleen "er is een opgeslagen stap van vandaag". Die staat er al zodra de
   flow begint, dus las een gloednieuwe gebruiker als allereerste zin op zijn scherm: "We gaan
   verder waar we gebleven waren. Je stopte bij stap 1 van 4." Er was niets om verder te gaan, en
   de Woordjes-tab zei op datzelfde moment w\\u00e9l het goede ("Start je les").

   Verdergaan veronderstelt dat je ergens was. Dat is waar zodra je voorbij de eerste stap bent, of
   zodra je vandaag iets hebt beantwoord. Geen nieuwe vlag: newToday() telt de nieuwe woorden van
   vandaag en stond er al. */
function lesFlowHervatKan(){
  var n = S.lesFlowNu;
  if(!n || n.d !== today() || !n.stap) return false;
  return lesFlowStapNum(n) > 1 || newToday() > 0;
}''',
)

# ------------- 2. de patronen erven de poort van de Conjugador-ladder

rep(
    '''function conjPatroonPool(id){
  var pat = conjPatroonVan(id);
  if(!pat) return [];
  return VERBOS.filter(function(v){ return conjInPatroon(v, pat); });
}''',
    '''function conjPatroonPool(id){
  var pat = conjPatroonVan(id);
  if(!pat) return [];
  return VERBOS.filter(function(v){ return conjInPatroon(v, pat); });
}
/* v23.131: de patronen gaan open wanneer de Conjugador de onregelmatige werkwoorden opent, en geen
   moment eerder.

   Doorlopen als vreemde: wie hola, gracias en adi\\u00f3s kende, kreeg op de Grammatica-tab "Nu: De
   yo-vorm op -go" te lezen, met alle zes de patroonlessen open. Dat is onzin voor iemand die drie
   woorden kent, en het is precies het scherm dat het verschil moet maken.

   De poort bestond al: CONJ_FASES zet ar, er, ir, seis en pas dan onreg. Een patroonles erft die,
   zodat er geen tweede niveau ontstaat dat iemand moet bijhouden. Wie al verder was toen dit erbij
   kwam merkt er niets van, want die staat allang voorbij fase onreg. */
var CONJ_PATROON_FASE = "onreg";
function conjPatroonOpen(){
  var nodig = conjFaseIdx(CONJ_PATROON_FASE);
  if(nodig < 0) return true;
  return conjOpenMax() >= nodig;
}''',
)

rep(
    '''function lesRijIds(){
  var uit = conjOpenTijden().slice();
  CONJ_PATRONEN.forEach(function(p){ if(conjPatroonPool(p.id).length) uit.push(p.id); });
  /* de mengrijen achteraan: door elkaar is de laatste stap, niet de eerste */
  LES_MIXRIJEN.forEach(function(m){ if(lesRij(m.id)) uit.push(m.id); });
  return uit;
}''',
    '''function lesRijIds(){
  var uit = conjOpenTijden().slice();
  if(!conjPatroonOpen()) return uit;   // v23.131: zie conjPatroonOpen()
  CONJ_PATRONEN.forEach(function(p){ if(conjPatroonPool(p.id).length) uit.push(p.id); });
  /* de mengrijen achteraan: door elkaar is de laatste stap, niet de eerste */
  LES_MIXRIJEN.forEach(function(m){ if(lesRij(m.id)) uit.push(m.id); });
  return uit;
}''',
)

# ------------- 2b. een route is pas "de route van nu" als hij te lopen is

rep(
    '''function gramPadNu(){
  var L = gramPadenGeordend(), i;
  for(i = 0; i < L.length; i++) if(gramPadBegonnen(L[i]) && !gramPadKlaar(L[i])) return L[i];
  for(i = 0; i < L.length; i++) if(!gramPadKlaar(L[i])) return L[i];
  return L[0] || null;
}''',
    '''/* v23.131: een route waarvan de lessen nog op slot staan is geen route maar een etalage. Afgeleid
   uit lesRijIds(), dus er komt geen tweede lijst bij: kan de les deze rij vandaag onderwijzen, dan
   kan de route hem aanbieden. Een route zonder lesstappen (die bestaat nu niet) telt als open. */
function gramPadOpen(p){
  var rijen = lesRijIds(), open = true;
  (p.stappen || []).forEach(function(s){
    if(s.soort === "les" && s.arg && rijen.indexOf(s.arg) === -1) open = false;
  });
  return open;
}
/* Waarom een route nog niet open is, in \\u00e9\\u00e9n regel op het scherm. */
function gramPadWachtZin(p){
  var f = CONJ_FASES[conjFaseIdx(CONJ_PATROON_FASE)];
  var wat = f ? ct(f.nl, f.en) : ct("de volgende fase", "the next phase");
  return ct("Gaat open zodra je in de Conjugador bij \\u201e" + wat + "\\u201d bent.",
            "Opens once you reach \\u201c" + wat + "\\u201d in the Conjugador.");
}
function gramPadNu(){
  var L = gramPadenGeordend().filter(gramPadOpen), i;
  for(i = 0; i < L.length; i++) if(gramPadBegonnen(L[i]) && !gramPadKlaar(L[i])) return L[i];
  for(i = 0; i < L.length; i++) if(!gramPadKlaar(L[i])) return L[i];
  return L[0] || null;
}''',
)

rep(
    '''function gramRouteHtml(){
  var p = gramPadNu();
  if(!p) return "";''',
    '''function gramRouteHtml(){
  var p = gramPadNu();
  /* v23.131: geen enkele route open (dat is de stand op dag 1). Weglaten zou verstoppen zijn, dus
     staat er wat er is en wat het opent. */
  if(!p) return "<div class='card' id='gramRoute'><h2>" + ct("De routes", "The routes") + " \\ud83e\\udded</h2>" +
    "<p class='muted'>" +
    ct("Er is nog geen route voor je open. Ze gaan open naarmate je in de Conjugador verder komt; tot die tijd is dit de plek om regels op te zoeken en te oefenen.",
       "No route is open for you yet. They open as you get further in the Conjugador; until then this is the place to look up rules and practise.") +
    "</p>" + gramAndereRoutesHtml(null) + "</div>";''',
)

rep(
    '''function gramAndereRoutesHtml(nu){
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
    '''function gramAndereRoutesHtml(nu){
  var rest = gramPadenGeordend().filter(function(p){ return p.id !== (nu || {}).id; });
  if(!rest.length) return "";
  var kop = nu
    ? "<div class='card' id='gramRoutes'><h2>" + ct("De andere routes", "The other routes") + "</h2>" +
      "<p class='muted' style='font-size:.88rem'>" +
      ct("In de volgorde waarin de Conjugador ze openzet. Je mag vooruit kijken; de route hierboven is waar je nu staat.",
         "In the order the Conjugador unlocks them. You may look ahead; the route above is where you stand now.") + "</p>"
    /* zonder route van nu staat dit blok binnen de routekaart zelf, dus geen tweede kop */
    : "<div id='gramRoutes' style='margin-top:8px'>";
  return kop +
    rest.map(function(p){
      var t = gramRouteTelling(p);
      var open = gramPadOpen(p);
      /* v23.131: een route op slot is aan te wijzen maar niet aan te klikken, en zegt waarom */
      return "<div class='lesson'" + (open ? " data-padga='" + p.id + "' style='cursor:pointer'" : " style='opacity:.5'") + ">" +
        "<div class='lnum'>" + (!open ? "\\ud83d\\udd12" : (gramPadKlaar(p) ? "\\u2713" : t.af + "/" + t.telt)) + "</div>" +
        "<div class='lbody'><b>" + ct(p.nl, p.en) + "</b><span>" +
          (open ? gramRouteRegel(p) : gramPadWachtZin(p)) + "</span></div>" +
        "<div class='lstatus'>" + (open ? "\\u25b6" : "\\u00b7") + "</div></div>";
    }).join("") + "</div>";
}''',
)

# ------------- 3. de titel

rep(
    '''<title>¡Vamos Stefan! · Spaans oefenen</title>''',
    '''<!-- v23.131: hier stond "¡Vamos Stefan!". Dat is de tekst in het tabblad, in de bookmark en in
     elke gedeelde link, ook bij iemand die Stefan niet is. Het manifest (manifestZetten) zei allang
     het goede; die twee waren uit elkaar gelopen. -->
<title>¡Vamos! · Spaans oefenen</title>''',
)

# ------------- 4. andermans naam uit de leerstof

rep(
    '''b18:{v:"Mi madre se llama Ilona.|Mijn moeder heet Ilona.",r:"zn (v) · mv: las madres"}''',
    '''b18:{v:"Mi madre se llama Mar\\u00eda.|Mijn moeder heet Mar\\u00eda.",r:"zn (v) · mv: las madres"}''',
)

rep(
    '''b18:"My mother is called Ilona."''',
    '''b18:"My mother is called Mar\\u00eda."''',
)

# ------------- 5. de mengrij telde zichzelf als patroonrij

rep(
    '''            ct(r.nl, r.en) + (r.tijd ? "" : " \\u00b7 " + conjPatroonPool(t).length + " " + ct("werkwoorden", "verbs")) +''',
    '''            /* v23.131: conjPatroonPool() geeft nul voor een mengrij, want die is geen patroon.
               Het aantal komt nu uit de rij zelf, dus elke soort rij telt zijn eigen werkwoorden. */
            ct(r.nl, r.en) + (r.tijd ? "" : " \\u00b7 " + (r.pool({inf:""}) || []).length + " " + ct("werkwoorden", "verbs")) +''',
)

# ------------- 6. geen ronde van één zin

rep(
    '''  if(!zinSpel) zinStart(null, null);
  if(!zinSpel.rij.length){''',
    '''  if(!zinSpel) zinStart(null, null);
  /* v23.131: op dag 1 staat er \\u00e9\\u00e9n zin vrijgespeeld, en een ronde van \\u00e9\\u00e9n vraag is geen oefening.
     Onder de helft van een ronde zeggen we wat er is in plaats van een ronde te doen alsof. */
  if(zinSpel.rij.length < Math.ceil(ZIN_LEN / 2)){''',
)

rep(
    '''    el.innerHTML = kop + "<p class='muted'>" +
      ct("Er zijn nog geen zinnen vrijgespeeld waarin precies \\u00e9\\u00e9n werkwoordsvorm staat. Doe eerst wat lessen; dan komen ze vanzelf.",
         "No unlocked sentences yet with exactly one verb form in them. Do a few lessons first and they will come.") + "</p>" +''',
    '''    el.innerHTML = kop + "<p class='muted'>" +
      ct("Hier zijn nog te weinig zinnen voor. Deze oefening put uit de zinnen die je hebt vrijgespeeld, en daar staan er nu " + zinSpel.rij.length + " van klaar met precies \\u00e9\\u00e9n werkwoordsvorm erin. Doe eerst wat lessen; dan komen ze vanzelf.",
         "There are too few sentences for this yet. This exercise draws on the sentences you have unlocked, and " + zinSpel.rij.length + " of those currently have exactly one verb form in them. Do a few lessons first and they will come.") + "</p>" +''',
)

# ------------- 6b. "de oefeningen uit de route hierboven" terwijl er geen route boven staat

rep(
    '''  return "<div class='card' id='gramOefen'><h2>" + ct("Los oefenen", "Practise separately") + "</h2>" +
    "<p class='muted'>" +
    ct("Dit zijn de oefeningen uit de route hierboven. De route wijst de volgorde aan; hier kies je zelf.",
       "These are the exercises from the route above. The route sets the order; here you choose yourself.") +
    "</p>" + r.nu + r.straks + "</div>";''',
    '''  /* v23.131: stond er "de oefeningen uit de route hierboven" terwijl er op dag 1 geen route
     boven staat. De zin hoort te kloppen in allebei de standen. */
  var heeftRoute = !!gramPadNu();
  return "<div class='card' id='gramOefen'><h2>" + ct("Los oefenen", "Practise separately") + "</h2>" +
    "<p class='muted'>" +
    (heeftRoute
      ? ct("Dit zijn de oefeningen uit de route hierboven. De route wijst de volgorde aan; hier kies je zelf.",
           "These are the exercises from the route above. The route sets the order; here you choose yourself.")
      : ct("De oefeningen waar de routes straks uit putten. Je mag ze nu al los doen; sommige gaan pas ergens over als je verder bent.",
           "The exercises the routes will draw on. You may do them separately already; some only start to mean something once you are further along.")) +
    "</p>" + r.nu + r.straks + "</div>";''',
)

# ------------- 7. de Oefenen-rij noemde één route

rep(
    '''     s:ct("De route door de verleden tijd, de losse oefeningen en alle regels om op te zoeken.","The route through the past tense, the separate exercises, and all the rules to look up.")}''',
    '''     s:ct("Je route door de werkwoorden, de losse oefeningen en alle regels om op te zoeken.","Your route through the verbs, the separate exercises, and all the rules to look up.")}''',
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
