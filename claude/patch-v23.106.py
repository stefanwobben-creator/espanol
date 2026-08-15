#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.106: achtergrond of gebeurtenis. De eerste brok, en de eerste meting die de twee dingen
uit elkaar haalt.

## Waar dit vandaan komt

Stefan, drie keer op één dag, in verschillende bewoordingen: "ik kan de regel 8 van de 10 keer
goed toepassen maar niet alle vervoegingen uit mijn hoofd, dus dan gok ik maar wat."

Elke grammaticavraag in de app test op dit moment twee dingen tegelijk:

    Mientras ___ (esperar) el autobús, ___ (ver) a un viejo amigo.
       esperaba, vi   |   esperé, vi   |   esperaba, veía

Om dit goed te doen moet je de regel kennen (achtergrond is imperfecto, gebeurtenis is
indefinido) én de vormen kennen (esperaba, vi). Ga je onderuit, dan weet niemand welke van de
twee het was. De app noteert "indefimperf fout", zet het concept op doos 0, en legt morgen de
regel opnieuw uit. De regel die je al kende.

Dat is een meetfout in het leersysteem zelf: één cijfer voor twee dingen. Precies de klasse
fout die deze week ook in de tellers, de weekkaart en de herkomstmeting zat.

## Wat dit scherm doet

Twaalf Nederlandse zinnen, twee bakjes: achtergrond of gebeurtenis. **Er komt geen woord Spaans
aan te pas.** Dat is het hele punt: zonder Spaans kan de vorm de meting niet vervuilen.

    11 of 12 goed  -> je snapt het verschil. Gaat het Spaans dan toch mis, dan ligt het aan de
                      vormen, en dat is een andere oefening.
     8 tot 10      -> het zit er half in.
     7 of minder   -> hier zit het gat, en meer vervoegingen stampen helpt niet.

Twee van de twaalf zijn met opzet een strikvraag, en ze vormen een paar:

    "Ik werkte bij die firma toen ik hem leerde kennen."  -> achtergrond (het loopt door)
    "Ik werkte drie jaar bij die firma."                  -> gebeurtenis (afgesloten blok)

Zelfde werkwoord, ander antwoord. Zo kun je niet op het woord patroonherkennen, en dat is
precies wat een meting die iets waard is moet uitsluiten.

## Waarom dit een eigen scherm is en niet een stap in de conceptles

Omdat het een meting is en geen les. Het antwoord moet iets betekenen op het moment dat je het
geeft, en het mag niet verdwijnen tussen vier andere vragen over hetzelfde onderwerp. Als het
model klopt (zie het projectdocument over de tien brokken) wordt dit later stap 1 van
indefinido-tegenover-imperfecto en komen de vormbrokken erachter.

## Waar de uitslag heen gaat

Naar S.brok, een nieuwe map, en bewust NIET naar S.gram. S.gram is de SRS-boekhouding per
concept en daar hangt van alles aan: gramFoutTop(), gcOpenSet(), de dagles. Een brok in die pot
gooien voordat we weten of het brokkenmodel klopt, is precies het soort verstrengeling waar we
deze week een dag aan kwijt waren. Eerst meten, dan pas koppelen.

## Architectuurregel

Afgesproken op 15 augustus, naar aanleiding van "de autoen staan in Madrid": staat een feit in
de data, dan schrijft geen enkele codeplek dat feit opnieuw. Hier zichtbaar in het feit dat de
twaalf zinnen, hun soort, hun uitleg en hun Engelse versie in één array staan en dat de
rendercode geen enkele zin kent. Een dertiende zin toevoegen is één regel data.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.106"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.106" not in src
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


# ---------------------------------------------------------------- de brok zelf
A_SPELINFO = '''function spelInfo(){
  return ['''
