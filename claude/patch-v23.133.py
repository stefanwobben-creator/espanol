#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.133: wat je opzoekt wordt van jou.

Ronde 2, eerste helft. De eerste ronde die je ziet.

## Wat er stuk was, en het is erger dan "een knop ontbreekt"

Sinds v23.21 kun je tijdens het lezen elk woord aantikken en krijg je de betekenis. Dat tikken werd
geteld ook: leesNoteer() schrijft het weg in S.leesZoek, met de toelichting "nog niet getoond: eerst
een paar hoofdstukken meten, dan pas iets beweren".

Gezocht waar S.leesZoek gelezen wordt: nergens. Twee plekken in het hele bestand, allebei de
schrijfkant. Elk woord dat Stefan ooit heeft opgezocht is geteld en vervolgens op de grond gevallen.
Dat is het sterkste signaal dat de app heeft over wat hij níet weet, en het ging naar niets.

Ondertussen is de leescyclus half: je leest, je struikelt over een woord, je tikt, je krijgt de
betekenis, en dan is het weg. Morgen struikel je er weer over. Lezen is de sterkste motor die er is
voor woordenschat (Nation), maar alleen als wat je opzoekt ergens terechtkomt.

## Wat er nu staat

Tik een woord, en er staat een knop onder de betekenis: **In mijn woorden**. Eén tik en het woord
ligt morgen in je woordjes, op doos 0.

Drie soorten woorden, drie routes, allemaal achter dezelfde knop:

  * Staat het al in een les (leesBetekenis geeft een id terug), dan krijgt dat woord gewoon een
    SRS-rij. Het springt daarmee voor de dagportie langs de poort en de nieuw-per-dag-rem heen, en
    dat hoort: je hebt er zelf om gevraagd.
  * Staat het alleen in de frequentielijst of in LEES_EXTRA, dan wordt het een eigen woord in
    S.mijn. Dat is nieuw: tot nu toe kon de app 3.682 woorden wél uitleggen en niet leren.
  * Is het een vervoegde vorm, dan gaat het hele werkwoord erin, niet de vorm. "dice" levert
    "decir" op.

S.mijn is data, geen tweede lijst. Bij het opstarten wordt WORDS ermee aangevuld, en daarna weet
geen enkele andere plek in de app dat deze woorden anders zijn ontstaan: dagportie, doosjes,
kaartjes, de Laatste stap, de voortgangsbalk. Precies de regel die hier geldt: staat een feit in de
data, dan schrijft geen codeplek dat feit opnieuw.

## En de teller die niemand las

S.leesZoek wordt nu wel gelezen. Onder een hoofdstuk staat wat je hier hebt opgezocht en nog niet in
je woorden hebt staan, met een knop om ze in één keer toe te voegen. Dat is de meting van drie weken
lezen, eindelijk aan het werk.

## De dekking, eerlijk

Onder de tekst staat van hoeveel woorden op deze bladzijde een kaartje in je stapel ligt. Gemeten
over alle 29 hoofdstukken tegen de huidige lijst: 42,7 procent. Nation's grens voor lezen zonder
woordenboek ligt op 95. Dat getal is dus geen compliment, maar het is wel het getal, en het beweegt
met elke tik omhoog.

Bewust niet "hoeveel procent je kent": dat weet de app niet. Wel van hoeveel woorden hier een
kaartje ligt.

Bewaakt door test/suites/pw-mijnwoorden.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.133"

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


# ------------- 1. de eigen woorden: opslag, pool, toevoegen

