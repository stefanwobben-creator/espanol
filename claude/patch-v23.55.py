#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.55: de vreemde begint na één seconde, niet na vijf.

Stefan, gevraagd wat erger is: de vreemde die op vrijdag vijf seconden wacht en misschien wegklikt,
of Ilona die op dag 12 wacht omdat er die ochtend gedeployd is. Antwoord: **de vreemde die
wegklikt.** Dat sluit de service worker uit als eerste stap (die doet niets voor een eerste bezoek)
en zet alles op het eerste scherm.

## Waar de vijf seconden zitten

Gemeten met gzip en de cacheheaders van GitHub Pages, traag 4G (1,6 Mbit, 300 ms rtt, cpu 4x):

    eerste byte             169 ms
    statische html binnen   ~950 ms     <- hier staat het laadscherm van v23.54
    script binnen          4295 ms     <- 806 KB over de lijn
    app bruikbaar          4911 ms

Het laadscherm van v23.54 maakte dat gat eerlijk. Deze versie maakt het leeg.

## Het idee

De vreemde hoeft niet op de app te wachten, want het eerste dat hij ziet is geen app. Het zijn drie
woordjes: *hola*, *gracias*, *adiós*, elk met twee knoppen. Dat is 2,3 KB aan data en een handvol
regels code, en dat kan mee met de statische HTML.

Dus staat er nu een tweede, klein `<script>`-blok direct onder de HTML, vóór het grote. De browser
voert dat uit zodra hij het geparseerd heeft, en dat is rond de seconde. De bezoeker beantwoordt zijn
eerste vraag terwijl de resterende 800 KB nog binnenkomt.

Drie vragen met 850 ms feedback ertussen kosten minstens vier à vijf seconden aan aandacht. Tegen de
tijd dat hij de derde heeft beantwoord is het grote script er, en neemt de helling het over.

## Geen tweede kopie van de proef

Wat verhuist is verhuisd en niet gekopieerd: `PROEF_WOORDEN`, `PROEF_TXT`, `UI_LANGS`,
`taalWeHebben()`, `browserTaal()`, `proefTaal()`, `proefStand`, `proefMem`, `proefData()`,
`proefBewaar()` en `proefWis()` staan nu in het vroege blok. Het zijn globals, dus het grote script
ziet ze onveranderd. Er is geen regel die twee keer bestaat.

Wat er wél bij komt is `vroegVraag()`, ongeveer veertig regels, en die dupliceert `renderProef()`
niet maar schrijft in het formaat waar `renderProef()` al uit hervat. Dat formaat bestaat sinds
v23.44 (toen de helling zijn stand ging bewaren zodat een per ongeluk ververste pagina niet alles
kwijt was):

    proefBewaar({bezig:true, xp:.., res:.., stand:{i:.., xp:.., res:..}})

`renderProef()` doet bij het opstarten `proefStand = (bew && bew.bezig && bew.stand) ? bew.stand :
{i:0,..}`. De overdracht is dus geen nieuwe koppeling maar een bestaande, en dat is precies waarom
dit veilig kan twee dagen voor een lancering.

## Wanneer het vroege blok zich koest houdt

Alles in een try/catch, en bij het minste of geringste doet het niets en gebeurt er wat er hiervoor
gebeurde. Het houdt zich koest bij:

  - een querystring in de URL (uitnodigingslink, ?beheer=, alles wat het grote script zelf afhandelt)
  - een bestaand profiel op dit apparaat (`espanol-profiles-v1` met een gevulde lijst)
  - een proef die al klaar of overgeslagen is
  - geen localStorage, geen `#profCard`, of welke fout dan ook

Dat zijn dezelfde voorwaarden als `normaalBegin()` in het grote script, en die blijft ook gewoon
staan: het vroege blok vervangt hem niet, het loopt erop vooruit.

## Twee dingen die anders zijn dan bij het grote script

*Geen Chispa.* De mascotte komt uit `petSVG()`, en die hangt aan `S`, aan `petLevel()` en aan de hele
tekenboom. Die verhuist niet mee. In plaats daarvan staat er een leeg vak van precies dezelfde hoogte,
zodat het ei erin verschijnt in plaats van dat de knoppen naar beneden springen.

*Geen toast en geen confetti.* Die zitten ook in het grote script. De uitslag staat daarom in het
kaartje zelf, onder de knoppen, en dat is op een telefoon zelfs beter zichtbaar dan een toast
onderaan.

## En het laadscherm

Zodra het vroege blok een vraag heeft getekend haalt het `window.__laadWeg()` over: er staat immers
iets echts. Voor wie al een profiel heeft blijft het gordijn tot `boot()` klaar is, want voor die
bezoeker is er niets om eerder te laten zien.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.55"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function vroegVraag" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

