# De regressiekern

39 browsersuites die samen de poort vormen. Groen betekent: dit mag live. Rood betekent: er gaat
niets naar buiten, niet met de hand en niet door een bot.

```
node test/poort.js                 alles (ongeveer 6 minuten rekentijd, 2 minuten wachten)
node test/poort.js --deel 2/4      alleen het tweede kwart (zo draait CI het)
node test/poort.js pw-taal.js      alleen deze suite
```

Eerst even `cd test && npm install && npx playwright install chromium`, eenmalig.

De suites vragen om `http://localhost:8321/espanol-stefan.html`. In deze repo heet dat bestand
`index.html`. De ingebouwde server in `poort.js` vertaalt dat ene pad en serveert verder gewoon de
repo, zodat `audio/` en `versie.txt` er ook zijn. Er staat dus geen tweede kopie van de app op
schijf: een kopie veroudert en dan test je stilletjes iets anders dan je publiceert.

## De poort praat met niets buiten zichzelf

`geenserver.js` wordt door `poort.js` voor elke suite ingeladen en breekt elk verzoek af dat niet
naar `localhost:8321` gaat. Geen enkele suite hoeft daar iets voor te doen.

Dat is er niet voor de netheid. De app belt bij het opstarten de familieserver op Render. In de
sandbox waarin deze suites geschreven zijn kwam dat verzoek nooit aan, en die stilte staat in elke
suite in de lijst met ruis die niet meetelt. Op een GitHub-runner is er wél internet: daar komt het
verzoek echt aan, weigert Render het omdat `localhost:8321` niet in zijn CORS-lijst staat, en schrijft
Chromium een zin in de console die in geen enkele ruislijst stond. Acht suites rood in alle vier de
shards, terwijl er aan de app niets mankeerde.

De les zit niet in die ene zin maar in de afhankelijkheid: de kleur van de poort hing af van of de
machine internet had, of Render wakker was en wat er in zijn CORS-lijst stond. Zoiets wordt een keer
rood op een moment dat er niets aan de hand is, en dan is de poort binnen een week een advies.

Wil je ooit tegen de echte server testen, dan is dat een eigen suite die dat expliciet aanzet.

Screenshots komen in `test/uitvoer/` terecht (genegeerd door git, in CI bewaard als artefact bij een
rode run).

## De laatste stap naar vast (v20.0)

`pw-echtecheck.js` bewaakt het enige getal in de app dat moet bewijzen dat je iets leert: de
A1-balk op Vandaag. Tot v19.99 liep die balk vol op een flashcard waarbij jij zelf op "wist ik"
drukte. Dat is geen meting, dat is een mening over jezelf.

Vanaf v20.0 komt een woord alleen in de bovenste doos na een check die je niet zelf beoordeelt:
je ziet de vertaling in je eigen taal en kiest uit vier Spaanse mogelijkheden, zonder dat het
antwoord ergens op het scherm staat. Het vinkje heet `st.k`. Alleen `wCheckAntwoord` en het
Avontuur (daar typ je het woord) zetten het. Spellen kunnen het sowieso niet, want die zitten al
vast op `SPEL_PLAFOND = 3`.

Wat de suite dus vasthoudt, in volgorde: "wist ik" brengt je hoogstens naar de een-na-laatste doos,
op die doos verschijnt de check in de productieve richting, goed zet het woord vast en laat de
A1-teller precies één omhoog gaan, fout kost één doosje in plaats van de hele rij, en profielen van
voor v20.0 krijgen hun vinkje cadeau in `normaliseerState` zodat niemands balk zakt door een
verbetering.

## Een blok verdient zijn plek (v20.1)

`pw-context.js` bewaakt de regel die Vandaag klein houdt: een blok verschijnt op het moment dat het
iets over jou zegt, en staat er tot die tijd niet. Geen instelling, geen knop om iets te verbergen.

De aanleiding staat in de bevindingen van Stefans moeder: te veel informatie op het scherm, te veel
knoppen waarvan de bedoeling onduidelijk is. De oorzaak was dat elk blok zichzelf tekende ook als
het niets te melden had: een nieuwskaart met de mededeling dat er geen nieuws was, een basisbalk op
0%, dertien lege staafjes met een knop naar cijfers die nog nergens over gingen, en drie chipjes met
een nul erin. `dagRelevantie()` beantwoordt nu per blok de vraag of er iets te zeggen valt.

