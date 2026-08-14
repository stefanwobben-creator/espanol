#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.95: de laatste stap wordt een typtoets, de steekproef gaat echt steekproeven, en je week krijgt
een getal (punt 4, 8 en 9).

## Punt 4: de laatste stap is nu typen

Vlak voordat een woord "vast" heet krijg je één toets. Die was een keuze uit vier, en de reden
daarvoor staat in de kop van v20.0: "op een telefoon is typen met accenten een gevecht met je
toetsenbord in plaats van met het Spaans". Dat argument klopte toen en klopt nu niet meer, want de
app heeft sindsdien `accentToetsenHtml()`: een rijtje accentknoppen boven het invoerveld, precies
voor dit probleem. Het vertaalscherm gebruikt dat al.

En er staat iets tegenover. Een keuze uit vier gokt 25 procent binnen, en `st.k` is definitief: wie
er doorheen gokt, krijgt die check nooit meer. Bij Stefan komen de komende twee weken 227 woorden
langs die allemaal op doos 4 staan. Met een keuze uit vier zouden daar tientallen bij zitten die hun
stempel op geluk krijgen, en dat stempel gaat nooit meer weg.

Accenten worden goedgerekend, zoals overal in de app. Strenger zijn dan de rest van de app zou hier
betekenen dat je je woord kwijtraakt op een toetsenbord in plaats van op je Spaans. De juiste vorm
mét accent staat wel in de uitslag, want dat is waar je hem leert.

En er is een uitweg: "Ik weet het niet". Zonder die knop is een leeg invoerveld een val, en dat is
precies het tegenovergestelde van wat een laatste stap moet zijn. Hij telt als fout, net als een
verkeerd antwoord: een doos terug en vandaag nog een keer.

`wCheckOpties()` is daarmee overbodig en gaat weg.

## Punt 8: de steekproef trok geen steekproef

`quizVraagVolgorde()` sorteerde op "eerder fout gedaan" en deed verder niets. Die sortering is
stabiel, dus wie niets fout had staan kreeg de vragen in hun oorspronkelijke volgorde: bij een
dagtoets van vier vragen dus vraag 1 tot en met 4, elke dag, altijd dezelfde. Wat er gemeten werd was
niet of je de regel snapt maar of je je die vier vragen herinnert, en dat wordt met de dag makkelijker.
Het cijfer steeg terwijl het begrip stilstond.

Nu: fout eerst, daarna wat je het langst niet hebt gehad, en gelijkspel wordt geschud. Over twee
weken zie je zo alle tien vragen in plaats van vier.

En de score. Een steekproef van vier vragen werd teruggerekend naar de volle lengte, dus 4/4 werd
10/10. Nu wordt opgeslagen wat je echt haalde. Dat blokkeert niets: `lessonProgress()` gebruikt `qa`
(heb je het toetsje ooit gemaakt) om de volgende les te openen, en `q` (minstens 80 procent) voor het
vinkje. De volgende les gaat dus gewoon open, en het vinkje vraagt voortaan wat het altijd al beloofde:
de hele toets, goed gemaakt.

## Punt 9: je week krijgt een getal

Op Voortgang werden `nieuw14`, `tempo` en `venster` al berekend en daarna weggegooid: `koersHtml`
bleef leeg sinds v23.37. Ondertussen is "ik zie niet dat ik iets leer" Stefans hoofdklacht.

Er staat nu één regel: hoeveel nieuwe woorden je deze week hebt opgepakt, hoeveel vorige week, en
hoeveel er in totaal vaststaan. Geen nieuwe meting, alleen het getal dat er al lag.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.95"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.95" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ================================================================ punt 4
A_OPTIES = '''function wCheckOpties(w){
  // afleiders het liefst uit dezelfde categorie: dan gaat de vraag over het woord en niet over
  // welke van de vier er toevallig bij het onderwerp past.
  var pool = WORDS.filter(function(x){ return x.id !== w.id && x.es !== w.es; });
  var zelfde = pool.filter(function(x){ return x.tag === w.tag; });
  var bron = zelfde.length >= 3 ? zelfde : pool;
  var g = geschud(bron), gezien = {}, af = [], i;
  for(i = 0; i < g.length && af.length < 3; i++){
    if(gezien[g[i].es]) continue;
    gezien[g[i].es] = 1;
    af.push(g[i].es);
  }
  return geschud([w.es].concat(af));
}

'''

A_RENDER_KOP = '''  if(!wCheck || wCheck.id !== w.id) wCheck = {id:w.id, opties:wCheckOpties(w), gekozen:null, goed:false};'''
N_RENDER_KOP = '''  if(!wCheck || wCheck.id !== w.id) wCheck = {id:w.id, gekozen:null, goed:false, accentMis:false};'''

