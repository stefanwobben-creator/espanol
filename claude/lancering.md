# Naar de lancering: wat er staat, wat er open is, en waarom

Geschreven op 11 augustus, aan het eind van een lange sessie, als startpunt voor de volgende. Stefan
wil vrijdag lanceren. Dit document is bedoeld om in een schone sessie als eerste te lezen, naast
`DEPLOY.md` (de werkwijze) en `claude/rapport.md` (de maatstaf voor de voortgangspagina).

## Het doel, in Stefans woorden

"De beste app die er is op de markt om me te helpen Spaans te leren." En daarnaast, sinds 11 aug, een
datum: vrijdag live voor publiek.

Die twee botsen, en de eerlijke lezing is deze. In drie dagen word je niet de beste van de markt. Wat
je in drie dagen wél kunt: zorgen dat een vreemde zonder Stefan slaagt, en dat de lancering geen geld
kost dat niemand wilde uitgeven. Alles in dit document is op die twee dingen gesorteerd.

## Wat er op 11 aug af is

- **v23.38** de week telt beurten in plaats van een aanwas die met de inhaalslag meesprong; de
  tijdmeting is nagemeten (zie `claude/rapport.md`, sectie De nameting) en er loopt een tweede meter
  mee die nog niets toont.
- **v23.39** Adivina, het negende spel: Lingo met de eigen woordenschat, punten en een dagreeks.
- **v23.40** de nachtrun, drillzin s176.
- **v23.41** de merge van `curriculum/les-20260811`: de eerste les die de avondrun zelf maakte
  (b1-11, veertien woorden stad en platteland).
- **v23.42** de nachtrun kan geen lege uitleg meer leveren, zelfstandige naamwoorden krijgen el of
  la, geen accentvallen meer in toetsjes, en schrijven staat weer in de dagles als vaste vierde stap
  van drie zinnen.
- **server** de AI-eindpunten op slot: herkomstcontrole, twintig aanroepen per uur en zestig per dag
  per IP, een dagplafond van 800 en een noodrem (`AI_UIT=1`).
- **nachtrun** kiest voortaan het gat dat er het meest toe doet (verschijnselen vóór woordgaten, zoals
  het commentaar altijd al beloofde) en maakt niets waar al genoeg ligt.
- **v23.43** de poort van dag 1 gaat weer dicht: een vers profiel viel per ongeluk onder de
  coulanceregel voor bestaande spelers, en de eis telt nu wat de bouwer echt in handen krijgt. Zie
  punt 1 hieronder.
- **v23.44** de helling: het aanmeldscherm vraagt je niveau niet meer maar vertelt het, na dertig
  woorden in één doorlopende beleving. Zie punt 1b hieronder.
- **v23.45** op het Vandaag-scherm staat niets dat nul is, en wie net de helling deed krijgt geen
  tweede peiling aangeboden. Zie punt 1c.
- **v23.46** de meting is een meting: de dertig woorden leveren geen taco's meer op, alleen de drie
  proefwoorden. Zie punt 1c.
- **v23.47** de onboarding zegt alleen nog dingen die waar zijn: vier teksten die niet waren
  meegegroeid met de app. Zie punt 1d.
- **v23.48** geen verzonnen werkwoordsvormen meer: twee grammaticaconcepten bouwden hun Nederlandse
  en Engelse vertaling met knip- en plakwerk op de infinitief. 90 kapotte NL- en 68 kapotte
  EN-vormen. Zie punt 6.
- **v23.49** de taalsalade weg: de app bood vier talen en heeft er twee. Zie punt 7, en dat is
  meteen de belangrijkste sectie van dit document geworden.
- **v23.50** de afleiders in de toets zijn van dezelfde woordsoort (van 15% raadbaar naar 0%), en
  de uitslag belooft geen verschil tussen A0 en A1 meer, want dat verschil bestaat niet. Zie punt 7.
- **v23.51** de knop staat waar je hem zoekt: "Volgende zin" stond ná de uitleg en de
  luisterknoppen en viel daarmee op 390 pixels onder de vouw. Nu direct onder de uitslag. Bevinding 3
  van de telefoontest, zie punt 7.
- **v23.52** na je les stuurt de app je niet meer naar een deur die op slot zit, en het antwoord op
  "en nu?" staat binnen het scherm. Bevinding 4 van de telefoontest, zie punt 7.
- **twee tijdbommen in de poort onschadelijk gemaakt.** `pw-samen` ging vannacht om middernacht af:
  hij zette `S.samen.gedeeld` op de vaste datum `2026-07-29` en `UITNODIG_RUST` is 14 dagen, dus op
  11 aug was dat dertien dagen (groen) en op 12 aug veertien (rood). `pw-maatje` had dezelfde
  constructie met een drempel van 21 dagen en zou op 19 aug zijn omgevallen. Beide rekenen nu vanaf
  `today()`. **Een suite met een datum erin heeft een houdbaarheidsdatum, en die staat nergens.**
- **pw-clasificador** is niet meer wisselvallig (punt 5 hieronder). Geen tijdsprobleem maar een
  dobbelsteen: `clNieuwSpel()` zonder id koos een willekeurig concept, en bij een concept met weinig
  patronen was de ronde al klaar vóór de misser die de test wilde meten. Staat nu op `serestar`.
- **v23.53** de grammatica heeft een volgorde (`GC_ORDE`, 23 onderwerpen van makkelijk naar
  moeilijk) en die volgorde is een poort. Dag 1 ging van vijftig open onderwerpen naar acht, en de
  grammatica-stap van je eerste les van *qué of cuál* naar *el of la*.
- **v23.54** een laadscherm dat na 822 ms staat in plaats van een dode kop, met drie noodremmen
  zodat het nooit blijft hangen. En "¡Vamos …!" is "¡Vamos!" geworden.
- **v23.55** het proefscherm zit in een eigen klein scriptblok bóven het grote: de eerste knop
  waar je op kunt tikken staat er na 567 ms in plaats van na 4911.

## Wat er open staat, op volgorde van hoe erg het is

### 1. Dag 1 van een vreemde is te vol

De app heeft negen spellen, Chispa met tapas en dansjes, een boek, liedjes, een avontuur, een muur,
een maatje, een peiling en een voortgangspagina. Voor Stefan is dat rijkdom, voor iemand op dag 1 is
het ruis. De regel uit gedragsontwerp is één handeling op dag 1.

De machinerie staat er al: `SPEEL_EIS` houdt spellen dicht tot je genoeg woorden kent, en
`lessonUnlocked` doet hetzelfde voor lessen. Ze staan alleen ruim afgesteld. Dit is aanpassen en niet
bouwen.

