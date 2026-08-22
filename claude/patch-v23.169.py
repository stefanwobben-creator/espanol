#!/usr/bin/env python3
# v23.169 - de leskaart is een introductie op dag 1 en verder alleen je plan
#
# Stefan, 22 aug, met zijn dagles open. Vier regels op de leskaart, en hij noemt ze één voor één:
#
#   "Sin prisa, pero sin pausa. Geen haast, maar wel doorgaan."
#       -> "we zouden Chispa zuiniger inzetten"
#   "Elke dag raak je alle vier de manieren aan waarop een taal binnenkomt..."
#       -> "deze zin is maar een keer nuttig om te lezen"
#   "Je route: De verleden tijd: indefinido of imperfecto. Nu: Zie je welke tijd er staat?, nog 3 stappen."
#       -> "dit snap ik niet? waarom zit ik in deze route? en als ik naar route ga kom ik uit mijn dagmodus"
#   "Daarna mag je Chispa 🥚 la tortilla española (aardappelomelet) geven."
#       -> "dit zegt me niet zoveel"
#
# HET PATROON, WANT HET IS ÉÉN FOUT EN GEEN VIER
#
# Alle vier zijn het teksten die op dag 1 iets uitleggen en vanaf dag 2 behang zijn. Chispa's spreuk
# stelt de app voor. De vier-draden-zin verantwoordt waarom je plan eruitziet zoals het eruitziet.
# De tapa-regel legt uit dat er een beloning bestaat. De routeregel vertelt dat er een route loopt.
# Stefan zit op dag 32. Hij heeft alle vier ongeveer dertig keer gelezen.
#
# Dat is dezelfde vorm als v23.167: een kaart die zijn eigen bestaan blijft uitleggen aan iemand die
# er al lang staat. De regel wordt dus: de leskaart is op dag 1 een introductie en zegt vanaf dag 2
# alleen nog wat je vandaag gaat doen.
#
# DE ROUTEREGEL, APART, WANT DAAR ZIT MEER
#
# Twee klachten in één zin, en allebei terecht.
#
# 1. "waarom zit ik in deze route?" De regel noemde een route en een stap en gaf geen enkele reden.
#    Die reden bestáát wel en staat al op de goede plek: gramWaaromHtml() (v23.143) zegt in de les
#    zelf waarom je dit onderwerp krijgt ("hier ging het 2 keer mis, dus je krijgt de hele uitleg",
#    "hier was je gebleven"). Wat er op de dagkaart stond was dus een aankondiging zonder reden,
#    terwijl de reden twee schermen verderop wél stond. Dat is de verkeerde volgorde: aankondigen
#    zonder uitleg wekt de vraag, en beantwoorden op het moment dat je bezig bent is genoeg.
#
# 2. "als ik naar route ga kom ik uit mijn dagmodus." Precies, en dat is sinds v23.167 een
#    ontwerpfout en geen ongemak: het dagscherm heeft een voorkant met één ding erop, en er stond
#    een knop op die je naar de Grammatica-tab bracht. De tweede voordeur die we net dichtdeden.
#
# De route verdwijnt niet. Hij loopt gewoon door als de grammaticastap van je dagles, en hij staat
# ná je les nog steeds als voorstel (routeVoorstel). Wat weggaat is de aankondiging vooraf.
#
# WAT DIT NIET IS
#
# Geen leerkaart onder de leerpoort, en dat is een oordeel dat ik hier expliciet maak zodat het
# nagekeken kan worden: er verandert geen enkele oefening, geen feedbackvorm, geen volgorde van
# stof. Vier teksten gaan weg van één scherm. De leerpoort is voor het leren, niet voor de opmaak,
# en hem hier toch aanroepen zou hem verwateren tot een formulier.
import re, pathlib

