#!/usr/bin/env python3
# v23.194 - de negen resterende gaten dicht
#
# Stefan, 24 aug: "ja ziet er goed uit. bouw nu de rest."
#
# De review "De grammatica als geheel" telde twaalf spiekkaarten met wél een toets en géén les.
# v23.193 dichtte er drie. Dit zijn de negen die overbleven, en daarmee staat het gat op nul.
#
# NIET NEGEN LESSEN, MAAR ZES PLUS TWEE AANHECHTINGEN
#
# Twee van de negen kaarten zijn geen grammatica-onderwerp maar een woordenlijst:
#
#   kaart 4   "Signaalwoorden om te herkennen"      ayer, hoy, ya, todavía no, hace dos años...
#   kaart 28  "Nuttige woorden om een anekdote..."  un día, mientras, de repente, al final
#
# Daar een microles voor verzinnen zou het gat op papier dichten en niets uitleggen: het zijn de
# signaalwoorden van twee regels die al een les hébben. Kaart 4 hoort bij perfecto-of-indefinido,
# kaart 28 bij indefinido-of-imperfecto.
#
# Die twee lessen krijgen er dus een alinea bij waarin die woorden echt staan, en pas dán claimen ze
# de kaart. Een kaart aanhechten zonder de uitleg uit te breiden zou een teller naar nul praten, en
# dat is precies het boekhouden waar de review tegen was.
#
# En twee kaarten krijgen samen één les:
#
#   kaart 18  "Parecer: je mening geven"            "werkt grammaticaal precies als gustar"
#   kaart 23  "Doler: pijn hebben"                  "werkt grammaticaal precies als gustar"
#
# Dat is één regel, niet twee; de kaarten zeggen het zelf. Twee lessen schrijven voor één regel is
# dezelfde fout als twee plekken die hetzelfde doen.
#
# DE ZES NIEUWE LESSEN
#
#   tijdmarkers    kaart 6    desde, desde hace, hace, durante - en welke tijd erbij hoort
#   posesivo       kaart 9    el mío, la tuya: het geslacht volgt het DING, niet de eigenaar
#   exclamacion    kaart 17   ¡Qué...! zonder lidwoord, en qué + znw + más + adjectief
#   gustarfamilie  18 en 23   doler, parecer, encantar, apetecer: het ding is het onderwerp
#   seimpersonal   kaart 21   se cocina / se necesitan: het werkwoord volgt wat erna komt
#   cantidad       kaart 22   un poco de, bastante, demasiado - en demasiado buigt mee
#
# WAAR ZE IN DE VOLGORDE KOMEN
#
# Elke les staat achter het onderwerp waar hij op leunt, en niet achteraan:
#
#   cantidad       na muymucho      dezelfde familie, en demasiado buigt net als mucho
#   gustarfamilie  na gustar        dezelfde constructie, andere werkwoorden
#   posesivo       na demostrativo  allebei bepalers die met het ding meebuigen
#   seimpersonal   na reflexivo     allebei se, en dat is precies de verwarring
#   exclamacion    na comparar      losstaand en makkelijk, dus niet achteraan
#   tijdmarkers    voor perfindef   de signaalwoorden komen vóór de regel die ze aanwijzen
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.194"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = '{id:"gustarfamilie"' not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

# =============================================================================================
# 1. de woordvoorraad
# =============================================================================================
DATA = r'''/* v23.194: de voorraad voor de zes lessen van deze versie. Elke rij draagt zijn eigen
   Nederlandse zin: afgeleid Nederlands ging in v23.193 mis ("Schrijven je naam"), en de les eromheen
   is niets waard als de vertaling krom is. */
/* fw = het functiewoord, arg = wat erachter hoort. Uit elkaar gehouden omdat er twee vragen in
   zitten: welke tijd hoort erbij (fw bepaalt dat), en welk woord hoort hier (dat is de eigenlijke
   vaardigheid). Met vier rijen kon de les maar zeven vragen maken en was hij na één ronde leeg. */
var GC_TIJDMARK = [
 {fw:"hace", arg:"dos años", tijd:"indefinido", zin:"Empecé ___.",
  nl:"Ik ben twee jaar geleden begonnen.", en:"I started two years ago."},
 {fw:"hace", arg:"tres meses", tijd:"indefinido", zin:"Nos mudamos ___.",
  nl:"We zijn drie maanden geleden verhuisd.", en:"We moved three months ago."},
 {fw:"desde", arg:"marzo", tijd:"presente", zin:"Vivo aquí ___.",
  nl:"Ik woon hier sinds maart.", en:"I have lived here since March."},
 {fw:"desde", arg:"el lunes", tijd:"presente", zin:"Estoy enfermo ___.",
  nl:"Ik ben sinds maandag ziek.", en:"I have been ill since Monday."},
 {fw:"desde hace", arg:"un año", tijd:"presente", zin:"Estudio español ___.",
  nl:"Ik leer al een jaar Spaans.", en:"I have been studying Spanish for a year."},
 {fw:"desde hace", arg:"dos semanas", tijd:"presente", zin:"Trabajo aquí ___.",
  nl:"Ik werk hier al twee weken.", en:"I have been working here for two weeks."},
 {fw:"durante", arg:"el verano", tijd:"indefinido", zin:"___ viví en Alicante.",
  nl:"Tijdens de zomer woonde ik in Alicante.", en:"During the summer I lived in Alicante."},
 {fw:"durante", arg:"la reunión", tijd:"indefinido", zin:"___ no dije nada.",
  nl:"Tijdens de vergadering zei ik niets.", en:"During the meeting I said nothing."}
];
var GC_TIJDMARK_FW = ["hace", "desde", "desde hace", "durante"];
/* een zin die met het ingevulde woord begint krijgt een hoofdletter, ook als dat woord in een
   <b> zit. Zonder dit stond er "durante el verano viví en Alicante." op het scherm. */
function gcZinHoofd(s){
  return String(s).replace(/^(\s*(?:<[^>]+>\s*)*)([a-záéíóúñü])/, function(_, pre, c){
    return pre + c.toUpperCase();
  });
}
var GC_POSES = [
 {es:"casa", g:"f", nl:"huis", en:"house", dl:"het"},
 {es:"coche", g:"m", nl:"auto", en:"car", dl:"de"},
 {es:"llave", g:"f", nl:"sleutel", en:"key", dl:"de"},
 {es:"libro", g:"m", nl:"boek", en:"book", dl:"het"}
];
var GC_POSES_PERS = [
 {m:"el mío", f:"la mía", nl:"de mijne", en:"mine"},
 {m:"el tuyo", f:"la tuya", nl:"de jouwe", en:"yours"},
 {m:"el nuestro", f:"la nuestra", nl:"de onze", en:"ours"}
];
/* nlB is de verbogen Nederlandse vorm. Afleiden met nl + "e" gaf "duure"; een les over vorm mag
   zijn eigen vertaling niet verbouwen. */
var GC_UITROEP = [
 {adj:"divertido", nl:"leuk", nlB:"leuke", en:"fun"},
 {adj:"bonito", nl:"mooi", nlB:"mooie", en:"pretty"},
 {adj:"raro", nl:"vreemd", nlB:"vreemde", en:"strange"},
 {adj:"caro", nl:"duur", nlB:"dure", en:"expensive"}
];
var GC_UITROEP_ZN = [
 {es:"pena", nl:"Wat jammer!", en:"What a shame!"},
 {es:"suerte", nl:"Wat een geluk!", en:"What luck!"},
 {es:"sorpresa", nl:"Wat een verrassing!", en:"What a surprise!"}
];
/* De gustar-familie. `enk` en `mv` zijn de vormen die horen bij wat er NÁ het voornaamwoord staat,
   want dat is het onderwerp, en niet de persoon die het voelt. */
var GC_GUSTARFAM = [
 {ww:"doler", enk:"duele", mv:"duelen", nl:"pijn doen", en:"to hurt",
  dEnk:"la cabeza", dEnkNl:"mijn hoofd", dEnkEn:"my head",
  dMv:"los pies", dMvNl:"mijn voeten", dMvEn:"my feet"},
 {ww:"encantar", enk:"encanta", mv:"encantan", nl:"geweldig vinden", en:"to love",
  dEnk:"el cine", dEnkNl:"de bioscoop", dEnkEn:"the cinema",
  dMv:"las fiestas", dMvNl:"feestjes", dMvEn:"parties"},
 {ww:"apetecer", enk:"apetece", mv:"apetecen", nl:"zin hebben in", en:"to fancy",
  dEnk:"un café", dEnkNl:"een koffie", dEnkEn:"a coffee",
  dMv:"unas tapas", dMvNl:"wat tapas", dMvEn:"some tapas"},
 /* st = wat er direct achter het werkwoord hoort. Parecer heeft een oordeel nodig: "me parece el
    plan" is geen zin, "me parece bien el plan" wel. De andere drie hebben niets nodig. */
 {ww:"parecer", enk:"parece", mv:"parecen", nl:"vinden van", en:"to think of", st:"bien ",
  dEnk:"el plan", dEnkNl:"het plan", dEnkEn:"the plan",
  dMv:"las ideas", dMvNl:"de ideeën", dMvEn:"the ideas"}
];
var GC_SEIMP = [
 {enk:"se cocina", mv:"se cocinan", dEnk:"el arroz", dEnkNl:"de rijst", dEnkEn:"the rice",
  dMv:"las patatas", dMvNl:"de aardappels", dMvEn:"the potatoes", nl:"gekookt", en:"cooked"},
 {enk:"se necesita", mv:"se necesitan", dEnk:"una cuchara", dEnkNl:"een lepel", dEnkEn:"a spoon",
  dMv:"dos cucharadas", dMvNl:"twee eetlepels", dMvEn:"two spoonfuls", nl:"nodig", en:"needed"},
 {enk:"se vende", mv:"se venden", dEnk:"el piso", dEnkNl:"het appartement", dEnkEn:"the flat",
  dMv:"los pisos", dMvNl:"de appartementen", dMvEn:"the flats", nl:"verkocht", en:"sold"},
 {enk:"se habla", mv:"se hablan", dEnk:"español", dEnkNl:"Spaans", dEnkEn:"Spanish",
  dMv:"dos idiomas", dMvNl:"twee talen", dMvEn:"two languages", nl:"gesproken", en:"spoken"}
];
var GC_CANT = [
 {es:"sal", g:"f", nl:"zout", en:"salt"},
 {es:"azúcar", g:"m", nl:"suiker", en:"sugar"},
 {es:"aceite", g:"m", nl:"olie", en:"oil"},
 {es:"agua", g:"f", nl:"water", en:"water"}
];
'''