rep(
    '''function leesNoteer(plat){
  if(!plat) return;
  S.leesZoek = S.leesZoek || {};
  S.leesZoek[plat] = (S.leesZoek[plat] || 0) + 1;
  persist();
}''',
    '''function leesNoteer(plat){
  if(!plat) return;
  S.leesZoek = S.leesZoek || {};
  S.leesZoek[plat] = (S.leesZoek[plat] || 0) + 1;
  persist();
}

/* ================= WAT JE OPZOEKT WORDT VAN JOU (v23.133) =================

   Sinds v23.21 kun je elk woord in een hoofdstuk aantikken en krijg je de betekenis. Daarna was het
   weg: morgen struikel je er weer over. Lezen is de sterkste motor die er is voor woordenschat,
   maar alleen als wat je opzoekt ergens terechtkomt.

   S.mijn is de opslag: platte vorm -> {es, nl, d}. Geen tweede woordenlijst en geen tweede SRS. Bij
   het opstarten wordt WORDS met deze rijen aangevuld, en daarna weet geen enkele andere plek in de
   app dat ze anders zijn ontstaan. Dagportie, doosjes, kaartjes, de Laatste stap en de
   voortgangsbalk werken er ongewijzigd op. Staat een feit in de data, dan schrijft geen codeplek
   dat feit opnieuw.

   Waarom een woord dat je toevoegt meteen een SRS-rij krijgt (doos 0, vandaag): daarmee is het een
   herhaling en geen nieuw woord, en dus komt het langs de poort en langs de nieuw-per-dag-rem. Dat
   hoort: je hebt er zelf om gevraagd, terwijl die twee remmen er zijn voor woorden die de app jou
   aanbiedt. De dagportie zelf heeft een bovengrens (portieMax), dus twintig woorden aantikken geeft
   geen les van twintig kaartjes extra; ze staan in de rij. */
function mijnWoordId(plat){ return "mijn-" + plat; }
function mijnWoordLijst(){
  var uit = [], k, m = (typeof S !== "undefined" && S && S.mijn) || {};
  for(k in m){
    if(!m[k] || !m[k].es) continue;
    uit.push({id:mijnWoordId(k), es:m[k].es, nl:m[k].nl, en:m[k].en || m[k].nl, tag:"mijn"});
  }
  return uit;
}
/* Aanvullen, niet vervangen: boot() bouwt WORDS uit de sporen en dat gebeurt voordat S bestaat. */
function mijnWoordenInPool(){
  if(typeof WORDS === "undefined") return 0;
  var lijst = mijnWoordLijst(), heb = {}, i, n = 0;
  for(i = 0; i < WORDS.length; i++) heb[WORDS[i].id] = 1;
  for(i = 0; i < lijst.length; i++){
    if(heb[lijst[i].id]) continue;
    WORDS.push(lijst[i]);
    n++;
  }
  return n;
}
/* Van een tooltip-uitkomst naar iets wat je kunt leren. Een woord uit een les heeft al een id en
   hoeft geen eigen rij; een woord uit de frequentielijst krijgt er een. Een vervoegde vorm levert
   het hele werkwoord op en niet die ene vorm: leesBetekenis zet b.es dan al op de infinitief. */
function mijnDoel(b){
  if(!b || !b.es || !b.nl) return null;
  if(b.id) return {id:b.id, eigen:false, es:b.es, nl:b.nl};
  var plat = leesPlat(b.es);
  if(!plat) return null;
  return {id:mijnWoordId(plat), eigen:true, plat:plat, es:b.es, nl:b.nl};
}
function mijnHeeft(d){ return !!(d && S.srs && S.srs[d.id]); }
/* Zet het woord in je stapel. Geeft terug of er iets veranderd is, zodat de knop kan zeggen wat er
   gebeurd is in plaats van elke keer hetzelfde. */
function mijnBij(d){
  if(!d || !d.id) return false;
  if(mijnHeeft(d)) return false;
  if(d.eigen){
    S.mijn = S.mijn || {};
    S.mijn[d.plat] = {es:d.es, nl:d.nl, d:today()};
    mijnWoordenInPool();
  }
  S.srs = S.srs || {};
  S.srs[d.id] = {box:0, due:today(), n:0, zelf:1};   // zelf: je hebt er zelf om gevraagd
  persist();
  updateBadge();
  return true;
}
/* Het hoofdstuk één keer ontleden in plaats van drie keer.

   Zowel de dekking als "hier zocht je eerder op" wil van elk woord op de bladzijde weten waar het
   heen zou gaan, en leesBetekenis() is niet goedkoop: hij loopt door vier lijsten en doet bij een
   misser ook nog een vormanalyse. Eerst stond dat er als twee losse lussen over alle tokens.
   Gemeten op de 29 hoofdstukken: mediaan 226 ms en piek 455 ms om een hoofdstuk te openen, en op
   een telefoon is dat drie keer zoveel. Anderhalve seconde wachten voordat je kunt lezen.

   Nu: één pas over de UNIEKE vormen (een hoofdstuk van 281 woorden heeft er ongeveer 150), met het
   resultaat bewaard tot je van hoofdstuk wisselt of er een woord bij komt. Wat er per vorm NIET in
   staat is of het al in je stapel ligt: dat verandert bij elke tik, en dat hoort dus niet in een
   cache maar in de vraag zelf. */
var _leesVormen = null;
function leesVormen(h){
  var id = (h && h.id) || "";
  if(_leesVormen && _leesVormen.id === id && _leesVormen.pool === WORDS.length) return _leesVormen;
  var toks = String((h && h.tekst) || "").match(/[A-Za-z\\u00c0-\\u024f]+/g) || [];
  var uniek = {}, i, plat, b;
  for(i = 0; i < toks.length; i++){
    plat = leesPlat(toks[i]);
    if(!plat) continue;
    if(uniek[plat]){ uniek[plat].n++; continue; }
    try { b = leesBetekenis(toks[i]); } catch(e){ b = null; }
    uniek[plat] = {n:1, woord:toks[i], doel:mijnDoel(b)};
  }
  _leesVormen = {id:id, pool:WORDS.length, n:toks.length, uniek:uniek};
  return _leesVormen;
}
/* Wat je in dit hoofdstuk hebt opgezocht en nog niet in je woorden hebt staan. Dit is de teller uit
   v23.21 die drie weken lang wel werd geschreven en nergens gelezen. */
function leesOpgezocht(h){
  var v = leesVormen(h), zoek = S.leesZoek || {}, uit = [], plat, x;
  for(plat in v.uniek){
    if(!zoek[plat]) continue;
    x = v.uniek[plat];
    if(!x.doel || mijnHeeft(x.doel)) continue;
    uit.push({woord:x.woord, doel:x.doel, keer:zoek[plat]});
  }
  uit.sort(function(a, c){ return c.keer - a.keer; });
  return uit;
}
/* Van hoeveel woorden op deze bladzijde ligt er een kaartje in je stapel? Met opzet niet "hoeveel
   procent ken je": dat weet de app niet, en een getal dat meer beweert dan het meet is precies wat
   dit scherm drie keer heeft laten struikelen. Namen tellen als onbekend; dat drukt het getal met
   een paar punten en dat is de eerlijke kant om op te missen. */
function leesDekking(h){
  var v = leesVormen(h), n = 0, plat, x, st;
  for(plat in v.uniek){
    x = v.uniek[plat];
    if(!x.doel) continue;
    st = S.srs && S.srs[x.doel.id];
    if(st && (st.box || 0) >= 1) n += x.n;      // maal hoe vaak de vorm op de bladzijde staat
  }
  return {n:v.n, bekend:n, pct:v.n ? Math.round(100 * n / v.n) : 0};
}''',
)

