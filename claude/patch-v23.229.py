#!/usr/bin/env python3
# v23.229 - de schil hangt aan de toestand, en de dagbalk zegt twee dingen
#
# Stefan, 2 sep: "als ik nu navigeer bijv naar woordjes of spelletjes dan mis ik nu wel de header
# met vamos Stefan, chispa en de zoekfunctie en ook de progress indicator (maar daar denk ik is
# wellicht een ander opzet nog beter, bijv dat je kan zien hoever je bent in je dagles maar ook tov
# je doel)."
#
# TWEE DINGEN, EN ZE HANGEN SAMEN
#
# 1. DE SCHIL
#
# v23.209 zette één veld in TABS (soort: taak of overzicht) en liet show() dat als data-schermsoort
# op body zetten. Op een taakscherm gaan de sitekop, de dagbalk en de voettekst weg. De meting
# daarachter was echt: op Stefans telefoon stond de eerste vraag op 221 van de 844 pixels, en
# daarboven stonden zijn naam, een zoekknop en een dagbalk.
#
# Alleen was de VRAAG te grof. Het tabblad besliste, terwijl de toestand hoort te beslissen.
# Woordjes tijdens je dagles is één opgave: daar geldt de meting. Woordjes waar je zelf naartoe
# klikt is geen opgave maar je eigen sessie, en dan is het wegnemen van je naam, je zoekknop en je
# dagbalk geen rust maar verlies. Precies wat Stefan meldt.
#
# Wat blijft staan: in een les gaat alles weg (het lesframe draagt daar zelf de stap en de uitgang,
# en de onderbalk is er sinds v23.155 ook niet), en een lopend spel in de speeltuin is ook één
# opgave. Wat verandert: buiten een les hebben Woordjes, Vertalen en het speeltuinmenu hun schil
# terug.
#
# Er komt geen tweede lijst bij. TABS blijft de bron; woorden/vertalen/speeltuin zijn daar nu
# gewoon een overzicht, chat en de weekmeting blijven altijd een opgave, en de speeltuin krijgt
# één regel data erbij die zegt wanneer hij bezig is (bezig: er loopt een spel).
#
# 2. DE DAGBALK
#
# Er stond "18/30 taco's · 42 dagen". Eén ding, en niet het ding waar je op dat moment in zit.
# Stefans eigen voorstel is beter: waar sta je in je dagles, en waar sta je tegenover je doel.
#
#     les 3/6 · 18/30 taco's · 42 dagen
#     les af ✓ · doel gehaald ✓ · 42 dagen
#     les nog te doen · 0/30 taco's
#
# De balk zelf blijft het dagdoel volgen, want dat is wat de dag sluit. De getallen van de les
# komen uit lesFlowStapNum/lesFlowStapTotaal en worden hier niet opnieuw opgeschreven: vier plekken
# die zelf "4" schreven was precies de fout die v23.135 opruimde.
#
# En let op de samenhang met punt 1: tijdens een lopende les is deze regel weg. Wat hier staat gaat
# dus altijd over een les die je gepauzeerd hebt, nog moet beginnen, of vandaag al afmaakte. Dat is
# geen beperking maar de reden dat het werkt: binnen de les vertelt het lesframe je waar je bent,
# buiten de les vertelt de dagbalk het.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.229"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = "function schermSoort(" not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # =========================================================================================
    # 1. de data: welk scherm is uit zichzelf een opgave, en wanneer is een scherm bezig
    # =========================================================================================
    rep("""  {id:"woorden", label:"Woordjes", soort:"taak"},
  {id:"vertalen", label:"Vertalen", soort:"taak"},""",
"""  {id:"woorden", label:"Woordjes", soort:"overzicht"},     // v23.229: buiten een les je eigen sessie
  {id:"vertalen", label:"Vertalen", soort:"overzicht"},    // v23.229: idem""")

    rep("""  {id:"speeltuin", label:"Speeltuin", soort:"taak"},""",
"""  /* v23.229: het speeltuinMENU is een pagina, een lopend SPEL is een opgave. Dat verschil zit in
     funView en nergens anders, dus staat het hier en niet in een if ergens in de schil. */
  {id:"speeltuin", label:"Speeltuin", soort:"overzicht", bezig:function(){ return !!funView; }},""")

    # =========================================================================================
    # 2. de schil: van tabblad naar toestand
    # =========================================================================================
    rep("""function tabSoort(id){
  for(var i = 0; i < TABS.length; i++){ if(TABS[i].id === id) return TABS[i].soort || "overzicht"; }
  return "overzicht";
}
""",
"""function tabSoort(id){
  for(var i = 0; i < TABS.length; i++){ if(TABS[i].id === id) return TABS[i].soort || "overzicht"; }
  return "overzicht";
}
/* ================= DE SCHIL HANGT AAN DE TOESTAND (v23.229) =================

   Stefan, 2 sep: "als ik nu navigeer bijv naar woordjes of spelletjes dan mis ik nu wel de header
   met vamos Stefan, chispa en de zoekfunctie en ook de progress indicator."

   v23.209 haalde de sitekop, de dagbalk en de voettekst weg op vijf tabbladen. De meting
   daarachter klopte (de eerste vraag stond op 221 van de 844 pixels), maar de vraag was te grof:
   het TABBLAD besliste, terwijl de TOESTAND hoort te beslissen. Woordjes tijdens je dagles is één
   opgave. Woordjes waar je zelf naartoe klikt is je eigen sessie, en dan is het wegnemen van je
   naam, je zoekknop en je dagbalk geen rust maar verlies.

   Drie regels, in deze volgorde:
     - loopt er een les, dan is elk scherm een opgave (het lesframe draagt de stap en de uitgang);
     - een scherm dat uit zichzelf één opgave is (chat, de weekmeting) blijft dat altijd;
     - een scherm dat bezig is (een lopend spel in de speeltuin) telt ook als opgave.

   Nog steeds zet één plek het attribuut, en nog steeds weet geen enkele renderfunctie ervan. */
function tabBezig(id){
  for(var i = 0; i < TABS.length; i++){
    if(TABS[i].id === id) return !!(TABS[i].bezig && TABS[i].bezig());
  }
  return false;
}
function schermSoort(id){
  if(lesFlow && lesFlow.stap) return "taak";
  if(tabSoort(id) === "taak") return "taak";
  return tabBezig(id) ? "taak" : "overzicht";
}
/* Welk scherm staat er nu? De tabs zijn de waarheid. Een tweede variabele die hetzelfde bijhoudt
   loopt er vroeg of laat naast, en dan verbergt de app zijn kop op een pagina. */
function schermNu(){
  for(var i = 0; i < TABS.length; i++){
    var el = document.getElementById("tab-" + TABS[i].id);
    if(el && !el.classList.contains("hidden")) return TABS[i].id;
  }
  return null;
}
function schilSync(tabId){
  try {
    var id = tabId || schermNu();
    if(id) document.body.setAttribute("data-schermsoort", schermSoort(id));
  } catch(e){}
  /* De dagbalk hoort bij de schil, en hij zegt sinds v23.229 waar je dagles staat. Dan moet hij
     ook op dezelfde momenten opnieuw geschreven worden: tot nu toe gebeurde dat alleen als je
     punten veranderden, en dan stond er na het pauzeren van je les nog de stand van daarvoor. */
  try { if(document.getElementById("goalTxt")) updateGoalUI(); } catch(e){}
}
""")

    # de enige plek die het attribuut zette, zet het nu via de toestand
    rep("""  /* v23.209: de enige plek die de soort zet. Alles wat de schil doet hangt hieraan, en geen enkele
     renderfunctie weet ervan. Een regel die voor zeventien schermen geldt, hoort door één plek
     afgedwongen te worden. */
  try { document.body.setAttribute("data-schermsoort", tabSoort(tabId)); } catch(e){}""",
"""  /* v23.209/v23.229: de enige plek die de soort zet. Alles wat de schil doet hangt hieraan, en
     geen enkele renderfunctie weet ervan. Een regel die voor zeventien schermen geldt, hoort door
     één plek afgedwongen te worden. Sinds v23.229 kijkt hij ook naar de toestand, en daarom staan
     de twee andere aanroepen hieronder: een les die start of stopt en een spel dat begint of
     eindigt wisselen van soort zonder dat er een tabblad verandert. */
  schilSync(tabId);""")

    # een les die start of stopt wisselt van soort zonder tabwissel
    rep("""  if(!lesFrameAan()){
    el.innerHTML = "";
    el.classList.add("leeg");
    document.body.classList.remove("in-les");
    return;
  }
  el.classList.remove("leeg");
  document.body.classList.add("in-les");""",
"""  if(!lesFrameAan()){
    el.innerHTML = "";
    el.classList.add("leeg");
    document.body.classList.remove("in-les");
    schilSync();                 // v23.229: de les is uit, dus je schil komt terug
    return;
  }
  el.classList.remove("leeg");
  document.body.classList.add("in-les");
  schilSync();                   // v23.229: in een les is elk scherm één opgave""")

    # en een spel dat begint of eindigt ook
    rep("""function renderFun(){
  var el = document.getElementById("funCard");
  if(!el) return;
  if(duelCur){ renderDuel(); return; }""",
"""function renderFun(){
  var el = document.getElementById("funCard");
  if(!el) return;
  /* v23.229: hier wisselt het speeltuinmenu met een lopend spel, zonder dat show() eraan te pas
     komt. Zonder deze regel houdt de speeltuin de schil van het vorige scherm. */
  schilSync();
  if(duelCur){ renderDuel(); return; }""")

    # =========================================================================================
    # 3. de dagbalk zegt twee dingen
    # =========================================================================================
    rep("""function updateGoalUI(){""",
"""/* ================= WAAR STAAT JE DAGLES? (v23.229) =================

   Stefan: "wellicht is een ander opzet nog beter, bijv dat je kan zien hoever je bent in je dagles
   maar ook tov je doel."

   Drie toestanden en niet meer: af, halverwege, nog te doen. De getallen komen uit
   lesFlowStapNum/lesFlowStapTotaal; hier wordt geen enkel totaal opnieuw opgeschreven, want vier
   plekken die zelf "4" schreven was de fout die v23.135 opruimde.

   Halverwege betekent hier altijd een GEPAUZEERDE les, want tijdens een lopende les is de dagbalk
   weg (zie de schil hierboven). Dat is geen gat maar de verdeling: binnen de les vertelt het
   lesframe waar je bent, buiten de les vertelt de dagbalk het. */
function dagLesLabel(){
  var t = today();
  if(S.lesFlow && S.lesFlow[t]) return ct("les af ✓","lesson done ✓");
  var f = lesFlow;
  if(!f && S.lesFlowNu && S.lesFlowNu.d === t) f = S.lesFlowNu;
  if(f && f.stap){
    var n = 0, tot = 0;
    try { n = lesFlowStapNum(f); tot = lesFlowStapTotaal(f); } catch(e){ n = 0; tot = 0; }
    if(n > 0 && tot > 0) return ct("les ","lesson ") + n + "/" + tot;
  }
  return ct("les nog te doen","lesson to do");
}
function updateGoalUI(){""")

    rep("""  var dl = dagenLabel();
  document.getElementById("goalTxt").textContent =
    (x >= dagdoel() ? "doel gehaald ✓" : x + "/" + dagdoel() + " "+xpw()+"") + (dl ? " · " + dl : "");""",
"""  /* v23.229: de balk blijft het dagdoel, want dat is wat de dag sluit. De tekst zegt er nu bij
     waar je les staat, want dat is waar je aan begint als je de app opent. */
  var dl = dagenLabel();
  var stukken = [dagLesLabel(),
                 x >= dagdoel() ? ct("doel gehaald ✓","goal reached ✓")
                                : x + "/" + dagdoel() + " " + xpw()];
  if(dl) stukken.push(dl);
  document.getElementById("goalTxt").textContent = stukken.join(" · ");""")

    # de regel is langer geworden; de balk mag krimpen maar niet verdwijnen
    rep("""  .goalbar{flex:1; height:9px; background:var(--border); border-radius:99px; overflow:hidden;}""",
"""  /* v23.229: de tekst rechts is langer geworden (les én doel). De balk mag daarvoor krimpen, want
     de tekst draagt de getallen, maar hij mag niet tot nul krimpen: dan staat er een streepje van
     niets naast een zin, en dat leest als een fout. */
  .goalbar{flex:1 1 auto; min-width:48px; height:9px; background:var(--border);
           border-radius:99px; overflow:hidden;}""")

