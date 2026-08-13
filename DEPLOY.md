# Deployen

Eén weg naar live. Een push naar `main` draait de poort in een echte browser, en alleen bij groen
gaat de map naar GitHub Pages. Dat geldt voor jou, voor mij en voor de avondrun. Er is geen knop om
het over te slaan, en dat is precies de bedoeling: een uitzondering die je één keer maakt, maak je
daarna elke keer.

De poort duurt ongeveer twee minuten, de deploy een halve. Vier keer per dag deployen is dus geen
ambitie maar gewoon de bovengrens van hoe vaak je zin hebt om iets af te maken.

## Eenmalig instellen

Settings, dan Pages, dan Build and deployment, dan Source op **GitHub Actions** in plaats van
"Deploy from a branch". Zolang die op branch staat, publiceert GitHub `main` rechtstreeks en is de
poort een advies in plaats van een poort.

## De ronde

1. **Eerst bijtrekken: `git pull --rebase`.** De avondrun schrijft 's nachts in `index.html` en
   `versie.txt`, dus je begint bijna nooit op wat je gisteren achterliet.
2. Eén verhaal uitkiezen (zie hieronder).
3. Bouwen. `APP_VERSIE` in `index.html` en `versie.txt` allebei ophogen, altijd samen.
4. Lokaal `node tools/syntaxcheck.js index.html` en `node test/poort.js`.
5. Pushen naar `main`. De poort draait opnieuw, want lokaal groen is geen bewijs.
6. Groen: het staat live, ongeveer drie minuten na de push. Rood: er is niets gebeurd, en onder
   Actions staan de schermafdrukken van het moment waarop het misging.

Stap 4 mag je overslaan als je haast hebt. De poort in CI is de echte; de lokale is om niet te
hoeven wachten op een fout die je in tien seconden zelf had gezien.

Stap 1 niet. Die kost een seconde en hij is de enige stap die iets voorkomt wat je pas veel later
merkt. Wat er gebeurt als je hem overslaat, op 10 aug: de patch voor v23.30 zocht een zin die de
avondrun die nacht had toegevoegd, vond hem niet, deed niets, en de commit ging door met een
boodschap over werk dat niet gedaan was. Pas de push liep vast, en toen leek het een gitprobleem.

## Patchen

Veranderingen aan `index.html` gaan via een idempotent pythonscript in `claude/`, met een
`rep(anker, nieuw, n=1)` die vastloopt als het anker niet precies n keer voorkomt. Nooit los zoeken
en vervangen: dat bestand is te groot om te overzien en een halve treffer merk je niet.

**Meerdere patches achter elkaar: `sh tools/patches.sh v23.50`.** Nooit met de hand in één blok
plakken. Wat er op 12 augustus gebeurde: na een botsing met de avondrun is de tak opnieuw opgebouwd
door zes patches in één blok te plakken. Twee ervan faalden precies zoals het hoort, met een melding
welk anker ontbrak en exitcode 1 — maar in een blok van zes scrolt zo'n melding voorbij en de rest
liep gewoon door. v23.50 en v23.51 stonden daardoor niet in het bestand, de poort ging rood in CI,
en er ging een uur in het zoeken zitten. De patches waren niet stuk; de manier waarop ze gedraaid
werden was stuk. Dat script draait ze één voor één, stopt bij de eerste fout, en doet daarna de
syntaxcheck.

**Anker niet op `APP_VERSIE` als de avondrun ertussen kan zitten.** Die hoogt het versienummer
onderweg op, en dan mist een patch die op `var APP_VERSIE = "v23.49";` mikt zijn anker terwijl er
inhoudelijk niets aan de hand is. Anker op de code die je verandert; het versienummer bijwerken kan
met een regex.

**Botst je werk met de avondrun, rebase dan niet.** Vier commits × een bestand van 2,5 MB is twaalf
keer met de hand in iets wat je niet kunt overzien. In plaats daarvan:

    git branch backup-<datum>                    # veiligheidsnet, kost niets
    git reset --soft origin/main                 # commits los, werkmap blijft
    git checkout origin/main -- index.html versie.txt tools/avondrun-hart.json
    sh tools/patches.sh v23.50 .                 # jouw wijzigingen er opnieuw overheen
    git add -A && git commit && git push