# ------------- 2. de eigen woorden staan in de pool zodra S geladen is

rep(
    '''  S = normaliseerState(store.load()); // v19.56: dezelfde normalisatie als bij een pull van de server''',
    '''  S = normaliseerState(store.load()); // v19.56: dezelfde normalisatie als bij een pull van de server
  mijnWoordenInPool();   // v23.133: WORDS is hierboven gebouwd zonder S, dus je eigen woorden pas hier''',
)

# ------------- 3. en ze mogen ook echt langskomen

rep(
    '''  if(typeof C_WORDS !== "undefined") out = out.concat(C_WORDS.map(function(w){ return w.id; }));
  return out;
}''',
    '''  if(typeof C_WORDS !== "undefined") out = out.concat(C_WORDS.map(function(w){ return w.id; }));
  /* v23.133: je eigen woorden hangen per definitie aan geen enkele les. Ze krijgen bij het
     toevoegen al een SRS-rij en komen daarmee als herhaling langs, maar zonder deze regel vallen ze
     binnen een les buiten de toegestane verzameling en dan zie je ze daar nooit. */
  out = out.concat(mijnWoordLijst().map(function(w){ return w.id; }));
  return out;
}''',
)

# ------------- 4. de knop onder de betekenis

rep(
    '''function leesToon(woord, span){
  var el = document.getElementById("leesUitleg");
  if(!el) return;''',
    '''/* Het woord dat nu open staat, plus waar het heen zou gaan. Staat hier en niet in de DOM, want uit
   een data-attribuut teruglezen zou betekenen dat de opmaak bepaalt wat je leert. */
var leesNu = null;
function leesMijnKnopHtml(d){
  if(!d) return "";
  if(mijnHeeft(d)){
    return "<p class='muted' style='font-size:.78rem; margin:6px 0 0'>\\u2713 "+
      ct("staat in je woorden","in your words")+"</p>";
  }
  return "<button class='mini' id='btnLeesMijn' style='margin:6px 0 0'>+ "+
    ct("In mijn woorden","Add to my words")+"</button>";
}
function leesMijnKlik(){
  var d = leesNu && leesNu.doel;
  if(!d) return;
  var nieuw = mijnBij(d);
  var el = document.getElementById("leesUitleg");
  var knop = document.getElementById("btnLeesMijn");
  if(knop && knop.parentNode){
    knop.outerHTML = "<p class='muted' style='font-size:.78rem; margin:6px 0 0'>\\u2713 "+
      (nieuw ? ct("staat nu in je woorden, morgen komt hij langs","added, it comes back tomorrow")
             : ct("staat in je woorden","in your words"))+"</p>";
  }
  if(el && el.getAttribute("data-hfd")) leesDekkingBij();
  addXP(1);
}
/* De regel onder de tekst opnieuw laten rekenen zonder het hele hoofdstuk te hertekenen: dat zou de
   tooltip sluiten en de leespositie kwijtraken, en dan is toevoegen duurder dan het waard is. */
function leesDekkingBij(){
  var el = document.getElementById("leesDek");
  if(!el || !bState || !bState.h) return;
  el.innerHTML = leesDekkingHtml(bState.h);
}
function leesDekkingHtml(h){
  var d = leesDekking(h);
  return ct("Van de "+d.n+" woorden hier oefen je er "+d.bekend+" ("+d.pct+"%).",
            "Of the "+d.n+" words here you are practising "+d.bekend+" ("+d.pct+"%).");
}

function leesToon(woord, span){
  var el = document.getElementById("leesUitleg");
  if(!el) return;''',
)

