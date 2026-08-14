#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.101: de fout die je net maakte wijst naar de regel erachter (punt 34, en daarmee punt 23).

## Wat er speelde

Stefan, 14 augustus: "en de grammatica, ik maak veel deze fout. en dat komt omdat ik uitleg mis of
instructie. pas ik de regel goed toe of niet? of ken ik gewoon het juiste woordje niet." En even
later, concreter: "dit foutje es está die maak ik vaker, wordt dat inhoudelijk goed gelogd?"

Het antwoord was nee. Je typte "Mi hermana está alta", de app onderstreepte *es* en zei "nog niet",
en daarmee hield het op. Er stond wél een fout in `S.errors`, maar op de zín. De app wist dus dat je
zin s142 fout had, niet dat je ser en estar door elkaar haalt. Dat is het verschil tussen een
strafregister en een diagnose: het eerste laat de zin vaker terugkomen, het tweede laat je de regel
leren waardoor hij niet meer terugkomt.

`bestDiff()` wist het antwoord al. Die functie vergelijkt woord voor woord en weet precies dat er
*es* hoorde te staan en dat jij *está* schreef. Dat paar ging alleen nergens heen: het werd meteen
in HTML gegoten om te onderstrepen en daarna weggegooid.

## Wat er nu gebeurt

Het paar (wat hoorde er, wat schreef jij) gaat langs een tabel van bekende verwarringen. Staat het
er in, dan drie dingen:

1. onder je antwoord staat waaróm het fout is, in één zin: "Je schreef está waar es hoort. Dat is
   geen woordje maar een regel: Ser of estar."
2. er staat een knop naast "Probeer opnieuw" die je rechtstreeks in de microles van dat onderwerp
   zet. Dat is punt 23: een toetsje hoort bereikbaar te zijn op het moment dat het ergens over
   gaat, en dat moment is nu.
3. `gramBij(cid, false)` noteert de fout op het onderwerp. Daarmee gaat dat onderwerp naar doos 0
   met vervaldatum morgen, en pikt `lesFlowGramId()` hem vanzelf op zodra je er twee keer op
   struikelt: dan opent je dagles morgen met precies deze regel. Die weg bestond al, hij kreeg
   alleen nooit iets binnen vanuit het echte werk.

Punt 3 is de belangrijkste van de drie en de enige die ook werkt als je de knop nooit aanraakt.

## Waarom een tabel en geen slimmigheid

De verleiding is een regel die altijd iets zegt: kijk naar de tag van de zin, of laat een model
raden. Beide leveren een onderwerp op dat plausibel is en soms fout, en een verkeerde diagnose is
erger dan geen diagnose, want hij stuurt je oefening de verkeerde kant op.

Daarom een tabel van paren die alleen afgaat als hij het zeker weet: allebei de woorden moeten in
hetzelfde paar staan. *es* tegenover *está* is ser-of-estar. *hay* tegenover *está* is hay-of-está.
*fue* tegenover *era* is indefinido-of-imperfecto. Maar *mesa* tegenover *silla* is gewoon een
woordje dat je niet kende, en daar zegt de app niets. Zwijgen is het normale geval: van de 23
onderwerpen zitten er 19 in de tabel, en die dekken alleen hun eigen verwarringen.

Vier onderwerpen staan er met opzet niet in:

- **perfecto of indefinido** en **de persoonlijke a**: die fouten zijn een woord meer of minder
  ("he hablado" tegenover "hablé"), en dan schuiven alle woorden op. Woord-voor-woord vergelijken
  ziet dat als vijf verschillen in plaats van één keuze.
- **woorden die meetellen** (rojo/roja) en **presente of gerundio**: die zijn wél te herkennen aan
  de vorm, maar niet te onderscheiden van een tikfout. Een regel die bij elke verschreven klinker
  aangaat, leert je de app te negeren.

Accenten spelen hier geen rol: `bestDiff()` vergelijkt zonder accenten, dus *esta* voor *está* is
voor de app geen verschil en komt hier nooit langs. Alles wat wél langskomt is een woordkeuze.

## De poort

`test/suites/pw-foutregel.js`, met drie controlegevallen. Een tabel die overal iets in ziet is net
zo groen als een tabel die nooit iets ziet, en allebei zijn ze kapot. Dus: *mesa* tegenover *silla*
moet zwijgen, een goed antwoord moet zwijgen, en een goed antwoord mag geen enkel onderwerp op fout
zetten.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.101"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.101" not in src
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


