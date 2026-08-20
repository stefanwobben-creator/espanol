#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.144: je kunt met Chispa praten.

Stefan, 20 aug: "ik kan ook nog niet chatten met chispa." En eerder: "ik denk dat die zinnen of
chatten met chispa of bijv ilona (iemand uit mijn groep) heel goed kan helpen bij produceren."

## Waarom dit het ontbrekende stuk is

Nation's tweede draad is betekenisgerichte output: iets zeggen omdat je iets wilt zeggen, niet omdat
er een modelantwoord achter een knop zit. Alles wat Vamos aan produceren doet is het tweede soort:
een Nederlandse zin, een Spaanse vertaling, goed of fout. Dat is nuttig (het is de ladder van
v23.136) maar het is geen taal gebruiken.

Een gesprek is het wel. Je kiest zelf wat je zegt, je moet het begrijpen om te kunnen antwoorden, en
er is geen goed antwoord om naar toe te schrijven.

## De vier keuzes

**Drie beurten, dan klaar.** Een open gesprek zonder eind is precies waar je op afhaakt: je weet niet
wanneer je mag stoppen, dus je begint niet. Drie beurten is af te maken en het staat er vooraf bij.

**De correctie staat naast het gesprek, niet erin.** Chispa reageert op wát je zegt; onder je eigen
zin staat een aparte notitie of hij klopt en hoe het natuurlijker kan. Dat scheidt de twee dingen die
tegelijk gebeuren. Een gesprekspartner die elke zin verbetert is geen gesprekspartner.

**Vastlopen mag in het Nederlands.** "Hoe zeg ik...?" geeft je de Spaanse zin plus één regel waarom,
en zet hem in je invoerveld. Doorgaan is meer waard dan zuiverheid; het alternatief is wegklikken.

**Chispa begint, zonder modelaanroep.** De openingsvraag komt uit een lijst van acht, één per dag.
Zo staat het gesprek er ook als de server niet bereikbaar is, en pas als jij iets terugzegt gaat er
een aanroep uit.

## Waar het staat

Op de Chispa-pagina, en als voorstel na je les (op plek drie, na je route en vóór El Corrector: het
is produceren en dat weegt zwaarder dan een spel). Eén gesprek per dag.

Nog niet: als vaste stap in de dagles. Dat is trede 6 van de zinnenladder in het prototype, en die
trede haal je pas na een stuk of twintig goede zinnen op rij. Eerst moet blijken dat het gesprek zelf
werkt.

Bewaakt door test/suites/pw-chat.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_SRV = os.path.join(WORTEL, "server", "index.js")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.144"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()
with io.open(PAD_SRV, encoding="utf-8") as f:
    srv = f.read()

DOE_APP = NIEUW not in src
DOE_SRV = "/api/ai/chat" not in srv
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER and not DOE_SRV:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


def repsrv(anker, nieuw, n=1):
    global srv
    if not DOE_SRV:
        return
    gevonden = srv.count(anker)
    assert gevonden == n, "server-anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    srv = srv.replace(anker, nieuw, n)


# ================= 1. de server: één eindpunt, twee vragen =================

