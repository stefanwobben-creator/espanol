#!/usr/bin/env python3
# v23.38 - de week klopt. Punt 1, 2, 3 en 6 uit claude/rapport.md.
#
#   1. De weekkop telde het verschil in `geoefend` tussen twee weekmetingen. Dat getal telt elk woord
#      dat ooit in S.srs kwam, dus de inhaalslag zette er in een keer honderden neer die je niet
#      geoefend maar weggeklikt had: "+449 woorden geoefend deze week" naast "26 minuten deze week".
#      Nu staan er beurten uit S.dagStats, over hetzelfde venster van zeven dagen als de minuten en
#      het foutpercentage ernaast.
#
#   6. De tijdmeting is nagemeten (claude/rapport.md, sectie "De nameting"). Ze is exact tussen twee
#      antwoorden onder de twee minuten en telt verder niets: geen lezen, geen luisteren, geen gat
#      boven de twee minuten. Dat is een ondergrens en dat staat er nu bij, met de seconden per beurt
#      erbij zodat het na te rekenen is. Daarnaast begint hier een tweede meter (asec) die nog niets
#      toont: over een week zeggen twee meters naast elkaar wat "minuten" hoort te betekenen.
#
#   2 en 3 kwamen erbij omdat de drie nieuwe poortregels er meteen op omvielen, en dat is waar ze
#      voor zijn. tempoMeting() viel voor weken zonder dekw terug op dek (twee maten in een verschil,
#      met een groen "op koers" eronder), en de cijferlijst rekende per niveau terwijl de balk
#      samentelt (50 onderaan, 406 bovenaan).
#
# Idempotent: draait hij twee keer, dan gebeurt er de tweede keer niets. Per bestand een eigen vlag,
# want anders slaat hij bestand twee stil over als bestand een al klaar was (zie DEPLOY.md).

# ---------- deel 1: de week en de tijdmeting ----------
import re, sys, pathlib

WORTEL = pathlib.Path.home() / "espanol"
APP = WORTEL / "index.html"
SUITE = WORTEL / "test" / "suites" / "pw-voortgang.js"
VERSIE = WORTEL / "versie.txt"
RAPPORT = WORTEL / "claude" / "rapport.md"

MEET_TEKST = r"""// De nameting bij punt 6 uit claude/rapport.md (v23.38). Geen suite en dus geen onderdeel van de
// poort: een meetprogramma dat zegt hoeveel van de kloktijd de app opschrijft en waar de rest blijft.
// Draaien met de testserver van de poort ernaast:
//
//   node test/poort.js pw-schema.js     (of een eigen servertje op 8321)
//   CHROMIUM=<pad> node claude/meet-tijd.js
//
const { chromium } = require('playwright');
const U = 'http://localhost:8321/espanol-stefan.html';

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM });
  const page = await browser.newPage({ viewport: { width: 420, height: 900 } });
  page.on('pageerror', e => console.log('PAGEERROR ' + e));
  await page.goto(U); await page.waitForTimeout(300);
  await page.evaluate(() => { try { localStorage.setItem('espanol-proef-v1', JSON.stringify({overgeslagen:true})); } catch(e){} });
  await page.goto(U); await page.waitForTimeout(700);
  await page.fill('input[placeholder="Naam"], input[placeholder="Name"]', 'Meet' + Date.now());
  await page.click('button:has-text("A1 ·")');
  await page.click('#btnNewProf');
  await page.waitForTimeout(900);
  await page.evaluate(() => { S.lang='nl'; S.tour=true; try{persist();}catch(e){} const w=document.getElementById('tourWrap'); if(w&&w.remove) w.remove(); });

  // 1. Wat meet trackTijd van een reeks antwoorden met bekende gaten?
  const m1 = await page.evaluate(async () => {
    const wacht = ms => new Promise(r => setTimeout(r, ms));
    const d = today();
    S.dagStats = {}; tijdLaatst = 0;
    const gaten = [3000, 3000, 3000, 3000, 3000];   // vijf gaten van 3 s tussen zes antwoorden
    trackPoging(false);                              // eerste antwoord van de sessie
    for (const g of gaten) { await wacht(g); trackPoging(false); }
    const klok = gaten.reduce((a,b)=>a+b,0);
    return { klokSec: klok/1000, gemeten: (S.dagStats[d]||{}).sec || 0, pog: (S.dagStats[d]||{}).pogingen || 0 };
  });
  console.log('A. zes antwoorden, vijf gaten van 3 s:');
  console.log('   klok tussen eerste en laatste antwoord: ' + m1.klokSec + ' s, opgeschreven: ' + m1.gemeten + ' s, pogingen: ' + m1.pog);

  // 2. Wat gebeurt er met een gat langer dan twee minuten?
  const m2 = await page.evaluate(() => {
    const d = today();
    S.dagStats = {}; tijdLaatst = 0;
    // handmatig de klok terugzetten in plaats van echt wachten
    trackPoging(false);                       // tijdLaatst = nu
    tijdLaatst = Date.now() - 130000;         // alsof het vorige antwoord 130 s geleden was
    trackPoging(false);
    const na1 = (S.dagStats[d]||{}).sec || 0;
    tijdLaatst = Date.now() - 110000;         // en nu een gat van 110 s
    trackPoging(false);
    return { na130: na1, na110: ((S.dagStats[d]||{}).sec || 0) - na1 };
  });
  console.log('B. een gat van 130 s levert ' + m2.na130 + ' s op, een gat van 110 s levert ' + m2.na110 + ' s op.');

  // 3. Hoeveel sessies per dag kosten hoeveel? tijdLaatst begint bij elke paginalading op 0.
  const m3 = await page.evaluate(() => {
    const d = today();
    S.dagStats = {}; tijdLaatst = 0;
    let n = 0;
    for (let s = 0; s < 3; s++) {           // drie sessies van vier antwoorden, gaten van 10 s
      tijdLaatst = 0;                        // nieuwe paginalading
      for (let i = 0; i < 4; i++) {
        if (i > 0) tijdLaatst = Date.now() - 10000;
        trackPoging(false); n++;
      }
    }
    return { pog: n, gemeten: (S.dagStats[d]||{}).sec || 0 };
  });
  console.log('C. drie sessies van vier antwoorden met gaten van 10 s: klok tussen eerste en laatste per sessie 30 s, dus 90 s totaal; opgeschreven: ' + m3.gemeten + ' s.');

  // 4. Welke schermen tellen mee? Tel de knoppen die wel/niet op een nagekeken antwoord uitkomen.
  await page.evaluate(() => { S.dagStats = {}; tijdLaatst = 0; });
  console.log('D. zie de codetelling hieronder (grep), niet in de browser te meten.');

  await browser.close();
})();
"""

