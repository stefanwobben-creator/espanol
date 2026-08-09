#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.21: tik op een woord in het verhaal.

Stefan leest Chispa met DeepL ernaast, zin voor zin. Nagerekend op de echte tekst van alle dertien
hoofdstukken (2986 woorden): de woordenschat van zijn track dekt 56 procent van de lopende woorden.
Dat zijn ongeveer vijf onbekende woorden in een zin van twaalf. Rond de 95 procent dekking kun je een
tekst met hulp volgen, rond de 98 zelfstandig (Hu & Nation, 2000). Hij zit daar ver onder, dus dit is
geen ongeduld maar rekenkunde.

Wachten tot A2 lost dat niet op: om op 95 procent te komen heb je een paar duizend woorden nodig, en
dat is B1 of hoger. Wie wacht tot het vanzelf gaat, leest dit boek nooit.

Wat wel kan: het woordenboek dat er al ligt aan de tekst hangen. Woorden plus FREQ dekken samen 95
procent van deze tekst, en vormAnalyse() herkent vervoegingen (comiste naar comer). Die machine
bestond al, er was alleen geen manier om hem vanuit een leestekst aan te roepen.

De hulp is met opzet op verzoek en niet standaard zichtbaar. Een vertaling die er altijd staat lees je
in plaats van het Spaans. Eén tik, nadat je het zelf hebt geprobeerd, is iets anders: de moeite blijft
en de hulp voorkomt alleen dat je vastloopt.

En wat je opzoekt wordt geteld. Dat is de eerlijkste gatenlijst die er bestaat, want het is je eigen
leesgedrag en geen indeling van het Instituto Cervantes. Nog niet zichtbaar, wel vanaf nu bewaard:
zonder opschrijven kun je er later niets mee, en verzinnen kan niet.