# ---- de twee stukken die verhuizen, per begin- en eindanker ----
TAAL_START = 'var UI_LANGS = {nl:{naam:"Nederlands"'
TAAL_EIND = '''function browserTaal(){
  try { return taalWeHebben((typeof navigator !== "undefined" && navigator.language) || "nl"); }
  catch(e){ return "en"; }
}
'''
PROEF_START = 'var PROEF_WOORDEN = ['
PROEF_EIND = 'function proefWis(){ proefMem = null; try{ localStorage.removeItem("espanol-proef-v1"); }catch(e){} }\n'

# Het vroege blok moet ná #profCard in het document staan, anders vindt het die niet: de browser
# voert een inline script uit op het moment dat hij het tegenkomt, en alles daaronder bestaat dan
# nog niet. Eerste poging stond boven <div class="wrap"> en deed daarom niets (gemeten: de eerste
# knop verscheen pas op 7266 ms, dus via het grote script). Vlak na de profielsectie staat het nog
# steeds ruim binnen de statische HTML.
A_LAAD = '''  <div id="storageWarn" class="warn hidden">'''
A_MARKER = 'var APP_VERSIE = "v23.54";'

if DOE_APP:
    ANKERS = [A_MARKER, TAAL_START, TAAL_EIND, PROEF_START, PROEF_EIND, A_LAAD]
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:90].replace("\n", " / ") for a in ontbreekt) +
              "\n\nDeze patch bouwt op v23.54. Eerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


def knip(start, eind):
    """Haalt het blok tussen start en eind (inclusief) uit src en geeft het terug. Verhuizen, niet
       kopiëren: als dit blok twee keer zou bestaan zouden ze uit elkaar gaan lopen."""
    global src
    assert src.count(start) == 1, "beginanker komt %d keer voor: %s" % (src.count(start), start[:80])
    i = src.index(start)
    j = src.index(eind, i)
    assert j != -1
    j += len(eind)
    blok = src[i:j]
    src = src[:i] + src[j:]
    return blok


