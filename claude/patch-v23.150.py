#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.150: praten met Chispa staat in je les.

Stefan, 20 aug: "en ja bouw chat met chispa". En daarvoor al twee keer: "ik kan ook nog niet chatten
met chispa."

## Eerst de diagnose, want die verandert wat er te bouwen valt

Het gesprek bestáát. Het is in v23.144 gebouwd, app en server allebei: drie beurten, Chispa begint
uit een lijst van acht openers zodat het gesprek er ook staat als de server plat ligt, de correctie
staat náást het gesprek in plaats van erin, en vastlopen mag in het Nederlands ("hoe zeg ik...?").
De server heeft /api/ai/chat met twee modi.

Het is alleen niet te vinden. De deur is de vierde kaart op de Chispa-pagina, en die pagina zit
achter Meer. Drie tikken diep, onder de groei- en vitrinekaart. En het voorstel na je les komt
alleen als je een les helemaal uitspeelt.

Dus dit is geen bouwronde maar een verhuizing: iets wat af is stond op een plek waar niemand komt.
Dat is precies dezelfde diagnose als bij Música gisteren, en bij lezen vóór v23.140. Het patroon is
inmiddels drie keer hetzelfde: **wat niet in de dagles staat, bestaat niet.**

## Wat er verandert

Het schrijfblok van je dagles is om de dag een gesprek.

  even dag:   3 zinnen vertalen   (gestuurde productie: de zin ligt vast, jij zoekt de vorm)
  oneven dag: 3 beurten praten    (vrije productie: jij bepaalt wat je zegt)

Allebei zijn het Nation's tweede draad, en ze doen iets anders. Vertalen traint de vorm met een vast
doel; praten traint het kiezen zelf, en dat is de stap die je in de echte wereld nodig hebt. Om de
dag, want ze zijn geen van beide vervanging van de ander.

Twee remmen:

  * **Niet vanaf dag één.** Pas als je op trede 2 van de zinnenladder staat (v23.136), dus als je
    minstens een paar zinnen zelf hebt geschreven. Vrij praten terwijl je nog geen zin kunt maken is
    geen oefening maar een muur.
  * **Niet als de AI plat ligt.** Dan staat er een knop naar het schrijfblok, want stilstaan
    halverwege je les is precies waar v20.5 op is teruggedraaid.

En het staat vooraf in je dagplan, met naam en minuten, net als de rest (v23.135).

Bewaakt door test/suites/pw-praatblok.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.150"

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


# ================= 1. wat het schrijfblok vandaag is =================

rep(
    '''function renderChat(){''',
    '''/* ================= HET PRAATBLOK (v23.150) =================

   Stefan, drie keer: "ik kan ook nog niet chatten met chispa."

   Het gesprek bestond al sinds v23.144, app en server allebei. Het stond alleen als vierde kaart op
   de Chispa-pagina, en die zit achter Meer: drie tikken diep. Wat niet in de dagles staat, bestaat
   niet; dat is nu drie keer dezelfde diagnose (lezen vóór v23.140, Música vóór v23.148, dit).

   Om de dag, en niet elke dag: vertalen en praten zijn allebei Nation's tweede draad maar ze doen
   iets anders. Bij vertalen ligt de zin vast en zoek jij de vorm; bij praten kies je zelf wat je
   zegt, en dat is de stap naar de echte wereld. Geen van beide vervangt de ander.

   Twee remmen. Niet vanaf dag één (trede 2 van de zinnenladder, v23.136): vrij praten terwijl je nog
   geen zin kunt maken is geen oefening maar een muur. En niet als de AI plat ligt: dan staat er een
   knop naar het schrijfblok, want halverwege je les stilstaan is waar v20.5 op is teruggedraaid. */
var PRAAT_TREDE_MIN = 2;

function praatKan(){
  if(chatGedaanVandaag()) return false;
  try { if(vertTrede() < PRAAT_TREDE_MIN) return false; } catch(e){ return false; }
  return true;
}
/* Om de dag, op jouw actieve dagen en niet op de kalender: wie een week overslaat komt terug waar
   hij gebleven was. Dezelfde teller als het liedblok (v23.148). */
function praatBeurt(){
  if(!praatKan()) return false;
  var d = 0;
  try { d = dagenTotaal(); } catch(e){ d = 0; }
  return d > 1 && (d % 2) === 1;
}
function praatBlokWat(){
  return ct(CHAT_BEURTEN + " beurten in het Spaans", CHAT_BEURTEN + " turns in Spanish");
}

function renderChat(){''',
)