N_SPELINFO = '''/* ================= BROK: ACHTERGROND OF GEBEURTENIS (v23.106) =================

   De eerste brok van het brokkenmodel. Zie de kop van patch-v23.106 voor het waarom; kort:
   elke grammaticavraag in de app test de regel en de vorm tegelijk, dus een fout zegt niet
   welke van de twee ontbrak. Hier staat geen woord Spaans, dus de vorm kan de meting niet
   vervuilen.

   De twaalf zinnen zijn data en de rendercode kent er geen enkele. Een dertiende toevoegen is
   één regel hieronder, en dan werkt alles mee: de teller, de uitslag, de vertaling.

   De twee strikvragen staan er met opzet, en ze vormen een paar met hetzelfde werkwoord:
   "toen ik hem leerde kennen" loopt door (achtergrond), "drie jaar" is een afgesloten blok
   (gebeurtenis). Zonder dat paar kun je op het werkwoord patroonherkennen en meet je niets. */
var BROK_TIJD = [
  {nl:"Vroeger woonde ik in Utrecht.",
   en:"I used to live in Utrecht.", s:"a",
   w:"Waar je toen woonde is een toestand, geen gebeurtenis. Vroeger, altijd, in die tijd: achtergrond.",
   wEn:"Where you lived back then is a state, not an event. Used to, always, in those days: background."},
  {nl:"Gisteren belde hij me op.",
   en:"He called me yesterday.", s:"g",
   w:"E\u00e9n keer, gisteren, klaar. Dat duwt het verhaal vooruit: gebeurtenis.",
   wEn:"Once, yesterday, done. That pushes the story forward: event."},
  {nl:"Ik ging altijd op zondag zwemmen.",
   en:"I always went swimming on Sundays.", s:"a",
   w:"Altijd, elke zondag: een gewoonte. Gewoontes zijn achtergrond.",
   wEn:"Always, every Sunday: a habit. Habits are background."},
  {nl:"Toen brak hij zijn arm.",
   en:"Then he broke his arm.", s:"g",
   w:"E\u00e9n moment, en daarna gaat het verhaal verder: gebeurtenis.",
   wEn:"One moment, and then the story moves on: event."},
  {nl:"Het was koud die winter.",
   en:"It was cold that winter.", s:"a",
   w:"Hoe het was. Weer, gevoel, uiterlijk: een beschrijving is achtergrond.",
   wEn:"How it was. Weather, mood, looks: a description is background."},
  {nl:"In 2019 verhuisden we naar Spanje.",
   en:"In 2019 we moved to Spain.", s:"g",
   w:"Een jaartal maakt het afgesloten: gebeurtenis.",
   wEn:"A year makes it closed off: event."},
  {nl:"Ik werkte bij die firma toen ik hem leerde kennen.",
   en:"I was working at that firm when I met him.", s:"a",
   w:"Het werken loopt door terwijl er iets anders gebeurt. Dat is het toneel, niet de gebeurtenis.",
   wEn:"The working continues while something else happens. That is the stage, not the event."},
  {nl:"Ik werkte drie jaar bij die firma.",
   en:"I worked at that firm for three years.", s:"g",
   w:"Drie jaar is lang, maar het is een blok met een begin en een eind. Afgesloten: gebeurtenis. Let op het verschil met de vorige zin: zelfde werkwoord, ander antwoord.",
   wEn:"Three years is long, but it is a block with a start and an end. Closed off: event. Note the difference with the previous sentence: same verb, different answer."},
  {nl:"Ze had lang haar toen ze klein was.",
   en:"She had long hair when she was little.", s:"a",
   w:"Hoe iemand eruitzag: beschrijving, dus achtergrond.",
   wEn:"How someone looked: description, so background."},
  {nl:"Op een dag stopte hij ermee.",
   en:"One day he stopped.", s:"g",
   w:"Op een dag kondigt een gebeurtenis aan die het verhaal vooruit duwt.",
   wEn:"One day announces an event that pushes the story forward."},
  {nl:"We aten elke dag om twee uur.",
   en:"We ate at two o'clock every day.", s:"a",
   w:"Elke dag: gewoonte, dus achtergrond. Ook al is eten een handeling.",
   wEn:"Every day: habit, so background. Even though eating is an action."},
  {nl:"Vorige week kocht ik een fiets.",
   en:"Last week I bought a bike.", s:"g",
   w:"Vorige week, \u00e9\u00e9n aankoop, klaar: gebeurtenis.",
   wEn:"Last week, one purchase, done: event."}
];
var BROK_ID = "indefimperf.betekenis";
var brokSpel = null;   // {rij:[indexen], i, goed, fout, gekozen}

/* Bewust een eigen map en niet S.gram. Aan S.gram hangen gramFoutTop(), gcOpenSet() en de
   dagles; een brok daarin gooien vóórdat we weten of het brokkenmodel klopt is precies de
   verstrengeling waar we deze week een dag aan kwijt waren. Eerst meten, dan koppelen. */
function brokLees(id){
  S.brok = S.brok || {};
  return S.brok[id] || {goed:0, fout:0, beste:0, laatst:"", rondes:0};
}
function brokBij(id, goed, totaal){
  S.brok = S.brok || {};
  var st = brokLees(id);
  st.goed += goed; st.fout += (totaal - goed);
  st.beste = Math.max(st.beste || 0, goed);
  st.laatst = today(); st.rondes = (st.rondes || 0) + 1;
  S.brok[id] = st;
  persist();
}
function brokZin(z){ return ct(z.nl, z.en); }
function brokWaarom(z){ return ct(z.w, z.wEn); }
function brokStart(){
  var rij = [];
  for(var i = 0; i < BROK_TIJD.length; i++) rij.push(i);
  brokSpel = {rij:geschud(rij), i:0, goed:0, gekozen:null};
}
function brokAntwoord(keuze){
  if(!brokSpel || brokSpel.gekozen !== null) return;
  var z = BROK_TIJD[brokSpel.rij[brokSpel.i]];
  brokSpel.gekozen = keuze;
  if(keuze === z.s){ brokSpel.goed++; addXP(1); }
  renderFunBrok();
}
function brokVolgende(){
  if(!brokSpel) return;
  brokSpel.i++; brokSpel.gekozen = null;
  if(brokSpel.i >= brokSpel.rij.length) brokBij(BROK_ID, brokSpel.goed, brokSpel.rij.length);
  renderFunBrok();
}
/* De uitslag is het punt van dit scherm. Niet "8/12" maar wat 8/12 betekent voor wat je morgen
   moet doen, want dat is precies wat je met \u00e9\u00e9n cijfer per concept nooit te weten komt. */
function brokUitslag(goed, totaal){
  if(goed >= totaal - 1)
    return ct("Je snapt het verschil. Gaat het in het Spaans dan toch mis, dan ligt het aan de vormen en niet aan de regel. Dat is een andere oefening, en die komt eraan.",
              "You get the difference. If Spanish still goes wrong, it is the forms and not the rule. That is a different exercise, and it is coming.");
  if(goed >= totaal - 4)
    return ct("Het zit er half in. Kijk bij welke zinnen je twijfelde: als dat de gewoontes waren, dan is dat \u00e9\u00e9n regel om te onthouden en ben je er zo.",
              "It is half there. Look at which sentences made you doubt: if it was the habits, that is one rule to remember and you are nearly there.");
  return ct("Hier zit je gat, en het is een goed gat om te vinden: meer vervoegingen stampen gaat je niet helpen zolang dit niet zit. Lees de uitleg nog eens en doe hem morgen opnieuw.",
            "This is your gap, and it is a good one to find: drilling more verb forms will not help while this is missing. Read the explanation again and do this once more tomorrow.");
}
function renderFunBrok(){
  var el = document.getElementById("funCard");
  if(!el) return;
  if(!brokSpel) brokStart();
  var totaal = brokSpel.rij.length;
  var kop = "<h2>" + ct("Achtergrond of gebeurtenis \\ud83c\\udfad", "Background or event \\ud83c\\udfad") + "</h2>";

  if(brokSpel.i >= totaal){
    var st = brokLees(BROK_ID);
    el.innerHTML = kop +
      "<div class='feedback " + (brokSpel.goed >= totaal - 1 ? "ok" : brokSpel.goed >= totaal - 4 ? "bijna" : "fout") + "'>" +
        brokSpel.goed + " / " + totaal + "</div>" +
      "<p class='muted'>" + brokUitslag(brokSpel.goed, totaal) + "</p>" +
      (st.rondes > 1 ? "<p class='muted' style='font-size:.85rem'>" +
        ct("Je beste ronde tot nu toe: ", "Your best round so far: ") + st.beste + " / " + totaal + "</p>" : "") +
      "<div class='row' style='margin-top:10px'>" +
        "<button class='primary' id='btnBrokNieuw'>" + ct("Nog een ronde", "Another round") + "</button>" +
        "<button class='ghost' id='btnFunTerug'>" + fx("terug") + "</button></div>";
    document.getElementById("btnBrokNieuw").onclick = function(){ brokStart(); renderFunBrok(); };
    document.getElementById("btnFunTerug").onclick = function(){ funView = null; brokSpel = null; renderFun(); };
    return;
  }

  var z = BROK_TIJD[brokSpel.rij[brokSpel.i]];
  var af = brokSpel.gekozen !== null;
  var goed = af && brokSpel.gekozen === z.s;
  el.innerHTML = kop +
    "<span class='kicker'>" + ct("Zin ", "Sentence ") + (brokSpel.i + 1) + "/" + totaal + "</span>" +
    (brokSpel.i === 0 && !af
      ? "<p class='muted'>" + ct("Geen Spaans, alleen Nederlands. Beschrijft de zin hoe iets w\u00e1s, of vertelt hij wat er gebeurde? Dat onderscheid is de hele regel achter indefinido en imperfecto.",
                                 "No Spanish, just English. Does the sentence describe how things were, or tell what happened? That distinction is the whole rule behind indefinido and imperfecto.") + "</p>"
      : "") +
    "<p class='big' style='margin:10px 0'>" + brokZin(z) + "</p>" +
    (af
      ? "<div class='feedback " + (goed ? "ok" : "fout") + "'>" +
          (goed ? ct("Goed \u2713", "Correct \u2713")
                : ct("Nog niet. Het is: ", "Not yet. It is: ") +
                  "<b>" + (z.s === "a" ? ct("achtergrond", "background") : ct("gebeurtenis", "event")) + "</b>") +
        "</div>" +
        "<p class='waarom' style='margin-top:8px'>" + brokWaarom(z) + "</p>" +
        "<div class='row' style='margin-top:10px'><button class='primary' id='btnBrokVerder'>" +
          (brokSpel.i + 1 >= totaal ? ct("Uitslag \u2192", "Result \u2192") : ct("Volgende \u2192", "Next \u2192")) + "</button></div>"
      : "<div class='row' style='margin-top:6px'>" +
          "<button class='ghost' id='btnBrokA' style='flex:1; min-height:64px'>" +
            ct("Achtergrond<br><span class='muted' style='font-weight:400; font-size:.82rem'>hoe het w\u00e1s</span>",
               "Background<br><span class='muted' style='font-weight:400; font-size:.82rem'>how things were</span>") + "</button>" +
          "<button class='ghost' id='btnBrokG' style='flex:1; min-height:64px'>" +
            ct("Gebeurtenis<br><span class='muted' style='font-weight:400; font-size:.82rem'>wat er gebeurde</span>",
               "Event<br><span class='muted' style='font-weight:400; font-size:.82rem'>what happened</span>") + "</button></div>") +
    "<div class='row' style='margin-top:10px'><button class='mini' id='btnFunTerug'>" + fx("terug") + "</button></div>";

  function wire(id, fn){ var b = document.getElementById(id); if(b) b.onclick = fn; }
  wire("btnBrokA", function(){ brokAntwoord("a"); });
  wire("btnBrokG", function(){ brokAntwoord("g"); });
  wire("btnBrokVerder", brokVolgende);
  wire("btnFunTerug", function(){ funView = null; brokSpel = null; renderFun(); });
}

function spelInfo(){
  return ['''