W = pathlib.Path(__file__).resolve().parents[1]
APP = W / "index.html"
VER = W / "versie.txt"
NIEUW = "v23.169"

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
    # 1. Chispa zegt niets meer op de leskaart
    # -----------------------------------------------------------------------
    rep('''        chispaZegHtml(
          (afgesloten ? "Hasta mañana." : hervat ? "Seguimos donde lo dejamos." : gedaanVandaag ? "¡Muy bien!" : groet.es),
          (afgesloten ? ct("Je bent klaar. Chispa slaapt zo lekker.","You're done. Chispa's off to sleep happy.")
            : hervat ? ct("We gaan verder waar we gebleven waren.","We pick up where we left off.")
            : gedaanVandaag ? ct("Chispa is trots op je.","Chispa is proud of you.")
            : ct(groet.nl, groet.en)))+''',
        '''        /* v23.169: alleen op dag 1. Stefan: "we zouden Chispa zuiniger inzetten."

           Wat hier stond was een begroeting plus een spreuk, en de kicker erboven zegt de toestand
           al ("Start je les", "Verder waar je was", "Klaar voor vandaag"). Op dag 1 stelt die regel
           Chispa voor en dat is werk; op dag 32 is het dezelfde spreuk voor de dertigste keer, en
           dan zegt hij alleen nog dat er een diertje bestaat.

           Chispa verdwijnt niet: ze staat als knop op deze kaart, ze praat in het gesprek, en ze
           krijgt haar tapa na je les. Dat zijn de twee plekken waar ze iets doet in plaats van iets
           zegt (prototype v3, beslissing 7). */
        (dagenTotaal() <= 1 ? chispaZegHtml(
          (afgesloten ? "Hasta mañana." : hervat ? "Seguimos donde lo dejamos." : gedaanVandaag ? "¡Muy bien!" : groet.es),
          (afgesloten ? ct("Je bent klaar. Chispa slaapt zo lekker.","You're done. Chispa's off to sleep happy.")
            : hervat ? ct("We gaan verder waar we gebleven waren.","We pick up where we left off.")
            : gedaanVandaag ? ct("Chispa is trots op je.","Chispa is proud of you.")
            : ct(groet.nl, groet.en))) : "")+''')

    # -----------------------------------------------------------------------
    # 2. de vier-draden-zin verklaart je plan, en dat hoeft niet elke dag
    # -----------------------------------------------------------------------
    rep('''  if(!s.klaar && dagDradenCompleet(s.blokken)){''',
        '''  /* v23.169: en alleen de eerste dagen. Stefan: "deze zin is maar een keer nuttig om te lezen."
     Hij verantwoordt waarom je plan eruitziet zoals het eruitziet, en dat is een vraag die je één
     keer stelt. Het plan zelf blijft staan; de voetnoot eronder gaat weg zodra je hem kent. Vier
     dagen, want het plan verschijnt pas vanaf dag 2 en dan zie je hem drie keer. */
  if(!s.klaar && dagenTotaal() <= 4 && dagDradenCompleet(s.blokken)){''')

    # -----------------------------------------------------------------------
    # 3. de routeregel gaat van de leskaart af
    # -----------------------------------------------------------------------
    rep('''        : toonPlan ? dagPlanHtml() + routeRegelHtml()   /* v23.141: en waar je route staat */
                   : "<p class='muted' style='margin:6px 0 0'>"+portieTxt+"</p>")+''',
        '''        /* v23.169: hier stond ook routeRegelHtml(). Zie de kop van de patch: die regel kondigde
           een route aan zonder reden, terwijl de reden al in de les zelf staat (gramWaaromHtml,
           v23.143), en de knop erbij bracht je naar de Grammatica-tab, dus uit je dag. Sinds
           v23.167 heeft de voorkant van de dag één ding, en dit was er een tweede. */
        : toonPlan ? dagPlanHtml()
                   : "<p class='muted' style='margin:6px 0 0'>"+portieTxt+"</p>")+''')

    # en dan zijn deze twee functies niemands werk meer
    rep('''function routeRegelHtml(){
  var r = routeStand();
  if(!r) return "";
  return "<p class='muted' style='margin:8px 0 0; font-size:.82rem'>"+
    ct("Je route: <b>"+r.titel+"</b>. Nu: "+r.stap+", nog "+r.open+" "+(r.open === 1 ? "stap" : "stappen")+". ",
       "Your route: <b>"+r.titel+"</b>. Now: "+r.stap+", "+r.open+" "+(r.open === 1 ? "step" : "steps")+" to go. ")+
    "<button class='mini' id='btnRouteDag' style='margin-top:4px'>"+
      ct("Naar je route","To your route")+"</button></p>";
}
function routeRegelWire(){
  var b = document.getElementById("btnRouteDag");
  if(!b) return;
  b.onclick = function(){
    var r = routeStand();
    if(r) gramPadGa(r.p, r.i);
  };
}
''',
        '''/* v23.169: routeRegelHtml() en routeRegelWire() stonden hier. Ze tekenden de routeregel op het
   dagscherm plus de knop ernaartoe, en allebei zijn ze weg. routeStand() blijft, want routeVoorstel()
   hieronder gebruikt hem: de route komt ná je les nog steeds langs, op de plek waar een voorstel
   hoort. */
''')

    rep('''  routeRegelWire();   // v23.141: de knop bij de routeregel onder je dagplan
''', '''''')

    # -----------------------------------------------------------------------
    # 4. de tapa-aankondiging
    # -----------------------------------------------------------------------
    rep('''        : "<p class='muted' style='margin:2px 0 0'>"+ct(
            "Daarna mag je Chispa "+tapaHoy.e+" <b>"+tapaHoy.es+"</b> ("+tapaHoy.nl+") geven.",
            "Then you get to give Chispa "+tapaHoy.e+" <b>"+tapaHoy.es+"</b> ("+tapaHoy.en+").")+"</p>"))+''',
        '''        /* v23.169: en vanaf dag 2 niets. Stefan: "dit zegt me niet zoveel." Terecht: het is een
           aankondiging van iets dat over tien minuten vanzelf gebeurt, met een gerecht dat je nog
           niet kent en dat je op dat moment niets kan schelen. De tapa zelf blijft, op het
           eindscherm, waar hij een beloning is in plaats van een vooraankondiging. */
        : ""))+''')

    # -----------------------------------------------------------------------
    # 5. EEN ONAFGEMAAKTE LES WINT VAN EEN GEHAALD DAGDOEL
    # -----------------------------------------------------------------------
    #
    # Stefan, 22 aug, midden in zijn les: "ik moet op pauzeer klikken en toen zei het lesje dat ik al
    # klaar was, wat niet zo is, ik heb niet gelezen of geschreven." Op de schermafdruk staat hij op
    # stap 4 van 6, en op de dagkaart erna staan alle zes de blokken afgevinkt, inclusief Lezen en
    # Schrijven.
    #
    # WAT ER GEBEURDE
    #
    # Twee verschillende dingen heetten allebei "klaar", en de kaart geloofde de verkeerde.
    #
    #   S.lesFlow[vandaag]   je les is afgerond
    #   S.dag.klaar          je dagdoel in XP is gehaald, en je hebt het feestscherm weggeklikt
    #
    # Die tweede kan halverwege je les gebeuren, en bij Stefan gebeurde dat ook: op de schermafdruk
    # van stap 4/6 staat in de kop al "doel gehaald ✓". Zodra dat waar is werd dagKlaar() waar, en
    # daar hing alles aan:
    #
    #   var hervat = !afgesloten && lesFlowHervatKan();
    #
    # Dus verdween de weg terug naar je eigen les, verscheen de kicker "Klaar voor vandaag ✓", en
    # rende de kaart dagPlanHtml("klaar") af, die elk blok een vinkje geeft. Je onafgemaakte les
    # stond nog gewoon in S.lesFlowNu, op stap 4, en er was geen knop meer die erheen ging.
    #
    # DE REGEL
    #
    # Een gehaald dagdoel is een felicitatie. Een onafgemaakte les is werk. Werk wint. En "klaar"
    # op de blokkenlijst betekent vanaf nu dat je les af is, niet dat je genoeg punten hebt.
    rep('''  var hervat = !afgesloten && lesFlowHervatKan();''',
        '''  /* v23.169: hier stond `!afgesloten && lesFlowHervatKan()`, en dat gaf een gehaald dagdoel
     voorrang op een onafgemaakte les. Zie de kop van de patch: Stefan stond op stap 4 van 6, haalde
     onderweg zijn dagdoel, en kreeg daarna een kaart die zei dat hij klaar was met alle zes de
     blokken afgevinkt, zonder knop terug naar zijn eigen les.

     Een gehaald dagdoel is een felicitatie, een onafgemaakte les is werk, en werk wint. */
  var hervat = lesFlowHervatKan() && !gedaanVandaag;''')

    rep('''  var afgesloten = dagKlaar();''',
        '''  /* v23.169: en "afgesloten" mag niet waar zijn zolang er een les open staat. Anders zegt de
     kicker "Klaar voor vandaag ✓" boven een les die op stap 4 stil is blijven staan.

     Let op de tweede helft: `&& !gedaanVandaag`. Zonder die voorwaarde zou ook een RESTJE van een
     afgeronde les de dag openhouden, want lesFlowHervatKan() kijkt alleen of er een herstelpunt van
     vandaag ligt en niet of de les daarna nog is afgemaakt. Dit is dezelfde voorwaarde als bij
     `hervat` hieronder, en ze horen bij elkaar: de dag is dicht, tenzij er een les openstaat die je
     nog kunt hervatten. */
  var afgesloten = dagKlaar() && !(lesFlowHervatKan() && !gedaanVandaag);''')

    # -----------------------------------------------------------------------
    # 6. EEN LES DIE NIET VERDER KAN, ZEGT DAT
    # -----------------------------------------------------------------------
    #
    # Stefan, 22 aug, op de uitslag van zijn toetsje: "als ik op doorgaan klik gebeurt er niks."
    #
    # De knop hangt aan lesFlowVolgende(), en die had geen enkele bodem. Klapt er iets in
    # lesFlowVolgendeKern() (een hoofdstuk dat niet opengaat, een luisterscene die er niet is, een
    # onverwachte staat na een herlaad), dan gooit de fout de hele aanroep weg en gebeurt er
    # letterlijk niets: geen schermwissel, geen melding, geen spoor. Je zit vast op een scherm met
    # een knop die dood is, en de enige manier om dat te zien is de console van je browser.
    #
    # Ik weet nog niet welke stap het bij Stefan was, en dit repareert die stap dus ook niet. Wat het
    # wel doet is de stilte weghalen: een les die niet verder kan zegt het, laat je op je dagscherm
    # achter mét je les nog open, en schrijft de fout in de console voor mij. Dat is dezelfde regel
    # als bij de nachtrun en de audio: een storing die niets zegt is duurder dan een storing die
    # klaagt, want de eerste kost dagen voordat iemand hem opmerkt.
    rep('''function lesFlowVolgende(){
  lesFlowVolgendeKern();
  lesFlowBewaar();
}''',
        '''function lesFlowVolgende(){
  /* v23.169: met een bodem eronder. Zie de kop van de patch: zonder deze try/catch was een fout
     halverwege de flow niet te onderscheiden van een knop die niets doet, en dat is precies wat
     Stefan zag op de uitslag van zijn toetsje.

     lesFlowBewaar() staat in de finally, zodat je les ook na een klapper op de stap staat waar je
     was en de knop "Verder waar je was" je terugbrengt in plaats van opnieuw te laten beginnen. */
  try {
    lesFlowVolgendeKern();
  } catch(e){
    try { console.error("lesFlowVolgende:", e && e.message, e); } catch(e2){}
    try { toast(ct("Deze stap kon niet openen. Je les staat nog waar je was.",
                   "This step could not open. Your session is still where you left it.")); } catch(e3){}
    try { show("lessen"); } catch(e4){}
  } finally {
    lesFlowBewaar();
  }
}''')

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
