#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.25: de tooltip herkent werkwoordconstructies.

Stefan las "los vecinos dejan de saludarse" en zei het precieze: je wilt hier "dejar de" uitgelegd
krijgen, niet "dejan" en "saludarse" los. Twee kloppende woordbetekenissen leveren samen een zin op
die iets anders betekent dan wat er staat, en dat is erger dan een woord dat je niet kent, want je
merkt het niet.

Dit is de bekendste valkuil van woord-voor-woord opzoeken. Spaans hangt aan vaste combinaties van een
werkwoord met een voorzetsel: dejar de (ophouden met), volver a (opnieuw), acabar de (net gedaan
hebben), tener que (moeten), ponerse a (beginnen te). Wie die niet herkent leest de woorden goed en
de zin fout.

Wat er nu gebeurt: bij het aantikken kijkt de app ook naar de buren in dezelfde zin. Past daar een
constructie omheen, dan staat die bovenaan in de tooltip, met de losse betekenis eronder. Zestien
constructies, en dat is met opzet een korte lijst: dit zijn de vormen die in bijna elke Spaanse tekst
staan, en een lange lijst met halve treffers zou het omgekeerde doen van waar hij voor is.

De vervoeging van het eerste werkwoord wordt op de stam herkend (dejan, deja, dejaron, dejó), want
anders werkt hij alleen in de derde persoon meervoud.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "LEES_CONSTRUCTIES" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. de constructies
rep(
    """var LEES_LETTERS = {""",
    """/* v23.25. Vaste combinaties van een werkwoord met een voorzetsel. Ze staan hier en niet bij de
   woorden, want het zijn geen woorden: het is een patroon over drie posities in een zin.

   stam is een reeks beginletters van het eerste werkwoord, zodat elke vervoeging meedoet (dejan,
   deja, dejaron, dejó). deel is het vaste woord ertussen, of leeg als er geen tussenwoord is. eind
   zegt wat er achteraan hoort: "inf" voor een hele werkwoordsvorm, "ger" voor een -ndo-vorm.

   Kort gehouden met opzet. Dit zijn de vormen die in vrijwel elke Spaanse tekst staan. Een lange
   lijst met halve treffers zou precies het omgekeerde doen van waar dit voor bedoeld is. */
var LEES_CONSTRUCTIES = [
 {stam:["dej"], deel:"de", eind:"inf", nl:"ophouden met, stoppen met", en:"to stop doing"},
 {stam:["empez","empie","comenz","comien"], deel:"a", eind:"inf", nl:"beginnen te", en:"to start to"},
 {stam:["volv","vuelv"], deel:"a", eind:"inf", nl:"opnieuw, weer", en:"to do again"},
 {stam:["acab"], deel:"de", eind:"inf", nl:"net gedaan hebben", en:"to have just done"},
 {stam:["termin"], deel:"de", eind:"inf", nl:"klaar zijn met", en:"to finish doing"},
 {stam:["trat"], deel:"de", eind:"inf", nl:"proberen te", en:"to try to"},
 {stam:["olvid"], deel:"de", eind:"inf", nl:"vergeten te", en:"to forget to"},
 {stam:["v","ib","ir"], deel:"a", eind:"inf", nl:"gaan (straks)", en:"going to (future)"},
 {stam:["pon","pus"], deel:"a", eind:"inf", nl:"beginnen te", en:"to start to"},
 {stam:["lleg"], deel:"a", eind:"inf", nl:"erin slagen te, zelfs gaan", en:"to manage to, even to"},
 {stam:["ayud"], deel:"a", eind:"inf", nl:"helpen om te", en:"to help to"},
 {stam:["aprend"], deel:"a", eind:"inf", nl:"leren om te", en:"to learn to"},
 {stam:["ten","tien","tuv","tendr"], deel:"que", eind:"inf", nl:"moeten", en:"to have to"},
 {stam:["hay"], deel:"que", eind:"inf", nl:"je moet, men moet", en:"one has to"},
 {stam:["sigu","sig","segu"], deel:"", eind:"ger", nl:"blijven (doorgaan met)", en:"to keep on doing"},
 {stam:["est"], deel:"", eind:"ger", nl:"aan het ... zijn", en:"to be doing"}
];
var LEES_LETTERS = {""")