RAPPORT_TEKST = r"""# Het voortgangsrapport op orde

Werklijst voor v23.38 en verder. Aanleiding: Stefan, 10 aug, na v23.37 live: "kijk goed naar de
grondslag en communicatiewaarde van dit rapport, voldoet het aan goede KPI's en zo niet, verbeter
dit rapport."

## De maatstaf

Een cijfer op dit scherm deugt als het aan alle vijf voldoet. Dit is de lat waar de rest van dit
document aan meet, en waar een volgende versie ook aan gemeten moet worden.

1. **Eén betekenis.** Dezelfde woorden op één scherm horen hetzelfde getal te zijn. Staat er twee
   keer "woorden houd je actief bij", dan hoort daar twee keer hetzelfde te staan.
2. **Beweegt binnen de periode.** Een weekcijfer dat pas na vijfentwintig dagen kan bewegen is geen
   weekcijfer.
3. **Te beïnvloeden.** Je moet er deze week iets aan kunnen doen. Anders is het een feit, geen
   stuurgetal, en dan hoort het niet bovenaan.
4. **Na te rekenen.** Teller en noemer zichtbaar, of ten minste te herleiden uit iets anders op het
   scherm. Een percentage zonder zijn breuk is een bewering.
5. **Ergens tegenaan.** Een doel, een vorige periode, of een band. Een los getal zegt niets over of
   het goed gaat.

En één regel die boven alle vijf staat: **liever niets dan bijna goed.** Een leeg vak met een zin
erbij is beter dan een getal in de verkeerde eenheid, want het eerste kost je niets en het tweede
kost je je vertrouwen in de rest van de pagina.

## Wat er nu niet klopt

Genummerd, met de oorzaak erbij, want de oorzaak bepaalt de oplossing.

### 1. "+449 woorden geoefend deze week" naast "26 minuten deze week"

Zeventien woorden per minuut, een week lang. Dat kan niet.

Oorzaak: het getal is het verschil in `geoefend` tussen twee weekmetingen, en `geoefend` telt elk
woord dat ooit in `S.srs` terechtkwam. De inhaalslag zet in één keer honderden woorden neer die je
niet hebt geoefend maar hebt weggeklikt als bekend. Het cijfer zakt op regel 3 en 4.

Oplossing: tellen wat je echt hebt beantwoord. `S.dagStats[dag].pogingen` bestaat al en telt precies
dat. Let op: dat zijn beurten en geen unieke woorden, dus de kop moet ook "beurten" zeggen, of we
gaan per dag de unieke woord-ids bijhouden. Ik neig naar beurten: het is er al, het is eerlijk, en
het sluit aan op de minuten ernaast (een beurt duurt seconden, dus beurten en minuten horen bij
elkaar te passen; doen ze dat niet, dan is er iets anders mis en dát wil je zien).

### 2. "27,2 per week nodig" tegenover "1 haal je nu"

Twee getallen naast elkaar in twee verschillende eenheden, en dat heb ik in v23.37 zelf gemaakt. Ik
heb de stand omgezet naar de nieuwe maat maar het tempo komt uit de weekmetingen, en die kennen
`dekw` pas sinds gisteren. Zakt op regel 1 en 5.

Oplossing: zolang er geen twee metingen in de nieuwe maat liggen staat er bij "haal je nu" geen
getal maar de zin wanneer het er wel staat. Precies zoals de grafiek het nu doet. Dat betekent ook:
geen koersoordeel ("later") zolang het tempo onbekend is, want dat oordeel rust nu op een artefact.

### 3. "50 woorden houd je actief bij op A2" onderaan, "406" bovenaan

Letterlijk dezelfde zin, twee getallen, één scherm. Zakt op regel 1. Dit is Stefans punt over de 197
tegenover de 357, dat ik in v23.37 niet heb opgelost maar verplaatst.

Oplossing: de cijferlijst rekent met dezelfde samentelling als de balk, of elke regel zegt expliciet
"alleen A2". Ik kies het eerste: één maat op de pagina, en wie het per niveau wil ziet dat in de
uitklapper die er al is.

### 4. "Waar je straks staat: 0 tot 10%"

Onder een pagina die zegt dat je op de helft zit. Drie afwijkingen in één blok: het rekent in
bewezen vast, het rekent per niveau, en het toont percentages terwijl de rest in aantallen praat.

Oplossing: dezelfde maat, dezelfde samentelling, en de waaier uit het prototype in plaats van twee
dunne balkjes met proza eronder. De waaier is niet versiering: hij laat zien dat het een band is en
geen belofte, en dat is precies wat de tekst nu in drie zinnen probeert uit te leggen.

### 5. Drie regels op "doosje 0/5" onder Zwakke plekken

Por of para, muy o mucho, indefinido of imperfecto staan alle drie op nul. Er valt niets te kiezen.
Zakt op regel 3: een lijst zonder rangschikking helpt je niet beslissen.

Oplossing: het aantal fouten van deze week ernaast, en daarop sorteren. Dat is wat ze onderscheidt
en het is wat je deze week kunt aanpakken. Staat er nergens een fout deze week, dan is het geen
zwakke plek maar een regel die je nog niet bent tegengekomen, en dan hoort hij hier niet.

### 6. 26 minuten in een week, terwijl je doel 30 minuten per dag is

Vier procent van je eigen instelling. Er zijn twee verklaringen en het rapport laat je raden welke.
Ofwel de meting klopt niet (hij telt alleen tussenpozen onder de twee minuten, telt niets buiten de
oefeningen om, en begon pas op 28 juli), ofwel je haalt je instelling echt niet.

Oplossing: eerst nameten, niet eerst tonen. Ik ga de meting naast je eigen sessies leggen voordat er
een conclusie aan hangt. Blijkt hij structureel te laag, dan is de eerlijke tekst "gemeten binnen de
oefeningen" en niet "minuten deze week".

### 7. Kleiner, maar het staat er wel

- "15 nieuwe woorden per dag" zonder de 210 die daarbij hoort over veertien dagen.
- "20 dagen erbij geweest" zonder erbij vanaf wanneer, naast "14 van de laatste 14 dagen".
- De uitklapper "Per niveau" met twee keer 0% naast een balk die op 406 staat.
- "Alles in cijfers" geeft elk getal een alinea. Dat is de reden dat je scrollt.

## De nameting (v23.38, punt 6)

Beloofd was: eerst nameten, niet eerst tonen. Dit is de uitkomst, gemeten tegen de echte app in een
browser (`claude/meet-tijd.js`, drie proeven).

- Zes antwoorden met gaten van drie seconden: klok 15 s, opgeschreven 15 s. Tussen twee antwoorden
  onder de twee minuten klopt de meter tot op de seconde. Er zit dus geen drift in.
- Een gat van 130 seconden levert 0 seconden op, een gat van 110 seconden levert er 110 op. Boven de
  drempel valt de hele pauze weg, ook het deel waarin je zat na te denken.
- `tijdLaatst` begint bij elke paginalading op nul, dus het eerste antwoord van een sessie levert
  niets op. Wie op een dag drie keer even opent, verliest drie aanlopen.
- En het grootste: `trackTijd` hangt onder `trackPoging`, en die staat op negentien plekken, allemaal
  een nagekeken antwoord. Lezen, luisteren, de muur, Chispa, de winkel, de uitleg van een
  grammaticapunt: nul seconden.

Conclusie: de meter drijft niet af, hij meet iets kleiners dan wat je denkt te meten. Hij is een
ondergrens van je tijd in de app. Hoeveel kleiner is niet uit de code te halen, want dat hangt aan
hoe jij de app gebruikt.

Wat er daarom in v23.38 gebeurt, en wat niet:

- Het scherm zegt "minuten gemeten" en niet "minuten deze week", met eronder de seconden per beurt en
  de zin dat de klok alleen tussen je antwoorden loopt. Nu is het na te rekenen: beurten en minuten
  staan in hetzelfde blok, uit hetzelfde venster van zeven dagen.
- Er begint een tweede meter (`asec` in `S.dagStats`) die het gat sinds je vorige handeling telt, met
  dezelfde tweeminutenregel. Die toont niets. Over een week ligt er een week aan beide meters naast
  elkaar, en dan pas is te zeggen of "minuten" de tijd tussen je antwoorden hoort te zijn of je tijd
  in de app. Dat verschil raden en meteen tonen was precies de fout die dit hele document beschrijft.

## De volgorde

Eerst de dingen die onwaar zijn, dan de dingen die verwarren, dan de vorm. Elke stap is een eigen
versie die los terug te draaien is, en elke stap gaat door de poort.

**v23.38, de week klopt (gedaan).** Punt 1 en 6, plus punt 2 en 3 die er onderweg bij kwamen. De
weekkop is beurten uit `S.dagStats`, de tijdmeting is nagemeten voordat er iets over gezegd is (zie
hierboven), en de drie regels van de maatstaf staan als proef in `pw-voortgang.js`.

Punt 2 en 3 kwamen erbij omdat die proeven meteen omvielen, en dat is precies waar ze voor zijn.
Maatstaf 2 ving dat `tempoMeting()` voor weken zonder `dekw` terugviel op `dek`: een verschil tussen
twee getallen die niet hetzelfde meten, met een groen "op koers" eronder. Weken zonder `dekw` doen
niet meer mee, en zolang er geen drie in de nieuwe maat liggen staat er geen tempo en geen oordeel.
Maatstaf 1 kon alleen omvallen als de cijferlijst en de balk verschillende getallen gaven, en dat
deden ze: dat is punt 3, en de cijferlijst rekent nu met dezelfde samentelling.

**v23.39, waar je straks staat.** Punt 4. Dezelfde maat, dezelfde samentelling, en de waaier uit
het prototype in plaats van twee dunne balkjes met proza eronder.

**v23.40, de zwakke plekken worden bruikbaar.** Punt 5. Fouten van deze week erbij, daarop
sorteren, en regels zonder verse fouten eruit.

**v23.41, de vorm.** De cijferlijst inkorten en de kleine dingen uit punt 7.

**Daarna, over een week:** de twee tijdmeters naast elkaar leggen (zie De nameting) en beslissen wat
"minuten" op dit scherm hoort te betekenen.

## Hoe we weten dat het klopt

Een suite die de maatstaf zelf bewaakt, niet de tekst. Concreet, en dit is het stuk dat het langst
meegaat:

- Elke zin die "woorden houd je actief bij" bevat toont hetzelfde getal, waar hij ook op het scherm
  staat. Dat is regel 1, en hij is machinaal te controleren.
- Geen enkel getal op het scherm dat uit een weekmeting komt zonder `dekw` wordt als tempo of koers
  gepresenteerd. Dat is regel 2 en het is de fout die ik in v23.37 maakte.
- Elk percentage heeft zijn breuk binnen dezelfde regel, of een label dat zegt wat het meet. Dat is
  regel 4.

Die drie horen in `pw-voortgang.js`, want dan valt de poort om zodra iemand (ik) er weer een tweede
telling naast zet.
"""

