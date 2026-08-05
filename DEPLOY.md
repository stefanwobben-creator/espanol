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

1. Eén verhaal uitkiezen (zie hieronder).
2. Bouwen. `APP_VERSIE` in `index.html` en `versie.txt` allebei ophogen, altijd samen.
3. Lokaal `node tools/syntaxcheck.js index.html` en `node test/poort.js`.
4. Pushen naar `main`. De poort draait opnieuw, want lokaal groen is geen bewijs.
5. Groen: het staat live, ongeveer drie minuten na de push. Rood: er is niets gebeurd, en onder
   Actions staan de schermafdrukken van het moment waarop het misging.

Stap 3 mag je overslaan als je haast hebt. De poort in CI is de echte; de lokale is om niet te
hoeven wachten op een fout die je in tien seconden zelf had gezien.

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

Let op: alleen de gepubliceerde map gaat terug. Wat de gebruiker in localStorage heeft staat er
gewoon nog, dus een terugdraai raakt zijn profiel niet, maar een verandering die de opslagvorm
verbouwt, is niet zomaar terug te draaien. Zulke veranderingen horen in een eigen push met een eigen
versienummer, en het is het waard om er even bij stil te staan voordat je hem doet.

## De avondrun

`curriculum.yml` schrijft 's nachts in `index.html` en pushte dat tot nu toe zonder dat er ooit een
browser naar het resultaat had gekeken. Nu draait de poort er twee keer omheen: één keer voordat de
bot iets schrijft (stond `main` al rood, dan is het niet zijn schuld) en één keer over zijn eigen
resultaat. Alleen bij groen wordt er gepusht.

Gaten dichten gaat direct live. Een compleet nieuwe les komt als pull request, want dat is
curriculum-uitbreiding en daar wil je zelf naar kijken.

## Wat er live komt

Expliciet opgesomd in `poort.yml`, niet "de hele map":

```
index.html  maatje.html  versie.txt  CNAME  .nojekyll  audio/
```

Testcode, servercode en gereedschap blijven binnen. Voeg je een bestand toe dat de app tijdens het
draaien zelf ophaalt, dan moet het in dat lijstje erbij, anders werkt het lokaal wel en live niet.
