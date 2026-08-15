#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.107: de imperfecto bestaat eindelijk als vorm, en de signaalwoorden bestaan voor het eerst.
Brok 3, 4, 5 en 9 uit het brokkenmodel.

## Wat Stefan zei

"nou 1 kan later wel, ik heb liever 2 en 3 dat we deze grammatica van begin tot einde helemaal
goed bouwen."

Dus niet de verhuizing van het meetschermpje, maar de twee brokken die er inhoudelijk niet zijn.

## Bevinding: de app kan de imperfecto helemaal niet vervoegen

Nagemeten, niet aangenomen. conjVorm() kende vier tijden:

    subjuntivo   uit VERBOS_SUBJ
    indefinido   uit VERBOS_PASADO
    perfecto     haber + participio
    presente     uit VERBOS

De imperfecto zat er niet bij, en ook niet in de elf fasen van de ladder. Terwijl de conceptkaart
je een imperfecto-tabel laat zien en er dan onder zet: "Drill de vormen in de Speeltuin en kom
hier terug zodra iets weer wiebelt." Die drill bestond niet. Stefans zoektocht ernaar was dus
terecht en zijn conclusie ("volgens mij bestaat die niet bij grammatica") klopte.

Dat dit uitgerekend de tijd is waar hij op vastloopt, is geen toeval: het is de enige verleden
tijd waarvoor de app geen enkele oefening heeft.

## Waarom dit de goedkoopste brok van de tien is

De imperfecto is volledig regelmatig op precies drie werkwoorden na, in de hele taal:

    -ar        stam + aba abas aba \u00e1bamos abais aban
    -er/-ir    stam + \u00eda \u00edas \u00eda \u00edamos \u00edais \u00edan       (en die twee zijn hier gelijk)
    ser        era eras era \u00e9ramos erais eran
    ir         iba ibas iba \u00edbamos ibais iban
    ver        ve\u00eda ve\u00edas ve\u00eda ve\u00edamos ve\u00edais ve\u00edan

Dus geen tabel van 33 werkwoorden zoals VERBOS_PASADO, maar een rekenregel en drie uitzonderingen.
Elk werkwoord dat morgen aan VERBOS wordt toegevoegd kan meteen mee, zonder dat iemand er een
vorm bij hoeft te typen. Dat is ook precies de architectuurregel van vandaag: het feit staat in de
infinitief, dus je schrijft het niet nog een keer op.

## Twee fasen erbij, en waar ze staan

Na "verleden tijd 1, compleet" en v\u00f3\u00f3r het perfecto, want dat is de volgorde van AULA 2 (indefinido
in hoofdstuk 2, imperfecto in hoofdstuk 9). Eerst alles behalve de drie, dan de drie erbij.

De imperfecto doet ook mee in de mix-fase, want die is de eindstand: niet elke vorm los kennen
maar ze uit elkaar houden.

## Brok 9: de signaalwoorden

Acht Spaanse woorden naar het bakje waar ze heen wijzen. Dit is de goedkoopste brok van het hele
model en hij bestond niet, terwijl in de helft van de zinnen het antwoord er gewoon bij staat
zodra je ze kent.

Hij komt binnen via een nieuw mechanisme: GC_VOORSTAPPEN, stappen die v\u00f3\u00f3r de patroonvragen van
een onderwerp komen. Alleen indefimperf heeft er nu \u00e9\u00e9n, met opzet: eerst bewijzen dat het klopt op
\u00e9\u00e9n onderwerp. Klopt het, dan is het voor de andere 22 data en geen code.

## En de echte verandering, in \u00e9\u00e9n regel

In gwKies() stond onvoorwaardelijk:

    if(o.concept) gramBij(o.concept, i === q.g);