Daar zijn de patchscripts voor gemaakt: ze zijn de wijziging, en `index.html` is maar een uitkomst.

Drie dingen die zo'n script moet doen, alle drie geleerd op 10 aug:

- **Twee keer draaien mag niets stukmaken.** Vandaar de idempotentiecheck bovenaan.
- **"Al gedaan" en "hier valt niets te doen" zijn niet hetzelfde.** Het eerste is een
  geruststelling, het tweede is een fout. Een script dat in beide gevallen "niets te doen" zegt,
  laat je doorlopen met een verkeerd beeld. Kijk of het bestand is wat je denkt dat het is, en stop
  met een uitleg als dat niet zo is.
- **Schrijft een script in meer dan één bestand, dan hoort de check per bestand.** Anders slaat hij
  het tweede stilletjes over omdat het eerste al klaar was.

Een handpatch moet ook zelf aan `versie.txt` denken. `pasToe()` in `tools/content-lib.js` doet dat
wel, een script in `claude/` niet, en dan wacht de servicewerker op een versie die nooit komt.

Een `id` uit een melding opzoeken zonder in twee megabyte te gaan zoeken: `node tools/zin.js s154`.
Werkt op zinnen, woorden en toetsjes.

## Een verhaal dat af te kaderen is

Vier keer per dag deployen werkt alleen als een verhaal klein genoeg is om in een halve zittijd af te
maken. De maat die hier past:

- **Eén zichtbare verandering.** Niet "profiel verbeteren", wel "de A1-balk staat bovenaan Vandaag".
- **Je kunt opschrijven wat er straks anders op het scherm staat.** Lukt dat niet, dan is het nog
  geen verhaal maar een idee.
- **Het is te verbinden met het doel.** Spaans leren op een leuke en ontspannen manier. Kun je die
  lijn niet trekken, dan hoort het in de bak met ooit.
- **Er komt een suite bij, of een bestaande dekt het af.** Zonder dat groeit de app wel en de poort
  niet, en dan is de poort over drie maanden een herinnering aan augustus.
- **Het is terug te draaien in zijn eentje.** Twee verhalen in één push betekent dat je bij een
  probleem allebei terug moet zetten.

Twijfel je of iets te groot is: als je het in één zin kunt zeggen zonder "en", is het goed.

## Terugdraaien

Actions, dan de workflow Poort, dan de run van de vorige goede versie, dan "Re-run all jobs". Die
zet die versie terug live. Geen revert-commit, geen haast, geen keuzes op het verkeerde moment.

Daarna pas uitzoeken wat er mis was. De site staat dan al weer goed, en dat scheelt in het hoofd.

**Gerepeteerd op 13 aug, en het werkt.** Twee dingen nagemeten, want een noodprocedure die je nooit
hebt uitgevoerd is een aanname:

- *Krijgt een re-run de oude code te pakken?* Ja. `actions/checkout@v4` zonder `ref` pakt de
  `github.sha` van de gebeurtenis, en die verandert niet als je een run opnieuw draait. De
  publicatiestap print dat commit-nummer, dus je ziet het ook in het logboek.
- *Is de vorige goede versie vandaag nog groen?* Voor `6ee6cdb` (v23.61, wat er nu live staat):
  67/67 groen, 679 s. Dat is de vraag die ertoe doet, want "Re-run all jobs" draait de poort
  opnieuw. Is die inmiddels rood, dan publiceert de re-run niets en sta je met lege handen op het
  slechtste moment.

**En daar zit de valkuil.** De poort van een oude commit kan vandaag rood zijn zonder dat er iets
mis is met die versie: een suite met een datum erin verloopt (dat is op 12 aug twee keer gebeurd),
of een suite is later strenger geworden. Ook getest: commit `30ea03b` is vandaag rood, en terecht,
want daar ontbraken v23.50 en v23.51 en hij is nooit live geweest.

Daarom, in deze volgorde:

1. **Kies een run die groen was, niet een commit die goed voelde.** In Actions zie je dat meteen.
2. Re-run all jobs. Blijft hij groen: klaar, ongeveer drie minuten.
3. Wordt hij rood op een suite die niets met jouw probleem te maken heeft, ga dan niet repareren
   in de oude commit. Draai in plaats daarvan de slechte verandering terug op `main`
   (`git revert <sha> && git push`): dan draait de poort op de huidige suites, en die zijn per
   definitie niet verlopen.