src = APP.read_text(encoding="utf-8")
DOE_APP = 'var APP_VERSIE = "v23.38"' not in src

if not DOE_APP:
    print("  index.html staat al op v23.38, die sla ik over")
else:
    if "function vgWeekGroei" not in src:
        print("Deze index.html kent vgWeekGroei niet, dus je repo loopt niet op v23.37.\n"
              "    git pull --rebase\n"
              "en draai me daarna opnieuw.")
        sys.exit(1)

    def rep(anker, nieuw, n=1):
        global src
        aantal = src.count(anker)
        assert aantal == n, "anker %d keer gevonden, verwacht %d: %r" % (aantal, n, anker[:90])
        src = src.replace(anker, nieuw, n)

    # ---------------------------------------------------------------- 1. de tweede tijdmeter
    rep(
        """  tijdLaatst = nu;
}
""",
        """  tijdLaatst = nu;
}
/* v23.38. De nameting bij punt 6: sec is exact tussen twee antwoorden onder de twee minuten, en
   telt verder niets. Niet het lezen, niet het luisteren, niet de kaart waar je nog over nadenkt
   als je stopt, niet je eerste antwoord van een sessie, en een gat boven de twee minuten telt voor
   nul en niet voor twee minuten. Het is dus een ondergrens, en hoeveel eronder weet niemand.

   asec meet hetzelfde langs de andere kant: het gat sinds je vorige handeling in de app, met
   dezelfde tweeminutenregel. Elke nagekeken beurt begint met een tik of een toets, dus asec is per
   definitie ruimer dan sec, en het verschil is precies wat sec niet ziet.

   Er wordt nog niets van getoond en dat is het punt. Twee meters die een week naast elkaar lopen
   zeggen samen wat "minuten" hoort te betekenen; een meter met een aanname erbij zegt dat niet. */
var aktieLaatst = 0;
function trackAktie(){
  if(!S) return;
  var nu = Date.now(), d = today();
  S.dagStats = S.dagStats || {};
  S.dagStats[d] = S.dagStats[d] || {pogingen:0, fouten:0};
  if(aktieLaatst && nu - aktieLaatst < TIJD_GAT){
    S.dagStats[d].asec = (S.dagStats[d].asec || 0) + Math.round((nu - aktieLaatst) / 1000);
  }
  aktieLaatst = nu;
}
/* In de capture-fase, zodat een handler die het event tegenhoudt de meting niet stilzet. Er wordt
   hier niet weggeschreven: dat doet trackPoging al bij elk antwoord, en anders het wegklikken van
   het tabblad hieronder. Een persist() per tik zou een schrijfactie per klik betekenen. */
function aktieWire(){
  if(aktieWire._klaar || typeof document === "undefined" || !document.addEventListener) return;
  aktieWire._klaar = true;
  document.addEventListener("pointerdown", trackAktie, true);
  document.addEventListener("keydown", trackAktie, true);
  document.addEventListener("visibilitychange", function(){
    if(document.hidden){ trackAktie(); try{ persist(); }catch(e){} }
  });
}
""")

    rep("""function tijdVenster(dagen){
  var t = today(), sec = 0, pog = 0, dagenMet = 0, i, e;
  for(i = 0; i < dagen; i++){
    e = (S.dagStats || {})[addDays(t, -i)];
    if(!e) continue;
    if(e.sec){ sec += e.sec; dagenMet++; }
    pog += e.pogingen || 0;
  }
  return {sec:sec, pog:pog, dagen:dagenMet,""",
        """function tijdVenster(dagen){
  var t = today(), sec = 0, asec = 0, pog = 0, dagenMet = 0, i, e;
  for(i = 0; i < dagen; i++){
    e = (S.dagStats || {})[addDays(t, -i)];
    if(!e) continue;
    if(e.sec){ sec += e.sec; dagenMet++; }
    asec += e.asec || 0;                 // v23.38: de tweede meter, nog nergens in beeld
    pog += e.pogingen || 0;
  }
  return {sec:sec, asec:asec, pog:pog, dagen:dagenMet,""")

    rep("""(function init(){
  if(!store.ok) document.getElementById("storageWarn").classList.remove("hidden");
  buildNav();""",
        """(function init(){
  if(!store.ok) document.getElementById("storageWarn").classList.remove("hidden");
  buildNav();
  aktieWire();                            // v23.38: de tweede tijdmeter, zie trackAktie""")

    # ---------------------------------------------------------------- 2. de weekkop
    oud_groei = """/* ---------- 1. Je week ---------- */
/* v23.37: de aanwas van geoefende woorden, niet van bewezen vast. Stefan: "hoezo maar +4 woorden
   erbij? dit zijn gegronde woorden denk ik, maar die gaan heel langzaam dus beter hier aantal
   nieuwe woorden geoefend." Precies: bewezen vast vraagt vijf goede beurten over vijfentwintig
   dagen, dus als weekcijfer meet dat vooral hoe lang je al bezig bent. Geoefend beweegt met wat je
   die week echt gedaan hebt, en staat al in elke weekmeting. */
function vgWeekGroei(wk){
  if(wk.length < 2) return null;
  return Math.max(0, wk[wk.length-1].geoefend - wk[wk.length-2].geoefend);
}
"""
    nieuw_groei = """/* ---------- 1. Je week ---------- */
/* v23.38, punt 1 uit claude/rapport.md. Hier stond de aanwas van geoefende woorden: het verschil in
   `geoefend` tussen twee weekmetingen. Twee dingen mis. Geoefend telt elk woord dat ooit in S.srs
   terechtkwam, dus de inhaalslag zet er in een keer honderden neer die je niet geoefend maar
   weggeklikt hebt als bekend; Stefan zag "+449 woorden geoefend deze week" naast "26 minuten deze
   week", en zeventien woorden per minuut houdt niemand een week vol. En het bewoog pas als er een
   nieuwe weekmeting geschreven was, dus het was geen weekcijfer maar een sprong.

   Nu staat er wat je echt gedaan hebt: de beurten uit S.dagStats, over hetzelfde venster van zeven
   dagen als de minuten en het foutpercentage die eronder staan. Een beurt is een nagekeken
   antwoord. Dat is geen woorden en het zegt het ook niet: liever een eerlijk getal in een andere
   eenheid dan een woordental dat niet klopt. */
"""
    rep(oud_groei, nieuw_groei)

    oud_week = """function vgWeekHtml(c){
  var t = today(), i, d, dagen = 0;
  for(i = 0; i < 7; i++){ d = addDays(t, -i); if((S.xp || {})[d] > 0) dagen++; }
  var wk = vgWeken(c.samen.nivs);
  var groei = vgWeekGroei(wk);
  var tv = tijdVenster(7);
  var h = "<div class='card'><span class='kicker'>"+ct("Je week","Your week")+" \\ud83d\\udc40</span>";
  /* De kop is de aanwas en niet de stand. De stand loopt altijd op, dus die kan niet zeggen of dit
     een goede week was; de aanwas wel. Zonder tweede weekmeting staat er geen aanwas, want een
     verschil met niets is geen verschil. */
  if(groei === null){
    h += "<p style='margin:0 0 6px'>"+ct("Je eerste weekmeting staat er. Vanaf de volgende staat hier "+
      "hoeveel er die week bij kwam.","Your first weekly measurement is in. From the next one on, this "+
      "shows how much came in that week.")+"</p>";
  } else {
    h += "<div class='vgKop'><div class='vgGroot'>"+(groei >= 0 ? "+" : "")+groei+"</div>"+
      "<div class='vgBij'>"+ct("woorden geoefend deze week","words practised this week")+"</div></div>";
  }
  /* v23.37: minuten in plaats van lessen. Stefan: "lessen is hier beetje verwarrend, misschien hier
     totale tijd per week?" Die tijd wordt al gemeten (uit de gaten tussen je antwoorden), hij stond
     alleen nergens per week. Zonder gemeten tijd staat er niets in plaats van een nul. */
  var minuten = tv.sec ? Math.round(tv.sec / 60) : null;
  h += "<div class='statgrid' style='margin-top:8px'>"+
    "<div class='stat'><b>"+dagen+"/7</b><span class='muted'>"+ct("dagen geoefend","days practised")+"</span></div>"+
    (minuten !== null
      ? "<div class='stat'><b>"+minuten+"</b><span class='muted'>"+ct("minuten deze week","minutes this week")+"</span></div>"
      : "<div class='stat'><b>"+afgemaakt7()+"</b><span class='muted'>"+ct("lessen afgemaakt","sessions finished")+"</span></div>")+
    "</div>";
  var los = [];
  los.push("\\ud83d\\udd25 " + streakNow() + " " + ct("dagen op rij","days in a row"));
  los.push(afgemaakt7() + " " + ct("lessen","sessions"));
  if(c.fout7.pct !== null) los.push(c.fout7.pct + "% " + ct("fout","wrong"));
  h += "<p class='muted' style='margin:8px 0 0; font-size:.86rem'>"+los.join(" \\u00b7 ")+"</p>";"""

    nieuw_week = """function vgWeekHtml(c){
  var t = today(), i, d, dagen = 0;
  for(i = 0; i < 7; i++){ d = addDays(t, -i); if((S.xp || {})[d] > 0) dagen++; }
  var tv = tijdVenster(7);
  var h = "<div class='card'><span class='kicker'>"+ct("Je week","Your week")+" \\ud83d\\udc40</span>";
  if(!tv.pog){
    h += "<p style='margin:0 0 6px'>"+ct("Zodra je een antwoord geeft telt hij hier mee. Deze week "+
      "staat er nog niets.","As soon as you answer something it counts here. Nothing yet this week.")+"</p>";
  } else {
    h += "<div class='vgKop'><div class='vgGroot'>"+tv.pog+"</div>"+
      "<div class='vgBij'>"+ct("beurten deze week","answers this week")+"</div></div>";
  }
  /* v23.37: minuten in plaats van lessen. Stefan: "lessen is hier beetje verwarrend, misschien hier
     totale tijd per week?" Die tijd wordt al gemeten (uit de gaten tussen je antwoorden), hij stond
     alleen nergens per week. Zonder gemeten tijd staat er niets in plaats van een nul. */
  var minuten = tv.sec ? Math.round(tv.sec / 60) : null;
  h += "<div class='statgrid' style='margin-top:8px'>"+
    "<div class='stat'><b>"+dagen+"/7</b><span class='muted'>"+ct("dagen geoefend","days practised")+"</span></div>"+
    (minuten !== null
      ? "<div class='stat'><b>"+minuten+"</b><span class='muted'>"+ct("minuten gemeten","minutes measured")+"</span></div>"
      : "<div class='stat'><b>"+afgemaakt7()+"</b><span class='muted'>"+ct("lessen afgemaakt","sessions finished")+"</span></div>")+
    "</div>";
  var los = [];
  los.push("\\ud83d\\udd25 " + streakNow() + " " + ct("dagen op rij","days in a row"));
  los.push(afgemaakt7() + " " + ct("lessen","sessions"));
  if(c.fout7.pct !== null) los.push(c.fout7.pct + "% " + ct("fout","wrong"));
  h += "<p class='muted' style='margin:8px 0 0; font-size:.86rem'>"+los.join(" \\u00b7 ")+"</p>";
  /* v23.38: de minuten staan er nu met hun noemer, want de beurten staan erboven. Deel het een door
     het ander en je ziet meteen of de meting kan kloppen; dat was precies wat er miste toen er
     "26 minuten" stond zonder iets om het tegenaan te houden. En erbij wat de meter niet ziet,
     want dat is geen detail: hij telt de gaten tussen je antwoorden en verder niets. */
  if(minuten !== null && tv.pog){
    h += "<p class='muted' style='margin:4px 0 0; font-size:.82rem'>"+
      ct("Dat is ongeveer "+getal1(tv.sec / tv.pog)+" seconde per beurt. De klok loopt tussen je "+
         "antwoorden, dus lezen, luisteren en lang nadenken tellen niet mee: het is een ondergrens.",
         "That is about "+getal1(tv.sec / tv.pog)+" seconds per answer. The clock runs between your "+
         "answers, so reading, listening and long pauses are not counted: this is a floor.")+"</p>";
  }"""
    rep(oud_week, nieuw_week)

    rep('var APP_VERSIE = "v23.37";', 'var APP_VERSIE = "v23.38";')
    APP.write_text(src, encoding="utf-8")
    print("  index.html: weekkop op beurten, tweede tijdmeter erbij, v23.38")