Elke vraag van elke stap van elk onderwerp ging naar \u00e9\u00e9n doos per onderwerp: 23 dozen voor 122
patronen. Daardoor kan "indefimperf doos 2" vier verschillende dingen betekenen, en met \u00e9\u00e9n cijfer
houd je die niet uit elkaar. Draagt een stap nu een brok-id, dan gaat het antwoord daarheen.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.107"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.107" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ================================================= brok 3, 4, 5: de imperfecto als vorm
A_VORM = '''function conjVorm(v, p, t){
  if(t === "subjuntivo"){ var sv = VERBOS_SUBJ[v.inf]; if(sv) return sv[p]; return v.presente[p]; }
  var d = VERBOS_PASADO[v.inf];
  if(t === "indefinido" && d) return d.i[p];
  if(t === "perfecto" && d) return HABER_PRES[p] + " " + d.part;
  return v.presente[p];
}'''
N_VORM = '''/* ---- de imperfecto (v23.107, brok 3, 4 en 5) ----
   De enige tijd in het Spaans die volledig regelmatig is op precies drie werkwoorden na. Dus geen
   tabel van 33 zoals VERBOS_PASADO, maar een rekenregel en drie uitzonderingen. Elk werkwoord dat
   morgen aan VERBOS wordt toegevoegd kan meteen mee: het feit staat al in de infinitief en hoort
   dus niet nog een keer opgeschreven te worden.
   Meevaller die de moeite van het vermelden waard is en die ook in de uitleg staat: -er en -ir
   zijn hier gelijk. Dat is de enige tijd waarin dat zo is. */
var CONJ_IMPERF_UIT = {
  ar: ["aba", "abas", "aba", "\\u00e1bamos", "abais", "aban"],
  er: ["\\u00eda", "\\u00edas", "\\u00eda", "\\u00edamos", "\\u00edais", "\\u00edan"]
};
var VERBOS_IMPERF = {
  ser: ["era", "eras", "era", "\\u00e9ramos", "erais", "eran"],
  ir:  ["iba", "ibas", "iba", "\\u00edbamos", "ibais", "iban"],
  ver: ["ve\\u00eda", "ve\\u00edas", "ve\\u00eda", "ve\\u00edamos", "ve\\u00edais", "ve\\u00edan"]
};
function conjImperfecto(v, p){
  var vast = VERBOS_IMPERF[v.inf];
  if(vast) return vast[p];
  var g = conjGroep(v);
  var u = CONJ_IMPERF_UIT[g === "ar" ? "ar" : "er"];   // -er en -ir vallen hier samen
  return v.inf.slice(0, -2) + u[p];
}
function conjVorm(v, p, t){
  if(t === "subjuntivo"){ var sv = VERBOS_SUBJ[v.inf]; if(sv) return sv[p]; return v.presente[p]; }
  if(t === "imperfecto") return conjImperfecto(v, p);
  var d = VERBOS_PASADO[v.inf];
  if(t === "indefinido" && d) return d.i[p];
  if(t === "perfecto" && d) return HABER_PRES[p] + " " + d.part;
  return v.presente[p];
}'''

A_LABEL = '''function conjTiempoLabel(t){
  if(t === "subjuntivo") return "presente de subjuntivo";
  if(t === "indefinido") return "pret\\u00e9rito indefinido";
  if(t === "perfecto") return "pret\\u00e9rito perfecto";
  return "presente";
}'''
N_LABEL = '''function conjTiempoLabel(t){
  if(t === "subjuntivo") return "presente de subjuntivo";
  if(t === "indefinido") return "pret\\u00e9rito indefinido";
  if(t === "imperfecto") return "pret\\u00e9rito imperfecto";   // v23.107
  if(t === "perfecto") return "pret\\u00e9rito perfecto";
  return "presente";
}'''

A_TIEMPOS = '''var CONJ_TIEMPOS = ["presente","indefinido","perfecto","subjuntivo","mix"];'''
N_TIEMPOS = '''var CONJ_TIEMPOS = ["presente","indefinido","imperfecto","perfecto","subjuntivo","mix"];'''

A_ACTIEF = '''  var opts = ["presente","indefinido","perfecto","subjuntivo"];'''
N_ACTIEF = '''  // v23.107: de imperfecto doet mee in de mix, want die fase is de eindstand: niet elke vorm los
  // kennen maar ze uit elkaar houden. En dat is precies waar indefinido tegenover imperfecto zit.
  var opts = ["presente","indefinido","imperfecto","perfecto","subjuntivo"];'''

A_POOL = '''  var tabel = (t === "subjuntivo") ? VERBOS_SUBJ : VERBOS_PASADO;
  var pool = basis.filter(function(v){ return !!tabel[v.inf]; });
  return pool.length ? pool : basis;'''
N_POOL = '''  // v23.107: de imperfecto is voor elk werkwoord te berekenen, dus daar valt niets te filteren.
  // Zonder deze regel zou hij de pool langs VERBOS_PASADO leggen en werkwoorden weglaten die hij
  // prima aankan.
  if(t === "imperfecto") return basis;
  var tabel = (t === "subjuntivo") ? VERBOS_SUBJ : VERBOS_PASADO;
  var pool = basis.filter(function(v){ return !!tabel[v.inf]; });
  return pool.length ? pool : basis;'''

