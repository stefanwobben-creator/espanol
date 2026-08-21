#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.148: het liedje van vandaag, en het laat iets achter.

Stefan, 20 aug: "Okay música mag blijven maar dan moet er automatisch een liedje van de dag of om de
x dagen komen. En de leeroutput moet ook hoger."

## Wat er nu gebeurt als je een lied doet

Je kijkt de video, je leest 6,6 uitgelegde uitdrukkingen ("te bloqueé · ik blokkeerde je · indefinido
van bloquear, mét de -qué spellingregel die je kent van practiqué"), je beantwoordt drie vragen, en
dan is het over. Van die 92 uitdrukkingen in veertien liedjes komt er geen enkele ooit terug. Ze zijn
alleen opzoekbaar in het woordenboek.

Dat is de leeropbrengst: nul, op het moment na. Een liedje is 4 minuten kijken plus 3 minuten lezen,
en er blijft niets van staan omdat de machine niet weet dat je het gezien hebt.

## Twee dingen, en het tweede is het belangrijkste

**1. Het liedje van vandaag.** Música wordt de derde optie van het inputblok (v23.140), naast lezen
en luisteren. Niet elke dag: een lied kost meer tijd dan een stukje hoofdstuk, dus eens per drie
actieve dagen. Welk lied is niet willekeurig per klik maar vast per dag, en het gaat eerst langs de
liedjes die je nog nooit hebt afgemaakt.

Op de Música-pagina staat hij ook bovenaan, met dezelfde keuze, zodat "het liedje van vandaag"
overal hetzelfde lied is.

**2. De oogst gaat naar je woorden.** De uitdrukkingen worden echte kaartjes in je stapel, via
precies dezelfde machinerie die v23.133 voor opgezochte leeswoorden bouwde (S.mijn plus een rij in
WORDS). Klaar met de quiz betekent: ze staan erin, en morgen zie je ze terug.

Waarom automatisch en niet met een knop per uitdrukking: bij het lezen is opzoeken een handeling die
je zelf doet en die dus iets zegt (v23.133). Bij een lied heb je de uitdrukking niet opgezocht, hij
is jou aangereikt, en dan is een knop per regel zeven keer dezelfde vraag stellen. De knop staat er
wel, voor wie de quiz overslaat.

Zeven uitdrukkingen per lied, eens per drie dagen, is ruim twee kaartjes per dag erbij. Dat past
naast de dagportie zonder hem om te gooien.

## En een gat uit v23.140

Escuchar heeft twee plekken die kijken of jij in het luisterblok van je les zit, en allebei stonden
ze nog op `stap === "produceren"`. Sinds v23.140 heet die stap "input". Gevolg: koos de app
luisteren, dan kreeg je na afloop geen "Door →" en stond je stil in de speeltuin. Dat is precies het
soort doodlopende weg waar v20.5 op is teruggedraaid.

Bewaakt door test/suites/pw-liedvandaag.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.148"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = NIEUW not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()


def _num(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


DOE_VER = _num(huidig_ver) < _num(NIEUW)

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    if not DOE_APP:
        return
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:220])
    src = src.replace(anker, nieuw, n)


# ================= 1. welk lied is dat van vandaag, en wat laat het achter =================

