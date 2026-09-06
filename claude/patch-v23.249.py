#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v23.249 - het gesprek met Chispa: één zin per oordeel, en een kop van 28 pixels
#
# Stefan, met twee schermafbeeldingen van het praatblok: "het gesprek met chispa is wel leuk maar ook
# nog wel wat lastig. hij reageert laat (het voelt niet instant)." En daarna: "fix ook de interface,
# chispa is nu heel groot, misschien moet een gewoon een doorlopend gesprek blijven."
#
# ================ WAT ER OP ZIJN SCHERM STOND ================
#
# Drie beurten, en drie keer dezelfde correctie, elke keer aan de verkeerde zin geplakt:
#
#   jij: "trabajo y voy mi clase de español"   -> "Het moet zijn: 'trabajo e **voy a** mi clase'"
#   jij: "bailar salsa"                        -> "Het moet zijn: 'voy a mi clase de español'"
#   jij: "si es un rato pero me gusta mucho"   -> "Het moet zijn: 'voy A mi clase' (met 'a')"
#
# Vier dingen zijn daar mis, en ze hebben alle vier een aanwijsbare plek.
#
# ---- EEN. DE ZIN DIE BEOORDEELD WORDT, WORDT NIET MEEGEGEVEN ----
#
# De app stuurt het hele gesprek als één blok tekst, en de opdracht aan het model is: "naast = wat er
# van de laatste zin van de LEERLING te zeggen valt". Welke zin dat is, moet het model zelf uit dat
# blok opdiepen. Er staat niets omheen, geen markering, geen apart veld. Het model pakte drie keer
# dezelfde eerste fout.
#
#     De zin die beoordeeld moet worden, hoort meegegeven te worden en niet gevonden.
#
# Dit is exact dezelfde vorm als de luisterknop van v23.246 (de knop droeg zijn eigen antwoordindex
# niet en werd op positie gemarkeerd) en als de nummerbotsing van v23.247. Derde keer deze week.
#
# En de app deed hetzelfde aan zijn kant: het antwoord werd geschreven naar
# s.beurten[s.beurten.length - 1], de laatste beurt op het moment dat het antwoord BINNENKWAM. Ook
# dat is een positie in plaats van een verwijzing. Nu wordt de index vastgelegd vóór de aanroep.
#
# ---- TWEE. DE CORRECTIE WAS ZELF FOUT ----
#
# "trabajo y voy a mi clase" is goed Spaans. De app zei dat het "trabajo e voy" moest zijn. De
# e-regel geldt alleen vóór een woord dat met i- of hi- begint (padre e hijo). Voor "voy" is het
# altijd "y". Hij is dus verbeterd op iets dat al klopte, en dat is de duurste soort feedback die er
# is: je leert een fout die je niet maakte.
#
# Dat volgt uit punt een (een model zonder duidelijk doelwit gaat overal aan zitten) en het krijgt
# hier bovendien een expliciete rem: verbeter alleen wat echt fout is, en laat een zin die klopt met
# rust.
#
# ---- DRIE. DE OPMAAK LEKTE ----
#
# Er stond letterlijk **voy a** met sterretjes op zijn scherm. Het model schrijft markdown en
# veiligHtml() zet het als platte tekst neer, wat terecht is: HTML uit een model doorlaten is precies
# wat je niet wilt. Dus wordt het aan de bron gevraagd (geen markdown) én bij binnenkomst gestript.
# Alleen het eerste zou een belofte in een prompt zijn, en die zijn niet af te dwingen.
#
# ---- VIER. DE MINI-CHISPA HAD NOOIT EEN MAAT GEKREGEN ----
#
# chispaMiniSvg() geeft een <svg> zonder width of height terug. Op twee plekken wordt hij gebruikt:
#
#   .lfchispa svg { width:48px; height:50px; }   <- de dagbalk, die geeft hem een maat
#   .chatrij (geen regel voor svg)               <- het gesprek, die niet
#
# Een <svg> zonder maat en zonder CSS wordt in de meeste browsers zo breed als zijn ouder. Vandaar
# een Chispa van een halve pagina, per beurt, precies zoals op zijn schermafbeelding.
#
#     Een maat die bij de aanroepplek staat in plaats van bij het ding zelf,
#     ontbreekt op de volgende aanroepplek.
#
# Dus draagt het ding zijn eigen maat: chispaMiniSvg() krijgt class="chmini" met een regel erbij. De
# bestaande regel .lfchispa svg is specifieker en wint, dus de dagbalk verandert niet.
#
# ================ EN DE TWEE ONTWERPKEUZES ================
#
# ---- DE CORRECTIE GAAT UIT DE BEURT ----
#
# In de kop van dit blok staat sinds v23.144: "Een gesprekspartner die elke zin verbetert is er
# geen." En daarna verbeterde hij elke zin, in de beurt zelf. Nu niet meer: tijdens het gesprek
# antwoordt Chispa alleen, en de bespreking van je zinnen komt in één keer als je drie beurten hebt
# gehad.
#
# Dat doet twee dingen tegelijk. Het is een gesprek in plaats van een overhoring, en het is sneller:
# de beurt-aanroep hoeft geen oordeel meer te vormen en vraagt 140 in plaats van 350 tokens. Dat is
# waar "het voelt niet instant" vandaan komt; er stond al een "Chispa denkt na..."-melding, dus het
# was echte wachttijd en geen ontbrekende spinner.
#
# ---- EN HET GESPREK MAG DOORLOPEN ----
#
# Drie beurten blijft de maat van het blok, want een gesprek zonder eind is waar je op afhaakt (de
# reden staat er sinds v23.144 en die verandert niet). Maar na die drie staat er nu "Nog een beurt"
# naast "Verder met je les". Het blok is af, en doorpraten mag. Die extra beurten krijgen geen
# bespreking, en dat is geen tekortkoming: praten zonder dat er iemand meekijkt is precies het ding
# waar dit blok voor bestaat.
import pathlib
import re
import sys

W = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / "claude"))
import patchhulp  # noqa: E402

APP = W / "index.html"
VER = W / "versie.txt"
SRV = W / "server" / "index.js"
GEPLAND = "v23.249"

src = APP.read_text(encoding="utf-8")
srv = SRV.read_text(encoding="utf-8")
huidig = VER.read_text(encoding="utf-8").strip()
DOE_APP = "function markdownWeg(" not in src
DOE_SRV = "nabespreking" not in srv


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "app-anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


def repsrv(anker, nieuw, n=1):
    global srv
    c = srv.count(anker)
    assert c == n, "server-anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    srv = srv.replace(anker, nieuw, n)


# ============================== DE SERVER ==============================
if DOE_SRV:
    repsrv(
        """   modus "hulp": {vraag} -> {es, uitleg}""",
        """   modus "gesprek" + alleenAntwoord: hetzelfde, maar zonder naast. Sneller en korter, en het is
     wat het praatblok sinds v23.249 vraagt: tijdens het gesprek antwoordt Chispa alleen.
   modus "nabespreking": {zinnen:[...], niveau} -> {regels:[{zin, oordeel, goed}]}
     De bespreking van alles wat de leerling zei, in één keer, na afloop. Elke regel draagt de zin
     waar hij over gaat, zodat de app hem niet op positie hoeft te raden.
   modus "hulp": {vraag} -> {es, uitleg}""",
    )
    repsrv(
        """  const { beurten, niveau, modus, vraag } = req.body || {};""",
        """  const { beurten, niveau, modus, vraag, zin, zinnen, alleenAntwoord } = req.body || {};""",
    )
    # de nabespreking, vóór de gesprek-tak
    repsrv(
        """    const rij = Array.isArray(beurten) ? beurten.slice(-8) : [];
    if (!rij.length) return bad(res, 400, "beurten verplicht");""",
        """    if (modus === "nabespreking") {
      /* v23.249: elke regel draagt de zin waar hij over gaat. Zonder dat veld zou de app de
         oordelen op volgorde aan de zinnen moeten koppelen, en dat is precies de fout die deze
         ronde repareert: iets aanwijzen op positie in plaats van het mee te geven. */
      const zl = (Array.isArray(zinnen) ? zinnen : []).map((z) => String(z || "").slice(0, 300)).filter(Boolean);
      if (!zl.length) return bad(res, 400, "zinnen verplicht");
      const txt = await vraagLadder(
        "Een Nederlandstalige leerling Spaans (niveau " + niv + ") heeft net een kort gesprek gevoerd. " +
        "Bespreek zijn zinnen, één regel per zin, in het Nederlands.\\n" +
        "VERBETER ALLEEN WAT ECHT FOUT IS. Klopt een zin, dan is het oordeel een korte bevestiging en " +
        "is goed=true. Twijfel je, of is het een kwestie van stijl, dan geldt de zin als goed. Een " +
        "leerling verbeteren op iets dat al klopte is erger dan een fout laten staan.\\n" +
        "Geen markdown, geen sterretjes, geen opmaak: platte tekst. Hoogstens twee zinnen per regel.\\n" +
        "Antwoord UITSLUITEND met geldige JSON: {\\"regels\\": [{\\"zin\\": \\"de zin van de leerling, " +
        "letterlijk overgenomen\\", \\"oordeel\\": \\"...\\", \\"goed\\": true|false}]}. " +
        "Evenveel regels als zinnen, in dezelfde volgorde.",
        "De zinnen van de leerling:\\n" + zl.map((z, i) => (i + 1) + ". " + z).join("\\n"),
        400, true, "ai-chat-na"
      );
      const mn = txt.match(/\\{[\\s\\S]*\\}/);
      if (!mn) return badReden(res, 502, "onleesbaar AI-antwoord", "stuk");
      const pn = JSON.parse(mn[0]);
      const regels = (Array.isArray(pn.regels) ? pn.regels : []).slice(0, 12).map((r) => ({
        zin: String((r && r.zin) || "").slice(0, 300),
        oordeel: String((r && r.oordeel) || "").slice(0, 400),
        goed: !!(r && r.goed)
      })).filter((r) => r.zin && r.oordeel);
      if (!regels.length) return badReden(res, 502, "leeg AI-antwoord", "stuk");
      return ok(res, { regels });
    }
    const rij = Array.isArray(beurten) ? beurten.slice(-8) : [];
    if (!rij.length) return bad(res, 400, "beurten verplicht");""",
    )
    # de gesprek-tak: de zin apart, en een korte modus zonder oordeel
    repsrv(
        """    const txt = await vraagLadder(
      "Je bent Chispa, een vrolijk pratend diertje in een Spaanse leerapp voor Nederlandstaligen op niveau " +
      niv + ". Je voert een kort gesprek in eenvoudig Spaans.\\n" +
      "Regels voor jouw beurt: hoogstens twaalf woorden, woordenschat die bij " + niv + " past, altijd één " +
      "vraag terug zodat de leerling verder kan, nooit Nederlands in het veld es, geen emoji.\\n" +
      "Antwoord UITSLUITEND met geldige JSON: " +
      "{\\"naast\\": \\"...\\", \\"es\\": \\"...\\", \\"nl\\": \\"...\\"}.\\n" +
      "naast = wat er van de laatste zin van de LEERLING te zeggen valt, in het Nederlands, hoogstens twee " +
      "zinnen: klopt hij, en zo niet, wat is de natuurlijke versie. Klopt hij helemaal, dan een korte " +
      "bevestiging. Reageer hier op de vorm; op de inhoud reageer je in es.\\n" +
      "es = jouw volgende zin in het Spaans. nl = de Nederlandse vertaling van precies die zin.",
      "Het gesprek tot nu toe:\\n" + gesprek,
      350, true, "ai-chat"
    );""",
        """    /* v23.249: de zin die beoordeeld wordt, komt als eigen veld mee.

       Wat hier stond was "naast = wat er van de laatste zin van de LEERLING te zeggen valt", met het
       hele gesprek als één blok tekst eronder. Welke zin dat was, moest het model zelf opdiepen.
       Stefan kreeg daardoor drie beurten lang dezelfde correctie op zijn eerste zin, geplakt aan
       zinnen die er niets mee te maken hadden.

           De zin die beoordeeld moet worden, hoort meegegeven te worden en niet gevonden. */
    const doelZin = String(zin || "").slice(0, 300) ||
      (rij.filter((b) => b && b.van === "jij").slice(-1)[0] || {}).es || "";
    const kort = !!alleenAntwoord;
    const txt = await vraagLadder(
      "Je bent Chispa, een vrolijk pratend diertje in een Spaanse leerapp voor Nederlandstaligen op niveau " +
      niv + ". Je voert een kort gesprek in eenvoudig Spaans.\\n" +
      "Regels voor jouw beurt: hoogstens twaalf woorden, woordenschat die bij " + niv + " past, altijd één " +
      "vraag terug zodat de leerling verder kan, nooit Nederlands in het veld es, geen emoji, geen markdown.\\n" +
      "Antwoord UITSLUITEND met geldige JSON: " +
      (kort ? "{\\"es\\": \\"...\\", \\"nl\\": \\"...\\"}.\\n"
            : "{\\"naast\\": \\"...\\", \\"es\\": \\"...\\", \\"nl\\": \\"...\\"}.\\n" +
              "naast = wat er te zeggen valt over DEZE ENE ZIN van de leerling, in het Nederlands, hoogstens " +
              "twee zinnen, platte tekst zonder sterretjes: \\"" + doelZin + "\\". Ga niet over een andere zin " +
              "uit het gesprek. VERBETER ALLEEN WAT ECHT FOUT IS; klopt de zin, dan een korte bevestiging. " +
              "Reageer hier op de vorm; op de inhoud reageer je in es.\\n") +
      "es = jouw volgende zin in het Spaans. nl = de Nederlandse vertaling van precies die zin.",
      "Het gesprek tot nu toe:\\n" + gesprek,
      kort ? 160 : 350, true, "ai-chat"
    );""",
    )
    repsrv(
        """    ok(res, { naast: String(p.naast || "").slice(0, 400), es: String(p.es || "").slice(0, 300),
              nl: String(p.nl || "").slice(0, 300) });""",
        """    /* de zin gaat mee terug. De app kan dan nakijken dat het oordeel over de zin gaat die hij
       stuurde, in plaats van erop te vertrouwen. */
    ok(res, { naast: kort ? "" : String(p.naast || "").slice(0, 400), zin: doelZin,
              es: String(p.es || "").slice(0, 300), nl: String(p.nl || "").slice(0, 300) });""",
    )
    SRV.write_text(srv, encoding="utf-8")
    print("server/index.js: de zin gaat mee, en er is een nabespreking")
