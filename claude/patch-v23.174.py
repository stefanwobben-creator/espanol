#!/usr/bin/env python3
# v23.174 - de nulmeting: een koude schrijftaak per week, met een fout-identiteit
#
# Stefan, 22 aug: "nou beide, nulmeting en dan de nachtrun."
#
# WAAROM DIT EERST KOMT
#
# De leerkaart van de zinstap zet twee getallen op 5 september, en het tweede daarvan is "het
# aandeel tijdfouten in de wekelijkse schrijftaak daalt". Die schrijftaak bestaat niet. Zonder hem
# is het volgende oordeel over de zinstap weer een vermoeden, en dat is precies de lus waar de
# leerpoort voor bedoeld is. Dus eerst de meter, dan de motor.
#
# De vorm ligt al vast in de leerkaart van de correctielaag, veld 6: "Eén wekelijkse koude
# schrijftaak waar géén feedback op komt, met een echte fout-identiteit (lemma plus foutcategorie
# plus doelvorm). Dat is het equivalent van de nieuwe-tekst-taak bij Truscott & Hsu, en het is het
# enige dat het verschil tussen repareren en kunnen kan zien."
#
# DRIE ONTWERPBESLUITEN, EN WAAROM
#
# 1. KOUD BETEKENT KOUD. Je krijgt geen correctie te zien. Dat voelt gek en het is het hele punt:
#    zodra je de verbetering terugkrijgt, meet de week erna niet meer wat je kunt maar wat je van
#    die verbetering hebt onthouden. De taak levert ook niets aan de herhaalwachtrij, zet niets in
#    S.errors, raakt geen doosje aan en telt niet mee in dagStats. Dat laatste is niet netheid maar
#    noodzaak: de weekmeting rekent haar foutpercentage uit dagStats, dus een schrijftaak die daarin
#    landt vervuilt de reeks die hij zelf moet meten.
#
# 2. DE TEKST WORDT BEWAARD, NIET ALLEEN HET OORDEEL. De beoordelingsprompt op de server ís het
#    meetinstrument. Verandert die prompt, dan verandert de meting, en dan is de reeks gebroken.
#    Daarom draagt elke meting het nummer van de prompt waarmee hij beoordeeld is (pv), en staat de
#    tekst zelf erbij, zodat oude weken opnieuw beoordeeld kunnen worden met een nieuwe prompt en de
#    reeks alsnog vergelijkbaar blijft. Zestig woorden per week kost niets in opslag.
#
# 3. DE OPDRACHT DWINGT VERLEDEN TIJD AF. "Vertel over je dag" laat zich in het presente schrijven,
#    en dan ziet de meter geen enkele tijdfout omdat er geen tijd te kiezen viel. Zes vaste
#    opdrachten, gekozen op weeknummer, dus ze keren elke zes weken terug en dan is week 1 met week
#    7 te vergelijken.
#
# WAT ER ONDERWEG STUK BLEEK
#
# mengMeting() verving bij een sync de hele weekregel zodra de andere kant een hogere `stevig` had.
# Dat wist de schrijftaak van die week uit op elk apparaat dat toevallig achterliep. Nu wordt er per
# veld samengevoegd en blijft een schrijftaak staan.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
SRV = W / "server" / "index.js"
VER = W / "versie.txt"
NIEUW = "v23.174"

src = APP.read_text(encoding="utf-8")
srv = SRV.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_SRV = "ai-meting" not in srv
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

def srep(anker, nieuw, n=1):
    global srv
    c = srv.count(anker)
    assert c == n, "server-anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    srv = srv.replace(anker, nieuw, n)

# ---------------------------------------------------------------- 1. het tabblad
if DOE_APP:
    rep(
        '  <section id="tab-chat" class="hidden">\n    <div id="chatWrap"></div>\n  </section>',
        '  <section id="tab-chat" class="hidden">\n    <div id="chatWrap"></div>\n  </section>\n'
        '\n'
        '  <!-- DE WEEKMETING (v23.174): een koude schrijftaak, één keer per week, zonder correctie. -->\n'
        '  <section id="tab-meting" class="hidden">\n    <div id="metingWrap"></div>\n  </section>',
    )

    rep(
        '  {id:"chat", label:"Praten met Chispa", nav:false},   // v23.144',
        '  {id:"chat", label:"Praten met Chispa", nav:false},   // v23.144\n'
        '  {id:"meting", label:"De weekmeting", nav:false},     // v23.174',
    )

    rep(
        '  if(tabId==="chat"){ renderChat(); }',
        '  if(tabId==="chat"){ renderChat(); }\n'
        '  if(tabId==="meting"){ renderMeting(); }',
    )