# ---------------------------------------------------------------- 3. de suite
s = SUITE.read_text(encoding="utf-8")
if "maatstaf 1" in s:
    print("  pw-voortgang.js staat al bij, die sla ik over")
else:
    def reps(anker, nieuw, n=1):
        global s
        aantal = s.count(anker)
        assert aantal == n, "suite-anker %d keer gevonden, verwacht %d: %r" % (aantal, n, anker[:90])
        s = s.replace(anker, nieuw, n)

    # fixture: echte dagstatistiek en een niveaudoel, zodat de weekkop en het tempo iets te zeggen hebben
    reps("""    const t = today();
    for (let i = 0; i < 10; i++) S.xp[addDays(t, -i)] = 20;
    for (let i = 0; i < 5; i++) S.lesFlow[addDays(t, -i)] = true;""",
         """    const t = today();
    for (let i = 0; i < 10; i++) S.xp[addDays(t, -i)] = 20;
    for (let i = 0; i < 5; i++) S.lesFlow[addDays(t, -i)] = true;
    /* v23.38: de weekkop komt hieruit en niet meer uit S.meting. Zeven dagen maal twaalf beurten is
       84, maal 300 seconden is 35 minuten, en 21 fouten op 84 beurten is 25%. Drie getallen die op
       het scherm bij elkaar horen te passen, dus alle drie uit dezelfde bron en hetzelfde venster. */
    S.dagStats = {};
    for (let i = 0; i < 7; i++) S.dagStats[addDays(t, -i)] = { pogingen: 12, fouten: 3, sec: 300 };
    // een niveaudoel, anders heeft het doelblok niets te tonen en toetst maatstaf 2 niets
    S.doelNiv = 'A1'; S.doelDatum = addDays(t, 140);""")

    reps("""  console.log('\\n-- je week rekent met het verschil, niet met de stand --');
  const week = await page.evaluate(() => {
    const k = [...document.querySelectorAll('#voortgangCard .card')][0];
    return (k ? k.innerText : '').replace(/\\s+/g, ' ');
  });
  /* v23.37: de week telt geoefende woorden, niet bewezen vast. De fixture gaat van 150 naar 200
     geoefend, dus +50. Bewezen vast ging van 78 naar 120; dat is wat hier eerst stond, en precies
     de teller waarvan Stefan zei dat hij als weekcijfer niets zegt. */
  ok(/\\+50/.test(week), 'de aanwas is die van geoefende woorden (+50)');
  ok(/\\/7/.test(week), 'met het aantal dagen dat je er was');""",
         """  console.log('\\n-- je week telt wat je gedaan hebt, niet wat er in S.srs staat --');
  const week = await page.evaluate(() => {
    const k = [...document.querySelectorAll('#voortgangCard .card')][0];
    return (k ? k.innerText : '').replace(/\\s+/g, ' ');
  });
  /* v23.38. Hier stond de aanwas van `geoefend` tussen twee weekmetingen (+50 in deze fixture). Dat
     getal springt met de inhaalslag mee en heeft niets met je week te maken. Nu: de beurten uit
     S.dagStats over zeven dagen, hetzelfde venster als de minuten en het foutpercentage eronder. */
  ok(/\\b84\\b/.test(week), 'de kop is het aantal beurten van deze week (84)');
  ok(/beurten/.test(week), 'en zegt ook beurten, niet woorden');
  ok(!/\\+50/.test(week), 'de aanwas uit de weekmeting staat er niet meer');
  ok(/\\/7/.test(week), 'met het aantal dagen dat je er was');
  ok(/\\b35\\b/.test(week), 'de gemeten minuten staan erbij (35)');
  ok(/per beurt/.test(week), 'en de seconden per beurt, zodat de minuten na te rekenen zijn');
  ok(/ondergrens/.test(week), 'met erbij dat de klok alleen tussen je antwoorden loopt');

  /* ---------- de drie regels uit claude/rapport.md, machinaal ----------
     Deze drie bewaken de maatstaf zelf en niet de tekst. Ze staan hier omdat elke fout die ik op dit
     scherm gemaakt heb er een van deze drie was, en omdat een maatstaf die alleen in een document
     staat de volgende versie niet haalt. */
  console.log('\\n-- maatstaf 1: dezelfde zin is hetzelfde getal --');
  const zelfde = await page.evaluate(() => {
    const t = document.getElementById('tab-voortgang').innerText;
    const uit = [];
    t.split('\\n').forEach((r) => {
      if (!/houd je actief bij|actief bij/.test(r)) return;
      const m = r.match(/\\d[\\d.]*/);
      if (m) uit.push(m[0]);
    });
    return uit;
  });
  ok(zelfde.length === 0 || zelfde.every((z) => z === zelfde[0]),
    'wat "actief bij" heet is overal hetzelfde getal (' + (zelfde.join(', ') || 'staat er niet') + ')');

  console.log('\\n-- maatstaf 2: geen tempo uit een meting die het niet weet --');
  /* De metingen in deze fixture kennen geen dekw, want die bestaat pas sinds v23.37. Dan is er geen
     tempo in de maat van de balk, en dus ook geen koersoordeel. Dit is de fout die ik in v23.37 zelf
     maakte: de stand omgezet naar de nieuwe maat en het tempo uit de oude laten komen. */
  const doel = await page.evaluate(() => {
    const k = [...document.querySelectorAll('#voortgangCard .card')][1];
    const ds = doelStand();
    return { tekst: (k ? k.innerText : '').replace(/\\s+/g, ' '), tempo: ds ? ds.tempo : null };
  });
  ok(doel.tempo === null, 'zonder dekw in de weekmetingen is er geen tempo (' + doel.tempo + ')');
  ok(!/op koers|later dan je datum/.test(doel.tekst), 'en dus staat er ook geen koersoordeel');

  console.log('\\n-- maatstaf 3: elk percentage heeft woorden bij zich --');
  const losPct = await page.evaluate(() => {
    const t = document.getElementById('tab-voortgang').innerText;
    return t.split('\\n').map((r) => r.trim()).filter((r) => /%/.test(r))
      .filter((r) => r.replace(/[\\d.,%]+/g, ' ').trim().split(/\\s+/).filter(Boolean).length < 2);
  });
  ok(losPct.length === 0, 'geen kaal percentage zonder wat het meet (' +
    (losPct.join(' | ') || 'geen') + ')');""")

    SUITE.write_text(s, encoding="utf-8")
    print("  pw-voortgang.js: de weekkop en de drie regels van de maatstaf")

