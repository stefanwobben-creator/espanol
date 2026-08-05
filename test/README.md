# De regressiekern

35 browsersuites die samen de poort vormen. Groen betekent: dit mag live. Rood betekent: er gaat
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

## Wat er niet in zit

Er waren 66 suites. 34 daarvan staan hier, plus pw-a1vandaag die bij v19.99 is bijgeschreven. 32 staan er niet bij. Die 32 zijn niet weggegooid maar ook niet opgenomen:
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
