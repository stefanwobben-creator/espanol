#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.149: eerst luisteren, dan pas meezingen.

Stefan, 20 aug: "Als het uitdrukkingen zijn niet meer dan 5 woorden dan kan het. Maar hoe ga je me
helpen met het liedje. Alleen het refrein. Meezingen of eerst alleen luisteren?"

## Het antwoord op zijn vraag

**Eerst luisteren, dan pas meezingen.** Meezingen met woorden die je niet begrijpt is een
uitspraakoefening, geen taaloefening: je maakt klanken na zonder dat er betekenis aan hangt, en dan
blijft er niets van staan. Andersom werkt wel: als je weet wat er staat, is meezingen het moment
waarop een uitdrukking van "gelezen" naar "in je mond" gaat.

**En niet het hele lied, maar de stukjes.** Niet omdat het refrein bijzonder is, maar omdat de
brokjes zijn wat je meeneemt. Een lied van drie minuten is te veel om te onthouden; zeven
uitdrukkingen van hoogstens vijf woorden zijn precies genoeg. Dat is ook waarom de app geen songtekst
laat zien: het gaat niet om de tekst, het gaat om de brokjes, en die staan er al.

## Wat het blok wordt

Drie stappen in plaats van één pagina met alles erop.

**1. Luisteren.** De video, en drie keer de vraag "welke van deze drie hoor je?" met twee
uitdrukkingen uit een ánder lied ertussen. Alleen Spaans, geen vertaling. Dat maakt van de eerste
luisterbeurt een opdracht in plaats van achtergrondmuziek, en het is te doen: je hoeft niet te
begrijpen wat er staat, je hoeft alleen te horen wat er staat.

Waarom afleiders uit andere liedjes en niet verzonnen: ze zijn even echt, even lang en even moeilijk,
dus de vraag gaat over wat je hoort en niet over welke er het gekst uitziet.

**2. De woorden erbij.** Nu pas de oogst met de uitleg. Je hebt de klanken al gehoord, dus je plakt
betekenis op iets wat er al zit; dat is een andere volgorde dan lezen-en-dan-horen en hij is beter.

**3. Meezingen.** Nog een keer luisteren, met de zeven uitdrukkingen ernaast, en de opdracht om die
mee te zingen als ze langskomen. Daarna de vragen die er al waren, en dan gaan ze naar je woorden.

## De grens van vijf woorden

Stefan: "Als het uitdrukkingen zijn niet meer dan 5 woorden dan kan het."

Gemeten over alle 92: 28 van één woord, 43 van twee, 12 van drie, 6 van vier, 3 van vijf. Nul erboven.
De grens verandert vandaag dus niets, en dat is precies waarom hij nu goedkoop in te bouwen is: als
regel, niet als opruimactie. Wat er straks bij komt kan hem niet meer overschrijden.

Bewaakt door test/suites/pw-liedstappen.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.149"

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


# ================= 1. de grens van vijf woorden =================

rep(
    '''function musOogstDoel(o){
  if(!o || !o.es || !o.nl) return null;
  var plat = musPlat(o.es);
  if(!plat) return null;
  return {id:mijnWoordId(plat), eigen:true, plat:plat, es:o.es, nl:o.nl};
}''',
    '''/* v23.149, Stefan: "als het uitdrukkingen zijn niet meer dan 5 woorden dan kan het."

   Gemeten over alle 92 oogstregels: 28 van één woord, 43 van twee, 12 van drie, 6 van vier, 3 van
   vijf, nul erboven. Deze grens verandert vandaag dus niets. Hij staat er als regel voor wat er nog
   bij komt, en niet als opruimactie.

   Waarom vijf: langer dan dat is geen brokje meer maar een zin, en een zin op een kaartje vraagt
   iets anders van je dan een uitdrukking. Zinnen maken doe je in het schrijfblok. */
var MUS_MAX_WOORDEN = 5;
function musTeLang(es){
  return musPlat(es).split(" ").filter(Boolean).length > MUS_MAX_WOORDEN;
}
function musOogstDoel(o){
  if(!o || !o.es || !o.nl) return null;
  if(musTeLang(o.es)) return null;
  var plat = musPlat(o.es);
  if(!plat) return null;
  return {id:mijnWoordId(plat), eigen:true, plat:plat, es:o.es, nl:o.nl};
}''',
)

# ================= 2. de drie stappen =================

