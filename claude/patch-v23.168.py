#!/usr/bin/env python3
# v23.168 - de correctielaag, eerste helft
#
# Dit is de eerste ronde onder de leerpoort, en de kaart erachter staat in het project:
# "Leerkaart - de correctielaag, en waarom versie 1 sneuvelde". Versie 1 van die kaart stelde een
# raadronde voor (fout aanwijzen, niet verbeteren, één nieuwe poging). Die is aangevallen en
# gesneuveld. Wat hier gebouwd wordt is versie 2, en die is kleiner en goedkoper.
#
# WAAROM GEEN RAADRONDE
#
# Vier bezwaren hielden stand:
#   - Li 2010, de meta-analyse waar versie 1 op leunde, vindt dat impliciete feedback (waar recasts
#     onder vallen) juist BETER behouden bleef over tijd. Versie 1 wees de goedkope recast af met
#     "die blijft slechter hangen", en dat is niet wat die bron zegt.
#   - Truscott & Hsu 2008 heeft precies dit ontwerp al uitgevoerd: fouten onderstreept, leerder
#     herstelt zelf. Beter in de revisie, en een week later op een nieuwe tekst gelijk aan de
#     controlegroep.
#   - Lyster & Saito draait op immersieklassen met kinderen, met leeftijd als moderator die de
#     andere kant op wijst. Li 2010 vindt lab groter dan klas en kort groter dan lang. Een
#     volwassene die dit maandenlang dagelijks doet zit aan de ongunstige kant van alle drie.
#   - Een verplichte raadronde beloont voorzichtig schrijven: korter en bekender levert minder
#     raadschermen op, en verlaagt het foutaandeel zonder dat er iets geleerd is.
#
# WAT ER WEL IN GAAT (Leeman 2003: salience-verhoogd positief bewijs deed het even goed als recasts,
# beide boven controle)
#
# A. DE VERGELIJKING. Bij een fout antwoord stond alleen de goede zin, met de afwijkende woorden
#    onderstreept. Je eigen zin was op dat moment al weg van het scherm. Je zag dus wat het moest
#    zijn zonder te zien wat jij schreef, en het verschil moest je uit je hoofd reconstrueren. Nu
#    staan ze onder elkaar, met aan beide kanten alleen het verschil gemarkeerd. Dat is dezelfde
#    informatie met minder werk om hem te zien, en dat is precies wat "salience" betekent.
#
# B. ÉÉN ACTIEVE STAP. Na een fout antwoord kun je de goede zin één keer overtypen. Dat is de
#    pushed output waar de prompt-theorie het werkzame deel legt, zonder de gokfase. Bewust een
#    aanbod en geen poort: de knop naar de volgende zin blijft staan. Levert geen XP op, want dan
#    zou overtypen gaan lonen boven het meteen goed hebben.
#
# C. DE VRAAG VAN DE DAG KRIJGT EEN ANTWOORD. Stefan, 22 aug: "deze is leuk maar hij corrigeert
#    niet mijn fout." Klopte: dagZinBij() knipte af op 140 tekens, sloeg op, gaf +4 XP en stuurde
#    het naar de groep. Geen check, geen fout gelogd, niets. Zijn zin stond ongecorrigeerd bij
#    Ilona en Martina op het scherm. Nu gaat hij langs /api/ai/chat (modus gesprek), waarvan het
#    veld `naast` precies hiervoor bestaat: wat er van de laatste zin van de leerling te zeggen
#    valt, in het Nederlands, náást het gesprek.
#
#    Twee dingen die dit met opzet NIET doet, allebei uit de aanval op de kaart:
#      - het blokkeert het plaatsen niet, en het verandert de XP niet. Een correctie die je post
#        tegenhoudt maakt schrijven duurder, en de bereidheid om vrij te schrijven is het schaarse
#        goed.
#      - er gaat niets van in S.errors. Taalmodellen halen op grammaticacorrectie ruwweg 52 tot 59
#        procent precisie met overcorrectie als bekend gedrag. Een gemiste fout kost bijna niets,
#        een verzonnen fout zou weken in de herhaalwachtrij worden gedrild. Dit is een mededeling
#        op het scherm, geen oordeel in je dossier.
#
# D. DE FOUT KRIJGT EEN IDENTITEIT. S.errors had een type ("zin"), en dat is de oefeningsoort en
#    geen fout. "Maak ik deze fout vaker" was daarmee onbeantwoordbaar. bestDiff() weet al welk
#    woord er hoorde en welk woord jij schreef (d.paren); dat paar gaat nu mee de foutregel in.
#    Dit bouwt niets zichtbaars, het maakt de meting van veld 6 op de kaart pas mogelijk.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.168"