Let op: alleen de gepubliceerde map gaat terug. Wat de gebruiker in localStorage heeft staat er
gewoon nog, dus een terugdraai raakt zijn profiel niet, maar een verandering die de opslagvorm
verbouwt, is niet zomaar terug te draaien. Zulke veranderingen horen in een eigen push met een eigen
versienummer, en het is het waard om er even bij stil te staan voordat je hem doet.

Voor de server (Render) is terugdraaien iets anders: daar staat een knop "Rollback" bij een eerdere
deploy. En als het om een slot gaat dat te streng staat, is de omgevingsvariabele sneller dan een
deploy: `POORT_UIT=1` voor sync en log, `AI_UIT=1` voor de AI-knoppen. Zie `server/README.md`.

## De avondrun

`curriculum.yml` schrijft 's nachts in `index.html` en pushte dat tot voor kort zonder dat er ooit
een browser naar het resultaat had gekeken. Nu draait de poort er twee keer omheen: één keer voordat
de bot iets schrijft (stond `main` al rood, dan is het niet zijn schuld) en één keer over zijn eigen
resultaat. Alleen bij groen wordt er gepusht.

Gaten dichten gaat direct live. Een compleet nieuwe les komt als pull request, want dat is
curriculum-uitbreiding en daar wil je zelf naar kijken.

**13 augustus, drie structurele reparaties.** Stefan: "avondrun gaat niet goed en doe ik in github
re-run jobs dan gaat het wel goed."

- *Een re-run is geen herkansing maar een nieuwe worp.* "Re-run all jobs" draait `curriculum.js`
  opnieuw, en die vraagt een taalmodel om nieuwe zinnen. De run was dus een machine die je 's
  ochtends met de hand moest aanzwengelen. `tools/avondrun.sh` doet die tweede worp nu zelf,
  hoogstens één keer. Twee en niet vijf: gaat het twee keer op rij mis, dan is er iets anders aan de
  hand dan een ongelukkige zin en wil je het zien.
- *Het bewijs werd weggegooid.* De stap die de kapotte poging moest bewaren kopieerde hem naar
  `/tmp/mislukt` en er stond nergens een `upload-artifact`. Die map gaat met de runner de prullenbak
  in. Nu hangt bij elke run een artefact `avondrun-afgekeurd-<id>` met per poging de diff van wat de
  bot schreef, het poortlog, de schermafdrukken en de hartslag. Veertien dagen bewaard.
- *De hartslag loog.* `curriculum.js` schrijft `gelukt` als hij klaar is met genereren, niet als er
  iets gepubliceerd is. Twee nachten op rij stond er "gelukt: true, geleverd: 5 zinnen" terwijl er
  niets op `main` stond. `tools/hartslag-af.js` zet er nu de uitkomst van de héle run in:
  `gegenereerd` (de oude betekenis), `gepubliceerd`, `pogingen` en een `reden` in gewone taal.

En één ding dat geen bug was maar wel meespeelde: een GitHub-runner heeft twee kernen en de poort
start standaard vier browsers. De avondrun draait de hele poort in één job, dus daar vecht hij met
zichzelf om processortijd. `TEGELIJK: 2` staat nu in de workflow. `poort.yml` heeft dat probleem
niet, want die verdeelt de suites over vier machines.

Wat je 's ochtends doet als de run rood is: open het artefact, lees `poging-1/poort.log` (daar staat
welke suite rood was) en `poging-1/wat-de-bot-schreef.diff` (daar staat waarom). Dat is genoeg om te
weten of het aan de content lag of aan de app.

## Wat er live komt

Expliciet opgesomd in `poort.yml`, niet "de hele map":

```
index.html  maatje.html  versie.txt  CNAME  .nojekyll  audio/
```

Testcode, servercode en gereedschap blijven binnen. Voeg je een bestand toe dat de app tijdens het
draaien zelf ophaalt, dan moet het in dat lijstje erbij, anders werkt het lokaal wel en live niet.