rep(
    '''function songWoordenLijst(){''',
    '''/* ================= HET LIEDJE VAN VANDAAG (v23.148) =================

   Stefan: "musica mag blijven maar dan moet er automatisch een liedje van de dag of om de x dagen
   komen. En de leeroutput moet ook hoger."

   Waarom eens per drie dagen en niet elke dag: een lied is vier minuten video plus de oogst lezen
   plus drie vragen. Dat is ruim twee keer een stukje hoofdstuk. Elke dag zou het inputblok laten
   uitdijen en de andere twee draden verdringen.

   Waarom vast per dag en niet willekeurig per klik: anders is "het liedje van vandaag" een ander
   lied als je twee keer kijkt, en dan betekent de naam niets. dagenTotaal() telt jouw actieve dagen,
   dus de teller loopt op jouw tempo en niet op de kalender. */
var MUS_OM_DE = 3;

function musLijst(){
  if(typeof SONGS === "undefined") return [];
  return SONGS.filter(function(sg){
    if(S.songHide && S.songHide[sg.id]) return false;
    return !!(sg.oogst && sg.oogst.length);
  });
}
function musGedaan(sg){ return !!(sg && S.musKlaar && S.musKlaar[sg.id]); }
/* Eerst de liedjes die je nog nooit hebt afgemaakt, en pas als die op zijn de rest. Binnen elke
   groep beslist de dag, niet het toeval. */
function musVanDag(){
  var alles = musLijst();
  if(!alles.length) return null;
  var vers = alles.filter(function(sg){ return !musGedaan(sg); });
  var pot = vers.length ? vers : alles;
  return pot[dayHash("musica") % pot.length];
}
/* Is het inputblok van vandaag een lied? Alleen als er nog liedjes zijn en de teller op nul staat.
   Dag 0 telt niet mee: op dag een is het dagscherm het eerste wat een vreemde ziet (v23.135). */
function musDagBeurt(){
  if(!musVanDag()) return false;
  var d = dagenTotaal();
  return d > 1 && (d % MUS_OM_DE) === 0;
}

/* Wat het achterlaat. Dezelfde machinerie als v23.133 voor opgezochte leeswoorden: een eigen rij in
   S.mijn, een rij in WORDS zodat de kaartjes ergens uit kunnen putten, en een doosje 0 in de SRS.

   Het verschil met v23.133 zit in het waarom, niet in de code: daar zocht je het woord zelf op, en
   dat opzoeken is het bewijs dat je het wilde weten. Hier krijg je de uitdrukking aangereikt, en dan
   is zeven keer vragen "wil je deze onthouden?" zeven keer dezelfde vraag. Dus gaan ze in één keer,
   en staat er daarna wat er gebeurd is. */
function musPlat(es){
  return stripAcc(String(es || "").toLowerCase()).replace(/[^a-z ]/g, "").replace(/\\s+/g, " ").trim();
}
function musOogstDoel(o){
  if(!o || !o.es || !o.nl) return null;
  var plat = musPlat(o.es);
  if(!plat) return null;
  return {id:mijnWoordId(plat), eigen:true, plat:plat, es:o.es, nl:o.nl};
}
function musOogstOpen(sg){
  if(!sg || !sg.oogst) return [];
  return sg.oogst.map(musOogstDoel).filter(function(d){ return d && !mijnHeeft(d); });
}
function musOogstBij(sg){
  var open = musOogstOpen(sg), n = 0;
  open.forEach(function(d){ if(mijnBij(d)) n++; });
  if(sg && sg.id){
    S.musKlaar = S.musKlaar || {};
    S.musKlaar[sg.id] = today();
    try { persist(); } catch(e){}
  }
  return n;
}
/* Zeg wat er gebeurt, niet hoe de machine heet (v23.139). Geen doosjes, geen SRS, geen "kaartjes":
   je ziet ze terug, en wanneer. */
function musOogstRegelHtml(sg){
  var open = musOogstOpen(sg).length;
  var totaal = (sg && sg.oogst && sg.oogst.length) || 0;
  if(!totaal) return "";
  if(!open){
    return "<p class='muted' style='margin:8px 0 0'>"+
      ct("Deze "+totaal+" uitdrukkingen staan al bij je woorden.",
         "These "+totaal+" phrases are already in your words.")+"</p>";
  }
  return "<p class='muted' style='margin:8px 0 0'>"+
      ct(open+" van deze uitdrukkingen "+(open === 1 ? "kun" : "kun")+" je bij je woorden zetten. Dan komen ze de komende dagen terug.",
         "You can add "+open+" of these phrases to your words. Then they come back over the next days.")+"</p>"+
    "<div class='row' style='margin-top:6px'><button class='ghost' id='btnMusOogst'>"+
      ct("Bij mijn woorden","Add to my words")+"</button></div><div id='musOogstFb'></div>";
}
function musOogstWire(sg){
  var b = document.getElementById("btnMusOogst");
  if(!b) return;
  b.onclick = function(){
    var n = musOogstBij(sg);
    var fb = document.getElementById("musOogstFb");
    if(fb) fb.innerHTML = "<div class='feedback ok'>"+musOogstGedaanTxt(n)+"</div>";
    b.disabled = true;
  };
}
function musOogstGedaanTxt(n){
  if(!n) return ct("Die stonden er al in.","Those were already in there.");
  return ct(n+" "+(n === 1 ? "uitdrukking staat" : "uitdrukkingen staan")+" nu bij je woorden. Morgen zie je "+
              (n === 1 ? "hem" : "ze")+" terug.",
            n+" "+(n === 1 ? "phrase is" : "phrases are")+" now in your words. You'll see "+
              (n === 1 ? "it" : "them")+" again tomorrow.");
}

function songWoordenLijst(){''',
)