if DOE_APP:
    rep("var GC_ADJ_SER = [", DATA + "var GC_ADJ_SER = [")

# =============================================================================================
# 2. de zes lessen
# =============================================================================================

TIJDMARK = r''' /* v23.194: kaart 6. Deze les gaat niet over woordjes maar over de tijd die eraan vastzit:
    "desde hace un año" dwingt presente af en "hace un año" indefinido, en dat is het hele punt. */
 {id:"tijdmarkers", icon:"⏱️", naam:"Sinds, al, geleden", naamEn:"Since, for, ago",
  corr:[], spiek:{a2:[6]}, wizard:null,
  uitleg:"<p>Vier woorden die in het Nederlands door elkaar lopen en in het Spaans elk hun eigen tijd meebrengen.</p>"+
    "<p><b>hace + tijd</b> = geleden, een punt in het verleden. Daar hoort de <b>indefinido</b> bij: <i>Empecé hace un año.</i></p>"+
    "<p><b>desde + moment</b> = sinds. Het loopt nog door, dus <b>presente</b>: <i>Vivo aquí desde marzo.</i></p>"+
    "<p><b>desde hace + duur</b> = al ... lang. Ook nog bezig, dus ook <b>presente</b>: <i>Estudio español desde hace un año.</i> In het Nederlands zeg je hier “ik leer al een jaar”, in het Engels “I have been studying”; het Spaans houdt het gewoon in de tegenwoordige tijd.</p>"+
    "<p><b>durante + periode</b> = tijdens, een afgesloten stuk: <i>Durante el verano viví en Alicante.</i></p>"+
    "<p>Let op: <i>hace</i> gaat over een duur, niet over een datum. <i>Hace marzo</i> bestaat niet.</p>",
  uitlegEn:"<p>Four words that blur together in Dutch and each carry their own tense in Spanish.</p>"+
    "<p><b>hace + time</b> = ago, a point in the past, so <b>indefinido</b>: <i>Empecé hace un año.</i></p>"+
    "<p><b>desde + moment</b> = since. It is still going, so <b>presente</b>: <i>Vivo aquí desde marzo.</i></p>"+
    "<p><b>desde hace + duration</b> = for ... now. Also still going, so <b>presente</b>: <i>Estudio español desde hace un año.</i> English says “I have been studying”; Spanish keeps it in the present.</p>"+
    "<p><b>durante + period</b> = during, a closed stretch: <i>Durante el verano viví en Alicante.</i></p>"+
    "<p>Note: <i>hace</i> takes a duration, not a date. <i>Hace marzo</i> does not exist.</p>",
  begrip:{v:"Waarom staat er presente in «Estudio español desde hace un año»?",
    vEn:"Why is there a present tense in «Estudio español desde hace un año»?",
    o:["Omdat het nog steeds bezig is","Omdat een jaar kort is","Omdat estudiar onregelmatig is","Omdat desde altijd presente vraagt"],
    oEn:["Because it is still going on","Because a year is short","Because estudiar is irregular","Because desde always takes the present"],
    g:0,
    w:"Desde hace zegt dat iets beéínd is en nog doorloopt. Wat doorloopt staat in het Spaans in de tegenwoordige tijd, ook als het Nederlands “al een jaar” zegt.",
    wEn:"Desde hace says something started and is still going. What is still going stays in the present in Spanish, even where English says “have been”."},
  patronen:[
   /* gcZinHoofd: staat het gat vooraan, dan begint de zin met het ingevulde woord en moet dat een
      hoofdletter krijgen. "durante el verano viví" stond er anders klein. */
   function(){ var m = gcKies(GC_TIJDMARK), es = m.fw + " " + m.arg;
     return {v:gcZinHoofd(m.zin.replace("___", "<b>"+es+"</b>")) + " — " + m.nl + "<br>Welke tijd hoort hier?",
             vEn:gcZinHoofd(m.zin.replace("___", "<b>"+es+"</b>")) + " — " + m.en + "<br>Which tense belongs here?",
             o:["presente", "indefinido"], g:m.tijd === "presente" ? 0 : 1,
             w:es + " → " + m.tijd + ". Hace en durante wijzen naar iets afgeslotens; desde en desde hace naar iets dat nog loopt.",
             wEn:es + " → " + m.tijd + ". Hace and durante point at something finished; desde and desde hace at something still going."}; },
   /* en de andere kant op: de zin en de vertaling staan er, welk van de vier woorden hoort hier?
      Dat is de vaardigheid; de tijd is er het gevolg van. */
   function(){ var m = gcKies(GC_TIJDMARK);
     return {v:m.zin.replace("___", "<b>___ " + m.arg + "</b>") + " — " + m.nl,
             vEn:m.zin.replace("___", "<b>___ " + m.arg + "</b>") + " — " + m.en,
             /* geen gcZinHoofd hier: het gat staat er nog, en een hoofdletter op "___" bestaat niet */
             o:GC_TIJDMARK_FW.slice(), g:GC_TIJDMARK_FW.indexOf(m.fw),
             w:m.fw + " " + m.arg + ". " + (m.fw === "hace" ? "Hace + duur = geleden, en dat is klaar." :
                m.fw === "desde" ? "Desde + moment = sinds, en het loopt nog." :
                m.fw === "desde hace" ? "Desde hace + duur = al ... lang, en het loopt nog." :
                "Durante + periode = tijdens, een afgesloten stuk."),
             wEn:m.fw + " " + m.arg + ". " + (m.fw === "hace" ? "Hace + duration = ago, and that is finished." :
                m.fw === "desde" ? "Desde + moment = since, and it is still going." :
                m.fw === "desde hace" ? "Desde hace + duration = for ... now, and it is still going." :
                "Durante + period = during, a closed stretch.")}; },
   function(){
     return {v:"Ik leer <b>al een jaar</b> Spaans. Welke zin klopt?",
             vEn:"I have been studying Spanish <b>for a year</b>. Which sentence is right?",
             o:["Estudio español desde hace un año.","Estudio español hace un año.","Estudié español desde hace un año."],
             oEn:["Estudio español desde hace un año.","Estudio español hace un año.","Estudié español desde hace un año."],
             g:0,
             w:"Al een jaar en nog bezig: desde hace + presente. Alleen hace zou “een jaar geleden” betekenen, en dan is het klaar.",
             wEn:"For a year and still going: desde hace + present. Just hace would mean “a year ago”, which is finished."}; },
   function(){
     return {v:"Wat is er mis met «Hace marzo que vivo aquí»?",
             vEn:"What is wrong with «Hace marzo que vivo aquí»?",
             o:["Hace wil een duur, geen maandnaam","Vivo moet viví zijn","Er hoort desde voor hace","Er is niets mis mee"],
             oEn:["Hace wants a duration, not a month name","Vivo should be viví","It needs desde before hace","Nothing is wrong with it"],
             g:0,
             w:"Hace + duur (dos años, un mes). Voor een moment gebruik je desde: desde marzo.",
             wEn:"Hace + duration (dos años, un mes). For a moment you use desde: desde marzo."}; },
   function(){
     return {v:"«Trabajé allí ___ 2010 ___ 2015.» (van 2010 tot 2015)",
             vEn:"«Trabajé allí ___ 2010 ___ 2015.» (from 2010 to 2015)",
             o:["desde ... hasta","hace ... hasta","durante ... desde","desde ... desde"],
             oEn:["desde ... hasta","hace ... hasta","durante ... desde","desde ... desde"],
             g:0,
             w:"Van-tot is desde ... hasta. Dit stuk is afgesloten, dus indefinido: trabajé.",
             wEn:"From-to is desde ... hasta. This stretch is finished, hence the indefinido: trabajé."}; }
  ]},

'''