A_TEGEL = '''    {v:"clas",    id:"ftClas",    e:"\\u26a1",                  t:"Clasificador",          s:ct("Links of rechts, en het gaat steeds sneller.","Left or right, and it keeps speeding up.")},'''
N_TEGEL = '''    {v:"clas",    id:"ftClas",    e:"\\u26a1",                  t:"Clasificador",          s:ct("Links of rechts, en het gaat steeds sneller.","Left or right, and it keeps speeding up.")},
    /* v23.106: geen spel maar een meting, en hij staat hier omdat dit de plek is waar je iets
       kunt doen dat geen dagportie is. Zodra het brokkenmodel staat verhuist hij naar stap 1
       van indefinido-tegenover-imperfecto. */
    {v:"brok",    id:"ftBrok",    e:"\\ud83c\\udfad",            t:ct("Achtergrond of gebeurtenis","Background or event"), s:ct("Twaalf Nederlandse zinnen, twee bakjes. Geen Spaans: dit meet of je de regel snapt, los van de vormen.","Twelve English sentences, two bins. No Spanish: this measures whether you get the rule, apart from the forms.")},'''

# De dagkaart put uit dezelfde lijst als de Speeltuin. DAGSPEL_UIT bestaat precies voor dingen
# die wel in de Speeltuin horen en niet op je dagkaart (Aventura en Palabra Duel staan er al in).
# Zonder deze regel groeit Vandaag met een tiende rij, en pw-v1998 zag dat meteen: de onderste
# tegel viel achter de vaste onderbalk. Dat is de juiste reparatie en niet de suite verzachten:
# Vandaag draagt je dagelijkse lus, en dit is een meting.
A_DAGUIT = '''var DAGSPEL_UIT = {avt:1, duel:1};'''
N_DAGUIT = '''var DAGSPEL_UIT = {avt:1, duel:1, brok:1};   // v23.106: zie de kop van deze patch'''

