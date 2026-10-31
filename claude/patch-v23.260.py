# patch-v23.260.py - de oefensessie: tien, twintig of veertig vragen door elkaar heen.
#
# WAT STEFAN ZEI
#
# "het oefenen van grammatica, nu zijn er twee en dan stop ik. dat is goed voor een dagelijkse of
# onverwachte toets, maar wil ik echt oefenen dan wil ik er veel meer achter elkaar oefenen, 10 of
# 20 of 50, meer, zodat het beter beklijft."
#
# WAT DE WETENSCHAP ERVAN ZEGT, EN WAAR IK HEM DUS NIET LETTERLIJK VOLG
#
# Vijftig achter elkaar over EEN onderwerp is niet vijfentwintig keer zoveel waard als twee. Rohrer
# en Taylor (2006) lieten deelnemers binnen een sessie doorploegen tot ver voorbij het punt waarop
# ze het konden; na vier weken was dat voordeel verdwenen, terwijl dezelfde tijd verspreid over
# dagen wel bleef. Cepeda e.a. (2006, 254 studies): de beste tussenpoos is ongeveer tien tot twintig
# procent van hoe lang je het wilt onthouden, en dat is bij een jaar dus weken, geen minuten.
# Vaughn en Rawson (2011): drie tot vier keer correct ophalen, verspreid, en daarna voegt meer
# bijna niets toe.
#
# Maar vijftig vragen over ACHT onderwerpen door elkaar is iets heel anders, en daar is het bewijs
# juist sterk. Rohrer, Dedrick en Stershic (2015) lieten leerlingen dezelfde sommen oefenen, de ene
# groep per soort gebundeld, de andere door elkaar. Op de toets een maand later: 38 procent tegen
# 72 procent. Door elkaar oefenen dwingt je per vraag opnieuw te beslissen welke regel geldt, en dat
# is precies waar het bij indefinido tegenover imperfecto misgaat.
#
# Dus: je kiest de lengte, de app kiest de spreiding. Hoogstens acht vragen per onderwerp in een
# sessie, de rest van je vragen gaat naar andere onderwerpen.
#
# WAAROM DIT WEL MEETELT EN DE DRILL NIET
#
# De bestaande drill (GC_DRILL_VRAGEN) telt met opzet niet mee voor je doosje: hij kwam na een
# misser, in dezelfde sessie, en wat je direct na een uitleg goed doet meet of je het net gelezen
# hebt. De oefensessie is iets anders: je kiest hem zelf, hij begint niet met een uitleg, en sinds
# v23.259 valt het oordeel pas na vijf antwoorden met een drempel van 75 procent. Daarmee is het
# betrouwbaar genoeg om te mogen tellen. Een doosje kan nog steeds hoogstens een stap per dag
# omhoog (v23.225), dus een lange sessie koopt geen trap.
import io, os, sys

P = os.path.expanduser("~/mnt/espanol/index.html")
s = io.open(P, encoding="utf-8").read()

if "gcSessieBouw" in s:
    print("al gepatcht")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global s
    assert s.count(anker) == n, "anker %d keer gevonden, verwacht %d: %r" % (s.count(anker), n, anker[:70])
    s = s.replace(anker, nieuw)


# ---------------------------------------------------------------- 1. de bouwer

