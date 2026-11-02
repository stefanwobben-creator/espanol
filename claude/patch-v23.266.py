# patch-v23.266.py - de les van de week: maandag drie voorstellen, jij kiest er een.
#
# WAT STEFAN VROEG
#
# "kunnen we ook een keer per week bijv een bestaand of nieuw grammatica concept, echt meer een
# volledige les introduceren?" En op de vraag of de app moet kiezen of hij zelf: "maandagochtend
# zelf kiezen uit drie voorstellen."
#
# WAT ER NU IS, EN WAAROM DAT GEEN LES IS
#
# Een microles is drie stappen en vijf vragen, en elke stap is: hier is een voorbeeld, kies de
# vorm, hier is een regel van een zin. Dat is een opfrisser. Wat eraan ontbreekt is de stap die
# ervoor hoort te komen.
#
# VanPatten en Cadierno (1993) lieten twee groepen hetzelfde grammaticapunt leren: de ene oefende
# zoals hier, door de vorm te produceren; de andere kreeg alleen zinnen te LEZEN en moest zeggen
# wat ze betekenden, met zinnen waarin je de uitgang nodig hebt om dat te kunnen. Die tweede groep
# deed het op de productietoets net zo goed en op de begripstoets veel beter. Hun verklaring is het
# Lexical Preference Principle: een leerling hangt aan de woorden en slaat de uitgang over, zolang
# de woorden alleen al genoeg zijn om de zin te snappen. Dan helpt meer produceren niet, want de
# vorm is nog nooit binnengekomen.
#
# DE VIER FASEN, EN WAT ZE HIER ZIJN
#
#   1. MERKEN. Zes complete zinnen, de helft met de goede vorm en de helft met een andere, en jij
#      zegt alleen of de zin klopt. Geen productie, geen gat om te vullen: lezen en oordelen. Deze
#      fase telt NIET mee voor je doosjes; het is binnenkomen, geen toets.
#   2. DE REGEL. De uitleg van het concept, met de ezelsbrug, en een begripsvraag erachter. Die
#      vraag staat er met opzet ná en niet vóór: pas als je zes zinnen hebt gezien kun je hem
#      beantwoorden (dezelfde volgorde als v23.59).
#   3. DOOR ELKAAR. Zes vragen over dit onderwerp, vermengd met vier van onderwerpen die je al
#      kent. Rohrer, Dedrick en Stershic (2015): dezelfde stof gebundeld tegenover door elkaar,
#      een maand later getoetst, 38 procent tegen 72. Deze fase telt wel mee, en elke vraag draagt
#      zijn eigen onderwerp (dezelfde afspraak als de oefensessie, v23.260).
#   4. ZELF SCHRIJVEN. Geen vierde stap in de wizard maar een knop aan het eind, naar het gesprek
#      met Chispa die sinds v23.257 meekijkt en je eerst zelf laat herstellen.
#
# WAAROM HIJ NAAST DE DAGLES STAAT EN NIET ERIN
#
# Stefan, over het plannen van lessen: "als je het leuk vind om af en toe een les te doen, werkt
# dit averechts, want dan moet je ofzo." Een les van een kwartier in de dagles zetten maakt van de
# dag die hij vrijwillig opent een verplichting. Hij staat er dus naast en wacht tot hij geopend
# wordt. En de fasen zijn los af te maken: stop je na fase 1 en 2, dan heb je het beste deel gehad
# en ben je niets kwijt.
#
# DE DRIE VOORSTELLEN
#
# Een uit elke hoek, zodat de keuze echt iets te kiezen heeft: waar het deze week het vaakst
# misging, het zwakste onderwerp dat openstaat, en iets nieuws van de route (ook als het venster
# het nog dichthoudt, want sinds v23.256 mag je dat zelf openen). Blijft er een plek over, dan
# wordt hij gevuld uit de route.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "weekVoorstellen" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