POSESIVO = r''' /* v23.194: kaart 9. De hele moeilijkheid zit in één ding: het geslacht volgt het DING en niet
    de eigenaar. Een man zegt la mía over een casa. */
 {id:"posesivo", icon:"🔑", naam:"De mijne, de jouwe", naamEn:"Mine, yours",
  corr:[], spiek:{a2:[9]}, wizard:null,
  uitleg:"<p>Is het zelfstandig naamwoord al genoemd, dan hoef je het niet te herhalen: je zegt <b>lidwoord + bezitsvorm</b>.</p>"+
    "<p><i>¿Es tu coche? No, el mío es azul.</i> — <i>Esta llave no es la mía.</i></p>"+
    "<table><tr><th></th><th>mannelijk</th><th>vrouwelijk</th></tr>"+
    "<tr><td>van mij</td><td>el mío</td><td>la mía</td></tr>"+
    "<tr><td>van jou</td><td>el tuyo</td><td>la tuya</td></tr>"+
    "<tr><td>van hem, haar, u</td><td>el suyo</td><td>la suya</td></tr>"+
    "<tr><td>van ons</td><td>el nuestro</td><td>la nuestra</td></tr></table>"+
    "<p>Meervoud gaat mee: <i>los míos, las tuyas</i>.</p>"+
    "<p><b>En dit is waar het misgaat:</b> het geslacht volgt het ding, niet de eigenaar. Een man die over een <i>casa</i> praat zegt <i>la mía</i>, want casa is vrouwelijk.</p>"+
    "<p>Na <i>ser</i> laat je het lidwoord meestal weg: <i>Este libro es mío.</i></p>",
  uitlegEn:"<p>If the noun has already been mentioned, you do not repeat it: you say <b>article + possessive</b>.</p>"+
    "<p><i>¿Es tu coche? No, el mío es azul.</i> — <i>Esta llave no es la mía.</i></p>"+
    "<table><tr><th></th><th>masculine</th><th>feminine</th></tr>"+
    "<tr><td>mine</td><td>el mío</td><td>la mía</td></tr>"+
    "<tr><td>yours</td><td>el tuyo</td><td>la tuya</td></tr>"+
    "<tr><td>his, hers, yours (formal)</td><td>el suyo</td><td>la suya</td></tr>"+
    "<tr><td>ours</td><td>el nuestro</td><td>la nuestra</td></tr></table>"+
    "<p>Plurals follow: <i>los míos, las tuyas</i>.</p>"+
    "<p><b>And this is where it goes wrong:</b> the gender follows the thing, not the owner. A man talking about a <i>casa</i> says <i>la mía</i>, because casa is feminine.</p>"+
    "<p>After <i>ser</i> you usually drop the article: <i>Este libro es mío.</i></p>",
  begrip:{v:"Een man praat over zijn huis (la casa). Wat zegt hij?",
    vEn:"A man is talking about his house (la casa). What does he say?",
    o:["la mía, want casa is vrouwelijk","el mío, want hij is een man","el mía, een mengvorm","lo mío, want het is een ding"],
    oEn:["la mía, because casa is feminine","el mío, because he is a man","el mía, a mix","lo mío, because it is a thing"],
    g:0,
    w:"Het geslacht komt van het woord waar je het over hebt. Wie het zegt doet er niet toe.",
    wEn:"The gender comes from the word you are talking about. Who says it is irrelevant."},
  patronen:[
   function(){ var s = gcKies(GC_POSES), pers = gcKies(GC_POSES_PERS);
     var goed = s.g === "f" ? pers.f : pers.m, mis = s.g === "f" ? pers.m : pers.f;
     return {v:"¿Es tu " + s.es + "? No, ___ es azul. (" + gcHoofd(pers.nl) + " is blauw — " + s.dl + " " + s.nl + ")",
             vEn:"¿Es tu " + s.es + "? No, ___ es azul. (" + pers.en + " is blue — the " + s.en + ")",
             o:[goed, mis], g:0,
             w:s.es + " is " + (s.g === "f" ? "vrouwelijk" : "mannelijk") + ", dus " + goed + ". Het geslacht volgt het ding.",
             wEn:s.es + " is " + (s.g === "f" ? "feminine" : "masculine") + ", so " + goed + ". The gender follows the thing."}; },
   /* het aanwijzend voornaamwoord buigt óók mee: "Este casa" was fout Spaans en zou de les
      tegenspreken die hij geeft. */
   function(){ var s = gcKies(GC_POSES), dem = s.g === "f" ? "Esta" : "Este";
     return {v:dem + " " + s.es + " es ___. (Dit is van mij — na ser)",
             vEn:dem + " " + s.es + " es ___. (This one is mine — after ser)",
             o:["mío", "mía", s.g === "f" ? "la mía" : "el mío"], g:s.g === "f" ? 1 : 0,
             w:"Na ser valt het lidwoord weg, en de vorm buigt nog steeds mee met " + s.es + ".",
             wEn:"After ser the article drops, and the form still agrees with " + s.es + "."}; },
   function(){
     return {v:"Wat is het meervoud van «la mía»?",
             vEn:"What is the plural of «la mía»?",
             o:["las mías","los míos","la mías","las mío"],
             oEn:["las mías","los míos","la mías","las mío"],
             g:0,
             w:"Lidwoord en bezitsvorm gaan allebei mee: las mías.",
             wEn:"Both the article and the possessive follow: las mías."}; }
  ]},

'''