# ================= 2. de quiz sluit af met de oogst, en fouten tellen mee =================

rep(
    '''  if(i >= sg.vragen.length){
    if(score === sg.vragen.length){ confetti(["🎵","🎉","⭐️"], 16); }
    el.innerHTML = "<p class='big'>"+score+"/"+sg.vragen.length+"</p><p class='muted'>"+(score===sg.vragen.length?ct("¡Perfecto! Je luistert als een local. (+"+xpw()+")","¡Perfecto! You listen like a local. (+"+xpw()+")"):ct("Kijk de taaloogst nog eens en luister opnieuw.","Look at the word harvest again and listen once more."))+"</p>";
    return;
  }''',
    '''  if(i >= sg.vragen.length){
    if(score === sg.vragen.length){ confetti(["🎵","🎉","⭐️"], 16); }
    /* v23.148: hier hield het op. Je had een lied gekeken, zeven uitgelegde uitdrukkingen gelezen en
       drie vragen beantwoord, en er bleef niets van staan omdat de machine niet wist dat je het
       gezien had. Nu gaan de uitdrukkingen naar je woorden, en zie je ze de komende dagen terug. */
    var geoogst = 0;
    try { geoogst = musOogstBij(sg); } catch(e){ geoogst = 0; }
    el.innerHTML = "<p class='big'>"+score+"/"+sg.vragen.length+"</p><p class='muted'>"+(score===sg.vragen.length?ct("¡Perfecto! Je luistert als een local. (+"+xpw()+")","¡Perfecto! You listen like a local. (+"+xpw()+")"):ct("Kijk de taaloogst nog eens en luister opnieuw.","Look at the word harvest again and listen once more."))+"</p>"+
      (geoogst ? "<div class='feedback ok'>"+musOogstGedaanTxt(geoogst)+"</div>" : "")+
      (lesFlow && lesFlow.stap === "input" && lesFlow.gekozenSpel === "musica"
        ? "<div class='row' style='margin-top:8px'><button class='primary' id='btnMusFlowDoor'>"+ct("Door →","Continue →")+"</button></div>"
        : "");
    var door = document.getElementById("btnMusFlowDoor");
    if(door) door.onclick = function(){ lesFlowVolgende(); };
    return;
  }''',
)

rep(
    '''      var goed = +b.getAttribute("data-i") === v.c;
      el.querySelectorAll(".opt")[v.c].classList.add("correct");
      if(!goed) b.classList.add("wrong");
      addXP(goed ? 2 : 1);''',
    '''      var goed = +b.getAttribute("data-i") === v.c;
      el.querySelectorAll(".opt")[v.c].classList.add("correct");
      if(!goed) b.classList.add("wrong");
      /* v23.148: een fout hier verdween. De vragen gaan over de grammatica van het lied (indefinido,
         wederkerend, pronomen achter de infinitief), dus ze horen in dezelfde foutenlijst als de
         rest; El Corrector en de foutenlus putten daaruit. */
      if(!goed){ try { logError(sg.id + "-q" + i, "song", sg.id, vraagTekst(v)); } catch(e){} }
      addXP(goed ? 2 : 1);''',
)