# ---------------------------------------------------------------- 4. versie.txt
v = VERSIE.read_text(encoding="utf-8").strip()
if v == "v23.38":
    print("  versie.txt staat al op v23.38")
else:
    VERSIE.write_text("v23.38\n", encoding="utf-8")
    print("  versie.txt: " + v + " -> v23.38")

# ---------------------------------------------------------------- 5. het rapport in de repo
# Het plan zelf hoort in de repo en niet alleen in een gesprek: de volgende sessie begint ermee.
if RAPPORT.exists() and "De nameting" in RAPPORT.read_text(encoding="utf-8"):
    print("  claude/rapport.md staat al bij")
else:
    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text(RAPPORT_TEKST, encoding="utf-8")
    print("  claude/rapport.md geschreven")

# ---------- deel 2: geen tempo uit een meting die het niet weet ----------
import pathlib, sys

WORTEL = pathlib.Path.home() / "espanol"
APP = WORTEL / "index.html"
SUITE = WORTEL / "test" / "suites" / "pw-voortgang.js"

src = APP.read_text(encoding="utf-8")
if "function metingenNieuweMaat" in src:
    print("  index.html staat al bij")
else:
    def rep(anker, nieuw, n=1):
        global src
        aantal = src.count(anker)
        assert aantal == n, "anker %d keer gevonden, verwacht %d: %r" % (aantal, n, anker[:90])
        src = src.replace(anker, nieuw, n)

    rep("""function tempoMeting(niveau){
  var ws = Object.keys(S.meting || {}).sort();
  if(ws.length < 3) return null;
  /* v23.37: het tempo rekent met wat je actief bijhoudt, net als de balk en het doel. Op dek
     (bewezen vast) gerekend kwam er 1 woord per week uit terwijl er tientallen bewegen, en dan is
     elke uitspraak over koers onbruikbaar. Weken zonder dekw vallen terug op dek: dat is wat we van
     die weken weten, en het alternatief is ze weggooien. */
  var reeks = ws.map(function(w){
    var m = S.meting[w] || {};
    return (m.dekw || {})[niveau] || (m.dek || {})[niveau] || 0;
  });
  var d = [], i;""",
        """/* v23.38. De weekmetingen die in de maat van deze pagina staan: actief bijgehouden, dus bewezen
   vast plus onderweg. Metingen van voor v23.37 kennen dekw niet en horen hier niet bij. */
function metingenNieuweMaat(niveau){
  var ws = Object.keys(S.meting || {}).sort(), uit = [], i, m;
  for(i = 0; i < ws.length; i++){
    m = S.meting[ws[i]] || {};
    if(m.dekw && typeof m.dekw[niveau] === "number") uit.push(m.dekw[niveau]);
  }
  return uit;
}
/* v23.37 rekende het tempo op dekw en viel voor oudere weken terug op dek. Dat leek voorzichtig
   (weggooien wat je hebt is zonde) maar het is het ergste van twee werelden: een verschil tussen
   twee getallen die niet hetzelfde meten is geen tempo maar een sprong van de ene maat naar de
   andere. Op Stefans scherm werd dat "27,2 per week nodig" naast "1 haal je nu", en in de fixture
   van de poort zelfs een groen "op koers" dat nergens op sloeg.

   v23.38: alleen weken in dezelfde maat. Zijn dat er nog geen drie, dan is er geen tempo. Dat kost
   drie weken zwijgen en dat is de goede prijs, want de rest van deze pagina hangt eraan. */
function tempoMeting(niveau){
  var reeks = metingenNieuweMaat(niveau);
  if(reeks.length < 3) return null;
  var d = [], i;""")

    rep("""function bandHtml(niveau){
  var weken = Object.keys(S.meting || {}).length;""",
        """function bandHtml(niveau){
  // v23.38: tellen wat meetelt. Weken zonder dekw staan wel in S.meting maar doen niet mee, dus met
  // Object.keys() zou hier "nog 1 week te gaan" staan die nooit voorbijgaat.
  var weken = metingenNieuweMaat(niveau).length;""")

    rep("""      ct("Wat je nu haalt is nog niet te meten; daar zijn drie weekmetingen voor nodig.",
         "What you're doing isn't measurable yet; that needs three weekly measurements.")+"</p>";""",
        """      ct("Wat je nu haalt is nog niet te meten: daar zijn drie weekmetingen voor nodig in dezelfde "+
         "maat als de balk hierboven, en die maat wordt sinds kort pas vastgelegd.",
         "What you're doing isn't measurable yet: that needs three weekly measurements in the same "+
         "unit as the bar above, and that unit has only recently started being recorded.")+"</p>";""")

    APP.write_text(src, encoding="utf-8")
    print("  index.html: tempo alleen uit weken in dezelfde maat")