if DOE_APP:
    # =========================================================================================
    # de controles
    # =========================================================================================
    for nodig in ["function schermSoort(", "function tabBezig(", "function schermNu(",
                  "function schilSync(", "function dagLesLabel(",
                  'bezig:function(){ return !!funView; }']:
        assert nodig in src, "ontbreekt: " + nodig
    # hijsen straft dubbele namen af, dus elke naam precies één keer
    for naam in ["schermSoort", "tabBezig", "schermNu", "schilSync", "dagLesLabel"]:
        c = src.count("function " + naam + "(")
        assert c == 1, "function %s staat %d keer in het bestand" % (naam, c)
    # het attribuut wordt nergens meer buiten schilSync gezet
    assert src.count('setAttribute("data-schermsoort"') == 1, \
        "data-schermsoort wordt op meer dan één plek gezet"
    assert 'setAttribute("data-schermsoort", tabSoort(' not in src, \
        "show() zet de soort nog steeds per tabblad"
    # en schilSync wordt op de drie plekken aangeroepen die van toestand kunnen wisselen
    assert src.count("schilSync(") == 5, \
        "schilSync wordt %d keer genoemd (verwacht 5: 1 definitie + 4 aanroepen)" % src.count("schilSync(")
    # de drie schermen die Stefan noemde staan niet langer als taak in de data
    tabs = src[src.index("var TABS = ["):src.index("function tabSoort(")]
    for id_ in ["woorden", "vertalen", "speeltuin"]:
        regel = [r for r in tabs.split("\n") if '{id:"' + id_ + '"' in r][0]
        assert 'soort:"taak"' not in regel, id_ + " staat nog als taak in TABS: " + regel.strip()
    for id_ in ["chat", "meting"]:
        regel = [r for r in tabs.split("\n") if '{id:"' + id_ + '"' in r][0]
        assert 'soort:"taak"' in regel, id_ + " is geen opgave meer: " + regel.strip()
    # de dagbalk noemt de les én het doel
    blok = src[src.index("function dagLesLabel("):src.index("var toastTimer")]
    for nodig in ["les af ✓", "les nog te doen", "lesFlowStapNum(f)", "lesFlowStapTotaal(f)",
                  "stukken.join(\" · \")"]:
        assert nodig in blok, "de dagbalk mist: " + nodig
    assert "/4" not in blok and '"4"' not in blok, "er staat een handgeschreven totaal in de dagbalk"
    APP.write_text(src, encoding="utf-8")
    print("index.html: de schil volgt de toestand, en de dagbalk zegt les én doel")
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