De suite meet dat in twee richtingen, en die tweede is de belangrijkste: weglaten mag nooit
verstoppen worden. Dag een is klein (alleen starten en spelen), en daarna wordt per blok de context
neergezet die het verdient, waarna het er ook echt moet staan: iets in doos 3 laat de basisbalk
verschijnen, twee dagen met punten laten de staafjes verschijnen, en elk chipje komt terug zodra er
iets in staat. Ook ligt hier vast dat de basisbalk over jouw niveau gaat: `dagNiveau()` volgt
`poortRang()`, dus wie de basis claimt ziet A2 met de noemer van A2, niet langer een hardgecodeerde
A1.

## Verder waar je was (v20.2)

`pw-verder.js` bewaakt de tweede helft van dezelfde opdracht: waar in een oefening ben je nu. De les
bestond tot v20.1 alleen in het geheugen van het tabblad (`lesFlow` was een gewone variabele), dus
wie halverwege wegklikte begon de volgende keer weer bij stap 1. De stopknop beloofde "Klaar voor
nu, je verliest niets" en maakte dat niet waar.

`S.lesFlowNu` is nu het herstelpunt: de stap, plus wat die stap nodig heeft om zichzelf opnieuw te
openen. `lesFlowVolgende()` is een schil om de stappenmachine die na elke overgang bewaart, dus er
is één plek waar dat gebeurt in plaats van bij elke return. Herstellen loopt via `lesFlowHervat()`
met een eigen opener per stap, want de stappenmachine valt door naar de volgende stap en zou je dus
juist voorbij je eigen plek zetten.

Twee grenzen liggen hier vast. Hervatten kan alleen binnen dezelfde dag: je dagportie is een dagding
en de wachtrij van gisteren is geen "waar je was" maar een verlopen plan, dus `normaliseerState`
gooit hem weg. En het dagscherm krijgt er geen blok bij: de startknop die er al staat wordt
contextueel ("Verder waar je was, stap 2/4, Grammatica"), met opnieuw beginnen als tekstregel
eronder. De suite telt daarom de knoppen in de kaart: precies één primaire knop, altijd. Twee
knoppen naast elkaar zou de tweede bevinding van Stefans moeder terugbrengen.

## De peiling (v20.3)

`pw-peiling.js` bewaakt de opdracht erachter: de voortgangsbalk moet een bevestiging zijn, iets van
"dit klopt ongeveer met het niveau waarvan ik zelf denk dat ik ben", en tegelijk moet er een stap in
te zien zijn. Dat botst: een bevestiging is een toestand, een stap is een verschil. De oplossing is
dat het getal boven de balk de toestand is (een schatting van je hele A1-woordenschat, dus inclusief
wat je al kon voordat je de app opende) en dat de stap als streepje plus een zin in diezelfde balk
zit. Geen tweede blok, want de regel uit v20.1 blijft staan: een blok verdient zijn plek.

De schatting is een steekproef, en de suite rekent hem op de eenheid na. Twaalf woorden per peiling,
vier keuzes, met een echte knop "geen idee" ernaast. Goed geraden wordt gecorrigeerd met
`r - (g - r) / 3`, want bij vier opties gok je gemiddeld een op vier goed; "geen idee" telt daarom
wel als niet gekend maar niet als gokfout. Rond het punt staat een Wilson-interval, en het punt zelf
is gestratificeerd: wat hier bewezen is telt als telling, de rest krijgt het gemeten percentage.
Onder de twintig antwoorden zwijgt de balk liever dan te raden.

Drie dingen liggen hier hard vast. Een peiling is een meting en geen les: er gaat geen woord naar
`S.srs`, er zijn geen punten en geen tapas, want een steekproef die zichzelf onderwijst meet zijn
eigen antwoord. Elke Cervantes-sleutel wordt hoogstens een keer gepeild, ooit. En de balk gebruikt
`balkNiveau()` in plaats van `dagNiveau()`: dagNiveau volgt `poortRang()` en die telt de
niveauclaim mee, dus wie bij het instellen "A2" aanvinkt zou een balk zien die op zijn eigen
verklaring rust. Een balk die op jouw eigen verklaring rust kan nooit een bevestiging zijn. De
suite legt daarom vast dat `balkNiveau()` A1 blijft terwijl `dagNiveau()` A2 zegt.