s = SUITE.read_text(encoding="utf-8")
if "het vak eromheen" in s:
    print("  pw-voortgang.js staat al bij")
else:
    oud = """  const losPct = await page.evaluate(() => {
    const t = document.getElementById('tab-voortgang').innerText;
    return t.split('\\n').map((r) => r.trim()).filter((r) => /%/.test(r))
      .filter((r) => r.replace(/[\\d.,%]+/g, ' ').trim().split(/\\s+/).filter(Boolean).length < 2);
  });"""
    nieuw = """  const losPct = await page.evaluate(() => {
    /* Naar het vak eromheen kijken en niet naar de regel: een meetbalk zet naam, staaf en getal in
       drie elementen, dus in innerText staat "23%" bijna altijd alleen op zijn eigen regel terwijl
       het label er in beeld pal naast staat. De vraag is of het vak waarin het percentage staat
       zegt wat het meet. */
    const vakken = [...document.querySelectorAll('#tab-voortgang .vgMeet, #tab-voortgang .stat, ' +
      '#tab-voortgang .cijfRij, #tab-voortgang p, #tab-voortgang li')];
    const kaal = vakken.filter((v) => {
      const t = (v.innerText || '').replace(/\\s+/g, ' ').trim();
      if (!/%/.test(t)) return false;
      return !/[a-z\\u00e0-\\u017f]{3}/i.test(t.replace(/[\\d.,%]+/g, ' '));
    }).map((v) => (v.innerText || '').replace(/\\s+/g, ' ').trim());
    // en een percentage dat in helemaal geen vak staat is per definitie kaal
    const zwevend = [...document.querySelectorAll('#tab-voortgang *')].filter((e) => {
      if (e.children.length) return false;
      return /%/.test((e.textContent || '')) && !e.closest('.vgMeet, .stat, .cijfRij, p, li');
    }).map((e) => (e.textContent || '').trim());
    return kaal.concat(zwevend);
  });"""
    assert s.count(oud) == 1, "suite-anker niet gevonden"
    s = s.replace(oud, nieuw, 1)
    SUITE.write_text(s, encoding="utf-8")
    print("  pw-voortgang.js: maatstaf 3 kijkt naar het vak eromheen")