rep(
    '''function songWoordenLijst(){''',
    '''/* ================= HET LIEDBLOK IN DRIE STAPPEN (v23.149) =================

   Stefan: "hoe ga je me helpen met het liedje. Alleen het refrein. Meezingen of eerst alleen
   luisteren?"

   Eerst luisteren, dan pas meezingen. Meezingen met woorden die je niet begrijpt is een
   uitspraakoefening en geen taaloefening: je maakt klanken na zonder betekenis, en er blijft niets
   van staan. Andersom werkt wel.

   En niet het hele lied maar de brokjes, want die neem je mee. Daarom staat er ook geen songtekst
   in de app: het gaat om de zeven uitdrukkingen, en die stonden er al.

     stap 1  luisteren     video + drie keer "welke van deze drie hoor je?", alleen Spaans
     stap 2  de woorden    de oogst met de uitleg erbij
     stap 3  meezingen     nog een keer, met de brokjes ernaast, en dan de vragen

   De afleiders komen uit andere liedjes en zijn niet verzonnen: even echt, even lang, even moeilijk.
   Dan gaat de vraag over wat je hoort en niet over welke er het gekst uitziet. */
var MUS_HOOR_N = 3;        // hoeveel keer "welke hoor je?"
var MUS_HOOR_OPTIES = 3;   // hoeveel keuzes per vraag
var musStap = 1;
var musHoorI = 0, musHoorGoed = 0;

function musHoorRij(sg){
  if(!sg || !sg.oogst) return [];
  /* Vast per lied en niet per klik: wie halverwege terugbladert hoort niet ineens andere brokjes.
     Alleen brokjes van twee woorden of meer, want één woord is in een lied niet te horen als keuze. */
  var eigen = sg.oogst.filter(function(o){ return musPlat(o.es).split(" ").filter(Boolean).length >= 2; });
  if(eigen.length < 2) eigen = sg.oogst.slice();
  var vreemd = [];
  musLijst().forEach(function(ander){
    if(ander.id === sg.id) return;
    (ander.oogst || []).forEach(function(o){
      if(musPlat(o.es).split(" ").filter(Boolean).length < 2) return;
      vreemd.push(o.es);
    });
  });
  var rij = [], i, j, h;
  for(i = 0; i < Math.min(MUS_HOOR_N, eigen.length); i++){
    h = dayHash(sg.id + "-hoor-" + i);
    var goed = eigen[(h + i) % eigen.length].es;
    var opties = [goed];
    for(j = 0; j < MUS_HOOR_OPTIES - 1 && vreemd.length; j++){
      var kand = vreemd[(h + j * 7 + i * 13) % vreemd.length];
      if(opties.indexOf(kand) === -1) opties.push(kand);
    }
    // door elkaar, maar wel vast: dezelfde vraag geeft dezelfde volgorde
    opties.sort(function(a, b){ return ((h + a.length) % 7) - ((h + b.length) % 7); });
    rij.push({goed:goed, opties:opties});
  }
  return rij;
}

function musStapKop(sg){
  var namen = [ct("Luisteren","Listen"), ct("De woorden erbij","The words"), ct("Meezingen","Sing along")];
  var h = "<div class='card'><span class='kicker'>"+
    ct("Stap ","Step ")+musStap+"/3 \\u00b7 "+namen[musStap - 1]+"</span>";
  if(musStap === 1){
    h += "<p style='margin:4px 0'>"+ct("Luister eerst. Je hoeft nog niet te snappen wat er staat: je hoeft alleen te horen wat er staat.",
                                       "Listen first. You don't have to understand yet: you only have to hear what is there.")+"</p>";
  } else if(musStap === 2){
    h += "<p style='margin:4px 0'>"+ct("Deze uitdrukkingen kwamen net langs. Nu de betekenis erbij.",
                                       "These phrases just went past. Now the meaning.")+"</p>";
  } else {
    h += "<p style='margin:4px 0'>"+ct("Nu weet je wat er staat. Zet hem nog een keer aan en zing deze stukjes mee als ze langskomen. Hard mag.",
                                       "Now you know what it says. Play it once more and sing these bits along when they come by. Loudly is fine.")+"</p>";
  }
  return h + "</div>";
}

function musHoorHtml(sg){
  var rij = musHoorRij(sg);
  if(!rij.length) return "<div class='card'><div class='row'><button class='primary' id='btnMusStap2'>"+
    ct("Verder \\u2192","Continue \\u2192")+"</button></div></div>";
  if(musHoorI >= rij.length){
    return "<div class='card'><div class='feedback "+(musHoorGoed === rij.length ? "ok" : "bijna")+"'>"+
      musHoorGoed+"/"+rij.length+" "+ct("gehoord","heard")+"</div>"+
      "<div class='row' style='margin-top:8px'><button class='primary' id='btnMusStap2'>"+
        ct("Wat betekenen ze? \\u2192","What do they mean? \\u2192")+"</button></div></div>";
  }
  var v = rij[musHoorI];
  var h = "<div class='card'><p><b>"+(musHoorI + 1)+"/"+rij.length+" \\u00b7 "+
    ct("Welke van deze drie hoor je in het lied?","Which of these three do you hear in the song?")+"</b></p>";
  v.opties.forEach(function(o, i){ h += "<button class='opt es' data-hoor='"+i+"'>"+o+"</button>"; });
  return h + "<div id='musHoorFb'></div></div>";
}

function musHoorWire(sg){
  var rij = musHoorRij(sg);
  var v = rij[musHoorI];
  var wrap = document.getElementById("songView");
  if(!wrap) return;
  var door = document.getElementById("btnMusStap2");
  if(door) door.onclick = function(){ musStap = 2; openSong(sg, true); };
  if(!v) return;
  wrap.querySelectorAll("[data-hoor]").forEach(function(b){
    b.onclick = function(){
      var gekozen = v.opties[+b.getAttribute("data-hoor")];
      var goed = gekozen === v.goed;
      wrap.querySelectorAll("[data-hoor]").forEach(function(x){
        if(v.opties[+x.getAttribute("data-hoor")] === v.goed) x.classList.add("correct");
      });
      if(!goed) b.classList.add("wrong");
      if(goed) musHoorGoed++;
      addXP(goed ? 2 : 1);
      document.getElementById("musHoorFb").innerHTML =
        "<div class='row' style='margin-top:8px'><button class='primary' id='btnMusHoorNext'>"+
          ct("Volgende \\u2192","Next \\u2192")+"</button></div>";
      document.getElementById("btnMusHoorNext").onclick = function(){
        musHoorI++; openSong(sg, true);
      };
    };
  });
}

function songWoordenLijst(){''',
)

