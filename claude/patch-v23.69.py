#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.69: het kaartje legt zichzelf uit, één sessie lang.

Stefan, 12 aug, met twee schermafdrukken van de woordtrainer: "hier als je niet bekend met
flashcards weet je niet wat je moet doen of hoe dit werkt. Je mist hier uitleg."

Hij heeft gelijk, en het gaat niet over de voorkant. Daar staat "Wat betekent dit?" en een knop
"Toon antwoord"; dat is te volgen. Het gaat over wat er dán gebeurt:

    el jardín
    de tuin
    [ Wist ik ]   [ Wist niet ]

Twee knoppen die je vragen jezelf een cijfer te geven, zonder te zeggen wat dat cijfer doet. Wie het
systeem kent weet dat "wist ik" het woord verder wegduwt en "wist niet" het morgen terugbrengt. Wie
het niet kent, ziet twee knoppen waarvan er één klinkt als toegeven dat je iets fout deed, en kiest
dus de vriendelijke. Dat is niet luiheid, dat is een interface die niet vertelt wat de knop kost.

En op de voorkant ontbreekt het stukje waar de hele methode op rust: dat je het antwoord éérst zelf
moet proberen, ook als je twijfelt. Zonder die poging is een kaartje omdraaien lezen, en lezen plakt
niet.

## Wanneer het er staat

Zolang je je eerste les nog niet hebt afgerond (`S.lesFlowEerste`). Dat is precies de groep waar
Stefan het over heeft, en het verdwijnt vanzelf zonder dat er ergens een telling bijgehouden hoeft
te worden. Wie de app al gebruikt, ziet niets nieuws.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.69"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "function kaartUitlegHtml" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_VOOR = '''    "<p class='muted'>"+(S.dir==="es-nl"?tt("watBetekent"):tt("hoeZegJe"))+"</p>"+
    "<div class='row'><button class='primary' id='btnShow'>"+tt("toonAntwoord")+"</button></div>"+'''

A_ACHTER = '''    "<div class='row'><button class='good' id='btnGood'>"+tt("wistIk")+"</button>"+
    "<button class='bad' id='btnBad'>"+tt("wistNiet")+"</button></div>"+
    wStopHtml();'''

A_PLEK = '''function showWord(){'''

if DOE_APP:
    ontbreekt = [a for a in [A_VOOR, A_ACHTER, A_PLEK] if a not in src]
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
    rep(A_PLEK, '''/* ================= HET KAARTJE LEGT ZICHZELF UIT (v23.69) =================
   Stefan: "hier als je niet bekend met flashcards weet je niet wat je moet doen of hoe dit werkt.
   Je mist hier uitleg."

   Twee regels, allebei over iets wat de app wel doet maar niet zegt. Op de voorkant: dat je het
   antwoord eerst zelf moet proberen, ook als je twijfelt, want zonder die poging is omdraaien
   gewoon lezen. Op de achterkant: wat de twee knoppen kosten. "Wist ik" duwt het woord verder weg,
   "wist niet" brengt het morgen terug. Zonder die zin klinkt "wist niet" als toegeven dat je iets
   fout deed, en kiest een beginner de vriendelijke knop.

   Alleen zolang je je eerste les nog niet hebt afgerond. Dat is precies de groep waar het om gaat,
   het verdwijnt vanzelf, en er hoeft nergens een teller voor bij te worden gehouden. */
function kaartEersteKeer(){
  try { return !S.lesFlowEerste; } catch(e){ return false; }
}
function kaartUitlegHtml(kant){
  if(!kaartEersteKeer()) return "";
  var t = kant === "achter"
    ? ct("Beoordeel jezelf eerlijk. <b>Wist ik</b> laat dit woord langer weg; <b>wist niet</b> brengt het morgen terug. Er kijkt niemand mee, en eerlijk zijn kost je niets.",
         "Judge yourself honestly. <b>Knew it</b> keeps this word away longer; <b>didn't know</b> brings it back tomorrow. Nobody is watching, and being honest costs you nothing.")
    : ct("Probeer het antwoord eerst zelf te bedenken, ook als je twijfelt. Die poging is wat het laat plakken; alleen lezen werkt niet.",
         "Try to come up with the answer yourself first, even if you are unsure. That attempt is what makes it stick; just reading does not.");
  return "<p class='muted' style='margin:8px 2px; font-size:.84rem; line-height:1.5'>"+t+"</p>";
}
function showWord(){''')

    rep(A_VOOR, '''    "<p class='muted'>"+(S.dir==="es-nl"?tt("watBetekent"):tt("hoeZegJe"))+"</p>"+
    kaartUitlegHtml("voor")+
    "<div class='row'><button class='primary' id='btnShow'>"+tt("toonAntwoord")+"</button></div>"+''')

    rep(A_ACHTER, '''    kaartUitlegHtml("achter")+
    "<div class='row'><button class='good' id='btnGood'>"+tt("wistIk")+"</button>"+
    "<button class='bad' id='btnBad'>"+tt("wistNiet")+"</button></div>"+
    wStopHtml();''')

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
