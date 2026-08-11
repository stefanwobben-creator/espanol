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
- **pw-clasificador** is niet meer wisselvallig (punt 5 hieronder). Geen tijdsprobleem maar een
  dobbelsteen: `clNieuwSpel()` zonder id koos een willekeurig concept, en bij een concept met weinig
  patronen was de ronde al klaar vóór de misser die de test wilde meten. Staat nu op `serestar`.

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

Let op het gat. Op een trage verbinding staat het aanmeldscherm er na 0,7 seconde, mét de naamvelden
en de niveauknoppen, want die staan in de statische HTML. Maar het script is pas twaalf seconden
later klaar. Een bezoeker ziet dus geen wit scherm maar iets ergers: een app die er staat en niet
reageert. Hij tikt op "hallo", er gebeurt niets, en hij concludeert dat het stuk is.

Niet op te lossen voor vrijdag (de content zit ín het bestand), wel te verzachten: een laadscherm dat
binnen 300 ms staat en pas weggaat als boot() alles heeft aangesloten. De echte oplossing, content per
niveau laden, is de eerste grote verbouwing ná de lancering.

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
- De titel toont "¡Vamos …!" met een naam die er nog niet is.
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

**6. De toets schaalt te hoog in.** Stefan: "bijna de helft kan je raden." Geen gevoel maar een
ontwerpfout. Bij *el jardín* waren de afleiders *de badkamer*, *hoeveel kost het?* en *blauw*: een
kamer, een vraag en een kleur. Je elimineert op soort zonder het woord te kennen. `peilOpties()`
neemt afleiders uit dezelfde categorie alleen als er drie beschikbaar zijn, anders uit de hele bak.
Daar komt bij dat veel A1-woorden cognaten zijn (jardín, hospital, pizarra) terwijl de gokcorrectie
in `niveauSchatting()` (r − f/3) blind raden veronderstelt en geen geïnformeerd elimineren. Fix:
afleiders uit dezelfde woordsoort en categorie, en de drempel omhoog. Raakt waar iedereen begint,
dus eerst.

**3. "Next sentence" vind je niet.** Bij het schrijven staat na Check eerst de groene uitslag, dan
*Why:*, dan de luisterknoppen, en pas daaronder de knop. Op een telefoon onder de vouw. Fix: bij een
goed antwoord automatisch door na een korte pauze; bij fout de knop direct onder de uitslag.

**4. Het loopt dood na de dagles.** Je bent klaar en er is geen volgende stap: geen Chispa voeren,
geen spel, geen tweede les. Staat al sinds v23.4 in de docs als `volgendeStap(context)` ("de zes
doodlopende plekken") en is nooit gebouwd.

**2 en 5, samen één verhaal: de app weet niet wat makkelijk is.** `GC_CONCEPTEN` heeft geen
moeilijkheidsvolgorde, alleen een verwijzing naar een spiekbrief, dus op dag 1 kwam *qué of cuál*
langs. Stefans voorstel is juist: begin bij el/la en los/las, en die concepten bestaan al (`genero`,
`concordancia`), ze staan alleen niet vooraan. En Oefenen en Grammatica staan wagenwijd open terwijl
lessen en spellen wél gepoort zijn, dus je kunt op dag 1 bij subjuntivo. Fix: elk concept een rang,
de dagles pakt de laagste die je nog niet hebt, en Oefenen krijgt dezelfde vriendelijke poort als de
spellen.