EXCLAM = r''' /* v23.194: kaart 17. Klein onderwerp, en juist daarom een eigen les: het is in twee minuten af
    en het zit in elk gesprek. */
 {id:"exclamacion", icon:"❗", naam:"¡Qué...! uitroepen", naamEn:"¡Qué...! exclamations",
  corr:[], spiek:{a2:[17]}, wizard:null,
  uitleg:"<p>Een spontane uitroep begint met <b>¡qué</b>, en er komt <b>geen lidwoord</b> achter. Dat laatste is het enige wat je hoeft te onthouden, want in het Nederlands zeg je juist wél “wat een”.</p>"+
    "<p><b>qué + bijvoeglijk naamwoord:</b> <i>¡Qué divertido! ¡Qué bien!</i></p>"+
    "<p><b>qué + zelfstandig naamwoord:</b> <i>¡Qué pena! ¡Qué suerte!</i> — niet <i>¡Qué una pena!</i></p>"+
    "<p><b>qué + znw + más of tan + adjectief:</b> <i>¡Qué día más bonito!</i> Hier zit het bijvoeglijk naamwoord er dus achter, met más of tan ertussen.</p>"+
    "<p>Er hoeft geen werkwoord bij: het is een losse uitroep, geen zin.</p>",
  uitlegEn:"<p>A spontaneous exclamation starts with <b>¡qué</b>, and <b>no article</b> follows. That is the only thing to remember, because English does say “what a”.</p>"+
    "<p><b>qué + adjective:</b> <i>¡Qué divertido! ¡Qué bien!</i></p>"+
    "<p><b>qué + noun:</b> <i>¡Qué pena! ¡Qué suerte!</i> — not <i>¡Qué una pena!</i></p>"+
    "<p><b>qué + noun + más or tan + adjective:</b> <i>¡Qué día más bonito!</i> Here the adjective goes after, with más or tan in between.</p>"+
    "<p>No verb needed: it is a loose exclamation, not a sentence.</p>",
  begrip:{v:"Wat gaat er mis in «¡Qué una pena!»?",
    vEn:"What is wrong with «¡Qué una pena!»?",
    o:["Er hoort geen lidwoord achter qué","Pena moet penas zijn","Er hoort een werkwoord bij","Het moet cuál zijn"],
    oEn:["No article goes after qué","Pena should be penas","It needs a verb","It should be cuál"],
    g:0,
    w:"Het Nederlands zegt “wat een jammer”, het Spaans laat het lidwoord weg: ¡Qué pena!",
    wEn:"English says “what a shame”; Spanish drops the article: ¡Qué pena!"},
  patronen:[
   function(){ var z = gcKies(GC_UITROEP_ZN);
     return {v:"___ (" + z.nl + ")", vEn:"___ (" + z.en + ")",
             o:["¡Qué " + z.es + "!", "¡Qué una " + z.es + "!", "¡Qué la " + z.es + "!"], g:0,
             w:"Geen lidwoord na qué. Dat het Nederlands “wat een” zegt is precies de val.",
             wEn:"No article after qué. That English says “what a” is exactly the trap."}; },
   function(){ var a = gcKies(GC_UITROEP);
     return {v:"___ (Wat " + a.nl + "!)", vEn:"___ (How " + a.en + "!)",
             o:["¡Qué " + a.adj + "!", "¡Qué el " + a.adj + "!", "¡Cómo " + a.adj + "!"], g:0,
             w:"Qué + bijvoeglijk naamwoord, verder niets.",
             wEn:"Qué + adjective, nothing else."}; },
   function(){ var a = gcKies(GC_UITROEP);
     return {v:"¡Qué día ___ " + a.adj + "! (Wat een " + a.nlB + " dag!)",
             vEn:"¡Qué día ___ " + a.adj + "! (What a " + a.en + " day!)",
             o:["más", "muy", "mucho"], g:0,
             w:"Staat er een zelfstandig naamwoord tussen, dan komt het bijvoeglijk naamwoord erachter met más of tan ertussen.",
             wEn:"With a noun in between, the adjective goes after, with más or tan between them."}; }
  ]},

'''