# ================= 2. het staat in je dagplan =================

rep(
    '''  var kanSchrijven = false;
  try { kanSchrijven = !!allowedSentIds().length; } catch(e){ kanSchrijven = false; }
  if(kanSchrijven){
    blokken.push({stap:"produceren", naam:ct("Schrijven","Writing"), draad:ct("zelf maken","output"),
      wat:SCHRIJF_PER_LES + " " + ct("zinnen","sentences"), sec:SCHRIJF_PER_LES * SCHRIJF_SEC});
  }''',
    '''  /* v23.150: om de dag is het schrijfblok een gesprek. Allebei zelf iets maken, maar bij vertalen
     ligt de zin vast en bij praten kies je zelf wat je zegt. */
  var praat = false;
  try { praat = praatBeurt(); } catch(e){ praat = false; }
  var kanSchrijven = false;
  try { kanSchrijven = !!allowedSentIds().length; } catch(e){ kanSchrijven = false; }
  if(praat){
    blokken.push({stap:"produceren", naam:ct("Praten met Chispa","Talking with Chispa"),
      draad:ct("zelf maken","output"), wat:praatBlokWat(), sec:CHAT_BEURTEN * SCHRIJF_SEC * 1.6});
  } else if(kanSchrijven){
    blokken.push({stap:"produceren", naam:ct("Schrijven","Writing"), draad:ct("zelf maken","output"),
      wat:SCHRIJF_PER_LES + " " + ct("zinnen","sentences"), sec:SCHRIJF_PER_LES * SCHRIJF_SEC});
  }''',
)

# ================= 3. de flow gaat er echt heen =================

rep(
    '''    if(allowedSentIds().length){
      lesFlow.stap = "produceren";
      lesFlow.vaardigheid = "schrijven";
      lesFlow.vaardigheidRij = [];
      lesFlow.gekozenSpel = "vertalen";
      lesFlow.vertalenTeGaan = lesFlow.vertalenTotaal = SCHRIJF_PER_LES;
      show("vertalen");
      return;
    }
    lesFlowKlaar();
    return;
  }
  if(lesFlow.stap === "produceren"){''',
    '''    if(lesFlowNaarProduceren()) return;   // v23.150
    lesFlowKlaar();
    return;
  }
  if(lesFlow.stap === "produceren"){''',
)

rep(
    '''    if(allowedSentIds().length){
      lesFlow.stap = "produceren";
      lesFlow.vaardigheid = "schrijven";
      lesFlow.vaardigheidRij = [];
      lesFlow.gekozenSpel = "vertalen";
      lesFlow.vertalenTeGaan = lesFlow.vertalenTotaal = SCHRIJF_PER_LES;
      show("vertalen");
      return;
    }''',
    '''    if(lesFlowNaarProduceren()) return;   // v23.150''',
)

rep(
    '''function lesFlowOpenProductie(){''',
    '''/* v23.150: één plek die het schrijfblok opent, want er waren er twee die hetzelfde deden en dan
   krijgt er straks eentje het gesprek niet mee. Geeft terug of er iets geopend is. */
function lesFlowNaarProduceren(){
  var praat = false;
  try { praat = praatBeurt(); } catch(e){ praat = false; }
  if(praat){
    lesFlow.stap = "produceren";
    lesFlow.vaardigheid = "praten";
    lesFlow.vaardigheidRij = [];
    lesFlow.gekozenSpel = "chat";
    show("chat");
    return true;
  }
  if(allowedSentIds().length){
    lesFlow.stap = "produceren";
    lesFlow.vaardigheid = "schrijven";
    lesFlow.vaardigheidRij = [];
    lesFlow.gekozenSpel = "vertalen";
    lesFlow.vertalenTeGaan = lesFlow.vertalenTotaal = SCHRIJF_PER_LES;
    show("vertalen");
    return true;
  }
  return false;
}

function lesFlowOpenProductie(){''',
)

