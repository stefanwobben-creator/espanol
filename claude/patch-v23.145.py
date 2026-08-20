#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.145: waar je loopt wordt geteld, en de Speeltuin krimpt naar drie plekken.

Stefan, 20 aug: "Ja zodat we alleen het beste behouden."

## Eerst het probleem met die zin

Om alleen het beste te behouden moet je weten wat het beste is, en dat weten we niet. Uit de meting
van 20 aug (`Waar het gras kaal is`): van Woordenzoeker, Crucigrama, Letras, Adivina, Memory,
Clasificador, Palabra Duel, Música, Aventura, Lezen en Samen staat er in zesentwintig dagen **geen
enkel gegeven**, van niemand.

Dat is geen bewijs dat ze niet gebruikt worden. De app registreert alleen waar je struikelt (het
foutenlogboek), niet waar je loopt. Een spel waarin je geen fout kúnt maken laat per definitie geen
spoor na. In Sivers' beeld: het park ligt er, er wordt gelopen, maar er is geen gras, want het is
beton.

Dus deze ronde doet twee dingen tegelijk, en de tweede leunt op de eerste.

## 1. De sensor

`navPush()` is de enige plek waar de app noteert dat je ergens naartoe gaat: elk tabblad, elk spel,
elke grammaticales gaat erdoorheen. Drie regels erbij: hoe vaak, en wanneer voor het laatst. Blijft
op je toestel, gaat mee in dezelfde sync die er al is (`logServer`).

Er wordt niet bij elke tik opgeslagen. Alleen de eerste keer per dag dat je ergens komt kost een
schrijfactie; de rest van de dag lift de teller mee op de opslag die er toch al gebeurt.

## 2. En hij wordt meteen gelezen

Dit is de reden dat de sensor er in dezelfde ronde bij zit en niet een week eerder. Drie keer eerder
bleek iets verzameld te worden dat nooit gelezen werd (`S.leesZoek` sinds v23.21, `voortgangBand()`,
de weekopnames). Een teller die alleen naar de server gaat is nummer vier.

De Speeltuin toonde negen tegels naast elkaar, allemaal even groot, allemaal even hard roepend. Nu
staan er drie: **het spel van vandaag** (dat wat je het langst niet geopend hebt, en dat weet hij van
de sensor), Aventura, en Música. De rest staat achter één regel: "alle spellen".

Waarom die drie vast: Aventura is het grote spel, Música heeft geen materiaal nodig en kan dus altijd
draaien, en Palabra Duel heeft een tweede speler nodig, dus die roteert niet mee.

Wat nog niet kan blijft staan waar het stond, in het grijs met de eis erbij. Verdwijnen is geen
opruimen (v23.77).

## Wat deze ronde NIET doet

Er gaat geen enkel spel weg. Dat is precies wat er zonder meting niet moet gebeuren, en over een week
staat er wel iets in de sensor. Wat er verandert is hoe hard ze roepen.

Bewaakt door test/suites/pw-waarjeloopt.js.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.145"

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


# ------------- 1. de sensor

rep(
    """function navPush(state){
  try{ if(window.history && history.pushState) history.pushState(state, ""); }catch(e){}
}""",
    """function navPush(state){
  try{ gezienBij(state); }catch(e){}
  try{ if(window.history && history.pushState) history.pushState(state, ""); }catch(e){}
}
/* ================= WAAR JE LOOPT (v23.145) =================

   De app registreerde tot nu toe alleen waar je struikelt: het foutenlogboek. Waar je heen gaat werd
   nergens vastgelegd. Gevolg (gemeten over 26 dagen, drie gebruikers): van elf onderdelen, waaronder
   alle spellen en het boek, is er geen enkel gegeven. Niet omdat ze niet gebruikt worden, maar omdat
   een spel waarin je geen fout kúnt maken geen spoor nalaat.

   navPush() is de enige plek waar élke overgang doorheen komt: een tab, een spel, een grammaticales.
   Daarom staat het hier en niet in twintig aanroepers.

   Opslaan gebeurt alleen bij de eerste keer per dag dat je ergens komt. De rest van de dag lift de
   teller mee op de opslag die er toch al plaatsvindt; anders kost bladeren evenveel schrijfacties
   als leren. */
function gezienNaam(st){
  if(!st || typeof st !== "object") return null;
  if(st.t === "tab") return st.id || null;
  if(st.t === "fun") return st.v ? ("spel:" + st.v) : null;
  if(st.t === "gramwiz") return "gramles";
  if(st.t === "gclees") return "gramlezen";
  return null;
}
function gezienBij(st){
  var naam = gezienNaam(st);
  if(!naam) return;
  S.gezien = S.gezien || {};
  var g = S.gezien[naam] || {n:0, l:""};
  var eersteVandaag = g.l !== today();
  g.n = (g.n || 0) + 1;
  g.l = today();
  S.gezien[naam] = g;
  if(eersteVandaag){ try { persist(); } catch(e){} }
}
function gezienLaatst(naam){
  var g = (S.gezien || {})[naam];
  return (g && g.l) || "";
}""",
)