A_FASE = '''  {id:"perfecto", tijd:"perfecto", personen:[0,1,2,3,4,5], nl:"verleden tijd 2", en:"past tense 2",'''
N_FASE = '''  /* v23.107: twee fasen erbij, hier en niet eerder. AULA 2 doet het indefinido in hoofdstuk 2 en
     het imperfecto in hoofdstuk 9, en Stefan volgt AULA. Eerst alles behalve de drie
     onregelmatige, dan de drie erbij: dat zijn er precies drie in de hele taal, en dat mag je
     weten voordat je eraan begint. */
  {id:"imperfreg", tijd:"imperfecto", personen:[0,1,2,3,4,5], nl:"hoe het was", en:"how things were",
   uitNl:"Het pret\\u00e9rito imperfecto: achtergrond, gewoonte, hoe het w\\u00e1s. Volledig regelmatig, en -er en -ir zijn hier gelijk.",
   uitEn:"The pret\\u00e9rito imperfecto: background, habit, how things were. Fully regular, and -er and -ir are identical here.",
   pool:function(v){ return !VERBOS_IMPERF[v.inf]; }},
  {id:"imperf", tijd:"imperfecto", personen:[0,1,2,3,4,5], nl:"hoe het was, compleet", en:"how things were, complete",
   uitNl:"Nu met ser, ir en ver erbij. Meer onregelmatige zijn er niet in deze tijd, in de hele taal niet.",
   uitEn:"Now with ser, ir and ver added. There are no more irregulars in this tense, not in the whole language.",
   pool:function(v){ return true; }},
  {id:"perfecto", tijd:"perfecto", personen:[0,1,2,3,4,5], nl:"verleden tijd 2", en:"past tense 2",'''

# ================================================= brok 9: de signaalwoorden
A_BROKID = '''var BROK_ID = "indefimperf.betekenis";'''
N_BROKID = '''/* v23.107, brok 9: de signaalwoorden. De goedkoopste brok van het hele model, en hij bestond niet
   terwijl in de helft van de zinnen het antwoord er gewoon bij staat zodra je ze kent. */
var BROK_SIGNAAL = [
  {es:"mientras",        s:"a", w:"Mientras zet iets neer dat doorloopt terwijl er iets anders gebeurt: imperfecto.",
   wEn:"Mientras sets up something ongoing while something else happens: imperfect."},
  {es:"siempre",         s:"a", w:"Altijd, dus een gewoonte: imperfecto.", wEn:"Always, so a habit: imperfect."},
  {es:"todos los d\\u00edas", s:"a", w:"Elke dag: gewoonte, dus imperfecto.", wEn:"Every day: habit, so imperfect."},
  {es:"antes",           s:"a", w:"Vroeger, hoe het toen was: imperfecto.", wEn:"Before, how things were: imperfect."},
  {es:"ayer",            s:"g", w:"Gisteren is afgesloten: indefinido.", wEn:"Yesterday is closed off: preterite."},
  {es:"un d\\u00eda",         s:"g", w:"Op een dag kondigt een gebeurtenis aan: indefinido.", wEn:"One day announces an event: preterite."},
  {es:"de repente",      s:"g", w:"Ineens: precies \\u00e9\\u00e9n moment, dus indefinido.", wEn:"Suddenly: exactly one moment, so preterite."},
  {es:"el a\\u00f1o pasado",  s:"g", w:"Vorig jaar is een afgesloten periode: indefinido.", wEn:"Last year is a closed period: preterite."}
];
/* Een sorteervraag met twee bakjes is gewoon een meerkeuzevraag met twee opties, dus de wizard kan
   dit al. Geen tweede vraagrenderer, geen tweede plek waar hetzelfde fout kan gaan.
   De opties worden bewust niet geschud: bij sorteren horen de bakjes op hun plek te blijven staan,
   en dat is het verschil tussen sorteren en raden. */
function brokStapSignaal(n){
  return {kop:"De signaalwoorden", kopEn:"The signal words",
    brok:"indefimperf.signaal",
    uitleg:"<p>Sommige woorden verraden welke tijd erachter komt. Ken je deze acht, dan staat in de helft van de zinnen het antwoord er gewoon bij.</p>",
    uitlegEn:"<p>Some words give away which tense follows. Know these eight and half the time the answer is right there in the sentence.</p>",
    vragen:geschud(BROK_SIGNAAL.slice()).slice(0, n).map(function(z){
      return {v:z.es, vEn:z.es, o:["imperfecto","indefinido"],
              g:(z.s === "a" ? 0 : 1), w:z.w, wEn:z.wEn};
    })};
}
/* Stappen die v\\u00f3\\u00f3r de patroonvragen van een onderwerp komen. Alleen indefimperf heeft er nu een,
   met opzet: eerst bewijzen dat het brokkenmodel klopt op \\u00e9\\u00e9n onderwerp. Klopt het, dan is het voor
   de andere 22 data en geen code. */
var GC_VOORSTAPPEN = {
  indefimperf: [function(){ return brokStapSignaal(8); }]
};

var BROK_ID = "indefimperf.betekenis";'''

