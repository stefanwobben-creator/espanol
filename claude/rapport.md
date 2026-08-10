# Het voortgangsrapport op orde

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