rep(
    """    payload.geleerd = Object.keys(S.srs || {}).length;
    payload.minuten = doelMinuten();
    payload.lessenAf = doneLessonCount();""",
    """    payload.geleerd = Object.keys(S.srs || {}).length;
    payload.minuten = doelMinuten();
    payload.lessenAf = doneLessonCount();
    payload.gezien = S.gezien || {};   // v23.145: waar je liep, niet alleen waar je struikelde""",
)

# ------------- 2. het spel van vandaag

rep(
    """function speelTegels(){ return spelInfo().filter(function(x){ return !x.gram; }); }""",
    """function speelTegels(){ return spelInfo().filter(function(x){ return !x.gram; }); }
/* v23.145: welke drie staan er vooraan?

   Aventura is het grote spel en Música heeft geen materiaal nodig, dus die twee staan er altijd. De
   derde plek roteert.

   Palabra Duel staat in geen van beide: hij heeft een tweede speler nodig, dus vooraan zetten belooft
   iets dat je alleen niet kunt, en "het spel van vandaag" zou een doodlopende weg zijn. Hij staat
   achter de regel bij de rest. */
var SPEL_VAST = ["avt", "musica"];
var SPEL_ROTEERT_NIET = ["avt", "musica", "duel"];
/* En het spel van vandaag is dat wat je het langst niet geopend hebt. Nooit geopend telt als het
   langst geleden: daar is de kans het grootst dat je iets vindt.

   Gelijkspel wordt met dayHash gebroken en niet met Math.random(). Anders verspringt de tegel onder
   je handen bij elke hertekening, en dan is "het spel van vandaag" een leugen. */
function spelVanVandaag(){
  var kand = speelTegels().filter(function(g){
    return SPEL_ROTEERT_NIET.indexOf(g.v) === -1 && speelKlaar(g.v);
  });
  if(!kand.length) return null;
  var draai = 0;
  try { draai = dayHash("spel"); } catch(e){ draai = 0; }
  var beste = null, besteSleutel = null;
  kand.forEach(function(x, i){
    var sleutel = (gezienLaatst("spel:" + x.v) || "0000-00-00") + "|" + ((draai + i) % kand.length);
    if(besteSleutel === null || sleutel < besteSleutel){ besteSleutel = sleutel; beste = x; }
  });
  return beste;
}""",
)

# ------------- 3. de Speeltuin krimpt

rep(
    """  var SPEELMENU = speelTegels();
  var rijen = tegelLijstHtml(SPEELMENU);
  var nuHtml = rijen.nu, straksHtml = rijen.straks;""",
    """  /* v23.145: negen tegels naast elkaar, allemaal even groot, allemaal even hard roepend. Nu drie
     vooraan en de rest achter één regel. Er gaat niets weg: wat je zoekt is één tik verderop, en wat
     nog niet kan staat nog steeds in het grijs met de eis erbij (v23.77, verdwijnen is geen
     opruimen). */
  var SPEELMENU = speelTegels();
  /* Op naam vergelijken en niet op het object: spelInfo() bouwt zijn lijst bij elke aanroep opnieuw,
     dus spelVanVandaag() geeft een ánder object terug met dezelfde v. Eerst met indexOf(g) gedaan,
     en toen stond het spel van vandaag er twee keer, met twee keer hetzelfde id. */
  var vandaagV = (spelVanVandaag() || {}).v || null;
  var vooropV = (vandaagV ? [vandaagV] : []).concat(SPEL_VAST.filter(function(v){ return v !== vandaagV; }));
  var voorop = [], rest = [];
  vooropV.forEach(function(v){
    SPEELMENU.forEach(function(g){ if(g.v === v) voorop.push(g); });
  });
  SPEELMENU.forEach(function(g){ if(vooropV.indexOf(g.v) === -1) rest.push(g); });
  var vandaagSpel = vandaagV;
  var rijenV = tegelLijstHtml(voorop), rijenR = tegelLijstHtml(rest);
  var allesUit = !!S.spelAlles;
  var nuHtml = (vandaagSpel ? "<p class='muted' style='margin:8px 0 2px; font-size:.82rem'>"+
                  ct("Het spel van vandaag","Today's game")+"</p>" : "")+
               rijenV.nu + (allesUit ? rijenR.nu : "");
  /* De verborgen tegels worden geteld uit dezelfde lijst die ze zou tekenen. Een handgeschreven
     getal naast een gefilterde lijst is de fout van v23.94 (drie getallen, één chipje). */
  var restN = rest.filter(function(g){ return speelKlaar(g.v); }).length;
  if(restN) nuHtml += "<button class='mini' id='spelMeer'>"+
    (allesUit ? ct("Minder","Fewer")
              : ct("Alle spellen ("+restN+" meer)","All games ("+restN+" more)"))+"</button>";
  // wat nog niet kan staat er hoe dan ook, open of dicht: dat is een belofte over later en geen keuze
  var straksHtml = rijenV.straks + rijenR.straks;""",
)

rep(
    """  tegelWire(SPEELMENU);
  var sa = document.getElementById("speelAlles");""",
    """  tegelWire(SPEELMENU);
  var sm = document.getElementById("spelMeer");
  if(sm) sm.onclick = function(ev){
    if(ev && ev.preventDefault) ev.preventDefault();
    S.spelAlles = !S.spelAlles;
    try { persist(); } catch(e){}
    renderFun();
    return false;
  };
  var sa = document.getElementById("speelAlles");""",
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