# de tooltip zelf: bij een woord zonder betekenis geen knop, bij een woord met betekenis wel

rep(
    '''    el.innerHTML = kop + "<p><span class='es'>"+woord+"</span></p>"+
      "<p class='muted' style='font-size:.85rem'>"+
        (naam ? ct("Een naam, van een persoon of een plaats.","A name, of a person or a place.")
              : ct("Staat niet in het woordenboek. Genoteerd.","Not in the dictionary. Noted."))+"</p>";
    if(span) leesTooltipPlaats(el, span);
    return;''',
    '''    leesNu = {woord:woord, doel:null};
    el.innerHTML = kop + "<p><span class='es'>"+woord+"</span></p>"+
      "<p class='muted' style='font-size:.85rem'>"+
        (naam ? ct("Een naam, van een persoon of een plaats.","A name, of a person or a place.")
              : ct("Staat niet in het woordenboek. Genoteerd.","Not in the dictionary. Noted."))+"</p>";
    if(span) leesTooltipPlaats(el, span);
    return;''',
)

rep(
    '''  el.innerHTML = kop + "<p><span class='es'>"+woord+"</span>"+
      (stripAcc(String(b.es).toLowerCase()) !== stripAcc(String(woord).toLowerCase())
        ? " <span class='muted'>"+brug+" <span class='es'>"+b.es+"</span></span>" : "")+
      extra+"</p>"+
    "<p>"+b.nl+"</p>";
  if(span) leesTooltipPlaats(el, span);''',
    '''  /* v23.133: en hier houdt het niet meer op. Zonder deze knop krijg je de betekenis, ben je hem
     morgen kwijt en struikel je over hetzelfde woord. Een woord uit een uitdrukking krijgt hem niet:
     dan zou je "dejan" als los kaartje leren terwijl de uitleg juist zegt dat dat de verkeerde
     eenheid is. */
  leesNu = {woord:woord, doel:(b.uitdrukking ? null : mijnDoel(b))};
  el.innerHTML = kop + "<p><span class='es'>"+woord+"</span>"+
      (stripAcc(String(b.es).toLowerCase()) !== stripAcc(String(woord).toLowerCase())
        ? " <span class='muted'>"+brug+" <span class='es'>"+b.es+"</span></span>" : "")+
      extra+"</p>"+
    "<p>"+b.nl+"</p>"+
    leesMijnKnopHtml(leesNu.doel);
  if(span) leesTooltipPlaats(el, span);''',
)

