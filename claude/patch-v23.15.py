#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.15: de Cervantes-brug.

Waarom. De balk van Stefan stond op A2 met noemer 409, terwijl de app maar 55 van die sleutels in
huis had. Die balk kon dus nooit boven de 14 procent komen, hoe goed je ook oefende, en de "nog niet
gezien" eronder telde 348 woorden die de app helemaal niet kent. Tegelijk liep hij leeg: 36
ontgrendelde woorden over van de 794.

Wat er nu gebeurt. Uit het Plan Curricular van het Instituto Cervantes (de inventarissen Nociones
generales en Nociones especificas, A1 tot en met C2) komt de volledige lijst sleutels per niveau. Uit
diezelfde bron komt per sleutel het thema. De Nederlandse vertaling komt uit FREQ, de frequentielijst
die al in het bestand stond en tot nu toe alleen de zoekfunctie en het lettersspel voedde.

De richting is met opzet deze en niet andersom. FREQ bevat woordvormen ("vamos", "tengo", "esta"),
Cervantes bevat lemma's. FREQ aflopen en de vormen tegen Cervantes aanhouden levert onzin op: "la"
werd zo B2 (het staat in de rubriek muziek), "un" werd A2 en "vamos" B1. Andersom is het veilig: we
beginnen bij een Cervantes-lemma, waarvan niveau en thema per definitie kloppen, en zoeken daar een
vertaling bij op. Wat geen vertaling heeft, komt er niet in.

Dat levert 1376 kaarten op. A2 gaat daarmee van 55 naar 253 van de 403 sleutels waar de app iets
voor heeft, dus van 14 naar 63 procent. En de noemers komen nu uit dezelfde regel als de sleutels,
in plaats van uit een andere telling: dat was de laatste plek waar twee sommen over hetzelfde getal
naast elkaar stonden.

Idempotent: draait hij twee keer, dan doet de tweede keer niets.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")
HIER = os.path.dirname(os.path.abspath(__file__))

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "var C_WORDS" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


def lees(naam):
    with io.open(os.path.join(HIER, naam), encoding="utf-8") as f:
        return f.read().strip()


KEYNIV = lees("cervantes-keyniv.txt")
CWORDS = lees("cervantes-cwords.js")

# ---------------------------------------------------------------- 1. de volledige sleutellijst
oud_i = src.index('var PCIC_KEYNIV_RAW = "')
oud_j = src.index('";', oud_i) + 2
src = src[:oud_i] + 'var PCIC_KEYNIV_RAW = "' + KEYNIV + '";' + src[oud_j:]

# ---------------------------------------------------------------- 2. noemers uit dezelfde regel
rep(
    'var PCIC_NOEMER = {"A1": 390, "A2": 409, "B1": 828, "B2": 1485, "C1": 1665, "C2": 1973};',
    '/* v23.15: deze zes getallen komen nu uit dezelfde uitpakregel als PCIC_KEYNIV_RAW hierboven.\n'
    '   Ze kwamen daarvoor ergens anders vandaan, en dat is precies hoe je twee sommen over hetzelfde\n'
    '   getal krijgt: de teller telde sleutels die de app kende, de noemer telde iets anders. */\n'
    'var PCIC_NOEMER = {"A1": 409, "A2": 403, "B1": 899, "B2": 1557, "C1": 1735, "C2": 1998};')

# ---------------------------------------------------------------- 3. de kaarten zelf
rep(
    "var TRACKS = {",
    "/* ================= DE CERVANTES-WOORDEN (v23.15) =================\n"
    "   Gegenereerd, niet met de hand geschreven. Per kaart: het lemma zoals het Cervantes het\n"
    "   opschrijft (sl), de Nederlandse vertaling uit FREQ, en het thema uit de rubriek waar\n"
    "   Cervantes het woord onderbrengt. Het niveau staat niet in de kaart maar volgt uit sl via\n"
    "   pcicNiv(), want anders zou het op twee plekken staan en dan lopen ze een keer uit elkaar.\n"
    "   Deze woorden hebben geen voorbeeldzin en geen audio. Dat mag: een kaart met een woord en\n"
    "   een vertaling is nog steeds een kaart, en de 431 woorden die Stefan in doos 3 heeft staan\n"
    "   bewijzen dat herhalen ook zonder die extra's werkt. */\n"
    + CWORDS + "\n\nvar TRACKS = {")