A_OPTIEBLOK = '''    "<div style='display:flex; flex-direction:column; gap:8px' id='wCheckOpties'>"+
      wCheck.opties.map(function(o){
        var cls = "ghost";
        if(wCheck.gekozen){
          if(o === w.es) cls = "good";
          else if(o === wCheck.gekozen) cls = "bad";
        }
        return "<button type='button' class='"+cls+"' data-wcheck=\\""+o.replace(/"/g,"&quot;")+
          "\\" style='text-align:left'>"+o+"</button>";
      }).join("")+
    "</div>";'''
N_OPTIEBLOK = '''    /* v23.95: hier stonden vier knoppen. Zie de kop van de patch: een op vier gokt zich erdoor en
       st.k is definitief, dus een gokje kostte je die check voorgoed. Typen kan sinds v23.x prima op
       een telefoon, want accentToetsenHtml() staat eronder. */
    (wCheck.gekozen === null
      ? "<input type='text' id='wCheckInp' autocomplete='off' autocapitalize='off' spellcheck='false' placeholder='"+
          ct("Typ het Spaanse woord...","Type the Spanish word...")+"'>"+
        accentToetsenHtml("wCheckAccent")+
        "<div class='row'><button class='primary' id='btnWCheckOk'>"+ct("Controleer","Check")+"</button></div>"+
        "<button class='mini' id='btnWCheckWeetNiet'>"+ct("Ik weet het niet","I don't know")+"</button>"
      : "<p class='big es' style='margin:2px 0 0'>"+w.es+"</p>");'''

A_UITSLAG = '''  if(wCheck.gekozen){
    html += "<p class='waarom'>"+(wCheck.goed
      ? ct("Goed. <b class='es'>"+w.es+"</b> staat vanaf nu vast en telt mee in je A1-balk.",
           "Correct. <b class='es'>"+w.es+"</b> is solid from now on and counts towards your A1 bar.")
      : ct("Het was <b class='es'>"+w.es+"</b>. Dit woord gaat een doosje terug en komt zo nog een keer langs.",
           "It was <b class='es'>"+w.es+"</b>. This word steps back one box and comes by again shortly."))+"</p>"+'''
N_UITSLAG = '''  if(wCheck.gekozen !== null){
    html += "<p class='waarom'>"+(wCheck.goed
      ? (wCheck.accentMis
          ? ct("Goed, alleen de accenten: het is <b class='es'>"+w.es+"</b>. Hij staat vanaf nu vast en telt mee in je A1-balk.",
               "Correct, just the accents: it is <b class='es'>"+w.es+"</b>. It is solid from now on and counts towards your A1 bar.")
          : ct("Goed. <b class='es'>"+w.es+"</b> staat vanaf nu vast en telt mee in je A1-balk.",
               "Correct. <b class='es'>"+w.es+"</b> is solid from now on and counts towards your A1 bar."))
      : ct("Het was <b class='es'>"+w.es+"</b>. Dit woord gaat een doosje terug en komt zo nog een keer langs.",
           "It was <b class='es'>"+w.es+"</b>. This word steps back one box and comes by again shortly."))+"</p>"+'''

A_UITLEG_VOOR = '''      ct("Dit woord heb je vaak genoeg goed gehad. Vind je hem nu terug zonder dat het antwoord op het scherm staat, dan telt hij mee in je A1-balk.",
         "You have had this word right often enough. Find it now without the answer on screen and it counts towards your A1 bar.")+"</p>";'''
N_UITLEG_VOOR = '''      ct("Dit woord heb je vaak genoeg goed gehad. Typ hem nu zelf, zonder dat het antwoord op het scherm staat, en hij telt mee in je A1-balk. Accenten mag je weglaten.",
         "You have had this word right often enough. Type it yourself now, without the answer on screen, and it counts towards your A1 bar. Accents may be left out.")+"</p>";'''

A_WIRE = '''  el.querySelectorAll("[data-wcheck]").forEach(function(b){
    b.onclick = function(){
      if(wCheck && wCheck.gekozen) return;
      wCheckAntwoord(b.getAttribute("data-wcheck"));
    };
  });'''
N_WIRE = '''  var wi = document.getElementById("wCheckInp");
  if(wi){
    wireAccentToetsen("wCheckAccent", "wCheckInp");
    var stuur = function(){
      if(wCheck && wCheck.gekozen !== null) return;
      wCheckAntwoord(wi.value || "");
    };
    document.getElementById("btnWCheckOk").onclick = stuur;
    wi.addEventListener("keydown", function(e){ if(e.key === "Enter") stuur(); });
    /* Zonder deze knop is een leeg invoerveld een val: je weet het niet, je kunt geen kant op, en je
       zit vast op precies het scherm dat je wilde belonen. Hij telt als fout, net als een verkeerd
       antwoord, dus een doosje terug en vandaag nog een keer. */
    document.getElementById("btnWCheckWeetNiet").onclick = function(){
      if(wCheck && wCheck.gekozen !== null) return;
      wCheckAntwoord("");
    };
    try{ wi.focus(); }catch(e){}
  }'''