# ---------------------------------------------------------------- 2. de sync-reparatie
if DOE_APP:
    rep(
        '  for(var w in voor){\n'
        '    if(!S.meting[w] || (voor[w].stevig || 0) > (S.meting[w].stevig || 0)) S.meting[w] = voor[w];\n'
        '  }',
        '  /* v23.174: per veld samenvoegen in plaats van de hele regel vervangen.\n'
        '     Hier stond: is `stevig` aan de andere kant hoger, neem dan die hele weekregel over. Dat\n'
        '     klopte zolang een weekregel alleen tellers bevatte, want die lopen binnen een week alleen\n'
        '     op. De schrijftaak is geen teller: hij staat op één apparaat en op geen enkel ander, dus\n'
        '     een pull vanaf een apparaat dat toevallig een hogere woordenstand had wiste hem uit. Een\n'
        '     meting die door een sync kan verdwijnen is geen meting. */\n'
        '  for(var w in voor){\n'
        '    var bin = voor[w] || {}, hier = S.meting[w];\n'
        '    if(!hier){ S.meting[w] = bin; continue; }\n'
        '    if((bin.stevig || 0) > (hier.stevig || 0)){\n'
        '      var schrijfHier = hier.schrijf;\n'
        '      S.meting[w] = bin;\n'
        '      if(schrijfHier && !bin.schrijf) S.meting[w].schrijf = schrijfHier;\n'
        '    } else if(bin.schrijf && !hier.schrijf){\n'
        '      hier.schrijf = bin.schrijf;\n'
        '    }\n'
        '  }',
    )

