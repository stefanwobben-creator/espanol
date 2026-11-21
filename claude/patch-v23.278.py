# patch-v23.278.py - het kale doosje mag een onderwerp niet levenslang vasthouden, en de regel
#                    komt terug bij elke herhaling.
#
# WAT STEFAN SCHREEF
#
# 21 november: "ik heb het idee dat er niet veel nieuwe content bij komt en dat grammatica beetje
# blijft hangen. Zoek uit of er wel progressie wordt gemeten maar het gewoon langzaam gaat. Ik denk
# dat ik meer verschillende soorten grammatica zou moeten oefenen maar vooral ook iedere keer weer
# uitleg dan toetsen."
#
# WAT DE METING ZEI (claude/stefan-gram.json, door de app zelf heen gehaald)
#
# Er wordt wel degelijk gemeten en er beweegt iets: 69 doosjes op 30 september, 96 op 21 november,
# 732 antwoorden tegen 1011, doos 5 van 11 naar 18. Maar de dagles bood die hele periode twee
# onderwerpen aan, en een daarvan was bijna altijd hetzelfde:
#
#     genero   249 antwoorden
#              #0 doos 5   #1 doos 5   #2 doos 5   #3 doos 5   #4 doos 5
#              kaal doos 1
#
# gramLees() beoordeelt een onderwerp op zijn ZWAKSTE doosje. Dat is een goede regel: je kent el of
# la pas als je de val ook kent. Maar het kale doosje is geen patroon. Het is de plek waar fouten
# landen die je in het wild maakt, want de losse oefenzin, de chatcorrector, het toetsje en de
# clasificador roepen gramBij() aan zonder patroonnummer. En de microles schrijft naar de
# patroondoosjes. Het kale doosje krijgt dus nooit gerichte oefening en kan alleen omlaag.
#
#     Een doosje dat alleen omlaag kan, mag niet beslissen of iets af is.
#
# Gevolg: gcFocusKlaar("genero") las doos 1, genero verliet de focus nooit en hield een van de twee
# plekken permanent bezet. In de tijdreeks van zijn logboek komt genero terug op 13 van de 17 dagen
# waarop hij grammatica deed. Ondertussen: 30 onderwerpen open, 68 doosjes toe, 85 van de 153
# patronen nooit gezien.
#
# DRIE DINGEN, EN WAAROM ZE BIJ ELKAAR HOREN
#
#   EEN. Het oordeel komt van de patroondoosjes als die er zijn. Het kale doosje houdt precies de
#   taak die het hoort te hebben: een verse fout in het wild brengt het onderwerp dezelfde week
#   terug (gcStaatFout). Het blokkeert alleen niet langer de voortgang. Nagerekend op zijn
#   gegevens: genero komt vrij en de focus schuift naar serestar. Een onderwerp, niet tien; de rest
#   zit echt vast op zijn patronen en niet op een boekhoudfout. Dat hoort erbij te staan, anders
#   belooft deze ronde meer dan hij levert.
#
#   TWEE. De regel komt terug bij elke herhaling. Nu ziet hij de uitleg van een onderwerp precies
#   een keer, bij de kennismaking: gwOpfrisInPlaats() vervangt een afgerond onderwerp door een
#   opfrisser, en die heeft geen uitlegscherm. Vanaf nu heeft de opfrisser twee stappen, met de
#   regel ertussen.
#
#   Niet ervoor, en dat is het enige punt waarop deze ronde hem tegenspreekt. Uitleg vlak voor de
#   toets meet of je net gelezen hebt en niet of je het weet (Kornell en Bjork, illusions of
#   competence); dit bestand citeert dat zelf al als reden waarom de drill niet meetelt voor het
#   doosje (v23.261). Dus: eerst de vragen, dan de regel, dan nog een vraag.
#
#   En het wordt niet langer. De vragen worden gesplitst, er komen er geen bij.
#
#   DRIE. Meer verschillende onderwerpen per dag, uit het onderhoudsbudget en niet uit de focus.
#   Die twee focusplekken heeft Stefan zelf afgedwongen (v23.234, "dwing dit meer af") en die zijn
#   voor wat hij aan het verwerven is. De breedte hoort bij de andere helft van de splitsing van
#   v23.235, en die leverde een doosje per dag terwijl er achtenzestig toe stonden.
#
#   Drie onderhoudsbeurten in plaats van een, en elk korter: twee vragen in plaats van vijf. Het is
#   onderhoud op iets dat al op doos 3 of hoger staat, en daar is vijf vragen te veel van het
#   goede. De dag wordt daarmee een vraag langer en drie onderwerpen breder.
#
# WAT DIT NIET DOET
#
# Dit maakt geen enkel onderwerp makkelijker en verlaagt geen enkele eis. De doosregel blijft zoals
# hij is: een misser op een dag kost de promotie. Wat verandert is welk doosje gevraagd wordt of
# het onderwerp af is.
import pathlib
import sys

W = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / "claude"))
import patchhulp  # noqa: E402

APP = W / "index.html"
VER = W / "versie.txt"
GEPLAND = "v23.278"

src = APP.read_text(encoding="utf-8")
huidig = VER.read_text(encoding="utf-8").strip()
DOE_APP = "GRAM_ONDERHOUD_N" not in src


def rep(anker, nieuw, n=1):
    global src
    c = src.count(anker)
    assert c == n, "anker %d keer (verwacht %d): %r" % (c, n, anker[:110])
    src = src.replace(anker, nieuw, n)


if DOE_APP:
    # ---------------- EEN: het oordeel komt van de patroondoosjes ----------------
    rep(
        r'''  var d = gramDoosjes(s);
  if(!d.length) return {box:0, due:"", goed:0, fout:0, laatst:""};
  var zwak = null, goed = 0, fout = 0, laatst = "";
  d.forEach(function(x){
    var st = x.st;
    goed += st.goed || 0;
    fout += st.fout || 0;
    if((st.laatst || "") > laatst) laatst = st.laatst || "";
    if(!zwak
       || (st.box || 0) < (zwak.box || 0)
       || ((st.box || 0) === (zwak.box || 0) && (st.due || "") < (zwak.due || ""))) zwak = st;
  });
  return {box: zwak.box || 0, due: zwak.due || "", half: zwak.half || 0, bd: zwak.bd || "",
          goed: goed, fout: fout, laatst: laatst, doosjes: d.length};''',
        r'''  var d = gramDoosjes(s);
  if(!d.length) return {box:0, due:"", goed:0, fout:0, laatst:""};
  /* v23.278: het OORDEEL komt van de patroondoosjes, de TELLERS van allemaal.

     Het kale doosje is geen patroon. Het is de plek waar fouten landen die je in het wild maakt:
     een losse oefenzin, de chatcorrector, een toetsje, de clasificador. Die roepen gramBij() aan
     zonder patroonnummer. De microles schrijft naar de patroondoosjes, dus het kale doosje krijgt
     nooit gerichte oefening en kan alleen omlaag.

     Gemeten bij Stefan op 20 november: genero heeft 249 antwoorden, alle vijf de patronen staan op
     doos 5 met 93 tot 100 procent goed, en het kale doosje staat op doos 1. Omdat deze functie het
     zwakste doosje teruggaf, gold genero als onaf en hield het weken een van de twee focusplekken
     bezet. Op 13 van de 17 dagen waarop hij grammatica deed, kwam genero terug.

         Een doosje dat alleen omlaag kan, mag niet beslissen of iets af is.

     Wat NIET verandert: de zwakste-regel zelf. Binnen de patronen geldt hij onverkort, want je
     kent el of la pas als je de val ook kent. En het kale doosje verdwijnt niet: het gaat mee in
     de tellers, het staat als kaalBox in de uitkomst, en gcStaatFout() gebruikt dat om een verse
     fout in het wild dezelfde week terug te brengen. Het mag alleen niets meer blokkeren.

     Heeft een onderwerp helemaal geen patroondoosjes (de handgeschreven wizards, en alles wat je
     alleen in het wild bent tegengekomen), dan is het kale doosje het enige bewijs dat er is en
     telt het gewoon mee. */
  var oordeel = d.filter(function(x){ return x.pi !== null; });
  if(!oordeel.length) oordeel = d;
  var zwak = null, goed = 0, fout = 0, laatst = "", kaalBox = null;
  d.forEach(function(x){
    var st = x.st;
    goed += st.goed || 0;
    fout += st.fout || 0;
    if((st.laatst || "") > laatst) laatst = st.laatst || "";
    if(x.pi === null) kaalBox = st.box || 0;
  });
  oordeel.forEach(function(x){
    var st = x.st;
    if(!zwak
       || (st.box || 0) < (zwak.box || 0)
       || ((st.box || 0) === (zwak.box || 0) && (st.due || "") < (zwak.due || ""))) zwak = st;
  });
  return {box: zwak.box || 0, due: zwak.due || "", half: zwak.half || 0, bd: zwak.bd || "",
          goed: goed, fout: fout, laatst: laatst, doosjes: d.length, kaalBox: kaalBox};''')

    # ---------------- EEN-B: en de verse fout in het wild komt nog steeds terug ----------------
    rep(
        r'''function gcStaatFout(st, cid){
  if(!st || !cid) return false;
  if((st.box || 0) !== 0) return false;
  return gcVersFout(cid);
}''',
        r'''function gcStaatFout(st, cid){
  if(!st || !cid) return false;
  if(!gcVersFout(cid)) return false;
  if((st.box || 0) === 0) return true;
  /* v23.278: en het kale doosje ook, want dat is precies waar een fout in het wild landt. Sinds
     gramLees() het oordeel van de patroondoosjes afleidt, zou een onderwerp waarvan alle patronen
     op doos 5 staan niet meer terugkomen van een slordigheid in een vrije zin. Dat is de helft van
     de taak van dat doosje, en die helft blijft. */
  return st.kaalBox === 0;
}''')

    # ---------------- TWEE: de regel terug in elke herhaling ----------------
    rep(
        r'''var GC_OPFRIS_VRAGEN = 5;''',
        r'''var GC_OPFRIS_VRAGEN = 5;
/* v23.278: en zoveel als het doosje al op onderhoud staat (doos 3 of hoger). Dat is dezelfde regel
   als bij GC_OPFRIS_LES_VRAGEN hieronder, alleen de andere kant op: de maat hangt aan het doosje
   en niet aan de naam van het onderdeel. Vijf vragen over iets wat je al kunt is geen onderhoud
   maar een les, en het kost de plek van drie andere onderwerpen. */
var GC_OPFRIS_ONDERHOUD = 2;''')

    rep(
        '''      };
    }
  }
  return {''',
        r'''      };
    }
  }
  /* ================= DE REGEL KOMT TERUG BIJ ELKE HERHALING (v23.278) =================

     Stefan, 21 november: "vooral ook iedere keer weer uitleg dan toetsen, (zou nou uitleg goed
     moeten gaan) maar omdat het vaak wordt herhaald zal het beklijven is mijn idee."

     Hij ziet de uitleg van een onderwerp op dit moment precies EEN keer. gwOpfrisInPlaats()
     (v23.172) vervangt een afgerond onderwerp door deze opfrisser, en die had een stap met
     uitleg:"" en verder niets dan vragen. De regel zelf (c.uitleg) kwam daarna nooit meer langs.

     Vanaf nu twee stappen, met de regel ertussen. Niet ervoor, en dat is het enige punt waarop
     deze ronde hem tegenspreekt: uitleg vlak voor de toets meet of je net gelezen hebt en niet of
     je het weet (Kornell en Bjork). Dit bestand citeert dat zelf al als de reden waarom de drill
     niet meetelt voor het doosje (v23.261). Dus eerst ophalen, dan de regel, dan nog een keer
     toepassen.

     En het wordt niet langer: dezelfde vragen, alleen gesplitst. De laatste gaat achter de regel.

     DE LENGTE HANGT AAN HET DOOSJE, net als hierboven bij de terugval-variant:

         doos 0 met genoeg geschiedenis  ->  de regel eerst, een begripsvraag, vier toepassingen
         doos 1 of 2                     ->  vier vragen, de regel, nog een vraag
         doos 3 of hoger (onderhoud)     ->  een vraag, de regel, nog een vraag

     Die laatste is nieuw en hoort bij de derde helft van deze ronde: de dagles biedt er drie van
     aan in plaats van een, dus ze moeten kort zijn. */
  var onderhoud = !!doosje && (doosje.box || 0) >= GRAM_ONDERHOUD_DOOS;
  var reeks = vragen.slice(0, onderhoud ? GC_OPFRIS_ONDERHOUD : GC_OPFRIS_VRAGEN);
  var regelTekst = String(ct(c.uitleg, c.uitlegEn || c.uitleg) || "").trim();
  var voor = reeks.slice(0, Math.max(1, reeks.length - 1));
  var na = reeks.slice(voor.length);
  var icoon = c.icon || "\ud83d\udd01";
  var kop1 = onderhoud ? ct("Nog steeds goed?", "Still good?") : ct("Even opfrissen", "Quick refresher");
  var titel1 = onderhoud ? ct("Onderhoud: " + naam, "Upkeep: " + naam)
                         : ct("Even opfrissen: " + naam, "Quick refresher: " + naam);
  var pitch1 = ct(reeks.length + " vragen, met de regel er tussendoor.",
                  reeks.length + " questions, with the rule in between.");
  if(regelTekst && na.length){
    return {
      icon: icoon,
      id: id, concept: cid, opfris: true, onderhoud: onderhoud,
      titel: titel1,
      titelEn: (onderhoud ? "Upkeep: " : "Quick refresher: ") + (c.naamEn || c.naam),
      pitch: pitch1,
      pitchEn: reeks.length + " questions, with the rule in between.",
      stappen: [
        { kop: kop1, kopEn: onderhoud ? "Still good?" : "Quick refresher",
          uitleg: "", uitlegEn: "",
          vragen: voor },
        { kop: ct("En dit is de regel", "And this is the rule"), kopEn: "And this is the rule",
          hulp: gcHulp(c.id),
          uitleg: c.uitleg, uitlegEn: c.uitlegEn || c.uitleg,
          vragen: na }
      ]
    };
  }
  /* Geen regeltekst of maar een vraag over: dan de oude vorm. Een stap zonder vragen bestaat
     nergens in dit bestand en ik ga hem hier niet uitvinden. */
  return {''')

    # en de oude vorm eronder krijgt dezelfde lengte en dezelfde kop mee
    rep(
        r'''    id: id, concept: cid, opfris: true,
    titel: ct("Even opfrissen: " + naam, "Quick refresher: " + naam),
    titelEn: "Quick refresher: " + (c.naamEn || c.naam),
    pitch: ct("Twee vragen. Je had dit al een keer goed.", "Two questions. You had this right before."),
    pitchEn: "Two questions. You had this right before.",
    stappen: [{ kop: ct("Even opfrissen", "Quick refresher"),
                kopEn: "Quick refresher",
                uitleg: "", uitlegEn: "",
                vragen: vragen }]
  };
}''',
        r'''    id: id, concept: cid, opfris: true, onderhoud: onderhoud,
    titel: titel1,
    titelEn: (onderhoud ? "Upkeep: " : "Quick refresher: ") + (c.naamEn || c.naam),
    pitch: pitch1,
    pitchEn: reeks.length + " questions.",
    stappen: [{ kop: kop1,
                kopEn: onderhoud ? "Still good?" : "Quick refresher",
                uitleg: "", uitlegEn: "",
                vragen: reeks }]
  };
}''')

    # ---------------- DRIE: drie onderhoudsbeurten in plaats van een ----------------
    rep(
        r'''  kand.sort(function(a, b){ return (a.st.due || "") < (b.st.due || "") ? -1 : 1; });
  return kand[0];
}''',
        r'''  kand.sort(function(a, b){ return (a.st.due || "") < (b.st.due || "") ? -1 : 1; });
  return kand[0];
}
/* ================= EN ER MAG MEER DAN EEN PER DAG DOORHEEN (v23.278) =================

   Stefan, 21 november: "Ik denk dat ik meer verschillende soorten grammatica zou moeten oefenen."

   Gemeten op zijn gegevens van 20 november: 30 onderwerpen open, 68 doosjes toe, en de dagles
   bood er twee aan. Die twee komen uit de focus, en de focus is met opzet smal (v23.234, op zijn
   eigen verzoek "dwing dit meer af"). Daar hoort de breedte dus niet vandaan te komen.

   Ze hoort hier vandaan. v23.235 splitste leren en onderhouden in twee budgetten juist omdat ze
   niet om dezelfde plek horen te vechten, en gaf het onderhoud er daarna een per dag. Dat is te
   zuinig als er achtenzestig doosjes staan te wachten.

   Drie, en uit DRIE VERSCHILLENDE onderwerpen. Dat laatste is de helft van het punt: drie
   patronen van hetzelfde onderwerp is nog steeds een onderwerp, en "heel veel el of la" was de
   klacht die v23.170 kwam repareren.

   Het wordt bijna niet langer, want een onderhoudsbeurt is sinds deze ronde twee vragen in plaats
   van vijf (GC_OPFRIS_ONDERHOUD). Een onderwerp werd zes vragen; drie onderwerpen worden er zes. */
var GRAM_ONDERHOUD_N = 3;
function gramOnderhoudRij(n){
  var rij = [];
  try { rij = gramWachtrij(); } catch(e){ return []; }
  var kand = rij.filter(function(x){ return (x.st.box || 0) >= GRAM_ONDERHOUD_DOOS; });
  kand.sort(function(a, b){ return (a.st.due || "") < (b.st.due || "") ? -1 : 1; });
  var uit = [], gezien = {};
  for(var i = 0; i < kand.length && uit.length < (n || GRAM_ONDERHOUD_N); i++){
    var k = kand[i];
    if(gezien[k.c.id]) continue;
    gezien[k.c.id] = 1;
    uit.push(k);
  }
  return uit;
}''')

    rep(
        r'''  var oh = null;
  try { oh = gramOnderhoudTop(); } catch(e){ oh = null; }
  if(oh){
    var ohId = gcOpfrisId(oh.c.id, oh.pi);
    if(uit.map(kaal).indexOf(kaal(ohId)) === -1){
      var ohO = null;
      try { ohO = gcGebouwd(ohId); } catch(e){ ohO = null; }
      if(ohO) uit.push(ohO.id);
    }
  }
  return uit;''',
        r'''  /* v23.278: drie in plaats van een, uit drie verschillende onderwerpen. Zie de kop bij
     gramOnderhoudRij(). Wat al in de les staat telt mee voor de ontdubbeling, dus een onderwerp
     dat vandaag ook geleerd wordt komt niet ook nog als onderhoud langs. */
  /* Ruimer vragen dan nodig en stoppen zodra er drie staan. Een doosje waarvan de generator geen
     vragen kan maken (dat komt voor: niet elk patroon levert er genoeg) zou anders een plek kosten
     in plaats van overgeslagen te worden. */
  var ohRij = [];
  try { ohRij = gramOnderhoudRij(GRAM_ONDERHOUD_N * 4); } catch(e){ ohRij = []; }
  var ohGezet = 0;
  for(var oi = 0; oi < ohRij.length && ohGezet < GRAM_ONDERHOUD_N; oi++){
    var ohId = gcOpfrisId(ohRij[oi].c.id, ohRij[oi].pi);
    if(uit.map(kaal).indexOf(kaal(ohId)) !== -1) continue;
    var ohO = null;
    try { ohO = gcGebouwd(ohId); } catch(e){ ohO = null; }
    if(!ohO) continue;
    uit.push(ohO.id);
    ohGezet++;
  }
  return uit;''')

    APP.write_text(src, encoding="utf-8")
    print("index.html: oordeel op patroondoosjes, de regel in elke opfrisser, drie onderhoudsbeurten")
else:
    print("index.html: stond er al")

nieuw, doe_ver, reden = patchhulp.nummerKiezen(huidig, GEPLAND, DOE_APP)
if reden:
    print("LET OP: " + reden)
if doe_ver:
    patchhulp.zetVersie(APP, VER, huidig, nieuw)
    print("versie.txt: %s -> %s" % (huidig, nieuw))
else:
    print("versie.txt: stond al op " + huidig)