SESSIE = '''/* ================= DE OEFENSESSIE (v23.260) =================

   Stefan: "wil ik echt oefenen dan wil ik er veel meer achter elkaar oefenen, 10 of 20 of 50."

   Hij krijgt zijn aantal, maar niet allemaal over hetzelfde onderwerp. Rohrer, Dedrick en Stershic
   (2015): dezelfde oefenstof gebundeld per soort tegenover door elkaar, getoetst een maand later,
   38 procent tegen 72. Door elkaar dwingt je per vraag opnieuw te kiezen welke regel geldt, en dat
   is precies wat er bij indefinido tegenover imperfecto misgaat.

   Hoogstens GC_SESSIE_PER_ONDERWERP vragen per onderwerp, want daarboven koop je overlearning:
   Rohrer en Taylor (2006) zagen dat voordeel binnen vier weken verdampen.

   De volgorde van de onderwerpen is die van de wachtrij (zwakste en langst vervallen eerst), met
   de rest van de open onderwerpen erachter zodat een lange sessie ook aan nieuwe stof toekomt. */
var GC_SESSIE_LENGTES = [10, 20, 40];
var GC_SESSIE_PER_ONDERWERP = 8;
function gcSessieId(n){ return "sessie-" + n; }
/* De onderwerpen van een sessie: eerst wat toe is, dan de rest van wat open staat. Alleen
   onderwerpen die ook echt vragen kunnen maken; een concept zonder patronen levert niets en hoort
   dan ook geen plek in de rij te krijgen. */
function gcSessieOnderwerpen(){
  var gehad = {}, uit = [];
  try {
    gramWachtrij().forEach(function(x){
      var id = x && x.c && x.c.id;
      if(!id || gehad[id]) return;
      gehad[id] = 1; uit.push(id);
    });
  } catch(e){}
  try {
    gcGeordend().forEach(function(c){
      if(gehad[c.id] || !gcConceptOpen(c.id)) return;
      gehad[c.id] = 1; uit.push(c.id);
    });
  } catch(e){}
  return uit;
}
function gcSessieBouw(id){
  var n = parseInt(String(id || "").replace(/^sessie-/, ""), 10);
  if(!n || isNaN(n)) return null;
  var ids = gcSessieOnderwerpen();
  if(!ids.length) return null;
  /* Per onderwerp een voorraadje vragen klaarzetten, en daarna om en om uitdelen. Andersom (per
     beurt een vraag maken) zou elk patroon opnieuw kunnen trekken en dus dubbelen opleveren;
     gcMaakVragen() houdt binnen een aanroep zelf bij wat er al gevraagd is. */
  var perOnderwerp = Math.min(GC_SESSIE_PER_ONDERWERP, Math.max(1, Math.ceil(n / ids.length) + 1));
  var potten = [];
  ids.forEach(function(cid){
    var c = gcConcept(cid);
    if(!c) return;
    var vr = [];
    try { vr = gcMaakVragen(c, perOnderwerp) || []; } catch(e){ vr = []; }
    // de vraag draagt zijn eigen onderwerp mee: in een sessie is dat niet af te leiden uit o
    vr.forEach(function(q){ q.cid = cid; });
    if(vr.length) potten.push(vr);
  });
  if(!potten.length) return null;
  var vragen = [], ronde = 0;
  while(vragen.length < n){
    var gaf = false;
    for(var i = 0; i < potten.length && vragen.length < n; i++){
      if(potten[i].length > ronde){ vragen.push(potten[i][ronde]); gaf = true; }
    }
    if(!gaf) break;   // alles uitgedeeld, ook al waren het er minder dan gevraagd
    ronde++;
  }
  if(vragen.length < 2) return null;
  var namen = {};
  vragen.forEach(function(q){ namen[q.cid] = 1; });
  var aantalOnderwerpen = Object.keys(namen).length;
  return {
    id: id, concept: null, sessie: true, icon: "\\ud83c\\udfaf", drill: null,
    titel: "Oefensessie", titelEn: "Practice run",
    pitch: vragen.length + " vragen over " + aantalOnderwerpen + " onderwerpen, door elkaar",
    pitchEn: vragen.length + " questions across " + aantalOnderwerpen + " topics, mixed",
    stappen: [{
      kop: vragen.length + " vragen, door elkaar",
      kopEn: vragen.length + " questions, mixed",
      uitleg: "", uitlegEn: "",
      vragen: vragen
    }]
  };
}
/* Waar stonden de doosjes toen deze sessie begon? Zonder deze foto kan het slotscherm niet zeggen
   wat er met je kaart gebeurd is, en dat is het enige wat van een sessie overblijft. */
function gcSessieFoto(){
  var uit = {};
  gcSessieOnderwerpen().forEach(function(cid){
    try { uit[cid] = gramLees(cid).box || 0; } catch(e){ uit[cid] = 0; }
  });
  return uit;
}
function gcSessieStart(n){
  gwStart(gcSessieId(n), 0);
  if(gwSess){ gwSess.voorBox = gcSessieFoto(); renderCheat(); }
}
/* Het slotscherm: niet je score maar wat er met je kaart gebeurde. Een doos omlaag is geen straf
   maar een afspraak om het vaker terug te zien, en zo hoort het er ook te staan. */
function gcSessieSlotHtml(){
  var voor = (gwSess && gwSess.voorBox) || null;
  if(!voor) return "";
  var op = [], blijft = [], neer = [];
  Object.keys(voor).forEach(function(cid){
    var nu = 0;
    try { nu = gramLees(cid).box || 0; } catch(e){ nu = 0; }
    var c = gcConcept(cid);
    if(!c) return;
    var naam = ct(c.naam, c.naamEn);
    if(nu > voor[cid]) op.push(naam + " \\u2192 " + nu);
    else if(nu < voor[cid]) neer.push(naam + " \\u2192 " + nu);
  });
  /* "blijft staan" telt alleen de onderwerpen die je deze sessie ook echt gehad hebt, en dat weet
     de vragenlijst en niet de foto: de foto staat over alle openstaande onderwerpen, ook die waar
     deze sessie niet aan toekwam. */
  var gehad = {};
  try {
    var o = gwOnderwerp(gwSess.id);
    (o.stappen[0].vragen || []).forEach(function(q){ if(q && q.cid) gehad[q.cid] = 1; });
  } catch(e){}
  blijft = Object.keys(gehad).filter(function(cid){
    var nu = 0;
    try { nu = gramLees(cid).box || 0; } catch(e){ nu = 0; }
    return nu === voor[cid] && gcConcept(cid);
  }).map(function(cid){ var c = gcConcept(cid); return ct(c.naam, c.naamEn); });
  var regel = function(kleur, kop, rij){
    if(!rij.length) return "";
    return "<p style='margin:6px 0 0; font-size:.88rem'><b style='color:" + kleur + "'>" + kop +
      "</b> <span class='muted'>" + rij.join(" \\u00b7 ") + "</span></p>";
  };
  return "<div style='margin-top:10px'>" +
    "<p style='margin:0'><b>" + ct("Wat er met je kaart gebeurde", "What happened to your map") + "</b></p>" +
    regel("var(--green)", ct("Een doos omhoog:", "A box up:"), op) +
    regel("var(--muted)", ct("Blijft staan:", "Unchanged:"), blijft) +
    regel("var(--accent)", ct("Een doos omlaag, komt vaker terug:", "A box down, comes back sooner:"), neer) +
    (op.length || neer.length ? "" :
      "<p class='muted' style='margin:6px 0 0; font-size:.85rem'>" +
      ct("Nog niets verschoven: een doosje beweegt pas na vijf antwoorden op hetzelfde onderwerp.",
         "Nothing moved yet: a box only shifts after five answers on the same topic.") + "</p>") +
    "</div>";
}

'''

