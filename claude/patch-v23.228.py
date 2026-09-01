#!/usr/bin/env python3
# v23.228 - het doosje verhuist van het concept naar het patroon
#
# Stefan, 1 sep: "el la los las die ken ik echt wel, de grammaticale regel, maar deze blijft
# terugkomen door het spaced repetition principe. dus bij grammaticale concepten en oefening is een
# effectievere aanpak nodig."
#
# En op de vraag wat er met zijn huidige stand moest gebeuren: "dat ik mijn progressie nu kwijt raak
# met grammatica is niet zo erg als we het daardoor conceptueel nu wel beter doen (dat doe ik de
# lessen gewoon nog een keer)."
#
# DE METING, UIT ZIJN EIGEN NACHTLOGBOEK
#
#     concept        doos  goed  fout   patronen
#     genero            2    55    17      5
#     indefimperf       2    37    17      4
#     serestar          2    39    12      5
#     reflexivo         0    11    11      5
#     zapato            5     6     0      5
#     tuusted           5     7     0      8
#     comparar          5     5     0      5
#
# Lees de kolommen goed en doos naast elkaar. Wat hij 72 keer heeft gedaan staat op doos 2; wat hij
# vijf keer heeft gedaan staat op doos 5. Meer oefenen zakt je. Dat kan nooit de bedoeling zijn.
#
# WAAROM DAT GEBEURT
#
# El of la is één doosje met vijf patronen eronder: de regel (-ción, -dad), de Griekse val (el
# problema), -or is mannelijk, de uitgang van een willekeurig zelfstandig naamwoord, en hetzelfde in
# het meervoud. Hij kent er vier. De vijfde is geen regel maar een lijstje woorden.
#
# Eén misser op dat vijfde patroon zet de doos van alle vijf naar nul. En omdat alle vijf maar twee
# knoppen hebben, is er sinds v23.212 ook nog een tweede schone dag nodig om één doos te klimmen.
#
# Nagerekend over een jaar, met een foutkans van 50% op de val en 6% op de rest:
#
#     doosje per concept    243 vragen per jaar, waarvan 80% op wat je al kent
#     doosje per patroon    718 vragen per jaar, waarvan 60% op de val
#
# Vier van de vijf keer dat el of la langskomt, oefent hij dus iets wat hij al kan. En de vijfde
# keer, de enige die ertoe doet, gooit alles om.
#
# WAT ER VERANDERT
#
# Het doosje gaat van het concept naar het patroon. genero heeft er vanaf nu zes: vijf voor zijn
# eigen patronen, en één voor de fouten die je in het WILD maakt.
#
# Die laatste is geen restje maar een eigen categorie, en dat is de sleutel tot deze hele ronde.
# gramBij() wordt namelijk op zes plaatsen aangeroepen die geen patroon kennen: een quiz, de tegels,
# een fout in een vrije zin (foutRegel), de Clasificador en El Corrector. Dat is bewijs over het
# concept en niet over één patroon. Zou zo'n misser alle patronen resetten, dan hadden we precies
# het oude probleem terug; zou hij nergens landen, dan verdwijnt het beste signaal dat de app heeft.
# Dus krijgt hij zijn eigen doosje onder dezelfde sleutel als vroeger: "in een echte zin".
#
# Een concept is vanaf nu zo sterk als zijn ZWAKSTE doosje. Dat is wat er op je scherm staat, en het
# is de eerlijke samenvatting: je kent el of la pas als je de val ook kent.
#
# EN DE OPFRISSER VRAAGT VOORTAAN HET PATROON DAT AAN DE BEURT IS
#
# Dit is de helft waar het effect vandaan komt. De wachtrij levert nu een patroon in plaats van een
# concept, en de opfrisser wordt uit dát patroon gebouwd. Kwam je vorige week om op de Griekse val,
# dan krijg je de Griekse val, en niet vier keer op vijf iets anders.
#
# WAT ER MET DE OUDE STAND GEBEURT
#
# De oude stand ZIT in dat zesde doosje: S.gram["genero"] was al de concept-brede sleutel en blijft
# precies waar hij is, met zijn tellers en zijn doos. Wat verdwijnt is dat die ene doos alles
# aanstuurde. De vijf patroondoosjes beginnen leeg, en een leeg doosje is geen herhaling maar
# kennismaking: ze komen pas in de wachtrij zodra je ze een keer gedaan hebt. Precies wat Stefan
# voorstelde: de lessen nog een keer doen, en dan bouwt het zich per patroon opnieuw op.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.228"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function gramSleutel(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # =========================================================================================
    # 1. de sleutel, en het lezen
    # =========================================================================================
    rep("""function gramLees(cid){
  return (S.gram && S.gram[cid]) || {box:0, due:"", goed:0, fout:0, laatst:""};
}""",
"""/* ================= HET DOOSJE ZIT OP HET PATROON (v23.228) =================

   Stefan: "el la los las die ken ik echt wel, de grammaticale regel, maar deze blijft terugkomen."

   Gemeten in zijn eigen logboek: genero 55 goed tegen 17 fout, en na 72 beurten nog steeds doos 2.
   Terwijl comparar met vijf beurten op doos 5 staat. Meer oefenen zakt je, en dat kan niet.

   De oorzaak is dat er één doos was voor vijf patronen. Hij kent de regel (-ci\\u00f3n is la), de -or, en
   het meervoud; hij mist de Griekse val (el problema, el tema), en dat is geen regel maar een
   lijstje woorden. \\u00c9\\u00e9n misser op die val zette de doos van alle vijf naar nul.

   Vanaf nu heeft elk patroon zijn eigen doos, onder de sleutel "concept#index". En de KALE sleutel
   (zonder #) blijft bestaan met een eigen betekenis: fouten die je in het wild maakt. gramBij()
   wordt namelijk op zes plaatsen aangeroepen die geen patroon kennen (een quiz, de tegels, een
   fout in een vrije zin, de Clasificador, El Corrector). Dat is bewijs over het concept en niet
   over \\u00e9\\u00e9n patroon, en het is het beste signaal dat de app heeft: het komt uit echt gebruik. Dus
   krijgt het zijn eigen doosje in plaats van alle andere te resetten. */
function gramSleutel(cid, pi){
  return (pi === undefined || pi === null || pi === "") ? String(cid) : String(cid) + "#" + pi;
}
function gramRuw(sleutel){
  return (S.gram && S.gram[sleutel]) || null;
}
function gramPatroonN(cid){
  var c = null;
  try { c = gcConcept(String(cid).split("#")[0]); } catch(e){ c = null; }
  return (c && c.patronen) ? c.patronen.length : 0;
}
/* Alle doosjes van dit concept die al bestaan: de patronen die je hebt gedaan, plus de kale sleutel
   als je de fout ooit in het wild hebt gemaakt. Een doosje dat er niet is, is geen nul maar een
   onbekende: nooit gedaan is kennismaking en geen herhaling. */
function gramDoosjes(cid){
  var s = String(cid || "").split("#")[0], uit = [], n = gramPatroonN(s), i, st;
  st = gramRuw(s);
  if(st) uit.push({sleutel:s, pi:null, st:st});
  for(i = 0; i < n; i++){
    st = gramRuw(gramSleutel(s, i));
    if(st) uit.push({sleutel:gramSleutel(s, i), pi:i, st:st});
  }
  return uit;
}
/* Een concept is zo sterk als zijn ZWAKSTE doosje, en dat is de eerlijke samenvatting: je kent el
   of la pas als je de val ook kent. De tellers worden opgeteld, want die zijn je geschiedenis. */
function gramLees(cid){
  var s = String(cid || "");
  if(s.indexOf("#") !== -1) return gramRuw(s) || {box:0, due:"", goed:0, fout:0, laatst:""};
  var d = gramDoosjes(s);
  if(!d.length) return {box:0, due:"", goed:0, fout:0, laatst:""};
  var zwak = null, goed = 0, fout = 0, laatst = "";
  d.forEach(function(x){
    var st = x.st;
    goed += st.goed || 0;
    fout += st.fout || 0;
    if((st.laatst || "") > laatst) laatst = st.laatst || "";
    if(!zwak
       || (st.box || 0) < (zwak.box || 0)
       || ((st.box || 0) === (zwak.box || 0) && (st.due || "") < (zwak.due || ""))) zwak = st;
  });
  return {box: zwak.box || 0, due: zwak.due || "", half: zwak.half || 0, bd: zwak.bd || "",
          goed: goed, fout: fout, laatst: laatst, doosjes: d.length};
}""")

    # =========================================================================================
    # 2. het schrijven
    # =========================================================================================
    rep("""function gramBij(cid, goed, keuzes){
  if(!cid) return;
  S.gram = S.gram || {};
  var st = S.gram[cid] || {box:0, due:"", goed:0, fout:0, laatst:""};""",
"""/* v23.228: `pi` erbij. Zonder patroonindex schrijft hij naar de kale sleutel, en dat is precies wat
   de zes aanroepers buiten de microles moeten doen: die weten welk concept fout ging maar niet welk
   patroon, want hun bewijs komt uit een vrije zin of een spel. */
function gramBij(cid, goed, keuzes, pi){
  if(!cid) return;
  S.gram = S.gram || {};
  var sleutel = gramSleutel(cid, pi);
  var st = S.gram[sleutel] || {box:0, due:"", goed:0, fout:0, laatst:""};""")
    rep("""  S.gram[cid] = st;
}
function gramAangeraakt(cid){""",
"""  S.gram[sleutel] = st;
}
function gramAangeraakt(cid){""")

    # =========================================================================================
    # 3. de vraag draagt zijn patroon
    # =========================================================================================
    rep("""    var q = null;
    try { q = p(); } catch(e){ q = null; }
    if(!q || gezien[q.v]) continue;
    gezien[q.v] = 1;
    uit.push(gcSchud(q));
  }
  return uit;
}""",
"""    var q = null;
    try { q = p(); } catch(e){ q = null; }
    if(!q || gezien[q.v]) continue;
    gezien[q.v] = 1;
    /* v23.228: welk patroon deze vraag maakte. Zonder dit weet gramAntwoord() alleen wélk concept
       fout ging en niet wélke regel, en dan kan het doosje niet op het patroon zitten. Dezelfde
       vorm als v23.168 bij de zinnen: niet "s142 ging fout" maar "ser en estar liepen door
       elkaar". */
    q.pi = (start + ronde - 1 + c.patronen.length * 99) % c.patronen.length;
    uit.push(gcSchud(q));
  }
  return uit;
}
/* Vragen uit \\u00e9\\u00e9n patroon. De opfrisser gebruikt dit sinds v23.228: de wachtrij levert een patroon
   en niet een concept, dus de vraag hoort over dat patroon te gaan. */
function gcVragenUitPatroon(c, pi, n){
  var p = c && c.patronen && c.patronen[pi];
  if(typeof p !== "function") return [];
  var uit = [], gezien = {}, poging = 0;
  while(uit.length < n && poging < n * 25){
    poging++;
    var q = null;
    try { q = p(); } catch(e){ q = null; }
    if(!q || gezien[q.v]) continue;
    gezien[q.v] = 1;
    q.pi = pi;
    uit.push(gcSchud(q));
  }
  return uit;
}""")

    # =========================================================================================
    # 4. het antwoord geeft het patroon door
    # =========================================================================================
    rep("""  gramBij(o.concept, goed, (q && q.o) ? q.o.length : 0);
  gramLog(o.concept, gwKanaal(o), goed);""",
"""  /* v23.228: en het patroon gaat mee. Draagt de vraag er geen (dat kan bij een handgeschreven
     wizardstap), dan landt het antwoord op de kale sleutel, net als voorheen. */
  gramBij(o.concept, goed, (q && q.o) ? q.o.length : 0, (q && typeof q.pi === "number") ? q.pi : null);
  gramLog(o.concept, gwKanaal(o), goed);""")

    # =========================================================================================
    # 5. de wachtrij levert een patroon
    # =========================================================================================
    rep("""  GC_CONCEPTEN.forEach(function(c){
    if(!gramAangeraakt(c.id)) return;          // nooit gedaan is geen herhaling maar kennismaking
    try { if(!gcConceptOpen(c.id)) return; } catch(e){}
    var st = gramLees(c.id);""",
"""  /* v23.228: per DOOSJE en niet per concept. Een concept met vijf patronen levert dus hoogstens
     vijf regels, en elke regel weet welk patroon hij is. Een patroon dat je nog nooit hebt gedaan
     heeft geen doosje en staat hier dus niet: kennismaking hoort in de les, niet in de wachtrij. */
  GC_CONCEPTEN.forEach(function(c){
    try { if(!gcConceptOpen(c.id)) return; } catch(e){ return; }
    gramDoosjes(c.id).forEach(function(d){
    var st = d.st;""")
    rep("""    var open = (st.box || 0) === 0 && (st.fout || 0) > 0 && !st.half;
    if(!open && st.due && st.due > t) return;
    uit.push({c:c, st:st});
  });
  uit.sort(function(a, b){""",
"""    var open = (st.box || 0) === 0 && (st.fout || 0) > 0 && !st.half;
    if(!open && st.due && st.due > t) return;
    uit.push({c:c, pi:d.pi, st:st});
    });
  });
  uit.sort(function(a, b){""")

    # =========================================================================================
    # 6. de openstaande rekening ook per doosje
    # =========================================================================================
    rep("""function gramFoutTop(){
  var uit = [];
  GC_CONCEPTEN.forEach(function(c){
    var st = gramLees(c.id);
    if(!st.fout) return;
    if((st.box || 0) > 0) return;           // je had hem daarna weer goed: geen openstaande rekening
    uit.push({c:c, st:st});
  });""",
"""function gramFoutTop(){
  var uit = [];
  /* v23.228: per doosje. Een concept waarvan \\u00e9\\u00e9n patroon op nul staat heeft een openstaande
     rekening op dat patroon, en niet op zichzelf. */
  GC_CONCEPTEN.forEach(function(c){
    gramDoosjes(c.id).forEach(function(d){
      var st = d.st;
      if(!st.fout) return;
      if((st.box || 0) > 0) return;         // je had hem daarna weer goed: geen openstaande rekening
      uit.push({c:c, pi:d.pi, st:st});
    });
  });""")

    # =========================================================================================
    # 7. de opfrisser gaat over het patroon dat aan de beurt is
    # =========================================================================================
    rep("""function gcOpfrisId(cid){ return "opfris-" + String(cid || "").replace(/^concept-/, ""); }""",
"""/* v23.228: met een patroonindex erachter, als de wachtrij er een geeft. "opfris-genero#1" is de
   opfrisser over de Griekse val; "opfris-genero" is de oude vorm en put uit alle patronen, en die
   blijft nodig voor het doosje van de vrije zin. */
function gcOpfrisId(cid, pi){
  var kaal = String(cid || "").replace(/^(concept|opfris)-/, "").split("#")[0];
  return "opfris-" + gramSleutel(kaal, pi);
}""")
    rep("""function gcOpfrisBouw(id){
  var cid = String(id || "").replace(/^opfris-/, "");
  var c = gcConcept(cid);
  if(!c) return null;""",
"""function gcOpfrisBouw(id){
  var sleutel = String(id || "").replace(/^opfris-/, "");
  var cid = sleutel.split("#")[0];
  var pi = sleutel.indexOf("#") === -1 ? null : parseInt(sleutel.split("#")[1], 10);
  var c = gcConcept(cid);
  if(!c) return null;""")
    rep("""  var vragen = [];
  try { vragen = gcMaakVragen(c, GC_OPFRIS_VRAGEN); } catch(e){ vragen = []; }
  if(vragen.length < GC_OPFRIS_VRAGEN) return null;""",
"""  /* v23.228: uit \\u00e9\\u00e9n patroon als de wachtrij er een aanwees. Dit is de helft waar het effect
     vandaan komt: kwam je om op de Griekse val, dan krijg je de Griekse val, en niet vier keer op
     vijf iets wat je allang kunt. */
  var vragen = [];
  try {
    vragen = (pi === null || isNaN(pi))
      ? gcMaakVragen(c, GC_OPFRIS_VRAGEN)
      : gcVragenUitPatroon(c, pi, GC_OPFRIS_VRAGEN);
  } catch(e){ vragen = []; }
  if(vragen.length < GC_OPFRIS_VRAGEN) return null;""")

    # =========================================================================================
    # 8. de dagles vraagt de opfrisser van het juiste patroon
    # =========================================================================================
    rep("""      var o = null;
      try { o = gcGebouwd(gcOpfrisId(top.c.id)); } catch(e){ o = null; }
      if(o) uit.push(o.id);""",
"""      var o = null;
      try { o = gcGebouwd(gcOpfrisId(top.c.id, top.pi)); } catch(e){ o = null; }
      if(o) uit.push(o.id);""")
    rep("""  var kaal = function(x){ return String(x || "").replace(/^(opfris|concept)-/, ""); };""",
"""  /* v23.228: de patroonindex hoort ook weg bij het ontdubbelen. "opfris-genero#1" en
     "concept-genero" gaan over hetzelfde onderwerp, en twee keer genero in \\u00e9\\u00e9n les is precies wat
     v23.170 kwam repareren. */
  var kaal = function(x){ return String(x || "").replace(/^(opfris|concept)-/, "").split("#")[0]; };""")

    # =========================================================================================
    # 9. de drill blijft over het hele concept gaan
    # =========================================================================================
    rep("""function gcDrillId(cid){ return "drill-" + String(cid || "").replace(/^(concept|opfris)-/, ""); }""",
"""/* De drill blijft over het hele concept gaan, ook als je op \\u00e9\\u00e9n patroon omkwam: vijf vragen uit
   dezelfde val is drillen op vijf keer hetzelfde woord, en dan oefen je de vorm en niet de keuze. */
function gcDrillId(cid){
  return "drill-" + String(cid || "").replace(/^(concept|opfris)-/, "").split("#")[0];
}""")
    rep("""  b = document.getElementById("gwDrill");
  if(b) b.onclick = function(){ gwStart(gcDrillId(gwSess.id.replace(/^concept-/, "")), 0); };""",
"""  b = document.getElementById("gwDrill");
  if(b) b.onclick = function(){ gwStart(gcDrillId(gwSess.id), 0); };""")

    # =========================================================================================
    # 10. de omleiding naar de opfrisser kiest het zwakste doosje
    # =========================================================================================
    rep("""  var oid = null;
  try { oid = gcOpfrisId(id); } catch(e){ return null; }""",
"""  /* v23.228: het zwakste doosje van dit concept, want dat is waar de opfrisser over hoort te gaan.
     Is er nog geen enkel patroondoosje, dan de oude vorm over alle patronen. */
  var oid = null;
  try {
    var cid = String(id).replace(/^concept-/, "");
    var d = gramDoosjes(cid).slice().sort(function(a, b){
      if((a.st.box || 0) !== (b.st.box || 0)) return (a.st.box || 0) - (b.st.box || 0);
      return (a.st.due || "") < (b.st.due || "") ? -1 : 1;
    })[0];
    oid = gcOpfrisId(cid, d ? d.pi : null);
  } catch(e){ return null; }""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    for nodig in ["function gramSleutel(", "function gramRuw(", "function gramDoosjes(",
                  "function gramPatroonN(", "function gcVragenUitPatroon(",
                  "function gramBij(cid, goed, keuzes, pi)", "q.pi = (start + ronde",
                  "uit.push({c:c, pi:d.pi, st:st})", "gcOpfrisId(top.c.id, top.pi)"]:
        assert nodig in src, "ontbreekt: " + nodig
    for f in ["gramSleutel", "gramRuw", "gramDoosjes", "gramPatroonN", "gramLees", "gramBij",
              "gcVragenUitPatroon", "gcOpfrisId", "gcOpfrisBouw", "gcDrillId", "gramFoutTop",
              "gramWachtrij"]:
        n = src.count("function " + f + "(")
        assert n == 1, "%s staat %d keer in het bestand (JavaScript hijst, dus de laatste wint stil)" % (f, n)
    # de zes aanroepers buiten de microles mogen GEEN patroon meegeven: hun bewijs komt uit het
    # wild (een quiz, de tegels, een vrije zin, de Clasificador, El Corrector) en landt dus op de
    # kale sleutel. Staan ze hier niet meer, dan is er stil een zevende betekenis bijgekomen.
    for wild in ["gramBij(cid, pct >= 0.8)",
                 "gramBij(t.cid, false)",
                 "gramBij(fregel.cid, false)",
                 "gramBij(clSpel.c.id, false)",
                 "gramBij(clSpel.c.id, true)",
                 "gramBij(gcConceptVoorCorr(id), goed)"]:
        assert wild in src, "deze aanroep hoort zonder patroon te blijven: " + wild
    assert 'gramBij(o.concept, goed, (q && q.o) ? q.o.length : 0, (q && typeof q.pi === "number") ? q.pi : null)' in src, \
        "gramAntwoord geeft het patroon niet door"
    APP.write_text(src, encoding="utf-8")
    print("index.html: het doosje zit nu op het patroon, en de opfrisser vraagt het patroon dat aan de beurt is")
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