A_ANTWOORD = '''function wCheckAntwoord(keuze){
  var w = wCur, t = today(), st = S.srs[w.id];
  if(!st || typeof st !== "object") st = {box:0, due:t};
  var goed = (keuze === w.es);
  wCheck.gekozen = keuze;
  wCheck.goed = goed;'''
N_ANTWOORD = '''function wCheckAntwoord(gegeven){
  var w = wCur, t = today(), st = S.srs[w.id];
  if(!st || typeof st !== "object") st = {box:0, due:t};
  /* v23.95: getypt in plaats van gekozen. woordGetypt() doet hier het werk dat het ook bij de zinnen
     doet: accentloos goedrekenen, en "el pintor / la pintora" telt aan beide kanten. Een leeg
     antwoord ("Ik weet het niet") is per definitie fout. */
  var chk = String(gegeven).trim() ? woordGetypt(gegeven, w.es) : {goed:false, accentMis:false};
  var goed = chk.goed;
  wCheck.gekozen = String(gegeven);
  wCheck.goed = goed;
  wCheck.accentMis = !!chk.accentMis;'''

# ================================================================ punt 8
A_VOLGORDE = '''function quizVraagVolgorde(qz){
  var out = qz.vragen.map(function(v,i){ return {v:v, oi:i}; });
  out.sort(function(a,b){
    var ea = S.errors["quiz:"+qz.id+"#"+a.oi], eb = S.errors["quiz:"+qz.id+"#"+b.oi];
    var wa = !!(ea && ea.count > 0), wb = !!(eb && eb.count > 0);
    if(wa === wb) return 0;
    return wa ? -1 : 1;
  });
  return out;
}'''
N_VOLGORDE = '''/* v23.95: hier zat de steekproef die geen steekproef was.

   Deze sortering zette je foute vragen vooraan en deed verder niets. Array.sort is stabiel, dus wie
   niets fout had staan kreeg de vragen in hun oorspronkelijke volgorde, en een dagtoets van vier
   vragen leverde dan vraag 1 tot en met 4. Elke dag. Altijd dezelfde vier. Wat er gemeten werd was
   niet of je de regel snapt maar of je je die vier vragen herinnert, en dat wordt met de dag
   makkelijker: het cijfer steeg terwijl het begrip stilstond.

   Nu drie lagen: fout eerst, dan wat je het langst niet hebt gehad, en gelijkspel wordt geschud.
   S.qzGezien onthoudt per vraag de dag waarop je hem voor het laatst kreeg. */
function quizVraagVolgorde(qz){
  var gz = S.qzGezien || {};
  var out = qz.vragen.map(function(v,i){
    return {v:v, oi:i, laatst: gz[qz.id+"#"+i] || "", munt: Math.random()};
  });
  out.sort(function(a,b){
    var ea = S.errors["quiz:"+qz.id+"#"+a.oi], eb = S.errors["quiz:"+qz.id+"#"+b.oi];
    var wa = !!(ea && ea.count > 0), wb = !!(eb && eb.count > 0);
    if(wa !== wb) return wa ? -1 : 1;
    if(a.laatst !== b.laatst) return a.laatst < b.laatst ? -1 : 1;   // langst niet gehad eerst
    return a.munt - b.munt;
  });
  return out;
}
// De dag waarop deze vraag voor het laatst is gesteld. Zonder dit blijft de rotatie hierboven raden.
function quizVraagGezien(qzId, oi){
  S.qzGezien = S.qzGezien || {};
  S.qzGezien[qzId+"#"+oi] = today();
}'''

A_SCORE = '''    var pct = st.score/gesteld;
    // score terugrekenen naar de volle lengte, zodat een korte dagles je lesvoortgang niet blokkeert
    var geschat = Math.round(pct * qz.vragen.length);
    var prev = S.quiz[qz.id];
    if(prev===undefined || geschat>prev){ S.quiz[qz.id] = geschat; persist(); }'''