Waar de app niet kan meten, doet ze geen uitspraak. `PEIL_DEKKING` staat op 0,8: van A1 heeft de app
356 van de 390 Cervantes-sleutels in huis, van A2 maar 55 van de 409. Over A2 zegt de balk dus
niets, en dat is geen omissie maar het punt.

## Wat er niet in zit

Er waren 66 suites. 34 daarvan staan hier, plus pw-a1vandaag (v19.99), pw-echtecheck (v20.0), pw-context (v20.1) en pw-verder (v20.2) die er later bij geschreven zijn. 32 staan er niet bij. Die 32 zijn niet weggegooid maar ook niet opgenomen:
een testsuite die faalt op iets dat allang met opzet veranderd is, is geen alarm maar ruis, en ruis
in een poort leidt binnen een week tot "ach, die is altijd rood". De schuld staat hieronder
expliciet, zodat het een keuze blijft en geen vergeetput.

**B, versie-assertie (8):** `pw-v1985` tot en met `pw-v1991d`. Ze controleren dat APP_VERSIE gelijk
is aan de versie waarin ze geschreven zijn. Dat kan per definitie maar één versie lang kloppen.
Reviven kost vijf minuten per stuk: haal de versiecheck eruit, laat de rest staan. Wat ze verder
testen is nog steeds zinnig.

**A, navigeert via een verhuisde tab (11):** `pw-a08`, `pw-a09`, `pw-competenties`, `pw-leerkpi`,
`pw-les6`, `pw-les8`, `pw-les9`, `pw-les10`, `pw-mappingfix`, `pw-moeilijktoggle`, `pw-nieuwe13`.
Sinds v19.98 zijn er nog vier tabs in de onderbalk en zit de rest achter Meer. Het mechanische deel
van de reparatie is `await page.click('#nav button[data-tab="vertalen"]')` vervangen door
`await page.evaluate(() => show('vertalen'))`. Bij `pw-jaartallen`, `pw-les7` en `pw-lezen` was dat
genoeg; die drie staan hierboven weer in de kern. Bij deze elf niet: ze vallen daarna nog steeds om
op iets anders, en dat is per suite uitzoekwerk.

**C, verwijst naar oude code (13):** `pw-chispa`, `pw-dagsessie`, `pw-gramwiz`, `pw-groei`,
`pw-hoewerkt`, `pw-indeling`, `pw-jerga`, `pw-kern84`, `pw-mijnchispa`, `pw-privacy`,
`pw-profielzones`, `pw-spiekwiz`, `pw-versie`. Ze roepen functies of ids aan die niet meer bestaan.
`pw-dagsessie` valt bijvoorbeeld om op `DAG_PORTIE is not defined`, en dat is geen recente regressie:
die naam komt in v19.92 al niet voor. Herschrijven of laten gaan, per suite.

## Een suite terugbrengen

1. Zet hem in `test/suites/` en draai `node test/poort.js pw-naam.js`.
2. Loopt hij groen, dan is hij vanaf nu onderdeel van de poort. Klaar.
3. Loopt hij rood, kijk dan eerst of hij iets test wat nog bestaat. Zo niet: laat hem buiten staan en
   schrijf liever een nieuwe suite bij het gedrag dat je nu wél belangrijk vindt.

Regel bij het bouwen van iets nieuws: een verhaal dat af is, levert een suite op. Zo groeit de kern
mee met de app in plaats van erachteraan.

## Wat een suite moet doen om mee te kunnen

Een suite is een gewoon node-programma. Geen testrunner, geen framework. De poort start het en kijkt
alleen naar de exitcode.

- `chromium.launch({ executablePath: process.env.CHROMIUM })`. Leeg in CI, daar vindt Playwright
  zijn eigen installatie; gevuld als je hem ergens draait waar de browser op een vaste plek staat.
- Ga naar `http://localhost:8321/espanol-stefan.html`.
- De rondleiding blokkeert klikken. Zet `S.tour = true` en haal `#tourWrap` weg voordat je klikt.
- Eindig met `process.exit(1)` als er iets fout is. Groen printen mag, maar de exitcode telt.
