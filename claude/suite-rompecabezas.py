# suite-rompecabezas.py - proeven voor de uitleg bij het bord (v23.271).
#
# Stefan: "bij de rompecabezas mis ik soms nog wat meer uitleg per oefening (wat zijn de vormen,
# voorbeelden, lijstjes en dan oefenen)."
#
# Wat hier bewaakt wordt is niet of er tekst staat, maar of die tekst ergens op slaat: de rijtjes
# moeten de echte RV_UITGANG zijn, de stammen moeten die van dít bord zijn, en de schoen moet de
# echte presente van dát werkwoord zijn. Een uitleg die los staat van het spel veroudert stilletjes,
# en dat is precies wat deze patch wilde vermijden.
import io, os, sys

ROOT = os.path.expanduser(os.environ.get("VAMOS", "~/mnt/espanol"))
P = os.path.join(ROOT, "test/suites/pw-rompecabezas.js")
s = io.open(P, encoding="utf-8").read()

if "rvUitlegHtml" in s:
    print("al bijgewerkt")
    sys.exit(0)

ANKER = """  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));"""

NIEUW = """  // ---- 7. de uitleg bij het bord (v23.271) ----
  //
  // Stefan: "bij de rompecabezas mis ik soms nog wat meer uitleg per oefening (wat zijn de vormen,
  // voorbeelden, lijstjes en dan oefenen)." Wat hier getoetst wordt is of die uitleg uit het spel
  // zelf komt. Een rijtje dat met de hand is overgetypt klopt vandaag en over een jaar niet meer.
  const uitleg = await page.evaluate(() => {
    S.rvUitleg = true; S.rvBest = 0;
    rvNieuweRonde();
    renderFunRompecabezas();
    const h = document.getElementById('funCard').innerHTML;
    const tekst = document.getElementById('funCard').textContent.replace(/\\s+/g, ' ');
    // elke uitgang uit de echte tabel moet in de rijtjes staan
    const alle = [].concat(RV_UITGANG.ar, RV_UITGANG.er, RV_UITGANG.ir);
    const mist = alle.filter(function (e) { return h.indexOf('>-' + e + '<') === -1; });
    // en elke persoon
    const persoonMist = RV_PERSOON.filter(function (p) { return tekst.indexOf(p) === -1; });
    // de stammen van dit bord staan erbij, met hun werkwoord
    const stamMist = rvSpel.stammen.filter(function (sk) { return tekst.indexOf(sk.inf) === -1; });
    // en de schoen van het eerste werkwoord is de echte presente
    const inf = rvSpel.stammen[0].inf;
    const vormen = rvIndex().perVerb[inf].delen.map(function (d) { return d.vorm; });
    const schoen = rvSchoenHtml(inf);
    const vormMist = vormen.filter(function (v) {
      return schoen.replace(/<[^>]*>/g, '').indexOf(v) === -1;
    });
    return { mist: mist, persoonMist: persoonMist, stamMist: stamMist.map(function (x) { return x.stam; }),
             inf: inf, vormen: vormen, vormMist: vormMist,
             knop: !!document.getElementById('rvUitlegKnop'),
             bordErnaast: document.querySelectorAll('[data-rvs]').length };
  });
  ok(uitleg.mist.length === 0, 'alle achttien uitgangen staan in de rijtjes (mist: ' + (uitleg.mist.join(',') || 'niets') + ')');
  ok(uitleg.persoonMist.length === 0, 'en alle zes de personen (mist: ' + (uitleg.persoonMist.join(',') || 'niets') + ')');
  ok(uitleg.stamMist.length === 0, 'de werkwoorden van DIT bord staan erbij (mist: ' + (uitleg.stamMist.join(',') || 'niets') + ')');
  ok(uitleg.vormMist.length === 0,
    'en de schoen van ' + uitleg.inf + ' is de echte presente: ' + uitleg.vormen.join(', '));
  ok(uitleg.bordErnaast > 0, 'het bord staat er gewoon naast, de uitleg vervangt het spel niet');
  ok(uitleg.knop === true, 'en er is een knop om hem dicht te klappen');

  const dicht = await page.evaluate(() => {
    S.rvUitleg = false;
    renderFunRompecabezas();
    return { rijtjes: document.getElementById('funCard').innerHTML.indexOf('>-amos<') !== -1,
             knop: (document.getElementById('rvUitlegKnop') || {}).textContent || '',
             bord: document.querySelectorAll('[data-rvs]').length };
  });
  ok(dicht.rijtjes === false, 'dichtgeklapt staan de rijtjes er niet meer');
  ok(dicht.bord > 0, 'maar het bord wel');
  ok(/Hoe werkt dit/.test(dicht.knop), 'en de knop nodigt uit om hem weer open te doen ("' + dicht.knop.trim() + '")');

  // na afloop staan de werkwoorden compleet op het eindscherm: je hebt ze net zelf geprobeerd
  const eind = await page.evaluate(() => {
    rvSpel.klaar = true;
    renderFunRompecabezas();
    const t = document.getElementById('funCard').textContent.replace(/\\s+/g, ' ');
    const infs = [];
    rvSpel.stammen.forEach(function (sk) { if (infs.indexOf(sk.inf) === -1) infs.push(sk.inf); });
    return { infs: infs, mist: infs.filter(function (i) { return t.indexOf(i) === -1; }),
             kop: /compleet/i.test(t) };
  });
  ok(eind.mist.length === 0, 'op het eindscherm staan alle werkwoorden van het potje (' + eind.infs.join(', ') + ')');
  ok(eind.kop === true, 'met een kop die zegt dat ze compleet zijn');

  ok(errors.length === 0, 'geen js-fouten: ' + errors.slice(0, 3).join(' | '));"""

assert s.count(ANKER) == 1, s.count(ANKER)
io.open(P, "w", encoding="utf-8").write(s.replace(ANKER, NIEUW))
print("bijgewerkt:", P)
