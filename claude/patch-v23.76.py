#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.76: een ontbrekende opname is geen stilte meer.

Stefan, 13 aug: "is het mogelijk om een lijst te krijgen van wat concreet is toegevoegd? bijv
nieuwe audiolessen? dat staat volgens mij stil."

Geteld, en het stond stil. audio/dictado/ bevat 201 bestanden: precies bs1-bs69 en s1-s132, de
stand van 30 juli. Sindsdien zijn er 50 zinnen bijgekomen. Op 20% van het corpus, en juist op het
nieuwste deel, deed de knop "Hoor hem" dus niets.

Niets, en niet "iets anders". Dat is wat deze patch repareert. Het vullen van de gaten gebeurt
elders (tools/avondrun-audio.js draait nu in de avondrun); dit gaat over wat de app doet als een
bestand er níét is.

## Twee plekken die een fout opaten

**De zinsknop.** zinSpreek() eindigde op:

    var p = a.play();
    if(p && p.catch) p.catch(function(){});

Een lege catch. De belofte wordt netjes afgehandeld en er gebeurt niets. Voor de gebruiker is dat
niet te onderscheiden van een kapotte knop, en er is geen enkel signaal, ook niet in de console.

**Het boek.** boekSpreek() ziet er beter uit maar is het niet:

    var teruggevallen = false;
    function valTerug(){ if(teruggevallen) return; teruggevallen = true; }
    a.addEventListener("error", valTerug);

Er staat een terugvalmechanisme, het wordt netjes tegen dubbel afvuren beschermd, en het doet
niets. De vlag wordt gezet en niemand leest hem. Erger: de opmerking erboven beweert het
tegenovergestelde ("valt de app terug op de voorleesstem van de browser; dat was al zo"). Dat is
twee keer mis, want ook de opmerking bij boekSpreek in v23.27 zei dit al.

Dit is hetzelfde patroon als de tests die groen stonden om een reden die niets met gedrag te maken
had: iets dat eruitziet alsof het gecontroleerd wordt, en dat niet wordt gecontroleerd.

## Wat er nu gebeurt

Allebei vallen ze terug op spreekTTS(), de browserstem die al in de app zit. Dat is hoorbaar
minder mooi dan ElevenLabs, en dat is precies goed: een gat hoor je nu, in plaats van dat het
niets doet. Er is geen melding, geen toast, geen uitleg. De zin klinkt, alleen anders.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.76"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.76" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

A_ZIN = '''var zinAudioEl = null;
function zinSpreek(zin, rate){
  try{
    if(zinAudioEl) zinAudioEl.pause();
    var a = new Audio("audio/dictado/" + zin.id + ".mp3");
    zinAudioEl = a;
    a.playbackRate = rate || 1;
    var p = a.play();
    if(p && p.catch) p.catch(function(){});
  }catch(e){}
}'''

A_BOEK = '''    var map = String(h.id).indexOf("hist-") === 0 ? "hist" : "boek";
    var a = new Audio("audio/" + map + "/" + h.id + ".mp3");
    boekAudioEl = a;
    var teruggevallen = false;
    function valTerug(){ if(teruggevallen) return; teruggevallen = true; }
    a.addEventListener("error", valTerug);
    var p = a.play();
    if(p && p.catch) p.catch(valTerug);
    return true;'''

if DOE_APP:
    ontbreekt = [naam for naam, anker in (("zinSpreek", A_ZIN), ("boekSpreek", A_BOEK)) if anker not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.74. Eerst bijtrekken:\n\n"
              "    git pull --rebase\n" % " en ".join(ontbreekt))
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    rep(A_ZIN, '''var zinAudioEl = null;
/* v23.76: terugvallen in plaats van zwijgen.

   Hier stond een lege catch. Ontbrak audio/dictado/<id>.mp3, dan gebeurde er niets: geen geluid,
   geen melding, geen spoor in de console. Op 13 aug waren dat 50 van de 251 zinnen, want de
   opnames stonden sinds 30 juli stil terwijl de zinnen doorgroeiden.

   De browserstem is hoorbaar minder mooi dan de opname, en dat is precies de bedoeling: zo hoor
   je dát er iets ontbreekt zonder dat de app het je hoeft te vertellen. Geen toast, geen uitleg,
   de zin klinkt alleen anders. */
function zinSpreek(zin, rate){
  try{
    if(zinAudioEl) zinAudioEl.pause();
    var a = new Audio("audio/dictado/" + zin.id + ".mp3");
    zinAudioEl = a;
    a.playbackRate = rate || 1;
    var gevallen = false;
    function valTerug(){
      if(gevallen) return;
      gevallen = true;
      zinAudioEl = null;
      spreekTTS(zin.es, (rate || 1) * 0.9);
    }
    a.addEventListener("error", valTerug);
    var p = a.play();
    if(p && p.catch) p.catch(valTerug);
  }catch(e){
    try{ spreekTTS(zin.es, (rate || 1) * 0.9); }catch(e2){}
  }
}''')

    rep(A_BOEK, '''    var map = String(h.id).indexOf("hist-") === 0 ? "hist" : "boek";
    var a = new Audio("audio/" + map + "/" + h.id + ".mp3");
    boekAudioEl = a;
    var teruggevallen = false;
    /* v23.76: deze functie zette een vlag en verder niets, terwijl de opmerking erboven beweerde
       dat de app terugviel op de browserstem. Dat deed hij dus niet: een ontbrekend hoofdstuk gaf
       stilte. Nu doet hij wat er al stond beschreven. De alineascheiding gaat eruit, anders leest
       de stem de lege regels als een hapering. */
    function valTerug(){
      if(teruggevallen) return;
      teruggevallen = true;
      boekAudioEl = null;
      spreekTTS(String(h.tekst || "").replace(/\\n+/g, " "), 0.95);
    }
    a.addEventListener("error", valTerug);
    var p = a.play();
    if(p && p.catch) p.catch(valTerug);
    return true;''')

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