GUSTARFAM = r''' /* v23.194: kaart 18 en 23 in één les. Allebei die kaarten zeggen letterlijk "werkt grammaticaal
    precies als gustar", dus het is één regel en niet twee. Twee lessen schrijven voor één regel is
    dezelfde fout als twee codeplekken die hetzelfde doen. */
 {id:"gustarfamilie", icon:"🫀", naam:"Werkt net als gustar", naamEn:"Works just like gustar",
  corr:[], spiek:{a2:[18,23]}, wizard:null,
  uitleg:"<p>Je kent <i>me gusta</i> al. Er is een hele familie werkwoorden die precies zo werkt, en dat scheelt je vier regels: <b>doler</b> (pijn doen), <b>encantar</b> (geweldig vinden), <b>apetecer</b> (zin hebben in) en <b>parecer</b> (vinden van).</p>"+
    "<p>Bij die werkwoorden is <b>niet de persoon het onderwerp</b> maar het ding. Je zegt dus letterlijk “mij doet het hoofd pijn”:</p>"+
    "<p><i>Me duele <b>la cabeza</b>.</i> — één ding, dus <b>duele</b>.<br>"+
    "<i>Me duelen <b>los pies</b>.</i> — meer dingen, dus <b>duelen</b>.</p>"+
    "<p>Het voornaamwoord ervoor zegt om wie het gaat: me, te, le, nos, os, les. Dat verandert niets aan het werkwoord.</p>"+
    "<p><i>¿Qué te parece el plan? — Me parece bien.</i> En: <i>Nos encantan las fiestas.</i></p>"+
    "<p>Pas op met <i>parecerse a</i>: dat is een ander werkwoord en betekent “lijken op”. <i>Me parezco a mi madre.</i></p>",
  uitlegEn:"<p>You already know <i>me gusta</i>. A whole family of verbs works exactly the same way, which saves you four rules: <b>doler</b> (to hurt), <b>encantar</b> (to love), <b>apetecer</b> (to fancy) and <b>parecer</b> (to think of).</p>"+
    "<p>With these verbs <b>the person is not the subject</b>, the thing is. So you literally say “to me hurts the head”:</p>"+
    "<p><i>Me duele <b>la cabeza</b>.</i> — one thing, so <b>duele</b>.<br>"+
    "<i>Me duelen <b>los pies</b>.</i> — more things, so <b>duelen</b>.</p>"+
    "<p>The pronoun in front says who it is about: me, te, le, nos, os, les. It changes nothing about the verb.</p>"+
    "<p><i>¿Qué te parece el plan? — Me parece bien.</i> And: <i>Nos encantan las fiestas.</i></p>"+
    "<p>Careful with <i>parecerse a</i>: a different verb, meaning “to look like”. <i>Me parezco a mi madre.</i></p>",
  begrip:{v:"Waarom is het «me duelen los pies» en niet «me duele»?",
    vEn:"Why is it «me duelen los pies» and not «me duele»?",
    o:["Omdat los pies meervoud is en het onderwerp","Omdat ik meervoud ben","Omdat voeten altijd meervoud zijn","Omdat doler onregelmatig is"],
    oEn:["Because los pies is plural and is the subject","Because I am plural","Because feet are always plural","Because doler is irregular"],
    g:0,
    w:"Het werkwoord volgt het ding dat erna komt, niet de persoon ervoor. Eén ding: duele. Meer dingen: duelen.",
    wEn:"The verb follows the thing that comes after, not the person before it. One thing: duele. More: duelen."},
  patronen:[
   function(){ var w = gcKies(GC_GUSTARFAM), mv = Math.random() < 0.5;
     var ding = mv ? w.dMv : w.dEnk, dingNl = mv ? w.dMvNl : w.dEnkNl, goed = mv ? w.mv : w.enk;
     var st = w.st || "";
     return {v:"Me ___ " + st + ding + ". (" + gcHoofd(dingNl) + ", " + w.nl + ")",
             vEn:"Me ___ " + st + ding + ". (" + dingNl + ", " + w.en + ")",
             o:[goed, mv ? w.enk : w.mv], g:0,
             w:ding + " is " + (mv ? "meervoud" : "enkelvoud") + ", dus " + goed + ". Het werkwoord kijkt naar wat erna staat.",
             wEn:ding + " is " + (mv ? "plural" : "singular") + ", so " + goed + ". The verb looks at what follows."}; },
   function(){ var w = gcKies(GC_GUSTARFAM);
     return {v:"Wat is het onderwerp in «me " + w.enk + " " + (w.st || "") + w.dEnk + "»?",
             vEn:"What is the subject in «me " + w.enk + " " + (w.st || "") + w.dEnk + "»?",
             o:[w.dEnk, "me", w.ww], oEn:[w.dEnk, "me", w.ww], g:0,
             w:"Het ding is het onderwerp, niet de persoon. Daarom stemt het werkwoord daarop af.",
             wEn:"The thing is the subject, not the person. That is why the verb agrees with it."}; },
   function(){
     return {v:"¿Qué te parece el plan? Welk antwoord klopt?",
             vEn:"¿Qué te parece el plan? Which answer is right?",
             o:["Me parece bien.","Yo parezco bien el plan.","Me parezco al plan.","El plan me parezco."],
             oEn:["Me parece bien.","Yo parezco bien el plan.","Me parezco al plan.","El plan me parezco."],
             g:0,
             w:"Parecer werkt als gustar: me parece. Me parezco a is iets anders en betekent “ik lijk op”.",
             wEn:"Parecer works like gustar: me parece. Me parezco a is different and means “I look like”."}; }
  ]},

'''