WEEK = r'''/* ================= DE LES VAN DE WEEK (v23.266) =================

   Stefan: "kunnen we ook een keer per week een bestaand of nieuw grammatica concept, echt meer een
   volledige les introduceren?" En: "maandagochtend zelf kiezen uit drie voorstellen."

   Vier fasen: merken, de regel, door elkaar oefenen, zelf schrijven. De eerste is de stap die in de
   microles helemaal ontbrak. VanPatten en Cadierno (1993): wie een vorm eerst alleen hoeft te LEZEN
   en te begrijpen, produceert hem daarna net zo goed als wie meteen gaat produceren, en begrijpt hem
   veel beter. Een leerling hangt aan de woorden en slaat de uitgang over zolang de woorden al genoeg
   zijn om de zin te snappen; dan helpt meer produceren niet.

   De week loopt van maandag tot maandag en de sleutel IS die maandag, als datum. Daarmee is er geen
   weeknummer nodig dat over de jaargrens heen fout kan gaan, en is in de opslag te lezen over welke
   week het gaat. */
var WEEK_KEUZES = 3;      // zoveel voorstellen krijg je op maandag
var WEEK_MERKEN = 6;      // zinnen om alleen te beoordelen in fase 1
var WEEK_OEFEN = 6;       // vragen over het onderwerp zelf in fase 3
var WEEK_ERBIJ = 4;       // vragen van onderwerpen die je al kent, erdoorheen

function weekMaandag(){
  try {
    var d = new Date(today() + "T12:00:00Z");
    d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 6) % 7));
    return d.toISOString().slice(0, 10);
  } catch(e){ return today(); }
}
function weekStand(){
  var m = weekMaandag();
  if(!S.weekles || S.weekles.week !== m) S.weekles = {week:m, cid:null};
  return S.weekles;
}
function weekId(cid){ return "week-" + cid; }
function weekKlaar(){
  var st = weekStand();
  if(!st.cid) return false;
  try { return !!(gwVoortgangLees(weekId(st.cid)) || {}).klaar; } catch(e){ return false; }
}
/* Een uit elke hoek. Drie keer het zwakste onderwerp aanbieden is geen keuze, en dat is precies wat
   een lijst op doos zou opleveren. */
function weekVoorstellen(){
  var uit = [], gehad = {};
  function voeg(id){ if(id && !gehad[id] && uit.length < WEEK_KEUZES){ gehad[id] = 1; uit.push(id); } }
  var open = [];
  try { open = gcGeordend().filter(function(c){ return gcConceptOpen(c.id); }); } catch(e){ open = []; }
  // 1. waar het deze week het vaakst misging
  var mis = open.slice().sort(function(a, b){ return gcVersMissers(b.id) - gcVersMissers(a.id); })[0];
  try { if(mis && gcVersMissers(mis.id) >= 1) voeg(mis.id); } catch(e){}
  // 2. het zwakste onderwerp dat openstaat
  var zwak = open.slice().sort(function(a, b){
    var ab = 0, bb = 0;
    try { ab = gramLees(a.id).box || 0; bb = gramLees(b.id).box || 0; } catch(e){}
    return ab - bb;
  })[0];
  if(zwak) voeg(zwak.id);
  // 3. iets nieuws van de route, ook als het venster het nog dichthoudt (v23.256)
  var nieuw = null;
  try { gcGeordend().forEach(function(c){ if(!nieuw && gcKiesbaar(c.id)) nieuw = c; }); } catch(e){}
  if(nieuw) voeg(nieuw.id);
  // en anders gewoon verder op de route
  open.forEach(function(c){ voeg(c.id); });
  return uit;
}
function weekKies(cid){
  var st = weekStand();
  st.cid = cid;
  /* Staat het onderwerp nog achter het venster, dan gaat het hiermee open. Dat is dezelfde
     handeling als de knop "Nu doen" op de route, en hij hoort hier ook te gelden: je kunt geen les
     van de week kiezen die daarna op slot blijft. */
  try { if(gcKiesbaar(cid)) gcKiesOnderwerp(cid); } catch(e){}
  persist();
}
/* De onderwerpen die erdoorheen gemengd worden: wat je al kunt, want daar gaat interleaving over.
   Een onderwerp dat je ook nog aan het leren bent erdoorheen mengen maakt er twee lessen van. */
function weekBekend(nietCid){
  var uit = [];
  try {
    gcGeordend().forEach(function(c){
      if(uit.length >= 2 || c.id === nietCid || !gcConceptOpen(c.id)) return;
      if((gramLees(c.id).box || 0) >= 2) uit.push(c);
    });
  } catch(e){}
  return uit;
}
function weekMeng(eigen, erbij){
  var uit = [], i = 0, j = 0;
  while(i < eigen.length || j < erbij.length){
    if(i < eigen.length) uit.push(eigen[i++]);
    if(i < eigen.length) uit.push(eigen[i++]);
    if(j < erbij.length) uit.push(erbij[j++]);
  }
  return uit;
}
/* Fase 1: dezelfde patroonvragen, maar omgedraaid. De gegenereerde vraag is "zin met een gat plus
   twee of drie opties"; hier wordt het gat gevuld (de helft met de goede vorm, de helft met een
   andere) en is de vraag alleen nog of de zin klopt. Geen productie, geen gat.

   Deze vragen dragen met opzet GEEN cid. gramAntwoord() schrijft dan niets weg, en dat is de
   bedoeling: oordelen over een zin die je voorgeschoteld krijgt is binnenkomen en geen toets, en
   met twee opties is de gokkans vijftig procent. */
function weekMerkVragen(c){
  var bron = [];
  try { bron = gcMaakVragen(c, WEEK_MERKEN) || []; } catch(e){ bron = []; }
  var uit = [];
  bron.forEach(function(q, i){
    if(!q || !q.o || q.o.length < 2 || String(q.v || "").indexOf("___") === -1) return;
    var goedeZin = (i % 2 === 0);
    var juist = q.o[q.g];
    var anders = q.o[(q.g + 1) % q.o.length];
    if(!goedeZin && String(anders) === String(juist)) return;
    var vul = goedeZin ? juist : anders;
    uit.push({
      v: String(q.v).replace("___", vul),
      vEn: String(q.vEn || q.v).replace("___", vul),
      o: ["Deze klopt", "Hier zit iets mis"],
      oEn: ["This one is right", "Something is off here"],
      g: goedeZin ? 0 : 1,
      w: (goedeZin ? "" : "Het moest " + juist + " zijn. ") + (q.w || ""),
      wEn: (goedeZin ? "" : "It had to be " + juist + ". ") + (q.wEn || q.w || "")
    });
  });
  return uit;
}
function weekBouw(id){
  var cid = String(id || "").replace(/^week-/, "");
  var c = gcConcept(cid);
  if(!c) return null;
  var naam = ct(c.naam, c.naamEn || c.naam);
  var stappen = [];

  var merken = weekMerkVragen(c);
  if(merken.length >= 3){
    stappen.push({
      kop: "Eerst alleen lezen", kopEn: "Just read, for now",
      uitleg: "<p>Zes zinnen. Je hoeft niets in te vullen en niets te bedenken: lees ze en zeg of " +
              "ze kloppen. Sommige kloppen niet.</p><p class='muted'>Deze stap telt niet mee voor je " +
              "doosjes. Hij is er om de vorm te laten binnenkomen voordat je hem zelf moet maken.</p>",
      uitlegEn: "<p>Six sentences. Nothing to fill in and nothing to work out: read them and say " +
                "whether they are right. Some are not.</p><p class='muted'>This step does not count " +
                "towards your boxes. It is here to let the form sink in before you have to produce it.</p>",
      vragen: merken
    });
  }

  var begrip = null;
  try {
    begrip = gcSchud({v:c.begrip.v, vEn:c.begrip.vEn, o:c.begrip.o.slice(),
                      oEn:c.begrip.oEn ? c.begrip.oEn.slice() : null,
                      g:c.begrip.g, w:c.begrip.w, wEn:c.begrip.wEn, cid:c.id});
  } catch(e){ begrip = null; }
  stappen.push({
    kop: "En dit is de regel", kopEn: "And this is the rule",
    hulp: (function(){ try { return gcHulp(c.id); } catch(e){ return null; } })(),
    uitleg: c.uitleg, uitlegEn: c.uitlegEn,
    vragen: begrip ? [begrip] : []
  });

  var eigen = [];
  try { eigen = (gcMaakVragen(c, WEEK_OEFEN) || []).map(function(q){ q.cid = c.id; return q; }); } catch(e){ eigen = []; }
  var erbij = [];
  weekBekend(c.id).forEach(function(oc){
    if(erbij.length >= WEEK_ERBIJ) return;
    try {
      (gcMaakVragen(oc, 2) || []).forEach(function(q){
        if(erbij.length >= WEEK_ERBIJ) return;
        q.cid = oc.id; erbij.push(q);
      });
    } catch(e){}
  });
  var door = weekMeng(eigen, erbij);
  if(door.length){
    stappen.push({
      kop: "En nu door elkaar", kopEn: "And now mixed up",
      procedureel: true,
      uitleg: "<p>" + naam + ", vermengd met onderwerpen die je al kent. Door elkaar oefenen voelt " +
              "rommeliger en levert meer op: je moet per vraag opnieuw beslissen wélke regel geldt.</p>",
      uitlegEn: "<p>" + naam + ", mixed with topics you already know. Mixed practice feels messier " +
                "and pays off more: you have to decide which rule applies all over again each time.</p>",
      vragen: door
    });
  }
  if(!stappen.length) return null;
  return {
    id: id, concept: null, week: true, weekCid: c.id, icon: c.icon, drill: c.drill || null,
    titel: "De les van de week: " + naam,
    titelEn: "This week's lesson: " + ct(c.naam, c.naamEn || c.naam),
    pitch: "Vier fasen, een kwartier. Je mag halverwege stoppen.",
    pitchEn: "Four phases, about fifteen minutes. You may stop halfway.",
    stappen: stappen
  };
}
/* De kaart op de grammaticatab: of drie voorstellen, of de les die je gekozen hebt. */
function weekKaartHtml(){
  var st = weekStand();
  var kop = "<p style='margin:16px 0 4px'><b>" + ct("De les van de week", "This week's lesson") +
    "</b> <span class='muted'>\u00b7 " +
    ct("een kwartier, naast je dagles, en je mag halverwege stoppen",
       "fifteen minutes, beside your daily session, and you may stop halfway") + "</span></p>";
  if(!st.cid){
    var v = weekVoorstellen();
    if(!v.length) return "";
    return kop + "<p class='muted' style='margin:0 0 6px; font-size:.84rem'>" +
      ct("Kies er een. De andere twee komen vanzelf nog een keer langs.",
         "Pick one. The other two will come round again.") + "</p>" +
      v.map(function(cid){
        var c = gcConcept(cid);
        if(!c) return "";
        var reden = "";
        try { reden = gcVersMissers(cid) >= 1
          ? ct("hier ging het deze week " + gcVersMissers(cid) + " keer mis",
               "this went wrong " + gcVersMissers(cid) + " times this week")
          : (gcKiesbaar(cid) ? ct("nieuw op je route", "new on your route")
                             : gcStatusHtml(cid)); } catch(e){ reden = ""; }
        return "<div class='lesson' data-weekkies='" + cid + "'>" +
          "<div class='lnum'>" + c.icon + "</div>" +
          "<div class='lbody'><b>" + ct(c.naam, c.naamEn) + "</b><span>" + reden + "</span></div>" +
          "<div class='lstatus' style='font-size:.72rem; text-align:right'>\u25b6</div></div>";
      }).join("");
  }
  var c2 = gcConcept(st.cid);
  if(!c2){ st.cid = null; return weekKaartHtml(); }
  var af = weekKlaar();
  return kop +
    "<div class='lesson'" + (af ? "" : " data-weekstart='" + st.cid + "'") + ">" +
      "<div class='lnum'>" + c2.icon + "</div>" +
      "<div class='lbody'><b>" + ct(c2.naam, c2.naamEn) + "</b><span>" +
        (af ? ct("deze week gedaan", "done this week")
            : ct("vier fasen: lezen, de regel, door elkaar, zelf schrijven",
                 "four phases: reading, the rule, mixed practice, writing")) + "</span></div>" +
      "<div class='lstatus' style='font-size:.72rem; text-align:right'>" + (af ? "\u2713" : "\u25b6") + "</div></div>" +
    (af ? "" : "<button type='button' class='ghost' id='weekAnders' style='margin-top:6px; font-size:.8rem'>" +
      ct("Toch een ander onderwerp", "A different topic after all") + "</button>");
}

'''

