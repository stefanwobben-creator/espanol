#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.43: de poort van dag 1 gaat weer dicht.

Wat er mis was, in een zin: de coulanceregel die bestaande spelers hun spellen laat houden, gold
per ongeluk ook voor iedere vreemde die net binnenkwam.

speelOoitInit() doet dit:

    if(Object.keys(S.srs || {}).length > 0){ for(var k in SPEEL_EIS) S.speelOoit[k] = true; }

De bedoeling is goed: wie al aan het oefenen was, raakt door een update niets kwijt. Maar het
proefscherm ("hola, wat betekent dit") zet drie woorden in S.srs voordat er een profiel bestaat,
en boot() verzilvert die drie meteen in het verse profiel. Dus staat er bij elke nieuwe bezoeker
iets in S.srs op het moment dat speelOoitInit() voor het eerst kijkt, en gaan alle acht sloten
open. SPEEL_EIS deed vanaf v19.92 dus niets meer voor precies de groep waarvoor hij bedoeld was.

Gemeten op een vers A0-profiel (3 woorden geleerd), dag 1, telefoonformaat:

    Clasificador   eis 25 woorden   opende op "Todos los días ___ con mi abuela" (indefinido of
                                    imperfecto), minuut een
    Crucigrama     eis 12 woorden   kaatste terug naar de speeltuin met de toast
                                    "Leer eerst wat meer woordjes voor een kruiswoord!"
    El Corrector   eis 8 zinnen     opende met 5 vrijgespeelde zinnen

Dat is precies de knop die v19.92 wilde uitroeien: hij belooft iets en levert een toast.

## De reparatie, twee delen

**1. Een vers profiel begint met een lege speelOoit.**

Eén regel in boot(), naast de twee regels die daar al staan om een vers profiel te herkennen
(S.gestart en niveauClaim). Allebei gebruiken ze !(S.txp > 0), en allebei staan ze boven het blok
dat de proef verzilvert, dus vóór de proef-XP binnenkomt. Deze regel komt daar tussen.

Wie al bezig was (txp > 0) heeft geen S.speelOoit en valt gewoon nog onder de oude coulanceregel.
Er raakt dus niemand iets kwijt; de regel geldt alleen niet meer voor mensen die nog nooit iets
gedaan hebben.

**2. De eis telt voortaan wat het spel echt nodig heeft.**

De eis stond op "aantal geleerde woorden", en dat getal zegt voor een woordenzoeker en een
kruiswoord niets. Die hebben letters nodig die in een raster passen, en wsWoordPool() gooit alles
weg wat uit meer dan een woord bestaat. De eerste dertien woorden van A0 zijn:

    hola · adiós · gracias · por favor · sí/no · buenos días · buenas noches · hasta mañana ·
    me llamo... · ¿cómo estás? · uno,dos,tres,cuatro,cinco · seis,siete,acht,negen,tien · ¿dónde?

Daarvan overleven er drie. Gemeten met kruisBouw(), vijf pogingen per stand: tot en met dertien
geleerde woorden 0 van de 5 geslaagd, vanaf veertien (el hombre, la mujer, el niño) 5 van de 5.
De oude eis van 12 woorden liet het kruiswoord dus open op een moment dat hij aantoonbaar niet
kon bouwen, ook zonder de coulancebug.

Daarom telt de eis nu de voorraad die de bouwer in handen krijgt in plaats van je woordenteller:

    ws      wsWoordPool() >= 4          precies de drempel die wsStart() zelf hanteert
    kruis   idem, lengte 4 t/m 8, >= 4  precies de drempel die kruisBouw() zelf hanteert
    mem     4 geleerde woorden          precies de drempel die memStart() zelf hanteert

Het getal in het slot is nu hetzelfde getal waarop het spel zelf afslaat. Daarmee is "de tegel
verschijnt zodra het spel kan draaien" geen belofte meer maar een gevolg.

De vier overige eisen blijven staan: letras (10), adiv (15), audi (20), clas (25) en corr (8
zinnen) zijn niveaudrempels en geen materiaaldrempels. Adivina en Letras putten uit de hele bak en
kunnen dus altijd bouwen; hun eis zegt "hier ben je nog niet aan toe", en dat is een ander soort
uitspraak dan "hier is niet genoeg van".

## Wat een vreemde nu ziet

    dag 1, na de proef (3 woorden)    Aventura, Rompecabezas
    dag 1, na de eerste les (8)       Aventura, Rompecabezas, Memory
    rond woord 14                     Woordenzoeker en Crucigrama komen erbij