N_SCORE = '''    var pct = st.score/gesteld;
    /* v23.95: hier werd de score teruggerekend naar de volle lengte, dus 4/4 werd 10/10. Dat was
       nodig omdat een korte dagles anders je lespad zou blokkeren, maar het betekende ook dat vier
       vragen konden doorgaan voor een volledig beheerst toetsje.
       Dat blokkeren gebeurt niet: lessonProgress() opent de volgende les op `qa` (heb je dit toetsje
       ooit gemaakt) en zet het vinkje op `q` (minstens 80 procent). Dus we slaan gewoon op wat je
       echt haalde. De les gaat open, en het vinkje vraagt voortaan wat het altijd al beloofde: de
       hele toets, goed gemaakt. */
    var prev = S.quiz[qz.id];
    if(prev===undefined || st.score>prev){ S.quiz[qz.id] = st.score; persist(); }'''

A_TOON = '''  var v = st.volgorde[st.i].v;
  st.locked = false;'''
N_TOON = '''  var v = st.volgorde[st.i].v;
  quizVraagGezien(qz.id, st.volgorde[st.i].oi);   // v23.95: voor de rotatie, zie quizVraagVolgorde
  st.locked = false;'''

# ================================================================ punt 9
A_KOERS = '''  var koersHtml = "";'''
N_KOERS = '''  /* v23.95: hier stond `var koersHtml = "";` en daarboven werden nieuw14, tempo en venster
     uitgerekend om vervolgens weggegooid te worden. Ondertussen is "ik zie nergens dat ik iets leer"
     de klacht die Stefan het vaakst heeft. Het getal lag er dus al.

     Deze week tegenover vorige week, want een getal zonder vergelijking zegt niets, en daarnaast
     hoeveel er vaststaan. Nieuwe woorden opgepakt is met opzet niet hetzelfde als geleerd: het eerste
     kun je vandaag zien, het tweede duurt vijfentwintig dagen.

     Let op de volgorde: dit staat NA `var vast`/`var opweg` en op de plek waar koersHtml werd
     gedeclareerd. Vullen vóór de declaratie werkt niet, want `var koersHtml = ""` hoist en zet hem
     daarna weer leeg. */
  var nieuw7 = 0, nieuw7v = 0;
  for(var d7 = 0; d7 < 14; d7++){
    var dg7 = addDays(t2, -d7), n7 = (S.newIntro && S.newIntro[dg7]) || 0;
    if(d7 < 7) nieuw7 += n7; else nieuw7v += n7;
  }
  var koersHtml = "";
  if(nieuw7 || nieuw7v || vast){
    koersHtml = "<div class=\'card\'><span class=\'kicker\'>"+ct("Deze week","This week")+"</span>"+
      "<p style=\'margin:6px 0 0\'><b>"+nieuw7+"</b> "+
        ct(nieuw7 === 1 ? "nieuw woord opgepakt" : "nieuwe woorden opgepakt",
           nieuw7 === 1 ? "new word started" : "new words started")+
        (nieuw7v ? " <span class=\'muted\'>("+ct("vorige week","last week")+" "+nieuw7v+")</span>" : "")+"</p>"+
      "<p class=\'muted\' style=\'margin:4px 0 0\'>"+
        ct(vast+" staan vast, "+opweg+" bijna. Vaststaan kost vijfentwintig dagen, dus dat getal loopt achter op vandaag.",
           vast+" solid, "+opweg+" nearly there. Solid takes twenty-five days, so that number lags behind today.")+
      "</p></div>";
  }'''

A_KOERS_VUL = None  # zie hieronder: alles gebeurt op de plek van de declaratie

if DOE_APP:
    ontbreekt = [n for n, a in (
        ("wCheckOpties", A_OPTIES), ("de kop van renderWordCheck", A_RENDER_KOP),
        ("het optieblok", A_OPTIEBLOK), ("de uitslagtekst", A_UITSLAG),
        ("de uitleg vooraf", A_UITLEG_VOOR), ("de knoppenkoppeling", A_WIRE),
        ("wCheckAntwoord", A_ANTWOORD), ("quizVraagVolgorde", A_VOLGORDE),
        ("de toetsscore", A_SCORE), ("de vraagweergave", A_TOON),
        ("koersHtml", A_KOERS)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.94. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_OPTIES, "")
    rep(A_RENDER_KOP, N_RENDER_KOP)
    rep(A_OPTIEBLOK, N_OPTIEBLOK)
    rep(A_UITSLAG, N_UITSLAG)
    rep(A_UITLEG_VOOR, N_UITLEG_VOOR)
    rep(A_WIRE, N_WIRE)
    rep(A_ANTWOORD, N_ANTWOORD)
    rep(A_VOLGORDE, N_VOLGORDE)
    rep(A_SCORE, N_SCORE)
    rep(A_TOON, N_TOON)
    rep(A_KOERS, N_KOERS)

    src = re.sub(r'var APP_VERSIE = "[^"]+";', 'var APP_VERSIE = "%s";' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
