#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.233 - de app leerde je vormen en nooit wat een tijd doet
#
# Stefan, 3 sep: "de grammatica is lastig want ik weet gewoon ook nog niet zo goed wat presente, de
# subjuntivo, aanvoegende wijs, verleden tijd enzo allemaal is. Dus die basisregel ken ik nog niet,
# maar ik moet direct ook nog het juiste woord erbij kiezen, dus ik heb het idee dat dat heel
# langzaam gaat en je oplossingen zijn iedere keer kleine tweaks maar ik heb niet echt het gevoel
# dat ik door de oefeningen het beter word."
#
# HIJ HEEFT GELIJK, EN HET STAAT IN ZIJN EIGEN CIJFERS
#
# Uit tools/logs-latest.json, tien opnames van zijn profiel (txp 19381 tot 20937). Verdeling van
# zijn 25 grammatica-onderwerpen over de doosjes:
#
#     doos 0  ######    6
#     doos 1  #######   7
#     doos 2  ###       3
#     doos 3            0
#     doos 4            0
#     doos 5  ######### 9
#
# Het midden is leeg. Er is geen enkel onderwerp dat ONDERWEG is. Je kunt het al (negen op doos 5,
# daar sinds het begin) of je zit onderaan (zestien op 0, 1 of 2). Wat hij beschrijft als "ik word
# er niet beter van" is precies deze vorm: er is geen zichtbare weg van beneden naar boven.
#
# En hij werd in dit venster wél beter, alleen zag hij dat nergens:
#
#     muymucho      75% goed (9 van de 12)   doos 3 -> 0
#     genero        62% goed (5 van de 8)    doos 2 -> 0
#     over alles    70% goed (26 van de 37)
#
# WAT ER MIST, EN HET IS GEEN TWEAK
#
# De app heeft een hele machine voor VORMEN: zes patroonrijen per tijd, een doosje per patroon, de
# les in zes stappen, drills. Alles daarin beantwoordt de vraag "hoe maak je estuve". Nergens staat
# het antwoord op de vraag die daarvóór komt: WAT DOET EEN TIJD MET DE BETEKENIS, en wanneer grijpt
# een Spanjaard naar de ene en niet naar de andere.
#
# Van de 46 spiekbrieven gaat er geen enkele over de tijden als geheel. Er is "Presente: welk
# rijtje?" en "Pretérito perfecto: haber + participio": allebei recepten voor de vorm. De les
# begint dus bij stap 4 van de ladder, en Stefan staat op stap 0.
#
# WAT ER NU STAAT
#
# 1. DE KAART VAN DE TIJDEN. Eén scherm, in gewone taal, zonder één vervoegingstabel. Wat een tijd
#    is, welke zes deze app gebruikt, wat elk doet, waaraan je hem herkent, en de drie keuzes waar
#    het echt om gaat (af of niet af, afgesloten of lopend tijdvak, feit of wens). De voorbeelden
#    zijn NEDERLANDS, want de vraag "welke tijd" kun je in het Nederlands al stellen en beantwoorden,
#    en dan hoef je maar één ding tegelijk te doen. Het Spaanse voorbeeld staat erbij als illustratie
#    en niet als opgave.
#
# 2. JE SCORE NAAST DE DOOS. Op de route stond "doos 0/5", en meer niet. Nu staat er ook hoe je het
#    de afgelopen week deed: "doos 0/5 · 75% goed deze week". De doosregel zelf blijft ongemoeid
#    (Stefan wees het zachter maken in v23.208 af en houdt daaraan vast), maar de app zegt er nu bij
#    wat hij ook weet. S.gramLog ligt er sinds v23.211 en werd tot nu toe alleen door de suite
#    gelezen: het venster is nu open.
#
#    Nul is geen bericht: onder de drie beurten staat er niets, want 1 van de 1 is geen percentage.
import io, pathlib, re

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.233"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()


def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]


