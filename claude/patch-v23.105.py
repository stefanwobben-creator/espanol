#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
v23.105: de meting onder de ketting. Waar komt iemand vandaan, en wie heeft hem binnengehaald?

Hoort bij de serverwijziging van dezelfde commit (twee kolommen op profiles en
GET /api/admin/keten).

## Waarom dit vóór de LinkedIn-post moet

Herkomst en verwijzer zijn de enige twee dingen die je later niet alsnog kunt uitrekenen. Retentie
wel: S.xp is een map van datum naar punten, dus wie op dag 2 terugkwam staat er altijd al in en is
met terugwerkende kracht af te lezen. Maar of iemand via Stefan binnenkwam of via een tijdlijn is
op het moment zelf te zien en daarna nooit meer. Wie dat op dag één niet vastlegt, kan over twee
weken alleen nog naar totalen kijken.

## Bevinding 1: iedereen die via een uitnodiging binnenkomt telt als "direct"

Nagemeten in de browser, vier links, dit is wat S.bron werd:

    ?van=linkedin              -> "linkedin"      goed
    ?groep=gtest1              -> "direct"        fout
    ?groep=gtest1&van=linkedin -> "direct"        fout, de van is ook weg
    (geen zoekreeks)           -> "direct"        goed

De oorzaak is een volgorde. Bij een uitnodigingslink haalt de app het groepscode eruit en veegt
daarna de zoekreeks van de adresbalk met history.replaceState. Dat gebeurt tijdens het inlezen van
het script. bronNu() draait pas veel later, bij de eerste persist(), en kijkt dan naar een
location.search die al leeg is.

Gevolg voor de meting: in tools/terugkomst.sh staat een kolom "bron" die precies bedoeld is om een
klik uit een tijdlijn te scheiden van een link die iemand je persoonlijk gaf, en die twee zitten
daar al die tijd op één hoop. En het is de hoop waarin de interessantste groep verstopt zit.

Nu wordt de herkomst bepaald op het moment dat de pagina opent, vóór het vegen, en een
uitnodigingslink krijgt zijn eigen herkomst in plaats van "direct".

## Bevinding 2: een uitnodiging draagt geen afzender

De link is ?groep=<gcode>. Daarmee weet de app in welke groep iemand terechtkomt, maar niet wie hem
gestuurd heeft. Bij twee mensen in een groep is dat nog af te leiden, bij drie niet meer, en een
generatie later helemaal niet.

Elke deelnemer krijgt nu een verwijscode: een los, kort, willekeurig kenmerk dat alleen dit kan
zeggen: "ik heb deze persoon binnengehaald". Bewust niet de sync-code, want daarmee geeft
GET /api/state/:code je hele voortgang weg, en een code die je in een WhatsApp-groep plakt mag dat
nooit kunnen. De link wordt ?groep=<gcode>&v=<verwijscode>.

De server legt het één keer vast en verandert het daarna niet meer; zie verwijzingVast() in
server/index.js. Wie eenmaal aan iemand hangt, blijft daar hangen, ook als hij later een andere
link opent.

## Wat je hiermee kunt zien, en wat niet

Wel: hoeveel generaties diep een uitnodiging draagt, hoe groot elke generatie is, en dus k
(hoeveel mensen levert een generatie op in de volgende). Ook: of mensen die via een uitnodiging
binnenkomen beter blijven hangen dan mensen van LinkedIn. Dat is de vraag die bepaalt of een
versterker de moeite waard is.

Niet: of iemand de app aan een ander heeft aanbevolen zonder de link te gebruiken. Dat blijft
onzichtbaar en dat is niet op te lossen.