else:
    print("server/index.js: stond er al")

# ============================== DE APP ==============================
if DOE_APP:
    # ---- de maat hoort bij het ding ----
    rep(
        """function chispaMiniSvg(){
  return "<svg viewBox='-16 -16 32 34'>"+escChispaMini()+"</svg>";
}""",
        """/* v23.249: mét een klasse die een maat draagt.

   Deze svg heeft geen width en geen height. Op de dagbalk gaf .lfchispa svg hem er een; in het
   gesprek stond geen enkele regel, en een <svg> zonder maat wordt zo breed als zijn ouder. Vandaar
   de Chispa van een halve pagina per beurt op Stefans scherm.

       Een maat die bij de aanroepplek staat in plaats van bij het ding zelf,
       ontbreekt op de volgende aanroepplek.

   .lfchispa svg is specifieker en wint, dus de dagbalk blijft 48 bij 50. */
function chispaMiniSvg(){
  return "<svg class='chmini' viewBox='-16 -16 32 34'>"+escChispaMini()+"</svg>";
}""",
    )
    rep(
        """  .chatrij{display:flex; gap:9px; align-items:flex-start; margin:9px 0;}""",
        """  .chmini{width:28px; height:30px; flex:0 0 28px;}
  .chatrij{display:flex; gap:9px; align-items:flex-start; margin:9px 0;}""",
    )

    # ---- markdown eruit ----
    rep(
        """function veiligHtml(s){""",
        """/* v23.249: sterretjes van het model eruit.

   Er stond letterlijk **voy a** op Stefans scherm. Het model schrijft markdown en veiligHtml() zet
   dat als platte tekst neer, wat precies goed is: HTML uit een model doorlaten wil je niet. De
   prompts vragen nu om platte tekst, maar dat is een belofte en geen afdwinging, dus wordt het hier
   ook weggehaald. Alleen paren, zodat een losse asterisk in een echte zin blijft staan. */
function markdownWeg(s){
  return String(s == null ? "" : s)
    .replace(/\\*\\*([^*]+)\\*\\*/g, "$1")
    .replace(/__([^_]+)__/g, "$1")
    .replace(/(^|[\\s(])\\*([^*\\n]+)\\*(?=[\\s.,!?)]|$)/g, "$1$2")
    .replace(/`([^`]+)`/g, "$1");
}
function veiligHtml(s){""",
    )

    # ---- het gesprek: geen oordeel in de beurt, wel een bespreking erna ----
    rep(
        """function chatStuur(){
  var inv = document.getElementById("chatInvoer");
  var tekst = inv ? (inv.value || "").trim() : "";
  if(!tekst || chatBezig) return;
  var st = chatStand();
  st.beurten.push({van:"jij", es:tekst.slice(0, 300)});
  addXP(3); chatBezig = true; persist(); renderChat();
  api("/api/ai/chat", "POST", {modus:"gesprek", niveau:chatNiveau(),
      beurten:st.beurten.map(function(b){ var t = chatTekst(b); return {van:b.van, es:t.es}; })})
    .then(function(res){
      chatBezig = false;
      var s = chatStand();
      var laatste = s.beurten[s.beurten.length - 1];
      if(!res || !res.ok){
        /* Geen model, geen gesprek: dan zegt Chispa dat zelf en telt de beurt gewoon mee. Wat je
           schreef blijft staan; dat is het enige wat je zelf gemaakt hebt. */
        if(laatste && laatste.van === "jij") laatste.naast = aiFoutTekst(res);
      } else {
        if(laatste && laatste.van === "jij" && res.naast) laatste.naast = res.naast;
        if(res.es) s.beurten.push({van:"chispa", es:res.es, nl:res.nl || ""});
      }
      if(chatKlaar()) s.klaar = true;
      persist();
      renderChat();
    });
}""",
        """function chatStuur(){
  var inv = document.getElementById("chatInvoer");
  var tekst = inv ? (inv.value || "").trim() : "";
  if(!tekst || chatBezig) return;
  var st = chatStand();
  var mijnZin = tekst.slice(0, 300);
  st.beurten.push({van:"jij", es:mijnZin});
  /* v23.249: de plek van MIJN beurt, vastgelegd vóór de aanroep.

     Hier stond s.beurten[s.beurten.length - 1] ná het antwoord, oftewel "de laatste beurt op het
     moment dat het antwoord binnenkwam". Dat is een positie en geen verwijzing, en het is dezelfde
     fout als aan de serverkant. Nu weet de afhandeling welke beurt van haar is. */
  var idx = st.beurten.length - 1;
  addXP(3); chatBezig = true; persist(); renderChat();
  api("/api/ai/chat", "POST", {modus:"gesprek", niveau:chatNiveau(), zin:mijnZin, alleenAntwoord:true,
      beurten:st.beurten.map(function(b){ var t = chatTekst(b); return {van:b.van, es:t.es}; })})
    .then(function(res){
      chatBezig = false;
      var s = chatStand();
      var mijn = s.beurten[idx];
      if(!res || !res.ok){
        /* Geen model, geen gesprek: dan zegt Chispa dat zelf en telt de beurt gewoon mee. Wat je
           schreef blijft staan; dat is het enige wat je zelf gemaakt hebt. */
        if(mijn && mijn.van === "jij") mijn.naast = aiFoutTekst(res);
      } else if(res.es){
        s.beurten.push({van:"chispa", es:markdownWeg(res.es), nl:markdownWeg(res.nl || "")});
      }
      if(chatKlaar()) s.klaar = true;
      persist();
      renderChat();
      if(chatKlaar()) chatNabespreking();
    });
}

/* De bespreking van je zinnen, in één keer, na afloop.

   Sinds v23.144 staat in de kop van dit blok: "Een gesprekspartner die elke zin verbetert is er
   geen." En daarna verbeterde hij elke zin, in de beurt zelf. Nu antwoordt Chispa tijdens het
   gesprek alleen, en komt dit erachteraan. Dat is een gesprek in plaats van een overhoring, en het
   is sneller: de beurt hoeft geen oordeel meer te vormen.

   Elke regel draagt de zin waar hij over gaat, en die wordt hier nagekeken. Komt hij niet voor in
   wat je gezegd hebt, dan valt de regel af: liever geen oordeel dan een oordeel over de verkeerde
   zin. */
var chatNaBezig = false;
function chatMijnZinnen(){
  return chatStand().beurten.filter(function(b){ return b.van === "jij"; })
    .map(function(b){ return b.es || ""; }).filter(Boolean);
}
function chatNabespreking(){
  var s = chatStand();
  if(s.review || chatNaBezig) return;
  var zinnen = chatMijnZinnen();
  if(!zinnen.length) return;
  chatNaBezig = true; renderChat();
  api("/api/ai/chat", "POST", {modus:"nabespreking", niveau:chatNiveau(), zinnen:zinnen})
    .then(function(res){
      chatNaBezig = false;
      var st2 = chatStand();
      if(!res || !res.ok || !res.regels || !res.regels.length){
        st2.review = {fout:aiFoutTekst(res), regels:[]};
      } else {
        var regels = res.regels.filter(function(r){ return r && r.zin && zinnen.indexOf(r.zin) !== -1; })
          .map(function(r){ return {zin:r.zin, oordeel:markdownWeg(r.oordeel), goed:!!r.goed}; });
        st2.review = regels.length ? {regels:regels}
                                   : {fout:ct("De bespreking ging over andere zinnen dan die van jou, dus die laat ik weg.",
                                              "The review was about other sentences than yours, so I am leaving it out."),
                                      regels:[]};
      }
      persist();
      renderChat();
    });
}
/* Doorpraten mag. Drie beurten blijft de maat van het blok (een gesprek zonder eind is waar je op
   afhaakt, v23.144), maar het blok is dan af en niet het gesprek. Extra beurten krijgen geen
   bespreking, en dat is geen gat: praten zonder dat er iemand meekijkt is waar dit blok voor is. */
function chatNogEen(){
  var s = chatStand();
  /* NIET s.klaar op false: chatKlaar() telt je beurten en die blijven op drie staan, dus dat had
     geen effect (de proef zag het meteen). En het zou het verkeerde zeggen ook: het blok van
     vandaag ís af, en chatGedaanVandaag() hangt daaraan. Wat hier opengaat is het gesprek. */
  s.door = true;
  persist();
  renderChat();
}
function chatReviewHtml(){
  var s = chatStand();
  if(chatNaBezig) return "<p class='muted' style='margin:10px 0 0'>\\ud83e\\udd16 "+
    ct("Chispa kijkt je zinnen na...","Chispa is reviewing your sentences...")+"</p>";
  if(!s.review) return "";
  if(s.review.fout) return "<div class='naast amber' style='margin-top:10px'>"+veiligHtml(s.review.fout)+"</div>";
  var n = s.review.regels.filter(function(r){ return r.goed; }).length;
  return "<div style='margin-top:12px'><span class='kicker'>"+
    ct("Je zinnen","Your sentences")+" \\u00b7 "+n+"/"+s.review.regels.length+" "+ct("goed","right")+"</span>"+
    s.review.regels.map(function(r){
      return "<div class='naast"+(r.goed ? "" : " amber")+"'>"+
        "<b class='es'>"+veiligHtml(r.zin)+"</b><br>"+veiligHtml(r.oordeel)+"</div>";
    }).join("")+"</div>";
}""",
    )

    # ---- de weergave: geen oordeel per beurt meer, en een doorpraatknop ----
    rep(
        """      h += "<div class='chatrij ik'><div class='bel ik'>"+veiligHtml(t.es)+"</div></div>";
      if(b.naast) h += "<div class='naast'>"+veiligHtml(b.naast)+"</div>";""",
        """      h += "<div class='chatrij ik'><div class='bel ik'>"+veiligHtml(t.es)+"</div></div>";
      /* v23.249: naast staat er alleen nog als er iets MIS ging (geen model). Het oordeel over je
         zinnen komt na afloop in één blok; zie chatNabespreking. */
      if(b.naast) h += "<div class='naast amber'>"+veiligHtml(markdownWeg(b.naast))+"</div>";""",
    )
    rep(
        """  h += "<div id='chatHulpVak'></div>";
  if(klaar){
    h += "<div class='feedback ok' style='margin-top:10px'>"+
      ct("Drie beurten, en je hebt ze zelf bedacht. Dat is iets anders dan een zin vertalen.",
         "Three turns, and you came up with them yourself. That's not the same as translating a sentence.")+"</div>"+
      "<div class='row' style='margin-top:10px'>"+
        (inFlow ? "<button class='primary' id='chatFlow'>"+ct("Verder met je les \\u2192","On with your session \\u2192")+"</button>"
                : "<button class='primary' id='chatTerug'>"+ct("Klaar","Done")+"</button>")+
      "</div>";""",
        """  h += "<div id='chatHulpVak'></div>";
  if(klaar){
    h += chatReviewHtml()+
      "<div class='feedback ok' style='margin-top:10px'>"+
      ct("Drie beurten, en je hebt ze zelf bedacht. Dat is iets anders dan een zin vertalen.",
         "Three turns, and you came up with them yourself. That's not the same as translating a sentence.")+"</div>"+
      "<div class='row' style='margin-top:10px'>"+
        (inFlow ? "<button class='primary' id='chatFlow'>"+ct("Verder met je les \\u2192","On with your session \\u2192")+"</button>"
                : "<button class='primary' id='chatTerug'>"+ct("Klaar","Done")+"</button>")+
        (praatDoor ? "" : "<button class='ghost' id='chatNogEen'>"+ct("Nog een beurt","One more turn")+"</button>")+
      "</div>";""",
    )
    # praatDoor: het gesprek staat open terwijl het blok al af is
    rep(
        """  var st = chatStand(), klaar = chatKlaar();""",
        """  var st = chatStand(), klaar = chatKlaar(), praatDoor = !!st.door;""",
    )
    # het invoerveld hoort ook te kunnen staan terwijl het blok af is: dat is "doorlopend gesprek"
    rep(
        """  } else {
    h += "<input type='text' id='chatInvoer' style='margin-top:10px' placeholder='"+""",
        """  }
  /* v23.249: geen else meer. Het blok is af bij drie beurten (daar hangt chatGedaanVandaag aan),
     maar het gesprek hoeft dat niet te zijn. Tik je "Nog een beurt", dan staan de bespreking en het
     invoerveld tegelijk op het scherm. */
  if(!klaar || praatDoor){
    h += "<input type='text' id='chatInvoer' style='margin-top:10px' placeholder='"+""",
    )
    rep(
        """  b = document.getElementById("chatStuur"); if(b) b.onclick = chatStuur;""",
        """  b = document.getElementById("chatStuur"); if(b) b.onclick = chatStuur;
  b = document.getElementById("chatNogEen"); if(b) b.onclick = chatNogEen;""",
    )
    # de hulp-uitvoer komt ook uit een model
    rep(
        """        u.innerHTML = "<p style='margin:6px 0 0'><b class='es'>"+veiligHtml(res.es)+"</b></p>"+
          (res.uitleg ? "<p class='muted' style='margin:2px 0 0'>"+veiligHtml(res.uitleg)+"</p>" : "");""",
        """        u.innerHTML = "<p style='margin:6px 0 0'><b class='es'>"+veiligHtml(markdownWeg(res.es))+"</b></p>"+
          (res.uitleg ? "<p class='muted' style='margin:2px 0 0'>"+veiligHtml(markdownWeg(res.uitleg))+"</p>" : "");""",
    )

    kaal = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    kaal = "\n".join([r.split("//")[0] for r in kaal.split("\n")])
    assert kaal.count("function markdownWeg(") == 1, "markdownWeg niet precies een keer"
    assert kaal.count("function chatNabespreking(") == 1, "chatNabespreking niet precies een keer"
    assert kaal.count("class='chmini'") == 1, "de mini-svg draagt zijn klasse niet"
    assert ".chmini{" in kaal, "er is geen maat voor .chmini"
    assert "s.beurten[s.beurten.length - 1]" not in kaal, "er wordt nog op positie geschreven"
    assert kaal.count("praatDoor") == 3, "praatDoor: een declaratie en twee lezers"
    assert kaal.count("if(!klaar || praatDoor){") == 1, "het invoerveld hangt niet aan praatDoor"
    APP.write_text(src, encoding="utf-8")
    print("index.html: het oordeel gaat over een zin, en Chispa is 28 pixels")
else:
    print("index.html: stond er al")

nieuw, doe_ver, reden = patchhulp.nummerKiezen(huidig, GEPLAND, DOE_APP or DOE_SRV)
if reden:
    print("LET OP: " + reden)
if doe_ver:
    patchhulp.zetVersie(APP, VER, huidig, nieuw)
    print("versie.txt: %s -> %s" % (huidig, nieuw))
else:
    print("versie.txt: stond al op " + huidig)
