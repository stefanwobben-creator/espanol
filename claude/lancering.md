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

Niet op te lossen voor vrijdag (de content zit ín het bestand), wel te verzachten: een laadscherm dat
binnen 300 ms staat, en de zware content pas na de eerste render. De echte oplossing, content per
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