# ---------------------------------------------------------------- 3. de meting zelf
MEET = r'''
/* ================= DE NULMETING (v23.174) =================

   Eén keer per week schrijf je een korte tekst zonder hulp, en je krijgt er geen correctie op.

   Waarom geen correctie: dit is het equivalent van de nieuwe-tekst-taak bij Truscott & Hsu 2008.
   Zodra je de verbetering terugziet, meet de week erna niet meer wat je kunt maar wat je van die
   verbetering hebt onthouden, en dan kan niemand ooit nog zeggen of de oefeningen werken. Alles wat
   je hier schrijft wordt geteld en verder met rust gelaten: geen XP voor goed, geen doosje, geen
   foutenlogboek, geen wachtrij, en niets in dagStats. Dat laatste is geen netheid maar noodzaak, want
   de weekmeting rekent haar eigen foutpercentage uit dagStats.

   Er is één beloning, en die hangt aan het dóén: je krijgt XP voor het inleveren, ongeacht hoe goed
   het was. Een meting die je beter beloont naarmate je beter schrijft, nodigt uit om voorzichtig te
   schrijven, en voorzichtig schrijven is precies wat de meting niet moet meten. */
var MEET_PROMPT_V = 1;   /* het nummer van de beoordelingsprompt op de server. De prompt ÍS het
                            meetinstrument: verandert hij, dan verandert de meting. Elke meting
                            draagt daarom het nummer waarmee hij beoordeeld is, en de tekst zelf,
                            zodat oude weken opnieuw te beoordelen zijn als dit nummer opschuift. */
var MEET_CATS = ["tijd","persoon","geslacht","serestar","voorzetsel","woordkeuze","spelling","volgorde","overig"];
var MEET_CAT_NL = {tijd:"tijd", persoon:"persoonsvorm", geslacht:"geslacht", serestar:"ser of estar",
  voorzetsel:"voorzetsel", woordkeuze:"woordkeuze", spelling:"spelling", volgorde:"woordvolgorde",
  overig:"overig"};
/* Vijftig woorden, ongeveer vijf zinnen en vijf minuten. Lager kan niet: bij 35 woorden staan er
   zes werkwoorden in en springt "tijdfouten per honderd woorden" in stappen van drie, en dan meet
   je ruis. Hoger wil ik niet, want een taak die je overslaat meet helemaal niets. */
var MEET_WOORDEN_MIN = 50;
/* Zes opdrachten die alle zes een verleden tijd afdwingen. "Vertel over je dag" laat zich netjes in
   het presente schrijven, en dan meet de meter nul tijdfouten omdat er geen tijd te kiezen viel.
   Gekozen op weeknummer, dus ze keren elke zes weken terug: week 1 is dan met week 7 te vergelijken
   in plaats van met een andere opdracht. */
var MEET_TAKEN = [
  {id:"gisteren", nl:"Vertel wat je gisteren hebt gedaan, van opstaan tot naar bed gaan.",
   en:"Tell what you did yesterday, from getting up to going to bed."},
  {id:"uiteten", nl:"Vertel over de laatste keer dat je uit eten ging. Waar was het, met wie, wat at je?",
   en:"Tell about the last time you ate out. Where was it, who with, what did you eat?"},
  {id:"vakantie", nl:"Vertel over een reis die je ooit hebt gemaakt. Waar ging je heen en wat gebeurde er?",
   en:"Tell about a trip you once made. Where did you go and what happened?"},
  {id:"weekend", nl:"Vertel wat je afgelopen weekend hebt gedaan.",
   en:"Tell what you did last weekend."},
  {id:"vroeger", nl:"Vertel hoe het vroeger bij jou thuis ging toen je klein was.",
   en:"Tell how things were at your house when you were little."},
  {id:"misging", nl:"Vertel over een keer dat er iets misging. Wat gebeurde er en hoe liep het af?",
   en:"Tell about a time something went wrong. What happened and how did it end?"}
];
var meetBezig = false, meetKlaarNu = false;

function meetWeek(){ return isoWeek(today()); }
function meetTaakVanWeek(w){
  var n = parseInt(String(w || meetWeek()).split("-W")[1], 10);
  if(!(n > 0)) n = 1;
  return MEET_TAKEN[n % MEET_TAKEN.length];
}
function meetGedaan(w){
  var m = (S.meting || {})[w || meetWeek()];
  return !!(m && m.schrijf);
}
function meetOpen(){ return !meetGedaan(); }
function meetWoorden(t){
  return String(t || "").trim().split(/\s+/).filter(function(x){ return x.length; }).length;
}
function meetZinnen(t){
  return String(t || "").split(/[.!?…]+/).filter(function(x){ return x.trim().length > 1; }).length;
}
/* Alle metingen op volgorde, alleen de weken waarin echt geschreven is. */
function meetReeks(){
  var uit = [];
  Object.keys(S.meting || {}).sort().forEach(function(w){
    var m = S.meting[w];
    if(m && m.schrijf && m.schrijf.n) uit.push({w:w, s:m.schrijf});
  });
  return uit;
}
/* Het getal waar het om gaat: tijdfouten per honderd woorden. Per honderd woorden en niet als
   percentage van je fouten, want dat tweede daalt ook als je andere fouten toenemen. */
function meetTijdPer100(s){
  if(!s || !s.n) return null;
  return Math.round(((s.per && s.per.tijd || 0) / s.n) * 1000) / 10;
}

function renderMeting(){
  var el = document.getElementById("metingWrap");
  if(!el) return;
  var taak = meetTaakVanWeek();
  if(meetKlaarNu){
    el.innerHTML =
      "<div class='card'>" +
      "<h2 style='margin:0 0 6px'>" + ct("Opgeslagen","Saved") + "</h2>" +
      "<p class='muted' style='margin:0 0 10px'>" +
      ct("Hier komt geen correctie op, en dat is met opzet. Zou je hem terugkrijgen, dan meet volgende week niet meer wat je kunt maar wat je van die correctie hebt onthouden. De reeks staat bij Voortgang zodra er drie metingen liggen.",
         "You get no corrections here, and that is on purpose. If you did, next week would measure what you remembered of the correction instead of what you can do. The series shows up under Progress once there are three measurements.") +
      "</p>" +
      "<button class='btn' id='btnMeetVerder'>" + ct("Verder","Continue") + "</button>" +
      "</div>";
    var bv = document.getElementById("btnMeetVerder");
    if(bv) bv.onclick = function(){
      meetKlaarNu = false;
      if(lesFlow) lesFlowVolgende(); else show("lessen");
    };
    return;
  }
  var bewaard = "";
  try { bewaard = (meetConcept() || ""); } catch(e){ bewaard = ""; }
  el.innerHTML =
    "<div class='card'>" +
    "<h2 style='margin:0 0 2px'>" + ct("De weekmeting","The weekly measurement") + "</h2>" +
    "<p class='muted' style='margin:0 0 10px; font-size:.9rem'>" +
    ct("Eén keer per week, zonder hulp en zonder correctie. Dit is geen oefening: het is de enige plek waar te zien is of de oefeningen iets doen.",
       "Once a week, no help and no corrections. This is not an exercise: it is the only place where you can see whether the exercises do anything.") +
    "</p>" +
    "<p style='margin:0 0 8px'><b>" + (profLang() === "nl" ? taak.nl : taak.en) + "</b></p>" +
    "<textarea id='meetInp' rows='7' style='width:100%; padding:10px; font-size:1rem' " +
    "placeholder='" + ct("Schrijf in het Spaans...","Write in Spanish...") + "'>" + bewaard + "</textarea>" +
    "<div class='muted' id='meetTel' style='margin:6px 0 10px; font-size:.85rem'></div>" +
    "<button class='btn' id='btnMeetKlaar'" + (meetBezig ? " disabled" : "") + ">" +
    (meetBezig ? ct("Bezig...","Working...") : ct("Inleveren","Hand in")) + "</button>" +
    "</div>";
  var inp = document.getElementById("meetInp");
  var tel = function(){
    var n = meetWoorden(inp ? inp.value : "");
    var t = document.getElementById("meetTel");
    if(t) t.textContent = n < MEET_WOORDEN_MIN
      ? ct("nog " + (MEET_WOORDEN_MIN - n) + " woorden te gaan", (MEET_WOORDEN_MIN - n) + " words to go")
      : ct(n + " woorden", n + " words");
    var b = document.getElementById("btnMeetKlaar");
    if(b) b.disabled = meetBezig || n < MEET_WOORDEN_MIN;
  };
  if(inp){
    inp.oninput = function(){ tel(); meetConceptZet(inp.value); };
    tel();
  }
  var bk = document.getElementById("btnMeetKlaar");
  if(bk) bk.onclick = meetVerstuur;
}
/* Een halve tekst mag niet weg zijn als je per ongeluk wegklikt. Los van S.meting, want dit is nog
   geen meting. */
function meetConcept(){ return (S.meetConcept && S.meetConcept.w === meetWeek()) ? S.meetConcept.t : ""; }
function meetConceptZet(t){ S.meetConcept = {w:meetWeek(), t:String(t || "").slice(0, 2000)}; }

function meetVerstuur(){
  var inp = document.getElementById("meetInp");
  var tekst = String(inp ? inp.value : "").trim();
  if(meetWoorden(tekst) < MEET_WOORDEN_MIN || meetBezig) return;
  meetBezig = true;
  renderMeting();
  var taak = meetTaakVanWeek();
  api("/api/ai/meting", "POST", {tekst:tekst, taak:(taak.nl + " (" + taak.id + ")"), niveau:chatNiveau()})
    .then(function(r){
      meetBewaar(tekst, taak, r);
      meetBezig = false; meetKlaarNu = true;
      renderMeting();
    });
}
/* Ook als de server niets teruggeeft wordt de meting bewaard, met ok:false erbij. De tekst is dan
   nog steeds bruikbaar: hij kan later alsnog beoordeeld worden. Wat niet mag gebeuren is dat een
   kapotte verbinding de week stilletjes overslaat en de reeks een gat krijgt dat niemand ziet. */
function meetBewaar(tekst, taak, r){
  var w = meetWeek();
  try { snapshotSchrijf(); } catch(e){}
  S.meting = S.meting || {};
  if(!S.meting[w]) S.meting[w] = {d:today()};
  var rauw = (r && Array.isArray(r.fouten)) ? r.fouten : [];
  var fouten = rauw.slice(0, 40).map(function(f){
    var c = String((f && f.cat) || "overig");
    if(MEET_CATS.indexOf(c) === -1) c = "overig";
    return {l:String((f && f.lemma) || "").slice(0, 24), c:c,
            g:String((f && f.gegeven) || "").slice(0, 40),
            d:String((f && f.doel) || "").slice(0, 40)};
  });
  var per = {};
  fouten.forEach(function(f){ per[f.c] = (per[f.c] || 0) + 1; });
  S.meting[w].schrijf = {
    taak: taak.id, dag: today(), pv: MEET_PROMPT_V, ok: !!(r && Array.isArray(r.fouten)),
    n: meetWoorden(tekst), z: meetZinnen(tekst),
    tekst: String(tekst).slice(0, 1200),
    f: fouten, per: per
  };
  delete S.meetConcept;
  /* XP voor het doen, niet voor het resultaat. Zie de kop van dit blok. */
  try { addXP(15); } catch(e){}
  try { persist(); } catch(e){}
}

/* De reeks op het Voortgangscherm. Pas vanaf drie metingen, want met twee punten is elk verschil
   toeval; dezelfde regel als bij de band en de voorspeller. */
function vgMetingHtml(){
  var r = meetReeks();
  if(r.length < 3) return "";
  var rijen = r.slice(-10).map(function(x){
    var t = meetTijdPer100(x.s);
    var tot = 0;
    Object.keys(x.s.per || {}).forEach(function(k){ tot += x.s.per[k]; });
    return "<tr><td class='muted' style='font-size:.85rem'>" + x.w + "</td>" +
      "<td>" + x.s.n + "</td><td>" + tot + "</td><td><b>" + (t === null ? "-" : t) + "</b></td></tr>";
  }).join("");
  return "<div class='card'>" +
    "<h2 style='margin:0 0 2px'>" + ct("De weekmeting","The weekly measurement") + "</h2>" +
    "<p class='muted' style='margin:0 0 8px; font-size:.85rem'>" +
    ct("Uit je koude schrijftaak, zonder hulp en zonder correctie. De laatste kolom is het getal dat ertoe doet: tijdfouten per honderd woorden.",
       "From your cold writing task, no help and no corrections. The last column is the number that matters: tense errors per hundred words.") +
    "</p><table style='width:100%'><tr><th class='muted' style='text-align:left; font-size:.8rem'>" +
    ct("week","week") + "</th><th class='muted' style='text-align:left; font-size:.8rem'>" +
    ct("woorden","words") + "</th><th class='muted' style='text-align:left; font-size:.8rem'>" +
    ct("fouten","errors") + "</th><th class='muted' style='text-align:left; font-size:.8rem'>" +
    ct("tijd/100","tense/100") + "</th></tr>" + rijen + "</table></div>";
}
'''