Idempotent. Twee keer draaien mag niets stukmaken.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.43"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

# "Al gedaan" en "hier valt niets te doen" zijn niet hetzelfde. Eerst kijken of dit bestand is wat
# we denken dat het is; pas daarna of het werk al gedaan is.
ANKER_BOOT = '  if(!S.gestart && !(S.txp > 0)) S.gestart = today();'
ANKER_EIS = 'var SPEEL_EIS = {'
if ANKER_BOOT not in src or ANKER_EIS not in src:
    print("Deze index.html ziet er niet uit zoals verwacht: het boot-anker of SPEEL_EIS ontbreekt.\n"
          "Eerst bijtrekken, dan pas patchen:\n\n    git pull --rebase\n")
    sys.exit(1)

DOE_APP = "function speelRasterN()" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. versie ----------
    rep('var APP_VERSIE = "%s";' % huidig_ver, 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 2. een vers profiel begint met een lege speelOoit ----------
    rep(ANKER_BOOT,
        ANKER_BOOT + "\n"
        "  /* v23.43: en een vers profiel begint met een lege spellenlijst. speelOoitInit() geeft\n"
        "     iedereen met iets in S.srs al zijn spellen cadeau (de coulanceregel van v19.92), maar\n"
        "     het proefscherm zet drie woorden in S.srs voordat dit profiel bestond. Zonder deze\n"
        "     regel valt dus elke nieuwe bezoeker onder de coulance en doet SPEEL_EIS niets. Staat\n"
        "     hier bewust boven het blok dat de proef verzilvert: daaronder is S.txp niet meer nul.\n"
        "     Wie al bezig was (txp > 0) heeft geen S.speelOoit en houdt de oude regel, dus er raakt\n"
        "     niemand iets kwijt. */\n"
        "  if(!S.speelOoit && !(S.txp > 0)) S.speelOoit = {};")

    # ---------- 3. de eis telt wat het spel nodig heeft ----------
    OUD_EIS = """var SPEEL_EIS = {
  ws:      {soort:"w", n:12},
  audi:    {soort:"w", n:20},
  clas:    {soort:"w", n:25},
  letras:  {soort:"w", n:10},
  adiv:    {soort:"w", n:15},
  kruis:   {soort:"w", n:12},
  mem:     {soort:"w", n:12},
  corr:    {soort:"z", n:8}
};
function speelWoordN(){ try { return Object.keys(S.srs || {}).length; } catch(e){ return 999; } }
function speelZinN(){ try { return allowedSentIds().length; } catch(e){ return 999; } }"""

    NIEUW_EIS = """/* v23.43. De eis stond op "aantal geleerde woorden", en voor drie van de acht spellen zegt dat
   getal niets. Een woordenzoeker en een kruiswoord hebben geen woorden nodig maar letters die in
   een raster passen, en wsWoordPool() gooit alles weg wat uit meer dan een woord bestaat. De
   eerste dertien woorden van A0 zijn begroetingen en uitdrukkingen (por favor, buenos días,
   hasta mañana, ¿cómo estás?, uno dos tres); daarvan overleven er drie. Gemeten: kruisBouw()
   faalt tot en met dertien geleerde woorden vijf van de vijf keer, en slaagt vanaf veertien.
   De eis van 12 liet het kruiswoord dus open op een moment dat hij niet kon bouwen.

   Nu telt de eis de voorraad die de bouwer in handen krijgt, en staat hij op precies het getal
   waarop het spel zelf afslaat. Daarmee is "de tegel verschijnt zodra het spel kan draaien" geen
   belofte meer maar een gevolg.

   De andere vijf blijven op je woordenteller staan, en dat is geen slordigheid: letras, adiv,
   audi, clas en corr kunnen altijd bouwen. Hun eis zegt "hier ben je nog niet aan toe", en dat is
   een andere uitspraak dan "hier is niet genoeg van". */
var SPEEL_EIS = {
  ws:      {soort:"raster", n:4},
  kruis:   {soort:"kruis",  n:4},
  mem:     {soort:"w",      n:4},
  letras:  {soort:"w",      n:10},
  adiv:    {soort:"w",      n:15},
  audi:    {soort:"w",      n:20},
  clas:    {soort:"w",      n:25},
  corr:    {soort:"z",      n:8}
};
function speelWoordN(){ try { return Object.keys(S.srs || {}).length; } catch(e){ return 999; } }
function speelZinN(){ try { return allowedSentIds().length; } catch(e){ return 999; } }
// Dezelfde vijver waar wsStart() uit put, en dezelfde drempel (4) die hij zelf hanteert.
function speelRasterN(){ try { return wsWoordPool().length; } catch(e){ return 999; } }
// kruisBouw() houdt daar nog een lengtefilter op aan, dus die telt hier ook mee.
function speelKruisN(){
  try {
    return wsWoordPool().filter(function(k){ return k.woord.length >= 4 && k.woord.length <= 8; }).length;
  } catch(e){ return 999; }
}
function speelTelN(soort){
  if(soort === "z") return speelZinN();
  if(soort === "raster") return speelRasterN();
  if(soort === "kruis") return speelKruisN();
  return speelWoordN();
}"""
    rep(OUD_EIS, NIEUW_EIS)

    OUD_KLAAR = """  return (SPEEL_EIS[v].soort === "w" ? speelWoordN() : speelZinN()) >= SPEEL_EIS[v].n;"""
    rep(OUD_KLAAR, """  return speelTelN(SPEEL_EIS[v].soort) >= SPEEL_EIS[v].n;""")

    OUD_WACHT = """function speelWacht(v){
  var eis = SPEEL_EIS[v];
  if(!eis) return "";
  var nu = eis.soort === "w" ? speelWoordN() : speelZinN();
  return eis.soort === "w"
    ? ct("doet mee vanaf "+eis.n+" geleerde woordjes · nu "+nu,
         "joins in from "+eis.n+" learned words · now "+nu)
    : ct("doet mee vanaf "+eis.n+" vrijgespeelde zinnen · nu "+nu,
         "joins in from "+eis.n+" unlocked sentences · now "+nu);
}"""
    NIEUW_WACHT = """function speelWacht(v){
  var eis = SPEEL_EIS[v];
  if(!eis) return "";
  var nu = speelTelN(eis.soort);
  if(eis.soort === "z"){
    return ct("doet mee vanaf "+eis.n+" vrijgespeelde zinnen · nu "+nu,
              "joins in from "+eis.n+" unlocked sentences · now "+nu);
  }
  // "woorden die in een raster passen" en niet "geleerde woorden": anders staat er straks
  // "vanaf 4 woorden · nu 13" en dat is de soort regel waar je de app niet meer op vertrouwt.
  if(eis.soort === "raster" || eis.soort === "kruis"){
    return ct("doet mee vanaf "+eis.n+" woorden die in een raster passen · nu "+nu,
              "joins in from "+eis.n+" words that fit in a grid · now "+nu);
  }
  return ct("doet mee vanaf "+eis.n+" geleerde woordjes · nu "+nu,
            "joins in from "+eis.n+" learned words · now "+nu);
}"""
    rep(OUD_WACHT, NIEUW_WACHT)

    # ---------- 4. drie dagknoppen, en drie verschillende ----------
    # Pas zichtbaar geworden doordat de eis eindelijk bijt. dagSpelKeuze() liep met een stap van 2
    # door de lijst speelbare spellen; bij een lijst van twee komt (h+0), (h+2), (h+4) drie keer op
    # dezelfde uit. Zolang er negen spellen open stonden viel dat nooit op. Op dag 1 met twee
    # speelbare spellen stond er twee keer Rompecabezas, en het spel dat wel kon (Memory) niet.
    OUD_KEUZE = """  var h = dayHash("spel");
  var uit = [];
  for(var i = 0; i < 3 && i < kan.length; i++) uit.push(kan[(h + i * 2) % kan.length]);
  return uit;"""
    NIEUW_KEUZE = """  var h = dayHash("spel");
  var uit = [];
  // De stap van 2 geeft de afwisseling per dag zolang de lijst lang genoeg is; de tweede ronde
  // met stap 1 vult aan als die stap in zichzelf terugvalt. Zonder die tweede ronde stond er op
  // dag 1 twee keer hetzelfde spel, en ontbrak het spel dat wel kon.
  for(var i = 0; i < kan.length && uit.length < 3; i++){
    var k1 = kan[(h + i * 2) % kan.length];
    if(uit.indexOf(k1) === -1) uit.push(k1);
  }
  for(var j = 0; j < kan.length && uit.length < 3; j++){
    var k2 = kan[(h + j) % kan.length];
    if(uit.indexOf(k2) === -1) uit.push(k2);
  }
  return uit;"""
    rep(OUD_KEUZE, NIEUW_KEUZE)

    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

# Een handpatch moet zelf aan versie.txt denken (DEPLOY.md). Eigen vlag, want dit is een tweede
# bestand: "index.html was al klaar" zegt niets over versie.txt.
if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