repsrv(
    """// POST /api/ai/uitleg {vraag, context}""",
    """/* POST /api/ai/chat  (v23.144)
   Twee vragen, één eindpunt, want ze delen dezelfde gespreksgeschiedenis.

   modus "gesprek": {beurten:[{van:"chispa"|"jij", es}], niveau} -> {naast, es, nl}
     naast = wat er van de laatste zin van de leerling te zeggen valt, in het Nederlands, náást het
     gesprek. Een gesprekspartner die elke zin verbetert is geen gesprekspartner, dus het staat
     apart en het gesprek loopt gewoon door.
   modus "hulp": {vraag} -> {es, uitleg}
     De leerling loopt vast en vraagt in het Nederlands hoe je iets zegt. Vastlopen mag; wegklikken
     niet. */
app.post("/api/ai/chat", async (req, res) => {
  const slot = aiSlot(req);
  if (slot) return badReden(res, slot.code, slot.tekst, slot.reden);
  const { beurten, niveau, modus, vraag } = req.body || {};
  const niv = /^(a0|a1|a2|b1)$/i.test(String(niveau || "")) ? String(niveau).toUpperCase() : "A2";
  try {
    if (modus === "hulp") {
      if (!vraag) return bad(res, 400, "vraag verplicht");
      const txt = await vraagLadder(
        "Een Nederlandstalige leerling Spaans (niveau " + niv + ") loopt vast in een gesprek en vraagt in " +
        "het Nederlands hoe je iets zegt. Antwoord UITSLUITEND met geldige JSON: " +
        "{\\"es\\": \\"de Spaanse zin, kort en op dit niveau\\", \\"uitleg\\": \\"één of twee zinnen Nederlands over waarom het zo is\\"}. " +
        "Kies de gewoonste manier om het te zeggen, niet de meest letterlijke vertaling.",
        "Vraag van de leerling: " + String(vraag).slice(0, 300),
        250, true, "ai-chat-hulp"
      );
      const m = txt.match(/\\{[\\s\\S]*\\}/);
      if (!m) return badReden(res, 502, "onleesbaar AI-antwoord", "stuk");
      const p = JSON.parse(m[0]);
      return ok(res, { es: String(p.es || "").slice(0, 200), uitleg: String(p.uitleg || "").slice(0, 400) });
    }
    const rij = Array.isArray(beurten) ? beurten.slice(-8) : [];
    if (!rij.length) return bad(res, 400, "beurten verplicht");
    const gesprek = rij.map((b) =>
      (b && b.van === "jij" ? "LEERLING: " : "CHISPA: ") + String((b && b.es) || "").slice(0, 300)
    ).join("\\n");
    const txt = await vraagLadder(
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
    );
    const m = txt.match(/\\{[\\s\\S]*\\}/);
    if (!m) return badReden(res, 502, "onleesbaar AI-antwoord", "stuk");
    const p = JSON.parse(m[0]);
    ok(res, { naast: String(p.naast || "").slice(0, 400), es: String(p.es || "").slice(0, 300),
              nl: String(p.nl || "").slice(0, 300) });
  } catch (e) {
    console.error(e);
    badReden(res, 502, "AI-fout", "stuk");
  }
});

// POST /api/ai/uitleg {vraag, context}""",
)

# ================= 2. de app: opmaak =================

rep(
    """  .ritme{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;}""",
    """  .ritme{display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;}
  /* v23.144: het gesprek met Chispa. Haar beurten links met haar kop ernaast, die van jou rechts.
     De notitie over jouw zin staat er los onder (klasse naast): het gesprek en de correctie zijn
     twee verschillende dingen en horen er ook verschillend uit te zien. */
  .chatrij{display:flex; gap:9px; align-items:flex-start; margin:9px 0;}
  .chatrij.ik{justify-content:flex-end;}
  .bel{border-radius:14px; padding:8px 12px; max-width:82%; font-size:.94rem;}
  .bel.zij{background:var(--accent-soft); border-bottom-left-radius:4px;}
  .bel.ik{background:var(--bg); border:1px solid var(--border); border-bottom-right-radius:4px;}
  .bel .nl{display:block; color:var(--muted); font-size:.8rem; margin-top:3px;}
  .naast{border-left:3px solid var(--border); padding:4px 0 4px 9px; margin:2px 0 9px 0;
         font-size:.85rem; color:var(--muted);}
  .naast.amber{border-left-color:var(--accent);}""",
)

# ================= 3. de app: het scherm =================

rep(
    """  <section id="tab-chispa" class="hidden">""",
    """  <!-- v23.144: praten met Chispa. Eigen scherm, want het is een gesprek en geen kaartje. -->
  <section id="tab-chat" class="hidden">
    <div id="chatWrap"></div>
  </section>

  <section id="tab-chispa" class="hidden">""",
)

rep(
    """  {id:"chispa", label:"Chispa", nav:false},""",
    """  {id:"chispa", label:"Chispa", nav:false},
  {id:"chat", label:"Praten met Chispa", nav:false},   // v23.144""",
)

rep(
    """  if(tabId==="chispa"){ renderChispaPagina(); }""",
    """  if(tabId==="chispa"){ renderChispaPagina(); }
  if(tabId==="chat"){ renderChat(); }""",
)

# ================= 4. de app: de machinerie =================

