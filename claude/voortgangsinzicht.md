# Voortgangsinzicht: cijfers en moeilijkheidsniveau

Stefan, 9 aug: "gisteren zeiden we morgen gaan we met schone lei verder om te kijken of het inzicht in
je voortgang met inzicht in cijfers, moeilijkheidsniveau nu goed kunnen krijgen, dat wil ik graag
oppakken."

Dit document is de opdracht voor die sessie, geschreven vanuit v23.12. Het bestaat omdat dit onderwerp
al drie keer half is aangeraakt (v23.0 fout, v23.1-v23.4 gerepareerd) en de fout elke keer dezelfde
vorm had: hetzelfde cijfer op twee schermen met twee verschillende sommen eronder.

## Wat er vast staat, en niet ter discussie is

De CEFR-doelstelling mag bestaan maar wordt nooit het leidende getal. Stefan: "ik vind de indicator
belangrijker dan de doelstelling."

Het bewijs dat de app werkt is dat de A1-balk vult. Zijn kritiek op Duolingo: "ik doe de habit maar ik
leer niks." Een balk die zich vult met wat je van jezelf vindt, is die kritiek nog een keer. Vandaar de
regel uit v23.8: zelf gezegd is geen bewijs.

Minder dan vier keer per week openen is zijn eigen drempel voor "het ontwerp deugt niet, niet mijn
discipline".

Op het profiel wil hij een lange lijst met alles in cijfers, en per cijfer één regel interpretatie.
Op Vandaag wil hij een simpel overzicht.

## Wat er inmiddels aan data ligt (en dat is nieuw sinds de vorige poging)

- `S.meting[week]` (v23.4): per week `stevig, bijna, geoefend, dek, txp, spel, spelw, pog, fout`.
  Vanaf ongeveer tien weken kan hier een persoonlijke foutmarge uit komen. Gestart 8 aug, dus rond
  half oktober bruikbaar. Tot die tijd niet doen alsof.
- `S.sweep` (v23.8): `{dag, ken, niet, goed, fout}`. Zodra `goed + fout >= 10` weet je hoe vaak zijn
  eigen "die ken ik wel" klopte. Dat is een gekalibreerd getal over zijn zelfinschatting, en het maakt
  de schattingslaag op de balk voor het eerst ijkbaar.
- `S.dagStats[dag]` met `pogingen` en `fouten`: de ruwe bron voor een foutpercentage per dag.
- `S.srs[id].claim`: welke woorden nog een eerste echte check moeten krijgen.
- `S.oogst` (v22.6, 7 dagen) en `S.mijlpalen` (v22.4).

## Het moeilijkheidsniveau: wat er wel en niet mag worden beweerd

Stefan wilde "te makkelijk / precies goed / te uitdagend" in plaats van een kaal foutpercentage, en
noemde het 85%-onderzoek. Dat onderzoek (Wilson e.a., Nature Communications 2019) is echt, maar gaat
over stochastic-gradient-descent-leerders op binaire classificatie en zegt expliciet niets over
woordenschat of spaced repetition. FSRS zegt dat de optimale retentie per gebruiker verschilt.

Conclusie die overeind staat: het label mag niet op dat paper leunen. De band moet uit zijn eigen
`S.meting`-reeks komen. Tot die reeks er is, toon je het foutpercentage kaal en zeg je erbij dat de
band nog wordt opgebouwd. Een label met een verzonnen grens is precies het soort getal waar dit
project al drie keer op is vastgelopen.

## Concrete werklijst

1. Vandaag: de voortgangsbalk (donker = bewezen vast, lichter = onderweg, grijs = nog niet gezien),
   een "geoefend"-teller die alleen oploopt, en het foutpercentage. Het doel als noemer, niet als kop.
2. Profiel: de lange lijst. Elk getal met één regel wat het betekent. Kandidaten: woorden actief,
   bewezen vast, onderweg, geoefend totaal, foutpercentage 7 dagen, dagen actief, zelfinschatting
   (uit `S.sweep`), per niveau de Cervantes-dekking, en de weekreeks zodra die iets zegt.
3. Weg: de 14-daagse strip. De "nieuw/fout"-regel verbergen als hij nul is. De stapzin ("Sinds je
   eerste peiling...") naar het profiel.
4. `volgendeStap(context)` bovenop `naRondeHtml()` voor de zes doodlopende plekken: na de dagles, na
   een spel, onderaan het woordenboek, na een hoofdstuk, op het voortgangsscherm, en als er niets
   urgents is. Hoogstens één suggestie per scherm, altijd weg te klikken.
5. Op het profiel tonen wannéér mijlpalen, dagoogst en weekmeting iets te zeggen hebben. Nu staan er
   lege beloftes.

## De valkuil, in één zin

Elke keer dat dit misging, ging het mis doordat er twee stukken code over hetzelfde getal bestonden.
Eén functie levert de cijfers, alle schermen roepen hem aan. Zodra je een tweede som schrijft omdat
"dit scherm net iets anders wil", is de tegenspraak al geboren.

## Openstaand van elders, hoort hier los van

- De avondrun levert nog niets: voorraad nieuwe lesstof staat op 0 dagen. De alt-reparatie van 9 aug
  (`herstelAlt` in content-lib) had de oorzaak van de laatste twee mislukte nachten weg moeten halen,
  maar dat moet zich nog bewijzen.
- Audio-achterstand s93-s152 en bs70-bs73.
- porpara-gram-doosje staat op box 0 (0 goed, 4 fout).

---

## Werkafspraken die in elke sessie golden

- Antwoord in het Nederlands, informeel en direct. Geen em-dashes, en-dashes of dubbele koppeltekens,
  ook niet in app-teksten of code-commentaar.
- Stefan beslist over richting, ik beslis over uitwerking en bouw het. Zijn woorden: "moet ik dat nu
  beslissen? en ik kan dat nu ook niet beslissen want ik ben geen pedagoog. Doe dat wat me bij het doel
  brengt: spaans leren op een leuke en ontspannen manier."
- Vaste regel: elke versie die af en groen is, gaat dezelfde sessie live.
- De poort (`test/poort.js`) draait volledig voor elke oplevering. 57 suites, ongeveer negen minuten.
  Draai vanuit de repo met `CHROMIUM=` gezet. Bracket-escape altijd bij pkill: `pkill -f 'srv[8]321'`.
- Code-commentaar legt uit waarom iets zo is, met Stefans eigen woorden erin waar die de reden zijn.
- Bevindingen van zijn moeder uit haar eerste sessie, nog steeds leidend: te veel informatie op het
  scherm, te veel knoppen waarvan het doel onduidelijk is, ze wilde stoppen en zag niet hoe.