# ---------------------------------------------------------------- 4. ze horen bij elke track
rep(
    """    WORDS = tr.words.concat(B_WORDS).concat(K_WORDS);""",
    """    WORDS = tr.words.concat(B_WORDS).concat(K_WORDS).concat(C_WORDS);""")
rep(
    """    WORDS = tr.words.concat(K_WORDS); SENTENCES = tr.sentences; QUIZZES = tr.quizzes;""",
    """    WORDS = tr.words.concat(K_WORDS).concat(C_WORDS); SENTENCES = tr.sentences; QUIZZES = tr.quizzes;""")

# ---------------------------------------------------------------- 5. hun sleutel in de mapping
rep(
    """function pcicMap(){
  if(_pcicMap) return _pcicMap;
  _pcicMap = {};
  PCIC_IDMAP_RAW.split("|").forEach(function(r){
    var p = r.split(" ");
    _pcicMap[p[0]] = p.slice(1);
  });
  return _pcicMap;
}""",
    """function pcicMap(){
  if(_pcicMap) return _pcicMap;
  _pcicMap = {};
  PCIC_IDMAP_RAW.split("|").forEach(function(r){
    var p = r.split(" ");
    _pcicMap[p[0]] = p.slice(1);
  });
  /* v23.15: de Cervantes-woorden dragen hun sleutel zelf mee, dus die hoeven niet nog een keer in
     PCIC_IDMAP_RAW te staan. Een woord dat uit een sleutel is gemaakt en daarna los in een lijst
     met sleutels wordt herhaald, is twee bronnen voor hetzelfde feit. */
  if(typeof C_WORDS !== "undefined"){
    for(var i = 0; i < C_WORDS.length; i++) _pcicMap[C_WORDS[i].id] = [C_WORDS[i].sl];
  }
  return _pcicMap;
}""")

# ---------------------------------------------------------------- 6. altijd open, net als de kernwoorden
rep(
    """  // v19.84: de A1-kernwoorden hangen aan geen enkele les, dus er is niets om te
  // ontgrendelen. Ze staan altijd open; de volgorde regelt de dagportie.
  out = out.concat(K_WORDS.map(function(w){ return w.id; }));
  return out;""",
    """  // v19.84: de A1-kernwoorden hangen aan geen enkele les, dus er is niets om te
  // ontgrendelen. Ze staan altijd open; de volgorde regelt de dagportie.
  out = out.concat(K_WORDS.map(function(w){ return w.id; }));
  /* v23.15: hetzelfde geldt voor de Cervantes-woorden. Ze hangen aan geen les, dus er valt niets
     te ontgrendelen, en de poort in dagPortie() regelt al dat je alleen woorden van jouw niveau
     krijgt plus precies een van erboven. Zonder deze regel liggen ze er wel maar komen ze nooit
     langs, en dan is de plank nog steeds leeg. */
  if(typeof C_WORDS !== "undefined") out = out.concat(C_WORDS.map(function(w){ return w.id; }));
  return out;""")

# ---------------------------------------------------------------- 6b. het woordenboek blijft snel
# WORDS gaat van 794 naar 2170, en renderDic liep drie keer per toetsaanslag over de hele lijst:
# een keer voor de zoekresultaten en een keer voor de kopregel ("x woorden uit je lessen"). Die
# kopregel staat er alleen als je NIET aan het zoeken bent, dus tijdens het typen werd hij berekend
# en weggegooid. Renderen ging daardoor van 19 naar 54 ms per aanslag, en dat is precies het soort
# vertraging dat je voelt maar niet kunt aanwijzen. Nu wordt hij berekend wanneer hij gebruikt wordt.
rep(
    """  var zichtbaar = dicZichtbareWoorden();
  var alleGroepen = dicGroups(zichtbaar);
  var geleerd = 0;
  alleGroepen.forEach(function(g){ if(g.items.some(function(it){ return S.srs[it.id]; })) geleerd++; });
  var q = stripAcc(dicZoek.toLowerCase());""",
    """  var zichtbaar = dicZichtbareWoorden();
  var q = stripAcc(dicZoek.toLowerCase());
  var alleGroepen = null, geleerd = 0;
  if(!q){
    alleGroepen = dicGroups(zichtbaar);
    alleGroepen.forEach(function(g){ if(g.items.some(function(it){ return S.srs[it.id]; })) geleerd++; });
  }""")

# ---------------------------------------------------------------- 7. versie
rep('var APP_VERSIE = "v23.14";', 'var APP_VERSIE = "v23.15";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.15 toegepast op", PAD)