# ---------- deel 3: de cijferlijst op dezelfde samentelling ----------
import pathlib

APP = pathlib.Path.home() / "espanol" / "index.html"
SUITE = pathlib.Path.home() / "espanol" / "test" / "suites" / "pw-voortgang.js"

src = APP.read_text(encoding="utf-8")
if "var nivT = samenNivTekst" in src:
    print("  index.html staat al bij")
else:
    def rep(anker, nieuw, n=1):
        global src
        aantal = src.count(anker)
        assert aantal == n, "anker %d keer gevonden, verwacht %d: %r" % (aantal, n, anker[:90])
        src = src.replace(anker, nieuw, n)

    rep("""function cijferLijstHtml(){
  var c = voortgangCijfers(), r = "";
  r += cijferRij(c.actief, ct("woorden houd je actief bij op "+c.niv, "words you actively keep up at "+c.niv),
    ct("Dit is het getal dat op Vandaag boven de balk staat: bewezen vast plus onderweg, van de "+
       c.noem+" woorden die het Instituto Cervantes voor "+c.niv+" telt.",
       "This is the number above the bar on Today: proven solid plus on the way, out of the "+
       c.noem+" words the Instituto Cervantes counts for "+c.niv+"."));
  r += cijferRij(c.vast, ct("bewezen vast","proven solid"),""",
        """function cijferLijstHtml(){
  var c = voortgangCijfers(), r = "";
  /* v23.38: dezelfde samentelling als de balk. Stond hier c.actief (alleen je huidige niveau), dan
     stond onderaan de pagina "50 woorden houd je actief bij op A2" terwijl bovenaan 406 stond, met
     dezelfde woorden erbij. Een lezer die dat ziet weet niet welk van de twee liegt, en gaat aan de
     rest van het scherm ook twijfelen. */
  var nivT = samenNivTekst(c.samen.nivs);
  r += cijferRij(c.samen.actief, ct("woorden houd je actief bij op "+nivT, "words you actively keep up at "+nivT),
    ct("Dit is het getal dat op Vandaag boven de balk staat: bewezen vast plus onderweg, van de "+
       c.samen.noem+" woorden die het Instituto Cervantes voor "+nivT+" telt.",
       "This is the number above the bar on Today: proven solid plus on the way, out of the "+
       c.samen.noem+" words the Instituto Cervantes counts for "+nivT+"."));
  r += cijferRij(c.samen.vast, ct("bewezen vast","proven solid"),""")

    rep("""  r += cijferRij(c.onderweg, ct("onderweg","on the way"),""",
        """  r += cijferRij(c.samen.onderweg, ct("onderweg","on the way"),""")

    rep("""  if(c.ongezien > 0){
    r += cijferRij(c.ongezien, ct("nog niet gezien","not seen yet"),
      ct("Woorden van "+c.niv+" die je hier nog niet bent tegengekomen. Dit getal daalt vanzelf "+
         "zolang je nieuwe woorden blijft krijgen.",
         "Words at "+c.niv+" you have not met here yet. This number drops on its own as long as "+
         "you keep getting new words."));
  }""",
        """  if(c.samen.ongezien > 0){
    r += cijferRij(c.samen.ongezien, ct("nog niet gezien","not seen yet"),
      ct("Woorden van "+nivT+" die je hier nog niet bent tegengekomen. Dit getal daalt vanzelf "+
         "zolang je nieuwe woorden blijft krijgen.",
         "Words at "+nivT+" you have not met here yet. This number drops on its own as long as "+
         "you keep getting new words."));
  }""")

    # de schatting blijft per niveau en zegt dat ook: een steekproefmarge van twee niveaus is niet
    # de som van twee marges
    rep("""    r += cijferRij(c.schat.punt, ct("geschat totaal op "+c.niv, "estimated total at "+c.niv),
      ct("Uit je peiling, en dat is een steekproef. Ergens tussen "+c.schat.onder+" en "+c.schat.boven+
         ". De marge hoort erbij: dit is een schatting en geen telling.",""",
        """    r += cijferRij(c.schat.punt, ct("geschat totaal op "+c.niv, "estimated total at "+c.niv),
      ct("Alleen "+c.niv+", en niet samengeteld zoals de regels hierboven: een marge van twee niveaus "+
         "is niet de som van twee marges. Uit je peiling, en dat is een steekproef. Ergens tussen "+
         c.schat.onder+" en "+c.schat.boven+
         ". De marge hoort erbij: dit is een schatting en geen telling.",""")
    rep("""         "From your check, which is a sample. Somewhere between "+c.schat.onder+" and "+c.schat.boven+
         ". The margin belongs to it: this is an estimate and not a count."));""",
        """         c.niv+" only, not added up like the rows above: a margin across two levels is not the sum "+
         "of two margins. From your check, which is a sample. Somewhere between "+c.schat.onder+
         " and "+c.schat.boven+
         ". The margin belongs to it: this is an estimate and not a count."));""")

    APP.write_text(src, encoding="utf-8")
    print("  index.html: de cijferlijst rekent met dezelfde samentelling als de balk")