SEIMP = r''' /* v23.194: kaart 21. Staat na reflexivo, want dat is dezelfde se en juist daar zit de verwarring. */
 {id:"seimpersonal", icon:"🍲", naam:"Se: hoe iets gedaan wordt", naamEn:"Se: how something is done",
  corr:[], spiek:{a2:[21]}, wizard:null,
  uitleg:"<p>In recepten en algemene regels zeg je vaak niet wíé iets doet, alleen wát er gebeurt. Daar is <b>se</b> voor.</p>"+
    "<p><i>Se cocina el arroz.</i> — de rijst wordt gekookt.<br><i>Se venden pisos.</i> — er worden appartementen verkocht.</p>"+
    "<p><b>En dit is de hele regel:</b> het werkwoord stemt af op wat er <b>ná</b> se staat, niet op wie het doet.</p>"+
    "<p>Eén ding → derde persoon enkelvoud: <i>se necesita una cuchara</i>.<br>Meer dingen → derde persoon meervoud: <i>se necesitan dos cucharadas</i>.</p>"+
    "<p>In het Nederlands vertaal je het meestal met een lijdende vorm (“wordt gekookt”) of met “je”: <i>Aquí se habla español</i> = hier wordt Spaans gesproken, of: hier spreken ze Spaans.</p>"+
    "<p>Verwar het niet met de reflexieve se (<i>se lava</i> = hij wast zich). Daar is er wél iemand die het doet.</p>",
  uitlegEn:"<p>In recipes and general rules you often do not say <b>who</b> does something, only what happens. That is what <b>se</b> is for.</p>"+
    "<p><i>Se cocina el arroz.</i> — the rice is cooked.<br><i>Se venden pisos.</i> — flats are sold here.</p>"+
    "<p><b>And this is the whole rule:</b> the verb agrees with what comes <b>after</b> se, not with who does it.</p>"+
    "<p>One thing → third person singular: <i>se necesita una cuchara</i>.<br>More things → third person plural: <i>se necesitan dos cucharadas</i>.</p>"+
    "<p>English usually uses a passive (“is cooked”) or “you”: <i>Aquí se habla español</i> = Spanish is spoken here.</p>"+
    "<p>Do not mix it up with reflexive se (<i>se lava</i> = he washes himself). There, someone is doing it.</p>",
  begrip:{v:"Waar kijkt het werkwoord naar bij se impersonal?",
    vEn:"What does the verb agree with in the impersonal se?",
    o:["Naar wat er ná se staat","Naar wie het doet","Naar de tijd van de zin","Naar het geslacht van se"],
    oEn:["With what comes after se","With who is doing it","With the tense","With the gender of se"],
    g:0,
    w:"Se cocina el arroz, maar se cocinan las patatas. Het ding erna bepaalt enkelvoud of meervoud.",
    wEn:"Se cocina el arroz, but se cocinan las patatas. The thing after it decides singular or plural."},
  patronen:[
   function(){ var w = gcKies(GC_SEIMP), mv = Math.random() < 0.5;
     var ding = mv ? w.dMv : w.dEnk, dingNl = mv ? w.dMvNl : w.dEnkNl, goed = mv ? w.mv : w.enk;
     return {v:"___ " + ding + ". (" + gcHoofd(dingNl) + " " + (mv ? "worden" : "wordt") + " " + w.nl + ".)",
             vEn:"___ " + ding + ". (" + gcHoofd(dingNl) + " " + (mv ? "are" : "is") + " " + w.en + ".)",
             o:[goed, mv ? w.enk : w.mv], g:0,
             w:ding + " is " + (mv ? "meervoud" : "enkelvoud") + ", dus " + goed + ".",
             wEn:ding + " is " + (mv ? "plural" : "singular") + ", so " + goed + "."}; },
   function(){
     return {v:"Wat betekent «Aquí se habla español»?",
             vEn:"What does «Aquí se habla español» mean?",
             o:["Hier wordt Spaans gesproken","Hij spreekt hier Spaans tegen zichzelf","Spreek hier Spaans!","Hier spreek ik Spaans"],
             oEn:["Spanish is spoken here","He speaks Spanish to himself here","Speak Spanish here!","I speak Spanish here"],
             g:0,
             w:"Se zonder duidelijke dader: er staat niet wie het doet, alleen dat het gebeurt.",
             wEn:"Se without a clear doer: it does not say who, only that it happens."}; },
   function(){
     return {v:"Welke zin heeft de reflexieve se en niet de onpersoonlijke?",
             vEn:"Which sentence has the reflexive se, not the impersonal one?",
             o:["Se lava las manos.","Se venden pisos.","Se cocina el arroz.","Se habla español."],
             oEn:["Se lava las manos.","Se venden pisos.","Se cocina el arroz.","Se habla español."],
             g:0,
             w:"Bij se lava is er iemand die iets met zichzelf doet. Bij de andere drie staat niet wie het doet.",
             wEn:"In se lava someone is doing something to themselves. The other three do not say who."}; }
  ]},

'''

CANTIDAD = r''' /* v23.194: kaart 22. Half woordenlijst, half regel: demasiado buigt mee en bastante niet, en dat
    is precies de fout die je in een recept maakt. Staat na muymucho, dezelfde familie. */
 {id:"cantidad", icon:"🥄", naam:"Een beetje, genoeg, te veel", naamEn:"A bit, enough, too much",
  corr:[], spiek:{a2:[22]}, wizard:null,
  uitleg:"<p>Vaste uitdrukkingen voor hoeveelheden. De eerste drie krijgen altijd <b>de</b> achter zich:</p>"+
    "<p><i>una pizca <b>de</b> sal</i> (een snufje) — <i>un poco <b>de</b> azúcar</i> (een beetje) — <i>una cucharada <b>de</b> aceite</i> (een eetlepel).</p>"+
    "<p><b>bastante</b> = genoeg, behoorlijk wat. Die verandert nooit van vorm en kan ook alleen staan: <i>Tengo bastante tiempo.</i> — <i>Ya es bastante.</i></p>"+
    "<p><b>demasiado</b> = te veel, en die <b>buigt wél mee</b> met het woord erachter: <i>demasiad<b>a</b> sal</i>, <i>demasiad<b>o</b> azúcar</i>.</p>"+
    "<p>Dat verschil is het enige wat je hier hoeft te onthouden: bastante blijft, demasiado beweegt.</p>",
  uitlegEn:"<p>Set expressions for quantities. The first three always take <b>de</b>:</p>"+
    "<p><i>una pizca <b>de</b> sal</i> (a pinch) — <i>un poco <b>de</b> azúcar</i> (a bit) — <i>una cucharada <b>de</b> aceite</i> (a spoonful).</p>"+
    "<p><b>bastante</b> = enough, quite a lot. It never changes form and can stand alone: <i>Tengo bastante tiempo.</i> — <i>Ya es bastante.</i></p>"+
    "<p><b>demasiado</b> = too much, and it <b>does</b> agree with the word behind it: <i>demasiad<b>a</b> sal</i>, <i>demasiad<b>o</b> azúcar</i>.</p>"+
    "<p>That difference is the only thing to remember here: bastante stays put, demasiado moves.</p>",
  begrip:{v:"Welke van de twee verandert mee met het woord erachter?",
    vEn:"Which of the two agrees with the word behind it?",
    o:["demasiado","bastante","allebei","geen van beide"],
    oEn:["demasiado","bastante","both","neither"],
    g:0,
    w:"Demasiada sal, demasiado azúcar. Bastante blijft altijd bastante.",
    wEn:"Demasiada sal, demasiado azúcar. Bastante always stays bastante."},
  patronen:[
   function(){ var s = gcKies(GC_CANT);
     var goed = s.g === "f" ? "demasiada" : "demasiado";
     return {v:"Has puesto ___ " + s.es + ". (Je hebt te veel " + s.nl + " gebruikt.)",
             vEn:"Has puesto ___ " + s.es + ". (You have used too much " + s.en + ".)",
             o:[goed, s.g === "f" ? "demasiado" : "demasiada"], g:0,
             w:s.es + " is " + (s.g === "f" ? "vrouwelijk" : "mannelijk") + ", dus " + goed + ".",
             wEn:s.es + " is " + (s.g === "f" ? "feminine" : "masculine") + ", so " + goed + "."}; },
   /* de opties zijn hele stukjes en geen losse woorden: een keuzeknop met een streepje erop
      ("hier hoort niets") vraagt zelf om uitleg, en dat is niet waar deze vraag over gaat. */
   function(){ var s = gcKies(GC_CANT);
     return {v:"___ (een beetje " + s.nl + ")",
             vEn:"___ (a bit of " + s.en + ")",
             o:["un poco de " + s.es, "un poco " + s.es, "un poco que " + s.es], g:0,
             w:"Un poco de + zelfstandig naamwoord. Net als una pizca de en una cucharada de.",
             wEn:"Un poco de + noun. Just like una pizca de and una cucharada de."}; },
   function(){ var s = gcKies(GC_CANT);
     return {v:"Tengo ___ " + s.es + ", no hace falta más. (Ik heb genoeg " + s.nl + ".)",
             vEn:"Tengo ___ " + s.es + ", no hace falta más. (I have enough " + s.en + ".)",
             o:["bastante", "bastanta", "bastante de"], g:0,
             w:"Bastante verandert nooit van vorm en heeft hier geen de nodig.",
             wEn:"Bastante never changes form and does not need de here."}; },
   function(){
     return {v:"Kan «bastante» ook zonder zelfstandig naamwoord?",
             vEn:"Can «bastante» stand without a noun?",
             o:["Ja: Ya es bastante.","Nee, er moet altijd een woord achter","Alleen in vragen","Alleen met de erachter"],
             oEn:["Yes: Ya es bastante.","No, a noun must always follow","Only in questions","Only with de after it"],
             g:0,
             w:"Ya es bastante = het is al genoeg. Bastante kan prima alleen staan.",
             wEn:"Ya es bastante = that is enough already. Bastante is fine on its own."}; }
  ]},

'''

