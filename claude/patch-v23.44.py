#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.44: de helling. Het aanmeldscherm vraagt je niveau niet meer, het vertelt het.

Stefan, 11 aug: "als je begint ben je misschien gemotiveerd en wil je wel iets meer woordjes doen.
Kunnen we dat ook zo vertellen, als soort van onboarding: je krijgt 30 woorden, dan schatten we je
niveau in." En daarna: "kunnen we er niet een geïntegreerde beleving van maken?"

## Waarom dertig, en niet twaalf

De app had al een peiling: twaalf woorden, "telt niet mee voor je punten". Maar PEIL_MIN_N staat op
20. Onder twintig antwoorden weigert niveauSchatting() iets te zeggen, en dan krijgt een vreemde op
zijn eerste dag letterlijk te lezen: "Bedankt. Nog 8 antwoorden en de balk kan je niveau schatten."
Een meting die weigert te meten, op precies de dag dat iemand het meest gemotiveerd is.

Dertig zit daar ruim boven. Daar mag de schatter spreken, mét Wilson-band en gokcorrectie.

## Waarom de helling niet adaptief is, en dat een keuze is en geen luiheid

De verleiding is een ladder die omhoog kruipt zolang je goed antwoordt. Dat mag hier niet, en de
reden is de wiskunde eronder: niveauSchatting() trekt een Wilson-interval om een steekproef, en een
Wilson-interval veronderstelt dat die steekproef aselect is. Een ladder die zijn vragen kiest op
grond van je vorige antwoorden levert precies geen aselecte steekproef, en dan is de band eromheen
een sier-interval dat niets meer betekent.

Dertig willekeurige A1-sleutels leveren vanzelf een mengeling van makkelijk (aprender) en lastig
(tímido), dus het voelt gevarieerd zonder dat de meting kapotgaat. De helling klimt in wat hij
oplevert, niet in wat hij vraagt.

## De blokkade die eerst weg moest

Vóór het eerste profiel staat WORDS op de kleine standaardbak van 313 woorden. peilMeetbaar() wil
tachtig procent dekking van de Cervantes-noemer, en A1 haalt daarmee twaalf procent. Er is dus vóór
het aanmelden geen enkel niveau meetbaar, en dat is precies het moment waarop we willen meten.
boot() vult WORDS pas nádat je een track hebt gekozen, en die keuze is nou juist wat we willen
wegnemen.

De helling laadt daarom zelf de ruime bak (dezelfde die de a2-track krijgt: 2184 woorden). Dan komt
A1 op 405 van de 409 sleutels en zijn er 405 kandidaten om uit te trekken.

Daarbij hoorde een tweede reparatie. pcicKeysApp() bewaart zijn uitkomst in _peilKeys, en boot()
verandert WORDS zonder die cache leeg te maken. Zolang niemand pcicKeysApp() vóór het aanmelden
aanriep viel dat niet op; vanaf nu roept de helling hem juist dán aan, dus zou de cache de rest van
de sessie op de verkeerde bak blijven staan. boot() maakt hem nu leeg.

## Wat er met je antwoorden gebeurt (de hybride)

- **Goed**: het woord krijgt `claim:1` in doosje SWEEP_BOX, gespreid over SWEEP_SPREIDING dagen.
  Dat is exact wat de inhaalslag (v23.8) doet. Het telt als voorsprong, niet als bewezen kennis, en
  zodra het woord voor het eerst echt wordt nagekeken verdwijnt de vlag en wordt in S.sweep geteld
  of jouw "die ken ik" klopte.
- **Fout of "geen idee"**: er gebeurt niets met S.srs. Het woord zit al in je leerlijn en komt daar
  vanzelf voorbij. Het bewust op doosje nul zetten zou het laten meetellen als "geoefend" terwijl je
  het alleen maar hebt gezien, en dat is de fout die claude/rapport.md punt 1 beschrijft.
- **Alle dertig** gaan als sleutel naar S.peil.items, dus de meting staat meteen op je
  voortgangspagina en de balk hoeft niet meer te zwijgen.

## Wat de oude weg doet