src = APP.read_text(encoding="utf-8")
huidig_ver = VER.read_text(encoding="utf-8").strip()

def _num(v):
    return [int(x) for x in re.findall(r"\d+", v)]

DOE_APP = NIEUW not in src
DOE_VER = _num(huidig_ver) < _num(NIEUW)

def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:90])
    src = src.replace(anker, nieuw, n)

if DOE_APP:
    # -----------------------------------------------------------------------
    # A1. bestDiff geeft ook de kant van de leerling terug
    # -----------------------------------------------------------------------
    rep('''    var aTok = norm(a).split(" ");
    var m = 0, html = [], paren = [];
    for(var i=0;i<aTok.length;i++){
      var g = gTok[i] || "";
      if(stripAcc(g) === stripAcc(aTok[i])){ html.push(aTok[i]); }
      else {''',
        '''    var aTok = norm(a).split(" ");
    /* v23.168: gHtml is jouw zin met dezelfde markering, zodat de twee onder elkaar kunnen. Hier
       werd alleen de goede kant opgebouwd, en dat betekende dat je op het scherm wel zag wat het
       moest zijn maar niet meer wat jij schreef: je eigen zin was op dat moment al vervangen. Het
       verschil moest je dus uit je hoofd reconstrueren, en dat is precies het werk dat de
       markering had moeten besparen. */
    var m = 0, html = [], gHtml = [], paren = [];
    for(var i=0;i<aTok.length;i++){
      var g = gTok[i] || "";
      if(stripAcc(g) === stripAcc(aTok[i])){ html.push(aTok[i]); gHtml.push(g); }
      else {
        // een leeg g betekent: jouw zin was hier korter, dus er mist een woord
        gHtml.push("<span class='diffmis'>" + (g || "\\u00b7\\u00b7\\u00b7") + "</span>");''')

    rep('''    m += Math.max(0, gTok.length - aTok.length);
    if(best === null || m < best.m) best = {m:m, len:aTok.length, html:html.join(" "), paren:paren};''',
        '''    m += Math.max(0, gTok.length - aTok.length);
    // wat je meer schreef dan er hoorde staat ook fout, en anders verdwijnt het stilletjes
    for(var j = aTok.length; j < gTok.length; j++) gHtml.push("<span class='diffmis'>" + gTok[j] + "</span>");
    if(best === null || m < best.m) best = {m:m, len:aTok.length, html:html.join(" "),
                                            gHtml:gHtml.join(" "), paren:paren};''')

    # -----------------------------------------------------------------------
    # A2. de twee zinnen onder elkaar, op beide plekken waar een fout getoond wordt
    # -----------------------------------------------------------------------
    rep('''function bestDiff(given, s){''',
        '''/* v23.168: jouw zin en de goede zin onder elkaar, met alleen het verschil gemarkeerd.

   Grond: Leeman 2003 vond dat salience-verhoogd positief bewijs het even goed deed als recasts,
   beide boven controle. Dat is de goedkoopste ingreep met bewijs erachter: geen extra scherm, geen
   modelaanroep, geen raadronde. Zie de leerkaart in het project voor waarom de raadronde het niet
   heeft gehaald. */
function zinVergelijkHtml(d, jouw){
  return "<div class='zinvgl'>"+
    "<div class='zinvglrij'><span class='zinvgllbl'>"+ct("Jij","You")+"</span>"+
      "<span class='es'>"+(d.gHtml || veiligHtml(jouw || ""))+"</span></div>"+
    "<div class='zinvglrij'><span class='zinvgllbl'>"+ct("Goed","Correct")+"</span>"+
      "<span class='es'>"+d.html+"</span></div></div>";
}

function bestDiff(given, s){''')

    rep('''      html = "<div class='feedback bijna'>"+ct("Zó dichtbij! "+d.m+" woord"+(d.m>1?"en":"")+" wijkt af (onderstreept): ","So close! "+d.m+" word"+(d.m>1?"s":"")+" differ"+(d.m>1?"":"s")+" (underlined): ")+"<b>"+d.html+"</b> (+2 "+xpw()+")</div>"+''',
        '''      html = "<div class='feedback bijna'>"+ct("Zó dichtbij! "+d.m+" woord"+(d.m>1?"en":"")+" wijkt af: ","So close! "+d.m+" word"+(d.m>1?"s":"")+" differ"+(d.m>1?"":"s")+": ")+" (+2 "+xpw()+")"+zinVergelijkHtml(d, rauw)+"</div>"+''')

    rep('''      html = "<div class='feedback fout'>"+ct("Nog niet. Het antwoord is: ","Not yet. The answer is: ")+"<b>"+d.html+"</b></div>";
      logError(s.id, "zin", s.tag, given); addXP(1); retryable = true;''',
        '''      html = "<div class='feedback fout'>"+ct("Nog niet.","Not yet.")+zinVergelijkHtml(d, rauw)+"</div>";
      logError(s.id, "zin", s.tag, given, d.paren); addXP(1); retryable = true;''')

    # de bijna-treffer logt ook, en die krijgt dezelfde identiteit mee
    rep('''      addXP(2); retryable = true; vertWacht = true;
      logError(s.id, "zin", s.tag, given);''',
        '''      addXP(2); retryable = true; vertWacht = true;
      logError(s.id, "zin", s.tag, given, d.paren);''')

    # -----------------------------------------------------------------------
    # B. de goede zin één keer overtypen
    # -----------------------------------------------------------------------
    rep('''  html += "<div class='row'>"+
    (retryable ? "<button class='primary' id='btnRetry'>"+ct("Probeer opnieuw","Try again")+"</button>"+''',
        '''  /* v23.168: de goede zin één keer overtypen.

     Dit is de enige actieve stap die het ontwerp overhoudt, en hij staat er om wat de
     prompt-theorie het werkzame deel noemt: zelf de vorm produceren in plaats van hem alleen zien.
     Bewust een aanbod en geen poort, want een verplichte stap na elke fout maakt fout maken duurder
     en dat beloont voorzichtig schrijven. Bewust ook zonder XP: anders gaat overtypen lonen boven
     het meteen goed hebben, en dan optimaliseer je op de verkeerde uitkomst. */
  if(retryable){
    html += "<div class='overtyp' id='overTypBlok'>"+
      "<p class='muted' style='margin:0 0 6px; font-size:.9rem'>"+
        ct("Typ hem één keer over. Dat is het enige moment waarop je de goede vorm zelf maakt.",
           "Type it once. That is the only moment where you produce the correct form yourself.")+"</p>"+
      "<input type='text' id='sOverTyp' autocomplete='off' autocapitalize='off' spellcheck='false' "+
        "placeholder='"+veiligHtml(s.es)+"'>"+
      "<div class='row' style='margin-top:6px'><button class='ghost' id='btnOverTyp'>"+
        ct("Klaar","Done")+"</button></div>"+
      "<p class='muted' id='overTypFb' style='margin:6px 0 0; font-size:.9rem'></p></div>";
  }
  html += "<div class='row'>"+
    (retryable ? "<button class='primary' id='btnRetry'>"+ct("Probeer opnieuw","Try again")+"</button>"+''')

    rep('''  var br = document.getElementById("btnRetry");
  if(br) br.onclick = function(){ renderSentence(false); };''',
        '''  var br = document.getElementById("btnRetry");
  if(br) br.onclick = function(){ renderSentence(false); };
  /* v23.168: het overtypen. Geen XP, geen doos, geen fout: alleen ja of nog niet. Accenten worden
     door de vingers gezien, net als in de bijna-tak hierboven, want dit is een productiestap en
     geen spellingstoets. */
  var bot = document.getElementById("btnOverTyp"), iot = document.getElementById("sOverTyp");
  if(bot && iot){
    var otKlaar = function(){
      var fbo = document.getElementById("overTypFb");
      if(!fbo) return;
      var goed = stripAcc(norm(iot.value || "")) === stripAcc(norm(s.es));
      fbo.textContent = goed ? ct("Ja, zo is het. ✓","Yes, that is it. ✓")
                             : ct("Nog niet helemaal. Kijk nog eens naar de gemarkeerde woorden.",
                                  "Not quite. Look at the marked words again.");
      fbo.style.color = goed ? "var(--goed, #2e7d32)" : "";
      if(goed) iot.disabled = true;
    };
    bot.onclick = otKlaar;
    iot.onkeydown = function(e){ if(e.key === "Enter"){ e.preventDefault(); otKlaar(); } };
  }''')

    # -----------------------------------------------------------------------
    # C. de vraag van de dag krijgt een antwoord
    # -----------------------------------------------------------------------
    rep('''  h += "<div class='oogst'><b>"+muurEsc(ct("Jij","You"))+"</b> \\u00b7 <span class='es'>"+muurEsc(mijn.es)+"</span></div>";''',
        '''  h += "<div class='oogst'><b>"+muurEsc(ct("Jij","You"))+"</b> \\u00b7 <span class='es'>"+muurEsc(mijn.es)+"</span></div>";
  /* v23.168: en wat eraan mankeert, onder je eigen zin. Stefan, 22 aug: "deze is leuk maar hij
     corrigeert niet mijn fout." Dat klopte: er ging niets langs een check.
     Het staat er als mededeling en niet als oordeel: geen XP-gevolg, geen fout in S.errors, en het
     plaatsen wordt er niet door tegengehouden. Zie de kop van de patch voor waarom modeloordelen
     hier niet in je herhaalwachtrij mogen. */
  if(mijn.naast){
    h += "<p class='muted' style='margin:4px 0 8px; font-size:.88rem'>\\ud83e\\udd16 "+muurEsc(mijn.naast)+"</p>";
  } else if(mijn.wacht){
    h += "<p class='muted' style='margin:4px 0 8px; font-size:.88rem'>\\ud83e\\udd16 "+
      ct("Even kijken wat er van je zin te zeggen valt...","Let me see what there is to say about your sentence...")+"</p>";
  }''')

    rep('''  function zet(){
    if(!dagZinBij(inp.value)) return;
    var el = document.getElementById("dagzinCard");
    if(el){
      var n = document.createElement("div");
      n.innerHTML = dagZinHtml();
      if(n.firstChild){ el.parentNode.replaceChild(n.firstChild, el); dagZinWire(); }
    }
    try { muurGehaald = 0; muurHaal(); } catch(e){}
  }''',
        '''  function teken(){
    var el = document.getElementById("dagzinCard");
    if(!el) return;
    var n = document.createElement("div");
    n.innerHTML = dagZinHtml();
    if(n.firstChild){ el.parentNode.replaceChild(n.firstChild, el); dagZinWire(); }
  }
  function zet(){
    if(!dagZinBij(inp.value)) return;
    if(S.dagzin) S.dagzin.wacht = true;
    teken();
    try { muurGehaald = 0; muurHaal(); } catch(e){}
    /* v23.168: modus "gesprek" bestaat al en zijn veld `naast` is precies dit: wat er van de
       laatste zin van de leerling te zeggen valt, in het Nederlands. Eén beurt is genoeg; het
       antwoord van Chispa (res.es) laten we hier liggen, want deze kaart is voor je groep en niet
       voor een gesprek. Mislukt de aanroep, dan verdwijnt de wachtregel en staat er verder niets:
       een correctie die niet komt mag geen foutmelding worden. */
    try {
      api("/api/ai/chat", "POST", {modus:"gesprek", niveau:chatNiveau(),
                                   beurten:[{van:"jij", es:S.dagzin.es}]}).then(function(res){
        if(!S.dagzin) return;
        S.dagzin.wacht = false;
        if(res && res.ok && res.naast) S.dagzin.naast = String(res.naast).slice(0, 400);
        persist();
        teken();
      });
    } catch(e){ if(S.dagzin){ S.dagzin.wacht = false; teken(); } }
  }''')

    # C2. en de knop moet ook werken als de muur niet opnieuw wordt opgehaald
    #
    # Gevonden door de suite van deze ronde. dagZinWire() hangt aan het staartje van muurTeken(),
    # en muurTeken() draait alleen ná een geslaagde muurHaal(). Die slaat zichzelf over als er
    # binnen zestig seconden al opgehaald is. Wie dus wegklikt en binnen een minuut terugkomt, kreeg
    # de kaart wél getekend en de knop níét aangesloten: je typt je zin en er gebeurt niets.
    # Bestond al vóór vandaag; viel nu pas op omdat de kaart sinds v23.167 achter je les staat en
    # dus vaker opnieuw getekend wordt.
    rep('''  if(lesAf){ muurWire(); muurHaal(); }''',
        '''  if(lesAf){ muurWire(); muurHaal(); try { dagZinWire(); } catch(e){} }''')

    # -----------------------------------------------------------------------
    # D. de fout krijgt een identiteit
    # -----------------------------------------------------------------------
    rep('''function logError(id, type, tag, extra){''',
        '''function logError(id, type, tag, extra, paren){''')

    rep('''  S.errors[k].laatst = extra || today();
  S.errors[k].dag = today();
  trackPoging(true);''',
        '''  S.errors[k].laatst = extra || today();
  S.errors[k].dag = today();
  /* v23.168: welke fout, niet alleen welke oefening. `type` is de oefeningsoort ("zin"), dus de
     vraag "maak ik deze fout vaker" was onbeantwoordbaar: de app wist dat zin s142 fout ging en
     niet dát ser en estar door elkaar liepen. bestDiff() kent het paar al (wat er hoorde, wat jij
     schreef); het ging alleen nergens heen.
     Dit bouwt niets zichtbaars. Het is het haakje waar de meting aan hangt die moet uitwijzen of
     deze hele correctielaag iets doet, en zonder die meting is het volgende oordeel weer een
     vermoeden. Hoogstens vier paren, want dit staat in localStorage en groeit anders mee met elke
     lange zin. */
  if(paren && paren.length){
    S.errors[k].paren = paren.slice(0, 4).map(function(p){ return {v:p.v, g:p.g}; });
  }
  trackPoging(true);''')

    # -----------------------------------------------------------------------
    # E. de opmaak
    # -----------------------------------------------------------------------
    rep('''.diffword{''',
        '''/* v23.168: de twee zinnen onder elkaar. Vaste kolom voor het label, zodat de zinnen links
   uitlijnen en je oog het verschil per positie vindt in plaats van per woord. */
.zinvgl{margin:8px 0 2px}
.zinvglrij{display:flex; gap:8px; align-items:baseline; margin:2px 0}
.zinvgllbl{flex:0 0 42px; font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; opacity:.6}
.diffmis{text-decoration:line-through; text-decoration-thickness:1px; opacity:.75}
.overtyp{margin:10px 0 2px; padding:10px; border-radius:10px; background:rgba(127,127,127,.08)}
.overtyp input{width:100%}
.diffword{''')

    src = src.replace('var APP_VERSIE = "%s"' % huidig_ver, 'var APP_VERSIE = "%s"' % NIEUW)
    APP.write_text(src, encoding="utf-8")
    print("index.html: bijgewerkt naar", NIEUW)
else:
    print("index.html: al op", NIEUW)

if DOE_VER:
    VER.write_text(NIEUW + "\n", encoding="utf-8")
    print("versie.txt:", NIEUW)
else:
    print("versie.txt: al op", huidig_ver)