if DOE_APP:
    rep(
        "function renderVoortgang(){",
        MEET.strip("\n") + "\n\nfunction renderVoortgang(){",
    )
    rep(
        "    vgSterkHtml() +\n    vgZwakHtml();",
        "    vgSterkHtml() +\n    vgZwakHtml() +\n    vgMetingHtml();",
    )

# ---------------------------------------------------------------- 4. in de dagles
if DOE_APP:
    rep(
        '  if(praat){\n'
        '    blokken.push({stap:"produceren", naam:ct("Praten met Chispa","Talking with Chispa"),',
        '  /* v23.174: één keer per week neemt de weekmeting de plaats van het productieblok in. Geen\n'
        '     nieuwe kaart op Vandaag en geen langere les: de meting IS het produceren van die dag, en\n'
        '     dat klopt ook inhoudelijk, want een koude schrijftaak is de zuiverste productie die er is. */\n'
        '  if(meetOpen()){\n'
        '    blokken.push({stap:"produceren", naam:ct("De weekmeting","The weekly measurement"),\n'
        '      draad:ct("zelf maken","output"), wat:ct("een korte tekst, zonder hulp","a short text, no help"),\n'
        '      sec:5 * 60, vaardigheid:"meting"});\n'
        '  } else if(praat){\n'
        '    blokken.push({stap:"produceren", naam:ct("Praten met Chispa","Talking with Chispa"),',
    )
    rep(
        '  var v = lesFlow.vaardigheid;\n'
        '  var tijd = vaardigheidTijd();\n'
        '  if(v === "praten"){   // v23.150',
        '  var v = lesFlow.vaardigheid;\n'
        '  var tijd = vaardigheidTijd();\n'
        '  if(v === "meting"){   // v23.174\n'
        '    lesFlow.gekozenSpel = "meting";\n'
        '    meetKlaarNu = false;\n'
        '    show("meting");\n'
        '    return;\n'
        '  }\n'
        '  if(v === "praten"){   // v23.150',
    )
    rep(
        '  if(f.stap === "produceren" && f.vaardigheid === "praten") return ct("Praten","Talking");',
        '  if(f.stap === "produceren" && f.vaardigheid === "meting") return ct("De weekmeting","The measurement");\n'
        '  if(f.stap === "produceren" && f.vaardigheid === "praten") return ct("Praten","Talking");',
    )