rep(
    '''  var v = lesFlow.vaardigheid;
  var tijd = vaardigheidTijd();
  if(v === "lezen"){''',
    '''  var v = lesFlow.vaardigheid;
  var tijd = vaardigheidTijd();
  if(v === "praten"){   // v23.150
    lesFlow.gekozenSpel = "chat";
    show("chat");
    return;
  }
  if(v === "lezen"){''',
)

# ================= 4. de banner noemt het bij naam =================

rep(
    '''  if(f.stap === "input" && f.vaardigheid === "musica") return ct("Liedje","Song");''',
    '''  if(f.stap === "input" && f.vaardigheid === "musica") return ct("Liedje","Song");
  if(f.stap === "produceren" && f.vaardigheid === "praten") return ct("Praten","Talking");''',
)

# ================= 5. ligt de AI plat, dan sta je niet stil =================

rep(
    '''      "<div class='row' style='margin-top:8px'>"+
        "<button class='primary' id='chatStuur'"+(chatBezig ? " disabled" : "")+">"+ct("Versturen","Send")+"</button>"+
        "<button class='ghost' id='chatHulp'>"+ct("Hoe zeg ik...?","How do I say...?")+"</button>"+
        (inFlow ? "<button class='ghost' id='chatFlow'>"+ct("Overslaan \\u2192","Skip \\u2192")+"</button>"
                : "<button class='ghost' id='chatTerug'>"+ct("\\u2190 Terug","\\u2190 Back")+"</button>")+
      "</div>";''',
    '''      "<div class='row' style='margin-top:8px'>"+
        "<button class='primary' id='chatStuur'"+(chatBezig ? " disabled" : "")+">"+ct("Versturen","Send")+"</button>"+
        "<button class='ghost' id='chatHulp'>"+ct("Hoe zeg ik...?","How do I say...?")+"</button>"+
        /* v23.150: sinds het gesprek een blok in de les is, is "overslaan" niet genoeg. Ligt de AI
           plat, dan hoort er iets te staan wat je wél kunt doen; halverwege je les stilstaan is
           precies waar v20.5 op is teruggedraaid. */
        (inFlow ? "<button class='ghost' id='chatNaarZinnen'>"+ct("Liever zinnen schrijven","Rather write sentences")+"</button>"
                : "")+
        (inFlow ? "<button class='ghost' id='chatFlow'>"+ct("Overslaan \\u2192","Skip \\u2192")+"</button>"
                : "<button class='ghost' id='chatTerug'>"+ct("\\u2190 Terug","\\u2190 Back")+"</button>")+
      "</div>";''',
)

rep(
    '''  b = document.getElementById("chatFlow"); if(b) b.onclick = function(){ chatStand().klaar = true; persist(); lesFlowVolgende(); };''',
    '''  b = document.getElementById("chatFlow"); if(b) b.onclick = function(){ chatStand().klaar = true; persist(); lesFlowVolgende(); };
  /* v23.150: hetzelfde blok, andere vorm. Niet lesFlowVolgende(): dan sla je het schrijfblok over in
     plaats van het te doen. */
  b = document.getElementById("chatNaarZinnen");
  if(b) b.onclick = function(){
    chatStand().klaar = true;
    persist();
    if(lesFlow && allowedSentIds().length){
      lesFlow.vaardigheid = "schrijven";
      lesFlow.gekozenSpel = "vertalen";
      lesFlow.vertalenTeGaan = lesFlow.vertalenTotaal = SCHRIJF_PER_LES;
      show("vertalen");
      return;
    }
    lesFlowVolgende();
  };''',
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