rep("function gcSessieBouw(id){", WEEK + "function gcSessieBouw(id){")

# de bouwer registreren
rep('''  // v23.260: de oefensessie. Eén stap met vragen van verschillende onderwerpen door elkaar.
  {pre: "sessie-",  bouw: function(id){ return gcSessieBouw(id); }}
];''',
    '''  // v23.260: de oefensessie. Eén stap met vragen van verschillende onderwerpen door elkaar.
  {pre: "sessie-",  bouw: function(id){ return gcSessieBouw(id); }},
  // v23.266: de les van de week, in vier fasen.
  {pre: "week-",    bouw: function(id){ return weekBouw(id); }}
];''')

# het kanaal
rep('''function gwKanaal(o){
  if(o && o.drillSess) return "drill";
  if(o && o.sessie) return "sessie";
  return (o && o.opfris) ? "opfris" : "microles";
}''',
    '''function gwKanaal(o){
  if(o && o.drillSess) return "drill";
  if(o && o.sessie) return "sessie";
  if(o && o.week) return "weekles";
  return (o && o.opfris) ? "opfris" : "microles";
}''')

# de kaart op de tab, boven de oefensessie
rep('''    gcStandHtml() +
    /* v23.260: de oefensessie.''',
    '''    gcStandHtml() +
    // v23.266: de les van de week staat bovenaan, want hij is van deze week en de rest is van elke dag
    weekKaartHtml() +
    /* v23.260: de oefensessie.''')