# ---------------------------------------------------------------- maatstaf 1 die echt kan omvallen
s = SUITE.read_text(encoding="utf-8")
if "const oudNiv = balkNiveau" in s:
    print("  pw-voortgang.js staat al bij")
else:
    oud = """  console.log('\\n-- maatstaf 1: dezelfde zin is hetzelfde getal --');
  const zelfde = await page.evaluate(() => {
    const t = document.getElementById('tab-voortgang').innerText;
    const uit = [];
    t.split('\\n').forEach((r) => {
      if (!/houd je actief bij|actief bij/.test(r)) return;
      const m = r.match(/\\d[\\d.]*/);
      if (m) uit.push(m[0]);
    });
    return uit;
  });
  ok(zelfde.length === 0 || zelfde.every((z) => z === zelfde[0]),
    'wat "actief bij" heet is overal hetzelfde getal (' + (zelfde.join(', ') || 'staat er niet') + ')');"""
    nieuw = """  console.log('\\n-- maatstaf 1: dezelfde zin is hetzelfde getal --');
  const zelfde = await page.evaluate(() => {
    /* Op een A1-profiel zijn "alleen je niveau" en "alle niveaus samen" hetzelfde getal, en dan kan
       deze regel niet omvallen: hij zou groen staan zonder iets te bewaken. Daarom even A2 als
       balkniveau. Dan telt de balk A1 en A2 samen, en moet elke regel die diezelfde woorden gebruikt
       dat ook doen. Dit is precies de fout die op Stefans scherm stond: 50 onderaan, 406 bovenaan. */
    const oudNiv = balkNiveau;
    balkNiveau = function () { return 'A2'; };
    try {
      const c = voortgangCijfers();
      const doos = document.createElement('div');
      doos.innerHTML = cijferLijstHtml();
      const rijen = [...doos.querySelectorAll('.cijfRij')]
        .filter((r) => /actief bij/.test(r.textContent || ''));
      return { samen: c.samen.actief, perNiveau: c.actief, nivs: c.samen.nivs,
               getallen: rijen.map((r) => ((r.querySelector('.cijfW') || {}).textContent || '').trim()) };
    } finally { balkNiveau = oudNiv; }
  });
  ok(zelfde.nivs.length > 1 && zelfde.samen !== zelfde.perNiveau,
    'de proef zet twee verschillende getallen tegenover elkaar (samen ' + zelfde.samen +
    ', alleen A2 ' + zelfde.perNiveau + ')');
  ok(zelfde.getallen.length > 0, 'de regel "actief bij" staat in de cijferlijst');
  ok(zelfde.getallen.every((g) => Number(g) === zelfde.samen),
    'en toont hetzelfde getal als de balk (' + (zelfde.getallen.join(', ') || 'niets') + ')');"""
    assert s.count(oud) == 1, "suite-anker maatstaf 1 niet gevonden"
    s = s.replace(oud, nieuw, 1)
    SUITE.write_text(s, encoding="utf-8")
    print("  pw-voortgang.js: maatstaf 1 kan nu omvallen")



# ---------- deel 4: het meetprogramma van de nameting ----------
# Een nameting die je niet kunt overdoen is een bewering. Dit is het programma waarmee de
# uitkomsten in claude/rapport.md gemeten zijn.
MEET = WORTEL / "claude" / "meet-tijd.js"
if MEET.exists():
    print("  claude/meet-tijd.js staat er al")
else:
    MEET.write_text(MEET_TEKST, encoding="utf-8")
    print("  claude/meet-tijd.js geschreven")

print("\nklaar. Draai nu de poort:")
print("  CHROMIUM=<pad naar chromium> node test/poort.js")