rep(
    """function renderChispaPagina(){""",
    """/* ================= PRATEN MET CHISPA (v23.144) =================

   Stefan: "ik kan ook nog niet chatten met chispa." En eerder: "chatten met chispa of bijv ilona kan
   heel goed helpen bij produceren."

   Dit is Nation's tweede draad: iets zeggen omdat je iets wilt zeggen. Alles wat Vamos daarvoor had
   is van het andere soort: een Nederlandse zin, een Spaanse vertaling, goed of fout.

   Vier keuzes, en ze hangen samen:

   * Drie beurten, dan klaar. Een gesprek zonder eind is precies waar je op afhaakt.
   * De correctie staat náást het gesprek. Chispa reageert op wat je zegt; of je zin klopt staat
     eronder in een aparte regel. Een gesprekspartner die elke zin verbetert is er geen.
   * Vastlopen mag in het Nederlands ("hoe zeg ik...?"). Doorgaan is meer waard dan zuiverheid.
   * Chispa begint zonder modelaanroep, uit een lijst van acht. Zo staat het gesprek er ook als de
     server niet bereikbaar is, en pas als jij iets terugzegt gaat er een aanroep uit. */
var CHAT_BEURTEN = 3;
var CHAT_OPENERS = [
  {es:"\\u00a1Hola! \\u00bfQu\\u00e9 tal el d\\u00eda?",      nl:"Hoi! Hoe is je dag?",                en:"Hi! How's your day?"},
  {es:"\\u00bfQu\\u00e9 has comido hoy?",                nl:"Wat heb je vandaag gegeten?",        en:"What did you eat today?"},
  {es:"\\u00bfD\\u00f3nde est\\u00e1s ahora?",                 nl:"Waar ben je nu?",                    en:"Where are you now?"},
  {es:"\\u00bfQu\\u00e9 vas a hacer ma\\u00f1ana?",            nl:"Wat ga je morgen doen?",             en:"What are you doing tomorrow?"},
  {es:"\\u00bfTe gusta m\\u00e1s el caf\\u00e9 o el t\\u00e9?",      nl:"Hou je meer van koffie of thee?",    en:"Do you prefer coffee or tea?"},
  {es:"\\u00bfC\\u00f3mo es tu casa?",                   nl:"Hoe is je huis?",                    en:"What's your house like?"},
  {es:"\\u00bfQu\\u00e9 tiempo hace hoy?",               nl:"Wat voor weer is het vandaag?",      en:"What's the weather like today?"},
  {es:"\\u00bfCon qui\\u00e9n vives?",                   nl:"Met wie woon je?",                   en:"Who do you live with?"}
];
/* De openingszin wordt als index bewaard en niet als tekst: anders staat er morgen Nederlands in een
   Engels profiel. Wat het model later stuurt is wél tekst, want dat bestaat maar in één taal. */
function chatStand(){
  if(!S.chat || S.chat.d !== today()) S.chat = {d:today(), beurten:[], klaar:false};
  if(!S.chat.beurten.length) S.chat.beurten.push({van:"chispa", i:dayHash("chat") % CHAT_OPENERS.length});
  return S.chat;
}
function chatTekst(b){
  if(typeof b.i === "number"){
    var o = CHAT_OPENERS[b.i] || CHAT_OPENERS[0];
    return {es:o.es, nl:ct(o.nl, o.en)};
  }
  return {es:b.es || "", nl:b.nl || ""};
}
function chatMijn(){
  return chatStand().beurten.filter(function(b){ return b.van === "jij"; }).length;
}
function chatKlaar(){ return chatMijn() >= CHAT_BEURTEN; }
function chatGedaanVandaag(){ return !!(S.chat && S.chat.d === today() && S.chat.klaar); }
var chatBezig = false;
/* Het profielveld heet "beginner" of "a2"; de server kent niveaus. gwTrackKey() is de plek waar die
   vertaling al staat, dus die wordt hier hergebruikt in plaats van hem opnieuw op te schrijven. */
function chatNiveau(){
  try { return gwTrackKey() === "a0" ? "a0" : "a2"; } catch(e){ return "a2"; }
}

function renderChat(){
  var el = document.getElementById("chatWrap");
  if(!el) return;
  var st = chatStand(), klaar = chatKlaar();
  var inFlow = !!(lesFlow && lesFlow.stap === "produceren");
  var h = (inFlow ? lesFlowBannerHtml() : "")+"<div class='card'>"+
    "<span class='kicker'>"+ct("Praten met Chispa","Talking with Chispa")+" \\u00b7 "+
      (klaar ? ct("klaar","done")
             : ct("beurt ","turn ")+(chatMijn()+1)+"/"+CHAT_BEURTEN)+"</span>";
  st.beurten.forEach(function(b){
    var t = chatTekst(b);
    if(b.van === "chispa"){
      h += "<div class='chatrij'>"+chispaMiniSvg()+
        "<div class='bel zij'><span class='es'>"+veiligHtml(t.es)+"</span>"+
        (t.nl ? "<span class='nl'>"+veiligHtml(t.nl)+"</span>" : "")+"</div></div>";
    } else {
      h += "<div class='chatrij ik'><div class='bel ik'>"+veiligHtml(t.es)+"</div></div>";
      if(b.naast) h += "<div class='naast'>"+veiligHtml(b.naast)+"</div>";
    }
  });
  if(chatBezig){
    h += "<p class='muted' style='margin:6px 0 0'>\\ud83e\\udd16 "+ct("Chispa denkt na...","Chispa is thinking...")+"</p>";
  }
  h += "<div id='chatHulpVak'></div>";
  if(klaar){
    h += "<div class='feedback ok' style='margin-top:10px'>"+
      ct("Drie beurten, en je hebt ze zelf bedacht. Dat is iets anders dan een zin vertalen.",
         "Three turns, and you came up with them yourself. That's not the same as translating a sentence.")+"</div>"+
      "<div class='row' style='margin-top:10px'>"+
        (inFlow ? "<button class='primary' id='chatFlow'>"+ct("Verder met je les \\u2192","On with your session \\u2192")+"</button>"
                : "<button class='primary' id='chatTerug'>"+ct("Klaar","Done")+"</button>")+
      "</div>";
  } else {
    h += "<input type='text' id='chatInvoer' style='margin-top:10px' placeholder='"+
      ct("Schrijf je antwoord in het Spaans...","Write your answer in Spanish...")+"' autocomplete='off'>"+
      "<div class='row' style='margin-top:8px'>"+
        "<button class='primary' id='chatStuur'"+(chatBezig ? " disabled" : "")+">"+ct("Versturen","Send")+"</button>"+
        "<button class='ghost' id='chatHulp'>"+ct("Hoe zeg ik...?","How do I say...?")+"</button>"+
        (inFlow ? "<button class='ghost' id='chatFlow'>"+ct("Overslaan \\u2192","Skip \\u2192")+"</button>"
                : "<button class='ghost' id='chatTerug'>"+ct("\\u2190 Terug","\\u2190 Back")+"</button>")+
      "</div>";
  }
  el.innerHTML = h + "</div>";
  chatWire();
}

function chatWire(){
  var b;
  b = document.getElementById("chatStuur"); if(b) b.onclick = chatStuur;
  b = document.getElementById("chatHulp"); if(b) b.onclick = chatHulpVak;
  b = document.getElementById("chatFlow"); if(b) b.onclick = function(){ chatStand().klaar = true; persist(); lesFlowVolgende(); };
  b = document.getElementById("chatTerug"); if(b) b.onclick = function(){ chatStand().klaar = true; persist(); show("chispa"); };
  var inv = document.getElementById("chatInvoer");
  if(inv){
    inv.onkeydown = function(e){ if(e.key === "Enter"){ e.preventDefault(); chatStuur(); } };
    inv.focus();
  }
  try { lesFlowWireBanner(); } catch(e){}
}

function chatStuur(){
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
}

/* Vastlopen mag in het Nederlands. Wat eruit komt gaat rechtstreeks in je invoerveld: dan is de
   volgende handeling versturen en niet overtypen. */
function chatHulpVak(){
  var vak = document.getElementById("chatHulpVak");
  if(!vak) return;
  if(vak.innerHTML){ vak.innerHTML = ""; return; }
  vak.innerHTML = "<div class='naast amber' style='margin-top:8px'>"+
    "<p style='margin:0 0 6px'>"+ct("Wat wil je zeggen? Schrijf het gewoon in het Nederlands.",
                                    "What do you want to say? Just write it in Dutch.")+"</p>"+
    "<input type='text' id='chatHulpIn' placeholder='"+ct("ik heb hem van mijn buurvrouw gekregen",
                                                          "my neighbour gave it to me")+"' autocomplete='off'>"+
    "<div class='row' style='margin-top:6px'><button class='mini' id='chatHulpGo'>"+
      ct("Zeg het me","Tell me")+"</button></div><div id='chatHulpUit'></div></div>";
  var go = document.getElementById("chatHulpGo");
  var hin = document.getElementById("chatHulpIn");
  function vraag(){
    var v = hin ? (hin.value || "").trim() : "";
    if(!v) return;
    var uit = document.getElementById("chatHulpUit");
    if(uit) uit.innerHTML = "<p class='muted' style='margin:6px 0 0'>\\ud83e\\udd16 "+ct("Even kijken...","One moment...")+"</p>";
    api("/api/ai/chat", "POST", {modus:"hulp", vraag:v, niveau:chatNiveau()})
      .then(function(res){
        var u = document.getElementById("chatHulpUit");
        if(!u) return;
        if(!res || !res.ok || !res.es){ u.innerHTML = "<p class='muted' style='margin:6px 0 0'>"+aiFoutTekst(res)+"</p>"; return; }
        u.innerHTML = "<p style='margin:6px 0 0'><b class='es'>"+veiligHtml(res.es)+"</b></p>"+
          (res.uitleg ? "<p class='muted' style='margin:2px 0 0'>"+veiligHtml(res.uitleg)+"</p>" : "");
        var inv = document.getElementById("chatInvoer");
        if(inv){ inv.value = res.es; inv.focus(); }
      });
  }
  if(go) go.onclick = vraag;
  if(hin){ hin.onkeydown = function(e){ if(e.key === "Enter"){ e.preventDefault(); vraag(); } }; hin.focus(); }
}

function renderChispaPagina(){""",
)