# ---------------------------------------------------------------- 2. de herkenner
rep(
    """function leesNoteer(plat){""",
    """function leesPlat(w){ return stripAcc(String(w || "").toLowerCase()).replace(/[^a-z]/g, ""); }
function leesIsInf(w){ return /(ar|er|ir|arse|erse|irse|arme|arte|arlo|arla|arle)$/.test(leesPlat(w)); }
function leesIsGer(w){ return /(ando|iendo|yendo)$/.test(leesPlat(w)); }
/* Past er een constructie om het woord dat je aantikte? We proberen drie startposities, zodat het
   niet uitmaakt of je op dejan, op de of op saludarse tikt: alle drie horen bij hetzelfde patroon. */
function leesConstructie(woorden, i){
  var start, c, k, w0, w1, w2, lengte, past;
  for(start = Math.max(0, i - 2); start <= i; start++){
    for(k = 0; k < LEES_CONSTRUCTIES.length; k++){
      c = LEES_CONSTRUCTIES[k];
      lengte = c.deel ? 3 : 2;
      if(start + lengte - 1 >= woorden.length) continue;
      if(i > start + lengte - 1) continue;
      w0 = leesPlat(woorden[start]);
      w1 = woorden[start + 1];
      w2 = woorden[start + 2];
      past = c.stam.some(function(s){ return w0.indexOf(s) === 0; });
      if(!past) continue;
      if(c.deel){
        if(leesPlat(w1) !== c.deel) continue;
        if(c.eind === "inf" && !leesIsInf(w2)) continue;
        if(c.eind === "ger" && !leesIsGer(w2)) continue;
        return {tekst:woorden[start] + " " + w1 + " " + w2, nl:ct(c.nl, c.en)};
      }
      if(c.eind === "ger" && !leesIsGer(w1)) continue;
      if(c.eind === "inf" && !leesIsInf(w1)) continue;
      return {tekst:woorden[start] + " " + w1, nl:ct(c.nl, c.en)};
    }
  }
  return null;
}
function leesNoteer(plat){""")

# ---------------------------------------------------------------- 3. de woorden onthouden per hoofdstuk
rep(
    """function leesTekstHtml(p){
  var veilig = String(p).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return veilig.replace(/([A-Za-z\\u00c0-\\u024f]+)/g, function(m){
    return "<span class='lw' data-lw=\\""+m+"\\">"+m+"</span>";
  });
}""",
    """/* De woorden van het hoofdstuk op volgorde, zodat de constructieherkenner de buren kan zien. Hij
   staat hier als lijst en niet in de DOM, want uit de DOM teruglezen zou betekenen dat de opmaak de
   betekenis bepaalt. */
var leesWoorden = [];
function leesTekstHtml(p){
  var veilig = String(p).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return veilig.replace(/([A-Za-z\\u00c0-\\u024f]+)/g, function(m){
    var i = leesWoorden.length;
    leesWoorden.push(m);
    return "<span class='lw' data-lw=\\""+m+"\\" data-li='"+i+"'>"+m+"</span>";
  });
}""")

rep(
    """  // v23.21: elk woord is aan te tikken. De alinea's blijven verder precies zoals ze waren.
  var paras = h.tekst.split("\\n\\n").map(function(p){ return "<p>"+leesTekstHtml(p)+"</p>"; }).join("");""",
    """  // v23.21: elk woord is aan te tikken. De alinea's blijven verder precies zoals ze waren.
  leesWoorden = [];
  var paras = h.tekst.split("\\n\\n").map(function(p){ return "<p>"+leesTekstHtml(p)+"</p>"; }).join("");""")

# ---------------------------------------------------------------- 4. in de tooltip
rep(
    """function leesToon(woord, span){
  var el = document.getElementById("leesUitleg");
  if(!el) return;""",
    """function leesToon(woord, span){
  var el = document.getElementById("leesUitleg");
  if(!el) return;
  var con = null;
  if(span && span.getAttribute("data-li") !== null){
    try { con = leesConstructie(leesWoorden, +span.getAttribute("data-li")); } catch(e){ con = null; }
  }
  /* De constructie staat bovenaan en het losse woord eronder. Die volgorde is het punt: wie
     "dejan de saludarse" leest heeft niets aan "dejan = zij laten", en zou met die twee losse
     betekenissen een zin bouwen die het tegenovergestelde zegt van wat er staat. */
  var kop = con ? "<p><span class='es'>"+con.tekst+"</span></p><p>"+con.nl+"</p>"+
                  "<div style='border-top:1px solid var(--border); margin:6px 0 4px'></div>" : "";""")

rep(
    """    var naam = /^[A-ZÁÉÍÓÚÑ]/.test(String(woord));
    el.innerHTML = "<p><span class='es'>"+woord+"</span></p>"+""",
    """    var naam = /^[A-ZÁÉÍÓÚÑ]/.test(String(woord));
    el.innerHTML = kop + "<p><span class='es'>"+woord+"</span></p>"+""")

rep(
    """  el.innerHTML = "<p><span class='es'>"+woord+"</span>"+
      (stripAcc(String(b.es).toLowerCase()) !== stripAcc(String(woord).toLowerCase())
        ? " <span class='muted'>"+brug+" <span class='es'>"+b.es+"</span></span>" : "")+
      extra+"</p>"+
    "<p>"+b.nl+"</p>";""",
    """  el.innerHTML = kop + "<p><span class='es'>"+woord+"</span>"+
      (stripAcc(String(b.es).toLowerCase()) !== stripAcc(String(woord).toLowerCase())
        ? " <span class='muted'>"+brug+" <span class='es'>"+b.es+"</span></span>" : "")+
      extra+"</p>"+
    "<p>"+b.nl+"</p>";""")

rep('var APP_VERSIE = "v23.24";', 'var APP_VERSIE = "v23.25";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.25 toegepast op", PAD)
