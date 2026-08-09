#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23.26, pw-lezen erachteraan.

De suite ging ervan uit dat het Lezen-scherm meteen de hoofdstukken toont. Sinds deze versie kom je
eerst op de boekenplank en kies je een boek. Dat is precies het soort verandering waarvoor een suite
hoort om te vallen, dus hij is niet zwakker gemaakt maar bijgewerkt: hij opent nu eerst Chispa en
controleert daarna hetzelfde als altijd.

Er komt een controle bij, want de plank is nieuw en onbewaakt: hij moet allebei de boeken tonen met
een percentage, en hij moet terug kunnen.

Idempotent.
"""
import io, os, sys

MAP = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/espanol/test/suites")
pad = os.path.join(MAP, "pw-lezen.js")

with io.open(pad, encoding="utf-8") as f:
    src = f.read()

if "leesReeks" in src:
    print("al toegepast, niets te doen")
    sys.exit(0)


def rep(anker, nieuw, n=1):
    global src
    gevonden = src.count(anker)
    assert gevonden == n, "anker komt %d keer voor in plaats van %d:\n%s" % (gevonden, n, anker[:160])
    src = src.replace(anker, nieuw, n)


rep(
    """  await page.evaluate(() => show('lezen')); // locale-onafhankelijk (nav-taal kan EN/NL/... zijn)
  await page.waitForTimeout(200);
""",
    """  await page.evaluate(() => show('lezen')); // locale-onafhankelijk (nav-taal kan EN/NL/... zijn)
  await page.waitForTimeout(200);

  /* v23.26: het Lezen-scherm begint nu op de boekenplank. Eerst kijken of die klopt, dan Chispa
     openen; de rest van deze suite gaat over de hoofdstukkenlijst en die zit een tik verder. */
  const plank = await page.evaluate(() => {
    const el = document.getElementById('lezenMenu');
    return {
      tekst: (el.innerText || '').replace(/\\s+/g, ' '),
      boeken: el.querySelectorAll('button[data-reeks]').length,
      geenHoofdstukken: el.querySelectorAll('button[data-boek]').length
    };
  });
  ok(plank.boeken >= 2, 'de boekenplank toont allebei de boeken (' + plank.boeken + ')');
  ok(plank.geenHoofdstukken === 0, 'en nog geen hoofdstukken: die zitten een tik verder');
  ok(/0%|\\d+%/.test(plank.tekst), 'met een percentage erbij hoe ver je in dat boek bent');
  await page.evaluate(() => { document.querySelector('button[data-reeks="chispa"]').click(); });
  await page.waitForTimeout(150);
  ok(await page.locator('#btnPlankTerug').count() === 1, 'in een boek staat een weg terug naar de plank');
""")

rep(
    """  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));""",
    """  /* De weg terug moet ook echt terug gaan, en niet alleen bestaan. Een knop die niets doet is
     erger dan geen knop, want je hebt hem al aangetikt voordat je het merkt. */
  await page.evaluate(() => { document.getElementById('btnPlankTerug').click(); });
  await page.waitForTimeout(150);
  ok(await page.evaluate(() => document.querySelectorAll('#lezenMenu button[data-reeks]').length) >= 2,
     'de weg terug brengt je op de plank, met de boeken er weer op');

  const relevanteErrors = errors.filter((e) => !/Failed to load resource|ERR_TUNNEL_CONNECTION_FAILED/.test(e));""")

with io.open(pad, "w", encoding="utf-8") as f:
    f.write(src)
print("pw-lezen.js bijgewerkt")