# ------------------------------------------------- bestDiff geeft het paar terug
A_DIFF = '''    var m = 0, html = [];
    for(var i=0;i<aTok.length;i++){
      var g = gTok[i] || "";
      if(stripAcc(g) === stripAcc(aTok[i])){ html.push(aTok[i]); }
      else { m++; html.push("<span class='diffword'>"+aTok[i]+"</span>"); }
    }
    m += Math.max(0, gTok.length - aTok.length);
    if(best === null || m < best.m) best = {m:m, len:aTok.length, html:html.join(" ")};
  });
  return best;
}'''
N_DIFF = '''    var m = 0, html = [], paren = [];
    for(var i=0;i<aTok.length;i++){
      var g = gTok[i] || "";
      if(stripAcc(g) === stripAcc(aTok[i])){ html.push(aTok[i]); }
      else {
        m++; html.push("<span class='diffword'>"+aTok[i]+"</span>");
        /* v23.101: welk woord hoorde er, en wat schreef jij. Dat paar was er altijd al; het ging
           alleen meteen in HTML om te onderstrepen en daarna weg. Zonder paar is een diff iets om
           te tonen, met paar is hij een aanwijzing. Zie foutRegel() hieronder.
           Een leeg g betekent dat je zin korter was: dan mist er een woord en is er geen keuze
           gemaakt, dus daar valt niets te diagnosticeren. */
        if(g) paren.push({v:aTok[i], g:g});
      }
    }
    m += Math.max(0, gTok.length - aTok.length);
    if(best === null || m < best.m) best = {m:m, len:aTok.length, html:html.join(" "), paren:paren};
  });
  return best;
}

/* ================= VAN FOUT NAAR REGEL (v23.101, punt 34 en 23) =================

   "dit foutje es está die maak ik vaker, wordt dat inhoudelijk goed gelogd?" — nee. De fout ging
   naar S.errors op de zín, dus de app wist dat zin s142 fout was en niet dat ser en estar door
   elkaar liepen. Dat is een strafregister, geen diagnose.

   Deze tabel maakt er een diagnose van, maar alleen waar hij het zeker weet. De eis is dat allebei
   de woorden in hetzelfde paar staan: jij schreef de ene, er hoorde de andere. Dan is het geen
   woordje dat je miste maar een keuze die je verkeerd maakte, en daar hoort een regel bij.

   Waarom paren en geen woordgroepen: met een groep ["es","esta","hay"] zou "hay" tegenover "esta"
   op ser-of-estar uitkomen terwijl het hay-of-está is. Paren kunnen dat niet verwarren, en dat is
   het meer typwerk waard.

   Wat er bewust NIET in staat, zie de kop van patch-v23.101: perfindef en apersonal zijn een woord
   meer of minder (dan schuift de hele zin op en ziet een woord-voor-woordvergelijking vijf
   verschillen in plaats van één keuze), concordancia en gerundio zijn niet te onderscheiden van
   een tikfout.

   Accenten komen hier nooit langs: bestDiff() vergelijkt met stripAcc, dus "esta" voor "está" is
   geen verschil. Alles wat hier binnenkomt is een woordkeuze. */
var FOUT_REGEL = [
  {cid:"serestar", p:[["es","esta"],["son","estan"],["soy","estoy"],["eres","estas"],
                      ["somos","estamos"],["ser","estar"],["fue","estuvo"],["era","estaba"],
                      ["sido","estado"],["sea","este"]]},
  {cid:"hayestar", p:[["hay","esta"],["hay","estan"],["hay","es"],["hay","son"],["habia","estaba"]]},
  {cid:"indefimperf", p:[["fue","era"],["fueron","eran"],["tuvo","tenia"],["estuvo","estaba"],
                         ["hizo","hacia"],["hubo","habia"],["quiso","queria"],["supo","sabia"],
                         ["pudo","podia"],["dijo","decia"],["vino","venia"],["fui","iba"],
                         ["tuve","tenia"],["estuve","estaba"],["empezo","empezaba"]]},
  {cid:"porpara", p:[["por","para"]]},
  {cid:"muymucho", p:[["muy","mucho"],["muy","mucha"],["muy","muchos"],["muy","muchas"],
                      ["mucho","mucha"],["muchos","muchas"]]},
  {cid:"gustar", p:[["gusta","gustan"],["gustaba","gustaban"],["encanta","encantan"],
                    ["duele","duelen"],["interesa","interesan"],["parece","parecen"],
                    ["queda","quedan"]]},
  {cid:"quecual", p:[["que","cual"],["que","cuales"],["cual","cuales"]]},
  {cid:"comparar", p:[["que","como"],["mas","tan"],["mas","menos"],["tan","tanto"],
                      ["tanta","tan"],["tantos","tan"]]},
  /* genero vóór pronombre: "el" tegenover "la" is het lidwoord, "lo" tegenover "la" is het
     voornaamwoord. De paren overlappen niet, de volgorde is er voor de lezer. */
  {cid:"genero", p:[["el","la"],["los","las"],["un","una"],["unos","unas"],["el","los"],["la","las"]]},
  {cid:"pronombre", p:[["lo","la"],["lo","le"],["la","le"],["los","les"],["las","les"],["le","les"]]},
  {cid:"reflexivo", p:[["me","te"],["me","se"],["te","se"],["se","nos"],["me","nos"]]},
  {cid:"demostrativo", p:[["este","ese"],["esta","esa"],["estos","esos"],["estas","esas"],
                          ["ese","aquel"],["esa","aquella"],["esto","eso"],["eso","aquello"]]},
  {cid:"saberconocer", p:[["se","conozco"],["sabe","conoce"],["saber","conocer"],
                          ["sabes","conoces"],["sabemos","conocemos"],["saben","conocen"]]},
  {cid:"saberpoder", p:[["se","puedo"],["sabe","puede"],["saber","poder"],["sabes","puedes"],
                        ["sabemos","podemos"],["saben","pueden"]]},
  {cid:"pedirpreguntar", p:[["pido","pregunto"],["pide","pregunta"],["pedir","preguntar"],
                            ["pides","preguntas"],["pedi","pregunte"],["pidio","pregunto"]]},
  {cid:"tuusted", p:[["tu","usted"],["tus","sus"],["tuyo","suyo"],["contigo","con"]]},
  {cid:"negacion", p:[["nada","algo"],["nadie","alguien"],["nunca","siempre"],["ningun","algun"],
                      ["ninguna","alguna"],["tampoco","tambien"],["nada","nadie"]]},
  {cid:"futuroir", p:[["voy","ire"],["va","ira"],["vamos","iremos"],["van","iran"],["vas","iras"]]},
  /* De klassieke uitkomst van "de klinker wisselt niet mee": een leerling schrijft de stam van de
     infinitief. Dit is de enige plek waar de tabel een vorm bevat die geen goed Spaans is, en dat
     hoort zo: het is precies de vorm die je typt als je de regel niet kent. */
  {cid:"zapato", p:[["quiero","quero"],["quiere","quere"],["puedo","podo"],["puede","pode"],
                    ["tiene","tene"],["tienes","tenes"],["vuelvo","volvo"],["vuelve","volve"],
                    ["empieza","empeza"],["duermo","dormo"],["pienso","penso"],["juega","juga"],
                    ["cierra","cerra"],["sigue","sige"]]}
];
function foutRegelKaal(w){ return stripAcc(String(w || "").toLowerCase()); }
/* Geeft {cid, v, g, naam} terug, of null. Null is het normale geval: een woord dat je niet kende is
   geen regel, en daar hoort de app niets over te beweren. */
function foutRegel(d){
  var paren = (d && d.paren) || [];
  for(var i = 0; i < paren.length; i++){
    var v = foutRegelKaal(paren[i].v), g = foutRegelKaal(paren[i].g);
    if(!v || !g || v === g) continue;
    for(var j = 0; j < FOUT_REGEL.length; j++){
      var lijst = FOUT_REGEL[j].p;
      for(var k = 0; k < lijst.length; k++){
        var a = lijst[k][0], b = lijst[k][1];
        if((v === a && g === b) || (v === b && g === a)){
          var c = gcConcept(FOUT_REGEL[j].cid);
          if(!c) continue;
          return {cid:c.id, v:paren[i].v, g:paren[i].g, naam:ct(c.naam, c.naamEn)};
        }
      }
    }
  }
  return null;
}'''