rep(
    """function renderChispaPagina(){
  renderPet();
  try { renderGroei(); renderVitrine(); renderKamer(); } catch(e){}
}""",
    """function renderChispaPagina(){
  renderPet();
  try { renderGroei(); renderVitrine(); renderKamer(); } catch(e){}
  try { renderChatKaart(); } catch(e){}
}
/* v23.144: de deur naar het gesprek, op de pagina waar Chispa woont. */
function renderChatKaart(){
  var el = document.getElementById("chatCard");
  if(!el) return;
  var gedaan = chatGedaanVandaag();
  el.innerHTML = "<span class='kicker'>"+ct("Praten met Chispa","Talking with Chispa")+"</span>"+
    "<p class='muted' style='margin:0 0 8px'>"+
      (gedaan ? ct("Jullie hebben vandaag gepraat. Morgen weer, met een nieuwe vraag.",
                   "You two talked today. Tomorrow again, with a new question.")
              : ct("Drie beurten in het Spaans. Zij begint, jij mag zeggen wat je wilt, en onder je zin staat of hij klopt.",
                   "Three turns in Spanish. She starts, you say whatever you like, and under your sentence you see if it holds up."))+
    "</p>"+
    "<div class='row'><button class='"+(gedaan ? "ghost" : "primary")+"' id='btnNaarChat'>"+
      (gedaan ? ct("Nog eens praten","Talk again") : ct("Praat met Chispa \\u2192","Talk with Chispa \\u2192"))+"</button></div>";
  var b = document.getElementById("btnNaarChat");
  if(b) b.onclick = function(){ show("chat"); };
}""",
)