# ================= 3. de oogstkaart krijgt zijn knop =================

rep(
    '''  if(sg.oogst && sg.oogst.length){
    html += "<div class='card'><h2>De taaloogst 🌾</h2>";
    sg.oogst.forEach(function(o){
      html += "<div class='oogst'><b>"+o.es+"</b> · "+o.nl+"<span class='muted'>"+o.u+"</span></div>";
    });
    html += "</div>";
  }''',
    '''  if(sg.oogst && sg.oogst.length){
    html += "<div class='card'><h2>De taaloogst 🌾</h2>";
    sg.oogst.forEach(function(o){
      html += "<div class='oogst'><b>"+o.es+"</b> · "+o.nl+"<span class='muted'>"+o.u+"</span></div>";
    });
    /* v23.148: de knop is er voor wie de quiz overslaat. Wie hem afmaakt krijgt hetzelfde
       automatisch; het is dezelfde functie. */
    html += musOogstRegelHtml(sg) + "</div>";
  }''',
)

rep(
    '''  el.innerHTML = html;
  document.getElementById("btnSongTerug").onclick = renderSongs;''',
    '''  el.innerHTML = html;
  musOogstWire(sg);   // v23.148
  document.getElementById("btnSongTerug").onclick = renderSongs;''',
)

# ================= 4. en bovenaan Música =================

rep(
    '''    "<div class='row'><button class='ghost' id='btnMusTerug'>← "+ct("Speeltuin","Playground")+"</button></div></div>";''',
    '''    "<div class='row'><button class='ghost' id='btnMusTerug'>← "+ct("Speeltuin","Playground")+"</button></div></div>";
  /* v23.148: hetzelfde lied als het inputblok van je les zou kiezen, uit dezelfde functie. Twee
     plekken die allebei "het liedje van vandaag" zeggen en een ander lied bedoelen, is precies de
     tweede waarheid waar deze app het meeste last van heeft gehad. */
  var vandaag = musVanDag();
  if(vandaag){
    html += "<div class='card'><span class='kicker'>"+ct("Het liedje van vandaag","Today's song")+"</span>"+
      "<div class='lesson' data-song='"+vandaag.id+"' style='opacity:1'><div class='lnum'>🎵</div>"+
      "<div class='lbody'><b>"+vandaag.titel+"</b><span>"+vandaag.artiest+" · "+
        (musGedaan(vandaag) ? ct("al gedaan, nog een keer mag","done already, again is fine")
                            : ct((vandaag.oogst||[]).length+" uitdrukkingen om mee te nemen",
                                 (vandaag.oogst||[]).length+" phrases to take with you"))+
      "</span></div><div class='lstatus'>▶</div></div></div>";
  }''',
)

# ================= 5. het inputblok kent een derde optie =================

rep(
    '''function lesFlowInputKeuze(){
  var lezen = null, audi = false;
  try { lezen = lesFlowBoekHoofdstuk(); } catch(e){ lezen = null; }''',
    '''function lesFlowInputKeuze(){
  /* v23.148: eens per drie actieve dagen is het inputblok een lied. Dat gaat vóór de wisseling
     tussen lezen en luisteren, want die twee komen elke andere dag langs en het lied niet. */
  try { if(musDagBeurt()) return "musica"; } catch(e){}
  var lezen = null, audi = false;
  try { lezen = lesFlowBoekHoofdstuk(); } catch(e){ lezen = null; }''',
)