# ------------------------------------------------- checkSentence
A_VARS = '''  var html = "", gehaald = false, retryable = false;'''
N_VARS = '''  var html = "", gehaald = false, retryable = false, fregel = null;   // v23.101: zie foutRegel()'''

A_ELSE = '''    var d = bestDiff(given, s);
    if(d.m <= 2 && d.len - d.m >= Math.ceil(d.len/2)){'''
N_ELSE = '''    var d = bestDiff(given, s);
    /* v23.101 (punt 34): hier eindigde het. De zin kreeg een strafregistratie en de regel erachter
       bleef ongenoemd, ook als hij overduidelijk was. gramBij(cid, false) zet dit onderwerp op doos
       0 met vervaldatum morgen; struikel je er twee keer over, dan opent lesFlowGramId() je dagles
       er morgen mee. Die weg bestond al en kreeg alleen nooit iets binnen uit het echte werk.
       Dit gebeurt ook als je de knop hieronder nooit aanraakt, en dat is met opzet het belangrijkste
       deel: je hoeft niet te weten dat je iets fout doet om er beter in te worden. */
    fregel = foutRegel(d);
    if(fregel) gramBij(fregel.cid, false);
    if(d.m <= 2 && d.len - d.m >= Math.ceil(d.len/2)){'''

