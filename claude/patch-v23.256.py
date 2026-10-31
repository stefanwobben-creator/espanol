# patch-v23.256.py - de grammaticakaart: je ziet waar je staat, en je mag zelf kiezen.
#
# WAT ER GEMETEN IS
#
# GC_ORDE heeft 31 onderwerpen en GC_VENSTER staat op 3. Nieuwe onderwerpen gaan dus strikt op
# volgorde open, drie tegelijk. indefimperf (indefinido of imperfecto) staat op plek 30 van 31.
#
# Stefan: "ik zit bijna al op a2 niveau dus ik moet het nu hebben over werkwoorden, verleden tijd
# enzo en dat oefenen en onthouden (...) nu heb ik gevoel dat ik vastloop en hier doorheen moet
# breken."
#
# Hij heeft gelijk en het is geen gevoel: met het venster van drie kan hij dat onderwerp dit jaar
# niet bereiken. En het is ook niet nodig, want de echte voorwaarden staan los in GC_VOOR, en daar
# staan er maar vijf van. 26 van de 31 onderwerpen hebben helemaal geen voorwaarde. Het venster is
# geen pedagogiek maar een rem tegen "overal een beetje, nergens iets af" (v23.234).
#
# Stefan, over wat het leerpad moet zijn: "doel is het meest efficiente leerpad, als dat is zelf
# kiezen want ik weet waar ik moeite heb dan is dat goed, maar als je gewoon een pad aanbiedt omdat
# het ene voortbouwt op het ander is dat ook goed."
#
# Allebei dus. Het pad blijft staan en blijft adviseren; de rem mag je zelf loslaten.
#
# WAT DEZE PATCH DOET
#
#   1. ZELF KIEZEN. Een onderwerp dat alleen op een plek in het venster wacht, krijgt een knop
#      "Nu doen". Daarmee gaat het open en springt het vooraan in de focus. Wat NIET wijkt: een
#      echte voorwaarde uit GC_VOOR (vijf stuks) en de vormladder (gcRouteOpen, v23.248). Je kunt
#      de keuze tussen twee verleden tijden niet kiezen voordat je de vormen hebt gehad; dat is
#      precies de fout die v23.248 repareerde en die blijft gerepareerd.
#   2. DE KAART. Boven de route een balk met vier getallen: beheerst, in onderhoud, bezig, nog te
#      gaan. Niet een percentage maar aantallen, want 31 onderwerpen zijn te tellen.
#
# Niemiec, Sikorski en Walberg (1996) over keuzevrijheid in leersystemen, en Ryan en Deci over
# autonomie: eigen regie werkt, zolang het systeem blijft adviseren. Het advies blijft dus staan.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "gcKeuzeSet" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


# ---------------------------------------------------------------- 1. zelf kiezen

KEUZE = '''/* ================= ZELF KIEZEN (v23.256) =================

   Het venster (GC_VENSTER) laat drie nieuwe onderwerpen tegelijk open, op volgorde van GC_ORDE.
   Dat is de rem van v23.234 tegen overal een beetje en nergens iets af, en die rem is goed. Maar
   hij is ook een plafond: indefimperf staat op plek 30 van 31, en dat is precies het onderwerp
   waar Stefan nu aan toe is.

   Een gekozen onderwerp gaat langs het venster heen. Het gaat NIET langs GC_VOOR (de vijf echte
   voorwaarden) en niet langs gcRouteOpen (de vormladder): die twee zeggen dat je iets nog niet
   kunt weten, en dat is geen rem maar een feit. Het venster zegt alleen dat je niet te veel
   tegelijk moet willen, en daar mag jij over gaan.

   Een gekozen onderwerp verbruikt geen vensterplek: anders zou kiezen een ander onderwerp dicht
   duwen, en dan is het geen keuze maar een ruil die je niet gevraagd hebt. */
function gcKeuzeSet(){
  var uit = {};
  try { (S.gcKeuze || []).forEach(function(id){ uit[id] = 1; }); } catch(e){}
  return uit;
}
/* Waar staat dit onderwerp op slot? Drie antwoorden, en ze zijn niet hetzelfde:
   "voorwaarde" = GC_VOOR, "vormen" = de ladder, "venster" = er is alleen geen plek. Alleen bij
   dat laatste mag je zelf kiezen. */
function gcSlotSoort(id){
  id = String(id || "").replace(/^concept-/, "");
  if(gcConceptOpen(id)) return "";
  if(!gcRouteOpen(id)) return "vormen";
  if(!gcVoorOk(id)) return "voorwaarde";
  return "venster";
}
function gcKiesbaar(id){ return gcSlotSoort(id) === "venster"; }
/* Kiezen zet het onderwerp vooraan in de focus. Zonder dat is de knop een loze knop: het onderwerp
   staat dan wel open, maar gcFocus() vult op volgorde van GC_ORDE en plek 30 komt nooit aan de
   beurt. GC_FOCUS_N blijft gelden, dus wat je kiest duwt het achterste eruit. Twee onderhanden
   blijft twee onderhanden. */
function gcKiesOnderwerp(id){
  id = String(id || "").replace(/^concept-/, "");
  if(!gcKiesbaar(id)) return;
  try {
    var k = (S.gcKeuze || []).slice();
    if(k.indexOf(id) === -1) k.push(id);
    S.gcKeuze = k;
    var f = (S.gramFocus || []).filter(function(x){ return x !== id; });
    f.unshift(id);
    S.gramFocus = f.slice(0, GC_FOCUS_N);
    persist();
  } catch(e){}
}

'''