if DOE_APP:
    # elk concept vlak vóór het concept waar het achter hoort te komen in de arrayvolgorde is niet
    # nodig: GC_ORDE bepaalt de volgorde. Ze gaan allemaal vóór apersonal de lijst in.
    rep(' {id:"apersonal", icon:',
        TIJDMARK + POSESIVO + EXCLAM + GUSTARFAM + SEIMP + CANTIDAD + ' {id:"apersonal", icon:')

# =============================================================================================
# 3. de twee aanhechtingen, mét de uitleg erbij
# =============================================================================================
if DOE_APP:
    # kaart 4: de signaalwoorden van perfecto tegenover indefinido. Eerst de alinea, dan de kaart:
    # de les moet de woorden echt uitleggen voordat hij de kaart mag claimen.
    rep('"<p>Daarom kan hetzelfde moment allebei zijn: om elf uur zeg je <i>esta mañana he tomado café</i>, s avonds <i>esta mañana tomé café</i>.</p>",',
        '"<p>Daarom kan hetzelfde moment allebei zijn: om elf uur zeg je <i>esta mañana he tomado café</i>, s avonds <i>esta mañana tomé café</i>.</p>"+\n'
        '    "<p>Vier woorden verraden het vak zonder dat je hoeft na te denken. <b>Ya</b> (al) en <b>todavía no</b> (nog niet) meten tegen nu, dus perfecto: <i>ya he comido</i>, <i>todavía no he llamado</i>. <b>Alguna vez</b> (ooit) en <b>últimamente</b> (de laatste tijd) kijken over je hele leven of over de afgelopen weken, en die lopen ook nog: <i>¿Has estado alguna vez en Cuba?</i></p>"+\n'
        '    "<p>En andersom: <b>hace dos años</b> (twee jaar geleden) en <b>aquel día</b> (die dag) wijzen een punt aan dat voorbij is, net als ayer. Dus indefinido: <i>hace dos años viví en Madrid</i>. Let op de valkuil: hace lijkt op het Nederlandse “al”, maar het betekent geleden, en geleden is dicht.</p>",')
    rep('"<p>So the same moment can be either: at eleven you say <i>esta mañana he tomado café</i>, in the evening <i>esta mañana tomé café</i>.</p>",',
        '"<p>So the same moment can be either: at eleven you say <i>esta mañana he tomado café</i>, in the evening <i>esta mañana tomé café</i>.</p>"+\n'
        '    "<p>Four words give the frame away without any thinking. <b>Ya</b> (already) and <b>todavía no</b> (not yet) measure against now, so perfect: <i>ya he comido</i>, <i>todavía no he llamado</i>. <b>Alguna vez</b> (ever) and <b>últimamente</b> (lately) look across your whole life or the past few weeks, and those are still running too: <i>¿Has estado alguna vez en Cuba?</i></p>"+\n'
        '    "<p>The other way round: <b>hace dos años</b> (two years ago) and <b>aquel día</b> (that day) point at a spot that is over, just like ayer. So preterite: <i>hace dos años viví en Madrid</i>. Watch out: hace means ago, and ago is closed.</p>",')

    anker4 = 'spiek:{a2:[0,5,27], a0:[21]}'
    assert src.count(anker4) == 1, "perfindef-spiek niet gevonden"
    src = src.replace(anker4, 'spiek:{a2:[0,5,27,4], a0:[21]}')

    # kaart 28: de verbindingswoorden van een anekdote. Ze stonden in de les als losse "signalen";
    # nu staan ze er als het skelet van een verhaal, want dat is waar de kaart voor is.
    rep('"<p>Signalen voor imperfecto: de niño, antes, siempre, todos los días, mientras. Signalen voor indefinido: ayer, de repente, un día, en 2019.</p>",',
        '"<p>Signalen voor imperfecto: de niño, antes, siempre, todos los días, mientras. Signalen voor indefinido: ayer, de repente, un día, en 2019.</p>"+\n'
        '    "<p>Vier woorden dragen een anekdote van begin tot eind, en ze kiezen de tijd voor je. <b>Un día</b> of <b>una vez</b> opent (indefinido: <i>Un día perdí el móvil</i>). <b>Mientras</b> zet er decor omheen, dus imperfecto: <i>mientras esperaba el autobús</i>. <b>De repente</b> knalt er een gebeurtenis in, dus indefinido: <i>de repente lo vi en el suelo</i>. En <b>al final</b> sluit af, ook indefinido: <i>al final lo encontré</i>.</p>"+\n'
        '    "<p>Zo hoef je niet per zin te kiezen: mientras plakt aan het decor, de andere drie aan de gebeurtenissen.</p>",')
    rep('"<p>Imperfect signals: de niño, antes, siempre, todos los días, mientras. Preterite signals: ayer, de repente, un día, en 2019.</p>",',
        '"<p>Imperfect signals: de niño, antes, siempre, todos los días, mientras. Preterite signals: ayer, de repente, un día, en 2019.</p>"+\n'
        '    "<p>Four words carry an anecdote from start to finish, and they pick the tense for you. <b>Un día</b> or <b>una vez</b> opens (preterite: <i>Un día perdí el móvil</i>). <b>Mientras</b> paints the scene around it, so imperfect: <i>mientras esperaba el autobús</i>. <b>De repente</b> drops an event into it, so preterite: <i>de repente lo vi en el suelo</i>. And <b>al final</b> closes, preterite as well: <i>al final lo encontré</i>.</p>"+\n'
        '    "<p>That way you do not choose per sentence: mientras sticks to the scene, the other three to the events.</p>",')

    anker28 = 'spiek:{a2:[14,15,16,26]}'
    assert src.count(anker28) == 1, "indefimperf-spiek niet gevonden"
    src = src.replace(anker28, 'spiek:{a2:[14,15,16,26,28]}')