A_ROUTE = '''  if(funView === "duel"){ renderFunDuel(); return; }'''
N_ROUTE = '''  if(funView === "duel"){ renderFunDuel(); return; }
  if(funView === "brok"){ renderFunBrok(); return; }   // v23.106'''

A_WIRE = '''  wire("ftDuel", function(){ funView = "duel"; navPush({t:"fun", v:"duel"}); renderFun(); });'''
N_WIRE = '''  wire("ftDuel", function(){ funView = "duel"; navPush({t:"fun", v:"duel"}); renderFun(); });
  wire("ftBrok", function(){ funView = "brok"; brokSpel = null; navPush({t:"fun", v:"brok"}); renderFun(); });'''

if DOE_APP:
    ontbreekt = [n for n, a in (
        ("spelInfo", A_SPELINFO), ("de Clasificador-tegel", A_TEGEL),
        ("de routering in renderFun", A_ROUTE), ("de knoppen van de Speeltuin", A_WIRE),
        ("de dagkaartfilter", A_DAGUIT)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.105. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_SPELINFO, N_SPELINFO)
    rep(A_TEGEL, N_TEGEL)
    rep(A_ROUTE, N_ROUTE)
    rep(A_WIRE, N_WIRE)
    rep(A_DAGUIT, N_DAGUIT)

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