# ================= 3. openSong gebruikt de stappen =================

rep(
    '''  if(!skipPush) navPush({t:"song", id:sg.id});
  document.getElementById("songList").classList.add("hidden");''',
    '''  if(!skipPush){
    navPush({t:"song", id:sg.id});
    musStap = 1; musHoorI = 0; musHoorGoed = 0;   // v23.149: een verse opening begint bij luisteren
  }
  document.getElementById("songList").classList.add("hidden");''',
)

rep(
    '''    "<p>"+(sg.intro||"")+"</p>"+
    "<p class='muted'>Tip: zet ondertiteling (CC) aan in de speler en zing gewoon mee, fouten maken mag hard.</p></div>";''',
    '''    /* v23.149: de intro staat in stap 2 en niet in stap 1. Hij is Nederlands en vertelt waar het
       lied over gaat, en in stap 1 is de vraag juist wat je hoort zonder dat je het al weet. */
    (musStap === 2 ? "<p>"+(sg.intro||"")+"</p>" : "")+
    "<p class='muted'>"+ct("Tip: zet ondertiteling (CC) aan in de speler.",
                           "Tip: turn on subtitles (CC) in the player.")+"</p></div>"+
    musStapKop(sg);   /* v23.149 */''',
)

rep(
    '''  if(sg.oogst && sg.oogst.length){
    html += "<div class='card'><h2>De taaloogst 🌾</h2>";
    sg.oogst.forEach(function(o){
      html += "<div class='oogst'><b>"+o.es+"</b> · "+o.nl+"<span class='muted'>"+o.u+"</span></div>";
    });
    /* v23.148: de knop is er voor wie de quiz overslaat. Wie hem afmaakt krijgt hetzelfde
       automatisch; het is dezelfde functie. */
    html += musOogstRegelHtml(sg) + "</div>";
  }
  if(sg.vragen && sg.vragen.length){
    html += "<div class='card'><h2>Snap je het lied?</h2><div id='songQuiz'></div></div>";
  }''',
    '''  /* v23.149: stap 1 is luisteren, en dan hoort de oogst er nog niet te staan. De hele vraag "welke
     van deze drie hoor je" is weg als de goede er in het Nederlands naast staat. */
  if(musStap === 1){
    html += musHoorHtml(sg);
  }
  if(musStap >= 2 && sg.oogst && sg.oogst.length){
    html += "<div class='card'><h2>De taaloogst 🌾</h2>";
    sg.oogst.forEach(function(o){
      html += "<div class='oogst'><b>"+o.es+"</b> · "+o.nl+
        (musStap === 2 ? "<span class='muted'>"+o.u+"</span>" : "")+"</div>";
    });
    if(musStap === 2){
      html += "<div class='row' style='margin-top:10px'><button class='primary' id='btnMusStap3'>"+
        ct("Nu meezingen \\u2192","Now sing along \\u2192")+"</button></div>";
    }
    /* v23.148: de knop is er voor wie de quiz overslaat. Wie hem afmaakt krijgt hetzelfde
       automatisch; het is dezelfde functie. In stap 3, want daarvoor heb je ze nog niet gehad. */
    if(musStap >= 3) html += musOogstRegelHtml(sg);
    html += "</div>";
  }
  if(musStap >= 3 && sg.vragen && sg.vragen.length){
    html += "<div class='card'><h2>Snap je het lied?</h2><div id='songQuiz'></div></div>";
  }''',
)

rep(
    '''  el.innerHTML = html;
  musOogstWire(sg);   // v23.148''',
    '''  el.innerHTML = html;
  /* v23.149 */
  if(musStap === 1) musHoorWire(sg);
  var b3 = document.getElementById("btnMusStap3");
  if(b3) b3.onclick = function(){ musStap = 3; openSong(sg, true); };
  musOogstWire(sg);   // v23.148''',
)

# de quiz start alleen als hij er staat
rep(
    '''  if(sg.vragen && sg.vragen.length) renderSongQuiz(sg, 0, 0);''',
    '''  if(musStap >= 3 && sg.vragen && sg.vragen.length) renderSongQuiz(sg, 0, 0);''',
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