# =============================================================================================
# 4. de leervolgorde
# =============================================================================================
if DOE_APP:
    rep('  "muymucho",        // muy of mucho: kijk naar het woord erachter\n',
        '  "muymucho",        // muy of mucho: kijk naar het woord erachter\n'
        '  "cantidad",        // v23.194: dezelfde familie, en demasiado buigt net als mucho\n')
    rep('  "gustar",          // gusta of gustan\n',
        '  "gustar",          // gusta of gustan\n'
        '  "gustarfamilie",   // v23.194: dezelfde constructie, met doler, encantar, apetecer, parecer\n')
    rep('  "demostrativo",    // este, ese, aquel\n',
        '  "demostrativo",    // este, ese, aquel\n'
        '  "posesivo",        // v23.194: el mio, la tuya - buigt met het ding mee, net als deze\n')
    rep('  "reflexivo",       // me, te, se\n',
        '  "reflexivo",       // me, te, se\n'
        '  "seimpersonal",    // v23.194: dezelfde se, en daar zit precies de verwarring\n')
    rep('  "comparar",        // mas que, tan como\n',
        '  "comparar",        // mas que, tan como\n'
        '  "exclamacion",     // v23.194: klein en losstaand, dus niet achteraan wegstoppen\n')
    rep('  "porpara",         // por of para\n',
        '  "porpara",         // por of para\n'
        '  "tijdmarkers",     // v23.194: de signaalwoorden komen voor de regel die ze aanwijzen\n')

# =============================================================================================
# 5. de ezelsbruggen
# =============================================================================================
HULP = r''' tijdmarkers:{
  kern:"Hace = geleden, en dat is klaar: indefinido. Desde en desde hace lopen nog door: presente. Durante is een afgesloten periode: indefinido.",
  kernEn:"Hace = ago, and that is finished: indefinido. Desde and desde hace are still going: presente. Durante is a closed period: indefinido.",
  brug:"Loopt het nog? Dan tegenwoordige tijd, hoe lang het ook al duurt. Het Spaans telt niet hoe lang iets al bezig is, alleen óf het nog bezig is.",
  brugEn:"Still going? Then present tense, however long it has lasted. Spanish does not count how long, only whether it is still going.",
  mis:"Het Nederlands zegt “ik leer al een jaar” en dat voelt als verleden tijd. In het Spaans is het presente, want je leert nog steeds.",
  misEn:"English says “I have been studying” and that feels like a past form. In Spanish it is the present, because you are still studying."},
 posesivo:{
  kern:"Lidwoord + bezitsvorm als het ding al genoemd is: el mío, la tuya, los nuestros. Na ser valt het lidwoord weg: es mío.",
  kernEn:"Article + possessive once the thing has been mentioned: el mío, la tuya, los nuestros. After ser the article drops: es mío.",
  brug:"Het bezit kijkt naar het ding, niet naar de baas. Een man met een casa zegt la mía.",
  brugEn:"The possessive looks at the thing, not at the owner. A man with a casa says la mía.",
  mis:"Bijna iedereen kiest op de eigenaar: el mío omdat ik een man ben. Het Spaans kijkt naar het woord waar je het over hebt.",
  misEn:"Almost everyone goes by the owner: el mío because I am male. Spanish looks at the word you are talking about."},
 exclamacion:{
  kern:"¡Qué + adjectief of zelfstandig naamwoord, zonder lidwoord. Zit er een zelfstandig naamwoord tussen, dan komt het adjectief erachter met más of tan.",
  kernEn:"¡Qué + adjective or noun, no article. With a noun in between, the adjective follows with más or tan.",
  brug:"Qué duldt niks tussen zichzelf en het woord. Geen un, geen una, geen el.",
  brugEn:"Qué allows nothing between itself and the word. No un, no una, no el.",
  mis:"Het Nederlands zegt “wat een pech”, dus je schrijft ¡Qué una pena! Precies dat lidwoord moet weg.",
  misEn:"English says “what a shame”, so you write ¡Qué una pena! That article is exactly what has to go."},
 gustarfamilie:{
  kern:"Doler, encantar, apetecer en parecer werken als gustar: het ding is het onderwerp. Eén ding → duele, meer dingen → duelen.",
  kernEn:"Doler, encantar, apetecer and parecer work like gustar: the thing is the subject. One thing → duele, more → duelen.",
  brug:"Kijk naar rechts. Wat er ná het werkwoord staat bepaalt de vorm; wat ervoor staat zegt alleen om wie het gaat.",
  brugEn:"Look to the right. What comes after the verb decides the form; what comes before only says who it is about.",
  mis:"Je maakt jezelf het onderwerp: me duelo, yo parezco bien. Het is andersom, en dat blijft raar voelen tot je het vertaalt met “mij doet het hoofd pijn”.",
  misEn:"You make yourself the subject: me duelo, yo parezco bien. It is the other way round, and it keeps feeling odd until you translate it as “to me hurts the head”."},
 seimpersonal:{
  kern:"Se + derde persoon, en het werkwoord volgt wat erna komt: se cocina el arroz, se cocinan las patatas.",
  kernEn:"Se + third person, and the verb follows what comes after: se cocina el arroz, se cocinan las patatas.",
  brug:"Se zegt niet wie, alleen wat. En het werkwoord kijkt vooruit, naar het ding.",
  brugEn:"Se does not say who, only what. And the verb looks ahead, at the thing.",
  mis:"Se venden pisos voelt fout omdat er geen zichtbare dader is, en dan schrijf je se vende. Het meervoud komt van pisos, niet van iemand.",
  misEn:"Se venden pisos feels wrong because there is no visible doer, so you write se vende. The plural comes from pisos, not from a person."},
 cantidad:{
  kern:"Una pizca de, un poco de en una cucharada de krijgen altijd de. Bastante verandert nooit; demasiado buigt mee met het woord erachter.",
  kernEn:"Una pizca de, un poco de and una cucharada de always take de. Bastante never changes; demasiado agrees with the word after it.",
  brug:"Bastante is een blok, demasiado is een elastiek. Het ene blijft, het andere rekt mee met sal of azúcar.",
  brugEn:"Bastante is a block, demasiado is elastic. One stays put, the other stretches to fit sal or azúcar.",
  mis:"Demasiado sal in plaats van demasiada sal. Sal ziet er mannelijk uit en is het niet.",
  misEn:"Demasiado sal instead of demasiada sal. Sal looks masculine and is not."},
'''

if DOE_APP:
    rep("var GC_HULP = {\n", "var GC_HULP = {\n" + HULP)

# =============================================================================================
# schrijven
# =============================================================================================
if DOE_APP:
    src = src.replace('var APP_VERSIE = "' + huidig_ver + '"', 'var APP_VERSIE = "' + NIEUW + '"')
    APP.write_text(src, encoding="utf-8")
    print("index.html: zes lessen erbij en twee kaarten aangehecht, versie " + NIEUW)
else:
    print("index.html: stond er al")

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt: " + huidig_ver + " -> " + NIEUW)
else:
    print("versie.txt: stond al op " + huidig_ver)