if DOE_APP:
    rep(A_MARKER, 'var APP_VERSIE = "%s";' % NIEUW)

    taal_blok = knip(TAAL_START, TAAL_EIND)
    proef_blok = knip(PROEF_START, PROEF_EIND)

    VROEG = '''<script>
/* ================= HET VROEGE SCHERM (v23.55) =================

   Gemeten op traag 4G (1,6 Mbit, 300 ms rtt, cpu 4x geremd), met gzip en de cacheheaders van
   GitHub Pages: de statische HTML staat er na ~950 ms, het grote script pas na 4,3 seconden, en de
   app is bruikbaar na 4,9. Het laadscherm van v23.54 maakte dat gat eerlijk; dit blok maakt het
   leeg.

   Want de vreemde hoeft helemaal niet op de app te wachten. Het eerste dat hij ziet is geen app,
   het zijn drie woordjes met elk twee knoppen. Dat is 2,3 KB, en dat kan mee met de HTML.

   Niets hieronder is een kopie. PROEF_WOORDEN, PROEF_TXT, UI_LANGS en de proef-opslag stonden in
   het grote script en zijn hierheen verhuisd; het zijn globals, dus daar verandert niets. Het enige
   nieuwe is vroegVraag(), en die dupliceert renderProef() niet maar schrijft in het formaat waar
   renderProef() sinds v23.44 al uit hervat: {bezig:true, stand:{i,xp,res}}. De overdracht is dus
   een koppeling die er al was.

   Alles staat in een try/catch en bij twijfel doet dit blok niets. Dan gebeurt er precies wat er
   voor v23.55 gebeurde, en dat is de reden dat dit twee dagen voor een lancering kan. */
''' + taal_blok + proef_blok + '''
var vroegBezig = false;
function vroegVraag(){
  var card = document.getElementById("profCard");
  if(!card) return;
  var box = document.getElementById("proefBox");
  if(!box){
    box = document.createElement("div");
    box.id = "proefBox"; box.className = "card";
    card.parentNode.insertBefore(box, card);
  }
  card.classList.add("hidden");
  box.classList.remove("hidden");
  var L = proefTaal(), d = PROEF_TXT[L] || PROEF_TXT.en;
  var st = proefStand;
  var i = st.i;
  if(i >= PROEF_WOORDEN.length){
    /* De drie zijn op en het grote script is er nog niet. Dat is zeldzaam (drie vragen met 850 ms
       feedback kosten meer tijd dan er nog te wachten valt), maar niet onmogelijk op een hele
       trage lijn. Dan staat hier de uitslag zonder de vervolgvraag, en neemt renderProef() het
       over zodra hij er is. */
    box.innerHTML = "<span class='kicker'>\\u00a1Vamos!</span>" +
      "<h2 style='margin:6px 0 2px'>" + d.klaarKop + "</h2>" +
      "<p class='muted'>+" + st.xp + " taco's</p>";
    return;
  }
  var w = PROEF_WOORDEN[i];
  var opts = w.opts[L] || w.opts.en;
  /* Het lege vak van 100 pixels is de plek van Chispa. petSVG() hangt aan S en aan de hele
     tekenboom en verhuist dus niet mee; het ei verschijnt zodra het grote script er is. Zonder dit
     vak zouden de knoppen op dat moment naar beneden springen. */
  box.innerHTML = "<div style='text-align:center'><div style='width:100px; height:100px; margin:0 auto'></div></div>" +
    "<span class='kicker'>\\u00a1Vamos! \\u00b7 " + (i + 1) + "/" + PROEF_WOORDEN.length + "</span>" +
    (i === 0 ? "<h2 style='margin:6px 0 2px'>" + d.kop + "</h2><p class='muted' style='margin:0 0 8px'>" + d.sub + "</p>" : "") +
    "<p style='font-size:1.7rem; margin:8px 0 2px; text-align:center'><b class='es'>" + w.es + "</b></p>" +
    "<p class='muted' style='margin:0 0 10px; text-align:center'>" + d.vraag + "</p>" +
    opts.map(function(o, oi){ return "<button class='opt' data-proef='" + oi + "' style='margin:4px 0'>" + o + "</button>"; }).join("") +
    "<p id='vroegUit' class='muted' style='margin:10px 0 0; text-align:center; min-height:1.2em'></p>" +
    "<p class='muted' style='margin-top:10px; text-align:center'><a href='#' id='lnkProefSkip'>" + d.heb + "</a></p>";
  var knoppen = box.querySelectorAll("button[data-proef]");
  for(var k = 0; k < knoppen.length; k++){
    (function(b){
      b.onclick = function(){
        for(var x = 0; x < knoppen.length; x++){ knoppen[x].disabled = true; }
        var goed = (+b.getAttribute("data-proef")) === w.c;
        st.xp += goed ? 2 : 1;
        st.res[w.id] = goed;
        st.i++;
        /* Precies het formaat waar renderProef() uit hervat. Meteen wegschrijven en niet pas aan
           het eind: als het grote script tussen twee vragen door binnenkomt, pakt hij de stand op
           in plaats van opnieuw bij nul te beginnen. */
        proefBewaar({bezig:true, xp:st.xp, res:st.res, stand:st});
        /* Geen toast en geen confetti: die zitten in het grote script. Op een telefoon is een regel
           in het kaartje zelf trouwens beter zichtbaar dan een balk onderaan. */
        var u = document.getElementById("vroegUit");
        if(u) u.innerHTML = goed ? "<b>" + d.goed + "</b>" : d.fout + "<b>" + opts[w.c] + "</b>" + d.foutXp;
        setTimeout(function(){
          /* Is het grote script er inmiddels? Dan geeft het vroege blok het stokje door en verdwijnt
             het uit beeld. renderProef() leest dezelfde stand terug. */
          if(typeof renderProef === "function"){ vroegBezig = false; renderProef(); return; }
          vroegVraag();
        }, 850);
      };
    })(knoppen[k]);
  }
  var sk = document.getElementById("lnkProefSkip");
  if(sk) sk.onclick = function(e){
    if(e && e.preventDefault) e.preventDefault();
    proefBewaar({overgeslagen:true});
    vroegBezig = false;
    box.classList.add("hidden");
    card.classList.remove("hidden");
    return false;
  };
}
(function(){
  try {
    /* Dezelfde voorwaarden als normaalBegin() in het grote script, maar dan uit ruwe localStorage,
       want profiles en proefData bestaan hier nog niet als objecten. normaalBegin() blijft gewoon
       staan: dit blok vervangt hem niet, het loopt erop vooruit. */
    if(location.search) return;                       // uitnodigingslink, ?beheer=, ?les= — dat regelt het grote script
    var pr = localStorage.getItem("espanol-proef-v1");
    if(pr){
      var pd = JSON.parse(pr);
      if(pd && (pd.klaar || pd.overgeslagen)) return;
      if(pd && pd.stand && pd.stand.i >= PROEF_WOORDEN.length) return;   // de helling is aan de beurt
    }
    var pf = localStorage.getItem("espanol-profiles-v1");
    if(pf){
      var p = JSON.parse(pf);
      if(p && p.list && p.list.length) return;        // geen vreemde
    }
    if(!document.getElementById("profCard")) return;
    var bew = null;
    try { bew = pr ? JSON.parse(pr) : null; } catch(e){ bew = null; }
    proefStand = (bew && bew.bezig && bew.stand) ? bew.stand : {i:0, xp:0, res:{}};
    vroegBezig = true;
    vroegVraag();
    /* Er staat nu iets echts, dus het gordijn van v23.54 mag open. Voor wie al een profiel heeft
       gebeurt dat pas als boot() klaar is, en dat klopt: voor die bezoeker valt er niets eerder te
       laten zien. */
    if(window.__laadWeg) window.__laadWeg();
  } catch(e){ vroegBezig = false; }
})();
</script>
'''

    rep(A_LAAD, VROEG + A_LAAD)

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