DOE_APP = "function tijdenKaartHtml(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # =========================================================================================
    # 1. de kaart van de tijden
    # =========================================================================================
    rep("""var gcLeesId = null;""",
"""var gcLeesId = null;
/* ================= DE KAART VAN DE TIJDEN (v23.233) =================

   Stefan: "ik weet gewoon ook nog niet zo goed wat presente, de subjuntivo, aanvoegende wijs,
   verleden tijd enzo allemaal is. Dus die basisregel ken ik nog niet, maar ik moet direct ook nog
   het juiste woord erbij kiezen."

   Twee dingen tegelijk, en het eerste stond nergens uitgelegd. De app heeft een hele machine voor
   VORMEN (zes patroonrijen per tijd, een doosje per patroon, de les in stappen) en van de 46
   spiekbrieven gaat er geen enkele over wat een tijd DOET.

   Daarom staan de voorbeelden hieronder in het NEDERLANDS. De vraag "welke tijd hoort hier" kun je
   in je eigen taal al stellen en beantwoorden, en dan doe je maar één ding tegelijk. Het Spaanse
   zinnetje staat erbij als illustratie, niet als opgave. Geen enkele vervoegingstabel: die staan
   al in de les en in de spiekbrieven, en dat is precies de verkeerde volgorde voor wie hier komt.

   Wat je hier NIET vindt is een compleet overzicht van het Spaanse werkwoordsysteem. Zes tijden,
   de zes die deze app gebruikt, en de drie keuzes waar het in de praktijk om gaat. */
var TIJDEN = [
 {id:"presente", es:"el presente", nl:"tegenwoordige tijd", en:"present tense",
  doet:"Wat nu waar is, wat je altijd doet, en wat er over vijf minuten gaat gebeuren.",
  doetEn:"What is true now, what you always do, and what happens five minutes from now.",
  herken:"vandaag, altijd, elke dag, meestal, nu",
  vb:["Ik woon in Spanje.", "Elke ochtend drink ik koffie.", "Straks bel ik je."],
  vbEn:["I live in Spain.", "Every morning I drink coffee.", "I will call you in a bit."],
  es1:"Vivo en Espa\\u00f1a.", nl1:"Ik woon in Spanje.",
  let:"Het Spaans gebruikt hem ook voor de nabije toekomst, net als wij: \\u2018straks bel ik je\\u2019.",
  letEn:"Spanish also uses it for the near future, just like English does with \\u2018I am calling you later\\u2019."},

 {id:"indefinido", es:"el pret\\u00e9rito indefinido", nl:"verleden tijd: wat er gebeurde",
  en:"simple past: what happened",
  doet:"E\\u00e9n gebeurtenis in het verleden, met een begin en een eind. Hij is af.",
  doetEn:"One event in the past, with a beginning and an end. It is finished.",
  herken:"gisteren, vorige week, in 1999, opeens, toen",
  vb:["Gisteren brak de vaas.", "In 2019 verhuisde ik naar Madrid.", "Opeens ging de telefoon."],
  vbEn:["Yesterday the vase broke.", "In 2019 I moved to Madrid.", "Suddenly the phone rang."],
  es1:"Ayer se rompi\\u00f3 el jarr\\u00f3n.", nl1:"Gisteren brak de vaas.",
  let:"Let op: het Nederlands heeft hier \\u00e9\\u00e9n vorm waar het Spaans er twee heeft. \\u2018Ik speelde\\u2019 kan jugu\\u00e9 zijn (\\u00e9\\u00e9n keer, af) of jugaba (elke zomer, gewoonte). Dat is de belangrijkste reden dat dit lastig is: je moet een keuze maken die je in je eigen taal nooit hoeft te maken. Dit is de tijd van het VERHAAL: wat er gebeurde, in volgorde.",
  letEn:"Note: English has one form here where Spanish has two. \\u2018I played\\u2019 can be jugu\\u00e9 (once, finished) or jugaba (every summer, a habit). That is the main reason this is hard: you have to make a choice your own language never asks of you. This is the tense of the STORY: what happened, in order."},

 {id:"imperfecto", es:"el pret\\u00e9rito imperfecto", nl:"verleden tijd: hoe het was",
  en:"imperfect: how things were",
  doet:"Hoe het toen was. Een toestand, een gewoonte, of iets dat nog aan de gang was.",
  doetEn:"How things were back then. A state, a habit, or something still going on.",
  herken:"vroeger, altijd, elke zomer, terwijl, toen ik klein was",
  vb:["Vroeger woonde ik in een dorp.", "Ze was moe.", "Terwijl ik kookte, ging de bel."],
  vbEn:["I used to live in a village.", "She was tired.", "While I was cooking, the bell rang."],
  es1:"Cuando era ni\\u00f1o, viv\\u00eda en un pueblo.", nl1:"Toen ik een kind was, woonde ik in een dorp.",
  let:"Dit is de tijd van het DECOR: hoe het eruitzag toen het verhaal gebeurde.",
  letEn:"This is the tense of the SCENERY: what it looked like while the story happened."},

 {id:"perfecto", es:"el pret\\u00e9rito perfecto", nl:"voltooid tegenwoordige tijd",
  en:"present perfect",
  doet:"Iets dat al gebeurd is, maar binnen een tijdvak dat nog loopt.",
  doetEn:"Something that already happened, but inside a period that is still running.",
  herken:"vandaag, deze week, dit jaar, ooit, al, nog niet",
  vb:["Vandaag heb ik drie koppen koffie gedronken.", "Ik heb die film nog niet gezien.", "Ben je ooit in Sevilla geweest?"],
  vbEn:["Today I have had three cups of coffee.", "I have not seen that film yet.", "Have you ever been to Seville?"],
  es1:"Hoy he bebido tres caf\\u00e9s.", nl1:"Vandaag heb ik drie koffie gedronken.",
  let:"Het verschil met de indefinido zit niet in de gebeurtenis maar in het TIJDVAK: vandaag loopt nog, gisteren niet.",
  letEn:"The difference with the indefinido is not the event but the PERIOD: today is still running, yesterday is not."},

 {id:"futuroir", es:"ir a + infinitief", nl:"toekomende tijd met \\u2018gaan\\u2019",
  en:"going to + verb",
  doet:"Een plan of een voornemen. Letterlijk: ik ga iets doen.",
  doetEn:"A plan or an intention. Literally: I am going to do something.",
  herken:"morgen, volgende week, straks, van plan",
  vb:["Morgen ga ik het proberen.", "We gaan een feest organiseren.", "Ik ga even bellen."],
  vbEn:["Tomorrow I am going to try it.", "We are going to throw a party.", "I am going to make a call."],
  es1:"Ma\\u00f1ana voy a intentarlo.", nl1:"Morgen ga ik het proberen.",
  let:"Het Spaans heeft ook een echte toekomende tijd (har\\u00e9, ir\\u00e9), maar in gesproken taal wint \\u2018ir a\\u2019 het ruimschoots.",
  letEn:"Spanish also has a real future tense (har\\u00e9, ir\\u00e9), but in speech \\u2018ir a\\u2019 wins by a mile."},

 {id:"subjuntivo", es:"el subjuntivo", nl:"aanvoegende wijs",
  en:"subjunctive",
  doet:"Geen tijd maar een STEMMING. Je zegt niet dat iets zo is, maar dat je het wilt, betwijfelt, hoopt of erover voelt.",
  doetEn:"Not a tense but a MOOD. You are not saying something is so; you want it, doubt it, hope it or feel about it.",
  herken:"ik wil dat, ik hoop dat, misschien, het is jammer dat, zodat",
  vb:["Ik wil dat je komt. (je komt nog niet)", "Ik hoop dat het lukt. (het is nog niet gelukt)", "Het is jammer dat hij weggaat."],
  vbEn:["I want you to come. (you are not coming yet)", "I hope it works out. (it has not yet)", "It is a shame that he is leaving."],
  es1:"Quiero que vengas.", nl1:"Ik wil dat je komt.",
  let:"Het Nederlands heeft hem bijna niet meer (\\u2018leve de koning\\u2019, \\u2018het ga je goed\\u2019), en dat is precies waarom hij vreemd voelt. De truc is niet de vorm maar de vraag: BEWEER ik iets, of wil, hoop of betwijfel ik het?",
  letEn:"English barely has it left (\\u2018if I were you\\u2019, \\u2018long live the king\\u2019), which is exactly why it feels odd. The trick is not the form but the question: am I STATING something, or wanting, hoping or doubting it?"}
];
/* De drie keuzes waar het in de praktijk op vastloopt. Ze staan apart omdat een lijstje van zes
   tijden je nog niet vertelt welke twee je tegen elkaar afweegt, en dat is wat je in een zin doet. */
var TIJD_KEUZES = [
 {vraag:"Is het af, of was het aan de gang?", vraagEn:"Is it finished, or was it going on?",
  a:"af \\u2192 indefinido", b:"aan de gang \\u2192 imperfecto",
  vb:"Terwijl ik KOOKTE (aan de gang), GING de bel (af).",
  vbEn:"While I WAS COOKING (going on), the bell RANG (finished)."},
 {vraag:"Loopt het tijdvak nog?", vraagEn:"Is the period still running?",
  a:"nog bezig: vandaag, deze week \\u2192 perfecto", b:"voorbij: gisteren, vorig jaar \\u2192 indefinido",
  vb:"VANDAAG heb ik gebeld. GISTEREN belde ik.",
  vbEn:"TODAY I have called. YESTERDAY I called."},
 {vraag:"Beweer je het, of wil of betwijfel je het?", vraagEn:"Are you stating it, or wanting or doubting it?",
  a:"beweren \\u2192 gewone vorm (indicativo)", b:"willen, hopen, twijfelen, voelen \\u2192 subjuntivo",
  vb:"Ik WEET dat hij komt. Ik WIL dat hij komt.",
  vbEn:"I KNOW he is coming. I WANT him to come."}
];
var tijdenOpenNu = false;
function tijdenOpen(){
  tijdenOpenNu = true;
  gwSess = null; gcLeesId = null; spiekLeesIdx = null;
  spiekVerseOpen = true;             // dezelfde afspraak als spiekOpen: niet wissen bij binnenkomst
  show("spiekbrief");
  try { window.scrollTo(0, 0); } catch(e){}
}
function tijdenRijHtml(t){
  var vb = (profLang() === "nl" ? t.vb : (t.vbEn || t.vb));
  return "<details class='tijdrij'><summary><b>" + t.es + "</b> \\u00b7 " +
      ct(t.nl, t.en) + "</summary><div class='inner'>" +
    "<p style='margin:2px 0 8px'>" + ct(t.doet, t.doetEn) + "</p>" +
    "<p class='muted' style='margin:0 0 8px; font-size:.85rem'>" +
      ct("Je herkent hem aan: ", "You spot it by: ") + t.herken + "</p>" +
    "<ul style='margin:0 0 8px; padding-left:18px'>" +
      vb.map(function(x){ return "<li>" + x + "</li>"; }).join("") + "</ul>" +
    "<p style='margin:0 0 6px'><span class='es'>" + t.es1 + "</span> \\u00b7 " +
      "<span class='muted'>" + t.nl1 + "</span></p>" +
    "<p class='muted' style='margin:0; font-size:.88rem'>" + ct(t.let, t.letEn) + "</p>" +
    "</div></details>";
}
function tijdenKaartHtml(){
  var terug = "<div class='row'><button class='ghost' id='btnTijdenTerug'>" +
    ct("\\u2190 Terug naar Grammatica", "\\u2190 Back to Grammar") + "</button></div>";
  return "<div class='card'><span class='kicker'>" + ct("De tijden", "The tenses") + "</span>" +
    "<h2 style='margin-top:2px'>" +
      ct("Wat doet een tijd eigenlijk?", "What does a tense actually do?") + "</h2>" + terug +
    "<p style='margin-top:10px'>" +
      ct("Een tijd is geen sier. Hij zegt <b>wanneer</b> iets gebeurde en, belangrijker, <b>hoe je ernaar kijkt</b>: als iets dat af is, of als iets dat aan de gang was. Het Spaans dwingt je die keuze te maken waar het Nederlands hem vaak in het midden laat, en d\\u00e1\\u00e1r zit het werk.",
         "A tense is not decoration. It says <b>when</b> something happened and, more importantly, <b>how you look at it</b>: as something finished, or as something that was going on. Spanish forces you to make that choice where English often leaves it open, and that is where the work is.") +
    "</p>" +
    "<p class='muted' style='margin:0 0 12px'>" +
      ct("De voorbeelden hieronder staan met opzet in het Nederlands. De vraag \\u2018welke tijd hoort hier\\u2019 kun je in je eigen taal al beantwoorden, en dan hoef je maar \\u00e9\\u00e9n ding tegelijk te doen. De Spaanse vorm komt daarna.",
         "The examples below are deliberately in English. You can answer \\u2018which tense goes here\\u2019 in your own language first, and then you only do one thing at a time. The Spanish form comes after.") +
    "</p>" +
    "<h3 style='margin:14px 0 6px'>" + ct("De zes op een rij", "The six of them") + "</h3>" +
    TIJDEN.map(tijdenRijHtml).join("") +
    "<h3 style='margin:18px 0 6px'>" + ct("En dit zijn de drie keuzes", "And these are the three choices") + "</h3>" +
    "<p class='muted' style='margin:0 0 8px; font-size:.88rem'>" +
      ct("In een zin weeg je nooit zes tijden tegen elkaar af. Je staat steeds voor \\u00e9\\u00e9n van deze drie vragen.",
         "In a sentence you never weigh six tenses against each other. You are always facing one of these three questions.") + "</p>" +
    TIJD_KEUZES.map(function(k){
      return "<div class='card' style='margin:0 0 8px; padding:12px'>" +
        "<b>" + ct(k.vraag, k.vraagEn) + "</b>" +
        "<p class='muted' style='margin:6px 0 4px'>" + k.a + "<br>" + k.b + "</p>" +
        "<p style='margin:0; font-size:.9rem'>" + ct(k.vb, k.vbEn) + "</p></div>";
    }).join("") + terug + "</div>";
}""")

    # de kaart tekenen, en de weg terug
    rep("""  // v23.232: één spiekbrief, opengeslagen, met een weg terug.""",
"""  // v23.233: de kaart van de tijden, opengeslagen, met een weg terug.
  if(tijdenOpenNu){
    el.innerHTML = tijdenKaartHtml();
    el.querySelectorAll("#btnTijdenTerug").forEach(function(b){
      b.onclick = function(){ tijdenOpenNu = false; renderCheat(); try { window.scrollTo(0, 0); } catch(e){} };
    });
    jargonScan(el);
    return;
  }
  // v23.232: één spiekbrief, opengeslagen, met een weg terug.""")

    # en langs de gewone weg binnenkomen sluit hem weer, net als de spiekbrief
    rep("""  if(tabId==="spiekbrief" && !spiekVerseOpen){ spiekLeesIdx = null; }""",
"""  if(tabId==="spiekbrief" && !spiekVerseOpen){ spiekLeesIdx = null; tijdenOpenNu = false; }""")

    # de ingang: bovenaan de Grammatica-tab, boven de route
    rep("""function gramHomeHtml(){ return gramRouteHtml() + gramOefenHtml(); }""",
"""/* v23.233: bovenaan, want dit is wat je nodig hebt vóórdat de route ergens over gaat. Eén regel,
   in de vorm die de app al voor dit soort ingangen gebruikt (meerrij), zodat er geen kaart bij komt
   op een scherm dat al vol staat. */
function tijdenIngangHtml(){
  return "<button class='meerrij' id='btnTijdenKaart' style='margin-bottom:12px'>" +
    "<span class='mi'>\\ud83d\\udcd8</span><span><b>" +
      ct("Wat doet een tijd eigenlijk?", "What does a tense actually do?") + "</b><span>" +
      ct("Presente, indefinido, imperfecto, subjuntivo: wat ze betekenen, in gewone taal en met Nederlandse voorbeelden.",
         "Presente, indefinido, imperfecto, subjuntivo: what they mean, in plain language with English examples.") +
    "</span></span></button>";
}
function gramHomeHtml(){ return tijdenIngangHtml() + gramRouteHtml() + gramOefenHtml(); }""")

    rep("""function gramHomeWire(){
  var p = gramPadNu();""",
"""function gramHomeWire(){
  var bt = document.getElementById("btnTijdenKaart");
  if(bt) bt.onclick = tijdenOpen;
  var p = gramPadNu();""")

    rep("""  .meerrij .mi{font-size:1.35rem; line-height:1; flex:0 0 auto;}""",
"""  .meerrij .mi{font-size:1.35rem; line-height:1; flex:0 0 auto;}
  /* v23.233: de rijen op de kaart van de tijden. Dichtgeklapt zie je zes namen, opengeklapt één
     tijd tegelijk; zes tijden tegelijk uitgeklapt is een muur tekst en dan leest niemand hem. */
  .tijdrij{border:1px solid var(--border); border-radius:12px; padding:10px 12px; margin-bottom:6px;
           background:var(--card);}
  .tijdrij > summary{cursor:pointer; font-size:.95rem;}
  .tijdrij .inner{padding-top:8px;}""")

    # =========================================================================================
    # 2. je score naast de doos
    # =========================================================================================
    rep("""function gcStatusHtml(cid){
  var st = gramLees(cid);
  if(gcStaatFout(st)) return "<span style='color:var(--red)'>" + ct("fout gegaan", "got this wrong") + "</span>";
  if(!st.goed && !st.fout) return ct("nog niet gedaan", "not done yet");
  return ct("doos ", "box ") + (st.box || 0) + "/" + (GRAM_BOX.length - 1);
}""",
"""/* ================= WAT DE DOOS NIET ZEGT (v23.233) =================

   Stefan: "ik heb niet echt het gevoel dat ik door de oefeningen het beter word."

   Gemeten in zijn eigen logboek, over tien opnames: muymucho 75% goed en de doos ging van 3 naar
   0; genero 62% goed en de doos ging van 2 naar 0; over alle onderwerpen samen 70% goed. Hij werd
   in dat venster dus wél beter, en het enige wat op zijn scherm stond was "doos 0/5".

   De doosregel zelf blijft zoals hij is: één misser op een dag zet hem naar nul, en Stefan heeft
   het zachter maken in v23.208 afgewezen en houdt daaraan vast. Wat verandert is dat de app erbij
   zegt wat hij óók weet. S.gramLog ligt er sinds v23.211, zeven dagen diep, en werd tot nu toe
   alleen door de suite gelezen. Dat venster staat nu open.

   Onder de drie beurten staat er niets: 1 van de 1 is geen percentage, en nul is geen bericht. */
var GRAMWEEK_MIN = 3;
function gramWeek(cid){
  var n = 0, goed = 0, s = String(cid || "").split("#")[0];
  try {
    var log = S.gramLog || {};
    Object.keys(log).forEach(function(dag){
      var r = (log[dag] || {})[s];
      if(!r) return;
      n += r.n || 0;
      goed += r.goed || 0;
    });
  } catch(e){ return null; }
  if(n < GRAMWEEK_MIN) return null;
  return {n:n, goed:goed, pct: Math.round(100 * goed / n)};
}
function gramWeekHtml(cid){
  var w = gramWeek(cid);
  if(!w) return "";
  return " <span class='muted' style='font-size:.72rem'>\\u00b7 " +
    w.pct + "% " + ct("goed deze week", "correct this week") + "</span>";
}
function gcStatusHtml(cid){
  var st = gramLees(cid);
  if(gcStaatFout(st)) return "<span style='color:var(--red)'>" + ct("fout gegaan", "got this wrong") + "</span>" + gramWeekHtml(cid);
  if(!st.goed && !st.fout) return ct("nog niet gedaan", "not done yet");
  return ct("doos ", "box ") + (st.box || 0) + "/" + (GRAM_BOX.length - 1) + gramWeekHtml(cid);
}""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    for nodig in ["var TIJDEN = [", "var TIJD_KEUZES = [", "function tijdenKaartHtml(",
                  "function tijdenOpen(", "function tijdenIngangHtml(", "function gramWeek(",
                  "function gramWeekHtml(", "btnTijdenKaart", ".tijdrij{"]:
        assert nodig in src, "ontbreekt: " + nodig
    for naam in ["tijdenOpen", "tijdenKaartHtml", "tijdenRijHtml", "tijdenIngangHtml",
                 "gramWeek", "gramWeekHtml"]:
        c = src.count("function " + naam + "(")
        assert c == 1, "function %s staat %d keer in het bestand" % (naam, c)
    # de zes tijden staan er allemaal, en de drie keuzes ook
    blok = src[src.index("var TIJDEN = ["):src.index("var tijdenOpenNu")]
    for t in ["presente", "indefinido", "imperfecto", "perfecto", "futuroir", "subjuntivo"]:
        assert 'id:"' + t + '"' in blok, "tijd ontbreekt op de kaart: " + t
    assert blok.count("doet:") == 6, "verwacht zes tijden, kreeg %d" % blok.count("doet:")
    assert src[src.index("var TIJD_KEUZES = ["):src.index("var tijdenOpenNu")].count("vraag:") == 3, \
        "verwacht drie keuzes"
    # en geen enkele vervoegingstabel op deze kaart: dat is precies de verkeerde volgorde
    assert "<table" not in blok, "er staat een tabel op de kaart van de tijden"
    # "voltooid verleden tijd" is in het Nederlands 'ik had gebroken', en dat is geen van deze zes.
    # Een kaart die de namen moet uitleggen mag ze zelf niet verkeerd noemen.
    assert "voltooid verleden tijd" not in blok, \
        "de kaart draagt een verkeerde Nederlandse naam (voltooid verleden tijd is 'ik had ...')"
    assert "vorm waar het Spaans er twee heeft" in blok, \
        "de kaart legt niet uit waarom indefinido en imperfecto lastig zijn"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de kaart van de tijden staat er, en de doos zegt er je weekscore bij")
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