A_STAPPEN = '''  var stappen = [];
  // stap 1: meteen een voorbeeld. Eén regel kader, zodat niemand denkt dat hij iets gemist heeft.'''
N_STAPPEN = '''  var stappen = [];
  /* v23.107: de brokken staan vooraan. Een onderwerp is niet één ding maar een stapel dingen, en
     de patroonvragen hieronder zijn de laatste ervan, niet de eerste. */
  (GC_VOORSTAPPEN[c.id] || []).forEach(function(maak){
    try { stappen.push(maak()); } catch(e){ /* een kapotte voorstap mag het onderwerp niet slopen */ }
  });
  // stap 1: meteen een voorbeeld. Eén regel kader, zodat niemand denkt dat hij iets gemist heeft.'''

# ================================================= elke stap zijn eigen geheugen
A_KIES = '''  if(o.concept) gramBij(o.concept, i === q.g);'''
N_KIES = '''  /* v23.107, en dit is de kern. Hier stond onvoorwaardelijk gramBij(o.concept), dus elke vraag van
     elke stap van elk onderwerp ging naar één doos per onderwerp: 23 dozen voor 122 patronen.
     "indefimperf doos 2" kan daardoor vier verschillende dingen betekenen (de regel niet snappen,
     de vormen missen, alleen de onregelmatige missen, of het niet tegelijk kunnen), en met één
     cijfer houd je die niet uit elkaar.
     Draagt een stap een brok-id, dan gaat het antwoord daarheen. Anders naar het onderwerp, zoals
     altijd, zodat de bestaande boekhouding niet verandert. */
  if(stap.brok) brokBij(stap.brok, i === q.g);
  else if(o.concept) gramBij(o.concept, i === q.g);'''

A_BROKBIJ = '''function brokBij(id, goed, totaal){
  S.brok = S.brok || {};
  var st = brokLees(id);
  st.goed += goed; st.fout += (totaal - goed);
  st.beste = Math.max(st.beste || 0, goed);
  st.laatst = today(); st.rondes = (st.rondes || 0) + 1;
  S.brok[id] = st;
  persist();
}'''
N_BROKBIJ = '''/* v23.107: er zijn nu twee aanroepers met een verschillend ritme. Het losse schermpje scoort per
   ronde, de wizard per vraag. Dus twee ingangen op dezelfde pot, en persist() blijft bij de
   aanroeper: gwKies() doet dat toch al na elk antwoord. */
function brokBij(id, goed){
  S.brok = S.brok || {};
  var st = brokLees(id);
  if(goed) st.goed++; else st.fout++;
  st.laatst = today();
  S.brok[id] = st;
}
function brokRonde(id, goed, totaal){
  S.brok = S.brok || {};
  var st = brokLees(id);
  st.goed += goed; st.fout += (totaal - goed);
  st.beste = Math.max(st.beste || 0, goed);
  st.laatst = today(); st.rondes = (st.rondes || 0) + 1;
  S.brok[id] = st;
  persist();
}'''

A_ROND = '''  if(brokSpel.i >= brokSpel.rij.length) brokBij(BROK_ID, brokSpel.goed, brokSpel.rij.length);'''
N_ROND = '''  if(brokSpel.i >= brokSpel.rij.length) brokRonde(BROK_ID, brokSpel.goed, brokSpel.rij.length);'''

# ================================================= de ontgrendeling mag niemand terugzetten
# Stefan staat op fase 10 van 11 (de subjuntivo). S.conjOpen is een index in CONJ_FASES, en er
# komen in deze versie twee fasen tussen. Zonder vertaling wijst index 9 ineens "imperf" aan in
# plaats van "subjuntivo" en is hij drie fasen kwijt. conjOpenInit zegt daar zelf over: "Een update
# die je terugzet naar af is precies zo'n reden om te stoppen."
#
# Eerst geprobeerd: de ontgrendeling als id opslaan in plaats van als getal. Structureel netter,
# maar dertien checks in pw-conjfase vielen om omdat een half dozijn plekken S.conjOpen als getal
# zetten en lezen. Een opslagmodel omgooien op het moment dat je ook nieuwe fasen toevoegt, is twee
# dingen tegelijk. Dus nu de kleine ingreep: het getal blijft, maar wordt één keer vertaald langs de
# oude volgorde. Verandert de ladder ooit weer, dan komt er een regel bij, en dat is zichtbaar werk
# in plaats van stille schade.
A_OPENINIT = """function conjOpenInit(){
  if(typeof S.conjOpen === "number") return S.conjOpen;
  var open = 0, geoefend = false;"""