A_ROW = '''  html += "<div class='row'>"+
    (retryable ? "<button class='primary' id='btnRetry'>"+ct("Probeer opnieuw","Try again")+"</button>"'''
N_ROW = '''  /* v23.101 (punt 23): een toetsje is iets dat naar je toe hoort te komen, niet iets dat je
     opzoekt. Wie 's avonds bedenkt "ik ga een toetsje maken" oefent voor de uitslag; wie de fout
     net gemaakt heeft, oefent voor de regel. Dit is dat moment.
     veiligHtml() om fregel.g heen: dat is letterlijk wat de gebruiker heeft ingetypt, en dit is de
     enige plek in de app waar dat weer op het scherm komt. */
  if(fregel){
    var fgV = "<b>"+veiligHtml(fregel.v)+"</b>", fgG = "<b>"+veiligHtml(fregel.g)+"</b>";
    html += "<p class='muted' style='margin:8px 2px 0; font-size:.9rem'>"+
      ct("Je schreef "+fgG+" waar "+fgV+" hoort. Dat is geen woordje dat je miste maar een keuze, en daar hoort een regel bij: <b>"+fregel.naam+"</b>.",
         "You wrote "+fgG+" where "+fgV+" belongs. That is not a word you were missing but a choice, and there is a rule behind it: <b>"+fregel.naam+"</b>.")+"</p>";
  }
  html += "<div class='row'>"+
    (retryable ? "<button class='primary' id='btnRetry'>"+ct("Probeer opnieuw","Try again")+"</button>"+
    (fregel ? "<button class='ghost' id='btnFoutRegel'>\\ud83d\\udcd8 "+ct("Oefen "+fregel.naam,"Practise "+fregel.naam)+"</button>" : "")'''

A_WIRE = '''  var br = document.getElementById("btnRetry");
  if(br) br.onclick = function(){ renderSentence(false); };'''
N_WIRE = '''  var br = document.getElementById("btnRetry");
  if(br) br.onclick = function(){ renderSentence(false); };
  /* v23.101: rechtstreeks de microles in, niet naar een overzicht met kaartjes. Wie eerst nog moet
     zoeken welk kaartje het was, is de fout al vergeten. gwStart regenereert de vragen (v20.5), dus
     je krijgt niet het toetsje dat je vorige week uit je hoofd hebt geleerd. */
  var bfr = document.getElementById("btnFoutRegel");
  if(bfr) bfr.onclick = function(){ zinDoorStop(); show("spiekbrief"); gwStart("concept-"+fregel.cid); };'''

if DOE_APP:
    ontbreekt = [n for n, a in (
        ("bestDiff", A_DIFF), ("de variabelen van checkSentence", A_VARS),
        ("de foutafhandeling van een zin", A_ELSE), ("de knoppenrij", A_ROW),
        ("de knop Probeer opnieuw", A_WIRE)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.100. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_DIFF, N_DIFF)
    rep(A_VARS, N_VARS)
    rep(A_ELSE, N_ELSE)
    rep(A_ROW, N_ROW)
    rep(A_WIRE, N_WIRE)

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