rep(
    '''  if(inputV){
    blokken.push({stap:"input", draad:ct("begrijpen","input"),
      naam: inputV === "lezen" ? ct("Lezen","Reading") : ct("Luisteren","Listening"),
      wat: inputV === "lezen" ? ct("een stukje uit je boek","a piece from your book")
                              : ct("een gesprek","one conversation"),
      sec: doelMinuten() * 60 * 0.25, vaardigheid: inputV});
  }''',
    '''  if(inputV){
    var musDag = inputV === "musica" ? musVanDag() : null;
    blokken.push({stap:"input", draad:ct("begrijpen","input"),
      naam: inputV === "musica" ? ct("Liedje","Song")
          : inputV === "lezen" ? ct("Lezen","Reading") : ct("Luisteren","Listening"),
      wat: inputV === "musica" ? (musDag ? musDag.titel : "M\\u00fasica")
         : inputV === "lezen" ? ct("een stukje uit je boek","a piece from your book")
                              : ct("een gesprek","one conversation"),
      sec: doelMinuten() * 60 * 0.25, vaardigheid: inputV});
  }''',
)

rep(
    '''  if(v === "luisteren"){
    /* v21.4: het luisterblok was dictado, en dat traint transcriberen in plaats van begrijpen.
       Nu gaat het naar Escuchar: een gesprek horen en zeggen waar het over ging. */''',
    '''  if(v === "musica"){
    /* v23.148: het lied van vandaag. Het opent zijn eigen tabblad, net als lezen dat doet, en komt
       terug via de knop onder de quizuitslag. */
    var sgDag = musVanDag();
    if(sgDag){
      lesFlow.gekozenSpel = "musica";
      show("musica");
      openSong(sgDag, true);
      return;
    }
    v = lesFlow.vaardigheid = "luisteren";
  }
  if(v === "luisteren"){
    /* v21.4: het luisterblok was dictado, en dat traint transcriberen in plaats van begrijpen.
       Nu gaat het naar Escuchar: een gesprek horen en zeggen waar het over ging. */''',
)

# ================= 6. het gat uit v23.140: Escuchar kende "input" niet =================

rep(
    '''  if(audMenu && !(lesFlow && lesFlow.stap === "produceren" && lesFlow.gekozenSpel === "audi")){''',
    '''  // v23.148: "input" erbij. Sinds v23.140 heet de stap van het luisterblok zo, en deze twee plekken
  // stonden nog op "produceren". Gevolg: koos de app luisteren, dan kreeg je na afloop geen "Door →"
  // en stond je stil in de speeltuin.
  if(audMenu && !(lesFlow && (lesFlow.stap === "produceren" || lesFlow.stap === "input") && lesFlow.gekozenSpel === "audi")){''',
)

rep(
    '''      (lesFlow && lesFlow.stap === "produceren" && lesFlow.gekozenSpel === "audi"
        ? "<div class='row' style='margin-top:8px'><button class='primary' id='btnAudFlowDoor'>" + ct("Door →","Continue →") + "</button></div>"''',
    '''      (lesFlow && (lesFlow.stap === "produceren" || lesFlow.stap === "input") && lesFlow.gekozenSpel === "audi"
        ? "<div class='row' style='margin-top:8px'><button class='primary' id='btnAudFlowDoor'>" + ct("Door →","Continue →") + "</button></div>"''',
)

# ================= 7. de banner noemt het lied bij naam =================

rep(
    '''  if(f.stap === "input" || f.stap === "produceren"){
    var v = f.vaardigheid;''',
    '''  if(f.stap === "input" && f.vaardigheid === "musica") return ct("Liedje","Song");
  if(f.stap === "input" || f.stap === "produceren"){
    var v = f.vaardigheid;''',
)

# ---------------------------------------------------------------- wegschrijven
if DOE_APP:
    src = re.sub(r'var APP_VERSIE = "[^"]+"', 'var APP_VERSIE = "%s"' % NIEUW, src, count=1)
    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html bijgewerkt naar %s" % NIEUW)

if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt -> %s" % NIEUW)