# ------------- 5. het hoofdstukscherm: de knop moet werken, en de dekking eronder

rep(
    '''  el.onclick = function(ev){
    var t = ev.target;
    // ergens anders tikken sluit de tooltip: dat is de gebaarloze manier om hem weg te krijgen
    if(!t || !t.classList || !t.classList.contains("lw")){ leesVerberg(); return; }''',
    '''  el.onclick = function(ev){
    var t = ev.target;
    // v23.133: de knop in de tooltip staat binnen deze kaart, dus zonder deze regel zou hij de
    // tooltip sluiten in plaats van het woord toe te voegen.
    if(t && t.id === "btnLeesMijn"){ leesMijnKlik(); return; }
    if(t && t.id === "btnLeesAlles"){ leesAllesKlik(); return; }
    // ergens anders tikken sluit de tooltip: dat is de gebaarloze manier om hem weg te krijgen
    if(!t || !t.classList || !t.classList.contains("lw")){ leesVerberg(); return; }''',
)

rep(
    '''    paras+
    "<p class='muted' style='font-size:.82rem; margin:10px 0 0'>"+
      ct("Tik op een woord dat je niet kent.","Tap a word you do not know.")+"</p>"+
    "<div class='leesUit weg' id='leesUitleg'></div>"+''',
    '''    paras+
    "<p class='muted' style='font-size:.82rem; margin:10px 0 0'>"+
      ct("Tik op een woord dat je niet kent.","Tap a word you do not know.")+"</p>"+
    /* v23.133: van hoeveel woorden hier ligt er een kaartje in je stapel. Het getal is laag en dat
       hoort: gemeten over alle 29 hoofdstukken staat de lijst op 42,7 procent, en de grens waarbij
       lezen zonder woordenboek gaat lopen ligt rond de 95 (Nation). Het beweegt met elke tik. */
    "<p class='muted' style='font-size:.82rem; margin:2px 0 0' id='leesDek'>"+leesDekkingHtml(h)+"</p>"+
    leesOpgezochtHtml(h)+
    "<div class='leesUit weg' id='leesUitleg'></div>"+''',
)

# ------------- 6. de teller die niemand las, aan het werk

rep(
    '''function renderBoekLectura(){''',
    '''/* v23.133: wat je in dit hoofdstuk eerder hebt opgezocht en nog steeds niet in je woorden hebt
   staan. S.leesZoek werd sinds v23.21 wel geschreven en nergens gelezen; dit is die meting, aan het
   werk. Hoogstens acht, want een lijst van veertig is geen aanbod maar een verwijt. */
var LEES_OPZOEK_MAX = 8;
function leesOpgezochtHtml(h){
  var lijst = leesOpgezocht(h);
  if(!lijst.length) return "";
  var toon = lijst.slice(0, LEES_OPZOEK_MAX);
  return "<p class='muted' style='font-size:.82rem; margin:8px 0 0'>"+
    ct("Hier zocht je eerder op: ","You looked these up here before: ")+
    toon.map(function(x){ return "<span class='es'>"+x.woord+"</span>"; }).join(", ")+
    (lijst.length > toon.length ? ct(" en nog "+(lijst.length - toon.length),
                                     " and "+(lijst.length - toon.length)+" more") : "")+
    ". <button class='mini' id='btnLeesAlles' style='margin-top:4px'>+ "+
    ct("Allemaal in mijn woorden","Add them all to my words")+"</button></p>";
}
function leesAllesKlik(){
  var h = bState && bState.h;
  if(!h) return;
  var lijst = leesOpgezocht(h), n = 0;
  lijst.forEach(function(x){ if(mijnBij(x.doel)) n++; });
  toast(n === 1 ? ct("1 woord toegevoegd","1 word added")
                : ct(n+" woorden toegevoegd", n+" words added"));
  renderBoekLectura();
}

function renderBoekLectura(){''',
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
