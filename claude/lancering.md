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

## Wat er open staat, op volgorde van hoe erg het is

### 1. Dag 1 van een vreemde is te vol

De app heeft negen spellen, Chispa met tapas en dansjes, een boek, liedjes, een avontuur, een muur,
een maatje, een peiling en een voortgangspagina. Voor Stefan is dat rijkdom, voor iemand op dag 1 is
het ruis. De regel uit gedragsontwerp is één handeling op dag 1.

De machinerie staat er al: `SPEEL_EIS` houdt spellen dicht tot je genoeg woorden kent, en
`lessonUnlocked` doet hetzelfde voor lessen. Ze staan alleen ruim afgesteld. Dit is aanpassen en niet
bouwen.

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