# de knoppen aansluiten
rep('''  el.querySelectorAll("[data-gcsessie]").forEach(function(d){''',
    '''  el.querySelectorAll("[data-weekkies]").forEach(function(d){
    d.onclick = function(){ weekKies(d.getAttribute("data-weekkies")); renderCheat(); };
  });
  el.querySelectorAll("[data-weekstart]").forEach(function(d){
    d.onclick = function(){ gwStart(weekId(d.getAttribute("data-weekstart")), 0); };
  });
  el.querySelectorAll("[data-gcsessie]").forEach(function(d){''')

rep('''  lb = document.getElementById("gcToggleAlles");
  if(lb) lb.onclick = function(){ S.gcAlles = !S.gcAlles; persist(); renderCheat(); };''',
    '''  lb = document.getElementById("gcToggleAlles");
  if(lb) lb.onclick = function(){ S.gcAlles = !S.gcAlles; persist(); renderCheat(); };
  lb = document.getElementById("weekAnders");
  if(lb) lb.onclick = function(){ weekStand().cid = null; persist(); renderCheat(); };''')

# fase 4: de knop naar Chispa op het eindscherm
rep('''    "<div class='feedback ok'>"+ct("Alle stappen doorlopen. ","All steps completed. ")+"</div>"+''',
    '''    "<div class='feedback ok'>"+ct("Alle stappen doorlopen. ","All steps completed. ")+"</div>"+
    /* v23.266: de vierde fase van de weekles. Geen stap in de wizard maar een overstap: zelf drie
       zinnen schrijven met het onderwerp erin, bij een Chispa die meekijkt (v23.257). Produceren
       hoort achteraan, na merken, de regel en het oefenen. */
    (o.week
      ? "<p>"+ct("Vierde fase: schrijf er zelf drie zinnen mee. Chispa kijkt mee en laat je het eerst zelf oplossen.",
                 "Fourth phase: write three sentences of your own with it. Chispa looks along and lets you fix it yourself first.")+"</p>"
      : "")+''')

rep('''      (o.drill ? "<button class='"+(inFlow ? "ghost" : "primary")+"' id='gwNaarDrill'>"+ct("Naar de Conjugador \\u2192","To the Conjugador \\u2192")+"</button>" : "")+''',
    '''      (o.week ? "<button class='primary' id='weekNaarChispa'>"+ct("Schrijven met Chispa \\u2192","Writing with Chispa \\u2192")+"</button>" : "")+
      (o.drill ? "<button class='"+(inFlow ? "ghost" : "primary")+"' id='gwNaarDrill'>"+ct("Naar de Conjugador \\u2192","To the Conjugador \\u2192")+"</button>" : "")+''')

rep('''  b = document.getElementById("gwNaarToetsje"); if(b) b.onclick = function(){''',
    '''  b = document.getElementById("weekNaarChispa");
  if(b) b.onclick = function(){ gwSess = null; scopeLesson = null; show("chat"); };
  b = document.getElementById("gwNaarToetsje"); if(b) b.onclick = function(){''')

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
