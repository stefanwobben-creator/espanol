#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.65: een spel dat je niet kent is geen aanbod, en een oefening is geen spel.

Stefan, 12 aug, over de kaart "Even spelen" op zijn dagscherm: "niet duidelijk wat een spelen is,
wat gebeurt er als ik daar klik, waarom zou ik dat doen ik snap het concept nog niet." En over de
knop eronder: "meer spellen maar waarom heb ik die unlocked? dan wil ik toch alle spellen zien maar
met eentje die niet locked is."

Wat er stond: vier tegels met een emoji en een Spaanse naam. "🔍 Sopa de letras". Verder niets. Een
vreemde weet niet wat dat is, en de app vertelt het pas nadat je erop hebt getikt.

## Eén: de uitleg bestond al, alleen op het andere scherm

Op "Alle spelletjes" staat bij elk spel een regel die zegt wat je doet ("puzzel met jouw geleerde
woorden"). Die regel stond niet op de dagkaart. Twee schermen die hetzelfde spel aanbieden, en één
ervan zwijgt. Nu is er één lijst, `spelInfo()`, en lezen ze er allebei uit.

De dagkaart ging van tegels naar regels, want in een tegel past die zin niet. En eronder staat, als
er nog iets dicht zit:

    Nog 5 spellen komen erbij als je meer woorden kent.   [ Alle spelletjes → ]

Dat was het antwoord op zijn tweede vraag, en het stond er niet. Het slot zelf was al goed geregeld
(v19.92: de dichte spellen staan grijs onder de open, met de eis erbij, plus een link "Laat ze toch
allemaal zien"); alleen wist je op de dagkaart niet dat dat scherm bestond.

## Twee: mijn eerste diagnose was fout, en de echte fout zat andersom

Ik legde de twee lijsten naast elkaar en zag dit:

    dagkaart (DAGSPELLEN)   ws  kruis  audi  conj  letras  adiv  clas  mem  corr
    alle spelletjes         ws  kruis    -     -   letras  adiv  clas  mem   -    + avt musica duel

Mijn conclusie was: de speeltuin laat er drie weg. Ik heb ze toegevoegd, en de poort werd rood op
pw-nav215.js, met een regel die er sinds v21.5 staat en die van Stefan zelf komt: "lessen, dat zijn
de oefeningen, die zitten nu ook onder speeltuin". Escuchar, El Corrector en Rompecabezas zijn geen
spellen maar oefeningen. Ze staan onder Oefenen, en de scheiding is in één zin te zeggen: onder
Oefenen telt het mee voor je niveau, onder Spelen niet.

De speeltuin hield zich dus keurig aan die regel. De dagkaart niet: onder de kop "Even spelen"
stonden drie oefeningen. Dat is de fout, en hij zat aan de kant waar ik hem niet zocht. Sinds deze
versie bevat de dagrotatie alleen spellen (zes), en de speeltuin ook (negen, inclusief Aventura,
Música en Palabra Duel).

Het eindscherm van de les wist het overigens al wel: `lesFlowWinst()` biedt El Corrector aan als
"hier win je het meeste", `lesFlowLeuk()` een spel als "of gewoon leuk".

## Eén naam per spel

De naam is die van het scherm waar je op landt. Meestal is dat Spaans; bij de woordenzoeker niet,
want dat scherm heet Woordenzoeker. Daarom staat er op de dagkaart geen "Sopa de letras" meer.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.65"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function spelInfo" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_LIJST = '''/* vier spelletjes, recht erin. Aventura staat vast (dat is het grote spel), de andere drie
   wisselen per dag, zodat je niet elke ochtend dezelfde drie ziet. */
var DAGSPELLEN = [
  {v:"ws",      e:"\\ud83d\\udd0d", n:"Sopa de letras"},
  {v:"kruis",   e:"\\u270f\\ufe0f", n:"Crucigrama"},
  {v:"audi",    e:"\\ud83d\\udc42", n:"Escuchar"},
  {v:"conj",    e:"\\ud83e\\udde9", n:"Rompecabezas"},
  {v:"letras",  e:"\\ud83d\\udd24", n:"Letras"},
  {v:"adiv",    e:"\\ud83d\\udfe9", n:"Adivina"},
  {v:"clas",    e:"\\u26a1", n:"Clasificador"},
  {v:"mem",     e:"\\ud83c\\udccf", n:"Memory"},
  {v:"corr",    e:"\\ud83d\\udd75\\ufe0f", n:"El Corrector"}
];'''

A_KEUZE = '''function dagSpelKeuze(){
  // v19.92: alleen spellen aanbieden die vandaag ook echt iets kunnen tonen. Een knop op je
  // dagscherm die uitkomt op "leer eerst wat meer woordjes" is een knop die je leert dat de
  // knoppen hier niet betrouwbaar zijn.
  var kan = DAGSPELLEN.filter(function(x){
    try { return speelKlaar(x.v); } catch(e){ return true; }
  });
  if(!kan.length) kan = DAGSPELLEN;
  var h = dayHash("spel");
  var uit = [];
  // De stap van 2 geeft de afwisseling per dag zolang de lijst lang genoeg is; de tweede ronde
  // met stap 1 vult aan als die stap in zichzelf terugvalt. Zonder die tweede ronde stond er op
  // dag 1 twee keer hetzelfde spel, en ontbrak het spel dat wel kon.
  for(var i = 0; i < kan.length && uit.length < 3; i++){
    var k1 = kan[(h + i * 2) % kan.length];
    if(uit.indexOf(k1) === -1) uit.push(k1);
  }
  for(var j = 0; j < kan.length && uit.length < 3; j++){
    var k2 = kan[(h + j) % kan.length];
    if(uit.indexOf(k2) === -1) uit.push(k2);
  }
  return uit;
}'''

A_LEUK = '''  var k = keus[0];
  return {icon:k.e, kop:k.n,'''

A_SPEELHTML = '''function dagSpeelHtml(){
  var keus = dagSpelKeuze();
  var knoppen = "<button class='speelknop' data-speel='avt'><span class='spe'>\\ud83d\\uddfa\\ufe0f</span>Aventura</button>";
  keus.forEach(function(k){
    knoppen += "<button class='speelknop' data-speel='"+k.v+"'><span class='spe'>"+k.e+"</span>"+k.n+"</button>";
  });
  return "<div class='card' id='speelKaart'><span class='kicker'>"+ct("Even spelen","Play something")+"</span>"+
    "<div class='speelgrid'>"+knoppen+"</div>"+
    "<div class='row' style='margin-top:8px'><button class='ghost' id='btnAlleSpellen'>"+ct("Alle spelletjes","All the games")+" \\u2192</button></div></div>";
}'''

A_MENU = '''  var SPEELMENU = [
    {v:"avt",     id:"ftAvt",     e:"\\ud83d\\uddfa\\ufe0f", t:"Aventura",           s:fx("avS")},
    {v:"musica",  id:"ftMusica",  e:"\\ud83c\\udfb5",        t:"M\\u00fasica",         s:fx("muS")},
    {v:"ws",      id:"ftWs",      e:"\\ud83d\\udd0d",        t:fx("wsT"),            s:fx("wsS")},
    {v:"kruis",   id:"ftKruis",   e:"\\u270f\\ufe0f",        t:"Crucigrama",         s:fx("krS")},
    {v:"letras",  id:"ftLetras",  e:"\\ud83d\\udd24",        t:"Letras",             s:ct("Zeven letters, hoeveel woorden haal je eruit? Geen klok.","Seven letters, how many words can you find? No clock.")},
    {v:"adiv",    id:"ftAdiv",    e:"\\ud83d\\udfe9",        t:"Adivina",            s:ct("Raad het woord in vijf pogingen. De eerste letter krijg je.","Guess the word in five tries. You get the first letter.")},
    {v:"clas",    id:"ftClas",    e:"\\u26a1",              t:"Clasificador",       s:ct("Links of rechts, en het gaat steeds sneller","Left or right, and it keeps speeding up")},
    {v:"mem",     id:"ftMem",     e:"\\ud83c\\udccf",        t:"Memory \\u00b7 Parejas", s:fx("meS")},
    {v:"duel",    id:"ftDuel",    e:"\\u2694\\ufe0f",        t:"Palabra Duel",       s:fx("duS")}
  ];'''

A_RIJ = '''      nuHtml += "<div class='lesson' id='"+g.id+"'>"+kop+g.s+"</span></div><div class='lstatus'>\\u25b6</div></div>";'''

A_CSS = '''  .speelknop:hover{border-color:var(--accent); background:var(--accent-soft);}'''

A_NAAR = '''function speelNaar(v){
  funView = v;
  if(v === "dictado"){ dIdx = null; dRonde = null; }'''

if DOE_APP:
    ontbreekt = [a for a in [A_LIJST, A_KEUZE, A_LEUK, A_SPEELHTML, A_MENU, A_RIJ, A_CSS, A_NAAR] if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:100].replace("\n", " / ") for a in ontbreekt) +
              "\n\nEerst bijtrekken:\n\n    git pull --rebase\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. één lijst voor alle spellen ----------
    rep(A_LIJST, '''/* ================= DE SPELLEN, OP ÉÉN PLEK (v23.65) =================
   Hier stond een lijst van negen met een emoji en een naam, en op het speeltuinscherm een lijst van
   negen met een emoji, een naam én een regel uitleg. Overlappend maar niet gelijk, en de dagkaart
   miste juist de regel die zegt wat een spel is.

   Stefan: "niet duidelijk wat een spelen is, wat gebeurt er als ik daar klik, waarom zou ik dat
   doen ik snap het concept nog niet." De uitleg bestond al, hij stond alleen op het andere scherm.

   Eén lijst dus, en beide schermen lezen eruit. De naam is die van het scherm waar je op landt:
   meestal Spaans, bij de woordenzoeker niet, want die heet daar Woordenzoeker.

   Het is een functie en geen var, omdat fx() en ct() de taal van het profiel nodig hebben en dat
   profiel er bij het inladen van het script nog niet is. */
function spelInfo(){
  return [
    {v:"avt",     id:"ftAvt",     e:"\\ud83d\\uddfa\\ufe0f",     t:"Aventura",              s:fx("avS")},
    {v:"musica",  id:"ftMusica",  e:"\\ud83c\\udfb5",            t:"M\\u00fasica",            s:fx("muS")},
    {v:"ws",      id:"ftWs",      e:"\\ud83d\\udd0d",            t:fx("wsT"),               s:fx("wsS")},
    {v:"kruis",   id:"ftKruis",   e:"\\u270f\\ufe0f",            t:"Crucigrama",            s:fx("krS")},
    {v:"letras",  id:"ftLetras",  e:"\\ud83d\\udd24",            t:"Letras",                s:ct("Zeven letters, hoeveel woorden haal je eruit? Geen klok.","Seven letters, how many words can you find? No clock.")},
    {v:"adiv",    id:"ftAdiv",    e:"\\ud83d\\udfe9",            t:"Adivina",               s:ct("Raad het woord in vijf pogingen. De eerste letter krijg je.","Guess the word in five tries. You get the first letter.")},
    {v:"clas",    id:"ftClas",    e:"\\u26a1",                  t:"Clasificador",          s:ct("Links of rechts, en het gaat steeds sneller.","Left or right, and it keeps speeding up.")},
    {v:"mem",     id:"ftMem",     e:"\\ud83c\\udccf",            t:"Memory \\u00b7 Parejas",  s:fx("meS")},
    {v:"duel",    id:"ftDuel",    e:"\\u2694\\ufe0f",            t:"Palabra Duel",          s:fx("duS")}
  ];
}
function spelInfoVan(v){
  var L = spelInfo(), i;
  for(i = 0; i < L.length; i++){ if(L[i].v === v) return L[i]; }
  return null;
}
/* De regels komen uit twee generaties tekst: sommige beginnen met een kleine letter en missen een
   punt ("puzzel met jouw geleerde woorden"), andere zijn hele zinnen. Onder elkaar in een lijst
   valt dat meteen op. Repareren bij het tonen en niet in de teksten zelf, want die staan ook in de
   vertaaltabel en daar zijn ze fragmenten. */
function spelZin(s){
  s = String(s || "").trim();
  if(!s) return "";
  s = s.charAt(0).toUpperCase() + s.slice(1);
  if(!/[.!?]$/.test(s)) s += ".";
  return s;
}
/* Aventura staat vast op de dagkaart (dat is het grote spel) en Palabra Duel heeft een tweede
   speler nodig. De rest wisselt per dag, Música inbegrepen: die heeft geen materiaal nodig en is
   daarmee op dag 1 het enige wat naast Aventura echt kan draaien. */
var DAGSPEL_UIT = {avt:1, duel:1};
/* v23.65, en dit was een echte fout. In DAGSPELLEN stonden Escuchar, El Corrector en Rompecabezas,
   dus de kaart met de kop "Even spelen" bood drie oefeningen aan. De regel van v21.5 is in één zin
   te zeggen (Stefan: "lessen, dat zijn de oefeningen, die zitten nu ook onder speeltuin"): onder
   Oefenen telt het mee voor je niveau, onder Spelen niet. De speeltuin hield zich daaraan, de
   dagkaart niet. Het eindscherm van de les wist het trouwens al wel: lesFlowWinst() biedt El
   Corrector aan als "hier win je het meeste" en lesFlowLeuk() een spel als "of gewoon leuk". */
function dagSpellen(){
  return spelInfo().filter(function(x){ return !DAGSPEL_UIT[x.v]; });
}''')

    # ---------- 2. de rotatie leest uit dezelfde lijst, en telt zelf niet meer tot drie ----------
    rep(A_KEUZE, '''/* v23.65: het aantal is een parameter geworden. De dagkaart toont sinds deze versie regels met
   een zin erbij in plaats van tegels, en dan zijn drie voorstellen naast Aventura te veel scherm.
   Het eindscherm van de les (lesFlowLeuk) vraagt er nog steeds gewoon één. */
function dagSpelKeuze(n){
  var doel = n || 3;
  // v19.92: alleen spellen aanbieden die vandaag ook echt iets kunnen tonen. Een knop op je
  // dagscherm die uitkomt op "leer eerst wat meer woordjes" is een knop die je leert dat de
  // knoppen hier niet betrouwbaar zijn.
  var alles = dagSpellen();
  var kan = alles.filter(function(x){
    try { return speelKlaar(x.v); } catch(e){ return true; }
  });
  /* v23.65: hier stond "if(!kan.length) kan = alles;". Dat sprak de regel erboven tegen: als niets
     kon, bood de kaart alsnog iets aan dat niet kan. Het viel niet op omdat Rompecabezas geen
     materiaal-eis heeft en dus altijd meetelde; nu dat een oefening is en geen spel, staat de
     dagrotatie op dag 1 leeg en werd de noodgreep zichtbaar. Niets aanbieden is het eerlijke
     antwoord: dagSpeelHtml() zet er dan "nog N spellen komen erbij" onder, en lesFlowLeuk() slaat
     zijn voorstel over. */
  var h = dayHash("spel");
  var uit = [];
  // De stap van 2 geeft de afwisseling per dag zolang de lijst lang genoeg is; de tweede ronde
  // met stap 1 vult aan als die stap in zichzelf terugvalt. Zonder die tweede ronde stond er op
  // dag 1 twee keer hetzelfde spel, en ontbrak het spel dat wel kon.
  for(var i = 0; i < kan.length && uit.length < doel; i++){
    var k1 = kan[(h + i * 2) % kan.length];
    if(uit.indexOf(k1) === -1) uit.push(k1);
  }
  for(var j = 0; j < kan.length && uit.length < doel; j++){
    var k2 = kan[(h + j) % kan.length];
    if(uit.indexOf(k2) === -1) uit.push(k2);
  }
  return uit;
}''')

    # ---------- 2b. het eindscherm las een veld dat niet meer bestaat ----------
    rep(A_LEUK, '''  var k = keus[0];
  /* v23.65: hier stond k.n. De spellijst heette DAGSPELLEN en had een veld n; spelInfo() noemt dat
     veld t, want zo heet het in de speeltuin ook. Zonder deze regel stond er "undefined" als kop
     boven het spelvoorstel op het eindscherm van je les. */
  return {icon:k.e, kop:k.t,''')

    # ---------- 3. de dagkaart zegt wat een spel is ----------
    rep(A_SPEELHTML, '''/* v23.65: van tegels naar regels. Een tegel heeft plek voor een emoji en een naam, en Stefan wist
   bij "Sopa de letras" niet wat hij zou krijgen. De regel die dat uitlegt stond al op het
   speeltuinscherm; nu staat hij hier ook, uit dezelfde bron. */
function dagSpeelRij(g){
  if(!g) return "";
  return "<button class='speelrij' data-speel='"+g.v+"'>"+
      "<span class='spe'>"+g.e+"</span>"+
      "<span class='sprij'><b>"+g.t+"</b><span class='muted'>"+spelZin(g.s)+"</span></span>"+
      "<span class='sppijl'>\\u25b6</span></button>";
}
function dagSpeelHtml(){
  var keus = dagSpelKeuze(2);
  var knoppen = dagSpeelRij(spelInfoVan("avt"));
  keus.forEach(function(k){ knoppen += dagSpeelRij(k); });
  /* v23.65. Stefan: "waarom heb ik die unlocked? dan wil ik toch alle spellen zien maar met eentje
     die niet locked is." Het antwoord stond op het volgende scherm en niet hier: daar staan de
     dichte spellen grijs onder de open, met de eis erbij (v19.92). Alleen wist je op deze kaart
     niet dat dat scherm bestond, en waarom deze er stonden en andere niet. */
  var dicht = 0;
  try {
    dicht = dagSpellen().filter(function(x){ return !speelKlaar(x.v); }).length;
  } catch(e){ dicht = 0; }
  return "<div class='card' id='speelKaart'><span class='kicker'>"+ct("Even spelen","Play something")+"</span>"+
    "<div class='speellijst'>"+knoppen+"</div>"+
    (dicht > 0
      ? "<p class='muted' style='margin:8px 0 0; font-size:.85rem'>"+
          ct("Nog "+dicht+" "+(dicht === 1 ? "spel komt" : "spellen komen")+" erbij als je meer woorden kent.",
             "Another "+dicht+" "+(dicht === 1 ? "game joins" : "games join")+" in once you know more words.")+"</p>"
      : "")+
    "<div class='row' style='margin-top:8px'><button class='ghost' id='btnAlleSpellen'>"+ct("Alle spelletjes","All the games")+" \\u2192</button></div></div>";
}''')

    # ---------- 4. de speeltuin toont ze allemaal ----------
    rep(A_MENU, '''  /* v23.65: uit spelInfo(), zodat dit scherm en de dagkaart niet meer uit elkaar kunnen lopen.
     De inhoud van deze lijst verandert niet: precies dezelfde negen spellen als hiervoor. Wat
     verandert is dat de dagkaart nu uit dezelfde bron leest, en dat de oefeningen daar weg zijn. */
  var SPEELMENU = spelInfo();''')

    # ---------- 4b. en daar staat de regel er ook netjes ----------
    rep(A_RIJ, '''      nuHtml += "<div class='lesson' id='"+g.id+"'>"+kop+spelZin(g.s)+"</span></div><div class='lstatus'>\\u25b6</div></div>";''')

    # ---------- 5. Música is een eigen tabblad, geen speeltuinweergave ----------
    rep(A_NAAR, '''function speelNaar(v){
  funView = v;
  /* v23.65: Música staat sinds deze versie ook in de dagrotatie (op dag 1 is het naast Aventura het
     enige dat echt kan draaien). Maar het is geen speeltuinweergave: het heeft een eigen tabblad,
     en renderFun() kent geen tak voor "musica". Zonder deze regel landde je op het speeltuinmenu.
     De speeltuin zelf deed dit al goed, met show("musica") in zijn eigen draadje. */
  if(v === "musica"){ show("musica"); return; }
  if(v === "dictado"){ dIdx = null; dRonde = null; }''')

    # ---------- 6. de regels hebben een vorm nodig ----------
    rep(A_CSS, '''  .speelknop:hover{border-color:var(--accent); background:var(--accent-soft);}
  /* v23.65: de dagkaart toont regels in plaats van tegels, want een tegel heeft geen plek voor de
     zin die zegt wat je gaat doen. Zelfde vorm als de lesregels, zodat je hem herkent. */
  .speellijst{display:flex; flex-direction:column; gap:8px; margin-top:10px;}
  .speelrij{display:flex; align-items:center; gap:12px; width:100%; text-align:left; padding:10px 12px;
            border-radius:var(--radius); border:1.5px solid var(--border); background:var(--card);
            color:var(--ink); cursor:pointer;}
  .speelrij .spe{flex:0 0 auto; font-size:1.35rem; line-height:1;}
  .speelrij .sprij{flex:1; min-width:0;}
  .speelrij .sprij b{display:block; font-size:.98rem;}
  .speelrij .sprij span{display:block; font-size:.82rem; color:var(--muted); font-weight:400;}
  .speelrij .sppijl{flex:0 0 auto; color:var(--muted); font-size:.8rem;}
  .speelrij:hover{border-color:var(--accent); background:var(--accent-soft);}''')

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