rep("function gcOpfrisBouw(id){", SESSIE + "function gcOpfrisBouw(id){")

# de bouwer registreren
OUD_B = '''  {pre: "drill-",   bouw: function(id){ return gcDrillBouw(id); }}
];'''
NIEUW_B = '''  {pre: "drill-",   bouw: function(id){ return gcDrillBouw(id); }},
  // v23.260: de oefensessie. Eén stap met vragen van verschillende onderwerpen door elkaar.
  {pre: "sessie-",  bouw: function(id){ return gcSessieBouw(id); }}
];'''
rep(OUD_B, NIEUW_B)

# ---------------------------------------------------------------- 2. de vraag draagt zijn onderwerp

OUD_A = '''  if(stap && stap.brok){ brokBij(stap.brok, goed); return; }
  if(!o || !o.concept) return;'''
NIEUW_A = '''  if(stap && stap.brok){ brokBij(stap.brok, goed); return; }
  /* v23.260: in een oefensessie staan vragen van verschillende onderwerpen door elkaar, dus het
     onderwerp kan niet meer uit o komen. Draagt de vraag er een, dan telt die; dat is dezelfde
     afspraak als bij q.pi hieronder (v23.228). Buiten een sessie draagt geen enkele vraag een cid
     en verandert er dus niets. */
  var cidQ = (q && q.cid) || (o && o.concept);
  if(!cidQ) return;'''
rep(OUD_A, NIEUW_A)

OUD_A2 = '''  gramBij(o.concept, goed, (q && q.o) ? q.o.length : 0,
          (q && typeof q.pi === "number") ? q.pi : null, gwKanaal(o));'''
NIEUW_A2 = '''  gramBij(cidQ, goed, (q && q.o) ? q.o.length : 0,
          (q && typeof q.pi === "number") ? q.pi : null, gwKanaal(o));'''
rep(OUD_A2, NIEUW_A2)

rep('function gwKanaal(o){ return o && o.opfris ? "opfris" : "microles"; }',
    'function gwKanaal(o){ return o && o.sessie ? "sessie" : (o && o.opfris ? "opfris" : "microles"); }')

# ---------------------------------------------------------------- 3. het slotscherm

OUD_S = '''      (perfect ? "" : (o.concept && !o.drill'''
NIEUW_S = '''      (o.sessie ? gcSessieSlotHtml() : "")+
      (perfect ? "" : (o.concept && !o.drill'''
rep(OUD_S, NIEUW_S)

# ---------------------------------------------------------------- 4. de knoppen op de tab

OUD_K = """    gcStandHtml() +"""
NIEUW_K = """    gcStandHtml() +
    /* v23.260: de oefensessie. Hij staat boven de route, want dit is wat je doet als je echt wilt
       oefenen; de route eronder is waar je kijkt hoe het ervoor staat. */
    "<p style='margin:14px 0 4px'><b>" + ct("Even echt oefenen", "A real practice run") + "</b> <span class='muted'>\\u00b7 " +
      ct("vragen door elkaar uit je openstaande onderwerpen, en ze tellen mee",
         "questions mixed across your open topics, and they count") + "</span></p>" +
    "<div class='row'>" + GC_SESSIE_LENGTES.map(function(n){
      return "<button type='button' class='ghost' data-gcsessie='" + n + "'>" + n + " " + ct("vragen", "questions") + "</button>";
    }).join("") + "</div>" +"""
rep(OUD_K, NIEUW_K)

OUD_W = '''  el.querySelectorAll("[data-gckies]").forEach(function(d){'''
NIEUW_W = '''  el.querySelectorAll("[data-gcsessie]").forEach(function(d){
    d.onclick = function(){ gcSessieStart(+d.getAttribute("data-gcsessie")); };
  });
  el.querySelectorAll("[data-gckies]").forEach(function(d){'''
rep(OUD_W, NIEUW_W)

io.open(P, "w", encoding="utf-8").write(s)
print("gepatcht:", P)