**Correctie, 11 aug (v23.43): ze stonden niet ruim afgesteld, ze stonden uit.** Nagemeten op een vers
A0-profiel in een browser. `speelOoitInit()` geeft iedereen met iets in `S.srs` al zijn spellen cadeau
(de coulanceregel van v19.92: wie al oefende raakt door een update niets kwijt), en het proefscherm
zet drie woorden in `S.srs` voordat er een profiel bestaat. Elke vreemde viel dus onder de coulance en
`SPEEL_EIS` deed sinds v19.92 niets voor precies de groep waarvoor hij bedoeld was. Op dag 1 met drie
geleerde woorden: Clasificador opende op indefinido-of-imperfecto, Crucigrama kaatste terug met "Leer
eerst wat meer woordjes", El Corrector opende met acht zinnen op vijf vrijgespeelde.

Wat v23.43 doet: een vers profiel begint met een lege `S.speelOoit` (één regel in `boot()`, boven het
blok dat de proef verzilvert, want daaronder is `S.txp` niet meer nul), en de eis telt voortaan wat de
bouwer echt in handen krijgt in plaats van je woordenteller. Dat laatste is geen extraatje: de eerste
dertien A0-woorden zijn begroetingen en uitdrukkingen (`por favor`, `buenos días`, `¿cómo estás?`,
`uno dos tres`) en `wsWoordPool()` gooit die allemaal weg. Gemeten met `kruisBouw()`, vijf pogingen per
stand: tot en met dertien woorden nul van de vijf geslaagd, vanaf veertien vijf van de vijf. De oude
eis van twaalf woorden liet het kruiswoord dus ook zonder de coulancebug open op een moment dat hij
niet kon bouwen. `ws`, `kruis` en `mem` staan nu op precies de ondergrens die hun eigen bouwer
hanteert; `letras`, `adiv`, `audi`, `clas` en `corr` blijven op je teller staan, want hun eis zegt
"hier ben je nog niet aan toe" en dat is een andere uitspraak dan "hier is niet genoeg van".

Onderweg gevonden en meegenomen: `dagSpelKeuze()` liep met een stap van 2 door de lijst speelbare
spellen, en bij een lijst van twee komt dat drie keer op dezelfde uit. Zolang er negen spellen open
stonden viel dat nooit op; zodra de eis bijt stond er op dag 1 twee keer Rompecabezas en ontbrak het
spel dat wel kon.

Wat een vreemde nu ziet: na de proef (3 woorden) Aventura en Rompecabezas, na de eerste les (8)
komt Memory erbij, en rond woord 14 de Woordenzoeker en Crucigrama. Vastgelegd in `pw-dag1.js`, dat
niet de teksten bewaakt maar de belofte: een tegel staat er alleen als het spel er ook echt uit kan
komen, gecontroleerd door de bouwer zelf aan te roepen. Op de oude `index.html` zakt die suite op acht
punten.

**Wat hier nog open staat.** De reparatie haalt de kapotte knoppen weg, maar het scherm is nog niet
leeg. Dag 1 telt nog steeds negentien zichtbare knoppen en verwijzingen, een balk van vijf en een
modal van twee stappen, en het eerste getal dat een vreemde ziet is een **0** ("0 van je 3 woorden").
Eén handeling op dag 1 betekent: EVEN SPELEN en de cijferregel weg tot je je eerste les af hebt. Dat
is het volgende verhaal, en het is een eigen versie waard.

### 1b. Het aanmeldscherm vroeg de enige vraag die een vreemde niet kan beantwoorden (v23.44, af)

Stefan, 11 aug: "als je begint ben je misschien gemotiveerd en wil je wel iets meer woordjes doen.
Je krijgt 30 woorden, dan schatten we je niveau in." En daarna: "kunnen we er niet een geïntegreerde
beleving van maken?"

Waarom dertig het goede getal is, en niet twaalf: `PEIL_MIN_N` staat op 20. Onder twintig antwoorden
weigert `niveauSchatting()` iets te zeggen, en de bestaande peiling gaf er twaalf. Een vreemde die op
dag 1 de peiling deed kreeg dus letterlijk "Bedankt. Nog 8 antwoorden en de balk kan je niveau
schatten": een meting die weigert te meten, op de dag dat iemand het meest gemotiveerd is.

De helling is één doorlopende beleving. Hij begint zoals de proef altijd al begon (hola, gracias,
adiós, viertalig, geen account), stopt daar niet meer maar biedt aan door te gaan, en loopt door tot
dertig. Daarna vraagt het aanmeldscherm je niveau niet meer maar vertelt het: "Op grond van je
woorden zetten we je op A1. Klopt dat niet? Kies hieronder zelf."

**Niet adaptief, en dat is een keuze en geen luiheid.** `niveauSchatting()` legt een Wilson-band om
de steekproef, en die band veronderstelt dat de steekproef aselect is. Een ladder die zijn volgende
vraag kiest op grond van je vorige antwoord levert precies dat niet, en dan is de marge eromheen
versiering. Dertig willekeurige A1-sleutels geven vanzelf makkelijk (aprender) en lastig (tímido)
door elkaar, dus het voelt gevarieerd zonder dat de meting kapotgaat.

Twee dingen moesten eerst weg. Vóór het eerste profiel staat `WORDS` op de kleine standaardbak van
313 woorden, en dan haalt A1 twaalf procent van de Cervantes-noemer terwijl `peilMeetbaar()` er
tachtig eist: er was vóór het aanmelden geen enkel niveau meetbaar, en dat is precies het moment
waarop we willen meten. De helling laadt daarom zelf de ruime bak (2184 woorden, A1 op 405 van de
409). En `pcicKeysApp()` bewaart zijn sleutelkaart in `_peilKeys` zonder dat `boot()` die leegmaakt;
zolang niemand hem vóór het aanmelden aanriep viel dat niet op, maar de helling doet dat juist wel.
`boot()` maakt hem nu leeg.