rep("function gcOpenSet(){", KEUZE + "function gcOpenSet(){")

OUD_OPEN = """function gcOpenSet(){
  var open = {}, nieuw = 0;
  GC_ORDE.forEach(function(id){"""
NIEUW_OPEN = """function gcOpenSet(){
  var open = {}, nieuw = 0, keuze = gcKeuzeSet();
  GC_ORDE.forEach(function(id){"""
rep(OUD_OPEN, NIEUW_OPEN)

OUD_VENSTER = """    if(((st.goed || 0) + (st.fout || 0)) > 0){ open[id] = 1; return; }
    if(nieuw >= GC_VENSTER) return;
    // een onderwerp dat op zijn voorganger wacht slaat zijn beurt over en verbruikt geen plek:
    // anders zou het venster op dag 1 half leeg staan (concordancia en hayestar wachten allebei)
    if(!gcVoorOk(id)) return;
    open[id] = 1; nieuw++;"""
NIEUW_VENSTER = """    if(((st.goed || 0) + (st.fout || 0)) > 0){ open[id] = 1; return; }
    // een onderwerp dat op zijn voorganger wacht slaat zijn beurt over en verbruikt geen plek:
    // anders zou het venster op dag 1 half leeg staan (concordancia en hayestar wachten allebei)
    // v23.256: deze regel staat nu vóór het venster in plaats van erna. Dat verandert niets aan de
    // uitkomst (hij sloeg de plek toch al over), maar de gekozen onderwerpen hieronder moeten er
    // ook langs, en een voorwaarde overslaan omdat je zelf koos is precies wat niet mag.
    if(!gcVoorOk(id)) return;
    if(keuze[id]){ open[id] = 1; return; }
    if(nieuw >= GC_VENSTER) return;
    open[id] = 1; nieuw++;"""
rep(OUD_VENSTER, NIEUW_VENSTER)

# ---------------------------------------------------------------- 2. de kaart

KAART = '''/* De kaart boven de route (v23.256). Vier getallen die samen 31 zijn, en een balk die laat zien
   hoe die 31 verdeeld staan. Geen percentage: 31 onderwerpen zijn te tellen, en "23 procent" zegt
   minder dan "7 beheerst".

   De grenzen komen uit de dozen die er al zijn: doos 4 en 5 staan op 21 en 55 dagen, en wat zo ver
   uit elkaar terugkomt is beheerst. Doos 3 (8 dagen) is onderhoud, en dat is ook precies de grens
   waarop een onderwerp de focus verlaat (GC_FOCUS_KLAAR). Daaronder ben je ermee bezig. */
function gcStand(){
  var u = {vast:0, onderhoud:0, bezig:0, open:0};
  GC_ORDE.forEach(function(id){
    var st = {};
    try { st = gramLees(id) || {}; } catch(e){ st = {}; }
    var beurten = (st.goed || 0) + (st.fout || 0);
    if(!beurten){ u.open++; return; }
    var b = st.box || 0;
    if(b >= 4) u.vast++;
    else if(b === 3) u.onderhoud++;
    else u.bezig++;
  });
  return u;
}
function gcStandHtml(){
  var u = gcStand(), n = GC_ORDE.length || 1;
  var pct = function(x){ return (100 * x / n).toFixed(1) + "%"; };
  var stip = function(kleur){
    return "<i style='display:inline-block; width:9px; height:9px; border-radius:50%; background:" +
      kleur + "; margin-right:5px; vertical-align:middle'></i>";
  };
  return "<div style='margin:12px 0 2px'>" +
    "<div style='height:9px; border-radius:99px; background:var(--border); overflow:hidden; display:flex'>" +
      "<i style='display:block; height:100%; width:" + pct(u.vast) + "; background:var(--green)'></i>" +
      "<i style='display:block; height:100%; width:" + pct(u.onderhoud) + "; background:var(--green); opacity:.55'></i>" +
      "<i style='display:block; height:100%; width:" + pct(u.bezig) + "; background:var(--accent)'></i>" +
    "</div>" +
    "<div class='muted' style='display:flex; flex-wrap:wrap; gap:4px 14px; font-size:.76rem; margin-top:7px'>" +
      "<span>" + stip("var(--green)") + u.vast + " " + ct("beheerst", "solid") + "</span>" +
      "<span>" + stip("rgba(47,107,79,.55)") + u.onderhoud + " " + ct("in onderhoud", "in upkeep") + "</span>" +
      "<span>" + stip("var(--accent)") + u.bezig + " " + ct("mee bezig", "in progress") + "</span>" +
      "<span>" + stip("var(--border)") + u.open + " " + ct("nog te gaan", "to go") + "</span>" +
    "</div></div>";
}

'''