Idempotent.
"""
import io, sys, os

PAD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/index.html")

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

if "function leesBetekenis(" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


# ---------------------------------------------------------------- 1. opmaak
rep(
    """  .vgDot.vgRest{background:#e8e1d4;}
""",
    """  .vgDot.vgRest{background:#e8e1d4;}
  /* v23.21: een woord in de leestekst is aan te tikken. Geen onderstreping en geen kleur, want dan
     wordt de bladzijde een veld met tweehonderd knoppen en leest niemand meer een verhaal. Alleen
     het woord dat je aantikt licht op. */
  .lw{cursor:pointer; border-radius:3px; padding:0 1px; margin:0 -1px;}
  .lw.aan{background:var(--accent-soft); box-shadow:0 0 0 1px var(--accent) inset;}
  .leesUit{position:sticky; bottom:0; background:var(--card); border-top:1px solid var(--border);
           padding:10px 2px 4px; margin-top:10px;}
  .leesUit .es{font-weight:700;}
  .leesUit p{margin:2px 0;}
""")

# ---------------------------------------------------------------- 2. de opzoeker
rep(
    """function renderBoekLectura(){""",
    """/* ================= LEZEN MET HULP (v23.21) =================
   Eén opzoeker voor de leestekst, en hij hangt aan de bronnen die er al zijn: eerst de leswoorden
   (want die hebben de vertaling die jij hier geleerd hebt), dan de frequentielijst, dan vormAnalyse
   voor vervoegingen, en pas als dat allemaal niets geeft een poging met het meervoud of het andere
   geslacht eraf. Geen enkele nieuwe woordenlijst: dit is dezelfde machine als het woordenboek. */
var leesFreqIdx = null;
function leesFreqZoek(plat){
  if(!leesFreqIdx){
    leesFreqIdx = {};
    if(typeof FREQ !== "undefined"){
      for(var i = 0; i < FREQ.length; i++){
        var p = stripAcc(FREQ[i][0].toLowerCase()).replace(/[^a-z]/g, "");
        if(p && leesFreqIdx[p] === undefined) leesFreqIdx[p] = i;
      }
    }
  }
  var idx = leesFreqIdx[plat];
  return idx === undefined ? null : {es:FREQ[idx][0], nl:freqGloss(FREQ[idx][0], FREQ[idx][1])};
}
function leesLesWoord(plat){
  var art = {el:1, la:1, los:1, las:1, un:1, una:1}, i, w, delen, j, kern;
  for(i = 0; i < WORDS.length; i++){
    w = WORDS[i];
    delen = String(w.es).toLowerCase().split(/[\\/,]/);
    for(j = 0; j < delen.length; j++){
      kern = delen[j].trim().split(/\\s+/).filter(function(t){ return !art[t]; }).join(" ");
      if(stripAcc(kern).replace(/[^a-z ]/g, "").split(" ").indexOf(plat) !== -1){
        return {es:w.es, nl:wTrans(w), id:w.id};
      }
    }
  }
  return null;
}
function leesBetekenis(ruw){
  var plat = stripAcc(String(ruw || "").toLowerCase()).replace(/[^a-z]/g, "");
  if(plat.length < 2) return null;
  var hit = leesLesWoord(plat);
  if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"les"};
  hit = leesFreqZoek(plat);
  if(hit) return {es:hit.es, nl:hit.nl, soort:"woordenboek"};
  var vormen = [];
  try { vormen = vormAnalyse(ruw); } catch(e){ vormen = []; }
  if(vormen.length && vormen[0].gloss){
    return {es:vormen[0].inf, nl:vormen[0].gloss, soort:"vorm", tijd:vormen[0].tijd,
            persoon:vormen[0].persoon};
  }
  // meervoud en geslacht: gaviotas naar gaviota, curiosos naar curioso
  var pogingen = [plat.replace(/es$/, ""), plat.replace(/s$/, ""),
                  plat.replace(/as$/, "a"), plat.replace(/os$/, "o"),
                  plat.replace(/a$/, "o"), plat.replace(/as$/, "o")];
  for(var k = 0; k < pogingen.length; k++){
    if(!pogingen[k] || pogingen[k] === plat || pogingen[k].length < 2) continue;
    hit = leesLesWoord(pogingen[k]) || leesFreqZoek(pogingen[k]);
    if(hit) return {es:hit.es, nl:hit.nl, id:hit.id, soort:"vorm"};
  }
  return null;
}
/* Wat je opzoekt, wordt geteld. Nog niet getoond: eerst een paar hoofdstukken meten, dan pas iets
   beweren. Zie de weekmetingen en de tijdmeting; dezelfde volgorde. */
function leesNoteer(plat){
  if(!plat) return;
  S.leesZoek = S.leesZoek || {};
  S.leesZoek[plat] = (S.leesZoek[plat] || 0) + 1;
  persist();
}
function leesTekstHtml(p){
  var veilig = String(p).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return veilig.replace(/([A-Za-z\\u00c0-\\u024f]+)/g, function(m){
    return "<span class='lw' data-lw=\\""+m+"\\">"+m+"</span>";
  });
}
function leesToon(woord){
  var el = document.getElementById("leesUitleg");
  if(!el) return;
  var b = leesBetekenis(woord);
  leesNoteer(stripAcc(String(woord).toLowerCase()).replace(/[^a-z]/g, ""));
  if(!b){
    el.innerHTML = "<p><span class='es'>"+woord+"</span></p>"+
      "<p class='muted' style='font-size:.85rem'>"+
        ct("Dit woord staat niet in het woordenboek. Het is genoteerd, zodat het er een keer bij komt.",
           "This word is not in the dictionary. It has been noted, so it can be added later.")+"</p>";
    return;
  }
  var extra = "";
  if(b.soort === "vorm" && b.tijd){
    extra = " <span class='muted'>("+b.tijd+(b.persoon ? ", "+b.persoon : "")+")</span>";
  }
  el.innerHTML = "<p><span class='es'>"+woord+"</span>"+
      (stripAcc(String(b.es).toLowerCase()) !== stripAcc(String(woord).toLowerCase())
        ? " <span class='muted'>"+ct("van","from")+" <span class='es'>"+b.es+"</span></span>" : "")+
      extra+"</p>"+
    "<p>"+b.nl+"</p>";
}

function renderBoekLectura(){""")

# ---------------------------------------------------------------- 3. de tekst wordt aantikbaar
rep(
    """  var paras = h.tekst.split("\\n\\n").map(function(p){ return "<p>"+p+"</p>"; }).join("");""",
    """  // v23.21: elk woord is aan te tikken. De alinea's blijven verder precies zoals ze waren.
  var paras = h.tekst.split("\\n\\n").map(function(p){ return "<p>"+leesTekstHtml(p)+"</p>"; }).join("");""")

rep(
    """    paras+
    "<div class='row'><button class='primary' id='btnBoekVragen'>"+ct("Naar de vragen →","To the questions →")+"</button>"+
    "<button class='ghost' id='btnBoekMenu'>"+ct("Terug","Back")+"</button></div>";
  document.getElementById("btnBoekLuister").onclick = function(){ boekSpreek(h); };""",
    """    paras+
    "<div class='leesUit' id='leesUitleg'><p class='muted' style='font-size:.85rem'>"+
      ct("Tik op een woord dat je niet kent, dan staat de betekenis hier.",
         "Tap a word you do not know and its meaning appears here.")+"</p></div>"+
    "<div class='row'><button class='primary' id='btnBoekVragen'>"+ct("Naar de vragen →","To the questions →")+"</button>"+
    "<button class='ghost' id='btnBoekMenu'>"+ct("Terug","Back")+"</button></div>";
  /* Eén luisteraar op de kaart in plaats van tweehonderd op de losse woorden: dat scheelt bij een
     hoofdstuk van driehonderd woorden een hoop werk bij elke render, en het gedrag is hetzelfde. */
  el.onclick = function(ev){
    var t = ev.target;
    if(!t || !t.classList || !t.classList.contains("lw")) return;
    var vorige = el.querySelector(".lw.aan");
    if(vorige) vorige.classList.remove("aan");
    t.classList.add("aan");
    leesToon(t.getAttribute("data-lw"));
  };
  document.getElementById("btnBoekLuister").onclick = function(){ boekSpreek(h); };""")

# ---------------------------------------------------------------- 4. versie
rep('var APP_VERSIE = "v23.20";', 'var APP_VERSIE = "v23.21";')

with io.open(PAD, "w", encoding="utf-8") as f:
    f.write(src)
print("v23.21 toegepast op", PAD)