De hybride, zoals afgesproken: goed beantwoorde woorden krijgen `claim:1` in doosje `SWEEP_BOX`,
precies zoals de inhaalslag ze zet (een voorsprong, geen bewijs, en `S.sweep` telt later of jouw "die
ken ik" klopte). Fout beantwoorde woorden gaan **niet** in `S.srs`: ze zitten al in je leerlijn, en ze
daar op doosje nul zetten zou ze laten meetellen als "geoefend" terwijl je ze alleen hebt gezien.
Dat is de fout uit `claude/rapport.md` punt 1. Alle dertig gaan wel als sleutel naar `S.peil.items`,
dus de voortgangspagina hoeft vanaf dag 1 niet meer te zwijgen.

De oude weg blijft heel: de drie vaste woorden, de vier niveauknoppen en de niveautest van tien
grammaticavragen werken onveranderd, "nee, ik maak gewoon een profiel" komt uit op precies het scherm
van hiervoor, en een bak die onverwacht niet meetbaar is valt daar vanzelf op terug. Bij het
allereerste scherm, drie dagen voor een lancering, wil je die terugvalweg hebben.

Vastgelegd in `pw-helling.js`. Twee dingen die daarbij misgingen en het onthouden waard zijn: mijn
eerste uitslagscherm noemde een puntschatting ("ongeveer 195 van de 409 A1-woorden") en na het
aanmelden rekent dezelfde schatter over de kleinere bak van je track en zegt 182 — zelfde vraag,
twee getallen, twee schermen na elkaar, dus maatstaf 1 van `rapport.md`. Het uitslagscherm telt nu
alleen nog wat het echt geteld heeft. En de suite was groen als losse run en rood in de poort, puur
door vaste pauzes die net onder de `setTimeout` van het scherm zaten; hij wacht nu op de toestand.

**Nog open hier:** onder het voorstel staat nog steeds "Kies een niveau, of doe de test van 10
vragen". Dat is nu een tegenspraak in het klein: de app heeft je niveau net verteld. Die regel hoort
te veranderen in een uitweg ("liever zelf kiezen?") in plaats van een opdracht.

### 2. De eerste indruk duurt te lang

`index.html` is 2,3 MB en bevat alle content. In de testomgeving laadt hij in 800 ms; op een
gemiddelde telefoon op 4G is vijf tot acht seconden wit scherm realistisch. Dat is precies het venster
waarin een vreemde wegklikt.

**Nagemeten op 11 aug**, want dit stond hier als schatting en dat is niet goed genoeg voor een punt
dat zo hoog op de lijst staat:

    verbinding                    eerste pixels    eerste knop die werkt
    geen rem                          76 ms                0,4 s
    4G (9 Mbit, 85 ms, 2x cpu)       184 ms                2,9 s
    traag 4G (1,6 Mbit, 300 ms)      724 ms               12,8 s

**Correctie op 12 aug.** Hierboven stond dat het aanmeldscherm er na 0,7 seconde staat "mét de
naamvelden en de niveauknoppen". Dat klopt niet: `<section id="tab-profiel">` heeft `class="hidden"`
in de statische HTML en wordt pas door het script zichtbaar gemaakt. Nagemeten wat er in dat gat
écht staat, traag 4G, 390 bij 844, cpu 4x geremd:

      964 ms   "¡Vamos …! Chispa ↑"
    13626 ms   het proefscherm verschijnt

Twaalf en een halve seconde een kop met drie puntjes en een Chispa-balk. Dat is niet "de app laadt
langzaam", dat is een pagina die eruitziet alsof hij klaar is en niets doet. Wit was eerlijker
geweest.

**AF in v23.54: het laadscherm.** Staat in de statische HTML met zijn stijl in het bestaande
`<style>`-blok, dus zonder één extra verzoek (dat kost op zo'n verbinding precies de tijd die je
probeert te winnen). Gemeten na de reparatie:

      822 ms   "¡Vamos!" + onbepaalde balk + "Even geduld, we zetten je Spaans klaar."
     7008 ms   erbij: "Dit duurt alleen de eerste keer."
    13558 ms   weg, proefscherm eronder

Geen percentage maar een onbepaalde balk: er ís geen voortgang te melden, het is één script dat
bezig is of klaar. Een balk die naar 80% kruipt en daar blijft hangen is een leugen met een animatie
eromheen. De regel over "de eerste keer" komt pas na zes seconden, want bij een snelle verbinding is
het scherm dan al weg en zou hij een probleem aankondigen dat er niet is.

**Drie noodremmen**, want een laadscherm is een gordijn dat je voor je eigen app hangt: blijft het
hangen, dan heb je de app niet trager gemaakt maar onbruikbaar. (1) `window.onerror` haalt het weg,
(2) een harde noodrem na 30 seconden, (3) het minitscript dat dit regelt staat direct onder het
scherm in de HTML en is losgekoppeld van het grote script. `pw-laadscherm.js` toetst dat allemaal
door het grote script écht te laten omvallen (via routing die een `throw` injecteert) en dan te
kijken of het gordijn tóch opengaat.

De echte oplossing — content per niveau laden — is de eerste grote verbouwing ná de lancering. Deze
versie maakt de wachttijd niet korter, alleen eerlijk. Dat is het verschil tussen iemand die wacht
en iemand die wegklikt.

### Tweede correctie, 12 aug: alle getallen hierboven zijn gemeten zónder compressie

Stefan vroeg of de index niet anders opgebouwd moet worden, of andere infra niet de structurele
oplossing is. Bij het nameten bleek eerst iets anders: **de testserver stuurt het bestand
ongecomprimeerd, en de productieserver niet.** Alle cijfers hierboven (12,8 s, 13,6 s) zijn dus
metingen van 2,4 MB over de lijn, terwijl er in productie 806 KB gaat.

Opnieuw gemeten met gzip en met de cacheheaders die GitHub Pages stuurt (`max-age=600` plus ETag),
traag 4G (1,6 Mbit, 300 ms rtt, cpu 4x):

    eerste bezoek                4911 ms    806 KB over de lijn
    tweede bezoek (binnen 10 m)   698 ms      0 KB  (304)
    na een deploy                4911 ms    806 KB  (bestand is veranderd)

**Het probleem is dus 2,4 keer kleiner dan hier stond.** Vijf seconden, niet dertien. En herhaalde
bezoeken zijn al goed, zolang je binnen het cachevenster valt en er niet net gedeployd is.

*Niet geverifieerd:* of vamos.stefanwobben.nl echt comprimeert. Deze omgeving komt niet bij het
publieke internet. Eén regel om het zelf te controleren, en dit is de belangrijkste van dit hele
punt, want als het antwoord "nee" is klopt er niets van bovenstaande:

    curl -sI -H 'Accept-Encoding: gzip, br' https://vamos.stefanwobben.nl/ | grep -i 'content-encoding\|cache-control'

### Wat het bestand eigenlijk is

Opgemeten met een echte parser (acorn) in plaats van met reguliere expressies, want die telden
overlappende blokken dubbel:

    bestand                2440 KB
      script               2334 KB
        data-literals      1205 KB  (52%)
        functiedeclaraties  762 KB  (33%)
        de rest             368 KB
      html + css            106 KB

De grootste blokken: FREQ 132, GRAMWIZ 125, FREQ_EN 121, C_WORDS 113, SENTENCES 98, GC_CONCEPTEN 89,
QUIZZES 77, DICINFO 54, BOOK 46, CHEATSHEET 44, B_QUIZZES 42.

### Wat de opties waard zijn, gemeten en niet geschat

    variant                              over de lijn    op traag 4G
    nu (gzip)                                 806 KB         4,1 s
    geminifyd (gzip)                          651 KB         3,3 s
    nu (brotli)                               639 KB         3,3 s
    geminifyd (brotli)                        523 KB         2,7 s
    schil zónder álle data (gzip)             422 KB         2,1 s

De onderste regel is een bovengrens die niet haalbaar is: een A0'er heeft zijn woorden, zinnen en
toetsjes meteen nodig. Realistisch uitstelbaar is FREQ, FREQ_EN, DICINFO, BOOK, SONGS, GRAMWIZ en
het A2-materiaal voor wie op A0 zit — ruim 500 KB ruw, en dan zit je rond de 600 KB gecomprimeerd.

**Andere infra levert precies één ding op: brotli** (806 → 639 KB, 0,8 seconde). GitHub Pages is al
een CDN; het knelpunt zijn de bytes, niet de host. Verhuizen om iets anders dan brotli is een
oplossing voor een probleem dat er niet is.

### De volgorde ná de lancering, op waarde gedeeld door kosten

1. **De curl hierboven.** Nul werk, en als het antwoord tegenvalt is het meteen de grootste winst
   die er te halen is.
2. **Een service worker.** Het eerste bezoek verandert niet, maar élk bezoek daarna is meteen klaar,
   ook buiten het cachevenster en ook vlak na een deploy (stale-while-revalidate: je krijgt de oude
   versie direct en de nieuwe de keer erna). Voor een app die je elke dag vijf minuten gebruikt is
   dat meer waard dan minify en brotli samen, en het is het enige dat ook offline werkt.
3. **Minify in de deploy-stap.** 806 → 651 KB zonder één regel code te veranderen. Wel eerst de
   poort op het gebouwde bestand laten draaien in plaats van op de bron, anders test je iets anders
   dan wat er live staat.
4. **Content per niveau splitsen.** De grootste winst, en veruit de duurste: het raakt overal, en
   het breekt de eigenschap waar de patch-werkwijze en de poort op leunen (één bestand, één anker,
   één diff). Pas hierna.

### AF in v23.55: het eerste scherm wacht niet meer op de app

Stefan koos, gevraagd wat erger is: **de vreemde die wegklikt**, niet Ilona die na een deploy wacht.
Dat sluit de service worker uit als eerste stap (die doet niets voor een eerste bezoek) en zet alles
op het eerste scherm.

En dan blijkt het antwoord niet "kleiner maken" maar "eerder beginnen". De vreemde hoeft namelijk
helemaal niet op de app te wachten: het eerste dat hij ziet is geen app, het zijn drie woordjes met
elk twee knoppen. Dat is 2,3 KB, en dat kan mee met de statische HTML.

Dus staat het proefscherm nu in een eigen klein `<script>`-blok bóven het grote. Gemeten, traag 4G:

    eerste knop waar je op kunt tikken     567 ms   (was 4911 ms)
    getikt, antwoord opgeslagen            591 ms
    vraag 2                               1907 ms
    grote script klaar, neemt het over    5136 ms   op dezelfde vraag, met je antwoord intact

Niets is gekopieerd: `PROEF_WOORDEN`, `PROEF_TXT`, `UI_LANGS`, `browserTaal()` en de proef-opslag
zijn verhuisd, en het zijn globals dus het grote script ziet ze onveranderd. Wat er bij komt is
`vroegVraag()`, veertig regels, en die schrijft in `{bezig:true, stand:{i,xp,res}}` — precies het
formaat waar `renderProef()` sinds v23.44 al uit hervat. De overdracht is dus geen nieuwe koppeling
maar een bestaande, en dat is waarom dit twee dagen voor een lancering kon.

**Bijvangst, gevonden door een test die omviel:** valt het grote script om, dan staan de drie
proefwoorden er tóch. Een kapotte app is geen wit scherm meer maar een app die minder kan.

**Drie meetfouten van mezelf, voor de volledigheid.** (1) Het vroege blok stond eerst bóven
`<div class="wrap">` en deed daarom niets: een inline script draait op het moment dat de parser hem
tegenkomt, en `#profCard` bestond dan nog niet. (2) `waitForSelector` rapporteerde 5560 ms terwijl de
knop er op 567 ms stond — die waiter draait in de pagina en de hoofddraad is vanaf één seconde bezig
met parsen. Pollen met `evaluate` in de gaten tussen de chunks geeft het echte moment. (3) Twee keer
getoetst op `typeof renderProef === 'undefined'` om te bewijzen dat een script niet gedraaid had:
functiedeclaraties worden bij het parsen gehoist en bestaan ook na een `throw`.

`tools/syntaxcheck.js` stond op "precies één inline scriptblok" en dat klopte sinds v23.54 niet meer.
Hij controleert nu elk blok apart en meldt in welk blok een fout zit.

### 3. De taal van het eerste scherm

Het proefscherm ("hola, wat betekent dit") stond in de testomgeving in het **Engels**, in een omgeving
zonder Nederlandse taalinstelling. Als dat een Nederlandse bezoeker ook overkomt, ben je hem in twee
seconden kwijt. Nakijken hoe de taal vóór het eerste profiel gekozen wordt.

### 4. Progressie kwijtraken

Alles staat in localStorage. Er zijn synccodes, dus herstel kán, maar een vreemde die zijn browser
leegt weet niet dat die code bestond. Het synccode-moment hoort ná de eerste voltooide les, niet
ervoor.

### 5. Kleine dingen die wel opvallen

- Bij een geblokkeerde AI-aanroep zegt de app "De AI is even niet bereikbaar". Sinds het slot op de
  server klopt dat niet meer: de echte reden staat in `res.fout` en die is vriendelijker.
- ~~De titel toont "¡Vamos …!" met een naam die er nog niet is.~~ **AF in v23.54:** het is
  "¡Vamos!" tot je een naam hebt. De spatie zit nu aan de naam vast in plaats van in de HTML.
- `/api/sync` en `/api/log` staan open. Kosten geen geld, wel rommel in de database.
- De privacytekst moet kloppen met wat de server echt bewaart.

## De architectuur die eraan komt: koppelen in plaats van produceren

Stefan, 11 aug: "de mensen met het hoogste niveau maken als pioniers de content, iedereen die daarna
komt kan veel hergebruiken. Dan is het voor de LLM minder produceren en meer koppelen van niveau en
fouten aan de juiste les."

Dat klopt, en de helft ervan is al waar: de content staat in één gedeelde bak in `index.html`, dus er
wordt al maximaal hergebruikt. Wat ontbreekt is de routering, en de oorzaak is aan te wijzen:

**Elke zin heeft één veld `tag`, en dat veld doet drie dingen tegelijk.** Van de dertig tags is
`les3` een les (21 zinnen), `cocina` een thema (12) en `imperfecto` een taalverschijnsel (13). Daardoor
kan de nachtrun niet vragen "welke bestaande zinnen drillen het verschijnsel waar deze fout over
gaat"; hij kan alleen vragen "hoeveel zinnen hebben dezelfde tag".

De weg vooruit, in drie stappen:

1. **Tag de bak één keer op verschijnsel.** Elke zin krijgt naast les en thema een lijstje van wat hij
   drilt (subjuntivo, ser tegenover estar, indefinido, por tegenover para, vergrotende trap). Eén
   LLM-ronde over 175 zinnen, eenmalig. Daarna is routeren gratis.
2. **Eerst zoeken, dan maken.** De eerste versie hiervan staat er sinds 11 aug: verzadigde onderwerpen
   worden overgeslagen. De volledige versie kan pas met stap 1.
3. **De pionier duwt alleen de rand op.** Nieuwe lessen worden alleen aan de voorkant gemaakt, voor
   het hoogste niveau dat iemand bereikt heeft.

Drie dingen die daarbij horen en die je anders half bouwt:

- De personalisatie verhuist van de inhoud naar de volgorde en de selectie. Dat is geen verlies, maar
  het betekent wel dat de routering het product wordt.
- De keuring moet strenger worden naarmate er meer hergebruikt wordt. Nu raakt een slechte zin één
  gebruiker; straks raakt hij iedereen, voor altijd.
- Aan de rand heeft de pionier een leerplan nodig en geen foutenlog. Wordt B1 op Stefans fouten
  gebouwd, dan krijgt iedereen straks drilzinnen over zijn rijbewijs.

## Twee cijfers om te onthouden

- **`voorraadDagen: 0`** in `tools/avondrun-hart.json`. Stefans plank met nieuwe woorden is leeg, en
  dat is de echte reden dat hij weinig nieuwe woorden krijgt: niet het tempo (dat geeft bij dertig
  minuten twaalf tot achttien per dag) maar de voorraad. Dit getal voorspelt zijn nieuwe woorden beter
  dan welk getal op de voortgangspagina ook, en het staat nu alleen in een bestand dat niemand opent.
- **412 van de 422** zelfstandige naamwoorden hadden hun lidwoord al goed vóór er een regel was. De
  inhoud is beter dan de controle erop; dat is een aanwijzing dat de regels achterlopen op de
  praktijk en niet andersom.

## Werkwijze, kort

Staat voluit in `DEPLOY.md`. De drie dingen die in deze sessie het vaakst misgingen:

- `git pull --rebase` vóór het patchen, altijd.
- Elke wijziging aan `index.html` via een idempotent pythonscript in `claude/` met een `rep()` die
  vastloopt als het anker niet precies zo vaak voorkomt. Nooit los zoeken en vervangen.
- Een script dat in meer dan één bestand schrijft, heeft per bestand een eigen vlag. "Al gedaan" en
  "hier valt niets te doen" zijn niet hetzelfde.

En twee dingen die specifiek in deze omgeving misgingen:

- De poort lokaal draaien vraagt eenmalig `cd test && npm install && npx playwright install chromium`.
  De `CHROMIUM=`-variabele is alleen nodig in de ontwikkelomgeving van de assistent, niet op Stefans
  Mac.
- Git draaien op Stefans schijf via de koppeling gaat mis: schrijven kan wel, verwijderen niet, en
  git heeft dat nodig om zijn eigen lockbestanden op te ruimen. Bestanden neerzetten is prima, git
  laat je aan Stefan.

### 1c. De onboarding zei dingen die niet meer waar waren (v23.45 en v23.46, af)

Nagemeten op de echte schermen, telefoonformaat, na v23.44. Vijf dingen klopten niet, en drie ervan
had ik er de dag ervoor zelf in gezet.

**Weg in v23.45.** Het eerste getal dat een vreemde van deze app te zien kreeg was een **0** ("van
je 3 woorden, gewogen naar hoe lang je ze onthoudt"). Die tegel verscheen bij `c.geoefend > 0`, en
dat zegt "er staat iets in je lijst" en niet "er valt iets te melden". Op dag 1 kán `kracht` niets
anders zijn dan nul. Nu verschijnt hij bij `c.kracht > 0`. Het Vandaag-scherm ging daarmee van drie
kaarten naar twee en van 1059 naar 810 pixels.

En: de app bood een peiling van twaalf woorden aan iemand die net dertig woorden had gedaan. De
helling schreef zichzelf niet weg als peiling, dus stond `S.peil.laatst` nog op `""` terwijl er wél
een schatting lag, en dan komt `peilAanbod()` via `peilDagenGeleden("")` = 9999 uit op aanbieden. De
helling registreert zich nu zoals `peilKlaar()` dat doet, inclusief een regel in `S.peil.log`. Dat
geeft de voortgangspagina meteen een nulpunt om groei tegen af te zetten.

**Weg in v23.46.** De helling deelde XP uit alsof het een oefening was: twee taco's per goed
antwoord, één per fout, zevenentwintig keer. Gemeten: 50 taco's op een dagdoel van 30, dus de
kopbalk zei **"doel gehaald ✓"** boven een knop die zei "start je les". Een tegenstrijdig bevel op
het enige moment dat een vreemde nog moet besluiten of hij hier iets gaat doen.

De regel die de app zelf al had, op het peilingscherm: *"Dit is een meting, geen les. Je punten en
je doosjes veranderen er niet van."* Stefan, 11 aug: "de meting is de meting." De drie vaste
proefwoorden houden hun taco's (+5), de dertig leveren niets meer op. Je begint dus op 5/30 en je
eerste les is nog steeds de weg naar je dagdoel. Op de vraagschermen staat het er nu ook bij:
"Deze woorden tellen niet voor je taco's, wel voor je startpunt."

**Nog open, en het is één verhaal (voorstel v23.47).** Drie teksten die niet zijn meegegroeid met
wat de app doet:

1. Onder het niveauvoorstel staat nog "Weet ik niet: doe de niveautest — Kies een niveau, of doe de
   test van 10 vragen (2 minuten)". Dat zijn tien grammaticavragen, en het is nu een tweede weg naar
   je niveau die een ander antwoord kan geven dan de dertig woorden erboven.
2. De dagles heet "6 woordjes (5 nieuw) · 1 grammaticapunt · 1 toetsje · 1 oefenronde". Vier
   gelijkwaardige stukken in de zin, zes tegen één in werk. Stefan: grammatica is maar een klein
   onderdeel nu.
3. De rondleiding belooft "hooguit 15 nieuwe woordjes"; bij het standaard dagdoel van 10 minuten is
   je portie er 5 en je plafond 8.

## Nieuwigheid: wat er vrijkomt, en dat niemand het merkt

Nagemeten door de drempel echt over te gaan, van 12 naar 16 geleerde woorden. Woordenzoeker,
Crucigrama en Adivina kwamen alle drie vrij.

Er gebeurt niets. `dagNieuwsRegels()` blijft leeg, er is geen "Nieuw voor jou"-kaart, en op Vandaag
staat geen enkel teken. De drie tegels zijn in de Speeltuin stil verhuisd van "Komt er straks bij"
naar de bovenste lijst. Om het te merken moet je zelf naar de Speeltuin gaan én je herinneren wat er
gisteren niet stond.

Dat is v19.92 ("verschijnen, niet ontgrendelen") die zijn eigen regel te ver heeft doorgevoerd. De
regel is goed tegen slotjes die je uitlachen, maar hij is doorgeslagen naar helemaal geen moment.

En er staat een inconsistentie naast: **lessen gebruiken wél een slot.** Op De cursus staat les 0
open en hebben 1 tot en met 9 een 🔒. Spellen krijgen de vriendelijke behandeling ("doet mee vanaf
25 geleerde woordjes · nu 16"), lessen de kale. Twee talen voor hetzelfde idee, in dezelfde app.

Wat "Nieuw voor jou" wél meldt: een nieuwe tapa, een nieuwe dans, een nieuwe fase in de Conjugador,
een afgeronde les, een niveau dat staat. De machinerie ligt er dus al.

De voorraad ligt er ook, en hij is groter dan gedacht: 9 spellen met drempels, 8 groeivormen voor
Chispa, 18 tapas, 11 winkelstukken, 23 boekhoofdstukken, 12 liedjes, 6 luisterscènes, 10 lessen,
de vier werelden van Aventura, de Conjugador-fases, het maatje, groepen en Palabra Duel. Het
probleem is niet aanbod maar aankondiging en tempo.

### 1d. Vier teksten die niet waren meegegroeid (v23.47, af)

Stefan, 11 aug, na het doorlopen van de schermen: "het verwijst ook nog naar oude dingen zoals
grammatica, want dat is maar een klein onderdeel nu." Het waren er vier, allemaal hetzelfde soort
fout: geen bug, de app werkt, hij vertelt het verkeerd. En juist daarom vindt niemand ze.

**De niveautest concurreerde met het voorstel.** Onder "we zetten je op A1" stond nog "Kies een
niveau, of doe de test van 10 vragen". De app vraagt niet meer om een keuze, dus dat is geen
instructie meer maar een tegenspraak, en die tien vragen gaan over grammatica terwijl je niveau nu
uit dertig woorden komt. Zodra er een voorstel staat verdwijnt de regel en heet de knop wat hij is:
"Liever de grammaticatest van 10 vragen?" Het woord *niveau* is nu van de dertig woorden. Wie de
helling overslaat houdt het oude scherm, want daar bepaalt die test je niveau wél.

**Grammatica kreeg een kwart van je dagles.** "6 woordjes (5 nieuw) · 1 grammaticapunt · 1 toetsje ·
1 oefenronde" gaf vier onderdelen evenveel gewicht terwijl het in werk zes tegen een is. Nu: "6
woordjes (5 nieuw) · daarna kort: grammatica, een toetsje en oefenen".

**De rondleiding beloofde vijftien nieuwe woordjes** terwijl je er bij het standaard dagdoel vijf
krijgt (plafond acht). "Hooguit" maakt dat formeel waar en praktisch misleidend. De zin rekent nu
met je eigen instelling, via een plaatshouder die `showTour()` invult.

**En hij wees naar schermen die niet bestaan.** Twee stappen, die verschijnen als je de rondleiding
later zelf opent via de voetregel, beschreven een app van maanden geleden: "Onder Grammatica staat
elk onderwerp opgeknipt in stappen", "de ronde 📖-knop bovenin is je woordenboek", "in de
Speeltuin", "Tik op je naam bovenaan voor je voortgang". Nagemeten: de balk heeft vijf plekken
(Vandaag, Woordjes, Oefenen, Spelen, Meer), Grammatica is één van vier tegels ónder Oefenen, de
📖-knop is sinds v21.6 de pil "🔍 Zoek" (juist veranderd omdat Stefan zelf niet wist dat dat boekje
het woordenboek was), en Voortgang zit sinds v23.32 onder Meer. Dit is de gemeenste van de vier: het
is de tekst achter de link "Rondleiding", dus precies wat iemand opent als hij het niet meer weet.
Verouderde hulp is erger dan geen hulp.

## 6. De content: waar de app zelf zinnen maakt (v23.48, af)

Aan het eind van 11 aug de hele bak nagelopen op wat een vreemde te zien krijgt. Eén klasse fouten
sprong eruit, en hij begon met een zin die Stefan zelf op zijn scherm zag:

    Todos los días ___ con mi abuela.  (Elke dag reizende ik met mijn oma.)

Geen typefout maar een sjabloon. Twee van de drieëntwintig grammaticaconcepten bouwden hun
vertaling met knip- en plakwerk op de infinitief:

    "Elke dag "+w.nl.replace(/r$/,"")+"de ik ..."   ->  reizen -> "reizende ik"
    "heb ik veel ge"+w.nl.replace(/en$/,"")+"t."    ->  reizen -> "gereizt"
    "I "+w.en+"ed a lot."                            ->  eat    -> "eated"

Gemeten door elk patroon van alle concepten tweehonderd keer te draaien: **1074 varianten, 90
kapotte Nederlandse vormen en 68 kapotte Engelse**, allemaal in `perfindef` en `indefimperf`.
Gereizt, gewont, gestudert, geett, gepratt, reizende ik, wonende ik, eated, liveed, studyed.

Waarom dit zo lang bleef staan: bij "werken" komt er toevallig "gewerkt" uit. Het werkte voor het
eerste werkwoord dat je toetste.

De vormen worden nu niet meer afgeleid maar opgeschreven. `GC_PAS` heeft er vier velden bij per
werkwoord (`nlVt`, `nlVd`, `enVt`, `enVd`). Vierentwintig woorden die één keer goed staan, in plaats
van een regel die bij elk nieuw werkwoord opnieuw kan misgaan.

Twee dingen die er onderweg bij kwamen. Het Engelse sjabloon zette het tijdvak altijd vooraan, dus
"Nunca" werd "Never I eated a lot"; nu "I have never eaten much". En het patroon `Un día ___ algo
increíble` trok uit alle zes de werkwoorden, terwijl *hablé algo increíble*, *trabajé algo
increíble* en *viajé algo increíble* geen Spaans zijn. Oefenen op een zin die niet bestaat is erger
dan een scheve vertaling, dus dat patroon trekt nu alleen uit werkwoorden met de vlag `obj`.

Vastgelegd in `pw-vormen.js`, de 64e suite. Hij bewaakt de regel en niet de zinnen: hij leidt uit
`GC_PAS` zelf af wat een naïeve afleiding zou opleveren, gooit weg wat toevallig ook een echte vorm
is, en kijkt of die verzonnen vormen ergens in de gegenereerde tekst opduiken. Voeg je morgen een
werkwoord toe, dan doet dat vanzelf mee. Draai één patroon terug en hij valt om op zes punten.

**Wat er schoon doorheen kwam.** De andere eenentwintig concepten: geen lege uitleg, geen dubbele
antwoordopties, geen antwoordindex buiten bereik, overal een Engelse variant. De patronen met drie
of vier opties zijn geen fout: Clasificador filtert zelf op twee, de Grammatica-tab gebruikt ze wel.

**Wat er nog ligt in deze hoek.** `vivir` staat in `GC_PAS` met de Nederlandse vertaling "wonen", en
dat klopt in "Als kind woonde ik in Sevilla" maar niet in "Dit jaar heb ik veel gewoond" (daar is
*he vivido mucho* eerder "geleefd"). Eén werkwoord met twee betekenissen in één veld. Kleine
verbetering, eigen versie waard, en niet urgent: de zin is niet fout, alleen houterig.

## 7. De telefoontest van 11 aug: zes bevindingen (WERKLIJST VOOR WOENSDAG)

Stefan zette v23.48 live en liep hem 's avonds voor het eerst door op zijn eigen telefoon, in een
privévenster, als vreemde. Tien minuten. Zes bevindingen, waar geen van de 64 suites op sloeg.

Niet omdat de tests slecht zijn, maar omdat ze allemaal in het Nederlands draaien, op een snelle
machine, met een profiel dat de tester zelf maakte. **De poort bewaakt wat we al weten; een vreemde
vindt wat we niet wisten.** Dat is het argument om er vóór vrijdag nog twee of drie doorheen te
sturen.

### Af: de taal (v23.49)

Zijn telefoon staat op Duits. Eén scherm, drie talen: de balk Duits, de schermtekst Engels, de
woordbetekenis Nederlands. De oorzaak, geteld in de bron:

    ct(nl, en)                927 aanroepen    2 talen
    tt(key) via TXT             9 aanroepen    4 talen
    TRANS (woordbetekenis)                     en 794 · fr 420 · de 420
    proefTaal() eigen tabel                    4 talen, los van de rest
    profLang() zonder profiel                  altijd "nl"

927 tegen 9. De app is tweetalig en het keuzemenu belooft vier vlaggen. `ct(nl, en)` maakt het
goedkoop om een Nederlandse zin toe te voegen en onmogelijk om een Duitse: de vorm van die functie
bepaalt hoeveel talen de app kan hebben, en dat is nooit bewust gekozen.

v23.49 snoeit tot wat waar is: nl en en, één functie `taalWeHebben()` in plaats van drie tabellen,
`profLang()` valt zonder profiel terug op `newLang`, bestaande de/fr-profielen gaan bij het opstarten
naar en, en de helling vraagt alleen woorden waarvan de betekenis in jouw taal bestaat. Dat laatste
kost bijna niets: Engels dekt 36% van de bak maar 97% van de A1-kern (416 van 427).

Wat er open blijft: buiten A1 ziet een Engelse gebruiker nog Nederlandse betekenissen. Dat vraagt
1390 vertalingen erbij, of dezelfde filter op de hele leerlijn (en dan krimpt de app voor hem van
2184 naar 794 woorden). Eerste grote klus ná de lancering, samen met het splitsen van de content.

### Open, op volgorde van bouwen

**6. De toets schaalt te hoog in — AF in v23.50, maar anders dan gedacht.** Stefan: "bijna de helft
kan je raden." Nagemeten op 200 getrokken vragen: bij **30 (15%)** was het goede antwoord het enige
van zijn woordsoort, en dat is echt kapot. `peilOpties()` viel bij een tag met weinig woorden meteen
terug op de hele bak van 2184. Nu is de volgorde zelfde tag én soort, dan zelfde soort, dan zelfde
tag, dan pas alles. Gemeten na de reparatie: 0%.

De andere helft van "je kunt de helft raden" zijn cognaten (*el hospital*, *el mapa*, *la
biblioteca*). Wie die herkent, kent ze ook echt: dat is woordenschat die je meebrengt, en een
A1-schatting hoort die mee te tellen. Daar valt niets te repareren zonder de meting te laten liegen.

**En de grootste vondst zat eronder: A0 en A1 zijn hetzelfde.** Beide knoppen hebben
`data-track="beginner"`, het profiel bewaart alleen `track`, en `lvl` wordt nergens opgeslagen.
`TRACKS` kent er twee. Drie knoppen, twee uitkomsten. "Te hoog ingeschaald op A1" heeft dus geen
enkel gevolg voor wat je leert; de grens die er wél toe doet is die naar A2 (POORT_PCT 0,85, dus
ongeveer 348 van de 409 A1-woorden) en daarachter wordt heel A1 als geclaimd weggezet. De uitslag
zegt nu wat er echt gebeurt ("Je begint bij het begin, bij les 1") in plaats van een label dat niets
doet. **Of A0 en A1 écht uit elkaar moeten is curriculumwerk en hoort na de lancering.**

De oude tekst hieronder, voor de volledigheid. Bij *el jardín* waren de afleiders *de badkamer*, *hoeveel kost het?* en *blauw*: een
kamer, een vraag en een kleur. Je elimineert op soort zonder het woord te kennen. `peilOpties()`
neemt afleiders uit dezelfde categorie alleen als er drie beschikbaar zijn, anders uit de hele bak.
Daar komt bij dat veel A1-woorden cognaten zijn (jardín, hospital, pizarra) terwijl de gokcorrectie
in `niveauSchatting()` (r − f/3) blind raden veronderstelt en geen geïnformeerd elimineren. Fix:
afleiders uit dezelfde woordsoort en categorie, en de drempel omhoog. Raakt waar iedereen begint,
dus eerst.

**3. "Next sentence" vind je niet — AF in v23.51.** Na Check stond eerst de uitslag, dan de uitleg,
dan de luisterknoppen, en pas daaronder de knop; op 390 pixels valt die onder de vouw. De volgorde is
nu uitslag, knoppen, uitleg, luisterknoppen. Bewust géén automatische doorloop: dan pak je het moment
af waarop je de zin nog kunt horen, en dat moment staat er met opzet. Het probleem was dat je de knop
niet zag, niet dat je erop moest tikken. Vastgelegd in `pw-zintegels.js`, dat nu de volgorde van de
blokken controleert én of de knop binnen het scherm valt.

**4. Het loopt dood na de dagles — AF in v23.52, en het lag anders dan gedacht.** Het klaar-scherm
had wél alles wat Stefan miste: de tapa-knop voor Chispa, "Nog een les doen", en twee voorstellen.
Er waren twee andere dingen mis.

*Het voorstel wees naar een gesloten deur.* Op dag 1 stelde `lesFlowWinst()` **El Corrector** voor
("11 regels staan op herhaling"), terwijl `speelKlaar("corr")` false is: dat spel doet mee vanaf acht
vrijgespeelde zinnen en een vreemde heeft er vijf. De poort van v23.43 verbergt de tegel, maar dit
voorstel roept `speelNaar("corr")` rechtstreeks aan. Een tweede deur naar dezelfde gesloten kamer,
precies op het moment dat iemand besluit of hij doorgaat. En na die reparatie kwam **Escuchar**
bovendrijven (vanaf twintig woorden), want `lesFlowVaardigheidOpen()` keek alleen of je die
vaardigheid vandaag al had gedaan. Beide volgen nu dezelfde poort. Op dag 1 blijft "Zinnen vertalen"
over, en dat kan een vreemde met drie woorden echt doen.

*En het antwoord viel van het scherm.* Gemeten op 390 bij 844: "LES AFGEROND" op 142, "HIER WIN JE
HET MEESTE" op 616, "OF GEWOON LEUK" op 865. Eenentwintig pixels eronder, en uitgerekend op dag 1 is
die eerste kaart het langst omdat er dan ook "Tot morgen?" in staat. Die zin staat nu onder de
knoppen (hij gaat over morgen), en de twee voorstelkaarten zijn één kaart "En nu?" geworden. Dat is
ook eerlijker: het zijn geen twee mededelingen maar één vraag met twee antwoorden. Resultaat: twee
kaarten in plaats van drie, "En nu?" begint op 609, paginahoogte van 1303 naar 1225.

Vastgelegd in `pw-naronde.js`, dat de poort zelf even dichtzet en kijkt of de voorstellen dat
respecteren. Draai je die ene regel terug, dan valt hij om.

**2 en 5, samen één verhaal: de app weet niet wat makkelijk is — AF in v23.53.**

Gemeten op een vers A0-profiel: de Grammatica-tab had 23 conceptkaartjes plus 5 diepe lessen plus 22
gegenereerde onderwerpen, **vijftig onderwerpen, allemaal open**. De grammatica-stap van de eerste
dagles was `concept-quecual`, en Chispa's Clasificador bood *por of para* en *perfecto of indefinido*
aan. Stefans voorbeeld was geen ongelukje: `lesFlowGramId()` pakt een concept dat aan een
spiekbriefkaart van je huidige les hangt, en les 1 verwijst naar kaart 4, en daar hangt qué-of-cuál
aan. De app deed precies wat er stond.

*Eerst geprobeerd en verworpen: de volgorde uit de data afleiden.* Elke les verwijst naar
spiekbriefkaarten en elk concept hangt aan zo'n kaart, dus daar valt een rangorde uit te halen.
Gemeten (A0, 10 lessen): les 0 quecual, les 1 serestar, les 2 genero, les 3 muymucho + hayestar, les
4 concordancia + demostrativo, les 5 gustar, les 6 reflexivo, les 7 pedirpreguntar, les 9 perfindef +
saberpoder. **Elf van de drieentwintig hangen aan geen enkele les.** Die afgeleide volgorde zet
quecual op nummer 1 en genero op nummer 3: precies verkeerd om, op precies het concept waar Stefan
over viel. De lessenreeks ordent woorden, geen grammatica.

*Wat het wel werd:* `GC_ORDE`, een expliciete handgeschreven volgorde van 23 ids. Dat is een oordeel
en dat hoort het te zijn, maar de **vorm** is machinaal controleerbaar, en dat is het verschil met
een verzonnen moeilijkheidsscore. `pw-gramorde.js` toetst: elk concept staat er precies één keer in,
GC_ORDE noemt geen id dat niet bestaat, elke voorwaarde in `GC_VOOR` bestaat en staat eerder in de
rij (dus geen kringetjes), en op dag 1 staat er iets open en niet alles. Voegt iemand later een
concept toe zonder het in de volgorde te zetten, dan gaat de poort rood in plaats van dat het
onderwerp stilzwijgend uit de app verdwijnt.

`GC_VOOR` is klein gehouden: zes regels, hoogstens twee voorgangers per onderwerp. concordancia en
demostrativo wachten op genero, hayestar op serestar, pronombre op apersonal, indefimperf op
perfindef, en de diepe les subjuntivo op indefimperf.

*De poort:* alles wat je ooit aanraakte blijft open (fouten moeten terug kunnen komen), en daarnaast
staan er `GC_VENSTER` = 3 nieuwe onderwerpen open. Wie op zijn voorganger wacht slaat zijn beurt
over, zodat er altijd echt drie te kiezen zijn. Dag 1 is daarmee **genero, serestar, negacion**, de
grammatica-stap van de dagles is `concept-genero`, en de tab toont 3 concepten + 2 diepe lessen + 3
gegenereerde onderwerpen in plaats van 50. Onder de lijst staat "nog 20 onderwerpen komen later",
want verstoppen zonder te zeggen dat je verstopt is de fout die v23.45 al een keer maakte.

Dezelfde poort geldt nu voor de drie plekken die zelf kozen: de dagles (`lesFlowGramId`, met een
nieuwe stap die terugvalt op het eerste open onderwerp in plaats van op de wizardlijst), de
Grammatica-tab (`gcLijst` in leervolgorde, GRAMWIZ gefilterd, `gwGenLijst` volgt je lespositie) en
Chispa's Clasificador. Het zoekvenster vindt nog steeds elk concept: zoeken is een bewuste handeling.

*Twee tests die groen waren om de verkeerde reden.* `pw-leermachine.js` controleerde dat de fout van
gisteren bovenaan de Grammatica-tab staat, en dat klopte alleen omdat muymucho toevallig het eerste
element in `GC_CONCEPTEN` was: `gcVandaagKaartjes()` filterde de volledige lijst in plaats van de
volgorde van `gcVandaagLijst()` te volgen. Met GC_ORDE ervoor viel het om, en dat was terecht — de
code is gerepareerd, niet de test. En vier suites (`pw-clasificador`, `pw-jargon`, `pw-les7`,
`pw-gramwiz2`) gingen ervan uit dat een vers profiel bij álles kan. Die zetten hun profiel nu
expliciet neer als een gevorderde, want ze gaan over het spel, de vaktermen en de wizards, niet over
de poort.

**Wat hierna komt, bewust niet nu.** Stefan: "veel tekst, weinig voorbeelden, weinig stap voor stap,
dat kan denk ik nog meer micro steps." Dat is de herontwerp van de uitleg zélf: voorbeeld eerst, dan
de keuze, dan één regel uitleg, met de lange tekst gedegradeerd tot "de hele regel". Het veld `w` per
patroon is er al en bevat precies die ene regel. v23.53 gaat alleen over wélk onderwerp je krijgt,
niet over hoe het eruitziet. **Na de lancering.**