# ---------------------------------------------------------------- 5. de server
SRV_EP = r'''
/* POST /api/ai/meting  (v23.174)
   {tekst, taak, niveau} -> {fouten:[{lemma, cat, gegeven, doel}], pv}

   Dit eindpunt is een meetinstrument en geen docent. Het legt fouten vast met een identiteit
   (grondwoord + categorie + wat er stond + wat er had moeten staan) en stuurt geen enkele uitleg
   terug, want de app laat de leerling niets van deze beoordeling zien.

   DE PROMPT HIERONDER IS BEVROREN. Hij bepaalt wat er gemeten wordt, dus elke wijziging breekt de
   vergelijkbaarheid met alle eerdere weken. Verandert hij toch, dan gaat MEET_PROMPT_V in index.html
   omhoog; de app bewaart de tekst van elke week, dus oude weken zijn dan opnieuw te beoordelen. */
const MEET_CATS = ["tijd","persoon","geslacht","serestar","voorzetsel","woordkeuze","spelling","volgorde","overig"];
app.post("/api/ai/meting", async (req, res) => {
  const slot = aiSlot(req);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { tekst, taak, niveau } = req.body || {};
  if (!tekst || String(tekst).trim().length < 20) return bad(res, 400, "tekst verplicht");
  const niv = /^(a0|a1|a2|b1)$/i.test(String(niveau || "")) ? String(niveau).toUpperCase() : "A2";
  try {
    const txt = await vraagLadder(
      "Je bent een corrector die ALLEEN meet. Een Nederlandstalige leerling Spaans (niveau " + niv +
      ") heeft een korte tekst geschreven. Noem elke echte fout en verder niets: geen stijladvies, " +
      "geen mooiere formulering, geen compliment, geen uitleg. De leerling krijgt jouw antwoord niet " +
      "te zien; het gaat naar een teller.\n" +
      "Een fout is alleen een fout als een moedertaalspreker hem zou verbeteren. Twijfel je, dan is " +
      "het geen fout. Noem elke fout apart, ook als hetzelfde woord twee keer misgaat.\n" +
      "Kies per fout precies één categorie uit deze lijst: " + MEET_CATS.join(", ") + ".\n" +
      "tijd = de verkeerde werkwoordstijd gekozen (bijvoorbeeld indefinido waar imperfecto hoort).\n" +
      "persoon = de goede tijd maar de verkeerde persoonsuitgang.\n" +
      "geslacht = lidwoord of bijvoeglijk naamwoord past niet bij het zelfstandig naamwoord.\n" +
      "serestar = ser en estar verwisseld.\n" +
      "voorzetsel = het verkeerde voorzetsel, of er ontbreekt er een.\n" +
      "woordkeuze = een bestaand Spaans woord dat hier niet past.\n" +
      "spelling = verkeerd gespeld of een ontbrekend accent, terwijl de vorm verder klopt.\n" +
      "volgorde = de woorden staan in de verkeerde volgorde.\n" +
      "overig = alles wat in geen van deze categorieën past.\n" +
      "Antwoord UITSLUITEND met geldige JSON: {\"fouten\":[{\"lemma\":\"...\",\"cat\":\"...\"," +
      "\"gegeven\":\"...\",\"doel\":\"...\"}]}. lemma = het grondwoord (de infinitief bij een " +
      "werkwoord, het enkelvoud bij een zelfstandig naamwoord). gegeven = precies wat de leerling " +
      "schreef. doel = wat er had moeten staan. Geen enkele fout gevonden: {\"fouten\":[]}.",
      "De opdracht was: " + String(taak || "-").slice(0, 200) + "\n\nDe tekst van de leerling:\n" +
        String(tekst).slice(0, 1500),
      900, true, "ai-meting"
    );
    const m = txt.match(/\{[\s\S]*\}/);
    if (!m) return badReden(res, 502, "onleesbaar AI-antwoord", "stuk");
    const p = JSON.parse(m[0]);
    const rij = Array.isArray(p.fouten) ? p.fouten.slice(0, 40) : [];
    ok(res, { pv: 1, fouten: rij.map((f) => ({
      lemma: String((f && f.lemma) || "").slice(0, 24),
      cat: MEET_CATS.indexOf(String((f && f.cat) || "")) === -1 ? "overig" : String(f.cat),
      gegeven: String((f && f.gegeven) || "").slice(0, 40),
      doel: String((f && f.doel) || "").slice(0, 40)
    })) });
  } catch (e) {
    console.error(e);
    badReden(res, 502, "AI-fout", "stuk");
  }
});

// POST /api/ai/uitleg {vraag, context}'''

if DOE_SRV:
    srep("\n// POST /api/ai/uitleg {vraag, context}", SRV_EP)

# ---------------------------------------------------------------- schrijven
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar " + NIEUW)
else:
    print("index.html: stond al op " + NIEUW)

if DOE_SRV:
    SRV.write_text(srv, encoding="utf-8")
    print("server/index.js: /api/ai/meting toegevoegd")
else:
    print("server/index.js: /api/ai/meting stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