Die blijft heel. De drie vaste proefwoorden (viertalig), de vier niveauknoppen en de niveautest van
tien grammaticavragen werken alle drie onveranderd. De helling ligt eroverheen: hij begint na het
derde woord met de vraag of je doorgaat, en wie "nee" zegt komt uit op precies het scherm van
gisteren. Ook als de bak onverwacht niet meetbaar blijkt (helBankLaden() geeft dan false) valt alles
terug op de oude route. Bij het allereerste scherm, drie dagen voor een lancering, wil je die
terugvalweg hebben.

## Ook meegenomen: de minutenknop bleef niet staan

`.trackpick:not(.langpick)` selecteert ook de doelpick-knoppen, want die dragen allebei de klasse.
Een tik op een niveauknop haalde daardoor de actieve markering van je gekozen dagdoel af. De waarde
bleef goed (newMinuten verandert niet), maar het scherm liet zien dat er niets gekozen was. Dat
raakt dag 1 harder dan het lijkt: het dagdoel bepaalt je dagportie, en dus of het kruiswoord op dag
1 opengaat. De selector is nu `.trackpick[data-lvl]`.

Idempotent.
"""
import io, sys, os

WORTEL = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol")
PAD = os.path.join(WORTEL, "index.html")
PAD_VER = os.path.join(WORTEL, "versie.txt")

NIEUW = "v23.44"

with io.open(PAD, encoding="utf-8") as f:
    src = f.read()

# "Al gedaan" en "hier valt niets te doen" zijn niet hetzelfde, en dat betekent ook dat de
# ankercontrole pas mag lopen als er nog werk is. Anders meldt de tweede run "je repo loopt achter"
# over ankers die deze patch zelf heeft opgegeten, en dat is precies het verkeerde beeld.
DOE_APP = "function helBankLaden" not in src
with io.open(PAD_VER, encoding="utf-8") as f:
    huidig_ver = f.read().strip()
DOE_VER = huidig_ver != NIEUW

if not DOE_APP and not DOE_VER:
    print("al toegepast, niets te doen")
    sys.exit(0)

if DOE_APP:
    ANKERS = [
        'function renderProef(){',
        '  if(i >= PROEF_WOORDEN.length){',
        '  document.querySelectorAll(".trackpick:not(.langpick)").forEach(function(b){',
        '  if(!S.gestart && !(S.txp > 0)) S.gestart = today();',
        '  var pd0 = proefData();',
        '  CHEATSHEET = tr.cheat; BATCH = tr.batch;',
    ]
    ontbreekt = [a for a in ANKERS if a not in src]
    if ontbreekt:
        print("Deze index.html ziet er niet uit zoals verwacht. Ontbrekende ankers:\n  " +
              "\n  ".join(a[:70] for a in ontbreekt) +
              "\n\nEerst bijtrekken, dan pas patchen:\n\n    git pull --rebase\n")
        sys.exit(1)
    if 'var APP_VERSIE = "v23.43";' not in src:
        print("Deze index.html staat niet op v23.43. De helling bouwt op de poort van v23.43\n"
              "(een vers profiel met een lege S.speelOoit). Eerst die patch draaien.\n")
        sys.exit(1)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:200])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------- 1. versie ----------
    rep('var APP_VERSIE = "v23.43";', 'var APP_VERSIE = "%s";' % NIEUW)

    # ---------- 2. de cache van pcicKeysApp mag boot() niet overleven ----------
    rep('  CHEATSHEET = tr.cheat; BATCH = tr.batch;',
        '  CHEATSHEET = tr.cheat; BATCH = tr.batch;\n'
        '  /* v23.44: WORDS is hierboven vervangen, dus de sleutelkaart die pcicKeysApp() bewaart\n'
        '     hoort bij de vorige bak. Tot nu toe viel dat niet op omdat niemand hem vóór het\n'
        '     aanmelden aanriep; de helling doet dat juist wel, en dan zou de cache de rest van de\n'
        '     sessie op de kleine bak blijven staan. */\n'
        '  _peilKeys = null;')

    # ---------- 3. de helling ----------
    HELLING = r'''
/* ================= DE HELLING (v23.44) =================
   Het aanmeldscherm vroeg een vreemde naar zijn niveau. Dat is de enige vraag op dat scherm die hij
   niet kan beantwoorden: wie weet of hij A1 of A2 is, is niet de persoon die dit voor het eerst
   opent. De helling draait het om. Je doet dertig woorden, en dan vertelt de app het jou.

   Dertig is geen rond getal maar een ondergrens: PEIL_MIN_N staat op 20, en daaronder weigert
   niveauSchatting() te spreken. Met twaalf (de oude peiling) krijg je "nog 8 antwoorden en de balk
   kan je niveau schatten", oftewel een meting die niets meet op de dag dat iemand het meest wil.

   Niet adaptief, en dat is een keuze. niveauSchatting() legt een Wilson-band om de steekproef, en
   die band veronderstelt dat de steekproef aselect is. Een ladder die zijn volgende vraag kiest op
   grond van je vorige antwoord levert precies dat niet, en dan is de band sier. Dertig willekeurige
   A1-sleutels geven vanzelf makkelijk en lastig door elkaar. */
var HEL_N = 30;                         // antwoorden in de eerste ronde, inclusief de drie vaste
var HEL_VAST = PROEF_WOORDEN.length;    // die eerste drie zijn viertalig en staan vast
var helBankKlaar = false;

function helBankLaden(){
  /* Vóór het eerste profiel staat WORDS op de kleine standaardbak (313) en haalt A1 twaalf procent
     van de Cervantes-noemer, ruim onder de 80 die peilMeetbaar() eist. boot() vult WORDS pas nadat
     je een track hebt gekozen, en dat is de keuze die we hier juist wegnemen. Dus laden we hier
     dezelfde ruime bak die de a2-track ook krijgt: A1 komt dan op 405 van de 409 sleutels. */
  try {
    if(!helBankKlaar){
      WORDS = TRACKS.a2.words.concat(B_WORDS).concat(K_WORDS).concat(C_WORDS);
      _peilKeys = null;
      helBankKlaar = true;
    }
    return peilMeetbaar("A1");
  } catch(e){ return false; }
}

/* De vragen in één keer trekken, zoals peilStart() dat ook doet. Geschud, want de sleutelvolgorde
   van pcicKeysApp() is alfabetisch en dan krijgt iedereen dezelfde dertig.

   De uitsluitlijst is niet overbodig. peilKandidaten() slaat sleutels over die al in S.peil.items
   staan, maar één woord kan aan meer dan één sleutel hangen, en de drie vaste proefwoorden hangen
   sowieso buiten dat systeem. Zonder deze filter kreeg een vreemde "gracias" twee keer in dezelfde
   ronde: één keer als vast proefwoord en één keer uit de bak. */
function helVragen(n, weg){
  var kand = geschud(peilKandidaten("A1")), uit = [], gehad = {}, i, w;
  (weg || []).forEach(function(id){ gehad[id] = 1; });
  for(i = 0; i < kand.length && uit.length < n; i++){
    w = peilWoordVoor(pcicKeysApp()["A1"][kand[i]]);
    if(!w || gehad[w.id]) continue;
    gehad[w.id] = 1;
    uit.push({key:kand[i], id:w.id, es:w.es, goed:wTrans(w), opties:peilOpties(w)});
  }
  return uit;
}

// De drie vaste proefwoorden tellen mee waar ze een Cervantes-sleutel hebben (gracias heeft er een,
// hola en adiós niet). Weglaten zou de meting zuiverder lijken dan hij is: je hebt die vraag echt
// beantwoord.
function helVasteSleutels(){
  var mp = {}, uit = [];
  try { mp = pcicMap() || {}; } catch(e){ mp = {}; }
  PROEF_WOORDEN.forEach(function(w){
    var ks = mp[w.id];
    if(ks && ks.length) uit.push({id:w.id, key:ks[0]});
  });
  return uit;
}

/* De schatting. Alles gaat via S.peil.items, want dat is wat niveauSchatting() leest. Let op:
   persist() mag hier niet, want store.key staat vóór het aanmelden nog op de standaardsleutel en
   dan schrijf je in het profiel van een ander. De helling bewaart in zijn eigen blob. */
function helMeet(stand){
  if(!helBankLaden()) return null;
  try {
    S.peil = S.peil || {items:{}, log:[], laatst:""};
    S.peil.items = S.peil.items || {};
    var res = (stand && stand.items) || {}, k;
    for(k in res) S.peil.items[k] = {r:res[k], d:today(), niv:"A1"};
    return niveauSchatting("A1");
  } catch(e){ return null; }
}

/* Van schatting naar startpunt. POORT_PCT (0,85) is elders in de app al de grens waarop een niveau
   "staat"; die hergebruiken we hier, zodat één getal niet op twee plekken iets anders betekent. */
function helVoorstel(sch){
  if(!sch || !sch.noem) return {track:"beginner", lvl:"A1", zeker:false};
  var p = sch.punt / sch.noem;
  if(p >= POORT_PCT) return {track:"a2", lvl:"A2", zeker:true};
  if(p >= 0.2)       return {track:"beginner", lvl:"A1", zeker:true};
  return {track:"beginner", lvl:"A0", zeker:true};
}

var HEL_TXT = {
 nl:{door:"Nog even door? Dan weten we straks waar je staat.", doorJa:"Ja, laat maar komen →",
     doorNee:"Nee, ik maak gewoon een profiel", vraag:"Wat betekent dit?", geen:"Geen idee",
     klaarKop:"Klaar. En nu weten we iets.", stop:"Genoeg voor nu",
     hoeveel:function(r,n){ return "Je herkende "+r+" van de "+n+" woorden."; },
     genoeg:"Genoeg om te zien waar je staat.",
     start:function(l){ return "Je begint op "+l+"."; },
     later:"De volledige schatting, met marge eromheen, staat straks op je voortgangspagina.",
     geenBand:"Nog te weinig antwoorden om er iets over te zeggen. Kies zelf maar even.",
     door2:"Verder →", zelf:"Ik kies liever zelf"},
 en:{door:"Keep going? Then we will know where you stand.", doorJa:"Yes, bring them on →",
     doorNee:"No, just make me a profile", vraag:"What does this mean?", geen:"No idea",
     klaarKop:"Done. And now we know something.", stop:"Enough for now",
     hoeveel:function(r,n){ return "You recognised "+r+" of the "+n+" words."; },
     genoeg:"Enough to see where you stand.",
     start:function(l){ return "You start at "+l+"."; },
     later:"The full estimate, with its margin, will be on your progress page.",
     geenBand:"Too few answers to say anything about it. Pick one yourself.",
     door2:"Continue →", zelf:"I would rather choose myself"}
};
function helTxt(){ var L = proefTaal(); return HEL_TXT[L] || HEL_TXT.en; }
'''
    rep("function renderProef(){", HELLING.lstrip("\n") + "\nfunction renderProef(){")

    # ---------- 4. renderProef: na de derde vraag houdt het niet meer op ----------
    OUD_KLAAR = '''  if(i >= PROEF_WOORDEN.length){
    box.innerHTML = "<div style='text-align:center'><div style='width:130px; margin:0 auto'>"+petSVG()+"</div>"+
      "<h2 style='margin:8px 0 4px'>"+d.klaarKop+"</h2>"+
      "<p class='muted'>+"+proefStand.xp+" "+xpw()+" · "+d.klaarSub+"</p>"+
      "<div class='row center'><button class='primary' id='btnProefDoor'>"+d.bewaar+"</button></div></div>";
    var bd = document.getElementById("btnProefDoor");
    if(bd) bd.onclick = function(){
      proefBewaar({klaar:true, xp:proefStand.xp, res:proefStand.res});
      box.classList.add("hidden");
      card.classList.remove("hidden");
      var nn = document.getElementById("newProfName");
      if(nn) nn.focus();
    };
    return;
  }'''

    NIEUW_KLAAR = '''  if(i >= PROEF_WOORDEN.length){
    /* v23.44: hier hield het op na drie woorden en werd je naar een formulier gestuurd dat je
       niveau vroeg. Nu is dit een tussenstand: de helling biedt aan om door te gaan, en pas na
       dertig antwoorden weet de app genoeg om je niveau te vertellen in plaats van te vragen.
       De oude weg blijft er: "nee" komt uit op precies het scherm van hiervoor, en een bak die
       onverwacht niet meetbaar is doet hetzelfde. */
    var h = helTxt();
    if(!proefStand.helKlaar && proefStand.helAan !== false && helBankLaden()){
      if(!proefStand.hel){
        /* Eerst de vaste woorden wegschrijven, dan pas trekken. peilKandidaten() slaat sleutels
           over die al in S.peil.items staan, dus deze volgorde voorkomt dat "gracias" twee keer in
           dezelfde ronde langskomt. */
        proefStand.items = proefStand.items || {};
        S.peil = S.peil || {items:{}, log:[], laatst:""};
        S.peil.items = S.peil.items || {};
        helVasteSleutels().forEach(function(v){
          if(proefStand.res[v.id] === undefined) return;
          proefStand.items[v.key] = proefStand.res[v.id] ? 1 : 0;
          S.peil.items[v.key] = {r:proefStand.items[v.key], d:today(), niv:"A1"};
        });
        proefStand.hel = helVragen(HEL_N - HEL_VAST, PROEF_WOORDEN.map(function(w){ return w.id; }));
      }
      if(proefStand.hel.length >= 4 && !proefStand.helGestart){
        box.innerHTML = "<div style='text-align:center'><div style='width:130px; margin:0 auto'>"+petSVG()+"</div>"+
          "<h2 style='margin:8px 0 4px'>"+d.klaarKop+"</h2>"+
          "<p class='muted'>+"+proefStand.xp+" "+xpw()+"</p>"+
          "<p style='margin:10px 0 12px'>"+h.door+"</p>"+
          "<div class='row center'><button class='primary' id='btnHelJa'>"+h.doorJa+"</button></div>"+
          "<p class='muted' style='margin-top:10px'><a href='#' id='lnkHelNee'>"+h.doorNee+"</a></p></div>";
        var bj = document.getElementById("btnHelJa");
        if(bj) bj.onclick = function(){ proefStand.helGestart = true; proefStand.helI = 0; renderProef(); };
        var ln = document.getElementById("lnkHelNee");
        if(ln) ln.onclick = function(e){
          if(e && e.preventDefault) e.preventDefault();
          proefStand.helAan = false; renderProef(); return false;
        };
        return;
      }
      if(proefStand.helGestart && proefStand.helI < proefStand.hel.length){ return helVraagRender(box, d, h); }
      if(proefStand.helGestart){ proefStand.helKlaar = true; return helUitslagRender(box, h); }
    }
    if(proefStand.helKlaar) return helUitslagRender(box, h);
    box.innerHTML = "<div style='text-align:center'><div style='width:130px; margin:0 auto'>"+petSVG()+"</div>"+
      "<h2 style='margin:8px 0 4px'>"+d.klaarKop+"</h2>"+
      "<p class='muted'>+"+proefStand.xp+" "+xpw()+" · "+d.klaarSub+"</p>"+
      "<div class='row center'><button class='primary' id='btnProefDoor'>"+d.bewaar+"</button></div></div>";
    var bd = document.getElementById("btnProefDoor");
    if(bd) bd.onclick = function(){
      proefBewaar({klaar:true, xp:proefStand.xp, res:proefStand.res, items:proefStand.items || {}});
      box.classList.add("hidden");
      card.classList.remove("hidden");
      var nn = document.getElementById("newProfName");
      if(nn) nn.focus();
    };
    return;
  }'''
    rep(OUD_KLAAR, NIEUW_KLAAR)

    # ---------- 5. de vraag- en uitslagschermen van de helling ----------
    HEL_SCHERMEN = r'''
/* De vraag zelf. Bewust dezelfde vorm als het proefscherm ervoor: je merkt de overgang van de drie
   vaste woorden naar de bak niet, en dat is het punt van "één beleving". */
function helVraagRender(box, d, h){
  var v = proefStand.hel[proefStand.helI];
  var nr = HEL_VAST + proefStand.helI + 1;
  var gekozen = proefStand.helGekozen;
  var knoppen = v.opties.map(function(o){
    var cls = "opt";
    if(gekozen !== undefined && gekozen !== null){
      if(o === v.goed) cls = "opt good";
      else if(o === gekozen) cls = "opt bad";
    }
    return "<button type='button' class='"+cls+"' data-hel=\"" + o.replace(/"/g, "&quot;") +
      "\" style='margin:4px 0'>"+o+"</button>";
  }).join("");
  box.innerHTML = "<span class='kicker'>¡Vamos! · "+nr+"/"+HEL_N+"</span>"+
    "<div class='progressbar'><div style='width:"+Math.round(100 * (nr - 1) / HEL_N)+"%'></div></div>"+
    "<p style='font-size:1.7rem; margin:10px 0 2px; text-align:center'><b class='es'>"+v.es+"</b></p>"+
    "<p class='muted' style='margin:0 0 10px; text-align:center'>"+h.vraag+"</p>"+
    knoppen+
    "<button type='button' class='ghost' id='btnHelGeen' style='margin-top:8px; width:100%'>"+h.geen+"</button>"+
    "<p class='muted' style='margin-top:12px; text-align:center'><a href='#' id='lnkHelStop'>"+h.stop+"</a></p>";
  if(gekozen !== undefined && gekozen !== null) return;
  function antwoord(keuze){
    if(proefStand.helGekozen !== undefined && proefStand.helGekozen !== null) return;
    proefStand.helGekozen = (keuze === null ? "" : keuze);
    proefStand.items = proefStand.items || {};
    proefStand.items[v.key] = (keuze === null ? -1 : (keuze === v.goed ? 1 : 0));
    if(keuze === v.goed){ proefStand.helGoed = (proefStand.helGoed || 0) + 1; proefStand.xp += 2; }
    else proefStand.xp += 1;
    // Bewaren na elk antwoord. Dertig vragen is lang genoeg dat een per ongeluk ververste pagina
    // echt pijn doet, en dit kost één regel.
    proefBewaar({bezig:true, xp:proefStand.xp, res:proefStand.res, items:proefStand.items, stand:proefStand});
    helVraagRender(box, d, h);
    setTimeout(function(){
      if(!proefStand) return;
      proefStand.helGekozen = null;
      proefStand.helI++;
      renderProef();
    }, 700);
  }
  box.querySelectorAll("[data-hel]").forEach(function(b){
    b.onclick = function(){ antwoord(b.getAttribute("data-hel")); };
  });
  var bg = document.getElementById("btnHelGeen");
  if(bg) bg.onclick = function(){ antwoord(null); };
  var ls = document.getElementById("lnkHelStop");
  if(ls) ls.onclick = function(e){
    if(e && e.preventDefault) e.preventDefault();
    proefStand.helKlaar = true; renderProef(); return false;
  };
}

/* De uitslag. Drie regels: wat je deed, dat het genoeg was, waar je begint.

   Wat hier bewust NIET staat is de puntschatting ("ongeveer 195 van de 409 A1-woorden"). Die was er
   eerst, en hij was fout op de manier die claude/rapport.md maatstaf 1 beschrijft: vóór het
   aanmelden rekent de schatter over de ruime bak (405 van de 409 A1-sleutels), en meteen na het
   aanmelden over de bak van jouw track (371). Zelfde vraag, zelfde persoon, twee getallen, twee
   schermen na elkaar. Gemeten: 195 hier, 182 daar. Het tweede ligt netjes binnen de marge van het
   eerste, dus het spreekt elkaar niet tegen, maar dat weet de lezer niet: die ziet een getal
   veranderen tussen twee schermen door.

   Wat je hier wél kunt zeggen verandert niet: hoeveel van de woorden die je zag je herkende. Dat is
   een telling en geen schatting. De volledige schatting hoort op de voortgangspagina, waar hij één
   keer wordt uitgerekend en met marge staat. */
function helUitslagRender(box, h){
  var sch = helMeet(proefStand);
  var voorstel = helVoorstel(sch);
  // Alles wat je hebt beantwoord telt, ook de twee vaste proefwoorden zonder Cervantes-sleutel.
  // De meting gaat over de sleutels; deze regel gaat over jouw ronde, en die was dertig lang.
  var n = HEL_VAST + (proefStand.helI || 0);
  var goed = (proefStand.helGoed || 0);
  PROEF_WOORDEN.forEach(function(w){ if(proefStand.res[w.id]) goed++; });
  proefStand.voorstel = voorstel;
  var body = "<p class='big' style='margin:8px 0 4px'>"+h.hoeveel(goed, n)+"</p>";
  if(sch) body += "<p class='muted' style='margin:0 0 8px'>"+h.genoeg+"</p>"+
                  "<p class='big' style='margin:8px 0 2px'>"+h.start(voorstel.lvl)+"</p>"+
                  "<p class='muted' style='margin:6px 0 0; font-size:.85rem'>"+h.later+"</p>";
  else body += "<p class='muted' style='margin:0 0 8px'>"+h.geenBand+"</p>";
  box.innerHTML = "<div style='text-align:center'><div style='width:130px; margin:0 auto'>"+petSVG()+"</div>"+
    "<h2 style='margin:8px 0 4px'>"+h.klaarKop+"</h2>"+body+
    "<div class='row center'><button class='primary' id='btnHelVerder'>"+h.door2+"</button></div>"+
    "<p class='muted' style='margin-top:10px'><a href='#' id='lnkHelZelf'>"+h.zelf+"</a></p></div>";
  function verder(metVoorstel){
    proefBewaar({klaar:true, xp:proefStand.xp, res:proefStand.res, items:proefStand.items || {},
                 voorstel:(metVoorstel ? voorstel : null)});
    box.classList.add("hidden");
    var card = document.getElementById("profCard");
    if(card) card.classList.remove("hidden");
    if(metVoorstel && sch) helVoorstelToepassen(voorstel);
    var nn = document.getElementById("newProfName");
    if(nn) nn.focus();
  }
  var bv = document.getElementById("btnHelVerder");
  if(bv) bv.onclick = function(){ verder(true); };
  var lz = document.getElementById("lnkHelZelf");
  if(lz) lz.onclick = function(e){ if(e && e.preventDefault) e.preventDefault(); verder(false); return false; };
}

// Het aanmeldscherm staat nu op het voorstel in plaats van op niets. De vier knoppen blijven staan
// en blijven aanklikbaar: dit is een voorstel, geen uitspraak.
function helVoorstelToepassen(v){
  try {
    newTrack = v.track;
    document.querySelectorAll(".trackpick[data-lvl]").forEach(function(x){
      x.classList.toggle("active", x.getAttribute("data-lvl") === v.lvl);
    });
    var r = document.getElementById("helRegel");
    if(r){
      r.textContent = (proefTaal() === "nl")
        ? "Op grond van je woorden zetten we je op "+v.lvl+". Klopt dat niet? Kies hieronder zelf."
        : "Based on your words we put you at "+v.lvl+". Not right? Pick your own below.";
      r.classList.remove("hidden");
    }
  } catch(e){}
}
'''
    rep("function renderDoelRow(){", HEL_SCHERMEN.lstrip("\n") + "\nfunction renderDoelRow(){")

    # ---------- 6. proefStand overleeft een ververste pagina ----------
    rep("  if(!proefStand) proefStand = {i:0, xp:0, res:{}};",
        "  if(!proefStand){\n"
        "    // v23.44: dertig vragen is lang genoeg dat een per ongeluk ververste pagina pijn doet,\n"
        "    // dus de helling schrijft na elk antwoord zijn stand weg en pakt hem hier weer op.\n"
        "    var bew = proefData();\n"
        "    proefStand = (bew && bew.bezig && bew.stand) ? bew.stand : {i:0, xp:0, res:{}};\n"
        "  }")

    # ---------- 7. de regel boven de niveauknoppen ----------
    rep('      <h2 id="profNieuwKop" style="margin-top:18px">Nieuw profiel</h2>',
        '      <h2 id="profNieuwKop" style="margin-top:18px">Nieuw profiel</h2>\n'
        '      <p id="helRegel" class="muted hidden" style="margin:2px 0 8px"></p>')

    # ---------- 8. een niveauknop mag je dagdoel niet ontselecteren ----------
    # .trackpick zit ook op de doelpick-knoppen. Een tik op een niveau haalde daardoor de actieve
    # markering van je gekozen aantal minuten af. De waarde bleef goed, het scherm loog.
    rep('  document.querySelectorAll(".trackpick:not(.langpick)").forEach(function(b){\n'
        '    b.onclick = function(){\n'
        '      newTrack = b.getAttribute("data-track");\n'
        '      document.querySelectorAll(".trackpick:not(.langpick)").forEach(function(x){ x.classList.toggle("active", x===b); });',
        '  document.querySelectorAll(".trackpick[data-lvl]").forEach(function(b){\n'
        '    b.onclick = function(){\n'
        '      newTrack = b.getAttribute("data-track");\n'
        '      /* v23.44: hier stond .trackpick:not(.langpick), en die selector pakt ook de\n'
        '         doelpick-knoppen, want die dragen dezelfde klasse. Een tik op een niveau haalde zo\n'
        '         de markering van je gekozen dagdoel weg. newMinuten bleef goed, maar het scherm\n'
        '         zei dat je niets gekozen had, en dat dagdoel bepaalt je dagportie. */\n'
        '      document.querySelectorAll(".trackpick[data-lvl]").forEach(function(x){ x.classList.toggle("active", x===b); });')

    # ---------- 9. verzilveren bij het aanmelden ----------
    OUD_VERZILVER = '''    var res0 = pd0.res || {};
    PROEF_WOORDEN.forEach(function(w){
      if(res0[w.id] === undefined) return;
      if(!S.srs[w.id]) S.srs[w.id] = {box: res0[w.id]?1:0, due: res0[w.id]?addDays(today(),1):today(), n:1, f: res0[w.id]?0:1};
    });
    proefWis();'''

    NIEUW_VERZILVER = '''    var res0 = pd0.res || {};
    PROEF_WOORDEN.forEach(function(w){
      if(res0[w.id] === undefined) return;
      if(!S.srs[w.id]) S.srs[w.id] = {box: res0[w.id]?1:0, due: res0[w.id]?addDays(today(),1):today(), n:1, f: res0[w.id]?0:1};
    });
    /* v23.44: en de helling. De sleutels gaan naar S.peil.items, zodat de meting meteen op je
       voortgangspagina staat en de balk niet hoeft te zwijgen (PEIL_MIN_N is 20, de helling levert
       er dertig). Woorden die je goed had krijgen claim:1 in doosje SWEEP_BOX, precies zoals de
       inhaalslag ze zet: een voorsprong, geen bewijs. Zodra zo'n woord voor het eerst echt wordt
       nagekeken verdwijnt de vlag en telt S.sweep of jouw "die ken ik" klopte.

       Wat je fout had gaat bewust NIET in S.srs. Die woorden zitten al in je leerlijn en komen daar
       vanzelf voorbij; ze hier op doosje nul zetten zou ze laten meetellen als "geoefend" terwijl je
       ze alleen maar hebt gezien, en dat is de fout uit claude/rapport.md punt 1. */
    var items0 = pd0.items || {}, kh;
    S.peil = S.peil || {items:{}, log:[], laatst:""};
    for(kh in items0) if(!S.peil.items[kh]) S.peil.items[kh] = {r:items0[kh], d:today(), niv:"A1"};
    if(pd0.hel && pd0.hel.length){
      var iz = 0;
      pd0.hel.forEach(function(v){
        if(!v || items0[v.key] !== 1) return;
        if(S.srs[v.id]) return;
        S.srs[v.id] = {box: SWEEP_BOX, due: addDays(today(), 1 + (iz % SWEEP_SPREIDING)), n:0, claim:1};
        iz++;
      });
      if(iz){
        S.sweep = S.sweep || {dag: today(), ken: 0, niet: 0, goed: 0, fout: 0};
        S.sweep.ken = (S.sweep.ken || 0) + iz;
      }
    }
    proefWis();'''
    rep(OUD_VERZILVER, NIEUW_VERZILVER)

    # De uitslag moet de gestelde vragen meegeven, anders weet boot() niet welk woord bij welke
    # sleutel hoorde en kan hij niets verzilveren.
    rep('''    proefBewaar({klaar:true, xp:proefStand.xp, res:proefStand.res, items:proefStand.items || {},
                 voorstel:(metVoorstel ? voorstel : null)});''',
        '''    proefBewaar({klaar:true, xp:proefStand.xp, res:proefStand.res, items:proefStand.items || {},
                 hel:(proefStand.hel || []), voorstel:(metVoorstel ? voorstel : null)});''')

    with io.open(PAD, "w", encoding="utf-8") as f:
        f.write(src)
    print("index.html gepatcht naar %s" % NIEUW)
else:
    print("index.html was al gepatcht")

# Eigen vlag per bestand: "index.html was al klaar" zegt niets over versie.txt (DEPLOY.md).
if DOE_VER:
    with io.open(PAD_VER, "w", encoding="utf-8") as f:
        f.write(NIEUW + "\n")
    print("versie.txt op %s" % NIEUW)
else:
    print("versie.txt stond al op %s" % NIEUW)