N_OPENINIT = """/* v23.107: de volgorde van de ladder vóór deze versie. Staat hier omdat hij nergens anders meer
   te vinden is, en dit is de enige plek die hem nog nodig heeft. */
var CONJ_FASES_OUD11 = ["ar","er","ir","seis","onreg","presente","indefreg","indef","perfecto","subjuntivo","mix"];
var CONJ_LADDER_NU = 13;
function conjLadderMigratie(){
  if(S.conjLadder === CONJ_LADDER_NU) return;
  if(typeof S.conjOpen === "number"){
    var oudId = CONJ_FASES_OUD11[S.conjOpen];
    var n = oudId ? conjFaseIdx(oudId) : -1;
    if(n >= 0) S.conjOpen = n;
  }
  S.conjLadder = CONJ_LADDER_NU;
  try { persist(); } catch(e){}
}
function conjOpenInit(){
  conjLadderMigratie();
  if(typeof S.conjOpen === "number") return S.conjOpen;
  var open = 0, geoefend = false;"""

A_DOORSTEEK = """    var fid = drill === "indefinido" ? "indef" : (drill === "perfecto" ? "perfecto" :
              (drill === "subjuntivo" ? "subjuntivo" : "presente"));"""
N_DOORSTEEK = """    // v23.107: imperfecto erbij. Zonder deze regel belooft de knop een tijd en land je in het
    // presente, en dat is precies waarvoor deze doorsteek ooit gebouwd is.
    var fid = drill === "indefinido" ? "indef" : (drill === "perfecto" ? "perfecto" :
              (drill === "subjuntivo" ? "subjuntivo" :
              (drill === "imperfecto" ? "imperf" : "presente")));"""

# o.drill zet de knop "Naar de Conjugador" op het slotscherm van de wizard. Vijf handgeschreven
# wizards hebben dat veld, alle 23 concepten niet, dus vanuit een conceptkaart was er nooit een
# doorsteek naar de vormdrill. Dat is precies de knop die Stefan zocht toen er "drill de vormen in
# de Speeltuin" stond zonder link. De emoji staat als echt teken in index.html, dus daar niet op
# ankeren.
A_CONCEPT = """  corr:[], spiek:{a2:[14,15,16,26]}, wizard:null,"""
N_CONCEPT = """  corr:[], spiek:{a2:[14,15,16,26]}, wizard:null, drill:"imperfecto","""

A_RETURN = """  return {id:"concept-" + c.id, concept:c.id, icon:c.icon,"""
N_RETURN = """  // v23.107: drill gaat mee, zodat een concept net als een handgeschreven wizard een knop naar de
  // vormdrill kan hebben. Zonder dit veld bestond die doorsteek alleen op papier.
  return {id:"concept-" + c.id, concept:c.id, icon:c.icon, drill:c.drill || null,"""


if DOE_APP:
    ontbreekt = [n for n, a in (
        ("conjVorm", A_VORM), ("conjTiempoLabel", A_LABEL), ("CONJ_TIEMPOS", A_TIEMPOS),
        ("de mix-tijden", A_ACTIEF), ("de werkwoordpool", A_POOL), ("de perfecto-fase", A_FASE),
        ("BROK_ID", A_BROKID), ("de stappen van gcBouw", A_STAPPEN),
        ("de scoreregel van gwKies", A_KIES), ("brokBij", A_BROKBIJ),
        ("de rondeafsluiting", A_ROND), ("conjOpenInit", A_OPENINIT),
        ("de doorsteek naar de Conjugador", A_DOORSTEEK), ("het concept indefimperf", A_CONCEPT),
        ("de teruggave van gcBouw", A_RETURN)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.106. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_VORM, N_VORM)
    rep(A_LABEL, N_LABEL)
    rep(A_TIEMPOS, N_TIEMPOS)
    rep(A_ACTIEF, N_ACTIEF)
    rep(A_POOL, N_POOL)
    rep(A_FASE, N_FASE)
    rep(A_BROKID, N_BROKID)
    rep(A_STAPPEN, N_STAPPEN)
    rep(A_KIES, N_KIES)
    rep(A_BROKBIJ, N_BROKBIJ)
    rep(A_ROND, N_ROND)
    rep(A_OPENINIT, N_OPENINIT)
    rep(A_DOORSTEEK, N_DOORSTEEK)
    rep(A_CONCEPT, N_CONCEPT)
    rep(A_RETURN, N_RETURN)

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