rep(
    """    <div class="card" id="kamerCard"></div>""",
    """    <div class="card" id="chatCard"></div>
    <div class="card" id="kamerCard"></div>""",
)

# ================= 5. en als voorstel na je les =================

rep(
    """  /* v23.141: de route komt hier, op plek twee.""",
    """  /* v23.144: het gesprek staat op plek twee, vóór je route.

     Waarom vóór: een route is er altijd en heeft tientallen stappen, dus alles wat erachter staat
     komt nooit aan de beurt (gemeten: het gespreksvoorstel kwam met de route ervoor geen enkele
     keer bovendrijven). Een gesprek is er één per dag en het is op, dus het kan alleen vandaag.
     Wat schaars is gaat voor wat er morgen ook nog staat.

     Eén per dag: een tweede gesprek op dezelfde dag is geen voorstel meer maar aandringen. */
  if(!chatGedaanVandaag()){
    return {icon:"\\ud83d\\udcac",
      kop:ct("Praat even met Chispa","Have a chat with Chispa"),
      waarom:ct("Drie beurten in het Spaans, en jij bepaalt wat je zegt. Dat is iets anders dan een zin vertalen: je moet haar begrijpen om te kunnen antwoorden.",
                "Three turns in Spanish, and you decide what to say. That's not the same as translating a sentence: you have to understand her to answer."),
      knop:ct("Beginnen","Start"),
      doe:function(){ show("chat"); }};
  }
  /* v23.141: de route komt hier, op plek twee.""",
)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_SRV:
    with io.open(PAD_SRV, "w", encoding="utf-8") as f:
        f.write(srv)
    print("server/index.js bijgewerkt")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