Idempotent.
"""
import io, sys, os, re

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.105"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

DOE_APP = "v23.105" not in src
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


# ---------------------------------------------------------- bevinding 1 en 2: de herkomstblok
A_BRON = '''function bronNu(){
  try{
    var m = (location.search || "").match(/[?&]van=([a-z0-9_-]{1,16})/i);
    if(m) return m[1].toLowerCase();
    var r = document.referrer || "";
    if(!r) return "direct";
    var h = r.split("/")[2] || "";
    h = h.replace(/^www\\./, "").toLowerCase();
    if(!h || h === location.hostname) return "direct";
    return h.slice(0, 40);
  }catch(e){ return "direct"; }
}
try{
  if(typeof location !== "undefined" && location.search){
    var gm = location.search.match(/[?&]groep=([a-z0-9]+)/i);
    if(gm) pendingGroep = gm[1].toLowerCase();
    var dm = location.search.match(/[?&]duel=([a-z0-9]+)/i);
    if(dm) pendingDuel = dm[1].toLowerCase();'''
N_BRON = '''function bronNu(){
  try{
    var z = location.search || "";
    var m = z.match(/[?&]van=([a-z0-9_-]{1,16})/i);
    if(m) return m[1].toLowerCase();
    /* v23.105: een uitnodigingslink is een eigen herkomst en niet "direct". Een klik uit een
       tijdlijn is nieuwsgierigheid, een link die iemand je persoonlijk stuurt is een afspraak, en
       die twee horen in terugkomst.sh nooit op één hoop. */
    if(/[?&](groep|duel|v)=/i.test(z)) return "uitnodiging";
    var r = document.referrer || "";
    if(!r) return "direct";
    var h = r.split("/")[2] || "";
    h = h.replace(/^www\\./, "").toLowerCase();
    if(!h || h === location.hostname) return "direct";
    return h.slice(0, 40);
  }catch(e){ return "direct"; }
}
/* v23.105: hier zat de fout, en het was een volgorde. Het blok hieronder veegt de zoekreeks van de
   adresbalk zodra het een uitnodigingslink ziet, en dat gebeurt tijdens het inlezen van dit script.
   bronNu() draaide pas bij de eerste persist(), en keek dan naar een location.search die al leeg
   was. Nagemeten: ?groep=g1 leverde "direct" op, en ?groep=g1&van=linkedin ook.

   Twee dingen die ik hier eerst fout deed, allebei nagemeten in plaats van beredeneerd:

   1. Ik zette de herkomst in een `var` hierboven en las die in persist(). Dat werkt niet: persist()
      draait tijdens het laden al een keer vóór deze regel, en dan is die var nog undefined door
      hoisting. Dit is dezelfde val als de weekkaart van v23.95. Daarom nu een functie: een
      functiedeclaratie hoist compleet, dus persist() kan hem aanroepen wat de volgorde ook is.
   2. Ik bewaarde niets. Tussen "de link openen" en "een profiel hebben" zit van alles: rondkijken,
      de tab sluiten, terugkomen, herladen. En na het vegen hierboven staat er een schone adresbalk,
      dus bij een herlaadbeurt is de herkomst weg. Nagemeten: "uitnodiging" werd alsnog "direct".

   Alleen een echte herkomst wordt bewaard. "direct" is precies wat je ná zo'n herlaadbeurt meet, en
   dat mag het eerste bezoek niet overschrijven.

   Wat hier bewust niet gebeurt: de sleutel opruimen zodra hij bij een profiel staat. Ik heb dat
   geprobeerd en het brak precies het geval waarvoor het bedoeld was, want persist() draait ook als
   er nog helemaal geen profiel is. Het gevolg van laten staan: begint iemand op dezelfde telefoon
   later een tweede profiel, dan erft dat dezelfde herkomst. Dat is een kleine onnauwkeurigheid en
   die is het opruimen niet waard. */
function bronVast(){
  var sleutel = "vamos-bron-v1";   // met opzet hier en niet in een var erboven: zie punt 1
  try{ var b = localStorage.getItem(sleutel); if(b) return b; }catch(e){}
  var nu = "direct";
  try{ nu = bronNu(); }catch(e){}
  if(nu && nu !== "direct"){ try{ localStorage.setItem(sleutel, nu); }catch(e){} }
  return nu;
}
/* En hier meteen één keer aanroepen, vóór het vegen hieronder. Zonder deze regel wordt de herkomst
   pas vastgelegd bij de eerste persist(), en die komt er niet op het eerste scherm: nagemeten, wie
   een uitnodigingslink opent en rondkijkt zonder zich aan te melden slaat niets op, en na een
   herlaadbeurt is de link niet meer terug te vinden. */
try{ bronVast(); }catch(e){}
/* De verwijscode waarmee je hier binnenkwam: wie heeft je binnengehaald. Zelfde verhaal, zelfde
   twee redenen: bewaren omdat aanmelden later kan gebeuren, en een functie omdat syncUp() eerder
   kan draaien dan de regel die pendingVia vult. */
var pendingVia = null;
function viaNu(){
  if(pendingVia) return pendingVia;
  try{ return localStorage.getItem("vamos-via-v1") || null; }catch(e){ return null; }
}
try{
  if(typeof location !== "undefined" && location.search){
    var gm = location.search.match(/[?&]groep=([a-z0-9]+)/i);
    if(gm) pendingGroep = gm[1].toLowerCase();
    var dm = location.search.match(/[?&]duel=([a-z0-9]+)/i);
    if(dm) pendingDuel = dm[1].toLowerCase();
    var vm = location.search.match(/[?&]v=([a-z0-9]{6,24})/i);
    if(vm){
      pendingVia = vm[1].toLowerCase();
      try{ localStorage.setItem("vamos-via-v1", pendingVia); }catch(e){}
    }'''

A_STRIP = '''    if((gm || dm || bm) && window.history && history.replaceState) history.replaceState(null, "", location.pathname);'''
N_STRIP = '''    // v23.105: vm staat er nu bij, anders blijft de verwijscode in de adresbalk staan en deelt
    // iemand hem per ongeluk door alsof hij van hemzelf is.
    if((gm || dm || bm || vm) && window.history && history.replaceState) history.replaceState(null, "", location.pathname);'''

# ---------------------------------------------------------- persist gebruikt de gemeten herkomst
A_PERSIST = '''  if(S && !S.bron){ try{ S.bron = bronNu(); }catch(e){} }'''
N_PERSIST = '''  // v23.105: bronVast() in plaats van bronNu(). Die eerste onthoudt de herkomst van je eerste
  // bezoek; opnieuw meten levert hier "direct" op voor iedereen die via een uitnodiging binnenkwam,
  // want de zoekreeks is dan al van de adresbalk geveegd.
  if(S && !S.bron){ try{ S.bron = bronVast(); }catch(e){} }'''

# ---------------------------------------------------------- de verwijscode en de sync
A_SYNC = '''function syncUp(){
  var p = activeProfile();
  if(!p) return;
  api("/api/sync", "POST", {code: ensureCode(p), name: p.name, track: p.track, state: S})'''
N_SYNC = '''/* v23.105: je eigen verwijscode. Los van je sync-code, en dat is de hele reden dat hij bestaat:
   met een sync-code geeft GET /api/state/:code je hele voortgang weg, en dit is een code die je in
   een WhatsApp-groep plakt. Deze kan precies één ding, namelijk "ik heb deze persoon binnengehaald".
   Client-side gemaakt, net als de sync-code zelf; de server neemt hem aan als hij nog vrij is. */
function mijnVerwijsCode(){
  if(!S.rcode){ S.rcode = randCode(); persist(); }
  return S.rcode;
}
function syncUp(){
  var p = activeProfile();
  if(!p) return;
  api("/api/sync", "POST", {code: ensureCode(p), name: p.name, track: p.track, state: S,
                            rcode: mijnVerwijsCode(), via: viaNu()})'''

# ---------------------------------------------------------- de links dragen een afzender
A_GLINK = '''function groepLink(g){ return "https://vamos.stefanwobben.nl/?groep=" + g.gcode; }'''
N_GLINK = '''/* v23.105: &v= erbij. Zonder afzender weet de app wel in welke groep iemand terechtkomt maar niet
   wie hem stuurde, en dan is een tweede generatie niet van een eerste te onderscheiden. */
function groepLink(g){ return "https://vamos.stefanwobben.nl/?groep=" + g.gcode + "&v=" + mijnVerwijsCode(); }'''

A_DLINK = '''function duelLink(d){ return "https://vamos.stefanwobben.nl/?duel=" + d.id; }'''
N_DLINK = '''function duelLink(d){ return "https://vamos.stefanwobben.nl/?duel=" + d.id + "&v=" + mijnVerwijsCode(); }'''

if DOE_APP:
    ontbreekt = [n for n, a in (
        ("het herkomstblok", A_BRON), ("het vegen van de adresbalk", A_STRIP),
        ("de herkomstregel in persist", A_PERSIST), ("syncUp", A_SYNC),
        ("de groepslink", A_GLINK), ("de duellink", A_DLINK)) if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht; %s staat er niet zoals verwacht.\n"
              "Deze patch bouwt op v23.101. Eerst bijtrekken:\n\n    git pull --rebase\n" % ", ".join(ontbreekt))
        sys.exit(1)

    rep(A_BRON, N_BRON)
    rep(A_STRIP, N_STRIP)
    rep(A_PERSIST, N_PERSIST)
    rep(A_SYNC, N_SYNC)
    rep(A_GLINK, N_GLINK)
    rep(A_DLINK, N_DLINK)

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
