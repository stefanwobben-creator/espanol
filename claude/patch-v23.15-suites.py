#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.15, de suites erachteraan.

Vier suites vielen om op een hardgecodeerd getal, niet op gedrag. De noemer van A1 was 390 en is nu
409, omdat hij vanaf deze versie uit dezelfde uitpakregel komt als de sleutels zelf. En hornear is
geen zoekstaart-woord meer maar een gewoon leswoord, want het staat in de Cervantes-inventaris.

De reparatie is niet "zet er 409 neer". Dat zou over een halfjaar weer omvallen. De suites leiden het
getal nu af, en houden vast wat ze eigenlijk bewaken: dat de noemer zichtbaar is, dat hij bij het
niveau hoort, en dat de rekensom van de peiling klopt.

Idempotent.
"""
import io, os, sys

MAP = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/test/suites")


def patch(bestand, paren):
    pad = os.path.join(MAP, bestand)
    with io.open(pad, encoding="utf-8") as f:
        src = f.read()
    if paren[0][1] in src:
        print("  al toegepast:", bestand)
        return
    for oud, nieuw in paren:
        n = src.count(oud)
        assert n == 1, "%s: anker komt %d keer voor:\n%s" % (bestand, n, oud[:120])
        src = src.replace(oud, nieuw, 1)
    with io.open(pad, "w", encoding="utf-8") as f:
        f.write(src)
    print("  bijgewerkt:", bestand)


# ---------------------------------------------------------------- pw-a1vandaag
patch("pw-a1vandaag.js", [(
    """    return { dek: t.dek.A1 || 0, noemer: PCIC_NOEMER.A1, tekst: tekst.replace(/\\s+/g, ' ') };
  });
  ok(cijfers.noemer === 390, 'de noemer is de 390 A1-eenheden van het Cervantes');""",
    """    return { dek: t.dek.A1 || 0, noemer: PCIC_NOEMER.A1,
             sleutels: Object.keys(pcicKeysApp().A1 || {}).length,
             tekst: tekst.replace(/\\s+/g, ' ') };
  });
  /* v23.15: hier stond `noemer === 390`. Dat getal is 409 geworden omdat de noemer nu uit dezelfde
     uitpakregel komt als de sleutellijst, en een suite die op een teller staat valt om zodra die
     teller loopt. Wat hier echt onder ligt is een verhouding: de noemer is de Cervantes-telling van
     A1, en de app hoort daar bijna alles van in huis te hebben. Zakt dat weg, dan meet de balk iets
     anders dan de lezer denkt, en dat is wel een reden om rood te worden. */
  ok(cijfers.noemer > 0 && cijfers.sleutels / cijfers.noemer >= 0.9,
     'de noemer is de A1-telling van het Cervantes en de app heeft er minstens 90 procent van ('
     + cijfers.sleutels + '/' + cijfers.noemer + ')');""")])

# ---------------------------------------------------------------- pw-context
patch("pw-context.js", [
    ("""  // v23.2: zie pw-a1vandaag. De noemer moet zichtbaar zijn, de rest staat in de legenda.
  ok(naBasis.tekst.indexOf('van de 390 A1-woorden') !== -1,
    'de zin noemt jouw niveau en de noemer erbij');""",
     """  // v23.2: zie pw-a1vandaag. De noemer moet zichtbaar zijn, de rest staat in de legenda.
  // v23.15: het getal wordt opgehaald in plaats van opgeschreven, want het hoort bij de sleutellijst
  // en die groeit mee met wat de app aan Cervantes in huis heeft.
  const noemA1 = await page.evaluate(() => PCIC_NOEMER.A1);
  ok(naBasis.tekst.indexOf('van de ' + noemA1 + ' A1-woorden') !== -1,
    'de zin noemt jouw niveau en de noemer erbij (' + noemA1 + ')');"""),
    ("""  ok(naA2.tekst.indexOf('van de 409 A2-woorden') !== -1, 'en de noemer is die van A2, niet die van A1');""",
     """  const noemA2 = await page.evaluate(() => PCIC_NOEMER.A2);
  ok(noemA2 !== noemA1 && naA2.tekst.indexOf('van de ' + noemA2 + ' A2-woorden') !== -1,
     'en de noemer is die van A2, niet die van A1 (' + noemA2 + ' tegenover ' + noemA1 + ')');"""),
])

# ---------------------------------------------------------------- pw-peiling
patch("pw-peiling.js", [(
    """  console.log('\\n-- de rekensom, op de cent --');
  const alles = await zetItems(page, 30, 0, 0);
  ok(alles && alles.punt === 390, 'dertig keer goed op een leeg profiel: schatting 390 (' + (alles && alles.punt) + ')');
  ok(alles && alles.onder < 390 && alles.onder > 330, 'met een ondergrens eronder, geen zekerheid (' + (alles && alles.onder) + ')');
  ok(alles && alles.boven === 390, 'en een bovengrens op de noemer (' + (alles && alles.boven) + ')');

  const niets = await zetItems(page, 0, 30, 0);
  ok(niets && niets.punt === 0, 'dertig keer fout: schatting 0 (' + (niets && niets.punt) + ')');

  const half = await zetItems(page, 15, 15, 0);
  ok(half && half.punt === 130, 'vijftien goed en vijftien fout is na gokcorrectie een derde: 130 (' + (half && half.punt) + ')');

  const geen = await zetItems(page, 20, 0, 10);
  ok(geen && geen.punt === 260, '"geen idee" telt als niet gekend maar niet als gokfout: 260 (' + (geen && geen.punt) + ')');""",
    """  console.log('\\n-- de rekensom, op de cent --');
  /* v23.15: deze vier getallen stonden hier als 390, 130 en 260. Dat waren geen losse waarden maar
     de noemer en twee breuken daarvan, en de noemer is 409 geworden. Ze worden nu uitgerekend uit
     PCIC_NOEMER, zodat de suite de rekensom bewaakt en niet de stand van de teller. */
  const noem = await page.evaluate(() => PCIC_NOEMER.A1);
  const alles = await zetItems(page, 30, 0, 0);
  ok(alles && alles.punt === noem, 'dertig keer goed op een leeg profiel: schatting ' + noem + ' (' + (alles && alles.punt) + ')');
  ok(alles && alles.onder < noem && alles.onder > noem * 0.8, 'met een ondergrens eronder, geen zekerheid (' + (alles && alles.onder) + ')');
  ok(alles && alles.boven === noem, 'en een bovengrens op de noemer (' + (alles && alles.boven) + ')');

  const niets = await zetItems(page, 0, 30, 0);
  ok(niets && niets.punt === 0, 'dertig keer fout: schatting 0 (' + (niets && niets.punt) + ')');

  const half = await zetItems(page, 15, 15, 0);
  ok(half && half.punt === Math.round(noem / 3), 'vijftien goed en vijftien fout is na gokcorrectie een derde: ' + Math.round(noem / 3) + ' (' + (half && half.punt) + ')');

  const geen = await zetItems(page, 20, 0, 10);
  ok(geen && geen.punt === Math.round(noem * 2 / 3), '"geen idee" telt als niet gekend maar niet als gokfout: ' + Math.round(noem * 2 / 3) + ' (' + (geen && geen.punt) + ')');""")])

# ---------------------------------------------------------------- pw-dic52
patch("pw-dic52.js", [(
    """  await page.fill('#dicZoek', 'hornear');
  await page.waitForTimeout(250);
  const selVerb = '.dicrow[data-dic="freq:hornear"]';""",
    """  /* v23.15: hier stond hornear. Dat woord staat in de Cervantes-inventaris en is daarmee een
     gewoon leswoord geworden, dus het komt niet meer als zoekstaart-treffer langs. derretir doet
     wat hornear hier deed: een werkwoord dat alleen in de frequentielijst zit. */
  await page.fill('#dicZoek', 'derretir');
  await page.waitForTimeout(250);
  const selVerb = '.dicrow[data-dic="freq:derretir"]';""")])

print("klaar")
