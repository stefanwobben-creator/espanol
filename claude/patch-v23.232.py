#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.232 - vier dingen die de app zei of onthield en die niet klopten
#
# Stefan, 3 sep, vier klachten op een rij. Ze lijken los maar hebben dezelfde vorm: de app doet
# iets wat hij niet doet, of onthoudt iets wat hij hoort te vergeten.
#
# 1. "EL OF LA BLIJFT FOUT ZEGGEN TERWIJL IK NU AL DAGEN ALLES GOED DOE"
#
# Op de route staat bij El of la: "fout gegaan", in het rood, met "vandaag" ernaast.
#
# Sinds v23.228 zit het doosje op het PATROON en niet op het concept, en gramLees() vat dat samen
# als het ZWAKSTE doosje. Dat is precies goed voor de planning (het concept is zo sterk als zijn
# zwakste patroon), maar gcStatusHtml() las die samenvatting als een oordeel:
#
#     if(st.fout && (st.box || 0) === 0) return "fout gegaan";
#
# st.fout is de OPTELSOM van alle fouten ooit, en st.box is het zwakste doosje. Bij genero staat de
# kale sleutel (fouten die je in het wild maakt, buiten de microles) op doos 0 en die komt daar
# alleen vanaf als je toevallig weer een quiz of een tegel op dat concept doet. Zolang dat niet
# gebeurt zegt de route "fout gegaan", ook na een week foutloos oefenen.
#
# Nu leest hij de datum in plaats van de optelsom: "fout gegaan" betekent dat het de afgelopen twee
# dagen echt fout ging. Daarna zegt hij gewoon in welk doosje je zit. Nul is geen bericht, en een
# fout van vorige maand is geen bericht.
#
# 2. "ALS IK NAAR DE PUZZEL GA STAAT IE NOG VOORGEVULD MET HET ANTWOORD VAN VORIGE KEER"
#
# Letras had sinds v23.188 een verversing:
#
#     verse: function(){ ltSpel = null; }
#
# En renderFunLetras() begint met:
#
#     if(!ltSpel && !ltHerstel()) ltNieuw();
#
# ltHerstel() haalt de puzzel terug uit S.letras, inclusief alles wat je al gevonden had. De
# verversing maakte dus het geheugen leeg en de opslag zette hem meteen terug. Een verversing die
# alleen het geheugen leegmaakt terwijl de opslag hem terugzet, verandert niets.
#
# Twee dingen: de verversing wist nu ook de opslag, en ltHerstel() weigert een puzzel die al af is.
# Dat tweede is de vangregel: een uitgespeelde puzzel is nooit iets om naar terug te keren, hoe je
# ook binnenkomt.
#
# 3. "ALS IK EEN ANTWOORD INTYP WORDT HET VAKJE NIET GROEN OF ROOD"
#
# Klopt, en het was erger dan geen kleur. ltCheck() deed bij een goed woord alles (punt, geluid,
# confetti) en bij een fout woord LETTERLIJK NIETS: geen kleur, geen regel, geen geluid. Je staat
# dan met vijf letters op je scherm en de app zwijgt. ltSpel.melding bestond al als veld en werd
# nergens getoond.
#
# Nu kleurt het woord zodra het lang genoeg is: rood als het niet in deze puzzel zit, groen als het
# er wel in zit. En na een vondst staat er een regel met het woord en de vertaling, want dat is het
# moment waarop je iets leert.
#
# 4. "HET SPIEKBRIEFJE KAN IK OOK NIET VINDEN"
#
# Onder een matig toetsje staat een knop "Spiekbrief". Die deed show("spiekbrief") en dat is het
# TABBLAD, dat "Grammatica" heet en begint met de route van 31 onderwerpen. De spiekbrief zelf
# staat verderop, en dan alleen als hij geen eigen onderwerpkaart heeft (spiekNaslagHtml toont
# alleen de weeskaarten). Voor een toetsje mét onderwerpkaart is de spiekbrief via die knop dus
# nergens te vinden, terwijl de knop wel wist welke kaart erbij hoorde: qz.spiek staat er.
#
# Nu opent diezelfde knop de kaart zelf, met de titel erboven en een weg terug. Eén functie die
# weet hoe je een spiekbrief opent, en iedereen die ernaartoe wijst gebruikt hem.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.232"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function spiekOpen(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # =========================================================================================
    # 1. vier plekken schreven hetzelfde oordeel op; nu een predicaat
    # =========================================================================================
    rep("""function gcStatusHtml(cid){
  var st = gramLees(cid);
  if(st.fout && (st.box || 0) === 0) return "<span style='color:var(--red)'>" + ct("fout gegaan", "got this wrong") + "</span>";
  if(!st.goed && !st.fout) return ct("nog niet gedaan", "not done yet");
  return ct("doos ", "box ") + (st.box || 0) + "/" + (GRAM_BOX.length - 1);
}""",
"""/* ================= WANNEER IS EEN ONDERWERP "FOUT GEGAAN"? (v23.232) =================

   Stefan: "el la los las die ken ik echt wel (...) het blijft fout zeggen terwijl ik nu al dagen
   lang alles goed doe."

   Op vier plekken stond hetzelfde oordeel met de hand uitgeschreven:

       st.fout && (st.box || 0) === 0

   Sinds v23.228 is st.fout de OPTELSOM van alle fouten ooit en st.box het ZWAKSTE doosje van het
   concept. Voor de planning is dat precies goed (een concept is zo sterk als zijn zwakste patroon),
   maar als oordeel deugt het niet. Bij genero staat de kale sleutel (fouten in het wild, buiten de
   microles) op doos 0, en die komt daar alleen vanaf als er toevallig weer een quiz of een tegel op
   dat concept langskomt. Tot die tijd is het antwoord op "ging dit fout?" altijd ja.

   En dat deed meer dan een rood woordje op de route: gcVandaagLijst() zet alles wat "fout ging"
   vooraan, dus El of la werd elke dag opnieuw gekozen als het onderwerp van vandaag. Precies de
   klacht.

   Nu leest het de DATUM in plaats van de optelsom, op één plek. Een fout van vorige maand is geen
   bericht. */
var GC_VERS_DAGEN = 2;
function gcStaatFout(st){
  if(!st || !st.laatst) return false;
  if((st.box || 0) !== 0) return false;
  return st.laatst >= addDays(today(), -GC_VERS_DAGEN);
}
function gcStatusHtml(cid){
  var st = gramLees(cid);
  if(gcStaatFout(st)) return "<span style='color:var(--red)'>" + ct("fout gegaan", "got this wrong") + "</span>";
  if(!st.goed && !st.fout) return ct("nog niet gedaan", "not done yet");
  return ct("doos ", "box ") + (st.box || 0) + "/" + (GRAM_BOX.length - 1);
}""")

    # en de drie andere plekken die hetzelfde uitschreven
    rep("""  var af = (st.goed || 0) > 0 && (st.box || 0) > 0 && !(st.fout && (st.box || 0) === 0);""",
"""  var af = (st.goed || 0) > 0 && (st.box || 0) > 0 && !gcStaatFout(st);""")

    rep("""    if(st.fout && (st.box || 0) === 0){ fout.push({c:c, st:st}); return; }""",
"""    if(gcStaatFout(st)){ fout.push({c:c, st:st}); return; }""")

    rep("""    else if(st.fout && (st.box || 0) === 0) fout++;""",
"""    else if(gcStaatFout(st)) fout++;""")

    # =========================================================================================
    # 2. de verversing van Letras wist ook de opslag
    # =========================================================================================
    rep("""    /* v23.188: de woordenzoeker had als enige rasterspel geen verse, dus je kwam terug op het
     raster dat je al had uitgespeeld. Zelfde afspraak als bij Letras en Crucigrama. */""",
"""    /* v23.188: de woordenzoeker had als enige rasterspel geen verse, dus je kwam terug op het
     raster dat je al had uitgespeeld. Zelfde afspraak als bij Letras en Crucigrama.

     v23.232: en Letras had die afspraak wél, maar hij deed niets. `ltSpel = null` maakt het
     geheugen leeg, waarna renderFunLetras() met ltHerstel() de puzzel uit S.letras terugzet,
     inclusief alles wat je al gevonden had. Een verversing die alleen het geheugen leegmaakt
     terwijl de opslag hem terugzet, verandert niets. */""")

    rep("""verse:function(){ ltSpel = null; }}""",
"""verse:function(){ ltVergeet(); }}""")

    rep("""function ltBewaar(){
  if(!ltSpel){ delete S.letras; persist(); return; }
  S.letras = {letters: ltSpel.letters.join(""), gevonden: Object.keys(ltSpel.gevonden)};
  persist();
}""",
"""/* v23.232: één plek die een puzzel echt weggooit, geheugen en opslag tegelijk. */
function ltVergeet(){
  ltSpel = null;
  try { delete S.letras; persist(); } catch(e){}
}
function ltBewaar(){
  if(!ltSpel){ delete S.letras; persist(); return; }
  /* v23.232: de vlag "af" wordt hier gezet, door de enige die het zeker weet: het spel dat op dit
     moment loopt en zijn eigen doelenlijst kent. ltHerstel() leest hem en rekent niets na. */
  var af = ltSpel.doelen.length > 0 &&
           Object.keys(ltSpel.gevonden).length >= ltSpel.doelen.length;
  S.letras = {letters: ltSpel.letters.join(""), gevonden: Object.keys(ltSpel.gevonden), af: af ? 1 : 0};
  persist();
}""")

    rep("""function ltHerstel(){
  var b = S && S.letras;
  if(!b || !b.letters) return false;""",
"""function ltHerstel(){
  var b = S && S.letras;
  if(!b || !b.letters) return false;""")

    # de vangregel: een uitgespeelde puzzel komt nooit terug, hoe je ook binnenkomt
    rep("""function ltHerstel(){
  var b = S && S.letras;
  if(!b || !b.letters) return false;""",
"""function ltHerstel(){
  var b = S && S.letras;
  if(!b || !b.letters) return false;
  /* v23.232, en dit is de vangregel. Er zijn meer wegen naar dit scherm dan er verversingen zijn
     (de tegel, de dagkaart, de terugknop van de browser, een herstart), en langs elk van die wegen
     is een uitgespeelde puzzel hetzelfde: niets om naar terug te keren. Dus wordt hij hier
     geweigerd, op de enige plek waar alle wegen samenkomen.

     De vlag komt uit ltBewaar() en wordt hier niet opnieuw uitgerekend. Dat was de eerste poging,
     en die was onbetrouwbaar: ltHerstel() bouwt de doelenlijst opnieuw uit de letters, en die lijst
     hoeft niet dezelfde te zijn als waarmee je speelde (LT_MAX_DOELEN kapt hem af). Een puzzel die
     af was kon zo alsnog als onaf terugkomen. Wie het weet schrijft het op; wie het niet weet
     rekent het niet na. */
  if(b.af){ try { delete S.letras; persist(); } catch(e){} return false; }""")

    # =========================================================================================
    # 3. het woord kleurt, en een misser krijgt antwoord
    # =========================================================================================
    rep("""function ltCheck(){
  var w = ltHuidig();
  if(w.length < LT_MIN) return;
  var raak = ltSpel.doelen.filter(function(d){ return ltPlat(d.es) === w; })[0];
  if(raak && !ltSpel.gevonden[ltPlat(raak.es)]){
    ltSpel.gevonden[ltPlat(raak.es)] = 1;
    ltSpel.gekozen = [];
    ltSpel.melding = "";""",
"""/* v23.232. Stefan: "als ik een antwoord intyp wordt het vakje niet groen of rood."

   Klopt, en het was erger dan geen kleur: bij een goed woord gebeurde alles (punt, piep, confetti)
   en bij een fout woord LETTERLIJK NIETS. Je stond met vijf letters op je scherm en de app zweeg.
   ltSpel.melding bestond al als veld en werd nergens getoond.

   ltStaat() zegt wat er van het woord onder je duim te vinden is; renderFunLetras() kleurt ermee.
   Eén functie, want de kleur en de melding horen niet uit elkaar te lopen. */
function ltStaat(){
  if(!ltSpel) return "";
  var w = ltHuidig();
  if(w.length < LT_MIN) return "";
  return ltSpel.doelen.some(function(d){ return ltPlat(d.es) === w; }) ? "raak" : "mis";
}
function ltCheck(){
  var w = ltHuidig();
  if(w.length < LT_MIN) return;
  var raak = ltSpel.doelen.filter(function(d){ return ltPlat(d.es) === w; })[0];
  if(raak && !ltSpel.gevonden[ltPlat(raak.es)]){
    ltSpel.gevonden[ltPlat(raak.es)] = 1;
    ltSpel.gekozen = [];
    ltSpel.melding = raak.es + " \\u00b7 " + raak.nl;""")

    rep("""    "<div class='lt-woord'>" + (huidig || "&nbsp;") + "</div>" +""",
"""    "<div class='lt-woord " + ltStaat() + "'>" + (huidig || "&nbsp;") + "</div>" +
    /* De regel onder het woord. Bij een vondst staat hier wát je vond en wat het betekent: dat is
       het moment waarop er iets te leren valt, en dat moment stond leeg. Bij een te lang woord dat
       er niet in zit staat er waarom er niets gebeurt. */
    "<div class='lt-melding'>" +
      (ltStaat() === "mis"
        ? "<span class='mis'>" + ct(huidig + " staat niet in deze puzzel", huidig + " is not in this puzzle") + "</span>"
        : (ltSpel.melding ? "<span class='raak'>\\u2713 " + ltSpel.melding + "</span>" : "&nbsp;")) +
    "</div>" +""")

    rep("""  document.getElementById("btnLtWis").onclick = function(){ ltSpel.gekozen = []; renderFunLetras(); };""",
"""  document.getElementById("btnLtWis").onclick = function(){ ltSpel.gekozen = []; ltSpel.melding = ""; renderFunLetras(); };""")

    rep("""  document.getElementById("btnFunTerug").onclick = function(){ ltSpel = null; funView = null; renderFun(); };
  if(klaar) naRondeWire();""",
"""  document.getElementById("btnFunTerug").onclick = function(){ ltVergeet(); funView = null; renderFun(); };
  if(klaar) naRondeWire();""")

    rep("""  .lt-woord{text-align:center; font-size:1.6rem; font-weight:800; letter-spacing:.12em;
            min-height:2.1rem; margin:10px 0 6px; color:var(--accent);}""",
"""  .lt-woord{text-align:center; font-size:1.6rem; font-weight:800; letter-spacing:.12em;
            min-height:2.1rem; margin:10px 0 2px; color:var(--accent);}
  /* v23.232: rood zodra het woord lang genoeg is en niet in deze puzzel zit, groen als het er wel
     in zit. Zonder dit staat er een woord op je scherm en zegt de app niets. */
  .lt-woord.mis{color:var(--red);}
  .lt-woord.raak{color:var(--green);}
  .lt-melding{text-align:center; min-height:1.2rem; font-size:.85rem; margin-bottom:6px;}
  .lt-melding .mis{color:var(--red);}
  .lt-melding .raak{color:var(--green); font-weight:600;}""")

    # =========================================================================================
    # 4. een spiekbrief die je kunt openen
    # =========================================================================================
    rep("""var gcLeesId = null;""",
"""var gcLeesId = null;
/* ================= EEN SPIEKBRIEF DIE JE KUNT OPENEN (v23.232) =================

   Stefan: "het spiekbriefje kan ik ook niet vinden."

   Onder een matig toetsje stond een knop "Spiekbrief", en die deed show("spiekbrief"). Dat is het
   TABBLAD, dat Grammatica heet en begint met de route van 31 onderwerpen. De spiekbrief zelf staat
   verderop op dat scherm, en dan alleen als hij geen eigen onderwerpkaart heeft: spiekNaslagHtml()
   toont met opzet alleen de weeskaarten. Voor een toetsje mét onderwerpkaart was de spiekbrief via
   die knop dus nergens te vinden.

   Terwijl de knop wist welke kaart erbij hoorde: qz.spiek staat er, dat is de index in CHEATSHEET.
   Wat ontbrak was een manier om er één te openen. Nu is er er één, en iedereen die naar een
   spiekbrief wijst gebruikt hem. */
var spiekLeesIdx = null;
function spiekOpen(idx){
  if(idx === undefined || idx === null) { show("spiekbrief"); return; }
  spiekLeesIdx = +idx;
  gwSess = null; gcLeesId = null;
  show("spiekbrief");
  try { window.scrollTo(0, 0); } catch(e){}
}
function spiekLeesHtml(){
  var c = CHEATSHEET[spiekLeesIdx];
  if(!c) return "";
  /* De weg terug staat boven én onder, want een spiekbrief is lang en je bent hier gekomen vanaf
     een toetsje waar je nog mee bezig was. */
  var terug = "<div class='row'><button class='ghost' id='btnSpiekTerug'>" +
    ct("\\u2190 Terug naar Grammatica","\\u2190 Back to Grammar") + "</button></div>";
  return "<div class='card'><span class='kicker'>" + ct("Spiekbrief","Cheat sheet") + "</span>" +
    "<h2 style='margin-top:2px'>" + spiekTitel(c) + "</h2>" + terug +
    "<div style='margin-top:10px'>" + spiekHtml(c) + "</div>" + terug + "</div>";
}""")

    rep("""  if(gcLeesId){
    el.innerHTML = renderGcLees();
    wireGramWiz(el);
    jargonScan(el);
    return;
  }""",
"""  if(gcLeesId){
    el.innerHTML = renderGcLees();
    wireGramWiz(el);
    jargonScan(el);
    return;
  }
  // v23.232: één spiekbrief, opengeslagen, met een weg terug.
  if(spiekLeesIdx !== null && CHEATSHEET[spiekLeesIdx]){
    el.innerHTML = spiekLeesHtml();
    el.querySelectorAll("#btnSpiekTerug").forEach(function(b){
      b.onclick = function(){ spiekLeesIdx = null; renderCheat(); try { window.scrollTo(0, 0); } catch(e){} };
    });
    jargonScan(el);
    return;
  }""")

    rep("""    if(bns) bns.onclick = function(){ closeQuiz(); show("spiekbrief"); };""",
"""    /* v23.232: naar de kaart die bij dít toetsje hoort, niet naar het tabblad. qz.spiek stond er
       al; er was alleen geen manier om er één te openen. */
    if(bns) bns.onclick = function(){ closeQuiz(); spiekOpen(qz.spiek[0]); };""")

    # en wie het tabblad langs de gewone weg opent, ziet weer de route en niet de laatste kaart
    rep("""  if(tabId==="cursus"){ renderCursus(); }""",
"""  // v23.232: een opengeslagen spiekbrief hoort bij de reis ernaartoe, niet bij het tabblad. Kom je
  // hier langs de gewone weg binnen, dan zie je weer de route.
  if(tabId==="spiekbrief" && !spiekVerseOpen){ spiekLeesIdx = null; }
  spiekVerseOpen = false;
  if(tabId==="cursus"){ renderCursus(); }""")

    rep("""function spiekOpen(idx){
  if(idx === undefined || idx === null) { show("spiekbrief"); return; }
  spiekLeesIdx = +idx;""",
"""var spiekVerseOpen = false;
function spiekOpen(idx){
  if(idx === undefined || idx === null) { show("spiekbrief"); return; }
  spiekLeesIdx = +idx;
  spiekVerseOpen = true;""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    for nodig in ["function gcStaatFout(", "function ltVergeet(", "function ltStaat(",
                  "function spiekOpen(", "function spiekLeesHtml(", "var spiekLeesIdx = null",
                  "verse:function(){ ltVergeet(); }", "spiekOpen(qz.spiek[0])",
                  ".lt-woord.mis{", ".lt-melding{"]:
        assert nodig in src, "ontbreekt: " + nodig
    for naam in ["gcStaatFout", "ltVergeet", "ltStaat", "spiekOpen", "spiekLeesHtml"]:
        c = src.count("function " + naam + "(")
        assert c == 1, "function %s staat %d keer in het bestand" % (naam, c)
    # het oude oordeel op de optelsom is echt weg
    # let op: het commentaar hierboven CITEERT de oude uitdrukking, dus toets op de uitvoerbare
    # vormen en niet op de tekst zelf
    for weg in ["if(st.fout && (st.box || 0) === 0) return",
                "&& !(st.fout && (st.box || 0) === 0)",
                "if(st.fout && (st.box || 0) === 0){ fout.push",
                "else if(st.fout && (st.box || 0) === 0) fout++"]:
        assert weg not in src, "er is nog een plek die het oordeel met de hand uitschrijft: " + weg
    # 1 definitie + 4 aanroepers: de status, het vinkje op de route, de keuze van vandaag, de reden
    assert src.count("gcStaatFout(st)") == 5, \
        "verwacht 1 definitie en 4 aanroepers, kreeg %d" % src.count("gcStaatFout(st)")
    # de verversing van Letras wist geheugen en opslag, en nergens blijft de oude vorm staan
    assert "verse:function(){ ltSpel = null; }" not in src, "de oude verse van Letras staat er nog"
    # de vangregel in ltHerstel
    assert "if(b.af){" in src, "ltHerstel weigert een afgemaakte puzzel niet"
    assert "af: af ? 1 : 0" in src, "ltBewaar schrijft de vlag niet"
    # de knop wijst niet meer naar het tabblad
    assert 'bns.onclick = function(){ closeQuiz(); show("spiekbrief"); }' not in src, \
        "de spiekbriefknop gaat nog naar het tabblad"
    APP.write_text(src, encoding="utf-8")
    print("index.html: fout gegaan leest de datum, Letras vergeet en kleurt, de spiekbrief gaat open")
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