rep("function gcRouteRijHtml(c, nr, vandaagSet){", KAART + "function gcRouteRijHtml(c, nr, vandaagSet){")

# de knop in de routerij
OUD_RIJ = """  return "<div class='lesson gcroute'" + (open ? " data-gclees='" + c.id + "'" : " style='opacity:.5'") + ">" +
    "<div class='lnum' style='color:" + kleur + "'>" + merk + "</div>" +
    "<div class='lbody'><b>" + c.icon + " " + ct(c.naam, c.naamEn) + "</b><span>" + onder + "</span></div>" +
    "<div class='lstatus' style='font-size:.72rem; text-align:right'>" +
      (!open ? "\\ud83d\\udd12"
             : (nu ? "<b style='color:var(--accent)'>" + ct("vandaag", "today") + "</b>" : "\\u25b6")) +
    "</div></div>";"""
NIEUW_RIJ = """  /* v23.256: een onderwerp dat alleen op een plek wacht, is geen slot maar een keuze. Het krijgt
     dus geen hangslot maar een knop, en het staat minder ver weggedimd dan een onderwerp waar je
     echt nog niet bij kunt. */
  var kiesbaar = false;
  try { kiesbaar = !open && gcKiesbaar(c.id); } catch(e){ kiesbaar = false; }
  var rechts = open ? (nu ? "<b style='color:var(--accent)'>" + ct("vandaag", "today") + "</b>" : "\\u25b6")
    : (kiesbaar
        ? "<button type='button' class='ghost' data-gckies='" + c.id + "' " +
          "style='font-size:.72rem; padding:5px 9px; white-space:nowrap'>" + ct("Nu doen", "Do this now") + "</button>"
        : "\\ud83d\\udd12");
  return "<div class='lesson gcroute'" + (open ? " data-gclees='" + c.id + "'" : " style='opacity:" + (kiesbaar ? ".8" : ".5") + "'") + ">" +
    "<div class='lnum' style='color:" + kleur + "'>" + merk + "</div>" +
    "<div class='lbody'><b>" + c.icon + " " + ct(c.naam, c.naamEn) + "</b><span>" + onder + "</span></div>" +
    "<div class='lstatus' style='font-size:.72rem; text-align:right'>" + rechts +
    "</div></div>";"""
rep(OUD_RIJ, NIEUW_RIJ)

# gcSlotReden: zeg bij het venster dat je zelf mag kiezen
OUD_REDEN = """  return ct("opent zodra je een van de open onderwerpen aanpakt",
            "opens once you take on one of the open topics");"""
NIEUW_REDEN = """  /* v23.256: hier stond "opent zodra je een van de open onderwerpen aanpakt". Dat was waar en het
     was ook een doodlopende weg: het onderwerp dat je wilt staat op plek 30 en je komt er nooit.
     Nu zegt de regel wat er werkelijk aan de hand is, en ernaast staat de knop. */
  return ct("wacht op een plek, of pak hem nu",
            "waiting for a slot, or take it now");"""
rep(OUD_REDEN, NIEUW_REDEN)

# ---------------------------------------------------------------- 3. de kaart inhangen

OUD_KOP = """    (con.length
      ? "<p style='margin:14px 0 4px'><b>" + ct("De route", "The route") + "</b> <span class='muted'>\\u00b7 " +"""
NIEUW_KOP = """    gcStandHtml() +
    (con.length
      ? "<p style='margin:14px 0 4px'><b>" + ct("De route", "The route") + "</b> <span class='muted'>\\u00b7 " +"""
rep(OUD_KOP, NIEUW_KOP)

# ---------------------------------------------------------------- 4. de knop aansluiten

OUD_WIRE = """  el.querySelectorAll("[data-gclees]").forEach(function(d){
    d.onclick = function(){ gcLeesOpen(d.getAttribute("data-gclees")); };
  });"""
NIEUW_WIRE = """  el.querySelectorAll("[data-gclees]").forEach(function(d){
    d.onclick = function(){ gcLeesOpen(d.getAttribute("data-gclees")); };
  });
  /* v23.256: zelf een onderwerp kiezen. De knop zit in een rij die GEEN data-gclees heeft (die rij
     staat immers op slot), dus er is niets om te stoppen; alleen openen en opnieuw tekenen. */
  el.querySelectorAll("[data-gckies]").forEach(function(d){
    d.onclick = function(ev){
      if(ev && ev.stopPropagation) ev.stopPropagation();
      gcKiesOnderwerp(d.getAttribute("data-gckies"));
      renderCheat();
    };
  });"""
rep(OUD_WIRE, NIEUW_WIRE)

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
